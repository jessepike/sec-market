from pathlib import Path
from unittest.mock import patch
import ast,json,os,sys,unittest
root=Path('/var/tmp/smp-cyera-controlled-integration-20261026/application')
sys.path[:0]=[str(root),str(root/'ops/ci'),str(root/'web/scripts/pipeline')]
os.chdir(root)
# Resolve literal external fixture roots before discovery, without importing tests.
frozen=set()
for path in (root/'ops/ci').glob('*.py'):
 for node in ast.walk(ast.parse(path.read_text())):
  if isinstance(node,ast.Constant) and isinstance(node.value,str) and node.value.startswith('/var/tmp/'):
   frozen.add('/var/tmp/'+node.value.split('/')[3])
frozen=sorted(frozen);assert not any(str(root).startswith(p) for p in frozen)
attempts=[]
def audit(event,args):
 if event in ('open','os.listdir','os.scandir') and args and isinstance(args[0],(str,bytes,os.PathLike)):
  name=os.fsdecode(args[0])
  if any(name==p or name.startswith(p+'/') for p in frozen):
   attempts.append({'event':event,'path':name});raise AssertionError('FROZEN_ARCHIVE_READ_WHILE_ABSENT')
sys.addaudithook(audit)
original=Path.exists
original_dir=Path.is_dir
original_file=Path.is_file
def hidden(path):
 name=str(path)
 return any(name==p or name.startswith(p+'/') for p in frozen)
def absent(path):
 name=str(path)
 return False if any(name==p or name.startswith(p+'/') for p in frozen) else original(path)
class Result(unittest.TextTestResult):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.successes=[]
 def addSuccess(self,test):self.successes.append(test.id());super().addSuccess(test)
with patch.object(Path,'exists',absent), patch.object(Path,'is_dir',lambda p:False if hidden(p) else original_dir(p)), patch.object(Path,'is_file',lambda p:False if hidden(p) else original_file(p)):
 suite=unittest.defaultTestLoader.discover('ops/ci',pattern='test_*.py')
 result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
output={'status':'PASS' if result.wasSuccessful() and not attempts else 'FAIL','mode':'fresh_full_operational_discovery_external_archives_absent_before_import',
        'testsRun':result.testsRun,'passed':len(result.successes),'skipped':[{'test':test.id(),'reason':reason} for test,reason in result.skipped],
        'frozenRoots':frozen,'frozenReadAttempts':attempts,'portableCyeraPassed':[name for name in result.successes if name.startswith('test_cyera')],
        'sourceRequests':0,'modelCalls':0,'repoWrites':0}
Path('/var/tmp/smp-cyera-controlled-integration-20261026/full-archive-absent.json').write_text(json.dumps(output,indent=2)+'\n')
assert result.wasSuccessful() and not attempts
