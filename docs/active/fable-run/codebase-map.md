# Security Market Pulse — codebase map

Read-only survey of `web/`. React 19 + TypeScript + Vite, server-rendered at build time
(`renderToString`) to static HTML, no client router. Paths are relative to
`/Users/jessepike/code/projects/sec-market/web/` unless given in full.

## 1. Routing and rendering
No router library. `src/data/routes.ts` builds `routes: RouteEntry[]` — `/`, `/issues/`,
`/issues/<id>/` per issue — derived from `src/data/issues/index.ts` so it can't drift from
real issues. `matchRoute(path)` normalizes the path (`normalizePath`, always trailing-slash)
and falls back to `/` for anything unrecognized. `src/App.tsx`'s `RouteContent` switches on
`matchRoute(path).kind`: `archive` → `IssueArchive`, `issue` → `IssuePage`, else → `FrontPage`.
`path` comes from `src/main.tsx` (reads `window.location.pathname`, `hydrateRoot`s if `#root`
has server markup else `createRoot`s) or from `src/entry-server.tsx`'s `render(path)`, called
once per route by `scripts/prerender.ts` after `vite build` + `vite build --ssr`. Prerender
splices each route's markup into `dist/index.html`'s `<div id="root"></div>` placeholder,
rewrites `<title>`/canonical/description/OG/Twitter per route (front page's hand-authored head
is untouched — `rewriteHead` skips it), and writes `dist/<path>/index.html`, running a
"must-see" gate before writing (§6).
Component tree, top to bottom. **`/` (FrontPage)**, wrapped in `VendorLensProvider`:
`SkipLink`, `ProvenanceRail`, `Header` (shell, outside FrontPage) → `IssueHero` (`#overview`)
→ `IssueLanes` (`#formation`, `#absorption`, `#prints-this-week`, `#capital`) → `WeThink`
(`#we-think`) → `JudgmentBoard` (`#read`, `leadContent` = `ThesisRunningScore` + `Hero.tsx`'s
`HeroContent` injected atop the same section) → `DomainBoard` default surface (`#landscape`)
→ `PlatformPressure` (`#platforms`) → `Hypotheses` (`#hypotheses`) → `VendorLens`
(`#vendor-lens-slot`) → `PrintGrid` (`#prints`) → six `<details>` depth sections in order:
`WhatMoved` (`#moved-depth`→`#moved`), `DomainBoard surface="tempo"` + `ActivityBoard`
(`#research-depth`→`#domains`,`#activity`), `MarketLayersChart` (`#layers`), `WatchList`
(`#watch`), `HowThisWorks` (`#method`), `EvidenceLibrary` (`#research`) → `MethodologyNote` →
`NextEdition` (`#next`) → `EvidenceDrawer` (shell, mounted once).
**`/issues/<id>/` (IssuePage)**, no provider: shell → `IssueHero` (`#overview`) → `IssueLanes`
(the four lanes) → `WeThink` (`#we-think`) → a `<section class="issue-permalink-links">`
linking `/issues/` and `/` → `EvidenceDrawer`. **`/issues/` (archive)**: shell +
`IssueArchive` only — `<h1>Issues</h1>` and a list of every issue (id, week-ending, `read`
line, sign-off status, permalink).
**What `/` has that the permalink doesn't**: everything from `JudgmentBoard` (`#read`) onward
— the standing thesis block, `DomainBoard` (landscape + tempo), `PlatformPressure`,
`Hypotheses`, `VendorLens`, `PrintGrid`, all six depth `<details>`, `MethodologyNote`,
`NextEdition`. The permalink is only hero/lanes/`weThink` plus two nav links, and never mounts
`VendorLensProvider` — `IssueLanes` renders unfiltered via `useVendorLens()`'s inactive fallback.

## 2. Page sections on `/`, in order
| Heading | Component | Data source | Anchor | `<details>`? | Client-opened? |
|---|---|---|---|---|---|
| issue read (h1) | `IssueHero.tsx` | `data/issues/2026-w36.ts` | `overview` | No | — |
| Formation/Absorption/Prints/Capital | `IssueLanes.tsx` | issue data | 4 lane ids | No | — |
| "What we now think" | `WeThink.tsx` | issue data | `we-think` | No | — |
| thesis score + market-call + "The read" | `ThesisRunningScore.tsx`, `Hero.tsx`, `JudgmentBoard.tsx` | `issueHelpers.ts`, `market.ts` | `read` | No | — |
| landscape | `DomainBoard.tsx` (Landscape) | `domains.ts` | `landscape` | No | — |
| platform pressure | `PlatformPressure.tsx` | `platformPressure.ts` | `platforms` | No | — |
| tracked hypotheses | `Hypotheses.tsx` | `hypotheses.ts` | `hypotheses` | No | — |
| vendor lens control | `VendorLens.tsx` | URL `?vendors=` | `vendor-lens-slot` | No | — |
| "This period" scorecard | `PrintGrid.tsx` | `prints.ts` | `prints` + 8 group ids | 8, one per `printGroups` entry | **Yes, all 8** |
| "What moved" | `WhatMoved.tsx` | `whatMoved.ts` | `moved-depth`→`moved` | Yes | No |
| tempo + M&A activity | `DomainBoard.tsx` (Tempo) + `ActivityBoard.tsx` | `edition.ts`, `activity.ts` | `research-depth`→`domains`,`activity` | Yes, plus 24 activity-row `<details>` + 2 more/background wrappers | No |
| "Market layers" | `MarketLayersChart.tsx` | `derivePanel.ts`, `panelRaw.ts` | `layers` | Yes | No |
| "Watch next" | `WatchList.tsx` | `watch.ts` | `watch` | Yes | No |
| "How this is built" | `HowThisWorks.tsx` | `method.ts`, `meta.ts` | `method` | Yes | No |
| evidence library | `EvidenceLibrary.tsx` | `evidence.ts` | `research` | Yes | No |
| methodology footer | `MethodologyNote.tsx` | `meta.ts` | — | No | — |
| "How a posture is set" / corrections | `NextEdition.tsx` | `method.ts`, `meta.ts` | `next` | No | — |

**41/0/8 reconciled**: 6 `App.tsx` top-level depth sections + 8 `PrintGrid.tsx` print-group
`<details>` (one per `printGroups` entry, `data/prints.ts` 4-13) + 1 `MarketLayersChart.tsx`
"View data table" details + 26 inside `ActivityBoard.tsx` (24 rows from `data/activity.ts`'s
24-item array, each its own `<details>`, plus "More"/"Background" wrapper details) = 41. None
has a JSX `open` prop → none open in served HTML. Exactly the 8 print groups are force-opened,
by `PrintGrid.tsx` lines 62-72: a `useEffect` sets `details.open = mq.matches` for
`matchMedia('(min-width: 769px)')`, deliberately a post-mount DOM mutation rather than React
state so server/first-paint markup never disagrees with hydration. `Header.tsx` line 30 also
force-opens whichever `<details>` ancestor contains a hash-nav target, but that's dynamic, not
a fixed count.
**"Refresh is manual" / "Not a weekly news cycle"**: `src/components/HowThisWorks.tsx`, lines
23-24: "Refresh is manual: earnings clusters, material closes or raises, and Watch-next
falsifiers. Not a weekly news cycle."

## 3. Data model
Types in `src/data/types.ts`.
**Weekly issue** (`Issue`, lines 270-289; example `src/data/issues/2026-w36.ts`):
`id, weekEnding, windowStart, published: string|null, status: 'draft'|'published', read
(≤140 chars, the h1), sections: {lane, intro?, items: IssueItem[]}[]` (exactly 4, Lane
order), `weThink: {summary, postureDeltas: PostureDelta[], thesis: ThesisScore|null,
noCalls, signedBy: string|null, signedOn: string|null}, proposed: MachineProposal|null,
sources: {readable, unreadable}`. `PostureDelta` (244-251): `{domainId, from: Posture, to:
Posture, basis, confidence, evidenceIds}`. `ThesisScore` (253-259): `{thesis:'episode-002',
verdict:'holds'|'strengthens'|'weakens'|'no-call', basis, confidence, evidenceIds}`. Example:
`verdict:'holds'`, `confidence:'medium'`.
**Market call** (`MarketCall`, `data/market.ts` 10-20): `headline, subhead, whatChanged:
string[], actions:{doItems,avoidItems}, meaning, confidenceNote, noCallBoundaries: string[],
changeTriggers: string[], evidenceIds`. Example headline: "Infrastructure is running ahead.
Security is splitting, not booming."
**Editions** (`data/edition.ts`): `EditionRecord` (types.ts 148-157) — `{id, date,
dateDisplay, summary, surfaces: EditionSurfaceChange[], postures: PostureSnapshot[], notes}`,
append-only array (`editions`, 3 entries: 2026-08-16/17, 2026-08-28). `currentEdition`
derives from the last two entries; a build-time loop (165-190) throws if the snapshot
disagrees with live `securityDomains`.
**Domain postures** (`SecurityDomain`, types.ts 111-129; `data/domains.ts`, 6 domains):
`{id, name, coverage: CoverageResult, posture: Posture, tag: TempoTag, asOf, horizon:
DecisionHorizon, momentum, evidenceStrength: ConfidenceLevel, print, why, summary,
watchItems, supportingEvidenceIds, counterEvidenceIds}`. Example (`network-sase`):
`posture:'PREPARE'`, `horizon:'This quarter'`.
**Evidence records** (`EvidenceRecord`, types.ts 89-109; ~90 in `data/evidence.ts`):
`{id, title, organization, publicationDate, economicPeriod, canonicalUrl, excerpt,
sourceClass: SourceClass, interpretation, limitations, conflictingEvidenceIds, artifactLabel,
tags, sourceAttributions?, retrievedAt?, retrieval?: {finalUrl, sha256, fetchedAt,
locator?}}`. `sourceClass` ∈ `FILING|IR|TRANSCRIPT|OFFICIAL|INDEPENDENT|OWN_ANALYSIS|
VENDOR-SURVEY|VENDOR-RESEARCH`. Example: `A1b`, NVIDIA FY27 Q1 filing, SEC EDGAR URL.
**`meta.ts`**: `EPISODE_ID`, `EPISODE_VERSION`, `RESEARCH_FREEZE`, `LAST_UPDATED_DISPLAY`/
`_ISO` (site stamp), `JUDGED_AS_OF_ISO`, `WEEK_MOVES_ENDING_ISO`, `PRODUCT_TITLE`,
`SITE_URL`, `AUTHOR_NAME`, `CONTACT_EMAIL`. A comment on `LAST_UPDATED_DISPLAY` notes these
four dates used to be one constant, split apart so shipping doesn't silently re-date
judgments nobody revisited.
**`thesisRunningScore`** (`issueHelpers.ts` 62-91): filters published issues with a
non-null thesis, sorts by `published`, excludes `verdict==='no-call'` from both numerator
and denominator, counts `holds`/`strengthens` as a hold. Renders via `ThesisRunningScore.tsx`
as one line, injected as `leadContent` atop `JudgmentBoard`'s `#read`.
**Evidence id resolution**: every surface carries `evidenceIds` (or a `Provenance` wrapper)
resolved via `evidenceById` (`Record<string,EvidenceRecord>` in `evidence.ts`). `EvidenceLink`
takes ids and calls `openEvidence(idList)` from `EvidenceContext` on click.

## 4. Evidence UI
`EvidenceLink` (`components/EvidenceLink.tsx`) is a `<button class="evidence-link">` with a
`FileSearch` icon and a computed label (`evidenceLabels.ts`'s `evidenceSourceLabel`); click
calls `openEvidence(ids)`. `EvidenceDrawer` (`components/EvidenceDrawer.tsx`) is a **modal
dialog** (`role="dialog" aria-modal="true"`, focus-trapped, closes on Escape/backdrop,
restores focus), styled as an overlay panel (`.evidence-drawer`/`.evidence-drawer-backdrop`),
not a navigation. Per record (lines 96-193) it shows: title, organization, a `<dl>` of
publication date / economic period / source class / "packet label"; `sourceAttributions`
list when present; a **real `<a href={record.canonicalUrl} target="_blank"
rel="noopener noreferrer">`** labelled "Canonical source" (or, if `canonicalUrl` is empty, a
note that none is available — used for the internal `LAG-NO-CALL` record); excerpt as
blockquote; interpretation; limitations; and, if `conflictingEvidenceIds` exist, buttons
calling `openConflictingEvidence(id)` (pushes history for "Back").

## 5. Styling
One file: `src/index.css` (2,951 lines), imported once from `src/main.tsx` (SSR entry does
not import it, keeping SSR a pure markup producer). `:root` tokens (lines 1-27):
```
--font-sans: 'IBM Plex Sans', system-ui, sans-serif
--font-display: 'Archivo', system-ui, sans-serif
--font-mono: 'IBM Plex Mono', ui-monospace, monospace
--color-bg: #e9ecf0          --color-surface: #ffffff
--color-border: #d3d8df      --color-border-strong: #12161c
--color-text: #3a424e        --color-text-muted: #57606e
--color-heading: #12161c     --color-accent: #0b6b5e
--color-accent-soft: #ecfdf5 --color-alert: #8e2f5e
--color-alert-soft: #fce7f3  --color-success: #0b6b5e
--color-warning: #6b5c28     --color-context: #1b2430
--shadow-sm: none            --shadow-md: 0 8px 24px rgba(18,22,28,.16)
--radius: 0                  --radius-sm: 0
--header-height: 56px        --content-max: 1280px
--prose-max: 68ch
```
A few dark-panel-only colors are hard-coded, not tokenized: `#e7ebf0` (brand text on dark),
`#8b97a6` (muted-on-dark), `#5fd4c0`/`#e8a0c4`/`#f3d48a` (up/down/hold accents on dark). Fonts
are **remote** (Google Fonts), not self-hosted: `index.html` lines 49-53 preconnect to
`fonts.googleapis.com`/`fonts.gstatic.com` and load Archivo, IBM Plex Mono, IBM Plex Sans via
a `css2` stylesheet link, `display=swap`; no `@font-face`/woff in the repo. Dark panels: top
provenance bar `.rail` (line 1900, `background: var(--color-heading)`); thesis/market-call
block is not the whole `#read` section — it's `.context-band` (327-332, nested in
`Hero.tsx`'s `HeroBody`, `background: var(--color-context)`), holding the three context stats
and market-call subhead; "How a posture is set" is `NextEdition.tsx`'s `.method-band` (line
2434, `background: var(--color-heading)`). Lane cards: `.issue-lane__item` (line 2698) —
`background: var(--color-surface); border: 1px solid var(--color-border); padding: .85rem
1rem`, inside `.issue-lane__list` (`display:grid; gap:.85rem`), one per `IssueItem`.

## 6. Build pipeline
```
"build": "verify:edition && verify:panel && verify:integrity && verify:issue && tsc -b && \
          build:client && build:server && prerender && seo && build:feed && verify:dist"
"test":  "lint && test:data && build && test:e2e"
```
- **`prerender.ts`** — §1. Must-see gate (57-98): per route kind, fixed section ids (front:
  `overview, formation, absorption, prints-this-week, capital, we-think, read, landscape,
  platforms, hypotheses, prints`; archive: `issues`; issue: the six issue ids) must appear
  with no `<details>` ancestor — counts open/close `<details>` tags before each marker, fails
  if unbalanced.
- **`generate-seo.ts`** — OG staleness gate (96-138): fails if `assets-src/og.svg`'s baked
  text or `index.html`'s `og:image:alt`/`twitter:image:alt` no longer contain
  `marketCall.headline` or every `contextStats[].value`. Injects one JSON-LD `<script>` per
  route. Writes `dist/sitemap.xml`.
- **`generate-feed.ts`** — writes `feed.xml`, `issues/<id>.json`, `issues/index.json`,
  `issues/lock.json`; injects RSS `<link rel="alternate">` into every head (see §9).
- **`verify-integrity.ts`** — every domain print resolves to evidence; every judged
  `weekMoves` row has evidence or `basisHref`; no duplicate/unresolved ids (unreferenced
  records logged, fail only past `MAX_UNREFERENCED=5`); a print's `secondaryGroup` must be
  real/different; checks 8/8b server-render `PrintGrid`, asserting every borrowed print shows
  "also counted under X" and each print-group header's "N covered" equals the actual rendered
  `print-card` count — guarding against a header reading "0 prints" over visible cards.
- **`verify-issue.ts`** — 14 numbered checks: id format/uniqueness/order/Sunday-weekEnding;
  no overlapping windows; exactly 4 sections in Lane order; every cited evidence id resolves,
  item dates inside window unless `background`; publish/signature consistency; at most one
  draft (must be newest); production guard (newest published on `main`); (8) append-only lock
  manifest (§8); published `PostureDelta`s agree with live domains/editions; (10) **render
  check** — server-renders `IssueHero+IssueLanes+WeThink` for the newest issue, asserts
  draft-banner presence matches status, per-lane rendered item counts match data, exact
  signature-line text matches; (12) **numeric-token check** — every number in an item's
  headline/why (`extractNumericTokens`) must appear in at least one cited evidence excerpt;
  strict ISO-date validation everywhere; bounds (≤8 items/lane, read ≤140 chars, headline
  ≤110, why non-empty); every cited evidence record needs a `retrieval` receipt (64-hex
  sha256, valid `fetchedAt`, non-empty `finalUrl`).
- **`verify-dist.ts`** — post-build file checks: every route HTML exists; every issue JSON
  deep-equals source issue + full evidence bodies; `issues/index.json` newest-first and
  row-identical; `feed.xml` parses (hand-written XML tokenizer) with correct guid set and
  per-item pubDate; `sitemap.xml` lists every route; `issues/lock.json` equals source exactly;
  every non-front route's three description meta tags equal route-specific text and differ
  from the front page's.
- **`verify-edition.ts`** / **`verify-panel.ts`** — SHA-256 hash gates over
  `JSON.stringify(editions)` and a canonical derived-panel payload against a hard-coded
  expected hash; `--write` prints the new hash to paste in. **`shot.mjs`** — not read this
  pass; per `AGENTS.md`, the full-page screenshot tool (1440px/390px), run from `web/`.

## 7. Tests
**Playwright** (`tests/e2e/`; `smoke.spec.ts` desktop-only, `issue.spec.ts`/`lens.spec.ts`
run at 1440×900 and 390×844):
- `smoke.spec.ts` — h1 equals `latestIssue.read`; `#moved-depth > summary` text is exactly
  `"What moved: edition delta"`, `#moved-depth #moved` attached-but-hidden; `#landscape`
  contains `"Network / SASE"`; `.landscape .evidence-link:nth(2)` contains one of
  `Fortinet|Upwind|Orca|Aqua` and must **not** contain `"Alphabet"` (guards the Wiz/Alphabet
  close mislabeling a Cloud card's print); `#market-call-heading` visible with both headline
  lines; `#research-depth` content hidden until its summary is clicked, then
  `"Zenity raised $115M Series C"` becomes visible; evidence-drawer test opens Fortinet's
  link, asserts `role="dialog" name="Evidence"` shows a "Canonical source" link and
  "Limitations / confounds" heading, and **no** link matching `github.com/jessepike/sec-market`.
- `issue.spec.ts` — front h1 equals `latestIssue.read`; every id in
  `[overview,formation,absorption,prints-this-week,capital,we-think]` and
  `[read,landscape,platforms,hypotheses,prints]` visible; draft banner
  (`.issue-hero .issue-draft-banner`) visible iff draft status; `/issues/` h1 is `"Issues"`
  with every issue id in `.issue-archive__list`; permalink repeats h1/section checks;
  `/feed.xml` returns 200 XML; `/issues/<newest>.json` has non-empty `evidence`; permalink's
  "Thesis" link navigates to `/#read` (real navigation, not same-page).
- `lens.spec.ts` — vendor slugs derived from live data, not hard-coded (avoids a
  vacuously-passing test as the newest issue changes). `?vendors=a,b` → both filter-status
  lines read `"Showing N of M"` with correct N/M; the actual rendered headline set
  (`.issue-lane__headline`) and print-card name set (`.print-card h3`) equal expected
  filtered sets exactly, not just counts; unknown slug → `"Showing 0 of M"` + visible clear
  link, no error; empty `?vendors=` = no parameter; clear link restores empty query; removing
  a chip re-filters and updates the URL; at 390px `.vendor-lens__chips` has `overflow-x:auto`.
**Data tests** (node's `--test` runner): `issue-data.test.ts` — ISO-week round-trips;
`thesisRunningScore` excludes no-call, excludes drafts; `vendorSlug` normalization;
`parseVendorsParam`/`serializeVendorsParam` round-trip, empty = absent; `extractNumericTokens`
excludes name-glued digits (`M12`, `FY2027`, `1Password`) but keeps `$100M`/`26%`/`1,200`;
`issueEvidenceIds` dedupes across items/deltas/thesis. `landscape-data.test.ts` — every
`platformPressure`/`hypotheses` evidence id resolves; every tracked print has non-empty
evidence; `platformPressure.ts`'s source contains **no literal `%` or `$`** (figures must
live in `prints.ts`/`activity.ts`, never hand-typed into pressure-row prose); Cloud card's
tracked evidence includes `C13`, excludes `D5a`; every pressure group non-empty.
`dist-fixtures.test.ts`/`html-escape.test.ts` exist but weren't read past listing.
**Redesign implication**: moving a section is safe for the id-based visibility assertions as
long as ids and `<details>` nesting are preserved, but converting `issue-lane__item` cards to
rows breaks `lens.spec.ts`'s `.issue-lane__headline` selector; a new route needs a new
`RouteEntry` plus updates to `MUST_SEE_SECTION_IDS`, `verify-issue.ts`'s id lists, and
sitemap/SEO scripts — none auto-discover a new route kind.

## 8. The lock manifest
`src/data/issues/issues.lock.json`: flat `{"<issue-id>": "<sha256 of
JSON.stringify(issue)>"}`, one entry today. Written only by `verify-issue.ts --write`, which
validates the candidate issue on every check but its own, refuses to write if any existing
entry would change hash or disappear, and checks two independent append-only anchors — a
**git-parent anchor** (`git show <parent>:web/src/data/issues/issues.lock.json` for every
parent of `HEAD`, kept separate, never merged) and a **network anchor** (fetches live
`https://securitymarketpulse.com/issues/lock.json`, shape-validated) — failing the write, or
failing the build on a protected branch (`main`/`preview`), if any anchor entry would be
missing or changed. Neither anchor available fails the build only on a protected branch.
`generate-feed.ts` publishes a verbatim copy to `dist/issues/lock.json`; `verify-dist.ts`
check 11f requires exact equality. What breaks it: changing any field of an already-locked,
published issue — the hash is over the **whole serialized object**, not per-field.
Compatibility: a new optional field on `Issue`, or a brand-new issue, is fine as long as it
doesn't change any *already-locked* issue's `JSON.stringify` output (`undefined` is safe; a
field defaulted to a real value on old data is not). New JSON *outputs* elsewhere (e.g. a
future `dist/thesis.json`) are entirely unconstrained — this manifest only governs the
`issues.lock.json` map itself.

## 9. Machine outputs today
**`generate-seo.ts` JSON-LD**, one per route: Front (`Report`) — `{"@context","@type":
"Report","@id",url,mainEntityOfPage,name,headline,description,abstract,reportNumber,
inLanguage,isAccessibleForFree,datePublished,dateModified,image,author:{"@type":"Person",
"name"},publisher:{"@type":"Organization","name","url"}}`. Archive (`CollectionPage`) —
`{"@context","@type","@id",url,name,description,isPartOf:{"@type":"WebSite","name","url"},
inLanguage}`. Issue (`Article`) — `{"@context","@type","@id",url,mainEntityOfPage,headline,
name,description,inLanguage,isAccessibleForFree,datePublished?,dateModified?,author,
publisher,isPartOf}`. Also writes `dist/sitemap.xml` (front priority 1.0, else 0.7).
**`generate-feed.ts`** writes: `dist/feed.xml` (RSS 2.0, one `<item>` per published issue:
title/link/guid/pubDate/description); `dist/issues/<id>.json` (`{issue, evidence:
EvidenceRecord[]}` for every issue); `dist/issues/index.json` (`{id,weekEnding,published,
status,read,url}[]`, newest first); `dist/issues/lock.json` (verbatim copy, §8).
**Nothing in the HTML links to these JSON files** — confirmed by grep: no component or
`index.html` references `.json`, `issues/index.json`, or `feed.xml` as an href/src anywhere
in `src/`. The only outbound reference is the machine-only
`<link rel="alternate" type="application/rss+xml">` autodiscovery tag injected at build time;
no visible RSS/JSON link exists for a human reader.

## 10. Constraints and surprises
- **Hydration parity is load-bearing, enforced only by convention.** `VendorLensProvider`
  starts `null` and reads the URL in a post-mount effect; `PrintGrid`'s desktop-open state is
  a raw DOM mutation, not React state; `MarketLayersChart` dynamically `import()`s the
  recharts-heavy `ChartsPanel` rather than `React.lazy` (a code comment says `lazy()` throws
  a real hydration error — React #419 — against this app's synchronous `renderToString`
  prerender). New client-only affordances must follow the same pattern.
- **Vendor lens** (`?vendors=slug,slug`) filters `IssueLanes`+`PrintGrid` only, scoped to the
  front page (no provider on the permalink page), inactive on first render both sides, fully
  round-tripped via `history.replaceState`. An empty `?vendors=` is treated identically to no
  parameter.
- **Vercel Analytics** renders null until a post-mount effect (same hydration discipline);
  its `/_vercel/insights/script.js` 404s locally, and both e2e specs special-case that.
- **`vercel.json`** sets `trailingSlash: true` (must match `routes.ts`), security headers on
  every route (no CSP), one-year immutable cache on `/assets/(.*)`. `robots.txt` is a static
  file at `public/robots.txt` (`Allow: /` + `Sitemap:` line), untouched by the build. Fonts
  are third-party (Google Fonts, not self-hosted) — a typography redesign either keeps the
  existing preconnect/stylesheet pattern in `index.html` or deliberately switches to
  self-hosting.
- **`recharts` is the single largest bundle dependency** (`MarketLayersChart.tsx` 6-9),
  called out in-code as the reason it and `BuyerBudgetChart`/`ChartsPanel` are split into a
  dynamically-imported chunk rather than the initial bundle.
- **Two build gates constrain composition beyond ordinary review**: `prerender.ts`'s
  must-see section-id gate and `verify-issue.ts`'s render/bounds checks both hard-fail the
  build if a section is renamed, removed, or newly nested inside a `<details>`. Moving
  sections requires updating `MUST_SEE_SECTION_IDS`, the matching id lists in
  `verify-issue.ts`, and the Playwright specs together.
- **The 769px breakpoint is duplicated** between `PrintGrid.tsx`'s JS `matchMedia` call and a
  CSS breakpoint pair a code comment says must stay in agreement — drifting one desyncs which
  print groups render pre-opened.
