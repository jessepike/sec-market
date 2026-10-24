"""Original scheduling proof and current freshness remain separate across UTC days."""
import copy
import json
import unittest

import test_retained_audit_rebinding as fixtures
from contracts import digest
from retained_audit import index_for, separated_details
from separation import MODE
from snapshot import build_snapshot, collector_continuity
from validation import reconcile


class MidnightPartitionReplayTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.RetainedAuditTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.f.contract['version'] = 'test-v2'
        self.f.contract['collection']['mode'] = MODE
        self.f.contract['model']['maxDocumentsPerRun'] = 1
        self.f.time = '2026-10-24T23:50:00Z'
        self.other = 'https://example.invalid/releases/two'
        source = self.f.contract['sources'][0]
        source.update(kind='sitemap', url='https://example.invalid/sitemap.xml')
        self.f.fetcher.pages[source['url']] = ('<urlset>' + ''.join(
            '<url><loc>' + url + '</loc><lastmod>2026-09-24T08:00:00Z</lastmod></url>'
            for url in (fixtures.URL, self.other)) + '</urlset>').encode()
        self.f.fetcher.pages[self.other] = self.f.fetcher.pages[fixtures.URL] + b'<!--second-->'
        self.result = self.f.run_pipeline(fixtures.FakeAgent())
        self.receipt = self.result['receipts'][0]
        self.plan = self.f.store.read('runs/' + self.result['runId'] + '/plan.json')
        self.source = source
        self.saved = json.loads(self.f.store.get(self.receipt['processingManifest']))
        self.at = '2026-10-25T00:23:00Z'

    def replay(self, result=None, at=None):
        result = result or self.result
        return reconcile(self.plan, result['receipts'], self.f.contract, at or self.at, self.f.store)

    def test_midnight_replays_original_seal_and_evaluates_new_scheduling_window_without_credit(self):
        self.assertEqual(self.saved['current'], sorted([fixtures.URL, self.other]))
        before = {oid: copy.deepcopy(self.f.store.read('observations/' + oid + '.json'))
                  for oid in self.receipt['observationIds']}
        old_snapshot = build_snapshot(self.f.contract, self.plan, self.result, self.f.store, self.f.time)
        current = self.replay()
        self.assertEqual(current['successfulTasks'], self.result['successfulTasks'])
        self.assertEqual(current['processing'], self.result['processing'])
        self.assertEqual(current['historicalReview'], self.result['historicalReview'])
        evaluated = separated_details(self.receipt, self.f.contract, self.source, self.at, self.f.store)
        self.assertEqual(evaluated['partitions']['current'], [])
        self.assertEqual(evaluated['partitions']['historical'], sorted([fixtures.URL, self.other]))
        self.assertEqual(json.loads(self.f.store.get(self.receipt['processingManifest'])), self.saved)
        continuity = collector_continuity(old_snapshot, self.f.contract, self.result, self.f.store)
        rebuilt = build_snapshot(self.f.contract, self.plan, current, self.f.store, self.at,
                                 previous=old_snapshot, continuity=continuity)
        self.assertEqual(rebuilt['events'], old_snapshot['events'])
        self.assertEqual(rebuilt['evidence'], old_snapshot['evidence'])
        self.assertEqual(rebuilt['coverage']['lastCollectionAt'], old_snapshot['coverage']['lastCollectionAt'])
        self.assertFalse(current['processing']['complete'])
        self.assertEqual(self.receipt['validatedFacts'], self.result['receipts'][0]['validatedFacts'])
        for oid, value in before.items():
            self.assertEqual(self.f.store.read('observations/' + oid + '.json'), value)

    def test_rehashed_manifest_or_changed_completion_clock_cannot_move_original_proof(self):
        bad = copy.deepcopy(self.result)
        partition = copy.deepcopy(self.saved)
        partition['historical'] = partition['current']
        partition['current'] = []
        bad['receipts'][0]['processingManifest'] = self.f.store.put(partition)
        with self.assertRaisesRegex(ValueError, 'partition proof differs'):
            self.replay(bad)
        bad = copy.deepcopy(self.result)
        bad['receipts'][0]['completedAt'] = self.at
        with self.assertRaisesRegex(ValueError, 'receipt clock differs'):
            self.replay(bad)

    def test_original_clock_does_not_make_expired_current_transport_fresh(self):
        # Fresh primary validations must still satisfy their current 30h limit.
        with self.assertRaisesRegex(ValueError, 'latest transport is stale or future'):
            self.replay(at='2026-10-26T06:00:01Z')

    def test_original_historical_view_uses_entire_sealed_receipt_and_exact_attempt(self):
        bad = copy.deepcopy(self.result)
        bad['receipts'][0]['startedAt'] = '2026-10-24T22:00:00Z'
        with self.assertRaisesRegex(ValueError, 'original sealed receipt'):
            self.replay(bad)
        path = 'runs/' + self.receipt['runId'] + '/attempts/' + self.receipt['attemptId'] + '.json'
        original_raw = self.f.store._path(path).read_bytes()
        altered = copy.deepcopy(self.receipt)
        altered['startedAt'] = '2026-10-24T22:00:00Z'
        from contracts import canonical
        self.f.store._path(path).write_bytes(canonical(altered))
        with self.assertRaisesRegex(ValueError, 'original sealed receipt'):
            self.replay()
        self.f.store._path(path).write_bytes(original_raw)

    def test_later_failed_primary_and_changed_subject_policy_still_reject(self):
        reviewed_url = self.receipt['documentValidations'][0]['url']
        failure = {'sourceId': self.source['id'], 'requestedUrl': reviewed_url,
                   'fetchedAt': '2026-10-25T00:10:00Z', 'observationId': 'midnight-newer-failure',
                   'status': 'blocked', 'httpStatus': 403}
        self.f.store.write_once('observations/' + failure['observationId'] + '.json', failure)
        index_for(self.f.store).register_observation(failure)
        with self.assertRaises(ValueError):
            self.replay()
        self.f.contract['suppliers'][0]['aliases'].append('Changed subject alias')
        with self.assertRaisesRegex(ValueError, 'Contract changed after planning'):
            self.replay()


if __name__ == '__main__':
    unittest.main()
