import json,sys,socket,unittest,io,gzip,copy,tempfile,importlib.util
from pathlib import Path
from unittest.mock import patch
R=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022')
sys.path[:0]=[str(R/'web/scripts/pipeline'),str(R/'ops/ci')]
from contracts import digest,plan_run
from storage import LocalStore
from onboarding import validate_qualification_probe_plan
A=R/'docs/active/daily-pipeline/accuracy'
D=A/'receipts/next-seven-newsroom-operational-selection-independent-review-2026-10-25'
D.mkdir(parents=True,exist_ok=True)
active=R/'contracts/source-qualification-probes.json';dormant=A/'next-seven-newsroom-review-plan-2026-10-25.json';raw=active.read_bytes()
assert raw==dormant.read_bytes() and len(raw)==4162 and digest(raw)=='3077d93ede8a9fe82302a6b851af61d8666f1c11cea433eed0f2725086c85fc2'
assert digest(json.loads(raw))==digest(raw)
spec=importlib.util.spec_from_file_location('actual_primary_audit',A/'receipts/q4-primary-qualification-actual-2026-10-25/audit_actual.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
root=Path('/var/tmp/smp-q4-primary-actual-40188161705-20261025/extracted')
entries,manifest=m.manifest(root,'bb1c3da1399e89341badf80bba8642d7892f32ce2030bd57fc1d4c165e383e4d')
store=m.ReadOnlyArchive(root,entries)
policyraw=(R/'contracts/market.json').read_bytes();assert digest(policyraw)=='24221c946781559c0ff3626e4e479c4647da915d0f2d7559ea88046982532c3c'
c=json.loads(policyraw);assert digest(c)=='8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db'
seals={}
def seal(p):
 b=p.read_bytes();v={'sha256':digest(b),'bytes':len(b),'mtimeNs':p.stat().st_mtime_ns};assert seals.setdefault(str(p),v)==v
 return b
for n in ['contracts/market.json','contracts/source-qualification-probes.json','contracts/factual-corrections.json','web/src/data/tracker/factualCorrectionPolicy.json','web/scripts/pipeline/onboarding.py','ops/ci/collect.py','web/scripts/pipeline/engine.py','web/scripts/pipeline/fetcher.py','web/scripts/pipeline/discovery.py','web/scripts/pipeline/source_qualification_origin.py','ops/ci/html_qualification_seed.py','ops/ci/test_source_qualification_probe.py','ops/ci/test_leased_source_probe.py','ops/ci/test_disabled_qualification_plan.py','ops/ci/test_onboarding_budget.py','docs/active/daily-pipeline/accuracy/next-seven-newsroom-review-plan-2026-10-25.json','docs/active/daily-pipeline/accuracy/next-seven-newsroom-operational-activation-spec-2026-10-25.md']:seal(R/n)
seal(root/'archive-manifest.json')
mutations=[]
base=json.loads(raw)
for key in base:
 p=copy.deepcopy(base);del p[key];mutations.append(p)
for value in [True,7.0,6,8,0]:
 p=copy.deepcopy(base);p['maxRequests']=value;mutations.append(p)
for field,value in [('expectedFormat','javascript'),('url',base['targets'][0]['url']+'#other'),('sourceId','nonexistent:official:1')]:
 p=copy.deepcopy(base);p['targets'][0][field]=value;mutations.append(p)
for field,value in [('fetchedAt','2026-10-25T11:20:10Z'),('type','unknown')]:
 p=copy.deepcopy(base);p['targets'][0]['proof'][field]=value;mutations.append(p)
p=copy.deepcopy(base);p['targets'][0]['proof']['extra']=1;mutations.append(p)
with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')),patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_LOCALSTORE')):
 checked=validate_qualification_probe_plan(c,store,active)
 assert checked['rawSha256']==checked['canonicalSha256']==digest(raw)and len(checked['targets'])==7
 with tempfile.TemporaryDirectory()as folder:
  path=Path(folder)/'invalid.json'
  for p in mutations:
   path.write_text(json.dumps(p))
   try:validate_qualification_probe_plan(c,store,path)
   except (ValueError,KeyError,TypeError):pass
   else:raise AssertionError('INVALID_MUTATION_PASSED')
 from corrections import _index,group_review_policy,replay_admission
 groups=json.loads((R/'contracts/factual-corrections.json').read_bytes());stamp=json.loads((R/'web/src/data/tracker/factualCorrectionPolicy.json').read_bytes())
 admissions=[]
 for g in groups['groups']:
  h=group_review_policy(g,c,groups['baseline']['sha256']);assert h==stamp['reviewPolicySha256ByGroup'][g['id']]
  ref=store.read(_index(g,h))['admission'];before=store.get(ref);replay_admission(g,ref,store,c,h,'2026-10-25T12:00:00Z');assert before==store.get(ref);admissions.append({'groupId':g['id'],'policySha256':h,'admission':ref})
 snapshot=store.read('heads/dailySnapshot.json');budget=store.read('heads/budget-2026-10-25.json');gate=store.read('heads/gate-budget-2026-10-25.json')
 assert len(snapshot['factProvenance'])==4 and len(snapshot['reviewQueue'])==38 and budget=={'calls':80,'documents':38,'fetches':869}and gate=={'attempts':2}
 for ref in snapshot['factProvenance'].values():store.get(ref)
candidates=[s for s in c['sources']if s['registration']=='candidate']
assert len(candidates)==25 and not any(s['kind']in('sec_index','sec_documents')for s in candidates)
whole=len(candidates)*(1+1+8)+checked['maxRequests'];assert whole==257
required=sum(t['required']for t in plan_run(c,'2026-10-25T00:00:00Z')['tasks']);assert required==557
output=io.StringIO()
with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')):
 suite=unittest.defaultTestLoader.loadTestsFromNames(['test_source_qualification_probe','test_leased_source_probe','test_disabled_qualification_plan','test_onboarding_budget'])
 result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
log=output.getvalue().encode();assert result.wasSuccessful()and not result.skipped
z=gzip.compress(log,mtime=0);assert gzip.decompress(z)==log;(D/'focused-tests.log.gz').write_bytes(z)
store.unchanged()
for path in list(seals):seal(Path(path))
r={'schemaVersion':1,'verdict':'PASS','openFindings':0,'selection':{'schemaVersion':1,'rawSha256':digest(raw),'canonicalSha256':digest(json.loads(raw)),'bytes':len(raw),'byteIdenticalDormant':True,'explicitTargets':[{k:t[k]for k in ['id','sourceId','url','expectedFormat','proof']}|{'literalRecognition':t['literalRecognition']}for t in checked['targets']]},'actualArchive':{'commit':'d2efafcb8a68d7330e4b700613b29f18b9892346','manifest':manifest,'entries':len(entries),'proofSource':'Previously complete authenticated actual primary archive, consumed through read/get-only adapter.'},'market':{'rawSha256':digest(policyraw),'canonicalSha256':digest(c),'unchanged':True,'requiredObligations':required},'wholeOperationBound':{'genericCandidateSources':25,'candidateSecPairs':0,'perGenericSourceMaximum':{'root':1,'robots':1,'disclosedEndpoints':8,'total':10},'genericMaximumLogicalFetches':250,'explicitTargetsMaximum':7,'wholeMaximumLogicalFetches':whole,'physicalWireAttemptsNotClaimed':True,'constraintsAndEarlyStops':['actual-day fetch allowance','1200-second operation deadline','UTC rollover','cancellation','per-source transport failure','robots and allowed-host checks','final in-flight guard'],'sourcePointers':['onboarding.py:1554,1570,1575,1586,1616','onboarding.py:582','ops/ci/collect.py:263,272,288']},'originalProofTimesPreserved':[t['proof']['fetchedAt']for t in checked['targets']],'sixOriginalAdmissions':admissions,'preservedState':{'budget':budget,'gates':gate,'factReferences':4,'holdRows':38,'privateSourceValidUntil':snapshot['coverage']['validUntil'],'normalHeadWrites':0},'focusedTests':{'modules':['test_source_qualification_probe','test_leased_source_probe','test_disabled_qualification_plan','test_onboarding_budget'],'tests':result.testsRun,'failures':0,'skips':0,'rawLogSha256':digest(log),'rawLogBytes':len(log),'gzipSha256':digest(z),'gzipBytes':len(z),'byteExactRoundtrip':True,'actualPlanAdversarialMutationsRejected':len(mutations)},'consultedArchiveSeals':store.touched,'consultedRepositoryAndManifestSeals':seals,'allSealsUnchanged':True,'sourceRequests':0,'modelCalls':0,'actualBudgetMutations':0,'actualArchiveWrites':0,'qualificationCredit':False,'coverageCredit':False,'semanticAdmission':False,'facts':[],'scope':'Exact local selection and future diagnostic route only; no actual dispatch or remote selection claimed.'}
out=A/'next-seven-newsroom-operational-selection-independent-review-2026-10-25.json';out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'output':str(out),'sha256':digest(out.read_bytes()),'bytes':out.stat().st_size,'focusedTests':r['focusedTests'],'archiveSeals':len(store.touched),'otherSeals':len(seals)}))
