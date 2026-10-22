#!/usr/bin/env python3
"""Stage an archived prebuilt smoke payload with the dedicated CI credential.

No model work, archive writes, project settings, promotion or alias changes.
This does not confer independent-release-gate authority on the smoke payload.
"""
import argparse
import json
import os
import urllib.request
from pathlib import Path
from urllib.parse import quote

from publisher_probe import PublisherAuth, PROJECT_ID, TEAM_ID, SCOPE, execute
from bootstrap import PROJECT, REPO
from archive import GitArchive
from artifacts import stage_files
from contracts import digest, require, utcnow
from storage import LocalStore
from vercel import VercelAdapter

SMOKE_ID = '76cb8908434843983d658df19a3e5c011713da973ffd708ef94c039eaec19c84'


def verify_files(base, files, opener=urllib.request.urlopen):
    verified = []
    for name, body in sorted(files.items()):
        if not name.startswith('static/'):
            continue
        path = '/' + quote(name[len('static/'):], safe='/')
        request = urllib.request.Request(base + path, headers={'Cache-Control': 'no-cache'})
        with opener(request, timeout=30) as response:
            require(response.status == 200 and response.url == base + path,
                    'STAGED_FILE_REDIRECT_OR_HTTP_FAILURE')
            actual = response.read(len(body) + 1)
        require(actual == body, 'STAGED_FILE_BYTES_DIFFER')
        verified.append({'path': path, 'sha256': digest(actual), 'bytes': len(actual)})
    return verified


def run(root):
    require(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_REPOSITORY') == PROJECT,
            'PRIVATE_GITHUB_RUNNER_REQUIRED')
    root = Path(root).absolute()
    require(not root.resolve().is_relative_to(REPO) and not root.exists() and not root.is_symlink(),
            'FRESH_OUTSIDE_CHECKOUT_STAGE_REQUIRED')
    root.mkdir(mode=0o700, parents=True)
    token = os.environ.pop('VERCEL_TOKEN', '')
    # The existing read probe independently checks the pinned project/team.
    os.environ['VERCEL_TOKEN'] = token
    access = execute(root / 'read-auth')
    require(access['publisherAccessPassed'], 'EXISTING_PROJECT_READ_REQUIRED')
    archive = GitArchive(root / 'mirror', 'https://github.com/jessepike/sec-market.git')
    restored = archive.restore(root / 'state')
    state = LocalStore(root / 'state')
    manifest = state.read('staging-tests/' + SMOKE_ID + '.json')
    require(manifest and manifest.get('releaseId') == SMOKE_ID and
            manifest.get('mode') == 'stage_only_smoke_test', 'ARCHIVED_SMOKE_PAYLOAD_REQUIRED')
    baseline = state.read('heads/production.json')
    require(baseline and baseline.get('legacyBaseline'), 'RETAINED_PRODUCTION_BASELINE_REQUIRED')
    with PublisherAuth(root / 'stage-auth', token) as auth:
        auth.pin_verified_team()
        adapter = VercelAdapter(state, PROJECT_ID, TEAM_ID, SCOPE,
                                global_config=str(auth.root), runner=auth.isolated_runner)
        before = adapter._get(adapter.site, '/app-release.json')
        require(before == baseline['legacyAppReceipt'], 'LIVE_BASELINE_CHANGED_REVIEW_REQUIRED')
        deployment = adapter.stage(manifest)
        # Retain a safe immutable URL before probing, so a failed byte check
        # remains inspectable without dumping CLI output or remote errors.
        progress = {'deployment': deployment, 'productionPromoted': False}
        (root / 'progress.json').write_text(json.dumps(progress))
        acknowledgement = adapter.probe(deployment)
        require(acknowledgement == adapter.pending, 'STAGED_RECEIPT_DIFFERS')
        files = stage_files(state, manifest['artifact'], adapter.pending)
        verified = verify_files(deployment, files)
        after = adapter._get(adapter.site, '/app-release.json')
        require(before == after, 'PRODUCTION_CHANGED_DURING_STAGING')
    return {'publisherStagePassed': True, 'checkedAt': utcnow(),
            'githubRunId': os.environ['GITHUB_RUN_ID'], 'projectId': PROJECT_ID, 'teamId': TEAM_ID,
            'archive': restored, 'deployment': deployment, 'artifactSha256': manifest['artifact']['sha256'],
            'smokeAppRevision': manifest['appRevision'], 'acknowledgement': acknowledgement,
            'verifiedStaticFiles': verified, 'productionAppRevision': before['appRevision'],
            'productionUnchanged': True, 'productionPromoted': False, 'projectSettingsChanged': False,
            'archiveChanged': False, 'modelCalls': 0, 'independentReleaseGateAccepted': False,
            'productionPathsControlled': access['productionPathsControlled'],
            'dailyWorkerActivated': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        receipt = run(args.root)
    except Exception as error:
        # Keep the same bounded category-only transport failure policy as the
        # read probe. No raw remote response or token reaches the artifact.
        reason = str(error) if isinstance(error, (ValueError, RuntimeError)) else type(error).__name__
        allowed = ('STAGED_', 'ARCHIVED_', 'LIVE_', 'PRODUCTION_', 'EXISTING_', 'RETAINED_',
                   'PRIVATE_', 'FRESH_', 'VERCEL_READ_ONLY_', 'VERCEL_PREBUILT_')
        receipt = {'publisherStagePassed': False, 'reason': reason if reason.startswith(allowed) else type(error).__name__,
                   'productionPromoted': False, 'dailyWorkerActivated': False, 'modelCalls': 0}
        progress = Path(args.root) / 'progress.json'
        if progress.exists():
            receipt.update(json.loads(progress.read_text()))
    Path(args.output).write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    raise SystemExit(0 if receipt['publisherStagePassed'] else 2)
