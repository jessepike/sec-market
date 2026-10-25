"""Read-only actual two-primary audit. Require real run, artifact, acknowledged manifest and delta-reuse inputs."""
import argparse
import base64
import gzip
import hashlib
import io
import json
import re
import socket
import sys
import subprocess
import stat
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from unittest.mock import patch

PHASE = "not_started"
def stage(name):
    global PHASE
    PHASE = name
def require(ok, message):
    if not ok:
        raise ValueError(message)
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def pin(path):
    raw = path.read_bytes()
    return {"sha256": sha(raw), "bytes": len(raw), "mtimeNs": path.stat().st_mtime_ns}
def read_json(path):
    return json.loads(Path(path).read_bytes())
def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")
def compressed(raw, path):
    output = io.BytesIO()
    with gzip.GzipFile(filename="", fileobj=output, mode="wb", compresslevel=9, mtime=0) as file:
        file.write(raw)
    packed = output.getvalue()
    require(gzip.decompress(packed) == raw, "GZIP_ROUND_TRIP_DIFFERS")
    path.write_bytes(packed)
    return {"file": path.name, "rawSha256": sha(raw), "rawBytes": len(raw),
            "gzipSha256": sha(packed), "gzipBytes": len(packed),
            "byteExactRoundTrip": True, "gzipMtime": 0, "gzipEmbeddedFilename": ""}
def manifest(root, expected):
    path = root / "archive-manifest.json"
    raw = path.read_bytes()
    require(sha(raw) == expected, "MANIFEST_PIN_DIFFERS")
    data = json.loads(raw)
    require(data.get("schemaVersion") == 1 and type(data.get("files")) is list, "MANIFEST_SHAPE_DIFFERS")
    entries = {}
    for row in data["files"]:
        key = row["key"]
        parts = PurePosixPath(key).parts
        require(parts and parts[0] == "state" and ".." not in parts and not key.startswith("/"), "MANIFEST_PATH_INVALID")
        require(key not in entries, "DUPLICATE_MANIFEST_KEY")
        entries[key] = row
    return entries, pin(path)
class ReadOnlyArchive:
    def __init__(self, root, entries):
        self.root, self.entries, self.touched = root, entries, {}
    def raw(self, key):
        require(type(key) is str and ".." not in PurePosixPath(key).parts and not key.startswith("/"),
                "READ_PATH_INVALID")
        path = self.root / "state" / key
        row = self.entries.get("state/" + key)
        if row is None:
            require(not path.exists(), "UNMANIFESTED_FILE")
            return None
        require(not path.is_symlink(), "SOURCE_SYMLINK")
        raw = path.read_bytes()
        require(sha(raw) == row["sha256"] and len(raw) == row["bytes"], "SOURCE_BYTES_DIFFER")
        before = pin(path)
        require(self.touched.setdefault(str(path), before) == before, "SOURCE_CHANGED_DURING_REPLAY")
        return raw
    def read(self, key):
        raw = self.raw(key)
        return json.loads(raw) if raw is not None else None
    def get(self, ref):
        raw = self.raw(ref["key"])
        require(raw is not None and sha(raw) == ref["sha256"] and len(raw) == ref["bytes"], "REFERENCE_DIFFERS")
        return raw
    def unchanged(self):
        for path, before in self.touched.items():
            require(pin(Path(path)) == before, "READ_ONLY_INPUT_CHANGED")
def audit(config):
    stage("validate_actual_metadata")
    repo = Path(config["repoRoot"])
    root = Path(config["archiveRoot"])
    baseline = Path(config["baselineRoot"])
    out = Path(config["outputDirectory"])
    require(not out.is_relative_to(repo) and not out.is_relative_to(root) and not out.is_relative_to(baseline),
            "OUTPUT_MUST_BE_OUTSIDE_CHECKOUT_AND_ARCHIVES")
    out.mkdir(parents=True, exist_ok=True)
    require(config.get("actualInputsProvided") is True, "ACTUAL_INPUTS_NOT_PROVIDED")
    require(re.fullmatch(r"[0-9a-f]{40}", config["appRevision"]) is not None, "ACTUAL_APP_REVISION_REQUIRED")
    run = read_json(config["runMetadata"])
    artifact = read_json(config["artifactMetadata"])
    result = read_json(config["receipt"])
    require(type(config["runId"]) is int and config["runId"] > 0, "ACTUAL_RUN_ID_REQUIRED")
    require(run["id"] == config["runId"] and run["head_sha"] == config["appRevision"] and
            run["event"] == "workflow_dispatch" and run["head_branch"] == "main" and
            run["status"] == "completed" and run["run_attempt"] == 1 and run["repository"]["private"],
            "ACTUAL_RUN_IDENTITY_DIFFERS")
    require(run["repository"]["full_name"] == "jessepike/sec-market" and run["repository"]["id"] == 1335546492, "ACTUAL_REPOSITORY_DIFFERS")
    archive_bytes = Path(config["artifactZip"]).read_bytes()
    require(artifact["workflow_run"]["id"] == run["id"] and
            artifact["workflow_run"]["head_sha"] == run["head_sha"] and artifact["name"] == "source-probe-receipt" and
            artifact["expired"] is False and len(archive_bytes) == artifact["size_in_bytes"] and
            "sha256:" + sha(archive_bytes) == artifact["digest"], "ARTIFACT_IDENTITY_OR_DIGEST_DIFFERS")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zipped:
        names = zipped.namelist()
        require(len(names) == 1 and names[0] == "smp-collection-receipt.json", "ARTIFACT_FILE_INVENTORY_DIFFERS")
        require(zipped.read(names[0]) == Path(config["receipt"]).read_bytes(), "RECEIPT_BYTES_DIFFER_FROM_ARTIFACT")
    require(artifact["workflow_run"]["repository_id"] == run["repository"]["id"] and
            artifact["workflow_run"]["head_repository_id"] == run["repository"]["id"],
            "ARTIFACT_REPOSITORY_DIFFERS")
    for relative, expected in config["expectedCodePins"].items():
        require(sha((repo / relative).read_bytes()) == expected, "LOCAL_REPLAY_CODE_PIN_DIFFERS:" + relative)
        committed = subprocess.run(["git", "-C", str(repo), "show", config["appRevision"] + ":" + relative], check=True, stdout=subprocess.PIPE).stdout
        require(sha(committed) == expected, "ACTUAL_APP_CODE_PIN_DIFFERS:" + relative)
    if not isinstance(result.get("diagnostic"), dict) or not isinstance(result.get("archive"), dict):
        write_json(out / "failure-before-diagnostic.json",
                   {"actualRunId": run["id"], "conclusion": run["conclusion"], "receipt": result,
                    "safePhase": "no_complete_diagnostic_or_archive_receipt",
                    "qualificationCredit": False, "retryAuthorized": False})
        raise ValueError("ACTUAL_DIAGNOSTIC_OR_ACK_UNAVAILABLE")
    require(result["githubRunId"] == str(run["id"]) and result["githubRunAttempt"] == 1 and
            result["githubEventName"] == run["event"] and result["githubRef"] == "refs/heads/main" and
            result["appRevision"] == run["head_sha"] and result["checkpointProfile"] == "source_probe",
            "OUTER_DIAGNOSTIC_IDENTITY_DIFFERS")
    stage("authenticate_acknowledged_archive")
    acknowledgement = result["archive"]
    commit = read_json(config["ackCommitMetadata"])
    tree = read_json(config["ackRootTreeMetadata"])
    require(commit["sha"] == acknowledgement["commit"] and tree["sha"] == commit["tree"]["sha"],
            "ACK_COMMIT_TREE_DIFFERS")
    entries, manifest_seal = manifest(root, acknowledgement["manifestSha256"])
    manifest_rows = [row for row in tree["tree"] if row["path"] == "archive-manifest.json"]
    require(len(manifest_rows) == 1 and len(entries) == acknowledgement["files"], "ACK_MANIFEST_COUNT_DIFFERS")
    raw_manifest = (root / "archive-manifest.json").read_bytes()
    blob_sha = hashlib.sha1(b"blob " + str(len(raw_manifest)).encode() + b"\0" + raw_manifest).hexdigest()
    require(blob_sha == manifest_rows[0]["sha"] and len(raw_manifest) == manifest_rows[0]["size"],
            "ACK_MANIFEST_GIT_BLOB_DIFFERS")
    old, baseline_seal = manifest(baseline, config["baselineManifestSha256"])
    baseline_store = ReadOnlyArchive(baseline, old)
    base_proof_raw = Path(config["baselineFullAudit"]).read_bytes()
    require(sha(base_proof_raw) == config["baselineFullAuditSha256"], "BASELINE_FULL_AUDIT_PIN_DIFFERS")
    base_proof = json.loads(base_proof_raw)
    require(base_proof["acknowledgedArchive"]["commit"] == config["baselineCommit"] ==
            "d6606a4f5dd1e1afc5f16dea6d91bc422347f8aa" and
            base_proof["manifest"]["sha256"] == config["baselineManifestSha256"] ==
            "40873bfd2dca9836b58ac325a3afb32919fb463b2082752cb72fc785a2d7239d" and
            base_proof["allEntriesVerified"] == len(old) == 48045, "BASELINE_AUTHENTICATION_DIFFERS")
    reuse_raw = Path(config["baselineReuseProof"]).read_bytes()
    reuse = json.loads(reuse_raw)
    require(reuse["baselineRoot"] == str(baseline) and reuse["destination"] == str(root) and
            reuse["baselineManifestSha256"] == config["baselineManifestSha256"] and
            reuse["acknowledgedManifestSha256"] == acknowledgement["manifestSha256"] and
            reuse["baselineFullAuditSha256"] == config["baselineFullAuditSha256"],
            "DELTA_REUSE_PROVENANCE_DIFFERS")
    reused, new_checked = [], []
    def identity(path):
        info = path.stat()
        require(stat.S_ISREG(info.st_mode) and not path.is_symlink(), "NONREGULAR_ARCHIVE_ENTRY")
        return {"device": info.st_dev, "inode": info.st_ino, "bytes": info.st_size, "mtimeNs": info.st_mtime_ns}
    for key, row in entries.items():
        path = root / key
        require(not path.is_symlink() and path.resolve().is_relative_to(root), "ARCHIVE_PATH_ESCAPE")
        if old.get(key) == row:
            saved = reuse["reusedEntries"].get(key)
            require(saved is not None and identity(path) == identity(baseline / key) == saved and
                    saved["bytes"] == row["bytes"], "FROZEN_HARDLINK_REUSE_DIFFERS:" + key)
            reused.append(key)
        else:
            raw = path.read_bytes()
            require(sha(raw) == row["sha256"] and len(raw) == row["bytes"], "DELTA_ARCHIVE_ENTRY_DIFFERS:" + key)
            if key.startswith("state/objects/"):
                require(Path(key).name == sha(raw), "CONTENT_ADDRESS_DIFFERS")
            new_checked.append(key)
    require(set(reuse["reusedEntries"]) == set(reused) and set(reuse["neededEntries"]) == set(new_checked),
            "DELTA_INVENTORY_DIFFERS")
    present = {str(path.relative_to(root)) for path in (root / "state").rglob("*") if path.is_file()}
    require(present == set(entries), "ARCHIVE_EXTRA_OR_MISSING_FILES")
    require(all(key in entries for key in old), "BASELINE_ENTRIES_MISSING")
    stage("replay_closed_report_and_admissions")
    sys.path[:0] = [str(repo / "web/scripts/pipeline"), str(repo / "ops/ci")]
    import q4_primary_qualification as operation
    from storage import LocalStore
    from contracts import digest, instant
    from corrections import _index, group_review_policy, replay_admission
    store = ReadOnlyArchive(root, entries)
    policy_raw = (repo / "contracts/market.json").read_bytes()
    policy = json.loads(policy_raw)
    report = result["diagnostic"]
    plan_raw = store.get(report["planReference"])
    require(report["operation"] == operation.OPERATION and
            result["contractSha256"] == report["contractSha256"] == digest(policy), "OPERATION_POLICY_DIFFERS")
    with patch.object(socket.socket, "connect", side_effect=AssertionError("NO_NETWORK")), \
            patch.object(LocalStore, "__init__", side_effect=AssertionError("NO_FROZEN_LOCALSTORE")):
        replay = operation.verify_report(policy, store, plan_raw, report)
        normalized = operation.validate_plan(policy, store, plan_raw)
        require(sha(plan_raw) == config["expectedPlanRawSha256"] ==
                "3a25e8e262b51fbf6f872c8655b25c9d255cf52b32ca0e9c4afa73d78893fbd4" and
                digest(json.loads(plan_raw)) == "3b7fc7c4de41c68471d4343f103e7e5ee705e5a4a51f760f5387e34a49a660ee" and
                len(plan_raw) == 4211, "ACTUAL_REVIEWED_PLAN_DIFFERS")
        require(type(result["executionCompleted"]) is bool and
                result["executionCompleted"] is report["executionCompleted"] and result["apiFallback"] is False and
                result["outcome"] in (("completed_diagnostic",) if report["executionCompleted"] else ("budget_denied", "cancelled")),
                "OUTER_COMPLETION_DIFFERS")
        require(result["facts"] == [] and result["semanticAdmission"] is False and result["coverageCredit"] is False and
                all(type(result[k]) is int and result[k] == 0 for k in ("modelCalls", "sourceChecksCredited", "qualifiedSources")) and
                result["publication"] == {"published": False, "reason": "SOURCE_PROBE_DIAGNOSTIC_ONLY"},
                "OUTER_CREDIT_OR_PUBLICATION_DIFFERS")
        require(instant(run["run_started_at"]) <= instant(report["startedAt"]) <=
                instant(report["checkedAt"]) <= instant(run["updated_at"]), "REPORT_OUTSIDE_ACTUAL_RUN")
        archived = store.read("ci/source-probe-runs/" + str(run["id"]) + "-1.json")
        require(archived == {key: value for key, value in result.items() if key != "archive"},
                "ARCHIVED_RESULT_DIFFERS_FROM_ARTIFACT")
        requests = json.loads((repo / "contracts/factual-corrections.json").read_bytes())
        stamp = json.loads((repo / "web/src/data/tracker/factualCorrectionPolicy.json").read_bytes())
        admissions = []
        for group in requests["groups"]:
            review_policy = group_review_policy(group, policy, requests["baseline"]["sha256"])
            require(review_policy == stamp["reviewPolicySha256ByGroup"][group["id"]], "OLD_ADMISSION_POLICY_DIFFERS")
            ref = store.read(_index(group, review_policy))["admission"]
            before = store.get(ref)
            replay_admission(group, ref, store, policy, review_policy, report["checkedAt"])
            require(store.get(ref) == before, "OLD_ADMISSION_CHANGED")
            admissions.append({"groupId": group["id"], "policySha256": review_policy, "admission": ref})
        stage("reconcile_actual_charges_and_preservation")
        day = report["reservationContext"]["budgetDay"]
        budget_key = "state/heads/budget-" + day + ".json"
        allowed_changed = {budget_key, "state/heads/cloud-lease.json"}
        missing = [key for key in old if key not in entries]
        changed = [key for key in old if entries.get(key) != old[key]]
        added = [key for key in entries if key not in old]
        require(not missing and set(changed).issubset(allowed_changed), "BASELINE_EVIDENCE_CHANGED")
        require(all(not key.startswith("state/heads/") or key == budget_key for key in added), "NEW_NORMAL_HEAD")
        previous_budget = baseline_store.read(budget_key.removeprefix("state/"))
        require(report["reservationContext"]["initialBudget"] == previous_budget, "ACTUAL_STARTING_LEDGER_DIFFERS")
        require(previous_budget == {"calls": 80, "documents": 38, "fetches": 867}, "FROZEN_BASELINE_LEDGER_DIFFERS")
        final_budget = store.read(budget_key.removeprefix("state/"))
        require(report["reservationContext"]["currentBudget"] == final_budget, "FINAL_LEDGER_DIFFERS")
        lease = store.read("heads/cloud-lease.json")
        require(lease["sessionId"] == "github-" + str(run["id"]) + "-1" and
                lease["checkpointProfile"] == "source_probe" and isinstance(lease.get("releasedAt"), str),
                "DIAGNOSTIC_LEASE_UNRELEASED_OR_WRONG")
        escrow = store.read("ci/budget-escrows/" + digest(lease["sessionId"]) + ".json")
        initial = previous_budget or {"calls": 0, "documents": 0, "fetches": 0}
        require(escrow["before"] == previous_budget and escrow["ceiling"] ==
                {**initial, "fetches": max(initial["fetches"], policy["schedule"]["maxFetchesPerRun"])},
                "ESCROW_COUNTERS_DIFFERS")
        snapshot = store.read("heads/dailySnapshot.json")
        for ref in snapshot["factProvenance"].values():
            store.get(ref)
        baseline_snapshot = baseline_store.read("heads/dailySnapshot.json")
        require(snapshot == baseline_snapshot, "FACT_HOLD_OR_DATE_SNAPSHOT_CHANGED")
        require(len(snapshot["factProvenance"]) == 4 and len(snapshot["reviewQueue"]) == 38,
                "BASELINE_FACT_OR_HOLD_CARDINALITY_DIFFERS")
        gate_budget = store.read("heads/gate-budget-" + day + ".json")
        require(gate_budget == baseline_store.read("heads/gate-budget-" + day + ".json"),
                "ACTUAL_DAY_GATE_LEDGER_CHANGED")
        bootstrap = read_json(config["bootstrapCommitMetadata"])
        escrow_commit = read_json(config["escrowCommitMetadata"])
        escrow_budget = read_json(config["escrowBudgetMetadata"])
        require(bootstrap["parents"][0]["sha"] == config["baselineCommit"] and
                escrow_commit["parents"][0]["sha"] == bootstrap["sha"] and
                commit["parents"][0]["sha"] == escrow_commit["sha"] == acknowledgement["parentCommit"],
                "ACKNOWLEDGED_PARENT_CHAIN_DIFFERS")
        require(escrow_budget.get("encoding") in ("base64", "utf-8"), "ESCROW_BLOB_ENCODING_INVALID")
        escrow_raw = (base64.b64decode(escrow_budget["content"], validate=False)
                      if escrow_budget["encoding"] == "base64" else escrow_budget["content"].encode("utf-8"))
        require(json.loads(escrow_raw) == escrow["ceiling"], "REMOTE_ESCROW_HEAD_DIFFERS")
        escrow_blob = hashlib.sha1(b"blob " + str(len(escrow_raw)).encode() + b"\0" + escrow_raw).hexdigest()
        require(escrow_blob == escrow_budget["sha"], "REMOTE_ESCROW_BLOB_DIFFERS")
        escrow_url = escrow_budget.get("html_url", escrow_budget.get("display_url"))
        require(escrow_url == "https://github.com/jessepike/sec-market/blob/" + escrow_commit["sha"] + "/" + budget_key,
                "REMOTE_ESCROW_COMMIT_PATH_DIFFERS")
        rows = []
        for index, (request, row) in enumerate(zip(report["requests"], report["results"])):
            observed = None
            if request["observation"] is not None:
                wrapper = json.loads(store.get(request["observation"]))
                observed = json.loads(store.get(wrapper["rawObservation"]))
            body_artifact = None
            if row["body"] is not None:
                raw = store.get(row["body"])
                body_artifact = compressed(raw, out / ("response-" + str(index) + "-body.bin.gz"))
            rows.append({"sourceId": row["sourceId"], "requestedUrl": row["requestedUrl"],
                         "requestedAt": request["requestedAt"], "responseCheckedAt": request["responseCheckedAt"],
                         "observationWrapper": request["observation"], "rawObservation": observed,
                         "finalUrl": row["finalUrl"], "fetchedAt": row["fetchedAt"], "httpStatus": row["httpStatus"],
                         "contentType": row["contentType"], "body": row["body"], "accepted": row["accepted"],
                         "primaryShape": row["primaryShape"], "sourceRow": normalized["targets"][index]["sample"],
                         "classificationReason": row["reason"], "transportError": request["transportError"],
                         "denial": request["denial"], "reservation": request["reservation"],
                         "retainedKnownBody": body_artifact})
    store.unchanged()
    baseline_store.unchanged()
    require(pin(root / "archive-manifest.json") == manifest_seal and
            pin(baseline / "archive-manifest.json") == baseline_seal, "FROZEN_MANIFEST_CHANGED")
    stage("audit_complete")
    proof = {"actualRunId": run["id"], "event": run["event"], "appRevision": run["head_sha"],
             "conclusion": run["conclusion"], "acknowledgedArchive": acknowledgement,
             "manifest": manifest_seal, "manifestGitBlobSha": blob_sha, "allEntriesVerified": len(entries),
             "baselineCommit": config["baselineCommit"], "baselineManifest": baseline_seal,
             "baselineFullAuditSha256": config["baselineFullAuditSha256"],
             "authenticationMethod": "Previously fully authenticated frozen d660 entries reused through equal manifests and exact hardlink/stat continuity; all delta bytes hash-verified.",
             "previouslyAuthenticatedReusedEntries": len(reused),
             "newOrChangedEntriesHashVerified": len(new_checked),
             "deltaEntryKeys": new_checked,
             "baselineReuseProofSha256": sha(reuse_raw),
             "originalBaselineEntries": len(old), "changedBaselineEntries": changed, "newEntries": added,
             "immutableBaselineEntriesPreserved": sum(not key.startswith("state/heads/") for key in old),
             "normalHeadsPreserved": sum(key.startswith("state/heads/") and key not in changed for key in old),
             "reportReplay": replay, "actualRequestResults": rows, "startingBudget": previous_budget,
             "finalBudget": final_budget, "actualDayGateBudget": gate_budget,
             "escrow": escrow, "releasedLease": lease,
             "admissions": admissions, "factReferences": len(snapshot["factProvenance"]),
             "heldQueueEntries": len(snapshot["reviewQueue"]), "sourceValidUntil": snapshot["coverage"]["validUntil"],
             "inputSeals": store.touched, "baselineInputSeals": baseline_store.touched,
             "inputSealsUnchanged": True, "qualificationCredit": False,
             "coverageCredit": False, "semanticAdmission": False, "verifierSourceRequests": 0,
             "verifierModelRequests": 0, "verifierArchiveWrites": 0, "executedJavaScript": False,
             "actualProposalEvidenceComplete": report["proposalEvidenceComplete"],
             "actualAcceptedSamples": report["acceptedSamples"],
             "executionCompleted": report["executionCompleted"],
             "originalStreams": [{"sourceId": s["sourceId"], "asOf": s["asOf"], "inventoryCount": len(s["records"]),
                                  "currentWindowCount": len(s["currentWindowItems"]), "originalBody": s["initialBody"],
                                  "timezone": s["timezone"], "datePrecision": s["datePrecision"]}
                                 for s in report["streams"]]}
    write_json(out / "actual-diagnostic-audit.json", proof)
    return proof
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="JSON containing real run/API/artifact/archive file paths")
    args = parser.parse_args()
    config = read_json(args.config)
    try:
        result = audit(config)
    except Exception as error:
        out = Path(config["outputDirectory"])
        out.mkdir(parents=True, exist_ok=True)
        write_json(out / "audit-failure.json",
                   {"phase": PHASE, "errorType": type(error).__name__, "message": str(error)[:300],
                    "actualRunId": config.get("runId"), "qualificationCredit": False, "retryAuthorized": False})
        raise
    print(json.dumps({"actualRunId": result["actualRunId"], "entriesVerified": result["allEntriesVerified"],
                      "proposalEvidenceComplete": result["actualProposalEvidenceComplete"],
                      "acceptedSamples": result["actualAcceptedSamples"],
                      "actualCharges": result["finalBudget"]["fetches"] - (result["startingBudget"] or {}).get("fetches", 0),
                      "qualificationCredit": False}))
if __name__ == "__main__":
    main()
