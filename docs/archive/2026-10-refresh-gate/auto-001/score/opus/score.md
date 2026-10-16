# Site score: Security Market Pulse, rubric v3.0

- **Deployment scored:** https://security-market-pulse-git-preview-pikeholdings.vercel.app/ (Vercel deployment `dpl_6rDzCXYzydfhBNVjj7oS9jqgKe8K`)
- **Commit served:** `190ecd498594e340c5aef9c5c1a5abd23cd80b92` on `preview` (GitHub deployment record for that SHA, created 2026-09-26T15:00:51Z, Vercel status "success" pointing at the same deployment id)
- **Scoring date:** 2026-09-26
- **Scorer:** Claude Opus 5.5 (`claude-opus-5-5`), blind. No score file, run-state file, auto report, `decisions.md` or `status.md` was read.
- **Rubric:** `docs/archive/2026-09-weekly-issue/fable-run/site-rubric.md`, `SEC-MARKET-FABLE-RUBRIC` v3.0

## Result

**Composite 51.4 / 100 (scored 2026-09-26). Not fit for purpose: blocker 1 (mislabelled figure), blocker 2 (stale beyond the line), blocker 3 (judgment on a live page), blocker 4 (run-status line inconsistent with the page).**

| # | Dimension | Weight | Score | Points |
|---|---|---|---|---|
| D1 | Freshness without fail | 22 | 2 | 8.8 |
| D2 | Coverage | 15 | 4 | 12.0 |
| D3 | Deciding a supplier's footing from facts alone | 20 | 2 | 8.0 |
| D4 | Evidence legibility and reconstructability | 13 | 4 | 10.4 |
| D5 | Trust | 12 | 2 | 4.8 |
| D6 | Density and scanability | 4 | 2 | 1.6 |
| D7 | Phone | 4 | 2 | 1.6 |
| D8 | Accessibility | 4 | 2 | 1.6 |
| D9 | Performance | 3 | 2 | 1.2 |
| D10 | Machine legibility | 2 | 3 | 1.2 |
| D11 | Craft | 1 | 1 | 0.2 |
| | **Total** | 100 | | **51.4** |

Caps: the freshness cap applies (Cato Networks, see below), limiting D1 to 3; D1 scores 2 on its own tests, so the cap does not bind. The coverage-gap cap does not apply: all twelve domains list suppliers, and endpoint, identity and managed security are all covered.

## Evidence base

All captures and raw measurements are in `docs/archive/2026-10-refresh-gate/auto-001/score/opus/evidence/`. Renders were made in the OrbStack dev VM with Playwright 1.61.1 and its bundled Chromium, axe-core 4.x, and Lighthouse 12, installed in `~/opus-score-tools` inside the VM only. The scripts that produced every measurement are copied beside the output (`measure.mjs`, `probe.mjs`, `probe2.mjs`, `probe3.mjs`, `probe4.mjs`); each was run as `node <script> https://security-market-pulse-git-preview-pikeholdings.vercel.app <outdir>`.

- First screens: `home-1440-fold.png`, `home-390-fold.png`, `home-320-fold.png`, `corr-1440-fold.png`, `corr-390-fold.png`
- Full pages: `home-1440-full.png` (10,090 px tall), `home-390-full.png` (13,734 px tall)
- Region crops: `p1440-900.png` (domain tables), `p1440-8100.png` (landscape cards, collapsed sections, footer), `p390-800.png` (phone tables)
- Interactions: `src-popover-1440.png` (evidence drawer), `landscape-popover-1440.png`, `row-expand-1440.png`, `row-expand-390.png`
- DOM measurements: `measure.json` (heights, chrome offset, font sizes, tap targets, axe, tab order), `probe.json` (overflow, tables, sections), `probe2.json` (drawers, sort, horizontal scroll), `probe3.json` (drawers for Entra, Okta, Cato, Snyk, Nozomi row), `contrast.json`
- Lighthouse: `lh-mobile-{1,2,3}-summary.json`, `lh-desktop-{1,2,3}-summary.json`
- Cold read: `curl -sS https://security-market-pulse-git-preview-pikeholdings.vercel.app/` (280,296 bytes, content present without scripts)

### Figure sample (blockers 1 and 2, D1 L3-3)

Sixteen figures were checked against the company's own release or SEC filing, plus five suppliers whose shown facts the staleness blocker could catch.

| # | Shown on the page | Source checked | Result |
|---|---|---|---|
| 1 | CrowdStrike rev. growth +26% Q Jul 26; ARR $5.84B | SEC EX-99.1, 2026-08-26 (`crwd-20260826xex991.htm`): "Total revenue was $1.47 billion, a 26% increase"; "ARR grew 25% ... to $5.84 billion" | Matches |
| 2 | Palo Alto Networks +34% Q Jul 26; NGS ARR $9.10B; results 1 Sep 26 | SEC EX-99.1 (`ex991q426earningsrelease.htm`), Sept. 1, 2026: "grew 34% ... to $3.41 billion"; "NGS ARR ... grew 63% ... to $9.10 billion" | Matches |
| 3 | Zscaler 25% Q Jul 26; ARR $3,771M | SEC EX-99.1 (`zs-07312026_991.htm`), Sept 3, 2026: "Revenue: Grew 25% ... to $898.2 million. ARR: Grew 25% ... to $3,771" | Matches |
| 4 | Okta 11% Q Jul 26; Revenue $805M; event "latest results, 24 Aug 26" | SEC EX-99.1 (`okta-7312026_ex991.htm`): dated **August 26, 2026**, "Second Quarter Fiscal Year 2027", revenue $805M +11% | Figure matches. Event date is wrong (24 Aug vs 26 Aug) and the evidence drawer titles the source "Okta Q4 FY2027 Earnings Release", publication date 2026-08-24; it is the Q2 FY2027 release of 26 Aug |
| 5 | SailPoint 16.8% Q Jul 26; ARR $1,230.7M; "What changed": "SailPoint — Q4 FY2027 revenue $308.8 million" | SEC EX-99.1 (`sailpointinc-20260731x991x.htm`), September 9, 2026: "Fiscal Second Quarter 2027 ... Total revenue was $309 million, an increase of 17%"; ARR $1.231B | Figures match. Period label "Q4 FY2027" is wrong (fiscal Q2 2027) |
| 6 | Fortinet 26% Q Jun 26, prior 20% Q Mar 26, Billings $2.37B | SEC EX-99.1 Q2 and Q1 2026: "Revenue grew 26% ... to $2.05 billion"; "Billings grew 33% ... to $2.37 billion"; Q1 "Revenue grew 20%" | Matches in the table. The visible landscape card "Fortinet +52%" is product revenue growth, shown with no metric or period |
| 7 | Check Point 1% Q Jun 26; Total Revenue $674M | checkpoint.com Q2 2026 release: "Total Revenues: $674 million, a 1 percent increase" | Matches |
| 8 | Cloudflare 36% Q Jun 26; Revenue $696.1M | cloudflare.com Q2 2026 release: "$696.1 million, representing an increase of 36%" | Matches |
| 9 | Microsoft Entra ID "18% Q Jun 26" under Rev. growth (also Microsoft Defender for Office 365) | SEC EX-99.1 (`msft-ex99_1.htm`): Microsoft total revenue $90.0B "increased 18%"; the site's own drawer (TR-msft-entra-1) says "FY2026 revenue $331.839 billion, +18% YoY. No discrete Entra ID revenue figure disclosed." | **Mislabelled**: parent-company total revenue growth shown as the product's revenue growth, and a fiscal-year figure labelled as a quarter |
| 10 | Rapid7 -1.5% Q Jun 26; ARR $824.0M | SEC EX-99.1 (`q22026rapid78-kex991.htm`): "Total revenue of $210.9 million, a decrease of 1.5%"; ARR $824 million | Matches |
| 11 | Varonis +18.3% Q Jun 26; Total SaaS ARR $726.0M | SEC EX-99.1: revenues $180.0M vs $152.2M (+18.3%); "Total SaaS ARR was $726.0 million" | Matches |
| 12 | Tenable +8.6%; Revenue $268.5M | SEC EX-99.1: "Revenue of $268.5 million, year-over-year growth of 8.6%" | Matches |
| 13 | Qualys +11%; Revenue $182.2M | SEC EX-99.1: "Q2 Revenue Growth of 11%", "$182.2 million" | Matches |
| 14 | SentinelOne +21%; ARR $1.218B | SEC EX-99.1: "Revenue grew 21% ... to $292 million"; "ARR grew 22% ... to $1.218 billion" | Matches |
| 15 | Rubrik +38%; Subscription ARR $1.66B | SEC EX-99.1: "revenue grew 38% ... to $427.3 million"; "subscription ARR grew 33% ... to $1.66 billion" | Matches |
| 16 | Netskope 29%; ARR $899M | SEC EX-99.1 (`ntsk-ex99_1.htm`): "Q2 revenue was $220.5 million, an increase of 29%"; "ARR grew 27% ... to $899 million" | Matches |
| S1 | Cato Networks "ARR $350+ million" (drawer: publication 2026-02-24, "Full year 2025") | PR Newswire Cato newsroom listing, **Jul 27, 2026**: "Cato Networks Exceeds $415M in ARR Fueled by 42% YoY Growth"; the Cato blog in the site's own evidence library quotes the same figure and the site's record says it "Supersedes the prior $350M/2025 ARR print" | **Stale**: the company published a newer figure 61 days before the scoring date; the table still shows the old one |
| S2 | Snyk "Series F $530M · Sep 2021" (source: CRN, 2021-09-09; drawer says "No later funding round was found") | PR Newswire Snyk newsroom: "Sep 30, 2021 - Snyk Secures $75 Million in Additional Funding" | **Stale** by the letter of the blocker: a newer company-published funding figure 21 days later is not shown |
| S3 | Nozomi Networks: ownership "–", 0 events | nozominetworks.com newsroom: "Nozomi Networks Enters Next Phase of Growth as Mitsubishi Electric Completes Acquisition" (listed January 2026) | Omission: an ownership change the company announced is not shown |
| S4 | Abnormal Security "ARR over $200M" (2024 source) | abnormal.ai press-release listing shows no newer ARR statement | No newer figure found |
| S5 | Delinea "ARR $400M (nearing)" | PR Newswire Delinea listing shows nothing newer | No newer figure found |

EDGAR filing indexes were also checked for the "What changed" list: SailPoint `0002030781-26-000021` is one 10-Q, filed 2026-09-10, period 2026-07-31; Palo Alto Networks `0001327567-26-000023` is one 10-K, filed 2026-09-10, period 2026-07-31; Okta `0001660134-26-000069` is one 10-Q, filed 2026-08-27, period 2026-07-31. The page's entries "SailPoint filed its 10-Q for the quarter ended 2025-07-31" (10 Sep 26), "Palo Alto Networks filed its 10-K (derived) for the quarter ended 2025-07-31", and the same pattern for Zscaler, Netskope, Rubrik, SentinelOne, Okta and CrowdStrike describe filings that were not made on those dates.

## Fit-for-purpose blockers

1. **Mislabelled figure: FAIL.** Microsoft Entra ID and Microsoft Defender for Office 365 show Microsoft's total fiscal-year revenue growth (18%) as their own "Rev. growth" for "Q Jun 26"; SailPoint's fiscal Q2 2027 is labelled "Q4 FY2027"; the "What changed" list reports eight 10-Q/10-K filings "for the quarter ended 2025-07-31" that do not exist; the visible landscape card shows "Fortinet +52%" with no metric or period (it is product revenue growth; revenue grew 26%).
2. **Stale beyond the line: FAIL.** Cato Networks shows ARR $350+ million from 24 Feb 2026 while Cato published $415M on 27 Jul 2026, 61 days before scoring. Snyk also misses a later company-published round by 21 days.
3. **Judgment on a live page: FAIL.** On `/`, the landscape card's evidence drawer reads "Current network/firewall demand is real; strongest realized network-security acceleration in the panel." (`landscape-popover-1440.png`). The collapsed "M&A and funding activity" section on `/` carries "Not a lead — mature-category check", "Identity becomes a PANW platform pillar.", "Akamai joined as strategic investor — cap table is the story.", "Capital heat, not disclosed revenue." (served HTML). `/corrections/` repeats "Watch whether it survives as a product or becomes a feature." The page title is "where the security market is going".
4. **Run-status line misstates what happened: FAIL.** The front page says "Figures checked 26 Sep 2026 · every source collected." The same page says "Frozen from SEC-MARKET-SIG-002 v0.2 (2026-08-15T19:03:08-07:00)" (`p1440-8100.png`), shows "What moved WINDOW · 11 Aug–17 Aug 2026", and holds a Cato evidence record marked as superseding the $350M figure while the table still shows $350M. Commit history on `preview` shows the only collection on 26 Sep was a "proof run" adding one Optiv fact (`cf9bbac`). This is the least certain of the four failures; it rests on plain inconsistency on the page.
5. **Accessibility failure: PASS.** axe-core returned zero violations of any impact on `/` and `/corrections/` at 1440 and 390 (`measure.json`); the page is operable by keyboard with a visible 2px focus outline.

## D1 Freshness without fail: 2

Level 3
1. Yes. "Run status: Figures checked 26 Sep 2026 · every source collected." visible after load (`home-1440-fold.png`).
2. Yes. The same line is on the first screen at 1440 and 390 (`home-1440-fold.png`, `home-390-fold.png`).
3. **No.** Cato Networks is 61 days behind its own 27 Jul 2026 figure (sample row S1).
4. Yes. "What changed in the last 30 days" is a dated list visible without expanding (section `#tracker-changed`, `probe.json`).

Level 5 (credit waiting)
1. Yes. Each evidence drawer shows "Publication date" and "Economic period" separately from the page-level "Figures checked" date (`src-popover-1440.png`).
2. No. No source failure is shown, so no plain-language failure message could be observed.
3. Yes. The newest fact is dated explicitly ("24 Sep 26" at the top of What changed).
4. No. "Tracked figures arrive through the week as companies report them" is not a cadence, and `/feed.xml` says "Weekly issues ... one per ISO week" while the footer says "Frozen from ... 2026-08-15".

Raise by one: show Cato's $415M ARR (27 Jul 2026) and make the collector refuse any figure older than a newer one in its own evidence library.

## D2 Coverage: 4

Level 3
1. Yes. "What this site covers" lists all twelve domains with one sentence each, on the page by scrolling.
2. Yes. Every domain lists 6 or 7 suppliers (`probe.json`, tables).
3. Yes. "Not covered" list on the same section.
4. Yes. "Ownership or last round" and "Events, 12 mo." columns for every supplier; a quiet supplier shows "0". (Accuracy caveat: Nozomi shows "–" and 0 although its acquisition by Mitsubishi Electric was announced as complete.)

Level 5
1. No. Domains have anchors (`#domain-endpoint-xdr` etc.); suppliers have no id or address (42 ids on the whole page, no duplicates, none per supplier).
2. Yes. "12 domains, 74 tracked suppliers."
3. Yes. "Adding or dropping a domain or a supplier is a data change, not a promise about who belongs in the market." and "being listed is not a recommendation".
4. Yes. A listed supplier with "0" events is distinguishable from an absent one.

Raise by one: give every supplier row a stable anchor id.

## D3 Deciding a supplier's footing from facts alone: 2

Level 3
1. **No.** In Identity and Email security, the Microsoft rows put Microsoft's total fiscal-year growth under the same "Rev. growth" heading as Okta's and SailPoint's quarterly GAAP growth (sample row 9).
2. Yes. Domain chips link to each table (`#domain-*`) at both widths.
3. Yes. At 1440 one row shows growth, prior quarter, own metric, ownership and latest dated event.
4. **No.** The landscape card lists "Fortinet +52% · Cato +43% · Netskope +31%" and its drawer calls Fortinet the "strongest realized network-security acceleration in the panel".

Level 5 (credit waiting)
1. No. Median rows exist for most domains but not Security operations, Managed security or Application security, and the omission is not explained.
2. Yes. Column sort buttons work (Rev. growth sort reorders Network and SASE; `probe2.json`).
3. Yes at 1440.
4. No. At 390 rows are collapsed and need a tap each (`row-expand-390.png`).

Raise by one: drop the parent-company figure from product rows (show "not reported separately") and remove the landscape cards and their drawer interpretations.

## D4 Evidence legibility and reconstructability: 4

Level 3
1. Yes. A "src" control sits beside every figure.
2. Yes for every figure sampled (SEC exhibits, company releases). Weak spot: some ownership labels cite a homepage (`https://www.microsoft.com/en-us/investor`, `https://delinea.com` "Current homepage check").
3. Yes. The revenue-growth definition is stated under "The market by domain" and in "How this is built".
4. Yes. Drawer "Publication date" and "Economic period" versus page "Figures checked 26 Sep 2026".

Level 5
1. Yes. The drawer opens in place; scroll position unchanged (`probe2.json`, scrollAfterClick [0,0]).
2. No. Microsoft rows approximate with the parent figure instead of saying "not reported".
3. Yes. "The sourcing ladder" in "How this is built", one click.
4. No. The drawer has no report-this-figure link; reporting is a general mailto.

Raise by one: add "report this figure" to the drawer and replace approximations with an explicit "not reported separately".

## D5 Trust: 2

Level 3
1. **No.** See blocker 3.
2. Yes. "Facts are collected, checked ... and published automatically — no human approval step, and no machine judgment." (How this is built).
3. Yes. `/corrections/` lists dated corrections (`corr-1440-fold.png`).
4. Yes. "Send a correction or a question" mailto visible without expanding.

Level 5 (credit waiting)
1. No. "Run by Jesse Pike" only; no statement of his relationship to tracked suppliers.
2. No. No statement of how suppliers are chosen or whether competitors and partners are held to the same standard.
3. No. The landscape cards, "What moved WINDOW · 11 Aug–17 Aug 2026", M&A notes and the "How a posture is set" panel sit on `/` without an archive label.
4. No. `/corrections/` says issues keep the original, but "a wrong entry there is fixed in place" for the standing tables.

Raise by one: remove every pre-tracker section (landscape, what moved, M&A notes, posture panel, drawer "Interpretation" fields) from `/`.

## D6 Density and scanability: 2

Level 3
1. Yes. Each domain table (6 or 7 rows, 279 to 494 px tall) fits one 1440x900 screen.
2. **No.** Figures are left-aligned, `font-variant-numeric: normal`, and signs are inconsistent in one column ("1%", "36%", "+34%" in Network and SASE).
3. **No.** Table cells are 13 px, and the intro paragraph runs about 90 characters per line at 1440.
4. Yes. "0" versus "3 · latest debt, 13 Aug 26".

Level 5
1. No. Page is 10,090 px tall at 1440; coverage starts at 7,350 px.
2. Yes. All domains are tables.
3. No. Masthead line "Sourced facts, checked and published automatically..." is 10 px.
4. Yes.

Raise by one: set tabular, right-aligned figures with one sign convention and 14 px cells.

## D7 Phone: 2

Level 3
1. **No.** At 390 the first screen ends at the "The market by domain" intro; no supplier row is visible (`home-390-fold.png`).
2. Yes. First content at 174 px of 844 (20.6%, `measure.json`).
3. **No.** "src" targets are 27x19 and 27x18 px (53 small targets at 390).
4. Yes. `html { overflow-x: clip }`; scrollX stays 0 at 390 and 320 (`probe2.json`), though see D8 L3-4.

Level 5 (credit waiting)
1. No. One tap per supplier at 390 versus zero clicks at 1440.
2. No. Row summaries and metadata are 12 px mono.
3. Yes. Domain chips work at 390.
4. No. Collapsed rows hide prior quarter, own metric and events.

Raise by one: move the run status and first domain table above the explanatory paragraph at 390, and enlarge "src" targets to 24 px.

## D8 Accessibility: 2

Level 3
1. Yes. Zero axe violations, all four runs (`measure.json`).
2. Yes. Tab stops reach nav, domain links and sort buttons with a "solid 2px rgb(11, 107, 94)" outline.
3. Yes. Lowest computed contrast 5.02:1 (`contrast.json`); axe flagged 12 contrast nodes as "incomplete", checked manually.
4. **No.** Content is clipped rather than reflowed at 390 and 320: document scrollWidth is 615 px, and the Exabeam, Cato and Sysdig row summaries and Cato's expand control run past the right edge (`probe.json` "over", `row-expand-390.png`).

Level 5 (credit waiting)
1. Yes. 2. Yes (axe target-size passes on spacing). 3. Yes (skip link first, domain links from stop 10). 4. Yes (56 `time` elements with `datetime`; header, nav, main, footer landmarks).

Raise by one: let row summaries wrap at narrow widths instead of clipping.

## D9 Performance: 2

Lighthouse 12, three runs each, `evidence/lh-*-summary.json`.

Level 3
1. **No.** Mobile LCP median 4,902 ms.
2. **No.** Desktop CLS 0.179 on all three runs (mobile 0).
3. Yes. Mobile TBT median 81 ms.
4. Yes. Desktop LCP median 1,007 ms.

Level 5 (credit waiting)
1. No. 2. No (JavaScript 258 KB compressed; total 402 KB). 3. Yes (document 27 to 61 KB). 4. No (Google Fonts stylesheet is render-blocking).

Raise by one: self-host or preload the fonts and reserve space for whatever shifts on desktop.

## D10 Machine legibility: 3

Level 3
1. Yes. Tables are in the served HTML (cold curl).
2. Yes. JSON-LD `Report` with `publisher` Organization and `dateModified` "2026-09-26".
3. Yes. RSS and JSON `<link rel="alternate">` in the head; `sitemap.xml` 200.
4. Yes. No empty headings, no duplicate ids.

Level 5
1. No. No tracker JSON (`/tracker.json` 404); the JSON alternates are issue and corrections files.
2. No. Figures have no anchor ids.
3. Yes. Publisher is an Organization with a stable url (no `@id` or `sameAs`).
4. No. `robots.txt` is "User-agent: * Allow: /", which is the default posture.

Raise by one: publish a tracker JSON with run status, domains and each supplier's latest figure.

## D11 Craft: 1

Level 3
1. **No.** Two sans families (Archivo, IBM Plex Sans) plus IBM Plex Mono; eighteen font sizes on `/`.
2. **No.** Dark panels (top bar, "How a posture is set", "What moved") and an orange chart colour beside the teal accent.
3. **No.** Row summaries clip at 390 and 320.
4. Yes.

Level 5 (credit waiting): 1 not checked; 2 No (sign formatting differs within one column); 3 No (the dark "How a posture is set" panel reads as marketing chrome).

Raise by one: cut to one sans and one mono and a six-step type scale.

## Three changes that would raise the score most

1. Fix the facts: show Cato's $415M ARR, drop parent-company growth from Microsoft product rows, correct the SailPoint and Okta period and date labels, and stop generating filings "for the quarter ended 2025-07-31". This clears blockers 1 and 2 and lifts D1 and D3.
2. Remove the pre-tracker material from `/`: the landscape cards, "What moved", the M&A notes, the posture panel, the "Frozen from ... 2026-08-15" footer, and every drawer "Interpretation". This clears blockers 3 and 4 and lifts D3 and D5.
3. Rework the phone layout: supplier rows visible on the first 390 screen, rows that wrap instead of clip, 24 px targets. This lifts D7 and D8.
