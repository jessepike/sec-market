from pathlib import Path,PurePosixPath
from unittest.mock import patch
from types import SimpleNamespace
from contextlib import nullcontext
import copy,hashlib,json,os,socket,sys,subprocess,tempfile,io
R=Path('/mnt/mac/Users/jessepike/.codex/worktrees/q4-normal-intake/sec-market');A=Path('/var/tmp/smp-next-seven-actual-40190857026-20261025/extracted');O=Path('/var/tmp/smp-q4-exact-j-independent-20261025')
sys.path[:0]=[str(R/'web/scripts/pipeline'),str(R/'ops/ci')]
from contracts import canonical,digest,plan_run,validate_contract
from storage import LocalStore
import q4_qualification_origin as q4,q4_qualification_seed as seed,q4_baseline_migration as baseline,source_qualification_origin as origins
from discovery import discover
from fetcher import Fetcher
from agents import SubscriptionAgent
from bootstrap import GuardedRunner
from engine import Pipeline
from retained_audit import index_for,activate_compatibility
from corrections import load_policy,process_corrections,group_review_policy,_index

def need(v,msg):
 if not v:raise AssertionError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 p=Path(p);b=p.read_bytes();return {'sha256':sha(b),'bytes':len(b),'mtimeNs':p.stat().st_mtime_ns}
seals={}
def raw(p):
 p=Path(p);v=pin(p);need(seals.setdefault(str(p),v)==v,'INPUT_CHANGED:'+str(p));return p.read_bytes()
def read(p):return json.loads(raw(p))
identitypath=Path('/var/tmp/smp-narrow-pagination-independent-20261025/authenticated-archive-file-identities.json');identity=read(identitypath);need(sha(identitypath.read_bytes())=='ca73c500d9e7b66135945ab56034563c01a788caa66efbaf2f9962bdf16fd720','AUTH_CACHE_PIN')
need(identity['archiveRoot']==str(A) and identity['acknowledgedCommit']=='9deb0c9ce9fe34999da0cf13bb023dfdfecc15c8','AUTH_CACHE_ARCHIVE')
def stat_identity(p):
 s=p.stat();return {'bytes':s.st_size,'mtimeNs':s.st_mtime_ns,'inode':s.st_ino,'device':s.st_dev}
def unchanged_archive():
 for k,v in identity['files'].items():need(stat_identity(A/k)==v,'FROZEN_IDENTITY_CHANGED:'+k)
unchanged_archive();manifest=read(A/'archive-manifest.json');need(sha((A/'archive-manifest.json').read_bytes())==identity['manifestSha256']=='8da12977648ce0f6ed62f16de0b52c2257977f41404145adbecb363069e037e1','AUTH_MANIFEST');entries={e['key']:e for e in manifest['files']};need(set(entries)==set(identity['files']) and len(entries)==48245,'AUTH_INVENTORY')
class Frozen:
 def raw(self,k):
  need(type(k)is str and not k.startswith('/') and '..' not in PurePosixPath(k).parts,'PATH')
  e=entries.get('state/'+k)
  if e is None:need(not (A/'state'/k).exists(),'UNMANIFESTED');return None
  b=raw(A/'state'/k);need(len(b)==e['bytes'] and sha(b)==e['sha256'],'ARCHIVE_BYTES');return b
 def read(self,k):
  b=self.raw(k);return json.loads(b) if b is not None else None
 def get(self,ref):
  b=self.raw(ref['key'])
  if b is None:raise FileNotFoundError(ref['key'])
  need(sha(b)==ref['sha256'] and len(b)==ref['bytes'],'REF');return b
 def put(self,*a):raise AssertionError('FROZEN_WRITE')
 def write_once(self,*a):raise AssertionError('FROZEN_WRITE')
 def compare_and_swap(self,*a):raise AssertionError('FROZEN_WRITE')
class Memory(Frozen):
 def __init__(self,files=None):self.root=A/'state';self.memory=dict(files or {});self.changes=[]
 def raw(self,k):return self.memory[k] if k in self.memory else super().raw(k)
 def get(self,ref):
  b=self.raw(ref['key'])
  if b is None:raise FileNotFoundError(ref['key'])
  need(sha(b)==ref['sha256'] and len(b)==ref['bytes'],'MEMORY_REF');return b
 def put(self,v):
  b=v if isinstance(v,bytes) else canonical(v);ref={'key':'objects/'+sha(b),'sha256':sha(b),'bytes':len(b)};self.write_once(ref['key'],b);return ref
 def write_once(self,k,v):
  b=v if isinstance(v,bytes) else canonical(v);old=self.raw(k);need(old is None or old==b,'IMMUTABLE_COLLISION');self.memory[k]=b;self.changes.append(k)
 def compare_and_swap(self,name,expected,value):
  k='heads/'+name+'.json';need(self.read(k)==expected,'MEMORY_CAS');self.memory[k]=canonical(value);self.changes.append(k)
 def lock(self,*a,**kw):return nullcontext()
s=Frozen();vpath=R/'docs/active/daily-pipeline/accuracy/receipts/q4-two-source-normal-intake-2026-10-25/verification.json';worker=read(vpath)
need(sha(vpath.read_bytes())=='79ce23bb08ab202534489f3f5610f744181c54b409cd7c185641e6ee3ac4c156','WORKER_HANDOFF_PIN')
for rel,p in worker['files'].items():
 b=raw(R/rel);need(sha(b)==p['sha256'] and len(b)==p['bytes'],'STABLE_HANDOFF_FILE:'+rel)
for name,module in list(sys.modules.items()):
 filename=getattr(module,'__file__',None)
 if filename and Path(filename).is_file() and Path(filename).is_relative_to(R):raw(Path(filename))
# Protected core remains byte-identical to the reviewed base; git is read-only and runs before offline guards.
protected={}
for rel in ['web/scripts/pipeline/engine.py','web/scripts/pipeline/agents.py','web/scripts/pipeline/validation.py','web/scripts/pipeline/retained_audit.py','web/scripts/pipeline/selection.py','web/scripts/pipeline/separation.py','web/scripts/pipeline/documents.py','web/scripts/pipeline/q4_press_list.py','web/scripts/pipeline/q4_retained_primary_template.py','web/scripts/pipeline/q4_primary_qualification.py','ops/ci/html_qualification_seed.py']:
 b=raw(R/rel);old=subprocess.run(['mac','git','-C',str(R).removeprefix('/mnt/mac'),'show','7a1aee7b:'+rel],stdout=subprocess.PIPE,check=True).stdout;need(old==b,'PROTECTED_CODE_CHANGED:'+rel);protected[rel]=sha(b)
J=read(R/'contracts/market.json');H=read(R/'contracts/html-qualification-seeds'/q4.H/('contracts__'+q4.H+'.json'));need(digest(H)==q4.H,'INDEPENDENT_H')
manifest_seed=read(R/seed.PACKAGE['path']);files={e['key']:raw(R/e['path']) for e in manifest_seed['files']};need(len(files)==55 and sum(map(len,files.values()))==4742948,'PACKAGE_55')
need(all(not k.startswith(('heads/','observations/','runs/','budgets/','sessions/')) for k in files),'PACKAGE_MUTABLE_KEY')
transition=json.loads(files[q4.AUTHORITY['transition']['key']]);D=json.loads(files[q4.AUTHORITY['descriptor']['key']]);proof=json.loads(files[q4.AUTHORITY['proof']['key']])
need(q4.AUTHORITY['descriptor']['sha256']=='0223ae2af8878aecf73b5b6a5665d7840d592e7e299470e44bd31cedf7a12c1b' and q4.AUTHORITY['proof']['sha256']=='eb82ff6f74ffd0461a74cc6590e3cb1ef52adae2be698f4421b904c79d25d714','ACCEPTED_PROOF_PINS')
expected=copy.deepcopy(H)
for i,sid in [(34,'jfrog:official:1'),(52,'rapid7:official:1')]:
 need(H['sources'][i]['id']==sid,'SOURCE_POSITION');new=copy.deepcopy(J['sources'][i]);origin=new.pop('qualificationOrigin');old=copy.deepcopy(H['sources'][i]);old.update(kind='q4_press_list',registration='verified',url=q4.URLS[sid]);need(canonical(new)==canonical(old),'SOURCE_PATCH_EXTRA')
 need(origin['kind']=='bounded_q4_press_qualification' and origin['sourceResultIndex']==(0 if i==34 else 1) and origin['descriptor']==q4.AUTHORITY['descriptor'] and origin['proof']==q4.AUTHORITY['proof'] and origin['originalContract']==q4.AUTHORITY['originalContract'],'ORIGIN_CLOSED');expected['sources'][i]={**old,'qualificationOrigin':origin}
need(canonical(expected)==canonical(J) and digest(expected)=='47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a','INDEPENDENT_EXPECTED_J')
results=[];negatives=[]
def passed(name,detail=None):
 results.append({'case':name,'passed':True,'detail':detail});print('PASS '+name,flush=True)
def reject(name,fn):
 try:fn()
 except (ValueError,KeyError,TypeError,AssertionError,FileNotFoundError) as e:negatives.append({'case':name,'rejected':True,'reason':str(e)[:200]})
 else:raise AssertionError('MUTATION_ACCEPTED:'+name)
original_init=LocalStore.__init__
def guarded_init(self,root,*a,**kw):
 p=Path(root).resolve();need(p.is_relative_to(O),'LOCALSTORE_OUTSIDE_REVIEW_TEMP');return original_init(self,root,*a,**kw)
def audit(event,args):
 if event.startswith(('socket.','subprocess.')) or event in ('os.system','os.posix_spawn'):raise AssertionError('OFFLINE_EVENT_DENIED:'+event)
 if event=='open':
  mode,flags=args[1:3];write=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
  if write and isinstance(args[0],(str,bytes,os.PathLike)):need(Path(args[0]).resolve().is_relative_to(O),'WRITE_OUTSIDE_REVIEW_TEMP')
 if event in ('os.remove','os.rename','os.mkdir','os.rmdir','os.link','os.symlink','os.chmod','os.chown','os.utime','os.truncate'):
  if isinstance(args[0],(str,bytes,os.PathLike)):need(Path(args[0]).resolve().is_relative_to(O),'MUTATION_OUTSIDE_REVIEW_TEMP')
sys.addaudithook(audit)
NOW='2026-10-25T12:30:00Z';LATER='2026-10-25T13:30:00Z'
with patch.object(LocalStore,'__init__',guarded_init):
 reject('guard_frozen_LocalStore',lambda:LocalStore(A/'state'));reject('guard_socket',lambda:socket.socket())
 checked=seed.validate_seed(R,s,J,NOW);overlay=Memory(checked['files']);need(q4.inverse_policy(J,overlay)==H,'INVERSE');need(q4.validate_rows(H,J,transition)==H,'WHOLE_ROWS');need(len(plan_run(J,NOW)['tasks'])==len(plan_run(H,NOW)['tasks'])==557,'557_TASKS');passed('J01_J03_J07_full_55_file_graph_exact_pair')
 policies=[]
 for name,mutate in [('extra',lambda x:x.update(unreviewed=True)),('source_order',lambda x:x['sources'].reverse()),('supplier_order',lambda x:x['suppliers'].reverse()),('other_source_extra',lambda x:x['sources'][0].update(extra=True)),('model_budget',lambda x:x['model'].update(maxCallsPerRun=81)),('collection_window',lambda x:x['collection'].update(currentWindowDays=31)),('source_bool',lambda x:x['sources'][34]['qualificationOrigin'].update(sourceResultIndex=False)),('new_host',lambda x:x['sources'][34].update(allowedHosts=['evil.invalid'])),('second_origin',lambda x:x['sources'][52]['qualificationOrigin'].update(sourceResultIndex=0)),('version',lambda x:x.update(version='future')),('family',lambda x:x['sources'][34].update(family='other')),('origin_extra',lambda x:x['sources'][34]['qualificationOrigin'].update(currentCoverage=True))]:
  x=copy.deepcopy(J);mutate(x);policies.append({'name':name,'object':x});reject('pair_'+name,lambda x=x:q4.validate_rows(H,x,transition))
 for key in transition:
  t=copy.deepcopy(transition);t.pop(key);reject('transition_missing_'+key,lambda t=t:q4.validate_rows(H,J,t))
 t=copy.deepcopy(transition);t['changes'].reverse();reject('transition_change_order',lambda:q4.validate_rows(H,J,t))
 for sid in ('ping-identity:official:1','delinea:official:1','sonatype:official:1'):
  a=origins.qualification_predecessors(H,sid,overlay,NOW);b=origins.qualification_predecessors(J,sid,overlay,NOW);need(canonical(a)==canonical(b),'OLD_ORIGIN_BYTES');need(canonical(origins.resolve_inventory_origin(a[0],H,sid,overlay,NOW))==canonical(origins.resolve_inventory_origin(b[0],J,sid,overlay,NOW)),'OLD_RESOLVER_CHANGED')
 passed('J04_old_three_H_validators_and_inventory_exact')
 for sid,count in zip(q4.SOURCE_IDS,(206,323)):
  pred=origins.qualification_predecessors(J,sid,overlay,NOW)[0];resolved=origins.resolve_inventory_origin(pred,J,sid,overlay,NOW);need(len(resolved['items'])==count and resolved['authority']=='inventory_only','INVENTORY_ONLY')
  for name,mutate in [('bool_index',lambda p:p['qualificationOrigin'].update(sourceResultIndex=False if sid==q4.SOURCE_IDS[0] else True)),('extra_success',lambda p:p.update(coverageCredit=True)),('transition_size',lambda p:p['transition'].update(bytes=True)),('wrong_kind',lambda p:p.update(kind='html_qualification_inventory')),('wrong_source',lambda p:p.update(sourceId='other:official:1'))]:
   x=copy.deepcopy(pred);mutate(x);reject(sid+'_'+name,lambda x=x,sid=sid:q4.resolve(x,J,sid,overlay,NOW))
  reject(sid+'_future_proof',lambda sid=sid,pred=pred:q4.resolve(pred,J,sid,overlay,'2026-10-24T00:00:00Z'))
 passed('J06_new_origins_529_full_rows_no_current_credit')
 for field in ['descriptor','proof']:
  bad=Memory(checked['files']);bad.memory[q4.AUTHORITY[field]['key']]=b'{}';reject('corrupt_'+field,lambda bad=bad:q4.predecessors(J,q4.SOURCE_IDS[0],bad,NOW))
 reject('J_seed_under_H',lambda:seed.validate_seed(R,s,H,NOW))
 from onboarding import validate_qualification_probe_plan
 reject('live_H_probe_plan_under_J',lambda:validate_qualification_probe_plan(J,s,R/'contracts/source-qualification-probes.json'))
 passed('J05_historical_H_fixture_and_live_plan_separate')
 # All six current admissions replay with a reservation callback that must never run.
 requests=read(R/'contracts/factual-corrections.json');stamp=read(R/'web/src/data/tracker/factualCorrectionPolicy.json');policy=load_policy(R,J)
 need(stamp['policySha256']==policy['policySha256'],'GLOBAL_STAMP')
 need(policy['reviewPolicySha256ByGroup']=={g['id']:group_review_policy(g,H,requests['baseline']['sha256']) for g in requests['groups']},'GROUP_POLICIES')
 class NoModel:
  def __getattr__(self,n):raise AssertionError('MODEL_FORBIDDEN')
 def noreserve(*a,**k):raise AssertionError('RESERVATION_FORBIDDEN')
 corrected=process_corrections(R,overlay,J,NoModel(),noreserve,NOW);need(len(corrected['admitted'])==6 and corrected['pending']==[] and corrected['attempts']==[],'ADMISSIONS')
 admissions=[]
 for g in requests['groups']:
  key=_index(g,policy['reviewPolicySha256ByGroup'][g['id']]);need(overlay.read(key)==s.read(key),'ADMISSION_INDEX_CHANGED');ref=s.read(key)['admission'];need(overlay.get(ref)==s.get(ref),'ADMISSION_BYTES_CHANGED');admissions.append({'groupId':g['id'],'index':key,'admission':ref})
 passed('J12_six_admissions_exact_no_calls_no_reservations',admissions)
 actual=read(R/'web/src/data/generated/dailyMarket.json');old=read(R/'web/scripts/migration-proofs/q4-h-original/dailyMarket.json');expect=copy.deepcopy(old)
 expect['contractSha256']=digest(J);expect['coverage']['contractSha256']=digest(J)
 for row in expect['coverage']['sources']:
  if row['sourceId'] in q4.SOURCE_IDS:row['registration']='verified'
 expect['prospectiveMigration']=copy.deepcopy(actual['prospectiveMigration']);expect['supersededPolicy']=copy.deepcopy(actual['supersededPolicy']);expect['snapshotSha256']=digest({k:v for k,v in expect.items() if k!='snapshotSha256'})
 need(canonical(expect)==canonical(actual),'BASELINE_ALLOWED_DIFF');need(actual['supersededPolicy']['snapshot']==old and actual['coverage']['successfulTasks']==0 and actual['coverage']['validUntil'] is None and actual['checkedAt']==old['checkedAt'],'ZERO_CREDIT_OR_HISTORY')
 baseline.verify(R,J,overlay,actual);baseline_mutants=[]
 for name,mutate in [('new_checked_at',lambda x:x.update(checkedAt=NOW)),('intake_credit',lambda x:x['coverage']['intake'].update(evaluated=True)),('new_expiry',lambda x:x['coverage'].update(validUntil='2026-10-27T00:00:00Z')),('old_history_date',lambda x:x['supersededPolicy']['snapshot'].update(checkedAt=NOW)),('drop_old_chain',lambda x:x.pop('supersededPolicy')),('old_registration',lambda x:next(v for v in x['coverage']['sources'] if v['sourceId']==q4.SOURCE_IDS[0]).update(registration='candidate')),('processing_credit',lambda x:x['coverage'].update(successfulTasks=2))]:
  x=copy.deepcopy(actual);mutate(x);x['snapshotSha256']=digest({k:v for k,v in x.items() if k!='snapshotSha256'});reject('baseline_'+name,lambda x=x:baseline.verify(R,J,overlay,x));baseline_mutants.append(name)
 passed('J10_J11_independent_Python_baseline_projection_and_zero_credit',{'currentSnapshotSha256':actual['snapshotSha256'],'preservedOldSnapshotSha256':old['snapshotSha256'],'mutants':baseline_mutants})
 # Real importer uses actual J repo/context and require_lease; only remote acknowledgement is synthetic.
 import collect
 class RestoredLeaseStore(LocalStore):
  def read(self,k):
   value=super().read(k);return value if value is not None else globals()['s'].read(k)
  def get(self,ref):
   try:return super().get(ref)
   except FileNotFoundError:return globals()['s'].get(ref)
 root=Path(tempfile.mkdtemp(prefix='lease-fixture-',dir=O));state=RestoredLeaseStore(root/'state');session={'sessionId':'github-991-1','role':'collector','appRevision':'a'*40,'executionMode':'github_subscription','startedAt':NOW,'restored':{'commit':'b'*40}}
 LocalStore(root).write_once('session.json',session);state.compare_and_swap('cloud-lease',state.read('heads/cloud-lease.json'),{'sessionId':session['sessionId'],'expiresAt':'2026-10-25T14:00:00Z'})
 event=root/'event.json';event.write_bytes(canonical({'repository':{'full_name':'jessepike/sec-market','private':True},'inputs':{'source_probe':'false'}}))
 env={'GITHUB_ACTIONS':'true','GITHUB_REPOSITORY':'jessepike/sec-market','GITHUB_REF':'refs/heads/main','GITHUB_EVENT_NAME':'workflow_dispatch','GITHUB_SHA':session['appRevision'],'GITHUB_RUN_ID':'991','GITHUB_RUN_ATTEMPT':'1','GITHUB_EVENT_PATH':str(event)}
 checkpoint_calls=[]
 def ack(root,store,session,phase,result):
  checkpoint_calls.append({'phase':phase,'contractSha256':result['contractSha256']});remote={'commit':'c'*40,'manifestSha256':'d'*64};local=LocalStore(root);previous=local.read('heads/remote-archive.json');local.compare_and_swap('remote-archive',previous,remote)
  return {'archive':remote,'receipt':{'phase':phase,'sessionId':session['sessionId'],'appRevision':session['appRevision'],'role':'collector','contractSha256':digest(J),'result':result}}
 runtime=SimpleNamespace(REPO=R,utcnow=lambda:NOW,require_lease=collect.session_runtime.require_lease,checkpoint=ack)
 with patch.dict(os.environ,env,clear=True):
  first=seed.seed_before_collection(R,root,state,session,J,runtime);second=seed.seed_before_collection(R,root,state,session,J,runtime);need(first==second and len(checkpoint_calls)==2,'IMPORT_IDEMPOTENCE_OR_ACK')
  need(all((state.root/k).read_bytes()==b for k,b in checked['files'].items()),'IMPORT_FIXED_PAYLOAD');need(all(state.read(k)==s.read(k) for k in ['heads/latest-run.json','heads/dailySnapshot.json','heads/production.json','heads/budget-2026-10-25.json']),'IMPORT_MUTABLE_HEAD')
  runtime.checkpoint=lambda *a:{};reject('import_missing_remote_ack',lambda:seed.seed_before_collection(R,root,state,session,J,runtime));runtime.checkpoint=ack
  oldlease=state.read('heads/cloud-lease.json');state.compare_and_swap('cloud-lease',oldlease,{**oldlease,'releasedAt':NOW})
  with patch.object(state,'write_once',side_effect=AssertionError('IMPORT_ATTEMPTED_AFTER_RELEASE')):reject('released_J_lease',lambda:seed.seed_before_collection(R,root,state,session,J,runtime))
 passed('J08_J09_real_J_lease_full_import_idempotence_and_ack',{'imports':2,'files':55,'checkpointAcknowledgement':'synthetic remote receipt only; real context, preflight, lease and importer execute'})
 # Real ordinary Pipeline._task plus Fetcher has no HTTP transport except synthetic opener responses.
 indexhash=dict(zip(q4.SOURCE_IDS,['f7d84b288a6665280f4b8ade996b0bf64fe9c3fa0ea7a8a15b1adfb0826ccc19','cf3c57d1c2080d65656e9f291eca371aefd99909476d413bb5c90155bc742db8']))
 indexraw={sid:s.raw('objects/'+h) for sid,h in indexhash.items()};mem=Memory(checked['files']);mem.memory['heads/budget-2026-10-25.json']=canonical({'fetches':985,'calls':80,'documents':38});wire=[];statuschecks=[];phase=[0]
 def fake_login(args,**kw):
  need(args[1:]==['login','status'],'MODEL_EXEC_ATTEMPT');statuschecks.append(args);return subprocess.CompletedProcess(args,0,'Logged in using ChatGPT','')
 agent=SubscriptionAgent(J['model'],runner=GuardedRunner(SimpleNamespace(checkpoint=lambda:need(False,'AUTH_REFRESH')),runner=fake_login))
 class Response(io.BytesIO):
  status=200
  def __init__(self,body,url,mime):super().__init__(body);self.url=url;self.headers={'Content-Type':mime,'ETag':'"reviewer-'+sha(body)[:12]+'"'}
 from urllib.error import HTTPError
 def opener(req,timeout):
  wire.append({'phase':phase[0],'url':req.full_url,'headers':dict(req.header_items())})
  sid=next((sid for sid in q4.SOURCE_IDS if req.full_url==next(x['url'] for x in J['sources'] if x['id']==sid)),None)
  if sid:
   if phase[0]==1:raise HTTPError(req.full_url,304,'Not modified',{'Content-Type':'application/json'},None)
   return Response(indexraw[sid],req.full_url,'application/json')
  return Response(('<html><article><h1>Synthetic budget-only document</h1><p>'+('Fictional issuer text for reservation mechanics only. '*35)+'</p></article></html>').encode(),req.full_url,'text/html')
 normal_receipts=[];cycle_clocks=[NOW,LATER]
 with patch('fetcher.safe_url',side_effect=lambda url,*a,**kw:url),patch('fetcher.urllib.request.build_opener',return_value=SimpleNamespace(open=opener)),patch('fetcher.time.sleep',return_value=None):
  for cycle in range(2):
   phase[0]=cycle;clock=cycle_clocks[cycle];f=Fetcher(mem);pipe=Pipeline(J,mem,f,agent=agent,clock=lambda clock=clock:clock);plan=plan_run(J,clock);plan=mem.read('runs/'+plan['runId']+'/plan.json') or plan;mem.write_once('runs/'+plan['runId']+'/plan.json',plan);pipe.audit_index=index_for(mem);pipe.audit_compatibility=activate_compatibility(mem,plan,J,pipe.audit_index);pipe.prior_receipts={};pipe.force_refresh=True;pipe.replay=False;pipe.budget_name='budget-2026-10-25';agent.reserve=pipe._reserve;batch=[]
   with patch('fetcher.utcnow',return_value=clock):
    for task in plan['tasks']:
     if task['sourceId'] in q4.SOURCE_IDS:batch.append(pipe._task(plan,task))
   normal_receipts.append(batch)
 for batch in normal_receipts:
  for row,count in zip(batch,(206,323)):
   need(row['discoveryComplete'] and len(json.loads(mem.get(row['retainedInventoryManifest']))['items'])==count and row['validatedFacts']==[] and row['newFactIds']==[],'NORMAL_DISCOVERY_OR_SEMANTICS')
 counts=mem.read('heads/budget-2026-10-25.json');need(counts['calls']==80 and 38<=counts['documents']<=40 and agent.calls==0,'CALL_DOCUMENT_CAP');need(len([x for x in wire if x['phase']==0])<=6 and len([x for x in wire if x['phase']==1])<=6,'INCREMENTAL_FETCH_BOUND');need(counts['fetches']==985+len(wire),'LOGICAL_WIRE_COUNTS')
 observed=[]
 for sid in q4.SOURCE_IDS:
  source=next(x for x in J['sources'] if x['id']==sid);head=mem.read('heads/download-'+digest(source['url'])+'.json')
  # Engine uses source+URL cache keys; enumerate retained observations instead of guessing a head name.
  values=[json.loads(b) for k,b in mem.memory.items() if k.startswith('observations/')]
  current=[v for v in values if v.get('sourceId')==sid and v.get('requestedUrl')==source['url'] and v.get('httpStatus')==304]
  need(len(current)==1 and current[0]['fetchedAt']==LATER and current[0]['status']=='not_modified','GENUINE_NORMAL_304')
  oldobs=mem.read('observations/'+current[0]['reusesObservationId']+'.json');need(oldobs['httpStatus']==200 and oldobs['fetchedAt']==NOW and oldobs['body']==current[0]['body'],'200_304_BODY_CHAIN');observed.append({'sourceId':sid,'full200':oldobs,'conditional304':current[0]})
 passed('J13_J14_J20_J21_real_ordinary_200_304_and_real_zero_call_guard',{'cycles':2,'wire':wire,'countsBefore':{'fetches':985,'calls':80,'documents':38},'countsAfter':counts,'agentCalls':agent.calls,'loginStatusChecks':len(statuschecks),'normalObservations':observed,'factsPreserved':len(s.read('heads/dailySnapshot.json')['factProvenance']),'holdsPreserved':len(s.read('heads/dailySnapshot.json')['reviewQueue'])})
 # Parser failure, date uncertainty, variable length and old-only quiet use actual production discover.
 source=next(x for x in J['sources'] if x['id']==q4.SOURCE_IDS[0]);rows=json.loads(indexraw[source['id']])['GetPressReleaseListResult']
 def observed(payload,**kw):return {'sourceId':source['id'],'requestedUrl':source['url'],'finalUrl':source['url'],'status':'fetched','httpStatus':200,'fetchedAt':NOW,'contentType':'application/json','body':{'key':'objects/'+sha(payload),'sha256':sha(payload),'bytes':len(payload)},**kw}
 def found(payload,**kw):return discover(source,lambda _: (observed(payload,**kw),payload))
 shorter=canonical({'GetPressReleaseListResult':rows[1:]});need(found(shorter)['complete'] and len(found(shorter)['items'])==205,'HARDCODED_COUNT')
 for name,change in [('extra_envelope',lambda x:x.update(TotalRecords=206)),('continuation_envelope',lambda x:x.update(nextPage=1)),('malformed_middle',lambda x:x['GetPressReleaseListResult'][100].pop('Headline')),('duplicate_last',lambda x:x['GetPressReleaseListResult'].append(x['GetPressReleaseListResult'][-1])),('unordered',lambda x:x['GetPressReleaseListResult'].reverse()),('unsafe_url',lambda x:x['GetPressReleaseListResult'][0].update(LinkToDetailPage='https://evil.invalid/a')),('impossible_date',lambda x:x['GetPressReleaseListResult'][0].update(PressReleaseDate='02/30/2026 00:00:00'))]:
  x=json.loads(indexraw[source['id']]);change(x);b=canonical(x);value=found(b);need(not value['complete'] and value['items']==[],'MALFORMED_NOT_REJECTED:'+name);negatives.append({'case':'ordinary_'+name,'rejected':True,'reason':value['reason']})
 for name,kw in [('failed',{'status':'failed'}),('wrong_source',{'sourceId':q4.SOURCE_IDS[1]}),('wrong_final',{'finalUrl':'https://evil.invalid/'}),('bad_mime',{'contentType':'text/html'}),('bodyless304',{'status':'not_modified','httpStatus':304,'body':None}),('missing304origin',{'status':'not_modified','httpStatus':304})]:
  value=found(indexraw[source['id']],**kw);need(not value['complete'],'TRANSPORT_NOT_REJECTED:'+name);negatives.append({'case':'ordinary_'+name,'rejected':True,'reason':value['reason']})
 oldrow=copy.deepcopy(rows[-1]);oldrow.update(PressReleaseDate='01/01/2000 00:00:00',LinkToDetailPage='/news/news-details/2000/Old/default.aspx');b=canonical({'GetPressReleaseListResult':[oldrow]});need(found(b)['currentWindowQuiet'] is True,'QUIET_OLDER');need(not found(canonical({'GetPressReleaseListResult':[]}))['complete'],'EMPTY_NOT_QUIET')
 for literal,boundary,anomaly in [('10/25/2026 00:00:00',True,False),('10/26/2026 00:00:00',True,False),('10/27/2026 00:00:00',False,True)]:
  x=copy.deepcopy(rows[0]);x['PressReleaseDate']=literal;b=canonical({'GetPressReleaseListResult':[x,oldrow]});v=found(b);need(v['complete'] and not v['currentWindowQuiet'] and bool(v['boundaryAmbiguousItems'])==boundary and bool(v['sourceDateAnomalies'])==anomaly and v['timezone'] is None,'DATE_BOUNDARY');need(v['originalDateStrings'][v['items'][0]] in (literal,oldrow['PressReleaseDate']),'LITERAL_DATE_RETAINED')
 passed('J15_J16_J17_J18_J19_transport_malformed_dates_quiet_variable_length')
 from unittest.mock import patch as clockpatch
 original_found=found(indexraw[source['id']])
 with clockpatch('discovery.utcnow',return_value='2030-01-01T00:00:00Z'):need(found(indexraw[source['id']])==original_found,'ORIGINAL_OBSERVATION_CLOCK_REBASED')
 # Ordinary quota/deadline controls run unchanged; all altered counters below are isolated negative fixtures.
 caps=Memory(checked['files']);caps.memory['heads/budget-2026-10-25.json']=canonical({'fetches':5500,'calls':80,'documents':40});cap_pipe=Pipeline(J,caps,NoModel());cap_pipe.budget_name='budget-2026-10-25';before=caps.read('heads/budget-2026-10-25.json')
 for kind,limit in [('fetches',5500),('calls',80),('documents',40)]:reject('ordinary_exhausted_'+kind,lambda kind=kind,limit=limit:cap_pipe._reserve(kind,limit))
 need(caps.read('heads/budget-2026-10-25.json')==before,'DENIAL_MUTATED_CAPS');cap_pipe.deadline=0;reject('ordinary_expired_deadline',lambda:cap_pipe._reserve('fetches',5500));need(caps.read('heads/budget-2026-10-25.json')==before,'DEADLINE_MUTATED_CAPS')
 retry_state=Memory(checked['files']);retry_state.memory['heads/budget-2026-10-25.json']=canonical({'fetches':985,'calls':80,'documents':38});retry_pipe=Pipeline(J,retry_state,Fetcher(retry_state));retry_pipe.budget_name='budget-2026-10-25';attempts=[]
 def transient(req,timeout):
  attempts.append(req.full_url)
  if len(attempts)<3:raise HTTPError(req.full_url,503,'Synthetic transient',{},None)
  return Response(indexraw[source['id']],req.full_url,'application/json')
 with patch('fetcher.safe_url',side_effect=lambda url,*a,**kw:url),patch('fetcher.urllib.request.build_opener',return_value=SimpleNamespace(open=transient)),patch('fetcher.time.sleep',return_value=None),patch('fetcher.utcnow',return_value=NOW):
  retried=retry_pipe._fetch_transport(source,source['url'],None)
 need(len(attempts)==3 and retried['httpStatus']==200 and retry_state.read('heads/budget-2026-10-25.json')=={'fetches':986,'calls':80,'documents':38},'LOGICAL_VS_PHYSICAL_RETRY')
 passed('J22_ordinary_caps_deadline_and_retry_distinction',{'logicalReservations':1,'syntheticWireAttempts':3,'quotaDenials':3,'deadlineDenials':1})

 # Verify frozen ordinary facts/holds and all source clocks are untouched by memory-only execution.
 need(s.read('heads/dailySnapshot.json')==json.loads(s.raw('heads/dailySnapshot.json')),'FROZEN_SNAPSHOT_CHANGED')
 unchanged_archive()
 for p,v in seals.items():need(pin(Path(p))==v,'FINAL_INPUT_SEAL:'+p)
 # Emit small cross-language cases; Node independently verifies the full projection and mutations.
 cross={'J':digest(J),'H':digest(H),'expectedJCanonicalSha256':digest(expected),'expectedBaselineSha256':digest(actual),'policyMutationNames':[x['name'] for x in policies],'baselineMutationNames':baseline_mutants}
 (O/'cross-language-input.json').write_text(json.dumps(cross,indent=2)+'\n')
 output={'schemaVersion':1,'verdict':'PASS_python_and_static_pending_independent_JS','J':digest(J),'H':digest(H),'seedManifest':{'sha256':sha(raw(R/seed.PACKAGE['path'])),'files':len(files),'payloadBytes':sum(map(len,files.values()))},'results':results,'negativeCases':negatives,'negativeCount':len(negatives),'protectedCodeUnchanged':protected,'workerVerification':{'path':str(vpath),**pin(vpath)},'inputSealsBeforeAfter':seals,'allInputSealsUnchanged':True,'authenticatedArchiveReuse':{'commit':identity['acknowledgedCommit'],'manifestSha256':identity['manifestSha256'],'entries':48245,'identityReceipt':{'path':str(identitypath),**pin(identitypath)},'allFileIdentitiesUnchanged':True},'reviewerSourceRequests':0,'reviewerModelCalls':0,'reviewerRealArchiveSessionBudgetWrites':0,'reviewerRepoWrites':0,'futureOperationalCredit':False}
 (O/'python-review.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({'results':len(results),'negativeCases':len(negatives),'inputSeals':len(seals),'report':str(O/'python-review.json')}))
