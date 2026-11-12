"""Offline, adversarial and recovery tests for the daily pipeline's real code."""
import copy
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import hashlib
import io
import zipfile
import importlib.util
from urllib.parse import urlsplit
from types import SimpleNamespace
from unittest.mock import patch
from datetime import datetime, timezone

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts/pipeline"
sys.path.insert(0, str(SCRIPTS))
from contracts import ContractError, canonical, digest, plan_run, validate_contract
from discovery import Page, discover, xml_links
from engine import Pipeline
from selection import select_documents, entity_url_priority
from release import release_daily
from fetcher import safe_url
from publication import health, prepare_release, publish, verify_acknowledgement
from storage import ConflictError, LocalStore
from validation import REVIEW_CHECKS, reconcile, verify_statement, eligible_fact_references
from reporting import inventory
from provenance import GitHubAuthority
from snapshot import build_snapshot, money
from agents import ModelUnavailable, SubscriptionAgent
from archive import GitArchive
from artifacts import build_artifact, stage_files, pack, unpack, inventory as artifact_inventory
from publication import recover_publication
from vercel import VercelAdapter
from native import NativeAgent, WorkPending, pending_work, submit_work

cloud_spec = importlib.util.spec_from_file_location("cloud_worker", SCRIPTS.parents[2] / "ops/ci/session_runtime.py")
cloud_worker = importlib.util.module_from_spec(cloud_spec)
cloud_spec.loader.exec_module(cloud_worker)

T = "2026-10-19T16:00:00Z"
QUOTE = "Fixture Vendor raised approximately $10 million on 2026-10-19."
URL = "https://example.invalid/releases/one"


def contract():
    return {"schemaVersion": 1, "version": "test-v1", "schedule": {"intervalHours": 24, "overdueHours": 30, "reconcileEveryRun": True, "maxWorkers": 1},
            "model": {"provider": "codex_subscription", "allowApiBilling": False, "maxDocumentsPerRun": 10, "maxCallsPerRun": 20, "maxDocumentChars": 30000, "timeoutSeconds": 5},
            "publication": {"enabled": False, "allowDegradedCoverage": True},
            "suppliers": [{"id": "fixture", "name": "Fixture Vendor", "kind": "private", "aliases": [], "sourceIds": ["official"], "requiredCategories": ["funding_valuation"], "requiredFamilies": ["official_announcements"]}],
            "sources": [{"id": "official", "supplierId": "fixture", "family": "official_announcements", "kind": "rss", "url": "https://example.invalid/feed.xml", "allowedHosts": ["example.invalid"], "registration": "verified", "required": True, "maxPages": 5, "scopePrefixes": ["/releases/"]}]}


def candidate():
    return {"supplierId": "fixture", "predicate": "funding", "valueText": QUOTE, "quote": QUOTE,
            "effectiveDate": "2026-10-19", "amount": "10000000", "currency": "USD", "qualifier": "approximately", "eventStatus": "reported", "scope": "company"}


def review(c, obs, policy):
    return {"result": "accepted", "candidateSha256": digest(c), "evidenceSha256": obs["body"]["sha256"], "policySha256": policy, "checks": {k: "pass" for k in REVIEW_CHECKS}}


class FakeFetcher:
    def __init__(self, store, pages=None):
        self.store = store
        self.pages = pages or {"https://example.invalid/feed.xml": b'<rss><channel><item><link>https://example.invalid/releases/one</link></item></channel></rss>', URL: f"<html><body>{QUOTE}</body></html>".encode()}

    def fetch(self, source, url, previous=None):
        body = self.pages[url]
        if isinstance(body, int):
            return {"requestedUrl": url, "fetchedAt": T, "status": "blocked", "httpStatus": body, "errorCode": f"HTTP_{body}"}
        return {"requestedUrl": url, "finalUrl": url, "fetchedAt": T, "status": "fetched", "httpStatus": 200, "body": self.store.put(body), "contentType": "text/html" if b"<html" in body else "application/xml"}


class FakeAgent:
    def __init__(self, empty=False):
        self.calls = 0
        self.empty = empty

    def extract(self, text, supplier):
        self.calls += 1
        return [] if self.empty else [candidate()]

    def review(self, text, c, obs, policy):
        self.calls += 1
        return review(c, obs, policy)

    def review_empty(self, text, supplier, obs, policy):
        self.calls += 1
        return {"noRelevantFacts": True, "evidenceSha256": obs["body"]["sha256"], "policySha256": policy}


class PipelineTests(unittest.TestCase):
    def duplicate_citation_fixture(self, compatible=True):
        self.c['sources'][0].update(kind='citation', family='citation_integrity', url=URL)
        clone = {**self.c['sources'][0], 'id': 'second'}
        if not compatible:
            clone['allowedHosts'] = ['example.invalid', 'other.invalid']
        self.c['sources'].append(clone)
        self.c['suppliers'][0]['sourceIds'].append('second')
        self.c['suppliers'][0]['requiredFamilies'] = ['citation_integrity']
        self.c['schedule'].update(maxWorkers=2, maxFetchesPerRun=1 if compatible else 2)

    def test_parallel_compatible_bindings_share_one_fetch_with_distinct_provenance(self):
        self.duplicate_citation_fixture()
        fetcher = FakeFetcher(self.store)
        original = fetcher.fetch
        def delayed(*args):
            time.sleep(0.02)
            return original(*args)
        with patch.object(fetcher, 'fetch', side_effect=delayed) as fetch:
            result = Pipeline(self.c, self.store, fetcher, clock=lambda: T).run(T)
        self.assertEqual(fetch.call_count, 1)
        self.assertTrue(result['complete'], result['receipts'])
        self.assertEqual(result['successfulTasks'], 2)
        observed = [self.store.read('observations/' + r['observationIds'][0] + '.json') for r in result['receipts']]
        self.assertEqual({o['sourceId'] for o in observed}, {'official', 'second'})
        self.assertEqual(len({o['observationId'] for o in observed}), 2)
        self.assertEqual(len({o['transportId'] for o in observed}), 1)
        self.assertEqual(sum(o['transportReused'] for o in observed), 1)
        self.assertEqual(self.store.read('heads/budget-' + T[:10] + '.json')['fetches'], 1)

    def test_incompatible_transport_host_policies_do_not_share(self):
        self.duplicate_citation_fixture(compatible=False)
        fetcher = FakeFetcher(self.store)
        with patch.object(fetcher, 'fetch', wraps=fetcher.fetch) as fetch:
            result = Pipeline(self.c, self.store, fetcher, clock=lambda: T).run(T)
        self.assertTrue(result['complete'])
        self.assertEqual(fetch.call_count, 2)

    def test_conditional_responses_keep_each_sources_own_retained_body_chain(self):
        self.duplicate_citation_fixture()
        self.c['schedule']['maxFetchesPerRun'] = 6
        self.run_pipeline()
        fetcher = FakeFetcher(self.store)
        def not_modified(source, url, previous):
            return {**previous, 'status': 'not_modified', 'httpStatus': 304,
                    'reusesObservationId': previous['observationId']}
        with patch.object(fetcher, 'fetch', side_effect=not_modified) as fetch:
            result = Pipeline(self.c, self.store, fetcher, clock=lambda: T).run(T, force_refresh=True)
        self.assertTrue(result['complete'])
        self.assertEqual(fetch.call_count, 2)
        for receipt in result['receipts']:
            observed = self.store.read('observations/' + receipt['observationIds'][0] + '.json')
            prior = self.store.read('observations/' + observed['reusesObservationId'] + '.json')
            self.assertEqual(prior['sourceId'], observed['sourceId'])

    def test_sec_index_pair_uses_shared_narrower_policy_and_archives_primary_text(self):
        source, document, index, pages = self.filing_fixture()
        second = {**source, 'id': 'submissions', 'kind': 'sec_submissions', 'family': 'regulatory_filings',
                  'allowedHosts': ['data.sec.gov']}
        self.c['sources'].append(second)
        self.c['suppliers'][0]['sourceIds'].append('submissions')
        self.c['suppliers'][0]['requiredFamilies'].append('regulatory_filings')
        self.c['schedule'].update(maxWorkers=2, maxFetchesPerRun=2)
        fetcher = FakeFetcher(self.store, pages)
        with patch.object(fetcher, 'fetch', wraps=fetcher.fetch) as fetch:
            result = Pipeline(self.c, self.store, fetcher, clock=lambda: T, structured=lambda *_: []).run(T)
        self.assertTrue(result['complete'], result['receipts'])
        self.assertEqual(fetch.call_count, 2)
        index_calls = [call for call in fetch.call_args_list if call.args[1] == source['url']]
        self.assertEqual(len(index_calls), 1)
        self.assertEqual(index_calls[0].args[0]['allowedHosts'], ['data.sec.gov'])

    def citation_retry_fixture(self):
        self.c['schedule']['maxFetchesPerRun'] = 1
        self.c['sources'][0].update(kind='citation', family='citation_integrity', url=URL)
        self.c['suppliers'][0]['requiredFamilies'] = ['citation_integrity']
        return self.run_pipeline()

    def test_exhausted_retry_reuses_hash_checked_success_without_refreshing_dates(self):
        first = self.citation_retry_fixture()
        fetcher = FakeFetcher(self.store)
        with patch.object(fetcher, 'fetch', side_effect=AssertionError('retry must not fetch')):
            second = Pipeline(self.c, self.store, fetcher, clock=lambda: T).run(T)
        self.assertTrue(second['complete'])
        self.assertEqual(second['receipts'], first['receipts'])
        self.assertEqual(self.store.read('heads/budget-' + T[:10] + '.json')['fetches'], 1)

    def test_success_can_recover_after_forced_cap_failure_overwrites_task_head(self):
        first = self.citation_retry_fixture()
        failed = self.run_pipeline()
        self.assertFalse(failed['complete'])
        self.assertEqual(failed['receipts'][0]['errorCode'], 'FETCHES_BUDGET_EXHAUSTED')
        recovered = Pipeline(self.c, self.store, FakeFetcher(self.store), clock=lambda: T).run(T)
        self.assertEqual(recovered['receipts'], first['receipts'])
        self.assertTrue(recovered['complete'])

    def test_fresh_receipt_cannot_reuse_stale_future_or_tampered_source(self):
        first = self.citation_retry_fixture()
        receipt = first['receipts'][0]
        path = self.store.root / ('observations/' + receipt['observationIds'][0] + '.json')
        original = json.loads(path.read_text())
        for stamp in ('2026-10-01T00:00:00Z', '2026-11-01T00:00:00Z'):
            path.write_text(json.dumps({**original, 'fetchedAt': stamp}))
            result = Pipeline(self.c, self.store, FakeFetcher(self.store), clock=lambda: T).run(T)
            self.assertFalse(result['complete'])
        path.write_text(json.dumps(original))
        (self.store.root / original['body']['key']).write_bytes(b'tampered')
        result = Pipeline(self.c, self.store, FakeFetcher(self.store), clock=lambda: T).run(T)
        self.assertFalse(result['complete'])

    def test_changed_policy_and_new_day_never_borrow_prior_task_success(self):
        first = self.citation_retry_fixture()
        changed = copy.deepcopy(self.c)
        changed['version'] = 'changed-policy'
        result = Pipeline(changed, self.store, FakeFetcher(self.store), clock=lambda: T).run(T)
        self.assertFalse(result['complete'])
        self.assertNotEqual(result['runId'], first['runId'])
        tomorrow = '2026-10-20T16:00:00Z'
        self.store.compare_and_swap('budget-' + tomorrow[:10], None, {'fetches': 1})
        result = Pipeline(self.c, self.store, FakeFetcher(self.store), clock=lambda: tomorrow).run(tomorrow)
        self.assertFalse(result['complete'])
        self.assertNotEqual(result['runId'], first['runId'])

    def test_blocked_or_malformed_prior_checks_never_earn_retry_success(self):
        self.c['schedule']['maxFetchesPerRun'] = 1
        self.c['sources'][0].update(kind='citation', family='citation_integrity', url=URL)
        self.c['suppliers'][0]['requiredFamilies'] = ['citation_integrity']
        blocked = self.run_pipeline(pages={URL: 403})
        self.assertEqual(blocked['receipts'][0]['outcome'], 'blocked')
        retried = Pipeline(self.c, self.store, FakeFetcher(self.store), clock=lambda: T).run(T)
        self.assertFalse(retried['complete'])

    def test_changed_attempt_json_cannot_override_content_addressed_success(self):
        first = self.citation_retry_fixture()
        receipt = first['receipts'][0]
        path = self.store.root / f"runs/{first['runId']}/attempts/{receipt['attemptId']}.json"
        path.write_text(json.dumps({**receipt, 'supplierId': 'forged'}))
        result = Pipeline(self.c, self.store, FakeFetcher(self.store), clock=lambda: T).run(T)
        self.assertFalse(result['complete'])

    def test_gate_attempt_is_checkpointed_before_external_dispatch(self):
        self.c["publication"].update(enabled=True, maxBatchesPerDay=2)
        self.store.write_once("releases/old.json", {"manifest": {}})
        self.store.compare_and_swap("latest-run", None, {"receipt": {"sha256": "a" * 64}})
        saved = []
        def checkpoint():
            # Simulate remote archival of the reservation immediately followed
            # by runner death before the external dispatch begins.
            saved.extend(p.read_text() for p in self.store.root.glob("heads/gate-budget-*.json"))
            raise RuntimeError("runner terminated")
        with patch("release.VercelAdapter") as adapter, patch("release.recover_publication", return_value={"releaseId": "old"}), patch("release.dispatch_gate") as dispatch, patch("release.preflight_corrections"):
            adapter.return_value.production_paths_controlled.return_value = True
            with self.assertRaisesRegex(RuntimeError, "runner terminated"):
                release_daily(self.store, self.c, {}, "b" * 40, {"vercel": {"project_id": "fixture"}}, checkpoint)
            dispatch.assert_not_called()
        self.assertEqual([json.loads(s)["attempts"] for s in saved], [1])

    def test_delta_selection_bounds_history_and_prioritizes_changed_current_documents(self):
        policy = {"currentWindowDays": 30, "maxDocumentsPerSource": 2, "maxAuditDocumentsPerSource": 1}
        found = {"items": ["old", "unknown", "new", "changed"], "itemModified": {"old": "2020-01-01", "new": "2026-10-19", "changed": "2026-10-20"}}
        history = {"changed": {"modified": "2026-10-18", "checkedAt": T}}
        selected, pending = select_documents(found, history, policy, T)
        self.assertEqual(selected, ["changed", "new"])
        self.assertEqual(pending, ["old", "unknown"])
        self.assertEqual(set(selected + pending), set(found["items"]))

    def test_undated_and_historical_audit_is_finite_and_rotates_after_success(self):
        policy = {"currentWindowDays": 30, "maxDocumentsPerSource": 2, "maxAuditDocumentsPerSource": 1}
        found = {"items": ["a", "b", "c"], "itemModified": {}}
        selected, pending = select_documents(found, {}, policy, T)
        self.assertEqual(selected, ["a"])
        self.assertEqual(pending, ["b", "c"])
        selected, pending = select_documents(found, {"a": {"modified": "", "checkedAt": T}}, policy, T)
        self.assertEqual(selected, ["b"])
        self.assertEqual(pending, ["c"])

    def test_successful_unchanged_inventory_has_no_false_pending_and_is_not_mutated(self):
        policy = {"currentWindowDays": 30, "maxDocumentsPerSource": 2, "maxAuditDocumentsPerSource": 1}
        found = {"items": ["a", "b"], "itemModified": {"a": "2026-10-19"}}
        history = {u: {"modified": found['itemModified'].get(u, ''), "checkedAt": T} for u in found['items']}
        before = json.dumps([found, history], sort_keys=True)
        self.assertEqual(select_documents(found, history, policy, T), ([], []))
        self.assertEqual(json.dumps([found, history], sort_keys=True), before)

    def test_pending_contains_only_unselected_due_work_including_failed_stale_changed_and_invalid(self):
        policy = {"currentWindowDays": 30, "maxDocumentsPerSource": 1, "maxAuditDocumentsPerSource": 1}
        found = {"items": ["valid", "failed", "stale", "changed", "malformed", "future"],
                 "itemModified": {"changed": "2026-10-20"}}
        history = {"valid": {"modified": "", "checkedAt": T},
                   "stale": {"modified": "", "checkedAt": "2020-01-01T00:00:00Z"},
                   "changed": {"modified": "2026-10-18", "checkedAt": T},
                   "malformed": {"modified": "", "checkedAt": "invalid"},
                   "future": {"modified": "", "checkedAt": "2099-01-01T00:00:00Z"}}
        # A failed review produces no successful history entry.
        selected, pending = select_documents(found, history, policy, T)
        self.assertEqual(selected, ["changed"])
        self.assertEqual(set(pending), {"failed", "stale", "malformed", "future"})

    def test_mixed_invalid_audit_cursor_types_remain_due_and_sort_safely(self):
        policy = {"currentWindowDays": 30, "maxDocumentsPerSource": 1, "maxAuditDocumentsPerSource": 1}
        found = {"items": ["none", "number", "missing", "bad", "future", "stale", "valid"], "itemModified": {}}
        history = {u: {"modified": "", "checkedAt": stamp} for u, stamp in
                   [("none", None), ("number", 42), ("bad", "invalid"),
                    ("future", "2099-01-01T00:00:00Z"), ("stale", "2020-01-01T00:00:00Z"), ("valid", T)]}
        history['missing'] = {"modified": ""}
        selected, pending = select_documents(found, history, policy, T)
        self.assertEqual(len(selected), 1)
        self.assertEqual(set(selected + pending), set(found['items']) - {'valid'})

    def test_shared_publisher_prioritizes_registered_entity_without_dropping_other_urls(self):
        supplier = {'name': 'Dragos, Inc.', 'aliases': ['Dragos']}
        relevant = 'https://newsroom.invalid/news/2026/accenture-dragos-acquisition'
        generic = ['https://newsroom.invalid/news/z-other', 'https://newsroom.invalid/news/y-other']
        found = {'items': [relevant, *generic], 'itemModified': {relevant: '2026-10-18', **{u: '2026-10-19' for u in generic}}}
        policy = {'currentWindowDays': 30, 'maxDocumentsPerSource': 2, 'maxAuditDocumentsPerSource': 1}
        selected, deferred = select_documents(found, {}, policy, T, supplier=supplier)
        self.assertEqual(selected[0], relevant)
        self.assertEqual(len(selected), 2)
        self.assertEqual(set(selected + deferred), set(found['items']))

    def test_entity_history_does_not_displace_current_work_or_expand_audit_allowance(self):
        supplier = {'name': 'Dragos, Inc.', 'aliases': ['Dragos']}
        current = ['https://newsroom.invalid/news/generic-a', 'https://newsroom.invalid/news/generic-b']
        archived = 'https://newsroom.invalid/news/2020/dragos-funding'
        undated = 'https://newsroom.invalid/news/dragos-undated'
        found = {'items': [*current, archived, undated], 'itemModified': {**{u: '2026-10-19' for u in current}, archived: '2020-01-01'}}
        policy = {'currentWindowDays': 30, 'maxDocumentsPerSource': 2, 'maxAuditDocumentsPerSource': 1}
        selected, deferred = select_documents(found, {}, policy, T, supplier=supplier)
        self.assertEqual(set(selected), set(current))
        self.assertEqual(set(deferred), {archived, undated})
        found['items'] = [archived, undated, 'https://newsroom.invalid/news/z-generic']
        selected, deferred = select_documents(found, {}, policy, T, supplier=supplier)
        self.assertEqual(len(selected), 1)
        self.assertIn(selected[0], (archived, undated))
        self.assertEqual(len(deferred), 2)

    def test_entity_url_priority_uses_whole_unambiguous_registered_slugs(self):
        dragos = {'name': 'Dragos, Inc.', 'aliases': ['D', 'Dragos']}
        self.assertTrue(entity_url_priority('https://publisher.invalid/news/dragos-funding', dragos))
        for url in ('https://dragos.invalid/news/other', 'https://publisher.invalid/news/notdragos',
                    'https://publisher.invalid/news/dragostechnology', 'https://publisher.invalid/news/other?q=dragos'):
            self.assertFalse(entity_url_priority(url, dragos))
        self.assertFalse(entity_url_priority('https://publisher.invalid/news/aqua-funding', {'name': 'Aqua', 'aliases': ['IBM', 'Wiz']}))
        self.assertFalse(entity_url_priority('https://publisher.invalid/news/security-update', {'name': 'Security, Inc.', 'aliases': []}))
        self.assertTrue(entity_url_priority('https://publisher.invalid/news/check-point-results', {'name': 'Check Point', 'aliases': []}))
        self.assertTrue(entity_url_priority('https://publisher.invalid/news/checkpoint-results', {'name': 'Check Point', 'aliases': []}))

    def test_bounded_collection_keeps_full_inventory_and_partial_facts(self):
        self.c["collection"] = {"mode": "delta_with_retained_audit", "currentWindowDays": 30, "maxDocumentsPerSource": 2, "maxAuditDocumentsPerSource": 1}
        pages = {"https://example.invalid/feed.xml": b'<rss><channel><item><link>https://example.invalid/releases/one</link></item><item><link>https://example.invalid/releases/two</link></item></channel></rss>', URL: f"<html><body>{QUOTE}</body></html>".encode()}
        result = self.run_pipeline(pages=pages)
        receipt = result["receipts"][0]
        self.assertFalse(result["complete"])
        self.assertEqual(receipt["outcome"], "not_checked")
        self.assertEqual(receipt["pendingDocuments"], 1)
        self.assertEqual(len(receipt["validatedFacts"]), 1)
        self.assertEqual(json.loads(self.store.get(receipt["pendingManifest"]))["items"], ["https://example.invalid/releases/two"])
        self.assertIsNone(self.store.read(f"heads/source-{digest('official')}.json"))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(self.temp.name)
        self.c = contract()

    def run_pipeline(self, c=None, agent=None, pages=None):
        return Pipeline(c or self.c, self.store, FakeFetcher(self.store, pages), agent or FakeAgent(), clock=lambda: T).run(T, force_refresh=True)

    def source_observation(self, text=QUOTE):
        body = self.store.put(text.encode())
        return {"observationId": "source-one", "sourceId": "official", "requestedUrl": URL, "body": body, "status": "fetched", "fetchedAt": T}

    def assert_bad_candidate(self, mutate, text=QUOTE):
        c = candidate(); mutate(c)
        obs = self.source_observation(text)
        with self.assertRaises(ContractError):
            verify_statement(c, obs, self.store, review(c, obs, digest(self.c)), self.c["suppliers"][0], digest(self.c))

    def test_canonical_hash_has_no_key_order_dependency(self):
        self.assertEqual(digest({"b": 2, "a": 1}), digest({"a": 1, "b": 2}))

    def test_article_extraction_excludes_unrelated_navigation_and_preserves_nested_main_content(self):
        text='Fixture Vendor publishes its announcement here. '+('This is the dated primary article. '*5)
        page=Page('<header>Unrelated old funding banner</header><div role="main"><div>'+text+'</div><p>Final article paragraph.</p></div><footer>Unrelated footer</footer>')
        self.assertIn('Final article paragraph.',page.readable)
        self.assertNotIn('funding banner',page.readable)
        self.assertNotIn('Unrelated footer',page.readable)

    def test_unique_article_publication_metadata_is_read_but_ambiguous_dates_are_held(self):
        one='<script type="application/ld+json">{"@type":"NewsArticle","datePublished":"2026-10-19"}</script>'
        two='<script type="application/ld+json">{"@type":"NewsArticle","datePublished":"2025-01-01"}</script>'
        self.assertEqual(Page(one).published,'2026-10-19')
        self.assertIsNone(Page(one+two).published)

    def test_labeled_publication_time_is_read_without_borrowing_an_event_or_listing_date(self):
        time='<div class="press-release-details__date"><time datetime="2019-11-13">Nov 13, 2019</time></div>'
        page=Page('<main>'+time+'<p>Announcement body</p></main>')
        self.assertEqual(page.published, '2019-11-13')
        self.assertTrue(page.published_from_time)
        self.assertIsNone(Page('<main><time datetime="2026-10-19">Upcoming event</time></main>').published)
        self.assertIsNone(Page('<main>'+time+time.replace('2019-11-13','2020-07-29')+'</main>').published)
        self.assertIsNone(Page('<main>'+time.replace('2019-11-13','2019-02-30')+'</main>').published)
        self.assertIsNone(Page('<time itemprop="dateModified" datetime="2026-10-19">Updated</time>').published)
        self.assertEqual(Page('<article><time itemprop="datePublished" datetime="2026-10-19T09:00:00Z">Published</time></article>').published,'2026-10-19')
        self.assertIsNone(Page('<aside>'+time+'</aside>').published)
        self.assertIsNone(Page('<main><div class="post-date"><time datetime="2026-10-19">Related article</time></div></main>').published)

    def test_existing_publication_metadata_keeps_its_cache_and_ambiguous_metadata_stays_held(self):
        time='<main><div class="press-release-details__date"><time datetime="2026-10-19">Published</time></div></main>'
        page=Page('<meta property="article:published_time" content="2026-10-18">'+time)
        self.assertEqual(page.published,'2026-10-18')
        self.assertFalse(page.published_from_time)
        ambiguous=''.join('<script type="application/ld+json">'+json.dumps({'@type':'NewsArticle','datePublished':d})+'</script>' for d in ['2026-10-17','2026-10-18'])
        self.assertIsNone(Page(ambiguous+time).published)

    def test_new_publication_time_reextracts_old_held_cache_then_reuses_reviewed_result(self):
        statement='Fixture Vendor raised approximately $10 million.'
        html=('<html><main><div class="press-release-details__date"><time datetime="2026-10-19">Oct 19, 2026</time></div><p>'+statement+'</p></main></html>').encode()
        pages={'https://example.invalid/feed.xml':b'<rss><channel><item><link>'+URL.encode()+b'</link></item></channel></rss>',URL:html}
        old_key=digest({'supplier':'fixture','body':digest(html),'contract':digest(self.c),'extractor':3})
        self.store.write_once('document-extractions/'+old_key+'.json',{'candidates':[{**candidate(),'effectiveDate':None}],'body':self.store.put(html),'policySha256':digest(self.c)})
        agent=FakeAgent()
        def extract(text,supplier):
            agent.calls+=1
            self.assertIn('Source publication date metadata: 2026-10-19',text)
            return [{**candidate(),'valueText':statement,'quote':statement}]
        agent.extract=extract
        first=self.run_pipeline(agent=agent,pages=pages)
        self.assertTrue(first['complete'])
        self.assertEqual(agent.calls,2)
        self.assertTrue(self.run_pipeline(agent=agent,pages=pages)['complete'])
        self.assertEqual(agent.calls,2)

    def test_daily_identity_uses_utc_even_when_input_has_an_offset(self):
        a=plan_run(self.c,'2026-10-20T00:30:00Z');b=plan_run(self.c,'2026-10-19T17:30:00-07:00')
        self.assertEqual(a['runId'],b['runId']);self.assertEqual(a['scheduledAt'],b['scheduledAt'])

    def test_expansion_has_no_hardcoded_supplier_limit(self):
        c = contract()
        for i in range(250):
            s = copy.deepcopy(c["suppliers"][0]); s.update(id=f"more-{i}", sourceIds=[]); c["suppliers"].append(s)
        validate_contract(c)
        self.assertEqual(len(plan_run(c, T)["supplierIds"]), 251)

    def test_paid_api_fallback_is_rejected(self):
        self.c["model"]["allowApiBilling"] = True
        with self.assertRaises(ContractError): validate_contract(self.c)

    def test_missing_family_stays_in_denominator(self):
        self.c["suppliers"][0]["requiredFamilies"].append("independent_reporting")
        result = self.run_pipeline()
        self.assertFalse(result["complete"])
        self.assertEqual((result["requiredTasks"], result["successfulTasks"]), (2, 1))

    def test_weekly_reconciliation_cannot_replace_daily(self):
        self.c["schedule"]["reconcileEveryRun"] = False
        with self.assertRaises(ContractError): validate_contract(self.c)

    def test_duplicate_supplier_is_rejected(self):
        self.c["suppliers"].append(copy.deepcopy(self.c["suppliers"][0]))
        with self.assertRaises(ContractError): validate_contract(self.c)

    def test_immutable_object_overwrite_is_rejected(self):
        self.store.write_once("receipts/one.json", {"a": 1})
        with self.assertRaises(ContractError): self.store.write_once("receipts/one.json", {"a": 2})

    def test_object_tamper_is_detected_on_read(self):
        ref = self.store.put(b"original")
        (self.store.root / ref["key"]).write_bytes(b"tampered")
        with self.assertRaises(ContractError): self.store.get(ref)

    def test_state_path_cannot_escape_store(self):
        with self.assertRaises(ContractError): self.store.write_once("../outside", b"x")

    def test_stale_release_cas_rejected(self):
        self.store.compare_and_swap("production", None, {"sequence": 1})
        with self.assertRaises(ConflictError): self.store.compare_and_swap("production", None, {"sequence": 2})

    def test_restore_is_independent_of_original_workspace(self):
        result = self.run_pipeline()
        # Keep the backup outside the traversed archive root.
        with tempfile.TemporaryDirectory() as dst:
            exported = self.store.export(dst)
            LocalStore.verify_export(dst, exported['manifestSha256'])
            restored = LocalStore(dst)
            head = restored.read("heads/latest-run.json")
            self.assertEqual(json.loads(restored.get(head["receipt"])), result)

    def test_backup_root_must_match_independent_receipt(self):
        self.store.put(b'evidence')
        with tempfile.TemporaryDirectory() as dst:
            self.store.export(dst)
            with self.assertRaises(ContractError): LocalStore.verify_export(dst,'0'*64)

    def test_lock_releases_after_worker_process_crash(self):
        code = "import sys,os;sys.path.insert(0,sys.argv[1]);from storage import LocalStore\nwith LocalStore(sys.argv[2]).lock('crash'):os._exit(0)"
        result = subprocess.run([sys.executable,'-c',code,str(SCRIPTS),self.temp.name],capture_output=True,timeout=5)
        self.assertEqual(result.returncode,0,result.stderr.decode())
        with self.store.lock('crash'): pass

    def test_kernel_lock_prevents_concurrent_publishers(self):
        with self.store.lock("production-publisher"):
            with self.assertRaises(ConflictError):
                with LocalStore(self.temp.name).lock("production-publisher"): pass

    def test_valid_source_fact_is_accepted(self):
        obs = self.source_observation()
        fact = verify_statement(candidate(), obs, self.store, review(candidate(), obs, digest(self.c)), self.c["suppliers"][0], digest(self.c))
        self.assertEqual(fact["assurance"], "source_statement_matched")

    def test_value_not_in_source_is_rejected(self):
        self.assert_bad_candidate(lambda c:c.update(amount="20000000"))

    def test_dropped_qualifier_is_rejected(self):
        self.assert_bad_candidate(lambda c:c.update(qualifier="exact"))

    def test_at_least_qualifier_cannot_be_dropped(self):
        text=QUOTE.replace("approximately", "at least")
        self.assert_bad_candidate(lambda c:c.update(quote=text,valueText=text,qualifier="exact"),text)

    def test_qualifier_changes_produce_distinct_assertions(self):
        c=candidate();obs=self.source_observation()
        a=verify_statement(c,obs,self.store,review(c,obs,digest(self.c)),self.c['suppliers'][0],digest(self.c))
        text=QUOTE.replace('approximately','at least');c.update(quote=text,valueText=text,qualifier='at_least');obs=self.source_observation(text)
        b=verify_statement(c,obs,self.store,review(c,obs,digest(self.c)),self.c['suppliers'][0],digest(self.c))
        self.assertNotEqual(a['factId'],b['factId'])

    def test_currency_mismatch_is_rejected(self):
        self.assert_bad_candidate(lambda c:c.update(currency="EUR"))

    def test_arr_cannot_become_revenue(self):
        self.assert_bad_candidate(lambda c:c.update(predicate="revenue", quote="Fixture Vendor reported approximately $10 million ARR on 2026-10-19.", valueText="Fixture Vendor reported approximately $10 million ARR on 2026-10-19."), "Fixture Vendor reported approximately $10 million ARR on 2026-10-19.")

    def test_future_acquisition_cannot_be_closed(self):
        text="Fixture Vendor plans to acquire a company on 2026-10-19."
        self.assert_bad_candidate(lambda c:c.update(predicate="acquisition", eventStatus="closed", quote=text, valueText=text, amount=None, currency=None), text)

    def test_unmatched_entity_is_rejected(self):
        self.assert_bad_candidate(lambda c:c.update(supplierId="another"))

    def test_missing_date_is_held(self):
        self.assert_bad_candidate(lambda c:c.update(effectiveDate=None))

    def test_unsupported_opinion_is_rejected(self):
        self.assert_bad_candidate(lambda c:c.update(predicate="financially_healthy"))

    def test_fabricated_quote_is_rejected(self):
        self.assert_bad_candidate(lambda c:c.update(quote="Invented statement about Fixture Vendor."))

    def test_stale_review_of_changed_value_is_rejected(self):
        obs=self.source_observation(); c=candidate(); proof=review(c,obs,digest(self.c)); c["eventStatus"]="announced"
        with self.assertRaises(ContractError): verify_statement(c,obs,self.store,proof,self.c["suppliers"][0],digest(self.c))

    def test_independent_reviewer_disagreement_is_held(self):
        obs=self.source_observation(); proof=review(candidate(),obs,digest(self.c));proof["checks"]["entity"]="unknown"
        with self.assertRaises(ContractError): verify_statement(candidate(),obs,self.store,proof,self.c["suppliers"][0],digest(self.c))

    def test_duplicate_wire_fact_has_one_identity(self):
        obs=self.source_observation(); a=verify_statement(candidate(),obs,self.store,review(candidate(),obs,digest(self.c)),self.c["suppliers"][0],digest(self.c))
        other={**obs,"observationId":"wire-copy"}
        b=verify_statement(candidate(),other,self.store,review(candidate(),other,digest(self.c)),self.c["suppliers"][0],digest(self.c))
        self.assertEqual(a["factId"],b["factId"])

    def test_concurrent_sources_share_document_validation_without_collisions(self):
        self.c['schedule']['maxWorkers']=2
        extra=copy.deepcopy(self.c['sources'][0]);extra['id']='wire-copy'
        self.c['sources'].append(extra);self.c['suppliers'][0]['sourceIds'].append('wire-copy')
        agent=FakeAgent();result=self.run_pipeline(agent=agent)
        self.assertTrue(result['complete']);self.assertEqual(result['successfulTasks'],2)
        self.assertEqual(agent.calls,2)
        self.assertEqual(len(list((self.store.root/'facts').glob('*.json'))),1)

    def test_full_cycle_is_idempotent_and_cache_saves_model_calls(self):
        first=self.run_pipeline(); self.assertTrue(first["complete"])
        agent=FakeAgent(); second=self.run_pipeline(agent=agent)
        self.assertTrue(second["complete"]); self.assertEqual(agent.calls,0)
        self.assertEqual(second["receipts"][0]["outcome"],"checked_no_change")
        self.assertEqual(len(list((self.store.root/"facts").glob('*.json'))),1)
        self.assertEqual(len(eligible_fact_references(second)),1)

    def test_native_cloud_roundtrip_separates_review_and_replays_without_refetch_or_rebudget(self):
        self.c['model']['maxDocumentsPerRun']=1
        self.c['model']['maxCallsPerRun']=2
        calls = []
        fetcher = FakeFetcher(self.store)
        original_fetch = fetcher.fetch
        def counted(*args):
            calls.append(args[1])
            return original_fetch(*args)
        fetcher.fetch = counted
        def advance(session):
            agent = NativeAgent(self.c['model'], self.store, digest(self.c), session, clock=lambda:T)
            return Pipeline(self.c, self.store, fetcher, agent, clock=lambda:T).run(T, replay=True)
        first = advance('collector-context')
        self.assertFalse(first['complete'])
        extract = pending_work(self.store, digest(self.c), 'collector', T)[0]
        submit_work(self.store,extract['taskId'],{'facts':[candidate()]},'collector','collector-context',digest(self.c),T)
        second = advance('governance-context')
        self.assertFalse(second['complete'])
        task = pending_work(self.store,digest(self.c),'governance',T)[0]
        obs = self.store.read('observations/'+second['receipts'][0]['observationIds'][-1]+'.json')
        answer = review(candidate(),obs,digest(self.c))
        with self.assertRaisesRegex(ContractError,'SEPARATE_CONTEXT'):
            submit_work(self.store,task['taskId'],answer,'governance','collector-context',digest(self.c),T)
        submit_work(self.store,task['taskId'],answer,'governance','governance-context',digest(self.c),T)
        third = advance('governance-context')
        self.assertTrue(third['complete'])
        self.assertEqual(len(eligible_fact_references(third)),1)
        self.assertEqual(len(calls),2) # current feed + article, not one download per model round
        budget = self.store.read('heads/budget-2026-10-19.json')
        self.assertEqual(budget,{'calls':2,'documents':1,'fetches':2})
        self.assertTrue(advance('governance-context')['complete'])
        self.assertEqual(self.store.read('heads/budget-2026-10-19.json'),budget)

    def test_fresh_cloud_bootstrap_restores_remote_state_and_excludes_overlapping_sessions(self):
        remote=Path(self.temp.name)/'cloud-remote.git'
        subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True)
        original=LocalStore(Path(self.temp.name)/'original')
        original.compare_and_swap('budget-day',None,{'calls':7})
        GitArchive(Path(self.temp.name)/'initial-mirror',str(remote)).push(original)
        def local_archive(root):return GitArchive(root/'archive',str(remote))
        def fake_git(*args):return 'a'*40 if args[0]=='rev-parse' else ''
        mock_process=SimpleNamespace(run=lambda *_args,**_kwargs:SimpleNamespace(stdout='v22.23.3'))
        root=Path(self.temp.name)/'cloud-one'
        with patch.object(cloud_worker,'archive_for',local_archive),patch.object(cloud_worker,'git',fake_git),patch.object(cloud_worker,'subprocess',mock_process),patch.object(cloud_worker.shutil,'which',return_value='/installed'):
            receipt=cloud_worker.bootstrap(root,'collector','cloud-one','a'*40)
            restored=LocalStore(root/'state')
            self.assertEqual(restored.read('heads/budget-day.json'),{'calls':7})
            self.assertEqual(receipt['archive']['commit'],LocalStore(root).read('heads/remote-archive.json')['commit'])
            with self.assertRaisesRegex(ContractError,'ACTIVE_LEASE'):
                cloud_worker.bootstrap(Path(self.temp.name)/'cloud-two','governance','cloud-two','a'*40)
            session=LocalStore(root).read('session.json')
            cloud_worker.checkpoint(root,restored,session,'finish',{'trial':True},finish=True)
            second=cloud_worker.bootstrap(Path(self.temp.name)/'cloud-three','governance','cloud-three','a'*40)
            self.assertEqual(second['receipt']['role'],'governance')
            self.assertFalse(second['receipt']['coverage']['complete'])

    def test_expired_cloud_lease_can_be_recovered_but_expired_owner_cannot_continue(self):
        session={'sessionId':'one','role':'collector'}
        cloud_worker.acquire_lease(self.store,session,T)
        with self.assertRaisesRegex(ContractError,'EXPIRED'):
            cloud_worker.require_lease(self.store,session,'2026-10-19T20:00:00Z')
        next_session={'sessionId':'two','role':'governance'}
        cloud_worker.acquire_lease(self.store,next_session,'2026-10-19T20:00:00Z')
        with self.assertRaises(ContractError):cloud_worker.require_lease(self.store,session,'2026-10-19T20:01:00Z')

    def test_native_queue_rejects_wrong_role_policy_schema_staleness_and_answer_overwrite(self):
        agent=NativeAgent(self.c['model'],self.store,digest(self.c),'collector-context',clock=lambda:T)
        agent.reserve=lambda *_:None
        with self.assertRaises(WorkPending):agent.extract(QUOTE,self.c['suppliers'][0])
        task=pending_work(self.store,digest(self.c),'collector',T)[0]
        for answer,role,policy,at in [({'facts':[]},'governance',digest(self.c),T),
                                     ({'facts':[]},'collector','a'*64,T),
                                     ({'facts':[],'extra':True},'collector',digest(self.c),T),
                                     ({'facts':[]},'collector',digest(self.c),'2026-10-21T16:00:00Z')]:
            with self.assertRaises(ContractError):submit_work(self.store,task['taskId'],answer,role,'collector-context',policy,at)
        submit_work(self.store,task['taskId'],{'facts':[]},'collector','collector-context',digest(self.c),T)
        with self.assertRaisesRegex(ContractError,'ALREADY_SEALED'):
            submit_work(self.store,task['taskId'],{'facts':[candidate()]},'collector','collector-context',digest(self.c),T)
        self.assertEqual(agent.extract(QUOTE,self.c['suppliers'][0]),[])

    def test_exhausted_model_budget_stops_backlog_downloads_but_keeps_missing_inventory(self):
        class AtCapacity(FakeAgent):
            def extract(self,*_):raise ModelUnavailable('SUBSCRIPTION_LIMIT_REACHED')
        pages=FakeFetcher(self.store).pages
        urls=[f'https://example.invalid/releases/{i}' for i in range(50)]
        pages['https://example.invalid/feed.xml']=('<rss><channel>'+''.join(f'<item><link>{u}</link></item>' for u in urls)+'</channel></rss>').encode()
        for u in urls:pages[u]=b'<html><body>Fixture Vendor news.</body></html>'
        result=self.run_pipeline(agent=AtCapacity(),pages=pages)
        self.assertFalse(result['complete'])
        receipt=result['receipts'][0]
        self.assertEqual(receipt['pendingDocuments'],50)
        self.assertEqual(len(json.loads(self.store.get(receipt['itemManifest']))['items']),50)
        self.assertEqual(len(receipt['observationIds']),2)

    def test_budget_reservations_survive_restarts(self):
        self.c['model']['maxDocumentsPerRun']=1
        result=self.run_pipeline(agent=FakeAgent(empty=True));self.assertFalse(result['complete'])
        pages=FakeFetcher(self.store).pages
        pages[URL]+=b' changed'
        result=self.run_pipeline(pages=pages);self.assertFalse(result['complete'])
        self.assertEqual(result['receipts'][0]['errorCode'],'DOCUMENTS_BUDGET_EXHAUSTED')

    def test_rejected_claim_is_quarantined_without_blocking_a_supported_fact(self):
        class DisagreesSecond(FakeAgent):
            def extract(self,text,supplier):
                second=candidate();second['predicate']='valuation'
                return [candidate(),second]
            def review(self,text,c,obs,policy):
                self.calls+=1
                proof=review(c,obs,policy)
                if self.calls==2: proof['result']='rejected'
                return proof
        result=self.run_pipeline(agent=DisagreesSecond())
        self.assertTrue(result['complete'])
        self.assertEqual(len(eligible_fact_references(result)),1)
        self.assertEqual(len(result['receipts'][0]['heldClaims']),1)
        snapshot=build_snapshot(self.c,plan_run(self.c,T),result,self.store,T)
        self.assertEqual(len(snapshot['events']),1)
        self.assertTrue(any(q['reason']=='Independent review did not accept' for q in snapshot['reviewQueue']))

    def test_partial_download_task_facts_are_not_eligible_and_cursor_does_not_advance(self):
        pages=FakeFetcher(self.store).pages
        pages['https://example.invalid/feed.xml']=b'<rss><channel><item><link>https://example.invalid/releases/one</link></item><item><link>https://example.invalid/releases/two</link></item></channel></rss>'
        pages['https://example.invalid/releases/two']=403
        result=self.run_pipeline(pages=pages)
        self.assertFalse(result['complete']);self.assertEqual(eligible_fact_references(result),[])
        self.assertIsNone(self.store.read('heads/source-'+digest('official')+'.json'))

    def test_unauthenticated_collection_archives_all_pending_documents_without_advancing(self):
        pages=FakeFetcher(self.store).pages
        pages['https://example.invalid/feed.xml']=b'<rss><channel><item><link>https://example.invalid/releases/one</link></item><item><link>https://example.invalid/releases/two</link></item></channel></rss>'
        pages['https://example.invalid/releases/two']=pages[URL]
        result=Pipeline(self.c,self.store,FakeFetcher(self.store,pages),clock=lambda:T).run(T)
        self.assertFalse(result['complete'])
        receipt=result['receipts'][0]
        self.assertEqual(receipt['pendingDocuments'],2)
        self.assertEqual(len(receipt['observationIds']),3)
        self.assertIsNone(self.store.read('heads/source-'+digest('official')+'.json'))

    def test_governance_rejects_a_downloaded_document_without_semantic_accounting(self):
        result=self.run_pipeline()
        result['receipts'][0]['documentValidations']=[]
        with self.assertRaises(ContractError):reconcile(plan_run(self.c,T),result['receipts'],self.c,T,self.store)

    def test_remote_archive_restores_without_original_worker_and_rejects_tampering(self):
        remote=Path(self.temp.name)/'remote.git'
        subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True)
        state=LocalStore(Path(self.temp.name)/'live')
        ref=state.put(b'real archived evidence')
        state.compare_and_swap('latest-run',None,{'receipt':ref})
        archive=GitArchive(Path(self.temp.name)/'mirror',str(remote))
        receipt=archive.push(state)
        archived_path=archive.root/'state'/ref['key'];stamp=archived_path.stat().st_mtime_ns
        self.assertEqual(archive.push(state)['commit'],receipt['commit'])
        self.assertEqual(archived_path.stat().st_mtime_ns,stamp)
        destination=Path(self.temp.name)/'restored'
        restored=GitArchive(Path(self.temp.name)/'fresh-mirror',str(remote)).restore(destination,receipt['commit'],receipt['manifestSha256'])
        self.assertEqual(receipt['manifestSha256'],restored['manifestSha256'])
        self.assertEqual(LocalStore(destination).get(ref),b'real archived evidence')
        (archive.root/'state'/ref['key']).write_bytes(b'corrupt')
        with self.assertRaises(ContractError):GitArchive.verify(archive.root,receipt['manifestSha256'])

    def test_linked_restore_keeps_mirror_and_state_independent(self):
        remote=Path(self.temp.name)/'remote.git'
        subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True)
        live=LocalStore(Path(self.temp.name)/'live')
        ref=live.put(b'evidence body')
        live.compare_and_swap('latest-run',None,{'receipt':ref})
        GitArchive(Path(self.temp.name)/'seed',str(remote)).push(live)
        mirror=GitArchive(Path(self.temp.name)/'mirror',str(remote))
        destination=Path(self.temp.name)/'restored'
        receipt=mirror.restore(destination)
        state=LocalStore(destination)
        # Restored files share storage with the mirror instead of a second copy.
        self.assertEqual((destination/ref['key']).stat().st_ino,(mirror.root/'state'/ref['key']).stat().st_ino)
        head=mirror.root/'state/heads/latest-run.json';before=head.read_bytes()
        state.compare_and_swap('latest-run',{'receipt':ref},{'receipt':ref,'next':1})
        self.assertEqual(head.read_bytes(),before)
        pushed=mirror.push(state,expected_commit=receipt['commit'])
        self.assertEqual(json.loads(head.read_text())['next'],1)
        self.assertEqual(state.get(ref),b'evidence body')
        GitArchive.verify(mirror.root,pushed['manifestSha256'])

    def test_archive_compare_and_swap_rejects_a_stale_cloud_session_before_overwriting_budget(self):
        remote=Path(self.temp.name)/'remote.git'
        subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True)
        live=LocalStore(Path(self.temp.name)/'live')
        live.compare_and_swap('budget-day',None,{'calls':1})
        archive=GitArchive(Path(self.temp.name)/'mirror',str(remote));first=archive.push(live)
        other=GitArchive(Path(self.temp.name)/'other-mirror',str(remote))
        destination=Path(self.temp.name)/'other-state';other.restore(destination)
        stale=LocalStore(destination)
        live.compare_and_swap('budget-day',{'calls':1},{'calls':2})
        second=archive.push(live,expected_commit=first['commit'])
        with self.assertRaisesRegex(ConflictError,'CHANGED_SINCE_RESTORE'):
            other.push(stale,expected_commit=first['commit'])
        restored=Path(self.temp.name)/'final-state'
        other.restore(restored,expected_commit=second['commit'])
        self.assertEqual(LocalStore(restored).read('heads/budget-day.json'),{'calls':2})

    def test_policy_change_cannot_reset_subscription_daily_budget(self):
        self.c['model']['maxDocumentsPerRun']=1
        agent=FakeAgent();self.assertTrue(self.run_pipeline(agent=agent)['complete'])
        self.c['version']='expanded-source-policy'
        result=self.run_pipeline(agent=agent)
        self.assertFalse(result['complete'])
        self.assertEqual(result['receipts'][0]['errorCode'],'DOCUMENTS_BUDGET_EXHAUSTED')
        self.assertEqual(agent.calls,2)

    def test_shared_publisher_entity_exclusions_are_rechecked_without_model_calls(self):
        self.c['sources'][0]['family']='investor_acquirer'
        self.c['suppliers'][0]['requiredFamilies']=['investor_acquirer']
        pages=FakeFetcher(self.store).pages
        pages[URL]=b'<html><body>Different Corporation announced a funding round. This lengthy announcement discusses only that unrelated corporation and its investors and contains no statement about the tracked entity.</body></html>'
        agent=FakeAgent();result=self.run_pipeline(pages=pages,agent=agent)
        self.assertTrue(result['complete']);self.assertEqual(agent.calls,0)
        ref=result['receipts'][0]['documentValidations'][0]['validation']
        validation=json.loads(self.store.get(ref));validation['supplierId']='different'
        result['receipts'][0]['documentValidations'][0]['validation']=self.store.put(validation)
        with self.assertRaises(ContractError):reconcile(plan_run(self.c,T),result['receipts'],self.c,T,self.store)

    def static_artifact(self):
        dist=Path(self.temp.name)/'dist';dist.mkdir()
        (dist/'index.html').write_text('<html>Exact tested build</html>')
        (dist/'app-release.json').write_text(json.dumps({'appRevision':'a'*40,'dailySnapshotSha256':'b'*64,'dailyContractSha256':'d'*64}))
        return build_artifact(self.store,dist,{'headers':[]})

    def test_detached_receipt_avoids_circular_hash_and_binds_tested_static_bytes(self):
        artifact=self.static_artifact()
        files=stage_files(self.store,artifact,{'artifactSha256':artifact['sha256']})
        self.assertIn('static/deployment-receipt.json',files)
        self.assertEqual(digest(artifact_inventory(files)),artifact['sha256'])
        files['static/index.html']=b'untested change'
        bad={**artifact,'archive':self.store.put(pack(files))}
        with self.assertRaises(ContractError):stage_files(self.store,bad,{'artifactSha256':bad['sha256']})

    def test_prebuilt_archive_rejects_traversal_and_executable_functions(self):
        artifact=self.static_artifact();files=unpack(self.store.get(artifact['archive']))
        for path in ['../escape','functions/injected.func/index.js']:
            with self.assertRaises(ContractError):unpack(pack({**files,path:b'malicious'}))

    def test_official_vercel_adapter_uploads_only_prebuilt_output(self):
        artifact=self.static_artifact();seen=[]
        def runner(args,**kwargs):
            seen.append(args)
            root=Path(kwargs['cwd'])
            self.assertEqual({p.name for p in root.iterdir()},{'.vercel', 'web'})
            self.assertEqual(list((root/'web').iterdir()), [])
            self.assertTrue((root/'.vercel/output/static/index.html').exists())
            self.assertIn('--prebuilt',args);self.assertNotIn('--prod',args)
            return SimpleNamespace(returncode=0,stdout='https://exact-tested-build.vercel.app\n',stderr='')
        adapter=VercelAdapter(self.store,'prj_123','team_123','pikeholdings',runner=runner)
        manifest={'releaseId':'e'*64,'appRevision':'a'*40,'snapshot':{'sha256':'b'*64},'artifact':artifact,'contractSha256':'d'*64}
        self.assertEqual(adapter.stage(manifest),'https://exact-tested-build.vercel.app')
        self.assertEqual(len(seen),1)

    def test_crash_after_promotion_recovers_acknowledgement_without_redeploying(self):
        previous={'releaseId':'old','sequence':1,'deploymentId':'old-deploy'}
        self.store.compare_and_swap('production',None,previous)
        manifest={'createdAt':T,'parentReleaseId':'old','sequence':2,'appRevision':'a'*40,'snapshot':{'sha256':'b'*64},'artifact':{'sha256':'c'*64},'contractSha256':'d'*64}
        manifest['releaseId']=digest(manifest)
        self.store.write_once('release-attempts/'+manifest['releaseId']+'.json',manifest)
        self.store.write_once('deployment-attempts/'+manifest['releaseId']+'.json',{'deploymentId':'new-deploy'})
        live={'ready':True,'dataReleaseId':manifest['releaseId'],'appRevision':'a'*40,'snapshotSha256':'b'*64,'artifactSha256':'c'*64,'contractSha256':'d'*64}
        adapter=SimpleNamespace(probe_production=lambda:live)
        head=recover_publication(self.store,adapter)
        self.assertEqual(head['releaseId'],manifest['releaseId']);self.assertEqual(head['sequence'],2)

    def test_stored_review_is_rechecked_during_reconciliation(self):
        result=self.run_pipeline();ref=result['receipts'][0]['validatedFacts'][0]
        fact=json.loads(self.store.get(ref));(self.store.root/fact['review']['key']).write_bytes(b'corrupt')
        with self.assertRaises(ContractError):reconcile(plan_run(self.c,T),result['receipts'],self.c,T,self.store)

    def test_matrix_cannot_borrow_success_from_changed_contract(self):
        result=self.run_pipeline();self.c['version']='new-policy'
        rows=inventory(self.c,T,result)
        self.assertTrue(all(r['outcome']=='not_checked' for r in rows))

    def test_fresh_cli_verifier_reconstructs_a_run_from_durable_receipts(self):
        self.run_pipeline()
        path=self.store.root/'test-contract.json';path.write_bytes(canonical(self.c))
        result=subprocess.run([sys.executable,str(SCRIPTS/'cli.py'),'verify','--contract',str(path),'--state',self.temp.name,'--at',T],capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['complete'])
        self.assertEqual(len(list((self.store.root/'verifications').rglob('*.json'))),1)

    def test_cli_status_is_nonzero_for_missing_or_degraded_coverage(self):
        path=self.store.root/'test-contract.json';path.write_bytes(canonical(self.c))
        args=[sys.executable,str(SCRIPTS/'cli.py'),'status','--contract',str(path),'--state',self.temp.name,'--at',T]
        result=subprocess.run(args,capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,2);self.assertFalse(json.loads(result.stdout)['healthy'])
        self.run_pipeline(agent=FakeAgent(empty=True))
        result=subprocess.run(args,capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,2);self.assertFalse(json.loads(result.stdout)['healthy'])

    def test_empty_extraction_cannot_hide_clear_business_signal(self):
        result=self.run_pipeline(agent=FakeAgent(empty=True))
        self.assertFalse(result["complete"])
        self.assertIn("EMPTY_EXTRACTION",result["receipts"][0]["errorCode"])

    def test_explicit_quiet_document_has_no_change_receipt(self):
        pages=FakeFetcher(self.store).pages;pages[URL]=b'<html><body>Fixture Vendor publishes this contact directory for customers and its support team. No business announcement is included.</body></html>'
        result=self.run_pipeline(agent=FakeAgent(empty=True),pages=pages)
        self.assertTrue(result["complete"]);self.assertEqual(result["receipts"][0]["outcome"],"checked_no_change")

    def test_unverified_endpoint_never_earns_coverage(self):
        self.c["sources"][0]["registration"]="candidate"
        result=self.run_pipeline();self.assertFalse(result["complete"]);self.assertEqual(result["successfulTasks"],0)

    def test_blocked_endpoint_has_durable_failure_receipt(self):
        pages={self.c["sources"][0]["url"]:403}
        result=self.run_pipeline(pages=pages)
        self.assertFalse(result["complete"]);self.assertEqual(result["receipts"][0]["outcome"],"blocked")
        self.assertTrue(list((self.store.root/'runs'/result['runId']/'attempts').glob('*.json')))

    def test_missing_receipt_is_rejected(self):
        result=self.run_pipeline();p=plan_run(self.c,T)
        with self.assertRaises(ContractError):reconcile(p,[],self.c,T,self.store)

    def test_duplicate_receipt_is_rejected(self):
        result=self.run_pipeline();p=plan_run(self.c,T);r=result['receipts'][0]
        with self.assertRaises(ContractError):reconcile(p,[r,r],self.c,T,self.store)

    def test_contract_denominator_cannot_change_after_plan(self):
        p=plan_run(self.c,T);result=self.run_pipeline();self.c['version']='changed'
        with self.assertRaises(ContractError):reconcile(p,result['receipts'],self.c,T,self.store)

    def test_fresh_receipt_cannot_reuse_stale_source_check(self):
        result=self.run_pipeline();r=result['receipts'][0];r['completedAt']='2026-10-21T16:00:00Z'
        with self.assertRaises(ContractError):reconcile(plan_run(self.c,T),[r],self.c,'2026-10-21T16:00:00Z',self.store)

    def test_no_change_with_new_facts_is_rejected(self):
        result=self.run_pipeline();r=result['receipts'][0];r['outcome']='checked_no_change'
        with self.assertRaises(ContractError):reconcile(plan_run(self.c,T),[r],self.c,T,self.store)

    def test_pagination_budget_is_not_completeness(self):
        source=self.c['sources'][0];source['maxPages']=1
        first=b'<feed><link rel="next" href="https://example.invalid/feed2.xml"/><entry><link href="https://example.invalid/releases/one"/></entry></feed>'
        pages={source['url']:first}
        result=self.run_pipeline(pages=pages)
        self.assertFalse(result['complete']);self.assertEqual(result['receipts'][0]['errorCode'],'PAGINATION_BUDGET_EXHAUSTED')

    def test_xml_external_entities_are_rejected(self):
        with self.assertRaises(ContractError):xml_links(b'<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><rss/>',URL)

    def test_rss_channel_pagination_is_retained(self):
        parsed=xml_links(b'<rss><channel><link rel="next" href="/page2.xml"/></channel></rss>',URL)
        self.assertEqual(parsed['indexes'],['https://example.invalid/page2.xml'])

    def test_private_and_unapproved_targets_are_rejected(self):
        def private(*a,**k):return [(socket.AF_INET,socket.SOCK_STREAM,6,'',('127.0.0.1',443))]
        with self.assertRaises(ContractError):safe_url(URL,['example.invalid'],private)
        with self.assertRaises(ContractError):safe_url('https://evil.invalid/x',['example.invalid'],private)

    def test_managed_proxy_owns_dns_but_cannot_bypass_host_or_literal_ip_guards(self):
        def unavailable(*a,**k):raise socket.gaierror('Cloud DNS is delegated to proxy')
        self.assertEqual(safe_url(URL,['example.invalid'],unavailable,proxy_dns=True),URL)
        with self.assertRaises(ContractError):safe_url(URL,['example.invalid'],unavailable)
        with self.assertRaises(ContractError):safe_url('https://127.0.0.1/x',['127.0.0.1'],unavailable,proxy_dns=True)
        with self.assertRaises(ContractError):safe_url('https://evil.invalid/x',['example.invalid'],unavailable,proxy_dns=True)

    def test_snapshot_connects_verified_statements_to_actual_site_events_and_evidence(self):
        coverage=self.run_pipeline()
        snapshot=build_snapshot(self.c,plan_run(self.c,T),coverage,self.store,T)
        self.assertEqual(len(snapshot['events']),1);self.assertEqual(len(snapshot['evidence']),1)
        event=snapshot['events'][0];self.assertEqual(event['supplierId'],'fixture')
        self.assertEqual(event['text'],QUOTE);self.assertEqual(event['type'],'funding')
        self.assertEqual(snapshot['evidence'][0]['retrieval']['sha256'],digest(f'<html><body>{QUOTE}</body></html>'.encode()))
        self.assertEqual(snapshot['supplierUpdates'],{}) # An undisclosed stage cannot be invented.

    def test_independent_press_alone_is_held_from_the_site(self):
        self.c['sources'][0]['family']='independent_reporting'
        self.c['suppliers'][0]['requiredFamilies']=['independent_reporting']
        coverage=self.run_pipeline();snapshot=build_snapshot(self.c,plan_run(self.c,T),coverage,self.store,T)
        self.assertEqual(snapshot['events'],[]);self.assertEqual(snapshot['reviewQueue'][0]['reason'],'PRIMARY_SOURCE_REQUIRED')

    def test_snapshot_cannot_renew_stale_coverage_or_accept_failed_task_facts(self):
        coverage=self.run_pipeline()
        with self.assertRaises(ContractError):build_snapshot(self.c,plan_run(self.c,T),coverage,self.store,'2026-10-21T16:00:00Z')
        coverage['receipts'][0]['outcome']='failed'
        coverage['receipts'][0]['documentValidations']=[]
        snapshot=build_snapshot(self.c,plan_run(self.c,T),coverage,self.store,T)
        self.assertEqual(snapshot['events'],[]);self.assertFalse(snapshot['coverage']['complete'])

    def test_completed_document_can_publish_with_degraded_coverage_for_another_document(self):
        pages=FakeFetcher(self.store).pages
        pages['https://example.invalid/feed.xml']=b'<rss><channel><item><link>https://example.invalid/releases/one</link></item><item><link>https://example.invalid/releases/two</link></item></channel></rss>'
        pages['https://example.invalid/releases/two']=403
        coverage=self.run_pipeline(pages=pages)
        snapshot=build_snapshot(self.c,plan_run(self.c,T),coverage,self.store,T)
        self.assertEqual(len(snapshot['events']),1)
        self.assertFalse(snapshot['coverage']['complete'])
        self.assertEqual(snapshot['coverage']['successfulTasks'],0)
        self.assertIsNone(self.store.read('heads/source-'+digest('official')+'.json'))

    def test_fresh_governance_run_does_not_extend_actual_source_freshness(self):
        coverage=self.run_pipeline()
        snapshot=build_snapshot(self.c,plan_run(self.c,T),coverage,self.store,'2026-10-20T15:00:00Z')
        self.assertEqual(snapshot['coverage']['validUntil'],'2026-10-20T22:00:00+00:00')
        self.assertEqual(snapshot['coverage']['lastCollectionAt'],T)

    def test_snapshot_retains_historical_events_without_relabelling_them_new(self):
        coverage=self.run_pipeline();first=build_snapshot(self.c,plan_run(self.c,T),coverage,self.store,T)
        second=build_snapshot(self.c,plan_run(self.c,T),coverage,self.store,T,previous=first)
        self.assertEqual(second['events'],first['events']);self.assertEqual(second['parentSnapshotSha256'],digest(first))

    def test_currency_and_qualifier_survive_display_formatting(self):
        c=candidate();c.update(amount='10250000',currency='CAD',qualifier='up_to')
        self.assertEqual(money(c),'up to C$10,250,000')

    def filing_fixture(self):
        source=self.c['sources'][0]
        source.update(kind='sec_documents',family='filing_documents',cik='0000000001',url='https://data.sec.gov/submissions/CIK0000000001.json',allowedHosts=['data.sec.gov','www.sec.gov'])
        self.c['suppliers'][0]['requiredFamilies']=['filing_documents']
        document='https://www.sec.gov/Archives/edgar/data/1/000000000126000001/report.htm'
        index={'cik':1,'filings':{'recent':{'accessionNumber':['0000000001-26-000001'],'form':['8-K'],'filingDate':['2026-10-19'],'primaryDocument':['report.htm']},'files':[]}}
        pages={source['url']:json.dumps(index).encode(),document:('<html><body>'+QUOTE*5+'</body></html>').encode()}
        return source,document,index,pages

    def test_sec_document_delta_archives_readable_text_then_reuses_immutable_bytes(self):
        source,document,index,pages=self.filing_fixture()
        first=self.run_pipeline(pages=pages);self.assertTrue(first['complete'])
        self.assertEqual(len(first['receipts'][0]['documents']),1)
        del pages[document] # Second run cannot fetch it; it must use hash-checked retained bytes.
        second=self.run_pipeline(pages=pages);self.assertTrue(second['complete'])
        obs=[self.store.read(f'observations/{oid}.json') for oid in second['receipts'][0]['observationIds']]
        self.assertTrue(any(o['status']=='retained_immutable' for o in obs))

    def test_scarce_fetch_budget_checks_sec_primary_document_before_citations(self):
        source, document, index, pages = self.filing_fixture()
        citation = {**source, 'id': 'citation', 'kind': 'citation', 'family': 'citation_integrity',
                    'url': 'https://example.invalid/citation', 'allowedHosts': ['example.invalid']}
        self.c['sources'].append(citation)
        self.c['suppliers'][0]['sourceIds'].append('citation')
        self.c['suppliers'][0]['requiredFamilies'].append('citation_integrity')
        self.c['schedule'].update(maxWorkers=1, maxFetchesPerRun=2)
        pages[citation['url']] = b'Citation body'
        checked = self.run_pipeline(pages=pages)
        receipts = {r['sourceId']: r for r in checked['receipts']}
        self.assertEqual(receipts[source['id']]['outcome'], 'checked_no_change')
        self.assertEqual(len(receipts[source['id']]['documents']), 1)
        self.assertEqual(receipts['citation']['errorCode'], 'FETCHES_BUDGET_EXHAUSTED')
        self.assertEqual(self.store.read('heads/budget-' + T[:10] + '.json')['fetches'], 2)

    def test_sec_document_disappearance_inside_retention_is_held(self):
        source,document,index,pages=self.filing_fixture();self.assertTrue(self.run_pipeline(pages=pages)['complete'])
        index['filings']['recent']={k:[] for k in index['filings']['recent']};pages[source['url']]=json.dumps(index).encode()
        result=self.run_pipeline(pages=pages)
        self.assertFalse(result['complete']);self.assertEqual(result['receipts'][0]['errorCode'],'SEC_INDEX_REMOVED_WITHIN_RETENTION')

    def test_missing_or_stale_health_is_not_green(self):
        self.assertFalse(health(None,T)['healthy'])
        result=self.run_pipeline();self.assertFalse(health(result,'2026-10-21T16:00:00Z')['healthy'])

    def test_health_cannot_borrow_another_policys_success_or_ignore_gaps(self):
        result=self.run_pipeline()
        self.assertFalse(health(result,T,expected_contract='0'*64)['healthy'])
        result['gapTaskIds']=['unperformed'];self.assertFalse(health(result,T)['healthy'])

    def test_wrong_deployed_data_receipt_fails(self):
        manifest={'appRevision':'a'*40,'releaseId':'r1','snapshot':{'sha256':'b'*64},'artifact':{'sha256':'c'*64},'contractSha256':'d'*64}
        with self.assertRaises(ContractError):verify_acknowledgement(manifest,{'ready':True,'appRevision':'a'*40,'dataReleaseId':'wrong'})

    def test_automatic_cutover_is_disabled_by_default(self):
        with self.assertRaises(ContractError):publish(self.store,self.c,{},None)

    def test_live_failure_rolls_back_and_retains_last_good_head(self):
        self.c['publication']['enabled']=True
        previous={'releaseId':'old','sequence':1,'deploymentId':'old-deploy'}
        self.store.compare_and_swap('production',None,previous)
        manifest={'createdAt':T,'releaseId':'new','parentReleaseId':'old','sequence':2,'appRevision':'a'*40,'snapshot':{'sha256':'b'*64},'artifact':{'sha256':'c'*64},'contractSha256':'d'*64}
        class Adapter:
            rolled_back=False
            def production_paths_controlled(self):return True
            def stage(self,m):return 'new-deploy'
            def probe(self,d):return {'ready':True,'appRevision':'a'*40,'dataReleaseId':'new','snapshotSha256':'b'*64,'artifactSha256':'c'*64,'contractSha256':'d'*64}
            def promote(self,d):pass
            def probe_production(self):return {'ready':True,'dataReleaseId':'old' if self.rolled_back else 'wrong'}
            def rollback(self,d):self.rolled_back=True
        adapter=Adapter()
        with self.assertRaises(ContractError):publish(self.store,self.c,manifest,adapter)
        self.assertTrue(adapter.rolled_back);self.assertEqual(self.store.read('heads/production.json'),previous)
        self.assertIsNotNone(self.store.read('rollback-events/new.json'))

    def test_promote_timeout_also_rolls_back(self):
        self.c['publication']['enabled']=True
        self.store.compare_and_swap('production',None,{'releaseId':'old','sequence':1,'deploymentId':'old-deploy'})
        manifest={'createdAt':T,'releaseId':'new','parentReleaseId':'old','sequence':2,'appRevision':'a'*40,'snapshot':{'sha256':'b'*64},'artifact':{'sha256':'c'*64},'contractSha256':'d'*64}
        class Adapter:
            rolled_back=False
            def production_paths_controlled(self):return True
            def stage(self,m):return 'new-deploy'
            def probe(self,d):return {'ready':True,'appRevision':'a'*40,'dataReleaseId':'new','snapshotSha256':'b'*64,'artifactSha256':'c'*64,'contractSha256':'d'*64}
            def promote(self,d):raise TimeoutError('lost response after alias changed')
            def rollback(self,d):self.rolled_back=True
            def probe_production(self):return {'ready':True,'dataReleaseId':'old'}
        adapter=Adapter()
        with self.assertRaises(TimeoutError):publish(self.store,self.c,manifest,adapter)
        self.assertTrue(adapter.rolled_back)

    def test_subscription_runner_strips_infrastructure_and_api_credentials(self):
        calls=[]
        def runner(args,**kwargs):
            calls.append(args)
            self.assertNotIn('OPENAI_API_KEY',kwargs['env']);self.assertNotIn('VERCEL_TOKEN',kwargs['env']);self.assertNotIn('GITHUB_TOKEN',kwargs['env'])
            if args[1]=='login':return SimpleNamespace(returncode=0,stdout='Logged in using ChatGPT',stderr='')
            self.assertIn('--ignore-user-config',args);self.assertIn('--ignore-rules',args)
            self.assertEqual(args[args.index('--sandbox')+1],'read-only')
            for feature in ['shell_tool','apps','multi_agent','hooks','browser_use']:self.assertIn(feature,args)
            Path(args[args.index('--output-last-message')+1]).write_text('{"facts":[]}')
            return SimpleNamespace(returncode=0,stdout='',stderr='')
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fixture-api','VERCEL_TOKEN':'fixture-vercel','GITHUB_TOKEN':'fixture-git'}):
            agent=SubscriptionAgent(self.c['model'],runner=runner)
            self.assertEqual(agent.extract('Quiet fixture',self.c['suppliers'][0]),[])
        self.assertEqual(len(calls),2)

    def test_api_authenticated_cli_is_not_used_as_subscription(self):
        def runner(*args,**kwargs):return SimpleNamespace(returncode=0,stdout='Logged in using an API key',stderr='')
        with self.assertRaises(ModelUnavailable):SubscriptionAgent(self.c['model'],runner=runner).call('probe',{})

    def test_github_provenance_requires_actual_run_and_exact_artifact(self):
        receipt={'githubRunId':12,'appRevision':'a'*40,'artifactSha256':'b'*64,'result':'pass','executedTests':7}
        archive=io.BytesIO()
        with zipfile.ZipFile(archive,'w') as z:z.writestr('gate-receipt.json',canonical(receipt))
        payload=archive.getvalue()
        run={'status':'completed','conclusion':'success','path':'.github/workflows/market-release-gate.yml','head_branch':'main','head_sha':'a'*40}
        meta={'workflow_run':{'id':12},'expired':False,'name':'daily-market-gate','digest':'sha256:'+hashlib.sha256(payload).hexdigest()}
        def runner(args,**kwargs):
            value=payload if args[-1].endswith('/zip') else canonical(run if 'actions/runs/' in args[-1] else meta)
            return SimpleNamespace(returncode=0,stdout=value,stderr=b'')
        authority=GitHubAuthority(runner=runner);supplied={**receipt,'githubArtifactId':34};artifact={'sha256':'b'*64}
        self.assertTrue(authority.verify_test_receipt(supplied,artifact))
        with self.assertRaises(ContractError):authority.verify_test_receipt({**supplied,'executedTests':9},artifact)
        run['head_branch']='unreviewed'
        with self.assertRaises(ContractError):authority.verify_test_receipt(supplied,artifact)

    def test_release_requires_current_coverage_and_exact_sec_claim_inventory(self):
        coverage=self.run_pipeline()
        self.c['certifiedCohorts']=[{'id':'sec','supplierIds':['fixture'],'claimGroups':['revenue'],'allRequired':True}]
        coverage['contractSha256']=digest(self.c)
        snapshot={'contractSha256':digest(self.c),'sha256':'b'*64,'allChangedClaimsVerified':True,'secCertification':{'required':1,'verified':1,'drift':0,'runId':coverage['runId'],'claimKeys':['fixture.revenue']}}
        artifact={'sha256':'c'*64};receipt={'result':'pass','executedTests':1,'artifactSha256':'c'*64,'appRevision':'a'*40,'snapshotSha256':'b'*64,'runId':coverage['runId'],'contractSha256':digest(self.c),'coverageSha256':digest(coverage)}
        authority=SimpleNamespace(verify_test_receipt=lambda *a:True)
        def prepare():return prepare_release(self.c,coverage,snapshot,'a'*40,artifact,receipt,None,T,authority)
        self.assertEqual(prepare()['sequence'],1)
        snapshot['secCertification']['claimKeys']=['wrong']
        with self.assertRaises(ContractError):prepare()
        snapshot['secCertification']['claimKeys']=['fixture.revenue'];coverage['checkedAt']='2026-10-16T16:00:00Z'
        with self.assertRaises(ContractError):prepare()

    def test_real_roster_has_all_87_and_honest_gaps(self):
        # 74 live suppliers plus the 8 onboarding under D-138 and the 5 added for application and AI security.
        c=validate_contract(json.loads((SCRIPTS.parents[2]/'contracts/market.json').read_text()))
        p=plan_run(c,T)
        self.assertEqual(len(p['supplierIds']),87)
        self.assertTrue(any(t['kind']=='missing_discovery' for t in p['tasks']))

    def test_distribution_and_investor_sites_are_not_company_discovery(self):
        c=json.loads((SCRIPTS.parents[2]/'contracts/market.json').read_text())
        for s in c['sources']:
            if s['kind']=='citation':continue
            host=urlsplit(s['url']).hostname
            if host in {'www.prnewswire.com','www.globenewswire.com'}:self.assertEqual(s['family'],'release_distribution')
            if host in {'www.thomabravo.com','newsroom.accenture.com','www.levelblue.com'}:self.assertEqual(s['family'],'investor_acquirer')


class HistoryWindowSelectionTests(unittest.TestCase):
    """Policy-versioned backlog cut: the window only exists when the contract declares it."""
    policy = {"currentWindowDays": 30, "historyWindowDays": 365, "maxDocumentsPerSource": 2,
              "maxAuditDocumentsPerSource": 1, "maxFetchAuditDocumentsPerSource": 3}

    def test_old_unreviewed_documents_are_archived_but_stay_in_the_queue(self):
        found = {"items": ["old", "recent"], "itemModified": {"old": "2020-01-01", "recent": "2026-10-19"}}
        selected, deferred = select_documents(found, {}, self.policy, T)
        self.assertEqual((selected, deferred), (["recent"], ["old"]))

    def test_policies_without_a_window_keep_the_old_behaviour(self):
        legacy = {"currentWindowDays": 30, "maxDocumentsPerSource": 2, "maxAuditDocumentsPerSource": 1}
        found = {"items": ["old", "recent"], "itemModified": {"old": "2020-01-01", "recent": "2026-10-19"}}
        self.assertEqual(select_documents(found, {}, legacy, T), (["recent", "old"], []))

    def test_undated_documents_remain_eligible_and_sort_after_dated_ones(self):
        found = {"items": ["a-undated", "b-dated"], "itemModified": {"b-dated": "2026-06-01"}}
        selected, deferred = select_documents(found, {}, {**self.policy, "maxFetchAuditDocumentsPerSource": 0}, T)
        self.assertEqual((selected, deferred), (["b-dated"], ["a-undated"]))

    def test_supplier_mention_check_name_alias_and_absence(self):
        from selection import mentions_supplier
        supplier = {"name": "Fixture Vendor, Inc.", "kind": "private", "aliases": ["FV Labs"]}
        self.assertTrue(mentions_supplier("fixture vendor raised money", supplier))
        self.assertTrue(mentions_supplier("Notes from FV Labs", supplier))
        self.assertFalse(mentions_supplier("Fixture Vendors Anonymous met; another company raised money", supplier))


if __name__=='__main__':unittest.main()


class SplitReleaseTests(unittest.TestCase):
    """The publisher dispatches the gate and ends; a later call completes it (no billed waiting)."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(self.temp.name)
        self.c = contract()
        self.c["publication"].update(enabled=True, maxBatchesPerDay=2)
        self.store.write_once("releases/old.json", {"manifest": {}})
        self.store.compare_and_swap("latest-run", None, {"receipt": {"sha256": "a" * 64}})
        self.archive = {"commit": "c" * 40, "manifestSha256": "d" * 64}
        self.checkpoints = 0
        self.gate = {"status": "completed", "conclusion": "success"}
        patches = {
            "VercelAdapter": patch("release.VercelAdapter"),
            "recover": patch("release.recover_publication", return_value={"releaseId": "old"}),
            "preflight": patch("release.preflight_corrections"),
            "authority": patch("release.GitHubAuthority"),
            "dispatch": patch("release.dispatch_gate", return_value=(77, None)),
            "artifact": patch("release.gate_artifact", return_value=88),
            "import": patch("release.import_gate", return_value=({"coverage": {}, "snapshot": {}, "artifact": {}}, {})),
            "prepare": patch("release.prepare_release", return_value={"manifest": True}),
            "publish": patch("release.publish", return_value={"releaseId": "new"}),
        }
        self.m = {k: p.start() for k, p in patches.items()}
        for p in patches.values():
            self.addCleanup(p.stop)
        self.m["VercelAdapter"].return_value.production_paths_controlled.return_value = True
        self.m["authority"].return_value._api.side_effect = lambda path: self.gate

    def checkpoint(self):
        self.checkpoints += 1

    def run_release(self, **kw):
        return release_daily(self.store, self.c, self.archive, "b" * 40, {"vercel": {"project_id": "fixture"}}, self.checkpoint, split=True, **kw)

    def budget(self):
        day = datetime.now(timezone.utc).date().isoformat()
        return (self.store.read(f"heads/gate-budget-{day}.json") or {}).get("attempts", 0)

    def pending(self):
        return self.store.read("heads/pending-gate.json")

    def test_request_reserves_one_attempt_records_pending_and_does_not_wait(self):
        result = self.run_release()
        self.assertEqual(result, {"published": False, "reason": "GATE_REQUESTED", "githubRunId": 77})
        self.assertEqual(self.m["dispatch"].call_args.kwargs, {"wait": False})
        self.assertEqual(self.budget(), 1)
        self.assertEqual(self.pending()["gateRunId"], 77)
        self.assertEqual(self.pending()["collectionReceiptSha256"], "a" * 64)
        self.assertEqual(self.pending()["archive"], self.archive)
        self.assertNotIn("closedAt", self.pending())
        self.assertEqual(self.checkpoints, 2)  # reservation before dispatch, pending after
        self.m["publish"].assert_not_called()

    def test_gate_budget_is_per_revision_with_a_daily_total(self):
        from release import gate_budget_check
        self.run_release()
        day = datetime.now(timezone.utc).date().isoformat()
        self.assertEqual(self.store.read(f"heads/gate-budget-{day}.json"), {"attempts": 1, "byRevision": {"b" * 40: 1}})
        # Two attempts on the same code use its allowance.
        with self.assertRaisesRegex(Exception, "DAILY_GATE_BUDGET_EXHAUSTED"):
            gate_budget_check({"attempts": 2, "byRevision": {"b" * 40: 2}}, "b" * 40, 2)
        # New code on main gets its own attempts the same day.
        self.assertEqual(gate_budget_check({"attempts": 2, "byRevision": {"b" * 40: 2}}, "f" * 40, 2)[0], 2)
        # The daily total still holds: 4 attempts across any revisions.
        with self.assertRaisesRegex(Exception, "DAILY_GATE_BUDGET_EXHAUSTED"):
            gate_budget_check({"attempts": 4, "byRevision": {"x": 2, "y": 2}}, "z" * 40, 2)
        # A record written before this rule counts toward the total only.
        self.assertEqual(gate_budget_check({"attempts": 2}, "b" * 40, 2)[0], 2)
        with self.assertRaisesRegex(Exception, "DAILY_GATE_BUDGET_EXHAUSTED"):
            gate_budget_check({"attempts": 4}, "b" * 40, 2)

    def test_running_gate_is_left_alone_without_new_attempts(self):
        self.run_release()
        self.gate = {"status": "in_progress"}
        self.assertEqual(self.run_release()["reason"], "GATE_PENDING")
        self.assertEqual(self.budget(), 1)
        self.assertEqual(self.m["dispatch"].call_count, 1)

    def test_finished_gate_publishes_once_and_closes_pending(self):
        self.run_release()
        result = self.run_release(complete_only=True)
        self.assertTrue(result["published"])
        self.assertEqual(result["githubRunId"], 77)
        self.m["import"].assert_called_once()
        self.assertEqual(self.m["import"].call_args.args[2:], (77, 88, self.archive))
        self.m["publish"].assert_called_once()
        self.assertEqual(self.pending()["outcome"], "published")
        self.assertEqual(self.budget(), 1)
        # A gate callback after completion finds nothing to do and never requests a gate.
        self.assertEqual(self.run_release(complete_only=True)["reason"], "NO_PENDING_GATE")
        self.assertEqual(self.m["dispatch"].call_count, 1)

    def test_gate_callback_without_pending_never_requests_or_spends(self):
        self.assertEqual(self.run_release(complete_only=True)["reason"], "NO_PENDING_GATE")
        self.m["dispatch"].assert_not_called()
        self.assertEqual(self.budget(), 0)

    def test_new_collection_or_code_supersedes_the_gate_result(self):
        self.run_release()
        self.store.compare_and_swap("latest-run", self.store.read("heads/latest-run.json"), {"receipt": {"sha256": "e" * 64}})
        self.assertEqual(self.run_release()["reason"], "GATE_SUPERSEDED")
        self.assertEqual(self.pending()["outcome"], "superseded")
        self.m["publish"].assert_not_called()
        self.run_release()  # the next run may request a fresh gate for the new collection
        self.assertEqual(self.budget(), 2)

    def test_failed_gate_refuses_records_and_retains_production(self):
        self.run_release()
        self.m["artifact"].side_effect = ValueError("Independent release gate failed; retain production")
        with self.assertRaisesRegex(ValueError, "retain production"):
            self.run_release()
        self.assertEqual(self.pending()["outcome"], "gate_failed")
        self.m["publish"].assert_not_called()

    def test_waiting_mode_is_unchanged(self):
        self.m["dispatch"].return_value = (77, 88)
        result = release_daily(self.store, self.c, self.archive, "b" * 40, {"vercel": {"project_id": "fixture"}}, self.checkpoint)
        self.assertTrue(result["published"])
        self.assertEqual(self.m["dispatch"].call_args.kwargs, {})
        self.assertIsNone(self.pending())
