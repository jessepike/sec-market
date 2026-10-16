# Measurements — live site, 2026-09-21

Deployment scored: https://securitymarketpulse.com (production, `main` branch as currently
served). Scorer: independent `claude-sonnet-5` instance, T7-7. All commands below were run
in the OrbStack dev VM (`orb run -m dev bash -lc '...'`), using the project's
`web/node_modules` Playwright/Chromium install. Scripts are copies of
`docs/archive/2026-09-weekly-issue/fable-run/evidence/after/*` and `evidence/after/measure/*`, with the base URL
changed from the preview deployment to `https://securitymarketpulse.com` and output paths
changed to this folder. Node module resolution for the copied `.mjs` files required the
script files to sit under `web/` at run time (ESM bare imports resolve from the importing
file's own path, not from `process.cwd()`); each script was copied into a throwaway
`web/.tmp-score-0921/` folder for the run and that folder was deleted immediately afterward,
so the working tree in `web/` is unaffected. Output files were written directly into this
evidence folder via an absolute `OUT` path or by setting the shell's working directory to
this folder before invoking `node` on the script's absolute path.

## Captures

`capture.mjs` and `measurements.mjs`, run against `/`, `/thesis/`, `/issues/2026-w36/` at
1440x900 and 390x844. Full-page and first-screen (viewport) PNGs saved with a `live-` prefix.
Two viewport-only shots (`live-thesis-390-viewport.png`, `live-issue-w36-390-viewport.png`)
were deleted after capture to keep the image count at or under ten, since the same
information is present in the corresponding full-page shot and in `measurements.json`.

Page heights (px, full document, from `capture.mjs` console output):

| Page | 1440 | 390 |
|---|---|---|
| `/` | 15,724 | 18,669 |
| `/thesis/` | 1,717 | 2,986 |
| `/issues/2026-w36/` | 5,712 | 8,137 |

Element offsets (px from top of document), from `measurements.json`:

| Element | 1440 | 390 |
|---|---|---|
| overview (the "This week" strip) | 338 | 493 |
| market (domain-by-domain section) | 505 | 804 |
| we-think | 1,770 | 3,348 |
| follow (RSS sentence) | 6,710 | 10,126 |
| landscape | 6,820 | 10,288 |
| platforms | 7,597 | 11,978 |
| prints (full scorecard) | 9,292 | 15,103 |
| hypotheses | 13,677 | 15,777 |
| read (thesis pointer) | 14,186 | 16,796 |
| method | 14,737 | 17,395 |
| next (watch-next) | 15,047 | 17,767 |

Site-chrome measurement (`chrome-height.mjs`): the DOM's actual first content element is
`<h1>` inside `<main>`, not `#overview` (which is a later "This week" strip, not the first
content on the page). Top offset of `<main>`: 89px at 1440 (9.9% of the 900px viewport), 160px
at 390 (19.0% of the 844px viewport). Both are comfortably under the rubric's 25% budget.

## Performance (Lighthouse, median of 3 runs each, `run-lighthouse.sh` + `parse-lighthouse.py`)

| Metric | Mobile | Desktop |
|---|---|---|
| Performance score | 0.74 | 0.98 |
| LCP | 4,297 ms | 945 ms |
| CLS | 0.00 | 0.022 |
| TBT | 42.5 ms | 0 ms |
| FCP | 3,870 ms | 945 ms |
| Total transfer | 377 KB | 377 KB |
| JS transfer | 227 KB | 227 KB |
| HTML document | 25.2 KB | 25.2 KB |
| Requests | 13 | 13 |
| Render-blocking third party | none | none |

Raw Lighthouse JSON was deleted after parsing per instructions; `measure/lighthouse-medians.json`
retains the parsed medians.

## Accessibility

`axe-scan.mjs` (axe-core 4.10.2, `resultTypes: ['violations']`, so the count already spans
every impact level) against `/`, `/issues/`, `/issues/2026-w36/` at 1440 and 390, plus a
supplementary `axe-scan-thesis.mjs` run against `/thesis/`: **0 violations on every route at
every width tested** (`measure/axe-results.json`, `measure/axe-results-thesis.json`).

`keyboard-walk.mjs`: 80 Tab presses from a fresh load of `/` at 1440x900.
- First stop is the skip link (`firstStopIsSkipLink: true`).
- All 80 stops show a visible focus indicator (`withVisibleIndicator: 80`, `withoutVisibleIndicator: 0`).
- No stop is hidden behind any sticky/fixed element (`hiddenBehindAnyStickyCount: 0`), of 15 sticky/fixed elements found on the page.
- The one `<details>` element sampled toggles correctly with both Enter and Space.
- "Signed by" text was not itself a tab stop's accessible name within 80 presses (the byline
  sits beside, not inside, a focusable element). Cross-referencing `keyboard-walk-offsets.mjs`
  (absolute Y per press) against the `we-think` and "signed" offsets from `main-measure.mjs`
  (1,792px / 2,049px at 1440) shows the tab order reaches that neighborhood at press 29-30, not
  within 15 presses.

`main-measure.mjs` (`measure/main-measure-results.json`):
- Reflow at 320x640: `scrollWidth === clientWidth` (320 = 320), so **no page-level horizontal
  scroll**. 40 elements were flagged as individually wider than the viewport, but all are rows
  inside `.table-scroll` containers (deliberately horizontally scrollable wide tables), not a
  document-level overflow.
- Contrast on text under 14px: 1,291 small-text nodes sampled, 0 failing 4.5:1.
- Target size at 390: 266 interactive elements, 256 eligible (10 excluded as inline-in-sentence
  links), 3 under 24x24 — all three are standalone paragraph links ("See correction" x2 at
  85x17, "Read the analysis and its record" at 237x20), each in its own `<p>`, not embedded in
  running sentence text.
- Headings: 110 total, 0 empty, 0 level skips.
- Disclosures: 41 `<details>` elements, 8 open by default.

`nontext-contrast.mjs` (control borders, focus indicator, chart marks against background):
- Focus indicator: `outline-color: rgb(18,22,28)` (near-black) on white — contrast far above 3:1.
- Control border on `button.evidence-link` and `button.nav-toggle`: border colour
  `rgb(211,216,223)` on `rgb(255,255,255)` — **contrast ratio 1.43:1**, below the 3:1 floor
  (`measure/nontext-contrast.json`).
- Chart gridlines: `#e2e8f0` strokes (decorative reference lines); one sampled data mark
  (`rect fill: rgb(0,0,0)`) has ample contrast.

`prose-fontsize.mjs`: of 199 text nodes over 40 characters, 68 render under 14px; most of
those are short metadata labels (e.g. "Tracked suppliers and what they last reported" at
10px), but genuine explanatory prose also renders at 13.6px — e.g. the "Site note" sentence
and the correction's withdrawn-comparison sentence (`measure/prose-fontsize.json`).

`density-check.mjs`: for the `.issue-lane__item` cards (the weekly lanes — funding,
acquisitions, earnings, capital), the best-case single-screen fit is **5 items at 1440x900**
and **3 items at 390x844** (`measure/density-check.json`), against the rubric's 8/4 floor.
Section-by-section average card heights: ~160-189px at 1440, ~216-281px at 390.

`evidence-click.mjs` / `evidence-click2.mjs`: clicking a `button.evidence-link` (e.g. "Cato
Networks") opens an `<aside role="dialog" aria-modal="true" class="evidence-drawer">` in place
(no navigation, focus/place preserved) containing publication date, economic period, source
class, packet label, a real `href` to the canonical source, a quoted excerpt, an
interpretation note, and a limitations/confounds note — all in one interaction. No
report-a-correction link exists inside the drawer itself.

## Structured data / agent legibility

- Raw `curl` of `/` (no JS) contains the full masthead text, "This week" headline, and the
  entire domain/lane content — confirms D8 level-3 test 1.
- `rel="alternate"` autodiscovery present for RSS (`/feed.xml`), issue index JSON
  (`/issues/index.json`), newest-issue JSON (`/issues/2026-w36.json`), a publication ledger
  (`/issues/lock.json`), and corrections JSON (`/corrections.json`).
- `/issues/2026-w36.json` items carry `evidenceIds` (e.g. `"W36-01"`) but not embedded source
  URLs or publisher/date; no `/evidence.json` or equivalent endpoint is discoverable (checked
  `/evidence.json`, `/evidence/index.json`, `/issues/2026-w36/evidence.json`,
  `/data/evidence.json` — all 404).
- JSON-LD present on `/` (`Report`), `/issues/2026-w36/` (`Article`), `/issues/`, `/thesis/`,
  and `/corrections/` (all checked routes carry a script tag). Author and publisher are given
  by `name` only — neither carries a stable `@id`.
- `/llms.txt` — 404. `/robots.txt` — 200, default `Allow: /` plus a sitemap reference, no
  stated crawler policy beyond that. `/sitemap.xml` — 200.

## Text extraction

Full rendered `innerText` (with all `<details>` forced open) was captured for `/`, `/thesis/`,
`/issues/2026-w36/`, `/corrections/`, `/issues/`, and `/method/` (`extract-text.mjs`,
`measure/text-*.txt`) and used for the factual and comparison checks in the score file.
`/method/` 404s as a standalone route — its content lives at the `#method` anchor on the
front page ("How this is built").
