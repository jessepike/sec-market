"""Root-authorized exact reviewed pending-only overlay; no runtime or Git writer."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
SOURCE=Path("/mnt/mac/Users/jessepike/.codex/worktrees/priority-corrections/sec-market")
TARGET=Path("/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022")
REVIEW=Path("/var/tmp/smp-priority-two-corrections-independent-20261025/handback")
MANIFEST=Path("/var/tmp/smp-priority-two-corrections-20261025/handback-index.json")
BASE="6bd3075c80bae7bba56a096cadb116cb379b2d63"
SOURCE_BASE="2387abb41069f3a74a005468d91e5401d97089ff"
OUT=TARGET/"docs/active/daily-pipeline/accuracy/receipts/priority-two-correction-controlled-integration-2026-10-25"
def raw(path):
 p=Path(path);return os.fsencode(os.readlink(p)) if p.is_symlink() else p.read_bytes()
def pin(path,mtime=False):
 p=Path(path);b=raw(p);r={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
 if mtime:r["mtimeNs"]=p.lstat().st_mtime_ns
 return r
def git(root,*args):return subprocess.check_output(["git","-C",str(root),*args])
assert pin(MANIFEST)=={"sha256":"843eaebd5592b85618d93643a7af7af29abf98394e38469447b523a9d6e051fd","bytes":7116}
m=json.loads(MANIFEST.read_bytes());assert m["fileCount"]==31
assert git(TARGET,"rev-parse","HEAD").decode().strip()==BASE
assert git(TARGET,"status","--porcelain")==b"", "Unexpected existing target change"
assert not OUT.exists()
files={n:{"source":SOURCE/n,"expected":p,"origin":"reviewed_worker_manifest"}for n,p in m["files"].items()}
review_stem=Path("docs/active/daily-pipeline/accuracy")
review_receipts=REVIEW/review_stem/"receipts/priority-two-correction-integration-independent-review-2026-10-25"
ri=json.loads((review_receipts/"index.json").read_bytes())
for name,expected in ri["files"].items():assert pin(review_receipts/name)==expected,name
rj=json.loads((REVIEW/review_stem/"priority-two-correction-integration-independent-review-2026-10-25.json").read_bytes())
assert rj["verdict"]=="PASS" and rj["findings"]==[]
for name,expected in rj["exactReviewed12Pins"].items():assert m["files"][name]==expected,name
for p in sorted(REVIEW.rglob("*")):
 if not p.is_file():continue
 name=str(p.relative_to(REVIEW));assert name.startswith(str(review_stem)+"/")
 assert name not in files
 files[name]={"source":p,"expected":pin(p),"origin":"sealed_independent_review"}
assert len(files)==48
before={};modes={}
for entry in git(TARGET,"ls-tree","-r","-z",BASE).split(b"\0"):
 if not entry:continue
 meta,nb=entry.split(b"\t",1);mode,kind,oid=meta.split();name=os.fsdecode(nb)
 assert kind==b"blob";b=raw(TARGET/name)
 assert hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()==oid.decode(),name
 before[name]=pin(TARGET/name,True);modes[name]=mode.decode()
owned_before={}
for name,row in files.items():
 assert pin(row["source"])==row["expected"],name
 dest=TARGET/name
 if dest.exists():
  assert name in before,name
  old=git(SOURCE,"show",SOURCE_BASE+":"+name)
  assert raw(dest)==old,"Target has a newer unexpected owned-file change: "+name
  owned_before[name]=before[name]
 else:owned_before[name]=None
# The complete preflight above precedes the first checkout write.
for name,row in files.items():
 dest=TARGET/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row["source"],dest)
 assert pin(dest)==row["expected"],name
for name,b in before.items():
 if name not in files:assert pin(TARGET/name,True)==b,name
for name,row in files.items():assert pin(row["source"])==row["expected"] and pin(TARGET/name)==row["expected"],name
assert git(TARGET,"rev-parse","HEAD").decode().strip()==BASE
subprocess.run(["git","-C",str(TARGET),"diff","--check"],check=True)
protected_names=["status.md","BACKLOG.md","intent.md","AGENTS.md","contracts/market.json","contracts/source-qualification-probes.json","contracts/factual-baseline.json","web/src/data/tracker/originals.json","web/src/data/generated/factualCorrections.json","web/src/data/generated/dailyBaseline.json","web/scripts/pipeline/corrections.py","web/scripts/pipeline/engine.py","web/scripts/pipeline/fetcher.py","ops/ci/collect.py","ops/ci/runtime_canary.py",".github/workflows/subscription-runtime-canary.yml"]
protected={name:before[name]for name in protected_names if name in before}
assert protected["contracts/market.json"]["sha256"]=="bb9735d073e41a0a22bdcfd315419c59e8791b82be34bc73ead699530147b3e6"
assert protected["contracts/source-qualification-probes.json"]["sha256"]=="ef9ee1bab6cfe6202b62e8d5605393f045d11fd64bd42ea1bcea769de15c8a01"
result={"schemaVersion":1,"verdict":"PASS_BYTE_EXACT_CONTROLLED_COPY_PENDING_ONLY","targetBaseCommit":BASE,"sourceBaseCommit":SOURCE_BASE,"sourceManifest":pin(MANIFEST),"copiedFiles":{name:{**row["expected"],"origin":row["origin"],"before":owned_before[name]}for name,row in files.items()},"fileCount":len(files),"workerFiles":31,"independentReviewFiles":17,"originalTrackedFilesChecked":len(before),"unchangedOtherTrackedFiles":len(set(before)-set(files)),"allOtherTrackedBytesSizeMtimeExact":True,"protectedFilesBeforeAndAfter":protected,"ownedSourcesUnchanged":True,"gitHeadUnchanged":True,"sourceJUnchanged":True,"disabledJProbePlanUnchanged":True,"newSemanticAdmissions":0,"sourceRequests":0,"modelRequests":0,"ledgerOrArchiveWrites":0,"dispatches":0,"gitMutations":0,"checksRepeated":False,"checksReused":"Byte-exact reviewed overlay with final 98 affected/972 present/913+59 absent, build80SEC/four renders and independent PASS. No unchanged suite rerun required.","canaryScope":"Existing hosted canary checks market/archived coverage/plan/attempt integrity, not current correction requests/admission/publication. It performs no source-probe replay.","remaining":"Root owns commit, preview/main promotion and actual natural-next-UTC review. Pending8 still holds publication before gate reservation."}
OUT.mkdir(parents=True)
(OUT/"copy-index.json").write_text(json.dumps(result,indent=2)+"\n")
shutil.copyfile(__file__,OUT/"controlled_copy.py")
print(json.dumps({"verdict":result["verdict"],"files":len(files),"protectedOriginalFiles":result["unchangedOtherTrackedFiles"],"copyIndex":pin(OUT/"copy-index.json"),"helper":pin(OUT/"controlled_copy.py")}))
