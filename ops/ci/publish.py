#!/usr/bin/env python3
"""Publish acknowledged evidence through the independent exact-artifact gate."""
import argparse
import json
import os
from pathlib import Path

import timer
from collect import REPO, session_runtime, recover, verified_scheduled_source
from bootstrap import PROJECT
from contracts import require, validate_contract, utcnow
from provenance import GitHubAuthority
from publisher_probe import PublisherAuth, PROJECT_ID, TEAM_ID, SCOPE
from release import release_daily
from storage import LocalStore


GATE_WORKFLOW = '.github/workflows/market-release-gate.yml'


def gate_callback(event):
    """True when this callback is the independent gate finishing (second half of a split release)."""
    return event.get('workflow_run', {}).get('path') == GATE_WORKFLOW


def callback_ready(event, api=None):
    """Read-only check before a workflow callback joins writer concurrency."""
    api = api or GitHubAuthority()._api
    upstream = event.get('workflow_run', {})
    if not isinstance(upstream.get('id'), int):
        return False
    run = api('actions/runs/' + str(upstream['id']))
    if run.get('path') == GATE_WORKFLOW:
        # Only a publisher-dispatched gate on main can complete a pending release;
        # a failed gate still completes, so the failure is recorded and alerted.
        return (run.get('id') == upstream['id'] and run.get('repository', {}).get('full_name') == PROJECT
                and run.get('head_branch') == 'main'
                and run.get('event') == 'workflow_dispatch' and run.get('status') == 'completed')
    if not (run.get('id') == upstream['id'] and run.get('repository', {}).get('full_name') == PROJECT
            and run.get('path') == '.github/workflows/subscription-collector.yml'
            and run.get('head_branch') == 'main' and timer.trusted_run(run)
            and run.get('status') == 'completed' and run.get('conclusion') == 'success'):
        return False
    # A backup timer that skipped because the day already ran also ends in
    # success. Only a run whose collection job actually succeeded may publish.
    jobs = api('actions/runs/' + str(upstream['id']) + '/jobs?per_page=20').get('jobs', [])
    if not any(j.get('name') == 'collect-and-reconcile' and j.get('conclusion') == 'success' for j in jobs):
        return False
    runs = api('actions/workflows/subscription-collector.yml/runs?per_page=100')['workflow_runs']
    return not any(r.get('status') in ('queued', 'in_progress', 'waiting', 'pending', 'requested') for r in runs)


def initial_collection_ready(state, contract, upstream_id=None):
    production = state.read('heads/production.json')
    if not (production or {}).get('legacyBaseline'):
        return True
    source = verified_scheduled_source(state, contract, utcnow())
    return source is not None and (upstream_id is None or source['githubRunId'] == upstream_id)


def safe_failure_reason(error):
    reason = str(error)
    # These are fixed categories emitted locally by the isolated CLI wrapper.
    categories = (
        'CLI_USAGE', 'AUTH_REQUIRED', 'TOKEN_REJECTED', 'ACCOUNT_ACCESS_DENIED', 'TEAM_ACCESS_DENIED',
        'RATE_LIMITED', 'NETWORK', 'USER_LOOKUP', 'TEAM_LOOKUP', 'ACCESS_DENIED', 'UNCLASSIFIED')
    allowed = {'VERCEL_' + phase + '_FAILED_' + category for category in categories
               for phase in ('PREBUILT_STAGE', 'GET_TARGET', 'PROMOTION', 'ROLLBACK', 'CONTROL')}
    allowed.update({'VERCEL_ALIAS_CHANGE_NOT_ACKNOWLEDGED', 'VERCEL_ALIAS_TARGET_NOT_READY_PROJECT_PRODUCTION',
                    'VERCEL_CONTROL_IDENTITY_OR_IGNORE_DIFFERS', 'VERCEL_CONTROL_ASSIGNMENT_NOT_CLOSED',
                    'VERCEL_OPERATION_FAILED', 'GITHUB_RELEASE_GATE_DISPATCH_FAILED', 'DAILY_GATE_BUDGET_EXHAUSTED'})
    return reason if reason in allowed else 'PUBLISHER_FAILED'


def execute(root):
    require(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_REPOSITORY') == PROJECT,
            'PRIVATE_GITHUB_RUNNER_REQUIRED')
    require(os.environ.get('GITHUB_REF') == 'refs/heads/main', 'REVIEWED_MAIN_REQUIRED')
    contract = validate_contract(json.loads((REPO / 'contracts/market.json').read_text()))
    if not contract['publication']['enabled']:
        return {'activated': False, 'published': False, 'reason': 'INITIAL_CUTOVER_NOT_ENABLED',
                'githubRunId': os.environ.get('GITHUB_RUN_ID'), 'githubEventName': os.environ.get('GITHUB_EVENT_NAME')}
    token = os.environ.pop('VERCEL_TOKEN', '')
    require(token, 'VERCEL_TOKEN_NOT_CONFIGURED')
    root = Path(root).resolve()
    revision = session_runtime.git('rev-parse', 'HEAD')
    identifier = 'github-publisher-' + os.environ['GITHUB_RUN_ID'] + '-' + os.environ.get('GITHUB_RUN_ATTEMPT', '1')
    recover(root / 'abandoned-lease-recovery')
    session_runtime.bootstrap(root, 'governance', identifier, revision, execution_mode='github_subscription')
    state = LocalStore(root / 'state')
    session = LocalStore(root).read('session.json')
    try:
        callback_ok = True
        upstream_id = None
        from_gate = False
        if os.environ.get('GITHUB_EVENT_NAME') == 'workflow_run':
            event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
            callback_ok = callback_ready(event)
            from_gate = gate_callback(event)
            upstream_id = None if from_gate else event.get('workflow_run', {}).get('id')
        if not callback_ok or not initial_collection_ready(state, contract, upstream_id):
            result = {'githubRunId': os.environ['GITHUB_RUN_ID'], 'published': False,
                      'activated': False, 'reason': 'WAITING_ACTUAL_SCHEDULED_COLLECTION'}
            result['archive'] = session_runtime.checkpoint(root, state, session, 'finish', result, finish=True)['archive']
            return result
        with PublisherAuth(root / 'publisher-auth', token) as auth:
            project = json.loads(auth.cli(['api', '/v9/projects/' + PROJECT_ID + '?teamId=' + TEAM_ID, '--raw']))
            require(project.get('id') == PROJECT_ID and project.get('accountId') == TEAM_ID,
                    'EXISTING_VERCEL_PROJECT_AND_TEAM_DIFFER')
            auth.pin_verified_team()
            config = {'vercel': {'project_id': PROJECT_ID, 'team_id': TEAM_ID, 'scope': SCOPE,
                                 'global_config': str(auth.root), 'runner': auth.isolated_runner}}
            archived = session_runtime.checkpoint(root, state, session, 'gate_requested', {})['archive']
            # Split release: this job dispatches the gate and ends; the gate's completion
            # (or the next publisher run) publishes, so no job is billed while it runs.
            publication = release_daily(state, contract, archived, revision, config,
                checkpoint=lambda: session_runtime.checkpoint(root, state, session, 'publication_journal', {})['archive'],
                split=True, complete_only=from_gate)
        result = {'githubRunId': os.environ['GITHUB_RUN_ID'], 'githubEventName': os.environ.get('GITHUB_EVENT_NAME'),
                  'appRevision': revision, 'activated': True, 'publication': publication}
        result['archive'] = session_runtime.checkpoint(root, state, session, 'finish', result, finish=True)['archive']
        return result
    except Exception as error:
        session_runtime.checkpoint(root, state, session, 'failed', {'errorType': type(error).__name__,
                                   'reason': safe_failure_reason(error), 'published': False}, finish=True)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        result = execute(args.root)
        code = 0
    except Exception as error:
        # Fixed categories only; remote response text can contain credentials.
        result = {'published': False, 'reason': safe_failure_reason(error), 'errorType': type(error).__name__}
        code = 2
    Path(args.output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(code)
