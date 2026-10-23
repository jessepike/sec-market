"""Official CLI prebuilt stage/promote/probe/rollback adapter.

Never uploads the checkout, never passes a token on argv, never uses --prod.
Management login remains in the official CLI credential store on the host.
"""
import json
import os
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote

from artifacts import stage_files
from contracts import canonical, require

IGNORE_GIT_PRODUCTION = 'test "$VERCEL_GIT_COMMIT_REF" = main || test "$VERCEL_GIT_COMMIT_REF" = data/archive'


class VercelAdapter:
    requires_remote_checkpoint = True
    def __init__(self, store, project_id, team_id, scope, site="https://securitymarketpulse.com", executable="vercel", global_config=None, runner=subprocess.run):
        require(re.fullmatch(r"prj_[A-Za-z0-9]+", project_id) and re.fullmatch(r"team_[A-Za-z0-9]+", team_id), "Pin existing Vercel project/team IDs")
        require(re.fullmatch(r"[a-z0-9-]+", scope), "Invalid Vercel scope")
        require(site == "https://securitymarketpulse.com", "Unexpected production site")
        self.store, self.project_id, self.team_id, self.scope, self.site = store, project_id, team_id, scope, site
        self.executable, self.global_config, self.runner = executable, global_config, runner
        self.pending = None
        self.pending_files = None

    def _cli(self, args, cwd=None):
        command = [self.executable, *args, "--scope", self.scope]
        if self.global_config:
            command.extend(["--global-config", self.global_config])
        env = dict(os.environ, VERCEL_TELEMETRY_DISABLED="1")
        # API keys are neither required nor a billing fallback.
        env.pop("OPENAI_API_KEY", None)
        result = self.runner(command, cwd=cwd, capture_output=True, text=True, timeout=300, env=env)
        require(result.returncode == 0, "VERCEL_OPERATION_FAILED")
        return result.stdout.strip()

    def production_paths_controlled(self):
        project = json.loads(self._cli(["api", f"/v9/projects/{self.project_id}", "--raw"]))
        return (project.get("id") == self.project_id and project.get("accountId") == self.team_id
                and project.get("autoAssignCustomDomains") is False
                and project.get("commandForIgnoringBuildStep") == IGNORE_GIT_PRODUCTION)

    def stage(self, manifest):
        receipt = {"ready": True, "appRevision": manifest["appRevision"], "dataReleaseId": manifest["releaseId"],
                   "snapshotSha256": manifest["snapshot"]["sha256"], "artifactSha256": manifest["artifact"]["sha256"],
                   "contractSha256": manifest["contractSha256"]}
        files = stage_files(self.store, manifest["artifact"], receipt)
        with tempfile.TemporaryDirectory(prefix="smp-prebuilt-") as directory:
            root = Path(directory)
            # The existing project has rootDirectory=web. The official CLI
            # validates that directory even when uploading only prebuilt output.
            (root / "web").mkdir()
            for name, body in files.items():
                path = root / ".vercel/output" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body)
            (root / ".vercel/project.json").write_bytes(canonical({"projectId": self.project_id, "orgId": self.team_id}))
            args = ["deploy", "--prebuilt", "--yes"]
            if manifest.get("mode") != "stage_only_smoke_test":
                # A production-target deployment with no assigned domain can
                # later be promoted without Vercel rebuilding tested bytes.
                args.extend(["--target=production", "--skip-domain"])
            output = self._cli(args, cwd=root)
        urls = re.findall(r"https://[a-z0-9-]+\.vercel\.app\b", output)
        require(len(set(urls)) == 1, "Unrecognized immutable deployment URL")
        self.pending = receipt
        self.pending_files = files
        return urls[0]

    def verify_static_files(self, deployment):
        require(deployment == self.site or re.fullmatch(r"https://[a-z0-9-]+\.vercel\.app", deployment), "Unapproved deployment probe")
        for name, expected in sorted((self.pending_files or {}).items()):
            if not name.startswith('static/'):
                continue
            url = deployment + '/' + quote(name[len('static/'):], safe='/')
            request = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(request, timeout=30) as response:
                require(response.status == 200 and response.url == url, 'DEPLOYED_STATIC_FILE_REDIRECT_OR_HTTP_FAILURE')
                actual = response.read(len(expected) + 1)
            require(actual == expected, 'DEPLOYED_STATIC_FILE_BYTES_DIFFER')

    @staticmethod
    def _get(base, path):
        require(base == "https://securitymarketpulse.com" or re.fullmatch(r"https://[a-z0-9-]+\.vercel\.app", base), "Unapproved deployment probe")
        request = urllib.request.Request(base + path, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(request, timeout=30) as response:
            require(response.status == 200 and response.url == base + path, "Deployment probe redirected or failed")
            body = response.read(1_000_001)
            require(len(body) <= 1_000_000, "Deployment receipt exceeds byte budget")
            return json.loads(body)

    def probe(self, deployment):
        app = self._get(deployment, "/app-release.json")
        try:
            receipt = self._get(deployment, "/deployment-receipt.json")
        except urllib.error.HTTPError as error:
            previous = self.store.read("heads/production.json")
            require(error.code == 404 and previous and previous.get("legacyBaseline") and app == previous.get("legacyAppReceipt"), "Deployment has no recognized release receipt")
            return {"ready": True, "dataReleaseId": previous["releaseId"], "appRevision": app["appRevision"], "legacyBaseline": True}
        require(app.get("appRevision") == receipt.get("appRevision") and app.get("dailySnapshotSha256") == receipt.get("snapshotSha256") and app.get("dailyContractSha256") == receipt.get("contractSha256"), "Application and detached deployment receipts differ")
        self.verify_static_files(deployment)
        return receipt

    def promote(self, deployment):
        require(re.fullmatch(r"https://[a-z0-9-]+\.vercel\.app", deployment), "Unapproved promotion target")
        self._cli(["promote", deployment, "--yes"])

    def probe_production(self):
        for attempt in range(6):
            try:
                result = self.probe(self.site)
                if self.pending is None or result.get("dataReleaseId") == self.pending["dataReleaseId"]:
                    return result
            except (ValueError, OSError):
                if attempt == 5:
                    raise
            if attempt < 5:
                time.sleep(5)
        raise ValueError("Production release did not converge to the promoted receipt")

    def rollback(self, deployment):
        require(re.fullmatch(r"https://[a-z0-9-]+\.vercel\.app", deployment), "Unapproved rollback target")
        previous = self.store.read("heads/production.json")
        self.pending = {"dataReleaseId": previous["releaseId"]} if previous else None
        self.pending_files = None
        # A previously served production deployment must use instant rollback.
        self._cli(["rollback", deployment, "--yes"])

    def import_baseline(self):
        require(self.store.read("heads/production.json") is None, "Production baseline already imported")
        app = self._get(self.site, "/app-release.json")
        require(re.fullmatch(r"[a-f0-9]{40}", app.get("appRevision", "")), "Live application revision missing")
        current = json.loads(self._cli(["api", "/v13/deployments/securitymarketpulse.com", "--raw"]))
        require(current.get("projectId") == self.project_id and current.get("readyState") == "READY", "Live deployment differs from project or is not ready")
        require(current.get("meta", {}).get("githubCommitSha") == app["appRevision"], "Live deployment/application code differs")
        deployment = "https://" + current["url"]
        require(self._get(deployment, "/app-release.json") == app, "Immutable baseline differs from production")
        baseline = {"sequence": 0, "deploymentId": deployment, "legacyBaseline": True, "legacyAppReceipt": app}
        from contracts import digest
        baseline["releaseId"] = digest(baseline)
        self.store.compare_and_swap("production", None, baseline)
        return baseline
