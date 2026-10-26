"""Dormant exact PR Newswire primary capture. Evidence only; no source or fact credit."""
import copy
import json
import re
from collections import Counter
from datetime import timezone
from pathlib import Path

from contracts import canonical, digest, instant, require
from onboarding import PersistentProbeBudget, ProbeReservationDenied
from q4_press_list import _object, _constant
import q4_primary_qualification as primary
import q4_qualification_origin as origin
import prnewswire_retained_window as retained

OPERATION = 'bounded_prnewswire_primary_capture'
POLICY_SHA256 = origin.AUTHORITY['activatedContractSha256']
MAX_REQUESTS = 2
MAX_BODY_BYTES = 2_000_000
REPO = Path(__file__).resolve().parents[3]
PLAN_CANONICAL_SHA256 = '01e468f5d73ddb28edbde014a0b725f7d202340a692964d01f6fd174faec7fb1'
_zero, _blob, _body, _read_observed = primary._zero, primary._blob, primary._body, primary._read_observed
ZERO_FIELDS = primary.ZERO_FIELDS


class _AuthenticatedReads:
    """Legacy validators retain their policy checks; every referenced raw read is sealed here."""
    def __init__(self, store): self.store = store
    def read(self, key):
        value = self.store.read(key)
        require(key == 'source-qualification-transitions/' + POLICY_SHA256 + '.json' and
                value == origin.AUTHORITY['transition'], 'PRN_EXACT_TRANSITION_POINTER_DIFFERS')
        raw = canonical(value)
        self.get({'key': key, 'sha256': digest(raw), 'bytes': len(raw)})
        return value
    def get(self, ref):
        raw = self.store.get(ref)
        require(type(raw) is bytes and len(raw) == ref['bytes'] and digest(raw) == ref['sha256'],
                'PRN_H_REFERENCED_BYTES_DIFFER')
        return raw


def _validate_capture(contract, store, plan):
    old = origin.inverse_policy(contract, store)
    require(plan['originalContract'] == origin.AUTHORITY['originalContract'] and
            plan['currentToOriginalTransition'] == origin.AUTHORITY['transition'] and digest(old) == origin.H,
            'PRN_EXACT_H_INVERSE_DIFFERS')
    pin = plan['descriptor']
    raw = (REPO / pin['path']).read_bytes()
    require(len(raw) == pin['bytes'] and digest(raw) == pin['sha256'] and
            digest(retained._json(raw)) == pin['canonicalSha256'], 'PRN_DESCRIPTOR_RAW_DIFFERS')
    report = retained.derive_report(old, store, raw)
    retained.verify_report(old, store, raw, report)
    require(digest(report) == plan['retainedReportSha256'] and report['originalRuns'] == plan['originalRuns'] and
            report['originalAsOf'] == plan['originalAsOf'], 'PRN_ORIGINAL_REPLAY_DIFFERS')
    descriptor = retained._json(raw)
    targets = []
    for row, stream, original in zip(plan['sources'], report['streams'], descriptor['sources']):
        source = next(s for s in contract['sources'] if s['id'] == row['sourceId'])
        old_source = next(s for s in old['sources'] if s['id'] == row['sourceId'])
        require(source == old_source == row['source'] and digest(source) == row['currentSourceSha256'] and
                source['family'] == 'release_distribution' and source['registration'] == 'candidate' and
                source['supplierId'] == row['supplierId'], 'PRN_CURRENT_SOURCE_DIFFERS')
        card = row['selectedRecord']
        require(card in stream['records'] and card['url'] in stream['currentWindowItems'] and
                card['boundaryAmbiguous'] is False and card['sourceId'] == row['sourceId'] and
                row['method'] == 'GET' and row['url'] == card['url'] and
                row['listPage'] == original['pages'][card['pageNumber']-1] and
                row['listPageBodySha256'] == row['listPage']['body']['sha256'] and
                row['listPageBodyBytes'] == row['listPage']['body']['bytes'], 'PRN_SELECTED_CARD_DIFFERS')
        require(row['knownInventoryUrls'] == len(stream['items']) and
                row['knownEvidenceUnionUrls'] == len(stream['knownEvidenceUnion']) and
                row['currentWindowItems'] == len(stream['currentWindowItems']) and
                all(row[k] == stream[k] for k in ('dailyWindowComplete','historicalEnumerationComplete',
                    'olderBoundary','pendingLiteralPaginationUrls','knownSeedsOutsideObservedList','sourceScopeComplete')) and
                row['existingPrimaryTemplate'] == next(p for p in report['primarySamples']
                    if p['sourceId'].startswith(source['supplierId']+':')), 'PRN_RETAINED_SCOPE_DIFFERS')
        targets.append({'sourceId': source['id'], 'supplierId': source['supplierId'], 'sourceSha256': digest(source),
                        'source': copy.deepcopy(source), 'url': card['url'], 'sample': copy.deepcopy(card)})
    return targets, report['streams']


def validate_plan(contract, store, raw, path=None):
    require(type(raw) is bytes and 0 < len(raw) <= 1_000_000, 'PRN_PLAN_SIZE_INVALID')
    plan = json.loads(raw, object_pairs_hook=_object, parse_constant=_constant)
    require(type(plan) is dict and digest(raw) == digest(plan) == PLAN_CANONICAL_SHA256 and
            type(plan['schemaVersion']) is int and plan['schemaVersion'] == 2 and plan['operation'] == OPERATION and
            type(plan['maxRequests']) is int and plan['maxRequests'] == MAX_REQUESTS and
            plan['marketSha256'] == digest(contract) == POLICY_SHA256, 'PRN_EXACT_REVIEWED_PLAN_REQUIRED')
    targets, streams = _validate_capture(contract, _AuthenticatedReads(store), plan)
    return {'operation': OPERATION, 'path': str(path) if path is not None else None,
            'rawSha256': digest(raw), 'canonicalSha256': digest(plan), 'plan': plan, 'targets': targets, 'streams': streams}


def _primary_response(store, observed, target, requested_at, checked_at, day):
    url = target['url']
    require(observed.get('requestedUrl') == observed.get('finalUrl') == url and
            observed.get('status') == 'fetched' and type(observed.get('httpStatus')) is int and
            observed['httpStatus'] == 200 and
            (observed.get('redirectDiagnostics') is None or type(observed['redirectDiagnostics']) is dict and
             not observed['redirectDiagnostics'].get('responses') and
             not observed['redirectDiagnostics'].get('responsesTruncated') and
             not observed['redirectDiagnostics'].get('lastHttpError')), 'PRN_PRIMARY_HTTP_OR_FINAL_URL_INVALID')
    fetched = instant(observed['fetchedAt']).astimezone(timezone.utc)
    require(requested_at <= fetched <= checked_at and fetched.date().isoformat() == day,
            'PRN_PRIMARY_RESPONSE_TIME_INVALID')
    require(isinstance(observed.get('contentType'), str) and re.fullmatch(
            r'(?:text/html|application/xhtml\+xml)(?:\s*;\s*charset\s*=\s*(?:utf-8|"utf-8"))?\s*',
            observed['contentType'], re.I), 'PRN_PRIMARY_HTML_MIME_INVALID')
    shape = retained.primary_shape(_body(store, observed.get('body')), url, target['sourceId'],
                                   target['sample']['calendarDay'])
    require(shape['heading'] == target['sample']['title'], 'PRN_PRIMARY_HEADING_CARD_DIFFERS')
    return {**shape, 'indexDateLiteral': target['sample']['dateLiteral'], 'selectedRecord': target['sample']}


def _results(store, plan, requests, started_at, checked_at, day):
    require(type(requests) is list and len(requests) <= MAX_REQUESTS, 'PRN_PRIMARY_REQUEST_INVENTORY_INVALID')
    start, end = instant(started_at), instant(checked_at)
    require(start <= end, 'PRN_PRIMARY_COMPLETION_TIME_REGRESSED')
    results = []
    for request, target in zip(requests, plan['targets']):
        require(type(request) is dict and set(request) == {'sourceId', 'url', 'requestedAt', 'reservation', 'observation',
                'responseCheckedAt', 'transportError', 'denial'} and request['sourceId'] == target['sourceId'] and
                request['url'] == target['url'], 'PRN_PRIMARY_REQUEST_TARGET_DIFFERS')
        if request['requestedAt'] is not None:
            at = instant(request['requestedAt'])
            require(request['reservation'] is not None and start <= at <= end and
                    at.astimezone(timezone.utc).date().isoformat() == day, 'PRN_PRIMARY_ATTEMPT_TIME_INVALID')
        result = {'sourceId': target['sourceId'], 'requestedUrl': target['url'], 'observation': request['observation'],
                  'accepted': False, 'finalUrl': None, 'fetchedAt': None, 'httpStatus': None, 'contentType': None,
                  'body': None, 'primaryShape': None, 'reason': 'TRANSPORT_NOT_OBSERVED', **_zero()}
        if request['observation'] is not None:
            require(request['reservation'] is not None and request['transportError'] is None and request['denial'] is None,
                    'PRN_PRIMARY_OBSERVATION_WITHOUT_REQUEST_INVALID')
            require(request['requestedAt'] is not None and isinstance(request['responseCheckedAt'], str) and
                    instant(request['requestedAt']) <= instant(request['responseCheckedAt']) <= end,
                    'PRN_PRIMARY_RESPONSE_CHECK_TIME_INVALID')
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
                    'PRN_PRIMARY_UNOBSERVED_REQUEST_INVALID')
        results.append(result)
    for target in plan['targets'][len(requests):]:
        results.append({'sourceId': target['sourceId'], 'requestedUrl': target['url'], 'observation': None,
            'accepted': False, 'finalUrl': None, 'fetchedAt': None, 'httpStatus': None, 'contentType': None,
            'body': None, 'primaryShape': None, 'reason': 'UNREACHED_AFTER_DENIAL', **_zero()})
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
    require(isinstance(budget, PersistentProbeBudget), 'PRN_PRIMARY_BOUND_BUDGET_REQUIRED')
    budget.assert_bound(store, contract)
    require(normalized_plan.get('operation') == OPERATION and isinstance(normalized_plan.get('path'), str),
            'PRN_PRIMARY_CURRENT_PLAN_PATH_REQUIRED')
    raw = Path(normalized_plan['path']).read_bytes()
    require(digest(raw) == normalized_plan.get('rawSha256'), 'PRN_PRIMARY_CURRENT_PLAN_CHANGED')
    plan = validate_plan(contract, store, raw, normalized_plan['path'])
    require(budget.reservations == 0, 'PRN_PRIMARY_EXCLUSIVE_BUDGET_REQUIRED')
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
    require(isinstance(budget, PersistentProbeBudget), 'PRN_PRIMARY_BOUND_BUDGET_REQUIRED')
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
            all(isinstance(d, str) and d for d in report['completionDenials']), 'PRN_PRIMARY_REPORT_ENVELOPE_DIFFERS')
    require(digest(report['streams']) == digest(plan['streams']), 'PRN_PRIMARY_REPLAYED_STREAMS_DIFFER')
    context = report['reservationContext']
    require(type(context) is dict and set(context) == {'budgetDay', 'contractSha256', 'fetchLimit', 'maximumRuntimeSeconds',
            'startedAt', 'initialBudget', 'currentBudget', 'probeFetchReservations', 'reservationDenials'} and
            context['contractSha256'] == POLICY_SHA256 and context['startedAt'] == report['startedAt'] and
            type(context['fetchLimit']) is int and context['fetchLimit'] == contract['schedule']['maxFetchesPerRun'] and
            type(context['maximumRuntimeSeconds']) is int and 0 < context['maximumRuntimeSeconds'] <= min(1200, contract['schedule'].get('maxRuntimeSeconds', 7200)) and
            type(context['probeFetchReservations']) is int and 0 <= context['probeFetchReservations'] <= MAX_REQUESTS and
            type(context['reservationDenials']) is dict and
            all(isinstance(k, str) and type(v) is int and v > 0 for k, v in context['reservationDenials'].items()),
            'PRN_PRIMARY_RESERVATION_CONTEXT_INVALID')
    require(all(context[k] is None or type(context[k]) is dict for k in ('initialBudget', 'currentBudget')),
            'PRN_PRIMARY_BUDGET_HEAD_SHAPE_INVALID')
    initial = context['initialBudget'] if context['initialBudget'] is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
    current = context['currentBudget'] if context['currentBudget'] is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
    require(type(initial) is dict and type(current) is dict and all(type(b.get(k)) is int and b[k] >= 0
            for b in (initial, current) for k in ('calls', 'documents', 'fetches')) and
            {k: v for k, v in initial.items() if k != 'fetches'} == {k: v for k, v in current.items() if k != 'fetches'} and
            current['fetches'] <= context['fetchLimit'] and
            current['fetches'] - initial['fetches'] == context['probeFetchReservations'], 'PRN_PRIMARY_COUNTERS_DIFFER')
    results = _results(store, plan, report['requests'], report['startedAt'], report['checkedAt'], context['budgetDay'])
    charges, denials = [], Counter(report['completionDenials'])
    for index, request in enumerate(report['requests']):
        reservation = request['reservation']
        if reservation is not None:
            require(type(reservation) is dict and set(reservation) == {'budgetDay', 'fetchLimit', 'chargedFetchCount'} and
                    reservation['budgetDay'] == context['budgetDay'] and type(reservation['fetchLimit']) is int and
                    reservation['fetchLimit'] == context['fetchLimit'] and type(reservation['chargedFetchCount']) is int,
                    'PRN_PRIMARY_RESERVATION_INVALID')
            charges.append(reservation['chargedFetchCount'])
        if request['denial'] is not None:
            require(isinstance(request['denial'], str) and index == len(report['requests']) - 1, 'PRN_PRIMARY_DENIAL_MUST_STOP_TRANSPORT')
            denials[request['denial']] += 1
    require(charges == list(range(initial['fetches'] + 1, current['fetches'] + 1)) and
            dict(denials) == context['reservationDenials'] and report['budgetDenied'] is bool(denials) and
            report['executionCompleted'] is (not bool(denials)) and
            (len(report['requests']) == MAX_REQUESTS or denials) and digest(results) == digest(report['results']) and
            type(report['acceptedSamples']) is int and report['acceptedSamples'] == sum(r['accepted'] for r in results) and
            report['proposalEvidenceComplete'] is (not bool(denials) and report['acceptedSamples'] == MAX_REQUESTS),
            'PRN_PRIMARY_REPLAYED_RESULTS_OR_CHARGES_DIFFER')
    start, end = instant(report['startedAt']).astimezone(timezone.utc), instant(report['checkedAt']).astimezone(timezone.utc)
    require(start.date().isoformat() == context['budgetDay'], 'PRN_PRIMARY_START_DAY_DIFFERS')
    if end.date().isoformat() != context['budgetDay'] or (end - start).total_seconds() >= context['maximumRuntimeSeconds']:
        require(denials and not report['proposalEvidenceComplete'], 'PRN_PRIMARY_EXPIRED_CAPTURE_CANNOT_COMPLETE')
    return {'proposalEvidenceComplete': report['proposalEvidenceComplete'], 'acceptedSamples': report['acceptedSamples'], **_zero()}
