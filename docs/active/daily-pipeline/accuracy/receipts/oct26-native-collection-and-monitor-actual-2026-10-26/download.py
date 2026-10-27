"""Run only after root provides an actual ordinary-J run ID and exact main SHA."""
import argparse,hashlib,io,json,subprocess,tarfile,zipfile
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--run-id',required=True)
p.add_argument('--revision',required=True)
p.add_argument('--output',required=True)
a=p.parse_args()
assert a.run_id.isdecimal() and len(a.revision)==40 and all(c in '0123456789abcdef' for c in a.revision)
base=Path(a.output);base.mkdir(parents=True,exist_ok=False)
H=lambda b:hashlib.sha256(b).hexdigest()
def api(route):return subprocess.check_output(['mac','gh','api','repos/jessepike/sec-market/'+route])
def save(name,b): (base/name).write_bytes(b);return b
run=json.loads(save('run.json',api('actions/runs/'+a.run_id)))
assert run['status']=='completed' and run['head_sha']==a.revision and run['head_branch']=='main'
assert run['event']=='schedule' and run['run_attempt']==1
listed=json.loads(save('artifacts.json',api('actions/runs/'+a.run_id+'/artifacts')))
matches=[x for x in listed['artifacts'] if x['name']=='subscription-collection-receipt']
assert len(matches)==1 and not matches[0]['expired']
artifact=matches[0]
zraw=save('collection-artifact.zip',api('actions/artifacts/'+str(artifact['id'])+'/zip'))
assert artifact.get('digest')=='sha256:'+H(zraw),'Actual GitHub artifact digest required'
with zipfile.ZipFile(io.BytesIO(zraw)) as z:
 assert z.namelist()==['smp-collection-receipt.json']
 raw=save('collection-receipt.json',z.read('smp-collection-receipt.json'))
r=json.loads(raw)
assert str(r['githubRunId'])==a.run_id and r['githubRef']=='refs/heads/main' and r['appRevision']==a.revision
assert r['githubEventName']=='schedule'
# Preserve genuine failure/unknown fields. Do not infer success from a receipt class.
ack=r.get('archive')
if not ack:
 save('terminal-no-archive.json',json.dumps({'runConclusion':run['conclusion'],'receipt':r},indent=2).encode()+b'\n')
 raise SystemExit('No acknowledged archive; actual failure retained without retry')
commit=ack['commit'];meta=json.loads(save('archive-git-commit.json',api('git/commits/'+commit)))
assert meta['sha']==commit
tree=json.loads(save('archive-root-tree.json',api('git/trees/'+meta['tree']['sha'])))
me=[x for x in tree['tree'] if x['path']=='archive-manifest.json'];assert len(me)==1
tar=save('archive.tar.gz',api('tarball/'+commit));out=base/'extracted';out.mkdir()
seen=set()
with tarfile.open(fileobj=io.BytesIO(tar),mode='r:gz') as t:
 for m in t:
  parts=Path(m.name).parts;assert parts and '..' not in parts and not Path(m.name).is_absolute()
  if len(parts)==1:continue
  rel=Path(*parts[1:]);assert str(rel) not in seen;seen.add(str(rel))
  assert not m.issym() and not m.islnk() and (m.isfile() or m.isdir())
  dest=out/rel
  if m.isdir():dest.mkdir(parents=True,exist_ok=True)
  else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(t.extractfile(m).read())
mb=(out/'archive-manifest.json').read_bytes();assert H(mb)==ack['manifestSha256']
assert hashlib.sha1(('blob '+str(len(mb))+'\0').encode()+mb).hexdigest()==me[0]['sha']
manifest=json.loads(mb);entries=manifest['files'];assert len(entries)==ack['files']
keys=set();identities=[]
for e in entries:
 key=e['key'];assert isinstance(key,str) and key.startswith('state/') and '..' not in Path(key).parts and key not in keys;keys.add(key)
 q=out/key;b=q.read_bytes();assert len(b)==e['bytes'] and H(b)==e['sha256'],key
 st=q.stat();identities.append({**e,'mtimeNs':st.st_mtime_ns,'inode':st.st_ino,'device':st.st_dev})
assert {str(x.relative_to(out)) for x in (out/'state').rglob('*') if x.is_file()}==keys, 'Unmanifested state files'
save('authenticated-file-identities.json',json.dumps(identities,separators=(',',':')).encode()+b'\n')
proof={'runId':a.run_id,'appRevision':a.revision,'runConclusion':run['conclusion'],'artifactId':artifact['id'],'githubArtifactDigest':artifact['digest'],'artifactZipSha256':H(zraw),'rawReceiptSha256':H(raw),'archiveAck':ack,'archiveCommit':commit,'manifestSha256':H(mb),'manifestBytes':len(mb),'manifestGitBlobSha1':me[0]['sha'],'manifestEntries':len(entries),'allManifestEntriesVerified':True,'archiveTarSha256':H(tar),'extractedRoot':str(out),'actualOrdinaryJIntakeReconciliation':'pending separate read-only replay','qualificationCreditFromDownload':False}
save('download-proof.json',json.dumps(proof,indent=2).encode()+b'\n')
print(json.dumps(proof,indent=2))
