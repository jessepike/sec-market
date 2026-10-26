from pathlib import Path
import copy,gzip,hashlib,json,shutil,socket,sys
from unittest.mock import patch
root=Path('/mnt/mac/Users/jessepike/.codex/worktrees/cyera-current-primary/sec-market')
sys.path[:0]=[str(root/'web/scripts/pipeline'),str(root/'ops/ci')]
from contracts import canonical,digest
from storage import LocalStore
import cyera_primary_capture as operation
from test_prnewswire_retained_window import replay_complete
receipts=root/'docs/active/daily-pipeline/accuracy/receipts/cyera-current-primary-build-2026-10-25'
vm=Path('/var/tmp/smp-cyera-current-primary-build-20261025')
archive=Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted')
raw_manifest=(archive/'archive-manifest.json').read_bytes();assert digest(raw_manifest)=='13d956802cd881c0d6805c00c0dee48de07bd6615196e69f74fbf4056a710e34'
entries={r['key']:r for r in json.loads(raw_manifest)['files']};assert len(entries)==52273
pins={}
class ReadOnly:
 def raw(self,key):
  relative='state/'+key;path=archive/relative;row=entries[relative]
  assert not path.is_symlink() and path.resolve().is_relative_to(archive)
  raw=path.read_bytes();assert digest(raw)==row['sha256'] and len(raw)==row['bytes']
  pins[relative]={'key':relative,'sha256':digest(raw),'bytes':len(raw),'mtimeNs':path.stat().st_mtime_ns};return raw
 def get(self,ref):
  raw=self.raw(ref['key']);assert digest(raw)==ref['sha256'] and len(raw)==ref['bytes'];return raw
 def read(self,key):return json.loads(self.raw(key))
store=ReadOnly();contract=json.loads((root/'contracts/market.json').read_bytes());rawplan=(root/'docs/active/daily-pipeline/accuracy/cyera-primary-capture-plan-2026-10-25.json').read_bytes()
with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')),patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_STORE')):
 normalized=operation.validate_plan(contract,store,rawplan)
 original=operation.origin.inverse_policy(contract,store)
 record=json.loads(store.get(normalized['plan']['historicalReplay']['record']))
 replay=replay_complete(record,original,store)
for relative,pin in pins.items():
 path=archive/relative;assert (digest(path.read_bytes()),path.stat().st_size,path.stat().st_mtime_ns)==(pin['sha256'],pin['bytes'],pin['mtimeNs'])
result={'status':'PASS','authority':'offline_build_evidence_only','archiveManifestSha256':digest(raw_manifest),'archiveManifestFiles':len(entries),
 'wholeArchiveAuthentication':'Existing root actual-J audit authenticates all 52273 files; this receipt authenticates and seals only the consumed read set.',
 'currentPolicySha256':digest(contract),'originalPolicySha256':digest(original),'candidatePlanRawSha256':digest(rawplan),
 'originalFullHReplay':replay,'genericSources':len(record['diagnostic']['sources']),'explicitTargets':len(record['diagnostic']['qualification']['targets']),
 'originalCharges':record['diagnostic']['reservationContext']['probeFetchReservations'],
 'sourceRequests':0,'modelCalls':0,'frozenWrites':0,'activePlanChanged':False,'consumedReadSet':sorted(pins.values(),key=lambda x:x['key']),
 'streamSha256':digest(normalized['streams'][0]),'cardCount':len(normalized['streams'][0]['records']),
 'seedCount':len(normalized['streams'][0]['knownSeedMembership']),'currentWindowItems':normalized['streams'][0]['currentWindowItems']}
(receipts/'actual-J-retained-replay.json').write_bytes(canonical(result))
(receipts/'retained-stream.json.gz').write_bytes(gzip.compress(canonical(normalized['streams'][0]),mtime=0))
for name in ('npm-test.log','operations-tests.log','archive-absent-tests.log','production-renders.log','local-renders.log','baseline-build.log'):
 (receipts/(name+'.gz')).write_bytes(gzip.compress((vm/name).read_bytes(),mtime=0))
for src,name in [('/var/tmp/cyera-focused-initial.log','focused-counterexample-before-adapter.log.gz'),('/var/tmp/cyera-focused-final.log','focused-final.log.gz')]:
 (receipts/name).write_bytes(gzip.compress(Path(src).read_bytes(),mtime=0))
shutil.copyfile(vm/'assembly.json',receipts/'assembly.json')
prior=Path('/mnt/mac/Users/jessepike/Documents/Codex/2026-10-22/security-market-pulse/renewal-20261024')
renders=[]
for surface in ('production','local'):
 for width in (1440,390):
  name=f'{surface}-{width}.png';new=(receipts/'images'/name).read_bytes();old=(prior/f'prn-dated-window-{name}').read_bytes();assert new==old
  renders.append({'surface':surface,'width':width,'sha256':digest(new),'bytes':len(new),'exactPriorImage':str(prior/f'prn-dated-window-{name}'),'unchanged':True,'viewed':True})
(receipts/'renders.json').write_bytes(canonical({'status':'PASS','scope':'No change to corresponding retained base render; pre-existing production/local data difference persists.','images':renders}))
print(json.dumps({'status':'PASS','consumedFiles':len(pins),'cards':56,'seeds':5,'replaySha256':digest(canonical(result)),'streamSha256':digest(normalized['streams'][0]),'renderCount':len(renders)}))
