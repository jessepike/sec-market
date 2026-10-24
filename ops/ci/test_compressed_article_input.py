"""Bounded compressed-input mechanics; no network, subscription or real state."""
import copy
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from contracts import canonical, digest, plan_run
from corrections import validate_sources
from discovery import Page, discover
from documents import article_input, readable_document
from engine import Pipeline
from storage import LocalStore
from validation import REVIEW_CHECKS, reconcile, verify_statement, verified_partial_document_facts
from ops.ci.test_regulatory_collection import NOW, FixtureFetcher, binding, contract

URL = 'https://example.invalid/releases/one'
FEED = 'https://example.invalid/feed.xml'
QUOTE = 'Fixture Vendor raised approximately $10 million on 2026-10-23.'
HTML = ('<html><body><article>' + QUOTE + '</article></body></html>').encode()
QUIET = b'<html><body><article>Fixture Vendor publishes its community calendar and office information for visitors. Details include regular meeting locations and contact instructions for guests.</article></body></html>'


def candidate(quote=QUOTE, day='2026-10-23'):
    return {'supplierId': 'fixture', 'predicate': 'funding', 'valueText': quote, 'quote': quote,
            'effectiveDate': day, 'amount': '10000000', 'currency': 'USD',
            'qualifier': 'approximately', 'eventStatus': 'reported', 'scope': 'company'}


def review(value, observation, policy):
    return {'result': 'accepted', 'candidateSha256': digest(value), 'evidenceSha256': observation['body']['sha256'],
            'policySha256': policy, 'checks': {key: 'pass' for key in REVIEW_CHECKS}}


class FictionalAgent:
    def __init__(self, empty=False):
        self.empty, self.inputs, self.reviews = empty, [], []

    def extract(self, text, supplier):
        self.inputs.append(text)
        return [] if self.empty else [candidate()]

    def review(self, text, value, observation, policy):
        self.reviews.append(text)
        return review(value, observation, policy)

    def review_empty(self, text, supplier, observation, policy):
        self.reviews.append(text)
        return {'noRelevantFacts': True, 'evidenceSha256': observation['body']['sha256'], 'policySha256': policy}


class CompressedArticleInputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(self.temp.name)
        source = binding('fixture', 'direct'); source.pop('regulatoryIssuer')
        source.update(kind='rss', family='official_announcements', url=FEED,
                      allowedHosts=['example.invalid'], scopePrefixes=['/releases/'])
        self.c = contract([source]); self.c['suppliers'][0]['name'] = 'Fixture Vendor'
        self.fetcher = FixtureFetcher(self.store, {FEED: self.feed([URL]), URL: gzip.compress(HTML)})
        self.agent = FictionalAgent()

    @staticmethod
    def feed(urls):
        return ('<rss><channel>' + ''.join('<item><link>' + url + '</link></item>' for url in urls) + '</channel></rss>').encode()

    def run_pipeline(self, force=True, agent=None):
        return Pipeline(self.c, self.store, self.fetcher, agent=agent or self.agent, clock=lambda: NOW).run(NOW, force_refresh=force)

    def validation(self, result):
        return json.loads(self.store.get(result['receipts'][0]['documentValidations'][0]['validation']))

    def observation(self, body=None, url=URL):
        return {'sourceId': self.c['sources'][0]['id'], 'observationId': 'synthetic-observation',
                'requestedUrl': url, 'finalUrl': url, 'fetchedAt': NOW,
                'status': 'fetched', 'body': self.store.put(gzip.compress(HTML) if body is None else body), 'contentType': 'text/html'}

    def rewrite_validation(self, result, mutate):
        receipts = copy.deepcopy(result['receipts'])
        document = receipts[0]['documentValidations'][0]
        value = json.loads(self.store.get(document['validation'])); mutate(value)
        document['validation'] = self.store.put(value)
        return receipts

    def test_compressed_article_extraction_review_and_exact_quote_keep_raw_provenance(self):
        raw = self.fetcher.pages[URL]
        result = self.run_pipeline()
        self.assertTrue(result['complete'], result['receipts'])
        self.assertEqual(self.agent.inputs, [QUOTE])
        self.assertEqual(self.agent.reviews, self.agent.inputs)
        validation = self.validation(result)
        descriptor = validation['compressedInput']
        self.assertEqual(descriptor['rawSha256'], digest(raw))
        self.assertEqual(descriptor['decodedSha256'], digest(HTML))
        self.assertEqual(descriptor['articleSha256'], digest(QUOTE.encode()))
        self.assertEqual(descriptor['modelInputSha256'], digest(QUOTE.encode()))
        self.assertEqual(self.store.get(validation['body']), raw)
        fact = json.loads(self.store.get(validation['factRefs'][0]))
        self.assertEqual(fact['quote'], QUOTE)
        self.assertEqual(fact['evidence'], [validation['body']])
        observed = self.store.read('observations/' + fact['sourceObservationId'] + '.json')
        self.assertEqual(observed['fetchedAt'], NOW)

    def test_plain_input_keeps_cache_key_three_and_record_shape(self):
        self.fetcher.pages[URL] = HTML
        result = self.run_pipeline(); self.assertTrue(result['complete'])
        key = digest({'supplier': 'fixture', 'body': digest(HTML), 'contract': digest(self.c), 'extractor': 3})
        self.assertEqual(self.store.read('document-validation/' + key + '.json'), self.validation(result))
        self.assertNotIn('compressedInput', self.validation(result))
        self.assertNotIn('compressedInput', self.store.read('document-extractions/' + key + '.json'))
        second = FictionalAgent(); self.assertTrue(self.run_pipeline(agent=second)['complete'])
        self.assertEqual(second.inputs, [])
        self.assertEqual(article_input(HTML, self.observation(HTML))['extractor'], 3)

    def test_compressed_cache_preserves_all_three_existing_extractor_bases(self):
        timed = b'<html><article><time itemprop="datePublished" datetime="2026-10-23">Published</time>Fixture Vendor community information</article></html>'
        scoped_url = 'https://www.esentire.com/news-releases/fixture'
        scoped = b'<html><div class="BlogBody__Content">Fixture Vendor article content.</div></html>'
        for html, url, expected in ((HTML, URL, 3), (timed, URL, 4), (scoped, scoped_url, 5)):
            with self.subTest(expected=expected):
                plain = article_input(html, self.observation(html, url))
                compressed = article_input(gzip.compress(html), self.observation(gzip.compress(html), url))
                self.assertEqual(plain['extractor'], expected)
                self.assertEqual(compressed['extractor']['extractor'], expected)
                self.assertEqual(compressed['compressedInput']['extractor'], expected)
                self.assertEqual(plain['modelText'], compressed['modelText'])
                self.assertNotEqual(plain['extractor'], compressed['extractor'])

    def test_same_compressed_bytes_at_different_urls_cannot_share_scoped_cache_identity(self):
        raw = gzip.compress(HTML)
        a = article_input(raw, self.observation(raw))
        b = article_input(raw, self.observation(raw, URL + '-different'))
        self.assertNotEqual(a['extractor'], b['extractor'])
        self.assertNotEqual(a['compressedInput'], b['compressedInput'])

    def test_compressed_statement_date_uses_same_publication_metadata_view(self):
        quote = 'Fixture Vendor appointed Alex as its chief executive officer.'
        html = ('<html><article><time itemprop="datePublished" datetime="2026-10-23">Published</time>' + quote + '</article></html>').encode()
        observed = self.observation(gzip.compress(html))
        value = {**candidate(quote), 'predicate': 'leadership_change', 'amount': None, 'currency': None, 'qualifier': 'exact'}
        fact = verify_statement(value, observed, self.store, review(value, observed, digest(self.c)), self.c['suppliers'][0], digest(self.c))
        self.assertEqual(fact['effectiveDate'], '2026-10-23')
        value['effectiveDate'] = '2026-10-22'
        with self.assertRaisesRegex(ValueError, 'date not grounded'):
            verify_statement(value, observed, self.store, review(value, observed, digest(self.c)), self.c['suppliers'][0], digest(self.c))

    def test_source_scoping_preserves_exclusion_of_unrelated_sidebar_quote(self):
        url = 'https://www.esentire.com/news-releases/fixture'
        html = ('<html><aside>' + QUOTE + '</aside><div class="BlogBody__Content">Only community information appears in this article.</div></html>').encode()
        observed = self.observation(gzip.compress(html), url)
        self.assertNotIn(QUOTE, article_input(self.store.get(observed['body']), observed)['modelText'])
        value = candidate()
        with self.assertRaisesRegex(ValueError, 'source excerpt missing'):
            verify_statement(value, observed, self.store, review(value, observed, digest(self.c)), self.c['suppliers'][0], digest(self.c))

    def test_statement_verification_preserves_html_nonhtml_date_evidence_parity(self):
        quote = 'Fixture Vendor appointed Alex as its chief executive officer.'
        html = ('<html><article><time itemprop="datePublished" datetime="2026-10-23">Published</time>' + quote + '</article></html>').encode()
        value = {**candidate(quote), 'predicate': 'leadership_change', 'amount': None, 'currency': None, 'qualifier': 'exact'}
        for body in (html, gzip.compress(html)):
            for content_type in ('text/html', 'application/octet-stream'):
                with self.subTest(compressed=body != html, content_type=content_type):
                    observed = {**self.observation(body), 'contentType': content_type}
                    if 'html' in content_type:
                        checked = verify_statement(value, observed, self.store, review(value, observed, digest(self.c)), self.c['suppliers'][0], digest(self.c))
                        self.assertEqual(checked['effectiveDate'], '2026-10-23')
                    else:
                        with self.assertRaisesRegex(ValueError, 'date not grounded'):
                            verify_statement(value, observed, self.store, review(value, observed, digest(self.c)), self.c['suppliers'][0], digest(self.c))

    def test_compressed_empty_review_records_and_replays_actual_input(self):
        self.fetcher.pages[URL] = gzip.compress(QUIET); self.agent = FictionalAgent(empty=True)
        result = self.run_pipeline(); self.assertTrue(result['complete'], result['receipts'])
        validation = self.validation(result)
        self.assertIn('compressedInput', validation)
        self.assertEqual(validation['candidateHashes'], [])
        self.assertEqual(len(self.agent.inputs), 1)
        self.assertEqual(self.agent.inputs, self.agent.reviews)
        self.assertTrue(reconcile(plan_run(self.c, NOW), result['receipts'], self.c, NOW, self.store)['complete'])

    def test_compressed_empty_extraction_cannot_hide_decoded_business_signal(self):
        self.agent = FictionalAgent(empty=True)
        result = self.run_pipeline()
        self.assertFalse(result['complete'])
        self.assertIn('EMPTY_EXTRACTION_WITH_BUSINESS_SIGNAL', result['receipts'][0]['errorCode'])
        self.assertNotIn('documentValidations', result['receipts'][0])

    def test_compressed_shared_publisher_exclusion_has_descriptor_and_zero_agent_calls(self):
        self.c['sources'][0]['family'] = 'investor_acquirer'
        self.c['suppliers'][0]['requiredFamilies'] = ['investor_acquirer']
        unrelated = QUIET.replace(b'Fixture Vendor', b'Other Company')
        self.fetcher.pages[URL] = gzip.compress(unrelated)
        result = self.run_pipeline(); self.assertTrue(result['complete'], result['receipts'])
        validation = self.validation(result)
        self.assertEqual(validation['exclusionRule'], 'no-registered-entity-mention-v1')
        self.assertIn('compressedInput', validation)
        self.assertEqual(self.agent.inputs, [])
        receipts = self.rewrite_validation(result, lambda v: v.pop('compressedInput'))
        with self.assertRaisesRegex(ValueError, 'COMPRESSED_ARTICLE_INPUT'):
            reconcile(plan_run(self.c, NOW), receipts, self.c, NOW, self.store)

    def test_malformed_truncated_and_invalid_utf8_gzip_fail_before_agent_or_document_reservation(self):
        for body in (b'\x1f\x8bnot-a-gzip', gzip.compress(HTML)[:-8], gzip.compress(b'<html>\xff\xfe</html>')):
            with self.subTest(body=body):
                self.fetcher.pages[URL] = body
                result = self.run_pipeline()
                self.assertFalse(result['complete'])
                self.assertEqual(self.agent.inputs, [])
                self.assertNotIn('documentValidations', result['receipts'][0])
                self.assertEqual(self.store.read('heads/budget-2026-10-23.json')['documents'], 0)

    def test_oversized_decoded_article_fails_before_agent_and_retains_original_evidence(self):
        raw = gzip.compress(b'<html>' + b'x' * 2000 + b'</html>'); self.fetcher.pages[URL] = raw
        with patch('discovery.MAX_DISCOVERY_BYTES', 512):
            result = self.run_pipeline()
        self.assertFalse(result['complete'])
        self.assertEqual(self.agent.inputs, [])
        self.assertIn('byte budget', result['receipts'][0]['errorCode'])
        observed = self.store.read('observations/' + result['receipts'][0]['observationIds'][-1] + '.json')
        self.assertEqual(self.store.get(observed['body']), raw)

    def test_old_compressed_extraction_validation_and_review_cache_are_not_reused(self):
        raw = self.fetcher.pages[URL]
        old_page = Page(raw.decode('utf8', errors='replace'), source_url=URL)
        old_base = 5 if old_page.scoped_extraction else 4 if old_page.published_from_time else 3
        old_key = digest({'supplier': 'fixture', 'body': digest(raw), 'contract': digest(self.c), 'extractor': old_base})
        observed = self.observation(raw)
        legacy = {'supplierId': 'fixture', 'body': observed['body'], 'contractSha256': digest(self.c),
                  'candidateHashes': [], 'factRefs': [], 'heldClaims': [], 'emptyReview': self.store.put({'noRelevantFacts': True})}
        self.store.write_once('document-validation/' + old_key + '.json', legacy)
        self.store.write_once('document-extractions/' + old_key + '.json', {'candidates': []})
        self.store.write_once('document-reservations/2026-10-23/' + old_key + '.json', {'cacheKey': old_key})
        self.store.compare_and_swap('budget-2026-10-23', None, {'calls': 7, 'documents': 8, 'fetches': 2, 'other': 99})
        result = self.run_pipeline(); self.assertTrue(result['complete'])
        self.assertEqual(self.agent.inputs, [QUOTE])
        self.assertIn('compressedInput', self.validation(result))
        self.assertEqual(self.store.read('document-validation/' + old_key + '.json'), legacy)
        self.assertEqual(self.store.read('heads/budget-2026-10-23.json'), {'calls': 7, 'documents': 9, 'fetches': 4, 'other': 99})

    def test_full_replay_rejects_absent_or_altered_descriptor_fields(self):
        result = self.run_pipeline()
        mutations = [lambda v: v.pop('compressedInput')]
        for key in self.validation(result)['compressedInput']:
            mutations.append(lambda v, key=key: v['compressedInput'].update({key: 'forged'}))
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                receipts = self.rewrite_validation(result, mutate)
                with self.assertRaisesRegex(ValueError, 'COMPRESSED_ARTICLE_INPUT'):
                    reconcile(plan_run(self.c, NOW), receipts, self.c, NOW, self.store)

    def test_same_day_reuse_rejects_legacy_successful_receipt_and_checks_decoded_input(self):
        result = self.run_pipeline()
        receipts = self.rewrite_validation(result, lambda v: v.pop('compressedInput'))
        legacy_receipt = receipts[0]
        # Coherent synthetic legacy seal, rather than an unrelated integrity failure.
        attempt = 'runs/' + legacy_receipt['runId'] + '/attempts/' + legacy_receipt['attemptId'] + '.json'
        self.store._path(attempt).write_bytes(canonical(legacy_receipt))
        seal = 'receipt-integrity/' + legacy_receipt['runId'] + '/' + legacy_receipt['taskId'] + '/' + legacy_receipt['attemptId'] + '.json'
        self.store._path(seal).write_bytes(canonical(self.store.put(legacy_receipt)))
        latest = self.store.read('heads/latest-run.json')
        self.store.compare_and_swap('latest-run', latest, {'runId': legacy_receipt['runId'], 'receipt': self.store.put({**result, 'receipts': receipts})})
        for path in (self.store.root / 'document-validation').glob('*.json'): path.unlink()
        for path in (self.store.root / 'document-extractions').glob('*.json'): path.unlink()
        second = FictionalAgent(); fresh = self.run_pipeline(force=False, agent=second)
        self.assertTrue(fresh['complete'], fresh['receipts'])
        self.assertNotEqual(fresh['receipts'][0]['attemptId'], legacy_receipt['attemptId'])
        self.assertEqual(second.inputs, [QUOTE])

    def test_partial_fact_release_requires_the_same_compressed_input_descriptor(self):
        second = URL + '-two'; self.fetcher.pages[FEED] = self.feed([URL, second]); self.fetcher.pages[second] = 403
        result = self.run_pipeline(); self.assertFalse(result['complete'])
        plan = plan_run(self.c, NOW)
        self.assertEqual(len(verified_partial_document_facts(plan, result, self.c, NOW, self.store)), 1)
        for mutate in (lambda v: v.pop('compressedInput'), lambda v: v['compressedInput'].update(extractor=999)):
            receipts = self.rewrite_validation(result, mutate)
            with self.assertRaisesRegex(ValueError, 'COMPRESSED_ARTICLE_INPUT'):
                reconcile(plan, receipts, self.c, NOW, self.store)
            with self.assertRaisesRegex(ValueError, 'COMPRESSED_ARTICLE_INPUT'):
                verified_partial_document_facts(plan, {'receipts': receipts}, self.c, NOW, self.store)

    def test_legacy_compressed_audit_url_becomes_due_without_resetting_plain_history(self):
        plain = URL + '-plain'; self.fetcher.pages[FEED] = self.feed([URL, plain]); self.fetcher.pages[plain] = QUIET
        self.c['collection'] = {'mode': 'delta_with_retained_audit', 'currentWindowDays': 30,
                                'maxDocumentsPerSource': 1, 'maxAuditDocumentsPerSource': 1}
        source_id = self.c['sources'][0]['id']
        old = {'modified': '', 'checkedAt': NOW}
        audit = {'documents': {URL: dict(old), plain: dict(old)}, 'contractSha256': digest(self.c)}
        self.store.compare_and_swap('audit-' + digest(source_id), None, audit)
        observed = self.observation()
        self.store.compare_and_swap('download-' + digest({'source': source_id, 'url': URL}), None, observed)
        result = self.run_pipeline()
        self.assertEqual(self.agent.inputs, [QUOTE])
        self.assertFalse(result['complete'])
        # The plain cursor has no anchored document proof. It stays unchanged
        # as history, while the actual unresolved URL now remains due.
        self.assertEqual(result['receipts'][0]['errorCode'], 'HISTORICAL_OR_UNCHANGED_AUDIT_PENDING')
        self.assertEqual(result['receipts'][0].get('retainedAuditDocuments', 0), 0)
        self.assertEqual(result['receipts'][0]['pendingDocuments'], 1)
        pending = json.loads(self.store.get(result['receipts'][0]['pendingManifest']))
        self.assertEqual(pending['items'], [plain])
        self.assertIsNone(self.store.read('heads/source-' + digest(source_id) + '.json'))
        new = self.store.read('heads/audit-' + digest(source_id) + '.json')
        self.assertEqual(new['documents'][plain], old)
        self.assertEqual(new['documents'][URL]['compressedInput'], self.validation(result)['compressedInput'])
        self.assertEqual(new['documents'][URL]['body'], observed['body'])
        again = FictionalAgent(); repeated = self.run_pipeline(agent=again)
        self.assertEqual(again.inputs, [article_input(QUIET, {'requestedUrl': plain})['modelText']])
        self.assertTrue(repeated['complete'], repeated['receipts'])
        self.assertEqual(repeated['receipts'][0]['retainedAuditDocuments'], 1)
        self.assertEqual(repeated['receipts'][0].get('pendingDocuments', 0), 0)
        self.assertIsNone(repeated['receipts'][0]['errorCode'])
        self.assertIsNotNone(self.store.read('heads/source-' + digest(source_id) + '.json'))

    def test_correction_source_quotes_use_bounded_decoded_text_and_keep_raw_reference(self):
        text = QUOTE + ' Independent fictional source details support this exact dated announcement.'
        raw = gzip.compress(('<html><body><article>' + text + '</article></body></html>').encode())
        observed = self.observation(raw); self.store.write_once('observations/' + observed['observationId'] + '.json', observed)
        bound = {'observationId': observed['observationId'], 'sourceId': observed['sourceId'], 'url': URL,
                 'body': observed['body'], 'fetchedAt': NOW, 'evidenceId': 'E'}
        group = {'sources': [bound], 'targets': [{'targetId': 'evidence:E', 'proposedValue': {'id': 'E', 'excerpt': QUOTE}}]}
        documents = validate_sources(group, self.store, self.c, NOW)
        self.assertEqual(documents[0]['text'], text)
        self.assertEqual(documents[0]['source']['body'], observed['body'])
        group['targets'][0]['proposedValue']['excerpt'] = 'An invented source excerpt.'
        with self.assertRaisesRegex(ValueError, 'not literally'): validate_sources(group, self.store, self.c, NOW)
        group['targets'] = []
        small = copy.deepcopy(self.c); small['model']['maxDocumentChars'] = 100
        with self.assertRaisesRegex(ValueError, 'exceeds limit'): validate_sources(group, self.store, small, NOW)

    def test_primary_document_decodes_before_html_and_pdf_detection(self):
        self.assertEqual(readable_document(gzip.compress(QUIET)), readable_document(QUIET))
        pdf = b'%PDF-1.7\nfictional bytes for detection only'
        def decode_pdf(args, **kwargs):
            self.assertEqual(Path(args[-2]).read_bytes(), pdf)
            Path(args[-1]).write_text('Fictional PDF retained text. ' * 10)
            return subprocess.CompletedProcess(args, 0)
        with patch('documents.subprocess.run', side_effect=decode_pdf) as runner:
            text = readable_document(gzip.compress(pdf))
        self.assertIn('Fictional PDF retained text.', text); runner.assert_called_once()

    def test_bad_or_oversized_primary_input_fails_before_pdf_execution(self):
        with patch('documents.subprocess.run') as runner:
            with self.assertRaises(ValueError): readable_document(b'\x1f\x8bbad', 'application/pdf')
            with patch('discovery.MAX_DISCOVERY_BYTES', 64):
                with self.assertRaises(ValueError): readable_document(gzip.compress(b'%PDF-' + b'x' * 100))
            with self.assertRaises(UnicodeDecodeError): readable_document(gzip.compress(b'<html>' + b'\xff' * 100 + b'</html>'))
            with self.assertRaises(UnicodeDecodeError): readable_document(gzip.compress(gzip.compress(QUIET)))
        runner.assert_not_called()

    def test_compressed_barracuda_shell_remains_incomplete_discovery(self):
        url = 'https://www.barracuda.com/company/news'
        endpoint = 'https://www.barracuda.com/content/barracuda-corp/us/en/company/news/jcr:content/root/container/container/news_room.news_room.json'
        body = ('<html><div class="cmp-news-room" data-cmp-is="NewsRoom"><div data-cmp-hook-news-room="cardsContainer" data-panel-endpoint="'
                + endpoint + '"></div></div></html>').encode()
        registered = {**self.c['sources'][0], 'kind': 'html_index', 'url': url,
                      'allowedHosts': ['www.barracuda.com'], 'scopePrefixes': ['/company'],
                      'htmlCompleteness': 'rel-next-exhaustion-v1'}
        raw = gzip.compress(body)
        found = discover(registered, lambda requested: ({'requestedUrl': requested, 'status': 'fetched', 'fetchedAt': NOW}, raw))
        self.assertFalse(found['complete'])
        self.assertEqual(found['items'], [])
        self.assertEqual(found['reason'], 'BARRACUDA_NEWSROOM_DATA_REQUIRED')
        self.assertEqual(found['requiredEndpoints'], [endpoint])

    def test_legacy_compressed_empty_review_cannot_supply_partial_work(self):
        self.fetcher.pages[URL] = gzip.compress(QUIET); self.agent = FictionalAgent(empty=True)
        result = self.run_pipeline()
        receipts = self.rewrite_validation(result, lambda v: v.pop('compressedInput'))
        receipts[0].update(outcome='not_checked', discoveryComplete=True)
        with self.assertRaisesRegex(ValueError, 'COMPRESSED_ARTICLE_INPUT'):
            verified_partial_document_facts(plan_run(self.c, NOW), {'receipts': receipts}, self.c, NOW, self.store)


if __name__ == '__main__':
    unittest.main()
