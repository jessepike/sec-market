import os
import unittest
from unittest.mock import patch, MagicMock

import publish


class PublisherBoundaryTests(unittest.TestCase):
    def test_fixed_stage_failures_preserve_unknown_outcome_without_remote_text(self):
        for reason in ['VERCEL_STATIC_STAGE_BYTE_LIMIT', 'VERCEL_STAGE_FIXED_BASIC_SETTINGS_REQUIRED',
                       'VERCEL_STAGE_CREATION_OUTCOME_UNKNOWN', 'VERCEL_STAGE_CREATED_IDENTITY_UNVERIFIED',
                       'VERCEL_STAGE_NATIVE_IDENTITY_DIFFERS', 'VERCEL_STAGE_STATE_UNKNOWN',
                       'VERCEL_STAGE_TERMINAL_FAILURE', 'VERCEL_STAGE_DEADLINE_EXCEEDED',
                       'VERCEL_STAGE_STOP_OUTCOME_UNKNOWN']:
            self.assertEqual(publish.safe_failure_reason(ValueError(reason)), reason)
            self.assertEqual(publish.safe_failure_reason(ValueError(reason+' secret remote detail')), 'PUBLISHER_FAILED')

    def test_callback_rejects_dispatch_and_busy_collectors_before_writer_queue(self):
        run = {'id': 123, 'repository': {'full_name': 'jessepike/sec-market', 'private': True},
               'path': '.github/workflows/subscription-collector.yml', 'head_branch': 'main',
               'event': 'schedule', 'status': 'completed', 'conclusion': 'success'}
        event = {'workflow_run': {'id': 123}}
        api = lambda path: {'workflow_runs': []} if 'workflows/' in path else run
        self.assertTrue(publish.callback_ready(event, api))
        run['event'] = 'workflow_dispatch'
        self.assertFalse(publish.callback_ready(event, api))
        run['event'] = 'schedule'
        busy_api = lambda path: {'workflow_runs': [{'status': 'queued'}]} if 'workflows/' in path else run
        self.assertFalse(publish.callback_ready(event, busy_api))

    def test_initial_hold_finishes_lease_without_auth_or_gate_and_valid_source_continues(self):
        os.environ.update(GITHUB_RUN_ID='123', VERCEL_TOKEN='test-token', GITHUB_EVENT_NAME='schedule')
        for ready in (False, True):
            os.environ['VERCEL_TOKEN'] = 'test-token'
            state, root = MagicMock(), MagicMock()
            with patch.object(publish, 'validate_contract', return_value={'publication': {'enabled': True}}), \
                 patch.object(publish, 'recover'), patch.object(publish.session_runtime, 'git', return_value='a'*40), \
                 patch.object(publish.session_runtime, 'bootstrap'), \
                 patch.object(publish, 'LocalStore', side_effect=[state, root]), \
                 patch.object(publish, 'initial_collection_ready', return_value=ready), \
                 patch.object(publish.session_runtime, 'checkpoint', return_value={'archive': {}}) as checkpoint, \
                 patch.object(publish, 'PublisherAuth') as auth, patch.object(publish, 'release_daily', return_value={'published': True}) as release:
                auth.return_value.__enter__.return_value.cli.return_value = publish.json.dumps({'id': publish.PROJECT_ID, 'accountId': publish.TEAM_ID})
                result = publish.execute('/tmp/fictional-publisher')
                self.assertTrue(checkpoint.call_args.kwargs['finish'])
                if ready:
                    release.assert_called_once()
                    self.assertTrue(result['publication']['published'])
                else:
                    release.assert_not_called()
                    auth.assert_not_called()
                    self.assertEqual(result['reason'], 'WAITING_ACTUAL_SCHEDULED_COLLECTION')
                    self.assertFalse(result['published'])

    def test_only_initial_baseline_requires_verified_scheduled_source(self):
        state = MagicMock()
        with patch.object(publish, 'verified_scheduled_source', return_value=None) as verify:
            state.read.return_value = {'legacyBaseline': True}
            self.assertFalse(publish.initial_collection_ready(state, {}))
            verify.assert_called_once()
            state.read.return_value = {'releaseId': 'daily'}
            self.assertTrue(publish.initial_collection_ready(state, {}))
            self.assertEqual(verify.call_count, 1)
            state.read.return_value = {'legacyBaseline': True}
            verify.return_value = {'githubRunId': 123}
            self.assertFalse(publish.initial_collection_ready(state, {}, upstream_id=124))
            self.assertTrue(publish.initial_collection_ready(state, {}, upstream_id=123))

    def test_failure_receipt_retains_only_fixed_local_error_categories(self):
        self.assertEqual(publish.safe_failure_reason(RuntimeError('VERCEL_PROMOTION_FAILED_USER_LOOKUP')),
                         'VERCEL_PROMOTION_FAILED_USER_LOOKUP')
        self.assertEqual(publish.safe_failure_reason(RuntimeError('remote secret sensitive')),'PUBLISHER_FAILED')
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
