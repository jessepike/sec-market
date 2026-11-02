"""Closed ordinary discovery for the three reviewed existing source rows."""
import copy
import re
from datetime import timezone

from contracts import digest, instant, require
import cyera_press_list as cyera
import prnewswire_press_list as prn

CYERA_MODE = cyera.VERSION
PRN_MODE = prn.VERSION
SOURCE_IDS = ('cato:official:1', 'chainguard:official:1', 'cyera:official:1')
MODES = (CYERA_MODE, PRN_MODE)
MAX_BYTES = 2_000_000


def matches(source):
    return source.get('id') in SOURCE_IDS and source.get('htmlCompleteness') in MODES


def _identity(source):
    sid = source.get('id')
    require(sid in SOURCE_IDS and source.get('kind') == 'html_index' and
            source.get('registration') == 'verified', 'THREE_SOURCE_ADAPTER_IDENTITY_INVALID')
    is_cyera = sid == cyera.SOURCE
    expected = (cyera.INDEX, 'www.cyera.com', 'official_announcements', CYERA_MODE) if is_cyera else (
        prn.index_url(sid), 'www.prnewswire.com', 'release_distribution', PRN_MODE)
    require((source.get('url'), source.get('allowedHosts'), source.get('family'), source.get('htmlCompleteness')) ==
            (expected[0], [expected[1]], expected[2], expected[3]) and
            type(source.get('maxPages')) is int and source['maxPages'] == 60,
            'THREE_SOURCE_ADAPTER_SCOPE_INVALID')
    return is_cyera


def _response(source, url, request, observations, anchor):
    observed, body = request(url)
    require(type(observed) is dict, 'THREE_SOURCE_INDEX_OBSERVATION_INVALID')
    observations.append(copy.deepcopy(observed))
    require(observed.get('sourceId') == source['id'] and
            observed.get('requestedUrl') == observed.get('finalUrl') == url,
            'THREE_SOURCE_INDEX_TRANSPORT_IDENTITY_INVALID')
    status = (observed.get('status'), observed.get('httpStatus'))
    require(type(observed.get('httpStatus')) is int and (status == ('fetched', 200) or
            status == ('not_modified', 304) and isinstance(observed.get('reusesObservationId'), str) and
            bool(re.fullmatch('[a-f0-9]{64}', observed['reusesObservationId']))),
            'THREE_SOURCE_INDEX_HTTP_INVALID')
    require(isinstance(observed.get('contentType'), str) and re.fullmatch(
            r'(?:text/html|application/xhtml\+xml)(?:\s*;\s*charset\s*=\s*(?:utf-8|"utf-8"))?\s*',
            observed['contentType'], re.I), 'THREE_SOURCE_INDEX_MIME_INVALID')
    ref = observed.get('body')
    require(type(ref) is dict and set(ref) == {'key', 'sha256', 'bytes'} and
            type(ref['bytes']) is int and 0 < ref['bytes'] <= MAX_BYTES and
            ref['key'] == 'objects/' + ref['sha256'] and type(body) is bytes and
            len(body) == ref['bytes'] and digest(body) == ref['sha256'],
            'THREE_SOURCE_INDEX_BODY_INVALID')
    when = instant(observed.get('fetchedAt')).astimezone(timezone.utc)
    if anchor is not None:
        start = instant(anchor).astimezone(timezone.utc)
        require(start <= when and start.date() == when.date(), 'THREE_SOURCE_INDEX_WINDOW_DAY_CHANGED')
    return body, observed['fetchedAt']


def _shape(source, stream, observations, complete, reason=None):
    records = stream.get('records', [])
    items = sorted(stream.get('items', []))
    dates = {row['url']: row['calendarDay'] for row in records if row.get('calendarDay') is not None}
    proof = {'schemaVersion': 1, 'kind': 'three_source_daily_window', 'sourceId': source['id'],
             'asOf': stream.get('asOf'), 'stream': stream,
             'dailyWindowComplete': bool(complete),
             'historicalEnumerationComplete': stream.get('historicalEnumerationComplete',
                 bool(complete) if source['id'] == cyera.SOURCE else False),
             'sourceWideRecallProved': False, 'reason': None if complete else 'DAILY_WINDOW_UNPROVED',
             'observations': [{key: copy.deepcopy(row[key]) for key in
                 ('observationId', 'requestedUrl', 'finalUrl', 'status', 'httpStatus', 'contentType',
                  'fetchedAt', 'body', 'reusesObservationId') if key in row}
                 for row in observations]}
    return {'complete': bool(complete), 'items': items, 'itemDates': dates, 'itemModified': dict(dates),
            'observations': observations, 'reason': reason,
            'originalDateStrings': {row['url']: row.get('dateLiteral') for row in records},
            'timezone': None, 'sourceDateAnomalies': stream.get('sourceDateAnomalies', []),
            'undeterminedWindowItems': stream.get('undeterminedWindowItems', []),
            'boundaryAmbiguousItems': stream.get('boundaryAmbiguousItems', []),
            'currentWindowQuiet': bool(complete and stream.get('currentWindowQuiet')),
            'sourceWindow': proof}


def discover_bound(source, request):
    """Pure adapter core; the registered caller additionally requires exact row authority."""
    is_cyera = _identity(source)
    observations, pages, stream, anchor = [], [], {}, None
    url = source['url']
    try:
        for _ in range(1 if is_cyera else prn.MAX_PAGES):
            body, fetched_at = _response(source, url, request, observations, anchor)
            anchor = anchor or fetched_at
            if is_cyera:
                stream = cyera.parse_press_list(body, source['id'], anchor, 30, source['seedEvidenceUrls'])
                require(all(stream['knownSeedMembership'].values()), 'CYERA_CURRENT_DECLARED_SEED_MISSING')
                complete = stream['dailyWindowComplete']
                return _shape(source, stream, observations, complete,
                              None if complete else 'CYERA_DAILY_WINDOW_UNPROVED')
            pages.append({'url': url, 'body': body})
            candidate = prn.derive_stream(source['id'], pages, anchor)
            stream = candidate
            if stream['dailyWindowComplete']:
                return _shape(source, stream, observations, True)
            last = stream['pages'][-1]
            if last['terminalProved']:
                return _shape(source, stream, observations, False, 'PRN_DAILY_WINDOW_UNPROVED')
            url = last['next']
        return _shape(source, stream, observations, False, 'PRN_DAILY_PAGE_BOUND_EXHAUSTED')
    except (ValueError, KeyError, TypeError, OSError, UnicodeError) as error:
        return _shape(source, stream, observations, False,
                      'THREE_SOURCE_INDEX_INCOMPLETE:' + str(error)[:160])


def discover(source, request):
    from three_source_qualification_origin import validate_source
    validate_source(source)
    return discover_bound(source, request)


def verify_window(found, manifest):
    require(found.get('sourceWindow') is not None and
            digest(found['sourceWindow']) == digest(manifest.get('sourceWindow')),
            'THREE_SOURCE_DISCOVERY_WINDOW_PROOF_DIFFERS')
