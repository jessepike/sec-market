"""Versioned intake/reporting semantics and exact subject-policy migration."""
import copy
import json

from contracts import digest, instant, require

MODE = 'daily_intake_with_separate_history'
MEASURE = 'daily_source_intake_v2'


def enabled(contract):
    return contract.get('collection', {}).get('mode') == MODE


def audit_version(contract):
    return 2 if enabled(contract) else 1


def original_contract(store, origin):
    plan = store.read('runs/' + origin['runId'] + '/plan.json')
    require(plan is not None, 'Original policy plan missing')
    contract = store.read('contracts/' + plan['contractSha256'] + '.json')
    require(contract is not None and digest(contract) == plan['contractSha256'], 'Original contract integrity differs')
    return contract


def semantic_context(contract, source_id):
    source = next((s for s in contract['sources'] if s['id'] == source_id), None)
    require(source is not None, 'Semantic source binding missing')
    supplier = next(s for s in contract['suppliers'] if s['id'] == source['supplierId'])
    policy = copy.deepcopy({k: v for k, v in contract.items() if k not in ('version', 'sources', 'suppliers')})
    policy.get('collection', {}).pop('mode', None)
    # Archive/fetch-check settings decide what is looked at, not how a document is
    # judged, so they cannot invalidate earlier reviews. Absent in older policies.
    for key in ('historyWindowDays', 'maxFetchAuditDocumentsPerSource'):
        policy.get('collection', {}).pop(key, None)
    return {'policy': policy, 'supplier': supplier, 'source': source,
            'semanticReviewRules': 'source-statement-and-review-checks-v1'}


def bridge(original, current, source_id):
    old_context, context = semantic_context(original, source_id), semantic_context(current, source_id)
    require(old_context == context, 'Retained semantic policy/source/supplier context differs')
    return {'schemaVersion': 1, 'originalContractSha256': digest(original),
            'currentContractSha256': digest(current), 'semanticContextSha256': digest(context)}


def compatible(original, current, source_id):
    try:
        bridge(original, current, source_id)
        return True
    except (ValueError, KeyError, StopIteration):
        return False


def document_context(source, observed, view):
    return {'sourceId': source['id'], 'requestedUrl': observed['requestedUrl'],
            'finalUrl': observed.get('finalUrl', observed['requestedUrl']), 'contentType': observed.get('contentType'),
            'extractor': view['extractor'], 'modelTextSha256': digest(view['modelText'].encode()),
            'compressedInput': view['compressedInput']}


def document_cache_key(contract, source, observed, view):
    value = {'supplier': source['supplierId'], 'body': observed['body']['sha256'],
             'contract': digest(contract), 'extractor': view['extractor']}
    if enabled(contract):
        value['inputContext'] = document_context(source, observed, view)
    return digest(value)


def summary(inventory, reviewed, held, pending, **extra):
    require(reviewed | pending == inventory and not reviewed & pending and held.issubset(reviewed),
            'Review inventory partition differs')
    return {'complete': not pending, 'inventoryDocuments': len(inventory), 'reviewedDocuments': len(reviewed),
            'pendingDocuments': len(pending), 'heldDocuments': len(held), **extra}


def totals(items, kind):
    fields = ('inventoryDocuments', 'reviewedDocuments', 'pendingDocuments', 'heldDocuments')
    if kind == 'processing':
        fields += ('changedDocuments', 'unknownDateDocuments')
        # Present only under policies with a history window.
        fields += tuple(f for f in ('archivedDocuments', 'notAboutSupplierDocuments')
                        if any(f in item[kind] for item in items))
    return {'complete': all(item[kind]['complete'] for item in items),
            **{field: sum(item[kind].get(field, 0) for item in items) for field in fields}}


def source_measure(receipt, source, contract, at, store, bounded_details=None, legacy_ok=False):
    """Derive separate measures; bounded_details comes only from independent replay."""
    empty = summary(set(), set(), set(), set())
    if bounded_details is not None:
        intake_ok = bounded_details['intakeComplete']
        details = bounded_details
    else:
        intake_ok = legacy_ok
        zero = {'archivedDocuments': 0, 'notAboutSupplierDocuments': 0} if 'historyWindowDays' in contract.get('collection', {}) else {}
        details = {'processing': {**empty, 'changedDocuments': 0, 'unknownDateDocuments': 0, **zero},
                   'historicalReview': empty}
    outcome = 'checked' if intake_ok else (receipt['outcome'] if receipt['outcome'] in ('blocked', 'failed') else 'not_checked')
    return {'taskId': receipt['taskId'], 'sourceId': receipt['sourceId'], 'supplierId': receipt['supplierId'],
            'outcome': outcome, 'intakeOutcome': outcome,
            'intakeErrorCode': None if intake_ok else (receipt.get('errorCode') or 'DAILY_INTAKE_INCOMPLETE'),
            'processingOutcome': receipt['outcome'], 'processingErrorCode': receipt.get('errorCode'),
            'processing': details['processing'], 'historicalReview': details['historicalReview']}
