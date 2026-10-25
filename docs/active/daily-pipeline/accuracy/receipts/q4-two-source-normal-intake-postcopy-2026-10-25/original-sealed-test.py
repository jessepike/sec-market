"""Exact-J offline integration. Actual proof is read-only; transport is synthetic."""
import copy
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'web/scripts/pipeline'), str(ROOT / 'ops/ci')]
from contracts import canonical, digest, plan_run, validate_contract
from discovery import discover
from fetcher import Fetcher
from storage import LocalStore
from onboarding import validate_qualification_probe_plan
import q4_qualification_origin as q4
import q4_qualification_seed as seed
import q4_baseline_migration as baseline
import source_qualification_origin as origins
from q4_intake_fixtures import ReadOnlyArchive, Overlay

NOW = '2026-10-25T12:30:00Z'
LATER = '2026-10-25T13:30:00Z'


class ActualProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = ReadOnlyArchive()
        cls.contract = json.loads((ROOT / 'contracts/market.json').read_bytes())
        with patch.object(socket, 'socket', side_effect=AssertionError('network prohibited')), \
             patch.object(LocalStore, '__init__', side_effect=AssertionError('frozen initialization prohibited')):
            cls.checked = seed.validate_seed(ROOT, cls.store, cls.contract, NOW)
        cls.overlay = Overlay(cls.store, cls.checked['files'])
        cls.original = q4.inverse_policy(cls.contract, cls.overlay)
        cls.transition = json.loads(cls.overlay.get(q4.AUTHORITY['transition']))

    @classmethod
    def tearDownClass(cls):
        cls.store.assert_unchanged()

    def test_actual_complete_graph_and_all_five_inventory_only_origins(self):
        self.assertEqual(digest(validate_contract(self.contract)), q4.AUTHORITY['activatedContractSha256'])
        self.assertEqual(len(plan_run(self.original, NOW)['tasks']), 557)
        self.assertEqual(len(plan_run(self.contract, NOW)['tasks']), 557)
        self.assertEqual(self.checked['preservation']['reviewQueueEntries'], 38)
        self.assertEqual(len(self.checked['files']), 55)
        self.assertFalse(any(k.startswith(('heads/', 'observations/', 'runs/')) for k in self.checked['files']))
        self.assertEqual([self.checked['qualificationInventory'][s]['documents'] for s in q4.SOURCE_IDS], [206, 323])
        for sid in ('ping-identity:official:1', 'delinea:official:1', 'sonatype:official:1'):
            old = origins.qualification_predecessors(self.original, sid, self.overlay, NOW)
            new = origins.qualification_predecessors(self.contract, sid, self.overlay, NOW)
            self.assertEqual(old, new)
            a = origins.resolve_inventory_origin(old[0], self.original, sid, self.overlay, NOW)
            b = origins.resolve_inventory_origin(new[0], self.contract, sid, self.overlay, NOW)
            self.assertEqual(a, b)
            self.assertEqual(b['authority'], 'inventory_only')

    def test_entire_forward_inverse_and_every_unlisted_policy_mutation_rejects(self):
        self.assertEqual(q4.validate_rows(self.original, self.contract, self.transition), self.original)
        candidates = []
        changed = copy.deepcopy(self.contract); changed['sources'].reverse(); candidates.append(changed)
        changed = copy.deepcopy(self.contract); changed['sources'][0]['extra'] = 1; candidates.append(changed)
        changed = copy.deepcopy(self.contract); changed['model']['maxCallsPerRun'] += 1; candidates.append(changed)
        for sid in q4.SOURCE_IDS:
            for key in ('kind', 'url', 'registration', 'qualificationOrigin'):
                changed = copy.deepcopy(self.contract)
                next(s for s in changed['sources'] if s['id'] == sid)[key] = 'substitution'
                candidates.append(changed)
        for changed in candidates:
            with self.subTest(hash=digest(changed)), self.assertRaises(ValueError):
                q4.validate_rows(self.original, changed, self.transition)
        for key in self.transition:
            changed = copy.deepcopy(self.transition); changed.pop(key)
            with self.subTest(key=key), self.assertRaises((ValueError, KeyError)):
                q4.validate_rows(self.original, self.contract, changed)

    def test_q4_predecessors_keep_all_items_and_reject_wrong_kind_source_time_or_reference(self):
        for sid, count in zip(q4.SOURCE_IDS, (206, 323)):
            prior = origins.qualification_predecessors(self.contract, sid, self.overlay, NOW)[0]
            value = origins.resolve_inventory_origin(prior, self.contract, sid, self.overlay, NOW)
            self.assertEqual(len(value['items']), count)
            self.assertEqual(value['authority'], 'inventory_only')
            for key in prior:
                changed = copy.deepcopy(prior); changed[key] = 'substitution'
                with self.subTest(sid=sid, key=key), self.assertRaises((ValueError, KeyError, TypeError)):
                    q4.resolve(changed, self.contract, sid, self.overlay, NOW)
            with self.assertRaises(ValueError): q4.resolve(prior, self.contract, sid, self.overlay, '2026-10-24T00:00:00Z')
            with self.assertRaises(ValueError): q4.resolve(prior, self.original, sid, self.overlay, NOW)

    def test_six_correction_admissions_and_group_policies_replay_without_any_work(self):
        from corrections import load_policy, process_corrections, group_review_policy
        requests = json.loads((ROOT / 'contracts/factual-corrections.json').read_bytes())
        new = load_policy(ROOT, self.contract)
        old_hash = digest({'marketSha256': digest(self.original), 'requestsSha256': digest(requests),
                           'baselineSha256': requests['baseline']['sha256']})
        self.assertNotEqual(old_hash, new['policySha256'])
        self.assertEqual({g['id']: group_review_policy(g, self.original, requests['baseline']['sha256'])
                          for g in requests['groups']}, new['reviewPolicySha256ByGroup'])
        class NoModel:
            def __getattr__(self, name): raise AssertionError('model prohibited')
        def deny(*_a, **_kw): raise AssertionError('reservation prohibited')
        with patch.object(socket, 'socket', side_effect=AssertionError('network prohibited')):
            result = process_corrections(ROOT, self.overlay, self.contract, NoModel(), deny, NOW)
        self.assertEqual(len(result['admitted']), 6)
        self.assertEqual(result['pending'], [])
        self.assertEqual(result['attempts'], [])

    def test_seed_rejects_wrong_policy_or_corrupt_immutable_before_any_write(self):
        with self.assertRaises(ValueError): seed.validate_seed(ROOT, self.store, self.original, NOW)
        first = seed._payload(ROOT, seed.PACKAGE)
        manifest = json.loads(first)
        entry = manifest['files'][0]
        corrupt = Overlay(self.store, {entry['key']: b'corrupt'})
        with self.assertRaises((ValueError, AssertionError)):
            seed.validate_seed(ROOT, corrupt, self.contract, NOW)
        for path in ('heads/latest-run.json', '../seed.json', 'contracts/q4-qualification-seeds/x/../seed.json'):
            with self.assertRaises(ValueError): seed._payload(ROOT, {'path': path, 'bytes': 1, 'sha256': 'a' * 64})
        self.assertTrue(all(key.startswith('objects/') or canonical(json.loads(body)) == body
                            for key, body in self.checked['files'].items()))

    def test_H_operational_probe_plan_rejects_under_J_and_disabled_J_is_exact(self):
        class NoRead:
            def get(self, *_): raise AssertionError('must reject policy before reads')
            def read(self, *_): raise AssertionError('must reject policy before reads')
        with self.assertRaises(ValueError):
            validate_qualification_probe_plan(self.contract, NoRead(), ROOT / 'contracts/source-qualification-probes.json')
        checked = validate_qualification_probe_plan(self.contract, NoRead(), ROOT /
            'docs/active/daily-pipeline/accuracy/q4-normal-intake-disabled-J-plan-2026-10-25.json')
        self.assertEqual(checked['maxRequests'], 0)
        self.assertEqual(checked['plan']['sources'], [])

    def test_python_zero_credit_baseline_exact_and_mutations_reject(self):
        value = json.loads((ROOT / 'web/src/data/generated/dailyMarket.json').read_bytes())
        baseline.verify(ROOT, self.contract, self.overlay, value)
        self.assertEqual(value['coverage']['successfulTasks'], 0)
        self.assertIsNone(value['coverage']['validUntil'])
        self.assertEqual(value['runId'], value['supersededPolicy']['snapshot']['runId'])
        for mutate in (lambda v: v.update(checkedAt=NOW), lambda v: v['coverage'].update(successfulTasks=2),
                       lambda v: v['supersededPolicy']['snapshot'].update(checkedAt=NOW),
                       lambda v: v['coverage']['sources'].reverse()):
            changed = copy.deepcopy(value); mutate(changed)
            with self.assertRaises(ValueError): baseline.verify(ROOT, self.contract, self.overlay, changed)

    def test_seed_uses_actual_J_context_immutable_import_and_acknowledgement(self):
        import collect
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); state = LocalStore(root / 'state')
            session = {'sessionId': 'github-123-1', 'role': 'collector', 'appRevision': 'a' * 40,
                       'executionMode': 'github_subscription', 'startedAt': NOW,
                       'restored': {'commit': 'b' * 40}}
            LocalStore(root).write_once('session.json', session)
            state.compare_and_swap('cloud-lease', None, {'sessionId': session['sessionId'],
                'expiresAt': '2026-10-25T14:00:00Z'})
            event = root / 'event.json'
            event.write_bytes(canonical({'repository': {'full_name': 'jessepike/sec-market', 'private': True},
                                         'inputs': {'source_probe': 'false'}}))
            env = {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'jessepike/sec-market',
                   'GITHUB_REF': 'refs/heads/main', 'GITHUB_EVENT_NAME': 'workflow_dispatch',
                   'GITHUB_SHA': session['appRevision'], 'GITHUB_RUN_ID': '123', 'GITHUB_RUN_ATTEMPT': '1',
                   'GITHUB_EVENT_PATH': str(event)}
            calls = []
            def checkpoint(root, store, current, phase, result):
                # Synthetic remote acknowledgement; real seed/context/lease checks execute.
                calls.append(result)
                archive = {'commit': 'c' * 40, 'manifestSha256': 'd' * 64}
                local = LocalStore(root); previous = local.read('heads/remote-archive.json')
                local.compare_and_swap('remote-archive', previous, archive)
                return {'archive': archive, 'receipt': {'phase': phase, 'sessionId': current['sessionId'],
                    'appRevision': current['appRevision'], 'role': 'collector',
                    'contractSha256': digest(self.contract), 'result': result}}
            runtime = SimpleNamespace(REPO=ROOT, utcnow=lambda: NOW,
                require_lease=collect.session_runtime.require_lease, checkpoint=checkpoint)
            before = copy.deepcopy(state.read('heads/cloud-lease.json'))
            with patch.dict(os.environ, env, clear=True), \
                 patch.object(seed, 'validate_seed', return_value=self.checked):
                one = seed.seed_before_collection(ROOT, root, state, session, self.contract, runtime)
                two = seed.seed_before_collection(ROOT, root, state, session, self.contract, runtime)
                self.assertEqual(one, two)
                self.assertEqual(state.read('heads/cloud-lease.json'), before)
                self.assertEqual(len(calls), 2)
                self.assertEqual(one['contractSha256'], digest(self.contract))
                self.assertFalse(one['coverageCredit']); self.assertFalse(one['semanticAdmission'])
                for key, raw in self.checked['files'].items(): self.assertEqual((state.root / key).read_bytes(), raw)
                for key in ('heads/latest-run.json', 'heads/dailySnapshot.json', 'heads/production.json'):
                    self.assertIsNone(state.read(key))
                runtime.checkpoint = lambda *_: {}
                with self.assertRaises(ValueError):
                    seed.seed_before_collection(ROOT, root, state, session, self.contract, runtime)
                runtime.checkpoint = checkpoint
                lease = state.read('heads/cloud-lease.json')
                state.compare_and_swap('cloud-lease', lease, {**lease, 'releasedAt': NOW})
                with patch.object(state, 'write_once', side_effect=AssertionError('denied before import')):
                    with self.assertRaises(ValueError):
                        seed.seed_before_collection(ROOT, root, state, session, self.contract, runtime)

    def test_zero_calls_real_subscription_guard_preserves_inventory_and_six_fetch_bound(self):
        from agents import SubscriptionAgent
        from bootstrap import GuardedRunner
        from engine import Pipeline
        from retained_audit import index_for, activate_compatibility
        from replay_retained_audit import MemoryStore
        from q4_intake_fixtures import ARCHIVE
        state = MemoryStore(ARCHIVE / 'state')  # Constructor is memory-only, never LocalStore initialization.
        state.memory.update(self.checked['files'])
        state.memory['heads/budget-2026-10-25.json'] = canonical({'fetches': 985, 'calls': 80, 'documents': 38})
        wire, login = [], []
        indexes = dict(zip(q4.SOURCE_IDS, ('f7d84b288a6665280f4b8ade996b0bf64fe9c3fa0ea7a8a15b1adfb0826ccc19',
                                         'cf3c57d1c2080d65656e9f291eca371aefd99909476d413bb5c90155bc742db8')))
        class OfflineFetcher:
            def fetch(inner, source, url, previous=None):
                wire.append((source['id'], url))
                raw = self.store.raw('objects/' + indexes[source['id']]) if url == source['url'] else (
                    '<html><body><article><h1>Synthetic financial release</h1><p>' +
                    ('This fictional issuer release is only a budget mechanics fixture. ' * 20) +
                    '</p></article></body></html>').encode()
                return {'requestedUrl': url, 'finalUrl': url, 'status': 'fetched', 'httpStatus': 200,
                        'fetchedAt': NOW, 'body': state.put(raw),
                        'contentType': 'application/json' if url == source['url'] else 'text/html'}
        def runner(args, **kwargs):
            self.assertEqual(args[1:], ['login', 'status'], 'no model exec is allowed')
            login.append(args)
            return subprocess.CompletedProcess(args, 0, 'Logged in using ChatGPT', '')
        auth = SimpleNamespace(checkpoint=lambda: self.fail('no model invocation means no auth refresh'))
        agent = SubscriptionAgent(self.contract['model'], runner=GuardedRunner(auth, runner=runner))
        pipeline = Pipeline(self.contract, state, OfflineFetcher(), agent=agent, clock=lambda: NOW)
        plan = plan_run(self.contract, NOW)
        state.write_once('runs/' + plan['runId'] + '/plan.json', plan)
        pipeline.audit_index = index_for(state)
        pipeline.audit_compatibility = activate_compatibility(state, plan, self.contract, pipeline.audit_index)
        pipeline.prior_receipts = {}; pipeline.force_refresh = True; pipeline.replay = False
        pipeline.budget_name = 'budget-2026-10-25'; agent.reserve = pipeline._reserve
        receipts = []
        with patch.object(socket, 'socket', side_effect=AssertionError('no real transport')):
            for task in plan['tasks']:
                if task['sourceId'] in q4.SOURCE_IDS: receipts.append(pipeline._task(plan, task))
        self.assertEqual(len(receipts), 2)
        for receipt, count in zip(receipts, (206, 323)):
            self.assertTrue(receipt['discoveryComplete'], receipt)
            self.assertEqual(len(json.loads(state.get(receipt['retainedInventoryManifest']))['items']), count)
            self.assertGreater(receipt.get('pendingDocuments', 0), 0)
            self.assertEqual(receipt['validatedFacts'], [])
            self.assertEqual(receipt['newFactIds'], [])
        self.assertTrue(2 <= len(wire) <= 6)
        self.assertEqual(sum(url == next(s['url'] for s in self.contract['sources'] if s['id'] == sid)
                             for sid, url in wire), 2)
        self.assertEqual(agent.calls, 0)
        counts = state.read('heads/budget-2026-10-25.json')
        self.assertEqual(counts['calls'], 80)
        self.assertTrue(38 <= counts['documents'] <= 40)
        self.assertEqual(counts['fetches'], 985 + len(wire))
        self.assertGreaterEqual(len(login), 1)


class OrdinaryDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / 'contracts/market.json').read_bytes())
        cls.archive = ReadOnlyArchive()
        cls.raw = {}
        for sid, sha in zip(q4.SOURCE_IDS, ('f7d84b288a6665280f4b8ade996b0bf64fe9c3fa0ea7a8a15b1adfb0826ccc19',
                                            'cf3c57d1c2080d65656e9f291eca371aefd99909476d413bb5c90155bc742db8')):
            cls.raw[sid] = cls.archive.raw('objects/' + sha)
    @classmethod
    def tearDownClass(cls): cls.archive.assert_unchanged()

    def source(self, sid): return next(s for s in self.contract['sources'] if s['id'] == sid)
    def observation(self, source, body, **changes):
        return {'sourceId': source['id'], 'observationId': '1' * 64, 'requestedUrl': source['url'],
                'finalUrl': source['url'], 'status': 'fetched', 'httpStatus': 200, 'fetchedAt': NOW,
                'contentType': 'application/json; charset=utf-8',
                'body': {'key': 'objects/' + digest(body), 'sha256': digest(body), 'bytes': len(body)}, **changes}

    def test_each_actual_array_uses_one_callback_and_preserves_every_unzoned_row(self):
        for sid, count in zip(q4.SOURCE_IDS, (206, 323)):
            source, body = self.source(sid), self.raw[sid]
            calls = []
            def request(url): calls.append(url); return self.observation(source, body), body
            value = discover(source, request)
            self.assertTrue(value['complete'], value)
            self.assertEqual(calls, [source['url']])
            self.assertEqual(len(value['items']), count)
            self.assertIsNone(value['timezone'])
            self.assertEqual(len(value['originalDateStrings']), count)
            self.assertTrue(all('T' not in day for day in value['itemDates'].values()))

    def test_transport_body_source_final_mime_or_status_failures_never_get_credit(self):
        source = self.source(q4.SOURCE_IDS[0]); body = self.raw[source['id']]
        substitutions = {'sourceId': 'rapid7:official:1', 'requestedUrl': source['url'] + '&x=1',
                         'finalUrl': 'https://elsewhere.invalid/', 'httpStatus': 201,
                         'status': 'blocked', 'contentType': 'text/html', 'fetchedAt': None,
                         'body': None}
        for field, value in substitutions.items():
            observed = self.observation(source, body); observed[field] = value
            result = discover(source, lambda _: (observed, body))
            with self.subTest(field=field):
                self.assertFalse(result['complete'])
                self.assertEqual(result['items'], [])
                self.assertEqual(result['observations'], [observed])
        for raw in (b'', b'{}', b'{"GetPressReleaseListResult":[]}', b'{"GetPressReleaseListResult":NaN}', b'{'):
            result = discover(source, lambda _: (self.observation(source, raw), raw))
            self.assertFalse(result['complete'])

    def test_source_row_cannot_widen_hosts_url_or_registration(self):
        for key, value in (('url', self.source(q4.SOURCE_IDS[0])['url'] + '&page=1'),
                           ('allowedHosts', ['foreign.invalid']), ('id', 'new:official:1')):
            source = copy.deepcopy(self.source(q4.SOURCE_IDS[0])); source[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                discover(source, lambda _: self.fail('request before source validation'))

    def test_genuine_fetcher_200_then_304_preserves_reuse_and_new_check_clock(self):
        from urllib.error import HTTPError
        from io import BytesIO
        with tempfile.TemporaryDirectory() as directory:
            store = LocalStore(Path(directory))
            source = self.source(q4.SOURCE_IDS[0]); raw = self.raw[source['id']]
            class Response(BytesIO):
                status = 200
                headers = {'Content-Type': 'application/json', 'ETag': '"fixture"'}
                url = source['url']
            requests = []
            def first(req, timeout): requests.append(req); return Response(raw)
            fetcher = Fetcher(store)
            with patch('fetcher.safe_url', side_effect=lambda url, *_a, **_k: url), \
                 patch('fetcher.urllib.request.build_opener', return_value=SimpleNamespace(open=first)), \
                 patch('fetcher.utcnow', return_value=NOW):
                old = fetcher.fetch(source, source['url'])
            old.update(sourceId=source['id'], observationId='a' * 64)
            def second(req, timeout):
                requests.append(req)
                raise HTTPError(source['url'], 304, 'Not modified', {'Content-Type': 'application/json'}, None)
            with patch('fetcher.safe_url', side_effect=lambda url, *_a, **_k: url), \
                 patch('fetcher.urllib.request.build_opener', return_value=SimpleNamespace(open=second)), \
                 patch('fetcher.utcnow', return_value=LATER):
                fresh = Fetcher(store).fetch(source, source['url'], old)
            fresh.update(sourceId=source['id'], observationId='b' * 64)
            result = discover(source, lambda _: (fresh, store.get(fresh['body'])))
            self.assertTrue(result['complete'], result)
            self.assertEqual(fresh['reusesObservationId'], old['observationId'])
            self.assertEqual(fresh['body'], old['body'])
            self.assertEqual(fresh['fetchedAt'], LATER)
            self.assertEqual(requests[1].get_header('If-none-match'), '"fixture"')

    def test_quiet_future_boundary_and_more_rows_use_original_index_clock(self):
        source = self.source(q4.SOURCE_IDS[0]); rows = json.loads(self.raw[source['id']])['GetPressReleaseListResult']
        old = copy.deepcopy(rows[-1]); old.update(PressReleaseDate='01/01/2000 00:00:00',
            LinkToDetailPage='/news/news-details/2000/Old/default.aspx')
        raw = canonical({'GetPressReleaseListResult': [old]})
        result = discover(source, lambda _: (self.observation(source, raw), raw))
        self.assertTrue(result['complete']); self.assertTrue(result['currentWindowQuiet'])
        for date, boundary, anomaly in (('10/26/2026 00:00:00', True, False),
                                       ('10/27/2026 00:00:00', False, True)):
            row = copy.deepcopy(rows[0]); row['PressReleaseDate'] = date
            raw = canonical({'GetPressReleaseListResult': [row, old]})
            value = discover(source, lambda _: (self.observation(source, raw), raw))
            self.assertTrue(value['complete']); self.assertFalse(value['currentWindowQuiet'])
            self.assertEqual(bool(value['boundaryAmbiguousItems']), boundary)
            self.assertEqual(bool(value['sourceDateAnomalies']), anomaly)
            self.assertEqual(len(value['undeterminedWindowItems']), 1)
