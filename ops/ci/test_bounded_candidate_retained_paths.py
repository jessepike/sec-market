"""Explicit V2 HTML modes accept three retained same-host article paths only."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
sys.path.insert(0, str(ROOT / 'ops/ci'))

from contracts import validate_contract
from discovery import (DELINEA_HTML_MODE_V2, DELINEA_INDEX, PING_HTML_MODE_V2,
                       PING_INDEX, SONATYPE_HTML_MODE_V2, SONATYPE_INDEX,
                       discover, parse_source_html_index)
from test_html_archive_discovery import delinea_page, sonatype_page
from test_ping_discovery import SOURCE as PING_SOURCE, complete_layout

ARCHIVE_STATE = Path('/var/tmp/smp-bounded-probe-20261024/archive-c9619457/'
    'jessepike-sec-market-c961945736499da3105d565e513eda78a01e996a/state')
RECEIPT = Path('/mnt/mac/Users/jessepike/Documents/Codex/2026-10-22/security-market-pulse/'
    'renewal-20261024/bounded-traversal-40072784799/source-probe-receipt/smp-collection-receipt.json')
AS_OF = '2026-10-24T07:08:47.637490Z'


def html_source(supplier, mode):
    return {
        'id': supplier + ':official:1', 'supplierId': supplier,
        'family': 'official_announcements', 'registration': 'candidate',
        'kind': 'html_index', 'required': True, 'maxPages': 60,
        'url': {'ping-identity': PING_INDEX, 'delinea': DELINEA_INDEX,
                'sonatype': SONATYPE_INDEX}[supplier],
        'allowedHosts': {'ping-identity': ['press.pingidentity.com'],
                         'delinea': ['delinea.com'],
                         'sonatype': ['www.sonatype.com']}[supplier],
        'htmlCompleteness': mode,
    }


class BoundedCandidateRetainedPathTests(unittest.TestCase):
    def test_v1_keeps_old_rejections_while_explicit_v2_accepts_pinned_shapes(self):
        ping = complete_layout()
        ping = ping.replace(b'2026-10-23-Release-1-0', b'202610-23-Release-1-0', 1)
        with self.assertRaisesRegex(ValueError, 'Unsafe Ping article path'):
            parse_source_html_index({**PING_SOURCE, 'registration': 'candidate'}, PING_INDEX,
                                    ping, 1, AS_OF)
        parsed = parse_source_html_index(html_source('ping-identity', PING_HTML_MODE_V2),
                                         PING_INDEX, ping, 1, AS_OF)
        self.assertIn('https://press.pingidentity.com/202610-23-Release-1-0', parsed['items'])

        delinea = delinea_page().replace(b'fixture-1-0', b'fixture-1-0-', 2)
        with self.assertRaisesRegex(ValueError, 'Unsafe HTML archive article path'):
            parse_source_html_index(html_source('delinea', 'delinea-news-pagination-v1'),
                                    DELINEA_INDEX, delinea, 1, AS_OF)
        parsed = parse_source_html_index(html_source('delinea', DELINEA_HTML_MODE_V2),
                                         DELINEA_INDEX, delinea, 1, AS_OF)
        self.assertIn(DELINEA_INDEX + '/fixture-1-0-', parsed['items'])

        sonatype = sonatype_page().replace(
            (SONATYPE_INDEX + '/fixture-1-0').encode(),
            (SONATYPE_INDEX + '/sonatype-introduces-cutting-edge-ai/ml-component-detection').encode(), 1)
        with self.assertRaisesRegex(ValueError, 'Unsafe HTML archive article path'):
            parse_source_html_index(html_source('sonatype', 'sonatype-press-pagination-v1'),
                                    SONATYPE_INDEX, sonatype, 1, AS_OF)
        parsed = parse_source_html_index(html_source('sonatype', SONATYPE_HTML_MODE_V2),
                                         SONATYPE_INDEX, sonatype, 1, AS_OF)
        self.assertIn(SONATYPE_INDEX + '/sonatype-introduces-cutting-edge-ai/ml-component-detection',
                      parsed['items'])

    def test_v2_article_path_allowances_do_not_admit_queries_foreign_hosts_or_pagination(self):
        delinea_source = html_source('delinea', DELINEA_HTML_MODE_V2)
        original = delinea_page()
        for old, new in [
            (b'https://delinea.com/news/fixture-1-0', b'https://evil.invalid/news/fixture-1-0-'),
            (b'https://delinea.com/news/fixture-1-0', b'https://delinea.com/news/fixture-1-0-?x=1'),
            (b'https://delinea.com/news/fixture-1-0', b'https://delinea.com/news/page/9'),
        ]:
            with self.subTest(new=new), self.assertRaises(ValueError):
                parse_source_html_index(delinea_source, DELINEA_INDEX, original.replace(old, new, 1), 1, AS_OF)

        sonatype_source = html_source('sonatype', SONATYPE_HTML_MODE_V2)
        unsafe = sonatype_page().replace(
            (SONATYPE_INDEX + '/fixture-1-0').encode(),
            (SONATYPE_INDEX + '/sonatype-introduces-cutting-edge-ai/ml-component-detection?x=1').encode(), 1)
        with self.assertRaisesRegex(ValueError, 'Unsafe HTML archive article path'):
            parse_source_html_index(sonatype_source, SONATYPE_INDEX, unsafe, 1, AS_OF)

    def test_normal_discovery_dispatches_explicit_v2_modes(self):
        ping = complete_layout().replace(b'2026-10-23-Release-1-0', b'202610-23-Release-1-0', 1)
        fixtures = [
            (html_source('ping-identity', PING_HTML_MODE_V2), ping),
            (html_source('delinea', DELINEA_HTML_MODE_V2), delinea_page(next_page=False)),
            (html_source('sonatype', SONATYPE_HTML_MODE_V2), sonatype_page()),
        ]
        for source, body in fixtures:
            source.update(registration='verified', checkedAt=AS_OF)
            requests = []

            def request(url):
                requests.append(url)
                if url != source['url']:
                    raise OSError('fixture contains only the root page')
                return {'status': 'fetched', 'requestedUrl': url, 'finalUrl': url,
                        'fetchedAt': AS_OF}, body

            result = discover(source, request)
            self.assertTrue(result['items'])
            self.assertEqual(requests[0], source['url'])

    def test_contract_recognizes_exact_v2_bindings_only(self):
        # V2 adapter validation starts from the original candidate declarations.
        contract = json.loads((ROOT / 'web/scripts/migration-proofs/daily-v2-original/market.json').read_text())
        for source_id, url, host, mode in (
            ('ping-identity:official:1', PING_INDEX, 'press.pingidentity.com', PING_HTML_MODE_V2),
            ('delinea:official:1', DELINEA_INDEX, 'delinea.com', DELINEA_HTML_MODE_V2),
            ('sonatype:official:1', SONATYPE_INDEX, 'www.sonatype.com', SONATYPE_HTML_MODE_V2),
        ):
            candidate = copy.deepcopy(contract)
            source = next(row for row in candidate['sources'] if row['id'] == source_id)
            source.update(kind='html_index', url=url, allowedHosts=[host], htmlCompleteness=mode)
            validate_contract(candidate)
            source['url'] = url + '/page/9'
            with self.assertRaises(ValueError):
                validate_contract(candidate)

    @unittest.skipUnless(ARCHIVE_STATE.exists() and RECEIPT.exists(),
                         'authenticated bounded-run archive is a local replay input')
    def test_actual_rejected_pages_replay_under_explicit_v2_modes_without_changing_bytes(self):
        receipt = json.loads(RECEIPT.read_text())
        expected = {
            'ping-identity:official:1': ('https://press.pingidentity.com/news-releases?o=170',
                PING_HTML_MODE_V2, '201907-09-Ping-Identity-Named-Best-Identity-Management-Solution-at-the-2019-SC-Awards-Europe'),
            'delinea:official:1': ('https://delinea.com/news/page/9',
                DELINEA_HTML_MODE_V2, 'https://delinea.com/news/fifth-consecutive-northface-scoreboard-award-'),
            'sonatype:official:1': ('https://www.sonatype.com/press-releases?page=3',
                SONATYPE_HTML_MODE_V2, 'https://www.sonatype.com/press-releases/sonatype-introduces-cutting-edge-ai/ml-component-detection'),
        }
        observed_sources = {row['sourceId']: row for row in receipt['diagnostic']['sources']}
        for source_id, (url, mode, literal_path) in expected.items():
            source_result = observed_sources[source_id]
            page = next(row for row in source_result['observations'] if row['url'] == url)
            self.assertIsNotNone(page.get('parser', {}).get('error'))
            wrapper_raw = (ARCHIVE_STATE / page['observation']['key']).read_bytes()
            self.assertEqual(hashlib.sha256(wrapper_raw).hexdigest(), page['observation']['sha256'])
            wrapper = json.loads(wrapper_raw)
            raw_observation = (ARCHIVE_STATE / wrapper['rawObservation']['key']).read_bytes()
            self.assertEqual(hashlib.sha256(raw_observation).hexdigest(), wrapper['rawObservation']['sha256'])
            observation = json.loads(raw_observation)
            body = (ARCHIVE_STATE / observation['body']['key']).read_bytes()
            self.assertEqual(hashlib.sha256(body).hexdigest(), observation['body']['sha256'])
            self.assertEqual(len(body), observation['body']['bytes'])
            source = html_source(source_id.split(':')[0], mode)
            parsed = parse_source_html_index(source, url, body, 1, observation['fetchedAt'])
            if source_id.startswith('ping'):
                self.assertTrue(any(literal_path in item for item in parsed['items']))
            else:
                self.assertIn(literal_path, parsed['items'])
            self.assertEqual(hashlib.sha256(body).hexdigest(), observation['body']['sha256'])


if __name__ == '__main__':
    unittest.main()
