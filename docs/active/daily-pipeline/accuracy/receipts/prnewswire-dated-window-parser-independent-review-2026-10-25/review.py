from pathlib import Path
import hashlib,json,os,socket,sys,tempfile,unittest,copy
from unittest.mock import patch
O=Path("/var/tmp/smp-prn-independent-20261025");A=Path("/mnt/mac/Users/jessepike/.codex/worktrees/prn-dated-window/sec-market");os.chdir(A);sys.path[:0]=[str(A/"ops/ci"),str(A/"web/scripts/pipeline")];tempfile.tempdir=str(O)
sha=lambda b:hashlib.sha256(b).hexdigest()
paths=["web/scripts/pipeline/prnewswire_press_list.py","web/scripts/pipeline/prnewswire_retained_window.py","ops/ci/test_prnewswire_press_list.py","ops/ci/test_prnewswire_retained_window.py","docs/active/daily-pipeline/accuracy/prnewswire-retained-window-descriptor-2026-10-25.json","docs/active/daily-pipeline/accuracy/prnewswire-dated-window-parser-build-spec-2026-10-25.md"]
def seal(p):
 s=p.stat();b=p.read_bytes();return dict(sha256=sha(b),bytes=len(b),mtimeNs=s.st_mtime_ns)
before={p:seal(A/p)for p in paths}
def audit(event,args):
 if event.startswith(("socket.","subprocess.")):raise AssertionError("NETWORK_OR_SUBPROCESS_DENIED")
 if event=="open" and isinstance(args[0],str)and args[0].startswith("/var/tmp/smp-listing-pagination-actual-40193925490-20261025/extracted"):
  mode=args[1];flags=args[2]
  assert not (isinstance(mode,str)and any(c in mode for c in "wax+"))and not flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND),"FROZEN_WRITE_DENIED"
sys.addaudithook(audit)
from storage import LocalStore
import test_prnewswire_press_list as T,test_prnewswire_retained_window as U
import prnewswire_press_list as P,prnewswire_retained_window as V
with patch.object(socket,"socket",side_effect=AssertionError("NO_NETWORK")),patch.object(LocalStore,"__init__",side_effect=AssertionError("NO_LOCALSTORE")):
 suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(T),unittest.defaultTestLoader.loadTestsFromModule(U)])
 result=unittest.TextTestRunner(verbosity=2).run(suite);assert result.wasSuccessful()and result.testsRun==26 and not result.skipped
 store=T.ReadOnlyActual();contract=json.loads((A/"contracts/market.json").read_bytes());raw=U.DESCRIPTOR.read_bytes();d=json.loads(raw);report=V.derive_report(contract,store,raw)
 extra=[]
 def rejects(name,fn):
  try:fn()
  except (ValueError,FileNotFoundError):extra.append(name)
  else:raise AssertionError("ACCEPTED:"+name)
 # Exhaustively test every source-specific language/path pairing as a positive, then cross-source unsafe pairs.
 locale=[]
 for sid,mapping in P.LANGUAGE_PATHS.items():
  for lang,prefixes in mapping.items():
   for prefix in prefixes:
    body=T.card(1,language=lang,href=prefix+"fixture.html");page=T.page([body],source_id=sid)
    got=P.parse_page(sid,P.index_url(sid),page,T.AS_OF);assert got["records"][0]["url"]==P.HOST+prefix+"fixture.html";locale.append([sid,lang,prefix])
 for sid,lang,path in [(T.SID,"fr","/il/news-releases/x.html"),(T.SID,"in","/in/news-releases/x.html"),("chainguard:official:1","il","/il/news-releases/x.html"),("chainguard:official:1","en-US","/in/news-releases/x.html")]:
  rejects("wrong_locale_pair:"+sid+":"+lang+":"+path,lambda sid=sid,lang=lang,path=path:P.parse_page(sid,P.index_url(sid),T.page([T.card(1,language=lang,href=path)],source_id=sid),T.AS_OF))
 # Requests must not inherit metadata-only identity; alternate query/order, authorities, locale roots stay rejected.
 for sid in P.SOURCES:
  for suffix in ("?page=2","?page=02&pagesize=25","?page=2&pagesize=025","?pagesize=25&page=2","?page=2&pagesize=25#x"):
   url=P.index_url(sid)+suffix;rejects("metadata_or_query_request:"+sid+suffix,lambda sid=sid,url=url:P.page_number(sid,url))
 # A retained positive requires exact external actual proof, never a newly authored assertion.
 for s in (d["sources"][0],d["sources"][1]):
  fake=copy.deepcopy(d);fake["sources"][0]["pages"][0]["body"]=s["primary"]["body"]
  rejects("rehashed_descriptor_substitution:"+s["sourceId"],lambda fake=fake:V.derive_report(contract,store,json.dumps(fake,sort_keys=True,separators=(",",":")).encode()))
 with tempfile.TemporaryDirectory(dir=O)as td:
  root=Path(td)
  for pin in d["externalFiles"]:
   p=root/pin["path"];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((A/pin["path"]).read_bytes())
  pin=d["externalFiles"][0];p=root/pin["path"];p.write_bytes(p.read_bytes()+b" ")
  with patch.object(V,"REPO",root):rejects("external_actual_audit_bytes_required",lambda:V.derive_report(contract,store,raw))
 # Exact report recomputation prevents dropping older missing seeds or turning inventory into freshness credit.
 for name,fn in [("erase_old_seed_scope_gap",lambda x:x["streams"][0].update(knownSeedsOutsideObservedList=[])),("declare_history_complete",lambda x:x["streams"][0].update(historicalEnumerationComplete=True)),("claim_qualification",lambda x:x.update(qualified=True)),("hide_index_timezone",lambda x:x["streams"][0].update(timezone="ET"))]:
  altered=copy.deepcopy(report);fn(altered);rejects(name,lambda altered=altered:V.verify_report(contract,store,raw,altered))
 for path,b in store.touched.items():assert seal(Path(path))==dict(sha256=b[0],bytes=b[1],mtimeNs=b[2])
 summary=dict(schemaVersion=1,verdict="PASS",focusedTests=26,focusedSkips=0,extraNegativeChecks=len(extra),extraNegativeNames=extra,positiveLocalePairs=locale,sourceCounts=[dict(sourceId=s["sourceId"],listUrls=len(s["items"]),knownUnion=len(s["knownEvidenceUnion"]),current=len(s["currentWindowItems"]),dailyWindowComplete=s["dailyWindowComplete"],historicalEnumerationComplete=s["historicalEnumerationComplete"],sourceScopeComplete=s["sourceScopeComplete"],missingSeeds=[dict(url=g["url"],publicationDay=g["shape"]["publicationCalendarDay"],calendarWindowState=g["calendarWindowState"])for g in s["knownSeedsOutsideObservedList"]])for s in report["streams"]],archiveInputsTouched=len(store.touched),consultedArchiveInputSeals={p:dict(sha256=x[0],bytes=x[1],mtimeNs=x[2])for p,x in store.touched.items()},codeAndSpecSealsBefore=before,codeAndSpecSealsAfter={p:seal(A/p)for p in paths},sourceRequests=0,modelRequests=0,frozenWrites=0,repoWrites=0,operationalCredit=False)
 assert summary["codeAndSpecSealsBefore"]==summary["codeAndSpecSealsAfter"]
 (O/"independent-review.json").write_text(json.dumps(summary,indent=2)+"\n");print(json.dumps({k:v for k,v in summary.items()if k!="consultedArchiveInputSeals"}))
