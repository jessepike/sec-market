"""Offline preparation only: real frozen sources/old admissions, no new admission or writer."""
from pathlib import Path
import json,sys,socket
from datetime import timedelta
from unittest.mock import patch
REPO=Path(__file__).resolve().parents[6]
sys.path[:0]=[str(REPO/'web/scripts/pipeline'),str(REPO/'ops/ci')]
from test_priority_two_corrections import ReadOnlyJ,ARCHIVE,NOW
from historical_correction_fixtures import historical_requests,historical_stamp
from contracts import digest,instant
from corrections import load_policy,validate_sources,_index,replay_admission
from discovery import Page
from storage import LocalStore
from artifacts import stage_files
OUT=Path(__file__).parent
market=json.loads((REPO/'contracts/market.json').read_bytes());context=load_policy(REPO,market);requests=context['requests']
packet_path=REPO/'docs/active/daily-pipeline/accuracy/priority-correction-candidate-packet-2026-10-25.json'
assert digest(packet_path.read_bytes())=='ffe9400b6f5d1750032ed7d6a1c04c190f43084fa0adde61a47edb3c2244519a'
packet=json.loads(packet_path.read_bytes());assert requests['groups'][6:]==packet['groups'];assert requests['groups'][:6]==historical_requests()['groups']
def pin(path):
 path=Path(path);raw=path.read_bytes();return {'sha256':digest(raw),'bytes':len(raw),'mtimeNs':path.stat().st_mtime_ns}
protected=['contracts/market.json','contracts/source-qualification-probes.json','contracts/factual-baseline.json','web/src/data/tracker/originals.json','web/src/data/generated/factualCorrections.json','web/src/data/generated/dailyBaseline.json','web/scripts/pipeline/corrections.py','web/scripts/pipeline/engine.py','web/scripts/pipeline/fetcher.py','ops/ci/collect.py']
protected=[p for p in protected if(REPO/p).exists()]
seals={p:pin(REPO/p)for p in protected};manifest=pin(ARCHIVE/'archive-manifest.json');store=ReadOnlyJ()
def chain(source,observation):
 values=[];seen=set()
 while True:
  assert observation['sourceId']==source['sourceId']and observation['requestedUrl']==source['url']and observation['body']==source['body']
  assert observation['observationId']not in seen;seen.add(observation['observationId']);values.append(observation)
  if observation['status']=='fetched':assert observation['httpStatus']==200;break
  assert(observation['status'],observation['httpStatus'])==('not_modified',304)
  prior=store.read('observations/'+observation['reusesObservationId']+'.json')
  assert instant(prior['fetchedAt'])<=instant(observation['fetchedAt']);observation=prior
 return values
with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')),patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_LOCALSTORE')):
 admissions=[]
 for g in requests['groups'][:6]:
  policy=context['reviewPolicySha256ByGroup'][g['id']];assert historical_stamp()['reviewPolicySha256ByGroup'][g['id']]==policy
  ref=store.read(_index(g,policy))['admission'];admission=replay_admission(g,ref,store,market,policy,NOW)
  admissions.append({'groupId':g['id'],'candidateSha256':digest(g),'reviewPolicySha256':policy,'admission':ref,'originalAdmittedAt':admission['admittedAt']})
 latest_keys={'varonis:citation:TR-varonis-2':'observations/4516ac3144bbfcb89f469c475f1dd0f882be3c00c2317619f655c9322265ac41.json','s1:citation:TR-s1-3':'observations/f653dacd4d25cb57566e3f2f7707298fc7a3501ae582a134a3bab00cfdb6947d.json'}
 rows=[]
 for group,expected_chars in zip(packet['groups'],(26465,8295)):
  source=group['sources'][0];docs=validate_sources(group,store,market,NOW);assert len(docs[0]['text'])==expected_chars
  completed='2026-10-26T00:06:00Z';validate_sources(group,store,market,completed)
  bound=instant(source['fetchedAt'])+timedelta(hours=30);validate_sources(group,store,market,bound.isoformat().replace('+00:00','Z'))
  try:validate_sources(group,store,market,(bound+timedelta(microseconds=1)).isoformat().replace('+00:00','Z'))
  except ValueError as exc:expiry_rejection=str(exc)
  else:raise AssertionError('Expired source was accepted')
  original=store.read('observations/'+source['observationId']+'.json');current=store.read(latest_keys[source['sourceId']]);assert current['body']==source['body']and current['fetchedAt']>=source['fetchedAt']
  original_chain=chain(source,original);latest_chain=chain(source,current);page=Page(store.get(source['body']).decode('utf8'),source_url=source['url'])
  rows.append({'groupId':group['id'],'source':source,'configuredSourceSha256':digest(next(s for s in market['sources']if s['id']==source['sourceId'])),'wholeNormalizedTextChars':len(docs[0]['text']),'wholeTextSha256':digest(docs[0]['text'].encode()),'hypotheticalReviewStart':NOW,'hypotheticalReviewCompletion':completed,'lastPermittedAdmissionAt':bound.isoformat().replace('+00:00','Z'),'oneMicrosecondLaterRejected':expiry_rejection,'originalBoundObservation':original,'original304To200Chain':original_chain,'latestActualJObservation':current,'latestActualJ304To200Chain':latest_chain,'latestBodyExactlySame':True,'newBindingSelected':False,'suppliedPublication':page.published,'publicationAmbiguous':page.publication_ambiguous,'jsonDates':sorted(page.json_dates),'newGroupReviewPolicySha256':context['reviewPolicySha256ByGroup'][group['id']]})
 production=store.read('heads/production.json');release=store.read('releases/'+production['releaseId']+'.json');files=stage_files(store,release['manifest']['artifact'],release['acknowledgement']);public=json.loads(files['static/factual-corrections.json']);assert len(public['groups'])==6
 public_rows=[]
 for group,row in zip(requests['groups'][:6],public['groups']):
  assert group['id']==row['id']and group['targets']==row['targets'];assert row['admission']['candidateSha256']==digest(group)
  public_rows.append({'groupId':row['id'],'rowSha256':digest(row),'originalPublicationDate':row['date'],'note':row['note']})
 snapshot=store.read('heads/dailySnapshot.json');ledger=store.read('heads/budget-2026-10-25.json');gate=store.read('heads/gate-budget-2026-10-25.json')
 assert ledger=={'fetches':1511,'calls':80,'documents':39}
for name,seal in seals.items():assert pin(REPO/name)==seal,name
assert pin(ARCHIVE/'archive-manifest.json')==manifest
for name,before in store.touched.items():s=pin(name);assert(s['sha256'],s['bytes'],s['mtimeNs'])==before
result={'schemaVersion':1,'verdict':'PASS_PENDING_PREPARATION_ONLY','sourceArchiveCommit':'8b3811df40cfdbec9d5ed52252524294566c88e0','manifest':manifest,'actualArchiveEntries':52273,'marketSha256':digest(market),'requestsSha256':digest(requests),'requestsRawSha256':digest((REPO/'contracts/factual-corrections.json').read_bytes()),'outerPolicySha256':context['policySha256'],'sourceValidationRows':rows,'oldSixAdmissionsUnchanged':admissions,'oldPublicCorrectionRowsUnchanged':public_rows,'actualPublicReleaseId':production['releaseId'],'actualFrozenLedger':ledger,'actualGateLedger':gate,'privateSnapshot':{'referenceCount':len(snapshot['factProvenance']),'reviewQueueRows':len(snapshot['reviewQueue']),'coverageValidUntil':snapshot['coverage']['validUntil']},'protectedSourcePins':seals,'archiveInputSeals':{p:{'sha256':s[0],'bytes':s[1],'mtimeNs':s[2]}for p,s in store.touched.items()},'allSealsUnchanged':True,'sourceRequests':0,'modelRequests':0,'newAdmissions':0,'archiveWrites':0,'semanticReviewPending':True,'minimumSuccessfulIncrementalReview':{'calls':2,'documents':2,'correctionFetches':0},'limits':'Future clocks are hypothetical guard checks, not real review or admission. Full archive authentication is inherited; consulted bytes are independently hash/size/mtime checked.'}
(OUT/'actual-source-and-old-admission-readiness.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'verdict':result['verdict'],'oldAdmissions':len(admissions),'sources':len(rows),'consultedArchiveSeals':len(store.touched),'ledger':ledger,'newAdmissions':0}))
