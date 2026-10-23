import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from stage_gate import execute, validate_request


class PreviewGateBoundaryTests(unittest.TestCase):
    def request(self):
        return {'operation': 'stage_verified_preview_gate', 'gateRunId': 123, 'artifactId': 456,
                'archiveCommit': 'a'*40, 'manifestSha256': 'b'*64}

    def test_archive_pin_and_actual_provenance_ids_required(self):
        self.assertEqual(validate_request(self.request())['commit'], 'a'*40)
        for field, value in [('gateRunId', True), ('artifactId', '456'), ('archiveCommit', 'bad'),
                             ('manifestSha256', 'b'*64+'\nref=main')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_request({**self.request(), field: value})

    def test_main_cannot_reach_artifact_import_or_publisher_credential(self):
        with patch.dict(os.environ, {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'jessepike/sec-market',
                                     'GITHUB_REF': 'refs/heads/main'}, clear=True), patch('stage_gate.import_gate') as imported:
            with self.assertRaisesRegex(ValueError, 'PREVIEW_BRANCH_REQUIRED'):
                execute('/tmp/fictional-stage', self.request())
            imported.assert_not_called()

    def test_non_actions_context_cannot_stage(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(ValueError, 'PRIVATE_GITHUB_RUNNER_REQUIRED'):
            execute('/tmp/fictional-stage', self.request())

    def test_verified_artifact_is_staged_only_as_preview_and_never_promoted(self):
        inputs = {'snapshot': {'sha256': 's'}, 'artifact': {'sha256': 'x'},
                  'coverage': {'complete': False, 'successfulTasks': 244, 'requiredTasks': 557, 'runId': 'run'}}
        receipt = {'appRevision': 'c'*40, 'contractSha256': 'd'*64}
        with tempfile.TemporaryDirectory() as directory, \
             patch.dict(os.environ, {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'jessepike/sec-market',
                                     'GITHUB_REF': 'refs/heads/preview', 'VERCEL_TOKEN': 'fictional'}, clear=True), \
             patch('stage_gate.GitHubAuthority') as authority, \
             patch('stage_gate.import_gate', return_value=(inputs, receipt)), \
             patch('stage_gate.PublisherAuth') as auth, patch('stage_gate.VercelAdapter') as adapter_class, \
             patch('stage_gate.stage_files', return_value={}), patch('stage_gate.verify_files', return_value=[]):
            from stage_gate import PROJECT_ID, TEAM_ID
            auth.return_value.__enter__.return_value.cli.return_value = '{"id":"' + PROJECT_ID + '","accountId":"' + TEAM_ID + '"}'
            adapter = adapter_class.return_value
            adapter.site = 'https://securitymarketpulse.com'
            adapter._get.return_value = {'appRevision': 'e'*40}
            adapter.stage.return_value = 'https://exact.vercel.app'
            adapter.pending = {'ready': True}
            adapter.probe.return_value = adapter.pending
            result = execute(Path(directory)/'fresh', self.request())
            authority.assert_called_once_with(branch='preview')
            self.assertEqual(adapter.stage.call_args.args[0]['mode'], 'stage_only_smoke_test')
            self.assertFalse(result['coverage']['complete'])
            self.assertTrue(result['productionUnchanged'])
            adapter.promote.assert_not_called()
            adapter.rollback.assert_not_called()
