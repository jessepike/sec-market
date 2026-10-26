from pathlib import Path
import sys,json,unittest,os
from unittest.mock import patch
R=Path('/var/tmp/smp-prn-controlled-integration-20261026/app');OUT=R.parent
roots=[p for p in Path('/var/tmp').glob('smp-*') if p.is_dir() and p!=OUT]
attempts=[]
def frozen(p):
 try:p=Path(p)
 except TypeError:return False
 return any(p==r or r in p.parents for r in roots)
exists=Path.exists
def absent(p):return False if frozen(p)else exists(p)
def audit(event,args):
 if event=='open' and args and isinstance(args[0],(str,bytes)) and frozen(args[0]):
  attempts.append(str(args[0]));raise AssertionError('FROZEN_ARCHIVE_READ_DENIED')
sys.addaudithook(audit)
os.chdir(R)
sys.path[:0]=[str(R),str(R/'ops/ci'),str(R/'web/scripts/pipeline')]
is_file,is_dir=Path.is_file,Path.is_dir
with patch.object(Path,'exists',absent), patch.object(Path,'is_file',lambda p:False if frozen(p) else is_file(p)), patch.object(Path,'is_dir',lambda p:False if frozen(p) else is_dir(p)):
 suite=unittest.defaultTestLoader.discover(str(R/'ops/ci'),pattern='test_*.py')
 with (OUT/'logs/operations-absent.log').open('w')as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
receipt={'status':'PASS'if result.wasSuccessful()and not attempts else 'FAIL','mode':'fresh_full_discovery_archives_absent_before_import','testsRun':result.testsRun,'passed':result.testsRun-len(result.skipped)-len(result.failures)-len(result.errors),'skipped':[{'test':str(t),'reason':r}for t,r in result.skipped],'frozenReadAttempts':attempts,'portablePRNCoreSkipped':[str(t)for t,r in result.skipped if 'prnewswire_primary_capture.CaptureTests' in str(t)]}
(OUT/'operations-absent.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='skipped'}));sys.exit(0 if receipt['status']=='PASS'else 1)
