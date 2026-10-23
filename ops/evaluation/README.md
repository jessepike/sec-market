# Offline operational scorecard

Run in the OrbStack VM with Python's standard library. No network, credentials, model calls or
archive mutations are required. The evaluator writes a new JSON report and Markdown companion.
It refuses existing output files.

```sh
python3 ops/evaluation/scorecard.py --manifest /path/to/pinned-inputs.json --output /path/to/new-scorecard
python3 -m unittest discover -s ops/evaluation -p 'test_*.py' -v
```

The manifest explicitly fixes evaluation time, application revision and the raw SHA-256 of every
supplied input. Paths are relative to the manifest unless absolute. Hashes are caller-supplied
pins from reviewed evidence; computing a new hash for an untrusted file does not authenticate it.
A changed contract requires matching coverage for that contract. Do not substitute today's working
contract for a historical receipt's policy.

```json
{
  "schemaVersion": 1,
  "evaluatedAt": "2026-10-23T13:00:00Z",
  "appRevision": "7bd94ec77e99462c068f254e134235a894585cbb",
  "inputs": {
    "contract": {"path": "contract.json", "sha256": "<raw file SHA-256>"},
    "coverage": {"path": "raw-collection-coverage.json", "sha256": "<raw file SHA-256>"},
    "gate": {"path": "accepted-main-gate.json", "sha256": "<raw file SHA-256>"},
    "collection": {"path": "actual-scheduled-collection.json", "sha256": "<raw file SHA-256>"},
    "publication": {"path": "actual-publication.json", "sha256": "<raw file SHA-256>"},
    "rollback": {"path": "actual-rollback-restoration.json", "sha256": "<raw file SHA-256>"}
  }
}
```

Only contract and raw coverage are required. The others use the existing receipt shapes under
`docs/active/daily-pipeline/receipts/`. Missing optional evidence remains unmeasured. Supplied
inconsistent evidence causes exit 2 and no scorecard. A valid report can contain failed measures;
its CLI exits 0 because report generation succeeded, not because operations passed.

The raw coverage must include its full task receipts and immutable inventory identities.
The smaller public daily-coverage.json cannot replace it. The manifest coverage byte hash must
match the gate's collectionReceiptSha256 when a gate is supplied. The evaluator recomputes
contract/task identities using the existing offline pipeline contract planner. It does not fetch
or revalidate observation bodies, authenticate GitHub, or establish that a caller-created receipt
is genuine. Keep source/archive verification in the independent release gate.

No overall score is produced. Null means unmeasured, never zero. Receipt-age freshness remains
separate from full-roster freshness. Historical successful coverage counts remain labeled with their
original checkedAt even when an evaluation is run after they expire. One-cycle execution,
publication and rollback evidence cannot establish sustained operation. Precision, recall and value
remain unmeasured until reviewed benchmark/use evidence and explicit denominators exist.

An optional `continuity` pin accepts an explicit audit with `runId`, `appRevision`, `checkedAt`,
`sourceSnapshotSha256`, `publishedSnapshotSha256`, `limitations` and `measures`. Each measure
has a unique `id`, integer `expected` and `retained` counts and boolean `passed`, which must equal
`retained == expected`. Use `review_queue.pending` and
`historical_candidates.retained_or_quarantined` for the known continuity defect. Historical
candidates held under an older policy need durable quarantine/review records; publication of
those candidates is not the expected result. A gate, if supplied, binds the published snapshot
hash. Missing continuity evidence remains unmeasured, independently of successful rollback.

JSON and Markdown also break the full inventory down by failure reason, source family, supplier
and domain. Registered verified bindings, candidate bindings and missing obligations are separate
columns. A supplier in multiple domains contributes to each domain; those subtotals can overlap.
The primary denominator always remains the entire pinned required inventory.
