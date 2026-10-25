"""Dormant exact two-GET capture derived from retained Q4 code. No qualification."""
import copy
import json
import re
from collections import Counter
from datetime import timezone
from pathlib import Path

from contracts import digest, instant, require
from onboarding import PersistentProbeBudget, ProbeReservationDenied
import q4_controller_capture as controllers

OPERATION = 'bounded_q4_initial_data_capture'
POLICY_SHA256 = controllers.POLICY_SHA256
MAX_REQUESTS = 2
MAX_BODY_BYTES = 2_000_000
REPO = Path(__file__).resolve().parents[3]
_zero = controllers._zero
_blob = controllers._blob
_body = controllers._body
_read_observed = controllers._read_observed
ZERO_FIELDS = controllers.ZERO_FIELDS
PLAN_CANONICAL_SHA256 = '5ec3a0fc8588e64af13f8caeec32f3c4327f3b60c2526123ff49b41d219a8dae'
INSPECTION = {'path': 'docs/active/daily-pipeline/accuracy/q4-controller-actual-code-next-requests-2026-10-25.json', 'sha256': '0542a4c9ae1b3468cd8ebe72ee7e2987e7ada34d510f46316a194b46e8754937', 'bytes': 37902}

def _validate_capture(contract, store, plan):
    proof = plan['captureProof']
    review_raw = (REPO / INSPECTION['path']).read_bytes()
    require(len(review_raw) == INSPECTION['bytes'] and digest(review_raw) == INSPECTION['sha256'],
            'Q4_DATA_INSPECTION_DIFFERS')
    review = json.loads(review_raw)
    require(review['acknowledgedArchive'] == proof['archive']['commit'] and
            review['archiveManifest']['sha256'] == proof['archive']['manifestSha256'] and
            review['archiveManifest']['bytes'] == proof['archive']['manifestBytes'],
            'Q4_DATA_ARCHIVE_PROOF_DIFFERS')
    record = json.loads(_blob(store, proof['record'], r'ci/source-probe-runs/40179255547-1\.json'))
    require(all(type(record.get(k)) is type(proof[k]) and record[k] == proof[k]
                for k in ('githubRunId', 'githubRunAttempt', 'githubEventName', 'githubRef', 'appRevision')) and
            record['checkpointProfile'] == 'source_probe' and record['contractSha256'] == POLICY_SHA256 and
            record['executionCompleted'] is True and record['outcome'] == 'completed_diagnostic' and
            record['publication'] == {'published': False, 'reason': 'SOURCE_PROBE_DIAGNOSTIC_ONLY'} and
            record['facts'] == [] and record['apiFallback'] is False and
            all(record[k] is False for k in ('semanticAdmission', 'coverageCredit')) and
            all(type(record[k]) is int and record[k] == 0 for k in ZERO_FIELDS),
            'Q4_DATA_CAPTURE_OUTER_IDENTITY_DIFFERS')
    report = record['diagnostic']
    original_raw = _blob(store, proof['plan'])
    original = json.loads(original_raw)
    require(report['planReference'] == proof['plan'] and
            report['planCanonicalSha256'] == proof['planCanonicalSha256'] == digest(original),
            'Q4_DATA_CONTROLLER_PLAN_DIFFERS')
    replay = controllers.verify_report(contract, store, original_raw, report)
    require(replay['captureComplete'] is True and replay['capturedControllers'] == 6,
            'Q4_DATA_INCOMPLETE_CONTROLLER_CAPTURE')
    for index, row in enumerate(plan['sources']):
        source = next(s for s in contract['sources'] if s['id'] == row['sourceId'])
        html = original['sources'][index]
        bound = row['controllerProof']
        result = report['results'][bound['resultIndex']]
        request = report['requests'][bound['resultIndex']]
        wrapper = json.loads(_blob(store, bound['observation']))
        require(source['registration'] == 'candidate' and source['supplierId'] == row['supplierId'] and
                digest(source) == row['originalSourceSha256'] and
                row['sourceId'] == html['sourceId'] == result['sourceId'] == request['sourceId'] and
                row['supplierId'] == html['supplierId'] and
                digest(row['htmlProof']) == digest(html['parentProof']) and
                result['observation'] == request['observation'] == bound['observation'] and
                wrapper['rawObservation'] == bound['rawObservation'] and
                result['body'] == bound['body'] and result['fetchedAt'] == bound['fetchedAt'] and
                result['captured'] is True, 'Q4_DATA_SOURCE_CONTROLLER_HTML_JOIN_DIFFERS')
        body = _blob(store, bound['body'])
        _blob(store, bound['rawObservation'])
        original_html = _blob(store, row['htmlProof']['body'])
        html_review = review['parents'][index]
        require(html_review['sourceId'] == row['sourceId'] and
                digest(html_review['parentProof']) == digest(row['htmlProof']),
                'Q4_DATA_HTML_CONFIG_PROOF_DIFFERS')
        for key in ('publicFunction', 'languageFunction', 'widgetCall', 'pagerConfig'):
            span = html_review[key]
            require(original_html[span['byteOffset']:span['byteOffset'] + span['byteLength']] == span['text'].encode(),
                    'Q4_DATA_HTML_CONFIG_SPAN_DIFFERS')
        for span in review['apiSpans'].values():
            require(body[span['byteOffset']:span['byteOffset'] + span['byteLength']] == span['text'].encode(),
                    'Q4_DATA_API_SPAN_DIFFERS')
        recommended = review['recommendedRequests'][index]
        require(recommended['sourceId'] == row['sourceId'] and recommended['supplierId'] == row['supplierId'] and
                row['request'] == {'method': recommended['method'], 'url': recommended['exampleExactUrl'],
                                   'body': recommended['body']},
                'Q4_DATA_REVIEWED_REQUEST_DIFFERS')


def validate_plan(contract, store, raw, path=None):
    """Closed reviewed tuple; complete retained proof before operation writes."""
    require(type(raw) is bytes and 0 < len(raw) <= 1_000_000, 'Q4_DATA_PLAN_SIZE_INVALID')
    plan = json.loads(raw)
    require(type(plan) is dict and digest(plan) == PLAN_CANONICAL_SHA256 and
            type(plan['schemaVersion']) is int and plan['schemaVersion'] == 2 and
            plan['operation'] == OPERATION and type(plan['maxRequests']) is int and
            plan['maxRequests'] == MAX_REQUESTS and plan['marketSha256'] == digest(contract) == POLICY_SHA256,
            'Q4_DATA_EXACT_REVIEWED_PLAN_REQUIRED')
    _validate_capture(contract, store, plan)
    targets = []
    for row in plan['sources']:
        source = next(s for s in contract['sources'] if s['id'] == row['sourceId'])
        targets.append({'sourceId': row['sourceId'], 'supplierId': row['supplierId'],
                        'sourceSha256': row['originalSourceSha256'], 'url': row['request']['url'],
                        'source': copy.deepcopy(source)})
    return {'operation': OPERATION, 'path': str(path) if path is not None else None,
            'rawSha256': digest(raw), 'canonicalSha256': digest(plan), 'plan': plan, 'targets': targets}


def _json_response(store, observed, url, requested_at, checked_at, day):
    require(observed.get('requestedUrl') == observed.get('finalUrl') == url and
            observed.get('status') == 'fetched' and type(observed.get('httpStatus')) is int and
            observed['httpStatus'] == 200 and
            (observed.get('redirectDiagnostics') is None or type(observed['redirectDiagnostics']) is dict and
             not observed['redirectDiagnostics'].get('responses') and
             not observed['redirectDiagnostics'].get('responsesTruncated') and
             not observed['redirectDiagnostics'].get('lastHttpError')), 'Q4_DATA_HTTP_OR_FINAL_URL_INVALID')
    fetched = instant(observed['fetchedAt']).astimezone(timezone.utc)
    require(requested_at <= fetched <= checked_at and fetched.date().isoformat() == day,
            'Q4_DATA_RESPONSE_TIME_INVALID')
    mime = observed.get('contentType')
    require(isinstance(mime, str) and re.fullmatch(
            r'(?:application/(?:json|[a-z0-9.-]+\+json)|text/json)(?:\s*;\s*charset\s*=\s*(?:utf-8|"utf-8"))?\s*',
            mime, re.I), 'Q4_DATA_JSON_MIME_INVALID')
    body = _body(store, observed.get('body'))
    text = body.decode('utf-8-sig', errors='strict')
    def invalid_constant(value):
        raise ValueError('Q4_DATA_NON_JSON_CONSTANT')
    value = json.loads(text, parse_constant=invalid_constant)
    require(type(value) is dict and bool(value), 'Q4_DATA_NONEMPTY_JSON_OBJECT_REQUIRED')


def _results(store, plan, requests, started_at, checked_at, day):
    require(type(requests) is list and len(requests) <= MAX_REQUESTS, 'Q4_DATA_REQUEST_INVENTORY_INVALID')
    start, end = instant(started_at), instant(checked_at)
    require(start <= end, 'Q4_DATA_COMPLETION_TIME_REGRESSED')
    results = []
    for request, target in zip(requests, plan['targets']):
        require(type(request) is dict and set(request) == {'sourceId', 'url', 'requestedAt', 'reservation', 'observation',
                'responseCheckedAt', 'transportError', 'denial'} and request['sourceId'] == target['sourceId'] and
                request['url'] == target['url'], 'Q4_DATA_REQUEST_TARGET_DIFFERS')
        if request['requestedAt'] is not None:
            at = instant(request['requestedAt'])
            require(request['reservation'] is not None and start <= at <= end and
                    at.astimezone(timezone.utc).date().isoformat() == day, 'Q4_DATA_ATTEMPT_TIME_INVALID')
        result = {'sourceId': target['sourceId'], 'requestedUrl': target['url'], 'observation': request['observation'],
                  'captured': False, 'finalUrl': None, 'fetchedAt': None, 'httpStatus': None, 'contentType': None,
                  'body': None, 'reason': 'TRANSPORT_NOT_OBSERVED', **_zero()}
        if request['observation'] is not None:
            require(request['reservation'] is not None and request['transportError'] is None and request['denial'] is None,
                    'Q4_DATA_OBSERVATION_WITHOUT_REQUEST_INVALID')
            require(request['requestedAt'] is not None and isinstance(request['responseCheckedAt'], str) and
                    instant(request['requestedAt']) <= instant(request['responseCheckedAt']) <= end,
                    'Q4_DATA_RESPONSE_CHECK_TIME_INVALID')
            observed = _read_observed(store, request['observation'], target)
            for key in ('finalUrl', 'fetchedAt', 'httpStatus', 'contentType', 'body'):
                result[key] = copy.deepcopy(observed.get(key))
            # A body, when returned, must remain authentic even for a rejected response.
            if observed.get('body') is not None:
                _body(store, observed['body'])
            try:
                _json_response(store, observed, target['url'], instant(request['requestedAt']),
                            instant(request['responseCheckedAt']), day)
                result.update(captured=True, reason='JSON_CAPTURED_REVIEW_REQUIRED')
            except (ValueError, KeyError, TypeError, UnicodeError, RecursionError) as error:
                result['reason'] = type(error).__name__ + ':' + str(error)[:160]
        else:
            require(request['responseCheckedAt'] is None and
                    (isinstance(request['denial'], str) and request['transportError'] is None or
                     request['denial'] is None and request['reservation'] is not None and
                     request['requestedAt'] is not None and isinstance(request['transportError'], str)),
                    'Q4_DATA_UNOBSERVED_REQUEST_INVALID')
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
    report['results'] = _results(store, plan, report['requests'], report['startedAt'], report['checkedAt'], budget.day)
    report['capturedResponses'] = sum(row['captured'] for row in report['results'])
    report['captureComplete'] = report['executionCompleted'] and report['capturedResponses'] == MAX_REQUESTS
    verify_report(contract, store, raw, report)
    return report


def execute(contract, store, fetcher, budget, normalized_plan):
    require(isinstance(budget, PersistentProbeBudget), 'Q4_DATA_BOUND_BUDGET_REQUIRED')
    budget.assert_bound(store, contract)
    require(normalized_plan.get('operation') == OPERATION and isinstance(normalized_plan.get('path'), str),
            'Q4_DATA_CURRENT_PLAN_PATH_REQUIRED')
    raw = Path(normalized_plan['path']).read_bytes()
    require(digest(raw) == normalized_plan.get('rawSha256'), 'Q4_DATA_CURRENT_PLAN_CHANGED')
    plan = validate_plan(contract, store, raw, normalized_plan['path'])
    require(budget.reservations == 0, 'Q4_DATA_EXCLUSIVE_BUDGET_REQUIRED')
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
            observed = fetcher.fetch(target['source'], target['url'])
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
    require(isinstance(budget, PersistentProbeBudget), 'Q4_DATA_BOUND_BUDGET_REQUIRED')
    budget.assert_bound(store, contract)
    verify_report(contract, store, raw, report)
    return _seal(contract, store, raw, report, budget)


def verify_report(contract, store, raw, report):
    """Replay retained script captures and exact reservations without transport."""
    plan = validate_plan(contract, store, raw)
    fields = {'schemaVersion', 'operation', 'contractSha256', 'planRawSha256', 'planCanonicalSha256', 'planReference',
              'startedAt', 'checkedAt', 'requests', 'completionDenials', 'reservationContext', 'budgetDenied',
              'executionCompleted', 'results', 'capturedResponses', 'captureComplete', *_zero()}
    require(type(report) is dict and set(report) == fields and type(report['schemaVersion']) is int and
            report['schemaVersion'] == 1 and report['operation'] == OPERATION and
            report['contractSha256'] == POLICY_SHA256 and report['planRawSha256'] == digest(raw) and
            report['planCanonicalSha256'] == plan['canonicalSha256'] and _blob(store, report['planReference']) == raw and
            all(report[k] is False for k in ('qualified', 'semanticAdmission', 'coverageCredit')) and report['facts'] == [] and
            all(type(report[k]) is int and report[k] == 0 for k in ZERO_FIELDS) and
            type(report['completionDenials']) is list and len(report['completionDenials']) <= 2 and
            all(isinstance(d, str) and d for d in report['completionDenials']), 'Q4_DATA_REPORT_ENVELOPE_DIFFERS')
    context = report['reservationContext']
    require(type(context) is dict and set(context) == {'budgetDay', 'contractSha256', 'fetchLimit', 'maximumRuntimeSeconds',
            'startedAt', 'initialBudget', 'currentBudget', 'probeFetchReservations', 'reservationDenials'} and
            context['contractSha256'] == POLICY_SHA256 and context['startedAt'] == report['startedAt'] and
            type(context['fetchLimit']) is int and context['fetchLimit'] == contract['schedule']['maxFetchesPerRun'] and
            type(context['maximumRuntimeSeconds']) is int and 0 < context['maximumRuntimeSeconds'] <= min(1200, contract['schedule'].get('maxRuntimeSeconds', 7200)) and
            type(context['probeFetchReservations']) is int and 0 <= context['probeFetchReservations'] <= MAX_REQUESTS and
            type(context['reservationDenials']) is dict and
            all(isinstance(k, str) and type(v) is int and v > 0 for k, v in context['reservationDenials'].items()),
            'Q4_DATA_RESERVATION_CONTEXT_INVALID')
    require(all(context[k] is None or type(context[k]) is dict for k in ('initialBudget', 'currentBudget')),
            'Q4_DATA_BUDGET_HEAD_SHAPE_INVALID')
    initial = context['initialBudget'] if context['initialBudget'] is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
    current = context['currentBudget'] if context['currentBudget'] is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
    require(type(initial) is dict and type(current) is dict and all(type(b.get(k)) is int and b[k] >= 0
            for b in (initial, current) for k in ('calls', 'documents', 'fetches')) and
            {k: v for k, v in initial.items() if k != 'fetches'} == {k: v for k, v in current.items() if k != 'fetches'} and
            current['fetches'] <= context['fetchLimit'] and
            current['fetches'] - initial['fetches'] == context['probeFetchReservations'], 'Q4_DATA_COUNTERS_DIFFER')
    results = _results(store, plan, report['requests'], report['startedAt'], report['checkedAt'], context['budgetDay'])
    charges, denials = [], Counter(report['completionDenials'])
    for index, request in enumerate(report['requests']):
        reservation = request['reservation']
        if reservation is not None:
            require(type(reservation) is dict and set(reservation) == {'budgetDay', 'fetchLimit', 'chargedFetchCount'} and
                    reservation['budgetDay'] == context['budgetDay'] and type(reservation['fetchLimit']) is int and
                    reservation['fetchLimit'] == context['fetchLimit'] and type(reservation['chargedFetchCount']) is int,
                    'Q4_DATA_RESERVATION_INVALID')
            charges.append(reservation['chargedFetchCount'])
        if request['denial'] is not None:
            require(isinstance(request['denial'], str) and index == len(report['requests']) - 1, 'Q4_DATA_DENIAL_MUST_STOP_TRANSPORT')
            denials[request['denial']] += 1
    require(charges == list(range(initial['fetches'] + 1, current['fetches'] + 1)) and
            dict(denials) == context['reservationDenials'] and report['budgetDenied'] is bool(denials) and
            report['executionCompleted'] is (not bool(denials)) and
            (len(results) == MAX_REQUESTS or denials) and digest(results) == digest(report['results']) and
            type(report['capturedResponses']) is int and report['capturedResponses'] == sum(r['captured'] for r in results) and
            report['captureComplete'] is (not bool(denials) and report['capturedResponses'] == MAX_REQUESTS),
            'Q4_DATA_REPLAYED_RESULTS_OR_CHARGES_DIFFER')
    start, end = instant(report['startedAt']).astimezone(timezone.utc), instant(report['checkedAt']).astimezone(timezone.utc)
    require(start.date().isoformat() == context['budgetDay'], 'Q4_DATA_START_DAY_DIFFERS')
    if end.date().isoformat() != context['budgetDay'] or (end - start).total_seconds() >= context['maximumRuntimeSeconds']:
        require(denials and not report['captureComplete'], 'Q4_DATA_EXPIRED_CAPTURE_CANNOT_COMPLETE')
    return {'captureComplete': report['captureComplete'], 'capturedResponses': report['capturedResponses'], **_zero()}
