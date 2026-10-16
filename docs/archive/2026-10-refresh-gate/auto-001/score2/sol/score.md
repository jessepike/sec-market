# Security Market Pulse preview score — rubric v3.0

- **Deployment:** https://security-market-pulse-git-preview-pikeholdings.vercel.app/
- **Scored:** 26 September 2026 (PDT).
- **Scorer:** GPT-6 Sol, blind scorer.
- **Commit served:** `8fa5359ce6fba7dd40c0d5639273d17fda8ad3a0`, inferred from `git ls-remote origin refs/heads/preview` and the deployment's `Last-Modified: Sat, 26 Sep 2026 15:52:52 GMT`. The served HTML does not disclose a commit SHA, so this identification is not independently proven by the deployment.
- **Method:** `curl -sSL` of the live `/`, `/corrections/`, `/issues/`, `/issues/2026-w36/`, and `/thesis/` routes; `curl` of the served JavaScript and CSS; `curl -A 'Security Market Pulse independent scoring verification jesse@keatingpike.com'` for SEC filings; and company publications linked below. No browser or render was run. Every test that depends on pixels, DOM geometry, axe, keyboard operation, or Lighthouse is marked **No — unverified**, rather than described as a visual failure. Archive routes were checked for separation, not for the live-page judgment ban.

## Result

| Dimension | Score / 5 | Weight | Contribution / 100 |
|---|---:|---:|---:|
| D1 Freshness without fail | 2 | 22 | 8.8 |
| D2 Coverage | 4 | 15 | 12.0 |
| D3 Supplier footing from facts | 2 | 20 | 8.0 |
| D4 Evidence legibility | 2 | 13 | 5.2 |
| D5 Trust | 2 | 12 | 4.8 |
| D6 Density and scanability | 2 | 4 | 1.6 |
| D7 Phone | 0 | 4 | 0.0 |
| D8 Accessibility | 0 | 4 | 0.0 |
| D9 Performance | 0 | 3 | 0.0 |
| D10 Machine legibility | 4 | 2 | 1.6 |
| D11 Craft | 0 | 1 | 0.0 |
| **Composite** | | **100** | **42.0** |

**Fit-for-purpose result: not fit for purpose: mislabelled figure/segment and judgment on a live page.** The accessibility blocker also cannot be cleared without the required axe and keyboard checks. The composite describes this restricted, markup-based scoring pass; it is not a rendered-site score.

### Fit-for-purpose blockers

| Blocker | Pass / fail | One-line reason |
|---|---|---|
| 1. Mislabelled figure | **Fail** | The email table has a `Check Point` row marked `Segment` beside another `Check Point` row marked public; [Check Point names the segment Check Point Email Security](https://blog.checkpoint.com/product-updates/introducing-check-point-email-security-a-new-name-aligned-with-our-ai-driven-strategy/), so the segment's supplier label does not identify the product. The sampled numeric figures otherwise matched their sources. |
| 2. Stale beyond 14 days | **Pass in the checked sample** | Ten seeded-random public growth figures and the additional figures below showed no newer same-metric company figure more than 14 days ahead; the three targeted candidates were Cato, SailPoint, and Cyera. |
| 3. Judgment on a live page | **Fail** | The live home page's `#method` section says “PREPARE only where the account has a matching live motion,” and `/corrections/` reproduces “Watch whether it survives as a product or becomes a feature.” |
| 4. Run-status truth | **Pass on page consistency only** | `/` says “Figures checked 26 Sep 2026 · every source collected” and shows dated updates through 24 Sep; no contrary state appears on the served page. A run log was outside this blind scorer's permitted evidence. |
| 5. Accessibility | **Fail to clear** | Zero serious/critical axe findings and keyboard operation at both widths require browser checks, which this run could not perform; this is an unverified gate, not an observed violation. |

**Caps:** No freshness cap applied: none of the sampled suppliers had a newer same-metric company figure more than 30 days ahead. No coverage-gap cap applied: all twelve domain tables have suppliers, and the coverage section names excluded areas. These are observations from the live sample and markup, not a complete market audit.

## Primary-source check

The latest-growth sample was selected from the 17 distinct suppliers with a number in the live `Rev. growth` column using `random.Random(20260926).sample(sorted(suppliers), 10)`. The table records the ten selected rows, then six additional numeric checks. The site abbreviates fiscal periods as `Q Jul 26` or `Q Jun 26`; the filings establish the exact fiscal quarter for CrowdStrike, Palo Alto Networks, SailPoint, and Zscaler. All SEC requests used `curl -A 'Security Market Pulse independent scoring verification jesse@keatingpike.com'`.

| Sample | Live figure | Company release or filing check |
|---|---|---|
| Random 1, Commvault | `+11%`, `Q Jun 26` | [Q1 FY2027 release](https://www.sec.gov/Archives/edgar/data/1169561/000116956126000020/q1fy27pressrelease.htm): revenue $314.131m versus $281.978m, quarter ended 30 June 2026; 11% rounded. |
| Random 2, Cloudflare | `36%`, `Q Jun 26` | [Q2 2026 release](https://www.sec.gov/Archives/edgar/data/1477333/000147733326000053/q226exhibit991.htm): $696.1m and 36%, quarter ended 30 June. |
| Random 3, Check Point public row | `1%`, `Q Jun 26` | [Q2 2026 release](https://www.checkpoint.com/press-releases/check-point-software-reports-2026-second-quarter-financial-results/): $674m, up 1%, quarter ended 30 June. This is distinct from the mislabeled segment row. |
| Random 4, Qualys | `+11%`, `Q Jun 26` | [Q2 2026 release](https://www.sec.gov/Archives/edgar/data/0001107843/000110784326000034/qlys-20260804xex991.htm): $182.2m, 11%, quarter ended 30 June. |
| Random 5, CrowdStrike | `+26%`, `Q Jul 26` | [Q2 FY2027 release](https://www.sec.gov/Archives/edgar/data/0001535527/000153552726000029/crwd-20260826xex991.htm): $1.47bn, 26%, quarter ended 31 July. Its separate ARR figure is $5.84bn. |
| Random 6, Palo Alto Networks | `+34%`, `Q Jul 26` | [Q4 FY2026 release](https://www.sec.gov/Archives/edgar/data/0001327567/000132756726000019/ex991q426earningsrelease.htm): $3.41bn, 34%, quarter ended 31 July. Its separate NGS ARR is $9.10bn. |
| Random 7, Zscaler | `25%`, `Q Jul 26` | [Q4 FY2026 release](https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm): $898.2m, 25%, quarter ended 31 July. Its ARR is $3,771m. |
| Random 8, Tenable | `+8.6%`, `Q Jun 26` | [Q2 2026 release](https://www.sec.gov/Archives/edgar/data/0001660280/000166028026000032/q22026financialresults-ear.htm): $268.5m, 8.6%, quarter ended 30 June. |
| Random 9, Varonis | `+18.3%`, `Q Jun 26` | [Q2 2026 release](https://www.sec.gov/Archives/edgar/data/0001361113/000117184326004948/exh_991.htm): $180.0m versus $152.2m, which computes to 18.3%, quarter ended 30 June. |
| Random 10, JFrog | `+29%`, `Q Jun 26` | [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1800667/000119312526340294/frog-20260630.htm): $163.8m versus $127.2m, 29%, quarter ended 30 June. The site's investor-release URL returned HTTP 403 to `curl`; the SEC filing supplied the check. |
| Additional, SentinelOne | `+21%` and `ARR $1.218B`, `Q Jul 26` | [Q2 FY2027 release](https://www.sec.gov/Archives/edgar/data/0001583708/000158370826000052/sentineloneq227exhibit991.htm): revenue $292m, up 21%, ARR $1.218bn. |
| Additional, Netskope | `29%` and `ARR $899M`, `Q Jul 26` | [Q2 FY2027 release](https://www.sec.gov/Archives/edgar/data/2063196/000119312526380188/ntsk-ex99_1.htm): revenue $220.5m, up 29%, and ARR $899m. |
| Additional, SailPoint | `16.8%` and `ARR $1,230.7M`, `Q Jul 26` | [Q2 FY2027 release](https://www.sec.gov/Archives/edgar/data/2030781/000162828026061015/sailpointinc-20260731x991x.htm): revenue $308.813m versus $264.359m computes to 16.8%; [10-Q](https://www.sec.gov/Archives/edgar/data/2030781/000203078126000021/sail-20260731.htm) reports ARR $1,230.7m. |
| Additional, Rubrik | `+38%` and `Subscription ARR $1.66B`, `Q Jul 26` | [Q2 FY2027 release](https://www.sec.gov/Archives/edgar/data/0001943896/000194389626000055/rubrikinc-991pressrelease7.htm): revenue $427.3m, up 38%, and subscription ARR $1.66bn. |
| Additional, Cato | `ARR $415M, +42% YoY` | [Cato's 27 July 2026 announcement](https://www.catonetworks.com/news/cato-exceeds-415m-arr-fueled-42-yoy-growth-and-enterprise-demand/) says ARR surpassed $415m, up 42%. Direct `curl` of the cited 20 August blog returned a 205-byte challenge response despite HTTP 200; the company newsroom and release supplied the check. |
| Additional, Cyera | `$400M` growth investment, Sep 2026 | [Cyera's 22 September announcement](https://www.cyera.com/press-releases/cyera-announces-400-million-investment-from-goldman-sachs-to-build-the-trust-layer-for-the-agentic-enterprise) states $400m. |

**Three staleness candidates:** Cato's [company newsroom](https://www.catonetworks.com/news/) has later September releases, but its most recent disclosed ARR remains the 27 July $415m / 42% announcement; SailPoint's [SEC submissions](https://data.sec.gov/submissions/CIK0002030781.json) show the 10 September 10-Q as the latest quarter report; Cyera's [22 September release](https://www.cyera.com/press-releases/cyera-announces-400-million-investment-from-goldman-sachs-to-build-the-trust-layer-for-the-agentic-enterprise) matches the site's latest funding entry. No newer same-metric figure was found in those checks.

**Every segment row:** The live tables show nine segment rows. [Microsoft Defender for Endpoint](https://www.microsoft.com/en-us/security/business/endpoint-security/microsoft-defender-endpoint), [Defender for Office 365](https://www.microsoft.com/en-us/security/business/siem-and-xdr/microsoft-defender-office-365), and [Entra ID](https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id) are Microsoft products; the [Microsoft FY2026 10-K](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm) reports the parent, not product revenue. [Google SecOps](https://cloud.google.com/security/products/security-operations) is a Google Cloud product; the site's cited [Alphabet Q2 release](https://www.sec.gov/Archives/edgar/data/0001652044/000165204426000066/googexhibit991q22026.htm) reports Cloud revenue but does not itself name SecOps. [Palo Alto Cortex XSIAM](https://www.paloaltonetworks.com/cortex/cortex-xsiam) and [CrowdStrike Falcon Exposure Management](https://www.crowdstrike.com/en-us/platform/exposure-management/) are parent product lines with no separate figure shown. [Cisco's Splunk acquisition filing](https://www.sec.gov/Archives/edgar/data/858877/000119312524070175/d783088dex991.htm) confirms Splunk became part of Cisco. [GitHub Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security) exists, but its live row supplies no parent or source at all. [Check Point's March 2026 product notice](https://blog.checkpoint.com/product-updates/introducing-check-point-email-security-a-new-name-aligned-with-our-ai-driven-strategy/) names the email product Check Point Email Security; the site's segment row says only `Check Point`, beside a second Check Point public-company row. These checks validate product existence and parentage where stated; absence of separate product revenue is not proof that no private metric exists.

**Judgment-language grep:** Parsed text from `curl -sSL` of all five served HTML routes (`/`, `/corrections/`, `/issues/`, `/issues/2026-w36/`, `/thesis/`) and searched `leading|leader|best|accelerat|slowing|forecast|watch|prepare|no-call|boom`. The home page's closed `#method` section contains “The best check on whether customers actually spent,” “That is a no-call,” and “PREPARE only where the account has a matching live motion.” The corrections page quotes “Watch whether it survives as a product or becomes a feature.” `/issues/` contains only its chrome's negative “no forecasts” match; the issue permalink contains dated “accelerated” and “no-call” language; `/thesis/` contains dated “NO-CALL,” “accelerating,” and “Prepare” language. The rubric exempts the three archive routes from this blocker. Closed content was read from served markup, not from an opened browser section.

## Dimension tests

Evidence references to `/` and `/corrections/` below mean the deployment URLs above, fetched with `curl -sSL`. CSS evidence comes from `curl -sSL https://security-market-pulse-git-preview-pikeholdings.vercel.app/assets/index-Bde-7EmK.css`. “No — unverified” means the required observation was unavailable, not that a rendered defect was observed.

### D1 — Freshness without fail: 2/5 (22)

| Test | Yes / no | Evidence |
|---|---|---|
| L3.1 | **Yes** | `/` has `<section id="overview">` with “Figures checked 26 Sep 2026 · every source collected,” outside a `<details>`. |
| L3.2 | **No — unverified** | `/` places that date near the top, but first-screen placement at 1440 and 390 requires a render. |
| L3.3 | **Yes, sampled** | The ten seeded-random latest growth rows in the primary-source table match the companies' releases, and no newer same-metric print was found in the targeted staleness checks. |
| L3.4 | **Yes** | `/` has `<section id="tracker-changed">`, headed “What changed in the last 30 days,” with dated entries from 27 Aug–24 Sep in markup outside `<details>`. |
| L5.1 | **No** | A CrowdStrike row shows `+26% Q Jul 26 src`, but no publication date beside the figure; its button's `aria-label` gives `2026-09-25`, while the page says checked 26 Sep and the [release](https://www.sec.gov/Archives/edgar/data/0001535527/000153552726000029/crwd-20260826xex991.htm) was 26 Aug. |
| L5.2 | **No — unverified** | `/` reports every source collected; no failed-source display is exposed by this served state. |
| L5.3 | **Yes** | The dated “What changed” list begins with `24 Sep 26` on `/`, a plain date rather than only a timestamp. |
| L5.4 | **No** | `/` says figures “arrive through the week as companies report them”; it does not give a definite one-sentence refresh cadence. |

To raise D1 by one, show the checked date on both verified first screens and keep the sample current; that would complete the level-3 set.

### D2 — Coverage: 4/5 (15)

| Test | Yes / no | Evidence |
|---|---|---|
| L3.1 | **Yes** | `/` has twelve `#domain-*` jump links and `#tracker-coverage` gives each named domain one descriptive sentence. |
| L3.2 | **Yes** | `curl` of `/` yields 12 `tracker-table` domain tables, each with 6 or 7 supplier rows (81 placements across 74 unique suppliers). |
| L3.3 | **Yes** | `#tracker-coverage` has the heading “Not covered” and a seven-item list, including product reviews and physical security. |
| L3.4 | **Yes** | Every row has an “Events, 12 mo.” column; the Exabeam row displays `0`, while Palo Alto displays `2 · latest results, 1 Sep 26`. A zero is a visible absence. |
| L5.1 | **No** | Domains have ids such as `domain-identity`; supplier rows are `<tr>` without supplier ids or links, so a particular supplier has no stable anchor in served HTML. |
| L5.2 | **Yes** | `#tracker-coverage` states “12 domains, 74 tracked suppliers.” |
| L5.3 | **Yes** | `/` says “Figures are listed, not ranked; being listed is not a recommendation and being absent is not a criticism.” |
| L5.4 | **Yes** | The named supplier row remains present with `0` events when quiet; an untracked supplier has no row, and `#tracker-coverage` states the boundary. |

To raise D2 by one, give every supplier row a stable URL fragment while retaining the existing domain anchors.

### D3 — Deciding a supplier's footing from facts alone: 2/5 (20)

| Test | Yes / no | Evidence |
|---|---|---|
| L3.1 | **No** | The Network and SASE table mixes `+34% Q Jul 26` for Palo Alto with `ARR $415M, +42% YoY` and no comparable revenue-growth cell for Cato; several private rows show `–` in the named revenue-growth column. |
| L3.2 | **Yes, markup** | `/` links to each `#domain-*` article directly from the index. The anchor route is present at both widths in markup; actual phone scrolling was not rendered. |
| L3.3 | **Yes, markup** | CrowdStrike's one row contains current `+26% Q Jul 26`, prior `+26% Q Apr 26`, `Public · CRWD`, and `1 · latest results, 26 Aug 26`. |
| L3.4 | **Yes** | The table is alphabetic by supplier (`aria-sort="ascending"`); its computed median is unlabeled as a winner, and no supplier ranking language appears in table text. |
| L5.1 | **Yes** | Endpoint ends with “Median revenue growth of tracked public suppliers: +26%”; domain tables repeat a median row. Credit waits on L3.1. |
| L5.2 | **No — unverified** | Column headers are sort buttons and `aria-sort` appears in markup, but reordering was not operated. |
| L5.3 | **No — unverified** | The under-one-minute interaction test needs a browser and timed use. |
| L5.4 | **No** | CSS at `@media (width<=640px)` hides `td:not(:first-child)` until `tracker-row--expanded`, adding a tap that desktop does not require. |

To raise D3 by one, give each supplier a comparable named footing field or an explicit “not reported” value with its period in the same column; the other level-3 tests already pass from markup.

### D4 — Evidence legibility and reconstructability: 2/5 (13)

| Test | Yes / no | Evidence |
|---|---|---|
| L3.1 | **Yes, markup** | Numeric table cells place a `src` control beside each value, for example `<span class="tracker-figure__value">+26%</span> ... <button class="evidence-link">src</button>` on `/`. |
| L3.2 | **No** | The Cato evidence URL served only a 205-byte challenge to `curl`; the XSIAM evidence points to a generic investor home page; and the GitHub Advanced Security row has no evidence control. Several segment sources therefore do not resolve to a checkable document about the shown row. |
| L3.3 | **Yes** | One click on `<details id="method"><summary>How this is built</summary>` exposes the plain definition of revenue growth. |
| L3.4 | **No** | Table cells show economic-period shorthand and `src`; the source's publication date and the 26 Sep check date are not shown as distinct dates beside each figure. |
| L5.1 | **No — unverified** | A `src` button is present, but the one-interaction evidence drawer and retention of reading position were not operated. |
| L5.2 | **No** | Nonreporting supplier cells display only `–`; the row does not say why a comparable figure is absent. |
| L5.3 | **Yes** | `#method`, one click from the home page, states a five-rung sourcing ladder and says an unconfirmed trade-press report does not publish alone. Credit waits on level 3. |
| L5.4 | **No** | The table's `src` buttons have no adjacent correction route; the contact link is in the footer and on `/corrections/`. |

To raise D4 by one, replace generic or challenged figure sources with directly checkable documents and show the publication and checked dates separately at each figure.

### D5 — Trust: 2/5 (12)

| Test | Yes / no | Evidence |
|---|---|---|
| L3.1 | **No** | `/` at `#method` includes “PREPARE only where the account has a matching live motion”; `/corrections/` includes “Watch whether it survives as a product or becomes a feature.” Both are served on live routes, even though each is historical context. |
| L3.2 | **Yes** | `/` says “Sourced facts, checked and published automatically”; one click into `#method` says “no human approval step, and no machine judgment.” |
| L3.3 | **Yes** | `/corrections/` has a stable address and dated entries for 20 and 21 Sep 2026; its introduction explains how corrections are recorded. |
| L3.4 | **Yes** | `/` footer has a visible `mailto:jesse@keatingpike.com` link; `/corrections/` repeats the address. |
| L5.1 | **No** | `/` says “Run by Jesse Pike,” but gives no relationship to suppliers or the operator's reseller/integrator work. |
| L5.2 | **No** | `#tracker-coverage` gives counts and excluded areas, but no supplier inclusion rule or partner-versus-competitor evidence-standard statement. |
| L5.3 | **Yes** | `/issues/` says signed weekly issues were discontinued on 25 Sep and kept as a dated record; `/thesis/` says the analysis is no longer updated. Credit waits on L3.1. |
| L5.4 | **Yes** | `/corrections/` says a published issue is never edited after the fact and the fix is placed beside the original. Credit waits on L3.1. |

To raise D5 by one, remove or paraphrase the judgment sentences on the live home and corrections routes so the level-3 judgment test passes.

### D6 — Density and scanability: 2/5 (4)

| Test | Yes / no | Evidence |
|---|---|---|
| L3.1 | **No — unverified** | Each domain has at most seven rows in `/`, but whether all fit within a 1440-by-900 capture was not measured. |
| L3.2 | **Yes, CSS** | `.tracker-cell--numeric,.tracker-figure__value{font-variant-numeric:tabular-nums}` and numeric table columns are right aligned; periods and sources have separate styles. |
| L3.3 | **No** | `.tracker-table{font-size:.8125rem}` is 13px at the 16px root, below 14px; the CSS prose maximum is `68ch`. |
| L3.4 | **Yes, markup** | The “Events, 12 mo.” cells distinguish `0` from `2 · latest results, 1 Sep 26`. |
| L5.1 | **No — unverified** | Page height and whether essential content is closed require DOM measurement. |
| L5.2 | **Yes** | Domain comparisons are `<table class="tracker-table">` with six consistent columns. Credit waits on level 3. |
| L5.3 | **No** | `.tracker-figure__period{font-size:.75rem}` and `.evidence-link--compact{font-size:.6875rem}` put recurring reading metadata at 12px and 11px. |
| L5.4 | **No — unverified** | A full-domain no-scroll scan requires a 1440-by-900 capture. |

To raise D6 by one, make tracker body text at least 14px and show from a desktop capture that a full domain fits in one viewport.

### D7 — Phone: 0/5 (4)

| Test | Yes / no | Evidence |
|---|---|---|
| L3.1 | **No — unverified** | `/` has status, a twelve-link domain index, then tables; whether the first supplier appears within the 390-by-844 first screen needs a render. |
| L3.2 | **No — unverified** | Chrome height at 390 needs DOM measurement. |
| L3.3 | **No — unverified** | Mobile CSS gives compact evidence controls a 24px minimum, but every tap target on the page was not measured. |
| L3.4 | **No — unverified** | CSS switches the tracker table to block rows at width 640 and below, but 390- and 320-pixel document overflow was not measured. |
| L5.1 | **No** | Mobile CSS hides detail cells until a row tap; desktop shows them on load. |
| L5.2 | **No** | The tracker table is 13px and periods are 12px, below the 14px phone-body test. |
| L5.3 | **No — unverified** | The same `#domain-*` links exist in HTML, but touch operation at 390 was not tested. |
| L5.4 | **No** | Mobile CSS explicitly sets `.tracker-table tr:not(.tracker-table__median) td:not(:first-child){display:none}` until the row expands. |

To raise D7 by one, verify the 390 first screen, chrome height, targets, and horizontal reflow in a rendered phone pass; one demonstrated level-3 pass would move this restricted score to 1.

### D8 — Accessibility: 0/5 (4)

| Test | Yes / no | Evidence |
|---|---|---|
| L3.1 | **No — unverified** | Axe was not run on `/` and `/corrections/` at either width. |
| L3.2 | **No — unverified** | Links and buttons appear in HTML and CSS has `:focus-visible`, but keyboard reachability and visible focus were not operated. |
| L3.3 | **No — unverified** | Small metadata uses `--color-text-muted:#57606e`; actual contrast against every rendered background was not measured. |
| L3.4 | **No — unverified** | No rendered 320-pixel overflow measurement exists. |
| L5.1 | **No — unverified** | Zero axe findings of every impact cannot be established without axe. |
| L5.2 | **No — unverified** | Pointer-target sizes were not measured across both routes. |
| L5.3 | **No — unverified** | `/` starts with `<a href="#main">Skip to main content</a>`, but the 15-Tab count was not operated. |
| L5.4 | **Yes, markup** | `/` has `<header>`, `<main>`, `<nav>`, and `<footer>`; 24 `<time dateTime="...">` elements were found, none without a machine-readable date. Credit waits on level 3. |

To raise D8 by one, run the required axe and keyboard checks at 1440, 390, and 320 and record one verified level-3 pass.

### D9 — Performance: 0/5 (3)

| Test | Yes / no | Evidence |
|---|---|---|
| L3.1 | **No — unverified** | No median of three mobile Lighthouse LCP runs exists. |
| L3.2 | **No — unverified** | No Lighthouse CLS results at both profiles exist. |
| L3.3 | **No — unverified** | No mobile Lighthouse TBT results exist. |
| L3.4 | **No — unverified** | No median of three desktop Lighthouse LCP runs exists. |
| L5.1 | **No — unverified** | Mobile LCP and TBT thresholds require Lighthouse. |
| L5.2 | **No — unverified** | `curl -H 'Accept-Encoding: gzip' --raw` measured 20,784 bytes HTML, 146,182 bytes app JavaScript, and 9,823 bytes app CSS, but total transfer and third-party JavaScript/font assets were not measured. |
| L5.3 | **Yes** | `curl -sSL -H 'Accept-Encoding: gzip' --raw -o /dev/null -w '%{size_download}' /` measured 20,784 compressed bytes, under 100 KB. Credit waits on level 3. |
| L5.4 | **No** | `/` head includes a third-party `fonts.googleapis.com/css2?...` stylesheet, a render-blocking request by markup. |

To raise D9 by one, obtain the required three-run Lighthouse medians and meet at least one level-3 threshold.

### D10 — Machine legibility: 4/5 (2)

| Test | Yes / no | Evidence |
|---|---|---|
| L3.1 | **Yes** | A cold `curl` of `/` contains all twelve tables and supplier figures, including `data-domain="endpoint-xdr"` and `+26% Q Jul 26`. |
| L3.2 | **Yes** | `/` has valid `application/ld+json` with `@type: Report`, `publisher: Organization`, and `dateModified: 2026-09-26`. |
| L3.3 | **Yes** | `/` head advertises `/feed.xml` and `/issues/index.json` with `<link rel="alternate">`; body also links the feed. |
| L3.4 | **Yes** | Parsing served `/` found 32 ids with no duplicate and no empty headings. |
| L5.1 | **No** | Advertised JSON describes dated issues; no discoverable JSON endpoint supplies current run state, all domains, and current supplier figures together. |
| L5.2 | **No** | Domain articles have ids, but individual figures have no stable ids and no corresponding structured-data references. |
| L5.3 | **Yes** | JSON-LD publisher is an `Organization` with a stable `https://securitymarketpulse.com/` URL. |
| L5.4 | **Yes** | `curl -sSL /robots.txt` returns `User-agent: *`, `Allow: /`, and a sitemap declaration; the preview response also sets `X-Robots-Tag: noindex`. |

To raise D10 by one, publish a discoverable current-tracker JSON endpoint and stable figure ids shared with the HTML.

### D11 — Craft: 0/5 (1)

| Test | Yes / no | Evidence |
|---|---|---|
| L3.1 | **No** | CSS root declares two sans families (`IBM Plex Sans`, `Archivo`) plus one monospace family, and CSS has more than six front-page font sizes. |
| L3.2 | **No — unverified** | CSS declares accent, alert, and warning colors on neutral tokens; their actual visual use and meaning on the page were not inspected. |
| L3.3 | **No — unverified** | Consistent spacing and collision-free layout at 1440, 390, and 320 need rendered inspection. |
| L3.4 | **No — unverified** | Whether decoration carries information requires rendered inspection. |
| L5.1 | **No — unverified** | No grayscale capture was made. |
| L5.2 | **No — unverified** | Repeated-pattern visual identity cannot be established from markup alone. |
| L5.3 | **No — unverified** | Whether the page reads as one instrument rather than marketing chrome needs a visual review. |

To raise D11 by one, reduce the front-page type system to one sans family and no more than six sizes, then verify that level-3 test from the served CSS.

## Three changes with the largest expected effect

1. Fix the email segment label, remove judgment sentences from the live home and corrections routes, and complete the axe and keyboard gate. This clears the observed fit-for-purpose failures and resolves the unverified accessibility gate.
2. Put the source publication date and separate checked date beside each figure, replace generic or challenged citations with checkable documents, and expose an auditable run-status receipt. This addresses the largest-weight dimension, D1, and the source failures in D4.
3. Give each supplier a comparable footing field with an explicit nonreporting state, stable supplier anchors, and full phone facts without an extra tap. This targets D3's 20-point weight, D2's remaining level-5 test, and the phone loss of substance.
