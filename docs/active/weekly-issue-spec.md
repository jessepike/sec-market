# Weekly issue specification

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-ISSUE-001` |
| **Version** | v0.1 |
| **Status** | specification, being built under D-64 |
| **Date** | 2026-09-03 |
| **Governs** | SEC-027 (issue model, page, gates), SEC-029 (feed, permalinks, JSON copy), SEC-030 (JSON interface), SEC-031 (vendor lens) |
| **Parent** | [weekly-issue-plan.md](weekly-issue-plan.md) |
| **Intent** | `SEC-MARKET-001` v1.2 |

## 1. What changes for a reader

The page opens with this week's issue: a dated one-line read, four lanes of sourced items, and a
signed "what we now think". Under it sits the standing reference: the Episode 002 thesis with its
running score, the domain postures led by their trigger sentence, the tracked hypotheses, the vendor
scorecard, and the evidence library. Every issue has a permalink and the archive lists them all. A
feed and a machine-readable copy of each issue ship with the page. A reader can filter the issue and
the scorecard to the vendors they hold and share that view by URL.

Nothing is deleted. Sections that leave the front page move into the depth disclosures, and the
change is proven by render at 1440 and 390 before and after.

## 2. Architecture decisions

The site stays a static, router-free React build prerendered to HTML. Three routes are added and
prerendered the same way the one route is today.

| Route | File emitted | Content |
|---|---|---|
| `/` | `dist/index.html` | latest issue, then the standing reference, then depth |
| `/issues/` | `dist/issues/index.html` | archive: every issue newest first, one row each |
| `/issues/<id>/` | `dist/issues/<id>/index.html` | that issue alone, with a link to the standing reference |
| `/issues/<id>.json` | `dist/issues/<id>.json` | machine-readable copy: the issue plus every evidence record it cites |
| `/issues/index.json` | `dist/issues/index.json` | list of issue ids, week endings, reads, permalinks |
| `/feed.xml` | `dist/feed.xml` | RSS 2.0, one item per published issue |

Mechanics:

- `src/entry-server.tsx` exports `render(path)`; `src/App.tsx` switches on `path` between the three
  views with a plain function, no router library. `src/main.tsx` passes `location.pathname`.
- `scripts/prerender.ts` iterates a route table derived from the issues array, renders each, writes
  each file from the `dist/index.html` template, and injects per-route `<title>`, canonical,
  description and Open Graph tags. The must-see gate runs per route with a per-route id list.
- `scripts/generate-seo.ts` writes one sitemap `<url>` per route and JSON-LD per file.
- `scripts/generate-feed.ts` and the JSON copies are emitted from the same route table.
- Cross-page links are ordinary anchors. In-page navigation keeps the hash-scroll behaviour.
- Vercel serves the emitted files as they are. No rewrites needed.
- Open Graph image: issues share the site image for now; per-issue images are backlogged because the
  build environment has no browser to rasterise them.

## 3. Data model

New file `src/data/issues/index.ts` exporting `issues: Issue[]`, append-only, newest last. One file
per issue at `src/data/issues/<id>.ts`. Types added to `src/data/types.ts`:

```ts
export type Lane = 'formation' | 'absorption' | 'prints' | 'capital'
export type IssueStatus = 'draft' | 'published'

export interface IssueItem {
  id: string                 // `${issueId}-${lane}-${n}`
  lane: Lane
  headline: string           // ≤ 110 chars, states the fact
  why: string                // one sentence, why it matters, may be empty on a draft
  date: string               // ISO date of the event or filing
  evidenceIds: [string, ...string[]]
  vendors?: string[]         // vendor slugs, for the lens
  domainId?: SecurityDomain['id']
  background?: true          // dated before the window; must say so on the page
}

export interface PostureDelta {
  domainId: SecurityDomain['id']
  from: Posture
  to: Posture
  basis: string
  evidenceIds: [string, ...string[]]
}

export interface ThesisScore {
  thesis: 'episode-002'
  verdict: 'holds' | 'strengthens' | 'weakens' | 'no-call'
  basis: string
  evidenceIds: string[]
}

export interface Issue {
  id: string                 // ISO week, `2026-w36`
  weekEnding: string         // ISO date, the Sunday
  windowStart: string        // ISO date; normally weekEnding − 6, longer only for the opening issue
  published: string | null   // ISO date; null while draft
  status: IssueStatus
  read: string               // one line, ≤ 140 chars, the h1
  quiet?: true               // a quiet week says so
  sections: Array<{ lane: Lane; intro?: string; items: IssueItem[] }>   // exactly four, in Lane order
  weThink: {
    summary: string
    postureDeltas: PostureDelta[]
    thesis: ThesisScore
    noCalls: string[]
    signedBy: string | null
    signedOn: string | null
  }
  sources: { readable: number; unreadable: string[] }
}
```

`DecisionHorizon` gains `'Next 4–8 quarters'` and `'Beyond 8 quarters'` so the 24-month horizon intent
promises is representable. No existing posture is re-judged by this spec.

Evidence records cited by an issue live in `src/data/evidence.ts` as today, with `retrievedAt` added
as an optional field.

The first issue is `2026-w36`, week ending 2026-09-06, window 2026-08-24 to 2026-09-06 as a stated
opening window, status `draft`, unsigned. It is drafted from a real gather during the build so the
owner's first review is of a real issue.

## 4. Page composition

### `/` front page, in order

1. **Header.** Nav: Issue · Archive · Thesis · Landscape · Scorecard · Evidence · Method. Archive is a
   cross-page link; the rest are hash anchors.
2. **Issue hero** (`#issue`). Eyebrow: `Issue 2026-w36 · week ending 6 Sep 2026 · published 16 Sep
   2026` or `· draft, awaiting signature`. `h1` is `issue.read`. A draft shows a visible banner
   reading "Draft. Not yet signed." on every width.
3. **Four lane sections** (`#formation`, `#absorption`, `#prints-this-week`, `#capital`). Each: the
   lane name as `h2`, optional intro, items as a list. An item shows headline, date, why, the
   evidence links, and a small "background" label when `background` is set. An empty lane renders
   its heading and one line: "Nothing new this week."
4. **What we now think** (`#we-think`). Summary, posture deltas as `from → to` with basis and
   evidence, the thesis score as a labelled line, no-calls, then the signature line
   `Signed by Jesse Pike · 16 Sep 2026` or `Unsigned draft`.
5. **Standing reference**, all visible, in this order:
   - **Thesis** (`#thesis`): the Episode 002 market call as today's `JudgmentBoard` content, with a
     new first line: the running score, derived from every published issue's `thesis.verdict`
     (`Holds in 3 of 3 issues since 16 Sep 2026`).
   - **Landscape** (`#landscape`): the four domain cards, **led by the trigger sentence** (the
     action line the card currently shows third) as the card title, with the domain name as a label
     above it. Posture tag, horizon and judged date as today. The confidence chip is shown only when
     confidence differs across the landscape cards; when every card reads the same value it is
     omitted from the cards and stated once in the Tempo table. Derived, not hand-set.
   - **Platform pressure** (`#platforms`) unchanged.
   - **Tracked hypotheses** (`#hypotheses`) unchanged.
   - **Scorecard** (`#prints`) unchanged, plus the vendor lens control at its top.
6. **Depth** disclosures, in order: What moved (edition delta, the current `WhatMoved` component),
   Tempo and prior Activity window (the current `research-depth` block, with the Activity board
   labelled as the pre-issue window it is), Layers, Watch next, Method, Evidence library.
7. Methodology note and the corrections block, as today.

Must-see ids for `/`: `issue`, `formation`, `absorption`, `prints-this-week`, `capital`, `we-think`,
`thesis`, `landscape`, `platforms`, `hypotheses`, `prints`.

### `/issues/` archive

Header, `h1` "Issues", one row per issue newest first: id, week ending, read, status or signature,
link. A draft row is labelled. Under the list, a link to the standing reference on `/`.

Must-see ids: `issues`.

### `/issues/<id>/` permalink

Header, the issue hero, four lanes, what we now think, exactly as on `/`, then a short block linking
to the archive and the standing reference. Canonical URL is itself.

Must-see ids: `issue`, `formation`, `absorption`, `prints-this-week`, `capital`, `we-think`.

### Phone (390)

Same document order. The draft banner and the signature line stay visible. Lane items stack. The
lens control collapses to a single row of chips with horizontal scroll.

## 5. Vendor lens (SEC-031)

A query parameter `?vendors=a,b,c` of vendor slugs. When present, the issue's lane items and the
scorecard's print cards are filtered client-side to items and prints carrying any listed slug; the
lens control shows the active set and a clear link; the URL is the share mechanism. Slugs are derived
from `vendorPrints` (lower-case, hyphenated vendor name) and stored on each `VendorPrint` and
`IssueItem.vendors`. Without the parameter the page is unchanged. Prerendered HTML is never
filtered; the lens applies after hydration, and the control reads "Showing N of M" so a reader can
tell it is active.

## 6. Gates

New `scripts/verify-issue.ts`, wired into `npm run build` after `verify:integrity`. Each check is
proven by perturbation before it counts.

1. `issues` is ordered by `weekEnding` ascending, ids match `^\d{4}-w\d{2}$`, and each `weekEnding`
   is the Sunday of that ISO week.
2. Windows do not overlap.
3. Exactly four sections in Lane order per issue.
4. Every `IssueItem.evidenceIds` entry resolves in `evidenceRecords`; every item `date` falls inside
   the window unless `background` is set.
5. A `published` issue has `published`, `signedBy` and `signedOn` set; a `draft` has all three null.
6. At most one draft, and it is the newest issue.
7. Production guard: when `VERCEL_GIT_COMMIT_REF` is `main`, the newest issue must be `published`.
8. Published issues are hash-locked: `sha256(JSON.stringify(issues.filter(published)))` must equal
   `EXPECTED_ISSUES_SHA`, with `--write` to print the new value, the `verify-edition` pattern.
9. Every `PostureDelta` in a published issue agrees with `securityDomains` (the domain's posture is
   `to`) and with `editions` (a record dated on or after `published` carries `to` for that domain).
10. Render check: `renderToStaticMarkup` of the issue view for the newest issue; each lane heading's
    rendered item count equals `items.length`, the draft banner is present iff `status === 'draft'`,
    and the signature line text matches the data.
11. Every published issue's permalink, JSON copy and the feed exist in `dist` after prerender, and
    `feed.xml` parses as XML with one `<item>` per published issue.

`scripts/prerender.ts` runs its must-see gate per route with the id lists in §4. `verify-integrity`
check 5 (unreferenced evidence) counts issue citations as references.

## 7. Tests

- `tests/e2e/issue.spec.ts`, run at both 1440×900 and 390×844 as two Playwright projects:
  `h1` equals the newest issue's read; the five issue sections and the standing-reference sections
  are visible via `checkVisibility()`; the draft banner is visible iff the newest issue is a draft;
  `/issues/` lists every issue; `/issues/<newest>/` renders with the same `h1`; `/feed.xml` returns
  200 and `content-type` XML; `/issues/<newest>.json` parses and its `evidence` array is non-empty;
  `?vendors=` filters the scorecard and shows "Showing N of M"; zero page errors.
- `playwright.config.ts` honours `E2E_BASE_URL` so the same suite runs against the live preview URL.
- `tests/issue-data.test.ts` covers the derived helpers (ISO week, window, thesis score, lens slugs).
- The existing smoke test is updated for the new `h1` and structure, without deleting any assertion
  that still holds.

## 8. Visual review

Before the preview is offered for review: `node scripts/shot.mjs` on production and on the preview
URL at both widths; a written statement of what moved, section by section; and the expected list is
this spec's §4. Everything on production is accounted for as kept, moved to depth, or changed.

## 9. Acceptance

- Front page opens with issue `2026-w36` as a labelled draft; `h1` is its read; all four lanes and
  "what we now think" visible at both widths with no disclosure ancestor.
- Standing reference visible below it in the order in §4; nothing from production missing.
- Archive and permalink routes prerendered and served on the preview URL; JSON copies and feed served.
- Landscape cards lead with the trigger sentence; the confidence rule derives; horizon type extended.
- Vendor lens filters and is shareable by URL.
- All eleven `verify:issue` checks proven by perturbation; full `npm run build` and `npm run test`
  green in the dev VM; the e2e suite green against the live preview URL.
- Rendered before-and-after at both widths with the written diff.

## 10. Not in scope

Per-issue Open Graph images. An email provider. Any change to a posture, confidence, call or
hypothesis state. Anything on `main`.
