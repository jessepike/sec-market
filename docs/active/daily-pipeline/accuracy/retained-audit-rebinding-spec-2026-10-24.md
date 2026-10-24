# Retained audit evidence rebinding

Proposal for review, October 24, 2026. No runtime implementation is authorized by this document.
The companion JSON contains the read-only replay results and the exact evidence references.

## Finding and recommendation

All 20 pages removed from false pending work by the selection repair have recoverable,
current-policy proof. All 20 passed the archived document replay and the stricter chain checks at
02:14:35 UTC on October 24. Seventeen have an immutable receipt-integrity seal. The other three
have exact membership in a previously archived, content-addressed coverage object. They must use
that membership proof; their scheduling stamps and unsealed attempt files alone are insufficient.

The newer archive also contains four additional completed document checks. Its current retained
set is therefore 24 pages, and all 24 replayed. There are no missing or policy-mismatched chains in
this set at the evaluation time. This is a result about archived proof and mechanical eligibility.
No collector receipt, independent review, admission or public release was created.

Implement one shared document replay function used by the engine and reconciliation. Carry each
retained document's original observation and complete semantic proof into the current receipt,
with its original dates. Add a separately bound full retained inventory so reconciliation can
check every historical URL, including URLs that disappear from a feed. Keep the 30-hour transport
limit. Rebinding alone completes none of the 17 historical source tasks: they still have 9,858
deferred due URLs, with another 32 due URLs selected for work. The coverage total remains 244/557.

## Evidence pins and boundaries

The application revision supplied for this investigation is `f17a636f`. The JSON pins the raw
bytes of the engine, validation, selection, storage, document parser, discovery, snapshot, agent,
archive, market contract and selection-repair artifacts actually read. Those file hashes are the
reproducible code identity; the revision label was not independently queried through Git.

The archive is the OrbStack VM directory:

```
/var/tmp/smp-renewal-20261024/archive-b9f1208b/jessepike-sec-market-b9f1208bd9e957bee5cca2c0b4db28a4fc1fa63f
```

Its supplied manifest SHA-256 is
`5480056315f07d6c6be4e66d5f9a643437d020eb039f2d51fe378ad70803c9bb`.
`GitArchive.verify` checked all 31,048 listed files. A separate inventory of all 31,052 files,
including the manifest and root metadata, had SHA-256
`7763b49b9f675e47d11ac379b2aae946a3b50f6c38e9cf39410525ce4c4f4d3c`
both before and after the investigation. No file in that archive changed.

The latest coverage object is
`objects/dd2b9964d49530c86429d5278a393f63ca8ecae9c35208b2b2ff45cafb1c5f35`,
506,366 bytes, checked at `2026-10-24T00:38:18.811621Z`. Its policy is
`de1932f7698d6b5ec86c23da52e77b1440c34d368e101c2aaabcbae6b39abfbe`.
The same digest was independently computed from the current project market contract. The plan
retains 557 tasks, 74 suppliers and inventory hash
`7b7823e4aac8d07689cc99e0b8a0363c7f100550d973ce026bb9df8b34ae5a95`.

The replay ran in OrbStack with Python bytecode writes disabled. An audit hook denied writes,
network and subprocess operations. A read-only store checked metadata against the pinned archive
manifest and content references against their hash and byte length. Calls made by
`verify_statement` to `store.put(review)` were replaced with checks that the identical object
already existed. One-document reconciliation fixtures existed only in memory. There were no
denied-operation attempts, source requests, model calls or archive writes. The only output files
are this proposal and its companion JSON in the project.

## What the existing code proves and where it stops

`engine.py:358-373` preserves the union of current discoveries, previous pending URLs and retained
audit inventory. Selection returns due work and deferred due work; the remainder is checked,
unchanged and not yet due according to the rotation cursor. `checkedAt` there schedules work. It
does not authenticate a document validation or renew transport freshness.

`engine.py:395-400` currently writes only the modification hint and scheduling check time to most
audit stamps. Compressed pages also retain a body/input descriptor. Neither form gives a complete
pointer to the original receipt, observation, extraction, review and disposition chain.
`engine.py:406-412` therefore holds an otherwise empty work queue with
`RETAINED_AUDIT_EVIDENCE_NOT_REBOUND`. That hold must remain until replay succeeds.

`validation.py:241-252` requires successful observations and source-specific transport freshness.
`validation.py:315-357` requires the document validation inventory, body/policy/supplier match,
candidate disposition inventory, reviewed empty result or valid shared-publisher exclusion, and
accepted-fact replay. Its document equality is currently against the discovery manifest alone.
That is insufficient for a retained URL that has fallen out of the current index. A new full
inventory binding must supplement the unchanged current-discovery record.

The existing successful-task path checks most semantic details only after an outcome claims
success. Retained binding validation must also run for incomplete tasks, so bad retained proof
cannot enter a partial receipt, a review queue or a later release through a weaker path.
`verified_partial_document_facts` and `collector_continuity` already distinguish document or
historical proof from source completeness; they do not grant retained source coverage on their
own. Preserve that distinction.

## Exact retained proof

The original 20 pages contain four accepted fact dispositions, five held dispositions, seven
independently reviewed empty extractions and eight deterministic shared-publisher exclusions.
The accepted facts remain their original records. All held candidates and their original
rejection reasons remain held. Two held candidates have an accepted model response but still
fail deterministic date validation. An accepted response must never erase that failure.

The three legacy exclusions are:

| Source | Page | Original transport time | Transport valid through |
|---|---|---|---|
| Exabeam | Thoma Bravo J.D. Power / Autodata release | 2026-10-23 04:15:22.688976Z | 2026-10-24 10:15:22.688976Z |
| Sophos | Thoma Bravo J.D. Power / Autodata release | 2026-10-23 04:15:22.373793Z | 2026-10-24 10:15:22.373793Z |
| Sophos | Thoma Bravo Quorum / Aucerna release | 2026-10-23 04:15:22.923121Z | 2026-10-24 10:15:22.923121Z |

Their original attempts appear exactly in coverage object
`objects/12baabcbf3f9eff5fab2022949c57ff5ffbf14b3361a715f67dafc8421ed87cb`,
503,331 bytes, checked at `2026-10-23T04:15:33.078892Z`. It carries the same policy and the exact
original task inventory. The two Sophos observations are genuine 304 checks whose body chains
lead to October 22 responses. Their bodies retain those older retrieval histories; the October 23
304 transport checks have their own original times. Exabeam has a full October 23 response.

The JSON gives every page URL, original receipt or coverage anchor, attempt and run ID,
observation ID and object digest, body hash and length, original and conditional transport times,
validation reference, extractor/cache identity, candidate hashes, fact and held references,
independent review references, replay outcome and freshness deadline. No new semantic result is
substituted for any original review.

## Proposed receipt contract

Apply this only to ordinary bounded discovery sources already handled by
`delta_with_retained_audit`. Leave citation, structured SEC, neutral SEC index and SEC filing
contracts on their existing paths. Do not extend SEC's immutable-document exception to ordinary
web pages.

Add `retainedAuditBindings`, `retainedInventoryManifest` and
`retainedInventoryPredecessorAnchors` to the bounded source receipt. An empty binding list is
valid; it grants no implicit coverage. Use the following binding shape as the implementation
interface, with an exact schema and no unknown authority fields:

```json
{
  "url": "https://publisher.example/original-page",
  "origin": {
    "runId": "original logical run",
    "taskId": "original task",
    "attemptId": "original attempt",
    "receipt": {"key": "objects/<hash>", "sha256": "<hash>", "bytes": 123}
  },
  "sourceObservationId": "original observation id",
  "sourceObservationSha256": "digest of complete original observation",
  "validation": {"key": "objects/<hash>", "sha256": "<hash>", "bytes": 123}
}
```

For an unsealed legacy attempt, `origin` instead carries `coverage` as a content-addressed
reference and the original run/task/attempt IDs. Resolve exactly one matching receipt inside that
object, and require equality with the original attempt. Never manufacture a seal for unsealed
history and then treat the new seal as its original authority. The three legacy cases above have
the required prior coverage object; an unsealed attempt without one remains unbound.

Both forms must also resolve the exact archived original plan and contract. The original task
must match the source, supplier and deterministic plan inventory. The original task may be
`not_checked`: a completed document from an incomplete multi-document source is usable if its
entire chain independently replays. Do not import the original task's completeness flag or its
other unchecked documents. Resolve references by their complete object identity, not a SHA
string without byte length and object content.

Bindings point to the original completed document check, not a chain of newer rebinding receipts.
Reject cycles and ambiguous origins. Repeated reuse must retain the same original transport time
and proof references instead of extending a chain of apparent new checks.

For future collection, audit stamps may add original run/task/attempt IDs, observation ID and
validation reference as lookup hints. `_finish` must have sealed the attempt before those hints
can become usable proof. A crash between writing a cursor and sealing an attempt must fail
closed. Cursors remain hints even when they carry proof pointers. They must not be re-dated when
retained work is replayed.

Prefer existing receipt-integrity references. For legacy migration, locate a prior coverage
object through the verified archive and resolve exact membership. A process-local lookup index
may speed the search, but it has no independent authority. Reconciliation checks every supplied
origin again. No hard-coded list of these 20 URLs or archive hashes belongs in normal runtime
eligibility logic.

## Full inventory and source context

Preserve `itemManifest` as the exact current discovery result with its own original discovery
observations. Build `retainedInventoryManifest` as the sorted, unique union of current discovery
items, previously retained inventory and previously pending items. Bind the predecessor records
to immutable prior receipts. For legacy audit inventory that exists only behind a mutable head,
use a verified prior archive-manifest membership proof of that exact inventory reference; do not
trust a fresh unanchored copy of the head. Failure to recover that predecessor holds completeness.
Previous inventory may add obligations; it never supplies semantic coverage.

Reconciliation must independently reconstruct this union and check the exact partition:

```
full inventory = newly completed URLs + successfully rebound URLs + unresolved pending URLs
```

The three sets must be disjoint and contain no missing, extra or duplicate URL. Selected work
that fails belongs in unresolved pending. An unresolved retained binding must remain explicitly
held; do not discard it, advance the successful source cursor or call it completed. Keep
`pendingDocuments` for actual due document work and report unresolved binding counts/reasons
separately, so a proof problem does not recreate false pending bookkeeping.

Require exact source/supplier/contract context before reusing semantic work. The full contract
hash binds supplier aliases, required categories and families, source registration, collector
kind, family, host restrictions and claim policy. Independently join the original observation to
that source and URL. A body shared by Exabeam and Sophos is not interchangeable source proof.
Bind final URL, content type and the parser/model input descriptor as well as the raw body.
Recompute compressed and ordinary input views with the current supported extractor and original
observation context. Where stored proof cannot establish the same input, require new validation.
An unsupported extractor change cannot be approved by a scheduling stamp.

Source-class and event-rung derivation must use the unchanged contracted source family. This
repair cannot promote a publisher's classification, alter a claim, change a category or bypass a
policy mismatch. Those changes retain their existing separate review requirements.

## Shared document replay

Extract a read-only validator in `validation.py` that accepts a resolved original receipt,
document binding, current contract/context, current time and store. Use it from both collection
and reconciliation. It must verify the following before returning any reusable references:

1. The immutable origin, exact original attempt membership, original plan/policy and complete
   source/supplier context all match.
2. The original observation is in that receipt, has the exact URL/source and a successful
   transport outcome, and its full object digest and body reference match. Check hashes and
   lengths on every object. Validate source-specific conditional-response chains. Reject
   unsupported `verifiedAt` renewal on generic web evidence.
3. The validation belongs to that receipt and covers the same supplier, body and contract.
   Reproduce the extractor/input descriptor and locate the matching extraction/validation cache.
   A cache key is a lookup hint; the records and chain must still be checked.
4. The extraction candidates match the complete validation candidate inventory. Every candidate
   has exactly one accepted or held disposition. Reject omitted or extra facts, candidates,
   reviews or held claims. Check both the document's own references and their presence in its
   original receipt.
5. Accepted facts reproduce exactly through `verify_statement`, including the full fact record,
   original source observation, quote, number, date, status, qualifier, policy and all seven
   accepted review dimensions. Same fact ID alone is insufficient.
6. Held candidates reproduce their exact candidate/body/policy/source/review bindings and their
   deterministic rejection reason. Preserve rejected, ambiguous and deterministically invalid
   candidates in the review queue. Rebinding does not resolve them.
7. An empty extraction retains its exact independent empty review and body/policy hashes, with
   the existing business-signal check. A deterministic entity exclusion remains limited to the
   contracted shared-publisher families, readable input and no registered entity mention. It
   cannot contain hidden candidates or claim references.

Append the original observation IDs, validation references, accepted fact references and held
references to the new receipt without editing their objects. Deduplicate references across
documents. A rebound fact is not a newly discovered market event and must not enter
`newFactIds` merely because it is copied into this receipt. Keep event identity and downstream
deduplication unchanged.

Track newly processed document checks separately from appended retained validations. The
`engine.py:395-400` audit-stamp update loop must run only for the former; iterating over the
combined validation array would wrongly renew every retained scheduling timestamp.

Reconciliation repeats this function for every retained binding before considering source
success, even if the source remains incomplete. It then enforces current discovery, inventory,
freshness and outcome rules. Remove the unconditional retained hold only after all bindings and
the full inventory pass; unresolved due work still keeps the source incomplete.

## Freshness and semantic reuse

Every generic document observation must remain within the existing 30-hour transport limit at
both collection and gate replay. The original task completion time, a sitemap `lastmod`, a new
receipt time, an audit cursor, unchanged bytes or a successful historical semantic replay cannot
extend that deadline. The existing small future-time tolerance is not permission to renew old
evidence. Preserve each original `fetchedAt`, body chain, effective date and review date.

At the evaluation time, the three oldest checks were about 21 hours 59 minutes old and still
eligible. After their stated October 24 10:15 UTC deadlines, their prior exclusions remain
historical proof. Current coverage requires a real new successful request or genuine
source-specific 304. An unchanged response body, supported extractor/input and exact policy/source
context may reuse the old semantic work. The new transport observation references the old body
and preserves the old evidence chain; it does not rewrite the original observation or reviews.
Changed body/input/policy/context needs the appropriate new validation. A policy mismatch cannot
be repaired by transport alone.

A stale retained observation creates genuine freshness-repair work. Keep its URL and historical
proof, expose the transport work as due, and select it within the existing collection and fetch
bounds. The read-only replay helper must not fetch old pages secretly or bypass the per-source
work allowance. Missing proof may remain a separate binding hold; expired transport requires an
actual new source check. If bounded work cannot refresh every required page before its deadline,
the task remains incomplete. This proposal does not make a large historical inventory fresh by
definition or authorize a different age policy.

Transport work remains charged to the existing fetch budget. Semantic cache replay makes no
model call. Any new extraction or review reserves against the unchanged persistent 40-document
and 80-call daily limits. No budget increase, uncharged retry or present-day live work is included.
The parent supplied exhausted current counters of 641 fetches, 80 calls, 40 documents and two
publication batches; this investigation did not change any counter.

## Effect on the 17 historical tasks

These counts use the newer b9 archive and the repaired selection function at the archived policy
time. The companion JSON pins each full URL inventory and deferred inventory hash.

| Source | Full inventory | Retained and replayable | Selected due | Deferred due |
|---|---:|---:|---:|---:|
| Proofpoint | 212 | 1 | 2 | 209 |
| Veeam | 727 | 1 | 2 | 724 |
| Exabeam | 638 | 5 | 2 | 631 |
| HiddenLayer | 89 | 3 | 1 | 85 |
| Optiv | 179 | 0 | 2 | 177 |
| Aqua | 448 | 0 | 2 | 446 |
| Mimecast | 137 | 0 | 2 | 135 |
| Arctic Wolf | 1,298 | 3 | 2 | 1,293 |
| WitnessAI | 243 | 2 | 2 | 239 |
| Expel | 329 | 0 | 2 | 327 |
| Ivanti | 429 | 1 | 2 | 426 |
| ReliaQuest | 91 | 1 | 2 | 88 |
| Upwind | 976 | 2 | 2 | 972 |
| Sophos | 638 | 4 | 2 | 632 |
| Snyk | 54 | 0 | 2 | 52 |
| eSentire | 170 | 0 | 1 | 169 |
| Dragos | 3,256 | 1 | 2 | 3,253 |
| Total | 9,914 | 24 | 32 | 9,858 |

The latest receipts report 9,910 pending URLs. Four completed documents from the latest archive
are already excluded there; the other 20 falsely pending pages account for the difference from
the 9,890 genuinely due URLs. They remain in the full inventory after that bookkeeping repair.
Rebinding their proof prevents a future completeness failure once due work is finished. It does
not resolve any of the thousands of due pages or change the 557-source denominator.

## Verification required before implementation can be accepted

The guarded investigation passed 24 original-chain audits and 24 existing one-document
reconciliation mechanics checks. Nine mutation probes were rejected: altered original attempt,
wrong supplier, wrong source, wrong URL, wrong policy, missing held reference, changed candidate
inventory, forged generic `verifiedAt`, and transport older than 30 hours. The two inventory
mutations were rejected at cache equality before a narrower inventory check. Implementation
tests must also rebuild those in-memory cache references and confirm the complete disposition
check itself rejects the omission. These are planned tests, not a claim that new runtime behavior
has already passed them.

Required implementation tests include:

- Valid sealed and legacy coverage-anchored origins, including completed documents inside an
  incomplete task; rejection of unsealed raw attempt JSON without an immutable membership anchor.
- Same-source/source-family, supplier aliases/categories, policy, URL/final URL, content type,
  extractor and compressed/plain input context checks. Same bytes from another source are rejected.
- Missing/corrupt body, observation, validation, extraction, candidate, accepted fact, held claim,
  review, seal or predecessor inventory; changed object hash, byte length or original time.
- Full equality of the discovered-plus-retained-plus-pending inventory and its disjoint completed,
  rebound and unresolved sets. Cover feed rollover, duplicate URLs, omitted prior pending URLs,
  forged predecessor snapshots and a crash before original receipt sealing.
- Recomputed accepted facts, all seven review dimensions, held reason replay, exact empty review,
  deterministic shared-publisher exclusions and partial inventories after rehashing every wrapper.
- Freshness at 30 hours and one second later; unchanged old body with a real fresh 304; failed or
  mismatched 304 chains; different body/input requiring new semantic work; no clock or quota renewal.
- No mutation of source bodies, observations, validation/review objects, cursor times or existing
  facts. No duplicate market event, false `newFactIds`, review resolution, source-class change or
  automatic current-policy admission from historical continuity.
- A source with only complete fresh retained proof can succeed after independent reconciliation;
  a source with unresolved work remains incomplete. Replay this archive with all 9,914 URLs
  retained, all 24 bindings checked and all 17 historical tasks still incomplete.
- Existing pipeline, semantic replay, partial-document, collector continuity, snapshot, gate and
  full application checks in OrbStack. Verify that another run/day, tampered cache or current
  receipt cannot borrow stale or policy-mismatched success.

Implementation, a real collector run, current-time gate replay and any later publication require
their own evidence. The current production release and exhausted allowances are unchanged.
