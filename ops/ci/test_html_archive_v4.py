"""V4 adds only authenticated Delinea and Sonatype article path forms."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from contracts import validate_contract
from discovery import (
    DELINEA_HTML_MODE_V3, DELINEA_HTML_MODE_V4, DELINEA_INDEX,
    SONATYPE_HTML_MODE_V3, SONATYPE_HTML_MODE_V4, SONATYPE_INDEX,
    parse_source_html_index,
)
from test_html_archive_discovery import delinea_page, sonatype_page, source

NOW = '2026-10-24T08:30:00Z'
TARGETS = Path('/var/tmp/smp-bounded-v3-probe-20261024/target-bundle')


def target_bundle_available(root=TARGETS):
    return all((root / name).is_file() for name in
               ('verified-targets.json', 'delinea.body', 'sonatype.body'))


class HtmlArchiveV4Tests(unittest.TestCase):
    def test_delinea_company_blog_route_requires_fixed_shape_and_calendar_date(self):
        row = {**source('delinea'), 'htmlCompleteness': DELINEA_HTML_MODE_V4}
        article = DELINEA_INDEX + '/company/blog/2020/06/02/thycotic-extends-pam-cloud-leadership-with-acquisition-of-onion-id'
        body = delinea_page().replace((DELINEA_INDEX + '/fixture-1-0').encode(), article.encode())
        self.assertIn(article, parse_source_html_index(row, DELINEA_INDEX, body, 1, NOW)['items'])
        for path in (
            '/company/blog/2020/02/30/valid-slug',
            '/company/blog/2020/6/02/valid-slug',
            '/company/blog/2020/06/02/valid-slug/extra',
            '/company/blog/2020/06/02/123',
            '/company/blog/2020/06/02/page',
            '/company/blog/2020/06/02/valid--slug',
        ):
            target = DELINEA_INDEX + path
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'Unsafe (HTML|V3)'):
                parse_source_html_index(row, DELINEA_INDEX,
                    delinea_page().replace((DELINEA_INDEX + '/fixture-1-0').encode(), target.encode()), 1, NOW)
        with self.assertRaisesRegex(ValueError, 'Unsafe HTML archive article path'):
            parse_source_html_index({**row, 'htmlCompleteness': DELINEA_HTML_MODE_V3},
                                    DELINEA_INDEX, body, 1, NOW)

    def test_sonatype_v4_allows_one_final_hyphen_and_keeps_slug_guards(self):
        row = {**source('sonatype'), 'htmlCompleteness': SONATYPE_HTML_MODE_V4}
        direct = SONATYPE_INDEX + '/sonatypes-2019-nexus-user-conference-'
        direct_body = sonatype_page().replace((SONATYPE_INDEX + '/fixture-1-0').encode(), direct.encode())
        self.assertIn(direct, parse_source_html_index(row, SONATYPE_INDEX, direct_body, 1, NOW)['items'])
        nested = SONATYPE_INDEX + '/sonatype-expands-solution/c-php-and-ruby-'
        nested_body = sonatype_page().replace((SONATYPE_INDEX + '/fixture-1-0').encode(), nested.encode())
        self.assertIn(nested, parse_source_html_index(row, SONATYPE_INDEX, nested_body, 1, NOW)['items'])
        for path in (
            '/sonatypes-2019-nexus-user-conference--',
            '/page-',
            '/123-',
            '/press-releases/foo/bar-',
            '/foo-/bar',
            '/foo//bar-',
        ):
            target = SONATYPE_INDEX + path
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'Unsafe (HTML|V3)'):
                parse_source_html_index(row, SONATYPE_INDEX,
                    sonatype_page().replace((SONATYPE_INDEX + '/fixture-1-0').encode(), target.encode()), 1, NOW)
        with self.assertRaisesRegex(ValueError, 'Unsafe HTML archive article path'):
            parse_source_html_index({**row, 'htmlCompleteness': SONATYPE_HTML_MODE_V3},
                                    SONATYPE_INDEX, direct_body, 1, NOW)

    def test_missing_archive_bundle_is_detected_without_affecting_synthetic_cases(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertFalse(target_bundle_available(Path(temp)))
        self.assertTrue(target_bundle_available(TARGETS) or not TARGETS.exists())

    @unittest.skipUnless(target_bundle_available(), 'authenticated actual-page bundle is local integration evidence; synthetic grammar tests still run')
    def test_authenticated_v3_page_bodies_replay_only_under_v4(self):
        cases = (
            ('delinea', 'delinea.body', '2d71b1e6366129e1ca17c9436764e4091d5d1a91c44bdf073cf5ad72f664dc28',
             DELINEA_INDEX + '/page/21', {**source('delinea'), 'htmlCompleteness': DELINEA_HTML_MODE_V4}, 21,
             DELINEA_INDEX + '/company/blog/2020/06/02/thycotic-extends-pam-cloud-leadership-with-acquisition-of-onion-id'),
            ('sonatype', 'sonatype.body', 'eb3c8166d0bcf3924f2992af9c32a1d64cc817ba24e9778d4038f0c6b1b9eb6a',
             SONATYPE_INDEX + '?page=8', {**source('sonatype'), 'htmlCompleteness': SONATYPE_HTML_MODE_V4}, 8,
             SONATYPE_INDEX + '/sonatypes-2019-nexus-user-conference-'),
        )
        for name, filename, expected_sha, url, row, highest, target in cases:
            body = (TARGETS / filename).read_bytes()
            with self.subTest(source=name):
                self.assertEqual(hashlib.sha256(body).hexdigest(), expected_sha)
                parsed = parse_source_html_index(row, url, body, highest, NOW)
                self.assertIn(target, parsed['items'])
                if name == 'delinea':
                    self.assertFalse(parsed['terminalProved'])
                prior_mode = DELINEA_HTML_MODE_V3 if name == 'delinea' else SONATYPE_HTML_MODE_V3
                with self.assertRaisesRegex(ValueError, 'Unsafe HTML archive article path'):
                    parse_source_html_index({**row, 'htmlCompleteness': prior_mode}, url, body, highest, NOW)

    def test_v4_contract_bindings_are_exact(self):
        contract = json.loads((ROOT / 'contracts' / 'market.json').read_text())
        for source_id, mode, root in (
            ('delinea:official:1', DELINEA_HTML_MODE_V4, DELINEA_INDEX),
            ('sonatype:official:1', SONATYPE_HTML_MODE_V4, SONATYPE_INDEX),
        ):
            modified = copy.deepcopy(contract)
            row = next(item for item in modified['sources'] if item['id'] == source_id)
            row['kind'] = 'html_index'
            row['htmlCompleteness'] = mode
            row['url'] = root
            validate_contract(modified)
            row['url'] = root + '/other'
            with self.subTest(source_id=source_id), self.assertRaises(ValueError):
                validate_contract(modified)


if __name__ == '__main__':
    unittest.main()
