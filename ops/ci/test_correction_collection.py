"""Offline collection mechanics. Synthetic outcomes never admit a correction."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from agents import SubscriptionAgent
from collect import BoundedPipeline, archive_collection_result, correction_work, execution_outcome, reuse_scheduled_collection
from contracts import digest, plan_run
from discovery import discover
from engine import Pipeline
from storage import LocalStore
from validation import reconcile


NOW = '2026-10-23T12:00:00Z'
REPO = Path(__file__).resolve().parents[2]
TEXT = 'Fixture Vendor has a primary source document with neutral background information. ' * 3


def fixture_contract():
    source = {'id': 'generic', 'supplierId': 'fixture', 'family': 'official_announcements',
              'kind': 'rss', 'url': 'https://example.invalid/feed.xml', 'allowedHosts': ['example.invalid'],
              'registration': 'verified', 'required': True, 'maxPages': 2, 'scopePrefixes': ['/release/']}
    sources = [source, {**source, 'id': 'citation', 'kind': 'citation', 'family': 'citation_integrity',
                        'url': 'https://example.invalid/release/one'},
               {**source, 'id': 'sec', 'kind': 'sec_facts', 'family': 'regulatory_filings',
                'url': 'https://example.invalid/facts.json'}]
    return {'schemaVersion': 1, 'version': 'synthetic-collection-mechanics',
            'schedule': {'intervalHours': 24, 'overdueHours': 30, 'reconcileEveryRun': True,
                         'maxWorkers': 3, 'maxFetchesPerRun': 10},
            'model': {'provider': 'codex_subscription', 'allowApiBilling': False, 'maxDocumentsPerRun': 2,
                      'maxCallsPerRun': 3, 'maxDocumentChars': 30000, 'timeoutSeconds': 2},
            'publication': {'enabled': False, 'allowDegradedCoverage': True},
            'suppliers': [{'id': 'fixture', 'name': 'Fixture Vendor', 'kind': 'private', 'aliases': [],
                           'sourceIds': [s['id'] for s in sources], 'requiredCategories': ['funding_valuation'],
                           'requiredFamilies': [s['family'] for s in sources]}], 'sources': sources}


class OfflineFetcher:
    def __init__(self, store):
        self.store = store
        self.calls = 0

    def fetch(self, source, url, previous=None):
        self.calls += 1
        body = (b'{"facts":{},"cik":1}' if url.endswith('.json') else
                b'<rss><channel><item><link>https://example.invalid/release/one</link></item></channel></rss>'
                if url.endswith('.xml') else ('<html><body>' + TEXT + '</body></html>').encode())
        return {'requestedUrl': url, 'finalUrl': url, 'fetchedAt': NOW, 'status': 'fetched',
                'httpStatus': 200, 'body': self.store.put(body), 'contentType': 'text/html'}


class MechanicsAgent(SubscriptionAgent):
    synthetic = True

    def __init__(self, config, events):
        super().__init__(config, runner=Mock(side_effect=AssertionError('No real model execution')))
        self.events = events

    def extract(self, text, supplier):
        self.reserve('calls', self.config['maxCallsPerRun'])
        self.calls += 1
        self.events.append('generic')
        return []

    def review_empty(self, text, supplier, observation, policy):
        self.reserve('calls', self.config['maxCallsPerRun'])
        self.calls += 1
        return {'noRelevantFacts': True, 'evidenceSha256': observation['body']['sha256'], 'policySha256': policy}


class CorrectionCollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.state = LocalStore(self.root / 'state')
        self.contract = fixture_contract()
        self.events = []
        self.agent = MechanicsAgent(self.contract['model'], self.events)
        self.fetcher = OfflineFetcher(self.state)

    def run_pipeline(self, work, pipeline=Pipeline, **kwargs):
        return pipeline(self.contract, self.state, self.fetcher, self.agent, clock=lambda: NOW,
                        structured=lambda *_: [], correction_work=work, **kwargs).run(NOW, replay=True)

    @staticmethod
    def pending(reason='SYNTHETIC_NON_ADMITTING'):
        return {'policySha256': 'a' * 64, 'admitted': [],
                'pending': [{'groupId': 'fixture-group', 'reason': reason}], 'attempts': []}

    def test_deterministic_tasks_finish_before_correction_and_generic_reservations(self):
        def work(*, reserve, now, cancelled):
            plan = plan_run(self.contract, NOW)
            for task in plan['tasks']:
                if task['sourceId'] in ('sec', 'citation'):
                    receipt = self.state.read('heads/task-' + task['taskId'] + '.json')
                    self.assertEqual(receipt['outcome'], 'checked_no_change')
            self.assertEqual(self.events, [])
            self.assertFalse(cancelled())
            self.assertEqual(now, NOW)
            reserve('documents', 2)
            reserve('calls', 3)
            self.events.append('correction')
            return self.pending()
        result = self.run_pipeline(work)
        self.assertEqual(self.events, ['correction', 'generic'])
        self.assertTrue(result['complete'])
        self.assertEqual(result['requiredTasks'], 3)
        self.assertEqual(len(result['receipts']), 3)
        self.assertEqual(self.state.read('heads/budget-2026-10-23.json'), {'calls': 3, 'documents': 2, 'fetches': 3})
        self.agent.runner.assert_not_called()

    def test_pending_corrections_archive_coverage_and_separate_hash_bound_outcome(self):
        result = self.run_pipeline(lambda **_: self.pending())
        latest = self.state.read('heads/latest-run.json')
        coverage = json.loads(self.state.get(latest['receipt']))
        plan = self.state.read('runs/' + result['runId'] + '/plan.json')
        self.assertEqual(coverage, reconcile(plan, result['receipts'], self.contract, NOW, self.state))
        self.assertNotIn('corrections', coverage)
        head = self.state.read('heads/correction-collection.json')
        correction = json.loads(self.state.get(head['outcome']))
        self.assertEqual(correction, {'runId': result['runId'], 'checkedAt': NOW, **self.pending()})
        self.assertEqual(head['runId'], coverage['runId'])
        self.assertEqual(result['corrections']['receipt'], head['outcome'])
        archived = archive_collection_result(self.state, {
            **result, 'githubRunId': '123', 'githubEventName': 'schedule', 'githubRef': 'refs/heads/main',
            'appRevision': 'a' * 40, **execution_outcome(result['complete'])}, self.contract, '1')
        self.assertEqual(archived['corrections'], result['corrections'])
        self.assertEqual(archived['requiredTasks'], 3)

    def test_uncached_citation_models_wait_for_corrections_and_reuse_primary_transport(self):
        def citation_documents(source, request):
            found = discover(source, request)
            if source['kind'] == 'citation':
                # Exercise a citation with uncached document work, even though
                # today's simple citation adapter only checks transport.
                found['items'] = [source['url']]
            return found

        def work(*, reserve, **_):
            self.assertEqual(self.agent.calls, 0)
            self.assertEqual(self.events, [])
            plan = plan_run(self.contract, NOW)
            citation = next(t for t in plan['tasks'] if t['sourceId'] == 'citation')
            first = self.state.read('heads/task-' + citation['taskId'] + '.json')
            self.assertEqual(first['errorCode'], 'CITATION_MODEL_WORK_DEFERRED_FOR_CORRECTIONS')
            self.assertTrue(first['citationModelWorkDeferred'])
            budget = self.state.read('heads/budget-2026-10-23.json')
            self.assertEqual((budget['calls'], budget['documents']), (0, 0))
            reserve('documents', 2)
            reserve('calls', 3)
            self.events.append('correction')
            return self.pending()

        with patch('engine.discover', side_effect=citation_documents):
            result = self.run_pipeline(work)
        self.assertEqual(self.events, ['correction', 'generic'])
        self.assertTrue(result['complete'])
        self.assertEqual(result['requiredTasks'], 3)
        self.assertEqual(len(result['receipts']), 3)
        self.assertEqual(len({r['taskId'] for r in result['receipts']}), 3)
        citation = next(r for r in result['receipts'] if r['sourceId'] == 'citation')
        self.assertEqual(citation['outcome'], 'checked_no_change')
        self.assertEqual(len(citation['observationIds']), 1)
        self.assertEqual(self.fetcher.calls, 3)
        self.assertEqual(self.state.read('heads/budget-2026-10-23.json'), {'calls': 3, 'documents': 2, 'fetches': 3})
        self.agent.runner.assert_not_called()

    def test_replay_invokes_corrections_without_repeating_valid_source_or_model_work(self):
        work = Mock(side_effect=lambda **_: self.pending())
        first = self.run_pipeline(work)
        counts = copy.deepcopy(self.state.read('heads/budget-2026-10-23.json'))
        with patch.object(self.fetcher, 'fetch', side_effect=AssertionError('No same-day refetch')):
            second = self.run_pipeline(work)
        self.assertEqual(work.call_count, 2)
        self.assertEqual(first['receipts'], second['receipts'])
        self.assertEqual(self.state.read('heads/budget-2026-10-23.json'), counts)
        self.assertEqual(self.agent.calls, 2)

    def test_new_workers_share_exhausted_daily_limits_and_keep_source_receipts(self):
        self.contract['model'].update(maxCallsPerRun=80, maxDocumentsPerRun=40)
        prior = {'calls': 80, 'documents': 40, 'fetches': 0}
        self.state.compare_and_swap('budget-2026-10-23', None, prior)
        def work(*, reserve, **_):
            try:
                reserve('documents', 40)
            except ValueError as error:
                return self.pending(str(error))
            self.fail('Exhausted correction document reservation succeeded')
        for _ in range(2):
            self.agent = MechanicsAgent(self.contract['model'], self.events)
            result = self.run_pipeline(work)
            self.assertEqual(result['corrections']['pending'][0]['reason'], 'DOCUMENTS_BUDGET_EXHAUSTED')
            self.assertEqual(len(result['receipts']), 3)
            self.assertEqual(result['requiredTasks'], 3)
            self.assertEqual(self.agent.calls, 0)
        budget = self.state.read('heads/budget-2026-10-23.json')
        self.assertEqual((budget['calls'], budget['documents']), (80, 40))

    def test_runtime_error_keeps_source_coverage_and_records_correction_error(self):
        result = self.run_pipeline(Mock(side_effect=ValueError('CORRECTION_POLICY_INVALID')))
        self.assertTrue(result['complete'])
        self.assertEqual(result['corrections']['error'], 'CORRECTION_POLICY_INVALID')
        self.assertEqual(result['corrections']['admitted'], [])
        self.assertEqual(len(result['receipts']), 3)

    def test_bounded_deadline_and_stop_reach_correction_callback_without_refund(self):
        observed = []
        def work(*, reserve, cancelled, **_):
            observed.append(cancelled())
            with self.assertRaisesRegex(ValueError, 'CI_COLLECTION_TIME_BUDGET_EXHAUSTED'):
                reserve('calls', 3)
            return self.pending('CORRECTION_CANCELLED_OR_DEADLINE')
        worker = BoundedPipeline(self.contract, self.state, self.fetcher, self.agent, clock=lambda: NOW,
                                 structured=lambda *_: [], correction_work=work, maximum_seconds=60)
        worker.stop()
        prior = {'calls': 2, 'documents': 1, 'fetches': 0}
        self.state.compare_and_swap('budget-2026-10-23', None, prior)
        result = worker.run(NOW)
        self.assertEqual(observed, [True])
        self.assertEqual(self.state.read('heads/budget-2026-10-23.json'), prior)
        self.assertEqual(len(result['receipts']), 3)
        self.assertEqual(result['corrections']['admitted'], [])
        worker.cancelled = False
        worker.account_deadline = 0
        self.assertTrue(worker._work_cancelled())

    def test_original_557_tasks_survive_when_every_correction_and_budget_is_pending(self):
        # This empty-store fixture predates qualification origins and their objects.
        self.contract = json.loads((REPO / 'web/scripts/migration-proofs/daily-v2-original/market.json').read_text())
        self.state.compare_and_swap('budget-2026-10-23', None, {'calls': 80, 'documents': 40, 'fetches': 5500})
        with patch.object(self.fetcher, 'fetch', side_effect=AssertionError('No HTTP allowed')):
            result = self.run_pipeline(lambda **_: self.pending('DOCUMENTS_BUDGET_EXHAUSTED'))
        self.assertEqual(result['requiredTasks'], 557)
        self.assertEqual(len(result['receipts']), 557)
        self.assertEqual(result['inventorySha256'], plan_run(self.contract, NOW)['inventorySha256'])
        self.assertEqual(self.state.read('heads/budget-2026-10-23.json'), {'calls': 80, 'documents': 40, 'fetches': 5500})

    def test_correction_contract_disables_timer_fast_path_before_any_lookup(self):
        lookup = Mock(side_effect=AssertionError('Fast-path must not inspect prior schedule'))
        self.assertIsNone(reuse_scheduled_collection(self.state, self.contract, NOW,
                                                   lookup=lookup, corrections_enabled=True))
        lookup.assert_not_called()

    def test_actual_callback_binds_same_agent_store_market_and_reserve(self):
        self.assertIsNone(correction_work(self.root, self.state, self.contract, self.agent))
        requests = self.root / 'contracts/factual-corrections.json'
        requests.parent.mkdir()
        requests.write_text(json.dumps({'groups': [{'id': 'one'}, {'id': 'two'}]}))
        work = correction_work(self.root, self.state, self.contract, self.agent)
        reserve, cancelled = Mock(), Mock(return_value=False)
        with patch('corrections.process_corrections', return_value=self.pending()) as process:
            self.assertEqual(work(reserve=reserve, now=NOW, cancelled=cancelled), self.pending())
        process.assert_called_once_with(self.root, self.state, self.contract, self.agent, reserve, NOW,
                                        cancelled=cancelled)
        with patch('corrections.process_corrections', side_effect=ValueError('POLICY_INVALID')):
            outcome = work(reserve=reserve, now=NOW, cancelled=cancelled)
        self.assertEqual(outcome['pending'], [{'groupId': g, 'reason': 'POLICY_INVALID'} for g in ('one', 'two')])
        self.assertEqual(outcome['admitted'], [])
        self.assertIsNone(outcome['policySha256'])


if __name__ == '__main__':
    unittest.main()
