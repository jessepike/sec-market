# Weekly issue specification

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-ISSUE-001` |
| **Version** | v0.2 — amended 2026-09-03 after Codex (gpt-5.6-sol) and Claude reviews; see §11 |
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
  confidence: ConfidenceLevel
  evidenceIds: [string, ...string[]]
}

export interface ThesisScore {
  thesis: 'episode-002'
  verdict: 'holds' | 'strengthens' | 'weakens' | 'no-call'
  basis: string
  confidence: ConfidenceLevel
  evidenceIds: string[]
}

/** What the gather proposes. Visible on a draft, labelled as a machine proposal; must be null once published. */
export interface MachineProposal {
  read: string
  thesis: ThesisScore
  noCalls: string[]
  postureDeltas: string          // prose only; the signer converts what they accept into PostureDelta records
  summary: string
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
    thesis: ThesisScore | null   // null on a draft; the signer sets it
    noCalls: string[]
    signedBy: string | null      // must equal AUTHOR_NAME in meta.ts when set
    signedOn: string | null
  }
  proposed: MachineProposal | null   // set by the gather on a draft; null once published
  sources: { readable: number; unreadable: string[] }
}
```

**Who writes what.** The gather writes `read`, the four sections, `sources`, and `proposed`. It leaves
`weThink.thesis` null, `weThink.postureDeltas` empty, `weThink.summary` empty. The signer reads the
proposal, writes `weThink` themselves, sets `proposed: null`, `signedBy`, `signedOn`, `published`,
`status: 'published'`. A posture change is one human-signed transaction that edits the issue's
`postureDeltas`, `domains.ts` and an appended `edition.ts` record together; posture-change language
belongs in `postureDeltas` and nowhere else. Issue `2026-w36` carries no deltas.

Evidence records gain an optional retrieval receipt:

```ts
retrieval?: { finalUrl: string; sha256: string; fetchedAt: string; locator?: string }
```

One evidence record per document. An excerpt never combines documents; an item cites several ids
instead.

**Cadence, canonical.** An issue id is the ISO week it covers; `weekEnding` is that week's Sunday. The
Tuesday gather drafts the ISO week that ended the previous Sunday. The first issue is `2026-w36`.
Dates elsewhere in the plan that imply a different first week are superseded by this paragraph.

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
2. **Issue hero** (`#overview`). Eyebrow: `Issue 2026-w36 · week ending 6 Sep 2026 · published 16 Sep
   2026` or `· draft, awaiting signature`. `h1` is `issue.read`. A draft shows a visible banner
   reading "Draft. Not yet signed." on every width.
3. **Four lane sections** (`#formation`, `#absorption`, `#prints-this-week`, `#capital`). Each: the
   lane name as `h2`, optional intro, items as a list. An item shows headline, date, why, the
   evidence links, and a small "background" label when `background` is set. An empty lane renders
   its heading and one line: "Nothing new this week."
4. **What we now think** (`#we-think`). On a published issue: summary, posture deltas as
   `from → to` with basis, confidence and evidence, the thesis score as a labelled line with its
   confidence, no-calls, then the signature line `Signed by Jesse Pike · 16 Sep 2026`. On a draft:
   the block is headed "Machine proposal, unsigned" and shows `proposed.*` in the same layout, with
   the line `Unsigned draft. Nothing here is a judgment until a named person signs it.`
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

Must-see ids for `/`: `overview` (the issue hero keeps this id), `formation`, `absorption`,
`prints-this-week`, `capital`, `we-think`, `read` (the thesis block keeps this id), `landscape`,
`platforms`, `hypotheses`, `prints`. The `moved` section leaves the must-see list deliberately: the
issue's four lanes replace it as the account of what moved, and the edition delta stays reachable in
depth. This is a recorded replacement, accepted under D-64, not a dropped guarantee.

### `/issues/` archive

Header, `h1` "Issues", one row per issue newest first: id, week ending, read, status or signature,
link. A draft row is labelled. Under the list, a link to the standing reference on `/`.

Must-see ids: `issues`.

### `/issues/<id>/` permalink

Header, the issue hero, four lanes, what we now think, exactly as on `/`, then a short block linking
to the archive and the standing reference. Canonical URL is itself.

Must-see ids: `overview`, `formation`, `absorption`, `prints-this-week`, `capital`, `we-think`.

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

Two scripts. `scripts/verify-issue.ts` runs before the build (after `verify:integrity`) and checks
the data, checks 1 to 10 and 12. `scripts/verify-dist.ts` runs last, after `seo`, and checks the
emitted files, check 11. Build order: `verify:edition && verify:panel && verify:integrity &&
verify:issue && tsc -b && build:client && build:server && prerender && seo && verify:dist`. Each
check is proven by perturbation before it counts.

1. `issues` is ordered by `weekEnding` ascending, ids match `^\d{4}-w\d{2}$`, each `weekEnding`
   is the Sunday of that ISO week, and both `id` and `weekEnding` are unique.
2. Windows do not overlap.
3. Exactly four sections in Lane order per issue.
4. Every `IssueItem.evidenceIds` entry resolves in `evidenceRecords`; every item `date` falls inside
   the window unless `background` is set.
5. A `published` issue has `published`, `signedBy`, `signedOn` set, `signedBy` equal to
   `AUTHOR_NAME` from `meta.ts`, `proposed` null, `weThink.summary` non-empty, `weThink.thesis`
   non-null with non-empty `basis` and `evidenceIds`, and every `PostureDelta` and the thesis carrying
   a `confidence`. A `draft` has `published`, `signedBy`, `signedOn` null and `weThink.thesis` null.
6. At most one draft, and it is the newest issue.
7. Production guard: when `VERCEL_GIT_COMMIT_REF` is `main`, the newest issue must be `published`.
8. Published issues are append-only, enforced by a manifest `src/data/issues/issues.lock.json`
   mapping each published id to `sha256(JSON.stringify(issue))`. The check fails if a manifest id is
   missing from `issues`, if a published issue's hash differs from its manifest entry, or if a
   published issue has no manifest entry. `--write` adds entries for new ids only and refuses to
   alter or remove an existing one; changing history requires deleting the entry by hand in a
   reviewed commit.
9. Every `PostureDelta` in a published issue agrees with `securityDomains` (the domain's posture is
   `to`) and with `editions` (a record dated on or after `published` carries `to` for that domain).
10. Render check: `renderToStaticMarkup` of the issue view for the newest issue; each lane heading's
    rendered item count equals `items.length`, the draft banner is present iff `status === 'draft'`,
    and the signature line text matches the data.
11. (`verify:dist`) Every issue's permalink and JSON copy, `issues/index.html`,
    `issues/index.json`, `feed.xml` and `sitemap.xml` exist in `dist`; `feed.xml` parses as XML with
    one `<item>` per published issue; the sitemap lists every route.
12. Every numeric token in an item's `headline` and `why` (integers, decimals, percentages, currency
    amounts with M or B suffixes, normalised for separators) appears in at least one cited evidence
    record's `excerpt`. A figure the page states that no cited excerpt states fails the build.

`scripts/prerender.ts` runs its must-see gate per route with the id lists in §4. `verify-integrity`
check 5 (unreferenced evidence) counts issue citations as references.

## 7. Tests

- `tests/e2e/issue.spec.ts`, run at both 1440×900 and 390×844 as two Playwright projects:
  `h1` equals the newest issue's read; the five issue sections and the standing-reference sections
  are visible via `checkVisibility()`; the draft banner is visible iff the newest issue is a draft;
  `/issues/` lists every issue; `/issues/<newest>/` renders with the same `h1`; `/feed.xml` returns
  200 and `content-type` XML; `/issues/<newest>.json` parses and its `evidence` array is non-empty;
  zero page errors and zero console errors.
- `tests/e2e/lens.spec.ts`, both widths: `?vendors=` filters both the issue items and the scorecard
  and shows "Showing N of M" on each; an unknown slug yields "Showing 0 of M" and a clear link, not
  an error; the clear link restores the unfiltered URL; the URL round-trips through the control; at
  390 the chip row is reachable and scrollable; zero console errors.
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

## 11. Amendments after external review (2026-09-03)

Codex `gpt-5.6-sol` and a fresh Claude Sonnet session reviewed v0.1 against intent v1.2, the plan
and the code. Accepted and folded in above: one canonical cadence (§3); confidence on every judgment
and a machine-proposal block that must be null at publication (§3, §6.5); `signedBy` allow-listed to
`AUTHOR_NAME` (§6.5); per-issue append-only lock manifest instead of one array hash (§6.8); split of
data and dist gates with the build order fixed (§6); uniqueness (§6.1); numeric-token check (§6.12);
retrieval receipts and one record per document (§3); posture change as one signed transaction (§3);
`overview` and `read` retained as must-see ids and the `moved` replacement recorded (§4); lens tests
widened (§7). Declined: an authenticated signer, which static data cannot carry; the merge by the
repository owner is the authentication.

### Amendments after the whole-diff review (2026-09-04)

A whole-diff external review (Codex and a fresh Claude session) of the built implementation found
gaps between what §6 described and what `scripts/verify-issue.ts` and `scripts/verify-dist.ts`
actually checked. Accepted and folded in:

- F1: check 4 now resolves `weThink.thesis.evidenceIds`, `weThink.postureDeltas[].evidenceIds`, and
  on a draft `proposed.thesis.evidenceIds`, the same way lane-item ids are resolved; check 12 no
  longer silently skips an unresolved id, it fails.
- F2: dates are now strict — every `date`, `weekEnding`, `windowStart`, `published` and `signedOn`
  must match `^\d{4}-\d{2}-\d{2}$` and name a real calendar date; a published issue requires
  non-empty `published` and `signedOn`; an item dated after `weekEnding` fails regardless of
  `background`, and `background` is only valid when the item is dated before `windowStart`.
- F3: a draft is now checked for an empty `weThink` block — empty `summary`, empty `postureDeltas`
  and `noCalls`, and null `thesis`, `signedBy`, `signedOn`, `published` — not just a published
  issue's completeness.
- F4: added bounds — at most eight items per lane, `read` at most 140 characters, an item
  `headline` at most 110 characters, and a non-empty `why` — each failure names the offending id
  and the measured length.
- F5: `--write` now validates the candidate issue on every other check before writing the
  manifest, and the manifest is append-only against a trusted base ref (`origin/preview`, else
  `preview`, else `HEAD~1`), not just self-consistent with the current `issues` array; a shallow
  clone with no matching ref prints one loud warning and continues rather than failing the build.
- F6: `verify:dist` now checks identity, not just presence — each `dist/issues/<id>.json`'s
  `issue.id` must match its filename and its `evidence` array must equal the ids the issue cites;
  `dist/issues/index.json` is checked for the exact newest-first id/status order, not just its
  length; `dist/feed.xml` is parsed for every `<item>`'s `guid` and `pubDate`, checked against the
  published-issue permalink set and RFC 822 respectively.
- F7: off the front page, `Header`'s brand link and section links now point to `/#<id>` and only
  intercept the click when that id exists in the current document, so a link to a front-page-only
  section navigates there instead of silently doing nothing.
- F8: every dynamic value `scripts/prerender.ts` inserts into `<title>` and a `<meta>` tag's
  `content` is now HTML-attribute-escaped, so an issue `read` line carrying `&`, `<`, `>`, `"` or
  `'` cannot break the tag it lands in.
- F9: every evidence record cited by an issue must now carry a machine-readable `retrieval`
  receipt (`finalUrl`, a 64-hex `sha256`, `fetchedAt`, and an optional `locator`) confirmed against
  a live re-fetch of its `canonicalUrl`; check 15 fails a citation with no receipt, naming the id.

