"""Offline fixed-inventory Q4 capture. Synthetic JavaScript earns no source credit."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'web/scripts/pipeline'), str(ROOT / 'ops/ci')]
from contracts import canonical, digest
from onboarding import PersistentProbeBudget
from storage import LocalStore
from test_s1_exact_filing_transport import ReadOnlyArchive, ARCHIVE
import q4_controller_capture as q4

PLAN = ROOT / 'docs/active/daily-pipeline/accuracy/q4-controller-capture-plan-2026-10-25.json'
NOW = '2026-10-25T12:00:00Z'


class Clock:
    def __init__(self): self.wall, self.elapsed = NOW, 0
    def now(self): return self.wall
    def monotonic(self): return self.elapsed


def markup():
    return ('<html><head>' + ''.join('<script type="text/javascript" src="' + p + '"></script>'
                                     for p in q4.PATHS) + '</head><body></body></html>').encode()


class CaptureFetcher:
    def __init__(self, fixture, response=None, callback=None):
        self.fixture, self.response, self.callback, self.calls = fixture, response, callback, []
    def fetch(self, source, url):
        self.calls.append((source['id'], url))
        if self.callback: self.callback(self, source, url)
        if isinstance(self.response, Exception): raise self.response
        result = {'requestedUrl': url, 'finalUrl': url, 'fetchedAt': self.fixture.clock.wall,
                  'status': 'fetched', 'httpStatus': 200, 'contentType': 'application/javascript; charset=utf-8',
                  'body': self.fixture.store.put(b'window.syntheticQ4Capture = function () { return 1; };')}
        if self.response: result.update(self.response)
        return result


class Q4CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.store = LocalStore(self.root / 'state'); self.clock = Clock()
        self.contract = json.loads((ROOT / ('contracts/html-qualification-seeds/' + '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db' + '/contracts__' + '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db' + '.json')).read_bytes())
        self.plan = json.loads(PLAN.read_bytes()); self.path = self.root / 'plan.json'
        # Only synthetic unit fixtures bypass the old diagnostic replay. Actual archive tests below do not.
        record = {'checkpointProfile': 'source_probe', 'contractSha256': q4.POLICY_SHA256,
                  'githubEventName': 'workflow_dispatch', 'githubRef': 'refs/heads/main',
                  'githubRunId': '40131875060', 'githubRunAttempt': 1, 'semanticAdmission': False,
                  'coverageCredit': False, 'qualifiedSources': 0, 'sourceChecksCredited': 0, 'modelCalls': 0}
        raw = canonical(record); key = 'ci/source-probe-runs/40131875060-1.json'; self.store.write_once(key, raw)
        ref = {'key': key, 'bytes': len(raw), 'sha256': digest(raw)}
        observed = {}
        for row, binding in zip(self.plan['sources'], q4.BINDINGS):
            sid, _, host, parent, _, _, _ = binding
            url = 'https://' + host + parent; proof = row['parentProof']
            proof['record'] = ref; proof['body'] = self.store.put(markup())
            observed[sid] = {'requestedUrl': url, 'finalUrl': url, 'status': 'fetched', 'httpStatus': 200,
                             'contentType': 'text/html; charset=utf-8', 'body': proof['body'], 'fetchedAt': proof['fetchedAt']}
        for authority in (patch.object(q4, 'PARENT_RECORD', ref),
                          patch.object(q4, '_qualification_proof_policy', side_effect=lambda r,p,s,c,t:(c,s)),
                          patch.object(q4, '_qualification_explicit_observation', side_effect=lambda r,p,s,c,t:observed[s['id']])):
            authority.start(); self.addCleanup(authority.stop)
        self.observed = observed
        self.save()
        for key in ('heads/collection.json', 'heads/publication.json', 'heads/latest-run.json',
                    'heads/correction-admissions.json', 'correction-admissions/old.json'):
            self.store.write_once(key, {'protected': key})
        self.protected = {str(p.relative_to(self.store.root)): p.read_bytes()
                          for p in self.store.root.rglob('*.json') if 'objects' not in p.parts}

    def save(self): self.path.write_bytes(canonical(self.plan))
    def budget(self):
        return PersistentProbeBudget(self.store, self.contract, clock=self.clock.now, monotonic=self.clock.monotonic)
    def run_report(self, fetcher=None, budget=None):
        self.fetcher = fetcher or CaptureFetcher(self)
        plan = q4.validate_plan(self.contract, self.store, self.path.read_bytes(), self.path)
        self.context = budget or self.budget()
        return q4.execute(self.contract, self.store, self.fetcher, self.context, plan)
    def replay(self, report): return q4.verify_report(self.contract, self.store, self.path.read_bytes(), report)

    def test_six_synthetic_captures_replay_without_execution_or_qualification(self):
        with patch('builtins.exec', side_effect=AssertionError('must never execute body')):
            report = self.run_report()
            self.assertTrue(self.replay(report)['captureComplete'])
        self.assertEqual(len(self.fetcher.calls), 6)
        self.assertEqual(self.fetcher.calls, [(r['sourceId'], u) for r in self.plan['sources'] for u in r['targets']])
        self.assertEqual(report['reservationContext']['currentBudget'], {'calls': 0, 'documents': 0, 'fetches': 6})
        for row in [report, *report['results']]:
            for key in q4.ZERO_FIELDS: self.assertEqual(row[key], 0)
            for key in ('qualified', 'semanticAdmission', 'coverageCredit'): self.assertIs(row[key], False)
            self.assertEqual(row['facts'], [])
        for key, body in self.protected.items(): self.assertEqual((self.store.root / key).read_bytes(), body)
        # Actual H omits maxRuntimeSeconds; the existing 7200-second contract default applies.
        self.assertNotIn('maxRuntimeSeconds', self.contract['schedule'])
        self.assertEqual(q4.finalize_report(self.contract, self.store, self.path.read_bytes(), report, self.context), report)

    def test_exact_plan_inventory_and_source_fields_fail_before_writes_or_reservations(self):
        mutations = [lambda p:p.update(schemaVersion=True), lambda p:p.update(maxRequests=6.0),
                     lambda p:p.update(extra=True), lambda p:p.update(marketSha256='0'*64),
                     lambda p:p['sources'].pop(), lambda p:p['sources'].append(copy.deepcopy(p['sources'][0])),
                     lambda p:p['sources'].reverse(), lambda p:p['sources'][0].update(supplierId='rapid7'),
                     lambda p:p['sources'][0].update(originalSourceSha256='0'*64),
                     lambda p:p['sources'][0].update(extra=True), lambda p:p['sources'][0]['targets'].reverse(),
                     lambda p:p['sources'][0]['targets'].pop(), lambda p:p['sources'][0]['targets'].append(p['sources'][0]['targets'][0])]
        original = copy.deepcopy(self.plan)
        for mutate in mutations:
            self.plan = copy.deepcopy(original); mutate(self.plan); self.save()
            before = sorted((str(p), p.read_bytes()) for p in self.store.root.rglob('*') if p.is_file())
            with self.subTest(mutate=mutate), patch.object(self.store, 'put', side_effect=AssertionError('preflight wrote')):
                with self.assertRaises((ValueError, KeyError, TypeError)): self.run_report()
            self.assertEqual(self.fetcher.calls, [])
            self.assertEqual(before, sorted((str(p), p.read_bytes()) for p in self.store.root.rglob('*') if p.is_file()))

    def test_unsafe_or_neighbor_target_urls_are_rejected(self):
        original = self.plan['sources'][0]['targets'][0]
        values = [original+'#x', original+'?x=1', original.replace('https:', 'http:'),
                  original.replace('.com/', '.com:443/'), original.replace('.com/', '.com:444/'),
                  original.replace('https://', 'https://user:password@'), original.replace('investors.jfrog.com', 'ir.rubrik.com'),
                  original.replace('/js/', '/%6as/'), original.replace('/js/', '/x/../js/'),
                  original.replace('q4Api', 'q4Other'), '//investors.jfrog.com'+q4.PATHS[0]]
        for url in values:
            with self.subTest(url=url):
                self.plan['sources'][0]['targets'][0] = url; self.save()
                with self.assertRaises(ValueError): self.run_report()
                self.assertEqual(self.fetcher.calls, [])

    def test_parent_proof_shape_hash_time_and_identity_are_bound(self):
        original = copy.deepcopy(self.plan)
        mutations = [lambda p:p.update(extra=True), lambda p:p.pop('body'),
                     lambda p:p.update(type='source_observation'), lambda p:p.update(priorTargetIndex=True),
                     lambda p:p.update(priorTargetIndex=5), lambda p:p.update(priorTargetId='next-rapid7-1'),
                     lambda p:p.update(record={**p['record'], 'sha256':'0'*64}),
                     lambda p:p.update(body={**p['body'], 'bytes':1}), lambda p:p.update(fetchedAt=NOW)]
        for mutate in mutations:
            self.plan = copy.deepcopy(original); mutate(self.plan['sources'][0]['parentProof']); self.save()
            with self.subTest(mutate=mutate):
                with self.assertRaises((ValueError, KeyError)): self.run_report()
                self.assertEqual(self.fetcher.calls, [])

    def test_live_plan_change_is_rejected_before_operation_writes(self):
        normalized = q4.validate_plan(self.contract, self.store, self.path.read_bytes(), self.path)
        self.path.write_bytes(self.path.read_bytes()+b' ')
        with patch.object(self.store, 'put', side_effect=AssertionError('changed plan wrote')):
            with self.assertRaisesRegex(ValueError, 'CURRENT_PLAN_CHANGED'):
                q4.execute(self.contract, self.store, CaptureFetcher(self), self.budget(), normalized)

    def test_literal_script_context_attributes_duplicates_and_base_are_strict(self):
        good = markup().decode(); first = '<script type="text/javascript" src="'+q4.PATHS[0]+'"></script>'
        cases = [good.replace(first, ''), good.replace(first, first*2),
                 good.replace(first, '<template>'+first+'</template>'), good.replace(first, '<noscript>'+first+'</noscript>'),
                 good.replace(first, '<template/>'+first), good.replace(first, '<noscript/>'+first),
                 good.replace(first, '<!--'+first+'-->'), good.replace(first, '<textarea>'+first+'</textarea>'),
                 good.replace(first, '<script>var text='+json.dumps(first)+';</script>'),
                 good.replace(first, first.replace('src=', 'src="wrong" src=')),
                 good.replace(first, first.replace('type="text/javascript"', 'type="application/json"')),
                 good.replace(first, first.replace(' src=', ' nomodule="" src=')),
                 good.replace(first, first.replace('/js/', '&#47;js/')),
                 good.replace(first, first.replace('></script>', '/>')),
                 good.replace(first, first.replace('></script>', '>alert(1)</script>')),
                 good.replace(first, first.replace('src="'+q4.PATHS[0]+'"', 'src='+q4.PATHS[0])),
                 good.replace('<head>', '<head><base href="https://evil.invalid/">'),
                 good.replace('<head>', '<head><base href="/">'), good.replace('/js/', '//evil.invalid/js/', 1)]
        self.assertEqual(q4.script_disclosures(markup()), list(q4.PATHS))
        for body in cases:
            with self.subTest(body=body[:160]), self.assertRaises(ValueError): q4.script_disclosures(body.encode())
        with self.assertRaises(UnicodeError): q4.script_disclosures(b'\xff')

    def test_content_status_redirect_encoding_and_empty_failures_keep_original_bytes(self):
        bodies = [b'', b'  ', b'<html>Login</html>', b'{"ok":true}', b'[1,2]', b'"login"', b'\xff', b'\x1f\x8bcompressed', b'null', b'plain login text']
        responses = [{'body': self.store.put(body)} for body in bodies]
        responses += [{'contentType': m} for m in ('text/html', 'application/json', '', 'application/javascript; charset=latin1',
                                                  'text/javascript; charset=utf-8; extra=1')]
        responses += [{'status':'failed','httpStatus':203}, {'status':'not_modified','httpStatus':304},
                      {'finalUrl':'https://investors.jfrog.com/redirected'},
                      {'redirectDiagnostics':{'responses':[{'httpStatus':302}]}},
                      {'fetchedAt':'2026-10-24T12:00:00Z'}]
        for response in responses:
            with self.subTest(response=response):
                report = self.run_report(CaptureFetcher(self, response=response))
                self.assertFalse(report['captureComplete']); self.assertTrue(report['executionCompleted'])
                self.assertEqual(report['capturedControllers'], 0); self.replay(report)
                row = report['results'][0]
                if 'body' in response:
                    self.assertEqual(row['body'], response['body']); self.assertEqual(self.store.get(row['body']), self.store.get(response['body']))

    def test_unknown_network_fields_remain_unknown_and_transport_is_charged(self):
        f = CaptureFetcher(self)
        f.fetch = lambda source,url:{'requestedUrl':url,'fetchedAt':NOW,'status':'failed','httpStatus':None,'errorCode':'SOURCE_CONNECTION_FAILED'}
        report = self.run_report(f)
        self.assertEqual(report['reservationContext']['probeFetchReservations'], 6)
        for row in report['results']:
            for key in ('body','finalUrl','contentType','httpStatus'): self.assertIsNone(row[key])
        report = self.run_report(CaptureFetcher(self,response=OSError('fictional transport failure')))
        self.assertEqual(report['reservationContext']['probeFetchReservations'], 6)
        self.assertFalse(report['captureComplete']); self.replay(report)

    def test_budget_exhaustion_and_prefetch_cancellation_stop_without_refund(self):
        self.store.compare_and_swap('budget-2026-10-25', None, {'calls':72,'documents':33,'fetches':5500})
        report = self.run_report(); self.assertEqual(self.fetcher.calls, [])
        self.assertTrue(report['budgetDenied']); self.replay(report)
        self.store.compare_and_swap('budget-2026-10-25', self.store.read('heads/budget-2026-10-25.json'), None)
        context = self.budget(); original = context.reserve_fetch
        def reserve_then_cancel():
            result = original(); context.deadline = 0; return result
        with patch.object(context, 'reserve_fetch', side_effect=reserve_then_cancel): report = self.run_report(budget=context)
        self.assertEqual(self.fetcher.calls, []); self.assertEqual(context.reservations, 1)
        self.assertFalse(report['captureComplete']); self.replay(report)
        q4.finalize_report(self.contract,self.store,self.path.read_bytes(),report,context)
        self.assertEqual(len(report['completionDenials']),2)

    def test_midnight_deadline_and_cancellation_in_flight_deny_completion(self):
        for mode in ('midnight','deadline','cancel'):
            self.clock = Clock(); context = self.budget()
            def callback(fetcher, source, url):
                if len(fetcher.calls) == 6:
                    if mode == 'midnight': self.clock.wall='2026-10-26T00:00:00Z'
                    elif mode == 'deadline': self.clock.elapsed=1200
                    else: context.deadline=0
            report=self.run_report(CaptureFetcher(self,callback=callback),context)
            self.assertEqual(len(self.fetcher.calls),6); self.assertFalse(report['executionCompleted'])
            self.assertFalse(report['captureComplete']); self.assertTrue(report['budgetDenied']); self.replay(report)

    def test_rollover_between_last_guard_and_request_marker_keeps_charged_denial(self):
        context=self.budget();calls=[]
        def crossing_clock():
            calls.append(None)
            return NOW if len(calls)<=3 else '2026-10-26T00:00:00Z'
        context.clock=crossing_clock
        report=self.run_report(budget=context)
        self.assertEqual(self.fetcher.calls,[]);self.assertEqual(context.reservations,1)
        self.assertIsNone(report['requests'][0]['requestedAt'])
        self.assertEqual(report['requests'][0]['denial'],'SOURCE_PROBE_UTC_DAY_CHANGED')
        self.assertFalse(report['executionCompleted']);self.assertFalse(report['captureComplete']);self.replay(report)
        final=q4.finalize_report(self.contract,self.store,self.path.read_bytes(),report,context)
        self.assertEqual(final['checkedAt'],'2026-10-26T00:00:00Z')
        self.assertEqual(len(final['completionDenials']),2);self.replay(final)

    def test_cancellation_and_partial_quota_stop_before_a_third_request(self):
        context=self.budget()
        def callback(fetcher,source,url):
            if len(fetcher.calls)==2:context.deadline=0
        report=self.run_report(CaptureFetcher(self,callback=callback),context)
        self.assertEqual(len(self.fetcher.calls),2);self.assertEqual(context.reservations,2)
        self.assertTrue(report['budgetDenied']);self.replay(report)
        self.store.compare_and_swap('budget-2026-10-25',self.store.read('heads/budget-2026-10-25.json'),
                                    {'calls':72,'documents':33,'fetches':5498})
        report=self.run_report()
        self.assertEqual(len(self.fetcher.calls),2)
        self.assertEqual(report['reservationContext']['currentBudget'],{'calls':72,'documents':33,'fetches':5500})
        self.assertFalse(report['captureComplete']);self.replay(report)

    def test_existing_fetcher_retains_opted_in_unexpected_status_without_changing_default(self):
        import fetcher as transport
        from io import BytesIO
        class Response(BytesIO):
            def __init__(self,url,status):
                super().__init__(b'window.syntheticCapture = function () { return 1; };')
                self.url,self.status,self.headers=url,status,{'Content-Type':'text/javascript; charset=utf-8'}
        class Opener:
            def __init__(self,status):self.status=status
            def open(_,request,timeout):return Response(request.full_url,_.status)
        source=next(s for s in self.contract['sources'] if s['id']==q4.BINDINGS[0][0])
        url=self.plan['sources'][0]['targets'][0]
        with patch.object(transport,'safe_url',side_effect=lambda u,*a,**k:u),\
             patch.object(transport.urllib.request,'build_opener',return_value=Opener(203)):
            with self.assertRaisesRegex(ValueError,'Unexpected source response status'):
                transport.Fetcher(self.store).fetch(source,url)
            observed=transport.Fetcher(self.store,unexpected_status_diagnostics=True,redirect_diagnostics=True).fetch(source,url)
        self.assertEqual(observed['httpStatus'],203);self.assertEqual(observed['finalUrl'],url)
        self.assertEqual(observed['contentType'],'text/javascript; charset=utf-8')
        self.assertEqual(self.store.get(observed['body']),b'window.syntheticCapture = function () { return 1; };')

    def test_bound_budget_and_tampered_report_cannot_claim_capture_or_credit(self):
        with self.assertRaisesRegex(ValueError,'BOUND_BUDGET_REQUIRED'):
            q4.execute(self.contract,self.store,CaptureFetcher(self),None,{})
        report=self.run_report()
        mutations=[lambda r:r.update(qualified=True),lambda r:r.update(qualifiedSources=1),
                   lambda r:r.update(facts=['fabricated']),lambda r:r.update(capturedControllers=True),
                   lambda r:r.update(extra=True),lambda r:r['requests'][0].update(url=r['requests'][1]['url']),
                   lambda r:r['requests'][0]['reservation'].update(chargedFetchCount=99),
                   lambda r:r['reservationContext'].update(initialBudget=[]),
                   lambda r:r['results'][0].update(contentType='text/html'),
                   lambda r:r['requests'].pop(),lambda r:r['requests'].append(copy.deepcopy(r['requests'][-1]))]
        for mutate in mutations:
            changed=copy.deepcopy(report); mutate(changed)
            with self.subTest(mutate=mutate),self.assertRaises((ValueError,KeyError)): self.replay(changed)

    def test_failed_transport_attempt_times_and_completion_cannot_be_forged(self):
        report=self.run_report(CaptureFetcher(self,response=OSError('fictional failure')))
        mutations=[lambda r:r['requests'][0].update(requestedAt=None),
                   lambda r:r['requests'][0].update(requestedAt='2026-10-24T12:00:00Z'),
                   lambda r:r['requests'][0].update(requestedAt='2026-10-25T13:00:00Z'),
                   lambda r:r.update(checkedAt='2026-10-24T12:00:00Z')]
        for mutate in mutations:
            changed=copy.deepcopy(report);mutate(changed)
            with self.subTest(mutate=mutate),self.assertRaises(ValueError):self.replay(changed)

    def test_leased_caller_routes_q4_only_after_preflight_and_escrow(self):
        import collect
        (self.root/'contracts').mkdir(); (self.root/'contracts/source-qualification-probes.json').write_bytes(self.path.read_bytes())
        acknowledged=[]; factory=CaptureFetcher(self)
        def transport(*args,**kwargs):
            self.assertEqual(acknowledged,['escrow']); self.assertTrue(kwargs['unexpected_status_diagnostics'])
            self.assertTrue(kwargs['redirect_diagnostics']); self.assertEqual(kwargs['max_bytes'],q4.MAX_BODY_BYTES)
            return factory
        def context(*args,**kwargs): return self.budget()
        env={'GITHUB_RUN_ID':'999','GITHUB_RUN_ATTEMPT':'1','GITHUB_EVENT_NAME':'workflow_dispatch','GITHUB_REF':'refs/heads/main'}
        with patch.object(collect,'REPO',self.root),patch.object(collect,'PersistentProbeBudget',side_effect=context),\
             patch.object(collect,'Fetcher',side_effect=transport),patch.object(collect,'probe_sources',side_effect=AssertionError('generic fanout')),\
             patch.object(collect.session_runtime,'require_source_probe_context'),\
             patch.object(collect.session_runtime,'checkpoint',return_value={'archive':{'synthetic':True}}),\
             patch.object(collect,'escrow_budgets',side_effect=lambda *a:acknowledged.append('escrow')),patch.dict(os.environ,env):
            result=collect.execute_source_probe(self.root,self.store,{'checkpointProfile':'source_probe','sessionId':'fictional','appRevision':'a'*40},self.contract,1200)
        self.assertEqual(len(factory.calls),6);self.assertEqual(result['facts'],[]);self.assertEqual(result['qualifiedSources'],0)
        self.assertTrue(result['diagnostic']['captureComplete'])


@unittest.skipUnless((ARCHIVE/'archive-manifest.json').exists(),'Requires frozen authenticated seven-source archive')
class ActualQ4ParentTests(unittest.TestCase):
    def setUp(self):
        self.store=ReadOnlyArchive(ARCHIVE);self.addCleanup(self.store.assert_unchanged,self)
        self.contract=json.loads((ROOT/('contracts/html-qualification-seeds/' + '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db' + '/contracts__' + '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db' + '.json')).read_bytes());self.raw=PLAN.read_bytes()

    def test_actual_charged_parent_proofs_and_six_exact_disclosures_read_only(self):
        with patch.object(LocalStore,'__init__',side_effect=AssertionError('must not initialize frozen archive')):
            plan=q4.validate_plan(self.contract,self.store,self.raw)
        self.assertEqual(len(plan['targets']),6);self.assertEqual(len(self.store.touched),8)
        self.assertEqual({r['sourceId'] for r in plan['targets']},{b[0] for b in q4.BINDINGS})

    def test_actual_original_plan_row_body_time_source_and_charge_proofs_reject_mutations(self):
        original=json.loads(self.raw)
        mutations=[lambda p:p.update(priorTargetSha256='0'*64),lambda p:p.update(priorPlanRawSha256='0'*64),
                   lambda p:p.update(priorPlanCanonicalSha256='0'*64),lambda p:p.update(priorPlanReference={**p['priorPlanReference'],'bytes':1}),
                   lambda p:p.update(observation={**p['observation'],'sha256':'0'*64}),lambda p:p.update(fetchedAt=NOW),
                   lambda p:p.update(body={**p['body'],'sha256':'0'*64}),lambda p:p.update(priorTargetIndex=5),
                   lambda p:p.update(priorTargetSha256=True),lambda p:p.update(historicalPolicyBridge={})]
        for mutate in mutations:
            plan=copy.deepcopy(original);mutate(plan['sources'][0]['parentProof'])
            with self.subTest(mutate=mutate),self.assertRaises((ValueError,KeyError)):
                q4.validate_plan(self.contract,self.store,canonical(plan))
        plan=copy.deepcopy(original);plan['sources'][0]['parentProof']=copy.deepcopy(plan['sources'][1]['parentProof'])
        with self.assertRaises(ValueError):q4.validate_plan(self.contract,self.store,canonical(plan))
        parent=self.store.get(q4.PARENT_RECORD)
        class ChangedArchive:
            def get(_,ref): return parent+b' ' if ref==q4.PARENT_RECORD else self.store.get(ref)
        with self.assertRaisesRegex(ValueError,'REFERENCE_BYTES_DIFFER'):
            q4.validate_plan(self.contract,ChangedArchive(),self.raw)
        prior=original['sources'][0]['parentProof']['priorPlanReference']
        class ChangedPriorPlan:
            def get(_,ref):return self.store.get(ref)+b' ' if ref==prior else self.store.get(ref)
        with self.assertRaises(ValueError):q4.validate_plan(self.contract,ChangedPriorPlan(),self.raw)


if __name__=='__main__':unittest.main()
