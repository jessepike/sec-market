"""Offline November 2 companion. Never import seeds into the authoritative archive."""
import argparse
import json
import pathlib
import socket
import sys
import time
from unittest.mock import patch

parser = argparse.ArgumentParser()
parser.add_argument('--repo', type=pathlib.Path, required=True)
parser.add_argument('--archive', type=pathlib.Path, required=True)
parser.add_argument('--output', type=pathlib.Path, required=True)
args = parser.parse_args()
R, A, O = args.repo.resolve(), args.archive.resolve(), args.output.resolve()
S = A / 'state'
assert not O.is_relative_to(A)
sys.path[:0] = [str(R / 'web/scripts/pipeline'), str(R / 'ops/ci')]
from contracts import canonical, digest
import three_source_qualification_seed as seed
import three_source_qualification_origin as three
import three_source_baseline_migration as migration
import html_qualification_seed as html
from corrections import (load_policy, process_corrections, project_bundle, _index,
                         replay_admission, group_review_policy)
from artifacts import stage_files
from storage import LocalStore
from separation import semantic_context, original_contract
from retained_audit import AuditIndex, HistoricalStoreView, verify_receipt, separated_details
from snapshot import verify_document_marker, verify_document_resolution, document_marker

started = time.monotonic()
manifest_raw = (A / 'archive-manifest.json').read_bytes()
assert digest(manifest_raw) == '3cb739133b60e03d418480e53ee8c454dca616efa8d3585fde87c5eb9ac61438'
entries = {row['key']: row for row in json.loads(manifest_raw)['files']}
assert len(entries) == 69873


def seal():
    result = {}
    for key, row in entries.items():
        p = A / key
        assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(A)
        raw = p.read_bytes()
        st = p.stat()
        assert len(raw) == row['bytes'] and digest(raw) == row['sha256']
        assert not st.st_mode & 0o222, key
        if key.startswith('state/objects/'):
            assert p.name == digest(raw)
        result[key] = {'sha256': digest(raw), 'bytes': len(raw), 'mtimeNs': st.st_mtime_ns,
                       'mode': st.st_mode}
    extras = {'.gitattributes', 'archive-manifest.json', 'vercel.json', 'web/vercel.json'}
    assert {p.relative_to(A).as_posix() for p in A.rglob('*') if p.is_file()} == set(entries) | extras
    for key in extras:
        p = A / key
        raw, st = p.read_bytes(), p.stat()
        assert not p.is_symlink() and not st.st_mode & 0o222
        result[key] = {'sha256': digest(raw), 'bytes': len(raw), 'mtimeNs': st.st_mtime_ns, 'mode': st.st_mode}
    return result


before_seal = seal()
readset = {}
original_read_bytes = pathlib.Path.read_bytes


def tracked_read(p):
    raw = original_read_bytes(p)
    if p.is_relative_to(A):
        key = p.relative_to(A).as_posix()
        if key in before_seal:
            row = {'sha256': digest(raw), 'bytes': len(raw), 'mtimeNs': p.stat().st_mtime_ns,
                   'mode': p.stat().st_mode}
            assert row == before_seal[key]
            readset[key] = row
    return raw


class ReadOnly:
    root = S

    def raw(self, key):
        archive_key = 'state/' + key
        if archive_key not in entries:
            assert not (S / key).exists()
            return None
        return (S / key).read_bytes()

    def read(self, key):
        raw = self.raw(key)
        return json.loads(raw) if raw is not None else None

    def get(self, ref):
        raw = self.raw(ref['key'])
        if raw is None:
            raise FileNotFoundError(ref['key'])
        assert digest(raw) == ref['sha256'] and len(raw) == ref['bytes']
        return raw


class NoModel:
    def __getattr__(self, name):
        raise AssertionError('NO_MODEL')


def deny(*_args, **_kwargs):
    raise AssertionError('NO_NETWORK_RESERVATION_OR_PERSISTENT_STORE')


base = ReadOnly()
market = json.loads((R / 'contracts/market.json').read_bytes())
at = '2026-11-02T15:00:00Z'
with patch.object(pathlib.Path, 'read_bytes', tracked_read), \
        patch.object(socket.socket, 'connect', deny), \
        patch.object(socket, 'create_connection', deny), \
        patch.object(LocalStore, '__init__', deny):
    checked = seed.validate_seed(R, base, market, at)
    overlay = html._Overlay(base, checked['files'])
    overlay.root = S  # Index scans the actual immutable state; seed data remains in memory.
    old = three.inverse_policy(market, overlay)
    assert digest(old) == three.J and digest(market) == three.AUTHORITY['activatedContractSha256']
    unchanged_contexts = {}
    for source in old['sources']:
        sid = source['id']
        if sid not in three.SOURCE_IDS:
            assert canonical(semantic_context(old, sid)) == canonical(semantic_context(market, sid))
            unchanged_contexts[sid] = digest(semantic_context(old, sid))
    baseline = migration.migrate(R, market, overlay)
    migration.verify(R, market, overlay, baseline)
    assert baseline == json.loads((R / 'web/src/data/generated/dailyMarket.json').read_bytes())
    assert baseline['coverage']['successfulTasks'] == 0 and baseline['coverage']['validUntil'] is None

    production = base.read('heads/production.json')
    release = base.read('releases/' + production['releaseId'] + '.json')
    files = stage_files(base, release['manifest']['artifact'], release['acknowledgement'])
    previous = json.loads(files['static/factual-corrections.json'])
    context = load_policy(R, market)
    for group in context['requests']['groups']:
        assert group_review_policy(group, old, context['requests']['baseline']['sha256']) == context['reviewPolicySha256ByGroup'][group['id']]
    prior = [base.read(_index(group, context['reviewPolicySha256ByGroup'][group['id']]))
             for group in context['requests']['groups']]
    result = process_corrections(R, overlay, market, NoModel(), deny, at, clock=lambda: at)
    assert len(result['admitted']) == 8 and result['pending'] == result['attempts'] == []
    assert result['admitted'] == prior
    admissions = {group['id']: replay_admission(group, row['admission'], overlay, market,
                   context['reviewPolicySha256ByGroup'][group['id']], at)
                  for group, row in zip(context['requests']['groups'], prior)}
    projected = project_bundle(R, overlay, market, result, previous_bundle=previous, publication_at=at)
    assert projected['groups'] == previous['groups'] and projected['policySha256'] != previous['policySha256']

    snap = base.read('heads/cloud-snapshot.json')
    assert snap['contractSha256'] == three.J and len(snap['reviewQueue']) == 51
    assert snap['coverage']['processing']['reviewedDocuments'] == 83
    assert snap['coverage']['historicalReview']['reviewedDocuments'] == 84
    assert snap['coverage']['processing']['heldDocuments'] == 20
    assert snap['coverage']['processing']['inventoryDocuments'] == 11671
    for item in snap['reviewQueue']:
        if item.get('kind') == 'source_document_revalidation':
            verify_document_marker(item, overlay)
    for item in snap['documentReviewResolutions']:
        assert verify_document_resolution(item, overlay) == item

    index = AuditIndex(overlay)
    overlay._retained_audit_index = index
    current = [(r, origin) for r, origin in index.receipts.values() if r['runId'] == snap['runId']]
    assert len(current) == 557
    inventories = {}
    current_receipt_identities = [{'sourceId': r['sourceId'], 'origin': origin, 'receiptSha256': digest(r),
                                  'startedAt': r['startedAt'], 'completedAt': r['completedAt'],
                                  'errorCode': r.get('errorCode')} for r, origin in current]
    retained, replay_failures = [], []
    for receipt, origin in current:
        if receipt.get('retainedAuditVersion') != 2:
            continue
        sid = receipt['sourceId']
        original = original_contract(overlay, origin)
        source = next(s for s in original['sources'] if s['id'] == sid)
        view = HistoricalStoreView(overlay, receipt)
        plan = overlay.read('runs/' + receipt['runId'] + '/plan.json')
        partitions = json.loads(overlay.get(receipt['processingManifest']))
        failure = None
        try:
            verify_receipt(receipt, plan, original, source, receipt['completedAt'], view)
            details = separated_details(receipt, original, source, receipt['completedAt'], view)
            assert partitions == {'schemaVersion': 2, 'sourceId': sid, 'runId': receipt['runId'], **details['partitions']}
        except (ValueError, KeyError, TypeError, AssertionError) as exc:
            failure = {'sourceId': sid, 'origin': origin, 'errorType': type(exc).__name__, 'error': str(exc),
                       'originalItemManifest': json.loads(overlay.get(receipt['itemManifest'])),
                       'originalDiscoveryComplete': receipt.get('discoveryComplete'),
                       'originalDiscoveryRecorded': receipt.get('discoveryRecorded'),
                       'originalError': receipt.get('errorCode')}
            replay_failures.append(failure)
            print(json.dumps({'retainedReplayFailure': {k: failure[k] for k in ('sourceId', 'errorType', 'error')}}),
                  file=sys.stderr, flush=True)
        # K changes only three candidate adapters. Every other historical proof is
        # rechecked with exactly the same semantic context and original clocks.
        if sid not in three.SOURCE_IDS:
            assert semantic_context(original, sid) == semantic_context(market, sid)
        inv = json.loads(overlay.get(receipt['retainedInventoryManifest']))
        inventories[sid] = {'originalOrigin': origin, 'inventorySha256': digest(inv),
                           'inventory': inv, 'processingManifest': partitions,
                           'itemManifest': json.loads(overlay.get(receipt['itemManifest'])),
                           'predecessorOrigins': receipt['retainedInventoryPredecessors'],
                           'originalStartedAt': receipt['startedAt'], 'originalCompletedAt': receipt['completedAt']}
        retained.append({'sourceId': sid, 'receiptSha256': digest(receipt),
                         'errors': {k: v for k, v in receipt.items() if 'error' in k.lower()},
                         'retainedBindingsSha256': digest(receipt.get('retainedAuditBindings', [])),
                         'documentValidationsSha256': digest(receipt.get('documentValidations', [])),
                         'heldClaims': receipt.get('heldClaims', []),
                         'independentlyReplayed': failure is None})
    # Preserve queued claims and resolutions byte-for-byte; derived markers are
    # separately inventoried, never regenerated under a new policy or removed.
    markers = [item for item in snap['reviewQueue'] if item.get('kind') == 'source_document_revalidation']
    derived = [{'before': item, 'after': item, 'changed': False} for item in markers]
    source_clocks = [{'sourceId': sid, 'url': url,
                      'observations': [{k: ob.get(k) for k in ('observationId', 'fetchedAt', 'verifiedAt',
                          'status', 'httpStatus', 'body', 'contentType', 'requestedUrl', 'finalUrl', 'reusesObservationId')}
                          for _, ob in sorted(history.items())]}
                     for (sid, url), history in sorted(index.observation_history.items())]
    for sid, n in zip(three.SOURCE_IDS, (127, 47, 56)):
        qualified = three.resolve(three.predecessors(market, sid, overlay, at)[0], market, sid, overlay, at)
        assert len(qualified['items']) == len(qualified['itemDates']) == n

after_seal = seal()
assert before_seal == after_seal
assert all(after_seal[k] == row for k, row in readset.items())
O.mkdir(parents=True, exist_ok=True)
for name, value in [('archive-before.json', before_seal), ('archive-after.json', after_seal),
                    ('readset.json', readset), ('current-inventories.json', inventories),
                    ('retained-receipts.json', retained), ('replay-failures.json', replay_failures),
                    ('current-receipt-identities.json', current_receipt_identities),
                    ('original-source-clocks.json', source_clocks),
                    ('review-queue.json', snap['reviewQueue']),
                    ('document-review-resolutions.json', snap['documentReviewResolutions']),
                    ('derived-hold-markers.json', derived), ('correction-admissions.json', admissions)]:
    (O / name).write_bytes(canonical(value))
summary = {'kind': 'three_source_current_j_readonly_replay',
    'archive': {'commit': '52632a360f4099f142ed0e10e46338e1d91f1bc9', 'manifestSha256': digest(manifest_raw),
                'entries': len(entries), 'beforeSha256': digest(before_seal), 'afterSha256': digest(after_seal),
                'allBytesAndMtimesUnchanged': True, 'consumedEntries': len(readset), 'readsetSha256': digest(readset)},
    'contractSha256': digest(market), 'previousContractSha256': digest(old),
    'seedManifestSha256': checked['manifestSha256'], 'immutableUnionFiles': len(checked['files']),
    'qualificationInventories': checked['qualificationInventory'], 'historicalPreservation': checked['preservation'],
    'unchangedSemanticContexts': len(unchanged_contexts), 'semanticContextMapSha256': digest(unchanged_contexts),
    'prospectiveBaselineOnly': True, 'prospectiveBaselineSuccessfulTasks': 0,
    'currentState': {'runId': snap['runId'], 'snapshotSha256': snap['snapshotSha256'],
        'reviewQueue': {'entries': len(snap['reviewQueue']), 'sha256': digest(snap['reviewQueue'])},
        'processing': snap['coverage']['processing'], 'historicalReview': snap['coverage']['historicalReview'],
        'currentReceiptsRead': len(current), 'retainedReceiptsAttempted': len(retained),
        'retainedReceiptsReplayed': sum(r['independentlyReplayed'] for r in retained),
        'retainedReplayFailures': [{k: r[k] for k in ('sourceId', 'errorType', 'error')} for r in replay_failures],
        'documentResolutionCount': len(snap['documentReviewResolutions']), 'derivedHoldMarkerChanges': 0,
        'allQueueIdentitiesAndResolutionsPreserved': True,
        'originalSourceClockSubjects': len(source_clocks), 'originalSourceClocksSha256': digest(source_clocks)},
    'corrections': {'cachedAdmissions': 8, 'priorIndexRows': prior,
        'originalAdmittedAt': {k: v['admittedAt'] for k, v in admissions.items()},
        'perGroupReviewPolicy': context['reviewPolicySha256ByGroup'],
        'publishedGroupsSha256': digest(previous['groups']),
        'publishedGroupDates': {g['id']: g['date'] for g in previous['groups']},
        'allPublicGroupsExactlyPreserved': True},
    'productionHeadReadOnly': production, 'sourceRequests': 0, 'modelCalls': 0, 'reservations': 0,
    'stateWrites': 0, 'publicationAttempts': 0, 'coverageCredit': False, 'semanticAdmission': False,
    'currentReplayPassed': not replay_failures,
    'durationSeconds': round(time.monotonic() - started, 3)}
(O / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({k: summary[k] for k in ('archive', 'currentState', 'durationSeconds')}, indent=2))
raise SystemExit(0 if summary['currentReplayPassed'] else 2)
