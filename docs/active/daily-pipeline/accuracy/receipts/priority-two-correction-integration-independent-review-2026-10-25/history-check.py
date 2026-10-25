from pathlib import Path
import json,sys,os,tempfile,socket,copy,hashlib
from unittest.mock import patch
O=Path("/var/tmp/smp-priority-two-corrections-independent-20261025");A=Path("/var/tmp/smp-priority-two-corrections-20261025/application");sys.path[:0]=[str(A/"ops/ci"),str(A/"web/scripts/pipeline")];os.chdir(A);tempfile.tempdir=str(O)
def audit(event,args):
 if event.startswith(("socket.","subprocess.")):raise AssertionError("NO_NETWORK_OR_PROCESS")
sys.addaudithook(audit)
import test_priority_two_corrections as T
from storage import LocalStore
from artifacts import stage_files
import corrections as C
original=LocalStore.__init__
def ctor(self,root,*a,**kw):
 assert Path(root).resolve().is_relative_to(O)
 return original(self,root,*a,**kw)
with patch.object(socket,"socket",side_effect=AssertionError("NO_NETWORK")),patch.object(LocalStore,"__init__",ctor):
 case=T.ActualSourceAndSyntheticMechanicsTests("test_SYNTHETIC_successful_two_group_review_cost_and_order_never_touch_real_state");case.setUp()
 try:
  out=case.process();assert len(out["admitted"])==8 and not out["pending"]
  production=case.base.read("heads/production.json");release=case.base.read("releases/"+production["releaseId"]+".json");files=stage_files(case.base,release["manifest"]["artifact"],release["acknowledgement"]);previous=json.loads(files["static/factual-corrections.json"])
  result=C.project_bundle(A,case.store,case.market,out,previous_bundle=previous,publication_at="2026-10-26T00:06:00Z")
  assert result["groups"][:6]==previous["groups"]and len(result["groups"])==8
  assert all(g["date"]=="2026-10-26"and g["note"]==req["noteTemplate"].replace("{date}","2026-10-26")for g,req in zip(result["groups"][6:],case.requests["groups"][6:]))
  fake=copy.deepcopy(previous);fake["groups"][0]["note"]+=" altered"
  try:C.project_bundle(A,case.store,case.market,out,previous_bundle=fake,publication_at="2026-10-26T00:06:00Z")
  except ValueError as e:assert "Historical correction changed"in str(e)
  else:raise AssertionError("OLD_HISTORY_MUTATION_ACCEPTED")
  oldindex=case.base.read("heads/budget-2026-10-25.json");assert oldindex==dict(fetches=1511,calls=80,documents=39)
  proof=dict(schemaVersion=1,verdict="PASS_SYNTHETIC_APPEND_MECHANICS_ONLY",oldPublicReleaseId=production["releaseId"],oldSixPublicRowsByteEquivalent=True,oldSixRowsSha256=[C.digest(g)for g in previous["groups"]],newRowsExactCandidateAndActualHypotheticalDay=True,rewrittenOldHistoryRejects=True,syntheticReviewCharges=case.charges,actualArchiveLedgerUnchanged=oldindex,actualNewAdmissions=0,sourceRequests=0,modelRequests=0,realStateWrites=0)
  (O/"history-check.json").write_text(json.dumps(proof,indent=2)+"\n");print(json.dumps(proof))
 finally:case.doCleanups()
