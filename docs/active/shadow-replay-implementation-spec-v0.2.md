# Gate S1 Shadow Replay — Implementation Specification v0.2

## Control

- **Specification ID:** `SEC-MARKET-SHADOW-S1-SPEC-001`
- **Version:** `0.2`
- **Lifecycle state:** `accepted — implementation not authorized`
- **Supersedes:** [shadow-replay-implementation-spec.md](../archive/shadow-replay-implementation-spec.md) v0.1 candidate
- **Design:** `SEC-MARKET-SHADOW-001` v0.2
- **Corpus:** `SEC-MARKET-SHADOW-CORPUS-001` v0.1
- **Authorization record:** `D-15`
- **Authorization:** specification only; no build, fetch, replay, live run, or installation
- **Independent review:** architecture, security, and builder/operator reviews passed 2026-08-15

## Objective and slice

Implement only the seven corpus facts. One slice cycle contains seven issuer runs:

```text
S1-<id>/
  nvda-run
  msft-run
  amzn-run
  goog-run
  crwd-run
  ftnt-run
  okta-run
```

Each run is one issuer × one period × one pinned document family × one metric. Secondary facts are forbidden.

## Runtime

- Python 3.12+
- standard library only
- system `ssh-keygen` for human signatures
- all commands in OrbStack:

```text
orb run -m dev env PYTHONPATH=src python -m secmarket_shadow ...
orb run -m dev env PYTHONPATH=src python -m unittest discover -s tests/shadow
```

No host package installation.

## Human-role prerequisite and proof

S1 is blocked until the owner registers two distinct human actor IDs and their SSH public-key fingerprints:

```json
{
  "registry_version": "actors-v0.1",
  "owner": {
    "actor_id": "PENDING",
    "ssh_public_key": "PENDING",
    "fingerprint": "PENDING"
  },
  "human_verifier": {
    "actor_id": "PENDING",
    "ssh_public_key": "PENDING",
    "fingerprint": "PENDING"
  },
  "promotion_authority": {
    "actor_id": "PENDING",
    "ssh_public_key": "PENDING",
    "fingerprint": "PENDING"
  },
  "collector_actor_id": "PENDING",
  "manual_retriever_actor_ids": ["PENDING", "PENDING"],
  "incident_handler_actor_id": "PENDING"
}
```

Store the unsigned object at `.shadow/actors.json`, permission `0600`. Store the detached owner signature at `.shadow/actors.json.sig`; the signature is not included in the bytes it signs.

The owner trust anchor is supplied during the separately authorized implementation step and pinned outside the registry at `config/shadow/owner-trust-anchor-v0.1.txt`. Canonical unsigned registry bytes are:

```python
json.dumps(unsigned_registry, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
```

`init` confirms the pinned fingerprint before trusting the owner key in `actors.json`, then verifies the detached signature over those bytes. Any registry change aborts the cycle.

Human commands use signed canonical attestations:

```text
ssh-keygen -Y sign -f <private-key> -n sec-market-shadow <payload-file>
```

The CLI verifies with `ssh-keygen -Y verify`. `--actor` alone proves nothing. Verifier and promoter actor IDs and fingerprints must both differ.

Actor IDs are stable semantic identities; fingerprints are rotatable credentials. The owner signs the actor-registry hash and attests that verifier and promoter are distinct humans. Key rotation appends a registry version and does not change actor IDs.

Generate `allowed_signers` from the frozen registry:

```text
{actor_id} namespaces="sec-market-shadow" {ssh_public_key}
```

For S1, `incident_handler_actor_id := owner.actor_id`, `collector_actor_id := promotion_authority.actor_id`, and `manual_retriever_actor_ids := [promotion_authority.actor_id, human_verifier.actor_id]`. The promotion authority supplies the first attachment as Collector; the verifier is authorized only for the independent second attachment and may not supply the first.

Tests use synthetic temporary SSH keypairs. They do not satisfy the owner-assignment blocker.

### Canonical attestation bytes

All signed payloads are UTF-8 bytes from:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
```

Every payload includes:

```text
command
actor_id
actor_registry_hash
replay_execution_key
cycle_id
run_id
nonce
issued_at
```

`cycle_id` is JSON `null` only for actor-registry and definition-level commands. `run_id` is JSON `null` for cycle-, version-, and definition-level commands. Candidate/run commands require both. The nullability is part of canonical bytes.

Keys are exactly the snake_case names above. `issued_at` is ISO-8601 with offset. Nonces are persisted in SQLite and unique per actor and command. Command attestations expire 15 minutes after `issued_at`; the detached owner registry signature does not expire and is versioned instead.

Command-specific keys:

- `attach-artifact`: `accession_or_issuer_document_id`, `content_sha256`, `limitation`
- `review-close`: `candidate_id`, `interaction_id`, `artifact_hash`, `validation_ids`, `check_ids`, `source_viewed_at`, `checks_viewed_at`, `prior_fact_viewed_at`, `no_prior_fact_acknowledged_at`
- `verify`: `candidate_id`, `artifact_hash`, `validation_ids`, `check_ids`, `basis_type`, `basis_id`, `verdict`
- `adjudicate`: `candidate_id`, `verification_id`, `interaction_id`, `disposition`, `target_version`, `rationale`, plus action-dependent `prior_accepted_evidence_id`, `prior_adjudication_id`, `assignee_actor_id`, `research_task_id`, and `return_condition`
- `definition-decide`: `metric_definition_id`, `decision`, `replacement_definition_id`, `rationale`
- `run-start` / `run-ready`: `target_id`, `manifest_hash`
- `run-interrupt` / `run-resume`: `target_id`, `reason`, `manifest_hash`
- `close-run`: `coverage`, `expected_observation_ids`, `open_item_ids`, `manifest_hash`
- `close-cycle`: `coverage`, `run_ids`, `open_item_ids`, `manifest_hash`
- `freeze-version`: `version_id`, `accepted_evidence_ids`, `manifest_hash`
- `incident-open`: `incident_id`, `artifact_ids`, `reason`
- `incident-quarantine`: `incident_id`, `artifact_ids`
- `incident-dispose`: `incident_id`, `artifact_ids`, `decision`, `rationale`
- `abort-run` / `abort-cycle`: `target_id`, `reason`, `open_item_ids`, `manifest_hash`

The CLI writes canonical payload bytes to a file. `--attestation` points to the `ssh-keygen -Y sign` signature file. Verification uses:

```text
ssh-keygen -Y verify -f allowed_signers -I {actor_id} -n sec-market-shadow -s {signature_file}
```

The CLI verifies namespace, registered actor ID, key fingerprint, nonce uniqueness, age, replay key, and exact command purpose. Altered or replayed payloads fail.

### Two-phase privileged command workflow

```text
... prepare-attestation --command <command> <command-fields...> --out <payload.json>
ssh-keygen -Y sign -f <private-key> -n sec-market-shadow <payload.json>
... <command> <command-fields...> --payload <payload.json> --attestation <payload.json.sig>
```

The execute command reuses `nonce` and `issued_at` from `payload.json`, recomputes all other expected fields from current state and command arguments, and requires byte equality before signature verification and nonce consumption. It never mints a new nonce or timestamp during execute. `actor_registry_hash` is SHA-256 of the same canonical unsigned registry bytes covered by the detached owner signature.

## Storage and layout

```text
.shadow/                         # gitignored
  actors.json
  actors.json.sig
  replay.db
  artifacts/sha256/<2>/<hash>
  fixtures/sha256/<2>/<hash>
  cycles/<cycle-id>/
    cycle-manifest.json
    <run-id>/review-queue.md

config/shadow/
  owner-trust-anchor-v0.1.txt
  replay-corpus-v0.1.json
  source-registry-v0.1.json
  metric-definitions-v0.1.json
  validator-rules-v0.1.json

src/secmarket_shadow/
tests/shadow/
```

Implementation step zero adds `.shadow/` to `.gitignore` and a test that fails if any path under `.shadow/` is tracked.

## Normative corpus serialization

JSON is a convenience representation.

Oracle hash:

```text
SHA256(UTF8(the exact fourteen newline-terminated G| and D| rows
from shadow-replay-corpus-v0.1.md, in listed order))
```

Definition-set hash:

```text
SHA256(newline_terminated_join(sort(metric_definition_id + ":" + definition_hash)))
```

Do not hash JSON bytes.

Required results:

```text
oracle = ca454cab21338d8569da835724a4183d64045cf6b63bd8acfb6d6c1af6de1755
definitions = 0d46af448ade5d9c2dafa0ca2588d9924d591536894e5e500f88dc7e3ec6f9e4
```

Example gold object:

```json
{
  "gold_id": "G-002",
  "publisher_id": "msft",
  "entity_id": "msft",
  "metric_definition_id": "msft.cash_ppe_additions.v1",
  "definition_hash": "41f0ee6c8f58da822d493c8a20888f504f6e3073c1e82a4262362a6925828fe3",
  "period_end": "2026-06-30",
  "normalized_value": "35802",
  "unit": "millions",
  "currency": "USD",
  "document_type": "ir_release",
  "source_family": "issuer_ir",
  "accession_or_issuer_document_id": "msft-fy2026-q4-release",
  "published_at": "2026-07-29",
  "event_type": "quarterly_results",
  "canonical_url": "https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast",
  "locator": {
    "row_labels": ["Additions to property and equipment"],
    "period_header": "Three Months Ended June 30, 2026",
    "source_unit": "USD millions",
    "sign_rule": "parentheses_are_presentation",
    "scale": "1"
  },
  "capture_limitation": "historical_raw_not_archived",
  "expected_action": "PROMOTE",
  "expected_state": "PROMOTED"
}
```

Top-level JSON contains:

```text
corpus_id
version
canonical_oracle_manifest_sha256
definition_set_sha256
replay_cutoff
expected_counts
golds[]
definitions[]
permitted_nondeterminism[]
```

Definition object example:

```json
{
  "metric_definition_id": "msft.cash_ppe_additions.v1",
  "name": "Cash additions to property and equipment",
  "formula": "cash_flow_line_three_month_period",
  "flow_or_stock": "flow",
  "reported_or_adjusted": "reported",
  "currency": "USD",
  "effective_from": "2023-03-31",
  "definition_hash": "41f0ee6c8f58da822d493c8a20888f504f6e3073c1e82a4262362a6925828fe3"
}
```

Config versions:

```text
registry_version=registry-v0.1
extractor_version=extractor-v0.1
checker_version=checker-v0.1
validator_version=validator-v0.1
validator_ruleset_hash=SHA256(UTF8(json.dumps(rules, sort_keys=True, separators=(',', ':'), ensure_ascii=True)))
target_shadow_evidence_version=shadow-replay-v0.1
```

## Locator recipes

| Gold | Adapter | Visible row labels | Column selector | Source scale | Sign rule | Normalized value |
|---|---|---|---|---|---|---|
| G-001 | `sec_ixbrl_table` | `Data Center` within market-platform revenue table | `Three Months Ended April 26, 2026` | USD millions | literal | `75246` |
| G-002 | `ir_html_table` | `Additions to property and equipment` within consolidated cash-flow statement | `Three Months Ended June 30, 2026` | USD millions | parentheses are presentation, value positive | `35802` |
| G-003 | `ir_html_table` | `Purchases of property and equipment` within consolidated cash-flow statement | `Three Months Ended June 30, 2026` | USD millions | parentheses are presentation, value positive | `54208` |
| G-004 | `sec_ixbrl_table` | `Purchases of property and equipment` within consolidated cash-flow statement | `Three Months Ended June 30, 2026` | USD millions | parentheses are presentation, value positive | `44924` |
| G-005 | `sec_ixbrl_table` | `Total revenue`, `Total revenues` within GAAP statement of operations | `Three Months Ended April 30, 2026` | USD thousands | divide by 1,000 only when visible unit header says thousands; `Decimal` + `ROUND_HALF_UP` | `1386` |
| G-006 | `ir_html_table` | `Total revenue` within financial highlights | `Three Months Ended June 30, 2026` | USD millions | literal | `2047.9` |
| G-007 | `sec_ixbrl_table` | `Total revenue` within financial highlights | `Three Months Ended April 30, 2026` | USD millions | literal | `765` |

SEC parsing ignores hidden `ix:` duplicates and narrative rounded values. It selects visible table cells only.

No other inference, YTD subtraction, currency conversion, or fiscal remapping is permitted.

`locator.period_header` uses the exact visible strings above. Normalize case and punctuation only. The ISO-style date commentary elsewhere is not a match key. Two-row headers must resolve to one combined period. More than one visible matching cell fails extraction; never choose the first match. For G-005, a missing unit header or a header other than thousands or millions fails extraction.

## Retrieval

### Headers

```text
SEC User-Agent: {SEC_USER_AGENT_NAME} {SEC_USER_AGENT_EMAIL}
IR User-Agent: {IR_USER_AGENT_NAME} {IR_USER_AGENT_EMAIL}
```

Refuse retrieval if required fields are missing.

### Network controls

- connect/read timeout: 30 seconds
- maximum redirects: 5
- maximum response size: 25 MiB
- every redirect hop and final host must be one of `www.sec.gov`, `www.microsoft.com`, `ir.aboutamazon.com`, or `investor.fortinet.com`; private, loopback, link-local, and literal-IP destinations fail
- enforce the size cap while streaming decompressed bytes; do not trust `Content-Length`
- SEC throttle: maximum 8 requests/second across all `sec.gov` hosts, tested with a fake clock
- one retry for timeout, connection error, HTTP 429, or HTTP 5xx
- second failure → `SOURCE_MISSING`

Write bytes to a temporary file, fsync, hash, then atomically rename into the content-addressed store.

### Manual attachment

Amazon and Fortinet may block `urllib`. The accepted fallback is:

```text
... attach-artifact \
  --run <run-id> \
  --origin <origin-id> \
  --actor <collector-id> \
  --path <file> \
  --limitation manual_retrieval \
  --attestation <signature>
```

The signed payload binds cycle, run, pinned `accession_or_issuer_document_id`, content SHA-256, limitation, actor-registry hash, and replay-execution key. Wrong origin or invalid signer fails.

Both manual attachments must precede extraction:

1. promotion authority acting as Collector supplies the first signed attachment;
2. human verifier independently supplies a second signed attachment;
3. the two retrieval-attempt IDs and signers must differ;
4. identical content hashes are allowed and expected; and
5. after both valid attachments, `SOURCE_MISSING → PENDING`.

Each attachment creates an immutable `RetrievalAttempt` containing origin, content hash, signer, timestamp, limitation, signature, and capture method. Attachment writes artifacts and attempts only and cannot verify or promote.

Manual-fallback order:

1. Collector signed attachment
2. verifier signed independent attachment
3. extraction uses the Collector artifact
4. independent check and human verification use the verifier artifact
5. human verification

## Fixture strategy

After separate owner authorization for fixture capture and source retrieval, manually capture one artifact per gold source into `.shadow/fixtures/`. Implementation authorization alone is insufficient. Raw fixtures are gitignored.

Commit only:

```text
tests/shadow/fixture-manifest-v0.1.json
```

The manifest contains origin, artifact SHA-256, locator recipe, and expected literal. Unit tests require local bytes matching those hashes. Live network retrieval is not a unit-test gate.

## Identity keys

Implement exact canonical concatenations with `|` separators and UTF-8:

```text
reporting_event = entity_id|period_end|event_type
document_origin = publisher_id|entity_id|accession_or_issuer_document_id|document_type|published_at
expected_observation = run_id|entity_id|metric_definition_id|period_end
semantic_candidate = entity_id|metric_definition_id|period_end|document_origin_key
fact_fingerprint = entity_id|metric_definition_id|period_end|normalized_value|unit|currency
extraction_attempt = semantic_candidate|artifact_hash|extractor_execution_id|attempt_number
validation = candidate_id|validator_version|ruleset_hash
agent_check = candidate_id|checker_version|checked_artifact_hash
human_verification = candidate_id|verifier_actor_id|verification_basis_id
adjudication = candidate_id|verification_id|promotion_authority_actor_id|disposition|target_version
accepted_evidence = fact_fingerprint|document_origin_key
replay_execution = corpus_id|corpus_version|canonical_oracle_manifest_sha256|registry_version|definition_set_hash|extractor_version|checker_version|validator_ruleset_hash|target_shadow_evidence_version
```

IDs are SHA-256 hex of the canonical key.

Mirrors attach attempts and `DUPLICATE_ORIGIN` relations to the origin-independent candidate. Byte-only drift adds an attempt. Changed value creates a replacement candidate with `replaces_candidate_id`.

## Run and cycle commands

From repository root:

```text
... init \
  --corpus config/shadow/replay-corpus-v0.1.json \
  --registry config/shadow/source-registry-v0.1.json \
  --definitions config/shadow/metric-definitions-v0.1.json \
  --rules config/shadow/validator-rules-v0.1.json
```

`init` verifies `ssh-keygen`, all hashes, the signed actor registry, and `.gitignore`.

Create one cycle and seven runs:

```text
... replay-create-cycle \
  --corpus config/shadow/replay-corpus-v0.1.json \
  --as-of 2026-08-15T19:17:24-07:00
```

For S1, `--as-of` must equal the corpus replay cutoff or creation fails.

Output:

```text
cycle_id
run_ids = {cycle_id}-nvda, -msft, -amzn, -goog, -crwd, -ftnt, -okta
```

Then:

```text
... fetch-cycle --cycle <cycle-id>
... # for any manual-fallback run: Collector attach, then verifier attach
... extract-cycle --cycle <cycle-id>
... validate-cycle --cycle <cycle-id>
... check-cycle --cycle <cycle-id>
... review-queue --cycle <cycle-id>
```

Each cycle command enumerates the seven runs; it does not merge them.

A second `replay-create-cycle` with the same replay-execution key returns the existing cycle and writes no semantic record. After the first full replay, execute the same sequence again and assert no semantic count changes.

## Candidate-state preconditions

- `extract` requires expected observation `PENDING`; manual-fallback runs additionally require two distinct signed retrieval-attempt IDs and signers
- `check` requires `VALIDATION_PASSED` / `CHECK_REQUIRED`
- `verify` requires `HUMAN_VERIFICATION_REQUIRED`
- `PROMOTE` or `SUPERSEDE` adjudication requires `VERIFIED_AWAITING_ADJUDICATION`
- `REJECT` is allowed from any terminal human-verdict state except `DEFINITION_CHANGED`, which requires an owner definition decision
- `DEFER` is allowed from `VERIFIED_AWAITING_ADJUDICATION`, `SOURCE_UNAVAILABLE`, or `INSUFFICIENT_CONTEXT`
- `REQUEST_RESEARCH` is allowed from `FIX_REQUIRED` or `INSUFFICIENT_CONTEXT`
- `PROMOTE` additionally requires validation pass, checker result, human verification, and closed review interaction
- run closure requires `READY_FOR_SIGNOFF`, `coverage_state=complete`, expected observation `REPORTED`, promoted primary candidate, and human signature
- cycle closure requires seven signed `CLOSED_COMPLETE` runs

These are enforced in application code and SQLite triggers.

## Review-interaction commands

```text
... review-open --run <run> --candidate <id> --actor <promoter>
... review-view-source --interaction <id> --actor <promoter>
... review-view-checks --interaction <id> --actor <promoter>
... review-ack-no-prior --interaction <id> --actor <promoter>
... review-view-prior --interaction <id> --actor <promoter> --prior-fact <id>
... review-close --interaction <id> --actor <promoter> --attestation <signature>
```

Each command records a distinct timestamp. The signed closed-interaction payload binds candidate, source artifact, check records, and prior/no-prior path.

Exactly one of `review-ack-no-prior` or `review-view-prior` may occur. S1 uses only the no-prior path.

## Human verification

Canonical payload includes candidate, artifact, source locator, validation/check IDs, verification basis, and verdict.

```text
... verify \
  --run <run> --candidate <id> --actor <verifier> \
  --basis fresh_retrieval|independently_preserved_artifact \
  --basis-id <id> \
  --ack-source-viewed --ack-checks-viewed \
  --verdict VERIFIED|FIX_REQUIRED|SOURCE_UNAVAILABLE|DEFINITION_CHANGED|DUPLICATE_ORIGIN|OUT_OF_SCOPE|INSUFFICIENT_CONTEXT \
  --attestation <signature>
```

## Adjudication

```text
... adjudicate \
  --run <run> --candidate <id> --actor <promoter> \
  --interaction <interaction-id> \
  --action PROMOTE|SUPERSEDE|REJECT|DEFER|REQUEST_RESEARCH \
  --target-version shadow-replay-v0.1 \
  --rationale <text> \
  --attestation <signature>
```

Action-dependent fields:

- `SUPERSEDE`: `--prior-accepted-evidence-id` and `--prior-adjudication-id`
- `REQUEST_RESEARCH`: `--assignee-actor-id`, `--return-condition`, and `--research-task-id`
- `DEFER`: `--return-condition`
- every action: non-empty rationale

Definition changes use an owner-signed `definition-decide --action VERSION|REJECT_CHANGE|RETIRE_METRIC`.

## Human-only closure and freeze

```text
... close-run --run <run> --actor <authorized-human> \
  --coverage complete|incomplete --attestation <signature>

... close-cycle --cycle <cycle> --actor <authorized-human> \
  --coverage complete|incomplete --attestation <signature>

... freeze-version --version shadow-replay-v0.1 \
  --actor <promotion-authority> --attestation <signature>

... abort-run --run <run> --actor <owner> --reason <text> --attestation <signature>
... abort-cycle --cycle <cycle> --actor <owner> --reason <text> --attestation <signature>
```

No automated component invokes these commands.

Only the registered promotion authority may sign `close-run`, `close-cycle`, and `freeze-version`. The owner may sign `ABORTED`.

`coverage=complete` requires every required observation `REPORTED`, every primary candidate `PROMOTED`, no open item, and complete manifest hashes.

`coverage=incomplete` requires the signed payload to enumerate every missing, deferred, rejected, quarantined, returned, or open item. It cannot pass Gate S1.

## SQLite requirements

Tables implement every accepted design contract, plus:

- `actors`
- `attestation_nonces`
- `incidents`
- `incident_actions`
- `review_interactions`
- `slice_cycles`

At `init`, actor fingerprints and registry hash are copied into SQLite and frozen for the cycle.

Append-only triggers reject `UPDATE`/`DELETE` for:

- actors and actor-registry versions;
- attestation nonces;
- metric definitions and registry versions;
- origins, origin relations, retrieval and extraction attempts;
- artifacts, candidates, transitions, validations, checks;
- review interactions after close;
- human verifications and adjudications;
- accepted evidence, supersessions, version members, invalidations;
- incidents and incident actions;
- signed run/cycle closures and frozen evidence versions.

## Atomic promotion

Use `sqlite3` explicit transaction control:

```text
BEGIN IMMEDIATE
  validate state and signatures
  insert adjudication
  insert accepted evidence
  append supersession edge when applicable
  add evidence-version membership
  append transition and audit hashes
COMMIT
```

Any exception executes `ROLLBACK`.

Failure-injection tests stop after each numbered step and assert zero partial rows.

## Tamper evidence

SQLite triggers alone are insufficient. Write chained integrity checkpoints after init, retrieval, extraction, validation/check, before human review, and at each human-signed closure:

- hash schema SQL;
- hash actor, registry, corpus, definition, and rules configurations;
- hash ordered append-only table exports;
- hash raw-artifact manifest;
- write checkpoint manifests outside SQLite; sign review-ready and closure checkpoints; and
- set database and closure manifest read-only between invocations.

Direct-file tampering causes the next command to abort.

Every privileged command begins one SQLite transaction that verifies the signature and expiry, inserts the unique `(actor_id, command, nonce)` into append-only `attestation_nonces`, performs the authorized action, and commits. A duplicate nonce or any failure rolls back the action while retaining no partially consumed authorization.

## Confidential-data workflow

S1 uses no probabilistic detector. The negative test injects exact marker:

```text
CONFIDENTIAL_MARK
```

Detection or human report invokes:

```text
... incident-open --run <run> --artifact <hash> --actor <incident-handler> --attestation <signature>
... incident-quarantine --incident <id> --actor <incident-handler> --attestation <signature>
... incident-dispose --incident <id> --decision retain|delete \
  --actor <incident-handler> --attestation <signature>
```

Only the designated incident handler may decide deletion. Prefer encrypted artifact storage and key destruction; otherwise record that filesystem unlink does not guarantee physical SSD erasure. Audit metadata and tombstones remain.

## Expected-observation transitions

- `PENDING → REPORTED` when pinned metric extraction succeeds
- `PENDING → NOT_DISCLOSED` when source exists and locator does not
- `PENDING → SOURCE_MISSING` after failed retry
- first valid manual attachment leaves `SOURCE_MISSING`; the second attachment from the distinct registered manual retriever changes `SOURCE_MISSING → PENDING`
- `PENDING/REPORTED → QUARANTINED` on definition mismatch

## Independent checker process

`check-cycle` launches:

```text
env PYTHONPATH=src python -m secmarket_shadow check-worker ...
```

with a new checker execution ID. It uses a fresh retrieval or, for a manual-fallback candidate, the verifier’s second independently signed attachment. It never uses the Extractor’s sole artifact. It searches the registered label, period, and value tokens independently.

## Schema and config deliverables

The implementation must include:

- full `schema.sql` with every key, enum check, foreign key, trigger, and transaction precondition;
- JSON schemas for all four config files;
- one filled valid object for each config;
- pinned versions and hash algorithms; and
- a generated schema/data dictionary.

Source-registry example:

```json
{
  "registry_version": "registry-v0.1",
  "entity_id": "msft",
  "publisher_id": "msft",
  "metric_definition_id": "msft.cash_ppe_additions.v1",
  "document_type": "ir_release",
  "source_family": "issuer_ir",
  "canonical_url": "https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast",
  "accession_or_issuer_document_id": "msft-fy2026-q4-release",
  "adapter": "ir_html_table",
  "locator": {
    "row_labels": ["Additions to property and equipment"],
    "period_header": "Three Months Ended June 30, 2026",
    "source_unit": "USD millions",
    "sign_rule": "parentheses_are_presentation",
    "scale": "1"
  }
}
```

Validator-rules example:

```json
{
  "ruleset_version": "validator-v0.1",
  "reject_secondary_candidates": true,
  "reject_missing_as_zero": true,
  "require_exact_period_header": true,
  "require_definition_hash": true,
  "max_candidates_per_run": 1
}
```

Fixture tests copy `.shadow/fixtures/sha256/<first-two>/<full-hash>` into the artifact store by hash before extraction. Database invocation sequence is: verify prior checkpoint → `chmod u+w` → open/write transaction → checkpoint → `chmod a-w`.

Unused design tables may be present but empty. S1 happy-path commands do not write acquisition adjustments or supersessions.

## Required tests

In addition to happy-path extraction:

1. corpus and definition hashes reproduce;
2. actor signatures verify and aliases alone fail;
3. verifier/promoter same actor ID or key fails;
4. verify before validation/check fails;
5. adjudicate before human verify fails;
6. identical extractor/checker execution IDs or identical retrieval-attempt IDs fail; identical content SHA-256 is allowed;
7. exactly one verification basis required;
8. review-interaction order and signature required;
9. automated freeze/closure fails;
10. closure without human sign-off fails;
11. missing source and omitted metric close incomplete;
12. definition mismatch quarantines;
13. mirror and byte-drift do not duplicate candidate;
14. changed value creates replacement;
15. immutable-table updates/deletes fail;
16. failure injection at every promotion step fully rolls back;
17. second promotion fails;
18. raw/config/database tamper aborts;
19. confidentiality marker blocks verify/promote/close;
20. only incident handler may dispose;
21. redirect outside allowlist, >5 redirects, timeout, and oversized response fail;
22. SEC global throttle remains ≤8 requests/second;
23. missing SEC or IR User-Agent fields fail closed;
24. retry behavior matches the matrix;
25. `.shadow/` tracked-file check fails when violated;
26. second identical replay creates no semantic records;
27. seven runs and one cycle close complete only after seven promotions.
28. promoter cannot verify and verifier cannot adjudicate;
29. altered, expired, wrong-command, or replayed signed payload fails;
30. prior-fact and no-prior review paths are mutually exclusive;
31. unsigned, wrong-origin, post-extraction, or wrong-actor attachment fails;
32. manual fallback requires an independent second retrieval/attachment basis;
33. required primary rejection forces incomplete closure;
34. any secondary candidate fails S1;
35. actor, incident, and incident-action mutation fails;
36. incomplete closure attestation enumerates every open or missing item.
37. actor-registry self-signature, untrusted owner key, or changed mapping fails;
38. first and second manual attachment use distinct signed retrieval attempts and permitted roles;
39. incident open/quarantine/dispose payloads bind exact artifact and incident IDs;
40. abort-run and abort-cycle require owner signature and reach `ABORTED`;
41. action-dependent adjudication fields and rationale are enforced;
42. same replay execution returns the existing cycle and run IDs.
43. interrupted run resumes from the open manifest without duplicating semantic rows.

## Run-state commands

```text
... run-start --run <run-id> --actor <promotion-authority> --attestation <signature>
... run-interrupt --run <run-id> --reason <text> --actor <promotion-authority> --attestation <signature>
... run-resume --run <run-id> --actor <promotion-authority> --attestation <signature>
... run-ready --run <run-id> --actor <promotion-authority> --attestation <signature>
```

Transitions follow the accepted design: `CREATED → RUNNING → INTERRUPTED → RUNNING → READY_FOR_SIGNOFF → CLOSED_*`, with owner-signed abort available from any open state.

## Implementation sequence and staged exit

1. Add package skeleton, `.gitignore`, owner trust-anchor path, and synthetic test actor support.
2. Encode the four config schemas and exact corpus/definition hashing.
3. Implement SQLite schema, transitions, append-only triggers, nonce table, and tamper checkpoints.
4. Implement identity keys and content-addressed storage.
5. Implement synthetic HTML fixtures sufficient to test parser mechanics without representing the gold corpus.
6. Implement retrieval, locator adapters, validation, checker, human commands, and incident flow.
7. Pass all non-gold synthetic, identity, transaction, state, and bypass tests.
8. Stop. Gold fixture capture requires separate owner authorization.
9. After fixture authorization, capture and hash the seven local fixtures and pass gold extraction tests.
10. Stop. Live replay requires another separate owner authorization.

An implementation may be structurally complete before fixture capture, but it is not replay-ready and cannot satisfy Gate S1 acceptance until the authorized gold fixtures and extraction tests pass.

## Gate S1 acceptance

- Python 3.12 standard-library tests pass in OrbStack;
- local fixture hashes match;
- live retrieval or signed manual attachments cover all seven sources;
- exactly seven runs and candidates;
- two distinct assigned humans sign verification and promotion;
- seven promoted shadow records and one frozen version;
- complete run/cycle coverage;
- idempotent second replay;
- no secondary facts, posture, publication, scheduler, or live S2 work;
- independent architecture, security, and operator review pass; and
- owner separately authorizes the replay run.

## Not authorized

This specification does not authorize implementation, fixture capture, source retrieval, replay, live collection, identity assignment, scheduling, posture changes, or publication.

The next decision is whether to accept this specification and separately authorize implementation.

