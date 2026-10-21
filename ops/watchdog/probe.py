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
    queue = read_archive("heads/cloud-snapshot.json" if native else "heads/dailySnapshot.json").get("reviewQueue", [])
    if queue:
        problems.append(f"OWNER_REVIEW_QUEUE_{len(queue)}")
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
    if not contract["publication"]["enabled"]:
        print(json.dumps({"activated": False, "healthy": False, "reason": "DAILY_CUTOVER_NOT_ENABLED"}))
        return 0  # Explicitly unactivated; a green Actions job is not coverage evidence.
    now = utcnow()
    try:
        commit = api("git/ref/archive/market-evidence")["object"]["sha"]
        def read_archive(key, reference=None):
            if not key.replace("/", "").replace("-", "").replace("_", "").replace(".", "").isalnum() or ".." in key.split("/"):
                raise ValueError("Invalid independent archive key")
            body = api(f"contents/state/{key}?ref={commit}", raw=True)
            if reference and (digest(body) != reference["sha256"] or len(body) != reference["bytes"]):
                raise ValueError("Independent coverage object hash differs")
            return json.loads(body)
        result = inspect(contract, read_archive, get_json, now, GitHubAuthority())
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        result = {"healthy": False, "checkedAt": now, "reasons": ["INDEPENDENT_PROBE_FAILED", type(error).__name__]}
    if args.notify:
        result["notification"] = notify(result)
    print(json.dumps(result, indent=2))
    return 0 if result["healthy"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
