from pathlib import Path
import json,hashlib,gzip
R=Path('/mnt/mac/Users/jessepike/.codex/worktrees/prn-current-primary/sec-market');B=Path('/var/tmp/smp-prn-current-primary-build-20261025');O=Path('/var/tmp/smp-prn-primary-implementation-independent-20261025')
def sha(b):return hashlib.sha256(b).hexdigest()
def seal(p):
 st=p.stat();b=p.read_bytes();return {'path':str(p),'sha256':sha(b),'bytes':len(b),'mtimeNs':st.st_mtime_ns,'inode':st.st_ino}
indexraw=(B/'copy-index.json').read_bytes();assert sha(indexraw)=='3bd45eff65d15bfd50b2e08e102bc0f452408fa7ed1e49f99887843ca5ee8b3f';index=json.loads(indexraw);seals=[seal(B/'copy-index.json')]
assert len(index['files'])==34
for row in index['files']:
 p=R/row['path'];s=seal(p);assert s['sha256']==row['sha256'] and s['bytes']==row['bytes'];seals.append(s)
 if p.suffix=='.gz':assert gzip.decompress(p.read_bytes())
raw=(B/'handback.json').read_bytes();assert sha(raw)=='6f82ca084a40a9a7813e3df5363110280c463ae12f3046ac629200b031fba4e4';j=json.loads(raw);seals.append(seal(B/'handback.json'))
assert j['operationsPresent']['testsRun']==j['operationsPresent']['passed']==992
assert j['operationsAbsent']['status']=='PASS' and j['operationsAbsent']['testsRun']==992 and j['operationsAbsent']['passed']==932 and not j['operationsAbsent']['frozenReadAttempts'] and not j['operationsAbsent']['portablePRNCoreSkipped']
P=R/'docs/active/daily-pipeline/accuracy/receipts/prnewswire-primary-capture-implementation-2026-10-25'
for name,marker in [('operations-present-sealed.log.gz','Ran 992 tests'),('operations-absent-sealed-v2.log.gz','OK (skipped=60)'),('npm-test-sealed.log.gz','80')]:
 log=gzip.decompress((P/name).read_bytes()).decode();assert marker in log
 (O/(name[:-3]+'.tail')).write_text(log[-9000:])
rawabs=json.loads((P/'operations-absent-sealed-v2.json').read_bytes());assert rawabs['status']=='PASS' and rawabs['testsRun']==992 and not rawabs['frozenReadAttempts']
images=[]
prior=Path('/mnt/mac/Users/jessepike/Documents/Codex/2026-10-22/security-market-pulse/renewal-20261024')
for name,row in j['render']['files'].items():
 p=B/name;s=seal(p);assert s['sha256']==row['sha256'] and s['bytes']==row['bytes'];seals.append(s)
 if name.startswith('local-'):assert p.read_bytes()==(B/name.replace('local-','baseline-')).read_bytes()
 if name.startswith(('local-','production-')):
  old=prior/('prn-dated-window-'+name);assert old.read_bytes()==p.read_bytes();seals.append(seal(old));images.append({'image':name,'bytesExactCorrespondingPrior':True,'sha256':s['sha256']})
assert len(images)==4
out={'status':'PASS','workerCopyIndexSha256':sha(indexraw),'workerReceiptSha256':sha(raw),'ownedFilesVerified':34,'opsPresent':992,'opsAbsent':{'total':992,'passed':932,'explicitSkips':60,'frozenReadAttempts':[],'portablePRNCoreSkipped':[]},'application':j['npmTest'],'images':images,'closedAt':j['closedAt'],'inputSeals':seals,'workerHistory':'Superseded pacing/adapter-negative runs and absence-driver failures are retained in the indexed worker evidence. Final exact-code log attribution is operations-present-sealed and operations-absent-sealed-v2.'}
(O/'worker-evidence-authentication.json').write_text(json.dumps(out,indent=2,sort_keys=True));print({k:v for k,v in out.items() if k!='inputSeals'})
