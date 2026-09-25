# SEC-MARKET-AUTO-001 — Step 1: stop rendering judged content

Branch `mon/facts-only`, worktree `sec-market-wt/facts-only`. Governing plan: `docs/active/autonomy-coverage-plan.md`, approved by D-76 and D-77.

## Fix pass (same branch, after coordinator review)

The coordinator reviewed the after captures below and asked for three changes. All three are done, tested, and pushed.

**1. Merged `origin/preview`.** Brought in step 0's refreshed scorecard figures (`web/src/data/prints.ts`, `web/src/data/evidence.ts`) and the EDGAR daily revenue runner (not yet wired to a page). One conflict, in `web/package.json`'s `test:data` script list — both branches had added a test file to it — resolved by keeping both additions (`run-status.test.ts` and `edgar-logic.test.ts`). Nothing else conflicted. Merge commit `9cf3868`.

**2. One date source for the whole page.** The rail said "AS OF 21 SEP 2026," the header's masthead date and the front-page "Site updated" line said "September 21, 2026," and the run-status box said "Figures checked 25 Sep 2026" — four places, two different dates, because `LAST_UPDATED_ISO`/`LAST_UPDATED_DISPLAY` in `web/src/data/meta.ts` were hand-set constants independent of `runStatus.lastChecked`. Fixed by deriving both from `runStatus.lastChecked` directly: `export const LAST_UPDATED_ISO = runStatus.lastChecked` and `export const LAST_UPDATED_DISPLAY = formatLongDate(LAST_UPDATED_ISO)`, a new long-form date formatter (`"September 25, 2026"`) added to `web/src/data/dates.ts`. Every component that read those two constants — `Header.tsx` (masthead date), `ProvenanceRail.tsx` ("AS OF"), `SiteMasthead.tsx` ("Site updated"), `HowThisWorks.tsx`, `IssueHero.tsx`, `Hero.tsx` — now reads the same derived value with no component code changed. `generate-seo.ts`'s JSON-LD `dateModified`/`datePublished` and the sitemap's `<lastmod>` already import `LAST_UPDATED_ISO` from `meta.ts`, so they stay in step automatically, with no separate edit needed.

Two tests enforce this going forward: a data-level pair in `web/tests/run-status.test.ts` ("meta.ts date derivation (single source)") asserting `LAST_UPDATED_ISO === runStatus.lastChecked` and `LAST_UPDATED_DISPLAY === formatLongDate(runStatus.lastChecked)`; and an e2e test in `web/tests/e2e/smoke.spec.ts` ("every as-of / site-updated / masthead date on the front page matches runStatus.lastChecked") that reads all four rendered dates back off the live front page — the rail's `<time>`, the header's `<time>`, the masthead's stamp text, and the run-status line — and fails if any of them disagrees with `runStatus.lastChecked`.

**3. Platform pressure and vendor-position labels are gone from live pages.** `<PlatformPressure />` is removed from `FrontPage()` in `web/src/App.tsx` — the whole section, not just its judged "read" column removed in step 1's first pass. The component file itself is untouched and still exported, the same as `DomainBoard.tsx`'s now-unreachable `TempoSection`; it simply has no route rendering it. `'platforms'` was removed from the front-page must-see list in `web/scripts/prerender.ts` and from the standing-reference id list in `web/tests/e2e/issue.spec.ts`.

I checked every other live surface named in the request — the scorecard (`PrintGrid.tsx`), the landscape cards (`DomainBoard.tsx`), what-moved (`WhatMoved.tsx`), and the evidence library/drawer — for anything rendering `Holding`/`Buying in`/`Outrun`/`Challengers` or `incumbent`/`challenger`/`early`/`platform` as a visible label. The scorecard, landscape cards, and evidence surfaces never rendered a position label to begin with (confirmed by reading each component; PlatformPressure was the only one that did). What-moved had a real leak: `web/src/data/whatMoved.ts`'s `trackedPrint()` pulled its text from `platformPressure.outrun`, choosing whichever row's `.read` sentence said "printing faster" — a judged competitive-position comparison (e.g. "X at +43% and Y at +25% are printing faster in the same category") — and placed it in the **TRACKED** column of "What moved," mislabelled, because the underlying print value was tracked even though the sentence around it was not. Removed `trackedPrint()` and its now-unused `fasterRead`/`printMove` plumbing entirely rather than reworded, since there's no factual substitute for "who is outrunning whom" without inventing one; "What moved" now shows only `trackedCapital()` and `trackedMa()`, both already purely factual. The one place `platformPressure` data is still read — `platformPressure['buying-in']` inside `whatMoved.ts`'s `trackedMa()` fallback — is kept, because that grouping selects by the factual `absorbed` position (an acquisition), which the coordinator's instruction explicitly exempts ("Acquisitions stay visible where they already appear as facts").

New assertions in `web/tests/e2e/smoke.spec.ts`: `#platforms` and `.pressure` both assert `toHaveCount(0)` on the front page, and an exact-text check confirms `Holding`, `Buying in`, `Outrun`, `Challengers`, `Incumbent`, `Challenger` render zero times anywhere on the page.

**Test results after the fix pass:** full `npm test` inside the OrbStack dev VM, exit 0 — 38 e2e tests passed, 1 skipped (same pre-existing skip as the first pass), 0 failed. All five build-time verify gates and prerender's section-nesting check passed.

**Front-page height, after the fix pass (`after2-front-*` in this directory):** 1440px full page 11,661px (down from 13,263px after the first pass — Platform pressure's removal accounts for the drop). 390px full page 10,549px (down from 12,467px). Screenshots: `after2-front-1440-viewport.png`, `after2-front-1440-full.png`, `after2-front-390-viewport.png`, `after2-front-390-full.png`. I looked at all four before writing this section: the rail, header, masthead, and run-status box all now read "25 Sep 2026" / "September 25, 2026" consistently, and a full top-to-bottom scan of the 1440px capture confirms no "Platform pressure" heading, no group headers (Holding/Buying in/Outrun/Challengers), and no position column anywhere on the page. The vendor figures visible in these captures also differ slightly from the first pass's `after-front-*` captures (e.g. Cato Networks +42% vs. +43%) because the `origin/preview` merge (item 1) brought in step 0's refreshed scorecard data.

**Commits:** `c61e69b` (step 1, first pass) → `9cf3868` (merge of `origin/preview`) → this fix pass's own commit, reported to the coordinator separately with its SHA.

## What this step does

Every live page stops showing stances, rankings, forecasts, and interpretive sentences. Tracked (mechanically refreshed, no-judgment) content stays. The issue archive and `/thesis/` are kept as unaltered dated-archive pages, each with one added notice line. The front page gets a new three-state "run status" line where the old issue strip used to sit.

## Every element removed or changed, with file:line

All paths are relative to `web/`.

### `src/App.tsx` — front page composition
- `FrontPage()` (around line 72 pre-edit, now ~71–96): removed `<IssueStrip>`, `<WeThink issue={latestIssue} condenseThesis />`, `<Hypotheses />`, `<ThesisPointer />`, the `<details id="watch"><WatchList /></details>` block, and `<DomainBoard surface="tempo" />`.
- Added `<RunStatus />` in the slot the old `<IssueStrip>` held (line ~75), and `<IssueLanes issue={latestIssue} showWhy={false} />` (line ~110–119) so the front page's lanes no longer carry the "why it matters" judged sentence.
- Disclosure summaries renamed: "What moved: tracked prints and capital", "M&A and funding activity".
- `IssuePage` (line ~143) now renders `<ArchiveNotice text="Signed weekly issues were discontinued on 25 September 2026. This page is kept unchanged as a dated record." />` before `<IssueHero>`.
- `ThesisPage` (line ~156) renders `<ArchiveNotice text="This analysis is kept as a dated record and is no longer updated." />` inside `<section id="thesis">`.
- Removed now-unused imports: `Hypotheses`, `IssueStrip`, `ThesisPointer`, `WatchList`. Added `RunStatus` import and a local `ArchiveNotice({ text })` helper.

### `src/components/DomainBoard.tsx` — landscape cards
- `LandscapeSection()` (line ~32–82 pre-edit): removed the `DirectionGlyph` function and its call, the posture/tag chip, the `JudgedStampSpaced` block (HORIZON / CONFIDENCE), and the `domain.why` / `domain.summary` prose. A card now shows only the domain name, the TRACKED print, and the evidence link.
- Removed unused imports (`claimId`, `effectiveJudgment`, `reconfirmations`, `JudgedStampSpaced`, the `Momentum` type) and the now-dead `landscapeConfidenceVaries()` helper.
- `TempoSection` (unedited, still in the file) is now unreachable from any live route — its only call site (`<DomainBoard surface="tempo" />` on the front page) was removed in `App.tsx`. Left in place per the "never delete a component" rule; it simply has no route rendering it.

### `src/components/MarketPicture.tsx`
- `DomainRow()` (line ~6–40): removed the `POSTURE_MEANING` map, `JudgedStamp`, the posture chip, and the horizon line. Removed the now-unused imports that fed them.

### `src/components/PlatformPressure.tsx`
- Line ~24–58: removed the "Judged read" column — the desktop `<th>`/`<td>` and the mobile `<p>{row.read}</p>` / `JudgedStampStacked` — and relabeled the remaining header "TRACKED PRINTS · JUDGED READ" to "TRACKED PRINTS". Table `colSpan` 4→3.
- Line ~38: `groupCopy` softened from posture-framed labels to plain state words — `Holding`, `Buying in`, `Outrun`, `Challengers`. This is a judgment call I'm flagging below, not a mechanical removal.
- Removed the now-unused imports that only fed the judged column.

### `src/components/WhatMoved.tsx`
- Line ~27–56 (old numbering): removed the entire "JUDGED" column/div — `weekMoves.judged`, the `AUTHOR_NAME` byline, the `FileSearch` icon import. Only the TRACKED column remains. Per-item `note` fields inside the tracked list were left alone; they are dated transaction caveats (e.g. "still private, no disclosed multiple"), not stances.

### `src/components/ActivityBoard.tsx`
- Line ~41: removed the `activityRead` import and its `<p>{activityRead}</p>` render — the interpretive framing sentence from `src/data/activity.ts` ("capital heat runs ahead of disclosed revenue…"). Per-item `note` fields left alone (factual transaction caveats).

### `src/components/FollowLine.tsx`
- Line ~7: removed "and a signed read publishes most weeks" — no longer true once judged reads stop shipping weekly.

### `src/components/IssueLanes.tsx`
- Line ~28: added `showWhy?: boolean` prop, default `true`. Line ~97: `{item.why ? …}` gated to `{showWhy && item.why ? …}`.
- The front page passes `showWhy={false}` (in `App.tsx`); the issue permalink (`/issues/<id>/`) doesn't pass the prop, so it defaults to `true` and stays byte-identical to before. This was the way to drop the judged "why it matters" line from the live front page without touching the locked issue archive content.

### `src/components/Header.tsx`
- Line ~17: nav label `'Issue'` → `'Status'`. The href is unchanged (`#overview`).

### `src/components/ProvenanceRail.tsx`
- Line ~1–17: replaced the TRACKED/JUDGED two-item `<ul className="rail__legend">` key with a single sentence: `<p className="rail__statement">Sourced facts, checked and published automatically. No stances, rankings or forecasts.</p>`.

### `src/components/SiteMasthead.tsx`
- Whole file effectively rewritten (lines 1–39 pre-edit): removed the "Domain stances judged {date} by {author}" clause and the computation feeding it. The stamp line is now `{SITE_DISCLAIMER} · Site updated {LAST_UPDATED_DISPLAY}.`

### `src/components/IssueArchive.tsx`
- Line ~7: added `<p className="archive-notice">Signed weekly issues were discontinued on 25 September 2026. This page is kept unchanged as a dated record.</p>` directly after the `<h1>` on `/issues/`.

### `src/data/meta.ts`
- Line ~51 (`SITE_DESCRIPTION`): rewrote from a first-person "practitioner's read... what it means if you run a security program" framing to a factual one: "Public, sourced facts about the business of the security market: who is growing, stalling, consolidating, being bought, or in financial trouble. Collected, checked and published automatically, with no stances, rankings or forecasts. Public sources only. Run by Jesse Pike."

### `src/components/HowThisWorks.tsx`
- Rewrote the intro paragraph and the "How editions age" section (renamed "How the tracker ages") to match the no-judgment framing. Left the "Signals we use" and "How we turn that into a call" tables alone — general method documentation, not a live judged call.

### `scripts/prerender.ts` — build gate
- `MUST_SEE_SECTION_IDS.front` (line ~63–72): dropped `'we-think'`, `'read'`, `'hypotheses'` from the required-section list for the front-page route kind. Everything else (`overview`, `market`, `formation`, `absorption`, `prints-this-week`, `capital`, `follow`, `landscape`, `platforms`, `prints`) is unchanged. Comment added explaining why.

### `scripts/generate-seo.ts`
- Line ~35: imported `SITE_DESCRIPTION`, `SITE_HEADLINE`.
- Line ~234–256: the front-page `Report` JSON-LD now uses `headline: SITE_HEADLINE, abstract: SITE_DESCRIPTION` instead of `marketCall.headline` / `marketCall.subhead`. The `'thesis'` route's JSON-LD is untouched — it still correctly carries `marketCall.headline`, since that page is the one place the judged thesis still legitimately lives.
- Line ~116–140: **relaxed** the two OG-staleness assertions (`ogImageAlt`/`twitterImageAlt` `.includes(marketCall.headline)`) down to existence-only checks, with a comment explaining why (see "Relaxations" below). The separate `og.svg`-vs-`marketCall`/`contextStats` internal-consistency check was left untouched.

### `index.html`
- Line ~23–48: added an HTML comment flagging that `public/og.png` still shows the retired thesis headline as baked-in pixels and is deliberately not regenerated this step. Changed `og:image:alt` and `twitter:image:alt` to "Security Market Pulse — a sourced, evidence-linked picture of the security market, updated as facts change." `<title>` and the other meta descriptions were already factual and are unchanged.

### New files
- `src/data/runStatus.ts` — `RunState` type (`'updated' | 'no-change' | 'incomplete'`), a `RunStatus` shape, and the exported `runStatus` value currently set to `{ lastChecked: '2026-09-25', state: 'updated', failedSources: [] }`.
- `src/components/RunStatus.tsx` — renders `id="overview"` (reusing the id the old issue strip held, so the header nav and the prerender gate needed no other changes), one line per state via a `statusLine()` switch.
- `tests/run-status.test.ts` — 4 unit tests over the three states plus a sanity check on the shipped default.

### CSS (`src/index.css`)
- Added `.rail__statement` (+ mobile variant), `.archive-notice`, `.run-status`/`.run-status__line`/`.run-status__line--{updated,no-change,incomplete}`/`.run-status__failed`. Nothing existing was deleted; the old `.rail__legend`/`.rail__state*` rules are still in the file, just no longer referenced by any live component.

## What a reader sees on the first screen

**Front page, 1440px, before → after:** the old first screen was the H1, a description that read like a personal newsletter ("A practitioner's read on... what it means if you run a security program"), a stamp line naming who judged domain stances and when, a black "THIS WEEK" issue strip with the week's signed one-line read, and landscape cards each carrying a posture chip (PREPARE/INVESTIGATE/etc.), a horizon line, and a JUDGED stamp. The after screen keeps the same H1 and layout shell but the description is now the factual "Public, sourced facts about..." wording, the stamp line drops the "Domain stances judged" clause, the black strip is now a single line reading "Figures checked 25 Sep 2026 · every source collected," and the landscape cards show only the domain name, its TRACKED supplier prints, and an evidence link — no chips, no posture, no horizon, no JUDGED stamp anywhere in that fold.

**Front page, 390px:** same substitution — nav has one fewer word-wrapped clause, the run-status box is much shorter than the old issue strip was, so more of "The market by domain" is visible without scrolling.

**Page height, front page:** 1440px full-page height went from 15744px (before) to 13263px (after) — about 16% shorter, mostly from the removed WeThink/Hypotheses/ThesisPointer/watchlist/tempo blocks and the flattened landscape cards. 390px went from 18669px to 12467px — about 33% shorter, since those same blocks reflow to more vertical space on mobile.

**`/issues/2026-w36/` (permalink), 1440px:** unchanged below the fold; the only visible difference is one added notice box right after the header: "Signed weekly issues were discontinued on 25 September 2026. This page is kept unchanged as a dated record." Height grew from 5712px to 5807px at 1440 (95px, exactly the notice box), and 8137px to 8293px at 390.

**`/thesis/`, 1440px:** same pattern — one notice line added ("This analysis is kept as a dated record and is no longer updated.") directly under the intro paragraph, everything else on the page byte-identical. Height grew from 1717px to 1779px at 1440, and 2986px to 3061px at 390.

**`/issues/` (archive index):** unaffected by this step's content changes; captured for completeness. 1440px full height 900px (single viewport, no scroll needed), 390px 844px.

Screenshots are under `docs/active/auto/step1/`: `before-front-*`, `after-front-*`, `before-issue-*`, `after-issue-*`, `before-thesis-*`, `after-thesis-*`, `after-archive-*`, each at `1440-viewport`, `1440-full`, `390-viewport`, `390-full`. I looked at the after-captures directly (front and issue and thesis, both widths) before writing this report and confirmed the notice boxes render correctly and no chip/posture/JUDGED-stamp content survives on the front page.

## Test results

Full `npm test` inside the OrbStack dev VM: **exit 0.** That includes `lint`, `test:data` (now including `tests/run-status.test.ts`), `build` (client build, SSR build, `prerender`, `generate-seo`, `build:feed`, `verify:dist` — all five build-time verify gates plus prerender's own section-nesting check passed), and `test:e2e` — **37 passed, 1 skipped**, 0 failed.

e2e specs updated to match the new page: `tests/e2e/smoke.spec.ts` (rewritten to check `#overview .run-status__line`, assert `toHaveCount(0)` on `#hypotheses`/`#we-think`/`#read`/`#watch`/`.domain-card .chip`/`PREPARE` text/domain-tempo elements, and simplified the judged-stamp test to assert zero judged stamps on the front page — the earlier assumption that `/thesis/` still used the literal `JudgedStamp` component was wrong; it uses "Signed by X · date" text instead, not that component), `tests/e2e/issue.spec.ts` (split section-id lists into front-lane vs. standing-reference sets, added archive-notice assertions), `tests/e2e/thesis.spec.ts` (added the archive-notice assertion, rewrote the front-page pointer test to assert the judged argument is gone).

One flake during the session: a `test:e2e` run failed once with the Playwright dev-server exit code 143 ("webServer was not able to start"). No stray process was holding the port; two standalone re-runs both passed cleanly (37/1). Treated as a one-off VM flake, not a regression.

## Relaxations — minimal, explained

One build gate relaxation, in `scripts/generate-seo.ts`: the OG-staleness check that asserted `og:image:alt`/`twitter:image:alt` **contained the literal judged thesis headline** was loosened to an existence check (alt text is non-empty and present). This was necessary because item 5 of the task explicitly asks for factual alt text and explicitly says not to regenerate `og.png`'s baked-in pixels this step — those two requirements are incompatible with a gate that requires the alt text to literally repeat the old thesis headline. The image-internal consistency check (`og.svg` contents vs. `marketCall`/`contextStats`) was left untouched since nothing in this step touches that asset or that data.

## Judgment calls to flag

1. **`PlatformPressure.tsx` `groupCopy` relabeling** ("Holding", "Buying in", "Outrun", "Challengers"): the task's "keep factual columns" framing doesn't map cleanly onto this component's actual schema (vendor / position-group / tracked print / judged read — there's no target/acquirer/price/status/date here). I removed the literal judged-read sentence and JudgedStamp, and kept the vendor + position-group as structural content, but softened the group labels themselves since the original wording ("Holding the line," etc.) read as interpretive framing rather than a plain state name. This is a step beyond mechanical removal — flagging it for review rather than presenting it as a pure deletion.
2. **`public/og.png` not regenerated**: the social-preview image still shows the retired thesis headline as pixels. Flagged in an `index.html` comment. Fixing this needs either a design pass on a new OG image or accepting a temporary mismatch between the (now factual) alt text and the image contents.
3. **`TempoSection` in `DomainBoard.tsx`** is now dead code — still exported, no longer called from any route. Left in place per the no-deletion rule; worth a backlog note if the owner wants it either wired back in somewhere or formally retired later.

## Not touched

`web/src/data/prints.ts` and `web/src/data/evidence.ts` — untouched, per the hard constraint. No component file, CSS rule, or data export was deleted; every change stopped something from rendering rather than removing it from the codebase.
