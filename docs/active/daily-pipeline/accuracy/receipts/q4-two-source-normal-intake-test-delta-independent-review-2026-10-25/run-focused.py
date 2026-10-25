from pathlib import Path
from unittest.mock import patch
import socket,sys,tempfile,unittest
R=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022');O=Path('/var/tmp/smp-q4-normal-intake-test-delta-independent-20261025');A=Path('/var/tmp/smp-next-seven-actual-40190857026-20261025/extracted')
sys.path[:0]=[str(R/'ops/ci'),str(R/'web/scripts/pipeline')];tempfile.tempdir=str(O)
from storage import LocalStore
original=LocalStore.__init__
def guarded(self,root,*a,**kw):
 p=Path(root).resolve()
 if p.is_relative_to(A):raise AssertionError('FROZEN_ARCHIVE_LOCALSTORE_DENIED')
 if not p.is_relative_to(O):raise AssertionError('TEST_LOCALSTORE_OUTSIDE_REVIEW_TEMP')
 return original(self,root,*a,**kw)
with patch.object(socket,'socket',side_effect=AssertionError('REVIEW_NETWORK_DENIED')),patch.object(LocalStore,'__init__',guarded):
 suite=unittest.defaultTestLoader.loadTestsFromName('test_q4_normal_intake');result=unittest.TextTestRunner(verbosity=2).run(suite)
 if result.testsRun!=14 or not result.wasSuccessful():raise SystemExit(1)
