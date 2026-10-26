"""Portable Cyera list proof and malformed-list boundaries; no source requests."""
import base64
import copy
import gzip
from html import escape
import json
from pathlib import Path
import sys
import unittest
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'web/scripts/pipeline'), str(ROOT / 'ops/ci')]
from contracts import digest
import cyera_press_list as parser

ACCURACY = ROOT / 'docs/active/daily-pipeline/accuracy'
PLAN = ACCURACY / 'cyera-primary-capture-plan-2026-10-25.json'
AS_OF = '2026-10-25T12:41:43.919481Z'
FIXTURE = ROOT / 'ops/ci/fixtures/cyera-retained-readset.json.gz'
FIXTURE_SHA = 'e210e23e6056a9fbac7707a0faa65b5b0e7055eb6ac574413f81109d0bbe2cdf'


class FixtureStore:
    """Sealed actual read subset only. This is never a runtime source authority."""
    def __init__(self):
        raw = FIXTURE.read_bytes()
        assert digest(raw) == FIXTURE_SHA
        fixture = json.loads(gzip.decompress(raw))
        assert fixture['authority'] == 'test_fixture_only' and fixture['archiveManifestFiles'] == 52273
        self.rows = fixture['consumed']
        self.touched = set()
    def raw(self, key):
        row = self.rows[key]; raw = base64.b64decode(row['base64'], validate=True)
        assert digest(raw) == row['entry']['sha256'] and len(raw) == row['entry']['bytes']
        assert row['entry']['key'] == 'state/' + key
        self.touched.add(key)
        return raw
    def read(self, key): return json.loads(self.raw(key))
    def get(self, ref):
        raw = self.raw(ref['key'])
        assert digest(raw) == ref['sha256'] and len(raw) == ref['bytes']
        return raw


def card(number=1, date='Oct 16, 2026', title=None, href=None):
    cms = quote(json.dumps([{'collectionId': parser.COLLECTION, 'itemId': format(number, '024x')}]), safe='')
    return ('<div role="listitem" class="card_item w-dyn-item"><a class="card_item-link w-inline-block" '
            'data-wf-cms-context="' + cms + '" href="' + (href or '/press-releases/fictional-' + str(number)) + '">'
            '<div class="card_date">' + date + '</div><h3>' + escape(title or 'Fictional release ' + str(number)) + '</h3></a></div>')


def page(cards):
    return ('<html><head><link rel="canonical" href="' + parser.INDEX + '"></head><body><main>'
            '<h1>Cyera press releases</h1><section><div class="card_list-wrapper w-dyn-list">'
            '<div class="card_list w-dyn-items">' + ''.join(cards) + '</div></div></section></main></body></html>').encode()


class ParserTests(unittest.TestCase):
    def parse(self, raw): return parser.parse_press_list(raw, parser.SOURCE, AS_OF)
    def test_all_actual_rows_five_seeds_original_clock_and_csv_match(self):
        plan = json.loads(PLAN.read_bytes()); index = plan['retainedIndex']
        result = parser.parse_press_list(FixtureStore().get(index['body']), parser.SOURCE, AS_OF, 30, index['knownSeedUrls'])
        self.assertEqual(len(result['records']), 56); self.assertEqual(len(result['knownSeedMembership']), 5)
        self.assertEqual([r['calendarDay'] for r in result['records'][:2]], ['2026-10-16', '2026-09-22'])
        self.assertEqual((result['windowStart'], result['windowEnd']), ('2026-09-25', '2026-10-25'))
        self.assertEqual(len(result['currentWindowItems']), 1); self.assertEqual(len(result['historicalItems']), 55)
        for key in ('recordsSha256', 'itemsSha256', 'knownSeedMembershipSha256'): self.assertEqual(result[key], index[key])
        self.assertEqual(parser.inventory_csv(result), (ACCURACY / index['inventoryCsv']['filename']).read_bytes())
        self.assertTrue(result['dailyWindowComplete'])
    def test_equal_dates_and_more_than_56_cards_are_valid(self):
        result = self.parse(page([card(n) for n in range(1, 60)] + [card(60, 'Sep 22, 2026')]))
        self.assertEqual(len(result['records']), 60); self.assertEqual(len(result['currentWindowItems']), 59)
    def test_future_and_boundary_day_are_explicit_and_cannot_prove_quiet(self):
        for date in ('Oct 26, 2026', 'Sep 25, 2026', 'Oct 25, 2026'):
            result = self.parse(page([card(1, date), card(2, 'Sep 22, 2026')]))
            self.assertFalse(result['dailyWindowComplete']); self.assertFalse(result['currentWindowQuiet'])
            self.assertTrue(result['undeterminedWindowItems'] or result['boundaryAmbiguousItems'])
    def test_urls_attributes_card_ids_inert_structure_and_dates_fail_closed(self):
        raw = page([card(), card(2, 'Sep 22, 2026')]).decode()
        changes = [lambda s:s.replace('href="/press-releases/fictional-1"', 'href="//evil.test/press-releases/a"'),
                   lambda s:s.replace('/press-releases/fictional-1', '/press-releases/fictional-1?q=1'),
                   lambda s:s.replace('/press-releases/fictional-1', '/press-releases/fictional-1#x'),
                   lambda s:s.replace('Oct 16, 2026', 'Feb 31, 2026'), lambda s:s.replace('Oct 16, 2026', ''),
                   lambda s:s.replace('Sep 22, 2026', 'Oct 17, 2026'),
                   lambda s:s.replace('class="card_date"', 'hidden class="card_date"', 1),
                   lambda s:s.replace('<h3>', '<template><h3>', 1).replace('</h3>', '</h3></template>', 1),
                   lambda s:s.replace('<h3>', '<h3><span>', 1),
                   lambda s:s.replace('<h3>', '<h3/>', 1), lambda s:s.replace('</h3>', '', 1),
                   lambda s:s.replace('<h1>', '<h1 hidden>'), lambda s:s.replace('</head>', '<base href="https://evil.test"></head>'),
                   lambda s:s.replace('class="card_item-link w-inline-block"', 'class="card_item-link w-inline-block" href="bad"', 1),
                   lambda s:s.replace('</section>', '<div class="w-pagination-wrapper"></div></section>'),
                   lambda s:s.replace('class="card_list w-dyn-items"', 'class="card_list w-dyn-items" fs-cmsload-element="list"'),
                   lambda s:s.replace('card_list-wrapper w-dyn-list', 'card_list-wrapper w-dyn-list" style="display:none'),
                   lambda s:s.replace('/press-releases/fictional-2', '/press-releases/fictional-1'),
                   lambda s:s.replace('000000000000000000000002', '000000000000000000000001'),
                   lambda s:s.replace(parser.COLLECTION, 'a'*24),
                   lambda s:s.replace('</main>', card(3) + '</main>')]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError): self.parse(change(raw).encode())
    def test_wrong_source_window_bytes_and_hidden_duplicate_headings_reject(self):
        raw = page([card()])
        for source, time, window in [('other', AS_OF, 30), (parser.SOURCE, AS_OF, True)]:
            with self.assertRaises(ValueError): parser.parse_press_list(raw, source, time, window)
        for body in (b'', b'\xff', raw.replace(b'</main>', b'<h1 hidden>Cyera press releases</h1></main>')):
            with self.assertRaises(ValueError): self.parse(body)


if __name__ == '__main__': unittest.main()
