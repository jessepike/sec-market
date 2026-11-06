"""Hash-bound retained document replay. Lookup hints never confer coverage."""
import copy
import json
import re
import threading
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit

from contracts import canonical, digest, instant, plan_run, require, unique
from documents import article_input, verify_article_input
from selection import (NOT_ABOUT_OUTCOME, NOT_ABOUT_RULE, collection_policy, mentions_supplier,
                       outside_history_window, windowed)
from separation import (enabled as separated, audit_version, original_contract, bridge, compatible, summary,
                        document_context, document_cache_key)
from source_qualification_origin import (is_qualification_predecessor, qualification_predecessors,
                                         resolve_inventory_origin)


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
    original = original_contract(store, entry['origin']) if entry else None
    require(entry and entry['contractSha256'] == digest(original) and all(
            entry[key] == receipt[key] for key in ('runId', 'taskId', 'attemptId', 'sourceId', 'supplierId')),
            'Unknown legacy-shaped bounded receipt requires retained audit proofs')
    require(resolve_origin(store, entry['origin'], original, receipt['sourceId']) == receipt,
            'Retained legacy migration receipt origin differs')
    return True


# Original discovery replays only write-once evidence (plans, sealed receipts,
# manifests, observations, content-addressed bodies), so one process may reuse a
# verified replay. Reconcile asks for the same origin once per retained URL; on
# the November 5 archive that repeated about 2,000 sitemap parses per check.
_ORIGINAL_DISCOVERY = {}
_VERIFIED_PLANS = set()


def original_discovery(binding, contract, source, store, require_complete=True):
    """Read the original source signature from pinned discovery bodies, never a cursor."""
    key = (str(Path(store.root).resolve()), canonical(binding['origin']), digest(source), digest(contract),
           bool(require_complete))
    if key not in _ORIGINAL_DISCOVERY:
        _ORIGINAL_DISCOVERY[key] = _original_discovery(binding, contract, source, store, require_complete)
    return copy.deepcopy(_ORIGINAL_DISCOVERY[key])


def _original_discovery(binding, contract, source, store, require_complete=True):
    origin = resolve_origin(store, binding['origin'], contract, source['id'])
    old_contract = original_contract(store, binding['origin'])
    old_source = next(s for s in old_contract['sources'] if s['id'] == source['id'])
    manifest = _object(store, origin['itemManifest'])
    observations = {oid: store.read('observations/' + oid + '.json') for oid in manifest['observations']}
    by_url = {ob['requestedUrl']: ob for ob in observations.values() if ob}
    from discovery import discover
    def request(url):
        require(url in by_url, 'Original discovery observation missing')
        ob = by_url[url]
        age = (instant(origin['completedAt']) - instant(ob['fetchedAt'])).total_seconds()/3600
        require(ob['sourceId'] == source['id'] and (not require_complete or ob['status'] in ('fetched', 'not_modified')) and
                'verifiedAt' not in ob and -5/60 <= age <= old_contract['schedule']['overdueHours'] and
                all(urlsplit(ob.get(k, url)).hostname in old_source['allowedHosts'] for k in ('requestedUrl', 'finalUrl')),
                'Original discovery transport context differs')
        return ob, store.get(ob['body']) if ob.get('body') else b''
    found = discover(old_source, request)
    require((not require_complete or found['complete']) and found['complete'] == origin.get('discoveryComplete') and
            found['items'] == manifest['items'], 'Original discovery proof differs')
    if separated(old_contract):
        require(found.get('itemModified', {}) == manifest.get('itemModified', {}) and
                found.get('itemDates', {}) == manifest.get('itemDates', {}), 'Original discovery signature differs')
    return found


def retained_index_signature(receipt, binding, contract, source, store):
    """Keep the last evidenced signature when an index fails or rolls a URL out."""
    candidates = index_for(store).discovery_candidates(source['id'], binding['url'], receipt)
    if not candidates:
        return None
    newest = max(instant(previous['completedAt']) for previous, _ in candidates)
    candidates = [(previous, origin) for previous, origin in candidates if instant(previous['completedAt']) == newest]
    signatures = {_object(store, previous['itemManifest']).get('itemModified', {}).get(binding['url'], '')
                  for previous, _ in candidates}
    require(len(signatures) == 1, 'Retained index signature ordering is ambiguous')
    previous, origin = max(candidates, key=lambda item: item[0]['attemptId'])
    old_contract = original_contract(store, origin)
    bridge(old_contract, contract, source['id'])
    view = HistoricalStoreView(store, previous)
    found = original_discovery({'origin': origin}, contract, source, view, require_complete=False)
    manifest = _object(store, previous['itemManifest'])
    for oid in manifest['observations']:
        observed = store.read('observations/' + oid + '.json')
        require(oid in previous['observationIds'] and observed['observationId'] == oid,
                'Retained signature observation membership differs')
        if observed['status'] in ('fetched', 'not_modified'):
            current_transport(observed, {**source, 'overdueHours': old_contract['schedule']['overdueHours']},
                              previous['completedAt'], view)
        else:
            # A failed terminal response is replayed as failure, never as intake
            # success. Successful siblings can still prove a known changed URL.
            require(index_for(view).latest_observation(source['id'], observed['requestedUrl']) == observed,
                    'Retained partial discovery failure differs')
    return {'url': binding['url'], 'origin': origin, 'itemManifest': previous['itemManifest'],
            'signature': found.get('itemModified', {}).get(binding['url'], ''),
            'policyBridge': bridge(old_contract, contract, source['id'])}


def revalidation_cursor(receipt, binding, contract, source, store, signature):
    """A flat reference to a real primary check, never to a quiet day's copied cursor."""
    candidates = index_for(store).revalidation_candidates(source['id'], binding['url'], receipt)
    if not candidates:
        return None
    previous, origin = max(candidates, key=lambda item: (item[0]['completedAt'], item[0]['attemptId']))
    old_contract = original_contract(store, origin)
    old_source = next(s for s in old_contract['sources'] if s['id'] == source['id'])
    resolve_origin(store, origin, contract, source['id'])
    prior = next(b for b in previous['retainedAuditBindings'] if b['url'] == binding['url'])
    semantic_keys = ('origin', 'sourceObservationId', 'sourceObservationSha256', 'validation')
    if any(prior[key] != binding[key] for key in semantic_keys):
        return None
    manifest = _object(store, previous['itemManifest'])
    # Replay the successful receipt with the transport information actually known
    # then. A later failure still overrides it in changed_bindings below.
    historical = HistoricalStoreView(store, previous)
    carried = (retained_index_signature(previous, prior, old_contract, old_source, historical)
               if binding['url'] not in manifest['items'] else None)
    witnessed_signature = (manifest.get('itemModified', {}).get(binding['url'], '')
                           if binding['url'] in manifest['items'] else carried['signature'] if carried else None)
    if witnessed_signature != signature:
        return None
    plan = store.read('runs/' + previous['runId'] + '/plan.json')
    verify_receipt(previous, plan, old_contract, old_source, previous['completedAt'], historical)
    details = separated_details(previous, old_contract, old_source, previous['completedAt'], historical)
    require(_object(store, previous['processingManifest']) == {'schemaVersion': 2, 'sourceId': source['id'],
            'runId': previous['runId'], **details['partitions']}, 'Revalidation witness processing proof differs')
    require(binding['url'] in details['partitions']['processingReviewed'] and
            binding['url'] not in details['partitions']['revalidationRequired'], 'Revalidation witness was not resolved')
    observed = store.read('observations/' + prior['transportObservationId'] + '.json')
    require(observed and digest(observed) == prior['transportObservationSha256'] and
            observed['observationId'] in previous['observationIds'] and
            instant(previous['startedAt']) <= instant(observed['fetchedAt']) <= instant(previous['completedAt']),
            'Revalidation witness lacks an actual current primary check')
    current_transport(observed, {**old_source, 'overdueHours': old_contract['schedule']['overdueHours']},
                      previous['completedAt'], historical)
    original = store.read('observations/' + prior['sourceObservationId'] + '.json')
    require(original['body'] == observed['body'] and
            document_context(old_source, original, article_input(store.get(original['body']), original)) ==
            document_context(old_source, observed, article_input(store.get(observed['body']), observed)),
            'Revalidation witness primary input differs')
    return {'url': binding['url'], 'origin': origin, 'itemManifest': previous['itemManifest'], 'signature': signature,
            'indexSignatureBinding': carried,
            **{key: prior[key] for key in semantic_keys if key != 'origin'}, 'semanticOrigin': prior['origin'],
            'transportObservationId': observed['observationId'], 'transportObservationSha256': digest(observed),
            'policyBridge': bridge(old_contract, contract, source['id'])}


def semantic_signature(binding, contract, source, store, found):
    """A fresh semantic review can check a URL already absent from its index."""
    if binding['url'] in found['items']:
        return found.get('itemModified', {}).get(binding['url'], '')
    original = resolve_origin(store, binding['origin'], contract, source['id'])
    old_contract = original_contract(store, binding['origin'])
    if not separated(old_contract):
        return ''
    old_source = next(s for s in old_contract['sources'] if s['id'] == source['id'])
    carried = retained_index_signature(original, binding, old_contract, old_source, HistoricalStoreView(store, original))
    recorded = [item for item in original.get('indexSignatureBindings', []) if item['url'] == binding['url']]
    require(recorded == ([carried] if carried else []), 'Original semantic index signature proof differs')
    return carried['signature'] if carried else ''


def binding_changes(receipt, contract, source, at, store, found=None):
    manifest = _object(store, receipt['itemManifest'])
    modified = (found or manifest).get('itemModified', {})
    current_items = set((found or manifest)['items'])
    changed, cursors, signatures = set(), [], []
    for binding in receipt.get('retainedAuditBindings', []):
        original = store.read('observations/' + binding['sourceObservationId'] + '.json')
        latest = index_for(store).latest_observation(source['id'], binding['url'])
        age = (instant(at) - instant(latest['fetchedAt'])).total_seconds()/3600 if latest else None
        same = latest and latest['status'] in ('fetched', 'not_modified') and 'verifiedAt' not in latest and age >= -5/60 and all(
            latest.get(k) == original.get(k) for k in ('body', 'contentType', 'finalUrl'))
        old_found = original_discovery(binding, contract, source, store)
        carried = (retained_index_signature(receipt, binding, contract, source, store)
                   if binding['url'] not in current_items else None)
        if carried:
            signatures.append(carried)
        signature = (modified.get(binding['url'], '') if binding['url'] in current_items else
                     carried['signature'] if carried else old_found.get('itemModified', {}).get(binding['url'], ''))
        signature_changed = signature != semantic_signature(binding, contract, source, store, old_found)
        current_check = False
        if same and instant(latest['fetchedAt']) >= instant(receipt['startedAt']):
            try:
                current_transport(latest, {**source, 'overdueHours': contract['schedule']['overdueHours']}, at, store)
                current_check = True
            except (ValueError, KeyError, TypeError):
                pass
        cursor = (revalidation_cursor(receipt, binding, contract, source, store, signature)
                  if same and signature_changed and not current_check else None)
        if cursor:
            cursors.append(cursor)
        if not same or (signature_changed and not current_check and not cursor):
            changed.add(binding['url'])
    retained_urls = {binding['url'] for binding in receipt.get('retainedAuditBindings', [])}
    for document in receipt.get('documentValidations', []):
        if document['url'] not in current_items and document['url'] not in retained_urls:
            carried = retained_index_signature(receipt, document, contract, source, store)
            if carried:
                signatures.append(carried)
    return changed, sorted(cursors, key=lambda cursor: cursor['url']), sorted(signatures, key=lambda item: item['url'])


def changed_bindings(receipt, contract, source, at, store, found=None):
    return binding_changes(receipt, contract, source, at, store, found)[0]


def separated_details(receipt, contract, source, at, store):
    """Called after verify_receipt; counts and URL sets are independently derived."""
    full = set(_object(store, receipt['retainedInventoryManifest'])['items'])
    manifest = _object(store, receipt['itemManifest'])
    pending = set(_object(store, receipt['pendingManifest'])['items']) if receipt.get('pendingManifest') else set()
    pending.update(item['url'] for item in receipt.get('retainedAuditUnbound', []))
    documents = {d['url']: _object(store, d['validation']) for d in receipt.get('documentValidations', [])}
    reviewed = set(documents)
    held = {url for url, validation in documents.items() if validation.get('heldClaims')}
    revalidation = changed_bindings(receipt, contract, source, at, store)
    changed = set(revalidation)
    # Changes remain classified after successful current review; unresolved
    # revalidation is a separate disposition and cannot silently become quiet.
    for url in full:
        try:
            prior = index_for(store).binding(source['id'], url, contract, at,
                                            before_attempt=receipt['attemptId'], before_time=receipt['startedAt'])
            old_found = original_discovery(prior, contract, source, store)
            original = store.read('observations/' + prior['sourceObservationId'] + '.json')
            latest = index_for(store).latest_observation(source['id'], url)
            context_changed = latest and (latest.get('body') != original.get('body') or
                (latest.get('body') and document_context(source, latest, article_input(store.get(latest['body']), latest)) !=
                 document_context(source, original, article_input(store.get(original['body']), original))))
            if context_changed or (url in manifest['items'] and
                    manifest.get('itemModified', {}).get(url, '') != semantic_signature(prior, contract, source, store, old_found)):
                changed.add(url)
        except (ValueError, KeyError, OSError, TypeError):
            pass  # An unavailable prior proof supplies no classification authority.
    from selection import date_partitions
    current, historical_dates, unknown = date_partitions(full, manifest.get('itemModified', {}), contract['collection'], at)
    unknown -= changed
    current -= changed
    historical_dates -= changed
    selected = set(receipt.get('selectedDocumentUrls', []))
    policy = collection_policy(contract, receipt)
    require(len(selected) == len(receipt.get('selectedDocumentUrls', [])) and selected.issubset(full) and
            len(selected) <= policy['maxDocumentsPerSource'] +
            policy.get('maxFetchAuditDocumentsPerSource', 0), 'Selected document bound/inventory differs')
    if receipt.get('collectionScope'):
        require(receipt['collectionScope']['mode'] == contract['collection']['mode'] and
                receipt['collectionScope']['selectedDocuments'] == len(selected), 'Selected work accounting differs')
    fresh = set(documents) - {b['url'] for b in receipt.get('retainedAuditBindings', [])}
    require(fresh.issubset(selected), 'Current document review is outside selected work')
    processing_reviewed = reviewed - pending
    archived, not_about = set(), set()
    if windowed(policy):
        # Archived = never reviewed, known date outside the history window, unchanged,
        # not selected, not an unresolved retained proof. Derived here, never trusted
        # from the engine, and always a subset of what the receipt still holds pending.
        unbound = {item['url'] for item in receipt.get('retainedAuditUnbound', [])}
        archived = {url for url in full - processing_reviewed
                    if url in manifest['items'] and url not in unbound and url not in changed and url not in selected
                    and outside_history_window(manifest.get('itemModified', {}).get(url, ''), policy, at)}
        not_about = {url for url in processing_reviewed if documents[url].get('exclusionRule') == NOT_ABOUT_RULE}
    # Archived documents stay in the retained queue and in historicalReview, but are
    # outside this processing denominator, so reviewed + pending == inventory still holds.
    processing = summary(full - archived, processing_reviewed, held & processing_reviewed,
                         (full - processing_reviewed) - archived,
                         changedDocuments=len(changed), unknownDateDocuments=len(unknown),
                         **({'archivedDocuments': len(archived), 'notAboutSupplierDocuments': len(not_about)}
                            if windowed(policy) else {}))
    processing['complete'] = not processing['pendingDocuments'] and not processing['heldDocuments']
    historical = summary(full, reviewed, held, full - reviewed)
    attempt_age = (instant(at) - instant(receipt['completedAt'])).total_seconds()/3600
    intake = bool(receipt.get('discoveryComplete') and source['registration'] == 'verified' and manifest['observations']
                  and -5/60 <= attempt_age <= contract['schedule']['overdueHours'])
    for oid in manifest['observations']:
        observed = store.read('observations/' + oid + '.json')
        try:
            require(observed and all(urlsplit(observed.get(k, observed['requestedUrl'])).hostname in source['allowedHosts']
                                    for k in ('requestedUrl', 'finalUrl')), 'Daily intake host differs')
            current_transport(observed, {**source, 'overdueHours': contract['schedule']['overdueHours']}, at, store)
            age = (instant(at) - instant(observed['fetchedAt'])).total_seconds()/3600
            require(-5/60 <= age <= contract['schedule']['overdueHours'], 'Daily intake observation stale')
        except (ValueError, KeyError, TypeError):
            intake = False
    return {'intakeComplete': intake, 'processing': processing, 'historicalReview': historical,
            'partitions': {'inventory': sorted(full), 'processingReviewed': sorted(processing_reviewed),
                           'processingPending': sorted(full - processing_reviewed),
                           'historicalReviewed': sorted(reviewed), 'historicalPending': sorted(full - reviewed),
                           'held': sorted(held), 'changed': sorted(changed), 'revalidationRequired': sorted(revalidation),
                           'unknownDate': sorted(unknown),
                           'current': sorted(current), 'historical': sorted(historical_dates),
                           'selected': sorted(selected), 'deferred': sorted((full - processing_reviewed) - selected),
                           **({'archived': sorted(archived), 'notAboutSupplier': sorted(not_about)} if windowed(policy) else {})}}


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


def resolve_origin(store, origin, contract, source_id, inventory_only=False):
    require(type(origin) is dict and set(origin) in
            ({'runId', 'taskId', 'attemptId', 'receipt'}, {'runId', 'taskId', 'attemptId', 'coverage'}),
            'Retained origin schema differs')
    plan = store.read('runs/' + origin['runId'] + '/plan.json')
    original = original_contract(store, origin)
    if separated(contract):
        if not inventory_only:
            bridge(original, contract, source_id)
    else:
        require(plan and plan['contractSha256'] == digest(contract), 'Retained origin policy differs')
    # A stored plan is write-once; re-deriving it once per process is enough.
    # Plans live at a write-once path and original_contract has already bound
    # this contract to plan['contractSha256'].
    verified = (str(Path(store.root).resolve()), origin['runId'], plan['contractSha256'])
    if verified not in _VERIFIED_PLANS:
        require(plan == plan_run(original, plan['scheduledAt'], plan.get('previousRunId')),
                'Retained origin plan inventory differs')
        _VERIFIED_PLANS.add(verified)
    task = next((task for task in plan['tasks'] if task['taskId'] == origin['taskId']), None)
    require(task and task['sourceId'] == source_id, 'Retained origin source task differs')
    if 'receipt' in origin:
        receipt = _object(store, origin['receipt'])
        seal = store.read('receipt-integrity/' + origin['runId'] + '/' + origin['taskId'] + '/' + origin['attemptId'] + '.json')
        require(seal == origin['receipt'], 'Retained origin receipt seal differs')
    else:
        coverage = _object(store, origin['coverage'])
        require(coverage.get('runId') == origin['runId'] and coverage.get('contractSha256') == digest(original)
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
        self.revalidations = {}
        self.discoveries = {}
        self.observations = {}
        self.observation_history = {}
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
            if receipt.get('itemManifest'):
                for url in _object(self.store, receipt['itemManifest'])['items']:
                    self.discoveries.setdefault((receipt['sourceId'], url), {})[key] = (receipt, origin)
            for document in receipt.get('documentValidations', []):
                if not any(binding['url'] == document['url'] for binding in
                           receipt.get('retainedAuditBindings', [])):
                    self.proofs.setdefault((receipt['sourceId'], document['url']), {})[key] = (receipt, origin, document)
            for binding in receipt.get('retainedAuditBindings', []):
                # Only actual selected primary transports can witness a cleared
                # signature. Quiet-day copies are never another proof origin.
                observed = self.store.read('observations/' + str(binding.get('transportObservationId')) + '.json')
                if (receipt.get('retainedAuditVersion') == 2 and binding['url'] in receipt.get('selectedDocumentUrls', [])
                        and observed and observed['observationId'] in receipt.get('observationIds', [])
                        and instant(receipt['startedAt']) <= instant(observed['fetchedAt']) <= instant(receipt['completedAt'])):
                    self.revalidations.setdefault((receipt['sourceId'], binding['url']), {})[key] = (receipt, origin)

    def revalidation_candidates(self, source_id, url, receipt):
        return [(previous, origin) for previous, origin in self.revalidations.get((source_id, url), {}).values()
                if previous['attemptId'] != receipt['attemptId'] and
                instant(previous['completedAt']) <= instant(receipt['startedAt'])]

    def discovery_candidates(self, source_id, url, receipt):
        return [(previous, origin) for previous, origin in self.discoveries.get((source_id, url), {}).values()
                if previous['attemptId'] != receipt['attemptId'] and
                instant(previous['completedAt']) <= instant(receipt['startedAt'])]

    def register(self, receipt, ref):
        with self.lock:
            self._add(receipt, {'runId': receipt['runId'], 'taskId': receipt['taskId'],
                               'attemptId': receipt['attemptId'], 'receipt': ref})

    def register_observation(self, observed):
        if not observed or not observed.get('sourceId') or not observed.get('requestedUrl'):
            return
        key = (observed['sourceId'], observed['requestedUrl'])
        with self.lock:
            self.observation_history.setdefault(key, {})[observed['observationId']] = observed
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
            original = self.store.read('contracts/' + plan['contractSha256'] + '.json') if plan else None
            if original is not None:
                require(digest(original) == plan['contractSha256'], 'Retained predecessor contract integrity differs')
            old_source = next((s for s in (original or {}).get('sources', []) if s['id'] == source_id), None)
            new_source = next((s for s in contract['sources'] if s['id'] == source_id), None)
            if plan and original is not None and (plan['contractSha256'] == digest(contract) or
                         (separated(contract) and old_source and new_source and old_source['supplierId'] == new_source['supplierId'])):
                resolve_origin(self.store, origin, contract, source_id, inventory_only=True)
                if receipt.get('retainedAuditVersion') not in (1, 2) and bounded(old_source, original):
                    legacy_eligible(receipt, original, self.store)
                result.append(origin)
        return (sorted(result, key=lambda origin: (origin['runId'], origin['attemptId'])) +
                qualification_predecessors(contract, source_id, self.store, before_time))

    def binding(self, source_id, url, contract, at, before_attempt=None, before_time=None):
        choices = []
        for receipt, origin, document in self.proofs.get((source_id, url), {}).values():
            if receipt['attemptId'] == before_attempt or (before_time is not None and
                    instant(receipt['completedAt']) > instant(before_time)):
                continue
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
        if separated(contract):
            binding['policyBridge'] = bridge(original_contract(self.store, origin), contract, source_id)
        replay_binding(binding, contract, source_id, at, self.store, self)
        return binding


def index_for(store):
    with _index_lock:
        if not hasattr(store, '_retained_audit_index'):
            store._retained_audit_index = AuditIndex(store)
        return store._retained_audit_index


class HistoricalStoreView:
    """Read-only replay at an original receipt time; later checks cannot rewrite history."""
    def __init__(self, store, receipt):
        while isinstance(store, HistoricalStoreView):
            store = store.store
        self.store, self.root = store, store.root
        self._retained_audit_index = HistoricalIndex(index_for(store), receipt)

    def read(self, key):
        return self.store.read(key)

    def get(self, ref):
        return self.store.get(ref)


class HistoricalIndex:
    def __init__(self, base, receipt):
        self.base, self.at = base, receipt['completedAt']
        self.preferred = {b['url']: b['transportObservationId'] for b in receipt.get('retainedAuditBindings', [])}
        self.known_ids = set(receipt.get('observationIds', [])) | set(self.preferred.values())

    def predecessors(self, *args, **kwargs):
        return self.base.predecessors(*args, **kwargs)

    def revalidation_candidates(self, *args, **kwargs):
        return self.base.revalidation_candidates(*args, **kwargs)

    def discovery_candidates(self, *args, **kwargs):
        return self.base.discovery_candidates(*args, **kwargs)

    @property
    def proofs(self):
        return self.base.proofs

    def binding(self, *args, **kwargs):
        # Classification only; use this view's historical latest transport too.
        source_id, url, contract, at = args
        choices = [(r, o, d) for r, o, d in self.base.proofs.get((source_id, url), {}).values()
                   if r['attemptId'] != kwargs.get('before_attempt') and
                   instant(r['completedAt']) <= instant(kwargs.get('before_time', self.at))]
        require(choices, 'RETAINED_AUDIT_ORIGIN_MISSING')
        receipt, origin, document = max(choices, key=lambda item: (item[0]['completedAt'], item[0]['attemptId']))
        observed = [self.read_observation(oid) for oid in receipt['observationIds']]
        observed = [ob for ob in observed if ob and ob['requestedUrl'] == url]
        require(len(observed) == 1, 'Retained original document observation differs')
        latest = self.latest_observation(source_id, url)
        binding = {'url': url, 'origin': origin, 'sourceObservationId': observed[0]['observationId'],
                   'sourceObservationSha256': digest(observed[0]), 'validation': document['validation'],
                   'transportObservationId': latest['observationId'], 'transportObservationSha256': digest(latest),
                   'policyBridge': bridge(original_contract(self.base.store, origin), contract, source_id)}
        replay_binding(binding, contract, source_id, at, self.base.store, self)
        return binding

    def read_observation(self, oid):
        return self.base.store.read('observations/' + oid + '.json')

    def latest_observation(self, source_id, url):
        values = [ob for ob in self.base.observation_history.get((source_id, url), {}).values()
                  if instant(ob['fetchedAt']) <= instant(self.at) or ob['observationId'] in self.known_ids]
        require(values, 'Historical source transport missing')
        newest = max(instant(ob['fetchedAt']) for ob in values)
        ties = [ob for ob in values if instant(ob['fetchedAt']) == newest]
        first = ties[0]
        require(all(all(ob.get(k) == first.get(k) for k in ('status', 'body', 'contentType', 'finalUrl')) for ob in ties),
                'RETAINED_AUDIT_AMBIGUOUS_LATEST_TRANSPORT')
        chosen = next((ob for ob in ties if ob['observationId'] == self.preferred.get(url)), first)
        require(self.read_observation(chosen['observationId']) == chosen, 'Historical source observation metadata differs')
        return chosen


def predecessor_inventory(origins, contract, source_id, store):
    items = set()
    seen = set()
    for origin in origins:
        if is_qualification_predecessor(origin):
            key = ('qualification', digest(origin))
            require(key not in seen, 'Duplicate qualification inventory predecessor')
            seen.add(key)
            items.update(resolve_inventory_origin(origin, contract, source_id, store)['items'])
            continue
        key = (origin['runId'], origin['attemptId'])
        require(key not in seen, 'Duplicate retained inventory predecessor')
        seen.add(key)
        receipt = resolve_origin(store, origin, contract, source_id, inventory_only=True)
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
    if receipt.get('retainedAuditVersion') != audit_version(contract):
        require(not separated(contract), 'New separated receipt omitted versioned intake/history proofs')
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


def replay_document(receipt, document, observed, contract, source, at, store, require_fresh=True, historical=False):
    from validation import mentions_entity, verify_statement, REVIEW_CHECKS
    supplier = next(s for s in contract['suppliers'] if s['id'] == source['supplierId'])
    policy = digest(contract)
    require(source['registration'] == 'verified' and receipt['supplierId'] == supplier['id'], 'Retained document subject differs')
    require(observed and observed['sourceId'] == source['id'] and observed['requestedUrl'] == document['url']
            and observed['observationId'] in receipt['observationIds'], 'Retained observation source/URL differs')
    require(observed['status'] in ('fetched', 'not_modified') and 'verifiedAt' not in observed,
            'Retained generic source lacks real successful transport')
    if require_fresh and not historical:
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
    cache = document_cache_key(contract, source, observed, view)
    if separated(contract):
        require(validation.get('inputContext') == document_context(source, observed, view),
                'Document validation input context differs')
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
    if validation.get('exclusionRule') == NOT_ABOUT_RULE:
        require(windowed(collection_policy(contract, receipt)) and validation.get('outcome') == NOT_ABOUT_OUTCOME and
                len(view['page'].readable) >= 100 and not mentions_supplier(view['page'].readable, supplier)
                and not hashes and validation.get('emptyReview') is None, 'Retained not-about-supplier exclusion differs')
    elif validation.get('exclusionRule'):
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
    expected = {'url', 'origin', 'sourceObservationId', 'sourceObservationSha256', 'validation',
                'transportObservationId', 'transportObservationSha256'}
    if separated(contract):
        expected.add('policyBridge')
    require(set(binding) == expected,
            'Retained binding schema differs')
    receipt = resolve_origin(store, binding['origin'], contract, source_id)
    original = original_contract(store, binding['origin'])
    if separated(contract):
        require(binding['policyBridge'] == bridge(original, contract, source_id), 'Retained semantic policy bridge differs')
        require((instant(receipt['completedAt']) - instant(at)).total_seconds() <= 300,
                'Retained original semantic check is future')
    original_source = next(s for s in original['sources'] if s['id'] == source_id)
    if receipt.get('retainedAuditVersion') not in (1, 2) and bounded(original_source, original):
        legacy_eligible(receipt, contract, store)
    require(not any(item['url'] == binding['url'] for item in
                    receipt.get('retainedAuditBindings', [])),
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
    if separated(contract):
        require(transport['sourceId'] == source_id and transport['requestedUrl'] == binding['url'],
                'Retained historical latest transport subject differs')
        return observed, replay_document(receipt, document, observed, original, original_source,
                                        receipt['completedAt'], store, historical=True)
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
    if not receipt.get('discoveryComplete') and not separated(contract):
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
    required_qualifications = {digest(origin) for origin in independently_required if is_qualification_predecessor(origin)}
    require(required_qualifications.issubset({digest(origin) for origin in receipt['retainedInventoryPredecessors']
                                            if is_qualification_predecessor(origin)}),
            'Retained predecessor omitted qualification origin')
    for origin in receipt['retainedInventoryPredecessors']:
        if is_qualification_predecessor(origin):
            resolve_inventory_origin(origin, contract, source['id'], store, receipt['startedAt'])
        else:
            require(origin['attemptId'] != receipt['attemptId'] and
                    instant(resolve_origin(store, origin, contract, source['id'], inventory_only=True)['completedAt']) <= instant(receipt['startedAt']),
                    'Retained predecessor is self or future')
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
        if not separated(contract):
            current_transport(ob, {**source, 'overdueHours': contract['schedule']['overdueHours']}, at, store)
        age = (instant(at) - instant(ob['fetchedAt'])).total_seconds()/3600
        require(ob['sourceId'] == source['id'] and
                (separated(contract) or ob['status'] in ('fetched', 'not_modified')) and
                'verifiedAt' not in ob and (separated(contract) or -5/60 <= age <= contract['schedule']['overdueHours']) and
                urlsplit(url).hostname in source['allowedHosts'], 'Retained discovery source/status/freshness differs')
        if ob['status'] == 'not_modified':
            old = store.read('observations/' + ob.get('reusesObservationId', '') + '.json')
            require(old and old['sourceId'] == source['id'] and old['requestedUrl'] == url and
                    old.get('body') == ob.get('body'), 'Retained discovery conditional body chain differs')
        return ob, store.get(ob['body']) if ob.get('body') else b''
    if separated(contract) and receipt.get('discoveryRecorded') is False:
        require(not receipt.get('discoveryComplete') and not manifest['observations'] and not manifest['items'],
                'Unattempted intake cannot contain discovery authority')
        found = {'complete': False, 'items': [], 'itemModified': {}, 'itemDates': {}}
    else:
        found = discover(source, request)
    require(found['complete'] == receipt.get('discoveryComplete') and
            (separated(contract) or found['complete'] is True) and found['items'] == manifest['items'],
            'Retained current discovery replay differs')
    if separated(contract):
        require(manifest.get('itemModified', {}) == found.get('itemModified', {}) and
                manifest.get('itemDates', {}) == found.get('itemDates', {}), 'Intake scheduling classification evidence differs')
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
    if separated(contract):
        require(not fresh_urls & (pending | unbound) and not pending & unbound and
                set(full['items']) == completed | pending | unbound, 'Retained full inventory disposition partition differs')
        changed, cursors, signatures = binding_changes(receipt, contract, source, at, store, found)
        require(receipt.get('revalidationCursors') == cursors, 'Retained revalidation cursor proof differs or is omitted')
        require(receipt.get('indexSignatureBindings') == signatures, 'Retained index signature proof differs or is omitted')
        require(changed.issubset(pending | unbound), 'Known changed retained document lacks processing hold')
    else:
        require(not completed & (pending | unbound) and not pending & unbound and
                set(full['items']) == completed | pending | unbound, 'Retained full inventory disposition partition differs')
    require(receipt.get('pendingDocuments', 0) == len(pending), 'Retained pending count differs')
    require(receipt.get('retainedAuditDocuments', 0) == len(bindings) + len(unbound), 'Retained binding count differs')
    require(not any(fid in {json.loads(store.get(ref))['factId'] for ref in _object(store, binding['validation'])['factRefs']}
                    for binding in bindings for fid in receipt.get('newFactIds', [])), 'Retained fact incorrectly labelled new')
    if receipt['outcome'] in ('updated', 'checked_no_change'):
        require(not pending and not unbound, 'Retained incomplete inventory cannot earn coverage')
    return True
