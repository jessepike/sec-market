import collections,hashlib,json
from pathlib import Path
B=Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025')
APP=B/'application';S=B/'capture/extracted/state';OUT=B/'handback/docs/active/daily-pipeline/accuracy';OUT.mkdir(parents=True,exist_ok=True)
H=lambda b:hashlib.sha256(b).hexdigest()
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def pin(p):
 b=p.read_bytes();return {'path':str(p),'sha256':H(b),'bytes':len(b)}
def ref(k):
 b=(S/k).read_bytes();return {'key':k,'sha256':H(b),'bytes':len(b)}
contract=json.loads((APP/'contracts/market.json').read_bytes());policy=H(canonical(contract))
assert policy=='47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a'
head=json.loads((S/'heads/latest-run.json').read_bytes());coverage=json.loads((S/head['receipt']['key']).read_bytes())
planKey='runs/'+coverage['runId']+'/plan.json';plan=json.loads((S/planKey).read_bytes())
sources={v['id']:v for v in contract['sources']};tasks={v['taskId']:v for v in plan['tasks']};attempts={v['taskId']:v for v in coverage['receipts']}
oldpath=APP/'docs/active/daily-pipeline/accuracy/current-candidate-source-queue-2026-10-25.json'
old=json.loads(oldpath.read_bytes());oldrows={v['sourceId']:v for v in old['queue']}
diagnostics=[]
for name in ('next-seven-newsroom-actual-source-review-2026-10-25.json','narrow-listing-pagination-actual-source-review-2026-10-25.json'):
 path=APP/'docs/active/daily-pipeline/accuracy'/name;v=json.loads(path.read_bytes());diagnostics.append((name,v,pin(path)))
results=[]
for normalized in coverage['tasks']:
 t=tasks[normalized['taskId']];r=attempts[t['taskId']]
 results.append({'taskId':t['taskId'],'sourceId':t['sourceId'],'supplierId':t['supplierId'],
  'family':sources[t['sourceId']]['family'] if t['sourceId'] else t['family'],'kind':t['kind'],'required':t['required'],
  'intakeOutcome':normalized.get('intakeOutcome'),'intakeErrorCode':normalized.get('intakeErrorCode'),
  'gap':t['taskId'] in coverage['gapTaskIds'],'attempt':ref('runs/'+coverage['runId']+'/attempts/'+r['attemptId']+'.json')})
assert len(results)==557 and sum(not v['gap'] for v in results)==266
gaps=[v for v in results if v['gap']];gapcounts=dict(collections.Counter(v['intakeErrorCode'] or v['intakeOutcome'] for v in gaps))
assert len(gaps)==291 and gapcounts=={'NO_REGISTERED_DISCOVERY_SOURCE':254,'SOURCE_BINDING_UNVERIFIED':23,'HTTP_403':9,'HTTP_429':4,'Unapproved source/redirect host':1}
composition=dict(collections.Counter(v['family'] for v in results if not v['gap']))
candidateSources=[v for v in contract['sources'] if v['registration']=='candidate'];assert len(candidateSources)==23
queue=[]
for source in candidateSources:
 sid=source['id'];row=next(v for v in results if v['sourceId']==sid);prior=oldrows[sid];progress=[]
 for name,d,auditpin in diagnostics:
  selected=[x for x in d.get('explicitResults',[]) if x.get('target',{}).get('sourceId')==sid]
  if not selected:continue
  record='ci/source-probe-runs/'+str(d['actualRun']['id'])+'-1.json'
  progress.append({'actualRunId':str(d['actualRun']['id']),'actualDiagnosticRecord':ref(record),
   'qualificationCredit':False,'reviewAudit':{'path':'docs/active/daily-pipeline/accuracy/'+name,'sha256':auditpin['sha256'],'bytes':auditpin['bytes']},
   'literalTargets':[{'targetId':x['target']['targetId'],'url':x['target']['url'],'reason':x['target'].get('reason'),
    'observation':x['target'].get('observation'),'actualObservation':x.get('actualObservation')} for x in selected],
   'staticInventorySummary':{k:v for k,v in d.get('issuerCardInventoryAndCalendarWindow',{}).get(sid,{}).items() if k not in ('inventoryUrls','duplicateOrOverlapOccurrences')}})
 queue.append({'sourceId':sid,'taskId':row['taskId'],'supplierId':source['supplierId'],'supplierName':prior['supplierName'],
  'family':source['family'],'sourceSha256':H(canonical(source)),'configuredUrl':source['url'],'registration':'candidate',
  'normalTask':row,'diagnosticProgress':progress,'olderEvidenceQueue':{'path':'docs/active/daily-pipeline/accuracy/current-candidate-source-queue-2026-10-25.json','sourceId':sid},
  'historicalNextAction':prior['nextExactAction'],'currentDisposition':'SOURCE_BINDING_UNVERIFIED; retained diagnostic evidence has no ordinary intake credit',
  'nextAction':'Reconcile the linked retained diagnostic evidence against current source scope, dates, window, pagination and readable primary criteria before proposing an adapter; preserve all held/unknown results.' if progress else prior['nextExactAction']})
budget=json.loads((S/'heads/budget-2026-10-25.json').read_bytes());snap=json.loads((S/'heads/dailySnapshot.json').read_bytes())
value={'schemaVersion':1,'kind':'current_candidate_source_queue_J','policySha256':policy,'actualRunId':'40199860540','appRevision':'40fe14bb41f6b10c8edc8527ef7f78d7b4d0dcf8',
 'archive':{'commit':'8b3811df40cfdbec9d5ed52252524294566c88e0','manifestSha256':'13d956802cd881c0d6805c00c0dee48de07bd6615196e69f74fbf4056a710e34','entries':52273},
 'coverage':head['receipt'],'plan':ref(planKey),'planScheduledAt':plan['scheduledAt'],'coverageCheckedAt':coverage['checkedAt'],'snapshotCheckedAt':snap['checkedAt'],
 'requiredTasks':557,'successfulTasks':266,'gaps':291,'gapReasons':gapcounts,'successfulCompositionBySourceFamily':composition,
 'successfulCompositionReadable':{'citation':196,'SEC':48,'official':19,'investor':3},'candidateSources':23,'candidateFamilies':dict(collections.Counter(v['family'] for v in candidateSources)),
 'requiredTaskResults':results,'gapTaskIds':coverage['gapTaskIds'],'queue':queue,'sourceQualificationProgress':{'jfrog:official:1':{'ordinaryIntake':'checked','inventoryDocuments':206},'rapid7:official:1':{'ordinaryIntake':'checked','inventoryDocuments':323}},
 'accountingAsOfActualArchive':{'budget':budget,'gateAttempts':2,'modelCallsThisActualRun':0,'processingReviewedInventoryDocuments':40,'historicalReviewedInventoryDocuments':41,
  'explanation':'documents39 is the cumulative daily charged reservation ledger; processing40 and historical41 count reviewed inventory dispositions including retained evidence. They measure different populations and are not new-run model-call counts.',
  'notADispatchAllowance':True},'privateValidUntil':snap['coverage']['validUntil'],'reviewQueueCount':len(snap['reviewQueue']),'factReferences':len(snap['factProvenance']),
 'frozen25CandidateQueue':pin(oldpath),'auditEvidence':'docs/active/daily-pipeline/accuracy/q4-two-source-normal-intake-actual-source-review-2026-10-25.json',
 'scope':{'sourceRequestsByQueue':0,'modelRequestsByQueue':0,'qualificationCreditByQueue':0,'semanticCreditByQueue':0,'publicationCreditByQueue':0},
 'note':'The two Q4 sources moved out of this candidate queue only after actual normal HTTP200 discovery and full retained replay. The remaining23 stay candidates. Private freshness does not renew the accepted public release.'}
js=OUT/'current-candidate-source-queue-J-2026-10-25.json';js.write_text(json.dumps(value,indent=2)+'\n')
lines=['# Current J candidate source queue','',
 'The actual ordinary run checked 266 of 557 obligations. The remaining 291 gaps are 254 missing discovery bindings, 23 unqualified candidates, nine HTTP 403 responses, four HTTP 429 responses and one unapproved source or redirect host.',
 '', 'The checked obligations comprise 196 citation checks, 48 SEC obligations, 19 official-announcement sources and three investor/acquirer sources. JFrog and Rapid7 each completed a real ordinary HTTP 200 index check, retaining all 206 and 323 source records; both still have zero reviewed processing or historical records. Their source calendars remain dates without an invented timezone.',
 '', 'The settled daily ledger is 1,511 fetches, 80 model calls and 39 charged documents, with two gate attempts. This run made zero model calls. The processing count of 40 reviewed inventory documents and historical count of 41 count retained dispositions; they are different measures from the daily document-reservation ledger. These counts authorize no further dispatch.',
 '', 'The new private snapshot expires at 2026-10-26T20:00:16.075798+00:00. The public release retains its existing clocks. The automatic callback skipped publication.',
 '', 'All 557 exact task/source results, 291 gap identities, current23 source bindings and raw diagnostic references are in the JSON companion. The earlier25-candidate queue remains unchanged. Diagnostic progress remains evidence for later qualification work; it does not qualify any of the remaining23 candidates.',
 '', '## Exact current candidate tasks','', '| Source ID | Current task ID | Retained progress |','|---|---|---|']
for row in queue:
 runids=', '.join(v['actualRunId'] for v in row['diagnosticProgress']) or 'Earlier retained queue evidence'
 lines.append('| `'+row['sourceId']+'` | `'+row['taskId']+'` | '+runids+'; still unqualified. |')
lines.extend(['','The JSON links each newer seven-source and listing/pagination record by exact retained reference, observation, body and committed review hash. Earlier source-specific next actions are labeled historical. I would use those retained bytes to finish the next closed adapter proposal before requesting additional source observations.','', 'Evidence: `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/current-candidate-source-queue-J-2026-10-25.json`.'])
(OUT/'current-candidate-source-queue-J-2026-10-25.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'candidateCount':len(queue),'gapReasons':gapcounts,'composition':composition,'json':pin(js)},indent=2))
