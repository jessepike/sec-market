# Independent re-score — Security Market Pulse, rebuilt front page (final)

**What was scored:** the front page (`/`), the archive (`/issues/`), the newest issue permalink
(`/issues/2026-w36/`) and the new corrections page (`/corrections/`) of Security Market Pulse as
deployed on the `preview` branch, after two further merges beyond my first score (task T6-9): the
author-name fix and mobile-chrome pass (`mon/wave1b`) and the corrections mechanism (`mon/corrections`).
**URL:** https://security-market-pulse-git-preview-pikeholdings.vercel.app/
**Date scored:** 2026-09-20
**Scorer:** claude-sonnet-5, independent scorer, task T6-14
**Rubric:** `docs/archive/2026-09-weekly-issue/fable-run/site-rubric.md` v2.1
**Blind rule:** followed. I did not open `score-baseline-v2.md`, `score-baseline.md`,
`evidence/baseline/independent-scores.md`, `RUN-STATE.md` or `design-spec.md` this session, and I did
not read the "Coordinator reconciliation" section the coordinator added near the top of my first
score file (`score-after-v2.1.md`); I only used the rest of that file plus fresh evidence.

**Pre-checks, both confirmed on the first try, no retry needed:**
- `curl -o /dev/null -w "%{http_code}"` on `/corrections/` returned 200.
- The home page HTML contains the text "CORRECTED" (one match, inside the Zscaler correction block).

## The result

**Composite: 57.2 / 100 — not fit for purpose: factual meaning (Blocker 1), comparison validity
(Blocker 2).**

**Exposure denominator: 1.** Unchanged from my first score. Read from
`docs/archive/2026-08-web-mvp/project-scorecard.md`, "Baseline — 2026-08-22": *"The site has been shown to one
person. That single number governs everything below it."* No later entry updates this. The composite
below is a craft score, not a use score.

## Coordinator note (added 2026-09-20)

The scorer's record below is left unedited. Two notes for a reader comparing it with the production
baseline of 32.8 in `score-baseline-v2.md`.

The D1 row of the score table shows 4.0 points where a score of 4 at weight 10 is 8.0. The total of
57.2 is correct and already uses 8.0.

On blocker 1 the scorer made a judgment call and said so: the two headlines are still wrong as
published, and a dated correction beside them does not make the published sentence right. The
coordinator wrote this rubric and built the correction, so it is not changing the rubric's wording
to pass its own work. Whether a locked, openly corrected error should count as a mislabelled figure
is recorded as a question for the owner and for the next outside review of the rubric. The
practical position: the error is corrected in the open on `preview`, and a gate now stops the same
mistake being published again.

On blocker 2 the scorer found two more lines in the same signed issue that use a superlative across
companies on different bases: "the strongest reacceleration among this week's prints"
(`2026-w36-prints-1`) and "the strongest print in this week's set" (`2026-w36-capital-1`). They are
in the locked issue and are the owner's signed words, like the Platform pressure wording. A second
correction would need his approval. The scorecard's green and red values come from a hand-set
`tone` field comparing a supplier with its own earlier figure; the coordinator does not count them
as a cross-supplier ranking, but the page gives no legend, and two separate readings by the scorer
took them for one.

## Score table

| # | Dimension | Score /5 | Weight | Score÷5×Weight | Changed since first score |
|---|---|---|---|---|---|
| D1 | Market picture clarity | 4 | 10 | 4.0 | Yes: 2 → 4 |
| D2 | Look back, look ahead | 2 | 7 | 2.8 | No (one test flipped inside it) |
| D3 | Freshness and reason to return | 4 | 15 | 12.0 | No |
| D4 | Decision value for a security leader | 2 | 20 | 8.0 | Yes: 1 → 2 |
| D5 | Evidence legibility | 3 | 12 | 7.2 | No |
| D6 | Density and scanability | 2 | 4 | 1.6 | No |
| D7 | Wayfinding | 1 | 3 | 0.6 | No |
| D8 | Agent legibility | 3 | 3 | 1.8 | No |
| D9 | Performance | 2 | 4 | 1.6 | Yes: 0 → 2 |
| D10 | Accessibility | 4 | 8 | 3.2 → 6.4 | Yes: 2 → 4 |
| D11 | Follow and share | 5 | 3 | 3.0 | No |
| D12 | Trust and authority | 2 | 10 | 4.0 | No (one test flipped, score unchanged) |
| D13 | Craft | 1 | 1 | 0.2 | No |
| | **Total** | | **100** | **57.2** | up from 44.4 |

Cadence cap (D3): not triggered — newest issue published 2026-09-19, one day before scoring; the
correction published 2026-09-20 does not create a new issue and does not move this. Misstated
freshness cap (D12): not triggered — checked again on the current page: the header, the rail and the
as-of line all read "20 Sep 2026" / "September 20, 2026" consistently, with no contradicting date
anywhere; D12's mechanical score (2) is already below the cap's ceiling regardless.

## Blockers

**1. Factual meaning — FAIL (new failure, not found in my first pass).** The rubric's wording: *"No
figure on the page is wrong or mislabelled as to company or segment, metric, period or units.
Checked by sampling at least ten figures against their sources."* Following the coordinator's
correction, I checked every lane headline in `2026-w36.ts` that carries a figure against its
evidence record's `economicPeriod` and `excerpt` in `evidence.ts` (ten prints/capital items plus the
thirteen formation/absorption items, twenty-three headlines in total). Two are wrong: the front page
still reads **"Zscaler FY2026 revenue grows to $898.2M, +25% YoY; ARR grows to $3,771M, +25%"**
(`2026-w36-prints-2`) and **"Palo Alto FY2026 revenue grows 34% to $3.41B; Next-Gen Security ARR
$9.10B, +63%"** (`2026-w36-prints-6`), while their evidence (`W36-15`, `W36-19`) both give
`economicPeriod: 'Quarter ended 2026-07-31'` — a fiscal-quarter figure stated as a fiscal-year
figure, exactly the failure mode Blocker 1 names. All twenty-one other lane headlines checked clean
against their evidence (for example `W36-20` Broadcom is correctly labelled "Q3," and `W36-23`
Microsoft's guidance headline carries no period label to be wrong). Every scorecard figure I sampled
in my first pass (seventeen figures) still checks out.

Both wrong headlines now sit beside a dated, attributed, equally-visible correction — a maroon-bordered,
pink-backed "CORRECTED 20 SEP 2026" block giving the right period and the right reading, with a link
to `/corrections/#C-2026-09-20-01` — and the site publishes a plain statement of policy (`/corrections/`:
*"A published issue is never edited after the fact. When something in one is wrong, the fix is a
dated note placed beside the item... with the original left in the record exactly as it was
published."*) I have to decide whether that counts as "mislabelled on the page." My reading: it does.
The rubric's test is a sampling check against the figure itself, and the sampled headline text —
"FY2026 revenue" — is still exactly as wrong, in isolation, as it was before the correction existed;
the correction sits beside it rather than inside it. A reader who reads only the bolded headline (which
is exactly what a skimming reader does, and exactly what the rubric's own sampling method does) still
receives a mislabelled figure. The correction is genuinely good practice — transparent, dated, signed,
comparable to a newspaper's published-correction convention — and it is exactly the kind of thing that
should raise D12 (trust) once the two other gaps there are closed. But good remediation of an error is
not the same claim as the error not existing on the page, and Blocker 1 asks the second question, not
the first. **What would flip this:** either edit the two original headlines so the on-page text is
correct, with the correction block explaining what changed and why (which the site's own immutability
principle currently rules out), or a rewrite of the rubric's test to explicitly read "no figure is
left wrong on the page without an equally prominent, adjacent correction giving the right figure" — a
policy call for the rubric's owner, not something I can decide for them.

**2. Comparison validity — FAIL, unchanged.** Same specific sentences as my first score, re-verified
on the current page: the "Platform pressure" table (`crop-platforms.png`; confirmed live in
`front3.html`) still groups vendors under "Being outrun in their own motion" and still writes *"Cato
Networks at +43% and Netskope at +31% are printing faster in the same category"* under Zscaler
(organic ARR, quarter ended April 2026, against Cato's full calendar-year 2025 ARR and Netskope's
FY26 annual ARR — three different bases) and *"Both accelerating on public numbers. The cleanest
data-side signal here"* under Rubrik/Varonis (different quarters, different ARR definitions). The
full scorecard still colours percentage figures green or red by sign across non-like-for-like
metrics: `grep` of the live HTML finds 17 `print-card__value--up` and 3 `print-card__value--down`
class uses. None of this changed in the last two merges. New evidence for the same defect, found
while checking Blocker 1: two lane "why it matters" lines make the identical kind of unsupported
comparison and were not touched by the correction — `2026-w36-prints-1` calls CrowdStrike's reacceleration
"the strongest reacceleration among this week's prints," and `2026-w36-capital-1` calls NVIDIA's
Data Center growth "the strongest print in this week's set" — both superlatives across companies
with different revenue bases and reporting periods, the same defect class as the Palo Alto claim that
was withdrawn by the correction, but left standing.

**3. Tracked and judged — PASS (flipped from FAIL).** Every one of the 42 `JUDGED <date>` stamps on
the live front page now carries a name: a script check stripping HTML tags and comments and matching
`JUDGED\s*\d{1,2} \w{3} \d{4}` against the same pattern followed by `· Jesse Pike` found 42 of 42
matching. Verified visually in `home-1440-platforms.png` ("JUDGED 17 AUG 2026 · JESSE PIKE" on every
row) and confirmed the same is true of the landscape, hypotheses and "what moved" sections per
`evidence/wave1b/report.md`. This closes the specific gap my first score flagged (the Platform
Pressure table's judgment rows carrying a date with no name anywhere in the section).

**4. Accessibility — PASS, now on stronger evidence.** My first score passed this blocker on
circumstantial evidence (semantic HTML, sitewide focus-visible CSS, a clean axe scan) without a live
keyboard test. `evidence/after/measurements.md` now supplies an actual keyboard walk: 80 of 80 Tab
stops show a visible focus indicator, and 0 of 80 are truly hidden under sticky or fixed content,
confirmed with `document.elementFromPoint` rather than a bounding-box check (which had flagged one
false positive on the skip link before that check was added). Axe found zero violations across all
six page/width combinations in the wave-1 evidence, zero again in the after-measurement run, and zero
again in the corrections-specific scan (`evidence/corrections/axe-results.json`: empty arrays for
`home-1440`, `home-390`, `corrections-1440`, `corrections-390`) — three independent runs across three
different commits, all clean.

## What changed since my first score

- **D1 test 3** (no undecoded id on the first screen): FAIL → PASS. The eyebrow now reads "WEEKLY
  ISSUE" as a link to the permalink, not the raw "2026-W36" id — confirmed live: a text-stripped
  search of the current HTML for "2026-w36" as visible text returns none; the string only remains in
  `href` and JSON-link attributes.
- **D1 test 4** (by-domain grid fits within 1800px at 1440): FAIL/ambiguous → PASS. `evidence/wave1b/report.md`:
  `#market` bottom moved from 2202px to 1747px, under the 1800px cutoff, from compacting the
  supplier rows.
- **D1 score:** 2 → 4 (all four level-3 tests now pass; three of four level-5 tests pass, same as
  would have been true before — the level-5 answers did not change, only the level-3 gate did).
- **D2 test 4** (every past judgment dated and attributed): FAIL → PASS, same evidence as Blocker 3.
  D2's score does not change (still 2 of 4 level-3 tests, since test 2 — a previous-period or
  direction-of-travel comparison — still has no example anywhere on the page) but the underlying test
  answer is worth recording since it is asked about explicitly by name in the rubric.
- **D4 test 2** (what changed + what it means within 1800px at 1440): FAIL → PASS. `#we-think` top
  moved from 2234px to 1779px, under the cutoff, same compaction.
- **D4 test 4** (mobile chrome ≤ quarter of viewport height): FAIL → PASS. `evidence/wave1b/report.md`:
  `#overview` top at 390 moved from 221px to 184px, under the 211px quarter-viewport line, from the
  phone-chrome tightening pass. (Note: `evidence/after/measurements.md`, captured earlier the same
  day, still shows 221px for this same measurement — that file was captured before this specific fix
  landed, which is exactly the "build before the last two merges" caveat the coordinator flagged; I
  used the more recent, purpose-built measurement instead.)
- **D4 score:** 1 → 2.
- **D9 (Performance):** 0 → 2. My first score failed all four level-3 tests as "not measured," since
  no lab tool was available in that session. `evidence/after/measurements.md` now supplies real
  Lighthouse medians: mobile LCP 4,545ms (fails the 2.5s test), CLS 0/0.0129 (passes), mobile TBT 93ms
  (passes), desktop LCP 1,201ms (passes) — 3 of 4 level-3 tests pass, giving score 2. These numbers
  predate the wave1b-second-pass and corrections merges, per the coordinator's note; neither of those
  merges plausibly changes render-blocking behaviour or bundle size enough to move LCP across the
  2.5s line, so I am treating the score as still representative, but it is not a fresh measurement of
  today's exact commit.
- **D10 (Accessibility):** 2 → 4. Three level-3 tests that I had failed for lack of evidence now pass
  on real measurement: keyboard/focus/sticky (test 2, see Blocker 4), 320px reflow (test 4:
  `evidence/after/measurements.md` — `scrollWidth` 320px equals viewport width, no horizontal scroll),
  and the axe test (test 1) is now corroborated three times over instead of once. All 5 level-3 tests
  now pass. On level 5, I checked two tests myself in the live HTML per the coordinator's instruction:
  a `<details><summary>View data table (accessible alternative)</summary>` block with a full
  `<table class="data-table">` exists for the "Market layers" chart section (test 4: PASS, reachable
  by keyboard since `details`/`summary` toggling by Enter and Space was directly confirmed in the
  keyboard walk), and `<main>`, `<nav>`, `<footer>` landmarks are present with 100 `<time dateTime>`
  elements used throughout the page (test 5: PASS). Combined with the already-passing pointer-target
  test (test 2) and zero-impact axe test (test 1), that is 4 of 6 level-5 tests passing — at least
  half, not all (test 3, 15-tab reachability of "Signed by," still fails; test 6, non-text contrast,
  is still not measured and fails per the rubric's own rule) — giving score 4.
- **Blocker 1:** PASS → FAIL. New failure, found only because the coordinator's correction directed
  me to sample lane headlines, which my first pass did not do for figures with a period label.
- **Blocker 3:** FAIL → PASS, detailed above.
- **Blocker 4:** PASS → PASS, but now backed by an actual keyboard walk instead of inference from
  markup.
- **Not changed:** D2's score (2), D3 (4), D5 (3), D6 (2), D7 (1), D8 (3), D11 (5), D12's score (2),
  D13 (1), and Blocker 2 (FAIL). Each carried forward from my first score; I spot-checked the cheap
  ones directly rather than assuming: the current CSS (new hash `index-BWuXijzw.css`, since the build
  changed) still defines three font families and more than twenty font-size values (D13 test 1 still
  fails), still defines four non-neutral colour tokens (D13 test 2 still fails), and the corrections
  route has its own distinct `<title>`/description (consistent with D11 test 4(L5).2 still passing).
  I did not re-run the full evidence-legibility (D5) or wayfinding (D7) test sets from scratch since
  nothing in the three build reports for this round touches evidence drawers, the archive page, or
  lane-item anchors — I did confirm directly that lane items (`<li class="issue-lane__item">`) still
  carry no `id` attribute, so D7 test 4 and D8 level-5 test 2 are unchanged.

## Per-dimension test tables

Tests marked **carried forward** repeat my first score's answer verbatim; I have spot-verified the
ones cheap to check (noted inline) and found no change.

### D1 — Market picture clarity — score 4/5 (up from 2)

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. One plain line: what/who-for/who-writes, both widths | 3 | Y | Carried forward. |
| 2. First screen carries a market statement | 3 | Y | Carried forward. |
| 3. No undecoded term/id on first screen | 3 | **Y (flipped)** | Live HTML: the eyebrow now reads `<a href="/issues/2026-w36/">Weekly issue</a>`, not the raw id; a text-only search for "2026-w36" as visible page text returns zero hits. |
| 4. By-domain picture within first screen + one scroll (<1800px at 1440) | 3 | **Y (flipped)** | `evidence/wave1b/report.md`: `#market` bottom now 1747px, under 1800px. |
| 5(L5).1 Each domain shows sourced, labelled, unranked vendor figures | 5 | Y | Carried forward — `market-crop-1440.png`/live HTML, alphabetical, labelled, captioned "labelled and not ranked." |
| 5(L5).2 Consolidation/distress has its own place, "none recorded" when empty | 5 | N | Re-checked live: no occurrence of "distress," "layoff," "shutdown," or "none recorded" anywhere on the page; the "absorption" lane covers M&A only. |
| 5(L5).3 Cold-reader test | 5 | Y | Judgment call: the first-screen capture alone (headline + description) supports a reader saying "a security-market intelligence read; this week's earnings were strong but funding/M&A were thin, and the lag call holds." |
| 5(L5).4 Every domain and vendor has a stable address | 5 | Y | Live HTML: `id="domain-network-sase"` etc. (six domain anchors) plus `id="vendor-network-sase-zscaler"` etc. (per-vendor anchors), both confirmed present. |

Mechanical result: all 4 level-3 pass; 3 of 4 level-5 pass — score 4.

### D2 — Look back, look ahead — score 2/5 (unchanged; one test flipped)

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. "What changed" visible without expanding | 3 | Y | Carried forward. |
| 2. Tracked figures show period+date and a previous-period/direction-of-travel comparison | 3 | N | Re-checked live: full-text search for "previously" still returns zero matches anywhere on the front page. |
| 3. Forward view labelled judgment, with confidence and change conditions | 3 | Y | Carried forward. |
| 4. Every past judgment dated and attributed | 3 | **Y (flipped)** | Same evidence as Blocker 3 — all 42 dated JUDGED stamps now carry "Jesse Pike." |

Mechanical result: 3 of 4 pass — still score 2 (test 2 alone keeps it from all-pass).

### D3 — Freshness and reason to return — score 4/5 (carried forward, spot-checked)

All five level-3 tests and the level-5 split (3 of 4) carried forward from my first score. Spot-check:
the site's "updated" date, the rail's "AS OF" date and the as-of line all now read "20 Sep 2026" /
"September 20, 2026" consistently on the live page (the site correctly moved its `LAST_UPDATED`
constant when the correction shipped), so there is no new contradiction to trigger the misstated-
freshness cap, and the correction itself is additional, fresh evidence for test 3 ("what's new is
identifiable on the front page") since the CORRECTED stamps are new content visible without
expanding anything.

### D4 — Decision value for a security leader — score 2/5 (up from 1)

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. Five seconds: judgment statement on first screen, both widths | 3 | Y | Carried forward. |
| 2. Thirty seconds: "what changed" + what it means within 1800px at 1440 | 3 | **Y (flipped)** | `#we-think` top now 1779px, under 1800px (`evidence/wave1b/report.md`). |
| 3. Highest-consequence events ordered/marked, not left to chronology | 3 | N | Unchanged: the four lanes are still plain lists with no size, ranking, or consequence marking. |
| 4. At 390, same order as desktop; chrome ≤ quarter of viewport height | 3 | **Y (flipped)** | `#overview` top at 390 now 184px against a 211px quarter-viewport line (`evidence/wave1b/report.md`, the fix built specifically for this test). |

Mechanical result: 3 of 4 pass — score 2 (at least half, not all).

### D5 — Evidence legibility — score 3/5 (carried forward)

Nothing in the last two merges touches evidence links, the evidence drawer, or the deep evidence
library. All test answers carried forward from my first score (level 3: 4 of 4 pass; level 5: 1 of 4
pass — score 3).

### D6 — Density and scanability — score 2/5 (carried forward, spot-checked)

Carried forward (level 3: 3 of 4 pass — score 2). Spot-check: the market-by-domain compaction makes
the page denser, not less dense, so test 1 (items per screen) if anything strengthens; test 2 (items
differing in consequence differing visibly) is unaffected — a small funding round and a large
acquisition still render as identically weighted cards.

### D7 — Wayfinding — score 1/5 (carried forward, spot-checked)

Carried forward (level 3: 1 of 4 pass — score 1). Spot-checked directly: lane items
(`<li class="issue-lane__item">`) still carry no `id` attribute on the live page, so test 4 still
fails; the archive row still has no distinct verdict field, and the issue permalink still has no
visible "newest/past" indicator, so tests 1 and 2 still fail.

### D8 — Agent legibility — score 3/5 (carried forward, spot-checked)

Carried forward (level 3: 5 of 5 pass; level 5: 1 of 7 pass — score 3). One new machine surface
exists (`/corrections.json`, with its own `<link rel="alternate" type="application/json">`
autodiscovery entry, confirmed live) and the per-issue JSON gained a `corrections` array — good
practice, but it does not change any of the seven level-5 answers (the by-domain picture is still
absent from structured data, lane items still have no anchor id matching their JSON id, and so on).

### D9 — Performance — score 2/5 (up from 0)

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. Mobile lab LCP ≤ 2.5s | 3 | N | `evidence/after/measurements.md`: median mobile LCP 4,545ms. |
| 2. CLS ≤ 0.1 both profiles | 3 | Y | Mobile 0, desktop 0.0129, both under 0.1. |
| 3. Mobile lab TBT ≤ 300ms | 3 | Y | Median 93ms. |
| 4. Desktop lab LCP ≤ 1.5s | 3 | Y | Median 1,201ms. |
| 5(L5).1 Mobile LCP ≤1.8s and TBT ≤150ms | 5 | N | LCP fails (4,545ms). |
| 5(L5).2 Total transfer ≤500KB, JS ≤200KB compressed | 5 | N | Total ≈368KB (passes), JS ≈225.5KB (fails the 200KB line). |
| 5(L5).3 HTML ≤100KB compressed | 5 | Y | 27,630 bytes. |
| 5(L5).4 No render-blocking third-party request | 5 | Y | Lighthouse's `renderBlockingStatus` field: none of `fonts.googleapis.com`, `fonts.gstatic.com`, `vercel.live` render-blocking. |

Mechanical result: 3 of 4 level-3 pass — score 2. These numbers are from the build before the
wave1b-second-pass and corrections merges; I judged neither merge likely to move LCP/TBT/CLS
meaningfully (both are layout/copy changes, not script or font changes), but this is a lab
measurement of an earlier commit, not today's exact one.

### D10 — Accessibility — score 4/5 (up from 2)

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. Zero critical/serious axe violations, 3 routes, both widths | 3 | Y | Three independent scans (wave1, after-measurement, corrections) all report zero violations. |
| 2. Keyboard reachable, visible focus, never hidden under sticky | 3 | **Y (flipped)** | `evidence/after/measurements.md`: 80 of 80 Tab stops have a visible focus indicator; 0 of 80 are hidden under sticky/fixed content, confirmed by `document.elementFromPoint` (not just bounding-box overlap). |
| 3. No text fails 4.5:1 contrast | 3 | Y | 1,299 small-text nodes checked at 1440px, 0 failures. |
| 4. Reflows at 320px, no horizontal scroll | 3 | **Y (flipped)** | `scrollWidth` 320px = viewport width, no horizontal scroll (the one `.table-scroll` overflow is a deliberate contained scroll region). |
| 5. No empty headings, no level skips | 3 | Y | 115 headings, 0 empty, 0 skips. |
| 5(L5).1 Zero axe violations of any impact | 5 | Y | Same three scans, empty violation arrays (not merely zero critical/serious). |
| 5(L5).2 Every pointer target ≥24×24px | 5 | Y | 0 of 254 eligible targets under 24×24px at 390. |
| 5(L5).3 Skip link first stop AND "Signed by" reachable within 15 Tab presses | 5 | N | Skip link is press 1 (yes), but "Signed by" is not reached in 80 presses (no) — compound test fails. |
| 5(L5).4 Every chart has a text/table alternative reachable without a pointer | 5 | **Y (checked myself, per instruction)** | Live HTML: `<details class="chart-table-details"><summary>View data table (accessible alternative)</summary>` wraps a full `<table class="data-table">` for the "Market layers" panel-index charts; `details`/`summary` keyboard toggling was directly confirmed in the keyboard walk. |
| 5(L5).5 Landmarks and `time`/`datetime` used throughout | 5 | **Y (checked myself, per instruction)** | Live HTML: one `<main>`, one `<nav>`, one `<footer>`, and 100 `<time dateTime>` elements. |
| 5(L5).6 Non-text contrast ≥3:1 (borders, focus rings, chart marks) | 5 | N | Not measured; the rubric states this test fails as "not measured" until that specific sample exists, and no tool in this evidence set performs it. |

Mechanical result: all 5 level-3 pass; 4 of 6 level-5 pass — score 4.

### D11 — Follow and share — score 5/5 (carried forward, spot-checked)

Carried forward (all level-3 and all level-5 pass — score 5). Spot-check: `/corrections/` is a new
route and it too carries its own distinct `<title>Corrections · Security Market Pulse</title>` and
description, consistent with test 4(L5).2 still holding across every route, old and new.

### D12 — Trust and authority — score 2/5 (carried forward; one gap closed, score unchanged)

| Test | Level | Y/N | Evidence |
|---|---|---|---|
| 1. Named person signs the judgment, with a date | 3 | Y | Carried forward, and now true in even more places (all 42 JUDGED stamps). |
| 2. Method visible after ≤1 click | 3 | Y | Carried forward. |
| 3. Site says what it will not call, and why | 3 | Y | Carried forward. |
| 4. Who the author is, beyond name/address, ≤1 click | 3 | N | Re-checked live: still no bio, role, or background text anywhere on the page. |
| 5. Author's role and commercial relationships disclosed, ≤1 click | 3 | N | Re-checked live: still zero matches for "reseller," "employer," "works for," or equivalent. |
| 5(L5).1 Corrections record at a stable address, "none to date" when empty | 5 | **Y (new capability, not yet scored)** | `/corrections/` now exists exactly as this test asks — a stable, listed, dated, attributed record. Not counted toward the score because level 5 is only evaluated once all level-3 tests pass, and tests 4 and 5 above still fail; this is the clearest illustration in this report of the mechanical rule holding a real improvement out of the score until the gating tests close. |

Mechanical result: 3 of 5 level-3 pass — score 2, unchanged from my first pass despite one real new
capability (the corrections record) that would immediately start counting once the bio and disclosure
gaps are closed.

### D13 — Craft — score 1/5 (carried forward, spot-checked)

Carried forward (level 3: 1 of 4 pass — score 1). Spot-check against the new CSS bundle
(`index-BWuXijzw.css`, since the build hash changed): still three font-family tokens (`Archivo`,
`IBM Plex Sans`, `IBM Plex Mono` — two sans families), still 21 distinct `font-size` values, still
four non-neutral colour tokens (accent/success, warning, alert). No change.

## Tests I found ambiguous

**Blocker 1 itself.** This is the central judgment call of this re-score, stated in full above: does
a wrong figure with an equally prominent, dated, adjacent correction still count as "mislabelled on
the page"? I ruled fail, on the reasoning that the rubric's own test is a sampling check against the
figure as written, and the wrong text is still exactly that, unedited by design. The strongest case
against my reading: the rubric's purpose statement for this whole instrument is whether a reader can
trust what they read, and a transparent, dated, signed correction sitting right beside the error is
arguably the single best mechanism a small site can build for exactly that trust, better in an
important sense than silently fixing the number would be. If the rubric's owner intends "the page" to
mean what a reasonable reader takes away from the page as a whole, this flips to a pass.

**D1 test 5(L5).3, the cold-reader test.** I scored this myself, from the same viewport capture I am
using for every other test on this page, rather than having an actual second reader look at it once
and report back. A real cold read by someone who has not been staring at this site for two sessions
could disagree.

**D3 test 5** (three kinds of date shown apart). Carried forward from my first score as an ambiguous
pass — the source-published date is still one click away in the evidence drawer rather than printed
on the card itself, and I still do not know whether the rubric's "shown" tolerates that click.

**D9's currency.** The Lighthouse numbers are real and were really run, but they predate the last two
merges. I judged the gap immaterial for LCP/TBT/CLS specifically because neither later merge touches
scripts, fonts, or render order — only text, spacing, and one new collapsible page. A fresh Lighthouse
run against the exact current commit could show a different number, particularly since the corrections
block adds a small amount of DOM and one more CSS rule set that loads with the rest of the stylesheet.

**D5's evidence-drawer tests**, carried forward from my first score, remain unconfirmed by a
screenshot of an opened drawer. Nothing in this round's evidence closes that gap.

## Three cheapest changes that would raise the score most

1. **Remove the sign-based colouring from the full scorecard and soften the "printing faster"/"being
   outrun" framing in Platform Pressure**, exactly as I recommended in my first score. This is
   unchanged and still the right first move: it is a CSS-class removal (the pattern is already proven
   — the same tone classes were already stripped from "The market by domain" in an earlier pass) plus
   rewording a handful of judgment sentences to stop comparing figures on different bases. This clears
   Blocker 2, one of the two remaining fit-for-purpose flags.

2. **Add two lines about who Jesse Pike is and one line disclosing the reseller relationship**,
   visible after at most one click (the existing "How this is built" details panel, or a short new
   block next to the "Signed by" line, are both already-proven patterns for exactly this kind of
   reachable-in-one-click content). This flips D12 tests 4 and 5, taking all five of D12's level-3
   tests to a pass and moving the dimension from 2 to at least 3 — worth 2.0 composite points on its
   own — and it would also let the corrections page (already built, already passing its own test)
   start counting toward the score, since level 5 only gets evaluated once level 3 is clean.

3. **Mark the single highest-consequence item in each of the four issue lanes**, for example a small
   "Biggest story this week" label on the top item in each lane (formation, absorption, prints,
   capital), rather than leaving all items in an undifferentiated list. This is the last remaining gap
   in D4, the highest-weighted dimension (20), and closing it alone would move D4's level-3 tests to
   4 of 4, taking the dimension from 2 to 3 — worth 4.0 composite points, the single largest gain
   identified in this report. It costs more judgment than items 1 and 2 (someone has to decide which
   item is "highest consequence" each week, which is itself a small editorial call rather than a
   mechanical template change), which is why it is ranked third rather than first, but the template
   change itself, once that call is made, is a one-line conditional style.
