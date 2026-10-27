"""Offline selection/preflight receipt. Never executes the source operation."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
ACTIVE = 'contracts/source-qualification-probes.json'
CANDIDATE = 'docs/active/daily-pipeline/accuracy/cyera-primary-capture-plan-2026-10-25.json'
DISABLED = 'ef9ee1bab6cfe6202b62e8d5605393f045d11fd64bd42ea1bcea769de15c8a01'
SELECTED = '25bf0ff72555188e7a8446b9499f3b8ba56c9327e397f8b70a5ce9deb82d350f'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def tracked():
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    return {name: {'sha256': sha((ROOT / name).read_bytes()), 'bytes': (ROOT / name).stat().st_size}
            for name in names if name}

def prepare():
    before = (ROOT / ACTIVE).read_bytes()
    selected = (ROOT / CANDIDATE).read_bytes()
    assert sha(before) == DISABLED and sha(selected) == SELECTED
    assert not (OUT / 'disabled-plan.json').exists()
    (OUT / 'disabled-plan.json').write_bytes(before)
    base = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
            'files': tracked()}
    (OUT / 'tracked-before.json.gz').write_bytes(gzip.compress(json.dumps(base, sort_keys=True).encode(), mtime=0))
    (ROOT / ACTIVE).write_bytes(selected)
    save('selection.json', {'authority': 'D-110/D-111/D-112; root delegated exact reviewed plan selection',
         'baseHead': base['head'], 'originalPlanRawSha256': sha(before), 'originalPlanBytes': len(before),
         'selectedPlanRawSha256': sha(selected), 'selectedPlanBytes': len(selected),
         'request': json.loads(selected)['sample']['request'], 'maximumLogicalRequests': 1,
         'explicitRetries': 0, 'modelCalls': 0, 'documentReservations': 0, 'gateAttempts': 0,
         'sourceChecksCredited': 0, 'qualifiedSources': 0, 'semanticAdmission': False,
         'coverageCredit': False, 'dispatched': False, 'executed': False})

def preflight(args):
    archive = Path(args.archive).resolve()
    manifest_path = archive / 'archive-manifest.json'
    manifest_raw = manifest_path.read_bytes()
    assert sha(manifest_raw) == args.manifest_sha256
    entries = {r['key']: r for r in json.loads(manifest_raw)['files']}
    assert len(entries) == args.manifest_files
    download_raw = (archive.parent / 'download-proof.json').read_bytes()
    download = json.loads(download_raw)
    assert download['allManifestEntriesVerified'] is True
    assert download['archiveAck']['commit'] == args.ack_commit
    assert download['archiveAck']['manifestSha256'] == args.manifest_sha256
    assert download['archiveAck']['files'] == len(entries)
    assert download['extractedRoot'] == str(archive)
    consumed = {}
    class ReadOnly:
        def raw(self, key):
            relative = 'state/' + key
            path, row = archive / relative, entries[relative]
            assert not path.is_symlink() and path.resolve().is_relative_to(archive)
            raw = path.read_bytes()
            assert sha(raw) == row['sha256'] and len(raw) == row['bytes']
            stat = path.stat()
            consumed[relative] = {**row, 'mtimeNs': stat.st_mtime_ns, 'inode': stat.st_ino}
            return raw
        def get(self, ref):
            raw = self.raw(ref['key'])
            assert sha(raw) == ref['sha256'] and len(raw) == ref['bytes']
            return raw
        def read(self, key):
            return json.loads(self.raw(key))
    sys.path[:0] = [str(ROOT / 'ops/ci'), str(ROOT / 'web/scripts/pipeline')]
    from storage import LocalStore
    from fetcher import Fetcher
    from agents import SubscriptionAgent
    import cyera_primary_capture as op
    from contracts import digest
    contract = json.loads((ROOT / 'contracts/market.json').read_bytes())
    selected = (ROOT / ACTIVE).read_bytes()
    assert sha(selected) == SELECTED
    heads = {r: sha((archive / r).read_bytes()) for r in entries if r.startswith('state/heads/')}
    blocked = []
    def audit(event, values):
        if event in ('socket.connect', 'subprocess.Popen'):
            blocked.append(event)
            raise AssertionError('NO_SOURCE_OR_OTHER_NETWORK')
        if event == 'open':
            path, mode, flags = values
            writing = isinstance(mode, str) and any(c in mode for c in 'wax+') or isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
            if writing:
                raise AssertionError('NO_WRITES_DURING_PLAN_VALIDATION:' + str(path))
    sys.addaudithook(audit)
    # The hook remains read-only for this process; emit the result on stdout.
    with patch.object(LocalStore, '__init__', side_effect=AssertionError('NO_FROZEN_LOCALSTORE')), \
         patch.object(Fetcher, 'fetch', side_effect=AssertionError('NO_SOURCE_REQUEST')), \
         patch.object(SubscriptionAgent, 'call', side_effect=AssertionError('NO_MODEL_CALL')), \
         patch.object(op.PersistentProbeBudget, '__init__', side_effect=AssertionError('NO_BUDGET_CONTEXT')), \
         patch.object(op.PersistentProbeBudget, 'reserve_fetch', side_effect=AssertionError('NO_RESERVATION')):
        normalized = op.validate_plan(contract, ReadOnly(), selected, ROOT / ACTIVE)
    for relative, pin in consumed.items():
        path = archive / relative
        assert sha(path.read_bytes()) == pin['sha256'] and path.stat().st_size == pin['bytes']
        assert path.stat().st_mtime_ns == pin['mtimeNs'] and path.stat().st_ino == pin['inode']
    assert heads == {r: sha((archive / r).read_bytes()) for r in heads}
    assert sha(manifest_path.read_bytes()) == args.manifest_sha256
    stream = normalized['streams'][0]
    result = {'status': 'PASS', 'authority': 'offline exact selected-plan preflight only',
              'archive': str(archive), 'acknowledgedArchiveCommit': args.ack_commit,
              'manifestSha256': args.manifest_sha256, 'manifestFiles': len(entries),
              'downloadProof': {'path': str(archive.parent / 'download-proof.json'),
                                'sha256': sha(download_raw), 'bytes': len(download_raw),
                                'allManifestEntriesVerified': True, 'runId': download['runId']},
              'policyCanonicalSha256': digest(contract), 'selectedPlanRawSha256': sha(selected),
              'retainedCards': len(stream['records']), 'currentWindowItems': stream['currentWindowItems'],
              'knownSeeds': stream['knownSeedMembership'], 'originalIndexFetchedAt': stream['asOf'],
              'originalWindowStart': stream['windowStart'], 'originalWindowEnd': stream['windowEnd'],
              'readSet': list(consumed.values()), 'readSetFiles': len(consumed),
              'unchangedHeads': heads, 'networkAttempts': blocked, 'sourceRequests': 0,
              'modelCalls': 0, 'documentReservations': 0, 'gateAttempts': 0,
              'explicitDenials': ['source_fetch', 'subscription_model_call', 'budget_context', 'fetch_reservation',
                                 'frozen_LocalStore', 'socket_connect', 'subprocess', 'all_file_writes'],
              'archiveWrites': 0, 'coverageCredit': False, 'qualified': False}
    print(json.dumps(result, indent=2, sort_keys=True))

def protection():
    before = json.loads(gzip.decompress((OUT / 'tracked-before.json.gz').read_bytes()))
    current = tracked()
    changed = {k: {'before': v, 'after': current.get(k)} for k, v in before['files'].items() if current.get(k) != v}
    assert changed.get(ACTIVE, {}).get('before', {}).get('sha256') == DISABLED
    assert changed[ACTIVE]['after']['sha256'] == SELECTED
    owned = {ACTIVE, 'ops/ci/test_q4_normal_intake.py'}
    protected = [k for k in changed if k not in owned and not k.startswith('docs/') and k not in ('status.md', 'BACKLOG.md')]
    assert not protected, protected
    assert sha((OUT / 'disabled-plan.json').read_bytes()) == DISABLED
    save('tracked-protection.json', {'baseHead': before['head'], 'trackedFiles': len(before['files']),
         'changedTrackedFiles': changed, 'unexpectedProtectedChanges': protected,
         'disabledOriginalPreserved': True, 'selectedPlanExact': True,
         'operatorOwnedPaths': sorted(owned),
         'concurrentDocumentationChangesExcludedFromOperatorOwnership': [k for k in changed if k not in owned]})

parser = argparse.ArgumentParser()
parser.add_argument('action', choices=['prepare', 'preflight', 'protection'])
parser.add_argument('--archive')
parser.add_argument('--manifest-sha256')
parser.add_argument('--manifest-files', type=int)
parser.add_argument('--ack-commit')
args = parser.parse_args()
if args.action == 'prepare':
    prepare()
elif args.action == 'preflight':
    preflight(args)
else:
    protection()
