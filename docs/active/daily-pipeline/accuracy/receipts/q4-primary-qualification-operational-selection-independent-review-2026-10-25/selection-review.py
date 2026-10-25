import sys,unittest,socket,json,gzip,hashlib,subprocess
from pathlib import Path
from unittest.mock import patch
R=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022')
sys.path[:0]=[str(R/'web/scripts/pipeline'),str(R/'ops/ci')]
from contracts import digest
from test_q4_press_list import ReadOnlyD660,ARCHIVE
from storage import LocalStore
import q4_primary_qualification as q
A=R/'docs/active/daily-pipeline/accuracy'
D=A/'receipts/q4-primary-qualification-operational-selection-independent-review-2026-10-25';D.mkdir(parents=True,exist_ok=True)
review=json.loads((A/'q4-primary-qualification-independent-review-2026-10-25.json').read_bytes())
oldtest=subprocess.run(['git','-C',str(R),'show','HEAD:ops/ci/test_q4_primary_qualification.py'],check=True,stdout=subprocess.PIPE).stdout
newtest=(R/'ops/ci/test_q4_primary_qualification.py').read_bytes()
assert oldtest.endswith(b'\n\n\n') and newtest==oldtest[:-2]
assert digest(newtest)=='0ae3925c6f9529f2f3654a055f219a30c8141b5286759c341e9394c2ab61ea24'
for name,v in review['reviewedFiles'].items():
 if name!='ops/ci/test_q4_primary_qualification.py':assert digest((R/name).read_bytes())==v['sha256']
for name in ['contracts/market.json','contracts/factual-corrections.json','web/src/data/tracker/factualCorrectionPolicy.json','web/scripts/pipeline/engine.py','web/scripts/pipeline/onboarding.py','web/scripts/pipeline/discovery.py','web/scripts/pipeline/corrections.py','web/scripts/pipeline/q4_controller_capture.py','web/scripts/pipeline/q4_initial_data_capture.py']:
 assert digest((R/name).read_bytes())==review['preservedFiles'][name]['sha256']
active=R/'contracts/source-qualification-probes.json';raw=active.read_bytes();dormant=(A/'q4-primary-qualification-plan-2026-10-25.json').read_bytes()
assert raw==dormant and len(raw)==4211 and digest(raw)=='3a25e8e262b51fbf6f872c8655b25c9d255cf52b32ca0e9c4afa73d78893fbd4' and digest(json.loads(raw))=='3b7fc7c4de41c68471d4343f103e7e5ee705e5a4a51f760f5387e34a49a660ee'
oldactive=subprocess.run(['git','-C',str(R),'show','HEAD:contracts/source-qualification-probes.json'],check=True,stdout=subprocess.PIPE).stdout
assert digest(oldactive)=='ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4'
seals={}
def seal(p):
 b=p.read_bytes();v={'sha256':digest(b),'bytes':len(b),'mtimeNs':p.stat().st_mtime_ns};assert seals.setdefault(str(p),v)==v;return b
s=ReadOnlyD660();orig=s.raw
def rawfile(key):
 p=ARCHIVE/'state'/key
 if p.exists():seal(p)
 return orig(key)
s.raw=rawfile
seal(ARCHIVE/'archive-manifest.json')
for name in set(review['reviewedFiles'])|set(review['preservedFiles']):seal(R/name)
for name in ['q4-primary-qualification-operational-activation-spec-2026-10-25.md','q4-primary-qualification-independent-review-2026-10-25.md','q4-primary-qualification-independent-review-2026-10-25.json']:seal(A/name)
with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')),patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_LOCALSTORE')):
 normalized=q.validate_plan(json.loads((R/'contracts/market.json').read_bytes()),s,raw,active)
 from corrections import _index,group_review_policy,replay_admission
 c=json.loads((R/'contracts/market.json').read_bytes());gs=json.loads((R/'contracts/factual-corrections.json').read_bytes());st=json.loads((R/'web/src/data/tracker/factualCorrectionPolicy.json').read_bytes())
 admissions=[]
 for g in gs['groups']:
  policy=group_review_policy(g,c,gs['baseline']['sha256']);assert policy==st['reviewPolicySha256ByGroup'][g['id']];ref=s.read(_index(g,policy))['admission'];b=s.get(ref);replay_admission(g,ref,s,c,policy,'2026-10-25T12:00:00Z');assert b==s.get(ref);admissions.append({'groupId':g['id'],'policySha256':policy,'admission':ref})
import io
output=io.StringIO()
with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')):
 suite=unittest.defaultTestLoader.loadTestsFromNames(['test_q4_press_list','test_q4_primary_qualification','test_leased_source_probe','test_leased_orca_probe'])
 result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
log=output.getvalue().encode();assert result.wasSuccessful() and not result.skipped
packed=gzip.compress(log,mtime=0);assert gzip.decompress(packed)==log
(D/'focused-tests.log.gz').write_bytes(packed)
for path in list(seals):seal(Path(path))
report={'schemaVersion':1,'verdict':'PASS','openFindings':0,'baseCommit':'5b7e8f50','selection':{'rawSha256':digest(raw),'canonicalSha256':digest(json.loads(raw)),'bytes':len(raw),'byteIdenticalDormant':True,'oldActiveDisabledSha256':digest(oldactive)},'formatOnlyTestDelta':{'oldSha256':digest(oldtest),'newSha256':digest(newtest),'removedBytes':2,'exactChange':'Removed two trailing LF bytes only.','semanticCodeChange':False},'reviewedCodeUnchanged':True,'activeActualProofReplay':{'archiveCommit':'d6606a4f5dd1e1afc5f16dea6d91bc422347f8aa','manifestSha256':digest((ARCHIVE/'archive-manifest.json').read_bytes()),'consumedArchiveInputs':len(s.touched),'inventoryCounts':[len(x['records'])for x in normalized['streams']],'originalWindowCounts':[len(x['currentWindowItems'])for x in normalized['streams']],'asOf':[x['asOf']for x in normalized['streams']]},'sixOriginalAdmissions':admissions,'focusedTests':{'tests':result.testsRun,'failures':0,'skips':0,'modules':['test_q4_press_list','test_q4_primary_qualification','test_leased_source_probe','test_leased_orca_probe'],'rawLogSha256':digest(log),'rawLogBytes':len(log),'gzipSha256':digest(packed),'gzipBytes':len(packed),'byteExactRoundtrip':True},'inputSeals':seals,'inputSealsUnchanged':True,'sourceRequests':0,'modelCalls':0,'budgetMutations':0,'archiveWrites':0,'operationalCredit':False,'scope':'Exact local selection reviewed. No push/remote selection/actual primary execution/publication claimed.'}
out=A/'q4-primary-qualification-operational-selection-independent-review-2026-10-25.json';out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'verdict':'PASS','tests':result.testsRun,'skips':len(result.skipped),'archiveInputs':len(s.touched),'seals':len(seals),'output':str(out),'sha256':digest(out.read_bytes()),'bytes':out.stat().st_size,'gzipSha256':digest(packed)}))
