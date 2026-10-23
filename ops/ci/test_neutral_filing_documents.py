"""Issuer-bound, zero-fact filing retention using fictional transport only."""
import copy
import gzip
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from contracts import digest, plan_run, validate_contract
from discovery import discover
from engine import Pipeline
from regulatory import SEC_FILING_FORMS, verify_filing_index_documents
from storage import LocalStore
from validation import eligible_fact_references, reconcile, verified_partial_document_facts
from ops.ci.test_regulatory_collection import (NOW, CIK, INDEX, ARCHIVE, FixtureFetcher,
                                                binding, contract, initial, row, table)

BODY = b'<html><main>' + b'Original fictional issuer filing retained for independent readable body verification. ' * 5 + b'</main></html>'


def source(subject='segment-a', relationship='parent'):
    return {**binding(subject, relationship), 'kind': 'sec_documents', 'family': 'filing_documents',
            'cik': CIK, 'allowedHosts': ['data.sec.gov', 'www.sec.gov']}


def filing_url(filing=None):
    filing = filing or row()
    return ('https://www.sec.gov/Archives/edgar/data/' + str(int(CIK)) + '/'
            + filing['accessionNumber'].replace('-', '') + '/' + filing['primaryDocument'])


class NeutralFilingDocumentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(Path(self.temp.name))
        self.c = contract([source()])
        self.fetcher = FixtureFetcher(self.store, {INDEX: initial(), filing_url(): BODY})
        self.agent = Mock()
        self.agent.queued_work = False
        self.agent.extract.side_effect = AssertionError('neutral documents cannot extract facts')
        self.agent.review.side_effect = AssertionError('neutral documents cannot review facts')
        self.structured = Mock(side_effect=AssertionError('neutral documents cannot use certified adapter'))

    def run_pipeline(self, clock=lambda: NOW, scheduled=NOW):
        return Pipeline(self.c, self.store, self.fetcher, agent=self.agent, clock=clock,
                        structured=self.structured).run(scheduled, force_refresh=True)

    def assert_neutral(self, result):
        self.assertTrue(result['complete'], result['receipts'])
        receipt = result['receipts'][0]
        self.assertEqual(receipt['outcome'], 'checked_no_change')
        self.assertEqual(receipt['validatedFacts'], [])
        self.assertEqual(receipt['newFactIds'], [])
        self.assertNotIn('documentValidations', receipt)
        self.assertNotIn('heldClaims', receipt)
        self.assertEqual(eligible_fact_references(result), [])
        self.assertEqual(verified_partial_document_facts(plan_run(self.c, NOW), result, self.c, NOW, self.store), [])
        self.agent.extract.assert_not_called()
        self.agent.review.assert_not_called()
        self.structured.assert_not_called()
        self.assertEqual(list((self.store.root / 'facts').glob('*.json')), [])
        return json.loads(self.store.get(receipt['regulatoryFilingValidation']))

    def replay(self, receipts):
        return reconcile(plan_run(self.c, NOW), receipts, self.c, NOW, self.store)

    def test_parent_retains_exact_bodies_text_selection_and_no_facts(self):
        result = self.run_pipeline()
        record = self.assert_neutral(result)
        receipt = result['receipts'][0]
        self.assertEqual(record['selectedDocuments'], [{'url': filing_url(), 'filingDate': '2026-10-20'}])
        self.assertEqual(record['verification']['facts'], [])
        self.assertEqual(record['verification']['sourceSha256'], digest(self.c['sources'][0]))
        self.assertEqual(record['observationIds'], receipt['observationIds'][:1])
        self.assertEqual(self.store.get(receipt['documents'][0]['body']), BODY)
        self.assertIn(b'Original fictional issuer filing', self.store.get(receipt['documents'][0]['text']))
        self.assertEqual(self.store.read('heads/budget-2026-10-23.json'), {'calls': 0, 'documents': 0, 'fetches': 2})

    def test_direct_public_uses_same_zero_fact_path(self):
        self.c = contract([source('public-a', 'direct')])
        self.assert_neutral(self.run_pipeline())

    def test_candidate_is_a_gap_and_performs_zero_requests(self):
        self.c['sources'][0]['registration'] = 'candidate'
        validate_contract(self.c)
        self.assertEqual(len(plan_run(self.c, NOW)['tasks']), 1)
        result = self.run_pipeline()
        self.assertFalse(result['complete'])
        self.assertEqual(result['receipts'][0]['errorCode'], 'SOURCE_BINDING_UNVERIFIED')
        self.assertEqual(self.fetcher.calls, [])
        self.agent.extract.assert_not_called()
        self.structured.assert_not_called()

    def test_contract_requires_exact_family_cik_endpoint_hosts_and_subject_kind(self):
        mutations = [lambda s: s.update(family='regulatory_filings'), lambda s: s.update(cik='0000999999'),
                     lambda s: s.pop('cik'), lambda s: s.update(url=INDEX + '?x=1'),
                     lambda s: s.update(allowedHosts=['www.sec.gov', 'data.sec.gov']),
                     lambda s: s['allowedHosts'].append('other.test'),
                     lambda s: s['regulatoryIssuer'].update(relationship='direct'),
                     lambda s: s['regulatoryIssuer'].update(legalName=''),
                     lambda s: s.update(kind='sec_submissions')]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                candidate = copy.deepcopy(self.c); mutate(candidate['sources'][0])
                with self.assertRaises(ValueError): validate_contract(candidate)

    def test_foreign_forms_amendments_and_safe_xsl_paths_share_form_set(self):
        forms = ('20-F', '20-F/A', '6-K', '6-K/A', '10-K/A')
        filings = [row('0000123456-26-' + str(i + 1).zfill(6), form=form,
                       document='xslF345X05/filing' + str(i) + '.xml') for i, form in enumerate(forms)]
        filings.append(row('0000123456-26-000006', form='4'))
        self.fetcher.pages = {INDEX: initial(filings), **{filing_url(r): BODY for r in filings[:-1]}}
        record = self.assert_neutral(self.run_pipeline())
        self.assertTrue(set(forms).issubset(SEC_FILING_FORMS))
        self.assertEqual([s['url'] for s in record['selectedDocuments']], sorted(filing_url(r) for r in filings[:-1]))
        self.assertEqual(len(self.fetcher.calls), 6)

    def test_older_index_is_complete_and_retained_selection_is_exact(self):
        older = row('0000123456-26-000002', day='2026-01-01', form='6-K')
        metadata = {'name': ARCHIVE.rsplit('/', 1)[1], 'filingCount': 1,
                    'filingFrom': '2026-01-01', 'filingTo': '2026-01-02'}
        self.fetcher.pages.update({INDEX: initial(history=[metadata]), ARCHIVE: table([older]), filing_url(older): BODY})
        record = self.assert_neutral(self.run_pipeline())
        self.assertEqual([d['url'] for d in record['documents']], [INDEX, ARCHIVE])
        self.assertEqual(len(record['selectedDocuments']), 2)
        self.assertEqual(len(self.fetcher.calls), 4)

    def test_validated_empty_eligible_selection_is_successful_without_primary_requests(self):
        for filings in ([], [row(form='4')], [row('0000123456-25-000001', day='2025-01-01')]):
            with self.subTest(filings=filings):
                self.fetcher.calls.clear(); self.fetcher.pages[INDEX] = initial(filings)
                # Fresh source identity avoids the intended within-retention removal guard.
                self.c['sources'][0]['id'] += '-empty'
                self.c['suppliers'][0]['sourceIds'] = [self.c['sources'][0]['id']]
                result = self.run_pipeline(); record = self.assert_neutral(result)
                self.assertEqual(record['selectedDocuments'], [])
                self.assertEqual(result['receipts'][0].get('documents', []), [])
                self.assertEqual([c['url'] for c in self.fetcher.calls], [INDEX])

    def test_missing_older_index_never_becomes_empty_success(self):
        self.fetcher.pages[INDEX] = initial([], [{'name': ARCHIVE.rsplit('/', 1)[1], 'filingCount': 1,
                                                'filingFrom': '2026-01-01', 'filingTo': '2026-01-01'}])
        result = self.run_pipeline()
        self.assertFalse(result['complete'])
        self.assertNotIn('regulatoryFilingValidation', result['receipts'][0])

    def test_immutable_reuse_keeps_original_bytes_times_and_current_complete_index_anchors(self):
        first = self.run_pipeline(); self.assert_neutral(first)
        self.fetcher.calls.clear()
        later = '2026-10-23T13:00:00Z'
        result = self.run_pipeline(clock=lambda: later)
        self.assertTrue(result['complete'], result['receipts'])
        receipt = result['receipts'][0]
        record = json.loads(self.store.get(receipt['regulatoryFilingValidation']))
        observed = self.store.read('observations/' + receipt['observationIds'][-1] + '.json')
        self.assertEqual(observed['status'], 'retained_immutable')
        self.assertEqual(observed['fetchedAt'], NOW)
        self.assertEqual(observed['verifiedAt'], later)
        self.assertEqual(observed['anchorObservationIds'], record['observationIds'])
        self.assertEqual(self.store.get(observed['body']), BODY)
        self.assertEqual([c['url'] for c in self.fetcher.calls], [INDEX])

    def test_missing_blocked_or_unreadable_document_keeps_source_incomplete(self):
        for body in (404, 403, b'<html>Too short</html>', b'<html>Access denied ' + b'x' * 200 + b'</html>'):
            with self.subTest(body=body):
                self.fetcher.pages[filing_url()] = body
                # A fetched unreadable body may be immutable; isolate cache per source.
                self.c['sources'][0]['id'] += '-blocked'; self.c['suppliers'][0]['sourceIds'] = [self.c['sources'][0]['id']]
                result = self.run_pipeline()
                self.assertFalse(result['complete'])
                self.assertEqual(result['receipts'][0]['validatedFacts'], [])
                self.structured.assert_not_called()
                self.agent.extract.assert_not_called()

    def test_wrong_issuer_sparse_unequal_unsafe_future_and_conflicting_rows_are_incomplete(self):
        cases = []
        wrong = initial(); wrong['name'] = 'WRONG ISSUER'; cases.append(wrong)
        wrong = initial(); wrong['cik'] = 999999; cases.append(wrong)
        wrong = initial(); del wrong['filings']['recent']['acceptanceDateTime']; cases.append(wrong)
        wrong = initial(); wrong['filings']['recent']['form'] = []; cases.append(wrong)
        for primary in ('../bad.htm', '/bad.htm', 'https://evil.test/doc', '', 'bad.htm?query'):
            cases.append(initial([row(document=primary)]))
        cases.extend([initial([row(day='2026-10-24')]),
                      initial([row(), {**row(), 'form': '6-K'}])])
        future = initial(); future['filings']['recent']['acceptanceDateTime'] = ['2026-10-24T00:00:00Z']; cases.append(future)
        for value in cases:
            with self.subTest(value=value):
                self.fetcher.calls.clear(); self.fetcher.pages[INDEX] = value
                result = self.run_pipeline()
                self.assertFalse(result['complete'])
                self.assertEqual([c['url'] for c in self.fetcher.calls], [INDEX])
                self.assertNotIn('regulatoryFilingValidation', result['receipts'][0])

    def test_full_index_rows_and_source_are_independently_verified(self):
        value = initial([row(), row()])
        checked = verify_filing_index_documents(self.c['sources'][0], [{'url': INDEX, 'document': value}], NOW)
        self.assertEqual(checked['duplicateRows'], 1)
        self.assertEqual(len(checked['selectedDocuments']), 1)
        candidate = copy.deepcopy(self.c['sources'][0]); candidate['registration'] = 'candidate'
        with self.assertRaises(ValueError): verify_filing_index_documents(candidate, [{'url': INDEX, 'document': value}], NOW)

    def test_inherited_semantic_heads_fail_before_any_request_or_cursor_advance(self):
        for key, value in [('validatedHashes', {'url': 'cache'}), ('validatedFacts', [{'sha256': 'a' * 64}]),
                           ('factRefs', [{'sha256': 'a' * 64}]), ('documentValidations', [{}]), ('heldClaims', [{}])]:
            with self.subTest(key=key):
                self.c['sources'][0]['id'] += '-old'; self.c['suppliers'][0]['sourceIds'] = [self.c['sources'][0]['id']]
                head = {'observations': {}, 'items': [], key: value}
                name = 'source-' + digest(self.c['sources'][0]['id'])
                self.store.compare_and_swap(name, None, head)
                self.fetcher.calls.clear(); result = self.run_pipeline()
                self.assertFalse(result['complete'])
                self.assertIn('semantic references', result['receipts'][0]['errorCode'])
                self.assertEqual(self.fetcher.calls, [])
                self.assertEqual(self.store.read('heads/' + name + '.json'), head)

    def test_all_receipts_and_partial_paths_reject_semantic_refs_including_malformed_empty_fields(self):
        result = self.run_pipeline()
        for key in ('validatedFacts', 'newFactIds', 'documentValidations', 'heldClaims', 'factRefs'):
            for value in ([{}], None, {}, False):
                for complete in (True, False):
                    with self.subTest(key=key, value=value, complete=complete):
                        receipts = copy.deepcopy(result['receipts'])
                        receipts[0].update(outcome='not_checked', discoveryComplete=complete)
                        receipts[0][key] = value
                        with self.assertRaisesRegex(ValueError, 'semantic references'): self.replay(receipts)
                        with self.assertRaisesRegex(ValueError, 'semantic references'):
                            verified_partial_document_facts(plan_run(self.c, NOW), {'receipts': receipts}, self.c, NOW, self.store)

    def test_reconciliation_rejects_self_authored_summary_selection_and_provenance_forgery(self):
        result = self.run_pipeline()
        for field in ('summary', 'selectedDate', 'source', 'subject', 'policy', 'indexBody', 'indexUrl', 'indexIds', 'time'):
            with self.subTest(field=field):
                receipts = copy.deepcopy(result['receipts']); receipt = receipts[0]
                record = json.loads(self.store.get(receipt['regulatoryFilingValidation']))
                if field == 'summary': record['verification']['retainedFilings'] = 999
                elif field == 'selectedDate': record['selectedDocuments'][0]['filingDate'] = '2026-10-19'
                elif field == 'source': record['sourceId'] = 'another-source'
                elif field == 'subject': record['supplierId'] = 'parent-instead-of-segment'
                elif field == 'policy': record['contractSha256'] = '0' * 64
                elif field == 'indexBody': record['documents'][0]['body'] = self.store.put(initial([]))
                elif field == 'indexUrl': record['documents'][0]['url'] = ARCHIVE
                elif field == 'indexIds': record['observationIds'] = []
                else: record['checkedAt'] = '2026-10-23T11:59:59Z'
                receipt['regulatoryFilingValidation'] = self.store.put(record)
                with self.assertRaises(ValueError): self.replay(receipts)

    def test_omitted_extra_duplicate_or_reordered_document_sets_fail_replay(self):
        second = row('0000123456-26-000002', form='6-K')
        self.fetcher.pages.update({INDEX: initial([row(), second]), filing_url(second): BODY})
        result = self.run_pipeline()
        for mode in ('omitted', 'extra', 'duplicate', 'reordered', 'manifestOmitted', 'fullOmissionForgery'):
            with self.subTest(mode=mode):
                receipts = copy.deepcopy(result['receipts']); receipt = receipts[0]
                if mode == 'omitted': receipt['documents'].pop()
                elif mode == 'extra': receipt['documents'].append({**receipt['documents'][0], 'url': 'https://www.sec.gov/Archives/extra.htm'})
                elif mode == 'duplicate': receipt['documents'].append(receipt['documents'][0])
                elif mode == 'reordered': receipt['documents'].reverse()
                else:
                    manifest = json.loads(self.store.get(receipt['itemManifest'])); manifest['items'].pop()
                    receipt['itemManifest'] = self.store.put(manifest)
                    if mode == 'fullOmissionForgery':
                        receipt['documents'].pop(); receipt['observationIds'].pop()
                        record = json.loads(self.store.get(receipt['regulatoryFilingValidation']))
                        record['selectedDocuments'].pop(); record['verification']['selectedDocuments'].pop()
                        receipt['regulatoryFilingValidation'] = self.store.put(record)
                with self.assertRaises(ValueError): self.replay(receipts)

    def test_changed_primary_body_or_text_cannot_match_by_length_only(self):
        result = self.run_pipeline()
        for field in ('body', 'text'):
            with self.subTest(field=field):
                receipts = copy.deepcopy(result['receipts'])
                receipts[0]['documents'][0][field] = self.store.put(b'Different readable text of sufficient length. ' * 20)
                with self.assertRaisesRegex(ValueError, 'body binding|readable text'): self.replay(receipts)

    def test_receipt_subject_cannot_override_bound_supplier(self):
        result = self.run_pipeline(); receipts = copy.deepcopy(result['receipts'])
        receipts[0]['supplierId'] = 'different-subject'
        with self.assertRaisesRegex(ValueError, 'receipt subject differs'): self.replay(receipts)

    def test_observation_identity_must_match_its_archived_reference(self):
        result = self.run_pipeline(); receipt = result['receipts'][0]
        path = 'observations/' + receipt['observationIds'][-1] + '.json'
        observed = self.store.read(path); observed['observationId'] = 'forged-identity'
        self.store._path(path).write_text(json.dumps(observed))
        with self.assertRaisesRegex(ValueError, 'observation identity differs'): self.replay(result['receipts'])

    def test_unlisted_primary_observation_and_final_url_are_rejected(self):
        result = self.run_pipeline()
        receipt = result['receipts'][0]
        path = 'observations/' + receipt['observationIds'][-1] + '.json'
        original = self.store.read(path)
        for changed in ({**original, 'finalUrl': filing_url() + '?redirect=1'},
                        {**original, 'requestedUrl': filing_url() + '?other=1'}):
            with self.subTest(changed=changed):
                self.store._path(path).write_text(json.dumps(changed))
                with self.assertRaises(ValueError): self.replay(result['receipts'])
        self.store._path(path).write_text(json.dumps(original))

    def test_immutable_replay_rejects_missing_current_index_anchor(self):
        self.run_pipeline()
        result = self.run_pipeline(clock=lambda: '2026-10-23T13:00:00Z')
        receipt = result['receipts'][0]
        path = 'observations/' + receipt['observationIds'][-1] + '.json'
        observed = self.store.read(path); observed['anchorObservationIds'] = []
        self.store._path(path).write_text(json.dumps(observed))
        with self.assertRaises(ValueError):
            reconcile(plan_run(self.c, NOW), result['receipts'], self.c, '2026-10-23T13:00:00Z', self.store)

    def test_day_crossing_during_document_fetch_never_advances_success_cursor(self):
        clock = {'now': '2026-10-23T23:59:59Z'}
        fetch = self.fetcher.fetch
        def crossing(source, url, previous=None):
            observed = fetch(source, url, previous)
            if url == filing_url(): clock['now'] = '2026-10-24T00:00:01Z'
            return observed
        self.fetcher.fetch = crossing
        result = self.run_pipeline(clock=lambda: clock['now'], scheduled=clock['now'])
        self.assertFalse(result['complete'])
        self.assertEqual(result['receipts'][0]['errorCode'], 'SEC_FILING_WINDOW_CHANGED_DURING_COLLECTION')
        self.assertIsNone(self.store.read('heads/source-' + digest(self.c['sources'][0]['id']) + '.json'))

    def test_reconciliation_rejects_changed_day_even_when_selection_would_be_unchanged(self):
        result = self.run_pipeline(); receipts = copy.deepcopy(result['receipts'])
        receipts[0]['completedAt'] = '2026-10-24T00:00:00Z'
        with self.assertRaisesRegex(ValueError, 'window changed'):
            reconcile(plan_run(self.c, NOW), receipts, self.c, '2026-10-24T00:00:00Z', self.store)

    def test_bounded_compressed_index_and_primary_preserve_original_bytes(self):
        index_bytes = gzip.compress(json.dumps(initial()).encode())
        primary_bytes = gzip.compress(BODY)
        self.fetcher.pages = {INDEX: index_bytes, filing_url(): primary_bytes}
        result = self.run_pipeline(); record = self.assert_neutral(result)
        self.assertEqual(self.store.get(record['documents'][0]['body']), index_bytes)
        self.assertEqual(self.store.get(result['receipts'][0]['documents'][0]['body']), primary_bytes)

    def test_legacy_sec_documents_still_works_without_neutral_issuer_record(self):
        self.c['sources'][0].pop('regulatoryIssuer')
        result = self.run_pipeline()
        self.assertTrue(result['complete'], result['receipts'])
        self.assertNotIn('regulatoryFilingValidation', result['receipts'][0])
        self.assertEqual(result['receipts'][0]['validatedFacts'], [])
        self.agent.extract.assert_not_called(); self.structured.assert_not_called()


if __name__ == '__main__':
    unittest.main()
