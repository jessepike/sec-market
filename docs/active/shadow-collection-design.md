# Human-Verified Shadow Collection Design

## Control

- **Design ID:** `SEC-MARKET-SHADOW-001`
- **Version:** `0.1`
- **Lifecycle state:** `superseded candidate — failed Gate S0 review`
- **Superseded by:** `shadow-collection-design-v0.2.md`
- **Governing Intent:** `SEC-MARKET-001` v1.0
- **Eligibility authority:** `SEC-MARKET-RUN-VAL-002`
- **Owner selection:** “design of a human-verified shadow collection process”
- **Authorization boundary:** design only; no implementation, execution, scheduling, or publication

## Purpose

Reduce the repetitive work of collecting and normalizing public market evidence without allowing automation to silently create facts, change the evidence basis, publish claims, or authorize market posture.

Shadow mode means:

> The system may discover, retrieve, preserve, extract, compare, and propose. Only a human may verify, promote, interpret, freeze, publish, or change posture.

## Outcome

A human reviewer receives a bounded queue of candidate financial facts and source changes that:

- preserve the original public document and its identity;
- separate observed facts from transformations and interpretation;
- expose failures, omissions, and definition changes;
- compare the candidate against the last accepted record;
- provide an independent verification result; and
- require an explicit promotion decision.

The process succeeds when it reduces collection burden while making evidence mistakes easier—not harder—to see.

## First bounded scope

### Entities

Use the fixed Episode 002 prospective cohorts:

- **Infrastructure suppliers:** NVIDIA, Cisco, Arista, Dell, Vertiv
- **Hyperscalers:** Microsoft, Amazon, Alphabet, Meta, Oracle
- **Cybersecurity vendors:** Palo Alto Networks, CrowdStrike, Fortinet, Zscaler, Check Point, Okta

### Sources

Allowlisted public sources only:

- SEC EDGAR filings and furnished exhibits;
- issuer investor-relations releases and presentations;
- official earnings transcripts when available; and
- approved secondary transcripts only as clearly labeled context, never as the sole source for a promoted numerical fact.

### Metrics

Start with the fixed Episode 002 metric map:

- NVIDIA Data Center revenue
- Cisco Networking product revenue
- Arista total revenue
- Dell Servers and Networking revenue
- Vertiv organic net sales
- Microsoft cash additions to PP&E
- Amazon gross purchases of PP&E
- Alphabet purchases of PP&E
- Meta gross purchases of PP&E excluding finance-lease principal
- Oracle TTM GAAP capex at each quarter end
- GAAP total revenue for the six fixed security vendors

Company-disclosed acquisition contributions, metric definitions, orders, backlog, ARR, RPO, cRPO, billings, and guidance may be captured as secondary facts. They remain unpooled and require separate definitions.

### Pilot sequence

1. Replay the accepted Episode 002 source set as a known-answer corpus.
2. Process the next complete reporting event for the fixed cohorts.
3. Process a second complete reporting event using the same contracts.
4. Evaluate whether shadow mode deserves continued use, correction, or retirement.

The sequence is event-based. It does not create a calendar deployment commitment.

## Explicitly out of scope

- market posture or domain recommendations;
- causal or lag inference;
- narrative generation for clients or leadership;
- external publishing, newsletters, dashboards, or alerts;
- confidential ePlus, account, client, CRM, or pipeline data;
- investment recommendations;
- vendor selection or procurement;
- autonomous source enrollment;
- silent metric substitution;
- a production database, scheduler, or unattended service; and
- any enforcement or gating of business decisions.

## Authority model

| Actor | May do | May not do |
|---|---|---|
| Project owner | authorize design, pilot, promotion rules, or retirement | delegate final posture implicitly |
| Collector | discover and retrieve allowlisted documents | invent a missing source or treat failure as no change |
| Extractor | propose candidate facts and locators | promote or interpret them |
| Deterministic validator | run schema, arithmetic, identity, and consistency checks | declare a claim true |
| Independent verifier | re-fetch or inspect the original source and verdict the candidate | reuse the extractor’s unverified summary as evidence |
| Market analyst | adjudicate meaning after facts are verified | silently rewrite the frozen evidence basis |
| Promotion authority | explicitly promote, reject, supersede, or defer each candidate | bulk-approve an unseen queue |

The extractor and independent verifier must be separate agent executions or separate human passes. Builder self-check is not independent verification.

## End-to-end flow

### 0. Register source

A human approves:

- entity;
- canonical source family;
- expected document type;
- expected reporting event;
- allowed retrieval method;
- fixed metric definitions; and
- known comparability risks.

No source enters automatically because it was mentioned in an article or model response.

### 1. Detect reporting event

The collector proposes that an allowlisted event exists.

Required output:

- entity;
- source URL;
- document title;
- filing or release type;
- publication timestamp;
- economic period end; and
- discovery method.

### 2. Preserve raw source

Where lawful and technically available, preserve the original bytes.

Record:

- retrieval timestamp;
- HTTP status and final URL;
- content type;
- byte length;
- SHA-256 hash;
- storage reference;
- SEC accession number or issuer document identifier;
- redirect chain; and
- retrieval limitations.

If raw preservation is unavailable, preserve the exact excerpt and disclose the limitation. Provenance and hashes establish origin and integrity—not correctness.

### 3. Establish document identity

The same economic event may appear as an 8-K exhibit, 10-Q, IR HTML page, PDF, or transcript.

Create one event identity using:

- entity;
- economic period end;
- document family;
- accession or issuer identifier; and
- publication timestamp.

Repeated mirrors resolve to the canonical source. They do not create multiple independent signals.

### 4. Extract candidate facts

Each fact is atomic:

- one entity;
- one economic period;
- one metric;
- one value;
- one unit and currency;
- one definition;
- one source locator; and
- one exact excerpt or table coordinate.

The extractor records the method, model or parser version, and any transformation. A calculated quarter derived from YTD values must retain every input and the formula.

### 5. Run deterministic validation

Validation checks structure and internal consistency. It does not establish truth.

Required checks:

- source URL, source hash, period end, locator, and metric definition present;
- no missing value converted to zero;
- period end used instead of fiscal-quarter label as the join key;
- units and currency explicit;
- arithmetic and YTD-to-quarter derivations reproduce;
- duplicate event and duplicate fact detection;
- rerun idempotency;
- current metric definition matches the registered definition;
- acquisition and restatement flags present when material;
- reported and organic values not collapsed;
- stock metrics and flow metrics distinguished;
- source publication precedes the episode freeze; and
- impossible or extreme changes route to review rather than auto-correction.

### 6. Independent source verification

The verifier:

1. retrieves or opens the raw source independently;
2. locates the cited table cell or exact excerpt;
3. confirms document identity and period;
4. checks value, units, signs, and definition;
5. checks transformations and acquisition treatment;
6. compares against prior accepted facts; and
7. issues a verdict.

Verdicts:

- `VERIFIED`
- `FIX_REQUIRED`
- `SOURCE_UNAVAILABLE`
- `DEFINITION_CHANGED`
- `DUPLICATE_ORIGIN`
- `OUT_OF_SCOPE`
- `INSUFFICIENT_CONTEXT`

An unavailable source cannot receive `VERIFIED`.

### 7. Produce shadow comparison

For every candidate, show:

- prior accepted value;
- proposed value;
- absolute and percentage change;
- prior and current definitions;
- source and period identity;
- extraction and verification verdicts;
- acquisition, restatement, or presentation changes;
- missing peers or expected documents; and
- whether the candidate changes only data or may change interpretation.

The comparison must render on real candidate data. A human-readable view is part of validation because schema checks do not expose every semantic error.

### 8. Human adjudication

The reviewer explicitly chooses:

- `PROMOTE`
- `REJECT`
- `DEFER`
- `SUPERSEDE`
- `REQUEST_RESEARCH`

Promotion requires:

- `VERIFIED`;
- all required deterministic checks passed;
- source and exact locator visible;
- definition and period confirmed;
- no unresolved conflict; and
- reviewer identity and timestamp.

### 9. Promote to accepted evidence

Promotion writes a new immutable evidence record. It never updates the prior record in place.

The promotion record includes:

- candidate fact ID;
- prior fact ID if superseding;
- verification record ID;
- promotion authority;
- decision timestamp;
- promotion rationale;
- target evidence version; and
- resulting packet hash.

Promotion does not change market posture automatically. A separate analysis and authorization step is required.

### 10. Close run

Every run ends with a manifest:

- expected sources;
- retrieved sources;
- failed or missing sources;
- candidate count;
- verified, rejected, deferred, and promoted counts;
- definition changes;
- unresolved conflicts;
- hashes of run artifacts; and
- human sign-off.

A run with missing expected sources cannot present “no material change.” It presents incomplete coverage.

## State machines

### Source state

`REGISTERED → EXPECTED → DISCOVERED → FETCHED`

Exception states:

- `FETCH_FAILED`
- `AUTH_OR_ACCESS_BLOCKED`
- `CONTENT_CHANGED`
- `SOURCE_RETIRED`
- `UNEXPECTED_DOCUMENT`

### Candidate fact state

`EXTRACTED → VALIDATION_PASSED → VERIFICATION_REQUIRED → VERIFIED → HUMAN_REVIEW → PROMOTED`

Alternative terminal states:

- `VALIDATION_FAILED`
- `FIX_REQUIRED`
- `REJECTED`
- `DEFERRED`
- `OUT_OF_SCOPE`
- `SUPERSEDED`

No automated transition enters `PROMOTED`.

## Data contracts

### Source registry

```text
source_id
entity_id
source_family
canonical_base_url
document_type
allowed_retrieval_method
expected_event
metric_ids[]
definition_version
comparability_notes
approved_by
approved_at
state
```

### Raw artifact

```text
artifact_id
source_id
event_id
requested_url
final_url
accession_or_document_id
published_at
period_end
retrieved_at
http_status
content_type
byte_length
sha256
storage_ref
capture_limitation
```

### Candidate fact

```text
candidate_fact_id
artifact_id
entity_id
layer
metric_id
metric_definition_version
period_end
published_at
value
unit
currency
reported_or_adjusted
acquisition_flag
restatement_flag
exact_excerpt
source_locator
transformation
input_fact_ids[]
extractor_id
extractor_version
extracted_at
state
```

### Verification record

```text
verification_id
candidate_fact_id
verifier_id
verified_against_artifact_id
document_identity_match
period_match
locator_match
value_match
unit_match
definition_match
transformation_reproduced
conflict_notes
verdict
verified_at
```

### Promotion record

```text
promotion_id
candidate_fact_id
verification_id
prior_fact_id
disposition
reviewer_id
rationale
target_evidence_version
promoted_at
resulting_packet_hash
```

### Run manifest

```text
run_id
started_at
closed_at
registry_version
expected_source_ids[]
retrieved_source_ids[]
failed_source_ids[]
candidate_fact_ids[]
verification_ids[]
promotion_ids[]
coverage_state
artifact_hashes[]
human_signoff
```

## Failure behavior

| Failure | Required behavior |
|---|---|
| Source unavailable | visible blocked state; no reuse of stale value as current |
| Document changed at same URL | preserve new hash as new artifact; do not overwrite prior bytes |
| Metric definition changed | quarantine candidate; require registry/version decision |
| Acquisition changes comparability | require disclosed bridge or quarantine from primary comparable series |
| Duplicate report or syndication | resolve to one original event |
| Extractor and source disagree | source wins; candidate becomes `FIX_REQUIRED` |
| Validator passes but verifier fails | verifier blocks promotion |
| Missing expected company report | coverage marked incomplete |
| Human does not review | candidate remains in shadow indefinitely |
| Run interrupted | manifest remains open; no “complete” output |

## Review surface

The minimum human review view presents one candidate at a time:

1. entity, metric, period, value, and units;
2. exact source excerpt or table crop;
3. canonical source link and hash;
4. previous accepted value and definition;
5. deterministic check results;
6. independent-verifier verdict;
7. detected conflicts or changes;
8. proposed disposition; and
9. explicit human action.

Bulk review may filter and sort. It may not bulk-promote without opening every candidate included in the action.

## Pilot gates

### Gate S0 — Design acceptance

Pass when:

- scope and authority are explicit;
- schemas and state machines are sufficient for a builder;
- failure visibility is designed;
- human promotion cannot be bypassed; and
- independent architecture and governance reviews pass.

### Gate S1 — Replay authorization

Requires a separate owner decision and an implementation specification.

Replay the Episode 002 accepted corpus. The implementation must reproduce:

- source identity;
- raw or excerpt hashes;
- period alignment;
- fixed metric values;
- acquisition and definition flags;
- known collection gaps; and
- the same promoted-versus-context distinctions.

### Gate S2 — First live shadow event

Run only after replay passes. No fact promotes automatically.

### Gate S3 — Second live shadow event

Use the same registry, schemas, and controls. Definition changes must be versioned rather than patched around.

### Gate S4 — Continue, correct, or retire

Independent review recommends:

- continue shadow mode;
- correct and repeat;
- narrow scope; or
- retire the mechanism.

Production or unattended operation requires a new owner decision and new governing controls.

## Acceptance criteria

The pilot passes only when:

- every candidate has canonical source identity, period, locator, and definition;
- every promoted fact is independently verified;
- every failed retrieval and expected-source omission is visible;
- repeated runs are idempotent;
- no metric definition changes silently;
- no missing value becomes zero;
- no duplicate report counts as independent evidence;
- every transformation reproduces;
- the review surface exposes differences a schema-only check misses;
- zero facts promote without explicit human action;
- no posture or publication changes automatically; and
- two consecutive live shadow events complete without unresolved high-severity provenance or promotion defects.

## Promotion and demotion

Shadow mode may be considered for a broader scope only after two consecutive live events pass.

Immediate demotion triggers:

- any silent source omission;
- any fabricated or mismatched citation;
- any unreviewed promotion;
- any wrong period, sign, unit, or definition in a promoted fact;
- any metric substitution without a registry version;
- any confidential data entering the system; or
- any automated posture or publication action.

Demotion returns the process to replay or retirement. It does not merely lower a score.

## Open implementation choices

These do not block design acceptance:

- raw-artifact storage location;
- local versus cloud execution;
- review interface format;
- parser and model choices;
- scheduling mechanism after pilot authorization; and
- canonical structured storage technology.

Each choice must preserve the contracts and gates above. Technology selection does not redefine the process.

## Not authorized by this design

This document does not authorize implementation.

The next decision is whether to:

- accept the design;
- request revision; or
- authorize a bounded replay implementation specification.

