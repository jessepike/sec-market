from pathlib import Path, PurePosixPath
from unittest.mock import patch
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit
import copy,hashlib,json,socket,sys,subprocess,zipfile,io
R=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022')
A=Path('/var/tmp/smp-next-seven-actual-40190857026-20261025/extracted')
P=Path('/var/tmp/smp-next-seven-actual-40190857026-20261025/handback/receipts')
O=Path('/var/tmp/smp-narrow-pagination-independent-20261025')
sys.path.insert(0,str(R/'web/scripts/pipeline'))
import onboarding as m
from contracts import canonical,digest,ContractError,instant
from storage import LocalStore
from discovery import decoded_discovery_body

def require(v,msg):
 if not v:raise AssertionError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def seal(p):
 b=p.read_bytes();return {'sha256':sha(b),'bytes':len(b),'mtimeNs':p.stat().st_mtime_ns}
seals={}
def read(p):
 p=Path(p);s=seal(p);require(seals.setdefault(str(p),s)==s,'CHANGED_INPUT:'+str(p));return p.read_bytes()
def js(p):return json.loads(read(p))
manifest=js(A/'archive-manifest.json');require(sha((A/'archive-manifest.json').read_bytes())=='8da12977648ce0f6ed62f16de0b52c2257977f41404145adbecb363069e037e1','MANIFEST_PIN')
entries={x['key']:x for x in manifest['files']};require(len(entries)==len(manifest['files'])==48245,'ENTRY_INVENTORY')
# Hash every retained byte independently, and seal every consulted archive entry.
allstat={};totalbytes=0
for k,v in entries.items():
 p=A/k;require(not p.is_symlink() and p.resolve().is_relative_to(A),'PATH_ESCAPE');b=p.read_bytes();require(len(b)==v['bytes'] and sha(b)==v['sha256'],'FULL_MANIFEST:'+k)
 if k.startswith('state/objects/'):require(p.name==sha(b),'OBJECT_ADDRESS')
 st=p.stat();allstat[k]={'bytes':st.st_size,'mtimeNs':st.st_mtime_ns,'inode':st.st_ino,'device':st.st_dev};totalbytes+=len(b)
require({str(p.relative_to(A)) for p in (A/'state').rglob('*') if p.is_file()}==set(entries),'UNMANIFESTED_OR_MISSING')
class Store:
 def raw(self,k):
  require(isinstance(k,str) and '..' not in PurePosixPath(k).parts and not k.startswith('/'),'BAD_KEY')
  row=entries.get('state/'+k)
  if row is None:require(not (A/'state'/k).exists(),'UNMANIFESTED');return None
  b=read(A/'state'/k);require(sha(b)==row['sha256'] and len(b)==row['bytes'],'BAD_BYTES');return b
 def read(self,k):
  b=self.raw(k);return json.loads(b) if b is not None else None
 def get(self,ref):
  b=self.raw(ref['key']);require(b is not None and sha(b)==ref['sha256'] and len(b)==ref['bytes'],'BAD_REFERENCE');return b
 def put(self,*args):raise AssertionError('STORE_PUT_FORBIDDEN')
 def write(self,*args):raise AssertionError('STORE_WRITE_FORBIDDEN')
 def write_once(self,*args):raise AssertionError('STORE_WRITE_ONCE_FORBIDDEN')
s=Store();policy=js(R/'contracts/market.json');require(digest(policy)=='8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db','POLICY_H')
preflight=js(R/'docs/active/daily-pipeline/accuracy/narrow-listing-pagination-preflight-review-2026-10-25.json')
for rel,pin in preflight['codePins'].items():require(seal(R/rel)['sha256']==pin['sha256'] and seal(R/rel)['bytes']==pin['bytes'],'CURRENT_CODE_PIN:'+rel);read(R/rel)
for rel in ['web/scripts/pipeline/fetcher.py','web/scripts/pipeline/html_index.py','web/scripts/pipeline/budget.py']:
 if (R/rel).exists():read(R/rel)
for rel in ['narrow-listing-pagination-build-spec-2026-10-25.md','narrow-listing-pagination-preflight-review-2026-10-25.md']:
 read(R/'docs/active/daily-pipeline/accuracy'/rel)
planpath=R/'docs/active/daily-pipeline/accuracy/narrow-listing-pagination-plan-2026-10-25.json';planraw=read(planpath);plan=json.loads(planraw)
require(len(planraw)==8977 and sha(planraw)==digest(plan)=='ac7393c6fc28d97826916462b0b56ca5fcd7a27521bb838de8df19542b494711','PLAN_PIN')
run=js(P/'run.json');artifact=js(P/'artifact.json');receipt=js(P/'receipt.json');ack=js(P/'ack-commit.json');tree=js(P/'ack-tree.json')
require(run['id']==40190857026 and run['event']=='workflow_dispatch' and run['head_branch']=='main' and run['head_sha']=='bd38e818f4aa7d2bae2169178a02047d252b260c' and run['conclusion']=='success','ACTUAL_RUN')
require(run['repository']['full_name']=='jessepike/sec-market' and run['repository']['id']==1335546492 and run['repository']['private'],'REPOSITORY')
zraw=read(P/'source-probe-artifact.zip');require('sha256:'+sha(zraw)==artifact['digest'] and len(zraw)==artifact['size_in_bytes'] and artifact['workflow_run']['id']==run['id'],'ARTIFACT')
with zipfile.ZipFile(io.BytesIO(zraw)) as z:require(z.namelist()==['smp-collection-receipt.json'] and z.read(z.namelist()[0])==read(P/'receipt.json'),'ARTIFACT_CONTENT')
require(ack['sha']==receipt['archive']['commit']=='9deb0c9ce9fe34999da0cf13bb023dfdfecc15c8' and ack['tree']['sha']==tree['sha'],'ACK_TREE')
mb=read(A/'archive-manifest.json');blob=hashlib.sha1(b'blob '+str(len(mb)).encode()+b'\0'+mb).hexdigest();mr=[r for r in tree['tree'] if r['path']=='archive-manifest.json'];require(len(mr)==1 and mr[0]['sha']==blob and mr[0]['size']==len(mb),'ACK_MANIFEST_BLOB')
key='ci/source-probe-runs/40190857026-1.json';record=s.read(key);require(record=={k:v for k,v in receipt.items() if k!='archive'},'ARCHIVED_RECEIPT')
report=record['diagnostic'];q=report['qualification'];priorraw=s.get(q['plan']['rawPlanReference']);prior=json.loads(priorraw)
require(sha(priorraw)==digest(prior)=='3077d93ede8a9fe82302a6b851af61d8666f1c11cea433eed0f2725086c85fc2' and len(priorraw)==4162,'PRIOR_PLAN')
oldpath=O/'original-retained-plan.json';oldpath.write_bytes(priorraw)
rows=report['sources'];explicit=q['targets'];context=report['reservationContext'];require(len(rows)==25 and len(explicit)==7,'ACTUAL_ROWS')
reservations=[r for row in rows for r in row['fetchReservations']]+[row['reservation'] for row in explicit]
require(context['initialBudget']=={'fetches':869,'calls':80,'documents':38} and context['currentBudget']=={'fetches':985,'calls':80,'documents':38},'LEDGERS')
require(len(reservations)==context['probeFetchReservations']==116 and sorted(x['chargedFetchCount'] for x in reservations)==list(range(870,986)),'CHARGED_COMPLETE')
require(sum(len(row['fetchReservations']) for row in rows)==109,'ACTUAL_GENERIC_COST')
# The production traversal runs unchanged with fully retained observation, charge and clock fixtures.
class ReplayStore:
 def read(self,k):return s.read(k)
 def get(self,ref):return s.get(ref)
 def put(self,value):
  raw=value if isinstance(value,bytes) else canonical(value);ref={'key':'objects/'+sha(raw),'sha256':sha(raw),'bytes':len(raw)};require(s.get(ref)==raw,'UNRETAINED_REPLAY_PUT');return ref
 def write_once(self,k,value):require(s.raw(k)==(value if isinstance(value,bytes) else canonical(value)),'REPLAY_OUTPUT_DIFFERS')
class Pool:
 def __init__(self,**kw):pass
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def map(self,fn,items):return [fn(x) for x in items]
ci=0;current=None;ri=0;oi=0;ei=0
budget=object.__new__(m.PersistentProbeBudget)
def clock():
 global ci,current,ri,oi
 i=ci;ci+=1
 if i<len(rows):current=rows[i];ri=oi=0;return current['checkedAt']
 require(i==len(rows),'EXTRA_CLOCK');return report['checkedAt']
def reserve():
 global ri,ei
 if ci<=len(rows) and ri<len(current['fetchReservations']):
  row=current['fetchReservations'][ri];ri+=1;return {k:v for k,v in row.items() if k!='url'}
 row=explicit[ei];ei+=1;return row['reservation']
class Fetcher:
 def fetch(self,source,url):
  global oi
  if ei:
   row=explicit[ei-1];require(source['id']==row['sourceId'] and url==row['url'],'EXPLICIT_FETCH_JOIN');return json.loads(s.get(row['observation']))
  require(source['id']==current['sourceId'] and url==current['fetchReservations'][oi]['url'],'GENERIC_FETCH_JOIN')
  if oi>=len(current['observations']):
   require(current['reason']=='ContractError' and current['sourceId']=='sysdig:official:1','UNEXPECTED_MISSING');raise ContractError('RETAINED_UNKNOWN_TRANSPORT_NO_HTTP_INFERENCE')
  ref=current['observations'][oi];oi+=1;observed=json.loads(s.get(ref));require(observed['requestedUrl']==url,'OBSERVATION_JOIN');return observed
budget.clock=clock;budget.reserve_fetch=reserve;budget.before_fetch=lambda:None;budget.assert_bound=lambda store,c:require(type(store) is ReplayStore and c==policy,'BAD_BINDING');budget.summary=lambda:context
# Mutated records are only held in memory with correct recalculated refs so semantic checks must execute.
class Overlay:
 def __init__(self,raws):self.raws=raws
 def get(self,ref):
  raw=self.raws.get(ref['key'])
  if raw is None:return s.get(ref)
  require(sha(raw)==ref['sha256'] and len(raw)==ref['bytes'],'OVERLAY_REF');return raw
 def read(self,k):return json.loads(self.raws[k]) if k in self.raws else s.read(k)
 def put(self,*args):raise AssertionError('OVERLAY_WRITE_DENIED')
 def write_once(self,*args):raise AssertionError('OVERLAY_WRITE_DENIED')
def mutated_record(fn):
 rec=copy.deepcopy(record);fn(rec);raw=canonical(rec);p=copy.deepcopy(plan);ref={'key':key,'sha256':sha(raw),'bytes':len(raw)}
 for t in p['targets']:t['proof']['record']=ref
 return p,Overlay({key:raw})
def refreshed_row(rec,index):
 # Update hash only when the test needs to pass the row digest guard to reach deeper checks.
 return digest(rec['diagnostic']['qualification']['targets'][index])
negatives=[];positives=[]
for module in list(sys.modules.values()):
 filename=getattr(module,'__file__',None)
 if filename and Path(filename).is_file() and Path(filename).is_relative_to(R):read(Path(filename))
with patch.object(socket.socket,'connect',side_effect=AssertionError('SOCKET_DENIED')),patch.object(socket.socket,'connect_ex',side_effect=AssertionError('SOCKET_DENIED')),patch.object(socket,'create_connection',side_effect=AssertionError('SOCKET_DENIED')),patch.object(LocalStore,'__init__',side_effect=AssertionError('FROZEN_LOCALSTORE_DENIED')),patch.object(subprocess,'run',side_effect=AssertionError('SUBPROCESS_DENIED')),patch.object(m,'ThreadPoolExecutor',Pool):
 for check in [lambda:socket.create_connection(('invalid',443)),lambda:LocalStore(A)]:
  try:check()
  except AssertionError:pass
  else:raise AssertionError('DENIAL_GUARD_NOT_ACTIVE')
 normalized=m.validate_qualification_probe_plan(policy,s,planpath);require(normalized['rawSha256']==sha(planraw),'CURRENT_PLAN_REPLAY')
 m.validate_qualification_probe_plan(policy,s,oldpath)
 replay=m.probe_sources(policy,ReplayStore(),Fetcher(),reservation_context=budget,qualification_plan_path=oldpath);replay['qualification']['plan']['path']=q['plan']['path'];require(replay==report,'WHOLE_PRIOR_REPORT_REPLAY')
 positives.append({'case':'exact_recommended_seven','passed':True,'catoSameSourcePages':4})
 reordered=copy.deepcopy(plan);reordered['targets'][2],reordered['targets'][3]=reordered['targets'][3],reordered['targets'][2];tmp=O/'legal-new-order.json';tmp.write_bytes(canonical(reordered));m.validate_qualification_probe_plan(policy,s,tmp);positives.append({'case':'legal_new_target_reorder','passed':True,'why':'New plan order is not a closed binding; the original retained row order is.'})
 def reject(name,p,store=s):
  f=O/'case-plan.json';f.write_bytes(canonical(p))
  try:m.validate_qualification_probe_plan(policy,store,f)
  except (ValueError,KeyError,TypeError) as e:negatives.append({'case':name,'rejected':True,'reason':str(e)})
  else:raise AssertionError('MUTATION_ACCEPTED:'+name)
 def pm(name,fn):
  p=copy.deepcopy(plan);fn(p);reject(name,p)
 pm('unknown_top_field',lambda p:p.update(operation='unreviewed'))
 pm('boolean_schema',lambda p:p.update(schemaVersion=True))
 pm('wrong_policy',lambda p:p.update(marketSha256='0'*64))
 pm('six_targets',lambda p:p['targets'].pop())
 pm('unknown_target_field',lambda p:p['targets'][0].update(method='GET'))
 pm('duplicate_id_with_legal_host',lambda p:p['targets'][3].update(id=p['targets'][2]['id']))
 pm('duplicate_url_same_legal_source',lambda p:p['targets'][3].update(url=p['targets'][2]['url']))
 pm('unknown_proof_field',lambda p:p['targets'][0]['proof'].update(renew=True))
 pm('prior_index_swap',lambda p:p['targets'][0]['proof'].update(priorTargetIndex=1))
 pm('prior_row_digest',lambda p:p['targets'][0]['proof'].update(priorTargetSha256='0'*64))
 pm('prior_raw_plan_digest',lambda p:p['targets'][0]['proof'].update(priorPlanRawSha256='0'*64))
 pm('prior_canonical_plan_digest',lambda p:p['targets'][0]['proof'].update(priorPlanCanonicalSha256='0'*64))
 pm('proof_body_size',lambda p:p['targets'][0]['proof']['body'].update(bytes=1))
 pm('proof_fetched_time',lambda p:p['targets'][0]['proof'].update(fetchedAt='2026-10-25T12:00:00Z'))
 pm('cato_page6_undisclosed',lambda p:p['targets'][2].update(url='https://www.prnewswire.com/news/cato-networks/?page=6&pagesize=25'))
 pm('cato_changed_page_size',lambda p:p['targets'][2].update(url='https://www.prnewswire.com/news/cato-networks/?page=2&pagesize=50'))
 pm('abnormal_www_alias',lambda p:p['targets'][0].update(url='https://www.abnormal.ai/newsroom/press-releases'))
 pm('same_host_wrong_issuer_proof',lambda p:p['targets'][2].update(sourceId='chainguard:official:1'))
 for name,fn in [
  ('original_rows_reordered',lambda r:r['diagnostic']['qualification']['targets'].reverse()),
  ('original_validated_rows_reordered',lambda r:r['diagnostic']['qualification']['plan']['targets'].reverse()),
  ('parent_semantic_credit',lambda r:r.update(semanticAdmission=True)),
  ('parent_event_schedule_substitution',lambda r:r.update(githubEventName='schedule')),
  ('parent_run_identity',lambda r:r.update(githubRunId='40190857025')),
  ('original_other_row_model_credit',lambda r:r['diagnostic']['qualification']['targets'][4].update(modelCalls=1)),
  ('parent_facts_added',lambda r:r['diagnostic'].update(facts=[{'id':'fake'}])),
  ('prior_plan_inline_substitution',lambda r:r['diagnostic']['qualification']['plan']['plan']['targets'][0].update(url='https://abnormal.ai/other')),
  ('reservation_duplicate_charge',lambda r:r['diagnostic']['sources'][0]['fetchReservations'][0].update(chargedFetchCount=r['diagnostic']['sources'][1]['fetchReservations'][0]['chargedFetchCount'])),
  ('reservation_missing',lambda r:r['diagnostic']['sources'][0]['fetchReservations'].pop()),
  ('reservation_cross_day',lambda r:r['diagnostic']['sources'][0]['fetchReservations'][0].update(budgetDay='2026-10-24')),
  ('reservation_limit_changed',lambda r:r['diagnostic']['sources'][0]['fetchReservations'][0].update(fetchLimit=6000)),
  ('parent_model_counter_changed',lambda r:r['diagnostic']['reservationContext']['currentBudget'].update(calls=81)),
  ('parent_document_counter_changed',lambda r:r['diagnostic']['reservationContext']['currentBudget'].update(documents=39)),
  ('parent_runtime_unbounded',lambda r:r['diagnostic']['reservationContext'].update(maximumRuntimeSeconds=1201)),
  ('parent_original_source_supplier_crossjoin',lambda r:next(x for x in r['diagnostic']['sources'] if x['sourceId']=='abnormal-security:official:1').update(supplierId='cyera')),
 ]:
  p,overlay=mutated_record(fn);reject(name,p,overlay)
# Literal disclosure independent of the production parser, and actual source authority.
class Anchors(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.rows=[]
 def handle_starttag(self,tag,attrs):
  for attr,val in attrs:
   if tag in ('a','link') and attr=='href' and val:self.rows.append({'tag':tag,'href':val,'literalTag':self.get_starttag_text()})
literals=[]
for t in plan['targets']:
 proof=t['proof'];row=explicit[proof['priorTargetIndex']];require(digest(row)==proof['priorTargetSha256'] and row['targetId']==proof['priorTargetId'],'ROW_BINDING')
 observed=json.loads(s.get(proof['observation']));require(observed['status']=='fetched' and observed['httpStatus']==200 and observed['fetchedAt']==proof['fetchedAt'] and observed['body']==proof['body'] and observed['requestedUrl']==observed['finalUrl']==row['url'],'FULL_200_JOIN')
 raw=decoded_discovery_body(s.get(proof['body']));parser=Anchors();parser.feed(raw.decode('utf8'));matches=[x for x in parser.rows if urljoin(observed['finalUrl'],x['href'])==t['url']];require(matches,'LITERAL_ANCHOR_MISSING')
 source=next(x for x in policy['sources'] if x['id']==t['sourceId']);require(urlsplit(t['url']).hostname in source['allowedHosts'] and source['registration']=='candidate','SOURCE_AUTHORITY')
 literals.append({'id':t['id'],'sourceId':t['sourceId'],'url':t['url'],'allowedHosts':source['allowedHosts'],'priorTargetId':row['targetId'],'priorTargetIndex':proof['priorTargetIndex'],'priorTargetSha256':digest(row),'originalRequestedUrl':observed['requestedUrl'],'fetchedAt':observed['fetchedAt'],'observation':proof['observation'],'body':proof['body'],'literalAnchor':matches[0]})
candidates=[x for x in policy['sources'] if x['registration']=='candidate'];require(len(candidates)==25 and not any(x['kind']=='sec_index' for x in candidates),'CANDIDATE_COUNT_OR_SEC_PAIR');require(25*(1+1+8)+7==257,'BOUND')
read(O/'review.py')
for p,v in seals.items():require(seal(Path(p))==v,'FINAL_SEAL_CHANGED:'+p)
for k,v in allstat.items():
 st=(A/k).stat();require({'bytes':st.st_size,'mtimeNs':st.st_mtime_ns,'inode':st.st_ino,'device':st.st_dev}==v,'FULL_ARCHIVE_STAT_CHANGED:'+k)
identitypath=O/'authenticated-archive-file-identities.json'
identitypath.write_text(json.dumps({'archiveRoot':str(A),'acknowledgedCommit':ack['sha'],'manifestSha256':sha(mb),'files':allstat},sort_keys=True,separators=(',',':'))+'\n')
proof={'schemaVersion':1,'verdict':'PASS','scope':'Independent offline acceptance of the exact dormant schema-1 seven-target plan. No operational selection or execution.','reviewedPlan':{'path':str(planpath),'sha256':sha(planraw),'canonicalSha256':digest(plan),'bytes':len(planraw),'fullObject':plan},'authenticatedArchive':{'commit':ack['sha'],'manifestSha256':sha(mb),'manifestBytes':len(mb),'manifestGitBlobSha1':blob,'allEntriesIndependentlyHashVerified':len(entries),'totalManifestBytes':totalbytes,'allArchiveStatsUnchanged':True,'reuseIdentityReceipt':{'path':str(identitypath),**seal(identitypath)}},'actualParent':{'runId':run['id'],'event':run['event'],'appRevision':run['head_sha'],'artifactSha256':sha(zraw),'priorPlanRawSha256':sha(priorraw),'priorPlanCanonicalSha256':digest(prior),'priorPlanBytes':len(priorraw),'fullProductionTraversalReplayExact':True,'originalGenericSources':25,'originalGenericReservations':109,'originalExplicitReservations':7,'originalTotalReservations':116,'initialBudget':context['initialBudget'],'currentBudget':context['currentBudget']},'positives':positives,'negativeCases':negatives,'negativeCount':len(negatives),'literalDisclosuresAndAuthority':literals,'wholeOperationLogicalFetchBound':257,'boundDerivation':'25 existing candidate probes × (root + robots + at most 8 discovery endpoints), plus 7 explicit targets. No candidate SEC pairs. Physical transport retries are governed separately.','limits':['A new returned page may expose a later continuation. Capturing the pages currently disclosed by the retained first page does not establish terminal completeness.','The latest actual 109 generic requests are an observation, not a bound for the proposed future execution.','Torq and Zenity controller gaps remain unresolved and outside this selected listing operation.','An actual lease, current ledger, real day, cancellation and runtime checks remain necessary before future execution.','No qualification, semantic admission, fact, review, history, coverage, freshness, scheduled-run or publication credit.'], 'guards':{'socketDenied':True,'socketGuardSelfTestPassed':True,'frozenLocalStoreConstructionDenied':True,'localStoreGuardSelfTestPassed':True,'subprocessDeniedDuringReplay':True,'archiveWriteMethodsDenied':True,'replayPutAndWriteOnceOnlyCompareRetainedBytes':True},'inputSealsBeforeAfter':seals,'allConsultedInputSealsUnchanged':True,'reviewerSourceRequests':0,'reviewerModelCalls':0,'reviewerArchiveWrites':0,'reviewerBudgetWrites':0,'reviewerRepoWrites':0}
(O/'review.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'verdict':'PASS','negativeCases':len(negatives),'positives':len(positives),'fullEntriesVerified':len(entries),'consultedSeals':len(seals),'wholeOperationBound':257,'report':str(O/'review.json')}))
