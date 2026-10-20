#!/usr/bin/env python3
"""Rebuild a candidate from archived receipts and test its exact static payload.

Runs on a fresh GitHub-hosted worker. It invokes no model, handles no Vercel
credential and cannot promote a deployment. The publisher later verifies the
GitHub run identity and the downloaded artifact's own GitHub digest.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from artifacts import build_artifact, unpack, inventory
from contracts import canonical, digest, require, utcnow, validate_contract
from snapshot import build_snapshot
from storage import LocalStore
from validation import reconcile


def prepare_data(repo, store, destination):
    contract = validate_contract(json.loads((repo / "contracts/market.json").read_text()))
    latest = store.read("heads/latest-run.json")
    require(latest is not None, "No archived collection receipt")
    coverage = json.loads(store.get(latest["receipt"]))
    plan = store.read(f"runs/{coverage['runId']}/plan.json")
    archived = [store.read(f"runs/{coverage['runId']}/attempts/{r['attemptId']}.json") for r in coverage["receipts"]]
    require(archived == coverage["receipts"], "Worker summary differs from archived receipts")
    verified = reconcile(plan, archived, contract, utcnow(), store)
    previous = json.loads((repo / "web/src/data/generated/dailyMarket.json").read_text())
    production = store.read("heads/production.json")
    if production and not production.get("legacyBaseline"):
        from vercel import VercelAdapter
        saved = store.read(f"releases/{production['releaseId']}.json")
        require(saved is not None, "Previous published release missing")
        from publication import verify_acknowledgement
        verify_acknowledgement(saved["manifest"], VercelAdapter._get("https://securitymarketpulse.com", "/deployment-receipt.json"))
        previous = json.loads(store.get(saved["manifest"]["snapshot"]))
        prior_artifact = saved["manifest"]["artifact"]
        files = unpack(store.get(prior_artifact["archive"]))
        require(digest(inventory(files)) == prior_artifact["sha256"], "Published baseline payload differs")
        # Compare with what is actually deployed, rather than main's older
        # committed data, when deciding whether a certified value changed.
        (repo / "web/src/data/generated/certifiedCoverage.json").write_bytes(files["static/certified-coverage.json"])
    snapshot = build_snapshot(contract, plan, verified, store, utcnow(), previous=previous)
    raw = (json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n").encode()
    target = repo / "web/src/data/generated/dailyMarket.json"
    target.write_bytes(raw)
    target.with_suffix(".seal.json").write_bytes(canonical({"schemaVersion": 1, "fileSha256": digest(raw), "runId": snapshot["runId"], "contractSha256": digest(contract)}))
    sources = {}
    registrations = {s["id"]: s for s in contract["sources"]}
    for receipt in verified["receipts"]:
        if receipt["outcome"] not in ("updated", "checked_no_change"):
            continue
        source = registrations.get(receipt["sourceId"], {})
        if source.get("kind") not in ("sec_facts", "sec_submissions", "sec_documents"):
            continue
        for oid in receipt["observationIds"]:
            observed = store.read(f"observations/{oid}.json")
            store.get(observed["body"])
            sources[observed["requestedUrl"]] = {"path": str(store._path(observed["body"]["key"])), "sha256": observed["body"]["sha256"], "checkedAt": observed.get("verifiedAt", observed["fetchedAt"]), "contentType": observed.get("contentType", "application/json")}
    cache = destination / "sec-cache.json"
    cache.write_bytes(canonical({"overdueHours": contract["schedule"]["overdueHours"], "sources": sources}))
    return contract, verified, snapshot, raw, cache, latest["receipt"]["sha256"]


def run_gate(repo, store, destination, github_run_id, app_revision):
    destination.mkdir(parents=True, exist_ok=True)
    contract, coverage, snapshot, raw, cache, collection_hash = prepare_data(repo, store, destination)
    env = dict(os.environ, VERCEL_GIT_COMMIT_SHA=app_revision)
    checks, logs = {}, []
    for name in ("refresh:edgar", "refresh:filing-events", "certify:sec", "test"):
        child_env = dict(env)
        if name != "test":
            child_env["SMP_SEC_CACHE_MANIFEST"] = str(cache)
            child_env["NODE_OPTIONS"] = "--import=" + str(repo / "web/scripts/pipeline/sec-cache-fetch.mjs")
        log = destination / (name.replace(":", "-") + ".log")
        with log.open("wb") as output:
            result = subprocess.run(["npm", "run", name], cwd=repo / "web", env=child_env, stdout=output, stderr=output, timeout=1800)
        require(result.returncode == 0, f"RELEASE_GATE_FAILED_{name}")
        body = log.read_bytes()
        checks[name] = {"result": "pass", "logSha256": digest(body)}
        logs.append(body.decode("utf8", errors="replace"))
    tested = "\n".join(logs)
    counts = re.findall(r"# tests (\d+)|Ran (\d+) tests|\b(\d+) passed\b", tested)
    executed = sum(int(n) for groups in counts for n in groups if n)
    require(executed > 0, "Passing test output contains no executed tests")
    coverage_sec = json.loads((repo / "web/src/data/generated/certifiedCoverage.json").read_text())
    proof = json.loads((repo / "web/src/data/generated/certifiedVerification.json").read_text())
    require(coverage_sec["state"] == "complete", "SEC certification incomplete")
    snapshot_ref = store.put(raw)
    cohort = next(c for c in contract["certifiedCohorts"] if c["id"] == "sec")
    snapshot_ref.update(contractSha256=digest(contract), allChangedClaimsVerified=True,
                        secCertification={"required": len(cohort["supplierIds"])*len(cohort["claimGroups"]), "verified": len(proof["verifiedClaims"]), "drift": 0,
                                          "runId": coverage["runId"], "claimKeys": [p["key"] for p in proof["verifiedClaims"]]})
    artifact = build_artifact(store, repo / "web/dist", json.loads((repo / "web/vercel.json").read_text()))
    receipt = {"result": "pass", "executedTests": executed, "checks": checks, "githubRunId": github_run_id,
               "appRevision": app_revision, "snapshotSha256": snapshot_ref["sha256"], "artifactSha256": artifact["sha256"],
               "runId": coverage["runId"], "contractSha256": digest(contract), "coverageSha256": digest(coverage),
               "collectionReceiptSha256": collection_hash,
               "archiveCommit": os.environ.get("SMP_ARCHIVE_COMMIT"), "archiveManifestSha256": os.environ.get("SMP_ARCHIVE_MANIFEST_SHA256")}
    (destination / "gate-receipt.json").write_bytes(canonical(receipt))
    (destination / "build.zip").write_bytes(store.get(artifact["archive"]))
    (destination / "snapshot.json").write_bytes(raw)
    (destination / "release-input.json").write_bytes(canonical({"artifact": artifact, "snapshot": snapshot_ref, "coverage": coverage}))
    # All downloadable files carry independent hashes in this exact test receipt.
    for path in (cache,):
        path.unlink()
    print(json.dumps({"result": "pass", "executedTests": executed, "artifactSha256": artifact["sha256"], "snapshotSha256": snapshot_ref["sha256"]}))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--destination", required=True)
    args = parser.parse_args()
    try:
        run_gate(Path(args.repo).resolve(), LocalStore(args.state), Path(args.destination).resolve(), int(os.environ["GITHUB_RUN_ID"]), os.environ["GITHUB_SHA"])
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(json.dumps({"ok": False, "reason": str(error)[:180]}), file=sys.stderr)
        raise SystemExit(2)
