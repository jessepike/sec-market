"""Dormant, fixed-H Orca evidence diagnostic. No dispatch or activation authority."""
import copy
import json
import re
from collections import Counter
from datetime import timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from contracts import digest, instant, require, validate_contract
from discovery import ORCA_HTML_MODE, IndexMarkup, decoded_discovery_body, orca_index, orca_index_number

OPERATION = 'bounded_orca_qualification'
POLICY_SHA256 = '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db'
SOURCE_ID = 'orca:official:1'
SOURCE_SHA256 = '11dc1755e9febe013fbc5d35a636afc948432251f6186cf62ce3effcb5cac4cf'
INDEX = 'https://orca.security/resources/news/'
MAX_PAGES, MAX_REQUESTS = 60, 61
START_PROOF = {
    'observation': {'key': 'observations/b5d6182ff2fed713a7cc26fea913c63719a2f97c369ff420be7212b8a360be9a.json',
                    'sha256': '4d1106359471da8aa436527bd3324f4dfea325c0b9364a52537bb4aac203c757', 'bytes': 596},
    'body': {'key': 'objects/9f0503f9a7c15f5a6e4686ebd9d3a4cf6be13626d43746154af19a7d1f627e54',
             'sha256': '9f0503f9a7c15f5a6e4686ebd9d3a4cf6be13626d43746154af19a7d1f627e54', 'bytes': 236182},
    'fetchedAt': '2026-10-23T04:14:41.172921Z'}
PLAN_FIELDS = {'schemaVersion', 'operation', 'marketSha256', 'originalContract', 'sourceId',
               'originalSourceSha256', 'proposedAdapterSha256', 'startProof',
               'maxRequests', 'maxIndexPages', 'primarySamples'}
ZERO_FIELDS = ('modelCalls', 'documentsProcessed', 'gateUses', 'sourceChecksCredited', 'qualifiedSources')


def _blob(store, ref, pattern=r'objects/[a-f0-9]{64}'):
    require(type(ref) is dict and set(ref) == {'key', 'sha256', 'bytes'} and
            isinstance(ref['key'], str) and re.fullmatch(pattern, ref['key']) and
            isinstance(ref['sha256'], str) and re.fullmatch(r'[a-f0-9]{64}', ref['sha256']) and
            type(ref['bytes']) is int and 0 < ref['bytes'] <= 32_000_000, 'ORCA_REFERENCE_INVALID')
    if ref['key'].startswith('objects/'):
        require(ref['key'] == 'objects/' + ref['sha256'], 'ORCA_OBJECT_ADDRESS_DIFFERS')
    raw = store.get(ref)
    require(len(raw) == ref['bytes'] and digest(raw) == ref['sha256'], 'ORCA_REFERENCE_INTEGRITY_DIFFERS')
    return raw


def _json(store, ref, pattern=r'objects/[a-f0-9]{64}'):
    value = json.loads(_blob(store, ref, pattern))
    require(type(value) is dict, 'ORCA_JSON_OBJECT_REQUIRED')
    return value


def _literal(base, href):
    require(isinstance(href, str) and href and not any(ord(c) <= 32 or ord(c) == 127 for c in href)
            and '%' not in href and '\\' not in href, 'ORCA_UNSAFE_LITERAL_URL')
    p = urlsplit(href)
    require(not (p.netloc and not p.scheme) and not p.query and not p.fragment,
            'ORCA_UNSAFE_LITERAL_URL')
    segments = p.path.split('/')[1:] if p.path.startswith('/') else p.path.split('/')
    if segments and segments[-1] == '':
        segments.pop()
    require(segments and all(s and s not in ('.', '..') for s in segments), 'ORCA_UNSAFE_LITERAL_PATH')
    return urljoin(base, href)


def _page(adapter, url, body, highest, as_of):
    require(re.fullmatch(r'https://orca\.security/resources/news/(?:page/[1-9]\d*/)?', url),
            'ORCA_UNSAFE_INDEX_URL')
    decoded = decoded_discovery_body(body)
    parsed = orca_index(adapter, url, decoded, highest)
    nodes = list(IndexMarkup(decoded.decode('utf8', errors='strict')).root.walk())
    # Validate literals before urljoin can erase a dot/empty/control segment.
    for node in nodes:
        if node.tag == 'link' and 'next' in node.attrs.get('rel', '').split():
            require(_literal(url, node.attrs.get('href')) == parsed['next'], 'ORCA_LITERAL_NEXT_DIFFERS')
        if node.tag == 'a' and 'page-numbers' in node.classes:
            orca_index_number(_literal(url, node.attrs.get('href')))
        if node.tag in ('div', 'article') and 'clickable-card' in node.classes:
            category = [n for n in node.walk() if 'post-card__category' in n.classes]
            if len(category) == 1 and ' '.join(category[0].text.split()) == 'Press Releases':
                for child in node.walk():
                    if child.tag == 'a' and child.attrs.get('href'):
                        target = _literal(url, child.attrs['href'])
                        require(target in parsed['items'], 'ORCA_LITERAL_CARD_DIFFERS')
                if node.attrs.get('data-url'):
                    require(_literal(url, node.attrs['data-url']) in parsed['items'], 'ORCA_LITERAL_CARD_DIFFERS')
    day = instant(as_of).astimezone(timezone.utc).date().isoformat()
    require(all(value <= day for value in parsed['dates'].values()), 'ORCA_FUTURE_INDEX_DATE')
    return {'currentPage': orca_index_number(url), 'highestPage': parsed['highestPage'],
            'items': sorted(parsed['items']), 'dates': parsed['dates'], 'next': parsed['next'],
            'terminalProved': parsed['next'] is None}


def validate_plan(contract, store, raw_plan_bytes, path=None):
    require(type(raw_plan_bytes) is bytes and 0 < len(raw_plan_bytes) <= 1_000_000, 'ORCA_PLAN_SIZE_INVALID')
    p = json.loads(raw_plan_bytes)
    require(type(p) is dict and set(p) == PLAN_FIELDS and type(p['schemaVersion']) is int and
            p['schemaVersion'] == 2 and p['operation'] == OPERATION and digest(contract) == POLICY_SHA256 and
            p['marketSha256'] == POLICY_SHA256 and p['sourceId'] == SOURCE_ID and
            p['originalSourceSha256'] == SOURCE_SHA256 and
            all(type(p[k]) is int and p[k] == n for k, n in
                (('maxRequests', MAX_REQUESTS), ('maxIndexPages', MAX_PAGES), ('primarySamples', 1))) and
            digest(p['startProof']) == digest(START_PROOF), 'ORCA_PLAN_SHAPE_OR_POLICY_INVALID')
    validate_contract(contract)
    original = _json(store, p['originalContract'], r'contracts/[a-f0-9]{64}\.json')
    require(p['originalContract']['key'] == 'contracts/' + POLICY_SHA256 + '.json' and
            digest(original) == POLICY_SHA256, 'ORCA_ORIGINAL_WHOLE_POLICY_DIFFERS')
    matches = [s for s in contract['sources'] if s['id'] == SOURCE_ID]
    require(len(matches) == 1 and digest(matches[0]) == SOURCE_SHA256 and
            matches[0]['registration'] == 'candidate', 'ORCA_ORIGINAL_SOURCE_DIFFERS')
    adapter = {**copy.deepcopy(matches[0]), 'kind': 'html_index', 'url': INDEX, 'htmlCompleteness': ORCA_HTML_MODE}
    require(p['proposedAdapterSha256'] == digest(adapter), 'ORCA_PROPOSED_ADAPTER_DIFFERS')
    observed = _json(store, p['startProof']['observation'], r'observations/[a-f0-9]{64}\.json')
    require(observed.get('sourceId') == 'orca:citation:TR-orca-1' and observed.get('status') == 'fetched' and
            type(observed.get('httpStatus')) is int and observed['httpStatus'] == 200 and
            observed.get('requestedUrl') == 'https://orca.security/resources/press-releases/' and
            observed.get('finalUrl') == INDEX and observed.get('body') == START_PROOF['body'] and
            observed.get('fetchedAt') == START_PROOF['fetchedAt'], 'ORCA_ORIGINAL_ENDPOINT_PROOF_DIFFERS')
    _page(adapter, INDEX, _blob(store, observed['body']), 1, observed['fetchedAt'])
    return {'operation': OPERATION, 'path': str(path) if path is not None else None,
            'rawSha256': digest(raw_plan_bytes), 'canonicalSha256': digest(p), 'plan': p,
            'sourceId': SOURCE_ID, 'source': copy.deepcopy(matches[0]), 'adapter': adapter,
            'proposedAdapterSha256': digest(adapter)}


def _read_observation(store, ref, plan, url):
    wrapper = _json(store, ref)
    require(set(wrapper) == {'schemaVersion', 'sourceId', 'adapterSha256', 'requestedUrl', 'rawObservation'} and
            type(wrapper['schemaVersion']) is int and wrapper['schemaVersion'] == 1 and
            wrapper['sourceId'] == SOURCE_ID and wrapper['adapterSha256'] == plan['proposedAdapterSha256'] and
            wrapper['requestedUrl'] == url, 'ORCA_OBSERVATION_SOURCE_BINDING_DIFFERS')
    observed = _json(store, wrapper['rawObservation'])
    if observed.get('body') is not None:
        _blob(store, observed['body'])
    return observed


def _response(store, observed, url, start, end, day):
    require(observed.get('status') == 'fetched' and type(observed.get('httpStatus')) is int and
            observed['httpStatus'] == 200 and observed.get('requestedUrl') == url and
            observed.get('finalUrl') == url and isinstance(observed.get('body'), dict), 'ORCA_RESPONSE_INCOMPLETE')
    at = instant(observed.get('fetchedAt')).astimezone(timezone.utc)
    require(start <= at <= end and at.date().isoformat() == day, 'ORCA_OBSERVATION_TIME_INVALID')
    return _blob(store, observed['body'])


def _reconstruct(store, plan, requests, started_at, checked_at, completion_denial):
    from onboarding import _candidate_primary_shape
    start, end = instant(started_at), instant(checked_at)
    require(end >= start and type(requests) is list and len(requests) <= MAX_REQUESTS, 'ORCA_REQUEST_INVENTORY_INVALID')
    day = start.astimezone(timezone.utc).date().isoformat()
    pages, items, dates, highest, next_url, sample = [], set(), {}, 1, INDEX, None
    terminal, stopped, reason = False, False, 'INDEX_TRAVERSAL_INCOMPLETE'
    for request in requests:
        require(type(request) is dict and set(request) == {'kind', 'url', 'reservation', 'observation', 'responseCheckedAt', 'transportError', 'denial'}
                and not stopped and (request['transportError'] is None or isinstance(request['transportError'], str)) and
                (request['denial'] is None or isinstance(request['denial'], str)), 'ORCA_REQUEST_SCHEMA_OR_CONTINUATION_DIFFERS')
        kind = 'primary' if terminal else 'index'
        if terminal:
            require(items and sample is None, 'ORCA_UNEXPECTED_PRIMARY_SAMPLE')
            newest = max(dates.values()); expected = min(u for u in items if dates[u] == newest)
        else:
            expected = next_url
            require(len(pages) < MAX_PAGES, 'ORCA_INDEX_PAGE_LIMIT_EXCEEDED')
        require(request['kind'] == kind and request['url'] == expected, 'ORCA_REQUEST_SEQUENCE_DIFFERS')
        observed = None
        if request['observation'] is not None:
            require(request['reservation'] is not None and request['denial'] is None and request['transportError'] is None,
                    'ORCA_OBSERVATION_REQUEST_JOIN_DIFFERS')
            observed = _read_observation(store, request['observation'], plan, expected)
            response_end = instant(request['responseCheckedAt'])
            require(start <= response_end <= end, 'ORCA_RESPONSE_CHECK_TIME_DIFFERS')
        else:
            require(request['responseCheckedAt'] is None, 'ORCA_UNOBSERVED_RESPONSE_CHECK_TIME')
            require((request['denial'] is not None) != (request['transportError'] is not None), 'ORCA_REQUEST_WITHOUT_OUTCOME')
            require(request['transportError'] is None or request['reservation'] is not None, 'ORCA_UNCHARGED_TRANSPORT')
        parsed = None
        try:
            require(observed is not None, request['denial'] or request['transportError'])
            body = _response(store, observed, expected, start, response_end, day)
            if kind == 'index':
                parsed = _page(plan['adapter'], expected, body, highest, started_at)
                require(all(u not in dates or dates[u] == d for u, d in parsed['dates'].items()), 'ORCA_CONFLICTING_INDEX_DATES')
                items.update(parsed['items']); dates.update(parsed['dates']); highest = parsed['highestPage']
                next_url = parsed['next']; terminal = parsed['terminalProved']
                if terminal:
                    require(parsed['currentPage'] == highest == len(pages) + 1, 'ORCA_TERMINAL_TRAVERSAL_DIFFERS')
                    reason = 'PRIMARY_SAMPLE_MISSING' if items else 'NO_OFFICIAL_RELEASE_SAMPLE'
                elif len(pages) + 1 == MAX_PAGES:
                    reason = 'ORCA_PAGINATION_LIMIT'; stopped = True
            else:
                parsed = _candidate_primary_shape(body, expected)
                reason = 'COMPLETE_DIAGNOSTIC_EVIDENCE_ONLY'; stopped = True
        except (ValueError, KeyError, TypeError, OSError, UnicodeError) as error:
            parsed = {'error': str(error)[:160]}; reason = parsed['error']; stopped = True
        snapshot = {'url': expected, 'observation': request['observation'], 'parsed': parsed}
        if kind == 'index':
            pages.append(snapshot)
        else:
            sample = snapshot
    ready = bool(terminal and sample and 'error' not in sample['parsed'] and completion_denial is None)
    return {'pages': pages, 'inventory': {'items': sorted(items), 'dates': dates}, 'primarySample': sample,
            'indexComplete': terminal, 'evidenceComplete': ready, 'reason': completion_denial or reason}


def execute(contract, store, fetcher, budget, normalized_plan):
    """Caller owns the external mutation lease. This module has no routing hook."""
    from onboarding import PersistentProbeBudget, ProbeReservationDenied, _store_bounded_candidate_observation
    require(isinstance(budget, PersistentProbeBudget), 'ORCA_BOUND_BUDGET_REQUIRED')
    budget.assert_bound(store, contract)
    require(normalized_plan.get('operation') == OPERATION and isinstance(normalized_plan.get('path'), str), 'ORCA_CURRENT_PLAN_PATH_REQUIRED')
    raw = Path(normalized_plan['path']).read_bytes()
    require(digest(raw) == normalized_plan.get('rawSha256'), 'ORCA_CURRENT_PLAN_CHANGED')
    plan = validate_plan(contract, store, raw, normalized_plan['path'])
    require(budget.reservations == 0, 'ORCA_EXCLUSIVE_BUDGET_REQUIRED')
    plan_ref = store.put(raw)
    requests, highest, items, dates, url, terminal = [], 1, set(), {}, INDEX, False
    for _ in range(MAX_REQUESTS):
        kind = 'primary' if terminal else 'index'
        request = {'kind': kind, 'url': url, 'reservation': None, 'observation': None,
                   'responseCheckedAt': None, 'transportError': None, 'denial': None}
        requests.append(request)
        try:
            request['reservation'] = budget.reserve_fetch()
            budget.before_fetch()
        except ProbeReservationDenied as error:
            request['denial'] = error.reason
            break
        try:
            observed = fetcher.fetch(plan['adapter'], url)
            request['observation'] = _store_bounded_candidate_observation(store, plan, url, observed)
            request['responseCheckedAt'] = budget.clock()
        except (OSError, ValueError, RuntimeError) as error:
            request['transportError'] = type(error).__name__ + ':' + str(error)[:120]
            break
        try:
            body = _response(store, observed, url, budget.started, instant(request['responseCheckedAt']), budget.day)
            if kind == 'primary':
                break
            parsed = _page(plan['adapter'], url, body, highest, budget.started_at)
            require(all(u not in dates or dates[u] == d for u, d in parsed['dates'].items()), 'ORCA_CONFLICTING_INDEX_DATES')
            items.update(parsed['items']); dates.update(parsed['dates']); highest = parsed['highestPage']
            terminal = parsed['terminalProved']
            if terminal:
                if not items:
                    break
                newest = max(dates.values()); url = min(u for u in items if dates[u] == newest)
            else:
                url = parsed['next']
                if len(requests) == MAX_PAGES:
                    break
        except (ValueError, KeyError, TypeError, OSError, UnicodeError):
            break
    checked_at, denial = None, None
    try:
        budget.before_fetch(); checked_at = budget.clock(); budget.before_fetch()
    except ProbeReservationDenied as error:
        denial = error.reason
    if checked_at is None:
        checked_at = budget.clock()
    report = {'schemaVersion': 1, 'operation': OPERATION, 'contractSha256': digest(contract),
              'planRawSha256': digest(raw), 'planCanonicalSha256': plan['canonicalSha256'], 'planReference': plan_ref,
              'sourceId': SOURCE_ID, 'supplierId': 'orca', 'originalSourceSha256': SOURCE_SHA256,
              'proposedAdapterSha256': plan['proposedAdapterSha256'], 'startedAt': budget.started_at, 'checkedAt': checked_at,
              'requests': requests, 'completionDenial': denial, 'reservationContext': budget.summary(),
              'budgetDenied': denial is not None or any(r['denial'] is not None for r in requests),
              'executionCompleted': denial is None and not any(r['denial'] is not None for r in requests),
              'qualified': False, 'semanticAdmission': False, 'coverageCredit': False,
              'facts': [], 'newFactIds': [], 'heldClaims': [], 'documentValidations': [], **{k: 0 for k in ZERO_FIELDS}}
    report.update(_reconstruct(store, plan, requests, report['startedAt'], checked_at, denial))
    verify_report(contract, store, raw, report)
    return report


def verify_report(contract, store, raw_plan_bytes, report):
    """Pure original-policy replay; completion flags never replace source bytes."""
    plan = validate_plan(contract, store, raw_plan_bytes)
    fields = {'schemaVersion', 'operation', 'contractSha256', 'planRawSha256', 'planCanonicalSha256', 'planReference',
              'sourceId', 'supplierId', 'originalSourceSha256', 'proposedAdapterSha256', 'startedAt', 'checkedAt',
              'requests', 'completionDenial', 'reservationContext', 'budgetDenied', 'executionCompleted',
              'qualified', 'semanticAdmission', 'coverageCredit', 'facts', 'newFactIds', 'heldClaims', 'documentValidations',
              'pages', 'inventory', 'primarySample', 'indexComplete', 'evidenceComplete', 'reason', *ZERO_FIELDS}
    require(type(report) is dict and set(report) == fields and type(report['schemaVersion']) is int and report['schemaVersion'] == 1 and
            report['operation'] == OPERATION and report['contractSha256'] == POLICY_SHA256 and report['sourceId'] == SOURCE_ID and
            report['supplierId'] == 'orca' and report['originalSourceSha256'] == SOURCE_SHA256 and
            report['proposedAdapterSha256'] == plan['proposedAdapterSha256'] and
            report['planRawSha256'] == digest(raw_plan_bytes) and report['planCanonicalSha256'] == plan['canonicalSha256'] and
            _blob(store, report['planReference']) == raw_plan_bytes and
            all(report[k] is False for k in ('qualified', 'semanticAdmission', 'coverageCredit')) and
            all(type(report[k]) is int and report[k] == 0 for k in ZERO_FIELDS) and
            all(report[k] == [] for k in ('facts', 'newFactIds', 'heldClaims', 'documentValidations')) and
            (report['completionDenial'] is None or isinstance(report['completionDenial'], str)), 'ORCA_REPORT_ENVELOPE_DIFFERS')
    c = report['reservationContext']
    require(type(c) is dict and set(c) == {'budgetDay', 'contractSha256', 'fetchLimit', 'maximumRuntimeSeconds', 'startedAt',
            'initialBudget', 'currentBudget', 'probeFetchReservations', 'reservationDenials'} and c['contractSha256'] == POLICY_SHA256 and
            c['startedAt'] == report['startedAt'] and type(c['fetchLimit']) is int and
            c['fetchLimit'] == contract['schedule']['maxFetchesPerRun'] <= 5500 and
            type(c['maximumRuntimeSeconds']) is int and 0 < c['maximumRuntimeSeconds'] <= min(1200, contract['schedule'].get('maxRuntimeSeconds', 7200)) and
            type(c['probeFetchReservations']) is int and 0 <= c['probeFetchReservations'] <= MAX_REQUESTS and
            type(c['reservationDenials']) is dict and all(type(v) is int and v > 0 for v in c['reservationDenials'].values()),
            'ORCA_RESERVATION_CONTEXT_DIFFERS')
    initial = c['initialBudget'] if c['initialBudget'] is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
    current = c['currentBudget'] if c['currentBudget'] is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
    require(type(initial) is dict and type(current) is dict and all(type(b.get(k)) is int and b[k] >= 0
            for b in (initial, current) for k in ('calls', 'documents', 'fetches')) and
            digest({k:v for k,v in initial.items() if k != 'fetches'}) == digest({k:v for k,v in current.items() if k != 'fetches'}) and
            current['fetches'] <= c['fetchLimit'] and current['fetches'] - initial['fetches'] == c['probeFetchReservations'], 'ORCA_COUNTERS_DIFFER')
    charges, denials = [], Counter()
    for row in report['requests']:
        reservation = row['reservation']
        if reservation is not None:
            require(type(reservation) is dict and set(reservation) == {'budgetDay', 'fetchLimit', 'chargedFetchCount'} and
                    reservation['budgetDay'] == c['budgetDay'] and type(reservation['fetchLimit']) is int and
                    reservation['fetchLimit'] == c['fetchLimit'] and type(reservation['chargedFetchCount']) is int, 'ORCA_CHARGE_INVALID')
            charges.append(reservation['chargedFetchCount'])
        if row['denial'] is not None:
            denials[row['denial']] += 1
    if report['completionDenial'] is not None:
        denials[report['completionDenial']] += 1
    require(charges == list(range(initial['fetches'] + 1, current['fetches'] + 1)) and
            dict(denials) == c['reservationDenials'] and report['budgetDenied'] is bool(denials) and
            report['executionCompleted'] is (not bool(denials)), 'ORCA_CHARGES_OR_DENIALS_DIFFER')
    replay = _reconstruct(store, plan, report['requests'], report['startedAt'], report['checkedAt'], report['completionDenial'])
    require(digest(replay) == digest({k:report[k] for k in replay}), 'ORCA_REPLAYED_RESULT_DIFFERS')
    start, end = instant(report['startedAt']).astimezone(timezone.utc), instant(report['checkedAt']).astimezone(timezone.utc)
    require(start.date().isoformat() == c['budgetDay'], 'ORCA_BUDGET_DAY_DIFFERS')
    if end.date().isoformat() != c['budgetDay'] or (end - start).total_seconds() >= c['maximumRuntimeSeconds']:
        require(denials and not replay['evidenceComplete'], 'ORCA_EXPIRED_RUN_CANNOT_COMPLETE')
    return {'indexComplete': replay['indexComplete'], 'evidenceComplete': replay['evidenceComplete'],
            'inventory': replay['inventory'], 'qualified': False, 'coverageCredit': False}


def replay_diagnostic(contract, store, record_ref, raw_plan_ref):
    """Internal joins only. External Actions authentication remains caller-owned."""
    record = _json(store, record_ref, r'ci/source-probe-runs/[0-9]+-[0-9]+\.json')
    require(type(record.get('schemaVersion')) is int and record['schemaVersion'] == 1 and
            record.get('checkpointProfile') == 'source_probe' and record.get('contractSha256') == POLICY_SHA256 and
            type(record.get('githubRunId')) in (str, int) and str(record['githubRunId']).isdigit() and
            type(record.get('githubRunAttempt')) is int and record['githubRunAttempt'] > 0 and
            record_ref['key'] == f"ci/source-probe-runs/{record['githubRunId']}-{record['githubRunAttempt']}.json" and
            record.get('githubEventName') == 'workflow_dispatch' and record.get('githubRef') == 'refs/heads/main' and
            isinstance(record.get('appRevision'), str) and re.fullmatch(r'[a-f0-9]{40}', record['appRevision']) and
            record.get('apiFallback') is False and all(type(record.get(k)) is int and record[k] == 0
                for k in ('modelCalls', 'sourceChecksCredited', 'qualifiedSources')) and
            record.get('semanticAdmission') is False and record.get('coverageCredit') is False and
            record.get('publication') == {'published': False, 'reason': 'SOURCE_PROBE_DIAGNOSTIC_ONLY'}, 'ORCA_HISTORICAL_RUN_ENVELOPE_DIFFERS')
    report = record.get('diagnostic')
    require(type(report) is dict and report.get('planReference') == raw_plan_ref and
            record.get('executionCompleted') is report.get('executionCompleted') and
            (record.get('outcome') == ('completed_diagnostic' if report['executionCompleted'] else 'budget_denied') or
             record.get('outcome') == 'cancelled' and record['executionCompleted'] is False), 'ORCA_HISTORICAL_OUTCOME_DIFFERS')
    raw = _blob(store, raw_plan_ref)
    return {'plan': validate_plan(contract, store, raw), 'report': report, 'readiness': verify_report(contract, store, raw, report)}
