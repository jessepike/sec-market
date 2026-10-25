"""Socket-denied exact actual proof and original-admission replay; read/get only."""
import json
import socket
import sys
from pathlib import Path
from unittest.mock import patch

repo = Path("/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022")
out = Path("/var/tmp/smp-q4-retained-build-20261025")
sys.path[:0] = [str(repo / "web/scripts/pipeline"), str(repo / "ops/ci")]
from contracts import digest
from storage import LocalStore
from corrections import _index, group_review_policy, replay_admission
from test_q4_retained_primary_template import ReadOnlyActual
import q4_retained_primary_template as operation

def file_seal(path):
    body = path.read_bytes()
    return {"sha256": digest(body), "bytes": len(body), "mtimeNs": path.stat().st_mtime_ns}
external_paths = [repo / p for p in (
    "contracts/market.json", "contracts/factual-corrections.json",
    "web/src/data/tracker/factualCorrectionPolicy.json",
    "docs/active/daily-pipeline/accuracy/q4-retained-primary-template-descriptor-2026-10-25.json",
    operation.primary.INSPECTION["path"], operation.primary.initial.INSPECTION["path"],
    "docs/active/daily-pipeline/accuracy/q4-primary-qualification-actual-source-review-2026-10-25.json")]
external_seals = {str(path): file_seal(path) for path in external_paths}
store = ReadOnlyActual()
contract = json.loads((repo / "contracts/market.json").read_bytes())
raw = (repo / "docs/active/daily-pipeline/accuracy/q4-retained-primary-template-descriptor-2026-10-25.json").read_bytes()
requests = json.loads((repo / "contracts/factual-corrections.json").read_bytes())
stamp = json.loads((repo / "web/src/data/tracker/factualCorrectionPolicy.json").read_bytes())
with patch.object(socket.socket, "connect", side_effect=AssertionError("NO_NETWORK")), patch.object(
        LocalStore, "__init__", side_effect=AssertionError("NO_FROZEN_LOCALSTORE")):
    protected = {key: store.raw(key) for key in (
        "heads/latest-run.json", "heads/dailySnapshot.json", "heads/production.json",
        "heads/budget-2026-10-25.json", "heads/gate-budget-2026-10-25.json")}
    report = operation.derive_report(contract, store, raw)
    replay = operation.verify_report(contract, store, raw, report)
    admissions = []
    for group in requests["groups"]:
        policy = group_review_policy(group, contract, requests["baseline"]["sha256"])
        assert policy == stamp["reviewPolicySha256ByGroup"][group["id"]]
        ref = store.read(_index(group, policy))["admission"]
        before = store.get(ref)
        replay_admission(group, ref, store, contract, policy, "2026-10-25T12:00:00Z")
        assert store.get(ref) == before
        admissions.append({"groupId": group["id"], "policySha256": policy, "admission": ref})
    snapshot = store.read("heads/dailySnapshot.json")
    assert len(snapshot["reviewQueue"]) == 38 and len(snapshot["factProvenance"]) == 4
    for ref in snapshot["factProvenance"].values(): store.get(ref)
    for key, original in protected.items(): assert store.raw(key) == original
for path, seal in store.touched.items():
    p = Path(path); b = p.read_bytes()
    assert (digest(b), len(b), p.stat().st_mtime_ns) == seal
for path in external_paths: assert file_seal(path) == external_seals[str(path)]
proof = {"externalInputSeals": external_seals, "schemaVersion": 1, "result": "PASS", "sourceRequests": 0, "modelRequests": 0,
         "archiveWrites": 0, "javascriptExecuted": False, "socketsDenied": True,
         "localStoreConstructionDenied": True, "derivedReplay": replay,
         "streams": report["streams"], "retainedSamples": report["retainedSamples"],
         "sixAdmissions": admissions, "preservedHeads": {k: digest(v) for k, v in protected.items()},
         "heldQueueEntries": len(snapshot["reviewQueue"]), "factReferences": snapshot["factProvenance"],
         "sourceValidUntil": snapshot["coverage"]["validUntil"],
         "inputSeals": {p: {"sha256": v[0], "bytes": v[1], "mtimeNs": v[2]} for p, v in store.touched.items()}}
(out / "derived-report.json").write_text(json.dumps(report, indent=2) + "\n")
(out / "actual-readonly-replay.json").write_text(json.dumps(proof, indent=2) + "\n")
print(json.dumps({"result": "PASS", "inputSeals": len(store.touched), "admissions": len(admissions),
                  "queueEntries": len(snapshot["reviewQueue"]), "factReferences": len(snapshot["factProvenance"]),
                  "originalAcceptedSamples": report["originalReportAcceptedSamples"],
                  "derivedProposalComplete": report["proposalEvidenceComplete"]}))
