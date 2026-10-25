"""One exact H-to-J Q4 transition. Qualification supplies inventory only."""
import copy
import json

from contracts import canonical, digest, instant, require
import q4_retained_primary_template as retained

H = '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db'
KIND = 'bounded_q4_press_qualification'
PREDECESSOR_KIND = 'q4_qualification_inventory'
TRANSITION_KIND = 'two_q4_press_source_qualification'
SOURCE_IDS = ('jfrog:official:1', 'rapid7:official:1')
URLS = {
    'jfrog:official:1': 'https://investors.jfrog.com/feed/PressRelease.svc/GetPressReleaseList?LanguageId=1&bodyType=0&pressReleaseDateFilter=3&categoryId=00000000-0000-0000-0000-000000000000&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=-1&excludeSelection=1',
    'rapid7:official:1': 'https://investors.rapid7.com/feed/PressRelease.svc/GetPressReleaseList?LanguageId=1&bodyType=0&pressReleaseDateFilter=3&categoryId=1cb807d2-208f-4bc3-9133-6a9ad45ac3b0&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=-1&excludeSelection=1',
}
# Populated only from the authenticated actual proof and reviewed exact policy.
AUTHORITY = {'activatedContractSha256': '47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a', 'originalContract': {'key': 'contracts/8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db.json', 'sha256': '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db', 'bytes': 204449}, 'transition': {'key': 'objects/d573ed7951f03610e630df97964e2498093a96a53686d6be885cf8019549bf67', 'sha256': 'd573ed7951f03610e630df97964e2498093a96a53686d6be885cf8019549bf67', 'bytes': 1002}, 'descriptor': {'key': 'objects/0223ae2af8878aecf73b5b6a5665d7840d592e7e299470e44bd31cedf7a12c1b', 'sha256': '0223ae2af8878aecf73b5b6a5665d7840d592e7e299470e44bd31cedf7a12c1b', 'bytes': 6105}, 'proof': {'key': 'objects/eb82ff6f74ffd0461a74cc6590e3cb1ef52adae2be698f4421b904c79d25d714', 'sha256': 'eb82ff6f74ffd0461a74cc6590e3cb1ef52adae2be698f4421b904c79d25d714', 'bytes': 7571}, 'actualProof': {'githubRunId': '40188161705', 'githubRunAttempt': 1, 'githubEventName': 'workflow_dispatch', 'githubRef': 'refs/heads/main', 'appRevision': 'b7c7841ab36c4cf04646978493ce74e1e542a2b9', 'record': {'key': 'ci/source-probe-runs/40188161705-1.json', 'sha256': '093fba7150d21255af66a563207b3c3f0490bae36873376203c43d5415be6897', 'bytes': 713736}, 'artifact': {'id': 12597132303, 'digest': 'sha256:2fd5b94683ea1473171d14bb9241364d9735ac8dbcb69b79c4cab2ad65e1d008', 'size_in_bytes': 134691}, 'archive': {'commit': 'd2efafcb8a68d7330e4b700613b29f18b9892346', 'manifestSha256': 'bb1c3da1399e89341badf80bba8642d7892f32ce2030bd57fc1d4c165e383e4d', 'manifestBytes': 9944331}, 'plan': {'bytes': 4211, 'key': 'objects/3a25e8e262b51fbf6f872c8655b25c9d255cf52b32ca0e9c4afa73d78893fbd4', 'sha256': '3a25e8e262b51fbf6f872c8655b25c9d255cf52b32ca0e9c4afa73d78893fbd4'}, 'planCanonicalSha256': '3b7fc7c4de41c68471d4343f103e7e5ee705e5a4a51f760f5387e34a49a660ee', 'audit': {'path': 'docs/active/daily-pipeline/accuracy/q4-primary-qualification-actual-source-review-2026-10-25.json', 'sha256': '3f133bc05fc7e3964dd3e0717b9a9cd0a3c859b0472b57bb00e6cd80615378bf', 'bytes': 53594}}, 'sources': {'jfrog:official:1': {'sourceIndex': 34, 'sourceSha256': '2d3fb9840dab3c870b7bcd8bf914a39c3c5c383770de39b252ea11d17db43113', 'origin': {'schemaVersion': 1, 'kind': 'bounded_q4_press_qualification', 'originalContract': {'key': 'contracts/8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db.json', 'sha256': '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db', 'bytes': 204449}, 'descriptor': {'key': 'objects/0223ae2af8878aecf73b5b6a5665d7840d592e7e299470e44bd31cedf7a12c1b', 'sha256': '0223ae2af8878aecf73b5b6a5665d7840d592e7e299470e44bd31cedf7a12c1b', 'bytes': 6105}, 'proof': {'key': 'objects/eb82ff6f74ffd0461a74cc6590e3cb1ef52adae2be698f4421b904c79d25d714', 'sha256': 'eb82ff6f74ffd0461a74cc6590e3cb1ef52adae2be698f4421b904c79d25d714', 'bytes': 7571}, 'sourceResultIndex': 0, 'originalSourceSha256': '1e8d43d1828092f65a14bf90b7a5e222d2e4e8e12bccaab23c2a7052f0da7bff', 'adapterSha256': '1806af8e93712f07da5a28bf590ecdce8f2b352c63559a2d0a46d90afcb01744', 'inventoryManifest': {'key': 'objects/db6cb99b0b9be266702686a607108080c0d77cca06340a624bba3e7fbc17a1f4', 'sha256': 'db6cb99b0b9be266702686a607108080c0d77cca06340a624bba3e7fbc17a1f4', 'bytes': 30669}}, 'change': {'sourceId': 'jfrog:official:1', 'sourceIndex': 34, 'originalSourceSha256': '1e8d43d1828092f65a14bf90b7a5e222d2e4e8e12bccaab23c2a7052f0da7bff', 'adapterSha256': '1806af8e93712f07da5a28bf590ecdce8f2b352c63559a2d0a46d90afcb01744', 'qualificationOriginSha256': '5a9d459c94528b99a45e679a0e7438863aabafaa9b3c1606b12fd2985c49b79e'}}, 'rapid7:official:1': {'sourceIndex': 52, 'sourceSha256': '2b77927e94626d7feef246b95536ec233849290223b79ed29d6f791713528310', 'origin': {'schemaVersion': 1, 'kind': 'bounded_q4_press_qualification', 'originalContract': {'key': 'contracts/8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db.json', 'sha256': '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db', 'bytes': 204449}, 'descriptor': {'key': 'objects/0223ae2af8878aecf73b5b6a5665d7840d592e7e299470e44bd31cedf7a12c1b', 'sha256': '0223ae2af8878aecf73b5b6a5665d7840d592e7e299470e44bd31cedf7a12c1b', 'bytes': 6105}, 'proof': {'key': 'objects/eb82ff6f74ffd0461a74cc6590e3cb1ef52adae2be698f4421b904c79d25d714', 'sha256': 'eb82ff6f74ffd0461a74cc6590e3cb1ef52adae2be698f4421b904c79d25d714', 'bytes': 7571}, 'sourceResultIndex': 1, 'originalSourceSha256': '05a6202088ab48d007b5969e9230844aa716749d7b9442d145953a51446209b5', 'adapterSha256': 'e33f08be7a81675ce1d8c925dd78d5165ac6b87eaf3ad71f1264856744f27cf3', 'inventoryManifest': {'key': 'objects/ac5b63569ed84b28053cc4f7cbda1c09abcb11866be40ba8e02f984ed21dcc25', 'sha256': 'ac5b63569ed84b28053cc4f7cbda1c09abcb11866be40ba8e02f984ed21dcc25', 'bytes': 49495}}, 'change': {'sourceId': 'rapid7:official:1', 'sourceIndex': 52, 'originalSourceSha256': '05a6202088ab48d007b5969e9230844aa716749d7b9442d145953a51446209b5', 'adapterSha256': 'e33f08be7a81675ce1d8c925dd78d5165ac6b87eaf3ad71f1264856744f27cf3', 'qualificationOriginSha256': '89791fac8c57cb8e39ef2602a5f80e6cb0e9c24cc4440e430175d1c9a7e23503'}}}}


def is_successor(contract):
    return digest(contract) == AUTHORITY.get('activatedContractSha256')


def _blob(store, ref):
    from source_qualification_origin import _json
    return _json(store, ref, r'objects/[a-f0-9]{64}')


def validate_source(source):
    expected = AUTHORITY.get('sources', {}).get(source.get('id'))
    require(expected is not None and digest(source) == expected['sourceSha256'] and
            source['kind'] == 'q4_press_list' and source['registration'] == 'verified' and
            source['url'] == URLS[source['id']], 'Q4_NORMAL_SOURCE_NOT_AUTHORIZED')
    return source


def validate_rows(original, current, transition):
    """Independently compute both whole objects; hashes never replace inversion."""
    require(digest(original) == H and is_successor(current) and
            digest(transition) == AUTHORITY['transition']['sha256'] and
            transition['originalContract'] == AUTHORITY['originalContract'] and
            transition['activatedContractSha256'] == digest(current), 'Q4_TRANSITION_POSITIVE_PAIR_REQUIRED')
    require(type(transition) is dict and set(transition) ==
            {'schemaVersion', 'kind', 'originalContract', 'activatedContractSha256', 'changes'} and
            type(transition['schemaVersion']) is int and transition['schemaVersion'] == 1 and
            transition['kind'] == TRANSITION_KIND and len(transition['changes']) == 2,
            'Q4_TRANSITION_SHAPE_INVALID')
    forward, inverse = copy.deepcopy(original), copy.deepcopy(current)
    require(len(original['sources']) == len(current['sources']), 'Q4_TRANSITION_SOURCE_COUNT_DIFFERS')
    for sid, change in zip(SOURCE_IDS, transition['changes']):
        expected = AUTHORITY['sources'][sid]
        index = expected['sourceIndex']
        old, new = original['sources'][index], current['sources'][index]
        require(change == expected['change'] and old['id'] == new['id'] == sid and
                digest(old) == change['originalSourceSha256'] and digest(new) == expected['sourceSha256'],
                'Q4_TRANSITION_SOURCE_POSITION_OR_BYTES_DIFFER')
        adapter = {**old, 'kind': 'q4_press_list', 'url': URLS[sid], 'registration': 'verified'}
        require(new == {**adapter, 'qualificationOrigin': expected['origin']} and
                digest(adapter) == change['adapterSha256'] and
                digest(expected['origin']) == change['qualificationOriginSha256'], 'Q4_TRANSITION_PATCH_DIFFERS')
        forward['sources'][index] = copy.deepcopy(new)
        inverse['sources'][index] = copy.deepcopy(old)
    require(canonical(forward) == canonical(current) and canonical(inverse) == canonical(original),
            'Q4_TRANSITION_WHOLE_FORWARD_OR_INVERSE_DIFFERS')
    return inverse


def inverse_policy(current, store):
    from source_qualification_origin import _contract
    require(is_successor(current), 'Q4_TRANSITION_NOT_AUTHORIZED')
    original = _contract(store, AUTHORITY['originalContract'])
    pointer = store.read('source-qualification-transitions/' + digest(current) + '.json')
    require(pointer == AUTHORITY['transition'], 'Q4_TRANSITION_POINTER_DIFFERS')
    transition = _blob(store, pointer)
    validate_rows(original, current, transition)
    return original


def _proof(original, store):
    descriptor = AUTHORITY['descriptor']
    raw = retained.primary._blob(store, descriptor)
    proof = _blob(store, AUTHORITY['proof'])
    checked = retained.verify_report(original, store, raw, proof)
    require(checked['proposalEvidenceComplete'] is True and checked['originalReportAcceptedSamples'] == 0 and
            proof['actualProof'] == AUTHORITY['actualProof'] and
            digest(proof) == AUTHORITY['proof']['sha256'], 'Q4_ORIGIN_PROOF_INCOMPLETE_OR_NOT_AUTHENTICATED')
    return proof


def predecessors(contract, source_id, store, before_time=None):
    require(source_id in SOURCE_IDS, 'Q4_ORIGIN_SOURCE_NOT_ALLOWED')
    source = next(s for s in contract['sources'] if s['id'] == source_id)
    value = {'kind': PREDECESSOR_KIND, 'sourceId': source_id,
             'qualificationOrigin': source['qualificationOrigin'], 'transition': AUTHORITY['transition']}
    resolve(value, contract, source_id, store, before_time)
    return [value]


def resolve(value, contract, source_id, store, before_time=None):
    original = inverse_policy(contract, store)
    require(source_id in SOURCE_IDS and type(value) is dict and set(value) ==
            {'kind', 'sourceId', 'qualificationOrigin', 'transition'} and value['kind'] == PREDECESSOR_KIND and
            value['sourceId'] == source_id and canonical(value['transition']) == canonical(AUTHORITY['transition']),
            'Q4_PREDECESSOR_SHAPE_INVALID')
    source = next(s for s in contract['sources'] if s['id'] == source_id)
    origin = AUTHORITY['sources'][source_id]['origin']
    require(canonical(value['qualificationOrigin']) == canonical(source['qualificationOrigin']) == canonical(origin),
            'Q4_PREDECESSOR_ORIGIN_DIFFERS')
    proof = _proof(original, store)
    i = origin['sourceResultIndex']
    manifest = _blob(store, origin['inventoryManifest'])
    stream = proof['streams'][i]
    # The original parser replays all records, not just a stored list/count flag.
    raw = retained.primary._blob(store, AUTHORITY['descriptor'])
    _, _, normalized = retained._validate(original, store, raw)
    complete = normalized['streams'][i]
    expected = {'schemaVersion': 1, 'kind': 'q4_qualification_inventory_manifest', 'sourceId': source_id,
                'descriptor': AUTHORITY['descriptor'], 'proof': AUTHORITY['proof'], 'sourceResultIndex': i,
                'streamSha256': digest(complete), 'items': complete['items']}
    require(manifest == expected and stream['streamSha256'] == digest(complete) and
            complete['sourceId'] == source_id, 'Q4_INVENTORY_NOT_FULL_REPLAYED_STREAM')
    completed = proof['originalCheckedAt']
    if before_time is not None:
        require(instant(completed) <= instant(before_time), 'Q4_QUALIFICATION_PREDECESSOR_FUTURE')
    return {'sourceId': source_id, 'items': list(complete['items']), 'completedAt': completed,
            'authority': 'inventory_only', 'provenance': [{'kind': KIND, 'descriptor': AUTHORITY['descriptor'],
                'proof': AUTHORITY['proof'], 'inventoryManifest': origin['inventoryManifest'],
                'sourceResultIndex': i, 'originalContract': AUTHORITY['originalContract']}]}
