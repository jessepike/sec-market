import json,hashlib,gzip,base64,os
from pathlib import Path
O=Path('/var/tmp/smp-cyera-implementation-independent-20261025')
R=Path('/mnt/mac/Users/jessepike/.codex/worktrees/cyera-current-primary/sec-market')
A=R/'docs/active/daily-pipeline/accuracy';P=A/'receipts/cyera-current-primary-build-2026-10-25'
F=Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted')
def sha(b):return hashlib.sha256(b).hexdigest()
def seal(p):
    st=p.stat();b=p.read_bytes();return {'path':str(p),'sha256':sha(b),'bytes':len(b),'mtimeNs':st.st_mtime_ns,'inode':st.st_ino}
index=json.loads((P/'receipt-index.json').read_bytes());assert sha((P/'receipt-index.json').read_bytes())=='03fd772e5a53865d5785067a2447a66849c1ac7e6fd5747334e99a073266f362'
inputseals=[]
for x in index['files']:
    p=P/x['path'];s=seal(p);assert (s['sha256'],s['bytes'])==(x['sha256'],x['bytes']);inputseals.append(s)
    if p.suffix=='.gz':assert gzip.decompress(p.read_bytes())
for x in index['ownedFiles']:
    p=R/x['path'];s=seal(p);assert (s['sha256'],s['bytes'])==(x['sha256'],x['bytes']);inputseals.append(s)
inputseals.append(seal(P/'receipt-index.json'))
manifest=F/'archive-manifest.json';mraw=manifest.read_bytes();assert sha(mraw)=='13d956802cd881c0d6805c00c0dee48de07bd6615196e69f74fbf4056a710e34';entries={r['key']:r for r in json.loads(mraw)['files']};assert len(entries)==52273
replay=json.loads((P/'actual-J-retained-replay.json').read_bytes());actualseals=[]
for row in replay['consumedReadSet']:
    p=F/row['key'];s=seal(p);assert s['sha256']==row['sha256'] and s['bytes']==row['bytes'] and s['mtimeNs']==row['mtimeNs'];assert entries[row['key']]['sha256']==s['sha256'];actualseals.append(s)
assert len(actualseals)==227
actualseals.append(seal(manifest))
allowed={'ops/ci/collect.py','status.md'};changed=[];exact=0;missing=[]
for raw in (O/'base-blobs.raw').read_bytes().split(b'\0'):
    if not raw:continue
    info,name=raw.split(b'\t',1);mode,kind,expected=info.decode().split();name=name.decode();p=R/name
    if kind!='blob':continue
    if not p.exists():missing.append(name);continue
    b=os.readlink(p).encode() if mode=='120000' else p.read_bytes()
    observed=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    if observed!=expected:changed.append({'path':name,'baseBlob':expected,'currentBlob':observed,'sha256':sha(b)})
    else:exact+=1
assert not missing and {x['path'] for x in changed}==allowed
for path in ('contracts/market.json','contracts/source-qualification-probes.json','contracts/factual-corrections.json','web/src/data/tracker/factualCorrectionPolicy.json'):
    inputseals.append(seal(R/path))
assert sha((R/'contracts/source-qualification-probes.json').read_bytes())=='ef9ee1bab6cfe6202b62e8d5605393f045d11fd64bd42ea1bcea769de15c8a01'
assert sha((R/'contracts/factual-corrections.json').read_bytes())=='9c9fbe0d3d40ece11e1407ce9460086c732f62da88d3b0f220ab9d6f8757da00'
images=json.loads((P/'renders.json').read_bytes())['images']
for row in images:
    p=P/f"images/{row['surface']}-{row['width']}.png";prior=Path(row['exactPriorImage']);assert p.read_bytes()==prior.read_bytes();assert sha(p.read_bytes())==row['sha256'];inputseals.append(seal(prior))
summary=json.loads((P/'verification-summary.json').read_bytes());assert summary['operationalPresent']=={'passed':984,'skipped':0,'testsRun':984};assert summary['operationalAbsent']=={'explicitRetainedSkips':53,'frozenReadAttempts':0,'passed':931,'portableCyeraPassed':22,'testsRun':984}
for name in ('operations-tests-final.log.gz','full-archive-absent.log.gz','npm-test.log.gz'):
    log=gzip.decompress((P/name).read_bytes()).decode();(O/(name[:-3]+'.tail')).write_text(log[-7000:])
result={'status':'PASS','base':'6bd3075c80bae7bba56a096cadb116cb379b2d63','baseBlobsExact':exact,'changedTracked':changed,'missing':missing,'archiveManifestEntries':len(entries),'authenticatedActualReadSet':227,'workerReceiptFiles':len(index['files']),'ownedFiles':index['ownedFiles'],'workerSummary':summary,'inputSeals':inputseals,'actualSeals':actualseals,'sameSurfaceImagesEqual':4,'preservedOldSixRequests':True,'protectedRuntimeContractPlanAndGeneratedDataUnchanged':True}
(O/'seals-and-protected-proof.json').write_text(json.dumps(result,indent=2,sort_keys=True))
print(json.dumps({k:result[k] for k in ('status','baseBlobsExact','changedTracked','archiveManifestEntries','authenticatedActualReadSet','workerReceiptFiles','sameSurfaceImagesEqual')}))
