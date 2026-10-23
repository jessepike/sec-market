#!/usr/bin/env python3
"""Exercise retained production rollback and restore the accepted exact artifact."""
import argparse
import json
import os
import re
from pathlib import Path

from collect import REPO, session_runtime, recover
from bootstrap import PROJECT
from artifacts import stage_files
from contracts import digest, require, utcnow, validate_contract
from publication import verify_acknowledgement
from provenance import GitHubAuthority
from publisher_probe import PublisherAuth, PROJECT_ID, TEAM_ID, SCOPE
from storage import LocalStore
from vercel import VercelAdapter


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
    verify_acknowledgement(manifest, adapter.probe(current['deploymentId']))
    files = stage_files(store, manifest['artifact'], saved['acknowledgement'])
    adapter.pending_files = files
    adapter.verify_static_files(current['deploymentId'])
    adapter.verify_static_files(adapter.site)
    verify_acknowledgement(manifest, adapter.probe(adapter.site))
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
        adapter.pending_files = stage_files(store, prior['manifest']['artifact'], prior['acknowledgement'])
        verify_acknowledgement(prior['manifest'], adapter.probe(baseline['deploymentId']))
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
    try:
        attempted = True
        adapter.rollback(baseline['deploymentId'])
        if baseline.get('legacyBaseline'):
            require(adapter._get(adapter.site, '/app-release.json') == baseline['legacyAppReceipt'],
                    'DRILL_BASELINE_LIVE_RECEIPT_DIFFERS')
        else:
            adapter.pending_files = stage_files(store, prior['manifest']['artifact'], prior['acknowledgement'])
            verify_acknowledgement(prior['manifest'], adapter.probe(adapter.site))
        record('baseline_acknowledged', baselineByteInventoryAvailable=not baseline.get('legacyBaseline', False))
    finally:
        if attempted:
            # Always restore the already accepted immutable deployment, even
            # when the baseline probe or its remote journal fails.
            adapter.rollback(current['deploymentId'])
            adapter.pending = saved['acknowledgement']
            adapter.pending_files = files
            verify_acknowledgement(manifest, adapter.probe_production())
            adapter.verify_static_files(adapter.site)
            record('current_restored', currentBytesVerified=True)
    require(store.read('heads/production.json') == current, 'DRILL_PRODUCTION_HEAD_CHANGED')
    record('passed', completedAt=utcnow())
    return journal


def execute(root, expected_release):
    require(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_REPOSITORY') == PROJECT
            and os.environ.get('GITHUB_REF') == 'refs/heads/main', 'DRILL_PRIVATE_REVIEWED_MAIN_REQUIRED')
    require(re.fullmatch(r'[a-f0-9]{64}', expected_release), 'DRILL_EXPECTED_RELEASE_HASH_REQUIRED')
    contract = validate_contract(json.loads((REPO / 'contracts/market.json').read_text()))
    require(contract['publication']['enabled'], 'DRILL_PUBLICATION_CUTOVER_REQUIRED')
    root = Path(root).resolve()
    recover(root / 'abandoned-lease-recovery')
    revision = session_runtime.git('rev-parse', 'HEAD')
    session_runtime.bootstrap(root, 'governance', 'github-publisher-' + os.environ['GITHUB_RUN_ID'] + '-'
                              + os.environ.get('GITHUB_RUN_ATTEMPT', '1'), revision, execution_mode='github_subscription')
    state, session = LocalStore(root/'state'), LocalStore(root).read('session.json')
    try:
        with PublisherAuth(root/'auth', os.environ.pop('VERCEL_TOKEN', '')) as auth:
            project = json.loads(auth.cli(['api', '/v9/projects/' + PROJECT_ID + '?teamId=' + TEAM_ID, '--raw']))
            require(project.get('id') == PROJECT_ID and project.get('accountId') == TEAM_ID, 'DRILL_PROJECT_DIFFERS')
            auth.pin_verified_team()
            adapter = VercelAdapter(state, PROJECT_ID, TEAM_ID, SCOPE, global_config=str(auth.root), runner=auth.isolated_runner)
            result = drill(state, adapter, expected_release,
                           lambda: session_runtime.checkpoint(root,state,session,'rollback_drill_journal',{}))
        final = session_runtime.checkpoint(root,state,session,'finish',{'rollbackDrill': result},finish=True)
        return {'passed': True, 'drill': result, 'archive': final['archive']}
    except Exception as error:
        session_runtime.checkpoint(root,state,session,'failed',{'errorType':type(error).__name__},finish=True)
        raise


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True)
    parser.add_argument('--expected-release',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    try:
        result=execute(args.root,args.expected_release)
    except Exception as error:
        result={'passed':False,'errorType':type(error).__name__}
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['passed'] else 2)
