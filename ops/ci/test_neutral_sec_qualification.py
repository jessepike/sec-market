"""Fictional neutral SEC diagnostics. No real requests, registration or semantic work."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'web/scripts/pipeline'))
from contracts import canonical, digest
from regulatory import TABLE_FIELDS
from storage import LocalStore
from onboarding import PersistentProbeBudget
import neutral_sec_qualification as sec

NOW = '2026-10-24T10:00:00Z'


class Clock:
    def __init__(self): self.wall, self.elapsed = NOW, 0
    def now(self): return self.wall
    def monotonic(self): return self.elapsed


def table(cik, count=1):
    rows = []
    for n in range(count):
        rows.append({'accessionNumber': f'{int(cik):010d}-26-{n+1:06d}', 'filingDate':'2026-10-20',
            'reportDate':'', 'acceptanceDateTime':'2026-10-20T12:00:00Z', 'act':'34','form':'8-K',
            'fileNumber':'001-123','filmNumber':'26123','items':'5.02','size':100,'isXBRL':0,
            'isInlineXBRL':0,'primaryDocument':f'fixture-{n}.htm','primaryDocDescription':'Fictional primary'})
    return {key:[r[key] for r in rows] for key in TABLE_FIELDS}


class Fetcher:
    def __init__(self, fixture, *, fail=None, count=1, callback=None, older=False):
        self.f, self.calls, self.fail, self.count, self.callback, self.older = fixture, [], fail, count, callback, older
    def fetch(self, source, url):
        self.calls.append((source['id'],url))
        if self.callback: self.callback(source,url)
        result = {'requestedUrl':url,'finalUrl':url,'fetchedAt':self.f.clock.now(),
                  'status':'fetched','httpStatus':200,'contentType':'text/html'}
        if self.fail and self.fail in url:
            return {**result,'status':'blocked','httpStatus':403,'errorCode':'HTTP_403'}
        if source['kind'] == 'sec_index':
            issuer = source['regulatoryIssuer']; cik = issuer['cik']
            rows = table(cik,self.count)
            if '-submissions-' in url:
                body = canonical(rows)
            else:
                body = canonical({'cik':int(cik),'name':issuer['legalName'], 'filings':{
                    'recent':table(cik,0) if self.older else rows,
                    'files':[{'name':f'CIK{cik}-submissions-001.json','filingCount':self.count,
                              'filingFrom':'2026-10-20','filingTo':'2026-10-20'}] if self.older else []}})
            result['contentType'] = 'application/json'
        else:
            body = ('<html><body>' + ('Readable fictional primary filing. '*15) + '</body></html>').encode()
        result['body'] = self.f.store.put(body)
        return result


class NeutralSecQualificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(Path(self.temp.name)/'state'); self.clock = Clock()
        self.policy = json.loads((ROOT/'contracts/market.json').read_bytes())
        reviewed = json.loads((ROOT/'docs/active/daily-pipeline/accuracy/four-neutral-regulatory-bindings-spec-2026-10-24.json').read_bytes())
        self.source_rows = reviewed['proposedSources']
        ids = {s['id'] for s in self.source_rows}
        self.policy['sources'] = [s for s in self.policy['sources'] if s['id'] not in ids] + copy.deepcopy(self.source_rows)
        for supplier in self.policy['suppliers']:
            if supplier['id'] in {b[0] for b in sec.BINDINGS}:
                supplier['sourceIds'] = [s for s in supplier['sourceIds'] if s not in ids] + [supplier['id']+':sec_index',supplier['id']+':sec_documents']
        raw_policy = canonical(self.policy); key = 'contracts/'+digest(self.policy)+'.json'
        self.store.write_once(key,raw_policy)
        policy_ref = {'key':key,'sha256':digest(raw_policy),'bytes':len(raw_policy)}
        proposal = {'archive':{'manifestSha256':sec.RELATIONSHIP_ARCHIVE_MANIFEST},
                    'proposedSources':copy.deepcopy(self.source_rows),'primaryParentRelationshipProofs':[]}
        for sid,cik,name,proof_id in sec.BINDINGS:
            phrase = 'Exposure Management' if sid=='crwd-exposure' else 'Cortex XSIAM'
            markup = f'<ix:nonNumeric name="dei:EntityCentralIndexKey">{cik}</ix:nonNumeric>'
            text = phrase + ' belongs to the parent issuer. ' + 'Original relationship evidence. '*12
            body = self.store.put(('<html><body>'+markup+'<p>'+text+'</p></body></html>').encode())
            url = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/fictional-parent.htm'
            observed = {'sourceId':sid+':original-parent','requestedUrl':url,'finalUrl':url,
                'observationId':digest(sid),'fetchedAt':'2026-10-20T12:00:00Z','status':'fetched','body':body,'httpStatus':200}
            raw = canonical(observed); key = 'observations/'+observed['observationId']+'.json'
            self.store.write_once(key,raw)
            proposal['primaryParentRelationshipProofs'].append({'proofId':proof_id,
                **{k:observed[k] for k in ('sourceId','requestedUrl','finalUrl','observationId','fetchedAt','status','body')},
                'observationActualReference':{'key':'state/'+key,'sha256':digest(raw),'bytes':len(raw)},
                'submissionsIdentity':{'cik':cik,'legalName':name,'initialIndexBody':self.store.put({'cik':int(cik),'name':name})},
                'inlineXbrlIdentity':{'EntityCentralIndexKey':{'value':cik,'rawMarkup':markup}},
                'relationshipPhrase':phrase,'excerpts':[{'text':text.strip()}]})
        proposal['proposalSha256'] = digest(proposal)
        raw = canonical(proposal); proposal_ref = self.store.put(raw)
        for name,value in [('PROPOSAL_SHA256',digest(raw)),('PROPOSAL_BYTES',len(raw)),('PROPOSAL_SEAL',proposal['proposalSha256'])]:
            p = patch.object(sec,name,value); p.start(); self.addCleanup(p.stop)
        pairs = []
        for sid,cik,name,proof_id in sec.BINDINGS:
            sources = {s['id']:s for s in self.source_rows}
            pairs.append({'supplierId':sid,'indexSourceId':sid+':sec_index',
                'indexSourceSha256':digest(sources[sid+':sec_index']), 'documentsSourceId':sid+':sec_documents',
                'documentsSourceSha256':digest(sources[sid+':sec_documents']),
                'regulatoryIssuer':{'cik':cik,'legalName':name,'relationship':'parent'},
                'relationshipProof':{'proposal':proposal_ref,'proofId':proof_id}})
        self.plan = {'schemaVersion':2,'operation':sec.OPERATION,'marketSha256':digest(self.policy),
            'originalContract':policy_ref,'maxRequests':280,'maxIndexPagesPerPair':40,
            'maxPrimaryBodiesPerPair':100,'lookbackDays':365,'pairs':pairs}
        self.path = Path(self.temp.name)/'plan.json'
        self.path.write_bytes(canonical(self.plan))

    def budget(self):
        return PersistentProbeBudget(self.store,self.policy,clock=self.clock.now,monotonic=self.clock.monotonic)

    def run_report(self, **kwargs):
        normalized = sec.validate_plan(self.policy,self.store,self.path.read_bytes(),self.path)
        self.fetcher = Fetcher(self,**kwargs)
        return sec.execute(self.policy,self.store,self.fetcher,self.budget(),normalized)

    def verify(self,report):
        return sec.verify_report(self.policy,self.store,self.path.read_bytes(),report)

    def test_exact_two_pairs_zero_fanout_and_semantic_budget_unchanged(self):
        seed={'calls':80,'documents':40,'fetches':641,'unrelated':'preserve'}
        self.store.compare_and_swap('budget-2026-10-24',None,seed)
        report=self.run_report()
        self.assertEqual(len(self.fetcher.calls),4)
        self.assertEqual([s for s,_ in self.fetcher.calls],[b[0]+suffix for b in sec.BINDINGS for suffix in (':sec_index',':sec_documents')])
        self.assertTrue(self.verify(report)['evidenceComplete'])
        self.assertFalse(report['qualified']); self.assertFalse(report['coverageCredit'])
        self.assertEqual(report['reservationContext']['currentBudget'],{**seed,'fetches':645})
        self.assertTrue(all(report[k]==0 for k in sec.ZERO_FIELDS))

    def test_strict_closed_plan_rejects_before_transport(self):
        for field,value in [('maxRequests',281),('maxIndexPagesPerPair',True),('schemaVersion',True),
                            ('operation','disabled_qualification_probe'),('marketSha256','f'*64),('pairs',[])]:
            plan=copy.deepcopy(self.plan); plan[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError): sec.validate_plan(self.policy,self.store,canonical(plan))

    def test_second_pair_bad_policy_or_relationship_rejects_entire_preflight(self):
        for field,value in [('documentsSourceSha256','f'*64),('supplierId','crwd-exposure'),('regulatoryIssuer',{'cik':'0001535527'})]:
            plan=copy.deepcopy(self.plan); plan['pairs'][1][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError): sec.validate_plan(self.policy,self.store,canonical(plan))
        plan=copy.deepcopy(self.plan);plan['pairs'][1]['relationshipProof']['proofId']='crwd-falcon-10k'
        with self.assertRaises(ValueError):sec.validate_plan(self.policy,self.store,canonical(plan))

    def test_current_plan_change_rejects_without_fetch(self):
        normalized=sec.validate_plan(self.policy,self.store,self.path.read_bytes(),self.path)
        self.path.write_bytes(b'{}'); fetcher=Fetcher(self)
        with self.assertRaisesRegex(ValueError,'CURRENT_PLAN_CHANGED'):sec.execute(self.policy,self.store,fetcher,self.budget(),normalized)
        self.assertEqual(fetcher.calls,[])

    def test_original_relationship_body_tamper_fails_preflight_without_transport(self):
        proposal=json.loads(self.store.get(self.plan['pairs'][1]['relationshipProof']['proposal']))
        body=proposal['primaryParentRelationshipProofs'][1]['body']
        (self.store.root/body['key']).write_bytes(b'Changed retained primary body')
        fetcher=Fetcher(self)
        with self.assertRaisesRegex(ValueError,'integrity verification'):
            sec.validate_plan(self.policy,self.store,self.path.read_bytes())
        self.assertEqual(fetcher.calls,[])

    def test_rehashed_verified_declaration_cannot_bypass_candidate_preflight(self):
        policy=copy.deepcopy(self.policy);plan=copy.deepcopy(self.plan)
        source=next(s for s in policy['sources'] if s['id']=='panw-xsiam:sec_documents')
        source['registration']='verified'
        raw=canonical(policy);key='contracts/'+digest(policy)+'.json';self.store.write_once(key,raw)
        plan['marketSha256']=digest(policy)
        plan['originalContract']={'key':key,'sha256':digest(raw),'bytes':len(raw)}
        plan['pairs'][1]['documentsSourceSha256']=digest(source)
        with self.assertRaisesRegex(ValueError,'EXACT_CANDIDATE_DECLARATION_DIFFERS'):
            sec.validate_plan(policy,self.store,canonical(plan))

    def test_literal_older_pages_under_index_id_and_exact_selected_bodies(self):
        report=self.run_report(older=True)
        self.assertEqual(len(self.fetcher.calls),6)
        self.assertTrue(self.verify(report)['evidenceComplete'])
        self.assertTrue(all('/submissions/' in url for sid,url in self.fetcher.calls if sid.endswith(':sec_index')))

    def test_body_failure_lifecycle_complete_but_readiness_false(self):
        report=self.run_report(fail='fixture-0')
        self.assertTrue(report['executionCompleted']);self.assertFalse(report['budgetDenied'])
        result=self.verify(report)
        self.assertFalse(result['evidenceComplete'])
        self.assertTrue(all(p['selectedCount']==1 and len(p['pendingPrimaryUrls'])==1 for p in result['pairs']))

    def test_root_failure_preserves_four_rows_and_zero_selection_authority(self):
        report=self.run_report(fail='CIK0001535527')
        self.assertEqual(len(report['sources']),4)
        self.assertFalse(self.verify(report)['pairs'][0]['indexComplete'])
        self.assertNotIn('selectedDocuments',report['sources'][1]['secDocumentsDiagnostic'])

    def test_body_guard_keeps_full_inventory_without_truncated_requests(self):
        report=self.run_report(count=101)
        self.assertEqual(len(self.fetcher.calls),2)
        self.assertFalse(self.verify(report)['evidenceComplete'])
        self.assertTrue(all(p['selectedCount']==101 and len(p['pendingPrimaryUrls'])==101 for p in report['pairReadiness']))

    def test_full_shared_budget_performs_no_requests(self):
        self.store.compare_and_swap('budget-2026-10-24',None,{'calls':80,'documents':40,'fetches':5500})
        report=self.run_report(); self.assertEqual(self.fetcher.calls,[])
        self.assertTrue(report['budgetDenied']);self.assertFalse(self.verify(report)['evidenceComplete'])

    def test_final_inflight_day_change_or_deadline_cannot_complete(self):
        def expire(source,url):
            if source['id']=='panw-xsiam:sec_documents':self.clock.elapsed=1201
        report=self.run_report(callback=expire)
        self.assertTrue(report['budgetDenied']);self.assertFalse(self.verify(report)['evidenceComplete'])

    def test_utc_day_change_after_response_is_held_without_new_day_reservation(self):
        def rollover(source,url):
            if source['id']=='crwd-exposure:sec_documents':self.clock.wall='2026-10-25T00:00:00Z'
        report=self.run_report(callback=rollover)
        self.assertTrue(report['budgetDenied']);self.assertFalse(self.verify(report)['evidenceComplete'])
        self.assertIsNone(self.store.read('heads/budget-2026-10-25.json'))

    def advancing_final_capture(self, *, rollover=False):
        from onboarding import _probe_sec_candidate_pair
        calls=0
        def pair(*args,**kwargs):
            nonlocal calls
            result=_probe_sec_candidate_pair(*args,**kwargs)
            calls+=1
            if calls==2:
                budget=args[4].base
                reads=0
                def advancing_clock():
                    nonlocal reads
                    reads+=1
                    if reads>=2:
                        if rollover:self.clock.wall='2026-10-25T00:00:00Z'
                        else:self.clock.elapsed=1201
                    return self.clock.wall
                budget.clock=advancing_clock
            return result
        with patch('onboarding._probe_sec_candidate_pair',side_effect=pair):
            return self.run_report()

    def test_deadline_crossed_during_final_timestamp_capture_returns_replayable_partial(self):
        report=self.advancing_final_capture()
        self.assertEqual(len(self.fetcher.calls),4)
        self.assertEqual(report['checkedAt'],NOW)
        self.assertEqual(report['completionDenial'],'SOURCE_PROBE_DEADLINE_EXCEEDED')
        self.assertFalse(report['executionCompleted']);self.assertTrue(report['budgetDenied'])
        self.assertEqual(report['reservationContext']['probeFetchReservations'],4)
        self.assertFalse(self.verify(report)['evidenceComplete'])

    def test_utc_day_crossed_during_final_timestamp_capture_returns_replayable_partial(self):
        report=self.advancing_final_capture(rollover=True)
        self.assertEqual(len(self.fetcher.calls),4)
        self.assertEqual(report['checkedAt'],'2026-10-25T00:00:00Z')
        self.assertEqual(report['completionDenial'],'SOURCE_PROBE_UTC_DAY_CHANGED')
        self.assertFalse(report['executionCompleted']);self.assertTrue(report['budgetDenied'])
        self.assertEqual(report['reservationContext']['probeFetchReservations'],4)
        self.assertFalse(self.verify(report)['evidenceComplete'])
        self.assertIsNone(self.store.read('heads/budget-2026-10-25.json'))

    def test_operation_bound_denies_281st_logical_reservation_before_charge(self):
        from onboarding import ProbeReservationDenied
        budget=self.budget();limited=sec._OperationBudget(budget)
        for _ in range(280):limited.reserve_fetch()
        before=self.store.read('heads/budget-2026-10-24.json')
        with self.assertRaisesRegex(ProbeReservationDenied,'OPERATION_LIMIT'):limited.reserve_fetch()
        self.assertEqual(self.store.read('heads/budget-2026-10-24.json'),before)
        self.assertEqual(budget.reservations,280)

    def test_complete_maximum_two_pair_traversal_uses_exactly_280_requests(self):
        fixture=self
        class MaximumFetcher(Fetcher):
            def fetch(self,source,url):
                if source['kind'] != 'sec_index' or '-submissions-' in url:
                    return super().fetch(source,url)
                self.calls.append((source['id'],url))
                cik=source['regulatoryIssuer']['cik']
                body=canonical({'cik':int(cik),'name':source['regulatoryIssuer']['legalName'], 'filings':{
                    'recent':table(cik,0),'files':[{'name':f'CIK{cik}-submissions-{i:03d}.json',
                        'filingCount':100,'filingFrom':'2026-10-20','filingTo':'2026-10-20'} for i in range(1,40)]}})
                return {'status':'fetched','httpStatus':200,'requestedUrl':url,'finalUrl':url,'fetchedAt':NOW,
                        'contentType':'application/json','body':fixture.store.put(body)}
        fetcher=MaximumFetcher(self,count=100)
        plan=sec.validate_plan(self.policy,self.store,self.path.read_bytes(),self.path)
        report=sec.execute(self.policy,self.store,fetcher,self.budget(),plan)
        self.assertEqual(len(fetcher.calls),280)
        self.assertTrue(self.verify(report)['evidenceComplete'])

    def test_rehashed_wrong_source_wrapper_and_extra_unobserved_request_reject(self):
        report=self.run_report()
        bad=copy.deepcopy(report)
        observed=json.loads(self.store.get(bad['sources'][0]['observations'][0]))
        observed['sourceId']='crwd:sec_submissions'
        bad['sources'][0]['observations'][0]=self.store.put(observed)
        with self.assertRaisesRegex(ValueError,'SOURCE_OR_URL_DIFFERS'):self.verify(bad)
        bad=copy.deepcopy(report)
        bad['sources'][1]['fetchReservations'].append({**bad['sources'][1]['fetchReservations'][0],
                                                       'url':'https://www.sec.gov/unlisted.htm'})
        with self.assertRaisesRegex(ValueError,'RESERVATION_SEQUENCE'):self.verify(bad)

    def test_replay_rejects_issuer_readiness_counter_charge_text_and_selection_tamper(self):
        report=self.run_report()
        mutations=[lambda r:r.__setitem__('modelCalls',1),lambda r:r['sources'][0].__setitem__('qualified',True),
            lambda r:r['pairReadiness'][0].__setitem__('evidenceComplete',False),
            lambda r:r['sources'][0]['fetchReservations'][0].__setitem__('chargedFetchCount',True),
            lambda r:r['sources'][1]['secDocumentsDiagnostic'].__setitem__('selectedDocuments',[]),
            lambda r:r['sources'][1]['secDocumentsDiagnostic']['primaryDocuments'][0].__setitem__('readableText',self.store.put(b'forged'))]
        for mutate in mutations:
            bad=copy.deepcopy(report);mutate(bad)
            with self.subTest(mutate=mutate),self.assertRaises(ValueError):self.verify(bad)

    def test_historical_replay_never_consults_replaced_live_plan(self):
        report=self.run_report(); raw=self.path.read_bytes()
        record={'schemaVersion':1,'checkpointProfile':'source_probe','contractSha256':digest(self.policy),
            'githubRunId':'12345','githubRunAttempt':1,'githubEventName':'workflow_dispatch','githubRef':'refs/heads/main',
            'appRevision':'a'*40,'apiFallback':False,'modelCalls':0,'sourceChecksCredited':0,'qualifiedSources':0,
            'semanticAdmission':False,'coverageCredit':False,'publication':{'published':False,'reason':'SOURCE_PROBE_DIAGNOSTIC_ONLY'},
            'diagnostic':report,'executionCompleted':True,'outcome':'completed_diagnostic'}
        raw_record=canonical(record);key='ci/source-probe-runs/12345-1.json';self.store.write_once(key,raw_record)
        ref={'key':key,'sha256':digest(raw_record),'bytes':len(raw_record)}
        self.path.write_bytes(b'{}')
        with patch('socket.socket.connect',side_effect=AssertionError('network forbidden')), \
             patch.object(self.store,'put',side_effect=AssertionError('writes forbidden')), \
             patch.object(self.store,'write_once',side_effect=AssertionError('writes forbidden')):
            replay=sec.replay_diagnostic(self.policy,self.store,ref,report['planReference'])
        self.assertTrue(replay['readiness']['evidenceComplete'])
        self.assertEqual(replay['report']['checkedAt'],NOW)
        self.assertEqual(sec.validate_plan(self.policy,self.store,raw)['rawSha256'],digest(raw))
        for index,(field,value) in enumerate([('modelCalls',1),('githubRef','refs/heads/preview'),
                            ('appRevision','not-a-code-pin'),('publication',{'published':True})]):
            bad=copy.deepcopy(record);bad[field]=value
            # Each candidate uses a separate temporary object address, preserving
            # existing immutable records while testing the run envelope.
            bad['githubRunId']=str(20000+index);key=f"ci/source-probe-runs/{bad['githubRunId']}-1.json"
            data=canonical(bad);self.store.write_once(key,data)
            ref={'key':key,'sha256':digest(data),'bytes':len(data)}
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'HISTORICAL_RUN_ENVELOPE'):
                sec.replay_diagnostic(self.policy,self.store,ref,report['planReference'])


class ArchivedRelationshipPreflightTests(unittest.TestCase):
    def test_reviewed_actual_parent_bytes_and_original_statuses_preflight_read_only(self):
        proposal_path=ROOT/'docs/active/daily-pipeline/accuracy/four-neutral-regulatory-bindings-spec-2026-10-24.json'
        raw_proposal=proposal_path.read_bytes();p=json.loads(raw_proposal)
        archive=Path(p['archive']['root'])/'state'
        if not archive.is_dir():self.skipTest('Authenticated local archive unavailable; no network fallback')
        def seals():
            result={}
            for key,pin in p['archive']['selectedEntries'].items():
                file=archive.parent/key;raw=file.read_bytes()
                self.assertEqual((digest(raw),len(raw),file.stat().st_mtime_ns),
                                 (pin['sha256'],pin['bytes'],pin['mtimeNs']))
                result[key]=(digest(raw),len(raw),file.stat().st_mtime_ns)
            return result
        before=seals()
        policy=json.loads((ROOT/'contracts/market.json').read_bytes())
        ids={s['id'] for s in p['proposedSources']}
        policy['sources']=[s for s in policy['sources'] if s['id'] not in ids]+copy.deepcopy(p['proposedSources'])
        for supplier in policy['suppliers']:
            if supplier['id'] in p['subjectSourceIdAppends']:
                supplier['sourceIds']=[s for s in supplier['sourceIds'] if s not in ids]+p['subjectSourceIdAppends'][supplier['id']]
        raw_policy=canonical(policy);policy_key='contracts/'+digest(policy)+'.json'
        overlay={policy_key:raw_policy,'objects/'+digest(raw_proposal):raw_proposal}
        class ReadOnlyStore:
            def get(self,ref):return overlay[ref['key']] if ref['key'] in overlay else (archive/ref['key']).read_bytes()
        proposal_ref={'key':'objects/'+digest(raw_proposal),'sha256':digest(raw_proposal),'bytes':len(raw_proposal)}
        sources={s['id']:s for s in p['proposedSources']}
        pairs=[{'supplierId':sid,'indexSourceId':sid+':sec_index','indexSourceSha256':digest(sources[sid+':sec_index']),
            'documentsSourceId':sid+':sec_documents','documentsSourceSha256':digest(sources[sid+':sec_documents']),
            'regulatoryIssuer':{'cik':cik,'legalName':name,'relationship':'parent'},
            'relationshipProof':{'proposal':proposal_ref,'proofId':proof}} for sid,cik,name,proof in sec.BINDINGS]
        plan={'schemaVersion':2,'operation':sec.OPERATION,'marketSha256':digest(policy),
            'originalContract':{'key':policy_key,'sha256':digest(raw_policy),'bytes':len(raw_policy)},
            'maxRequests':280,'maxIndexPagesPerPair':40,'maxPrimaryBodiesPerPair':100,'lookbackDays':365,'pairs':pairs}
        with patch('socket.socket.connect',side_effect=AssertionError('network forbidden')):
            validated=sec.validate_plan(policy,ReadOnlyStore(),canonical(plan))
            from onboarding import _validate_sec_candidate_index
            from regulatory import filing_document_inventory
            selected=[]
            for pair,proof in zip(validated['pairs'],p['primaryParentRelationshipProofs']):
                root=json.loads(ReadOnlyStore().get(proof['submissionsIdentity']['initialIndexBody']))
                pages=[{'url':pair['index']['url'],'document':root}]
                checked=_validate_sec_candidate_index(pair['index'],pages,'2026-10-23T11:34:15.010723Z')
                selected.append(len(filing_document_inventory(pair['documents'],pages,checked['windowStart'],checked['windowEnd'])))
        self.assertEqual(len(validated['pairs']),2)
        self.assertTrue(all(pair['index']['registration']=='candidate' for pair in validated['pairs']))
        self.assertEqual(selected,[12,17])
        self.assertEqual(seals(),before)


if __name__=='__main__':unittest.main()
