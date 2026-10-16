# Human-Verified Shadow Collection Design v0.2

## Control

- **Design ID:** `SEC-MARKET-SHADOW-001`
- **Version:** `0.2`
- **Lifecycle state:** `accepted — Gate S0 passed`
- **Supersedes:** [shadow-collection-design.md](shadow-collection-design-v0.1.md) v0.1 candidate
- **Governing Intent:** `SEC-MARKET-001` v1.0
- **Eligibility authority:** `SEC-MARKET-RUN-VAL-002`
- **Replay corpus:** `SEC-MARKET-SHADOW-CORPUS-001` v0.1
- **Authorization boundary:** design only; no implementation, replay, live run, scheduler, database, or publication
- **Independent review:** architecture, governance, and operator reviews passed 2026-08-15

## Purpose

Reduce repetitive public-evidence collection without allowing automation to create accepted facts, silently omit expected evidence, change market posture, or publish claims.

> Automated components may retrieve, preserve, extract, validate, compare, and propose. Only an identified human may verify. A different identified human must adjudicate promotion.

## First pilot scope

The first pilot uses seven primary facts only:

- NVIDIA Data Center revenue
- Microsoft cash additions to PP&E
- Amazon gross purchases of PP&E
- Alphabet purchases of PP&E
- CrowdStrike GAAP total revenue
- Fortinet GAAP total revenue
- Okta GAAP total revenue

The exact known-answer rows are in `shadow-replay-corpus-v0.1.md`.

### Secondary facts

Secondary facts are excluded from Gates S1–S3.

Orders, backlog, ARR, RPO, cRPO, billings, guidance, surveys, incidents, regulation, acquisitions, and transcripts may not create candidates. Acquisition and definition changes may appear only as blocking metadata needed to determine whether a primary candidate is comparable.

### Expansion

The remaining Episode 002 cohorts may be proposed only after Gate S4. Expansion requires a new corpus and owner authorization.

## Work units

### Reporting run

One run covers:

```text
one issuer
× one economic period_end
× one allowlisted primary document family
× one registered primary metric
```

### Pilot cycle

One pilot cycle contains one terminal reporting run for each of the seven pilot entities.

A cycle closes:

- `CLOSED_COMPLETE` when all seven expected observations have terminal human dispositions and no required item remains open; or
- `CLOSED_INCOMPLETE` when a human signs off with every missing, failed, deferred, or quarantined item listed.

Incomplete cycles do not pass Gates S2 or S3.

## Manual trigger boundary

Gates S1–S3 are manually triggered.

No scheduler, watcher, recurring service, autonomous source enrollment, or unattended execution is authorized. Any such mechanism requires a separate post-pilot owner decision and new controls.

## Roles and structural authority

| Role | Actor requirement | Authority |
|---|---|---|
| Collector | agent or human | retrieve allowlisted source; no candidate promotion |
| Extractor | agent execution | emit candidate facts |
| Automated checker | separate agent execution or deterministic code | emit `CHECK_PASSED`, `CHECK_FAILED`, or `INCONCLUSIVE` only |
| Human verifier | `actor_type=HUMAN`; different identity from extractor execution and promotion authority | issue `VERIFIED`, `FIX_REQUIRED`, or other verification verdict |
| Human promotion authority | `actor_type=HUMAN`; different identity from human verifier | `PROMOTE`, `REJECT`, `DEFER`, `SUPERSEDE`, or `REQUEST_RESEARCH` |
| Owner | human | authorize design, replay implementation, expansion, retirement, or later production consideration |

### Non-bypassable invariants

- An automated actor cannot issue `VERIFIED`.
- A human verification must record the source-view interaction and a fresh retrieval or independently preserved artifact.
- Extractor execution ID must differ from automated-check execution ID.
- Human verifier ID must differ from the extractor operator identity when the extractor is human-assisted.
- Human verifier ID must differ from promotion-authority ID.
- A promotion cannot exist without a prior human `VERIFIED` record.
- A run cannot close without human sign-off.
- No automated transition enters `PROMOTED`, `SUPERSEDED`, `FROZEN`, `CLOSED_COMPLETE`, or `CLOSED_INCOMPLETE`.

S1 is blocked until the owner assigns named `human_verifier_id` and `promotion_authority_id` values that are different identities.

## Identity model

### Reporting event

Economic event:

```text
reporting_event_key =
entity_id + economic_period_end + event_type
```

### Document origin

Publisher-issued document:

```text
document_origin_key =
publisher_id + entity_id + accession_or_issuer_document_id + document_type + published_at
```

Enums:

```text
event_type = quarterly_results | annual_results
document_type = ir_release | sec_exhibit | 10-q | 10-k
source_family = sec_filing | issuer_ir | official_transcript
```

For S1–S3, `publisher_id := entity_id`.

Relations:

- `mirror_of`
- `amends`
- `restates`
- `supersedes`
- `supports_event`

### Retrieval attempt

One attempt to retrieve one origin:

```text
attempt_id
document_origin_key
requested_url
final_url
redirect_chain[]
attempted_at
http_status
content_type
byte_length
failure_reason
```

### Raw artifact

Immutable retrieved content:

```text
artifact_key = sha256(raw_bytes)
```

Record storage reference and capture limitation. A later change at the same URL creates a new artifact.

## Source registry and precedence

Gate S1 seeds its registry from the seven corpus rows.

Canonical numerical precedence:

1. SEC filing or furnished exhibit
2. issuer IR release or PDF
3. official issuer transcript

The secondary-transcript allowlist is empty for S1–S3.

The source registry is persistent configuration. Run-specific expected-source occurrences are separate records and do not mutate registry state.

S2 and S3 use each entity’s pinned document family from the corpus. A run starts on the first document of that family published after the stated cutoff, not on the first document of any family.

## Metric definitions

Each metric definition is immutable and versioned:

```text
metric_definition_id
entity_id
metric_id
name
formula
unit
currency
flow_or_stock
reported_or_adjusted
source_precedence
effective_from
effective_to
predecessor_definition_id
definition_hash
adjustment_policy
```

`definition_hash` covers reusable metric semantics, not entity registration or effective dates:

```text
definition_hash =
SHA256(UTF8(name + "|" + flow_or_stock + "|" + currency + "|" + reported_or_adjusted))
```

This intentionally gives CrowdStrike, Fortinet, and Okta the same hash for the same GAAP total-revenue semantics while retaining separate entity-scoped metric IDs and effective dates.

```text
definition_set_hash =
SHA256(newline_terminated_join(sort(metric_definition_id + ":" + definition_hash)))
```

The S1 definition-set hash is `0d46af448ade5d9c2dafa0ca2588d9924d591536894e5e500f88dc7e3ec6f9e4`.

Definition change requires an owner decision:

- `VERSION`
- `REJECT_CHANGE`
- `RETIRE_METRIC`

No extractor, checker, verifier, or reviewer may silently substitute a metric.

## Expected observations

Every run begins with one expected observation:

```text
expected_observation_key =
run_id + entity_id + metric_definition_id + period_end
```

States:

- `PENDING`
- `REPORTED`
- `NOT_DISCLOSED`
- `NOT_APPLICABLE`
- `SOURCE_MISSING`
- `QUARANTINED`

A retrieved report that omits the metric becomes `NOT_DISCLOSED`; it does not disappear from the queue.

Coverage derives from expected observations, not candidate count.

| Event | Expected-observation transition |
|---|---|
| run created | none → `PENDING` |
| pinned source and metric found | `PENDING` → `REPORTED` |
| pinned source found, metric absent | `PENDING` → `NOT_DISCLOSED` |
| pinned source fails after retry | `PENDING` → `SOURCE_MISSING` |
| metric does not apply to event | `PENDING` → `NOT_APPLICABLE` |
| definition or acquisition comparability blocks use | `PENDING` or `REPORTED` → `QUARANTINED` |

## Extraction attempts

Attempts preserve execution history without duplicating semantic candidates:

```text
extraction_attempt_id
semantic_candidate_key
artifact_key
extractor_execution_id
extractor_version
attempted_value
unit
currency
excerpt
locator
attempted_at
attempt_result
```

```text
extraction_attempt_key =
semantic_candidate_key + artifact_key + extractor_execution_id + attempt_number
```

## Candidate facts

Atomic contract:

```text
candidate_fact_id
semantic_candidate_key
semantic_fact_fingerprint
replaces_candidate_id
reporting_event_key
document_origin_key
supporting_artifact_keys[]
extraction_attempt_ids[]
entity_id
layer: supplier | hyperscaler | security
metric_definition_id
period_end
published_at
value
unit
currency
exact_excerpt
document_native_locator
transformation
input_fact_ids[]
acquisition_adjustment_id
created_at
state
```

```text
semantic_candidate_key =
entity_id + metric_definition_id + period_end + document_origin_key

semantic_fact_fingerprint =
entity_id + metric_definition_id + period_end + normalized_value + unit + currency
```

For S1, `normalized_value` is exactly the corpus manifest literal with no thousands separator:

```text
75246 | 35802 | 54208 | 44924 | 1386 | 2047.9 | 765
```

`unit=millions` and `currency=USD`. Implementations must use canonical decimal serialization with no trailing zero added to integer literals.

Byte-only drift appends an extraction attempt and supporting artifact; it does not create another candidate when the semantic fact fingerprint is unchanged. A changed value or definition creates a new candidate linked through `replaces_candidate_id`.

Candidate identity precedence:

- `semantic_candidate_key` groups extraction attempts for one origin;
- `semantic_fact_fingerprint` is the origin-independent canonical candidate identity; and
- a mirrored origin attaches an attempt and `DUPLICATE_ORIGIN` relation to the existing candidate rather than minting another candidate.

## Acquisition adjustment

```text
acquisition_adjustment_id
candidate_fact_id
reporting_event_key
document_origin_key
artifact_key
contribution_value
denominator
unit
currency
growth_effect_percentage_points
formula
bridge_observations[]
source_locator
threshold_result
comparability_state: comparable | quarantined | restored
```

`bridge_observations[]` are non-candidate blocking metadata. Each contains source origin, artifact, period, value, unit, currency, locator, and role in the formula. They cannot be promoted as facts in S1–S3.

Quarantine when:

- acquired contribution is at least 5 percent of the metric; or
- growth changes by at least 2 percentage points.

Restore comparability only with a company-disclosed bridge or a full comparable YoY base.

## Validation records

Every deterministic check is recorded:

```text
validation_record_key =
candidate_fact_id + validator_version + ruleset_hash

validation_record_id
candidate_fact_id
validator_version
ruleset_hash
checks[]
overall_result
validated_at
```

Required checks:

- source, artifact hash, period, metric definition, locator, value, unit, and currency present;
- no missing value represented as zero;
- period end—not fiscal label—is the join key;
- arithmetic and transformations reproduce;
- duplicate origins and candidates detected;
- metric definition unchanged;
- acquisition thresholds applied;
- source publication meets the run `as_of`;
- no automated correction at any severity; and
- rerun semantic keys produce no duplicate records.

Replay uses:

```text
published_at <= 2026-08-15T19:17:24-07:00
```

Live runs use:

```text
published_at <= run.as_of
```

`run.as_of` is entered by the operator and frozen when the run enters `CREATED`. Amendments published after `as_of` belong to a later run.

## Automated check

The separate checker independently retrieves the canonical origin or reads an artifact captured by the Collector before and separately from the Extractor execution. The same extractor-produced artifact cannot be the sole check basis.

It may emit only:

- `CHECK_PASSED`
- `CHECK_FAILED`
- `INCONCLUSIVE`

```text
agent_check_key =
candidate_fact_id + checker_version + checked_artifact_key
```

An automated check cannot satisfy human verification.

## Human source verification

Required record:

```text
human_verification_id
candidate_fact_id
verifier_actor_type = HUMAN
verifier_id
verification_basis_type: fresh_retrieval | independently_preserved_artifact
fresh_retrieval_attempt_id
independently_preserved_artifact_key
review_interaction_id
document_identity_match
period_match
locator_match
value_match
unit_match
definition_match
transformation_reproduced
prior_fact_compared
conflict_notes
verdict
verified_at
```

Verdicts:

- `VERIFIED`
- `FIX_REQUIRED`
- `SOURCE_UNAVAILABLE`
- `DEFINITION_CHANGED`
- `DUPLICATE_ORIGIN`
- `OUT_OF_SCOPE`
- `INSUFFICIENT_CONTEXT`

Only a human may issue these verdicts.

Exactly one verification basis reference is required:

- `fresh_retrieval` requires `fresh_retrieval_attempt_id`; or
- `independently_preserved_artifact` requires an artifact captured by the Collector before and separately from the Extractor.

## Review interactions

Per candidate:

```text
review_interaction_id
candidate_fact_id
human_actor_id
opened_at
source_viewed_at
prior_fact_id
prior_fact_viewed_at
no_prior_fact_acknowledged_at
checks_viewed_at
closed_at
```

Promotion is rejected unless:

- the promotion authority opened the candidate;
- the source and check results were viewed;
- exactly one of `prior_fact_id + prior_fact_viewed_at` or `no_prior_fact_acknowledged_at` is present;
- the interaction closed after the views; and
- the interaction belongs to that candidate.

This makes blind bulk promotion detectable and structurally invalid.

## Candidate transition table

| Current state | Actor / event | Next state |
|---|---|---|
| none | Extractor emits valid atomic attempt | `EXTRACTED` |
| `EXTRACTED` | deterministic validation fails | `VALIDATION_FAILED` |
| `EXTRACTED` | deterministic validation passes | `VALIDATION_PASSED` |
| `VALIDATION_FAILED` | operator requests repair | `RETURNED_TO_EXTRACTOR` |
| `VALIDATION_FAILED` | operator rejects invalid attempt | `REJECTED_VALIDATION` |
| `VALIDATION_PASSED` | automated checker starts | `CHECK_REQUIRED` |
| `CHECK_REQUIRED` | `CHECK_PASSED` | `HUMAN_VERIFICATION_REQUIRED` |
| `CHECK_REQUIRED` | `CHECK_FAILED` | `HUMAN_VERIFICATION_REQUIRED` with conflict |
| `CHECK_REQUIRED` | `INCONCLUSIVE` | `HUMAN_VERIFICATION_REQUIRED` with limitation |
| `HUMAN_VERIFICATION_REQUIRED` | human `VERIFIED` | `VERIFIED_AWAITING_ADJUDICATION` |
| `HUMAN_VERIFICATION_REQUIRED` | human `FIX_REQUIRED` | `FIX_REQUIRED` |
| `HUMAN_VERIFICATION_REQUIRED` | human `SOURCE_UNAVAILABLE` | `SOURCE_UNAVAILABLE` |
| `HUMAN_VERIFICATION_REQUIRED` | human `DEFINITION_CHANGED` | `DEFINITION_CHANGED` |
| `HUMAN_VERIFICATION_REQUIRED` | human duplicate/out-of-scope/context verdict | matching verdict state |
| `VERIFIED_AWAITING_ADJUDICATION` | promotion authority acts | `PROMOTED`, `PROMOTED_WITH_SUPERSESSION`, `REJECTED`, or `DEFERRED` |
| `RETURNED_TO_EXTRACTOR` | Extractor emits replacement | old remains immutable; new candidate starts `EXTRACTED` |
| `RETURNED_TO_RESEARCH` | Collector or Extractor completes a named research task | replacement candidate starts `EXTRACTED`, or item becomes `DEFERRED` / `REJECTED` |

An in-run repair may still reach `CLOSED_COMPLETE` when the replacement candidate completes verification and adjudication before sign-off and the original candidate is terminal. Open returned items force `CLOSED_INCOMPLETE`.

## Decision table

| Human verification verdict | Allowed promotion-authority actions | Resulting candidate state | May run close? |
|---|---|---|---|
| `VERIFIED` | `PROMOTE`, `SUPERSEDE`, `REJECT`, `DEFER` | `PROMOTED`, `PROMOTED_WITH_SUPERSESSION`, `REJECTED`, `DEFERRED` | Only after action |
| `FIX_REQUIRED` | `REQUEST_RESEARCH`, `REJECT` | `RETURNED_TO_EXTRACTOR`, `REJECTED` | Incomplete if returned |
| `SOURCE_UNAVAILABLE` | `DEFER`, `REJECT` | `DEFERRED`, `REJECTED` | Incomplete |
| `DEFINITION_CHANGED` | owner: `VERSION`, `REJECT_CHANGE`, `RETIRE_METRIC` | `QUARANTINED`, `REJECTED`, `METRIC_RETIRED` | Incomplete unless terminal owner decision |
| `DUPLICATE_ORIGIN` | `REJECT` | `REJECTED_DUPLICATE` | Yes |
| `OUT_OF_SCOPE` | `REJECT` | `REJECTED_OUT_OF_SCOPE` | Yes |
| `INSUFFICIENT_CONTEXT` | `REQUEST_RESEARCH`, `DEFER`, `REJECT` | `RETURNED_TO_RESEARCH`, `DEFERRED`, `REJECTED` | Incomplete if open |

Rules:

- `FIX_REQUIRED` creates a new candidate linked through `replaces_candidate_id`; the old candidate remains immutable.
- `SUPERSEDE` applies only to correction of the same entity + metric + period and requires an existing accepted record.
- A new period uses `PROMOTE`, not `SUPERSEDE`.
- `PROMOTE_CONTEXT` does not exist in S1–S3 because secondary facts are excluded.
- `REQUEST_RESEARCH` assigns a named Collector or Extractor task with a return condition. It does not authorize external or secondary sources outside the registry.
- A `Yes` close result for `DUPLICATE_ORIGIN` or `OUT_OF_SCOPE` applies only to non-required candidates; a required primary observation still follows the stricter incomplete-coverage rule.

## Adjudication records

All human dispositions use:

```text
adjudication_key =
candidate_fact_id + human_verification_id + promotion_authority_id + disposition + target_shadow_evidence_version

adjudication_id
candidate_fact_id
human_verification_id
promotion_authority_id
review_interaction_id
disposition
target_shadow_evidence_version
supersedes_adjudication_id
rationale
decided_at
```

Reject, defer, and research requests do not populate promotion fields.

## Accepted shadow evidence

Promotion creates an immutable shadow record:

```text
accepted_evidence_key =
semantic_fact_fingerprint + document_origin_key

accepted_evidence_id
candidate_snapshot
artifact_key
human_verification_id
adjudication_id
prior_accepted_evidence_id
accepted_at
record_hash
```

Storage must be append-only or write-once with content hashing. Technology choice is open; immutability is not.

Promotion writes only to the shadow evidence store. Later shadow versions reference the same accepted-evidence ID rather than re-promoting an unchanged semantic fact. It does not change Episode 001, Episode 002, a market posture, or a published evidence packet.

### Supersession record

Prior accepted evidence is never mutated.

```text
supersession_record_id
prior_accepted_evidence_id
new_accepted_evidence_id
adjudication_id
reason
created_at
record_hash
```

The evidence-version manifest derives which record is current from appended supersession edges.

## Shadow evidence versions

```text
shadow_evidence_version
parent_version
state: DRAFT | FROZEN
accepted_evidence_ids[]
manifest_hash
human_freezer_id
frozen_at
```

Only a human may freeze. A freeze cannot contain an unverified promoted fact.

## Atomic promotion transaction

One transaction must:

1. validate human verification and review-interaction invariants;
2. create the adjudication;
3. create the accepted evidence record;
4. append a supersession record when applicable without mutating prior evidence;
5. add the record to the draft shadow evidence version; and
6. write audit hashes.

Failure rolls back all six steps. Other dispositions never create accepted evidence.

## Idempotency

| Stage | Semantic uniqueness |
|---|---|
| Reporting event | entity + period end + event type |
| Document origin | publisher + entity + accession/document ID + document type + publication time |
| Artifact | SHA-256 content hash |
| Expected observation | run + entity + metric definition + period |
| Extraction attempt | semantic candidate key + artifact + extractor execution + attempt number |
| Candidate | semantic fact fingerprint; multiple attempts may support one candidate |
| Validation | candidate + validator version + ruleset hash |
| Agent check | candidate + checker version + checked artifact |
| Human verification | candidate + verifier + verification-basis reference |
| Adjudication | candidate + human verification + authority + disposition + target shadow version |
| Accepted evidence | semantic fact fingerprint + document origin |

```text
replay_execution_key =
corpus_id + corpus_version + canonical_oracle_manifest_sha256 +
registry_version + definition_set_hash + extractor_version +
checker_version + validator_ruleset_hash + target_shadow_evidence_version
```

A changed human decision appends a new adjudication with `supersedes_adjudication_id`; it does not reuse an arbitrary token or mutate the prior decision.

Rerunning the same corpus with the same registry, definitions, extractor, checker, and validator versions creates no duplicate semantic records and cannot create a second promotion.

## Run state machine

States:

- `CREATED`
- `RUNNING`
- `INTERRUPTED`
- `READY_FOR_SIGNOFF`
- `CLOSED_COMPLETE`
- `CLOSED_INCOMPLETE`
- `ABORTED`

| Current state | Human or system event | Next state |
|---|---|---|
| none | human creates run and freezes `as_of` | `CREATED` |
| `CREATED` | human starts manually | `RUNNING` |
| `RUNNING` | interruption or recoverable technical failure | `INTERRUPTED` |
| `INTERRUPTED` | human resumes from manifest | `RUNNING` |
| `RUNNING` | all expected observations and candidates terminal | `READY_FOR_SIGNOFF` |
| `READY_FOR_SIGNOFF` | human signs complete coverage | `CLOSED_COMPLETE` |
| `READY_FOR_SIGNOFF` | human signs with visible gaps | `CLOSED_INCOMPLETE` |
| any open state | owner stops or confidentiality response requires stop | `ABORTED` |

Rules:

- interrupted runs resume from the open manifest;
- completed candidate records remain immutable;
- one automated retry is permitted for retrieval failure;
- after one failed retry, the expected observation becomes `SOURCE_MISSING`;
- a human may attach a manually retrieved artifact with a capture limitation;
- unexpected documents remain out of registry until owner approval;
- no automated actor closes a run; and
- `CLOSED_COMPLETE` requires `coverage_state=complete`, every expected observation `REPORTED`, every required primary candidate promoted, no open returned item, and human sign-off.
- `SOURCE_MISSING`, `NOT_DISCLOSED`, `NOT_APPLICABLE`, `QUARANTINED`, deferred, or rejected required primary evidence forces human-signed `CLOSED_INCOMPLETE`.

## Slice-cycle contract

```text
slice_cycle_id
corpus_id
run_ids[7]
state: CREATED | RUNNING | READY_FOR_SIGNOFF | CLOSED_COMPLETE | CLOSED_INCOMPLETE | ABORTED
coverage_state: open | complete | incomplete
missing_or_open_item_ids[]
human_signoff_id
started_at
closed_at
```

| Cycle condition | Allowed closure |
|---|---|
| Seven runs `CLOSED_COMPLETE`; seven expected observations promoted; no open item | `CLOSED_COMPLETE` |
| Any `SOURCE_MISSING`, `NOT_DISCLOSED`, `DEFERRED`, `QUARANTINED`, rejected expected primary, or `CLOSED_INCOMPLETE` run | human-signed `CLOSED_INCOMPLETE` |
| Any `RETURNED_TO_EXTRACTOR`, `RETURNED_TO_RESEARCH`, unreviewed `VERIFIED`, or open `FIX_REQUIRED` | cannot close complete |
| Confidentiality incident or owner stop | `ABORTED` or `CLOSED_INCOMPLETE` after incident disposition |

Only a human may close a cycle.

## Run manifest

```text
run_id
slice_cycle_id
as_of
registry_version
definition_versions[]
state
expected_observation_ids[]
retrieval_attempt_ids[]
artifact_ids[]
candidate_fact_ids[]
validation_record_ids[]
agent_check_ids[]
human_verification_ids[]
adjudication_ids[]
accepted_evidence_ids[]
coverage_state: open | complete | incomplete
open_item_ids[]
artifact_hashes[]
human_signoff_id
started_at
closed_at
```

No run may present “no material change” when coverage is incomplete.

## Confidential-data response

If suspected confidential, client, CRM, pipeline, or non-public data is captured:

1. quarantine the artifact and all derived candidates;
2. block verification, promotion, and run closure;
3. restrict access to the owner and designated incident handler;
4. record the incident without reproducing the sensitive content;
5. determine lawful secure deletion or retention requirements;
6. append an invalidation/tombstone record for affected hashes and derived records; securely delete bytes only when the designated incident handler determines it is lawful and required; and
7. demote the process to replay or retire it.

No confidential artifact can enter accepted shadow evidence.

## Pilot operator artifact

Each run produces:

```text
runs/<run_id>/review-queue.md
```

The queue shows allowed dispositions without pre-selecting one:

- candidate and prior value;
- canonical source and content hash;
- exact excerpt and native locator;
- definition and period;
- validation results;
- automated-check result;
- human-verification state;
- conflicts and missing observations; and
- review-interaction status.

The pilot expects seven primary candidates per complete slice cycle. If additional candidates appear, stop and close incomplete until the registry or corpus is explicitly revised.

## Replay gate S1

Replay against `SEC-MARKET-SHADOW-CORPUS-001` v0.1.

Pass requires:

- exactly seven primary expected observations and candidates;
- values, units, periods, origins, locators, and dispositions match the gold rows;
- zero secondary candidates;
- the new raw-artifact hashes are recorded but are not compared with unavailable historical raw hashes;
- every mismatch is visible;
- rerun creates no duplicate semantic record; and
- human verifier and separate promotion authority complete all seven rows.

Any non-permitted difference fails S1.

## First live gate S2

After separate owner authorization and S1 pass:

- wait for each entity’s first document in its corpus-pinned family published after `2026-08-15T19:17:24-07:00`;
- run one issuer-period run for each;
- close the slice cycle only when all seven runs are terminal; and
- require `CLOSED_COMPLETE`, seven terminal primary dispositions, no open `FIX_REQUIRED`, no unseen promotion, and human sign-off.

## Second live gate S3

Repeat the same seven-entity slice for the following reporting event for each entity using unchanged contracts or explicit definition versions.

Pass conditions are identical to S2.

## Gate S4 — continue, correct, narrow, or retire

Independent architecture, evidence, and operator reviews inspect S1–S3.

Possible owner decisions:

- continue the seven-entity shadow slice;
- correct and repeat;
- narrow;
- authorize design of an expanded corpus; or
- retire.

No scheduler, production service, external publication, or automated posture action follows automatically.

## Demotion triggers

The owner monitors:

- silent source omission;
- fabricated or mismatched citation;
- unreviewed or blind promotion;
- wrong period, sign, unit, value, or definition in accepted evidence;
- metric substitution without a definition version;
- confidential data capture;
- automated run closure;
- automated posture or publication; or
- irreproducible transformation.

Any trigger fails the current gate and returns the process to replay, correction, or retirement.

## Gate S0 acceptance

The design passes S0 when independent review confirms:

- the replay corpus is a runnable oracle;
- human verification and separate human promotion cannot be bypassed;
- source, metric, and expected-observation identities are explicit;
- every verdict maps to an operator action and state;
- semantic idempotency is testable;
- promotion is atomic and append-only;
- incomplete coverage is visible;
- confidentiality response is defined;
- S1–S3 are bounded and manually triggered; and
- a builder can write an implementation specification without inventing policy.

## Still open after design

These implementation choices do not change policy:

- local versus cloud runtime;
- raw-artifact storage technology;
- structured shadow-evidence storage technology;
- parser and model choices; and
- implementation language.

They may be selected only in a separately authorized replay implementation specification.

## Not authorized

This design does not authorize implementation.

The next owner decision after S0 is whether to authorize a bounded S1 replay implementation specification.

