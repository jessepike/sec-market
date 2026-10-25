"""Reproduce exact-J local proof; all retained source state remains read-only."""
import json
import os
from pathlib import Path
import socket
import sys
from unittest.mock import patch

REPO = Path('/mnt/mac/Users/jessepike/.codex/worktrees/q4-normal-intake/sec-market')
SCRATCH = Path('/var/tmp/smp-q4-normal-intake-build-20261025')
sys.path[:0] = [str(REPO / 'web/scripts/pipeline'), str(REPO / 'ops/ci')]
from contracts import canonical, digest, plan_run, validate_contract
from storage import LocalStore
from q4_intake_fixtures import ARCHIVE, MANIFEST, Overlay, ReadOnlyArchive
import q4_qualification_origin as q4
import q4_qualification_seed as seed
import q4_baseline_migration as baseline
from corrections import load_policy, process_corrections, group_review_policy
from onboarding import validate_qualification_probe_plan

before = json.loads((SCRATCH / 'baseline-authentication.json').read_bytes())
assert len(before['seals']) == 48245
denied = []
def audit(event, args):
    if event.startswith('socket.'):
        denied.append(event); raise AssertionError('No network in retained replay')
    if event == 'open':
        name, mode, flags = args[:3]
        write = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (
            isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if isinstance(name, (str, bytes)) and str(ARCHIVE) in str(name) and write:
            denied.append(event); raise AssertionError('Frozen archive write denied')
sys.addaudithook(audit)
at = '2026-10-25T12:30:00Z'  # Synthetic later replay clock; never a new source observation.
store = ReadOnlyArchive()
current = json.loads((REPO / 'contracts/market.json').read_bytes())
with patch.object(LocalStore, '__init__', side_effect=AssertionError('No frozen LocalStore initialization')):
    checked = seed.validate_seed(REPO, store, current, at)
    overlay = Overlay(store, checked['files'])
    original = q4.inverse_policy(current, overlay)
    transition = json.loads(overlay.get(q4.AUTHORITY['transition']))
    q4.validate_rows(original, current, transition)
    baseline.verify(REPO, current, overlay, json.loads((REPO / 'web/src/data/generated/dailyMarket.json').read_bytes()))
    def no_work(*_args, **_kwargs): raise AssertionError('No work may be requested')
    class NoModel:
        def __getattr__(self, key): return no_work
    context = load_policy(REPO, current)
    result = process_corrections(REPO, overlay, current, NoModel(), no_work, at)
    assert len(result['admitted']) == 6 and not result['pending'] and not result['attempts']
    probe = validate_qualification_probe_plan(current, overlay, REPO /
        'docs/active/daily-pipeline/accuracy/q4-normal-intake-disabled-J-plan-2026-10-25.json')

# Exercise the real bounded Pipeline/SubscriptionAgent/GuardedRunner fixture once
# more, observing only memory CAS values. Login status is synthetic; exec forbidden.
from test_q4_normal_intake import ActualProofTests
from replay_retained_audit import MemoryStore
case = ActualProofTests('test_zero_calls_real_subscription_guard_preserves_inventory_and_six_fetch_bound')
case.store, case.checked, case.contract = store, checked, current
counts = []
real_cas = MemoryStore.compare_and_swap
def observe_cas(self, name, expected, value):
    if name == 'budget-2026-10-25': counts.append(dict(value))
    return real_cas(self, name, expected, value)
with patch.object(MemoryStore, 'compare_and_swap', observe_cas):
    case.test_zero_calls_real_subscription_guard_preserves_inventory_and_six_fetch_bound()
assert counts and counts[-1]['calls'] == 80 and counts[-1]['documents'] <= 40

requests = json.loads((REPO / 'contracts/factual-corrections.json').read_bytes())
groups = {g['id']: group_review_policy(g, original, requests['baseline']['sha256']) for g in requests['groups']}
assert groups == context['reviewPolicySha256ByGroup']
for key, pin in before['seals'].items():
    path = ARCHIVE / key; raw = path.read_bytes()
    assert {'sha256': digest(raw), 'bytes': len(raw), 'mtimeNs': path.stat().st_mtime_ns} == pin, key
store.assert_unchanged()
protected = {key: digest((REPO / key).read_bytes()) for key, sha in before['codeBefore'].items()
             if key not in ('web/scripts/pipeline/source_qualification_origin.py',)}
assert all(protected[key] == before['codeBefore'][key] for key in protected)
source_pairs = [(s['id'], digest(s)) for s in original['sources'] if s['id'] not in q4.SOURCE_IDS]
assert source_pairs == [(s['id'], digest(s)) for s in current['sources'] if s['id'] not in q4.SOURCE_IDS]
proof = {'kind': 'local_exact_J_readonly_replay', 'actualExecution': False,
    'archive': {k: before[k] for k in ('archiveCommit', 'manifestSha256', 'manifestBytes', 'verifiedEntries')},
    'allArchiveBytesSizesMtimesUnchanged': True, 'archiveSealsSha256': digest(before['seals']),
    'H': q4.H, 'J': digest(current), 'wholeForwardAndInverseEqual': True,
    'requiredObligations': len(plan_run(current, at)['tasks']), 'unchangedSourceRows': len(source_pairs),
    'seedManifest': seed.PACKAGE, 'immutableFiles': len(checked['files']),
    'qualificationInventory': checked['qualificationInventory'], 'preservation': checked['preservation'],
    'sixExistingAdmissionGroups': [g['groupId'] for g in result['admitted']],
    'unchangedGroupReviewPolicies': groups, 'newOuterCorrectionPolicySha256': context['policySha256'],
    'normalMechanics': {'syntheticTransportAndLoginOnly': True, 'actualModelInvocations': 0,
        'beforeBudget': {'fetches': 985, 'calls': 80, 'documents': 38},
        'budgetReservations': counts, 'afterBudget': counts[-1],
        'logicalFetches': counts[-1]['fetches'] - 985, 'bound': 6,
        'pendingInventoryDocuments': [206, 323]},
    'disabledJPlan': {k: probe[k] for k in ('rawSha256', 'canonicalSha256', 'marketSha256', 'maxRequests', 'operation')},
    'protectedCodePins': protected, 'consultedRetainedInputs': {k: list(v) for k, v in store.touched.items()},
    'deniedAttempts': denied, 'credits': {'intake': 0, 'facts': 0, 'qualification': 0, 'publication': 0},
    'limits': ['9deb is a preservation fixture, not a future activation baseline.',
               'The normal mechanics use synthetic responses and a synthetic acknowledgement.',
               'Actual J seed, ordinary collection and publication remain unobserved.']}
out = SCRATCH / 'actual-readonly-replay.json'
out.write_text(json.dumps(proof, indent=2) + '\n')
print(json.dumps({k: proof[k] for k in ('J', 'requiredObligations', 'immutableFiles', 'normalMechanics')}, indent=2))
