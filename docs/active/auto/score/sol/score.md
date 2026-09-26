# Security Market Pulse site score, rubric v3.0

- **Deployment:** https://security-market-pulse-git-preview-pikeholdings.vercel.app/
- **Scored:** 2026-09-26, 15:11 UTC.
- **Scorer:** GPT-6 Sol, blind scoring run.
- **Served commit:** `190ecd498594e340c5aef9c5c1a5abd23cd80b92` is the best-supported identification, **inferred**, not proved by deployment metadata. `git rev-parse origin/preview` returned this SHA; its commit time was 15:00:27 UTC and the preview response's `Last-Modified` was 15:01:06 UTC. The response did not expose a commit SHA.
- **Composite:** **59.4 / 100**, **not fit for purpose: mislabelled figure, stale beyond the line, judgment on live pages, and accessibility assurance failure**. The accessibility result means the required axe and keyboard checks could not be established without a browser; it is not a claim that axe found a violation.

## Evidence and method

`H` means the served [home page](https://security-market-pulse-git-preview-pikeholdings.vercel.app/); `C` means [corrections](https://security-market-pulse-git-preview-pikeholdings.vercel.app/corrections/); `CSS` means the served [stylesheet](https://security-market-pulse-git-preview-pikeholdings.vercel.app/assets/index-B9Vb5wF9.css); `JS` means the served [bundle](https://security-market-pulse-git-preview-pikeholdings.vercel.app/assets/index-DDwT_JCG.js). Capture command: `curl -sSL -D /tmp/sec-market-preview-headers.txt -o /tmp/sec-market-preview-home.html H`, with the literal home URL substituted for `H`; the same `curl -sSL -o` form fetched `C`, `CSS`, and `JS`. Primary SEC documents were fetched with `curl -sSL -A 'Security Market Pulse blind scoring (research; contact: jesse@keatingpike.com)' URL`. All source URLs below returned HTTP 200. `curl -H 'Accept-Encoding: gzip' -w '%{size_download}'` measured 28,575 bytes for HTML, 154,545 for JavaScript, and 9,772 for CSS. No browser, rendered capture, axe, keyboard run, or Lighthouse run was available. A **read from markup** result is a CSS/HTML inference, not a visual or interaction measurement.

For D1 level-3 test 3, I parsed the `Rev. growth` cells, deduplicated by the displayed supplier name, and took ten from the 19 nonempty unique rows with `random.Random(20260926).sample(pool, 10)`. The pool and seed are reproducible from `curl H` and Python's standard `random` module. Source values below were checked against the linked primary document, and SEC filing recency was checked with `curl -A 'Security Market Pulse blind scoring (research; contact: jesse@keatingpike.com)' https://data.sec.gov/submissions/CIK##########.json`. The two Microsoft rows fail the company's metric and period labels even though 18% is a real Microsoft *annual companywide* number.

| Randomly sampled live figure | Primary-source check |
|---|---|
| SentinelOne +21%, Q Jul 26 | [Q2 FY2027 release](https://www.sec.gov/Archives/edgar/data/1583708/000158370826000052/sentineloneq227exhibit991.htm): revenue $292 million, up 21%; matches. |
| Palo Alto Networks +34%, Q Jul 26 | [Q4 FY2026 release](https://www.sec.gov/Archives/edgar/data/1327567/000132756726000019/ex991q426earningsrelease.htm): revenue $3.41 billion, up 34%; matches. |
| CrowdStrike +26%, Q Jul 26 | [Q2 FY2027 release](https://www.sec.gov/Archives/edgar/data/1535527/000153552726000029/crwd-20260826xex991.htm): revenue $1.47 billion, up 26%; matches. |
| Zscaler 25%, Q Jul 26 | [Q4 FY2026 release](https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm): revenue $898.2 million, up 25%; matches. |
| Varonis Systems +18.3%, Q Jun 26 | [Q2 2026 release](https://www.sec.gov/Archives/edgar/data/1361113/000117184326004948/exh_991.htm): revenue $180.023 million versus $152.163 million, or 18.31%; matches at one decimal. |
| Microsoft Entra ID 18%, Q Jun 26 | [Microsoft FY2026 10-K](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm): $331.839 billion versus $281.724 billion, up 18% for the **full fiscal year across Microsoft**. The filing gives no Entra ID revenue growth. The product and quarter labels are wrong. |
| Microsoft Defender for Office 365 18%, Q Jun 26 | The same [Microsoft 10-K](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm) supplies annual companywide growth, not this product's quarterly growth. The product and quarter labels are wrong. |
| SailPoint 16.8%, Q Jul 26 | [Q2 FY2027 10-Q](https://www.sec.gov/Archives/edgar/data/2030781/000203078126000021/sail-20260731.htm): revenue $308.813 million versus $264.359 million, or 16.82%; matches at one decimal. |
| Tenable +8.6%, Q Jun 26 | [Q2 2026 release](https://www.sec.gov/Archives/edgar/data/1660280/000166028026000032/q22026financialresults-ear.htm): revenue $268.5 million, up 8.6%; matches. |
| JFrog +29%, Q Jun 26 | [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1800667/000119312526340294/frog-20260630.htm): revenue $163.8 million versus $127.2 million, reported as 29% growth; matches. |

Three additional checks specifically probe the 14-day staleness blocker. All three old values are still in H's visible, uncollapsed `#landscape` cards under “Tracked suppliers and the latest sourced figure for each.” The newer values are for the **same ARR-growth metric**.

| Live landscape figure | Superseding company report | Age beyond newer report at scoring |
|---|---|---|
| Netskope +31% | [11 Mar 2026 release](https://www.sec.gov/Archives/edgar/data/2063196/000119312526102142/ck0002063196-ex99_1.htm) says ARR growth 31%; [2 Sep 2026 release](https://www.sec.gov/Archives/edgar/data/2063196/000119312526380188/ntsk-ex99_1.htm) says 27%. | 24 days. |
| Rubrik +32% | [4 Jun 2026 release](https://www.sec.gov/Archives/edgar/data/1943896/000194389626000041/rubrikinc-991pressrelease4.htm) says subscription ARR growth 32%; [27 Aug 2026 release](https://www.sec.gov/Archives/edgar/data/1943896/000194389626000055/rubrikinc-991pressrelease7.htm) says 33%. | 30 days. |
| SailPoint +28% | [18 Mar 2026 release](https://www.sec.gov/Archives/edgar/data/2030781/000162828026019034/sailpointinc-20260131x991x.htm) says ARR growth 28%; [9 Sep 2026 release](https://www.sec.gov/Archives/edgar/data/2030781/000162828026061015/sailpointinc-20260731x991x.htm) says 25%. | 17 days. |

The newer release dates to 26 September are shown in the final column; all exceed 14 days. The main tables carry newer figures for these suppliers, but the landscape still presents their older growth rates as latest. The blocker applies to **any shown figure**. The freshness cap is narrower: it asks whether a supplier's **newest shown figure** lags its newest company figure by more than 30 days. The main-table figures are current, so that cap does not apply on this evidence. No coverage-gap cap applies: all 12 declared domains have suppliers, and the site explicitly names excluded areas.

## Fit-for-purpose blockers

1. **Mislabelled figure: FAIL.** H's `#domain-identity` and `#domain-email` tables call Microsoft Entra ID and Microsoft Defender for Office 365 “18% · Q Jun 26” under `Rev. growth`; Microsoft's [10-K](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm) reports 18% for the *full year and whole company*, with no separate growth for either product.
2. **Stale beyond the line: FAIL.** H's live `#landscape` still says “Netskope +31%,” “Rubrik +32%,” and “SailPoint +28%” as latest figures, despite the newer same-metric company releases linked above being 24, 30, and 17 days old respectively.
3. **Judgment on a live page: FAIL.** H's live `#research-depth` section says “Not a lead — mature-category check” for Horizon3.ai and “Capital, not demand” for an acquisition; H also retains “How a posture is set.” C quotes “Watch whether it survives as a product or becomes a feature.” These are interpretive or forward-looking statements on live pages, even though archive pages are exempt.
4. **Run-status truth: PASS, limited to available evidence.** H says “Figures checked 26 Sep 2026 · every source collected.” Same-day preview commit history includes the collection proof run and status-line fix (`git log -8 --format='%h %cI %s' origin/preview`); H has no direct statement of a failed source. The run log was outside this blind read, so collection completeness was not independently established.
5. **Accessibility failure: FAIL as an assurance gate.** The specified zero-critical/zero-serious axe results at 1440 and 390, and keyboard operation, cannot be proved from HTML/CSS or run without a browser. CSS also gives `.evidence-link--compact` 0 minimum height, `.6875rem` text and only `.2rem` horizontal padding, so the 24-by-24 target test is unsupported. This is a verification failure, not an observed axe result.

## Dimension scores

The score rule is applied mechanically. Tests requiring a viewport, interaction, axe, Lighthouse, or a capture are still answered yes/no from served HTML/CSS where possible, labelled **read from markup**; unproved measurements are no. Level-5 credit cannot lift a dimension while a level-3 test fails.

### D1 — Freshness without fail: 4/5, weight 22

**Level 3:**
1. **Yes.** H: “Figures checked 26 Sep 2026 · every source collected.”
2. **Yes, read from markup.** H puts `AS OF <time dateTime="2026-09-26">` in the rail before `<main>`; CSS has the rail before the header at both widths. Actual first-screen visibility was not rendered.
3. **Yes for recency.** The seeded ten-figure sample above found no newer company financial release for the same figure more than 14 days old. The two Microsoft rows are mislabelled, which fails blocker 1 but is a separate question from this test's recency check. Three additional live landscape figures fail blocker 2 and the freshness cap.
4. **Yes.** H has an uncollapsed `<section id="tracker-changed">` headed “What changed in the last 30 days,” with dated `<time>` rows.

**Level 5:**
1. **No.** H's CrowdStrike cell has `Q Jul 26`, while its `src` button labels the source “2026-09-25”; the [release](https://www.sec.gov/Archives/edgar/data/1535527/000153552726000029/crwd-20260826xex991.htm) was 26 August. A publisher date is available through JS evidence, but each figure does not display a reliable publication date separately from the 26 September check date.
2. **Yes, conditional.** No declared source failure is shown in H's status line; the naming requirement is not triggered in this served state.
3. **Yes.** H's uncollapsed changed list explicitly dates its newest item 24 Sep 26.
4. **Yes.** H says “Tracked figures arrive through the week as companies report them”; H's method says they are updated as companies report, without a conflicting cadence.

**Cap:** All four level-3 tests pass, as do three of four level-5 tests, giving 4. The stale landscape figures fail blocker 2, but the newer main-table figures keep the narrower freshness cap from applying. **To reach 5:** show the actual publication date for each figure separately from the site check date.

### D2 — Coverage: 4/5, weight 15

**Level 3:**
1. **Yes.** H's uncollapsed `#tracker-coverage` lists all 12 domains with a sentence each, including “Identity — Identity and access management, privileged access management, and identity governance.”
2. **Yes.** H contains 12 `<article id="domain-...">` sections and 81 table rows across them; each domain has six or seven rows.
3. **Yes.** H's `#tracker-coverage` has an uncollapsed “Not covered” list naming news, product reviews, physical security, GRC, insurance, and other outside domains.
4. **Yes.** Each domain table has an `Events, 12 mo.` column; H shows a type and date where an event exists, such as “latest restructuring, 2 Sep 26,” and `0` where none is present.

**Level 5:**
1. **No.** Domain IDs such as `#domain-identity` are stable, but supplier rows have no `id` or linkable supplier anchor in H.
2. **Yes.** H states “12 domains, 74 tracked suppliers.”
3. **Yes.** H says “Figures are listed, not ranked; being listed is not a recommendation and being absent is not a criticism.”
4. **Yes.** A supplier present in a domain has its own row and event count, including `0`; an absent supplier has no row. H also states the declared exclusions.

**Cap:** No coverage-gap cap. **To reach 5:** give every supplier row a stable anchor and make it addressable from the domain index or a direct URL.

### D3 — Deciding a supplier's footing from facts alone: 2/5, weight 20

**Level 3:**
1. **No.** H's `#domain-identity` mixes public-company revenue growth, product-line rows with Microsoft-wide annual growth, and private suppliers with `–`; these are not the same metric and period for every supplier.
2. **Yes, read from markup.** H's index links `#domain-identity` and the other 11 IDs; the same anchor list is in the mobile CSS. A live tap was not performed.
3. **Yes for a named desktop row, read from markup.** H's CrowdStrike row puts +26% Q Jul 26, +26% Q Apr 26, public ownership, and “1 · latest results, 26 Aug 26” in the same `<tr>`. Phone interaction is separately tested below.
4. **No.** H's old `#landscape` and `#research-depth` content includes interpretive language such as “Not a lead — mature-category check.”

**Level 5:**
1. **No.** H shows median revenue growth in some tables, but `#domain-managed-security`, `#domain-secops`, `#domain-appsec`, `#domain-ot-iot`, and `#domain-ai-security` have no median row or explicit unavailable reference point.
2. **Yes, read from markup and JS.** H renders `button.tracker-table__sort` on each named column, and JS carries the sort handler. Sort behavior was not run in a browser.
3. **No, read from markup.** The under-a-minute task cannot be timed without a rendered interaction, and phone rows add an expansion step.
4. **No, read from markup.** CSS hides `td:not(:first-child)` on phone until a row gains `.tracker-row--expanded`; desktop columns start open.

**To reach 3:** make the comparison basis explicit for every row, especially companywide figures placed under product names, and move the interpretive legacy sections out of the live page.

### D4 — Evidence legibility and reconstructability: 4/5, weight 13

**Level 3:**
1. **Yes, read from markup and JS.** H places a `src` evidence button beside each nonempty tracker figure; JS's evidence record renders a canonical source `href` after activation.
2. **Yes for checked sources.** The ten sampled sources above resolve to company releases or SEC documents. JS stores their `canonicalUrl` values; no checked source was an internal self-link. This is a sample, not proof of every source in the library.
3. **Yes.** H's `#market` introduction defines revenue growth as year-over-year reported GAAP revenue for the named quarter; it is already visible without opening the closed method section.
4. **Yes, read from markup and JS, with a labeling problem.** H shows the quarter in each cell and “Figures checked 26 Sep 2026” above; JS evidence records hold distinct `publicationDate` and `economicPeriod` fields. Yet the button `aria-label` uses 25 September as “source” date for older releases, which confuses retrieval with publication.

**Level 5:**
1. **Yes, read from JS.** JS's evidence record renders source organization, `<time dateTime={publicationDate}>`, economic period, and canonical link together after one evidence-button activation. The interaction was not run.
2. **No.** H displays `–` in private or segment `Rev. growth` cells without a per-row explanation that a comparable company metric was not disclosed; the general method statement does not identify the affected supplier.
3. **Yes.** H's closed `#method` can be opened in one click and says a lone trade-press distress report does not publish; its sourcing ladder identifies which primary records can publish alone.
4. **No.** H's evidence buttons open source records, but JS's evidence-record link area contains no correction link; the mail link sits in the general footer.

**To reach 5:** explain every `–` at the row and put a correction link in the evidence record; also label publication and retrieval dates accurately.

### D5 — Trust: 2/5, weight 12

**Level 3:**
1. **No.** H and C contain the judgment examples cited in blocker 3.
2. **Yes.** H's `#method` states facts are “published automatically — no human approval step, and no machine judgment”; it is one `<details>` click away.
3. **Yes.** C is a stable route and lists corrections dated 20 and 21 September; JS contains “No corrections have been published” for an empty record.
4. **Yes.** H has an uncollapsed mail link to `jesse@keatingpike.com` and names Jesse Pike.

**Level 5:**
1. **No.** H names Jesse Pike but does not state his relationship to tracked suppliers.
2. **No.** H says inclusion is a data change, but gives no supplier-selection rule or statement that operator partners and competitors use the same evidence standard.
3. **No.** H links an issue archive and thesis, but still embeds older landscape and market calls on the live front page.
4. **Yes.** C says the original issue wording stays in the record with a dated correction beside it, while standing-table fixes are dated and listed.

**To reach 3:** remove interpretive text from H and C's live explanatory copy while preserving historical corrections as clearly marked quotations.

### D6 — Density and scanability: 2/5, weight 4

**Level 3:**
1. **No, read from markup.** H has six or seven rows per domain and CSS uses `.35rem .5rem` table-cell padding, but the required 1440-by-900 capture was unavailable, so eight-or-whole-table visibility was not established.
2. **Yes, read from CSS.** `.tracker-cell--numeric` is right aligned with `font-variant-numeric:tabular-nums`; dates, periods, and source buttons use distinct mono/muted styles.
3. **No, read from CSS.** `body` is 16px and prose max width is `68ch`, but `.tracker-table` is `.8125rem` (13px), below the 14px body-text threshold.
4. **Yes.** H's `Events, 12 mo.` column distinguishes `0` from counts with a named latest event and date.

**Level 5:**
1. **No, read from markup.** H includes 12 full tables plus the older landscape, activity, charts, method, and research sections; a sub-6,000-pixel DOM height was not measured and is not supported by this structure.
2. **Yes.** Each `article.tracker-domain` contains a `<table class="tracker-table">` with consistent columns.
3. **Yes, read from CSS.** Continuous prose uses 16px body text; sub-13px styles are short metadata, labels, or source controls.
4. **No, read from markup.** A full-domain 1440-pixel scan requires a rendered viewport; no capture was available.

**To reach 3:** raise the 13px table text to at least 14px while retaining row density, then verify a whole-domain desktop capture.

### D7 — Phone: 2/5, weight 4

**Level 3:**
1. **No, read from markup.** At 390px the 12-link domain index follows the masthead and run line before any supplier table; the CSS does not compact it enough to establish suppliers on the first 844px screen. No rendered first screen was available.
2. **Yes, read from markup.** CSS sets a 56px header and a compact rail, well under 211px (one quarter of 844px) before page content; exact DOM offset was not measured.
3. **No, read from CSS.** `.evidence-link--compact` has `min-height:0`, 11px text, and small padding; it does not establish a 24-by-24 target.
4. **Yes, read from markup.** CSS sets `html{overflow-x:clip}` and at 640px and below converts table rows and cells to block layout with `.tracker-table-scroll{overflow-x:visible}`. Actual 390/320 scroll was not measured.

**Level 5:**
1. **No, read from markup.** Mobile hides fact cells until the row is expanded; desktop shows them without a click.
2. **No, read from CSS.** Mobile keeps `.tracker-figure__period` at 12px and compact source text at 11px.
3. **Yes, read from markup.** The `#domain-*` jump list remains in H, and mobile CSS has no rule hiding it.
4. **No, read from CSS.** `td:not(:first-child){display:none}` until `.tracker-row--expanded` means figures are hidden in every collapsed supplier row.

**To reach 3:** expose a domain's supplier figures on the first phone screen and enlarge the source targets to 24 by 24 pixels.

### D8 — Accessibility: 2/5, weight 4

**Level 3:**
1. **No; browser required.** No axe run at either width on H or C was possible, so zero critical and serious violations is unproved.
2. **Yes, read from markup and CSS.** H uses native anchors/buttons for jumps, sorting, and evidence; CSS has `:focus-visible` styling on sort and evidence controls, and a skip link moves into view on focus. Keyboard operation was not executed.
3. **No; rendered contrast audit required.** CSS exposes text colors including `#57606e` muted metadata and several backgrounds, but every text/background pairing was not measured at both widths.
4. **Yes, read from markup.** The mobile CSS blocks table cells and clips horizontal overflow on `html`; this supports 320px reflow, though a rendered 320px scroll check was unavailable.

**Level 5:**
1. **No; browser required.** No axe run of any impact was possible.
2. **No, read from CSS.** Compact `src` buttons do not establish 24-by-24 pointer targets or a documented exception.
3. **No, read from markup.** The skip link is the first focusable element in H, but reaching `#market` within 15 actual Tab presses cannot be verified without keyboard operation.
4. **Yes.** H uses `<main>`, `<nav>`, `<header>`, `<section>`, and many `<time dateTime="...">` elements throughout the tracker.

**To reach 3:** run axe and keyboard checks at the specified widths, fix any findings, and include target-size and contrast measurements.

### D9 — Performance: 0/5, weight 3

**Level 3:**
1. **No; Lighthouse required.** No median of three mobile LCP runs; `curl` transfer timing is not LCP.
2. **No; Lighthouse required.** No CLS measurement at either profile.
3. **No; Lighthouse required.** No mobile TBT measurement.
4. **No; Lighthouse required.** No desktop LCP measurement.

**Level 5:**
1. **No; Lighthouse required.** No mobile LCP/TBT median.
2. **No; browser transfer record required.** The measured compressed core files total 192,892 bytes and JS alone is 154,545 bytes, but font and other runtime requests were not included in a complete page transfer.
3. **Yes.** `curl -H 'Accept-Encoding: gzip' -w '%{size_download}' H` returned 28,575 compressed bytes, below 100 KB.
4. **No, read from markup.** H has a render-blocking Google Fonts stylesheet `<link href="https://fonts.googleapis.com/css2?..." rel="stylesheet">` in `<head>`.

**To reach 1:** obtain the required three-run Lighthouse medians so at least one measured level-3 threshold can pass.

### D10 — Machine legibility: 4/5, weight 2

**Level 3:**
1. **Yes.** `curl H` returns all 12 domain tables and their figures in the HTML before executing JS.
2. **Yes.** H has valid parseable `application/ld+json` with `@type: Report`, `publisher`, and `dateModified: 2026-09-26`; `python3 -m json.tool` can parse the script content.
3. **Yes.** H links `/feed.xml`, `/issues/index.json`, and `/sitemap.xml` is declared by [robots.txt](https://security-market-pulse-git-preview-pikeholdings.vercel.app/robots.txt).
4. **Yes.** A Python `html.parser` pass over H found zero empty `h1`–`h4` and zero duplicate IDs.

**Level 5:**
1. **No.** H's discoverable JSON routes describe issues, corrections, and the ledger; none exposes current run status plus domains and each supplier's latest figure as structured data.
2. **No.** H has domain IDs but no per-figure anchor IDs, and no matching structured-data identifiers.
3. **Yes.** H's JSON-LD publisher is an `Organization` with stable URL `https://securitymarketpulse.com/`.
4. **Yes.** [robots.txt](https://security-market-pulse-git-preview-pikeholdings.vercel.app/robots.txt) explicitly says `User-agent: *` and `Allow: /`.

**To reach 5:** publish a linked current-tracker JSON endpoint with run state, domains, suppliers, and stable IDs shared with HTML figures.

### D11 — Craft: 1/5, weight 1

**Level 3:**
1. **No, read from CSS.** CSS defines IBM Plex Sans and Archivo as two sans families, exceeding the one-sans-family test.
2. **Yes, read from CSS.** CSS has a green accent on a light neutral base; pink alert and gold warning are semantic status colors.
3. **No, read from markup.** A spacing scale is present, but collisions, clipping, and overflow at three widths cannot be cleared without rendered pages; `html{overflow-x:clip}` could conceal overflow.
4. **No, read from markup.** H retains an `aria-hidden` header mark and rail divider that carry no information.

**Level 5:**
1. **No; greyscale capture required.** No rendered greyscale image was available.
2. **No.** H uses different source patterns in tracker rows, the old landscape, and the research library, so the repeated evidence pattern is not identical.
3. **No, read from markup.** The old landscape cards and “How a posture is set” band read as a separate promotional presentation beside the tracker.

**To reach 2:** use one sans family and remove information-free decoration, then inspect 1440, 390, and 320px renders for collisions.

## Highest-value changes

1. Correct the two Microsoft product rows' company/period attribution and add a check that rejects companywide annual metrics in product-level quarterly cells. This clears the observed mislabelling blocker and the random-sample failure.
2. Remove or date the live legacy landscape and activity material, including its stale ARR growth figures and interpretive copy; keep the dated analysis in the archive. This clears the observed staleness and judgment blockers and lifts D1, D3, and D5.
3. Make phone rows and evidence links usable without tiny targets or hidden facts, then run the required axe, keyboard, viewport, and Lighthouse checks. This directly addresses D7–D9 and the accessibility assurance blocker.
