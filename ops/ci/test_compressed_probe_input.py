"""Candidate probe decoding with fictional transport and temporary ledgers only."""
import copy
import gzip
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from contracts import digest
from onboarding import PersistentProbeBudget, probe_sources
from storage import LocalStore
from ops.ci.test_onboarding_budget import Clock, NOW, contract

HOME = 'https://example.invalid/news'
ROBOTS = 'https://example.invalid/robots.txt'
FEED = 'https://example.invalid/advertised-feed.xml'
SITEMAP = 'https://example.invalid/maps/advertised.xml'
FALLBACK = 'https://example.invalid/sitemap.xml'
HTML = b'<html><head><link rel="alternate" type="application/rss+xml" href="/advertised-feed.xml"></head><body>Fictional publisher.</body></html>'
ALLOW = b'User-agent: *\nAllow: /\n'
RSS = b'<rss><channel><item><link>https://example.invalid/release-one</link></item><item><link>https://example.invalid/release-two</link></item></channel></rss>'
XML = b'<urlset><url><loc>https://example.invalid/release-one</loc></url></urlset>'


class FictionalTransport:
    def __init__(self, store, pages):
        self.store, self.pages, self.calls, self.observations, self.charged_counts = store, pages, [], [], []

    def fetch(self, source, url):
        self.calls.append(url)
        self.charged_counts.append(self.store.read('heads/budget-2026-10-23.json')['fetches'])
        body = self.pages.get(url, 404)
        observed = {'requestedUrl': url, 'finalUrl': url, 'fetchedAt': NOW,
                    'observationId': digest({'url': url, 'call': len(self.calls)})}
        if isinstance(body, int):
            observed.update(status='blocked' if body == 403 else 'failed', httpStatus=body, errorCode='HTTP_' + str(body))
        else:
            observed.update(status='fetched', httpStatus=200, body=self.store.put(body), contentType='application/octet-stream')
        self.observations.append(copy.deepcopy(observed))
        return observed


class CompressedProbeInputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(Path(self.temp.name) / 'synthetic-state')
        self.clock = Clock()
        self.c = contract(); self.c['sources'][0]['url'] = HOME
        self.initial = {'calls': 80, 'documents': 40, 'fetches': 7, 'extra': {'unchanged': 9}}
        self.store.compare_and_swap('budget-2026-10-23', None, self.initial)
        self.sentinel = {'runId': 'unchanged-real-coverage-is-not-a-probe'}
        self.store.compare_and_swap('latest-run', None, self.sentinel)

    def probe(self, pages):
        before = copy.deepcopy(self.c)
        fetcher = FictionalTransport(self.store, pages)
        budget = PersistentProbeBudget(self.store, self.c, clock=self.clock.now, monotonic=self.clock.monotonic)
        result = probe_sources(self.c, self.store, fetcher, reservation_context=budget)
        self.assertEqual(self.c, before)
        self.assertEqual(self.store.read('heads/latest-run.json'), self.sentinel)
        self.assertFalse(result['qualified']); self.assertFalse(result['semanticAdmission']); self.assertFalse(result['coverageCredit'])
        self.assertEqual(result['sourceChecksCredited'], 0); self.assertEqual(result['qualifiedSources'], 0); self.assertEqual(result['facts'], [])
        self.assertEqual(result['reservationContext']['probeFetchReservations'], len(fetcher.calls))
        self.assertEqual(self.store.read('heads/budget-2026-10-23.json'), {**self.initial, 'fetches': self.initial['fetches'] + len(fetcher.calls)})
        source = result['sources'][0]
        self.assertEqual(source['registration'], 'candidate'); self.assertFalse(source['qualified'])
        self.assertFalse(source['semanticAdmission']); self.assertFalse(source['coverageCredit']); self.assertEqual(source['facts'], [])
        self.assertEqual([json.loads(self.store.get(ref)) for ref in source['observations']], fetcher.observations)
        for observed in fetcher.observations:
            self.assertEqual(observed['fetchedAt'], NOW)
            if 'body' in observed:
                self.assertEqual(self.store.get(observed['body']), pages[observed['requestedUrl']])
        return source, fetcher, result

    def test_compressed_html_advertises_feed_and_original_observations_remain_unchanged(self):
        source, fetcher, result = self.probe({HOME: gzip.compress(HTML), ROBOTS: ALLOW, FEED: RSS})
        self.assertEqual(fetcher.calls, [HOME, ROBOTS, FEED])
        self.assertEqual(fetcher.charged_counts, [8, 9, 10])
        self.assertEqual(source['endpoints'][0]['result'], 'DISCOVERY_ENDPOINT_RESPONDED')
        self.assertEqual(source['endpoints'][0]['format'], 'rss')
        self.assertEqual(source['endpoints'][0]['itemCount'], 2)
        self.assertEqual(source['reason'], 'ENDPOINTS_PROBED_SCOPE_AND_HISTORY_REVIEW_REQUIRED')
        self.assertTrue(result['executionCompleted']); self.assertFalse(result['budgetDenied'])

    def test_compressed_robots_advertises_only_its_sitemap(self):
        source, fetcher, _ = self.probe({HOME: b'<html>Fictional publisher.</html>',
            ROBOTS: gzip.compress(ALLOW + ('Sitemap: ' + SITEMAP + '\n').encode()), SITEMAP: XML})
        self.assertEqual(fetcher.calls, [HOME, ROBOTS, SITEMAP])
        self.assertEqual(source['endpoints'][0]['url'], SITEMAP)
        self.assertEqual(source['endpoints'][0]['itemCount'], 1)
        self.assertNotIn(FALLBACK, fetcher.calls)

    def test_compressed_robots_denial_prevents_advertised_feed_and_sitemap_requests(self):
        robots = b'User-agent: SecurityMarketPulse\nDisallow: /advertised-feed.xml\nDisallow: /maps/\n' + ('Sitemap: ' + SITEMAP + '\n').encode()
        source, fetcher, _ = self.probe({HOME: gzip.compress(HTML), ROBOTS: gzip.compress(robots)})
        self.assertEqual(fetcher.calls, [HOME, ROBOTS])
        self.assertEqual([entry['result'] for entry in source['endpoints']], ['ROBOTS_DISALLOWED', 'ROBOTS_DISALLOWED'])

    def test_compressed_xml_feed_and_sitemap_index_use_existing_bounded_xml_parser(self):
        index = b'<sitemapindex><sitemap><loc>https://example.invalid/child.xml</loc></sitemap></sitemapindex>'
        robots = gzip.compress(ALLOW + ('Sitemap: ' + SITEMAP + '\n').encode())
        source, fetcher, _ = self.probe({HOME: gzip.compress(HTML), ROBOTS: robots,
                                        FEED: gzip.compress(RSS), SITEMAP: gzip.compress(index)})
        self.assertEqual(fetcher.calls, [HOME, ROBOTS, FEED, SITEMAP])
        self.assertEqual(source['endpoints'][0]['itemCount'], 2)
        self.assertEqual(source['endpoints'][1]['indexCount'], 1)
        self.assertEqual(source['endpoints'][1]['sampleIndexes'], ['https://example.invalid/child.xml'])
        self.assertNotIn('https://example.invalid/child.xml', fetcher.calls)

    def test_unregistered_hosts_and_ordinary_html_links_never_become_requests(self):
        html = HTML + b'<a href="/arbitrary.xml">Not a feed</a><link type="application/rss+xml" href="https://unregistered.invalid/feed.xml">'
        source, fetcher, _ = self.probe({HOME: gzip.compress(html), ROBOTS: gzip.compress(ALLOW), FEED: RSS})
        self.assertEqual(fetcher.calls, [HOME, ROBOTS, FEED])
        self.assertEqual(source['endpoints'][1]['result'], 'ADDITIONAL_HOST_REQUIRES_REGISTRATION')

    def test_candidate_endpoint_limit_remains_eight_after_decoding(self):
        urls = ['https://example.invalid/feed-' + str(index) + '.xml' for index in range(10)]
        html = ('<html>' + ''.join('<link type="application/rss+xml" href="' + url + '">' for url in urls) + '</html>').encode()
        source, fetcher, _ = self.probe({HOME: gzip.compress(html), ROBOTS: gzip.compress(ALLOW), **{url: RSS for url in urls}})
        self.assertEqual(fetcher.calls, [HOME, ROBOTS, *urls[:8]])
        self.assertEqual(len(source['endpoints']), 8)

    def test_malformed_truncated_invalid_utf8_and_nested_gzip_root_stop_before_robots(self):
        for body in (b'\x1f\x8binvalid', gzip.compress(HTML)[:-8], gzip.compress(b'<html>\xff</html>'), gzip.compress(gzip.compress(HTML))):
            with self.subTest(body=body), tempfile.TemporaryDirectory() as directory:
                self.store = LocalStore(Path(directory) / 'synthetic-state')
                self.store.compare_and_swap('budget-2026-10-23', None, self.initial)
                self.store.compare_and_swap('latest-run', None, self.sentinel)
                source, fetcher, result = self.probe({HOME: body})
                self.assertEqual(fetcher.calls, [HOME]); self.assertEqual(source['endpoints'], [])
                self.assertIn(source['reason'], ('ValueError', 'UnicodeDecodeError'))
                self.assertFalse(result['budgetDenied'])

    def test_malformed_truncated_invalid_utf8_and_nested_gzip_robots_stop_before_endpoints(self):
        for body in (b'\x1f\x8binvalid', gzip.compress(ALLOW)[:-8], gzip.compress(b'User-agent: *\n\xff'), gzip.compress(gzip.compress(ALLOW))):
            with self.subTest(body=body), tempfile.TemporaryDirectory() as directory:
                self.store = LocalStore(Path(directory) / 'synthetic-state')
                self.store.compare_and_swap('budget-2026-10-23', None, self.initial)
                self.store.compare_and_swap('latest-run', None, self.sentinel)
                source, fetcher, _ = self.probe({HOME: HTML, ROBOTS: body})
                self.assertEqual(fetcher.calls, [HOME, ROBOTS]); self.assertEqual(source['endpoints'], [])
                self.assertIn(source['reason'], ('ValueError', 'UnicodeDecodeError'))

    def test_oversized_root_and_robots_keep_all_charges_without_further_requests(self):
        for location, pages, calls in ((HOME, {HOME: gzip.compress(b'x' * 2048)}, [HOME]),
                                      (ROBOTS, {HOME: HTML, ROBOTS: gzip.compress(b'x' * 2048)}, [HOME, ROBOTS])):
            with self.subTest(location=location), tempfile.TemporaryDirectory() as directory:
                self.store = LocalStore(Path(directory) / 'synthetic-state')
                self.store.compare_and_swap('budget-2026-10-23', None, self.initial)
                self.store.compare_and_swap('latest-run', None, self.sentinel)
                with patch('discovery.MAX_DISCOVERY_BYTES', 256):
                    source, fetcher, _ = self.probe(pages)
                self.assertEqual(fetcher.calls, calls); self.assertEqual(source['endpoints'], [])
                self.assertEqual(source['reason'], 'ContractError')

    def test_bad_compressed_xml_never_earns_an_endpoint_success(self):
        source, fetcher, _ = self.probe({HOME: HTML, ROBOTS: ALLOW, FEED: gzip.compress(RSS)[:-8]})
        self.assertEqual(fetcher.calls, [HOME, ROBOTS, FEED])
        self.assertEqual(source['endpoints'], [{'url': FEED, 'result': 'NOT_DISCOVERY_XML'}])

    def test_compressed_xml_entity_prohibition_and_decoded_size_bound_remain_in_force(self):
        for body in (gzip.compress(b'<!DOCTYPE rss [<!ENTITY bad "injected">]><rss/>'), gzip.compress(b'<rss>' + b'x' * 2048 + b'</rss>')):
            with self.subTest(body=body), tempfile.TemporaryDirectory() as directory:
                self.store = LocalStore(Path(directory) / 'synthetic-state')
                self.store.compare_and_swap('budget-2026-10-23', None, self.initial)
                self.store.compare_and_swap('latest-run', None, self.sentinel)
                with patch('discovery.MAX_DISCOVERY_BYTES', 256):
                    source, fetcher, _ = self.probe({HOME: HTML, ROBOTS: ALLOW, FEED: body})
                self.assertEqual(fetcher.calls, [HOME, ROBOTS, FEED])
                self.assertEqual(source['endpoints'][0]['result'], 'NOT_DISCOVERY_XML')

    def test_ordinary_and_compressed_probes_choose_the_same_endpoints_and_rules(self):
        outcomes = []
        for compress in (lambda body: body, gzip.compress):
            with tempfile.TemporaryDirectory() as directory:
                self.store = LocalStore(Path(directory) / 'synthetic-state')
                self.store.compare_and_swap('budget-2026-10-23', None, self.initial)
                self.store.compare_and_swap('latest-run', None, self.sentinel)
                source, fetcher, _ = self.probe({HOME: compress(HTML), ROBOTS: compress(ALLOW), FEED: compress(RSS)})
                outcomes.append((fetcher.calls, source['reason'], [{key: value for key, value in row.items() if key != 'body'} for row in source['endpoints']]))
        self.assertEqual(outcomes[0], outcomes[1])

    def test_plain_invalid_utf8_keeps_existing_replacement_behavior(self):
        source, fetcher, _ = self.probe({HOME: HTML + b'\xff', ROBOTS: ALLOW + b'# \xff\n', FEED: RSS})
        self.assertEqual(fetcher.calls, [HOME, ROBOTS, FEED])
        self.assertEqual(source['endpoints'][0]['result'], 'DISCOVERY_ENDPOINT_RESPONDED')

    def test_full_5500_ledger_denies_every_compressed_probe_before_transport(self):
        self.initial = {**self.initial, 'fetches': 5500}
        prior = self.store.read('heads/budget-2026-10-23.json')
        self.store.compare_and_swap('budget-2026-10-23', prior, self.initial)
        path = self.store.root / 'heads/budget-2026-10-23.json'; before = path.read_bytes()
        source, fetcher, result = self.probe({HOME: gzip.compress(HTML)})
        self.assertEqual(fetcher.calls, []); self.assertEqual(path.read_bytes(), before)
        self.assertEqual(source['reason'], 'FETCHES_BUDGET_EXHAUSTED')
        self.assertTrue(result['budgetDenied']); self.assertFalse(result['executionCompleted'])

    def test_last_unit_is_charged_for_compressed_root_and_robots_is_not_requested(self):
        self.initial = {**self.initial, 'fetches': 5499}
        prior = self.store.read('heads/budget-2026-10-23.json')
        self.store.compare_and_swap('budget-2026-10-23', prior, self.initial)
        source, fetcher, result = self.probe({HOME: gzip.compress(HTML), ROBOTS: gzip.compress(ALLOW), FEED: RSS})
        self.assertEqual(fetcher.calls, [HOME]); self.assertEqual(fetcher.charged_counts, [5500])
        self.assertEqual(source['reason'], 'FETCHES_BUDGET_EXHAUSTED')
        self.assertTrue(result['budgetDenied']); self.assertFalse(result['executionCompleted'])


if __name__ == '__main__':
    unittest.main()
