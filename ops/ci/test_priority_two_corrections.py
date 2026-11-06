"""Pending two-group preparation and synthetic temporary mechanics; never real admissions."""
import copy
from contextlib import contextmanager
from datetime import timedelta
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'web/scripts/pipeline'),str(ROOT/'ops/ci')]
from agents import SubscriptionAgent
from contracts import canonical,digest,instant
from corrections import load_policy,group_review_policy,validate_sources,process_corrections,project_bundle,_index,replay_admission
from historical_correction_fixtures import historical_requests,historical_stamp,historical_repo
from release import preflight_corrections
from storage import LocalStore
from validation import REVIEW_CHECKS
PACKET=ROOT/'docs/active/daily-pipeline/accuracy/priority-correction-candidate-packet-2026-10-25.json'
ARCHIVE=Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted')
NOW='2026-10-26T00:05:00Z'
def read(path):return json.loads(path.read_bytes())
def stamp(requests,market):
 return {'schemaVersion':1,'policySha256':digest({'marketSha256':digest(market),'requestsSha256':digest(requests),'baselineSha256':requests['baseline']['sha256']}),'groupIds':[g['id']for g in requests['groups']],'targetIds':[t['targetId']for g in requests['groups']for t in g['targets']],'sourceEvidenceIds':{g['id']:[s['evidenceId']for s in g['sources']]for g in requests['groups']},'reviewPolicySha256ByGroup':{g['id']:group_review_policy(g,market,requests['baseline']['sha256'])for g in requests['groups']}}
@contextmanager
def candidate_repo(requests,market):
 with historical_repo(ROOT) as repo:
  (repo/'contracts/factual-corrections.json').write_bytes(canonical(requests))
  (repo/'web/src/data/tracker/factualCorrectionPolicy.json').write_bytes(canonical(stamp(requests,market)))
  yield repo
class ReadOnlyJ:
 def __init__(self):
  raw=(ARCHIVE/'archive-manifest.json').read_bytes();assert digest(raw)=='13d956802cd881c0d6805c00c0dee48de07bd6615196e69f74fbf4056a710e34'
  self.entries={r['key']:r for r in json.loads(raw)['files']};assert len(self.entries)==52273;self.touched={}
 def raw(self,key):
  path=ARCHIVE/'state'/key;row=self.entries.get('state/'+key)
  if row is None:assert not path.exists();return None
  assert not path.is_symlink()and path.resolve().is_relative_to(ARCHIVE)
  raw=path.read_bytes();assert digest(raw)==row['sha256']and len(raw)==row['bytes']
  self.touched[str(path)]=(digest(raw),len(raw),path.stat().st_mtime_ns);return raw
 def read(self,key):
  raw=self.raw(key);return json.loads(raw)if raw is not None else None
 def get(self,ref):
  raw=self.raw(ref['key']);assert digest(raw)==ref['sha256']and len(raw)==ref['bytes'];return raw
 def unchanged(self,case):
  for name,before in self.touched.items():
   p=Path(name);raw=p.read_bytes();case.assertEqual((digest(raw),len(raw),p.stat().st_mtime_ns),before)
class Overlay:
 def __init__(self,local,base):self.local,self.base=local,base
 def read(self,key):
  value=self.local.read(key);return value if value is not None else self.base.read(key)
 def get(self,ref):return self.local.get(ref)if(self.local.root/ref['key']).exists()else self.base.get(ref)
 def put(self,value):return self.local.put(value)
 def write_once(self,key,value):return self.local.write_once(key,value)
class PendingPolicyTests(unittest.TestCase):
 def setUp(self):
  self.market=read(ROOT/'contracts/market.json');self.requests=read(ROOT/'contracts/factual-corrections.json');self.packet=read(PACKET)
 def test_exact_packet_append_version_and_current_J_with_immutable_old_six(self):
  self.assertEqual(digest(PACKET.read_bytes()),'ffe9400b6f5d1750032ed7d6a1c04c190f43084fa0adde61a47edb3c2244519a')
  from roster_transition import authority_contract
  self.assertEqual(digest(authority_contract(self.market)),'47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a')
  self.assertEqual(self.requests['version'],'2026-10-25.1');self.assertEqual(self.requests['groups'][:6],historical_requests()['groups'])
  self.assertEqual(self.requests['groups'][6:],self.packet['groups']);self.assertEqual(sum(len(g['targets'])for g in self.packet['groups']),5)
  oldraw=(ROOT/'ops/ci/fixtures/accepted-six-correction-requests-2026-10-25.json').read_text();newraw=(ROOT/'contracts/factual-corrections.json').read_text();decoder=json.JSONDecoder();i=oldraw.index('"groups": [')+len('"groups": [')
  for _ in range(6):
   while oldraw[i].isspace()or oldraw[i]==',':i+=1
   _,end=decoder.raw_decode(oldraw,i);self.assertEqual(newraw[i:end],oldraw[i:end]);i=end
 def test_only_outer_stamp_changes_and_generated_projection_remains_disabled(self):
  ctx=load_policy(ROOT,self.market);current=read(ROOT/'web/src/data/tracker/factualCorrectionPolicy.json');self.assertEqual(current,stamp(self.requests,self.market))
  for gid,policy in historical_stamp()['reviewPolicySha256ByGroup'].items():self.assertEqual(ctx['reviewPolicySha256ByGroup'][gid],policy)
  self.assertNotEqual(ctx['policySha256'],historical_stamp()['policySha256'])
  self.assertEqual(read(ROOT/'web/src/data/generated/factualCorrections.json'),{'schemaVersion':1,'enabled':False,'policySha256':None,'checkedAt':None,'groups':[]})
  self.assertEqual(digest((ROOT/'contracts/factual-baseline.json').read_bytes()),self.requests['baseline']['sha256'])
 def test_original_target_source_and_attestation_substitutions_reject(self):
  mutations=[]
  for path,value in [(('targets',0,'originalSha256'),'0'*64),(('targets',0,'original','text'),'forged'),(('sources',0,'sourceId'),'s1:citation:TR-s1-3'),(('sources',0,'url'),'https://evil.invalid/release')]:
   q=copy.deepcopy(self.requests);obj=q['groups'][6]
   for key in path[:-1]:obj=obj[key]
   obj[path[-1]]=value;mutations.append(q)
  for field in self.packet['groups'][1]['sources'][0]['transportAttestation']:
   q=copy.deepcopy(self.requests);q['groups'][7]['sources'][0]['transportAttestation'][field]='forged';mutations.append(q)
  for q in mutations:
   with self.subTest(q=digest(q)),self.assertRaises((ValueError,TypeError)):
    with candidate_repo(q,self.market)as repo:load_policy(repo,self.market)
 def test_pending_current_inventory_blocks_projection_before_any_gate_or_model(self):
  with tempfile.TemporaryDirectory(prefix='synthetic-pending-correction-gate-')as tmp:
   store=LocalStore(Path(tmp));ctx=load_policy(ROOT,self.market);pending={'runId':'SYNTHETIC-PENDING','checkedAt':NOW,'policySha256':ctx['policySha256'],'admitted':[],'pending':[{'groupId':g['id'],'reason':'PENDING_REAL_INDEPENDENT_REVIEW'}for g in self.packet['groups']],'attempts':[]}
   store.compare_and_swap('correction-collection',None,{'runId':pending['runId'],'outcome':store.put(pending)})
   with self.assertRaisesRegex(ValueError,'pending'):preflight_corrections(ROOT,store,self.market,pending['runId'],None,NOW)
   self.assertIsNone(store.read('heads/gate-budget-2026-10-26.json'));self.assertIsNone(store.read('heads/publication-budget-2026-10-26.json'))
@unittest.skipUnless((ARCHIVE/'archive-manifest.json').exists(),'Full authenticated actual J archive available only in offline evidence VM')
class ActualSourceAndSyntheticMechanicsTests(unittest.TestCase):
 def setUp(self):
  self.market=read(ROOT/'contracts/market.json');self.requests=read(ROOT/'contracts/factual-corrections.json');self.packet=read(PACKET);self.base=ReadOnlyJ();self.addCleanup(self.base.unchanged,self)
  self.tmp=tempfile.TemporaryDirectory(prefix='SYNTHETIC-NON-ADMITTING-priority-corrections-');self.addCleanup(self.tmp.cleanup)
  self.local=LocalStore(Path(self.tmp.name));self.store=Overlay(self.local,self.base);self.charges=[];self.reviewed=[];self.transform=lambda x:x
  self.runner=Mock(side_effect=self.synthetic_runner);self.agent=SubscriptionAgent(self.market['model'],runner=self.runner)
  self.net=patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK'));self.net.start();self.addCleanup(self.net.stop)
  self.localguard=patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_LOCALSTORE_CONSTRUCTION'));self.localguard.start();self.addCleanup(self.localguard.stop)
 def reserve(self,kind,limit):self.charges.append((kind,limit))
 def synthetic_runner(self,args,**kwargs):
  if args[1:3]==['login','status']:return subprocess.CompletedProcess(args,0,'Logged in using ChatGPT','')
  payload=json.loads(kwargs['input'].split('UNTRUSTED CORRECTION AND PRIMARY EVIDENCE:\n')[1]);self.reviewed.append(payload['group']['id'] if'group'in payload else payload.get('correction',{}).get('id'))
  response={key:payload[key]for key in('candidateSha256','evidenceSetSha256','policySha256')};response.update(result='accepted',checks={key:'pass'for key in REVIEW_CHECKS});response=self.transform(response)
  Path(args[args.index('--output-last-message')+1]).write_text(json.dumps(response));return subprocess.CompletedProcess(args,0,'','')
 def process(self,**kwargs):return process_corrections(ROOT,self.store,self.market,self.agent,self.reserve,NOW,clock=lambda:NOW,**kwargs)
 def test_new_J_retains_exact_old_packet_sources_whole_texts_and_200_304_clocks(self):
  for group,chars in zip(self.packet['groups'],(26465,8295)):
   docs=validate_sources(group,self.base,self.market,NOW);self.assertEqual(len(docs[0]['text']),chars)
   source=group['sources'][0];obs=self.base.read('observations/'+source['observationId']+'.json');self.assertEqual((obs['status'],obs['httpStatus']),('not_modified',304));self.assertEqual(obs['body'],source['body']);self.assertEqual(obs['fetchedAt'],source['fetchedAt'])
   seen=set();chain=[]
   while True:
    self.assertNotIn(obs['observationId'],seen);seen.add(obs['observationId']);chain.append(obs)
    if obs['status']=='fetched':self.assertEqual(obs['httpStatus'],200);break
    self.assertEqual(obs['httpStatus'],304);prior=self.base.read('observations/'+obs['reusesObservationId']+'.json');self.assertEqual(prior['body'],source['body']);self.assertLessEqual(instant(prior['fetchedAt']),instant(obs['fetchedAt']));obs=prior
   self.assertGreater(len(chain),1)
 def test_each_actual_source_age_has_inclusive_30h_limit_at_start_and_completion(self):
  for group in self.packet['groups']:
   bound=instant(group['sources'][0]['fetchedAt'])+timedelta(hours=30)
   validate_sources(group,self.base,self.market,bound.isoformat().replace("+00:00","Z"))
   for at in(bound+timedelta(microseconds=1),instant(group['sources'][0]['fetchedAt'])-timedelta(microseconds=1)):
    with self.assertRaisesRegex(ValueError,'expired or future'):validate_sources(group,self.base,self.market,at.isoformat().replace("+00:00","Z"))
 def test_literal_excerpt_and_source_body_clock_mismatches_reject(self):
  for index in range(2):
   group=copy.deepcopy(self.packet['groups'][index]);next(t for t in group['targets']if t['targetId'].startswith('evidence:'))['proposedValue']['excerpt']='Fabricated primary excerpt'
   with self.assertRaisesRegex(ValueError,'not literally'):validate_sources(group,self.base,self.market,NOW)
   for field,value in [('fetchedAt',NOW),('observationId','0'*64),('body',{'key':'objects/'+'0'*64,'sha256':'0'*64,'bytes':1})]:
    group=copy.deepcopy(self.packet['groups'][index]);group['sources'][0][field]=value
    with self.subTest(field=field),self.assertRaises(ValueError):validate_sources(group,self.base,self.market,NOW)
 def test_six_old_admissions_replay_without_reservations_before_two_pending_groups(self):
  result=process_corrections(ROOT,self.store,self.market,None,self.reserve,NOW,clock=lambda:NOW)
  self.assertEqual(len(result['admitted']),6);self.assertEqual(len(result['pending']),2);self.assertFalse(self.charges)
  self.assertEqual([r['groupId']for r in result['pending']],[g['id']for g in self.packet['groups']])
  ctx=load_policy(ROOT,self.market)
  for group in self.requests['groups'][:6]:
   policy=ctx['reviewPolicySha256ByGroup'][group['id']];ref=self.base.read(_index(group,policy))['admission'];self.assertEqual(replay_admission(group,ref,self.base,self.market,policy,NOW)['sources'],group['sources'])
 def test_SYNTHETIC_successful_two_group_review_cost_and_order_never_touch_real_state(self):
  result=self.process();self.assertEqual(result['pending'],[]);self.assertEqual(len(result['admitted']),8)
  self.assertEqual(self.charges,[('documents',40),('calls',80),('documents',40),('calls',80)])
  self.assertEqual(len(self.reviewed),2)
  self.assertEqual([r['groupId']for r in result['admitted'][-2:]],[g['id']for g in self.packet['groups']])
  self.assertFalse(self.process()['attempts']);self.assertEqual(len(self.charges),4)
 def test_synthetic_marker_and_rejected_review_remain_pending_without_gate(self):
  self.agent.synthetic=True;result=self.process();self.assertEqual(len(result['pending']),2);self.assertFalse(self.charges)
  del self.agent.synthetic;self.transform=lambda response:{**response,'result':'rejected'};result=self.process();self.assertEqual(len(result['pending']),2);self.assertEqual(len(result['admitted']),6)
  head={'runId':'SYNTHETIC-REJECTED','checkedAt':NOW,**result};self.local.compare_and_swap('correction-collection',None,{'runId':head['runId'],'outcome':self.local.put(head)})
  with self.assertRaisesRegex(ValueError,'pending'):preflight_corrections(ROOT,self.store,self.market,head['runId'],None,NOW)
  self.assertIsNone(self.local.read('heads/gate-budget-2026-10-26.json'))
 def test_completion_after_source_expiry_cannot_admit_second_group(self):
  expiry=instant(self.packet['groups'][1]['sources'][0]['fetchedAt'])+timedelta(hours=30,microseconds=1)
  result=process_corrections(ROOT,self.store,self.market,self.agent,self.reserve,NOW,clock=lambda:expiry.isoformat().replace("+00:00","Z"))
  self.assertEqual(len(result['admitted']),7);self.assertEqual(len(result['pending']),1);self.assertIn('expired',result['pending'][0]['reason'])
  self.assertEqual(len(self.charges),4)
if __name__=='__main__':unittest.main()
