"""The real timer and archived execution must agree before monitoring is green."""
import copy
import importlib.util
import unittest
import io
import json
import tempfile
from contextlib import redirect_stdout
from unittest.mock import patch
from pathlib import Path

spec = importlib.util.spec_from_file_location("watchdog", Path(__file__).with_name("probe.py"))
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ScheduledCollectionTests(unittest.TestCase):
    def setUp(self):
        self.contract = {"schedule": {"overdueHours": 30}, "publication": {"enabled": False}}
        self.coverage = {"runId": "daily", "checkedAt": "2026-10-23T04:00:00Z",
                         "contractSha256": probe.digest(self.contract), "complete": True,
                         "successfulTasks": 2, "requiredTasks": 2, "gapTaskIds": []}
        self.entries = {"heads/cloud-collector.json": {"phase": "finish", "appRevision": "a"*40,
                         "result": {"githubRunId": "123", "githubEventName": "workflow_dispatch"}},
                        "heads/latest-run.json": {"receipt": {"key": "coverage"}}, "coverage": self.coverage}
        self.run = {"path": ".github/workflows/subscription-collector.yml", "head_sha": "a"*40,
                    "event": "workflow_dispatch", "status": "completed", "conclusion": "success"}
        self.scheduled = {"id": 122, "run_attempt": 1, "head_sha": "a"*40,
                          "path": ".github/workflows/subscription-collector.yml",
                          "display_title": "bounded subscription collector",
                          "event": "schedule", "head_branch": "main", "status": "completed",
                          "conclusion": "success", "created_at": "2026-10-23T03:30:00Z",
                          "html_url": "https://github.com/jessepike/sec-market/actions/runs/122"}
        self.runs = [self.scheduled]
        self.entries["ci/collection-runs/122-1.json"] = {
            "executionCompleted": True, "githubRunId": "122", "githubEventName": "schedule",
            "githubRef": "refs/heads/main", "appRevision": "a"*40,
            "contractSha256": probe.digest(self.contract)}

    def inspect(self):
        owner = self
        class Authority:
            def _api(self, path):
                if "workflows/" in path:
                    return {"workflow_runs": owner.runs}
                if path.endswith("/jobs?per_page=20"):
                    return owner.jobs.get(path.split("/")[2], {"jobs": []})
                return owner.run
        return probe.inspect_collection(self.contract, lambda key, **kw: self.entries[key],
                                        "2026-10-23T04:10:00Z", Authority())

    jobs = {}

    def test_outside_timer_dispatch_counts_and_plain_dispatch_does_not(self):
        timer_run = dict(self.scheduled, event="workflow_dispatch", display_title="daily timer collection")
        self.runs = [timer_run]
        self.entries["ci/collection-runs/122-1.json"].update(githubEventName="workflow_dispatch", githubTimer=True)
        self.assertTrue(self.inspect()["healthy"])
        self.entries["ci/collection-runs/122-1.json"].pop("githubTimer")
        self.assertIn("SCHEDULED_COLLECTION_RECEIPT_DIFFERS", self.inspect()["reasons"])
        self.runs = [dict(timer_run, display_title="bounded subscription collector")]
        self.assertIn("NO_ACTUAL_SCHEDULED_COLLECTION", self.inspect()["reasons"])

    def test_backup_timer_that_skipped_is_passed_over_for_the_real_collection(self):
        backup = dict(self.scheduled, id=130, created_at="2026-10-23T04:05:00Z")
        self.jobs = {"130": {"jobs": [{"name": "schedule-guard", "conclusion": "success"},
                                      {"name": "collect-and-reconcile", "conclusion": "skipped"}]}}
        self.runs = [backup, self.scheduled]
        result = self.inspect()
        self.assertTrue(result["healthy"])
        self.assertEqual(result["scheduledRunUrl"], self.scheduled["html_url"])

    def test_dispatch_success_cannot_substitute_for_a_timer(self):
        self.runs = []
        self.assertIn("NO_ACTUAL_SCHEDULED_COLLECTION", self.inspect()["reasons"])

    def test_successful_schedule_and_verified_complete_archive_pass_even_before_publish_activation(self):
        result = self.inspect()
        self.assertTrue(result["healthy"])
        self.assertFalse(result["publicationEnabled"])
        self.assertEqual(result["scheduledRunUrl"], self.scheduled["html_url"])

    def test_other_branch_and_dispatch_runs_cannot_prove_default_branch_clock(self):
        self.runs = [dict(self.scheduled, head_branch="preview"), dict(self.scheduled, event="workflow_dispatch")]
        self.assertIn("NO_ACTUAL_SCHEDULED_COLLECTION", self.inspect()["reasons"])

    def test_successful_runner_with_incomplete_source_coverage_stays_unhealthy(self):
        self.coverage.update(complete=False, successfulTasks=1, gapTaskIds=["gap"])
        result = self.inspect()
        self.assertFalse(result["healthy"])
        self.assertIn("OVERDUE_OR_INCOMPLETE_COVERAGE", result["reasons"])

    def test_green_timer_without_its_own_archived_collection_is_detected(self):
        del self.entries["ci/collection-runs/122-1.json"]
        self.assertIn("SCHEDULED_COLLECTION_RECEIPT_MISSING", self.inspect()["reasons"])

    def test_failed_or_expired_timer_and_forged_archive_trigger_are_detected(self):
        self.scheduled.update(conclusion="failure", created_at="2026-10-20T03:30:00Z")
        self.entries["heads/cloud-collector.json"]["result"]["githubEventName"] = "schedule"
        result = self.inspect()
        for reason in ("SCHEDULED_COLLECTION_FAILED_OR_UNFINISHED", "SCHEDULED_COLLECTION_OVERDUE", "COLLECTOR_GITHUB_IDENTITY_DIFFERS"):
            self.assertIn(reason, result["reasons"])


class InitialPublicationTests(unittest.TestCase):
    def inspect_baseline(self, changed=False):
        contract = {"schedule": {"overdueHours": 30}, "suppliers": [{"id": "fixture"}]}
        coverage = {"runId": "daily", "checkedAt": "2026-10-23T04:00:00Z",
                    "contractSha256": probe.digest(contract), "complete": False,
                    "supplierCount": 1, "successfulTasks": 0, "requiredTasks": 1, "gapTaskIds": ["gap"]}
        app = {"appRevision": "a" * 40, "certifiedAt": "2026-10-21T04:00:00Z"}
        entries = {"heads/latest-run.json": {"receipt": {"key": "coverage"}}, "coverage": coverage,
                   "heads/worker-heartbeat.json": {"finishedAt": "2026-10-23T04:00:00Z", "phases": {"finish": 0}, "executionMode": "github_subscription"},
                   "heads/production.json": {"legacyBaseline": True, "releaseId": "legacy", "legacyAppReceipt": app}}
        reads, requests = [], []
        def read(key, **kwargs):
            reads.append(key)
            return entries[key]
        def live(url):
            requests.append(url)
            return {**app, "appRevision": "b" * 40} if changed else app
        with patch.object(probe, "plan_run", return_value={"tasks": [{"required": True}]}):
            result = probe.inspect(contract, read, live, "2026-10-23T04:10:00Z")
        self.assertFalse(any(key.startswith("releases/") for key in reads))
        self.assertEqual(requests, ["https://securitymarketpulse.com/app-release.json"])
        return result

    def test_retained_legacy_baseline_reports_pending_cutover_and_coverage_gaps(self):
        result = self.inspect_baseline()
        self.assertFalse(result["healthy"])
        self.assertIn("INITIAL_PRODUCTION_CUTOVER_PENDING", result["reasons"])
        self.assertIn("OVERDUE_OR_INCOMPLETE_COVERAGE", result["reasons"])
        self.assertNotIn("LEGACY_PRODUCTION_BASELINE_DIFFERS", result["reasons"])

    def test_changed_legacy_baseline_stays_held(self):
        self.assertIn("LEGACY_PRODUCTION_BASELINE_DIFFERS", self.inspect_baseline(changed=True)["reasons"])

    def test_publication_probe_failure_preserves_collection_diagnosis(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "contracts").mkdir()
            (root / "contracts/market.json").write_text(json.dumps({"publication": {"enabled": True}}))
            output = io.StringIO()
            with patch.object(probe, "ROOT", root), patch("sys.argv", ["probe.py"]), patch.object(probe, "api", return_value={"object": {"sha": "a" * 40}}), patch.object(probe, "inspect_collection", return_value={"healthy": False, "reasons": ["NO_ACTUAL_SCHEDULED_COLLECTION"]}), patch.object(probe, "inspect", side_effect=KeyError("missing")), redirect_stdout(output):
                self.assertEqual(probe.main(), 2)
            reasons = json.loads(output.getvalue())["reasons"]
            self.assertIn("NO_ACTUAL_SCHEDULED_COLLECTION", reasons)
            self.assertIn("INDEPENDENT_PROBE_FAILED", reasons)


class HeldClaimAlertTests(unittest.TestCase):
    """Held facts require evidence work; their count does not assign a human decision."""
    def inspect(self, held, complete=True):
        contract = {"schedule": {"overdueHours": 30}, "suppliers": [{"id": "fixture"}]}
        coverage = {"runId": "daily", "checkedAt": "2026-10-23T04:00:00Z",
                    "contractSha256": probe.digest(contract), "complete": complete,
                    "supplierCount": 1, "successfulTasks": 2 if complete else 1,
                    "requiredTasks": 2, "gapTaskIds": [] if complete else ["gap"],
                    "validUntil": "2026-10-24T10:00:00Z"}
        app = {"appRevision": "a" * 40, "dailySnapshotSha256": "b" * 64}
        entries = {"heads/latest-run.json": {"receipt": {"key": "coverage"}}, "coverage": coverage,
                   "heads/worker-heartbeat.json": {"finishedAt": "2026-10-23T04:00:00Z",
                       "phases": {"finish": 0}, "executionMode": "github_subscription"},
                   "heads/production.json": {"releaseId": "fixture"},
                   "releases/fixture.json": {"manifest": {"appRevision": app["appRevision"],
                       "snapshot": {"sha256": app["dailySnapshotSha256"]}}},
                   "heads/dailySnapshot.json": {"reviewQueue": [{"reason": "source date unresolved"}] * held}}
        public = {"https://securitymarketpulse.com/deployment-receipt.json": {"fictional": True},
                  "https://securitymarketpulse.com/app-release.json": app,
                  "https://securitymarketpulse.com/daily-coverage.json": coverage}
        with patch.object(probe, "plan_run", return_value={"tasks": [{"required": True}] * 2}), \
             patch.object(probe, "verify_acknowledgement"):
            return probe.inspect(contract, lambda key, **kw: entries[key], lambda url: public[url],
                                 "2026-10-23T04:10:00Z")

    def test_held_claims_stay_unhealthy_without_implying_an_owner_decision(self):
        result = self.inspect(28)
        self.assertFalse(result["healthy"])
        self.assertEqual(result["reasons"], ["HELD_CLAIMS_28"])

    def test_empty_queue_does_not_raise_a_held_claim_alert(self):
        result = self.inspect(0)
        self.assertTrue(result["healthy"])
        self.assertEqual(result["reasons"], [])

    def test_source_gaps_and_held_claims_keep_separate_reasons(self):
        result = self.inspect(28, complete=False)
        self.assertFalse(result["healthy"])
        self.assertEqual(set(result["reasons"]), {
            "OVERDUE_OR_INCOMPLETE_COVERAGE", "PUBLIC_COVERAGE_INCOMPLETE_OR_OVERDUE", "HELD_CLAIMS_28"})


class CorrectionCollectionTests(unittest.TestCase):
    def setUp(self):
        self.context = {"policySha256": "p", "requests": {"groups": [{"id": "one"}, {"id": "two"}]}}
        self.outcome = {"runId": "daily", "policySha256": "p", "pending": [], "admitted": [{"groupId": "one"}, {"groupId": "two"}]}
        self.entries = {"heads/correction-collection.json": {"runId": "daily", "outcome": {"key": "correction"}}, "correction": self.outcome}

    def inspect(self):
        return probe.inspect_corrections(self.context, lambda key, **kw: self.entries[key], "daily")

    def test_complete_correction_inventory_has_its_own_green_check(self):
        self.assertEqual(self.inspect(), [])

    def test_pending_and_input_error_cannot_be_hidden_by_source_success(self):
        self.outcome["pending"] = [{"groupId": "two", "reason": "held"}]
        self.assertEqual(self.inspect(), ["FACTUAL_CORRECTIONS_PENDING_1"])
        self.outcome.update(pending=[], error="invalid input")
        self.assertEqual(self.inspect(), ["FACTUAL_CORRECTION_INPUT_ERROR"])

    def test_stale_policy_missing_or_duplicate_admissions_are_detected(self):
        self.outcome["admitted"] = [{"groupId": "one"}, {"groupId": "one"}]
        self.assertEqual(self.inspect(), ["FACTUAL_CORRECTION_ADMISSIONS_INCOMPLETE"])
        self.outcome["policySha256"] = "old"
        self.assertEqual(self.inspect(), ["CORRECTION_COLLECTION_POLICY_OR_RUN_DIFFERS"])
        del self.entries["heads/correction-collection.json"]
        self.assertEqual(self.inspect(), ["FACTUAL_CORRECTION_COLLECTION_MISSING_OR_INVALID"])


class SeparateCoverageTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((Path(__file__).resolve().parents[2] / 'contracts/market.json').read_text())
        self.plan = probe.plan_run(self.contract, '2026-10-23T04:00:00Z')
        sources = {source['id']: source for source in self.contract['sources']}
        self.checked = next(task for task in self.plan['tasks']
                            if task['required'] and sources.get(task['sourceId'], {}).get('registration') == 'verified')
        self.coverage = self.make_coverage()

    @staticmethod
    def progress(kind, pending=0):
        inventory = pending
        value = dict(complete=pending == 0, inventoryDocuments=inventory,
                     reviewedDocuments=0, pendingDocuments=pending, heldDocuments=0)
        if kind == 'processing':
            value.update(changedDocuments=0, unknownDateDocuments=0)
        return value

    def make_coverage(self):
        required = [task for task in self.plan['tasks'] if task['required']]
        rows, receipts = [], []
        for task in self.plan['tasks']:
            checked = task['taskId'] == self.checked['taskId']
            intake = 'checked' if checked else 'not_checked'
            receipt = dict(taskId=task['taskId'], sourceId=task['sourceId'], supplierId=task['supplierId'],
                           outcome='checked_no_change' if checked else 'not_checked',
                           discoveryComplete=checked, observationIds=['observation'] if checked else [])
            receipts.append(receipt)
            rows.append(dict(taskId=task['taskId'], sourceId=task['sourceId'], supplierId=task['supplierId'],
                             intakeOutcome=intake, outcome=intake, processingOutcome=receipt['outcome'],
                             processing=self.progress('processing'),
                             historicalReview=self.progress('historicalReview', 1 if checked else 0)))
        good = {self.checked['taskId']}
        gaps = sorted({task['taskId'] for task in required} - good)
        coverage = dict(schemaVersion=2, measure='daily_source_intake_v2', checkedAt='2026-10-23T04:00:00Z',
                        contractSha256=probe.digest(self.contract), inventorySha256=self.plan['inventorySha256'],
                        runId=self.plan['runId'], successfulTasks=1, requiredTasks=len(required),
                        complete=False, gapTaskIds=gaps,
                        intake=dict(measure='daily_source_intake_v2', evaluated=True, status='collected', successfulTasks=1,
                                    requiredTasks=len(required), complete=False, gapTaskIds=gaps),
                        tasks=rows, receipts=receipts)
        for kind in ('processing', 'historicalReview'):
            fields = ['inventoryDocuments', 'reviewedDocuments', 'pendingDocuments', 'heldDocuments']
            if kind == 'processing':
                fields += ['changedDocuments', 'unknownDateDocuments']
            coverage[kind] = {field:sum(row[kind][field] for row in rows) for field in fields}
            coverage[kind]['complete'] = all(row[kind]['complete'] for row in rows)
        return coverage

    def test_public_unbound_source_encoding_matches_planned_none(self):
        public = copy.deepcopy(self.coverage)
        public['sources'] = public['tasks']
        for row in public['tasks']:
            if row['sourceId'] is None:
                row['sourceId'] = ''
        reasons, _ = probe.separate_health(self.contract, public, public=True, plan=self.plan)
        self.assertNotIn('SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED', reasons)

    def test_raw_discovery_cannot_disagree_with_checked_intake(self):
        receipt = next(item for item in self.coverage['receipts'] if item['taskId'] == self.checked['taskId'])
        receipt['discoveryComplete'] = False
        reasons, _ = probe.separate_health(self.contract, self.coverage, plan=self.plan)
        self.assertIn('SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED', reasons)

    def test_failed_intake_can_retain_partial_or_ineligible_observations(self):
        task = next(row for row in self.coverage['tasks'] if row['intakeOutcome'] != 'checked')
        receipt = next(item for item in self.coverage['receipts'] if item['taskId'] == task['taskId'])
        receipt['observationIds'] = ['partial-page']
        reasons, _ = probe.separate_health(self.contract, self.coverage, plan=self.plan)
        self.assertNotIn('SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED', reasons)
        receipt['discoveryComplete'] = True  # complete but possibly stale or otherwise ineligible
        reasons, _ = probe.separate_health(self.contract, self.coverage, plan=self.plan)
        self.assertNotIn('SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED', reasons)

    def test_historical_backlog_is_reported_separately_from_fresh_intake(self):
        reasons, details = probe.separate_health(self.contract, self.coverage, plan=self.plan)
        self.assertIn('HISTORICAL_REVIEW_PENDING_1', reasons)
        self.assertIn('DAILY_INTAKE_INCOMPLETE', reasons)
        self.assertNotIn('PROCESSING_PENDING_1', reasons)
        self.assertEqual(details['historicalReview']['pendingDocuments'], 1)

    def test_transition_does_not_relabel_legacy_or_invalid_observations(self):
        root = Path(__file__).resolve().parents[2]
        legacy = json.loads((root / 'docs/active/daily-pipeline/evaluations/2026-10-24/operational-inputs/coverage.json').read_text())
        self.assertEqual((legacy['successfulTasks'], legacy['requiredTasks']), (244, 557))
        uncollected = copy.deepcopy(self.coverage)
        uncollected['intake'].update(evaluated=False, status='uncollected')
        invalid = copy.deepcopy(self.coverage)
        invalid['historicalReview']['pendingDocuments'] += 1
        for observed in (legacy, uncollected, invalid):
            with self.subTest(schema=observed.get('schemaVersion')):
                before = copy.deepcopy(observed)
                reasons, details = probe.separate_health(self.contract, observed, plan=self.plan)
                self.assertIn('SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED', reasons)
                self.assertNotIn('coverageMeasure', details)
                self.assertEqual(details['expectedCoverageMeasure'], 'daily_source_intake_v2')
                self.assertEqual(observed, before)
        reasons, details = probe.separate_health(self.contract, self.coverage, plan=self.plan)
        self.assertNotIn('SEPARATE_COVERAGE_INVALID_OR_UNCOLLECTED', reasons)
        self.assertEqual(details['coverageMeasure'], 'daily_source_intake_v2')


if __name__ == "__main__":
    unittest.main()


class RegressionTriageTests(unittest.TestCase):
    """D-143: known structural gaps are tracked; only a change raises the alert."""
    NOW = "2026-11-04T20:00:00Z"

    def setUp(self):
        self.contract = {"schedule": {"overdueHours": 30}}
        self.known = {"sourceGaps": {"acme:official:1": "HTTP_403"}}
        self.coverage = {"runId": "today", "checkedAt": "2026-11-04T05:35:00Z",
                         "gapTaskIds": ["t1", "t2"],
                         "tasks": [{"taskId": "t1", "sourceId": "acme:official:1"},
                                   {"taskId": "t2", "sourceId": None},
                                   {"taskId": "t3", "sourceId": "acme:citation:1"}],
                         "processing": {"pendingDocuments": 100, "reviewedDocuments": 50}}
        self.previous = {"runId": "yesterday", "processing": {"pendingDocuments": 110, "reviewedDocuments": 40},
                         "gapTaskIds": ["y1", "y3"], "tasks": [{"taskId": "y1", "sourceId": "acme:official:1"},
                                                              {"taskId": "y3", "sourceId": "acme:citation:1"}]}
        self.reasons = ["OVERDUE_OR_INCOMPLETE_COVERAGE", "DAILY_INTAKE_INCOMPLETE", "PROCESSING_PENDING_100",
                        "PROCESSING_HELD_3", "HISTORICAL_REVIEW_PENDING_9", "PUBLIC_DAILY_INTAKE_INCOMPLETE",
                        "PUBLIC_PROCESSING_PENDING_100", "PUBLIC_COVERAGE_INCOMPLETE_OR_OVERDUE", "HELD_CLAIMS_5"]

    def triage(self, reasons=None, previous="default"):
        previous = self.previous if previous == "default" else previous
        return probe.triage({"reasons": list(self.reasons if reasons is None else reasons)},
                            self.contract, self.coverage, previous, self.known, self.NOW)

    def test_known_gaps_with_moving_review_are_tracked_not_alerted(self):
        result = self.triage()
        self.assertTrue(result["healthy"])
        self.assertEqual(result["reasons"], [])
        self.assertEqual(result["tracked"], self.reasons)
        self.assertEqual(result["reviewedSincePreviousRun"], 10)

    def test_a_source_outside_the_baseline_failing_alerts(self):
        self.coverage["gapTaskIds"].append("t3")
        result = self.triage()
        self.assertEqual(result["reasons"], ["NEW_SOURCE_GAPS_1"])
        self.assertEqual(result["newSourceGaps"], ["acme:citation:1"])

    def test_a_one_day_blip_is_reported_but_does_not_alert(self):
        self.coverage["gapTaskIds"].append("t3")
        self.previous["gapTaskIds"] = ["y1"]
        result = self.triage()
        self.assertTrue(result["healthy"])
        self.assertEqual(result["newSourceGapsFirstDay"], ["acme:citation:1"])

    def test_known_gap_that_recovers_is_reported_for_baseline_pruning(self):
        self.coverage["gapTaskIds"] = ["t2"]
        result = self.triage()
        self.assertTrue(result["healthy"])
        self.assertEqual(result["knownGapsNowCollecting"], ["acme:official:1"])

    def test_review_that_stops_moving_alerts(self):
        self.previous["processing"].update(pendingDocuments=100, reviewedDocuments=50)
        self.assertEqual(self.triage()["reasons"], ["REVIEW_STALLED"])

    def test_unreadable_review_trend_is_not_counted_as_progress(self):
        self.assertEqual(self.triage(previous=None)["reasons"], ["REVIEW_TREND_UNREADABLE"])
        self.coverage["processing"]["pendingDocuments"] = 0
        self.assertTrue(self.triage(previous=None)["healthy"])

    def test_overdue_collection_alerts_even_though_incompleteness_is_tracked(self):
        self.coverage["checkedAt"] = "2026-11-03T05:35:00Z"
        self.assertIn("COVERAGE_OVERDUE", self.triage()["reasons"])

    def test_pipeline_failures_still_alert(self):
        result = self.triage(self.reasons + ["COLLECTION_HAS_NOT_REACHED_PRODUCTION", "SCHEDULED_COLLECTION_OVERDUE"])
        self.assertEqual(result["reasons"], ["COLLECTION_HAS_NOT_REACHED_PRODUCTION", "SCHEDULED_COLLECTION_OVERDUE"])

    def test_malformed_input_alerts(self):
        self.known = {"sourceGaps": ["not", "a", "map"]}
        self.assertIn("TRIAGE_INPUT_INVALID", self.triage()["reasons"])

    def test_baseline_names_only_real_contract_sources(self):
        known = json.loads(probe.KNOWN_GAPS_PATH.read_text())
        contract = json.loads((probe.ROOT / "contracts/market.json").read_text())
        ids = {source["id"] for source in contract["sources"]}
        self.assertTrue(known["sourceGaps"])
        self.assertLessEqual(set(known["sourceGaps"]), ids)
