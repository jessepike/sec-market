"""Dormant, positively pinned immutable HTML qualification package import.

This module grants no intake or semantic credit. Its only mutation is importing
the exact approved immutable bytes before the existing leased checkpoint ACK.
"""
import json
import os
from pathlib import Path
import re

from contracts import canonical, digest, instant, require
import source_qualification_origin as origins
from separation import semantic_context


# A future independently reviewed activation adds its exact package pin here.
# Neither archive metadata nor a repository package can populate this registry.
SEED_PACKAGES = (
{'contractSha256': '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db',
 'manifest': {'bytes': 5619,
              'path': 'contracts/html-qualification-seeds/8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db/seed.json',
              'sha256': '468acb882c44a1f75122b39b55a767e343361486eebe5269d1071bc8ae3666ba'}},
)
KIND = 'three_html_qualification_seed'
SOURCE_IDS = ('ping-identity:official:1', 'delinea:official:1', 'sonatype:official:1')


def _ref(ref):
    require(type(ref) is dict and set(ref) == {'key', 'sha256', 'bytes'} and
            type(ref['key']) is str and re.fullmatch(r'(objects/[a-f0-9]{64}|contracts/[a-f0-9]{64}\.json)', ref['key']) and
            type(ref['sha256']) is str and re.fullmatch(r'[a-f0-9]{64}', ref['sha256']) and
            type(ref['bytes']) is int and 0 < ref['bytes'] <= 32_000_000,
            'HTML_SEED_REFERENCE_INVALID')
    if ref['key'].startswith('objects/'):
        require(ref['key'] == 'objects/' + ref['sha256'], 'HTML_SEED_OBJECT_ADDRESS_DIFFERS')
    return ref


def _object(store, ref):
    _ref(ref)
    raw = store.get(ref)
    require(type(raw) is bytes and len(raw) == ref['bytes'] and digest(raw) == ref['sha256'],
            'HTML_SEED_REFERENCE_INTEGRITY_DIFFERS')
    value = json.loads(raw)
    require(canonical(value) == raw, 'HTML_SEED_OBJECT_NOT_CANONICAL')
    if ref['key'].startswith('contracts/'):
        require(ref['key'] == 'contracts/' + digest(value) + '.json', 'HTML_SEED_POLICY_ADDRESS_DIFFERS')
    return value


def _payload(repo, pin):
    require(type(pin) is dict and set(pin) == {'path', 'sha256', 'bytes'} and
            type(pin['path']) is str and re.fullmatch(r'contracts/html-qualification-seeds/[A-Za-z0-9_./-]+', pin['path']) and
            '..' not in pin['path'].split('/') and type(pin['bytes']) is int and 0 < pin['bytes'] <= 32_000_000 and
            type(pin['sha256']) is str and re.fullmatch(r'[a-f0-9]{64}', pin['sha256']),
            'HTML_SEED_PAYLOAD_PIN_INVALID')
    root = Path(repo).resolve()
    path = root / pin['path']
    require(path.resolve().is_relative_to(root) and not any(p.is_symlink() for p in
            (path, *path.parents) if p != root.parent), 'HTML_SEED_PAYLOAD_PATH_ESCAPES')
    raw = path.read_bytes()
    require(len(raw) == pin['bytes'] and digest(raw) == pin['sha256'], 'HTML_SEED_PAYLOAD_INTEGRITY_DIFFERS')
    return raw


class _Overlay:
    """Read-only view; qualification replay can see seed bytes before import."""
    def __init__(self, store, files):
        self._store, self._files = store, files

    def get(self, ref):
        raw = self._files.get(ref['key'])
        if raw is None:
            raw = self._store.get(ref)
        require(digest(raw) == ref['sha256'] and len(raw) == ref['bytes'], 'HTML_SEED_OVERLAY_INTEGRITY_DIFFERS')
        return raw

    def read(self, key):
        raw = self._files.get(key)
        return json.loads(raw) if raw is not None else self._store.read(key)


def preservation_summary(store, preservation, original, current):
    """Preserve pinned old evidence and derive its inventory/projection hashes.

    This checks historical byte retention and subject compatibility. It does not
    re-admit facts or label any historical receipt as a current collection.
    """
    require(type(preservation) is dict and set(preservation) ==
            {'coverage', 'snapshot', 'protectedReferences', 'summary'} and
            type(preservation['protectedReferences']) is list, 'HTML_SEED_PRESERVATION_SCHEMA_INVALID')
    coverage = _object(store, preservation['coverage'])
    snapshot = _object(store, preservation['snapshot'])
    require(coverage['contractSha256'] == digest(original) and snapshot['contractSha256'] == digest(original),
            'HTML_SEED_PRESERVATION_POLICY_DIFFERS')
    require({'runId', 'inventorySha256', 'requiredTasks', 'successfulTasks', 'supplierCount',
             'tasks', 'checkedAt', 'receipts'}.issubset(coverage) and
            type(coverage['tasks']) is list and type(coverage['receipts']) is list and
            len(coverage['tasks']) == len(coverage['receipts']) and
            snapshot.get('runId') == coverage['runId'] and type(snapshot.get('coverage')) is dict and
            all(canonical(snapshot['coverage'].get(key)) == canonical(value) for key, value in coverage.items()
                if key not in ('receipts', 'checkedAt')) and
            instant(coverage['checkedAt']) <= instant(snapshot['coverage']['checkedAt']) == instant(snapshot['checkedAt']),
            'HTML_SEED_ORIGINAL_COVERAGE_SNAPSHOT_JOIN_DIFFERS')
    unsigned = {k: v for k, v in snapshot.items() if k != 'snapshotSha256'}
    require(snapshot.get('snapshotSha256') == digest(unsigned), 'HTML_SEED_OLD_SNAPSHOT_SEAL_DIFFERS')
    pairs, retained_pairs, bindings, facts = set(), set(), [], {}
    for receipt in coverage['receipts']:
        sid = receipt['sourceId']
        items = set()
        for field in ('itemManifest', 'pendingManifest', 'retainedInventoryManifest'):
            if receipt.get(field):
                manifest = _object(store, receipt[field])
                require(manifest['sourceId'] == sid and type(manifest['items']) is list and
                        all(type(url) is str for url in manifest['items']) and
                        len(manifest['items']) == len(set(manifest['items'])), 'HTML_SEED_OLD_INVENTORY_INVALID')
                items.update(manifest['items'])
                if field == 'retainedInventoryManifest':
                    retained_pairs.update((sid, url) for url in manifest['items'])
        if items or receipt.get('documentValidations') or receipt.get('validatedFacts') or receipt.get('heldClaims'):
            require(sid not in SOURCE_IDS and digest(semantic_context(original, sid)) ==
                    digest(semantic_context(current, sid)), 'HTML_SEED_OLD_SUBJECT_CONTEXT_DIFFERS')
        pairs.update((sid, url) for url in items)
        bindings.extend(receipt.get('retainedAuditBindings', []))
        for ref in receipt.get('validatedFacts', []):
            _object(store, ref)
            facts[digest(ref)] = ref
    protected = preservation['protectedReferences']
    require([digest(ref) for ref in protected] == sorted(set(digest(ref) for ref in protected)),
            'HTML_SEED_PROTECTED_REFERENCES_ORDER_OR_DUPLICATE')
    for ref in protected:
        _object(store, ref)
    result = {'inventoryPairs': len(pairs), 'inventoryPairsSha256': digest(sorted(pairs)),
              'retainedInventoryPairs': len(retained_pairs), 'retainedInventoryPairsSha256': digest(sorted(retained_pairs)),
              'retainedBindings': len(bindings), 'retainedBindingsSha256': digest(sorted(bindings, key=digest)),
              'factReferences': len(facts), 'factReferencesSha256': digest(sorted(facts.values(), key=digest)),
              'reviewQueueEntries': len(snapshot['reviewQueue']), 'reviewQueueSha256': digest(snapshot['reviewQueue']),
              'snapshotSha256': snapshot['snapshotSha256'],
              'protectedReferencesSha256': digest(protected)}
    require(type(preservation['summary']) is dict and canonical(result) == canonical(preservation['summary']),
            'HTML_SEED_PRESERVATION_SUMMARY_DIFFERS')
    return result


def validate_seed(repo, store, contract, at):
    """Pure preflight, returning only predetermined bytes after full origin replay."""
    active = [s['id'] for s in contract['sources'] if 'qualificationOrigin' in s]
    if not active:
        return None
    require(set(active) == set(SOURCE_IDS) and len(active) == 3, 'HTML_SEED_THREE_ORIGINS_REQUIRED')
    rows = [row for row in SEED_PACKAGES if row.get('contractSha256') == digest(contract)]
    require(len(rows) == 1 and set(rows[0]) == {'contractSha256', 'manifest'}, 'HTML_SEED_PACKAGE_NOT_TRUSTED')
    raw = _payload(repo, rows[0]['manifest'])
    manifest = json.loads(raw)
    require(canonical(manifest) == raw and type(manifest) is dict and set(manifest) ==
            {'schemaVersion', 'kind', 'activatedContractSha256', 'transition', 'proofArchive', 'files', 'preservation'} and
            type(manifest['schemaVersion']) is int and manifest['schemaVersion'] == 1 and manifest['kind'] == KIND and
            manifest['activatedContractSha256'] == digest(contract) and type(manifest['files']) is list,
            'HTML_SEED_MANIFEST_SCHEMA_INVALID')
    authority = origins._authority(contract, manifest['transition'])
    proof = manifest['proofArchive']
    mains = [row for row in authority['diagnostics'] if row['record'] == authority['mainDiagnostic']]
    require(type(proof) is dict and set(proof) == {'commit', 'manifestSha256'} and len(mains) == 1 and
            proof == {'commit': mains[0]['archiveCommit'], 'manifestSha256': mains[0]['archiveManifestSha256']},
            'HTML_SEED_PROOF_ARCHIVE_DIFFERS')
    h = digest(contract)
    pointer_key = 'source-qualification-transitions/' + h + '.json'
    allowed = {pointer_key, 'contracts/' + h + '.json', _ref(manifest['transition'])['key']}
    allowed.update(_ref(s['qualificationOrigin']['inventoryManifest'])['key'] for s in contract['sources'] if s['id'] in SOURCE_IDS)
    # The archived mutable snapshot head is frozen as one exact original object.
    # Its trusted manifest pin authorizes those bytes, never a head replacement.
    allowed.add(_ref(manifest['preservation']['snapshot'])['key'])
    require(len(allowed) == 7, 'HTML_SEED_PAYLOAD_GRAPH_DIFFERS')
    files, keys = {}, []
    for entry in manifest['files']:
        require(type(entry) is dict and set(entry) == {'key', 'sha256', 'bytes', 'path'} and
                type(entry['key']) is str and entry['key'] in allowed, 'HTML_SEED_FILE_KEY_NOT_ALLOWED')
        body = _payload(repo, {k: entry[k] for k in ('path', 'sha256', 'bytes')})
        require(canonical(json.loads(body)) == body, 'HTML_SEED_FILE_NOT_CANONICAL')
        key = entry['key']
        if key.startswith('objects/'):
            require(key == 'objects/' + digest(body), 'HTML_SEED_FILE_OBJECT_ADDRESS_DIFFERS')
        require(key not in files, 'HTML_SEED_DUPLICATE_FILE')
        # Existing immutable bytes are never replaced, even during preflight.
        existing = store.read(key)
        if existing is not None:
            require(store.get({'key': key, 'sha256': digest(body), 'bytes': len(body)}) == body,
                    'HTML_SEED_EXISTING_IMMUTABLE_DIFFERS')
        files[key] = body
        keys.append(key)
    require(keys == sorted(allowed), 'HTML_SEED_FILES_MISSING_OR_ORDER_DIFFERS')
    require(files['contracts/' + h + '.json'] == canonical(contract) and
            files[pointer_key] == canonical(manifest['transition']), 'HTML_SEED_POLICY_OR_POINTER_DIFFERS')
    overlay = _Overlay(store, files)
    original = _object(overlay, authority['originalContract'])
    before = preservation_summary(overlay, manifest['preservation'], original, contract)
    inventory = {}
    for sid in SOURCE_IDS:
        predecessor = origins.qualification_predecessors(contract, sid, overlay, at)
        require(len(predecessor) == 1, 'HTML_SEED_ORIGIN_MISSING')
        result = origins.resolve_inventory_origin(predecessor[0], contract, sid, overlay, at)
        require(result['authority'] == 'inventory_only' and instant(result['completedAt']) <= instant(at),
                'HTML_SEED_ORIGIN_AUTHORITY_OR_TIME_DIFFERS')
        inventory[sid] = {'documents': len(result['items']), 'itemsSha256': digest(result['items']),
                          'completedAt': result['completedAt']}
    require(before == preservation_summary(overlay, manifest['preservation'], original, contract),
            'HTML_SEED_OVERLAY_CHANGED_OLD_EVIDENCE')
    return {'files': files, 'manifestSha256': digest(raw), 'contractSha256': h,
            'preservation': before, 'qualificationInventory': inventory}


def _context(root, store, session, runtime, at):
    require(os.environ.get('GITHUB_ACTIONS') == 'true' and os.environ.get('GITHUB_REPOSITORY') == 'jessepike/sec-market' and
            os.environ.get('GITHUB_REF') == 'refs/heads/main' and os.environ.get('GITHUB_EVENT_NAME') in ('schedule', 'workflow_dispatch') and
            os.environ.get('GITHUB_SHA') == session.get('appRevision') and
            re.fullmatch(r'[a-f0-9]{40}', session.get('appRevision', '')) and
            session.get('role') == 'collector' and session.get('executionMode') == 'github_subscription' and
            'checkpointProfile' not in session, 'HTML_SEED_PRIVATE_REVIEWED_MAIN_REQUIRED')
    run, attempt = os.environ.get('GITHUB_RUN_ID', ''), os.environ.get('GITHUB_RUN_ATTEMPT', '')
    require(re.fullmatch(r'[1-9][0-9]*', run) and re.fullmatch(r'[1-9][0-9]*', attempt) and
            session.get('sessionId') == 'github-' + run + '-' + attempt, 'HTML_SEED_RUN_IDENTITY_DIFFERS')
    event = json.loads(Path(os.environ.get('GITHUB_EVENT_PATH', '')).read_bytes())
    require(event.get('repository', {}).get('full_name') == 'jessepike/sec-market' and
            event.get('repository', {}).get('private') is True and
            event.get('inputs', {}).get('source_probe') not in (True, 'true'), 'HTML_SEED_PRIVATE_COLLECTION_REQUIRED')
    from storage import LocalStore
    require(LocalStore(root).read('session.json') == session, 'HTML_SEED_SESSION_DIFFERS')
    runtime.require_lease(store, session, at)
    require(not store.read('heads/cloud-lease.json').get('checkpointProfile'), 'HTML_SEED_ORDINARY_LEASE_REQUIRED')


def seed_before_collection(repo, root, store, session, contract, runtime):
    """Import and remotely acknowledge the approved package before any reuse/work."""
    if not any('qualificationOrigin' in source for source in contract['sources']):
        return None
    at = runtime.utcnow()
    _context(root, store, session, runtime, at)
    checked = validate_seed(repo, store, contract, at)
    _context(root, store, session, runtime, runtime.utcnow())
    for key, raw in checked['files'].items():
        store.write_once(key, raw)
    _context(root, store, session, runtime, runtime.utcnow())
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
            receipt['receipt'].get('role') == 'collector' and
            receipt['receipt'].get('contractSha256') == digest(contract) and
            receipt['receipt'].get('result') == result, 'HTML_SEED_REMOTE_ACK_REQUIRED')
    _context(root, store, session, runtime, runtime.utcnow())
    return {**result, 'archive': archive}
