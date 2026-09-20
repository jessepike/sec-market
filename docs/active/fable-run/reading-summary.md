# Reading Summary — Security Market Pulse

Extracted 2026-09-19 from README.md, status.md, weekly-issue-spec.md, project-scorecard.md, durability-spec.md, routes.ts, generate-seo.ts, generate-feed.ts, decisions.md (D-60 onward), decision-impact-log.md, BACKLOG.md, and the site stack.

## A. Product Model: The Weekly Issue

A weekly issue is the unit of product. Each issue covers a calendar window (typically the week ending the previous Sunday) and carries four sourced lanes: **formation** (funding rounds), **absorption** (M&A), **prints-this-week** (vendor releases and financials), and **capital** (sector capital events). Every issue is drafted by an autonomous agent, reviewed by the owner, and published under the owner's signature.

**Sections per issue.** The hero carries an eyebrow naming the week and status, and an `h1` stating the read as one headline. Four lanes follow, each with a lane name as `h2`, optional intro text, and a list of items. Each item has a headline (under 110 chars, stating the fact), a why line (one sentence explaining why it matters), an ISO date, a list of evidence IDs, optional vendor slugs for filtering, and an optional background flag if the item predates the window. Below the lanes sits "What we now think" — a signed judgment carrying a summary, any posture deltas (from → to, basis, confidence, evidence), the standing thesis verdict against Episode 002 (holds / strengthens / weakens / no-call), confidence level, no-call boundaries, and the signature line `Signed by [AUTHOR_NAME] · [date]` (landing at /Users/jessepike/code/projects/sec-market/web/src/data/meta.ts).

**The standing thesis.** Episode 002's market call — "Infrastructure is running ahead. Security is splitting, not booming." — is the frozen research call that every issue scores against. The thesis carries a verdict (one of four: holds, strengthens, weakens, no-call) which is set by the owner's signature at publication. Each issue's verdict contributes to a running score shown in the thesis block as "Holds in 1 of 1 issues since 19 Sep 2026" (weekly-issue-spec.md §4, line 173).

**Signed means.** The owner reads the machine proposal (headlines, lanes, the machine-proposed thesis verdict), rewrites the summary and verdict and confidence in weThink (leaving postureDeltas empty unless a posture actually moved, which it hasn't yet), sets `proposed: null` to retire the machine proposal, sets `signedBy` to AUTHOR_NAME from meta.ts, and sets `signedOn` to today's ISO date. At that moment the issue moves from draft to published and is immutable (enforced by the append-only lock manifest). Quote: "A posture change is one human-signed transaction that edits the issue's `postureDeltas`, `domains.ts` and an appended `edition.ts` record together; posture-change language belongs in `postureDeltas` and nowhere else" (weekly-issue-spec.md §3, line 126).

## B. Current State — D-65 and D-66

**As of 2026-09-19.** Issue `2026-w36` (week ending 2026-09-06, window 2026-08-24 to 2026-09-06) was signed by Jesse Pike and promoted to production by D-66. `main` moved from `b423b70` to `aa04875` — fifty-four commits, the first promotion since 2026-08-28. The page now opens with the issue hero and Formation lane instead of the judgment layer. Production confirmed serving by render: 15,033 px at 1440, 17,760 px at 390, identical to preview at both widths. All four new endpoints return 200.

D-65 (2026-09-05) merged the entire weekly-issue improvement to `preview` for owner review: the data model, fifteen `verify:issue` checks, issue 2026-w36 as an unsigned draft with 23 items and a machine proposal, the reframed front page, archive and permalink routes, JSON copies, RSS feed, lock manifest, vendor lens, and the gather specs v0.2. Validation: three external review rounds, Playwright suite at both widths against the live branch deploy, no console errors.

D-66 recorded the signature and promotion. The owner "adopted the gather's proposal as written" — no posture deltas were accepted, thesis verdict is `holds` at medium confidence, and the signature line now reads "Signed by Jesse Pike · 19 Sep 2026". The running score lines "Holds in 1 of 1 issues since 19 Sep 2026".

**Still pending from D-65.** Promotion to main (done). Signing 2026-w36 (done). Arming the Tuesday schedule (not done — routine is disabled). Naming the pilot list for email (not done).

## C. Cadence: Why the Gather Job Is Not Running

The Tuesday gather routine (`trig_01VeQpLYzXjccqKeSFS1Xgo6` on the Claude Code cloud environment) is disabled and has never run on schedule. A one-off dry run on 2026-09-05 (`trig_01La16jZAq9WaQPHyqpUUcyG`) proved the mechanics (checkout, brief, files, all five gates, commit, push) but failed at every source fetch: "the cloud environment's egress proxy returns 403 on CONNECT to any host outside its allowlist (npm, GitHub, Anthropic), so Return on Security, SEC.gov, SecurityWeek, Cybersecurity Ventures and even example.com were unreachable. Zero evidence was gathered" (status.md, line 141).

**SEC-027 and SEC-028** are the weekly-issue model (building) and the Tuesday gather job (building). Both are being built autonomously under D-64, merged to preview, and await owner approval of promotion.

**SEC-039** (`SEC-MARKET-DURABLE-001` v0.1, durability-spec.md) proposes the Sunday-afternoon cadence and two runtimes. Primary: add the source hosts to the cloud allowlist at https://claude.ai/code/environments (www.returnonsecurity.com, cybersecurityventures.com, www.securityweek.com, www.sec.gov, efts.sec.gov, techcrunch.com, and eight specialist VC hosts from the catalog, plus all issuer investor-relations hosts). Fallback: `scripts/gather.sh` runs `claude -p --model claude-sonnet-5` from the laptop by hand, or as a launchd job on macmini registered through jobs-agent. Decision rule: "if the probe cannot be made to pass within one week of the allowlist change, the fallback becomes primary and the cloud routine is deleted" (durability-spec.md §3, line 58).

**For next week's issue to exist,** the owner must (1) choose runtime (allowlist first or straight to local runner), (2) authorize the durability spec build (brief change, probes, sign script, post-promote script), and (3) arm the schedule. Without these, no 2026-w37 issue will be drafted on 2026-09-09 (the Tuesday after). The first issue covers two weeks by design, so the first useful scheduled run is Tuesday 2026-09-15 for 2026-w37.

## D. The Outcome Scorecard

The project scorecard (`SEC-MARKET-SCORE-001` v0.2, project-scorecard.md) measures outcomes by evidence state, not by numeric score. It keeps two instruments deliberately separate.

**The exposure denominator.** "How many qualified people had a genuine opportunity to use this intelligence, and who were they?" (project-scorecard.md §2, line 78). Currently **1** — the site has been shown to one person. An outcome cannot be rated better than `not_assessed` while the denominator is one. Qualified exposure is a named pilot set, drawn from ePlus account teams and CSPs and named clients, recorded by role, segment and pseudonymous identifier (never by name — the mapping lives in the ePlus operating cockpit per D-58). Security leadership peers outside the engagement are excluded because their decisions are not observable.

**It refuses a composite number.** v0.1 was sent for independent review and "largely failed it" (project-scorecard.md §1, line 8). v0.2 replaces it with per-outcome states (`not_assessed`, `no_observed_effect`, `anecdotal`, `independently_evidenced`, `repeated`) so that "the single overall number hid the thing that mattered" — each outcome carries evidence state separately. The two questions D-55 left open — who scores the outcome review, and which named people count as qualified exposure — remain owner-owned (D-58).

**The decision-impact log.** Located at `/Users/jessepike/code/projects/sec-market/docs/active/decision-impact-log.md`, line 40: "(None yet — first use wins the proof.)" It has a template to capture who looked at what, which evidence they clicked, what decision or conversation changed, and two load-bearing questions: "Did they already know it?" (U2 incremental value) and "Were options still open?" (U3 lead time). The goal is "Two logged uses in two weeks, against a pilot set named in advance" (decision-impact-log.md, line 8).

## E. Distribution and Newsletter Rules

**The pilot list is unnamed.** D-58 settled that qualified exposure is drawn from two beneficiary groups, named in advance. The actual names remain owner-owned. Until they are named the denominator stays at one and the impact log stays empty.

**The four-held-issues condition.** "Analytics on, issue #1 emailed to the pilot list by hand, RSS feed and per-issue permalink and Open Graph image by issue #2, email provider and public list only after four held issues" (BACKLOG.md, SEC-029, line 122). D-64 records "the entire improvement intent completed into preview for me to review… public email not authorized before the 2026-10-08 review" (decisions.md D-64, line 695).

**The 2026-10-08 review.** SEC-029 lists it as the gate for deciding whether to use an email provider. SEC-039 §10 (durability-spec.md, line 122) records four measures reviewed on that date: freshness (≤1 day since newest weekEnding), run receipt rate (4 of 4 Sundays with a PR by 22:00 UTC), owner minutes per week (≤15), and alerts fired that were true. At that review the owner will also decide (1) Sunday cadence, (2) allowlist or local runner, (3) the shape of the signing file, and (4) whether to authorize the full build.

## F. Machine Surface That Already Exists

**Routes in routes.ts.** Four prerendered routes with trailing-slash normalization:
- `/` — front page, kind `front`, carries the newest issue
- `/issues/` — archive, kind `archive`, lists every issue newest first
- `/issues/<id>/` — permalink, kind `issue`, that single issue (one route per published or draft issue; 2026-w36 generates `/issues/2026-w36/`)

(routes.ts line 24: `issuesList.map((issue) => ({ path: `/issues/${issue.id}/`, kind: 'issue' as const, issueId: issue.id }))`). Each prerendered to HTML by scripts/prerender.ts with per-route `<title>`, canonical, og:description, twitter:description injected.

**JSON-LD per route (generate-seo.ts):** Schema.org structured data emitted by `structuredDataFor()` (line 142):
- Front page: `Report` with reportNumber `${EPISODE_ID} v${EPISODE_VERSION}`, headline `marketCall.headline`, datePublished/dateModified = `LAST_UPDATED_ISO`
- Archive: `CollectionPage` with isPartOf WebSite
- Issue permalink: `Article` with headline = `issue.read`, datePublished = `issue.published` (when not draft), author Person, dateModified = published date

**Feed output (generate-feed.ts).** Writes four machine artifacts:
- `/feed.xml` — RSS 2.0 with one `<item>` per *published* issue (empty feed until first signature), `<pubDate>` in RFC 822
- `/issues/<id>.json` — `{ issue, evidence }` object for every issue; evidence array holds every record the issue cites by ID, in the writer's own order (identity-checked by verify:dist check G3, line 369)
- `/issues/index.json` — archive entries (id, weekEnding, published, status, read, url) newest first
- `/issues/lock.json` — public copy of the append-only lock manifest (identity-checked verbatim by verify:dist)

Feed autodiscovery `<link rel="alternate" type="application/rss+xml" … href="/feed.xml">` added to every route's `</head>`.

**Sitemap at /sitemap.xml** — one `<url>` per route with lastmod (issue.published or LAST_UPDATED_ISO), changefreq weekly, priority 1.0 for front page, 0.7 for others.

**Static files in web/public/:**
- `robots.txt` — static, never regenerated
- `og.png` — hand-rendered from `assets-src/og.svg`, published alongside the hand-maintained image
- `favicon.svg` — static

**What does NOT exist:** Per-issue Open Graph images (SEC-032, flagged but not authorized). Archive rows as an HTML table (SEC-035, not yet authorized). In-page vendor picker for the lens (SEC-036, not authorized). Markdown variants of anything (nothing in the build outputs markdown). `llms.txt` (not mentioned in any spec or script).

## G. Site Stack

**Framework & build.** React 19.2.8 with TypeScript 6.0, Vite 8.2.0 for dev server and build. No router library — routes are implemented as a plain function switch in App.tsx (weekly-issue-spec.md §2, line 41). Recharts 3.10.1 for charts. Lucide React 1.31.0 for icons. Vercel Analytics tag (no external dashboard, just the SDK).

**Prerendering strategy.** `src/entry-server.tsx` exports `render(path)` function; `scripts/prerender.ts` iterates the route table and writes each to `dist/` as an HTML file. Per-route SEO meta tags (`<title>`, canonical, descriptions) and JSON-LD injected by `scripts/generate-seo.ts`. No server-side rendering to a live service; prerendered HTML deployed as static files to Vercel.

**The five verify gates** (in build order: lint && verify:edition && verify:panel && verify:integrity && verify:issue && tsc -b && build:client && build:server && prerender && seo && build:feed && verify:dist).
1. `lint` — oxlint 1.75.0 over the codebase (no ESLint config shipped, using oxlint defaults)
2. `verify:edition` — checks edition data array is append-only, hashes against a frozen snapshot (verify-edition.ts)
3. `verify:panel` — domain postures and panel snapshot match; quarterly panel exists; dates are valid (verify-panel.ts)
4. `verify:integrity` — five checks: provenance & evidence match, uncertainty & alternatives expressed, freshness declared, legibility (no collapsed must-see sections), boundary safety (no confidential info, no forced calls). Each check proven by perturbation before acceptance (verify-integrity.ts).
5. `verify:issue` — twelve checks on the issues array: ordering, uniqueness, windows don't overlap, evidence resolves, published issues complete, at most one draft, production guard (on main: newest must be published), append-only lock manifest against git parents + live production manifest, postures match domains.ts, render check (item counts match), dist files exist & identity-match source, numeric tokens appear in cited evidence. Checks 4 and 12 share an `issueEvidenceIds()` helper to prevent drift (verify-issue.ts, line 419-422).
6. `verify:dist` — files exist (every route's HTML + JSON + feed + lock), identity match (each issue's JSON deep-equals source, not just presence; feed parses by hand-written well-formedness tokenizer; sitemap lists all routes; lock.json equals source exactly; per-route descriptions differ from front page)

**What `npm test` runs** (package.json line 26):
```
npm run lint && npm run test:data && npm run build && npm run test:e2e
```
- Lint with oxlint
- Data tests: `tests/landscape-data.test.ts`, `tests/issue-data.test.ts`, `tests/dist-fixtures.test.ts`, `tests/html-escape.test.ts` (Node test runner via tsx)
- Full build (all six gates above)
- E2e: Playwright suite at two widths (1440×900 and 390×844 as separate projects; issues.spec.ts, lens.spec.ts, checks visibility, console errors, feed/JSON parse, archive/permalink routes)

## H. Backlog SEC-027 Through SEC-042

**SEC-027 — Weekly issue is the product.** Build the weekly-issue model (four lanes, signed judgment, archive, permalinks, lock manifest, vendor lens). Plan: weekly-issue-plan.md. Spec: weekly-issue-spec.md. Status (2026-09-05): built and merged to preview (D-65); 2026-w36 on preview unsigned; issue 2026-w37 awaits next week's gather and signature.

**SEC-028 — Tuesday gather job.** Scheduled agent gathers from catalogued sources every Tuesday, drafts as a PR against preview, never publishes. Plan: weekly-issue-plan.md. Spec: gather-job-spec.md. Status: routine disabled; dry run proved mechanics, failed on network (cloud proxy blocks sources). Awaits owner decision on runtime (allowlist vs. local) and schedule arming.

**SEC-029 — Distribution.** Analytics (done), issue #1 by hand to pilot (not done — list unnamed), RSS feed and JSON (done), email provider after four held issues (decision 2026-10-08). Status: feed + JSON on preview/production; pilot list remains owner-owned; provider choice pending.

**SEC-030 — ePlus downstream digest interface.** Pulse ships `/issues/<id>.json`; ePlus channel builds its own digest inside its own repo. No ePlus surface on this domain. Status: JSON copy working on preview/production; handoffs sent to eplus-security-advisor and eplus-ops.

**SEC-031 — Vendor lens.** Filter issue lanes and scorecard by vendor slugs via URL parameter `?vendors=a,b,c`. Status: built and merged to preview; filters after hydration (prerendered HTML never filtered); shows "Showing N of M"; clears by link; scrolls as one row on 390.

**SEC-032 — Per-issue social preview images.** Each `/issues/<id>/` page would carry its own OG image. Status: flagged 2026-09-04; not authorized (no browser in build environment for rasterization).

**SEC-033 — Period-label patterns in check 12.** The numeric-token gate flags "Q2 FY2027" as a claim. Decide: allow-list period labels or keep rule and document it. Status: flagged 2026-09-04; 2026-w36 worked around it; decision pending.

**SEC-034 — Email provider for pilot list.** Choose provider that takes `/issues/<id>.json`, keeps list private, no tracking pixels. Status: flagged 2026-09-04; decision at 2026-10-08 review.

**SEC-035 — Archive rows as a table.** IssueArchive.tsx is flex layout; a `<table>` with column headers would read better in screen readers. Status: flagged 2026-09-04; small and reversible; do after issue #2 exists.

**SEC-036 — Vendor picker for the lens.** In-page control to add vendors to the lens without editing URL. Status: flagged 2026-09-04; net-new surface; not authorized.

**SEC-037 — Local e2e and analytics script path.** Vite preview returns SPA index for `/_vercel/insights/script.js` instead of 404, breaks zero-errors assertion. Status: flagged 2026-09-05; small; do with next test change.

**SEC-038 — Make verify-issue.ts unit-testable.** Export validators as functions; prove all checks by fixture tests like verify-dist does. Status: flagged 2026-09-05; not authorized.

**SEC-039 — Durable weekly pipeline.** Sunday cadence, runtime allowlist-first (cloud) or local fallback, run receipts with alerts, signing pass (15 min), post-promote check. Spec: durability-spec.md. Status: proposed 2026-09-07; owner decisions in spec §12; not authorized.

**SEC-040 — A frontier lane.** Fifth lane for AI-frontier security. Spec: durability-spec.md §11. Status: idea 2026-09-07; needs owner scope decision and data-model change; not authorized.

**SEC-041 — Triage category-compression intake.** Vendor claims on Cloudflare, Fortinet, SentinelOne, Varonis, Rubrik and a structural lens landed 2026-09-09. Two owner decisions: enter vendor claims in next gather packet, or become a market read for owner signature. Status: intake only (d2cae33 on local, not yet pushed).

**SEC-042 — Weekly destination and monetization run.** Thesis that visibly develops week over week, first-screen redesign against a rubric, machine-readable surface for AI agents as readers. Brief: fable-run-brief.md (SEC-MARKET-FABLE-001 v0.1), owner-approved as brief; gates inside it still owner-held. Status: brief approved 2026-09-19; gates (promotion, paywall, signed thesis, intent amendment, robots policy) still pending.

## I. Conflicts & Constraints

**On a paywall or subscribe path:**
- Project scorecard: "The binding constraint is not quality. It is that almost nobody has seen it" (project-scorecard.md §4, line 196). No amount of polish makes a paywall work; the exposure denominator must move first.
- D-62 and D-63: Weekly issue is the product; ePlus consumes downstream. Confidential ePlus overlay cannot sit on this public domain.
- SEC-034 (email provider) held to 2026-10-08; four-held-issues condition holds public email.

**On investor-facing content:**
- Intent v1.2: "Must remain true: A machine may retrieve, extract, compare and propose, and only a named person signs a judgment or publishes an issue" (decisions.md D-63, line 673).
- D-62: "declining an eplus.securitymarketpulse.com subdomain. The tailoring ePlus needs is confidential and cannot sit on this domain" (decisions.md, line 651).
- SEC-030: "No ePlus surface on this domain; no account data flows back" (BACKLOG.md, line 134).

**On AI-crawler policy:**
- No `llms.txt` built or deployed.
- No statement on the project's stance toward AI crawler access.
- Robots.txt is static (web/public/robots.txt, 77 bytes) — content unknown without reading; check live site.
