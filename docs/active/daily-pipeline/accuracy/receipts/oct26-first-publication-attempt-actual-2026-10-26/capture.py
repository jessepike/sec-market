import base64,hashlib,io,json,os,subprocess,zipfile
from pathlib import Path
B=Path('/var/tmp/smp-oct26-publish-40266519925');C=B/'capture';C.mkdir(exist_ok=False)
OLD=Path('/var/tmp/smp-oct26-ordinary-40263678287/capture/extracted');OUT=C/'extracted'
H=lambda b:hashlib.sha256(b).hexdigest()
def api(route):return subprocess.check_output(['mac','gh','api','repos/jessepike/sec-market/'+route])
def save(name,raw):(C/name).write_bytes(raw);return raw
run=json.loads(save('publisher-run.json',api('actions/runs/40266519925')))
assert run['status']=='completed' and run['event']=='workflow_dispatch' and run['head_sha']=='3bb9e40c8f6324aa4f419fbe13022ec4dcaece55' and run['head_branch']=='main' and run['run_attempt']==1
save('publisher-jobs.json',api('actions/runs/40266519925/jobs'))
artifacts=json.loads(save('publisher-artifacts.json',api('actions/runs/40266519925/artifacts')))
matches=[a for a in artifacts['artifacts'] if a['name']=='daily-publication-receipt' and not a['expired']];assert len(matches)==1
artifact=matches[0];raw=save('publisher-artifact.zip',api('actions/artifacts/'+str(artifact['id'])+'/zip'));assert artifact['digest']=='sha256:'+H(raw)
with zipfile.ZipFile(io.BytesIO(raw)) as z:
 assert z.namelist()==['smp-publish-receipt.json'];receiptBytes=save('publisher-receipt.json',z.read(z.namelist()[0]))
receipt=json.loads(receiptBytes)
receiptAck=receipt.get('archive')
if receiptAck:
 ack=receiptAck;commit=ack['commit'];pinSource='terminalReceiptAcknowledgement'
else:
 assert run['conclusion']=='failure' and receipt.get('published') is False
 ref=json.loads(save('terminal-failure-archive-ref.json',api('git/ref/archive/market-evidence')));commit=ref['object']['sha'];ack=None;pinSource='exactArchiveRefAfterTerminalFailure'
meta=json.loads(save('archive-commit.json',api('git/commits/'+commit)));assert meta['sha']==commit
root=json.loads(save('archive-root-tree.json',api('git/trees/'+meta['tree']['sha'])))
manifestEntry=next(v for v in root['tree'] if v['path']=='archive-manifest.json')
manifestBlob=json.loads(save('archive-manifest-blob-api.json',api('git/blobs/'+manifestEntry['sha'])))
mb=base64.b64decode(manifestBlob['content']);assert hashlib.sha1(('blob '+str(len(mb))+'\0').encode()+mb).hexdigest()==manifestEntry['sha']
manifest=json.loads(mb)
if ack:assert H(mb)==ack['manifestSha256'] and len(manifest['files'])==ack['files']
observedArchive={'commit':commit,'manifestSha256':H(mb),'files':len(manifest['files']),'ref':'refs/archive/market-evidence'}
prior=json.loads((OLD/'archive-manifest.json').read_bytes());old={e['key']:e for e in prior['files']};new={e['key']:e for e in manifest['files']}
assert len(new)==len(manifest['files']) and not(set(old)-set(new))
changed=[k for k in old if old[k]!=new[k]];added=sorted(set(new)-set(old));assert all(k.startswith('state/heads/') for k in changed)
OUT.mkdir();identities=[]
for e in manifest['files']:
 key=e['key'];assert key.startswith('state/') and not Path(key).is_absolute() and '..' not in Path(key).parts
 target=OUT/key;target.parent.mkdir(parents=True,exist_ok=True)
 if key in old and old[key]==e:os.link(OLD/key,target)
 else:
  raw=api('contents/'+key+'?ref='+commit) if e['bytes']<900000 else api('contents/'+key+'?ref='+commit)
  response=json.loads(raw)
  if response.get('encoding')=='base64':body=base64.b64decode(response['content'])
  else:body=api('git/blobs/'+response['sha']);body=base64.b64decode(json.loads(body)['content'])
  assert len(body)==e['bytes'] and H(body)==e['sha256'],key;target.write_bytes(body)
 raw=target.read_bytes();assert len(raw)==e['bytes'] and H(raw)==e['sha256'],key
 st=target.stat();identities.append([key,e['bytes'],e['sha256'],st.st_mtime_ns,st.st_ino,st.st_dev])
(OUT/'archive-manifest.json').write_bytes(mb)
save('authenticated-file-identities.json',json.dumps(identities,separators=(',',':')).encode()+b'\n')
# Walk only immutable archive commit metadata to the exact ordinary collector acknowledgement.
sha=commit;chain=[];seen=set();baseline='6cf79ce0af6cfd63f8ed237465e5c6bf0800ff9c'
for i in range(40):
 if sha==baseline:break
 assert sha not in seen;seen.add(sha)
 raw=save('archive-ancestor-'+str(i)+'.json',api('git/commits/'+sha));entry=json.loads(raw);assert entry['sha']==sha and len(entry['parents'])==1
 chain.append({'commit':sha,'parent':entry['parents'][0]['sha'],'tree':entry['tree']['sha'],'rawSha256':H(raw)})
 sha=entry['parents'][0]['sha']
assert sha==baseline
ref=json.loads(save('archive-ref-at-audit.json',api('git/ref/archive/market-evidence')))
proof={'actualPublisherRunId':'40266519925','publisherConclusion':run['conclusion'],'safeReceipt':receipt,'publisherArtifactId':artifact['id'],'publisherArtifactDigest':artifact['digest'],'publisherArtifactZipSha256':H((C/'publisher-artifact.zip').read_bytes()),'publisherReceiptSha256':H(receiptBytes),'acknowledgedArchive':ack,'observedArchive':observedArchive,'archivePinSource':pinSource,'manifestGitBlobSha1':manifestEntry['sha'],'manifestBytes':len(mb),'manifestEntries':len(new),'allManifestEntriesVerified':True,'baselineArchiveCommit':baseline,'baselineManifestSha256':H((OLD/'archive-manifest.json').read_bytes()),'baselineEntries':len(old),'priorImmutableEntriesExact':True,'changedMutableHeads':changed,'addedEntries':added,'archiveAncestry':chain,'baselineIsAncestor':True,'archiveRefAtRead':ref['object']['sha'],'ackIsCurrentAtRead':ref['object']['sha']==commit,'materialization':'Unchanged authenticated files hardlinked read-only from exact ordinary collector archive; changed/new files fetched from exact Git commit and hash checked; no source/archive-state writes.'}
save('authenticated-publisher-archive.json',json.dumps(proof,indent=2).encode()+b'\n')
print(json.dumps({k:proof[k] for k in ('actualPublisherRunId','publisherConclusion','acknowledgedArchive','manifestEntries','allManifestEntriesVerified','baselineIsAncestor','ackIsCurrentAtRead')},indent=2))
