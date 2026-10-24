"""Offline retained-audit integration and adversarial receipt replay."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/tests'))
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from test_pipeline import contract, candidate, FakeAgent, FakeFetcher, QUOTE, URL, T
from contracts import digest, plan_run
from engine import Pipeline
from retained_audit import index_for, replay_binding, resolve_origin, reference, legacy_registry
from storage import LocalStore
from validation import reconcile, verified_partial_document_facts
from snapshot import build_snapshot


class ClockFetcher(FakeFetcher):
    def __init__(self, store, now, pages=None):
        super().__init__(store, pages)
        self.now = now
        self.requests = []

    def fetch(self, source, url, previous=None):
        self.requests.append(url)
        return {**super().fetch(source, url, previous), 'fetchedAt': self.now}


class RetainedAuditTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.store = LocalStore(self.folder.name)
        self.contract = contract()
        self.contract['collection'] = {'mode': 'delta_with_retained_audit', 'currentWindowDays': 30,
                                       'maxDocumentsPerSource': 2, 'maxAuditDocumentsPerSource': 1}
        self.time = T
        self.fetcher = ClockFetcher(self.store, self.time)

    def run_pipeline(self, agent=None):
        self.fetcher.now = self.time
        return Pipeline(self.contract, self.store, self.fetcher, agent=agent, clock=lambda: self.time).run(self.time, force_refresh=True)

    def replay(self, result):
        plan = self.store.read('runs/' + result['runId'] + '/plan.json')
        return reconcile(plan, result['receipts'], self.contract, self.time, self.store)

    def feed(self, urls):
        self.fetcher.pages[self.contract['sources'][0]['url']] = (
            '<rss><channel>' + ''.join('<item><link>' + url + '</link></item>' for url in urls) + '</channel></rss>').encode()

    def test_rebinds_original_seal_without_model_fetch_cursor_or_fact_changes(self):
        first = self.run_pipeline(FakeAgent())
        self.assertTrue(first['complete'])
        original = first['receipts'][0]
        history = copy.deepcopy(self.store.read('heads/audit-' + digest('official') + '.json'))
        self.time = '2026-10-19T17:00:00Z'
        self.fetcher.requests = []
        second = self.run_pipeline()
        self.assertTrue(second['complete'], second['receipts'])
        receipt = second['receipts'][0]
        self.assertEqual(self.fetcher.requests, [self.contract['sources'][0]['url']])
        self.assertEqual(receipt['newFactIds'], [])
        self.assertEqual(receipt['retainedAuditBindings'][0]['origin']['attemptId'], original['attemptId'])
        self.assertEqual(receipt['validatedFacts'], original['validatedFacts'])
        self.assertEqual(self.store.read('heads/audit-' + digest('official') + '.json')['documents'], history['documents'])
        self.time = '2026-10-19T18:00:00Z'
        third = self.run_pipeline()
        self.assertEqual(third['receipts'][0]['retainedAuditBindings'][0]['origin'], receipt['retainedAuditBindings'][0]['origin'])
        self.assertEqual(index_for(self.store).scans, 1)

    def test_completed_documents_from_partial_task_join_full_inventory(self):
        other = 'https://example.invalid/releases/two'
        self.feed([URL, other])
        self.fetcher.pages[other] = self.fetcher.pages[URL].replace(b'</body>', b'<p>Second document.</p></body>')
        first = self.run_pipeline(FakeAgent())
        self.assertFalse(first['complete'])
        self.assertEqual(first['receipts'][0]['pendingDocuments'], 1)
        self.time = '2026-10-19T17:00:00Z'
        second = self.run_pipeline(FakeAgent())
        self.assertTrue(second['complete'], second['receipts'])
        receipt = second['receipts'][0]
        self.assertEqual(len(receipt['documentValidations']), 2)
        self.assertEqual(len(receipt['retainedAuditBindings']), 1)
        self.assertEqual(receipt['newFactIds'], [])
        fact_ids = {json.loads(self.store.get(ref))['factId'] for ref in receipt['validatedFacts']}
        self.assertEqual(len(fact_ids), 1)

    def test_feed_rollover_retains_previous_urls_and_rejects_omitted_predecessor(self):
        self.run_pipeline(FakeAgent())
        other = 'https://example.invalid/releases/two'
        self.feed([other]); self.fetcher.pages[other] = self.fetcher.pages[URL].replace(b'</body>', b'<p>Second document.</p></body>')
        self.time = '2026-10-19T17:00:00Z'
        result = self.run_pipeline(FakeAgent())
        self.assertTrue(result['complete'], result['receipts'])
        receipt = result['receipts'][0]
        full = json.loads(self.store.get(receipt['retainedInventoryManifest']))
        self.assertEqual(full['items'], [URL, other])
        bad = copy.deepcopy(result)
        bad['receipts'][0]['retainedInventoryPredecessors'] = []
        bad['receipts'][0]['retainedInventoryManifest'] = self.store.put({'sourceId': 'official', 'items': [other]})
        with self.assertRaisesRegex(ValueError, 'omitted anchored history'):
            self.replay(bad)

    def test_new_receipt_cannot_downgrade_to_legacy_or_omit_proofs(self):
        result = self.run_pipeline(FakeAgent())
        for remove in ('retainedAuditVersion', 'retainedAuditBindings', 'retainedInventoryManifest'):
            bad = copy.deepcopy(result); del bad['receipts'][0][remove]
            with self.assertRaisesRegex(ValueError, 'requires retained audit proofs|omitted retained'):
                self.replay(bad)

    def test_feed_rollover_partial_release_uses_full_independently_replayed_inventory(self):
        first = self.run_pipeline(FakeAgent())
        retained_fact = first['receipts'][0]['validatedFacts'][0]
        other = 'https://example.invalid/releases/two'
        third = 'https://example.invalid/releases/three'
        self.feed([other, third])
        for url in (other, third):
            self.fetcher.pages[url] = self.fetcher.pages[URL].replace(b'</body>', ('<p>' + url + '</p></body>').encode())
        self.time = '2026-10-19T17:00:00Z'
        result = self.run_pipeline(FakeAgent())
        self.assertFalse(result['complete'])
        plan = self.store.read('runs/' + result['runId'] + '/plan.json')
        refs = verified_partial_document_facts(plan, result, self.contract, self.time, self.store)
        self.assertIn(retained_fact, refs)
        snapshot = build_snapshot(self.contract, plan, result, self.store, self.time)
        self.assertEqual(len(snapshot['events']), 1)
        self.assertEqual(snapshot['coverage']['successfulTasks'], 0)
        bad = copy.deepcopy(result)
        bad['receipts'][0]['retainedAuditBindings'][0]['sourceObservationSha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'observation digest differs'):
            verified_partial_document_facts(plan, bad, self.contract, self.time, self.store)

    def test_tampered_compatibility_cannot_admit_a_new_repaired_attempt(self):
        result = self.run_pipeline(FakeAgent()); receipt = result['receipts'][0]
        path = 'runs/' + result['runId'] + '/retained-audit-compatibility.json'
        record = self.store.read(path)
        record['legacyOrigins'] = [{'runId': result['runId'], 'taskId': receipt['taskId'],
                                   'attemptId': receipt['attemptId'], 'receipt': self.store.put(receipt)}]
        self.store._path(path).write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, 'cannot admit a repaired receipt'):
            self.replay(result)

    def test_dual_strip_cannot_turn_rollover_receipt_into_legacy(self):
        self.run_pipeline(FakeAgent())
        other = 'https://example.invalid/releases/two'
        self.feed([other]); self.fetcher.pages[other] = self.fetcher.pages[URL].replace(b'</body>', b'<p>Second document.</p></body>')
        self.time = '2026-10-19T17:00:00Z'
        result = self.run_pipeline(FakeAgent())
        self.assertTrue(result['complete'])
        bad = copy.deepcopy(result)
        receipt = bad['receipts'][0]
        receipt.update({k: v for k, v in receipt.items() if not k.startswith('retained')})
        for key in list(receipt):
            if key.startswith('retained'): del receipt[key]
        receipt['documentValidations'] = [d for d in receipt['documentValidations'] if d['url'] == other]
        receipt['observationIds'] = [oid for oid in receipt['observationIds']
                                     if self.store.read('observations/' + oid + '.json')['requestedUrl'] != URL]
        self.store._path('runs/' + result['runId'] + '/retained-audit-compatibility.json').unlink()
        with self.assertRaisesRegex(ValueError, 'Unknown legacy-shaped'):
            self.replay(bad)

    def test_incomplete_discovery_cannot_publish_unreviewed_held_claim(self):
        self.fetcher.pages[self.contract['sources'][0]['url']] = 403
        result = self.run_pipeline(FakeAgent())
        self.assertFalse(result['complete'])
        bad = copy.deepcopy(result)
        bad['receipts'][0]['heldClaims'] = [self.store.put({'reason': 'FORGED_UNREVIEWED_REASON'})]
        plan = self.store.read('runs/' + result['runId'] + '/plan.json')
        for action in (lambda: self.replay(bad), lambda: build_snapshot(self.contract, plan, bad, self.store, self.time)):
            with self.assertRaisesRegex(ValueError, 'Incomplete discovery cannot carry'):
                action()

    def test_current_discovery_and_documents_reject_later_failed_transport(self):
        result = self.run_pipeline(FakeAgent())
        for url in (URL, self.contract['sources'][0]['url']):
            with self.subTest(url=url):
                failure = {'sourceId': 'official', 'requestedUrl': url, 'fetchedAt': '2026-10-19T17:00:00Z',
                           'observationId': digest(url), 'status': 'blocked', 'httpStatus': 403}
                self.store.write_once('observations/' + failure['observationId'] + '.json', failure)
                index_for(self.store).register_observation(failure)
                self.time = failure['fetchedAt']
                with self.assertRaisesRegex(ValueError, 'NEWER_TRANSPORT'):
                    self.replay(result)
                plan = self.store.read('runs/' + result['runId'] + '/plan.json')
                with self.assertRaisesRegex(ValueError, 'NEWER_TRANSPORT'):
                    build_snapshot(self.contract, plan, result, self.store, self.time)
                self.store._path('observations/' + failure['observationId'] + '.json').unlink()
                del self.store._retained_audit_index

    def test_equal_time_conflicting_transport_holds_ambiguity(self):
        result = self.run_pipeline(FakeAgent())
        failure = {'sourceId': 'official', 'requestedUrl': URL, 'fetchedAt': self.time,
                   'observationId': 'equal-time-failure', 'status': 'blocked', 'httpStatus': 403}
        self.store.write_once('observations/equal-time-failure.json', failure)
        index_for(self.store).register_observation(failure)
        with self.assertRaisesRegex(ValueError, 'AMBIGUOUS_LATEST_TRANSPORT'):
            self.replay(result)

    def test_equal_time_anchored_predecessor_is_required(self):
        first = self.run_pipeline(FakeAgent())
        original = first['receipts'][0]
        origins = index_for(self.store).predecessors('official', self.contract, 'different-attempt', original['completedAt'])
        self.assertIn(original['attemptId'], [o['attemptId'] for o in origins])

    def test_equal_clock_rollover_cannot_drop_a_known_predecessor(self):
        self.run_pipeline(FakeAgent())
        other = 'https://example.invalid/releases/two'
        self.feed([other])
        self.fetcher.pages[other] = self.fetcher.pages[URL].replace(b'</body>', b'<p>Second document.</p></body>')
        # Conflicting index bytes with indistinguishable transport times have no
        # trustworthy latest order. The actual engine/reconcile path must hold.
        with self.assertRaisesRegex(ValueError, 'AMBIGUOUS_LATEST_TRANSPORT'):
            self.run_pipeline(FakeAgent())

    def test_migration_registry_bytes_are_fixed_in_code(self):
        self.assertGreater(len(legacy_registry()), 0)
        with patch('retained_audit.Path.read_bytes', return_value=b'{}'):
            with self.assertRaisesRegex(ValueError, 'registry hash differs'):
                legacy_registry()

    def test_legacy_coverage_membership_is_supported_but_raw_attempt_alone_is_not(self):
        result = self.run_pipeline(FakeAgent()); original = copy.deepcopy(result['receipts'][0])
        # A separate fixture store represents an archive that predates this schema.
        with tempfile.TemporaryDirectory() as folder:
            legacy = LocalStore(folder)
            for path in self.store.root.rglob('*'):
                if path.is_file() and 'locks' not in path.parts and 'retained-audit-compatibility' not in path.name:
                    key = path.relative_to(self.store.root).as_posix()
                    if key.startswith(('receipt-integrity/', 'runs/')) and '/plan.json' not in key:
                        continue
                    if key.startswith('objects/') and b'"receipts"' in path.read_bytes() and b'"inventorySha256"' in path.read_bytes():
                        continue
                    legacy.write_once(key, path.read_bytes())
            original = {key: value for key, value in original.items() if not key.startswith('retained')}
            path = 'runs/' + result['runId'] + '/attempts/' + original['attemptId'] + '.json'
            legacy.write_once(path, original)
            coverage = {**result, 'receipts': [original]}
            coverage_ref = legacy.put(coverage)
            index = index_for(legacy)
            origin = {'runId': original['runId'], 'taskId': original['taskId'],
                      'attemptId': original['attemptId'], 'coverage': coverage_ref}
            entry = {'receiptSha256': digest(original), 'contractSha256': digest(self.contract),
                     **{k: original[k] for k in ('runId', 'taskId', 'attemptId', 'sourceId', 'supplierId')},
                     'origin': origin}
            fixture_registry = patch('retained_audit.legacy_registry', return_value={digest(original): entry})
            fixture_registry.start(); self.addCleanup(fixture_registry.stop)
            binding = index.binding('official', URL, self.contract, self.time)
            self.assertEqual(binding['origin']['coverage'], coverage_ref)
            self.assertEqual(resolve_origin(legacy, binding['origin'], self.contract, 'official'), original)
            legacy._path(coverage_ref['key']).unlink()
            with self.assertRaises((OSError, ValueError)):
                replay_binding(binding, self.contract, 'official', self.time, legacy, index)

    def test_newer_failed_transport_blocks_old_good_proof_and_success_cursor(self):
        first = self.run_pipeline(FakeAgent())
        head = copy.deepcopy(self.store.read('heads/source-' + digest('official') + '.json'))
        self.time = '2026-10-19T17:00:00Z'
        blocked = {'sourceId': 'official', 'requestedUrl': URL, 'fetchedAt': self.time,
                   'observationId': 'newer-failure', 'status': 'blocked', 'httpStatus': 403}
        self.store.write_once('observations/newer-failure.json', blocked)
        index_for(self.store).register_observation(blocked)
        with self.assertRaisesRegex(ValueError, 'NEWER_TRANSPORT'):
            index_for(self.store).binding('official', URL, self.contract, self.time)
        self.fetcher.pages[URL] = 403
        result = self.run_pipeline()
        self.assertFalse(result['complete'])
        self.assertEqual(self.store.read('heads/source-' + digest('official') + '.json'), head)
        self.assertEqual(len(first['receipts'][0]['newFactIds']), 1)

    def test_fresh_same_body_transport_can_reuse_older_semantics_after_expiry(self):
        first = self.run_pipeline(FakeAgent()); facts = first['receipts'][0]['validatedFacts']
        self.time = '2026-10-20T23:00:01Z'
        with self.assertRaisesRegex(ValueError, 'STALE'):
            index_for(self.store).binding('official', URL, self.contract, self.time)
        agent = FakeAgent()
        result = self.run_pipeline(agent)
        self.assertTrue(result['complete'], result['receipts'])
        self.assertEqual(agent.calls, 0)
        self.assertEqual(result['receipts'][0]['validatedFacts'], facts)
        self.assertEqual(result['receipts'][0]['newFactIds'], [])

    def test_held_accepted_review_with_bad_date_stays_held_on_reuse(self):
        class BadDate(FakeAgent):
            def extract(self, text, supplier):
                return [{**candidate(), 'effectiveDate': None}]
        first = self.run_pipeline(BadDate())
        self.assertTrue(first['complete'], first['receipts'])
        held = first['receipts'][0]['heldClaims']
        self.assertEqual(json.loads(self.store.get(held[0]))['reason'], 'Fact date missing')
        self.time = '2026-10-19T17:00:00Z'
        result = self.run_pipeline()
        self.assertEqual(result['receipts'][0]['heldClaims'], held)
        self.assertEqual(result['receipts'][0]['validatedFacts'], [])

    def test_partial_repaired_receipt_replays_every_disposition(self):
        other = 'https://example.invalid/releases/two'
        self.feed([URL, other]); self.fetcher.pages[other] = self.fetcher.pages[URL]
        result = self.run_pipeline(FakeAgent())
        self.assertFalse(result['complete'])
        bad = copy.deepcopy(result); bad['receipts'][0]['validatedFacts'] = []
        with self.assertRaisesRegex(ValueError, 'missing from original receipt'):
            self.replay(bad)

    def test_rebinding_cannot_become_a_new_original_or_acquire_new_fact_ids(self):
        self.run_pipeline(FakeAgent()); self.time = '2026-10-19T17:00:00Z'
        result = self.run_pipeline(); receipt = result['receipts'][0]
        binding = copy.deepcopy(receipt['retainedAuditBindings'][0])
        binding['origin'] = {'runId': result['runId'], 'taskId': receipt['taskId'],
                             'attemptId': receipt['attemptId'], 'receipt': self.store.put(receipt)}
        with self.assertRaisesRegex(ValueError, 'chain cannot become'):
            replay_binding(binding, self.contract, 'official', self.time, self.store)
        bad = copy.deepcopy(result)
        bad['receipts'][0]['newFactIds'] = [json.loads(self.store.get(receipt['validatedFacts'][0]))['factId']]
        with self.assertRaisesRegex(ValueError, 'incorrectly labelled new'):
            self.replay(bad)

    def test_rehashed_partial_validation_cannot_omit_candidate_dispositions(self):
        other = 'https://example.invalid/releases/two'
        self.feed([URL, other]); self.fetcher.pages[other] = self.fetcher.pages[URL]
        result = self.run_pipeline(FakeAgent()); receipt = result['receipts'][0]
        document = receipt['documentValidations'][0]
        validation = json.loads(self.store.get(document['validation']))
        validation['candidateHashes'] = []
        from documents import article_input
        ob = self.store.read('observations/' + receipt['observationIds'][-1] + '.json')
        view = article_input(self.store.get(ob['body']), ob)
        key = digest({'supplier': 'fixture', 'body': ob['body']['sha256'],
                      'contract': digest(self.contract), 'extractor': view['extractor']})
        self.store._path('document-validation/' + key + '.json').write_text(json.dumps(validation))
        bad = copy.deepcopy(result)
        bad['receipts'][0]['documentValidations'][0]['validation'] = self.store.put(validation)
        with self.assertRaisesRegex(ValueError, 'candidate/disposition inventory differs'):
            self.replay(bad)

    def test_fresh_304_reuses_historical_semantics_without_rewriting_original_time(self):
        result = self.run_pipeline(FakeAgent())
        original = self.store.read('observations/' + result['receipts'][0]['observationIds'][-1] + '.json')
        original_bytes = self.store._path('observations/' + original['observationId'] + '.json').read_bytes()
        self.time = '2026-10-20T23:00:01Z'
        fresh = {**original, 'status': 'not_modified', 'httpStatus': 304, 'observationId': 'fresh-304',
                 'fetchedAt': self.time, 'reusesObservationId': original['observationId']}
        self.store.write_once('observations/fresh-304.json', fresh)
        index_for(self.store).register_observation(fresh)
        binding = index_for(self.store).binding('official', URL, self.contract, self.time)
        self.assertEqual(binding['sourceObservationId'], original['observationId'])
        self.assertEqual(binding['transportObservationId'], 'fresh-304')
        replay_binding(binding, self.contract, 'official', self.time, self.store)
        self.assertEqual(self.store._path('observations/' + original['observationId'] + '.json').read_bytes(), original_bytes)
        self.store._path('observations/fresh-304.json').write_text(json.dumps({**fresh, 'reusesObservationId': 'missing'}))
        with self.assertRaises(ValueError):
            replay_binding(binding, self.contract, 'official', self.time, self.store)

    def test_transport_boundary_and_changed_body_cannot_fall_back_to_old_review(self):
        result = self.run_pipeline(FakeAgent())
        index = index_for(self.store)
        index.binding('official', URL, self.contract, '2026-10-20T22:00:00Z')
        with self.assertRaisesRegex(ValueError, 'STALE'):
            index.binding('official', URL, self.contract, '2026-10-20T22:00:01Z')
        original = self.store.read('observations/' + result['receipts'][0]['observationIds'][-1] + '.json')
        changed = {**original, 'observationId': 'changed-body', 'fetchedAt': '2026-10-19T17:00:00Z',
                   'body': self.store.put(b'<html><body>A different unreviewed business statement.</body></html>')}
        self.store.write_once('observations/changed-body.json', changed)
        index.register_observation(changed)
        with self.assertRaisesRegex(ValueError, 'NEWER_TRANSPORT'):
            index.binding('official', URL, self.contract, '2026-10-19T17:00:00Z')

    def test_policy_category_family_and_original_observation_tampering_fail(self):
        self.run_pipeline(FakeAgent()); index = index_for(self.store)
        for mutate in (lambda c: c['suppliers'][0]['requiredCategories'].append('leadership'),
                       lambda c: c['sources'][0].update(family='release_distribution')):
            changed = copy.deepcopy(self.contract); mutate(changed)
            with self.assertRaisesRegex(ValueError, 'policy differs'):
                index.binding('official', URL, changed, self.time)
        binding = index.binding('official', URL, self.contract, self.time)
        binding['sourceObservationSha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'observation digest differs'):
            replay_binding(binding, self.contract, 'official', self.time, self.store)

    def test_empty_and_shared_publisher_exclusions_replay_without_new_reviews(self):
        quiet = ('<html><body>Fixture Vendor publishes its community calendar and office information. '
                 'Visitors can find locations, meeting hours and public contact details on this page.</body></html>').encode()
        self.fetcher.pages[URL] = quiet
        self.run_pipeline(FakeAgent(empty=True)); self.time = '2026-10-19T17:00:00Z'
        self.assertTrue(self.run_pipeline()['complete'])
        with tempfile.TemporaryDirectory() as folder:
            store = LocalStore(folder)
            changed = copy.deepcopy(self.contract)
            changed['sources'][0]['family'] = 'investor_acquirer'
            changed['suppliers'][0]['requiredFamilies'] = ['investor_acquirer']
            pages = dict(self.fetcher.pages); pages[URL] = quiet.replace(b'Fixture Vendor', b'Unrelated Organization')
            fetcher = ClockFetcher(store, T, pages)
            first = Pipeline(changed, store, fetcher, clock=lambda: T).run(T)
            self.assertTrue(first['complete'])
            validation = json.loads(store.get(first['receipts'][0]['documentValidations'][0]['validation']))
            self.assertEqual(validation['exclusionRule'], 'no-registered-entity-mention-v1')
            self.assertTrue(index_for(store).binding('official', URL, changed, T))


if __name__ == '__main__':
    unittest.main()
