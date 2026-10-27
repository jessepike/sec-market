"""Seal this offline activation handback after the affected tests finish."""
import gzip
import hashlib
import json
from pathlib import Path
import re
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[5]
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
def result(name):
    raw = (OUT / name).read_text()
    run = re.search(r'Ran (\d+) tests? in ([\d.]+)s', raw)
    assert run
    return {'log': name, 'tests': int(run[1]), 'seconds': float(run[2]),
            'passed': raw.rstrip().endswith('OK'), 'skips': len(re.findall(r'\.\.\. skipped ', raw)),
            'sha256': sha(raw.encode())}

final = result('q4-cyera-affected-green-v2.log')
assert final['passed'] and final['tests'] == 37 and final['skips'] == 0
focused = result('focused-tests.log')
assert focused['passed'] and focused['tests'] == 23 and focused['skips'] == 0
first = result('q4-cyera-affected-green.log')
assert not first['passed'] and first['tests'] == 37
red = result('q4-historical-selected-red.log')
assert not red['passed'] and red['tests'] == 1
probe = result('q4-quiet-targeted-diagnostic.log')
assert probe['passed'] and probe['tests'] == 1
preflight = json.loads((OUT / 'current-actual-preflight.json').read_bytes())
assert preflight['status'] == 'PASS' and preflight['sourceRequests'] == preflight['archiveWrites'] == 0
protection = json.loads((OUT / 'tracked-protection.json').read_bytes())
assert protection['unexpectedProtectedChanges'] == []
assert set(protection['changedTrackedFiles']) == {'contracts/source-qualification-probes.json', 'ops/ci/test_q4_normal_intake.py'}
original = json.loads(gzip.decompress((OUT / 'tracked-before.json.gz').read_bytes()))
dependencies = {}
for name, pin in original['files'].items():
    if name.startswith(('ops/ci/', 'web/scripts/pipeline/', 'contracts/')) or name.endswith((
            '/cyera-primary-capture-plan-2026-10-25.json', '/cyera-retained-56-card-inventory.csv',
            '/narrow-listing-pagination-actual-source-review-2026-10-25.json')):
        expected = protection['changedTrackedFiles'].get(name, {}).get('after', pin)
        raw = (ROOT / name).read_bytes()
        assert {'sha256': sha(raw), 'bytes': len(raw)} == expected
        dependencies[name] = expected
save('source-dependencies.json', {'authority': 'complete tracked source/contract dependency pins after source-frozen run',
     'pins': dependencies, 'count': len(dependencies),
     'originalTree': original['head'], 'expectedOwnedChanges': list(protection['changedTrackedFiles'])})
test = 'ops/ci/test_q4_normal_intake.py'
assert sha((ROOT / test).read_bytes()) == '21e93d92d0a54ef5faa5529af4c8a5001db207ad508503903fc2c38738383114'
download = Path(preflight['downloadProof']['path']).read_bytes()
assert sha(download) == preflight['downloadProof']['sha256']
(OUT / 'current-archive-download-proof.json').write_bytes(download)
summary = {'status': 'PASS', 'sealedAt': datetime.now(timezone.utc).isoformat(),
           'scope': 'exact reviewed Cyera one-primary plan selection and one historical Q4 fixture test',
           'baseHead': original['head'], 'focused': focused, 'affectedFinal': final,
           'preservedFailures': [red, first], 'isolatedQuietMethodDiagnostic': probe,
           'firstAffectedFailure': {'attribute': 'assertEqu', 'file': test,
               'sourceSha256ObservedBeforeFreshRerun': '21e93d92d0a54ef5faa5529af4c8a5001db207ad508503903fc2c38738383114',
               'cause': 'Unproven; fresh isolated bytecode-prefix run passes unchanged source. First error retained.'},
           'finalCommand': 'PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/var/tmp/smp-cyera-activation-fresh-bytecode-20261027 PYTHONPATH=ops/ci:web/scripts/pipeline python3 -m unittest -v test_q4_normal_intake test_cyera_press_list test_cyera_primary_capture',
           'currentActualPlanPreflight': {k: preflight[k] for k in ('status', 'acknowledgedArchiveCommit',
               'manifestSha256', 'manifestFiles', 'readSetFiles', 'selectedPlanRawSha256', 'policyCanonicalSha256')},
           'sourceRequests': 0, 'modelCalls': 0, 'documentReservations': 0, 'gateAttempts': 0,
           'coverageCredit': False, 'sourceQualified': False, 'sourceDependencies': len(dependencies),
           'runtimeSourcePolicyChanged': False, 'runtimeGuardsChanged': False,
           'activePlanSelected': True, 'originalDisabledBytesPreserved': True,
           'committed': False, 'pushed': False, 'dispatched': False, 'published': False}
save('verification-summary.json', summary)
pins = [{'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size}
        for path in sorted(OUT.rglob('*')) if path.is_file() and path.name != 'receipt-index.json']
save('receipt-index.json', {'schemaVersion': 1, 'files': pins, 'fileCount': len(pins),
                           'sourceRequests': 0, 'coverageCredit': False})
print(json.dumps({'status': summary['status'], 'tests': final['tests'], 'skips': final['skips'],
                  'receiptFiles': len(pins), 'sourceDependencies': len(dependencies)}))
