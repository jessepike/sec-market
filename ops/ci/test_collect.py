import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from collect import BoundedPipeline, escrow_budgets, session_runtime, execution_outcome, exit_code, archive_collection_result
from storage import LocalStore


class CollectionDurabilityTests(unittest.TestCase):
    def test_timer_receipt_binds_actual_identity_policy_and_coverage_without_secrets(self):
        result = {'githubRunId': '123', 'githubEventName': 'schedule', 'githubRef': 'refs/heads/main',
                  'appRevision': 'a'*40, 'runId': 'real-collection', 'successfulTasks': 244,
                  'requiredTasks': 557, 'complete': False, **execution_outcome(False),
                  'unexpectedSecret': 'must not survive'}
        retained = archive_collection_result(self.state, result, self.contract, '2')
        self.assertEqual(self.state.read('ci/collection-runs/123-2.json'), retained)
        self.assertEqual(retained['githubEventName'], 'schedule')
        self.assertEqual(retained['githubRunAttempt'], 2)
        self.assertFalse(retained['complete'])
        self.assertNotIn('unexpectedSecret', retained)
        from contracts import digest
        self.assertEqual(retained['contractSha256'], digest(self.contract))
        with self.assertRaisesRegex(ValueError, 'Immutable object collision'):
            archive_collection_result(self.state, {**result, 'runId': 'different'}, self.contract, '2')

    def test_completed_partial_execution_is_success_without_upgrading_coverage(self):
        receipt = {'complete': False, **execution_outcome(False)}
        self.assertFalse(receipt['complete'])
        self.assertEqual(receipt['outcome'], 'completed_with_gaps')
        self.assertEqual(exit_code(receipt), 0)

    def test_completed_full_execution_keeps_explicit_coverage_outcome(self):
        self.assertEqual(execution_outcome(True), {'executionCompleted': True, 'outcome': 'completed_complete'})

    def test_cancelled_execution_fails_even_with_complete_coverage(self):
        receipt = {'complete': True, **execution_outcome(True, cancelled=True)}
        self.assertEqual(receipt['outcome'], 'cancelled')
        self.assertEqual(exit_code(receipt), 2)

    def test_setup_failure_or_legacy_coverage_cannot_claim_completed_execution(self):
        self.assertEqual(exit_code({'complete': False, 'reason': 'RUNNER_SETUP_NOT_COMPLETED'}), 2)
        self.assertEqual(exit_code({'complete': True}), 2)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.state = LocalStore(self.root / 'state')
        self.contract = {'sources': [], 'suppliers': [], 'model': {'maxCallsPerRun': 8, 'maxDocumentsPerRun': 4},
                         'schedule': {'maxFetchesPerRun': 10}}

    def test_exhausted_outer_deadline_does_not_consume_daily_capacity(self):
        with patch('collect.time.monotonic', return_value=10):
            worker = BoundedPipeline(self.contract, self.state, None, maximum_seconds=60)
        worker.budget_name = 'budget-2026-10-21'
        with patch('collect.time.monotonic', return_value=70):
            with self.assertRaisesRegex(ValueError, 'CI_COLLECTION_TIME_BUDGET_EXHAUSTED'):
                worker._reserve('calls', 8)
        self.assertIsNone(self.state.read('heads/budget-2026-10-21.json'))

    def test_cancellation_stops_new_work_without_refunding_usage(self):
        worker = BoundedPipeline(self.contract, self.state, None, maximum_seconds=60)
        worker.budget_name = 'budget-2026-10-23'
        prior = {'calls': 80, 'documents': 40, 'fetches': 5000}
        self.state.compare_and_swap(worker.budget_name, None, prior)
        worker.stop()
        with self.assertRaisesRegex(ValueError, 'CI_COLLECTION_TIME_BUDGET_EXHAUSTED'):
            worker._reserve('calls', 80)
        self.assertEqual(self.state.read('heads/budget-2026-10-23.json'), prior)

    def test_remote_ceiling_precedes_local_spending_and_preserves_prior_usage(self):
        prior = {'calls': 3, 'documents': 2, 'fetches': 5}
        self.state.compare_and_swap('budget-2026-10-21', None, prior)
        acknowledged = []
        with patch.object(session_runtime, 'checkpoint', side_effect=lambda *_a, **_k: acknowledged.append(self.state.read('heads/budget-2026-10-21.json'))):
            escrow_budgets(self.root, self.state, {'sessionId': 'fictional-run'}, self.contract, '2026-10-21T12:00:00Z')
        self.assertEqual(acknowledged, [{'calls': 8, 'documents': 4, 'fetches': 10}])
        self.assertEqual(self.state.read('heads/budget-2026-10-21.json'), prior)

    def test_failed_remote_reservation_never_refunds_capacity(self):
        with patch.object(session_runtime, 'checkpoint', side_effect=RuntimeError('remote unavailable')):
            with self.assertRaisesRegex(RuntimeError, 'remote unavailable'):
                escrow_budgets(self.root, self.state, {'sessionId': 'fictional-run'}, self.contract, '2026-10-21T12:00:00Z')
        self.assertEqual(self.state.read('heads/budget-2026-10-21.json'), {'calls': 8, 'documents': 4, 'fetches': 10})


if __name__ == '__main__':
    unittest.main()
