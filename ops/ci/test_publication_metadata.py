"""Source-scoped archived publication metadata, not generic WebPage trust."""
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from discovery import Page
from contracts import digest
from engine import Pipeline
from storage import LocalStore
sys.path.insert(0, str(ROOT / 'web/tests'))
from test_pipeline import contract, FakeFetcher, FakeAgent, T

FIXTURES = Path(__file__).parent / 'fixtures/esentire-publication'
CEO_URL = 'https://www.esentire.com/news-releases/esentire-appoints-cybersecurity-industry-veteran-james-c-foster-as-chief-executive-officer'
CONFLICT_URL = 'https://www.esentire.com/news-releases/esentire-advances-controlled-autonomy-secops-with-agentic-ai-that-preempts-detects-and-responds-in-a-single-unified-platform'


class PublicationMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ceo = (FIXTURES / 'ceo.html').read_text()
        cls.conflict = (FIXTURES / 'autonomy-conflict.html').read_text()

    def mutate_node(self, change):
        # Change only the real WebPage JSON-LD; canonical/body stay fixed.
        def replace(match):
            node = json.loads(match.group(2))
            graph = node.get('@graph', [])
            page = next((item for item in graph if item.get('@type') == 'WebPage'), None)
            if page:
                change(page, graph)
                return match.group(1) + json.dumps(node) + match.group(3)
            return match.group(0)
        return re.sub(r'(<script[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)', replace, self.ceo, flags=re.S)

    def test_fixtures_are_exact_archived_bytes(self):
        for item in json.loads((FIXTURES / 'provenance.json').read_text())['fixtures']:
            raw = (FIXTURES / item['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), item['originalBodySha256'])
            self.assertEqual(len(raw), item['bytes'])

    def test_actual_ceo_article_date_and_body_exclude_related_acquisition(self):
        page = Page(self.ceo, source_url=CEO_URL)
        self.assertEqual(page.published, '2026-03-19T01:00:00-04:00')
        self.assertTrue(page.scoped_extraction)
        self.assertIn('James C. Foster', page.readable)
        self.assertIn('Kerry Bailey', page.readable)
        self.assertNotIn('Acquires Stealth-Mode AI Security Startup', page.readable)
        self.assertNotIn('Resources__Eyebrow', page.readable)

    def test_actual_conflicting_dateline_keeps_publication_unknown(self):
        page = Page(self.conflict, source_url=CONFLICT_URL)
        self.assertIsNone(page.published)
        self.assertTrue(page.publication_ambiguous)
        self.assertTrue(page.scoped_extraction)
        self.assertIn('May 27, 2026', page.readable)
        self.assertIn('Ilan Mindel', page.readable)
        self.assertNotIn('Acquires Stealth-Mode AI Security Startup', page.readable)

    def test_no_source_url_does_not_trust_webpage_or_change_old_cache_input(self):
        page = Page(self.ceo)
        self.assertIsNone(page.published)
        self.assertFalse(page.scoped_extraction)

    def test_wrong_observed_url_cannot_borrow_canonical_date(self):
        self.assertIsNone(Page(self.ceo, source_url=CEO_URL + '-different').published)
        self.assertIsNone(Page(self.ceo, source_url=CEO_URL.replace('www.esentire.com', 'other.example')).published)
        self.assertIsNone(Page(self.ceo, source_url=CEO_URL.replace('/news-releases/', '/blog/')).published)

    def test_wrong_node_identity_and_multiple_nodes_rejected(self):
        for field in ('url', 'mainEntityOfPage'):
            html = self.mutate_node(lambda page, graph: page.update({field: CEO_URL + '-other'}))
            self.assertIsNone(Page(html, source_url=CEO_URL).published)
        html = self.mutate_node(lambda page, graph: graph.append(copy.deepcopy(page)))
        self.assertIsNone(Page(html, source_url=CEO_URL).published)

    def test_future_invalid_and_modified_only_dates_rejected(self):
        for value in ('2099-03-19T01:00:00-04:00', '2026-02-31T01:00:00Z', 'not-a-date'):
            html = self.mutate_node(lambda page, graph: page.update(datePublished=value))
            if value.startswith('2099'):
                # Match the dateline so the future-date guard itself is exercised.
                html = html.replace('March 19, 2026', 'March 19, 2099')
            self.assertIsNone(Page(html, source_url=CEO_URL).published)
        html = self.mutate_node(lambda page, graph: page.pop('datePublished'))
        self.assertIsNone(Page(html, source_url=CEO_URL).published)

    def test_wrong_canonical_multiple_canonicals_and_arbitrary_time_rejected(self):
        html = self.ceo.replace('href="' + CEO_URL + '" rel="canonical"', 'href="https://www.esentire.com/news-releases/other" rel="canonical"')
        self.assertIsNone(Page(html, source_url=CEO_URL).published)
        html = self.ceo + '<link rel="canonical" href="' + CEO_URL + '">'
        self.assertIsNone(Page(html, source_url=CEO_URL).published)
        html = self.mutate_node(lambda page, graph: page.pop('datePublished')) + '<time datetime="2026-03-19">Event date</time>'
        self.assertIsNone(Page(html, source_url=CEO_URL).published)

    def test_exact_article_class_does_not_match_left_or_right(self):
        html = self.ceo.replace('class="BlogBody__Content"', 'class="BlogBody__ContentRight"')
        page = Page(html, source_url=CEO_URL)
        self.assertFalse(page.scoped_extraction)
        self.assertIsNone(page.published)

    def test_other_article_and_mimecast_cache_inputs_unchanged(self):
        article = '<article><p>' + 'Existing article body. ' * 10 + '</p></article><meta property="article:published_time" content="2026-03-19T00:00:00Z">'
        page = Page(article, source_url='https://example.com/article')
        self.assertEqual(page.published, '2026-03-19T00:00:00Z')
        self.assertFalse(page.scoped_extraction)

    def test_real_scoped_article_reextracts_version_three_but_preserves_old_hold(self):
        with tempfile.TemporaryDirectory() as directory:
            store = LocalStore(Path(directory))
            policy = contract()
            policy['suppliers'][0]['name'] = 'eSentire'
            source = policy['sources'][0]
            source.update(url='https://www.esentire.com/feed.xml', allowedHosts=['www.esentire.com'], scopePrefixes=['/news-releases/'])
            html = self.ceo.encode()
            old_key = digest(dict(supplier='fixture', body=digest(html), contract=digest(policy), extractor=3))
            old_hold = store.put({'fixture': 'old held claim remains untouched'})
            old_validation = dict(supplierId='fixture', body=store.put(html), contractSha256=digest(policy), candidateHashes=[], factRefs=[], heldClaims=[old_hold])
            store.write_once('document-validation/' + old_key + '.json', old_validation)
            pages = {source['url']: ('<rss><channel><item><link>' + CEO_URL + '</link></item></channel></rss>').encode(), CEO_URL: html}
            agent = FakeAgent(empty=True)
            def extract(text, supplier):
                agent.calls += 1
                self.assertIn('Source publication date metadata: 2026-03-19', text)
                self.assertNotIn('Acquires Stealth-Mode AI Security Startup', text)
                statement = 'appointment of James C. Foster as Chief Executive Officer'
                self.assertIn(statement, text)
                return [dict(supplierId='fixture', predicate='leadership_change', valueText=statement, quote=statement,
                             effectiveDate='2026-03-19', amount=None, currency=None, qualifier='exact', eventStatus='announced', scope='company')]
            agent.extract = extract
            result = Pipeline(policy, store, FakeFetcher(store, pages), agent, clock=lambda: T).run(T)
            self.assertTrue(result['complete'], result)
            self.assertEqual(agent.calls, 2)
            self.assertEqual(store.read('document-validation/' + old_key + '.json'), old_validation)
            new_key = digest(dict(supplier='fixture', body=digest(html), contract=digest(policy), extractor=5))
            self.assertIsNotNone(store.read('document-validation/' + new_key + '.json'))
            Pipeline(policy, store, FakeFetcher(store, pages), agent, clock=lambda: T).run(T, force_refresh=True)
            self.assertEqual(agent.calls, 2)
        mimecast = '<main><div class="press-release-details__date"><time datetime="2025-12-10">Dec 10</time></div><p>' + 'Mimecast article body. ' * 10 + '</p></main>'
        page = Page(mimecast, source_url='https://www.mimecast.com/resources/press-releases/apac-expansion/')
        self.assertEqual(page.published, '2025-12-10')
        self.assertTrue(page.published_from_time)
        self.assertFalse(page.scoped_extraction)


if __name__ == '__main__':
    unittest.main()
