#!/usr/bin/env python3
"""Independent GitHub-side probe for a worker that runs outside GitHub.

Read a pinned archive ref and actual production receipts. No model, worker
filesystem, Vercel secret or third-party notification service is required.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "web/scripts/pipeline"))
from contracts import canonical, digest, instant, plan_run, utcnow
from publication import health, verify_acknowledgement
from provenance import GitHubAuthority

REPO = "jessepike/sec-market"
TITLE = "Daily pipeline needs attention"


def api(path, raw=False):
    args = ["gh", "api", f"repos/{REPO}/{path}", "--header", "Cache-Control: no-cache"]
    if raw:
        args.extend(["--header", "Accept: application/vnd.github.raw+json"])
    result = subprocess.run(args, capture_output=True, timeout=60)
    if result.returncode:
        raise ValueError("Independent archive/API check unavailable")
    if len(result.stdout) > 40_000_000:
        raise ValueError("Health receipt exceeds byte budget")
    return result.stdout if raw else json.loads(result.stdout)


def get_json(url):
    request = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
    with urllib.request.urlopen(request, timeout=25) as response:
        if response.status != 200 or response.url != url:
            raise ValueError("Production health receipt failed or redirected")
        body = response.read(1_000_001)
        if len(body) > 1_000_000:
            raise ValueError("Production health receipt exceeds byte budget")
        return json.loads(body)


def inspect_collection(contract, read_archive, now, authority):
    """Check the installed Actions clock separately from source completeness.

    A dispatch can prove execution, but cannot prove the daily timer fired.
    The archive's trigger is compared with GitHub's own run metadata.
    """
    problems = []
    collector = read_archive("heads/cloud-collector.json")
    result = collector.get("result", {})
    run_id = result.get("githubRunId")
    if not str(run_id).isdigit():
        problems.append("COLLECTOR_RUN_ID_MISSING")
    else:
        run = authority._api(f"actions/runs/{run_id}")
        if (run.get("path") != ".github/workflows/subscription-collector.yml"
                or run.get("head_sha") != collector.get("appRevision")
                or run.get("event") != result.get("githubEventName")):
            problems.append("COLLECTOR_GITHUB_IDENTITY_DIFFERS")
        if collector.get("phase") != "finish" or run.get("status") != "completed":
            problems.append("COLLECTOR_DID_NOT_FINISH")
    runs = authority._api("actions/workflows/subscription-collector.yml/runs?event=schedule&per_page=10")["workflow_runs"]
    scheduled = next((r for r in runs if r.get("event") == "schedule" and r.get("head_branch") == "main"), None)
    if not scheduled:
        problems.append("NO_ACTUAL_SCHEDULED_COLLECTION")
    else:
        age = (instant(now) - instant(scheduled["created_at"])).total_seconds()/3600
        if not 0 <= age <= contract["schedule"]["overdueHours"]:
            problems.append("SCHEDULED_COLLECTION_OVERDUE")
        if scheduled.get("status") != "completed" or scheduled.get("conclusion") != "success":
            problems.append("SCHEDULED_COLLECTION_FAILED_OR_UNFINISHED")
        try:
            acknowledgement = read_archive(f"ci/collection-runs/{scheduled['id']}-{scheduled.get('run_attempt', 1)}.json")
            if (not acknowledgement or acknowledgement.get("executionCompleted") is not True
                    or str(acknowledgement.get("githubRunId")) != str(scheduled["id"])
                    or acknowledgement.get("githubEventName") != "schedule"
                    or acknowledgement.get("githubRef") != "refs/heads/main"
                    or acknowledgement.get("appRevision") != scheduled.get("head_sha")
                    or acknowledgement.get("contractSha256") != digest(contract)):
                problems.append("SCHEDULED_COLLECTION_RECEIPT_DIFFERS")
        except (KeyError, ValueError, OSError, subprocess.SubprocessError):
            problems.append("SCHEDULED_COLLECTION_RECEIPT_MISSING")
    latest = read_archive("heads/latest-run.json")
    coverage = read_archive(latest["receipt"]["key"], reference=latest["receipt"])
    state = health(coverage, now, contract["schedule"]["overdueHours"], digest(contract))
    if not state["healthy"]:
        problems.append(state["reason"])
    return {"healthy": not problems, "checkedAt": now, "runId": coverage["runId"],
            "reasons": problems, "publicationEnabled": contract["publication"]["enabled"],
            "scheduledRunUrl": scheduled.get("html_url") if scheduled else None,
            "successfulTasks": coverage["successfulTasks"], "requiredTasks": coverage["requiredTasks"]}


def inspect_corrections(context, read_archive, run_id):
    """Report correction work separately from the fixed source denominator."""
    try:
        head = read_archive("heads/correction-collection.json")
        if head.get("runId") != run_id:
            return ["CORRECTION_COLLECTION_COVERS_DIFFERENT_RUN"]
        outcome = read_archive(head["outcome"]["key"], reference=head["outcome"])
        if outcome.get("runId") != run_id or outcome.get("policySha256") != context["policySha256"]:
            return ["CORRECTION_COLLECTION_POLICY_OR_RUN_DIFFERS"]
        pending = outcome.get("pending", [])
        if pending or outcome.get("error"):
            return ["FACTUAL_CORRECTIONS_PENDING_" + str(len(pending))] if pending else ["FACTUAL_CORRECTION_INPUT_ERROR"]
        expected = [group["id"] for group in context["requests"]["groups"]]
        actual = [group["groupId"] for group in outcome.get("admitted", [])]
        if len(actual) != len(expected) or set(actual) != set(expected):
            return ["FACTUAL_CORRECTION_ADMISSIONS_INCOMPLETE"]
        return []
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError):
        return ["FACTUAL_CORRECTION_COLLECTION_MISSING_OR_INVALID"]


def inspect(contract, read_archive, get_live, now, authority=None):
    latest = read_archive("heads/latest-run.json")
    coverage = read_archive(latest["receipt"]["key"], reference=latest["receipt"])
    problems = []
    status = health(coverage, now, contract["schedule"]["overdueHours"], digest(contract))
    if not status["healthy"]:
        problems.append(status["reason"])
    expected = plan_run(contract, coverage["checkedAt"])
    if coverage["supplierCount"] != len(contract["suppliers"]) or coverage["requiredTasks"] != sum(t["required"] for t in expected["tasks"]):
        problems.append("COVERAGE_DENOMINATOR_DIFFERS")
    heartbeat = read_archive("heads/worker-heartbeat.json")
    age = (instant(now) - instant(heartbeat["finishedAt"])).total_seconds()/3600
    if not 0 <= age <= contract["schedule"]["overdueHours"]:
        problems.append("WORKER_HEARTBEAT_OVERDUE")
    if any(value != 0 for value in heartbeat.get("phases", {}).values()) or not heartbeat.get("phases"):
        problems.append("WORKER_PHASE_FAILED")
    native = heartbeat.get("executionMode") == "codex_cloud_native"
    if native:
        roles = {}
        for role in ("collector", "governance"):
            receipt = read_archive("heads/cloud-" + role + ".json")
            roles[role] = receipt
            checked_age = (instant(now) - instant(receipt["checkedAt"])).total_seconds()/3600
            if not 0 <= checked_age <= contract["schedule"]["overdueHours"] or receipt["phase"] != "finish":
                problems.append("CLOUD_" + role.upper() + "_NOT_FINISHED_OR_OVERDUE")
            if receipt.get("contractSha256") != digest(contract) or receipt["coverage"]["runId"] != coverage["runId"]:
                problems.append("CLOUD_" + role.upper() + "_COVERS_DIFFERENT_RUN_OR_POLICY")
        if roles["collector"]["sessionId"] == roles["governance"]["sessionId"]:
            problems.append("CLOUD_GOVERNANCE_CONTEXT_NOT_SEPARATE")
    production = read_archive("heads/production.json")
    if production.get("legacyBaseline"):
        problems.append("INITIAL_PRODUCTION_CUTOVER_PENDING")
        app = get_live("https://securitymarketpulse.com/app-release.json")
        if app != production.get("legacyAppReceipt"):
            problems.append("LEGACY_PRODUCTION_BASELINE_DIFFERS")
        return {"healthy": False, "checkedAt": now, "runId": coverage["runId"], "reasons": problems}
    saved = read_archive(f"releases/{production['releaseId']}.json")
    manifest = saved["manifest"]
    if authority:
        test = read_archive(f"gate-receipts/{manifest['testProvenance']['githubRunId']}.json")
        if digest(test) != manifest["testReceiptSha256"]:
            problems.append("RELEASE_TEST_RECEIPT_DIFFERS")
        authority.verify_test_receipt(test, manifest["artifact"])
    live = get_live("https://securitymarketpulse.com/deployment-receipt.json")
    try:
        verify_acknowledgement(manifest, live)
    except ValueError:
        problems.append("PRODUCTION_RELEASE_NOT_ACKNOWLEDGED")
    app = get_live("https://securitymarketpulse.com/app-release.json")
    if app.get("appRevision") != manifest["appRevision"] or app.get("dailySnapshotSha256") != manifest["snapshot"]["sha256"]:
        problems.append("DEPLOYED_APPLICATION_DATA_PAIR_DIFFERS")
    public = get_live("https://securitymarketpulse.com/daily-coverage.json")
    if public.get("runId") != coverage["runId"] or public.get("contractSha256") != digest(contract):
        problems.append("COLLECTION_HAS_NOT_REACHED_PRODUCTION")
    if public.get("complete") is not True or not public.get("validUntil") or instant(now) > instant(public["validUntil"]):
        problems.append("PUBLIC_COVERAGE_INCOMPLETE_OR_OVERDUE")
    if manifest.get("factualCorrections"):
        expected = manifest["factualCorrections"]
        public_corrections = get_live("https://securitymarketpulse.com/factual-corrections.json")
        if (public_corrections.get("enabled") is not True or public_corrections.get("policySha256") != expected["policySha256"]
                or [g["id"] for g in public_corrections.get("groups", [])] != expected["groupIds"]
                or [t["targetId"] for g in public_corrections.get("groups", []) for t in g["targets"]] != expected["targetIds"]
                or app.get("factualCorrections", {}).get("fileSha256") != expected["fileSha256"]):
            problems.append("PUBLIC_FACTUAL_CORRECTION_INVENTORY_DIFFERS")
    queue = read_archive("heads/cloud-snapshot.json" if native else "heads/dailySnapshot.json").get("reviewQueue", [])
    if queue:
        problems.append(f"HELD_CLAIMS_{len(queue)}")
    return {"healthy": not problems, "checkedAt": now, "runId": coverage["runId"], "reasons": problems}


def notify(result):
    issues = api("issues?state=open&per_page=100&sort=updated&direction=desc")
    existing = next((i for i in issues if i["title"] == TITLE and "pull_request" not in i), None)
    body = ("The independent daily pipeline probe " + ("recovered." if result["healthy"] else "needs attention.")
            + "\n\nChecked: " + result["checkedAt"] + "\n\nReasons: " + ", ".join(result["reasons"])
            + "\n\nNo missing check is counted as fresh. Inspect the daily coverage receipt and the private refs/archive/market-evidence ref."
            + "\n\n[Daily coverage](https://securitymarketpulse.com/daily-coverage.json)")
    if result["healthy"] and not existing:
        return {"delivery": "no_alert_needed"}
    import tempfile
    with tempfile.TemporaryDirectory(prefix="smp-health-") as directory:
        file = Path(directory) / "issue.json"
        if existing:
            payload = {"body": body, "state": "closed" if result["healthy"] else "open"}
            path, method = f"issues/{existing['number']}", "PATCH"
        else:
            payload = {"title": TITLE, "body": body, "assignees": ["jessepike"]}
            path, method = "issues", "POST"
        file.write_bytes(canonical(payload))
        sent = subprocess.run(["gh", "api", f"repos/{REPO}/{path}", "--method", method, "--input", str(file)], capture_output=True, timeout=60)
        if sent.returncode:
            raise ValueError("GITHUB_OWNER_ALERT_DELIVERY_FAILED")
        issue = json.loads(sent.stdout)
        return {"delivery": "github_issue_updated", "url": issue["html_url"], "number": issue["number"], "state": issue["state"], "notificationTransport": "GitHub account notification settings"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notify", action="store_true")
    args = parser.parse_args()
    contract = json.loads((ROOT / "contracts/market.json").read_text())
    now = utcnow()
    result = None
    try:
        commit = api("git/ref/archive/market-evidence")["object"]["sha"]
        def read_archive(key, reference=None):
            if not key.replace("/", "").replace("-", "").replace("_", "").replace(".", "").isalnum() or ".." in key.split("/"):
                raise ValueError("Invalid independent archive key")
            body = api(f"contents/state/{key}?ref={commit}", raw=True)
            if reference and (digest(body) != reference["sha256"] or len(body) != reference["bytes"]):
                raise ValueError("Independent coverage object hash differs")
            return json.loads(body)
        authority = GitHubAuthority()
        result = inspect_collection(contract, read_archive, now, authority)
        if (ROOT / "contracts/factual-corrections.json").exists():
            from corrections import load_policy
            context = load_policy(ROOT, contract)
            result["reasons"] += inspect_corrections(context, read_archive, result["runId"])
            result["healthy"] = not result["reasons"]
        if contract["publication"]["enabled"]:
            publication = inspect(contract, read_archive, get_json, now, authority)
            result["reasons"] = list(dict.fromkeys(result["reasons"] + publication["reasons"]))
            result["healthy"] = not result["reasons"]
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        result = {**(result or {}), "healthy": False, "checkedAt": now,
                  "reasons": list(dict.fromkeys((result or {}).get("reasons", []) + ["INDEPENDENT_PROBE_FAILED", type(error).__name__]))}
    if args.notify:
        result["notification"] = notify(result)
    print(json.dumps(result, indent=2))
    return 0 if result["healthy"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
