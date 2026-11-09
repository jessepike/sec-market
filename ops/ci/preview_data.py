#!/usr/bin/env python3
"""Copy the data the release gate accepted onto the preview branch.

Production is built only by the gate, from the evidence archive. Preview builds
from the data committed on the branch, which no daily run updated, so the
preview URL showed October 21 data. After each acknowledged publish this copies
the gate's tested build inputs (web/src/data/generated) to preview.

It never touches main or production. It skips, without failing, when preview's
own checks would not accept the data (for example, preview already carries a
different source contract): the next publish after promotion catches up.
"""
import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

PROJECT = 'jessepike/sec-market'
GATE_WORKFLOW = '.github/workflows/market-release-gate.yml'
TARGET = Path('web/src/data/generated')
NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]*\.json')
MAX_BYTES = 50_000_000


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def gh(path, binary=False, runner=subprocess.run):
    result = runner(['gh', 'api', f'repos/{PROJECT}/{path}'], capture_output=True, timeout=120)
    if result.returncode:
        raise RuntimeError('GITHUB_API_FAILED')
    if len(result.stdout) > 100_000_000:
        raise RuntimeError('GATE_ARTIFACT_TOO_LARGE')
    return result.stdout if binary else json.loads(result.stdout)


def accepted_files(gate_run_id, api=gh):
    """Download and check the gate's artifact; return {name: bytes} and its receipt."""
    run = api(f'actions/runs/{gate_run_id}')
    if not (run.get('path') == GATE_WORKFLOW and run.get('head_branch') == 'main'
            and run.get('status') == 'completed' and run.get('conclusion') == 'success'):
        raise RuntimeError('GATE_RUN_NOT_A_PASSED_MAIN_GATE')
    listing = api(f'actions/runs/{gate_run_id}/artifacts?per_page=20')['artifacts']
    named = [a for a in listing if a.get('name') == 'daily-market-gate' and not a.get('expired')]
    if len(named) != 1:
        raise RuntimeError('GATE_ARTIFACT_MISSING')
    payload = api(f"actions/artifacts/{named[0]['id']}/zip", binary=True)
    if named[0].get('digest') != 'sha256:' + sha256(payload):
        raise RuntimeError('GATE_ARTIFACT_DIGEST_DIFFERS')
    with zipfile.ZipFile(io.BytesIO(payload)) as outer:
        receipt = json.loads(outer.read('gate-receipt.json'))
        bundle = outer.read('generated.zip')
    if receipt.get('result') != 'pass' or receipt.get('githubRunId') != gate_run_id \
            or receipt.get('appRevision') != run.get('head_sha'):
        raise RuntimeError('GATE_RECEIPT_DIFFERS')
    if receipt.get('generatedSha256') != sha256(bundle):
        raise RuntimeError('GENERATED_BUNDLE_DIFFERS_FROM_RECEIPT')
    return unpack(bundle), receipt


def unpack(bundle):
    files = {}
    with zipfile.ZipFile(io.BytesIO(bundle)) as inner:
        members = inner.infolist()
        if not members or len(members) > 40:
            raise RuntimeError('GENERATED_BUNDLE_INVENTORY_DIFFERS')
        for item in members:
            if not NAME.fullmatch(item.filename) or item.file_size > MAX_BYTES:
                raise RuntimeError('GENERATED_BUNDLE_MEMBER_REFUSED')
            files[item.filename] = inner.read(item)
    return files


def git(repo, *args, check=True):
    return subprocess.run(['git', '-C', str(repo), *args], check=check, capture_output=True, text=True)


def write(repo, files):
    folder = Path(repo) / TARGET
    for name, raw in files.items():
        (folder / name).write_bytes(raw)


def preview_accepts(repo):
    """Run the daily-data and correction checks the preview build runs.

    The correction bundle is stamped with the release's contract, so a preview
    that already carries a newer contract refuses it and keeps its own data.
    """
    script = ("Promise.all([import('./web/scripts/verify-daily.mjs'), import('./web/scripts/verify-factual-corrections.mjs')])"
              ".then(([d, c]) => { d.verifyDaily('web'); c.verifyFactualCorrections('web') })")
    return subprocess.run(['node', '--input-type=module', '-e', script], cwd=repo,
                          capture_output=True, text=True, timeout=120).returncode == 0


def sync(repo, gate_run_id, api=gh, attempts=3):
    repo = Path(repo).resolve()
    files, receipt = accepted_files(gate_run_id, api)
    message = (f'data(preview): accepted data from release gate run {gate_run_id}\n\n'
               f"Collection {receipt.get('runId')}, app revision {receipt.get('appRevision')}.\n"
               'Copied by the publisher after an acknowledged release; production is unchanged.\n')
    for _ in range(attempts):
        git(repo, 'fetch', '--quiet', 'origin', 'preview')
        git(repo, 'reset', '--quiet', '--hard', 'origin/preview')
        write(repo, files)
        if not git(repo, 'status', '--porcelain', '--', str(TARGET)).stdout.strip():
            return {'synced': False, 'reason': 'PREVIEW_ALREADY_CURRENT'}
        if not preview_accepts(repo):
            git(repo, 'checkout', '--', str(TARGET))
            return {'synced': False, 'reason': 'PREVIEW_CHECKS_REFUSE_THIS_DATA'}
        git(repo, 'add', '--', str(TARGET))
        git(repo, '-c', 'user.name=Jesse Pike', '-c', 'user.email=jesse@keatingpike.com',
            'commit', '--quiet', '-m', message)
        if git(repo, 'push', '--quiet', 'origin', 'HEAD:preview', check=False).returncode == 0:
            return {'synced': True, 'commit': git(repo, 'rev-parse', 'HEAD').stdout.strip(),
                    'gateRunId': gate_run_id, 'runId': receipt.get('runId')}
    return {'synced': False, 'reason': 'PREVIEW_MOVED_DURING_PUSH'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True)
    parser.add_argument('--gate-run', required=True, type=int)
    args = parser.parse_args()
    result = sync(args.repo, args.gate_run)
    print(json.dumps(result))
    if not result['synced']:
        print(f"::notice title=preview-data::{result['reason']}")
    sys.exit(0)
