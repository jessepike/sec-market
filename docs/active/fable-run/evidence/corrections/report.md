# T6-13 report: public correction and corrections mechanism (2026-w36)

Branch `mon/corrections`, worktree `/Users/jessepike/code/projects/sec-market-wt/corrections`.
Final commit: `0ca804b8d09563d82812b43ab78de5b13bd2f4a5`.
Branch deploy: https://security-market-pulse-git-mon-corrections-pikeholdings.vercel.app/ — confirmed serving `/`, `/corrections/`, `/corrections.json`, `/issues/2026-w36/`, and `/feed.xml` at 200, and confirmed by direct curl that the live copy no longer contains em-dashes.

## Files added and changed

Five commits carry this work, in order:

1. `feat(web): add the corrections data model and gate` — `web/src/data/types.ts` (new `Correction`/`CorrectedReading` types), `web/src/data/corrections.ts` (new, the one approved entry), `web/src/data/correctionHelpers.ts` (new: lookup helpers, JSON payload builder, and `findFiscalPeriodMismatches`, the gate), `web/src/data/meta.ts` (`LAST_UPDATED_ISO`/`LAST_UPDATED_DISPLAY` bumped to 2026-09-20).
2. `feat(web): render correction notes and add the /corrections/ page` — `web/src/components/Corrections.tsx` (new page), `web/src/components/IssueLanes.tsx` (renders the correction stamp beside a matched item), `web/src/App.tsx` (routes to the new page), `web/src/data/routes.ts` (new `corrections` route kind), `web/src/components/NextEdition.tsx` (the "no form and no list" line), `web/src/index.css` (new styles for the page and the stamp).
3. `feat(web): wire corrections into the build and verify pipeline` — `web/scripts/prerender.ts`, `web/scripts/generate-seo.ts`, `web/scripts/generate-feed.ts`, `web/scripts/verify-dist.ts`, `web/scripts/verify-issue.ts`, `web/src/data/issueHelpers.ts`.
4. `test(web): cover the corrections data, gate, and UI` — `web/tests/corrections-data.test.ts` (new), `web/tests/e2e/corrections.spec.ts` (new), `web/tests/dist-fixtures.test.ts` (one call-site update), `web/playwright.config.ts`, `web/package.json`.
5. `fix(web): drop em-dashes from corrections copy` — `web/src/components/Corrections.tsx`, `web/src/data/corrections.ts` (the copy fix covered below).

Full diffstat against `origin/preview`: 21 files, 937 insertions, 70 deletions.

No file under `web/src/data/issues/` or `web/src/data/evidence.ts` was touched, and `web/scripts/shot.mjs` was not touched.

## What each requirement produced

**1. Data.** `corrections.ts` holds one entry, `C-2026-09-20-01`, dated 2026-09-20, for issue `2026-w36`, `approvedBy` set from `AUTHOR_NAME`. It carries the approved text verbatim with the date filled in, and a corrected reading for each of the two items: `2026-w36-prints-2` (Zscaler, evidence `W36-15`) and `2026-w36-prints-6` (Palo Alto, evidence `W36-19`, plus the note withdrawing the "fastest of the week" comparison). Both readings were checked against `economicPeriod` and the excerpt text in `evidence.ts` before writing.

**2. Rendering.** `IssueLanes.tsx` (the one component behind both the front page and the issue permalink) now looks up a correction for each item and, when one exists, renders a stamped block after the original headline and "why it matters" text: "CORRECTED 20 SEP 2026" in a `<time dateTime="2026-09-20">`, the corrected reading in normal text, the withdrawal note where present, and a "See correction" link to `/corrections/#C-2026-09-20-01`. The original headline is untouched, not struck through, and stays first. Because this lives inside the same list item as the rest of the item's markup, it travels through vendor-lens filtering with the item.

**3. The `/corrections/` page.** New route kind `corrections`, added to `routesFor()`, prerendered, with its own title/description in `prerender.ts` and a `CollectionPage` JSON-LD block plus a sitemap entry in `generate-seo.ts`. The page explains in three sentences that issues are never edited, that a correction is a dated note beside the item with the original left in place, and how to report an error (mailto link to the existing contact address). Below that it lists every correction newest-first, anchored by its id, with date, a link to the issue permalink, the full approved text, and the approver. Linked from `NextEdition.tsx`.

**4. `NextEdition.tsx`.** The line "There is no form and no list" is gone. It now reads: "There is no form, and every correction that gets published is listed at `/corrections/`," with `/corrections/` as a real link. I grepped the test suite and `verify-*.ts` for any assertion on the old wording and found none, so no test or verify-script assertion needed to change for this line.

**5. Machine-readable surfaces.** `/corrections.json` is generated the same way the other JSON files are (`writeCorrectionsJson` in `generate-feed.ts`, mirroring the `issueJsonCopy`/`writeIssueJsonCopies` pattern), and is verified against a pure payload builder (`correctionsJsonPayload`) by a new dist check. The per-issue JSON at `dist/issues/2026-w36.json` gained a sibling `corrections` array (the corrections for that issue), added in `issueJsonCopy` in `issueHelpers.ts`. This is safe: `checkEveryIssueJsonExists` in `verify-dist.ts` only runs `deepStrictEqual` on the `.issue` and `.evidence` sub-objects, never on the whole parsed file, so the sibling field is invisible to that check and the hashed `Issue` object itself is never touched. I confirmed this by reading the check's source and then by running the full build, which passed. `feed.xml` now includes a correction item alongside the issue items (its own guid, `isPermaLink="false"`), and `<link rel="alternate">` discovery on every page now also requires `${SITE_URL}/corrections.json` to be present and resolvable — `checkAlternateLinksResolve` in `verify-dist.ts` was extended to check for that specific href, not just "some links resolve." `EXPECTED_CHECK_COUNT` in `verify-dist.ts` moved from 8 to 9 for the new check (11i, `checkCorrectionsJsonExists`).

**6. Tests.** `corrections-data.test.ts` checks id uniqueness, that `issueId` and `itemId` exist, that dates are valid and not in the future (using the project's own `LAST_UPDATED_ISO` comparison, not a clock), and that `approvedBy`/text/corrected headlines are non-empty with resolvable evidence ids. It also unit-tests the gate directly (below). `e2e/corrections.spec.ts` checks that the front page shows the corrected note beside both items with the originals still present, that the issue permalink shows the same, that `/corrections/` renders the entry with a working anchor, and that `/corrections.json` matches the source data.

**7. The gate.** `findFiscalPeriodMismatches` in `correctionHelpers.ts` flags any item whose headline matches a fiscal-year/full-year pattern while its cited evidence's `economicPeriod` starts with "Quarter," unless a correction already covers that item. It's wired into `verify-issue.ts` as check 16. Proof, run twice (once mid-session, once again after the copy fix, both as scratch runs not committed):

- With `corrections.ts` temporarily emptied, `npm run verify:issue` failed check 16, naming exactly two items: `2026-w36-prints-2` ("Zscaler FY2026 revenue grows to $898.2M...", evidence `W36-15`, economicPeriod "Quarter ended 2026-07-31") and `2026-w36-prints-6` ("Palo Alto FY2026 revenue grows 34%...", evidence `W36-19`, economicPeriod "Quarter ended 2026-07-31"). All 14 other checks still passed.
- Restoring `corrections.ts` from an exact backup (verified byte-identical with `diff`), `npm run verify:issue` passed all 15 checks including 16.
- No other item in `2026-w36` — the only issue file that exists in this repo — was flagged in either run. There is nothing else to report here.

This is also exercised as an automated unit test in `corrections-data.test.ts`: a synthetic issue/evidence/correction fixture shows the gate returns no violations when the correction is present and exactly one violation for the same item when the corrections array is empty, so this proof runs on every future `npm test`, not just this scratch check.

**8. `LAST_UPDATED_DISPLAY`.** Its own contract comment says to move it whenever the site ships a visible change. This ships a visible change (the correction stamps and the new page), so I moved `LAST_UPDATED_ISO` from `2026-09-19` to `2026-09-20` and `LAST_UPDATED_DISPLAY` from "September 19, 2026" to "September 20, 2026."

## Merging origin/preview

Mid-session, `origin/preview` moved ahead with a front-page pass (merge `0ece0ce`, touching `IssueHero.tsx`, `MarketPicture.tsx`, `index.css`, `PlatformPressure.tsx`, `DomainBoard.tsx`, `Hypotheses.tsx`, `WhatMoved.tsx`, and `smoke.spec.ts`). I ran `git fetch origin && git merge origin/preview` on `mon/corrections`. The merge was clean: no conflict markers anywhere (checked with a repo-wide grep for `<<<<<<<`/`=======`/`>>>>>>>`), and `git status --short` was clean afterward. `web/src/index.css` was the only file both sides touched, and git's merge resolved it automatically without needing manual reconciliation — their compaction/name-stamp CSS and my new corrections CSS both landed intact. I rebuilt and re-ran the full test suite on the merged result before pushing, and recaptured screenshots from that merged build.

## Copy fix

The Palo Alto note in `corrections.ts` and doc comments in `corrections.ts` and `Corrections.tsx` used em-dashes, which the brief's no-em-dash rule for copy I write covers. Fixed exactly as specified:

- `corrections.ts` line 6 (doc comment): "once published — add" became "once published: add"
- `corrections.ts` note field: two em-dashes replaced with commas, text otherwise identical
- `Corrections.tsx` doc comment: an em-dash replaced with a colon

The existing mailto subject string `'Security Market Pulse — correction or question'` in `Corrections.tsx` was left exactly as it was (it's a copy of the pre-existing subject in `NextEdition.tsx`, not new copy, and the two need to match). Diff for this fix: 2 files, 4 insertions, 4 deletions, nothing else touched.

## Test tail

`npm test` (lint, `test:data`, build with all verify gates, e2e) ran green three times total: right after the origin/preview merge, again unchanged, and a third time after the copy fix. Each run:

- lint: 0 errors, 0 warnings
- `test:data`: 80 passed (including the new corrections-data tests)
- `verify:issue`: all 15 checks passed, including the new check 16
- `verify:dist`: all 9 checks passed, including the new check 11i
- e2e: 34 passed, 1 skipped — the skip is `[desktop] lens.spec.ts:188 "at 390 the chip row is reachable and scrollable"`, a pre-existing test that only runs at 390px and is unrelated to this work; it was already skipping before this branch existed

## Heights

Baseline ("before"), a fresh build of `origin/preview@0ece0ce`: 16,630px at 1440, 20,752px at 390. This matches the coordinator's own independently-stated figure for that commit.

"After" (merged `mon/corrections`, measured before the copy fix): 16,882px at 1440, 21,208px at 390 — the increase is the two correction blocks added to the front page. The copy fix only swaps em-dashes for commas of nearly identical length, so it does not meaningfully change page height; I did not re-measure full-page height after the copy fix, only recaptured the two affected item crops (below), which is what changed visually.

## What the images show

All ten original screenshots were viewed with the Read tool. The three Palo Alto (`2026-w36-prints-6`) crops were retaken after the copy fix and viewed again just now:

- Original headlines are fully intact, readable, and never struck through, on both the front page and the issue permalink.
- The correction block is visually distinct from a second headline: a small-caps mono "CORRECTED 20 SEP 2026" stamp, a muted pink background, and a left accent border (the same alert treatment the site already uses for its draft banner), followed by the corrected reading in normal text, the withdrawal note in italics, and a plain "See correction" link.
- At 390px, all text wraps cleanly with no truncation, clipping, or overflow.
- `/corrections/` renders as a plain page matching the site's existing typography at both widths, with the one entry's full approved text, date, issue link, and approver.
- The issue-permalink crops are visually identical in content to the front-page crops, as expected since both use `IssueLanes.tsx`.
- The recaptured Palo Alto crops confirm the copy fix is live in the rendered page: the note now reads "...comparison, that this growth was the fastest among this week's public-issuer prints, is withdrawn..." with commas, no em-dashes.

Axe-core scan: zero violations across `home-1440`, `home-390`, `corrections-1440`, `corrections-390`.

## What I was unsure about

Nothing blocked the build or required a judgment call beyond what's documented above. The one thing worth flagging explicitly: the front-page height numbers above are from before the copy fix, since the fix only changes punctuation and I judged a full re-measure unnecessary; if that judgment is wrong, it's a five-minute rerun of the same capture script used for the original numbers.

## Deferred to backlog

Deferred to backlog: I noticed while wiring the feed and JSON outputs that the correction items in `feed.xml` and `corrections.json` don't currently distinguish "correction added" from "correction later amended," since the schema is append-only and has no revision field. That's fine for the one entry that exists today but could matter if a correction itself ever needs a follow-up note. I did not build anything for this since it's speculative generality beyond what was asked; noting it here rather than in a file elsewhere, since it's a one-line observation with no immediate action.
