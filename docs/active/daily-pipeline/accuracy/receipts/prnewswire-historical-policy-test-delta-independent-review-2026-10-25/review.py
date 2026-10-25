from pathlib import Path
from unittest.mock import patch
import json,sys,os,socket,unittest,tempfile,hashlib
O=Path("/var/tmp/smp-prn-historical-test-delta-independent-20261025");A=Path("/var/tmp/smp-prn-historical-test-delta-20261025/combined-J");sys.path[:0]=[str(A/"ops/ci"),str(A/"web/scripts/pipeline")];os.chdir(A);tempfile.tempdir=str(O);mode=sys.argv[1];absent=mode=="absent";frozen="/var/tmp/smp-listing-pagination-actual-40193925490-20261025/extracted";attempts=[]
def audit(event,args):
 if event.startswith(("socket.","subprocess.")):raise AssertionError("NO_NETWORK_OR_SUBPROCESS")
 if event in ("open","os.listdir","os.scandir")and args and isinstance(args[0],(str,bytes,os.PathLike))and os.fsdecode(args[0]).startswith(frozen):
  if absent:attempts.append(os.fsdecode(args[0]));raise AssertionError("FROZEN_READ_ATTEMPT")
  if event=="open":assert not (isinstance(args[1],str)and any(x in args[1]for x in "wax+"))and not args[2]&(os.O_RDWR|os.O_WRONLY|os.O_TRUNC|os.O_CREAT|os.O_APPEND)
sys.addaudithook(audit)
original_exists=Path.exists
class Result(unittest.TextTestResult):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.successes=[]
 def addSuccess(self,t):self.successes.append(t.id());super().addSuccess(t)
def exists(p):return False if absent and str(p).startswith(frozen)else original_exists(p)
with patch.object(Path,"exists",exists),patch.object(socket,"socket",side_effect=AssertionError("NO_NETWORK")):
 suite=unittest.defaultTestLoader.discover(str(A/"ops/ci"),pattern="test_prnewswire*.py")
 from storage import LocalStore
 with patch.object(LocalStore,"__init__",side_effect=AssertionError("NO_LOCALSTORE")):
  result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
  assert result.wasSuccessful()and result.testsRun==26 and not attempts
  assert (len(result.successes),len(result.skipped))==((13,13)if absent else(26,0))
  from contracts import digest
  import test_prnewswire_retained_window as T,prnewswire_retained_window as V
  J=json.loads((A/"contracts/market.json").read_bytes());assert digest(J)=="47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a"
  H="8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db";rel="contracts/html-qualification-seeds/"+H+"/contracts__"+H+".json";hraw=(A/rel).read_bytes();assert len(hraw)==204449 and digest(hraw)==digest(json.loads(hraw))==H
  checks=[]
  try:V.derive_report(J,None,T.DESCRIPTOR.read_bytes())
  except ValueError:checks.append("current_J_not_accepted_as_original_H")
  else:raise AssertionError("CURRENT_J_BRIDGED")
  for corrupt in (False,True):
   with tempfile.TemporaryDirectory(dir=O)as td:
    root=Path(td)
    if corrupt:p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(hraw+b" ")
    with patch.object(T,"ROOT",root):
     try:T.RetainedTests.setUpClass()
     except (AssertionError,FileNotFoundError):checks.append("corrupt_historical_fixture_rejects"if corrupt else"missing_historical_fixture_rejects")
     else:raise AssertionError("UNPINNED_H_FIXTURE_ACCEPTED")
 output=dict(schemaVersion=1,verdict="PASS",mode=mode,testsRun=26,passed=len(result.successes),skipped=[dict(test=t.id(),reason=r)for t,r in result.skipped],passedNames=result.successes,frozenReadAttempts=attempts,extraChecks=checks,currentCanonicalJ=digest(J),historicalRawAndCanonicalH=H,historicalBytes=len(hraw),sourceRequests=0,modelRequests=0,frozenWrites=0,repoWrites=0)
 (O/(mode+".json")).write_text(json.dumps(output,indent=2)+"\n");print(json.dumps(output))
