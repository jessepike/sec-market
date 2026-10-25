"""Prepare a hash-authenticated hardlink delta from frozen d660, only after actual ack inputs exist."""
import argparse, hashlib, json, os, shutil, stat
from pathlib import Path, PurePosixPath
def digest(raw):return hashlib.sha256(raw).hexdigest()
def need(ok,message):
 if not ok:raise ValueError(message)
def records(raw):
 value=json.loads(raw);need(value.get('schemaVersion')==1 and type(value.get('files'))is list,'MANIFEST_SHAPE_INVALID')
 rows={}
 for r in value['files']:
  key=r['key'];p=PurePosixPath(key)
  need(type(key)is str and p.parts and p.parts[0]=='state' and '..'not in p.parts and not p.is_absolute() and str(p)==key,'MANIFEST_PATH_INVALID')
  need(key not in rows and type(r['bytes'])is int and r['bytes']>=0 and type(r['sha256'])is str and len(r['sha256'])==64,'MANIFEST_ROW_INVALID')
  rows[key]=r
 return rows
def identity(path):
 st=path.stat();need(stat.S_ISREG(st.st_mode)and not path.is_symlink(),'NONREGULAR_BASELINE_FILE')
 return {'device':st.st_dev,'inode':st.st_ino,'bytes':st.st_size,'mtimeNs':st.st_mtime_ns}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['baseline','baseline-sha','baseline-proof','baseline-proof-sha','manifest','manifest-sha','manifest-blob','destination','needed','reuse-proof']:p.add_argument('--'+name,required=True)
 a=p.parse_args();baseline=Path(a.baseline).resolve();dest=Path(a.destination).resolve()
 prior=(baseline/'archive-manifest.json').read_bytes();raw=Path(a.manifest).read_bytes();proofraw=Path(a.baseline_proof).read_bytes()
 need(digest(prior)==a.baseline_sha=='40873bfd2dca9836b58ac325a3afb32919fb463b2082752cb72fc785a2d7239d','FROZEN_BASELINE_MANIFEST_DIFFERS')
 need(digest(raw)==a.manifest_sha,'ACK_MANIFEST_HASH_DIFFERS')
 need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==a.manifest_blob,'ACK_MANIFEST_GIT_BLOB_DIFFERS')
 need(digest(proofraw)==a.baseline_proof_sha=='f6d39334462c8f2dfa8ebf49439451969e5c3ed8b863b504b666821ca81f5033','BASELINE_FULL_AUDIT_DIFFERS')
 proof=json.loads(proofraw);old,new=records(prior),records(raw)
 need(proof['acknowledgedArchive']['commit']=='d6606a4f5dd1e1afc5f16dea6d91bc422347f8aa' and proof['manifest']['sha256']==a.baseline_sha and proof['allEntriesVerified']==len(old)==48045,'BASELINE_FULL_AUTHENTICATION_DIFFERS')
 need(not dest.exists()and not dest.is_relative_to(baseline)and not baseline.is_relative_to(dest),'UNSAFE_DESTINATION')
 need(str(dest).startswith('/var/tmp/'),'DESTINATION_MUST_BE_VM_SCRATCH')
 need(all(k in new for k in old),'BASELINE_ENTRY_REMOVED')
 need(all(not path.is_symlink()for path in baseline.rglob('*')),'BASELINE_SYMLINK')
 reused={};needed={}
 for key,row in new.items():
  if old.get(key)==row:
   x=identity(baseline/key);need(x['bytes']==row['bytes'],'BASELINE_SIZE_DIFFERS');reused[key]=x
  else:needed[key]=row
 shutil.copytree(baseline,dest,copy_function=os.link)
 (dest/'archive-manifest.json').unlink();(dest/'archive-manifest.json').write_bytes(raw)
 for key,row in needed.items():
  target=dest/key;target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():target.unlink()
 for key,x in reused.items():need(identity(dest/key)==identity(baseline/key)==x,'SHARED_BASELINE_IDENTITY_CHANGED')
 output={'schemaVersion':1,'baselineRoot':str(baseline),'destination':str(dest),'baselineManifestSha256':a.baseline_sha,'acknowledgedManifestSha256':a.manifest_sha,'manifestGitBlobSha':a.manifest_blob,'baselineFullAuditSha256':a.baseline_proof_sha,'baselineEntries':len(old),'acknowledgedEntries':len(new),'reusedEntries':reused,'neededEntries':needed,'completeArchiveAuthenticated':False,'method':'Unchanged prior-authenticated bytes share original inodes; delta bytes still must be materialized/authenticated before audit.'}
 Path(a.needed).write_text(json.dumps(list(needed.values()),indent=2)+'\n');Path(a.reuse_proof).write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'baselineEntries':len(old),'acknowledgedEntries':len(new),'reusedEntries':len(reused),'neededEntries':len(needed),'completeArchiveAuthenticated':False}))
if __name__=='__main__':main()
