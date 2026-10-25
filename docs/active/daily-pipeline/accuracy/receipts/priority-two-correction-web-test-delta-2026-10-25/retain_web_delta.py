from pathlib import Path
import gzip,hashlib,json,shutil,subprocess
REPO=Path("/mnt/mac/Users/jessepike/.codex/worktrees/priority-corrections/sec-market")
BASE=Path("/var/tmp/smp-priority-two-corrections-20261025")
OUT=REPO/"docs/active/daily-pipeline/accuracy/receipts/priority-two-correction-web-test-delta-2026-10-25"
OUT.mkdir(parents=True,exist_ok=True)
def pin(p):
 b=Path(p).read_bytes();return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
pins=json.loads((BASE/"web-test-delta-pins.json").read_bytes())
original=json.loads((BASE/"handback-index.json").read_bytes())
for name,expected in original["files"].items():assert pin(REPO/name)==expected,name
for name,expected in pins.items():assert pin(REPO/name)==expected and pin(BASE/"application"/name)==expected,name
logs={}
for label,name in (("initial-historical-fixture-failure","full-web-tests.log"),("final-full-web-pass","full-web-tests-final.log")):
 source=BASE/name;b=source.read_bytes();dest=OUT/(label+".log.gz");dest.write_bytes(gzip.compress(b,mtime=0));assert gzip.decompress(dest.read_bytes())==b
 logs[label]={"originalPath":str(source),"raw":pin(source),"gzipFile":dest.name,"gzip":pin(dest),"roundtripExact":True}
final=(BASE/"full-web-tests-final.log").read_text()
assert "# tests 379\n" in final and "# pass 379\n" in final and "# fail 0\n" in final
assert "Ran 115 tests" in final and "42 passed" in final and "1 skipped" in final
assert '"required":80,"verified":80,"blockers":0,"drift":0' in final
patch=subprocess.check_output(["git","-C",str(REPO),"diff","--",*pins])
(OUT/"three-test-only.patch").write_bytes(patch)
shutil.copyfile(__file__,OUT/"retain_web_delta.py")
result={"schemaVersion":1,"verdict":"PASS_FULL_WEB_WITH_HISTORICAL_SIX_TEST_FIXTURES","deltaFiles":pins,"original31WorkerFilesPreservedExact":True,"originalWorkerManifest":pin(BASE/"handback-index.json"),"runtimeAndRequestStampChanges":0,"newSkips":0,"historicalRequests":{"path":"ops/ci/fixtures/accepted-six-correction-requests-2026-10-25.json",**pin(REPO/"ops/ci/fixtures/accepted-six-correction-requests-2026-10-25.json")},"historicalStamp":{"path":"ops/ci/fixtures/accepted-six-correction-stamp-J-2026-10-25.json",**pin(REPO/"ops/ci/fixtures/accepted-six-correction-stamp-J-2026-10-25.json")},"validation":{"lintErrors":0,"preExistingLintWarnings":1,"data":{"passed":379,"skipped":0},"pipeline":{"passed":115},"build":{"requiredSec":80,"verifiedSec":80,"blockers":0,"drift":0},"browser":{"passed":42,"existingFixtureSkips":1}},"logs":logs,"applicationRoot":str(BASE/"application"),"overlay":"Original reviewed12-file pending-only overlay plus exactly these3 historical test fixture changes; all production code identical.","initialFailure":"Ten historical data fixture failures stopped the first npm run before pipeline/build/browser. Existing production guards correctly rejected mismatched synthetic inventories. Original failed log is retained; final full-stage run supersedes it.","requests":0,"models":0,"admissions":0,"archiveWrites":0,"publication":False}
(OUT/"verification-addendum.json").write_text(json.dumps(result,indent=2)+"\n")
index={p.name:pin(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!="receipt-index.json"}
(OUT/"receipt-index.json").write_text(json.dumps({"schemaVersion":1,"files":index},indent=2)+"\n")
print(json.dumps({"receiptIndex":pin(OUT/"receipt-index.json"),"verification":pin(OUT/"verification-addendum.json"),"rawFinalLog":logs["final-full-web-pass"]["raw"],"files":len(index)+1}))
