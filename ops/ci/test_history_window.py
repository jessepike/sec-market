"""History window, fetch-only supplier check and model-budget exhaustion (D-112 backlog cut).

Archiving only changes what is selected and how processing is counted. Every URL, date,
pending entry and receipt stays; nothing is deleted.
"""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/tests'))
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
import test_retained_audit_rebinding as fixtures
from contracts import ContractError, validate_contract
from engine import Pipeline
from selection import (collection_policy, event_url_hint, history_binding, load_history_policy, mentions_supplier,
                       outside_history_window, select_documents)
from separation import MODE

NOW = '2026-10-19T16:00:00Z'
BASE = 'https://example.invalid/releases/'
ABOUT = 'Fixture Vendor announced a new product line today for its customers and partners across the market. '
OTHER = 'Unrelated Company announced a new product line today for its customers and partners across the market. '


def page(text):
    return ('<html><body><main>' + text * 2 + '</main></body></html>').encode()


class HistoryWindowSelectionTests(unittest.TestCase):
    policy = {'currentWindowDays': 30, 'historyWindowDays': 365, 'maxDocumentsPerSource': 2,
              'maxAuditDocumentsPerSource': 1, 'maxFetchAuditDocumentsPerSource': 3}

    def test_old_never_reviewed_documents_are_archived_and_never_selected(self):
        found = {'items': ['old', 'older', 'recent'], 'itemModified': {'old': '2020-01-01', 'older': '2024-01-01', 'recent': '2026-10-19'}}
        selected, deferred = select_documents(found, {}, self.policy, NOW)
        self.assertEqual(selected, ['recent'])
        self.assertEqual(deferred, ['old', 'older'])  # kept in the queue, never dropped
        self.assertTrue(outside_history_window('2020-01-01', self.policy, NOW))
        self.assertFalse(outside_history_window('2026-01-01', self.policy, NOW))

    def test_policy_without_window_is_unchanged(self):
        legacy = {k: v for k, v in self.policy.items() if k not in ('historyWindowDays', 'maxFetchAuditDocumentsPerSource')}
        found = {'items': ['old', 'recent'], 'itemModified': {'old': '2020-01-01', 'recent': '2026-10-19'}}
        self.assertEqual(select_documents(found, {}, legacy, NOW), (['recent', 'old'], []))
        self.assertFalse(outside_history_window('2020-01-01', legacy, NOW))

    def test_undated_and_future_dated_documents_stay_pending_and_sort_last(self):
        found = {'items': ['a-undated', 'b-dated', 'c-future', 'd-dated'],
                 'itemModified': {'b-dated': '2026-03-01', 'c-future': '2099-01-01', 'd-dated': '2026-04-01'}}
        policy = {**self.policy, 'maxDocumentsPerSource': 5}
        selected, deferred = select_documents(found, {}, policy, NOW)
        self.assertEqual(selected[:2], ['b-dated', 'd-dated'])
        self.assertEqual(set(selected[2:]), {'a-undated', 'c-future'})
        self.assertEqual(deferred, [])
        self.assertFalse(outside_history_window('2099-01-01', policy, NOW))
        self.assertFalse(outside_history_window('', policy, NOW))

    def test_undated_business_event_address_is_reviewed_before_other_undated_pages(self):
        found = {'items': [BASE + 'a-product-tips', BASE + 'b-webinar', BASE + 'z-acme-raises-series-b', BASE + 'dated'],
                 'itemModified': {BASE + 'dated': '2026-03-01'}}
        policy = {**self.policy, 'maxDocumentsPerSource': 2, 'maxAuditDocumentsPerSource': 2, 'maxFetchAuditDocumentsPerSource': 0}
        selected, deferred = select_documents(found, {}, policy, NOW)
        self.assertEqual(selected, [BASE + 'dated', BASE + 'z-acme-raises-series-b'])  # dated still first
        self.assertEqual(deferred, [BASE + 'a-product-tips', BASE + 'b-webinar'])  # nothing is dropped
        self.assertTrue(event_url_hint(BASE + 'names-new-chief-financial-officer'))
        self.assertFalse(event_url_hint('https://fundraising.example.invalid/blog/product-tips'))  # host is ignored

    def test_already_reviewed_old_document_is_neither_archived_nor_reaudited(self):
        found = {'items': ['old'], 'itemModified': {'old': '2020-01-01'}}
        history = {'old': {'modified': '2020-01-01', 'checkedAt': '2026-01-01T00:00:00Z'}}
        self.assertEqual(select_documents(found, history, self.policy, NOW), ([], []))

    def test_changed_old_document_is_current_work_not_archived(self):
        found = {'items': ['old'], 'itemModified': {'old': '2020-02-02'}}
        history = {'old': {'modified': '2020-01-01', 'checkedAt': '2026-01-01T00:00:00Z'}}
        self.assertEqual(select_documents(found, history, self.policy, NOW)[0], ['old'])

    def test_extra_audit_slots_are_bounded_and_rotate_by_day(self):
        urls = ['u%02d' % i for i in range(30)]
        found = {'items': urls, 'itemModified': {u: '2026-06-01' for u in urls}}
        first, _ = select_documents(found, {}, self.policy, NOW)
        again, _ = select_documents(found, {}, self.policy, NOW)
        later, _ = select_documents(found, {}, self.policy, '2026-10-20T16:00:00Z')
        self.assertEqual(len(first), self.policy['maxAuditDocumentsPerSource'] + self.policy['maxFetchAuditDocumentsPerSource'])
        self.assertEqual(first, again)
        self.assertNotEqual(first[1:], later[1:])

    def test_contract_validation(self):
        base = fixtures.contract()
        base['collection'] = {**self.policy, 'mode': MODE}
        validate_contract(base)
        for bad in ({'historyWindowDays': 30}, {'historyWindowDays': '365'}, {'maxFetchAuditDocumentsPerSource': -1},
                    {'mode': 'delta_with_retained_audit'}):
            broken = copy.deepcopy(base); broken['collection'].update(bad)
            with self.assertRaises(ContractError):
                validate_contract(broken)


class SupplierMentionTests(unittest.TestCase):
    def test_name_alias_and_absence(self):
        supplier = {'name': 'Arctic Wolf Networks, Inc.', 'kind': 'private', 'aliases': ['Arctic Wolf']}
        self.assertTrue(mentions_supplier('News from ARCTIC WOLF NETWORKS today', supplier))
        self.assertTrue(mentions_supplier('arctic wolf expands', supplier))
        self.assertTrue(mentions_supplier('Arctic-Wolf expands', supplier))
        self.assertFalse(mentions_supplier('Arctic Wolfpack expands and an unrelated company raised money', supplier))
        self.assertFalse(mentions_supplier('A completely different company raised money', supplier))

    def test_whole_word_only(self):
        self.assertFalse(mentions_supplier('Octopus and Oktane keynote', {'name': 'Okta', 'kind': 'public', 'aliases': []}))
        self.assertTrue(mentions_supplier('Okta, Inc. reported', {'name': 'Okta', 'kind': 'public', 'aliases': []}))

    def test_parenthetical_names_and_legal_suffixes_match_plain_use(self):
        sophos = {'name': 'Sophos Group (Sophos Ltd)', 'kind': 'pe-owned', 'aliases': ['Sophos Group (Sophos']}
        self.assertTrue(mentions_supplier('Thoma Bravo completed its Sophos investment', sophos))
        self.assertTrue(mentions_supplier('Crowdstrike Holdings reported', {'name': 'CrowdStrike Holdings, Inc.', 'kind': 'public', 'aliases': []}))

    def test_segments_are_never_excluded(self):
        self.assertTrue(mentions_supplier('Microsoft announced updates', {'name': 'Microsoft Entra ID', 'kind': 'segment', 'aliases': []}))


class HistoryWindowPipelineTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.RetainedAuditTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        c = self.f.contract
        c['version'] = 'test-window'
        c['collection'] = {'mode': MODE, 'currentWindowDays': 30, 'historyWindowDays': 365, 'maxDocumentsPerSource': 2,
                           'maxAuditDocumentsPerSource': 1, 'maxFetchAuditDocumentsPerSource': 10}
        c['sources'][0].update(kind='sitemap', url='https://example.invalid/sitemap.xml')
        self.f.time = NOW
        self.agent = fixtures.FakeAgent()

    def site(self, documents):
        """documents: {name: (lastmod or None, html bytes)}"""
        rows = ''.join('<url><loc>' + BASE + n + '</loc>' + ('<lastmod>' + d + '</lastmod>' if d else '') + '</url>'
                       for n, (d, _) in documents.items())
        self.f.fetcher.pages[self.f.contract['sources'][0]['url']] = ('<urlset>' + rows + '</urlset>').encode()
        for n, (_, body) in documents.items():
            self.f.fetcher.pages[BASE + n] = body

    def run_once(self):
        result = self.f.run_pipeline(self.agent)
        self.f.replay(result)  # the independent verifier must accept the receipt
        return result, result['receipts'][0]

    def assert_partitions(self, result):
        p, h = result['processing'], result['historicalReview']
        self.assertEqual(p['reviewedDocuments'] + p['pendingDocuments'], p['inventoryDocuments'])
        self.assertEqual(p['inventoryDocuments'] + p['archivedDocuments'], h['inventoryDocuments'])
        self.assertLessEqual(p['notAboutSupplierDocuments'], p['reviewedDocuments'])
        for row in result['tasks']:
            q = row['processing']
            self.assertEqual(q['reviewedDocuments'] + q['pendingDocuments'], q['inventoryDocuments'])

    def test_archive_exclusion_and_counters_stay_consistent(self):
        self.site({'old': ('2020-01-01', page(ABOUT)), 'older': ('2021-06-01', page(OTHER)),
                   'mid-other': ('2026-03-01', page(OTHER)), 'mid-about': ('2026-04-01', page(ABOUT)),
                   'undated-other': (None, page(OTHER)), 'fresh': ('2026-10-18', page(ABOUT))})
        result, receipt = self.run_once()
        p = result['processing']
        self.assertEqual(p['archivedDocuments'], 2)  # both old documents, one that mentions the supplier and one that does not
        self.assertEqual(result['historicalReview']['inventoryDocuments'], 6)
        self.assert_partitions(result)
        # Archived URLs stay in the pending manifest with their original dates; nothing is deleted.
        pending = json.loads(self.f.store.get(receipt['pendingManifest']))['items']
        self.assertIn(BASE + 'old', pending); self.assertIn(BASE + 'older', pending)
        manifest = json.loads(self.f.store.get(receipt['itemManifest']))
        self.assertEqual(manifest['itemModified'][BASE + 'old'], '2020-01-01')
        self.assertNotIn(BASE + 'old', receipt['selectedDocumentUrls'])
        self.assertNotIn(BASE + 'older', receipt['selectedDocumentUrls'])

    def test_not_about_supplier_makes_no_model_call_and_no_fact(self):
        self.site({'other': ('2026-09-01', page(OTHER)), 'undated-other': (None, page(OTHER))})
        result, receipt = self.run_once()
        self.assertEqual(self.agent.calls, 0)
        self.assertEqual(receipt['validatedFacts'], [])
        self.assertEqual(result['processing']['notAboutSupplierDocuments'], 2)
        self.assertEqual(result['processing']['reviewedDocuments'], 2)
        self.assertEqual(result['processing']['pendingDocuments'], 0)
        self.assertTrue(result['processing']['complete'])
        for document in receipt['documentValidations']:
            validation = json.loads(self.f.store.get(document['validation']))
            self.assertEqual(validation['outcome'], 'not_about_supplier')
            self.assertEqual(validation['candidateHashes'], [])
        self.assertIsNone(self.f.store.read('heads/budget-2026-10-19.json') and
                          self.f.store.read('heads/budget-2026-10-19.json').get('documents') or None)

    def test_name_and_alias_mentions_go_to_the_model(self):
        self.f.contract['suppliers'][0]['aliases'] = ['FV Labs']
        self.site({'name': ('2026-09-01', page(ABOUT)), 'alias': ('2026-09-02', page(OTHER.replace('Unrelated Company', 'FV Labs')))})
        result, receipt = self.run_once()
        self.assertEqual(result['processing']['notAboutSupplierDocuments'], 0)
        self.assertGreater(self.agent.calls, 0)
        self.assertEqual(result['processing']['reviewedDocuments'], 2)

    def first_pass_agent(self, default_model_agrees):
        log = []

        class Agent(fixtures.FakeAgent):
            def extract(self, text, supplier, first_pass=True):
                log.append('extract:first' if first_pass else 'extract:default')
                return [] if first_pass else super().extract(text, supplier)

            def review(self, *args):
                log.append('review')
                return super().review(*args)

            def review_empty(self, *args):
                log.append('review_empty')
                return {**super().review_empty(*args), 'noRelevantFacts': default_model_agrees}
        return Agent(), log

    def test_default_model_redoes_a_page_when_it_disagrees_with_an_empty_first_pass(self):
        self.f.contract['model']['extractModel'] = 'gpt-6-luna'
        self.agent, log = self.first_pass_agent(default_model_agrees=False)
        self.site({'name': ('2026-09-01', page(ABOUT))})
        self.run_once()
        self.assertEqual(log[:3], ['extract:first', 'review_empty', 'extract:default'])
        self.assertIn('review', log[3:])
        self.assertEqual(log.count('review_empty'), 1)

    def test_agreed_empty_first_pass_costs_one_default_model_call(self):
        self.f.contract['model']['extractModel'] = 'gpt-6-luna'
        self.agent, log = self.first_pass_agent(default_model_agrees=True)
        self.site({'name': ('2026-09-01', page(ABOUT))})
        result, _ = self.run_once()
        self.assertEqual(log, ['extract:first', 'review_empty'])
        self.assertEqual(result['processing']['reviewedDocuments'], 1)

    def test_exhausted_model_budget_leaves_work_pending_but_keeps_draining_fetch_only_documents(self):
        self.f.contract['model']['maxDocumentsPerRun'] = 1
        docs = {'about-%d' % i: ('2026-09-%02d' % (i + 1), page(ABOUT + str(i))) for i in range(4)}
        docs.update({'other-%d' % i: ('2026-08-%02d' % (i + 1), page(OTHER + str(i))) for i in range(4)})
        self.site(docs)
        result, receipt = self.run_once()
        p = result['processing']
        self.assertEqual(p['notAboutSupplierDocuments'], 4)  # drained even though the model budget ran out
        self.assertEqual(p['pendingDocuments'], 3)           # waiting for model budget, not failed
        self.assertEqual(p['reviewedDocuments'], 5)
        self.assertNotEqual(receipt['outcome'], 'failed')
        self.assertEqual(self.f.store.read('heads/budget-2026-10-19.json')['documents'], 1)
        self.assertFalse(receipt.get('heldDocuments'))
        self.assert_partitions(result)

    def test_second_day_clears_archive_without_reviewing_it(self):
        self.site({'old': ('2020-01-01', page(OTHER)), 'fresh': ('2026-10-18', page(ABOUT))})
        first, _ = self.run_once()
        self.f.time = '2026-10-20T16:00:00Z'
        second, _ = self.run_once()
        self.assertEqual(second['processing']['archivedDocuments'], 1)
        self.assertEqual(second['historicalReview']['inventoryDocuments'], 2)
        self.assertEqual(second['historicalReview']['pendingDocuments'], 1)
        self.assert_partitions(second)

    def test_forged_exclusion_over_a_document_that_names_the_supplier_fails_replay(self):
        from retained_audit import replay_document
        self.site({'other': ('2026-09-01', page(OTHER))})
        result, receipt = self.run_once()
        validation = json.loads(self.f.store.get(receipt['documentValidations'][0]['validation']))
        self.assertEqual(validation['exclusionRule'], 'not-about-supplier-v1')
        observed = next(o for o in (self.f.store.read('observations/' + oid + '.json') for oid in receipt['observationIds'])
                        if o['requestedUrl'] == BASE + 'other')
        about = self.f.store.put(page(ABOUT))
        forged = {**validation, 'body': about}
        document = {'url': BASE + 'other', 'validation': self.f.store.put(forged)}
        with self.assertRaises(ValueError):
            replay_document(receipt, document, {**observed, 'body': about}, self.f.contract,
                            self.f.contract['sources'][0], NOW, self.f.store)


class HistoryPolicyFileTests(HistoryWindowPipelineTests):
    """The same behaviour, switched on by contracts/history-window.json instead of the contract.

    The contract is left without the keys (so its digest is untouched); the engine records the
    policy's digest and values in every receipt and the replay verifier reads them from there.
    """
    def setUp(self):
        super().setUp()
        collection = self.f.contract['collection']
        values = {'schemaVersion': 1, 'historyWindowDays': collection.pop('historyWindowDays'),
                  'maxFetchAuditDocumentsPerSource': collection.pop('maxFetchAuditDocumentsPerSource')}
        self.binding = history_binding(values, collection)

        def run_pipeline(agent=None):
            self.f.fetcher.now = self.f.time
            return Pipeline(self.f.contract, self.f.store, self.f.fetcher, agent=agent, clock=lambda: self.f.time,
                            history=values).run(self.f.time, force_refresh=True)
        self.f.run_pipeline = run_pipeline

    def test_every_receipt_binds_the_exact_digest_and_values(self):
        self.site({'old': ('2020-01-01', page(OTHER)), 'fresh': ('2026-10-18', page(ABOUT))})
        result, receipt = self.run_once()
        self.assertEqual(receipt['historyWindow'], self.binding)
        self.assertEqual(len(self.binding['sha256']), 64)
        self.assertNotIn('historyWindowDays', self.f.contract['collection'])
        self.assertEqual(result['processing']['archivedDocuments'], 1)

    def test_replay_uses_the_bound_values_not_the_working_policy(self):
        self.site({'old': ('2020-01-01', page(OTHER)), 'fresh': ('2026-10-18', page(ABOUT))})
        result, receipt = self.run_once()
        self.assertEqual(collection_policy(self.f.contract, receipt)['historyWindowDays'], 365)
        # A receipt with edited values no longer matches its recorded digest.
        forged = {**receipt, 'historyWindow': {**receipt['historyWindow'], 'historyWindowDays': 3650}}
        with self.assertRaises(ValueError):
            collection_policy(self.f.contract, forged)


class HistoryPolicyAbsentTests(unittest.TestCase):
    def test_no_file_means_no_cut_and_no_binding(self):
        f = fixtures.RetainedAuditTests()
        f.setUp(); self.addCleanup(f.doCleanups)
        f.contract['sources'][0].update(kind='sitemap', url='https://example.invalid/sitemap.xml')
        f.time = NOW
        f.fetcher.pages['https://example.invalid/sitemap.xml'] = (
            '<urlset><url><loc>' + BASE + 'old</loc><lastmod>2020-01-01</lastmod></url></urlset>').encode()
        f.fetcher.pages[BASE + 'old'] = page(ABOUT)
        receipt = f.run_pipeline(fixtures.FakeAgent())['receipts'][0]
        self.assertNotIn('historyWindow', receipt)
        self.assertIs(collection_policy(f.contract, receipt), f.contract['collection'])

    def test_missing_file_is_off_and_invalid_values_are_refused(self):
        self.assertIsNone(load_history_policy(ROOT / 'contracts/no-such-file.json'))
        collection = {'mode': MODE, 'currentWindowDays': 30}
        good = {'schemaVersion': 1, 'historyWindowDays': 365, 'maxFetchAuditDocumentsPerSource': 80}
        history_binding(good, collection)
        for bad in ({'historyWindowDays': 30}, {'historyWindowDays': '365'}, {'maxFetchAuditDocumentsPerSource': -1},
                    {'extra': 1}, {'schemaVersion': 2}):
            with self.assertRaises(ValueError):
                history_binding({**good, **bad}, collection)
        with self.assertRaises(ValueError):
            history_binding(good, {**collection, 'mode': 'delta_with_retained_audit'})

    def test_committed_policy_is_valid_for_the_committed_contract(self):
        contract = validate_contract(json.loads((ROOT / 'contracts/market.json').read_text()))
        binding = load_history_policy(ROOT / 'contracts/history-window.json')
        self.assertEqual((binding['historyWindowDays'], binding['maxFetchAuditDocumentsPerSource']), (365, 80))
        self.assertTrue(collection_policy(contract, {'historyWindow': binding})['historyWindowDays'] == 365)
        self.assertNotIn('historyWindowDays', contract['collection'])  # the contract digest is untouched


class ConsumerCounterTests(unittest.TestCase):
    """Every reader of the processing counters accepts the new fields and rejects bad ones."""

    def coverage(self, **extra):
        from test_coverage_summary import separated_coverage
        value = separated_coverage()
        value['processing'].update({'archivedDocuments': 11000, 'notAboutSupplierDocuments': 1, **extra})
        return value

    def test_coverage_summary_keeps_reviewed_plus_pending_equal_inventory_with_archive(self):
        from coverage_summary import coverage_details
        details = coverage_details(self.coverage())
        p = details['processing']
        self.assertEqual(p['reviewedDocuments'] + p['pendingDocuments'], p['inventoryDocuments'])
        self.assertEqual(p['archivedDocuments'], 11000)
        for bad in ({'archivedDocuments': -1}, {'archivedDocuments': True}, {'notAboutSupplierDocuments': 2}):
            with self.assertRaises(ValueError):
                coverage_details(self.coverage(**bad))

    def test_scorecard_progress_validator_accepts_and_rejects(self):
        sys.path.insert(0, str(ROOT / 'ops/evaluation'))
        from scorecard import separate_progress
        value = {'complete': False, 'inventoryDocuments': 3, 'reviewedDocuments': 1, 'pendingDocuments': 2, 'heldDocuments': 0,
                 'changedDocuments': 0, 'unknownDateDocuments': 0, 'archivedDocuments': 9, 'notAboutSupplierDocuments': 1}
        self.assertEqual(separate_progress(value, 'processing')['archivedDocuments'], 9)
        self.assertEqual(separate_progress({k: v for k, v in value.items() if k not in ('archivedDocuments', 'notAboutSupplierDocuments')},
                                           'processing').get('archivedDocuments'), None)
        with self.assertRaises(ValueError):
            separate_progress({**value, 'notAboutSupplierDocuments': 5}, 'processing')

    def test_totals_add_archive_only_when_a_source_reports_it(self):
        from separation import totals, summary
        empty = summary(set(), set(), set(), set())
        plain = {'processing': {**empty, 'changedDocuments': 0, 'unknownDateDocuments': 0}}
        windowed_row = {'processing': {**empty, 'changedDocuments': 0, 'unknownDateDocuments': 0,
                                       'archivedDocuments': 4, 'notAboutSupplierDocuments': 1}}
        self.assertNotIn('archivedDocuments', totals([plain, plain], 'processing'))
        self.assertEqual(totals([plain, windowed_row], 'processing')['archivedDocuments'], 4)


if __name__ == '__main__':
    unittest.main()
