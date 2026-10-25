import sys,json,hashlib,gzip,re,io,contextlib,socket,subprocess,urllib.request,importlib.util,datetime
from pathlib import Path
B=Path(__file__).parent;APP=B/"application";ARCHIVE=Path("/var/tmp/smp-scheduled-monitor-acceptance-20261025/scheduled-publisher-40190348786/post-publisher-extracted");PUB=Path("/var/tmp/smp-scheduled-monitor-acceptance-20261025/scheduled-publisher-40190348786")
sys.path.insert(0,str(APP/"web/scripts/pipeline"));from contracts import canonical,digest,instant,plan_run
from provenance import GitHubAuthority
import storage
seals={}
def read(p):
 raw=p.read_bytes();v={"sha256":digest(raw),"bytes":len(raw),"mtimeNs":p.stat().st_mtime_ns};key=str(p);assert key not in seals or seals[key]==v;seals[key]=v;return raw
def J(p):return json.loads(read(p))
run=J(B/"github-run.json");jobs=J(B/"github-jobs.json");actual=J(B/"actual-monitor-result.json");issue=J(B/"issue10-after.json");assert run["event"]=="schedule" and run["head_branch"]=="main" and run["head_sha"]=="bd38e818f4aa7d2bae2169178a02047d252b260c";assert {j["name"]:j["conclusion"] for j in jobs["jobs"]}=={"daily-pipeline":"failure","probe":"success"}
log=gzip.decompress(read(B/"daily-pipeline.log.gz")).decode();plain="\n".join(re.sub(r"^\d{4}-\d\d-\d\dT\S+ ","",line) for line in log.splitlines());assert re.search(r"Ran 36 tests in [^\n]+\n\nOK(?:\n|$)",plain) and "(skipped=" not in plain
assert not any(r in actual["reasons"] for r in ("INDEPENDENT_PROBE_FAILED","SCHEDULED_COLLECTION_RECEIPT_DIFFERS","SCHEDULED_COLLECTION_RECEIPT_MISSING"));assert actual["scheduledRunUrl"].endswith("/40182324149") and actual["successfulTasks"]==264 and actual["requiredTasks"]==557
for p in sorted(APP.rglob("*")):
 if p.is_file():read(p)
contract=J(APP/"contracts/market.json");assert digest(contract)=="8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db"
fixtures=B/"github-fixtures";gate=J(fixtures/"gate-run.json");artifact=J(fixtures/"gate-artifact.json");zipraw=read(fixtures/"gate-artifact.zip");collector=J(fixtures/"collector-run.json");assert artifact["digest"]=="sha256:"+digest(zipraw)
requests=[];netdenied=[]
def denied(*args,**kwargs):netdenied.append("denied");raise AssertionError("offline verifier forbids transport or process")
socket.socket.connect=denied;socket.create_connection=denied;subprocess.run=denied;storage.LocalStore.__init__=denied
apiFixtures={"actions/runs/40182324149":collector,"actions/workflows/subscription-collector.yml/runs?event=schedule&per_page=10":{"workflow_runs":[collector]},"actions/runs/40172376435":gate,"actions/artifacts/12590843044":artifact,"actions/artifacts/12590843044/zip":zipraw}
def fixtureRunner(args,**kwargs):
 assert args[:2]==["gh","api"];path=args[2];prefix="repos/jessepike/sec-market/";assert path.startswith(prefix);key=path[len(prefix):];assert key in apiFixtures,key;value=apiFixtures[key];requests.append(key);return subprocess.CompletedProcess(args,0,value if isinstance(value,bytes) else canonical(value),b"")
authority=GitHubAuthority(runner=fixtureRunner)
spec=importlib.util.spec_from_file_location("actual_watchdog",APP/"ops/watchdog/probe.py");probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
archiveReads=[]
def readArchive(key,reference=None):
 assert ".." not in Path(key).parts and not Path(key).is_absolute();raw=read(ARCHIVE/"state"/key)
 if reference:assert len(raw)==reference["bytes"] and digest(raw)==reference["sha256"]
 archiveReads.append(key);return json.loads(raw)
public={}
for name in ("app-release.json","deployment-receipt.json","daily-coverage.json","factual-corrections.json"):
 p=PUB/("public-"+name+(".gz" if name=="daily-coverage.json" else ""));raw=read(p);public["https://securitymarketpulse.com/"+name]=gzip.decompress(raw) if name=="daily-coverage.json" else raw
liveReads=[];mutate=False
class Response:
 def __init__(self,url,body):self.status=200;self.url=url;self.buffer=io.BytesIO(body)
 def __enter__(self):return self
 def __exit__(self,*args):return False
 def read(self,count=-1):return self.buffer.read(count)
def fixtureUrlopen(request,timeout=None):
 url=request.full_url;assert url in public;body=public[url]
 if mutate and url.endswith("/daily-coverage.json"):body=body[:-1]+(b" " if body[-1:]!=b" " else b"\n")
 liveReads.append({"url":url,"fixtureBytes":len(body)});return Response(url,body)
probe.urllib.request.urlopen=fixtureUrlopen;probe.GitHubAuthority=lambda:authority;probe.utcnow=lambda:actual["checkedAt"]
def pinnedAPI(path,raw=False):
 if path=="git/ref/archive/market-evidence":return {"object":{"sha":"496ad86ade09969edab9d79d96f24bbab0a8e3e0"}}
 prefix="contents/state/";assert path.startswith(prefix) and path.endswith("?ref=496ad86ade09969edab9d79d96f24bbab0a8e3e0");key=path[len(prefix):].split("?ref=")[0];body=read(ARCHIVE/"state"/key);archiveReads.append(key);return body if raw else json.loads(body)
probe.api=pinnedAPI
oldargv=sys.argv;sys.argv=["probe.py"]
with contextlib.redirect_stdout(io.StringIO()) as output:exitcode=probe.main()
sys.argv=oldargv;replayed=json.loads(output.getvalue());assert exitcode==2 and replayed=={k:v for k,v in actual.items() if k!="notification"},(replayed,actual)
# Exercise the actual accepted-inventory reader and original-plan binder on real retained records.
prod=readArchive("heads/production.json");saved=readArchive("releases/"+prod["releaseId"]+".json");manifest=saved["manifest"];test=readArchive("gate-receipts/40172376435.json");expected=probe._accepted_coverage_inventory(manifest,test,readArchive);assert expected["bytes"]==1337257 and expected["sha256"]=="ac8068379c6c79760331711bfb7bb6387fbc639f9ab6f921713502c6982d47fc"
mutate=True
try:probe.get_json(probe.PUBLIC_COVERAGE_URL,expected=expected);raise AssertionError("tampered real public body accepted")
except ValueError as error:assert "differs from accepted artifact bytes" in str(error)
mutate=False
latest=readArchive("heads/latest-run.json");private=readArchive(latest["receipt"]["key"],reference=latest["receipt"]);publicCoverage=json.loads(public[probe.PUBLIC_COVERAGE_URL]);privatePlan=probe._original_plan(contract,private,readArchive);publicPlan=probe._original_plan(contract,publicCoverage,readArchive);assert privatePlan==publicPlan
bad=dict(privatePlan);bad["scheduledAt"]="2026-10-26T06:45:06.886154Z"
try:probe._original_plan(contract,private,plan=bad);raise AssertionError("changed original plan accepted")
except ValueError:pass
snapshot=readArchive("heads/dailySnapshot.json");acceptedSnapshot=readArchive(manifest["snapshot"]["key"],reference=manifest["snapshot"]);heartbeat=readArchive("heads/worker-heartbeat.json");assert heartbeat["sessionId"]=="github-publisher-40190348786-1" and heartbeat["phases"]=={"failed":2}
assert len(snapshot["reviewQueue"])==38 and len(acceptedSnapshot["reviewQueue"])==37
assert instant(actual["checkedAt"])<instant(publicCoverage["validUntil"]) and publicCoverage["validUntil"]=="2026-10-26T12:45:29.479727+00:00";assert snapshot["coverage"]["validUntil"]=="2026-10-26T15:55:27.307096+00:00"
assert actual["checkedAt"] in issue["body"] and all(r in issue["body"] for r in actual["reasons"]) and issue["state"]=="open" and [v["login"] for v in issue["assignees"]]==["jessepike"]
for k,v in seals.items():
 p=Path(k);raw=p.read_bytes();assert v=={"sha256":digest(raw),"bytes":len(raw),"mtimeNs":p.stat().st_mtime_ns}
result={"schemaVersion":1,"actualRunId":"40191154739","actualEvent":"schedule","actualHeadSha":run["head_sha"],"watchdogTests":36,"watchdogSkips":0,"actualWorkflowConclusion":"failure","monitorReaderAndBindingAcceptance":"PASS","actualResult":actual,"offlineExactMainReplayMatchesActualResult":True,"offlineReplayExitCode":2,"replayArchiveCommit":"496ad86ade09969edab9d79d96f24bbab0a8e3e0","actualMonitorArchiveCommit":"not emitted by the monitor; no later ref is attributed to its read","postRunObservedArchiveRef":J(B/"observed-archive-ref.json")["object"]["sha"],"replayBoundary":"Reused the authenticated frozen post-publisher baseline and authentic retained public/GitHub fixtures. Normal records reproduce actual output exactly. This replay does not claim its chosen archive commit was the unlogged actual monitor read head.","acceptedPublicInventoryEntry":expected,"actualLargeReaderReached":True,"tamperedSameSizePublicBodyRejected":True,"originalPrivateAndPublicPlan":{"runId":privatePlan["runId"],"scheduledAt":privatePlan["scheduledAt"],"previousRunId":privatePlan.get("previousRunId"),"planSha256":digest(privatePlan),"inventoriesReconstructExactly":True,"wrongOriginalPlanRejected":True},"scheduledCollector":{"id":collector["id"],"event":collector["event"],"headSha":collector["head_sha"],"conclusion":collector["conclusion"],"receiptMismatchAbsent":True},"privateState":{"intake":{"checked":264,"required":557,"gaps":293},"processing":private["processing"],"historicalReview":private["historicalReview"],"heldQueue":38,"validUntil":snapshot["coverage"]["validUntil"]},"acceptedPublicState":{"releaseId":prod["releaseId"],"appRevision":manifest["appRevision"],"snapshotSha256":manifest["snapshot"]["sha256"],"intake":{"checked":264,"required":557,"gaps":293},"processing":publicCoverage["processing"],"historicalReview":publicCoverage["historicalReview"],"heldQueue":37,"validUntil":publicCoverage["validUntil"],"notExpiredAtActualCheck":True},"workerPhaseFailure":{"sessionId":heartbeat["sessionId"],"phases":heartbeat["phases"],"reason":"Actual scheduled publisher failed at the spent daily gate; this is not a new collector failure or reader exception."},"issue":{"number":10,"state":issue["state"],"updatedAt":issue["updated_at"],"assignees":[v["login"] for v in issue["assignees"]],"body":issue["body"]},"independentProbeFailureAbsent":True,"noInventedExpiry":True,"sourceAndModelRequests":0,"verifierPublicRequests":0,"verifierArchiveWrites":0,"LocalStoreConstructionDenied":True,"socketAndSubprocessDenied":True,"deniedAttempts":len(netdenied),"fixtureGitHubCalls":requests,"fixturePublicReads":liveReads,"originalArchiveReads":sorted(set(archiveReads)),"inputSeals":seals,"inputSealsUnchanged":True}
(B/"replay-proof.json").write_bytes(canonical(result));print(json.dumps({k:result[k] for k in ("monitorReaderAndBindingAcceptance","watchdogTests","watchdogSkips","offlineExactMainReplayMatchesActualResult","tamperedSameSizePublicBodyRejected","originalPrivateAndPublicPlan","independentProbeFailureAbsent","inputSealsUnchanged")},indent=2))
