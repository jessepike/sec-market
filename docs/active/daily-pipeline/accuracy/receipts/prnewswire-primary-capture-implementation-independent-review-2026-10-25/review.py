import os,sys,json,copy,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
O=Path('/var/tmp/smp-prn-primary-implementation-independent-20261025');O.mkdir(exist_ok=True)
ROOT=Path('/mnt/mac/Users/jessepike/.codex/worktrees/prn-current-primary/sec-market')
ARCHIVE=Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted')
ABSENT='--absent' in sys.argv;sys.dont_write_bytecode=True
os.chdir(ROOT);sys.path[:0]=[str(ROOT/'ops/ci'),str(ROOT/'web/scripts/pipeline')];tempfile.tempdir=str(O)
blocked=[]
def audit(event,args):
    if event in ('socket.connect','subprocess.Popen'):raise AssertionError('NO_NETWORK_OR_PROCESS:'+event)
    if event=='open':
        p,mode,flags=args
        if isinstance(p,(str,bytes,os.PathLike)):
            name=os.fsdecode(p)
            if ABSENT and name.startswith(str(ARCHIVE)):
                blocked.append(name);raise AssertionError('NO_FROZEN_READ')
            writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
            if writing and not name.startswith(str(O)+'/'):raise AssertionError('WRITE_OUTSIDE_SCRATCH:'+name)
sys.addaudithook(audit)
exists=Path.exists
if ABSENT:Path.exists=lambda self:False if str(self).startswith(str(ARCHIVE)) else exists(self)
import test_prnewswire_primary_capture as worker
import prnewswire_primary_capture as op
from contracts import digest,canonical
from storage import LocalStore
original_init=LocalStore.__init__
def local_init(self,root,*args,**kwargs):
    if not str(Path(root).resolve()).startswith(str(O)+'/'):raise AssertionError('FROZEN_LOCALSTORE_DENIED')
    return original_init(self,root,*args,**kwargs)
LocalStore.__init__=local_init
extra=[]
class Independent(unittest.TestCase):
    def fixture(self):
        f=worker.CaptureTests('runTest');f.setUp();self.addCleanup(f.doCleanups);return f
    def test_saturated_models_documents_two_fetches_only(self):
        f=self.fixture();f.local.compare_and_swap('budget-2026-10-25',None,{'calls':80,'documents':40,'fetches':1511});r=f.capture();f.replay(r)
        self.assertEqual(r['reservationContext']['currentBudget'],{'calls':80,'documents':40,'fetches':1513})
        self.assertEqual(f.fetcher.calls,[(x['sourceId'],x['url'],None,2) for x in f.plan['sources']])
        self.assertEqual(len(r['results']),2);self.assertEqual(r['acceptedSamples'],2)
        for key,v in f.normal.items():self.assertEqual(f.local.read(key),v)
        self.assertFalse(r['qualified']);self.assertEqual(r['facts'],[]);extra.append('1511/80/40 -> 1513/80/40; ordered exact two requests, normal heads unchanged')
    def test_deadline_after_first_response_does_not_charge_second(self):
        f=self.fixture();budget=f.budget()
        def stop():budget.deadline=0
        r=f.capture(worker.ResponseFetcher(f,callback=stop),budget);f.replay(r)
        self.assertEqual(len(f.fetcher.calls),1);self.assertEqual(r['reservationContext']['probeFetchReservations'],1)
        self.assertIsNone(r['requests'][1]['reservation']);self.assertIsNone(r['requests'][1]['requestedAt'])
        self.assertIsNotNone(r['results'][0]['body']);self.assertIsNone(r['results'][1]['body']);self.assertFalse(r['proposalEvidenceComplete'])
        extra.append('Deadline after first response: one actual call and charge; second unrequested; first raw body retained')
    def test_every_report_field_omission_rejects(self):
        f=self.fixture();r=f.capture();count=0
        for key in r:
            p=copy.deepcopy(r);del p[key]
            with self.assertRaises((ValueError,TypeError,KeyError)):f.replay(p)
            count+=1
        extra.append({'missingReportFieldsRejected':count})
    def test_exact_whole_policy_order_and_raw_plan_boundary(self):
        f=self.fixture();old=op.origin.inverse_policy(f.contract,f.base)
        with self.assertRaises(ValueError):op.validate_plan(old,f.base,f.raw)
        p=copy.deepcopy(f.plan);p['sources'].reverse()
        for raw in (f.raw+b'\n',canonical(p),canonical({**f.plan,'extra':None})):
            with self.assertRaises(ValueError):op.validate_plan(f.contract,f.base,raw)
        for mutate in (lambda c:c.update(extra=None),lambda c:c['sources'][0].update(extra=None),lambda c:c['sources'][0].update(allowedHosts=['evil.test'])):
            c=copy.deepcopy(f.contract);mutate(c)
            with self.assertRaises(ValueError):op.validate_plan(c,f.base,f.raw)
        extra.append('H/current-J separation, whole policy/host/extra fields, reversed ordered targets and raw plan whitespace rejected')
    def test_scope_and_original_clocks_are_replayed_without_history_overclaim(self):
        f=self.fixture();n=op.validate_plan(f.contract,f.base,f.raw);c,ch=n['streams']
        self.assertEqual((len(c['records']),len(c['items']),len(c['knownEvidenceUnion']),len(c['currentWindowItems'])),(125,125,127,2))
        self.assertFalse(c['sourceScopeComplete']);self.assertFalse(c['historicalEnumerationComplete']);self.assertEqual(len(c['knownSeedsOutsideObservedList']),2)
        self.assertEqual((len(ch['records']),len(ch['items']),len(ch['currentWindowItems'])),(47,47,5))
        self.assertEqual(c['asOf'],worker.AS_OF);self.assertEqual(ch['asOf'],worker.AS_OF)
        self.assertEqual([t['sample']['calendarDay'] for t in n['targets']],['2026-10-06','2026-10-14'])
        self.assertEqual([t['sample']['cardIndex'] for t in n['targets']],[1,0])
        extra.append({'CatoList':125,'CatoUnion':127,'olderMissingSeeds':2,'CatoCurrent':2,'ChainguardList':47,'ChainguardCurrent':5,'asOf':worker.AS_OF})
    def test_modification_values_and_unknown_numeric_offset_are_preserved(self):
        f=self.fixture();r=f.capture();f.replay(r)
        for row,target in zip(r['results'],f.plan['sources']):
            shape=row['primaryShape'];self.assertIsNone(shape['indexTimezone']);self.assertEqual(shape['publicationCalendarDay'],target['selectedRecord']['calendarDay'])
            self.assertEqual(shape['suppliedJsonLd']['dateModified'],target['selectedRecord']['calendarDay']+'T02:00:00')
        extra.append('Written calendar dates and supplied modification literals preserved; ET gains no invented offset')
    def test_all_portable_payloads_equal_actual_manifest_if_present(self):
        if ABSENT:self.skipTest('Actual manifest comparison only; all portable capture cases still execute')
        fixture=worker.FixtureStore();mraw=(ARCHIVE/'archive-manifest.json').read_bytes();self.assertEqual(digest(mraw),'13d956802cd881c0d6805c00c0dee48de07bd6615196e69f74fbf4056a710e34');entries={x['key']:x for x in json.loads(mraw)['files']};seals=[]
        for key,row in fixture.rows.items():
            raw=fixture.raw(key);p=ARCHIVE/('state/'+key);st=p.stat();self.assertEqual(raw,p.read_bytes());self.assertEqual(entries['state/'+key],row['entry'])
            self.assertEqual((st.st_ino,st.st_size,st.st_mtime_ns),(p.stat().st_ino,p.stat().st_size,p.stat().st_mtime_ns))
            seals.append({'path':str(p),'sha256':digest(raw),'bytes':len(raw),'mtimeNs':st.st_mtime_ns,'inode':st.st_ino})
        self.assertEqual(len(seals),63);(O/'portable-actual-seals.json').write_text(json.dumps(seals,sort_keys=True));extra.append({'portableActualEntriesAuthenticated':63})
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(worker),unittest.defaultTestLoader.loadTestsFromTestCase(Independent)])
result=unittest.TextTestRunner(verbosity=2).run(suite)
summary={'status':'PASS' if result.wasSuccessful() else 'FAIL','absent':ABSENT,'testsRun':result.testsRun,'passed':result.testsRun-len(result.skipped)-len(result.failures)-len(result.errors),'skipped':[(str(t),r) for t,r in result.skipped],'failures':[(str(t),s) for t,s in result.failures],'errors':[(str(t),s) for t,s in result.errors],'frozenReadAttempts':blocked,'extraResults':extra,'sourceRequests':0,'models':0,'frozenWrites':0,'scope':'offline dormant build review'}
(O/('absent.json' if ABSENT else 'present.json')).write_text(json.dumps(summary,indent=2,sort_keys=True));print(json.dumps({k:summary[k] for k in ('status','testsRun','passed','skipped','frozenReadAttempts')}));sys.exit(not result.wasSuccessful())
