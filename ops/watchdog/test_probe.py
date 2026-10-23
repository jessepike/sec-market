"""The real timer and archived execution must agree before monitoring is green."""
import copy
import importlib.util
import unittest
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


if __name__ == "__main__":
    unittest.main()
