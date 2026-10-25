from pathlib import Path
from unittest.mock import patch
import hashlib,json,os,socket,sys,tempfile,unittest
O=Path('/var/tmp/smp-q4-ci-portability-independent-20261025');A=O/'application';mode=sys.argv[1];absent=mode=='absent';sys.path[:0]=[str(A/'ops/ci'),str(A/'web/scripts/pipeline'),str(A)];os.chdir(A);tempfile.tempdir=str(O/'temps')
frozen=['/var/tmp/smp-next-seven-actual-40190857026-20261025/extracted','/var/tmp/smp-listing-pagination-actual-40193925490-20261025/extracted'];access=[];denied=[]
def audit(event,args):
 if event.startswith(('socket.','subprocess.')):raise AssertionError('NO_NETWORK_OR_PROCESS:'+event)
 if event in ('open','os.listdir','os.scandir')and args and isinstance(args[0],(str,bytes,os.PathLike)):
  value=os.fsdecode(args[0])
  if any(value.startswith(p)for p in frozen):
   access.append({'event':event,'path':value})
   if absent:denied.append(value);raise AssertionError('FROZEN_READ_IN_HOSTED_ABSENCE')
sys.addaudithook(audit)
from storage import LocalStore
import q4_intake_fixtures as fixtures
if absent:fixtures.ARCHIVE=O/'missing-external-archive'
original=LocalStore.__init__
def local(self,root,*a,**kw):
 p=Path(root).resolve()
 if not p.is_relative_to(O):raise AssertionError('LOCALSTORE_OUTSIDE_REVIEW_TEMP')
 return original(self,root,*a,**kw)
class Result(unittest.TextTestResult):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.successes=[]
 def addSuccess(self,test):self.successes.append(test.id());super().addSuccess(test)
with patch.object(socket,'socket',side_effect=AssertionError('NO_NETWORK')),patch.object(LocalStore,'__init__',local):
 suite=unittest.defaultTestLoader.loadTestsFromName('test_q4_normal_intake');result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
 assert result.testsRun==14 and result.wasSuccessful()
 expected={'test_q4_normal_intake.ActualArchiveProofTests.test_actual_complete_graph_and_all_five_inventory_only_origins','test_q4_normal_intake.ActualArchiveProofTests.test_six_correction_admissions_and_group_policies_replay_without_any_work'}
 if absent:assert {t.id()for t,reason in result.skipped}==expected and len(result.successes)==12 and not access and not denied
 else:assert len(result.successes)==14 and not result.skipped
 # Authenticate the fixed committed package, and prove missing/corrupt data fails instead of skipping.
 import q4_qualification_seed as seed,q4_qualification_origin as q4
 repo=fixtures.CommittedSeed(A);manifest=repo.manifest;assert len(repo.files)==55 and sum(map(len,repo.files.values()))==4742948
 bad=O/('bad-package-'+mode);first=manifest['files'][0];p=bad/seed.PACKAGE['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((A/seed.PACKAGE['path']).read_bytes());p=bad/first['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'corrupt')
 try:fixtures.CommittedSeed(bad)
 except ValueError:pass
 else:raise AssertionError('CORRUPT_PACKAGE_ACCEPTED')
 try:fixtures.CommittedSeed(O/('missing-package-'+mode))
 except FileNotFoundError:pass
 else:raise AssertionError('MISSING_PACKAGE_SILENTLY_SKIPPED')
 proof=q4.AUTHORITY['proof'];saved=repo.files.pop(proof['key']);J=json.loads((A/'contracts/market.json').read_bytes())
 try:q4.predecessors(J,q4.SOURCE_IDS[0],repo,'2026-10-25T12:30:00Z')
 except FileNotFoundError:pass
 else:raise AssertionError('MISSING_PROOF_ACCEPTED_OR_SKIPPED')
 repo.files[proof['key']]=saved;repo.assert_unchanged()
 output={'schemaVersion':1,'mode':mode,'verdict':'PASS','testsRun':result.testsRun,'passed':len(result.successes),'skipped':[{'test':t.id(),'reason':reason}for t,reason in result.skipped],'successfulTests':result.successes,'archiveAccessEvents':len(access),'deniedFrozenReadAttempts':len(denied),'committedFilesHashAuthenticated':len(repo.files),'payloadBytes':sum(map(len,repo.files.values())),'extraAdversarialChecks':['corrupt_payload_fails','missing_package_fails_not_skip','missing_Q4_proof_fails_not_skip'],'sourceRequests':0,'modelRequests':0,'runtimePolicyPackageChanges':0,'repoWrites':0};(O/('independent-'+mode+'.json')).write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
