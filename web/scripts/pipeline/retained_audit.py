"""Hash-bound retained document replay. Lookup hints never confer coverage."""
import json
import re
import threading
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit

from contracts import canonical, digest, instant, plan_run, require, unique
from documents import article_input, verify_article_input


VERSION = 1
LEGACY_REGISTRY_SHA256 = '6fdf2884bbcc70962a0fc41622c5c862a61c31ed79bbf97b18cc193a843b4dce'
FIELDS = ('supplierId', 'predicate', 'valueText', 'quote', 'effectiveDate', 'amount',
          'currency', 'qualifier', 'eventStatus', 'scope')
SIGNAL = re.compile(r'\b(funding|raised|acquisition|appointed|restructuring|layoffs|ARR|revenue|debt|shutdown)\b', re.I)
_index_lock = threading.RLock()


def legacy_registry():
    """An explicit format-migration boundary, never an author-created trust flag."""
    raw = Path(__file__).with_name('retained_audit_legacy.json').read_bytes()
    require(digest(raw) == LEGACY_REGISTRY_SHA256, 'Retained legacy migration registry hash differs')
    value = json.loads(raw)
    require(value.get('schemaVersion') == 1 and value.get('kind') == 'precutover_retained_audit_receipts',
            'Retained legacy migration registry schema differs')
    return {entry['receiptSha256']: entry for entry in value['receipts']}


def legacy_eligible(receipt, contract, store):
    entry = legacy_registry().get(digest(receipt))
    require(entry and entry['contractSha256'] == digest(contract) and all(
            entry[key] == receipt[key] for key in ('runId', 'taskId', 'attemptId', 'sourceId', 'supplierId')),
            'Unknown legacy-shaped bounded receipt requires retained audit proofs')
    require(resolve_origin(store, entry['origin'], contract, receipt['sourceId']) == receipt,
            'Retained legacy migration receipt origin differs')
    return True


def bounded(source, contract):
    return bool(contract.get('collection') and source and source['kind'] not in
                ('sec_facts', 'sec_submissions', 'sec_documents', 'sec_index', 'citation'))


def reference(value):
    raw = canonical(value)
    return {'key': 'objects/' + digest(raw), 'sha256': digest(raw), 'bytes': len(raw)}


def _object(store, ref):
    require(type(ref) is dict and set(ref) == {'key', 'sha256', 'bytes'} and
            ref['key'] == 'objects/' + ref['sha256'], 'Retained object reference differs')
    return json.loads(store.get(ref))


def resolve_origin(store, origin, contract, source_id):
    require(type(origin) is dict and set(origin) in
            ({'runId', 'taskId', 'attemptId', 'receipt'}, {'runId', 'taskId', 'attemptId', 'coverage'}),
            'Retained origin schema differs')
    plan = store.read('runs/' + origin['runId'] + '/plan.json')
    require(plan and plan['contractSha256'] == digest(contract), 'Retained origin policy differs')
    require(store.read('contracts/' + digest(contract) + '.json') == contract, 'Retained original contract bytes differ')
    require(plan == plan_run(contract, plan['scheduledAt'], plan.get('previousRunId')),
            'Retained origin plan inventory differs')
    task = next((task for task in plan['tasks'] if task['taskId'] == origin['taskId']), None)
    require(task and task['sourceId'] == source_id, 'Retained origin source task differs')
    if 'receipt' in origin:
        receipt = _object(store, origin['receipt'])
        seal = store.read('receipt-integrity/' + origin['runId'] + '/' + origin['taskId'] + '/' + origin['attemptId'] + '.json')
        require(seal == origin['receipt'], 'Retained origin receipt seal differs')
    else:
        coverage = _object(store, origin['coverage'])
        require(coverage.get('runId') == origin['runId'] and coverage.get('contractSha256') == digest(contract)
                and coverage.get('inventorySha256') == plan['inventorySha256'], 'Retained legacy coverage context differs')
        matches = [r for r in coverage['receipts'] if r['attemptId'] == origin['attemptId']]
        require(len(matches) == 1, 'Retained legacy attempt membership differs')
        receipt = matches[0]
    require(receipt['runId'] == origin['runId'] and receipt['taskId'] == origin['taskId']
            and receipt['attemptId'] == origin['attemptId'] and receipt['sourceId'] == source_id
            and receipt['supplierId'] == task['supplierId'], 'Retained original receipt subject differs')
    require(store.read('runs/' + origin['runId'] + '/attempts/' + origin['attemptId'] + '.json') == receipt,
            'Retained original attempt differs from immutable anchor')
    return receipt


class AuditIndex:
    """One metadata/object traversal per process/store; replay still checks chosen bytes."""
    def __init__(self, store):
        self.store = store
        self.receipts = {}
        self.by_source = {}
        self.proofs = {}
        self.observations = {}
        self.ambiguous_observations = set()
        self.scans = 1
        self.lock = threading.RLock()
        for path in sorted((store.root / 'receipt-integrity').glob('*/*/*.json')):
            ref = store.read(path.relative_to(store.root).as_posix())
            receipt = _object(store, ref)
            self._add(receipt, {'runId': receipt['runId'], 'taskId': receipt['taskId'],
                               'attemptId': receipt['attemptId'], 'receipt': ref})
        for path in sorted((store.root / 'objects').glob('*')):
            if not path.is_file():
                continue
            raw = path.read_bytes()
            if not raw.startswith(b'{') or b'"receipts"' not in raw or b'"inventorySha256"' not in raw:
                continue
            require(digest(raw) == path.name, 'Retained coverage object integrity differs')
            try:
                coverage = json.loads(raw)
            except (ValueError, UnicodeError):
                continue
            if not isinstance(coverage, dict) or not all(key in coverage for key in
                    ('receipts', 'runId', 'contractSha256', 'inventorySha256', 'checkedAt')):
                continue
            ref = {'key': 'objects/' + path.name, 'sha256': path.name, 'bytes': len(raw)}
            for receipt in coverage['receipts']:
                self._add(receipt, {'runId': receipt['runId'], 'taskId': receipt['taskId'],
                                   'attemptId': receipt['attemptId'], 'coverage': ref})
        for path in sorted((store.root / 'observations').glob('*.json')):
            observed = store.read(path.relative_to(store.root).as_posix())
            self.register_observation(observed)

    def _add(self, receipt, origin):
        key = (receipt['runId'], receipt['attemptId'])
        existing = self.receipts.get(key)
        require(existing is None or existing[0] == receipt, 'Retained anchored attempt collision')
        if existing is None or 'receipt' in origin:
            self.receipts[key] = (receipt, origin)
            self.by_source.setdefault(receipt['sourceId'], set()).add(key)
            for document in receipt.get('documentValidations', []):
                if not any(binding['url'] == document['url'] for binding in receipt.get('retainedAuditBindings', [])):
                    self.proofs.setdefault((receipt['sourceId'], document['url']), {})[key] = (receipt, origin, document)

    def register(self, receipt, ref):
        with self.lock:
            self._add(receipt, {'runId': receipt['runId'], 'taskId': receipt['taskId'],
                               'attemptId': receipt['attemptId'], 'receipt': ref})

    def register_observation(self, observed):
        if not observed or not observed.get('sourceId') or not observed.get('requestedUrl'):
            return
        key = (observed['sourceId'], observed['requestedUrl'])
        with self.lock:
            current = self.observations.get(key)
            if current is None or instant(observed['fetchedAt']) > instant(current['fetchedAt']):
                self.observations[key] = observed
                self.ambiguous_observations.discard(key)
            elif instant(observed['fetchedAt']) == instant(current['fetchedAt']) and any(
                    observed.get(field) != current.get(field) for field in ('status', 'body', 'contentType', 'finalUrl')):
                self.ambiguous_observations.add(key)

    def latest_observation(self, source_id, url):
        require((source_id, url) not in self.ambiguous_observations,
                'RETAINED_AUDIT_AMBIGUOUS_LATEST_TRANSPORT')
        saved = self.observations.get((source_id, url))
        head = self.store.read('heads/download-' + digest({'source': source_id, 'url': url}) + '.json')
        if head and saved and instant(head['fetchedAt']) == instant(saved['fetchedAt']):
            require(all(head.get(field) == saved.get(field) for field in ('status', 'body', 'contentType', 'finalUrl')),
                    'RETAINED_AUDIT_AMBIGUOUS_LATEST_TRANSPORT')
        if head and (saved is None or instant(head['fetchedAt']) > instant(saved['fetchedAt'])):
            saved = head
        if saved:
            actual = self.store.read('observations/' + saved['observationId'] + '.json')
            require(actual == saved, 'Retained latest transport metadata differs')
        return saved

    def predecessors(self, source_id, contract, before_attempt=None, before_time=None):
        result = []
        for key in self.by_source.get(source_id, []):
            receipt, origin = self.receipts[key]
            if receipt['sourceId'] != source_id or receipt['attemptId'] == before_attempt:
                continue
            if before_time is not None and instant(receipt['completedAt']) > instant(before_time):
                continue
            plan = self.store.read('runs/' + receipt['runId'] + '/plan.json')
            if plan and plan['contractSha256'] == digest(contract):
                resolve_origin(self.store, origin, contract, source_id)
                if receipt.get('retainedAuditVersion') != VERSION:
                    legacy_eligible(receipt, contract, self.store)
                result.append(origin)
        return sorted(result, key=lambda origin: (origin['runId'], origin['attemptId']))

    def binding(self, source_id, url, contract, at):
        choices = []
        for receipt, origin, document in self.proofs.get((source_id, url), {}).values():
            choices.append((receipt['completedAt'], receipt, origin, document))
        require(choices, 'RETAINED_AUDIT_ORIGIN_MISSING')
        _, receipt, origin, document = max(choices, key=lambda item: (item[0], item[1]['attemptId']))
        resolve_origin(self.store, origin, contract, source_id)
        matches = [self.store.read('observations/' + oid + '.json') for oid in receipt['observationIds']]
        matches = [o for o in matches if o and o['requestedUrl'] == url]
        require(len(matches) == 1, 'Retained original document observation differs')
        observed = matches[0]
        latest = self.latest_observation(source_id, url)
        binding = {'url': url, 'origin': origin, 'sourceObservationId': observed['observationId'],
                   'sourceObservationSha256': digest(observed), 'validation': document['validation'],
                   'transportObservationId': latest['observationId'] if latest else None,
                   'transportObservationSha256': digest(latest) if latest else None}
        replay_binding(binding, contract, source_id, at, self.store, self)
        return binding


def index_for(store):
    with _index_lock:
        if not hasattr(store, '_retained_audit_index'):
            store._retained_audit_index = AuditIndex(store)
        return store._retained_audit_index


def predecessor_inventory(origins, contract, source_id, store):
    items = set()
    seen = set()
    for origin in origins:
        key = (origin['runId'], origin['attemptId'])
        require(key not in seen, 'Duplicate retained inventory predecessor')
        seen.add(key)
        receipt = resolve_origin(store, origin, contract, source_id)
        for name in ('itemManifest', 'pendingManifest', 'retainedInventoryManifest'):
            if receipt.get(name):
                manifest = _object(store, receipt[name])
                require(manifest['sourceId'] == source_id, 'Retained predecessor inventory source differs')
                unique(manifest['items'], 'retained predecessor URL')
                items.update(manifest['items'])
    return items


def activate_compatibility(store, plan, contract, index):
    path = 'runs/' + plan['runId'] + '/retained-audit-compatibility.json'
    existing = store.read(path)
    if existing is not None:
        verify_compatibility(existing, plan, contract, store)
        return reference(existing)
    sources = {source['id']: source for source in contract['sources']}
    origins = [origin for (receipt, origin) in index.receipts.values()
               if receipt['runId'] == plan['runId'] and 'retainedAuditVersion' not in receipt
               and bounded(sources.get(receipt['sourceId']), contract)]
    value = {'schemaVersion': VERSION, 'runId': plan['runId'], 'contractSha256': digest(contract),
             'legacyOrigins': sorted(origins, key=lambda origin: origin['attemptId'])}
    store.write_once(path, value)
    return store.put(value)


def verify_compatibility(record, plan, contract, store):
    require(set(record) == {'schemaVersion', 'runId', 'contractSha256', 'legacyOrigins'} and
            record['schemaVersion'] == VERSION and record['runId'] == plan['runId'] and
            record['contractSha256'] == digest(contract), 'Retained compatibility record differs')
    cache = getattr(store, '_retained_compatibility_cache', {})
    if digest(record) in cache:
        return cache[digest(record)]
    legacy = set()
    for origin in record['legacyOrigins']:
        original_plan = store.read('runs/' + origin['runId'] + '/plan.json')
        task = next(t for t in original_plan['tasks'] if t['taskId'] == origin['taskId'])
        receipt = resolve_origin(store, origin, contract, task['sourceId'])
        require('retainedAuditVersion' not in receipt and origin['runId'] == plan['runId'],
                'Retained compatibility cannot admit a repaired receipt')
        legacy_eligible(receipt, contract, store)
        legacy.add(digest(receipt))
    cache[digest(record)] = legacy
    store._retained_compatibility_cache = cache
    return legacy


def require_version(receipt, plan, contract, store):
    record = store.read('runs/' + plan['runId'] + '/retained-audit-compatibility.json')
    if receipt.get('retainedAuditVersion') != VERSION:
        legacy_eligible(receipt, contract, store)
        if record is not None:
            require(digest(receipt) in verify_compatibility(record, plan, contract, store),
                    'Retained compatibility omitted an explicitly eligible legacy receipt')
        return False
    require(record is not None, 'Repaired receipt lacks immutable compatibility record')
    verify_compatibility(record, plan, contract, store)
    require(receipt.get('retainedAuditCompatibility') == reference(record), 'Retained compatibility binding differs')
    return True


def current_transport(observed, source, at, store):
    latest = index_for(store).latest_observation(source['id'], observed['requestedUrl'])
    require(latest and latest['sourceId'] == source['id'] and latest['requestedUrl'] == observed['requestedUrl'] and
            latest['status'] in ('fetched', 'not_modified') and 'verifiedAt' not in latest and
            latest.get('body') == observed.get('body') and latest.get('contentType') == observed.get('contentType') and
            latest.get('finalUrl', latest['requestedUrl']) == observed.get('finalUrl', observed['requestedUrl']),
            'RETAINED_AUDIT_NEWER_TRANSPORT_REQUIRES_CHECK')
    age = (instant(at) - instant(latest['fetchedAt'])).total_seconds()/3600
    require(-5/60 <= age <= source.get('overdueHours', 30), 'Retained latest transport is stale or future')
    if latest['status'] == 'not_modified':
        prior = store.read('observations/' + latest.get('reusesObservationId', '') + '.json')
        require(prior and prior['status'] in ('fetched', 'not_modified') and prior['sourceId'] == source['id']
                and prior['requestedUrl'] == latest['requestedUrl'] and prior['body'] == latest['body'] and
                instant(prior['fetchedAt']) <= instant(latest['fetchedAt']),
                'Retained latest conditional transport chain differs')
        store.get(prior['body'])


def replay_document(receipt, document, observed, contract, source, at, store, require_fresh=True):
    from validation import mentions_entity, verify_statement, REVIEW_CHECKS
    supplier = next(s for s in contract['suppliers'] if s['id'] == source['supplierId'])
    policy = digest(contract)
    require(source['registration'] == 'verified' and receipt['supplierId'] == supplier['id'], 'Retained document subject differs')
    require(observed and observed['sourceId'] == source['id'] and observed['requestedUrl'] == document['url']
            and observed['observationId'] in receipt['observationIds'], 'Retained observation source/URL differs')
    require(observed['status'] in ('fetched', 'not_modified') and 'verifiedAt' not in observed,
            'Retained generic source lacks real successful transport')
    if require_fresh:
        current_transport(observed, {**source, 'overdueHours': contract['schedule']['overdueHours']}, at, store)
    require(all(urlsplit(observed.get(key, document['url'])).hostname in source['allowedHosts']
                for key in ('requestedUrl', 'finalUrl')), 'Retained response host differs')
    age = (instant(at) - instant(observed['fetchedAt'])).total_seconds() / 3600
    require(age >= -5/60 and (not require_fresh or age <= contract['schedule']['overdueHours']),
            'RETAINED_AUDIT_TRANSPORT_STALE_OR_FUTURE')
    require(instant(observed['fetchedAt']) <= instant(receipt['completedAt']), 'Retained completion precedes source check')
    require(instant(receipt['startedAt']) <= instant(receipt['completedAt']) and
            (instant(receipt['completedAt']) - instant(at)).total_seconds() <= 300,
            'Retained original attempt time differs or is future')
    raw = store.get(observed['body'])
    if observed['status'] == 'not_modified':
        old = store.read('observations/' + observed.get('reusesObservationId', '') + '.json')
        require(old and old['status'] in ('fetched', 'not_modified') and old['sourceId'] == source['id'] and old['requestedUrl'] == document['url']
                and old['body'] == observed['body'] and instant(old['fetchedAt']) <= instant(observed['fetchedAt']),
                'Retained conditional body/source/time chain differs')
        store.get(old['body'])
    validation = _object(store, document['validation'])
    require(validation['body'] == observed['body'] and validation['supplierId'] == supplier['id']
            and validation['contractSha256'] == policy, 'Retained validation body/policy/entity differs')
    view = verify_article_input(validation, raw, observed)
    cache = digest({'supplier': supplier['id'], 'body': observed['body']['sha256'],
                    'contract': policy, 'extractor': view['extractor']})
    require(store.read('document-validation/' + cache + '.json') == validation, 'Retained extractor validation cache differs')
    hashes = []
    fact_hashes = {ref['sha256'] for ref in receipt.get('validatedFacts', [])}
    held_hashes = {ref['sha256'] for ref in receipt.get('heldClaims', [])}
    for kind, refs in (('accepted', validation['factRefs']), ('held', validation.get('heldClaims', []))):
        for ref in refs:
            fact = _object(store, ref)
            original = store.read('observations/' + fact['sourceObservationId'] + '.json')
            evidence = fact['evidence'][0] if kind == 'accepted' else fact['evidence']
            require(original and original['body'] == observed['body'] == evidence and original['sourceId'] == source['id']
                    and original['requestedUrl'] == document['url'], 'Retained disposition observation differs')
            require(fact['supplierId'] == supplier['id'] and fact['policySha256'] == policy,
                    'Retained disposition entity/policy differs')
            candidate = {key: fact[key] for key in FIELDS} if kind == 'accepted' else fact['candidate']
            require(fact['candidateSha256'] == digest(candidate), 'Retained candidate hash differs')
            review = _object(store, fact['review'])
            require(review.get('candidateSha256') == digest(candidate) and review.get('evidenceSha256') == evidence['sha256']
                    and review.get('policySha256') == policy and set(review.get('checks', {})) == REVIEW_CHECKS,
                    'Retained semantic review binding differs')
            if kind == 'accepted':
                require(ref['sha256'] in fact_hashes, 'Retained accepted fact missing from original receipt')
                require(verify_statement(candidate, original, store, review, supplier, policy, read_only=True) == fact,
                        'Retained accepted fact full replay differs')
            else:
                require(ref['sha256'] in held_hashes, 'Retained held claim missing from original receipt')
                reason = None
                try:
                    verify_statement(candidate, original, store, review, supplier, policy, read_only=True)
                except ValueError as exc:
                    reason = str(exc)[:160]
                require(reason == fact['reason'], 'Retained held disposition no longer matches')
            hashes.append(digest(candidate))
    require(Counter(hashes) == Counter(validation['candidateHashes']), 'Retained candidate/disposition inventory differs')
    unique(validation['candidateHashes'], 'retained candidate disposition')
    if validation.get('exclusionRule'):
        require(validation['exclusionRule'] == 'no-registered-entity-mention-v1' and
                source['family'] in ('investor_acquirer', 'release_distribution') and len(view['page'].readable) >= 100
                and not mentions_entity(view['page'].readable, supplier) and not hashes and validation.get('emptyReview') is None,
                'Retained shared-publisher exclusion differs')
    else:
        extraction = store.read('document-extractions/' + cache + '.json')
        require(extraction and extraction['body'] == observed['body'] and extraction['policySha256'] == policy,
                'Retained extraction evidence/policy differs')
        verify_article_input(extraction, raw, observed)
        require([digest(candidate) for candidate in extraction['candidates']] == validation['candidateHashes'],
                'Retained extraction candidate inventory differs')
        require(len(view['modelText']) <= contract['model']['maxDocumentChars'], 'Retained model input exceeds contract')
        if not hashes:
            empty = _object(store, validation['emptyReview'])
            require(empty.get('noRelevantFacts') is True and empty.get('evidenceSha256') == observed['body']['sha256']
                    and empty.get('policySha256') == policy and not SIGNAL.search(view['page'].readable),
                    'Retained independent empty review differs')
    return validation


def replay_binding(binding, contract, source_id, at, store, index=None):
    require(set(binding) == {'url', 'origin', 'sourceObservationId', 'sourceObservationSha256', 'validation',
                            'transportObservationId', 'transportObservationSha256'},
            'Retained binding schema differs')
    receipt = resolve_origin(store, binding['origin'], contract, source_id)
    if receipt.get('retainedAuditVersion') != VERSION:
        legacy_eligible(receipt, contract, store)
    require(not any(item['url'] == binding['url'] for item in receipt.get('retainedAuditBindings', [])),
            'Retained rebinding chain cannot become a new origin')
    document = {'url': binding['url'], 'validation': binding['validation']}
    require(document in receipt.get('documentValidations', []), 'Retained validation absent from original receipt')
    observed = store.read('observations/' + binding['sourceObservationId'] + '.json')
    require(observed and digest(observed) == binding['sourceObservationSha256'], 'Retained original observation digest differs')
    index = index or index_for(store)
    transport = store.read('observations/' + str(binding['transportObservationId']) + '.json')
    require(transport and digest(transport) == binding['transportObservationSha256'] and
            index.latest_observation(source_id, binding['url']) == transport,
            'RETAINED_AUDIT_NEWER_TRANSPORT_REQUIRES_CHECK')
    source = next(source for source in contract['sources'] if source['id'] == source_id)
    require(transport['sourceId'] == source_id and transport['requestedUrl'] == binding['url'] and
            transport['status'] in ('fetched', 'not_modified') and 'verifiedAt' not in transport and
            transport.get('body') == observed['body'] and transport.get('finalUrl', transport['requestedUrl']) ==
            observed.get('finalUrl', observed['requestedUrl']) and transport.get('contentType') == observed.get('contentType'),
            'RETAINED_AUDIT_NEWER_TRANSPORT_REQUIRES_CHECK')
    age = (instant(at) - instant(transport['fetchedAt'])).total_seconds()/3600
    require(-5/60 <= age <= contract['schedule']['overdueHours'], 'RETAINED_AUDIT_TRANSPORT_STALE_OR_FUTURE')
    if transport['status'] == 'not_modified':
        prior = store.read('observations/' + transport.get('reusesObservationId', '') + '.json')
        require(prior and prior['status'] in ('fetched', 'not_modified') and prior['sourceId'] == source_id and prior['requestedUrl'] == binding['url'] and
                prior['body'] == transport['body'] and instant(prior['fetchedAt']) <= instant(transport['fetchedAt']),
                'Retained current conditional transport chain differs')
        store.get(prior['body'])
    old_view = article_input(store.get(observed['body']), observed)
    new_view = article_input(store.get(transport['body']), transport)
    require(old_view['extractor'] == new_view['extractor'] and old_view['modelText'] == new_view['modelText'] and
            old_view['compressedInput'] == new_view['compressedInput'], 'Retained current transport input context differs')
    return transport, replay_document(receipt, document, observed, contract, source, at, store, require_fresh=False)


def verify_receipt(receipt, plan, contract, source, at, store):
    """Replay repaired receipts even when due work still holds source completeness."""
    if not require_version(receipt, plan, contract, store):
        if receipt.get('discoveryComplete'):
            for oid in receipt.get('observationIds', []):
                observed = store.read('observations/' + oid + '.json')
                if observed and observed.get('status') in ('fetched', 'not_modified'):
                    current_transport(observed, {**source, 'overdueHours': contract['schedule']['overdueHours']}, at, store)
        return False
    if not receipt.get('discoveryComplete'):
        require(all(receipt.get(key, []) == [] for key in
                    ('documentValidations', 'validatedFacts', 'heldClaims', 'newFactIds')) and
                not any(key in receipt for key in ('retainedInventoryManifest', 'retainedInventoryPredecessors',
                                                    'retainedAuditBindings', 'retainedAuditUnbound', 'retainedAuditDocuments')),
                'Incomplete discovery cannot carry semantic or retained authority')
        return True
    require(all(key in receipt for key in ('retainedInventoryManifest', 'retainedInventoryPredecessors',
            'retainedAuditBindings', 'retainedAuditUnbound')), 'New bounded receipt omitted retained inventory proofs')
    manifest = _object(store, receipt['itemManifest'])
    full = _object(store, receipt['retainedInventoryManifest'])
    prior = predecessor_inventory(receipt['retainedInventoryPredecessors'], contract, source['id'], store)
    independently_required = index_for(store).predecessors(source['id'], contract, receipt['attemptId'], receipt['startedAt'])
    required_prior = predecessor_inventory(independently_required, contract, source['id'], store)
    require(required_prior.issubset(prior), 'Retained predecessor inventory omitted anchored history')
    require(all(origin['attemptId'] != receipt['attemptId'] and
                instant(resolve_origin(store, origin, contract, source['id'])['completedAt']) <= instant(receipt['startedAt'])
                for origin in receipt['retainedInventoryPredecessors']), 'Retained predecessor is self or future')
    require(full['sourceId'] == manifest['sourceId'] == source['id'], 'Retained receipt inventory source differs')
    unique(full['items'], 'retained full inventory URL')
    require(set(full['items']) == set(manifest['items']) | prior, 'Retained full inventory/predecessor join differs')
    # Current discovery is independently replayed from this receipt's original index observations.
    observed = {oid: store.read('observations/' + oid + '.json') for oid in receipt['observationIds']}
    unique(receipt['observationIds'], 'retained receipt observation')
    require(all(ob and ob.get('observationId') == oid for oid, ob in observed.items()), 'Retained observation identity differs')
    require(type(manifest['observations']) is list and set(manifest['observations']).issubset(observed),
            'Retained discovery observation inventory differs')
    current = {observed[oid]['requestedUrl']: observed[oid] for oid in manifest['observations']}
    from discovery import discover
    def request(url):
        require(url in current, 'Retained discovery observation missing')
        ob = current[url]
        current_transport(ob, {**source, 'overdueHours': contract['schedule']['overdueHours']}, at, store)
        age = (instant(at) - instant(ob['fetchedAt'])).total_seconds()/3600
        require(ob['sourceId'] == source['id'] and ob['status'] in ('fetched', 'not_modified') and
                'verifiedAt' not in ob and -5/60 <= age <= contract['schedule']['overdueHours'] and
                urlsplit(url).hostname in source['allowedHosts'], 'Retained discovery source/status/freshness differs')
        if ob['status'] == 'not_modified':
            old = store.read('observations/' + ob.get('reusesObservationId', '') + '.json')
            require(old and old['sourceId'] == source['id'] and old['requestedUrl'] == url and
                    old.get('body') == ob.get('body'), 'Retained discovery conditional body chain differs')
        return ob, store.get(ob['body']) if ob.get('body') else b''
    found = discover(source, request)
    require(found['complete'] is True and found['items'] == manifest['items'], 'Retained current discovery replay differs')
    bindings = receipt['retainedAuditBindings']
    unique([binding['url'] for binding in bindings], 'retained binding URL')
    documents = receipt.get('documentValidations', [])
    unique([document['url'] for document in documents], 'retained document URL')
    documents_by_url = {document['url']: document for document in documents}
    fact_refs, held_refs = set(), set()
    rebound_urls = set()
    for binding in bindings:
        ob, validation = replay_binding(binding, contract, source['id'], at, store)
        require(ob['observationId'] in receipt['observationIds'] and documents_by_url.get(binding['url']) ==
                {'url': binding['url'], 'validation': binding['validation']}, 'Retained proof missing from current receipt')
        rebound_urls.add(binding['url'])
        fact_refs.update(ref['sha256'] for ref in validation['factRefs'])
        held_refs.update(ref['sha256'] for ref in validation.get('heldClaims', []))
    fresh_urls = set(documents_by_url) - rebound_urls
    by_url = {ob['requestedUrl']: ob for ob in observed.values()}
    for url in fresh_urls:
        validation = replay_document(receipt, documents_by_url[url], by_url.get(url), contract, source, at, store)
        fact_refs.update(ref['sha256'] for ref in validation['factRefs'])
        held_refs.update(ref['sha256'] for ref in validation.get('heldClaims', []))
    require(fact_refs == {ref['sha256'] for ref in receipt.get('validatedFacts', [])}
            and held_refs == {ref['sha256'] for ref in receipt.get('heldClaims', [])}, 'Retained current disposition union differs')
    pending = set()
    if receipt.get('pendingManifest'):
        pending_manifest = _object(store, receipt['pendingManifest'])
        require(pending_manifest['sourceId'] == source['id'] and pending_manifest['runId'] == plan['runId'],
                'Retained pending inventory provenance differs')
        unique(pending_manifest['items'], 'retained pending URL')
        pending = set(pending_manifest['items'])
    unbound = {item['url'] for item in receipt['retainedAuditUnbound']}
    require(len(unbound) == len(receipt['retainedAuditUnbound']), 'Duplicate retained unbound URL')
    completed = fresh_urls | rebound_urls
    require(not completed & (pending | unbound) and not pending & unbound and
            set(full['items']) == completed | pending | unbound, 'Retained full inventory disposition partition differs')
    require(receipt.get('pendingDocuments', 0) == len(pending), 'Retained pending count differs')
    require(receipt.get('retainedAuditDocuments', 0) == len(bindings) + len(unbound), 'Retained binding count differs')
    require(not any(fid in {json.loads(store.get(ref))['factId'] for ref in _object(store, binding['validation'])['factRefs']}
                    for binding in bindings for fid in receipt.get('newFactIds', [])), 'Retained fact incorrectly labelled new')
    if receipt['outcome'] in ('updated', 'checked_no_change'):
        require(not pending and not unbound, 'Retained incomplete inventory cannot earn coverage')
    return True
