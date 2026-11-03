"""Offline scheduled-cycle regression tests. Synthetic transport earns no collection credit."""
import contextlib
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "web/scripts/pipeline"))
import collect
from contracts import canonical, digest
from engine import Pipeline
from fetcher import Fetcher
from storage import LocalStore
from test_correction_collection import fixture_contract, MechanicsAgent, TEXT

EARLY = "2026-10-25T00:05:00Z"
LATER = "2026-10-25T09:34:00Z"
NORMAL_EVENT = {"GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": "jessepike/sec-market",
                "GITHUB_EVENT_NAME": "schedule", "GITHUB_REF": "refs/heads/main", "SMP_EVENT_SCHEDULE": "17 5 * * *"}


class ScheduledSelectionTests(unittest.TestCase):
    def test_only_normal_main_github_timer_selects_forced_refresh(self):
        with patch.dict(os.environ, NORMAL_EVENT, clear=True):
            self.assertTrue(collect.scheduled_source_refresh())
        excluded = {"GITHUB_ACTIONS": ("false", "", None), "GITHUB_REPOSITORY": ("other/sec-market", None),
                    "GITHUB_EVENT_NAME": ("workflow_dispatch", "push", "pull_request", "workflow_run", None),
                    "GITHUB_REF": ("refs/heads/preview", "refs/heads/codex/test", "refs/tags/main", None),
                    "SMP_EVENT_SCHEDULE": ("7 6 23 10 *", "7 7 23 10 *", "17 6 * * *", "17 5 * * * ", "", None)}
        for key, values in excluded.items():
            for value in values:
                event = {**NORMAL_EVENT, key: value}
                if value is None: del event[key]
                with self.subTest(key=key, value=value), patch.dict(os.environ, event, clear=True):
                    self.assertFalse(collect.scheduled_source_refresh())

    def test_outside_timer_dispatch_and_backup_cron_also_select_forced_refresh(self):
        timer_event = {**NORMAL_EVENT, "GITHUB_EVENT_NAME": "workflow_dispatch", "SMP_TIMER": "true"}
        del timer_event["SMP_EVENT_SCHEDULE"]
        for event in (timer_event, {**NORMAL_EVENT, "SMP_EVENT_SCHEDULE": "47 9 * * *"}):
            with self.subTest(event=event), patch.dict(os.environ, event, clear=True):
                self.assertTrue(collect.scheduled_source_refresh())
        for event in ({**timer_event, "SMP_TIMER": "false"}, {**timer_event, "GITHUB_REF": "refs/heads/preview"},
                      {**timer_event, "GITHUB_EVENT_NAME": "push"}):
            with self.subTest(event=event), patch.dict(os.environ, event, clear=True):
                self.assertFalse(collect.scheduled_source_refresh())

    def test_execute_passes_selection_to_pipeline_and_keeps_correction_replay(self):
        class BoundaryReached(RuntimeError):
            pass
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            (repo / "contracts").mkdir(parents=True)
            (repo / "contracts/market.json").write_bytes(canonical(fixture_contract()))
            (repo / "contracts/factual-corrections.json").write_text("{}")
            for event, expected in (({}, True), ({"GITHUB_EVENT_NAME": "workflow_dispatch"}, False),
                                    ({"GITHUB_REF": "refs/heads/preview"}, False),
                                    ({"SMP_EVENT_SCHEDULE": "7 6 23 10 *"}, False)):
                environment = {**NORMAL_EVENT, **event, "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "1",
                               "SMP_CODEX_AUTH_JSON": "fictional", "SMP_AUTH_STORE_TOKEN": "fictional"}
                with self.subTest(event=event), contextlib.ExitStack() as stack:
                    stack.enter_context(patch.dict(os.environ, environment, clear=True))
                    stack.enter_context(patch.object(collect, "REPO", repo))
                    stack.enter_context(patch.object(collect, "recover"))
                    stack.enter_context(patch.object(collect.session_runtime, "git", return_value="a" * 40))
                    stack.enter_context(patch.object(collect.session_runtime, "bootstrap"))
                    stack.enter_context(patch.object(collect.session_runtime, "checkpoint"))
                    stack.enter_context(patch.object(collect, "LocalStore", return_value=Mock(read=Mock(return_value={"sessionId": "synthetic"}))))
                    keeper = Mock(home=Path(directory) / "nonexistent-auth")
                    stack.enter_context(patch.object(collect, "AuthStore", return_value=keeper))
                    stack.enter_context(patch.object(collect, "GuardedRunner"))
                    agent = stack.enter_context(patch.object(collect, "SubscriptionAgent"))
                    fetcher = stack.enter_context(patch.object(collect, "Fetcher"))
                    stack.enter_context(patch.object(collect, "validate_contract", side_effect=lambda value: value))
                    stack.enter_context(patch("html_qualification_seed.seed_before_collection"))
                    stack.enter_context(patch.object(collect, "reuse_scheduled_collection", return_value=None))
                    stack.enter_context(patch.object(collect, "correction_work", return_value=object()))
                    stack.enter_context(patch.object(collect, "escrow_budgets"))
                    stack.enter_context(patch.object(collect, "utcnow", return_value=LATER))
                    stack.enter_context(patch.object(collect.signal, "signal"))
                    pipeline = stack.enter_context(patch.object(collect, "BoundedPipeline"))
                    pipeline.return_value.run.side_effect = BoundaryReached("stop before collection")
                    with self.assertRaises(BoundaryReached):
                        collect.execute(Path(directory) / "runtime", maximum_seconds=60)
                    pipeline.return_value.run.assert_called_once_with(LATER, replay=True, force_refresh=expected)
                    agent.return_value.extract.assert_not_called()
                    fetcher.return_value.fetch.assert_not_called()
                    keeper.restore.assert_called_once_with("fictional")  # Mock only; no account work.

    def test_source_probe_returns_before_any_collection_selection_or_account_work(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
            root = Path(directory)
            (root / "contracts").mkdir()
            (root / "contracts/market.json").write_bytes(canonical(fixture_contract()))
            environment = {**NORMAL_EVENT, "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_RUN_ID": "123"}
            stack.enter_context(patch.dict(os.environ, environment, clear=True))
            stack.enter_context(patch.object(collect, "REPO", root))
            stack.enter_context(patch.object(collect, "recover"))
            stack.enter_context(patch.object(collect, "LocalStore", return_value=Mock(read=Mock(return_value={}))))
            stack.enter_context(patch.object(collect, "validate_contract", side_effect=lambda value: value))
            stack.enter_context(patch.object(collect.session_runtime, "require_source_probe_context"))
            stack.enter_context(patch.object(collect.session_runtime, "git", return_value="a" * 40))
            stack.enter_context(patch.object(collect.session_runtime, "bootstrap"))
            probe = stack.enter_context(patch.object(collect, "execute_source_probe", return_value={"diagnostic": True}))
            forbidden = [stack.enter_context(patch.object(collect, name, side_effect=AssertionError(name)))
                         for name in ("AuthStore", "BoundedPipeline", "scheduled_source_refresh")]
            self.assertEqual(collect.execute(root / "runtime", maximum_seconds=60, source_probe=True), {"diagnostic": True})
            probe.assert_called_once()
            for mock in forbidden: mock.assert_not_called()


class CycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(Path(self.temp.name) / "synthetic-state")
        self.contract = fixture_contract()
        self.contract["sources"] = [next(s for s in self.contract["sources"] if s["kind"] == "citation")]
        self.reset_supplier()
        self.clock = EARLY
        self.requests = []
        self.pages = {}
        owner = self
        class OfflineTransport:
            def fetch(self, source, url, previous=None):
                owner.requests.append((copy.deepcopy(source), url, copy.deepcopy(previous)))
                body = owner.pages.get(url, ("<html><body>" + TEXT + "</body></html>").encode())
                return {"requestedUrl": url, "finalUrl": url, "fetchedAt": owner.clock, "status": "fetched", "httpStatus": 200,
                        "body": owner.store.put(body), "etag": '"synthetic-v1"', "lastModified": "Sat, 24 Oct 2026 00:00:00 GMT",
                        "contentType": "application/json" if url.endswith(".json") else "text/html"}
        self.fetcher = OfflineTransport()

    def reset_supplier(self):
        self.contract["suppliers"][0]["sourceIds"] = [s["id"] for s in self.contract["sources"]]
        self.contract["suppliers"][0]["requiredFamilies"] = list({s["family"] for s in self.contract["sources"]})

    def worker(self, fetcher=None, **kwargs):
        return Pipeline(self.contract, self.store, fetcher or self.fetcher, clock=lambda: self.clock, **kwargs)

    def run_cycle(self, force=False, fetcher=None, **kwargs):
        return self.worker(fetcher, **kwargs).run(self.clock, replay=True, force_refresh=force)

    def observation(self, result, index=0):
        return self.store.read("observations/" + result["receipts"][index]["observationIds"][0] + ".json")

    def test_ordinary_same_day_retry_preserves_receipt_observation_clock_and_budget(self):
        early = self.run_cycle()
        counts = self.store.read("heads/budget-2026-10-25.json")
        self.clock = LATER
        with patch.object(self.fetcher, "fetch", side_effect=AssertionError("ordinary retry must not fetch")):
            retry = self.run_cycle()
        self.assertTrue(retry["complete"])
        self.assertEqual(early["receipts"], retry["receipts"])
        self.assertEqual(self.observation(retry)["fetchedAt"], EARLY)
        self.assertEqual(self.store.read("heads/budget-2026-10-25.json"), counts)

    def test_forced_replay_bypasses_both_caches_without_replacing_immutable_pointer(self):
        early = self.run_cycle()
        first = self.observation(early)
        pointers = {p: p.read_bytes() for p in (self.store.root / "runs" / early["runId"] / "downloads").glob("*.json")}
        self.clock = LATER
        worker = self.worker()
        with patch.object(worker, "_reusable_receipt", side_effect=AssertionError("forced cycle must bypass receipts")):
            later = worker.run(LATER, replay=True, force_refresh=True)
        self.assertTrue(later["complete"], later["receipts"])
        self.assertEqual(later["runId"], early["runId"])
        self.assertEqual(len(self.requests), 2)
        self.assertEqual(self.requests[-1][2]["observationId"], first["observationId"])
        new = self.observation(later)
        self.assertEqual(new["fetchedAt"], LATER)
        self.assertNotEqual(new["observationId"], first["observationId"])
        self.assertEqual(new["body"], first["body"])
        self.assertEqual({p: p.read_bytes() for p in pointers}, pointers)
        self.assertEqual(self.store.read("heads/budget-2026-10-25.json")["fetches"], 2)
        with patch.object(self.fetcher, "fetch", side_effect=AssertionError("retry should use latest successful receipt")):
            retry = self.run_cycle()
        self.assertEqual(retry["receipts"], later["receipts"])

    def test_ordinary_saved_download_replay_still_keeps_original_clock(self):
        early = self.run_cycle()
        self.clock = LATER
        worker = self.worker()
        with patch.object(worker, "_reusable_receipt", return_value=None), \
             patch.object(self.fetcher, "fetch", side_effect=AssertionError("saved replay should not fetch")):
            replay = worker.run(LATER, replay=True)
        self.assertTrue(replay["complete"])
        self.assertEqual(self.observation(replay), self.observation(early))
        self.assertEqual(len(self.requests), 1)

    def test_forced_conditional_http_304_uses_actual_new_clock_and_original_body_chain(self):
        early = self.run_cycle()
        original = self.observation(early)
        self.clock = LATER
        requests = []
        class ConditionalOpener:
            def open(self, request, **kwargs):
                requests.append(request)
                raise HTTPError(request.full_url, 304, "Not Modified", {}, None)
        with patch("fetcher.safe_url", side_effect=lambda url, *_a, **_k: url), \
             patch("fetcher.urllib.request.build_opener", return_value=ConditionalOpener()), \
             patch("fetcher.utcnow", return_value=LATER):
            later = self.run_cycle(True, fetcher=Fetcher(self.store))
        self.assertTrue(later["complete"], later["receipts"])
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].get_header("If-none-match"), original["etag"])
        self.assertEqual(requests[0].get_header("If-modified-since"), original["lastModified"])
        observed = self.observation(later)
        self.assertEqual((observed["status"], observed["httpStatus"]), ("not_modified", 304))
        self.assertEqual(observed["fetchedAt"], LATER)
        self.assertEqual(observed["body"], original["body"])
        self.assertEqual(observed["reusesObservationId"], original["observationId"])
        self.assertFalse(observed["transportReused"])
        self.assertEqual(self.store.read("observations/" + original["observationId"] + ".json"), original)

    def test_forced_cycle_shares_only_current_invocation_full_responses(self):
        source = self.contract["sources"][0]
        self.contract["sources"].append({**source, "id": "second-citation"})
        self.reset_supplier()
        early = self.run_cycle()
        self.assertTrue(early["complete"])
        self.assertEqual(len(self.requests), 1)
        self.clock = LATER
        later = self.run_cycle(True)
        self.assertTrue(later["complete"])
        self.assertEqual(len(self.requests), 2)
        observations = [self.observation(later, index) for index in (0, 1)]
        self.assertEqual({o["fetchedAt"] for o in observations}, {LATER})
        self.assertEqual(len({o["transportId"] for o in observations}), 1)
        self.assertEqual(sum(o["transportReused"] for o in observations), 1)
        self.assertEqual(self.store.read("heads/budget-2026-10-25.json")["fetches"], 2)

    def test_depleted_allowance_never_reuses_old_transport_or_refunds_capacity(self):
        self.contract["schedule"]["maxFetchesPerRun"] = 1
        early = self.run_cycle()
        original = self.observation(early)
        counts = self.store.read("heads/budget-2026-10-25.json")
        self.clock = LATER
        later = self.run_cycle(True)
        self.assertFalse(later["complete"])
        self.assertEqual(later["receipts"][0]["errorCode"], "FETCHES_BUDGET_EXHAUSTED")
        self.assertEqual(later["receipts"][0]["observationIds"], [])
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(self.store.read("heads/budget-2026-10-25.json"), counts)
        self.assertEqual(self.store.read("observations/" + original["observationId"] + ".json"), original)

    def test_cancellation_and_execution_deadline_stop_forced_transport_before_reservation(self):
        self.run_cycle()
        counts = self.store.read("heads/budget-2026-10-25.json")
        self.clock = LATER
        worker = collect.BoundedPipeline(self.contract, self.store, self.fetcher, clock=lambda: self.clock, maximum_seconds=60)
        worker.stop()
        cancelled = worker.run(LATER, replay=True, force_refresh=True)
        self.assertFalse(cancelled["complete"])
        self.assertEqual(cancelled["receipts"][0]["errorCode"], "CI_COLLECTION_TIME_BUDGET_EXHAUSTED")
        worker = self.worker()
        self.contract["schedule"]["maxRuntimeSeconds"] = 1
        calls = []
        def elapsed():
            calls.append(True)
            return 0 if len(calls) == 1 else 2
        with patch("engine.time.monotonic", side_effect=elapsed):
            expired = worker.run(LATER, replay=True, force_refresh=True)
        self.assertEqual(expired["receipts"][0]["errorCode"], "RUN_TIME_BUDGET_EXHAUSTED")
        self.assertEqual(self.store.read("heads/budget-2026-10-25.json"), counts)
        self.assertEqual(len(self.requests), 1)

    def test_forced_immutable_sec_document_reuse_requires_genuine_current_index_anchor(self):
        source = self.contract["sources"][0]
        source.update(kind="sec_documents", family="filing_documents", cik="0000000001",
                      url="https://data.sec.gov/submissions/CIK0000000001.json", allowedHosts=["data.sec.gov", "www.sec.gov"])
        self.reset_supplier()
        document = "https://www.sec.gov/Archives/edgar/data/1/000000000126000001/report.htm"
        index = {"cik": 1, "filings": {"recent": {"accessionNumber": ["0000000001-26-000001"], "form": ["8-K"],
                 "filingDate": ["2026-10-24"], "primaryDocument": ["report.htm"]}, "files": []}}
        self.pages[source["url"]] = canonical(index)
        early = self.run_cycle()
        self.assertTrue(early["complete"], early["receipts"])
        self.assertEqual(len(self.requests), 2)
        old = [self.store.read("observations/" + oid + ".json") for oid in early["receipts"][0]["observationIds"]]
        original_document = next(o for o in old if o["requestedUrl"] == document)
        self.clock = LATER
        later = self.run_cycle(True)
        self.assertTrue(later["complete"], later["receipts"])
        self.assertEqual(len(self.requests), 3)
        self.assertEqual(self.requests[-1][1], source["url"])
        new = [self.store.read("observations/" + oid + ".json") for oid in later["receipts"][0]["observationIds"]]
        anchor = next(o for o in new if o["requestedUrl"] == source["url"])
        retained = next(o for o in new if o["requestedUrl"] == document)
        self.assertEqual(anchor["fetchedAt"], LATER)
        self.assertEqual(retained["status"], "retained_immutable")
        self.assertEqual(retained["fetchedAt"], EARLY)
        self.assertEqual(retained["verifiedAt"], LATER)
        self.assertEqual(retained["anchorObservationIds"], [anchor["observationId"]])
        self.assertEqual(retained["reusesObservationId"], original_document["observationId"])
        self.assertEqual(retained["body"], original_document["body"])

    def test_unchanged_primary_body_reuses_semantic_review_without_new_model_calls(self):
        self.contract = fixture_contract()
        self.contract["sources"] = [next(s for s in self.contract["sources"] if s["kind"] == "rss")]
        self.reset_supplier()
        source = self.contract["sources"][0]
        self.pages[source["url"]] = b'<rss><channel><item><link>https://example.invalid/release/one</link></item></channel></rss>'
        agent = MechanicsAgent(self.contract["model"], [])
        early = self.run_cycle(agent=agent)
        self.assertTrue(early["complete"], early["receipts"])
        calls = agent.calls
        model_counts = {key: self.store.read("heads/budget-2026-10-25.json")[key] for key in ("calls", "documents")}
        validations = {p: p.read_bytes() for p in (self.store.root / "document-validation").glob("*.json")}
        self.clock = LATER
        later = self.run_cycle(True, agent=agent)
        self.assertTrue(later["complete"], later["receipts"])
        self.assertEqual(agent.calls, calls)
        self.assertEqual({key: self.store.read("heads/budget-2026-10-25.json")[key] for key in model_counts}, model_counts)
        self.assertEqual({p: p.read_bytes() for p in validations}, validations)
        self.assertEqual(later["receipts"][0]["validatedFacts"], early["receipts"][0]["validatedFacts"])
        agent.runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
