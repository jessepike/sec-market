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

import timer
from auth_store import AuthStore
from bootstrap import GuardedRunner, PROJECT
from recover_lease import recover, github_run
from schedule_guard import ACCEPTANCE_CRONS, ACCEPTANCE_DATE

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "web/scripts/pipeline"))
from agents import ModelUnavailable, SubscriptionAgent
from contracts import digest, instant, require, utcnow, validate_contract
from engine import Pipeline
from fetcher import Fetcher
from selection import load_history_policy
from reporting import csv_matrix, inventory, markdown_matrix
from onboarding import PersistentProbeBudget, ProbeReservationDenied, probe_sources, validate_qualification_probe_plan
from snapshot import build_snapshot
from storage import LocalStore
from validation import reconcile
from coverage_summary import coverage_details

spec = importlib.util.spec_from_file_location("session_runtime", REPO / "ops/ci/session_runtime.py")
session_runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_runtime)


# The collect step runs inside a 45-minute job. About 2 minutes go to setup
# before this script starts and about 2 to cleanup after it, so the script must
# finish within 40 minutes. The work after collection (two evidence checks, the
# snapshot and two archive pushes) is reserved before collection starts: on
# November 5 a fixed 20-minute collection left too little time for it and the
# job was cancelled with nothing recorded for the day. On November 7, the first
# run with 603 sources, that work took 14 minutes against a 10-minute reserve
# and the job ended 7 seconds inside its old 35-minute limit. On November 8,
# with 667 sources, the last in-flight requests ran 163 seconds past the
# collection budget and the closing work (mostly reconcile's retained-evidence
# replay) took 1161 seconds: 2524 seconds in all, and the job ended 104 seconds
# inside its 45-minute limit. The reserve covers both with about 3 minutes spare.
STEP_SECONDS = 2400
POST_COLLECTION_RESERVE_SECONDS = 1500
MINIMUM_COLLECTION_SECONDS = 300


def collection_seconds(maximum_seconds, started, now, step_seconds=STEP_SECONDS,
                       reserve=POST_COLLECTION_RESERVE_SECONDS):
    """Collection time left once restore is done and the closing work is reserved.

    A short collection records fewer sources; a cancelled job records nothing.
    """
    left = int(step_seconds - (now - started) - reserve)
    require(left >= MINIMUM_COLLECTION_SECONDS, "CI_STEP_TIME_EXHAUSTED_BEFORE_COLLECTION")
    return min(maximum_seconds, left)


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

    def _work_cancelled(self):
        return time.monotonic() >= self.account_deadline or super()._work_cancelled()


def correction_work(repo, state, contract, agent):
    """Enable the separate group review only for a committed requests contract."""
    requests = Path(repo) / 'contracts/factual-corrections.json'
    if not requests.exists():
        return None

    def process(*, reserve, now, cancelled):
        from corrections import process_corrections
        try:
            return process_corrections(repo, state, contract, agent, reserve, now, cancelled=cancelled)
        except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
            # Keep invalid-policy/input work visible without losing the source
            # collection. Only the admission adapter can produce admissions.
            reason = str(exc)[:160] if isinstance(exc, (ValueError, ModelUnavailable)) else type(exc).__name__
            try:
                groups = json.loads(requests.read_text()).get('groups', [])
                pending = [{'groupId': g['id'], 'reason': reason} for g in groups]
            except (ValueError, OSError, KeyError, TypeError):
                pending = []
            return {'policySha256': None, 'admitted': [], 'pending': pending, 'attempts': [], 'error': reason}

    return process


def scheduled_source_refresh():
    """Only the normal trusted daily main timer starts a forced transport cycle."""
    return (os.environ.get('GITHUB_ACTIONS') == 'true'
            and os.environ.get('GITHUB_REPOSITORY') == PROJECT
            and timer.trusted_environment())


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
    if session.get('checkpointProfile') is not None:
        lease = state.read('heads/cloud-lease.json')
        require(session.get('checkpointProfile') == 'source_probe' and lease
                and lease.get('checkpointProfile') == 'source_probe'
                and lease.get('sessionSha256') == digest(session)
                and LocalStore(root).read('session.json') == session, 'SOURCE_PROBE_PROFILE_UNBOUND')
        session_runtime.require_source_probe_context(session['sessionId'])
        session_runtime.require_lease(state, session, utcnow())
        # Diagnostics can consume fetches only. A killed probe cannot imply
        # unknown model calls/documents, so retain those exact prior counters.
        limits = {'fetches': limits['fetches']}
    ceiling = {**(before or {}), **{key: max((before or {}).get(key, 0), limit) for key, limit in limits.items()}}
    state.write_once(f"ci/budget-escrows/{digest(session['sessionId'])}.json",
                     {"sessionId": session["sessionId"], "day": at[:10], "before": before, "ceiling": ceiling})
    state.compare_and_swap(name, before, ceiling)
    session_runtime.checkpoint(root, state, session, "budget_reserved", {"day": at[:10], "ceiling": ceiling})
    # Only after remote acknowledgement can this runner use its reserved share.
    state.compare_and_swap(name, ceiling, before or {"calls": 0, "documents": 0, "fetches": 0})


def execution_outcome(complete, cancelled=False, coverage=None):
    """Keep runner completion separate from the unchanged coverage verdict."""
    separated = coverage_details(coverage) if coverage is not None else {}
    outcome = ("completed_intake" if complete else "completed_intake_with_gaps") if separated else ("completed_complete" if complete else "completed_with_gaps")
    return {"executionCompleted": not cancelled, "outcome": "cancelled" if cancelled else outcome, **separated}


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
    for key in ('githubTimer','reusesScheduledCollectionRunId','sourceReceiptSha256','sourceCheckedAt','corrections',
                'coverageMeasure','intake','processing','historicalReview'):
        if key in result:
            retained[key]=result[key]
    retained.update(githubRunAttempt=int(attempt), contractSha256=digest(contract))
    state.write_once(f'ci/collection-runs/{run_id}-{attempt}.json', retained)
    return retained


def verified_scheduled_source(state, contract, now, lookup=github_run):
    """Return actual completed timer evidence without changing source work."""
    latest=state.read('heads/latest-run.json')
    if not latest:
        return None
    coverage=json.loads(state.get(latest['receipt']))
    age=(instant(now)-instant(coverage['checkedAt'])).total_seconds()/3600
    if coverage.get('contractSha256') != digest(contract) or coverage.get('requiredTasks',0) <= 0 \
            or not 0 <= age <= contract['schedule']['overdueHours']:
        return None
    details = coverage_details(coverage)
    summary=(state.read('heads/cloud-collector.json') or {}).get('coverage',{})
    if any(summary.get(k) != coverage.get(k) for k in ('runId','successfulTasks','requiredTasks','complete')):
        return None
    if any(summary.get(k) != v for k, v in details.items()):
        return None
    selected=None
    for path in sorted((state.root/'ci/collection-runs').glob('*.json'),reverse=True):
        clock=json.loads(path.read_text())
        if clock.get('executionCompleted') is not True or not timer.trusted_clock(clock) \
                or clock.get('githubRef') != 'refs/heads/main' or clock.get('runId') != coverage['runId'] \
                or clock.get('contractSha256') != digest(contract):
            continue
        run=lookup(str(clock['githubRunId']))
        if run.get('id') != int(clock['githubRunId']) or run.get('repository',{}).get('full_name') != PROJECT \
                or run.get('repository',{}).get('private') is not True \
                or run.get('path') != '.github/workflows/subscription-collector.yml' \
                or run.get('status') != 'completed' or run.get('conclusion') != 'success' \
                or not timer.trusted_run(run) or run.get('event') != clock.get('githubEventName') \
                or run.get('head_branch') != 'main' \
                or run.get('head_sha') != clock.get('appRevision') \
                or run.get('run_attempt') != clock.get('githubRunAttempt') \
                or run.get('created_at','')[:10] != now[:10]:
            continue
        if any(clock.get(k) != coverage.get(k) for k in ('successfulTasks','requiredTasks','complete')):
            continue
        if any(clock.get(k) != v for k, v in details.items()):
            continue
        selected={'githubRunId':run['id'],'clock':clock,'run':run,'coverage':coverage,'receipt':latest['receipt']}
        break
    if selected is None:
        return None
    plan=state.read(f"runs/{coverage['runId']}/plan.json")
    receipts=[state.read(f"runs/{coverage['runId']}/attempts/{r['attemptId']}.json") for r in coverage['receipts']]
    require(receipts == coverage['receipts'],'REUSED_SCHEDULE_RECEIPTS_DIFFER')
    original=reconcile(plan,receipts,contract,coverage['checkedAt'],state)
    require(original == coverage,'REUSED_SCHEDULE_RECONCILIATION_DIFFERS')
    current=reconcile(plan,receipts,contract,now,state)
    if any(current.get(k) != coverage.get(k) for k in ('successfulTasks','requiredTasks','complete','gapTaskIds')):
        return None
    if coverage_details(current) != details:
        return None
    return selected


def reuse_scheduled_collection(state, contract, now, lookup=github_run, corrections_enabled=False):
    """Reuse verified timer work only for the date-bound acceptance retries."""
    # Even an unchanged market contract can acquire new correction requests.
    # Replay source receipts and let the adapter validate its exact cache.
    if corrections_enabled:
        return None
    if os.environ.get('GITHUB_EVENT_NAME') != 'schedule' or os.environ.get('GITHUB_REF') != 'refs/heads/main' \
            or os.environ.get('SMP_EVENT_SCHEDULE') not in ACCEPTANCE_CRONS or now[:10] != ACCEPTANCE_DATE:
        return None
    source=verified_scheduled_source(state,contract,now,lookup)
    if not source:
        return None
    coverage=source['coverage']
    return {'githubRunId':os.environ['GITHUB_RUN_ID'],'githubEventName':'schedule','githubRef':'refs/heads/main',
            'appRevision':session_runtime.git('rev-parse','HEAD'),'runId':coverage['runId'],
            'successfulTasks':coverage['successfulTasks'],'requiredTasks':coverage['requiredTasks'],
            'complete':coverage['complete'],'executionCompleted':True,'outcome':'source_work_reused',
            **coverage_details(coverage),
            'reusesScheduledCollectionRunId':source['githubRunId'],'sourceReceiptSha256':source['receipt']['sha256'],
            'sourceCheckedAt':coverage['checkedAt'],'modelCalls':0,'fetches':0,'apiFallback':False,
            'executionMode':'github_subscription','publication':{'published':False,'reason':'SEPARATE_PUBLISHER_REQUIRED'}}


def execute_source_probe(root, state, session, contract, maximum_seconds):
    """Leased diagnostics share escrow/CAS but never collection or account work."""
    require(session.get('checkpointProfile') == 'source_probe', 'SOURCE_PROBE_PROFILE_UNBOUND')
    session_runtime.require_source_probe_context(session['sessionId'])
    cancelled = False
    previous_signals = {}
    selected_q4 = False
    try:
        qualification_plan = REPO / 'contracts/source-qualification-probes.json'
        qualification_raw = qualification_plan.read_bytes()
        require(0 < len(qualification_raw) <= 1_000_000, 'QUALIFICATION_PLAN_SIZE_INVALID')
        selected_plan = json.loads(qualification_raw)
        selected_q4 = isinstance(selected_plan, dict) and selected_plan.get('operation') in (
            'bounded_q4_controller_capture', 'bounded_q4_initial_data_capture', 'bounded_q4_primary_qualification',
            'bounded_cyera_primary_capture', 'bounded_prnewswire_primary_capture')
        orca = None
        q4 = None
        if isinstance(selected_plan, dict) and selected_plan.get('operation') == 'bounded_orca_qualification':
            import orca_qualification as orca
            orca_plan = orca.validate_plan(contract, state, qualification_raw, qualification_plan)
        elif isinstance(selected_plan, dict) and selected_plan.get('operation') == 'bounded_q4_controller_capture':
            import q4_controller_capture as q4
            q4_plan = q4.validate_plan(contract, state, qualification_raw, qualification_plan)
        elif isinstance(selected_plan, dict) and selected_plan.get('operation') == 'bounded_q4_initial_data_capture':
            import q4_initial_data_capture as q4
            q4_plan = q4.validate_plan(contract, state, qualification_raw, qualification_plan)
        elif isinstance(selected_plan, dict) and selected_plan.get('operation') == 'bounded_q4_primary_qualification':
            import q4_primary_qualification as q4
            q4_plan = q4.validate_plan(contract, state, qualification_raw, qualification_plan)
        elif isinstance(selected_plan, dict) and selected_plan.get('operation') == 'bounded_cyera_primary_capture':
            import cyera_primary_capture as q4
            q4_plan = q4.validate_plan(contract, state, qualification_raw, qualification_plan)
        elif isinstance(selected_plan, dict) and selected_plan.get('operation') == 'bounded_prnewswire_primary_capture':
            import prnewswire_primary_capture as q4
            q4_plan = q4.validate_plan(contract, state, qualification_raw, qualification_plan)
        else:
            validate_qualification_probe_plan(contract, state, qualification_plan)
        # This exact day is escrowed. A midnight crossing during the remote
        # acknowledgement is denied by the same bound context before transport.
        budget = PersistentProbeBudget(state, contract, clock=utcnow, monotonic=time.monotonic,
                                       maximum_seconds=maximum_seconds)
        def stop(*_args):
            nonlocal cancelled
            cancelled = True
            budget.deadline = 0
        previous_signals = {s: signal.getsignal(s) for s in (signal.SIGINT, signal.SIGTERM)}
        for signum in previous_signals:
            signal.signal(signum, stop)
        escrow_budgets(root, state, session, contract, budget.started_at)
        if q4 is not None:
            report = q4.execute(contract, state, Fetcher(state, timeout=12, max_bytes=q4.MAX_BODY_BYTES,
                redirect_diagnostics=True, unexpected_status_diagnostics=True), budget, q4_plan)
            report = q4.finalize_report(contract, state, qualification_raw, report, budget)
        elif orca is not None:
            report = orca.execute(contract, state, Fetcher(state, timeout=12, redirect_diagnostics=True), budget, orca_plan)
            # Reconstruct readiness and retain repeated module/caller denials.
            report = orca.finalize_report(contract, state, qualification_raw, report, budget)
        else:
            diagnostic_options = {'unexpected_status_diagnostics': True} if selected_plan.get('schemaVersion') == 1 else {}
            report = probe_sources(contract, state, Fetcher(state, timeout=12, **diagnostic_options), reservation_context=budget,
                                   qualification_plan_path=qualification_plan)
            # The final in-flight request can finish after its deadline/day even
            # when there is no next request to trigger the ordinary guard.
            try:
                budget.before_fetch()
            except ProbeReservationDenied as error:
                report.update(executionCompleted=False, budgetDenied=True, completionDenial=error.reason)
            report['reservationContext'] = budget.summary()
        completed = report['executionCompleted'] and not cancelled
        result = {'schemaVersion': 1, 'checkpointProfile': 'source_probe',
                  'githubRunId': os.environ['GITHUB_RUN_ID'],
                  'githubRunAttempt': int(os.environ['GITHUB_RUN_ATTEMPT']),
                  'githubEventName': os.environ['GITHUB_EVENT_NAME'], 'githubRef': os.environ['GITHUB_REF'],
                  'appRevision': session['appRevision'], 'contractSha256': digest(contract),
                  'diagnostic': report, 'executionCompleted': completed,
                  'outcome': 'cancelled' if cancelled else 'completed_diagnostic' if completed else 'budget_denied',
                  'modelCalls': 0, 'apiFallback': False, 'semanticAdmission': False,
                  'coverageCredit': False, 'sourceChecksCredited': 0, 'qualifiedSources': 0,
                  'publication': {'published': False, 'reason': 'SOURCE_PROBE_DIAGNOSTIC_ONLY'}}
        if selected_q4:
            result['facts'] = []
        state.write_once(f"ci/source-probe-runs/{result['githubRunId']}-{result['githubRunAttempt']}.json", result)
        result['archive'] = session_runtime.checkpoint(root, state, session, 'finish', result, finish=True)['archive']
        return result
    except Exception as error:
        failed = {'checkpointProfile': 'source_probe', 'errorType': type(error).__name__,
                  'executionCompleted': False, 'outcome': 'failed', 'modelCalls': 0,
                  'semanticAdmission': False, 'coverageCredit': False,
                  'publication': {'published': False, 'reason': 'SOURCE_PROBE_DIAGNOSTIC_ONLY'}}
        if selected_q4:
            failed.update(qualifiedSources=0, sourceChecksCredited=0, facts=[])
        state.write_once(f"ci/source-probe-failures/{digest(session['sessionId'])}/{digest(failed)}.json", failed)
        lease = state.read('heads/cloud-lease.json')
        if lease and not lease.get('releasedAt'):
            session_runtime.checkpoint(root, state, session, 'failed', failed, finish=True)
        raise
    finally:
        for signum, handler in previous_signals.items():
            signal.signal(signum, handler)


def execute(root, maximum_seconds=1200, publisher_config=None, *, source_probe=False):
    require(os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_REPOSITORY") == PROJECT, "PRIVATE_GITHUB_RUNNER_REQUIRED")
    require(60 <= maximum_seconds <= 1200, "CI collection budget may not exceed twenty minutes")
    require(type(source_probe) is bool, 'SOURCE_PROBE_MODE_MUST_BE_BOOLEAN')
    started = time.monotonic()
    identifier = "github-" + os.environ["GITHUB_RUN_ID"] + "-" + os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    if source_probe:
        session_runtime.require_source_probe_context(identifier)
    auth = os.environ.pop("SMP_CODEX_AUTH_JSON", "")
    writer = os.environ.pop("SMP_AUTH_STORE_TOKEN", "")
    root = Path(root).resolve()
    revision = session_runtime.git("rev-parse", "HEAD")
    recover(root / 'abandoned-lease-recovery')
    profile = {'checkpoint_profile': 'source_probe'} if source_probe else {}
    session_runtime.bootstrap(root, "collector", identifier, revision, execution_mode="github_subscription", **profile)
    state = LocalStore(root / "state")
    session = LocalStore(root).read("session.json")
    if source_probe:
        try:
            import roster_transition
            # Dormant qualification probes are pinned to J; under J's roster successor they judge J (D-138).
            contract = roster_transition.authority_contract(
                validate_contract(json.loads((REPO / 'contracts/market.json').read_text())))
        except Exception as error:
            session_runtime.checkpoint(root, state, session, 'failed',
                {'errorType': type(error).__name__, 'executionCompleted': False, 'published': False}, finish=True)
            raise
        return execute_source_probe(root, state, session, contract, maximum_seconds)
    keeper = AuthStore(root / "auth", writer)
    try:
        contract = validate_contract(json.loads((REPO / "contracts/market.json").read_text()))
        import q4_qualification_origin as q4_origin
        import roster_transition
        # Seeding authorities judge J; a reviewed additive roster successor collects as itself (D-138).
        authority = roster_transition.authority_contract(contract)
        if q4_origin.is_successor(authority):
            from q4_qualification_seed import seed_before_collection
        else:
            from html_qualification_seed import seed_before_collection
        seed_before_collection(REPO, root, state, session, authority, session_runtime)
        corrections_enabled = (REPO / 'contracts/factual-corrections.json').exists()
        reused=reuse_scheduled_collection(state,contract,utcnow(),corrections_enabled=corrections_enabled)
        if reused:
            archive_collection_result(state,reused,contract,os.environ.get('GITHUB_RUN_ATTEMPT','1'))
            reused['archive']=session_runtime.checkpoint(root,state,session,'finish',reused,finish=True)['archive']
            return reused
        require(auth and writer, "DEDICATED_ACCOUNT_AND_SECRET_WRITER_REQUIRED")
        keeper.restore(auth)
        os.environ["CODEX_HOME"] = str(keeper.home)
        guarded = GuardedRunner(keeper)
        agent = SubscriptionAgent(contract["model"], runner=guarded)
        work = correction_work(REPO, state, contract, agent)
        budget = collection_seconds(maximum_seconds, started, time.monotonic())
        print(json.dumps({"collectionSeconds": budget, "restoreSeconds": round(time.monotonic() - started)}), flush=True)
        collector = BoundedPipeline(contract, state, Fetcher(state), agent, maximum_seconds=budget,
                                    correction_work=work,
                                    history=load_history_policy(REPO / 'contracts/history-window.json'))
        previous_signals = {s: signal.getsignal(s) for s in (signal.SIGINT, signal.SIGTERM)}
        for signum in previous_signals:
            signal.signal(signum, collector.stop)
        # All restored checkpoints and daily budgets exist before model work.
        scheduled_at = utcnow()
        escrow_budgets(root, state, session, contract, scheduled_at)
        collected = collector.run(scheduled_at, replay=work is not None, force_refresh=scheduled_source_refresh())
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
        snapshot = build_snapshot(contract, plan, checked, state, utcnow(), previous=previous, reconciled_here=True)
        state.compare_and_swap("dailySnapshot", state.read("heads/dailySnapshot.json"), snapshot)
        state.compare_and_swap("cloud-snapshot", state.read("heads/cloud-snapshot.json"), snapshot)
        rows = inventory(contract, utcnow(), checked)
        state.put(csv_matrix(rows).encode())
        state.put(markdown_matrix(contract, rows).encode())
        keeper.checkpoint()
        result = {"githubRunId": os.environ["GITHUB_RUN_ID"],
                  "githubEventName": os.environ.get("GITHUB_EVENT_NAME"),
                  "githubRef": os.environ.get("GITHUB_REF"), "appRevision": revision,
                  **({"githubTimer": True} if timer.timer_dispatch() else {}),
                  "runId": checked["runId"],
                  "successfulTasks": checked["successfulTasks"], "requiredTasks": checked["requiredTasks"],
                  "complete": checked["complete"], "modelCalls": agent.calls, "apiFallback": False,
                  "snapshotSha256": snapshot["snapshotSha256"], "reviewQueue": len(snapshot["reviewQueue"]),
                  "executionMode": "github_subscription", "publication": {"published": False, "reason": "INITIAL_CUTOVER_NOT_ENABLED"},
                  # Read by the workflow so the outside watchdog can flag an expired login.
                  "modelUnavailable": getattr(collector, "model_unavailable", None)}
        result.update(execution_outcome(checked['complete'], collector.cancelled, checked))
        if 'corrections' in collected:
            result['corrections'] = collected['corrections']
        if contract["publication"]["enabled"]:
            # Publication has a separate runner/time budget and never receives
            # subscription auth. Its independent gate may take 35 minutes.
            result["publication"] = {"published": False, "reason": "SEPARATE_PUBLISHER_REQUIRED"}
        archive_collection_result(state, result, contract, os.environ.get('GITHUB_RUN_ATTEMPT', '1'))
        finished = session_runtime.checkpoint(root, state, session, "finish", result, finish=True)
        result["archive"] = finished["archive"]
        # A cancellation arriving during the final remote write still fails
        # execution, even if the durable evidence checkpoint succeeded.
        result.update(execution_outcome(checked['complete'], collector.cancelled, checked))
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
    parser.add_argument('--source-probe', action='store_true', help='Private manual main diagnostics with the shared lease and budget')
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        result = execute(args.root, args.maximum_seconds, args.publisher_config, source_probe=args.source_probe)
    except Exception as error:
        result = {"complete": False, "executionCompleted": False, "outcome": "failed",
                  "reason": str(error)[:120] if type(error) is RuntimeError else type(error).__name__, "apiFallback": False}
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(exit_code(result))
