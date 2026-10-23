#!/usr/bin/env python3
"""Report runner failures and recovery through an owner-assigned GitHub issue."""
import argparse
import json
import os
import subprocess

REPO = 'jessepike/sec-market'


def api(path, payload=None, runner=subprocess.run):
    args = ['gh', 'api', 'repos/' + REPO + '/' + path]
    if payload is not None:
        args += ['--method', 'PATCH' if path.startswith('issues/') else 'POST', '--input', '-']
    result = runner(args, input=json.dumps(payload) if payload is not None else None,
                    capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise RuntimeError('GITHUB_PIPELINE_ALERT_FAILED')
    return json.loads(result.stdout)


def notify(job, status, run_id):
    if job not in ('collector', 'publisher') or status not in ('success', 'failure', 'cancelled') or not str(run_id).isdigit():
        raise ValueError('INVALID_JOB_ALERT_INPUT')
    title = 'Daily market ' + job + ' needs attention'
    issues = api('issues?state=open&per_page=100&sort=updated&direction=desc')
    existing = next((i for i in issues if i.get('title') == title and 'pull_request' not in i), None)
    if status == 'success' and not existing:
        return {'delivery': 'no_alert_needed'}
    url = 'https://github.com/' + REPO + '/actions/runs/' + str(run_id)
    body = ('The daily ' + job + (' recovered.' if status == 'success' else ' did not finish successfully.')
            + '\n\n[Runner receipt and logs](' + url + '). Runner result: ' + status + '.'
            + '\n\nIncomplete coverage stays incomplete. A successful runner alone does not prove publication, full coverage or phone/email delivery.')
    if existing:
        sent = api('issues/' + str(existing['number']), {'body': body, 'state': 'closed' if status == 'success' else 'open'})
    else:
        sent = api('issues', {'title': title, 'body': body, 'assignees': ['jessepike']})
    return {'delivery': 'github_issue_updated', 'number': sent['number'], 'state': sent['state'], 'url': sent['html_url']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', required=True, choices=['collector', 'publisher'])
    parser.add_argument('--status', required=True, choices=['success', 'failure', 'cancelled'])
    args = parser.parse_args()
    print(json.dumps(notify(args.job, args.status, os.environ['GITHUB_RUN_ID'])))
