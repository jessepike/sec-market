#!/usr/bin/env python3
"""Daily pipeline commands. A failed/degraded run deliberately exits nonzero."""
import argparse
import json
import re
import sys
from pathlib import Path

from agents import SubscriptionAgent
from native import NativeAgent, pending_work, submit_work
from contracts import digest, plan_run, utcnow, validate_contract
from engine import Pipeline
from fetcher import Fetcher
from publication import health
from selection import load_history_policy
from reporting import csv_matrix, inventory, markdown_matrix
from validation import reconcile
from storage import LocalStore
from snapshot import build_snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check-contracts", "plan", "run", "verify", "snapshot", "onboard", "status", "report", "backup", "verify-backup", "archive-push", "archive-restore", "native-pending", "native-submit"])
    parser.add_argument("--contract", default=str(Path(__file__).resolve().parents[3] / "contracts/market.json"))
    parser.add_argument("--state", default=str(Path(__file__).resolve().parents[3] / ".collect/daily-state"))
    parser.add_argument("--at", default=None)
    parser.add_argument("--destination")
    parser.add_argument("--baseline", help="Optional exported baseline supplier JSON")
    parser.add_argument("--expected-sha256", help="Independently retained backup root hash")
    parser.add_argument("--archive-mirror", help="Dedicated Git mirror outside the live state directory")
    parser.add_argument("--archive-remote", default="https://github.com/jessepike/sec-market.git")
    parser.add_argument("--expected-commit", help="Pinned remote archive commit for push or restoration")
    parser.add_argument("--subscription-worker", action="store_true", help="Use existing ChatGPT-authenticated Codex CLI; never API-key fallback")
    parser.add_argument("--native-worker", action="store_true", help="Queue model work for the scheduled native Codex agent; no nested login")
    parser.add_argument("--role", choices=["collector", "governance"])
    parser.add_argument("--session-id", help="Actual native task/chat context identifier; not a credential")
    parser.add_argument("--task-id")
    parser.add_argument("--response-file")
    args = parser.parse_args()
    if args.command == 'onboard':
        parser.error('Standalone live onboarding is disabled; use the private main collector workflow manual source_probe input for leased diagnostics')
    if args.command == 'archive-push' and not re.fullmatch(r'[0-9a-f]{40}', args.expected_commit or ''):
        parser.error('archive-push requires --expected-commit with the full acknowledged remote commit')
    contract = validate_contract(json.loads(Path(args.contract).read_text()))
    store = LocalStore(args.state)
    at = args.at or utcnow()
    if args.command == "check-contracts":
        result = {"valid": True, "suppliers": len(contract["suppliers"]), "sourceBindings": len(contract["sources"]), "reconciliation": "every daily run", "paidApiFallback": False}
    elif args.command == "plan":
        result = plan_run(contract, at)
    elif args.command == "run":
        if args.native_worker and (args.subscription_worker or not args.session_id):
            parser.error("Native work requires --session-id and cannot also select the CLI worker")
        agent = SubscriptionAgent(contract["model"]) if args.subscription_worker else None
        if args.native_worker:
            agent = NativeAgent(contract["model"], store, digest(contract), args.session_id)
        # The history policy sits beside the contract and is optional: no file, no archive cut.
        history = load_history_policy(Path(args.contract).with_name('history-window.json'))
        result = Pipeline(contract, store, Fetcher(store), agent, history=history).run(at, replay=args.native_worker)
    elif args.command == "native-pending":
        if not args.role:
            parser.error("--role required")
        tasks = pending_work(store, digest(contract), args.role, at)
        if args.task_id:
            tasks = [task for task in tasks if task["taskId"] == args.task_id]
        result = {"pending": len(tasks), "tasks": tasks}
    elif args.command == "native-submit":
        if not all((args.task_id, args.response_file, args.role, args.session_id)):
            parser.error("Submit requires --task-id, --response-file, --role and --session-id")
        result = submit_work(store, args.task_id, json.loads(Path(args.response_file).read_text()), args.role, args.session_id, digest(contract), at)
    elif args.command == "snapshot":
        if not args.destination:
            parser.error("--destination required")
        latest = store.read("heads/latest-run.json")
        if not latest:
            raise ValueError("No archived daily run to materialize")
        coverage = json.loads(store.get(latest["receipt"]))
        plan = store.read(f"runs/{coverage['runId']}/plan.json")
        path = Path(args.destination)
        previous = json.loads(path.read_text()) if path.exists() else None
        baseline = json.loads(Path(args.baseline).read_text()) if args.baseline else None
        result = build_snapshot(contract, plan, coverage, store, at, baseline, previous)
        body = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        path.with_suffix(".seal.json").write_text(json.dumps({"schemaVersion": 1, "fileSha256": digest(body), "runId": result["runId"], "contractSha256": result["contractSha256"]}, indent=2) + "\n")
        result = {"snapshotSha256": result["snapshotSha256"], "fileSha256": digest(body), "events": len(result["events"]), "supplierUpdates": len(result["supplierUpdates"]), "reviewQueue": len(result["reviewQueue"])}
    elif args.command in ("status", "verify"):
        latest = store.read("heads/latest-run.json")
        coverage = json.loads(store.get(latest["receipt"])) if latest else None
        if args.command == "verify" and coverage:
            plan = store.read(f"runs/{coverage['runId']}/plan.json")
            receipts = []
            for claimed in coverage["receipts"]:
                archived = store.read(f"runs/{coverage['runId']}/attempts/{claimed['attemptId']}.json")
                if archived != claimed:
                    raise ValueError("Worker summary differs from archived task receipt")
                receipts.append(archived)
            result = reconcile(plan, receipts, contract, at, store)
            store.write_once(f"verifications/{coverage['runId']}/{result['checkedAt'].replace(':', '-')}.json", result)
        else:
            result = health(coverage, at, contract["schedule"]["overdueHours"], digest(contract))
    elif args.command == "report":
        if not args.destination:
            parser.error("--destination required")
        latest = store.read("heads/latest-run.json")
        coverage = json.loads(store.get(latest["receipt"])) if latest else None
        rows = inventory(contract, at, coverage)
        destination = Path(args.destination)
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "source-matrix.csv").write_text(csv_matrix(rows))
        (destination / "coverage-matrix.md").write_text(markdown_matrix(contract, rows))
        result = {"suppliers": len(contract["suppliers"]), "requiredTasks": len(rows), "missingBindings": sum(r["registration"] == "missing" for r in rows), "candidateBindings": sum(r["registration"] == "candidate" for r in rows)}
    elif args.command in ("archive-push", "archive-restore"):
        from archive import GitArchive
        if not args.archive_mirror:
            parser.error("--archive-mirror required")
        archive = GitArchive(args.archive_mirror, args.archive_remote)
        if args.command == "archive-push":
            result = archive.push(store, expected_commit=args.expected_commit)
        else:
            if not args.destination or not args.expected_commit or not args.expected_sha256:
                parser.error("Restore requires --destination, --expected-commit and --expected-sha256")
            result = archive.restore(args.destination, args.expected_commit, args.expected_sha256)
    elif args.command == "backup":
        if not args.destination:
            parser.error("--destination required")
        result = store.export(args.destination)
    else:
        if not args.expected_sha256:
            parser.error("--expected-sha256 required for backup verification")
        result = LocalStore.verify_export(args.destination or args.state, args.expected_sha256)
    print(json.dumps(result, indent=2))
    if result.get("complete") is False or result.get("healthy") is False:
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, RuntimeError) as error:
        print(json.dumps({"ok": False, "errorType": type(error).__name__, "reason": str(error)[:180]}), file=sys.stderr)
        sys.exit(2)
