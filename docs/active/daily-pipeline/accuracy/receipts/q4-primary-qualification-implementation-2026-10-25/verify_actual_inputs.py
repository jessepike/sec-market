"""Offline actual parent proof/admission replay. No source requests or frozen writes."""
import json, socket, sys
from pathlib import Path
from unittest.mock import patch
repo=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022')
sys.path[:0]=[str(repo/'web/scripts/pipeline'),str(repo/'ops/ci')]
from contracts import digest
from storage import LocalStore
from test_q4_press_list import ReadOnlyD660, ARCHIVE
from corrections import _index, group_review_policy, replay_admission
import q4_primary_qualification as operation
out=Path('/var/tmp/smp-q4-primary-build-20261025')
previous=json.loads((out/'actual-readonly-replay.json').read_bytes())
store=ReadOnlyD660();contract=json.loads((repo/'contracts/market.json').read_bytes())
raw=(repo/'docs/active/daily-pipeline/accuracy/q4-primary-qualification-plan-2026-10-25.json').read_bytes()
requests=json.loads((repo/'contracts/factual-corrections.json').read_bytes())
stamp=json.loads((repo/'web/src/data/tracker/factualCorrectionPolicy.json').read_bytes())
with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')), patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_LOCALSTORE')):
    plan=operation.validate_plan(contract,store,raw)
    for group in requests['groups']:
        policy=group_review_policy(group,contract,requests['baseline']['sha256'])
        assert policy==stamp['reviewPolicySha256ByGroup'][group['id']]
        ref=store.read(_index(group,policy))['admission'];before=store.get(ref)
        replay_admission(group,ref,store,contract,policy,'2026-10-25T12:00:00Z')
        assert store.get(ref)==before
    snapshot=store.read('heads/dailySnapshot.json')
    for ref in snapshot['factProvenance'].values():store.get(ref)
    assert store.read('heads/production.json')==previous['preservedBaseline']['production']
    assert store.read('heads/budget-2026-10-25.json')==previous['preservedBaseline']['budget']
    assert store.read('heads/gate-budget-2026-10-25.json')==previous['preservedBaseline']['gates']
    assert len(snapshot['reviewQueue'])==38 and len(snapshot['factProvenance'])==4
for name,before in store.touched.items():
    f=Path(name);body=f.read_bytes();assert (digest(body),len(body),f.stat().st_mtime_ns)==before
previous['sources']=[{'sourceId':stream['sourceId'],'records':len(stream['records']),'currentWindowRecords':len(stream['currentWindowItems']),'asOf':stream['asOf'],'windowStart':stream['windowStart'],'windowEnd':stream['windowEnd'],'olderBoundaryPresent':stream['olderBoundaryPresent'],'timezone':stream['timezone'],'sourceDateAnomalies':stream['sourceDateAnomalies'],'sample':plan['targets'][i]['sample'],'initialBody':stream['initialBody'],'originalFetchedAt':stream['originalFetchedAt']} for i,stream in enumerate(plan['streams'])]
previous['inputSeals']={k:{'sha256':v[0],'bytes':v[1],'mtimeNs':v[2]} for k,v in store.touched.items()}
previous['replayedFinalCodePins']={name:digest((repo/name).read_bytes()) for name in ['web/scripts/pipeline/q4_press_list.py','web/scripts/pipeline/q4_primary_qualification.py','ops/ci/collect.py']}
(out/'actual-readonly-replay.json').write_text(json.dumps(previous,indent=2)+'\n')
print(json.dumps({'actualInputSeals':len(store.touched),'admissions':6,'sourceCounts':[len(x['records']) for x in plan['streams']],'currentWindowCounts':[len(x['currentWindowItems']) for x in plan['streams']],'allInputsUnchanged':True}))
