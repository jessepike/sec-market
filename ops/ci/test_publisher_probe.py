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

    def resource_probe(self, resource_config, *, include=True, default_resource_config=None, include_default=False):
        project = {'id': PROJECT_ID, 'accountId': TEAM_ID, 'rootDirectory': 'web', 'framework': 'vite'}
        if include:
            project['resourceConfig'] = resource_config
        if include_default:
            project['defaultResourceConfig'] = default_resource_config
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {
            'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'jessepike/sec-market',
            'GITHUB_RUN_ID': 'fictional-run', 'VERCEL_TOKEN': 'fictional-token',
        }), patch('publisher_probe.PublisherAuth.cli', return_value=json.dumps(project)) as cli:
            receipt = execute(Path(folder) / 'auth')
        cli.assert_called_once_with(['api', '/v9/projects/' + PROJECT_ID + '?teamId=' + TEAM_ID, '--raw'])
        self.assertTrue(receipt['publisherAccessPassed'])
        self.assertTrue(receipt['readOnly'])
        self.assertFalse(receipt['deploymentAttempted'])
        self.assertFalse(receipt['publishPermissionAccepted'])
        self.assertNotIn('resourceConfig', receipt)
        self.assertNotIn('defaultResourceConfig', receipt)
        return receipt

    def test_native_resource_readback_exposes_only_three_typed_fields(self):
        expected = {'buildMachineType': 'basic', 'buildMachineSelection': 'fixed',
                    'elasticConcurrencyEnabled': False}
        receipt = self.resource_probe({**expected, 'unrelatedNativeField': 'fictional-resource-secret'})
        self.assertEqual({key: receipt[key] for key in expected}, expected)
        self.assertNotIn('fictional-resource-secret', json.dumps(receipt))

    def test_absent_or_non_object_native_resource_fields_remain_unknown(self):
        for include, resource in [(False, None), (True, None), (True, []), (True, 'basic'),
                                  (True, False), (True, 1), (True, {})]:
            with self.subTest(include=include, resource=resource):
                receipt = self.resource_probe(resource, include=include)
                for key in ('buildMachineType', 'buildMachineSelection', 'elasticConcurrencyEnabled'):
                    self.assertIsNone(receipt[key])

    def test_malformed_native_resource_fields_are_null_without_hiding_valid_siblings(self):
        values = [({'nested': 'fictional-resource-secret'}, 'fixed', False),
                  ('basic', ['fictional-resource-secret'], True),
                  ('basic', 'fixed', 'false'), ('basic', 'fixed', 0)]
        for machine, selection, concurrency in values:
            with self.subTest(machine=machine, selection=selection, concurrency=concurrency):
                receipt = self.resource_probe({'buildMachineType': machine,
                                              'buildMachineSelection': selection,
                                              'elasticConcurrencyEnabled': concurrency})
                self.assertEqual(receipt['buildMachineType'], machine if type(machine) is str else None)
                self.assertEqual(receipt['buildMachineSelection'], selection if type(selection) is str else None)
                self.assertEqual(receipt['elasticConcurrencyEnabled'], concurrency if type(concurrency) is bool else None)
                self.assertNotIn('fictional-resource-secret', json.dumps(receipt))

    def test_override_and_default_diagnostics_preserve_raw_unknowns_without_effective_setting(self):
        for override in ({}, {'elasticConcurrencyEnabled': None}, {'elasticConcurrencyEnabled': False},
                         {'elasticConcurrencyEnabled': True}, {'elasticConcurrencyEnabled': 'false'}):
            for default in (False, True, None, 'false', {'hidden': 'fictional-default-secret'}):
                with self.subTest(override=override, default=default):
                    receipt = self.resource_probe(override, default_resource_config={
                        'elasticConcurrencyEnabled': default, 'hidden': 'fictional-default-secret'}, include_default=True)
                    self.assertTrue(receipt['resourceConfigPresent'])
                    self.assertEqual(receipt['resourceConfigType'], 'object')
                    self.assertEqual(receipt['elasticConcurrencyEnabledPresent'], 'elasticConcurrencyEnabled' in override)
                    self.assertEqual(receipt['elasticConcurrencyEnabledType'],
                                     'missing' if not override else {type(None): 'null', bool: 'boolean', str: 'string'}[type(override['elasticConcurrencyEnabled'])])
                    self.assertTrue(receipt['defaultResourceConfigPresent'])
                    self.assertEqual(receipt['defaultResourceConfigType'], 'object')
                    self.assertTrue(receipt['defaultElasticConcurrencyEnabledPresent'])
                    self.assertEqual(receipt['defaultElasticConcurrencyEnabled'], default if type(default) is bool else None)
                    self.assertEqual(receipt['defaultElasticConcurrencyEnabledType'],
                                     {type(None): 'null', bool: 'boolean', str: 'string', dict: 'object'}[type(default)])
                    if type(override.get('elasticConcurrencyEnabled')) is bool:
                        self.assertEqual(receipt['elasticConcurrencyEnabled'], override['elasticConcurrencyEnabled'])
                    else:
                        self.assertIsNone(receipt['elasticConcurrencyEnabled'])
                    self.assertNotIn('fictional-default-secret', json.dumps(receipt))
                    self.assertFalse(any('effective' in name.lower() for name in receipt))

    def test_resource_shape_diagnostics_distinguish_missing_null_and_malformed_objects(self):
        for value, expected in [(None, 'null'), ([], 'array'), ('bad', 'string'), (False, 'boolean'), (1, 'number')]:
            with self.subTest(value=value):
                receipt = self.resource_probe(value, default_resource_config=value, include_default=True)
                for prefix in ('resourceConfig', 'defaultResourceConfig'):
                    self.assertTrue(receipt[prefix + 'Present'])
                    self.assertEqual(receipt[prefix + 'Type'], expected)
                for prefix in ('elasticConcurrencyEnabled', 'defaultElasticConcurrencyEnabled'):
                    self.assertIsNone(receipt[prefix])
                    self.assertIsNone(receipt[prefix + 'Present'])
                    self.assertEqual(receipt[prefix + 'Type'], 'unavailable')
        receipt = self.resource_probe(None, include=False)
        for prefix in ('resourceConfig', 'defaultResourceConfig'):
            self.assertFalse(receipt[prefix + 'Present'])
            self.assertEqual(receipt[prefix + 'Type'], 'missing')
        receipt = self.resource_probe({}, default_resource_config={}, include_default=True)
        self.assertIsNone(receipt['defaultElasticConcurrencyEnabled'])
        self.assertFalse(receipt['defaultElasticConcurrencyEnabledPresent'])
        self.assertEqual(receipt['defaultElasticConcurrencyEnabledType'], 'missing')

    def test_read_only_workflow_retains_all_guards_and_only_reduces_its_test_selection(self):
        workflow = (Path(__file__).resolve().parents[2] / '.github/workflows/subscription-publisher-probe.yml').read_text()
        self.assertEqual(workflow.count("run: python3 -m unittest discover -s ops/ci -p 'test_publisher_probe.py' -v"), 1)
        self.assertIn("github.repository == 'jessepike/sec-market' && github.event.repository.private == true", workflow)
        self.assertIn("if: contains(github.event.head_commit.message, '[stage-publisher]')", workflow)
        self.assertIn('persist-credentials: false', workflow)
        self.assertIn('VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}', workflow)
        self.assertIn('contents: read', workflow)
        self.assertIn('actions: read', workflow)
        self.assertIn('name: publisher-access-receipt', workflow)
        self.assertIn('if-no-files-found: error', workflow)
        self.assertIn('Remove ephemeral publisher credentials', workflow)
        full_ci = (Path(__file__).resolve().parents[2] / '.github/workflows/web.yml').read_text()
        self.assertIn("python3 -m unittest discover -s ops/ci -p 'test_*.py'", full_ci)

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
                    client.pin_verified_team()
                    self.assertEqual(json.loads((root / 'config.json').read_text()), {
                        'currentTeam': TEAM_ID, 'cachedTeamIds': {'pikeholdings': TEAM_ID},
                    })
                    client.cli(['api', '/v9/projects/' + PROJECT_ID, '--raw'])
            self.assertFalse(root.exists())
            self.assertNotIn('fictional-vercel', calls[0][0])
            self.assertNotIn('--scope', calls[0][0])
            for key in ['GH_TOKEN', 'SMP_AUTH_STORE_TOKEN', 'OPENAI_API_KEY', 'VERCEL_TOKEN', 'CODEX_HOME']:
                self.assertNotIn(key, calls[0][1])

    def test_stage_runner_sanitizes_inherited_credentials_and_cli_failure(self):
        with patch.dict(os.environ, {'GH_TOKEN': 'fictional-gh', 'SMP_CODEX_AUTH_JSON': 'fictional-auth',
                                     'VERCEL_TOKEN': 'fictional-vercel'}), patch('publisher_probe.subprocess.run') as runner:
            runner.return_value = SimpleNamespace(returncode=1, stdout='fictional-vercel', stderr='Error: Not able to load user')
            with self.assertRaisesRegex(RuntimeError, '^VERCEL_PREBUILT_STAGE_FAILED_USER_LOOKUP$'):
                PublisherAuth.isolated_runner(['vercel', 'deploy'], env=dict(os.environ))
            env = runner.call_args.kwargs['env']
            for key in ['GH_TOKEN', 'SMP_CODEX_AUTH_JSON', 'VERCEL_TOKEN']:
                self.assertNotIn(key, env)

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
