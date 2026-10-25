from pathlib import Path
import hashlib,json,gzip,os,shutil,datetime
O=Path("/var/tmp/smp-q4-ci-portability-independent-20261025");A=O/"application"
W=Path("/var/tmp/smp-q4-ci-portability-20261025/handback/docs/active/daily-pipeline/accuracy/receipts/q4-normal-intake-ci-portability-repair-2026-10-25")
sha=lambda b:hashlib.sha256(b).hexdigest()
def seal(p):
 s=p.stat();b=p.read_bytes();return dict(sha256=sha(b),bytes=len(b),mtimeNs=s.st_mtime_ns,inode=s.st_ino,device=s.st_dev)
P=json.loads((O/"fresh-application-proof.json").read_bytes());changed=[];verified=0
raw=(O/"base-git-blobs.raw").read_bytes()
for row in raw.split(b"\0"):
 if not row:continue
 meta,name=row.split(b"\t",1);mode,kind,oid=meta.split();path=name.decode();p=A/path
 if kind!=b"blob":continue
 body=os.readlink(p).encode()if mode==b"120000"else p.read_bytes()
 actual=hashlib.sha1(b"blob "+str(len(body)).encode()+b"\0"+body).hexdigest()
 if actual!=oid.decode():
  assert path in P["onlyOverlays"],path
  assert sha(body)==P["onlyOverlays"][path]["newSha256"];changed.append(path)
 verified+=1
assert verified==2569 and sorted(changed)==sorted(P["onlyOverlays"])
vraw=(W/"verification.json").read_bytes();assert sha(vraw)=="b517e6931871216b227d2bb817705a9f4376be2cdc848f3f66060a8b0ef40315";V=json.loads(vraw)
for path,pin in V["protectedOther81ImplementationPins"].items():
 b=(A/path).read_bytes();assert sha(b)==pin["sha256"]and len(b)==pin["bytes"],path
assert len(V["protectedOther81ImplementationPins"])==81
logs={}
for name,pin in V["logs"].items():
 z=(W/pin["gzipFile"]).read_bytes();b=gzip.decompress(z)
 assert sha(z)==pin["gzipSha256"]and len(z)==pin["gzipBytes"]and sha(b)==pin["rawSha256"]and len(b)==pin["rawBytes"]
 logs[name]=dict(sha256=sha(b),bytes=len(b),tail=[line for line in b.decode().splitlines()if line.startswith(("Ran ","OK","FAILED"))])
assert "Ran 935 tests"in "\n".join(logs["full-present.log"]["tail"])
assert "OK (skipped=39)"in "\n".join(logs["full-absent.log"]["tail"])
stem="q4-normal-intake-ci-portability-independent-review-2026-10-25";R=O/"handback/docs/active/daily-pipeline/accuracy";D=R/"receipts"/stem;D.mkdir(parents=True,exist_ok=True)
inputs=[W/"verification.json"]+[O/p for p in ["run-review.py","seal-review.py","fresh-application-proof.json","independent-absent.json","independent-present.json","independent-absent.log","independent-present.log","test_q4_normal_intake.py.diff","q4_intake_fixtures.py.diff","base-git-blobs.raw"]]
for p in inputs[1:]:shutil.copyfile(p,D/p.name)
closure=dict(schemaVersion=1,verdict="PASS",baseGitBlobFilesVerifiedAfterTests=verified,onlyChangedBasePaths=sorted(changed),rawGitLsTreeSha256=sha(raw),protectedOther81PinsVerified=V["protectedOther81ImplementationPins"],workerVerification=dict(path=str(W/"verification.json"),sha256=sha(vraw)),workerLogGzipAndRawHashesAuthenticated=logs,consultedInputSealsAfterTests={str(p):seal(p)for p in inputs},sourceRequests=0,modelRequests=0,finishWrites=0,frozenArchiveWrites=0)
(D/"post-test-closure.json").write_text(json.dumps(closure,indent=2)+"\n")
review=dict(schemaVersion=1,kind="independent_test_only_CI_portability_delta_review",verdict="PASS",findings=[],reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseCommit=P["base"],reviewedFiles=P["onlyOverlays"],baseReconstruction=dict(gitBlobFilesVerifiedBeforeAndAfter=2569,onlyTwoTestOverlays=True,rawGitLsTreeSha256=sha(raw)),independentAbsent=json.loads((O/"independent-absent.json").read_bytes()),independentPresent=json.loads((O/"independent-present.json").read_bytes()),workerFullSuiteAuthenticated=V["tests"],protectedOther81PinsVerified=81,additionalUniqueAdversarialChecks=3,additionalChecksRunInEachMode=True,mockAttribution=dict(guardOnlyImporterTests="Explicitly supplied checked preflight result; not complete unmocked seed validation.",fullArchivePositiveTests="Two retained unmocked seed/current-state and six-correction-admission positives run present; explicitly skip only when external archive absent.",quotaTest="Real Pipeline, SubscriptionAgent, GuardedRunner and temporary writable LocalStore; synthetic transport/login status; no model execution."),preservedFailure=dict(actualHostedRun="40197621420",attribution="Parent/worker supplied actual setup failure; runtime canary not reached. No new hosted run claimed.",localInitialFullAbsentDriver="Three loader import errors retained in worker gzip; corrected harness full rerun passed; initial run not counted as successful."),limits=dict(actualHostedCI="Pending root rerun; local absence simulation only.",JActivationOrAcknowledgementCredit=False,publicationOrCoverageOrFreshnessCredit=False,sourceRequests=0,modelRequests=0,frozenArchiveWrites=0,realAccountSessionBudgetWrites=0,runtimePolicyPackageChanges=0,finishWrites=0),priorSealedReviews="Original implementation106-check review, original83-path worker verification and selected-J test delta unchanged. Separate two-file replacement review only.",receiptsRelative="receipts/"+stem)
(R/(stem+".json")).write_text(json.dumps(review,indent=2)+"\n")
md="""# Q4 normal-intake CI portability review

PASS. The two-file test repair can proceed to hosted CI. No material finding remains.

The reviewed application is a fresh export of `f32946c11f7db4bf3b63fc0380780ab9bf5d6836` with only `ops/ci/test_q4_normal_intake.py` and `ops/ci/q4_intake_fixtures.py` overlaid. All 2,569 Git blob files were checked before and after tests. Only those two files differ; the other 81 original implementation pins match.

| Check | Independent result |
|---|---|
| Retained archive available | 14 passed, no skips |
| External archive absent; frozen reads denied | 12 passed; exactly two full-archive positives skipped; zero frozen-read attempts |
| Fixed committed package | All 55 payloads, 4,742,948 bytes authenticated in both modes |
| Corrupt payload, missing package, missing Q4 proof | Each rejected in both modes; none silently skipped |
| Worker full suite, authenticated logs | Present: 935 passed. Absent: 896 passed, 39 skipped, no errors/failures; 37 skips already existed and two belong to this repair |

The portable tests execute the 206/323 arrays and 529 inventory rows, exact H/J policy and provenance mutations, ordinary 200/304 transport, dates and unknown dates, future/quiet cases, and quota mechanics. The quota test uses a real Pipeline, SubscriptionAgent, GuardedRunner and isolated LocalStore with synthetic transport/login status and no model execution. Guard-only importer tests explicitly supply their checked preflight result. The two external positives retain complete unmocked validation and all six correction admissions when the archive is present.

The actual hosted setup failure `40197621420` remains a failure before the canary. The worker first local full-absence harness had three import errors; its failed log remains retained, and the corrected full rerun passed. Neither is recast as a successful initial run.

This accepts test portability. Hosted CI and actual J collection/acknowledgement remain separate evidence. It supplies no publication, coverage or freshness credit. No runtime, policy, seed payload, frozen archive, account allowance, or prior sealed review was changed. No source or model request was made.

The companion JSON records exact old/new SHA-256 pins, successful test names, attribution and limits. The receipt folder retains the independent driver, logs, fresh-export proof, Git blob inventory, diffs and post-test closure. Root controls copying and subsequent CI.
"""
(R/(stem+".md")).write_text(md)
index=dict(schemaVersion=1,files={p.name:dict(sha256=sha(p.read_bytes()),bytes=p.stat().st_size)for p in sorted(D.iterdir())if p.is_file()})
(D/"index.json").write_text(json.dumps(index,indent=2)+"\n")
for p in [R/(stem+".md"),R/(stem+".json"),D/"index.json"]:print(str(p),sha(p.read_bytes()),p.stat().st_size)
