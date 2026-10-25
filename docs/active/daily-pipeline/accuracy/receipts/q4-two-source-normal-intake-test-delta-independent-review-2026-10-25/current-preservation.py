from pathlib import Path
import hashlib,json
O=Path('/var/tmp/smp-q4-normal-intake-test-delta-independent-20261025');A=Path('/var/tmp/smp-listing-pagination-actual-40193925490-20261025/extracted');B=Path('/var/tmp/smp-next-seven-actual-40190857026-20261025/extracted');C=Path('/var/tmp/smp-narrow-pagination-independent-20261025/authenticated-archive-file-identities.json')
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def need(v,m):
 if not v:raise AssertionError(m)
def ident(p):
 s=p.stat();return {'bytes':s.st_size,'mtimeNs':s.st_mtime_ns,'inode':s.st_ino,'device':s.st_dev}
cache=json.loads(C.read_bytes());need(sha(C.read_bytes())=='ca73c500d9e7b66135945ab56034563c01a788caa66efbaf2f9962bdf16fd720','CACHE');oldraw=(B/'archive-manifest.json').read_bytes();newraw=(A/'archive-manifest.json').read_bytes();need(sha(oldraw)==cache['manifestSha256'] and sha(newraw)=='148842177a7e7d9a5fd5c2ea4574576264a957b41958ee4cdf5effa80ea029c2' and len(newraw)==10012399,'MANIFEST')
old={e['key']:e for e in json.loads(oldraw)['files']};new={e['key']:e for e in json.loads(newraw)['files']};need(len(new)==48420 and set(old)<=set(new),'INVENTORY');reused=[];verified=[];stats={}
for k,e in new.items():
 p=A/k;need(not p.is_symlink(),'SYMLINK');stats[k]=ident(p)
 if old.get(k)==e and ident(B/k)==cache['files'][k]==stats[k]:reused.append(k)
 else:
  b=p.read_bytes();need(sha(b)==e['sha256'] and len(b)==e['bytes'],'DELTA_BYTES');verified.append(k)
need(len(reused)==48243 and len(verified)==177,'EXPECTED_DELTA');need({str(p.relative_to(A)) for p in (A/'state').rglob('*') if p.is_file()}==set(new),'EXTRA_OR_MISSING')
exclude={'state/heads/budget-2026-10-25.json','state/heads/cloud-lease.json'};keys={k for k in new if k.startswith('state/heads/') and k.endswith('.json')}-exclude;need(keys=={k for k in old if k.startswith('state/heads/') and k.endswith('.json')}-exclude and len(keys)==8605,'ALL_HEADS_SCOPE');heads={}
for k in sorted(keys):
 a=(A/k).read_bytes();b=(B/k).read_bytes();need(a==b and sha(a)==new[k]['sha256']==old[k]['sha256'],'NORMAL_HEAD_BYTES');heads[k]=sha(a)
need(digest(heads)=='490b7e470a9cdbd9b767664741644094bfdb1c5edd5a1e9d8ea8633b129032cd','CANONICAL_HEAD_HASH')
budget=json.loads((A/'state/heads/budget-2026-10-25.json').read_bytes());need(budget=={'fetches':1101,'calls':80,'documents':38},'CURRENT_BUDGET');snapshot=json.loads((A/'state/heads/dailySnapshot.json').read_bytes());need(len(snapshot['factProvenance'])==4 and len(snapshot['reviewQueue'])==38,'FACTS_HOLDS')
for k,v in stats.items():need(ident(A/k)==v,'AFTER_IDENTITY')
result={'schemaVersion':1,'verdict':'PASS','acknowledgedArchive':'9e4a9806fdcc1b7cd6f91314b8b4ff4bb4ef2174','archiveRoot':str(A),'manifestSha256':sha(newraw),'manifestBytes':len(newraw),'entries':48420,'cachedBaseline':'9deb0c9ce9fe34999da0cf13bb023dfdfecc15c8','cachedIdentityReceiptSha256':sha(C.read_bytes()),'previouslyAuthenticatedIdenticalHardlinks':len(reused),'deltaEntriesHashVerified':len(verified),'canonicalHeadScope':{'directory':'state/heads/*.json','except':sorted(exclude),'count':len(keys),'sha256':digest(heads),'allByteExactAgainst9deb':True},'changedOldEntryKeys':[k for k in old if old[k]!=new[k]],'newEntryCount':len(new)-len(old),'currentActualBudgetUnchanged':budget,'factReferences':4,'heldRows':38,'privateSourceExpiryUnchanged':snapshot['coverage']['validUntil'],'all48420FileIdentitiesUnchangedAfter':True,'sourceRequests':0,'modelRequests':0,'archiveWrites':0,'budgetWrites':0};(O/'current-preservation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
