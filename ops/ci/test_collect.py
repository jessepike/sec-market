import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from collect import BoundedPipeline, escrow_budgets, session_runtime
from storage import LocalStore


class CollectionDurabilityTests(unittest.TestCase):
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
