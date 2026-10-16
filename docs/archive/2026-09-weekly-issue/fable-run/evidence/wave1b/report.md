# T6-11 report — name the author on every judged stamp

Branch `mon/wave1b`, built from a worktree at `/Users/jessepike/code/projects/sec-market-wt/wave1`, off `preview` at the commit that carries wave 1's merge (`f557b4c`). Not merged anywhere. Commit `efa8ca2`.

## The rule and the gap

The site's rule is that every judgment must carry a name and a date. "The market by domain" (`MarketPicture.tsx`) does this: its stamp reads "JUDGED 16 AUG 2026 · JESSE PIKE". Four other places stamped a judgment with a date but no name.

## Every JUDGED stamp found, and what it showed before this fix

| File and lines | What it renders | Had a name already |
|---|---|---|
| `web/src/components/MarketPicture.tsx` lines 41-43 | "JUDGED 16 AUG 2026 · JESSE PIKE" (the market-by-domain stance) | Yes — this is the reference pattern |
| `web/src/components/PlatformPressure.tsx` lines 61-68 (desktop table, judged read column) | "JUDGED 17 AUG 2026" | No — fixed |
| `web/src/components/PlatformPressure.tsx` lines 91-98 (mobile stack, same data) | "JUDGED 17 AUG 2026" | No — fixed |
| `web/src/components/DomainBoard.tsx` lines 108-111 (landscape domain cards) | "JUDGED 16 AUG 2026" | No — fixed |
| `web/src/components/Hypotheses.tsx` lines 21-28 (tracked hypotheses) | "JUDGED 15 AUG 2026" or "JUDGED 17 AUG 2026" depending on the hypothesis | No — fixed |
| `web/src/components/WhatMoved.tsx` lines 29-33 (what-moved judged column, inside the closed "What moved" disclosure) | "JUDGED · a person signed this · 17 AUG 2026" | No — fixed |
| `web/src/components/ProvenanceRail.tsx` line 20 | "JUDGED · signed and dated by a person" — the legend key at the top of every page, explaining what the colour means in general | Not applicable — see note below |
| `web/src/components/PlatformPressure.tsx` line 30 | "TRACKED PRINTS · JUDGED READ" — a column-group header, not a dated judgment | Not applicable — no date attached |
| `web/src/components/WeThink.tsx` | Uses a different pattern, "Signed by {name} · {date}" (lines 58-61), which already names the signer directly. Does not render the word "JUDGED" at all. | Already compliant, different mechanism |

Two items are worth a second look but are not judged stamps in the sense the rule is aimed at, so I left them alone and I'm flagging them rather than fixing them:

- `ProvenanceRail.tsx`'s legend text has no specific date attached to it — it is explaining the category, not stamping an individual judgment — so there is nothing to hang a name on in the way the rule intends.
- `IssueHero.tsx` line 41 has the sentence "Domain stances judged 16 Aug 2026," inside the page's as-of line. This carries a date but no name, and it does use the word "judged" (lowercase, inside a sentence, not the uppercase stamp pattern the other sections use). It's close enough to the same rule that I want to name it, but it's a different rendering shape than every other case here, so I left it out of this fix and I'm noting it below for the backlog.

## What I changed

For each of the four missing-name cases, I added " · JESSE PIKE" after the date, reusing the `AUTHOR_NAME` constant from `web/src/data/meta.ts` (the same constant `MarketPicture.tsx` already uses) rather than typing the name again. The `.stamp-label` CSS class uppercases text automatically, so writing the constant in its natural mixed case ("Jesse Pike") renders visually identical to the existing "JESSE PIKE" stamps — confirmed in `web/src/index.css` line 1896 (`text-transform: uppercase`). The `<time dateTime>` element in every case is untouched.

- `web/src/components/PlatformPressure.tsx`: added the import, then appended `&middot; {AUTHOR_NAME}` after the `<time>` close, once in the desktop table (line ~66) and once in the mobile stack (line ~96).
- `web/src/components/DomainBoard.tsx`: added the import, appended `&middot; {AUTHOR_NAME}` after the `<time>` close in the landscape card's judged layer (line ~110).
- `web/src/components/Hypotheses.tsx`: added the import, appended `&middot; {AUTHOR_NAME}` after the `<time>` close (line ~26).
- `web/src/components/WhatMoved.tsx`: added the import, appended `&middot; {AUTHOR_NAME}` after the `<time>` close in the judged column (line ~32). Left the existing "a person signed this" wording in place — that's label text describing the mechanism, not the judgment's substance, and the instruction was to add a name, not rewrite the sentence.

No data value, no judgment text, and no colour changed anywhere. No component, CSS rule, export, or page section was removed.

## Test added

Added a new test to `web/tests/e2e/smoke.spec.ts`: "every judged stamp with a date also names who judged it." It queries every element with the `.stamp-label` class across the whole page (not just the visible ones — this reaches into the closed "What moved" disclosure without needing to click it open first), keeps only the ones whose text contains the literal word "JUDGED" and that also contain a `<time>` element, and asserts every one of those contains "Jesse Pike". No existing assertion was weakened or changed.

## Test run

Ran `npm test` in the OrbStack dev VM (lint, data tests, the full build with all verify gates, then e2e). Full result: green.

```
> web@0.0.0 lint
> oxlint
Found 0 warnings and 0 errors.

> web@0.0.0 test:data
(all data test suites passed)

> web@0.0.0 build
(verify:edition, verify:panel, verify:integrity, verify:issue all PASS; tsc, build:client, build:server, prerender, seo, build:feed, verify:dist all PASS — verify:dist 11a through 11h all PASS)

> web@0.0.0 test:e2e
> playwright test

Running 27 tests using 5 workers
1 skipped
26 passed (9.9s)
```

The new stamp-naming test is included in that 26 and passed.

## Page height, before and after

The build report for wave 1 (`docs/archive/2026-09-weekly-issue/fable-run/evidence/wave1/build-report.md`) recorded the current preview page at 17084px tall at 1440 and 21437px tall at 390. Building this branch and measuring the same way gives the identical numbers: 17084px at 1440, 21437px at 390. The added text (" · Jesse Pike", about 12 characters) fits on the existing line in every case without pushing anything to a new line, so the page did not grow.

## What the crops show

Captured the home page full-page at 1440 and 390, plus cropped screenshots of `#platforms`, `#landscape`, and `#hypotheses` at both widths, plus `#moved` (opening its disclosure first, since it's collapsed by default). Files are in this folder: `home-1440-full.png`, `home-390-full.png`, and `home-<width>-<section>.png` for platforms, landscape, hypotheses, and moved.

- `#platforms`: every row in the judged-read column now reads "JUDGED 17 AUG 2026 · JESSE PIKE" at 1440, and the same text wraps cleanly onto its own line inside each card at 390. Nothing else in the table moved.
- `#landscape`: all four domain cards now read "JUDGED 16 AUG 2026 · JESSE PIKE" in the judged layer, on one line at both widths, sitting in the same place relative to the horizon/confidence line below it.
- `#hypotheses`: all four hypothesis rows now carry "JUDGED 15 AUG 2026 · JESSE PIKE" or "JUDGED 17 AUG 2026 · JESSE PIKE" depending on the hypothesis, right-aligned above the evidence chip, unchanged layout otherwise.
- `#moved`: the judged column's header now reads "JUDGED · A PERSON SIGNED THIS · 17 AUG 2026 · JESSE PIKE". At 1440 it stays on one line; at 390 it wraps to two lines, which reads fine and doesn't crowd the "HELD" row underneath it.

Nothing else in any of the four crops moved. No colour changed. No section was removed.

## Assertions changed

None. The new test is additive; no existing test's expected text, count, or visibility was touched.

## Second pass (T6-12)

Four small fixes on the same branch, addressing the cheapest failing tests an independent scorer identified. Commits, in order: `00e4ed1`, `7849c1f`, `9cb3c08`, `0523c8f`.

### 1. Compact the supplier rows in "The market by domain"

Each supplier's evidence chip sat on its own line below the metric and period text, costing a full chip-height per row. Moved the chip onto the same row as the metric/period text in `web/src/components/MarketPicture.tsx` (wrapped both in a new `market-picture__vendor-metaRow` div) and tightened the vertical gaps in `web/src/index.css`: the vendor list's gap went from 0.75rem to 0.3rem, each vendor's top padding from 0.65rem to 0.3rem, and the list's top margin from 0.5rem to 0.35rem. The evidence chip gets a smaller size only inside this list (`market-picture__evidence`: 28px min-height, 0.2rem/0.5rem padding, 0.75rem font), still above the 24x24 CSS px minimum pointer target, and every other evidence chip on the page is untouched.

Where the metric text is long enough that it and the chip would collide (an older figure plus a segment tag, for example — CrowdStrike Falcon Cloud and Palo Alto XSIAM both hit this), the row wraps and the chip drops to its own line underneath rather than overlapping. Checked this directly in the crops below.

Measurements, before and after, at 1440:

| | Before | After | Target |
|---|---|---|---|
| `#market` bottom | 2202px | 1747px | ≤1750px |
| `#we-think` top | 2234px | 1779px | <1800px |

At 390 nothing needed to change beyond what the CSS already does; rows still read cleanly and the chip drops to its own line where the metric text is long, which is expected and fine per the task.

### 2. Phone chrome — get `#overview` higher at 390

At 390x844 the dark provenance rail (`web/src/components/ProvenanceRail.tsx`) stacks to three lines (brand + as-of on one line, then each legend line on its own), and the header wraps the Menu button onto its own row below the brand/date row. Neither component's markup changed; only `web/src/index.css`'s existing `@media (max-width: 768px)` rules were tightened:

- `.rail__inner`: padding from `8px 1rem` to `6px 1rem`, row-gap from 0.5rem to 0.3rem (column-gap unchanged at 1rem).
- Added `line-height: 1.2` for `.rail__brand`, `.rail__asof`, `.rail__legend` at this width only (body default is 1.6).
- `.rail__legend`'s internal gap from 0.75rem to 0.5rem.
- `.site-header__inner`: padding from `0.75rem 1.25rem` (the all-widths default) to `0.5rem 1.25rem`, and the wrap row-gap set to 0.5rem, at this breakpoint only.

Nothing removed: the rail still shows the AS OF date and both legend lines ("TRACKED · public prints, no judgment" and "JUDGED · signed and dated by a person"), and the Menu button measured 44px tall in the browser (`min-height: 44px` on `.nav-toggle`, untouched). 1440 is untouched because every edit sits inside the existing max-width:768px media query.

Measurements:

| | Before | After | Target |
|---|---|---|---|
| `#overview` top at 390 | 221px | 184px | ≤205px |
| `#overview` top at 1440 | 113px | 113px (unchanged) | n/a |

### 3. Front-page eyebrow: link instead of raw id

The first-screen eyebrow read "ISSUE 2026-W36 · WEEK ENDING 6 SEP 2026 · PUBLISHED 19 SEP 2026 · FEED" — "2026-w36" is an internal id a new reader has no way to decode. In `web/src/components/IssueHero.tsx`, on the front page only (gated on the existing `showAsOf` prop, which is already true only on the front page's call site and false everywhere else), the "Issue 2026-w36" lead-in becomes a link reading "Weekly issue" pointing at `/issues/2026-w36/`. The permalink page and the archive are unaffected — `showAsOf` defaults to false there, so they keep rendering the plain "Issue 2026-w36 · ..." text exactly as before. Confirmed by loading both routes directly:

- Front page: `WEEKLY ISSUE · WEEK ENDING 6 SEP 2026 · PUBLISHED 19 SEP 2026 · FEED`, with "Weekly issue" linking to `/issues/2026-w36/`.
- Permalink (`/issues/2026-w36/`): `ISSUE 2026-W36 · WEEK ENDING 6 SEP 2026 · PUBLISHED 19 SEP 2026 · FEED`, unchanged.

Checked `web/tests/e2e/issue.spec.ts`, `web/tests/e2e/smoke.spec.ts`, and `verify:issue`'s render check (`scripts/verify-issue.ts`, check 10) for any assertion on the front-page eyebrow's id text. None exists — the render check calls `IssueHero` without `showAsOf`, so it exercises the unchanged permalink-style text, and the e2e specs check the archive list and the JSON feed by `issue.id` directly, never the front-page eyebrow string. No assertion changed.

### 4. Name the author on the domain-stances as-of line

Changed "Domain stances judged 16 Aug 2026." to "Domain stances judged 16 Aug 2026 by Jesse Pike." in `web/src/components/IssueHero.tsx`, using the `AUTHOR_NAME` constant from `web/src/data/meta.ts` (imported alongside the existing `LAST_UPDATED_DISPLAY` import) rather than typing the name again.

### Test run (second pass)

Ran `npm test` in the OrbStack dev VM after all four changes, and again after splitting the working tree into the four commits above to confirm the final state is identical. Both runs: fully green.

```
> web@0.0.0 lint
> oxlint
Found 0 warnings and 0 errors.

> web@0.0.0 test:data
(all data test suites passed)

> web@0.0.0 build
(verify:edition, verify:panel, verify:integrity, verify:issue all PASS; tsc, build:client, build:server, prerender, seo, build:feed, verify:dist all PASS)

> web@0.0.0 test:e2e
> playwright test

Running 27 tests using 5 workers
1 skipped
26 passed (9.6s)
```

No existing assertion was weakened, changed, or removed. Page height dropped from 17084px to 16630px at 1440, and from 21437px to 20752px at 390 — expected, since compacting the market-by-domain section and the phone chrome both remove vertical space rather than add it.

### What the crops show

Captured `pass2-home-<width>-viewport.png`, `pass2-home-<width>-full.png`, and `pass2-home-<width>-market.png` at 1440 and 390 into this folder.

- Viewport shots: at 1440 the rail, header, description, disclaimer, the new "Domain stances judged 16 Aug 2026 by Jesse Pike." line, the "WEEKLY ISSUE" link, and the top of "The market by domain" all read cleanly with nothing overlapping. At 390 the same content is visibly more compact at the top — rail on three tight lines, header on two tight lines, Menu button clearly tappable — before the h1 and the market section begin.
- Market crops: every supplier row's evidence chip sits inline with short metric text (Cato Networks, Check Point, Fortinet, and so on) and drops cleanly to its own line under long metric text (CrowdStrike Falcon Cloud's "cloud ending ARR · FY26 · older figure · product line, not the whole company", Palo Alto XSIAM's similar combination) at both widths, with no overlap or collision in either case.

Nothing else in any of the crops looked wrong.

### Assertions changed

None, in either the compaction work or the eyebrow-link work. The e2e suite passed unmodified.
