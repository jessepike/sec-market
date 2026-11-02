"""Pure closed Q4 press-list parsing. Dates are calendar hints, never event times."""
import json
import re
from datetime import datetime, timedelta, timezone

from contracts import digest, instant, require

VERSION = 'q4-press-list-single-response-v1'
NULL_OVERRIDE_VERSION = 'q4-press-list-single-response-null-override-v2'
NULL_OVERRIDE_FIELD = 'UrlOverrideContentFileWorkflowId'
HOSTS = {'jfrog:official:1': 'investors.jfrog.com', 'rapid7:official:1': 'investors.rapid7.com'}
ROW_FIELDS = set('Attachments Body Category DocumentFileSize DocumentFileType DocumentPath ExcludeFromLatest '
                 'Headline LanguageId LinkToDetailPage LinkToPage LinkToUrl MediaCollection MediaFiles MetaData '
                 'OpenInNewWindow PressReleaseDate PressReleaseId ProjectWorkflowId RelatedDocumentContentFileWorkflowId '
                 'RevisionNumber SeoName ShortBody ShortDescription Subheadline SubheadlineHtml TagsList ThumbnailPath WorkflowId'.split())


def _object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'Q4_LIST_DUPLICATE_JSON_KEY')
        value[key] = item
    return value


def _constant(_):
    raise ValueError('Q4_LIST_NON_JSON_CONSTANT')


def parse_press_list(raw, source_id, as_of, window_days=30, *, implementation_profile=NULL_OVERRIDE_VERSION):
    """Validate every row before producing a complete finite returned inventory.

    The caller separately proves the first-party single-response client graph.
    No server-wide recall, source qualification or semantic credit is asserted here.
    """
    require(type(implementation_profile) is str and implementation_profile in (VERSION, NULL_OVERRIDE_VERSION),
            'Q4_DISCOVERY_PROFILE_INVALID')
    require(source_id in HOSTS and type(raw) is bytes and 0 < len(raw) <= 2_000_000,
            'Q4_LIST_SOURCE_OR_BYTES_INVALID')
    require(type(window_days) is int and 0 < window_days <= 365, 'Q4_LIST_WINDOW_INVALID')
    day = instant(as_of).astimezone(timezone.utc).date()
    cutoff = day - timedelta(days=window_days)
    envelope = json.loads(raw.decode('utf-8-sig', errors='strict'), object_pairs_hook=_object,
                          parse_constant=_constant)
    require(type(envelope) is dict and set(envelope) == {'GetPressReleaseListResult'} and
            type(envelope['GetPressReleaseListResult']) is list and bool(envelope['GetPressReleaseListResult']),
            'Q4_LIST_NONEMPTY_EXACT_ENVELOPE_REQUIRED')
    records, ids, workflows, urls = [], set(), set(), set()
    previous = None
    schema = None
    for index, row in enumerate(envelope['GetPressReleaseListResult']):
        allowed = (ROW_FIELDS,) if implementation_profile == VERSION else (ROW_FIELDS, ROW_FIELDS | {NULL_OVERRIDE_FIELD})
        require(type(row) is dict and set(row) in allowed,
                'Q4_LIST_ROW_SCHEMA_INVALID')
        fields = set(row)
        require(schema is None or fields == schema, 'Q4_LIST_MIXED_ROW_SCHEMA')
        schema = fields
        require(NULL_OVERRIDE_FIELD not in row or row[NULL_OVERRIDE_FIELD] is None,
                'Q4_LIST_NON_NULL_URL_OVERRIDE')
        title, literal, href = row['Headline'], row['PressReleaseDate'], row['LinkToDetailPage']
        require(type(row['LanguageId']) is int and row['LanguageId'] == 1 and
                type(row['PressReleaseId']) is int and row['PressReleaseId'] > 0 and
                isinstance(row['WorkflowId'], str) and
                re.fullmatch(r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}', row['WorkflowId']) and
                isinstance(title, str) and title.strip() == title and bool(title), 'Q4_LIST_IDENTITY_INVALID')
        require(isinstance(literal, str) and re.fullmatch(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}', literal),
                'Q4_LIST_DATE_SYNTAX_INVALID')
        stamp = datetime.strptime(literal, '%m/%d/%Y %H:%M:%S')
        require(previous is None or stamp <= previous, 'Q4_LIST_UNORDERED_DATE')
        previous = stamp
        require(isinstance(href, str) and re.fullmatch(
                r'/news/news-details/' + str(stamp.year) + r'/[A-Za-z0-9_.~()-]+/default\.aspx', href) and
                '/./' not in href and '/../' not in href, 'Q4_LIST_DETAIL_URL_INVALID')
        url = 'https://' + HOSTS[source_id] + href
        require(row['PressReleaseId'] not in ids and row['WorkflowId'] not in workflows and url not in urls,
                'Q4_LIST_DUPLICATE_OR_CONFLICTING_IDENTITY')
        ids.add(row['PressReleaseId']); workflows.add(row['WorkflowId']); urls.add(url)
        require(row['Body'] is None or isinstance(row['Body'], str), 'Q4_LIST_BODY_FIELD_INVALID')
        records.append({'rowIndex': index, 'recordSha256': digest(row), 'pressReleaseId': row['PressReleaseId'],
                        'workflowId': row['WorkflowId'], 'title': title, 'url': url, 'dateLiteral': literal,
                        'calendarDay': stamp.date().isoformat(), 'timezone': None,
                        'dateAnomaly': 'FUTURE_PUBLICATION_CALENDAR_UNRESOLVED' if stamp.date() > day + timedelta(days=1) else None,
                        'boundaryAmbiguous': stamp.date() in (cutoff, day, day + timedelta(days=1))})
    dates = {row['url']: row['calendarDay'] for row in records}
    current = [row['url'] for row in records if cutoff.isoformat() <= row['calendarDay'] <= day.isoformat()]
    older = [row['url'] for row in records if row['calendarDay'] < cutoff.isoformat()]
    undetermined = [row['url'] for row in records if row['calendarDay'] > day.isoformat()]
    version = NULL_OVERRIDE_VERSION if NULL_OVERRIDE_FIELD in schema else VERSION
    return {'parserVersion': version, 'sourceId': source_id, 'asOf': as_of, 'datePrecision': 'calendar_day',
            'timezone': None, 'windowStart': cutoff.isoformat(), 'windowEnd': day.isoformat(),
            'records': records, 'items': sorted(urls), 'itemDates': dates, 'itemModified': dict(dates),
            'originalDateStrings': {row['url']: row['dateLiteral'] for row in records},
            'currentWindowItems': current, 'historicalItems': older,
            'undeterminedWindowItems': undetermined,
            'sourceDateAnomalies': [{'url': row['url'], 'reason': row['dateAnomaly']}
                                    for row in records if row['dateAnomaly'] is not None],
            'boundaryAmbiguousItems': [row['url'] for row in records if row['boundaryAmbiguous']],
            'olderBoundaryPresent': bool(older), 'currentWindowQuiet': not current and not undetermined and bool(older)}
