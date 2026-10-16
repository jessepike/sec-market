---
id: SEC-MARKET-AUTO-002-P0
version: 0.2
state: built; independent audit fixes applied
created: 2026-10-15
parent: SEC-MARKET-AUTO-002 (docs/reference/auto-002-proposal.md)
decisions: D-89 (certified scope), D-85/D-86 (100% gate, no self-certification), D-96 (cadence)
---

# Phase 0: make the 100% gate passable for the SEC filers

> Decision record, written 2026-10-15 before Phase 0 was built. "Today" below means that date. The laptop collector it mentions was retired on 2026-10-16; file names are current.

## Goal

A run with no human and no AI produces a certified snapshot of the SEC filers that passes `evaluateRefresh` at 100%, using primary SEC data only. Phase 0 proves the gate can pass. It does not schedule anything, publish anything, or change the site. Scheduling is Phase 1; the site's tier display is Phase 2.

## What the code review found

- `evaluateRefresh` in `web/scripts/claim-gate.mjs` (named `refresh-publication-gate.mjs` until 2026-10-16) is generic. It requires one proof per supplier × group listed in the contract it is given. A narrower contract needs no gate change.
- Nothing produces proofs today. `web/src/data/generated/refreshVerification.json` has 0 verified claims.
- Displayed SEC revenue already comes entirely from XBRL (`web/src/data/tracker/edgarRevenue.ts`), including `releaseDate`, which is the 10-Q or 10-K filing date.
- `selectRevenueFacts` takes the first concept with any USD fact. A filer that changes revenue tag can silently freeze on an old concept.

## Design

### 1. Certified contract `smp-certified-v2`

File: `web/src/data/tracker/certifiedContract.json`. The v1 contract and its 74-supplier path are untouched in Phase 0.

- `supplierIds`: every tracker supplier whose `edgarId` is in `edgarRegistry`. Currently 16. Never hand-set: a test fails if the file differs from the derived set.
- Groups and freshness (hours): `identity` 720, `revenue.latest` 24, `revenue.prior` 24, `secEvents` 24.
- Components: identity `name`, `ticker`, `kind`; revenue.latest `value`, `priorYearValue`, `yoyGrowth`, `period`, `periodEnd`, `releaseDate`; revenue.prior `value`, `priorYearValue`, `yoyGrowth`, `period`, `periodEnd`; secEvents is one list value.
- No exclusions and no undisclosed answers.

Scope rule, fixed before any results: the certified tier is "suppliers with structured SEC XBRL revenue". It is chosen by source class, not by which claims passed. Check Point and Trend Micro stay outside because they do not file XBRL quarterly revenue with the SEC.

### 2. Independent verifier

File: `web/scripts/sec-verify/independent.mjs`. Plain JavaScript. It does not import `edgarLogic.ts`, `edgarRevenue.ts` or `filing-events.ts`. The point is that the code that produces a value is not the code that checks it.

For each certified supplier it fetches, with the SEC User-Agent and rate limit, and hashes the raw bytes of:

- `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`
- `https://data.sec.gov/submissions/CIK##########.json`

Then, per group:

| Group | Verified when |
|---|---|
| identity | CIK submissions `tickers` contains the ticker; submissions `name` equals the tracker name after removing case, punctuation and legal suffixes (Inc, Ltd, Corp, Corporation, Holdings, Co, plc, N.V., S.A.); no Form 15 or Form 25 filed in the last 400 days |
| revenue.latest / revenue.prior | The displayed dollar value equals a 10-Q or 10-K USD fact for that exact period, or for a derived fiscal Q4, equals the 10-K annual fact minus the three filed quarters; the prior-year value and growth (one decimal) recompute exactly; `releaseDate` equals the filing date; `period` text matches |
| revenue staleness (both) | No revenue concept in the raw facts has a quarter ending later than the displayed latest quarter; the newest 10-Q or 10-K in submissions was filed on or before the displayed `releaseDate` |
| secEvents | Every tracker event for the supplier with an sec.gov source maps to an accession present in submissions with the same filing date; every in-window 8-K whose items include a tracked code is represented by an event on that filing date |

The certified events window is the SEC filing run's own window (`filingRun.json` `windowEnd` back 365 days). Today the site's event list instead ends at `runStatus.lastChecked`, the earlier of the laptop collector and the SEC refresh; Phase 2 must render certified SEC events on the SEC window.

Certified event claims cover the filing date, the filing's presence in the SEC index, and completeness of tracked forms and items. The prose of hand-collected events is not machine-verified; Phase 2 must show that distinction.

A group that fails gets no proof. The gate then fails that group and the run is held, as D-85 requires.

Proof shape is exactly what `evaluateRefresh` checks: `valueSha256` over the sorted candidate fields, `discovery` from the submissions fetch with scope `company-or-parent`, and `evidence` entries with method `structured-validation`, the source hash, a locator (concept, period, accession) and a short excerpt.

### 3. Runner and gate

- `web/scripts/certify-sec.ts`: builds candidate fields from the current tracker data, runs the verifier, writes `web/src/data/generated/certifiedCoverage.json` and `certifiedVerification.json`.
- `web/scripts/certify-gate.ts`: runs `evaluateRefresh` with the certified contract, coverage and verification; writes `.collect/certified-attempt.json`; exits 0 only at 100%.
- npm scripts: `certify:sec`, `certify:gate`.

### 4. Fixes to the producer

- `selectRevenueFacts`: among candidate concepts with 10-Q or 10-K USD facts, pick the one with the newest period end; tie goes to priority order.
- `filing-events.ts`: add 8-K Item 2.03 (type `debt`, "creation of a direct financial obligation"), Forms 25 and 25-NSE (type `going-concern`, "notification of removal from listing"), and DEFM14A and PREM14A (type `acquisition`, "proxy statement for a proposed merger"). Late-filing notices (NT 10-K, NT 10-Q) need a new event type and a display label, so they move to Phase 2. Debt amount and purpose need text extraction from the filing; also Phase 2.

### 5. Tests

- Contract supplier set equals the derived set.
- Verifier unit tests on fixture companyfacts and submissions: a matching value passes; a changed value, a newer concept, a newer 10-Q, a missing 8-K event, a Form 25 and a mismatched name each fail.
- `selectRevenueFacts` picks the newest concept.
- Existing 271 data tests still pass.

## Done when

`npm run certify:sec && npm run certify:gate` passes 100% on live SEC data from this repo, all data tests pass, and an independent reviewer confirms there is no denominator gaming or self-certification.

## Out of scope for Phase 0

Scheduling and workflows (Phase 1), site display of the two tiers and removal of run-status panels (Phase 2), email (D-92 workstream), private-company data.

## Audit and fixes (2026-10-15)

An independent auditor (separate agent, no prior context) returned "sound with fixes". All required fixes but one are applied; the open one is listed below.

| Audit finding | Fix |
|---|---|
| Gate trusted the copied coverage values; a value changed after certification still passed | `certify-gate.ts` re-derives every claim from the build inputs (`sec-verify/candidates.ts`) and refuses drift. Tested by changing CrowdStrike revenue after certification: refused |
| Stale prior quarter could pass | `verifyPriorAdjacent`: prior must be the quarter immediately before latest |
| Event dates barely checked; any same-day event covered a missed item | Events anchor to a cited filing (8-K report date or filing date; 10-Q/10-K period); evidence publication date must equal the SEC filing date; every tracked item needs an event of a matching type or citing the accession |
| Displayed fields outside certification were unstated | 8-quarter table certified as `revenue.history`; remaining uncertified fields listed in the contract's `notCertified` |
| Evidence dates mismatched filing dates | Fixed TR-varonis-2, TR-okta-1, TR-rapid7-4 to SEC filing dates |
| Placeholder locator/excerpt accepted | Runner refuses missing locator/excerpt; gate refuses placeholders |
| Raw responses not archived | Saved by SHA-256 under `.collect/sec-archive/` (Phase 1 uploads them as workflow artifacts) |
| Verifier copies the producer's XBRL rules | Stated in the contract policy: this is a reproducibility check against SEC data, not a second methodology. Site wording must say "re-derived from SEC filings", not "independently verified". **Open:** a second oracle (for example SEC frames) is a Phase 1 candidate |

The stricter event rules also found a real gap: the filing-events generator skipped any 8-K item on a date that already had a hand-collected event, of any type. Palo Alto Networks' 2025-11-19 officer change (Item 5.02, filed with the Chronosphere announcement) and a 2026-02-11 debt filing were missing. Dedupe is now by date and type.

Re-audit: fixes 1, 2, 4 and 5 closed; fix 3 had two small holes (a cited accession counted regardless of type; a loose 10-Q/10-K anchor), both fixed in a third pass. Fix 6 archive is local until Phase 1 uploads it. Fix 7 (second oracle) open and disclosed.

Result after fixes: 80 of 80 claims (16 suppliers, 5 groups) on live SEC data, 279 data tests pass, build passes, production data unchanged.
