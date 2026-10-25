"""The one positively pinned H-to-J public migration grants no collection credit."""
import copy
import json
from pathlib import Path

from contracts import digest, require
import q4_qualification_origin as q4

PINS = {
    'market.json': ('24221c946781559c0ff3626e4e479c4647da915d0f2d7559ea88046982532c3c', 284062),
    'dailyMarket.json': ('e1945874cb3f2cb661bf67671ec2bd760ae363761e21f85e3ea8d044afd91384', 5108696),
    'dailyMarket.seal.json': ('9a2ff0562a582a05d1405ab2da8fe80fd23cf71f484775973b90ac4cdc50444b', 276),
}
KIND = 'prospective_h_to_j_q4'


def migrate(repo, current, store):
    root = Path(repo) / 'web/scripts/migration-proofs/q4-h-original'
    values = {}
    for name, pin in PINS.items():
        raw = (root / name).read_bytes()
        require((digest(raw), len(raw)) == pin, 'Q4_BASELINE_ORIGINAL_BYTES_DIFFER')
        values[name] = json.loads(raw)
    original, old, seal = (values[k] for k in PINS)
    transition = json.loads(store.get(q4.AUTHORITY['transition']))
    q4.validate_rows(original, current, transition)
    require(old['contractSha256'] == seal['contractSha256'] == q4.H and
            seal['fileSha256'] == PINS['dailyMarket.json'][0] and seal['runId'] == old['runId'] and
            digest({k: v for k, v in old.items() if k != 'snapshotSha256'}) == old['snapshotSha256'] and
            old['coverage']['intake']['evaluated'] is False and old['coverage']['requiredTasks'] == 557 and
            old['coverage']['successfulTasks'] == 0 and old['coverage']['validUntil'] is None,
            'Q4_BASELINE_ORIGINAL_IDENTITY_OR_CREDIT_DIFFERS')
    from contracts import canonical
    pointer = canonical(q4.AUTHORITY['transition'])
    result = copy.deepcopy(old)
    result['contractSha256'] = digest(current)
    result['coverage']['contractSha256'] = digest(current)
    for row in result['coverage']['sources']:
        if row['sourceId'] in q4.SOURCE_IDS:
            require(row['registration'] == 'candidate', 'Q4_BASELINE_ORIGINAL_REGISTRATION_DIFFERS')
            row['registration'] = 'verified'
    result['prospectiveMigration'] = {'schemaVersion': 1, 'kind': KIND, 'transitionReference': {
        'key': 'source-qualification-transitions/' + digest(current) + '.json',
        'sha256': digest(pointer), 'bytes': len(pointer)}}
    result['supersededPolicy'] = {'schemaVersion': 1, 'kind': 'daily_v2_baseline',
        'contractSha256': q4.H, 'contract': original, 'snapshotSha256': old['snapshotSha256'],
        'snapshotFileSha256': PINS['dailyMarket.json'][0], 'snapshotFileBytes': PINS['dailyMarket.json'][1],
        'snapshot': old, 'sealSha256': PINS['dailyMarket.seal.json'][0],
        'sealFileBytes': PINS['dailyMarket.seal.json'][1], 'seal': seal}
    result['snapshotSha256'] = digest({k: v for k, v in result.items() if k != 'snapshotSha256'})
    return result


def verify(repo, current, store, value):
    from contracts import canonical
    require(canonical(migrate(repo, current, store)) == canonical(value), 'Q4_BASELINE_PROJECTION_DIFFERS')
    return {'migration': KIND, 'contractSha256': digest(current), 'coverageCredit': False}
