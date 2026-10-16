# T6-16 report: the founding thesis moves to /thesis/

Run SEC-MARKET-FABLE-001, task T6-16. Branch `mon/thesis`, built in the worktree at
`/Users/jessepike/code/projects/sec-market-wt/thesis`. Final commit: `49b114ef9fe52c42b4c44b3f1a2ebbc603f3d789`.

## What changed, in plain words

The founding thesis (does security spending lag infrastructure spending) had two jobs on the
front page: it was both the site's main argument and a section inside it. Per
`docs/archive/2026-09-weekly-issue/product-core.md` section 5, it should be neither -- it is one standing analysis among
the site's outputs, with its own home and its own record. It now lives at `/thesis/`. The front
page keeps a short pointer to it where the argument used to sit.

A complication came up mid-task. The other session working on this project, in the main checkout,
pushed two commits to `preview` while I was working: `8fb326f` (a real front-page redesign -- the
h1 became the site's own headline, the weekly read moved into a new "issue strip," and the market
picture now reaches the first screen) and `a3deb36` (the write-up of that same change). My branch
had forked before those landed. I rebased `mon/thesis` onto the new `preview` tip, resolved two
merge conflicts (both were doc-comment or import-list conflicts, not logic conflicts -- the actual
component trees merged cleanly), and reran everything. The build described below reflects the
combined state: their redesign plus my move, composing correctly.

## Files added

- `web/src/components/ThesisPointer.tsx` -- the front page's compact pointer at `#read`.
- `web/tests/e2e/thesis.spec.ts` -- the new e2e coverage for `/thesis/`.

## Files changed

- `web/src/App.tsx` -- new `ThesisPage` component and `RouteContent` branch for the `thesis` route
  kind; `FrontPage` drops `JudgmentBoard`, adds `ThesisPointer` after `#hypotheses`, and passes
  `condenseThesis` to `WeThink`.
- `web/src/components/WeThink.tsx` -- new `condenseThesis` prop (default `false`, so the issue
  permalink is unaffected) and a `ThesisLine` helper that renders either the original paragraph or
  a one-line pointer to `/thesis/`.
- `web/src/components/Header.tsx` -- removed the "Thesis" nav item.
- `web/src/components/NextEdition.tsx` -- added a "Standing analysis" link to `/thesis/` in the
  front page's secondary-links block.
- `web/src/data/routes.ts` -- new `thesis` `RouteKind` and its route entry (`/thesis/`).
- `web/src/index.css` -- styles for `.thesis-pointer`, `.thesis-page`, and `.we-think__thesis-link`.
- `web/scripts/prerender.ts` -- must-see section ids for the `thesis` route kind, and its
  title/description/canonical branch.
- `web/scripts/generate-seo.ts` -- JSON-LD branch for the `thesis` route kind (modeled as an
  `Article`, like an issue permalink, since it is one output among several, not the site itself).
- `web/tests/e2e/issue.spec.ts`, `web/tests/e2e/smoke.spec.ts` -- updated assertions (below).

Nothing in `web/src/data/issues/`, `evidence.ts`, `corrections.ts`, or `market.ts` values was
touched. No component, CSS rule, export, or data was deleted. The lock manifest logic is untouched.

## Every assertion or gate I changed, with why

**`web/tests/e2e/smoke.spec.ts`**

- Old: three assertions checking `#market-call-heading` was visible on the front page and
  contained the headline text.
  New: `await expect(page.locator('#market-call-heading')).toHaveCount(0)`, plus assertions that
  `#read` (now the pointer) contains the pointer's own heading text and the market-call headline
  read from `marketCall.headline`, and that its link has `href="/thesis/"`.
  Why: the market-call heading moved to `/thesis/`; the same assertion now lives in
  `thesis.spec.ts`, and the front page needs its own check that the full heading is really gone
  and the pointer is really there.

**`web/tests/e2e/issue.spec.ts`**

- Old: `test('permalink page: clicking "Thesis" navigates to the front page at #read', ...)`,
  clicking the nav item labelled "Thesis" and asserting the URL lands on `/#read`.
  New: the same test, renamed, using "Landscape" in place of "Thesis" and asserting `/#landscape`.
  Why: "Thesis" left the top nav entirely, so there is no longer a nav item by that name to click.
  The test exists to guard a specific regression (F7): a front-page-only hash nav item, clicked
  from a page where its target doesn't exist, must fall through to a real navigation rather than a
  same-page no-op. "Landscape" is still such an item, so it exercises the identical regression at
  the identical strictness. I did not weaken this gate; I moved it to a target that still exists.

**New: `web/tests/e2e/thesis.spec.ts`** (not a change to an existing gate, but the replacement
coverage for what left the front page)

- `/thesis/` renders exactly one h1 with the new heading text, the market-call heading, the
  running score, every item in `marketCall.changeTriggers`, every item in
  `marketCall.noCallBoundaries`, the "Do" and "Avoid" headings and every item under each, and a
  working "Back to the front page" link.
- An evidence chip inside `#read` on `/thesis/` opens the evidence drawer and Escape closes it.
- On the front page: the `#read` pointer contains the pointer heading and the market-call
  headline and links to `/thesis/`; `#market-call-heading`, the "Do"/"Avoid" headings, and every
  change-trigger sentence are absent; "Thesis" is gone from the header nav; "Standing analysis"
  links to `/thesis/`; `#we-think` contains "Standing analysis:" and a "See the record." link to
  `/thesis/`.

## The permalink diff

I built `preview` at its current tip (`a3deb36`) in a separate worktree and diffed its
`dist/issues/2026-w36/index.html` against the same file from the `mon/thesis` build, after
normalizing the two builds' hashed asset filenames to the same placeholder so a routine
content-hash change wouldn't show up as noise. The full diff:

```
145,147d144
< <a href="/#read">Thesis</a>
< </li>
< <li>
```

That is the entire difference: the removed "Thesis" nav item in the shared header, three lines.
Nothing else in the permalink page changed -- not the issue content, not `WeThink`'s full thesis
paragraph (the permalink never passes `condenseThesis`), not any data. That matches the
requirement that the permalink render byte-for-byte the same apart from navigation.

## Test tail

Full `npm test` in the OrbStack dev VM, after the rebase, ran clean:

```
# tests 80
# suites 17
# pass 80
# fail 0
...
PASS  1 ordering-id-format-sunday-unique  ... through ...  PASS  10 render-check
verify:issue passed
Prerender OK: route "/" -- 13 sections verified un-nested
Prerender OK: route "/issues/" -- 1 sections verified un-nested
Prerender OK: route "/corrections/" -- 1 sections verified un-nested
Prerender OK: route "/thesis/" -- 2 sections verified un-nested; wrote dist/thesis/index.html (10817 bytes)
Prerender OK: route "/issues/2026-w36/" -- 6 sections verified un-nested
Prerender OK: 5 route(s) written.
SEO OK: injected 1146 chars of JSON-LD into route "/thesis/".
SEO OK: wrote dist/sitemap.xml with 5 route(s) and 4 JSON machine-surface entries.
PASS  11a through 11i -- verify:dist passed
Running 38 tests using 8 workers
...
1 skipped
37 passed (10.0s)
```

The one skipped test is `lens.spec.ts`'s phone-only chip-row check, skipped on the desktop
project by its own pre-existing `test.skip`, unrelated to this change.

## Measurements

`document.getElementById(id).getBoundingClientRect().top + scrollY`, front page, before
(`preview` at its current tip) and after (`mon/thesis`), both widths. Full file:
`docs/archive/2026-09-weekly-issue/fable-run/evidence/thesis/measurements.json`.

| | 1440 before | 1440 after | 390 before | 390 after |
|---|---|---|---|---|
| page height | 16873 | 15724 | 21250 | 18669 |
| #overview | 338 | 338 | 493 | 493 |
| #market | 505 | 505 | 804 | 804 |
| #we-think | 1770 | 1770 | 3348 | 3348 |
| #follow | 6908 | 6710 | 10683 | 10126 |
| #landscape | 7019 | 6820 | 10845 | 10288 |
| #platforms | 7795 | 7597 | 12535 | 11978 |
| #prints | 9490 | 9292 | 15659 | 15103 |
| #hypotheses | 15083 | 13677 | 18664 | 15777 |
| #read | 13875 | 14186 | 16334 | 16796 |
| #method | 15940 | 14737 | 20030 | 17395 |

`#overview`, `#market`, and `#we-think` land at the identical pixel in both builds, which is the
proof the rebase actually worked: everything above the thesis pointer is untouched by my change.
Below that, `#read` moved later (it now sits after `#hypotheses` instead of before it) and the
page got shorter -- about 1,150px shorter at 1440, about 2,580px shorter at 390 -- because the
full argument (`JudgmentBoard`, the running score, the Do/Avoid panels) left the front page for a
short stamp-and-link block, and `#we-think`'s own thesis paragraph condensed to one line.

## Axe results

`docs/archive/2026-09-weekly-issue/fable-run/evidence/thesis/axe-results.json`:

```
thesis-1440: 0 rules violated
thesis-390: 0 rules violated
```

## What I saw in each image

All in `docs/archive/2026-09-weekly-issue/fable-run/evidence/thesis/`.

- **before-home-1440-viewport.png / after-home-1440-viewport.png** -- identical first screens
  except the header nav: "Thesis" is present before, gone after, replaced in position by
  "Landscape" moving up. Everything else on the first screen (the masthead headline "The security
  market, from public numbers," the boxed "THIS WEEK" strip, the three visible domain cards) is
  pixel-identical, confirming the redesign from the other session came through the rebase intact
  and my change didn't touch it.
- **before-crop-read-1440.png** -- the old full #read block: running score, market-call headline
  and stat band, "The read" with its confidence note, four cards (What changed, Do, Avoid, We
  will not call, What would change the call).
- **after-crop-read-1440.png** -- the new pointer: "STANDING ANALYSIS" eyebrow, the heading "Does
  security spending lag infrastructure spending?", the market-call headline as one plain line, a
  "JUDGED SEPTEMBER 20, 2026 - JESSE PIKE" stamp, and the "Read the analysis and its record" link.
  Visibly short and quiet next to the before image -- roughly 190px tall at 1440, inside the
  150-220px target.
- **after-crop-read-390.png** -- the same pointer at phone width, wraps cleanly onto two lines
  for the heading, everything still legible and in order.
- **before-crop-we-think-1440.png** -- the old #we-think: summary, then a full boxed thesis
  paragraph with confidence stamp and an evidence-source chip, then the no-call list and
  signature.
- **after-crop-we-think-1440.png** -- same block, but the boxed thesis paragraph is gone,
  replaced by one quiet line: "Standing analysis: holds. See the record." linking to /thesis/.
- **after-thesis-1440-full.png** -- the new page end to end: h1, the intro paragraph in the exact
  wording specified, then the unmodified JudgmentBoard (running score, headline, stat band, "The
  read," all four cards), then "Back to the front page." Heading order is valid -- one h1, then
  h2s, then h3s inside the cards, no skips.
- **after-thesis-390-full.png** -- the same page at phone width. The two-column card pairs
  (Do/Avoid, We will not call/What would change the call) stack to one column, which is the
  existing JudgmentBoard responsive behavior, unmodified by this task. Everything reads in the
  same order as at 1440.
- **before-issue-w36-1440-full.png / after-issue-w36-1440-full.png** -- visually identical except
  the header nav item, matching the three-line HTML diff above.

## Branch and deployment

`git push -u origin mon/thesis` succeeded. The preview URL
`https://security-market-pulse-git-mon-thesis-pikeholdings.vercel.app/thesis/` returned an initial
308 (deployment still finishing) and then 200 on the next check, about 30 seconds later. Confirmed
the served page's `<title>` and h1 match what was built.

## Anything I was unsure about

- **Where exactly to put the "Standing analysis" secondary link.** The task allowed "the footer or
  the existing block where secondary links live." There is no single global footer that renders on
  every route today -- `MethodologyNote` and `NextEdition` (the closest things to a footer) render
  on the front page only. I put the link in `NextEdition`'s existing `method-band__links` block,
  which only reaches the front page. That satisfies the literal instruction and gives the front
  page a second path to /thesis/ beyond the pointer itself, but a reader on /corrections/,
  /issues/, or an issue permalink has no in-page link to /thesis/ at all (only the URL). I did not
  build a global footer to fix this -- it is outside what was asked, so it is in the backlog note
  below rather than built.
- **The JSON-LD type for /thesis/.** I modeled it as `Article`, matching the issue permalink
  pattern, rather than `Report`, which is what the front page uses for the same `marketCall` data
  today. Both were defensible; `Article` felt closer to "one output among several," which is the
  point of the move. No test checks JSON-LD `@type`, so this is a judgment call, not a gate.
- **The mid-task rebase.** I want to flag it plainly rather than let it pass as ordinary process:
  my branch was based on a `preview` tip that moved out from under it while I worked, because
  another session pushed two commits touching exactly the file (`App.tsx`) and exactly the two
  test files (`smoke.spec.ts`, `issue.spec.ts`) I was also changing. I rebased and reconciled by
  hand rather than building on the stale base, and reran the full suite and the whole evidence
  capture afterward. I did not touch anything in the other session's commits beyond resolving the
  two doc-comment conflicts they created with mine.

Deferred to backlog: I noticed the "Standing analysis" link only reaches readers on the front
page -- /corrections/, /issues/, /issues/<id>/, and the archive have no in-page link to /thesis/
at all today. Building a link that reaches every route would mean either adding a real site-wide
footer or adding a "Standing analysis" entry back into the shared Header, and the task was
explicit that this link belongs in "the footer or the existing block where secondary links live,"
not the top nav, and did not ask for a new site-wide footer. I left this as a backlog note rather
than building it. I also noticed, while reading docs/archive/2026-09-weekly-issue/fable-run/owner-packet-phase3.html for
context, that a "wave 2" plan exists for /thesis/ involving a verdict ledger, a change-condition
status table, a corrections list at /thesis/#corrections, and a /method/ route -- none of that was
in this task's scope and I did not build any of it.

## Fix: judged date

The coordinator flagged a defect after review: the front-page pointer's stamp read "JUDGED SEPTEMBER 20, 2026 · JESSE PIKE", built from the site's `LAST_UPDATED` constant. `LAST_UPDATED` says when the site last shipped a change, not when anyone judged the thesis, so the stamp stated something false under the author's name. This section covers the fix on top of commit `49b114ef9fe52c42b4c44b3f1a2ebbc603f3d789`.

What changed:

- Added `newestThesisJudgment(issues)` to `web/src/data/issueHelpers.ts`. It filters to published issues with a signed thesis score (`weThink.thesis`, `weThink.signedOn`, and `weThink.signedBy` all set), sorts by `published` ascending, and returns the newest one's `{ signedOn, signedBy }`, or `null` if no issue has signed a thesis verdict yet. This is the same kind of published-issue scan `thesisRunningScore` already does in the same file, just picking the newest signed entry instead of scoring every counted one.
- Rewrote `web/src/components/ThesisPointer.tsx` to call that helper instead of importing `AUTHOR_NAME`/`LAST_UPDATED_DISPLAY`/`LAST_UPDATED_ISO` from `meta.ts`. The JUDGED line now renders `formatShortDate(judgment.signedOn)` for the visible date and `judgment.signedOn` (the raw ISO string) for `<time dateTime>`, with `judgment.signedBy` as the name — matching the short-date, uppercase-via-CSS style every other JUDGED stamp on the site already uses (`DomainBoard.tsx`, `MarketPicture.tsx`, `IssueArchive.tsx`). When `newestThesisJudgment` returns `null`, the stamp paragraph is omitted entirely rather than showing a placeholder date.
- Removed the doc-comment paragraph that had justified reusing `LAST_UPDATED` ("marketCall carries no thesis-specific 'judged' date of its own... reuses that constant") and replaced it with a paragraph stating the actual sourcing and the "render nothing rather than invent a date" rule.
- Checked the `/thesis/` route itself (`ThesisPage` in `web/src/App.tsx`) for the same mistake. It does not use `LAST_UPDATED` anywhere in the content I added (the h1, the intro paragraph, the back-link section) — the only place `LAST_UPDATED` appears inside `/thesis/`'s rendered output is inside `HeroContent` (`Hero.tsx`'s pre-existing "UPDATED {LAST_UPDATED_DISPLAY}" line), which `JudgmentBoard`/`HeroContent` already rendered before this task and which the coordinator said to leave exactly as it was. No change made there.
- Added one assertion to `web/tests/e2e/thesis.spec.ts`'s third test (the front-page pointer test). It imports `issues` and `newestThesisJudgment` directly from `src/data` (the same direct-import pattern the file already uses for `marketCall`), computes the expected judgment in Node, and asserts the pointer's `.stamp-label time` has `datetime` equal to `judgment.signedOn` and that the stamp's text contains `judgment.signedBy` — read from the data the same way the component computes it, not hard-coded to today's issue.
- Confirmed `web/tests/e2e/smoke.spec.ts`'s existing test `'every judged stamp with a date also names who judged it'` needed no change and still passes: it scans every `.stamp-label` containing "JUDGED" with a `<time>` child and asserts the text includes "Jesse Pike", which the new stamp still satisfies because `weThink.signedBy` on the one issue in the data is `"Jesse Pike"` (the data invariant that it "must equal AUTHOR_NAME" holds).

What the stamp now reads: **JUDGED 19 SEP 2026 · JESSE PIKE**, with `<time dateTime="2026-09-19">`. This comes from `2026-w36`, the only published issue, whose `weThink.thesis` verdict is "holds" and whose `weThink.signedOn`/`signedBy` are `"2026-09-19"`/`"Jesse Pike"` — the same date the front page's `#we-think` block already shows as "Signed by Jesse Pike · 19 Sep 2026". If a future issue signs a newer thesis verdict, the pointer picks that one up automatically; if the data ever has no signed thesis at all, the pointer renders no JUDGED line rather than a fabricated one.

Test tail (full `npm test` in the OrbStack dev VM, after the fix):

```
verify:integrity passed
verify:issue passed (checks 1-9, 12-16, 10 render-check — all PASS)
build:client / build:server / prerender (5 routes, including /thesis/) / seo / build:feed all OK
verify:dist passed (11a-11i, all PASS)
test:e2e (playwright):
  38 tests using 8 workers
  1 skipped
  37 passed (10.7s)
```

The same pre-existing skip as before; nothing else changed shape.

Recaptured `docs/archive/2026-09-weekly-issue/fable-run/evidence/thesis/after-crop-read-1440.png` and `after-crop-read-390.png` against a fresh build of `mon/thesis` (dist rebuilt by `npm test`, served via a throwaway `vite preview` on port 4181, stopped afterward). Both show the corrected stamp: "STANDING ANALYSIS / Does security spending lag infrastructure spending? / Infrastructure is running ahead. Security is splitting, not booming. / JUDGED 19 SEP 2026 · JESSE PIKE / Read the analysis and its record." No other visible change from the prior crop — same layout, same copy, only the stamp's date and the underlying reasoning changed.

Files changed in this fix: `web/src/data/issueHelpers.ts` (new `newestThesisJudgment` export), `web/src/components/ThesisPointer.tsx` (rewritten to use it, doc comment corrected), `web/tests/e2e/thesis.spec.ts` (one new assertion). No other file touched.
