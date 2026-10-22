import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from publisher_probe import PublisherAuth, PROJECT_ID, TEAM_ID, execute, failure_reason


class PublisherCredentialTests(unittest.TestCase):
    def test_project_probe_uses_fixed_team_without_user_scope_discovery(self):
        project = {'id': PROJECT_ID, 'accountId': TEAM_ID, 'rootDirectory': 'web', 'framework': 'vite'}
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {
            'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'jessepike/sec-market',
            'GITHUB_RUN_ID': 'fictional-run', 'VERCEL_TOKEN': 'fictional-token',
        }), patch('publisher_probe.PublisherAuth.cli', return_value=json.dumps(project)) as cli:
            receipt = execute(Path(folder) / 'auth')
        cli.assert_called_once_with(['api', '/v9/projects/' + PROJECT_ID + '?teamId=' + TEAM_ID, '--raw'])
        self.assertTrue(receipt['publisherAccessPassed'])
        self.assertFalse(receipt['publishPermissionAccepted'])
        self.assertFalse(receipt['deploymentAttempted'])

    def test_failure_classification_never_returns_raw_transport_or_credentials(self):
        for message, category in [
            ('Error: unknown option --raw', 'CLI_USAGE'),
            ('Error: You do not have access to the specified account', 'ACCOUNT_ACCESS_DENIED'),
            ('Error: The specified scope does not exist', 'TEAM_ACCESS_DENIED'),
            ('Error: token is not valid', 'TOKEN_REJECTED'),
            ('Error: Not able to load user: fetch failed', 'NETWORK'),
            ('Error: Not able to load user', 'USER_LOOKUP'),
            ('fictional-secret-response', 'UNCLASSIFIED'),
        ]:
            with self.subTest(category=category):
                result = SimpleNamespace(stdout='fictional-secret-token', stderr=message)
                self.assertEqual(failure_reason(result), 'VERCEL_READ_ONLY_ACCESS_PROBE_FAILED_' + category)

    def test_private_auth_file_and_no_credentials_on_argv_or_in_child_environment(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'publisher'
            calls = []
            def runner(args, **kwargs):
                calls.append((args, kwargs['env']))
                return SimpleNamespace(returncode=0, stdout='{}')
            with patch.dict(os.environ, {'GH_TOKEN': 'fictional-gh', 'SMP_AUTH_STORE_TOKEN': 'fictional-writer',
                                         'OPENAI_API_KEY': 'fictional-api', 'VERCEL_TOKEN': 'fictional-vercel'}):
                with PublisherAuth(root, 'fictional-vercel', runner) as client:
                    self.assertEqual(root.stat().st_mode & 0o777, 0o700)
                    self.assertEqual((root / 'auth.json').stat().st_mode & 0o777, 0o600)
                    self.assertEqual(json.loads((root / 'auth.json').read_text()), {'token': 'fictional-vercel'})
                    client.cli(['api', '/v9/projects/' + PROJECT_ID, '--raw'])
            self.assertFalse(root.exists())
            self.assertNotIn('fictional-vercel', calls[0][0])
            self.assertNotIn('--scope', calls[0][0])
            for key in ['GH_TOKEN', 'SMP_AUTH_STORE_TOKEN', 'OPENAI_API_KEY', 'VERCEL_TOKEN', 'CODEX_HOME']:
                self.assertNotIn(key, calls[0][1])

    def test_unsafe_auth_paths_and_missing_tokens_are_rejected(self):
        from bootstrap import REPO
        for path, token in [(REPO / 'unsafe-auth', 'fictional'), (Path('/tmp/unused-publisher-auth'), '')]:
            with self.assertRaises(RuntimeError):
                with PublisherAuth(path, token):
                    self.fail('Unsafe auth accepted')

    def test_failed_probe_removes_auth_without_exposing_raw_response(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'publisher'
            with self.assertRaisesRegex(RuntimeError, 'VERCEL_READ_ONLY_ACCESS_PROBE_FAILED'):
                with PublisherAuth(root, 'fictional', lambda *_a, **_k: SimpleNamespace(returncode=1, stdout='fictional-sensitive-response')) as client:
                    client.cli(['api', '/v9/projects/' + PROJECT_ID, '--raw'])
            self.assertFalse(root.exists())


if __name__ == '__main__':
    unittest.main()
