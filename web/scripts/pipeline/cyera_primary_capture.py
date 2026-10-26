"""Dormant exact Cyera primary capture. Evidence only; no source or fact credit."""
import copy
import json
from collections import Counter
from datetime import timezone
from pathlib import Path

from contracts import digest, instant, require
from onboarding import (PersistentProbeBudget, ProbeReservationDenied,
                        _validate_legacy_qualification_probe_plan, _qualification_explicit_observation)
from q4_press_list import _object, _constant
import q4_primary_qualification as primary
import q4_qualification_origin as origin
from cyera_press_list import parse_press_list, inventory_csv

OPERATION = 'bounded_cyera_primary_capture'
POLICY_SHA256 = origin.AUTHORITY['activatedContractSha256']
MAX_REQUESTS = 1
MAX_BODY_BYTES = 2_000_000
REPO = Path(__file__).resolve().parents[3]
PLAN_CANONICAL_SHA256 = '25bf0ff72555188e7a8446b9499f3b8ba56c9327e397f8b70a5ce9deb82d350f'
CSV_PATH = 'docs/active/daily-pipeline/accuracy/cyera-retained-56-card-inventory.csv'
_zero, _blob, _body, _read_observed = primary._zero, primary._blob, primary._body, primary._read_observed
ZERO_FIELDS = primary.ZERO_FIELDS


class _AuthenticatedReads:
    """Legacy validators retain their policy checks; every referenced raw read is sealed here."""
    def __init__(self, store): self.store = store
    def read(self, key): return self.store.read(key)
    def get(self, ref):
        raw = self.store.get(ref)
        require(type(raw) is bytes and len(raw) == ref['bytes'] and digest(raw) == ref['sha256'],
                'CYERA_H_REFERENCED_BYTES_DIFFER')
        return raw


def _validate_capture(contract, store, plan):
    history, index = plan['historicalReplay'], plan['retainedIndex']
    old = origin.inverse_policy(contract, store)
    require(digest(old) == history['originalPolicySha256'] and history['originalContract'] == origin.AUTHORITY['originalContract'] and
            history['currentToOriginalTransition'] == origin.AUTHORITY['transition'], 'CYERA_EXACT_H_INVERSE_DIFFERS')
    source = next(s for s in contract['sources'] if s['id'] == plan['source']['sourceId'])
    old_source = next(s for s in old['sources'] if s['id'] == source['id'])
    require(source == old_source and digest(source) == plan['source']['originalSourceSha256'] and
            source['supplierId'] == plan['source']['supplierId'] and source['family'] == plan['source']['family'] and
            source['registration'] == 'candidate' and source['kind'] == 'official_discovery' and
            source['url'] == 'https://www.cyera.com/' and source['allowedHosts'] == ['www.cyera.com'] and
            source['seedEvidenceUrls'] == index['knownSeedUrls'], 'CYERA_EXACT_SOURCE_DIFFERS')
    review_pin = history['review']
    review_raw = (REPO / review_pin['path']).read_bytes()
    require(len(review_raw) == review_pin['bytes'] and digest(review_raw) == review_pin['sha256'], 'CYERA_H_AUDIT_DIFFERS')
    audit = json.loads(review_raw)
    require(audit['verdict'] == 'PASS' and audit['artifact'] == history['artifact'] and
            audit['acknowledgedArchive']['commit'] == history['archive']['commit'] and
            audit['acknowledgedArchive']['manifestSha256'] == history['archive']['manifestSha256'] and
            audit['acknowledgedArchive']['files'] == history['archive']['manifestFiles'] and
            audit['manifest']['bytes'] == history['archive']['manifestBytes'], 'CYERA_H_ARCHIVE_JOIN_DIFFERS')
    record = json.loads(_blob(store, history['record'], r'ci/source-probe-runs/40193925490-1\.json'))
    require(all(type(record.get(k)) is type(v) and record[k] == v for k, v in history['outerIdentity'].items()) and
            record['checkpointProfile'] == 'source_probe' and record['contractSha256'] == digest(old) and
            record['apiFallback'] is False and all(record[k] is False for k in ('semanticAdmission', 'coverageCredit')) and
            all(type(record[k]) is int and record[k] == 0 for k in ZERO_FIELDS), 'CYERA_H_OUTER_IDENTITY_DIFFERS')
    proof = history['startProof']
    old_raw = _blob(store, proof['priorPlanReference'])
    _validate_legacy_qualification_probe_plan(old, store, None, raw=old_raw, plan=json.loads(old_raw))
    observed = _qualification_explicit_observation(record, proof, old_source, old, store)
    require(observed.get('status') == 'fetched' and type(observed.get('httpStatus')) is int and observed['httpStatus'] == 200 and
            observed.get('requestedUrl') == observed.get('finalUrl') == index['url'] and
            observed.get('fetchedAt') == index['fetchedAt'] == proof['fetchedAt'] and
            observed.get('body') == index['body'] == proof['body'] and index['observation'] == proof['observation'] and
            observed.get('contentType', '').lower() == 'text/html; charset=utf-8', 'CYERA_H_INDEX_RESPONSE_DIFFERS')
    stream = parse_press_list(_blob(store, index['body']), source['id'], index['fetchedAt'],
                              contract['collection']['currentWindowDays'], source['seedEvidenceUrls'])
    require(stream['parserVersion'] == index['parserVersion'] and len(stream['records']) == index['expectedCards'] and
            all(stream[k] == index[k] for k in ('itemsSha256', 'recordsSha256', 'knownSeedMembershipSha256')) and
            stream['windowStart'] == index['originalWindowStart'] and stream['windowEnd'] == index['originalWindowEnd'] and
            stream['dailyWindowComplete'] and all(stream['knownSeedMembership'].values()), 'CYERA_RETAINED_STREAM_DIFFERS')
    csv = (REPO / CSV_PATH).read_bytes()
    require(index['inventoryCsv']['filename'] == Path(CSV_PATH).name and len(csv) == index['inventoryCsv']['bytes'] and
            digest(csv) == index['inventoryCsv']['sha256'] and csv == inventory_csv(stream), 'CYERA_RETAINED_CSV_DIFFERS')
    row = stream['records'][plan['sample']['rowIndex']]
    core = {k:v for k,v in row.items() if k not in ('sourceId', 'timezone')}
    sample = {**core, 'recordSha256': digest(core), 'request': {'method': 'GET', 'url': row['url'], 'body': None}}
    require(sample == plan['sample'] and row['url'] in stream['currentWindowItems'] and
            row['url'] not in stream['boundaryAmbiguousItems'], 'CYERA_CURRENT_SAMPLE_DIFFERS')
    stream = {**stream, 'historicalReplay': copy.deepcopy(history), 'indexBody': index['body'],
              'indexObservation': index['observation'], 'inventoryCsv': index['inventoryCsv']}
    target = {'sourceId': source['id'], 'supplierId': source['supplierId'], 'sourceSha256': digest(source),
              'source': copy.deepcopy(source), 'url': row['url'], 'sample': sample}
    return [target], [stream]


def validate_plan(contract, store, raw, path=None):
    require(type(raw) is bytes and 0 < len(raw) <= 1_000_000, 'CYERA_PLAN_SIZE_INVALID')
    plan = json.loads(raw, object_pairs_hook=_object, parse_constant=_constant)
    require(type(plan) is dict and digest(raw) == digest(plan) == PLAN_CANONICAL_SHA256 and
            type(plan['schemaVersion']) is int and plan['schemaVersion'] == 2 and plan['operation'] == OPERATION and
            type(plan['maxRequests']) is int and plan['maxRequests'] == MAX_REQUESTS and
            plan['marketSha256'] == digest(contract) == POLICY_SHA256, 'CYERA_EXACT_REVIEWED_PLAN_REQUIRED')
    targets, streams = _validate_capture(contract, _AuthenticatedReads(store), plan)
    return {'operation': OPERATION, 'path': str(path) if path is not None else None,
            'rawSha256': digest(raw), 'canonicalSha256': digest(plan), 'plan': plan, 'targets': targets, 'streams': streams}


def _primary_response(store, observed, target, requested_at, checked_at, day):
    shape = primary._primary_response(store, observed, target, requested_at, checked_at, day)
    require(type(shape.get('readableCharacters')) is int and shape['readableCharacters'] > 0, 'CYERA_PRIMARY_UNREADABLE')
    return shape


def _results(store, plan, requests, started_at, checked_at, day):
    require(type(requests) is list and len(requests) <= MAX_REQUESTS, 'CYERA_PRIMARY_REQUEST_INVENTORY_INVALID')
    start, end = instant(started_at), instant(checked_at)
    require(start <= end, 'CYERA_PRIMARY_COMPLETION_TIME_REGRESSED')
    results = []
    for request, target in zip(requests, plan['targets']):
        require(type(request) is dict and set(request) == {'sourceId', 'url', 'requestedAt', 'reservation', 'observation',
                'responseCheckedAt', 'transportError', 'denial'} and request['sourceId'] == target['sourceId'] and
                request['url'] == target['url'], 'CYERA_PRIMARY_REQUEST_TARGET_DIFFERS')
        if request['requestedAt'] is not None:
            at = instant(request['requestedAt'])
            require(request['reservation'] is not None and start <= at <= end and
                    at.astimezone(timezone.utc).date().isoformat() == day, 'CYERA_PRIMARY_ATTEMPT_TIME_INVALID')
        result = {'sourceId': target['sourceId'], 'requestedUrl': target['url'], 'observation': request['observation'],
                  'accepted': False, 'finalUrl': None, 'fetchedAt': None, 'httpStatus': None, 'contentType': None,
                  'body': None, 'primaryShape': None, 'reason': 'TRANSPORT_NOT_OBSERVED', **_zero()}
        if request['observation'] is not None:
            require(request['reservation'] is not None and request['transportError'] is None and request['denial'] is None,
                    'CYERA_PRIMARY_OBSERVATION_WITHOUT_REQUEST_INVALID')
            require(request['requestedAt'] is not None and isinstance(request['responseCheckedAt'], str) and
                    instant(request['requestedAt']) <= instant(request['responseCheckedAt']) <= end,
                    'CYERA_PRIMARY_RESPONSE_CHECK_TIME_INVALID')
            observed = _read_observed(store, request['observation'], target)
            for key in ('finalUrl', 'fetchedAt', 'httpStatus', 'contentType', 'body'):
                result[key] = copy.deepcopy(observed.get(key))
            # A body, when returned, must remain authentic even for a rejected response.
            if observed.get('body') is not None:
                _body(store, observed['body'])
            try:
                shape = _primary_response(store, observed, target, instant(request['requestedAt']),
                                          instant(request['responseCheckedAt']), day)
                result.update(accepted=True, primaryShape=shape, reason='PRIMARY_SAMPLE_MATCHED_PROPOSAL_ONLY')
            except (ValueError, KeyError, TypeError, UnicodeError, RecursionError) as error:
                result['reason'] = type(error).__name__ + ':' + str(error)[:160]
        else:
            require(request['responseCheckedAt'] is None and
                    (isinstance(request['denial'], str) and request['transportError'] is None or
                     request['denial'] is None and request['reservation'] is not None and
                     request['requestedAt'] is not None and isinstance(request['transportError'], str)),
                    'CYERA_PRIMARY_UNOBSERVED_REQUEST_INVALID')
        results.append(result)
    return results


def _seal(contract, store, raw, report, budget):
    validate_plan(contract, store, raw)
    try:
        budget.before_fetch()
        report['checkedAt'] = budget.clock()
        budget.before_fetch()
    except ProbeReservationDenied as error:
        report['completionDenials'].append(error.reason)
        report['checkedAt'] = budget.clock()
    report['reservationContext'] = budget.summary()
    report['budgetDenied'] = bool(report['reservationContext']['reservationDenials'])
    report['executionCompleted'] = not report['budgetDenied']
    plan = validate_plan(contract, store, raw)
    report['streams'] = plan['streams']
    report['results'] = _results(store, plan, report['requests'], report['startedAt'], report['checkedAt'], budget.day)
    report['acceptedSamples'] = sum(row['accepted'] for row in report['results'])
    report['proposalEvidenceComplete'] = report['executionCompleted'] and report['acceptedSamples'] == MAX_REQUESTS
    verify_report(contract, store, raw, report)
    return report


def execute(contract, store, fetcher, budget, normalized_plan):
    require(isinstance(budget, PersistentProbeBudget), 'CYERA_PRIMARY_BOUND_BUDGET_REQUIRED')
    budget.assert_bound(store, contract)
    require(normalized_plan.get('operation') == OPERATION and isinstance(normalized_plan.get('path'), str),
            'CYERA_PRIMARY_CURRENT_PLAN_PATH_REQUIRED')
    raw = Path(normalized_plan['path']).read_bytes()
    require(digest(raw) == normalized_plan.get('rawSha256'), 'CYERA_PRIMARY_CURRENT_PLAN_CHANGED')
    plan = validate_plan(contract, store, raw, normalized_plan['path'])
    require(budget.reservations == 0, 'CYERA_PRIMARY_EXCLUSIVE_BUDGET_REQUIRED')
    plan_ref = store.put(raw)
    requests = []
    for target in plan['targets']:
        request = {'sourceId': target['sourceId'], 'url': target['url'], 'requestedAt': None,
                   'reservation': None, 'observation': None, 'responseCheckedAt': None,
                   'transportError': None, 'denial': None}
        requests.append(request)
        try:
            request['reservation'] = budget.reserve_fetch()
            budget.before_fetch()
            request['requestedAt'] = budget.clock()
            budget.before_fetch()
        except ProbeReservationDenied as error:
            # No transport was invoked. Keep the reservation and denial without
            # presenting the intermediate guard clock as an actual request time.
            request['requestedAt'] = None
            request['denial'] = error.reason
            break
        try:
            observed = fetcher.fetch(target['source'], target['url'], previous=None, attempt=2)
            raw_ref = store.put(observed)
            request['observation'] = store.put({'schemaVersion': 1, 'sourceId': target['sourceId'],
                'sourceSha256': target['sourceSha256'], 'requestedUrl': target['url'], 'rawObservation': raw_ref})
            request['responseCheckedAt'] = budget.clock()
        except (OSError, ValueError, RuntimeError) as error:
            request['transportError'] = type(error).__name__ + ':' + str(error)[:120]
    report = {'schemaVersion': 1, 'operation': OPERATION, 'contractSha256': digest(contract),
              'planRawSha256': digest(raw), 'planCanonicalSha256': plan['canonicalSha256'], 'planReference': plan_ref,
              'startedAt': budget.started_at, 'requests': requests, 'completionDenials': [], **_zero()}
    return _seal(contract, store, raw, report, budget)


def finalize_report(contract, store, raw, report, budget):
    require(isinstance(budget, PersistentProbeBudget), 'CYERA_PRIMARY_BOUND_BUDGET_REQUIRED')
    budget.assert_bound(store, contract)
    verify_report(contract, store, raw, report)
    return _seal(contract, store, raw, report, budget)


def verify_report(contract, store, raw, report):
    """Replay retained script captures and exact reservations without transport."""
    plan = validate_plan(contract, store, raw)
    fields = {'schemaVersion', 'operation', 'contractSha256', 'planRawSha256', 'planCanonicalSha256', 'planReference',
              'startedAt', 'checkedAt', 'requests', 'completionDenials', 'reservationContext', 'budgetDenied',
              'executionCompleted', 'streams', 'results', 'acceptedSamples', 'proposalEvidenceComplete', *_zero()}
    require(type(report) is dict and set(report) == fields and type(report['schemaVersion']) is int and
            report['schemaVersion'] == 1 and report['operation'] == OPERATION and
            report['contractSha256'] == POLICY_SHA256 and report['planRawSha256'] == digest(raw) and
            report['planCanonicalSha256'] == plan['canonicalSha256'] and _blob(store, report['planReference']) == raw and
            all(report[k] is False for k in ('qualified', 'semanticAdmission', 'coverageCredit')) and report['facts'] == [] and
            all(type(report[k]) is int and report[k] == 0 for k in ZERO_FIELDS) and
            type(report['completionDenials']) is list and len(report['completionDenials']) <= 2 and
            all(isinstance(d, str) and d for d in report['completionDenials']), 'CYERA_PRIMARY_REPORT_ENVELOPE_DIFFERS')
    require(digest(report['streams']) == digest(plan['streams']), 'CYERA_PRIMARY_REPLAYED_STREAMS_DIFFER')
    context = report['reservationContext']
    require(type(context) is dict and set(context) == {'budgetDay', 'contractSha256', 'fetchLimit', 'maximumRuntimeSeconds',
            'startedAt', 'initialBudget', 'currentBudget', 'probeFetchReservations', 'reservationDenials'} and
            context['contractSha256'] == POLICY_SHA256 and context['startedAt'] == report['startedAt'] and
            type(context['fetchLimit']) is int and context['fetchLimit'] == contract['schedule']['maxFetchesPerRun'] and
            type(context['maximumRuntimeSeconds']) is int and 0 < context['maximumRuntimeSeconds'] <= min(1200, contract['schedule'].get('maxRuntimeSeconds', 7200)) and
            type(context['probeFetchReservations']) is int and 0 <= context['probeFetchReservations'] <= MAX_REQUESTS and
            type(context['reservationDenials']) is dict and
            all(isinstance(k, str) and type(v) is int and v > 0 for k, v in context['reservationDenials'].items()),
            'CYERA_PRIMARY_RESERVATION_CONTEXT_INVALID')
    require(all(context[k] is None or type(context[k]) is dict for k in ('initialBudget', 'currentBudget')),
            'CYERA_PRIMARY_BUDGET_HEAD_SHAPE_INVALID')
    initial = context['initialBudget'] if context['initialBudget'] is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
    current = context['currentBudget'] if context['currentBudget'] is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
    require(type(initial) is dict and type(current) is dict and all(type(b.get(k)) is int and b[k] >= 0
            for b in (initial, current) for k in ('calls', 'documents', 'fetches')) and
            {k: v for k, v in initial.items() if k != 'fetches'} == {k: v for k, v in current.items() if k != 'fetches'} and
            current['fetches'] <= context['fetchLimit'] and
            current['fetches'] - initial['fetches'] == context['probeFetchReservations'], 'CYERA_PRIMARY_COUNTERS_DIFFER')
    results = _results(store, plan, report['requests'], report['startedAt'], report['checkedAt'], context['budgetDay'])
    charges, denials = [], Counter(report['completionDenials'])
    for index, request in enumerate(report['requests']):
        reservation = request['reservation']
        if reservation is not None:
            require(type(reservation) is dict and set(reservation) == {'budgetDay', 'fetchLimit', 'chargedFetchCount'} and
                    reservation['budgetDay'] == context['budgetDay'] and type(reservation['fetchLimit']) is int and
                    reservation['fetchLimit'] == context['fetchLimit'] and type(reservation['chargedFetchCount']) is int,
                    'CYERA_PRIMARY_RESERVATION_INVALID')
            charges.append(reservation['chargedFetchCount'])
        if request['denial'] is not None:
            require(isinstance(request['denial'], str) and index == len(report['requests']) - 1, 'CYERA_PRIMARY_DENIAL_MUST_STOP_TRANSPORT')
            denials[request['denial']] += 1
    require(charges == list(range(initial['fetches'] + 1, current['fetches'] + 1)) and
            dict(denials) == context['reservationDenials'] and report['budgetDenied'] is bool(denials) and
            report['executionCompleted'] is (not bool(denials)) and
            (len(results) == MAX_REQUESTS or denials) and digest(results) == digest(report['results']) and
            type(report['acceptedSamples']) is int and report['acceptedSamples'] == sum(r['accepted'] for r in results) and
            report['proposalEvidenceComplete'] is (not bool(denials) and report['acceptedSamples'] == MAX_REQUESTS),
            'CYERA_PRIMARY_REPLAYED_RESULTS_OR_CHARGES_DIFFER')
    start, end = instant(report['startedAt']).astimezone(timezone.utc), instant(report['checkedAt']).astimezone(timezone.utc)
    require(start.date().isoformat() == context['budgetDay'], 'CYERA_PRIMARY_START_DAY_DIFFERS')
    if end.date().isoformat() != context['budgetDay'] or (end - start).total_seconds() >= context['maximumRuntimeSeconds']:
        require(denials and not report['proposalEvidenceComplete'], 'CYERA_PRIMARY_EXPIRED_CAPTURE_CANNOT_COMPLETE')
    return {'proposalEvidenceComplete': report['proposalEvidenceComplete'], 'acceptedSamples': report['acceptedSamples'], **_zero()}
