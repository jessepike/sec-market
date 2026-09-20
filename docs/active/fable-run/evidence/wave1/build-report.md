# T6-2 build report — front-page redesign, step A, wave 1

Branch `mon/wave1`, built from a worktree at `/Users/jessepike/code/projects/sec-market-wt/wave1`, off `preview`. Not merged anywhere. Last commit: `ca2e529 feat(web): add machine-surface links per agent-surface-spec section 6`.

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
