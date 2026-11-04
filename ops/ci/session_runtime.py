#!/usr/bin/env python3
"""Session runtime for the daily collector: restore, lease, bounded work and checkpoint.

Used by ops/ci/collect.py. Originally written for a Codex Cloud session (ops/cloud/run.py);
moved here when that route was retired. Publication retains the existing gate.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "web/scripts/pipeline"))
sys.path.insert(0, str(REPO / "ops/ci"))
from archive import GitArchive
from contracts import canonical, digest, instant, require, utcnow, validate_contract
from engine import Pipeline
from fetcher import Fetcher
from native import NativeAgent, pending_work, submit_work
from reporting import csv_matrix, inventory, markdown_matrix
from release import release_daily
from snapshot import build_snapshot
from storage import LocalStore
from validation import reconcile
from coverage_summary import coverage_details


def git(*args):
    result = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, timeout=180)
    require(result.returncode == 0, "CLOUD_REPOSITORY_OPERATION_FAILED")
    return result.stdout.strip()


def archive_for(root):
    return GitArchive(root / "archive", "https://github.com/jessepike/sec-market.git")


def require_source_probe_context(session_id):
    """Only the existing private, manual main workflow can own this profile."""
    require(os.environ.get('GITHUB_ACTIONS') == 'true'
            and os.environ.get('GITHUB_REPOSITORY') == 'jessepike/sec-market'
            and os.environ.get('GITHUB_REF') == 'refs/heads/main'
            and os.environ.get('GITHUB_EVENT_NAME') == 'workflow_dispatch', 'SOURCE_PROBE_PRIVATE_MANUAL_MAIN_REQUIRED')
    run_id, attempt = os.environ.get('GITHUB_RUN_ID', ''), os.environ.get('GITHUB_RUN_ATTEMPT', '')
    require(re.fullmatch(r'[1-9][0-9]*', run_id) and re.fullmatch(r'[1-9][0-9]*', attempt)
            and session_id == f'github-{run_id}-{attempt}', 'SOURCE_PROBE_RUN_IDENTITY_REQUIRED')
    event = json.loads(Path(os.environ.get('GITHUB_EVENT_PATH', '')).read_text())
    selected = event.get('inputs', {}).get('source_probe')
    require(event.get('repository', {}).get('full_name') == 'jessepike/sec-market'
            and event.get('repository', {}).get('private') is True
            and (selected is True or selected == 'true'), 'SOURCE_PROBE_DISPATCH_INPUT_REQUIRED')


def acquire_lease(store, session, now):
    previous = store.read("heads/cloud-lease.json")
    require(not previous or previous.get("releasedAt") or instant(previous["expiresAt"]) <= instant(now), "ANOTHER_CLOUD_SESSION_HAS_ACTIVE_LEASE")
    lease = {"sessionId": session["sessionId"], "role": session["role"], "startedAt": now,
             "expiresAt": (instant(now) + timedelta(hours=3)).isoformat().replace("+00:00", "Z")}
    if 'checkpointProfile' in session:
        require(session['checkpointProfile'] == 'source_probe', 'UNKNOWN_CHECKPOINT_PROFILE')
        lease['checkpointProfile'] = session['checkpointProfile']
        lease['sessionSha256'] = digest(session)
    store.compare_and_swap("cloud-lease", previous, lease)


def require_lease(store, session, now):
    lease = store.read("heads/cloud-lease.json")
    require(lease and lease["sessionId"] == session["sessionId"] and not lease.get("releasedAt")
            and instant(lease["expiresAt"]) > instant(now), "CLOUD_SESSION_LEASE_MISSING_OR_EXPIRED")


def summary(store):
    head = store.read("heads/latest-run.json")
    coverage = json.loads(store.get(head["receipt"])) if head else None
    return {"runId": coverage["runId"] if coverage else None,
            "successfulTasks": coverage["successfulTasks"] if coverage else 0,
            "requiredTasks": coverage["requiredTasks"] if coverage else None,
            "complete": bool(coverage and coverage["complete"]),
            **(coverage_details(coverage) if coverage else {})}


def checkpoint(root, store, session, phase, result, finish=False):
    now = utcnow()
    profile = session.get('checkpointProfile')
    lease = store.read('heads/cloud-lease.json')
    require(profile in (None, 'source_probe'), 'UNKNOWN_CHECKPOINT_PROFILE')
    if profile or (lease or {}).get('checkpointProfile'):
        require(profile == 'source_probe' and lease and lease.get('checkpointProfile') == profile
                and lease.get('sessionSha256') == digest(session)
                and session['role'] == 'collector' and session.get('executionMode') == 'github_subscription',
                'SOURCE_PROBE_PROFILE_UNBOUND')
        require_source_probe_context(session['sessionId'])
        require_lease(store, session, now)
        retained_session = LocalStore(root).read('session.json')
        require((retained_session is None and phase == 'bootstrap') or retained_session == session,
                'SOURCE_PROBE_SESSION_METADATA_DIFFERS')
        entry = {'sessionId': session['sessionId'], 'role': session['role'], 'appRevision': session['appRevision'],
                 'checkpointProfile': profile, 'phase': phase, 'recordedAt': now, 'result': result,
                 'contractSha256': digest(json.loads((REPO / 'contracts/market.json').read_text()))}
        store.write_once(f"ci/source-probe-checkpoints/{digest(session['sessionId'])}/{digest(entry)}.json", entry)
    else:
        entry = collection_checkpoint(store, session, phase, result, now)
    if finish:
        lease = store.read("heads/cloud-lease.json")
        require(lease and lease["sessionId"] == session["sessionId"], "CLOUD_LEASE_CHANGED")
        store.compare_and_swap("cloud-lease", lease, {**lease, "releasedAt": now})
    runtime = LocalStore(root)
    previous_ack = runtime.read("heads/remote-archive.json")
    expected = previous_ack["commit"] if previous_ack else session["restored"]["commit"]
    acknowledged = archive_for(root).push(store, expected_commit=expected)
    runtime.compare_and_swap("remote-archive", previous_ack, acknowledged)
    return {"receipt": entry, "archive": acknowledged}


def collection_checkpoint(store, session, phase, result, now):
    """The default collection/heartbeat protocol remains unchanged."""
    entry = {"sessionId": session["sessionId"], "role": session["role"], "appRevision": session["appRevision"],
             "phase": phase, "checkedAt": now, "coverage": summary(store), "result": result,
             "contractSha256": digest(json.loads((REPO / "contracts/market.json").read_text())),
             "publication": "held_until_live_gate_and_cutover"}
    store.write_once(f"cloud/sessions/{digest(session['sessionId'])}/{digest(entry)}.json", entry)
    name = "cloud-" + session["role"]
    store.compare_and_swap(name, store.read(f"heads/{name}.json"), entry)
    heartbeat = {"executionMode": session.get("executionMode", "codex_cloud_native"), "startedAt": session["startedAt"], "finishedAt": now,
                 "appRevision": session["appRevision"], "role": session["role"], "sessionId": session["sessionId"],
                 "phases": {phase: 0 if phase == "finish" and result.get("executionCompleted", True) else 2},
                 "coverageComplete": entry["coverage"]["complete"],
                 "publication": result.get("publication", entry["publication"]) if isinstance(result, dict) else entry["publication"]}
    store.compare_and_swap("worker-heartbeat", store.read("heads/worker-heartbeat.json"), heartbeat)
    return entry


def bootstrap(root, role, session_id, revision, execution_mode="codex_cloud_native", checkpoint_profile=None):
    require(role in ("collector", "governance") and session_id and len(session_id) <= 160, "CLOUD_ROLE_AND_CONTEXT_REQUIRED")
    require(checkpoint_profile in (None, 'source_probe'), 'UNKNOWN_CHECKPOINT_PROFILE')
    if checkpoint_profile:
        require(role == 'collector' and execution_mode == 'github_subscription', 'SOURCE_PROBE_PROFILE_UNBOUND')
        require_source_probe_context(session_id)
    require(revision == git("rev-parse", "HEAD"), "CLOUD_REVISION_DIFFERS_FROM_REVIEWED_PIN")
    require(not git("status", "--porcelain", "--untracked-files=normal"), "CLOUD_CHECKOUT_MUST_BE_CLEAN")
    require(not root.is_relative_to(REPO), "Cloud runtime must be outside application checkout")
    require(not (root / "session.json").exists(), "Cloud session already initialized; resume without bootstrap")
    require(shutil.disk_usage(root.parent).free > 5_000_000_000, "INSUFFICIENT_SPACE_FOR_VERIFIED_ARCHIVE_RESTORE")
    for program in ("git", "gh", "node", "pdftotext"):
        require(shutil.which(program), "CLOUD_DEPENDENCY_MISSING_" + program.upper())
    version = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True).stdout.strip()
    require(version.startswith("v22."), "Cloud worker requires reviewed Node 22 runtime")
    root.mkdir(parents=True, exist_ok=True)
    restored = archive_for(root).restore(root / "state")
    store = LocalStore(root / "state")
    require(execution_mode in ("codex_cloud_native", "github_subscription"), "Unknown execution mode")
    session = {"schemaVersion": 1, "sessionId": session_id, "role": role, "appRevision": revision, "executionMode": execution_mode,
               "startedAt": utcnow(), "restored": restored}
    if checkpoint_profile:
        session['checkpointProfile'] = checkpoint_profile
    acquire_lease(store, session, session["startedAt"])
    # Win the remote fast-forward race before exposing any model work or budgets.
    receipt = checkpoint(root, store, session, "bootstrap", {"restored": restored})
    LocalStore(root).write_once("session.json", session)
    return receipt


def execute(args):
    root = Path(args.root).resolve()
    require(not root.is_relative_to(REPO), "Cloud runtime must be outside application checkout")
    if args.command == "bootstrap":
        return bootstrap(root, args.role, args.session_id, args.revision)
    session = LocalStore(root).read("session.json")
    require(session is not None, "Bootstrap a fresh cloud runtime first")
    require(not session.get('checkpointProfile'), 'SOURCE_PROBE_NATIVE_WORK_FORBIDDEN')
    require(session["appRevision"] == git("rev-parse", "HEAD"), "CLOUD_APPLICATION_PIN_CHANGED")
    require(not git("status", "--porcelain", "--untracked-files=normal"), "CLOUD_CHECKOUT_MUST_BE_CLEAN")
    store = LocalStore(root / "state")
    contract = validate_contract(json.loads((REPO / "contracts/market.json").read_text()))
    with store.lock("cloud-operation"):
        require_lease(store, session, utcnow())
        if args.command == "pending":
            ack = LocalStore(root).read("heads/remote-archive.json")
            remote = archive_for(root)
            refs = remote._git("ls-remote", "origin", remote.remote_ref).stdout.decode().split()
            require(refs and ack and refs[0] == ack["commit"], "REMOTE_ARCHIVE_CHANGED_BEFORE_NATIVE_WORK")
            tasks = pending_work(store, digest(contract), session["role"])
            if args.task_id:
                tasks = [t for t in tasks if t["taskId"] == args.task_id]
            # Return metadata by default to keep a large queue out of model context.
            return {"pending": len(tasks), "tasks": tasks if args.task_id else [
                {"taskId": t["taskId"], "stage": t["request"]["stage"], "createdAt": t["createdAt"]} for t in tasks]}
        try:
            if args.command == "advance":
                latest = store.read("heads/latest-run.json")
                old = json.loads(store.get(latest["receipt"])) if latest else None
                old_plan = store.read(f"runs/{old['runId']}/plan.json") if old else None
                at = old_plan["scheduledAt"] if old_plan and old_plan["contractSha256"] == digest(contract) and old_plan["scheduledAt"][:10] == utcnow()[:10] else utcnow()
                agent = NativeAgent(contract["model"], store, digest(contract), session["sessionId"])
                Pipeline(contract, store, Fetcher(store), agent).run(at, replay=True)
                result = summary(store)
            elif args.command == "submit":
                require(args.response_file and args.task_id, "Task and response file required")
                path = Path(args.response_file)
                require(path.stat().st_size <= 1_000_000, "Native response exceeds byte budget")
                answer = submit_work(store, args.task_id, json.loads(path.read_text()), session["role"], session["sessionId"], digest(contract))
                result = {"taskId": answer["taskId"], "submittedAt": answer["submittedAt"]}
            else:
                require(args.command == "finish", "Unknown cloud command")
                latest = store.read("heads/latest-run.json")
                require(latest is not None, "No collection receipt to validate")
                coverage = json.loads(store.get(latest["receipt"]))
                plan = store.read(f"runs/{coverage['runId']}/plan.json")
                receipts = []
                for claimed in coverage["receipts"]:
                    archived = store.read(f"runs/{coverage['runId']}/attempts/{claimed['attemptId']}.json")
                    require(archived == claimed, "Cloud summary differs from task evidence")
                    receipts.append(archived)
                verified = reconcile(plan, receipts, contract, utcnow(), store)
                store.write_once(f"verifications/{coverage['runId']}/{verified['checkedAt'].replace(':', '-')}.json", verified)
                prior_snapshot = store.read("heads/cloud-snapshot.json") or store.read("heads/dailySnapshot.json")
                snapshot = build_snapshot(contract, plan, verified, store, utcnow(), previous=prior_snapshot)
                store.compare_and_swap("cloud-snapshot", store.read("heads/cloud-snapshot.json"), snapshot)
                rows = inventory(contract, utcnow(), verified)
                store.put(csv_matrix(rows).encode())
                store.put(markdown_matrix(contract, rows).encode())
                result = {**summary(store), "verifiedComplete": verified["complete"], "snapshotSha256": snapshot["snapshotSha256"],
                          "events": len(snapshot["events"]), "reviewQueue": len(snapshot["reviewQueue"])}
                if session["role"] == "governance" and contract["publication"]["enabled"]:
                    require(args.publisher_config, "Cloud publication requires reviewed managed Vercel configuration")
                    config = json.loads(Path(args.publisher_config).read_text())
                    require(set(config) == {"vercel"}, "Cloud publisher configuration must contain only Vercel adapter settings")
                    archived = checkpoint(root, store, session, "gate_requested", result)["archive"]
                    result["publication"] = release_daily(store, contract, archived, session["appRevision"], config,
                        checkpoint=lambda: checkpoint(root, store, session, "publication_journal", {})["archive"])
            return checkpoint(root, store, session, args.command, result, finish=args.command == "finish")
        except Exception as error:
            # Save the failure and release the lease if possible; never report readiness.
            checkpoint(root, store, session, "failed", {"ok": False, "errorType": type(error).__name__}, finish=True)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["bootstrap", "advance", "pending", "submit", "finish"])
    parser.add_argument("--root", required=True, help="Fresh session directory outside the app checkout")
    parser.add_argument("--role", choices=["collector", "governance"])
    parser.add_argument("--session-id")
    parser.add_argument("--revision")
    parser.add_argument("--task-id")
    parser.add_argument("--response-file")
    parser.add_argument("--publisher-config", help="Outside-checkout Vercel adapter settings; credentials remain in managed storage")
    args = parser.parse_args()
    try:
        result = execute(args)
        print(json.dumps(result, indent=2))
        coverage = result.get("receipt", {}).get("coverage", {})
        return 2 if args.command == "finish" and not coverage.get("complete") else 0
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(json.dumps({"ok": False, "errorType": type(error).__name__, "reason": str(error)[:180]}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
