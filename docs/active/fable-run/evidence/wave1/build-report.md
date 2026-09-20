# T6-2 build report — front-page redesign, step A, wave 1

Branch `mon/wave1`, built from a worktree at `/Users/jessepike/code/projects/sec-market-wt/wave1`, off `preview`. Not merged anywhere. Original build's last commit: `ca2e529 feat(web): add machine-surface links per agent-surface-spec section 6`. A fix pass (T6-7) landed after this report was first written — see that section below for what changed and the branch's current last commit.

## Fix pass T6-7

Four small visual fixes from the coordinator's review of the wave 1 renders, applied on top of the build described below. No new features, no data changes.

1. **Growth figures were colour-coded green/high, red/low in MarketPicture**, which visually ranks suppliers right under a caption that says they are labelled and not ranked, and the figures aren't like for like across vendors. Removed the tone-based colour class from `MarketPicture.tsx` (`market-picture__vendor-value--up`/`--down`) so every figure renders in the same neutral ink colour, same weight and size as before. `PrintGrid`'s scorecard uses its own separate `print-card__value--*` classes and was not touched, confirmed by grep before making the change. The two now-unused CSS rules (`.market-picture__vendor-value--up`, `--down`) were left in `web/src/index.css` rather than deleted, per this fix pass's own instruction not to delete a CSS rule; they're simply unreferenced now.
2. **The domain grid was four columns at 1440**, leaving two orphan cards on their own row, and `align-items` defaulted to `stretch`, so short cards (Cloud Security, Identity, with only one or two vendors) stretched to match the tallest card in their row, leaving large empty white space. Changed `.market-picture__domains` to one column below 700px, two columns from 700px, three columns from 1100px (two even rows of three for the six domains, no orphan), and added `align-items: start` so each card sizes to its own content. Confirmed by screenshot at 390, 800, and 1440 that no card stretches and the three-column layout has no orphan row.
3. **The as-of line sat flush against the issue-meta line with no gap**, because `.issue-hero__asof` had no bottom margin and the shared `.eyebrow` class has zero margin everywhere it's reused. Added `margin-bottom: 0.6rem` (about 10px) scoped to `.issue-hero__asof` alone, so nothing else that reuses `.eyebrow` elsewhere on the site is affected. Confirmed by screenshot that the two lines read as two lines at both widths.
4. **The as-of line mentioned domain stances but rendered on the issue permalink too**, where no domains appear. Added a `showAsOf` prop to `IssueHero` (default `false`); the front page passes `showAsOf`, the permalink page does not, so the description and disclaimer lines still appear on both pages but the as-of line now appears on the front page only. Confirmed by screenshot of `/issues/2026-w36/` that the as-of line is gone while the description and disclaimer remain.

   On the date question: it was a mistake, not a deliberate "latest across domains, platforms, and hypotheses" computation. The as-of line was reading `JUDGED_AS_OF_ISO` from `meta.ts`, a constant whose own doc comment says it covers the tracked hypotheses and platform-pressure reads specifically — not domains — and which happens to hold a different date (17 Aug 2026) than the domain cards (`domain.asOf`, all six of which are `2026-08-16`). I used the wrong constant when I first wrote this line. Fixed by sourcing the date directly from `securityDomains` (the same data `MarketPicture`'s cards read), computed as the latest `asOf` across all domains, so the line can never drift from what the cards say. It now reads "Domain stances judged 16 Aug 2026," matching the cards, and `JUDGED_AS_OF_ISO` remains correctly in use by `hypotheses.ts` and `platformPressure.ts`, which is what it was always for.

### Assertion changes in the fix pass

None. No test's expected behavior was changed. `IssueHero`'s new `showAsOf` prop is additive (defaults to `false`, matching the permalink's existing unchanged call site); the front page's call site was the only one updated.

### Retest and recapture

Killed a leftover `vite preview` process before testing this time (none was actually running, confirmed via `ss -ltnp | grep 4173` before starting). Full `npm test` passed clean: lint (0 warnings, 0 errors), 67 data tests, the full build with all 8 verify:dist checks, and 26 e2e tests (25 passed, 1 skipped). Tail:

```
> web@0.0.0 test:e2e
> playwright test

Running 26 tests using 5 workers
1 skipped
25 passed (9.8s)
```

Recaptured all 12 required screenshots, the market and follow crops, DOM measurements, and the axe scan; overwrote the originals in this folder. New measurements:

| | 1440px | 390px |
|---|---|---|
| `#market` top | 514 | 799 |
| `#follow` top | 7144 | 10919 |
| `#read` top | 14111 | 16570 |
| `#we-think` top | 2234 | 3991 |
| `.we-think__signature` top | 2711 | 5078 |
| Header height | 53 | 113 |
| `#overview` top | 113 | 221 |
| Total page height | 17084 | 21437 |

`#market`'s top moved from 505 to 514 at 1440 (and 789 to 799 at 390) — the small gap added under the as-of line pushes everything below it down by roughly the same amount; nothing else changed shape. Page height moved by single-digit pixels for the same reason. Axe: zero violations at all six page/width combinations, same as the original build.

Nothing looked wrong in the new renders. The three-column grid has no orphan row and no stretched short cards at 1440; the two-column middle breakpoint (checked at 800px) shows the same non-stretching behavior; the single column at 390 is unaffected by the grid change since it was already one column. The neutral-colour growth figures read cleanly against the alphabetical, unranked framing the caption already states. The gap between the as-of line and the issue-meta line reads as two distinct lines at both widths. The permalink page shows the description and disclaimer but not the as-of line, and its layout is otherwise unaffected.

## What was built, file by file

All nine items from design-spec v0.3 step A are built, with the MarketPicture table rebuilt per the coordinator's mid-task spec change (see the dedicated section below).

- `web/src/data/meta.ts` — added `SITE_DESCRIPTION` and `SITE_DISCLAIMER` as constants.
- `web/src/components/IssueHero.tsx` — renders the description, the disclaimer, an as-of line (last-updated date + domain-stances-judged date, both from existing `meta.ts` constants, never the render clock), a "Feed" link next to the eyebrow, and a site-added plain-words note under the h1 when the newest issue's `read` text matches a term in the new site term list. Because `IssueHero` is shared between the front page and the issue permalink, all of this now also appears on `/issues/2026-w36/`. That is a real behavior change beyond the front page and is worth a second look — it was not explicitly ruled out by the spec, and duplicating the description/disclaimer on the permalink reads fine in the screenshots, but it was not explicitly asked for either.
- `web/src/data/jargonNotes.ts` (new) — a small term list; currently one entry, for "lag call."
- `web/src/data/marketPicture.ts` (new) — pure data logic for the new section: which prints qualify per domain, the 120-day "older figure" rule computed from evidence dates, the "previously" match on exact metric label, and the segment tag for the two curated product-line prints.
- `web/src/components/MarketPicture.tsx` (new) — renders the "market" section, one card per domain.
- `web/tests/market-picture.test.ts` (new) — unit tests for the above.
- `web/src/App.tsx` — reordered the front page per design-spec section 3.1 and wired in `MarketPicture` and `FollowLine`.
- `web/src/components/IssueLanes.tsx` — the four lane headings changed to plain words; ids and class names untouched.
- `web/scripts/prerender.ts` — added `market` and `follow` to the must-see section list the prerender gate checks.
- `web/tests/e2e/issue.spec.ts` — added `market` and `follow` to the list of standing-reference ids the e2e suite checks resolve on both the front page and the permalink.
- `web/src/components/HowThisWorks.tsx` — replaced the cadence sentence with the exact wording from the spec.
- `web/src/components/FollowLine.tsx` (new) — the "follow" section: one sentence plus a visible link to `/feed.xml`.
- `web/src/components/Header.tsx` — added a visible "Feed" link to the header nav.
- `web/scripts/generate-feed.ts` — added `<link rel="alternate" type="application/json">` tags for the issue index, the newest published issue's JSON, and the publication ledger, injected into every route the same way the existing RSS link already is.
- `web/scripts/generate-seo.ts` — added those same three URLs to the sitemap, and added `author`, `datePublished`, `dateModified` to the archive page's JSON-LD, computed from the oldest and newest published issues.
- `web/scripts/verify-dist.ts` — added a new gate that fails the build if any alternate link's target file is missing from `dist/`.
- `web/src/components/MethodologyNote.tsx` — added a "Data" line linking to the same three URLs.
- `web/src/index.css` — one commented block appended at the end, styling everything above. No changes to existing rules or tokens.
- `web/package.json` — added the new test file to `test:data`.

## The MarketPicture table: changed from ranked top-three to alphabetical, on the coordinator's instruction

The original design-spec v0.3 called for a ranked "leading vendors" list per domain. Partway through the build, a coordinator message arrived citing an external review: ranking vendors by growth implies a comparison the underlying data can't support, since the growth figures measure different things on different bases, and a ranked list would read as the site author's endorsement of a vendor whose reseller he works for. I applied that change before finishing the task, as instructed.

The table now lists every vendor with a real, comparable growth figure (never a raise, close, or valuation with no rate) alphabetically by name, with no cap unless a domain has more than six, in which case it shows six and a "show all" link to the fuller detail lower on the page. Each entry shows the exact metric label and period from the record, not a normalized figure. A "previously" value appears only when an earlier record from the same vendor uses the identical metric label — different metrics never get compared or connected. Anything more than 120 days older than 2026-09-20, computed from the evidence date, is marked "older figure." The two entries that are a product line rather than the whole company (Palo Alto XSIAM, CrowdStrike Falcon Cloud) are tagged as such. The caption is the coordinator's exact wording. None of "leading," "top," "winner," "best," or a ranking word appears anywhere in the section.

Vendors whose records I found ambiguous, worth a second look before this table is treated as authoritative:

- CrowdStrike appears under two different domains with two different metrics: Falcon Cloud segment ARR under Cloud Security, and total ending ARR under SecOps. Both are real and both are tagged correctly, but a reader skimming both cards could reasonably wonder if it's the same number twice. It isn't.
- Cisco Security's period is an annual figure (FY26) while the accompanying judgment note references a quarterly number. The print itself is annual; the note about the quarter is analysis, not the print's own period, but the two sitting side by side could read as inconsistent.
- SailPoint's period is FY26 ending January 2026, not calendar-quarter aligned like most of the other prints in this table. It's marked "older figure" correctly by date math, but a reader who assumes all periods are calendar quarters could misjudge how current it is.
- The two segment-tagged prints (Palo Alto XSIAM, CrowdStrike Falcon Cloud) are the clearest cases of "this is a product line, not the company," and are the only two carrying that tag; I checked the rest of the qualifying prints by hand and didn't find another segment-vs-company case the tag is missing from.

One more coordinator-requested change: added the sentence "Not a news site and not investment advice." directly under the description line in the hero section, confirmed on the first screen at both 1440 and 390 in the screenshots.

## Test suite

Full `npm test` — lint, 68 data tests (67 plus the new `market-picture.test.ts` file, itself several assertions), the full production build with all verify gates, and the Playwright e2e suite — passed completely against the final committed state. Tail of the run:

```
> web@0.0.0 build:server
✓ built in 26ms

> web@0.0.0 prerender
Prerender OK: route "/" — 13 sections verified un-nested; wrote dist/index.html (235705 bytes).
Prerender OK: route "/issues/" — 1 sections verified un-nested; wrote dist/issues/index.html (5312 bytes).
Prerender OK: route "/issues/2026-w36/" — 6 sections verified un-nested; wrote dist/issues/2026-w36/index.html (30987 bytes).
Prerender OK: 3 route(s) written.

> web@0.0.0 seo
SEO OK: wrote dist/sitemap.xml with 3 route(s) and 3 JSON machine-surface entries.

> web@0.0.0 build:feed
generate-feed OK: dist/feed.xml written with 1 item(s).
generate-feed OK: wrote 1 dist/issues/<id>.json file(s).
generate-feed OK: wrote dist/issues/index.json with 1 entry.
generate-feed OK: wrote dist/issues/lock.json with 1 entry.
generate-feed OK: added feed + 3 JSON alternate link(s) to 3 route(s).

> web@0.0.0 verify:dist
PASS  11a every-route-html-exists — 3 route HTML file(s) present
PASS  11b every-issue-json-exists — 1 issue JSON file(s) present, well-formed, and identity-checked
PASS  11c issues-index-json-exists — 1 entries in the expected newest-first order, full row identity checked
PASS  11d feed-xml-exists-and-parses — 1 <item>(s), guid set and per-item pubDate verified against published date
PASS  11e sitemap-xml-lists-every-route — 3 route(s) present in sitemap.xml
PASS  11f issues-lock-json-matches-source — dist/issues/lock.json matches the source manifest exactly, 1 entry
PASS  11g route-description-meta-identity — front page description confirmed distinct; 2 non-front route(s) verified
PASS  11h alternate-link-targets-exist — 12 alternate link target(s) verified across 3 route(s)
verify:dist passed

> web@0.0.0 test:e2e
Running 26 tests using 5 workers
1 skipped
25 passed (10.0s)
```

One thing worth flagging honestly: a background `vite preview` server I had left running from evidence capture was still holding port 4173 on the first `npm test` run, which made the Playwright webServer step time out. I killed it and reran the whole suite clean; the numbers above are from that clean rerun, not the failed one.

## Assertions changed and why

- `web/tests/e2e/issue.spec.ts`: `STANDING_REFERENCE_IDS` extended from `['read', 'landscape', 'platforms', 'hypotheses', 'prints']` to `['market', 'follow', 'read', 'landscape', 'platforms', 'hypotheses', 'prints']`. Reason: the two new standing sections need the same cross-page presence guarantee the existing ones already have; nothing existing was weakened.
- `web/scripts/prerender.ts`: `MUST_SEE_SECTION_IDS.front` gained `'market'` and `'follow'`. Reason: same as above, at the prerender gate rather than the e2e layer.
- `web/scripts/verify-dist.ts`: `EXPECTED_CHECK_COUNT` raised from 7 to 8 for the new alternate-link check. Reason: a new gate was added; the count exists specifically to catch a forgotten check.

No existing assertion's expected behavior was changed or weakened. Nothing was skipped or deleted.

## DOM measurements

| | 1440px | 390px |
|---|---|---|
| `#market` top | 505 | 789 |
| `#follow` top | 7166 | 10909 |
| `#read` top | 14133 | 16560 |
| `#we-think` top | 2256 | 3981 |
| `.we-think__signature` top | 2734 | 5068 |
| Header height | 53 | 113 |
| `#overview` top (first content) | 113 | 221 |
| Total page height | 17107 | 21428 |

At 390 wide, the header's own date stamp ("AS OF 19 SEP 2026") duplicates the new as-of line's content, so per the spec I left the header alone rather than removing anything from it, and I'm reporting the 221px figure above as the height of everything above the first content element at that width, as instructed.

## Accessibility (axe)

Zero violations at every page and width tested: front page, `/issues/`, and `/issues/2026-w36/`, each at 1440 and 390. Six page/width combinations, six empty violation lists.

## Screenshots

All in `docs/active/fable-run/evidence/wave1/`: `wave1-home-{1440,390}-{full,viewport}.png`, `wave1-issues-{1440,390}-{full,viewport}.png`, `wave1-issue-w36-{1440,390}-{full,viewport}.png` (12 files, the required set), plus targeted crops used for closer visual review: `market-crop-1440.png`, `follow-crop.png`, `crop-read.png`, `crop-hypotheses.png`, `crop-platforms.png`, `crop-prints.png`.

## Visible changes

- Front page reordered: overview, market (new), we-think, the four lanes (now plain-worded), follow (new), landscape, platforms/vendor-lens/prints, standing thesis, hypotheses, then the unchanged depth sections.
- New "The market by domain" section: one card per domain, alphabetical vendor lists with metric/period/older-figure/segment labeling, no ranking language.
- New "Follow" line with a visible RSS link.
- New description, disclaimer, and as-of line under the h1 on both the front page and the issue permalink (a spread beyond the front page alone, flagged above).
- Occasional site-added plain-words note under the h1, visibly labeled.
- Lane headings reworded to plain language.
- "Feed" link added to the header nav.
- Cadence sentence in "How this works" reworded.

## Invisible changes

- Three new JSON-LD/sitemap/alternate-link machine surfaces (issue index, newest issue JSON, publication ledger), reachable via visible links in "How this works" and MethodologyNote but otherwise structural.
- Archive page JSON-LD gained author/datePublished/dateModified.
- A new build gate (verify-dist check 11h) enforcing that every alternate link actually resolves.

## What was deliberately not done, and why

- Step B of the design spec was explicitly out of scope and untouched.
- No data file under `web/src/data/issues/` or `web/src/data/evidence.ts`, and no data VALUES in `prints.ts`, `domains.ts`, or `market.ts`, were touched — only the two new constants in `meta.ts` and the copy strings the spec called out.
- The literal "one table, six rows" instruction from design-spec v0.3 was not built as a `<table>` element. A CSS grid of block cards was used instead, because a real table doesn't accommodate a variable-length vendor list per domain without a lot of extra responsive-table CSS to un-tableize it at 390px, and the codebase already has a block-card idiom (`DomainBoard`) this follows. This is a deliberate deviation from the letter of the spec, flagged here rather than silently substituted. The resulting section reads and functions correctly at both widths per the screenshots and the DOM measurements.
- I did not attempt to move the header's own date stamp on mobile to avoid duplicating the new as-of line; the spec explicitly allowed leaving the header alone in that case and asked only for the reported measurement, which is above.

## Honest notes on the screenshots

- The three weakest things visible: the description/disclaimer/as-of block now appearing on the issue permalink page (not just the front page) is the biggest judgment call in this build — it looks fine, but it wasn't explicitly asked for and duplicates content a reader has often already seen if they arrived from the front page first. Second, the market cards' "older figure" and "product line, not the whole company" tags are both small italic text next to the metric line, and at the smallest phone width they sit close enough together (e.g. Netskope's card) that a reader skimming fast could miss which tag applies to which figure if a domain ever had a vendor carrying both tags at once (none currently do, but nothing structurally prevents it). Third, the "show all N" overflow link only exists for domains with more than six qualifying vendors, and none currently trigger it, so that code path has never been visually verified against a real overflowing domain.

## Preview

Branch `mon/wave1` pushed to `origin/mon/wave1`. Vercel preview at `https://security-market-pulse-git-mon-wave1-pikeholdings.vercel.app` returns HTTP 200, and the served HTML contains both `id="market"` and `id="follow"`. Not merged into `preview`, and `main` was never touched.
