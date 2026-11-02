"""Exact J-to-K prospective projection; all collection credit remains unevaluated."""
import copy
import json
from pathlib import Path
from contracts import canonical, digest, require
import q4_baseline_migration as q4
import three_source_qualification_origin as three

PINS = {'market.json': ('47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a',
                 206939),
 'dailyMarket.json': ('7120790449e8a4427446e2a62d69889cf651692153e6624359c50daa0379197f',
                      7696749),
 'dailyMarket.seal.json': ('6e0cec0115cd21a6165b901b91f563da5588e8e335147e05715d95ce1ba065d7',
                           276)}
KIND = 'prospective_j_to_k_three_source'


def migrate(repo, current, store):
    root = Path(repo) / 'web/scripts/migration-proofs/three-source-j-original'
    values = {}
    for name, pin in PINS.items():
        raw = (root / name).read_bytes()
        require((digest(raw), len(raw)) == pin, 'THREE_BASELINE_ORIGINAL_BYTES_DIFFER')
        values[name] = json.loads(raw)
    original, old, seal = (values[name] for name in PINS)
    three.validate_rows(original, current, json.loads(store.get(three.AUTHORITY['transition'])))
    q4.verify(repo, original, store, old)
    require(old['contractSha256'] == seal['contractSha256'] == three.J and
            seal['fileSha256'] == PINS['dailyMarket.json'][0] and seal['runId'] == old['runId'] and
            digest({key: value for key, value in old.items() if key != 'snapshotSha256'}) == old['snapshotSha256'] and
            old['coverage']['intake']['evaluated'] is False and old['coverage']['requiredTasks'] == 557 and
            old['coverage']['successfulTasks'] == 0 and old['coverage']['validUntil'] is None,
            'THREE_BASELINE_ORIGINAL_IDENTITY_OR_CREDIT_DIFFERS')
    result = copy.deepcopy(old)
    result['contractSha256'] = result['coverage']['contractSha256'] = digest(current)
    for row in result['coverage']['sources']:
        if row['sourceId'] in three.SOURCE_IDS:
            require(row['registration'] == 'candidate', 'THREE_BASELINE_ORIGINAL_REGISTRATION_DIFFERS')
            row['registration'] = 'verified'
    pointer = canonical(three.AUTHORITY['transition'])
    result['prospectiveMigration'] = {'schemaVersion': 1, 'kind': KIND, 'transitionReference': {
        'key': 'source-qualification-transitions/' + digest(current) + '.json',
        'sha256': digest(pointer), 'bytes': len(pointer)}}
    result['supersededPolicy'] = {'schemaVersion': 1, 'kind': 'daily_v2_baseline',
        'contractSha256': three.J, 'contract': original, 'snapshotSha256': old['snapshotSha256'],
        'snapshotFileSha256': PINS['dailyMarket.json'][0], 'snapshotFileBytes': PINS['dailyMarket.json'][1],
        'snapshot': old, 'sealSha256': PINS['dailyMarket.seal.json'][0],
        'sealFileBytes': PINS['dailyMarket.seal.json'][1], 'seal': seal}
    result['snapshotSha256'] = digest({key: value for key, value in result.items() if key != 'snapshotSha256'})
    return result


def verify(repo, current, store, value):
    require(canonical(migrate(repo, current, store)) == canonical(value), 'THREE_BASELINE_PROJECTION_DIFFERS')
    return {'migration': KIND, 'contractSha256': digest(current), 'coverageCredit': False}
