"""Build only dormant plans and replay unchanged validation against frozen9deb; no source requests."""
from pathlib import Path
from unittest.mock import patch
import copy,hashlib,importlib.util,json,socket,sys
REPO=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022')
ROOT=Path('/var/tmp/smp-next-seven-actual-40190857026-20261025/extracted')
OUT=Path('/var/tmp/smp-next-qualification-design-20261025');OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(REPO/'web/scripts/pipeline'))
from contracts import digest,canonical
from storage import LocalStore
from onboarding import validate_qualification_probe_plan,_candidate_primary_shape
spec=importlib.util.spec_from_file_location('actual_adapter',REPO/'docs/active/daily-pipeline/accuracy/receipts/q4-primary-qualification-actual-2026-10-25/audit_actual.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
entries,manifestseal=a.manifest(ROOT,'8da12977648ce0f6ed62f16de0b52c2257977f41404145adbecb363069e037e1');store=a.ReadOnlyArchive(ROOT,entries)
key='ci/source-probe-runs/40190857026-1.json';record=store.read(key);ref={**entries['state/'+key],'key':key};q=record['diagnostic']['qualification'];old=q['targets'];policy=json.loads((REPO/'contracts/market.json').read_bytes())
def target(index,id,url):
 row=old[index];o=json.loads(store.get(row['observation']));return {'id':id,'sourceId':row['sourceId'],'url':url,'expectedFormat':'html','proof':{'type':'qualification_observation','record':ref,'observation':row['observation'],'body':o['body'],'fetchedAt':o['fetchedAt'],'priorTargetId':row['targetId'],'priorTargetIndex':index,'priorTargetSha256':digest(row),'priorPlanRawSha256':q['plan']['rawSha256'],'priorPlanCanonicalSha256':q['plan']['canonicalSha256'],'priorPlanReference':q['plan']['rawPlanReference']}}
targets=[target(0,'abnormal-press-list','https://abnormal.ai/newsroom/press-releases'),target(1,'cyera-press-list','https://www.cyera.com/newsroom/press-releases')]+[target(5,'cato-page-'+str(i),'https://www.prnewswire.com/news/cato-networks/?page='+str(i)+'&pagesize=25') for i in range(2,6)]+[target(6,'chainguard-page-2','https://www.prnewswire.com/news/chainguard/?page=2&pagesize=25')]
plan={'schemaVersion':1,'marketSha256':digest(policy),'maxRequests':7,'targets':targets};planpath=OUT/'recommended-next-seven.json';planpath.write_bytes(canonical(plan));results={};negative=[]
with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')),patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_LOCALSTORE')):
 for name,items in [('recommended',targets),('veracode_alternative',[target(3,'veracode-press-list','https://www.veracode.com/newsroom/press-release/')]+targets[1:])]:
  p=OUT/(name+'-validation-plan.json');v={**plan,'targets':items};p.write_bytes(canonical(v));checked=validate_qualification_probe_plan(policy,store,p);results[name]={'rawSha256':digest(p.read_bytes()),'canonicalSha256':checked['canonicalSha256'],'bytes':len(p.read_bytes()),'literalRecognitionByTarget':[(t['id'],t['literalRecognition']) for t in checked['targets']]}
 mutations=[]
 def change(name,fn):
  v=copy.deepcopy(plan);fn(v);mutations.append((name,v))
 change('top_extra',lambda v:v.update(unreviewed=True));change('six_targets',lambda v:v['targets'].pop());change('max6',lambda v:v.update(maxRequests=6));change('target_extra',lambda v:v['targets'][0].update(method='GET'));change('duplicate_id',lambda v:v['targets'][1].update(id=v['targets'][0]['id']));change('duplicate_url',lambda v:v['targets'][1].update(url=v['targets'][0]['url']));change('proof_extra',lambda v:v['targets'][0]['proof'].update(refresh=True));change('date_rebase',lambda v:v['targets'][0]['proof'].update(fetchedAt='2026-10-25T12:00:00Z'));change('prior_row_index',lambda v:v['targets'][0]['proof'].update(priorTargetIndex=1));change('prior_row_hash',lambda v:v['targets'][0]['proof'].update(priorTargetSha256='0'*64));change('prior_plan_hash',lambda v:v['targets'][0]['proof'].update(priorPlanRawSha256='0'*64));change('record_hash',lambda v:v['targets'][0]['proof']['record'].update(sha256='0'*64));change('body_bytes',lambda v:v['targets'][0]['proof']['body'].update(bytes=1));change('observation_hash',lambda v:v['targets'][0]['proof']['observation'].update(sha256='0'*64));change('undisclosed_page6',lambda v:v['targets'][2].update(url='https://www.prnewswire.com/news/cato-networks/?page=6&pagesize=25'));change('changed_page_size',lambda v:v['targets'][2].update(url='https://www.prnewswire.com/news/cato-networks/?page=2&pagesize=50'));change('fragment',lambda v:v['targets'][0].update(url=v['targets'][0]['url']+'#press'));change('http',lambda v:v['targets'][0].update(url=v['targets'][0]['url'].replace('https:','http:')));change('www_alias',lambda v:v['targets'][0].update(url='https://www.abnormal.ai/newsroom/press-releases'));change('source_crossbind',lambda v:v['targets'][0].update(sourceId='cyera:official:1'))
 script=target(2,'torq-disclosed-controller','https://torq.io/wp-content/themes/elxr/js/loadmore.js?ver=1.8.58');mutations.append(('script_attribute_not_supported_by_existing_Page',{**plan,'targets':[script]+targets[1:]}))
 for name,v in mutations:
  p=OUT/'negative-plan.json';p.write_bytes(canonical(v))
  try:validate_qualification_probe_plan(policy,store,p)
  except (ValueError,KeyError,TypeError) as e:negative.append({'case':name,'rejected':True,'reason':str(e)})
  else:raise AssertionError('MUTATION_ACCEPTED:'+name)
 shapes=json.loads((OUT/'retained-primary-shapes.json').read_bytes());shape_results=[]
 for item in shapes['results']:
  k=item['recordKey'].removeprefix('state/');o=store.read(k);shape=_candidate_primary_shape(store.get(o['body']),o['requestedUrl']);assert shape==item['existingPrimaryShape'] and o['status']=='fetched' and o['httpStatus']==200 and o['finalUrl']==o['requestedUrl'];shape_results.append({'recordKey':k,'sourceId':o['sourceId'],'fetchedAt':o['fetchedAt'],'body':o['body'],'shape':shape})
 chain=[];o=store.read('observations/e093d30012f13f5403bd5d9e3f14bc5421ecc3a1714352fd7a2b3e44224580b2.json');seen=set()
 while True:
  assert o['observationId'] not in seen;seen.add(o['observationId']);chain.append(o);store.get(o['body'])
  if o['status']=='fetched':assert o['httpStatus']==200;break
  assert o['status']=='not_modified' and o['httpStatus']==304 and o['reusesObservationId'];prior=store.read('observations/'+o['reusesObservationId']+'.json');assert prior['body']==o['body'] and prior['sourceId']==o['sourceId'] and prior['requestedUrl']==o['requestedUrl'] and prior['fetchedAt']<=o['fetchedAt'];o=prior
store.unchanged();assert a.pin(ROOT/'archive-manifest.json')==manifestseal
report={'schemaVersion':1,'verdict':'PASS','actualParentRunId':40190857026,'archiveCommit':'9deb0c9ce9fe34999da0cf13bb023dfdfecc15c8','manifest':manifestseal,'plans':results,'negativeCases':negative,'negativeCount':len(negative),'normalSourceCredit':0,'socketDenied':True,'LocalStoreInitializationDenied':True,'archiveInputSeals':store.touched,'allSealsUnchanged':True,'retainedPrimaryShapes':shape_results,'cyeraActual304ReuseChain':chain,'newSourceRequests':0,'newModelCalls':0,'sharedArchiveWrites':0,'runtimeWrites':0,'operationChanges':0}
(OUT/'preflight-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'PASS':True,'recommended':results['recommended'],'negativeCases':len(negative),'retainedPrimaryShapes':len(shape_results),'cyeraReuseChainLength':len(chain),'inputSeals':len(store.touched)}))
