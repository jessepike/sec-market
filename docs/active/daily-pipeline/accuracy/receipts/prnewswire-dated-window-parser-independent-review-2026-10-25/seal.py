from pathlib import Path
import json,hashlib,gzip,shutil,datetime
O=Path("/var/tmp/smp-prn-independent-20261025");A=Path("/mnt/mac/Users/jessepike/.codex/worktrees/prn-dated-window/sec-market");W=A/"docs/active/daily-pipeline/accuracy/receipts/prnewswire-dated-window-parser-implementation-2026-10-25"
sha=lambda b:hashlib.sha256(b).hexdigest()
def seal(p):
 s=p.stat();b=p.read_bytes();return dict(sha256=sha(b),bytes=len(b),mtimeNs=s.st_mtime_ns)
vraw=(W/"verification.json").read_bytes();assert sha(vraw)=="68b0294a34b22e80bc99a77cb1363a5e9968d9b5f6a0792ea15300b7e6f6c7e3";v=json.loads(vraw)
for path,pin in v["codeAndSpecPins"].items():
 b=(A/path).read_bytes();assert sha(b)==pin["sha256"]and len(b)==pin["bytes"]
for path,pin in v["protectedTrackedFilesUnchangedFromBase"].items():
 b=(A/path).read_bytes();assert sha(b)==pin["sha256"]and len(b)==pin["bytes"]
logs={}
for name,pins in v["testLogs"].items():
 b=(W/pins["gzip"]["file"]).read_bytes();r=gzip.decompress(b)
 assert sha(b)==pins["gzip"]["sha256"]and len(b)==pins["gzip"]["bytes"]and sha(r)==pins["raw"]["sha256"]and len(r)==pins["raw"]["bytes"]
 logs[name]=[line for line in r.decode().splitlines()if line.startswith(("Ran ","OK","FAILED"))]
raw=(W/v["actualReplay"]["file"]).read_bytes();assert sha(raw)==v["actualReplay"]["sha256"];replay=json.loads(raw)
for path,pin in (replay["archiveInputs"]|replay["externalAndProtectedSeals"]).items():assert seal(Path(path))==pin,path
assert len(replay["archiveInputs"])==461 and len(replay["externalAndProtectedSeals"])==21
F=Path("/var/tmp/smp-listing-pagination-actual-40193925490-20261025/extracted/archive-manifest.json");assert seal(F)==replay["manifestSeal"]
present=json.loads((O/"independent-review.json").read_bytes());absent=json.loads((O/"absent.json").read_bytes())
assert present["verdict"]==absent["verdict"]=="PASS"
stem="prnewswire-dated-window-parser-independent-review-2026-10-25";R=O/"handback/docs/active/daily-pipeline/accuracy";D=R/"receipts"/stem;D.mkdir(parents=True,exist_ok=True)
for p in [O/"review.py",O/"review.log",O/"independent-review.json",O/"absent.py",O/"absent.json",O/"absent.log",O/"seal.py"]:shutil.copyfile(p,D/p.name)
closure=dict(schemaVersion=1,verdict="PASS",workerVerification=seal(W/"verification.json"),workerLogsAuthenticated=logs,all461ArchiveInputsAnd21ExternalSealsRechecked=True,archiveManifestSeal=replay["manifestSeal"],workerProtectedTrackedPinsVerified=v["protectedTrackedFilesUnchangedFromBase"],workerCodeAndSpecPinsVerified=v["codeAndSpecPins"],frozenArchiveWrites=0,repoWrites=0)
(D/"closure.json").write_text(json.dumps(closure,indent=2)+"\n")
report=dict(schemaVersion=1,verdict="PASS",findings=[],reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope="Pure retained PRN parser and closed proposal verifier only; no caller or policy activation.",reviewedPins=v["codeAndSpecPins"],archive=replay["originalArchive"],independentPresent=dict(testsRun=26,passed=26,skipped=0,extraNegatives=21,positiveSourceLocalePathPairs=12,fullOriginalDiagnosticReplays=2,sixAdmissionReplay=True),independentAbsent=absent,sourceResults=present["sourceCounts"],workerSuite=dict(run=947,passed=947,skipped=0,attribution="Worker full-suite lossless gzip authenticated; independent focused suite rerun separately."),authorityChecks=["Exact H and descriptor canonical digest fixed before source proof", "External actual audit files pinned and independently read", "Both complete original diagnostic run/raw-plan/reservation/observation/body graphs replay with unchanged verifier", "Altered or rehashed authored descriptor/report, omitted history/seed gap and replaced external proof reject", "Head canonical/prev/next metadata URLs are separate from body-pager request URLs", "Source-specific locale/path pairs preserve literal identities without normalization"],limits=dict(qualified=False,sourceChecksCredited=0,modelCalls=0,operationalIntake=False,sourceRequests=0,coverageOrFreshnessOrPublicationCredit=False,knownOlderHistory="Cato prefix not complete; two absent known seeds both precede Sep25 and remain explicit scope/history gap; no whole-history prerequisite or universal recall claim.",hostedCI="Fresh-process local absence simulation only; no new GitHub receipt.",mainOrCallerIntegration="Not reviewed or activated by this offline unit."),preservation=dict(archiveInputsRehashedAndSealsVerified=461,externalProtectedInputsRehashedAndSealsVerified=21,manifestHashVerified=True,protectedTrackedPinsUnchanged=15,frozenWrites=0,checkoutWrites=0),receiptsRelative="receipts/"+stem)
(R/(stem+".json")).write_text(json.dumps(report,indent=2)+"\n")
md="""# PR Newswire retained parser independent review

PASS. The pure parser and closed retained-proposal verifier satisfy the accepted offline scope. No material finding remains.

Independent execution passed all 26 focused tests, including both full original diagnostic replays and all six existing correction admissions. Another 21 rejection checks and all 12 observed source-specific language/path pairs passed. The worker 947-test full-suite log was hash-checked and decompressed without loss; it records 947 passes and no skips.

| Actual retained stream | Observed URLs | Known union | Current calendar window | Daily window | Older history |
|---|---:|---:|---:|---|---|
| Cato | 125 | 127 | 2 | Complete under the recognized ordering contract | Incomplete; pages 6–8 remain disclosed |
| Chainguard | 47 | 47 | 5 | Complete under the recognized ordering contract | Captured terminal on page 2 |

The Cato union preserves two known seeds absent from the captured list. Their supplied publication days are February 24 and July 27, 2026, both earlier than the September 25 cutoff. They remain a source-scope/history gap and supply no observed current-window counterexample. The review imposes no universal whole-history prerequisite and makes no universal recall claim.

The observed two card wrappers, leaf localized titles, source-specific locale paths and exact retained Cato language-menu token are supported by the pinned bodies. Metadata-only canonical and previous/next URLs stay separate from body-pager request URLs. Equal timestamps and dates across page boundaries pass. Unknown dates retain their URL and prevent completion; future dates stay explicit, and no index timezone is inferred.

The retained proof fixes the original H contract and descriptor, hashes external actual audits, replays the original run/plan/transport graph, and derives the complete report again. Rehashed descriptor substitutions, altered external audit bytes, omitted seed/history evidence, false qualification and supplied primary identity/date conflicts reject. Actual 304 chains retain their older full-200 origin and original clocks.

A fresh-process absence test hid the VM archive before discovery and denied frozen reads, network, subprocesses and LocalStore construction. All 26 tests were discovered: the 13 portable parser/date/structure/URL/pager tests passed and 13 retained-evidence tests explicitly skipped, with zero frozen-read attempts. Those skips are one actual-list test plus twelve retained-report tests, including their real-body mutations. Their archive-dependent coverage is supplied by the separate all-26 present run; it is not represented as portable coverage.

All 461 retained archive input seals, the manifest, 21 external/protected seals and 15 protected tracked pins were checked. No caller, policy, source registry, seed, correction, source clock, allowance or archive was changed. No source/model request was made. Qualification, ordinary intake and public acceptance remain separate future work. This review gives no coverage, freshness or publication credit.

The companion JSON records exact file pins, test names, limits and the two older Cato seeds. Safe receipts retain the independent present/absence drivers and logs plus the closing seals. The review remains outside the finish checkout until root releases copying.
"""
(R/(stem+".md")).write_text(md)
index=dict(schemaVersion=1,files={p.name:dict(sha256=sha(p.read_bytes()),bytes=p.stat().st_size)for p in sorted(D.iterdir())if p.is_file()});(D/"index.json").write_text(json.dumps(index,indent=2)+"\n")
for p in [R/(stem+".md"),R/(stem+".json"),D/"index.json"]:print(str(p),sha(p.read_bytes()),p.stat().st_size)
