"""Offline recognized publisher-list parsing; fictional mutations earn no credit."""
import copy
from html import escape
import json
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "web/scripts/pipeline"), str(ROOT / "ops/ci")]
from contracts import digest
from storage import LocalStore
import prnewswire_press_list as parser

ARCHIVE = Path("/var/tmp/smp-listing-pagination-actual-40193925490-20261025/extracted")
ACCURACY = ROOT / "docs/active/daily-pipeline/accuracy"
AS_OF = "2026-10-25T12:42:16.956348Z"
SID = "cato:official:1"


class ReadOnlyActual:
    def __init__(self):
        raw = (ARCHIVE / "archive-manifest.json").read_bytes()
        assert digest(raw) == "148842177a7e7d9a5fd5c2ea4574576264a957b41958ee4cdf5effa80ea029c2"
        self.entries = {r["key"]: r for r in json.loads(raw)["files"]}
        self.touched = {}
    def raw(self, key):
        assert key in self.entries or "state/" + key in self.entries
        relative = key if key in self.entries else "state/" + key
        path, row = ARCHIVE / relative, self.entries[relative]
        assert not path.is_symlink() and path.resolve().is_relative_to(ARCHIVE)
        raw = path.read_bytes()
        assert digest(raw) == row["sha256"] and len(raw) == row["bytes"]
        self.touched[str(path)] = (digest(raw), len(raw), path.stat().st_mtime_ns)
        return raw
    def read(self, key):
        return json.loads(self.raw(key))
    def get(self, ref):
        raw = self.raw(ref["key"])
        assert digest(raw) == ref["sha256"] and len(raw) == ref["bytes"]
        return raw
    def unchanged(self, case):
        for name, before in self.touched.items():
            path = Path(name); raw = path.read_bytes()
            case.assertEqual((digest(raw), len(raw), path.stat().st_mtime_ns), before)


def card(number, date="Oct 07, 2026, 08:30 ET", language="en-US", href=None):
    href = href or "/news-releases/fictional-" + str(number) + ".html"
    small = "<small>" + escape(date) + "</small>" if date is not None else ""
    return ('<div class="row newsCards" lang="' + language + '"><div class="card col-view" role="group" '
            'aria-label="News Release"><a class="newsreleaseconsolidatelink display-outline w-100" href="' + href +
            '"><h3>' + small + 'Fictional Cato Networks release ' + str(number) + '</h3><p>Issuer release</p></a></div></div>')


def page(cards, number=1, terminal=True, source_id=SID):
    root = parser.index_url(source_id)
    def link(n): return '?page=' + str(n) + '&amp;pagesize=25'
    previous = ('<li class="disabled"><a aria-label="Previous"><span aria-hidden="true">«</span></a></li>' if number == 1 else
                '<li><a aria-label="Previous" href="' + link(number - 1) + '"><span aria-hidden="true">«</span></a></li>')
    numbered = ''.join('<li' + (' class="active"' if n == number else '') + '><a' +
                       ('' if n == number else ' href="' + link(n) + '"') + '>' + str(n) + '</a></li>'
                       for n in range(1, max(number, 2 if not terminal else number) + 1))
    following = ('<li class="disabled"><a aria-label="Next"><span aria-hidden="true">»</span></a></li>' if terminal else
                 '<li><a aria-label="Next" href="' + link(number + 1) + '"><span aria-hidden="true">»</span></a></li>')
    metadata = ('<link rel="prev" href="' + root + ('?page=' + str(number - 1) if number > 2 else '') + '">' if number > 1 else '')
    metadata += '<link rel="next" href="' + root + '?page=' + str(number + 1) + '">' if not terminal else ''
    canonical = root + ('?page=' + str(number) if number > 1 else '')
    return ('<html><head><link rel="canonical" href="' + canonical + '">' + metadata + '</head><body>'
        '<main id="main" class="headline-listing" role="main" tabindex="-1"><section class="container"><h1>News from ' +
        parser.SOURCES[source_id][1] + '<small>Publisher boilerplate</small></h1></section><section class="container">'
        '<div class="row"><div class="col-md-8 col-sm-12"><div class="card-list card-list-hr nativo-section">'
        '<h2 class="section-header">Latest<small></small></h2>' + ''.join(cards) + '</div></div></div></section>'
        '<section class="container"><div class="row"><div class="col-sm-12"><div class="toolbar-container">'
        '<div class="pagination-bar"><div class="page-list pull-right"><nav aria-label="pagination"><ul class="pagination">' +
        previous + numbered + following + '</ul></nav></div></div></div></div></div></section></main></body></html>').encode()


class PressListTests(unittest.TestCase):
    def parse(self, raw, **kwargs):
        return parser.parse_page(kwargs.get("source_id", SID), kwargs.get("url", parser.index_url(SID)), raw, AS_OF)
    def stream(self, raw):
        return parser.derive_stream(SID, [{"url": parser.index_url(SID), "body": raw}], AS_OF)
    def test_equal_dates_and_timestamps_preserve_distinct_urls_and_titles(self):
        result = self.stream(page([card(1), card(2), card(3, "Sep 24, 2026, 09:00 ET")]))
        self.assertEqual(len(result["records"]), 3)
        self.assertEqual(len(result["currentWindowItems"]), 2)
        self.assertEqual(len({r["title"] for r in result["records"]}), 3)
        self.assertTrue(result["dailyWindowComplete"])
        self.assertFalse(result["qualified"])
    def test_equal_dates_across_connected_pages_are_legal(self):
        p1 = page([card(n) for n in range(25)], terminal=False)
        p2 = page([card(25), card(26, "Sep 24, 2026, 09:00 ET")], number=2)
        result = parser.derive_stream(SID, [{"url": parser.index_url(SID), "body": p1},
            {"url": parser.index_url(SID, 2), "body": p2}], AS_OF)
        self.assertEqual(len(result["currentWindowItems"]), 26)
        self.assertTrue(result["historicalEnumerationComplete"])
    def test_calendar_boundaries_and_all_future_rows_remain_explicit(self):
        result = self.stream(page([card(1, "Dec 01, 2026, 09:00 ET"), card(2, "Oct 26, 2026, 00:01 ET"),
            card(3, "Oct 25, 2026, 00:01 ET"), card(4, "Sep 25, 2026, 23:59 ET"), card(5, "Sep 24, 2026, 09:00 ET")]))
        self.assertEqual(len(result["currentWindowItems"]), 2)
        self.assertEqual(len(result["undeterminedWindowItems"]), 2)
        self.assertEqual(len(result["boundaryAmbiguousItems"]), 3)
        self.assertEqual(len(result["sourceDateAnomalies"]), 1)
        self.assertFalse(result["currentWindowQuiet"])
        self.assertTrue(all(r["timezone"] is None for r in result["records"]))
    def test_unknown_and_missing_dates_never_drop_urls_or_create_quiet(self):
        for date in (None, "", "Unknown", "Sep 24, 2026", "Sep 24, 2026, 09:00 UTC"):
            with self.subTest(date=date):
                result = self.stream(page([card(1, date), card(2, "Sep 24, 2026, 09:00 ET")]))
                self.assertEqual(len(result["records"]), 2)
                self.assertEqual(len(result["unresolvedDateItems"]), 1)
                self.assertFalse(result["dailyWindowComplete"])
                self.assertFalse(result["currentWindowQuiet"])
    def test_impossible_calendar_and_increasing_dates_reject(self):
        for date in ("Feb 30, 2026, 09:00 ET", "Oct 07, 2026, 24:00 ET"):
            with self.subTest(date=date), self.assertRaises(ValueError): self.parse(page([card(1, date)]))
        with self.assertRaises(ValueError): self.parse(page([card(1, "Sep 24, 2026, 09:00 ET"), card(2)]))
    def test_duplicates_with_same_or_conflicting_dates_reject(self):
        for date in ("Oct 07, 2026, 08:30 ET", "Oct 06, 2026, 08:30 ET"):
            with self.subTest(date=date), self.assertRaises(ValueError): self.parse(page([card(1), card(1, date)]))
    def test_unsafe_source_transport_and_metadata_urls_reject(self):
        root = parser.index_url(SID)
        for url in (root+'?page=1&pagesize=25', root+'?page=2', root+'?pagesize=25&page=2', root+'#x',
                    root.replace('www.', ''), root.replace('https:', 'http:'), root.replace('cato-networks', 'chainguard')):
            with self.subTest(url=url), self.assertRaises(ValueError): self.parse(page([card(1)]), url=url)
        for href in ('https://evil.example/news-releases/x.html', '//evil.example/x', '/news-releases/../x.html',
                     '/news-releases/x.html?x=1', '/news-releases/%78.html', '/il/news-releases/x.html'):
            with self.subTest(href=href), self.assertRaises(ValueError): self.parse(page([card(1, href=href)]))
        with self.assertRaises(ValueError): self.parse(page([card(1)]), source_id='cyera:official:1')
    def test_all_unrecognized_structure_hidden_decoys_and_attribute_ambiguity_reject(self):
        raw = page([card(1)])
        mutations = [raw.replace(b'News from Cato Networks', b'News from Chainguard'),
            raw.replace(b'>Latest<', b'>Oldest<'), raw.replace(b'role="group"', b'role="group" hidden'),
            raw.replace(b'<h3>', b'<h3 aria-hidden="true">'), raw.replace(b'<h3>', b'<h3 style="display:none">'),
            raw.replace(b'lang="en-US"', b'lang="xx"'), raw.replace(b'class="card col-view"', b'class="card other"'),
            raw.replace(b'<h3>', b'<h3><span>decoy</span>'), raw.replace(b'<h3>', b'<h3><small>Oct 07, 2026, 08:30 ET</small>'),
            raw.replace(b'<main ', b'<template/><main '), raw.replace(b'<main ', b'<base href="https://evil.example"><main '),
            raw.replace(b'role="group"', b'role="group" role="other"'),
            raw.replace(b'</body>', (card(2)).encode()+b'</body>'),
            raw.replace(b'<h3>', b'<template><h3>').replace(b'</h3>', b'</h3></template>'),
            raw.replace(b'<h3>', b'<h3/><h3>')]
        for changed in mutations:
            with self.subTest(mutation=changed[:50]), self.assertRaises(ValueError): self.parse(changed)
    def test_pager_active_terminal_unknown_controls_and_head_conflicts_reject(self):
        raw = page([card(1)])
        changes = [raw.replace(b'class="active"><a>1', b'class="active"><a>2'),
            raw.replace(b'aria-label="Next"', b'aria-label="Next" href="?page=2&amp;pagesize=25"'),
            raw.replace(b'</ul>', b'<button>More</button></ul>'),
            raw.replace(b'</head>', b'<link rel="next" href="https://www.prnewswire.com/news/cato-networks/?page=2"></head>'),
            raw.replace(b'<nav aria-label="pagination">', b'<nav aria-label="other">')]
        for changed in changes:
            with self.subTest(changed=changed[:40]), self.assertRaises(ValueError): self.parse(changed)
    def test_metadata_only_page_urls_are_separate_and_conflicts_reject(self):
        raw=page([card(n) for n in range(25)],terminal=False)
        result=self.parse(raw)
        metadata=parser.index_url(SID)+'?page=2'
        self.assertEqual(result['headPaginationMetadata']['next'],metadata)
        self.assertNotIn(metadata,result['literalPaginationUrls'])
        self.assertEqual(result['next'],parser.index_url(SID,2))
        for changed in (raw.replace(metadata.encode(),(parser.index_url(SID)+'?page=3').encode()),
                        raw.replace(metadata.encode(),parser.index_url(SID,2).encode()),
                        raw.replace(b'<ul class="pagination">',b'<ul class="pagination">unexpected')):
            with self.subTest(sha=digest(changed)),self.assertRaises(ValueError):self.parse(changed)
        with self.assertRaises(ValueError):parser.page_number(SID,metadata)

    def test_prefix_stop_never_claims_older_history_complete(self):
        raw = page([card(n, "Sep 24, 2026, 09:00 ET") for n in range(25)], terminal=False)
        result = self.stream(raw)
        self.assertTrue(result["dailyWindowComplete"])
        self.assertTrue(result["currentWindowQuiet"])
        self.assertFalse(result["historicalEnumerationComplete"])
        self.assertTrue(result["unknownOlderHistory"])
        self.assertEqual(result["pendingLiteralPaginationUrls"], [parser.index_url(SID, 2)])
    def test_cross_page_increasing_duplicate_and_gap_reject(self):
        first = {"url": parser.index_url(SID), "body": page([card(n) for n in range(25)], terminal=False)}
        for second in (page([card(30, "Oct 08, 2026, 09:00 ET")], number=2), page([card(1)], number=2)):
            with self.subTest(second=second[:40]), self.assertRaises(ValueError):
                parser.derive_stream(SID, [first, {"url": parser.index_url(SID, 2), "body": second}], AS_OF)
        with self.assertRaises(ValueError): parser.derive_stream(SID, [first, {"url": parser.index_url(SID, 3), "body": first['body']}], AS_OF)
    def test_input_size_and_schema_bounds_reject(self):
        for raw in (b'', b'x'*2_000_001, b'\xff'):
            with self.subTest(raw=raw[:10]), self.assertRaises((ValueError, UnicodeError)): self.parse(raw)
        with self.assertRaises(ValueError): parser.derive_stream(SID, [], AS_OF)
        with self.assertRaises(ValueError): parser.derive_stream(SID, [{'url':parser.index_url(SID),'body':page([card(1)]),'extra':1}], AS_OF)


@unittest.skipUnless((ARCHIVE / "archive-manifest.json").exists(), "Requires authenticated retained 9e4a archive")
class ActualPressListTests(unittest.TestCase):
    def test_actual_all_cards_locale_paths_and_separate_completion(self):
        store = ReadOnlyActual(); self.addCleanup(store.unchanged, self)
        fixture = json.loads((ACCURACY / 'receipts/narrow-listing-pagination-actual-2026-10-25/listing-card-pagination-inspection.json').read_bytes())
        with patch.object(socket.socket, 'connect', side_effect=AssertionError('NO_NETWORK')), patch.object(LocalStore, '__init__', side_effect=AssertionError('NO_FROZEN_STORE')):
            for sid, count, current, terminal in ((SID,125,2,False),('chainguard:official:1',47,5,True)):
                result = parser.derive_stream(sid, [{'url':p['requestedUrl'],'body':store.get(p['body'])} for p in fixture['pages'] if p['sourceId']==sid], AS_OF)
                self.assertEqual(result['items'], fixture['groups'][sid]['inventoryUrls'])
                self.assertEqual(len(result['records']), count); self.assertEqual(len(result['currentWindowItems']), current)
                self.assertTrue(result['dailyWindowComplete']); self.assertEqual(result['historicalEnumerationComplete'],terminal)
                self.assertEqual(result['unresolvedDateItems'],[])
                self.assertTrue(any(row['language']!='en-US' for row in result['records']))
                if sid==SID:self.assertEqual(result['pendingLiteralPaginationUrls'],[parser.index_url(SID,n) for n in (6,7,8)])


if __name__ == '__main__': unittest.main()
