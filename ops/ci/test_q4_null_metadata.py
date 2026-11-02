"""Recognize only the observed null metadata shape; grant no source qualification."""
import copy
import gzip
import io
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'web/scripts/pipeline'), str(ROOT / 'ops/ci')]
from contracts import canonical, digest
from q4_press_list import NULL_OVERRIDE_FIELD, NULL_OVERRIDE_VERSION, VERSION, parse_press_list
from test_q4_press_list import AS_OF, BODIES, encoded, row

SEED = ROOT / 'contracts/q4-qualification-seeds/47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a'
OLD_OUTPUTS = ('b626aa3327add51d31636267b345bc3581ce6ecf43b3b6129464c03a468a3f59',
               '81964c9dd4f47165c689c9e68a4487bf1439050a0fa17a35a066ad0612aee866')
CAPTURE = os.environ.get('SMP_Q4_NULL_METADATA_CAPTURE_ROOT')
MANIFEST = os.environ.get('SMP_Q4_NULL_METADATA_ARCHIVE_MANIFEST')
MANIFEST_SHA = '3cb739133b60e03d418480e53ee8c454dca616efa8d3585fde87c5eb9ac61438'
FIXTURES = ROOT / 'ops/ci/fixtures/q4-null-metadata-2026-11-02'
PROVENANCE_SHA = '13f17e3068e3a4fff03fc64c068921cc05904e191f9714ddf381346190582f39'
MAX_BODY_BYTES = 2_000_000
ACTUAL = (
    ('jfrog', '55403fd7a14cff45307e52173b26530fc766b2e5db66e1b7c1f8393ebd80836f', 292860,
     '05f1b3dcb0cb1f7e98e1ff349bdbfbbfedcaff58b274372902abda874aabeb2e', 207, 4, 203),
    ('rapid7', '4c6671119e33f158028fb690656b4c1ffe336ae86ac151ca2e6117bfd05d1ad9', 427470,
     'dd0e01931667da797d6d6a89dfc94869aa53033fa09b6e94741bb42e11813cce', 323, 3, 320),
)


def null_row(number=1, date='10/14/2026 16:05:00'):
    return {**row(number, date), NULL_OVERRIDE_FIELD: None}


def bounded_gzip(raw):
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_BODY_BYTES:
        raise ValueError('FIXTURE_COMPRESSED_SIZE_INVALID')
    with gzip.GzipFile(fileobj=io.BytesIO(raw), mode='rb') as source:
        decoded = source.read(MAX_BODY_BYTES + 1)
    if not 0 < len(decoded) <= MAX_BODY_BYTES:
        raise ValueError('FIXTURE_DECODED_SIZE_INVALID')
    return decoded


class NullMetadataTests(unittest.TestCase):
    def parse(self, rows):
        return parse_press_list(encoded(rows), 'jfrog:official:1', AS_OF)

    def test_exact_null_variant_has_distinct_version_and_full_actual_row_hash(self):
        item = null_row()
        result = self.parse([item, null_row(2, '09/02/2026 08:30:00')])
        self.assertEqual(result['parserVersion'], NULL_OVERRIDE_VERSION)
        self.assertNotEqual(NULL_OVERRIDE_VERSION, VERSION)
        self.assertEqual(result['records'][0]['recordSha256'], digest(item))
        self.assertNotEqual(result['records'][0]['recordSha256'], digest(row()))
        self.assertEqual(result['originalDateStrings'][result['records'][0]['url']], item['PressReleaseDate'])
        self.assertIsNone(result['timezone'])
        self.assertEqual((len(result['currentWindowItems']), len(result['historicalItems'])), (1, 1))
        self.assertNotIn('qualified', result)
        self.assertNotIn('facts', result)

    def test_every_non_null_override_rejects_including_false_empty_and_routing_values(self):
        for value in ('', 0, False, [], {}, 'https://other.example/', '/other',
                      '00000000-0000-0000-0000-000000000001'):
            with self.subTest(value=value):
                changed = null_row()
                changed[NULL_OVERRIDE_FIELD] = value
                with self.assertRaisesRegex(ValueError, 'Q4_LIST_NON_NULL_URL_OVERRIDE'):
                    self.parse([changed])

    def test_mixed_recognized_shapes_reject_in_either_order(self):
        for rows in ([row(), null_row(2)], [null_row(), row(2)]):
            with self.subTest(rows=rows), self.assertRaisesRegex(ValueError, 'Q4_LIST_MIXED_ROW_SCHEMA'):
                self.parse(rows)

    def test_unknown_extra_or_missing_original_field_stays_rejected(self):
        changed = null_row()
        changed['nextPage'] = None
        with self.assertRaisesRegex(ValueError, 'Q4_LIST_ROW_SCHEMA_INVALID'):
            self.parse([changed])
        for key in row():
            changed = null_row()
            del changed[key]
            with self.subTest(field=key), self.assertRaisesRegex(ValueError, 'Q4_LIST_ROW_SCHEMA_INVALID'):
                self.parse([changed])

    def test_duplicate_json_null_field_is_not_silently_deduplicated(self):
        field = json.dumps(NULL_OVERRIDE_FIELD).encode() + b':null'
        raw = encoded([null_row()]).replace(field, field + b',' + field)
        with self.assertRaisesRegex(ValueError, 'Q4_LIST_DUPLICATE_JSON_KEY'):
            parse_press_list(raw, 'jfrog:official:1', AS_OF)

    def test_new_shape_keeps_identity_date_order_and_url_guards(self):
        for key, value in (('PressReleaseId', True), ('LanguageId', 2),
                           ('WorkflowId', 'invalid'), ('PressReleaseDate', '10/14/2026'),
                           ('LinkToDetailPage', 'https://other.example/')):
            changed = null_row()
            changed[key] = value
            with self.subTest(field=key), self.assertRaises(ValueError):
                self.parse([changed])
        with self.assertRaisesRegex(ValueError, 'Q4_LIST_UNORDERED_DATE'):
            self.parse([null_row(1, '09/02/2026 00:00:00'), null_row(2)])

    def test_committed_old_primary_arrays_keep_complete_original_output_bytes(self):
        for index, source in enumerate(('jfrog:official:1', 'rapid7:official:1')):
            raw = (SEED / ('objects__' + BODIES[index])).read_bytes()
            self.assertEqual(digest(raw), BODIES[index])
            result = parse_press_list(raw, source, AS_OF)
            self.assertEqual(result['parserVersion'], VERSION)
            self.assertEqual(digest(result), OLD_OUTPUTS[index])
            self.assertEqual(len(canonical(result)), (271835, 435895)[index])

    def test_fixture_decompression_is_bounded_and_rejects_invalid_gzip(self):
        self.assertEqual(bounded_gzip(gzip.compress(b'fixture', mtime=0)), b'fixture')
        for raw in (b'', b'x' * (MAX_BODY_BYTES + 1)):
            with self.assertRaisesRegex(ValueError, 'FIXTURE_COMPRESSED_SIZE_INVALID'):
                bounded_gzip(raw)
        with self.assertRaisesRegex(ValueError, 'FIXTURE_DECODED_SIZE_INVALID'):
            bounded_gzip(gzip.compress(b'x' * (MAX_BODY_BYTES + 1), mtime=0))
        for raw in (b'not gzip', gzip.compress(b'fixture', mtime=0)[:-4]):
            with self.assertRaises((OSError, EOFError)):
                bounded_gzip(raw)


class ActualNullMetadataTests(unittest.TestCase):
    def setUp(self):
        self.touched = {}
        raw = self.read(FIXTURES / 'provenance.json')
        self.assertEqual(digest(raw), PROVENANCE_SHA)
        self.provenance = json.loads(raw)
        self.assertEqual(self.provenance['archive'], {
            'commit': '52632a360f4099f142ed0e10e46338e1d91f1bc9',
            'manifestSha256': MANIFEST_SHA, 'manifestEntries': 69873,
            'manifestUrl': 'https://github.com/jessepike/sec-market/blob/52632a360f4099f142ed0e10e46338e1d91f1bc9/archive-manifest.json'})
        selected = self.provenance['selectedManifestEntries']
        self.entries = {entry['key']: entry for entry in selected}
        self.assertEqual(len(self.entries), 4)
        self.assertEqual(len(selected), 4)
        # The committed subset preserves the earlier authenticated selection. It
        # does not independently prove the full archive's hash without its bytes.
        if MANIFEST:
            full_raw = self.read(Path(MANIFEST), maximum=32_000_000)
            self.assertEqual(digest(full_raw), MANIFEST_SHA)
            full = json.loads(full_raw)['files']
            self.assertEqual(len(full), 69873)
            full_entries = {entry['key']: entry for entry in full}
            for entry in selected:
                self.assertEqual(entry, full_entries[entry['key']])

    def read(self, path, maximum=64_000):
        with path.open('rb') as source:
            raw = source.read(maximum + 1)
        self.assertLessEqual(len(raw), maximum)
        self.touched[path] = (digest(raw), len(raw), path.stat().st_mtime_ns)
        return raw

    def tearDown(self):
        for path, expected in self.touched.items():
            raw = path.read_bytes()
            self.assertEqual((digest(raw), len(raw), path.stat().st_mtime_ns), expected)

    def capture(self, name, body_sha, byte_count, observation_sha):
        declared = next(source for source in self.provenance['sources'] if source['sourceId'] == name + ':official:1')
        self.assertEqual(declared['bodyGzip']['file'], name + '.json.gz')
        compressed = self.read(FIXTURES / declared['bodyGzip']['file'], maximum=MAX_BODY_BYTES)
        self.assertEqual((digest(compressed), len(compressed)),
                         (declared['bodyGzip']['sha256'], declared['bodyGzip']['bytes']))
        raw = bounded_gzip(compressed)
        self.assertEqual(declared['observation']['file'], name + '-observation.json')
        observed_raw = self.read(FIXTURES / declared['observation']['file'])
        observed = json.loads(observed_raw)
        self.assertEqual((digest(raw), len(raw)), (body_sha, byte_count))
        self.assertEqual(declared['body'], {'sha256': body_sha, 'bytes': byte_count})
        self.assertEqual(digest(observed_raw), observation_sha)
        self.assertEqual((digest(observed_raw), len(observed_raw)),
                         (declared['observation']['sha256'], declared['observation']['bytes']))
        self.assertEqual(observed['sourceId'], name + ':official:1')
        for field in ('requestedUrl', 'finalUrl', 'fetchedAt', 'contentType', 'httpStatus'):
            self.assertEqual(observed[field], declared[field])
        self.assertEqual(observed['body'], {'key': 'objects/' + body_sha, 'sha256': body_sha, 'bytes': byte_count})
        for key, content in [('state/objects/' + body_sha, raw),
                             ('state/observations/' + observed['observationId'] + '.json', observed_raw)]:
            entry = self.entries[key]
            self.assertEqual((digest(content), len(content)), (entry['sha256'], entry['bytes']))
        self.assertEqual(observed['requestedUrl'], observed['finalUrl'])
        self.assertEqual((observed['status'], observed['httpStatus']), ('fetched', 200))
        self.assertEqual(observed['contentType'], 'application/json; charset=utf-8')
        self.assertTrue(observed['fetchedAt'].startswith('2026-11-02T13:'))
        if CAPTURE:
            self.assertEqual(raw, self.read(Path(CAPTURE) / f'smp-q4-{name}-body.json', maximum=MAX_BODY_BYTES))
            self.assertEqual(observed_raw, self.read(Path(CAPTURE) / f'smp-q4-{name}-observation.json'))
        return raw, observed

    def test_actual_new_arrays_parse_without_rewriting_original_dates_rows_or_source_observations(self):
        from discovery import discover_q4_press_list
        contract = json.loads((ROOT / 'contracts/market.json').read_bytes())
        for name, body_sha, size, observation_sha, count, current, historical in ACTUAL:
            with self.subTest(source=name):
                raw, observed = self.capture(name, body_sha, size, observation_sha)
                rows = json.loads(raw)['GetPressReleaseListResult']
                self.assertEqual(len(rows), count)
                self.assertTrue(all(item[NULL_OVERRIDE_FIELD] is None for item in rows))
                parsed = parse_press_list(raw, name + ':official:1', observed['fetchedAt'])
                self.assertEqual(parsed['parserVersion'], NULL_OVERRIDE_VERSION)
                self.assertEqual((len(parsed['records']), len(parsed['items'])), (count, count))
                self.assertEqual((len(parsed['currentWindowItems']), len(parsed['historicalItems'])), (current, historical))
                self.assertEqual(parsed['sourceDateAnomalies'], [])
                self.assertEqual(parsed['undeterminedWindowItems'], [])
                for original, record in zip(rows, parsed['records']):
                    self.assertEqual(record['recordSha256'], digest(original))
                    self.assertEqual(record['dateLiteral'], original['PressReleaseDate'])
                    self.assertIsNone(record['timezone'])
                source = next(s for s in contract['sources'] if s['id'] == observed['sourceId'])
                requested = []
                def request(url):
                    requested.append(url)
                    return copy.deepcopy(observed), raw
                with patch('socket.socket', side_effect=AssertionError('Offline fixture replay forbids network')):
                    result = discover_q4_press_list(source, request)
                self.assertEqual(requested, [source['url']])
                self.assertIs(result['complete'], True)
                self.assertEqual(result['items'], parsed['items'])
                self.assertEqual(result['observations'], [observed])


if __name__ == '__main__':
    unittest.main()
