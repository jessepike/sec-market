import hashlib,json,subprocess
from pathlib import Path
B=Path('/var/tmp/smp-oct27-native-40489959161');C=B/'capture'
proof=json.loads((C/'download-proof.json').read_bytes());tip=proof['archiveCommit']
base='62c021b6913b030fcda3b8910f87d42a9924ca50';immediate='5a696e3b20909d054fa4bd2c34d86152bab49a5a'
rows=[];seen=set();sha=tip
for i in range(40):
 if sha==base:break
 assert sha not in seen;seen.add(sha)
 raw=subprocess.check_output(['mac','gh','api','repos/jessepike/sec-market/git/commits/'+sha]);item=json.loads(raw)
 (C/('archive-ancestor-'+str(i)+'.json')).write_bytes(raw)
 assert item['sha']==sha and len(item['parents'])==1
 rows.append({'commit':sha,'tree':item['tree']['sha'],'parent':item['parents'][0]['sha'],'rawSha256':hashlib.sha256(raw).hexdigest(),'rawBytes':len(raw),'message':item['message']})
 sha=item['parents'][0]['sha']
assert sha==base and immediate in seen, 'Actual archive is not a successor of expected baselines'
raw=subprocess.check_output(['mac','gh','api','repos/jessepike/sec-market/git/ref/archive/market-evidence']);ref=json.loads(raw)
(C/'archive-ref-after-audit.json').write_bytes(raw)
result={'actualAcknowledgedCommit':tip,'baselineCommit':base,'baselineIsAncestor':True,'immediatePriorArchive':immediate,'immediatePriorIsAncestor':True,'commits':rows,'archiveRefAtRead':ref['object']['sha'],'tipIsCurrentAtRead':ref['object']['sha']==tip}
(C/'archive-ancestry.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'baselineIsAncestor':True,'immediatePriorIsAncestor':True,'commits':len(rows),'tipIsCurrentAtRead':result['tipIsCurrentAtRead']},indent=2))
