# Independent score — Security Market Pulse, rebuilt front page (wave 1, after)

**What was scored:** the front page (`/`), the archive (`/issues/`) and the newest issue permalink
(`/issues/2026-w36/`) of Security Market Pulse as deployed on the `preview` branch.
**URL:** https://security-market-pulse-git-preview-pikeholdings.vercel.app/
**Date scored:** 2026-09-20
**Scorer:** claude-sonnet-5, independent scorer, task T6-9
**Rubric:** `docs/active/fable-run/site-rubric.md` v2.1
**Blind rule:** followed. I did not open `score-baseline-v2.md`, `score-baseline.md`,
`evidence/baseline/independent-scores.md`, `RUN-STATE.md` or `design-spec.md` at any point in this
session.

**id="market" check:** confirmed on the first `curl` of `/` — the served HTML contains `id="market"`
once. No retry loop was needed.

## The result

**Composite: 44.4 / 100 — not fit for purpose: comparison validity (Blocker 2), tracked and judged
(Blocker 3).**

**Exposure denominator: 1.** Read from `docs/active/project-scorecard.md`, "Baseline — 2026-08-22":
*"The site has been shown to one person. That single number governs everything below it."* No later
entry in that file updates the figure. The composite below says nothing about whether the site has
reached, or changed the mind of, an actual security leader — that is a different question, answered
by the exposure denominator and the outcome review in the project scorecard, not by this instrument.

## Score table

| # | Dimension | Score /5 | Weight | Score÷5×Weight |
|---|---|---|---|---|
| D1 | Market picture clarity | 2 | 10 | 4.0 |
| D2 | Look back, look ahead | 2 | 7 | 2.8 |
| D3 | Freshness and reason to return | 4 | 15 | 12.0 |
| D4 | Decision value for a security leader | 1 | 20 | 4.0 |
| D5 | Evidence legibility | 3 | 12 | 7.2 |
| D6 | Density and scanability | 2 | 4 | 1.6 |
| D7 | Wayfinding | 1 | 3 | 0.6 |
| D8 | Agent legibility | 3 | 3 | 1.8 |
| D9 | Performance | 0 | 4 | 0.0 |
| D10 | Accessibility | 2 | 8 | 3.2 |
| D11 | Follow and share | 5 | 3 | 3.0 |
| D12 | Trust and authority | 2 | 10 | 4.0 |
| D13 | Craft | 1 | 1 | 0.2 |
| | **Total** | | **100** | **44.4** |

Cadence cap (D3): not triggered — newest issue published 2026-09-19, one day before scoring.
Misstated-freshness cap (D12): not triggered — no contradictory cadence statement found, and D12's
mechanical score (2) is already below the cap's ceiling.

## Blockers

**1. Factual meaning — PASS.** Seventeen figures sampled (fifteen from "The market by domain" and
the full scorecard, two from the issue lanes) against `web/src/data/prints.ts`, `web/src/data/evidence.ts`
and `web/src/data/issues/2026-w36.ts`. All seventeen matched their source on company/segment, metric,
period and units. No mislabeling found. Detail in the Blocker 1 table below.

**2. Comparison validity — FAIL.** The "Platform pressure" section (`#platforms`, nav label
"Landscape" leads here, screenshot `crop-platforms.png`) groups vendors under headings including
"Being outrun in their own motion" and writes judgments such as *"Cato Networks at +43% and Netskope
at +31% are printing faster in the same category"* directly under Zscaler's row. Zscaler's figure is
organic ARR for the quarter ended April 2026; Cato's is full calendar-year 2025 ARR growth; Netskope's
is FY26 annual ARR growth. Three different periods and, for Cato and Netskope, company-wide ARR
against Zscaler's organic-only figure. The same is true of the row grouping "Rubrik · Varonis"
judged *"Both accelerating on public numbers. The cleanest data-side signal here"* — Rubrik's figure
is subscription ARR for the quarter ended April 2026, Varonis's is SaaS ARR ex-conversions for the
quarter ended June 2026. Separately, the full scorecard (`#prints`, screenshot `crop-prints.png`)
colours every percentage figure green (`print-card__value--up`) or red/maroon
(`print-card__value--down`) by sign, across metrics that are not like for like — Fortinet's product
revenue +52% (green) sits beside Okta's cRPO +12% (red) and Cisco's FY26 security revenue +2% (red)
beside Palo Alto XSIAM's segment ARR +100% (green). The "market by domain" section explicitly
disclaims this ("labelled and not ranked... they measure different things over different periods")
and was fixed in the T6-7 fix pass to remove tone colouring; the scorecard and the platform-pressure
table were not, per the build report's own note: *"PrintGrid's scorecard uses its own separate
`print-card__value--*` classes and was not touched."*

**3. Tracked and judged — FAIL.** Every row of the "Platform pressure" table carries interpretive
text — "Refresh spike. Not yet proven as a lasting rotation," "Recovered. The cloud segment is real
revenue, not a category series," "Growing faster than Zscaler organic. A split inside the category,
not a new SASE wave" — stamped only `JUDGED <time dateTime="2026-08-17">17 Aug 2026</time>` with no
name anywhere in the section. A search of that section's rendered HTML for "Jesse Pike" returns zero
matches. This is judgment (comparative, interpretive language, not a restated fact) presented with a
date but no attribution, which the rubric requires to be either signed or explicitly marked unsigned.
It is neither.

**4. Accessibility — PASS.** `axe-results.json` records zero violations across all six page/width
combinations tested (`/`, `/issues/`, `/issues/2026-w36/`, each at 1440 and 390). Every interactive
element on the page is a native `<a>`, `<button>` or `<summary>` element, and the compiled CSS
(`index-Cw-oe3ll.css`) carries a sitewide `a:focus-visible,button:focus-visible,input:focus-visible,
select:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:2px solid
var(--color-accent);outline-offset:2px}` rule plus a working skip link (`.skip-link:focus{top:1rem}`).
I did not run a live keyboard walkthrough, so this is weaker evidence than a Tab-by-Tab test; see
"tests I found ambiguous."

## Per-dimension test tables

### D1 — Market picture clarity — score 2/5

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. One plain line says what the site is, who for, who writes it, both widths | 3 | Y | `wave1-home-1440-viewport.png` and `wave1-home-390-viewport.png`: "A practitioner's read on the business of the security market... Public sources only. Written by Jesse Pike." Names the writer explicitly; names the reader only implicitly via "what it means if you run a security program" — flagged as ambiguous below. |
| 2. First screen carries this period's read as a market statement | 3 | Y | Same screenshots: h1 "Record earnings from CrowdStrike, Zscaler, Palo Alto, Rubrik and NVIDIA meet thin VC and quiet M&A — the infra-to-security lag call holds." |
| 3. No term on first screen needs another page to decode | 3 | N | The eyebrow line on the first screen reads "ISSUE 2026-W36 · WEEK ENDING 6 SEP 2026 · PUBLISHED 19 SEP 2026," an undecoded episode id, which the rubric names explicitly as disallowed. The adjacent "lag call" term is decoded in place by a site note, but the episode id is not. |
| 4. By-domain picture visible within first screen + one scroll (<1800px at 1440) | 3 | N | `docs/active/fable-run/evidence/wave1/measurements.json`: `market` section starts at 514px and the next section (`we-think`) starts at 2234px at 1440 — the six-domain, two-row grid (`market-crop-1440.png`) occupies most of that 514–2234px span, and I have no DOM measurement of the grid's own bottom edge to confirm it closes before 1800px. Treated as failing under the hard-marker rule since I cannot confirm it. |

Mechanical result: 2 of 4 level-3 tests pass — score 2 (level 5 not evaluated, since not all level-3 pass). One point to raise it: drop the visible "2026-W36" id from the first-screen eyebrow line, or fold it into already-decoded prose.

### D2 — Look back, look ahead — score 2/5

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. "What changed" visible without expanding, honest when nothing changed | 3 | Y | `we-think` section (front-page HTML, char 26573, not inside any `<details>`): "This week combined eight public-issuer earnings prints... The pattern is consistent with the standing infrastructure-to-security lag call, not a change to it." |
| 2. Tracked figures carry period+date, and reader sees previous period or direction of travel | 3 | N | Every vendor figure on the page carries a period (e.g. "APR '26"), but a full-text search of the served front-page HTML for "previously" returns zero matches — no vendor or domain currently shows a prior-period comparison anywhere on the page. |
| 3. Forward view exists, labelled judgment, carries confidence, says what would change it | 3 | Y | `crop-read.png`: "CONFIDENCE · MEDIUM," and a "What would change the call" box listing four conditions each with their own bullet. |
| 4. Every past judgment is dated and attributed (signed, or marked unsigned) | 3 | N | The Platform Pressure table's judgment rows (e.g. Fortinet: "Refresh spike. Not yet proven as a lasting rotation.") carry `JUDGED 17 Aug 2026` with no name anywhere in that section (verified: zero occurrences of "Jesse Pike" in that section's HTML). Same evidence as Blocker 3. |

Mechanical result: 2 of 4 pass — score 2. One point to raise it: add a name next to every `JUDGED` date in the Platform Pressure table, matching what the domain cards already do.

### D3 — Freshness and reason to return — score 4/5 (cadence cap not triggered)

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. Date of newest update + period visible on first screen | 3 | Y | "Updated September 19, 2026. Domain stances judged 16 Aug 2026." and "Issue 2026-w36 · week ending 6 Sep 2026 · published 19 Sep 2026," both on the first screen at both widths. |
| 2. Cadence stated as a sentence, reachable without expanding, no contradiction | 3 | Y | `#follow` section (char 51468, not gated): "Tracked figures arrive through the week as companies report them, and a signed read publishes most weeks — follow by RSS." |
| 3. What's new since previous update identifiable on front page | 3 | Y | `we-think` summary plus the deeper `#read` section's numbered "What changed" list (`crop-read.png`), both reachable by scrolling only. |
| 4. At least one way to be told about updates, visible without expanding | 3 | Y | RSS link in the header nav ("Feed") and in the `#follow` section, both plain, un-gated links. |
| 5. Period, source-published date and judgment-review date kept apart and shown | 3 | Y (ambiguous) | Period shown on the card ("APR '26"), judgment date shown separately ("JUDGED 16 Aug 2026"); source-published date is one click away in the evidence record (e.g. Fortinet's evidence `C3`, `publicationDate: '2026-07-29'`), not printed on the card itself. Scored as passing on a generous reading of "shown"; see ambiguous tests. |
| 5(L5).1 If cadence is missed, site says so automatically | 5 | N | No banner, status line, or copy anywhere on the page addresses a missed cadence; only one issue has ever been published, so the mechanism has never had to run, and I found no code-visible mechanism for it in the served page. |
| 5(L5).2 Front page differs in purpose from the issue permalink | 5 | Y | `/issues/2026-w36/`'s HTML has only six section ids (`overview`, `formation`, `absorption`, `prints-this-week`, `capital`, `we-think`) versus the front page's sixteen — the permalink omits "the market by domain," the scorecard, platform pressure and the deep thesis entirely. |
| 5(L5).3 Age of newest update is honest at a glance | 5 | Y | Every date on the page is an explicit `<time datetime>` value, not a relative "recently"; the issue is in fact one day old at scoring time. |
| 5(L5).4 Last three updates' headlines visible on front page, or as many as exist | 5 | Y | Only one issue exists, and its headline is the front page's own h1 — the small-scale honesty rule scores this on the mechanism, and the one headline that exists is shown. |

Mechanical result: all 5 level-3 pass; 3 of 4 level-5 pass (test 1 fails) — score 4.

### D4 — Decision value for a security leader — score 1/5

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. Five seconds: first screen carries a judgment statement, both widths | 3 | Y | Same h1 as D1.2, present at both 1440 and 390 (viewport screenshots). |
| 2. Thirty seconds: within 1800px at 1440, reach "what changed" and what it means | 3 | N | `measurements.json`: `we-think` (the section carrying the "what changed" statement) starts at 2234px, past the 1800px cutoff; nothing before that point states what changed, only the current by-domain postures. |
| 3. Highest-consequence events ordered or marked as such | 3 | N | The four issue lanes ("New companies and funding," "Acquisitions and consolidation," "Earnings and reported numbers," "Capital and financial position") are plain lists with no size, ranking or consequence marking — a $2.6M pre-seed round and a $32B acquisition render in the same typographic weight and position. |
| 4. At 390, same order as desktop; site chrome ≤ quarter of viewport height | 3 | N | `measurements.json`: `firstContentTop` at 390 is 221px. A 390×844 viewport's quarter-height is 211px. 221 > 211 — chrome takes 26.2% of the viewport, just over the quarter-height ceiling. |

Mechanical result: 1 of 4 pass — score 1. One point to raise it: trim roughly 10–15px from the mobile header/rail so `firstContentTop` at 390 drops under 211px — the cheapest single change identified in this review (see "three cheapest changes").

### D5 — Evidence legibility — score 3/5

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. Every tracked item names its source next to it, with a link/control | 3 | Y | Every vendor row in `market-crop-1440.png` and `crop-prints.png` carries an adjacent `evidence-link` button (e.g. "Fortinet," "Rubrik") reaching the source. |
| 2. Every judgment block shows or links its evidence within one interaction | 3 | Y | The `we-think` block carries an `evidence-link` button ("CrowdStrike, Palo Alto Networks +2"); platform-pressure rows carry similar buttons (`crop-platforms.png`). |
| 3. Tracked facts and signed judgments visually distinguishable beyond a top legend | 3 | Y | Each domain card separates a "JUDGED ... · Jesse Pike" posture line from a "Tracked suppliers and what they last reported" heading over its vendor list — the distinction repeats at the point of use, not only in the top rail legend. |
| 4. Dates of underlying events shown on items | 3 | Y | Every lane item carries a `<time dateTime>` element (e.g. "24 Aug 2026" on the Socure item). |
| 5(L5).1 Figures carry their evidentiary kind (filing, disclosure, press report...) where they appear | 5 | N | The evidentiary-kind tag (`evidence-library__class`, e.g. "FILING") only appears inside the deep evidence library, itself inside a collapsed `<details id="research-depth">`/`<details id="research">` — not next to the figure itself. |
| 5(L5).2 One interaction from figure to source, with publisher and date, without losing place | 5 | Y (unconfirmed) | `evidence-drawer-backdrop` is a `position:fixed` overlay in the CSS, and every evidence button carries `aria-label="View evidence: <source>"`, consistent with an in-place drawer; I did not capture a screenshot of the drawer open, so this is inferred from markup rather than observed. |
| 5(L5).3 Conflicting evidence/alternatives shown next to the judgment they qualify | 5 | N | `evidence.ts` records a `conflictingEvidenceIds` field internally, but no rendered UI on the page surfaces a counter-view next to a judgment; the "we will not call" and "avoid" lists state what the site declines to conclude, not opposing evidence. |
| 5(L5).4 A way to report a wrong figure is reachable from the evidence itself | 5 | N | The "send a correction" mailto link lives in the separate `#next` section, not inside the evidence drawer/card itself. |

Mechanical result: all 4 level-3 pass; 1 of 4 level-5 pass — score 3.

### D6 — Density and scanability — score 2/5

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. ≥8 items per 1440×900 list screen, ≥4 per 390×844 | 3 | Y | `crop-prints.png`: the scorecard's card grid packs well over eight vendor cards into any 900px band, both at desktop and in the mobile capture. |
| 2. Items differing greatly in consequence differ visibly | 3 | N | `crop-prints.png`: a $2.6M-scale item and a $32B item (Wiz) render as identically sized, identically weighted cards with no size cue, amount column, or grouping by consequence. |
| 3. Tabular figures, aligned; metadata has consistent treatment | 3 | Y | `print-card__value{font-family:var(--font-mono)...}` — all figures use IBM Plex Mono, a monospaced (tabular-by-default) face, and metadata consistently uses the `.mono`/`.stamp-label` classes. |
| 4. Body text ≥14px; line length ~50–80 characters at 1440 | 3 | Y | `body{font-size:16px;line-height:1.6}` in the compiled CSS — well above the 14px floor; no evidence of excessive line length in the captured screenshots. |

Mechanical result: 3 of 4 pass — score 2 (at least half, not all; level 5 not evaluated).

### D7 — Wayfinding — score 1/5

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. Permanent URL + archive lists date + verdict as a distinct labelled field | 3 | N | `/issues/` HTML: the one archive row shows an id, week, headline and "Signed by Jesse Pike · 19 Sep 2026," but no distinct verdict field — the word "holds" only appears inside the headline text, which the rubric explicitly excludes. |
| 2. Current location indicated; a past issue says so and links to the newest | 3 | N | `/issues/2026-w36/`'s HTML contains no visible text indicating it is the newest (or a past) issue — the only occurrence of "Newest" on that page is a `<link>` element's `title` attribute, never rendered. |
| 3. Main sections reachable by in-page nav at both widths | 3 | Y | Header nav (`Issue, Archive, Thesis, Landscape, Scorecard, Evidence, Method, Feed`) present in both the 1440 screenshot and the 390 screenshot (behind a "Menu" toggle). |
| 4. Every section heading and every lane item has a linkable anchor | 3 | N | Section headings mostly carry ids, but lane items do not: `grep -c 'id=' <li class="issue-lane__item">` returns none — the 23 lane items on the front page have no per-item id at all. |

Mechanical result: 1 of 4 pass — score 1. One point to raise it: add a distinct verdict chip to each archive row, sourced from the issue JSON's existing `thesis.verdict` field.

### D8 — Agent legibility — score 3/5

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. All content in prerendered HTML, extractable without scripts | 3 | Y | `curl` of `/` returns 237,168 bytes of static HTML containing the full headline, market cards and lane items — confirmed by the `id="market"` check and by direct grep of vendor names in the raw response. |
| 2. Archive + each issue available as JSON, discoverable from home/sitemap | 3 | Y | `/issues/index.json` and `/issues/2026-w36.json` both return 200 and are linked via `<link rel="alternate">` on every route and listed in `/sitemap.xml`. |
| 3. Each issue's JSON carries evidence records with source URLs | 3 | Y | `/issues/2026-w36.json`'s `evidence` array (23 entries) includes `canonicalUrl` fields, e.g. `https://www.returnonsecurity.com/p/security-funded-259` for `W36-01`. |
| 4. Valid JSON-LD on every route, with page type, author, dates | 3 | Y | `/` carries a `Report` node, `/issues/` a `CollectionPage` node, `/issues/2026-w36/` an `Article` node — each with `author.name: "Jesse Pike"`, `datePublished` and `dateModified`. |
| 5. Feed exists, advertised by autodiscovery link | 3 | Y | `<link rel="alternate" type="application/rss+xml" ... href=".../feed.xml">` on every route; `/feed.xml` returns 200 and parses as valid RSS. |
| 5(L5).1 Cold agent gets read, confidence, author, date, and by-domain picture from structured data alone | 5 | N | The issue JSON's `weThink` block does carry the read, confidence ("medium") and a signature, but no field in the JSON or JSON-LD carries the by-domain picture (the postures/horizons rendered in "The market by domain" are absent from `/issues/2026-w36.json`, whose `proposed` field is `null`). |
| 5(L5).2 Each claim/lane item has a stable anchor id, appearing in the JSON | 5 | N | Lane items in the JSON carry ids (e.g. `2026-w36-formation-1`), but the corresponding `<li class="issue-lane__item">` elements in the HTML carry no `id` attribute at all — a claim cannot be cited by URL fragment. |
| 5(L5).3 Plain-text/Markdown representation advertised | 5 | N | No `rel="alternate"` of a text or Markdown type found in any route's head. |
| 5(L5).4 Resolvable Organization/Person with stable `@id`; licence machine-discoverable | 5 | N | JSON-LD `author`/`publisher` nodes carry only `name`, no `@id`; no licence or terms statement found anywhere on the page. |
| 5(L5).5 Immutability discoverable and explained | 5 | N | `/issues/lock.json` exists and is linked, but it is a bare hash map (`{"2026-w36": "be70d2ae..."}`) with no accompanying statement, on the page or in the JSON, that published issues do not change. |
| 5(L5).6 Crawler policy stated deliberately | 5 | N | `robots.txt` reads only `User-agent: * / Allow: /` — the default, not a deliberate policy; `product-core.md` itself lists "crawler policy and content licence" as open and low priority. |
| 5(L5).7 No empty headings, no duplicate ids, any route | 5 | Y | Checked programmatically on all three routes: 0 empty headings, 0 duplicate ids (71 unique ids on `/`, 5 on `/issues/`, 15 on `/issues/2026-w36/`). |

Mechanical result: all 5 level-3 pass; 1 of 7 level-5 pass — score 3.

### D9 — Performance — score 0/5

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. Mobile lab LCP ≤ 2.5s | 3 | Not measured — fail | No Lighthouse or lab-throttled measurement tool was available in this session (no npm/node on the host, per this task's constraints). Per the rubric's own instruction, an un-measurable lab test is recorded as failing. |
| 2. CLS ≤ 0.1 both profiles | 3 | Not measured — fail | Same reason. |
| 3. Mobile lab TBT ≤ 300ms | 3 | Not measured — fail | Same reason. |
| 4. Desktop lab LCP ≤ 1.5s | 3 | Not measured — fail | Same reason. |
| 5(L5).1 Mobile LCP ≤1.8s, TBT ≤150ms | 5 | Not measured — fail | Same reason. |
| 5(L5).2 Total transfer ≤500KB, JS ≤200KB compressed | 5 | Y (credit waiting) | `curl` with `Accept-Encoding: gzip`: HTML 28,084 bytes, JS 117,114 bytes, CSS 8,208 bytes — total ≈153KB, JS well under the 200KB ceiling. |
| 5(L5).3 HTML document ≤100KB compressed | 5 | Y (credit waiting) | Same curl: HTML gzip size 28,084 bytes, well under 100KB. |
| 5(L5).4 No render-blocking third-party request | 5 | N | The page loads `https://fonts.googleapis.com/css2?...` as a plain, synchronous `<link rel="stylesheet">` with no preload/swap trick — a render-blocking third-party request. |

Mechanical result: 0 of 4 level-3 pass (all "not measured," scored as failing per the rubric's own rule) — score 0. The level-5 transfer-size passes are real but do not raise the score, per the rubric's "credit waiting" rule; a lab measurement (real device or throttled Lighthouse run) is the only thing that can move this dimension off zero.

### D10 — Accessibility — score 2/5

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. Zero critical/serious axe violations, all 3 routes, both widths | 3 | Y | `axe-results.json`: empty violation array for all six of `home-1440`, `home-390`, `issues-1440`, `issues-390`, `issue-w36-1440`, `issue-w36-390`. |
| 2. Keyboard reachable, visible focus, never hidden under sticky content | 3 | N | Global `:focus-visible` outline confirmed in CSS, but `.site-header{position:sticky;top:0;z-index:100}` creates a real risk that an anchor-jumped or tabbed-to element scrolls under the sticky header (SC 2.4.11); I found no `scroll-margin-top` compensation rule in the CSS, and did not run a live keyboard walkthrough to confirm or rule this out, so scored as failing. |
| 3. No text fails 4.5:1 contrast, including metadata | 3 | Y | Computed contrast from the site's CSS colour tokens: body text `#3a424e` on white is 10.15:1, muted metadata text `#57606e` on white is 6.36:1, the accent colour `#0b6b5e` on white is 6.4:1 — all comfortably clear 4.5:1. |
| 4. Reflows at 320px, no horizontal scroll | 3 | Not measured — fail | No 320px capture exists in the evidence set (only 1440 and 390 were captured); scored as failing for lack of evidence. |
| 5. No empty headings; heading levels don't skip | 3 | Y | Checked programmatically: 0 empty headings on any route; the heading sequence on `/` never jumps more than one level (h1→h2→h3→h4, no skips). |
| 5(L5).6 Non-text contrast (borders, focus rings, chart marks) ≥3:1 | 5 | Not measured — fail | Per the rubric's own instruction, this test fails as "not measured" until the specific computed-colour sampling exercise is done; I did not perform it. |

Mechanical result: 3 of 5 level-3 pass — score 2 (at least half, not all; level 5 not evaluated further).

### D11 — Follow and share — score 5/5

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. Follow visible on front page without expanding, both widths | 3 | Y | `#follow` section, not gated, visible by scroll at both 1440 (`follow-crop.png`) and 390. |
| 2. Follow prompt says what and how often | 3 | Y | "Tracked figures arrive through the week as companies report them, and a signed read publishes most weeks." |
| 3. Prompt appears at a moment of value, not only in a footer | 3 | Y | The follow section sits after the four issue lanes and before "Landscape" — mid-page, not a footer element. |
| 4(L5).1 Authorized capture path works end to end, tested | 5 | Y | `/feed.xml` returns 200 and is valid RSS with the current issue as an item; build report confirms an automated check (`11d feed-xml-exists-and-parses`) passed. |
| 4(L5).2 Every route has its own title/description/social card | 5 | Y | `/`, `/issues/` and `/issues/2026-w36/` each carry distinct `<title>` and `og:description` values (verified by direct comparison of the three head blocks), though all three share one static `og:image`. |
| 4(L5).3 A way to reach the author is visible without expanding | 5 | Y | `mailto:jesse@keatingpike.com` link and "Jesse Pike · jesse@keatingpike.com" text in the un-gated `#next` section. |
| 4(L5).4 Nothing implies a paid offer while none exists | 5 | Y | No pricing, subscription-tier, or "premium" language found anywhere on the page. |

Mechanical result: all 3 level-3 pass; 4 of 4 level-5 pass — score 5.

### D12 — Trust and authority — score 2/5 (misstated-freshness cap not triggered)

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. A named person signs the judgment, with a date, visibly | 3 | Y | `we-think__signature`: "Signed by Jesse Pike · 19 Sep 2026"; domain cards: "JUDGED 16 Aug 2026 · Jesse Pike." |
| 2. Method visible after ≤1 click, says how evidence becomes a call | 3 | Y | `<details id="method"><summary>How this is built</summary>...` — one click reveals a table of signal families and what each "is" and "is not" treated as; the un-gated method-band text separately states "How a posture is set." |
| 3. Site says what it will not call, and why | 3 | Y | `crop-read.png`, "We will not call": stable 0–8-quarter lag, domain-specific lag, AI compression of the lag, broad cybersecurity-boom motion — each a declined conclusion. |
| 4. Who the author is, beyond a name/address, visible after ≤1 click | 3 | N | No text anywhere on the page describes Jesse Pike beyond the name and email address — no bio, role or background line found in any section, gated or not. |
| 5. Author's professional role and relevant commercial relationships disclosed, ≤1 click | 3 | N | Zero matches anywhere on the page for "reseller," "employer," "works for," or any equivalent disclosure — despite `docs/active/product-core.md` naming this as a live, unresolved item ("the reader needs to know the author's interests... a reseller of these vendors"). |
| 5(L5).1 Corrections record at a stable address, "none to date" when empty | 5 | N | The `#next` section offers only a "send a correction" mailto prompt — no record/log page exists, and no "none to date" statement appears. |

Mechanical result: 3 of 5 level-3 pass — score 2 (at least half, not all; level 5 not evaluated further, though the corrections-record gap is noted since it would matter immediately if the level-3 gaps were closed).

### D13 — Craft — score 1/5

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. One sans family, ≤1 mono family, type scale ≤6 sizes | 3 | N | Compiled CSS defines three font-family tokens: `--font-display:"Archivo"`, `--font-sans:"IBM Plex Sans"`, `--font-mono:"IBM Plex Mono"` — two sans families, not one. The same stylesheet uses at least 20 distinct `font-size` values, far more than six. |
| 2. One accent colour on a neutral scale, light theme only | 3 | N | Four non-neutral colour tokens defined and used: `--color-accent`/`--color-success` (#0b6b5e), `--color-warning` (#6b5c28), `--color-alert` (#8e2f5e) — light-theme-only clause passes (no `prefers-color-scheme` rule found), but "one accent colour" does not. |
| 3. Spacing consistent; nothing collides/clips/overflows at 1440, 390, 320 | 3 | N (unverified at 320) | No 320px capture exists in the evidence set; scored as failing for lack of evidence at that width, though 1440 and 390 captures show no visible collision. |
| 4. No decoration carrying no information | 3 | Y | Screenshots show a spare, functional design — icons are all attached to evidence links or the search field, no purely ornamental elements found. |

Mechanical result: 1 of 4 pass — score 1.

## Tests I found ambiguous

**D1 test 1 ("who it is written for").** The description names the writer explicitly but names the
reader only by implication ("what it means if you run a security program"). I scored this a pass.
It would flip to a clear pass, removing the ambiguity, if the line named "security leaders" or
"security programs" directly as the audience, the way `product-core.md` does.

**D1 test 4 and D4 test 2 (the 1800px cutoff).** I have the market section's start (514px) and the
next section's start (2234px) from `measurements.json`, but not the exact bottom edge of the
six-domain grid itself, so I do not know whether the grid closes before or after 1800px. A single
additional DOM measurement (the bottom offset of the domain grid, not the section that follows it)
would settle this precisely.

**D3 test 5 (three kinds of date "shown").** I passed this on the reading that a one-click evidence
drawer counts as "shown," since the test's own wording does not use the rubric's "without expanding
anything" phrase the way the level-3 tests around it do. A stricter reading, requiring the
source-published date to appear without any click, would flip this to a fail.

**D4 test 4 (mobile chrome height, 221px vs. 211px).** This is a 10-pixel margin on a mechanically
precise threshold, from a measurement file I read rather than one I captured myself this session. If
the deployed preview has drifted even slightly from the `wave1` evidence folder's numbers, this could
already pass; I treated the recorded number as current since the build was merged into `preview`
before this scoring.

**D10 test 2 (focus hidden under the sticky header).** I inferred a real risk from the sticky
header's CSS and the absence of a compensating `scroll-margin-top` rule, but I did not perform a live
Tab-key walkthrough. A keyboard test showing every focus target lands clear of the header — or one
showing it doesn't — would resolve this outright.

**D5 test 5(L5).2 (the evidence drawer).** I inferred the drawer opens in place, without navigation,
from the `evidence-drawer-backdrop` CSS and the buttons' `aria-label`s, but never captured it open. A
screenshot of an opened drawer showing publisher and retrieval date would confirm the pass; its
absence, or a drawer that only shows the excerpt with no publisher/date, would flip it to a fail.

**Blocker 4 (accessibility, "operated by keyboard").** I passed this on strong circumstantial
evidence (native interactive elements, sitewide focus-visible styling, zero axe violations) rather
than a live keyboard session. This is the same underlying uncertainty as the D10 test 2 item above.

## Three cheapest changes that would raise the score most

1. **Add a name to every `JUDGED` stamp in the Platform Pressure table.** The domain cards already
   render `JUDGED <date> · Jesse Pike`; the platform-pressure rows currently render `JUDGED <date>`
   alone, with no name anywhere in that section. This is the same data (one author, one site) and the
   same template pattern already in use two sections above it, so it is a one-line change. It directly
   fixes D2 test 4 and clears Blocker 3 (tracked and judged), which is one of the two "not fit for
   purpose" flags on this score.

2. **Trim the mobile header/rail height by 10–15px.** `firstContentTop` at 390px is 221px against a
   211px ceiling (a quarter of the 844px mobile viewport) — a 10-pixel-scale CSS change (padding or
   line-height on the sticky rail/header) flips D4 test 4 from fail to pass, moving D4 from 1 of 4
   level-3 tests passing to 2 of 4, which raises its score from 1 to 2. At a weight of 20, this is the
   single largest point gain available from a change this small.

3. **Remove the sign-based colouring from the full scorecard and add a "labelled, not ranked"
   caption.** The T6-7 fix pass already proved the pattern (it stripped identical `--up`/`--down`
   tone classes from "The market by domain" and left the CSS rules themselves in place, unreferenced,
   specifically so this exact follow-up is cheap): removing the two `print-card__value--up`/`--down`
   class references from the scorecard's rendering and adding one caption sentence like the one the
   market-by-domain section already carries ("These figures measure different things over different
   periods... labelled and not ranked") clears Blocker 2 (comparison validity), the other "not fit
   for purpose" flag, for a CSS-class removal plus one sentence of copy.

Together, items 1 and 3 clear both fit-for-purpose blockers without touching a single data value, and
item 2 is the cheapest available point gain on the highest-weighted dimension.
