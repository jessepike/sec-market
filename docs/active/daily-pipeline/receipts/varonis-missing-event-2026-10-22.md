# Varonis missing-event correction

Inspected October 22, 2026 Pacific (October 23 UTC). This is a manually checked
public-source data correction; it does not change daily collection acceptance or enable publication.

## Actual production

`https://securitymarketpulse.com/app-release.json` returned revision
`54590be4d91113a50879a8fb5d180441e7d149f4`, rootView `tracker`, releaseKind `certified`,
built `2026-10-18T19:13:57.104Z`. The rendered root references `/assets/index-DFMsvbr-.js`.
Its October 15 Varonis event is a generic Form 8-K Item 5.02 leadership record. The
acquisition agreement is absent; Proofpoint's displayed acquisition event concerns Acuvity.

The current build uses `web/src/data/tracker/events.ts`, `suppliers.ts` and
`web/src/data/evidence.ts` through the certified tracker renderer.
`web/scripts/app-release.mjs` invokes `build:certified`; `web/vercel.json` publishes `dist`.
`web/published-app` is absent. D-102 and the Phase 2 specification document its removal.
Editing a legacy published-app snapshot would not repair the actual root.

## Primary evidence

1. Joint company release, dated October 15, 2026:
   https://www.proofpoint.com/us/newsroom/press-releases/proofpoint-acquire-varonis-creating-global-leader-data-and-ai-security
   HTML SHA-256: `6c712edbfb4aa71e87567f5dc9de15dc6efebb72de73154daff595bbb9b220ca`.
   Explicit HTML publication metadata: `2026-10-15T11:55:41-07:00`; visible date October 15.
   Evidence excerpt is retained in `TR-varonis-proofpoint-agreement`.
   Opening announcement and transaction-details sections support approximately $6.3 billion
   in cash, $49.75/share, expected first-half 2027 closing subject to shareholder/regulatory
   approvals, and separate companies until closing.
2. Varonis CEO announcement, last updated October 15, 2026:
   https://www.varonis.com/blog/proofpoint
   HTML SHA-256: `4d80a9dc7f2208c90281de7748775f0aae565b5796bdd396841893b3a6c096eb`.
   Its opening paragraph confirms the agreement; “What happens next” confirms the
   separate-company and expected-closing conditions.
3. Varonis Form 8-K, report date October 15, 2026, Item 1.01:
   https://www.sec.gov/Archives/edgar/data/1361113/000121390026109904/ea0308610-8k_varonis.htm
   It identifies the signed merger agreement and parties and expected first-half 2027 closing.
   This corroborates the company release; the new event cites the joint release directly.

The missing current event is the Proofpoint agreement. AllTrue.ai is an older, distinct
February 2026 transaction. No AllTrue value or completion assertion was added.

## Correction and limits

Added `EV-varonis-proofpoint-agreement` dated October 15, 2026 and its primary-source
evidence record. Varonis ownership now discloses the agreement and conditions while retaining
`kind: public`, Nasdaq ticker and no `closed` date. Existing facts/events remain intact.
No acquisition completion, certified acquisition claim, forecast, or judgment is asserted.
Generated daily snapshots and historical coverage receipts were not upgraded.

## Checks

OrbStack dev VM: the new agreement regression test and tracker-data suite passed all 20 tests.
`verify-tracker.ts` passed: 12 domains, 74 suppliers, 124 events.
The regression checks dates, amount, price, approvals, continued separate operation, primary
source and public ownership without a closing date.

A broader data-suite attempt passed 206 tests and failed four because this new worktree lacked
local `react`/`tsx` module resolution. This is not a full-suite pass; the integrator must install
dependencies in the VM and run the required suite/build and visual review before pushing.
No push, promotion, production change, credential change, model call or budget reset was performed.
