"""Dormant two-primary proposal evidence. Never activate a source or admit facts."""
import copy
import json
import re
from collections import Counter
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from contracts import digest, instant, require
from discovery import decoded_discovery_body
from onboarding import PersistentProbeBudget, ProbeReservationDenied, _candidate_primary_shape
import q4_initial_data_capture as initial
from q4_press_list import parse_press_list
from q4_press_list import _object, _constant

OPERATION = 'bounded_q4_primary_qualification'
POLICY_SHA256 = initial.POLICY_SHA256
MAX_REQUESTS = 2
MAX_BODY_BYTES = 2_000_000
REPO = Path(__file__).resolve().parents[3]
PLAN_CANONICAL_SHA256 = '3b7fc7c4de41c68471d4343f103e7e5ee705e5a4a51f760f5387e34a49a660ee'
INSPECTION = {'path': 'docs/active/daily-pipeline/accuracy/q4-initial-data-capture-actual-source-review-2026-10-25.json',
              'sha256': 'e5b4b799d36e984a3cbad88ea4e618de7a5060be2546aed9f1494af671dc2a24', 'bytes': 32449}
_zero, _blob, _body, _read_observed = initial._zero, initial._blob, initial._body, initial._read_observed
ZERO_FIELDS = initial.ZERO_FIELDS
CLIENT = '2ce36889709b0c9ff34e2b657d5abe0600009604d7e5407d41198f9a9c72d5e7'
PAGER = '4e9d26dabe182ce0694a7e892892b5dc24a502cf14ee1b251542c9b920796a79'


def _validate_capture(contract, store, plan):
    proof = plan['initialDataProof']
    inspection = (REPO / INSPECTION['path']).read_bytes()
    require(len(inspection) == INSPECTION['bytes'] and digest(inspection) == INSPECTION['sha256'],
            'Q4_PRIMARY_EXTERNAL_INSPECTION_DIFFERS')
    review = json.loads(inspection)
    require(review['archive']['commit'] == proof['archive']['commit'] and
            review['archiveManifest']['sha256'] == proof['archive']['manifestSha256'] and
            review['archiveManifest']['bytes'] == proof['archive']['manifestBytes'] and
            review['appRevision'] == proof['appRevision'] and
            review['actualRunId'] == int(proof['githubRunId']) and
            review['artifact']['workflow_run']['head_sha'] == proof['appRevision'],
            'Q4_PRIMARY_EXTERNAL_ARCHIVE_JOIN_DIFFERS')
    record = json.loads(_blob(store, proof['record'], r'ci/source-probe-runs/40184027106-1\.json'))
    require(all(type(record.get(k)) is type(proof[k]) and record[k] == proof[k]
                for k in ('githubRunId', 'githubRunAttempt', 'githubEventName', 'githubRef', 'appRevision')) and
            record['checkpointProfile'] == 'source_probe' and record['contractSha256'] == POLICY_SHA256 and
            record['executionCompleted'] is True and record['outcome'] == 'completed_diagnostic' and
            record['publication'] == {'published': False, 'reason': 'SOURCE_PROBE_DIAGNOSTIC_ONLY'} and
            record['facts'] == [] and record['apiFallback'] is False and
            all(record[k] is False for k in ('semanticAdmission', 'coverageCredit')) and
            all(type(record[k]) is int and record[k] == 0 for k in ZERO_FIELDS),
            'Q4_PRIMARY_INITIAL_OUTER_IDENTITY_DIFFERS')
    report = record['diagnostic']
    original_raw = _blob(store, proof['plan'])
    original = json.loads(original_raw)
    require(report['planReference'] == proof['plan'] and
            report['planCanonicalSha256'] == proof['planCanonicalSha256'] == digest(original),
            'Q4_PRIMARY_INITIAL_PLAN_DIFFERS')
    replay = initial.verify_report(contract, store, original_raw, report)
    require(replay['captureComplete'] is True and replay['capturedResponses'] == 2,
            'Q4_PRIMARY_INITIAL_CAPTURE_INCOMPLETE')
    # These authenticated bytes describe a finite returned array and local DOM paging.
    client = _blob(store, {'key': 'objects/' + CLIENT, 'sha256': CLIENT, 'bytes': 25534})
    pager = _blob(store, {'key': 'objects/' + PAGER, 'sha256': PAGER, 'bytes': 7642})
    require(all(span in client for span in (
            b'this._fetchItems(-1).done', b't.resolve(r,e)', b'void 0!==t?r._renderWidget(t)',
            b'o.map(e[n.contentType.itemsResultField]', b'o.each(t.items,function(e,t){n.append')) and
            b'Math.ceil((this.$items?this.$items.length:e.count)/(e.perPage||1))' in pager and
            b'.slice(i,i+t.perPage)' in pager and
            not re.search(br'ajax|fetch\(|XMLHttpRequest|/feed/|/Services/', pager),
            'Q4_PRIMARY_SINGLE_RESPONSE_CLIENT_GRAPH_DIFFERS')
    targets, streams = [], []
    for index, row in enumerate(plan['sources']):
        source = next(s for s in contract['sources'] if s['id'] == row['sourceId'])
        result = report['results'][index]
        request = report['requests'][index]
        wrapper = json.loads(_blob(store, row['observation']))
        require(type(row['resultIndex']) is int and row['resultIndex'] == index and
                source['registration'] == 'candidate' and source['supplierId'] == row['supplierId'] and
                digest(source) == row['originalSourceSha256'] and
                row['sourceId'] == result['sourceId'] == request['sourceId'] == original['sources'][index]['sourceId'] and
                row['observation'] == result['observation'] == request['observation'] and
                wrapper['rawObservation'] == row['rawObservation'] and result['body'] == row['body'] and
                result['fetchedAt'] == row['fetchedAt'] and result['captured'] is True,
                'Q4_PRIMARY_SOURCE_RESPONSE_JOIN_DIFFERS')
        _blob(store, row['rawObservation'])
        stream = parse_press_list(_blob(store, row['body']), source['id'], report['checkedAt'],
                                  contract['collection']['currentWindowDays'])
        require(stream['olderBoundaryPresent'] and all(url in stream['items'] for url in source['seedEvidenceUrls']),
                'Q4_PRIMARY_WINDOW_OR_KNOWN_SEED_MISSING')
        selected = stream['records'][row['sample']['rowIndex']]
        expected = {'rowIndex': selected['rowIndex'], 'recordSha256': selected['recordSha256'],
                    'pressReleaseId': selected['pressReleaseId'], 'workflowId': selected['workflowId'],
                    'title': selected['title'], 'dateLiteral': selected['dateLiteral'],
                    'request': {'method': 'GET', 'url': selected['url'], 'body': None}}
        require(row['sample'] == expected and selected['rowIndex'] == 2 and
                selected['url'] in stream['currentWindowItems'] and not selected['boundaryAmbiguous'],
                'Q4_PRIMARY_EXACT_FINANCIAL_SAMPLE_DIFFERS')
        streams.append({**stream, 'initialObservation': row['observation'], 'initialBody': row['body'],
                        'originalFetchedAt': row['fetchedAt'], 'declaredStreamComplete': True})
        targets.append({'sourceId': source['id'], 'supplierId': source['supplierId'],
                        'sourceSha256': row['originalSourceSha256'], 'url': selected['url'],
                        'source': copy.deepcopy(source), 'sample': copy.deepcopy(selected)})
    return targets, streams


def validate_plan(contract, store, raw, path=None):
    require(type(raw) is bytes and 0 < len(raw) <= 1_000_000, 'Q4_PRIMARY_PLAN_SIZE_INVALID')
    plan = json.loads(raw)
    require(type(plan) is dict and digest(plan) == PLAN_CANONICAL_SHA256 and
            type(plan['schemaVersion']) is int and plan['schemaVersion'] == 2 and plan['operation'] == OPERATION and
            type(plan['maxRequests']) is int and plan['maxRequests'] == MAX_REQUESTS and
            plan['marketSha256'] == digest(contract) == POLICY_SHA256, 'Q4_PRIMARY_EXACT_REVIEWED_PLAN_REQUIRED')
    targets, streams = _validate_capture(contract, store, plan)
    return {'operation': OPERATION, 'path': str(path) if path is not None else None,
            'rawSha256': digest(raw), 'canonicalSha256': digest(plan), 'plan': plan,
            'targets': targets, 'streams': streams}


class _PublicationMetadata(HTMLParser):
    """Keep explicitly supplied publication values, including invalid ones."""
    INERT = {'template', 'noscript', 'iframe', 'textarea', 'xmp', 'plaintext', 'svg', 'math'}

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.values, self.inert, self.parts = [], [], None
        self.feed(text); self.close()
        require(self.parts is None, 'Q4_PRIMARY_UNCLOSED_PUBLICATION_JSON')

    def handle_starttag(self, tag, attrs):
        if tag in self.INERT:
            self.inert.append(tag)
        if self.inert:
            return
        fields = dict(attrs)
        declared_json = tag == 'script' and any(name == 'type' and isinstance(value, str) and
                                                value.strip().lower() == 'application/ld+json' for name, value in attrs)
        declared_meta = tag == 'meta' and any(name in ('property', 'name', 'itemprop') and
                                              value in ('article:published_time', 'datePublished') for name, value in attrs)
        require(not (declared_json or declared_meta) or len(fields) == len(attrs),
                'Q4_PRIMARY_AMBIGUOUS_PUBLICATION_ATTRIBUTES')
        if tag == 'script' and isinstance(fields.get('type'), str) and fields['type'].strip().lower() == 'application/ld+json':
            require(self.parts is None and len(fields) == len(attrs), 'Q4_PRIMARY_AMBIGUOUS_PUBLICATION_JSON')
            self.parts = []
        elif tag == 'time' and 'datetime' in fields:
            require(len(fields) == len(attrs), 'Q4_PRIMARY_AMBIGUOUS_PUBLICATION_ATTRIBUTES')
            self.values.append({'kind': 'time_datetime', 'value': fields['datetime']})
        elif declared_meta:
            require(len(fields) == len(attrs), 'Q4_PRIMARY_AMBIGUOUS_PUBLICATION_ATTRIBUTES')
            self.values.append({'kind': 'published_meta', 'value': fields.get('content')})

    def handle_startendtag(self, tag, attrs):
        require(tag != 'script' and tag not in self.INERT, 'Q4_PRIMARY_AMBIGUOUS_SELF_CLOSING_CONTEXT')
        self.handle_starttag(tag, attrs)

    def handle_data(self, value):
        if self.parts is not None:
            self.parts.append(value)

    def handle_endtag(self, tag):
        if tag in self.inert:
            del self.inert[self.inert.index(tag):]
            return
        if tag == 'script' and self.parts is not None:
            value = json.loads(''.join(self.parts), object_pairs_hook=_object, parse_constant=_constant)
            self.parts = None
            require(type(value) in (dict, list), 'Q4_PRIMARY_PUBLICATION_JSON_SHAPE_INVALID')
            self._published(value)

    def _published(self, value):
        if isinstance(value, list):
            for child in value:
                self._published(child)
        elif isinstance(value, dict):
            types = value.get('@type', [])
            types = [types] if isinstance(types, str) else types
            require(isinstance(types, list) and all(isinstance(kind, str) and kind for kind in types),
                    'Q4_PRIMARY_PUBLICATION_JSON_TYPE_INVALID')
            if any(kind in ('Article', 'NewsArticle', 'BlogPosting', 'PressRelease') for kind in types) and 'datePublished' in value:
                self.values.append({'kind': 'jsonld_published', 'value': value['datePublished']})
            for child in value.values():
                if isinstance(child, (dict, list)):
                    self._published(child)


def _primary_response(store, observed, target, requested_at, checked_at, day):
    url = target['url']
    require(observed.get('requestedUrl') == observed.get('finalUrl') == url and
            observed.get('status') == 'fetched' and type(observed.get('httpStatus')) is int and
            observed['httpStatus'] == 200 and
            (observed.get('redirectDiagnostics') is None or type(observed['redirectDiagnostics']) is dict and
             not observed['redirectDiagnostics'].get('responses') and
             not observed['redirectDiagnostics'].get('responsesTruncated') and
             not observed['redirectDiagnostics'].get('lastHttpError')), 'Q4_PRIMARY_HTTP_OR_FINAL_URL_INVALID')
    fetched = instant(observed['fetchedAt']).astimezone(timezone.utc)
    require(requested_at <= fetched <= checked_at and fetched.date().isoformat() == day,
            'Q4_PRIMARY_RESPONSE_TIME_INVALID')
    mime = observed.get('contentType')
    require(isinstance(mime, str) and re.fullmatch(
            r'(?:text/html|application/xhtml\+xml)(?:\s*;\s*charset\s*=\s*(?:utf-8|"utf-8"))?\s*', mime, re.I),
            'Q4_PRIMARY_HTML_MIME_INVALID')
    body = _body(store, observed.get('body'))
    shape = _candidate_primary_shape(body, url)
    normalize = lambda text: ' '.join(unescape(text).split())
    require(normalize(shape['heading']) == normalize(target['sample']['title']), 'Q4_PRIMARY_HEADING_ROW_DIFFERS')
    metadata = _PublicationMetadata(decoded_discovery_body(body).decode('utf-8', errors='strict')).values
    for item in metadata:
        # Compare the publisher's written calendar day; preserve any offset as written.
        value = item['value']
        require(isinstance(value, str) and re.match(r'^\d{4}-\d{2}-\d{2}(?:$|T| )', value),
                'Q4_PRIMARY_PUBLICATION_DATE_INVALID')
        published = datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(published.date().isoformat() == target['sample']['calendarDay'],
                'Q4_PRIMARY_PUBLICATION_CALENDAR_CONFLICT')
    return {**shape, 'dateMetadata': metadata, 'dateMetadataState': 'present' if metadata else 'unknown',
            'sourceRowSha256': target['sample']['recordSha256'], 'indexDateLiteral': target['sample']['dateLiteral'],
            'indexTimezone': None, 'publicationComparison': 'written_calendar_day'}

def _results(store, plan, requests, started_at, checked_at, day):
    require(type(requests) is list and len(requests) <= MAX_REQUESTS, 'Q4_PRIMARY_REQUEST_INVENTORY_INVALID')
    start, end = instant(started_at), instant(checked_at)
    require(start <= end, 'Q4_PRIMARY_COMPLETION_TIME_REGRESSED')
    results = []
    for request, target in zip(requests, plan['targets']):
        require(type(request) is dict and set(request) == {'sourceId', 'url', 'requestedAt', 'reservation', 'observation',
                'responseCheckedAt', 'transportError', 'denial'} and request['sourceId'] == target['sourceId'] and
                request['url'] == target['url'], 'Q4_PRIMARY_REQUEST_TARGET_DIFFERS')
        if request['requestedAt'] is not None:
            at = instant(request['requestedAt'])
            require(request['reservation'] is not None and start <= at <= end and
                    at.astimezone(timezone.utc).date().isoformat() == day, 'Q4_PRIMARY_ATTEMPT_TIME_INVALID')
        result = {'sourceId': target['sourceId'], 'requestedUrl': target['url'], 'observation': request['observation'],
                  'accepted': False, 'finalUrl': None, 'fetchedAt': None, 'httpStatus': None, 'contentType': None,
                  'body': None, 'primaryShape': None, 'reason': 'TRANSPORT_NOT_OBSERVED', **_zero()}
        if request['observation'] is not None:
            require(request['reservation'] is not None and request['transportError'] is None and request['denial'] is None,
                    'Q4_PRIMARY_OBSERVATION_WITHOUT_REQUEST_INVALID')
            require(request['requestedAt'] is not None and isinstance(request['responseCheckedAt'], str) and
                    instant(request['requestedAt']) <= instant(request['responseCheckedAt']) <= end,
                    'Q4_PRIMARY_RESPONSE_CHECK_TIME_INVALID')
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
                    'Q4_PRIMARY_UNOBSERVED_REQUEST_INVALID')
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
    require(isinstance(budget, PersistentProbeBudget), 'Q4_PRIMARY_BOUND_BUDGET_REQUIRED')
    budget.assert_bound(store, contract)
    require(normalized_plan.get('operation') == OPERATION and isinstance(normalized_plan.get('path'), str),
            'Q4_PRIMARY_CURRENT_PLAN_PATH_REQUIRED')
    raw = Path(normalized_plan['path']).read_bytes()
    require(digest(raw) == normalized_plan.get('rawSha256'), 'Q4_PRIMARY_CURRENT_PLAN_CHANGED')
    plan = validate_plan(contract, store, raw, normalized_plan['path'])
    require(budget.reservations == 0, 'Q4_PRIMARY_EXCLUSIVE_BUDGET_REQUIRED')
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
    require(isinstance(budget, PersistentProbeBudget), 'Q4_PRIMARY_BOUND_BUDGET_REQUIRED')
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
            all(isinstance(d, str) and d for d in report['completionDenials']), 'Q4_PRIMARY_REPORT_ENVELOPE_DIFFERS')
    require(digest(report['streams']) == digest(plan['streams']), 'Q4_PRIMARY_REPLAYED_STREAMS_DIFFER')
    context = report['reservationContext']
    require(type(context) is dict and set(context) == {'budgetDay', 'contractSha256', 'fetchLimit', 'maximumRuntimeSeconds',
            'startedAt', 'initialBudget', 'currentBudget', 'probeFetchReservations', 'reservationDenials'} and
            context['contractSha256'] == POLICY_SHA256 and context['startedAt'] == report['startedAt'] and
            type(context['fetchLimit']) is int and context['fetchLimit'] == contract['schedule']['maxFetchesPerRun'] and
            type(context['maximumRuntimeSeconds']) is int and 0 < context['maximumRuntimeSeconds'] <= min(1200, contract['schedule'].get('maxRuntimeSeconds', 7200)) and
            type(context['probeFetchReservations']) is int and 0 <= context['probeFetchReservations'] <= MAX_REQUESTS and
            type(context['reservationDenials']) is dict and
            all(isinstance(k, str) and type(v) is int and v > 0 for k, v in context['reservationDenials'].items()),
            'Q4_PRIMARY_RESERVATION_CONTEXT_INVALID')
    require(all(context[k] is None or type(context[k]) is dict for k in ('initialBudget', 'currentBudget')),
            'Q4_PRIMARY_BUDGET_HEAD_SHAPE_INVALID')
    initial = context['initialBudget'] if context['initialBudget'] is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
    current = context['currentBudget'] if context['currentBudget'] is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
    require(type(initial) is dict and type(current) is dict and all(type(b.get(k)) is int and b[k] >= 0
            for b in (initial, current) for k in ('calls', 'documents', 'fetches')) and
            {k: v for k, v in initial.items() if k != 'fetches'} == {k: v for k, v in current.items() if k != 'fetches'} and
            current['fetches'] <= context['fetchLimit'] and
            current['fetches'] - initial['fetches'] == context['probeFetchReservations'], 'Q4_PRIMARY_COUNTERS_DIFFER')
    results = _results(store, plan, report['requests'], report['startedAt'], report['checkedAt'], context['budgetDay'])
    charges, denials = [], Counter(report['completionDenials'])
    for index, request in enumerate(report['requests']):
        reservation = request['reservation']
        if reservation is not None:
            require(type(reservation) is dict and set(reservation) == {'budgetDay', 'fetchLimit', 'chargedFetchCount'} and
                    reservation['budgetDay'] == context['budgetDay'] and type(reservation['fetchLimit']) is int and
                    reservation['fetchLimit'] == context['fetchLimit'] and type(reservation['chargedFetchCount']) is int,
                    'Q4_PRIMARY_RESERVATION_INVALID')
            charges.append(reservation['chargedFetchCount'])
        if request['denial'] is not None:
            require(isinstance(request['denial'], str) and index == len(report['requests']) - 1, 'Q4_PRIMARY_DENIAL_MUST_STOP_TRANSPORT')
            denials[request['denial']] += 1
    require(charges == list(range(initial['fetches'] + 1, current['fetches'] + 1)) and
            dict(denials) == context['reservationDenials'] and report['budgetDenied'] is bool(denials) and
            report['executionCompleted'] is (not bool(denials)) and
            (len(results) == MAX_REQUESTS or denials) and digest(results) == digest(report['results']) and
            type(report['acceptedSamples']) is int and report['acceptedSamples'] == sum(r['accepted'] for r in results) and
            report['proposalEvidenceComplete'] is (not bool(denials) and report['acceptedSamples'] == MAX_REQUESTS),
            'Q4_PRIMARY_REPLAYED_RESULTS_OR_CHARGES_DIFFER')
    start, end = instant(report['startedAt']).astimezone(timezone.utc), instant(report['checkedAt']).astimezone(timezone.utc)
    require(start.date().isoformat() == context['budgetDay'], 'Q4_PRIMARY_START_DAY_DIFFERS')
    if end.date().isoformat() != context['budgetDay'] or (end - start).total_seconds() >= context['maximumRuntimeSeconds']:
        require(denials and not report['proposalEvidenceComplete'], 'Q4_PRIMARY_EXPIRED_CAPTURE_CANNOT_COMPLETE')
    return {'proposalEvidenceComplete': report['proposalEvidenceComplete'], 'acceptedSamples': report['acceptedSamples'], **_zero()}
