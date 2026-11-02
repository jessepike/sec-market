#!/usr/bin/env python3
"""Read-only Vercel publisher access acceptance, with private file-backed auth."""
import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from bootstrap import PROJECT, REPO, safe_process_env

PROJECT_ID = 'prj_g8sZPXo81XT2Xopa1oLrsbYjTehV'
TEAM_ID = 'team_gRV7FrVjjr1PPI1IvgoCEJrH'
SCOPE = 'pikeholdings'


def failure_reason(result):
    """Classify CLI failures without retaining remote text or credential values."""
    text = ((result.stdout or '') + '\n' + (getattr(result, 'stderr', '') or '')).lower()
    categories = [
        ('CLI_USAGE', ('unknown option', 'unexpected argument', 'missing required')),
        ('AUTH_REQUIRED', ('no existing credentials', 'authentication required', 'please log in')),
        ('TOKEN_REJECTED', ('invalid token', 'token is not valid', 'token has expired', 'unauthorized', 'invalid_token')),
        ('ACCOUNT_ACCESS_DENIED', ('do not have access to the specified account',)),
        ('TEAM_ACCESS_DENIED', ('do not have access to the specified team', 'specified scope does not exist')),
        ('RATE_LIMITED', ('rate limit', 'too many requests')),
        ('NETWORK', ('fetch failed', 'enotfound', 'econnreset', 'etimedout', 'certificate')),
        ('USER_LOOKUP', ('not able to load user',)),
        ('TEAM_LOOKUP', ('not able to load teams',)),
        ('ACCESS_DENIED', ('forbidden', 'not authorized', 'not_authorized', 'permission')),
    ]
    category = next((name for name, markers in categories if any(x in text for x in markers)), 'UNCLASSIFIED')
    return 'VERCEL_READ_ONLY_ACCESS_PROBE_FAILED_' + category


class PublisherAuth:
    def __init__(self, root, token, runner=subprocess.run):
        self.root = Path(root).absolute()
        self.token, self.runner = token, runner

    def __enter__(self):
        if self.root.resolve().is_relative_to(REPO) or self.root.exists() or self.root.is_symlink():
            raise RuntimeError('FRESH_OUTSIDE_CHECKOUT_PUBLISHER_AUTH_REQUIRED')
        if not self.token or not isinstance(self.token, str) or any(c.isspace() for c in self.token):
            raise RuntimeError('VERCEL_TOKEN_NOT_CONFIGURED_OR_INVALID')
        self.root.mkdir(mode=0o700, parents=True)
        fd = os.open(self.root / 'auth.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as handle:
            json.dump({'token': self.token}, handle)
            handle.flush()
            os.fsync(handle.fileno())
        # Official CLI scope resolution accepts a cached team selector. Pin it
        # only after the fixed project/team API check; no user lookup is needed
        # for an already verified, repository-owned project.
        self.token = None
        return self

    def pin_verified_team(self):
        (self.root / 'config.json').write_text(json.dumps({
            'currentTeam': TEAM_ID, 'cachedTeamIds': {SCOPE: TEAM_ID},
        }))

    @staticmethod
    def isolated_runner(args, **kwargs):
        env = safe_process_env()
        env.update(CI='1', VERCEL_TELEMETRY_DISABLED='1', NO_UPDATE_NOTIFIER='1')
        kwargs['env'] = env
        result = subprocess.run(args, **kwargs)
        if result.returncode:
            raise RuntimeError(failure_reason(result).replace('READ_ONLY_ACCESS_PROBE', 'PREBUILT_STAGE'))
        return result

    def cli(self, args):
        env = safe_process_env()
        env.update(CI='1', VERCEL_TELEMETRY_DISABLED='1', NO_UPDATE_NOTIFIER='1')
        # The endpoint carries the known team ID. --scope first performs user
        # discovery, which can fail before a team-scoped token reaches it.
        result = self.runner(['vercel', *args, '--global-config', str(self.root)],
                             capture_output=True, text=True, timeout=90, env=env)
        if result.returncode:
            raise RuntimeError(failure_reason(result))
        return result.stdout.strip()

    def __exit__(self, *_args):
        shutil.rmtree(self.root)


def execute(root):
    if os.environ.get('GITHUB_ACTIONS') != 'true' or os.environ.get('GITHUB_REPOSITORY') != PROJECT:
        raise RuntimeError('PRIVATE_GITHUB_RUNNER_REQUIRED')
    token = os.environ.pop('VERCEL_TOKEN', '')
    with PublisherAuth(root, token) as client:
        project = json.loads(client.cli(['api', '/v9/projects/' + PROJECT_ID + '?teamId=' + TEAM_ID, '--raw']))
        if project.get('id') != PROJECT_ID or project.get('accountId') != TEAM_ID:
            raise RuntimeError('EXISTING_VERCEL_PROJECT_AND_TEAM_DIFFER')
        resource = project.get('resourceConfig')
        if not isinstance(resource, dict):
            resource = {}
        resource_fields = {key: resource.get(key) if type(resource.get(key)) is expected else None
                           for key, expected in [('buildMachineType', str), ('buildMachineSelection', str),
                                                 ('elasticConcurrencyEnabled', bool)]}
        return {'publisherAccessPassed': True, 'githubRunId': os.environ['GITHUB_RUN_ID'],
                **resource_fields,
                'projectId': PROJECT_ID, 'teamId': TEAM_ID, 'scope': SCOPE,
                'rootDirectory': project.get('rootDirectory'), 'framework': project.get('framework'),
                'productionPathsControlled': project.get('autoAssignCustomDomains') is False and
                    project.get('commandForIgnoringBuildStep') == 'test "$VERCEL_GIT_COMMIT_REF" = main || test "$VERCEL_GIT_COMMIT_REF" = data/archive',
                'readOnly': True, 'deploymentAttempted': False,
                'publishPermissionAccepted': False, 'dailyWorkerActivated': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        receipt = execute(args.root)
    except Exception as error:
        receipt = {'publisherAccessPassed': False,
                   'reason': str(error) if type(error) is RuntimeError else type(error).__name__,
                   'deploymentAttempted': False, 'dailyWorkerActivated': False}
    Path(args.output).write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    raise SystemExit(0 if receipt['publisherAccessPassed'] else 2)
