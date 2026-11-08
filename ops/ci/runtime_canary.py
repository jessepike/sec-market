#!/usr/bin/env python3
"""Private hosting/archive integrity proof without market-source transport."""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "web/scripts/pipeline"))
from archive import EVIDENCE_REMOTE, GitArchive
from contracts import digest, instant, plan_run, require, utcnow, validate_contract
from storage import LocalStore
from coverage_summary import coverage_details


def run(root):
    require(os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_REPOSITORY") == "jessepike/sec-market", "Use the actual repository's GitHub runner")
    event = json.loads(Path(os.environ.get('GITHUB_EVENT_PATH', '')).read_text())
    require(event.get('repository', {}).get('full_name') == 'jessepike/sec-market', 'GITHUB_HOSTING_CONTEXT_REQUIRED')
    root = Path(root).resolve()
    require(not root.is_relative_to(REPO), "Canary state must be outside the application checkout")
    require(shutil.disk_usage(root.parent).free >= 5_000_000_000, "Insufficient disk for verified archive restore")
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    archive = GitArchive(root / "mirror", EVIDENCE_REMOTE)
    restored = archive.restore(root / "state")
    state = LocalStore(root / "state")
    latest = state.read("heads/latest-run.json")
    require(latest is not None, "Archive has no collection receipt")
    coverage = json.loads(state.get(latest["receipt"]))
    contract = validate_contract(json.loads((REPO / "contracts/market.json").read_text()))
    require(coverage["contractSha256"] == digest(contract), "Canary archive uses another source contract")
    require(latest['runId'] == coverage['runId'], 'CANARY_ARCHIVED_RUN_IDENTITY_DIFFERS')
    plan = state.read(f"runs/{coverage['runId']}/plan.json")
    require(plan is not None and plan == plan_run(contract, plan['scheduledAt'], plan.get('previousRunId')),
            'CANARY_ARCHIVED_PLAN_DIFFERS')
    require(coverage['inventorySha256'] == plan['inventorySha256']
            and coverage['supplierCount'] == len(contract['suppliers'])
            and type(coverage['requiredTasks']) is int
            and coverage['requiredTasks'] == sum(t['required'] for t in plan['tasks'])
            and type(coverage['successfulTasks']) is int
            and 0 <= coverage['successfulTasks'] <= coverage['requiredTasks']
            and type(coverage['complete']) is bool
            and coverage['complete'] == (coverage['requiredTasks'] > 0 and coverage['successfulTasks'] == coverage['requiredTasks']),
            'CANARY_ARCHIVED_COVERAGE_INVENTORY_DIFFERS')
    details = coverage_details(coverage)
    instant(coverage['checkedAt'])
    receipts = coverage['receipts']
    tasks = {task['taskId']: task for task in plan['tasks']}
    require(len(receipts) == len(tasks) and {row['taskId'] for row in receipts} == set(tasks),
            'CANARY_ARCHIVED_ATTEMPT_INVENTORY_DIFFERS')
    for row in receipts:
        require(row['runId'] == plan['runId'] and row['sourceId'] == tasks[row['taskId']]['sourceId']
                and state.read(f"runs/{plan['runId']}/attempts/{row['attemptId']}.json") == row,
                'CANARY_ARCHIVED_ATTEMPT_DIFFERS')
    result = {"kind": "credential-free-github-host-canary", "checkedAt": utcnow(),
              'runtimeCanaryScope': 'private_hosting_archive_integrity',
              "appRevision": revision, "githubRunId": os.environ.get("GITHUB_RUN_ID"),
              "runnerOs": platform.system(), "archive": restored,
              "archivedCoverage": {"runId": coverage["runId"], 'checkedAt': coverage['checkedAt'], 'historical': True,
                  'receiptSha256': latest['receipt']['sha256'], 'inventorySha256': plan['inventorySha256'],
                  "successfulTasks": coverage["successfulTasks"], "requiredTasks": coverage["requiredTasks"], "complete": coverage["complete"], **details},
              **noncollection_fields(),
              "modelCalls": 0, "subscriptionCredentialsTransferred": False,
              "archiveChanged": False, "publicationAttempted": False,
              "recurringWorkerActivated": False, "runtimeCanaryPassed": True}
    return result


def noncollection_fields():
    return {'sourceProbe': {'performed': False, 'reason': 'LEASED_COLLECTOR_WORKFLOW_REQUIRED'},
            'marketSourceRequests': 0, 'sourceChecksCredited': 0, 'qualifiedSources': 0,
            'coverageCredit': False, 'semanticAdmission': False}


def failure(error):
    return {'runtimeCanaryScope': 'private_hosting_archive_integrity', 'runtimeCanaryPassed': False,
            'reason': type(error).__name__, **noncollection_fields(), 'modelCalls': 0,
            'subscriptionCredentialsTransferred': False, 'archiveChanged': False,
            'publicationAttempted': False, 'recurringWorkerActivated': False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        result = run(args.root)
    except (ValueError, OSError, RuntimeError, KeyError, TypeError, subprocess.SubprocessError) as error:
        result = failure(error)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["runtimeCanaryPassed"] else 2)
