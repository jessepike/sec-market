---
id: SEC-MARKET-AUTO-002-P0
version: 0.1
state: in build
created: 2026-10-15
parent: SEC-MARKET-AUTO-002 (docs/active/automation-portfolio-proposal-2026-10-15.md)
decisions: D-89 (certified scope), D-85/D-86 (100% gate, no self-certification), D-96 (cadence)
---

# Phase 0: make the 100% gate passable for the SEC filers

## Goal

A run with no human and no AI produces a certified snapshot of the SEC filers that passes `evaluateRefresh` at 100%, using primary SEC data only. Phase 0 proves the gate can pass. It does not schedule anything, publish anything, or change the site. Scheduling is Phase 1; the site's tier display is Phase 2.

## What the code review found

- `evaluateRefresh` in `web/scripts/refresh-publication-gate.mjs` is generic. It requires one proof per supplier × group listed in the contract it is given. A narrower contract needs no gate change.
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

A group that fails gets no proof. The gate then fails that group and the run is held, as D-85 requires.

Proof shape is exactly what `evaluateRefresh` checks: `valueSha256` over the sorted candidate fields, `discovery` from the submissions fetch with scope `company-or-parent`, and `evidence` entries with method `structured-validation`, the source hash, a locator (concept, period, accession) and a short excerpt.

### 3. Runner and gate

- `web/scripts/certify-sec.mjs`: builds candidate fields from the current tracker data, runs the verifier, writes `web/src/data/generated/certifiedCoverage.json` and `certifiedVerification.json`.
- `web/scripts/certify-gate.mjs`: runs `evaluateRefresh` with the certified contract, coverage and verification; writes `.collect/certified-attempt.json`; exits 0 only at 100%.
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
