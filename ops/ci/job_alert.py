#!/usr/bin/env python3
"""Report runner failures and recovery through a workflow annotation.

Issues live in the private repository (jessepike/sec-market-private), which the
workflow token cannot write. The hourly outside health check (ops/timer) already
alerts the owner there when the collector or publisher fails, and reads this
annotation for the failure detail.
"""
import argparse
import json
import os
import sys

REPO = 'jessepike/sec-market'
ANNOTATION = 'pipeline-job'


def notify(job, status, run_id, stream=None):
    if job not in ('collector', 'publisher') or status not in ('success', 'failure', 'cancelled') or not str(run_id).isdigit():
        raise ValueError('INVALID_JOB_ALERT_INPUT')
    stream = stream or sys.stderr
    url = 'https://github.com/' + REPO + '/actions/runs/' + str(run_id)
    if status == 'success':
        return {'delivery': 'no_alert_needed'}
    message = ('The daily ' + job + ' did not finish successfully. Runner result: ' + status + '. ' + url
               + '. Incomplete coverage stays incomplete. A successful runner alone does not prove publication or full coverage.')
    print('::error title=' + ANNOTATION + '::' + message, file=stream)
    return {'delivery': 'workflow_annotation', 'title': ANNOTATION, 'job': job, 'state': 'open', 'url': url}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', required=True, choices=['collector', 'publisher'])
    parser.add_argument('--status', required=True, choices=['success', 'failure', 'cancelled'])
    args = parser.parse_args()
    print(json.dumps(notify(args.job, args.status, os.environ['GITHUB_RUN_ID'])))
