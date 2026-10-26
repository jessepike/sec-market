"""Portable single-fetch mechanics and exact retained Cyera proof; no real transport."""
import copy
from html import escape
import io
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from test_cyera_press_list import ROOT, PLAN, AS_OF, FixtureStore
from contracts import canonical, digest
from storage import LocalStore
from onboarding import PersistentProbeBudget
from fetcher import Fetcher
import cyera_primary_capture as operation

NOW = '2026-10-25T15:00:00Z'
NEXT_DAY = '2026-10-26T00:00:00Z'
ARCHIVE = Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted')


class Clock:
    wall, elapsed = NOW, 0
    def now(self): return self.wall
    def monotonic(self): return self.elapsed


class Overlay:
    def __init__(self, local, base): self.local, self.base = local, base
    def __getattr__(self, name): return getattr(self.local, name)
    def read(self, key):
        return self.local.read(key) if (self.local.root / key).exists() else self.base.read(key) if key in self.base.rows else None
    def get(self, ref):
        return self.local.get(ref) if (self.local.root / ref['key']).exists() else self.base.get(ref)


def html(fixture, metadata=''):
    sample = fixture.plan['sample']
    return ('<html><head><link rel="canonical" href="' + sample['url'] + '">' + metadata +
            '</head><body><main><article><h1>' + escape(sample['title']) + '</h1><p>' +
            'Fictional source text retained only for portable transport and primary-shape tests. '*6 +
            '</p></article></main></body></html>').encode()


class ResponseFetcher:
    def __init__(self, fixture, body=None, changes=None, error=None, callback=None):
        self.fixture, self.body, self.changes, self.error, self.callback = fixture, body, changes or {}, error, callback
        self.calls = []
    def fetch(self, source, url, previous=None, attempt=0):
        self.calls.append((source['id'], url, previous, attempt))
        assert previous is None and attempt == 2
        if self.callback: self.callback()
        if self.error: raise self.error
        result = {'requestedUrl': url, 'finalUrl': url, 'status': 'fetched', 'httpStatus': 200,
                  'fetchedAt': self.fixture.clock.now(), 'contentType': 'text/html; charset=utf-8',
                  'body': self.fixture.store.put(self.body if self.body is not None else html(self.fixture))}
        result.update(self.changes)
        return result


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.clock = Clock(); self.base = FixtureStore()
        self.local = LocalStore(self.root / 'state'); self.store = Overlay(self.local, self.base)
        self.contract = json.loads((ROOT / 'contracts/market.json').read_bytes())
        self.raw = PLAN.read_bytes(); self.plan = json.loads(self.raw)
        self.path = self.root / 'plan.json'; self.path.write_bytes(self.raw)
        self.net = patch.object(socket.socket, 'connect', side_effect=AssertionError('NO_NETWORK'))
        self.net.start(); self.addCleanup(self.net.stop)
        self.normal = {'heads/latest-run.json': {'old': 'normal'}, 'heads/production.json': {'old': 'production'}}
        for key, value in self.normal.items(): self.local.write_once(key, value)
    def budget(self):
        return PersistentProbeBudget(self.store, self.contract, clock=self.clock.now, monotonic=self.clock.monotonic)
    def capture(self, fetcher=None, budget=None):
        self.fetcher = fetcher or ResponseFetcher(self); self.context = budget or self.budget()
        normalized = operation.validate_plan(self.contract, self.store, self.raw, self.path)
        report = operation.execute(self.contract, self.store, self.fetcher, self.context, normalized)
        return operation.finalize_report(self.contract, self.store, self.raw, report, self.context)
    def replay(self, report): return operation.verify_report(self.contract, self.store, self.raw, report)
    def test_one_logical_get_no_generic_candidates_or_other_credits(self):
        import onboarding
        self.assertEqual(len([s for s in self.contract['sources'] if s['registration'] == 'candidate']), 23)
        with patch.object(onboarding, 'probe_sources', side_effect=AssertionError('NO_GENERIC_PROBES')):
            report = self.capture()
        self.assertTrue(self.replay(report)['proposalEvidenceComplete']); self.assertEqual(report['acceptedSamples'], 1)
        self.assertEqual(self.fetcher.calls, [('cyera:official:1', self.plan['sample']['url'], None, 2)])
        self.assertEqual(report['reservationContext']['currentBudget'], {'calls': 0, 'documents': 0, 'fetches': 1})
        self.assertEqual(report['streams'][0]['asOf'], AS_OF); self.assertEqual(report['facts'], [])
        for key in operation.ZERO_FIELDS: self.assertEqual(report[key], 0)
        for key, value in self.normal.items(): self.assertEqual(self.local.read(key), value)
    def test_full_consumed_actual_graph_is_portable_and_read_only(self):
        with patch.object(LocalStore, '__init__', side_effect=AssertionError('NO_FROZEN_STORE')):
            result = operation.validate_plan(self.contract, self.base, self.raw)
        self.assertEqual(len(result['streams'][0]['records']), 56); self.assertEqual(len(self.base.touched), 17)
    def test_plan_policy_and_csv_substitutions_reject_before_writes_or_reservations(self):
        mutations = []
        for key in self.plan:
            p = copy.deepcopy(self.plan); del p[key]; mutations.append(canonical(p))
        def leafpaths(value, path=()):
            if isinstance(value, dict):
                for k,v in value.items(): yield from leafpaths(v,path+(k,))
            elif isinstance(value,list):
                for k,v in enumerate(value): yield from leafpaths(v,path+(k,))
            else: yield path
        for path in leafpaths(self.plan):
            p=copy.deepcopy(self.plan); node=p
            for key in path[:-1]: node=node[key]
            node[path[-1]]=None if node[path[-1]] is not None else True; mutations.append(canonical(p))
        mutations += [b'{"schemaVersion":2,"schemaVersion":2}', b'{"x":NaN}', b'[]']
        before = sorted(str(p) for p in self.local.root.rglob('*'))
        for raw in mutations:
            with self.subTest(raw=raw[:30]), self.assertRaises((ValueError, KeyError, TypeError)):
                operation.validate_plan(self.contract, self.store, raw)
        changed = copy.deepcopy(self.contract); changed['sources'][0]['extra'] = True
        with self.assertRaises(ValueError): operation.validate_plan(changed, self.store, self.raw)
        original = Path.read_bytes
        def corrupt(path):
            raw=original(path)
            return raw+b' ' if str(path).endswith(operation.CSV_PATH) else raw
        with patch.object(Path, 'read_bytes', corrupt), self.assertRaises(ValueError):
            operation.validate_plan(self.contract, self.store, self.raw)
        self.assertEqual(sorted(str(p) for p in self.local.root.rglob('*')), before)
    def test_every_consumed_original_input_is_authenticated(self):
        for key in self.base.rows:
            base = self.base
            class Changed:
                def get(_, ref): return base.get(ref) + b' ' if ref['key'] == key else base.get(ref)
                def read(_, name):
                    value=base.read(name)
                    return {'tampered':True} if name == key else value
            with self.subTest(key=key), self.assertRaises((ValueError, KeyError, TypeError)):
                operation.validate_plan(self.contract, Changed(), self.raw)
    def test_changed_live_plan_or_failed_preflight_cannot_write_or_charge(self):
        normalized = operation.validate_plan(self.contract, self.store, self.raw, self.path)
        budget = self.budget(); self.path.write_bytes(self.raw + b' ')
        with patch.object(self.store.local, 'put', side_effect=AssertionError('WRITE')), self.assertRaises(ValueError):
            operation.execute(self.contract, self.store, ResponseFetcher(self), budget, normalized)
        self.assertEqual(budget.reservations, 0)
    def test_actual_fetcher_5xx_is_one_wire_attempt_one_charge_and_status_is_retained(self):
        for status in (500, 502, 503, 504):
            with self.subTest(status=status):
                opener = unittest.mock.Mock(); opener.open.side_effect = HTTPError(self.plan['sample']['url'], status, 'fake', {}, io.BytesIO())
                fetcher = Fetcher(self.store, timeout=12, max_bytes=operation.MAX_BODY_BYTES,
                                  redirect_diagnostics=True, unexpected_status_diagnostics=True)
                with patch('urllib.request.build_opener', return_value=opener), patch('fetcher.safe_url', side_effect=lambda url,*a,**kw:url), \
                     patch('fetcher.utcnow', return_value=NOW), patch('fetcher.time.sleep', side_effect=AssertionError('NO_RETRY')):
                    report = self.capture(fetcher)
                self.assertEqual(opener.open.call_count, 1); self.assertFalse(self.replay(report)['proposalEvidenceComplete'])
                row=report['results'][0]; self.assertEqual(row['httpStatus'], status)
                for key in ('body','contentType','finalUrl'): self.assertIsNone(row[key])
                self.assertEqual(report['reservationContext']['probeFetchReservations'], 1)
    def test_transport_read_size_failures_are_charged_and_unobserved_fields_stay_unknown(self):
        for error in (OSError('read'), ValueError('size'), RuntimeError('transport')):
            report=self.capture(ResponseFetcher(self,error=error)); self.replay(report)
            self.assertEqual(report['reservationContext']['probeFetchReservations'],1)
            self.assertFalse(report['proposalEvidenceComplete']); self.assertTrue(report['executionCompleted'])
            for k in ('body','contentType','finalUrl','httpStatus','fetchedAt'):self.assertIsNone(report['results'][0][k])
    def test_http_redirect_identity_mime_body_and_time_failures_keep_returned_body(self):
        cases=[{'httpStatus':n} for n in (203,302,403,429)] + [
            {'finalUrl':self.plan['sample']['url']+'-other'}, {'fetchedAt':'2026-10-25T14:00:00Z'},
            {'redirectDiagnostics':{'responses':[{'httpStatus':302}]}}, {'httpStatus':None}]
        cases += [{'contentType':m} for m in (None,'','application/json','text/html; charset=latin1')]
        for changes in cases:
            report=self.capture(ResponseFetcher(self,changes=changes));self.replay(report)
            self.assertFalse(report['proposalEvidenceComplete']);self.assertIsNotNone(report['results'][0]['body'])
        for body in (b'', b'{}', b'\xff', html(self).replace(b'rel="canonical"',b'rel="alternate"')):
            report=self.capture(ResponseFetcher(self,body));self.replay(report);self.assertFalse(report['proposalEvidenceComplete'])
    def test_publication_metadata_preserves_unknown_and_matching_written_offset(self):
        for meta in ('','<meta property="article:published_time" content="2026-10-16T23:30:00-12:00">',
                     '<script type="application/ld+json">{"@type":"NewsArticle","datePublished":"2026-10-16"}</script>'):
            report=self.capture(ResponseFetcher(self,html(self,meta)));self.replay(report)
            self.assertTrue(report['proposalEvidenceComplete']);shape=report['results'][0]['primaryShape']
            self.assertEqual(shape['dateMetadataState'],'present' if meta else 'unknown');self.assertIsNone(shape['indexTimezone'])
    def test_invalid_or_conflicting_supplied_metadata_and_wrong_heading_hold(self):
        metas=['<meta property="article:published_time" content="'+v+'">' for v in ('','tomorrow','2026-10-15')]
        metas += ['<script type="application/ld+json">{"@type":"NewsArticle","datePublished":'+v+'}</script>'
                  for v in ('null','123','[]','""','"2026-10-16","datePublished":"2026-10-15"')]
        metas += ['<time datetime=""></time>','<script type="application/ld+json"/>',
                  '<meta property="datePublished" property="other" content="2026-10-16">']
        for meta in metas:
            report=self.capture(ResponseFetcher(self,html(self,meta)));self.replay(report)
            self.assertFalse(report['proposalEvidenceComplete']);self.assertIn(meta.encode(),self.store.get(report['results'][0]['body']))
        body=html(self).replace(escape(self.plan['sample']['title']).encode(),b'Other headline')
        self.assertFalse(self.capture(ResponseFetcher(self,body))['proposalEvidenceComplete'])
    def test_exhausted_quota_day_deadline_cancel_and_final_guard_keep_truthful_charges(self):
        self.local.compare_and_swap('budget-2026-10-25',None,{'calls':80,'documents':39,'fetches':5500})
        report=self.capture();self.assertEqual(self.fetcher.calls,[]);self.replay(report)
        self.assertEqual(report['reservationContext']['currentBudget'],{'calls':80,'documents':39,'fetches':5500})
        self.local.compare_and_swap('budget-2026-10-25',self.local.read('heads/budget-2026-10-25.json'),{'calls':80,'documents':39,'fetches':1511})
        for boundary in ('day','deadline','cancel'):
            self.clock=Clock();budget=self.budget()
            def cross():
                if boundary=='day':self.clock.wall=NEXT_DAY
                elif boundary=='deadline':self.clock.elapsed=1200
                else:budget.deadline=0
            report=self.capture(ResponseFetcher(self,callback=cross),budget);self.replay(report)
            self.assertEqual(len(self.fetcher.calls),1);self.assertFalse(report['executionCompleted']);self.assertIsNotNone(report['results'][0]['body'])
        self.clock=Clock();budget=self.budget();budget.deadline=0
        report=self.capture(budget=budget);self.assertEqual(self.fetcher.calls,[]);self.replay(report)
    def test_day_crossing_before_transport_keeps_charged_fetch(self):
        budget=self.budget();original=budget.before_fetch;calls=0
        def guard():
            nonlocal calls
            calls+=1
            if calls==2:self.clock.wall=NEXT_DAY
            return original()
        budget.before_fetch=guard
        report=self.capture(budget=budget);self.replay(report);self.assertEqual(self.fetcher.calls,[])
        self.assertEqual(budget.reservations,1);self.assertIsNone(report['requests'][0]['requestedAt'])
    def test_budget_binding_exclusivity_and_lease_context_denials_precede_transport(self):
        import collect
        normalized=operation.validate_plan(self.contract,self.store,self.raw,self.path)
        budget=self.budget()
        budget.contract_sha256='a'*64
        with self.assertRaises(ValueError):operation.execute(self.contract,self.store,ResponseFetcher(self),budget,normalized)
        budget=self.budget();budget.reservations=1
        with self.assertRaises(ValueError):operation.execute(self.contract,self.store,ResponseFetcher(self),budget,normalized)
        with patch.object(collect.session_runtime,'require_source_probe_context',side_effect=ValueError('LEASE_REQUIRED')), \
             patch.object(collect,'Fetcher',side_effect=AssertionError('NO_TRANSPORT')):
            with self.assertRaises(ValueError):
                collect.execute_source_probe(self.root,self.store,{'checkpointProfile':'source_probe','sessionId':'unbound'},self.contract,1200)
        self.assertIsNone(self.local.read('heads/budget-2026-10-25.json'))
    def test_shared_caller_preflight_failure_retains_zero_credit_outer_fields(self):
        import collect
        (self.root/'contracts').mkdir()
        changed=copy.deepcopy(self.plan);changed['maxRequests']=2
        (self.root/'contracts/source-qualification-probes.json').write_bytes(canonical(changed))
        with patch.object(collect,'REPO',self.root),patch.object(collect.session_runtime,'require_source_probe_context'), \
             patch.object(collect,'Fetcher',side_effect=AssertionError('NO_TRANSPORT')):
            with self.assertRaises(ValueError):
                collect.execute_source_probe(self.root,self.store,{'checkpointProfile':'source_probe','sessionId':'synthetic'},self.contract,1200)
        records=list((self.local.root/'ci/source-probe-failures').rglob('*.json'))
        self.assertEqual(len(records),1);failed=json.loads(records[0].read_bytes())
        self.assertEqual(failed['facts'],[])
        for key in operation.ZERO_FIELDS:self.assertEqual(failed[key],0)
        self.assertFalse(failed['executionCompleted']);self.assertIsNone(self.local.read('heads/budget-2026-10-25.json'))
    def test_missing_transport_fields_remain_unknown_with_original_raw_observation(self):
        for missing in ('httpStatus','finalUrl','contentType','body','fetchedAt'):
            fixture=self
            class Missing(ResponseFetcher):
                def fetch(self,*args,**kwargs):
                    observed=super().fetch(*args,**kwargs);del observed[missing];return observed
            report=self.capture(Missing(fixture));self.replay(report)
            self.assertFalse(report['proposalEvidenceComplete']);self.assertIsNone(report['results'][0][missing])
            wrapper=json.loads(self.store.get(report['requests'][0]['observation']))
            self.assertNotIn(missing,json.loads(self.store.get(wrapper['rawObservation'])))

    def test_report_observation_reservation_and_credit_tampering_rejects(self):
        report=self.capture()
        mutations=[lambda p:p.update(extra=True),lambda p:p.update(facts=[{}]),lambda p:p.update(modelCalls=1),
                   lambda p:p.update(qualified=True),lambda p:p.update(proposalEvidenceComplete=False),lambda p:p.update(acceptedSamples=True),
                   lambda p:p.update(checkedAt='2026-10-25T14:00:00Z'), lambda p:p['streams'][0].update(asOf=NOW),
                   lambda p:p['results'][0].update(httpStatus=503),lambda p:p['requests'][0].update(requestedAt=None),
                   lambda p:p['requests'][0]['reservation'].update(chargedFetchCount=2),
                   lambda p:p['reservationContext'].update(probeFetchReservations=2)]
        for change in mutations:
            changed=copy.deepcopy(report);change(changed)
            with self.subTest(change=change),self.assertRaises((ValueError,KeyError,TypeError)):self.replay(changed)
    def test_shared_leased_caller_routes_directly_and_preserves_outer_zeros(self):
        import collect
        events=[];(self.root/'contracts').mkdir();(self.root/'contracts/source-qualification-probes.json').write_bytes(self.raw)
        def transport(*args,**kwargs):
            self.assertEqual(kwargs,{'timeout':12,'max_bytes':2_000_000,'redirect_diagnostics':True,'unexpected_status_diagnostics':True})
            events.append('transport');return ResponseFetcher(self)
        with patch.object(collect,'REPO',self.root),patch.object(collect,'PersistentProbeBudget',side_effect=lambda *a,**k:self.budget()), \
             patch.object(collect,'escrow_budgets',side_effect=lambda *a:events.append('escrow')),patch.object(collect,'Fetcher',side_effect=transport), \
             patch.object(collect,'probe_sources',side_effect=AssertionError('NO_GENERIC')),patch.object(collect.session_runtime,'require_source_probe_context'), \
             patch.object(collect.session_runtime,'checkpoint',return_value={'archive':{'synthetic':True}}), \
             patch.dict('os.environ',{'GITHUB_RUN_ID':'123','GITHUB_RUN_ATTEMPT':'1','GITHUB_EVENT_NAME':'workflow_dispatch','GITHUB_REF':'refs/heads/main'}):
            result=collect.execute_source_probe(self.root,self.store,{'checkpointProfile':'source_probe','sessionId':'synthetic','appRevision':'a'*40},self.contract,1200)
        self.assertEqual(events,['escrow','transport']);self.assertEqual(result['facts'],[])
        self.assertTrue(result['diagnostic']['proposalEvidenceComplete']);self.assertEqual(result['modelCalls'],0)


@unittest.skipUnless((ARCHIVE/'archive-manifest.json').exists(), 'Full actual-J archive replay only; portable core tests always run')
class FullActualArchiveTests(unittest.TestCase):
    def test_full_original_H_diagnostic_replay_from_authenticated_J_read_only(self):
        from test_prnewswire_retained_window import replay_complete
        raw=(ARCHIVE/'archive-manifest.json').read_bytes()
        self.assertEqual(digest(raw),'13d956802cd881c0d6805c00c0dee48de07bd6615196e69f74fbf4056a710e34')
        entries={r['key']:r for r in json.loads(raw)['files']};self.assertEqual(len(entries),52273)
        pins={}
        class ReadOnly:
            def raw(_,key):
                relative='state/'+key;path=ARCHIVE/relative;row=entries[relative]
                assert not path.is_symlink() and path.resolve().is_relative_to(ARCHIVE)
                raw=path.read_bytes();assert digest(raw)==row['sha256'] and len(raw)==row['bytes']
                pins[str(path)]=(digest(raw),len(raw),path.stat().st_mtime_ns);return raw
            def get(self,ref):
                raw=self.raw(ref['key']);assert digest(raw)==ref['sha256'] and len(raw)==ref['bytes'];return raw
            def read(self,key):return json.loads(self.raw(key))
        base=ReadOnly();contract=json.loads((ROOT/'contracts/market.json').read_bytes());rawplan=PLAN.read_bytes()
        with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')),patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_STORE')):
            normalized=operation.validate_plan(contract,base,rawplan)
            original=operation.origin.inverse_policy(contract,base)
            record=json.loads(base.get(normalized['plan']['historicalReplay']['record']))
            self.assertTrue(replay_complete(record,original,base)['fullLegacyTraversalReplay'])
        for name,before in pins.items():
            path=Path(name);self.assertEqual((digest(path.read_bytes()),path.stat().st_size,path.stat().st_mtime_ns),before)
        self.assertGreater(len(pins),100)


if __name__ == '__main__':unittest.main()
