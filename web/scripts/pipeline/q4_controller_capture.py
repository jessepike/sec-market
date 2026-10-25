"""Dormant capture of six literally disclosed Q4 scripts. Never execute or qualify."""
import copy
import json
import re
from collections import Counter
from datetime import timezone
from html.parser import HTMLParser
from pathlib import Path

from contracts import digest, instant, require
from onboarding import (PersistentProbeBudget, ProbeReservationDenied, _qualification_reference,
                        _qualification_proof_policy, _qualification_explicit_observation)

OPERATION = 'bounded_q4_controller_capture'
POLICY_SHA256 = '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db'
MAX_REQUESTS = 6
MAX_BODY_BYTES = 2_000_000
PATHS = ('/js/module/widgets/dist/latest/evergreen.q4Api.min.js',
         '/js/module/widgets/dist/latest/evergreen.q4Pager.min.js')
BINDINGS = (
    ('jfrog:official:1', 'jfrog', 'investors.jfrog.com', '/news/default.aspx',
     '1e8d43d1828092f65a14bf90b7a5e222d2e4e8e12bccaab23c2a7052f0da7bff', 4, 'next-jfrog-1'),
    ('rapid7:official:1', 'rapid7', 'investors.rapid7.com', '/news/default.aspx',
     '05a6202088ab48d007b5969e9230844aa716749d7b9442d145953a51446209b5', 5, 'next-rapid7-1'),
    ('rubrik:official:1', 'rubrik', 'ir.rubrik.com', '/news-events/press-releases/default.aspx',
     '3bdfd09fadc261c1d2b09e84499e76983278f527b1c99e06e8d181d5ad56cab0', 6, 'next-rubrik-1'),
)
PARENT_RECORD = {'key': 'ci/source-probe-runs/40131875060-1.json',
                 'sha256': '90f8b45b299dd868fd558d1218fd1e0bcc0fda59c46d9f9a779352d461596aee', 'bytes': 90157}
PROOF_FIELDS = {'type', 'record', 'priorTargetId', 'priorTargetIndex', 'priorTargetSha256',
                'priorPlanRawSha256', 'priorPlanCanonicalSha256', 'priorPlanReference',
                'observation', 'body', 'fetchedAt'}
ZERO_FIELDS = ('qualifiedSources', 'sourceChecksCredited', 'modelCalls')


def _zero():
    return {'qualified': False, 'semanticAdmission': False, 'coverageCredit': False,
            'facts': [], **{key: 0 for key in ZERO_FIELDS}}


def _blob(store, ref, pattern=r'objects/[a-f0-9]{64}'):
    body = _qualification_reference(store, ref, pattern)
    require(type(body) is bytes and len(body) == ref['bytes'] and digest(body) == ref['sha256'],
            'Q4_RETAINED_REFERENCE_BYTES_DIFFER')
    return body


def _body(store, ref):
    # Empty bodies must remain inspectable diagnostic failures.
    require(type(ref) is dict and set(ref) == {'key', 'sha256', 'bytes'} and
            isinstance(ref['sha256'], str) and re.fullmatch(r'[a-f0-9]{64}', ref['sha256']) and
            ref['key'] == 'objects/' + ref['sha256'] and type(ref['bytes']) is int and
            0 <= ref['bytes'] <= MAX_BODY_BYTES, 'Q4_BODY_REFERENCE_INVALID')
    body = store.get(ref)
    require(type(body) is bytes and len(body) == ref['bytes'] and digest(body) == ref['sha256'], 'Q4_BODY_BYTES_DIFFER')
    return body


class _Scripts(HTMLParser):
    """Recognize only the retained, quoted, root-relative external-script form."""
    INERT = {'template', 'noscript', 'iframe', 'textarea', 'title', 'xmp', 'plaintext', 'style', 'svg', 'math'}

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.inert, self.active, self.counts = [], None, Counter()

    def handle_starttag(self, tag, attrs):
        require(tag != 'base', 'Q4_HTML_BASE_NOT_ALLOWED')
        if tag in self.INERT:
            self.inert.append(tag)
        if tag != 'script':
            return
        srcs = [value for name, value in attrs if name == 'src']
        if not any(isinstance(value, str) and ('evergreen.q4Api' in value or 'evergreen.q4Pager' in value)
                   for value in srcs):
            return
        require(not self.inert and self.active is None and len(attrs) == 2 and
                len({name for name, _ in attrs}) == 2 and dict(attrs).get('type') == 'text/javascript' and
                len(srcs) == 1 and srcs[0] in PATHS, 'Q4_SCRIPT_ATTRIBUTES_OR_CONTEXT_INVALID')
        # HTMLParser decodes attribute entities; require the actual quoted literal too.
        raw = self.get_starttag_text()
        pieces = re.findall(r'''([A-Za-z]+)\s*=\s*(["'])(.*?)\2''', raw, re.S)
        require(len(pieces) == 2 and {name.lower(): value for name, _, value in pieces} == dict(attrs) and
                re.fullmatch(r'''<script\s+(?:[A-Za-z]+\s*=\s*(?:"[^"]*"|'[^']*')\s*){2}>''', raw, re.I),
                'Q4_SCRIPT_LITERAL_SYNTAX_INVALID')
        self.active = srcs[0]

    def handle_startendtag(self, tag, attrs):
        require(tag not in {'script', 'base', *self.INERT}, 'Q4_AMBIGUOUS_SELF_CLOSING_CONTEXT_INVALID')

    def handle_endtag(self, tag):
        if tag == 'script' and self.active is not None:
            self.counts[self.active] += 1
            self.active = None
        if tag in self.INERT and tag in self.inert:
            self.inert = self.inert[:self.inert.index(tag)]

    def handle_data(self, data):
        require(self.active is None or not data.strip(), 'Q4_EXTERNAL_SCRIPT_INLINE_BODY_INVALID')


def script_disclosures(body):
    parser = _Scripts()
    parser.feed(body.decode('utf-8', errors='strict'))
    parser.close()
    require(parser.active is None and parser.counts == Counter({path: 1 for path in PATHS}),
            'Q4_EXACT_SCRIPT_DISCLOSURES_REQUIRED')
    return list(PATHS)


def validate_plan(contract, store, raw, path=None):
    """Pure whole-plan preflight, including original charged historical evidence."""
    require(type(raw) is bytes and 0 < len(raw) <= 1_000_000, 'Q4_PLAN_SIZE_INVALID')
    plan = json.loads(raw)
    require(type(plan) is dict and set(plan) == {'schemaVersion', 'operation', 'marketSha256', 'maxRequests', 'sources'} and
            type(plan['schemaVersion']) is int and plan['schemaVersion'] == 2 and plan['operation'] == OPERATION and
            plan['marketSha256'] == digest(contract) == POLICY_SHA256 and
            type(plan['maxRequests']) is int and plan['maxRequests'] == MAX_REQUESTS and
            type(plan['sources']) is list and len(plan['sources']) == len(BINDINGS), 'Q4_PLAN_SHAPE_OR_POLICY_INVALID')
    targets = []
    for row, binding in zip(plan['sources'], BINDINGS):
        source_id, supplier, host, parent_path, source_sha, index, target_id = binding
        source = next(s for s in contract['sources'] if s['id'] == source_id)
        require(type(row) is dict and set(row) == {'sourceId', 'supplierId', 'originalSourceSha256', 'parentProof', 'targets'} and
                row['sourceId'] == source_id and row['supplierId'] == supplier == source['supplierId'] and
                row['originalSourceSha256'] == digest(source) == source_sha and source['registration'] == 'candidate' and
                host in source['allowedHosts'] and row['targets'] == ['https://' + host + p for p in PATHS],
                'Q4_EXACT_SOURCE_AND_TARGETS_REQUIRED')
        proof = row['parentProof']
        require(type(proof) is dict and set(proof) == PROOF_FIELDS and proof['type'] == 'qualification_observation' and
                proof['record'] == PARENT_RECORD and type(proof['priorTargetIndex']) is int and
                proof['priorTargetIndex'] == index and proof['priorTargetId'] == target_id, 'Q4_PARENT_PROOF_SHAPE_INVALID')
        record = json.loads(_blob(store, proof['record'], r'ci/source-probe-runs/[0-9]+-[0-9]+\.json'))
        require(record.get('checkpointProfile') == 'source_probe' and record.get('contractSha256') == POLICY_SHA256 and
                record.get('githubEventName') == 'workflow_dispatch' and record.get('githubRef') == 'refs/heads/main' and
                str(record.get('githubRunId')) + '-' + str(record.get('githubRunAttempt')) == '40131875060-1' and
                all(type(record.get(k)) is int and record[k] == 0 for k in ZERO_FIELDS) and
                record.get('semanticAdmission') is False and record.get('coverageCredit') is False,
                'Q4_PARENT_RUN_PROVENANCE_INVALID')
        proof_contract, proof_source = _qualification_proof_policy(record, proof, source, contract, store)
        observed = _qualification_explicit_observation(record, proof, proof_source, proof_contract, store)
        parent_url = 'https://' + host + parent_path
        require(observed.get('status') == 'fetched' and type(observed.get('httpStatus')) is int and
                observed['httpStatus'] == 200 and observed.get('requestedUrl') == observed.get('finalUrl') == parent_url and
                observed.get('body') == proof['body'] and observed.get('fetchedAt') == proof['fetchedAt'] and
                observed.get('contentType', '').lower() == 'text/html; charset=utf-8', 'Q4_PARENT_RESPONSE_DIFFERS')
        script_disclosures(_blob(store, proof['body']))
        targets.extend({'sourceId': source_id, 'supplierId': supplier, 'sourceSha256': source_sha,
                        'url': url, 'source': copy.deepcopy(source)} for url in row['targets'])
    return {'operation': OPERATION, 'path': str(path) if path is not None else None,
            'rawSha256': digest(raw), 'canonicalSha256': digest(plan), 'plan': plan, 'targets': targets}


def _read_observed(store, reference, target):
    wrapper = json.loads(_blob(store, reference))
    require(type(wrapper) is dict and set(wrapper) == {'schemaVersion', 'sourceId', 'sourceSha256', 'requestedUrl', 'rawObservation'} and
            type(wrapper['schemaVersion']) is int and wrapper['schemaVersion'] == 1 and
            wrapper['sourceId'] == target['sourceId'] and wrapper['sourceSha256'] == target['sourceSha256'] and
            wrapper['requestedUrl'] == target['url'], 'Q4_OBSERVATION_BINDING_DIFFERS')
    observed = json.loads(_blob(store, wrapper['rawObservation']))
    require(type(observed) is dict, 'Q4_RAW_OBSERVATION_INVALID')
    return observed


def _javascript(store, observed, url, requested_at, checked_at, day):
    require(observed.get('requestedUrl') == observed.get('finalUrl') == url and
            observed.get('status') == 'fetched' and type(observed.get('httpStatus')) is int and observed['httpStatus'] == 200 and
            (observed.get('redirectDiagnostics') is None or type(observed['redirectDiagnostics']) is dict and
             not observed['redirectDiagnostics'].get('responses') and
             not observed['redirectDiagnostics'].get('responsesTruncated') and
             not observed['redirectDiagnostics'].get('lastHttpError')), 'Q4_HTTP_OR_FINAL_URL_INVALID')
    fetched = instant(observed['fetchedAt']).astimezone(timezone.utc)
    require(requested_at <= fetched <= checked_at and fetched.date().isoformat() == day, 'Q4_RESPONSE_TIME_INVALID')
    mime = observed.get('contentType')
    require(isinstance(mime, str) and re.fullmatch(
            r'(?:text|application)/(?:javascript|ecmascript)(?:\s*;\s*charset\s*=\s*(?:utf-8|"utf-8"))?\s*', mime, re.I),
            'Q4_JAVASCRIPT_MIME_INVALID')
    body = _body(store, observed.get('body'))
    # Retain raw bytes; no decompression, charset guessing, parsing or execution.
    text = body.decode('utf-8-sig', errors='strict').strip()
    require(text and not text.startswith('<') and '\x00' not in text, 'Q4_JAVASCRIPT_BODY_INVALID')
    try:
        json.loads(text)
    except (ValueError, RecursionError):
        pass
    else:
        raise ValueError('Q4_JSON_BODY_INVALID')
    require(re.search(r'[;{}()]|=>', text) is not None, 'Q4_JAVASCRIPT_BODY_INVALID')


def _results(store, plan, requests, started_at, checked_at, day):
    require(type(requests) is list and len(requests) <= MAX_REQUESTS, 'Q4_REQUEST_INVENTORY_INVALID')
    start, end = instant(started_at), instant(checked_at)
    require(start <= end, 'Q4_COMPLETION_TIME_REGRESSED')
    results = []
    for request, target in zip(requests, plan['targets']):
        require(type(request) is dict and set(request) == {'sourceId', 'url', 'requestedAt', 'reservation', 'observation',
                'responseCheckedAt', 'transportError', 'denial'} and request['sourceId'] == target['sourceId'] and
                request['url'] == target['url'], 'Q4_REQUEST_TARGET_DIFFERS')
        if request['requestedAt'] is not None:
            at = instant(request['requestedAt'])
            require(request['reservation'] is not None and start <= at <= end and
                    at.astimezone(timezone.utc).date().isoformat() == day, 'Q4_ATTEMPT_TIME_INVALID')
        result = {'sourceId': target['sourceId'], 'requestedUrl': target['url'], 'observation': request['observation'],
                  'captured': False, 'finalUrl': None, 'fetchedAt': None, 'httpStatus': None, 'contentType': None,
                  'body': None, 'reason': 'TRANSPORT_NOT_OBSERVED', **_zero()}
        if request['observation'] is not None:
            require(request['reservation'] is not None and request['transportError'] is None and request['denial'] is None,
                    'Q4_OBSERVATION_WITHOUT_REQUEST_INVALID')
            require(request['requestedAt'] is not None and isinstance(request['responseCheckedAt'], str) and
                    instant(request['requestedAt']) <= instant(request['responseCheckedAt']) <= end,
                    'Q4_RESPONSE_CHECK_TIME_INVALID')
            observed = _read_observed(store, request['observation'], target)
            for key in ('finalUrl', 'fetchedAt', 'httpStatus', 'contentType', 'body'):
                result[key] = copy.deepcopy(observed.get(key))
            # A body, when returned, must remain authentic even for a rejected response.
            if observed.get('body') is not None:
                _body(store, observed['body'])
            try:
                _javascript(store, observed, target['url'], instant(request['requestedAt']),
                            instant(request['responseCheckedAt']), day)
                result.update(captured=True, reason='JAVASCRIPT_CAPTURED_REVIEW_REQUIRED')
            except (ValueError, KeyError, TypeError, UnicodeError) as error:
                result['reason'] = type(error).__name__ + ':' + str(error)[:160]
        else:
            require(request['responseCheckedAt'] is None and
                    (isinstance(request['denial'], str) and request['transportError'] is None or
                     request['denial'] is None and request['reservation'] is not None and
                     request['requestedAt'] is not None and isinstance(request['transportError'], str)),
                    'Q4_UNOBSERVED_REQUEST_INVALID')
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
    report['capturedControllers'] = sum(row['captured'] for row in report['results'])
    report['captureComplete'] = report['executionCompleted'] and report['capturedControllers'] == MAX_REQUESTS
    verify_report(contract, store, raw, report)
    return report


def execute(contract, store, fetcher, budget, normalized_plan):
    require(isinstance(budget, PersistentProbeBudget), 'Q4_BOUND_BUDGET_REQUIRED')
    budget.assert_bound(store, contract)
    require(normalized_plan.get('operation') == OPERATION and isinstance(normalized_plan.get('path'), str),
            'Q4_CURRENT_PLAN_PATH_REQUIRED')
    raw = Path(normalized_plan['path']).read_bytes()
    require(digest(raw) == normalized_plan.get('rawSha256'), 'Q4_CURRENT_PLAN_CHANGED')
    plan = validate_plan(contract, store, raw, normalized_plan['path'])
    require(budget.reservations == 0, 'Q4_EXCLUSIVE_BUDGET_REQUIRED')
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
    require(isinstance(budget, PersistentProbeBudget), 'Q4_BOUND_BUDGET_REQUIRED')
    budget.assert_bound(store, contract)
    verify_report(contract, store, raw, report)
    return _seal(contract, store, raw, report, budget)


def verify_report(contract, store, raw, report):
    """Replay retained script captures and exact reservations without transport."""
    plan = validate_plan(contract, store, raw)
    fields = {'schemaVersion', 'operation', 'contractSha256', 'planRawSha256', 'planCanonicalSha256', 'planReference',
              'startedAt', 'checkedAt', 'requests', 'completionDenials', 'reservationContext', 'budgetDenied',
              'executionCompleted', 'results', 'capturedControllers', 'captureComplete', *_zero()}
    require(type(report) is dict and set(report) == fields and type(report['schemaVersion']) is int and
            report['schemaVersion'] == 1 and report['operation'] == OPERATION and
            report['contractSha256'] == POLICY_SHA256 and report['planRawSha256'] == digest(raw) and
            report['planCanonicalSha256'] == plan['canonicalSha256'] and _blob(store, report['planReference']) == raw and
            all(report[k] is False for k in ('qualified', 'semanticAdmission', 'coverageCredit')) and report['facts'] == [] and
            all(type(report[k]) is int and report[k] == 0 for k in ZERO_FIELDS) and
            type(report['completionDenials']) is list and len(report['completionDenials']) <= 2 and
            all(isinstance(d, str) and d for d in report['completionDenials']), 'Q4_REPORT_ENVELOPE_DIFFERS')
    context = report['reservationContext']
    require(type(context) is dict and set(context) == {'budgetDay', 'contractSha256', 'fetchLimit', 'maximumRuntimeSeconds',
            'startedAt', 'initialBudget', 'currentBudget', 'probeFetchReservations', 'reservationDenials'} and
            context['contractSha256'] == POLICY_SHA256 and context['startedAt'] == report['startedAt'] and
            type(context['fetchLimit']) is int and context['fetchLimit'] == contract['schedule']['maxFetchesPerRun'] and
            type(context['maximumRuntimeSeconds']) is int and 0 < context['maximumRuntimeSeconds'] <= min(1200, contract['schedule'].get('maxRuntimeSeconds', 7200)) and
            type(context['probeFetchReservations']) is int and 0 <= context['probeFetchReservations'] <= MAX_REQUESTS and
            type(context['reservationDenials']) is dict and
            all(isinstance(k, str) and type(v) is int and v > 0 for k, v in context['reservationDenials'].items()),
            'Q4_RESERVATION_CONTEXT_INVALID')
    require(all(context[k] is None or type(context[k]) is dict for k in ('initialBudget', 'currentBudget')),
            'Q4_BUDGET_HEAD_SHAPE_INVALID')
    initial = context['initialBudget'] if context['initialBudget'] is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
    current = context['currentBudget'] if context['currentBudget'] is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
    require(type(initial) is dict and type(current) is dict and all(type(b.get(k)) is int and b[k] >= 0
            for b in (initial, current) for k in ('calls', 'documents', 'fetches')) and
            {k: v for k, v in initial.items() if k != 'fetches'} == {k: v for k, v in current.items() if k != 'fetches'} and
            current['fetches'] <= context['fetchLimit'] and
            current['fetches'] - initial['fetches'] == context['probeFetchReservations'], 'Q4_COUNTERS_DIFFER')
    results = _results(store, plan, report['requests'], report['startedAt'], report['checkedAt'], context['budgetDay'])
    charges, denials = [], Counter(report['completionDenials'])
    for index, request in enumerate(report['requests']):
        reservation = request['reservation']
        if reservation is not None:
            require(type(reservation) is dict and set(reservation) == {'budgetDay', 'fetchLimit', 'chargedFetchCount'} and
                    reservation['budgetDay'] == context['budgetDay'] and type(reservation['fetchLimit']) is int and
                    reservation['fetchLimit'] == context['fetchLimit'] and type(reservation['chargedFetchCount']) is int,
                    'Q4_RESERVATION_INVALID')
            charges.append(reservation['chargedFetchCount'])
        if request['denial'] is not None:
            require(isinstance(request['denial'], str) and index == len(report['requests']) - 1, 'Q4_DENIAL_MUST_STOP_TRANSPORT')
            denials[request['denial']] += 1
    require(charges == list(range(initial['fetches'] + 1, current['fetches'] + 1)) and
            dict(denials) == context['reservationDenials'] and report['budgetDenied'] is bool(denials) and
            report['executionCompleted'] is (not bool(denials)) and
            (len(results) == MAX_REQUESTS or denials) and digest(results) == digest(report['results']) and
            type(report['capturedControllers']) is int and report['capturedControllers'] == sum(r['captured'] for r in results) and
            report['captureComplete'] is (not bool(denials) and report['capturedControllers'] == MAX_REQUESTS),
            'Q4_REPLAYED_RESULTS_OR_CHARGES_DIFFER')
    start, end = instant(report['startedAt']).astimezone(timezone.utc), instant(report['checkedAt']).astimezone(timezone.utc)
    require(start.date().isoformat() == context['budgetDay'], 'Q4_START_DAY_DIFFERS')
    if end.date().isoformat() != context['budgetDay'] or (end - start).total_seconds() >= context['maximumRuntimeSeconds']:
        require(denials and not report['captureComplete'], 'Q4_EXPIRED_CAPTURE_CANNOT_COMPLETE')
    return {'captureComplete': report['captureComplete'], 'capturedControllers': report['capturedControllers'], **_zero()}
