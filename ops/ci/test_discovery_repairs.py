"""Offline discovery regressions. Every source/response below is synthetic."""
import copy
import gzip
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))

from contracts import plan_run, validate_contract
from discovery import MAX_DISCOVERY_BYTES, decoded_discovery_body, discover, xml_links


BASE = 'https://orca.security/resources/news/'
ITEM = 'https://orca.security/resources/press-releases/example-release/'
DATA_PATH = '/content/barracuda-corp/us/en/company/news/jcr:content/root/container/container/news_room.news_room.json'


def source(**changes):
    return {'id': 'orca:official:1', 'supplierId': 'orca', 'family': 'official_announcements',
            'kind': 'html_index', 'registration': 'verified', 'url': BASE,
            'allowedHosts': ['orca.security'], 'scopePrefixes': ['/resources'],
            'maxPages': 60, 'required': True, 'htmlCompleteness': 'orca-news-pagination-v1', **changes}


def page_url(number):
    return BASE if number == 1 else f'{BASE}page/{number}/'


def card(url=ITEM, label='Press Releases', day='Oct 22, 2026', featured=False):
    tag = 'article' if featured else 'div'
    classes = 'clickable-card post-card post-card--featured' if featured else 'clickable-card horizontal-post-card horizontal-post-card--large'
    return (f'<{tag} class="{classes}"><p class="post-card__category">{label}</p>'
            f'<h2 class="post-card__title"><a href="{url}">Release title</a></h2>'
            f'<div class="post-card__date">{day}</div></{tag}>')


def page(number=1, next_number=None, last=None, cards=None, head_target=None, class_target=None, controls='', featured=''):
    next_url = page_url(next_number) if next_number else None
    head_target = next_url if head_target is None else head_target
    class_target = next_url if class_target is None else class_target
    head = f'<link rel="next" href="{head_target}">' if head_target else ''
    next_anchor = f'<a class="next page-numbers" href="{class_target}">Next</a>' if class_target else ''
    numbered = f'<a class="page-numbers" href="{page_url(last)}">{last}</a>' if last and last != number else ''
    cards = card() if cards is None else cards
    return (f'<!DOCTYPE html><html><head>{head}</head><body>'
            f'<nav><a href="{BASE}comparisons/">Navigation</a><a href="{ITEM}nav-only/">Not a card</a></nav>'
            f'<div class="newsroom-listing-featured">{featured}</div>'
            '<div class="newsroom-posts"><div class="newsroom-posts-listing">'
            f'<div class="horizontal-post-card-wrap orca-posts-container-newsroom">{cards}</div></div>'
            '<div class="orca-pagination archive-posts-results__show-more">'
            f'<span aria-current="page" class="page-numbers current">{number}</span>{numbered}{next_anchor}{controls}'
            '</div></div></body></html>').encode()


def replay(responses, registered=None):
    requests, observations = [], []
    def request(url):
        requests.append(url)
        if url not in responses:
            return {'status': 'failed', 'errorCode': 'ARCHIVED_PAGE_MISSING', 'requestedUrl': url,
                    'fetchedAt': '2026-10-23T01:00:00Z'}, b''
        observation = {'status': 'fetched', 'requestedUrl': url, 'finalUrl': url,
                       'fetchedAt': '2026-10-23T01:00:00Z', 'body': {'sha256': 'a' * 64}}
        observations.append(copy.deepcopy(observation))
        return observation, responses[url]
    found = discover(registered or source(), request)
    return found, requests, observations


class DiscoveryRepairTests(unittest.TestCase):
    def test_gzip_html_is_classified_after_decoding_and_raw_bytes_stay_unchanged(self):
        raw = gzip.compress(page())
        saved = bytes(raw)
        found, calls, original = replay({BASE: raw})
        self.assertTrue(found['complete'])
        self.assertEqual(found['items'], [ITEM])
        self.assertEqual(raw, saved)
        self.assertEqual(found['observations'], original)

    def test_gzip_xml_and_plain_xml_have_identical_items(self):
        body = b'<urlset><url><loc>https://example.test/news/one</loc></url></urlset>'
        self.assertEqual(xml_links(body, 'https://example.test/'), xml_links(gzip.compress(body), 'https://example.test/'))

    def test_gzip_decoder_rejects_bad_or_truncated_stream(self):
        for value in (b'\x1f\x8bnot-gzip', gzip.compress(b'example')[:-5]):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Invalid compressed'):
                decoded_discovery_body(value)

    def test_decoded_and_uncompressed_bounds_are_enforced(self):
        with patch('discovery.MAX_DISCOVERY_BYTES', 100):
            for value in (b'x' * 101, gzip.compress(b'x' * 101)):
                with self.subTest(compressed=value.startswith(b'\x1f\x8b')), self.assertRaisesRegex(ValueError, 'byte budget'):
                    decoded_discovery_body(value)
            self.assertEqual(len(decoded_discovery_body(gzip.compress(b'x' * 100))), 100)

    def test_actual_32_megabyte_gzip_output_limit_is_enforced(self):
        self.assertEqual(MAX_DISCOVERY_BYTES, 32_000_000)
        oversized = gzip.compress(b'x' * 32_000_001)
        with self.assertRaisesRegex(ValueError, 'byte budget'):
            decoded_discovery_body(oversized)

    def test_xml_entity_prohibition_survives_gzip_decode(self):
        with self.assertRaisesRegex(ValueError, 'entity declarations prohibited'):
            xml_links(gzip.compress(b'<!DOCTYPE urlset><urlset/>'), BASE)

    def test_barracuda_shell_is_incomplete_and_exposes_only_required_data_endpoint(self):
        url = 'https://www.barracuda.com/company/news'
        body = (f'<main><a href="/company/leadership">Navigation</a>'
                '<div data-cmp-is="NewsRoom" class="cmp-news-room">'
                f'<div data-cmp-hook-news-room="cardsContainer" data-panel-endpoint="{DATA_PATH}"></div>'
                '<div>Sorry! No articles could be found with those filters.</div></div></main>').encode()
        registered = source(id='barracuda:official:1', supplierId='barracuda', url=url,
                            allowedHosts=['www.barracuda.com'], scopePrefixes=['/company'],
                            htmlCompleteness='rel-next-exhaustion-v1')
        found, calls, original = replay({url: gzip.compress(body)}, registered)
        self.assertFalse(found['complete'])
        self.assertEqual(found['reason'], 'BARRACUDA_NEWSROOM_DATA_REQUIRED')
        self.assertEqual(found['items'], [])
        self.assertEqual(found['requiredEndpoints'], ['https://www.barracuda.com' + DATA_PATH])
        self.assertEqual(calls, [url])
        self.assertEqual(found['observations'], original)

    def test_barracuda_unknown_layout_cannot_become_quiet(self):
        url = 'https://www.barracuda.com/company/news'
        registered = source(url=url, allowedHosts=['www.barracuda.com'], htmlCompleteness='rel-next-exhaustion-v1')
        found, _, _ = replay({url: b'<main>Static no results text without proved records or pagination.</main>'}, registered)
        self.assertFalse(found['complete'])
        self.assertEqual(found['reason'], 'BARRACUDA_NEWSROOM_LAYOUT_UNVERIFIED')
        self.assertEqual(found['items'], [])

    def test_barracuda_citation_behavior_is_unchanged(self):
        url = 'https://www.barracuda.com/company/news'
        found, _, _ = replay({url: gzip.compress(b'<main>shell</main>')}, source(url=url, kind='citation'))
        self.assertTrue(found['complete'])
        self.assertEqual(found['items'], [])

    def test_orca_two_page_positive_deduplicates_next_controls_and_items(self):
        found, calls, _ = replay({BASE: page(next_number=2, last=2), page_url(2): page(2)})
        self.assertTrue(found['complete'])
        self.assertEqual(calls, [BASE, page_url(2)])
        self.assertEqual(found['items'], [ITEM])
        self.assertEqual(found['itemDates'][ITEM], '2026-10-22')
        self.assertEqual(found['itemModified'][ITEM], '2026-10-22')

    def test_synthetic_quiet_window_keeps_older_dated_cards_after_full_traversal(self):
        older = card(day='Aug 01, 2026')
        found, calls, _ = replay({BASE: page(next_number=2, last=2, cards=older), page_url(2): page(2, cards=older)})
        self.assertTrue(found['complete'])
        self.assertEqual(calls, [BASE, page_url(2)])
        self.assertEqual(found['items'], [ITEM])
        self.assertFalse(any('2026-09-23' <= day <= '2026-10-23' for day in found['itemDates'].values()))

    def test_missing_page_retains_found_items_and_stays_incomplete(self):
        found, calls, _ = replay({BASE: page(next_number=2, last=41)})
        self.assertFalse(found['complete'])
        self.assertEqual(found['reason'], 'ARCHIVED_PAGE_MISSING')
        self.assertEqual(found['items'], [ITEM])
        self.assertEqual(calls, [BASE, page_url(2)])

    def test_missing_page_exception_is_also_incomplete(self):
        def missing(_url):
            raise FileNotFoundError('No archived response')
        found = discover(source(), missing)
        self.assertFalse(found['complete'])
        self.assertEqual(found['reason'], 'ORCA_INDEX_REQUEST_FAILED')

    def test_page_cap_keeps_incomplete(self):
        found, calls, _ = replay({BASE: page(next_number=2, last=2)}, source(maxPages=1))
        self.assertFalse(found['complete'])
        self.assertEqual(found['reason'], 'PAGINATION_BUDGET_EXHAUSTED')
        self.assertEqual(calls, [BASE])

    def test_highest_advertised_page_survives_later_pages(self):
        found, _, _ = replay({BASE: page(next_number=2, last=41), page_url(2): page(2)})
        self.assertFalse(found['complete'])
        self.assertIn('terminal', found['detail'])

    def test_conflicting_or_missing_continuation_is_incomplete(self):
        for head, anchor in ((page_url(2), page_url(3)), (page_url(2), ''), ('', page_url(2))):
            with self.subTest(head=head, anchor=anchor):
                found, calls, _ = replay({BASE: page(head_target=head, class_target=anchor)})
                self.assertFalse(found['complete'])
                self.assertIn('next controls', found['detail'])
                self.assertEqual(calls, [BASE])

    def test_loop_and_skipped_page_are_incomplete(self):
        for target in (BASE, page_url(3)):
            with self.subTest(target=target):
                found, _, _ = replay({BASE: page(head_target=target, class_target=target)})
                self.assertFalse(found['complete'])
                self.assertIn('loop or skipped', found['detail'])

    def test_unsafe_or_unapproved_next_destination_never_gets_requested(self):
        for target in ('https://evil.test/resources/news/page/2/', 'http://orca.security/resources/news/page/2/',
                       'https://orca.security:443/resources/news/page/2/', BASE + '?page=2',
                       'https://orca.security/resources/press-releases/example/', BASE + 'page/2/#part'):
            with self.subTest(target=target):
                found, calls, _ = replay({BASE: page(head_target=target, class_target=target)})
                self.assertFalse(found['complete'])
                self.assertEqual(calls, [BASE])

    def test_unknown_pagination_control_and_dots_cannot_establish_terminal(self):
        for control in ('<button>Load more</button>', '<span class="page-numbers dots">…</span>',
                        '<a href="/unknown">More</a>'):
            with self.subTest(control=control):
                found, _, _ = replay({BASE: page(controls=control)})
                self.assertFalse(found['complete'])

    def test_wrong_current_page_is_incomplete(self):
        found, _, _ = replay({BASE: page(number=2)})
        self.assertFalse(found['complete'])
        self.assertIn('current page mismatch', found['detail'])

    def test_empty_static_or_js_cards_container_cannot_be_quiet(self):
        for cards in ('', '<script>renderCards()</script>', '<template>' + card() + '</template>'):
            with self.subTest(cards=cards):
                found, _, _ = replay({BASE: page(cards=cards)})
                self.assertFalse(found['complete'])
                self.assertIn('no recognized static cards', found['detail'])

    def test_external_news_and_navigation_are_excluded_but_featured_release_is_kept(self):
        featured_url = ITEM.replace('example-release', 'featured-release')
        mixed = card() + card('https://reporter.test/news/story', 'News')
        found, _, _ = replay({BASE: page(cards=mixed, featured=card(featured_url, featured=True))})
        self.assertTrue(found['complete'])
        self.assertEqual(found['items'], sorted([ITEM, featured_url]))

    def test_invalid_release_card_fields_stay_incomplete(self):
        variants = [card('https://evil.test/resources/press-releases/example/'), card(day='not a date'),
                    card(label='Unknown'), card().replace('post-card__date', 'unknown-date'),
                    card().replace('</div></div>', '</div>'),
                    card().replace('<h2 ', '<h2 class="post-card__title">duplicate</h2><h2 ')]
        for cards in variants:
            with self.subTest(cards=cards):
                found, _, _ = replay({BASE: page(cards=cards)})
                self.assertFalse(found['complete'])

    def test_conflicting_duplicate_article_dates_across_pages_are_incomplete(self):
        found, _, _ = replay({BASE: page(next_number=2, last=2), page_url(2): page(2, cards=card(day='Oct 21, 2026'))})
        self.assertFalse(found['complete'])
        self.assertIn('Conflicting Orca dates across pages', found['detail'])

    def test_candidate_registration_does_not_request_any_page(self):
        found, calls, _ = replay({}, source(registration='candidate'))
        self.assertFalse(found['complete'])
        self.assertEqual(found['reason'], 'SOURCE_BINDING_UNVERIFIED')
        self.assertEqual(calls, [])

    def test_explicit_orca_mode_rejects_another_supplier_or_root(self):
        for changes in ({'supplierId': 'different'}, {'url': 'https://orca.security/'}, {'kind': 'official_discovery'}, {'maxPages': 61}):
            registered = source(**changes)
            found, _, _ = replay({registered['url']: page()}, registered)
            self.assertFalse(found['complete'])

    def test_unrecognized_card_or_malformed_external_card_cannot_disappear(self):
        for cards in (card() + '<div>Unrecognized card</div>',
                      card('https://reporter.test/news/story', 'News').replace('post-card__date', 'unknown-date')):
            with self.subTest(cards=cards):
                found, _, _ = replay({BASE: page(cards=cards)})
                self.assertFalse(found['complete'])

    def test_ordinary_registered_html_mode_remains_available(self):
        registered = source(url='https://example.test/news/', allowedHosts=['example.test'], scopePrefixes=['/news/'],
                            htmlCompleteness='rel-next-exhaustion-v1')
        body = b'<main>A sufficiently long ordinary index body with known rel-next exhaustion.<a href="/news/article">Article</a></main>'
        found, _, _ = replay({registered['url']: gzip.compress(body)}, registered)
        self.assertTrue(found['complete'])
        self.assertEqual(found['items'], ['https://example.test/news/article'])

    def test_original_contract_has_74_suppliers_557_obligations_and_28_candidates(self):
        # The original baseline remains fixed when candidates later qualify.
        contract = json.loads((ROOT / 'web/scripts/migration-proofs/daily-v2-original/market.json').read_text())
        validate_contract(contract)
        self.assertEqual(len(contract['suppliers']), 74)
        self.assertEqual(len(plan_run(contract, '2026-10-23T00:00:00Z')['tasks']), 557)
        self.assertEqual(sum(s['registration'] == 'candidate' for s in contract['sources']), 28)
        self.assertFalse(any(s.get('htmlCompleteness') == 'orca-news-pagination-v1' for s in contract['sources']))

    def test_contract_mode_validation_requires_exact_binding(self):
        contract = json.loads((ROOT / 'contracts/market.json').read_text())
        candidate = next(s for s in contract['sources'] if s['id'] == 'orca:official:1')
        candidate.update(kind='html_index', url=BASE, htmlCompleteness='orca-news-pagination-v1')
        validate_contract(contract)
        candidate['url'] = 'https://orca.security/'
        with self.assertRaisesRegex(ValueError, 'Orca HTML mode'):
            validate_contract(contract)


if __name__ == '__main__':
    unittest.main()
