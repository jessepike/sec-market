"""Fictional stores, remote acknowledgements and transport. No live requests."""
import contextlib
import copy
import io
import json
import re
import os
from pathlib import Path
import signal
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import collect
import cli
from contracts import canonical, digest
from storage import LocalStore
from test_onboarding_budget import Clock, FictionalFetcher, NOW, contract
from test_source_qualification_probe import seed_qualification_plan


class LeasedSourceProbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'runtime'
        self.repo = self.base / 'fictional-repo'
        (self.repo / 'contracts').mkdir(parents=True)
        self.policy = contract()
        self.policy['model'] = {'maxCallsPerRun': 80, 'maxDocumentsPerRun': 40}
        (self.repo / 'contracts/market.json').write_bytes(canonical(self.policy))
        self.event = self.base / 'event.json'
        self.event.write_text(json.dumps({'repository': {'full_name': 'jessepike/sec-market', 'private': True},
                                          'inputs': {'source_probe': 'true'}}))
        self.env = {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'jessepike/sec-market',
                    'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GITHUB_REF': 'refs/heads/main',
                    'GITHUB_RUN_ID': '123', 'GITHUB_RUN_ATTEMPT': '2', 'GITHUB_EVENT_PATH': str(self.event)}
        self.clock = Clock()
        self.pushes, self.events = [], []
        self.last_commit = 'b' * 40
        self.seed = {'calls': 7, 'documents': 3, 'fetches': 8, 'extra': 'retain'}
        self.protected = {}
        self.fail_push_at = None
        outer = self
        class Archive:
            def restore(self, destination):
                outer.events.append('restore')
                state = LocalStore(destination)
                for name in ('cloud-collector', 'worker-heartbeat', 'latest-run', 'dailySnapshot', 'cloud-snapshot'):
                    state.compare_and_swap(name, None, {'sentinel': name})
                    outer.protected[name] = (state.root / f'heads/{name}.json').read_bytes()
                state.compare_and_swap('budget-2026-10-23', None, outer.seed)
                state.write_once('ci/collection-runs/old-1.json', {'keep': True})
                state.write_once('cloud/sessions/old/old.json', {'keep': True})
                seed_qualification_plan(state, outer.policy, outer.repo / 'contracts/source-qualification-probes.json')
                return {'commit': outer.last_commit, 'sha256': 'c' * 64}
            def push(self, state, expected_commit=None):
                outer.events.append('push')
                outer.pushes.append({'expected': expected_commit,
                    'budget': copy.deepcopy(state.read('heads/budget-2026-10-23.json')),
                    'lease': copy.deepcopy(state.read('heads/cloud-lease.json'))})
                outer.assertEqual(expected_commit, outer.last_commit)
                if outer.fail_push_at == len(outer.pushes):
                    raise RuntimeError('synthetic remote acknowledgement failed')
                outer.last_commit = f'{len(outer.pushes):040x}'
                return {'commit': outer.last_commit, 'sha256': 'd' * 64}
        self.archive = Archive()
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict(os.environ, self.env, clear=True))
        self.stack.enter_context(patch.object(collect, 'REPO', self.repo))
        self.stack.enter_context(patch.object(collect, 'validate_contract', side_effect=lambda value: value))
        self.stack.enter_context(patch.object(collect, 'utcnow', self.clock.now))
        self.stack.enter_context(patch.object(collect.time, 'monotonic', self.clock.monotonic))
        self.recovery = self.stack.enter_context(patch.object(collect, 'recover'))
        runtime = collect.session_runtime
        self.stack.enter_context(patch.object(runtime, 'REPO', self.repo))
        self.stack.enter_context(patch.object(runtime, 'utcnow', self.clock.now))
        self.stack.enter_context(patch.object(runtime, 'archive_for', return_value=self.archive))
        self.stack.enter_context(patch.object(runtime, 'git', side_effect=lambda *args: 'a'*40 if args[0] == 'rev-parse' else ''))
        self.stack.enter_context(patch.object(runtime.shutil, 'which', return_value='/installed'))
        self.stack.enter_context(patch.object(runtime.shutil, 'disk_usage', return_value=SimpleNamespace(free=10**12)))
        self.stack.enter_context(patch.object(runtime, 'subprocess', SimpleNamespace(run=lambda *_a, **_k: SimpleNamespace(stdout='v22.0.0'))))
        self.fetcher = None
        self.stack.enter_context(patch.object(collect, 'Fetcher', side_effect=self.transport))
        self.forbidden = []
        for name in ('AuthStore', 'GuardedRunner', 'SubscriptionAgent', 'BoundedPipeline', 'correction_work',
                     'reuse_scheduled_collection', 'archive_collection_result', 'build_snapshot', 'reconcile'):
            self.forbidden.append(self.stack.enter_context(patch.object(collect, name, side_effect=AssertionError(name + ' forbidden'))))

    def transport(self, state, **_kwargs):
        def observed(_url):
            self.events.append('fetch')
            self.assertGreaterEqual(len(self.pushes), 2)
            self.assertEqual(self.pushes[0]['lease']['checkpointProfile'], 'source_probe')
            self.assertEqual(self.pushes[1]['budget'], {**self.seed, 'fetches': 5500})
        self.fetcher = FictionalFetcher(state, callback=observed)
        return self.fetcher

    def run_probe(self):
        return collect.execute(self.root, maximum_seconds=60, source_probe=True)

    def state(self):
        return LocalStore(self.root / 'state')

    def assert_preserved(self):
        state = self.state()
        for name, body in self.protected.items():
            self.assertEqual((state.root / f'heads/{name}.json').read_bytes(), body, name)
        self.assertEqual([str(p.relative_to(state.root)) for p in (state.root / 'ci/collection-runs').glob('*')],
                         ['ci/collection-runs/old-1.json'])
        self.assertEqual(list((state.root / 'cloud/sessions').glob('*/*')), [state.root / 'cloud/sessions/old/old.json'])
        for forbidden in self.forbidden:
            forbidden.assert_not_called()

    def test_lease_escrow_before_fetch_final_cas_and_diagnostic_only(self):
        result = self.run_probe()
        self.assertTrue(result['executionCompleted'])
        self.assertEqual(result['outcome'], 'completed_diagnostic')
        self.assertEqual(self.events, ['restore', 'push', 'push'] + ['fetch']*8 + ['push'])
        self.assertEqual([p['expected'] for p in self.pushes], ['b'*40, f'{1:040x}', f'{2:040x}'])
        self.assertEqual(self.state().read('heads/budget-2026-10-23.json'), {**self.seed, 'fetches': 16})
        self.assertTrue(self.pushes[-1]['lease']['releasedAt'])
        archived = self.state().read('ci/source-probe-runs/123-2.json')
        self.assertEqual(archived, {k: v for k, v in result.items() if k != 'archive'})
        for key in ('runId', 'successfulTasks', 'requiredTasks', 'complete'):
            self.assertNotIn(key, archived)
        self.assertEqual(result['modelCalls'], 0)
        self.assertFalse(result['semanticAdmission'])
        self.assertFalse(result['coverageCredit'])
        self.assertFalse(result['publication']['published'])
        self.assertEqual(result['diagnostic']['qualification']['chargedExplicitRequests'], 7)
        self.assertEqual(result['diagnostic']['qualification']['plan']['maxRequests'], 7)
        self.assert_preserved()

    def test_invalid_plan_or_tampered_proof_starts_no_transport_or_escrow(self):
        for mode in ('plan', 'proof'):
            with self.subTest(mode=mode):
                # A distinct runtime preserves each failed lease's evidence.
                self.root = self.base / ('runtime-invalid-' + mode)
                original_restore = self.archive.restore
                def invalid_restore(destination):
                    restored = original_restore(destination)
                    path = self.repo / 'contracts/source-qualification-probes.json'
                    if mode == 'plan':
                        plan = json.loads(path.read_text())
                        plan['targets'][-1]['url'] = 'https://example.invalid/not-disclosed'
                        path.write_bytes(canonical(plan))
                    else:
                        plan = json.loads(path.read_text())
                        body = Path(destination) / plan['targets'][-1]['proof']['body']['key']
                        body.write_bytes(b'fictional tampering')
                    return restored
                self.pushes.clear()
                self.events.clear()
                with patch.object(self.archive, 'restore', side_effect=invalid_restore), self.assertRaises(ValueError):
                    self.run_probe()
                self.assertIsNone(self.fetcher)
                self.assertNotIn('fetch', self.events)
                self.assertEqual(self.state().read('heads/budget-2026-10-23.json'), self.seed)
                self.assertFalse((self.state().root / 'source-probes').exists())
                self.assertTrue(self.state().read('heads/cloud-lease.json')['releasedAt'])
                # Only lease bootstrap/failure acknowledgement; no fetch escrow push.
                self.assertTrue(all(p['budget'] == self.seed for p in self.pushes))
                self.assert_preserved()

    def test_wrong_ref_event_repository_or_identity_starts_no_restore(self):
        for key, value in (('GITHUB_REF', 'refs/heads/preview'), ('GITHUB_EVENT_NAME', 'schedule'),
                           ('GITHUB_REPOSITORY', 'other/repo'), ('GITHUB_RUN_ID', 'not-a-run'),
                           ('GITHUB_RUN_ATTEMPT', '0'), ('GITHUB_ACTIONS', 'false')):
            with self.subTest(key=key), patch.dict(os.environ, {key: value}), self.assertRaises(ValueError):
                self.run_probe()
        self.recovery.assert_not_called()
        self.assertEqual(self.events, [])
        self.assertFalse(self.root.exists())

    def test_private_event_and_explicit_true_input_are_required(self):
        for event in ({'repository': {'full_name': 'other/repo', 'private': True}, 'inputs': {'source_probe': 'true'}},
                      *[{'repository': {'full_name': 'jessepike/sec-market', 'private': True}, 'inputs': {'source_probe': value}}
                        for value in (False, 'false', None, 1)]):
            with self.subTest(event=event):
                self.event.write_text(json.dumps(event))
                with self.assertRaises(ValueError):
                    self.run_probe()
        self.recovery.assert_not_called()
        self.assertEqual(self.events, [])

    def test_invalid_runtime_and_nonboolean_mode_start_no_restore(self):
        for seconds in (59, 1201):
            with self.subTest(seconds=seconds), self.assertRaises(ValueError):
                collect.execute(self.root, maximum_seconds=seconds, source_probe=True)
        with self.assertRaisesRegex(ValueError, 'BOOLEAN'):
            collect.execute(self.root, source_probe='true')
        self.assertEqual(self.events, [])

    def test_failed_lease_acknowledgement_starts_no_fetch_or_normal_proof(self):
        self.fail_push_at = 1
        with self.assertRaisesRegex(RuntimeError, 'acknowledgement'):
            self.run_probe()
        self.assertIsNone(self.fetcher)
        self.assertEqual(self.state().read('heads/budget-2026-10-23.json'), self.seed)
        self.assert_preserved()

    def test_failed_escrow_acknowledgement_retains_ceiling_and_starts_no_fetch(self):
        self.fail_push_at = 2
        with self.assertRaisesRegex(RuntimeError, 'acknowledgement'):
            self.run_probe()
        self.assertIsNone(self.fetcher)
        self.assertEqual(self.state().read('heads/budget-2026-10-23.json'), {**self.seed, 'fetches': 5500})
        self.assert_preserved()

    def test_contract_failure_after_bootstrap_keeps_normal_heads_and_account_untouched(self):
        with patch.object(collect, 'validate_contract', side_effect=ValueError('fictional invalid policy')):
            with self.assertRaisesRegex(ValueError, 'invalid policy'):
                self.run_probe()
        self.assertIsNone(self.fetcher)
        self.assertTrue(self.state().read('heads/cloud-lease.json')['releasedAt'])
        self.assertEqual(self.state().read('heads/budget-2026-10-23.json'), self.seed)
        self.assert_preserved()

    def test_transport_setup_failure_archives_only_diagnostic_failure(self):
        with patch.object(collect, 'Fetcher', side_effect=RuntimeError('fictional transport setup')):
            with self.assertRaisesRegex(RuntimeError, 'transport setup'):
                self.run_probe()
        self.assertEqual(self.state().read('heads/budget-2026-10-23.json'), self.seed)
        self.assertTrue(self.state().read('heads/cloud-lease.json')['releasedAt'])
        self.assertTrue(list((self.state().root / 'ci/source-probe-failures').glob('*/*')))
        self.assert_preserved()

    def test_killed_probe_lease_recovery_retains_fetch_ceiling_without_model_charge(self):
        from recover_lease import release_terminated
        runtime = collect.session_runtime
        runtime.bootstrap(self.root, 'collector', 'github-123-2', 'a'*40,
                          execution_mode='github_subscription', checkpoint_profile='source_probe')
        session = LocalStore(self.root).read('session.json')
        collect.escrow_budgets(self.root, self.state(), session, self.policy, NOW)
        # The acknowledged remote state, before the live runner uses its local
        # share, is the ceiling restored by a successor after an unknown kill.
        state = self.state()
        before = state.read('heads/budget-2026-10-23.json')
        state.compare_and_swap('budget-2026-10-23', before, self.pushes[1]['budget'])
        charged = (state.root / 'heads/budget-2026-10-23.json').read_bytes()
        recovered = release_terminated(state, lookup=lambda _id: {
            'id': 123, 'run_attempt': 2, 'repository': {'full_name': 'jessepike/sec-market'},
            'status': 'completed', 'conclusion': 'cancelled'})
        self.assertTrue(recovered['recovered'])
        self.assertEqual((state.root / 'heads/budget-2026-10-23.json').read_bytes(), charged)
        self.assertEqual(state.read('heads/budget-2026-10-23.json'), {**self.seed, 'fetches': 5500})
        self.assert_preserved()

    def test_full_daily_cap_starts_no_fetch_and_preserves_prior_metadata(self):
        self.seed = {'calls': 80, 'documents': 40, 'fetches': 5500, 'extra': {'retain': True}}
        result = self.run_probe()
        self.assertFalse(result['executionCompleted'])
        self.assertTrue(result['diagnostic']['budgetDenied'])
        self.assertEqual(collect.exit_code(result), 2)
        self.assertEqual(self.fetcher.calls, [])
        self.assertEqual(self.state().read('heads/budget-2026-10-23.json'), self.seed)
        self.assert_preserved()

    def test_midnight_during_remote_escrow_ack_does_not_spend_new_day(self):
        self.clock.current = '2026-10-23T23:59:59Z'
        original_push = self.archive.push
        def cross_midnight(*args, **kwargs):
            result = original_push(*args, **kwargs)
            if len(self.pushes) == 2:
                self.clock.current = '2026-10-24T00:00:00Z'
            return result
        with patch.object(self.archive, 'push', side_effect=cross_midnight):
            result = self.run_probe()
        self.assertFalse(result['executionCompleted'])
        self.assertEqual(result['diagnostic']['completionDenial'], 'SOURCE_PROBE_UTC_DAY_CHANGED')
        self.assertEqual(result['diagnostic']['reservationContext']['budgetDay'], '2026-10-23')
        self.assertEqual(self.fetcher.calls, [])
        self.assertIsNone(self.state().read('heads/budget-2026-10-24.json'))
        self.assertEqual(self.state().read('heads/budget-2026-10-23.json'), self.seed)
        self.assert_preserved()

    def test_deadline_during_escrow_starts_zero_requests(self):
        original_push = self.archive.push
        def late(*args, **kwargs):
            result = original_push(*args, **kwargs)
            if len(self.pushes) == 2:
                self.clock.elapsed = 60
            return result
        with patch.object(self.archive, 'push', side_effect=late):
            result = self.run_probe()
        self.assertFalse(result['executionCompleted'])
        self.assertEqual(self.fetcher.calls, [])
        self.assertEqual(result['diagnostic']['completionDenial'], 'SOURCE_PROBE_DEADLINE_EXCEEDED')
        self.assert_preserved()

    def test_last_inflight_failure_finishing_late_cannot_claim_completion(self):
        original_transport = self.transport
        def late_fetcher(state, **kwargs):
            fetcher = original_transport(state, **kwargs)
            fetcher.callback = lambda _url: setattr(self.clock, 'elapsed', 60)
            return fetcher
        with patch.object(collect, 'Fetcher', side_effect=late_fetcher):
            result = self.run_probe()
        self.assertEqual(len(self.fetcher.calls), 1)
        self.assertFalse(result['executionCompleted'])
        self.assertEqual(result['diagnostic']['completionDenial'], 'SOURCE_PROBE_DEADLINE_EXCEEDED')
        self.assertEqual(self.state().read('heads/budget-2026-10-23.json')['fetches'], 9)
        self.assert_preserved()

    def test_cooperative_cancellation_records_charge_and_stops_followup_transport(self):
        original_transport = self.transport
        def cancelled_fetcher(state, **kwargs):
            fetcher = original_transport(state, **kwargs)
            fetcher.statuses = ['fetched']
            fetcher.callback = lambda _url: signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
            return fetcher
        prior_handler = signal.getsignal(signal.SIGTERM)
        with patch.object(collect, 'Fetcher', side_effect=cancelled_fetcher):
            result = self.run_probe()
        self.assertEqual(result['outcome'], 'cancelled')
        self.assertFalse(result['executionCompleted'])
        self.assertEqual(len(self.fetcher.calls), 1)
        self.assertEqual(self.state().read('heads/budget-2026-10-23.json')['fetches'], 9)
        self.assertIs(signal.getsignal(signal.SIGTERM), prior_handler)
        self.assert_preserved()

    def test_final_archive_failure_cannot_return_success(self):
        self.fail_push_at = 3
        with self.assertRaisesRegex(RuntimeError, 'acknowledgement'):
            self.run_probe()
        self.assertEqual(len(self.fetcher.calls), 8)
        self.assertEqual(LocalStore(self.root).read('heads/remote-archive.json')['commit'], f'{2:040x}')
        self.assert_preserved()

    def test_profile_cannot_be_added_removed_or_changed_after_bootstrap(self):
        runtime = collect.session_runtime
        runtime.bootstrap(self.root, 'collector', 'github-123-2', 'a'*40,
                          execution_mode='github_subscription', checkpoint_profile='source_probe')
        session = LocalStore(self.root).read('session.json')
        variants = [{k: v for k, v in session.items() if k != 'checkpointProfile'},
                    {**session, 'checkpointProfile': 'unknown'}, {**session, 'appRevision': 'f'*40}]
        before = len(self.pushes)
        for variant in variants:
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                runtime.checkpoint(self.root, self.state(), variant, 'finish', {}, finish=True)
        self.assertEqual(len(self.pushes), before)
        self.assert_preserved()

    def test_unknown_profile_and_native_profile_reject_before_restore(self):
        runtime = collect.session_runtime
        for mode, profile in (('github_subscription', 'other'), ('codex_cloud_native', 'source_probe')):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                runtime.bootstrap(self.root, 'collector', 'github-123-2', 'a'*40,
                                  execution_mode=mode, checkpoint_profile=profile)
        self.assertEqual(self.events, [])

    def test_probe_session_cannot_enter_native_advance(self):
        runtime = collect.session_runtime
        runtime.bootstrap(self.root, 'collector', 'github-123-2', 'a'*40,
                          execution_mode='github_subscription', checkpoint_profile='source_probe')
        with self.assertRaisesRegex(ValueError, 'NATIVE_WORK_FORBIDDEN'):
            runtime.execute(SimpleNamespace(root=str(self.root), command='advance'))
        self.assert_preserved()


class SourceProbeEntryTests(unittest.TestCase):
    def test_archive_push_requires_full_commit_before_state_or_transport(self):
        for expected in (None, 'a'*39, 'A'*40, 'not-a-commit'):
            args = ['cli.py', 'archive-push'] + (['--expected-commit', expected] if expected else [])
            with self.subTest(expected=expected), patch.object(sys, 'argv', args), \
                    patch.object(cli, 'LocalStore') as store, patch.object(cli, 'validate_contract') as validator, \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                cli.main()
            store.assert_not_called()
            validator.assert_not_called()

    def test_archive_push_passes_exact_acknowledged_commit_to_existing_api(self):
        with tempfile.TemporaryDirectory() as directory:
            policy = Path(directory) / 'policy.json'
            policy.write_text('{}')
            args = ['cli.py', 'archive-push', '--contract', str(policy), '--state', directory + '/state',
                    '--archive-mirror', directory + '/archive', '--expected-commit', 'a'*40]
            with patch.object(sys, 'argv', args), patch.object(cli, 'validate_contract', return_value={}), \
                    patch('archive.GitArchive') as archive, contextlib.redirect_stdout(io.StringIO()):
                archive.return_value.push.return_value = {'commit': 'b'*40}
                self.assertEqual(cli.main(), 0)
            self.assertEqual(archive.return_value.push.call_args.kwargs, {'expected_commit': 'a'*40})

    def test_workflow_probe_is_manual_default_false_without_account_or_alert_step(self):
        workflow = (Path(__file__).resolve().parents[2] / '.github/workflows/subscription-collector.yml').read_text()
        self.assertIn('source_probe:\n', workflow)
        self.assertIn('type: boolean\n        required: false\n        default: false', workflow)
        probe = workflow.split('- name: Probe candidate sources', 1)[1].split('- name:', 1)[0]
        self.assertIn("if: github.event_name == 'workflow_dispatch' && inputs.source_probe", probe)
        self.assertIn('--source-probe', probe)
        # The only secret is the deploy key for the private evidence repository.
        self.assertEqual(set(re.findall(r'secrets\.(\w+)', probe)), {'SMP_EVIDENCE_DEPLOY_KEY'})
        self.assertNotIn('SMP_CODEX_AUTH_JSON', probe)
        for label in ('Install pinned application and official account client',
                      'Restore acknowledged evidence, collect bounded deltas and reconcile'):
            step = workflow.split('- name: ' + label, 1)[1].split('- name:', 1)[0]
            self.assertIn("if: github.event_name != 'workflow_dispatch' || !inputs.source_probe", step)
        alert = workflow.split('- name: Report failure or recovery to the owner', 1)[1].split('- name:', 1)[0]
        self.assertIn("if: always() && (github.event_name != 'workflow_dispatch' || !inputs.source_probe)", alert)
        self.assertIn('job_alert.py --job collector', alert)
        from publish import callback_ready
        run = {'id': 123, 'repository': {'full_name': 'jessepike/sec-market', 'private': True},
               'path': '.github/workflows/subscription-collector.yml', 'head_branch': 'main',
               'event': 'workflow_dispatch', 'status': 'completed', 'conclusion': 'success'}
        calls = []
        def api(path):
            calls.append(path)
            return run
        self.assertFalse(callback_ready({'workflow_run': {'id': 123}}, api=api))
        self.assertEqual(calls, ['actions/runs/123'])


if __name__ == '__main__':
    unittest.main()
