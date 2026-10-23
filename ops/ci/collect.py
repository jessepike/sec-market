#!/usr/bin/env python3
"""Private subscription worker using restored evidence and governed account auth."""
import argparse
import importlib.util
import json
import os
import signal
import sys
import time
from pathlib import Path

from auth_store import AuthStore
from bootstrap import GuardedRunner, PROJECT
from recover_lease import recover

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "web/scripts/pipeline"))
from agents import SubscriptionAgent
from contracts import digest, require, utcnow, validate_contract
from engine import Pipeline
from fetcher import Fetcher
from reporting import csv_matrix, inventory, markdown_matrix
from snapshot import build_snapshot
from storage import LocalStore
from validation import reconcile

spec = importlib.util.spec_from_file_location("session_runtime", REPO / "ops/cloud/run.py")
session_runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_runtime)


class BoundedPipeline(Pipeline):
    def __init__(self, *args, maximum_seconds=1200, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_deadline = time.monotonic() + maximum_seconds
        self.cancelled = False

    def stop(self, *_args):
        # Cooperative stop: finish/record in-flight work before snapshotting.
        # A SIGKILL retains the conservative remote escrow for unknown usage.
        self.cancelled = True
        self.account_deadline = 0

    def _task(self, plan, task):
        if self.cancelled:
            # Pipeline handles reservation failures as explicit task receipts.
            self.account_deadline = 0
        return super()._task(plan, task)

    def _reserve(self, kind, limit):
        require(time.monotonic() < self.account_deadline, "CI_COLLECTION_TIME_BUDGET_EXHAUSTED")
        return super()._reserve(kind, limit)


def escrow_budgets(root, state, session, contract, at):
    """Reserve remaining capacity remotely; a killed runner cannot reset it.

    A normal finish checkpoints actual usage. No snapshot races concurrent
    collection writes, and auth files stay outside archived state.
    """
    name = "budget-" + at[:10]
    before = state.read(f"heads/{name}.json")
    limits = {"calls": contract["model"]["maxCallsPerRun"],
              "documents": contract["model"]["maxDocumentsPerRun"],
              "fetches": contract["schedule"].get("maxFetchesPerRun", 5000)}
    ceiling = {**(before or {}), **{key: max((before or {}).get(key, 0), limit) for key, limit in limits.items()}}
    state.write_once(f"ci/budget-escrows/{digest(session['sessionId'])}.json",
                     {"sessionId": session["sessionId"], "day": at[:10], "before": before, "ceiling": ceiling})
    state.compare_and_swap(name, before, ceiling)
    session_runtime.checkpoint(root, state, session, "budget_reserved", {"day": at[:10], "ceiling": ceiling})
    # Only after remote acknowledgement can this runner use its reserved share.
    state.compare_and_swap(name, ceiling, before or {"calls": 0, "documents": 0, "fetches": 0})


def execution_outcome(complete, cancelled=False):
    """Keep runner completion separate from the unchanged coverage verdict."""
    return {"executionCompleted": not cancelled,
            "outcome": "cancelled" if cancelled else "completed_complete" if complete else "completed_with_gaps"}


def exit_code(result):
    return 0 if result.get('executionCompleted') is True else 2


def archive_collection_result(state, result, contract, attempt):
    """Bind the runner identity to actual reconciled collection evidence."""
    import re
    run_id = str(result['githubRunId'])
    require(re.fullmatch(r'[0-9]+', run_id) and re.fullmatch(r'[0-9]+', str(attempt)),
            'COLLECTION_RUN_IDENTITY_REQUIRED')
    fields = ('githubRunId', 'githubEventName', 'githubRef', 'appRevision', 'runId',
              'successfulTasks', 'requiredTasks', 'complete', 'executionCompleted', 'outcome')
    retained = {key: result[key] for key in fields}
    retained.update(githubRunAttempt=int(attempt), contractSha256=digest(contract))
    state.write_once(f'ci/collection-runs/{run_id}-{attempt}.json', retained)
    return retained


def execute(root, maximum_seconds=1200, publisher_config=None):
    require(os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_REPOSITORY") == PROJECT, "PRIVATE_GITHUB_RUNNER_REQUIRED")
    require(60 <= maximum_seconds <= 1200, "CI collection budget may not exceed twenty minutes")
    auth = os.environ.pop("SMP_CODEX_AUTH_JSON", "")
    writer = os.environ.pop("SMP_AUTH_STORE_TOKEN", "")
    require(auth and writer, "DEDICATED_ACCOUNT_AND_SECRET_WRITER_REQUIRED")
    root = Path(root).resolve()
    revision = session_runtime.git("rev-parse", "HEAD")
    identifier = "github-" + os.environ["GITHUB_RUN_ID"] + "-" + os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    recover(root / 'abandoned-lease-recovery')
    session_runtime.bootstrap(root, "collector", identifier, revision, execution_mode="github_subscription")
    state = LocalStore(root / "state")
    session = LocalStore(root).read("session.json")
    keeper = AuthStore(root / "auth", writer)
    try:
        keeper.restore(auth)
        os.environ["CODEX_HOME"] = str(keeper.home)
        contract = validate_contract(json.loads((REPO / "contracts/market.json").read_text()))
        guarded = GuardedRunner(keeper)
        agent = SubscriptionAgent(contract["model"], runner=guarded)
        collector = BoundedPipeline(contract, state, Fetcher(state), agent, maximum_seconds=maximum_seconds)
        previous_signals = {s: signal.getsignal(s) for s in (signal.SIGINT, signal.SIGTERM)}
        for signum in previous_signals:
            signal.signal(signum, collector.stop)
        # All restored checkpoints and daily budgets exist before model work.
        scheduled_at = utcnow()
        escrow_budgets(root, state, session, contract, scheduled_at)
        collected = collector.run(scheduled_at)
        session_runtime.checkpoint(root, state, session, "collection", session_runtime.summary(state))
        plan = state.read(f"runs/{collected['runId']}/plan.json")
        receipts = []
        for claimed in collected["receipts"]:
            archived = state.read(f"runs/{collected['runId']}/attempts/{claimed['attemptId']}.json")
            require(archived == claimed, "CI summary differs from archived evidence")
            receipts.append(archived)
        checked = reconcile(plan, receipts, contract, utcnow(), state)
        state.write_once(f"verifications/{collected['runId']}/{checked['checkedAt'].replace(':', '-')}.json", checked)
        previous = state.read("heads/dailySnapshot.json") or state.read("heads/cloud-snapshot.json")
        snapshot = build_snapshot(contract, plan, checked, state, utcnow(), previous=previous)
        state.compare_and_swap("dailySnapshot", state.read("heads/dailySnapshot.json"), snapshot)
        state.compare_and_swap("cloud-snapshot", state.read("heads/cloud-snapshot.json"), snapshot)
        rows = inventory(contract, utcnow(), checked)
        state.put(csv_matrix(rows).encode())
        state.put(markdown_matrix(contract, rows).encode())
        keeper.checkpoint()
        result = {"githubRunId": os.environ["GITHUB_RUN_ID"],
                  "githubEventName": os.environ.get("GITHUB_EVENT_NAME"),
                  "githubRef": os.environ.get("GITHUB_REF"), "appRevision": revision,
                  "runId": checked["runId"],
                  "successfulTasks": checked["successfulTasks"], "requiredTasks": checked["requiredTasks"],
                  "complete": checked["complete"], "modelCalls": agent.calls, "apiFallback": False,
                  "snapshotSha256": snapshot["snapshotSha256"], "reviewQueue": len(snapshot["reviewQueue"]),
                  "executionMode": "github_subscription", "publication": {"published": False, "reason": "INITIAL_CUTOVER_NOT_ENABLED"}}
        result.update(execution_outcome(checked['complete'], collector.cancelled))
        if contract["publication"]["enabled"]:
            # Publication has a separate runner/time budget and never receives
            # subscription auth. Its independent gate may take 35 minutes.
            result["publication"] = {"published": False, "reason": "SEPARATE_PUBLISHER_REQUIRED"}
        archive_collection_result(state, result, contract, os.environ.get('GITHUB_RUN_ATTEMPT', '1'))
        finished = session_runtime.checkpoint(root, state, session, "finish", result, finish=True)
        result["archive"] = finished["archive"]
        # A cancellation arriving during the final remote write still fails
        # execution, even if the durable evidence checkpoint succeeded.
        result.update(execution_outcome(checked['complete'], collector.cancelled))
        return result
    except Exception as error:
        session_runtime.checkpoint(root, state, session, "failed", {"errorType": type(error).__name__, "published": False}, finish=True)
        raise
    finally:
        if 'previous_signals' in locals():
            for signum, handler in previous_signals.items():
                signal.signal(signum, handler)
        # Never reset from bootstrap. Persist latest official-client state even
        # on model failure; any persistence error makes the job fail visibly.
        if (keeper.home / "auth.json").exists():
            keeper.checkpoint()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--maximum-seconds", type=int, default=1200)
    parser.add_argument("--publisher-config")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        result = execute(args.root, args.maximum_seconds, args.publisher_config)
    except Exception as error:
        result = {"complete": False, "executionCompleted": False, "outcome": "failed",
                  "reason": str(error)[:120] if type(error) is RuntimeError else type(error).__name__, "apiFallback": False}
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(exit_code(result))
