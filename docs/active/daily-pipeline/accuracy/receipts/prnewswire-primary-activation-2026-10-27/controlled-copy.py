import hashlib,json,os,sys
from pathlib import Path
ROOT=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022')
OUTSIDE=Path('/var/tmp/smp-prn-primary-activation-20261027')
TARGET=ROOT/'docs/active/daily-pipeline/accuracy/receipts/prnewswire-primary-activation-2026-10-27'
BASE='6e0da6379b15e0759a3504ad46f1489350624dc9'
SELECTED='01e468f5d73ddb28edbde014a0b725f7d202340a692964d01f6fd174faec7fb1'
PRIOR='25bf0ff72555188e7a8446b9499f3b8ba56c9327e397f8b70a5ce9deb82d350f'
AUDIT='/var/tmp/smp-cyera-probe-40529776219/actual-probe-audit.json'
AUDIT_SHA='cfa8329537930ff76884bc6cc707a7c17c1d9577d2dea35bcb6608ed6dfd1c18'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def pin(raw):return {'sha256':sha(raw),'bytes':len(raw)}
def save(name,data):(TARGET/name).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
assert not TARGET.exists()
indexraw=(OUTSIDE/'receipt-index.json').read_bytes()
assert sha(indexraw)=='8bcd76d89dbae01853ecabf30012ce511bdb74c644b7662f369e4d4bc65980ba'
assert sha((OUTSIDE/'copy-index.json').read_bytes())=='8557cc5bd0626b47bed29303281e2558813408e2b8604fae247996d1115fd3b7'
index=json.loads(indexraw);declared={row['path']:row for row in index['files']}
assert len(declared)==3224
for name,row in declared.items():assert pin((OUTSIDE/name).read_bytes())=={key:row[key] for key in ('sha256','bytes')},name
auditraw=Path(AUDIT).read_bytes();assert sha(auditraw)==AUDIT_SHA
entries=[]
for token in sys.stdin.buffer.read().split(b'\0'):
 if not token:continue
 metadata,name=token.split(b'\t',1);mode,kind,blob=metadata.decode().split();assert kind=='blob'
 relative=name.decode();path=ROOT/relative
 raw=os.readlink(path).encode() if mode=='120000' else path.read_bytes()
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,relative
 entries.append({'path':relative,'gitMode':mode,'gitBlob':blob,**pin(raw)})
assert len(entries)>3200
source_before=json.loads((OUTSIDE/'source-before.json').read_bytes());codechecked=0
for name,row in source_before['files'].items():
 if not name.startswith('docs/') and name not in ('status.md','BACKLOG.md'):
  assert pin((ROOT/name).read_bytes())==row,name
  codechecked+=1
active=ROOT/'contracts/source-qualification-probes.json';before=active.read_bytes();assert sha(before)==PRIOR
selected=(OUTSIDE/'selected-prn-plan.json').read_bytes();assert sha(selected)==SELECTED
TARGET.mkdir(parents=True);copied=[]
for name,row in declared.items():
 if '/' in name:continue
 raw=(OUTSIDE/name).read_bytes();(TARGET/name).write_bytes(raw)
 copied.append({'outsideRelativePath':name,'targetRelativePath':str((TARGET/name).relative_to(ROOT)),**pin(raw)})
assert len(copied)==12
(TARGET/'outside-sealed-receipt-index.json').write_bytes(indexraw)
(TARGET/'actual-cyera-prerequisite-audit.json').write_bytes(auditraw)
(TARGET/'controlled-copy.py').write_bytes(Path(__file__).read_bytes())
active.write_bytes(selected)
for row in entries:
 path=ROOT/row['path'];raw=os.readlink(path).encode() if row['gitMode']=='120000' else path.read_bytes()
 expected=SELECTED if row['path']=='contracts/source-qualification-probes.json' else row['sha256']
 assert sha(raw)==expected,row['path']
save('actual-base-and-prerequisites.json',{
 'actualBaseCommit':BASE,'outsideAssemblyCommit':source_before['commit'],
 'currentBaseDifference':'documentation only; all non-documentation code/contract/configuration pins authenticate',
 'liveSelectionAuthority':'root accepted exact outside PRN unit and explicitly authorized this controlled copy',
 'cyeraPrerequisite':{'source':'root accepted auditor-authenticated actual result; bounded safe audit copied byte-exact',
  'githubRunId':'40529776219','appRevision':'1b2176087ca148c066f6d21efb4d7fc80daa7504','conclusion':'success',
  'acknowledgedArchiveCommit':'066d52b826cb3408429be4cff3ff604f14c7cb4a',
  'manifestSha256':'e244ddc834b54198b45cfde18a0059dbc20f9b3ad79e2add0a990a4c3f9fa8ae','authenticatedEntries':62632,
  'logicalRequests':1,'httpStatus':200,'bodyBytes':266519,'readableCharacters':8040,'acceptedCalendarDay':'2026-10-16',
  'settledSourceLedger':{'fetches':450,'calls':67,'documents':31},'writerLeaseReleasedAt':'2026-10-27T15:26:39.561695Z',
  'reportedUnchanged':'other normal heads, gate count one, publication reservation, public sequence six, 48 holds and eight admissions/clocks',
  'independentFullReplay':{'status':'PASS','consumedFrozenEntries':238,'receipt':'actual-cyera-prerequisite-audit.json',**pin(auditraw)},
  'sourceQualification':False},
 'prnPreflightArchive':{'commit':'ac082a358d1ce897854d9a08a964bdfbd335a06e',
  'manifestSha256':'3aca334fd331a89142cae4efeaa06eab5922c6b38eb8ac53f88aae1ac2861503','entries':62602,
  'status':'original sealed outside preflight retained unchanged; not rerun against latest Cyera archive'},
 'selectedPlan':pin(selected),'replacedCyeraPlan':pin(before),
 'postPRNRestoration':{'file':'post-capture-disabled-J-plan.json',**pin((TARGET/'post-capture-disabled-J-plan.json').read_bytes())},
 'sourcePolicyChanged':False,'sourceRequests':0,'modelCalls':0,'newLiveReservations':0,'gateAttempts':0,
 'sourceQualified':False,'coverageCredit':False,'committed':False,'pushed':False,'dispatched':False})
save('controlled-copy-index.json',{'actualBaseCommit':BASE,'copiedPayloads':copied,
 'outsideReceiptIndexSha256':sha(indexraw),'outsideReceiptIndexMeaning':'binds full original VM assembly; source/ payloads stay outside and are not copied into this receipt directory',
 'activePlanChange':{'target':'contracts/source-qualification-probes.json','before':pin(before),'after':pin(selected)},
 'authenticatedWholeTrackedTreeBeforeFiles':len(entries),'unchangedOtherTrackedFiles':len(entries)-1,
 'unchangedNonDocumentationAssemblyPins':codechecked,'onlyChangedExistingTrackedFile':'contracts/source-qualification-probes.json'})
save('tracked-tree-before.json',{'baseCommit':BASE,'files':entries})
(TARGET/'controlled-copy.md').write_text('\n\n'.join([
 '# Controlled PRN activation copy',
 'Root accepted the sealed two-target unit and authorized this copy after the actual Cyera run reached its acknowledged archive. The actual finish base is 6e0da6379b15e0759a3504ad46f1489350624dc9, a documentation-only descendant of the original 1b217608 assembly. Every existing tracked file was authenticated against that exact Git tree before the copy. All code, contracts and configuration still match the prepared assembly.',
 'Only the selected plan changed, from exact Cyera 25bf0ff7 to accepted PRN 01e468f5. All other existing tracked files remain exact. Twelve sealed outside receipts and the unchanged outside receipt index are retained here. The full source assembly remains in the VM; the outside receipt index names those original external source paths and does not claim those files were copied here. The copied verifier retains its original outside-assembly meaning.',
 'The original PRN preflight remains the successful ac082 archive check. The latest Cyera acknowledgement, settled 450/67/31 ledger and released lease are recorded separately in actual-base-and-prerequisites.json. The auditor then completed its full replay; its exact safe audit is retained as actual-cyera-prerequisite-audit.json. This copy did not rerun PRN preflight against the newer archive.',
 'The exact ef9 disabled J plan is preserved as the post-PRN restoration target. The saved Cyera plan is provenance. Root owns commit, push, main promotion and the one actual PRN dispatch; this copy performed none of them and earned no source or qualification credit. No status or backlog file was written.'
 ])+'\n')
files=[]
for path in sorted(TARGET.rglob('*')):
 if path.is_file():files.append({'path':str(path.relative_to(TARGET)),**pin(path.read_bytes())})
save('integration-receipt-index.json',{'schemaVersion':1,'files':files,'fileCount':len(files),'sourceRequests':0,'coverageCredit':False})
print(json.dumps({'status':'PASS','base':BASE,'trackedBefore':len(entries),'unchangedOtherTracked':len(entries)-1,
 'unchangedNonDocumentationPins':codechecked,'copiedOutsidePayloads':len(copied),'selectedPlan':sha(selected),
 'integrationReceiptIndexSha256':sha((TARGET/'integration-receipt-index.json').read_bytes())}))
