import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'web/scripts/pipeline'))
from contracts import digest
from snapshot import build_snapshot, collector_continuity
from storage import LocalStore
from validation import REVIEW_CHECKS, verify_statement
import gate


class GateContinuityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store=LocalStore(self.temp.name)
        self.supplier={'id':'example','name':'Example Security','aliases':[],'kind':'private','requiredCategories':['leadership']}
        self.source={'id':'example:official','supplierId':'example','family':'official_announcements',
                     'allowedHosts':['example.invalid']}
        self.contract={'suppliers':[self.supplier],'sources':[self.source],'schedule':{'overdueHours':30},
                       'publication':{'enabled':True}}
        self.coverage={'runId':'actual-run','contractSha256':digest(self.contract),'inventorySha256':'i',
                       'successfulTasks':0,'requiredTasks':1,'complete':False,'gapTaskIds':['task'],
                       'checkedAt':'2026-10-23T11:34:15Z','receipts':[{'completedAt':'2026-10-23T11:34:15Z'}]}
        self.plan={'runId':'actual-run','scheduledAt':'2026-10-23T05:17:00Z',
                   'tasks':[{'supplierId':'example','taskId':'task','required':True}]}
        self.observation={'observationId':'a'*64,'sourceId':'example:official','status':'fetched',
                          'requestedUrl':'https://example.invalid/news','finalUrl':'https://example.invalid/news',
                          'fetchedAt':'2026-10-22T01:15:00Z','contentType':'text/plain'}
        self.observation['body']=self.store.put(b'On 2026-03-19, Example Security announced appointment of Alice as chief executive officer.')
        self.store.write_once('observations/' + 'a'*64 + '.json',self.observation)
        self.candidate={'supplierId':'example','predicate':'leadership_change','valueText':'appointment of Alice as chief executive officer',
                        'quote':'On 2026-03-19, Example Security announced appointment of Alice as chief executive officer.',
                        'effectiveDate':'2026-03-19','amount':None,'currency':None,'qualifier':'exact','eventStatus':'announced','scope':'company'}
        self.review={'candidateSha256':digest(self.candidate),'evidenceSha256':self.observation['body']['sha256'],
                     'policySha256':'b'*64,'checks':{k:'pass' for k in REVIEW_CHECKS},'result':'accepted'}
        self.fact=verify_statement(self.candidate,self.observation,self.store,self.review,self.supplier,'b'*64)
        self.store.write_once('facts/'+self.fact['factId']+'.json',self.fact)
        fid=self.fact['factId'];eid='DAILY-'+fid
        self.event={'id':'EV-daily-'+fid,'supplierId':'example','date':'2026-03-19','type':'exec-change',
                    'text':self.candidate['valueText'],'evidenceIds':[eid],'rung':1}
        self.evidence={'id':eid,'publicationDate':'2026-03-19','excerpt':self.candidate['quote'],
                       'canonicalUrl':self.observation['finalUrl'],'interpretation':'',
                       'retrieval':{'sha256':self.observation['body']['sha256'],'fetchedAt':self.observation['fetchedAt'],
                                    'locator':self.candidate['quote']}}
        self.collector={'enabled':True,'runId':'actual-run','contractSha256':digest(self.contract),
                        'checkedAt':'2026-10-23T11:34:34Z','coverage':self.coverage,
                        'events':[self.event],'evidence':[self.evidence],'reviewQueue':[]}
        self.seal()

    def seal(self):
        self.collector['snapshotSha256']=digest({k:v for k,v in self.collector.items() if k!='snapshotSha256'})

    def held(self,index):
        candidate={**self.candidate,'effectiveDate':None,'valueText':self.candidate['valueText']+str(index)}
        review={**self.review,'candidateSha256':digest(candidate)}
        held={'candidate':candidate,'candidateSha256':digest(candidate),'supplierId':'example',
              'reason':'Fact date missing','evidence':self.observation['body'],'review':self.store.put(review),
              'policySha256':'b'*64,'sourceObservationId':self.observation['observationId']}
        ref=self.store.put(held)
        return {'factId':digest(candidate),'supplierId':'example','reason':'Fact date missing','receiptSha256':ref['sha256']}

    def build(self,previous,continuity,references=None):
        with patch('snapshot.reconcile',return_value=self.coverage),patch('snapshot.inventory',return_value=[]), \
             patch('snapshot.eligible_fact_references',return_value=references or []),patch('snapshot.verified_partial_document_facts',return_value=[]):
            return build_snapshot(self.contract,self.plan,self.coverage,self.store,'2026-10-23T12:00:00Z',
                                  previous=previous,continuity=continuity)

    def resolvable_hold(self, candidate=None, evidence=None):
        candidate = candidate or self.candidate
        body = evidence or self.observation['body']
        old_review = {**self.review,'candidateSha256':digest(candidate),'evidenceSha256':body['sha256']}
        held = {'candidate':candidate,'candidateSha256':digest(candidate),'supplierId':'example',
                'reason':'Earlier parser held claim','evidence':body,'review':self.store.put(old_review),
                'policySha256':'b'*64,'sourceObservationId':self.observation['observationId']}
        ref = self.store.put(held)
        return {'factId':digest(candidate),'supplierId':'example','reason':held['reason'],'receiptSha256':ref['sha256']}

    def accepted_reference(self):
        review = {**self.review,'policySha256':digest(self.contract)}
        return self.store.put(verify_statement(self.candidate,self.observation,self.store,review,
                                               self.supplier,digest(self.contract)))

    def test_exact_current_acceptance_resolves_only_raw_hold_and_retains_proof(self):
        held = self.resolvable_hold()
        unrelated = self.held(1)
        primary = {'factId':self.fact['factId'],'supplierId':'example','reason':'PRIMARY_SOURCE_REQUIRED'}
        conflict = {**primary,'reason':'CONFLICTING_SAME_DATE_FIELD'}
        snapshot = self.build({'enabled':True,'reviewQueue':[held,unrelated,primary,conflict]},None,
                              [self.accepted_reference()])
        self.assertEqual(snapshot['reviewQueue'],[unrelated,primary,conflict])
        proof = snapshot['resolvedReviews'][0]
        self.assertEqual(proof['heldReceiptSha256'],held['receiptSha256'])
        self.assertEqual(proof['candidate'],self.candidate)
        self.assertEqual(proof['evidence'],[self.observation['body']])
        self.assertEqual(proof['originalSourceFetchedAt'],self.observation['fetchedAt'])
        self.assertEqual(proof['effectiveDate'],'2026-03-19')
        self.assertEqual(proof['resolvedAt'],'2026-10-23T12:00:00Z')
        admitted = json.loads(self.store.get(proof['admittedFact']))
        review = json.loads(self.store.get(proof['admittedReview']))
        self.assertEqual(admitted['candidateSha256'],proof['candidateSha256'])
        self.assertEqual(review['policySha256'],digest(self.contract))
        self.assertEqual(proof['resolutionSha256'],digest({k:v for k,v in proof.items() if k!='resolutionSha256'}))

    def test_different_date_quote_or_body_does_not_resolve(self):
        variants = [self.resolvable_hold({**self.candidate,'effectiveDate':'2026-03-20'}),
                    self.resolvable_hold({**self.candidate,'quote':self.candidate['quote']+' Different quote.'}),
                    self.resolvable_hold(evidence=self.store.put(b'different archived source body'))]
        for held in variants:
            with self.subTest(held=held['receiptSha256']):
                snapshot = self.build({'enabled':True,'reviewQueue':[held]},None,[self.accepted_reference()])
                self.assertEqual(snapshot['reviewQueue'],[held])
                self.assertNotIn('resolvedReviews',snapshot)

    def test_old_collector_hold_does_not_reopen_proven_resolution(self):
        held = self.resolvable_hold()
        first = self.build({'enabled':True,'reviewQueue':[held]},None,[self.accepted_reference()])
        continuity = {'reviewQueue':[held],'pendingFacts':[]}
        later = self.build(first,continuity)
        self.assertEqual(later['reviewQueue'],[])
        self.assertEqual(later['resolvedReviews'],first['resolvedReviews'])

    def test_old_policy_acceptance_keeps_exact_hold_open(self):
        held = self.resolvable_hold()
        snapshot = self.build({'enabled':True,'reviewQueue':[held]},None,[self.store.put(self.fact)])
        self.assertEqual(snapshot['reviewQueue'],[held])
        self.assertNotIn('resolvedReviews',snapshot)

    def test_forged_resolution_or_unaccepted_review_fails_closed(self):
        held = self.resolvable_hold()
        first = self.build({'enabled':True,'reviewQueue':[held]},None,[self.accepted_reference()])
        first['resolvedReviews'][0]['originalSourceFetchedAt']='2026-10-23T12:00:00Z'
        with self.assertRaisesRegex(ValueError,'RESOLUTION_RECORD_DIFFERS'):
            self.build(first,None)
        fact = json.loads(self.store.get(self.accepted_reference()))
        rejected = {**self.review,'policySha256':digest(self.contract),'result':'held'}
        fact['review'] = self.store.put(rejected)
        with self.assertRaises(ValueError):
            self.build({'enabled':True,'reviewQueue':[held]},None,[self.store.put(fact)])

    def test_actual_shaped_old_policy_unpublished_event_is_quarantined_with_exact_evidence(self):
        continuity=collector_continuity(self.collector,self.contract,self.coverage,self.store)
        snapshot=self.build({'enabled':True,'events':[],'evidence':[]},continuity)
        self.assertEqual(snapshot['events'],[])
        self.assertEqual(snapshot['evidence'],[])
        held=snapshot['pendingFacts'][0]
        self.assertEqual(held['reason'],'CURRENT_POLICY_REVIEW_REQUIRED')
        self.assertEqual(held['event'],self.event)
        self.assertEqual(held['evidence'],[self.evidence])
        self.assertEqual(held['sourceObservation']['fetchedAt'],'2026-10-22T01:15:00Z')
        self.assertEqual(held['sourceSnapshotCheckedAt'],'2026-10-23T11:34:34Z')

    def test_all_28_unresolved_holds_survive_merge_with_14_published_holds(self):
        queue=[self.held(i) for i in range(28)]
        self.collector['reviewQueue']=queue;self.seal()
        continuity=collector_continuity(self.collector,self.contract,self.coverage,self.store)
        snapshot=self.build({'enabled':True,'reviewQueue':queue[:14]},continuity)
        self.assertEqual(len(snapshot['reviewQueue']),28)
        self.assertEqual({q['receiptSha256'] for q in snapshot['reviewQueue']},{q['receiptSha256'] for q in queue})

    def test_trusted_already_published_event_and_evidence_are_not_removed_or_redated(self):
        continuity=collector_continuity(self.collector,self.contract,self.coverage,self.store)
        snapshot=self.build({'enabled':True,'events':[self.event],'evidence':[self.evidence]},continuity)
        self.assertEqual(snapshot['events'],[self.event])
        self.assertEqual(snapshot['evidence'],[self.evidence])
        self.assertEqual(snapshot['pendingFacts'],[])

    def test_tampered_snapshot_or_wrong_run_fails_closed(self):
        self.collector['events'][0]['text']='altered'
        with self.assertRaisesRegex(ValueError,'CONTINUITY_COLLECTOR_HASH_DIFFERS'):
            collector_continuity(self.collector,self.contract,self.coverage,self.store)
        self.collector['runId']='wrong';self.seal()
        with self.assertRaisesRegex(ValueError,'CONTINUITY_COLLECTOR_RUN_OR_POLICY_DIFFERS'):
            collector_continuity(self.collector,self.contract,self.coverage,self.store)

    def test_resealed_event_tamper_or_deleted_evidence_cannot_pass_source_replay(self):
        self.collector['events'][0]['text']='altered';self.seal()
        with self.assertRaisesRegex(ValueError,'CONTINUITY_EVENT_CONTENT_DIFFERS'):
            collector_continuity(self.collector,self.contract,self.coverage,self.store)
        self.collector['events'][0]['text']=self.candidate['valueText']
        self.collector['evidence']=[];self.seal()
        with self.assertRaisesRegex(ValueError,'CONTINUITY_EVENT_EVIDENCE_DIFFERS'):
            collector_continuity(self.collector,self.contract,self.coverage,self.store)

    def test_changed_source_bytes_and_wrong_coverage_cannot_be_hidden_by_snapshot_seal(self):
        ref=self.observation['body']
        self.store._path(ref['key']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Archived evidence failed integrity verification'):
            collector_continuity(self.collector,self.contract,self.coverage,self.store)
        self.collector['coverage']={**self.coverage,'successfulTasks':1};self.seal()
        with self.assertRaisesRegex(ValueError,'CONTINUITY_SOURCE_COVERAGE_DIFFERS'):
            collector_continuity(self.collector,self.contract,self.coverage,self.store)

    def test_gate_keeps_live_publication_baseline_separate_from_collector_history(self):
        repo=Path(self.temp.name)/'repo'
        data=repo/'web/src/data/generated';data.mkdir(parents=True)
        (repo/'contracts').mkdir()
        (repo/'contracts/market.json').write_text(json.dumps(self.contract))
        (data/'dailyMarket.json').write_text(json.dumps({'enabled':True,'events':[],'committed':'stale'}))
        receipt={'attemptId':'c'*64,'completedAt':'2026-10-23T11:34:15Z','outcome':'not_checked',
                 'sourceId':'example:official','observationIds':[]}
        self.coverage['receipts']=[receipt]
        self.seal()
        self.store.write_once('runs/actual-run/plan.json',self.plan)
        self.store.write_once('runs/actual-run/attempts/'+ 'c'*64 +'.json',receipt)
        self.store.compare_and_swap('latest-run',None,{'receipt':self.store.put(self.coverage)})
        self.store.compare_and_swap('dailySnapshot',None,self.collector)
        self.store.compare_and_swap('production',None,{'releaseId':'published'})
        published={'enabled':True,'events':[],'reviewQueue':[],'published':'trusted'}
        self.store.write_once('releases/published.json',{'manifest':{
            'snapshot':self.store.put(json.dumps(published).encode()),
            'artifact':{'archive':self.store.put(b'fixture-build'),'sha256':digest([])}}})
        output={'runId':'actual-run','contractSha256':digest(self.contract)}
        destination=Path(self.temp.name)/'gate';destination.mkdir()
        with patch('gate.validate_contract',return_value=self.contract),patch('gate.reconcile',return_value=self.coverage), \
             patch('gate.build_snapshot',return_value=output) as build, \
             patch('gate.unpack',return_value={'static/certified-coverage.json':b'{"baseline":"published"}'}), \
             patch('gate.inventory',return_value=[]),patch('publication.verify_acknowledgement'), \
             patch('vercel.VercelAdapter._get',return_value={}):
            gate.prepare_data(repo,self.store,destination)
        self.assertEqual(build.call_args.kwargs['previous'],published)
        self.assertEqual(build.call_args.kwargs['continuity']['pendingFacts'][0]['event'],self.event)
        self.assertEqual((data/'certifiedCoverage.json').read_bytes(),b'{"baseline":"published"}')
