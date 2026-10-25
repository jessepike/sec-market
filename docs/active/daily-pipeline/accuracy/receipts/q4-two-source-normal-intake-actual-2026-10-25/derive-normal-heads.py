import hashlib,json,sys
from pathlib import Path
B=Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025');S=B/'capture/extracted/state'
sys.path.insert(0,str(B/'application/web/scripts/pipeline'))
from contracts import digest
proof=json.loads((B/'actual-ordinary-j-audit.json').read_bytes());rows=[]
for v in proof['q4Sources']:
 sid=v['sourceId'];attempt=v['attempt'];ob=v['ordinaryObservations'][0];url=ob['requestedUrl']
 key='heads/download-'+digest({'source':sid,'url':url})+'.json';raw=(S/key).read_bytes();assert json.loads(raw)==ob
 task='heads/task-'+attempt['taskId']+'.json';traw=(S/task).read_bytes();assert json.loads(traw)==attempt
 source='heads/source-'+digest(sid)+'.json';sraw=(S/source).read_bytes() if (S/source).exists() else None
 rows.append({'sourceId':sid,'ordinaryLogicalFetches':len(attempt['observationIds']),'newDownloadHead':{'key':key,'sha256':digest(raw),'bytes':len(raw),'value':ob},'currentTaskHead':{'key':task,'sha256':digest(traw),'bytes':len(traw)},'legacySourceHead':{'key':source,'exists':sraw is not None,'sha256':digest(sraw) if sraw is not None else None},'factValidations':len(attempt.get('validatedFacts',[])),'documentValidations':len(attempt.get('documentValidations',[]))})
assert sum(v['ordinaryLogicalFetches'] for v in rows)==2 and all(v['factValidations']==v['documentValidations']==0 for v in rows)
(B/'ordinary-q4-heads.json').write_text(json.dumps({'sources':rows,'normalQ4LogicalFetches':2,'modelCalls':0,'factOrDocumentValidations':0,'note':'Normal source200 download heads and task heads are actual new evidence; original diagnostic objects have not been imported as normal heads.'},indent=2)+'\n')
print(json.dumps({'normalQ4LogicalFetches':2,'factOrDocumentValidations':0,'sourceHeadExists':[r['legacySourceHead']['exists'] for r in rows]},indent=2))
