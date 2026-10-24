#!/usr/bin/env python3
"""Stage the exact independent preview gate payload without production writes."""
import argparse
import json
import os
import re
from pathlib import Path

from bootstrap import PROJECT, REPO
from publisher_probe import PublisherAuth, PROJECT_ID, TEAM_ID, SCOPE
from publisher_stage import verify_files
from artifacts import stage_files
from contracts import digest, require, utcnow
from provenance import GitHubAuthority
from release import import_gate
from storage import LocalStore
from vercel import VercelAdapter
from coverage_summary import coverage_details


def validate_request(request):
    require(request.get('operation') == 'stage_verified_preview_gate', 'PREVIEW_GATE_OPERATION_REQUIRED')
    for key in ('gateRunId', 'artifactId'):
        require(type(request.get(key)) is int and request[key] > 0, 'PREVIEW_GATE_PROVENANCE_IDS_REQUIRED')
    for key, length in (('archiveCommit', 40), ('manifestSha256', 64)):
        require(isinstance(request.get(key), str) and re.fullmatch('[a-f0-9]{' + str(length) + '}', request[key]),
                'PREVIEW_GATE_ARCHIVE_PIN_REQUIRED')
    return {'commit': request['archiveCommit'], 'manifestSha256': request['manifestSha256']}


def execute(root, request):
    require(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_REPOSITORY') == PROJECT,
            'PRIVATE_GITHUB_RUNNER_REQUIRED')
    require(os.environ.get('GITHUB_REF') == 'refs/heads/preview', 'PREVIEW_BRANCH_REQUIRED')
    archived = validate_request(request)
    root = Path(root).absolute()
    require(not root.resolve().is_relative_to(REPO) and not root.exists() and not root.is_symlink(),
            'FRESH_OUTSIDE_CHECKOUT_STAGE_REQUIRED')
    root.mkdir(mode=0o700, parents=True)
    state = LocalStore(root / 'state')
    # Fixed preview authority deliberately cannot satisfy production provenance.
    authority = GitHubAuthority(branch='preview')
    inputs, receipt = import_gate(state, authority, request['gateRunId'], request['artifactId'], archived)
    details = coverage_details(inputs['coverage'])
    manifest = {'mode': 'stage_only_smoke_test', 'appRevision': receipt['appRevision'],
                'snapshot': inputs['snapshot'], 'artifact': inputs['artifact'],
                'contractSha256': receipt['contractSha256']}
    if inputs['snapshot'].get('factualCorrections'):
        manifest['factualCorrections'] = inputs['snapshot']['factualCorrections']
    manifest['releaseId'] = digest({'previewOnly': manifest, 'gateReceipt': receipt})
    token = os.environ.pop('VERCEL_TOKEN', '')
    with PublisherAuth(root / 'auth', token) as auth:
        project = json.loads(auth.cli(['api', '/v9/projects/' + PROJECT_ID + '?teamId=' + TEAM_ID, '--raw']))
        require(project.get('id') == PROJECT_ID and project.get('accountId') == TEAM_ID,
                'EXISTING_VERCEL_PROJECT_AND_TEAM_DIFFER')
        auth.pin_verified_team()
        adapter = VercelAdapter(state, PROJECT_ID, TEAM_ID, SCOPE,
                                global_config=str(auth.root), runner=auth.isolated_runner)
        before = adapter._get(adapter.site, '/app-release.json')
        deployment = adapter.stage(manifest)
        (root / 'progress.json').write_text(json.dumps({'deployment': deployment, 'productionPromoted': False}))
        acknowledgement = adapter.probe(deployment)
        require(acknowledgement == adapter.pending, 'STAGED_RECEIPT_DIFFERS')
        verified = verify_files(deployment, stage_files(state, manifest['artifact'], adapter.pending))
        after = adapter._get(adapter.site, '/app-release.json')
        require(before == after, 'PRODUCTION_CHANGED_DURING_STAGING')
    return {'publisherStagePassed': True, 'checkedAt': utcnow(), 'deployment': deployment,
            'appRevision': receipt['appRevision'], 'gateRunId': request['gateRunId'], 'artifactId': request['artifactId'],
            'archive': archived, 'artifactSha256': manifest['artifact']['sha256'],
            'snapshotSha256': manifest['snapshot']['sha256'], 'coverage': {
                **{key: inputs['coverage'][key] for key in ('complete', 'successfulTasks', 'requiredTasks', 'runId')}, **details},
            'acknowledgement': acknowledgement, 'verifiedStaticFiles': verified,
            'productionAppRevision': before.get('appRevision'), 'productionUnchanged': True,
            'productionPromoted': False, 'projectSettingsChanged': False, 'archiveChanged': False,
            'modelCalls': 0, 'productionGateAuthority': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--request', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        result = execute(args.root, json.loads(Path(args.request).read_text()))
    except Exception as error:
        result = {'publisherStagePassed': False, 'errorType': type(error).__name__, 'productionPromoted': False}
        progress = Path(args.root) / 'progress.json'
        if progress.exists():
            result.update(json.loads(progress.read_text()))
    Path(args.output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['publisherStagePassed'] else 2)
