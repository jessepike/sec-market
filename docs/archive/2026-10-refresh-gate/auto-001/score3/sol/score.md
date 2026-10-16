# Security Market Pulse site score — rubric v3.0

- **Deployment scored:** https://security-market-pulse-git-preview-pikeholdings.vercel.app/
- **Scoring date:** 2026-09-26, approximately 18:13 UTC.
- **Scorer:** GPT-6 Sol, blind scoring run.
- **Commit served:** The served HTML exposes Vercel deployment `dpl_78Rxd3zYmYUEcXEzmhDMma42TEtb`, but no Git commit SHA. `git rev-parse origin/preview` returned `a8d39760ff0f115dcefcd455d080bfb78611baa4` during scoring. The deployment-to-commit link could not be verified, so that SHA is a branch reference, not an asserted deployment identity.
- **Composite:** **39.0 / 100**. **Not fit for purpose: the run-status line miscounts public suppliers; accessibility clearance was not established.** This is a score of the served artifact on this date, not an outcome or audience score.

## Evidence and limits

`H` is `/tmp/secmarket-home.html`, captured with `curl -LsS -D /tmp/secmarket-home.headers -o /tmp/secmarket-home.html https://security-market-pulse-git-preview-pikeholdings.vercel.app/`. Its response was HTTP 200, ETag `W/"063837400f3b5bdb991b8fa5516d878e"`. `C`, `I`, `P`, and `T` are the same curl capture for `/corrections/`, `/issues/`, `/issues/2026-w36/`, and `/thesis/`, respectively, at `/tmp/secmarket-corrections.html`, `/tmp/secmarket-issues.html`, `/tmp/secmarket-issue.html`, and `/tmp/secmarket-thesis.html`. `B` and `S` are the served `/assets/index-DZAFyDAp.js` and `/assets/index-BLv0D9Nq.css`, captured at `/tmp/secmarket-app.js` and `/tmp/secmarket-style.css`. `R` is the served `/robots.txt`. Commands below refer to these captures and the named live URLs.

Company documents were fetched with `curl -LfsS --max-time 12 -A 'Security Market Pulse blind scoring contact jesse@keatingpike.com' -o /tmp/secmarket-sources/<id>.html <source-url>`. The descriptive User-Agent was used for every SEC request, including `https://data.sec.gov/submissions/CIK##########.json`. I checked the source text, the units, the stated fiscal period, and the percentage or its numerator and denominator. The 18 public suppliers with figures were checked as a complete set, rather than a ten-row draw. Recent SEC submission lists were checked for 17 of them; Trend Micro's company release was used for the eighteenth. This sample found no newer same-metric public report more than 14 days ahead of a shown figure. It cannot prove that no unobserved company statement exists.

No browser was run. `find docs/archive/2026-10-refresh-gate/auto-001/score3/opus/evidence -maxdepth 2 -type f` found only `home.html` and `home.headers`, with no render, axe, keyboard, Lighthouse, or screenshot record. Tests requiring those observations are recorded **No (unverified)**. Other UI conclusions below are explicitly **read from markup/CSS**, not claimed as rendered observations.

## Source audit

The following are direct company releases or filings opened by curl. “Match” means the shown figure and period agree with that source, including arithmetic where a filing only gives component values.

| Shown figure | Company source and check |
|---|---|
| CrowdStrike +26%, ARR $5.84B, quarter ended Jul 2026 | [Q2 FY2027 exhibit](https://www.sec.gov/Archives/edgar/data/1535527/000153552726000029/crwd-20260826xex991.htm): $1.47B revenue, +26%; $5.84B ARR. Match. |
| Palo Alto Networks +34%, NGS ARR $9.10B, quarter ended Jul 2026 | [Q4 FY2026 exhibit](https://www.sec.gov/Archives/edgar/data/1327567/000132756726000019/ex991q426earningsrelease.htm): $3.41B revenue, +34%; $9.10B NGS ARR. Match. |
| SentinelOne +21%, ARR $1.218B, quarter ended Jul 2026 | [Q2 FY2027 exhibit](https://www.sec.gov/Archives/edgar/data/1583708/000158370826000052/sentineloneq227exhibit991.htm): $292M revenue, +21%; $1.218B ARR. Match. |
| Trend Micro ARR greater than $1.7B, quarter ended Jun 2026 | [Q2 2026 company release](https://newsroom.trendmicro.com/2026-08-13-Trend-Micro-Reports-Earnings-Results-for-Q2-2026): ARR exceeds $1.7B. Match. |
| Check Point +1%, $674M revenue, quarter ended Jun 2026 | [Q2 2026 company release](https://www.checkpoint.com/press-releases/check-point-software-reports-2026-second-quarter-financial-results/): $674M, +1%. Match. |
| Cloudflare +36%, $696.1M revenue, quarter ended Jun 2026 | [Q2 2026 exhibit](https://www.sec.gov/Archives/edgar/data/1477333/000147733326000053/q226exhibit991.htm): $696.1M, +36%. Match. |
| Fortinet +26%, $2.37B billings, quarter ended Jun 2026 | [Q2 2026 exhibit](https://www.sec.gov/Archives/edgar/data/1262039/000126203926000018/ftntq2-2026ex991.htm): $2.05B revenue, +26%; $2.37B billings. Match. |
| Netskope +29%, ARR $899M, quarter ended Jul 2026 | [Q2 FY2027 exhibit](https://www.sec.gov/Archives/edgar/data/2063196/000119312526380188/ntsk-ex99_1.htm): $220.5M revenue, +29%; $899M ARR. Match. |
| Zscaler +25%, ARR $3,771M, quarter ended Jul 2026 | [Q4 FY2026 exhibit](https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm): $898.2M revenue, +25%; $3,771M ARR. Match. |
| Okta +11%, cRPO $2.585B, quarter ended Jul 2026 | [Q2 FY2027 10-Q](https://www.sec.gov/Archives/edgar/data/1660134/000166013426000069/okta-20260731.htm): revenue $805M versus $728M and cRPO $2,585M. Rounded growth is 11%. Match. |
| SailPoint +16.8%, ARR $1,230.7M, quarter ended Jul 2026 | [Q2 FY2027 10-Q](https://www.sec.gov/Archives/edgar/data/2030781/000203078126000021/sail-20260731.htm): revenue $308.813M versus $264.359M; ARR $1,230.7M. Growth computes to 16.8%. Match. |
| Commvault +11%, subscription ARR $1,054M, quarter ended Jun 2026 | [Q1 FY2027 exhibit](https://www.sec.gov/Archives/edgar/data/1169561/000116956126000020/q1fy27pressrelease.htm): revenue $314.131M versus $281.978M; ARR $1,054M. Rounded growth is 11%. Match. |
| Rubrik +38%, subscription ARR $1.66B, quarter ended Jul 2026 | [Q2 FY2027 exhibit](https://www.sec.gov/Archives/edgar/data/1943896/000194389626000055/rubrikinc-991pressrelease7.htm): $427.3M revenue, +38%; $1.66B ARR. Match. |
| Varonis +18.3%, SaaS ARR $726.0M, quarter ended Jun 2026 | [Q2 2026 exhibit](https://www.sec.gov/Archives/edgar/data/1361113/000117184326004948/exh_991.htm): revenue $180.0M versus $152.2M, or 18.3%; SaaS ARR $726.0M. Match. |
| Qualys +11%, $182.2M revenue, quarter ended Jun 2026 | [Q2 2026 exhibit](https://www.sec.gov/Archives/edgar/data/1107843/000110784326000034/qlys-20260804xex991.htm): $182.2M, +11%. Match. |
| Rapid7 −1.5%, ARR $824.0M, quarter ended Jun 2026 | [Q2 2026 exhibit](https://www.sec.gov/Archives/edgar/data/1560327/000156032726000043/q22026rapid78-kex991.htm): $210.9M revenue, −1.5%; $824.0M ARR. Match. |
| Tenable +8.6%, $268.5M revenue, quarter ended Jun 2026 | [Q2 2026 exhibit](https://www.sec.gov/Archives/edgar/data/1660280/000166028026000032/q22026financialresults-ear.htm): $268.5M, +8.6%. Match. |
| JFrog +29%, $87.5M cloud revenue, quarter ended Jun 2026 | The linked investor page would not return a usable curl response; the [company's Q2 2026 exhibit filed with the SEC](https://www.sec.gov/Archives/edgar/data/1800667/000119312526337998/frog-ex99_1.htm) states $163.8M total revenue, +29%, and $87.5M cloud revenue, +53%, for the June quarter. Match. |

Three fiscal-period labels were checked explicitly: CrowdStrike's “Q Jul 26” is its Q2 FY2027 quarter ended July 31; Zscaler's “Q Jul 26” is its Q4 FY2026 quarter ended July 31; Commvault's “Q Jun 26” is its Q1 FY2027 quarter ended June 30. The abbreviated labels name calendar end months rather than fiscal quarter numbers, but none of these three reverses the period. The linked releases above provide the evidence.

All nine segment rows were checked as separate products or acquisitions against primary pages. [Microsoft Defender for Endpoint](https://learn.microsoft.com/en-us/defender-endpoint/), [Microsoft Defender for Office 365](https://learn.microsoft.com/en-us/defender-office-365/mdo-deployment-guide), and [Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/fundamentals/faq) are Microsoft products; [Google SecOps](https://cloud.google.com/security/products/security-operations) is a Google Cloud product; [Cortex XSIAM](https://www.paloaltonetworks.com/cortex) is a Palo Alto Networks product; [Falcon Exposure Management](https://www.crowdstrike.com/en-us/platform/exposure-management/continuous-threat-exposure-management-ctem/) is a CrowdStrike product; [Splunk](https://www.sec.gov/Archives/edgar/data/858877/000119312524070175/d783088dex991.htm) was acquired by Cisco; [Check Point Email Security](https://blog.checkpoint.com/product-updates/introducing-check-point-email-security-a-new-name-aligned-with-our-ai-driven-strategy/) is Check Point's renamed product; and [GitHub Advanced Security](https://docs.github.com/en/enterprise-cloud@latest/get-started/learning-about-github/about-github-advanced-security) is a GitHub product. Each identity is supported, and no row invents a separate segment revenue figure. The tracker itself gives GitHub Advanced Security no ownership/source entry. Its citations for Microsoft, Google SecOps, Cortex XSIAM, and Falcon Exposure Management point to general investor material or an earnings filing that does not name the product, even though the direct product pages above do.

The five private-supplier event counts in `H` were checked against their underlying company announcements: Cyera **5** ([January funding](https://www.cyera.com/press-releases/cyera-raises-400m-to-meet-rapidly-growing-demand-for-ai-security-among-enterprises), [Ryft](https://www.cyera.com/press-releases/cyera-acquires-ryft-to-extend-its-agentic-ai-security-platform), [June funding](https://www.cyera.com/press-releases/cyera-raises-600-million-at-12-billion-valuation-to-continue-building-the-trust-layer-for-the-ai-era), [Oasis](https://www.cyera.com/press-releases/cyera-completes-acquisition-of-oasis-security), [September investment](https://www.cyera.com/press-releases/cyera-announces-400-million-investment-from-goldman-sachs-to-build-the-trust-layer-for-the-agentic-enterprise)); Delinea **3** ([StrongDM agreement](https://delinea.com/news/delinea-strongdm-to-unite-redefine-identity-security-for-the-ai-era), [closing](https://www.globenewswire.com/news-release/2026/03/05/3250113/0/en/delinea-completes-strongdm-acquisition-to-secure-ai-agents-with-continuous-identity-authorization.html), [CFO appointment](https://www.globenewswire.com/news-release/2026/09/23/3367539/0/en/delinea-appoints-timothy-regan-as-chief-financial-officer.html)); Torq **2** ([round](https://torq.io/news/torq-seriesd/), [Jit](https://torq.io/news/torq-acquires-jit/)); Upwind **2** ([round](https://www.upwind.io/feed/building-next-wave-cloud-security-upwind), [Aegis statement](https://www.upwind.io/feed/building-the-future-introducing-the-upwind-ai-security-lab)); HiddenLayer **1** ([round](https://www.hiddenlayer.com/news/hiddenlayer-100m-series-b-ai-security)). These checks support the events the site counted, but do not establish that every event these companies published was collected.

Three plausible staleness candidates received an additional company-source check. Ping's “approaching $800M ARR” comes from a [November 2024 company release](https://press.pingidentity.com/2024-11-14-Ping-Identity-Surpasses-30-Annual-Growth-in-SaaS-Revenue-and-Approaches-800M-ARR-as-an-Enterprise-Identity-Market-Leader); later [Ping releases](https://press.pingidentity.com/) checked did not show a newer ARR figure. Abnormal's “over $200M ARR” comes from its [August 2024 release](https://abnormal.ai/newsroom/press-releases/series-d-5b-valuation); the checked [2026 newsroom](https://abnormal.ai/newsroom) had newer product and customer news but no newer ARR figure in the inspected results. Cato's $415M ARR and +42% agree with its [July 2026 company-issued release](https://www.prnewswire.com/il/news-releases/cato-networks-exceeds-415m-in-arr-fueled-by-42-yoy-growth-and-enterprise-demand-302833667.html); the [company news index](https://www.catonetworks.com/news/) showed later releases but none with a newer ARR figure in the inspected list. The Cato site blocked curl, so the company-issued syndicated release was used. These old figures need visible source dates; age alone does not meet the rubric's stale-against-newer-company-figure condition.

For judgment language, I extracted visible text from each HTML route above and ran `rg -ni 'leading|leader|accelerat|slowing|winner|best|ahead|behind|lag|weak|strong|boom|thesis|forecast|should|recommend|fastest|prospects|outlook|pressure|stalls|stalling' /tmp/secmarket-{home,corrections,issues,issue,thesis}.txt`. The front page's hits are source titles, method exclusions, or generic coverage language. The corrections page quotes withdrawn judgments as corrections. `/issues/`, its issue permalink, and `/thesis/` do contain old judgments, and explicitly identify themselves as discontinued or dated records. No live tracker stance was found in the served text. This is a text and HTML check, not a rendered overlay check.

## Blockers and caps

1. **Mislabelled figure — Pass in the required sample.** The 18 public rows and three fiscal-period labels above matched their own disclosures. Segment product identities matched primary pages, with weak tracker citations noted above.
2. **Stale beyond 14 days against a newer company figure — Pass in the checked sample.** SEC submission histories and the three company-news candidates above revealed no newer same-metric print more than 14 days ahead of what is shown. This is a sample result, not a universal absence claim.
3. **Judgment on a live page — Pass.** `H` and `C` carry facts, method statements, source titles, and explicitly withdrawn historical wording; `I`, `P`, and `T` are marked archive material and are exempt by the rubric.
4. **Run-status line misstates what happened — Fail.** `H` says “Filings complete for all 14 public suppliers; company news pages could not be read for 28 of 74 suppliers.” The same served table labels **18 distinct suppliers** “Public.” Command: parse `table.tracker-table tbody tr` and count unique `.tracker-row__name` where the ownership cell starts `Public ·`; result 18. The public-supplier denominator is wrong on the page, regardless of what the internal filing job intended by 14. The failed-newsroom list does name 28 suppliers.
5. **Accessibility — Fail to establish clearance.** No permitted blind-scorer axe or keyboard record exists for `/` and `/corrections/` at both widths, and this scorer was prohibited from running a browser. This records missing proof, not an observed critical or serious violation.

**Freshness cap:** Not applied. The source check found no company-published newer figure over 30 days ahead of a shown figure. **Coverage-gap cap:** Not applied. `H` shows suppliers in all 12 domains, and its not-covered list addresses the main category boundary explicitly.

## Dimension scores and individual tests

Each “No (unverified)” counts as No under the rubric's binary rule. “Read from markup” denotes an inference from the served HTML/CSS/JS rather than a render.

### D1 — Freshness without fail: 2 / 5 (22 weight; 8.8 points)

Level 3: **1 No** — `H`, `.run-status__line`, says 28 company news pages could not be read, but the supplier names are inside the closed “Which sources failed” `details`; the test requires names without expansion. **2 Yes, read from markup** — `H` places both `AS OF 26 Sep 2026` and `Figures checked 26 Sep 2026` before `#market`; `S` has no small-screen rule hiding either date. The first-screen conclusion was not rendered. **3 Yes** — the public-figure source audit and SEC submissions above checked more than ten latest figures without a newer same-metric report over 14 days ahead. **4 Yes** — `H`, `#tracker-changed`, has visible dated rows, newest September 24, with no closed parent section.

Level 5: **1 No** — `H`, Cato's “ARR $415M” and Abnormal's “ARR over $200M” lack a publication date beside the figure, although the global check date is shown. **2 Yes** — `H`, `.run-status__failed li`, names Armis Security, Axonius, and the other failed pages with plain reasons. **3 Yes** — `H`, `#tracker-changed`, states “24 Sep 26” for its newest fact. **4 Yes** — `H`, `#follow`, states “SEC filings refresh daily; press, funding and distress facts refresh twice a week”; the method repeats it. The old issue feed describes the archive, not the tracker refresh.

One-step raise: name the failed company sources in the visible run-status line, without requiring the “Which sources failed” expansion.

### D2 — Coverage: 2 / 5 (15 weight; 6.0 points)

Level 3: **1 Yes** — `H`, `#tracker-coverage`, lists 12 linked domains and one description for each; `#tracker-domain-index` also links to each. **2 Yes** — parsing `H` finds 12 domain tables, each with six or seven supplier rows. **3 Yes** — `H`, `#tracker-coverage`, has the “Not covered” list without an expansion. **4 No** — `H` has an “Events, 12 mo.” count and latest type, but no supplier-level distress or consolidation section with an explicit “nothing to show”; zero is shown as `0` in a generic event cell.

Level 5: **1 Yes** — `H` has 12 `article.tracker-domain[id]` anchors and 74 first-occurrence `tr[id^="s-"]` anchors for 74 suppliers; repeated supplier rows use the first stable anchor. **2 Yes** — `H`, `#tracker-coverage`: “12 domains, 74 tracked suppliers.” **3 Yes** — `H`, `#market`: “Figures are listed, not ranked”; rows are alphabetical by default and have no inclusion verdict. **4 Yes** — `H` shows tracked suppliers with `0` events, while an expected but absent supplier is absent from the 74-name roster; the general not-covered list states the scope boundary.

One-step raise: give every supplier an explicit distress/consolidation field, including a plain absence statement when there is no sourced fact.

### D3 — Deciding a supplier's footing from facts alone: 2 / 5 (20 weight; 8.0 points)

Level 3: **1 No** — `H`, Endpoint and XDR, mixes public GAAP revenue growth, Trend Micro ARR, private ownership, and an undisclosed Microsoft product line; its six rows do not share one named metric and period. **2 Yes, read from markup** — `H`, `#tracker-domain-index a[href="#domain-..."]`, reaches any named domain's supplier table in one anchor click on either width; the index is not hidden by `S`. **3 Yes** — `H`, CrowdStrike row `#s-crwd`, puts latest +26%, prior +26%, public ownership, and one dated August 26 event in the same row. **4 Yes** — `H`, `#market`, labels the figures “listed, not ranked”; default order is supplier name, and medians are computed numbers without a winner label.

Level 5: **1 No** — `H` has a median row in six domains, while Security operations, Managed security, Application security, Email security, OT/IoT, and AI security have none. **2 Yes, read from markup** — `H` gives every table six sort buttons; `B`, `Wn/Un`, changes sort by the shown column. **3 No (unverified)** — the one-minute, keep-your-place task needs an observed interaction. **4 No** — `S` at `@media (width<=640px)` hides every row cell after the supplier name until the row toggle is pressed; desktop exposes those cells on load.

One-step raise: make one genuinely comparable period and footing field available for all tracked suppliers, with explicit non-disclosure where the company publishes none, and preserve each company's own metric separately.

### D4 — Evidence legibility and reconstructability: 1 / 5 (13 weight; 2.6 points)

Level 3: **1 No** — `H`, Tines and several other rows show an “Events, 12 mo.” value of `0` without an adjacent source or explanation of the counted set; GitHub Advanced Security has no ownership source. **2 No** — `B` maps some row source buttons to generic pages such as `https://www.microsoft.com/en-us/investor` for Defender for Endpoint and an SEC filing index for Cortex XSIAM; those pages do not substantiate the named product. The primary product pages in the segment audit do. **3 Yes** — `H`, “How this is built,” opens in one `details` click and defines GAAP revenue growth and the sourcing ladder in plain sentences. **4 No** — `H` shows one global “Figures checked” date, but several private own-metric and ownership cells, such as Abnormal ARR and Microsoft's segment status, omit the underlying publication date beside that fact.

Level 5: **1 Yes, read from bundled markup** — `B`, `.evidence-record__sources`, renders publisher, `<time dateTime=...>`, and a canonical source `href` in the evidence overlay invoked by a `src` button; the overlay itself was not rendered here. **2 Yes** — `H`, “How this is built”: “where a company reports no comparable revenue figure, the table says so rather than estimating one,” and the relevant table cells contain `–`. **3 Yes** — `H`, “The sourcing ladder,” states which of five source classes may publish distress or consolidation alone. **4 No** — `B`'s evidence-record markup has canonical source and excerpt but no correction link; `H` offers only the general correction section near the page end.

One-step raise: replace generic source landing pages with direct product or disclosure documents and link a source or clear count-method note beside every event count.

### D5 — Trust: 4 / 5 (12 weight; 9.6 points)

Level 3: **1 Yes** — the route-wide HTML text grep described above found no current supplier stance in `H` or `C`; the old issue and thesis judgment is explicitly dated archive content. **2 Yes** — `H`, “How this is built”: “Facts are collected ... and published automatically — no human approval step, and no machine judgment.” **3 Yes** — `C` is a stable `/corrections/` page with dated September 20 and 21 entries and an explicit record policy. **4 Yes** — `H`, `#next`, displays `mailto:jesse@keatingpike.com` without expanding anything; `C` repeats the address.

Level 5: **1 No** — `H` says “Run by Jesse Pike” but does not disclose his relationship to tracked suppliers. **2 No** — `H` states the 12-domain scope but gives no supplier-selection rule or statement that operator partners and competitors meet the same evidence standard. **3 Yes** — `I` says signed weekly issues were discontinued on September 25 and kept as a dated record; `T` says the standing analysis is no longer updated. **4 Yes** — `C` says the original issue wording remains in the historical record with the dated fix beside it; it separately explains in-place fixes for standing tables.

One-step raise: disclose the operator's relevant supplier relationships and the rule used to select suppliers, including the standard applied to partners and competitors.

### D6 — Density and scanability: 2 / 5 (4 weight; 1.6 points)

Level 3: **1 No (unverified)** — eight rows or a whole domain per 1440-by-900 capture cannot be counted without a render. **2 Yes, read from CSS** — `S`, `.tracker-cell--numeric,.tracker-figure__value{font-variant-numeric:tabular-nums}` and right-aligned growth columns; period dates use muted monospace, and ownership has its own column. **3 No** — `S`, `.tracker-table{font-size:.8125rem}` is 13 pixels at the 16-pixel root; the test requires body text of at least 14 pixels. **4 Yes** — `H`, event column shows `0` for Tines and `5 · latest funding, 22 Sep 26` for Cyera.

Level 5: **1 No (unverified)** — no DOM height measurement or render is available. **2 Yes** — `H` uses fixed-column `<table>` markup for all 12 comparisons. **3 No** — `S` makes repeated table text 13 pixels and several date/source labels 12 or 11 pixels; these are continuous reading surfaces. **4 No (unverified)** — a full domain in one 1440-by-900 screen was not captured.

One-step raise: lift table reading text to 14 pixels and demonstrate a whole small domain per desktop screen in a measured render.

### D7 — Phone: 0 / 5 (4 weight; 0 points)

Level 3: **1 No (unverified)** — `H` puts the 12-item domain index before the first supplier table; no 390-by-844 capture proves a supplier fits on the first screen with run status. **2 No (unverified)** — `S` defines rail and header sizes, but there is no DOM measurement of the first content offset at 390. **3 No (unverified)** — `S` gives mobile source buttons 24-by-24 and supplier toggles 44 pixels high, but no full target audit at 390 exists. **4 No (unverified)** — `S` uses `html{overflow-x:clip}` and mobile block rows, but there is no 390/320 rendered scroll check.

Level 5: **1 No** — `S` hides metric, prior, ownership, and event cells behind a row toggle at 390, adding a tap relative to desktop. **2 No** — `S` sets mobile table reading text to 13 pixels and metadata as low as 10 pixels. **3 Yes, read from markup** — `H` has the same `#tracker-domain-index` links in the mobile DOM; `S` has no rule removing that index. **4 No** — `S`, `.tracker-table tr:not(.tracker-table__median) td:not(:first-child){display:none}` until expansion, so a domain cannot be scanned with all figures exposed.

One-step raise: show the run status and a domain's suppliers in a 390-pixel first-screen capture, then prove both widths have no horizontal page scroll.

### D8 — Accessibility: 1 / 5 (4 weight; 0.8 points)

Level 3: **1 No (unverified)** — no permitted axe result exists for `/` and `/corrections/` at both widths. **2 Yes, read from markup/CSS** — `H` uses native links and buttons for jumps, evidence, and sorts; `S` defines a visible `:focus-visible` outline. Actual keyboard operation was not observed. **3 No (unverified)** — no complete rendered text-contrast audit exists. **4 No (unverified)** — no 320-pixel reflow capture exists.

Level 5: **1 No (unverified)** — no zero-all-impact axe record exists. **2 No (unverified)** — no complete pointer-target audit exists. **3 No (unverified)** — `H` starts with `a.skip-link`, but the number of Tab presses to `#market` was not measured. **4 No** — `H` has landmarks and some `<time dateTime>` elements, but table periods are plain `.tracker-figure__period` spans, so `time` is not used throughout.

One-step raise: produce axe and keyboard receipts on both routes at 1440 and 390, and resolve any serious or critical violation found.

### D9 — Performance: 0 / 5 (3 weight; 0 points)

Level 3: **1 No (unverified)** — no three-run mobile Lighthouse LCP median. **2 No (unverified)** — no CLS measurements at either profile. **3 No (unverified)** — no mobile TBT median. **4 No (unverified)** — no desktop LCP median.

Level 5: **1 No (unverified)** — no mobile LCP/TBT median. **2 No (unverified)** — `curl -H 'Accept-Encoding: gzip' -o /dev/null -w '%{size_download}'` returned HTML 21,961, JS 155,856, and CSS 9,887 bytes, but third-party font transfer was not measured, so the total-transfer test is incomplete; the JS sublimit passes. **3 Yes** — the same command measured the compressed HTML at 21,961 bytes. **4 No** — `H` has a third-party `fonts.googleapis.com` stylesheet in the document head.

One-step raise: obtain three Lighthouse runs on both profiles and a passing mobile LCP, TBT, or CLS median.

### D10 — Machine legibility: 4 / 5 (2 weight; 1.6 points)

Level 3: **1 Yes** — `H` includes all 12 tables and their supplier figures in prerendered HTML, including CrowdStrike `#s-crwd` at cold read. **2 Yes** — `H` has valid JSON-LD `@type: Report`, `publisher: Organization`, and `dateModified: 2026-09-26` (parsed with `json.loads`). **3 Yes** — `H` links `/feed.xml` and `/issues/index.json` in its head and page. **4 Yes** — parsing `H` found no duplicate IDs or empty headings.

Level 5: **1 No** — the discoverable JSON index is for the retired issues; no endpoint exposes the current run state, 12 domains, and supplier figures together. **2 No** — supplier anchors exist, but no figure-specific anchor or shared figure ID in structured data exists. **3 Yes** — JSON-LD publisher is an `Organization` with the stable `https://securitymarketpulse.com/` URL. **4 Yes** — `R` deliberately says `User-agent: *`, `Allow: /`, and names the sitemap; the preview response additionally carries `x-robots-tag: noindex`.

One-step raise: publish a current tracker JSON endpoint with stable figure IDs shared with HTML anchors.

### D11 — Craft: 0 / 5 (1 weight; 0 points)

Level 3: **1 No** — `S`, `:root`, defines two sans families (`IBM Plex Sans`, `Archivo`) plus mono, beyond the one-sans allowance. **2 No** — `S` uses a teal accent, magenta alert, gold warning, and a blue-to-teal brand gradient, beyond one accent on neutrals. **3 No (unverified)** — no render at 1440, 390, or 320 establishes no collision or clipping. **4 No** — `S`, `.site-header__mark`, gives an information-free gradient square.

Level 5: **1 No (unverified)** — no greyscale capture. **2 No (unverified)** — no rendered comparison of every repeated pattern. **3 No (unverified)** — no render supports the one-instrument judgment; the decorative brand mark is visible in CSS.

One-step raise: use one sans family and remove the decorative gradient mark, then inspect all three widths.

## Three changes with the largest likely score effect

1. Correct the public-supplier count, name failed sources in the visible run-status line, and make both claims traceable to the actual source inventory. This clears the observed fit-for-purpose blocker and raises D1 past its level-3 gate.
2. Put source publication dates and direct, claim-specific source links beside every figure and event count, with explicit no-event and no-comparable-metric states. This addresses D1, D2, D3, and D4 together.
3. Make the 390-pixel tracker readable without opening every supplier row, then capture both widths and run axe, keyboard, and three-run Lighthouse checks. This supplies the missing evidence for D6 through D9 and the accessibility blocker.
