"""Which collector runs count as the trusted daily timer.

GitHub's own `schedule` event is often hours late, so the owner approved an
outside clock (Vercel Cron, 2026-11-03) that starts the collector through
`workflow_dispatch` with the `timer` input. Both routes are trusted. Any other
manual dispatch stays a diagnostic run and never counts as the daily timer.

A dispatched timer run is recognised three ways that must agree: the event is
`workflow_dispatch`, the run title is TIMER_TITLE (set by `run-name` from the
`timer` input), and the archived receipt records `githubTimer: true`.
"""
import os

COLLECTOR_PATH = '.github/workflows/subscription-collector.yml'
TIMER_TITLE = 'daily timer collection'
# Primary GitHub schedule plus one backup. Both skip when the day already ran.
DAILY_CRONS = frozenset({'17 5 * * *', '47 9 * * *'})


def trusted_event(event, title=None):
    return event == 'schedule' or (event == 'workflow_dispatch' and title == TIMER_TITLE)


def trusted_run(run):
    """A GitHub API run object for the collector started by a trusted timer."""
    return (run.get('path') == COLLECTOR_PATH
            and trusted_event(run.get('event'), run.get('display_title')))


def trusted_clock(clock):
    """An archived collection receipt written by a trusted timer run."""
    event = clock.get('githubEventName')
    return event == 'schedule' or (event == 'workflow_dispatch' and clock.get('githubTimer') is True)


def timer_dispatch(env=None):
    env = os.environ if env is None else env
    return env.get('GITHUB_EVENT_NAME') == 'workflow_dispatch' and env.get('SMP_TIMER') == 'true'


def trusted_environment(env=None):
    """This runner was started by the daily timer on main."""
    env = os.environ if env is None else env
    if env.get('GITHUB_REF') != 'refs/heads/main':
        return False
    if env.get('GITHUB_EVENT_NAME') == 'schedule':
        return env.get('SMP_EVENT_SCHEDULE') in DAILY_CRONS
    return timer_dispatch(env)
