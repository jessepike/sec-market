"""Neutral SEC submissions-index checks. No networking, extraction or fact admission.

The supplier/issuer relationship must be qualified separately before registration.
Document inputs are ordered {url, document} objects with the original decoded JSON.
Transport observation and raw-byte integrity remain the collector's responsibility.
"""
import copy
from datetime import date, timedelta, timezone
import re

from contracts import digest, instant, require

TABLE_FIELDS = {
    'accessionNumber', 'filingDate', 'reportDate', 'acceptanceDateTime', 'act', 'form',
    'fileNumber', 'filmNumber', 'items', 'size', 'isXBRL', 'isInlineXBRL',
    'primaryDocument', 'primaryDocDescription',
}
STRING_FIELDS = {'act', 'fileNumber', 'filmNumber', 'items', 'primaryDocDescription'}


def validate_index_source(source, suppliers=None):
    """Validate an explicit declaration; with suppliers, also check subject kind/join.

    Return the original source unchanged. This never establishes qualification
    evidence for the declared direct or parent relationship.
    """
    require(isinstance(source, dict) and source.get('kind') == 'sec_index'
            and source.get('family') == 'regulatory_filings', 'Invalid neutral SEC index kind/family')
    require(all(isinstance(source.get(key), str) and source[key].strip() for key in ('id', 'supplierId')),
            'SEC index source/subject identity missing')
    require(source.get('registration') in ('candidate', 'verified') and type(source.get('required')) is bool,
            'SEC index requires normal registration status and boolean requirement')
    require(type(source.get('maxPages')) is int and 1 <= source['maxPages'] <= 1000,
            'Invalid SEC index page bound')
    require(type(source.get('lookbackDays', 365)) is int and 1 <= source.get('lookbackDays', 365) <= 3650,
            'Invalid SEC index retained window')
    issuer = source.get('regulatoryIssuer')
    require(isinstance(issuer, dict) and set(issuer) == {'cik', 'legalName', 'relationship'},
            'SEC index issuer schema differs')
    require(isinstance(issuer['cik'], str) and re.fullmatch(r'[0-9]{10}', issuer['cik'])
            and int(issuer['cik']) > 0, 'SEC index issuer CIK must be a nonzero ten-digit string')
    require(isinstance(issuer['legalName'], str) and issuer['legalName'].strip() == issuer['legalName']
            and issuer['legalName'] and not re.search(r'[\x00-\x1f\x7f]', issuer['legalName']),
            'SEC index issuer legal name missing or malformed')
    require(issuer['relationship'] in ('direct', 'parent'), 'Invalid SEC index issuer relationship')
    endpoint = 'https://data.sec.gov/submissions/CIK' + issuer['cik'] + '.json'
    require(source.get('url') == endpoint and source.get('allowedHosts') == ['data.sec.gov'],
            'SEC index requires its exact issuer endpoint and restricted host')
    if suppliers is not None:
        require(isinstance(suppliers, list) and all(isinstance(supplier, dict) for supplier in suppliers),
                'SEC index supplier inventory must contain objects')
        matches = [supplier for supplier in suppliers if supplier.get('id') == source['supplierId']]
        require(len(matches) == 1, 'SEC index subject supplier missing or duplicate')
        supplier = matches[0]
        require(source['id'] in supplier.get('sourceIds', []), 'SEC index source absent from subject supplier')
        expected_kind = 'public' if issuer['relationship'] == 'direct' else 'segment'
        require(supplier.get('kind') == expected_kind, 'SEC index relationship incompatible with subject kind')
    return source


def _date(value, label):
    require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value), label + ' must be a date')
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        require(False, label + ' is invalid')
    return parsed


def _cik(value):
    require((type(value) is int and 0 < value < 10**10)
            or (isinstance(value, str) and re.fullmatch(r'[0-9]{1,10}', value) and int(value) > 0),
            'SEC response CIK malformed')
    return str(value).zfill(10)


def _table(value, checked, label):
    require(isinstance(value, dict) and TABLE_FIELDS.issubset(value), label + ' filing table fields missing')
    require(all(isinstance(column, list) for column in value.values()), label + ' filing table column is not an array')
    count = len(value['accessionNumber'])
    require(all(len(column) == count for column in value.values()), label + ' filing table array lengths differ')
    rows = [{key: column[index] for key, column in value.items()} for index in range(count)]
    for row in rows:
        accession = row['accessionNumber']
        require(isinstance(accession, str) and re.fullmatch(r'[0-9]{10}-[0-9]{2}-[0-9]{6}', accession),
                label + ' invalid filing accession')
        require(_date(row['filingDate'], label + ' filing date') <= checked.date(), label + ' future filing date')
        if row['reportDate'] != '':
            _date(row['reportDate'], label + ' report date')
        require(isinstance(row['acceptanceDateTime'], str) and row['acceptanceDateTime'], label + ' acceptance time missing')
        require(instant(row['acceptanceDateTime']) <= checked, label + ' future filing acceptance time')
        require(isinstance(row['form'], str) and row['form'].strip() == row['form'] and row['form']
                and len(row['form']) <= 80 and not re.search(r'[\x00-\x1f\x7f]', row['form']), label + ' invalid filing form')
        document = row['primaryDocument']
        require(isinstance(document, str) and document and all(
            part not in ('.', '..') and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', part)
            for part in document.split('/')), label + ' unsafe primary document path')
        require(all(isinstance(row[key], str) for key in STRING_FIELDS), label + ' invalid filing metadata')
        require((type(row['size']) is int and row['size'] >= 0)
                or (isinstance(row['size'], str) and re.fullmatch(r'[0-9]+', row['size'])), label + ' invalid filing size')
        require(all(type(row[key]) is int and row[key] in (0, 1) for key in ('isXBRL', 'isInlineXBRL')),
                label + ' invalid filing XBRL flags')
    return rows


def verify_index_documents(source, documents, checked_at):
    """Independently verify the complete URL-bound index set and return zero facts.

    Required older pages come only from the initial issuer's filings.files
    metadata. No secondary page can replace that issuer response. Duplicate
    identical rows are counted transparently; conflicting full rows fail.
    """
    validate_index_source(source)
    require(source['registration'] == 'verified', 'SEC index acceptance requires verified source registration')
    checked = instant(checked_at).astimezone(timezone.utc)
    cutoff = checked.date() - timedelta(days=source.get('lookbackDays', 365))
    require(isinstance(documents, list) and documents and len(documents) <= source['maxPages'],
            'SEC index document inventory missing or exceeds page bound')
    for item in documents:
        require(isinstance(item, dict) and set(item) == {'url', 'document'}
                and isinstance(item['url'], str) and isinstance(item['document'], dict), 'SEC index document wrapper malformed')
    require(documents[0]['url'] == source['url'], 'Initial SEC issuer response must be first')
    urls = [item['url'] for item in documents]
    require(len(urls) == len(set(urls)), 'Duplicate SEC index page')
    initial = documents[0]['document']
    issuer = source['regulatoryIssuer']
    require(_cik(initial.get('cik')) == issuer['cik'] and initial.get('name') == issuer['legalName'],
            'SEC index initial issuer CIK/name differs')
    filings = initial.get('filings')
    require(isinstance(filings, dict) and isinstance(filings.get('files'), list), 'Initial SEC filings/history metadata missing')
    recent = _table(filings.get('recent'), checked, 'Initial SEC index')
    required, names = {}, set()
    for archive in filings['files']:
        require(isinstance(archive, dict) and set(archive) == {'name', 'filingCount', 'filingFrom', 'filingTo'},
                'SEC older index metadata schema differs')
        name = archive['name']
        require(isinstance(name, str) and re.fullmatch(r'CIK' + issuer['cik'] + r'-submissions-[0-9]{3}\.json', name),
                'Unsafe SEC older index filename or wrong issuer')
        require(name not in names, 'Duplicate SEC older index metadata')
        names.add(name)
        first = _date(archive['filingFrom'], 'Older SEC index first date')
        last = _date(archive['filingTo'], 'Older SEC index last date')
        require(first <= last <= checked.date(), 'SEC older index date boundaries invalid')
        require(type(archive['filingCount']) is int and archive['filingCount'] > 0, 'Invalid SEC older index filing count')
        if last >= cutoff:
            required['https://data.sec.gov/submissions/' + name] = archive
    require(set(urls[1:]) == set(required), 'SEC retained older index pages missing, extra or unlisted')
    all_rows, summaries = [], []
    for index, item in enumerate(documents):
        metadata = None
        if index == 0:
            rows = recent
        else:
            rows = _table(item['document'], checked, 'Older SEC index')
            metadata = required[item['url']]
            require(len(rows) == metadata['filingCount'], 'SEC older index filing count differs from metadata')
            dates = [row['filingDate'] for row in rows]
            # In the two pinned historical tables, filingTo encloses a range
            # ending after the observed last filing. Require containment and
            # exact count, without assuming every declared endpoint has a row.
            require(metadata['filingFrom'] <= min(dates) <= max(dates) <= metadata['filingTo'],
                    'SEC older index rows outside declared retained boundaries')
        all_rows.extend(rows)
        dates = [row['filingDate'] for row in rows]
        summaries.append({'url': item['url'], 'documentSha256': digest(item['document']),
                          'filingRows': len(rows), 'firstFilingDate': min(dates) if dates else None,
                          'lastFilingDate': max(dates) if dates else None,
                          'declaredFilingFrom': metadata['filingFrom'] if metadata else None,
                          'declaredFilingTo': metadata['filingTo'] if metadata else None,
                          'declaredFilingCount': metadata['filingCount'] if metadata else None})
    unique_rows = {}
    for row in all_rows:
        accession = row['accessionNumber']
        require(accession not in unique_rows or unique_rows[accession] == row,
                'Conflicting duplicate SEC accession row')
        unique_rows[accession] = row
    return {'schemaVersion': 1, 'kind': 'regulatory_index_validation', 'sourceId': source['id'],
            'supplierId': source['supplierId'], 'issuer': copy.deepcopy(issuer),
            'sourceSha256': digest(source), 'checkedAt': checked_at,
            'windowStart': cutoff.isoformat(), 'windowEnd': checked.date().isoformat(),
            'documentCount': len(documents), 'filingRows': len(all_rows), 'uniqueFilings': len(unique_rows),
            'duplicateRows': len(all_rows) - len(unique_rows),
            'retainedFilings': sum(cutoff.isoformat() <= row['filingDate'] <= checked.date().isoformat() for row in unique_rows.values()),
            'documents': summaries, 'documentsSha256': digest(documents), 'facts': []}
