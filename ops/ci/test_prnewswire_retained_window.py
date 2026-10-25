"""Read-only original graph replay, primary joins and closed proposal adversaries."""
import copy
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from test_prnewswire_press_list import ROOT, ACCURACY, ARCHIVE, AS_OF, ReadOnlyActual
from contracts import canonical, digest, ContractError
from storage import LocalStore
from historical_correction_fixtures import historical_requests
import onboarding
import prnewswire_retained_window as operation

DESCRIPTOR = ACCURACY / 'prnewswire-retained-window-descriptor-2026-10-25.json'


def replay_complete(record, contract, store):
    """Replay unchanged legacy traversal with already charged, already fetched evidence only."""
    report = record['diagnostic']; rows = report['sources']; explicit = report['qualification']['targets']
    state = {'clock':0, 'generic':None, 'reserve':0, 'observe':0, 'explicit':0}
    class FrozenReplayStore:
        def get(self, ref): return store.get(ref)
        def read(self, key): return store.read(key)
        def put(self, value):
            raw = value if isinstance(value, bytes) else canonical(value)
            ref = {'key':'objects/'+digest(raw),'sha256':digest(raw),'bytes':len(raw)}
            assert store.get(ref) == raw
            return ref
        def write_once(self, key, value):
            raw = value if isinstance(value, bytes) else canonical(value)
            assert store.raw(key) == raw
    class SequentialPool:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def map(self, fn, items): return [fn(item) for item in items]
    def clock():
        index = state['clock']; state['clock'] += 1
        if index < len(rows):
            state.update(generic=rows[index], reserve=0, observe=0)
            return rows[index]['checkedAt']
        assert index == len(rows)
        return report['checkedAt']
    def reserve():
        if state['clock'] <= len(rows) and state['reserve'] < len(state['generic']['fetchReservations']):
            row = state['generic']['fetchReservations'][state['reserve']]; state['reserve'] += 1
            return {k:v for k,v in row.items() if k!='url'}
        row = explicit[state['explicit']]; state['explicit'] += 1
        return row['reservation']
    budget = object.__new__(onboarding.PersistentProbeBudget)
    budget.clock = clock; budget.reserve_fetch = reserve; budget.before_fetch = lambda: None
    def bound(s, c): assert isinstance(s, FrozenReplayStore) and c == contract
    budget.assert_bound = bound; budget.summary = lambda: report['reservationContext']
    class FrozenFetcher:
        def fetch(self, source, url):
            if state['explicit']:
                row = explicit[state['explicit']-1]
                assert source['id'] == row['sourceId'] and url == row['url']
                return json.loads(store.get(row['observation']))
            row = state['generic']; index = state['observe']
            assert source['id'] == row['sourceId'] and url == row['fetchReservations'][index]['url']
            if index >= len(row['observations']):
                assert row['reason']=='ContractError'
                raise ContractError('RETAINED_FAILURE_WITH_NO_STATUS_INFERENCE')
            state['observe'] += 1
            value = json.loads(store.get(row['observations'][index])); assert value['requestedUrl']==url
            return value
    with tempfile.TemporaryDirectory(prefix='prn-legacy-replay-') as temporary:
        path = Path(temporary)/'original-plan.json'
        path.write_bytes(store.get(report['qualification']['plan']['rawPlanReference']))
        with patch.object(onboarding, 'ThreadPoolExecutor', SequentialPool):
            result = onboarding.probe_sources(contract, FrozenReplayStore(), FrozenFetcher(),
                reservation_context=budget, qualification_plan_path=path)
        result['qualification']['plan']['path'] = report['qualification']['plan']['path']
        assert result == report
    return {'runId':record['githubRunId'],'fullLegacyTraversalReplay':True,'frozenWrites':0,'sourceRequests':0}


@unittest.skipUnless((ARCHIVE/'archive-manifest.json').exists(), 'Requires authenticated retained 9e4a archive')
class RetainedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Original actual records stay under their pinned H, even after current policy advances.
        historical=ROOT/'contracts/html-qualification-seeds/8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db/contracts__8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db.json'
        historical_raw=historical.read_bytes()
        assert digest(historical_raw)=='8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db'
        cls.contract=json.loads(historical_raw)
        assert digest(cls.contract)=='8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db'
        cls.raw=DESCRIPTOR.read_bytes(); cls.descriptor=json.loads(cls.raw)
    def setUp(self):
        self.store=ReadOnlyActual(); self.addCleanup(self.store.unchanged,self)
        self.net=patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK'));self.net.start();self.addCleanup(self.net.stop)
        self.local=patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_STORE'));self.local.start();self.addCleanup(self.local.stop)
    def derive(self): return operation.derive_report(self.contract,self.store,self.raw)
    def test_actual_complete_proposal_separates_window_history_seed_scope_and_zero_credit(self):
        report=self.derive(); result=operation.verify_report(self.contract,self.store,self.raw,report)
        self.assertTrue(result['proposalEvidenceComplete']); self.assertFalse(result['qualified'])
        self.assertEqual((result['qualifiedSources'],result['sourceChecksCredited'],result['modelCalls']), (0,0,0))
        cato,chai=report['streams']
        self.assertEqual((len(cato['items']),len(chai['items'])),(125,47))
        self.assertEqual((len(cato['currentWindowItems']),len(chai['currentWindowItems'])),(2,5))
        self.assertFalse(cato['sourceScopeComplete']);self.assertTrue(chai['sourceScopeComplete'])
        self.assertEqual(len(cato['knownEvidenceUnion']),127);self.assertEqual(len(chai['knownEvidenceUnion']),47)
        self.assertFalse(cato['historicalEnumerationComplete']);self.assertTrue(chai['historicalEnumerationComplete'])
        self.assertTrue(all(s['dailyWindowComplete'] and not s['qualificationReadiness'] for s in (cato,chai)))
        self.assertEqual([r['shape']['publicationCalendarDay'] for r in cato['knownSeedsOutsideObservedList']], ['2026-07-27','2026-02-24'])
        self.assertTrue(all(r['calendarWindowState']=='older_calendar_day' for r in cato['knownSeedsOutsideObservedList']))
    def test_both_complete_original_diagnostics_replay_without_frozen_writes(self):
        for pin in self.descriptor['originalRuns']:
            record=json.loads(self.store.get(pin['record']))
            self.assertTrue(replay_complete(record,self.contract,self.store)['fullLegacyTraversalReplay'])
    def test_primary_original_full200_and_real304_chain_are_preserved(self):
        report=self.derive()
        for sample in report['primarySamples']:
            self.assertEqual(sample['originalReuseChain'][0]['httpStatus'],304)
            self.assertEqual(sample['originalReuseChain'][-1]['httpStatus'],200)
            self.assertNotEqual(sample['originalFull200FetchedAt'],sample['latestRevalidationAt'])
            self.assertNotEqual(sample['shape']['suppliedJsonLd']['datePublished'],sample['shape']['suppliedJsonLd']['dateModified'])
            self.assertTrue(sample['noClockRenewal'])
    def test_every_descriptor_scalar_and_missing_extra_fields_reject(self):
        def paths(value, at=()):
            if isinstance(value,dict):
                for k,v in value.items():yield from paths(v,at+(k,))
            elif isinstance(value,list):
                for i,v in enumerate(value):yield from paths(v,at+(i,))
            else:yield at
        count=0
        for path in paths(self.descriptor):
            changed=copy.deepcopy(self.descriptor);parent=changed
            for part in path[:-1]:parent=parent[part]
            value=parent[path[-1]];parent[path[-1]]=value+'-tampered' if isinstance(value,str) else -1
            with self.subTest(path=path),self.assertRaises(ValueError):operation.derive_report(self.contract,self.store,canonical(changed))
            count+=1
        self.assertGreater(count,200)
        for key in self.descriptor:
            changed=copy.deepcopy(self.descriptor);del changed[key]
            with self.subTest(missing=key),self.assertRaises(ValueError):operation.derive_report(self.contract,self.store,canonical(changed))
        changed=copy.deepcopy(self.descriptor);changed['qualified']=True
        with self.assertRaises(ValueError):operation.derive_report(self.contract,self.store,canonical(changed))
    def test_duplicate_plan_json_keys_and_nonfinite_constants_reject(self):
        for raw in (b'{"schemaVersion":1,"schemaVersion":1}',b'{"x":NaN}',b'{"x":Infinity}',b'{}',b'[]',b'{',b'x'*100001):
            with self.subTest(raw=raw[:30]),self.assertRaises(ValueError):operation.derive_report(self.contract,self.store,raw)
    def test_source_policy_mutation_rejects_without_historical_authority_bridge(self):
        changed=copy.deepcopy(self.contract)
        source=next(s for s in changed['sources'] if s['id']=='cato:official:1');source['registration']='verified'
        with self.assertRaises(ValueError):operation.derive_report(changed,self.store,self.raw)
    def test_store_cannot_forge_record_plan_page_primary_or_clock_even_with_rehashed_body(self):
        pins=[p['record'] for p in self.descriptor['originalRuns']]+[p['rawPlan'] for p in self.descriptor['originalRuns']]
        pins += [p['body'] for s in self.descriptor['sources'] for p in s['pages']]
        pins += [s['primary']['body'] for s in self.descriptor['sources']]
        pins += [s['primary']['latest'] for s in self.descriptor['sources']]
        for pin in pins:
            original=self.store.get(pin)
            class Forged:
                def get(_,ref):return original+b' ' if ref['key']==pin['key'] else self.store.get(ref)
                def read(_,key):return self.store.read(key)
            with self.subTest(key=pin['key']),self.assertRaises(ValueError):operation.derive_report(self.contract,Forged(),self.raw)
    def test_omitted_card_history_or_boundary_and_forged_credit_cannot_replay(self):
        report=self.derive()
        changes=[]
        for field in ('records','items','currentWindowItems','historicalItems'):
            changed=copy.deepcopy(report);changed['streams'][0][field].pop();changes.append(changed)
        changed=copy.deepcopy(report);changed['streams'][0]['historicalEnumerationComplete']=True;changes.append(changed)
        changed=copy.deepcopy(report);changed['qualifiedSources']=2;changes.append(changed)
        changed=copy.deepcopy(report);changed['primarySamples'][0]['originalFull200FetchedAt']=AS_OF;changes.append(changed)
        for changed in changes:
            with self.subTest(field=field),self.assertRaises(ValueError):operation.verify_report(self.contract,self.store,self.raw,changed)
    def test_supplied_primary_metadata_identity_conflicts_and_hidden_container_reject(self):
        pin=self.descriptor['sources'][1]['primary'];raw=self.store.get(pin['body'])
        report=self.derive();shape=report['primarySamples'][1]['shape'];day=shape['publicationCalendarDay']
        published=shape['suppliedJsonLd']['datePublished'].encode()
        mutations=[raw.replace(published,b'2025-10-24T11:00:00-04:00'),
            raw.replace(b'"NewsArticle"',b'"Product"'),raw.replace(b'"headline":',b'"headline":"other","headline":'),
            raw.replace(b'<h1>',b'<h1 hidden>'),raw.replace(b'class="release-body container ',b'class="release-body container hidden '),
            raw.replace(b'<script type="application/ld+json">',b'<script type="application/ld+json"/><script type="application/ld+json">'),
            raw.replace(b'<h1>',b'<template/><h1>'),raw.replace(pin['url'].encode(),b'https://www.prnewswire.com/news-releases/other.html')]
        # A made-up CSS class is not a visibility control; use the actual hidden attribute for that mutation.
        mutations[4]=raw.replace(b'class="release-body container ',b'hidden class="release-body container ')
        for changed in mutations:
            self.assertNotEqual(changed,raw)
            with self.subTest(sha=digest(changed)),self.assertRaises(ValueError):operation.primary_shape(changed,pin['url'],'chainguard:official:1',day)
    def test_legitimate_modification_date_difference_is_preserved(self):
        report=self.derive()
        for sample in report['primarySamples']:
            self.assertNotEqual(sample['shape']['suppliedJsonLd']['datePublished'],sample['shape']['suppliedJsonLd']['dateModified'])
    def test_six_existing_admissions_facts_holds_budget_and_expiry_remain_exact(self):
        from corrections import _index, group_review_policy, replay_admission
        requests=historical_requests()
        stamp=json.loads((ROOT/'web/src/data/tracker/factualCorrectionPolicy.json').read_bytes())
        admissions=[]
        for group in requests['groups']:
            policy=group_review_policy(group,self.contract,requests['baseline']['sha256'])
            self.assertEqual(stamp['reviewPolicySha256ByGroup'][group['id']],policy)
            ref=self.store.read(_index(group,policy))['admission']
            replay_admission(group,ref,self.store,self.contract,policy,AS_OF)
            admissions.append(ref)
        self.assertEqual(len(admissions),6)
        snapshot=self.store.read('heads/dailySnapshot.json')
        self.assertEqual(len(snapshot['factProvenance']),4);self.assertEqual(len(snapshot['reviewQueue']),38)
        self.assertEqual(snapshot['coverage']['validUntil'],'2026-10-26T15:55:27.307096+00:00')
        self.assertEqual(self.store.read('heads/budget-2026-10-25.json'),{'calls':80,'documents':38,'fetches':1101})

    def test_original_primary_article_token_exception_is_closed(self):
        pin=self.descriptor['sources'][0]['primary'];raw=self.store.get(pin['body']);day='2025-06-30'
        for changed in (raw.replace(b'aria-labelledby="langauge-dropdown"',b'aria-labelledby="other"'),
                        raw.replace(b'<ul class="dropdown-menu"',b'<template/><ul class="dropdown-menu"')):
            self.assertNotEqual(changed,raw)
            with self.assertRaises(ValueError):operation.primary_shape(changed,pin['url'],'cato:official:1',day)


if __name__=='__main__':unittest.main()
