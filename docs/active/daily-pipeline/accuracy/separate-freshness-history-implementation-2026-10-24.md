# Daily intake and historical review implementation

D-112 authorizes this implementation of the approved separation specification. Existing limits,
registration, the 557 required tasks, correction admissions and publishing rules remain unchanged.

## Machine contract

The market contract becomes `market-daily-v2`, with collection mode
`daily_intake_with_separate_history`. New coverage reports have `schemaVersion: 2` and
`measure: daily_source_intake_v2`. Their existing `successfulTasks`, `requiredTasks`, `gapTaskIds`
and `complete` fields explicitly describe intake only. They also contain `intake` with the same
counts and measure, `processing`, and `historicalReview`. Old combined reports remain schema 1
under their original contracts and definitions.

`processing` contains `complete`, `inventoryDocuments`, `reviewedDocuments`, `pendingDocuments`,
`heldDocuments`, `changedDocuments` and `unknownDateDocuments`. `historicalReview` contains
`complete`, `inventoryDocuments`, `reviewedDocuments`, `pendingDocuments` and `heldDocuments`.
A completed review includes every candidate disposition; held claims remain separately counted.
Unknown dates remain explicit even where a document has previously been reviewed.
`unknownDateDocuments` counts URLs without a usable index scheduling-date hint. Index hints
include sitemap `lastmod` and feed dates; they do not establish independently verified article
publication dates. A known scheduling hint must never be presented as a verified publication date.

Coverage `tasks` and public source rows expose intake outcome and error separately from the raw
receipt's processing outcome, plus both processing and historical summaries. Public source
`outcome` follows the report's intake measure. Raw receipts keep their processing `outcome`;
`retainedAuditVersion: 2` identifies the new replay rules. Full URL partitions and classifications
remain content-addressed evidence in the receipt, not assertions inferred from a count.

The successful intake outcome is `checked`. Required task views and all existing success/gap
aliases use that outcome consistently. Inventory equals reviewed plus pending within each
measure. Processing is complete only with zero pending and zero held documents; historical
review is complete with zero pending documents, including documents whose full review held
claims. Changed and unknown-date classifications are disjoint. They can overlap reviewed or
pending status and therefore must not be added to those status counts.

Actual intake has `evaluated: true, status: collected`. The prospective committed baseline has
`evaluated: false, status: uncollected`, zero of 557 intake checks, no validity deadline, and
unevaluated processing and historical review. It retains the complete prior snapshot and policy
under `supersededPolicy`, with original dates. Its migration receipt is
`separate-freshness-history-baseline-migration-2026-10-24.json`.

## Retained evidence and policy migration

Each retained binding records an exact `policyBridge` between its original contract hash and the
current contract hash, plus an independently derived semantic-context hash. Replay resolves the
actual original plan and contract, the positive legacy registry where required, and every original
candidate/review/disposition at its original check time. Original hashes, effective dates and
observation/review times are preserved.

The compatibility projection includes the complete subject supplier and source, aliases,
categories, source class, scope, hosts, model/input policy and review-rule identity, plus the
remaining policy. It excludes the contract version and collection mode and omits other suppliers
and other source registrations, whose records do not participate in this source's semantic proof.
A subject or semantic-policy mismatch holds; unrelated qualification of another supplier does
not invalidate this source's proof. The original full contract stays independently pinned.

Daily discovery requires real fresh successful transport and complete replay, including latest
failure and equal-time ambiguity checks. Historical proof does not renew a source timestamp.
Known changed index signatures or later changed/failed article transport remain processing work
until checked; historical review cannot close that work. Fresh unchanged primary bytes may reuse
an existing exact semantic proof without creating new fact identifiers. Changed bytes require the
existing current-primary extraction and independent review path.

## Revalidation over several days

New receipts contain `revalidationCursors` and `indexSignatureBindings`, including empty arrays
where no references apply. Replay independently reconstructs both sets; omission or alteration
fails. A cursor references the sealed receipt that actually checked the primary against the
changed index signature. It pins that receipt's discovery manifest, exact primary observation,
full input context, direct original semantic origin and semantic-policy bridge. Replay checks
the witness at its original completion time, with causal predecessor ordering. A quiet receipt
never becomes another cursor origin, so later quiet days retain a flat reference to the same
actual primary check. Source and semantic dates remain unchanged.

When a URL disappears from a complete index or intake fails, `indexSignatureBindings` pins its
last independently replayed discovery signature. An uncleared change therefore remains pending
until an actual primary check resolves it. Newer failed, changed, future or ambiguous primary
transport overrides any earlier cursor. A successful exact-input primary check can reuse the
original complete semantic dispositions. The current work limit remains two documents per
source, including at most one ordinary historical audit. Known changed transport enters the
existing current-work lane even if the mutable audit scheduling hint is absent.

The primary check may happen after that URL has rolled out of the current index. Its witness
then pins the independently carried signature rather than inventing an empty signature. This
applies both to unchanged-input reuse and to a fresh semantic review of changed input. Later
quiet receipts keep the actual primary-check origin and the original discovery origin flat.
Partial-index replay reproduces failed terminal responses as failures while retaining the
signature proved by a successful sibling page; it never grants complete-intake credit.

The v2 document cache includes requested and final URLs, MIME type, extractor, model-text hash
and the complete compressed-input descriptor. Equal bytes with different relevant input context
require the existing current semantic review path. The original v1 cache namespace is unchanged.

## Review queue continuity

`source_document_revalidation` queue entries bind exact supplier, source and URL to a sealed
receipt and its independently replayed processing partition. Continuity replays these typed
proofs at their original times. A later independently proved fresh primary check and complete
semantic disposition closes only that exact marker. `documentReviewResolutions` retains both
the original marker and its sealed resolution provenance. Raw candidate holds remain in history.
`factProvenance` pins the exact current fact object when the same fact identifier gains another
reviewed observation, allowing continuity to validate the event against its actual evidence.
The existing funding-round detail advisory is independently checked against its funding fact
and event; it does not pretend to be a raw candidate-held object.

Existing citation sources retain their link and body integrity checks. Their successful intake
does not imply new semantic review or full claim accuracy. They add no generic document-history
counts and no new model work under this repair.

## Acceptance evidence

Focused tests cover intake with unfinished history, blocked/stale/incomplete discovery, unknown
and changed work, original-time semantic replay and migration tampering, policy/subject mismatch,
feed rollover, omitted predecessors, version stripping and exhausted work budgets. Actual archived
replay will preserve the complete 9,914-URL inventory and report all three measures independently,
with no live credit or archive changes. All runtime and tests run in OrbStack.

The completed guarded replay is saved in
`separate-freshness-history-actual-replay-2026-10-24.json`. It authenticates all 31,075 manifest
files in the 9c archive and records identical content, file-mtime and directory-mtime fingerprints
before and after. It preserves all 9,914 source-and-URL obligations, 24 original reviewed
document bindings, five reviewed documents with held claims, and all four exact original accepted
fact references. The remaining 9,890 documents remain pending; all 17 historical source tasks
remain incomplete for processing. Only those 17 discoveries were replayed at the archived clock,
so the separate intake result is 17 of the full 557 tasks, with every other task explicitly
unexecuted. The original combined report independently remains 244 of 557 under its original
contract. The replay made 98 archived transport reads with one process-local index scan and zero
source requests, model calls, archive writes, publications or denied-operation attempts.

Final verification passed 25 focused separation tests, the complete 555-test operations suite,
and all 115 pipeline tests. Independent read-only review repeated the lifecycle and multi-day
counterexamples and found no remaining actionable defect in that bounded review. These are
mechanical and archived-evidence results. They provide no live collection, semantic admission,
source freshness renewal or publication credit.
