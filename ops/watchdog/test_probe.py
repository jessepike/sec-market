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
                return {"workflow_runs": owner.runs} if "workflows/" in path else owner.run
        return probe.inspect_collection(self.contract, lambda key, **kw: self.entries[key],
                                        "2026-10-23T04:10:00Z", Authority())

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


if __name__ == "__main__":
    unittest.main()
