import hashlib,json,os,socket,sys,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
OUT=Path(__file__).resolve().parent;ROOT=OUT/'source'
ARCHIVE=Path('/var/tmp/smp-oct27-native-40489959161/capture/extracted')
MANIFEST='3aca334fd331a89142cae4efeaa06eab5922c6b38eb8ac53f88aae1ac2861503'
ACK='ac082a358d1ce897854d9a08a964bdfbd335a06e'
sys.dont_write_bytecode=True
sys.path[:0]=[str(ROOT/'ops/ci'),str(ROOT/'web/scripts/pipeline')]
(OUT/'scratch').mkdir(exist_ok=True);tempfile.tempdir=str(OUT/'scratch')
def digest(raw):return hashlib.sha256(raw).hexdigest()
def pin(path):
 raw=path.read_bytes();s=path.stat();return {'sha256':digest(raw),'bytes':len(raw),'mtimeNs':s.st_mtime_ns}
def save(name,data):(OUT/name).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
manifest=(ARCHIVE/'archive-manifest.json').read_bytes();assert digest(manifest)==MANIFEST
entries={row['key']:row for row in json.loads(manifest)['files']};assert len(entries)==62602
proof_raw=(ARCHIVE.parent/'download-proof.json').read_bytes();proof=json.loads(proof_raw)
assert proof['allManifestEntriesVerified'] is True and proof['archiveAck']['commit']==ACK and proof['manifestSha256']==MANIFEST
(OUT/'archive-download-proof.json').write_bytes(proof_raw)
reads={}
class ReadOnly:
 def raw(self,key):
  name='state/'+key;path=ARCHIVE/name
  assert not path.is_symlink() and path.resolve().is_relative_to(ARCHIVE)
  raw=path.read_bytes();row=entries[name]
  assert digest(raw)==row['sha256'] and len(raw)==row['bytes']
  reads.setdefault(name,pin(path));return raw
 def get(self,ref):
  raw=self.raw(ref['key']);assert digest(raw)==ref['sha256'] and len(raw)==ref['bytes'];return raw
 def read(self,key):return json.loads(self.raw(key))
heads={key:pin(ARCHIVE/key) for key in entries if key.startswith('state/heads/')}
from storage import LocalStore
from fetcher import Fetcher
from agents import SubscriptionAgent
from onboarding import PersistentProbeBudget
import prnewswire_primary_capture as operation
from test_prnewswire_retained_window import replay_complete
attempts=[]
def audit(event,args):
 if event in ('socket.connect','subprocess.Popen'):
  attempts.append(event);raise AssertionError('NO_NETWORK_OR_PROCESS:'+event)
 if event=='open':
  path,mode,flags=args
  writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)
  if writing and isinstance(path,(str,bytes,os.PathLike)) and not Path(os.fsdecode(path)).resolve().is_relative_to(OUT):
   raise AssertionError('WRITE_OUTSIDE_ISOLATED_UNIT:'+str(path))
sys.addaudithook(audit)
raw=(ROOT/'contracts/source-qualification-probes.json').read_bytes()
assert digest(raw)=='01e468f5d73ddb28edbde014a0b725f7d202340a692964d01f6fd174faec7fb1'
contract=json.loads((ROOT/'contracts/market.json').read_bytes())
started=time.monotonic();store=ReadOnly()
with patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_LOCALSTORE')), \
     patch.object(Fetcher,'fetch',side_effect=AssertionError('NO_SOURCE_TRANSPORT')), \
     patch.object(SubscriptionAgent,'call',side_effect=AssertionError('NO_MODEL')), \
     patch.object(PersistentProbeBudget,'__init__',side_effect=AssertionError('NO_FRESH_BUDGET')):
 normalized=operation.validate_plan(contract,store,raw,ROOT/'contracts/source-qualification-probes.json')
 original=operation.origin.inverse_policy(contract,store)
 originals=[replay_complete(json.loads(store.get(item['record'])),original,store) for item in normalized['plan']['originalRuns']]
assert all(row['fullLegacyTraversalReplay'] and row['frozenWrites']==row['sourceRequests']==0 for row in originals)
preflight={'status':'PASS','archiveCommit':ACK,'manifestSha256':MANIFEST,'manifestFiles':len(entries),
 'selectedPlanRawSha256':digest(raw),'selectedPlanBytes':len(raw),'policyCanonicalSha256':operation.POLICY_SHA256,
 'operation':normalized['operation'],'maximumLogicalRequests':2,'originalAsOf':normalized['plan']['originalAsOf'],
 'targets':[{'sourceId':target['sourceId'],'family':target['source']['family'],'url':target['url'],
             'selectedRecord':target['sample']} for target in normalized['targets']],
 'streams':[{'sourceId':stream['sourceId'],'observedItems':len(stream['items']),
             'knownEvidenceUnion':len(stream['knownEvidenceUnion']),'currentWindowItems':stream['currentWindowItems'],
             'dailyWindowComplete':stream['dailyWindowComplete'],'historicalEnumerationComplete':stream['historicalEnumerationComplete'],
             'sourceScopeComplete':stream['sourceScopeComplete'],'knownSeedsOutsideObservedList':stream['knownSeedsOutsideObservedList']} for stream in normalized['streams']],
 'fullOriginalHReplays':originals,'sourceRequests':0,'modelCalls':0,'newReservations':0,'coverageCredit':False,
 'seconds':time.monotonic()-started,'allowanceClaim':'none; exact current shared-budget check remains root-owned before actual dispatch'}
save('current-actual-preflight.json',preflight)
import test_prnewswire_primary_capture as tests
names=['test_two_logical_gets_no_generic_candidates_or_other_credits',
       'test_changed_live_plan_or_failed_preflight_cannot_write_or_charge',
       'test_budget_binding_exclusivity_and_lease_context_denials_precede_transport',
       'test_shared_leased_caller_routes_directly_and_preserves_outer_zeros']
suite=unittest.TestSuite(tests.CaptureTests(name) for name in names)
with patch.object(SubscriptionAgent,'call',side_effect=AssertionError('NO_MODEL')):
 result=unittest.TextTestRunner(verbosity=2).run(suite)
assert result.wasSuccessful() and not result.skipped
for name,expected in reads.items():assert pin(ARCHIVE/name)==expected,name
for name,expected in heads.items():assert pin(ARCHIVE/name)==expected,name
assert digest((ARCHIVE/'archive-manifest.json').read_bytes())==MANIFEST
before=json.loads((OUT/'source-before.json').read_bytes())['files'];changed=[]
for name,old in before.items():
 path=ROOT/name;raw_now=path.read_bytes();new={'sha256':digest(raw_now),'bytes':len(raw_now)}
 if old!=new:changed.append(name)
assert changed==['contracts/source-qualification-probes.json'],changed
save('readset-before-after.json',{'consumed':reads,'unchangedHeads':heads,'frozenWrites':0})
save('verification-summary.json',{'status':'PASS','preflight':'current-actual-preflight.json','focusedTests':names,'testsPassed':result.testsRun,
 'skips':[],'sourceFiles':len(before),'unchangedOtherFiles':len(before)-1,'onlyChangedFile':changed[0],
 'consumedArchiveFiles':len(reads),'unchangedHeads':len(heads),'networkAttempts':attempts,'sourceRequests':0,
 'modelCalls':0,'liveReservations':0,'gateAttempts':0,'sourceQualified':False,'coverageCredit':False,
 'finishWrites':0,'currentPlanSelected':False,'originalHReplays':originals,'seconds':time.monotonic()-started})
print(json.dumps({'status':'PASS','testsPassed':result.testsRun,'consumedArchiveFiles':len(reads),'unchangedOtherFiles':len(before)-1,'sourceRequests':0,'seconds':time.monotonic()-started}))
