# Offline operational scorecard

The separate `correction_resolution.py` evaluator measures only remediation of the five fixed
contradictions in the frozen claim audit. Offline invocation keeps all five rows unmeasured.
Measured results require its authenticated production-gather mode, original charged review
attempts, the exact gate and publisher artifacts, Vercel acknowledgement and every static byte.
The [retained October 24 observation](../../docs/active/daily-pipeline/accuracy/current-correction-resolution-observation-2026-10-24.md)
records 5/5 resolved at approximately 04:01 UTC. This is neither current general accuracy nor
reader value. See the [implementation evidence](../../docs/active/daily-pipeline/accuracy/correction-resolution-implementation-evidence-2026-10-24.md)
for the read-only gather command and archive prerequisites.

Run in the OrbStack VM with Python's standard library. No network, credentials, model calls or
archive mutations are required. The evaluator writes a new JSON report and Markdown companion.
It refuses existing output files.

```sh
python3 ops/evaluation/scorecard.py --manifest /path/to/pinned-inputs.json --output /path/to/new-scorecard
python3 -m unittest discover -s ops/ci -p 'test_evaluation.py' -v
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

For the accepted `daily_intake_with_separate_history` policy, the evaluator requires coverage
schema 2 and reports fresh source intake, current-document processing and retained historical
review as separate measures. A checked intake must have complete discovery and observation
references in its raw receipt. Failed intake may retain partial, stale or otherwise ineligible
observations; offline scoring cannot authenticate their freshness. A processing outcome cannot
replace successful-intake proof. Counter consistency is checked, but supplied summaries are not
source-body authentication. Pending or held
processing stays visible beside intake, and historical review backlog stays separate from freshness.
An empty observed document inventory is unmeasured rather than 0/0. The frozen October 23 legacy
report is replayed byte-for-byte by the evaluator test suite.

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

The current pinned operational report is
`docs/active/daily-pipeline/evaluations/2026-10-24/operational-scorecard.md`.
It records 244/557 successful source checks, 48/48 SEC source checks, and the repaired release's
publication and rollback. It retains the original collection time, 00:38:18 UTC, rather than the
later gate's reconciliation time. The fixed older claim audit remains a separate historical
benchmark. Manual collector receipts never create a scheduled-attempt denominator; their identity
and coverage must still match if supplied. Reproduce the current report to a new output prefix:

```sh
python3 ops/evaluation/scorecard.py \
  --manifest docs/active/daily-pipeline/evaluations/2026-10-24/operational-scorecard-inputs.json \
  --output /tmp/smp-operational-scorecard-replay
```

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

An optional `claimAudit` pin accepts the output of `claim_reviews.py` for the same application
revision. It exposes fixed-inventory review coverage and known contradicting records separately
from release-test results. A known contradiction fails its own measure even if every release test
passed. The report must contain verified source/dataset bindings, all three review partitions,
unique records, exact verdict counters and an observation time no later than evaluation. The
scorecard checks that summary's internal consistency; it does not rerun its source-byte verifier
or independently adjudicate its semantic judgments. Precision and recall remain unmeasured.

To reproduce the fixed existing-record binding check after restoring the verified archive:

```sh
python3 ops/evaluation/claim_reviews.py --root . --state /path/to/restored/state \
  --manifest docs/active/daily-pipeline/accuracy/source-bindings-inputs-2026-10-23.json \
  --outputprefix /path/to/new-source-bindings
```

Manifest paths resolve inside the explicit repository root. The tool reads known JSON array
declarations without executing TypeScript, verifies the exact inventory and raw source proofs,
and writes a new JSON/Markdown pair. Original issue corrections, source objects and publication
state remain unchanged. The retained Varonis fixture is the only explicit exception to archived
observation proof and is bound to its earlier receipt and exact known body hash.

After the manual arrays moved into `web/src/data/tracker/originals.json`, the original command
above correctly fails because the historical TypeScript file bytes changed. It does not select
another source format automatically. Reproduce the same historical benchmark through the
explicit, reviewed migration manifest and its raw SHA-256 pin:

```sh
python3 ops/evaluation/claim_reviews.py --root . --state /path/to/restored/state \
  --manifest docs/active/daily-pipeline/accuracy/source-bindings-inputs-2026-10-23.json \
  --source-migration-manifest docs/active/daily-pipeline/accuracy/source-migration-inputs-2026-10-23.json \
  --source-migration-sha256 2824776f6c739161f93a6fe8107a1599eeacaff968ce29e9ad2ea55ee65240a6 \
  --outputprefix /path/to/new-migrated-source-bindings
```

Both migration options are required together. The migration manifest pins the unchanged
historical input manifest, the current original JSON bytes and the factual baseline bytes. The
verifier checks every canonical before-value hash for all 97 original events, 74 suppliers and
273 evidence objects. It compares all 177 benchmark records and all 144 relevant complete
evidence objects exactly with the frozen inventory before replaying the original source proofs.
It never imports or executes the TypeScript application or reads the effective correction view.

In this explicit mode, the old TypeScript `sourceFiles` hashes remain historical metadata
describing the reviewed application. They are not claims about the refactored TypeScript bytes.
The new raw original/baseline pins and exact value comparisons establish the migration binding.
The historical application revision, input manifest, review ledgers, verdicts and retrieval times
stay unchanged. The report labels its migration separately and sets `semanticAdmission: false`.
It audits the frozen historical benchmark only, not current effective facts or correction
admission. Changing a file and generating replacement pins does not authorize new content.

The migration contract and first actual replay are in
`docs/active/daily-pipeline/accuracy/source-migration-spec-2026-10-23.md` and
`docs/active/daily-pipeline/accuracy/source-migration-bindings-2026-10-23.json`.
