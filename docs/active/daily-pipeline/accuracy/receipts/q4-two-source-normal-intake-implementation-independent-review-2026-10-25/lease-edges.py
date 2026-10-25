from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json,sys,os,tempfile,socket,hashlib
R=Path('/mnt/mac/Users/jessepike/.codex/worktrees/q4-normal-intake/sec-market');O=Path('/var/tmp/smp-q4-exact-j-independent-20261025');sys.path[:0]=[str(R/'web/scripts/pipeline'),str(R/'ops/ci')]
from contracts import canonical,digest
from storage import LocalStore
from q4_intake_fixtures import ReadOnlyArchive
import q4_qualification_seed as seed,q4_qualification_origin as q4,collect
S=ReadOnlyArchive();J=json.loads((R/'contracts/market.json').read_bytes());NOW='2026-10-25T12:30:00Z';cases=[];init=LocalStore.__init__
def need(v,msg):
 if not v:raise AssertionError(msg)
def guard(self,root,*a,**kw):need(Path(root).resolve().is_relative_to(O),'FROZEN_LOCALSTORE_DENIED');return init(self,root,*a,**kw)
class Restored(LocalStore):
 def read(self,k):
  v=super().read(k);return v if v is not None else S.read(k)
 def get(self,ref):
  try:return super().get(ref)
  except FileNotFoundError:return S.get(ref)
def fixture():
 root=Path(tempfile.mkdtemp(prefix='lease-edge-',dir=O));state=Restored(root/'state');session={'sessionId':'github-992-1','role':'collector','appRevision':'a'*40,'executionMode':'github_subscription','startedAt':NOW,'restored':{'commit':'b'*40}};LocalStore(root).write_once('session.json',session);state.compare_and_swap('cloud-lease',state.read('heads/cloud-lease.json'),{'sessionId':session['sessionId'],'expiresAt':'2026-10-25T14:00:00Z'});event=root/'event.json';event.write_bytes(canonical({'repository':{'full_name':'jessepike/sec-market','private':True},'inputs':{'source_probe':'false'}}));env={'GITHUB_ACTIONS':'true','GITHUB_REPOSITORY':'jessepike/sec-market','GITHUB_REF':'refs/heads/main','GITHUB_EVENT_NAME':'workflow_dispatch','GITHUB_SHA':session['appRevision'],'GITHUB_RUN_ID':'992','GITHUB_RUN_ATTEMPT':'1','GITHUB_EVENT_PATH':str(event)}
 def ack(root,store,current,phase,result):
  remote={'commit':'c'*40,'manifestSha256':'d'*64};local=LocalStore(root);local.compare_and_swap('remote-archive',local.read('heads/remote-archive.json'),remote);return {'archive':remote,'receipt':{'phase':phase,'sessionId':current['sessionId'],'appRevision':current['appRevision'],'role':'collector','contractSha256':digest(J),'result':result}}
 runtime=SimpleNamespace(REPO=R,utcnow=lambda:NOW,require_lease=collect.session_runtime.require_lease,checkpoint=ack)
 return root,state,session,event,env,runtime,ack
def reject(name,fn,kind=ValueError):
 try:fn()
 except kind as e:cases.append({'case':name,'rejected':True,'reason':str(e)})
 else:raise AssertionError('ACCEPTED:'+name)
with patch.object(socket,'socket',side_effect=AssertionError('SOCKET_DENIED')),patch.object(LocalStore,'__init__',guard):
 checked=seed.validate_seed(R,S,J,NOW)
 root,state,session,event,env,runtime,ack=fixture()
 with patch.dict(os.environ,env,clear=True),patch.object(seed,'validate_seed',return_value=checked),patch.object(state,'write_once',side_effect=AssertionError('WRITE_BEFORE_CONTEXT_REJECTION')):
  for name,changes in [('publisher_role',{'role':'publisher'}),('diagnostic_session',{'checkpointProfile':'source_probe'}),('wrong_session_run',{'sessionId':'github-993-1'}),('unapproved_mode',{'executionMode':'local'})]:
   reject(name,lambda changes=changes:seed.seed_before_collection(R,root,state,{**session,**changes},J,runtime))
  with patch.dict(os.environ,{'GITHUB_REF':'refs/heads/preview'}):reject('preview_ref',lambda:seed.seed_before_collection(R,root,state,session,J,runtime))
  with patch.dict(os.environ,{'GITHUB_SHA':'b'*40}):reject('wrong_app_revision',lambda:seed.seed_before_collection(R,root,state,session,J,runtime))
  original_event=event.read_bytes();event.write_bytes(canonical({'repository':{'full_name':'jessepike/sec-market','private':False},'inputs':{}}));reject('nonprivate_event',lambda:seed.seed_before_collection(R,root,state,session,J,runtime));event.write_bytes(original_event)
  old=state.read('heads/cloud-lease.json')
  for name,change in [('wrong_lease_owner',{'sessionId':'github-993-1'}),('expired_lease',{'expiresAt':'2026-10-25T12:00:00Z'}),('diagnostic_lease',{'checkpointProfile':'source_probe'})]:
   current=state.read('heads/cloud-lease.json');state.compare_and_swap('cloud-lease',current,{**old,**change});reject(name,lambda:seed.seed_before_collection(R,root,state,session,J,runtime))
  state.compare_and_swap('cloud-lease',state.read('heads/cloud-lease.json'),old)
  wrong=SimpleNamespace(**runtime.__dict__);wrong.REPO=R/'wrong';reject('wrong_runtime_repository',lambda:seed.seed_before_collection(R,root,state,session,J,wrong))
 # Post-preflight acknowledgement adversaries retain a real valid context and importer.
 with patch.dict(os.environ,env,clear=True),patch.object(seed,'validate_seed',return_value=checked):
  def wrong_ack(*args):
   r=ack(*args);r['receipt']['contractSha256']=q4.H;return r
  runtime.checkpoint=wrong_ack;reject('H_checkpoint_receipt_under_J',lambda:seed.seed_before_collection(R,root,state,session,J,runtime))
  def raced_ack(root,store,current,phase,result):
   r=ack(root,store,current,phase,result);lease=store.read('heads/cloud-lease.json');store.compare_and_swap('cloud-lease',lease,{**lease,'releasedAt':NOW});return r
  runtime.checkpoint=raced_ack;reject('lease_released_during_checkpoint',lambda:seed.seed_before_collection(R,root,state,session,J,runtime))
 root,state,session,event,env,runtime,ack=fixture();calls=[0];actual_write=state.write_once
 def interrupted(k,b):
  if calls[0]==10:raise OSError('SYNTHETIC_IMPORT_INTERRUPTION')
  calls[0]+=1;return actual_write(k,b)
 with patch.dict(os.environ,env,clear=True),patch.object(seed,'validate_seed',return_value=checked):
  with patch.object(state,'write_once',side_effect=interrupted):reject('interrupted_fixed_import',lambda:seed.seed_before_collection(R,root,state,session,J,runtime),OSError)
  need(calls[0]==10,'INTERRUPTION_NOT_EXERCISED');done=seed.seed_before_collection(R,root,state,session,J,runtime);need(all((state.root/k).read_bytes()==b for k,b in checked['files'].items()),'PARTIAL_RETRY_BYTES');need(done['coverageCredit'] is False and done['semanticAdmission'] is False,'PARTIAL_CREDIT')
 for path in ['../seed.json','contracts/q4-qualification-seeds/x/../seed.json','heads/latest-run.json']:
  reject('payload_path_'+path,lambda path=path:seed._payload(R,{'path':path,'sha256':'0'*64,'bytes':1}))
 S.assert_unchanged()
 output={'schemaVersion':1,'verdict':'PASS','negativeCases':cases,'negativeCount':len(cases),'interruptedImportSuccessfulRetry':{'partialWrites':10,'finalImmutableFiles':55,'coverageCredit':False},'attribution':'Complete real seed preflight runs first. Context, lease, importer and acknowledgement code then run unchanged; post-preflight negative tests reuse that prevalidated result. Remote acknowledgement is synthetic.','frozenInputSeals':S.touched,'allFrozenInputsUnchanged':True,'reviewerSourceRequests':0,'reviewerModelCalls':0,'reviewerRealArchiveSessionBudgetWrites':0};(O/'lease-edge-review.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({'verdict':'PASS','negativeCases':len(cases),'partialRetry':55}))
