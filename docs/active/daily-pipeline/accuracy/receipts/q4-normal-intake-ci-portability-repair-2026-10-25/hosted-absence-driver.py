"""Fresh-process hosted-file absence simulation. Never move retained archives."""
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

BASE = Path('/var/tmp/smp-q4-ci-portability-20261025')
APP = BASE / 'application'
os.chdir(APP)
sys.path[:0] = [str(APP), str(APP / 'ops/ci'), str(APP / 'web/scripts/pipeline')]
import q4_intake_fixtures
q4_intake_fixtures.ARCHIVE = BASE / 'unavailable-retained-archive'
denied = []
def retained_path(value):
    name = str(value)
    return name.startswith('/var/tmp/smp-') and not name.startswith(str(BASE)) and any(
        part in name for part in ('/extracted', '/archive-', '/target-bundle'))
def audit(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)) and retained_path(args[0]):
        denied.append(str(args[0]))
        raise AssertionError('Hosted simulation forbids reading a local frozen fixture')
sys.addaudithook(audit)
real_exists, real_dir, real_file = Path.exists, Path.is_dir, Path.is_file
with patch.object(Path, 'exists', lambda path: False if retained_path(path) else real_exists(path)), \
     patch.object(Path, 'is_dir', lambda path: False if retained_path(path) else real_dir(path)), \
     patch.object(Path, 'is_file', lambda path: False if retained_path(path) else real_file(path)):
    pattern = sys.argv[1] if len(sys.argv) > 1 else 'test_*.py'
    suite = unittest.defaultTestLoader.discover(str(APP / 'ops/ci'), pattern=pattern)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
proof = {'kind': 'fresh_process_hosted_fixture_absence_simulation',
    'pattern': pattern, 'fixtureAssignedBeforeDiscovery': str(q4_intake_fixtures.ARCHIVE),
    'frozenReadsProhibited': True, 'frozenReadAttempts': denied, 'archivesMovedOrWritten': False,
    'testsRun': result.testsRun, 'skipped': len(result.skipped), 'failures': len(result.failures),
    'errors': len(result.errors), 'skipDetails': [(str(test), reason) for test, reason in result.skipped]}
print(json.dumps(proof, indent=2))
name = 'hosted-absence-focused.json' if pattern == 'test_q4_normal_intake.py' else 'hosted-absence-full.json'
(BASE / name).write_text(json.dumps(proof, indent=2) + '\n')
raise SystemExit(0 if result.wasSuccessful() and not denied else 1)
