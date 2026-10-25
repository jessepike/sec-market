"""Retain completed offline tests and verify the exact pending-only file set."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import shutil
import subprocess

REPO = Path(__file__).resolve().parents[6]
OUT = Path(__file__).parent
SCRATCH = Path('/var/tmp/smp-priority-two-corrections-20261025')
BASE = '2387abb41069f3a74a005468d91e5401d97089ff'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    raw = Path(path).read_bytes()
    return {'sha256': sha(raw), 'bytes': len(raw)}


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


assembly = json.loads((SCRATCH / 'assembly.json').read_bytes())
assert assembly['baseCommit'] == BASE
owned = assembly['exactOwnedOverlay']
for name, expected in owned.items():
    assert pin(REPO / name) == expected, name
    assert pin(Path(assembly['applicationRoot']) / name) == expected, name

tracked_changes = set(git('diff', '--name-only', BASE).decode().splitlines())
expected_changes = {
    'contracts/factual-corrections.json',
    'web/src/data/tracker/factualCorrectionPolicy.json',
    'ops/ci/test_prnewswire_retained_window.py',
    'ops/ci/test_publisher_disclosure_correction.py',
    'ops/ci/test_q4_initial_data_capture.py',
    'ops/ci/test_q4_normal_intake.py',
    'ops/ci/test_q4_primary_qualification.py',
    'ops/ci/test_s1_exact_filing_transport.py',
}
assert tracked_changes == expected_changes
unchanged = 0
for entry in git('ls-tree', '-r', '-z', BASE).split(b'\0'):
    if not entry:
        continue
    metadata, name_bytes = entry.split(b'\t', 1)
    mode, kind, object_id = metadata.split()
    assert kind == b'blob'
    name = os.fsdecode(name_bytes)
    if name in tracked_changes:
        continue
    path = REPO / name
    raw = os.fsencode(os.readlink(path)) if mode == b'120000' else path.read_bytes()
    actual = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert actual == object_id.decode(), name
    unchanged += 1

old_raw = git('show', BASE + ':contracts/factual-corrections.json')
new_raw = (REPO / 'contracts/factual-corrections.json').read_bytes()
decoder = json.JSONDecoder()


def literal_groups(raw):
    text = raw.decode()
    offset = text.index('[', text.index('"groups"')) + 1
    result = []
    while True:
        while text[offset].isspace() or text[offset] == ',':
            offset += 1
        if text[offset] == ']':
            return result
        _, end = decoder.raw_decode(text, offset)
        result.append(text[offset:end].encode())
        offset = end


old_blocks, new_blocks = literal_groups(old_raw), literal_groups(new_raw)
assert len(old_blocks) == 6 and len(new_blocks) == 8
assert new_blocks[:6] == old_blocks
readiness = json.loads((OUT / 'actual-source-and-old-admission-readiness.json').read_bytes())
for name, expected in readiness['archiveInputSeals'].items():
    path = Path(name)
    assert pin(path) == {key: expected[key] for key in ('sha256', 'bytes')}, name
    assert path.stat().st_mtime_ns == expected['mtimeNs'], name
archive = Path('/var/tmp/smp-q4-ordinary-j-40199860540-20261025/capture/extracted')
manifest = archive / 'archive-manifest.json'
assert pin(manifest) == {key: readiness['manifest'][key] for key in ('sha256', 'bytes')}
assert manifest.stat().st_mtime_ns == readiness['manifest']['mtimeNs']

copies = {
    'assembly.json': SCRATCH / 'assembly.json',
    'hosted-absence-driver.py': SCRATCH / 'hosted-absence-driver.py',
    'hosted-absence-full.json': SCRATCH / 'hosted-absence-full.json',
    'render-comparison.json': SCRATCH / 'render-comparison.json',
}
for name, source in copies.items():
    shutil.copyfile(source, OUT / name)
    assert pin(source) == pin(OUT / name)

logs = {
    'focused-tests.log': Path('/var/tmp/smp-priority-corrections-focused-20261025.log'),
    'full-ops-present.log': Path('/var/tmp/smp-priority-corrections-full-present-20261025.log'),
    'full-ops-absent.log': Path('/var/tmp/smp-priority-corrections-full-absent-20261025.log'),
    'initial-test-diagnostic.log': Path('/var/tmp/smp-priority-corrections-focused-initial-20261025.log'),
    'build.log': SCRATCH / 'build.log',
    'render-production.log': SCRATCH / 'render-production.log',
    'render-local.log': SCRATCH / 'render-local.log',
}
log_index = {}
for name, source in logs.items():
    raw = source.read_bytes()
    compressed = gzip.compress(raw, mtime=0)
    assert gzip.decompress(compressed) == raw
    target = OUT / (name + '.gz')
    target.write_bytes(compressed)
    log_index[name] = {'originalPath': str(source), 'raw': pin(source),
                       'retainedPath': target.name, 'gzip': pin(target),
                       'roundtripExact': True}

present = logs['full-ops-present.log'].read_text()
absent = json.loads((OUT / 'hosted-absence-full.json').read_bytes())
focused = logs['focused-tests.log'].read_text()
assert 'Ran 972 tests' in present and present.rstrip().endswith('OK')
assert 'Ran 98 tests' in focused and focused.rstrip().endswith('OK')
assert (absent['testsRun'], absent['skipped'], absent['failures'], absent['errors']) == (972, 59, 0, 0)
assert absent['frozenReadAttempts'] == []
build = logs['build.log'].read_text()
assert '{"complete":true,"required":80,"verified":80,"blockers":0,"drift":0}' in build
render = json.loads((OUT / 'render-comparison.json').read_bytes())
assert len(render['rows']) == 4 and render['allComparedPixelsUnchanged']
for row in render['rows']:
    assert pin(row['path']) == {key: row[key] for key in ('sha256', 'bytes')}
    assert row['changedPixels'] == 0 and row['byteIdentical']
parity = json.loads((OUT / 'javascript-policy-parity.json').read_bytes())
assert parity['groups'] == 8 and parity['newAdmissions'] == 0
assert parity['validation']['enabled'] is False

verification = {
    'schemaVersion': 1, 'verdict': 'PASS_PENDING_PREPARATION_ONLY',
    'baseCommit': BASE, 'baseTree': git('rev-parse', BASE + '^{tree}').decode().strip(),
    'exactOwnedFiles': owned, 'trackedChanges': sorted(tracked_changes),
    'unchangedOriginalGitBlobs': unchanged, 'allOtherTrackedBytesExact': True,
    'oldSixLiteralGroupBlocks': [pin_value for pin_value in
        ({'sha256': sha(raw), 'bytes': len(raw)} for raw in old_blocks)],
    'oldSixBlocksByteIdentical': True,
    'sourceManifestSha256': readiness['manifest']['sha256'],
    'consultedArchiveSeals': len(readiness['archiveInputSeals']),
    'consultedArchiveBytesSizeMtimeUnchanged': True,
    'actualLedgerUnchanged': readiness['actualFrozenLedger'],
    'actualGateLedgerUnchanged': readiness['actualGateLedger'],
    'oldAdmissionsReplayed': len(readiness['oldSixAdmissionsUnchanged']),
    'newAdmissions': 0, 'sourceRequests': 0, 'modelRequests': 0,
    'sourceWrites': 0, 'dispatches': 0, 'gitMutations': 0,
    'validation': {'affected': {'tests': 98, 'skips': 0},
        'fullPresent': {'tests': 972, 'skips': 0},
        'fullAbsent': {'tests': 972, 'passed': 913, 'skips': 59, 'frozenReadAttempts': []},
        'build': {'requiredSec': 80, 'verifiedSec': 80, 'blockers': 0, 'drift': 0},
        'renders': {'actualImages': 4, 'changedPixelsAgainstPrior': 0},
        'javascriptPythonPolicyParity': True},
    'logs': log_index,
    'limits': [
        'The initial diagnostic log contains corrected test-fixture/UTC-Z mistakes; it is superseded by the final passing logs.',
        'Hypothetical review clocks and temporary synthetic model results are not semantic admissions.',
        'Actual independent model review waits for naturally renewed UTC capacity; no fallback is selected.',
        'Full archive authentication is inherited from the actual J audit; 67 consulted entries and its manifest are independently rechecked.',
        'Normal collection and publication retain their own charges and guards.',
    ],
}
(OUT / 'verification.json').write_text(json.dumps(verification, indent=2) + '\n')
index = {path.name: pin(path) for path in sorted(OUT.iterdir()) if path.is_file() and path.name != 'receipt-index.json'}
(OUT / 'receipt-index.json').write_text(json.dumps({'schemaVersion': 1, 'files': index}, indent=2) + '\n')
print(json.dumps({'verdict': verification['verdict'], 'retainedFiles': len(index),
                  'unchangedGitBlobs': unchanged, 'verification': pin(OUT / 'verification.json'),
                  'receiptIndex': pin(OUT / 'receipt-index.json')}))
