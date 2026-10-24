# Inventory-only qualification origins

Status: dormant implementation unit under the scoped source-qualification transition specification. Root confirmed the preceding promotion before implementation started. No source activation, collection, model work, state migration or deployment is part of this unit.

## Boundary

Implement a new `source_qualification_origin.py`, one focused operational test module and the minimum `retained_audit.py` branches needed to carry a separately typed inventory predecessor. Normal run/task/attempt origins, the 188-origin legacy registry, semantic replay, current transport checks, audit cursors and D112 intake rules remain unchanged.

A diagnostic origin never pretends to be a normal run. It may add literal observed source/URL inventory and retain original date-hint provenance. It cannot supply a reviewed document, accepted/held semantic disposition, fresh timestamp, model result, audit cursor or intake success. Historical failures and partial observations retain their URLs, without acquiring registration or success authority.

## Immutable historical replay dependency

`onboarding.py` remains owned by its existing operator. The agreed pure entry point is `replay_bounded_candidate_diagnostic(original_contract, store, run_record_reference, raw_plan_reference)`, returning the independently validated `plan` and `report`. It authenticates the supplied immutable raw-plan reference under the original full contract, validates the original schema-2 plan and independently replays the stored bounded diagnostic. It also validates the actual diagnostic wrapper and zero-credit metadata. The existing current-execution entry point continues requiring equality with the committed plan file.

Do not temporarily replace the live plan file, patch `Path`, copy a verified source declaration, or add a permissive historical flag in the origin resolver. Authentic partial bounded diagnostics must be replayable for inventory even when they cannot establish registration readiness. The main qualification record must prove all three complete consecutive traversals and successful source-bound samples at its original time.

The new helper parses each exact immutable whole walk once per store and process. It records every immutable reference read by that replay and rechecks all raw hashes and lengths on reuse. Cached parsed output is copied, and cannot bypass a later detected byte change. It performs no object-archive or source-history directory scan; the finite trusted authority list bounds the diagnostic lookup work.

## Trusted external authority

Internal envelope and body replay cannot authenticate an Actions run or authorize registration. `ACTIVATION_AUTHORITIES` is a fixed source-controlled positive registry in the new helper. It is empty in this unit. Consequently no archive-authored transition, ready flag or rehashed diagnostic can activate an origin. Adding an eventual exact authority row requires the actual complete main qualification and root's independently authenticated external run, artifact and archive evidence to be reviewed and retained first.

Each authority row has exactly `activatedContractSha256`, immutable `transition` reference, immutable `originalContract` reference, `mainDiagnostic` and `mainPlan` references, and a canonically ordered `diagnostics` array. Each listed diagnostic binds its exact immutable `record` and `originalContract` references, `rawPlanSha256`, `canonicalPlanSha256`, `githubRunId`, integer `githubRunAttempt`, `appRevision`, `externalReceiptSha256`, `artifactSha256`, `archiveCommit` and `archiveManifestSha256`. Those external evidence pins record the trusted code review boundary; the pure historical API makes no separate claim to have contacted or authenticated GitHub. Replay matches the actual retained run/app/contract/plan bytes against that exact trusted row, with no network fallback.

Every earlier inventory diagnostic must be listed by exact record hash too. The finite listed records supply discovery hints for required earlier partial walks and source-scoped HTML pages. Every selected entry then independently replays its original full proof. Unlisted matching metadata grants no authority and cannot silently extend the eligible evidence set. Omission of a listed earlier retained page fails even when source and transition hashes are recomputed. The metadata pointer selecting the transition remains lookup only because its exact referenced transition and resulting whole-contract hash must match the fixed trusted authority row.

## Closed data shapes

Each future activated source has one `qualificationOrigin` object with exactly:

```
schemaVersion: 1
kind: "bounded_html_qualification"
originalContract: exact immutable reference
diagnostic: exact immutable ci/source-probe-runs record reference
plan: exact immutable raw-plan object reference
sourceResultIndex: integer 0, 1 or 2 in the fixed Ping/Delinea/Sonatype order
sourceResultSha256: canonical hash of the selected original source result
originalSourceSha256: canonical hash of its actual original candidate declaration
proposedAdapterSha256: canonical hash from the actual original-policy adapter helper
activationBaseSha256: canonical hash of that adapter with only registration changed to verified
inventoryManifest: exact immutable object reference
```

The resolver derives the candidate adapter from the independently replayed plan's exact selected index and mode, reconstructs it with the existing adapter helper, and checks every stated hash. It permits only the fixed source-specific parser revision 1 or revision 2 binding tuple. An absent historical revision remains revision 1. A V2 main origin can retain earlier V1 partial inventory under the same original candidate declaration; each old result still replays using its exact original revision. No old parser failure or incomplete flag is reinterpreted through the newer parser. Removing only `qualificationOrigin` from the current source must exactly reproduce the derived activation base. Every original source, supplier, family, host, alias, bound and mode remains under its original full policy. No future global policy hash appears in the source's origin object, avoiding a hash cycle.

The flat inventory manifest has exactly `schemaVersion=1`, `kind=qualification_inventory_manifest`, `sourceId` and `entries`. Each entry is either:

- `kind=bounded_candidate_result`, with exact `originalContract`, `diagnostic`, `plan`, `sourceResultIndex` and `sourceResultSha256` fields. This independently replays a main or earlier partial bounded diagnostic under its original policy.
- `kind=explicit_qualification_page`, with exact `originalContract` and an existing complete `qualification_observation` proof. This retains literal card URLs from earlier schema-1 page diagnostics, including pages which disappeared before the eventual full walk. Existing original-plan/row/charge/body/time checks remain mandatory. Existing historical D112 descriptors, where present, retain their exact original-policy guard; they do not authorize a substantive source change.

Schema-1 explicit diagnostics asserted retained HTML, format and canonical structure. They contain no original card-parser result or revision. After fully replaying their original candidate/policy/row/body/time/charge proof, derive their card inventory through the exact approved main qualification adapter, restricted to that source's closed V1/V2 mode family. Retain its adapter hash with the original page proof and original fetch time. This derives new inventory from retained raw bytes without replacing any prior card result or date claim. In contrast, a bounded V1 report already contains an asserted parser/error/inventory snapshot: always replay and preserve it under its original V1 semantics, even when the main qualification uses V2.

Require unique, canonically ordered entry hashes. The main complete bounded result must appear exactly once. Every entry must bind the same exact original candidate source/adapter context, belong no later than the main qualification time, and contain no nested inventory manifest or chain of qualification origins. Derive URL inventory and original page/date-hint provenance from body replay; no authored URL list or copied ready flag is authority.

The external closed transition descriptor is an immutable object referenced by `source-qualification-transitions/<activated-whole-contract-sha>.json`. That metadata pointer is lookup only. The descriptor has exactly `schemaVersion=1`, `kind=three_html_source_qualification`, `originalContract`, `activatedContractSha256` and three ordered `changes`. Each change binds `sourceId`, exact original source-array index, original source hash, derived proposed adapter hash, derived activation-base hash and qualification-origin hash. The only forward transformation replaces those three exact original candidate rows with the independently derived activation bases plus their exact origin objects. Every other whole-contract byte value/order/type remains canonically equal, including version and all supplier records. The inverse must reconstruct the authenticated original whole contract exactly. Unknown transition kinds, fourth edits, reorderings, missing fields and JSON type drift reject.

This first closed transition deliberately changes no enclosing version or allowance. If integration needs another global-field change, root must add its exact scope to the reviewed transition rather than silently widening this validator. The descriptor is outside the contract it names, so its resulting contract hash is non-circular.

## Retained audit integration

Expose a typed predecessor shaped as `kind=qualification_inventory`, `sourceId`, `qualificationOrigin` and `transition` reference. It contains no run/task/attempt identifier.

1. `AuditIndex.predecessors` asks the new helper for the active source's typed predecessor only when `qualificationOrigin` is present. The default returns an empty list and performs no qualification lookup. Existing normal predecessors remain unchanged.
2. `predecessor_inventory` dispatches that exact kind to the new inventory resolver and unions its body-derived URLs with normal predecessor inventories. Deduplicate the qualification origin canonically while preserving existing normal run/attempt duplicate checks.
3. Independent `verify_receipt` requires the current source's typed predecessor explicitly, checks its original completion time causally against the new attempt start, and includes its full union in the existing full-inventory equality. Diagnostic origins are excluded from the normal self-attempt check because they have no attempt ID. They remain rejected by ordinary semantic `resolve_origin`.

The existing engine already obtains predecessor inventories on both complete and failed discovery paths, so this requires no engine changes. New source URLs remain pending/unknown until ordinary selection and genuine review resolve them. The qualification inventory never enters the semantic proof index or audit history. Later current intake failures do not erase historical inventory and cannot gain intake success from it.

## Acceptance

Use fictional stores and transport in the VM. Positive bookkeeping fixtures may substitute a fictional complete terminal proof at the collaborator boundary; they must not be reported as actual Delinea terminal evidence. Current actual Delinea terminal is unproved and must remain unable to activate this origin. Independently exercise real historical replay on partial records and reject incomplete main activation.

Cover exact forward/inverse transformation, all three mandatory rows, original contract and raw-plan references, source/adapter/base/origin hashes, wrong source/slot, record/body/observation/charge/date tampering, immutable replay after the live plan is replaced, full-partition inventory union, earlier partial/sparse-page rollover, duplicate or omitted manifest references, extra authored URLs, JSON Boolean/integer drift, future/self origin times, missing transition and no typed-origin authority for semantics/intake/cursors. Prove source-without-origin behavior unchanged and all old inventory pairs survive the union.

Keep all 9,914 old source/URL pairs, 24 reviewed bindings, four original ordinary facts, 32 queue entries and four older quarantines distinct in later real activation evidence. This inactive unit creates none of the missing actual qualification evidence and authorizes no fresh request. The legacy registry and all six correction admissions/rows/dates remain untouched. Root owns any later exact activation patch, external transition record, disabled operational plan, correction stamp and actual collection.

The focused tests label their fictional collaborator completion evidence explicitly and patch only the fixed authority registry in those fixtures. Separate tests exercise the actual immutable replay API and existing exact schema-1 row/plan/charge/body/time checks. The actual partial Delinea fixture replays as inventory but still fails the main activation readiness check after the live plan is replaced. A synthetic 9,914-URL ordinary inventory proves union retention mechanically; it is not a new count or replay claim about an authenticated production archive. No complete actual three-source qualification or trusted activation row exists at this unit's boundary.
