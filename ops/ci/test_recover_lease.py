import tempfile
import unittest

from recover_lease import release_terminated
from storage import LocalStore


class AbandonedLeaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(self.temp.name)
        self.lease = {'sessionId': 'github-123-1', 'expiresAt': '2026-10-23T07:01:00Z'}
        self.store.compare_and_swap('cloud-lease', None, self.lease)
        self.budget = {'calls': 80, 'documents': 40, 'fetches': 5000}
        self.store.compare_and_swap('budget-2026-10-23', None, self.budget)

    def run_info(self, status='completed', conclusion='cancelled'):
        return {'id': 123, 'run_attempt': 1, 'repository': {'full_name': 'jessepike/sec-market'},
                'status': status, 'conclusion': conclusion}

    def test_cancelled_runner_releases_only_lease_retaining_full_unknown_capacity(self):
        before = (self.store.root / 'heads/budget-2026-10-23.json').read_bytes()
        result = release_terminated(self.store, lambda _: self.run_info())
        self.assertTrue(result['recovered'])
        self.assertTrue(result['lease']['recovery']['unknownCapacityRetained'])
        self.assertEqual((self.store.root / 'heads/budget-2026-10-23.json').read_bytes(), before)

    def test_running_owner_cannot_be_recovered_even_if_expiry_looks_old(self):
        with self.assertRaisesRegex(ValueError, 'LEASE_OWNER_STILL_RUNNING'):
            release_terminated(self.store, lambda _: self.run_info('in_progress', None))
        self.assertEqual(self.store.read('heads/cloud-lease.json'), self.lease)

    def test_other_repository_receipt_cannot_release_lease(self):
        run = self.run_info()
        run['repository']['full_name'] = 'attacker/other'
        with self.assertRaisesRegex(ValueError, 'LEASE_RECOVERY_RUN_IDENTITY_DIFFERS'):
            release_terminated(self.store, lambda _: run)

    def test_newer_still_running_rerun_cannot_release_old_lease(self):
        run = self.run_info('in_progress', None)
        run['run_attempt'] = 2
        with self.assertRaisesRegex(ValueError, 'LEASE_OWNER_STILL_RUNNING'):
            release_terminated(self.store, lambda _: run)
