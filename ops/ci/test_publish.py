import os
import unittest
from unittest.mock import patch

import publish


class PublisherBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'jessepike/sec-market',
                                          'GITHUB_REF': 'refs/heads/main'}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_preview_cannot_reach_auth_or_archive(self):
        os.environ['GITHUB_REF'] = 'refs/heads/preview'
        with patch.object(publish.session_runtime, 'bootstrap') as bootstrap:
            with self.assertRaisesRegex(ValueError, 'REVIEWED_MAIN_REQUIRED'):
                publish.execute('/tmp/fictional-publisher')
            bootstrap.assert_not_called()

    def test_disabled_cutover_needs_no_secret_and_writes_no_archive(self):
        with patch.object(publish, 'validate_contract', return_value={'publication': {'enabled': False}}), \
             patch.object(publish.session_runtime, 'bootstrap') as bootstrap:
            result = publish.execute('/tmp/fictional-publisher')
        self.assertFalse(result['activated'])
        self.assertFalse(result['published'])
        bootstrap.assert_not_called()

    def test_missing_publisher_credential_fails_before_archive_lease(self):
        with patch.object(publish, 'validate_contract', return_value={'publication': {'enabled': True}}), \
             patch.object(publish.session_runtime, 'bootstrap') as bootstrap:
            with self.assertRaisesRegex(ValueError, 'VERCEL_TOKEN_NOT_CONFIGURED'):
                publish.execute('/tmp/fictional-publisher')
        bootstrap.assert_not_called()
