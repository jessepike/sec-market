#!/usr/bin/env python3
"""Dedicated official account login on the private runner, with safe progress.

Only the temporary browser challenge is posted to a private check. OAuth files
and secret-writer credentials never enter logs, Git, artifacts or model input.
"""
import argparse
import json
import os
import re
import selectors
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from auth_store import AuthStore, AuthStoreError

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "web/scripts/pipeline"))
from agents import SubscriptionAgent, ModelUnavailable

PROJECT = "jessepike/sec-market"
CHECK_NAME = "Dedicated subscription account setup"


def safe_process_env(token=None, home=None):
    names = {"PATH", "HOME", "LANG", "LC_ALL", "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "https_proxy", "http_proxy", "no_proxy", "SSL_CERT_FILE", "NODE_EXTRA_CA_CERTS", "REQUESTS_CA_BUNDLE", "TMPDIR"}
    env = {k: v for k, v in os.environ.items() if k in names}
    if token:
        env["GH_TOKEN"] = token
    if home:
        env["CODEX_HOME"] = str(home)
    return env


def github(path, token, body=None):
    args = ["gh", "api", "repos/" + PROJECT + "/" + path, "--header", "Cache-Control: no-cache"]
    if body is not None:
        args.extend(["--method", "PATCH" if path.startswith("check-runs/") else "POST", "--input", "-"])
    result = subprocess.run(args, input=json.dumps(body) if body is not None else None,
                            capture_output=True, text=True, timeout=45, env=safe_process_env(token=token))
    if result.returncode:
        raise RuntimeError("PRIVATE_SETUP_API_OPERATION_FAILED")
    return json.loads(result.stdout)


class SetupCheck:
    def __init__(self, token):
        self.token = token
        self.run_id = os.environ["GITHUB_RUN_ID"]
        self.check = github("check-runs", token, {"name": CHECK_NAME, "head_sha": os.environ["GITHUB_SHA"],
            "external_id": "smp-bootstrap-" + self.run_id, "status": "in_progress",
            "details_url": f"https://github.com/{PROJECT}/actions/runs/{self.run_id}",
            "output": {"title": "Preparing dedicated account login", "summary": "No account credentials have been published. Waiting for the official browser challenge."}})["id"]

    def update(self, title, summary, conclusion=None):
        body = {"output": {"title": title, "summary": summary}}
        if conclusion:
            body.update(status="completed", conclusion=conclusion)
        github("check-runs/" + str(self.check), self.token, body)


def device_challenge(text):
    plain = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    code = re.search(r"(?m)^\s*([A-Z0-9]{4,6}-[A-Z0-9]{4,6})\s*$", plain)
    url = "https://auth.openai.com/codex/device"
    return {"url": url, "code": code[1]} if url in plain and code else None


def login(home, check):
    home.mkdir(mode=0o700, parents=True)
    (home / "config.toml").write_text('cli_auth_credentials_store = "file"\n')
    os.chmod(home / "config.toml", 0o600)
    process = subprocess.Popen(["codex", "login", "--device-auth"], stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, env=safe_process_env(home=home), start_new_session=True)
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    text, shown = "", False
    deadline = time.monotonic() + 16 * 60
    try:
        while time.monotonic() < deadline:
            for key, _ in selector.select(timeout=1):
                data = os.read(key.fileobj.fileno(), 4096)
                if data:
                    text = (text + data.decode(errors="replace"))[-32768:]
            challenge = device_challenge(text)
            if challenge and not shown:
                expires = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
                check.update("Official browser sign-in required",
                    "Approve this dedicated private CI login in your own ChatGPT account.\n\n"
                    + challenge["url"] + "\n\nOne-time device code: **" + challenge["code"] + "**\n\n"
                    + "Expires in approximately 15 minutes (" + expires + "). No refresh/access token is shown. "
                    + "The challenge will be removed when this attempt ends.")
                print("Official device challenge is available in the private setup check.", flush=True)
                shown = True
            if process.poll() is not None:
                break
        if process.poll() is None:
            raise RuntimeError("OFFICIAL_DEVICE_SIGN_IN_TIMED_OUT")
        if process.returncode or not (home / "auth.json").is_file():
            raise RuntimeError("OFFICIAL_DEVICE_SIGN_IN_FAILED")
    finally:
        selector.close()
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)


class GuardedRunner:
    def __init__(self, store, runner=subprocess.run):
        self.store, self.runner = store, runner
        self.contexts = []
        self.failed_closed = False

    def __call__(self, *args, **kwargs):
        if self.failed_closed:
            raise ModelUnavailable("AUTH_REFRESH_PERSISTENCE_FAILED_STOP_WORK")
        try:
            result = self.runner(*args, **kwargs)
            for line in (result.stdout or "").splitlines():
                try:
                    event = json.loads(line)
                except (ValueError, TypeError):
                    continue
                if event.get("type") == "thread.started":
                    self.contexts.append(event.get("thread_id"))
            return result
        finally:
            command = args[0] if args else []
            if len(command) > 1 and command[1] == "exec":
                try:
                    self.store.checkpoint()
                except (AuthStoreError, OSError):
                    self.failed_closed = True
                    raise ModelUnavailable("AUTH_REFRESH_PERSISTENCE_FAILED_STOP_WORK") from None


def check_request(request, secrets):
    """initialize_codex creates the login; sign_in_again replaces an expired one.

    Both need the owner's approval recorded in the request. Replacing is refused
    unless a login exists, so a typo cannot turn a first setup into a silent overwrite.
    """
    operation = request.get("operation")
    if operation not in ("initialize_codex", "sign_in_again") or request.get("ownerApproved") is not True:
        raise RuntimeError("EXPLICIT_INITIALIZATION_REQUEST_REQUIRED")
    if operation == "sign_in_again" and not request.get("approval"):
        raise RuntimeError("OWNER_APPROVAL_REFERENCE_REQUIRED")
    if secrets.get("total_count", 0) > 100:
        raise RuntimeError("SECRET_INVENTORY_REQUIRES_PAGINATION_REVIEW")
    exists = any(s["name"] == "SMP_CODEX_AUTH_JSON" for s in secrets["secrets"])
    if operation == "initialize_codex" and exists:
        raise RuntimeError("ACCOUNT_ALREADY_INITIALIZED_USE_PROBE_INSTEAD")
    if operation == "sign_in_again" and not exists:
        raise RuntimeError("NO_LOGIN_TO_REPLACE_USE_INITIALIZE")
    return operation


def execute(root):
    if os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("GITHUB_REPOSITORY") != PROJECT:
        raise RuntimeError("PRIVATE_GITHUB_RUNNER_REQUIRED")
    request = json.loads((REPO / "ops/ci/bootstrap-request.json").read_text())
    writer = os.environ.pop("SMP_AUTH_STORE_TOKEN", "")
    if not writer:
        raise RuntimeError("SMP_AUTH_STORE_TOKEN_NOT_CONFIGURED")
    check_request(request, github("actions/secrets?per_page=100", writer))
    check = SetupCheck(os.environ["GH_TOKEN"])
    home = Path(root).resolve() / "codex-account"
    if home.is_relative_to(REPO) or home.exists():
        raise RuntimeError("FRESH_OUTSIDE_CHECKOUT_AUTH_DIRECTORY_REQUIRED")
    stored = False
    try:
        login(home, check)
        store = AuthStore(home, writer)
        store.checkpoint()
        stored = True
        check.update("Dedicated login saved; testing subscription",
                     "Official sign-in completed and the dedicated login is in encrypted repository secret storage. The temporary challenge has been removed. Running one bounded model probe.")
        os.environ["CODEX_HOME"] = str(home)
        config = dict(json.loads((REPO / "contracts/market.json").read_text())["model"])
        config.update(maxCallsPerRun=1, timeoutSeconds=90)
        guarded = GuardedRunner(store)
        agent = SubscriptionAgent(config, runner=guarded)
        schema = {"type": "object", "additionalProperties": False, "required": ["ok"], "properties": {"ok": {"type": "boolean"}}}
        answer = agent.call('Return the JSON object {"ok":true}. Use no tools.', schema)
        if answer != {"ok": True}:
            raise RuntimeError("SUBSCRIPTION_PROBE_RESPONSE_DIFFERS")
        store.checkpoint()
        result = {"bootstrapPassed": True, "githubRunId": os.environ["GITHUB_RUN_ID"], "secretCreated": True,
                  "provider": "codex_subscription", "apiFallback": False, "modelCalls": agent.calls,
                  "isolatedContextIds": guarded.contexts, "dailyWorkerActivated": False}
        check.update("Dedicated subscription login and probe passed",
                     "Official dedicated CI login saved securely. One subscription model call passed; refreshed credentials were checkpointed. No API fallback or daily activation.", "success")
        return result
    except Exception as error:
        check.update("Dedicated account setup needs attention",
                     "The temporary sign-in challenge has been removed. Reason: " + type(error).__name__
                     + ". Login secret created: " + str(stored) + ". No daily worker activated.", "failure")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        result = execute(args.root)
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        # Never include raw CLI/auth responses in errors or artifacts.
        result = {"bootstrapPassed": False, "reason": str(error)[:120] if type(error) is RuntimeError else type(error).__name__, "dailyWorkerActivated": False}
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["bootstrapPassed"] else 2)
