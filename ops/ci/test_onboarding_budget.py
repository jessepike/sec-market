"""Fictional fetchers and temporary budget ledgers only; no live onboarding."""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'web/scripts/pipeline'))
import cli
from contracts import canonical
from onboarding import PersistentProbeBudget, probe_sources
from storage import LocalStore


NOW = '2026-10-23T12:00:00Z'


def contract(count=1, cap=5500):
    sources = [{'id': f'synthetic-{index}', 'supplierId': f'synthetic-{index}',
                'registration': 'candidate', 'kind': 'html_index', 'family': 'official_announcements',
                'url': f'https://example.invalid/news/{index}', 'allowedHosts': ['example.invalid'],
                'maxPages': 2, 'required': True} for index in range(count)]
    return {'schemaVersion': 1, 'version': 'synthetic-probe-budget-only',
            'schedule': {'maxFetchesPerRun': cap, 'maxRuntimeSeconds': 7200}, 'sources': sources}


class Clock:
    def __init__(self, current=NOW):
        self.current, self.elapsed = current, 0

    def now(self):
        return self.current

    def monotonic(self):
        return self.elapsed


class FictionalFetcher:
    def __init__(self, store, statuses=None, callback=None):
        self.store = store
        self.statuses = list(statuses or ['failed'])
        self.callback = callback
        self.calls = []
        self.lock = threading.Lock()

    def fetch(self, source, url):
        with self.lock:
            self.calls.append(url)
            status = self.statuses.pop(0) if self.statuses else 'failed'
        if self.callback:
            self.callback(url)
        if isinstance(status, Exception):
            raise status
        result = {'requestedUrl': url, 'fetchedAt': NOW, 'status': status}
        if status in ('fetched', 'not_modified'):
            if url.endswith('robots.txt'):
                body = b'User-agent: *\nAllow: /\n'
            elif url.endswith('sitemap.xml'):
                body = b'<urlset><url><loc>https://example.invalid/release</loc></url></urlset>'
            else:
                body = b'<html><body>Synthetic publisher.</body></html>'
            result['body'] = self.store.put(body)
        if status == 'not_modified':
            result['httpStatus'] = 304
        return result


class OnboardingBudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(Path(self.temp.name) / 'synthetic-state')
        self.clock = Clock()
        self.contract = contract()

    def budget(self, policy=None, **kwargs):
        return PersistentProbeBudget(self.store, policy or self.contract, clock=self.clock.now,
                                     monotonic=self.clock.monotonic, **kwargs)

    def seed(self, value, day='2026-10-23'):
        self.store.compare_and_swap('budget-' + day, None, value)
        return self.store.root / ('heads/budget-' + day + '.json')

    def run_probes(self, fetcher, policy=None, budget=None):
        policy = policy or self.contract
        return probe_sources(policy, self.store, fetcher, reservation_context=budget or self.budget(policy))

    def candidate_sec_recent_fixture(self):
        from regulatory import TABLE_FIELDS
        issuer = {'cik': '0001535527', 'legalName': 'CrowdStrike Holdings, Inc.', 'relationship': 'parent'}
        index = {'id': 'crwd-exposure:sec_index', 'supplierId': 'crwd-exposure',
            'family': 'regulatory_filings', 'kind': 'sec_index', 'url': 'https://data.sec.gov/submissions/CIK0001535527.json',
            'allowedHosts': ['data.sec.gov'], 'scopePrefixes': ['/submissions/'], 'maxPages': 40,
            'lookbackDays': 365, 'regulatoryIssuer': issuer, 'registration': 'candidate', 'required': True}
        documents = {'id': 'crwd-exposure:sec_documents', 'supplierId': 'crwd-exposure',
            'family': 'filing_documents', 'kind': 'sec_documents', 'registration': 'candidate',
            'url': index['url'], 'allowedHosts': ['data.sec.gov', 'www.sec.gov'],
            'scopePrefixes': ['/Archives/edgar/data/'], 'maxPages': 100, 'lookbackDays': 365,
            'cik': issuer['cik'], 'regulatoryIssuer': issuer, 'required': True}
        filing = {'accessionNumber': '0001535527-26-000001', 'filingDate': '2026-10-20',
            'reportDate': '', 'acceptanceDateTime': '2026-10-20T12:00:00Z', 'act': '34',
            'form': '8-K', 'fileNumber': '001-12345', 'filmNumber': '26123456', 'items': '5.02',
            'size': 42, 'isXBRL': 0, 'isInlineXBRL': 0, 'primaryDocument': 'release.htm',
            'primaryDocDescription': 'Synthetic release'}
        recent = {key: [filing[key]] for key in TABLE_FIELDS}
        root = {'cik': 1535527, 'name': issuer['legalName'], 'filings': {'recent': recent, 'files': []}}
        self.contract['sources'] = [index, documents]
        primary_url = 'https://www.sec.gov/Archives/edgar/data/1535527/000153552726000001/release.htm'
        return index, documents, root, primary_url

    def test_fully_charged_5500_80_40_ledger_makes_zero_requests_and_preserves_bytes(self):
        self.contract = contract(count=8)
        original = {'calls': 80, 'documents': 40, 'fetches': 5500, 'extraCounter': 12, 'extraMetadata': {'keep': True}}
        path = self.seed(original)
        before = path.read_bytes()
        sentinel = {'runId': 'do-not-touch', 'receipt': {'unchanged': True}}
        self.store.compare_and_swap('latest-run', None, sentinel)
        fetcher = FictionalFetcher(self.store)
        report = self.run_probes(fetcher)
        self.assertEqual(fetcher.calls, [])
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(report['reservationContext']['initialBudget'], original)
        self.assertEqual(report['reservationContext']['probeFetchReservations'], 0)
        self.assertEqual(report['reservationContext']['currentBudget'], original)
        self.assertTrue(report['budgetDenied'])
        self.assertFalse(report['executionCompleted'])
        self.assertEqual(report['sourceChecksCredited'], 0)
        self.assertEqual(report['qualifiedSources'], 0)
        self.assertTrue(all(row['reason'] == 'FETCHES_BUDGET_EXHAUSTED' for row in report['sources']))
        self.assertEqual(self.store.read('heads/latest-run.json'), sentinel)

    def test_parallel_last_unit_only_one_fetch_and_no_counter_overwrite(self):
        for cap, used in ((5500, 5499), (5000, 4999)):
            with self.subTest(cap=cap), tempfile.TemporaryDirectory() as directory:
                state = LocalStore(Path(directory) / 'synthetic-state')
                policy = contract(count=16, cap=cap)
                initial = {'calls': 80, 'documents': 40, 'fetches': used, 'other': 'retained'}
                state.compare_and_swap('budget-2026-10-23', None, initial)
                budget = PersistentProbeBudget(state, policy, clock=self.clock.now, monotonic=self.clock.monotonic)
                fetcher = FictionalFetcher(state)
                report = probe_sources(policy, state, fetcher, reservation_context=budget)
                self.assertEqual(len(fetcher.calls), 1)
                self.assertEqual(state.read('heads/budget-2026-10-23.json'), {**initial, 'fetches': cap})
                self.assertEqual(report['reservationContext']['probeFetchReservations'], 1)
                self.assertEqual(len([row for row in report['sources'] if row['budgetDenied']]), 15)

    def test_multiple_bound_contexts_share_the_same_persistent_lock_and_cap(self):
        from concurrent.futures import ThreadPoolExecutor
        self.contract = contract(count=4, cap=5)
        self.seed({'calls': 3, 'documents': 2, 'fetches': 4, 'extra': 7})
        budgets = [self.budget(), self.budget()]
        fetcher = FictionalFetcher(self.store)
        with ThreadPoolExecutor(max_workers=2) as pool:
            reports = list(pool.map(lambda budget: self.run_probes(fetcher, budget=budget), budgets))
        self.assertEqual(len(fetcher.calls), 1)
        self.assertEqual(sum(report['reservationContext']['probeFetchReservations'] for report in reports), 1)
        self.assertEqual(self.store.read('heads/budget-2026-10-23.json'), {'calls': 3, 'documents': 2, 'fetches': 5, 'extra': 7})

    def test_failed_blocked_304_and_exception_requests_remain_charged(self):
        for status in ('failed', 'blocked', 'not_modified', TimeoutError('synthetic timeout')):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as directory:
                state = LocalStore(Path(directory) / 'synthetic-state')
                budget = PersistentProbeBudget(state, self.contract, clock=self.clock.now, monotonic=self.clock.monotonic)
                fetcher = FictionalFetcher(state, [status])
                report = probe_sources(self.contract, state, fetcher, reservation_context=budget)
                self.assertEqual(len(fetcher.calls), 1)
                self.assertEqual(state.read('heads/budget-2026-10-23.json'), {'calls': 0, 'documents': 0, 'fetches': 1})
                self.assertEqual(report['reservationContext']['probeFetchReservations'], 1)
                self.assertFalse(report['semanticAdmission'])
                self.assertFalse(report['sources'][0]['qualified'])

    def test_each_logical_root_robots_and_sitemap_get_reserves_before_transport(self):
        self.seed({'calls': 80, 'documents': 40, 'fetches': 7, 'other': {'kept': True}})
        observed_counts = []
        fetcher = FictionalFetcher(self.store, ['fetched', 'fetched', 'fetched'],
            callback=lambda _url: observed_counts.append(self.store.read('heads/budget-2026-10-23.json')['fetches']))
        report = self.run_probes(fetcher)
        self.assertEqual(observed_counts, [8, 9, 10])
        self.assertEqual(len(fetcher.calls), 3)
        self.assertTrue(report['executionCompleted'])
        self.assertFalse(report['budgetDenied'])
        self.assertEqual(report['sources'][0]['endpoints'][0]['result'], 'DISCOVERY_ENDPOINT_RESPONDED')
        self.assertEqual(report['sources'][0]['registration'], 'candidate')
        self.assertFalse(report['sources'][0]['qualified'])
        self.assertEqual(report['facts'], [])
        self.assertEqual(self.contract['sources'][0]['registration'], 'candidate')
        self.assertIsNone(self.store.read('heads/latest-run.json'))

    def test_expired_deadline_or_day_change_starts_zero_requests_without_ledger_writes(self):
        for mode in ('deadline', 'day', 'clock-regression'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                state = LocalStore(Path(directory) / 'synthetic-state')
                state.compare_and_swap('budget-2026-10-23', None, {'calls': 80, 'documents': 40, 'fetches': 4})
                before = (state.root / 'heads/budget-2026-10-23.json').read_bytes()
                clock = Clock()
                budget = PersistentProbeBudget(state, self.contract, clock=clock.now, monotonic=clock.monotonic)
                reason = {'deadline': 'SOURCE_PROBE_DEADLINE_EXCEEDED', 'day': 'SOURCE_PROBE_UTC_DAY_CHANGED', 'clock-regression': 'SOURCE_PROBE_CLOCK_REGRESSED'}[mode]
                if mode == 'deadline':
                    clock.elapsed = 1200
                else:
                    clock.current = '2026-10-24T00:00:00Z' if mode == 'day' else '2026-10-23T11:59:59Z'
                fetcher = FictionalFetcher(state)
                report = probe_sources(self.contract, state, fetcher, reservation_context=budget)
                self.assertEqual(fetcher.calls, [])
                self.assertEqual((state.root / 'heads/budget-2026-10-23.json').read_bytes(), before)
                self.assertIsNone(state.read('heads/budget-2026-10-24.json'))
                self.assertEqual(report['sources'][0]['reason'], reason)
                self.assertFalse(report['executionCompleted'])

    def test_time_expiry_after_an_inflight_fetch_prevents_the_next_get(self):
        budget = self.budget()
        fetcher = FictionalFetcher(self.store, ['fetched'], callback=lambda _url: setattr(self.clock, 'elapsed', 1200))
        report = self.run_probes(fetcher, budget=budget)
        self.assertEqual(len(fetcher.calls), 1)
        self.assertEqual(report['sources'][0]['reason'], 'SOURCE_PROBE_DEADLINE_EXCEEDED')
        self.assertEqual(self.store.read('heads/budget-2026-10-23.json')['fetches'], 1)

    def test_day_change_after_reservation_never_refunds_or_starts_transport(self):
        budget = self.budget()
        original_guard = budget.before_fetch
        def changed_day():
            self.clock.current = '2026-10-24T00:00:00Z'
            original_guard()
        fetcher = FictionalFetcher(self.store)
        with patch.object(budget, 'before_fetch', side_effect=changed_day):
            report = self.run_probes(fetcher, budget=budget)
        self.assertEqual(fetcher.calls, [])
        self.assertEqual(self.store.read('heads/budget-2026-10-23.json')['fetches'], 1)
        self.assertIsNone(self.store.read('heads/budget-2026-10-24.json'))
        self.assertTrue(report['sources'][0]['reservationDenials'][0]['reservationCharged'])

    def test_naturally_later_day_new_bucket_does_not_change_old_5500_80_40_bucket(self):
        old = self.seed({'calls': 80, 'documents': 40, 'fetches': 5500, 'historical': 'unchanged'})
        before = old.read_bytes()
        self.clock.current = '2026-10-24T00:00:01Z'
        report = self.run_probes(FictionalFetcher(self.store))
        self.assertEqual(old.read_bytes(), before)
        self.assertEqual(self.store.read('heads/budget-2026-10-24.json'), {'calls': 0, 'documents': 0, 'fetches': 1})
        self.assertEqual(report['reservationContext']['budgetDay'], '2026-10-24')

    def test_unbounded_library_call_and_wrong_store_contract_context_fail_closed(self):
        fetcher = FictionalFetcher(self.store)
        with self.assertRaisesRegex(ValueError, 'BOUND_RESERVATION_CONTEXT_REQUIRED'):
            probe_sources(self.contract, self.store, fetcher)
        with self.assertRaisesRegex(ValueError, 'BOUND_RESERVATION_CONTEXT_REQUIRED'):
            probe_sources(self.contract, self.store, fetcher, reservation_context=lambda: None)
        budget = self.budget()
        other = LocalStore(Path(self.temp.name) / 'another-synthetic-state')
        with self.assertRaisesRegex(ValueError, 'CONTEXT_UNBOUND'):
            probe_sources(self.contract, other, fetcher, reservation_context=budget)
        changed = {**self.contract, 'version': 'changed'}
        with self.assertRaisesRegex(ValueError, 'CONTEXT_UNBOUND'):
            probe_sources(changed, self.store, fetcher, reservation_context=budget)
        self.assertEqual(fetcher.calls, [])

    def test_invalid_ledger_and_runtime_caps_are_explicit_denials(self):
        self.seed({'calls': 80, 'documents': 40, 'fetches': 'not-an-integer', 'kept': 1})
        before = (self.store.root / 'heads/budget-2026-10-23.json').read_bytes()
        report = self.run_probes(FictionalFetcher(self.store))
        self.assertEqual(report['sources'][0]['reason'], 'SOURCE_PROBE_FETCH_LEDGER_INVALID')
        self.assertEqual((self.store.root / 'heads/budget-2026-10-23.json').read_bytes(), before)
        shorter = copy.deepcopy(self.contract)
        shorter['schedule']['maxRuntimeSeconds'] = 5
        budget = self.budget(shorter)
        self.assertEqual(budget.maximum_seconds, 5)
        self.clock.elapsed = 5
        report = self.run_probes(FictionalFetcher(self.store), shorter, budget)
        self.assertEqual(report['sources'][0]['reason'], 'SOURCE_PROBE_DEADLINE_EXCEEDED')
        for policy in (contract(cap=5501), contract(cap=True)):
            with self.assertRaisesRegex(ValueError, 'FETCH_LIMIT_INVALID'):
                self.budget(policy)
        with self.assertRaisesRegex(ValueError, 'RUNTIME_LIMIT_INVALID'):
            self.budget(maximum_seconds=1201)

    def test_reservation_persistence_failure_is_explicit_and_starts_no_fetch(self):
        budget = self.budget()
        fetcher = FictionalFetcher(self.store)
        with patch.object(self.store, 'compare_and_swap', side_effect=OSError('synthetic persistence failure')):
            report = self.run_probes(fetcher, budget=budget)
        self.assertEqual(fetcher.calls, [])
        self.assertTrue(report['budgetDenied'])
        self.assertFalse(report['executionCompleted'])
        self.assertEqual(report['sources'][0]['reason'], 'SOURCE_PROBE_RESERVATION_PERSISTENCE_FAILED')
        self.assertIsNone(report['sources'][0]['reservationDenials'][0]['reservationCharged'])
        self.assertIsNone(self.store.read('heads/budget-2026-10-23.json'))

    def test_probe_worker_concurrency_is_bounded_at_four(self):
        self.contract = contract(count=8)
        barrier = threading.Barrier(4)
        lock = threading.Lock()
        active, maximum = 0, 0
        def synchronized_fetch(_url):
            nonlocal active, maximum
            with lock:
                active += 1
                maximum = max(maximum, active)
            barrier.wait(timeout=5)
            with lock:
                active -= 1
        fetcher = FictionalFetcher(self.store, callback=synchronized_fetch)
        report = self.run_probes(fetcher)
        self.assertEqual(maximum, 4)
        self.assertEqual(len(fetcher.calls), 8)
        self.assertTrue(report['executionCompleted'])
        self.assertEqual(report['sourceChecksCredited'], 0)

    def test_candidate_sec_pair_fetches_selected_primary_under_document_source_id(self):
        from regulatory import TABLE_FIELDS
        issuer = {'cik': '0001535527', 'legalName': 'CrowdStrike Holdings, Inc.', 'relationship': 'parent'}
        index = self.contract['sources'][0]
        index.update({'id': 'crwd-exposure:sec_index', 'supplierId': 'crwd-exposure',
            'family': 'regulatory_filings', 'kind': 'sec_index', 'url': 'https://data.sec.gov/submissions/CIK0001535527.json',
            'allowedHosts': ['data.sec.gov'], 'scopePrefixes': ['/submissions/'], 'maxPages': 40,
            'lookbackDays': 365, 'regulatoryIssuer': issuer, 'registration': 'candidate'})
        documents = {'id': 'crwd-exposure:sec_documents', 'supplierId': 'crwd-exposure',
            'family': 'filing_documents', 'kind': 'sec_documents', 'registration': 'candidate',
            'url': index['url'], 'allowedHosts': ['data.sec.gov', 'www.sec.gov'],
            'scopePrefixes': ['/Archives/edgar/data/'], 'maxPages': 100, 'lookbackDays': 365,
            'cik': issuer['cik'], 'regulatoryIssuer': issuer, 'required': True}
        self.contract['sources'] = [index, documents]
        filing = {'accessionNumber': '0001535527-26-000001', 'filingDate': '2026-10-20',
            'reportDate': '', 'acceptanceDateTime': '2026-10-20T12:00:00Z', 'act': '34',
            'form': '8-K', 'fileNumber': '001-12345', 'filmNumber': '26123456', 'items': '5.02',
            'size': 42, 'isXBRL': 0, 'isInlineXBRL': 0, 'primaryDocument': 'release.htm',
            'primaryDocDescription': 'Synthetic release'}
        table = {key: [] for key in TABLE_FIELDS}
        older_table = {key: [filing[key]] for key in TABLE_FIELDS}
        older_url = 'https://data.sec.gov/submissions/CIK0001535527-submissions-001.json'
        root = {'cik': 1535527, 'name': issuer['legalName'], 'filings': {'recent': table, 'files': [
            {'name': 'CIK0001535527-submissions-001.json', 'filingCount': 1,
             'filingFrom': '2026-10-20', 'filingTo': '2026-10-20'}]}}
        older = older_table
        primary_url = 'https://www.sec.gov/Archives/edgar/data/1535527/000153552726000001/release.htm'
        calls = []
        class JsonAndBodyFetcher:
            def fetch(inner, received_source, url):
                calls.append((received_source['id'], url))
                if url == index['url']:
                    raw = json.dumps(root).encode()
                elif url == older_url:
                    raw = json.dumps(older).encode()
                else:
                    raw = ('<html><body>' + ('Readable primary filing body. ' * 20) + '</body></html>').encode()
                return {'requestedUrl': url, 'finalUrl': url, 'fetchedAt': NOW, 'status': 'fetched',
                        'httpStatus': 200, 'contentType': 'application/json' if url != primary_url else 'text/html',
                        'body': self.store.put(raw)}
        report = self.run_probes(JsonAndBodyFetcher())
        by_source = {row['sourceId']: row for row in report['sources']}
        self.assertEqual(calls, [('crwd-exposure:sec_index', index['url']),
                                 ('crwd-exposure:sec_index', older_url),
                                 ('crwd-exposure:sec_documents', primary_url)])
        index_row = by_source['crwd-exposure:sec_index']
        document_row = by_source['crwd-exposure:sec_documents']
        self.assertTrue(index_row['secIndexDiagnostic']['allRequiredPagesFetched'])
        self.assertEqual(len(index_row['observations']), 2)
        for reference in index_row['observations']:
            self.assertEqual(json.loads(self.store.get(reference))['sourceId'], 'crwd-exposure:sec_index')
        self.assertEqual(index_row['secIndexDiagnostic']['requiredOlderPages'][0]['url'], older_url)
        self.assertEqual(document_row['secDocumentsDiagnostic']['selectedCount'], 1)
        self.assertTrue(document_row['secDocumentsDiagnostic']['allSelectedBodiesFetched'])
        observation = json.loads(self.store.get(document_row['observations'][0]))
        self.assertEqual(observation['sourceId'], 'crwd-exposure:sec_documents')
        self.assertEqual(document_row['secDocumentsDiagnostic']['indexObservations'], index_row['observations'])
        self.assertEqual(len(document_row['secDocumentsDiagnostic']['primaryDocuments']), 1)
        self.assertEqual(document_row['secDocumentsDiagnostic']['primaryDocuments'][0]['filingDate'], '2026-10-20')
        self.assertIsNotNone(self.store.get(document_row['secDocumentsDiagnostic']['primaryDocuments'][0]['readableText']))
        self.assertFalse(document_row['secDocumentsDiagnostic']['semanticEvidence'])
        self.assertFalse(document_row['qualified'])
        self.assertEqual(document_row['facts'], [])
        self.assertEqual(report['sourceChecksCredited'], 0)

    def test_candidate_sec_ambiguous_join_fails_before_any_request(self):
        issuer = {'cik': '0001535527', 'legalName': 'CrowdStrike Holdings, Inc.', 'relationship': 'parent'}
        index = {'id': 'crwd-exposure:sec_index', 'supplierId': 'crwd-exposure',
            'family': 'regulatory_filings', 'kind': 'sec_index', 'url': 'https://data.sec.gov/submissions/CIK0001535527.json',
            'allowedHosts': ['data.sec.gov'], 'scopePrefixes': ['/submissions/'], 'maxPages': 40,
            'lookbackDays': 365, 'regulatoryIssuer': issuer, 'registration': 'candidate', 'required': True}
        duplicate = copy.deepcopy(index)
        duplicate['id'] = 'crwd-exposure:sec_index_duplicate'
        documents = {'id': 'crwd-exposure:sec_documents', 'supplierId': 'crwd-exposure',
            'family': 'filing_documents', 'kind': 'sec_documents', 'registration': 'candidate',
            'url': index['url'], 'allowedHosts': ['data.sec.gov', 'www.sec.gov'],
            'scopePrefixes': ['/Archives/edgar/data/'], 'maxPages': 100, 'lookbackDays': 365,
            'cik': issuer['cik'], 'regulatoryIssuer': issuer, 'required': True}
        self.contract['sources'] = [index, duplicate, documents]
        self.contract['sources'].append({'id': 'ordinary-candidate', 'supplierId': 'ordinary-candidate',
            'registration': 'candidate', 'kind': 'html_index', 'family': 'official_announcements',
            'url': 'https://example.invalid/news', 'allowedHosts': ['example.invalid'],
            'maxPages': 2, 'required': True})
        fetcher = FictionalFetcher(self.store)
        report = self.run_probes(fetcher)
        self.assertEqual(fetcher.calls, [])
        by_source = {row['sourceId']: row for row in report['sources']}
        self.assertTrue(all(by_source[source_id]['reason'] == 'SEC_DIAGNOSTIC_EXACT_ONE_TO_ONE_SOURCE_JOIN_REQUIRED'
                            for source_id in (index['id'], duplicate['id'], documents['id'])))
        self.assertEqual(by_source['ordinary-candidate']['reason'],
                         'SEC_DIAGNOSTIC_PREFLIGHT_BLOCKED_ALL_TRANSPORT')

    def test_candidate_sec_final_deadline_and_utc_rollover_hold_both_rows_incomplete(self):
        for mode in ('deadline', 'day'):
            with self.subTest(mode=mode):
                self.store = LocalStore(Path(self.temp.name) / ('synthetic-' + mode))
                self.clock = Clock()
                index, documents, root, primary_url = self.candidate_sec_recent_fixture()
                calls = []
                class LastFetchExpires:
                    def fetch(inner, received_source, url):
                        calls.append((received_source['id'], url))
                        if url == index['url']:
                            raw = json.dumps(root).encode()
                            return {'requestedUrl': url, 'finalUrl': url, 'fetchedAt': NOW, 'status': 'fetched',
                                    'httpStatus': 200, 'contentType': 'application/json', 'body': self.store.put(raw)}
                        if url == primary_url:
                            if mode == 'deadline':
                                self.clock.elapsed = 1201
                            else:
                                self.clock.current = '2026-10-24T00:00:00Z'
                            raw = ('<html><body>' + ('Readable primary filing body. ' * 20) + '</body></html>').encode()
                            return {'requestedUrl': url, 'finalUrl': url, 'fetchedAt': NOW, 'status': 'fetched',
                                    'httpStatus': 200, 'contentType': 'text/html', 'body': self.store.put(raw)}
                        raise AssertionError('unexpected SEC request: ' + url)
                report = self.run_probes(LastFetchExpires())
                by_source = {row['sourceId']: row for row in report['sources']}
                expected = 'SOURCE_PROBE_DEADLINE_EXCEEDED' if mode == 'deadline' else 'SOURCE_PROBE_UTC_DAY_CHANGED'
                self.assertEqual(calls, [('crwd-exposure:sec_index', index['url']),
                                         ('crwd-exposure:sec_documents', primary_url)])
                for row in by_source.values():
                    self.assertEqual(row['reason'], expected)
                    self.assertFalse(row['executionCompleted'])
                    self.assertTrue(row['budgetDenied'])
                    self.assertEqual(row['reservationDenials'][-1]['reason'], expected)
                self.assertFalse(by_source[index['id']]['secIndexDiagnostic']['allRequiredPagesFetched'])
                self.assertFalse(by_source[documents['id']]['secDocumentsDiagnostic']['allSelectedBodiesFetched'])

    def test_candidate_sec_pre_and_post_reservation_denials_report_charge_truthfully(self):
        for mode in ('pre-reservation', 'post-reservation'):
            with self.subTest(mode=mode):
                self.store = LocalStore(Path(self.temp.name) / ('synthetic-' + mode))
                self.clock = Clock()
                index, documents, root, _primary_url = self.candidate_sec_recent_fixture()
                if mode == 'pre-reservation':
                    self.seed({'calls': 80, 'documents': 40, 'fetches': 5500})
                budget = self.budget()
                if mode == 'post-reservation':
                    original_before_fetch = budget.before_fetch
                    def expire_after_reservation():
                        self.clock.elapsed = 1201
                        original_before_fetch()
                    budget.before_fetch = expire_after_reservation
                report = self.run_probes(FictionalFetcher(self.store), budget=budget)
                row = next(item for item in report['sources'] if item['sourceId'] == index['id'])
                denial = row['reservationDenials'][0]
                self.assertEqual(denial['reason'], 'FETCHES_BUDGET_EXHAUSTED' if mode == 'pre-reservation'
                                 else 'SOURCE_PROBE_DEADLINE_EXCEEDED')
                self.assertIs(denial['reservationCharged'], mode == 'post-reservation')
                self.assertEqual(len(row['fetchReservations']), 0 if mode == 'pre-reservation' else 1)
                self.assertEqual(budget.summary()['probeFetchReservations'], 0 if mode == 'pre-reservation' else 1)

    def test_candidate_sec_failed_primary_body_is_retained_as_incomplete(self):
        from regulatory import TABLE_FIELDS
        issuer = {'cik': '0001535527', 'legalName': 'CrowdStrike Holdings, Inc.', 'relationship': 'parent'}
        index = {'id': 'crwd-exposure:sec_index', 'supplierId': 'crwd-exposure',
            'family': 'regulatory_filings', 'kind': 'sec_index', 'url': 'https://data.sec.gov/submissions/CIK0001535527.json',
            'allowedHosts': ['data.sec.gov'], 'scopePrefixes': ['/submissions/'], 'maxPages': 40,
            'lookbackDays': 365, 'regulatoryIssuer': issuer, 'registration': 'candidate', 'required': True}
        documents = {'id': 'crwd-exposure:sec_documents', 'supplierId': 'crwd-exposure',
            'family': 'filing_documents', 'kind': 'sec_documents', 'registration': 'candidate',
            'url': index['url'], 'allowedHosts': ['data.sec.gov', 'www.sec.gov'],
            'scopePrefixes': ['/Archives/edgar/data/'], 'maxPages': 100, 'lookbackDays': 365,
            'cik': issuer['cik'], 'regulatoryIssuer': issuer, 'required': True}
        self.contract['sources'] = [index, documents]
        filing = {'accessionNumber': '0001535527-26-000001', 'filingDate': '2026-10-20',
            'reportDate': '', 'acceptanceDateTime': '2026-10-20T12:00:00Z', 'act': '34',
            'form': '8-K', 'fileNumber': '001-12345', 'filmNumber': '26123456', 'items': '5.02',
            'size': 42, 'isXBRL': 0, 'isInlineXBRL': 0, 'primaryDocument': 'release.htm',
            'primaryDocDescription': 'Synthetic release'}
        recent = {key: [filing[key]] for key in TABLE_FIELDS}
        root = {'cik': 1535527, 'name': issuer['legalName'], 'filings': {'recent': recent, 'files': []}}
        primary_url = 'https://www.sec.gov/Archives/edgar/data/1535527/000153552726000001/release.htm'
        calls = []
        class FailedPrimaryFetcher:
            def fetch(inner, received_source, url):
                calls.append((received_source['id'], url))
                if url == index['url']:
                    raw = json.dumps(root).encode()
                    return {'requestedUrl': url, 'finalUrl': url, 'fetchedAt': NOW, 'status': 'fetched',
                            'httpStatus': 200, 'contentType': 'application/json', 'body': self.store.put(raw)}
                return {'requestedUrl': url, 'finalUrl': url, 'fetchedAt': NOW, 'status': 'blocked',
                        'httpStatus': 403, 'errorCode': 'HTTP_403'}
        report = self.run_probes(FailedPrimaryFetcher())
        by_source = {row['sourceId']: row for row in report['sources']}
        row = by_source['crwd-exposure:sec_documents']
        self.assertEqual(calls, [('crwd-exposure:sec_index', index['url']),
                                 ('crwd-exposure:sec_documents', primary_url)])
        self.assertEqual(row['reason'], 'SEC_DIAGNOSTIC_PRIMARY_BODY_RESPONSE_INVALID')
        self.assertFalse(row['secDocumentsDiagnostic']['allSelectedBodiesFetched'])
        self.assertEqual(row['secDocumentsDiagnostic']['primaryDocuments'][0]['httpStatus'], 403)
        self.assertEqual(report['sourceChecksCredited'], 0)

    def cli_args(self, extra=None):
        path = Path(self.temp.name) / 'synthetic-contract.json'
        path.write_bytes(canonical(self.contract))
        return ['cli.py', 'onboard', '--contract', str(path), '--state', str(self.store.root), *(extra or [])]

    def test_cli_rejects_backdating_and_worker_flags_before_fetch(self):
        for flags in (['--at', NOW], ['--native-worker'], ['--subscription-worker'], ['--session-id', 'synthetic']):
            with self.subTest(flags=flags), patch.object(sys, 'argv', self.cli_args(flags)), \
                    patch.object(cli, 'validate_contract', side_effect=lambda value: value), \
                    patch.object(cli, 'Fetcher') as fetcher, contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                cli.main()
            fetcher.assert_not_called()

    def test_cli_standalone_rejects_before_contract_state_or_transport(self):
        self.seed({'calls': 80, 'documents': 40, 'fetches': 5500})
        before = (self.store.root / 'heads/budget-2026-10-23.json').read_bytes()
        with patch.object(sys, 'argv', self.cli_args()), patch.object(cli, 'validate_contract') as validator, \
                patch.object(cli, 'LocalStore') as state, patch.object(cli, 'Fetcher') as fetcher, \
                contextlib.redirect_stderr(io.StringIO()) as output, self.assertRaises(SystemExit) as raised:
            cli.main()
        self.assertEqual(raised.exception.code, 2)
        self.assertIn('leased diagnostics', output.getvalue())
        validator.assert_not_called()
        state.assert_not_called()
        fetcher.assert_not_called()
        self.assertEqual((self.store.root / 'heads/budget-2026-10-23.json').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
