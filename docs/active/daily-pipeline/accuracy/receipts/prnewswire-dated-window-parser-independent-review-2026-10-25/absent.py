from pathlib import Path
from unittest.mock import patch
import os,socket,sys,unittest,json
O=Path("/var/tmp/smp-prn-independent-20261025");A=Path("/mnt/mac/Users/jessepike/.codex/worktrees/prn-dated-window/sec-market");os.chdir(A);sys.path[:0]=[str(A/"ops/ci"),str(A/"web/scripts/pipeline")]
frozen="/var/tmp/smp-listing-pagination-actual-40193925490-20261025/extracted";attempts=[]
def audit(event,args):
 if event.startswith(("socket.","subprocess.")):raise AssertionError("NO_NETWORK_OR_SUBPROCESS")
 if event in ("open","os.listdir","os.scandir")and args and isinstance(args[0],(str,bytes,os.PathLike))and os.fsdecode(args[0]).startswith(frozen):
  attempts.append({"event":event,"path":os.fsdecode(args[0])});raise AssertionError("FROZEN_READ_ATTEMPTED")
sys.addaudithook(audit)
original=Path.exists
class Result(unittest.TextTestResult):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.successes=[]
 def addSuccess(self,test):self.successes.append(test.id());super().addSuccess(test)
def exists(p):return False if str(p).startswith(frozen)else original(p)
with patch.object(Path,"exists",exists),patch.object(socket,"socket",side_effect=AssertionError("NO_NETWORK")):
 suite=unittest.defaultTestLoader.discover(str(A/"ops/ci"),pattern="test_prnewswire*.py")
 from storage import LocalStore
 with patch.object(LocalStore,"__init__",side_effect=AssertionError("NO_LOCALSTORE")):
  result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
 assert result.wasSuccessful()and result.testsRun==26 and len(result.successes)==13 and len(result.skipped)==13 and not attempts
 output=dict(schemaVersion=1,verdict="PASS",mode="fresh_process_external_archive_absent_before_discovery",testsRun=result.testsRun,passed=len(result.successes),passedTestNames=result.successes,skipped=[dict(test=t.id(),reason=reason)for t,reason in result.skipped],frozenReadAttempts=attempts,sourceRequests=0,modelRequests=0,repoWrites=0)
 (O/"absent.json").write_text(json.dumps(output,indent=2)+"\n");print(json.dumps(output))
