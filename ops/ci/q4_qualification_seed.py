"""Exact J immutable seed. No source, semantic, budget or normal-head authority."""
import json
from pathlib import Path
import re

from contracts import canonical, digest, instant, require
import html_qualification_seed as html
import q4_qualification_origin as q4
from separation import semantic_context

KIND = 'two_q4_qualification_seed'
PACKAGE = {'path': 'contracts/q4-qualification-seeds/47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a/seed.json',
           'sha256': '4423bc092868d3774b4e52b22299a97efdc13ab009d1297cc6c33fe354ba842b', 'bytes': 21926}


def _payload(repo, pin):
    root = Path(repo).resolve()
    require(type(pin) is dict and set(pin) == {'path', 'sha256', 'bytes'} and
            type(pin['path']) is str and pin['path'].startswith('contracts/q4-qualification-seeds/' +
                q4.AUTHORITY['activatedContractSha256'] + '/') and '..' not in pin['path'].split('/') and
            type(pin['bytes']) is int and 0 < pin['bytes'] <= 32_000_000 and
            type(pin['sha256']) is str and re.fullmatch(r'[a-f0-9]{64}', pin['sha256']), 'Q4_SEED_PAYLOAD_PIN_INVALID')
    path = root / pin['path']
    require(path.resolve().is_relative_to(root) and not any((root.joinpath(*path.relative_to(root).parts[:i])).is_symlink()
            for i in range(1, len(path.relative_to(root).parts) + 1)), 'Q4_SEED_PAYLOAD_PATH_ESCAPES')
    raw = path.read_bytes()
    require(digest(raw) == pin['sha256'] and len(raw) == pin['bytes'], 'Q4_SEED_PAYLOAD_BYTES_DIFFER')
    return raw


def _preservation(store, value, original, current):
    require(type(value) is dict and set(value) == {'coverage', 'snapshot', 'protectedReferences', 'summary'},
            'Q4_SEED_PRESERVATION_SHAPE_INVALID')
    coverage, snapshot = html._object(store, value['coverage']), html._object(store, value['snapshot'])
    require(coverage['contractSha256'] == snapshot['contractSha256'] == q4.H and
            coverage['runId'] == snapshot['runId'] and
            all(canonical(snapshot['coverage'].get(k)) == canonical(v) for k, v in coverage.items()
                if k not in ('receipts', 'checkedAt')) and
            instant(coverage['checkedAt']) <= instant(snapshot['coverage']['checkedAt']) == instant(snapshot['checkedAt']) and
            digest({k: v for k, v in snapshot.items() if k != 'snapshotSha256'}) == snapshot['snapshotSha256'],
            'Q4_SEED_PRESERVATION_JOIN_DIFFERS')
    pairs, retained, bindings, facts = set(), set(), [], {}
    for receipt in coverage['receipts']:
        sid = receipt['sourceId']
        if sid:
            if sid in q4.SOURCE_IDS:
                require(not any(receipt.get(k) for k in ('validatedFacts', 'documentValidations', 'heldClaims',
                    'retainedAuditBindings')), 'Q4_SEED_CHANGED_SUBJECT_HAS_SEMANTIC_AUTHORITY')
            else:
                require(canonical(semantic_context(original, sid)) == canonical(semantic_context(current, sid)),
                        'Q4_SEED_UNCHANGED_SUBJECT_DIFFERS')
        for key in ('itemManifest', 'pendingManifest', 'retainedInventoryManifest'):
            if receipt.get(key):
                manifest = html._object(store, receipt[key])
                require(manifest['sourceId'] == sid and type(manifest['items']) is list and
                        all(type(url) is str for url in manifest['items']) and
                        len(manifest['items']) == len(set(manifest['items'])), 'Q4_SEED_OLD_INVENTORY_DIFFERS')
                pairs.update((sid, url) for url in manifest['items'])
                if key == 'retainedInventoryManifest':
                    retained.update((sid, url) for url in manifest['items'])
        bindings.extend(receipt.get('retainedAuditBindings', []))
        for ref in receipt.get('validatedFacts', []):
            html._object(store, ref)
            facts[digest(ref)] = ref
    protected = value['protectedReferences']
    require([digest(ref) for ref in protected] == sorted(set(digest(ref) for ref in protected)),
            'Q4_SEED_PROTECTED_REFERENCES_DIFFERS')
    for ref in protected:
        html._object(store, ref)
    result = {'inventoryPairs': len(pairs), 'inventoryPairsSha256': digest(sorted(pairs)),
              'retainedInventoryPairs': len(retained), 'retainedInventoryPairsSha256': digest(sorted(retained)),
              'retainedBindings': len(bindings), 'retainedBindingsSha256': digest(sorted(bindings, key=digest)),
              'factReferences': len(facts), 'factReferencesSha256': digest(sorted(facts.values(), key=digest)),
              'reviewQueueEntries': len(snapshot['reviewQueue']), 'reviewQueueSha256': digest(snapshot['reviewQueue']),
              'snapshotSha256': snapshot['snapshotSha256'], 'protectedReferencesSha256': digest(protected)}
    require(canonical(result) == canonical(value['summary']), 'Q4_SEED_PRESERVATION_SUMMARY_DIFFERS')
    return result


def validate_seed(repo, store, contract, at):
    require(q4.is_successor(contract), 'Q4_SEED_EXACT_J_REQUIRED')
    raw = _payload(repo, PACKAGE)
    manifest = json.loads(raw)
    require(canonical(manifest) == raw and type(manifest) is dict and set(manifest) ==
            {'schemaVersion', 'kind', 'activatedContractSha256', 'transition', 'originalHtmlPackageSha256',
             'proofArchive', 'preservationArchive', 'files', 'preservation'} and
            type(manifest['schemaVersion']) is int and manifest['schemaVersion'] == 1 and manifest['kind'] == KIND and
            manifest['activatedContractSha256'] == digest(contract) and manifest['transition'] == q4.AUTHORITY['transition'],
            'Q4_SEED_MANIFEST_SHAPE_OR_AUTHORITY_DIFFERS')
    actual = q4.AUTHORITY['actualProof']['archive']
    require(manifest['proofArchive'] == {'commit': actual['commit'], 'manifestSha256': actual['manifestSha256']},
            'Q4_SEED_ACTUAL_PROOF_ARCHIVE_DIFFERS')
    files = {}
    for entry in manifest['files']:
        require(type(entry) is dict and set(entry) == {'key', 'sha256', 'bytes', 'path'} and
                type(entry['key']) is str and re.fullmatch(
                    r'(objects/[a-f0-9]{64}|contracts/[a-f0-9]{64}\.json|ci/source-probe-runs/[0-9]+-[0-9]+\.json|source-qualification-transitions/[a-f0-9]{64}\.json)',
                    entry['key']) and entry['key'] not in files, 'Q4_SEED_FILE_KEY_OR_ORDER_DIFFERS')
        body = _payload(repo, {k: entry[k] for k in ('path', 'sha256', 'bytes')})
        if entry['key'].startswith('objects/'):
            require(entry['key'] == 'objects/' + digest(body), 'Q4_SEED_OBJECT_ADDRESS_DIFFERS')
        try:
            require(store.get({k: entry[k] for k in ('key', 'sha256', 'bytes')}) == body,
                    'Q4_SEED_EXISTING_IMMUTABLE_DIFFERS')
        except FileNotFoundError:
            pass
        files[entry['key']] = body
    require(list(files) == sorted(files), 'Q4_SEED_FILE_ORDER_DIFFERS')
    overlay = html._Overlay(store, files)
    original = q4.inverse_policy(contract, overlay)
    checked = html.validate_seed(repo, overlay, original, at)
    require(checked['manifestSha256'] == manifest['originalHtmlPackageSha256'] and
            all(files.get(k) == v for k, v in checked['files'].items()), 'Q4_SEED_ORIGINAL_HTML_PACKAGE_DIFFERS')
    inventories = {}
    import source_qualification_origin as origins
    for sid in (*html.SOURCE_IDS, *q4.SOURCE_IDS):
        prior = origins.qualification_predecessors(contract, sid, overlay, at)
        require(len(prior) == 1, 'Q4_SEED_ORIGIN_MISSING')
        result = origins.resolve_inventory_origin(prior[0], contract, sid, overlay, at)
        require(result['authority'] == 'inventory_only', 'Q4_SEED_CANNOT_IMPORT_SEMANTIC_AUTHORITY')
        inventories[sid] = {'documents': len(result['items']), 'itemsSha256': digest(result['items']),
                            'completedAt': result['completedAt']}
    before = _preservation(overlay, manifest['preservation'], original, contract)
    require(before == _preservation(overlay, manifest['preservation'], original, contract),
            'Q4_SEED_PRESERVATION_CHANGED_DURING_PREFLIGHT')
    return {'files': files, 'manifestSha256': digest(raw), 'contractSha256': digest(contract),
            'preservation': before, 'qualificationInventory': inventories}


def seed_before_collection(repo, root, store, session, contract, runtime):
    """Validate the full immutable union before the first operation import."""
    require(Path(runtime.REPO).resolve() == Path(repo).resolve() and
            digest(json.loads((Path(repo) / 'contracts/market.json').read_bytes())) == digest(contract),
            'Q4_SEED_RUNTIME_POLICY_OR_REPOSITORY_DIFFERS')
    html._context(root, store, session, runtime, runtime.utcnow())
    checked = validate_seed(repo, store, contract, runtime.utcnow())
    html._context(root, store, session, runtime, runtime.utcnow())
    for key, raw in checked['files'].items():
        store.write_once(key, raw)
    html._context(root, store, session, runtime, runtime.utcnow())
    result = {k: v for k, v in checked.items() if k != 'files'}
    result.update(coverageCredit=False, semanticAdmission=False, sourceChecksCredited=0)
    receipt = runtime.checkpoint(root, store, session, 'qualification_seeded', result)
    from storage import LocalStore
    archive = receipt.get('archive')
    require(type(archive) is dict and re.fullmatch(r'[a-f0-9]{40}', archive.get('commit', '')) and
            re.fullmatch(r'[a-f0-9]{64}', archive.get('manifestSha256', '')) and
            LocalStore(root).read('heads/remote-archive.json') == archive and
            receipt.get('receipt', {}).get('phase') == 'qualification_seeded' and
            receipt['receipt'].get('sessionId') == session['sessionId'] and
            receipt['receipt'].get('appRevision') == session['appRevision'] and
            receipt['receipt'].get('role') == 'collector' and receipt['receipt'].get('contractSha256') == digest(contract) and
            receipt['receipt'].get('result') == result, 'Q4_SEED_REMOTE_ACK_REQUIRED')
    html._context(root, store, session, runtime, runtime.utcnow())
    return {**result, 'archive': archive}
