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
from onboarding import PersistentProbeBudget
import q4_primary_qualification as data

PLAN = ROOT / 'docs/active/daily-pipeline/accuracy/q4-primary-qualification-plan-2026-10-25.json'
from test_q4_press_list import ARCHIVE, ReadOnlyD660
NOW = '2026-10-25T12:00:00Z'
NEXT_DAY = '2026-10-26T00:00:00Z'


class Clock:
    wall, elapsed = NOW, 0
    def now(self): return self.wall
    def monotonic(self): return self.elapsed


def synthetic_html(fixture, url, metadata=''):
    from html import escape
    title = next(r['sample']['title'] for r in fixture.plan['sources'] if r['sample']['request']['url'] == url)
    return ('<html><head><link rel="canonical" href="' + escape(url, quote=True) + '">' + metadata +
            '</head><body><main><article><h1>' + escape(title) + '</h1><p>' +
            'Fictional primary issuer text for transport and shape verification only. ' * 5 +
            '</p></article></main></body></html>').encode()


class ResponseFetcher:
    def __init__(self, fixture, body=None, changes=None, error=None, callback=None):
        self.fixture, self.body, self.changes, self.error, self.callback = fixture, body, changes or {}, error, callback
        self.calls = []
    def fetch(self, source, url):
        self.calls.append((source['id'], url))
        if self.callback: self.callback(self)
        if self.error: raise self.error
        body = self.body if self.body is not None else synthetic_html(self.fixture, url)
        observed = {'requestedUrl': url, 'finalUrl': url, 'status': 'fetched', 'httpStatus': 200,
                    'fetchedAt': self.fixture.clock.now(), 'contentType': 'text/html; charset=utf-8',
                    'body': self.fixture.store.put(body)}
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
        targets = []
        for source_row in self.plan['sources']:
            source = next(s for s in self.contract['sources'] if s['id'] == source_row['sourceId'])
            sample = source_row['sample']
            selected = {'rowIndex': 2, 'recordSha256': sample['recordSha256'], 'title': sample['title'],
                        'dateLiteral': sample['dateLiteral'], 'calendarDay': '2026-10-14'}
            targets.append({'sourceId': source['id'], 'supplierId': source['supplierId'],
                            'sourceSha256': source_row['originalSourceSha256'], 'source': source,
                            'url': sample['request']['url'], 'sample': selected})
        parent_patch = patch.object(data, '_validate_capture', return_value=(targets, [{'fictionalStream': t['sourceId']} for t in targets]))
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
        self.assertTrue(self.replay(report)['proposalEvidenceComplete']); self.assertEqual(report['acceptedSamples'], 2)
        self.assertEqual([url for _, url in self.fetcher.calls], [r['sample']['request']['url'] for r in self.plan['sources']])
        self.assertEqual([r['reservation']['chargedFetchCount'] for r in report['requests']], [1, 2])
        self.assertEqual(report['facts'], []); self.assertFalse(report['qualified'])
        for key in ('qualifiedSources', 'sourceChecksCredited', 'modelCalls'): self.assertEqual(report[key], 0)
        for key, raw in self.protected.items(): self.assertEqual((self.store.root / key).read_bytes(), raw)

    def test_unknown_missing_and_typed_plan_fields_fail_before_proof_writes_or_reservations(self):
        changes = []
        for key in self.plan:
            p = copy.deepcopy(self.plan); del p[key]; changes.append(p)
        for key in self.plan['initialDataProof']:
            p = copy.deepcopy(self.plan); del p['initialDataProof'][key]; changes.append(p)
        for field in ('sourceId', 'supplierId', 'originalSourceSha256', 'observation', 'body', 'sample'):
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
                self.assertFalse(report['proposalEvidenceComplete']); self.replay(report)
                for row in report['results']:
                    self.assertEqual(self.store.get(row['body']), body)
                    self.assertFalse(row['accepted']); self.assertFalse(row['coverageCredit'])



    def test_unobserved_network_and_size_failures_remain_unknown_and_charged(self):
        for error in (OSError('synthetic network'), ValueError('synthetic byte limit')):
            report = self.capture(ResponseFetcher(self, error=error)); self.replay(report)
            self.assertFalse(report['proposalEvidenceComplete']); self.assertTrue(report['executionCompleted'])
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
            self.assertFalse(report['proposalEvidenceComplete']); self.replay(report)
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
        mutations = [lambda p: p.update(proposalEvidenceComplete=False), lambda p: p.update(acceptedSamples=3),
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
        self.assertEqual(result['diagnostic']['acceptedSamples'], 2)
        self.assertEqual(result['publication']['reason'], 'SOURCE_PROBE_DIAGNOSTIC_ONLY')

    def test_one_matching_sample_cannot_complete_the_two_source_proposal(self):
        def fail_second(fetcher):
            if len(fetcher.calls) == 2: fetcher.changes['httpStatus'] = 403
        report = self.capture(ResponseFetcher(self, callback=fail_second)); self.replay(report)
        self.assertEqual(report['acceptedSamples'], 1); self.assertFalse(report['proposalEvidenceComplete'])
        self.assertTrue(report['executionCompleted']); self.assertEqual(len(self.fetcher.calls), 2)
        self.assertIsNotNone(report['results'][1]['body'])
        forged = copy.deepcopy(report); forged['proposalEvidenceComplete'] = True
        with self.assertRaises(ValueError): self.replay(forged)

    def test_optional_metadata_preserves_offsets_and_compares_written_day(self):
        for metadata in ('', '<meta property="article:published_time" content="2026-10-14T23:30:00-12:00">',
                         '<meta property="article:published_time" content="2026-10-14">',
                         '<script type="application/ld+json">{"@graph":[{"@type":"NewsArticle","datePublished":"2026-10-14T16:05:00-04:00"}]}</script>',
                         '<time datetime="2026-10-14T16:05:00"></time>'):
            class MetadataFetcher(ResponseFetcher):
                def fetch(this, source, url):
                    this.body = synthetic_html(self, url, metadata)
                    return super().fetch(source, url)
            report = self.capture(MetadataFetcher(self)); self.replay(report)
            self.assertTrue(report['proposalEvidenceComplete'])
            for result in report['results']:
                shape = result['primaryShape']; self.assertIsNone(shape['indexTimezone'])
                self.assertEqual(shape['dateMetadataState'], 'unknown' if not metadata else 'present')
                if '-12:00' in metadata:
                    self.assertEqual(shape['dateMetadata'][0]['value'], '2026-10-14T23:30:00-12:00')

    def test_supplied_invalid_publication_metadata_never_becomes_unknown_success(self):
        metadata = ['<meta property="article:published_time" content="">',
                    '<meta property="article:published_time">', '<time datetime=""></time>',
                    '<meta itemprop="datePublished" content="tomorrow">',
                    '<script type="application/ld+json">{"@type":"NewsArticle","datePublished":"tomorrow"}</script>',
                    '<script type="application/ld+json">{"@type":"NewsArticle","datePublished":null}</script>',
                    '<script type="application/ld+json">{"@type":"NewsArticle","datePublished":123}</script>',
                    '<script type="application/ld+json">{"@type":"NewsArticle","datePublished":[]}</script>',
                    '<script type="application/ld+json">{"@type":"NewsArticle","datePublished":""}</script>',
                    '<script type="application/ld+json">{"@type":"NewsArticle","datePublished":"2026-10-15","datePublished":"2026-10-14"}</script>',
                    '<script type=" application/ld+json ">{"@type":"NewsArticle","datePublished":"2026-10-15"}</script>',
                    '<template/><meta property="article:published_time" content="2026-10-15">',
                    '<script type="application/ld+json"/>',
                    '<script type="application/ld+json" type="text/plain">{"@type":"NewsArticle","datePublished":"2026-10-15"}</script>',
                    '<meta property="datePublished" property="other" content="2026-10-15">',
                    '<script type="application/ld+json">{"@type":"NewsArticle","datePublished":</script>']
        for supplied in metadata:
            class MetadataFetcher(ResponseFetcher):
                def fetch(this, source, url):
                    this.body = synthetic_html(self, url, supplied)
                    return super().fetch(source, url)
            report = self.capture(MetadataFetcher(self)); self.replay(report)
            self.assertFalse(report['proposalEvidenceComplete'])
            self.assertEqual(report['acceptedSamples'], 0)
            for result in report['results']:
                self.assertIsNone(result['primaryShape'])
                self.assertIn(supplied.encode(), self.store.get(result['body']))

    def test_wrong_heading_canonical_block_and_conflicting_dates_keep_raw_bytes(self):
        cases = [lambda text: text.replace('JFrog Announces Timing', 'Other Company Announces Timing'),
                 lambda text: text.replace('rel="canonical"', 'rel="alternate"'),
                 lambda text: text.replace('</head>', '<meta property="article:published_time" content="2026-10-15T00:00:00Z"></head>'),
                 lambda text: text.replace('</head>', '<script type="application/ld+json">{"@type":"NewsArticle","datePublished":"2026-10-15"}</script></head>'),
                 lambda text: text.replace('Fictional primary issuer text', 'Access denied')]
        for change in cases:
            class BadFetcher(ResponseFetcher):
                def fetch(this, source, url):
                    this.body = change(synthetic_html(self, url).decode()).encode()
                    return super().fetch(source, url)
            report = self.capture(BadFetcher(self)); self.replay(report)
            self.assertFalse(report['proposalEvidenceComplete'])
            self.assertIsNotNone(report['results'][0]['body'])

    def test_stream_inventory_shape_and_failed_attempt_tampering_rejects(self):
        report = self.capture()
        for mutate in (lambda p: p['streams'].append({}),
                       lambda p: p['results'][0]['primaryShape'].update(indexTimezone='UTC'),
                       lambda p: p['results'][0]['primaryShape'].update(indexDateLiteral='10/15/2026 16:05:00'),
                       lambda p: p['requests'][0].update(sourceId='rubrik:official:1')):
            changed = copy.deepcopy(report); mutate(changed)
            with self.subTest(mutate=mutate), self.assertRaises(ValueError): self.replay(changed)
        failed = self.capture(ResponseFetcher(self, error=OSError('fictional failed request')))
        failed['requests'][0]['requestedAt'] = NEXT_DAY
        with self.assertRaises(ValueError): self.replay(failed)

    def test_all_exact_plan_and_sample_substitutions_reject_before_parent_validation(self):
        changes = []
        for key, value in [('githubRunId', '1'), ('githubRunAttempt', True), ('githubEventName', 'schedule'),
                           ('githubRef', 'refs/heads/preview'), ('appRevision', 'a' * 40)]:
            p = copy.deepcopy(self.plan); p['initialDataProof'][key] = value; changes.append(p)
        for key in ('record', 'plan', 'archive'):
            p = copy.deepcopy(self.plan); p['initialDataProof'][key] = {}; changes.append(p)
        for key in self.plan['sources'][0]:
            p = copy.deepcopy(self.plan); p['sources'][0][key] = None; changes.append(p)
        for key in self.plan['sources'][0]['sample']:
            p = copy.deepcopy(self.plan); p['sources'][0]['sample'][key] = None; changes.append(p)
        p = copy.deepcopy(self.plan); p['sources'][0]['sample']['rowIndex'] = 0; changes.append(p)
        p = copy.deepcopy(self.plan); p['sources'][0]['sample']['request']['url'] += '?year=2026'; changes.append(p)
        self.parent.reset_mock()
        for changed in changes:
            with self.subTest(plan=changed), self.assertRaises(ValueError):
                data.validate_plan(self.contract, self.store, canonical(changed))
        self.parent.assert_not_called()


@unittest.skipUnless((ARCHIVE / 'archive-manifest.json').exists(), 'Requires actual authenticated d660 archive')
class ActualProofTests(unittest.TestCase):
    def setUp(self):
        self.store = ReadOnlyD660(); self.addCleanup(self.store.assert_unchanged, self)
        self.contract = json.loads((ROOT / 'contracts/html-qualification-seeds/8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db/contracts__8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db.json').read_bytes()); self.raw = PLAN.read_bytes()
        self.plan = json.loads(self.raw)
    def test_whole_actual_report_graph_row_two_and_original_window_replay_read_only(self):
        with patch.object(LocalStore, '__init__', side_effect=AssertionError('No frozen LocalStore')), \
             patch.object(socket.socket, 'connect', side_effect=AssertionError('No network')):
            plan = data.validate_plan(self.contract, self.store, self.raw)
        self.assertEqual([len(s['records']) for s in plan['streams']], [206, 323])
        self.assertEqual([len(s['currentWindowItems']) for s in plan['streams']], [3, 4])
        self.assertTrue(all(s['asOf'] == '2026-10-25T10:19:17.801039Z' for s in plan['streams']))
        self.assertTrue(all(t['sample']['rowIndex'] == 2 for t in plan['targets']))
        self.assertEqual([t['sample']['workflowId'] for t in plan['targets']],
                         ['717ce770-88db-49b1-a63a-071d28989c99', 'c4a988fc-6aab-42ee-a2af-4fb57a7ed054'])
        self.assertGreaterEqual(len(self.store.touched), 32)
    def test_changed_original_envelope_body_wrapper_html_and_controller_fail_closed(self):
        base = self.store; plan = self.plan
        refs = [plan['initialDataProof']['record'], plan['initialDataProof']['plan']]
        for row in plan['sources']: refs += [row['observation'], row['rawObservation'], row['body']]
        parent = json.loads(base.get(plan['initialDataProof']['plan']))
        for row in parent['sources']: refs += [row['htmlProof']['body'], row['controllerProof']['body']]
        for ref in refs:
            class Changed:
                read = base.read
                def get(_, requested):
                    raw = base.get(requested)
                    return raw + b' ' if requested['key'] == ref['key'] else raw
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                data.validate_plan(self.contract, Changed(), self.raw)
    def test_all_six_old_admission_hashes_and_original_bytes_replay(self):
        from corrections import _index, group_review_policy, replay_admission
        requests = json.loads((ROOT / 'contracts/factual-corrections.json').read_bytes())
        stamp = json.loads((ROOT / 'web/src/data/tracker/factualCorrectionPolicy.json').read_bytes())
        with patch.object(socket.socket, 'connect', side_effect=AssertionError('No network')):
            for group in requests['groups']:
                policy = group_review_policy(group, self.contract, requests['baseline']['sha256'])
                self.assertEqual(policy, stamp['reviewPolicySha256ByGroup'][group['id']])
                ref = self.store.read(_index(group, policy))['admission']; raw = self.store.get(ref)
                replay_admission(group, ref, self.store, self.contract, policy, NOW)
                self.assertEqual(self.store.get(ref), raw)
    def test_real_parent_with_fictional_samples_in_separate_writable_overlay(self):
        base = self.store
        with tempfile.TemporaryDirectory() as directory:
            local = LocalStore(Path(directory) / 'state')
            local.compare_and_swap('budget-2026-10-26', None, {'calls': 0, 'documents': 0, 'fetches': 0})
            class Overlay:
                def __getattr__(_, key): return getattr(local, key)
                def read(_, key): return local.read(key) if (local.root / key).exists() else base.read(key)
                def get(_, ref): return local.get(ref) if (local.root / ref['key']).exists() else base.get(ref)
            self.store = Overlay(); self.clock = Clock(); self.clock.wall = '2026-10-26T01:00:00Z'
            path = Path(directory) / 'plan.json'; path.write_bytes(self.raw)
            with patch.object(socket.socket, 'connect', side_effect=AssertionError('No network')):
                normalized = data.validate_plan(self.contract, self.store, self.raw, path)
                budget = PersistentProbeBudget(self.store, self.contract, clock=self.clock.now, monotonic=self.clock.monotonic)
                fetcher = ResponseFetcher(self)
                report = data.execute(self.contract, self.store, fetcher, budget, normalized)
                report = data.finalize_report(self.contract, self.store, self.raw, report, budget)
                replay = data.verify_report(self.contract, self.store, self.raw, report)
            self.assertTrue(replay['proposalEvidenceComplete']); self.assertEqual(len(fetcher.calls), 2)
            self.assertEqual([s['asOf'] for s in report['streams']], ['2026-10-25T10:19:17.801039Z'] * 2)
            self.assertEqual(report['reservationContext']['budgetDay'], '2026-10-26')
            self.assertEqual(report['reservationContext']['currentBudget'], {'calls': 0, 'documents': 0, 'fetches': 2})
            self.assertFalse(report['qualified']); self.assertFalse(report['semanticAdmission'])


if __name__ == '__main__': unittest.main()
