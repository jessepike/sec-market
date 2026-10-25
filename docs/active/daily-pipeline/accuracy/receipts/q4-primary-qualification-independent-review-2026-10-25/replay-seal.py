import json,sys,socket
from pathlib import Path
from unittest.mock import patch
R=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022')
sys.path[:0]=[str(R/'web/scripts/pipeline'),str(R/'ops/ci')]
from contracts import digest
from test_q4_press_list import ReadOnlyD660,ARCHIVE
from storage import LocalStore
import q4_primary_qualification as q
from corrections import _index,group_review_policy,replay_admission
OUT=Path('/var/tmp/smp-q4-primary-independent-seals-20261025.json')
seals={}
def seal(p):
 b=p.read_bytes();x={'sha256':digest(b),'bytes':len(b),'mtimeNs':p.stat().st_mtime_ns};assert seals.setdefault(str(p),x)==x;return b
manifest=seal(ARCHIVE/'archive-manifest.json')
s=ReadOnlyD660();orig=s.raw
def bound(key):
 p=ARCHIVE/'state'/key
 if p.exists():seal(p)
 return orig(key)
s.raw=bound
files=['web/scripts/pipeline/q4_press_list.py','web/scripts/pipeline/q4_primary_qualification.py','ops/ci/collect.py','ops/ci/test_q4_press_list.py','ops/ci/test_q4_primary_qualification.py','docs/active/daily-pipeline/accuracy/q4-primary-qualification-plan-2026-10-25.json']
preserve=['contracts/market.json','contracts/source-qualification-probes.json','contracts/factual-corrections.json','web/src/data/tracker/factualCorrectionPolicy.json','web/scripts/pipeline/engine.py','web/scripts/pipeline/onboarding.py','web/scripts/pipeline/discovery.py','web/scripts/pipeline/corrections.py','web/scripts/pipeline/q4_controller_capture.py','web/scripts/pipeline/q4_initial_data_capture.py','web/scripts/pipeline/html_qualification_origin.py','.github/workflows/collect.yml']
preserve += ['docs/active/daily-pipeline/accuracy/q4-single-response-qualification-build-spec-2026-10-25.md','docs/active/daily-pipeline/accuracy/q4-primary-qualification-operational-activation-spec-2026-10-25.md']
for p in files+preserve:
 if (R/p).exists():seal(R/p)
seal(R/q.INSPECTION['path'])
c=json.loads((R/'contracts/market.json').read_bytes());raw=(R/'docs/active/daily-pipeline/accuracy/q4-primary-qualification-plan-2026-10-25.json').read_bytes()
admissions=[]
with patch.object(socket.socket,'connect',side_effect=AssertionError('socket denied')),patch.object(LocalStore,'__init__',side_effect=AssertionError('frozen constructor denied')):
 normalized=q.validate_plan(c,s,raw)
 gs=json.loads((R/'contracts/factual-corrections.json').read_bytes());st=json.loads((R/'web/src/data/tracker/factualCorrectionPolicy.json').read_bytes())
 for g in gs['groups']:
  policy=group_review_policy(g,c,gs['baseline']['sha256']);assert policy==st['reviewPolicySha256ByGroup'][g['id']]
  ref=s.read(_index(g,policy))['admission'];before=s.get(ref)
  replay_admission(g,ref,s,c,policy,'2026-10-25T12:00:00Z');assert s.get(ref)==before
  admissions.append({'groupId':g['id'],'reviewPolicySha256':policy,'admission':ref,'rawSha256':digest(before)})
for path,before in list(seals.items()):seal(Path(path))
result={'schemaVersion':1,'scope':'independent-offline-replay-only','archive':{'commit':'d6606a4f5dd1e1afc5f16dea6d91bc422347f8aa','manifestSha256':digest(manifest),'manifestBytes':len(manifest)},'reviewedFiles':{p:seals[str(R/p)]for p in files},'preservedFiles':{p:seals[str(R/p)]for p in preserve if str(R/p)in seals},'allConsultedFileSeals':seals,'archiveConsumedInputs':len(s.touched),'archiveConsumedInputsPreserved':True,'inventoryCounts':[len(x['records'])for x in normalized['streams']],'originalWindowCounts':[len(x['currentWindowItems'])for x in normalized['streams']],'sixOriginalAdmissions':admissions,'networkRequests':0,'LocalStoreConstructedOnFrozenArchive':False,'operationalPlanEnabled':False,'semanticAdmission':False,'qualificationCredit':0}
OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'output':str(OUT),'sha256':digest(OUT.read_bytes()),'bytes':OUT.stat().st_size,'seals':len(seals),'archiveInputs':len(s.touched)}))
