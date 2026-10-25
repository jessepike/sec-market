"""Actual ordinary-J retained replay. No transport or writable frozen stores."""
import collections,hashlib,json,socket,sys
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch

B=Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025')
APP=B/'application';CAP=B/'capture';NEW=CAP/'extracted'
OLD=Path('/var/tmp/smp-listing-pagination-actual-40193925490-20261025/extracted')
RUN='40199860540';REV='40fe14bb41f6b10c8edc8527ef7f78d7b4d0dcf8'
sys.path[:0]=[str(APP/'ops/ci'),str(APP/'web/scripts/pipeline')]
from contracts import canonical,digest,instant,require,utcnow
from storage import LocalStore
from validation import reconcile
from snapshot import collector_continuity
from discovery import discover
from retained_audit import bounded
import q4_qualification_origin as q4
import q4_qualification_seed as seed
import source_qualification_origin as origins
from corrections import load_policy,process_corrections,group_review_policy

def manifest(root):
 raw=(root/'archive-manifest.json').read_bytes();m=json.loads(raw)
 return raw,{e['key']:e for e in m['files']}
oldraw,oldm=manifest(OLD);newraw,newm=manifest(NEW)
require(digest(oldraw)=='148842177a7e7d9a5fd5c2ea4574576264a957b41958ee4cdf5effa80ea029c2','Prior9e4a manifest differs')
download=json.loads((CAP/'download-proof.json').read_bytes())
require(download['manifestSha256']==digest(newraw) and download['allManifestEntriesVerified'] is True,'New actual archive authentication missing')
def full_check(root,entries):
 ids=[]
 for key,e in sorted(entries.items()):
  p=root/key;raw=p.read_bytes();st=p.stat()
  require(len(raw)==e['bytes'] and digest(raw)==e['sha256'],'Retained manifest bytes differ: '+key)
  ids.append([key,e['bytes'],e['sha256'],st.st_mtime_ns,st.st_ino,st.st_dev])
 return ids
beforeOld=full_check(OLD,oldm);beforeNew=full_check(NEW,newm)
class RO:
 def __init__(self,root):self.root=root/'state';self.putLookups=0
 def _path(self,key):
  require(type(key) is str and not key.startswith('/') and '..' not in key.split('/'),'Unsafe frozen lookup')
  return self.root/key
 def read(self,key):
  p=self._path(key)
  return json.loads(p.read_bytes()) if p.exists() else None
 def get(self,ref):
  b=self._path(ref['key']).read_bytes();require(len(b)==ref['bytes'] and digest(b)==ref['sha256'],'Frozen reference differs');return b
 def put(self,value):
  b=value if type(value) is bytes else canonical(value);ref={'key':'objects/'+digest(b),'sha256':digest(b),'bytes':len(b)}
  require(self.get(ref)==b,'Verifier requested nonretained object');self.putLookups+=1;return ref
 def write_once(self,*a,**kw):raise AssertionError('Frozen writes prohibited')
 def compare_and_swap(self,*a,**kw):raise AssertionError('Frozen head writes prohibited')
s=RO(NEW);o=RO(OLD)
contract=json.loads((APP/'contracts/market.json').read_bytes());require(digest(contract)==q4.AUTHORITY['activatedContractSha256'],'ExactJ required')
raw=json.loads((CAP/'collection-receipt.json').read_bytes());clock=s.read('ci/collection-runs/'+RUN+'-1.json')
require(clock is not None and all(clock[k]==v for k,v in raw.items() if k in clock),'Actual outer receipt differs')
require(clock['githubRunId']==RUN and clock['githubEventName']=='workflow_dispatch' and clock['githubRef']=='refs/heads/main' and clock['appRevision']==REV,'Actual outer run identity differs')
head=s.read('heads/latest-run.json');coverage=json.loads(s.get(head['receipt']));plan=s.read('runs/'+coverage['runId']+'/plan.json')
snap=s.read('heads/dailySnapshot.json');prior=o.read('heads/dailySnapshot.json')
require(coverage['contractSha256']==snap['contractSha256']==digest(contract),'ActualJ receipt/snapshot policy differs')
require(raw['snapshotSha256']==snap['snapshotSha256'] and raw['reviewQueue']==len(snap['reviewQueue']),'Actual snapshot identity differs')
receipts=[]
for r in coverage['receipts']:
 saved=s.read('runs/'+coverage['runId']+'/attempts/'+r['attemptId']+'.json');require(saved==r,'Attempt differs');receipts.append(saved)
with patch.object(socket,'socket',side_effect=AssertionError('Audit network prohibited')),patch.object(LocalStore,'__init__',side_effect=AssertionError('Frozen initialization prohibited')):
 replayed=reconcile(plan,receipts,contract,coverage['checkedAt'],s);require(replayed==coverage,'Complete557 reconciliation differs')
 continuity=collector_continuity(snap,contract,coverage,s)
 checkedSeed=seed.validate_seed(APP,s,contract,coverage['checkedAt'])
 original=q4.inverse_policy(contract,s)
 originResults={}
 for sid in ('ping-identity:official:1','delinea:official:1','sonatype:official:1',*q4.SOURCE_IDS):
  rows=origins.qualification_predecessors(contract,sid,s,coverage['checkedAt']);require(len(rows)==1,'Five-origin predecessor differs')
  v=origins.resolve_inventory_origin(rows[0],contract,sid,s,coverage['checkedAt']);require(v['authority']=='inventory_only','Origin acquired semantic authority')
  originResults[sid]={'documents':len(v['items']),'itemsSha256':digest(v['items']),'completedAt':v['completedAt'],'authority':v['authority']}
 class NoModel:
  def __getattr__(self,name):raise AssertionError('Audit model prohibited')
 def deny(*a,**kw):raise AssertionError('Audit reservation prohibited')
 corrections=process_corrections(APP,s,contract,NoModel(),deny,coverage['checkedAt'])
 require(len(corrections['admitted'])==6 and not corrections['pending'] and not corrections['attempts'],'Six admissions did not replay')
 require(clock['corrections']['admitted']==corrections['admitted'] and not clock['corrections']['pending'],'Actual correction result differs')
 context=load_policy(APP,contract)
 require(context['reviewPolicySha256ByGroup']=={g['id']:group_review_policy(g,original,context['requests']['baseline']['sha256']) for g in context['requests']['groups']},'Per-group correction authority changed')
 for row in corrections['admitted']:require(s.get(row['admission'])==o.get(row['admission']),'Prior admission bytes changed')
 retainedRaw=q4.retained.primary._blob(s,q4.AUTHORITY['descriptor'])
 _,_,originalNormalized=q4.retained._validate(original,s,retainedRaw)
 q4Rows=[]
 for sid in q4.SOURCE_IDS:
  source=next(v for v in contract['sources'] if v['id']==sid)
  found=[r for r in receipts if r['sourceId']==sid];require(len(found)==1,'Two normal Q4 task receipts required')
  r=found[0];m=json.loads(s.get(r['itemManifest']))
  obs=[s.read('observations/'+oid+'.json') for oid in m['observations']]
  byurl={v['requestedUrl']:v for v in obs}
  def request(url):
   require(url in byurl,'Actual Q4 response missing');v=byurl[url];return v,s.get(v['body']) if v.get('body') else b''
  discovery=discover(source,request)
  require(discovery['complete'] and discovery['items']==m['items'] and discovery['itemDates']==m['itemDates'],'Actual ordinary Q4 discovery replay differs')
  require(discovery.get('timezone') is None,'Unknown Q4 timezone changed')
  predecessor=origins.resolve_inventory_origin(origins.qualification_predecessors(contract,sid,s,coverage['checkedAt'])[0],contract,sid,s,coverage['checkedAt'])
  require(set(predecessor['items']).issubset(m['items']),'Original Q4 inventory rows lost')
  oldstream=next(v for v in originalNormalized['streams'] if v['sourceId']==sid)
  require(all(m['itemDates'].get(url)==date for url,date in oldstream['itemDates'].items()),'Original Q4 calendar dates changed')
  require(all(discovery['originalDateStrings'].get(url)==literal for url,literal in oldstream['originalDateStrings'].items()),'Original Q4 written date strings changed')
  transport=[]
  for ob in obs:
   require('state/observations/'+ob['observationId']+'.json' not in oldm,'Diagnostic observation mistaken for actual normal intake')
   require(ob['requestedUrl']==ob['finalUrl']==source['url'],'Actual ordinary Q4 URL differs')
   if ob['status']=='not_modified':
    ancestor=s.read('observations/'+ob['reusesObservationId']+'.json')
    require(ob['httpStatus']==304 and ancestor['body']==ob['body'],'304 retained-chain differs')
   else:require(ob['status']=='fetched' and ob['httpStatus']==200,'Actual normal Q4 transport did not succeed')
   transport.append(ob)
  normalized=next(v for v in coverage['tasks'] if v['taskId']==r['taskId']);require(normalized['intakeOutcome'] in ('checked','quiet'),'Actual Q4 normal intake not credited')
  q4Rows.append({'sourceId':sid,'normalizedTask':normalized,'attempt':r,'indexManifest':m,'discovery':{k:v for k,v in discovery.items() if k!='observations'},'ordinaryObservations':transport,'originalInventoryDocuments':len(predecessor['items']),'originalInventoryItemsSha256':digest(predecessor['items']),'ordinaryInventoryDocuments':len(m['items'])})
missing=sorted(set(oldm)-set(newm));changed=[k for k in oldm if k in newm and oldm[k]!=newm[k]]
require(not missing and all(k.startswith('state/heads/') for k in changed),'Old immutable archive entry changed')
require(len(prior['factProvenance'])==4 and all(snap['factProvenance'].get(k)==v for k,v in prior['factProvenance'].items()),'Old fact references changed')
for key in ('events','evidence'):
 before={v['id']:v for v in prior[key]};after={v['id']:v for v in snap[key]}
 require(all(after.get(k)==v for k,v in before.items()),'Old '+key+' content/date differs')
identity=lambda q:(q.get('factId'),q.get('reason'))
oldq={identity(v):v for v in prior['reviewQueue']};newq={identity(v):v for v in snap['reviewQueue']}
require(len(oldq)==len(prior['reviewQueue'])==38 and set(oldq).issubset(newq),'Old held identity removed')
def inventories(root,receipt):
 pairs=set()
 for row in receipt['receipts']:
  for key in ('itemManifest','pendingManifest','retainedInventoryManifest'):
   if row.get(key):
    m=json.loads(root.get(row[key]));pairs.update((row['sourceId'],url) for url in m['items'])
 return pairs
oldhead=o.read('heads/latest-run.json');oldcoverage=json.loads(o.get(oldhead['receipt']))
oldpairs=inventories(o,oldcoverage);newpairs=inventories(s,coverage)
require(oldpairs.issubset(newpairs),'Prior normal inventory pair lost')
observations={}
sourceMap={v['id']:v for v in contract['sources']}
for r in receipts:
 ids=json.loads(s.get(r['itemManifest']))['observations'] if bounded(sourceMap.get(r.get('sourceId')),contract) else r.get('observationIds',[])
 for oid in ids:
  ob=s.read('observations/'+oid+'.json')
  if ob and ob['status'] in ('fetched','not_modified','retained_immutable'):
   if ob.get('body'):s.get(ob['body'])
   if ob['status']=='not_modified':
    ancestor=s.read('observations/'+ob['reusesObservationId']+'.json');require(ob['httpStatus']==304 and ancestor and ob['body']==ancestor['body'],'Actual304 chain differs')
   observations[oid]={'sourceId':ob['sourceId'],'observationId':oid,'status':ob['status'],'httpStatus':ob.get('httpStatus'),'fetchedAt':ob['fetchedAt'],'verifiedAt':ob.get('verifiedAt'),'effectiveClock':ob.get('verifiedAt',ob['fetchedAt']),'body':ob.get('body'),'reusesObservationId':ob.get('reusesObservationId'),'requestedUrl':ob.get('requestedUrl'),'newSinceBaseline':'state/observations/'+oid+'.json' not in oldm}
clocks=[instant(v['effectiveClock']) for v in observations.values()]
expiry=(min(clocks)+timedelta(hours=contract['schedule']['overdueHours'])).isoformat() if clocks else None
require(expiry==snap['coverage']['validUntil'],'Actual source expiry differs')
sessions=[s.read(str(p.relative_to(NEW/'state'))) for p in sorted((NEW/'state/cloud/sessions'/digest('github-'+RUN+'-1')).glob('*.json'))]
byphase={v['phase']:v for v in sessions}
require(all(p in byphase for p in ('bootstrap','qualification_seeded','collection','finish')),'Actual seed/collector checkpoint missing')
for value in sessions:require(value['sessionId']=='github-'+RUN+'-1' and value['appRevision']==REV and value['contractSha256']==digest(contract),'Actual session identity differs')
seeded=byphase['qualification_seeded'];require(seeded['result']=={**{k:v for k,v in checkedSeed.items() if k!='files'},'coverageCredit':False,'semanticAdmission':False,'sourceChecksCredited':0},'Actual immutable seed checkpoint differs')
times=[instant(byphase[p]['checkedAt']) for p in ('bootstrap','qualification_seeded','collection','finish')];require(times==sorted(times),'Actual seed checkpoint order differs')
lease=s.read('heads/cloud-lease.json');require(lease['sessionId']=='github-'+RUN+'-1' and lease.get('releasedAt'),'Actual collector lease not released')
budgets={k:s.read('heads/'+k+'-2026-10-25.json') for k in ('budget','gate-budget','publication-budget')}
escrow=s.read('ci/budget-escrows/'+digest('github-'+RUN+'-1')+'.json')
statcheck=lambda root,rows:all((root/key).stat().st_mtime_ns==mtime and (root/key).stat().st_ino==ino and (root/key).stat().st_dev==dev and (root/key).stat().st_size==size for key,size,sha,mtime,ino,dev in rows)
require(statcheck(OLD,beforeOld) and statcheck(NEW,beforeNew),'Frozen retained identities changed during replay')
proof={'scope':'ACTUAL_ORDINARY_J_INTAKE_REPLAY','actualRunId':RUN,'appRevision':REV,'archive':download,'priorCommit':'9e4a9806fdcc1b7cd6f91314b8b4ff4bb4ef2174','priorManifestSha256':digest(oldraw),'priorEntries':len(oldm),'actualEntries':len(newm),'requiredTasks':coverage['requiredTasks'],'successfulTasks':coverage['successfulTasks'],'complete':coverage['complete'],'outcome':coverage['outcome'],'reconciliation557Replayed':True,'runId':coverage['runId'],'planScheduledAt':plan['scheduledAt'],'coverageCheckedAt':coverage['checkedAt'],'snapshotSha256':snap['snapshotSha256'],'snapshotCheckedAt':snap['checkedAt'],'validUntil':snap['coverage']['validUntil'],'intake':coverage['intake'],'processing':coverage['processing'],'historicalReview':coverage['historicalReview'],'gapBreakdown':dict(collections.Counter(v.get('intakeErrorCode') or v.get('intakeOutcome') or v.get('outcome','unknown') for v in coverage['tasks'] if v['taskId'] in coverage['gapTaskIds'])),'q4Sources':q4Rows,'allFiveOrigins':originResults,'original529CalendarDatesAndWrittenStringsExact':True,'originalQ4InventoryDocuments':sum(v['originalInventoryDocuments'] for v in q4Rows),'actualQ4InventoryDocuments':sum(v['ordinaryInventoryDocuments'] for v in q4Rows),'sourceObservations':list(observations.values()),'sourceObservationCounts':dict(collections.Counter(v['status'] for v in observations.values())),'sourceClockMinimum':min(clocks).isoformat() if clocks else None,'sourceClockMaximum':max(clocks).isoformat() if clocks else None,'newSourceObservationCount':sum(v['newSinceBaseline'] for v in observations.values()),'seed':{'manifestSha256':checkedSeed['manifestSha256'],'files':len(checkedSeed['files']),'preservation':checkedSeed['preservation'],'checkpoint':seeded},'sessions':sessions,'corrections':corrections,'perGroupReviewPolicies':context['reviewPolicySha256ByGroup'],'oldImmutableRecordsPreserved':True,'baselineMissingEntries':missing,'changedMutableHeads':changed,'priorInventoryPairs':len(oldpairs),'priorInventoryPairsSha256':digest(sorted(oldpairs)),'actualInventoryPairs':len(newpairs),'actualInventoryPairsSha256':digest(sorted(newpairs)),'factProvenance':snap['factProvenance'],'allFourPriorFactReferencesExact':True,'reviewQueueCount':len(snap['reviewQueue']),'priorHoldIdentitiesPreserved':len(oldq),'priorHoldRowsExact':sum(newq[k]==v for k,v in oldq.items()),'newHolds':[v for k,v in newq.items() if k not in oldq],'budgetHeads':budgets,'priorBudget':o.read('heads/budget-2026-10-25.json'),'budgetEscrow':escrow,'lease':lease,'actualProcessModelCalls':raw.get('modelCalls'),'continuity':continuity,'frozenInputSeals':{'baseline':digest(beforeOld),'actual':digest(beforeNew),'baselineFiles':len(beforeOld),'actualFiles':len(beforeNew),'unchangedAfter':True},'sourceRequestsByAudit':0,'modelRequestsByAudit':0,'archiveWritesByAudit':0,'verifierExistingObjectLookups':s.putLookups,'publicationProof':False,'publicDataStillNeedsSeparatePublisherReceipt':True}
(B/'actual-ordinary-j-audit.json').write_bytes(canonical(proof))
print(json.dumps({k:proof[k] for k in ('actualRunId','successfulTasks','requiredTasks','intake','processing','historicalReview','validUntil','originalQ4InventoryDocuments','actualQ4InventoryDocuments','reviewQueueCount','budgetHeads','frozenInputSeals')},indent=2))
