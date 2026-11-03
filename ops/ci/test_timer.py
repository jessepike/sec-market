import unittest

import timer

PATH = '.github/workflows/subscription-collector.yml'


class TrustedTimerTests(unittest.TestCase):
    def test_schedule_and_titled_timer_dispatch_are_trusted(self):
        self.assertTrue(timer.trusted_run({'path': PATH, 'event': 'schedule'}))
        self.assertTrue(timer.trusted_run({'path': PATH, 'event': 'workflow_dispatch', 'display_title': timer.TIMER_TITLE}))

    def test_plain_dispatch_other_workflows_and_other_events_are_not(self):
        for run in ({'path': PATH, 'event': 'workflow_dispatch', 'display_title': 'bounded subscription collector'},
                    {'path': PATH, 'event': 'push', 'display_title': timer.TIMER_TITLE},
                    {'path': '.github/workflows/web.yml', 'event': 'schedule'}):
            self.assertFalse(timer.trusted_run(run))

    def test_archived_clock_needs_explicit_timer_flag_for_dispatch(self):
        self.assertTrue(timer.trusted_clock({'githubEventName': 'schedule'}))
        self.assertTrue(timer.trusted_clock({'githubEventName': 'workflow_dispatch', 'githubTimer': True}))
        for clock in ({'githubEventName': 'workflow_dispatch'}, {'githubEventName': 'workflow_dispatch', 'githubTimer': 'true'},
                      {'githubEventName': 'push', 'githubTimer': True}):
            self.assertFalse(timer.trusted_clock(clock))
