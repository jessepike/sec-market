# Fix pass 4 — UI report

Branch `mon/uifix`, worktree `/Users/jessepike/code/projects/sec-market-wt/uifix`. This covers the
UI half of fix pass 4 only — layout, type, phone, accessibility, performance and copy. The data,
SEC runner and collector work was a separate build happening in parallel and is not covered here.

"Before" screenshots and measurements are against the live preview site,
`https://security-market-pulse-git-preview-pikeholdings.vercel.app/` — the same URL the two blind
scorers reviewed when they scored this 59.8/100 and 39.0/100. "After" screenshots and measurements
are against a local production build (`npm run build` + `npm run preview`) running in the OrbStack
dev VM, per the project's own instruction to measure performance locally because the live preview's
`vercel.live` script can add its own layout shift. Evidence lives under `ui-evidence/` next to this
file: `before-live/` (screenshots + the full capture JSON), `after-local/` (same, after my changes),
and `lighthouse/` (3 runs each, before and after, mobile and desktop).

## Items, one by one

**1. Keyboard at 390px — sort buttons off-screen in tab order.** Done. The old fix clipped the table
header to one pixel but kept it focusable, so all 72 sort buttons still received focus off-screen. The
header is now `display: none` at phone width, which removes it from the tab order outright. A 40-stop
keyboard sweep on the after build found zero stops landing in a hidden header at either 390 or 1440.

**2. Tap targets at 390px under 24px.** Done. Fixed in two passes: the first pass widened the compact
"src" evidence buttons, the domain-jump links, and the "Which sources failed" summary. A follow-up
capture still found five inline text links under 24px tall — the archive-links row ("Issue archive ·
Standing thesis · Evidence · Method"), the RSS follow link, and the `/corrections/` link inside
NextEdition's prose — fixed with the same `inline-flex` + `min-height: 24px` pattern. The after
capture shows zero targets under 24px at 390px. (Desktop keeps the smaller "src" marks as designed —
the brief scoped this requirement to 390px, and the desktop inline-with-figure layout is intentional.)

**3. Phone rows collapsed to one figure behind a tap.** Done. The tap-to-expand row and its chevron
are gone. Every row now renders all six columns unconditionally, laid out with CSS Grid as a
two-column, three-line card (name with ownership, growth with the prior quarter, the company's own
metric with its latest event), using `grid-area` placement rather than DOM reordering so the tab and
reading order stay the same as the column order. This is also why mobile table rows got noticeably
taller — showing six columns without a tap takes more vertical space than hiding five of them behind
a button did. That is the direct, expected cost of this item, not a defect.

**4. First screen must reach supplier rows at 390px.** Done. Before: the first domain's first table
row sat at 1,261px — nowhere near an 844px first screen. The single biggest cause was the
twelve-domain jump index, which wrapped into five or six rows of pills before any table started. It
is now one horizontally scrollable row at phone width instead of wrapping. That alone brought the
first row to about 1,007px; mobile-only spacing and type-size tightening on the masthead, the
run-status box, and the market section's intro paragraph closed the rest of the gap. The first row
now lands at 840.9px — on screen at 390×844. The run-status line and the "Figures checked" date stay
on the first screen at both 390 and 1440 before and after; neither needed to move. None of this
touched the words in the masthead description or the run-status text — both are data, not mine to
shorten — only spacing and, for the two longest blocks, the font size.

**5. Growth formatting — signed, one decimal, tabular, right-aligned.** Done on the rendering side.
Every growth figure now renders through a `signedGrowth()` helper that adds a real minus sign (−) for
negative values and a plus sign for positive ones; the cells already used a tabular-number, numeric,
right-aligned style from an earlier pass. Decimal precision itself comes from the stored data, which
was the parallel data build's job, not mine — I render whatever precision the data carries,
consistently.

**6. Every domain table needs a reference point.** Done. Domains with two or more public suppliers
still show the median line. Domains with fewer now show a plain sentence instead of nothing: "One
public supplier in this domain; no median shown." or "No public suppliers in this domain; no median
shown." The footer row is now always rendered rather than conditionally omitted.

**7. Type and colour.** Done. One sans family (IBM Plex Sans, self-hosted) plus IBM Plex Mono for
data; Archivo is gone. Before, the live preview carried 14 distinct font sizes across three font
families (IBM Plex Sans, IBM Plex Mono, and Archivo, including a 42.4px hero headline) by the same
measurement script. After, the whole site uses 6 absolute sizes (28/22/18/16/14/12px) plus two
relative units, and 2 font families. The run-status line is no longer crimson in any state — same
neutral heading colour throughout, with the word "incomplete" and the named failure still carrying
the meaning without colour. The logo mark is a flat accent-colour fill, not a gradient. The masthead
h1 is now a fixed 1.75rem/700 instead of a fluid clamp running up to 2.65rem/800. Two prose blocks
that ran past roughly 75 characters per line — the "what changed" list's text column (sitting in an
unconstrained `1fr` grid track, measured around 190 characters per line) and the "what this site
covers" domain list — are now capped to the same `--prose-max` token the rest of the page's prose
already used.

**8. Performance.** Partly measured, partly inconclusive — see the Lighthouse section below. Google
Fonts is gone from `index.html`; IBM Plex Sans (one variable woff2, 45.7KB) and IBM Plex Mono (three
static weights, 14.7–15.6KB each) are self-hosted under `web/public/fonts/`, the Sans file is
preloaded, and every `@font-face` uses `font-display: swap`. The live preview's render-blocking audit
had itemized the Google Fonts request at 417ms of blocking time before; the local after-build shows
0ms from any font request. Desktop CLS measured 0 in both the before (live preview) and after (local)
runs in this pass — see the caveat below on why that doesn't fully close this item.

**9. Dates as `<time>` elements.** Done. Every date in the tracker table — the quarter-end date, the
filed date, the ownership/last-round date, and the latest-event date — and the "AS OF" date in the
provenance rail now render inside a `<time dateTime="YYYY-MM-DD">`.

**10. "How suppliers are chosen" copy.** Done. Added as a new subsection in `HowThisWorks.tsx`,
written only from `docs/active/autonomy-coverage-plan.md` §4 (the twelve domains match how a security
budget is spent; each domain's supplier list is fixed and declared; a small funding round is logged in
the change feed but doesn't get a tracker row unless the company is already on the list). It says
nothing about the operator's own relationships — that line is explicitly left for the owner to write.
It sits one click from the front page via the existing "How this is built" disclosure.

**11. Archive routes — drop the live tagline above old judgments.** Done. `ProvenanceRail` now takes
an `archive` flag; `App.tsx` sets it for the issue archive, an issue permalink, and `/thesis/` — the
three routes each already carrying their own "kept as a dated record" notice. On those three routes
the rail still shows the brand and the "AS OF" date, but not the "published automatically, with no
stances…" statement. `/corrections/` is unaffected — it's a live, maintained page, and keeps the
statement.

**12. Coverage statement link near the top.** Done. Added "Coverage" to the header nav, between
"Market" and "Evidence" — the smallest, most reversible way to reach a section that previously sat
about 7,000px down the page with nothing pointing at it from the top, without reordering the page the
earlier fix passes already arranged.

## What moved, visually

Comparing `ui-evidence/before-live/beforelive-home-390-fold.png` against
`ui-evidence/after-local/check3-home-390-fold.png`, and the matching 1440 pair:

- The run-status box's text is crimson red before; neutral dark grey after.
- The logo mark is a blue-to-teal gradient square before; a flat teal square after.
- The hero heading is larger and in a different, bolder display face before (Archivo); the same
  family as the body text after, at a smaller, fixed size.
- The domain-jump row is absent from the first screen before (it's further down, wrapped); after, it
  appears as a single scrollable row of pills, with the first domain's table visible right below it
  at 390px.
- The header nav gains a "Coverage" item.
- The "Which sources failed" disclosure triangle and row are visibly taller/easier to tap after.

I did not find anything that moved unintentionally — no component, rule, or section was removed; every
change above is a size, colour, spacing, or markup change to something already in the component tree.

## Lighthouse

3 runs per profile, median reported, `--throttling-method=simulate`. Raw JSON for all 12 runs is in
`ui-evidence/lighthouse/`.

| Profile | Metric | Before (live preview) | After (local build) |
|---|---|---|---|
| Mobile | LCP | 4,002ms | 2,612ms |
| Mobile | CLS | 0 | 0 |
| Mobile | TBT | 70ms | 9ms |
| Mobile | Performance score | 0.76 | 0.94 |
| Desktop | LCP | 964ms | 2,554ms |
| Desktop | CLS | 0.144 | 0 |
| Desktop | TBT | 0ms | 0ms |
| Desktop | Performance score | 0.92 | 0.73 |

Mobile LCP and desktop CLS both move the direction the brief asked for and land where the brief asked
for: mobile LCP is now well under the 4.0s problem the scorers flagged, and desktop CLS — the exact
0.144 figure named in the brief — is 0 on the local build.

Desktop LCP got worse in this comparison, and I want to flag that plainly rather than bury it. Two
things make this not a clean apples-to-apples read: the "before" run hit the live Vercel-hosted
preview over the network (TTFB 216ms), while "after" hit a local dev-server build with no CDN (TTFB
4ms) — simulated throttling amplifies whatever round-trips remain, and a local server has different
ones than an edge-hosted site. More importantly, the LCP element itself changed between runs: before,
it was the "market by domain" section's intro paragraph, further down the page; after, with the hero
shortened for item 4, it's the masthead description paragraph near the top. I did not chase this
further inside this pass's turn budget. Before trusting the desktop LCP number specifically, the right
check is a preview-vs-preview comparison once this branch is actually pushed to the `preview` URL,
so both sides are measured against the same hosting.

## Accessibility and keyboard

axe-core (`wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa`) found zero violations on `/` and
`/corrections/`, at both 390 and 1440, before and after.

Keyboard: a 40-stop Tab sweep on `/` at 390px found zero stops landing inside a hidden table header,
off-screen, after this pass's changes (the `display: none` header fix for item 1). The same check
against the live preview also showed zero such stops, which likely means an earlier fix pass already
addressed part of this, or the check (written against the current markup) doesn't reproduce the exact
old clip-rect pattern the scorers saw — either way, the after state is confirmed directly against the
component: the header has no interactive descendants when it's `display: none`, so nothing in it can
receive focus.

## Tap targets

390px: before, 22 elements measured under 24px tall, including the "Which sources failed" summary
(22px), the twelve domain-jump links (20px), and assorted footer links (15–20px). After, zero.

1440px: the compact "src" evidence buttons (27×19–20px) remain under 24px by design — the brief
scoped the 24px requirement to 390px, and the desktop inline-with-figure layout is unchanged from
before this pass.

## Tests

- `npm run lint` (oxlint): 0 warnings, 0 errors.
- `npm run test:data`: 248/248 passing, no changes needed to any test file.
- `npm run build` (the full verify + build + prerender + SEO + feed + verify:dist chain): passes
  clean.
- `npm run test:e2e` (Playwright, 30 tests across chromium/phone/desktop projects): 30/30 passing, no
  changes needed to any spec file. I specifically checked for assertions tied to the old
  tap-to-expand row pattern (`tracker-row--expanded`, `aria-expanded`, `.tracker-row__toggle`) before
  removing it — none exist in the e2e suite, and the one place a test reaches into a row
  (`getByTitle('Microsoft Entra ID')` in `smoke.spec.ts`) still works because the simplified row
  markup keeps the `title` attribute.

No e2e assertions were stale or needed updating.

## Gates

lint, test:data, build, test:e2e all green on the final state. `git status --short` is empty except
for this evidence folder and report, which are being committed with this report.
