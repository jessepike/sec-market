"""Closed HTML qualification provenance with inventory-only authority."""
import copy
import json
import re

from contracts import digest, instant, require


ORIGIN_KIND = 'bounded_html_qualification'
PREDECESSOR_KIND = 'qualification_inventory'
TRANSITION_KIND = 'three_html_source_qualification'
ORIGIN_FIELDS = {'schemaVersion', 'kind', 'originalContract', 'diagnostic', 'plan',
                 'sourceResultIndex', 'sourceResultSha256', 'originalSourceSha256',
                 'proposedAdapterSha256', 'activationBaseSha256', 'inventoryManifest'}
BOUNDED_FIELDS = {'kind', 'originalContract', 'diagnostic', 'plan', 'sourceResultIndex', 'sourceResultSha256'}
# Deliberately empty. A later reviewed activation must add exact externally
# authenticated proof pins in code. Archive metadata cannot add trusted entries.
ACTIVATION_AUTHORITIES = ()


def _json(store, ref, pattern):
    require(type(ref) is dict and set(ref) == {'key', 'sha256', 'bytes'} and
            isinstance(ref['key'], str) and re.fullmatch(pattern, ref['key']) and
            isinstance(ref['sha256'], str) and re.fullmatch(r'[a-f0-9]{64}', ref['sha256']) and
            type(ref['bytes']) is int and 0 < ref['bytes'] <= 32_000_000,
            'QUALIFICATION_ORIGIN_REFERENCE_INVALID')
    if ref['key'].startswith('objects/'):
        require(ref['key'] == 'objects/' + ref['sha256'], 'QUALIFICATION_ORIGIN_OBJECT_ADDRESS_DIFFERS')
    raw = store.get(ref)
    require(len(raw) == ref['bytes'] and digest(raw) == ref['sha256'], 'QUALIFICATION_ORIGIN_REFERENCE_INTEGRITY_DIFFERS')
    value = json.loads(raw)
    require(type(value) is dict, 'QUALIFICATION_ORIGIN_OBJECT_INVALID')
    return value


def _contract(store, ref):
    value = _json(store, ref, r'contracts/[a-f0-9]{64}\.json')
    require(ref['key'] == 'contracts/' + digest(value) + '.json', 'QUALIFICATION_ORIGIN_POLICY_ADDRESS_DIFFERS')
    return value


def _binding(original, source_id, plan=None):
    from onboarding import (BOUNDED_CANDIDATE_BINDINGS, BOUNDED_CANDIDATE_BINDINGS_V2,
                            BOUNDED_CANDIDATE_BINDINGS_V3, _candidate_adapter)
    selected = [(i, url, mode) for i, (sid, url, mode) in enumerate(BOUNDED_CANDIDATE_BINDINGS) if sid == source_id]
    require(len(selected) == 1, 'QUALIFICATION_ORIGIN_SOURCE_NOT_ALLOWED')
    index, url, mode = selected[0]
    matches = [s for s in original['sources'] if s['id'] == source_id]
    require(len(matches) == 1 and matches[0].get('registration') == 'candidate' and
            matches[0].get('kind') == 'official_discovery' and 'qualificationOrigin' not in matches[0],
            'QUALIFICATION_ORIGIN_ORIGINAL_SOURCE_INVALID')
    candidate = matches[0]
    if plan is not None:
        row = plan['sources'][index]
        revision = plan.get('parserRevision', 1)
        require(type(revision) is int and revision in (1, 2, 3), 'QUALIFICATION_ORIGIN_PARSER_REVISION_INVALID')
        expected = {1: BOUNDED_CANDIDATE_BINDINGS, 2: BOUNDED_CANDIDATE_BINDINGS_V2,
                    3: BOUNDED_CANDIDATE_BINDINGS_V3}[revision][index]
        require(row['sourceId'] == source_id and (source_id, row['indexUrl'], row['adapter']['htmlCompleteness']) == expected,
                'QUALIFICATION_ORIGIN_PLAN_SOURCE_DIFFERS')
        url, mode = row['indexUrl'], row['adapter']['htmlCompleteness']
    adapter = _candidate_adapter(candidate, url, mode)
    if plan is not None:
        require(digest(adapter) == digest(row['adapter']), 'QUALIFICATION_ORIGIN_PLAN_ADAPTER_DIFFERS')
    require(adapter['registration'] == 'candidate', 'QUALIFICATION_ORIGIN_ADAPTER_ACTIVATED')
    base = {**copy.deepcopy(adapter), 'registration': 'verified'}
    return index, candidate, adapter, base


def _same_candidate_context(old, baseline, source_id, allow_d112=False):
    _, old_source, _, _ = _binding(old, source_id)
    _, source, _, _ = _binding(baseline, source_id)
    require(digest(old) == digest(baseline) or (allow_d112 and
            old.get('version') == 'market-daily-v1' and baseline.get('version') == 'market-daily-v2' and
            old.get('collection', {}).get('mode') == 'delta_with_retained_audit' and
            baseline.get('collection', {}).get('mode') == 'daily_intake_with_separate_history'),
            'QUALIFICATION_INVENTORY_POLICY_TRANSITION_NOT_ALLOWED')
    reduced_old, reduced = copy.deepcopy(old), copy.deepcopy(baseline)
    for policy in (reduced_old, reduced):
        policy.pop('version', None)
        policy.get('collection', {}).pop('mode', None)
    require(digest(reduced_old) == digest(reduced) and digest(old_source) == digest(source),
            'QUALIFICATION_INVENTORY_ORIGINAL_CONTEXT_DIFFERS')


def _result(store, entry):
    require(type(entry) is dict and set(entry) == BOUNDED_FIELDS and entry['kind'] == 'bounded_candidate_result' and
            type(entry['sourceResultIndex']) is int, 'QUALIFICATION_INVENTORY_RESULT_SCHEMA_INVALID')
    original = _contract(store, entry['originalContract'])
    replay = _replay_once(original, store, entry['diagnostic'], entry['plan'])
    rows = replay['report']['sources']
    i = entry['sourceResultIndex']
    require(0 <= i < len(rows) and digest(rows[i]) == entry['sourceResultSha256'], 'QUALIFICATION_INVENTORY_RESULT_JOIN_DIFFERS')
    result = rows[i]
    index, candidate, adapter, base = _binding(original, result['sourceId'], replay['plan'])
    require(i == index and replay['plan']['sources'][i]['sourceId'] == candidate['id'] and
            replay['plan']['sources'][i]['originalSourceSha256'] == digest(candidate) and
            replay['plan']['sources'][i]['proposedAdapterSha256'] == digest(adapter),
            'QUALIFICATION_INVENTORY_RESULT_SOURCE_DIFFERS')
    return original, replay, result, candidate, adapter, base


def _replay_once(original, store, diagnostic, plan):
    """Parse one immutable walk once, while rechecking all pinned bytes on reuse."""
    from onboarding import replay_bounded_candidate_diagnostic
    key = digest({'contract': original, 'diagnostic': diagnostic, 'plan': plan})
    cache = getattr(store, '_qualification_origin_replays', None)
    if cache is None:
        cache = {}
        store._qualification_origin_replays = cache
    if key not in cache:
        references = {}
        class RecordingStore:
            def __getattr__(self, name):
                return getattr(store, name)
            def get(self, ref):
                raw = store.get(ref)
                require(len(raw) == ref['bytes'] and digest(raw) == ref['sha256'],
                        'QUALIFICATION_REPLAY_CACHE_REFERENCE_INTEGRITY_DIFFERS')
                references[digest(ref)] = copy.deepcopy(ref)
                return raw
        replay = replay_bounded_candidate_diagnostic(original, RecordingStore(), diagnostic, plan)
        cache[key] = (copy.deepcopy(replay), list(references.values()))
    replay, references = cache[key]
    for ref in references:
        raw = store.get(ref)
        require(len(raw) == ref['bytes'] and digest(raw) == ref['sha256'],
                'QUALIFICATION_REPLAY_CACHE_REFERENCE_INTEGRITY_DIFFERS')
    return copy.deepcopy(replay)


def _ready(replay):
    report = replay['report']
    require(report.get('executionCompleted') is True and report.get('budgetDenied') is False and
            report.get('facts') == [] and report.get('newFactIds') == [] and
            report.get('semanticAdmission') is False and report.get('coverageCredit') is False,
            'QUALIFICATION_ORIGIN_MAIN_RUN_INCOMPLETE')
    for result in report['sources']:
        sample = result.get('primarySample')
        shape = sample.get('shape') if isinstance(sample, dict) else None
        require(result.get('indexComplete') is True and result.get('terminalProved') is True and
                not result.get('reservationDenials') and not result.get('completionGuardReason') and
                type(shape) is dict and 'error' not in shape and shape.get('canonical') == sample['url'] and
                type(shape.get('readableCharacters')) is int and shape['readableCharacters'] > 0,
                'QUALIFICATION_ORIGIN_SOURCE_NOT_READY')


def _main_entry(origin):
    return {'kind': 'bounded_candidate_result', **{key: origin[key] for key in BOUNDED_FIELDS - {'kind'}}}


def _origin(store, value, source_id):
    require(type(value) is dict and set(value) == ORIGIN_FIELDS and type(value['schemaVersion']) is int and
            value['schemaVersion'] == 1 and value['kind'] == ORIGIN_KIND,
            'QUALIFICATION_ORIGIN_SCHEMA_INVALID')
    original, replay, result, candidate, adapter, base = _result(store, _main_entry(value))
    _ready(replay)
    require(result['sourceId'] == source_id and value['originalSourceSha256'] == digest(candidate) and
            value['proposedAdapterSha256'] == digest(adapter) and value['activationBaseSha256'] == digest(base),
            'QUALIFICATION_ORIGIN_DERIVED_BINDING_DIFFERS')
    return original, replay, base


def _authority(contract, transition):
    matches = [row for row in ACTIVATION_AUTHORITIES if row.get('activatedContractSha256') == digest(contract)]
    require(len(matches) == 1, 'QUALIFICATION_ACTIVATION_NOT_EXTERNALLY_AUTHENTICATED')
    row = matches[0]
    require(set(row) == {'activatedContractSha256', 'transition', 'originalContract',
                         'mainDiagnostic', 'mainPlan', 'diagnostics'} and
            row['transition'] == transition and type(row['diagnostics']) is list and row['diagnostics'],
            'QUALIFICATION_ACTIVATION_AUTHORITY_SCHEMA_DIFFERS')
    hashes = []
    fields = {'record', 'originalContract', 'rawPlanSha256', 'canonicalPlanSha256',
              'githubRunId', 'githubRunAttempt', 'appRevision', 'externalReceiptSha256',
              'artifactSha256', 'archiveCommit', 'archiveManifestSha256'}
    for diagnostic in row['diagnostics']:
        require(type(diagnostic) is dict and set(diagnostic) == fields and
                type(diagnostic['githubRunId']) is str and diagnostic['githubRunId'].isdigit() and
                type(diagnostic['githubRunAttempt']) is int and diagnostic['githubRunAttempt'] > 0 and
                all(isinstance(diagnostic[key], str) and re.fullmatch(r'[a-f0-9]{64}', diagnostic[key]) for key in
                    ('rawPlanSha256', 'canonicalPlanSha256', 'externalReceiptSha256', 'artifactSha256', 'archiveManifestSha256')) and
                all(isinstance(diagnostic[key], str) and re.fullmatch(r'[a-f0-9]{40}', diagnostic[key])
                    for key in ('appRevision', 'archiveCommit')),
                'QUALIFICATION_ACTIVATION_DIAGNOSTIC_AUTHORITY_INVALID')
        hashes.append(diagnostic['record']['sha256'])
    require(hashes == sorted(set(hashes)), 'QUALIFICATION_ACTIVATION_DIAGNOSTIC_AUTHORITY_DUPLICATE_OR_ORDER')
    return row


def _listed_diagnostic(authority, store, record_ref, original_ref, raw_hash, canonical_hash):
    rows = [row for row in authority['diagnostics'] if row['record'] == record_ref]
    require(len(rows) == 1, 'QUALIFICATION_INVENTORY_DIAGNOSTIC_NOT_AUTHENTICATED')
    row = rows[0]
    record = _json(store, record_ref, r'ci/source-probe-runs/[0-9]+-[0-9]+\.json')
    require(row['originalContract'] == original_ref and row['rawPlanSha256'] == raw_hash and
            row['canonicalPlanSha256'] == canonical_hash and
            str(record.get('githubRunId')) == row['githubRunId'] and
            type(record.get('githubRunAttempt')) in (str, int) and
            str(record['githubRunAttempt']) == str(row['githubRunAttempt']) and
            record.get('appRevision') == row['appRevision'],
            'QUALIFICATION_INVENTORY_EXTERNAL_PROVENANCE_DIFFERS')
    return record


def _transition(store, ref, contract):
    from onboarding import BOUNDED_CANDIDATE_BINDINGS
    authority = _authority(contract, ref)
    descriptor = _json(store, ref, r'objects/[a-f0-9]{64}')
    require(set(descriptor) == {'schemaVersion', 'kind', 'originalContract', 'activatedContractSha256', 'changes'} and
            type(descriptor['schemaVersion']) is int and descriptor['schemaVersion'] == 1 and
            descriptor['kind'] == TRANSITION_KIND and descriptor['activatedContractSha256'] == digest(contract) and
            type(descriptor['changes']) is list and len(descriptor['changes']) == 3,
            'QUALIFICATION_TRANSITION_SCHEMA_OR_POLICY_INVALID')
    original = _contract(store, descriptor['originalContract'])
    require(authority['originalContract'] == descriptor['originalContract'], 'QUALIFICATION_ACTIVATION_ORIGINAL_POLICY_DIFFERS')
    forward, inverse, resolved = copy.deepcopy(original), copy.deepcopy(contract), {}
    shared_main = None
    fields = {'sourceId', 'sourceIndex', 'originalSourceSha256', 'proposedAdapterSha256',
              'activationBaseSha256', 'qualificationOriginSha256'}
    for change, (source_id, _, _) in zip(descriptor['changes'], BOUNDED_CANDIDATE_BINDINGS):
        require(type(change) is dict and set(change) == fields and change['sourceId'] == source_id and
                type(change['sourceIndex']) is int, 'QUALIFICATION_TRANSITION_CHANGE_SCHEMA_INVALID')
        positions = [i for i, s in enumerate(original['sources']) if s['id'] == source_id]
        require(len(positions) == 1 and change['sourceIndex'] == positions[0] and
                len(contract['sources']) == len(original['sources']), 'QUALIFICATION_TRANSITION_SOURCE_POSITION_DIFFERS')
        i = positions[0]
        old_source, current = original['sources'][i], contract['sources'][i]
        require(current['id'] == source_id and 'qualificationOrigin' in current, 'QUALIFICATION_TRANSITION_SOURCE_MISSING')
        origin = current['qualificationOrigin']
        origin_original, replay, base = _origin(store, origin, source_id)
        require(origin['diagnostic'] == authority['mainDiagnostic'] and origin['plan'] == authority['mainPlan'],
                'QUALIFICATION_ACTIVATION_MAIN_PROOF_DIFFERS')
        _listed_diagnostic(authority, store, origin['diagnostic'], origin['originalContract'],
                           replay['plan']['rawSha256'], replay['plan']['canonicalSha256'])
        require(digest(origin_original) == digest(original) and origin['originalContract'] == descriptor['originalContract'],
                'QUALIFICATION_TRANSITION_ORIGINAL_POLICY_DIFFERS')
        signature = digest({'diagnostic': origin['diagnostic'], 'plan': origin['plan']})
        require(shared_main is None or shared_main == signature, 'QUALIFICATION_TRANSITION_MIXED_MAIN_RUNS')
        shared_main = signature
        expected = {**base, 'qualificationOrigin': origin}
        require(digest(current) == digest(expected) and change['originalSourceSha256'] == digest(old_source) and
                change['proposedAdapterSha256'] == origin['proposedAdapterSha256'] and
                change['activationBaseSha256'] == digest(base) and change['qualificationOriginSha256'] == digest(origin),
                'QUALIFICATION_TRANSITION_SOURCE_PATCH_DIFFERS')
        forward['sources'][i] = copy.deepcopy(expected)
        inverse['sources'][i] = copy.deepcopy(old_source)
        resolved[source_id] = (origin, origin_original, replay)
    require(digest(forward) == digest(contract) and digest(inverse) == digest(original),
            'QUALIFICATION_TRANSITION_WHOLE_POLICY_DIFFERS')
    return resolved, authority


def is_qualification_predecessor(origin):
    return isinstance(origin, dict) and origin.get('kind') == PREDECESSOR_KIND


def qualification_predecessors(contract, source_id, store, before_time=None):
    source = next((s for s in contract['sources'] if s['id'] == source_id), None)
    if not source or 'qualificationOrigin' not in source:
        return []
    transition = store.read('source-qualification-transitions/' + digest(contract) + '.json')
    require(transition is not None, 'QUALIFICATION_TRANSITION_REFERENCE_MISSING')
    origin = {'kind': PREDECESSOR_KIND, 'sourceId': source_id,
              'qualificationOrigin': source['qualificationOrigin'], 'transition': transition}
    resolve_inventory_origin(origin, contract, source_id, store, before_time)
    return [origin]


def _entry_identity(entry):
    if entry.get('kind') == 'bounded_candidate_result':
        return ('bounded', entry['diagnostic']['sha256'], entry['sourceResultIndex'])
    if entry.get('kind') == 'explicit_qualification_page':
        return ('explicit', entry['proof']['record']['sha256'], entry['proof']['priorTargetIndex'])
    require(False, 'QUALIFICATION_INVENTORY_ENTRY_KIND_INVALID')


def _sparse_adapter(original, source_id, selected=None):
    from onboarding import (BOUNDED_CANDIDATE_BINDINGS, BOUNDED_CANDIDATE_BINDINGS_V2,
                            BOUNDED_CANDIDATE_BINDINGS_V3, _candidate_adapter)
    index, candidate, adapter, _ = _binding(original, source_id)
    if selected is None:
        return adapter
    require((source_id, selected.get('url'), selected.get('htmlCompleteness')) in
            (BOUNDED_CANDIDATE_BINDINGS[index], BOUNDED_CANDIDATE_BINDINGS_V2[index],
             BOUNDED_CANDIDATE_BINDINGS_V3[index]),
            'QUALIFICATION_INVENTORY_SPARSE_ADAPTER_NOT_APPROVED')
    derived = _candidate_adapter(candidate, selected['url'], selected['htmlCompleteness'])
    require(digest(derived) == digest(selected), 'QUALIFICATION_INVENTORY_SPARSE_ADAPTER_CONTEXT_DIFFERS')
    return derived


def _explicit_inventory(store, entry, baseline, source_id, main_adapter=None):
    from onboarding import _qualification_explicit_observation, _qualification_proof_policy
    from discovery import parse_source_html_index
    require(set(entry) == {'kind', 'originalContract', 'proof'} and entry['kind'] == 'explicit_qualification_page',
            'QUALIFICATION_INVENTORY_EXPLICIT_SCHEMA_INVALID')
    original = _contract(store, entry['originalContract'])
    _same_candidate_context(original, baseline, source_id, allow_d112=True)
    adapter = _sparse_adapter(original, source_id, main_adapter)
    _, baseline_candidate, _, _ = _binding(baseline, source_id)
    proof = entry['proof']
    require(type(proof) is dict and proof.get('type') == 'qualification_observation', 'QUALIFICATION_INVENTORY_EXPLICIT_PROOF_INVALID')
    fields = {'type', 'record', 'body', 'fetchedAt', 'observation', 'priorTargetId',
              'priorTargetIndex', 'priorTargetSha256', 'priorPlanRawSha256', 'priorPlanCanonicalSha256'}
    require(('priorPlanReference' in proof) != ('priorPlanRaw' in proof), 'QUALIFICATION_INVENTORY_EXPLICIT_PLAN_REPRESENTATION')
    fields.add('priorPlanReference' if 'priorPlanReference' in proof else 'priorPlanRaw')
    if 'historicalPolicyBridge' in proof:
        fields.add('historicalPolicyBridge')
    require(set(proof) == fields, 'QUALIFICATION_INVENTORY_EXPLICIT_PROOF_SCHEMA_INVALID')
    record = _json(store, proof['record'], r'ci/source-probe-runs/[0-9]+-[0-9]+\.json')
    require(record.get('checkpointProfile') == 'source_probe' and
            record.get('githubEventName') == 'workflow_dispatch' and record.get('githubRef') == 'refs/heads/main' and
            type(record.get('githubRunId')) in (str, int) and str(record['githubRunId']).isdigit() and
            type(record.get('githubRunAttempt')) in (str, int) and str(record['githubRunAttempt']).isdigit() and
            int(record['githubRunAttempt']) > 0 and proof['record']['key'] ==
            f"ci/source-probe-runs/{record['githubRunId']}-{record['githubRunAttempt']}.json" and
            all(type(record.get(k)) is int and record[k] == 0 for k in
                ('modelCalls', 'sourceChecksCredited', 'qualifiedSources')) and
            record.get('semanticAdmission') is False and record.get('coverageCredit') is False,
            'QUALIFICATION_INVENTORY_EXPLICIT_RUN_ENVELOPE_DIFFERS')
    checked_contract, checked_source = _qualification_proof_policy(record, proof, baseline_candidate, baseline, store)
    require(digest(checked_contract) == digest(original), 'QUALIFICATION_INVENTORY_EXPLICIT_POLICY_DIFFERS')
    observed = _qualification_explicit_observation(record, proof, checked_source, checked_contract, store)
    require(observed.get('status') == 'fetched' and observed.get('httpStatus') == 200 and
            observed.get('requestedUrl') == observed.get('finalUrl') and observed.get('body') == proof['body'] and
            observed.get('fetchedAt') == proof['fetchedAt'], 'QUALIFICATION_INVENTORY_EXPLICIT_OBSERVATION_DIFFERS')
    body = _json_body(store, proof['body'])
    parsed = parse_source_html_index(adapter, observed['requestedUrl'], body, 1, observed['fetchedAt'])
    return set(parsed['items']), parsed['dates'], observed['fetchedAt'], [{'observation': proof['observation'],
            'body': proof['body'], 'fetchedAt': observed['fetchedAt'], 'pageUrl': observed['requestedUrl'],
            'items': sorted(parsed['items']), 'dates': parsed['dates'], 'adapterSha256': digest(adapter)}]


def _json_body(store, ref):
    require(type(ref) is dict and set(ref) == {'key', 'sha256', 'bytes'} and
            isinstance(ref.get('sha256'), str) and re.fullmatch(r'[a-f0-9]{64}', ref['sha256']) and
            ref.get('key') == 'objects/' + ref['sha256'] and type(ref.get('bytes')) is int and
            0 < ref['bytes'] <= 32_000_000, 'QUALIFICATION_INVENTORY_BODY_REFERENCE_INVALID')
    raw = store.get(ref)
    require(digest(raw) == ref['sha256'] and len(raw) == ref['bytes'], 'QUALIFICATION_INVENTORY_BODY_INTEGRITY_DIFFERS')
    return raw


def _bounded_inventory(store, entry, baseline, source_id):
    from onboarding import _read_bounded_candidate_observation
    original, replay, result, _, _, _ = _result(store, entry)
    _same_candidate_context(original, baseline, source_id)
    require(result['sourceId'] == source_id, 'QUALIFICATION_INVENTORY_PARTIAL_SOURCE_DIFFERS')
    binding = replay['plan']['sources'][entry['sourceResultIndex']]
    provenance = []
    for page in result['observations']:
        parsed = page['parser']
        if not isinstance(parsed, dict) or 'items' not in parsed:
            continue
        observed = _read_bounded_candidate_observation(store, page['observation'], binding, page['url'])
        provenance.append({'observation': page['observation'], 'body': observed['body'],
                           'fetchedAt': observed['fetchedAt'], 'pageUrl': page['url'],
                           'items': parsed['items'], 'dates': parsed['dates']})
    return set(result['inventory']['items']), result['inventory']['dates'], replay['report']['checkedAt'], provenance


def _required_inventory_hints(store, baseline, source_id, completed, authority, main_adapter):
    """Listed record metadata discovers candidates; each entry replays separately.

    Inspect only the finite externally authenticated record set. A mutable directory
    listing, unlisted matching record or raw card hint never adds trusted authority.
    """
    from discovery import parse_source_html_index
    required = set()
    for listed in authority['diagnostics']:
        record = _json(store, listed['record'], r'ci/source-probe-runs/[0-9]+-[0-9]+\.json')
        diagnostic = record.get('diagnostic', {})
        at = diagnostic.get('checkedAt')
        policy_hash = record.get('contractSha256')
        if (not isinstance(at, str) or instant(at) > instant(completed) or
                not isinstance(policy_hash, str) or not re.fullmatch(r'[a-f0-9]{64}', policy_hash)):
            continue
        original = _contract(store, listed['originalContract'])
        require(digest(original) == policy_hash, 'QUALIFICATION_INVENTORY_HINT_POLICY_INTEGRITY_DIFFERS')
        try:
            _same_candidate_context(original, baseline, source_id, allow_d112=True)
        except ValueError:
            continue
        if diagnostic.get('operation') == 'bounded_candidate_traversal':
            for index, result in enumerate(diagnostic.get('sources', [])):
                if result.get('sourceId') == source_id and result.get('inventory', {}).get('items'):
                    required.add(('bounded', listed['record']['sha256'], index))
            continue
        adapter = _sparse_adapter(original, source_id, main_adapter)
        rows = diagnostic.get('qualification', {}).get('targets', [])
        for index, row in enumerate(rows):
            if (row.get('sourceId') != source_id or row.get('expectedFormat') != 'html' or
                    not isinstance(row.get('observation'), dict)):
                continue
            observed = _json(store, row['observation'], r'objects/[a-f0-9]{64}')
            if (observed.get('status') != 'fetched' or observed.get('httpStatus') != 200 or
                    observed.get('requestedUrl') != row.get('url') or observed.get('finalUrl') != row.get('url')):
                continue
            try:
                parsed = parse_source_html_index(adapter, row['url'], _json_body(store, observed['body']),
                                                 1, observed['fetchedAt'])
            except (ValueError, KeyError, TypeError):
                continue  # A primary article, RSS page or corporate sitemap is outside this layout.
            if parsed['items']:
                required.add(('explicit', listed['record']['sha256'], index))
    return required


def resolve_inventory_origin(origin, contract, source_id, store, before_time=None):
    require(type(origin) is dict and set(origin) == {'kind', 'sourceId', 'qualificationOrigin', 'transition'} and
            origin['kind'] == PREDECESSOR_KIND and origin['sourceId'] == source_id,
            'QUALIFICATION_PREDECESSOR_SCHEMA_INVALID')
    source = next((s for s in contract['sources'] if s['id'] == source_id), None)
    require(source and digest(source.get('qualificationOrigin')) == digest(origin['qualificationOrigin']),
            'QUALIFICATION_PREDECESSOR_SOURCE_DIFFERS')
    resolved, authority = _transition(store, origin['transition'], contract)
    require(source_id in resolved, 'QUALIFICATION_PREDECESSOR_SOURCE_NOT_IN_TRANSITION')
    pointer, original, main = resolved[source_id]
    main_adapter = main['plan']['sources'][pointer['sourceResultIndex']]['adapter']
    completed = main['report']['checkedAt']
    if before_time is not None:
        require(instant(completed) <= instant(before_time), 'QUALIFICATION_PREDECESSOR_FUTURE')
    manifest = _json(store, pointer['inventoryManifest'], r'objects/[a-f0-9]{64}')
    require(set(manifest) == {'schemaVersion', 'kind', 'sourceId', 'entries'} and
            type(manifest['schemaVersion']) is int and manifest['schemaVersion'] == 1 and
            manifest['kind'] == 'qualification_inventory_manifest' and manifest['sourceId'] == source_id and
            type(manifest['entries']) is list and manifest['entries'], 'QUALIFICATION_INVENTORY_MANIFEST_SCHEMA_INVALID')
    hashes = [digest(entry) for entry in manifest['entries']]
    require(hashes == sorted(set(hashes)), 'QUALIFICATION_INVENTORY_MANIFEST_DUPLICATE_OR_ORDER')
    require(sum(digest(entry) == digest(_main_entry(pointer)) for entry in manifest['entries']) == 1,
            'QUALIFICATION_INVENTORY_MAIN_RESULT_OMITTED')
    items, provenance, identities = set(), [], set()
    for entry in manifest['entries']:
        require(type(entry) is dict, 'QUALIFICATION_INVENTORY_ENTRY_INVALID')
        identity = _entry_identity(entry)
        require(identity not in identities, 'QUALIFICATION_INVENTORY_DUPLICATE_ORIGIN')
        identities.add(identity)
        if entry['kind'] == 'bounded_candidate_result':
            _, replayed, _, _, _, _ = _result(store, entry)
            recorded = _listed_diagnostic(authority, store, entry['diagnostic'], entry['originalContract'],
                                          replayed['plan']['rawSha256'], replayed['plan']['canonicalSha256'])
        else:
            proof = entry['proof']
            recorded = _listed_diagnostic(authority, store, proof['record'], entry['originalContract'],
                                          proof['priorPlanRawSha256'], proof['priorPlanCanonicalSha256'])
        require(instant(recorded['diagnostic']['checkedAt']) <= instant(completed),
                'QUALIFICATION_INVENTORY_FUTURE_PARTIAL')
        if entry['kind'] == 'bounded_candidate_result':
            observed_items, dates, observed_at, pages = _bounded_inventory(store, entry, original, source_id)
        else:
            observed_items, dates, observed_at, pages = _explicit_inventory(store, entry, original, source_id, main_adapter)
        require(instant(observed_at) <= instant(completed), 'QUALIFICATION_INVENTORY_FUTURE_PARTIAL')
        items.update(observed_items)
        provenance.append({'origin': copy.deepcopy(entry), 'observedAt': observed_at,
                           'items': sorted(observed_items), 'dates': dates, 'pages': pages})
    require(_required_inventory_hints(store, original, source_id, completed, authority, main_adapter).issubset(identities),
            'QUALIFICATION_INVENTORY_OMITTED_RETAINED_PAGE')
    return {'sourceId': source_id, 'items': sorted(items), 'completedAt': completed,
            'provenance': provenance, 'authority': 'inventory_only'}
