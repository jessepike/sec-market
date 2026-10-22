#!/usr/bin/env python3
"""Restore dedicated CI auth on a fresh runner; verify official refresh/write-back."""
import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from auth_store import AuthStore, managed_auth
from bootstrap import GuardedRunner, SubscriptionAgent, PROJECT
from account_rpc import refresh_account


def execute(root, exercise_refresh=False):
    if os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("GITHUB_REPOSITORY") != PROJECT:
        raise RuntimeError("PRIVATE_GITHUB_RUNNER_REQUIRED")
    auth = os.environ.pop("SMP_CODEX_AUTH_JSON", "")
    writer = os.environ.pop("SMP_AUTH_STORE_TOKEN", "")
    if not auth or not writer:
        raise RuntimeError("DEDICATED_AUTH_AND_SECRET_WRITER_REQUIRED")
    home = Path(root).resolve() / "codex-account"
    store = AuthStore(home, writer)
    store.restore(auth)
    before = managed_auth(auth)
    started = datetime.now(timezone.utc)
    if exercise_refresh:
        # The official protocol explicitly requests managed OAuth refresh.
        # Do not mutate cache dates or implement OAuth endpoints ourselves.
        refresh_account(store)
    os.environ["CODEX_HOME"] = str(home)
    repo = Path(__file__).resolve().parents[2]
    config = dict(json.loads((repo / "contracts/market.json").read_text())["model"])
    config.update(maxCallsPerRun=1, timeoutSeconds=90)
    guarded = GuardedRunner(store)
    agent = SubscriptionAgent(config, runner=guarded)
    schema = {"type": "object", "additionalProperties": False, "required": ["ok"], "properties": {"ok": {"type": "boolean"}}}
    answer = agent.call('Return the JSON object {"ok":true}. Use no tools.', schema)
    if answer != {"ok": True}:
        raise RuntimeError("SUBSCRIPTION_PROBE_RESPONSE_DIFFERS")
    after = managed_auth((home / "auth.json").read_bytes())
    changed = any(before["tokens"][k] != after["tokens"][k] for k in ("refresh_token", "access_token"))
    refreshed_at = after.get("last_refresh")
    if exercise_refresh:
        if not changed or not refreshed_at or datetime.fromisoformat(refreshed_at.replace("Z", "+00:00")) < started - timedelta(minutes=5):
            raise RuntimeError("OFFICIAL_CLIENT_REFRESH_NOT_CONFIRMED")
    store.checkpoint()
    return {"probePassed": True, "githubRunId": os.environ["GITHUB_RUN_ID"], "provider": "codex_subscription",
            "freshRunnerRestore": True, "officialRefreshExercised": exercise_refresh,
            "tokenRotationConfirmed": changed, "authCheckpointConfirmed": True,
            "modelCalls": agent.calls, "isolatedContextIds": guarded.contexts,
            "apiFallback": False, "dailyWorkerActivated": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--exercise-refresh", action="store_true")
    args = parser.parse_args()
    try:
        result = execute(args.root, args.exercise_refresh)
    except Exception as error:
        result = {"probePassed": False, "reason": str(error)[:120] if type(error) is RuntimeError else type(error).__name__, "dailyWorkerActivated": False}
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["probePassed"] else 2)
