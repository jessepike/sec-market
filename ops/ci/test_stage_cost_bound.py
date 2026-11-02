"""Ordinary publisher safety at real CLI/storage boundaries, without provider calls."""
import json
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from storage import LocalStore
from vercel import MAX_STAGE_BYTES, VercelAdapter
from publication import publish


class StageCostBoundTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(self.temp.name)
        self.calls = []
        self.state = 'READY'
        self.cancel_state = 'CANCELED'
        self.metadata = {'smpReleaseId': 'e'*64, 'smpAppRevision': 'a'*40, 'smpArtifactSha256': 'b'*64}
        self.manifest = {'releaseId': 'e'*64, 'appRevision': 'a'*40, 'artifact': {'sha256': 'b'*64},
                         'snapshot': {'sha256': 'c'*64}, 'contractSha256': 'd'*64}
        self.adapter = VercelAdapter(self.store, 'prj_123', 'team_123', 'pikeholdings', runner=self.runner)

    def identity(self):
        return {'id': 'dpl_123', 'url': 'exact.vercel.app', 'projectId': 'prj_123',
                'target': 'production', 'readyState': self.state, 'meta': self.metadata}

    def project(self):
        return {'id': 'prj_123', 'accountId': 'team_123', 'resourceConfig': {
            'buildMachineType': 'basic', 'buildMachineSelection': 'fixed', 'elasticConcurrencyEnabled': False}}

    def runner(self, args, **kwargs):
        self.calls.append((args, kwargs))
        if args[1] == 'deploy':
            self.assertEqual(kwargs['timeout'], 30)
            return SimpleNamespace(returncode=0, stdout='https://exact.vercel.app', stderr='')
        self.assertIn('teamId=team_123', args[2])
        self.assertEqual(kwargs['timeout'], 10)
        if '/v9/projects/' in args[2]:
            return SimpleNamespace(returncode=0, stdout=json.dumps(self.project()), stderr='')
        if '/cancel?' in args[2]:
            self.assertIn('PATCH', args)
            self.state = self.cancel_state
        return SimpleNamespace(returncode=0, stdout=json.dumps(self.identity()), stderr='')

    def stage(self, checkpoint=None):
        with patch('vercel.stage_files', return_value={'config.json': b'{"version":3}', 'static/index.html': b'exact'}):
            return self.adapter.stage(self.manifest, checkpoint=checkpoint)

    def test_ready_stage_is_nonblocking_metadata_pinned_and_checkpointed(self):
        saved = []
        self.assertEqual(self.stage(lambda: saved.append(self.store.read('deployment-creations/'+'e'*64+'.json'))),
                         'https://exact.vercel.app')
        command = next(args for args, _ in self.calls if args[1] == 'deploy')
        self.assertIn('--no-wait', command)
        self.assertIn('--skip-domain', command)
        self.assertIn('--target=production', command)
        self.assertNotIn('--prod', command)
        for key, value in self.metadata.items():
            self.assertIn(key+'='+value, command)
        self.assertEqual(saved[0]['deploymentId'], 'https://exact.vercel.app')
        self.assertEqual(saved[0]['nativeId'], 'dpl_123')
        self.assertEqual(saved[0]['staticBytes'], 18)
        self.assertIsNone(self.store.read('deployment-attempts/'+'e'*64+'.json'))

    def test_total_exact_static_bytes_rejected_before_provider_creation(self):
        with patch('vercel.stage_files', return_value={'static/index.html': b'x'*MAX_STAGE_BYTES, 'config.json': b'x'}):
            with self.assertRaisesRegex(ValueError, 'VERCEL_STATIC_STAGE_BYTE_LIMIT'):
                self.adapter.stage(self.manifest)
        self.assertEqual(self.calls, [])

    def test_native_identity_mismatch_never_cancels_or_promotes_a_foreign_build(self):
        for field, value in [('id', 'wrong'), ('projectId', 'prj_other'), ('url', 'other.vercel.app'),
                             ('target', 'preview'), ('meta', {}), ('readyState', 'MYSTERY')]:
            with self.subTest(field=field), patch.object(self.adapter, '_cli', side_effect=[
                json.dumps(self.project()), 'https://exact.vercel.app', json.dumps({**self.identity(), field: value})]):
                with self.assertRaisesRegex(ValueError, 'VERCEL_STAGE_CREATED_IDENTITY_UNVERIFIED'):
                    self.stage()
        self.assertIsNone(self.store.read('deployment-creations/'+'e'*64+'.json'))

    def test_expired_stage_requests_one_scoped_cancel_and_reads_terminal_ack(self):
        self.state = 'BUILDING'
        with patch('vercel.time.monotonic', side_effect=[0, 91]):
            with self.assertRaisesRegex(ValueError, '^VERCEL_STAGE_DEADLINE_EXCEEDED$'):
                self.stage()
        self.assertEqual(sum('/cancel?' in args[2] for args, _ in self.calls if args[1]=='api'), 1)
        self.assertEqual(self.state, 'CANCELED')
        self.assertIsNone(self.adapter.pending)

    def test_late_ready_is_held_without_canceling_terminal_deployment(self):
        with patch('vercel.time.monotonic', side_effect=[0, 91]):
            with self.assertRaisesRegex(ValueError, 'VERCEL_STAGE_STOP_OUTCOME_UNKNOWN'):
                self.stage()
        self.assertFalse(any('/cancel?' in args[2] for args, _ in self.calls if args[1]=='api'))
        self.assertIsNone(self.adapter.pending)

    def test_cancel_ack_lost_or_not_terminal_holds_without_retry(self):
        self.state = 'BUILDING'
        self.cancel_state = 'BUILDING'
        with patch('vercel.time.monotonic', side_effect=[0, 91]):
            with self.assertRaisesRegex(ValueError, 'VERCEL_STAGE_STOP_OUTCOME_UNKNOWN'):
                self.stage()
        self.assertEqual(sum(args[1]=='deploy' for args, _ in self.calls), 1)
        self.assertEqual(sum('/cancel?' in args[2] for args, _ in self.calls if args[1]=='api'), 1)

    def test_cancel_lost_response_is_reconciled_by_native_terminal_readback(self):
        self.state = 'BUILDING'
        calls = []
        def cli(args, **_kwargs):
            calls.append(args)
            if '/cancel' in args[1]:
                self.state = 'CANCELED'
                raise subprocess.TimeoutExpired('redacted', 10)
            return json.dumps(self.identity())
        with patch.object(self.adapter, '_cli', side_effect=cli):
            self.adapter._cancel_stage('https://exact.vercel.app', self.metadata, 'production', 'dpl_123')
        self.assertEqual(len(calls), 3)
        self.assertEqual(sum('/cancel' in args[1] for args in calls), 1)

    def test_lost_creation_response_does_not_repeat_or_guess_cancel_identity(self):
        with patch.object(self.adapter, '_cli', side_effect=[json.dumps(self.project()), subprocess.TimeoutExpired('redacted',30)]) as cli:
            with self.assertRaisesRegex(ValueError, 'VERCEL_STAGE_CREATION_OUTCOME_UNKNOWN'):
                self.stage()
        self.assertEqual(cli.call_count, 2)

    def test_failed_initial_identity_lookup_retains_untrusted_url_without_cancel_authority(self):
        with patch.object(self.adapter, '_cli', side_effect=[json.dumps(self.project()),
                'https://exact.vercel.app', OSError('native read unavailable')]) as cli:
            with self.assertRaisesRegex(ValueError, 'VERCEL_STAGE_CREATED_IDENTITY_UNVERIFIED'):
                self.stage()
        self.assertEqual(cli.call_count, 3)
        self.assertEqual(self.store.read('deployment-create-responses/'+'e'*64+'.json'),
                         {'deploymentUrlHint': 'https://exact.vercel.app', 'identityVerified': False})
        self.assertIsNone(self.store.read('deployment-creations/'+'e'*64+'.json'))
        self.assertIsNone(self.store.read('deployment-attempts/'+'e'*64+'.json'))

    def test_checkpoint_failure_cancels_known_scoped_build(self):
        self.state = 'BUILDING'
        def fail():
            raise OSError('checkpoint unavailable')
        with self.assertRaisesRegex(OSError, 'checkpoint unavailable'):
            self.stage(fail)
        self.assertEqual(self.state, 'CANCELED')

    def test_ready_without_checkpoint_on_time_still_preserves_identity(self):
        self.stage()
        self.assertEqual(self.store.read('deployment-creations/'+'e'*64+'.json')['deploymentId'], 'https://exact.vercel.app')
        self.assertIsNone(self.store.read('deployment-attempts/'+'e'*64+'.json'))

    def test_remote_attempt_survives_lost_create_response_and_prevents_recreation(self):
        self.store.compare_and_swap('production', None, {'releaseId': 'old', 'sequence': 1, 'deploymentId': 'old'})
        manifest = {**self.manifest, 'createdAt': '2026-11-02T19:00:00Z', 'parentReleaseId': 'old', 'sequence': 2}
        contract = {'publication': {'enabled': True, 'maxBatchesPerDay': 2}}
        remote = []
        def checkpoint():
            remote.append({'manifest': self.store.read('release-attempts/'+'e'*64+'.json'),
                           'budget': self.store.read('heads/publication-budget-2026-11-02.json')})
        def lost_create(*_args, **_kwargs):
            self.assertEqual(remote[0]['manifest'], manifest)
            self.assertEqual(remote[0]['budget']['attempts'], ['e'*64])
            raise subprocess.TimeoutExpired('redacted', 30)
        with patch.object(self.adapter, 'production_paths_controlled', return_value=True), \
             patch.object(self.adapter, '_cli', side_effect=lost_create) as cli, \
             patch.object(self.adapter, '_stage_build_settings'), \
             patch('vercel.stage_files', return_value={'static/index.html': b'exact'}):
            with self.assertRaisesRegex(ValueError, 'VERCEL_STAGE_CREATION_OUTCOME_UNKNOWN'):
                publish(self.store, contract, manifest, self.adapter, checkpoint)
            with self.assertRaisesRegex(ValueError, 'already attempted'):
                publish(self.store, contract, manifest, self.adapter, checkpoint)
        self.assertEqual(cli.call_count, 1)

    def test_unknown_or_nonbasic_settings_fail_before_creation(self):
        good = self.project()
        variants = [[], {}, {**good, 'resourceConfig': None}, {**good, 'id': 'prj_other'}, {**good, 'accountId': 'team_other'}]
        for field, value in [('buildMachineType', 'turbo'), ('buildMachineSelection', 'elastic'),
                             ('elasticConcurrencyEnabled', True), ('elasticConcurrencyEnabled', None)]:
            variants.append({**good, 'resourceConfig': {**good['resourceConfig'], field: value}})
        for project in variants:
            with self.subTest(project=project), patch.object(self.adapter, '_cli', return_value=json.dumps(project)) as cli:
                with self.assertRaisesRegex(ValueError, 'VERCEL_STAGE_FIXED_BASIC_SETTINGS_REQUIRED'):
                    self.stage()
                self.assertEqual(cli.call_count, 1)

    def test_failed_remote_precreate_checkpoint_performs_no_provider_creation(self):
        self.store.compare_and_swap('production', None, {'releaseId': 'old', 'sequence': 1, 'deploymentId': 'old'})
        manifest = {**self.manifest, 'createdAt': '2026-11-02T19:00:00Z', 'parentReleaseId': 'old', 'sequence': 2}
        def checkpoint():
            raise OSError('remote checkpoint unavailable')
        with patch.object(self.adapter, 'production_paths_controlled', return_value=True), \
             patch.object(self.adapter, 'stage') as stage:
            with self.assertRaisesRegex(OSError, 'checkpoint unavailable'):
                publish(self.store, {'publication': {'enabled': True}}, manifest, self.adapter, checkpoint)
        stage.assert_not_called()

    def test_only_preview_git_deployments_are_enabled_before_build_allocation(self):
        # Pin the provider-native rule, not a second implementation of its
        # minimatch semantics. ** also covers refs containing slashes; exact
        # preview is the sole true exception under Vercel's documented rules.
        config = json.loads((Path(__file__).resolve().parents[2] / 'web/vercel.json').read_text())
        self.assertEqual(config['git']['deploymentEnabled'], {'**': False, 'preview': True})


if __name__ == '__main__':
    unittest.main()
