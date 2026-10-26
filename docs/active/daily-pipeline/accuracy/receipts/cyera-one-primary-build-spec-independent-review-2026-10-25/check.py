from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote
import json,csv,hashlib,sys,datetime,socket,urllib.error
O=Path("/var/tmp/smp-cyera-primary-spec-independent-20261025");A=Path("/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022");D=Path("/var/tmp/smp-cyera-primary-build-spec-20261025");F=Path("/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted");sys.path[:0]=[str(A/"web/scripts/pipeline")]
from contracts import digest,canonical,plan_run
from discovery import IndexMarkup
import q4_qualification_origin as Q,onboarding as B,fetcher as X
from storage import LocalStore
sha=lambda b:hashlib.sha256(b).hexdigest()
def seal(p):
 s=p.stat();b=p.read_bytes();return dict(sha256=sha(b),bytes=len(b),mtimeNs=s.st_mtime_ns)
inputs={str(p):seal(p)for p in D.iterdir()if p.is_file()};planraw=(D/"cyera-primary-J-candidate-plan-2026-10-25.json").read_bytes();plan=json.loads(planraw);assert digest(planraw)==digest(plan)=="25bf0ff72555188e7a8446b9499f3b8ba56c9327e397f8b70a5ce9deb82d350f"
mraw=(F/"archive-manifest.json").read_bytes();assert sha(mraw)=="13d956802cd881c0d6805c00c0dee48de07bd6615196e69f74fbf4056a710e34";entries={r["key"]:r for r in json.loads(mraw)["files"]};touched={}
class Store:
 def raw(self,key):
  p=F/"state"/key;r=entries["state/"+key];b=p.read_bytes();assert sha(b)==r["sha256"]and len(b)==r["bytes"];touched[str(p)]=seal(p);return b
 def read(self,key):return json.loads(self.raw(key))if "state/"+key in entries else None
 def get(self,ref):
  b=self.raw(ref["key"]);assert len(b)==ref["bytes"]and sha(b)==ref["sha256"];return b
store=Store();J=json.loads((A/"contracts/market.json").read_bytes())
with patch.object(socket,"socket",side_effect=AssertionError("NO_NETWORK")),patch.object(LocalStore,"__init__",side_effect=AssertionError("NO_LOCALSTORE")):
 H=Q.inverse_policy(J,store);sid="cyera:official:1";old=next(s for s in H["sources"]if s["id"]==sid);new=next(s for s in J["sources"]if s["id"]==sid);assert old==new and digest(new)==plan["source"]["originalSourceSha256"]
 h=plan["historicalReplay"];record=json.loads(store.get(h["record"]));raw=store.get(h["startProof"]["priorPlanReference"]);assert raw==(D/"original-H-seven-target-plan.json").read_bytes();report=record["diagnostic"]
 checked=B._validate_legacy_qualification_probe_plan(H,store,report["qualification"]["plan"]["path"],raw=raw,plan=json.loads(raw));assert checked=={k:v for k,v in report["qualification"]["plan"].items()if k!="rawPlanReference"}
 ob=B._qualification_explicit_observation(record,h["startProof"],old,H,store);assert ob["status"]=="fetched"and ob["httpStatus"]==200 and ob["requestedUrl"]==ob["finalUrl"]==plan["retainedIndex"]["url"]
 body=store.get(ob["body"]);nodes=list(IndexMarkup(body.decode()).root.walk());wrappers=[n for n in nodes if "card_list-wrapper"in n.classes];lists=[n for n in nodes if "card_list"in n.classes];assert len(wrappers)==len(lists)==1 and lists[0].parent is wrappers[0]
 cards=[n for n in nodes if "card_item"in n.classes];assert len(cards)==56 and all(n.parent is lists[0]for n in cards)
 csvrows=list(csv.DictReader((D/"cyera-retained-56-card-inventory.csv").open(newline="")));assert len(csvrows)==56;actual=[]
 for i,(card,row)in enumerate(zip(cards,csvrows)):
  child=list(card.walk());links=[n for n in child if "card_item-link"in n.classes];dates=[n for n in child if "card_date"in n.classes];titles=[n for n in child if n.tag=="h3"];assert len(links)==len(dates)==len(titles)==1
  link,date,title=links[0],dates[0],titles[0];ctx=json.loads(unquote(link.attrs["data-wf-cms-context"]));assert len(ctx)==1
  literal=" ".join(date.text.split());day=datetime.datetime.strptime(literal,"%b %d, %Y").date().isoformat();url="https://www.cyera.com"+link.attrs["href"]
  got=dict(rowIndex=str(i),sourceId=sid,url=url,title=" ".join(title.text.split()),dateLiteral=literal,calendarDay=day,timezone="",cmsCollectionId=ctx[0]["collectionId"],cmsItemId=ctx[0]["itemId"],currentWindow=str("2026-09-25"<=day<="2026-10-25"),knownSeed=str(url in new["seedEvidenceUrls"]));assert got==row,(i,got,row);actual.append(got)
 assert len({r["url"]for r in actual})==len({r["cmsItemId"]for r in actual})==56
 assert all(a["calendarDay"]>=b["calendarDay"]for a,b in zip(actual,actual[1:]));assert sum(r["currentWindow"]=="True"for r in actual)==1 and sum(r["knownSeed"]=="True"for r in actual)==5
 task=next(t for t in plan_run(J,"2026-10-25T15:00:00Z")["tasks"]if t["sourceId"]==sid);assert task["taskId"]=="ed4efbce40842341fe927359413639ff65e9fe4a4ed4cc406f085749e87c2d20"
 # Existing Fetcher interface can suppress default retry without changing global transport.
 class NoWrite:
  def put(self,*a):raise AssertionError("NO_BODY_WAS_RETURNED_FOR_HTTP_ERROR")
 class Opener:
  def __init__(self):self.calls=0
  def open(self,request,**kwargs):self.calls+=1;raise urllib.error.HTTPError(request.full_url,503,"Unavailable",{},None)
 transport=[]
 for attempt,expected in [(0,3),(2,1)]:
  opener=Opener();f=X.Fetcher(NoWrite(),timeout=12,max_bytes=2000000,redirect_diagnostics=True,unexpected_status_diagnostics=True);f.proxy_dns=True
  with patch.object(X.urllib.request,"build_opener",lambda *a:opener),patch.object(X.time,"sleep",lambda *a:None):res=f.fetch(new,plan["sample"]["url"],attempt=attempt)
  assert opener.calls==expected and res["status"]=="failed"and res["httpStatus"]==503;transport.append(dict(attempt=attempt,wireAttempts=opener.calls,response=res))
 for name,pin in touched.items():assert seal(Path(name))==pin
 assert inputs=={str(p):seal(p)for p in D.iterdir()if p.is_file()}
 proof=dict(schemaVersion=1,verdict="PASS_WITH_ACCEPTED_RETRY_AMENDMENT",originalInputSeals=inputs,actualArchiveManifestSha256=sha(mraw),exactJInverseToH=True,fullOriginalSevenTargetPlanValidated=True,strictChargedParentCyeraObservationValidated=True,actualCyeraTask=task,all56CsvRowsIndependentlyReconstructed=True,all5SeedsPresent=True,currentRows=1,olderBoundary=actual[1]["calendarDay"],earliestDay=actual[-1]["calendarDay"],equalDatePairs=sum(a["calendarDay"]==b["calendarDay"]for a,b in zip(actual,actual[1:])),existingFetcherRetryCounterexampleAndFix=transport,consultedArchiveInputSeals=touched,sourceRequests=0,modelRequests=0,realStateWrites=0,checkoutWrites=0)
 (O/"proof.json").write_text(json.dumps(proof,indent=2)+"\n");print(json.dumps({k:v for k,v in proof.items()if k not in["consultedArchiveInputSeals","originalInputSeals"]}))
