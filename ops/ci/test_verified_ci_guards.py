import subprocess
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from verified_ci_guards import REPOSITORY, SUITE_STEP, api, execute, proof


SHA = 'a' * 40


def fixtures():
    run = {'id': 123, 'head_sha': SHA, 'event': 'push', 'head_branch': 'main',
           'path': '.github/workflows/web.yml', 'status': 'completed', 'conclusion': 'success',
           'repository': {'full_name': REPOSITORY, 'private': True},
           'head_repository': {'full_name': REPOSITORY}, 'run_attempt': 2}
    job = {'id': 456, 'run_id': 123, 'head_sha': SHA, 'run_attempt': 2, 'name': 'test',
           'status': 'completed', 'conclusion': 'success', 'steps': [
               {'name': SUITE_STEP, 'status': 'completed', 'conclusion': 'success'}]}
    return {'workflow_runs': [run]}, {'total_count': 1, 'jobs': [job]}


class ExactCodeCiTests(unittest.TestCase):
    def test_accepts_exact_successful_push_suite_and_attempt(self):
        calls = []
        values = iter(fixtures())
        result = proof(SHA, lambda path: (calls.append(path), next(values))[1])
        self.assertEqual(result['runId'], 123)
        self.assertEqual(result['jobId'], 456)
        self.assertEqual(result['runAttempt'], 2)
        self.assertEqual(calls, [f'actions/workflows/web.yml/runs?head_sha={SHA}&status=success&event=push&per_page=20',
                                'actions/runs/123/attempts/2/jobs?per_page=100'])

    def test_preview_push_is_valid_but_other_refs_are_not(self):
        for branch, expected in [('preview', True), ('feature', False), ('main', True)]:
            runs, jobs = fixtures()
            runs['workflow_runs'][0]['head_branch'] = branch
            self.assertEqual(proof(SHA, lambda path: jobs if '/attempts/' in path else runs) is not None, expected)

    def test_rejects_untrusted_run_identity_or_completion(self):
        mutations = [('id', True), ('head_sha', 'b' * 40), ('event', 'pull_request'),
                     ('path', '.github/workflows/other.yml'), ('status', 'in_progress'),
                     ('conclusion', 'failure'), ('run_attempt', True),
                     ('repository', {'full_name': REPOSITORY, 'private': False}),
                     ('repository', {'full_name': 'foreign/sec-market', 'private': True}),
                     ('head_repository', {'full_name': 'foreign/sec-market'})]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                runs, jobs = fixtures()
                runs['workflow_runs'][0][key] = value
                self.assertIsNone(proof(SHA, lambda path: jobs if '/attempts/' in path else runs))

    def test_rejects_missing_failed_skipped_ambiguous_or_other_attempt_job(self):
        mutations = [('head_sha', 'b' * 40), ('run_id', 124), ('run_attempt', 1),
                     ('status', 'in_progress'), ('conclusion', 'failure'), ('id', True),
                     ('steps', []), ('steps', [{'name': SUITE_STEP, 'status': 'completed', 'conclusion': 'skipped'}]),
                     ('steps', [{'name': SUITE_STEP, 'status': 'completed', 'conclusion': 'failure'}])]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                runs, jobs = fixtures()
                jobs['jobs'][0][key] = value
                self.assertIsNone(proof(SHA, lambda path: jobs if '/attempts/' in path else runs))
        runs, jobs = fixtures()
        jobs['jobs'] *= 2
        jobs['total_count'] = 2
        self.assertIsNone(proof(SHA, lambda path: jobs if '/attempts/' in path else runs))
        runs, jobs = fixtures()
        jobs['jobs'][0]['steps'] *= 2
        self.assertIsNone(proof(SHA, lambda path: jobs if '/attempts/' in path else runs))

    def test_incomplete_or_oversized_lists_are_not_proof(self):
        runs, jobs = fixtures()
        for broken in ({'total_count': 101, 'jobs': jobs['jobs']}, {'total_count': True, 'jobs': jobs['jobs']},
                       {'total_count': 0, 'jobs': []}, {'total_count': 2, 'jobs': jobs['jobs']}):
            with self.assertRaises(ValueError):
                proof(SHA, lambda path: broken if '/attempts/' in path else runs)
        for broken in ({}, {'workflow_runs': [runs['workflow_runs'][0]] * 21}, {'workflow_runs': {}}):
            with self.assertRaises(ValueError):
                proof(SHA, lambda path: broken)

    def test_invalid_revision_never_reaches_api(self):
        for value in ('', 'A' * 40, 'a' * 39, 'a' * 40 + '?x', None):
            with self.assertRaises(ValueError):
                proof(value, lambda path: self.fail('unexpected API read'))

    @patch('verified_ci_guards.subprocess.run')
    def test_api_rejects_duplicate_nonfinite_and_oversized_json(self, run):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'x' * 2_000_001, b''):
            run.return_value = SimpleNamespace(stdout=raw)
            with self.assertRaises(ValueError):
                api('safe')
        run.return_value = SimpleNamespace(stdout=b'{"jobs":[]}')
        self.assertEqual(api('safe'), {'jobs': []})
        self.assertEqual(run.call_args.kwargs['timeout'], 20)

    def execute_case(self, read, env=None, head=SHA, fallback_code=0, dirty='', tree='c' * 40):
        calls = []
        def runner(argv, **kwargs):
            calls.append(argv)
            if argv == ['git', 'rev-parse', 'HEAD']:
                return SimpleNamespace(stdout=head + '\n')
            if argv == ['git', 'rev-parse', 'HEAD^{tree}']:
                return SimpleNamespace(stdout=tree + '\n')
            if argv[:2] == ['git', 'status']:
                return SimpleNamespace(stdout=dirty)
            self.assertEqual(argv[1:], ['-m', 'unittest', 'discover', '-s', 'ops/ci', '-p', 'test_*.py', '-v'])
            self.assertFalse(kwargs['check'])
            return SimpleNamespace(returncode=fallback_code)
        environment = {'GITHUB_REPOSITORY': REPOSITORY, 'GITHUB_REF': 'refs/heads/main', 'GITHUB_SHA': SHA}
        environment.update(env or {})
        code = execute(Path('.'), env=environment, read=read, runner=runner)
        return code, calls

    def test_verified_code_avoids_only_repeated_suite(self):
        runs, jobs = fixtures()
        code, calls = self.execute_case(lambda path: jobs if '/attempts/' in path else runs)
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 3)

    def test_missing_or_api_uncertain_proof_runs_full_suite_and_propagates_failure(self):
        def failure(path):
            raise subprocess.TimeoutExpired('gh', 20)
        for read in (failure, lambda path: {'workflow_runs': []}, lambda path: None):
            for exit_code in (0, 1):
                code, calls = self.execute_case(read, fallback_code=exit_code)
                self.assertEqual(code, exit_code)
                self.assertEqual(len(calls), 4)

    def test_changed_checkout_or_wrong_runtime_context_cannot_reuse_ci(self):
        for env in ({'GITHUB_REPOSITORY': 'foreign/sec-market'}, {'GITHUB_REF': 'refs/pull/1/merge'},
                    {'GITHUB_SHA': 'b' * 40}):
            code, calls = self.execute_case(lambda path: self.fail('unexpected API read'), env=env)
            self.assertEqual(code, 0)
            self.assertIn('unittest', calls[-1])

    def test_modified_runtime_tests_or_untracked_source_cannot_reuse_ci(self):
        for dirty in (' M ops/ci/collect.py\n', ' M ops/ci/test_collect.py\n', '?? ops/ci/new_guard.py\n'):
            code, calls = self.execute_case(lambda path: self.fail('unexpected API read'), dirty=dirty)
            self.assertEqual(code, 0)
            self.assertIn('unittest', calls[-1])
        code, calls = self.execute_case(lambda path: self.fail('unexpected API read'), tree='broken')
        self.assertEqual(code, 0)
        self.assertIn('unittest', calls[-1])

    def test_workflow_retains_full_ci_suite_and_uses_readback_in_both_hosted_jobs(self):
        root = Path(__file__).resolve().parents[2]
        web = (root / '.github/workflows/web.yml').read_text()
        self.assertIn('name: ' + SUITE_STEP, web)
        self.assertIn("python3 -m unittest discover -s ops/ci -p 'test_*.py' -v", web)
        for name in ('subscription-collector.yml', 'subscription-publisher.yml'):
            text = (root / '.github/workflows' / name).read_text()
            self.assertIn('run: python3 ops/ci/verified_ci_guards.py', text)
            self.assertIn('GH_TOKEN: ${{ github.token }}', text)
        self.assertNotIn('verified_ci_guards', (root / '.github/workflows/market-release-gate.yml').read_text())

    def test_primary_collection_callback_daily_recovery_and_independent_monitor_remain(self):
        root = Path(__file__).resolve().parents[2]
        publisher = (root / '.github/workflows/subscription-publisher.yml').read_text()
        self.assertIn("- cron: '23 16 * * *'", publisher)
        self.assertNotIn("23 0,6,16 * * *", publisher)
        self.assertIn("workflows: ['bounded subscription collector']", publisher)
        self.assertIn('types: [completed]', publisher)
        self.assertIn('workflow_dispatch:', publisher)
        self.assertIn('python3 ops/ci/job_alert.py --job publisher', publisher)
        collector = (root / '.github/workflows/subscription-collector.yml').read_text()
        self.assertIn("- cron: '17 5 * * *'", collector)
        self.assertIn('python3 ops/ci/schedule_guard.py', collector)
        watchdog = (root / '.github/workflows/freshness.yml').read_text()
        self.assertIn("- cron: '41 */6 * * *'", watchdog)
