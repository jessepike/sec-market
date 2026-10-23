"""Synthetic neutral index mechanics; no fetch, model, archive write or qualification."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'web/scripts/pipeline'))
from contracts import digest
from regulatory import TABLE_FIELDS, validate_index_source, verify_index_documents


NOW = '2026-10-23T12:00:00Z'


def source(relationship='direct'):
    return {'id': 'synthetic:sec-index', 'supplierId': 'synthetic', 'kind': 'sec_index',
            'family': 'regulatory_filings', 'registration': 'verified', 'required': True,
            'url': 'https://data.sec.gov/submissions/CIK0000123456.json',
            'allowedHosts': ['data.sec.gov'], 'maxPages': 10, 'lookbackDays': 365,
            'regulatoryIssuer': {'cik': '0000123456', 'legalName': 'EXACT SYNTHETIC ISSUER INC', 'relationship': relationship}}


def row(accession='0000123456-26-000001', day='2026-10-20', **values):
    result = {'accessionNumber': accession, 'filingDate': day, 'reportDate': '',
              'acceptanceDateTime': day + 'T10:00:00Z', 'act': '34', 'form': '8-K',
              'fileNumber': '001-12345', 'filmNumber': '26123456', 'items': '5.02',
              'size': 1234, 'isXBRL': 0, 'isInlineXBRL': 0,
              'primaryDocument': 'synthetic-20261020.htm', 'primaryDocDescription': ''}
    return {**result, **values}


def table(rows):
    return {key: [item[key] for item in rows] for key in sorted(TABLE_FIELDS)}


def initial(rows=None, files=None):
    return {'cik': 123456, 'name': 'EXACT SYNTHETIC ISSUER INC',
            'filings': {'recent': table([row()] if rows is None else rows), 'files': files or []}}


def wrapped(value, url=None):
    return {'url': url or source()['url'], 'document': value}


def archive_metadata(name='CIK0000123456-submissions-001.json', day='2026-01-01', count=1):
    return {'name': name, 'filingCount': count, 'filingFrom': day, 'filingTo': day}


class RegulatoryIndexTests(unittest.TestCase):
    def test_direct_public_and_segment_parent_sources_are_explicit_and_unchanged(self):
        for relationship, kind in [('direct', 'public'), ('parent', 'segment')]:
            binding = source(relationship)
            suppliers = [{'id': 'synthetic', 'kind': kind, 'sourceIds': [binding['id']]}]
            before = copy.deepcopy(binding)
            self.assertIs(validate_index_source(binding, suppliers), binding)
            summary = verify_index_documents(binding, [wrapped(initial())], NOW)
            self.assertEqual(summary['issuer'], binding['regulatoryIssuer'])
            self.assertEqual(summary['supplierId'], 'synthetic')
            self.assertEqual(summary['facts'], [])
            self.assertEqual(summary['uniqueFilings'], 1)
            self.assertEqual(binding, before)
            summary['issuer']['legalName'] = 'Result mutation'
            self.assertEqual(binding, before)

    def test_source_family_endpoint_host_registration_and_bounds_fail_closed(self):
        for key, value in [
            ('kind', 'sec_submissions'), ('family', 'official_announcements'), ('registration', 'unknown'),
            ('required', 1), ('maxPages', 0), ('maxPages', True), ('lookbackDays', 0),
            ('allowedHosts', ['data.sec.gov', 'www.sec.gov']),
            ('url', 'https://data.sec.gov/submissions/CIK0000999999.json'),
            ('url', 'https://data.sec.gov/submissions/CIK0000123456.json?x=1'),
            ('url', 'https://data.sec.gov/submissions/CIK0000123456.json#fragment'),
            ('url', 'https://user@data.sec.gov/submissions/CIK0000123456.json'),
            ('url', 'https://data.sec.gov:443/submissions/CIK0000123456.json'),
            ('url', 'http://data.sec.gov/submissions/CIK0000123456.json'),
        ]:
            binding = {**source(), key: value}
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate_index_source(binding)

    def test_candidate_source_shape_is_valid_but_cannot_accept_any_index(self):
        binding = {**source(), 'registration': 'candidate'}
        suppliers = [{'id': 'synthetic', 'kind': 'public', 'sourceIds': [binding['id']]}]
        self.assertIs(validate_index_source(binding, suppliers), binding)
        with self.assertRaisesRegex(ValueError, 'requires verified source registration'):
            verify_index_documents(binding, [wrapped(initial())], NOW)

    def test_issuer_shape_and_subject_relationship_cannot_be_inferred(self):
        for issuer in [None, {'cik': '0000123456'},
                       {**source()['regulatoryIssuer'], 'cik': 123456},
                       {**source()['regulatoryIssuer'], 'cik': '0000000000'},
                       {**source()['regulatoryIssuer'], 'cik': '123456'},
                       {**source()['regulatoryIssuer'], 'legalName': ' EXACT SYNTHETIC ISSUER INC'},
                       {**source()['regulatoryIssuer'], 'relationship': 'brand'},
                       {**source()['regulatoryIssuer'], 'claim': 'unqualified mapping'}]:
            with self.subTest(issuer=issuer), self.assertRaises(ValueError):
                validate_index_source({**source(), 'regulatoryIssuer': issuer})
        for relationship, kind in [('direct', 'segment'), ('parent', 'public'), ('direct', 'private'), ('parent', 'acquired')]:
            binding = source(relationship)
            with self.subTest(relationship=relationship, kind=kind), self.assertRaisesRegex(ValueError, 'subject kind'):
                validate_index_source(binding, [{'id': 'synthetic', 'kind': kind, 'sourceIds': [binding['id']]}])
        for suppliers in [[], [{'id': 'other', 'kind': 'public', 'sourceIds': [source()['id']]}],
                          [{'id': 'synthetic', 'kind': 'public', 'sourceIds': []}],
                          [{'id': 'synthetic', 'kind': 'public'}, {'id': 'synthetic', 'kind': 'public'}]]:
            with self.subTest(suppliers=suppliers), self.assertRaises(ValueError):
                validate_index_source(source(), suppliers)

    def test_initial_exact_cik_name_and_wrapper_order_are_required(self):
        for changes in [{'cik': 999999}, {'cik': True}, {'cik': 'not-cik'}, {'name': 'FAMILIAR WRONG NAME'},
                        {'name': 'exact synthetic issuer inc'}, {'name': 'EXACT SYNTHETIC ISSUER INC '}, {'filings': {}}]:
            body = {**initial(), **changes}
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                verify_index_documents(source(), [wrapped(body)], NOW)
        for documents in [[], [wrapped(initial(), 'https://data.sec.gov/submissions/CIK0000123456-submissions-001.json')],
                          [{'url': source()['url'], 'document': '<html>Access denied</html>'}],
                          [{'url': source()['url'], 'document': initial(), 'untrusted': True}],
                          [wrapped({'cik': 123456, 'name': 'EXACT SYNTHETIC ISSUER INC'})]]:
            with self.subTest(documents=documents), self.assertRaises(ValueError):
                verify_index_documents(source(), documents, NOW)

    def test_requires_all_normal_table_arrays_and_equal_lengths_including_extra_columns(self):
        for missing in TABLE_FIELDS:
            body = initial()
            del body['filings']['recent'][missing]
            with self.subTest(missing=missing), self.assertRaisesRegex(ValueError, 'fields missing'):
                verify_index_documents(source(), [wrapped(body)], NOW)
        for value in [None, 'not-array', {}, []]:
            body = initial()
            body['filings']['recent']['filingDate'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                verify_index_documents(source(), [wrapped(body)], NOW)
        body = initial()
        body['filings']['recent']['futureSECField'] = []
        with self.assertRaisesRegex(ValueError, 'lengths differ'):
            verify_index_documents(source(), [wrapped(body)], NOW)

    def test_rejects_malformed_full_filing_rows(self):
        for key, value in [('accessionNumber', '000012345626000001'), ('accessionNumber', '../wrong'),
                           ('filingDate', '2026-02-30'), ('filingDate', '2026-10-24'),
                           ('reportDate', 'invalid'), ('acceptanceDateTime', ''),
                           ('acceptanceDateTime', '2026-10-23T13:00:00Z'), ('form', ''), ('form', '8-K\n'),
                           ('size', -1), ('size', True), ('isXBRL', 2), ('isInlineXBRL', False), ('act', None)]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                verify_index_documents(source(), [wrapped(initial([row(**{key: value})]))], NOW)

    def test_primary_document_paths_reject_url_traversal_encoding_and_unsafe_names(self):
        for path in ['', '../filing.htm', 'x/../filing.htm', './filing.htm', '/filing.htm',
                     'https://evil.invalid/filing.htm', 'x//filing.htm', 'x\\filing.htm',
                     'filing.htm?x=1', 'filing.htm#x', '%2e%2e/filing.htm', 'file name.htm', 'x/%2Ffiling.htm']:
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'unsafe primary document'):
                verify_index_documents(source(), [wrapped(initial([row(primaryDocument=path)]))], NOW)
        summary = verify_index_documents(source(), [wrapped(initial([row(primaryDocument='xslF345X05/primary_doc.xml')]))], NOW)
        self.assertEqual(summary['uniqueFilings'], 1)

    def test_exact_mandatory_older_pages_and_metadata_are_replayed(self):
        old = row('0000123456-26-000002', '2026-01-01')
        metadata = archive_metadata()
        url = 'https://data.sec.gov/submissions/' + metadata['name']
        documents = [wrapped(initial(files=[metadata])), wrapped(table([old]), url)]
        before = copy.deepcopy(documents)
        summary = verify_index_documents(source(), documents, NOW)
        self.assertEqual(summary['documentCount'], 2)
        self.assertEqual(summary['filingRows'], 2)
        self.assertEqual(summary['uniqueFilings'], 2)
        self.assertEqual(summary['retainedFilings'], 2)
        self.assertEqual(summary['documents'][1]['firstFilingDate'], '2026-01-01')
        self.assertEqual(summary['documentsSha256'], digest(documents))
        self.assertEqual(summary['sourceSha256'], digest(source()))
        self.assertEqual(summary['facts'], [])
        self.assertEqual(documents, before)
        for altered in [documents[:1], documents + [copy.deepcopy(documents[1])],
                        [documents[1], documents[0]],
                        documents + [wrapped(table([old]), 'https://data.sec.gov/submissions/CIK0000123456-submissions-002.json')]]:
            with self.subTest(altered=altered), self.assertRaises(ValueError):
                verify_index_documents(source(), altered, NOW)
        with self.assertRaisesRegex(ValueError, 'page bound'):
            verify_index_documents({**source(), 'maxPages': 1}, documents, NOW)

    def test_older_filename_issuer_boundaries_counts_and_duplicates_fail_closed(self):
        metadata = archive_metadata()
        for change in [{'name': '../older.json'}, {'name': 'CIK0000999999-submissions-001.json'},
                       {'name': 'CIK0000123456-submissions-001.json?x=1'}, {'filingFrom': '2026-02-30'},
                       {'filingTo': '2025-12-31'}, {'filingTo': '2026-10-24'}, {'filingCount': 0}, {'filingCount': True}]:
            altered = {**metadata, **change}
            with self.subTest(change=change), self.assertRaises(ValueError):
                verify_index_documents(source(), [wrapped(initial(files=[altered]))], NOW)
        with self.assertRaisesRegex(ValueError, 'Duplicate SEC older index metadata'):
            verify_index_documents(source(), [wrapped(initial(files=[metadata, copy.deepcopy(metadata)]))], NOW)
        older = row('0000123456-26-000002', '2026-01-01')
        url = 'https://data.sec.gov/submissions/' + metadata['name']
        for rows in [[], [older, copy.deepcopy(older)], [row('0000123456-26-000002', '2026-01-02')]]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                verify_index_documents(source(), [wrapped(initial(files=[metadata])), wrapped(table(rows), url)], NOW)

    def test_identical_duplicate_rows_are_counted_and_any_conflicting_field_fails(self):
        unchanged = row()
        result = verify_index_documents(source(), [wrapped(initial([unchanged, copy.deepcopy(unchanged)]))], NOW)
        self.assertEqual((result['filingRows'], result['uniqueFilings'], result['duplicateRows']), (2, 1, 1))
        for key, value in [('primaryDocDescription', 'different original metadata'), ('form', '8-K/A'),
                           ('filingDate', '2026-10-19'), ('size', 9999)]:
            conflicting = {**unchanged, key: value}
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'Conflicting duplicate SEC accession'):
                verify_index_documents(source(), [wrapped(initial([unchanged, conflicting]))], NOW)

    def test_no_current_filings_can_still_require_retained_older_history(self):
        metadata = archive_metadata()
        url = 'https://data.sec.gov/submissions/' + metadata['name']
        summary = verify_index_documents(source(), [wrapped(initial([], [metadata])),
            wrapped(table([row('0000123456-26-000002', '2026-01-01')]), url)], NOW)
        self.assertEqual(summary['retainedFilings'], 1)
        self.assertEqual(summary['documents'][0]['filingRows'], 0)
        with self.assertRaisesRegex(ValueError, 'pages missing'):
            verify_index_documents(source(), [wrapped(initial([], [metadata]))], NOW)
        summary = verify_index_documents(source(), [wrapped(initial([]))], NOW)
        self.assertEqual((summary['uniqueFilings'], summary['retainedFilings'], summary['facts']), (0, 0, []))

    def test_outside_window_archive_is_not_fetched_or_silently_substituted(self):
        expired = archive_metadata(day='2024-01-01')
        cutoff = archive_metadata(name='CIK0000123456-submissions-002.json', day='2025-10-23')
        url = 'https://data.sec.gov/submissions/' + cutoff['name']
        summary = verify_index_documents(source(), [wrapped(initial([], [expired, cutoff])),
            wrapped(table([row('0000123456-25-000002', '2025-10-23')]), url)], NOW)
        self.assertEqual(summary['windowStart'], '2025-10-23')
        self.assertEqual(summary['retainedFilings'], 1)
        with self.assertRaisesRegex(ValueError, 'extra or unlisted'):
            verify_index_documents(source(), [wrapped(initial([], [expired])),
                wrapped(table([row('0000123456-24-000002', '2024-01-01')]), 'https://data.sec.gov/submissions/' + expired['name'])], NOW)

    def test_unknown_fields_participate_in_full_row_conflict_detection(self):
        body = initial([row(), row()])
        body['filings']['recent']['futureSECField'] = ['same', 'different']
        with self.assertRaisesRegex(ValueError, 'Conflicting duplicate SEC accession'):
            verify_index_documents(source(), [wrapped(body)], NOW)

    def test_declared_archive_ranges_can_enclose_observed_dates_but_cannot_omit_rows(self):
        metadata = {**archive_metadata(), 'filingTo': '2026-01-31'}
        url = 'https://data.sec.gov/submissions/' + metadata['name']
        older = row('0000123456-26-000002', '2026-01-15')
        documents = [wrapped(initial(files=[metadata])), wrapped(table([older]), url)]
        summary = verify_index_documents(source(), documents, NOW)
        page = summary['documents'][1]
        self.assertEqual((page['declaredFilingFrom'], page['declaredFilingTo'], page['declaredFilingCount']),
                         ('2026-01-01', '2026-01-31', 1))
        self.assertEqual((page['firstFilingDate'], page['lastFilingDate']), ('2026-01-15', '2026-01-15'))
        for day in ('2025-12-31', '2026-02-01'):
            with self.subTest(day=day), self.assertRaisesRegex(ValueError, 'outside declared retained boundaries'):
                verify_index_documents(source(), [documents[0], wrapped(table([row('0000123456-26-000002', day)]), url)], NOW)
        with self.assertRaisesRegex(ValueError, 'filing count differs'):
            verify_index_documents(source(), [documents[0], wrapped(table([]), url)], NOW)

    def test_actual_historical_issuer_pages_when_pinned_readonly_archive_is_present(self):
        # Optional local evidence replay; always-running synthetic tests above
        # carry the acceptance rules in CI. No current freshness or subject
        # relationship is asserted by loading these historical issuer bodies.
        root = Path('/tmp/smp-coverage-baseline-20261023')
        if not (root / 'state').is_dir():
            self.skipTest('Historical read-only archive absent; synthetic neutral-index mechanics still run')
        self.assertEqual(digest((root / 'archive-manifest.json').read_bytes()),
                         '760b5c38fcb7fba2a3a223233539cce4eb5aa47d559571efa95b287047ac1ff8')
        cases = [
            ('crwd', '0001535527', 'CrowdStrike Holdings, Inc.',
             ('d7bdf41f479438099d203999aa7051df0a8eb3dbfcdb9d398f97b2f49c59d34f', 156749),
             ('ec42aac9136a82b721386b03207e592eb28f510d6fb815469e1e353972768e28', 47574),
             1307, 258, '2020-12-20', '2020-12-17'),
            ('panw', '0001327567', 'Palo Alto Networks Inc',
             ('54acd6c26e8bfcdf5e0f0dea30dabef27123525133df99729bb4ccd8f000c402', 154769),
             ('27f17d2b43ee0fb41ca44b148c2da497fd9b305e9b3cf67d63d28829f5b84937', 140668),
             1908, 130, '2019-09-30', '2019-09-19'),
        ]
        for key, cik, legal_name, root_pin, old_pin, all_count, retained, declared_to, observed_to in cases:
            pages = []
            for sha, size in (root_pin, old_pin):
                raw = (root / 'state/objects' / sha).read_bytes()
                self.assertEqual((digest(raw), len(raw)), (sha, size))
                pages.append(json.loads(raw))
            binding = {**source('parent'), 'id': 'historical-hypothetical-' + key,
                       'supplierId': 'hypothetical-subject',
                       'url': 'https://data.sec.gov/submissions/CIK' + cik + '.json',
                       'regulatoryIssuer': {'cik': cik, 'legalName': legal_name, 'relationship': 'parent'}}
            documents = [wrapped(pages[0], binding['url']), wrapped(pages[1],
                'https://data.sec.gov/submissions/CIK' + cik + '-submissions-001.json')]
            # Retain the auditor's original historical observation time.
            at = '2026-10-23T20:32:39.105568Z'
            current_window = verify_index_documents(binding, documents[:1], at)
            self.assertEqual(current_window['retainedFilings'], retained)
            self.assertEqual(current_window['facts'], [])
            all_pages = verify_index_documents({**binding, 'lookbackDays': 3650}, documents, at)
            self.assertEqual(all_pages['uniqueFilings'], all_count)
            self.assertEqual(all_pages['facts'], [])
            self.assertEqual(all_pages['documents'][1]['declaredFilingTo'], declared_to)
            self.assertEqual(all_pages['documents'][1]['lastFilingDate'], observed_to)
            self.assertLess(observed_to, declared_to)
            outside = copy.deepcopy(documents)
            outside[1]['document']['filingDate'][0] = '2026-10-20'
            with self.assertRaisesRegex(ValueError, 'outside declared retained boundaries'):
                verify_index_documents({**binding, 'lookbackDays': 3650}, outside, at)
            missing = copy.deepcopy(documents)
            for column in missing[1]['document'].values():
                column.pop()
            with self.assertRaisesRegex(ValueError, 'filing count differs'):
                verify_index_documents({**binding, 'lookbackDays': 3650}, missing, at)


if __name__ == '__main__':
    unittest.main()
