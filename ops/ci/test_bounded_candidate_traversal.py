"""Offline schema-2 candidate traversal tests; all transport is fictional."""
import json
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
sys.path.insert(0, str(ROOT / 'ops/ci'))

from contracts import canonical, digest
from onboarding import (BOUNDED_CANDIDATE_BINDINGS, BOUNDED_CANDIDATE_LIMIT,
                        BOUNDED_CANDIDATE_MAX_REQUESTS, BOUNDED_CANDIDATE_OPERATION,
                        PersistentProbeBudget, _candidate_adapter, _verify_bounded_candidate_result,
                        validate_qualification_probe_plan, probe_sources)
from storage import LocalStore
from test_html_archive_discovery import delinea_page, sonatype_page, sonatype_url
from test_ping_discovery import complete_layout

NOW = '2026-10-23T12:00:00Z'


class Clock:
    def __init__(self, wall=NOW): self.elapsed, self.wall = 0, wall
    def now(self): return self.wall
    def monotonic(self): return self.elapsed


class CandidateFetcher:
    def __init__(self, store, *, sonatype_last=13, clock=None):
        self.store, self.calls, self.sonatype_last, self.clock = store, [], sonatype_last, clock

    def fetch(self, source, url):
        self.calls.append((source['id'], url))
        if url == BOUNDED_CANDIDATE_BINDINGS[0][1]:
            body = complete_layout(1, last=1)
        elif url == BOUNDED_CANDIDATE_BINDINGS[1][1]:
            body = delinea_page(next_page=False)
        elif url == BOUNDED_CANDIDATE_BINDINGS[2][1] or url.startswith('https://www.sonatype.com/press-releases?page='):
            number = int(url.split('page=')[1]) if 'page=' in url else 1
            body = sonatype_page(number, last=self.sonatype_last)
        else:
            body = ('<html><head><link rel="canonical" href="' + url + '"></head><body><article><h1>Release</h1>'
                    + '<p>Readable primary source text supporting a diagnostic shape check. ' * 12
                    + '</p><time datetime="2026-10-22">October 22, 2026</time></article></body></html>').encode()
        return {'status': 'fetched', 'httpStatus': 200, 'requestedUrl': url, 'finalUrl': url,
                'fetchedAt': self.clock.now() if self.clock else NOW,
                'contentType': 'text/html', 'body': self.store.put(body)}


class BoundedCandidateTraversalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(Path(self.temp.name) / 'state')
        # This fixture models the original, unqualified HTML candidates.
        self.policy = json.loads((ROOT / 'web/scripts/migration-proofs/daily-v2-original/market.json').read_text())
        self.path = Path(self.temp.name) / 'plan.json'
        self.clock = Clock()

    def _start_proof(self, source, index_url, index):
        observed_url = {
            'ping-identity:official:1': 'https://press.pingidentity.com/news-releases?o=30',
            'delinea:official:1': 'https://delinea.com/news/page/2',
            'sonatype:official:1': 'https://www.sonatype.com/press-releases?page=13',
        }[source['id']]
        body = ('<html><head><link rel="canonical" href="' + index_url
                + '"></head><body>Retained diagnostic start proof.</body></html>').encode()
        body_ref = self.store.put(body)
        observed = {'status': 'fetched', 'httpStatus': 200, 'requestedUrl': observed_url,
                    'finalUrl': observed_url, 'fetchedAt': NOW, 'body': body_ref}
        observation_ref = self.store.put(observed)
        run_id = str(900 + index)
        record_key = f'ci/source-probe-runs/{run_id}-1.json'
        old_target_proof = {'type': 'prior-explicit-target-proof'}
        old_plan = {'schemaVersion': 1, 'marketSha256': digest(self.policy), 'maxRequests': 7,
                    'targets': [{'id': f'prior-{n}', 'sourceId': source['id'], 'url': observed_url,
                                 'expectedFormat': 'html', 'proof': old_target_proof} for n in range(7)]}
        old_raw = canonical(old_plan)
        old_plan_ref = self.store.put(old_raw)
        target_index = index
        row = {'targetId': f'prior-{target_index}', 'sourceId': source['id'], 'url': observed_url,
               'expectedFormat': 'html', 'proof': old_target_proof, 'observation': observation_ref,
               'reservation': {'budgetDay': '2026-10-23', 'fetchLimit': 5500, 'chargedFetchCount': target_index + 1},
               'budgetDenied': False, 'reason': 'RESPONSE_RETAINED_SCOPE_AND_HISTORY_REVIEW_REQUIRED',
               'qualified': False, 'facts': [], 'semanticAdmission': False, 'coverageCredit': False,
               'sourceChecksCredited': 0, 'qualifiedSources': 0, 'modelCalls': 0}
        validated = [dict(target, literalRecognition='html_link_feed_or_canonical') for target in old_plan['targets']]
        prior = {'rawSha256': digest(old_raw), 'canonicalSha256': digest(old_plan),
                 'marketSha256': digest(self.policy), 'maxRequests': 7, 'plan': old_plan,
                 'targets': validated, 'rawPlanReference': old_plan_ref}
        prior_targets = [dict(row, targetId=f'prior-{n}', observation=observation_ref,
                              reservation={'budgetDay': '2026-10-23', 'fetchLimit': 5500,
                                           'chargedFetchCount': n + 1}) for n in range(7)]
        diagnostic = {'contractSha256': digest(self.policy), 'checkedAt': NOW, 'executionCompleted': True,
                      'qualified': False, 'budgetDenied': False, 'semanticAdmission': False,
                      'coverageCredit': False, 'facts': [], 'sourceChecksCredited': 0, 'qualifiedSources': 0,
                      'reservationContext': {'contractSha256': digest(self.policy), 'initialBudget':
                          {'calls': 0, 'documents': 0, 'fetches': 0}, 'currentBudget':
                          {'calls': 0, 'documents': 0, 'fetches': 8}, 'fetchLimit': 5500,
                          'budgetDay': '2026-10-23', 'probeFetchReservations': 8,
                          'maximumRuntimeSeconds': 1200, 'startedAt': NOW},
                      'sources': [{'sourceId': source['id'], 'supplierId': source['supplierId'],
                          'registration': 'candidate', 'qualified': False, 'facts': [],
                          'semanticAdmission': False, 'coverageCredit': False,
                          'fetchReservations': [{'budgetDay': '2026-10-23', 'fetchLimit': 5500,
                                                'chargedFetchCount': 8}]}],
                      'qualification': {'plan': prior, 'targets': prior_targets,
                          'maximumExplicitRequests': 7, 'chargedExplicitRequests': 7,
                          'modelCalls': 0, 'semanticAdmission': False, 'coverageCredit': False,
                          'facts': [], 'sourceChecksCredited': 0, 'qualifiedSources': 0}}
        recorded = {'checkpointProfile': 'source_probe', 'contractSha256': digest(self.policy),
                    'executionCompleted': True, 'outcome': 'completed_diagnostic', 'apiFallback': False,
                    'modelCalls': 0, 'sourceChecksCredited': 0, 'qualifiedSources': 0,
                    'semanticAdmission': False, 'coverageCredit': False,
                    'githubRunId': run_id, 'githubRunAttempt': '1', 'githubEventName': 'workflow_dispatch',
                    'githubRef': 'refs/heads/main',
                    'appRevision': 'a' * 40, 'publication': {'published': False,
                        'reason': 'SOURCE_PROBE_DIAGNOSTIC_ONLY'}, 'diagnostic': diagnostic}
        self.store.write_once(record_key, recorded)
        return {'type': 'qualification_observation', 'record': {
                    'key': record_key, 'sha256': digest(canonical(recorded)),
                    'bytes': len(canonical(recorded))},
                'body': body_ref, 'fetchedAt': NOW, 'observation': observation_ref,
                'priorTargetId': f'prior-{target_index}', 'priorTargetIndex': target_index,
                'priorTargetSha256': digest(prior_targets[target_index]),
                'priorPlanRawSha256': digest(old_raw), 'priorPlanCanonicalSha256': digest(old_plan),
                'priorPlanReference': old_plan_ref}, observed

    def plan(self):
        current_sources = {row['id']: row for row in self.policy['sources']}
        source_rows = []
        for index, (source_id, index_url, mode) in enumerate(BOUNDED_CANDIDATE_BINDINGS):
            source = current_sources[source_id]
            adapter = _candidate_adapter(source, index_url, mode)
            proof, _ = self._start_proof(source, index_url, (0, 3, 6)[index])
            source_rows.append({'sourceId': source_id, 'originalSourceSha256': digest(source),
                                'proposedAdapterSha256': digest(adapter), 'startProof': proof})
        plan = {'schemaVersion': 2, 'operation': BOUNDED_CANDIDATE_OPERATION,
                'marketSha256': digest(self.policy), 'maxRequests': BOUNDED_CANDIDATE_MAX_REQUESTS,
                'maxIndexPagesPerSource': BOUNDED_CANDIDATE_LIMIT,
                'primarySamplesPerSource': 1, 'sources': source_rows}
        self.path.write_bytes(canonical(plan))
        return plan

    def _authenticated_test_authority(self):
        return (patch('onboarding._qualification_proof_policy', side_effect=lambda _r, _p, s, c, _st: (c, s)),
                patch('onboarding._qualification_explicit_observation',
                      side_effect=lambda _r, _p, s, _c, _st: {
                          'status': 'fetched', 'httpStatus': 200,
                          'requestedUrl': {'ping-identity:official:1': 'https://press.pingidentity.com/news-releases?o=30',
                              'delinea:official:1': 'https://delinea.com/news/page/2',
                              'sonatype:official:1': 'https://www.sonatype.com/press-releases?page=13'}[s['id']],
                          'finalUrl': {'ping-identity:official:1': 'https://press.pingidentity.com/news-releases?o=30',
                              'delinea:official:1': 'https://delinea.com/news/page/2',
                              'sonatype:official:1': 'https://www.sonatype.com/press-releases?page=13'}[s['id']],
                          'fetchedAt': NOW, 'body': _p['body']}))

    def test_schema2_validates_three_exact_start_proofs_and_adapter_pins(self):
        self.plan()
        auth, observation = self._authenticated_test_authority()
        with auth, observation:
            result = validate_qualification_probe_plan(self.policy, self.store, self.path)
        self.assertEqual(result['operation'], BOUNDED_CANDIDATE_OPERATION)
        self.assertEqual([row['sourceId'] for row in result['sources']], [row[0] for row in BOUNDED_CANDIDATE_BINDINGS])
        self.assertEqual(result['maxRequests'], 183)
        self.assertTrue(all(row['adapter']['registration'] == 'candidate' for row in result['sources']))

    def test_start_proof_rechecks_authenticated_run_envelope_and_zero_credit(self):
        for offset, (field, value) in enumerate((('checkpointProfile', 'ordinary'), ('githubRef', 'refs/heads/preview'),
                             ('githubEventName', 'push'), ('modelCalls', 80),
                             ('sourceChecksCredited', 3))):
            with self.subTest(field=field):
                plan = self.plan()
                proof = plan['sources'][0]['startProof']
                recorded = json.loads(self.store.get(proof['record']))
                recorded[field] = value
                altered_raw = canonical(recorded)
                run_id = str(910 + offset)
                recorded['githubRunId'] = run_id
                recorded['githubRunAttempt'] = '1'
                altered_raw = canonical(recorded)
                record_key = f'ci/source-probe-runs/{run_id}-1.json'
                self.store.write_once(record_key, recorded)
                proof['record'] = {'key': record_key, 'sha256': digest(altered_raw), 'bytes': len(altered_raw)}
                self.path.write_bytes(canonical(plan))
                auth, observation = self._authenticated_test_authority()
                with auth, observation, self.assertRaisesRegex(ValueError,
                        'BOUNDED_CANDIDATE_START_PROVENANCE_INVALID'):
                    validate_qualification_probe_plan(self.policy, self.store, self.path)

    def test_adapter_tamper_fails_full_preflight_without_transport(self):
        plan = self.plan()
        plan['sources'][0]['proposedAdapterSha256'] = '0' * 64
        self.path.write_bytes(canonical(plan))
        fetcher = CandidateFetcher(self.store)
        budget = PersistentProbeBudget(self.store, self.policy, clock=self.clock.now,
                                       monotonic=self.clock.monotonic, maximum_seconds=1200)
        auth, observation = self._authenticated_test_authority()
        with auth, observation, self.assertRaisesRegex(ValueError, 'PROPOSED_ADAPTER_BINDING_INVALID'):
            probe_sources(self.policy, self.store, fetcher,
                reservation_context=budget, qualification_plan_path=self.path)
        self.assertEqual(fetcher.calls, [])
        self.assertEqual(budget.reservations, 0)

    def test_bounded_operation_skips_generic_fanout_and_retains_unknown_terminal(self):
        self.plan()
        fetcher = CandidateFetcher(self.store)
        clock = self.clock
        budget = PersistentProbeBudget(self.store, self.policy, clock=clock.now,
                                       monotonic=clock.monotonic, maximum_seconds=1200)
        auth, observation = self._authenticated_test_authority()
        with auth, observation:
            report = probe_sources(self.policy, self.store, fetcher,
                reservation_context=budget, qualification_plan_path=self.path)
        self.assertEqual(report['operation'], BOUNDED_CANDIDATE_OPERATION)
        self.assertTrue(report['executionCompleted'])
        self.assertFalse(report['budgetDenied'])
        self.assertFalse(report['coverageCredit'])
        self.assertFalse(report['semanticAdmission'])
        self.assertEqual(report['facts'], [])
        self.assertEqual(len(fetcher.calls), 18)
        self.assertEqual(len({source_id for source_id, _ in fetcher.calls}), 3)
        rows = {row['sourceId']: row for row in report['sources']}
        self.assertTrue(rows['ping-identity:official:1']['indexComplete'])
        self.assertFalse(rows['delinea:official:1']['indexComplete'])
        self.assertEqual(rows['delinea:official:1']['reason'], 'BOUNDED_CANDIDATE_TERMINAL_UNPROVED')
        self.assertTrue(rows['sonatype:official:1']['indexComplete'])
        self.assertTrue(all(row['primarySample'] for row in rows.values()))
        original_url = rows['sonatype:official:1']['observations'][0]['url']
        rows['sonatype:official:1']['observations'][0]['url'] = original_url + '&tampered=1'
        with self.assertRaisesRegex(ValueError, 'BOUNDED_CANDIDATE_PAGE_SEQUENCE_INVALID'):
            _verify_bounded_candidate_result(self.policy, self.store,
                validate_qualification_probe_plan(self.policy, self.store, self.path), report)

    def test_deadline_after_first_response_records_uncharged_denial(self):
        self.plan()
        clock = self.clock

        class DeadlineFetcher(CandidateFetcher):
            def fetch(self, source, url):
                result = super().fetch(source, url)
                clock.elapsed = 1200
                return result

        fetcher = DeadlineFetcher(self.store)
        budget = PersistentProbeBudget(self.store, self.policy, clock=clock.now,
                                       monotonic=clock.monotonic, maximum_seconds=1200)
        auth, observation = self._authenticated_test_authority()
        with auth, observation:
            report = probe_sources(self.policy, self.store, fetcher,
                reservation_context=budget, qualification_plan_path=self.path)
        self.assertEqual(len(fetcher.calls), 1)
        self.assertTrue(report['budgetDenied'])
        self.assertFalse(report['executionCompleted'])
        self.assertEqual(report['sources'][0]['observations'][0]['url'], BOUNDED_CANDIDATE_BINDINGS[0][1])
        denial = report['sources'][0]['reservationDenials'][0]
        self.assertEqual(denial['reason'], 'SOURCE_PROBE_DEADLINE_EXCEEDED')
        self.assertFalse(denial['reservationCharged'])
        self.assertIsNone(denial['reservation'])

    def test_deadline_after_final_response_is_recorded_by_completion_guard(self):
        self.plan()
        clock = self.clock

        class FinalDeadlineFetcher(CandidateFetcher):
            def fetch(self, source, url):
                result = super().fetch(source, url)
                if len(self.calls) == 18:
                    clock.elapsed = 1200
                return result

        fetcher = FinalDeadlineFetcher(self.store)
        budget = PersistentProbeBudget(self.store, self.policy, clock=clock.now,
                                       monotonic=clock.monotonic, maximum_seconds=1200)
        auth, observation = self._authenticated_test_authority()
        with auth, observation:
            report = probe_sources(self.policy, self.store, fetcher,
                reservation_context=budget, qualification_plan_path=self.path)
        self.assertEqual(len(fetcher.calls), 18)
        self.assertTrue(report['budgetDenied'])
        self.assertFalse(report['executionCompleted'])
        denial = report['sources'][-1]['reservationDenials'][-1]
        self.assertEqual(denial['reason'], 'SOURCE_PROBE_DEADLINE_EXCEEDED')
        self.assertEqual(denial['phase'], 'post_response_completion_guard')
        self.assertFalse(denial['reservationCharged'])

    def test_replay_rejects_source_mismatch_unconsumed_rows_credit_and_ledger_drift(self):
        self.plan()
        fetcher = CandidateFetcher(self.store)
        budget = PersistentProbeBudget(self.store, self.policy, clock=self.clock.now,
                                       monotonic=self.clock.monotonic, maximum_seconds=1200)
        auth, observation = self._authenticated_test_authority()
        with auth, observation:
            report = probe_sources(self.policy, self.store, fetcher,
                reservation_context=budget, qualification_plan_path=self.path)
            plan = validate_qualification_probe_plan(self.policy, self.store, self.path)

        original_report = copy.deepcopy(report)
        ping = report['sources'][0]
        ping['observations'].append(copy.deepcopy(ping['observations'][0]))
        with self.assertRaisesRegex(ValueError, 'BOUNDED_CANDIDATE_UNCONSUMED_PAGE_ROWS'):
            _verify_bounded_candidate_result(self.policy, self.store, plan, report)
        ping['observations'].pop()

        delinea = report['sources'][1]
        delinea_observation = delinea['observations'][0]['observation']
        delinea['observations'][0]['observation'] = ping['observations'][0]['observation']
        with self.assertRaisesRegex(ValueError, 'BOUNDED_CANDIDATE_OBSERVATION_SOURCE_BINDING_INVALID'):
            _verify_bounded_candidate_result(self.policy, self.store, plan, report)
        delinea['observations'][0]['observation'] = delinea_observation

        ping['modelCalls'] = 999
        with self.assertRaisesRegex(ValueError, 'BOUNDED_CANDIDATE_SOURCE_REPORT_JOIN_INVALID'):
            _verify_bounded_candidate_result(self.policy, self.store, plan, report)
        ping['modelCalls'] = 0
        for field, value in (('newFactIds', ['injected']), ('sourceChecksCredited', 3),
                             ('qualifiedSources', 3), ('coverageCredit', True),
                             ('semanticAdmission', True), ('qualified', True), ('facts', [{'id': 'f'}])):
            original = ping[field]
            ping[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError,
                    'BOUNDED_CANDIDATE_SOURCE_REPORT_JOIN_INVALID'):
                _verify_bounded_candidate_result(self.policy, self.store, plan, report)
            ping[field] = original

        context = report['reservationContext']
        context['currentBudget']['calls'] = 80
        context['currentBudget']['documents'] = 40
        with self.assertRaisesRegex(ValueError, 'BOUNDED_CANDIDATE_NONFETCH_LEDGER_CHANGED'):
            _verify_bounded_candidate_result(self.policy, self.store, plan, report)
        context['currentBudget']['calls'] = 0
        context['currentBudget']['documents'] = 0
        context['currentBudget']['fetches'] += 1
        with self.assertRaisesRegex(ValueError, 'BOUNDED_CANDIDATE_TOTAL_REQUEST_BOUND_INVALID'):
            _verify_bounded_candidate_result(self.policy, self.store, plan, report)

        report = copy.deepcopy(original_report)
        report['reservationContext']['fetchLimit'] = 9999
        report['reservationContext']['currentBudget']['fetches'] += 5500
        for source_result in report['sources']:
            for request in source_result['requestReservations']:
                request['reservation']['chargedFetchCount'] += 5500
                request['reservation']['fetchLimit'] = 9999
        with self.assertRaisesRegex(ValueError, 'BOUNDED_CANDIDATE_RESERVATION_CONTEXT_INVALID'):
            _verify_bounded_candidate_result(self.policy, self.store, plan, report)

        report = copy.deepcopy(original_report)
        report['modelCalls'] = False
        with self.assertRaisesRegex(ValueError, 'BOUNDED_CANDIDATE_REPORT_CREDIT_OR_POLICY_INVALID'):
            _verify_bounded_candidate_result(self.policy, self.store, plan, report)

    def test_primary_redirect_and_future_time_are_retained_as_incomplete(self):
        for mode in ('redirect', 'future'):
            with self.subTest(mode=mode):
                self.plan()

                class BadSampleFetcher(CandidateFetcher):
                    def fetch(self, source, url):
                        result = super().fetch(source, url)
                        if len(self.calls) == 2:
                            if mode == 'redirect':
                                result['finalUrl'] = url + '/redirected'
                            else:
                                result['fetchedAt'] = '2030-01-01T00:00:00Z'
                        return result

                fetcher = BadSampleFetcher(self.store)
                budget = PersistentProbeBudget(self.store, self.policy, clock=self.clock.now,
                                               monotonic=self.clock.monotonic, maximum_seconds=1200)
                auth, observation = self._authenticated_test_authority()
                with auth, observation:
                    report = probe_sources(self.policy, self.store, fetcher,
                        reservation_context=budget, qualification_plan_path=self.path)
                ping = report['sources'][0]
                self.assertFalse(ping['primarySample']['shape'])
                self.assertEqual(ping['reason'], 'BOUNDED_CANDIDATE_PRIMARY_RESPONSE_INVALID' if mode == 'redirect'
                                 else 'BOUNDED_CANDIDATE_PRIMARY_RESPONSE_TIME_INVALID')

    def test_last_primary_crossing_utc_day_keeps_sample_failure_and_completion_denial(self):
        self.plan()
        clock = Clock('2026-10-23T23:59:59Z')

        class MidnightFetcher(CandidateFetcher):
            def fetch(self, source, url):
                if len(self.calls) == 17:
                    clock.wall = '2026-10-24T00:00:01Z'
                return super().fetch(source, url)

        fetcher = MidnightFetcher(self.store, clock=clock)
        budget = PersistentProbeBudget(self.store, self.policy, clock=clock.now,
                                       monotonic=clock.monotonic, maximum_seconds=1200)
        auth, observation = self._authenticated_test_authority()
        with auth, observation:
            report = probe_sources(self.policy, self.store, fetcher,
                reservation_context=budget, qualification_plan_path=self.path)
        final = report['sources'][-1]
        self.assertEqual(len(fetcher.calls), 18)
        self.assertEqual(final['reason'], 'BOUNDED_CANDIDATE_PRIMARY_RESPONSE_TIME_INVALID')
        self.assertEqual(final['completionGuardReason'], 'SOURCE_PROBE_UTC_DAY_CHANGED')
        self.assertEqual(report['reservationContext']['probeFetchReservations'], 18)
        self.assertFalse(report['executionCompleted'])
        self.assertTrue(report['budgetDenied'])

    def test_page_cap_retains_only_sequential_pages_and_never_fetches_page_61(self):
        self.plan()
        fetcher = CandidateFetcher(self.store, sonatype_last=61)
        budget = PersistentProbeBudget(self.store, self.policy, clock=self.clock.now,
                                       monotonic=self.clock.monotonic, maximum_seconds=1200)
        auth, observation = self._authenticated_test_authority()
        with auth, observation:
            report = probe_sources(self.policy, self.store, fetcher,
                reservation_context=budget, qualification_plan_path=self.path)
        sonatype = next(row for row in report['sources'] if row['sourceId'] == 'sonatype:official:1')
        self.assertEqual(len(sonatype['observations']), BOUNDED_CANDIDATE_LIMIT)
        self.assertEqual(sonatype['reason'], 'BOUNDED_CANDIDATE_PAGE_CAP_REACHED')
        self.assertFalse(sonatype['indexComplete'])
        self.assertFalse(any('page=61' in url for _, url in fetcher.calls))
        self.assertEqual(len(fetcher.calls), 65)  # 60 Sonatype pages plus the other traversals and samples
        self.assertLessEqual(len(fetcher.calls), BOUNDED_CANDIDATE_MAX_REQUESTS)

    def test_pre_reservation_lease_exhaustion_records_no_false_charge_or_transport(self):
        self.plan()
        fetcher = CandidateFetcher(self.store)
        self.store.write_once('heads/budget-2026-10-23.json', {'calls': 0, 'documents': 0, 'fetches': 5500})
        budget = PersistentProbeBudget(self.store, self.policy, clock=self.clock.now,
                                       monotonic=self.clock.monotonic, maximum_seconds=1200)
        auth, observation = self._authenticated_test_authority()
        with auth, observation:
            report = probe_sources(self.policy, self.store, fetcher,
                reservation_context=budget, qualification_plan_path=self.path)
        self.assertEqual(fetcher.calls, [])
        self.assertEqual(budget.reservations, 0)
        self.assertTrue(report['budgetDenied'])
        self.assertFalse(report['executionCompleted'])
        first = report['sources'][0]['reservationDenials'][0]
        self.assertEqual(first['reason'], 'FETCHES_BUDGET_EXHAUSTED')
        self.assertFalse(first['reservationCharged'])
        self.assertIsNone(first['reservation'])

    def test_deadline_after_reservation_is_charged_without_transport(self):
        self.plan()
        fetcher = CandidateFetcher(self.store)
        budget = PersistentProbeBudget(self.store, self.policy, clock=self.clock.now,
                                       monotonic=self.clock.monotonic, maximum_seconds=1200)
        before_fetch = budget.before_fetch

        def expire_after_reservation():
            self.clock.elapsed = 1200
            before_fetch()

        auth, observation = self._authenticated_test_authority()
        with auth, observation, patch.object(budget, 'before_fetch', side_effect=expire_after_reservation):
            report = probe_sources(self.policy, self.store, fetcher,
                reservation_context=budget, qualification_plan_path=self.path)
        self.assertEqual(fetcher.calls, [])
        self.assertEqual(budget.reservations, 1)
        denial = report['sources'][0]['reservationDenials'][0]
        self.assertEqual(denial['reason'], 'SOURCE_PROBE_DEADLINE_EXCEEDED')
        self.assertTrue(denial['reservationCharged'])
        self.assertEqual(report['reservationContext']['probeFetchReservations'], 1)


if __name__ == '__main__':
    unittest.main()
