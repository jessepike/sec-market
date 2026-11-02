"""Closed source-adapter tests. All transports are local synthetic responses."""
import copy
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'web/scripts/pipeline'), str(ROOT / 'ops/ci')]
from contracts import digest
from storage import LocalStore
from fetcher import Fetcher
import three_source_discovery as adapter
import test_cyera_press_list as cyera
import test_prnewswire_press_list as prn
import test_prnewswire_primary_capture as primary

NOW = '2026-10-25T15:00:00Z'


def source(sid):
    market = json.loads((ROOT / 'contracts/market.json').read_bytes())
    row = copy.deepcopy(next(value for value in market['sources'] if value['id'] == sid))
    mode = adapter.CYERA_MODE if sid == cyera.parser.SOURCE else adapter.PRN_MODE
    url = cyera.parser.INDEX if sid == cyera.parser.SOURCE else prn.parser.index_url(sid)
    row.update(kind='html_index', registration='verified', htmlCompleteness=mode, url=url)
    return row


def observation(row, url, body, **changes):
    return {'sourceId': row['id'], 'observationId': 'a' * 64, 'requestedUrl': url, 'finalUrl': url,
            'status': 'fetched', 'httpStatus': 200, 'fetchedAt': NOW, 'contentType': 'text/html; charset=utf-8',
            'body': {'key': 'objects/' + digest(body), 'sha256': digest(body), 'bytes': len(body)}, **changes}


class ClosedAdapterTests(unittest.TestCase):
    def setUp(self):
        self.net = patch.object(socket.socket, 'connect', side_effect=AssertionError('NO_SOURCE_NETWORK'))
        self.net.start(); self.addCleanup(self.net.stop)

    def test_authentic_cyera_finite_list_keeps_56_dates_and_five_seeds(self):
        row = source('cyera:official:1')
        plan = json.loads(cyera.PLAN.read_bytes())
        body = cyera.FixtureStore().get(plan['retainedIndex']['body'])
        calls = []
        def request(url):
            calls.append(url)
            return observation(row, url, body), body
        result = adapter.discover_bound(row, request)
        self.assertTrue(result['complete'], result['reason'])
        self.assertEqual(calls, [row['url']])
        self.assertEqual(len(result['items']), 56)
        stream = result['sourceWindow']['stream']
        self.assertEqual(stream['asOf'], NOW)
        self.assertEqual(len(stream['knownSeedMembership']), 5)
        self.assertTrue(all(stream['knownSeedMembership'].values()))
        self.assertTrue(all('T' not in date for date in result['itemDates'].values()))
        self.assertIsNone(result['timezone'])

    def test_authentic_prn_prefixes_stop_at_daily_boundary_without_history_credit(self):
        plan = json.loads(primary.PLAN.read_bytes())
        frozen = primary.FixtureStore()
        for item in plan['sources']:
            with self.subTest(sid=item['sourceId']):
                row = source(item['sourceId'])
                body = frozen.get(item['listPage']['body'])
                calls = []
                def request(url):
                    calls.append(url)
                    return observation(row, url, body), body
                result = adapter.discover_bound(row, request)
                self.assertTrue(result['complete'], result['reason'])
                self.assertEqual(calls, [row['url']])
                self.assertEqual(len(result['items']), 25)
                self.assertFalse(result['sourceWindow']['historicalEnumerationComplete'])
                self.assertTrue(result['sourceWindow']['stream']['pendingLiteralPaginationUrls'])
                self.assertEqual(row['family'], 'release_distribution')

    def test_connected_pagination_is_followed_only_until_older_boundary(self):
        row = source(prn.SID)
        bodies = [prn.page([prn.card(i) for i in range(25)], terminal=False),
                  prn.page([prn.card(25, 'Sep 24, 2026, 09:00 ET')], number=2)]
        calls = []
        def request(url):
            body = bodies[len(calls)]
            calls.append(url)
            return observation(row, url, body), body
        result = adapter.discover_bound(row, request)
        self.assertTrue(result['complete'], result['reason'])
        self.assertEqual(calls, [row['url'], prn.parser.index_url(prn.SID, 2)])
        self.assertEqual(len(result['items']), 26)
        self.assertTrue(result['sourceWindow']['historicalEnumerationComplete'])

    def test_missing_later_page_keeps_original_prefix_and_failure_observation(self):
        row = source(prn.SID)
        body = prn.page([prn.card(i) for i in range(25)], terminal=False)
        calls = []
        def request(url):
            calls.append(url)
            if len(calls) == 2:
                return observation(row, url, b'blocked', status='blocked', httpStatus=403), b'blocked'
            return observation(row, url, body), body
        result = adapter.discover_bound(row, request)
        self.assertFalse(result['complete'])
        self.assertEqual(len(result['items']), 25)
        self.assertEqual(len(result['observations']), 2)
        self.assertFalse(result['currentWindowQuiet'])
        self.assertIn('THREE_SOURCE_INDEX_HTTP_INVALID', result['reason'])

    def test_eight_page_bound_never_guesses_another_page(self):
        row = source(prn.SID)
        calls = []
        def request(url):
            number = len(calls) + 1
            calls.append(url)
            body = prn.page([prn.card((number - 1) * 25 + i) for i in range(25)],
                            number=number, terminal=False)
            if 2 <= number <= 7:
                numbered = ''.join('<li' + (' class="active"' if n == number else '') + '><a' +
                    ('' if n == number else ' href="?page=' + str(n) + '&amp;pagesize=25"') + '>' + str(n) + '</a></li>'
                    for n in range(max(1, number - 2), number + 2))
                controls = ('<li><a aria-label="Previous" href="?page=' + str(number - 1) +
                    '&amp;pagesize=25"><span aria-hidden="true">«</span></a></li>' + numbered +
                    '<li><a aria-label="Next" href="?page=' + str(number + 1) +
                    '&amp;pagesize=25"><span aria-hidden="true">»</span></a></li>').encode()
                before, after = body.split(b'<ul class="pagination">')
                body = before + b'<ul class="pagination">' + controls + b'</ul>' + after.split(b'</ul>', 1)[1]
            return observation(row, url, body), body
        result = adapter.discover_bound(row, request)
        self.assertFalse(result['complete'])
        self.assertEqual(len(calls), 8)
        self.assertEqual(calls, [prn.parser.index_url(prn.SID, n) for n in range(1, 9)])
        self.assertEqual(len(result['items']), 175)
        self.assertFalse(result['currentWindowQuiet'])
        self.assertTrue(result['sourceWindow']['stream']['pendingLiteralPaginationUrls'])

    def test_request_exception_keeps_disclosed_prefix_and_never_guesses_next(self):
        row = source(prn.SID)
        calls = []
        def request(url):
            calls.append(url)
            if len(calls) == 2:
                raise OSError('synthetic request interruption')
            body = prn.page([prn.card(i) for i in range(25)], terminal=False)
            return observation(row, url, body), body
        result = adapter.discover_bound(row, request)
        self.assertFalse(result['complete'])
        self.assertEqual(calls, [row['url'], prn.parser.index_url(prn.SID, 2)])
        self.assertEqual(len(result['items']), 25)
        self.assertEqual(len(result['observations']), 1)
        self.assertFalse(result['currentWindowQuiet'])
        self.assertIn('synthetic request interruption', result['reason'])

    def test_empty_and_preserved_prefix_budget_denials_replay_same_incomplete_proof(self):
        row = source(prn.SID)
        body = prn.page([prn.card(i) for i in range(25)], terminal=False)
        for permitted in (0, 1):
            observed = {}
            sends = []
            def request(url):
                if len(sends) >= permitted:
                    raise ValueError('FETCH_BUDGET_EXHAUSTED')
                sends.append(url)
                value = observation(row, url, body)
                observed[url] = (value, body)
                return value, body
            found = adapter.discover_bound(row, request)
            def replay(url):
                if url not in observed:
                    raise ValueError('Retained discovery observation missing')
                return observed[url]
            repeated = adapter.discover_bound(row, replay)
            self.assertFalse(found['complete']); self.assertFalse(repeated['complete'])
            self.assertEqual(len(sends), permitted)
            self.assertEqual(len(found['items']), 25 if permitted else 0)
            self.assertIn('FETCH_BUDGET_EXHAUSTED', found['reason'])
            self.assertEqual(found['sourceWindow']['reason'], 'DAILY_WINDOW_UNPROVED')
            adapter.verify_window(repeated, {'sourceWindow': found['sourceWindow']})

    def test_genuine_http_failure_metadata_is_retained_and_replayed(self):
        row = source(prn.SID)
        raw = b'Publisher returned a genuine blocked response'
        observed = observation(row, row['url'], raw, status='blocked', httpStatus=403)
        found = adapter.discover_bound(row, lambda url: (observed, raw))
        repeated = adapter.discover_bound(row, lambda url: (copy.deepcopy(observed), raw))
        adapter.verify_window(repeated, {'sourceWindow': found['sourceWindow']})
        self.assertFalse(found['complete'])
        self.assertEqual(found['observations'][0], observed)
        self.assertEqual(found['sourceWindow']['observations'][0]['httpStatus'], 403)
        changed = copy.deepcopy(found['sourceWindow']); changed['observations'][0]['httpStatus'] = 404
        with self.assertRaises(ValueError): adapter.verify_window(repeated, {'sourceWindow': changed})

    def test_source_identity_widening_denied_before_request(self):
        row = source(prn.SID)
        for key, value in (('family', 'official_announcements'), ('allowedHosts', ['elsewhere.invalid']),
                           ('url', row['url'] + '?page=2'), ('maxPages', True),
                           ('registration', 'candidate'), ('id', 'other:official:1')):
            altered = copy.deepcopy(row); altered[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                adapter.discover_bound(altered, lambda url: self.fail('request before source validation'))

    def test_transport_clock_mime_body_and_reuse_failures_are_incomplete(self):
        row = source(prn.SID)
        body = prn.page([prn.card(1, 'Sep 24, 2026, 09:00 ET')])
        good = observation(row, row['url'], body)
        for key, value in (('sourceId', 'other:official:1'), ('finalUrl', row['url'] + '?x=1'),
                           ('contentType', 'application/json'), ('httpStatus', True), ('body', None),
                           ('fetchedAt', None), ('status', 'failed')):
            altered = {**good, key: value}
            with self.subTest(key=key):
                result = adapter.discover_bound(row, lambda url: (altered, body))
                self.assertFalse(result['complete'])
                self.assertFalse(result['currentWindowQuiet'])
        bad_reuse = {**good, 'status': 'not_modified', 'httpStatus': 304}
        self.assertFalse(adapter.discover_bound(row, lambda url: (bad_reuse, body))['complete'])

    def test_cross_utc_day_traversal_is_incomplete_and_preserves_first_clock(self):
        row = source(prn.SID)
        bodies = [prn.page([prn.card(i) for i in range(25)], terminal=False),
                  prn.page([prn.card(25, 'Sep 24, 2026, 09:00 ET')], number=2)]
        calls = []
        def request(url):
            body = bodies[len(calls)]; calls.append(url)
            when = NOW if len(calls) == 1 else '2026-10-26T00:00:01Z'
            return observation(row, url, body, fetchedAt=when), body
        result = adapter.discover_bound(row, request)
        self.assertFalse(result['complete'])
        self.assertEqual(result['sourceWindow']['asOf'], NOW)
        self.assertEqual(len(result['observations']), 2)
        self.assertIn('WINDOW_DAY_CHANGED', result['reason'])

    def test_future_boundary_and_unknown_dates_remain_explicit_and_never_quiet(self):
        row = source(prn.SID)
        for date in ('Oct 25, 2026, 08:30 ET', 'Oct 27, 2026, 08:30 ET', None):
            body = prn.page([prn.card(1, date), prn.card(2, 'Sep 24, 2026, 09:00 ET')])
            result = adapter.discover_bound(row, lambda url: (observation(row, url, body), body))
            self.assertFalse(result['currentWindowQuiet'])
            if date is None:
                self.assertFalse(result['complete'])
                self.assertEqual(len(result['sourceWindow']['stream']['unresolvedDateItems']), 1)
            elif date.startswith('Oct 27'):
                self.assertEqual(len(result['undeterminedWindowItems']), 1)
                self.assertEqual(len(result['sourceDateAnomalies']), 1)
            else:
                self.assertEqual(len(result['boundaryAmbiguousItems']), 1)

    def test_literal_inert_presence_is_denied_for_both_parsers(self):
        row = source(prn.SID)
        prn_body = prn.page([prn.card(1), prn.card(2, 'Sep 24, 2026, 09:00 ET')])
        cyera_body = cyera.page([cyera.card(), cyera.card(2, 'Sep 22, 2026')])
        for value in (b' inert', b' inert="false"'):
            with self.subTest(value=value):
                altered = prn_body.replace(b'<main ', b'<main' + value + b' ', 1)
                self.assertFalse(adapter.discover_bound(row, lambda url: (observation(row, url, altered), altered))['complete'])
                with self.assertRaises(ValueError):
                    cyera.parser.parse_press_list(cyera_body.replace(b'<main>', b'<main' + value + b'>'),
                                                   cyera.parser.SOURCE, cyera.AS_OF)

    def test_window_proof_missing_extra_or_changed_fields_reject(self):
        row = source(prn.SID)
        body = prn.page([prn.card(1, 'Sep 24, 2026, 09:00 ET')])
        result = adapter.discover_bound(row, lambda url: (observation(row, url, body), body))
        manifest = {'sourceWindow': copy.deepcopy(result['sourceWindow'])}
        adapter.verify_window(result, manifest)
        for change in (lambda value: value.clear(),
                       lambda value: value['sourceWindow'].update(extra=True),
                       lambda value: value['sourceWindow'].update(historicalEnumerationComplete=False),
                       lambda value: value['sourceWindow']['stream'].update(asOf='2026-10-26T00:00:00Z')):
            altered = copy.deepcopy(manifest); change(altered)
            with self.assertRaises(ValueError): adapter.verify_window(result, altered)
        self.assertFalse(adapter.matches({'id': 'jfrog:official:1', 'htmlCompleteness': 'q4_press_list'}))

    def test_genuine_fetcher_200_then_304_keeps_body_and_fresh_index_clock(self):
        row = source(prn.SID)
        body = prn.page([prn.card(1, 'Sep 24, 2026, 09:00 ET')])
        with tempfile.TemporaryDirectory() as directory:
            store = LocalStore(Path(directory) / 'state')
            class Response(io.BytesIO):
                status = 200
                headers = {'Content-Type': 'text/html; charset=utf-8', 'ETag': '"fixture"'}
                url = row['url']
            with patch('fetcher.safe_url', side_effect=lambda url, *_a, **_k: url), \
                 patch('fetcher.urllib.request.build_opener', return_value=SimpleNamespace(open=lambda *a, **k: Response(body))), \
                 patch('fetcher.utcnow', return_value=NOW):
                first = Fetcher(store).fetch(row, row['url'])
            first.update(sourceId=row['id'], observationId='a' * 64)
            def unchanged(*args, **kwargs):
                raise HTTPError(row['url'], 304, 'Not modified', {'Content-Type': 'text/html'}, None)
            later = '2026-10-25T16:00:00Z'
            with patch('fetcher.safe_url', side_effect=lambda url, *_a, **_k: url), \
                 patch('fetcher.urllib.request.build_opener', return_value=SimpleNamespace(open=unchanged)), \
                 patch('fetcher.utcnow', return_value=later):
                fresh = Fetcher(store).fetch(row, row['url'], first)
            fresh.update(sourceId=row['id'], observationId='b' * 64)
            result = adapter.discover_bound(row, lambda url: (fresh, store.get(fresh['body'])))
            self.assertTrue(result['complete'], result['reason'])
            self.assertEqual(fresh['body'], first['body'])
            self.assertEqual(result['sourceWindow']['asOf'], later)
            self.assertEqual(fresh['reusesObservationId'], first['observationId'])



class OrdinaryPipelineTests(unittest.TestCase):
    def setUp(self):
        from test_three_source_qualification_seed import Committed
        from contracts import plan_run
        from engine import Pipeline
        from retained_audit import index_for, activate_compatibility
        self.tmp = tempfile.TemporaryDirectory(prefix='SYNTHETIC-three-source-ordinary-')
        self.addCleanup(self.tmp.cleanup)
        self.market = json.loads((ROOT / 'contracts/market.json').read_bytes())
        self.store = LocalStore(Path(self.tmp.name))
        for key, raw in Committed().files.items(): self.store.write_once(key, raw)
        self.now = '2026-10-27T16:00:00Z'
        self.plan = plan_run(self.market, self.now)
        self.store.write_once('runs/' + self.plan['runId'] + '/plan.json', self.plan)
        self.store.write_once('contracts/' + digest(self.market) + '.json', self.market)
        self.wire = []
        self.bodies = {}
        frozen = primary.FixtureStore()
        for row in json.loads(primary.PLAN.read_bytes())['sources']:
            self.bodies[row['sourceId']] = frozen.get(row['listPage']['body'])
        cyera_plan = json.loads(cyera.PLAN.read_bytes())
        self.bodies['cyera:official:1'] = cyera.FixtureStore().get(cyera_plan['retainedIndex']['body'])
        case = self
        class Transport:
            def fetch(self, row, url, previous):
                case.wire.append((row['id'], url))
                if url == row['url']:
                    body = case.bodies[row['id']]
                    return {'requestedUrl': url, 'finalUrl': url, 'status': 'fetched', 'httpStatus': 200,
                            'fetchedAt': case.now, 'contentType': 'text/html; charset=utf-8',
                            'body': case.store.put(body)}
                return {'requestedUrl': url, 'finalUrl': url, 'status': 'blocked', 'httpStatus': 403,
                        'fetchedAt': case.now, 'contentType': 'text/html', 'body': None}
        self.pipeline = Pipeline(self.market, self.store, Transport(), agent=None, clock=lambda: self.now)
        self.pipeline.replay = False
        self.pipeline.force_refresh = True
        self.pipeline.audit_index = index_for(self.store)
        self.pipeline.audit_compatibility = activate_compatibility(self.store, self.plan, self.market, self.pipeline.audit_index)
        self.pipeline.prior_receipts = {}
        self.pipeline.budget_name = 'budget-' + self.now[:10]
        self.net = patch.object(socket.socket, 'connect', side_effect=AssertionError('NO_REAL_TRANSPORT'))
        self.net.start(); self.addCleanup(self.net.stop)

    def tasks(self):
        return [next(row for row in self.plan['tasks'] if row['sourceId'] == sid) for sid in adapter.SOURCE_IDS]

    def test_ordinary_three_source_receipts_keep_fresh_proof_and_all_retained_date_partitions(self):
        from retained_audit import separated_details, verify_receipt
        from contracts import digest
        counts = {'fetches': 452, 'calls': 67, 'documents': 31, 'unchangedMetadata': {'actual': 'preserved'}}
        self.store.compare_and_swap(self.pipeline.budget_name, None, counts)
        for task, n in zip(self.tasks(), (127,47,56)):
            receipt = self.pipeline._task(self.plan, task)
            self.assertTrue(receipt['discoveryComplete'], receipt.get('errorCode'))
            manifest = json.loads(self.store.get(receipt['itemManifest']))
            self.assertTrue(manifest['sourceWindow']['dailyWindowComplete'])
            self.assertEqual(len(manifest['items']), 56 if n == 56 else 25)
            self.assertEqual(set(manifest['itemDates']), set(manifest['items']))
            full = json.loads(self.store.get(receipt['retainedInventoryManifest']))
            self.assertEqual(len(full['items']), n)
            details = separated_details(receipt, self.market, self.pipeline.sources[task['sourceId']], self.now, self.store)
            self.assertEqual(details['processing']['unknownDateDocuments'], 0)
            self.assertEqual(details['processing']['inventoryDocuments'], n)
            self.assertFalse(receipt['validatedFacts'])
        after = self.store.read('heads/' + self.pipeline.budget_name + '.json')
        self.assertEqual(after['fetches'], 461)
        self.assertEqual(after['calls'], 67); self.assertEqual(after['documents'], 31)
        self.assertEqual(after['unchangedMetadata'], counts['unchangedMetadata'])
        self.assertEqual(len(self.wire), 9)

    def test_shared_fetch_denial_stops_further_transport_and_keeps_existing_charges(self):
        maximum = self.market['schedule']['maxFetchesPerRun']
        counts = {'fetches': maximum-1, 'calls': 67, 'documents': 31, 'metadata': 'unchanged'}
        self.store.compare_and_swap(self.pipeline.budget_name, None, counts)
        receipts = [self.pipeline._task(self.plan, task) for task in self.tasks()]
        self.assertEqual(len(self.wire), 1)
        self.assertEqual(self.store.read('heads/' + self.pipeline.budget_name + '.json'), {**counts, 'fetches':maximum})
        self.assertTrue(receipts[0]['discoveryComplete'])
        self.assertTrue(all(not row['discoveryComplete'] for row in receipts[1:]))
        self.assertTrue(all(not row['validatedFacts'] for row in receipts))

if __name__ == '__main__':
    unittest.main()
