# Correcting existing tracker facts without rewriting history

## Recommendation

Add one small, separate ledger for source-verified tracker corrections and a deterministic
projection over the current event and supplier data. Preserve the original hand-collected
objects. Admit each replacement through the existing source-statement and independent-review
checks before the projection can apply it. Show a dated factual correction beside the affected
record and on the corrections page, with its original reading accessible.

The current owner-approved issue/thesis corrections are a different record. Do not add Jesse's
name, an approval date, or an `approvedBy` assertion to an automated factual correction. The
owner authorized the accuracy work and automated sourced facts; that does not mean he approved
the exact wording of these five corrections.

This is a proposal, with no public data or application code changed.

## Existing authority and working mechanisms

- D-76 authorizes sourced, machine-validated facts without a human factual approval step;
  machine-written judgments remain prohibited. See
  [decisions.md](/Users/jessepike/code/projects/sec-market-finish-20261022/decisions.md:976).
- D-110 authorizes the reviewed daily pipeline while preserving individual changed-fact
  evidence gates and complete SEC certification. Its wording approves activation and
  verification, not these exact correction texts. See
  [decisions.md](/Users/jessepike/code/projects/sec-market-finish-20261022/decisions.md:1296).
- The current `Correction` type requires verbatim owner-approved text and `approvedBy`.
  Its item references are issue-item references. Standing-reference corrections can omit an
  issue, but still require the owner-approved text and attribution. See
  [types.ts](/Users/jessepike/code/projects/sec-market-finish-20261022/web/src/data/types.ts:290)
  and [corrections.ts](/Users/jessepike/code/projects/sec-market-finish-20261022/web/src/data/corrections.ts:5).
- The existing helper finds the first matching corrected reading for an issue item; it is not
  a versioned tracker-event or supplier-field replacement resolver. See
  [correctionHelpers.ts](/Users/jessepike/code/projects/sec-market-finish-20261022/web/src/data/correctionHelpers.ts:14).
  The corrections renderer explicitly prints `Approved by`. Its current JSON/feed exports
  also use the existing correction type. See
  [Corrections.tsx](/Users/jessepike/code/projects/sec-market-finish-20261022/web/src/components/Corrections.tsx:12)
  and [generate-feed.ts](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/generate-feed.ts:98).
- `retainedTrackerEvents` combines hand-collected, filing-generated and daily events. The
  comment explicitly preserves append-only source history; `trackerEvents` then applies the
  trailing-year date window. There is no supersession/withdrawal mechanism. See
  [events.ts](/Users/jessepike/code/projects/sec-market-finish-20261022/web/src/data/tracker/events.ts:1117).
- Supplier data already uses projections: manual supplier records pass through daily data and
  then SEC revenue. Generic daily updates only support `headlineMetric` and `lastRound`, with
  newer-date rules. They cannot safely correct an old ownership sentence or old funding
  amount by simply appending a daily event. See
  [suppliers.ts](/Users/jessepike/code/projects/sec-market-finish-20261022/web/src/data/tracker/suppliers.ts:2042)
  and [daily.ts](/Users/jessepike/code/projects/sec-market-finish-20261022/web/src/data/tracker/daily.ts:34).
- Generic admission requires exact source bytes, an exact quote, a published statement
  supported verbatim, grounded dates/qualifiers/status, and a separate review bound to the
  exact candidate, evidence hash and current policy. See
  [validation.py](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/validation.py:38)
  and [engine.py](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/engine.py:219).
- The fresh gate reconciles archived receipts, rebuilds the snapshot and runs SEC and full
  application checks. The publisher's `allChangedClaimsVerified` requirement is currently a
  snapshot assertion, not an implemented audit of arbitrary edits to static hand-collected
  text. It must not be treated as automatic admission for these corrections. See
  [gate.py](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/gate.py:23),
  [gate.py](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/gate.py:98)
  and [publication.py](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/publication.py:24).

## The five concrete correction candidates

These are proposed factual changes from the archived audit. They have not been admitted or
published. Preserve the source-body and observation pins from the existing accuracy ledgers.

| Target | Required factual change | Safe scope and remaining admission |
|---|---|---|
| `EV-checkpoint-2` | Remove the claim that the notes were issued in Q2 2026. The existing primary 6-K dates the offering to December 8, 2025. Distinguish approximately $1.97 billion of offering net proceeds from the later release's approximately $1.8 billion after issuance costs and capped calls. | `EV-checkpoint-4` already records the December offering. Preserve both original records; withdraw the erroneous duplicate from the current projection or replace it with a source-dated clarification linked to the existing correct event. Do not count a correction as another financing event. |
| `EV-optiv-2` | Use the March 16, 2026 agreement announcement. The source says amendments will extend maturities upon closing; it does not establish that the extension had closed. | Retain the August 2028/2029 maturity targets as conditional terms. Change both date and status wording together, with the original May 8/closed reading retained in the correction record. |
| `EV-splunk-1` | Cisco's company-wide estimate is up to $1 billion; the cited evidence does not establish a realized $1 billion charge or a specific Splunk allocation. | Prefer withdrawing this unsupported Splunk-attributed event from the current projection, while showing the dated correction and primary Cisco statement. Do not add Cisco to the roster or assign an undisclosed charge to Splunk. If retained as parent-company context, explicitly identify company-wide scope and estimated/up-to status; that needs a scoped display contract, not an inferred allocation. |
| `EV-zscaler-2` | Correct Raj Judge's board-resignation effective day from April 16 to April 15, 2026. | Preserve the separate September announcement and October 1 CRO-transition clauses where independently supported. Do not change the entire event date to April 15 merely because one retrospective clause has that effective date. |
| Expel `lastRound.amount` and `ownership.status` | The October 3, 2022 release says the Series E increased **to** $171.3 million, with total funding $288.8 million. It does not say an additional $171.3 million was raised. | Replace both affected fields consistently. Use the round total stated by the source; do not introduce a computed $31 million incremental amount into the generic verbatim admission path. Preserve the initial-round date and valuation attribution where supported. |

Evidence and findings are in
[A–M event review](/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/event-review-a-m-2026-10-23.json),
[N–Z event review](/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/event-review-n-z-2026-10-23.json)
and [supplier-field review](/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/supplier-fields-review-2026-10-23.json).

## Smallest implementation options

1. **Edit the static objects and append a dated factual note.** This has the fewest code
   changes and can preserve prior text in a separate note, but it rewrites the original event
   array that the current code explicitly treats as append-only. Existing static edits also
   lack a per-replacement admission check. I would not choose this for the hand events.
2. **Append replacement events with new IDs and a supersedes field.** This preserves the array,
   but still needs a resolver, current-view suppression, dated notes, admission checks and a
   separate supplier-field mechanism. Simply appending would leave both wrong and right facts
   in the timeline and inflate event counts.
3. **Use one typed factual-correction ledger and current-data projection.** This preserves the
   originals, covers events and supplier fields, and shares admission, dated notes and
   provenance. I recommend this option. It needs no database, service or contract/roster expansion.

The recommended record needs only: stable correction ID; recorded/published date separate from
event effective date; target event ID or supplier ID plus an allowlisted field path; original
object/value hash; replacement value or explicit withdrawal; reason code and factual source
references; current-policy candidate/fact/review/evidence hashes; and an optional prior correction
ID for later amendments. The original value/text stays in the ledger and in the retained source.
Avoid arbitrary object patches, executable expressions, mutable source URLs as proof, and a
machine-generated `approvedBy` field.

Keep this type separate from the legacy `Correction`. A renderer can combine both correction
lists by date while retaining their distinct attribution: existing owner-approved records keep
their original text and attribution; verified tracker facts show their actual source/evidence
status. Extend the existing corrections page/JSON/feed deliberately rather than pretending a
machine correction is an owner-approved issue correction. No change to the frozen issue/thesis
records is needed.

## Where to join it and what must fail closed

Apply event corrections before the trailing-year filter, so changing a factual date also fixes
the window and chronology. Preserve the raw retained originals as a separate export. Provide one
effective retained-event export for both the UI and the checks that certify its displayed facts.
Update these consumers together:

- [verify-tracker.ts](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/verify-tracker.ts:528)
  currently searches raw retained events for matching supplier facts.
- [verify-integrity.ts](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/verify-integrity.ts:112)
  must validate original and replacement evidence joins.
- [candidates.ts](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/sec-verify/candidates.ts:26)
  must derive certification candidates from the same effective event view as the UI. Its current
  `secEvents` projection contains IDs, dates, types, accessions and evidence dates, not semantic
  proof of every event sentence.
- [filing-events.ts](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/filing-events.ts:146)
  currently deduplicates generated records against original hand event dates/types. Corrected
  dates and withdrawals need an explicit regression check so a raw original does not suppress
  a necessary generated event or create a duplicate.

Apply supplier corrections as an allowlisted projection over manual values before normal daily/SEC
overlays; constrain these five corrections to their named fields. Newer independently admitted
data must retain normal precedence. A changed target hash, ambiguous correction chain, duplicate
active correction, missing current-policy admission, mismatched body/review hash or unsupported
replacement must stop the release. Do not silently skip a correction and publish its old error.

The gate must bind each displayed replacement/withdrawal to its admitted correction manifest and
verify that rendered after-values match that manifest. This closes the static-edit admission gap.
Reuse current source-statement validation and review artifacts; add only target/before/after
binding and deterministic presentation rules. Prefer exact admitted source statements to new
paraphrases. A multi-clause explanatory sentence must have all its factual clauses covered; one
correct source link is not sufficient. A withdrawal still needs its dated correction and the
independently checked mismatch evidence; it must not bypass admission by being called a refactor.

The existing generic candidate schema has no correction target or withdrawal operation. A small
admission adapter is therefore required; this is not already implemented. Its independent review
must bind the exact correction bundle, including target, old value, replacement/withdrawal and
source facts. Reuse the existing seven semantic dimensions and charged subscription-review
mechanism, but do not relabel a review of an unrelated source sentence as approval to withdraw
an arbitrary event. Both bundle identity and underlying source-statement admission must be checked.

Minimum tests should prove original objects remain unchanged; wrong date/status/qualifier reading
is replaced exactly once; before-hash mismatch and old-policy review fail; pending corrections
cannot publish; timeline counts exclude withdrawn duplicates; certification and UI share the
effective view; Expel's two fields remain consistent; and old issue correction attribution/text
is unchanged. Render the affected records and corrections page at desktop and phone sizes.

## What can happen now

Prepare the five exact correction drafts, raw-byte pins, target hashes and deterministic tests.
Implement the disabled projection/admission plumbing and review the resulting local artifacts.
Offline replay can prove mechanics, preservation and rejection behavior. It cannot create an
independent semantic-admission result for a newly worded fact.

The current day has exhausted its 80 model calls, 40 document reservations and 5,500 fetches,
and its release attempts are charged. Keep these candidates pending until the normal allowance
renews and the required current-policy independent review and release gate run. Existing exact
valid admission may be reused only if its candidate, raw evidence, policy and source-specific
freshness actually match; the audit ledger alone is not such admission. Do not reset counters,
manually declare `allChangedClaimsVerified`, or treat an offline review as an uncharged publisher.

No owner factual approval is inherently needed for these supported corrections under D-76.
No unresolved factual choice here justifies asking him to approve a date or funding amount. If a
code/presentation change falls outside the already authorized scope, present that concrete change
through the normal reviewed preview route; do not manufacture exact-text approval from D-110.
Source gaps, mismatched reviews and exhausted allowances remain agent execution work or explicit
limits. New services, spending, a roster change or publishing judgments would require separate
authorization; none is recommended here.

## Source-record consistency follow-through

The latest draft bundle is
[version 2](dated-correction-candidates-2026-10-23.v2.json): six event/supplier targets plus five
related evidence-record replacements, still in the same five factual correction groups. Source
metadata can contain the same wrong reading as the event. In particular, Optiv's evidence date
is May 8 in the registry while the source is March 16; several stored excerpts repeat the
incorrect financing or resignation reading. Correcting an event while showing its old false
excerpt in the drawer would leave the reader with contradictory data.

The typed correction target must therefore also support an exact evidence-record replacement.
Preserve its original object/hash; allow only the relevant title, publication date, economic
period, excerpt and limitations to change. Keep its identity, canonical URL, organization,
source class and original retrieval date intact for these five cases. Validate every new excerpt
against the actual bound body, and have the independent bundle review cover its dates and
interpretation. Apply the corrected evidence view consistently to drawers, current exports and
checks while retaining originals for the dated correction history. Do not relabel old metadata
as newly fetched evidence or use a registry excerpt as primary proof.
