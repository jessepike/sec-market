import os,sys,json,copy,unittest,socket,tempfile
from pathlib import Path
from unittest.mock import patch
O=Path('/var/tmp/smp-cyera-implementation-independent-20261025')
O.mkdir(exist_ok=True)
ROOT=Path('/mnt/mac/Users/jessepike/.codex/worktrees/cyera-current-primary/sec-market')
ARCHIVE=Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted')
ABSENT='--absent' in sys.argv
sys.dont_write_bytecode=True
os.chdir(ROOT);sys.path[:0]=[str(ROOT/'ops/ci'),str(ROOT/'web/scripts/pipeline')]
tempfile.tempdir=str(O)
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
import test_cyera_press_list as parser_test
import test_cyera_primary_capture as capture_test
from contracts import digest,canonical
from storage import LocalStore
import cyera_primary_capture as op
import cyera_press_list as parser
real_init=LocalStore.__init__
def local_init(self,root,*a,**kw):
    if not str(Path(root).resolve()).startswith(str(O)+'/'):raise AssertionError('FROZEN_LOCALSTORE_DENIED')
    return real_init(self,root,*a,**kw)
LocalStore.__init__=local_init
extra=[]
class Independent(unittest.TestCase):
    def fixture(self):
        f=capture_test.CaptureTests('runTest');f.setUp();self.addCleanup(f.doCleanups);return f
    def test_saturated_model_and_document_budget_changes_fetch_only(self):
        f=self.fixture();f.local.compare_and_swap('budget-2026-10-25',None,{'calls':80,'documents':39,'fetches':1511})
        before={k:f.local.read(k) for k in f.normal};r=f.capture();f.replay(r)
        self.assertEqual(r['reservationContext']['initialBudget'],{'calls':80,'documents':39,'fetches':1511})
        self.assertEqual(r['reservationContext']['currentBudget'],{'calls':80,'documents':39,'fetches':1512})
        self.assertFalse(r['qualified']);self.assertFalse(r['coverageCredit']);self.assertEqual(r['facts'],[])
        self.assertEqual({k:f.local.read(k) for k in f.normal},before);extra.append('1511/80/39 -> 1512/80/39; no normal heads changed')
    def test_every_report_field_missing_rejected(self):
        f=self.fixture();r=f.capture();count=0
        for field in r:
            changed=copy.deepcopy(r);del changed[field]
            with self.assertRaises((ValueError,TypeError,KeyError)):f.replay(changed)
            count+=1
        extra.append({'missingReportFieldsRejected':count})
    def test_all_referenced_raw_whitespace_is_authenticated(self):
        f=self.fixture();base=f.base
        referenced=[]
        class Recording:
            def read(self,key):return base.read(key)
            def get(self,ref):referenced.append(ref['key']);return base.get(ref)
        op.validate_plan(f.contract,Recording(),f.raw)
        class Altered:
            def __init__(self,key):self.key=key
            def read(self,key):return base.read(key)
            def get(self,ref):return base.get(ref)+(b' ' if ref['key']==self.key else b'')
        count=0
        for key in sorted(set(referenced)):
            with self.assertRaises((ValueError,TypeError,KeyError,AssertionError)):
                op.validate_plan(f.contract,Altered(key),f.raw)
            count+=1
        extra.append({'rawReferencedWhitespaceSubstitutionsRejected':count,'semanticHeadChangesCoveredSeparately':True})
    def test_exact_policy_whole_objects_and_original_plan_required(self):
        f=self.fixture();old=op.origin.inverse_policy(f.contract,f.base)
        with self.assertRaises(ValueError):op.validate_plan(old,f.base,f.raw)
        for mutation in (lambda c:c.update(extra=None),lambda c:c['sources'][0].update(extra=None),lambda c:c['sources'][0].update(allowedHosts=['evil.test'])):
            c=copy.deepcopy(f.contract);mutation(c)
            with self.assertRaises(ValueError):op.validate_plan(c,f.base,f.raw)
        with self.assertRaises(ValueError):op.validate_plan(f.contract,f.base,f.raw+b'\n')
        extra.append('whole J/H boundary, unknown root/source keys/host substitution and raw plan whitespace rejected')
    def test_unclosed_and_inert_card_subtrees_rejected(self):
        body=parser_test.page([parser_test.card(),parser_test.card(2,'Sep 22, 2026')])
        bads=[body.replace(b'<h3>',b'<h3><span>',1),body.replace(b'</h3>',b'<span></h3>',1),body.replace(b'<div class="card_date">',b'<div class="card_date"><span>',1),body.replace(b'</a>',b'<span hidden></span></a>',1)]
        for raw in bads:
            with self.assertRaises(ValueError):parser.parse_press_list(raw,parser.SOURCE,parser_test.AS_OF)
        valid=body.replace(b'<h3>',b'<h3><span>',1).replace(b'</h3>',b'</span></h3>',1)
        self.assertEqual(len(parser.parse_press_list(valid,parser.SOURCE,parser_test.AS_OF)['records']),2)
        extra.append({'ambiguousCardSubtreeNegatives':len(bads),'closedNestedTitlePositive':True})
    def test_dated_seed_membership_uses_dom_order_and_no_inferred_timezone(self):
        base=parser_test.FixtureStore();p=json.loads(parser_test.PLAN.read_bytes());idx=p['retainedIndex']
        stream=parser.parse_press_list(base.get(idx['body']),parser.SOURCE,idx['fetchedAt'],30,idx['knownSeedUrls'])
        matched=[r['url'] for r in stream['records'] if r['url'] in idx['knownSeedUrls']]
        self.assertEqual(digest(matched),'055a5fd979ed3309d7104665970231ff3052ea52bc56bcbc1444e167caf21949')
        self.assertEqual(len(canonical(matched)),599);self.assertTrue(all(r['timezone'] is None for r in stream['records']))
        self.assertEqual(len(stream['records']),56);self.assertEqual(len(stream['currentWindowItems']),1)
        self.assertEqual(stream['windowStart'],'2026-09-25');self.assertEqual(stream['windowEnd'],'2026-10-25')
        extra.append({'rows':56,'current':1,'historical':55,'matchedSeeds':5,'membershipBytes':599,'timezone':None})
    def test_portable_payloads_equal_manifest_and_bytes_if_present(self):
        if ABSENT:self.skipTest('Actual manifest comparison only; portable hash checks run in 22 core tests')
        fixture=parser_test.FixtureStore();manifest=json.loads((ARCHIVE/'archive-manifest.json').read_bytes());entries={r['key']:r for r in manifest['files']};seals=[]
        for key,row in fixture.rows.items():
            raw=fixture.raw(key);path=ARCHIVE/('state/'+key);before=path.stat();actual=path.read_bytes()
            self.assertEqual(entries['state/'+key],row['entry']);self.assertEqual(raw,actual)
            self.assertEqual((before.st_ino,before.st_mtime_ns,before.st_size),(path.stat().st_ino,path.stat().st_mtime_ns,path.stat().st_size))
            seals.append({'path':str(path),'sha256':digest(actual),'bytes':len(actual),'mtimeNs':before.st_mtime_ns,'inode':before.st_ino})
        (O/'portable-payload-actual-seals.json').write_text(json.dumps(seals,sort_keys=True))
        self.assertEqual(len(seals),17);extra.append({'portableActualEntriesCompared':17})
suite=unittest.TestSuite()
for module in (parser_test,capture_test):suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(Independent))
result=unittest.TextTestRunner(verbosity=2).run(suite)
summary={'status':'PASS' if result.wasSuccessful() else 'FAIL','absent':ABSENT,'testsRun':result.testsRun,'passed':result.testsRun-len(result.skipped)-len(result.errors)-len(result.failures),'skipped':[(str(t),r) for t,r in result.skipped],'errors':[(str(t),e) for t,e in result.errors],'failures':[(str(t),e) for t,e in result.failures],'frozenReadAttempts':blocked,'extraResults':extra,'sourceRequests':0,'modelCalls':0,'frozenWrites':0,'authority':'offline review only'}
(O/('review-absent.json' if ABSENT else 'review-present.json')).write_text(json.dumps(summary,indent=2,sort_keys=True))
print(json.dumps({k:summary[k] for k in ('status','absent','testsRun','passed','skipped','frozenReadAttempts')}))
sys.exit(not result.wasSuccessful())
