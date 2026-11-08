import io
import unittest

from job_alert import notify


class JobAlertTests(unittest.TestCase):
    def test_failure_writes_an_error_annotation_linking_the_actual_run(self):
        stream = io.StringIO()
        result = notify('collector', 'failure', '123', stream)
        self.assertTrue(stream.getvalue().startswith('::error title=pipeline-job::The daily collector'))
        self.assertIn('/actions/runs/123', stream.getvalue())
        self.assertEqual(result['state'], 'open')
        self.assertEqual(result['delivery'], 'workflow_annotation')

    def test_success_is_quiet_and_writes_nothing(self):
        stream = io.StringIO()
        self.assertEqual(notify('publisher', 'success', 125, stream), {'delivery': 'no_alert_needed'})
        self.assertEqual(stream.getvalue(), '')

    def test_cancelled_is_reported(self):
        stream = io.StringIO()
        self.assertEqual(notify('publisher', 'cancelled', 126, stream)['state'], 'open')
        self.assertIn('Runner result: cancelled', stream.getvalue())

    def test_untrusted_run_id_rejected(self):
        with self.assertRaisesRegex(ValueError, 'INVALID_JOB_ALERT_INPUT'):
            notify('collector', 'failure', '123?token=bad')

    def test_no_github_write_path_remains(self):
        import job_alert
        self.assertFalse(hasattr(job_alert, 'api'))
        self.assertFalse(hasattr(job_alert, 'subprocess'))


if __name__ == '__main__':
    unittest.main()
