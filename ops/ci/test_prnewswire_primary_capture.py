"""Portable two-fetch mechanics and exact retained PR Newswire proof; no real transport."""
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

import base64, gzip, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'web/scripts/pipeline'),str(ROOT/'ops/ci')]
PLAN=ROOT/'docs/active/daily-pipeline/accuracy/prnewswire-primary-capture-plan-2026-10-25.json'
AS_OF='2026-10-25T12:42:16.956348Z'
class FixtureStore:
    def __init__(self):
        raw=(ROOT/'ops/ci/fixtures/prnewswire-primary-retained-readset.json.gz').read_bytes()
        assert digest(raw)=='490b649e268337ceb47cc4c3080bfbc6e3d6fd69d58224e40bc6cd40b1cde2b9'
        value=json.loads(gzip.decompress(raw));assert value['archiveManifestFiles']==52273
        self.rows=value['consumed'];self.touched=set()
    def raw(self,key):
        row=self.rows[key];raw=base64.b64decode(row['base64'],validate=True)
        assert digest(raw)==row['entry']['sha256'] and len(raw)==row['entry']['bytes']
        self.touched.add(key);return raw
    def get(self,ref):
        raw=self.raw(ref['key']);assert digest(raw)==ref['sha256'] and len(raw)==ref['bytes'];return raw
    def read(self,key):return json.loads(self.raw(key))

from q4_intake_fixtures import frozen_j_asset
from contracts import canonical, digest
from storage import LocalStore
from onboarding import PersistentProbeBudget
from fetcher import Fetcher
import prnewswire_primary_capture as operation

NOW = '2026-10-25T15:00:00Z'
NEXT_DAY = '2026-10-26T00:00:00Z'
ARCHIVE = Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted')

# Only these transport/report unit cases substitute an authenticated normalized
# preflight context. Authority/raw-proof and full end-to-end cases stay uncached.
MECHANICS_METHODS = frozenset({
    'test_actual_fetcher_5xx_is_one_wire_attempt_one_charge_and_status_is_retained',
    'test_budget_binding_exclusivity_and_lease_context_denials_precede_transport',
    'test_changed_live_plan_or_failed_preflight_cannot_write_or_charge',
    'test_day_crossing_before_transport_keeps_charged_fetch',
    'test_exhausted_quota_day_deadline_cancel_and_final_guard_keep_truthful_charges',
    'test_first_success_second_quota_denial_has_one_charge_and_unreached_hold',
    'test_http_redirect_identity_mime_body_and_time_failures_keep_returned_body',
    'test_missing_transport_fields_remain_unknown_with_original_raw_observation',
    'test_report_observation_reservation_and_credit_tampering_rejects',
    'test_required_template_metadata_and_all_present_publication_days',
    'test_shared_caller_preflight_failure_retains_zero_credit_outer_fields',
    'test_transport_read_size_failures_are_charged_and_unobserved_fields_stay_unknown',
})


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


def html(fixture, metadata='', target=0):
    sample=fixture.plan['sources'][target]['selectedRecord'];url=sample['url'];title=sample['title']
    data={'@type':'NewsArticle','mainEntityOfPage':{'@id':url},'headline':title,
          'datePublished':sample['calendarDay']+'T01:00:00','dateModified':sample['calendarDay']+'T02:00:00'}
    issuer=('Cato Networks','Chainguard')[target]
    return ('<html><head><link rel="canonical" href="'+url+'">'+metadata+
        '<script type="application/ld+json">'+json.dumps(data)+'</script></head><body><main id="main">'+
        '<article class="news-release"><header class="release-header"><h1>'+escape(title)+
        '</h1></header><section class="release-body">'+issuer+' '+
        'Synthetic transport fixture article text. '*10+'</section></article></main></body></html>').encode()


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
                  'body': self.fixture.store.put(self.body if self.body is not None else html(self.fixture,target=len(self.calls)-1))}
        result.update(self.changes)
        return result


class CaptureTests(unittest.TestCase):
    _normalized_mechanics_bytes = None

    @classmethod
    def authenticated_mechanics_bytes(cls):
        if cls._normalized_mechanics_bytes is None:
            # This is test-only normalization, authenticated once through the
            # unchanged production validator and sealed portable input graph.
            with patch.object(socket.socket, 'connect', side_effect=AssertionError('NO_NETWORK')), \
                 patch.object(LocalStore, '__init__', side_effect=AssertionError('NO_FROZEN_STORE')):
                contract = frozen_j_asset(ROOT)
                normalized = operation.validate_plan(contract, FixtureStore(), PLAN.read_bytes())
            cls._normalized_mechanics_bytes = canonical({
                'targets': normalized['targets'], 'streams': normalized['streams']})
        return cls._normalized_mechanics_bytes

    def start_normalized_mechanics_boundary(self):
        if self._testMethodName not in MECHANICS_METHODS:
            return
        frozen = self.authenticated_mechanics_bytes()
        def normalized_context(contract, store, plan):
            # validate_plan still parses/hashes the plan and checks its contract
            # before this explicit unit boundary. Every return is a fresh copy.
            context = json.loads(frozen)
            return context['targets'], context['streams']
        boundary = patch.object(operation, '_validate_capture', side_effect=normalized_context)
        self.mechanics_boundary = boundary.start()
        self.addCleanup(boundary.stop)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.clock = Clock(); self.base = FixtureStore()
        self.local = LocalStore(self.root / 'state'); self.store = Overlay(self.local, self.base)
        self.contract = frozen_j_asset(ROOT)
        self.raw = PLAN.read_bytes(); self.plan = json.loads(self.raw)
        self.path = self.root / 'plan.json'; self.path.write_bytes(self.raw)
        self.net = patch.object(socket.socket, 'connect', side_effect=AssertionError('NO_NETWORK'))
        self.net.start(); self.addCleanup(self.net.stop)
        self.normal = {'heads/latest-run.json': {'old': 'normal'}, 'heads/production.json': {'old': 'production'}}
        for key, value in self.normal.items(): self.local.write_once(key, value)
        self.start_normalized_mechanics_boundary()
    def budget(self):
        return PersistentProbeBudget(self.store, self.contract, clock=self.clock.now, monotonic=self.clock.monotonic)
    def capture(self, fetcher=None, budget=None):
        self.fetcher = fetcher or ResponseFetcher(self); self.context = budget or self.budget()
        normalized = operation.validate_plan(self.contract, self.store, self.raw, self.path)
        report = operation.execute(self.contract, self.store, self.fetcher, self.context, normalized)
        return operation.finalize_report(self.contract, self.store, self.raw, report, self.context)
    def replay(self, report): return operation.verify_report(self.contract, self.store, self.raw, report)
    def test_two_logical_gets_no_generic_candidates_or_other_credits(self):
        import onboarding
        self.assertEqual(len([s for s in self.contract['sources'] if s['registration'] == 'candidate']), 23)
        with patch.object(onboarding, 'probe_sources', side_effect=AssertionError('NO_GENERIC_PROBES')):
            report = self.capture()
        self.assertTrue(self.replay(report)['proposalEvidenceComplete']); self.assertEqual(report['acceptedSamples'], 2)
        self.assertEqual(self.fetcher.calls, [(r['sourceId'],r['url'],None,2) for r in self.plan['sources']])
        self.assertEqual(report['reservationContext']['currentBudget'], {'calls': 0, 'documents': 0, 'fetches': 2})
        self.assertEqual(report['streams'][0]['asOf'], AS_OF); self.assertEqual(report['facts'], [])
        for key in operation.ZERO_FIELDS: self.assertEqual(report[key], 0)
        for key, value in self.normal.items(): self.assertEqual(self.local.read(key), value)
    def test_full_consumed_actual_graph_is_portable_and_read_only(self):
        with patch.object(LocalStore, '__init__', side_effect=AssertionError('NO_FROZEN_STORE')):
            result = operation.validate_plan(self.contract, self.base, self.raw)
        self.assertEqual(len(result['streams'][0]['records']), 125); self.assertEqual(len(self.base.touched), 63)
    def test_plan_policy_and_descriptor_substitutions_reject_before_writes_or_reservations(self):
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
            return raw+b' ' if str(path).endswith('prnewswire-retained-window-descriptor-2026-10-25.json') else raw
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
                opener = unittest.mock.Mock(); opener.open.side_effect = HTTPError(self.plan['sources'][0]['url'], status, 'fake', {}, io.BytesIO())
                fetcher = Fetcher(self.store, timeout=12, max_bytes=operation.MAX_BODY_BYTES,
                                  redirect_diagnostics=True, unexpected_status_diagnostics=True)
                with patch('urllib.request.build_opener', return_value=opener), patch('fetcher.safe_url', side_effect=lambda url,*a,**kw:url), \
                     patch('fetcher.utcnow', return_value=NOW), patch('fetcher.time.sleep', return_value=None):
                    report = self.capture(fetcher)
                self.assertEqual(opener.open.call_count, 2); self.assertFalse(self.replay(report)['proposalEvidenceComplete'])
                row=report['results'][0]; self.assertEqual(row['httpStatus'], status)
                for key in ('body','contentType','finalUrl'): self.assertIsNone(row[key])
                self.assertEqual(report['reservationContext']['probeFetchReservations'], 2)
    def test_transport_read_size_failures_are_charged_and_unobserved_fields_stay_unknown(self):
        for error in (OSError('read'), ValueError('size'), RuntimeError('transport')):
            report=self.capture(ResponseFetcher(self,error=error)); self.replay(report)
            self.assertEqual(report['reservationContext']['probeFetchReservations'],2)
            self.assertFalse(report['proposalEvidenceComplete']); self.assertTrue(report['executionCompleted'])
            for k in ('body','contentType','finalUrl','httpStatus','fetchedAt'):self.assertIsNone(report['results'][0][k])
    def test_http_redirect_identity_mime_body_and_time_failures_keep_returned_body(self):
        cases=[{'httpStatus':n} for n in (203,302,403,429)] + [
            {'finalUrl':self.plan['sources'][0]['url']+'-other'}, {'fetchedAt':'2026-10-25T14:00:00Z'},
            {'redirectDiagnostics':{'responses':[{'httpStatus':302}]}}, {'httpStatus':None}]
        cases += [{'contentType':m} for m in (None,'','application/json','text/html; charset=latin1')]
        for changes in cases:
            report=self.capture(ResponseFetcher(self,changes=changes));self.replay(report)
            self.assertFalse(report['proposalEvidenceComplete']);self.assertIsNotNone(report['results'][0]['body'])
        for body in (b'', b'{}', b'\xff', html(self).replace(b'rel="canonical"',b'rel="alternate"')):
            report=self.capture(ResponseFetcher(self,body));self.replay(report);self.assertFalse(report['proposalEvidenceComplete'])
    def test_required_template_metadata_and_all_present_publication_days(self):
        self.assertTrue(self.capture()['proposalEvidenceComplete'])
        for meta in ('<meta property="article:published_time" content="2026-10-07">',
                     '<time datetime=""></time>', '<meta property="datePublished" content="tomorrow">'):
            report=self.capture(ResponseFetcher(self,html(self,meta)))
            self.assertFalse(report['proposalEvidenceComplete']);self.replay(report)
        for old,new in ((b'NewsArticle',b'Product'),(b'Cato Networks Achieves',b'Other title'),
                        (b'2026-10-06T01:00:00',b'2026-10-07T01:00:00'),
                        (b'class="release-body"',b'hidden class="release-body"')):
            report=self.capture(ResponseFetcher(self,html(self).replace(old,new)))
            self.assertFalse(report['proposalEvidenceComplete']);self.replay(report)
    def test_partial_failure_retains_both_actual_results(self):
        class Partial(ResponseFetcher):
            def fetch(inner,*args,**kwargs):
                result=super().fetch(*args,**kwargs)
                if len(inner.calls)==2:result['httpStatus']=503
                return result
        report=self.capture(Partial(self));self.replay(report)
        self.assertEqual(report['acceptedSamples'],1);self.assertEqual(len(report['results']),2)
        self.assertEqual(report['results'][1]['httpStatus'],503)
        self.assertEqual(report['reservationContext']['probeFetchReservations'],2)
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
    def test_first_success_second_quota_denial_has_one_charge_and_unreached_hold(self):
        self.local.compare_and_swap('budget-2026-10-25',None,{'calls':80,'documents':39,'fetches':5499})
        report=self.capture();self.replay(report)
        self.assertEqual(len(self.fetcher.calls),1);self.assertTrue(report['results'][0]['accepted'])
        self.assertFalse(report['results'][1]['accepted']);self.assertEqual(report['results'][1]['reason'],'TRANSPORT_NOT_OBSERVED')
        self.assertEqual(report['requests'][1]['denial'],'FETCHES_BUDGET_EXHAUSTED')
        self.assertIsNone(report['requests'][1]['requestedAt']);self.assertIsNone(report['requests'][1]['reservation'])
        self.assertEqual(report['reservationContext']['probeFetchReservations'],1)
        self.assertEqual(report['reservationContext']['currentBudget'],{'calls':80,'documents':39,'fetches':5500})
    def test_transition_pointer_raw_hash_is_checked_even_if_json_value_matches(self):
        base=self.base
        class WhitespacePointer:
            def read(_,key):return base.read(key)
            def get(_,ref):
                raw=base.get(ref)
                return raw+b' ' if ref['key'].startswith('source-qualification-transitions/') else raw
        with self.assertRaises(ValueError):operation.validate_plan(self.contract,WhitespacePointer(),self.raw)
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
        changed=copy.deepcopy(self.plan);changed['maxRequests']=3
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
                   lambda p:p['reservationContext'].update(probeFetchReservations=3)]
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



class MechanicsBoundaryTests(unittest.TestCase):
    def test_all_authority_and_full_capture_examples_remain_outside_unit_boundary(self):
        uncached = {
            'test_every_consumed_original_input_is_authenticated',
            'test_full_consumed_actual_graph_is_portable_and_read_only',
            'test_partial_failure_retains_both_actual_results',
            'test_plan_policy_and_descriptor_substitutions_reject_before_writes_or_reservations',
            'test_shared_leased_caller_routes_directly_and_preserves_outer_zeros',
            'test_transition_pointer_raw_hash_is_checked_even_if_json_value_matches',
            'test_two_logical_gets_no_generic_candidates_or_other_credits',
        }
        methods = {name for name in dir(CaptureTests) if name.startswith('test_')}
        self.assertEqual(methods - MECHANICS_METHODS, uncached)
        self.assertTrue(MECHANICS_METHODS.isdisjoint(uncached))
        self.assertEqual(len(MECHANICS_METHODS), 12)
        for name in uncached:
            case = CaptureTests(name)
            with patch.object(case, 'authenticated_mechanics_bytes', side_effect=AssertionError('UNCACHED_REQUIRED')):
                case.start_normalized_mechanics_boundary()
            self.assertFalse(hasattr(case, 'mechanics_boundary'))

    def test_normalized_bytes_match_fresh_uncached_full_sealed_graph(self):
        frozen = CaptureTests.authenticated_mechanics_bytes()
        contract = frozen_j_asset(ROOT)
        with patch.object(socket.socket, 'connect', side_effect=AssertionError('NO_NETWORK')), \
             patch.object(LocalStore, '__init__', side_effect=AssertionError('NO_FROZEN_STORE')):
            normalized = operation.validate_plan(contract, FixtureStore(), PLAN.read_bytes())
        self.assertEqual(frozen, canonical({'targets': normalized['targets'], 'streams': normalized['streams']}))
        self.assertIs(type(frozen), bytes)

    def test_unit_context_copies_and_outer_plan_contract_checks_remain_live(self):
        case = CaptureTests('test_http_redirect_identity_mime_body_and_time_failures_keep_returned_body')
        self.addCleanup(case.doCleanups)
        case.setUp()
        self.assertTrue(hasattr(case, 'mechanics_boundary'))
        changed = copy.deepcopy(case.contract)
        changed['sources'][0]['extra'] = True
        for raw, contract in ((b'[]', case.contract), (b'{}', case.contract),
                              (case.raw + b' ', case.contract), (case.raw, changed)):
            with self.subTest(raw=raw[:20]), self.assertRaises((ValueError, KeyError, TypeError)):
                operation.validate_plan(contract, case.store, raw)
        case.mechanics_boundary.assert_not_called()
        first = operation.validate_plan(case.contract, case.store, case.raw)
        first['targets'][0]['url'] = 'synthetic-mutated-copy'
        first['streams'][0]['records'].clear()
        second = operation.validate_plan(case.contract, case.store, case.raw)
        self.assertEqual(second['targets'][0]['url'], case.plan['sources'][0]['url'])
        self.assertEqual(len(second['streams'][0]['records']), 125)
        self.assertEqual(case.mechanics_boundary.call_count, 2)


@unittest.skipUnless((ARCHIVE/'archive-manifest.json').exists(),'Explicit full archive original-H replay only')
class FullHistoricalReplay(unittest.TestCase):
    def test_both_original_diagnostics_replay_in_full_under_H(self):
        from test_priority_two_corrections import ReadOnlyJ
        from test_prnewswire_retained_window import replay_complete
        import q4_qualification_origin as origin
        base=ReadOnlyJ();market=frozen_j_asset(ROOT)
        with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')), \
             patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_STORE')):
            old=origin.inverse_policy(market,base)
            for pin in json.loads(PLAN.read_bytes())['originalRuns']:
                record=json.loads(base.get(pin['record']))
                self.assertTrue(replay_complete(record,old,base)['fullLegacyTraversalReplay'])
        base.unchanged(self)

if __name__=='__main__':unittest.main()
