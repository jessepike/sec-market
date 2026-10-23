#!/usr/bin/env python3
"""Publish acknowledged evidence through the independent exact-artifact gate."""
import argparse
import json
import os
from pathlib import Path

from collect import REPO, session_runtime, recover
from bootstrap import PROJECT
from contracts import require, validate_contract
from publisher_probe import PublisherAuth, PROJECT_ID, TEAM_ID, SCOPE
from release import release_daily
from storage import LocalStore


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
        with PublisherAuth(root / 'publisher-auth', token) as auth:
            project = json.loads(auth.cli(['api', '/v9/projects/' + PROJECT_ID + '?teamId=' + TEAM_ID, '--raw']))
            require(project.get('id') == PROJECT_ID and project.get('accountId') == TEAM_ID,
                    'EXISTING_VERCEL_PROJECT_AND_TEAM_DIFFER')
            auth.pin_verified_team()
            config = {'vercel': {'project_id': PROJECT_ID, 'team_id': TEAM_ID, 'scope': SCOPE,
                                 'global_config': str(auth.root), 'runner': auth.isolated_runner}}
            archived = session_runtime.checkpoint(root, state, session, 'gate_requested', {})['archive']
            publication = release_daily(state, contract, archived, revision, config,
                checkpoint=lambda: session_runtime.checkpoint(root, state, session, 'publication_journal', {})['archive'])
        result = {'githubRunId': os.environ['GITHUB_RUN_ID'], 'githubEventName': os.environ.get('GITHUB_EVENT_NAME'),
                  'appRevision': revision, 'activated': True, 'publication': publication}
        result['archive'] = session_runtime.checkpoint(root, state, session, 'finish', result, finish=True)['archive']
        return result
    except Exception as error:
        session_runtime.checkpoint(root, state, session, 'failed', {'errorType': type(error).__name__, 'published': False}, finish=True)
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
        result = {'published': False, 'reason': 'PUBLISHER_FAILED', 'errorType': type(error).__name__}
        code = 2
    Path(args.output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(code)
