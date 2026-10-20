#!/usr/bin/env python3
"""Daily pipeline commands. A failed/degraded run deliberately exits nonzero."""
import argparse
import json
import sys
from pathlib import Path

from agents import SubscriptionAgent
from contracts import digest, plan_run, utcnow, validate_contract
from engine import Pipeline
from fetcher import Fetcher
from publication import health
from reporting import csv_matrix, inventory, markdown_matrix
from validation import reconcile
from storage import LocalStore


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check-contracts", "plan", "run", "verify", "status", "report", "backup", "verify-backup"])
    parser.add_argument("--contract", default=str(Path(__file__).resolve().parents[3] / "contracts/market.json"))
    parser.add_argument("--state", default=str(Path(__file__).resolve().parents[3] / ".collect/daily-state"))
    parser.add_argument("--at", default=None)
    parser.add_argument("--destination")
    parser.add_argument("--expected-sha256", help="Independently retained backup root hash")
    parser.add_argument("--subscription-worker", action="store_true", help="Use existing ChatGPT-authenticated Codex CLI; never API-key fallback")
    args = parser.parse_args()
    contract = validate_contract(json.loads(Path(args.contract).read_text()))
    store = LocalStore(args.state)
    at = args.at or utcnow()
    if args.command == "check-contracts":
        result = {"valid": True, "suppliers": len(contract["suppliers"]), "sourceBindings": len(contract["sources"]), "reconciliation": "every daily run", "paidApiFallback": False}
    elif args.command == "plan":
        result = plan_run(contract, at)
    elif args.command == "run":
        agent = SubscriptionAgent(contract["model"]) if args.subscription_worker else None
        result = Pipeline(contract, store, Fetcher(store), agent).run(at)
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
