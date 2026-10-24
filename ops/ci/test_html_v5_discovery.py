"""Focused V5 route and terminal parser tests; actual bundles are optional local evidence."""
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import socket

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
sys.path.insert(0, str(ROOT / 'ops/ci'))

from contracts import validate_contract
from discovery import (DELINEA_HTML_MODE_V4, DELINEA_HTML_MODE_V5, DELINEA_INDEX,
                       SONATYPE_HTML_MODE_V4, SONATYPE_HTML_MODE_V5, SONATYPE_INDEX,
                       discover, parse_source_html_index)
from test_html_archive_discovery import (NOW, delinea_url, sonatype_page, sonatype_url, source)


V4_BUNDLE = Path('/var/tmp/smp-bounded-v4-probe-20261024/target-bundle')
V4_STATE = Path('/var/tmp/smp-bounded-v4-probe-20261024/archive-e467ab00/jessepike-sec-market-e467ab000b8225931d6684eb6d0aa39bbba1f6c9/state')
SONATYPE_PAGE13_BODY_SHA256 = '7af5acbbd1aa77e6d5819b03d682e1c41ad692583516f24a573806e0e25fec8d'
SONATYPE_PAGE13_URL = SONATYPE_INDEX + '?page=13'


def delinea_source(mode=DELINEA_HTML_MODE_V5):
    return {**source('delinea'), 'htmlCompleteness': mode}


def sonatype_source(mode=SONATYPE_HTML_MODE_V5):
    return {**source('sonatype'), 'htmlCompleteness': mode}


def delinea_terminal_page(*, current=25, numbered=None, disabled_href=None, disabled_classes=None,
                           extra_disabled_attrs='', duplicate_next=False, head_next=False, cards=12,
                           include_next=True):
    numbered = list(numbered if numbered is not None else range(current - 4, current + 1))
    cards_html = ''.join(
        '<article class="blog-index__post blog-index__post--small">'
        f'<a class="blog-index__post-image-wrapper" href="{DELINEA_INDEX}/fixture-{current}-{i}">Image</a>'
        '<h2 class="blog-index__post-title"><a class="blog-index__post-title-link" '
        f'href="{DELINEA_INDEX}/fixture-{current}-{i}">Fixture title</a></h2></article>'
        for i in range(cards))
    head_prev = '' if current == 1 else f'<link rel="prev" href="{delinea_url(current - 1)}">'
    if head_next:
        head_next_link = f'<link rel="next" href="{delinea_url(current + 1)}">'
    else:
        head_next_link = ''
    prev = ('<a class="blog-pagination__link blog-pagination__prev-link" '
            f'href="{delinea_url(current - 1)}">Prev</a>')
    nums = ''.join(
        '<a class="blog-pagination__link blog-pagination__number-link' +
        (' blog-pagination__link--active" aria-current="true"' if n == current else '"') +
        f' href="{delinea_url(n)}">{n}</a>' for n in numbered)
    classes = disabled_classes or ('blog-pagination__link blog-pagination__next-link '
                                    'blog-pagination__next-link--disabled')
    href = f' href="{disabled_href}"' if disabled_href is not None else ''
    disabled = (f'<a class="{classes}"{href}{extra_disabled_attrs}>'
                '<span class="blog-pagination__link-text">Next</span>'
                '<svg aria-hidden="true" version="1.0" viewbox="0 0 320 512" width="13" '
                'xmlns="http://www.w3.org/2000/svg"><g id="chevron-right3_layer">'
                '<path d="M1 1" /></g></svg></a>') if include_next else ''
    if duplicate_next and include_next:
        disabled += (f'<a class="{classes}"{href}{extra_disabled_attrs}>'
                     '<span>Next</span></a>')
    return (f'<html><head><link rel="canonical" href="{DELINEA_INDEX}">{head_prev}{head_next_link}</head>'
            f'<body><section class="blog-index">{cards_html}</section>'
            f'<nav class="blog-pagination" role="navigation" aria-label="Pagination">{prev}{nums}{disabled}</nav>'
            '</body></html>').encode()


class HtmlV5DiscoveryTests(unittest.TestCase):
    def test_delinea_positive_terminal_is_structural_and_v4_stays_unproved(self):
        body = delinea_terminal_page()
        v5 = parse_source_html_index(delinea_source(), delinea_url(25), body, 25, NOW)
        self.assertTrue(v5['terminalProved'])
        self.assertIsNone(v5['next'])
        self.assertEqual(v5['currentPage'], 25)
        self.assertEqual(v5['highestPage'], 25)
        self.assertEqual(len(v5['items']), 12)
        self.assertEqual(v5['publisherLeadWarnings'], [])
        v4 = parse_source_html_index(delinea_source(DELINEA_HTML_MODE_V4), delinea_url(25), body, 25, NOW)
        self.assertFalse(v4['terminalProved'])
        self.assertNotIn('publisherLeadWarnings', v4)

    def test_delinea_terminal_rejects_missing_conflicting_or_hidden_control_state(self):
        body = delinea_terminal_page()
        no_next = delinea_terminal_page(include_next=False)
        no_next_result = parse_source_html_index(delinea_source(), delinea_url(25), no_next, 25, NOW)
        self.assertFalse(no_next_result['terminalProved'])
        cases = [
            ('disabled link has href', delinea_terminal_page(disabled_href=delinea_url(26))),
            ('missing disabled class', delinea_terminal_page(disabled_classes='blog-pagination__link blog-pagination__next-link')),
            ('duplicate disabled control', delinea_terminal_page(duplicate_next=True)),
            ('head next contradicts terminal', delinea_terminal_page(head_next=True)),
            ('hidden target attribute', delinea_terminal_page(extra_disabled_attrs=' data-href="https://delinea.com/news/page/26"')),
            ('active page is not last', delinea_terminal_page(numbered=range(22, 27))),
            ('prior higher page retained', delinea_terminal_page()),
            ('empty card region', delinea_terminal_page(cards=0)),
        ]
        event_handler = body.replace(
            b'<span class="blog-pagination__link-text">Next</span>',
            b'<span class="blog-pagination__link-text" onpointerdown="location.href=\'https://delinea.com/news/page/26\'">Next</span>', 1)
        embedded_control = body.replace(
            b'</svg></a>',
            b'</svg><input type="button" data-next="https://delinea.com/news/page/26"></a>', 1)
        embedded_script = body.replace(
            b'</svg></a>',
            b'</svg><script src="https://delinea.com/news/page/26"></script></a>', 1)
        for label, value in [('span event destination', event_handler),
                             ('embedded control destination', embedded_control),
                             ('embedded script destination', embedded_script)]:
            with self.subTest(label=label), self.assertRaises(ValueError):
                parse_source_html_index(delinea_source(), delinea_url(25), value, 25, NOW)
        for label, value in cases:
            highest = 26 if label == 'prior higher page retained' else 25
            with self.subTest(label=label), self.assertRaises(ValueError):
                parse_source_html_index(delinea_source(), delinea_url(25), value, highest, NOW)

    def test_sonatype_v5_emits_one_exact_publisher_lead_warning(self):
        from discovery import SONATYPE_V5_PUBLISHER_LEAD_URL
        page = sonatype_page(10)
        original = SONATYPE_INDEX + '/fixture-10-2'
        page = page.replace(original.encode(), SONATYPE_V5_PUBLISHER_LEAD_URL.encode(), 1)
        parsed = parse_source_html_index(sonatype_source(), sonatype_url(10), page, 13, NOW)
        self.assertIn(SONATYPE_V5_PUBLISHER_LEAD_URL, parsed['items'])
        self.assertEqual(parsed['publisherLeadWarnings'], [{
            'url': SONATYPE_V5_PUBLISHER_LEAD_URL,
            'cardTitle': 'Fixture title',
            'indexDate': '2026-05-30',
            'reason': 'PUBLISHER_CARD_LINK_REQUIRES_PRIMARY_REVIEW',
        }])
        self.assertEqual(parsed['dates'][SONATYPE_V5_PUBLISHER_LEAD_URL], '2026-05-30')
        self.assertFalse(parsed['terminalProved'])

    def test_sonatype_exception_is_exact_card_scoped_and_v4_stays_rejected(self):
        from discovery import SONATYPE_V5_PUBLISHER_LEAD_URL
        page = sonatype_page(10)
        original = SONATYPE_INDEX + '/fixture-10-2'
        page = page.replace(original.encode(), SONATYPE_V5_PUBLISHER_LEAD_URL.encode(), 1)
        with self.assertRaisesRegex(ValueError, 'Unsafe HTML archive article path'):
            parse_source_html_index(sonatype_source(SONATYPE_HTML_MODE_V4), sonatype_url(10), page, 13, NOW)
        for other in (
            SONATYPE_V5_PUBLISHER_LEAD_URL + '/extra',
            SONATYPE_INDEX + '/resources/other/report',
            SONATYPE_V5_PUBLISHER_LEAD_URL + '?source=x',
            SONATYPE_V5_PUBLISHER_LEAD_URL + '#fragment',
            SONATYPE_V5_PUBLISHER_LEAD_URL.replace('/resources/', '/resources/%2f'),
        ):
            with self.subTest(url=other), self.assertRaises(ValueError):
                parse_source_html_index(sonatype_source(), sonatype_url(10),
                    page.replace(SONATYPE_V5_PUBLISHER_LEAD_URL.encode(), other.encode(), 1), 13, NOW)
        outside_only = page.replace(SONATYPE_V5_PUBLISHER_LEAD_URL.encode(), original.encode(), 1)
        outside_only = outside_only.replace(b'</body>',
            f'<a href="{SONATYPE_V5_PUBLISHER_LEAD_URL}">outside</a></body>'.encode())
        parsed = parse_source_html_index(sonatype_source(), sonatype_url(10), outside_only, 13, NOW)
        self.assertEqual(parsed['publisherLeadWarnings'], [])
        self.assertNotIn(SONATYPE_V5_PUBLISHER_LEAD_URL, parsed['items'])

    def test_sonatype_discovery_preserves_warning_without_granting_semantic_result(self):
        from discovery import SONATYPE_V5_PUBLISHER_LEAD_URL
        pages = {sonatype_url(n): sonatype_page(n) for n in range(1, 14)}
        original = SONATYPE_INDEX + '/fixture-2-2'
        pages[sonatype_url(2)] = pages[sonatype_url(2)].replace(original.encode(), SONATYPE_V5_PUBLISHER_LEAD_URL.encode(), 1)
        calls = []
        def request(url):
            calls.append(url)
            return {'status': 'fetched', 'requestedUrl': url, 'finalUrl': url, 'fetchedAt': NOW}, pages[url]
        with patch.object(socket.socket, 'connect', side_effect=AssertionError('network forbidden')):
            found = discover(sonatype_source(), request)
        self.assertTrue(found['complete'])
        self.assertEqual(len(calls), 13)
        self.assertEqual(len(found['publisherLeadWarnings']), 1)
        self.assertEqual(found['publisherLeadWarnings'][0]['url'], SONATYPE_V5_PUBLISHER_LEAD_URL)
        self.assertEqual(found['itemModified'][SONATYPE_V5_PUBLISHER_LEAD_URL], '2026-10-05')
        self.assertNotIn('facts', found)
        self.assertNotIn('newFactIds', found)

    def test_v5_bindings_validate_without_registering_a_source(self):
        # This test deliberately validates adapters without activating candidates.
        contract = json.loads((ROOT / 'web/scripts/migration-proofs/daily-v2-original/market.json').read_text())
        for source_id, mode, index, host in [
            ('delinea:official:1', DELINEA_HTML_MODE_V5, DELINEA_INDEX, 'delinea.com'),
            ('sonatype:official:1', SONATYPE_HTML_MODE_V5, SONATYPE_INDEX, 'www.sonatype.com'),
        ]:
            source_row = next(row for row in contract['sources'] if row['id'] == source_id)
            source_row.update(kind='html_index', url=index, allowedHosts=[host], htmlCompleteness=mode)
        validate_contract(contract)

    @unittest.skipUnless(V4_BUNDLE.is_dir() and V4_STATE.is_dir(),
                         'authenticated V4 target bundle and archive are local replay inputs')
    def test_actual_v4_terminal_and_mislink_are_only_reinterpreted_by_v5(self):
        from discovery import SONATYPE_V5_PUBLISHER_LEAD_URL
        delinea_observation = json.loads((V4_BUNDLE / 'delinea.observation.json').read_text())
        delinea_body = (V4_BUNDLE / 'delinea.body').read_bytes()
        self.assertEqual(hashlib.sha256(delinea_body).hexdigest(), '2cbb9f7c9da6ecbe9205efd1212833d77b7344b8766891d4a545728cf677526d')
        self.assertEqual(hashlib.sha256(delinea_body).hexdigest(), delinea_observation['body']['sha256'])
        old = parse_source_html_index(delinea_source(DELINEA_HTML_MODE_V4), delinea_observation['requestedUrl'],
                                      delinea_body, 25, delinea_observation['fetchedAt'])
        self.assertFalse(old['terminalProved'])
        new = parse_source_html_index(delinea_source(), delinea_observation['requestedUrl'],
                                      delinea_body, 25, delinea_observation['fetchedAt'])
        self.assertTrue(new['terminalProved'])

        sonatype_observation = json.loads((V4_BUNDLE / 'sonatype.observation.json').read_text())
        sonatype_body = (V4_BUNDLE / 'sonatype.body').read_bytes()
        self.assertEqual(hashlib.sha256(sonatype_body).hexdigest(), '9b94a74c28bfee4c52761c5730c567e0fd61b64604c6f4df8e8851afb05abf74')
        self.assertEqual(hashlib.sha256(sonatype_body).hexdigest(), sonatype_observation['body']['sha256'])
        with self.assertRaisesRegex(ValueError, 'Unsafe HTML archive article path'):
            parse_source_html_index(sonatype_source(SONATYPE_HTML_MODE_V4), sonatype_observation['requestedUrl'],
                                    sonatype_body, 13, sonatype_observation['fetchedAt'])
        parsed = parse_source_html_index(sonatype_source(), sonatype_observation['requestedUrl'],
                                         sonatype_body, 13, sonatype_observation['fetchedAt'])
        self.assertEqual(len(parsed['items']), 16)
        self.assertEqual(len(parsed['publisherLeadWarnings']), 1)
        self.assertEqual(parsed['publisherLeadWarnings'][0], {
            'url': SONATYPE_V5_PUBLISHER_LEAD_URL,
            'cardTitle': 'Sonatype Nexus Delivers Advanced Staging; Further Simplifying DevOps-Native Software Development',
            'indexDate': '2018-07-09',
            'reason': 'PUBLISHER_CARD_LINK_REQUIRES_PRIMARY_REVIEW',
        })

        page13_body = (V4_STATE / 'objects' / SONATYPE_PAGE13_BODY_SHA256).read_bytes()
        self.assertEqual(hashlib.sha256(page13_body).hexdigest(), SONATYPE_PAGE13_BODY_SHA256)
        page13 = parse_source_html_index(sonatype_source(), SONATYPE_PAGE13_URL, page13_body, 13,
                                         '2026-10-24T06:18:06.058227Z')
        self.assertTrue(page13['terminalProved'])
        self.assertEqual(len(page13['items']), 13)
        self.assertEqual(page13['publisherLeadWarnings'], [])


if __name__ == '__main__':
    unittest.main()
