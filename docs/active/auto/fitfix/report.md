# AUTO-001 fix pass — report

Worktree: `/Users/jessepike/code/projects/sec-market-wt/fitfix`, branch `mon/fitfix` (based on `preview`).
Scope: the eight numbered items in the fix-pass brief, built against the two blind scores of `preview` under rubric v3.0 (Opus 5.5: 51.4/100, GPT-6 Sol: 54.2/100, both "not fit for purpose").

## 1. Every blocker finding fixed

**Mislabelled figure — Microsoft Entra ID / Defender for Office 365 (both scorers, blocker 1).** Both rows carried Microsoft's whole-company revenue growth on a product line Microsoft does not separately disclose. `web/src/data/tracker/suppliers.ts`: removed the `revenue` field from both `msft-entra` and `msft-defender-o365`; `ownership.status` now reads "Segment of Microsoft Corporation (publicly traded, Nasdaq: MSFT). No separate revenue disclosed." The table now shows "–" for growth on these rows. Verified: `web/scripts/verify-tracker.ts` gate 7 now fails the build if any `kind: "segment"` supplier carries a `revenue` field at all, so this cannot regress silently. Screenshot: `front-fold-1440.png` shows the Microsoft Defender for Endpoint row with "–" across Rev. growth / Prior q / Own metric and "Segment of Microsoft" in the last column.

**SailPoint's period label (Opus, blocker 1 sample; both scorers on the underlying "what changed" defect).** SailPoint and Okta's most recent quarter (period end 2026-07-31, each filer's fiscal Q2 FY2027) was hand-labelled "Q4 FY2027"; the prior quarter (2026-04-30, fiscal Q1 FY2027) was labelled "Q3 FY2027." Both filers have a 31 January fiscal year end, so Q4 only lands on a July period end for a company whose fiscal year ends in July, which neither does. Fixed the four period strings in `suppliers.ts` and the matching text in `web/src/data/tracker/events.ts` and `web/src/data/evidence.ts` (titles, canonical URLs). Verified two ways: (a) a new pure function, `expectedFiscalQuarter(periodEnd, fiscalYearEndMMDD)` in `web/src/data/edgarLogic.ts`, derives the correct fiscal quarter from a period end and a filer's fiscal year end, with 5 unit tests in `web/tests/edgar-logic.test.ts` covering the SailPoint/Okta case, a fiscal-year-end-itself edge case, and a calendar-year filer; (b) `verify-tracker.ts` gate 8 calls that function for every supplier with an `edgarId` and a `"Q<n> FY<year>"`-shaped period label and fails the build on any mismatch against `edgarRegistry.ts`'s fiscal year end — this is a general audit, not a spot fix, so it also covers every other supplier with a fiscal-labelled period, addressed below.

**Audit every period/fiscal label against edgarRegistry (item 1's general instruction).** Rather than hand-checking each of the 74 suppliers, gate 8 above audits all of them at build time. `npm run verify:tracker` passes cleanly against the current data (74 suppliers), meaning no other supplier currently carries a mismatched fiscal-quarter label.

**"What changed" list citing prior-year comparatives (both scorers: "filed its 10-Q for the quarter ended 2025-07-31").** Root cause: `edgarFacts.json`'s de-duplication keeps the latest-filed value per period end, and a 10-Q's prior-year comparative fact gets the same `filedDate` as the current quarter's own fact — so the naive "any filing filed in the last 30 days" query picked up the restated comparative alongside the real new filing. Rewrote `edgarFilingsInLast30Days` in `web/src/data/tracker/derive.ts` to first find each supplier's chronologically latest quarter by `periodEnd`, then check only that one quarter's `filedDate` against the 30-day window — a restated comparative for an older `periodEnd` is never considered regardless of its `filedDate`. Verified: new unit test in `web/tests/tracker-data.test.ts` ("never reports a restated prior-year comparative as a new filing"), plus `verify-tracker.ts` gate 9, which independently re-derives each supplier's true latest quarter straight from `edgarFacts.json` and fails the build if what `edgarFilingsInLast30Days` returns ever disagrees — so a future edit to that function's selection logic cannot silently reintroduce the defect.

**Bare growth figure with no named metric (Opus: Fortinet's landscape-card "+52%").** The landscape card itself is gone (item 4 below), but the underlying gap — a `headlineMetric` with no label — is closed generally: `verify-tracker.ts` gate 10 fails the build if any `headlineMetric.label` is blank. Fortinet's own tracker entry already names its metric ("product revenue"); this gate exists so no future entry can omit one.

## 2. Gates added to `verify:tracker`

`web/scripts/verify-tracker.ts` gained six gates (7–12), documented in the file's own header comment:

- **7 — segment/parent-figure.** A `kind: "segment"` supplier may not carry a `revenue` field.
- **8 — fiscal period label.** A `"Q<n> FY<year>"` period label must match `expectedFiscalQuarter(periodEnd, fiscalYearEnd)`.
- **9 — what-changed latest-quarter.** Every EDGAR filing the 30-day "what changed" window would show must be that supplier's own chronologically latest quarter, never a restated comparative.
- **10 — metric label.** Every `headlineMetric` must carry a non-blank `label`.
- **11 — staleness vs. EDGAR (item 5).** A supplier's `revenue.latest.periodEnd` may not be older than the latest quarter already on file for the same `edgarId` in `edgarFacts.json`.
- **12 — run-status consistency (item 5).** `runStatus.state` may not read `"updated"` while gate 11 found a stale figure.

All six ran clean against the corrected data (`74 suppliers, 63 events` — see `verify:tracker passed` in the build log below).

## 3. Stale figures fixed

- **Cato Networks (both scorers; Opus's sample S1).** The table showed $350M ARR from a 24 Feb 2026 record while Cato had published $415M ARR (+42% YoY) on 27 Jul 2026 — 61 days before scoring. Updated `suppliers.ts`'s `headlineMetric` to $415M/+42%, added a new evidence record `TR-cato-3` sourced to Cato's own blog post, and noted in `TR-cato-2`'s `limitations` that it is superseded. Verified against the source cited in the Opus score (Cato's PR Newswire listing) during step 0 of this pass.
- **Snyk (Opus's sample S2).** The record showed a $530M Series F (9 Sep 2021) and stated "no later funding round was found," but Snyk announced a $75M extension to that same round on 30 Sep 2021. Confirmed via WebFetch against Snyk's own PR Newswire release (WebSearch's budget was exhausted mid-session; fell back to WebFetch against the newsroom listing and the release itself). Updated `suppliers.ts`'s `lastRound` to $605M total ($530M initial + $75M extension), added evidence record `TR-snyk-2` for the extension announcement, and updated `TR-snyk-1`'s `limitations` to describe the supersession. No funding round after 2021 was found in Snyk's newsroom, so this is the correct latest figure.
- **Sol's three landscape-card figures (Netskope +31%, Rubrik +32%, SailPoint +28%, all in the now-removed `#landscape` section).** These figures lived only in `DomainBoard.tsx`'s `LandscapeSection`, which no longer renders anywhere (item 4). The tracker's own Netskope, Rubrik and SailPoint rows carry current, correctly labelled figures.
- Checked Abnormal Security and Delinea (Opus's samples S4/S5, both flagged "no newer figure found" by the scorer itself) — confirmed no newer public figure exists; no change needed.

## 4. Pre-tracker material removed from the front page

Removed from `web/src/App.tsx`'s `FrontPage()`: the old landscape cards (`DomainBoard`'s `LandscapeSection`, including "Tracked suppliers and the latest sourced figure for each"), the second "security market, by domain" scorecard, "What moved" (`WhatMoved`), the activity/M&A notes (`ActivityBoard`), the "How a posture is set" panel (`NextEdition`'s `method-band` block, including its "Standing analysis" link — `ArchiveLinks`' existing "Standing thesis" link already pointed at the same page, so no replacement link was needed), and the "Frozen from ..." footer (`MethodologyNote`). None of the four now-orphaned component files (`DomainBoard.tsx`, `ActivityBoard.tsx`, `MarketLayersChart.tsx`, `WhatMoved.tsx`) were deleted, per the hard rule that a component that stops rendering stays as a file.

`EvidenceDrawer.tsx` and `EvidenceLibrary.tsx`: the front page's evidence drawer and evidence library used to be able to surface a thesis-era judged record (non-empty `interpretation`). `EvidenceDrawer` now renders its "Interpretation" and "Limitations / confounds" sections conditionally (every `TR-`-prefixed tracker record's `interpretation` is empty by construction, so this never shows on a tracker record but still shows on an archive page's judged record). `EvidenceLibrary`'s front-page instance now filters to `TR-`-prefixed records only and no longer searches the `interpretation` field.

Grepped the built HTML of every live route (`/`, `/corrections/`, and `/thesis/` as a check that archive pages are correctly exempt) for the rubric's banned judgment words plus "Watch", "story", "acceleration", "strongest". Remaining hits on `/` and `/corrections/` are all in the methodology/disclosure copy ("the sourcing ladder, strongest first" — a table caption; "weak" describing survey-source reliability; "Separate the fact from the story" — a step in the site's own editorial-discipline explanation) — these describe the site's own rules, not a supplier's prospects, so they are not judgment language under the rubric's definition ("an interpretation of what a fact means for a supplier's prospects"). The one hit of "Watch whether it survives as a product or becomes a feature" on `/corrections/` is inside quotation marks in the 21 September correction record, describing what the (unrendered) `PlatformPressure` row used to read — permitted under the task's carve-out for a correction quoting the retracted sentence. `/thesis/` (an archive page, exempt) still carries "accelerating"/"acceleration"/"strong" in its own unaltered argument, as expected.

## 5. Run-status line

Added `verify-tracker.ts` gates 11 and 12 (above): the build now fails if any tracked figure is behind EDGAR's own latest quarter for the same filer, and separately fails if `runStatus.state` claims `"updated"` while such a figure exists. This makes the front page's "Figures checked 26 Sep 2026 · every source collected" line a verified claim rather than a hand-typed one — it currently passes because gate 11 found no stale figure. A fuller pipeline that writes `runStatus.ts` automatically from the collection run was judged out of scope for this pass (see "Disagreements" below).

## 6. Phone (390px) fixes

- **Tap targets.** `.evidence-link--compact` (the small "src" mark) was `min-height: 0` on the desktop layout. Added a phone-width override (inside the existing `@media (max-width: 640px)` block) setting `min-height: 24px; min-width: 24px;`. Measured via Playwright at 390px: all sampled compact links now render at 24×32.6px or larger.
- **Row wrapping instead of clipping.** `.tracker-row__toggle` had no `flex-wrap`, and `.tracker-row__summary` was `white-space: nowrap` with no shrink — a long supplier name plus its summary figure overflowed the row's width instead of wrapping (the Exabeam/Cato/Sysdig rows both scores flagged). Added `flex-wrap: wrap` to the toggle, `min-width: 0; overflow-wrap: break-word` to the name, and `white-space: normal; flex: 0 1 auto` to the summary. Verified at 320px: all three named rows now wrap cleanly with no clipped text (`row-exabeam-320.png`, `row-cato-320.png`, `row-sysdig-320.png`).
- **No horizontal scroll at 320px.** Measured via Playwright: `document.documentElement.scrollWidth === clientWidth === 320`.
- **Supplier rows visible on first or second screen.** At 390×844 (first screen), the run-status line and the first domain group's heading are visible; the first supplier rows with figures are fully visible by 390×1688 (second screen) — see `front-fold-390.png` and `front-secondscreen-390.png`. This meets the stated bar ("first or second screen"); it does not reach the first screen alone, which was not required.

## 7. Tests, accessibility, and screenshots

`npm test` (lint → 246 data tests → full build, including all `verify:*` gates → 30 Playwright e2e tests across `chromium`/`desktop`/`phone` projects) passes clean. Fixed three pre-existing test bugs surfaced by this pass's own data changes, all in test code, not product code:

- `tests/e2e/issue.spec.ts`: the "Market" nav-link test used a non-exact role-name match, which now also matches the header brand link's accessible name ("Security Market Pulse" contains "Market"). Changed to `{ name: 'Market', exact: true }`.
- `tests/e2e/smoke.spec.ts` (two tests): assumed the compact evidence link's accessible name was its visible text ("src"); it is actually overridden by an `aria-label` naming the source and context. Both tests now target the Microsoft Entra ID row's Ownership-cell link by its aria-label prefix (`/^Ownership — source:/`), since the row now also carries a second compact link for its "Latest event" cell.

**Accessibility.** `@axe-core/playwright` is not in this project's dependencies, and no existing axe or accessibility-checking script was found in the repo, so neither of the task's two named options was available; installing a new dependency was treated as outside this pass's scope (a net-new tool, not a fix to what the scores flagged) and is noted below rather than added unilaterally. In its place, ran a manual keyboard pass via Playwright at 1440px against the front page: the skip link is the first Tab stop and works; every header nav link and the first domain's expand link receive a visible 2px solid focus outline in Tab order; a row's expand/collapse toggle is operable with Enter and updates `aria-expanded`; a compact evidence link opens the drawer with Enter; Escape closes the drawer and returns focus to the button that opened it. Color contrast was not checked — no tool for it was available in this pass, and it is not something the two scores flagged, so it is left as a known gap rather than asserted clean.

**Screenshots** (`docs/active/auto/fitfix/`): `front-1440.png`, `front-390.png` (full page); `front-fold-1440.png`, `front-fold-390.png` (first screen only); `corrections-1440.png`, `corrections-390.png` (full page); `corrections-fold-1440.png`, `corrections-fold-390.png` (first screen only). Looked at all eight; the front page and corrections page both render as described above at both widths, with no landscape cards, no "What moved," no activity board, and the Microsoft segment rows showing "–" with the segment-of-parent note.

## 8. Disagreements with the scores

- **GPT-6 Sol's D1 level-5 credit ("show the actual publication date for each figure separately from the site check date")** — not built in this pass. The per-figure `releaseDate` field already exists on `revenue.latest` and is used by the fiscal-label gate; surfacing it in the visible table is a net-new display change beyond the fix-pass brief's eight items, so it was left for a separate pass rather than built here.
- **A machine-written `runStatus` pipeline** (rather than the build-gate consistency check built here) was judged out of scope. The task's own bar was "make runStatus consistent with what's actually on the page after this pass," which the new gates satisfy by making the claim verified rather than trusted; a full collector-writes-runStatus.ts pipeline is a larger architecture change than "at minimum" called for.
- **Accessibility tooling.** Neither scorer could independently verify accessibility without a browser (Sol said so explicitly: "the required axe and keyboard checks could not be established without a browser"). This pass could run a browser and did a manual keyboard pass, but did not install `@axe-core/playwright` since it was not already present and installing new tooling was read as outside the fix pass's scope. This is a gap, not a disagreement with either score.

## Build and test evidence

- `npm run verify:tracker` — 12 domains, 74 suppliers, 63 events, all 12 gates pass.
- `npm run test:data` — 246 tests, 60 suites, 0 failures.
- `npm run lint` — 0 warnings, 0 errors (130 files).
- `npm run build` — all `verify:*` gates, `tsc -b`, client + SSR build, prerender (5 routes), SEO, feed, `verify:dist` all pass.
- `npm run test:e2e` — 30 tests across 3 Playwright projects (chromium/desktop/phone), 0 failures.
- `npm test` — the full chain above, run once end to end, clean.

## Second pass

Scope: the eight numbered items in the coordinator's second fix-pass brief, following two more blind
rescores of `preview` under rubric v3.0 (Opus 5.5: 56.0/100, `docs/active/auto/score2/opus/score.md`;
GPT-6 Sol: 42.0/100, `docs/active/auto/score2/sol/score.md`), both still "not fit for purpose."

**1. Event counts.** Added the five missing 12-month funding events (Torq, Upwind, Chainguard, Claroty,
Xage) to `web/src/data/tracker/events.ts`, each sourced with the same evidence already backing the
supplier's `lastRound`. Added gate 14 to `web/scripts/verify-tracker.ts`: for every supplier whose
`lastRound.date` or `ownership.announced`/`.closed` falls inside the same trailing-365-day window
`eventSummaryForSupplier` uses for the "Events, 12 mo." column, the build now fails unless a
same-type event exists in that window. This is a general audit, not five spot fixes — it will catch
the same defect on any future supplier.

**2. Labels.** CyberArk's Palo Alto Networks acquisition was typed `"shutdown"`; it is now
`"acquisition"` (`web/src/data/tracker/events.ts`, `EV-cyberark-1`). Audited every event's `type`
against its `text` across all 68 events; no other mismatches found. Check Point's email-segment row
(`checkpoint-email`) is renamed to "Check Point Email Security" — the vendor's own current product
name, confirmed via Check Point's own blog announcing the rename from "Harmony Email &
Collaboration" on 2026-03-25 — with its `ownership.status` now reading "Segment of Check Point
Software Technologies..." so it can no longer be confused with the public-company `checkpoint-sase`
row. Added gate 13: the build now fails if two suppliers in the same domain share a display `name`.

**3. Missing facts.** Verified and added, from primary sources: Mitsubishi Electric Corporation's
acquisition of Nozomi Networks (announced 2025-09-09, completed 2026-01-29 — two PRNewswire releases,
`TR-nozomi-1`/`TR-nozomi-2`), updating `nozomi`'s `kind` to `"acquired"` and adding a full `ownership`
block plus `EV-nozomi-1`. Verified and added Rapid7's four board resignations (Burns, Holzman,
Schodorf, Sondhi; effective 2026-08-27), sourced to the company's own SEC EDGAR 8-K (Item 5.02,
`TR-rapid7-5`), as a new `exec-change` event (`EV-rapid7-5`) — no new event type was needed. Did not
attempt a full re-collection, per the brief's explicit constraint.

**4. Run status, made machine-derived.** `web/src/data/runStatus.ts` is no longer a hand-set value —
it is now a pure derivation (`deriveRunStatus()`) computed at import time from
`web/src/data/generated/edgarFacts.json` (`generatedAt`, `failures`) and a new
`web/src/data/generated/collectState.json`, which gained a script-owned `collectorRun` block
(`at`, `state`, `detail`, `restrictedTo`, `failedSources`). `lastChecked` is the older of the two
sources' dates. The state is `'incomplete'` with a plain-language `detail` whenever the last collect
run covered only a slice of suppliers or any source failed; `collectState.json` was seeded with the
real historical restricted run (`SMP_COLLECT_ONLY=optiv,snyk,cyera,rapid7`, 2026-09-26), which is why
the shipped status line now reads "Press, funding and distress sources last checked for 4 of 74
suppliers on 26 Sep 2026 (restricted run: optiv, snyk, cyera, rapid7)" — an honest statement, not a
coincidence matching the brief's example wording. `scripts/collect.sh` and `scripts/auto-publish.sh`
now write `collectState.json`'s `collectorRun` block instead of patching `runStatus.ts` directly (both
verified via `bash scripts/test-auto-publish.sh` on the host, all checks passing); three draft
GitHub Actions workflow files under `docs/active/auto/` that still referenced writing `runStatus.ts`
were updated to match. The rendered-date test (`smoke.spec.ts`, "every as-of / site-updated / masthead
date... matches runStatus.lastChecked") needed no changes since it was already fully derived.

**5. Judgment text on live routes.** `FollowLine.tsx`'s cadence sentence now states the real schedule
("SEC filings refresh daily; press, funding and distress facts refresh twice a week") instead of the
vague "arrive through the week." `HowThisWorks.tsx` no longer imports or renders `signalFamilies` or
`reasoningSteps` from `data/method.ts` — the two tables that carried the exact phrases both blind
scores quoted ("PREPARE only where...", "That is a no-call", "The best check on whether customers
actually spent") are gone from `/`; `data/method.ts` itself is untouched, since that data still backs
the archived `/thesis/` page. A "What is not covered" section replaces them, pointing to the existing
coverage statement rather than duplicating it. On `/corrections/`, the `C-2026-09-21-01` entry
(`web/src/data/corrections.ts`) is edited directly — the one exception to that file's own "append, never
edit" rule, taken because the coordinator's brief named this exact text as something to change and
because the alternative (appending a new entry while the old one keeps rendering) cannot make a live
banned phrase stop being served. The correction now describes the retracted sentence as "a sentence
that described Palo Alto Networks and F5 as hyperscalers" (matching the brief's given wording) and
describes the rows' replacement text — previously quoted verbatim as *"AI security absorbed into a
platform vendor. Watch whether it survives as a product or becomes a feature."*, the exact phrase both
scorers flagged as live forecast language — as "states only that the target was acquired by a platform
vendor, with no claim about what happens to the product next," with no quotation at all. Grepped the
built HTML of `/` and `/corrections/` (the two live, non-archive routes — `/issues/`, each issue
permalink, and `/thesis/` all carry their own "archive/record" notice by design, per D-76, and are
exempt) for the rubric's banned words plus watch, prepare, no-call, best, accelerat, boom, story.
Remaining hits are the pre-existing sourcing-ladder copy ("stays a lead until a stronger source", "the
weakest rung", "strongest first") describing the site's own editorial rules rather than a supplier's
prospects, and one instance of "boom" inside an HTML comment (invisible dev note about a static
`og.png` asset, already flagged in `docs/active/auto/step1/report.md` for a separate owner-approved
regeneration) — no visible, live judgment language found.

**6. Source links.** Replaced ten evidence records' `canonicalUrl` with the specific document rather
than a newsroom index or homepage (Check Point's rename post, Tines's Bloomberg valuation piece,
Sysdig's CEO-announcement press release, Palo Alto Networks' FY2026 10-K filing index, two Cyera
acquisition releases, HiddenLayer's funding release, Veracode's TA Associates release, Delinea's CFO
appointment release, plus the two new Nozomi releases and the Rapid7 8-K), each verified live via
WebFetch. Four facts could not be re-sourced to a specific document after extensive search (Aqua
Security's January 2024 funding, BeyondTrust's 2021 Clearlake investment, Delinea's March 2025 ARR
figure, and its February 2022 TPG rebrand) — per the brief's own instruction, these were dropped
rather than left pointing at a bad URL: the `lastRound`/`ownership`/`headlineMetric` fields citing them
were removed from `suppliers.ts`, and the four now-orphaned evidence records were deleted outright
(`verify:integrity`'s unreferenced-record gate went from 9 back down to its normal 5). Added gate 15:
the build now fails if any evidence record actually used by the tracker has a `canonicalUrl` whose
path is empty or is a single newsroom/index-style segment (news, press, investors, blog, and
similar).

**7. Publication date.** The latest-quarter growth figure now shows its filing date next to its period
in muted mono — "+26% Q Jul 26 · filed 26 Aug" — via a new `formatFiledDate` helper
(`web/src/data/tracker/derive.ts`) and `GrowthCell` in `MarketByDomain.tsx`. Only the `latest` column
carries a `releaseDate` in the data (`prior` periods only record the period they cover, not a separate
filing date), so the prior-quarter column is unchanged. On phone this renders inside the same
already-existing expanded-row markup, so no separate phone-only code path was needed. Keeping the row
one line at 1440 needed a real CSS fix, not just the added text: forcing `flex-wrap: nowrap` on every
`.tracker-figure` first fixed the growth cells but pushed some tables (e.g. Security operations)
142px wider than their container, clipping the Events column out of view — measured directly via a
Playwright script against `.tracker-table-scroll`'s `scrollWidth`. The fix scopes `nowrap` to just the
Rev. growth and Prior q columns (`td:nth-child(2)`/`(3)`), leaving the Own metric and Ownership
columns free to wrap as they always could, since those hold real prose (a PE-ownership or acquisition
description), not a single figure. Re-measured all 12 domain tables at 1440 after the fix: zero
horizontal overflow on every one.

**8. Stable anchors.** Every supplier row now carries `id="s-<supplierId>"`
(`web/src/index.css` also gained `tr[id] { scroll-margin-top: ... }` so the sticky header doesn't
cover a row a link lands on). Palo Alto Networks, CrowdStrike, and Check Point's SASE segment each
belong to more than one domain and so render more than one row; a naive per-row id would have produced
duplicate ids (confirmed: `panw` appeared 5 times, `crwd` 3 times, `checkpoint-sase` 2 times) — invalid
HTML, and the second occurrence would have been unreachable by anchor regardless, since a browser
jumps to the first match. `MarketByDomain` now threads a single `anchoredSupplierIds` set (created
fresh each render) through every `DomainTable` in `trackerDomains` order, so only the first table a
given supplier appears in claims the anchor. Verified against the built HTML: every `id="s-..."`
appears exactly once.

**Accessibility and keyboard.** `@axe-core/playwright` was installed with `npm install --no-save`
(nothing added to `package.json`/`package-lock.json`) and run against the local preview build at 1440
and 390 on both `/` and `/corrections/`: zero violations at every combination, including after the
anchor fix above (duplicate ids are exactly the kind of thing axe's `duplicate-id` rule would have
caught). A scripted keyboard pass tabbed through both routes at both widths with no errors: `/` reaches
well over 200 focusable stops (hit the script's loop cap), `/corrections/` reaches 11 stops at 1440 and
6 at 390.

**Screenshots** (`docs/active/auto/fitfix/`, `after3-` prefix): `after3-front-1440.png`,
`after3-front-390.png` (full page); `after3-front-fold-1440.png`, `after3-front-fold-390.png` (first
screen); `after3-corrections-1440.png`, `after3-corrections-390.png` (full page);
`after3-corrections-fold-1440.png`, `after3-corrections-fold-390.png` (first screen). Looked at all
eight: the run-status banner reads the real restricted-run detail sentence; every growth cell across
every domain (Endpoint and XDR, Security operations, Network and SASE, Identity, Data security,
Vulnerability and exposure management, all spot-checked) stays one line with its filed date at 1440,
with no column clipped off the right edge; `/corrections/` shows the rewritten `C-2026-09-21-01` entry
with no quoted judgment phrase.

**Build and test evidence, second pass.**

- `npm run verify:tracker` — 12 domains, 74 suppliers, 68 events, all 15 gates pass.
- `npm run test:data` — 247 tests, 60 suites, 0 failures.
- `npm run lint` — 0 warnings, 0 errors (130 files).
- `npm run build` — all `verify:*` gates (including new gates 13–15), `tsc -b`, client + SSR build,
  prerender (5 routes), SEO, feed, `verify:dist` all pass.
- `npm run test:e2e` — 30 tests across 3 Playwright projects, 0 failures.
- `bash scripts/test-auto-publish.sh` — host-only bash suite for `auto-publish.sh`, all checks pass.
- axe (`@axe-core/playwright`, dev-only, not committed) and a scripted keyboard pass — 0 violations,
  0 errors, both routes, both widths.

**Not built this pass.** A permanent `@axe-core/playwright` devDependency was deliberately not added —
this pass ran it as an uninstalled (`--no-save`) check to close the accessibility-tooling gap the first
pass's report flagged, without expanding the project's dependency surface beyond what the brief asked
for; a permanent accessibility CI check is a reasonable follow-up but is net-new scope, not part of
this fix pass.
