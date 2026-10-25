"""Offline exact original graph, proposal and admission replay; no frozen writes."""
from pathlib import Path
import json,sys,socket
from unittest.mock import patch
REPO=Path(__file__).resolve().parents[6]
sys.path[:0]=[str(REPO/'web/scripts/pipeline'),str(REPO/'ops/ci')]
from test_prnewswire_press_list import ReadOnlyActual,AS_OF,ARCHIVE
from test_prnewswire_retained_window import replay_complete
from contracts import digest
from corrections import _index,group_review_policy,replay_admission
from storage import LocalStore
import prnewswire_retained_window as proof
OUT=Path(__file__).parent
accuracy=REPO/'docs/active/daily-pipeline/accuracy'
raw=(accuracy/'prnewswire-retained-window-descriptor-2026-10-25.json').read_bytes()
descriptor=json.loads(raw)
def pin(path):
 path=Path(path);data=path.read_bytes()
 return {'sha256':digest(data),'bytes':len(data),'mtimeNs':path.stat().st_mtime_ns}
externals=[REPO/p['path'] for p in descriptor['externalFiles']]
protected=['contracts/market.json','contracts/source-qualification-probes.json','contracts/factual-corrections.json',
 'web/src/data/tracker/factualCorrectionPolicy.json','web/scripts/pipeline/onboarding.py',
 'web/scripts/pipeline/discovery.py','web/scripts/pipeline/fetcher.py','web/scripts/pipeline/engine.py',
 'web/scripts/pipeline/corrections.py','ops/ci/collect.py']
code=['web/scripts/pipeline/prnewswire_press_list.py','web/scripts/pipeline/prnewswire_retained_window.py',
 'ops/ci/test_prnewswire_press_list.py','ops/ci/test_prnewswire_retained_window.py',
 'docs/active/daily-pipeline/accuracy/prnewswire-retained-window-descriptor-2026-10-25.json',
 'docs/active/daily-pipeline/accuracy/prnewswire-dated-window-parser-build-spec-2026-10-25.md']
seals={str(p):pin(p) for p in externals+[REPO/p for p in protected+code]}
manifest_seal=pin(ARCHIVE/"archive-manifest.json")
store=ReadOnlyActual()
with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')),patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_STORE')):
 contract=json.loads((REPO/'contracts/market.json').read_bytes())
 report=proof.derive_report(contract,store,raw)
 verify=proof.verify_report(contract,store,raw,report)
 replays=[replay_complete(json.loads(store.get(p['record'])),contract,store) for p in descriptor['originalRuns']]
 requests=json.loads((REPO/'contracts/factual-corrections.json').read_bytes())
 stamp=json.loads((REPO/'web/src/data/tracker/factualCorrectionPolicy.json').read_bytes())
 admissions=[]
 for group in requests['groups']:
  policy=group_review_policy(group,contract,requests['baseline']['sha256'])
  assert stamp['reviewPolicySha256ByGroup'][group['id']]==policy
  ref=store.read(_index(group,policy))['admission']
  replay_admission(group,ref,store,contract,policy,AS_OF)
  admissions.append({'groupId':group['id'],'reviewPolicySha256':policy,'admission':ref})
 snapshot=store.read('heads/dailySnapshot.json')
 assert len(snapshot['factProvenance'])==4 and len(snapshot['reviewQueue'])==38
 assert snapshot['coverage']['validUntil']=='2026-10-26T15:55:27.307096+00:00'
 ledger=store.read('heads/budget-2026-10-25.json');assert ledger=={'fetches':1101,'calls':80,'documents':38}
 for ref in snapshot['factProvenance'].values():store.get(ref)
for path,seal in seals.items():assert pin(path)==seal,path
for path,before in store.touched.items():
 assert (pin(path)['sha256'],pin(path)['bytes'],pin(path)['mtimeNs'])==before,path
assert pin(ARCHIVE/"archive-manifest.json")==manifest_seal
assert len(admissions)==6
result={'schemaVersion':1,'verdict':'PASS','originalArchive':descriptor['archive'],'originalAsOf':AS_OF,
 'replayedOriginalRuns':replays,'proposalVerification':verify,'sixAdmissions':admissions,
 'factReferences':snapshot['factProvenance'],'holdRows':len(snapshot['reviewQueue']),
 'sourceExpiry':snapshot['coverage']['validUntil'],'actualFrozenLedger':ledger,
 'manifestSeal':manifest_seal,
 'archiveInputs':{p:{'sha256':s[0],'bytes':s[1],'mtimeNs':s[2]} for p,s in store.touched.items()},
 'externalAndProtectedSeals':seals,'allInputSealsUnchanged':True,'networkDenied':True,
 'frozenLocalStoreConstructionDenied':True,'frozenArchiveWrites':0,'sourceRequests':0,'modelCalls':0,
 'executedJavaScript':False,'newQualificationCredit':0,
 'preservationMethod':'Read/get-only archive adapter checks every consulted input against the authenticated manifest; original and consulted bytes/size/mtime stay exact. Full archive authentication is inherited from sealed actual audits; this replay makes no new whole-archive authentication claim.'}
for name,value in [('derived-report.json',report),('actual-readonly-replay.json',result)]:
 (OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'verdict':'PASS','fullOriginalReplays':len(replays),'admissions':len(admissions),'archiveInputs':len(store.touched),'externalAndProtectedInputs':len(seals),'codePins':{k:pin(REPO/k) for k in code}}))
