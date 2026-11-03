# Codex handoff: three visitor-facing data bugs (2026-11-03)

Diagnosis only. Nothing here is fixed yet. Line numbers are against `origin/preview` at `2e44342`.
Live checks were read from https://securitymarketpulse.com/ on 2026-11-03 ("Window ends 2026-11-02").

Rules that apply to every fix below:

- Work on a short branch from `preview`. Run `npm test` from `web/`.
- Render production and your build at 1440px and 390px (`node scripts/shot.mjs`) and say in the commit
  what moved.
- All three fixes change what a reader sees (counts, a chart marker). End each commit with
  `Owner-Review: required`.
- Do not edit or delete hand-collected events or `originals.json` records to make counts drop. Those are
  sourced records; fix how they are counted. Wording changes to hand-collected records go through
  the correction process.
- The live events come from the published daily snapshot, not the committed
  `web/src/data/generated/dailyMarket.json` (that file is dated 2026-10-20 and holds 0 events).
  Reproduce against the current release snapshot.

---

## Bug 1. "Results reported: 0 in last 30 days" while the filter shows 2 results

**Symptom.** The Results tile says `19` / `0 in last 30 days`. Clicking it lists 2 entries: Fortinet
10-Q (2026-10-30) and Commvault 10-Q (2026-10-28). Fortinet's +20.5% for the quarter ended 2026-09-30
is on the growth chart. The October column of the 12-month grid shows no results. Fortinet's directory
card says "0 events in 12 months".

**Root cause.** Two different data sources answer the same question.

- The tiles count `monthEvents` / `yearEvents`, which are `TrackerEvent`s only
  (`web/src/components/MarketDesk.tsx:192-193`, `web/src/data/tracker/presentation.ts:23-24`).
- The change log is `recentChanges()` (`presentation.ts:37-49`). It adds synthetic rows of type
  `'filing'` built from `edgarFacts.json` when no `results` event matches. The filter then maps
  `'filing'` to the Results group (`MarketDesk.tsx:184`). So the filtered list includes filings that
  the tile never counts.
- Nothing turns an SEC quarterly filing into a `results` event. `web/scripts/filing-events.ts:63-71`
  maps 8-K items 5.02, 2.01, 1.03, 2.05, 3.01 and 2.03, but not 2.02 (results of operations), and
  10-Q/10-K are not in `FORM_MAP`. The only `results` events are hand-collected ones or daily
  `revenue`/`arr` facts. Fortinet has no tracker events at all, so the timeline grid
  (`MarketDesk.tsx:131`) and the supplier card (`eventSummaryForSupplier`, `derive.ts:200-206`,
  rendered at `MarketDesk.tsx:173`) also show 0.

**Suggested fix.** Make one source of truth: generate a `results` `TrackerEvent` for each certified
SEC filer's 10-Q/10-K quarter in the trailing 12 months, from `edgarFacts.json` (form, filedDate,
periodEnd, value, sourceUrl). Date it on `filedDate`, rung 1, evidence pointing at the filing index.
Skip it when a hand-collected or daily `results` event already exists for the same supplier and the
same quarter (reuse the matching rule in `recentChanges()`: within 30 days before `filedDate` and the
same `periodEnd`). Text states only the filing facts, for example
"Filed 10-Q for the quarter ended 2026-09-30." Then `recentChanges()` no longer needs the synthetic
`'filing'` branch for these, and the tile, grid, card and log all read `trackerEvents`.

The smaller alternative is to count `recentChanges()` in the tile. It fixes the tile only, not the grid
or the card. Don't do that alone.

Expect the 12-month Results count to rise well above 19 once filings count. That is the correct
number, but it is a visible change: call it out in the commit.

**Acceptance checks.**

1. On a build with the current snapshot, the Results tile's "in last 30 days" number equals the number
   of entries shown when the tile is clicked (2 today: Fortinet, Commvault).
2. For every group, `tile recent count === filtered change-log length`. Add this as a test in
   `web/tests/tracker-presentation.test.ts`.
3. The October 2026 Results cell in the 12-month grid is at least 2.
4. Fortinet's directory card shows at least 1 event in 12 months.
5. No supplier has two `results` events for the same quarter (test).

---

## Bug 2. Varonis/Proofpoint counted three times; Delinea/StrongDM twice

**Symptom.** One deal on 2026-10-15 produces three counted events: Varonis "Acquisition"
(hand-collected), Proofpoint "Acquisition" (daily pipeline) and Proofpoint "Funding" (the Ontario
Teachers' co-investment, daily pipeline). Those are all of October's 2 acquisitions and 1 funding round.
Delinea's StrongDM deal counts twice: announcement (2026-01-15, `EV-delinea-2`) and completion
(2026-03-05, `EV-delinea-3`).

**Root cause.** Events are counted one row per supplier per fact, with no idea of a transaction.

- The daily pipeline keys each event by `factId`, a digest of supplier, predicate, effective date,
  amount, currency, qualifier, event status and scope (`web/scripts/pipeline/validation.py:96-105`).
  Each supplier and each stage of a deal therefore gets its own event
  (`web/scripts/pipeline/snapshot.py:323`).
- `EVENT_TYPES` maps both `funding` and `valuation` predicates to the `funding` type
  (`snapshot.py:11-13`). A co-investment that pays for an acquisition becomes a "funding round".
- Hand-collected and daily events are concatenated with no cross-source check
  (`web/src/data/tracker/events.ts:52-56`). `filing-events.ts` dedupes only against hand-collected events
  of the same supplier and date.
- The tiles and grid count rows (`MarketDesk.tsx:131, 192`).

**Suggested fix.** Count deals, not rows, and keep every row visible in supplier drawers.

1. Add an optional `dealId` to `TrackerEvent` (`events.ts:30-38`). Keep a small hand-maintained map,
   for example `web/src/data/tracker/deals.ts`, from event id to deal id. Seed it with
   `varonis-proofpoint-2026` (the Varonis event, the Proofpoint acquisition event and the Proofpoint
   funding event) and `delinea-strongdm-2026` (`EV-delinea-2`, `EV-delinea-3`). Daily event ids are
   stable (`EV-daily-<factId>`); look them up in the current snapshot.
2. In the tile and grid counts, count each `dealId` once, in the group of its acquisition or
   divestiture event, at the date of its earliest event in the window. Events without a `dealId` count as
   today. The change log and supplier drawers still list every event, so both companies keep their
   history.
3. Add a guard in `web/scripts/verify-tracker.ts`: fail the build when two `acquisition`, `divestiture`
   or `funding` events in the window share a date and an evidence URL, or name each other's supplier,
   and are not linked by a `dealId`. This stops the next big deal from silently double-counting.
4. Optional, pipeline side: in `snapshot.py`, when a `funding` fact and an `acquisition` fact come from
   the same source document, route the funding fact to the review queue
   (reason `FUNDING_WITHIN_ACQUISITION`) instead of publishing it as a round. Only do this if (1) to (3)
   are not enough.

**Acceptance checks.**

1. With the current snapshot, October 2026 shows 1 acquisition and 0 funding rounds in the grid. The
   tile "in last 30 days" shows 1 under acquisitions and 0 under funding.
2. The Varonis and Proofpoint drawers still list their 2026-10-15 events.
3. Delinea/StrongDM counts as 1 acquisition in the 12-month tile. Both dated rows remain in the
   Delinea drawer.
4. A test fixture with two unlinked acquisition events on the same date and same source URL makes
   `npm run verify:tracker` fail.
5. `web/tests/varonis-acquisition.test.ts` still passes unchanged.

---

## Bug 3. Trend Micro's yen growth sits on the USD chart with no marker

**Symptom.** "Reported revenue growth" shows Trend Micro at +13% alongside SEC filers' USD growth. The
+13% is growth in yen. The drawer says so, and the chart's header note says growth is "in each
company's reporting currency", but the row itself carries no marker.

**Root cause.** The basis is stored only as free text in `revenue.latest.growthBasis`
(`web/src/data/tracker/suppliers.ts:28-29`; value in `web/src/data/tracker/originals.json`, Trend Micro
supplier: "JPY net sales; $468 million is the company-reported USD equivalent at 159.47 JPY per USD.").
The chart row only puts it in the hover `title` of the value link (`MarketDesk.tsx:107`). The row's
`aria-label` (`MarketDesk.tsx:102`) and the visible text do not mention it. `revenueGrowthRows()`
(`presentation.ts:57-66`) has no currency field to act on.

**Suggested fix.**

1. Add a structured `growthCurrency?: string` (ISO 4217, for example `'JPY'`) to `RevenuePeriod`. Set
   it for Trend Micro's latest (and prior, if present) period. Leave `growthBasis` as the explanation.
2. In the growth chart, when `growthCurrency` is set and is not `USD`, show a small visible tag next to
   the value, for example `+13% JPY`, and add "growth in Japanese yen" to the row's `aria-label`.
   Use existing chart styles; no new colours.
3. Add a `verify-tracker.ts` rule: a public supplier whose `growthBasis` mentions a non-USD currency
   must have `growthCurrency` set. That catches the next non-US filer.

**Acceptance checks.**

1. At 1440px and 390px the Trend Micro row shows the `JPY` tag beside +13%, with no wrapping or
   overflow at 390px.
2. The row's accessible name includes "Japanese yen" (or "JPY").
3. No other row changes. Compare screenshots before and after.
4. Removing `growthCurrency` from Trend Micro makes `npm run verify:tracker` fail.

---

## Seen in the same review, not in scope here

Leave these for a separate change unless the owner asks: Check Point "1%" without a sign, a Trend Micro
guidance cut filed under Restructuring, "1 events" grammar, stale private-company metrics without an
age cue, and pipeline jargon above the fold. Source:
`market-pulse-site-and-pipeline-review-2026-11-02.md` in the project files.
