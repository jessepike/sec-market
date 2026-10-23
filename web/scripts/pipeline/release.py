"""Connect the archived daily run to independent CI and immutable publication."""
import io
import json
import re
import subprocess
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from artifacts import inventory, unpack
from contracts import canonical, digest, require, utcnow
from provenance import GitHubAuthority
from publication import prepare_release, publish, recover_publication
from vercel import VercelAdapter


def import_gate(store, authority, run_id, artifact_id, expected_archive):
    meta = authority._api(f"actions/artifacts/{artifact_id}")
    payload = authority._api(f"actions/artifacts/{artifact_id}/zip", binary=True)
    require(meta.get("digest") == "sha256:" + digest(payload), "Gate transport digest differs")
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for item in archive.infolist():
            require(item.file_size <= 100_000_000, "Gate artifact member exceeds byte budget")
        require(len(archive.infolist()) <= 20, "Unexpected gate archive inventory")
        receipt = json.loads(archive.read("gate-receipt.json"))
        receipt["githubArtifactId"] = artifact_id
        require(receipt["githubRunId"] == run_id and receipt.get("archiveCommit") == expected_archive["commit"] and receipt.get("archiveManifestSha256") == expected_archive["manifestSha256"], "Gate covers a different evidence archive")
        inputs = json.loads(archive.read("release-input.json"))
        authority.verify_test_receipt(receipt, inputs["artifact"])
        build = archive.read("build.zip")
        fields = unpack(build)
        require(store.put(build) == inputs["artifact"]["archive"], "Gate build transport hash differs")
        require(store.put(inventory(fields)) == inputs["artifact"]["inventory"], "Gate tested file inventory differs")
        require(digest(inventory(fields)) == inputs["artifact"]["sha256"], "Gate payload digest differs")
        corrections = inputs["snapshot"].get("factualCorrections")
        require(corrections == receipt.get("factualCorrections"), "CORRECTION_GATE_RECEIPT_DIFFERS")
        if corrections:
            body = fields.get("static/factual-corrections.json")
            require(body is not None and digest(body) == corrections["fileSha256"], "CORRECTION_GATE_PUBLIC_BYTES_DIFFER")
            public = json.loads(body)
            require(public.get("enabled") is True and public.get("policySha256") == corrections["policySha256"]
                    and [g["id"] for g in public["groups"]] == corrections["groupIds"]
                    and [t["targetId"] for g in public["groups"] for t in g["targets"]] == corrections["targetIds"],
                    "CORRECTION_GATE_PUBLIC_INVENTORY_DIFFERS")
        raw = archive.read("snapshot.json")
        reference = store.put(raw)
        require(all(inputs["snapshot"].get(k) == v for k, v in reference.items()), "Gate snapshot bytes differ")
        require(receipt["coverageSha256"] == digest(inputs["coverage"]), "Gate coverage bytes differ")
    store.put(receipt)
    store.write_once(f"gate-receipts/{run_id}.json", receipt)
    return inputs, receipt


def dispatch_gate(store, archive, revision, authority, runner=subprocess.run):
    require(re.fullmatch(r"[a-f0-9]{40}", revision), "Pin reviewed application revision")
    existing = authority._api("actions/workflows/market-release-gate.yml/runs?event=workflow_dispatch&per_page=30")["workflow_runs"]
    known = {r["id"] for r in existing}
    with tempfile.TemporaryDirectory(prefix="smp-gate-dispatch-") as directory:
        path = Path(directory) / "dispatch.json"
        path.write_bytes(canonical({"ref": "main", "inputs": {"archive_commit": archive["commit"], "manifest_sha256": archive["manifestSha256"]}}))
        result = runner(["gh", "api", f"repos/{authority.repo}/actions/workflows/market-release-gate.yml/dispatches", "--method", "POST", "--input", str(path)], capture_output=True, timeout=60)
    require(result.returncode == 0, "GITHUB_RELEASE_GATE_DISPATCH_FAILED")
    deadline = time.monotonic() + 35*60
    selected = None
    while time.monotonic() < deadline:
        if selected is None:
            runs = authority._api("actions/workflows/market-release-gate.yml/runs?event=workflow_dispatch&per_page=30")["workflow_runs"]
            candidates = [r for r in runs if r["id"] not in known and r["head_branch"] == "main" and r["head_sha"] == revision]
            require(len(candidates) <= 1, "Concurrent release gates need explicit receipt selection")
            if candidates:
                selected = candidates[0]["id"]
                store.write_once(f"gate-requests/{archive['commit']}.json", {"githubRunId": selected, "archive": archive, "appRevision": revision})
        if selected:
            run = authority._api(f"actions/runs/{selected}")
            if run["status"] == "completed":
                require(run["conclusion"] == "success", "Independent release gate failed; retain production")
                artifacts = authority._api(f"actions/runs/{selected}/artifacts")["artifacts"]
                matches = [a for a in artifacts if a["name"] == "daily-market-gate" and not a["expired"]]
                require(len(matches) == 1, "Independent gate artifact missing or ambiguous")
                return selected, matches[0]["id"]
        time.sleep(10)
    raise TimeoutError("Independent release gate did not finish within its budget")


def preflight_corrections(repo, store, contract, collection_run_id, previous_manifest, now):
    """Pending reviews must not consume a scarce gate/publication attempt."""
    if not (Path(repo) / "contracts/factual-corrections.json").exists():
        return
    from corrections import project_bundle
    latest = store.read("heads/correction-collection.json")
    require(latest and latest.get("runId") == collection_run_id, "CURRENT_CORRECTION_COLLECTION_REQUIRED")
    outcome = json.loads(store.get(latest["outcome"]))
    require(outcome.get("runId") == collection_run_id, "CORRECTION_COLLECTION_RUN_DIFFERS")
    previous_bundle = None
    if previous_manifest:
        files = unpack(store.get(previous_manifest["artifact"]["archive"]))
        require(digest(inventory(files)) == previous_manifest["artifact"]["sha256"], "Previous correction baseline artifact differs")
        if "static/factual-corrections.json" in files:
            previous_bundle = json.loads(files["static/factual-corrections.json"])
    project_bundle(repo, store, contract, outcome, previous_bundle=previous_bundle, publication_at=now)


def release_daily(store, contract, archive, revision, config, checkpoint):
    if not contract["publication"]["enabled"]:
        return {"published": False, "reason": "INITIAL_CUTOVER_NOT_ENABLED"}
    require(config.get("vercel"), "Vercel project configuration missing")
    adapter = VercelAdapter(store, **config["vercel"])
    require(adapter.production_paths_controlled(), "Close competing production paths before activating daily publication")
    previous = recover_publication(store, adapter)
    latest = store.read("heads/latest-run.json")
    require(latest is not None, "Collection receipt missing")
    already = store.read(f"releases/{previous['releaseId']}.json")
    if already and already["manifest"].get("collectionReceiptSha256") == latest["receipt"]["sha256"] and already["manifest"]["appRevision"] == revision:
        return {"published": False, "reason": "EXACT_COLLECTION_AND_CODE_ALREADY_ACKNOWLEDGED", "releaseId": previous["releaseId"]}
    preflight_corrections(Path(__file__).resolve().parents[3], store, contract, latest.get("runId"),
                          already["manifest"] if already else None, utcnow())
    authority = GitHubAuthority()
    day = datetime.now(timezone.utc).date().isoformat()
    with store.lock("daily-release-controller"):
        prior = store.read(f"heads/gate-budget-{day}.json")
        count = (prior or {}).get("attempts", 0)
        require(count < contract["publication"]["maxBatchesPerDay"], "DAILY_GATE_BUDGET_EXHAUSTED")
        store.compare_and_swap(f"gate-budget-{day}", prior, {"attempts": count + 1})
        # Persist the reservation remotely before dispatch. A killed ephemeral
        # runner must not refund its gate attempt on the next archive restore.
        checkpoint()
        run_id, artifact_id = dispatch_gate(store, archive, revision, authority)
        inputs, receipt = import_gate(store, authority, run_id, artifact_id, archive)
        manifest = prepare_release(contract, inputs["coverage"], inputs["snapshot"], revision, inputs["artifact"], receipt, previous, utcnow(), authority)
        head = publish(store, contract, manifest, adapter, checkpoint=checkpoint)
        checkpoint()
        return {"published": True, **head, "githubRunId": run_id}
