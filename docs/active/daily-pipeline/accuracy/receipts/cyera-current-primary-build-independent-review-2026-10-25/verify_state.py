from pathlib import Path
import json,hashlib
O=Path('/var/tmp/smp-cyera-implementation-independent-20261025')
F=Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted')
entries=json.loads((F/'archive-manifest.json').read_bytes())['files']
rows=[r for r in entries if r['key'].startswith('state/correction-admissions/') or r['key'] in ('state/heads/dailySnapshot.json','state/heads/production.json','state/heads/budget-2026-10-25.json','state/heads/gate-budget-2026-10-25.json','state/heads/correction-collection.json')]
assert sum(r['key'].startswith('state/correction-admissions/') for r in rows)==6
seals=[]
for row in rows:
    p=F/row['key'];st=p.stat();raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    assert sha==row['sha256'] and len(raw)==row['bytes']
    seals.append({'path':str(p),'sha256':sha,'bytes':len(raw),'mtimeNs':st.st_mtime_ns,'inode':st.st_ino})
snapshot=json.loads((F/'state/heads/dailySnapshot.json').read_bytes());assert len(snapshot['reviewQueue'])==38 and len(snapshot['factProvenance'])==4
j={'status':'PASS','actualAdmissions':6,'factProvenance':4,'reviewQueue':38,'originalEventObjects':8,'budget':json.loads((F/'state/heads/budget-2026-10-25.json').read_bytes()),'seals':seals,'sourceClockAndDatesRebased':False,'newAdmissions':0,'reviewAuthority':'offline dormant build only; pending two correction groups are outside this historical-six worktree'}
(O/'actual-state-preservation.json').write_text(json.dumps(j,indent=2,sort_keys=True));print({k:v for k,v in j.items() if k!='seals'})
