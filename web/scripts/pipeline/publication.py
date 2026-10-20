"""Release manifests and deployment acknowledgement; no agent can waive gates."""
from contracts import digest, instant, require, valid_hash
from storage import ConflictError


def prepare_release(contract, coverage, snapshot, app_revision, artifact, test_receipt, previous, now, authority):
    require(len(app_revision) == 40 and all(c in "0123456789abcdef" for c in app_revision), "Pin a full reviewed application revision")
    require(coverage["contractSha256"] == digest(contract), "Coverage contract mismatch")
    age = (instant(now) - instant(coverage["checkedAt"])).total_seconds() / 3600
    require(0 <= age <= contract["schedule"]["overdueHours"], "Stale/future coverage cannot publish")
    require(snapshot["contractSha256"] == digest(contract), "Snapshot contract mismatch")
    require(test_receipt.get("result") == "pass" and test_receipt.get("executedTests", 0) > 0, "Executed passing tests required")
    require(test_receipt.get("artifactSha256") == artifact["sha256"], "Tests do not cover exact artifact")
    require(test_receipt.get("appRevision") == app_revision and test_receipt.get("snapshotSha256") == snapshot["sha256"], "Tests do not bind the code/data pair")
    require(valid_hash(artifact["sha256"]) and valid_hash(snapshot["sha256"]), "Release hashes invalid")
    require(coverage["complete"] or contract["publication"]["allowDegradedCoverage"], "Incomplete coverage held by policy")
    # Preserve the current fixed SEC cohort. General model confidence cannot satisfy it.
    sec = snapshot.get("secCertification", {})
    cohort = next(c for c in contract["certifiedCohorts"] if c["id"] == "sec")
    expected_keys = {f"{sid}.{group}" for sid in cohort["supplierIds"] for group in cohort["claimGroups"]}
    require(bool(expected_keys) and sec.get("required") == len(expected_keys) and sec.get("verified") == len(expected_keys) and sec.get("drift") == 0 and sec.get("runId") == coverage["runId"], "Fresh complete SEC certification required")
    require(len(sec.get("claimKeys", [])) == len(expected_keys) and set(sec["claimKeys"]) == expected_keys, "SEC claim inventory missing, duplicated or changed")
    require(snapshot.get("allChangedClaimsVerified") is True, "Unverified changed facts cannot publish")
    require(authority is not None and authority.verify_test_receipt(test_receipt, artifact), "Trusted workflow provenance required")
    manifest = {"schemaVersion": 1, "sequence": (previous or {}).get("sequence", 0) + 1,
                "parentReleaseId": (previous or {}).get("releaseId"), "createdAt": now,
                "appRevision": app_revision, "contractSha256": digest(contract),
                "runId": coverage["runId"], "coverageOutcome": coverage["outcome"],
                "snapshot": snapshot, "artifact": artifact, "testReceiptSha256": digest(test_receipt)}
    return {**manifest, "releaseId": digest(manifest)}


def verify_acknowledgement(manifest, receipt):
    require(receipt.get("ready") is True, "Deployment not ready")
    require(receipt.get("appRevision") == manifest["appRevision"], "Deployed code differs")
    require(receipt.get("dataReleaseId") == manifest["releaseId"], "Deployed data release differs")
    require(receipt.get("snapshotSha256") == manifest["snapshot"]["sha256"], "Deployed snapshot differs")
    require(receipt.get("artifactSha256") == manifest["artifact"]["sha256"], "Deployed artifact differs")
    require(receipt.get("contractSha256") == manifest["contractSha256"], "Deployed coverage contract differs")
    return receipt


def publish(store, contract, manifest, adapter):
    require(contract["publication"]["enabled"] is True, "Production cutover is not enabled")
    require(adapter.production_paths_controlled(), "Competing production paths have not been closed")
    with store.lock("production-publisher"):
        previous = store.read("heads/production.json")
        require(previous is not None, "Import and verify the current production baseline before cutover")
        require((previous or {}).get("releaseId") == manifest["parentReleaseId"], "Stale release parent")
        require(manifest["sequence"] == (previous or {}).get("sequence", 0) + 1, "Release sequence regressed")
        deployment = adapter.stage(manifest)
        verify_acknowledgement(manifest, adapter.probe(deployment))
        try:
            adapter.promote(deployment)
            ack = verify_acknowledgement(manifest, adapter.probe_production())
        except Exception:
            if previous:
                adapter.rollback(previous["deploymentId"])
                restored = adapter.probe_production()
                require(restored.get("ready") is True and restored.get("dataReleaseId") == previous["releaseId"], "ROLLBACK_NOT_ACKNOWLEDGED")
                store.write_once(f"rollback-events/{manifest['releaseId']}.json", {"failedReleaseId": manifest["releaseId"], "restoredReleaseId": previous["releaseId"]})
            raise
        store.write_once(f"releases/{manifest['releaseId']}.json", {"manifest": manifest, "acknowledgement": ack})
        head = {"releaseId": manifest["releaseId"], "sequence": manifest["sequence"], "deploymentId": deployment}
        store.compare_and_swap("production", previous, head)
        return head


def health(coverage, now, overdue_hours=30, expected_contract=None):
    if coverage is None:
        return {"healthy": False, "reason": "NO_SUCCESSFUL_RUN_RECEIPT"}
    if expected_contract is not None and coverage.get("contractSha256") != expected_contract:
        return {"healthy": False, "reason": "COVERAGE_CONTRACT_DIFFERS"}
    age = (instant(now) - instant(coverage["checkedAt"])).total_seconds() / 3600
    complete = coverage.get("complete") is True and coverage["requiredTasks"] > 0 and coverage["successfulTasks"] == coverage["requiredTasks"] and coverage.get("gapTaskIds") == []
    return {"healthy": complete and 0 <= age <= overdue_hours,
            "reason": "COMPLETE" if complete and 0 <= age <= overdue_hours else "OVERDUE_OR_INCOMPLETE_COVERAGE",
            "ageHours": age, "requiredTasks": coverage["requiredTasks"], "successfulTasks": coverage["successfulTasks"]}
