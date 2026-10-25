from pathlib import Path
import json,hashlib,gzip,shutil,datetime
O=Path("/var/tmp/smp-priority-two-corrections-independent-20261025");W=Path("/mnt/mac/Users/jessepike/.codex/worktrees/priority-corrections/sec-market");A=Path("/var/tmp/smp-priority-two-corrections-20261025/application");D0=W/"docs/active/daily-pipeline/accuracy/receipts/priority-two-correction-integration-2026-10-25";F=Path("/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted")
sha=lambda b:hashlib.sha256(b).hexdigest()
def seal(p):
 s=p.stat();b=p.read_bytes();return dict(sha256=sha(b),bytes=len(b),mtimeNs=s.st_mtime_ns)
vraw=(D0/"verification.json").read_bytes();assert sha(vraw)=="56b8653e314619189e4302abc22cb0fa2c00ae9ffd69de0f600ce905a0518f7f";v=json.loads(vraw);src=json.loads((D0/"actual-source-and-old-admission-readiness.json").read_bytes())
for path,pin in v["exactOwnedFiles"].items():
 for root in [W,A]:b=(root/path).read_bytes();assert sha(b)==pin["sha256"]and len(b)==pin["bytes"]
for path,pin in src["archiveInputSeals"].items():assert seal(Path(path))==pin,path
assert len(src["archiveInputSeals"])==67 and seal(F/"archive-manifest.json")==src["manifest"]
for path,pin in src["protectedSourcePins"].items():assert seal(W/path)==pin,path
logproof={}
for name,pin in v["logs"].items():
 z=(D0/pin["retainedPath"]).read_bytes();b=gzip.decompress(z);assert sha(z)==pin["gzip"]["sha256"]and len(z)==pin["gzip"]["bytes"]and sha(b)==pin["raw"]["sha256"]and len(b)==pin["raw"]["bytes"]
 logproof[name]=dict(raw=pin["raw"],gzip=pin["gzip"],roundtrip=True,resultLines=[s for s in b.decode().splitlines()if s.startswith(("Ran ","OK","FAILED"))])
render=json.loads((D0/"render-comparison.json").read_bytes())
for row in render["rows"]:
 b=Path(row["path"]).read_bytes();old=Path(row["priorPath"]).read_bytes();assert b==old and sha(b)==row["sha256"]==row["priorSha256"]and len(b)==row["bytes"]
js=json.loads((O/"javascript.log").read_text());present=json.loads((O/"present.json").read_bytes());absent=json.loads((O/"absent.json").read_bytes());history=json.loads((O/"history-check.json").read_bytes());base=json.loads((O/"base-verification.json").read_bytes());assert present["verdict"]==absent["verdict"]=="PASS"and js["policySha256"]==present["outerPolicySha256"]and not js["enabled"]
# No admission index for either proposed group exists in the actual frozen archive.
import sys
sys.path[:0]=[str(A/"web/scripts/pipeline"),str(A/"ops/ci")]
import corrections as C,test_priority_two_corrections as T
market=json.loads((A/"contracts/market.json").read_bytes());context=C.load_policy(A,market);real=T.ReadOnlyJ()
for group in context["requests"]["groups"][6:]:assert real.read(C._index(group,context["reviewPolicySha256ByGroup"][group["id"]]))is None
stem="priority-two-correction-integration-independent-review-2026-10-25";R=O/"handback/docs/active/daily-pipeline/accuracy";D=R/"receipts"/stem;D.mkdir(parents=True,exist_ok=True)
for name in ["review.py","seal.py","present.log","absent.log","present.json","absent.json","initial-driver-error.log","history-check.py","history-check.json","history-check.log","javascript.log","base-git-blobs.raw","base-verification.json"]:shutil.copyfile(O/name,D/name)
closure=dict(schemaVersion=1,workerVerification=seal(D0/"verification.json"),workerReadiness=seal(D0/"actual-source-and-old-admission-readiness.json"),workerLogsAuthenticated=logproof,renderPairsByteExact=render,archiveManifestSeal=src["manifest"],all67ConsultedArchiveSealsVerified=src["archiveInputSeals"],protectedSourceSealsVerified=src["protectedSourcePins"],bothNewActualAdmissionIndicesAbsent=True,oldSixLiteralBlocks=v["oldSixLiteralGroupBlocks"],all12CodeAndRequestPins=v["exactOwnedFiles"])
(D/"closure.json").write_text(json.dumps(closure,indent=2)+"\n")
report=dict(schemaVersion=1,verdict="PASS",findings=[],reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewScope="Exact pending two-group request/stamp integration and historical fixture/test adaptation; no semantic admission or operational execution.",baseCommit=base["baseCommit"],exactReviewed12Pins=v["exactOwnedFiles"],requestAndStamp=dict(rawRequests=present["requestsRawSha256"],canonicalRequests=present["requestsCanonicalSha256"],rawStamp=present["stampRawSha256"],outerPolicy=present["outerPolicySha256"]),independentPresent=present,independentAbsent=absent,independentJavaScript=js,independentSyntheticHistoryProjection=history,baseVerification=base,workerTestsAuthenticated=v["validation"],workerLogResults=logproof,sourceArchive=dict(commit=src["sourceArchiveCommit"],manifest=src["manifest"],entries=src["actualArchiveEntries"],consultedBytesSealed=67),oldSixAdmissionsAndPublicHistoryUnchanged=True,oldSixPublishedDates="2026-10-24 retained exactly",bothNewActualAdmissionIndicesAbsent=True,syntheticLimit="Mocked model acceptance and projection were exercised only in temporary or in-memory reviewer state. These are mechanics, never independent semantic review or publishable admissions.",preservedDiagnostics=dict(worker="Initial fixture/UTC-Z diagnostic log retained; final98/972/absence logs supersede it.",reviewer="Initial extra-check driver lacked write_once on its in-memory adapter; all11 supplied tests already passed. Added adapter-only write_once and reran successfully; failed log retained."),boundaries=dict(sourceRequests=0,modelRequests=0,newRealAdmissions=0,realArchiveSessionBudgetWrites=0,checkoutWrites=0,operationalActivation=False,qualificationCoverageFreshnessPublicationCredit=False),receiptsRelative="receipts/"+stem)
(R/(stem+".json")).write_text(json.dumps(report,indent=2)+"\n")
md="""# Two priority corrections: independent integration review

PASS. The exact pending two-group append and outer policy stamp meet the accepted integration spec. No material finding remains. This accepts preparation and tests; real independent semantic review is still required for both new groups.

The requests contain the exact accepted packet after six byte-identical original group blocks. Varonis retains its three-target atomic withdrawal/end-of-life/evidence repair; SentinelOne retains its two-target planned approximately-8%/estimated-approximately-$25-million repair and exact transport attestation. No proposed value was inserted into an accepted public projection.

| Reviewed pin | SHA-256 |
|---|---|
| Requests, raw | `aa2ffd8722f2e82ecbf4ec152485e2334946469627f3fa04845d441695e201ae` |
| Requests, canonical | `722a0c086d5e7c270f74cc01e317284edbe83a4d290e73127b4dcf8dde12eadc` |
| Build stamp, raw | `58d93745f554563f61960037b4466de70ae058a9b2295272d530d95f639880aa` |
| Outer correction policy | `1c629249347b9bdacaf4fadf563e1a0ed807b96c0cbb02e3e2492ae00a839e5b` |

Independent execution passed all 11 new tests with actual retained sources. Fresh-process absence before discovery passed four portable tests and explicitly skipped seven actual-source tests, with zero frozen-read attempts. The portable tests check exact append/current J identity, outer stamp/baseline preservation, original/source/attestation substitutions and the pending publication hold.

Additional checks called the real release controller with either one or two pending groups. Both stopped before any gate reservation, checkpoint or dispatch. Actual six-group admission replay required no model or reservation. A separately labelled synthetic eight-group projection preserved all six actual public correction rows and their October 24 dates, appended exactly the two new candidate rows on the hypothetical October 26 publication day, and rejected altering older history. No synthetic result was written into the actual archive. Independent JavaScript validation matched the Python outer policy and disabled pending projection.

Both bound 09:56 UTC observations remain genuine 304 responses with their original full-200 chains. Newer actual-J 14:00 UTC observations in archive `8b3811df40cfdbec9d5ed52252524294566c88e0` have exactly the same bodies. The complete texts remain 26,465 and 8,295 characters; neither source clock was rebased. Initial admission must finish by October 26 15:56:21.524634 UTC for Varonis and 15:56:12.797588 UTC for SentinelOne. Inclusive boundaries pass; future/expired start times and completion after expiry fail. Both new actual admission indices are absent.

All 2,662 base Git blob files were checked against commit `2387abb41069f3a74a005468d91e5401d97089ff`. Only the expected eight tracked paths differ, with four additional fixture/test files, and all twelve pins match the isolated application and worktree. Runtime/caller/transport/workflow files, current J, original inventories, factual and daily baselines, accepted views, old six group-policy hashes and actual admission references remain unchanged. Historical tests use separately hash-pinned six-group fixtures; they do not truncate the current eight-group inventory.

Authenticated worker evidence records 98 affected tests and 972 full operational tests passing with no skips. Hosted absence records 913 passes and 59 explicit retained-fixture skips, with no frozen reads. The build verifies all 80 SEC claims with no blockers or drift. Four new 1440/390 captures are byte-identical to their respective earlier production/local surfaces; an existing local-versus-production fixture difference remains explicit. These captures do not show the pending proposals as public corrections.

The worker initial fixture/UTC-Z diagnostic and an independent in-memory-adapter setup error remain retained and are not counted as passing runs. Final code, logs and closing seals supersede those diagnostics.

The JSON and receipt folder retain all twelve pins, exact test names, counter/clock guards, synthetic attribution, authenticated full logs, 67 consulted archive input seals and manifest, old history hashes, render comparisons and the base inventory proof. No source/model request, real admission, account allowance change, checkpoint or checkout write occurred. Root owns reviewed integration and subsequent execution with naturally renewed UTC capacity.
"""
(R/(stem+".md")).write_text(md)
index=dict(schemaVersion=1,files={p.name:dict(sha256=sha(p.read_bytes()),bytes=p.stat().st_size)for p in sorted(D.iterdir())if p.is_file()});(D/"index.json").write_text(json.dumps(index,indent=2)+"\n")
for p in [R/(stem+".md"),R/(stem+".json"),D/"index.json"]:print(str(p),sha(p.read_bytes()),p.stat().st_size)
