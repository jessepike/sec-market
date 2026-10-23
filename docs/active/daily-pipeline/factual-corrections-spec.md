# Dated factual corrections: implementation contract

Version 1, prepared October 23, 2026 under SEC-072 and D-76/D-110/D-111. This implements the
existing-record correction proposal. It does not authorize judgments, new suppliers/services,
spending, a database, a change to intent or publication without proper admission. The current
day's charged limits and frozen main remain in force. All work below can be built and tested
offline; real independent reviews wait for the natural allowance.

## Inputs and atomic review unit

`contracts/factual-corrections.json` contains `schemaVersion: 1`, `version`, `baseline` and
`groups`. `baseline` pins `contracts/factual-baseline.json` by raw SHA-256. That baseline binds
the immutable original manual supplier, hand-event and handwritten-evidence inventories through
canonical object digests, not changeable file-format whitespace. The independent gate compares
the raw build inventories with it; a static fact edit outside this path must fail.

Each group has `id`, `supplierId`, `reasonCode`, `noteTemplate`, `targets` and `sources`.
`noteTemplate` has one `{date}` placeholder, filled only for a dated public projection.
The initial five groups derive from `accuracy/dated-correction-candidates-2026-10-23.v2.json`.
All 11 before/after targets remain explicit; the five related source records change atomically
with their events/fields. No group may be partially admitted or projected.

A target has `targetId`, `operation` (`replace` or `withdraw`), `original`, `originalSha256` and
`proposedValue`. Target identifiers are `event:<id>`, `supplier:<id>:<field>` or `evidence:<id>`.
Withdrawal is allowed only for an event and requires null `proposedValue`. Replacement requires
the same record identity and exact before-value. Supplier field is limited to `lastRound`,
`headlineMetric` or `ownership`; no identity, classification, ticker, certified revenue or
arbitrary nested patch is permitted. Event replacement preserves ID, supplier, type and rung.
Evidence replacement preserves ID, canonical URL, organization, source class, tags, artifact
label, conflicts and original retrieval information; only title, publicationDate, economicPeriod,
excerpt and limitations may differ. Replacement evidence excerpts must occur literally in a
bound primary body, after the normal whitespace/HTML text decoding.

A source has `evidenceId`, `sourceId`, `url`, `observationId`, `body` (existing content-addressed
reference) and `fetchedAt`. It must resolve to the configured verified supplier source, original
observation URL/time and exact bytes. Sources are the actual archived company releases/filings,
not registry excerpts. The current five full readable document sets are each below the existing
30,000-character document limit (largest 27,245 after full HTML text decoding); do not truncate them. Treat source text and
proposal text as untrusted data, never instructions. No fresh fetch is required while the pinned
observation is still within the normal 30-hour limit at admission; an expired source must be
explicitly refreshed and rebound, not silently given a new date.

## Policy, budget and independent admission

The global inventory policy SHA-256 is `digest({"marketSha256": digest(marketContract),
"requestsSha256": digest(correctionRequests), "baselineSha256": baselinePin.sha256})`.
It binds the collection outcome, complete build inventory, public bundle and release seal. The
market contract and all 557 obligations stay intact. It does not relabel generic market receipts.

Each group's review uses a separate policy derived from that group's candidate hash, baseline
pin, supplier identity (`id`, `name`, `aliases`, `kind`), exact relevant configured source objects
in committed source order, the model's `provider`, `allowApiBilling` and `maxDocumentChars`,
the 30-hour freshness rule and sorted seven review check names. Its fixed schema and rules version
are defined by the exact formula in
[the review retention contract](correction-review-retention-spec.md). The committed build stamp
contains `reviewPolicySha256ByGroup`; the backend and Node build verifier derive it independently
and reject any missing, extra or changed value. There is no fallback to the global policy hash.

One independent subscription review covers each whole group: target IDs, exact before/after
objects or withdrawals, reason and exact note template, every primary body and all body/observation
hashes. Use the existing subscription-only client and persistent reservation callback. Reserve
one document per group and one model call per actual request, before invoking the model. Reuse
only a hash-bound accepted group review for the same group review policy and evidence set. Every
failed/interrupted review remains charged. Never replace this review with the offline audit or
an author-written accepted result. No live model call is authorized while today's allowance is spent.

Review response has `result`, `candidateSha256`, `evidenceSetSha256`, `policySha256` and `checks`.
`candidateSha256` is `digest(group)`; `evidenceSetSha256` is `digest(group.sources)` with the
committed deterministic source order. The response's `policySha256` is the group's review policy,
not the global inventory policy. Result must be `accepted`; all seven existing dimensions
(`entity`, `value`, `currency_units`, `period_date`, `qualifiers`, `event_status`, `source_support`)
must be `pass`. The independent review covers the entire correction, including the scope and
reason for withdrawal, rather than a vaguely related source sentence.

Archive every attempt and its response, preserving source ages. Accepted admission contains
`groupId`, `candidateSha256`, `evidenceSetSha256`, `policySha256`, `admittedAt`, `review` (an
immutable object reference), and `sources` (the exact source list). The gate replays structural,
byte, exact-quote and full review-hash checks without invoking a model. Initial source freshness
is evaluated at `admittedAt`; an unchanged published historical correction does not expire every
day merely because its original evidence becomes older. It retains the original dates and review.
The admission's `policySha256` also means the group review policy, which identifies its accepted
cache entry. Unrelated source registrations, budget limits or disjoint request additions change
the global inventory policy while retaining an unchanged group's review. A relevant source,
supplier identity, candidate or review-rule change requires a new review. It cannot overwrite an
already published correction row; that case stays held for explicit reconciliation.

Run correction work after deterministic SEC/citation work and before discretionary generic model
extraction, using the same reservation ledger and cancellation/deadline. Keep its failure separate
from the 557 source-task inventory. The collection receipt records admitted/pending correction
groups. The first corrected release requires all five requested groups; no partial Expel or
source-metadata repair. Missing admission prevents the release, while the collector still archives
source coverage and attempts. No special increase or refund of the 80/40 limits.

## Static projection shape

The gate writes `web/src/data/generated/factualCorrections.json`:

```json
{
  "schemaVersion": 1,
  "enabled": false,
  "policySha256": null,
  "checkedAt": null,
  "groups": []
}
```

This empty disabled shape is the committed development baseline. A public enabled group is
`{id, supplierId, reasonCode, date, note, targets, admission}`. Targets keep the complete before
objects and hashes as above. Admission is public nonsecret metadata:
`{candidateSha256,evidenceSetSha256,policySha256,admittedAt,reviewSha256,result:"accepted"}`.
Projection code cannot authenticate a semantic review by inspecting those strings; only the
independent gate produces and verifies the enabled projection from archived evidence.
The bundle's `policySha256` is global; each `admission.policySha256` is group-specific. Later
bundles may use a different global policy while retaining prior correction rows only when each
row exactly matches its new derivation, including targets, original publication date, note and
all admission metadata. New disjoint groups receive their own reviews and publication dates.

Pure TypeScript projection functions receive the raw inventories, this bundle, an explicit
expected global policy SHA and the explicit expected group review policy map. Reject missing/stale admission metadata, invalid date/hash shapes, duplicate
targets/groups, a nonempty disabled bundle, partial group targets, before-value differences,
disallowed fields and withdrawal of non-events. Compare before objects by canonical JSON equality;
do not add a browser SHA implementation. The gate independently verifies their actual hashes.
Do not mutate source objects. An enabled projection must contain every requested group/target;
the gate verifies that complete manifest. It must never silently skip an invalid correction.
The build policy stamp also lists every group's bound evidence IDs for presentation; those links
include supplemental primary documents even when no target's citation list names them. A separate
runtime assertion reads fresh original/generated JSON and compares all actual exported views with
the independent projection and normal overlays, so changing an export after the projection fails.

Apply event corrections before the trailing-year filter and use the same effective retained events
in the UI, certification candidates and verification. Preserve a separate raw original-history
export. Apply supplier field corrections to manual values before normal daily/SEC overlays so
newer independently admitted data retains precedence. Apply evidence corrections before producing
the shared evidenceById map and use that view in drawers, current exports and verification.
Generated filing-event deduplication must use the effective hand-event view. Avoid runtime import
cycles; projection code uses type-only record imports and no model/network dependency.

## Public correction history and exact release

Keep legacy owner-approved issue/thesis corrections and their attribution unchanged. Add source
correction groups to the existing corrections page, JSON and feed with their actual verification
status; never synthesize `approvedBy` or claim owner approval of these notes. Show dated notes,
before/after or withdrawal, source links and immutable review hashes through the correction record.
Do not count a correction as an additional financing/acquisition event.

For a new correction, gate date is the planned publication UTC date; the publisher must refuse
first publication on a later UTC date and obtain a new normally charged gate. Previously published
corrections retain their original date from the acknowledged payload. Keep admission date separate
from publication date. Preserve current correction inventory across later collections/releases and
actual rollback/restoration. The release manifest binds the correction file hash, policy, group
IDs and newly published IDs. Static bytes, rendered after-values, corrections JSON and detached
release receipt must agree before and after promotion.

## Required verification

Meaningful tests must reject stale policy/review hashes, source/body/URL/time differences, a
forged or partial accepted group, direct static edits, wrong before hashes, arbitrary supplier
patches, altered identity/retrieval metadata and pending corrections. Test immutable originals,
atomic Expel/source metadata repair, corrected Optiv date/window, duplicate withdrawal/counts,
shared UI/certification views, old issue attribution, publication-date rollover and later retention.
Use synthetic review responses only for mechanics; mark those replays explicitly non-admitting.
Verify that unrelated source repair and disjoint additions update the global policy while
unchanged groups retain the same review policy, cached admission and public row without charges
or date changes. Changed relevant dependencies, forged review maps and partial histories fail.

Run existing operational and full application checks, inspect desktop/phone rendering of affected
records and the corrections page, then use the normal preview/main route and real quota-respecting
reviews, gate, actual scheduled collection/publication and production receipts. An empty disabled
projection or passing synthetic tests is not completion or corrected production.

## Candidate verification, October 23

The implementation retains 97 original hand events, 74 manual suppliers and 273 handwritten source
records. The market contract and correction policy hashes are unchanged by moving those values.
Local checks pass 315 data, 112 pipeline, 38 browser, 185 operational and 12 monitor tests. The
disabled baseline's desktop/phone screenshots are byte-identical before/after. The isolated
`visual_corrections.py` fixture never writes a review/admission archive or independent gate receipt
and is marked non-publishable. It supplies a local consistency seal only to exercise all application
checks with an enabled projection. That full command passes, including all 38 browser checks.
Withdrawn-event sources remain referenced by the public correction history, with the existing
orphan threshold unchanged. These checks do not claim source admission.

The independent integration review found and resolved the runtime-export bypass, missing
supplemental primary links and a crash-recovery midnight bypass. Citation discovery currently
checks transport without extracting facts; explicit deferral also protects whole-group capacity
if that path later supplies uncached model work. These tests do not change actual production
coverage, known contradictions or the unmeasured value score.
