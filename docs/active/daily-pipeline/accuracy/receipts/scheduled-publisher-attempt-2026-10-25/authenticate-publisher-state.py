import subprocess,json,hashlib,base64,os
from pathlib import Path
B=Path(__file__).parent;OLD=Path("/var/tmp/smp-q4-primary-actual-40188161705-20261025/extracted");OUT=B/"post-publisher-extracted"
H=lambda b:hashlib.sha256(b).hexdigest()
def api(route,*args):return subprocess.check_output(["mac","gh","api",*args,route])
run=json.loads(api("repos/jessepike/sec-market/actions/runs/40190348786"));assert run["status"]=="completed",run["status"]
assert run["event"]=="schedule" and run["head_branch"]=="main" and run["head_sha"]=="900a51f9875838417dfd3a189457595ba19d578f"
(B/"publisher-run.json").write_text(json.dumps(run,indent=2)+"\n")
a=json.loads(api("repos/jessepike/sec-market/actions/runs/40190348786/artifacts"))["artifacts"];a=[v for v in a if v["name"]=="daily-publication-receipt"];assert len(a)==1
import io,zipfile
zbytes=api("repos/jessepike/sec-market/actions/artifacts/"+str(a[0]["id"])+"/zip");assert not a[0].get("digest") or a[0]["digest"]=="sha256:"+H(zbytes)
with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
 assert z.namelist()==["smp-publish-receipt.json"];raw=z.read(z.namelist()[0])
(B/"publisher-artifact.zip").write_bytes(zbytes);(B/"publisher-receipt.json").write_bytes(raw);(B/"publisher-artifact.json").write_text(json.dumps({**a[0],"zipSha256":H(zbytes),"rawReceiptSha256":H(raw),"rawReceiptBytes":len(raw)},indent=2)+"\n")
ref=json.loads(api("repos/jessepike/sec-market/git/ref/archive/market-evidence"));commit=ref["object"]["sha"]
metadata=json.loads(api("repos/jessepike/sec-market/git/commits/"+commit));tree=json.loads(api("repos/jessepike/sec-market/git/trees/"+metadata["tree"]["sha"]));me=next(v for v in tree["tree"] if v["path"]=="archive-manifest.json")
blob=json.loads(api("repos/jessepike/sec-market/git/blobs/"+me["sha"]));mb=base64.b64decode(blob["content"]);assert hashlib.sha1(("blob "+str(len(mb))+"\0").encode()+mb).hexdigest()==me["sha"]
nm=json.loads(mb);om=json.loads((OLD/"archive-manifest.json").read_bytes());old={e["key"]:e for e in om["files"]};new={e["key"]:e for e in nm["files"]}
missing=sorted(set(old)-set(new));changed=[k for k in old if k in new and old[k]!=new[k]];added=sorted(set(new)-set(old));assert not missing;assert all(k.startswith("state/") for k in changed+added)
OUT.mkdir(exist_ok=False)
for e in nm["files"]:
 k=e["key"];assert ".." not in Path(k).parts and not Path(k).is_absolute();p=OUT/k;p.parent.mkdir(parents=True,exist_ok=True)
 if k in old and old[k]==e:os.link(OLD/k,p)
 else:
  body=api("repos/jessepike/sec-market/contents/"+k+"?ref="+commit,"-H","Accept: application/vnd.github.raw+json");assert H(body)==e["sha256"] and len(body)==e["bytes"],k;p.write_bytes(body)
(OUT/"archive-manifest.json").write_bytes(mb)
for e in nm["files"]:
 body=(OUT/e["key"]).read_bytes();assert H(body)==e["sha256"] and len(body)==e["bytes"],e["key"]
for key,value in (("post-publisher-ref.json",ref),("post-publisher-git-commit.json",metadata),("post-publisher-root-tree.json",tree)):(B/key).write_text(json.dumps(value,indent=2)+"\n")
proof={"actualScheduledPublisherRunId":"40190348786","publisherConclusion":run["conclusion"],"publisherReceipt":json.loads(raw),"baselineActualPrimaryCaptureCommit":"d2efafcb8a68d7330e4b700613b29f18b9892346","archiveCommit":commit,"gitParentCommits":[p["sha"] for p in metadata["parents"]],"manifestSha256":H(mb),"manifestGitBlobSha1":me["sha"],"manifestBytes":len(mb),"manifestEntries":len(nm["files"]),"missingEntries":missing,"changedEntries":changed,"addedEntries":added,"allManifestEntriesVerified":True,"extractedRoot":str(OUT),"materialization":"Unchanged immutable bytes hardlinked from authenticated collector archive; changed and new bytes retrieved from exact Git commit and independently hash checked. No source archive writes."}
(B/"post-publisher-proof.json").write_text(json.dumps(proof,indent=2)+"\n");print(json.dumps(proof,indent=2))
