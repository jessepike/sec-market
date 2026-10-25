from pathlib import Path
import hashlib,json,gzip,shutil,os,datetime
O=Path("/var/tmp/smp-priority-three-web-test-delta-independent-20261025");W=Path("/mnt/mac/Users/jessepike/.codex/worktrees/priority-corrections/sec-market");A=Path("/var/tmp/smp-priority-two-corrections-20261025/application");D0=W/"docs/active/daily-pipeline/accuracy/receipts/priority-two-correction-web-test-delta-2026-10-25";sha=lambda b:hashlib.sha256(b).hexdigest()
vraw=(D0/"verification-addendum.json").read_bytes();assert sha(vraw)=="aea9f3754b580b91671c844e18c59c55a1249f42e8a4e1293a23676f7f04064d";v=json.loads(vraw)
for p,pin in v["deltaFiles"].items():
 for root in [A,W]:b=(root/p).read_bytes();assert sha(b)==pin["sha256"]and len(b)==pin["bytes"]
manifest=Path("/var/tmp/smp-priority-two-corrections-20261025/handback-index.json").read_bytes();assert sha(manifest)=="843eaebd5592b85618d93643a7af7af29abf98394e38469447b523a9d6e051fd";old=json.loads(manifest)
for p,pin in old["files"].items():b=(W/p).read_bytes();assert sha(b)==pin["sha256"]and len(b)==pin["bytes"]
prior=Path("/var/tmp/smp-priority-two-corrections-independent-20261025/handback/docs/active/daily-pipeline/accuracy");stem0="priority-two-correction-integration-independent-review-2026-10-25"
for name,pin in {stem0+".md":"cb5b34f155ec1a1cee2c0333fae3355a69d1f9e7b09875dd44579172293ea8bb",stem0+".json":"54763777fb2614482edf922323efd1c58671ed630e5d56c19d6f463fbde0ff94"}.items():assert sha((prior/name).read_bytes())==pin
base=Path("/var/tmp/smp-priority-two-corrections-independent-20261025/base-git-blobs.raw").read_bytes();overlays=json.loads(Path("/var/tmp/smp-priority-two-corrections-20261025/assembly.json").read_bytes())["exactOwnedOverlay"]|v["deltaFiles"];n=0;changed=[]
for row in base.split(b"\0"):
 if not row:continue
 meta,name=row.split(b"\t",1);mode,kind,oid=meta.split()
 if kind!=b"blob":continue
 name=name.decode();p=A/name;b=os.readlink(p).encode()if mode==b"120000"else p.read_bytes()
 if hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()!=oid.decode():assert name in overlays and sha(b)==overlays[name]["sha256"];changed.append(name)
 n+=1
assert n==2662 and len(changed)==11
logs={}
for name,pin in v["logs"].items():
 z=(D0/pin["gzipFile"]).read_bytes();b=gzip.decompress(z);assert sha(z)==pin["gzip"]["sha256"]and len(z)==pin["gzip"]["bytes"]and sha(b)==pin["raw"]["sha256"]and len(b)==pin["raw"]["bytes"];logs[name]=pin
log=(O/"selected-tests.log").read_text();assert "# tests 43"in log and "# pass 43"in log and "# fail 0"in log and "# skipped 0"in log
stem="priority-two-correction-web-test-delta-independent-review-2026-10-25";R=O/"handback/docs/active/daily-pipeline/accuracy";D=R/"receipts"/stem;D.mkdir(parents=True,exist_ok=True)
for name in ["seal.py","selected-tests.log","initial-driver-tsconfig-error.log","three-test.diff"]:shutil.copyfile(O/name,D/name)
report=dict(schemaVersion=1,verdict="PASS",findings=[],reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope="Separate three-test historical-six fixture delta only.",deltaFiles=v["deltaFiles"],fixtures=dict(requests=v["historicalRequests"],stamp=v["historicalStamp"]),independentSelectedTests=dict(command="cd application/web; ./node_modules/.bin/tsx --tsconfig tsconfig.app.json --test tests/factual-correction-build.test.mjs tests/publisher-disclosure-corrections.test.ts tests/s1-exact-filing-transport.test.mjs",tests=43,passed=43,skipped=0,failures=0,logSha256=sha(log.encode())),workerFullNpmAuthenticated=v["validation"],workerLogPinsAuthenticated=logs,protected=dict(original31WorkerPathsAllExact=True,originalWorkerManifestSha256=sha(manifest),originalIndependentMDJSONExact=True,baseGitBlobsChecked=2662,baseChangedPaths=changed,onlyOriginal12PlusNew3Overlay=True,runtimeOrRequestsOrStampChanges=0,assertionWeakening=False,newSkips=0),diagnostics=dict(actualInitialNpm="Ten old-six data-fixture failures stopped initial npm before later stages; original failed raw/gzip log remains retained.",independentDriver="Ad-hoc node --import tsx omitted project JSX tsconfig and failed one React render. Exact project tsx --tsconfig runner passes43/43; driver-failure log retained. No product code was changed."),boundaries=dict(sourceRequests=0,modelRequests=0,newAdmissions=0,realStateOrArchiveWrites=0,checkoutWrites=0,publicationCredit=False),receiptsRelative="receipts/"+stem)
(R/(stem+".json")).write_text(json.dumps(report,indent=2)+"\n")
md="""# Priority corrections: separate web-test fixture delta review

PASS. The three test files now use the existing hash-pinned historical-six request/stamp fixtures for their historical mechanics. No assertion was weakened and no skip was added. The current eight-group policy remains independently checked by the pending-integration tests and runtime validators.

Independent execution used the active-eight isolated application and the project tsx runner with `tsconfig.app.json`: all 43 selected tests passed, with no skips. The worker final full npm log was authenticated and losslessly decompressed: 379 data tests, 115 pipeline tests, all 80 SEC claims, and 42 browser tests passed, with one existing browser fixture skip; lint has no error and one existing warning.

The requests fixture remains raw SHA-256 `9c9fbe0d3d40ece11e1407ce9460086c732f62da88d3b0f220ab9d6f8757da00`; the historical J stamp remains `365058911a182610cde401307fb30cc1855930b7940969440a618441cbbef9b2`. Both are explicitly checked before use. Only the three named test files change. All 31 prior worker handback paths and the original independent review MD/JSON remain byte-exact. All 2,662 base Git blobs were checked again; differences are confined to the original reviewed overlay and these three tests. No runtime, request, stamp, baseline or accepted view changed.

The actual initial npm failure remains retained: ten historical-fixture failures stopped its data stage. A separate independent ad-hoc invocation omitted the project JSX configuration and failed one React render; the corrected project runner passed without a code change. Neither failed run is recast as passing.

The companion JSON records exact new test pins, selected command/results, full npm raw/gzip pins, protected old handoffs and limits. The separate receipt folder retains the diff, successful selected log and independent driver failure. No source/model request, real admission, archive write or checkout write occurred. Root controls copying this test-only delta.
"""
(R/(stem+".md")).write_text(md)
index=dict(schemaVersion=1,files={p.name:dict(sha256=sha(p.read_bytes()),bytes=p.stat().st_size)for p in sorted(D.iterdir())if p.is_file()});(D/"index.json").write_text(json.dumps(index,indent=2)+"\n")
for p in [R/(stem+".md"),R/(stem+".json"),D/"index.json"]:print(str(p),sha(p.read_bytes()),p.stat().st_size)
