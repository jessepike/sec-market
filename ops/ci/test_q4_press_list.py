"""Closed returned-array parsing. Fictional arrays grant no source credit."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'web/scripts/pipeline'), str(ROOT / 'ops/ci')]
from contracts import canonical, digest
from q4_press_list import ROW_FIELDS, parse_press_list

ARCHIVE = Path('/var/tmp/smp-q4-initial-data-actual-40184027106-20261025/extracted')
AS_OF = '2026-10-25T10:19:17.801039Z'
BODIES = ('f7d84b288a6665280f4b8ade996b0bf64fe9c3fa0ea7a8a15b1adfb0826ccc19',
          'cf3c57d1c2080d65656e9f291eca371aefd99909476d413bb5c90155bc742db8')


class ReadOnlyD660:
    def __init__(self):
        raw = (ARCHIVE / 'archive-manifest.json').read_bytes()
        assert digest(raw) == '40873bfd2dca9836b58ac325a3afb32919fb463b2082752cb72fc785a2d7239d'
        self.entries = {r['key']: r for r in json.loads(raw)['files']}; self.touched = {}
    def raw(self, key):
        path = ARCHIVE / 'state' / key; entry = self.entries.get('state/' + key)
        if entry is None:
            assert not path.exists(); return None
        raw = path.read_bytes(); assert digest(raw) == entry['sha256'] and len(raw) == entry['bytes']
        self.touched[str(path)] = (digest(raw), len(raw), path.stat().st_mtime_ns)
        return raw
    def read(self, key):
        raw = self.raw(key); return json.loads(raw) if raw is not None else None
    def get(self, ref):
        raw = self.raw(ref['key']); assert digest(raw) == ref['sha256'] and len(raw) == ref['bytes']; return raw
    def assert_unchanged(self, case):
        for path, before in self.touched.items():
            p = Path(path); raw = p.read_bytes()
            case.assertEqual((digest(raw), len(raw), p.stat().st_mtime_ns), before)


def row(number=1, date='10/14/2026 16:05:00'):
    value = dict.fromkeys(ROW_FIELDS)
    value.update(PressReleaseId=number, WorkflowId=f'00000000-0000-0000-0000-{number:012d}',
                 Headline='Fictional financial announcement ' + str(number), LanguageId=1,
                 PressReleaseDate=date, LinkToDetailPage='/news/news-details/2026/Fictional-' + str(number) + '/default.aspx')
    return value


def encoded(rows): return canonical({'GetPressReleaseListResult': rows})


class PressListTests(unittest.TestCase):
    def parse(self, rows, **kwargs):
        return parse_press_list(encoded(rows), 'jfrog:official:1', AS_OF, **kwargs)
    def test_every_old_record_and_original_unzoned_date_is_retained(self):
        result = self.parse([row(), row(2, '09/02/2026 08:30:00')])
        self.assertEqual(len(result['items']), 2); self.assertEqual(len(result['currentWindowItems']), 1)
        self.assertEqual(result['originalDateStrings'][result['records'][0]['url']], '10/14/2026 16:05:00')
        self.assertEqual(result['records'][0]['calendarDay'], '2026-10-14')
        self.assertIsNone(result['timezone']); self.assertTrue(result['olderBoundaryPresent'])
        self.assertNotIn('qualified', result); self.assertNotIn('facts', result)
    def test_boundary_uncertainty_is_explicit_and_dates_are_not_shifted(self):
        result = self.parse([row(1, '10/25/2026 00:15:00'), row(2, '09/25/2026 23:30:00'), row(3, '09/24/2026 12:00:00')])
        self.assertEqual(len(result['boundaryAmbiguousItems']), 2)
        self.assertEqual([r['calendarDay'] for r in result['records']], ['2026-10-25', '2026-09-25', '2026-09-24'])
        self.assertTrue(all(r['timezone'] is None for r in result['records']))
        next_day = self.parse([row(1, '10/26/2026 00:15:00'), row(2, '09/02/2026 08:30:00')])
        self.assertEqual(len(next_day['undeterminedWindowItems']), 1)
        self.assertEqual(next_day['records'][0]['calendarDay'], '2026-10-26')
        self.assertFalse(next_day['currentWindowQuiet'])
        future = self.parse([row(1, '12/01/2026 00:15:00'), row(2, '09/02/2026 08:30:00')])
        self.assertEqual(len(future['items']), 2); self.assertEqual(len(future['undeterminedWindowItems']), 1)
        self.assertEqual(future['records'][0]['calendarDay'], '2026-12-01')
        self.assertEqual(future['sourceDateAnomalies'][0]['reason'], 'FUTURE_PUBLICATION_CALENDAR_UNRESOLVED')
        self.assertFalse(future['currentWindowQuiet'])
    def test_quiet_requires_recognized_nonempty_older_inventory(self):
        self.assertTrue(self.parse([row(date='09/02/2026 08:30:00')])['currentWindowQuiet'])
        self.assertFalse(self.parse([row()])['currentWindowQuiet'])
        self.assertFalse(self.parse([row()])['olderBoundaryPresent'])
        with self.assertRaises(ValueError): self.parse([])
    def test_exact_envelope_and_json_constants_reject(self):
        for raw in (b'{}', b'[]', b'{', b'{"error":"no"}', b'{"GetPressReleaseListResult":[]}',
                    b'{"GetPressReleaseListResult":[],"TotalRecords":0}', b'{"GetPressReleaseListResult":[],"next":"x"}',
                    b'{"GetPressReleaseListResult":[],"GetPressReleaseListResult":[]}',
                    b'{"GetPressReleaseListResult":NaN}', b'{"GetPressReleaseListResult":Infinity}', b'\xff'):
            with self.subTest(raw=raw), self.assertRaises((ValueError, UnicodeError)):
                parse_press_list(raw, 'jfrog:official:1', AS_OF)
    def test_all_missing_extra_and_nonobject_row_shapes_reject(self):
        changes = [None, {}, 'row', []]
        for key in ROW_FIELDS:
            changed = row(); del changed[key]; changes.append(changed)
        changed = row(); changed['nextPage'] = 'x'; changes.append(changed)
        for changed in changes:
            with self.subTest(row=changed), self.assertRaises((ValueError, TypeError)):
                self.parse([changed])
    def test_ids_language_titles_and_conflicting_duplicates_reject_before_dedup(self):
        for key, value in [('PressReleaseId', True), ('PressReleaseId', -1), ('WorkflowId', 'invalid'),
                           ('LanguageId', True), ('LanguageId', 2), ('Headline', ''), ('Headline', ' leading')]:
            changed = row(); changed[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError): self.parse([changed])
        for key in ('PressReleaseId', 'WorkflowId', 'LinkToDetailPage'):
            changed = row(2); changed[key] = row()[key]
            with self.subTest(key=key), self.assertRaises(ValueError): self.parse([row(), changed])
        with self.assertRaises(ValueError): self.parse([row(), row()])
    def test_unsafe_or_mismatched_detail_links_reject(self):
        original = row()['LinkToDetailPage']
        for href in ('https://evil.example' + original, '//investors.jfrog.com' + original,
                     original + '?x=1', original + '#x', original.replace('/2026/', '/2025/'),
                     original.replace('/news/', '/news/../'), original.replace('Fictional', '%46ictional'),
                     original.replace('Fictional', 'Fictional bad'), '/news/news-details/2026/../default.aspx'):
            changed = row(); changed['LinkToDetailPage'] = href
            with self.subTest(href=href), self.assertRaises(ValueError): self.parse([changed])
    def test_invalid_and_unordered_dates_reject(self):
        for date in ('02/30/2026 00:00:00', '10/14/2026 24:00:00',
                     '2026-10-14', '10/14/2026 16:05:00Z', ' 10/14/2026 16:05:00'):
            with self.subTest(date=date), self.assertRaises(ValueError): self.parse([row(date=date)])
        with self.assertRaises(ValueError): self.parse([row(1, '09/02/2026 00:00:00'), row(2)])
    def test_source_window_and_byte_bounds_are_closed(self):
        for days in (True, 0, 366, 30.0):
            with self.subTest(days=days), self.assertRaises(ValueError): self.parse([row()], window_days=days)
        with self.assertRaises(ValueError): parse_press_list(encoded([row()]), 'rubrik:official:1', AS_OF)
        with self.assertRaises(ValueError): parse_press_list(b'x' * 2_000_001, 'jfrog:official:1', AS_OF)


@unittest.skipUnless((ARCHIVE / 'archive-manifest.json').exists(), 'Requires authenticated actual d660 archive')
class ActualPressListTests(unittest.TestCase):
    def test_all_actual_arrays_keep_206_323_records_and_original_3_4_window(self):
        store = ReadOnlyD660(); self.addCleanup(store.assert_unchanged, self)
        for index, source in enumerate(('jfrog:official:1', 'rapid7:official:1')):
            raw = store.raw('objects/' + BODIES[index]); result = parse_press_list(raw, source, AS_OF)
            self.assertEqual(len(result['records']), (206, 323)[index])
            self.assertEqual(len(result['currentWindowItems']), (3, 4)[index])
            self.assertTrue(result['olderBoundaryPresent']); self.assertEqual(result['boundaryAmbiguousItems'], [])
            self.assertEqual(result['records'][2]['dateLiteral'], '10/14/2026 16:05:00')
            self.assertEqual(len(result['items']), len(result['records']))
            self.assertIsNone(result['timezone'])
    def test_real_arrays_have_no_fixed_count_ceiling_and_later_calendar_can_be_quiet(self):
        store = ReadOnlyD660(); self.addCleanup(store.assert_unchanged, self)
        raw = store.raw('objects/' + BODIES[0]); envelope = json.loads(raw)
        extra = copy.deepcopy(envelope['GetPressReleaseListResult'][-1])
        extra.update(PressReleaseId=999999, WorkflowId='00000000-0000-0000-0000-000000999999',
                     PressReleaseDate='09/01/2019 00:00:00', LinkToDetailPage='/news/news-details/2019/Fictional-older/default.aspx')
        envelope['GetPressReleaseListResult'].append(extra)
        result = parse_press_list(canonical(envelope), 'jfrog:official:1', AS_OF)
        self.assertEqual(len(result['records']), 207)
        self.assertIn('https://investors.jfrog.com/news/news-details/2019/Fictional-older/default.aspx', result['items'])
        # Pure-parser later window is hypothetical; the proof-bound operation keeps its original as-of.
        later = parse_press_list(raw, 'jfrog:official:1', '2026-11-25T12:00:00Z')
        self.assertTrue(later['currentWindowQuiet']); self.assertEqual(len(later['records']), 206)


if __name__ == '__main__': unittest.main()
