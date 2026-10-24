"""Strict V3 route grammar for the three explicitly versioned HTML sources."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from contracts import validate_contract
from discovery import (
    DELINEA_HTML_MODE, DELINEA_HTML_MODE_V2, DELINEA_HTML_MODE_V3, DELINEA_INDEX,
    PING_HTML_MODE, PING_HTML_MODE_V2, PING_HTML_MODE_V3, PING_INDEX,
    SONATYPE_HTML_MODE, SONATYPE_HTML_MODE_V2, SONATYPE_HTML_MODE_V3, SONATYPE_INDEX,
    parse_source_html_index, ping_article_date,
)
from test_html_archive_discovery import delinea_page, sonatype_page, source
from test_ping_discovery import SOURCE as PING_SOURCE, complete_layout


NOW = '2026-10-24T08:00:00Z'
TARGETS = Path('/var/tmp/smp-bounded-v2-probe-20261024/target-bundle')


class HtmlArchiveV3Tests(unittest.TestCase):
    def test_ping_date_helper_is_full_path_strict_and_nonthrowing(self):
        self.assertEqual(ping_article_date('/2018-11-7-Global-Survey', PING_HTML_MODE_V3), '2018-11-07')
        self.assertEqual(ping_article_date('/201810-07-Global-Survey', PING_HTML_MODE_V2), '2018-10-07')
        for path, mode in [
            (None, PING_HTML_MODE_V3),
            ('/2018-11-7-Global-Survey/extra', PING_HTML_MODE_V3),
            ('/2018-2-30-Global-Survey', PING_HTML_MODE_V3),
            ('/201810-32-Global-Survey', PING_HTML_MODE_V2),
            ('/2018-11-7-Global-Survey', PING_HTML_MODE),
        ]:
            with self.subTest(path=path, mode=mode):
                self.assertIsNone(ping_article_date(path, mode))

    def test_ping_v3_accepts_literal_unpadded_date_and_requires_card_date_match(self):
        source = {**PING_SOURCE, 'htmlCompleteness': PING_HTML_MODE_V3}
        body = complete_layout(page=25, last=25)
        body = body.replace(b'/2026-02-25-', b'/2026-2-25-', 1)
        body = body.replace(b'/2026-02-24-', b'/2026-2-24-', 1)
        parsed = parse_source_html_index(source, PING_INDEX + '?o=240', body, 25, NOW)
        self.assertIn('https://press.pingidentity.com/2026-2-25-Release-25-0', parsed['items'])
        self.assertEqual(parsed['dates']['https://press.pingidentity.com/2026-2-25-Release-25-0'], '2026-02-25')
        with self.assertRaisesRegex(ValueError, 'differs from card date'):
            parse_source_html_index(source, PING_INDEX + '?o=240', body.replace(b'Feb 25, 2026', b'Feb 26, 2026', 1), 25, NOW)
        bad_day = body.replace(b'/2026-2-25-Release-25-0', b'/2026-2-30-Release-25-0', 1)
        with self.assertRaisesRegex(ValueError, 'Unsafe Ping article path'):
            parse_source_html_index(source, PING_INDEX + '?o=240', bad_day, 25, NOW)
        original = b'https://press.pingidentity.com/2026-2-25-Release-25-0'
        for raw_href in (b'ignored/../2026-2-25-Release-25-0',
                         b'/2026-2-25-Release-25-0//extra',
                         b'//press.pingidentity.com/2026-2-25-Release-25-0'):
            with self.subTest(raw_href=raw_href), self.assertRaisesRegex(ValueError, 'Unsafe V3'):
                parse_source_html_index(source, PING_INDEX + '?o=240', body.replace(original, raw_href, 1), 25, NOW)

    def test_delinea_v3_accepts_only_observed_historical_press_release_route(self):
        source_row = {**source('delinea'), 'htmlCompleteness': DELINEA_HTML_MODE_V3}
        article = DELINEA_INDEX + '/about-us/news/press-releases/2020/centrify-momentum-fueled-digital-transformation-including-secure'
        body = delinea_page().replace((DELINEA_INDEX + '/fixture-1-0').encode(), article.encode())
        parsed = parse_source_html_index(source_row, DELINEA_INDEX, body, 1, NOW)
        self.assertIn(article, parsed['items'])
        self.assertFalse(parsed['terminalProved'])
        legacy_terminal = DELINEA_INDEX + '/legacy-press-release-'
        legacy_body = delinea_page().replace((DELINEA_INDEX + '/fixture-1-0').encode(), legacy_terminal.encode())
        self.assertIn(legacy_terminal, parse_source_html_index(source_row, DELINEA_INDEX, legacy_body, 1, NOW)['items'])
        for unsafe in (
            DELINEA_INDEX + '/about-us/news/press-releases/2020/first/second',
            DELINEA_INDEX + '/about-us/news/press-releases/2020/first?x=1',
            DELINEA_INDEX + '/about-us/news/press-releases/2020/../first',
            *(DELINEA_INDEX + '/' + slug for slug in ('page', 'pages', 'news', 'press-releases', '123')),
            *(DELINEA_INDEX + '/about-us/news/press-releases/2020/' + slug
              for slug in ('page', 'pages', 'news', 'press-releases', '123')),
        ):
            with self.subTest(unsafe=unsafe), self.assertRaisesRegex(ValueError, 'Unsafe (HTML|V3)'):
                parse_source_html_index(source_row, DELINEA_INDEX,
                    delinea_page().replace((DELINEA_INDEX + '/fixture-1-0').encode(), unsafe.encode()), 1, NOW)
        for raw_href in ('news//fixture-1-0', 'news/about-us//news/press-releases/2020/fixture'):
            with self.subTest(raw_href=raw_href), self.assertRaisesRegex(ValueError, 'Unsafe V3'):
                parse_source_html_index(source_row, DELINEA_INDEX,
                    delinea_page().replace((DELINEA_INDEX + '/fixture-1-0').encode(), raw_href.encode()), 1, NOW)

    def test_sonatype_v3_accepts_one_nested_slug_and_rejects_controls_or_deeper_routes(self):
        source_row = {**source('sonatype'), 'htmlCompleteness': SONATYPE_HTML_MODE_V3}
        article = SONATYPE_INDEX + '/sonatype-expands-solution-to-support-c/c-php-and-ruby'
        body = sonatype_page().replace((SONATYPE_INDEX + '/fixture-1-0').encode(), article.encode())
        parsed = parse_source_html_index(source_row, SONATYPE_INDEX, body, 1, NOW)
        self.assertIn(article, parsed['items'])
        for unsafe in (
            *(SONATYPE_INDEX + '/' + slug for slug in ('page', 'pages', 'news', 'press-releases', '123')),
            SONATYPE_INDEX + '/page/7',
            SONATYPE_INDEX + '/foo/bar/baz',
            SONATYPE_INDEX + '/foo/123',
            *(SONATYPE_INDEX + '/foo/' + slug for slug in ('page', 'pages', 'news', 'press-releases')),
            SONATYPE_INDEX + '/foo/bar#x',
        ):
            with self.subTest(unsafe=unsafe), self.assertRaisesRegex(ValueError, 'Unsafe HTML archive article path'):
                parse_source_html_index(source_row, SONATYPE_INDEX,
                    sonatype_page().replace((SONATYPE_INDEX + '/fixture-1-0').encode(), unsafe.encode()), 1, NOW)
        for raw_href in ('press-releases//fixture-1-0', 'press-releases/foo//bar'):
            with self.subTest(raw_href=raw_href), self.assertRaisesRegex(ValueError, 'Unsafe V3'):
                parse_source_html_index(source_row, SONATYPE_INDEX,
                    sonatype_page().replace((SONATYPE_INDEX + '/fixture-1-0').encode(), raw_href.encode()), 1, NOW)

    def test_v3_shared_article_url_guards_remain_strict(self):
        cases = [
            (source('delinea') | {'htmlCompleteness': DELINEA_HTML_MODE_V3}, DELINEA_INDEX, delinea_page(),
             DELINEA_INDEX + '/fixture-1-0'),
            (source('sonatype') | {'htmlCompleteness': SONATYPE_HTML_MODE_V3}, SONATYPE_INDEX, sonatype_page(),
             SONATYPE_INDEX + '/fixture-1-0'),
        ]
        for row, root, body, article in cases:
            for target in (article + '?x=1', article + '#fragment', article.replace('https://', 'http://'),
                           article.replace('https://', 'https://user@'), article.replace('.com/', '.com:444/'),
                           article.replace('/fixture', '/%66ixture'), article.replace('/fixture', '//fixture'),
                           article.replace('/fixture', '/../news/fixture'), article.replace('fixture', 'bad\\path')):
                with self.subTest(source=row['supplierId'], target=target), self.assertRaises(ValueError):
                    parse_source_html_index(row, root, body.replace(article.encode(), target.encode()), 1, NOW)

    def test_reserved_direct_slugs_remain_legacy_behavior_only(self):
        for mode in (DELINEA_HTML_MODE, DELINEA_HTML_MODE_V2):
            row = {**source('delinea'), 'htmlCompleteness': mode}
            body = delinea_page().replace((DELINEA_INDEX + '/fixture-1-0').encode(),
                                          (DELINEA_INDEX + '/page').encode())
            self.assertIn(DELINEA_INDEX + '/page', parse_source_html_index(row, DELINEA_INDEX, body, 1, NOW)['items'])
        for mode in (SONATYPE_HTML_MODE, SONATYPE_HTML_MODE_V2):
            row = {**source('sonatype'), 'htmlCompleteness': mode}
            body = sonatype_page().replace((SONATYPE_INDEX + '/fixture-1-0').encode(),
                                           (SONATYPE_INDEX + '/page').encode())
            self.assertIn(SONATYPE_INDEX + '/page', parse_source_html_index(row, SONATYPE_INDEX, body, 1, NOW)['items'])

    def test_v3_contract_mode_is_source_bound(self):
        contract = json.loads((ROOT / 'contracts' / 'market.json').read_text())
        for source_id, mode in (
            ('ping-identity:official:1', PING_HTML_MODE_V3),
            ('delinea:official:1', DELINEA_HTML_MODE_V3),
            ('sonatype:official:1', SONATYPE_HTML_MODE_V3),
        ):
            modified = copy.deepcopy(contract)
            row = next(item for item in modified['sources'] if item['id'] == source_id)
            row['kind'] = 'html_index'
            row['htmlCompleteness'] = mode
            row['url'] = {'ping-identity:official:1': PING_INDEX,
                          'delinea:official:1': DELINEA_INDEX,
                          'sonatype:official:1': SONATYPE_INDEX}[source_id]
            validate_contract(modified)
            row['allowedHosts'] = ['attacker.invalid']
            with self.subTest(source_id=source_id), self.assertRaises(ValueError):
                validate_contract(modified)

    @unittest.skipUnless((TARGETS / 'verified-targets.json').exists(), 'authenticated V2 target bodies are VM-local')
    def test_authenticated_v2_examples_are_v3_parseable_but_not_rewritten(self):
        pins = {
            'ping': ('ping-identity.body', 'fb43c33de4629c766ac62e84895fa446e6d7d12513dfdaf6bb34fc7cff86cdef',
                     PING_INDEX + '?o=200', {**PING_SOURCE, 'htmlCompleteness': PING_HTML_MODE_V3}, 20,
                     'https://press.pingidentity.com/2018-11-7-Global-Survey-from-Ping-Identity-Shows-Consumers-Are-Abandoning-Brands-After-Data-Breaches'),
            'delinea': ('delinea.body', 'e4b5201c4f21e94415f203717ccc2f3000d68852fdef1c627bed9b84adf7e791',
                        DELINEA_INDEX + '/page/18', {**source('delinea'), 'htmlCompleteness': DELINEA_HTML_MODE_V3}, 18,
                        DELINEA_INDEX + '/about-us/news/press-releases/2020/centrify-momentum-fueled-digital-transformation-including-secure'),
            'sonatype': ('sonatype.body', '2e94dddf68d90a83fa76cb8bc264d5cb206ead4cf73a1358c2a884fc223ff7bf',
                         SONATYPE_INDEX + '?page=7', {**source('sonatype'), 'htmlCompleteness': SONATYPE_HTML_MODE_V3}, 7,
                         SONATYPE_INDEX + '/sonatype-expands-solution-to-support-c/c-php-and-ruby'),
        }
        for name, (filename, sha, url, source_row, highest, expected) in pins.items():
            body = (TARGETS / filename).read_bytes()
            with self.subTest(source=name):
                self.assertEqual(hashlib.sha256(body).hexdigest(), sha)
                parsed = parse_source_html_index(source_row, url, body, highest, NOW)
                self.assertIn(expected, parsed['items'])
                if name == 'delinea':
                    self.assertFalse(parsed['terminalProved'])
                if name == 'ping':
                    for mode in (PING_HTML_MODE, PING_HTML_MODE_V2):
                        with self.subTest(source=name, historical_mode=mode), self.assertRaisesRegex(ValueError, 'Unsafe Ping article path'):
                            parse_source_html_index({**source_row, 'htmlCompleteness': mode}, url, body, highest, NOW)
                elif name == 'delinea':
                    with self.assertRaisesRegex(ValueError, 'Unsafe HTML archive article path'):
                        parse_source_html_index({**source_row, 'htmlCompleteness': DELINEA_HTML_MODE}, url, body, highest, NOW)
                else:
                    with self.assertRaisesRegex(ValueError, 'Unsafe HTML archive article path'):
                        parse_source_html_index({**source_row, 'htmlCompleteness': SONATYPE_HTML_MODE}, url, body, highest, NOW)


if __name__ == '__main__':
    unittest.main()
