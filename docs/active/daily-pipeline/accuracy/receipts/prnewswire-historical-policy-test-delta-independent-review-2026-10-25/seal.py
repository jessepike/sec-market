from pathlib import Path
import hashlib,json,gzip,shutil,datetime
O=Path("/var/tmp/smp-prn-historical-test-delta-independent-20261025");A=Path("/var/tmp/smp-prn-historical-test-delta-20261025/combined-J");W=Path("/mnt/mac/Users/jessepike/.codex/worktrees/prn-dated-window/sec-market");sha=lambda b:hashlib.sha256(b).hexdigest()
old="96f47e4056eb03e3dbaf4a5cf2445696d6ac7c92c50e83ec090330cc8c12cd2d";new="f059f6b45732ef935dbed9a30dc6e5e8f38f41dae8a183e8dd6a08019bfd888e"
original=W/"docs/active/daily-pipeline/accuracy/receipts/prnewswire-historical-policy-test-delta-2026-10-25/original-test_prnewswire_retained_window.py";assert sha(original.read_bytes())==old
p=W/"ops/ci/test_prnewswire_retained_window.py";assert sha(p.read_bytes())==new and p.read_bytes()==(A/"ops/ci/test_prnewswire_retained_window.py").read_bytes()
prior=Path("/var/tmp/smp-prn-independent-20261025/handback/docs/active/daily-pipeline/accuracy");stem0="prnewswire-dated-window-parser-independent-review-2026-10-25"
priorpins={stem0+".md":"928376127ba1347a47e8e9bfd4888abf2688af50de8d362c2ab509cd2b968144",stem0+".json":"e941e8a6bd2d9b379c55e21c5a86cf528b3244493c7c4dea28a265644462dbcf"}
for name,pin in priorpins.items():assert sha((prior/name).read_bytes())==pin
v=W/"docs/active/daily-pipeline/accuracy/receipts/prnewswire-dated-window-parser-implementation-2026-10-25/verification.json";assert sha(v.read_bytes())=="68b0294a34b22e80bc99a77cb1363a5e9968d9b5f6a0792ea15300b7e6f6c7e3"
workerfull=Path("/var/tmp/smp-prn-historical-test-delta-20261025/full-present.log").read_bytes();assert b"Ran 961 tests"in workerfull and workerfull.rstrip().endswith(b"OK")
base=json.loads((O/"combined-base-verification.json").read_bytes());present=json.loads((O/"present.json").read_bytes());absent=json.loads((O/"absent.json").read_bytes());assert present["verdict"]==absent["verdict"]=="PASS"
stem="prnewswire-historical-policy-test-delta-independent-review-2026-10-25";R=O/"handback/docs/active/daily-pipeline/accuracy";D=R/"receipts"/stem;D.mkdir(parents=True,exist_ok=True)
for name in ["review.py","seal.py","present.json","absent.json","present.log","absent.log","test-only.diff","combined-base-blobs.raw","combined-base-verification.json"]:shutil.copyfile(O/name,D/name)
shutil.copyfile(original,D/"original-sealed-test.py");z=gzip.compress(workerfull,mtime=0);(D/"worker-combined-J-full-ops.log.gz").write_bytes(z);assert gzip.decompress(z)==workerfull
report=dict(schemaVersion=1,kind="independent_PRN_historical_policy_test_only_delta",verdict="PASS",findings=[],reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseCommit=base["baseCommit"],changedFile=dict(path="ops/ci/test_prnewswire_retained_window.py",oldSha256=old,oldBytes=14277,newSha256=new,newBytes=14809),onlyChange="Load committed historical H fixture and assert both its raw and canonical digest before replay; active market remains J.",historicalFixture=dict(path="contracts/html-qualification-seeds/8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db/contracts__8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db.json",rawAndCanonicalSha256=present["historicalRawAndCanonicalH"],bytes=204449),combinedBaseProof=base,independentPresent=present,independentAbsent=absent,workerCombinedFullOps=dict(run=961,passed=961,skipped=0,rawSha256=sha(workerfull),rawBytes=len(workerfull),gzipSha256=sha(z),gzipBytes=len(z),attribution="Worker actual combined current-J full-suite raw log authenticated; independent focused runs recorded separately."),priorIndependentReviewSealsPreserved=priorpins,originalWorkerVerificationSha256="68b0294a34b22e80bc99a77cb1363a5e9968d9b5f6a0792ea15300b7e6f6c7e3",boundaries=dict(parserVerifierDescriptorChanges=0,activeJPolicyChanges=0,historicalHToJAuthorityRelaxation=False,sourceRequests=0,modelRequests=0,frozenArchiveWrites=0,checkoutWrites=0,qualificationFreshnessPublicationCredit=False),receiptsRelative="receipts/"+stem)
(R/(stem+".json")).write_text(json.dumps(report,indent=2)+"\n")
md="""# PR Newswire historical-policy test delta review

PASS. The single test setup change is safe for integration with current J. The original parser review and worker receipts remain unchanged.

The test now reads the existing committed 204,449-byte H fixture and checks both its raw and canonical SHA-256, `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`. Historical diagnostic evidence therefore keeps its original policy when the active market contract is J. The parser, retained verifier, descriptor and policy are unchanged.

The reviewed test SHA moves from `96f47e4056eb03e3dbaf4a5cf2445696d6ac7c92c50e83ec090330cc8c12cd2d` to `f059f6b45732ef935dbed9a30dc6e5e8f38f41dae8a183e8dd6a08019bfd888e`. The diff changes only the historical contract load and its two digest assertions.

Independent checks used the fresh combined application from current J commit `40fe14bb41f6b10c8edc8527ef7f78d7b4d0dcf8` with exactly six PRN overlays. All 2,602 base Git blob files were checked; only the accepted build-spec overlay differs among tracked base files. The active contract remains canonical J `47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a`.

| Check | Result |
|---|---|
| Independent retained archive present | 26 passed, no skips |
| Independent archive absent before discovery | 13 portable parser tests passed; 13 retained-evidence tests explicitly skipped; zero frozen-read attempts |
| Current J supplied as original historical H | Rejected in both modes |
| Missing or corrupt historical H fixture | Rejected in both modes before retained proof |
| Worker combined-J full suite | 961 passed, no skips; raw log authenticated |

The absence run denied frozen reads, sockets, subprocesses and LocalStore construction. Portable calendar/date/order/URL/metadata/structure checks continue to execute. Real-body and original-graph checks retain their explicit external-fixture boundary and pass in the separate present run.

No runtime guard or H/J authority boundary was relaxed. This separate test delta provides no source qualification, intake, acknowledgement, freshness or publication credit. No source/model request, frozen write or checkout write occurred. Copying remains root-controlled.
"""
(R/(stem+".md")).write_text(md)
index=dict(schemaVersion=1,files={p.name:dict(sha256=sha(p.read_bytes()),bytes=p.stat().st_size)for p in sorted(D.iterdir())if p.is_file()});(D/"index.json").write_text(json.dumps(index,indent=2)+"\n")
for p in [R/(stem+".md"),R/(stem+".json"),D/"index.json"]:print(str(p),sha(p.read_bytes()),p.stat().st_size)
