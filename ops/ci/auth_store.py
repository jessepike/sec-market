"""Proposed private CI credential round-trip; never invoked by the host canary.

Owner approval and two repository secrets are prerequisites. Uses GitHub's
encrypted Actions secret storage, not repository files, caches or artifacts.
"""
import hashlib
import json
import os
import subprocess
from pathlib import Path


class AuthStoreError(RuntimeError):
    pass


def managed_auth(body):
    try:
        value = json.loads(body)
        valid = (value.get("auth_mode") == "chatgpt" and
                 all(isinstance(value.get("tokens", {}).get(k), str) and value["tokens"][k]
                     for k in ("access_token", "id_token", "refresh_token")))
        if not valid:
            raise ValueError()
        return value
    except (ValueError, TypeError, AttributeError):
        raise AuthStoreError("Dedicated file-backed ChatGPT account sign-in required") from None


class AuthStore:
    def __init__(self, home, secret_writer_token, runner=subprocess.run):
        self.home = Path(home)
        repository = Path(__file__).resolve().parents[2]
        if self.home.resolve().is_relative_to(repository):
            raise AuthStoreError("Credentials must be outside the repository checkout")
        self.token = secret_writer_token
        self.runner = runner
        self.saved_sha = None

    def restore(self, body):
        managed_auth(body)
        if self.home.is_symlink() or self.home.exists() and any(self.home.iterdir()):
            raise AuthStoreError("Use an empty dedicated private Codex directory")
        self.home.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self.home, 0o700)
        body = body.encode() if isinstance(body, str) else body
        fd = os.open(self.home / "auth.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as file:
            file.write(body)
            file.flush()
            os.fsync(file.fileno())
        (self.home / "config.toml").write_text('cli_auth_credentials_store = "file"\n')
        os.chmod(self.home / "config.toml", 0o600)
        # Input is already the current encrypted GitHub secret. Never reseed on resume.
        self.saved_sha = hashlib.sha256(body).hexdigest()

    def checkpoint(self):
        path = self.home / "auth.json"
        if path.is_symlink():
            raise AuthStoreError("Credential symlink prohibited")
        body = path.read_bytes()
        managed_auth(body)
        os.chmod(path, 0o600)
        sha = hashlib.sha256(body).hexdigest()
        if sha == self.saved_sha:
            return {"saved": False, "reason": "unchanged"}
        if not self.token:
            raise AuthStoreError("Private CI secret-write permission required")
        # The helper receives plaintext only over stdin. Nothing sensitive goes
        # on argv, stdout, model input or the evidence/archive/artifact path.
        env = {k: v for k, v in os.environ.items() if k in {"PATH", "HOME", "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "SSL_CERT_FILE"}}
        env["GH_TOKEN"] = self.token
        try:
            result = self.runner(["gh", "secret", "set", "SMP_CODEX_AUTH_JSON", "--repo", "jessepike/sec-market"],
                                 input=body, capture_output=True, timeout=45, env=env)
        except (OSError, subprocess.TimeoutExpired):
            raise AuthStoreError("Refreshed credential persistence failed; stop model work") from None
        if result.returncode:
            raise AuthStoreError("Refreshed credential persistence failed; stop model work")
        self.saved_sha = sha
        return {"saved": True}
