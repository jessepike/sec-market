"""Independent intake, processing and historical proof under D-112."""
import copy
import json
import unittest
import test_retained_audit_rebinding as fixtures

from contracts import digest, plan_run
from retained_audit import index_for, replay_binding
from separation import MODE, MEASURE, bridge
from snapshot import build_snapshot, collector_continuity
from validation import reconcile, verified_partial_document_facts


class SeparateFreshnessHistoryTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.RetainedAuditTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)

    def migrate(self):
        self.f.contract['version'] = 'test-v2'
        self.f.contract['collection']['mode'] = MODE
        self.f.time = '2026-10-21T16:00:00Z'

    def replay(self, result):
        return self.f.replay(result)

    def test_complete_fresh_intake_keeps_unknown_unreviewed_work_visible(self):
        self.migrate()
        other = 'https://example.invalid/releases/two'
        self.f.feed([fixtures.URL, other])
        self.f.fetcher.pages[other] = self.f.fetcher.pages[fixtures.URL] + b'<!--other-->'
        result = self.f.run_pipeline(fixtures.FakeAgent())
        self.assertEqual(result['schemaVersion'], 2)
        self.assertEqual(result['measure'], MEASURE)
        self.assertTrue(result['intake']['complete'])
        self.assertFalse(result['processing']['complete'])
        self.assertFalse(result['historicalReview']['complete'])
        self.assertEqual(result['processing']['inventoryDocuments'], 2)
        self.assertEqual(result['processing']['pendingDocuments'], 1)
        self.assertEqual(result['processing']['unknownDateDocuments'], 2)
        self.assertEqual(result['tasks'][0]['intakeOutcome'], 'checked')
        self.assertEqual(result['tasks'][0]['processingOutcome'], 'not_checked')
        plan = self.f.store.read('runs/' + result['runId'] + '/plan.json')
        snapshot = build_snapshot(self.f.contract, plan, result, self.f.store, self.f.time)
        self.assertEqual(snapshot['coverage']['sources'][0]['outcome'], 'checked')
        self.assertEqual(len(snapshot['events']), 1)

    def test_original_semantics_replay_after_30_hours_with_original_times_and_policy(self):
        original = self.f.run_pipeline(fixtures.FakeAgent())
        old_contract = copy.deepcopy(self.f.contract)
        facts = original['receipts'][0]['validatedFacts']
        before = {oid: copy.deepcopy(self.f.store.read('observations/' + oid + '.json'))
                  for oid in original['receipts'][0]['observationIds']}
        self.migrate(); self.f.fetcher.requests = []
        result = self.f.run_pipeline()
        receipt = result['receipts'][0]
        self.assertTrue(result['intake']['complete'])
        self.assertTrue(result['historicalReview']['complete'])
        self.assertEqual(receipt['validatedFacts'], facts)
        self.assertEqual(receipt['newFactIds'], [])
        binding = receipt['retainedAuditBindings'][0]
        self.assertEqual(binding['policyBridge'], bridge(old_contract, self.f.contract, 'official'))
        self.assertEqual(self.f.fetcher.requests, [self.f.contract['sources'][0]['url']])
        for oid, value in before.items():
            self.assertEqual(self.f.store.read('observations/' + oid + '.json'), value)
        plan = self.f.store.read('runs/' + result['runId'] + '/plan.json')
        snapshot = build_snapshot(self.f.contract, plan, result, self.f.store, self.f.time)
        self.assertGreater(snapshot['coverage']['validUntil'], self.f.time)

    def test_blocked_intake_preserves_original_full_history(self):
        self.f.run_pipeline(fixtures.FakeAgent())
        self.migrate()
        self.f.fetcher.pages[self.f.contract['sources'][0]['url']] = 403
        result = self.f.run_pipeline()
        self.assertFalse(result['intake']['complete'])
        self.assertEqual(result['successfulTasks'], 0)
        self.assertTrue(result['historicalReview']['complete'])
        self.assertEqual(result['historicalReview']['inventoryDocuments'], 1)

    def test_newer_article_failure_is_visible_while_discovery_intake_passes(self):
        self.f.run_pipeline(fixtures.FakeAgent()); self.migrate()
        failure = {'sourceId': 'official', 'requestedUrl': fixtures.URL, 'fetchedAt': '2026-10-20T16:00:00Z',
                   'observationId': 'newer-bad', 'status': 'blocked', 'httpStatus': 403}
        self.f.store.write_once('observations/newer-bad.json', failure)
        index_for(self.f.store).register_observation(failure)
        self.f.fetcher.pages[fixtures.URL] = 403
        result = self.f.run_pipeline()
        self.assertTrue(result['intake']['complete'])
        self.assertEqual(result['processing']['changedDocuments'], 1)
        self.assertEqual(result['processing']['pendingDocuments'], 1)
        self.assertEqual(result['historicalReview']['reviewedDocuments'], 1)
        self.assertFalse(result['processing']['complete'])

    def test_changed_primary_body_needs_new_review_without_losing_old_proof(self):
        self.f.run_pipeline(fixtures.FakeAgent()); self.migrate()
        old = index_for(self.f.store).latest_observation('official', fixtures.URL)
        changed = {**old, 'body': self.f.store.put(b'<html><body>Fixture Vendor changed its funding disclosure.</body></html>'),
                   'fetchedAt': '2026-10-20T16:00:00Z', 'observationId': 'newer-changed'}
        self.f.store.write_once('observations/newer-changed.json', changed)
        index_for(self.f.store).register_observation(changed)
        self.f.fetcher.pages[fixtures.URL] = self.f.store.get(changed['body'])
        result = self.f.run_pipeline()
        self.assertTrue(result['intake']['complete'])
        self.assertEqual(result['processing']['changedDocuments'], 1)
        self.assertEqual(result['processing']['pendingDocuments'], 1)
        self.assertEqual(result['historicalReview']['reviewedDocuments'], 1)

    def test_semantic_context_source_alias_and_review_policy_changes_hold(self):
        self.f.run_pipeline(fixtures.FakeAgent()); self.migrate()
        baseline = copy.deepcopy(self.f.contract)
        for mutate in (lambda c: c['suppliers'][0]['aliases'].append('Different Entity'),
                       lambda c: c['sources'][0].update(family='investor_acquirer'),
                       lambda c: c['model'].update(maxDocumentChars=20000),
                       lambda c: c['suppliers'][0]['requiredCategories'].append('revenue')):
            current = copy.deepcopy(baseline); mutate(current)
            with self.assertRaisesRegex(ValueError, 'semantic policy/source/supplier'):
                index_for(self.f.store).binding('official', fixtures.URL, current, self.f.time)

    def test_unrelated_supplier_registration_does_not_reinterpret_subject_policy(self):
        self.f.run_pipeline(fixtures.FakeAgent()); old = copy.deepcopy(self.f.contract); self.migrate()
        self.f.contract['suppliers'].append({'id': 'other', 'name': 'Other', 'aliases': []})
        self.f.contract['sources'].append({'id': 'other:source', 'supplierId': 'other', 'registration': 'candidate'})
        binding = index_for(self.f.store).binding('official', fixtures.URL, self.f.contract, self.f.time)
        self.assertEqual(binding['policyBridge'], bridge(old, self.f.contract, 'official'))

    def test_bridge_and_partition_tampering_rejected(self):
        self.f.run_pipeline(fixtures.FakeAgent()); self.migrate()
        result = self.f.run_pipeline()
        bad = copy.deepcopy(result)
        bad['receipts'][0]['retainedAuditBindings'][0]['policyBridge']['semanticContextSha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'bridge differs'):
            self.replay(bad)
        bad = copy.deepcopy(result)
        partition = json.loads(self.f.store.get(bad['receipts'][0]['processingManifest']))
        partition['processingReviewed'] = []
        bad['receipts'][0]['processingManifest'] = self.f.store.put(partition)
        with self.assertRaisesRegex(ValueError, 'partition proof differs'):
            self.replay(bad)

    def test_new_version_cannot_strip_proofs_and_become_legacy(self):
        self.migrate(); result = self.f.run_pipeline(fixtures.FakeAgent())
        bad = copy.deepcopy(result)
        for key in list(bad['receipts'][0]):
            if key.startswith('retained'):
                del bad['receipts'][0][key]
        self.f.store._path('runs/' + result['runId'] + '/retained-audit-compatibility.json').unlink()
        with self.assertRaisesRegex(ValueError, 'omitted versioned'):
            self.replay(bad)

    def test_feed_rollover_keeps_full_partition_and_original_fact(self):
        self.f.run_pipeline(fixtures.FakeAgent()); self.migrate()
        other = 'https://example.invalid/releases/two'
        self.f.feed([other]); self.f.fetcher.pages[other] = self.f.fetcher.pages[fixtures.URL] + b'<!--other-->'
        result = self.f.run_pipeline()
        self.assertTrue(result['intake']['complete'])
        self.assertEqual(result['historicalReview']['inventoryDocuments'], 2)
        self.assertEqual(result['historicalReview']['reviewedDocuments'], 1)
        self.assertEqual(result['processing']['pendingDocuments'], 1)
        bad = copy.deepcopy(result); bad['receipts'][0]['retainedInventoryPredecessors'] = []
        with self.assertRaisesRegex(ValueError, 'omitted anchored history'):
            self.replay(bad)

    def test_legacy_reports_keep_old_measure_and_freshness(self):
        original = self.f.run_pipeline(fixtures.FakeAgent())
        self.assertEqual(original['schemaVersion'], 1)
        self.assertNotIn('intake', original)
        self.f.time = '2026-10-21T16:00:00Z'
        with self.assertRaisesRegex(ValueError, 'stale|STALE'):
            self.replay(original)

    def test_future_transport_cannot_clear_evidenced_index_change(self):
        self.f.contract['sources'][0].update(kind='sitemap', url='https://example.invalid/sitemap.xml')
        feed = self.f.contract['sources'][0]['url']
        def sitemap(day):
            return ('<urlset><url><loc>' + fixtures.URL + '</loc><lastmod>' + day + '</lastmod></url></urlset>').encode()
        self.f.fetcher.pages[feed] = sitemap('2026-10-19')
        self.f.run_pipeline(fixtures.FakeAgent()); self.migrate()
        self.f.fetcher.pages[feed] = sitemap('2026-10-21')
        original = index_for(self.f.store).latest_observation('official', fixtures.URL)
        future = {**original, 'observationId': 'future-article', 'fetchedAt': '2030-01-01T00:00:00Z'}
        self.f.store.write_once('observations/future-article.json', future)
        index_for(self.f.store).register_observation(future)
        result = self.f.run_pipeline()
        self.assertTrue(result['intake']['complete'])
        self.assertFalse(result['processing']['complete'])
        self.assertEqual(result['processing']['changedDocuments'], 1)
        self.assertEqual(result['historicalReview']['reviewedDocuments'], 1)

    def test_reviewed_held_claims_do_not_make_processing_complete(self):
        class HeldAgent(fixtures.FakeAgent):
            def review(self, text, candidate, observed, policy):
                value = super().review(text, candidate, observed, policy)
                value['checks']['entity'] = 'fail'
                return value
        self.migrate(); result = self.f.run_pipeline(HeldAgent())
        self.assertTrue(result['intake']['complete'])
        self.assertTrue(result['historicalReview']['complete'])
        self.assertEqual(result['processing']['heldDocuments'], 1)
        self.assertEqual(result['processing']['reviewedDocuments'], 1)
        self.assertFalse(result['processing']['complete'])

    def test_old_index_body_never_supplies_new_intake_freshness(self):
        self.f.run_pipeline(fixtures.FakeAgent()); self.migrate()
        original_fetch = self.f.fetcher.fetch
        def stale(source, url, previous=None):
            return {**original_fetch(source, url, previous), 'fetchedAt': fixtures.T}
        self.f.fetcher.fetch = stale
        result = self.f.run_pipeline()
        self.assertFalse(result['intake']['complete'])
        self.assertTrue(result['historicalReview']['complete'])

    def test_existing_citation_intake_remains_link_and_body_integrity_only(self):
        self.f.contract['sources'][0].update(kind='citation', family='citation_integrity', url=fixtures.URL)
        self.f.contract['suppliers'][0]['requiredFamilies'] = ['citation_integrity']
        self.migrate()
        agent = fixtures.FakeAgent()
        result = self.f.run_pipeline(agent)
        self.assertTrue(result['intake']['complete'])
        self.assertEqual(agent.calls, 0)
        self.assertEqual(result['receipts'][0]['validatedFacts'], [])
        self.assertEqual(result['processing']['inventoryDocuments'], 0)
        self.assertNotIn('retainedFactBindings', result['receipts'][0])

    def test_current_same_body_check_resolves_work_without_erasing_change_classification(self):
        self.f.contract['sources'][0].update(kind='sitemap', url='https://example.invalid/sitemap.xml')
        feed = self.f.contract['sources'][0]['url']
        def sitemap(day):
            return ('<urlset><url><loc>' + fixtures.URL + '</loc><lastmod>' + day + '</lastmod></url></urlset>').encode()
        self.f.fetcher.pages[feed] = sitemap('2026-10-19')
        self.f.run_pipeline(fixtures.FakeAgent()); self.migrate()
        self.f.fetcher.pages[feed] = sitemap('2026-10-21')
        agent = fixtures.FakeAgent()
        result = self.f.run_pipeline(agent)
        self.assertTrue(result['processing']['complete'])
        self.assertEqual(result['processing']['changedDocuments'], 1)
        self.assertEqual(agent.calls, 0)
        partitions = json.loads(self.f.store.get(result['receipts'][0]['processingManifest']))
        self.assertEqual(partitions['changed'], [fixtures.URL])
        self.assertEqual(partitions['revalidationRequired'], [])

    def sitemap_signature(self, signature, include=True):
        self.f.contract['sources'][0].update(kind='sitemap', url='https://example.invalid/sitemap.xml')
        self.f.fetcher.pages[self.f.contract['sources'][0]['url']] = (
            '<urlset>' + ('<url><loc>' + fixtures.URL + '</loc><lastmod>' + signature + '</lastmod></url>'
                         if include else '') + '</urlset>').encode()

    def exhausted_agent(self):
        self.f.store.compare_and_swap('budget-' + self.f.time[:10], None,
                                      {'calls': self.f.contract['model']['maxCallsPerRun']})
        agent = fixtures.FakeAgent(); agent.queued_work = True
        return agent

    def test_sealed_primary_check_clears_same_signature_on_later_days_without_capacity(self):
        self.sitemap_signature('2026-10-19')
        original = self.f.run_pipeline(fixtures.FakeAgent())
        old_observations = {oid: copy.deepcopy(self.f.store.read('observations/' + oid + '.json'))
                            for oid in original['receipts'][0]['observationIds']}
        self.migrate(); self.sitemap_signature('2026-10-21')
        checked = self.f.run_pipeline(fixtures.FakeAgent())
        self.assertTrue(checked['processing']['complete'])
        self.f.time = '2026-10-22T16:00:00Z'; self.f.fetcher.requests = []
        quiet = self.f.run_pipeline(self.exhausted_agent())
        self.assertEqual(self.f.fetcher.requests, [self.f.contract['sources'][0]['url']])
        self.assertTrue(quiet['processing']['complete'])
        cursor = quiet['receipts'][0]['revalidationCursors'][0]
        self.assertEqual(cursor['origin']['attemptId'], checked['receipts'][0]['attemptId'])
        self.assertEqual(cursor['semanticOrigin'], checked['receipts'][0]['retainedAuditBindings'][0]['origin'])
        for field in ('revalidationCursors', 'indexSignatureBindings'):
            bad = copy.deepcopy(quiet); bad['receipts'][0].pop(field)
            with self.assertRaisesRegex(ValueError, 'cursor proof|signature proof'):
                self.replay(bad)
        bad = copy.deepcopy(quiet); bad['receipts'][0]['revalidationCursors'][0]['signature'] = 'forged'
        with self.assertRaisesRegex(ValueError, 'cursor proof'):
            self.replay(bad)
        self.f.time = '2026-10-23T16:00:00Z'; self.f.fetcher.requests = []
        next_quiet = self.f.run_pipeline(self.exhausted_agent())
        self.assertEqual(next_quiet['receipts'][0]['revalidationCursors'], quiet['receipts'][0]['revalidationCursors'])
        self.assertEqual(self.f.fetcher.requests, [self.f.contract['sources'][0]['url']])
        self.assertEqual(next_quiet['receipts'][0]['newFactIds'], [])
        for oid, ob in old_observations.items():
            self.assertEqual(self.f.store.read('observations/' + oid + '.json'), ob)
        failed = {'sourceId': 'official', 'requestedUrl': fixtures.URL, 'fetchedAt': '2026-10-23T17:00:00Z',
                  'observationId': 'failure-after-sealed-cursor', 'status': 'blocked', 'httpStatus': 403}
        self.f.store.write_once('observations/' + failed['observationId'] + '.json', failed)
        index_for(self.f.store).register_observation(failed)
        self.f.time = '2026-10-24T16:00:00Z'
        held = self.f.run_pipeline(self.exhausted_agent())
        self.assertFalse(held['processing']['complete'])
        self.assertEqual(held['processing']['pendingDocuments'], 1)
        self.assertEqual(held['receipts'][0]['revalidationCursors'], [])

    def test_unresolved_signature_survives_blocked_intake_and_complete_feed_rollover(self):
        for blocked in (True, False):
            with self.subTest(blocked=blocked):
                if not blocked:
                    self.f.doCleanups(); self.setUp()
                self.sitemap_signature('2026-10-19'); self.f.run_pipeline(fixtures.FakeAgent())
                self.migrate(); self.sitemap_signature('2026-10-21')
                pending = self.f.run_pipeline(self.exhausted_agent())
                self.assertEqual(pending['processing']['pendingDocuments'], 1)
                self.f.time = '2026-10-22T16:00:00Z'
                if blocked:
                    self.f.fetcher.pages[self.f.contract['sources'][0]['url']] = 403
                else:
                    self.sitemap_signature('', include=False)
                held = self.f.run_pipeline(self.exhausted_agent())
                self.assertFalse(held['processing']['complete'])
                self.assertEqual(held['processing']['pendingDocuments'], 1)
                self.assertEqual(held['processing']['changedDocuments'], 1)
                self.assertTrue(held['historicalReview']['complete'])
                signature = held['receipts'][0]['indexSignatureBindings'][0]
                self.assertEqual(signature['origin']['attemptId'], pending['receipts'][0]['attemptId'])
                bad = copy.deepcopy(held); bad['receipts'][0]['indexSignatureBindings'] = []
                with self.assertRaisesRegex(ValueError, 'signature proof'):
                    self.replay(bad)

    def test_partial_index_signature_replays_failed_terminal_without_granting_intake(self):
        self.sitemap_signature('2026-10-19')
        root = self.f.contract['sources'][0]['url']
        child, failed = 'https://example.invalid/aaa.xml', 'https://example.invalid/zzz.xml'
        self.f.fetcher.pages[child] = self.f.fetcher.pages[root]
        self.f.fetcher.pages[root] = ('<sitemapindex><sitemap><loc>' + child + '</loc></sitemap></sitemapindex>').encode()
        self.f.run_pipeline(fixtures.FakeAgent()); self.migrate()
        self.f.fetcher.pages[child] = self.f.fetcher.pages[child].replace(b'2026-10-19', b'2026-10-21')
        self.f.fetcher.pages[root] = ('<sitemapindex><sitemap><loc>' + child + '</loc></sitemap><sitemap><loc>' +
                                    failed + '</loc></sitemap></sitemapindex>').encode()
        self.f.fetcher.pages[failed] = 403
        partial = self.f.run_pipeline(self.exhausted_agent())
        self.assertFalse(partial['intake']['complete'])
        self.assertEqual(partial['processing']['pendingDocuments'], 1)
        self.f.time = '2026-10-22T16:00:00Z'; self.f.fetcher.pages[root] = 403
        held = self.f.run_pipeline(self.exhausted_agent())
        self.assertFalse(held['intake']['complete'])
        self.assertFalse(held['processing']['complete'])
        self.assertEqual(held['processing']['changedDocuments'], 1)
        self.assertEqual(held['receipts'][0]['indexSignatureBindings'][0]['origin']['attemptId'],
                         partial['receipts'][0]['attemptId'])

    def test_primary_check_after_rollover_creates_flat_cursor_for_carried_signature(self):
        self.sitemap_signature('2026-10-19'); self.f.run_pipeline(fixtures.FakeAgent())
        self.migrate(); self.sitemap_signature('2026-10-21')
        pending = self.f.run_pipeline(self.exhausted_agent())
        self.assertEqual(pending['processing']['pendingDocuments'], 1)
        self.f.time = '2026-10-22T16:00:00Z'; self.sitemap_signature('', include=False)
        checked = self.f.run_pipeline(fixtures.FakeAgent())
        self.assertTrue(checked['processing']['complete'])
        self.assertEqual(checked['receipts'][0]['indexSignatureBindings'][0]['signature'], '2026-10-21')
        self.f.time = '2026-10-23T16:00:00Z'; self.f.fetcher.requests = []
        quiet = self.f.run_pipeline(self.exhausted_agent())
        self.assertTrue(quiet['processing']['complete'])
        self.assertEqual(self.f.fetcher.requests, [self.f.contract['sources'][0]['url']])
        cursor = quiet['receipts'][0]['revalidationCursors'][0]
        self.assertEqual(cursor['origin']['attemptId'], checked['receipts'][0]['attemptId'])
        self.assertEqual(cursor['indexSignatureBinding']['origin']['attemptId'], pending['receipts'][0]['attemptId'])
        self.assertEqual(cursor['signature'], '2026-10-21')
        self.f.time = '2026-10-24T16:00:00Z'
        next_quiet = self.f.run_pipeline(self.exhausted_agent())
        self.assertTrue(next_quiet['processing']['complete'])
        self.assertEqual(next_quiet['receipts'][0]['revalidationCursors'], quiet['receipts'][0]['revalidationCursors'])

    def test_fresh_changed_primary_review_after_rollover_preserves_carried_signature(self):
        self.sitemap_signature('2026-10-19'); self.f.run_pipeline(fixtures.FakeAgent())
        self.migrate(); self.sitemap_signature('2026-10-21')
        pending = self.f.run_pipeline(self.exhausted_agent())
        self.assertEqual(pending['processing']['pendingDocuments'], 1)
        self.f.time = '2026-10-22T16:00:00Z'; self.sitemap_signature('', include=False)
        self.f.fetcher.pages[fixtures.URL] += b'<!-- actual changed input -->'
        agent = fixtures.FakeAgent(); checked = self.f.run_pipeline(agent)
        self.assertEqual(agent.calls, 2)
        self.assertTrue(checked['processing']['complete'])
        self.assertEqual(checked['receipts'][0]['retainedAuditBindings'], [])
        self.assertEqual(checked['receipts'][0]['indexSignatureBindings'][0]['signature'], '2026-10-21')
        self.f.time = '2026-10-23T16:00:00Z'; self.f.fetcher.requests = []
        quiet = self.f.run_pipeline(self.exhausted_agent())
        self.assertTrue(quiet['processing']['complete'])
        self.assertEqual(self.f.fetcher.requests, [self.f.contract['sources'][0]['url']])
        self.assertEqual(quiet['receipts'][0]['retainedAuditBindings'][0]['origin']['attemptId'],
                         checked['receipts'][0]['attemptId'])
        self.assertEqual(quiet['receipts'][0]['newFactIds'], [])

    def snapshot(self, result, previous=None, continuity=None):
        plan = self.f.store.read('runs/' + result['runId'] + '/plan.json')
        return build_snapshot(self.f.contract, plan, result, self.f.store, self.f.time,
                              previous=previous, continuity=continuity)

    def test_known_transport_change_uses_current_lane_ahead_of_unrelated_audits(self):
        self.f.run_pipeline(fixtures.FakeAgent()); self.migrate()
        audits = ['https://example.invalid/releases/aaa', 'https://example.invalid/releases/aab']
        self.f.feed([fixtures.URL, *audits])
        for i, url in enumerate(audits):
            self.f.fetcher.pages[url] = self.f.fetcher.pages[fixtures.URL] + ('<!--audit' + str(i) + '-->').encode()
        changed = self.f.fetcher.pages[fixtures.URL] + b'<!-- changed -->'
        old = index_for(self.f.store).latest_observation('official', fixtures.URL)
        observed = {**old, 'body': self.f.store.put(changed), 'observationId': 'known-transport-change',
                    'fetchedAt': '2026-10-20T16:00:00Z'}
        self.f.store.write_once('observations/known-transport-change.json', observed)
        index_for(self.f.store).register_observation(observed)
        self.f.fetcher.pages[fixtures.URL] = changed
        # Removing a mutable scheduling hint cannot suppress known changed work.
        key = 'heads/audit-' + digest('official') + '.json'
        head = self.f.store.read(key); head['documents'] = {}
        self.f.store._path(key).write_text(json.dumps(head))
        result = self.f.run_pipeline(fixtures.FakeAgent())
        self.assertIn(fixtures.URL, result['receipts'][0]['selectedDocumentUrls'])
        self.assertEqual(len(result['receipts'][0]['selectedDocumentUrls']), 2)
        self.assertEqual(len(set(result['receipts'][0]['selectedDocumentUrls']) & set(audits)), 1)
        partitions = json.loads(self.f.store.get(result['receipts'][0]['processingManifest']))
        self.assertIn(fixtures.URL, partitions['processingReviewed'])
        self.assertNotIn(fixtures.URL, partitions['revalidationRequired'])

    def test_typed_revalidation_marker_continuity_and_exact_resolution_keep_raw_hold(self):
        class HeldAgent(fixtures.FakeAgent):
            def review(self, text, candidate, observed, policy):
                value = super().review(text, candidate, observed, policy)
                value['checks']['entity'] = 'fail'
                return value
        first = self.f.run_pipeline(HeldAgent())
        old_hold = first['receipts'][0]['heldClaims'][0]['sha256']
        previous = self.snapshot(first)
        self.migrate()
        self.f.fetcher.pages[fixtures.URL] += b'<!-- changed primary -->'
        old = index_for(self.f.store).latest_observation('official', fixtures.URL)
        changed = {**old, 'body': self.f.store.put(self.f.fetcher.pages[fixtures.URL]),
                   'observationId': 'known-changed-marker', 'fetchedAt': '2026-10-20T16:00:00Z'}
        self.f.store.write_once('observations/known-changed-marker.json', changed)
        index_for(self.f.store).register_observation(changed)
        pending = self.f.run_pipeline()
        pending_snapshot = self.snapshot(pending, previous)
        markers = [q for q in pending_snapshot['reviewQueue'] if q.get('kind') == 'source_document_revalidation']
        self.assertEqual(len(markers), 1)
        continuity = collector_continuity(pending_snapshot, self.f.contract, pending, self.f.store)
        self.f.time = '2026-10-22T16:00:00Z'
        reviewed = self.f.run_pipeline(fixtures.FakeAgent())
        final = self.snapshot(reviewed, pending_snapshot, continuity)
        self.assertTrue(reviewed['processing']['complete'])
        self.assertFalse(any(q.get('kind') == 'source_document_revalidation' for q in final['reviewQueue']))
        self.assertTrue(any(q.get('receiptSha256') == old_hold for q in final['reviewQueue']))
        self.assertEqual(len(final['documentReviewResolutions']), 1)
        self.assertEqual(final['documentReviewResolutions'][0]['marker'], markers[0])
        collector_continuity(final, self.f.contract, reviewed, self.f.store)
        bad = copy.deepcopy(pending_snapshot)
        marker = next(q for q in bad['reviewQueue'] if q.get('kind') == 'source_document_revalidation')
        marker['url'] = 'https://example.invalid/releases/not-reviewed'
        bad.pop('snapshotSha256'); bad['snapshotSha256'] = digest(bad)
        with self.assertRaises(ValueError):
            collector_continuity(bad, self.f.contract, pending, self.f.store)

    def test_same_primary_bytes_after_failure_resolve_marker_without_model_or_new_facts(self):
        self.f.run_pipeline(fixtures.FakeAgent()); self.migrate()
        self.f.fetcher.pages[fixtures.URL] = 403
        failure = {'sourceId': 'official', 'requestedUrl': fixtures.URL, 'fetchedAt': '2026-10-20T16:00:00Z',
                   'observationId': 'known-failure-marker', 'status': 'blocked', 'httpStatus': 403}
        self.f.store.write_once('observations/known-failure-marker.json', failure)
        index_for(self.f.store).register_observation(failure)
        pending = self.f.run_pipeline()
        old = self.snapshot(pending)
        continuity = collector_continuity(old, self.f.contract, pending, self.f.store)
        self.f.time = '2026-10-22T16:00:00Z'
        self.f.fetcher.pages[fixtures.URL] = ('<html><body>' + fixtures.QUOTE + '</body></html>').encode()
        agent = fixtures.FakeAgent()
        reviewed = self.f.run_pipeline(agent)
        self.assertEqual(agent.calls, 0)
        self.assertEqual(reviewed['receipts'][0]['newFactIds'], [])
        final = self.snapshot(reviewed, old, continuity)
        self.assertFalse(any(q.get('kind') == 'source_document_revalidation' for q in final['reviewQueue']))
        self.assertEqual(len(final['documentReviewResolutions']), 1)

    def test_redirect_context_requires_exact_new_review_for_both_migration_and_current_cache(self):
        for migrate in (True, False):
            with self.subTest(migrate=migrate):
                if not migrate:
                    self.f.doCleanups(); self.setUp(); self.migrate(); self.f.time = fixtures.T
                self.f.run_pipeline(fixtures.FakeAgent())
                if migrate:
                    self.migrate()
                else:
                    self.f.time = '2026-10-20T16:00:00Z'
                original = index_for(self.f.store).latest_observation('official', fixtures.URL)
                redirect = {**original, 'finalUrl': 'https://example.invalid/releases/redirected',
                            'observationId': 'known-redirect-' + str(migrate),
                            'fetchedAt': '2026-10-20T15:00:00Z'}
                self.f.store.write_once('observations/' + redirect['observationId'] + '.json', redirect)
                index_for(self.f.store).register_observation(redirect)
                fetch = self.f.fetcher.fetch
                self.f.fetcher.fetch = lambda source, url, previous=None: {
                    **fetch(source, url, previous), **({'finalUrl': redirect['finalUrl']} if url == fixtures.URL else {})}
                agent = fixtures.FakeAgent()
                result = self.f.run_pipeline(agent)
                self.assertEqual(agent.calls, 2)
                self.assertTrue(result['processing']['complete'])
                validation = json.loads(self.f.store.get(result['receipts'][0]['documentValidations'][0]['validation']))
                self.assertEqual(validation['inputContext']['finalUrl'], redirect['finalUrl'])
                self.assertEqual(result['processing']['changedDocuments'], 1)



if __name__ == '__main__':
    unittest.main()
