"""Dormant Orca diagnostic fixtures. Every transport/run identity is fictional."""
import copy
import json
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
from test_discovery_repairs import page, page_url, card
import orca_qualification as orca

NOW = '2026-10-24T12:00:00Z'
H_ASSET = ROOT / ('contracts/html-qualification-seeds/' + orca.POLICY_SHA256 + '/contracts__' + orca.POLICY_SHA256 + '.json')
ARCHIVE = Path('/var/tmp/smp-bounded-v5-probe-20261024/archive-85b1dc72/jessepike-sec-market-85b1dc728091de55ef7ff584ecdc8502585ff29b/state')


class Clock:
    def __init__(self): self.wall, self.elapsed = NOW, 0
    def now(self): return self.wall
    def monotonic(self): return self.elapsed


class Fetcher:
    def __init__(self, fixture, *, last=2, failure=None, callback=None, root_body=None):
        self.fixture, self.last, self.failure, self.callback, self.root_body = fixture, last, failure, callback, root_body
        self.calls = []
    def fetch(self, source, url):
        self.calls.append((source['id'], url))
        if self.callback: self.callback(self, source, url)
        if self.failure and self.failure in url:
            raise OSError('fictional missing response')
        if url.startswith(orca.INDEX):
            number = 1 if url == orca.INDEX else int(url.rstrip('/').split('/')[-1])
            body = page(number, number + 1 if number < self.last else None, self.last,
                        cards=card('https://orca.security/resources/press-releases/release-' + str(number) + '/'))
            if number == 1 and self.root_body is not None: body = self.root_body
        else:
            body = ('<html><head><link rel="canonical" href="' + url + '"></head><body><article><h1>Orca release</h1>'
                    + '<p>Readable fictional primary release content. ' * 20 + '</p></article></body></html>').encode()
        return {'status': 'fetched', 'httpStatus': 200, 'requestedUrl': url, 'finalUrl': url,
                'fetchedAt': self.fixture.clock.wall, 'contentType': 'text/html', 'body': self.fixture.store.put(body)}


class OrcaQualificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(Path(self.temp.name) / 'state'); self.clock = Clock()
        self.contract = json.loads(H_ASSET.read_bytes())
        self.assertEqual(digest(self.contract), orca.POLICY_SHA256)
        raw = canonical(self.contract); key = 'contracts/' + digest(self.contract) + '.json'
        self.store.write_once(key, raw)
        self.contract_ref = {'key': key, 'sha256': digest(raw), 'bytes': len(raw)}
        self.source = next(s for s in self.contract['sources'] if s['id'] == orca.SOURCE_ID)
        self.adapter = {**copy.deepcopy(self.source), 'kind': 'html_index', 'url': orca.INDEX,
                        'htmlCompleteness': 'orca-news-pagination-v1'}
        body = self.store.put(page(1, 2, 2))
        old = {'sourceId': 'orca:citation:TR-orca-1', 'status': 'fetched', 'httpStatus': 200,
               'requestedUrl': 'https://orca.security/resources/press-releases/', 'finalUrl': orca.INDEX,
               'body': body, 'fetchedAt': '2026-10-23T04:14:41.172921Z'}
        raw = canonical(old); key = 'observations/' + 'a' * 64 + '.json'; self.store.write_once(key, raw)
        fictional = {'observation': {'key': key, 'sha256': digest(raw), 'bytes': len(raw)},
                     'body': body, 'fetchedAt': old['fetchedAt']}
        authority = patch.object(orca, 'START_PROOF', fictional); authority.start(); self.addCleanup(authority.stop)
        self.plan = {'schemaVersion': 2, 'operation': orca.OPERATION, 'marketSha256': orca.POLICY_SHA256,
                     'originalContract': self.contract_ref, 'sourceId': orca.SOURCE_ID,
                     'originalSourceSha256': digest(self.source), 'proposedAdapterSha256': digest(self.adapter),
                     'startProof': copy.deepcopy(fictional), 'maxRequests': 61, 'maxIndexPages': 60, 'primarySamples': 1}
        self.path = Path(self.temp.name) / 'plan.json'; self.path.write_bytes(canonical(self.plan))
    def budget(self):
        return PersistentProbeBudget(self.store, self.contract, clock=self.clock.now, monotonic=self.clock.monotonic)
    def run_report(self, fetcher=None, budget=None):
        self.fetcher = fetcher or Fetcher(self); self.context = budget or self.budget()
        return orca.execute(self.contract, self.store, self.fetcher, self.context,
                            orca.validate_plan(self.contract, self.store, self.path.read_bytes(), self.path))
    def verify(self, report):
        return orca.verify_report(self.contract, self.store, self.path.read_bytes(), report)

    def test_complete_two_page_graph_has_separate_sample_and_zero_credit(self):
        report = self.run_report(); replay = self.verify(report)
        self.assertTrue(replay['indexComplete']); self.assertTrue(replay['evidenceComplete'])
        self.assertEqual(len(self.fetcher.calls), 3)
        self.assertEqual({s for s, _ in self.fetcher.calls}, {orca.SOURCE_ID})
        self.assertEqual(len(report['inventory']['items']), 2)
        self.assertEqual(report['primarySample']['parsed']['dateMetadataState'], 'unknown')
        self.assertEqual(report['facts'], []); self.assertEqual(report['modelCalls'], 0)
        self.assertFalse(report['qualified']); self.assertFalse(report['coverageCredit'])

    def test_strict_plan_policy_and_source_preflight_before_any_transport(self):
        mutations = [lambda p:p.update(maxRequests=61.0), lambda p:p.update(maxIndexPages=True),
                     lambda p:p.update(primarySamples=True), lambda p:p.update(schemaVersion=2.0),
                     lambda p:p.update(sourceId='delinea:official:1'), lambda p:p.update(uncontrolledUrl='https://evil.invalid/'),
                     lambda p:p.update(proposedAdapterSha256='0' * 64), lambda p:p.update(marketSha256='0' * 64),
                     lambda p:p['startProof'].update(fetchedAt=NOW)]
        for mutate in mutations:
            p = copy.deepcopy(self.plan); mutate(p); self.path.write_bytes(canonical(p))
            transport = Fetcher(self)
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                orca.validate_plan(self.contract, self.store, self.path.read_bytes(), self.path)
            self.assertEqual(transport.calls, [])
        changed = copy.deepcopy(self.contract); changed['schedule']['maxFetchesPerRun'] -= 1
        with self.assertRaises(ValueError): orca.validate_plan(changed, self.store, canonical(self.plan))

    def test_start_body_tamper_and_live_plan_replacement_reject_before_transport(self):
        normalized = orca.validate_plan(self.contract, self.store, self.path.read_bytes(), self.path)
        self.path.write_bytes(b'{}'); transport = Fetcher(self)
        with self.assertRaisesRegex(ValueError, 'CURRENT_PLAN_CHANGED'):
            orca.execute(self.contract, self.store, transport, self.budget(), normalized)
        self.assertEqual(transport.calls, [])
        self.path.write_bytes(canonical(self.plan))
        self.store._path(self.plan['startProof']['body']['key']).write_bytes(b'tampered')
        with self.assertRaises(ValueError): orca.validate_plan(self.contract, self.store, self.path.read_bytes())

    def test_missing_second_page_preserves_first_inventory_and_actual_charge(self):
        r = self.run_report(Fetcher(self, failure='/page/2/'))
        self.assertFalse(r['indexComplete']); self.assertFalse(r['evidenceComplete'])
        self.assertEqual(len(r['inventory']['items']), 1)
        self.assertEqual(r['reservationContext']['probeFetchReservations'], 2)
        self.assertTrue(r['executionCompleted']); self.verify(r)

    def test_maximum_60_pages_plus_sample_and_nonterminal_cap(self):
        r = self.run_report(Fetcher(self, last=60))
        self.assertTrue(r['evidenceComplete']); self.assertEqual(len(self.fetcher.calls), 61)
        # A new operation gets a distinct ledger but retains the same fixed plan.
        self.store.compare_and_swap('budget-2026-10-24', self.store.read('heads/budget-2026-10-24.json'), None)
        r = self.run_report(Fetcher(self, last=61))
        self.assertFalse(r['evidenceComplete']); self.assertEqual(len(self.fetcher.calls), 60)
        self.assertEqual(len(r['inventory']['items']), 60); self.assertEqual(r['reason'], 'ORCA_PAGINATION_LIMIT')

    def test_full_budget_no_request_and_prefetch_denial_keeps_charged_reservation(self):
        self.store.compare_and_swap('budget-2026-10-24', None, {'calls': 80, 'documents': 40, 'fetches': 5500})
        r = self.run_report(); self.assertEqual(self.fetcher.calls, [])
        self.assertEqual(r['reservationContext']['currentBudget']['fetches'], 5500)
        self.assertFalse(r['evidenceComplete'])
        self.store.compare_and_swap('budget-2026-10-24', self.store.read('heads/budget-2026-10-24.json'), None)
        budget = self.budget(); reserve = budget.reserve_fetch
        def charged_then_cancel():
            value = reserve(); budget.deadline = 0; return value
        with patch.object(budget, 'reserve_fetch', side_effect=charged_then_cancel): r = self.run_report(budget=budget)
        self.assertEqual(self.fetcher.calls, []); self.assertEqual(budget.reservations, 1)
        self.assertIsNotNone(r['requests'][0]['reservation']); self.assertFalse(r['evidenceComplete'])

    def test_failed_redirect_conditional_empty_or_blocked_primary_cannot_complete(self):
        for mode in ('redirect', '304', 'empty', 'blocked'):
            f = Fetcher(self, last=1); get = f.fetch
            def changed(source, url):
                r = get(source, url)
                if '/press-releases/' in url:
                    if mode == 'redirect': r['finalUrl'] += 'other/'
                    elif mode == '304': r.update(status='not_modified', httpStatus=304)
                    elif mode == 'empty': r['body'] = self.store.put(b'<html></html>')
                    else: r.update(status='blocked', httpStatus=403)
                return r
            f.fetch = changed
            with self.subTest(mode=mode):
                r = self.run_report(f); self.assertTrue(r['indexComplete']); self.assertFalse(r['evidenceComplete']); self.verify(r)

    def test_conflicting_future_dates_and_unsafe_literal_controls_stay_partial(self):
        cases = [page(1, 2, 2, cards=card(day='Oct 25, 2026')),
                 page(1, 2, 2, head_target='https://orca.security/resources/news/x/../page/2/',
                      class_target='https://orca.security/resources/news/x/../page/2/'),
                 page(1, 2, 2, head_target=page_url(3)),
                 page(1, 2, 2, cards='<div>Unknown layout</div>')]
        for body in cases:
            with self.subTest(body=body[:100]):
                r = self.run_report(Fetcher(self, root_body=body)); self.assertFalse(r['evidenceComplete']); self.verify(r)
        f = Fetcher(self); get = f.fetch
        def conflicting(source, url):
            r = get(source, url)
            if url == page_url(2): r['body'] = self.store.put(page(2, cards=card('https://orca.security/resources/press-releases/release-1/', day='Oct 21, 2026')))
            return r
        f.fetch = conflicting; r = self.run_report(f)
        self.assertFalse(r['evidenceComplete']); self.assertIn('CONFLICTING', r['reason'])

    def test_quiet_old_cards_are_complete_evidence_without_semantic_dates(self):
        r = self.run_report(Fetcher(self, last=1, root_body=page(cards=card(day='Jan 01, 2020'))))
        self.assertTrue(r['evidenceComplete']); self.assertEqual(set(r['inventory']['dates'].values()), {'2020-01-01'})
        self.assertEqual(r['documentsProcessed'], 0); self.assertEqual(r['facts'], [])

    def test_future_response_time_retained_as_incomplete_original_observation(self):
        f = Fetcher(self); get = f.fetch
        def future(source, url):
            r = get(source, url); r['fetchedAt'] = '2026-10-24T13:00:00Z'; return r
        f.fetch = future; r = self.run_report(f)
        self.assertFalse(r['evidenceComplete']); self.assertEqual(r['reason'], 'ORCA_OBSERVATION_TIME_INVALID')
        self.assertIsNotNone(r['requests'][0]['observation']); self.verify(r)

    def test_repeated_identical_featured_card_keeps_both_page_provenances(self):
        f = Fetcher(self); get = f.fetch
        shared = card('https://orca.security/resources/press-releases/featured-release/', featured=True)
        def featured(source, url):
            r = get(source, url)
            if url.startswith(orca.INDEX):
                n = 1 if url == orca.INDEX else 2
                r['body'] = self.store.put(page(n, 2 if n == 1 else None, 2,
                    cards=card('https://orca.security/resources/press-releases/release-' + str(n) + '/'), featured=shared))
            return r
        f.fetch = featured; r = self.run_report(f)
        self.assertTrue(r['evidenceComplete']); self.assertEqual(len(r['inventory']['items']), 3)
        self.assertEqual([len(p['parsed']['items']) for p in r['pages']], [2, 2])

    def test_index_redirect_and_raw_url_normalization_cannot_gain_completion(self):
        for body in (page(1, 2, 2, head_target=page_url(2).replace('/news/', '/news//'),
                          class_target=page_url(2).replace('/news/', '/news//')),
                     page(1, 2, 2, head_target=page_url(2).replace('/news/', '/news/\t'),
                          class_target=page_url(2).replace('/news/', '/news/\t'))):
            r = self.run_report(Fetcher(self, root_body=body))
            self.assertFalse(r['evidenceComplete']); self.assertEqual(len(self.fetcher.calls), 1)
        f = Fetcher(self); get = f.fetch
        def redirected(source, url):
            r = get(source, url); r['finalUrl'] = orca.INDEX + 'page/2/'; return r
        f.fetch = redirected; r = self.run_report(f)
        self.assertFalse(r['evidenceComplete']); self.assertEqual(r['reason'], 'ORCA_RESPONSE_INCOMPLETE')

    def test_cancellation_and_last_response_deadline_or_day_cannot_claim_readiness(self):
        for mode in ('cancel', 'deadline', 'day'):
            budget = self.budget()
            def advance(fetcher, source, url):
                if mode == 'cancel' and len(fetcher.calls) == 1: budget.deadline = 0
                elif '/press-releases/' in url:
                    if mode == 'deadline': self.clock.elapsed = 1201
                    elif mode == 'day': self.clock.wall = '2026-10-25T00:00:00Z'
            with self.subTest(mode=mode):
                r = self.run_report(Fetcher(self, callback=advance), budget)
                self.assertFalse(r['evidenceComplete']); self.assertFalse(r['executionCompleted']); self.verify(r)
            self.clock.wall, self.clock.elapsed = NOW, 0

    def test_final_timestamp_capture_is_between_two_guards(self):
        for rollover in (False, True):
            budget = self.budget(); f = Fetcher(self, last=1); get = f.fetch
            def last(source, url):
                r = get(source, url)
                if '/press-releases/' in url:
                    calls = [0]
                    def clock():
                        calls[0] += 1
                        if calls[0] >= 3:  # response stamp, guard, final capture
                            if rollover: self.clock.wall = '2026-10-25T00:00:00Z'
                            else: self.clock.elapsed = 1201
                        return self.clock.wall
                    budget.clock = clock
                return r
            f.fetch = last
            with self.subTest(rollover=rollover):
                r = self.run_report(f, budget)
                self.assertFalse(r['evidenceComplete']); self.assertFalse(r['executionCompleted']); self.verify(r)
            self.clock.wall, self.clock.elapsed = NOW, 0

    def test_rehashed_completion_inventory_source_charge_and_text_forgeries_reject(self):
        r = self.run_report()
        for mutate in (lambda x:x.update(modelCalls=False), lambda x:x.update(qualified=True),
                       lambda x:x['inventory']['items'].pop(), lambda x:x['pages'].pop(),
                       lambda x:x['pages'].append(copy.deepcopy(x['pages'][-1])),
                       lambda x:x['requests'][0]['reservation'].update(chargedFetchCount=5501),
                       lambda x:x['primarySample']['parsed'].update(heading='Forged heading'),
                       lambda x:x['requests'].pop(), lambda x:x['reservationContext'].update(fetchLimit=5501)):
            bad = copy.deepcopy(r); mutate(bad)
            with self.subTest(mutate=mutate), self.assertRaises(ValueError): self.verify(bad)
        bad = copy.deepcopy(r); wrapper = json.loads(self.store.get(bad['requests'][0]['observation']))
        wrapper['sourceId'] = 'orca:citation:TR-orca-1'; bad['requests'][0]['observation'] = self.store.put(wrapper)
        with self.assertRaises(ValueError): self.verify(bad)

    def test_partial_flags_cannot_be_rehashed_into_readiness(self):
        r = self.run_report(Fetcher(self, failure='/page/2/'))
        r.update(indexComplete=True, evidenceComplete=True, reason='COMPLETE_DIAGNOSTIC_EVIDENCE_ONLY')
        with self.assertRaisesRegex(ValueError, 'REPLAYED_RESULT'): self.verify(r)

    def test_immutable_historical_plan_replay_has_no_transport_or_writes(self):
        r = self.run_report(); raw = canonical({'schemaVersion': 1, 'checkpointProfile': 'source_probe',
            'contractSha256': orca.POLICY_SHA256, 'githubRunId': '987654', 'githubRunAttempt': 1,
            'githubEventName': 'workflow_dispatch', 'githubRef': 'refs/heads/main', 'appRevision': 'f' * 40,
            'apiFallback': False, 'modelCalls': 0, 'sourceChecksCredited': 0, 'qualifiedSources': 0,
            'semanticAdmission': False, 'coverageCredit': False,
            'publication': {'published': False, 'reason': 'SOURCE_PROBE_DIAGNOSTIC_ONLY'},
            'executionCompleted': True, 'outcome': 'completed_diagnostic', 'diagnostic': r})
        key = 'ci/source-probe-runs/987654-1.json'; self.store.write_once(key, raw)
        ref = {'key': key, 'sha256': digest(raw), 'bytes': len(raw)}; self.path.write_bytes(b'{}')
        with patch('socket.socket.connect', side_effect=AssertionError('network')), \
             patch.object(self.store, 'put', side_effect=AssertionError('write')), \
             patch.object(self.store, 'write_once', side_effect=AssertionError('write')):
            replay = orca.replay_diagnostic(self.contract, self.store, ref, r['planReference'])
        self.assertTrue(replay['readiness']['evidenceComplete']); self.assertFalse(replay['readiness']['qualified'])


class ActualOrcaBodyTests(unittest.TestCase):
    @unittest.skipUnless(ARCHIVE.is_dir(), 'authenticated archive is a local-only test input')
    def test_exact_original_endpoint_authority_and_root_to_missing_page_two(self):
        policy = json.loads(H_ASSET.read_bytes()); proof = copy.deepcopy(orca.START_PROOF)
        selected = [ARCHIVE / proof[k]['key'] for k in ('observation', 'body')]
        before = [(digest(p.read_bytes()), len(p.read_bytes()), p.stat().st_mtime_ns) for p in selected]
        with tempfile.TemporaryDirectory() as directory:
            store = LocalStore(Path(directory) / 'state')
            for key in ('observation', 'body'):
                ref = proof[key]; raw = (ARCHIVE / ref['key']).read_bytes()
                self.assertEqual((digest(raw), len(raw)), (ref['sha256'], ref['bytes']))
                store.write_once(ref['key'], raw)
            raw = canonical(policy); key = 'contracts/' + orca.POLICY_SHA256 + '.json'; store.write_once(key, raw)
            source = next(s for s in policy['sources'] if s['id'] == orca.SOURCE_ID)
            adapter = {**source, 'kind': 'html_index', 'url': orca.INDEX, 'htmlCompleteness': 'orca-news-pagination-v1'}
            plan = {'schemaVersion': 2, 'operation': orca.OPERATION, 'marketSha256': orca.POLICY_SHA256,
                    'originalContract': {'key': key, 'sha256': digest(raw), 'bytes': len(raw)},
                    'sourceId': orca.SOURCE_ID, 'originalSourceSha256': digest(source), 'proposedAdapterSha256': digest(adapter),
                    'startProof': proof, 'maxRequests': 61, 'maxIndexPages': 60, 'primarySamples': 1}
            path = Path(directory) / 'plan.json'; path.write_bytes(canonical(plan))
            normalized = orca.validate_plan(policy, store, path.read_bytes(), path)
            f = type('FictionalClockFixture', (), {'store': store, 'clock': Clock()})()
            transport = Fetcher(f, root_body=store.get(proof['body']), failure='/page/2/')
            budget = PersistentProbeBudget(store, policy, clock=f.clock.now, monotonic=f.clock.monotonic)
            with patch('socket.socket.connect', side_effect=AssertionError('network')):
                report = orca.execute(policy, store, transport, budget, normalized)
            self.assertEqual(len(report['inventory']['items']), 2)
            self.assertEqual(report['pages'][0]['parsed']['highestPage'], 41)
            self.assertEqual([u for _, u in transport.calls], [orca.INDEX, page_url(2)])
            self.assertFalse(report['evidenceComplete']); self.assertFalse(report['indexComplete'])
        self.assertEqual(before, [(digest(p.read_bytes()), len(p.read_bytes()), p.stat().st_mtime_ns) for p in selected])


if __name__ == '__main__': unittest.main()
