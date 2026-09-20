# After measurements — preview deployment

Measured 2026-09-20 against the `preview` branch build
(`https://security-market-pulse-git-preview-pikeholdings.vercel.app/`, `/issues/`,
`/issues/2026-w36/`). All tooling ran inside the OrbStack dev VM (Playwright's bundled Chromium,
`orb run -m dev`), using the same commands and scripts as the baseline measurement, with only the
target URL and output paths changed. Raw tool output sits in `evidence/after/measure/`. These are
lab numbers, not opinions, and this session did not fix anything. Every number below was actually
run; nothing here is estimated.

One thing to read every row against: this is a Vercel **preview** deployment, not production. It
carries an `x-robots-tag: noindex` response header (Vercel's standard preview behaviour) and, on
some page loads, an extra `vercel.live` "preview feedback" toolbar script and iframe that will not
exist once this is promoted to production. Both are called out below wherever they change a number.

## 1. Performance (Lighthouse, home page, median of 3 runs)

Mobile = default simulated throttling; Desktop = `--preset=desktop`. Command, unchanged from
baseline: `npx --yes lighthouse <url> --chrome-flags='--headless=new --no-sandbox'
[--preset=desktop]`. All six runs (3 mobile, 3 desktop) completed with no errors.

| Metric | Production (baseline) | Preview (measured) |
|---|---|---|
| Performance score | 0.76 | 0.73 |
| LCP | 4356 ms | 4545 ms |
| CLS | 0 | 0 |
| TBT | 45 ms | 93 ms |
| FCP | 3857 ms | 3930 ms |
| Speed Index | 3857 ms | 4032 ms |
| Total transfer size | 371,455 bytes | 376,643 bytes (376,486 bytes excluding the preview-only `vercel.live` toolbar) |
| Number of requests | 13 | 14 (13 excluding `vercel.live`) |
| HTML document transfer size | 24,823 bytes | 27,630 bytes |
| Total JS transfer bytes | 229,021 bytes | 230,933 bytes (230,776 excluding `vercel.live`) |
| Total CSS transfer bytes | 10,321 bytes | 10,798 bytes |
| LCP element | `h1#issue-hero-heading` ("Record earnings from CrowdStrike, Zscaler, Palo Alto...") | same element and same headline text |

**Desktop:**

| Metric | Production (baseline) | Preview (measured) |
|---|---|---|
| Performance score | 0.98 | 0.94 |
| LCP | 859 ms | 1201 ms |
| CLS | 0.00056 | 0.0129 |
| TBT | 0 ms | 0 ms |
| Total transfer size | 371,451 bytes | 435,711 bytes (376,608 bytes excluding the preview-only `vercel.live` toolbar, which added an extra ~59 KB feedback-widget document on desktop only) |
| Number of requests | 13 | 18 (15 excluding `vercel.live`) |
| HTML document transfer size (main document only) | 24,823 bytes | 27,625 bytes |
| Total JS transfer bytes | 229,029 bytes | 254,343 bytes (230,753 excluding `vercel.live`) |
| Total CSS transfer bytes | 10,289 bytes | 10,798 bytes |

Per-run performance scores: mobile 0.88 / 0.73 / 0.73 (median 0.73), desktop 0.96 / 0.94 / 0.92
(median 0.94). This is more run-to-run variance than the baseline saw (baseline: mobile 0.76 /
0.75 / 0.76, desktop 0.98 / 0.98 / 0.99). Per-run mobile LCP was 2905 / 4670 / 4545 ms; the spread
is wide enough that a single run is not reliable, which is exactly why the rubric asks for a
median of three.

Secondary Lighthouse category scores (median): Accessibility 1.00/1.00 (mobile/desktop, unchanged
from baseline), Best Practices 1.00/1.00 (unchanged), SEO 0.66/0.66 (baseline: 1.00/1.00). The SEO
drop is caused entirely by one audit, `is-crawlable`, failing because this URL serves
`x-robots-tag: noindex`. That is standard Vercel behaviour for a preview deployment and is not
expected to apply once this branch is promoted to production; it is not a defect in the page.

Third-party requests found (Lighthouse `network-requests`, checked against the page's own
origin): `fonts.googleapis.com` (1 request, a stylesheet, not render-blocking),
`fonts.gstatic.com` (5 font-file requests, not render-blocking), and `vercel.live` (1 request on
mobile, 3 on desktop — the preview feedback toolbar, not render-blocking, and not present on
production). No third-party request was flagged as render-blocking on either profile. The baseline
write-up did not itemize third-party origins for production; by its own byte arithmetic
(html+js+css bytes fall about 107 KB short of the reported total), production almost certainly
loads the same Google Fonts requests, just not broken out in that write-up.

A plain `curl` of preview `/` (no `Accept-Encoding` negotiation forcing compression) returned
237,168 bytes, versus the baseline's reported 216,418 uncompressed bytes for production — about
20,750 bytes more raw HTML, consistent with the wave 1 front-page content added on `preview`.

These are lab numbers under simulated throttling from a single VM location, not field data and not
a measure of real-user experience — same caveat as the baseline.

## 2. Accessibility tooling (axe-core 4.10.2 via Playwright + CDN script)

Ran `axe.run(document, { resultTypes: ['violations'] })` against `/`, `/issues/`, and
`/issues/2026-w36/` at 1440px and 390px (6 total page/width combinations), identical method to
baseline.

| Page | Width | Production (baseline) | Preview (measured) |
|---|---|---|---|
| / | 1440 | 0 violations | 0 violations |
| / | 390 | 0 violations | 0 violations |
| /issues/ | 1440 | 0 violations | 0 violations |
| /issues/ | 390 | 0 violations | 0 violations |
| /issues/2026-w36/ | 1440 | 0 violations | 0 violations |
| /issues/2026-w36/ | 390 | 0 violations | 0 violations |

No rule was violated on any page at either width, on preview or on production. Verified as a
genuine run: a sanity pass on the preview home page confirmed axe loaded (`axe.version` 4.10.2)
and actually evaluated the page (43 passes, 1 incomplete, 45 inapplicable, 0 violations).

## 3. Keyboard walk, `/` at 1440px (Playwright, up to 80 Tab presses)

This section's sticky/fixed check goes further than the baseline script did. The baseline only
checked whether a stop's box fell under the single tallest element pinned to `top: 0`. This run
enumerates **every** `position: sticky` and `position: fixed` element on the page, and for each Tab
stop confirms true visual occlusion with `document.elementFromPoint` (not just a bounding-box
overlap, which produced a false positive on the skip link before the elementFromPoint check was
added — the skip link sits at the same coordinates as the header until focused, then paints above
it).

| Check | Production (baseline) | Preview (measured) |
|---|---|---|
| Skip link exists and is first stop | Yes — press 1, "Skip to main content" | Yes — press 1, "Skip to main content" |
| Sticky/fixed elements found on the page | No sticky/fixed element pinned to the top was found | 15 found: `header.site-header` (`position: sticky`, `top: 0px`, rendered top 36px, height 53px) plus 14 `<th>` row/column headers inside `div.table-scroll > table.data-table` (`position: sticky`, `top: auto`, height ~32-33px each — these are sticky within a horizontally scrollable table container, not pinned to the page) |
| Stops with a visible focus indicator | 80 of 80 | 80 of 80 |
| Stops truly hidden under sticky/fixed content (confirmed by `elementFromPoint`) | 0 | 0 |
| `details`/`summary` reachable via Tab | Yes, `tabindex` 0 on the summary | Yes, `tabindex` 0 on the summary |
| Toggles with Enter | Yes — open state flipped true → false | Yes — open state flipped true → false |
| Toggles with Space | Yes — open state flipped true → false | Yes — open state flipped true → false |
| Tab presses to reach text "Signed by" | Not reached in 80 presses | Not reached in 80 presses |

The sticky header (`header.site-header`) does exist on preview and did not exist on production
(baseline explicitly found none). It did not hide any focus stop: the bounding-box check flagged
one apparent overlap (press 1, the skip link, against the header) but the `elementFromPoint` check
showed the skip link paints on top of the header when focused, so it is not actually hidden. The
14 sticky table headers are confirmed contained inside their own scrollable table wrapper and never
overlapped a focus stop.

On preview, press 28 sits at y=2576 and press 29 at y=2961, and "Signed by" sits at y=2711 (from
the position measurement below), which falls in that gap. Same finding as baseline: the sentence
containing "Signed by" has no focusable element inside it, so keyboard focus jumps over it without
landing — this holds on preview even though the page's layout has changed enough that "Signed by"
now sits at y=2711 (1440px) instead of the baseline's y=5137.

## 4. Target size, `/` at 390px (links, buttons, `summary`; inline sentence links excluded)

| Metric | Production (baseline) | Preview (measured) |
|---|---|---|
| Total `a`/`button`/`summary` elements found | 240 | 261 |
| Excluded as inline links inside a sentence | 1 | 7 |
| Eligible elements checked | 239 | 254 |
| Elements smaller than 24×24 CSS px | 0 | 0 |

None of the 254 eligible targets on preview falls under 24×24px, so there is no "ten smallest" list
to report, matching the baseline's finding. Preview has a "Feed" link in primary navigation that
baseline did not have (a visible 34×14px feed link plus a 0×0 collapsed-nav counterpart, both
excluded from the failing count the same way the seven baseline nav links were: not currently
rendered at this width, not counted as failing).

## 5. Reflow, `/` at 320×640

| Metric | Production (baseline) | Preview (measured) |
|---|---|---|
| `document.documentElement.scrollWidth` | 320px | 320px |
| Viewport width | 320px | 320px |
| Horizontal scrolling at the document level | No | No |

No page-level horizontal scrollbar appears on preview, same as production. The overflow sample
(capped at 40 elements, same cap as the baseline script) shows the same pattern as baseline: a
`table.tempo-table` inside a `div.table-scroll` wrapper extends past the viewport width (right edge
at 346px against a 320px viewport), but `.table-scroll` is a horizontally scrollable container by
design, so it is a contained, intentional scroll region and not page-level reflow breakage.

## 6. Contrast on small text (<14px computed font size), `/` at 1440px

| Metric | Production (baseline) | Preview (measured) |
|---|---|---|
| Text nodes under 14px checked | 1,219 | 1,299 |
| Failing 4.5:1 (all locations, including the dark top bar) | 0 | 0 |
| Failing 4.5:1, dark top bar only | 0 | 0 |
| Failing 4.5:1, everywhere else | 0 | 0 |

No small text on preview fails 4.5:1 contrast against its resolved effective background, same
result as production, using the same ancestor-walking effective-background method as baseline.

## 7. Headings, `/`

| Metric | Production (baseline) | Preview (measured) |
|---|---|---|
| Total heading elements (h1–h6) | 108 | 115 |
| Empty or whitespace-only headings | 0 | 0 |
| Heading level skips (e.g., h2 → h4) | 0 | 0 |

Same clean result as baseline: no empty headings, no level skips, on a page with seven more heading
elements than production.

## 8. Position measurements, `/`

The page's structure changed enough between baseline and preview (the "wave 1" front-page merge)
that the absolute pixel offsets below are not directly comparable in isolation — they are reported
as measured, with the document height for scale.

| Element | Production 1440×900 — y (px) | Production 1440×900 — % of doc | Preview 1440×900 — y (px) | Preview 1440×900 — % of doc |
|---|---|---|---|---|
| Document height | 15,022px | — | 17,084px | — |
| "Signed by" paragraph | 5,137 | 34.2% | 2,711 | 15.9% |
| "What we now think" heading | 4,682 | 31.2% | 2,256 | 13.2% |
| "Infrastructure is running ahead" | 5,269 | 35.1% | 14,157 | 82.9% |

| Element | Production 390×844 — y (px) | Production 390×844 — % of doc | Preview 390×844 — y (px) | Preview 390×844 — % of doc |
|---|---|---|---|---|
| Document height | 17,715px | — | 21,437px | — |
| "Signed by" paragraph | 7,323 | 41.3% | 5,078 | 23.7% |
| "What we now think" heading | 6,258 | 35.3% | 4,013 | 18.7% |
| "Infrastructure is running ahead" | 7,455 | 42.1% | 16,616 | 77.5% |

| Lane items (Formation/Absorption/Prints/Capital cards) | Production 1440×900 | Production 390×844 | Preview 1440×900 | Preview 390×844 |
|---|---|---|---|---|
| Fully visible in the first viewport | 2 | 1 | 0 | 0 |
| Total on the page | 23 | 23 | 23 | 23 |

"Fully visible" means the card's full bounding box sits between y=0 and the bottom of that first
viewport, with no scrolling. Preview shows the "Signed by" verdict and "What we now think" much
higher up the page (both moved from roughly a third of the way down to roughly an eighth to a
sixth of the way down), consistent with the wave 1 change putting the market picture first. No lane
item is fully visible without scrolling on preview at either width, where baseline had 2 (1440) and
1 (390) fully visible.

## 9. Disclosure count, `/`

| Metric | Production (baseline) | Preview (measured) |
|---|---|---|
| Total `<details>` elements | 41 | 41 |
| `open` in the live DOM after page load (Playwright, `networkidle` + 1s) | 8 | 8 |

Same count on both: 41 total disclosures, 8 open after hydration (confirmed by name: Network &
edge, Cloud security, Data, Identity, SecOps, AI runtime, Platform, Infrastructure — the same eight
domain-tempo vendor groups as baseline). Raw server-rendered `open` count was not re-checked with
`curl` + grep for preview; not measured for this run.

## 10. Word counts, `/`

| Metric | Production (baseline) | Preview (measured) |
|---|---|---|
| Visible word count, all disclosures closed | 3,098 | 3,577 |
| Total word count of prerendered HTML text, including closed disclosures | 5,235 | 5,610 |

Preview carries about 479 more visible words and 375 more total words than production, consistent
with new front-page content from the wave 1 merge.

## Chrome-height measurement (for rubric D4 test 4)

The rubric's "site chrome" defined term is "everything above the first line of page content,
measured by DOM as the top offset of the first content element," tested at 390px in D4 test 4
("site chrome takes no more than a quarter of the viewport height, measured by DOM"). Measured on
preview at 390×844:

| Measurement | Value |
|---|---|
| Top offset of `#overview` | 221px |
| Top offset of the first text inside `#overview` | 221px |

Both land at the same pixel because the first text inside `#overview` sits immediately at the top
of that section with no further offset. For context only (this run was not asked to score D4): a
quarter of an 844px viewport is 211px, so 221px sits slightly above that line.

## What could not be measured and why

- **Lighthouse's own LCP-element audit** (`largest-contentful-paint-element`) does not exist in the
  installed Lighthouse version, same as baseline — the LCP element above was recovered from the
  `lcp-breakdown-insight` audit's node data, matching baseline's method exactly.
- **Third-party render-blocking status** was checked (`renderBlockingStatus` field on each network
  request); none of the found third-party requests were render-blocking. The baseline write-up did
  not run this check, so there is no baseline comparison figure for it, only the preview number.
- **The raw server-rendered `open` count for `<details>` elements** (item 9's `curl` + grep check)
  was not re-run for preview; only the post-hydration DOM count was measured. Baseline ran both and
  found 0 vs. 8; only the "after load" number (8) is reported here for preview.
- **D10 level-5 tests 4, 5 and 6** (chart text/table alternatives reachable without a pointer,
  landmark and `time`/`datetime` usage throughout, and non-text contrast at 3:1 on control borders,
  focus indicators and chart marks) were not measured in this session — no script in either the
  baseline or the after tooling checks them, and the rubric itself says test 6 fails as "not
  measured" until that sample exists. They are scored as not passing in the D10 test table below,
  per the rubric's own instruction not to guess.
- Nothing else was blocked. Lighthouse, axe-core, and all Playwright measurements ran directly
  against the preview URL with no Vercel authentication gate, no CSP blocking the CDN script tag,
  and normal VM egress to the preview host, `cdnjs.cloudflare.com`, `fonts.googleapis.com`,
  `fonts.gstatic.com` and `vercel.live`.

## Rubric tests — D9 (Performance) and D10 (Accessibility), preview only

Rubric: `docs/active/fable-run/site-rubric.md` v2.1. Mechanical scoring rule (from the rubric): 0 =
no level-3 test passes; 1 = at least one but fewer than half of level-3 tests pass; 2 = at least
half but not all level-3 tests pass; 3 = all level-3 pass and fewer than half of level-5 pass; 4 =
all level-3 pass and at least half (but not all) of level-5 pass; 5 = all level-3 and all level-5
pass.

### D9 — Performance

**Level 3**

| # | Test | Number that decides it | Answer |
|---|---|---|---|
| 1 | Mobile lab LCP at or under 2.5 seconds | 4,545 ms | No |
| 2 | CLS at or under 0.1 at both profiles | mobile 0, desktop 0.0129 | Yes |
| 3 | Mobile lab TBT at or under 300 ms | 93 ms | Yes |
| 4 | Desktop lab LCP at or under 1.5 seconds | 1,201 ms | Yes |

3 of 4 level-3 tests pass (test 1 fails). That is at least half but not all.

**Level 5** (recorded for completeness; does not raise the score because not all level-3 tests
passed)

| # | Test | Number that decides it | Answer |
|---|---|---|---|
| 1 | Mobile LCP at or under 1.8s and TBT at or under 150ms | LCP 4,545 ms, TBT 93 ms | No (LCP fails) |
| 2 | Total transfer at or under 500KB and JS at or under 200KB compressed | total 376,643 bytes (under 500KB); JS 230,933 bytes / 225 KB (over 200KB) | No |
| 3 | HTML document at or under 100KB compressed | 27,630 bytes | Yes |
| 4 | No render-blocking third-party request | none of `fonts.googleapis.com`, `fonts.gstatic.com`, `vercel.live` is render-blocking | Yes |

**D9 score: 2** (at least half of level-3 tests pass, not all; the mechanical rule stops the score
at 2 regardless of the level-5 results above).

### D10 — Accessibility

**Level 3**

| # | Test | Number that decides it | Answer |
|---|---|---|---|
| 1 | Zero critical/serious axe violations on `/`, `/issues/`, newest issue at both widths | 0 violations across all 6 page/width combinations | Yes |
| 2 | Every interactive element reachable by keyboard with a visible focus indicator, and focus never hidden under sticky content | 80 of 80 tab stops had a visible focus indicator; 0 of 80 were hidden under sticky/fixed content (confirmed by `elementFromPoint`) | Yes |
| 3 | No text fails 4.5:1 contrast, including small metadata | 0 of 1,299 small-text (<14px) nodes fail 4.5:1 at 1440px | Yes |
| 4 | Page reflows at 320 CSS px with no horizontal scroll | `scrollWidth` 320px = viewport 320px, no horizontal scroll | Yes |
| 5 | No empty headings; heading levels do not skip | 0 empty headings, 0 level skips out of 115 headings | Yes |

All 5 level-3 tests pass.

**Level 5**

| # | Test | Number that decides it | Answer |
|---|---|---|---|
| 1 | Zero axe violations of any impact on the three routes at both widths | 0 violations, all 6 combinations | Yes |
| 2 | Every pointer target at least 24×24 CSS px or a listed exception | 0 of 254 eligible targets under 24×24px at 390 | Yes |
| 3 | Skip link is first focus stop AND signed judgment reachable within 15 Tab presses | skip link is press 1 (yes); "Signed by" not reached in 80 presses (no) | No |
| 4 | Every chart has a text or table alternative reachable without a pointer | not measured | No (not measured) |
| 5 | Landmarks and `time` elements with `datetime` used throughout | not measured | No (not measured) |
| 6 | Non-text contrast meets 3:1 on control borders, focus indicators and chart marks | not measured; rubric states this test fails as "not measured" until the sample exists | No (not measured) |

2 of 6 level-5 tests pass, which is fewer than half.

**D10 score: 3** (all level-3 tests pass, and fewer than half of level-5 tests pass).
