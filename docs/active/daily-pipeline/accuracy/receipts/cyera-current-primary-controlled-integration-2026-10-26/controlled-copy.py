from pathlib import Path
import gzip,hashlib,json,os,shutil,subprocess
SRC=Path('/mnt/mac/Users/jessepike/.codex/worktrees/cyera-current-primary/sec-market')
TARGET=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022')
HAND=Path('/var/tmp/smp-cyera-implementation-independent-20261025/handback')
OUT=Path('/var/tmp/smp-cyera-controlled-integration-20261026');OUT.mkdir(exist_ok=True)
BASE='3bb9e40c8f6324aa4f419fbe13022ec4dcaece55'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def git(*args):return subprocess.check_output(['git','-C',str(TARGET),*args])
def payload(path):return os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
def require(ok,reason):
 if not ok:raise AssertionError(reason)
def safe(rel):
 p=Path(rel);require(not p.is_absolute() and '..' not in p.parts,'UNSAFE_COPY_PATH');return rel
items={}
def add(root,rel,pin=None):
 safe(rel);p=root/rel;require(p.is_file() and not p.is_symlink(),'SOURCE_FILE_REQUIRED '+rel);raw=p.read_bytes()
 if pin:require(sha(raw)==pin['sha256'] and len(raw)==pin['bytes'],'SOURCE_PIN_DIFFERS '+rel)
 if rel in items:require(items[rel]['raw']==raw,'COPY_SOURCE_CONFLICT '+rel)
 items[rel]={'source':str(p),'raw':raw,'sha256':sha(raw),'bytes':len(raw)}
idxrel='docs/active/daily-pipeline/accuracy/receipts/cyera-current-primary-build-2026-10-25/receipt-index.json'
raw=(SRC/idxrel).read_bytes();require(sha(raw)=='03fd772e5a53865d5785067a2447a66849c1ac7e6fd5747334e99a073266f362','BUILD_INDEX_DIFFERS');idx=json.loads(raw)
for row in idx['ownedFiles']:
 if row['path']!='status.md':add(SRC,row['path'],row)
add(SRC,idxrel)
folder=str(Path(idxrel).parent)
for row in idx['files']:add(SRC,folder+'/'+row['path'],row)
sp='docs/active/daily-pipeline/accuracy/receipts/cyera-one-primary-build-spec-independent-review-2026-10-25/index.json'
raw=(SRC/sp).read_bytes();require(sha(raw)=='51c6b099c5017cff3b0bee7bc04fc20a00fe43b00f7a643eeb5725d4ba39ea73','SPEC_REVIEW_INDEX_DIFFERS');add(SRC,sp)
for name,pin in json.loads(raw)['files'].items():add(SRC,str(Path(sp).parent/name),pin)
ir='docs/active/daily-pipeline/accuracy/receipts/cyera-current-primary-build-independent-review-2026-10-25/receipt-index.json'
raw=(HAND/ir).read_bytes();require(sha(raw)=='094fed5761f587e05562c2b226e1d6ec445d60a2a918f54423cb2c912fa02d79','INDEPENDENT_INDEX_DIFFERS');review=json.loads(raw)
require(review['verdict']=='PASS' and review['writesStopped'] is True,'INDEPENDENT_REVIEW_NOT_SEALED')
add(HAND,ir)
for row in review['files']+review['reports']:add(HAND,row['path'],row)
require(git('rev-parse','HEAD').decode().strip()==BASE,'TARGET_HEAD_MOVED')
require(not git('status','--porcelain').strip(),'TARGET_NOT_CLEAN')
require((TARGET/'ops/ci/collect.py').read_bytes()==git('show','6bd3075c80bae7bba56a096cadb116cb379b2d63:ops/ci/collect.py'),'TARGET_COLLECT_NOT_EXACT_BASE')
tracked={}
for entry in git('ls-tree','-rz','HEAD').split(b'\0'):
 if not entry:continue
 meta,path=entry.split(b'\t');mode,kind,blob=meta.decode().split();rel=path.decode();raw=payload(TARGET/rel)
 require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,'TARGET_BASE_BLOB_DIFFERS '+rel)
 tracked[rel]={'mode':mode,'gitBlob':blob,'sha256':sha(raw),'bytes':len(raw)}
for rel,row in items.items():
 require(rel=='ops/ci/collect.py' or rel not in tracked,'UNEXPECTED_EXISTING_TRACKED_COPY '+rel)
 if (TARGET/rel).exists() and rel!='ops/ci/collect.py':require((TARGET/rel).read_bytes()==row['raw'],'DESTINATION_EXISTS_DIFFERENT '+rel)
# No mutation occurs until every source pin and every target base blob has passed.
for rel,row in items.items():
 p=TARGET/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(row['raw'])
require(git('rev-parse','HEAD').decode().strip()==BASE,'TARGET_HEAD_MOVED_DURING_COPY')
for rel,before in tracked.items():
 if rel!='ops/ci/collect.py':require(sha(payload(TARGET/rel))==before['sha256'],'PROTECTED_TARGET_CHANGED '+rel)
for rel,row in items.items():require(sha((TARGET/rel).read_bytes())==row['sha256'],'COPIED_TARGET_PIN_DIFFERS '+rel)
result={'status':'PASS_CONTROLLED_COPY_ONLY','base':BASE,'sourceBuildIndexSha256':sha((SRC/idxrel).read_bytes()),'independentIndexSha256':sha((HAND/ir).read_bytes()),
 'trackedBaseCount':len(tracked),'protectedUnchanged':len(tracked)-1,'allowedExistingDelta':['ops/ci/collect.py'],
 'excluded':['status.md from source','contracts','requests','correction stamp','generated data','workflows'],
 'files':[{'path':rel,'source':row['source'],'sha256':row['sha256'],'bytes':row['bytes']} for rel,row in sorted(items.items())],
 'sourceRequests':0,'modelCalls':0,'liveStateWrites':0,'dispatches':0,'commits':0,'pushes':0}
(OUT/'target-base-before.json.gz').write_bytes(gzip.compress(canonical(tracked),mtime=0))
(OUT/'copy-index.json').write_bytes(canonical(result));shutil.copyfile('/mnt/mac/private/tmp/cyera-controlled-copy.py',OUT/'controlled-copy.py')
print(json.dumps({'copied':len(items),'trackedBaseCount':len(tracked),'indexSha256':sha((OUT/'copy-index.json').read_bytes())}))
