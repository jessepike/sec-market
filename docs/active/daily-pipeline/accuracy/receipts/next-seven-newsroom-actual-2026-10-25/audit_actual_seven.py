"""Offline actual seven-source audit; all observed bytes come from the acknowledged archive."""
import base64,hashlib,importlib.util,json,socket,subprocess,sys,gzip,io,os
from html.parser import HTMLParser
from collections import Counter
from pathlib import Path
from unittest.mock import patch
REPO=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022')
HOST=Path('/mnt/mac/private/tmp/smp-next-seven-actual-40190857026-20261025')
WORK=Path('/var/tmp/smp-next-seven-actual-40190857026-20261025')
ROOT=WORK/'extracted'
BASE=Path('/var/tmp/smp-scheduled-monitor-acceptance-20261025/scheduled-publisher-40190348786/post-publisher-extracted')
OUT=WORK/'proof'
OUT.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def load(p):return json.loads(Path(p).read_bytes())
def dump(p,j):Path(p).write_text(json.dumps(j,indent=2)+'\n')
def pin(p):
 p=Path(p);b=p.read_bytes();return {'sha256':sha(b),'bytes':len(b),'mtimeNs':p.stat().st_mtime_ns}
spec=importlib.util.spec_from_file_location('oldactual',REPO/'docs/active/daily-pipeline/accuracy/receipts/q4-primary-qualification-actual-2026-10-25/audit_actual.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
entries,manifestpin=helper.manifest(ROOT,'8da12977648ce0f6ed62f16de0b52c2257977f41404145adbecb363069e037e1')
old,basepin=helper.manifest(BASE,'a4cf620a0c8b2f66a8031ecc05c0f7a23be979a9572a41e03eada8b4137d1018')
store=helper.ReadOnlyArchive(ROOT,entries);baseline=helper.ReadOnlyArchive(BASE,old)
run=load(HOST/'run.json');artifact=load(HOST/'artifact.json');receipt=load(HOST/'receipt.json');report=receipt['diagnostic'];ack=load(HOST/'ack-commit.json');tree=load(HOST/'ack-tree.json');reuse=load(WORK/'reuse-proof.json')
need(run['id']==40190857026 and run['run_attempt']==1 and run['status']=='completed' and run['conclusion']=='success' and run['event']=='workflow_dispatch' and run['head_branch']=='main' and run['head_sha']=='bd38e818f4aa7d2bae2169178a02047d252b260c','RUN_IDENTITY')
need(run['repository']['full_name']=='jessepike/sec-market' and run['repository']['private'] and run['repository']['id']==1335546492,'REPOSITORY')
zipraw=(HOST/'artifact.zip').read_bytes();need(len(zipraw)==artifact['size_in_bytes']==14766 and artifact['digest']=='sha256:'+sha(zipraw)=='sha256:887b847b2baceaa0aece585b28197789c433bc59fb400ce4ce6240544ffed369','ARTIFACT_DIGEST')
import zipfile
with zipfile.ZipFile(HOST/'artifact.zip') as z:need(z.namelist()==['smp-collection-receipt.json'] and z.read(z.namelist()[0])==(HOST/'receipt.json').read_bytes(),'ARTIFACT_CONTENT')
need(artifact['id']==12598281472 and artifact['name']=='source-probe-receipt' and artifact['expired'] is False and artifact['workflow_run']['id']==run['id'] and artifact['workflow_run']['head_sha']==run['head_sha'],'ARTIFACT_IDENTITY')
need(ack['sha']==receipt['archive']['commit']=='9deb0c9ce9fe34999da0cf13bb023dfdfecc15c8' and ack['tree']['sha']==tree['sha'],'ACK')
mr=[r for r in tree['tree'] if r['path']=='archive-manifest.json'];raw=(ROOT/'archive-manifest.json').read_bytes();need(len(mr)==1 and mr[0]['size']==len(raw) and mr[0]['sha']==hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'MANIFEST_GIT_BLOB')
need(len(entries)==receipt['archive']['files']==48245 and len(old)==48060 and set(old)<=set(entries),'MANIFEST_INVENTORY')
reused=[];delta=[]
for k,r in entries.items():
 p=ROOT/k;need(not p.is_symlink() and p.resolve().is_relative_to(ROOT),'PATH')
 if old.get(k)==r:
  st=p.stat();bt=(BASE/k).stat();x={'inode':st.st_ino,'device':st.st_dev,'mtimeNs':st.st_mtime_ns,'bytes':st.st_size};need(x==reuse['reused'][k] and st.st_ino==bt.st_ino and st.st_dev==bt.st_dev and st.st_mtime_ns==bt.st_mtime_ns and st.st_size==bt.st_size==r['bytes'],'BASELINE_REUSE');reused.append(k)
 else:
  b=p.read_bytes();need(sha(b)==r['sha256'] and len(b)==r['bytes'],'DELTA_HASH')
  if k.startswith('state/objects/'):need(Path(k).name==sha(b),'CONTENT_ADDRESS')
  delta.append(k)
need({str(p.relative_to(ROOT)) for p in (ROOT/'state').rglob('*') if p.is_file()}==set(entries),'EXTRA_MISSING_FILES')
baselineproof=Path('/var/tmp/smp-scheduled-monitor-acceptance-20261025/scheduled-publisher-40190348786/publisher-audit.json');bp=pin(baselineproof);need(bp['sha256']=='be869399f30fc42d411b4545d35655d158d19d7a32e2cec53a047e5813c73708' and load(baselineproof)['authenticatedState']['allManifestEntriesVerified'] is True,'BASELINE_FULL_PROOF')
sys.path[:0]=[str(REPO/'web/scripts/pipeline'),str(REPO/'ops/ci')]
import onboarding
from contracts import canonical,digest,instant,ContractError
from storage import LocalStore
from corrections import _index,group_review_policy,replay_admission
from discovery import IndexMarkup,Page,decoded_discovery_body
policy=load(REPO/'contracts/market.json');need(digest(policy)==receipt['contractSha256']==report['contractSha256']=='8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db','H')
codepins={}
for rel in ['web/scripts/pipeline/onboarding.py','web/scripts/pipeline/discovery.py','web/scripts/pipeline/fetcher.py','web/scripts/pipeline/corrections.py','ops/ci/collect.py','contracts/market.json','contracts/factual-corrections.json','web/src/data/tracker/factualCorrectionPolicy.json']:
 p=REPO/rel
 if not p.exists():continue
 b=p.read_bytes();committed=subprocess.run(['git','-C',str(REPO),'show',run['head_sha']+':'+rel],check=True,stdout=subprocess.PIPE).stdout;need(b==committed,'APP_CODE_DIFFERS:'+rel);codepins[rel]=pin(p)
for k,v in {'githubRunId':str(run['id']),'githubRunAttempt':1,'githubEventName':'workflow_dispatch','githubRef':'refs/heads/main','appRevision':run['head_sha'],'checkpointProfile':'source_probe','executionCompleted':True,'outcome':'completed_diagnostic','modelCalls':0,'apiFallback':False,'semanticAdmission':False,'coverageCredit':False,'sourceChecksCredited':0,'qualifiedSources':0}.items():need(receipt[k]==v,'OUTER:'+k)
need('facts' not in receipt and report['facts']==[] and receipt['publication']=={'published':False,'reason':'SOURCE_PROBE_DIAGNOSTIC_ONLY'},'LEGACY_OUTER_FIELDS')
need(store.read('ci/source-probe-runs/40190857026-1.json')=={k:v for k,v in receipt.items() if k!='archive'},'ARCHIVED_RECORD')
planraw=store.get(report['qualification']['plan']['rawPlanReference']);need(len(planraw)==4162 and sha(planraw)==digest(json.loads(planraw))=='3077d93ede8a9fe82302a6b851af61d8666f1c11cea433eed0f2725086c85fc2','PLAN')
planpath=WORK/'actual-plan.json';planpath.write_bytes(planraw)
class ReplayStore:
 def get(self,ref):return store.get(ref)
 def read(self,k):return store.read(k)
 def put(self,b):
  b=b if isinstance(b,bytes) else canonical(b);ref={'key':'objects/'+digest(b),'sha256':digest(b),'bytes':len(b)};need(store.get(ref)==b,'REPLAY_PUT_NOT_RETAINED');return ref
 def write_once(self,k,b):
  b=b if isinstance(b,bytes) else canonical(b);need(store.raw(k)==b,'REPLAY_RESULT_DIFFERS:'+k)
class SequentialPool:
 def __init__(self,**kw):pass
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def map(self,fn,items):return [fn(x) for x in items]
rows=report['sources'];explicit=report['qualification']['targets'];clock_index=[0];current=[None];ri=[0];oi=[0];ei=[0]
budget=object.__new__(onboarding.PersistentProbeBudget)
def clock():
 i=clock_index[0];clock_index[0]+=1
 if i<len(rows):current[0]=rows[i];ri[0]=oi[0]=0;return rows[i]['checkedAt']
 need(i==len(rows),'EXTRA_CLOCK');return report['checkedAt']
def reserve():
 if clock_index[0]<=len(rows) and ri[0]<len(current[0]['fetchReservations']):
  r=current[0]['fetchReservations'][ri[0]];ri[0]+=1;return {k:v for k,v in r.items() if k!='url'}
 r=explicit[ei[0]];ei[0]+=1;return r['reservation']
budget.clock=clock;budget.reserve_fetch=reserve;budget.before_fetch=lambda:None;budget.assert_bound=lambda s,c:need(s.__class__ is ReplayStore and c==policy,'REPLAY_BINDING');budget.summary=lambda:report['reservationContext']
class FrozenFetcher:
 def fetch(self,source,url):
  if ei[0]:
   row=explicit[ei[0]-1];need(source['id']==row['sourceId'] and url==row['url'],'EXPLICIT_FETCH_BINDING');return json.loads(store.get(row['observation']))
  row=current[0];need(source['id']==row['sourceId'] and url==row['fetchReservations'][oi[0]]['url'],'GENERIC_FETCH_BINDING')
  if oi[0]>=len(row['observations']):
   need(row['reason']=='ContractError' and row['sourceId']=='sysdig:official:1','UNEXPECTED_MISSING_OBSERVATION');raise ContractError('RETAINED_UNKNOWN_TRANSPORT_NO_HTTP_INFERENCE')
  ref=row['observations'][oi[0]];oi[0]+=1;o=json.loads(store.get(ref));need(o['requestedUrl']==url,'OBSERVATION_REQUEST_JOIN');return o
with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')),patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_LOCALSTORE')),patch.object(onboarding,'ThreadPoolExecutor',SequentialPool):
 normalized=onboarding.validate_qualification_probe_plan(policy,store,planpath)
 replay=onboarding.probe_sources(policy,ReplayStore(),FrozenFetcher(),reservation_context=budget,qualification_plan_path=planpath)
 replay['qualification']['plan']['path']=report['qualification']['plan']['path']
 need(replay==report,'FULL_LEGACY_CLASSIFICATION_REPLAY_DIFFERS')
 admissions=[];requests=load(REPO/'contracts/factual-corrections.json');stamp=load(REPO/'web/src/data/tracker/factualCorrectionPolicy.json')
 for group in requests['groups']:
  h=group_review_policy(group,policy,requests['baseline']['sha256']);need(stamp['reviewPolicySha256ByGroup'][group['id']]==h,'REVIEW_POLICY');ref=store.read(_index(group,h))['admission'];need(ref==baseline.read(_index(group,h))['admission'],'ADMISSION_REF_CHANGED');replay_admission(group,ref,store,policy,h,report['checkedAt']);admissions.append({'groupId':group['id'],'reviewPolicySha256':h,'admission':ref})
day=report['reservationContext']['budgetDay'];bk='heads/budget-'+day+'.json';before=baseline.read(bk);after=store.read(bk);need(before=={'calls':80,'documents':38,'fetches':869} and after=={'calls':80,'documents':38,'fetches':985},'BUDGET');need(report['reservationContext']['initialBudget']==before and report['reservationContext']['currentBudget']==after,'REPORT_BUDGET')
reservations=[{**r,'sourceId':s['sourceId'],'type':'generic'} for s in rows for r in s['fetchReservations']]+[{**t['reservation'],'sourceId':t['sourceId'],'url':t['url'],'type':'explicit'} for t in explicit]
need(len(reservations)==116 and sorted(r['chargedFetchCount'] for r in reservations)==list(range(870,986)) and all(r['budgetDay']==day and r['fetchLimit']==5500 for r in reservations),'CHARGES')
changed=[k for k in old if entries.get(k)!=old[k]];added=[k for k in entries if k not in old];need(set(changed)=={'state/'+bk,'state/heads/cloud-lease.json'} and not any(k.startswith('state/heads/') for k in added),'PRESERVATION')
snapshot=store.read('heads/dailySnapshot.json');need(snapshot==baseline.read('heads/dailySnapshot.json') and len(snapshot['factProvenance'])==4 and len(snapshot['reviewQueue'])==38,'FACTS_HOLDS_CLOCKS')
for ref in snapshot['factProvenance'].values():store.get(ref)
gate=store.read('heads/gate-budget-'+day+'.json');need(gate==baseline.read('heads/gate-budget-'+day+'.json'),'GATE')
lease=store.read('heads/cloud-lease.json');need(lease['sessionId']=='github-40190857026-1' and lease['checkpointProfile']=='source_probe' and isinstance(lease.get('releasedAt'),str),'LEASE')
escrow=store.read('ci/budget-escrows/'+digest(lease['sessionId'])+'.json');need(escrow['before']==before and escrow['ceiling']=={'calls':80,'documents':38,'fetches':5500},'ESCROW')
boot=load(HOST/'bootstrap-commit.json');ec=load(HOST/'escrow-commit.json');need(boot['parents'][0]['sha']=='496ad86ade09969edab9d79d96f24bbab0a8e3e0' and ec['parents'][0]['sha']==boot['sha'] and ack['parents'][0]['sha']==ec['sha']==receipt['archive']['parentCommit'],'ACK_CHAIN')
eb=load(HOST/'escrow-budget.json');ebraw=base64.b64decode(eb['content']);need(json.loads(ebraw)==escrow['ceiling'] and hashlib.sha1(b'blob '+str(len(ebraw)).encode()+b'\0'+ebraw).hexdigest()==eb['sha'] and eb['html_url']=='https://github.com/jessepike/sec-market/blob/'+ec['sha']+'/state/'+bk,'ESCROW_REMOTE')
need(instant(run['run_started_at'])<=instant(report['reservationContext']['startedAt'])<=instant(report['checkedAt'])<=instant(run['updated_at']),'RUN_CLOCKS')
allobs=[]
for s in rows:
 for idx,r in enumerate(s['fetchReservations']):
  o=json.loads(store.get(s['observations'][idx])) if idx<len(s['observations']) else None
  if o:
   need(o['requestedUrl']==r['url'] and instant(report['reservationContext']['startedAt'])<=instant(o['fetchedAt'])<=instant(report['checkedAt']),'OBS_CLOCK_JOIN')
   if o.get('body'):store.get(o['body'])
  allobs.append({'sourceId':s['sourceId'],'reservation':r,'observation':o,'unknownReason':None if o else s['reason']})
class LiteralAttributes(HTMLParser):
 def __init__(self,text):
  super().__init__(convert_charrefs=True);self.rows=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  for key,value in attrs:
   if key in ('href','src','action'):self.rows.append({'tag':tag,'attribute':key,'value':value,'line':self.getpos()[0],'column':self.getpos()[1]})
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
explicitrows=[]
for t in explicit:
 o=json.loads(store.get(t['observation']));b=store.get(o['body']);need(o['status']=='fetched' and o['httpStatus']==200 and o['requestedUrl']==o['finalUrl']==t['url'] and o['contentType'].lower().startswith('text/html'),'EXPLICIT_TRANSPORT');need(instant(report['reservationContext']['startedAt'])<=instant(o['fetchedAt'])<=instant(report['checkedAt']),'EXPLICIT_CLOCK')
 compressed=io.BytesIO()
 with gzip.GzipFile(filename='',fileobj=compressed,mode='wb',mtime=0) as f:f.write(b)
 packed=compressed.getvalue();need(gzip.decompress(packed)==b,'BODY_ROUNDTRIP');(OUT/(t['targetId']+'-body.html.gz')).write_bytes(packed)
 text=b.decode('utf8');page=Page(text,source_url=t['url']);nodes=list(IndexMarkup(text).root.walk());anchors=[{'href':n.attrs.get('href'),'text':' '.join(n.text.split())[:300]} for n in nodes if n.tag=='a' and n.attrs.get('href')];dates=[{'tag':n.tag,'datetime':n.attrs.get('datetime'),'text':' '.join(n.text.split())[:160]} for n in nodes if n.tag=='time'];scripturls=[n.attrs.get('src') for n in nodes if n.tag=='script' and n.attrs.get('src')];heads=[' '.join(n.text.split()) for n in nodes if n.tag in ('h1','h2')]
 explicitrows.append({'target':t,'actualObservation':o,'bodyPath':str(ROOT/'state'/o['body']['key']),'bodyGzip':{'file':t['targetId']+'-body.html.gz','sha256':sha(packed),'bytes':len(packed),'rawSha256':sha(b),'rawBytes':len(b),'byteExactRoundTrip':True},'heads':heads,'anchors':anchors,'timeElements':dates,'indexMarkupScriptUrls':scripturls,'literalHtmlAttributes':LiteralAttributes(text).rows,'inspectionLimit':'Static literal attribute and text inventory only; no script execution, active-DOM or terminal-completeness claim. Existing IndexMarkup can omit links outside its recognized tree.','qualificationCredit':False})
dump(OUT/'cold-index-inspection.json',explicitrows)
store.unchanged();baseline.unchanged();need(pin(ROOT/'archive-manifest.json')==manifestpin and pin(BASE/'archive-manifest.json')==basepin,'MANIFEST_CHANGED')
for rel,v in codepins.items():need(pin(REPO/rel)==v,'CODE_CHANGED_DURING_AUDIT')
proof={'schemaVersion':1,'verdict':'PASS','actualRunId':run['id'],'appRevision':run['head_sha'],'event':run['event'],'conclusion':run['conclusion'],'artifact':{'id':artifact['id'],'sha256':sha(zipraw),'bytes':len(zipraw)},'acknowledgedArchive':receipt['archive'],'manifest':manifestpin,'manifestGitBlobSha1':mr[0]['sha'],'allEntriesVerified':len(entries),'baselineCommit':reuse['baselineCommit'],'baselineManifest':basepin,'baselineFullAudit':{'path':str(baselineproof),**bp},'previouslyAuthenticatedReusedEntries':len(reused),'newOrChangedEntriesHashVerified':len(delta),'changedBaselineEntries':changed,'addedEntryKeys':added,'immutableBaselineEntriesPreserved':sum(not k.startswith('state/heads/') for k in old),'normalHeadsPreserved':sum(k.startswith('state/heads/') and k not in changed for k in old),'fullLegacyTraversalReplay':{'passed':True,'productionLogicUnmodified':True,'adapters':'read-only write validation, frozen actual fetch observations/reservations/clocks, sequential scheduling; sole output path relocated back before exact comparison','networkDenied':True,'LocalStoreConstructionDenied':True},'actualReservations':reservations,'genericObservationResults':allobs,'genericSourceCount':len(rows),'genericReservations':109,'explicitReservations':7,'totalReservations':116,'wholeOperationReservationUpperBound':257,'explicitReached':7,'explicitUnreached':0,'explicitActualResults':[{k:v for k,v in r.items() if k not in ('anchors','literalHtmlAttributes','indexMarkupScriptUrls','heads','timeElements')} for r in explicitrows],'startingBudget':before,'finalBudget':after,'gateBudget':gate,'lease':lease,'escrow':escrow,'admissions':admissions,'facts':len(snapshot['factProvenance']),'holdRows':len(snapshot['reviewQueue']),'sourceExpiry':snapshot['coverage']['validUntil'],'inputSeals':store.touched,'baselineInputSeals':baseline.touched,'codePins':codepins,'inputSealsUnchanged':True,'credit':{'qualifiedSources':0,'sourceChecksCredited':0,'coverageCredit':False,'semanticAdmission':False,'factsAdded':0,'modelCalls':0,'published':False},'reviewerSourceRequests':0,'reviewerModelRequests':0,'reviewerArchiveWrites':0,'executedJavaScript':False}
dump(OUT/'actual-diagnostic-audit.json',proof)
print(json.dumps({'PASS':True,'allEntries':len(entries),'reused':len(reused),'deltaHashVerified':len(delta),'legacyTraversalReplay':True,'admissions':len(admissions),'facts':4,'holds':38,'fetches':after['fetches'],'allSevenHTTP200':True,'consultedArchiveInputs':len(store.touched)}))
