#!/usr/bin/env python3
"""Release a dead GitHub runner's lease without refunding unknown usage."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'web/scripts/pipeline'))
from archive import GitArchive
from contracts import digest, require, utcnow
from storage import LocalStore


def github_run(run_id):
    result = subprocess.run(['gh', 'api', 'repos/jessepike/sec-market/actions/runs/' + run_id],
                            capture_output=True, text=True, timeout=60)
    require(result.returncode == 0, 'LEASE_RECOVERY_RUN_STATUS_UNAVAILABLE')
    return json.loads(result.stdout)


def release_terminated(store, lookup=github_run):
    lease = store.read('heads/cloud-lease.json')
    if not lease or lease.get('releasedAt'):
        return {'recovered': False, 'reason': 'NO_ACTIVE_LEASE'}
    matched = re.fullmatch(r'github-(?:publisher-)?([0-9]+)-([0-9]+)', lease.get('sessionId', ''))
    require(matched is not None, 'ACTIVE_LEASE_IS_NOT_GITHUB_RUNNER')
    run = lookup(matched[1])
    require(run.get('id') == int(matched[1]) and run.get('repository', {}).get('full_name') == 'jessepike/sec-market',
            'LEASE_RECOVERY_RUN_IDENTITY_DIFFERS')
    require(run.get('status') == 'completed' and bool(run.get('conclusion')), 'LEASE_OWNER_STILL_RUNNING')
    # A rerun uses the same run ID. An older finished attempt does not prove
    # that the current attempt has stopped.
    require(int(run.get('run_attempt', 0)) >= int(matched[2]), 'LEASE_RECOVERY_RUN_ATTEMPT_DIFFERS')
    budgets = {p.name: p.read_bytes() for p in (store.root / 'heads').glob('budget-*.json')}
    recovered = {**lease, 'releasedAt': utcnow(), 'recovery': {
        'githubRunId': run['id'], 'conclusion': run['conclusion'], 'unknownCapacityRetained': True}}
    store.compare_and_swap('cloud-lease', lease, recovered)
    require(budgets == {p.name: p.read_bytes() for p in (store.root / 'heads').glob('budget-*.json')},
            'LEASE_RECOVERY_MUST_NOT_CHANGE_BUDGETS')
    return {'recovered': True, 'lease': recovered, 'budgetSha256': {k: digest(v) for k, v in budgets.items()}}


def recover(root):
    root = Path(root).resolve()
    archive = GitArchive(root / 'archive', 'https://github.com/jessepike/sec-market.git')
    restored = archive.restore(root / 'state')
    store = LocalStore(root / 'state')
    result = release_terminated(store)
    if result['recovered']:
        store.write_once('ci/lease-recoveries/' + digest(result['lease']) + '.json', result)
        result['archive'] = archive.push(store, expected_commit=restored['commit'])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    args = parser.parse_args()
    print(json.dumps(recover(args.root), indent=2))
