from pathlib import Path
import os,json,hashlib,gzip
R=Path('/mnt/mac/Users/jessepike/.codex/worktrees/prn-current-primary/sec-market');O=Path('/var/tmp/smp-prn-primary-implementation-independent-20261025')
def sha(b):return hashlib.sha256(b).hexdigest()
def seal(p):
    st=p.stat();b=p.read_bytes();return {'path':str(p),'sha256':sha(b),'bytes':len(b),'mtimeNs':st.st_mtime_ns,'inode':st.st_ino}
changed=[];missing=[];exact=0
for raw in (O/'base-blobs.raw').read_bytes().split(b'\0'):
    if not raw:continue
    info,name=raw.split(b'\t',1);mode,kind,expected=info.decode().split();name=name.decode();p=R/name
    if kind!='blob':continue
    if not p.exists():missing.append(name);continue
    b=os.readlink(p).encode() if mode=='120000' else p.read_bytes();observed=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    if observed==expected:exact+=1
    else:changed.append({'path':name,'baseBlob':expected,'newBlob':observed,'sha256':sha(b)})
assert not missing and {x['path'] for x in changed}=={'ops/ci/collect.py','status.md'}
paths=['web/scripts/pipeline/prnewswire_primary_capture.py','ops/ci/collect.py','ops/ci/test_prnewswire_primary_capture.py','ops/ci/fixtures/prnewswire-primary-retained-readset.json.gz','docs/active/daily-pipeline/accuracy/prnewswire-primary-capture-build-spec-v0.2-2026-10-25.md','docs/active/daily-pipeline/accuracy/prnewswire-primary-capture-original-proposal-2026-10-25.md','docs/active/daily-pipeline/accuracy/prnewswire-primary-capture-plan-2026-10-25.json','docs/active/daily-pipeline/accuracy/prnewswire-retained-window-descriptor-2026-10-25.json','web/scripts/pipeline/prnewswire_retained_window.py','web/scripts/pipeline/prnewswire_press_list.py','web/scripts/pipeline/q4_qualification_origin.py','web/scripts/pipeline/q4_primary_qualification.py','web/scripts/pipeline/fetcher.py','web/scripts/pipeline/onboarding.py','ops/cloud/run.py','contracts/market.json','contracts/source-qualification-probes.json','contracts/factual-corrections.json','web/src/data/tracker/factualCorrectionPolicy.json']
seals=[seal(R/x) for x in paths]
assert seals[0]['sha256']=='88ae350323bed4215071e9171c4e357b9a10f4e3912ccdda09de953fc4e558c8'
assert seals[6]['sha256']=='01e468f5d73ddb28edbde014a0b725f7d202340a692964d01f6fd174faec7fb1'
assert seals[-3]['sha256']=='ef9ee1bab6cfe6202b62e8d5605393f045d11fd64bd42ea1bcea769de15c8a01'
assert seals[-2]['sha256']=='aa2ffd8722f2e82ecbf4ec152485e2334946469627f3fa04845d441695e201ae'
assert seals[-1]['sha256']=='58d93745f554563f61960037b4466de70ae058a9b2295272d530d95f639880aa'
F=Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted')
mraw=(F/'archive-manifest.json').read_bytes();assert sha(mraw)=='13d956802cd881c0d6805c00c0dee48de07bd6615196e69f74fbf4056a710e34';entries=json.loads(mraw)['files']
state=[]
for row in entries:
    if row['key'].startswith('state/correction-admissions/') or row['key'] in ('state/heads/dailySnapshot.json','state/heads/production.json','state/heads/budget-2026-10-25.json','state/heads/gate-budget-2026-10-25.json'):
        p=F/row['key'];s=seal(p);assert s['sha256']==row['sha256'] and s['bytes']==row['bytes'];state.append(s)
assert sum('/correction-admissions/' in r['path'] for r in state)==6
snap=json.loads((F/'state/heads/dailySnapshot.json').read_bytes());assert len(snap['reviewQueue'])==38 and len(snap['factProvenance'])==4
j={'status':'PASS','base':'3bb9e40c8f6324aa4f419fbe13022ec4dcaece55','baseBlobsExact':exact,'changedTracked':changed,'missing':missing,'inputSeals':seals,'actualStateSeals':state,'actualArchivedAdmissions':6,'actualArchivedFactReferences':4,'actualArchivedHolds':38,'pendingRequestGroups':8,'pendingRequestRawSha256':seals[-2]['sha256'],'outerStampRawSha256':seals[-1]['sha256'],'actualArchiveLimit':'Frozen 8b3811 retained baseline only; current in-flight ordinary collection is audited separately.','requiredCombinedIntegration':'Merge only explicit PRN dispatch hunk into current collect.py, preserving accepted Cyera operation membership and elif dispatch. Re-run a focused combined route check before selecting any live operation.'}
(O/'protected-proof.json').write_text(json.dumps(j,indent=2,sort_keys=True));print({k:v for k,v in j.items() if k not in ('inputSeals','actualStateSeals')})
