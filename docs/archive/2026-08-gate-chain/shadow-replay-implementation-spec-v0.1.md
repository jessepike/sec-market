# Gate S1 Shadow Replay — Implementation Specification

## Control

- **Specification ID:** `SEC-MARKET-SHADOW-S1-SPEC-001`
- **Version:** `0.1`
- **Lifecycle state:** `superseded candidate — failed independent review`
- **Superseded by:** `shadow-replay-implementation-spec-v0.2.md`
- **Design authority:** `SEC-MARKET-SHADOW-001` v0.2
- **Replay corpus:** `SEC-MARKET-SHADOW-CORPUS-001` v0.1
- **Design manifest:** `SEC-MARKET-SHADOW-MAN-001`
- **Owner authorization:** “go”
- **Authorization boundary:** specification only; no implementation, replay, live collection, or package installation

## Objective

Specify the smallest deterministic implementation that can replay the seven-row known-answer corpus and prove the human-authority, provenance, missingness, idempotency, and append-only controls in the accepted shadow design.

The implementation is a local replay instrument, not a production pipeline.

## Hard blockers before implementation or replay

The owner must assign:

```text
human_verifier_id = PENDING
promotion_authority_id = PENDING
```

The identities must be different humans.

The implementation must refuse initialization, verification, promotion, and closure when:

- either identity is empty;
- the identities are equal; or
- the active actor cannot prove the role claimed by the command.

No names are inferred by this specification.

## Runtime decision

### Language and standard library

- Python 3.12 or later
- Python standard library only for Gate S1
- `sqlite3`, `urllib`, `html.parser`, `hashlib`, `json`, `decimal`, `datetime`, `pathlib`, `argparse`, and `unittest`

No package installation is required.

### Execution environment

All commands run in the OrbStack `dev` VM:

```text
orb run -m dev <command>
```

Nothing installs on the host Mac.

### Storage

Local replay state:

```text
.shadow/
  replay.db
  actors.json
  artifacts/sha256/<first-two>/<full-hash>
  runs/<run-id>/
    review-queue.md
    run-manifest.json
```

`.shadow/` is gitignored.

Version-controlled configuration:

```text
config/shadow/
  source-registry-v0.1.json
  metric-definitions-v0.1.json
  replay-corpus-v0.1.json
  validator-rules-v0.1.json
```

No raw source bytes or human identity configuration are committed.

## Repository layout

```text
src/secmarket_shadow/
  __init__.py
  __main__.py
  cli.py
  config.py
  identity.py
  retrieval.py
  artifacts.py
  extract/
    __init__.py
    sec_html.py
    ir_html.py
  validation.py
  checker.py
  review_queue.py
  human_verification.py
  adjudication.py
  evidence_store.py
  runs.py
  replay.py
  schema.sql

tests/
  shadow/
    fixtures/
    test_corpus_hash.py
    test_identity.py
    test_retrieval.py
    test_extraction.py
    test_validation.py
    test_checker_independence.py
    test_actor_separation.py
    test_review_interaction.py
    test_promotion_transaction.py
    test_idempotency.py
    test_missingness.py
    test_replay.py
```

## Machine-readable corpus

`config/shadow/replay-corpus-v0.1.json` is generated manually from the accepted Markdown corpus and committed.

It must contain:

- corpus ID and version;
- canonical oracle-manifest hash;
- definition-set hash;
- replay cutoff;
- seven gold records;
- permitted nondeterminism; and
- expected counts and terminal states.

At startup, canonical serialization must reproduce:

```text
ca454cab21338d8569da835724a4183d64045cf6b63bd8acfb6d6c1af6de1755
```

Definition-set serialization must reproduce:

```text
0d46af448ade5d9c2dafa0ca2588d9924d591536894e5e500f88dc7e3ec6f9e4
```

Mismatch aborts S1 before network retrieval.

## Source registry

One registered row per gold entity:

```text
entity_id
publisher_id
metric_definition_id
event_type
document_type
source_family
canonical_url
accession_or_issuer_document_id
published_at
period_end
adapter
locator
expected_value
unit
currency
expected_action
expected_terminal_state
capture_limitation
```

Adapters:

- `sec_html`
- `ir_html`

No secondary transcript adapter exists in S1.

## HTTP retrieval

### General

- follow redirects;
- record requested and final URL;
- record redirect chain;
- record status, content type, length, and retrieval timestamp;
- write raw bytes to the content-addressed artifact store before parsing;
- compute SHA-256 over exact bytes; and
- never overwrite an existing artifact.

### SEC

Require environment variables:

```text
SEC_USER_AGENT_NAME
SEC_USER_AGENT_EMAIL
```

Build the descriptive SEC User-Agent from those fields. Refuse SEC retrieval when either is absent.

Throttle all SEC hosts to remain below the SEC limit. Gate S1 may fetch each canonical source once plus one independent checker retrieval.

### Issuer IR

Use a descriptive non-browser User-Agent naming the project and a contact email supplied through environment configuration.

One retry is allowed. A second failure records `SOURCE_MISSING`; it does not reuse a previous artifact as current.

## Identity and idempotency

Implement the accepted design keys exactly.

### Reporting event

```text
entity_id + period_end + event_type
```

### Document origin

```text
publisher_id + entity_id + origin_id + document_type + published_at
```

### Artifact

```text
sha256(raw_bytes)
```

### Candidate fingerprint

```text
entity_id + metric_definition_id + period_end +
normalized_value + unit + currency
```

For S1, normalized values are the exact corpus literals:

```text
75246
35802
54208
44924
1386
2047.9
765
```

### Replay execution

```text
corpus_id + corpus_version + corpus_manifest_hash +
registry_version + definition_set_hash + extractor_version +
checker_version + validator_ruleset_hash + target_shadow_version
```

A repeated replay with identical inputs creates no second semantic record or promotion.

## Database schema

SQLite implements the accepted contracts as append-oriented tables:

- `reporting_events`
- `document_origins`
- `origin_relations`
- `retrieval_attempts`
- `raw_artifacts`
- `source_registry`
- `metric_definitions`
- `expected_observations`
- `extraction_attempts`
- `candidate_facts`
- `candidate_attempt_links`
- `acquisition_adjustments`
- `validation_records`
- `agent_checks`
- `review_interactions`
- `human_verifications`
- `adjudications`
- `accepted_evidence`
- `supersession_records`
- `shadow_evidence_versions`
- `shadow_evidence_members`
- `runs`
- `slice_cycles`
- `state_transitions`
- `invalidations`

### Required database constraints

- unique semantic keys from the design;
- foreign keys enabled;
- append-only triggers rejecting `UPDATE` and `DELETE` for artifacts, candidates, validations, checks, verifications, adjudications, accepted evidence, supersessions, and frozen versions;
- role checks on verification and adjudication;
- verifier/promoter identity inequality;
- required review-interaction timestamps before adjudication;
- one of prior-fact-view or no-prior acknowledgement;
- no accepted evidence without `VERIFIED`;
- one active adjudication per candidate, verification, disposition, authority, and target version;
- atomic promotion transaction; and
- no frozen version containing unverified evidence.

Secure deletion for a confidentiality incident applies to quarantined raw bytes only and appends an invalidation record. It does not delete audit metadata.

## Extractor implementation

### SEC HTML adapter

Use `html.parser` to produce:

- normalized document text;
- ordered table rows and cells; and
- document-native table labels.

Locate the registered row label, period column, and value. Emit one extraction attempt.

### IR HTML adapter

Use a separate parser configuration for issuer pages, but the same atomic candidate contract.

### Transformations

S1 permits no YTD subtraction, currency conversion, fiscal-quarter remapping, acquisition adjustment, or inference.

Only:

- strip currency symbols and thousands separators;
- interpret parentheses as presentation signs only when the registered metric is a cash outflow; and
- normalize to the corpus unit.

Every normalization step is recorded.

## Deterministic validator

Ruleset v0.1 checks:

- corpus, definition-set, and registry hashes;
- event, origin, period, metric, value, unit, currency, locator, and limitation present;
- source publication at or before replay cutoff;
- expected observation exists;
- exactly one candidate fingerprint per expected primary;
- no secondary candidate;
- value and normalized literal match the gold record;
- definition hash matches;
- no missing value represented as zero;
- no unexpected transformation;
- no duplicate origin treated as independent evidence;
- extractor and checker execution IDs differ; and
- rerun semantic counts remain unchanged.

Output is an immutable `ValidationRecord`.

## Independent automated checker

Run as a separate process with a separate execution ID.

It performs a new retrieval or reads a Collector-preserved artifact that predates extraction.

The checker uses an independent method:

- normalize visible text;
- search for the registered label and value tokens;
- verify the origin metadata and period; and
- compare the normalized literal.

It emits only:

- `CHECK_PASSED`
- `CHECK_FAILED`
- `INCONCLUSIVE`

It cannot write `HumanVerification`.

## Human review workflow

### Actor configuration

`.shadow/actors.json`:

```json
{
  "human_verifier_id": "PENDING",
  "promotion_authority_id": "PENDING"
}
```

This file is not committed.

### Review queue

Generate:

```text
.shadow/runs/<run-id>/review-queue.md
```

One section per candidate displays:

- candidate and prior value;
- source URL and content hash;
- exact excerpt and locator;
- metric definition and period;
- validation and checker results;
- expected-observation state;
- review-interaction state; and
- allowed actions with no preselected default.

### Verification command

Proposed command:

```text
orb run -m dev python -m secmarket_shadow verify \
  --run <run-id> \
  --candidate <candidate-id> \
  --actor <human-verifier-id> \
  --verdict VERIFIED
```

The command:

- refuses non-human actor type;
- refuses the promotion-authority identity;
- requires source-view and check-view acknowledgements;
- records fresh retrieval or independent-artifact basis; and
- appends `HumanVerification`.

### Adjudication command

```text
orb run -m dev python -m secmarket_shadow adjudicate \
  --run <run-id> \
  --candidate <candidate-id> \
  --actor <promotion-authority-id> \
  --action PROMOTE \
  --ack-source-viewed \
  --ack-no-prior-fact
```

The command:

- refuses the verifier identity;
- requires a prior human `VERIFIED`;
- requires candidate-specific review interaction;
- rejects blind bulk invocation;
- writes one atomic promotion transaction; and
- never changes market posture or Episode 002.

## Run commands

All commands are manual.

```text
orb run -m dev python -m secmarket_shadow init \
  --corpus config/shadow/replay-corpus-v0.1.json

orb run -m dev python -m secmarket_shadow replay-create \
  --as-of 2026-08-15T19:17:24-07:00

orb run -m dev python -m secmarket_shadow fetch --run <run-id>
orb run -m dev python -m secmarket_shadow extract --run <run-id>
orb run -m dev python -m secmarket_shadow validate --run <run-id>
orb run -m dev python -m secmarket_shadow check --run <run-id>
orb run -m dev python -m secmarket_shadow review-queue --run <run-id>
```

Human verification and adjudication follow for each of seven candidates.

```text
orb run -m dev python -m secmarket_shadow close-run --run <run-id>
orb run -m dev python -m secmarket_shadow replay-assert --run <run-id>
```

No command runs on a schedule.

## Replay assertions

Gate S1 requires:

- exactly seven reporting events;
- exactly seven expected observations, all `REPORTED`;
- exactly seven canonical candidates;
- zero secondary candidates;
- seven human `VERIFIED` records;
- seven separate human `PROMOTE` adjudications;
- seven accepted-evidence records;
- one frozen shadow evidence version;
- manifest and definition-set hashes match;
- all gold values, periods, origins, locators, units, and limitations match;
- no open, deferred, rejected, quarantined, or missing required item;
- `CLOSED_COMPLETE` run and slice cycle with human sign-off;
- a second identical replay produces no new semantic records or promotions; and
- no Episode, posture, publication, or external system changes.

## Required negative tests

1. Empty actor IDs block initialization.
2. Same verifier and promoter ID blocks initialization.
3. Agent actor cannot issue `VERIFIED`.
4. Verifier cannot adjudicate.
5. Promoter cannot verify.
6. Promotion without candidate-specific source-view record fails.
7. Promotion without prior-fact view or no-prior acknowledgement fails.
8. Missing source closes incomplete.
9. Retrieved source with omitted metric becomes `NOT_DISCLOSED`.
10. Changed definition becomes `QUARANTINED`.
11. Duplicate mirror does not create a second candidate.
12. Byte-only page drift does not create a second semantic candidate.
13. Changed value creates a replacement candidate.
14. Validator failure cannot promote.
15. Checker failure still requires human verdict and cannot auto-promote.
16. Second promotion of identical semantic fact fails.
17. Update or delete of immutable records fails.
18. Unreviewed verified item blocks complete closure.
19. Confidential-data quarantine blocks verification and promotion.
20. Any secondary fact causes S1 failure.

## Implementation sequence

1. Add Python package skeleton, `.gitignore` entry, and standard-library test runner.
2. Encode corpus, registry, definitions, and validator rules; verify hashes.
3. Implement SQLite schema, constraints, state transitions, and append-only triggers.
4. Implement identity and content-addressed artifact storage.
5. Implement SEC and IR retrieval with one-retry behavior.
6. Implement the two extraction adapters.
7. Implement deterministic validation.
8. Implement separate checker process.
9. Implement Markdown review queue.
10. Implement human verification and adjudication commands.
11. Implement atomic promotion, supersession edges, evidence freezing, and closure.
12. Implement replay assertions and all negative tests.
13. Run independent architecture, security, and operator review.

## Build exit conditions

An implementation is ready for an authorized S1 replay only when:

- all unit and negative tests pass inside the OrbStack dev VM;
- corpus and definition hashes reproduce;
- the two human identities are assigned and distinct;
- a second reader can execute the manual command sequence;
- no command schedules or runs unattended;
- independent review has no unresolved high-severity defect; and
- the owner separately authorizes the replay run.

## Not authorized

This specification does not authorize:

- creating the files or installing tooling described above;
- fetching any source;
- running the replay;
- assigning invented human identities;
- starting S2 or S3;
- adding a scheduler or service;
- promoting market evidence outside the local shadow store;
- changing posture; or
- publishing output.

The next decision is whether to accept this specification and then separately authorize implementation.

