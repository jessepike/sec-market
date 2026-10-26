import base64,concurrent.futures,gzip,hashlib,json,socket,sys,urllib.request
from pathlib import Path
from urllib.parse import quote
from unittest.mock import patch
B=Path('/var/tmp/smp-oct26-publish-40266519925');C=B/'capture';D=B/'gate-failure';R=C/'extracted/state';OLD=Path('/var/tmp/smp-oct26-ordinary-40263678287/capture/extracted/state');APP=Path('/var/tmp/smp-oct26-ordinary-40263678287/application');OUT=B/'failure-verification';OUT.mkdir(exist_ok=False)
sys.path[:0]=[str(APP/'web/scripts/pipeline'),str(APP/'ops/ci')]
from contracts import canonical,digest,require,utcnow
from artifacts import unpack,inventory
from corrections import load_policy,replay_admission,project_bundle
from snapshot import collector_continuity
from storage import LocalStore
J=lambda p:json.loads(p.read_bytes())
def save(n,b):(OUT/n).write_bytes(b);return b
def read(k):p=R/k;return J(p) if p.exists() else None
def get(ref):
 b=(R/ref['key']).read_bytes();require(len(b)==ref['bytes'] and digest(b)==ref['sha256'],'Actual archive reference differs');return b
class RO:
 root=R
 def _path(self,key):return R/key
 def read(self,key):return read(key)
 def get(self,ref):return get(ref)
 def put(self,value):
  b=value if isinstance(value,bytes) else canonical(value);ref={'key':'objects/'+digest(b),'sha256':digest(b),'bytes':len(b)};require(get(ref)==b,'Verifier attempted nonretained object');return ref
 def write_once(self,*a,**k):raise AssertionError('Frozen write prohibited')
 def compare_and_swap(self,*a,**k):raise AssertionError('Frozen head write prohibited')
s=RO();proof=J(C/'authenticated-publisher-archive.json');receipt=J(C/'publisher-receipt.json');run=J(C/'publisher-run.json');gateRun=J(D/'gate-run.json');art=J(D/'gate-artifacts.json')['artifacts'];require(len(art)==1 and art[0]['name']=='daily-gate-diagnostics','Actual diagnostic artifact differs')
require(art[0]['digest']=='sha256:'+digest((D/'diagnostics.zip').read_bytes()),'Actual diagnostic transport differs')
require(run['conclusion']=='failure' and gateRun['conclusion']=='failure' and run['head_sha']==gateRun['head_sha']=='3bb9e40c8f6324aa4f419fbe13022ec4dcaece55','Actual failed main identity differs')
require(receipt=={'published':False,'reason':'PUBLISHER_FAILED','errorType':'ContractError'},'Actual publisher failure differs')
logs={name:(D/name).read_bytes() for name in ['certify-sec.log','refresh-edgar.log','refresh-filing-events.log','test.log']};lines=logs['test.log'].decode().splitlines();failure=next(i for i,x in enumerate(lines) if x.startswith('not ok 141 -'))
require('J baseline preserves full H history and all dates while granting zero credit' in lines[failure] and any('Q4 baseline projection changed historical facts, dates, obligations or zero-credit state' in x for x in lines[failure:failure+20]),'Exact failing counterexample differs')
testSummary={}
for line in lines:
 for name in ['tests','pass','fail','cancelled','skipped','todo']:
  if line.startswith('# '+name+' '):testSummary[name]=int(line.split()[-1])
require(testSummary=={'tests':379,'pass':378,'fail':1,'cancelled':0,'skipped':0,'todo':0},'Actual failed test tally differs')
cert=[json.loads(x) for x in logs['certify-sec.log'].decode().splitlines() if x.startswith('{')][-1];require(cert['proofs']==80 and cert['failed']==0 and cert['suppliers']==16,'Actual80 SEC certification result differs')
market=J(APP/'contracts/market.json');latest=read('heads/latest-run.json');coverage=json.loads(get(latest['receipt']));collector=read('heads/dailySnapshot.json');require(collector==J(OLD/'heads/dailySnapshot.json') and latest==J(OLD/'heads/latest-run.json'),'Failed publisher changed actual collection')
head=read('heads/production.json');require(head==J(OLD/'heads/production.json') and head['sequence']==4 and head['releaseId']=='fc8bf0984dbeacbe79519574911837d8b638f42215f6547e31ae8968b29951e4','Failed gate changed production')
record=read('releases/'+head['releaseId']+'.json');manifest=record['manifest'];ack=record['acknowledgement'];files=unpack(get(manifest['artifact']['archive']));require(digest(inventory(files))==manifest['artifact']['sha256'],'Old accepted static artifact differs')
oldBundle=json.loads(files['static/factual-corrections.json']);require(len(oldBundle['groups'])==6,'Actual public six history rows differ')
outcomeHead=read('heads/correction-collection.json');outcome=json.loads(get(outcomeHead['outcome']));require(len(outcome['admitted'])==8 and not outcome['pending'] and outcomeHead==J(OLD/'heads/correction-collection.json'),'Private actual all8 admission outcome changed')
reviews=[]
with patch.object(socket,'socket',side_effect=AssertionError('Audit source/model network prohibited')),patch.object(LocalStore,'__init__',side_effect=AssertionError('Writable frozen store prohibited')):
 continuity=collector_continuity(collector,market,coverage,s);context=load_policy(APP,market)
 for group in context['requests']['groups']:
  entry=next(v for v in outcome['admitted'] if v['groupId']==group['id']);ad=replay_admission(group,entry['admission'],s,market,context['reviewPolicySha256ByGroup'][group['id']],collector['checkedAt']);reviews.append({'groupId':group['id'],'admission':entry['admission'],'admittedAt':ad['admittedAt'],'reviewRef':ad['review']})
 projection=project_bundle(APP,s,market,outcome,previous_bundle=oldBundle,publication_at=collector['checkedAt']);require(projection['groups'][:6]==oldBundle['groups'],'Oldsix history changed')
source=read('heads/budget-2026-10-26.json');gate=read('heads/gate-budget-2026-10-26.json');pubBudget=read('heads/publication-budget-2026-10-26.json');lease=read('heads/cloud-lease.json');require(source=={'calls':76,'documents':37,'fetches':444} and gate=={'attempts':1} and pubBudget is None,'Actual failure charges differ')
require(lease['sessionId']=='github-publisher-40266519925-1' and lease['releasedAt']=='2026-10-26T04:07:01.428398Z','Actual failed writer lease differs')
for k in ('budget','gate-budget','publication-budget'):require(read('heads/'+k+'-2026-10-25.json')==J(OLD/('heads/'+k+'-2026-10-25.json')),'October25 charged history changed')
files['static/deployment-receipt.json']=canonical(ack);hosts=[head['deploymentId'],'https://securitymarketpulse.com'];requests=[(host,name,body) for host in hosts for name,body in sorted(files.items()) if name.startswith('static/')]
def check(entry):
 host,name,body=entry;url=host+'/'+quote(name.removeprefix('static/'),safe='/');req=urllib.request.Request(url,headers={'Cache-Control':'no-cache','Accept-Encoding':'identity'})
 with urllib.request.urlopen(req,timeout=40) as response:
  actual=response.read(len(body)+1);require(response.status==200 and response.url==url and actual==body,'Actual unchanged public bytes/HTTP/URL differ: '+url)
  return {'host':host,'path':'/'+name.removeprefix('static/'),'sha256':digest(actual),'bytes':len(actual),'httpStatus':200}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:comparisons=list(pool.map(check,requests))
for name in ['app-release.json','deployment-receipt.json','daily-coverage.json','factual-corrections.json']:
 body=files['static/'+name];save('public-'+name+('.gz' if name=='daily-coverage.json' else ''),gzip.compress(body,mtime=0) if name=='daily-coverage.json' else body)
app=json.loads(files['static/app-release.json']);publicCoverage=json.loads(files['static/daily-coverage.json']);require(app['appRevision']=='6d5e87feba4ffbc75e50f35cb564cb8fd91708ca' and publicCoverage['successfulTasks']==264 and publicCoverage['requiredTasks']==557 and publicCoverage['validUntil']=='2026-10-26T12:45:29.479727+00:00','Accepted old public state differs')
ready=J(B/'old-public-vercel-ready.json');require(ready['readyState']=='READY' and ready['url']==head['deploymentId'].removeprefix('https://'),'Actual retained public deployment not READY')
for key,size,sha,mtime,ino,dev in J(C/'authenticated-file-identities.json'):
 p=C/'extracted'/key;st=p.stat();require((st.st_size,st.st_mtime_ns,st.st_ino,st.st_dev)==(size,mtime,ino,dev) and digest(p.read_bytes())==sha,'Frozen publisher audit input changed')
summary={'checkedAt':utcnow(),'verdict':'ACTUAL_GATE_FAILED_NO_NEW_PUBLICATION','actualPublisherRunId':40266519925,'actualGateRunId':40266928448,'exactMainRevision':run['head_sha'],'publisherReceipt':receipt,'gateFailure':{'code':'RELEASE_GATE_FAILED_test','diagnosticArtifactId':art[0]['id'],'diagnosticArtifactDigest':art[0]['digest'],'executedDataTests':testSummary,'failedTest':'J baseline preserves full H history and all dates while granting zero credit','testPath':'web/tests/q4-baseline-migration.test.mjs:32','reason':'Q4 baseline projection changed historical facts, dates, obligations or zero-credit state','callSite':'web/scripts/pipeline/daily_q4_baseline_migration.mjs:78','fixtureCause':'Historical test reads mutable web/src/data/generated/dailyMarket.json; actual gate replaces that file with the fresh ordinary snapshot before npm test. Frozen migration verifier correctly rejects the live snapshot as a historical zero-credit fixture.','passedCertification':cert,'artifactLogSha256':{n:digest(b) for n,b in logs.items()},'noAcceptedGateArtifactOrStaticBuild':True},'authenticatedArchive':proof['observedArchive'],'authenticatedEntries':proof['manifestEntries'],'allManifestEntriesVerified':True,'baselineArchiveCommit':proof['baselineArchiveCommit'],'baselineIsAncestor':True,'changedMutableHeads':proof['changedMutableHeads'],'addedEntries':proof['addedEntries'],'sourceStateExact':True,'privateCollection':{'runId':coverage['runId'],'successfulTasks':265,'requiredTasks':557,'processing':coverage['processing'],'historicalReview':coverage['historicalReview'],'sourceExpiry':collector['coverage']['validUntil'],'queue':44,'all8Admitted':True,'pendingGroups':[],'actualAdmissionReviewReferences':reviews,'correctionPolicySha256':context['policySha256'],'all38OldHoldRowsAccountedForAs37QueuedPlus1VerifiedResolution':True},'allowances':{'settledSource':source,'gateAttempts':gate,'remainingGateSlotsUnderUnchanged2Limit':1,'publicationBudget':pubBudget,'noResetOrRefund':True},'lease':lease,'actualProduction':{'head':head,'appRevision':app['appRevision'],'snapshotSha256':app['dailySnapshotSha256'],'publicExpiry':publicCoverage['validUntil'],'intake':{'checked':264,'required':557},'sixPublicCorrectionRowsExact':True,'newCorrectionsPublic':False,'actualDeployment':ready},'publicStaticProof':{'artifactStaticFiles':len(comparisons)//2-1,'filesWithDetachedReceipt':len(comparisons)//2,'hosts':2,'requests':len(comparisons),'allBytesExact':True},'frozenPublisherInputsUnchanged':True,'verifier':{'sourceOrModelRequests':0,'stateMutations':0,'dispatches':0,'reservations':0,'commits':0,'pushes':0,'publicStaticGets':len(comparisons)}}
save('static-file-comparison.json',canonical({'checkedAt':summary['checkedAt'],'allBytesExact':True,'files':comparisons}));save('release-record.json',canonical(record));save('actual-failure-summary.json',canonical(summary))
# Save a small, selected failure excerpt only. Full job logs remain private VM scratch.
excerpt='\n'.join(lines[max(0,failure-2):failure+20]+lines[-9:])+'\n';require(not any(w in excerpt.lower() for w in ['token','secret','password','authorization','cookie','credential','bearer']),'Unsafe failure excerpt');save('test-failure-excerpt.txt',excerpt.encode())
print(json.dumps({k:summary[k] for k in ['verdict','authenticatedArchive','authenticatedEntries','allowances','lease','actualProduction','publicStaticProof']},indent=2))
