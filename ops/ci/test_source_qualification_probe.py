"""Seven disclosed diagnostic requests, with fictional evidence and transport only."""
import copy
from html import escape
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from test_onboarding_budget import Clock, FictionalFetcher, NOW, contract
from contracts import canonical, digest
from onboarding import (PersistentProbeBudget, _probe_qualification_targets,
                        probe_sources, validate_qualification_probe_plan)
from storage import LocalStore


def file_reference(store, key):
    raw = (store.root / key).read_bytes()
    return {'key': key, 'sha256': digest(raw), 'bytes': len(raw)}


def seed_qualification_plan(store, policy, path, *, disclosure='html', source_observation=False,
                            record_mutation=None, encoded_link=False):
    """Seed only a temporary archive; never change the caller's market contract."""
    source = policy['sources'][0]
    targets = ['https://example.invalid/qualification-' + str(i) for i in range(7)]
    if encoded_link:
        targets[-1] += '?first=one&second=two'
    if disclosure == 'rss':
        body = ('<rss><channel>' + ''.join('<item><link>' + u + '</link></item>' for u in targets)
                + '</channel></rss>').encode()
    else:
        # Include all recognized HTML disclosure forms and relative/entity decoding.
        body = ('<html><head><link rel="canonical" href="/qualification-0">'
                '<link rel="alternate" type="application/rss+xml" href="/qualification-1"></head><body>'
                + ''.join('<a href="' + escape(u, quote=True) + '">Retained disclosure</a>' for u in targets[2:])
                + '</body></html>').encode()
    body_ref = store.put(body)
    observed = {'requestedUrl': source['url'], 'finalUrl': source['url'], 'status': 'fetched',
                'httpStatus': 200, 'fetchedAt': NOW, 'body': body_ref}
    if source_observation:
        verified = next(s for s in policy['sources'] if s['registration'] == 'verified')
        observed.update(sourceId=verified['id'], requestedUrl=verified['url'], finalUrl=verified['url'],
                        observationId='a'*64)
        key = 'observations/' + observed['observationId'] + '.json'
        store.write_once(key, observed)
        proof = {'type': 'source_observation', 'record': file_reference(store, key),
                 'body': body_ref, 'fetchedAt': NOW}
    else:
        observation_ref = store.put(observed)
        record = {'checkpointProfile': 'source_probe', 'contractSha256': digest(policy),
                  'modelCalls': 0, 'sourceChecksCredited': 0, 'qualifiedSources': 0,
                  'semanticAdmission': False, 'coverageCredit': False,
                  'githubEventName': 'workflow_dispatch', 'githubRef': 'refs/heads/main',
                  'githubRunId': '901', 'githubRunAttempt': '1',
                  'diagnostic': {'sources': [{'sourceId': source['id'], 'supplierId': source['supplierId'],
                    'registration': 'candidate', 'qualified': False, 'facts': [],
                    'semanticAdmission': False, 'coverageCredit': False,
                    'observations': [observation_ref], 'fetchReservations': [{'url': source['url']}]}]}}
        if record_mutation:
            record_mutation(record)
        key = 'ci/source-probe-runs/901-1.json'
        store.write_once(key, record)
        proof = {'type': 'diagnostic_observation', 'record': file_reference(store, key),
                 'observation': observation_ref, 'body': body_ref, 'fetchedAt': NOW}
    plan = {'schemaVersion': 1, 'marketSha256': digest(policy), 'maxRequests': 7,
            'targets': [{'id': 'qualification-' + str(i), 'sourceId': source['id'],
                         'url': url, 'expectedFormat': 'html', 'proof': copy.deepcopy(proof)}
                        for i, url in enumerate(targets)]}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(plan))
    return plan


def retained_files(store):
    return {str(p.relative_to(store.root)): p.read_bytes() for p in store.root.rglob('*') if p.is_file()}


class Responses:
    def __init__(self, store, responses=None):
        self.store, self.responses, self.calls = store, list(responses or []), []

    def fetch(self, source, url):
        self.calls.append((source['id'], url))
        value = self.responses.pop(0) if self.responses else b'<html><body>Fictional release.</body></html>'
        if isinstance(value, Exception):
            raise value
        row = {'status': 'fetched', 'httpStatus': 200, 'requestedUrl': url, 'finalUrl': url,
               'fetchedAt': NOW}
        if isinstance(value, dict):
            row.update(value)
        else:
            row['body'] = self.store.put(value)
        return row


class SourceQualificationProbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'contracts/source-qualification-probes.json'
        self.store = LocalStore(Path(self.temp.name) / 'state')
        self.policy = contract()
        self.clock = Clock()
        self.plan = seed_qualification_plan(self.store, self.policy, self.path)

    def validate(self):
        return validate_qualification_probe_plan(self.policy, self.store, self.path)

    def budget(self):
        return PersistentProbeBudget(self.store, self.policy, clock=self.clock.now,
                                     monotonic=self.clock.monotonic, maximum_seconds=60)

    def write(self, plan):
        self.path.write_bytes(canonical(plan))

    def explicit_followup(self, *, channel=None, modern=False):
        if channel:
            source_id, feed, index = channel
            source=self.policy['sources'][0]
            source.update(id=source_id, url=feed, allowedHosts=[urlsplit(feed).hostname,'example.invalid'])
            seed_qualification_plan(self.store,self.policy,self.path,disclosure='rss')
        old_raw=self.path.read_text()
        old=validate_qualification_probe_plan(self.policy,self.store,self.path)
        self.store.compare_and_swap('budget-2026-10-23',None,{'calls':80,'documents':40,'fetches':10})
        source=self.policy['sources'][0]
        next_urls=['https://'+source['allowedHosts'][0]+'/next-'+str(i) for i in range(7)]
        next_urls[-1]+= ',literal?first=one&second=two'
        if channel:
            next_urls[0]=index
            body=('<rss><channel><link>'+index+'</link>'+''.join('<item><link>'+escape(u)+'</link></item>'
                  for u in next_urls[1:])+'</channel></rss>').encode()
            # The selected prior request must be the exact source feed.
            for target in old['plan']['targets']:
                if target['id']=='qualification-0':target['url']=feed;target['expectedFormat']='rss'
            old_raw=canonical(old['plan']).decode()
            old.update(rawSha256=digest(old_raw.encode()),canonicalSha256=digest(old['plan']))
            old['targets']=[{**t,'literalRecognition':'html_link_feed_or_canonical'} for t in old['plan']['targets']]
        else:
            body=('<html><body>'+''.join('<a href="'+escape(u,quote=True)+'">Next literal</a>' for u in next_urls)+'</body></html>').encode()
        budget=self.budget()
        explicit=_probe_qualification_targets(self.policy,self.store,Responses(self.store,[body]*7),budget,old)
        if modern:
            explicit['plan']['rawPlanReference']=self.store.put(old_raw.encode())
        record={'checkpointProfile':'source_probe','contractSha256':digest(self.policy),'executionCompleted':True,
                'appRevision':'a'*40,
                'outcome':'completed_diagnostic','apiFallback':False,
                'publication':{'published':False,'reason':'SOURCE_PROBE_DIAGNOSTIC_ONLY'},
                'modelCalls':0,'sourceChecksCredited':0,'qualifiedSources':0,'semanticAdmission':False,'coverageCredit':False,
                'githubEventName':'workflow_dispatch','githubRef':'refs/heads/main','githubRunId':'902','githubRunAttempt':1,
                'diagnostic':{'contractSha256':digest(self.policy),'executionCompleted':True,'checkedAt':NOW,
                    'qualified':False,'budgetDenied':False,
                    'sources':[{'sourceId':source['id'],'supplierId':source['supplierId'],
                                'registration':'candidate','qualified':False,'facts':[],
                                'semanticAdmission':False,'coverageCredit':False,'fetchReservations':[]}],
                    'facts':[],'qualifiedSources':0,'sourceChecksCredited':0,
                    'semanticAdmission':False,'coverageCredit':False,
                    'reservationContext':budget.summary(),'qualification':explicit}}
        key='ci/source-probe-runs/902-1.json';self.store.write_once(key,record)
        row=explicit['targets'][0];observed=json.loads(self.store.get(row['observation']))
        proof={'type':'qualification_observation','record':file_reference(self.store,key),
               'priorTargetId':row['targetId'],'priorTargetIndex':0,'priorTargetSha256':digest(row),
               'priorPlanRaw':old_raw,'priorPlanRawSha256':old['rawSha256'],
               'priorPlanCanonicalSha256':old['canonicalSha256'],'observation':row['observation'],
               'body':observed['body'],'fetchedAt':observed['fetchedAt']}
        if modern:
            proof.pop('priorPlanRaw')
            proof['priorPlanReference']=explicit['plan']['rawPlanReference']
        plan={'schemaVersion':1,'marketSha256':digest(self.policy),'maxRequests':7,
              'targets':[{'id':'next-'+str(i),'sourceId':source['id'],'url':u,'expectedFormat':'html',
                          'proof':copy.deepcopy(proof)} for i,u in enumerate(next_urls)]}
        self.write(plan)
        return plan,record,key

    def test_actual_execution_retains_exact_raw_plan_once_and_pure_validation_stays_read_only(self):
        raw=self.path.read_bytes();before=retained_files(self.store)
        validated=self.validate()
        self.assertNotIn('rawPlanReference',validated)
        self.assertEqual(retained_files(self.store),before)
        with patch.object(self.store,'put',wraps=self.store.put) as put:
            result=probe_sources(self.policy,self.store,Responses(self.store),reservation_context=self.budget(),
                                 qualification_plan_path=self.path)
        reference=result['qualification']['plan']['rawPlanReference']
        self.assertEqual(self.store.get(reference),raw)
        self.assertEqual(reference['sha256'],result['qualification']['plan']['rawSha256'])
        self.assertEqual(sum(call.args[0]==raw for call in put.call_args_list),1)

    def test_compact_reference_proof_replays_and_rejects_missing_altered_or_legacy_fallback(self):
        plan,record,_key=self.explicit_followup(modern=True)
        before=retained_files(self.store);self.validate();self.assertEqual(retained_files(self.store),before)
        def raw_only(proof):
            proof['priorPlanRaw']=self.store.get(proof.pop('priorPlanReference')).decode()
        mutations=[lambda p:p['priorPlanReference'].update(bytes=1),
                   lambda p:p['priorPlanReference'].update(sha256='b'*64),
                   lambda p:p.update(priorPlanReference=self.store.put(b'{}')),
                   lambda p:p.update(priorPlanRaw='{}'),
                   lambda p:p.pop('priorPlanReference'),raw_only]
        for mutate in mutations:
            candidate=copy.deepcopy(plan);mutate(candidate['targets'][-1]['proof']);self.write(candidate)
            fetcher=Responses(self.store);budget=self.budget();before=retained_files(self.store)
            with self.subTest(mutation=mutate),patch.object(self.store,'put') as put,self.assertRaises(ValueError):
                probe_sources(self.policy,self.store,fetcher,reservation_context=budget,qualification_plan_path=self.path)
            put.assert_not_called();self.assertEqual(fetcher.calls,[]);self.assertEqual(retained_files(self.store),before)
        self.write(plan)
        reference=plan['targets'][0]['proof']['priorPlanReference']
        path=self.store.root/reference['key'];raw=path.read_bytes();path.write_bytes(b'tampered')
        with self.assertRaisesRegex(ValueError,'integrity'):self.validate()
        path.write_bytes(raw);path.unlink()
        with self.assertRaises(FileNotFoundError):self.validate()

    def test_leased_execution_persists_raw_plan_only_after_acknowledged_escrow(self):
        from test_leased_source_probe import LeasedSourceProbeTests
        case=LeasedSourceProbeTests();case.setUp();persisted=[];original=LocalStore.put
        def put(store,body):
            path=case.repo/'contracts/source-qualification-probes.json'
            if isinstance(body,bytes) and path.exists() and body==path.read_bytes():
                self.assertGreaterEqual(len(case.pushes),2)
                persisted.append(body)
            return original(store,body)
        try:
            with patch.object(LocalStore,'put',new=put):result=case.run_probe()
            self.assertEqual(len(persisted),1)
            reference=result['diagnostic']['qualification']['plan']['rawPlanReference']
            self.assertEqual(case.state().get(reference),persisted[0])
        finally:case.doCleanups()

    def test_invalid_last_target_persists_no_current_raw_plan_and_starts_no_transport(self):
        plan=copy.deepcopy(self.plan);plan['targets'][-1]['url']='https://example.invalid/not-disclosed';self.write(plan)
        fetcher=Responses(self.store);budget=self.budget();before=retained_files(self.store)
        with patch.object(self.store,'put') as put,self.assertRaisesRegex(ValueError,'NOT_LITERAL'):
            probe_sources(self.policy,self.store,fetcher,reservation_context=budget,qualification_plan_path=self.path)
        put.assert_not_called();self.assertEqual(fetcher.calls,[]);self.assertEqual(retained_files(self.store),before)

    def test_several_actual_synthetic_generations_use_small_references_without_raw_nesting(self):
        self.store.compare_and_swap('budget-2026-10-23',None,{'calls':80,'documents':40,'fetches':0})
        sizes=[]
        for generation in range(6):
            next_urls=['https://example.invalid/generation-'+str(generation)+'-'+str(i) for i in range(7)]
            body=('<html><body>'+''.join('<a href="'+u+'">Next disclosure</a>' for u in next_urls)+'</body></html>').encode()
            result=probe_sources(self.policy,self.store,Responses(self.store,[body]*30),reservation_context=self.budget(),
                                 qualification_plan_path=self.path)
            prior=result['qualification']['plan'];row=result['qualification']['targets'][0]
            observation=json.loads(self.store.get(row['observation']))
            key='ci/source-probe-runs/'+str(1000+generation)+'-1.json'
            record={'checkpointProfile':'source_probe','contractSha256':digest(self.policy),'appRevision':'a'*40,
                    'executionCompleted':True,'outcome':'completed_diagnostic','apiFallback':False,
                    'publication':{'published':False,'reason':'SOURCE_PROBE_DIAGNOSTIC_ONLY'},
                    'modelCalls':0,'sourceChecksCredited':0,'qualifiedSources':0,'semanticAdmission':False,'coverageCredit':False,
                    'githubEventName':'workflow_dispatch','githubRef':'refs/heads/main','githubRunId':str(1000+generation),
                    'githubRunAttempt':1,'diagnostic':result}
            self.store.write_once(key,record)
            proof={'type':'qualification_observation','record':file_reference(self.store,key),
                   'priorTargetId':row['targetId'],'priorTargetIndex':0,'priorTargetSha256':digest(row),
                   'priorPlanReference':prior['rawPlanReference'],'priorPlanRawSha256':prior['rawSha256'],
                   'priorPlanCanonicalSha256':prior['canonicalSha256'],'observation':row['observation'],
                   'body':observation['body'],'fetchedAt':observation['fetchedAt']}
            plan={'schemaVersion':1,'marketSha256':digest(self.policy),'maxRequests':7,
                  'targets':[{'id':'generation-'+str(generation)+'-'+str(i),'sourceId':self.policy['sources'][0]['id'],
                              'url':u,'expectedFormat':'html','proof':copy.deepcopy(proof)} for i,u in enumerate(next_urls)]}
            self.write(plan);self.validate();sizes.append(len(self.path.read_bytes()))
            self.assertTrue(all('priorPlanRaw' not in t['proof'] for t in plan['targets']))
        self.assertLess(max(sizes),20_000)
        self.assertLess(max(sizes)-min(sizes),1_000)

    def test_explicit_followup_binds_prior_plan_row_charge_and_literal_commas_without_writes(self):
        plan,_record,_key=self.explicit_followup()
        before=retained_files(self.store)
        result=self.validate()
        self.assertEqual(retained_files(self.store),before)
        self.assertEqual([t['url'] for t in result['targets']],[t['url'] for t in plan['targets']])
        self.assertIn(',literal?',result['targets'][-1]['url'])
        self.assertEqual(self.store.read('heads/budget-2026-10-23.json'),{'calls':80,'documents':40,'fetches':17})

    def test_explicit_followup_proof_tampering_fails_all_seven_before_transport(self):
        plan,_record,_key=self.explicit_followup()
        mutations=[lambda p:p.update(priorTargetId='missing'),lambda p:p.update(priorTargetIndex=1),
                   lambda p:p.update(priorTargetSha256='b'*64),lambda p:p.update(priorPlanRaw=p['priorPlanRaw']+' '),
                   lambda p:p.update(priorPlanRawSha256='b'*64),lambda p:p.update(priorPlanCanonicalSha256='b'*64),
                   lambda p:p.update(fetchedAt='2026-10-24T00:00:00Z'),lambda p:p['body'].update(bytes=1)]
        for mutate in mutations:
            changed=copy.deepcopy(plan);mutate(changed['targets'][-1]['proof']);self.write(changed)
            before=retained_files(self.store);fetcher=Responses(self.store);budget=self.budget()
            with self.subTest(mutation=mutate),self.assertRaises(ValueError):
                probe_sources(self.policy,self.store,fetcher,reservation_context=budget,qualification_plan_path=self.path)
            self.assertEqual(fetcher.calls,[]);self.assertEqual(budget.reservations,0)
            self.assertEqual(retained_files(self.store),before)

    def test_changed_prior_results_or_reservation_ledger_fail_even_with_rehashed_record(self):
        plan,record,key=self.explicit_followup()
        def row(r):return r['diagnostic']['qualification']['targets'][0]
        def old(r):return r['diagnostic']['qualification']['plan']
        mutations=[lambda r:row(r).update(reservation=None),lambda r:row(r).update(budgetDenied=True),
                   lambda r:row(r).update(reason='HTTP_403'),lambda r:row(r).update(sourceId='other-source'),
                   lambda r:row(r).update(coverageCredit=True),lambda r:r.update(apiFallback=True),
                   lambda r:r['diagnostic']['sources'][0].update(supplierId='other-supplier'),
                   lambda r:r['diagnostic']['sources'].append(copy.deepcopy(r['diagnostic']['sources'][0])),
                   lambda r:r['diagnostic']['qualification']['targets'][1].update(modelCalls=1),
                   lambda r:r.update(executionCompleted=False),lambda r:r.update(contractSha256='b'*64),
                   lambda r:old(r).update(rawSha256='b'*64),
                   lambda r:old(r)['targets'].reverse(),
                   lambda r:r['diagnostic']['qualification']['targets'].reverse(),
                   lambda r:r['diagnostic']['qualification']['targets'].append(copy.deepcopy(row(r))),
                   lambda r:row(r)['reservation'].update(chargedFetchCount=12),
                   lambda r:r['diagnostic']['reservationContext']['currentBudget'].update(calls=81)]
        for mutate in mutations:
            changed=copy.deepcopy(record);mutate(changed)
            (self.store.root/key).write_bytes(canonical(changed))
            candidate=copy.deepcopy(plan)
            for target in candidate['targets']:
                target['proof']['record']=file_reference(self.store,key)
                target['proof']['priorTargetSha256']=digest(row(changed))
            self.write(candidate)
            with self.subTest(mutation=mutate),self.assertRaises(ValueError):self.validate()

    def test_prior_runtime_day_and_diagnostic_flags_reject_rehashed_contradictions(self):
        plan,record,key=self.explicit_followup()
        mutations={
            'start previous day':lambda r:r['diagnostic']['reservationContext'].update(startedAt='2026-10-22T23:59:00Z'),
            'finish next day':lambda r:r['diagnostic'].update(checkedAt='2026-10-24T00:00:00Z'),
            'local date hides UTC crossing':lambda r:r['diagnostic']['reservationContext'].update(startedAt='2026-10-23T00:30:00+02:00'),
            'elapsed overrun':lambda r:r['diagnostic']['reservationContext'].update(startedAt='2026-10-23T11:00:00Z'),
            'boolean runtime':lambda r:r['diagnostic']['reservationContext'].update(maximumRuntimeSeconds=True),
            'zero runtime':lambda r:r['diagnostic']['reservationContext'].update(maximumRuntimeSeconds=0),
            'oversized runtime':lambda r:r['diagnostic']['reservationContext'].update(maximumRuntimeSeconds=1201),
            'qualified diagnostic':lambda r:r['diagnostic'].update(qualified=True),
            'budget denied diagnostic':lambda r:r['diagnostic'].update(budgetDenied=True),
            'qualified integer zero':lambda r:r['diagnostic'].update(qualified=0),
            'budget denied integer zero':lambda r:r['diagnostic'].update(budgetDenied=0),
            'unfinished inflight':lambda r:r['diagnostic'].update(executionCompleted=False),
        }
        for name,mutate in mutations.items():
            changed=copy.deepcopy(record);mutate(changed)
            (self.store.root/key).write_bytes(canonical(changed));candidate=copy.deepcopy(plan)
            for target in candidate['targets']:target['proof']['record']=file_reference(self.store,key)
            self.write(candidate)
            fetcher=Responses(self.store);budget=self.budget();before=retained_files(self.store)
            with self.subTest(name=name),self.assertRaises(ValueError):
                probe_sources(self.policy,self.store,fetcher,reservation_context=budget,qualification_plan_path=self.path)
            self.assertEqual(fetcher.calls,[]);self.assertEqual(budget.reservations,0)
            self.assertEqual(retained_files(self.store),before)

    def test_only_exact_source_bound_rss_channel_disclosures_are_allowed(self):
        for source_id,feed,index in (
            ('delinea:official:1','https://delinea.com/news/rss.xml','https://delinea.com/news'),
            ('sonatype:official:1','https://www.sonatype.com/press-releases/rss.xml','https://www.sonatype.com/press-releases')):
            # Each case owns a fresh archive and no transport beyond fictional responses.
            with self.subTest(source=source_id),tempfile.TemporaryDirectory() as directory:
                original_store,original_policy,original_path=self.store,self.policy,self.path
                self.store=LocalStore(Path(directory)/'state');self.policy=contract();self.path=Path(directory)/'plan.json'
                try:
                    plan,_record,_key=self.explicit_followup(channel=(source_id,feed,index))
                    result=self.validate()
                    self.assertEqual(result['targets'][0]['literalRecognition'],'source_bound_rss_channel_link')
                    plan['targets'][0]['url']=index+'/invented';self.write(plan)
                    with self.assertRaisesRegex(ValueError,'NOT_LITERAL'):self.validate()
                finally:self.store,self.policy,self.path=original_store,original_policy,original_path

    def repin_explicit_observation(self, plan, record, key, observation):
        reference=self.store.put(observation)
        row=record['diagnostic']['qualification']['targets'][0]
        row['observation']=reference
        (self.store.root/key).write_bytes(canonical(record))
        for target in plan['targets']:
            target['proof'].update(record=file_reference(self.store,key),observation=reference,
                                  priorTargetSha256=digest(row),body=observation.get('body'))
        self.write(plan)

    def test_explicit_failed_or_redirected_prior_observation_is_not_disclosure_proof(self):
        plan,record,key=self.explicit_followup()
        observed=json.loads(self.store.get(record['diagnostic']['qualification']['targets'][0]['observation']))
        for change in ({'status':'blocked','httpStatus':403}, {'finalUrl':'https://example.invalid/different'},
                       {'fetchedAt':'2026-10-24T00:00:00Z'}):
            with self.subTest(change=change):
                self.repin_explicit_observation(copy.deepcopy(plan),copy.deepcopy(record),key,{**observed,**change})
                with self.assertRaises(ValueError):self.validate()

    def test_duplicate_rss_channel_cannot_supply_source_bound_index_proof(self):
        self.store=LocalStore(Path(self.temp.name)/'channel-state')
        plan,record,key=self.explicit_followup(channel=(
            'delinea:official:1','https://delinea.com/news/rss.xml','https://delinea.com/news'))
        observed=json.loads(self.store.get(record['diagnostic']['qualification']['targets'][0]['observation']))
        raw=self.store.get(observed['body']).replace(b'<channel>',b'<channel><link>https://delinea.com/news</link>')
        observed['body']=self.store.put(raw)
        self.repin_explicit_observation(plan,record,key,observed)
        with self.assertRaisesRegex(ValueError,'CHANNEL_DISCLOSURE_DIFFERS'):self.validate()

    def test_explicit_followup_body_tamper_fails_integrity_without_transport(self):
        plan,_record,_key=self.explicit_followup()
        (self.store.root/plan['targets'][0]['proof']['body']['key']).write_bytes(b'changed body')
        fetcher=Responses(self.store);budget=self.budget()
        with self.assertRaisesRegex(ValueError,'integrity'):
            probe_sources(self.policy,self.store,fetcher,reservation_context=budget,qualification_plan_path=self.path)
        self.assertEqual(fetcher.calls,[]);self.assertEqual(budget.reservations,0)

    def test_exact_plan_hashes_literal_disclosures_and_read_only_validation(self):
        before = retained_files(self.store)
        result = self.validate()
        self.assertEqual(retained_files(self.store), before)
        self.assertEqual(result['rawSha256'], digest(self.path.read_bytes()))
        self.assertEqual(result['canonicalSha256'], digest(self.plan))
        self.assertEqual(result['maxRequests'], 7)
        self.assertEqual([t['url'] for t in result['targets']], [t['url'] for t in self.plan['targets']])
        self.assertEqual({t['literalRecognition'] for t in result['targets']}, {'html_link_feed_or_canonical'})
        self.path.write_text(json.dumps(self.plan, indent=2))
        formatted = self.validate()
        self.assertNotEqual(formatted['rawSha256'], result['rawSha256'])
        self.assertEqual(formatted['canonicalSha256'], result['canonicalSha256'])

    def test_rss_item_disclosure_and_verified_original_binding(self):
        for mode in ('rss', 'source_observation'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                store = LocalStore(Path(directory) / 'state')
                policy = contract()
                if mode == 'source_observation':
                    policy['sources'].append({**policy['sources'][0], 'id': 'original-citation',
                        'registration': 'verified', 'url': 'https://example.invalid/original'})
                path = Path(directory) / 'plan.json'
                seed_qualification_plan(store, policy, path, disclosure='rss' if mode == 'rss' else 'html',
                                        source_observation=mode == 'source_observation')
                result = validate_qualification_probe_plan(policy, store, path)
                self.assertEqual(len(result['targets']), 7)
                self.assertEqual(result['targets'][0]['literalRecognition'],
                                 'rss_or_atom_item_link' if mode == 'rss' else 'html_link_feed_or_canonical')

    def test_literal_html_entity_decoding_does_not_construct_a_new_endpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            store = LocalStore(Path(directory) / 'state')
            path = Path(directory) / 'plan.json'
            seeded = seed_qualification_plan(store, self.policy, path, encoded_link=True)
            result = validate_qualification_probe_plan(self.policy, store, path)
            self.assertEqual(result['targets'][-1]['url'], seeded['targets'][-1]['url'])
            self.assertIn('&second=two', result['targets'][-1]['url'])

    def test_invalid_plan_and_proof_fail_before_any_transport_or_state_write(self):
        mutations = {
            'wrong policy': lambda p: p.update(marketSha256='b'*64),
            'six targets': lambda p: p['targets'].pop(),
            'eight targets': lambda p: p['targets'].append(copy.deepcopy(p['targets'][0])),
            'cap bool': lambda p: p.update(maxRequests=True),
            'cap eight': lambda p: p.update(maxRequests=8),
            'duplicate id': lambda p: p['targets'][-1].update(id=p['targets'][0]['id']),
            'duplicate url': lambda p: p['targets'][-1].update(url=p['targets'][0]['url']),
            'different source': lambda p: p['targets'][-1].update(sourceId='unregistered'),
            'unadvertised URL': lambda p: p['targets'][-1].update(url='https://example.invalid/guessed'),
            'outside host': lambda p: p['targets'][-1].update(url='https://other.invalid/qualification-6'),
            'credentials': lambda p: p['targets'][-1].update(url='https://user@example.invalid/qualification-6'),
            'fragment': lambda p: p['targets'][-1].update(url=p['targets'][-1]['url']+'#hidden'),
            'port': lambda p: p['targets'][-1].update(url='https://example.invalid:8443/qualification-6'),
            'http': lambda p: p['targets'][-1].update(url='http://example.invalid/qualification-6'),
            'format': lambda p: p['targets'][-1].update(expectedFormat='sitemap'),
            'proof time': lambda p: p['targets'][-1]['proof'].update(fetchedAt='2026-10-24T00:00:00Z'),
            'proof size': lambda p: p['targets'][-1]['proof']['body'].update(bytes=1),
            'proof digest': lambda p: p['targets'][-1]['proof']['body'].update(sha256='b'*64),
            'record digest': lambda p: p['targets'][-1]['proof']['record'].update(sha256='b'*64),
            'record missing': lambda p: p['targets'][-1]['proof']['record'].update(key='ci/source-probe-runs/902-1.json'),
            'proof traversal': lambda p: p['targets'][-1]['proof']['body'].update(key='../objects/'+'a'*64),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                plan = copy.deepcopy(self.plan)
                mutate(plan)
                self.write(plan)
                budget = self.budget()
                fetcher = Responses(self.store)
                before = retained_files(self.store)
                with self.assertRaises((ValueError, OSError)):
                    probe_sources(self.policy, self.store, fetcher, reservation_context=budget,
                                  qualification_plan_path=self.path)
                self.assertEqual(fetcher.calls, [])
                self.assertEqual(retained_files(self.store), before)
                self.assertEqual(budget.reservations, 0)
        self.path.unlink()
        before = retained_files(self.store)
        with self.assertRaises(FileNotFoundError):
            self.validate()
        self.assertEqual(retained_files(self.store), before)

    def test_tampered_body_bytes_are_rejected_without_writes(self):
        target = self.plan['targets'][-1]
        body_path = self.store.root / target['proof']['body']['key']
        body_path.write_bytes(b'tampered')
        before = retained_files(self.store)
        with self.assertRaisesRegex(ValueError, 'integrity'):
            self.validate()
        self.assertEqual(retained_files(self.store), before)

    def test_missing_body_is_rejected_without_transport_or_archive_writes(self):
        body = self.store.root / self.plan['targets'][-1]['proof']['body']['key']
        body.unlink()
        budget, fetcher = self.budget(), Responses(self.store)
        before = retained_files(self.store)
        with patch.object(self.store, 'put') as put, patch.object(self.store, 'write_once') as write, \
                patch.object(self.store, 'compare_and_swap') as cas, self.assertRaises(FileNotFoundError):
            probe_sources(self.policy, self.store, fetcher, reservation_context=budget,
                          qualification_plan_path=self.path)
        put.assert_not_called()
        write.assert_not_called()
        cas.assert_not_called()
        self.assertEqual(fetcher.calls, [])
        self.assertEqual(retained_files(self.store), before)

    def test_diagnostic_provenance_and_source_join_cannot_be_forged(self):
        def source(record):
            return record['diagnostic']['sources'][0]
        mutations = [lambda r: r.update(coverageCredit=True), lambda r: r.update(modelCalls=False),
                     lambda r: r.update(githubRef='refs/heads/preview'), lambda r: r.update(githubRunId='902'),
                     lambda r: source(r).update(supplierId='other-supplier'),
                     lambda r: source(r).update(facts=None), lambda r: source(r).update(observations=[]),
                     lambda r: source(r).update(observations=None),
                     lambda r: source(r).update(fetchReservations=[None]),
                     lambda r: source(r).update(fetchReservations=[{'url': 'https://example.invalid/wrong'}])]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as directory:
                store = LocalStore(Path(directory) / 'state')
                path = Path(directory) / 'plan.json'
                seed_qualification_plan(store, self.policy, path, record_mutation=mutate)
                before = retained_files(store)
                with self.assertRaises(ValueError):
                    validate_qualification_probe_plan(self.policy, store, path)
                self.assertEqual(retained_files(store), before)

    def test_target_verified_status_does_not_silently_activate_diagnostic(self):
        self.policy['sources'][0]['registration'] = 'verified'
        self.plan['marketSha256'] = digest(self.policy)
        self.write(self.plan)
        with self.assertRaisesRegex(ValueError, 'CANDIDATE'):
            self.validate()

    def test_seven_charged_results_retain_failures_redirects_and_malformed_bodies(self):
        plan = self.validate()
        plan['targets'][3]['expectedFormat'] = 'rss'
        plan['targets'][4]['expectedFormat'] = 'rss'
        plan['targets'][5]['expectedFormat'] = 'rss'
        fetcher = Responses(self.store, [
            {'status': 'blocked', 'httpStatus': 403, 'errorCode': 'HTTP_403'},
            {'status': 'blocked', 'httpStatus': 429, 'errorCode': 'HTTP_429'},
            {'finalUrl': 'https://example.invalid/alternate'},
            b'<rss><broken>', b'<rss><channel/></rss>',
            b'<rss><channel><item><link>https://example.invalid/unplanned</link></item></channel></rss>',
            b'<html><body></body></html>'])
        budget = self.budget()
        result = _probe_qualification_targets(self.policy, self.store, fetcher, budget, plan)
        self.assertEqual([r['reason'] for r in result['targets']], ['HTTP_403', 'HTTP_429',
            'QUALIFICATION_REDIRECTED', 'ParseError', 'EMPTY_FEED_RETAINED_REQUIRES_QUALIFICATION',
            'RESPONSE_RETAINED_SCOPE_AND_HISTORY_REVIEW_REQUIRED', 'QUALIFICATION_EMPTY_HTML'])
        self.assertEqual(result['chargedExplicitRequests'], 7)
        self.assertEqual(len(fetcher.calls), 7)
        self.assertEqual([u for _s, u in fetcher.calls], [t['url'] for t in self.plan['targets']])
        self.assertEqual(budget.summary()['currentBudget'], {'calls': 0, 'documents': 0, 'fetches': 7})
        for row in result['targets']:
            self.assertFalse(row['qualified'])
            self.assertFalse(row['semanticAdmission'])
            self.assertFalse(row['coverageCredit'])
            self.assertEqual(row['facts'], [])
            self.assertEqual(row['modelCalls'], 0)
            self.assertIsNotNone(row['observation'])
        self.assertEqual(len(list((self.store.root / 'source-probes/qualification').glob('*/*.json'))), 7)

    def test_transport_exceptions_remain_charged_and_do_not_retry(self):
        fetcher = Responses(self.store, [RuntimeError('fictional transport failure')]*7)
        result = _probe_qualification_targets(self.policy, self.store, fetcher, self.budget(), self.validate())
        self.assertEqual(len(fetcher.calls), 7)
        self.assertEqual(result['chargedExplicitRequests'], 7)
        self.assertTrue(all(r['reason'] == 'RuntimeError' and r['observation'] is None for r in result['targets']))

    def test_last_capacity_and_day_guard_prevent_unreserved_transport(self):
        self.store.compare_and_swap('budget-2026-10-23', None, {'calls': 80, 'documents': 40, 'fetches': 5499})
        fetcher = Responses(self.store)
        result = _probe_qualification_targets(self.policy, self.store, fetcher, self.budget(), self.validate())
        self.assertEqual(len(fetcher.calls), 1)
        self.assertEqual(result['chargedExplicitRequests'], 1)
        self.assertEqual(sum(r['budgetDenied'] for r in result['targets']), 6)
        self.assertEqual(self.store.read('heads/budget-2026-10-23.json'), {'calls': 80, 'documents': 40, 'fetches': 5500})
        self.clock.current = '2026-10-24T00:00:00Z'
        budget = self.budget()
        self.clock.current = '2026-10-25T00:00:00Z'
        fetcher = Responses(self.store)
        result = _probe_qualification_targets(self.policy, self.store, fetcher, budget, self.validate())
        self.assertEqual(fetcher.calls, [])
        self.assertTrue(all(r['reason'] == 'SOURCE_PROBE_UTC_DAY_CHANGED' for r in result['targets']))
        self.assertIsNone(self.store.read('heads/budget-2026-10-25.json'))

    def test_day_change_after_reservation_retains_charge_without_transport(self):
        budget = self.budget()
        reserve = budget.reserve_fetch
        def cross_midnight():
            result = reserve()
            self.clock.current = '2026-10-24T00:00:00Z'
            return result
        fetcher = Responses(self.store)
        with patch.object(budget, 'reserve_fetch', side_effect=cross_midnight):
            result = _probe_qualification_targets(self.policy, self.store, fetcher, budget, self.validate())
        self.assertEqual(result['chargedExplicitRequests'], 1)
        self.assertEqual(fetcher.calls, [])
        self.assertEqual(self.store.read('heads/budget-2026-10-23.json')['fetches'], 1)
        self.assertTrue(all(r['budgetDenied'] for r in result['targets']))

    def test_generic_probe_and_explicit_seven_remain_separate_without_fact_heads(self):
        self.store.compare_and_swap('latest-run', None, {'keep': 'normal collector'})
        head = (self.store.root / 'heads/latest-run.json').read_bytes()
        fetcher = FictionalFetcher(self.store)
        report = probe_sources(self.policy, self.store, fetcher, reservation_context=self.budget(),
                               qualification_plan_path=self.path)
        self.assertEqual(len(report['sources']), 1)
        self.assertEqual(len(report['qualification']['targets']), 7)
        self.assertEqual(len(fetcher.calls), 8)
        self.assertEqual(report['reservationContext']['probeFetchReservations'], 8)
        self.assertEqual((self.store.root / 'heads/latest-run.json').read_bytes(), head)
        self.assertEqual(report['facts'], [])
        self.assertEqual(report['sourceChecksCredited'], 0)
        self.assertEqual(report['qualifiedSources'], 0)
        self.assertFalse(report['coverageCredit'])
        self.assertFalse(report['semanticAdmission'])


if __name__ == '__main__':
    unittest.main()
