#!/usr/bin/env python3
"""Credential-free hosting proof. Does not run models, publish or alter the archive."""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "web/scripts/pipeline"))
from archive import GitArchive
from contracts import digest, require, utcnow
from fetcher import Fetcher
from storage import LocalStore


def run(root):
    require(os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_REPOSITORY") == "jessepike/sec-market", "Use the actual private repository's GitHub runner")
    root = Path(root).resolve()
    require(not root.is_relative_to(REPO), "Canary state must be outside the application checkout")
    require(shutil.disk_usage(root.parent).free >= 5_000_000_000, "Insufficient disk for verified archive restore")
    revision = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    archive = GitArchive(root / "mirror", "https://github.com/jessepike/sec-market.git")
    restored = archive.restore(root / "state")
    state = LocalStore(root / "state")
    latest = state.read("heads/latest-run.json")
    require(latest is not None, "Archive has no collection receipt")
    coverage = json.loads(state.get(latest["receipt"]))
    contract = json.loads((REPO / "contracts/market.json").read_text())
    require(coverage["contractSha256"] == digest(contract), "Canary archive uses another source contract")
    source = next(s for s in contract["sources"] if s["kind"] == "sec_facts" and s["registration"] == "verified")
    # A real source probe from the actual runner, distinct from old coverage.
    observation = Fetcher(state, timeout=20).fetch(source)
    value = json.loads(state.get(observation["body"])) if observation.get("body") else {}
    source_ok = observation["status"] == "fetched" and isinstance(value.get("facts"), dict) and bool(value.get("cik"))
    result = {"kind": "credential-free-github-host-canary", "checkedAt": utcnow(),
              "appRevision": revision, "githubRunId": os.environ.get("GITHUB_RUN_ID"),
              "runnerOs": platform.system(), "archive": restored,
              "archivedCoverage": {"runId": coverage["runId"], "successfulTasks": coverage["successfulTasks"], "requiredTasks": coverage["requiredTasks"], "complete": coverage["complete"]},
              "sourceProbe": {"sourceId": source["id"], "checkedAt": observation["fetchedAt"], "outcome": observation["status"], "httpStatus": observation.get("httpStatus"), "validSecResponse": source_ok},
              "modelCalls": 0, "subscriptionCredentialsTransferred": False,
              "archiveChanged": False, "publicationAttempted": False,
              "recurringWorkerActivated": False, "runtimeCanaryPassed": source_ok}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        result = run(args.root)
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        result = {"runtimeCanaryPassed": False, "reason": type(error).__name__, "modelCalls": 0, "recurringWorkerActivated": False}
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["runtimeCanaryPassed"] else 2)
