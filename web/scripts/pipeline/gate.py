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
from snapshot import build_snapshot, collector_continuity
from storage import LocalStore
from validation import reconcile


def prepare_corrections(repo, store, contract, coverage, previous_bundle=None, now=None):
    """Replay real archived admissions before any application build command."""
    from corrections import load_policy, project_bundle
    context = load_policy(repo, contract)
    latest = store.read("heads/correction-collection.json")
    require(latest and latest.get("runId") == coverage["runId"], "CURRENT_CORRECTION_COLLECTION_REQUIRED")
    outcome = json.loads(store.get(latest["outcome"]))
    require(outcome.get("runId") == coverage["runId"] and outcome.get("policySha256") == context["policySha256"],
            "CORRECTION_COLLECTION_POLICY_OR_RUN_DIFFERS")
    moment = now or utcnow()
    bundle = project_bundle(repo, store, contract, outcome, previous_bundle=previous_bundle, publication_at=moment)
    old_ids = {group["id"] for group in (previous_bundle or {}).get("groups", [])}
    raw = (json.dumps(bundle, indent=2, ensure_ascii=False) + "\n").encode()
    seal = {"schemaVersion": 1, "fileSha256": digest(raw), "policySha256": context["policySha256"],
            "groupIds": [group["id"] for group in bundle["groups"]],
            "targetIds": [target["targetId"] for group in bundle["groups"] for target in group["targets"]],
            "newGroupIds": [group["id"] for group in bundle["groups"] if group["id"] not in old_ids],
            "publicationDate": moment[:10]}
    target = repo / "web/src/data/generated/factualCorrections.json"
    target.write_bytes(raw)
    target.with_suffix(".seal.json").write_bytes(canonical(seal))
    return seal


def prepare_data(repo, store, destination):
    contract = validate_contract(json.loads((repo / "contracts/market.json").read_text()))
    latest = store.read("heads/latest-run.json")
    require(latest is not None, "No archived collection receipt")
    coverage = json.loads(store.get(latest["receipt"]))
    plan = store.read(f"runs/{coverage['runId']}/plan.json")
    archived = [store.read(f"runs/{coverage['runId']}/attempts/{r['attemptId']}.json") for r in coverage["receipts"]]
    require(archived == coverage["receipts"], "Worker summary differs from archived receipts")
    verified = reconcile(plan, archived, contract, utcnow(), store)
    collector=store.read('heads/dailySnapshot.json') or store.read('heads/cloud-snapshot.json')
    require(collector is not None, 'Archived collector continuity missing')
    continuity=collector_continuity(collector,contract,coverage,store)
    previous = json.loads((repo / "web/src/data/generated/dailyMarket.json").read_text())
    previous_corrections = None
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
        if "static/factual-corrections.json" in files:
            previous_corrections = json.loads(files["static/factual-corrections.json"])
    if (repo / "contracts/factual-corrections.json").exists():
        prepare_corrections(repo, store, contract, coverage, previous_bundle=previous_corrections)
    snapshot = build_snapshot(contract, plan, verified, store, utcnow(), previous=previous,continuity=continuity)
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
    correction_path = repo / "web/src/data/generated/factualCorrections.json"
    correction_proof = None
    if (repo / "contracts/factual-corrections.json").exists():
        correction_proof = json.loads(correction_path.with_suffix(".seal.json").read_text())
        require(correction_proof["fileSha256"] == digest(correction_path.read_bytes()), "CORRECTION_PROJECTION_CHANGED_DURING_GATE")
        require((repo / "web/dist/factual-corrections.json").read_bytes() == correction_path.read_bytes(), "CORRECTION_PUBLIC_EXPORT_DIFFERS")
        snapshot_ref["factualCorrections"] = correction_proof
    artifact = build_artifact(store, repo / "web/dist", json.loads((repo / "web/vercel.json").read_text()))
    receipt = {"result": "pass", "executedTests": executed, "checks": checks, "githubRunId": github_run_id,
               "appRevision": app_revision, "snapshotSha256": snapshot_ref["sha256"], "artifactSha256": artifact["sha256"],
               "runId": coverage["runId"], "contractSha256": digest(contract), "coverageSha256": digest(coverage),
               "collectionReceiptSha256": collection_hash,
               "archiveCommit": os.environ.get("SMP_ARCHIVE_COMMIT"), "archiveManifestSha256": os.environ.get("SMP_ARCHIVE_MANIFEST_SHA256")}
    if correction_proof:
        receipt["factualCorrections"] = correction_proof
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
