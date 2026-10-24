"""Fictional pagination fixtures; optional authenticated bodies supply layout evidence only."""
from datetime import date, timedelta
import gzip
import hashlib
import json
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from contracts import validate_contract
from discovery import (DELINEA_HTML_MODE, DELINEA_INDEX, SONATYPE_HTML_MODE, SONATYPE_INDEX,
                       discover, html_index_number, parse_source_html_index)

NOW = '2026-10-24T06:30:00Z'
OLD_BUNDLE = Path('/var/tmp/smp-followup-probe-20261024/target-bundle')
NEW_BUNDLE = Path('/var/tmp/smp-pagination-probe-20261024/target-bundle')


def source(supplier):
    return {'id': supplier + ':official:1', 'supplierId': supplier, 'family': 'official_announcements',
            'registration': 'verified', 'kind': 'html_index', 'required': True, 'maxPages': 60,
            'url': DELINEA_INDEX if supplier == 'delinea' else SONATYPE_INDEX,
            'allowedHosts': ['delinea.com' if supplier == 'delinea' else 'www.sonatype.com'],
            'htmlCompleteness': DELINEA_HTML_MODE if supplier == 'delinea' else SONATYPE_HTML_MODE}


def delinea_url(page):
    return DELINEA_INDEX if page == 1 else DELINEA_INDEX + '/page/' + str(page)


def delinea_page(page=1, next_page=True):
    cards = ''.join(f'<article class="blog-index__post blog-index__post--small">'
                    f'<a class="blog-index__post-image-wrapper" href="{DELINEA_INDEX}/fixture-{page}-{i}">Image</a>'
                    f'<h2 class="blog-index__post-title"><a class="blog-index__post-title-link" '
                    f'href="{DELINEA_INDEX}/fixture-{page}-{i}">Fixture title</a></h2></article>' for i in range(12))
    window = range(max(1, page - 2), max(1, page - 2) + 5)
    nums = ''.join(f'<a class="blog-pagination__link blog-pagination__number-link'
                   + (' blog-pagination__link--active" aria-current="true"' if n == page else '"')
                   + f' href="{delinea_url(n)}">{n}</a>' for n in window)
    prev = ('class="blog-pagination__link blog-pagination__prev-link blog-pagination__prev-link--disabled"'
            if page == 1 else f'class="blog-pagination__link blog-pagination__prev-link" href="{delinea_url(page-1)}"')
    head_prev = '' if page == 1 else f'<link rel="prev" href="{DELINEA_INDEX}/page/{page-1}">'
    head_next = f'<link rel="next" href="{delinea_url(page+1)}">' if next_page else ''
    next_control = f'<a class="blog-pagination__link blog-pagination__next-link" href="{delinea_url(page+1)}">Next</a>' if next_page else ''
    return (f'<html><head><link rel="canonical" href="{DELINEA_INDEX}">{head_prev}{head_next}</head>'
            f'<body><a href="https://evil.invalid/footer">Not an article</a><section class="blog-index">{cards}</section>'
            f'<nav class="blog-pagination" role="navigation" aria-label="Pagination"><a {prev}>Prev</a>{nums}{next_control}</nav></body></html>').encode()


def sonatype_url(page):
    return SONATYPE_INDEX if page == 1 else SONATYPE_INDEX + '?page=' + str(page)


def sonatype_page(page=1, last=13, terminal=None):
    terminal = page == last if terminal is None else terminal
    size = 13 if terminal else 16
    cards = []
    for i in range(size):
        day = date(2026, 10, 23) - timedelta(days=(page - 1) * 16 + i)
        stamp = day.strftime('%B ') + str(day.day) + day.strftime(', %Y')
        cards.append(f'<div class="listing__grid-card"><div class="card-content"><div class="card-content__meta"><p>{stamp}</p></div>'
                     f'<h3>Fixture title</h3><p>Fixture synopsis</p></div><a class="btn pr_link" '
                     f'href="{SONATYPE_INDEX}/fixture-{page}-{i}">Read More</a></div>')
    numbers = sorted({1, max(1, page - 1), page, min(last, page + 1), last})
    controls = ''
    for i, n in enumerate(numbers):
        if i and n > numbers[i-1] + 1:
            controls += '<li>...</li>'
        controls += '<li><a class="pagination-link' + (' current-page' if n == page else '') + f'" href="/press-releases?page={n}">{n}</a></li>'
    return (f'<html><head><link rel="canonical" href="{SONATYPE_INDEX}"></head><body>'
            f'<div class="listing__grid">{"".join(cards)}</div><div class="pagination">'
            f'<div class="pagination-btn previous d-inline-block mx-2 mx-md-3{" hide" if page == 1 else ""}">'
            f'<a class="btn btn-secondary" href="/press-releases?page={page-1}#resource-grid">Prev</a></div><ul class="pages ps-0 mb-0">{controls}</ul>'
            f'<div class="pagination-btn next d-inline-block mx-2 mx-md-3{" hide" if terminal else ""}">'
            f'<a class="btn btn-secondary" href="/press-releases?page={page+1}">Next</a></div></div></body></html>').encode()


def replay(supplier, pages, **changes):
    calls = []
    def request(url):
        calls.append(url)
        if url not in pages:
            raise OSError('fictional page absent')
        return {'status': 'fetched', 'requestedUrl': url, 'finalUrl': url, 'fetchedAt': NOW}, pages[url]
    with patch.object(socket.socket, 'connect', side_effect=AssertionError('network forbidden')):
        return discover({**source(supplier), **changes}, request), calls


class HtmlArchiveDiscoveryTests(unittest.TestCase):
    def parse(self, supplier, body, page=1, highest=1):
        return parse_source_html_index(source(supplier), delinea_url(page) if supplier == 'delinea' else sonatype_url(page), body, highest, NOW)

    def test_delinea_cards_are_unique_and_dates_remain_unknown(self):
        parsed = self.parse('delinea', delinea_page())
        self.assertEqual(len(parsed['items']), 12)
        self.assertEqual(parsed['dates'], {})
        self.assertEqual(parsed['next'], delinea_url(2))
        self.assertEqual(parsed['highestPage'], 5)
        self.assertFalse(parsed['terminalProved'])

    def test_delinea_window_moves_beyond_five_and_head_previous_alias_is_not_queued(self):
        parsed = self.parse('delinea', delinea_page(5), page=5, highest=5)
        self.assertEqual(parsed['highestPage'], 7)
        self.assertEqual(parsed['next'], delinea_url(6))
        found, calls = replay('delinea', {DELINEA_INDEX: delinea_page(), delinea_url(2): delinea_page(2)})
        self.assertEqual(calls, [DELINEA_INDEX, delinea_url(2), delinea_url(3)])
        self.assertEqual(len(found['items']), 24)
        self.assertEqual(found['reason'], 'DELINEA_INDEX_REQUEST_FAILED')

    def test_delinea_missing_next_is_unproved_terminal_with_retained_items(self):
        found, _ = replay('delinea', {DELINEA_INDEX: delinea_page(next_page=False)})
        self.assertFalse(found['complete'])
        self.assertEqual(found['reason'], 'DELINEA_TERMINAL_LAYOUT_UNPROVED')
        self.assertEqual(len(found['items']), 12)

    def test_delinea_conflicting_head_controls_and_metadata_hold(self):
        original = delinea_page().decode()
        for old, new in [('<link rel="next" href="https://delinea.com/news/page/2">', '<link rel="next" href="https://delinea.com/news/page/3">'),
                         ('aria-current="true"', 'aria-current="page"'),
                         ('blog-index__post-title-link', 'wrong-title-link'),
                         ('href="https://delinea.com/news/fixture-1-0">Image', 'href="https://delinea.com/news/other">Image'),
                         ('blog-pagination__prev-link--disabled', 'unknown-control')]:
            with self.subTest(old=old), self.assertRaises(ValueError):
                self.parse('delinea', original.replace(old, new, 1).encode())

    def test_sonatype_dates_are_scheduling_hints_and_hidden_previous_is_never_requested(self):
        parsed = self.parse('sonatype', sonatype_page())
        self.assertEqual(len(parsed['items']), 16)
        self.assertEqual(parsed['firstDate'], '2026-10-23')
        found, calls = replay('sonatype', {SONATYPE_INDEX: sonatype_page()})
        self.assertEqual(calls, [SONATYPE_INDEX, sonatype_url(2)])
        self.assertEqual(found['reason'], 'SONATYPE_INDEX_REQUEST_FAILED')
        self.assertEqual(found['itemDates'], found['itemModified'])

    def test_sonatype_future_card_check_uses_utc_day_for_offset_timestamps(self):
        s=source('sonatype')
        self.assertEqual(len(parse_source_html_index(s,SONATYPE_INDEX,sonatype_page(),1,'2026-10-22T23:30:00-07:00')['items']),16)
        with self.assertRaisesRegex(ValueError,'Future date'):
            parse_source_html_index(s,SONATYPE_INDEX,sonatype_page(),1,'2026-10-23T00:30:00+14:00')

    def test_sonatype_terminal_requires_exact_hidden_next_and_highest_page(self):
        parsed = self.parse('sonatype', sonatype_page(13), page=13, highest=13)
        self.assertTrue(parsed['terminalProved'])
        self.assertIsNone(parsed['next'])
        self.assertEqual(len(parsed['items']), 13)
        with self.assertRaises(ValueError):
            self.parse('sonatype', sonatype_page(13), page=13, highest=14)
        with self.assertRaises(ValueError):
            self.parse('sonatype', sonatype_page(1, terminal=True))

    def test_sonatype_full_synthetic_traversal_is_complete_but_no_fact_review_occurs(self):
        pages = {sonatype_url(n): sonatype_page(n) for n in range(1, 14)}
        found, calls = replay('sonatype', pages)
        self.assertTrue(found['complete'])
        self.assertEqual(len(calls), 13)
        self.assertEqual(len(found['items']), 205)  # Fictional fixture inventory only.
        self.assertNotIn('facts', found)
        self.assertNotIn('newFactIds', found)

    def test_sonatype_missing_middle_page_never_jumps_to_known_terminal(self):
        found, calls = replay('sonatype', {SONATYPE_INDEX: sonatype_page(), sonatype_url(13): sonatype_page(13)})
        self.assertFalse(found['complete'])
        self.assertEqual(calls, [SONATYPE_INDEX, sonatype_url(2)])
        self.assertEqual(len(found['items']), 16)

    def test_sonatype_missing_next_and_date_conflicts_hold(self):
        original = sonatype_page().decode()
        no_next = original[:original.index('<div class="pagination-btn next')] + '</div></body></html>'
        found, _ = replay('sonatype', {SONATYPE_INDEX: no_next.encode()})
        self.assertEqual(found['reason'], 'SONATYPE_TERMINAL_LAYOUT_UNPROVED')
        for old, new in [('October 23, 2026', 'October 32, 2026'), ('October 23, 2026', 'October 23, 2099'),
                         ('October 23, 2026', '2026-10-23'), ('page=0#resource-grid', 'page=1#resource-grid'),
                         ('href="/press-releases?page=2">Next', 'href="/press-releases?page=3">Next')]:
            with self.subTest(old=old), self.assertRaises(ValueError):
                self.parse('sonatype', original.replace(old, new, 1).encode())

    def test_duplicate_cards_and_cross_page_date_order_hold(self):
        for supplier, body, base in [('delinea', delinea_page(), DELINEA_INDEX), ('sonatype', sonatype_page(), SONATYPE_INDEX)]:
            duplicate = body.replace((base + '/fixture-1-1').encode(), (base + '/fixture-1-0').encode())
            with self.subTest(supplier=supplier), self.assertRaises(ValueError):
                self.parse(supplier, duplicate)
        second = sonatype_page(2).replace(b'October 7, 2026', b'October 24, 2026')
        found, _ = replay('sonatype', {SONATYPE_INDEX: sonatype_page(), sonatype_url(2): second})
        self.assertFalse(found['complete'])
        self.assertEqual(found['reason'], 'SONATYPE_INDEX_INCOMPLETE')
        self.assertEqual(len(found['items']), 16)

    def test_index_response_redirect_and_foreign_head_next_are_not_followed(self):
        for supplier, body in [('delinea', delinea_page()), ('sonatype', sonatype_page())]:
            s = source(supplier); calls = []
            def wrong(url):
                calls.append(url)
                return {'status': 'fetched', 'requestedUrl': url, 'finalUrl': url + '/redirected', 'fetchedAt': NOW}, body
            found = discover(s, wrong)
            self.assertFalse(found['complete'])
            self.assertEqual(calls, [s['url']])
            self.assertEqual(found['items'], [])
        body = delinea_page().replace(b'<link rel="next" href="https://delinea.com/news/page/2">',
                                      b'<link rel="next" href="https://evil.invalid/news/page/2">')
        found, calls = replay('delinea', {DELINEA_INDEX: body})
        self.assertFalse(found['complete'])
        self.assertEqual(calls, [DELINEA_INDEX])

    def test_terminal_next_query_and_advertised_gap_tampering_hold(self):
        body = sonatype_page(13)
        for old, new in [(b'page=14">Next', b'page=15">Next'),
                         (b'<li>...</li>', b'<li>ignored</li>'),
                         (b'next d-inline-block mx-2 mx-md-3 hide', b'next d-inline-block mx-2 mx-md-3')]:
            with self.subTest(old=old), self.assertRaises(ValueError):
                self.parse('sonatype', body.replace(old, new, 1), page=13, highest=13)

    def test_unscoped_pagination_and_canonical_outside_head_hold(self):
        for supplier, body, base in [('delinea', delinea_page(), DELINEA_INDEX), ('sonatype', sonatype_page(), SONATYPE_INDEX)]:
            canonical = f'<link rel="canonical" href="{base}">'.encode()
            outside = body.replace(canonical, b'', 1).replace(b'</body>', canonical + b'</body>')
            with self.subTest(supplier=supplier), self.assertRaises(ValueError):
                self.parse(supplier, outside)
        outside = delinea_page().replace(b'</body>', b'<a class="blog-pagination__next-link" href="https://delinea.com/news/page/9">Next</a></body>')
        with self.assertRaises(ValueError):
            self.parse('delinea', outside)

    def test_foreign_encoded_normalized_and_query_article_paths_hold(self):
        for supplier, body, original in [('delinea', delinea_page(), DELINEA_INDEX + '/fixture-1-0'),
                                         ('sonatype', sonatype_page(), SONATYPE_INDEX + '/fixture-1-0')]:
            for path in ('https://evil.invalid/news/one', original + '?x=1', original + '#fragment',
                         original.replace('fixture', '%66ixture'), original.replace('/fixture', '/../news/fixture'),
                         original.replace('fixture', 'fix\tture'), original.replace('fixture', 'fix\\ture')):
                with self.subTest(supplier=supplier, path=path), self.assertRaises(ValueError):
                    self.parse(supplier, body.replace(original.encode(), path.encode(), 1))

    def test_strict_index_url_grammar(self):
        for mode, root in [(DELINEA_HTML_MODE, DELINEA_INDEX), (SONATYPE_HTML_MODE, SONATYPE_INDEX)]:
            for url in (root + '#resource-grid', root + '?page=0', root.replace('https:', 'http:'),
                        root.replace('https://', 'https://user@'), root + '\n', root + '?page=2&x=1'):
                with self.subTest(url=url), self.assertRaises(ValueError):
                    html_index_number(url, mode)
        with self.assertRaises(ValueError):
            html_index_number(DELINEA_INDEX + '/page/1', DELINEA_HTML_MODE)

    def test_caps_partial_inventory_and_gzip_preserve_original_body(self):
        for supplier, root, body in [('delinea', DELINEA_INDEX, delinea_page()), ('sonatype', SONATYPE_INDEX, sonatype_page())]:
            raw = gzip.compress(body)
            found, calls = replay(supplier, {root: raw}, maxPages=1)
            self.assertEqual(found['reason'], 'PAGINATION_BUDGET_EXHAUSTED')
            self.assertEqual(calls, [root])
            self.assertEqual(gzip.decompress(raw), body)
            self.assertTrue(found['items'])

    def test_exact_bindings_candidate_gate_and_contract_bounds(self):
        for supplier, body in [('delinea', delinea_page()), ('sonatype', sonatype_page())]:
            s = source(supplier)
            for key, value in [('id', 'other'), ('supplierId', 'other'), ('allowedHosts', ['evil.invalid']),
                               ('family', 'investor_acquirer'), ('url', s['url'] + '/'), ('maxPages', 61), ('maxPages', True)]:
                with self.subTest(supplier=supplier, key=key), self.assertRaises(ValueError):
                    parse_source_html_index({**s, key: value}, s['url'], body, 1, NOW)
            found, calls = replay(supplier, {}, registration='candidate')
            self.assertEqual(found['reason'], 'SOURCE_BINDING_UNVERIFIED')
            self.assertEqual(calls, [])
            contract = json.loads((ROOT / 'contracts/market.json').read_text())
            registered = next(x for x in contract['sources'] if x['id'] == s['id'])
            registered.update(s)
            validate_contract(contract)
            registered['maxPages'] = 61
            with self.assertRaises(ValueError):
                validate_contract(contract)

    @unittest.skipUnless(OLD_BUNDLE.exists() and NEW_BUNDLE.exists(), 'authenticated response bundles are local replay inputs')
    def test_actual_roots_pages_and_terminal_are_layout_evidence_not_traversal(self):
        old = json.loads((OLD_BUNDLE / 'receipt.json').read_text())['targets']
        new = json.loads((NEW_BUNDLE / 'receipt.json').read_text())['diagnostic']['qualification']['targets']
        for bundle, rows in [(OLD_BUNDLE, old), (NEW_BUNDLE, new)]:
            for row in rows:
                target_id = row.get('targetId', row.get('id'))
                if not target_id.startswith(('delinea-news-', 'sonatype-press-')):
                    continue
                raw = (bundle / (target_id + '.observation.json')).read_bytes()
                observed = json.loads(raw)
                body = (bundle / (target_id + '.body')).read_bytes()
                self.assertEqual(hashlib.sha256(body).hexdigest(), observed['body']['sha256'])
                self.assertEqual(len(body), observed['body']['bytes'])
                supplier = 'delinea' if target_id.startswith('delinea') else 'sonatype'
                parsed = parse_source_html_index(source(supplier), observed['requestedUrl'], body, 1, observed['fetchedAt'])
                self.assertEqual(parsed['terminalProved'], target_id == 'sonatype-press-page-13')
                self.assertEqual(len(parsed['items']), 13 if target_id == 'sonatype-press-page-13' else 12 if supplier == 'delinea' else 16)
                if supplier == 'delinea':
                    self.assertEqual(parsed['dates'], {})
                self.assertEqual((bundle / (target_id + '.body')).read_bytes(), body)


if __name__ == '__main__':
    unittest.main()
