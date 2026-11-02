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
MAX_STAGE_BYTES = 20_000_000
STAGE_DEADLINE_SECONDS = 90
STAGE_RPC_TIMEOUT_SECONDS = 10


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

    def _cli(self, args, cwd=None, timeout=300):
        args = list(args)
        if args[0] == 'api':
            # The known team ID avoids account/user discovery in high-level
            # CLI promotion commands. Every API call is explicitly scoped.
            args[1] += ('&' if '?' in args[1] else '?') + 'teamId=' + self.team_id
        command = [self.executable, *args]
        if args[0] != 'api':
            command.extend(["--scope", self.scope])
        if self.global_config:
            command.extend(["--global-config", self.global_config])
        env = dict(os.environ, VERCEL_TELEMETRY_DISABLED="1")
        # API keys are neither required nor a billing fallback.
        env.pop("OPENAI_API_KEY", None)
        result = self.runner(command, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
        require(result.returncode == 0, "VERCEL_OPERATION_FAILED")
        return result.stdout.strip()

    def production_paths_controlled(self):
        project = json.loads(self._cli(["api", f"/v9/projects/{self.project_id}", "--raw"]))
        return (project.get("id") == self.project_id and project.get("accountId") == self.team_id
                and project.get("autoAssignCustomDomains") is False
                and project.get("commandForIgnoringBuildStep") == IGNORE_GIT_PRODUCTION)

    def stage(self, manifest, checkpoint=None):
        receipt = {"ready": True, "appRevision": manifest["appRevision"], "dataReleaseId": manifest["releaseId"],
                   "snapshotSha256": manifest["snapshot"]["sha256"], "artifactSha256": manifest["artifact"]["sha256"],
                   "contractSha256": manifest["contractSha256"]}
        if manifest.get("factualCorrections"):
            receipt["factualCorrections"] = manifest["factualCorrections"]
        files = stage_files(self.store, manifest["artifact"], receipt)
        # Include config and the detached receipt. The artifact parser separately
        # rejects functions, external rewrites and executable output.
        require(sum(map(len, files.values())) <= MAX_STAGE_BYTES, "VERCEL_STATIC_STAGE_BYTE_LIMIT")
        metadata = {"smpReleaseId": manifest["releaseId"], "smpAppRevision": manifest["appRevision"],
                    "smpArtifactSha256": manifest["artifact"]["sha256"]}
        self._stage_build_settings()
        started = time.monotonic()
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
            args = ["deploy", "--prebuilt", "--yes", "--no-wait"]
            for key, value in metadata.items():
                args.extend(["--meta", key + "=" + value])
            if manifest.get("mode") != "stage_only_smoke_test":
                # A production-target deployment with no assigned domain can
                # later be promoted without Vercel rebuilding tested bytes.
                args.extend(["--target=production", "--skip-domain"])
            # A timeout can leave an unknown paid creation. The already saved
            # publication attempt remains consumed; never repeat the create.
            try:
                output = self._cli(args, cwd=root, timeout=30)
            except Exception:
                raise ValueError("VERCEL_STAGE_CREATION_OUTCOME_UNKNOWN") from None
        urls = re.findall(r"https://[a-z0-9-]+\.vercel\.app\b", output)
        require(len(set(urls)) == 1, "VERCEL_STAGE_CREATION_OUTCOME_UNKNOWN")
        deployment = urls[0]
        target = None if manifest.get("mode") == "stage_only_smoke_test" else "production"
        try:
            # This URL is a reconciliation hint, not native identity or tested
            # deployment authority. Normal failure finalization archives it.
            self.store.write_once(f"deployment-create-responses/{manifest['releaseId']}.json", {
                "deploymentUrlHint": deployment, "identityVerified": False,
            })
            identity = self._stage_read(deployment, metadata, target)
        except Exception:
            raise ValueError("VERCEL_STAGE_CREATED_IDENTITY_UNVERIFIED") from None
        identifier = identity["id"]
        try:
            # Keep creation separate from deployment-attempts: the latter is
            # recovery authority only after the exact public bytes pass probing.
            self.store.write_once(f"deployment-creations/{manifest['releaseId']}.json", {
                "deploymentId": deployment, "nativeId": identifier, "projectId": self.project_id,
                "appRevision": manifest["appRevision"], "artifactSha256": manifest["artifact"]["sha256"],
                "staticBytes": sum(map(len, files.values())),
            })
            if checkpoint:
                checkpoint()  # Keep the scoped identity through worker/disk loss.
            while time.monotonic() - started < STAGE_DEADLINE_SECONDS:
                state = identity["readyState"]
                require(state not in ("CANCELED", "ERROR"), "VERCEL_STAGE_TERMINAL_FAILURE")
                if state == "READY":
                    self.pending = receipt
                    self.pending_files = files
                    return deployment
                time.sleep(min(2, max(0, STAGE_DEADLINE_SECONDS - (time.monotonic() - started))))
                identity = self._stage_read(deployment, metadata, target, identifier)
        except Exception:
            # Cancellation is only permitted after the native project, URL and
            # exact release metadata establish ownership. Never cancel another
            # deployment on an identity mismatch or guessed ID.
            self._cancel_stage(deployment, metadata, target, identifier)
            raise
        self._cancel_stage(deployment, metadata, target, identifier)
        raise ValueError("VERCEL_STAGE_DEADLINE_EXCEEDED")

    def _stage_build_settings(self):
        project = json.loads(self._cli(["api", f"/v9/projects/{self.project_id}", "--raw"],
                                       timeout=STAGE_RPC_TIMEOUT_SECONDS))
        require(isinstance(project, dict), "VERCEL_STAGE_FIXED_BASIC_SETTINGS_REQUIRED")
        resource = project.get("resourceConfig", {})
        require(isinstance(resource, dict)
                and project.get("id") == self.project_id and project.get("accountId") == self.team_id
                and resource.get("buildMachineType") == "basic"
                and resource.get("buildMachineSelection") == "fixed"
                and resource.get("elasticConcurrencyEnabled") is False,
                "VERCEL_STAGE_FIXED_BASIC_SETTINGS_REQUIRED")

    def _stage_read(self, deployment, metadata, target, identifier=None):
        host = deployment.removeprefix("https://")
        identity = json.loads(self._cli(["api", "/v13/deployments/" + (identifier or host), "--raw"],
                                        timeout=STAGE_RPC_TIMEOUT_SECONDS))
        require(isinstance(identity, dict), "VERCEL_STAGE_NATIVE_IDENTITY_DIFFERS")
        require(isinstance(identity.get("id"), str) and re.fullmatch(r"dpl_[A-Za-z0-9]+", identity["id"])
                and (identifier is None or identity["id"] == identifier)
                and identity.get("projectId") == self.project_id and identity.get("url") == host
                and identity.get("target") == target
                and isinstance(identity.get("meta"), dict)
                and all(identity.get("meta", {}).get(key) == value for key, value in metadata.items()),
                "VERCEL_STAGE_NATIVE_IDENTITY_DIFFERS")
        require(identity.get("readyState") in ("INITIALIZING", "QUEUED", "BUILDING", "READY", "ERROR", "CANCELED"),
                "VERCEL_STAGE_STATE_UNKNOWN")
        return identity

    def _cancel_stage(self, deployment, metadata, target, identifier):
        # Cancellation acknowledgement is a separate fact from a request. A
        # late READY or unavailable response cannot establish a billing ceiling.
        try:
            current = self._stage_read(deployment, metadata, target, identifier)
            if current["readyState"] in ("INITIALIZING", "QUEUED", "BUILDING"):
                try:
                    self._cli(["api", f"/v12/deployments/{identifier}/cancel", "--method", "PATCH", "--raw"],
                              timeout=STAGE_RPC_TIMEOUT_SECONDS)
                except Exception:
                    # A lost response or terminal-state race still needs a
                    # native read-back. Never resend the cancellation request.
                    pass
                current = self._stage_read(deployment, metadata, target, identifier)
            require(current["readyState"] in ("CANCELED", "ERROR"), "VERCEL_STAGE_STOP_NOT_ACKNOWLEDGED")
        except Exception:
            raise ValueError("VERCEL_STAGE_STOP_OUTCOME_UNKNOWN") from None

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
        self._switch_production(deployment, 'promote')

    def _switch_production(self, deployment, operation):
        require(operation in ('promote', 'rollback'), 'VERCEL_ALIAS_OPERATION_INVALID')
        host = deployment.removeprefix('https://')
        meta = json.loads(self._alias_api(['api', '/v13/deployments/' + host, '--raw'], 'GET_TARGET'))
        identifier = meta.get('id', '')
        require(re.fullmatch(r'dpl_[A-Za-z0-9]+', identifier) and meta.get('projectId') == self.project_id
                and meta.get('readyState') == 'READY' and meta.get('target') == 'production'
                and meta.get('url') == host, 'VERCEL_ALIAS_TARGET_NOT_READY_PROJECT_PRODUCTION')
        expected = self._get(deployment, '/app-release.json')
        version = 'v10' if operation == 'promote' else 'v9'
        with tempfile.TemporaryDirectory(prefix='smp-alias-') as directory:
            body = Path(directory) / 'body.json'
            body.write_text('{}')
            self._alias_api(['api', f'/{version}/projects/{self.project_id}/{operation}/{identifier}',
                             '--method', 'POST', '--input', str(body), '--raw'],
                            'PROMOTION' if operation == 'promote' else 'ROLLBACK')
        # API acceptance is asynchronous. Wait for actual domain assignment
        # before the publication journal records an acknowledgement.
        for attempt in range(36):
            try:
                if self._get(self.site, '/app-release.json') == expected:
                    self._close_assignment_after_alias()
                    return
            except (ValueError, OSError):
                pass
            if attempt < 35:
                time.sleep(5)
        raise ValueError('VERCEL_ALIAS_CHANGE_NOT_ACKNOWLEDGED')

    def _close_assignment_after_alias(self):
        path = '/v9/projects/' + self.project_id
        def read():
            project = json.loads(self._alias_api(['api', path, '--raw'], 'CONTROL'))
            require(project.get('id') == self.project_id and project.get('accountId') == self.team_id
                    and project.get('commandForIgnoringBuildStep') == IGNORE_GIT_PRODUCTION,
                    'VERCEL_CONTROL_IDENTITY_OR_IGNORE_DIFFERS')
            return project
        project = read()
        if project.get('autoAssignCustomDomains') is True:
            # Promotion/rollback may change this server-side. Repair only this
            # already authorized invariant; never replace unrelated settings.
            with tempfile.TemporaryDirectory(prefix='smp-control-') as directory:
                body = Path(directory) / 'body.json'
                body.write_text('{"autoAssignCustomDomains":false}')
                self._alias_api(['api', path, '--method', 'PATCH', '--input', str(body), '--raw'], 'CONTROL')
            project = read()
        require(project.get('autoAssignCustomDomains') is False, 'VERCEL_CONTROL_ASSIGNMENT_NOT_CLOSED')

    def _alias_api(self, args, phase):
        try:
            return self._cli(args)
        except (RuntimeError, ValueError) as error:
            categories = ('CLI_USAGE', 'AUTH_REQUIRED', 'TOKEN_REJECTED', 'ACCOUNT_ACCESS_DENIED',
                          'TEAM_ACCESS_DENIED', 'RATE_LIMITED', 'NETWORK', 'USER_LOOKUP', 'TEAM_LOOKUP',
                          'ACCESS_DENIED', 'UNCLASSIFIED')
            category = next((c for c in categories if str(error) == 'VERCEL_PREBUILT_STAGE_FAILED_' + c),
                            'UNCLASSIFIED')
            raise RuntimeError('VERCEL_' + phase + '_FAILED_' + category) from None

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
        self._switch_production(deployment, 'rollback')

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
