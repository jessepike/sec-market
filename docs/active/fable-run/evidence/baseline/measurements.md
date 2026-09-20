# Baseline measurements — securitymarketpulse.com

Measured 2026-09-20 against production (`https://securitymarketpulse.com/`, `/issues/`,
`/issues/2026-w36/`). All tooling ran inside the OrbStack dev VM (Playwright's bundled Chromium,
`orb run -m dev`); raw tool output sits in `evidence/baseline/measure/`. These are lab numbers, not
opinions, and nothing here was fixed.

## 1. Performance (Lighthouse, home page, median of 3 runs)

Mobile = default simulated throttling; Desktop = `--preset=desktop`. Command:
`npx --yes lighthouse <url> --chrome-flags='--headless=new --no-sandbox' [--preset=desktop]`.

| Metric | Mobile (median) | Desktop (median) |
|---|---|---|
| Performance score | 0.76 | 0.98 |
| LCP | 4356 ms | 859 ms |
| CLS | 0 | 0.00056 |
| TBT | 45 ms | 0 ms |
| FCP | 3857 ms | 859 ms |
| Speed Index | 3857 ms | 969 ms |
| Total transfer size | 371,455 bytes | 371,451 bytes |
| Number of requests | 13 | 13 |
| HTML document transfer size | 24,823 bytes | 24,823 bytes |
| Total JS transfer bytes | 229,021 bytes | 229,029 bytes |
| Total CSS transfer bytes | 10,321 bytes | 10,289 bytes |
| LCP element | `h1#issue-hero-heading` ("Record earnings from CrowdStrike, Zscaler, Palo Alto...") | same |

Per-run performance scores were 0.76/0.75/0.76 (mobile) and 0.98/0.98/0.99 (desktop) — low run-to-run
variance. Transfer sizes above are compressed (gzip/br); a plain `curl` of `/` reports 216,418
uncompressed bytes.

Secondary Lighthouse category scores (median): Accessibility 1.00, Best Practices 1.00, SEO 1.00 on
both mobile and desktop.

These are lab numbers under simulated throttling from a single VM location, not field data and not a
measure of real-user experience.

## 2. Accessibility tooling (axe-core 4.10.2 via Playwright + CDN script)

Ran `axe.run(document, { resultTypes: ['violations'] })` against `/`, `/issues/`, and
`/issues/2026-w36/` at 1440px and 390px (6 total page/width combinations).

| Page | Width | Violations |
|---|---|---|
| / | 1440 | 0 |
| / | 390 | 0 |
| /issues/ | 1440 | 0 |
| /issues/ | 390 | 0 |
| /issues/2026-w36/ | 1440 | 0 |
| /issues/2026-w36/ | 390 | 0 |

| Impact | Count (all 6 combos combined) |
|---|---|
| Critical | 0 |
| Serious | 0 |
| Moderate | 0 |
| Minor | 0 |

No rule was violated on any page at either width, so there is no per-rule table to report. Verified
as a genuine run, not a silent failure: a sanity pass on the home page confirmed axe loaded
(`axe.version` 4.10.2) and actually evaluated the page (42 passes, 1 incomplete, 46 inapplicable, 0
violations).

## 3. Keyboard walk, `/` at 1440px (Playwright, up to 80 Tab presses)

| Check | Result |
|---|---|
| Skip link exists and is first stop | Yes — press 1, "Skip to main content" |
| Sticky/fixed header detected | No — no `position: fixed`/`sticky` element found pinned to the top; header scrolls with the page, so no stop was hidden behind it |
| Stops with a visible focus indicator | 80 of 80 (compared computed `outline`/`box-shadow` focused vs. blurred for every stop) |
| Stops hidden behind a sticky header | 0 |
| `details`/`summary` reachable via Tab | Yes, `tabindex` 0 on the summary |
| Toggles with Enter | Yes — open state flipped true → false |
| Toggles with Space | Yes — open state flipped true → false |
| Tab presses to reach text "Signed by" | Not reached in 80 presses — see note below |

First 25 focus stops (tag, accessible name), in order:

| # | Tag | Accessible name |
|---|---|---|
| 1 | A | Skip to main content |
| 2 | A | Security Market Pulse |
| 3 | A | Issue |
| 4 | A | Archive |
| 5 | A | Thesis |
| 6 | A | Landscape |
| 7 | A | Scorecard |
| 8 | A | Evidence |
| 9 | A | Method |
| 10 | BUTTON | View evidence: Return on Security |
| 11 | BUTTON | View evidence: Return on Security |
| 12 | BUTTON | View evidence: Return on Security |
| 13 | BUTTON | View evidence: Return on Security |
| 14 | BUTTON | View evidence: Return on Security |
| 15 | BUTTON | View evidence: HiddenLayer |
| 16 | BUTTON | View evidence: AIR Security |
| 17 | BUTTON | View evidence: Palo Alto Networks & TechCrunch |
| 18 | BUTTON | View evidence: Return on Security |
| 19 | BUTTON | View evidence: Return on Security |
| 20 | BUTTON | View evidence: Return on Security |
| 21 | BUTTON | View evidence: Return on Security |
| 22 | BUTTON | View evidence: Return on Security |
| 23 | BUTTON | View evidence: CrowdStrike |
| 24 | BUTTON | View evidence: Zscaler |
| 25 | BUTTON | View evidence: SentinelOne |

Note on "Signed by": the sentence contains no focusable element, so no Tab stop lands inside it.
Tracking each stop's absolute page-Y position instead: press 33 sits at y=5002 and press 34 at
y=5558. The signature line itself sits at y=5137 and "Infrastructure is running ahead" at y=5269
(item 8) — both fall in that gap, so keyboard focus jumps over the whole region without stopping.

## 4. Target size, `/` at 390px (links, buttons, `summary`; inline sentence links excluded)

| Metric | Count |
|---|---|
| Total `a`/`button`/`summary` elements found | 240 |
| Excluded as inline links inside a sentence | 1 |
| Eligible elements checked | 239 |
| Elements smaller than 24×24 CSS px | 0 |

None of the 239 eligible targets falls under 24×24px, so there is no "ten smallest" list to report.
The smallest is 57.5×44px (four "F5" evidence-link buttons); a "Menu" button is 61×44px. Seven
primary-nav links (Issue, Archive, Thesis, Landscape, Scorecard, Evidence, Method) report a 0×0 box
at this width because the mobile nav is collapsed behind the "Menu" toggle — those are excluded from
both totals as not currently rendered, not counted as failing.

## 5. Reflow, `/` at 320×640

| Metric | Value |
|---|---|
| `document.documentElement.scrollWidth` | 320px |
| Viewport width | 320px |
| Horizontal scrolling at the document level | No |

No page-level horizontal scrollbar appears. Individual elements inside the "Tempo" section's data
tables (`table.tempo-table`, inside a `div.table-scroll` wrapper) do extend to about 346px, up to
26px past the viewport, but that wrapper is a horizontally scrollable container by design
(`overflow-x` on `.table-scroll`), so it does not create page-level reflow — it's a contained,
intentional scroll region, not a layout break.

## 6. Contrast on small text (<14px computed font size), `/` at 1440px

| Metric | Count |
|---|---|
| Text nodes under 14px checked | 1,219 |
| Failing 4.5:1 (all locations, including the dark top bar) | 0 |
| Failing 4.5:1, dark top bar only | 0 |
| Failing 4.5:1, everywhere else | 0 |

No small text on the page fails 4.5:1 contrast against its resolved effective background, including
the dark provenance bar at the top, so there is no "five worst" list to report. Effective background
was resolved by walking up the ancestor chain to the first element with a non-transparent
`background-color`, blending for partial alpha.

## 7. Headings, `/`

| Metric | Count |
|---|---|
| Total heading elements (h1–h6) | 108 |
| Empty or whitespace-only headings | 0 |
| Heading level skips (e.g., h2 → h4) | 0 |

Measured via `textContent` on each heading element, which counts nested markup. Four `h2` elements
under "Where the security market is going" (the domain-posture cards) look empty under a naive
`grep -o '<h2>[^<]*</h2>'` because their text sits inside a nested `<span>` plus additional inline
text rather than directly in the tag — but their actual accessible text (checked here) is not empty;
each carries a label like "Network / SASE" plus a full descriptive sentence.

## 8. Position measurements, `/`

| Element | 1440×900 — y (px) | 1440×900 — % of doc | 1440×900 — viewport-heights | 390×844 — y (px) | 390×844 — % of doc | 390×844 — viewport-heights |
|---|---|---|---|---|---|---|
| Document height | 15,022px | — | — | 17,715px | — | — |
| "Signed by" paragraph | 5,137 | 34.2% | 5.71 | 7,323 | 41.3% | 8.68 |
| "What we now think" heading | 4,682 | 31.2% | 5.20 | 6,258 | 35.3% | 7.41 |
| "Infrastructure is running ahead" | 5,269 | 35.1% | 5.85 | 7,455 | 42.1% | 8.83 |

| Lane items (Formation/Absorption/Prints/Capital cards) | 1440×900 | 390×844 |
|---|---|---|
| Fully visible in the first viewport | 2 | 1 |
| Total on the page | 23 | 23 |

"Fully visible" means the card's full bounding box sits between y=0 and the bottom of that first
viewport, with no scrolling.

## 9. Disclosure count, `/`

| Metric | Count |
|---|---|
| Total `<details>` elements | 41 |
| `open` in the raw server-rendered HTML (`curl` + grep) | 0 |
| `open` in the live DOM after page load (Playwright, `networkidle` + 1s) | 8 |

The 8 that end up open after load are the eight domain-tempo vendor-group disclosures (Network &
edge, Cloud security, Data, Identity, SecOps, AI runtime, Platform, Infrastructure) — client-side
code opens these specific eight after hydration even though the server sends all 41 closed.

## 10. Word counts, `/`

| Metric | Count |
|---|---|
| Visible word count, all disclosures closed | 3,098 |
| Total word count of prerendered HTML text, including closed disclosures | 5,235 |

Visible count used `document.body.innerText` (respects CSS visibility) in the page's default-load
state; the total used `document.body.textContent` with `<script>`/`<style>` removed first, which
counts text inside closed `<details>` as well.

## What could not be measured and why

- **Lighthouse's own LCP-element audit** (`largest-contentful-paint-element`) does not exist in
  Lighthouse 13.5.0 — that audit was replaced by an "insight" audit. The LCP element reported above
  was recovered from the `lcp-breakdown-insight` audit's node data instead, which carries the same
  selector and snippet.
- **Item 9's "at load" number is reported two ways** (raw HTML vs. post-hydration DOM) because they
  genuinely differ (0 vs. 8) and the task's phrasing doesn't specify which state counts — both are
  real, verified numbers, not a gap.
- Nothing else in the ten items was blocked. Axe-core, Lighthouse, and all Playwright measurements
  ran directly against production with no Vercel auth gate, no CSP blocking the CDN script tag, and
  normal VM egress to both `securitymarketpulse.com` and `cdnjs.cloudflare.com`.
