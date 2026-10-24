"""Dormant qualification-origin bookkeeping; all completion fixtures are fictional.

The collaborator replay mock supplies fictional validated terminal evidence. It does
not assert that the actual Delinea traversal has completed. A separate test uses the
real bounded replay and confirms its authentic incomplete fixture cannot activate.
"""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
sys.path.insert(0, str(ROOT / 'ops/ci'))

from contracts import canonical, digest
from onboarding import BOUNDED_CANDIDATE_BINDINGS, _candidate_adapter
from storage import LocalStore
from source_qualification_origin import (qualification_predecessors, resolve_inventory_origin,
                                         _main_entry, _origin, _explicit_inventory)
from retained_audit import AuditIndex, predecessor_inventory, resolve_origin, verify_receipt

NOW = '2026-10-24T07:00:00Z'
LATER = '2026-10-24T08:00:00Z'


class QualificationOriginTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(Path(self.temp.name) / 'state')
        self.original = json.loads((ROOT / 'contracts/market.json').read_text())
        raw = canonical(self.original)
        key = 'contracts/' + digest(self.original) + '.json'
        self.store.write_once(key, raw)
        self.contract_ref = {'key': key, 'sha256': digest(raw), 'bytes': len(raw)}
        self.replays = {}
        self.records = {}
        self.authorities = []
        authority_patch = patch('source_qualification_origin.ACTIVATION_AUTHORITIES', self.authorities)
        authority_patch.start()
        self.addCleanup(authority_patch.stop)
        self.main = self.result(1000)
        self.mock = patch('onboarding.replay_bounded_candidate_diagnostic', side_effect=self.replay)
        self.mock.start()
        self.addCleanup(self.mock.stop)

    def replay(self, original, store, record_ref, plan_ref):
        self.assertEqual(digest(original), digest(self.original))
        record = json.loads(store.get(record_ref))
        result = self.replays[record_ref['sha256']]
        self.assertEqual(record['diagnostic'], result['report'])
        self.assertEqual(result['report']['planReference'], plan_ref)
        store.get(plan_ref)
        return copy.deepcopy(result)

    def result(self, run, *, complete=True, at=NOW, suffix='main', revision=1):
        from onboarding import BOUNDED_CANDIDATE_BINDINGS_V2, BOUNDED_CANDIDATE_BINDINGS_V3, BOUNDED_CANDIDATE_BINDINGS_V4
        rows, bindings = [], []
        sources = {s['id']: s for s in self.original['sources']}
        selected = {1: BOUNDED_CANDIDATE_BINDINGS, 2: BOUNDED_CANDIDATE_BINDINGS_V2,
                    3: BOUNDED_CANDIDATE_BINDINGS_V3, 4: BOUNDED_CANDIDATE_BINDINGS_V4}[revision]
        for i, (sid, url, mode) in enumerate(selected):
            source = sources[sid]
            adapter = _candidate_adapter(source, url, mode)
            body = self.store.put(('Fictional retained layout ' + suffix + sid).encode())
            ob = {'status': 'fetched', 'httpStatus': 200, 'requestedUrl': url,
                  'finalUrl': url, 'fetchedAt': at, 'body': body}
            wrapper = self.store.put({'schemaVersion': 1, 'sourceId': sid,
                'adapterSha256': digest(adapter), 'requestedUrl': url, 'rawObservation': self.store.put(ob)})
            item = url + '/fictional-' + suffix
            parsed = {'items': [item], 'dates': {item: '2026-10-23'}}
            rows.append({'sourceId': sid, 'inventory': parsed,
                'observations': [{'url': url, 'observation': wrapper, 'parser': parsed}],
                'indexComplete': complete, 'terminalProved': complete,
                'reservationDenials': [], 'completionGuardReason': None,
                'primarySample': {'url': item, 'shape': {'canonical': item, 'readableCharacters': 100}}})
            bindings.append({'sourceId': sid, 'indexUrl': url, 'adapter': adapter,
                'originalSourceSha256': digest(source), 'proposedAdapterSha256': digest(adapter)})
        plan = {'sources': bindings, 'parserRevision': revision}
        plan_ref = self.store.put({'fictionalPlan': run})
        plan.update(rawSha256=plan_ref['sha256'], canonicalSha256=plan_ref['sha256'])
        report = {'checkedAt': at, 'operation': 'bounded_candidate_traversal',
            'planReference': plan_ref, 'executionCompleted': True, 'budgetDenied': False,
            'facts': [], 'newFactIds': [], 'semanticAdmission': False,
            'coverageCredit': False, 'sources': rows}
        record = {'contractSha256': digest(self.original), 'diagnostic': report,
                  'githubRunId': str(run), 'githubRunAttempt': 1, 'appRevision': 'a' * 40}
        raw = canonical(record)
        key = f'ci/source-probe-runs/{run}-1.json'
        self.store.write_once(key, raw)
        record_ref = {'key': key, 'sha256': digest(raw), 'bytes': len(raw)}
        self.replays[digest(raw)] = {'plan': plan, 'report': report}
        self.records[run] = record_ref
        return [{'kind': 'bounded_candidate_result', 'originalContract': self.contract_ref,
                 'diagnostic': record_ref, 'plan': plan_ref, 'sourceResultIndex': i,
                 'sourceResultSha256': digest(row)} for i, row in enumerate(rows)]

    def activate(self, *, extra=None, mutate=None, drop_main=False, revision=1):
        from onboarding import BOUNDED_CANDIDATE_BINDINGS_V2, BOUNDED_CANDIDATE_BINDINGS_V3, BOUNDED_CANDIDATE_BINDINGS_V4
        current = copy.deepcopy(self.original)
        changes = []
        selected = {1: BOUNDED_CANDIDATE_BINDINGS, 2: BOUNDED_CANDIDATE_BINDINGS_V2,
                    3: BOUNDED_CANDIDATE_BINDINGS_V3, 4: BOUNDED_CANDIDATE_BINDINGS_V4}[revision]
        for i, (sid, url, mode) in enumerate(selected):
            pos = next(j for j, s in enumerate(current['sources']) if s['id'] == sid)
            old = current['sources'][pos]
            adapter = _candidate_adapter(old, url, mode)
            base = {**adapter, 'registration': 'verified'}
            entries = ([] if drop_main else [self.main[i]]) + (extra or {}).get(sid, [])
            manifest = {'schemaVersion': 1, 'kind': 'qualification_inventory_manifest',
                        'sourceId': sid, 'entries': sorted(entries, key=digest)}
            origin = {'schemaVersion': 1, 'kind': 'bounded_html_qualification',
                **{k:v for k,v in self.main[i].items() if k != 'kind'},
                'originalSourceSha256': digest(old), 'proposedAdapterSha256': digest(adapter),
                'activationBaseSha256': digest(base), 'inventoryManifest': self.store.put(manifest)}
            current['sources'][pos] = {**base, 'qualificationOrigin': origin}
            changes.append({'sourceId': sid, 'sourceIndex': pos, 'originalSourceSha256': digest(old),
                'proposedAdapterSha256': digest(adapter), 'activationBaseSha256': digest(base),
                'qualificationOriginSha256': digest(origin)})
        if mutate:
            mutate(current)
        descriptor = {'schemaVersion': 1, 'kind': 'three_html_source_qualification',
            'originalContract': self.contract_ref, 'activatedContractSha256': digest(current), 'changes': changes}
        transition = self.store.put(descriptor)
        self.store.write_once('source-qualification-transitions/' + digest(current) + '.json', transition)
        diagnostics = []
        for run, ref in self.records.items():
            replay = self.replays[ref['sha256']]
            diagnostics.append({'record': ref, 'originalContract': self.contract_ref,
                'rawPlanSha256': replay['plan']['rawSha256'],
                'canonicalPlanSha256': replay['plan']['canonicalSha256'],
                'githubRunId': str(run), 'githubRunAttempt': 1, 'appRevision': 'a' * 40,
                'externalReceiptSha256': 'b' * 64, 'artifactSha256': 'c' * 64,
                'archiveCommit': 'd' * 40, 'archiveManifestSha256': 'e' * 64})
        self.authorities.append({'activatedContractSha256': digest(current), 'transition': transition,
            'originalContract': self.contract_ref, 'mainDiagnostic': self.main[0]['diagnostic'],
            'mainPlan': self.main[0]['plan'],
            'diagnostics': sorted(diagnostics, key=lambda d: d['record']['sha256'])})
        return current

    def origin(self, contract, sid=None):
        sid = sid or BOUNDED_CANDIDATE_BINDINGS[0][0]
        return qualification_predecessors(contract, sid, self.store, LATER)[0]

    def test_no_origin_is_dormant_and_does_not_read_transition(self):
        with patch.object(self.store, 'read', side_effect=AssertionError('No lookup needed')):
            self.assertEqual(qualification_predecessors(self.original, BOUNDED_CANDIDATE_BINDINGS[0][0], self.store), [])

    def test_self_consistent_archive_cannot_add_external_activation_authority(self):
        contract = self.activate()
        with patch('source_qualification_origin.ACTIVATION_AUTHORITIES', ()), self.assertRaisesRegex(ValueError,
                'NOT_EXTERNALLY_AUTHENTICATED'):
            self.origin(contract)

    def test_listed_record_and_external_app_revision_pins_are_exact(self):
        contract = self.activate()
        self.authorities[-1]['diagnostics'][0]['appRevision'] = 'f' * 40
        with self.assertRaisesRegex(ValueError, 'EXTERNAL_PROVENANCE_DIFFERS'):
            self.origin(contract)
        self.authorities[-1]['diagnostics'] = []
        with self.assertRaisesRegex(ValueError, 'AUTHORITY_SCHEMA_DIFFERS'):
            self.origin(contract)

    def test_closed_three_source_transition_has_inventory_only_authority(self):
        contract = self.activate()
        for sid, _, _ in BOUNDED_CANDIDATE_BINDINGS:
            origin = self.origin(contract, sid)
            resolved = resolve_inventory_origin(origin, contract, sid, self.store, LATER)
            self.assertEqual(resolved['authority'], 'inventory_only')
            self.assertEqual(resolved['completedAt'], NOW)
            self.assertEqual(len(resolved['items']), 1)
            self.assertNotIn('validatedFacts', resolved)
            self.assertNotIn('auditHistory', resolved)
            with self.assertRaisesRegex(ValueError, 'Retained origin schema'):
                resolve_origin(self.store, origin, contract, sid, inventory_only=True)

    def test_earlier_partial_urls_remain_flat_and_original_dates_unchanged(self):
        partial = self.result(999, complete=False, at='2026-10-24T06:00:00Z', suffix='disappeared')
        contract = self.activate(extra={sid: [partial[i]] for i,(sid,_,_) in enumerate(BOUNDED_CANDIDATE_BINDINGS)})
        sid = BOUNDED_CANDIDATE_BINDINGS[0][0]
        resolved = resolve_inventory_origin(self.origin(contract), contract, sid, self.store, LATER)
        self.assertEqual(len(resolved['items']), 2)
        self.assertEqual(sorted(p['observedAt'] for p in resolved['provenance']), ['2026-10-24T06:00:00Z', NOW])
        self.assertTrue(all('inventoryManifest' not in p['origin'] for p in resolved['provenance']))

    def test_omitting_known_partial_rejects_even_with_rehashed_closed_transition(self):
        self.result(999, complete=False, at='2026-10-24T06:00:00Z', suffix='disappeared')
        with self.assertRaisesRegex(ValueError, 'OMITTED_RETAINED_PAGE'):
            self.origin(self.activate())

    def test_incomplete_main_cannot_activate(self):
        self.main = self.result(1001, complete=False, suffix='incomplete')
        with self.assertRaisesRegex(ValueError, 'SOURCE_NOT_READY'):
            self.origin(self.activate())

    def test_future_partial_rejects(self):
        future = self.result(1002, at=LATER, suffix='future')
        sid = BOUNDED_CANDIDATE_BINDINGS[0][0]
        with self.assertRaisesRegex(ValueError, 'FUTURE_PARTIAL'):
            self.origin(self.activate(extra={sid: [future[0]]}))

    def test_future_origin_rejects(self):
        contract = self.activate()
        with self.assertRaisesRegex(ValueError, 'PREDECESSOR_FUTURE'):
            qualification_predecessors(contract, BOUNDED_CANDIDATE_BINDINGS[0][0], self.store, '2026-10-24T06:00:00Z')

    def test_unrelated_policy_and_type_changes_reject(self):
        changes = [lambda c: c['schedule'].__setitem__('maxWorkers', True),
                   lambda c: c['sources'][0]['allowedHosts'].append('extra.invalid'),
                   lambda c: c['suppliers'][0].__setitem__('aliases', ['changed']),
                   lambda c: c['sources'].reverse(),
                   lambda c: c.__setitem__('version', str(c['version']) + '-changed')]
        for change in changes:
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'QUALIFICATION_TRANSITION'):
                self.origin(self.activate(mutate=change))

    def test_duplicate_and_omitted_main_entries_reject(self):
        sid = BOUNDED_CANDIDATE_BINDINGS[0][0]
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_OR_ORDER'):
            self.origin(self.activate(extra={sid: [self.main[0]]}))
        partial = self.result(998, complete=False, suffix='partial')
        with self.assertRaisesRegex(ValueError, 'MAIN_RESULT_OMITTED'):
            self.origin(self.activate(drop_main=True, extra={s: [partial[i]] for i,(s,_,_) in enumerate(BOUNDED_CANDIDATE_BINDINGS)}))

    def test_missing_transition_and_reference_integrity_fail_closed(self):
        contract = self.activate()
        key = 'source-qualification-transitions/' + digest(contract) + '.json'
        (self.store.root / key).unlink()
        with self.assertRaisesRegex(ValueError, 'TRANSITION_REFERENCE_MISSING'):
            self.origin(contract)
        origin = next(s for s in contract['sources'] if 'qualificationOrigin' in s)['qualificationOrigin']
        origin['diagnostic']['bytes'] += 1
        with self.assertRaisesRegex(ValueError, 'integrity verification'):
            _origin(self.store, origin, BOUNDED_CANDIDATE_BINDINGS[0][0])

    def test_index_adds_exact_typed_predecessor_and_inventory_union_preserves_old_urls(self):
        contract = self.activate()
        sid = BOUNDED_CANDIDATE_BINDINGS[0][0]
        origins = AuditIndex(self.store).predecessors(sid, contract, before_time=LATER)
        self.assertEqual(origins, [self.origin(contract)])
        old = ['https://old.invalid/' + str(i) for i in range(9914)]
        normal = {'runId': 'old', 'taskId': 'task', 'attemptId': 'attempt', 'receipt': {}}
        manifest = self.store.put({'sourceId': sid, 'items': old})
        with patch('retained_audit.resolve_origin', return_value={'itemManifest': manifest}):
            union = predecessor_inventory([normal] + origins, contract, sid, self.store)
        self.assertTrue(set(old).issubset(union))
        self.assertEqual(len(union), 9915)
        with self.assertRaisesRegex(ValueError, 'Duplicate qualification'):
            predecessor_inventory(origins * 2, contract, sid, self.store)

    def test_receipt_cannot_omit_typed_origin_even_if_ordinary_inventory_contains_same_urls(self):
        contract = self.activate()
        sid = BOUNDED_CANDIDATE_BINDINGS[0][0]
        source = next(s for s in contract['sources'] if s['id'] == sid)
        origin = self.origin(contract)
        items = resolve_inventory_origin(origin, contract, sid, self.store)['items']
        manifest = self.store.put({'sourceId': sid, 'items': items})
        normal = {'runId': 'old', 'taskId': 'task', 'attemptId': 'old-attempt', 'receipt': {}}
        receipt = {'retainedInventoryManifest': manifest, 'itemManifest': manifest,
                   'retainedInventoryPredecessors': [normal], 'retainedAuditBindings': [],
                   'retainedAuditUnbound': [], 'attemptId': 'new-attempt', 'startedAt': LATER}
        with patch('retained_audit.require_version', return_value=True), \
             patch('retained_audit.resolve_origin', return_value={'itemManifest': manifest}), \
             patch('retained_audit.index_for', return_value=type('Index', (), {'predecessors': lambda *_: [origin]})()), \
             self.assertRaisesRegex(ValueError, 'omitted qualification origin'):
            verify_receipt(receipt, {}, contract, source, LATER, self.store)

    def test_v2_origin_uses_exact_plan_adapter_and_can_retain_v1_partial(self):
        old = copy.deepcopy(self.main)
        self.main = self.result(1003, suffix='v2', revision=2)
        contract = self.activate(revision=2, extra={s: [old[i]] for i,(s,_,_) in enumerate(BOUNDED_CANDIDATE_BINDINGS)})
        sid = BOUNDED_CANDIDATE_BINDINGS[0][0]
        origin = self.origin(contract)
        resolved = resolve_inventory_origin(origin, contract, sid, self.store)
        self.assertEqual(len(resolved['items']), 2)
        self.assertTrue(next(s for s in contract['sources'] if s['id'] == sid)['htmlCompleteness'].endswith('-v2'))
        self.assertEqual([p['origin'] for p in resolved['provenance']], sorted([old[0], self.main[0]], key=digest))

    def test_v3_origin_preserves_both_earlier_revision_inventories(self):
        old = copy.deepcopy(self.main)
        middle = self.result(1004, suffix='v2-partial', revision=2, complete=False)
        self.main = self.result(1005, suffix='v3', revision=3)
        contract = self.activate(revision=3, extra={s: [old[i], middle[i]]
            for i, (s, _, _) in enumerate(BOUNDED_CANDIDATE_BINDINGS)})
        sid = BOUNDED_CANDIDATE_BINDINGS[0][0]
        resolved = resolve_inventory_origin(self.origin(contract), contract, sid, self.store)
        self.assertEqual(len(resolved['items']), 3)
        self.assertTrue(next(s for s in contract['sources'] if s['id'] == sid)['htmlCompleteness'].endswith('-v3'))
        self.assertEqual([p['origin'] for p in resolved['provenance']],
                         sorted([old[0], middle[0], self.main[0]], key=digest))


    def test_v4_origin_preserves_three_original_revision_inventories(self):
        earlier = [copy.deepcopy(self.main),
                   self.result(1004, suffix='v2-partial', revision=2, complete=False),
                   self.result(1005, suffix='v3-partial', revision=3, complete=False)]
        self.main = self.result(1006, suffix='v4', revision=4)
        contract = self.activate(revision=4, extra={sid: [rows[i] for rows in earlier]
            for i, (sid, _, _) in enumerate(BOUNDED_CANDIDATE_BINDINGS)})
        for source in contract['sources']:
            if source['id'] not in {sid for sid, _, _ in BOUNDED_CANDIDATE_BINDINGS}:
                continue
            resolved = resolve_inventory_origin(self.origin(contract, source['id']), contract, source['id'], self.store)
            self.assertEqual(len(resolved['items']), 4)
            expected = '-v3' if source['id'].startswith('ping-identity:') else '-v4'
            self.assertTrue(source['htmlCompleteness'].endswith(expected))

    def test_v4_selected_sparse_adapter_keeps_exact_original_candidate_context(self):
        from onboarding import BOUNDED_CANDIDATE_BINDINGS_V4
        from source_qualification_origin import _sparse_adapter
        sources = {s['id']: s for s in self.original['sources']}
        for sid, url, mode in BOUNDED_CANDIDATE_BINDINGS_V4:
            adapter = _candidate_adapter(sources[sid], url, mode)
            self.assertEqual(_sparse_adapter(self.original, sid, adapter), adapter)
            altered = dict(adapter, maxPages=59)
            with self.assertRaisesRegex(ValueError, 'SPARSE_ADAPTER_CONTEXT_DIFFERS'):
                _sparse_adapter(self.original, sid, altered)


class RealReplayOriginBoundaryTests(unittest.TestCase):
    def setUp(self):
        from test_bounded_candidate_history_replay import BoundedCandidateHistoryReplayTests
        self.fixture = BoundedCandidateHistoryReplayTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)

    def original_reference(self):
        fixture = self.fixture.fixture
        raw = canonical(fixture.policy)
        key = 'contracts/' + digest(fixture.policy) + '.json'
        fixture.store.write_once(key, raw)
        return {'key': key, 'sha256': digest(raw), 'bytes': len(raw)}

    def test_real_partial_replay_survives_live_plan_replacement_but_cannot_activate(self):
        from source_qualification_origin import _bounded_inventory
        fixture = self.fixture.fixture
        report = self.fixture._report()
        run_ref = self.fixture._archived_run(report)
        fixture.path.write_bytes(b'{"disabled":true}')
        row = report['sources'][1]
        source = next(s for s in fixture.policy['sources'] if s['id'] == row['sourceId'])
        sid, url, mode = BOUNDED_CANDIDATE_BINDINGS[1]
        adapter = _candidate_adapter(source, url, mode)
        entry = {'kind': 'bounded_candidate_result', 'originalContract': self.original_reference(),
                 'diagnostic': run_ref, 'plan': report['planReference'], 'sourceResultIndex': 1,
                 'sourceResultSha256': digest(row)}
        items, _, at, _ = _bounded_inventory(fixture.store, entry, fixture.policy, sid)
        self.assertEqual(items, set(row['inventory']['items']))
        self.assertEqual(at, report['checkedAt'])
        origin = {'schemaVersion': 1, 'kind': 'bounded_html_qualification',
            **{k:v for k,v in entry.items() if k != 'kind'}, 'originalSourceSha256': digest(source),
            'proposedAdapterSha256': digest(adapter),
            'activationBaseSha256': digest({**adapter, 'registration': 'verified'}),
            'inventoryManifest': fixture.store.put({'unused': True})}
        with self.assertRaisesRegex(ValueError, 'SOURCE_NOT_READY'):
            _origin(fixture.store, origin, sid)

    def test_process_cache_rechecks_all_original_bytes_without_reparsing_walk(self):
        from onboarding import replay_bounded_candidate_diagnostic
        from source_qualification_origin import _bounded_inventory
        fixture = self.fixture.fixture
        report = self.fixture._report()
        run_ref = self.fixture._archived_run(report)
        sid = BOUNDED_CANDIDATE_BINDINGS[0][0]
        entry = {'kind': 'bounded_candidate_result', 'originalContract': self.original_reference(),
                 'diagnostic': run_ref, 'plan': report['planReference'], 'sourceResultIndex': 0,
                 'sourceResultSha256': digest(report['sources'][0])}
        with patch('onboarding.replay_bounded_candidate_diagnostic', wraps=replay_bounded_candidate_diagnostic) as calls:
            first = _bounded_inventory(fixture.store, entry, fixture.policy, sid)
            self.assertEqual(first, _bounded_inventory(fixture.store, entry, fixture.policy, sid))
            self.assertEqual(calls.call_count, 1)
            page = report['sources'][0]['observations'][0]
            wrapper = json.loads(fixture.store.get(page['observation']))
            observed = json.loads(fixture.store.get(wrapper['rawObservation']))
            (fixture.store.root / observed['body']['key']).write_bytes(b'Altered immutable bytes')
            with self.assertRaisesRegex(ValueError, 'integrity verification'):
                _bounded_inventory(fixture.store, entry, fixture.policy, sid)

    def explicit_page(self, compact=False):
        from test_ping_discovery import complete_layout
        fixture = self.fixture.fixture
        sid, url, _ = BOUNDED_CANDIDATE_BINDINGS[0]
        source = next(s for s in fixture.policy['sources'] if s['id'] == sid)
        proof, observed = fixture._start_proof(source, url, 0)
        record = json.loads(fixture.store.get(proof['record']))
        body = complete_layout(4, last=4)
        if compact:
            body = body.replace(b'/2026-09-', b'/202609-')
        observed['body'] = fixture.store.put(body)
        observed_ref = fixture.store.put(observed)
        for row in record['diagnostic']['qualification']['targets']:
            row['observation'] = observed_ref
        record['githubRunId'] = '8800'
        raw = canonical(record)
        key = 'ci/source-probe-runs/8800-1.json'
        fixture.store.write_once(key, raw)
        proof.update(record={'key': key, 'sha256': digest(raw), 'bytes': len(raw)},
                     body=observed['body'], observation=observed_ref,
                     priorTargetSha256=digest(record['diagnostic']['qualification']['targets'][0]))
        return sid, {'kind': 'explicit_qualification_page', 'originalContract': self.original_reference(), 'proof': proof}

    def test_real_explicit_page_proof_replays_rows_charges_body_and_original_dates(self):
        fixture = self.fixture.fixture
        sid, entry = self.explicit_page()
        items, dates, at, pages = _explicit_inventory(fixture.store, entry, fixture.policy, sid)
        self.assertTrue(items)
        self.assertEqual(at, entry['proof']['fetchedAt'])
        self.assertEqual(pages[0]['body'], entry['proof']['body'])
        self.assertTrue(set(dates).issubset(items))
        for field, value in [('priorTargetIndex', True), ('fetchedAt', LATER),
                             ('priorTargetSha256', 'f' * 64), ('priorPlanRawSha256', 'f' * 64)]:
            bad = copy.deepcopy(entry)
            bad['proof'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                _explicit_inventory(fixture.store, bad, fixture.policy, sid)

    def test_explicit_failure_cannot_be_relabelled_as_inventory_only_success(self):
        fixture = self.fixture.fixture
        sid, entry = self.explicit_page()
        record = json.loads(fixture.store.get(entry['proof']['record']))
        record['githubRunId'] = '8801'
        record['publication'] = {'published': True}
        raw = canonical(record)
        key = 'ci/source-probe-runs/8801-1.json'
        fixture.store.write_once(key, raw)
        entry['proof']['record'] = {'key': key, 'sha256': digest(raw), 'bytes': len(raw)}
        with self.assertRaisesRegex(ValueError, 'NOT_COMPLETED_DIAGNOSTIC'):
            _explicit_inventory(fixture.store, entry, fixture.policy, sid)

    def test_raw_only_explicit_page_can_use_main_v2_card_scope_with_original_dates(self):
        from onboarding import BOUNDED_CANDIDATE_BINDINGS_V2
        fixture = self.fixture.fixture
        sid, entry = self.explicit_page(compact=True)
        with self.assertRaisesRegex(ValueError, 'Unsafe Ping article path'):
            _explicit_inventory(fixture.store, entry, fixture.policy, sid)
        _, url, mode = BOUNDED_CANDIDATE_BINDINGS_V2[0]
        source = next(s for s in fixture.policy['sources'] if s['id'] == sid)
        adapter = _candidate_adapter(source, url, mode)
        items, dates, at, pages = _explicit_inventory(fixture.store, entry, fixture.policy, sid, adapter)
        self.assertEqual(at, entry['proof']['fetchedAt'])
        self.assertTrue(all('/202609-' in item for item in items))
        self.assertEqual(set(dates.values()), {'2026-09-22', '2026-09-23'})
        self.assertEqual(pages[0]['adapterSha256'], digest(adapter))
        adapter['allowedHosts'].append('extra.invalid')
        with self.assertRaisesRegex(ValueError, 'SPARSE_ADAPTER_CONTEXT_DIFFERS'):
            _explicit_inventory(fixture.store, entry, fixture.policy, sid, adapter)

    def test_prior_explicit_pages_use_exact_v4_adapter_without_renewing_original_proof(self):
        from onboarding import BOUNDED_CANDIDATE_BINDINGS_V3, BOUNDED_CANDIDATE_BINDINGS_V4
        from test_html_archive_discovery import delinea_page, sonatype_page
        fixture = self.fixture.fixture
        for index, make_body, page in ((1, delinea_page, 2), (2, sonatype_page, 13)):
            sid, root, mode = BOUNDED_CANDIDATE_BINDINGS_V4[index]
            source = next(s for s in fixture.policy['sources'] if s['id'] == sid)
            proof, observed = fixture._start_proof(source, root, (0, 3, 6)[index])
            body = make_body(page)
            article = (root + '/company/blog/2020/06/02/retained-release' if index == 1
                       else root + '/retained-release-')
            body = body.replace((root + f'/fixture-{page}-0').encode(), article.encode())
            observed['body'] = fixture.store.put(body)
            observation_ref = fixture.store.put(observed)
            record = json.loads(fixture.store.get(proof['record']))
            for row in record['diagnostic']['qualification']['targets']:
                row['observation'] = observation_ref
            record['githubRunId'] = str(8810 + index)
            raw = canonical(record)
            key = f"ci/source-probe-runs/{record['githubRunId']}-1.json"
            fixture.store.write_once(key, raw)
            proof.update(record={'key': key, 'sha256': digest(raw), 'bytes': len(raw)},
                         body=observed['body'], observation=observation_ref,
                         priorTargetSha256=digest(record['diagnostic']['qualification']['targets'][proof['priorTargetIndex']]))
            entry = {'kind': 'explicit_qualification_page',
                     'originalContract': self.original_reference(), 'proof': proof}
            adapter = _candidate_adapter(source, root, mode)
            prior = _candidate_adapter(source, root, BOUNDED_CANDIDATE_BINDINGS_V3[index][2])
            with self.subTest(source=sid):
                with self.assertRaisesRegex(ValueError, 'Unsafe HTML archive article path'):
                    _explicit_inventory(fixture.store, entry, fixture.policy, sid, prior)
                items, dates, at, pages = _explicit_inventory(fixture.store, entry, fixture.policy, sid, adapter)
                self.assertIn(article, items)
                self.assertEqual(at, proof['fetchedAt'])
                self.assertEqual(pages[0]['observation'], observation_ref)
                self.assertEqual(pages[0]['body'], proof['body'])
                self.assertEqual(pages[0]['adapterSha256'], digest(adapter))
                if index == 1:
                    self.assertEqual(dates, {})
                altered = dict(adapter, maxPages=59)
                with self.assertRaisesRegex(ValueError, 'SPARSE_ADAPTER_CONTEXT_DIFFERS'):
                    _explicit_inventory(fixture.store, entry, fixture.policy, sid, altered)


if __name__ == '__main__':
    unittest.main()
