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


class DailyTimerSkipTests(unittest.TestCase):
    PATH = '.github/workflows/subscription-collector.yml'

    def api(self, runs, jobs):
        def call(path):
            if path.startswith('actions/workflows/'):
                return {'workflow_runs': runs}
            return {'jobs': jobs.get(path.split('/')[2], [])}
        return call

    def run_of(self, run_id, event='schedule', title='bounded subscription collector', day='2026-11-04', conclusion='success'):
        return {'id': run_id, 'path': self.PATH, 'event': event, 'display_title': title, 'head_branch': 'main',
                'created_at': day + 'T05:18:00Z', 'conclusion': conclusion}

    def env(self, **extra):
        return {'SMP_EVENT_NAME': 'schedule', 'SMP_EVENT_SCHEDULE': '47 9 * * *', 'GITHUB_REF': 'refs/heads/main',
                'GITHUB_RUN_ID': '900', **extra}

    def test_backup_skips_after_outside_timer_collected_today(self):
        from schedule_guard import decide
        runs = [self.run_of(1, 'workflow_dispatch', 'daily timer collection')]
        jobs = {'1': [{'name': 'collect-and-reconcile', 'conclusion': 'success'}]}
        allowed_now, _ = decide(self.env(), '2026-11-04', self.api(runs, jobs))
        self.assertFalse(allowed_now)

    def test_backup_still_collects_when_earlier_timer_failed_skipped_or_was_yesterday(self):
        from schedule_guard import decide
        cases = [([self.run_of(1, conclusion='failure')], {}),
                 ([self.run_of(1)], {'1': [{'name': 'collect-and-reconcile', 'conclusion': 'skipped'}]}),
                 ([self.run_of(1, day='2026-11-03')], {'1': [{'name': 'collect-and-reconcile', 'conclusion': 'success'}]}),
                 ([self.run_of(1, 'workflow_dispatch')], {'1': [{'name': 'collect-and-reconcile', 'conclusion': 'success'}]})]
        for runs, jobs in cases:
            self.assertTrue(decide(self.env(), '2026-11-04', self.api(runs, jobs))[0])

    def test_manual_diagnostics_are_not_blocked_and_timer_cannot_be_a_probe(self):
        from schedule_guard import decide
        boom = lambda path: (_ for _ in ()).throw(AssertionError('no API call expected'))
        self.assertTrue(decide(self.env(SMP_EVENT_NAME='workflow_dispatch', SMP_EVENT_SCHEDULE=''), '2026-11-04', boom)[0])
        with self.assertRaises(RuntimeError):
            decide(self.env(SMP_EVENT_NAME='workflow_dispatch', SMP_TIMER='true', SMP_SOURCE_PROBE='true'), '2026-11-04', boom)
