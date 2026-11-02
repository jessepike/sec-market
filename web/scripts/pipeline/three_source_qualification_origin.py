"""One exact J successor; capture evidence grants inventory authority only."""
import copy
import json
from pathlib import Path

from contracts import canonical, digest, instant, require
import q4_qualification_origin as q4
from q4_primary_qualification import _blob
import cyera_primary_capture as cyera
import prnewswire_primary_capture as prn
from three_source_discovery import SOURCE_IDS, CYERA_MODE, PRN_MODE

J = q4.AUTHORITY['activatedContractSha256']
KIND = 'bounded_three_source_qualification'
PREDECESSOR_KIND = 'three_source_qualification_inventory'
TRANSITION_KIND = 'three_existing_source_qualification'
REPO = Path(__file__).resolve().parents[3]
# Filled only after root accepts both actual captures and the exact generated payload.
AUTHORITY = {'activatedContractSha256': '6cb053a5954a52f2dddf7773caeca1db436dbe5966e085ea421d911691774a68',
 'originalContract': {'key': 'contracts/47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a.json',
                      'sha256': '47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a',
                      'bytes': 206939},
 'descriptor': {'key': 'objects/43700f2e6946adfe8a61d1a2ea113182077b5ebe742e00e47db01f989152a9f5',
                'sha256': '43700f2e6946adfe8a61d1a2ea113182077b5ebe742e00e47db01f989152a9f5',
                'bytes': 1862},
 'proof': {'key': 'objects/de6bfe05ec4b1539dbe87d560b568e9e2a475a8f1475a10506b843967970c67f',
           'sha256': 'de6bfe05ec4b1539dbe87d560b568e9e2a475a8f1475a10506b843967970c67f',
           'bytes': 405227},
 'transition': {'key': 'objects/866686755b925f3ca1523dc8fc157f25608ef39b0d20b77ac52e2ad903250492',
                'sha256': '866686755b925f3ca1523dc8fc157f25608ef39b0d20b77ac52e2ad903250492',
                'bytes': 1034},
 'sources': {'cato:official:1': {'sourceIndex': 7,
                                 'originalSourceSha256': '8a03fa1c619021c0b45987ea009a2d35a4ba4cb5b418c4b87196d14af9825b9a',
                                 'sourceSha256': '72600280242b33b218c6c221b4cc9c36e2ad70f7b45256998f191ce42caea267',
                                 'url': 'https://www.prnewswire.com/news/cato-networks/',
                                 'adapterSha256': '06226996416c637c53f6348e7b5ef2ecbd35b56f88353ff5419b87cc305bfdcd',
                                 'origin': {'schemaVersion': 1,
                                            'kind': 'bounded_three_source_qualification',
                                            'originalContract': {'key': 'contracts/47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a.json',
                                                                 'sha256': '47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a',
                                                                 'bytes': 206939},
                                            'descriptor': {'key': 'objects/43700f2e6946adfe8a61d1a2ea113182077b5ebe742e00e47db01f989152a9f5',
                                                           'sha256': '43700f2e6946adfe8a61d1a2ea113182077b5ebe742e00e47db01f989152a9f5',
                                                           'bytes': 1862},
                                            'proof': {'key': 'objects/de6bfe05ec4b1539dbe87d560b568e9e2a475a8f1475a10506b843967970c67f',
                                                      'sha256': 'de6bfe05ec4b1539dbe87d560b568e9e2a475a8f1475a10506b843967970c67f',
                                                      'bytes': 405227},
                                            'sourceResultIndex': 0,
                                            'originalSourceSha256': '8a03fa1c619021c0b45987ea009a2d35a4ba4cb5b418c4b87196d14af9825b9a',
                                            'proposedAdapterSha256': '06226996416c637c53f6348e7b5ef2ecbd35b56f88353ff5419b87cc305bfdcd',
                                            'inventoryManifest': {'key': 'objects/48fc31044ab37a5f9f47fa19066b72668eaabc72a850e24b5f7580b6db438362',
                                                                  'sha256': '48fc31044ab37a5f9f47fa19066b72668eaabc72a850e24b5f7580b6db438362',
                                                                  'bytes': 19165}},
                                 'change': {'sourceIndex': 7,
                                            'sourceId': 'cato:official:1',
                                            'originalSourceSha256': '8a03fa1c619021c0b45987ea009a2d35a4ba4cb5b418c4b87196d14af9825b9a',
                                            'sourceSha256': '72600280242b33b218c6c221b4cc9c36e2ad70f7b45256998f191ce42caea267'}},
             'chainguard:official:1': {'sourceIndex': 8,
                                       'originalSourceSha256': '80eca52f173a73bc1baeab6b9a5b23f550dde1fdd58c8afd55835ee8ad05ead9',
                                       'sourceSha256': 'f524de08592de3311bb06d85f6d7ce1e63f728fb9305f66b1ceaa82b0a704f00',
                                       'url': 'https://www.prnewswire.com/news/chainguard/',
                                       'adapterSha256': '2a8288bc725ece9f5f1593b14fe3f5a1580fddef6a8f1b8ee1f270a87531d778',
                                       'origin': {'schemaVersion': 1,
                                                  'kind': 'bounded_three_source_qualification',
                                                  'originalContract': {'key': 'contracts/47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a.json',
                                                                       'sha256': '47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a',
                                                                       'bytes': 206939},
                                                  'descriptor': {'key': 'objects/43700f2e6946adfe8a61d1a2ea113182077b5ebe742e00e47db01f989152a9f5',
                                                                 'sha256': '43700f2e6946adfe8a61d1a2ea113182077b5ebe742e00e47db01f989152a9f5',
                                                                 'bytes': 1862},
                                                  'proof': {'key': 'objects/de6bfe05ec4b1539dbe87d560b568e9e2a475a8f1475a10506b843967970c67f',
                                                            'sha256': 'de6bfe05ec4b1539dbe87d560b568e9e2a475a8f1475a10506b843967970c67f',
                                                            'bytes': 405227},
                                                  'sourceResultIndex': 1,
                                                  'originalSourceSha256': '80eca52f173a73bc1baeab6b9a5b23f550dde1fdd58c8afd55835ee8ad05ead9',
                                                  'proposedAdapterSha256': '2a8288bc725ece9f5f1593b14fe3f5a1580fddef6a8f1b8ee1f270a87531d778',
                                                  'inventoryManifest': {'key': 'objects/57d56ae30167d1c0d6fbcc669724f0dd2e9304b5baa8d908e0c9652291627e02',
                                                                        'sha256': '57d56ae30167d1c0d6fbcc669724f0dd2e9304b5baa8d908e0c9652291627e02',
                                                                        'bytes': 7904}},
                                       'change': {'sourceIndex': 8,
                                                  'sourceId': 'chainguard:official:1',
                                                  'originalSourceSha256': '80eca52f173a73bc1baeab6b9a5b23f550dde1fdd58c8afd55835ee8ad05ead9',
                                                  'sourceSha256': 'f524de08592de3311bb06d85f6d7ce1e63f728fb9305f66b1ceaa82b0a704f00'}},
             'cyera:official:1': {'sourceIndex': 19,
                                  'originalSourceSha256': '6121c066ba4624d6406a3dc586d6a4cea3adcf38ff09275b9296d1e7083da6f0',
                                  'sourceSha256': 'd0bda0397e1354436008e5376fe2647ee9ff2ae2789ced6dfe32d4f9b10b0edf',
                                  'url': 'https://www.cyera.com/newsroom/press-releases',
                                  'adapterSha256': '557c8739d5beff5b9797daaaac9a8fd35af33e366c00c9ea9b7c17259166e02c',
                                  'origin': {'schemaVersion': 1,
                                             'kind': 'bounded_three_source_qualification',
                                             'originalContract': {'key': 'contracts/47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a.json',
                                                                  'sha256': '47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a',
                                                                  'bytes': 206939},
                                             'descriptor': {'key': 'objects/43700f2e6946adfe8a61d1a2ea113182077b5ebe742e00e47db01f989152a9f5',
                                                            'sha256': '43700f2e6946adfe8a61d1a2ea113182077b5ebe742e00e47db01f989152a9f5',
                                                            'bytes': 1862},
                                             'proof': {'key': 'objects/de6bfe05ec4b1539dbe87d560b568e9e2a475a8f1475a10506b843967970c67f',
                                                       'sha256': 'de6bfe05ec4b1539dbe87d560b568e9e2a475a8f1475a10506b843967970c67f',
                                                       'bytes': 405227},
                                             'sourceResultIndex': 2,
                                             'originalSourceSha256': '6121c066ba4624d6406a3dc586d6a4cea3adcf38ff09275b9296d1e7083da6f0',
                                             'proposedAdapterSha256': '557c8739d5beff5b9797daaaac9a8fd35af33e366c00c9ea9b7c17259166e02c',
                                             'inventoryManifest': {'key': 'objects/c6cbdd1280cc9ccf893903e55c9499dc61ce1894fee225f998c043116cec22ca',
                                                                   'sha256': 'c6cbdd1280cc9ccf893903e55c9499dc61ce1894fee225f998c043116cec22ca',
                                                                   'bytes': 7652}},
                                  'change': {'sourceIndex': 19,
                                             'sourceId': 'cyera:official:1',
                                             'originalSourceSha256': '6121c066ba4624d6406a3dc586d6a4cea3adcf38ff09275b9296d1e7083da6f0',
                                             'sourceSha256': 'd0bda0397e1354436008e5376fe2647ee9ff2ae2789ced6dfe32d4f9b10b0edf'}}}}


def is_successor(contract):
    return AUTHORITY is not None and digest(contract) == AUTHORITY['activatedContractSha256']


def validate_source(source):
    expected = AUTHORITY.get('sources', {}).get(source.get('id')) if AUTHORITY is not None else None
    require(expected is not None and digest(source) == expected['sourceSha256'],
            'THREE_SOURCE_NORMAL_ROW_NOT_AUTHORIZED')
    return source


def _object(store, reference):
    return json.loads(_blob(store, reference,
        r'(?:objects/[a-f0-9]{64}|contracts/[a-f0-9]{64}\.json|ci/source-probe-runs/[0-9]+-[0-9]+\.json)'))


def validate_rows(original, current, transition):
    require(AUTHORITY is not None and digest(original) == J and is_successor(current) and
            digest(transition) == AUTHORITY['transition']['sha256'], 'THREE_SOURCE_EXACT_POLICY_PAIR_REQUIRED')
    expected_transition = {'schemaVersion': 1, 'kind': TRANSITION_KIND,
                          'originalContract': AUTHORITY['originalContract'],
                          'activatedContractSha256': digest(current),
                          'changes': [AUTHORITY['sources'][sid]['change'] for sid in SOURCE_IDS]}
    require(canonical(transition) == canonical(expected_transition), 'THREE_SOURCE_TRANSITION_DIFFERS')
    require(len(original['sources']) == len(current['sources']), 'THREE_SOURCE_SOURCE_COUNT_DIFFERS')
    forward, inverse = copy.deepcopy(original), copy.deepcopy(current)
    for sid in SOURCE_IDS:
        authority = AUTHORITY['sources'][sid]
        index = authority['sourceIndex']
        old, new = original['sources'][index], current['sources'][index]
        require(old['id'] == new['id'] == sid and digest(old) == authority['originalSourceSha256'] and
                digest(new) == authority['sourceSha256'], 'THREE_SOURCE_POSITION_OR_ROW_DIFFERS')
        adapter = {**old, 'kind': 'html_index', 'registration': 'verified', 'url': authority['url'],
                   'htmlCompleteness': CYERA_MODE if sid == 'cyera:official:1' else PRN_MODE}
        require(digest(adapter) == authority['adapterSha256'] and
                new == {**adapter, 'qualificationOrigin': authority['origin']}, 'THREE_SOURCE_PATCH_DIFFERS')
        forward['sources'][index] = copy.deepcopy(new)
        inverse['sources'][index] = copy.deepcopy(old)
    require(canonical(forward) == canonical(current) and canonical(inverse) == canonical(original),
            'THREE_SOURCE_WHOLE_FORWARD_OR_INVERSE_DIFFERS')
    return inverse


def inverse_policy(current, store):
    require(is_successor(current), 'THREE_SOURCE_POLICY_NOT_AUTHORIZED')
    original = _object(store, AUTHORITY['originalContract'])
    require(digest(original) == J, 'THREE_SOURCE_ORIGINAL_J_DIFFERS')
    pointer = store.read('source-qualification-transitions/' + digest(current) + '.json')
    require(pointer == AUTHORITY['transition'], 'THREE_SOURCE_TRANSITION_POINTER_DIFFERS')
    return validate_rows(original, current, _object(store, pointer))


def _audit(pin):
    path = REPO / pin['path']
    require(not path.is_symlink() and path.resolve().is_relative_to(REPO), 'THREE_SOURCE_AUDIT_PATH_INVALID')
    raw = path.read_bytes()
    require(len(raw) == pin['bytes'] and digest(raw) == pin['sha256'], 'THREE_SOURCE_ACTUAL_AUDIT_DIFFERS')
    return json.loads(raw)


def derive_proof(original, store, descriptor):
    require(digest(original) == J and type(descriptor) is dict and set(descriptor) ==
            {'schemaVersion', 'kind', 'originalContract', 'captures'} and
            type(descriptor['schemaVersion']) is int and descriptor['schemaVersion'] == 1 and
            descriptor['kind'] == KIND and len(descriptor['captures']) == 2,
            'THREE_SOURCE_DESCRIPTOR_INVALID')
    require(descriptor['originalContract']['sha256'] == J and
            canonical(_object(store, descriptor['originalContract'])) == canonical(original),
            'THREE_SOURCE_DESCRIPTOR_J_DIFFERS')
    streams, captures = {}, []
    for capture, operation, count in zip(descriptor['captures'], (cyera, prn), (1, 2)):
        require(type(capture) is dict and set(capture) == {'operation', 'record', 'plan', 'outerIdentity', 'audit'} and
                capture['operation'] == operation.OPERATION, 'THREE_SOURCE_CAPTURE_DESCRIPTOR_INVALID')
        audit = _audit(capture['audit'])
        require(set(capture['outerIdentity']) == {'githubRunId', 'githubRunAttempt', 'githubEventName', 'githubRef', 'appRevision'},
                'THREE_SOURCE_OUTER_IDENTITY_SHAPE_INVALID')
        record = _object(store, capture['record'])
        require(all(type(record.get(key)) is type(value) and record[key] == value
                    for key, value in capture['outerIdentity'].items()) and
                record.get('contractSha256') == J and record.get('checkpointProfile') == 'source_probe' and
                all(record.get(key) is False for key in ('semanticAdmission', 'coverageCredit')) and
                record.get('executionCompleted') is True and record.get('facts') == [] and
                all(type(record.get(key)) is int and record[key] == 0 for key in
                    ('modelCalls', 'sourceChecksCredited', 'qualifiedSources')),
                'THREE_SOURCE_ACTUAL_OUTER_IDENTITY_DIFFERS')
        raw = _blob(store, capture['plan'])
        normalized = operation.validate_plan(original, store, raw)
        report = record['diagnostic']
        replay = operation.verify_report(original, store, raw, report)
        require(replay['proposalEvidenceComplete'] is True and replay['acceptedSamples'] == count,
                'THREE_SOURCE_ACTUAL_SAMPLE_INCOMPLETE')
        audit_entry = audit['consumedClosure']['state/' + capture['record']['key']]
        require(audit['actualRunId'] == record['githubRunId'] and audit['appRevision'] == record['appRevision'] and
                audit['selectedPlanSha256'] == digest(raw) and audit['reportVerifier'] == replay and
                audit['consumedFrozenInputsUnchanged'] is True and audit['sourceQualificationProven'] is False and
                all(audit_entry[key] == capture['record'][key] for key in ('sha256', 'bytes')),
                'THREE_SOURCE_ACTUAL_AUDIT_JOIN_DIFFERS')
        captures.append({'operation': operation.OPERATION, 'record': capture['record'], 'plan': capture['plan'],
                         'outerIdentity': capture['outerIdentity'], 'audit': capture['audit'],
                         'reportSha256': digest(report), 'checkedAt': report['checkedAt'], 'acceptedSamples': count})
        for stream, result in zip(normalized['streams'], report['results']):
            sid = stream['sourceId']
            require(sid in SOURCE_IDS and sid not in streams and result['sourceId'] == sid and result['accepted'] is True,
                    'THREE_SOURCE_ACTUAL_RESULT_SOURCE_DIFFERS')
            items = stream.get('knownEvidenceUnion', stream['items'])
            require(type(items) is list and len(items) == len(set(items)), 'THREE_SOURCE_UNION_INVALID')
            streams[sid] = {'sourceId': sid, 'originalAsOf': stream['asOf'], 'stream': copy.deepcopy(stream),
                            'items': sorted(items), 'sample': copy.deepcopy(result)}
    require(set(streams) == set(SOURCE_IDS), 'THREE_SOURCE_CAPTURE_SOURCE_SET_DIFFERS')
    return {'schemaVersion': 1, 'kind': KIND, 'originalContractSha256': J,
            'descriptorSha256': digest(descriptor), 'captures': captures,
            'streams': [streams[sid] for sid in SOURCE_IDS],
            'completedAt': max((row['checkedAt'] for row in captures), key=instant),
            'authority': 'inventory_only', 'coverageCredit': False, 'semanticAdmission': False,
            'sourceChecksCredited': 0, 'modelCalls': 0, 'facts': []}


def _proof(original, store):
    require(AUTHORITY is not None, 'THREE_SOURCE_AUTHORITY_UNAVAILABLE')
    descriptor = _object(store, AUTHORITY['descriptor'])
    proof = _object(store, AUTHORITY['proof'])
    key = digest({'original': original, 'descriptor': descriptor, 'proof': proof})
    cache = getattr(store, '_three_source_proof_replays', None)
    if cache is None:
        cache = {}
        store._three_source_proof_replays = cache
    if key not in cache:
        references, reads = {}, {}
        class Recording:
            def __getattr__(self, name): return getattr(store, name)
            def get(self, ref):
                raw = store.get(ref)
                require(len(raw) == ref['bytes'] and digest(raw) == ref['sha256'],
                        'THREE_SOURCE_REPLAY_REFERENCE_DIFFERS')
                references[digest(ref)] = copy.deepcopy(ref)
                return raw
            def read(self, name):
                value = store.read(name)
                reads[name] = digest(value)
                return value
        require(canonical(proof) == canonical(derive_proof(original, Recording(), descriptor)),
                'THREE_SOURCE_QUALIFICATION_PROOF_DIFFERS')
        cache[key] = (list(references.values()), reads)
    references, reads = cache[key]
    for ref in references:
        raw = store.get(ref)
        require(len(raw) == ref['bytes'] and digest(raw) == ref['sha256'], 'THREE_SOURCE_REPLAY_REFERENCE_DIFFERS')
    for name, sha in reads.items():
        require(digest(store.read(name)) == sha, 'THREE_SOURCE_REPLAY_METADATA_DIFFERS')
    for capture in descriptor['captures']:
        _audit(capture['audit'])
    return copy.deepcopy(proof)


def predecessors(contract, source_id, store, before_time=None):
    require(source_id in SOURCE_IDS, 'THREE_SOURCE_ORIGIN_SOURCE_NOT_ALLOWED')
    value = {'kind': PREDECESSOR_KIND, 'sourceId': source_id,
             'qualificationOrigin': AUTHORITY['sources'][source_id]['origin'], 'transition': AUTHORITY['transition']}
    resolve(value, contract, source_id, store, before_time)
    return [value]


def resolve(value, contract, source_id, store, before_time=None):
    original = inverse_policy(contract, store)
    require(source_id in SOURCE_IDS and type(value) is dict and set(value) ==
            {'kind', 'sourceId', 'qualificationOrigin', 'transition'} and
            value['kind'] == PREDECESSOR_KIND and value['sourceId'] == source_id and
            canonical(value['transition']) == canonical(AUTHORITY['transition']), 'THREE_SOURCE_PREDECESSOR_INVALID')
    source = next(row for row in contract['sources'] if row['id'] == source_id)
    authority = AUTHORITY['sources'][source_id]
    require(canonical(source['qualificationOrigin']) == canonical(value['qualificationOrigin']) ==
            canonical(authority['origin']), 'THREE_SOURCE_PREDECESSOR_ORIGIN_DIFFERS')
    proof = _proof(original, store)
    index = SOURCE_IDS.index(source_id)
    stream = proof['streams'][index]
    expected = {'schemaVersion': 1, 'kind': PREDECESSOR_KIND, 'sourceId': source_id,
                'descriptor': AUTHORITY['descriptor'], 'proof': AUTHORITY['proof'],
                'sourceResultIndex': index, 'streamSha256': digest(stream), 'items': stream['items']}
    manifest = _object(store, authority['origin']['inventoryManifest'])
    require(canonical(manifest) == canonical(expected), 'THREE_SOURCE_FULL_INVENTORY_MANIFEST_DIFFERS')
    if before_time is not None:
        require(instant(proof['completedAt']) <= instant(before_time), 'THREE_SOURCE_PREDECESSOR_FUTURE')
    dates = {row['url']: row['calendarDay'] for row in stream['stream']['records']
             if row.get('calendarDay') is not None}
    for seed in stream['stream'].get('knownSeedsOutsideObservedList', []):
        require(seed['calendarWindowState'] == 'older_calendar_day' and seed['url'] in stream['items'],
                'THREE_SOURCE_SEED_DATE_CONTEXT_DIFFERS')
        dates[seed['url']] = seed['shape']['publicationCalendarDay']
    require(set(dates).issubset(stream['items']), 'THREE_SOURCE_DATE_INVENTORY_DIFFERS')
    return {'sourceId': source_id, 'items': list(stream['items']), 'itemDates': dates,
            'originalAsOf': stream['originalAsOf'], 'completedAt': proof['completedAt'],
            'authority': 'inventory_only', 'provenance': [{'kind': KIND, 'descriptor': AUTHORITY['descriptor'],
                'proof': AUTHORITY['proof'], 'inventoryManifest': authority['origin']['inventoryManifest'],
                'sourceResultIndex': index, 'originalContract': AUTHORITY['originalContract']}]}


def scheduling_view(found, contract, source, store, before_time):
    """Carry old publication hints for absent URLs, without renewing their observation clocks."""
    from three_source_discovery import matches
    if not matches(source):
        return found
    validate_source(source)
    prior = predecessors(contract, source['id'], store, before_time)
    retained = resolve(prior[0], contract, source['id'], store, before_time)
    # A fresh row owns its signature, including a new unknown or anomalous value.
    dates = {url: day for url, day in retained['itemDates'].items() if url not in found['items']}
    dates.update(found.get('itemModified', {}))
    return {**found, 'itemModified': dates}
