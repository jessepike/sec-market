from pathlib import Path
from unittest.mock import patch
import copy,json,hashlib,os,socket,sys,tempfile,unittest
O=Path("/var/tmp/smp-priority-two-corrections-independent-20261025");A=Path("/var/tmp/smp-priority-two-corrections-20261025/application");os.chdir(A);sys.path[:0]=[str(A/"ops/ci"),str(A/"web/scripts/pipeline")];tempfile.tempdir=str(O);mode=sys.argv[1];absent=mode=="absent";denied=[];frozen="/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted"
sha=lambda b:hashlib.sha256(b).hexdigest()
def audit(event,args):
 if event.startswith(("socket.","subprocess.")):raise AssertionError("NETWORK_OR_PROCESS_DENIED")
 if event=="open"and isinstance(args[0],(str,bytes,os.PathLike))and os.fsdecode(args[0]).startswith(frozen):
  if absent:denied.append(os.fsdecode(args[0]));raise AssertionError("FROZEN_READ_DENIED")
  assert not(isinstance(args[1],str)and any(x in args[1]for x in "wax+"))and not args[2]&(os.O_CREAT|os.O_WRONLY|os.O_RDWR|os.O_TRUNC|os.O_APPEND)
sys.addaudithook(audit)
from storage import LocalStore
real_init=LocalStore.__init__;real_exists=Path.exists
def init(self,root,*a,**kw):
 assert Path(root).resolve().is_relative_to(O),"LOCALSTORE_OUTSIDE_OWN_TEMP"
 return real_init(self,root,*a,**kw)
def exists(p):return False if absent and str(p).startswith(frozen)else real_exists(p)
class Result(unittest.TextTestResult):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.passed=[]
 def addSuccess(self,t):self.passed.append(t.id());super().addSuccess(t)
with patch.object(socket,"socket",side_effect=AssertionError("NO_NETWORK")),patch.object(LocalStore,"__init__",init),patch.object(Path,"exists",exists):
 suite=unittest.defaultTestLoader.loadTestsFromName("test_priority_two_corrections");r=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
 assert r.wasSuccessful()and r.testsRun==11 and (len(r.passed),len(r.skipped))==((4,7)if absent else(11,0))and not denied
 import corrections as C,release as R,test_priority_two_corrections as T
 J=json.loads((A/"contracts/market.json").read_bytes());ctx=C.load_policy(A,J);packet=json.loads((A/"docs/active/daily-pipeline/accuracy/priority-correction-candidate-packet-2026-10-25.json").read_bytes());assert ctx["requests"]["groups"][6:]==packet["groups"]
 extra=[]
 if not absent:
  base=T.ReadOnlyJ()
  class Memory:
   def __init__(self):self.memory={};self.mutations=[]
   def read(self,key):return json.loads(self.memory[key])if key in self.memory else base.read(key)
   def get(self,ref):return self.memory[ref["key"]]if ref["key"]in self.memory else base.get(ref)
   def put(self,value):
    b=value if type(value)is bytes else C.canonical(value);ref=dict(key="objects/"+sha(b),sha256=sha(b),bytes=len(b));self.memory[ref["key"]]=b;return ref
   def write_once(self,key,value):
    b=value if type(value)is bytes else C.canonical(value);assert key not in self.memory or self.memory[key]==b;self.memory[key]=b
   def compare_and_swap(self,name,old,new):self.mutations.append(name);raise AssertionError("GATE_OR_ACCOUNT_WRITE_BEFORE_PENDING_HOLD")
  mem=Memory();out=C.process_corrections(A,mem,J,None,lambda *a:(_ for _ in()).throw(AssertionError("NO_RESERVATIONS")),T.NOW,clock=lambda:T.NOW)
  assert len(out["admitted"])==6 and len(out["pending"])==2;extra.append("actual_six_replayed_without_model_or_reservation")
  # The real release controller must stop for either one or two pending groups before reserving or dispatching.
  class Adapter:
   def __init__(self,*a,**kw):pass
   def production_paths_controlled(self):return True
  latest=base.read("heads/latest-run.json")
  for count in (1,2):
   value=dict(out,runId=latest["runId"],checkedAt=T.NOW,pending=out["pending"][:count]);ref=mem.put(value);mem.memory["heads/correction-collection.json"]=C.canonical(dict(runId=latest["runId"],outcome=ref))
   dispatch=[]
   with patch.object(R,"VercelAdapter",Adapter),patch.object(R,"recover_publication",lambda *a:dict(releaseId="SYNTHETIC-MISSING-RELEASE")),patch.object(R,"dispatch_gate",lambda *a:dispatch.append(a)):
    try:R.release_daily(mem,J,{},"0"*40,{"vercel":{"unused":True}},lambda:(_ for _ in()).throw(AssertionError("NO_CHECKPOINT")))
    except ValueError as e:assert "pending"in str(e),str(e)
    else:raise AssertionError("PENDING_GROUP_RELEASED")
   assert not dispatch and not mem.mutations;extra.append(str(count)+"_pending_groups_stop_real_release_before_gate")
  # Compare every bound old source against actual latest ordinary-J source observation bodies.
  receipt=json.loads(base.get(latest["receipt"]));current=[]
  for group in packet["groups"]:
   s=group["sources"][0];row=next(t for t in receipt["receipts"]if t["sourceId"]==s["sourceId"]);obs=[base.read("observations/"+oid+".json")for oid in row["observationIds"]];ob=next(o for o in obs if o["requestedUrl"]==s["url"]);assert ob["body"]==s["body"];current.append(dict(sourceId=s["sourceId"],bound=s,latestObserved=ob))
  for name,before in base.touched.items():p=Path(name);b=p.read_bytes();assert(sha(b),len(b),p.stat().st_mtime_ns)==before
 else:current=[]
 output=dict(schemaVersion=1,verdict="PASS",mode=mode,testsRun=11,passed=len(r.passed),passedNames=r.passed,skipped=[dict(test=t.id(),reason=reason)for t,reason in r.skipped],frozenReadAttempts=denied,additionalChecks=extra,actualCurrentJSourceBodyComparisons=current,requestsRawSha256=sha((A/"contracts/factual-corrections.json").read_bytes()),requestsCanonicalSha256=C.digest(ctx["requests"]),stampRawSha256=sha((A/"web/src/data/tracker/factualCorrectionPolicy.json").read_bytes()),outerPolicySha256=ctx["policySha256"],sourceRequests=0,modelRequests=0,realAdmissions=0,realStateWrites=0,checkoutWrites=0,syntheticMechanics="Supplied tests exercise mocked model responses and admissions only in reviewer-owned temporary state; never semantic acceptance.")
 (O/(mode+".json")).write_text(json.dumps(output,indent=2)+"\n");print(json.dumps(output))
