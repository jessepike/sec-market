"""Verify actual GitHub run/artifact provenance, never a worker's trusted=true."""
import hashlib
import io
import json
import re
import subprocess
import zipfile

from contracts import canonical, require


class GitHubAuthority:
    def __init__(self, repo="jessepike/sec-market", workflow=".github/workflows/market-release-gate.yml", branch="main", runner=subprocess.run):
        require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) is not None, "Invalid repository")
        self.repo, self.workflow, self.branch, self.runner = repo, workflow, branch, runner

    def _api(self, path, binary=False):
        result = self.runner(["gh", "api", f"repos/{self.repo}/{path}"], capture_output=True, timeout=60)
        require(result.returncode == 0, "GITHUB_PROVENANCE_UNAVAILABLE")
        require(len(result.stdout) <= 100_000_000, "Artifact exceeds verifier byte budget")
        return result.stdout if binary else json.loads(result.stdout)

    def verify_test_receipt(self, receipt, artifact):
        run_id, artifact_id = receipt.get("githubRunId"), receipt.get("githubArtifactId")
        require(isinstance(run_id, int) and run_id > 0 and isinstance(artifact_id, int) and artifact_id > 0, "GitHub provenance IDs required")
        run = self._api(f"actions/runs/{run_id}")
        require(run["status"] == "completed" and run["conclusion"] == "success", "Test workflow did not complete successfully")
        require(run["path"] == self.workflow and run["head_branch"] == self.branch and run["head_sha"] == receipt["appRevision"], "Workflow identity or reviewed code revision differs")
        meta = self._api(f"actions/artifacts/{artifact_id}")
        require(meta["workflow_run"]["id"] == run_id and not meta["expired"] and meta["name"] == "daily-market-gate", "Wrong/expired gate artifact")
        archive = self._api(f"actions/artifacts/{artifact_id}/zip", binary=True)
        require(meta.get("digest") == "sha256:" + hashlib.sha256(archive).hexdigest(), "GitHub artifact digest mismatch")
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            info = z.getinfo("gate-receipt.json")
            require(info.file_size <= 1_000_000, "Gate receipt exceeds byte budget")
            authoritative = json.loads(z.read(info))
        supplied = {k: v for k, v in receipt.items() if k != "githubArtifactId"}
        require(canonical(authoritative) == canonical(supplied), "Receipt differs from trusted workflow artifact")
        require(authoritative["artifactSha256"] == artifact["sha256"], "Trusted artifact does not cover exact build")
        return True
