import sys,json,socket,unittest,hashlib
from pathlib import Path
from unittest.mock import patch
R=Path('/mnt/mac/Users/jessepike/.codex/worktrees/prn-current-primary/sec-market');O=Path('/var/tmp/smp-prn-primary-implementation-independent-20261025');F=Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted')
sys.dont_write_bytecode=True;sys.path[:0]=[str(R/'ops/ci'),str(R/'web/scripts/pipeline')]
from contracts import digest
from storage import LocalStore
import prnewswire_primary_capture as op
from test_prnewswire_retained_window import replay_complete
raw=(F/'archive-manifest.json').read_bytes();assert digest(raw)=='13d956802cd881c0d6805c00c0dee48de07bd6615196e69f74fbf4056a710e34';entries={x['key']:x for x in json.loads(raw)['files']};assert len(entries)==52273
seals={}
class ReadOnly:
 def raw(self,key):
  p=F/'state'/key;row=entries.get('state/'+key)
  if row is None:assert not p.exists();return None
  assert not p.is_symlink() and p.resolve().is_relative_to(F)
  st=p.stat();b=p.read_bytes();assert digest(b)==row['sha256'] and len(b)==row['bytes']
  seal={'path':str(p),'sha256':digest(b),'bytes':len(b),'mtimeNs':st.st_mtime_ns,'inode':st.st_ino}
  if key in seals:assert seals[key]==seal
  seals[key]=seal;return b
 def read(self,key):
  raw=self.raw(key);return json.loads(raw) if raw is not None else None
 def get(self,ref):
  b=self.raw(ref['key']);assert digest(b)==ref['sha256'] and len(b)==ref['bytes'];return b
base=ReadOnly();contract=json.loads((R/'contracts/market.json').read_bytes());rawplan=(R/'docs/active/daily-pipeline/accuracy/prnewswire-primary-capture-plan-2026-10-25.json').read_bytes();results=[]
def audit(event,args):
 if event in ('socket.connect','subprocess.Popen'):raise AssertionError('NO_NETWORK_OR_PROCESS')
 if event=='open' and isinstance(args[0],(str,bytes)) and str(args[0]).startswith(str(F)):
  mode,flags=args[1:];assert not (isinstance(mode,str) and any(x in mode for x in 'wax+')) and not (isinstance(flags,int) and flags & 3),'NO_FROZEN_WRITES'
sys.addaudithook(audit)
with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')),patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_STORE')):
 normalized=op.validate_plan(contract,base,rawplan);old=op.origin.inverse_policy(contract,base)
 for pin in normalized['plan']['originalRuns']:
  record=json.loads(base.get(pin['record']));result=replay_complete(record,old,base);assert result['fullLegacyTraversalReplay'];results.append({'runId':pin['runId'],'proof':result,'genericRows':len(record['diagnostic']['sources']),'explicitRows':len(record['diagnostic']['qualification']['targets']),'fetchReservations':record['diagnostic']['reservationContext']['probeFetchReservations']})
for row in seals.values():
 p=Path(row['path']);st=p.stat();assert digest(p.read_bytes())==row['sha256'] and st.st_size==row['bytes'] and st.st_mtime_ns==row['mtimeNs'] and st.st_ino==row['inode']
out={'status':'PASS','manifestSha256':digest(raw),'manifestFiles':52273,'currentJ':digest(contract),'originalH':digest(old),'completeOriginalReplays':results,'consumedInputCount':len(seals),'seals':list(seals.values()),'sourceRequests':0,'models':0,'frozenWrites':0,'sourceClocksRebased':False}
(O/'actual-full-graph-replay.json').write_text(json.dumps(out,indent=2,sort_keys=True));print({k:v for k,v in out.items() if k!='seals'})
