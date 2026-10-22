import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from publisher_probe import PublisherAuth, PROJECT_ID, execute


class PublisherCredentialTests(unittest.TestCase):
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
