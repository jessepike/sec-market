#!/usr/bin/env python3
"""Exercise retained production rollback and restore the accepted exact artifact."""
import argparse
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import timer
from collect import REPO, session_runtime, recover
from bootstrap import PROJECT
from artifacts import stage_files
from contracts import digest, require, utcnow, validate_contract
from publication import verify_acknowledgement
from provenance import GitHubAuthority
from publisher_probe import PublisherAuth, PROJECT_ID, TEAM_ID, SCOPE
from storage import LocalStore
from vercel import VercelAdapter


def failure_category(error):
    # Never expose remote response text, URLs, headers or CLI stderr.
    reason = str(error)
    if reason == 'Application and detached deployment receipts differ':
        return 'RECEIPT_PAIR_DIFFERS'
    if reason in ('DEPLOYED_STATIC_FILE_BYTES_DIFFER', 'DEPLOYED_STATIC_FILE_REDIRECT_OR_HTTP_FAILURE'):
        return 'STATIC_BYTES_OR_RESPONSE_DIFFERS'
    if reason in ('Deployment not ready', 'Deployed code differs', 'Deployed data release differs',
                  'Deployed snapshot differs', 'Deployed artifact differs', 'Deployed coverage contract differs',
                  'Deployed correction projection differs', 'DRILL_BASELINE_LIVE_RECEIPT_DIFFERS'):
        return 'EXPECTED_ACKNOWLEDGEMENT_DIFFERS'
    if isinstance(error, OSError):
        return 'NETWORK_OR_IO'
    return 'UNCLASSIFIED'


class DrillVerificationError(ValueError):
    def __init__(self, phase, category):
        self.failure_phase, self.failure_category = phase, category
        super().__init__('DRILL_VERIFICATION_FAILED_' + phase.upper() + '_' + category)


def require_payload(files):
    require(isinstance(files, dict) and any(name.startswith('static/')
            and name != 'static/deployment-receipt.json' for name in files),
            'DRILL_NONEMPTY_STATIC_PAYLOAD_REQUIRED')


def verify_release_pair(adapter, deployment, manifest, acknowledgement, files, phase):
    """Retry one complete exact pair/acknowledgement/static check, never its criteria."""
    require_payload(files)
    verify_acknowledgement(manifest, acknowledgement)
    adapter.pending, adapter.pending_files = acknowledgement, files
    for attempt in range(6):
        try:
            verify_acknowledgement(manifest, adapter.probe(deployment))
            adapter.verify_static_files(deployment)
            return
        except (ValueError, OSError) as error:
            if attempt == 5:
                raise DrillVerificationError(phase, failure_category(error)) from None
        time.sleep(5)


def verify_legacy_live(adapter, baseline):
    for attempt in range(6):
        try:
            require(adapter._get(adapter.site, '/app-release.json') == baseline['legacyAppReceipt'],
                    'DRILL_BASELINE_LIVE_RECEIPT_DIFFERS')
            return
        except (ValueError, OSError) as error:
            if attempt == 5:
                raise DrillVerificationError('baseline_verification', failure_category(error)) from None
        time.sleep(5)


def verify_ready(adapter, deployment):
    require(re.fullmatch(r'https://[a-z0-9-]+\.vercel\.app', deployment), 'DRILL_IMMUTABLE_DEPLOYMENT_REQUIRED')
    meta = json.loads(adapter._cli(['api', '/v13/deployments/' + deployment.removeprefix('https://'), '--raw']))
    require(meta.get('projectId') == PROJECT_ID and meta.get('readyState') == 'READY'
            and 'https://' + meta.get('url', '') == deployment and meta.get('target') == 'production',
            'DRILL_READY_PRODUCTION_TARGET_REQUIRED')


def drill(store, adapter, expected_release, checkpoint, authority=None):
    current = store.read('heads/production.json')
    require(current and current.get('releaseId') == expected_release and not current.get('legacyBaseline'),
            'DRILL_ACCEPTED_CURRENT_RELEASE_REQUIRED')
    saved = store.read(f'releases/{expected_release}.json')
    require(saved and saved['manifest']['releaseId'] == expected_release, 'DRILL_CURRENT_MANIFEST_REQUIRED')
    manifest = saved['manifest']
    require(digest({k: v for k, v in manifest.items() if k != 'releaseId'}) == expected_release,
            'DRILL_CURRENT_MANIFEST_HASH_DIFFERS')
    baseline = store.read(f"production-baselines/{manifest['parentReleaseId']}.json")
    require(baseline and baseline['releaseId'] == manifest['parentReleaseId'], 'DRILL_RETAINED_PARENT_REQUIRED')
    test = store.read(f"gate-receipts/{manifest['testProvenance']['githubRunId']}.json")
    require(test and digest(test) == manifest['testReceiptSha256'], 'DRILL_MAIN_GATE_RECEIPT_REQUIRED')
    require((authority or GitHubAuthority()).verify_test_receipt(test, manifest['artifact']),
            'DRILL_MAIN_GATE_PROVENANCE_REJECTED')
    require(adapter.production_paths_controlled(), 'DRILL_COMPETING_PATHS_MUST_BE_CLOSED')
    verify_ready(adapter, current['deploymentId'])
    verify_ready(adapter, baseline['deploymentId'])
    files = stage_files(store, manifest['artifact'], saved['acknowledgement'])
    verify_release_pair(adapter, current['deploymentId'], manifest, saved['acknowledgement'], files, 'preflight_current')
    verify_release_pair(adapter, adapter.site, manifest, saved['acknowledgement'], files, 'preflight_current')
    if baseline.get('legacyBaseline'):
        require(digest({k: v for k, v in baseline.items() if k != 'releaseId'}) == baseline['releaseId'],
                'DRILL_LEGACY_BASELINE_HASH_DIFFERS')
        require(adapter._get(baseline['deploymentId'], '/app-release.json') == baseline['legacyAppReceipt'],
                'DRILL_LEGACY_BASELINE_RECEIPT_DIFFERS')
    else:
        prior = store.read(f"releases/{baseline['releaseId']}.json")
        require(prior is not None, 'DRILL_PARENT_MANIFEST_REQUIRED')
        require(prior['manifest'].get('releaseId') == baseline['releaseId'] and
                digest({k:v for k,v in prior['manifest'].items() if k != 'releaseId'}) == baseline['releaseId'],
                'DRILL_PARENT_MANIFEST_HASH_DIFFERS')
        baseline_files = stage_files(store, prior['manifest']['artifact'], prior['acknowledgement'])
        verify_release_pair(adapter, baseline['deploymentId'], prior['manifest'], prior['acknowledgement'],
                            baseline_files, 'preflight_parent')
    identifier = digest({'run': os.environ.get('GITHUB_RUN_ID'), 'attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
                         'current': current, 'baseline': baseline})
    journal = {'drillId': identifier, 'startedAt': utcnow(), 'current': current, 'baseline': baseline,
               'phase': 'intent_archived', 'productionHeadRemains': expected_release}
    def record(phase, **extra):
        nonlocal journal
        journal = {**journal, 'phase': phase, 'checkedAt': utcnow(), **extra}
        store.write_once(f'rollback-drills/{identifier}/{phase}.json', journal)
        store.compare_and_swap('rollback-drill', store.read('heads/rollback-drill.json'), journal)
        checkpoint()
    record('intent_archived')
    attempted = False
    phase = 'baseline_alias_change'
    try:
        attempted = True
        adapter.rollback(baseline['deploymentId'])
        phase = 'baseline_verification'
        if baseline.get('legacyBaseline'):
            verify_legacy_live(adapter, baseline)
        else:
            verify_release_pair(adapter, adapter.site, prior['manifest'], prior['acknowledgement'],
                                baseline_files, 'baseline_verification')
        record('baseline_acknowledged', baselineByteInventoryAvailable=not baseline.get('legacyBaseline', False),
               baselineBytesVerified=not baseline.get('legacyBaseline', False))
    except Exception as error:
        record('baseline_failed', failurePhase=phase,
               failureCategory=getattr(error, 'failure_category', failure_category(error)))
        raise
    finally:
        if attempted:
            # Always restore the already accepted immutable deployment, even
            # when the baseline probe or its remote journal fails.
            adapter.rollback(current['deploymentId'])
            verify_release_pair(adapter, adapter.site, manifest, saved['acknowledgement'], files,
                                'current_restoration_verification')
            record('current_restored', currentBytesVerified=True)
    require(store.read('heads/production.json') == current, 'DRILL_PRODUCTION_HEAD_CHANGED')
    record('passed', completedAt=utcnow())
    return journal


def scheduled_upstream(run_id, runner=subprocess.run):
    require(str(run_id).isdigit(), 'DRILL_UPSTREAM_RUN_ID_REQUIRED')
    response=runner(['gh','api','repos/' + PROJECT + '/actions/runs/' + str(run_id)],
                    capture_output=True,text=True,timeout=60)
    require(response.returncode == 0, 'DRILL_UPSTREAM_STATUS_UNAVAILABLE')
    run=json.loads(response.stdout)
    require(run.get('id') == int(run_id) and run.get('repository',{}).get('full_name') == PROJECT
            and run.get('repository',{}).get('private') is True
            and run.get('path') == '.github/workflows/subscription-publisher.yml'
            and run.get('head_branch') == 'main' and re.fullmatch(r'[a-f0-9]{40}',run.get('head_sha',''))
            and run.get('status') == 'completed' and run.get('conclusion') == 'success'
            and run.get('event') in ('schedule','workflow_run'), 'DRILL_UPSTREAM_NOT_TRUSTED_SCHEDULED_PUBLISHER')
    return {'githubRunId':run['id'],'appRevision':run['head_sha'],
            'event':run['event'],'createdAt':run.get('created_at'),'finishedAt':run.get('updated_at')}


def automatic_target(store, upstream):
    if store.read('heads/rollback-drill.json'):
        return None, 'DRILL_ALREADY_RECORDED'
    current=store.read('heads/production.json')
    if not current or current.get('legacyBaseline'):
        return None, 'DRILL_NO_ACCEPTED_DAILY_RELEASE'
    saved=store.read(f"releases/{current['releaseId']}.json")
    require(saved and saved['manifest']['appRevision'] == upstream['appRevision'],
            'DRILL_UPSTREAM_DOES_NOT_MATCH_CURRENT_RELEASE')
    return current['releaseId'], None


def scheduled_source_clocks(store, manifest):
    clocks=[]
    for path in sorted((store.root/'ci/collection-runs').glob('*.json')):
        clock=json.loads(path.read_text())
        if clock.get('runId') == manifest['runId'] and clock.get('contractSha256') == manifest['contractSha256'] \
                and clock.get('executionCompleted') is True and timer.trusted_clock(clock) \
                and clock.get('githubRef') == 'refs/heads/main':
            clocks.append(clock)
    return clocks


def preflight_api(path, optional=False):
    response=subprocess.run(['gh','api','repos/' + PROJECT + '/' + path,
                             '--header','Accept: application/vnd.github.raw+json'],
                            capture_output=True,text=True,timeout=60)
    if optional and response.returncode and '(HTTP 404)' in response.stderr:
        return None
    require(response.returncode == 0, 'DRILL_AUTOMATIC_PREFLIGHT_API_FAILED')
    return json.loads(response.stdout)


def automatic_preflight(upstream_id, api=preflight_api, lookup=scheduled_upstream, today=None):
    today=today or datetime.now(timezone.utc).date().isoformat()
    if today != '2026-10-23':
        return {'allowed':False,'reason':'DRILL_AUTOMATIC_ACCEPTANCE_DATE_EXPIRED'}
    upstream=lookup(upstream_id)
    policy=digest(json.loads((REPO/'contracts/market.json').read_text()))
    runs=api('actions/workflows/subscription-collector.yml/runs?per_page=40')['workflow_runs']
    if any(r.get('status') != 'completed' for r in runs):
        return {'allowed':False,'reason':'DRILL_COLLECTOR_IS_QUEUED_OR_RUNNING'}
    scheduled=[r for r in runs if r.get('event') == 'schedule' and r.get('status') == 'completed'
               and r.get('conclusion') == 'success' and r.get('head_branch') == 'main'
               and r.get('created_at','')[:10] == today]
    if not scheduled:
        return {'allowed':False,'reason':'DRILL_NO_COMPLETED_SCHEDULED_COLLECTOR'}
    commit=api('git/ref/archive/market-evidence')['object']['sha']
    require(re.fullmatch(r'[a-f0-9]{40}',commit),'DRILL_PREFLIGHT_ARCHIVE_PIN_INVALID')
    recorded=api('contents/state/heads/rollback-drill.json?ref=' + commit,optional=True)
    if recorded:
        return {'allowed':False,'reason':'DRILL_ALREADY_RECORDED'}
    production=api('contents/state/heads/production.json?ref=' + commit)
    if production.get('legacyBaseline'):
        return {'allowed':False,'reason':'DRILL_NO_ACCEPTED_DAILY_RELEASE'}
    for run in scheduled:
        receipt=api('contents/state/ci/collection-runs/' + str(run['id']) + '-'
                    + str(run.get('run_attempt',1)) + '.json?ref=' + commit,optional=True)
        if receipt and receipt.get('executionCompleted') is True and receipt.get('githubEventName') == 'schedule' \
                and receipt.get('githubRef') == 'refs/heads/main' and str(receipt.get('githubRunId')) == str(run['id']) \
                and receipt.get('appRevision') == run.get('head_sha') and receipt.get('contractSha256') == policy:
            return {'allowed':True,'upstreamPublisher':upstream,'scheduledCollectorReceipt':receipt}
    return {'allowed':False,'reason':'DRILL_SCHEDULED_COLLECTOR_ARCHIVE_BINDING_MISSING'}


def execute(root, expected_release=None, upstream_run=None):
    require(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_REPOSITORY') == PROJECT
            and os.environ.get('GITHUB_REF') == 'refs/heads/main', 'DRILL_PRIVATE_REVIEWED_MAIN_REQUIRED')
    upstream=None
    if upstream_run:
        if datetime.now(timezone.utc).date().isoformat() != '2026-10-23':
            return {'passed':False,'skipped':True,'reason':'DRILL_AUTOMATIC_ACCEPTANCE_DATE_EXPIRED'}
        upstream=scheduled_upstream(upstream_run)
    else:
        require(isinstance(expected_release,str) and re.fullmatch(r'[a-f0-9]{64}', expected_release),
                'DRILL_EXPECTED_RELEASE_HASH_REQUIRED')
    contract = validate_contract(json.loads((REPO / 'contracts/market.json').read_text()))
    require(contract['publication']['enabled'], 'DRILL_PUBLICATION_CUTOVER_REQUIRED')
    root = Path(root).resolve()
    recover(root / 'abandoned-lease-recovery')
    revision = session_runtime.git('rev-parse', 'HEAD')
    session_runtime.bootstrap(root, 'governance', 'github-publisher-' + os.environ['GITHUB_RUN_ID'] + '-'
                              + os.environ.get('GITHUB_RUN_ATTEMPT', '1'), revision, execution_mode='github_subscription')
    state, session = LocalStore(root/'state'), LocalStore(root).read('session.json')
    try:
        if upstream:
            expected_release,skip=automatic_target(state,upstream)
            if skip:
                result={'passed':False,'skipped':True,'reason':skip,'upstreamPublisher':upstream}
                session_runtime.checkpoint(root,state,session,'finish',result,finish=True)
                return result
            accepted=state.read(f'releases/{expected_release}.json')['manifest']
            clocks=scheduled_source_clocks(state,accepted)
            require(bool(clocks),'DRILL_ACCEPTED_RELEASE_SCHEDULED_SOURCE_CLOCK_REQUIRED')
        with PublisherAuth(root/'auth', os.environ.pop('VERCEL_TOKEN', '')) as auth:
            project = json.loads(auth.cli(['api', '/v9/projects/' + PROJECT_ID + '?teamId=' + TEAM_ID, '--raw']))
            require(project.get('id') == PROJECT_ID and project.get('accountId') == TEAM_ID, 'DRILL_PROJECT_DIFFERS')
            auth.pin_verified_team()
            adapter = VercelAdapter(state, PROJECT_ID, TEAM_ID, SCOPE, global_config=str(auth.root), runner=auth.isolated_runner)
            result = drill(state, adapter, expected_release,
                           lambda: session_runtime.checkpoint(root,state,session,'rollback_drill_journal',{}))
        output={'passed': True, 'drill': result}
        if upstream:
            output['upstreamPublisher']=upstream
            output['sourceCollectionReceipts']=clocks
        state.write_once('ci/rollback-acceptance-runs/' + os.environ['GITHUB_RUN_ID'] + '-'
                         + os.environ.get('GITHUB_RUN_ATTEMPT','1') + '.json',output)
        final = session_runtime.checkpoint(root,state,session,'finish',output,finish=True)
        output['archive']=final['archive']
        return output
    except Exception as error:
        diagnostic={'errorType':type(error).__name__, 'failureCategory':getattr(error,'failure_category',failure_category(error))}
        if isinstance(error, DrillVerificationError):
            diagnostic['failurePhase']=error.failure_phase
        session_runtime.checkpoint(root,state,session,'failed',diagnostic,finish=True)
        raise


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True)
    parser.add_argument('--expected-release')
    parser.add_argument('--upstream-run')
    parser.add_argument('--preflight-upstream')
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    try:
        if args.preflight_upstream:
            result=automatic_preflight(args.preflight_upstream)
            with open(os.environ['GITHUB_OUTPUT'],'a') as output:
                output.write('allowed=' + str(result['allowed']).lower() + '\n')
            result['skipped']=not result['allowed']
            result['passed']=result['allowed']
        else:
            result=execute(args.root,args.expected_release,args.upstream_run)
    except Exception as error:
        result={'passed':False,'errorType':type(error).__name__,
                'failureCategory':getattr(error,'failure_category',failure_category(error))}
        if isinstance(error, DrillVerificationError):
            result['failurePhase']=error.failure_phase
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result.get('passed') or result.get('skipped') else 2)
