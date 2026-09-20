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

The build report for wave 1 (`docs/active/fable-run/evidence/wave1/build-report.md`) recorded the current preview page at 17084px tall at 1440 and 21437px tall at 390. Building this branch and measuring the same way gives the identical numbers: 17084px at 1440, 21437px at 390. The added text (" · Jesse Pike", about 12 characters) fits on the existing line in every case without pushing anything to a new line, so the page did not grow.

## What the crops show

Captured the home page full-page at 1440 and 390, plus cropped screenshots of `#platforms`, `#landscape`, and `#hypotheses` at both widths, plus `#moved` (opening its disclosure first, since it's collapsed by default). Files are in this folder: `home-1440-full.png`, `home-390-full.png`, and `home-<width>-<section>.png` for platforms, landscape, hypotheses, and moved.

- `#platforms`: every row in the judged-read column now reads "JUDGED 17 AUG 2026 · JESSE PIKE" at 1440, and the same text wraps cleanly onto its own line inside each card at 390. Nothing else in the table moved.
- `#landscape`: all four domain cards now read "JUDGED 16 AUG 2026 · JESSE PIKE" in the judged layer, on one line at both widths, sitting in the same place relative to the horizon/confidence line below it.
- `#hypotheses`: all four hypothesis rows now carry "JUDGED 15 AUG 2026 · JESSE PIKE" or "JUDGED 17 AUG 2026 · JESSE PIKE" depending on the hypothesis, right-aligned above the evidence chip, unchanged layout otherwise.
- `#moved`: the judged column's header now reads "JUDGED · A PERSON SIGNED THIS · 17 AUG 2026 · JESSE PIKE". At 1440 it stays on one line; at 390 it wraps to two lines, which reads fine and doesn't crowd the "HELD" row underneath it.

Nothing else in any of the four crops moved. No colour changed. No section was removed.

## Assertions changed

None. The new test is additive; no existing test's expected text, count, or visibility was touched.
