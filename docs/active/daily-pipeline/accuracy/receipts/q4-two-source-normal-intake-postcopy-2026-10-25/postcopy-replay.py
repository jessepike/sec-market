"""Fresh-process finish-path validation over the newest authenticated actual archive."""
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022')
ARCHIVE = Path('/var/tmp/smp-listing-pagination-actual-40193925490-20261025/extracted')
OLDER = Path('/var/tmp/smp-next-seven-actual-40190857026-20261025/extracted')
OUT = Path('/var/tmp/smp-q4-normal-intake-postcopy-20261025')
sys.path[:0] = [str(ROOT / 'web/scripts/pipeline'), str(ROOT / 'ops/ci')]
from contracts import canonical, digest, plan_run, validate_contract
from storage import LocalStore
from q4_intake_fixtures import Overlay
import q4_qualification_seed as seed
import q4_qualification_origin as q4
import q4_baseline_migration as baseline
from corrections import load_policy, process_corrections, group_review_policy
from onboarding import validate_qualification_probe_plan

raw = (ARCHIVE / 'archive-manifest.json').read_bytes()
assert digest(raw) == '148842177a7e7d9a5fd5c2ea4574576264a957b41958ee4cdf5effa80ea029c2' and len(raw) == 10012399
entries = {r['key']: r for r in json.loads(raw)['files']}
assert len(entries) == 48420
seals = {}
for key, row in entries.items():
    path = ARCHIVE / key; body = path.read_bytes()
    assert digest(body) == row['sha256'] and len(body) == row['bytes'], key
    seals[key] = [digest(body), len(body), path.stat().st_mtime_ns]

denied = []
def audit(event, args):
    if event.startswith('socket.'):
        denied.append(event); raise AssertionError('No network in post-copy proof')
    if event == 'open':
        name, mode, flags = args[:3]
        mutation = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (
            isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if isinstance(name, (str, bytes)) and str(ARCHIVE) in str(name) and mutation:
            denied.append(event); raise AssertionError('Frozen archive mutation denied')
sys.addaudithook(audit)
class CurrentArchive:
    def __init__(self): self.consulted = {}
    def raw(self, key):
        row = entries.get('state/' + key)
        if row is None:
            assert not (ARCHIVE / 'state' / key).exists()
            return None
        path = ARCHIVE / 'state' / key; body = path.read_bytes()
        pin = [digest(body), len(body), path.stat().st_mtime_ns]
        assert pin == seals['state/' + key]
        self.consulted[key] = pin
        return body
    def read(self, key):
        body = self.raw(key)
        return json.loads(body) if body is not None else None
    def get(self, ref):
        body = self.raw(ref['key'])
        if body is None: raise FileNotFoundError(ref['key'])
        assert digest(body) == ref['sha256'] and len(body) == ref['bytes']
        return body
store = CurrentArchive()
market = json.loads((ROOT / 'contracts/market.json').read_bytes())
at = '2026-10-25T13:30:00Z'  # Local replay time only, no source clock is rewritten.
with patch.object(LocalStore, '__init__', side_effect=AssertionError('No frozen LocalStore constructor')):
    validate_contract(market)
    checked = seed.validate_seed(ROOT, store, market, at)
    overlay = Overlay(store, checked['files'])
    original = q4.inverse_policy(market, overlay)
    baseline.verify(ROOT, market, overlay, json.loads((ROOT / 'web/src/data/generated/dailyMarket.json').read_bytes()))
    class NoModel:
        def __getattr__(self, _): raise AssertionError('No model')
    def no_reserve(*_a, **_k): raise AssertionError('No quota reservation')
    outcome = process_corrections(ROOT, overlay, market, NoModel(), no_reserve, at)
    assert len(outcome['admitted']) == 6 and not outcome['pending'] and not outcome['attempts']
    disabled = validate_qualification_probe_plan(market, overlay, ROOT / 'contracts/source-qualification-probes.json')
    assert disabled['maxRequests'] == 0 and disabled['rawSha256'] == 'ef9ee1bab6cfe6202b62e8d5605393f045d11fd64bd42ea1bcea769de15c8a01'
normal = {}
for key in entries:
    if key.startswith('state/heads/') and key.removeprefix('state/heads/').startswith((
            'latest-run.', 'dailySnapshot.', 'production.', 'source-', 'task-', 'audit-', 'download-')):
        assert (ARCHIVE / key).read_bytes() == (OLDER / key).read_bytes(), key
        normal[key] = entries[key]['sha256']
for key, seal in seals.items():
    path = ARCHIVE / key; body = path.read_bytes()
    assert [digest(body), len(body), path.stat().st_mtime_ns] == seal, key
snapshot = store.read('heads/dailySnapshot.json')
budget = store.read('heads/budget-2026-10-25.json')
context = load_policy(ROOT, market)
proof = {'kind': 'post_copy_latest_actual_readonly_J_preflight', 'actualJExecution': False,
    'finishRoot': str(ROOT), 'J': digest(market), 'H': q4.H,
    'archive': {'commit': '9e4a9806fdcc1b7cd6f91314b8b4ff4bb4ef2174',
        'manifestSha256': digest(raw), 'manifestBytes': len(raw), 'entries': len(entries),
        'allBytesSizesMtimesVerifiedBeforeAfter': True, 'sealsSha256': digest(seals)},
    'normalHeadsUnchangedFrom9deb': {'count': len(normal), 'sha256': digest(normal)},
    'currentBudgetUnchanged': budget, 'currentSourceExpiryUnchanged': snapshot['coverage']['validUntil'],
    'currentHeldRowsUnchanged': len(snapshot['reviewQueue']), 'seedManifest': seed.PACKAGE,
    'immutableFiles': len(checked['files']), 'allFiveInventoryOrigins': checked['qualificationInventory'],
    'requiredObligations': len(plan_run(market, at)['tasks']), 'preservation': checked['preservation'],
    'oldAdmissionsReplayed': [entry['groupId'] for entry in outcome['admitted']],
    'groupPolicies': context['reviewPolicySha256ByGroup'], 'outerPolicySha256': context['policySha256'],
    'activePlan': {k: disabled[k] for k in ('rawSha256', 'canonicalSha256', 'marketSha256', 'maxRequests', 'operation')},
    'consultedInputSeals': store.consulted, 'deniedAttempts': denied,
    'sourceRequests': 0, 'modelRequests': 0, 'stateWrites': 0, 'quotaReservations': 0,
    'limits': ['Read-only local proof against the latest actual H archive; actual J collection and acknowledgement remain pending.']}
(OUT / 'latest-actual-preflight.json').write_text(json.dumps(proof, indent=2) + '\n')
print(json.dumps({k: proof[k] for k in ('J', 'archive', 'normalHeadsUnchangedFrom9deb', 'currentBudgetUnchanged',
    'currentHeldRowsUnchanged', 'requiredObligations')}, indent=2))
