# Blind score: Security Market Pulse preview, rubric v3.0

- **Deployment:** https://security-market-pulse-git-preview-pikeholdings.vercel.app/
- **Commit served:** `a8d3976` (origin/preview head at scoring time; response `last-modified: Sat, 26 Sep 2026 18:12:33 GMT`, headers in `evidence/home.headers`)
- **Date:** 2026-09-26 (captures 18:12 to 18:35 UTC)
- **Scorer:** Claude Opus 5.5 (`claude-opus-5-5`), blind. No score file, RUN-STATE file, report under `docs/archive/2026-10-refresh-gate/auto-001/`, `decisions.md` or `status.md` was read.
- **Rubric:** `docs/archive/2026-09-weekly-issue/fable-run/site-rubric.md` v3.0

## Result

**Composite: 59.8 / 100 (26 Sep 2026). Not fit for purpose: blocker 1 (mislabelled figure) and blocker 2 (stale beyond the line).**

| # | Dimension | Weight | Score | Points |
|---|---|---|---|---|
| D1 | Freshness without fail | 22 | 2 (freshness cap applies, max 3) | 8.8 |
| D2 | Coverage | 15 | 5 | 15.0 |
| D3 | Deciding footing from facts alone | 20 | 4 | 16.0 |
| D4 | Evidence legibility | 13 | 2 | 5.2 |
| D5 | Trust | 12 | 3 | 7.2 |
| D6 | Density and scanability | 4 | 2 | 1.6 |
| D7 | Phone | 4 | 2 | 1.6 |
| D8 | Accessibility | 4 | 2 | 1.6 |
| D9 | Performance | 3 | 2 | 1.2 |
| D10 | Machine legibility | 2 | 3 | 1.2 |
| D11 | Craft | 1 | 2 | 0.4 |
| | | 100 | | **59.8** |

Caps: the **freshness cap applies** (Snyk, below: the shown "last round" is more than three years older than a round Snyk itself announced), so D1 cannot exceed 3; it scores 2 on its own tests anyway. The **coverage-gap cap does not apply**: all 12 domains list suppliers, and endpoint, identity and managed security are all present.

## Evidence files

All under `docs/archive/2026-10-refresh-gate/auto-001/score3/opus/evidence/`.

- `home.html`, `route-corrections.html`, `route-issues.html`, `route-issues-2026-w36.html`, `route-thesis.html`: served HTML, fetched with curl.
- `home-{1440,390,320}-fold.png` and `-full.png`, `corrections-*-full.png`, `table-first-{1440,390}.png`, `row-expanded-{1440,390}.png`, `src-popover-1440.png`, `deeplink-*.png`, `home-320-network.png`, `focus-sort-390.png`: renders from Playwright 1.62.1 with Chromium in the OrbStack dev VM.
- `capture.mjs` → `capture.json`: DOM measurements, axe-core 4 (wcag2a/aa, 21a/aa, 22aa, best-practice) on `/` and `/corrections/` at 1440 and 390, and a 40-stop Tab pass at both widths.
- `interact.mjs` → `interact.json`: source drawer, row expand, column sort, deep links.
- `dump-drawers.mjs` → `drawers.json`: every evidence drawer on the tracker (81 rows).
- `evidence-library.txt`: the 143 evidence-library items, from served HTML.
- `sec/`: SEC exhibits and EDGAR `submissions` JSON, fetched with User-Agent `SecurityMarketPulse-scorer jesse@keatingpike.com`.
- `web/`: Wikipedia and company newsroom pages used for the staleness checks.
- `judgment-grep.txt`: judgment-language grep across the served HTML of every live and archive route.
- `lighthouse/lh-{mobile,desktop}-{1,2,3}.json`: Lighthouse, three runs per profile, in the VM.
- `bundle.js`, `site.css`: the served assets, used to read the run-status logic.

## Fit-for-purpose blockers

**1. Mislabelled figure: FAIL.** Snyk's "Ownership or last round" cell reads `Series F (plus extension) $605M (initial close $530M plus extension $75M) · Sep 2021`. Snyk's own GlobeNewswire release of 24 Jan 2023 ("Snyk Secures Strategic Investment from ServiceNow…", `web/` fetch) says the ServiceNow investment "comes on the heels of Snyk's announcement of $196.5 million in Series G investment in late 2022." Axios (13 Dec 2022) and Wikipedia (`web/snyk-wiki.html`) agree. The cell is wrong about which round was last and when. The drawer admits "no funding round after 2021 was found in Snyk's newsroom" but still publishes the label.

Twenty-one other figures matched their sources exactly. Two further defects are recorded, though neither is needed for the fail:
- Ping Identity shows `0` events in 12 months, but Ping completed its Keyless acquisition on 8 Jan 2026 (Pulse 2.0, 8 Jan 2026; Finovate, 3 Nov 2025, on the announcement).
- Dragos is labelled "Acquired by Accenture plc", when Accenture's own release describes a majority investment.

**2. Stale beyond the line: FAIL.** The same Snyk cell is more than three years older than the round Snyk itself announced (late 2022) and the investment it announced on 24 Jan 2023. Ping's `ARR $800M (approaching)` comes from Nov 2024, and its own drawer says "treat as stale". I found no newer Ping ARR figure, so Ping does not trip this blocker on its own. It is shown in the table with no period at all.

**3. Judgment on a live page: PASS.** `judgment-grep.txt` covers `/` and `/corrections/`. Every hit is self-description ("No stances, rankings or forecasts"), domain definitions ("security posture management"), the sourcing ladder ("weakest rung", "strongest first"), or a correction quoting the withdrawn word "fastest" in order to withdraw it. No supplier is characterised. Vendor puffery appears only inside quoted source excerpts in the drawers, for example "Torq, the established agentic security operations leader". Those are quotations, not the site's voice, but they are worth trimming.

**4. Run-status line misstates what happened: PASS, with a defect.** The line reads: "Figures checked 26 Sep 2026. Filings complete for all 14 public suppliers; company news pages could not be read for 28 of 74 suppliers." The claimed state, incomplete with the failed sources named, is true. The served bundle shows `collectorRun.state: "incomplete"`, 28 `failedSources`, and an EDGAR refresh dataset of 14 CIKs with `failures: []`, generated at 2026-09-26T18:08Z.

The defect is that the page shows **18** rows marked "Public ·". Commvault, JFrog, Check Point and Trend Micro are outside the 14-company filing collection, so "all … public suppliers" overstates coverage. Commvault's 8-K of 24 Sep 2026 (a director appointment) is not reflected in its events. Okta's 8-K of 18 Sep 2026 (a director resignation) is also absent, although Okta is inside the 14 and Rapid7's comparable board resignations were counted. A stricter reader could fail this blocker on plain inconsistency; I pass it because the declared state is correct.

**5. Accessibility failure: PASS.** axe reports 0 violations of any impact on `/` and `/corrections/` at 1440 and 390 (`capture.json` keys `axe-*`). The page is operable by keyboard: skip link first, then nav, the "Which sources failed" summary, domain jump links, sort buttons and source buttons (`kbd-home-*`).

## Figures checked against primary sources (21 matched, 1 wrong)

| Supplier | Shown | Source | Match |
|---|---|---|---|
| CrowdStrike | +26% Q Jul 26; ARR $5.84B | 8-K ex99.1, 26 Aug 2026: "Total revenue was $1.47 billion, a 26% increase"; "ARR … grew 25% … to $5.84 billion as of July 31, 2026" | yes |
| Palo Alto Networks | +34% Q Jul 26, filed 1 Sep; NGS ARR $9.10B | ex991q426: "grew 34% year over year to $3.41 billion"; "grew 63% … to $9.10 billion"; EDGAR 8-K 2.02 filed 2026-09-01 | yes |
| Palo Alto Networks, prior | +31% Q Apr 26 | Q3 FY26 ex99.1: "Total revenue for the fiscal third quarter 2026 grew 31%" | yes |
| SentinelOne | +21%; ARR $1.218B | "revenue grew 21% to $292 million"; "ARR) grew 22% to $1,218 million" | yes |
| Check Point | 1% Q Jun 26; $674M | 6-K zk2635799: "Total Revenues: $674 million, a 1 percent increase" | yes |
| Cloudflare | 36% Q Jun 26; $696.1M | "revenue totaled $696.1 million, representing an increase of 36%" | yes |
| Cloudflare, prior | 34% Q Mar 26 | Q1 ex99.1: "$639.8 million, representing an increase of 34%" | yes |
| Fortinet | 26% Q Jun 26; Billings $2.37B | "Total revenue $2,047.9 / $1,630.0" (= +25.6%); "Billings grew 33% … to $2.37 billion" | yes |
| Fortinet, prior | 20% Q Mar 26 | Q1: "$1,849.6 / $1,539.7" (= +20.1%) | yes |
| Netskope | 29% Q Jul 26; ARR $899M | "Q2 revenue increased 29% … to $221 million"; "ARR grew 27% … to $899 million" | yes |
| Zscaler | 25% Q Jul 26; ARR $3,771M | "Revenue: Grew 25% … to $898.2 million. ARR: Grew 25% … to $3,771 million" | yes |
| Okta | 11% Q Jul 26; cRPO $2.585B | 10-Q: revenue 805 vs 728 (+10.6%); "Current remaining performance obligations $2,585" | yes |
| Okta, prior | 11.2% Q Apr 26 | Q1 ex99.1: "$765 million, an increase of 11%" | yes (rounding style differs) |
| SailPoint | 16.8% Q Jul 26; prior 21.5% Q Apr 26 | 10-Q: 308,813 vs 264,359 (+16.8%); Q1 drawer, 10-Q sail-20260430 | yes |
| Commvault | +11% Q Jun 26; Sub. ARR $1,054M | "$314,131 11%"; "Subscription ARR … $1,054 million, up 22%" | yes |
| Rubrik | +38%; Sub. ARR $1.66B | "revenue grew 38% … to $427.3 million"; "Subscription ARR grew 33% … to $1.66 billion" | yes |
| Varonis | +18.3% Q Jun 26; SaaS ARR $726.0M | "$180.0 million, compared with $152…"; "Total SaaS ARR was $726.0 million" | yes |
| Varonis, prior | +27% Q Mar 26 | Q1 ex99.1: "$173.1 million, compared with $136…" (= +27%) | yes |
| Qualys / Tenable / Rapid7 | +11% / +8.6% / −1.5% (prior −0.3%) | "$182.2 million"; "$268.5 million, an 8.6% increase"; "$210.9 million, a decrease of 1.5%"; Q1 "a decrease of 0.3%" | yes |
| JFrog | +29%; cloud $87.5M | "Total Second Quarter Revenues of $163.8 million; up 29%"; "Cloud revenue equaled $87.5 million" | yes |
| Snyk | last round Series F Sep 2021 | Snyk release, 24 Jan 2023: Series G $196.5M, late 2022 | **no** |

**Fiscal-period labels (3 or more required, all correct).** CrowdStrike "Q Jul 26" is Q2 FY2027, ended 2026-07-31. Commvault "Q Jun 26" is Q1 FY2027, ended 2026-06-30. SailPoint "Q Apr 26" is Q1 FY2027, ended 2026-04-30. Palo Alto "Q Jul 26" is Q4 FY2026. The "filed" dates in the table are 8-K earnings-release dates, not 10-Q dates (CrowdStrike 8-K 26 Aug, 10-Q 27 Aug). That is acceptable, but a reader will see the what-changed list say "CrowdStrike filed its 10-Q" on 27 Aug.

**Segment rows (every one checked).**
- Microsoft Defender for Endpoint, "Segment of Microsoft": the source is the investor landing page, not a document.
- Google SecOps, "Segment of Alphabet": the Alphabet Q2 8-K confirms Google Cloud $24.8B, +82%, with no SecOps line.
- Palo Alto Networks Cortex XSIAM shows the bare word "Segment" with no parent named. The source is the 10-K filing index.
- Splunk, "Segment of Cisco Systems": the Cisco 8-K ex99.1 of Mar 2024 confirms the close.
- Microsoft Entra ID, "Segment of Microsoft": the FY26 10-K is cited.
- CrowdStrike Falcon Exposure Management shows the bare word "Segment". Its source is CrowdStrike's earnings release, which says nothing about the product.
- Check Point Email Security, "Segment of Check Point…, renamed…": the Q2 release and the rename blog are cited.
- Microsoft Defender for Office 365, "Segment of Microsoft": the FY26 10-K is cited.
- GitHub Advanced Security shows ownership "–", when it is plainly a Microsoft segment. Its only event is dated "31 Dec 25" in the table, but the drawer's source is dated 11 Aug 2025.

No segment row shows a revenue figure, which is correct. Three segment rows are under-labelled.

**Event counts for private suppliers (7 checked).** Each was checked against the evidence library, the drawer and the company's own page.
- Torq 2: Series D, 9 Jan 2026 (torq.io, 200) and the Jit acquisition, 19 May 2026. Correct.
- Upwind 2: Series B, 26 Jan 2026 and Aegis, 23 Sep 2026. Correct.
- Delinea 3: StrongDM announced 15 Jan and completed 5 Mar 2026, and the CFO appointment on 23 Sep 2026. Correct.
- Cyera 5: 8 Jan, 23 Apr, 10 Jun, 3 Sep and 22 Sep 2026. Correct.
- Veeam 2: Securiti AI announced 21 Oct 2025 and completed 11 Dec 2025. Correct.
- Optiv 2: lender agreement amendment, 8 May 2026, and ACT sale, 2 Jun 2026. Correct. The debt amendment is visible only in the evidence library, not in the table.
- **Ping Identity 0: wrong.** Keyless completed 8 Jan 2026.

**Staleness candidates (4 checked).**
- **Snyk: stale. Blocker.**
- Ping ARR from Nov 2024: stale per its own drawer, and no newer figure found.
- Abnormal ARR from Aug 2024: the newsroom lists no later ARR release; the newest corporate item is a CFO appointment in Jan 2025, outside 12 months. Not stale by the rule.
- Cato ARR $415M: newer than the Feb 2026 figure. The table shows no period for it, and its "latest results, 24 Feb 26" event ignores the Jul 2026 figure.

EDGAR `submissions` for all 17 SEC filers show no earnings release newer than the one shown.

## D1: Freshness without fail, score 2

Level 3:
1. **Yes.** "company news pages could not be read for 28 of 74 suppliers" states incomplete and names the source class without expanding. The per-supplier list is behind a closed `<details>`. A strict reading of "names which sources" could fail this test.
2. **Yes.** "Figures checked 26 Sep 2026" is on the first screen at 1440 and at 390 (`home-1440-fold.png`, `home-390-fold.png`).
3. **No.** Snyk's last round is 3+ years older than Snyk's own later announcement.
4. **Yes.** "What changed in the last 30 days" is open, with 26 dated rows. The bundle holds the empty state "No tracked change in the last 30 days."

Level 5 (credit waiting):
1. **No.** Only the growth cell carries a fact date ("filed 26 Aug"). Prior quarter, own metric and ownership carry none in the table.
2. **Yes.** For example, "Armis Security — newsroom blocked automated reading".
3. **Yes.** The newest fact is dated "24 Sep 26" at the top of the what-changed list.
4. **Yes.** "SEC filings refresh daily; press, funding and distress facts refresh twice a week" is in the open footer, and nothing contradicts it.

To raise by one: fix the Snyk round, and add a staleness check that flags any "last round" or own metric older than the company's newest release.

## D2: Coverage, score 5

Level 3:
1. **Yes.** "What this site covers" lists 12 domains, each with one sentence, on the front page.
2. **Yes.** Domain counts run from 6 to 7.
3. **Yes.** A "Not covered" list of 7 items is open.
4. **Yes.** The Events column shows a count, the latest type (debt, restructuring, rating, divestiture, acquisition) and a date, or a plain "0". Ownership shows acquired, merged or PE-owned. Caveat: only the latest event is shown, so Optiv's debt amendment is invisible in the table.

Level 5:
1. **Yes.** `#domain-*` and `#s-*` resolve after hydration (`interact.json` deeplink). Rows land about 26 px under the sticky header.
2. **Yes.** "12 domains, 74 tracked suppliers."
3. **Yes.** "being listed is not a recommendation and being absent is not a criticism."
4. **Yes.** An absent supplier and a tracked supplier showing "0" are visibly different.

To raise by one: already at the maximum. Correct the Ping count and show an ownership fact where one exists (Arctic Wolf, Expel, BeyondTrust, Delinea, Cohesity and Aqua show "–").

## D3: Deciding a supplier's footing from facts alone, score 4

Level 3:
1. **Yes.** One table per domain, with revenue growth on one metric and quarterly periods.
2. **Yes.** A domain jump index of 12 links works at both widths.
3. **Yes.** At 1440 the CrowdStrike row shows its figure, prior quarter, ARR, ownership and latest dated event.
4. **Yes.** The default order is alphabetical (`aria-sort="ascending"` on Supplier), with no ranking words.

Level 5:
1. **No.** A median row appears in 6 domains only. Security operations, email, application security and AI security each contain a public supplier but show no reference point and no note.
2. **Yes.** Every column sorts in both directions (`interact.json` `sort-1440`).
3. **Yes.** From the jump link to the row, everything is in one row.
4. **No.** At 390 a row is collapsed to one figure, and a tap is needed for the rest (`row-expanded-390.png`).

To raise by one: show every column at 390, for example as a two-line row, and give every domain a reference point or a stated "only one public supplier".

## D4: Evidence legibility and reconstructability, score 2

Level 3:
1. **Yes.** All 207 non-empty figure cells have a `src` control (script check over `drawers.json`: 0 missing).
2. **No.** Several sources are not checkable documents:
   - Sophos's Moody's downgrade links to `app.researchpool.com/.../moodys-investors-service`, which returns HTTP 403. It is a distress fact, and it breaks the site's own ladder ("most reliably read on the rated company's own newsroom").
   - Both Ping cells link to the newsroom index.
   - Defender for Endpoint links to `microsoft.com/en-us/investor`.
   - Cortex XSIAM links to a filing index.
3. **Yes.** The revenue-growth definition sits above the tables, and "How this is built" is one click.
4. **Yes.** "filed 26 Aug" and the drawer's publication date are separate from "Figures checked 26 Sep 2026".

Level 5:
1. **Yes.** The drawer shows publisher, publication date and period in one click, with the page kept behind it (`src-popover-1440.png`).
2. **No.** Trend Micro's growth and Qualys's and Tenable's prior quarter show a bare "–" with no reason. Qualys and Tenable both reported Q1 2026.
3. **Yes.** The five-rung sourcing ladder.
4. **No.** The drawer has no "report this figure" link.

The drawers also expose internal labels ("Packet label SEC-MARKET-AUTO-001-STEP5 / TR-crwd-1").

To raise by one: replace the aggregator and index-page sources with the actual documents.

## D5: Trust, score 3

Level 3:
1. **Yes.** See blocker 3.
2. **Yes.** "Collected, checked and published automatically" in the intro, and "no human approval step" in "How this is built".
3. **Yes.** `/corrections/` has two dated entries.
4. **Yes.** "Send a correction or a question" and a mailto link are open in the footer.

Level 5:
1. **No.** "Run by Jesse Pike" says nothing about any relationship to the tracked suppliers.
2. **No.** Nothing says how suppliers are chosen, or whether partners and competitors meet one evidence standard.
3. **Yes.** `/issues/` and `/thesis/` say "discontinued on 25 September 2026 … kept unchanged as a dated record". One weakness: the w36 issue page carries the live tagline ("published automatically, with no stances…") directly above a signed "lag call holds".
4. **No.** For the tracker, "a wrong entry there is fixed in place". Only issues keep the original wording.

To raise by one: add an operator-relationship and selection-method statement, one click from the front page.

## D6: Density and scanability, score 2

Level 3:
1. **Yes.** Every domain table fits one 1440×900 screen (281 to 608 px).
2. **No.** The figures use `tabular-nums`, but the growth column mixes "+34%" with "36%", "1%" and "25%", and "11%" with "11.2%". The Network and SASE column does not align.
3. **No.** Table text is 13 px. Intro prose runs about 94 to 96 characters per line, and what-changed rows about 190.
4. **Yes.** "0" sits against "7 · latest exec-change, 24 Sep 26".

Level 5:
1. **No.** The page is 9,924 px, and the coverage statement is about 7,000 px down.
2. **Yes.** Fixed-column tables.
3. **No.** The 10 px header tagline and 12 px metadata sentences.
4. **Yes.** One full domain table fits on one screen at 1440.

To raise by one: format signs and decimals consistently, and set table text at 14 px.

## D7: Phone, score 2

Level 3:
1. **No.** The 390 first screen shows the run status but no suppliers (`home-390-fold.png`).
2. **Yes.** The first content starts at 174 px of 844 (20.6%).
3. **No.** Domain links are 20 px tall, footer links 15 to 19 px, and the "Which sources failed" summary is 22 px (`capture.json` `home-390.smallTargets`).
4. **Yes.** `scrollWidth` equals `clientWidth` at 390 and at 320.

Level 5:
1. **No.** A tap per row is needed.
2. **No.** Text is 13 px, with 11 to 12 px metadata.
3. **Yes.** The jump index works the same way.
4. **No.** Collapsed rows hide the prior quarter, own metric and events.

At 390 the "+" chevron wraps onto its own line under long rows.

To raise by one: shorten the hero so a domain's first rows reach the first screen, and pad the links to 24 px.

## D8: Accessibility, score 2

Level 3:
1. **Yes.** Zero axe violations.
2. **No.** At 390 the table header is visually hidden (`clip: rect(0,0,0,0)`), but its 6 sort buttons per domain, 72 in all, stay in the tab order. Focus lands on invisible controls at x = −15 px (`focus-sort-390.png`, Tab stops 17 to 22 in `kbd-home-390`). The 1440 pass shows a visible 2 px teal outline on every stop.
3. **Yes.** No color-contrast findings.
4. **Yes.** Reflows at 320.

Level 5 (credit waiting):
1. **Yes.** Zero violations of any impact.
2. **No.** `src` buttons are 27×19 px.
3. **Yes.** The skip link is stop 1, and a domain link is at stop 10 at 1440 and stop 5 at 390.
4. **No.** There are 27 `time[datetime]` elements, but the table dates are plain text.

To raise by one: remove the hidden sort buttons from the tab order at narrow widths, or show them.

## D9: Performance, score 2

These are Lighthouse lab medians of 3 runs in the VM (`lighthouse/`).

Level 3:
1. **No.** Mobile LCP is 4.00 s.
2. **No.** Desktop CLS is 0.144 on all three runs (mobile 0). The preview-only `vercel.live` feedback script may contribute.
3. **Yes.** Mobile TBT is 70 ms.
4. **Yes.** Desktop LCP is 0.96 s.

Level 5:
1. **No.**
2. **Yes.** Transfer is 296 KB and JavaScript 154 KB.
3. **Yes.** The HTML is 21.8 KB compressed.
4. **No.** The Google Fonts CSS is render-blocking, at 1,010 ms on mobile.

To raise by one: self-host or preload the fonts, and find the desktop layout shift.

## D10: Machine legibility, score 3

Level 3:
1. **Yes.** All 215 figure values are in the served HTML.
2. **Yes.** JSON-LD is valid: `Report`, publisher `Organization`, `dateModified` 2026-09-26.
3. **Yes.** `feed.xml` is linked in `<head>`, and `robots.txt` points to the sitemap.
4. **Yes.** No empty headings and no duplicate ids in the served HTML.

Level 5:
1. **No.** There is no tracker JSON. `/tracker.json` and similar return 404, and only the legacy issue JSON exists.
2. **No.**
3. **No.** The publisher has only a `url`, with no `@id` or `sameAs`.
4. **No.** `robots.txt` is `Allow: /` plus a sitemap, which amounts to the default.

The JSON-LD `reportNumber` still reads "SEC-MARKET-SIG-002 v0.2".

To raise by one: publish a tracker JSON endpoint with run status, domains and per-figure ids.

## D11: Craft, score 2

Level 3:
1. **No.** There are two sans families (IBM Plex Sans and Archivo) plus IBM Plex Mono, and 14 font sizes.
2. **No.** Teal links and focus, a crimson run-status line and a gradient logo mean more than one accent.
3. **Yes.** Nothing clips at 1440, 390 or 320, though the chevron wraps at 390.
4. **Yes.**

Level 5:
1. **Yes.** The status reads without color.
2. **No.** Growth formatting is inconsistent.
3. **No.** The 42 px Archivo hero reads as marketing chrome.

To raise by one: use one sans family and cut the type scale to 6 sizes.

## Scorer notes

- The run-status count "14 public suppliers" against 18 "Public ·" rows is the likeliest place for two scorers to split on blocker 4.
- D1 level-3 test 1 turns on whether naming the failed source class counts as naming "which sources". I read it leniently.
- Nothing was committed.
