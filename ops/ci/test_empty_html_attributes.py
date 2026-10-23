"""Valueless HTML attributes carry no parser match or publication evidence."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'web/scripts/pipeline'))
from discovery import IndexMarkup, Page


class EmptyHtmlAttributeTests(unittest.TestCase):
    def test_empty_class_keeps_article_readable(self):
        text = 'Retained supplier announcement text. ' * 5
        page = Page('<article class>' + text + '</article>')
        self.assertEqual(page.readable, text.strip())
        self.assertIsNone(page.published)

    def test_empty_relation_does_not_become_next_or_canonical(self):
        page = Page('<main><a rel href="/release">Release</a>'
                    '<link rel href="https://example.invalid/release"></main>')
        self.assertEqual(page.links, [{'url': '/release', 'next': False}])
        self.assertEqual(page.canonicals, [])

    def test_empty_itemprop_supplies_no_publication_date(self):
        page = Page('<article><time itemprop datetime="2026-10-22">Event time</time></article>')
        self.assertIsNone(page.published)
        self.assertFalse(page.published_from_time)

    def test_empty_datetime_supplies_no_publication_date(self):
        page = Page('<article><time itemprop="datePublished" datetime>Unknown</time></article>')
        self.assertIsNone(page.published)
        self.assertFalse(page.published_from_time)

    def test_empty_metadata_does_not_supply_publication(self):
        page = Page('<meta property="article:published_time" content>')
        self.assertFalse(page.published)
        self.assertFalse(page.meta_published)

    def test_normal_publication_metadata_is_unchanged(self):
        page = Page('<meta property="article:published_time" content="2026-10-22">'
                    '<article class><time itemprop="datePublished" datetime="2026-10-21">'
                    'Earlier date</time></article>')
        self.assertEqual(page.published, '2026-10-22')
        self.assertTrue(page.meta_published)
        self.assertFalse(page.published_from_time)

    def test_structural_index_empty_classes_and_relations_are_empty_strings(self):
        nodes = list(IndexMarkup('<main class><a class rel href="/release">Release</a></main>').root.walk())
        main = next(n for n in nodes if n.tag == 'main')
        link = next(n for n in nodes if n.tag == 'a')
        self.assertEqual(main.classes, set())
        self.assertEqual(link.classes, set())
        self.assertEqual(link.attrs['rel'], '')
        self.assertEqual(link.attrs['href'], '/release')

    def test_empty_source_scope_attributes_do_not_match_article_container(self):
        page = Page('<div class id><p>Unscoped text</p></div>',
                    source_url='https://www.esentire.com/news-releases/synthetic')
        self.assertFalse(page.scoped_extraction)
        self.assertEqual(page.scoped_articles, 0)
        self.assertIsNone(page.published)


if __name__ == '__main__':
    unittest.main()
