"""Synthetic neutral-index collection and independent receipt replay."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from contracts import digest, plan_run, validate_contract
from engine import Pipeline
from regulatory import TABLE_FIELDS
from storage import LocalStore
from validation import eligible_fact_references, reconcile, verified_partial_document_facts

NOW = '2026-10-23T12:00:00Z'
CIK = '0000123456'
INDEX = 'https://data.sec.gov/submissions/CIK' + CIK + '.json'
ARCHIVE = 'https://data.sec.gov/submissions/CIK' + CIK + '-submissions-001.json'


def row(accession='0000123456-26-000001', day='2026-10-20', form='8-K', document='release.htm'):
    return {'accessionNumber': accession, 'filingDate': day, 'reportDate': '',
            'acceptanceDateTime': day + 'T10:00:00Z', 'act': '34', 'form': form,
            'fileNumber': '001-12345', 'filmNumber': '26123456', 'items': '5.02',
            'size': 1234, 'isXBRL': 0, 'isInlineXBRL': 0,
            'primaryDocument': document, 'primaryDocDescription': ''}


def table(rows):
    return {key: [r[key] for r in rows] for key in TABLE_FIELDS}


def initial(rows=None, history=None):
    return {'cik': 123456, 'name': 'EXACT SYNTHETIC PARENT INC',
            'filings': {'recent': table([row()] if rows is None else rows), 'files': history or []}}


def binding(subject='segment-a', relationship='parent'):
    return {'id': subject + ':regulatory', 'supplierId': subject, 'family': 'regulatory_filings',
            'kind': 'sec_index', 'registration': 'verified', 'required': True,
            'url': INDEX, 'allowedHosts': ['data.sec.gov'], 'maxPages': 10,
            'lookbackDays': 365, 'scopePrefixes': ['/submissions/'],
            'regulatoryIssuer': {'cik': CIK, 'legalName': 'EXACT SYNTHETIC PARENT INC', 'relationship': relationship}}


def contract(sources=None):
    sources = sources or [binding()]
    suppliers = []
    for source in sources:
        if any(s['id'] == source['supplierId'] for s in suppliers):
            continue
        own = [s for s in sources if s['supplierId'] == source['supplierId']]
        relationship = source.get('regulatoryIssuer', {}).get('relationship', 'direct')
        suppliers.append({'id': source['supplierId'], 'name': 'Synthetic ' + source['supplierId'], 'aliases': [],
                          'kind': 'segment' if relationship == 'parent' else 'public',
                          'sourceIds': [s['id'] for s in own], 'requiredCategories': ['announcements_results'],
                          'requiredFamilies': list(dict.fromkeys(s['family'] for s in own))})
    return {'schemaVersion': 1, 'version': 'synthetic-neutral-index',
            'schedule': {'intervalHours': 24, 'overdueHours': 30, 'reconcileEveryRun': True,
                         'maxWorkers': 2, 'maxFetchesPerRun': 5500},
            'model': {'provider': 'codex_subscription', 'allowApiBilling': False,
                      'maxDocumentsPerRun': 40, 'maxCallsPerRun': 80, 'maxDocumentChars': 30000, 'timeoutSeconds': 5},
            'publication': {'enabled': False, 'allowDegradedCoverage': True}, 'suppliers': suppliers, 'sources': sources}


class FixtureFetcher:
    def __init__(self, store, pages):
        self.store, self.pages, self.calls = store, pages, []
        self.conditional = False

    def fetch(self, source, url, previous=None):
        self.calls.append({'url': url, 'source': copy.deepcopy(source), 'previous': copy.deepcopy(previous)})
        if self.conditional and previous:
            return {**previous, 'status': 'not_modified', 'httpStatus': 304,
                    'reusesObservationId': previous['observationId']}
        value = self.pages.get(url, 404)
        if isinstance(value, int):
            return {'requestedUrl': url, 'fetchedAt': NOW, 'status': 'blocked' if value == 403 else 'failed',
                    'httpStatus': value, 'errorCode': 'HTTP_' + str(value)}
        body = value if isinstance(value, bytes) else json.dumps(value).encode()
        return {'requestedUrl': url, 'finalUrl': url, 'fetchedAt': NOW, 'status': 'fetched', 'httpStatus': 200,
                'body': self.store.put(body), 'contentType': 'text/html' if body.startswith(b'<') else 'application/json'}


class RegulatoryCollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(Path(self.temp.name))
        self.c = contract()
        self.fetcher = FixtureFetcher(self.store, {INDEX: initial()})
        self.agent = Mock()
        self.agent.queued_work = False
        self.agent.extract.side_effect = AssertionError('neutral index must not extract')
        self.agent.review.side_effect = AssertionError('neutral index must not review')
        self.structured = Mock(side_effect=AssertionError('neutral index must not enter certified adapter'))

    def run_pipeline(self, force=True):
        return Pipeline(self.c, self.store, self.fetcher, agent=self.agent, clock=lambda: NOW,
                        structured=self.structured).run(NOW, force_refresh=force)

    def assert_neutral(self, result):
        self.assertTrue(result['complete'], result['receipts'])
        for receipt in result['receipts']:
            self.assertEqual(receipt['validatedFacts'], [])
            self.assertEqual(receipt['newFactIds'], [])
            self.assertNotIn('documentValidations', receipt)
            record = json.loads(self.store.get(receipt['regulatoryIndexValidation']))
            self.assertEqual(record['verification']['facts'], [])
            self.assertEqual(record['observationIds'], receipt['observationIds'])
        self.agent.extract.assert_not_called()
        self.agent.review.assert_not_called()
        self.structured.assert_not_called()
        self.assertEqual(eligible_fact_references(result), [])

    def test_parent_segment_check_has_zero_facts_models_and_certified_adapter_calls(self):
        result = self.run_pipeline()
        self.assert_neutral(result)
        self.assertEqual(result['successfulTasks'], 1)
        self.assertEqual(self.store.read('heads/budget-2026-10-23.json'), {'calls': 0, 'documents': 0, 'fetches': 1})
        self.assertEqual(list((self.store.root / 'facts').glob('*.json')), [])

    def test_filing_arriving_during_request_is_checked_after_the_last_observation(self):
        clock = {'now': NOW}
        filing = row(day='2026-10-23')
        filing['acceptanceDateTime'] = '2026-10-23T12:01:00Z'
        self.fetcher.pages[INDEX] = initial([filing])
        original_fetch = self.fetcher.fetch
        def advancing_fetch(*args):
            observation = original_fetch(*args)
            clock['now'] = '2026-10-23T12:02:00Z'
            return {**observation, 'fetchedAt': clock['now']}
        self.fetcher.fetch = advancing_fetch
        result = Pipeline(self.c, self.store, self.fetcher, agent=self.agent, clock=lambda: clock['now'],
                          structured=self.structured).run(NOW)
        self.assert_neutral(result)
        record = json.loads(self.store.get(result['receipts'][0]['regulatoryIndexValidation']))
        self.assertEqual(record['traversalAsOf'], NOW)
        self.assertEqual(record['checkedAt'], '2026-10-23T12:02:00Z')
        observation = self.store.read('observations/' + record['observationIds'][0] + '.json')
        self.assertEqual(observation['fetchedAt'], record['checkedAt'])

    def test_utc_day_crossing_during_discovery_cannot_mix_retention_windows(self):
        clock = {'now': '2026-10-23T23:59:59Z'}
        original_fetch = self.fetcher.fetch
        def crossing_fetch(*args):
            observation = original_fetch(*args)
            clock['now'] = '2026-10-24T00:00:01Z'
            return {**observation, 'fetchedAt': clock['now']}
        self.fetcher.fetch = crossing_fetch
        result = Pipeline(self.c, self.store, self.fetcher, agent=self.agent, clock=lambda: clock['now'],
                          structured=self.structured).run('2026-10-23T23:59:59Z')
        self.assertFalse(result['complete'])
        self.assertEqual(result['receipts'][0]['errorCode'], 'SEC_INDEX_WINDOW_CHANGED_DURING_DISCOVERY')
        self.assertNotIn('regulatoryIndexValidation', result['receipts'][0])

    def test_direct_public_index_uses_same_neutral_route(self):
        self.c = contract([binding('direct-supplier', 'direct')])
        self.assert_neutral(self.run_pipeline())

    def test_candidate_shape_plans_and_stays_unverified_without_fetch(self):
        self.c['sources'][0]['registration'] = 'candidate'
        self.assertEqual(len(plan_run(self.c, NOW)['tasks']), 1)
        result = self.run_pipeline()
        self.assertFalse(result['complete'])
        self.assertEqual(result['receipts'][0]['errorCode'], 'SOURCE_BINDING_UNVERIFIED')
        self.assertEqual(self.fetcher.calls, [])
        self.structured.assert_not_called()
        self.agent.extract.assert_not_called()

    def test_required_older_page_is_fetched_bound_and_independently_checked(self):
        metadata = {'name': ARCHIVE.rsplit('/', 1)[1], 'filingCount': 1,
                    'filingFrom': '2026-01-01', 'filingTo': '2026-01-01'}
        self.fetcher.pages = {INDEX: initial(history=[metadata]), ARCHIVE: table([row('0000123456-26-000002', '2026-01-01')])}
        result = self.run_pipeline()
        self.assert_neutral(result)
        record = json.loads(self.store.get(result['receipts'][0]['regulatoryIndexValidation']))
        self.assertEqual([d['url'] for d in record['documents']], [INDEX, ARCHIVE])
        self.assertEqual(record['verification']['documentCount'], 2)
        self.assertEqual(record['verification']['retainedFilings'], 2)

    def test_older_history_outside_retained_window_is_not_requested(self):
        metadata = {'name': ARCHIVE.rsplit('/', 1)[1], 'filingCount': 1,
                    'filingFrom': '2024-01-01', 'filingTo': '2024-01-01'}
        self.fetcher.pages[INDEX] = initial(history=[metadata])
        self.assert_neutral(self.run_pipeline())
        self.assertEqual([c['url'] for c in self.fetcher.calls], [INDEX])

    def test_no_current_filings_keeps_retained_index_check_neutral(self):
        self.fetcher.pages[INDEX] = initial([row('0000123456-25-000001', '2025-01-01')])
        result = self.run_pipeline()
        self.assert_neutral(result)
        record = json.loads(self.store.get(result['receipts'][0]['regulatoryIndexValidation']))
        self.assertEqual(record['verification']['retainedFilings'], 0)

    def test_missing_or_blocked_required_archive_cannot_earn_coverage(self):
        metadata = {'name': ARCHIVE.rsplit('/', 1)[1], 'filingCount': 1,
                    'filingFrom': '2026-01-01', 'filingTo': '2026-01-01'}
        self.fetcher.pages[INDEX] = initial(history=[metadata])
        for status in (404, 403):
            with self.subTest(status=status):
                self.fetcher.pages[ARCHIVE] = status
                result = self.run_pipeline()
                self.assertFalse(result['complete'])
                self.assertNotIn('regulatoryIndexValidation', result['receipts'][0])
                self.assertEqual(result['receipts'][0]['validatedFacts'], [])

    def test_wrong_initial_issuer_and_truncated_arrays_stay_incomplete(self):
        wrong_cik = initial(); wrong_cik['cik'] = 999999
        wrong_name = initial(); wrong_name['name'] = 'Familiar but different name'
        truncated = initial(); truncated['filings']['recent']['primaryDocument'] = []
        malformed = initial(); del malformed['filings']['recent']['acceptanceDateTime']
        for value in (wrong_cik, wrong_name, truncated, malformed):
            with self.subTest(value=value):
                self.fetcher.pages[INDEX] = value
                result = self.run_pipeline()
                self.assertFalse(result['complete'])
                self.assertFalse(result['receipts'][0]['discoveryComplete'])
                self.assertEqual(result['receipts'][0]['validatedFacts'], [])

    def test_conflicting_rows_rejected_by_independent_helper_after_discovery(self):
        first = row(); second = {**first, 'form': '10-Q'}
        self.fetcher.pages[INDEX] = initial([first, second])
        result = self.run_pipeline()
        self.assertFalse(result['complete'])
        self.assertIn('Conflicting duplicate', result['receipts'][0]['errorCode'])
        self.assertEqual(result['receipts'][0]['validatedFacts'], [])

    def test_older_page_truncation_and_conflicting_boundary_are_rejected(self):
        metadata = {'name': ARCHIVE.rsplit('/', 1)[1], 'filingCount': 2,
                    'filingFrom': '2026-01-01', 'filingTo': '2026-01-02'}
        self.fetcher.pages = {INDEX: initial(history=[metadata]), ARCHIVE: table([row('0000123456-26-000002', '2026-01-01')])}
        result = self.run_pipeline()
        self.assertFalse(result['complete'])
        self.assertIn('filing count differs', result['receipts'][0]['errorCode'])

    def test_unsafe_or_wrong_issuer_archive_name_is_never_requested(self):
        for name in ('../wrong.json', 'CIK0000999999-submissions-001.json', 'CIK0000123456-submissions-1.json'):
            with self.subTest(name=name):
                self.fetcher.calls.clear()
                self.fetcher.pages[INDEX] = initial(history=[{'name': name, 'filingCount': 1,
                                                            'filingFrom': '2026-01-01', 'filingTo': '2026-01-01'}])
                self.assertFalse(self.run_pipeline()['complete'])
                self.assertEqual([c['url'] for c in self.fetcher.calls], [INDEX])

    def test_page_cap_cannot_truncate_a_required_older_index(self):
        self.c['sources'][0]['maxPages'] = 1
        self.fetcher.pages[INDEX] = initial(history=[{'name': ARCHIVE.rsplit('/', 1)[1], 'filingCount': 1,
                                                    'filingFrom': '2026-01-01', 'filingTo': '2026-01-01'}])
        self.assertFalse(self.run_pipeline()['complete'])
        self.assertEqual([c['url'] for c in self.fetcher.calls], [INDEX])

    def test_previous_fact_references_and_validated_hashes_cannot_carry_into_neutral_head(self):
        head = {'observations': {}, 'items': [], 'validatedHashes': {'old-model-cache': 'old'},
                'validatedFacts': [{'sha256': 'a' * 64}], 'factRefs': [{'sha256': 'b' * 64}]}
        name = 'source-' + digest(self.c['sources'][0]['id'])
        self.store.compare_and_swap(name, None, head)
        result = self.run_pipeline()
        self.assert_neutral(result)
        saved = self.store.read('heads/' + name + '.json')
        self.assertEqual(saved['validatedHashes'], {})
        self.assertNotIn('factRefs', saved)
        self.assertNotIn('validatedFacts', saved)

    def test_independent_reconciliation_rejects_forged_summary_and_url_body_binding(self):
        result = self.run_pipeline()
        plan = plan_run(self.c, NOW)
        for mutate in ('summary', 'binding', 'issuer'):
            with self.subTest(mutate=mutate):
                receipts = copy.deepcopy(result['receipts'])
                record = json.loads(self.store.get(receipts[0]['regulatoryIndexValidation']))
                if mutate == 'summary': record['verification']['retainedFilings'] = 999
                elif mutate == 'binding': record['documents'][0]['url'] = ARCHIVE
                else: record['verification']['issuer']['legalName'] = 'Wrong parent'
                receipts[0]['regulatoryIndexValidation'] = self.store.put(record)
                with self.assertRaises(ValueError):
                    reconcile(plan, receipts, self.c, NOW, self.store)

    def test_independent_reconciliation_rejects_validation_before_its_source_observation(self):
        result = self.run_pipeline(); receipts = copy.deepcopy(result['receipts'])
        record = json.loads(self.store.get(receipts[0]['regulatoryIndexValidation']))
        receipts[0]['startedAt'] = '2026-10-23T11:00:00Z'
        record['traversalAsOf'] = '2026-10-23T11:00:00Z'
        record['checkedAt'] = '2026-10-23T11:59:00Z'
        receipts[0]['regulatoryIndexValidation'] = self.store.put(record)
        with self.assertRaisesRegex(ValueError, 'precedes source observation'):
            reconcile(plan_run(self.c, NOW), receipts, self.c, NOW, self.store)

    def test_independent_reconciliation_rejects_an_accession_manifest_omission(self):
        result = self.run_pipeline(); receipts = copy.deepcopy(result['receipts'])
        manifest = json.loads(self.store.get(receipts[0]['itemManifest']))
        manifest['items'] = []
        receipts[0]['itemManifest'] = self.store.put(manifest)
        with self.assertRaisesRegex(ValueError, 'accession inventory differs'):
            reconcile(plan_run(self.c, NOW), receipts, self.c, NOW, self.store)

    def test_independent_reconciliation_rejects_a_different_final_response_url(self):
        result = self.run_pipeline(); receipt = result['receipts'][0]
        path = 'observations/' + receipt['observationIds'][0] + '.json'
        observation = self.store.read(path)
        observation['finalUrl'] = 'https://data.sec.gov/submissions/CIK0000999999.json'
        # Deliberately tamper the isolated fixture, not a real immutable archive.
        self.store._path(path).write_text(json.dumps(observation))
        with self.assertRaisesRegex(ValueError, 'final response URL differs'):
            reconcile(plan_run(self.c, NOW), result['receipts'], self.c, NOW, self.store)

    def test_neutral_receipt_cannot_release_parent_facts_or_semantic_document_work(self):
        result = self.run_pipeline(); plan = plan_run(self.c, NOW)
        for key in ('validatedFacts', 'newFactIds', 'documentValidations', 'heldClaims', 'documents'):
            with self.subTest(key=key):
                receipts = copy.deepcopy(result['receipts']); receipts[0][key] = [{'parentRevenue': 'forged'}]
                with self.assertRaisesRegex(ValueError, 'Neutral SEC index receipt contains'):
                    reconcile(plan, receipts, self.c, NOW, self.store)

    def test_falsy_nonarrays_cannot_masquerade_as_empty_neutral_semantic_fields(self):
        result = self.run_pipeline(); plan = plan_run(self.c, NOW)
        for key in ('validatedFacts', 'newFactIds', 'documentValidations', 'heldClaims', 'documents'):
            for value in (None, {}, False):
                with self.subTest(key=key, value=value):
                    receipts = copy.deepcopy(result['receipts']); receipts[0][key] = value
                    with self.assertRaisesRegex(ValueError, 'Neutral SEC index receipt contains'):
                        reconcile(plan, receipts, self.c, NOW, self.store)

    def test_partial_neutral_path_rejects_all_five_malformed_semantic_fields(self):
        result = self.run_pipeline(); plan = plan_run(self.c, NOW)
        for key in ('validatedFacts', 'newFactIds', 'documentValidations', 'heldClaims', 'documents'):
            with self.subTest(key=key):
                coverage = copy.deepcopy(result)
                coverage['receipts'][0].update(outcome='not_checked')
                coverage['receipts'][0][key] = False
                with self.assertRaisesRegex(ValueError, 'Neutral SEC index cannot release partial'):
                    verified_partial_document_facts(plan, coverage, self.c, NOW, self.store)

    def test_neutral_manifest_rejects_duplicate_or_nonarray_accession_inventory(self):
        result = self.run_pipeline(); plan = plan_run(self.c, NOW)
        for items in ([row()['accessionNumber']] * 2, None, {}, False, ['invalid-accession']):
            with self.subTest(items=items):
                receipts = copy.deepcopy(result['receipts'])
                manifest = json.loads(self.store.get(receipts[0]['itemManifest']))
                manifest['items'] = items
                receipts[0]['itemManifest'] = self.store.put(manifest)
                with self.assertRaises(ValueError):
                    reconcile(plan, receipts, self.c, NOW, self.store)

    def test_missing_archived_body_cannot_survive_independent_reconciliation(self):
        result = self.run_pipeline(); receipt = result['receipts'][0]
        observation = self.store.read('observations/' + receipt['observationIds'][0] + '.json')
        self.store._path(observation['body']['key']).unlink()
        with self.assertRaises((ValueError, FileNotFoundError)):
            reconcile(plan_run(self.c, NOW), result['receipts'], self.c, NOW, self.store)

    def test_neutral_index_never_enters_partial_semantic_release(self):
        result = self.run_pipeline(); coverage = copy.deepcopy(result)
        coverage['receipts'][0].update(outcome='not_checked', documentValidations=[{'url': INDEX}], validatedFacts=[{'sha256': 'a' * 64}])
        with self.assertRaisesRegex(ValueError, 'Neutral SEC index cannot release partial'):
            verified_partial_document_facts(plan_run(self.c, NOW), coverage, self.c, NOW, self.store)

    def test_two_segments_share_one_strict_parent_get_with_distinct_provenance_and_zero_facts(self):
        self.c = contract([binding('segment-a'), binding('segment-b')])
        result = self.run_pipeline()
        self.assert_neutral(result)
        self.assertEqual(len(self.fetcher.calls), 1)
        observations = [self.store.read('observations/' + r['observationIds'][0] + '.json') for r in result['receipts']]
        self.assertEqual(len({o['observationId'] for o in observations}), 2)
        self.assertEqual(len({o['sourceId'] for o in observations}), 2)
        self.assertEqual(len({o['transportId'] for o in observations}), 1)
        self.assertEqual({o['fetchedAt'] for o in observations}, {NOW})
        self.assertEqual(sum(o['transportReused'] for o in observations), 1)

    def test_neutral_index_runs_before_citations_in_deterministic_phase(self):
        citation = binding('citation-subject', 'direct'); citation.pop('regulatoryIssuer')
        citation.update(kind='citation', family='citation_integrity', url='https://example.test/citation', allowedHosts=['example.test'])
        self.c = contract([citation, binding()]); self.c['schedule']['maxWorkers'] = 1
        self.fetcher.pages[citation['url']] = b'<html>Retained citation body</html>'
        result = self.run_pipeline()
        self.assertTrue(result['complete'])
        self.assertEqual([call['url'] for call in self.fetcher.calls], [INDEX, citation['url']])

    def test_shared_parent_certified_route_remains_its_own_only_fact_subject(self):
        parent = binding('parent', 'direct')
        parent.update(kind='sec_submissions'); parent.pop('regulatoryIssuer')
        self.c = contract([binding('segment-a'), parent])
        self.structured.side_effect = lambda s, _docs, _day: [{'factId': 'a' * 64, 'supplierId': s['supplierId'],
                                                              'predicate': 'sec_revenue_snapshot', 'value': {'revenue': 123},
                                                              'assurance': 'sec_rederived'}]
        result = self.run_pipeline()
        self.assertTrue(result['complete'], result['receipts'])
        self.assertEqual(len(self.fetcher.calls), 1)
        self.assertEqual(self.structured.call_count, 1)
        self.assertEqual(self.structured.call_args.args[0]['supplierId'], 'parent')
        segment = next(r for r in result['receipts'] if r['supplierId'] == 'segment-a')
        self.assertEqual(segment['validatedFacts'], [])
        facts = [json.loads(self.store.get(ref)) for ref in eligible_fact_references(result)]
        self.assertEqual({f['supplierId'] for f in facts}, {'parent'})
        self.agent.extract.assert_not_called()

    def test_conditional_304_chains_are_separate_after_initial_shared_full_response(self):
        self.c = contract([binding('segment-a'), binding('segment-b')])
        first = self.run_pipeline(); self.assert_neutral(first)
        self.fetcher.calls.clear(); self.fetcher.conditional = True
        second = self.run_pipeline(); self.assert_neutral(second)
        self.assertEqual(len(self.fetcher.calls), 2)
        for receipt in second['receipts']:
            observed = self.store.read('observations/' + receipt['observationIds'][0] + '.json')
            prior = self.store.read('observations/' + observed['reusesObservationId'] + '.json')
            self.assertEqual(observed['sourceId'], prior['sourceId'])
            self.assertFalse(observed['transportReused'])

    def test_broader_or_ordinary_source_policy_does_not_share_strict_sec_response(self):
        pipeline = Pipeline(self.c, self.store, self.fetcher, clock=lambda: NOW)
        pipeline.budget_name = 'budget-2026-10-23'
        pipeline._fetch_transport(binding(), INDEX, None)
        broader = {**binding('other'), 'kind': 'citation', 'allowedHosts': ['data.sec.gov', 'www.sec.gov']}
        pipeline._fetch_transport(broader, INDEX, None)
        self.assertEqual(len(self.fetcher.calls), 2)
        self.assertEqual(self.fetcher.calls[0]['source']['allowedHosts'], ['data.sec.gov'])
        self.assertEqual(self.fetcher.calls[1]['source']['allowedHosts'], ['data.sec.gov', 'www.sec.gov'])

    def test_failed_strict_sec_response_is_not_shared(self):
        pipeline = Pipeline(self.c, self.store, self.fetcher, clock=lambda: NOW)
        pipeline.budget_name = 'budget-2026-10-23'
        self.fetcher.pages[INDEX] = 403
        pipeline._fetch_transport(binding(), INDEX, None)
        self.fetcher.pages[INDEX] = initial()
        pipeline._fetch_transport(binding('other'), INDEX, None)
        self.assertEqual(len(self.fetcher.calls), 2)

    def test_source_kind_family_relationship_and_issuer_shape_are_contract_rules(self):
        for mutate in ('kind', 'family', 'relationship', 'host', 'url'):
            candidate = contract()
            if mutate == 'kind': candidate['sources'][0]['kind'] = 'sec_submissions'
            elif mutate == 'family': candidate['sources'][0]['family'] = 'official_announcements'
            elif mutate == 'relationship': candidate['sources'][0]['regulatoryIssuer']['relationship'] = 'direct'
            elif mutate == 'host': candidate['sources'][0]['allowedHosts'].append('www.sec.gov')
            else: candidate['sources'][0]['url'] += '?extra=1'
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                validate_contract(candidate)

    def test_foreign_forms_are_retained_as_documents_without_fact_or_model_admission(self):
        filings = [row(f'0000123456-26-00000{i}', form=form, document=f'foreign{i}.htm')
                   for i, form in enumerate(('20-F', '20-F/A', '6-K', '6-K/A'), 1)]
        source = binding('foreign-public', 'direct'); source.pop('regulatoryIssuer')
        source.update(kind='sec_documents', family='filing_documents', cik=CIK,
                      allowedHosts=['data.sec.gov', 'www.sec.gov'])
        self.c = contract([source]); self.fetcher.pages = {INDEX: initial(filings)}
        urls = ['https://www.sec.gov/Archives/edgar/data/123456/' + r['accessionNumber'].replace('-', '') + '/' + r['primaryDocument'] for r in filings]
        self.fetcher.pages.update({url: b'<html><main>' + b'Foreign filing retained as a primary document only. ' * 10 + b'</main></html>' for url in urls})
        result = self.run_pipeline()
        self.assertTrue(result['complete'], result['receipts'])
        receipt = result['receipts'][0]
        self.assertEqual({d['url'] for d in receipt['documents']}, set(urls))
        self.assertEqual(receipt['validatedFacts'], [])
        self.assertEqual(eligible_fact_references(result), [])
        self.structured.assert_not_called(); self.agent.extract.assert_not_called()


if __name__ == '__main__':
    unittest.main()
