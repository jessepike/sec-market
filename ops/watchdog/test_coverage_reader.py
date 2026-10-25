"""Socket-denied coverage reader and original-plan regressions with retained bytes."""
import copy
import gzip
import importlib.util
import io
import json
from pathlib import Path
import socket
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
AREA = ROOT / 'docs/active/daily-pipeline/accuracy'
ACTUAL = AREA / 'receipts/recovery-monitor-2026-10-25'
FIXTURES = AREA / 'receipts/coverage-monitor-inventory-bound-read-2026-10-25'
spec = importlib.util.spec_from_file_location('coverage_watchdog', Path(__file__).with_name('probe.py'))
probe = importlib.util.module_from_spec(spec); spec.loader.exec_module(probe)
NOW = '2026-10-25T08:13:04.369084Z'
PINS = {
    'current-original-plan.json': '0470e19e732f7c8d5bef1fd434a4e1798bdb61f9bf28285199102eda021eb429',
    'current-original-coverage.json': 'f2486a623d93da011eaaf11926e09d6ce1533dab26d4a8f2fa2875a95a84d0b6',
    'current-original-snapshot.json': 'ae75279b62c84bbd072748c7b228aaef5d908dfc5c87c856a7e0b1a173b94563',
    'current-accepted-factual-corrections.json': '1dcdfc2bfd3b1f02b44e299421f67c939dc48ca4bf7cfbc712ea53cac0e859cf',
    'cross-day-original-plan.json': '52f5875609394b7aa52c793fe133c1d10a970f64cc57cff69fe89f21342e30c3',
    'cross-day-source-original-coverage.json': '4780f1b69db3d5b7fef1d599ce88819d80fe84fbf5d002f1f21ff00b64672180',
    'cross-day-gate-rebuilt-release-input.json': 'bae92100e98b4431d8084f0911fa420f240849f6e7eff4565a361ac4199fed7e',
    'cross-day-rebuilt-public-coverage.json': '56b42229af9d56a739791e72faeda61ebd7c54122a729a5fabc14364b54b8c14',
    'cross-day-rebuilt-artifact-inventory.json': 'b5df9e0a2b756d697f3fde8831762429c04e0e74330603b846c824d787ccfe2a',
}


def fixture(name):
    raw = gzip.decompress((FIXTURES / (name + '.gz')).read_bytes())
    probe.require(probe.digest(raw) == PINS[name], 'Retained fixture differs')
    return json.loads(raw)


def actual(name): return json.loads((ACTUAL / (name + '.json')).read_bytes())


class Response(io.BytesIO):
    def __init__(self, body, url, status=200):
        super().__init__(body)
        self.url, self.status = url, status
        self.headers = {'Content-Length': '999999999'}  # Cannot grant a larger allowance.
        self.reads = []
    def read(self, count=-1):
        self.reads.append(count)
        return super().read(count)


class CoverageReaderTests(unittest.TestCase):
    def setUp(self):
        denied = patch.object(socket.socket, 'connect', side_effect=AssertionError('No network in fixtures'))
        denied.start(); self.addCleanup(denied.stop)
        self.body = gzip.decompress((ACTUAL / 'public-daily-coverage.json.gz').read_bytes())
        self.assertEqual(len(self.body), 1337257)
        self.assertEqual(probe.digest(self.body), 'ac8068379c6c79760331711bfb7bb6387fbc639f9ab6f921713502c6982d47fc')
        self.entry = {'path': probe.PUBLIC_COVERAGE_PATH, 'bytes': len(self.body), 'sha256': probe.digest(self.body)}
        self.contract = json.loads((ROOT / 'contracts/market.json').read_bytes())
        self.manifest = actual('release')['manifest']; self.production = actual('production')
        self.test = actual('gate-receipt'); self.inventory = actual('accepted-artifact-inventory')
        self.plan = fixture('current-original-plan.json'); self.coverage = fixture('current-original-coverage.json')
        self.reads, self.events = [], []
        self.reader = probe.get_json
        self.entries = {'heads/latest-run.json': actual('latest'),
            'heads/worker-heartbeat.json': actual('worker-heartbeat'), 'heads/production.json': self.production,
            'releases/' + self.manifest['releaseId'] + '.json': {'manifest': self.manifest},
            'gate-receipts/40172376435.json': self.test,
            actual('latest')['receipt']['key']: self.coverage,
            self.manifest['artifact']['inventory']['key']: self.inventory,
            'runs/' + self.plan['runId'] + '/plan.json': self.plan,
            'heads/dailySnapshot.json': fixture('current-original-snapshot.json')}
        self.live = {probe.PUBLIC_COVERAGE_URL: self.body}
        for name in ('deployment-receipt', 'app-release'):
            self.live['https://securitymarketpulse.com/' + name + '.json'] = gzip.decompress((ACTUAL / ('public-' + name + '.json.gz')).read_bytes())
        self.live['https://securitymarketpulse.com/factual-corrections.json'] = gzip.decompress(
            (FIXTURES/'current-accepted-factual-corrections.json.gz').read_bytes())
        self.assertEqual(probe.digest(self.live['https://securitymarketpulse.com/factual-corrections.json']),
                         PINS['current-accepted-factual-corrections.json'])
        owner = self
        class Authority:
            def verify_test_receipt(_, receipt, artifact):
                owner.events.append('authority_verified')
                owner.assertEqual(receipt, owner.test); owner.assertEqual(artifact, owner.manifest['artifact'])
                return True
        self.authority = Authority()

    def read_archive(self, key, reference=None):
        self.reads.append(key)
        if key == self.manifest['artifact']['inventory']['key']:
            self.assertIn('authority_verified', self.events)
        value = self.entries[key]
        if reference is not None:
            raw = probe.canonical(value)
            self.assertEqual((probe.digest(raw), len(raw)), (reference['sha256'], reference['bytes']))
        return copy.deepcopy(value)

    def live_read(self, url, **kwargs):
        response = Response(self.live[url], url)
        with patch.object(probe.urllib.request, 'urlopen', return_value=response) as opener:
            result = self.reader(url, **kwargs)
        self.assertEqual(opener.call_args.kwargs['timeout'], 25)
        self.events.append(('read', url, response.reads))
        return result

    def inspect(self, now=NOW):
        return probe.inspect(self.contract, self.read_archive, self.live_read, now, self.authority)

    def direct(self, body=None, entry=None, url=None, status=200, final=None):
        url = url or probe.PUBLIC_COVERAGE_URL
        response = Response(self.body if body is None else body, final or url, status)
        with patch.object(probe.urllib.request, 'urlopen', return_value=response):
            result = probe.get_json(url, expected=self.entry if entry is None else entry)
        return result, response

    def test_actual_large_response_uses_exact_authenticated_bound_and_keeps_clocks(self):
        result, response = self.direct()
        self.assertEqual(result, json.loads(self.body)); self.assertEqual(response.reads, [1337258])
        response = Response(self.body, probe.PUBLIC_COVERAGE_URL)
        with patch.object(probe.urllib.request, 'urlopen', return_value=response):
            with self.assertRaisesRegex(ValueError, 'exceeds byte budget'): probe.get_json(probe.PUBLIC_COVERAGE_URL)
        self.assertEqual(response.reads, [1000001])

    def test_short_long_and_changed_bytes_fail_before_json_interpretation(self):
        for body in (self.body[:-1], self.body+b' ', b'X'+self.body[1:]):
            with self.subTest(length=len(body)), self.assertRaises(ValueError): self.direct(body)

    def test_invalid_json_cannot_pass_even_with_matching_size_and_hash(self):
        body=b'{broken'
        entry={**self.entry,'bytes':len(body),'sha256':probe.digest(body)}
        with self.assertRaises(json.JSONDecodeError): self.direct(body,entry)

    def test_redirect_and_non_200_remain_rejected(self):
        for status, final in ((203,None),(304,None),(200,probe.PUBLIC_COVERAGE_URL+'?changed'),
                              (200,probe.PUBLIC_COVERAGE_URL.replace('securitymarketpulse.com','evil.invalid'))):
            with self.subTest(status=status,final=final), self.assertRaises(ValueError): self.direct(status=status,final=final)

    def test_no_other_receipt_or_untrusted_url_gets_a_larger_limit(self):
        for name in ('app-release','deployment-receipt','factual-corrections'):
            url='https://securitymarketpulse.com/'+name+'.json'; response=Response(self.body,url)
            with patch.object(probe.urllib.request,'urlopen',return_value=response):
                with self.assertRaises(ValueError):probe.get_json(url)
            self.assertEqual(response.reads,[1000001])
        for url in ('https://evil.invalid/daily-coverage.json',probe.PUBLIC_COVERAGE_URL+'?x',
                    probe.PUBLIC_COVERAGE_URL+'#x',probe.PUBLIC_COVERAGE_URL.replace('.com/','.com:443/')):
            with patch.object(probe.urllib.request,'urlopen',side_effect=AssertionError('invalid bound reached transport')):
                with self.assertRaises(ValueError):probe.get_json(url,expected=self.entry)

    def test_invalid_entry_types_shapes_hashes_and_absolute_ceiling_fail_before_io(self):
        cases=[[],{}, {**self.entry,'extra':True},{**self.entry,'path':'daily-coverage.json'},
               {**self.entry,'sha256':'0'}, {**self.entry,'sha256':True}]
        cases += [{**self.entry,'bytes':v} for v in (True,0,-1,1.0,'1337257',40_000_001)]
        for entry in cases:
            with self.subTest(entry=entry),patch.object(probe.urllib.request,'urlopen',side_effect=AssertionError('invalid entry reached transport')):
                with self.assertRaises(ValueError):probe.get_json(probe.PUBLIC_COVERAGE_URL,expected=entry)

    def test_production_manifest_identity_and_sequence_are_verified(self):
        probe._accepted_release(self.production,self.manifest,self.contract)
        for key,value in (('releaseId','0'*64),('sequence',True),('sequence',99)):
            head={**self.production,key:value}
            with self.subTest(key=key),self.assertRaises(ValueError):probe._accepted_release(head,self.manifest,self.contract)
        for key,value in (('runId','changed'),('contractSha256','0'*64),('schemaVersion',True)):
            manifest={**self.manifest,key:value}
            with self.subTest(key=key),self.assertRaises(ValueError):probe._accepted_release(self.production,manifest,self.contract)

    def test_bad_inventory_references_and_gate_joins_fail_before_archive_io(self):
        ref=self.manifest['artifact']['inventory']
        refs=[None,{}, {**ref,'extra':True},{**ref,'key':'objects/'+'0'*64},
              {**ref,'sha256':'0'*64},{**ref,'sha256':True}]
        refs += [{**ref,'bytes':v} for v in (True,0,-1,1.0,'9441',40_000_001)]
        for reference in refs:
            manifest=copy.deepcopy(self.manifest);manifest['artifact']['inventory']=reference
            with self.subTest(reference=reference):
                with self.assertRaises(ValueError):probe._accepted_coverage_inventory(manifest,self.test,lambda *a,**k:self.fail('invalid ref reached archive'))
        for key,value in (('artifactSha256','0'*64),('appRevision','0'*40),('snapshotSha256','0'*64),
                          ('contractSha256','0'*64),('runId','wrong'),('githubRunId',True),('githubArtifactId',99)):
            test={**self.test,key:value}
            with self.subTest(key=key),self.assertRaises(ValueError):
                probe._accepted_coverage_inventory(self.manifest,test,lambda *a,**k:self.fail('invalid gate reached archive'))

    def test_inventory_hash_and_exact_path_entry_are_required(self):
        with self.assertRaises(ValueError):
            probe._accepted_coverage_inventory(self.manifest,self.test,lambda *a,**k:self.inventory+[self.entry])
        bad_entries=[[],[self.entry,self.entry],[{**self.entry,'path':'other/daily-coverage.json'}],
                     [{**self.entry,'bytes':True}],[{**self.entry,'bytes':0}],[{**self.entry,'bytes':40_000_001}],
                     [{**self.entry,'sha256':'bad'}],[{**self.entry,'extra':True}]]
        for inventory in bad_entries:
            raw=probe.canonical(inventory);manifest=copy.deepcopy(self.manifest);test=copy.deepcopy(self.test)
            manifest['artifact']['sha256']=probe.digest(raw)
            manifest['artifact']['inventory']={'key':'objects/'+probe.digest(raw),'sha256':probe.digest(raw),'bytes':len(raw)}
            test['artifactSha256']=probe.digest(raw)
            with self.subTest(inventory=inventory),self.assertRaises(ValueError):
                probe._accepted_coverage_inventory(manifest,test,lambda *a,**k:inventory)

    def test_full_actual_inspection_reaches_honest_backlog_and_held_claim_reasons(self):
        result=self.inspect()
        self.assertFalse(result['healthy'])
        for reason in ('DAILY_INTAKE_INCOMPLETE','PROCESSING_PENDING_10617','PROCESSING_HELD_10',
                       'HISTORICAL_REVIEW_PENDING_10616','PUBLIC_DAILY_INTAKE_INCOMPLETE',
                       'PUBLIC_PROCESSING_PENDING_10617','PUBLIC_PROCESSING_HELD_10',
                       'PUBLIC_HISTORICAL_REVIEW_PENDING_10616','HELD_CLAIMS_37'):
            self.assertIn(reason,result['reasons'])
        self.assertNotIn('SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED',result['reasons'])
        self.assertNotIn('PUBLIC_SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED',result['reasons'])
        self.assertNotIn('INDEPENDENT_PROBE_FAILED',result['reasons'])
        self.assertEqual(next(e[2] for e in self.events if isinstance(e,tuple) and e[1]==probe.PUBLIC_COVERAGE_URL),[1337258])
        combined=set(result['reasons'])|set(actual('actual-monitor-result')['reasons'][:6])
        self.assertIn('SCHEDULED_COLLECTION_RECEIPT_DIFFERS',combined)

    def test_no_authority_means_no_inventory_allowance_and_failed_authority_stops(self):
        with patch.object(self.authority,'verify_test_receipt',return_value=False):
            with self.assertRaisesRegex(ValueError,'AUTHORITY_REQUIRED'):self.inspect()
        self.assertNotIn(self.manifest['artifact']['inventory']['key'],self.reads)
        with self.assertRaisesRegex(ValueError,'exceeds byte budget'):
            probe.inspect(self.contract,self.read_archive,self.live_read,NOW)
        self.assertNotIn(self.manifest['artifact']['inventory']['key'],self.reads)

    def test_current_and_cross_day_original_plans_keep_real_clocks_and_specific_alarms(self):
        current=json.loads(self.body);current_before=copy.deepcopy(current)
        self.assertNotIn('SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED',probe.separate_health(self.contract,current,public=True,plan=self.plan)[0])
        old_plan=fixture('cross-day-original-plan.json')
        original=fixture('cross-day-source-original-coverage.json')
        rebuilt=fixture('cross-day-gate-rebuilt-release-input.json')['coverage']
        public=fixture('cross-day-rebuilt-public-coverage.json')
        self.assertEqual(original['checkedAt'],'2026-10-24T18:32:56.227836Z')
        self.assertEqual(rebuilt['checkedAt'],'2026-10-25T00:59:59.916017Z')
        self.assertEqual(public['checkedAt'],'2026-10-25T01:00:34.491456Z')
        expected={'DAILY_INTAKE_INCOMPLETE','PROCESSING_PENDING_10632','PROCESSING_HELD_5','HISTORICAL_REVIEW_PENDING_10631'}
        for coverage,is_public in ((original,False),(rebuilt,False),(public,True)):
            before=copy.deepcopy(coverage)
            self.assertEqual(set(probe.separate_health(self.contract,coverage,public=is_public,plan=old_plan)[0]),expected)
            self.assertEqual(coverage,before)
        for coverage,is_public in ((rebuilt,False),(public,True)):
            wrong=probe.plan_run(self.contract,coverage['checkedAt'])
            self.assertIn('SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED',probe.separate_health(self.contract,coverage,public=is_public,plan=wrong)[0])
        self.assertEqual(current,current_before)

    def test_invalid_or_missing_original_plans_and_source_joins_fail_closed(self):
        original=copy.deepcopy(self.plan)
        mutations=[lambda p:p.update(runId='0'*64),lambda p:p.update(contractSha256='0'*64),
                   lambda p:p.update(inventorySha256='0'*64),lambda p:p.update(scheduledAt='2026-10-26T00:00:00Z'),
                   lambda p:p.update(extra=True),lambda p:p['tasks'][0].update(supplierId='wrong'),
                   lambda p:p['tasks'][0].update(sourceId='wrong'),lambda p:p['tasks'].pop(),
                   lambda p:p['supplierIds'].pop()]
        for mutate in mutations:
            plan=copy.deepcopy(original);mutate(plan)
            with self.subTest(mutate=mutate):
                self.assertIn('SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED',probe.separate_health(self.contract,self.coverage,plan=plan)[0])
        for plan in (None,{},[]):
            self.assertIn('SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED',probe.separate_health(self.contract,self.coverage,plan=plan)[0])
        for run_id in ('../escape','wrong',True,None):
            coverage={**self.coverage,'runId':run_id}
            with self.subTest(runId=run_id):
                self.assertIn('SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED',probe.separate_health(self.contract,coverage,read_archive=lambda *a,**k:self.fail('invalid run constructed archive path'))[0])
        public=json.loads(self.body);public['scheduledAt']='2026-10-25T00:00:00Z'
        self.assertIn('SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED',probe.separate_health(self.contract,public,public=True,plan=self.plan)[0])

    def test_expired_public_source_is_not_refreshed_by_a_successful_bounded_read(self):
        before=json.loads(self.body)
        result=self.inspect(now='2026-10-27T00:00:00Z')
        self.assertFalse(result['healthy']);self.assertIn('PUBLIC_COVERAGE_INCOMPLETE_OR_OVERDUE',result['reasons'])
        self.assertEqual(json.loads(self.body),before)

    def test_newer_private_and_older_rehearsal_public_load_their_own_original_plans(self):
        # This isolates routing with real retained H data/plans, not an actual
        # older H production acceptance. The older public bytes came from rehearsal.
        public=fixture('cross-day-rebuilt-public-coverage.json')
        old_plan=fixture('cross-day-original-plan.json')
        before=copy.deepcopy(public)
        self.entries['runs/'+old_plan['runId']+'/plan.json']=old_plan
        app={'appRevision':'a'*40,'dailySnapshotSha256':'b'*64}
        self.entries['heads/production.json']={'releaseId':'routing-fixture'}
        self.entries['releases/routing-fixture.json']={'manifest':{'appRevision':app['appRevision'],'snapshot':{'sha256':app['dailySnapshotSha256']}}}
        def live(url):
            if url==probe.PUBLIC_COVERAGE_URL:return copy.deepcopy(public)
            if url.endswith('/app-release.json'):return app
            return {'syntheticRoutingOnly':True}
        with patch.object(probe,'verify_acknowledgement'):
            result=probe.inspect(self.contract,self.read_archive,live,NOW)
        self.assertFalse(result['healthy'])
        self.assertIn('COLLECTION_HAS_NOT_REACHED_PRODUCTION',result['reasons'])
        self.assertIn('PUBLIC_PROCESSING_PENDING_10632',result['reasons'])
        self.assertNotIn('PUBLIC_SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED',result['reasons'])
        self.assertIn('runs/'+self.plan['runId']+'/plan.json',self.reads)
        self.assertIn('runs/'+old_plan['runId']+'/plan.json',self.reads)
        self.assertEqual(public,before)

    def test_complete_main_loop_retains_actual_timer_and_partial_alarms_without_generic_failure(self):
        original=actual('actual-monitor-result')
        collection={**original,'reasons':original['reasons'][:6]}
        collection.pop('notification',None)
        archive_commit=actual('archive-ref')['object']['sha']
        def api(path,raw=False):
            if path=='git/ref/archive/market-evidence':return {'object':{'sha':archive_commit}}
            prefix='contents/state/'
            self.assertTrue(raw and path.startswith(prefix))
            key=path[len(prefix):].split('?ref=')[0]
            return probe.canonical(self.entries[key])
        output=io.StringIO()
        with patch.object(probe,'api',side_effect=api),patch.object(probe,'utcnow',return_value=NOW),\
             patch.object(probe,'inspect_collection',return_value=collection),\
             patch.object(probe,'inspect_corrections',return_value=[]),\
             patch.object(probe,'GitHubAuthority',return_value=self.authority),\
             patch.object(probe,'get_json',side_effect=self.live_read),patch('sys.argv',['probe.py']),redirect_stdout(output):
            self.assertEqual(probe.main(),2)
        result=json.loads(output.getvalue())
        self.assertFalse(result['healthy']);self.assertIn('SCHEDULED_COLLECTION_RECEIPT_DIFFERS',result['reasons'])
        self.assertIn('HELD_CLAIMS_37',result['reasons']);self.assertNotIn('INDEPENDENT_PROBE_FAILED',result['reasons'])


if __name__=='__main__':unittest.main()
