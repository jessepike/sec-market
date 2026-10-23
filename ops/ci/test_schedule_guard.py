import unittest
from schedule_guard import allowed, ACCEPTANCE_CRONS


class SchedulerAcceptanceTests(unittest.TestCase):
    def test_actual_temporary_schedule_runs_only_on_accepted_utc_date(self):
        for cron in ACCEPTANCE_CRONS:
            self.assertTrue(allowed('schedule', cron, '2026-10-23'))
            for day in ('2026-10-22', '2026-10-24', '2027-10-23'):
                self.assertFalse(allowed('schedule', cron, day))

    def test_regular_schedule_and_manual_requests_remain_available(self):
        self.assertTrue(allowed('schedule', '17 5 * * *', '2027-10-23'))
        self.assertTrue(allowed('workflow_dispatch', '', '2027-10-23'))
        self.assertTrue(allowed('push', '', '2027-10-23'))
