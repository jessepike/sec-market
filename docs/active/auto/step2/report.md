# Step 2 report — SEC EDGAR daily revenue runner

**Artifact:** `SEC-MARKET-AUTO-001` step 2, per `docs/active/autonomy-coverage-plan.md` §4–5
(D-76/D-77). Branch `mon/edgar`, built in the worktree at
`/Users/jessepike/code/projects/sec-market-wt/edgar`.

A plain script pulls structured GAAP revenue for every US-listed security supplier that files
10-Q/10-K with the SEC, straight from EDGAR's XBRL `companyfacts` API. No model is in the loop, so
it cannot invent a number. Nothing here is wired into a page yet — this step only produces and
validates the data file.

## 1. Registry (`web/src/data/edgarRegistry.ts`)

14 suppliers, each with a CIK looked up against `https://www.sec.gov/files/company_tickers.json`
and cross-checked against that filer's own `data.sec.gov/submissions/CIK##########.json` (name and
fiscal year end confirmed to match):

| id | Name | Ticker | CIK | Fiscal year end |
|---|---|---|---|---|
| crwd | CrowdStrike | CRWD | 1535527 | Jan 31 |
| zscaler | Zscaler | ZS | 1713683 | Jul 31 |
| panw | Palo Alto Networks | PANW | 1327567 | Jul 31 |
| fortinet | Fortinet | FTNT | 1262039 | Dec 31 |
| cloudflare | Cloudflare | NET | 1477333 | Dec 31 |
| okta | Okta | OKTA | 1660134 | Jan 31 |
| sailpoint | SailPoint | SAIL | 2030781 | Jan 31 |
| s1 | SentinelOne | S | 1583708 | Jan 31 |
| rubrik | Rubrik | RBRK | 1943896 | Jan 31 |
| varonis | Varonis | VRNS | 1361113 | Dec 31 |
| netskope | Netskope | NTSK | 2063196 | Jan 31 |
| tenable | Tenable | TENB | 1660280 | Dec 31 |
| qualys | Qualys | QLYS | 1107843 | Dec 31 |
| rapid7 | Rapid7 | RPD | 1560327 | Dec 31 |

Ids reuse the supplier ids already implied by `print-<id>` entries in `prints.ts` (e.g.
`print-crwd` → `crwd`) wherever that supplier is already tracked there, so the two data sets join
without a remapping table.

### Unsupported, and why (`unsupported` export in the same file)

- **Check Point (CHKP, CIK 1015922)** — foreign private issuer. Confirmed against its own
  submissions record: it files an annual 20-F (most recent 2026-03-31) and furnishes 6-Ks, never a
  10-Q or 10-K. Its 20-F XBRL only carries annual-duration facts, so there is no discrete quarterly
  revenue in EDGAR structured data for it at all.
- **Cisco security (CSCO, CIK 858877)** — total Cisco revenue is not a security figure, and the
  security product-category split it discloses is tagged with a segment dimension. EDGAR's
  companyfacts API only returns entity-wide, non-dimensional facts — it strips exactly that
  dimension — so the segment figure cannot be pulled by a plain revenue-concept lookup. Fiscal year
  end Jul 25; most recent 10-K 2026-09-02.
- **Akamai security segment (AKAM, CIK 1086222)** — same limitation as Cisco: the security line is
  a disclosed segment, not a top-level GAAP concept, and companyfacts does not expose it. Total
  Akamai revenue is trackable but is not a security figure, so it is left out rather than published
  mislabeled.

## 2. What the runner does

`web/src/data/edgarLogic.ts` holds all the extraction and validation logic, pure and network-free
(matches the existing pattern of `staleReport.ts` behind `report:stale`). `web/scripts/edgar-refresh.ts`
fetches each supplier's `companyfacts` JSON with the descriptive User-Agent from
`docs/active/gather-brief.md` (`SecurityMarketPulse research jesse@keatingpike.com`) at roughly 4
requests/second, and calls the pure logic:

1. Picks the first revenue concept (in priority order — `RevenueFromContractWithCustomerExcludingAssessedTax`,
   then the "including tax" variant, then `Revenues`) that has any 10-Q/10-K USD facts.
2. Keeps facts with an 80–100 day duration as directly reported quarters.
3. Where a fiscal Q4 has no discrete quarterly tag (the normal case — only the 10-K's annual total
   exists), derives it: finds the three preceding quarters by chaining contiguous period dates
   (each quarter starts the calendar day after the previous one ends), then Q4 = annual total −
   (Q1+Q2+Q3), marked `derived: true`.
4. De-duplicates a period that appears more than once (a restated comparative shown again in a
   later filing) by keeping the value from the most recently filed document.
5. Computes YoY growth for the latest quarter and the quarter before it, each against its own
   same-fiscal-quarter figure one year earlier (350–380 day window). A quarter with no matching
   prior year, an unexpected duration, or growth beyond ±80% is flagged, never dropped or silently
   corrected.
6. Records period start/end, value, form, accession number, filed date, and a source URL built
   from the accession (the filing's own index page on sec.gov) for every quarter.

Output: `web/src/data/generated/edgarFacts.json`, committed, with `generatedAt`, each supplier's
last 8 quarters plus computed latest/prior YoY, the `unsupported` list, and a `failures` array
(supplier id + reason) so a bad fetch is visible instead of silently missing. The script exits
non-zero only if more than half of suppliers fail — one or two bad fetches show up in `failures`
without failing the whole run.

## 3. Live run — 2026-09-25

Ran with `npm run refresh:edgar` in the OrbStack dev VM against the real SEC EDGAR API.
**14 of 14 suppliers succeeded, 0 failures.**

| Supplier | Latest quarter end | Revenue | YoY | Prior-quarter YoY | Derived? |
|---|---|---:|---:|---:|---|
| CrowdStrike | 2026-07-31 | $1,470,897,000 | 25.8% | 25.6% | no |
| Zscaler | 2026-07-31 | $898,185,000 | 24.9% | 25.4% | **yes (Q4)** |
| Palo Alto Networks | 2026-07-31 | $3,410,000,000 | 34.5% | 31.1% | **yes (Q4)** |
| Fortinet | 2026-06-30 | $2,047,900,000 | 25.6% | 20.1% | no |
| Cloudflare | 2026-06-30 | $696,061,000 | 35.9% | 33.5% | no |
| Okta | 2026-07-31 | $805,000,000 | 10.6% | 11.2% | no |
| SailPoint | 2026-07-31 | $308,813,000 | 16.8% | 21.6% | no |
| SentinelOne | 2026-07-31 | $291,981,000 | 20.6% | 20.8% | no |
| Rubrik | 2026-07-31 | $427,260,000 | 37.9% | 39.0% | no |
| Varonis | 2026-06-30 | $180,023,000 | 18.3% | 26.9% | no |
| Netskope | 2026-07-31 | $220,541,000 | 29.2% | 27.8% | no |
| Tenable | 2026-06-30 | $268,508,000 | 8.6% | 9.6% | no |
| Qualys | 2026-06-30 | $182,175,000 | 11.0% | 9.8% | no |
| Rapid7 | 2026-06-30 | $210,883,000 | -1.5% | -0.3% | no |

Zscaler and Palo Alto Networks both have a July 31 fiscal year end, so their most recent quarter is
a derived Q4 — no 10-Q tags it directly, only the 10-K's annual total does.

No supplier's figures triggered a flag (no `no-prior-year-match`, `growth-out-of-band`,
`unexpected-duration`, or `fiscal-period-mismatch` across any of the 14 latest/prior pairs).

## 4. Sanity check against primary filings

The task asked for a check against press releases; this session's web-search budget was exhausted
partway through, so the check instead went straight to each company's own SEC filing (the primary
source a press release is itself summarizing — arguably a stronger check):

- **CrowdStrike, quarter ended 2026-07-31:** fetched the filing index
  (`sec.gov/Archives/edgar/data/1535527/000153552726000031/`) — period of report confirmed as
  2026-07-31 — then the 10-Q document itself. Its own MD&A states "Total revenue $1,470,897
  [thousand] ... increased by $301.9 million, or 26%" for the quarter. That matches the extracted
  value exactly ($1,470,897,000) and the extracted YoY (25.8%, which the filing rounds to 26%).
- **Okta, quarter ended 2026-07-31:** filing index confirmed period of report 2026-07-31; the 10-Q
  shows "Total revenue 805 728" (current vs. prior-year quarter, in millions) with "$77, 11%"
  change. The extracted prior-year comparator the pipeline computed ($728,000,000, implied by the
  10.6% YoY on $805,000,000) matches the filing's own comparative figure exactly.
- **Zscaler, quarter ended 2026-07-31 (derived Q4):** filing index confirmed period of report
  2026-07-31 on the 10-K. The 10-K states FY2026 revenue of $3,352,523,000. Summing the pipeline's
  four FY2026 quarters (Q1 $788,112,000 + Q2 $815,751,000 + Q3 $850,475,000 + derived Q4
  $898,185,000) equals $3,352,523,000 exactly — the Q4 derivation is exact, not approximate.

## 5. Tests

`web/tests/edgar-logic.test.ts`, 17 tests against `web/src/data/edgarLogic.ts`, using a saved
fixture (`web/tests/fixtures/edgar-companyfacts-fixture.json`, a hand-built two-fiscal-year
companyfacts shape) and no network:

- Quarter/annual duration classification (`daysBetween`, `isQuarterlyDuration`, `isAnnualDuration`).
- Filing index URL construction.
- Revenue-concept selection, including the "no concept matches" case.
- Q4 derivation across two fiscal years, matched against hand-computed expected values.
- Restatement de-duplication: the fixture carries the same quarter twice (original $110M, restated
  $115M filed later) and the test confirms the later-filed value wins.
- Same-fiscal-quarter-prior-year matching and YoY computation for both the latest and prior
  quarter.
- Flag behavior: no-prior-year-match, and growth beyond ±80% (flagged, figure kept, not dropped).
- `buildSupplierRecord` end to end from the fixture, and its throw path when no revenue concept is
  found (the shape the refresh script catches to populate `failures`).

Added to `test:data` in `web/package.json`, alongside the ten existing data-test files.

## 6. Full test run

`npm test` in the OrbStack dev VM: lint, `test:data` (all 216 tests across 54 suites, including
the 17 new ones), the full `build` pipeline (verify:edition/panel/integrity/issue/prints,
tsc, client+server build, prerender, seo, feed, verify:dist), and `test:e2e` (37 passed, 1 skipped,
0 failed). Nothing broke.

## 7. What is deliberately not done

- `edgarFacts.json` is not read by any page or component yet — that is step 5 of the plan.
- No auto-publish path exists — the draft workflow at
  `docs/active/auto/step2/edgar-refresh.yml.txt` only fetches, verifies, and commits to a
  short-lived branch, matching where the plan actually is (step 4, the auto-merge path, is not
  built yet).
- `.github/workflows/` was not touched directly — this session's token cannot push there.
