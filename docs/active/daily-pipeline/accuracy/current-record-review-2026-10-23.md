# Existing-record accuracy review

## Result and production scope

The fixed review covers all 97 hand-collected events and 80 selected non-SEC supplier fields,
177 records in total. It identifies five directly contradicting records, 90 supported records,
71 records with insufficient support for at least one clause, and 11 lacking the primary proof
required by this review. These are review judgments about this fixed scope, not whole-site
precision or recall. An insufficient record may have a supported core fact and one unsupported
qualifier; it is not automatically false.

The exact source arrays match production application
`7bd94ec77e99462c068f254e134235a894585cbb`. Actual production probes confirmed all 11 proposed
targets' original text in the served application bundle, and the two Expel fields in
`/tracker.json`. Historical events still follow the UI's normal date filters; bundle presence
does not mean every historical event is on the first screen.

Source checking remains **121/557**. The 177-record audit is a separate denominator. No source
check, source timestamp, allowance or publication receipt was upgraded by this review.

## Corrections prepared

Five correction groups affect six event/field targets and five related evidence records. The extra
supplier target is Expel's funding field,
whose wording is ambiguous alongside its directly incorrect ownership sentence. The drafts
preserve original objects and their hashes, proposed after-values or withdrawals, source-body
and observation identities, and the original fetch dates.

| Group | Existing reading | Primary evidence and proposed action |
|---|---|---|
| Check Point debt | Notes issued during Q2 2026, approximately $1.8 billion net proceeds | The offering closed December 8, 2025 and is already recorded separately. Withdraw the duplicate July issuance entry. Distinguish offering net proceeds from proceeds after capped-call purchases. |
| Optiv debt | Closed extension on May 8, 2026 | The cited release is dated March 16 and describes an agreement with extensions effective upon closing. Correct the date and conditional status together. |
| Splunk restructuring | Fixed $1 billion charge including Splunk integration | Cisco's filing describes company-wide estimated future charges of up to $1 billion. It does not allocate an amount to Splunk. Withdraw the unsupported Splunk-specific record; do not infer that Splunk was excluded. |
| Zscaler leadership | Board resignation effective April 16, mixed into the September CRO record | The separate primary filing gives April 15, already recorded in its own event. Remove the incorrect retrospective clause and retain the supported CRO transition. |
| Expel funding | Additional $171.3 million in the Series E extension | The company increased the total Series E round to $171.3 million. Correct both affected fields and keep cumulative company funding, initial round and valuation date distinct. Do not infer an incremental amount from rounded totals. |

The related evidence records contain some of the same errors in their excerpts or publication
metadata. Draft version 2 corrects those five records too, including Optiv's source date and the
incorrect Expel, Check Point and Zscaler excerpts. Their replacement excerpts are literal text
from the bound primary bodies. All 11 original target readings are still present in the served
production bundle. This targeted metadata follow-through does not change the fixed 177-record
audit denominator or claim that every evidence-record field has been reviewed.

See [latest exact draft targets and source bindings](dated-correction-candidates-2026-10-23.v2.json).
Draft correction dates remain placeholders until actual publication. No correction has been
admitted, applied or published.

## Other findings remain visible

The full ledgers retain date conflicts, unsupported completion/current-ownership claims,
accounting-versus-transaction value differences, missing qualifiers and citations that should
point to an already archived primary document. Those findings are not waived by fixing the
five clearest errors. Some strict missing-primary findings concern issuer-attributed syndicated
press releases; their content may support the claim while original-publisher provenance remains
unresolved. They are not counted as known false claims.

The original Proofpoint and Varonis source bodies used for the missing-event correction were
still in temporary files, outside the evidence-archive baseline. They are now retained unchanged
as hash-verified fixtures with their original provenance. This improves reconstructability without
asserting a new retrieval or current endpoint check.

## Evidence and admission boundary

The frozen inventory and the three ledgers retain exact published objects, complete review IDs,
source URLs, archived observation IDs, original dates, body hashes, proof excerpts and limitations.
The offline binding verifier checks the independent source-array inventory and actual bytes.
It rejects omitted/duplicate records, changed datasets/bodies, invented excerpts, wrong URLs,
future timestamps and arbitrary local-fixture substitutions. Passing those checks establishes
identity and reconstructability; it does not independently certify the reviewers' interpretations.
All 177 bindings passed. The verifier initially rejected 13 clipped or irrelevant supplier excerpt
contexts; those were replaced with exact relevant text or explicit proof-gap notes, without
changing the source-body pins or semantic verdicts. Agents performed the text review in this
session; zero model calls refers to collection/extraction/admission worker calls, not an absence
of agent reasoning.

The operational scorecard now exposes fixed review coverage and known contradicting records
separately from release tests. A passing SEC/build gate cannot hide a known factual error.
Overall precision, eligible-event recall, sustained durability and reader value remain unmeasured.

The public correction path still needs implementation and current-policy independent admission.
Use a separate factual-correction ledger and deterministic current view, preserving original
history and keeping existing owner-approved issue/thesis corrections untouched. The existing
publisher assertion does not independently verify arbitrary edits to static hand-collected text.
The proposed admission adapter must bind each exact before-value, replacement/withdrawal and
supporting evidence; it must reject unreviewed static edits. See
[correction-path proposal](correction-path-proposal-2026-10-23.md).

No owner factual decision is needed for the five supported correction groups under the existing
authorization for sourced facts. Implementation, source qualification and the remaining reviews
are agent work. October 23's charged limits remain spent. Publication requires the next natural
allowance, proper independent review and normal release receipts; offline audit work is not a
substitute for those steps.

## Files

- [Frozen 177-record inventory](published-inventory-2026-10-23.json).
- [A–M event ledger](event-review-a-m-2026-10-23.json).
- [N–Z event ledger](event-review-n-z-2026-10-23.json).
- [Supplier-field ledger](supplier-fields-review-2026-10-23.json).
- [Actual production presence for all 11 targets](production-claim-presence-2026-10-23.v2.json).
- [Pinned binding inputs](source-bindings-inputs-2026-10-23.json).
- [Verified source bindings](source-bindings-2026-10-23.md).
- [Updated operational scorecard](../evaluations/2026-10-23/accuracy-scorecard.md).
- [Review plan](../accuracy-review-plan-2026-10-23.md).
