"""Offline exact-main diagnosis. Never execute notify or perform transport."""
import gzip,hashlib,io,json,re,socket,sys,traceback
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

APP=Path('/var/tmp/smp-recovery-monitor-40175735011-20261025/app')
OUT=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/receipts/recovery-monitor-2026-10-25')
ARCHIVE=Path('/var/tmp/smp-manual-freshness-recovery-40169973257-20261025/extracted')
PRIOR=Path('/var/tmp/smp-manual-freshness-publication-40172130763-20261025')
sys.path[:0]=[str(APP/'ops/watchdog'),str(APP/'web/scripts/pipeline')]
import probe
from contracts import digest,canonical,instant
from provenance import GitHubAuthority
from artifacts import unpack,inventory

def read(name):return json.loads((OUT/name).read_bytes())
def sha(body):return hashlib.sha256(body).hexdigest()

trace=[]
manifest_raw=(ARCHIVE/'archive-manifest.json').read_bytes()
assert sha(manifest_raw)=='540bb0449b922b0ea69ab3a088d35b0f3bc8926243a8d5c817ab93c2659abd8e'
entries={r['key']:r for r in json.loads(manifest_raw)['files']}
consulted={'archive-manifest.json':(sha(manifest_raw),len(manifest_raw),(ARCHIVE/'archive-manifest.json').stat().st_mtime_ns)}
def frozen_get(reference):
 key='state/'+reference['key'];row=entries[key];path=ARCHIVE/key
 raw=path.read_bytes();assert sha(raw)==row['sha256']==reference['sha256'] and len(raw)==row['bytes']==reference['bytes']
 consulted[key]=(sha(raw),len(raw),path.stat().st_mtime_ns)
 return raw

latest=read('latest.json');release=read('release.json');manifest=release['manifest']
coverage_raw=frozen_get(latest['receipt'])
coverage=json.loads(coverage_raw)
assert latest['runId']==coverage['runId']==manifest['runId']
archive_files={'heads/latest-run.json':latest,'heads/worker-heartbeat.json':read('worker-heartbeat.json'),
               'heads/production.json':read('production.json'),
               'releases/'+manifest['releaseId']+'.json':release,
               'gate-receipts/40172376435.json':read('gate-receipt.json')}
def read_archive(key,reference=None):
 trace.append({'phase':'archive_read','key':key})
 return json.loads(frozen_get(reference)) if reference else archive_files[key]

gate_zip=(PRIOR/'gate-artifact.zip').read_bytes()
metadata=read('gate-artifact-metadata.json')
assert metadata['digest']=='sha256:'+sha(gate_zip)
assert sha(gate_zip)=='ef628abef50d32f88c9c8dec0a04099f74b84a5fa7d954f1d22d7e8931d6b3d4'
gate_receipt=read('gate-receipt.json')
assert digest(gate_receipt)==manifest['testReceiptSha256']
build_raw=(PRIOR/'build.zip').read_bytes()
assert sha(build_raw)==manifest['artifact']['archive']['sha256']
files=unpack(build_raw);artifact_inventory=inventory(files);inventory_raw=canonical(artifact_inventory)
assert sha(inventory_raw)==manifest['artifact']['sha256']==manifest['artifact']['inventory']['sha256']
assert len(inventory_raw)==manifest['artifact']['inventory']['bytes']
(OUT/'accepted-artifact-inventory.json').write_bytes(inventory_raw)

def runner(args,**kwargs):
 path=args[-1]
 trace.append({'phase':'authority_api_fixture','path':path})
 bodies={'repos/jessepike/sec-market/actions/runs/40172376435':(OUT/'gate-run.json').read_bytes(),
         'repos/jessepike/sec-market/actions/artifacts/12590843044':(OUT/'gate-artifact-metadata.json').read_bytes(),
         'repos/jessepike/sec-market/actions/artifacts/12590843044/zip':gate_zip}
 assert path in bodies
 return SimpleNamespace(returncode=0,stdout=bodies[path],stderr=b'')
class Authority(GitHubAuthority):
 def verify_test_receipt(self,*args):
  trace.append({'phase':'authority_verify_start'})
  result=super().verify_test_receipt(*args)
  assert result is True
  trace.append({'phase':'authority_verify_pass'})
  return result

live={}
for name in ('deployment-receipt','app-release','daily-coverage'):
 raw=gzip.decompress((OUT/('public-'+name+'.json.gz')).read_bytes())
 live['https://securitymarketpulse.com/'+name+'.json']=raw
 if name!='deployment-receipt':assert raw==files['static/'+name+'.json']
coverage_entry=next(row for row in artifact_inventory if row['path']=='static/daily-coverage.json')
assert coverage_entry['bytes']==1337257 and coverage_entry['sha256']==sha(live['https://securitymarketpulse.com/daily-coverage.json'])
class Response(io.BytesIO):
 def __init__(self,url):
  super().__init__(live[url]);self.status,self.url=200,url
 def read(self,n=-1):
  result=super().read(n)
  trace.append({'phase':'response_read','url':self.url,'requestedBytes':n,'returnedBytes':len(result),'actualFullBodyBytes':len(live[self.url])})
  return result
def urlopen(request,timeout):
 url=request.full_url
 assert url in live and timeout==25
 trace.append({'phase':'get_json_urlopen_fixture','url':url,'httpStatus':200})
 return Response(url)
def get_live(url):
 trace.append({'phase':'get_live','url':url})
 return probe.get_json(url)

raw_log=gzip.decompress((OUT/'daily-pipeline.log.gz').read_bytes())
plain='\n'.join(re.sub(r'^\ufeff?\d{4}-\d{2}-\d{2}T[^ ]+Z ','',line) for line in raw_log.decode('utf-8').splitlines())
marker=plain.index('{\n  "healthy":')
actual_result,_=json.JSONDecoder().raw_decode(plain[marker:])
assert actual_result['checkedAt']=='2026-10-25T08:13:04.369084Z'
(OUT/'actual-monitor-result.json').write_text(json.dumps(actual_result,indent=2)+'\n')
contract=json.loads((APP/'contracts/market.json').read_bytes())
caught=None
with patch.object(probe.urllib.request,'urlopen',side_effect=urlopen),patch.object(socket.socket,'connect',side_effect=AssertionError('offline replay prohibits network')):
 try:
  probe.inspect(contract,read_archive,get_live,actual_result['checkedAt'],Authority(runner=runner))
 except ValueError as error:
  caught={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
assert caught and caught['message']=='Production health receipt exceeds byte budget'
probe.verify_acknowledgement(manifest,json.loads(live['https://securitymarketpulse.com/deployment-receipt.json']))
app=json.loads(live['https://securitymarketpulse.com/app-release.json'])
assert app['appRevision']==manifest['appRevision'] and app['dailySnapshotSha256']==manifest['snapshot']['sha256']
assert any(r['phase']=='authority_verify_pass' for r in trace)
coverage_reads=[r for r in trace if r['phase']=='response_read' and r['url'].endswith('/daily-coverage.json')]
assert coverage_reads==[{'phase':'response_read','url':'https://securitymarketpulse.com/daily-coverage.json','requestedBytes':1000001,'returnedBytes':1000001,'actualFullBodyBytes':1337257}]
assert not any(r.get('key','').endswith('dailySnapshot.json') for r in trace)
for key,before in consulted.items():
 path=ARCHIVE/key;raw=path.read_bytes();assert (sha(raw),len(raw),path.stat().st_mtime_ns)==before
public=json.loads(live['https://securitymarketpulse.com/daily-coverage.json'])
heartbeat=archive_files['heads/worker-heartbeat.json']
result={'scope':'Offline deterministic reproduction with exact unmodified main6d source and actual retained inputs; no new probe, notify, source/model/gate or archive mutation',
 'appRevision':'6d5e87feba4ffbc75e50f35cb564cb8fd91708ca','archiveCommit':'b08469e082606def8ef37d9bfeb1cc9609f48176','actualRunId':40175735011,
 'actualRunOnlyLoggedExceptionType':'ValueError','reproducedException':caught,'authorityVerifiedBeforeFailure':True,
 'earlierPublicAcknowledgementAndAppPairPassed':True,'publicCoverageArtifactEntry':coverage_entry,'artifactInventorySha256':sha(inventory_raw),'artifactInventoryBytes':len(inventory_raw),
 'rawPublicCoverageCanonicalSha256':digest(public),'validUntil':public['validUntil'],'actualMonitorCheckedAt':actual_result['checkedAt'],
 'publicOverdueAtActualMonitor':instant(actual_result['checkedAt'])>instant(public['validUntil']),
 'heartbeatPhases':heartbeat['phases'],'heartbeatFreshAtActualMonitor':0<=(instant(actual_result['checkedAt'])-instant(heartbeat['finishedAt'])).total_seconds()/3600<=contract['schedule']['overdueHours'],
 'actualHealthReasons':actual_result['reasons'],'trace':trace,'frozenInputSeals':[{'key':k,'sha256':v[0],'bytes':v[1],'mtimeNs':v[2],'unchanged':True} for k,v in consulted.items()],
 'sourcePins':{p:sha((APP/p).read_bytes()) for p in ('ops/watchdog/probe.py','web/scripts/pipeline/provenance.py','web/scripts/pipeline/publication.py','contracts/market.json')}}
(OUT/'exact-main-cause-replay.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
