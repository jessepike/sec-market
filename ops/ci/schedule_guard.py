#!/usr/bin/env python3
"""Bound the temporary real scheduler acceptance to one UTC date."""
import os
from datetime import datetime, timezone

ACCEPTANCE_CRON = '7 6 23 10 *'
ACCEPTANCE_DATE = '2026-10-23'


def allowed(event, schedule, utc_date):
    return not (event == 'schedule' and schedule == ACCEPTANCE_CRON) or utc_date == ACCEPTANCE_DATE


if __name__ == '__main__':
    run = allowed(os.environ['SMP_EVENT_NAME'], os.environ.get('SMP_EVENT_SCHEDULE', ''),
                  datetime.now(timezone.utc).date().isoformat())
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
        output.write('allowed=' + str(run).lower() + '\n')
    print('Temporary scheduler acceptance allowed.' if run else 'Temporary scheduler acceptance expired; collection skipped.')
