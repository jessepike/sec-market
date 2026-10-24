"""Portable XML grammar fixtures; no archived source or transport dependency."""
import gzip
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'web/scripts/pipeline'))
from contracts import ContractError
import discovery

BASE = 'https://example.invalid/feed/'
ERROR = 'XML entity declarations prohibited'


class XmlDoctypeGuardTests(unittest.TestCase):
    def rejected_doctype(self, text, encoding='utf-8'):
        with self.assertRaisesRegex(ContractError, '^' + ERROR + '$'):
            discovery.xml_links(text.encode(encoding), BASE)

    def test_html_doctype_inside_rss_cdata_is_text(self):
        body = (b'<rss xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel><item>'
                b'<link>https://example.invalid/news/one</link><pubDate>Thu, 22 Oct 2026 17:21:30 +0000</pubDate>'
                b'<content:encoded><![CDATA[<!DOCTYPE html PUBLIC "example" "https://example.invalid/html.dtd">'
                b'<html><body>Article text</body></html>]]></content:encoded></item></channel></rss>')
        self.assertEqual(discovery.xml_links(body, BASE), {'kind': 'rss',
            'links': ['https://example.invalid/news/one'], 'indexes': [], 'modified': {}})

    def test_entity_shaped_text_inside_cdata_is_not_expanded(self):
        body = b'<rss><channel><![CDATA[<!ENTITY x SYSTEM "file:///unread"> &x;]]></channel></rss>'
        self.assertEqual(discovery.xml_links(body, BASE)['links'], [])

    def test_declaration_shaped_comment_is_inert(self):
        self.assertEqual(discovery.xml_links(b'<rss><!-- <!DOCTYPE rss> --><channel/></rss>', BASE)['kind'], 'rss')

    def test_declaration_shaped_processing_instruction_is_inert(self):
        self.assertEqual(discovery.xml_links(b'<rss><?example <!DOCTYPE rss> ?><channel/></rss>', BASE)['kind'], 'rss')

    def test_external_dtd_utf8_rejected(self):
        self.rejected_doctype('<!DOCTYPE rss SYSTEM "file:///unread"><rss/>')

    def test_external_dtd_utf16_rejected(self):
        self.rejected_doctype('<!DOCTYPE rss SYSTEM "https://example.invalid/unread"><rss/>', 'utf-16')

    def test_internal_entity_utf8_rejected(self):
        self.rejected_doctype('<!DOCTYPE rss [<!ENTITY x "expand">]><rss>&x;</rss>')

    def test_internal_entity_utf16_rejected(self):
        self.rejected_doctype('<!DOCTYPE rss [<!ENTITY x "expand">]><rss>&x;</rss>', 'utf-16')

    def test_parameter_entity_utf8_rejected(self):
        self.rejected_doctype('<!DOCTYPE rss [<!ENTITY % x SYSTEM "file:///unread">%x;]><rss/>')

    def test_parameter_entity_utf16_rejected(self):
        self.rejected_doctype('<!DOCTYPE rss [<!ENTITY % x SYSTEM "file:///unread">%x;]><rss/>', 'utf-16')

    def test_bare_doctype_utf8_rejected(self):
        self.rejected_doctype('<!DOCTYPE rss><rss/>')

    def test_bare_doctype_utf16_rejected(self):
        self.rejected_doctype('<!DOCTYPE rss><rss/>', 'utf-16')

    def test_standalone_entity_declaration_rejected(self):
        with self.assertRaises(ET.ParseError):
            discovery.xml_links(b'<!ENTITY x "expand"><rss/>', BASE)

    def test_undefined_entity_rejected(self):
        with self.assertRaises(ET.ParseError):
            discovery.xml_links(b'<rss>&undefined;</rss>', BASE)

    def test_malformed_cdata_rejected(self):
        with self.assertRaises(ET.ParseError):
            discovery.xml_links(b'<rss><![CDATA[<!DOCTYPE rss></rss>', BASE)

    def test_html_challenge_is_not_discovery_xml(self):
        with self.assertRaisesRegex(ValueError, 'Unsupported XML discovery format'):
            discovery.xml_links(b'<html><body>Challenge</body></html>', BASE)

    def test_expansion_is_rejected_before_document_text_delivery(self):
        delivered = []
        original = ET.TreeBuilder
        class TrackingTreeBuilder(original):
            def data(self, value):
                delivered.append(value)
                return super().data(value)
        definitions = ['<!ENTITY e0 "expand">']
        for i in range(1, 13):
            definitions.append('<!ENTITY e' + str(i) + ' "' + ('&e' + str(i - 1) + ';') * 10 + '">')
        text = '<!DOCTYPE rss [' + ''.join(definitions) + ']><rss>&e12;</rss>'
        with patch.object(discovery.ET, 'TreeBuilder', TrackingTreeBuilder):
            self.rejected_doctype(text)
        self.assertEqual(delivered, [])

    def test_decoded_byte_limit_remains_before_xml_parsing(self):
        with patch.object(discovery, 'MAX_DISCOVERY_BYTES', 16):
            with self.assertRaisesRegex(ValueError, 'Decoded discovery body exceeds byte budget'):
                discovery.xml_links(b'<rss><channel/></rss>', BASE)

    def test_gzip_dtd_stays_rejected_after_bounded_decoding(self):
        with self.assertRaisesRegex(ContractError, '^' + ERROR + '$'):
            discovery.xml_links(gzip.compress(b'<!DOCTYPE rss><rss/>'), BASE)

    def test_existing_rss_atom_and_sitemap_extraction_is_unchanged(self):
        self.assertEqual(discovery.xml_links(b'<rss><channel><item><link>/news/a</link></item></channel></rss>', BASE),
            {'kind': 'rss', 'links': ['https://example.invalid/news/a'], 'indexes': [], 'modified': {}})
        self.assertEqual(discovery.xml_links(b'<feed><link rel="next" href="page2"/><entry><link href="/news/a"/></entry></feed>', BASE),
            {'kind': 'feed', 'links': ['https://example.invalid/news/a'], 'indexes': [BASE + 'page2'], 'modified': {}})
        self.assertEqual(discovery.xml_links(b'<urlset><url><loc>/news/a</loc><lastmod>2026-10-22</lastmod></url></urlset>', BASE),
            {'kind': 'urlset', 'links': ['https://example.invalid/news/a'], 'indexes': [],
             'modified': {'https://example.invalid/news/a': '2026-10-22'}})


if __name__ == '__main__':
    unittest.main()
