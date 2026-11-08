#!/usr/bin/env python3
"""Reuse only GitHub-acknowledged invariant tests for this exact checked-out code."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPOSITORY = 'jessepike/sec-market'
WORKFLOW = '.github/workflows/web.yml'
SUITE_STEP = 'Verify all operational guards for exact code'
MAX_BYTES = 2_000_000


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('CI_PROOF_DUPLICATE_KEY')
        value[key] = item
    return value


def api(path):
    result = subprocess.run(['gh', 'api', f'repos/{REPOSITORY}/{path}'],
                            capture_output=True, timeout=20, check=True)
    if not 0 < len(result.stdout) <= MAX_BYTES:
        raise ValueError('CI_PROOF_SIZE_INVALID')
    return json.loads(result.stdout, object_pairs_hook=unique_object,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('CI_PROOF_NONFINITE')))


def proof(sha, read=api):
    if not isinstance(sha, str) or not re.fullmatch(r'[a-f0-9]{40}', sha):
        raise ValueError('CI_PROOF_REVISION_INVALID')
    listing = read(f'actions/workflows/web.yml/runs?head_sha={sha}&status=success&event=push&per_page=20')
    if type(listing) is not dict or type(listing.get('workflow_runs')) is not list or len(listing['workflow_runs']) > 20:
        raise ValueError('CI_PROOF_RUN_LIST_INVALID')
    for run in listing['workflow_runs']:
        if (type(run) is not dict or type(run.get('id')) is not int or run['id'] <= 0
                or run.get('head_sha') != sha or run.get('event') != 'push'
                or run.get('head_branch') not in ('main', 'preview') or run.get('path') != WORKFLOW
                or run.get('status') != 'completed' or run.get('conclusion') != 'success'
                or type(run.get('head_repository')) is not dict
                or run['head_repository'].get('full_name') != REPOSITORY
                or type(run.get('repository')) is not dict
                or run['repository'].get('full_name') != REPOSITORY
                or type(run.get('run_attempt')) is not int or run['run_attempt'] <= 0):
            continue
        attempt = run['run_attempt']
        jobs = read(f"actions/runs/{run['id']}/attempts/{attempt}/jobs?per_page=100")
        if (type(jobs) is not dict or type(jobs.get('total_count')) is not int
                or type(jobs.get('jobs')) is not list or jobs['total_count'] != len(jobs['jobs'])
                or not 0 < jobs['total_count'] <= 100):
            raise ValueError('CI_PROOF_JOB_LIST_INCOMPLETE')
        candidates = [job for job in jobs['jobs'] if type(job) is dict and job.get('name') == 'test']
        if len(candidates) != 1:
            continue
        job = candidates[0]
        if (type(job.get('id')) is not int or job['id'] <= 0 or job.get('run_id') != run['id']
                or job.get('head_sha') != sha or job.get('run_attempt') != attempt
                or job.get('status') != 'completed' or job.get('conclusion') != 'success'
                or type(job.get('steps')) is not list):
            continue
        steps = [step for step in job['steps'] if type(step) is dict and step.get('name') == SUITE_STEP]
        if len(steps) == 1 and steps[0].get('status') == 'completed' and steps[0].get('conclusion') == 'success':
            return {'mode': 'exact_code_ci_verified', 'revision': sha, 'runId': run['id'],
                    'runAttempt': attempt, 'jobId': job['id'], 'suiteStep': SUITE_STEP}
    return None


def execute(root, env=None, read=api, runner=subprocess.run):
    env = os.environ if env is None else env
    result = None
    reason = 'EXACT_CODE_CI_NOT_AVAILABLE'
    try:
        if env.get('GITHUB_REPOSITORY') != REPOSITORY or env.get('GITHUB_REF') not in ('refs/heads/main', 'refs/heads/preview'):
            raise ValueError('CI_PROOF_RUNTIME_CONTEXT_INVALID')
        sha = env.get('GITHUB_SHA', '')
        head = runner(['git', 'rev-parse', 'HEAD'], cwd=root, capture_output=True,
                      text=True, timeout=10, check=True).stdout.strip()
        if sha != head:
            raise ValueError('CI_PROOF_CHECKOUT_REVISION_MISMATCH')
        dirty = runner(['git', 'status', '--porcelain', '--untracked-files=normal'], cwd=root,
                       capture_output=True, text=True, timeout=10, check=True).stdout
        if dirty:
            raise ValueError('CI_PROOF_CHECKOUT_NOT_CLEAN')
        tree = runner(['git', 'rev-parse', 'HEAD^{tree}'], cwd=root, capture_output=True,
                      text=True, timeout=10, check=True).stdout.strip()
        if not re.fullmatch(r'[a-f0-9]{40}', tree):
            raise ValueError('CI_PROOF_SOURCE_TREE_INVALID')
        result = proof(sha, read)
        if result is not None:
            # The full Git tree binds every tracked runtime, workflow and test file.
            result['sourceTree'] = tree
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError):
        # Uncertain proof does not bypass a test. Retain the existing full local suite.
        reason = 'EXACT_CODE_CI_UNVERIFIED'
    if result is not None:
        print(json.dumps(result, sort_keys=True))
        return 0
    print(json.dumps({'mode': 'full_suite_fallback', 'reason': reason}, sort_keys=True), flush=True)
    completed = runner([sys.executable, '-m', 'unittest', 'discover', '-s', 'ops/ci', '-p', 'test_*.py', '-v'],
                       cwd=root, check=False)
    return completed.returncode


if __name__ == '__main__':
    raise SystemExit(execute(Path(__file__).resolve().parents[2]))
