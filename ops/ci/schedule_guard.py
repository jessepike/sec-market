#!/usr/bin/env python3
"""Decide whether this collector run may collect.

1. The temporary scheduler acceptance crons are bound to one UTC date.
2. A daily timer run (GitHub schedule or the outside Vercel Cron dispatch)
   skips when another timer run already collected successfully today, so the
   primary clock and its backups never collect twice in one UTC day.
"""
import json
import os
import subprocess
from datetime import datetime, timezone

import timer

ACCEPTANCE_CRON = '7 6 23 10 *'
ACCEPTANCE_CRONS = {ACCEPTANCE_CRON, '7 7 23 10 *'}
ACCEPTANCE_DATE = '2026-10-23'
PROJECT = 'jessepike/sec-market'


def allowed(event, schedule, utc_date):
    return not (event == 'schedule' and schedule in ACCEPTANCE_CRONS) or utc_date == ACCEPTANCE_DATE


def collected_today(runs, jobs_for, utc_date, own_id):
    """Another trusted timer run on main collected successfully on this UTC date."""
    for run in runs:
        if str(run.get('id')) == str(own_id) or run.get('head_branch') != 'main' or not timer.trusted_run(run):
            continue
        if run.get('created_at', '')[:10] != utc_date or run.get('conclusion') != 'success':
            continue
        if any(j.get('name') == 'collect-and-reconcile' and j.get('conclusion') == 'success'
               for j in jobs_for(run['id'])):
            return True
    return False


def github_api(path):
    response = subprocess.run(['gh', 'api', f'repos/{PROJECT}/{path}'], capture_output=True, text=True, timeout=60)
    if response.returncode:
        raise RuntimeError('SCHEDULE_GUARD_GITHUB_API_FAILED')
    return json.loads(response.stdout)


def decide(env, utc_date, api=github_api):
    event, schedule = env['SMP_EVENT_NAME'], env.get('SMP_EVENT_SCHEDULE', '')
    if not allowed(event, schedule, utc_date):
        return False, 'Temporary scheduler acceptance expired; collection skipped.'
    if env.get('SMP_TIMER') == 'true' and env.get('SMP_SOURCE_PROBE') == 'true':
        raise RuntimeError('TIMER_AND_SOURCE_PROBE_ARE_EXCLUSIVE')
    is_timer = (event == 'schedule' and schedule in timer.DAILY_CRONS) or \
        (event == 'workflow_dispatch' and env.get('SMP_TIMER') == 'true')
    if is_timer and env.get('GITHUB_REF') == 'refs/heads/main':
        runs = api('actions/workflows/subscription-collector.yml/runs?branch=main&per_page=30')['workflow_runs']
        jobs_for = lambda run_id: api(f'actions/runs/{run_id}/jobs?per_page=20').get('jobs', [])
        if collected_today(runs, jobs_for, utc_date, env.get('GITHUB_RUN_ID')):
            return False, 'Today already has a successful timer collection; this backup start skipped.'
    return True, 'Collection allowed.'


if __name__ == '__main__':
    run, message = decide(os.environ, datetime.now(timezone.utc).date().isoformat())
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
        output.write('allowed=' + str(run).lower() + '\n')
    print(message)
