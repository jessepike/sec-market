#!/usr/bin/env python3
"""Create an isolated, non-publishable correction UI fixture; never an admission.

Run in OrbStack only. The destination must be new and outside the checkout.
This uses no source fetch, subscription request, archive write or quota change.
It deliberately does not create a gate seal or semantic admission record.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'web/scripts/pipeline'))
from contracts import digest, instant


def create_fixture(repo, destination, checked_at):
    repo, destination = Path(repo).resolve(), Path(destination).resolve()
    if destination.exists() or destination.is_relative_to(repo):
        raise ValueError('A fresh destination outside the checkout is required')
    instant(checked_at)
    destination.mkdir(parents=True)
    shutil.copytree(repo / 'contracts', destination / 'contracts')
    shutil.copytree(repo / 'web', destination / 'web', ignore=shutil.ignore_patterns(
        'node_modules', 'dist', 'dist-ssr', 'test-results', 'playwright-report', '__pycache__', '.env*', '.vercel', '.git'))
    (destination / 'web/node_modules').symlink_to(repo / 'web/node_modules', target_is_directory=True)
    requests = json.loads((repo / 'contracts/factual-corrections.json').read_bytes())
    stamp = json.loads((repo / 'web/src/data/tracker/factualCorrectionPolicy.json').read_bytes())
    bundle = {'schemaVersion': 1, 'enabled': True, 'policySha256': stamp['policySha256'], 'checkedAt': checked_at, 'groups': []}
    for group in requests['groups']:
        bundle['groups'].append({'id': group['id'], 'supplierId': group['supplierId'], 'reasonCode': group['reasonCode'],
            'date': checked_at[:10], 'note': group['noteTemplate'].replace('{date}', checked_at[:10]), 'targets': group['targets'],
            'admission': {'candidateSha256': digest(group), 'evidenceSetSha256': digest(group['sources']),
                'policySha256': stamp['policySha256'], 'admittedAt': checked_at,
                'reviewSha256': digest({'syntheticNonAdmittingVisualFixture': group['id']}), 'result': 'accepted'}})
    target = destination / 'web/src/data/generated/factualCorrections.json'
    target.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + '\n')
    target.with_suffix('.seal.json').unlink(missing_ok=True)
    receipt = {'kind': 'synthetic_non_admitting_visual_fixture', 'semanticAdmission': False, 'publishable': False,
        'checkedAt': checked_at, 'policySha256': stamp['policySha256'], 'groups': len(bundle['groups']),
        'targets': sum(len(group['targets']) for group in bundle['groups']), 'modelCalls': 0, 'sourceRequests': 0,
        'bundleSha256': digest(target.read_bytes()), 'fixture': str(destination)}
    (destination / 'SYNTHETIC-NON-ADMITTING.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=REPO)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--at', required=True)
    args = parser.parse_args()
    print(json.dumps(create_fixture(args.repo, args.destination, args.at)))
