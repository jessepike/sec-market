import unittest
from unittest.mock import patch

from job_alert import notify


class JobAlertTests(unittest.TestCase):
    @patch('job_alert.api')
    def test_failure_assigns_owner_and_links_actual_run(self, api):
        api.side_effect = [[], {'number': 9, 'state': 'open', 'html_url': 'https://github.com/issue/9'}]
        result = notify('collector', 'failure', '123')
        payload = api.call_args.args[1]
        self.assertEqual(payload['assignees'], ['jessepike'])
        self.assertIn('/actions/runs/123', payload['body'])
        self.assertEqual(result['state'], 'open')

    @patch('job_alert.api')
    def test_recovery_closes_existing_alert(self, api):
        api.side_effect = [[{'title': 'Daily market collector needs attention', 'number': 9}],
                           {'number': 9, 'state': 'closed', 'html_url': 'https://github.com/issue/9'}]
        notify('collector', 'success', 124)
        self.assertEqual(api.call_args.args[1]['state'], 'closed')
        self.assertIn('recovered', api.call_args.args[1]['body'])

    @patch('job_alert.api', return_value=[])
    def test_success_without_prior_failure_is_quiet(self, api):
        self.assertEqual(notify('publisher', 'success', 125), {'delivery': 'no_alert_needed'})
        self.assertEqual(api.call_count, 1)

    def test_untrusted_run_id_rejected_before_remote_call(self):
        with self.assertRaisesRegex(ValueError, 'INVALID_JOB_ALERT_INPUT'):
            notify('collector', 'failure', '123?token=bad')
