"""Closed diagnostic tests. Synthetic responses grant no source credit."""
import copy
import json
import socket
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'web/scripts/pipeline'), str(ROOT / 'ops/ci')]
from contracts import canonical, digest
from storage import LocalStore
from historical_correction_fixtures import historical_requests
from onboarding import PersistentProbeBudget
import q4_initial_data_capture as data

PLAN = ROOT / 'docs/active/daily-pipeline/accuracy/q4-initial-data-capture-plan-2026-10-25.json'
ARCHIVE = Path('/var/tmp/smp-q4-controller-actual-20261025/extracted')
NOW = '2026-10-25T12:00:00Z'
NEXT_DAY = '2026-10-26T00:00:00Z'


class Clock:
    wall, elapsed = NOW, 0
    def now(self): return self.wall
    def monotonic(self): return self.elapsed


class ResponseFetcher:
    def __init__(self, fixture, body=b'{"synthetic":true}', changes=None, error=None, callback=None):
        self.fixture, self.body, self.changes, self.error, self.callback = fixture, body, changes or {}, error, callback
        self.calls = []
    def fetch(self, source, url):
        self.calls.append((source['id'], url))
        if self.callback: self.callback(self)
        if self.error: raise self.error
        observed = {'requestedUrl': url, 'finalUrl': url, 'status': 'fetched', 'httpStatus': 200,
                    'fetchedAt': self.fixture.clock.now(), 'contentType': 'application/json; charset=utf-8',
                    'body': self.fixture.store.put(self.body)}
        observed.update(self.changes)
        return observed


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.store = LocalStore(self.root / 'state'); self.clock = Clock()
        self.contract = json.loads((ROOT / 'contracts/html-qualification-seeds/8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db/contracts__8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db.json').read_bytes())
        self.raw = PLAN.read_bytes(); self.plan = json.loads(self.raw); self.path = self.root / 'plan.json'
        self.path.write_bytes(self.raw)
        # Transport units isolate the new operation; actual-proof tests below do not bypass this helper.
        parent_patch = patch.object(data, '_validate_capture')
        self.parent = parent_patch.start(); self.addCleanup(parent_patch.stop)
        for key in ('heads/latest-run.json', 'heads/dailySnapshot.json', 'heads/production.json', 'old-evidence.json'):
            self.store.write_once(key, {'original': key})
        self.protected = {k: (self.store.root / k).read_bytes() for k in
                          ('heads/latest-run.json', 'heads/dailySnapshot.json', 'heads/production.json', 'old-evidence.json')}
    def budget(self):
        return PersistentProbeBudget(self.store, self.contract, clock=self.clock.now, monotonic=self.clock.monotonic)
    def capture(self, fetcher=None, budget=None):
        normalized = data.validate_plan(self.contract, self.store, self.path.read_bytes(), self.path)
        self.context = budget or self.budget(); self.fetcher = fetcher or ResponseFetcher(self)
        return data.execute(self.contract, self.store, self.fetcher, self.context, normalized)
    def replay(self, report): return data.verify_report(self.contract, self.store, self.raw, report)

    def test_two_exact_gets_capture_only_and_replay_without_js_or_credit(self):
        report = self.capture()
        self.assertTrue(self.replay(report)['captureComplete']); self.assertEqual(report['capturedResponses'], 2)
        self.assertEqual([url for _, url in self.fetcher.calls], [r['request']['url'] for r in self.plan['sources']])
        self.assertEqual([r['reservation']['chargedFetchCount'] for r in report['requests']], [1, 2])
        self.assertEqual(report['facts'], []); self.assertFalse(report['qualified'])
        for key in ('qualifiedSources', 'sourceChecksCredited', 'modelCalls'): self.assertEqual(report[key], 0)
        for key, raw in self.protected.items(): self.assertEqual((self.store.root / key).read_bytes(), raw)

    def test_unknown_missing_and_typed_plan_fields_fail_before_proof_writes_or_reservations(self):
        changes = []
        for key in self.plan:
            p = copy.deepcopy(self.plan); del p[key]; changes.append(p)
        for key in self.plan['captureProof']:
            p = copy.deepcopy(self.plan); del p['captureProof'][key]; changes.append(p)
        for field in ('sourceId', 'supplierId', 'originalSourceSha256', 'htmlProof', 'controllerProof', 'request'):
            p = copy.deepcopy(self.plan); del p['sources'][0][field]; changes.append(p)
        for value in (True, 2.0, 6, -1):
            p = copy.deepcopy(self.plan); p['maxRequests'] = value; changes.append(p)
        p = copy.deepcopy(self.plan); p['extra'] = True; changes.append(p)
        self.parent.reset_mock()
        before = list(self.store.root.rglob('*'))
        for p in changes:
            with self.subTest(plan=p), self.assertRaises(ValueError):
                data.validate_plan(self.contract, self.store, canonical(p))
        self.parent.assert_not_called(); self.assertEqual(list(self.store.root.rglob('*')), before)

    def test_every_run_ref_source_category_method_and_query_substitution_rejects(self):
        changes = []
        for key, value in [('githubRunId', '1'), ('githubRunAttempt', True), ('githubEventName', 'schedule'),
                           ('githubRef', 'refs/heads/preview'), ('appRevision', 'a' * 40)]:
            p = copy.deepcopy(self.plan); p['captureProof'][key] = value; changes.append(p)
        for key in ('record', 'plan', 'archive'):
            p = copy.deepcopy(self.plan); p['captureProof'][key] = {}; changes.append(p)
        for section in ('htmlProof', 'controllerProof'):
            for key in self.plan['sources'][0][section]:
                p = copy.deepcopy(self.plan); p['sources'][0][section][key] = None; changes.append(p)
        original = self.plan['sources'][0]['request']['url']
        variants = [original.replace('00000000-0000-0000-0000-000000000000', '1cb807d2-208f-4bc3-9133-6a9ad45ac3b0'),
                    original.replace('year=-1', 'year=2026'), original.replace('pageSize=-1', 'pageSize=100'),
                    original.replace('tagList=', 'tagList=x'), original.replace('includeTags=true', 'includeTags=True'),
                    original.replace('LanguageId=1&bodyType=0', 'bodyType=0&LanguageId=1'), original + '&year=-1',
                    original + '#x', original.replace('https:', 'http:'), original.replace('.com/', '.com:443/'),
                    original.replace('/feed/', '/news/../feed/'), original.replace('pageNumber=0', 'pageNumber=1')]
        for url in variants:
            p = copy.deepcopy(self.plan); p['sources'][0]['request']['url'] = url; changes.append(p)
        for request in ({'method': 'POST', 'url': original, 'body': None},
                        {'method': 'GET', 'url': original, 'body': ''}):
            p = copy.deepcopy(self.plan); p['sources'][0]['request'] = request; changes.append(p)
        for p in changes:
            with self.subTest(plan=p), self.assertRaises(ValueError):
                data.validate_plan(self.contract, self.store, canonical(p))

    def test_live_plan_replacement_and_parent_failure_precede_operation_writes(self):
        normalized = data.validate_plan(self.contract, self.store, self.raw, self.path)
        budget = self.budget(); self.path.write_bytes(self.raw + b' ')
        with patch.object(self.store, 'put', side_effect=AssertionError('write')), self.assertRaises(ValueError):
            data.execute(self.contract, self.store, ResponseFetcher(self), budget, normalized)
        self.assertEqual(budget.reservations, 0)
        self.path.write_bytes(self.raw)
        self.parent.side_effect = ValueError('proof invalid')
        with patch.object(self.store, 'put', side_effect=AssertionError('write')), self.assertRaises(ValueError):
            data.execute(self.contract, self.store, ResponseFetcher(self), budget, normalized)
        self.assertEqual(budget.reservations, 0)

    def test_service_error_object_is_captured_only_for_review(self):
        report = self.capture(ResponseFetcher(self, body=b'{"error":"synthetic service failure"}'))
        self.assertTrue(report['captureComplete']); self.assertEqual(report['facts'], [])
        self.assertFalse(report['coverageCredit']); self.assertFalse(report['semanticAdmission'])
        self.assertEqual({r['reason'] for r in report['results']}, {'JSON_CAPTURED_REVIEW_REQUIRED'})

    def test_known_status_redirect_mime_charset_and_json_failures_retain_original_bytes(self):
        cases = [(b'{"a":1}', {'httpStatus': n}) for n in (203, 302, 403, 429)]
        cases += [(b'{"a":1}', {'finalUrl': 'https://investors.jfrog.com/elsewhere'}),
                  (b'{"a":1}', {'redirectDiagnostics': {'responses': [{'status': 302}]}})]
        cases += [(b'{"a":1}', {'contentType': x}) for x in
                  (None, '', 'text/html', 'application/javascript', 'application/json; charset=latin1')]
        cases += [(b, {}) for b in (b'', b'{}', b'[]', b'null', b'true', b'<html/>', b'{', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}', b'\xff')]
        for body, changes in cases:
            with self.subTest(body=body, changes=changes):
                report = self.capture(ResponseFetcher(self, body, changes))
                self.assertFalse(report['captureComplete']); self.replay(report)
                for row in report['results']:
                    self.assertEqual(self.store.get(row['body']), body)
                    self.assertFalse(row['captured']); self.assertFalse(row['coverageCredit'])

    def test_json_mime_allowlist_and_utf8_are_explicit(self):
        for mime in ('application/json', 'text/json', 'application/problem+json', 'application/json; charset="utf-8"'):
            with self.subTest(mime=mime):
                self.assertTrue(self.capture(ResponseFetcher(self, b'{"synthetic":"ok"}', {'contentType': mime}))['captureComplete'])

    def test_decoder_recursion_failure_keeps_known_raw_response(self):
        loads = json.loads
        body = b'{"synthetic_decoder_limit":true}'
        def limited(value, *args, **kwargs):
            if value == body.decode(): raise RecursionError('synthetic decoder limit')
            return loads(value, *args, **kwargs)
        with patch.object(data.json, 'loads', side_effect=limited):
            report = self.capture(ResponseFetcher(self, body)); self.replay(report)
        self.assertFalse(report['captureComplete'])
        self.assertEqual(self.store.get(report['results'][0]['body']), body)

    def test_unobserved_network_and_size_failures_remain_unknown_and_charged(self):
        for error in (OSError('synthetic network'), ValueError('synthetic byte limit')):
            report = self.capture(ResponseFetcher(self, error=error)); self.replay(report)
            self.assertFalse(report['captureComplete']); self.assertTrue(report['executionCompleted'])
            self.assertEqual(report['reservationContext']['probeFetchReservations'], 2)
            for request, result in zip(report['requests'], report['results']):
                self.assertIsNotNone(request['transportError'])
                for key in ('body', 'fetchedAt', 'finalUrl', 'contentType', 'httpStatus'): self.assertIsNone(result[key])

    def test_full_budget_denial_does_not_transport_or_refund(self):
        self.store.compare_and_swap('budget-2026-10-25', None, {'calls': 72, 'documents': 33, 'fetches': 5500})
        report = self.capture(); self.replay(report)
        self.assertEqual(self.fetcher.calls, []); self.assertTrue(report['budgetDenied'])
        self.assertEqual(report['reservationContext']['probeFetchReservations'], 0)
        self.assertEqual(report['reservationContext']['currentBudget'], {'calls': 72, 'documents': 33, 'fetches': 5500})

    def test_final_inflight_midnight_and_deadline_retain_response_and_deny_completion(self):
        for boundary in ('midnight', 'deadline'):
            self.clock = Clock()
            budget = self.budget()
            def callback(fetcher):
                if len(fetcher.calls) == 2:
                    if boundary == 'midnight': self.clock.wall = NEXT_DAY
                    else: self.clock.elapsed = 1200
            report = self.capture(ResponseFetcher(self, callback=callback), budget)
            self.assertEqual(len(self.fetcher.calls), 2); self.assertFalse(report['executionCompleted'])
            self.assertFalse(report['captureComplete']); self.replay(report)
            self.assertIsNotNone(report['results'][-1]['body'])

    def test_rollover_after_reservation_before_transport_keeps_charge_without_request_marker(self):
        budget = self.budget(); calls = 0
        def crossing():
            nonlocal calls
            calls += 1
            return NOW if calls <= 3 else NEXT_DAY
        budget.clock = crossing
        report = self.capture(budget=budget)
        self.assertEqual(self.fetcher.calls, []); self.assertEqual(budget.reservations, 1)
        self.assertIsNone(report['requests'][0]['requestedAt']); self.replay(report)

    def test_cancellation_and_partial_quota_stop_without_followup(self):
        self.store.compare_and_swap('budget-2026-10-25', None, {'calls': 72, 'documents': 33, 'fetches': 5499})
        report = self.capture(); self.assertEqual(len(self.fetcher.calls), 1); self.replay(report)
        budget = self.budget(); budget.deadline = 0
        report = self.capture(budget=budget); self.assertEqual(self.fetcher.calls, []); self.replay(report)

    def test_all_report_fields_counters_observations_times_and_credits_are_bound(self):
        report = self.capture()
        mutations = [lambda p: p.update(captureComplete=False), lambda p: p.update(capturedResponses=3),
                     lambda p: p.update(checkedAt='2026-10-25T11:00:00Z'), lambda p: p.update(facts=[{}]),
                     lambda p: p.update(modelCalls=1), lambda p: p.update(qualifiedSources=1),
                     lambda p: p.update(semanticAdmission=True), lambda p: p.update(extra=True),
                     lambda p: p['requests'][0].update(requestedAt=None),
                     lambda p: p['requests'][0].update(responseCheckedAt=NEXT_DAY),
                     lambda p: p['requests'][0]['reservation'].update(chargedFetchCount=2),
                     lambda p: p['reservationContext'].update(probeFetchReservations=1),
                     lambda p: p['results'][0].update(finalUrl='https://invalid.example/'),
                     lambda p: p['results'][0]['body'].update(bytes=0)]
        for mutate in mutations:
            changed = copy.deepcopy(report); mutate(changed)
            with self.subTest(mutate=mutate), self.assertRaises((ValueError, KeyError, TypeError)):
                self.replay(changed)
        failed = self.capture(ResponseFetcher(self, error=OSError('synthetic')))
        failed['requests'][0]['requestedAt'] = None
        with self.assertRaises(ValueError): self.replay(failed)

    def test_shared_leased_caller_uses_two_request_route_after_escrow(self):
        import collect
        events = []
        (self.root / 'contracts').mkdir(); (self.root / 'contracts/source-qualification-probes.json').write_bytes(self.raw)
        def transport(*args, **kwargs):
            self.assertEqual(kwargs, {'timeout': 12, 'max_bytes': 2_000_000,
                                     'redirect_diagnostics': True, 'unexpected_status_diagnostics': True})
            events.append('transport'); return ResponseFetcher(self)
        def escrow(*args): events.append('escrow')
        with patch.object(collect, 'REPO', self.root), patch.object(collect, 'PersistentProbeBudget', side_effect=lambda *a, **k: self.budget()), \
             patch.object(collect, 'escrow_budgets', side_effect=escrow), patch.object(collect, 'Fetcher', side_effect=transport), \
             patch.object(collect.session_runtime, 'require_source_probe_context'), \
             patch.object(collect.session_runtime, 'checkpoint', return_value={'archive': {'synthetic': True}}), \
             patch.dict('os.environ', {'GITHUB_RUN_ID': '123', 'GITHUB_RUN_ATTEMPT': '1',
                                      'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GITHUB_REF': 'refs/heads/main'}):
            result = collect.execute_source_probe(self.root, self.store,
                        {'checkpointProfile': 'source_probe', 'sessionId': 'synthetic', 'appRevision': 'a' * 40}, self.contract, 1200)
        self.assertEqual(events, ['escrow', 'transport']); self.assertEqual(result['facts'], [])
        self.assertEqual(result['diagnostic']['capturedResponses'], 2)
        self.assertEqual(result['publication']['reason'], 'SOURCE_PROBE_DIAGNOSTIC_ONLY')


class ReadOnlyArchive:
    def __init__(self):
        raw = (ARCHIVE / 'archive-manifest.json').read_bytes()
        assert digest(raw) == '600e58564c989206856ba48795bf4ce9f6fbbf73a604e806594e95327b53203a'
        self.entries = {r['key']: r for r in json.loads(raw)['files']}; self.touched = {}
    def raw(self, key):
        path = ARCHIVE / 'state' / key; entry = self.entries.get('state/' + key)
        if entry is None:
            assert not path.exists(); return None
        raw = path.read_bytes(); assert digest(raw) == entry['sha256'] and len(raw) == entry['bytes']
        self.touched[str(path)] = (digest(raw), len(raw), path.stat().st_mtime_ns)
        return raw
    def read(self, key):
        raw = self.raw(key); return json.loads(raw) if raw is not None else None
    def get(self, ref):
        raw = self.raw(ref['key']); assert digest(raw) == ref['sha256'] and len(raw) == ref['bytes']; return raw
    def assert_unchanged(self, case):
        for path, before in self.touched.items():
            p = Path(path); raw = p.read_bytes()
            case.assertEqual((digest(raw), len(raw), p.stat().st_mtime_ns), before)


@unittest.skipUnless((ARCHIVE / 'archive-manifest.json').exists(), 'Requires actual authenticated 9634 archive')
class ActualProofTests(unittest.TestCase):
    def setUp(self):
        self.store = ReadOnlyArchive(); self.addCleanup(self.store.assert_unchanged, self)
        self.contract = json.loads((ROOT / 'contracts/html-qualification-seeds/8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db/contracts__8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db.json').read_bytes()); self.raw = PLAN.read_bytes()
    def test_complete_original_capture_and_two_source_controller_html_joins(self):
        with patch.object(LocalStore, '__init__', side_effect=AssertionError('No frozen LocalStore')), \
             patch.object(socket.socket, 'connect', side_effect=AssertionError('No network')):
            plan = data.validate_plan(self.contract, self.store, self.raw)
        self.assertEqual(len(plan['targets']), 2); self.assertGreaterEqual(len(self.store.touched), 23)
        self.assertEqual([r['sourceId'] for r in plan['targets']], ['jfrog:official:1', 'rapid7:official:1'])

    def test_changed_actual_record_plan_wrappers_raw_api_and_html_fail_closed(self):
        original = self.store; plan = json.loads(self.raw)
        refs = [plan['captureProof']['record'], plan['captureProof']['plan']]
        for row in plan['sources']:
            refs += [row['htmlProof']['body'], row['controllerProof']['body'],
                     row['controllerProof']['observation'], row['controllerProof']['rawObservation']]
        for selected in refs:
            class Changed:
                read = original.read
                def get(_, ref):
                    raw = original.get(ref)
                    return raw + b' ' if ref['key'] == selected['key'] else raw
            with self.subTest(reference=selected), self.assertRaises(ValueError):
                data.validate_plan(self.contract, Changed(), self.raw)

    def test_all_six_old_admissions_and_hashes_replay_unchanged(self):
        from corrections import _index, group_review_policy, replay_admission
        requests = historical_requests()
        stamp = json.loads((ROOT / 'web/src/data/tracker/factualCorrectionPolicy.json').read_bytes())
        for group in requests['groups']:
            policy = group_review_policy(group, self.contract, requests['baseline']['sha256'])
            self.assertEqual(policy, stamp['reviewPolicySha256ByGroup'][group['id']])
            ref = self.store.read(_index(group, policy))['admission']; raw = self.store.get(ref)
            replay_admission(group, ref, self.store, self.contract, policy, NOW)
            self.assertEqual(self.store.get(ref), raw)

    def test_real_proof_preflight_capture_finalize_and_replay_in_isolated_writable_overlay(self):
        base = self.store
        with tempfile.TemporaryDirectory() as directory:
            local = LocalStore(Path(directory) / 'state')
            local.compare_and_swap('budget-2026-10-25', None, {'calls': 72, 'documents': 33, 'fetches': 450})
            class Overlay:
                def __getattr__(_, key): return getattr(local, key)
                def read(_, key):
                    return local.read(key) if (local.root / key).exists() else base.read(key)
                def get(_, ref):
                    return local.get(ref) if (local.root / ref['key']).exists() else base.get(ref)
            self.store = Overlay(); self.clock = Clock()
            path = Path(directory) / 'plan.json'; path.write_bytes(self.raw)
            with patch.object(socket.socket, 'connect', side_effect=AssertionError('No network')):
                normalized = data.validate_plan(self.contract, self.store, self.raw, path)
                budget = PersistentProbeBudget(self.store, self.contract, clock=self.clock.now, monotonic=self.clock.monotonic)
                fetcher = ResponseFetcher(self)
                report = data.execute(self.contract, self.store, fetcher, budget, normalized)
                report = data.finalize_report(self.contract, self.store, self.raw, report, budget)
                replay = data.verify_report(self.contract, self.store, self.raw, report)
            self.assertTrue(replay['captureComplete']); self.assertEqual(len(fetcher.calls), 2)
            self.assertEqual(report['reservationContext']['currentBudget'], {'calls': 72, 'documents': 33, 'fetches': 452})
            self.assertFalse(report['semanticAdmission']); self.assertFalse(report['coverageCredit'])


if __name__ == '__main__': unittest.main()
