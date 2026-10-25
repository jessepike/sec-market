from pathlib import Path
import sys,unittest,json
from unittest.mock import patch
root=Path('/var/tmp/smp-prn-historical-test-delta-20261025/combined-J')
sys.path[:0]=[str(root/'ops/ci'),str(root/'web/scripts/pipeline')]
original=Path.exists
archive=Path('/var/tmp/smp-listing-pagination-actual-40193925490-20261025/extracted')
def absent(path):
 if path==archive or path==archive/'archive-manifest.json':return False
 return original(path)
with patch.object(Path,'exists',absent):
 import test_prnewswire_press_list,test_prnewswire_retained_window
 suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(test_prnewswire_press_list),unittest.defaultTestLoader.loadTestsFromModule(test_prnewswire_retained_window)])
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 assert result.testsRun==26 and len(result.skipped)==13 and not result.errors and not result.failures
 print(json.dumps({'testsRun':result.testsRun,'executed':result.testsRun-len(result.skipped),'skipped':len(result.skipped),'passed':result.wasSuccessful(),'frozenPathsRenamed':False,'newRequests':0}))
