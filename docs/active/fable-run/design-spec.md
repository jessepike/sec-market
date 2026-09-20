# Design specification — Security Market Pulse

**Artifact ID:** `SEC-MARKET-FABLE-DESIGN` v0.1 (proposal, awaiting owner acceptance)
**Written by:** the run coordinator, 2026-09-20
**Built on:** `site-rubric.md` v1.1, `score-baseline.md` (composite 33.0, exposure denominator 1),
`research-synthesis.md`, `codebase-map.md`, `research/08-thesis-history-inventory.md`
**Status:** nothing in this document has been built. Phase 4 starts only after the owner accepts it.

## 1. The design in one paragraph

The site already contains a good argument. It is in the wrong order. The signed judgment, what
changed, what to do and avoid, what the site refuses to call, and the four conditions that would
change the call all exist today, well written, between 4,700 and 7,000 pixels down a 15,000 pixel
page, underneath twenty-three funding and filing cards. This design moves the argument to the top,
turns the cards into rows, gives the standing thesis a page of its own that grows by one line every
time an issue is signed, and removes the three dark panels and the second typeface. Almost all of
it is reordering and restyling of content that is already signed and published. Very little new
prose is needed, and none of it is a market judgment.

## 2. Principles

1. **Argument before inventory.** A security leader came for the read. The tracked items are the
   evidence for the read and sit below it.
2. **The thesis is a standing object, the issue is a weekly event.** They look different, live at
   different addresses and are never confused on screen.
3. **Honest at small scale.** One signed issue exists. Every history surface shows one row and
   says so. Nothing is padded to look established.
4. **Rows, tables and plain labels.** Linear's restraint, Zed's density. One accent colour. Light
   theme only.
5. **Accessibility is the thing to protect.** The site scores 4 of 5 today with zero axe
   violations. Denser layouts are exactly what breaks target size and focus rules, so every
   stream re-runs the measurements in `evidence/baseline/measure/` before it merges.
6. **Keep the gates green.** Section ids, the `details` nesting rule, the render check and the
   lock manifest are constraints on this design, listed in section 9.

## 3. The first screen

The first screen is the first viewport with no scrolling, at 1440 by 900 and at 390 by 844. The
reading order is the same at both widths.

### 3.1 At 1440 by 900

```
+----------------------------------------------------------------------------------------------+
| Security Market Pulse            This week   Thesis   Issues   Evidence   Method   Feed       |  56
+----------------------------------------------------------------------------------------------+
| A weekly signed read on where security spending is actually moving, for security leaders      |
| and the teams who advise them. Public sources only. Signed by Jesse Pike.                     |  ~48
|                                                                                              |
| ISSUE 2026-W36 · WEEK ENDING 6 SEP 2026 · SIGNED 19 SEP 2026 · NEXT ISSUE EXPECTED <date>    |  ~32
|                                                                                              |
| THIS WEEK'S READ                                | STANDING THESIS · since 15 Aug 2026         |
| <h1: the signed read, 32px, up to 3 lines>      | Infrastructure is running ahead. Security   |
|                                                 | is splitting, not booming.          (24px) |
| <gloss line, only when the headline uses a      |                                             |
|  term of art: one sentence decoding it>         | HOLDS · medium confidence                   |
|                                                 | judged 19 Sep 2026 by Jesse Pike            |
| <the read in full, 16px, up to 3 lines>         | Held in 1 of 1 signed issues  ->  record    |
|                                                 |                                             |
| SINCE THE LAST ISSUE                            | DOES NOT CLAIM                              |
| · First signed issue. Nothing earlier to        | A stable lag between infrastructure         |
|   compare against.                              | spending and security spending.             |
| · No domain posture moved.                      |                                             |
| · 23 tracked items across four lanes.           | WOULD CHANGE THE CALL          status       |
|                                                 | Security budgets grow and...   no movement  |
| Read the signed judgment  v                     | Organic acceleration across... no movement  |
|                                                 | AI pilots reach production...  no movement  |
|                                                 | Registered impulse then...     no movement  |
+----------------------------------------------------------------------------------------------+  900
```

Left column is seven of twelve grid columns, right column is five. The right column is the new
`ThesisPanel`. It is a white surface with a one pixel strong border. It replaces the dark thesis
block. The status column in the panel depends on owner decision D-3 in section 11; without it the
four conditions are listed with no status.

### 3.2 At 390 by 844

```
+--------------------------------------+
| Security Market Pulse          Menu  |   48   chrome ends here
+--------------------------------------+
| A weekly signed read on where        |
| security spending is moving. Signed  |
| by Jesse Pike.                       |   ~56
| ISSUE 2026-W36 · WEEK ENDING 6 SEP   |
| SIGNED 19 SEP 2026                   |   ~40
| THIS WEEK'S READ                     |
| <h1, 24px, up to 5 lines>            |   ~160
| <gloss line when needed>             |
| STANDING THESIS                      |
| Infrastructure is running ahead.     |
| Security is splitting, not booming.  |   ~90   (20px)
| HOLDS · medium · 19 Sep 2026         |
| Held in 1 of 1 signed issues ->      |   ~60
| DOES NOT CLAIM a stable lag...       |   ~50
+--------------------------------------+  ~560 to 700 of 844
```

Site chrome drops from 221 pixels (26.2 percent of the viewport) to 48 pixels. The header loses
its second row on phones; the issue line and the descriptor become the first lines of page
content. The full read, "since the last issue" and the change conditions follow directly below
the fold in the same order as desktop.

### 3.3 What each first-screen element is for

| Element | Source in the codebase | Rubric tests it answers |
|---|---|---|
| Descriptor line | New site copy in `src/data/meta.ts`. Owner edits the wording on preview. | D1 L3-4, D4 L5-3 |
| Issue line with both dates | Exists in `IssueHero`. Gains "next issue expected", decision D-4. | D3 L3-1, L5-1, L5-3 |
| "This week's read" label and h1 | `issue.read`, already the h1. | D4 L3-1, D1 L3-2 |
| Gloss line | New optional site-level map from a term to one plain sentence. See 3.4. | D1 L3-3 |
| Standing thesis panel | `marketCall.headline`, `issue.weThink.thesis`, `thesisRunningScore()`, `marketCall.noCallBoundaries`, `marketCall.changeTriggers`. All existing data. | D1 L3-1, L3-2, L5-1, L5-3, L5-4; D2 L3-1, L3-3 |
| "Since the last issue" | Derived at build time from `weThink.postureDeltas`, the previous issue's verdict and the item counts. No new judgment. | D2 L3-2, D3 L3-3 |

### 3.4 The jargon problem, stated honestly

The signed headline of issue 2026-w36 ends "the infra-to-security lag call holds". That is
internal language and it fails D1 L3-3. The text of a published issue is hash-locked and must not
be edited. So the design does two things. It puts a one-sentence gloss under any headline that
uses a listed term of art ("The lag call is this site's refusal to claim that infrastructure
spending leads security spending by a fixed interval."). And it asks the owner for a writing rule
for future issues, decision D-5: the read is written for a reader who has never seen the site.
The gloss is a site-level annotation beside the locked text. It does not change the locked text.

## 4. The rest of the front page

### 4.1 Order

| # | Section | id (unchanged) | Change |
|---|---|---|---|
| 1 | First screen | `overview` | Reshaped as above. New `ThesisPanel` inside it. |
| 2 | The signed judgment | `we-think` | Moves up from y=5,137 to directly under the first screen. Target: signature above y=1,700 at 1440 and y=1,650 at 390. |
| 3 | The standing call: what changed, do, avoid, will not call, would change the call | `read` | Moves up with it. Tightened to two columns at 1440. The dark background goes. |
| 4 | Follow line | new, `follow` | One sentence and a feed link, placed after the judgment. |
| 5 | Domain postures | `landscape` | Six cards become one table: domain, posture, horizon, since, tracked basis, judged basis. |
| 6 | Vendor filter | `vendor-lens-slot` | Moves to the head of the lanes it filters. Class names unchanged. |
| 7 | The four lanes | `formation`, `absorption`, `prints-this-week`, `capital` | Cards become rows. See 4.2. |
| 8 | Platform pressure, hypotheses, prints | `platforms`, `hypotheses`, `prints` | Order kept. Restyled to the shared row and table patterns. |
| 9 | Depth sections | `moved-depth`, `research-depth`, `layers`, `watch`, `research` | Stay as closed sections. Summary text unchanged, because the smoke test asserts it. |
| 10 | Method | `method` | Decision D-2: moves to its own page `/method/`, leaving a three-line summary and a link. |
| 11 | Next edition | `next` | Kept. Agrees with the issue line. |

Nothing in this order puts a required section inside a closed section, so the prerender must-see
gate holds. No gate or test asserts section order.

**Height budget at 1440.** First screen 900, judgment 500, standing call 1,100, follow 80,
postures table 420, filter 80, lanes 1,300. That puts the judgment, the change conditions, the
postures and all of the week's evidence inside 4,400 pixels, against D4 L5-1's limit of 5,000.
The whole page should land near 8,000 pixels, down from 15,022. The rubric's 6,000 pixel test
(D6 L5-1) is a stretch that this plan does not promise.

### 4.2 Lane rows

One row per tracked item, replacing `.issue-lane__item` cards. The class names
`.issue-lane__item` and `.issue-lane__headline` stay, because `tests/e2e/lens.spec.ts` selects on
them.

```
1440:  06 SEP   Headline that states the fact, up to 110 characters            FILING   Source ›   #
                Why it matters, one sentence, 14px, muted
 390:  06 SEP · FILING · Source ›
       Headline that states the fact
       Why it matters
```

- Row height about 64 pixels at 1440, so a full lane of eight fits one screen (D6 L3-1, L5-4).
  About 150 pixels at 390, so five rows fit a phone screen.
- The date is a `time` element in monospace. The evidentiary kind (filing, company disclosure,
  database, press, own estimate) is a small text label from `EvidenceRecord.sourceClass`, shown on
  the row itself and not only inside the evidence panel (D5 L5-1).
- The source control is the existing chip and opens the existing evidence panel. Its target stays
  at least 24 by 24 pixels, with the 44 pixel height it has today on phones.
- Each row gets `id={item.id}`. The ids already exist in the data (`2026-w36-formation-3`). A
  small "#" link copies the address (D7 L3-4, D8 L5-2).
- **Consequence ordering (D4 L3-3, D6 L3-2)** needs owner decision D-3, because `IssueItem` has
  no size or importance field today. With it, the signer marks up to two items per lane as the
  lead; lead rows render first with a heavier headline. Without it, rows stay chronological and
  those two tests keep failing. Issue 2026-w36 is locked and stays chronological either way.

### 4.3 The evidence panel

The panel is the best-made thing on the site and is left alone apart from two additions: the
retrieved date (already in the data as `retrievedAt`) and a "Report a problem with this source"
mail link that carries the evidence id in its subject (D5 L5-2, L5-4).

## 5. The thesis surface, and how it accumulates

A new route, `/thesis/`. It is the stable address for the argument (D1 L5-2) and the one place the
whole history sits in order (D2 L5-2). The navigation item "Thesis" points to it. The front page
anchor `/#read` stays alive.

| Block | Content | Source | Accumulates how |
|---|---|---|---|
| Statement | The thesis sentence, a plain paragraph on what it means, the confidence note | `marketCall.headline`, `.meaning`, `.confidenceNote` | Changes only when the owner changes the standing call |
| Does not claim | The four no-call boundaries | `marketCall.noCallBoundaries` | Same |
| Current verdict | Verdict, confidence, basis, signer, date, link to the issue | newest `issue.weThink.thesis` | Replaced each signed issue |
| Verdict ledger | Table, newest first: issue, week ending, verdict, confidence, one-line basis, signed by, link | Derived from every published issue | **One new row per signed issue, with no extra work** |
| Change conditions | The four conditions, each with a status and a date | `marketCall.changeTriggers` plus the new optional field in D-3 | One status per condition per issue |
| Earlier record | The three unsigned edition records of 16, 17 and 28 August, labelled "unsigned edition record" | `src/data/edition.ts`, already rendered in a closed section | Closed history |
| How scoring works | What holds, strengthens, weakens and no-call mean, and how "held in N of M" is computed | New method copy, drafted from `issueHelpers.ts` lines 62 to 91 | Static |
| Calibration | One honest statement: the thesis has no resolution date yet, so there is nothing to calibrate against; a comparison of stated confidence with outcomes will appear once there are resolved calls | New copy, owner edits | Becomes a table later |
| Corrections | A dated list with a stable anchor, `/thesis/#corrections`. Reads "None to date." today | New empty data file | One entry per correction |

The ledger is the mechanism that makes the thesis "live". With one issue it shows one row and
says "one signed issue so far". A week in which the verdict holds still shows movement if the
condition statuses are recorded, which is why D-3 matters more than it looks.

The front page and the permalink stop being the same page in purpose (D3 L5-2). The front page
shows the current state of the argument. The permalink is the immutable record of one week, says
so in a line under its header, links the lock manifest, links previous and next issues, and, when
it is not the newest issue, says "This is a past issue. The newest is <link>."

## 6. Information architecture and navigation

| Route | Status | Purpose |
|---|---|---|
| `/` | exists, reordered | The current state of the argument, then this week's evidence |
| `/thesis/` | new | The standing thesis, its verdict ledger, corrections |
| `/issues/` | exists | The archive. Gains a verdict column and a confidence column (D7 L3-1) |
| `/issues/<id>/` | exists | The immutable record. Gains previous and next links, the past-issue line, the lock link |
| `/method/` | new, decision D-2 | How evidence becomes a call, who the author is, boundaries, independence, machine access, terms |

Navigation: This week, Thesis, Issues, Evidence, Method, Feed. Six items, down from seven
anchors. At 390 they sit behind the existing Menu control.

A new route is not discovered automatically. The build stream must touch `src/data/routes.ts`,
`MUST_SEE_SECTION_IDS` in `scripts/prerender.ts`, the per-route logic in
`scripts/generate-seo.ts` and the id lists in `scripts/verify-issue.ts` together, and
`tests/e2e/issue.spec.ts` must be changed on purpose where it asserts that "Thesis" navigates to
`/#read`.

## 7. Type and colour

**Type.** One sans family and one monospace family. IBM Plex Sans for everything that is prose
or heading, IBM Plex Mono for dates, ids, amounts and labels. Archivo is retired (decision D-6);
headings use Plex Sans at weight 600. Both families are self-hosted as subset `woff2` files with
`font-display: swap` and a preload for the two weights used on the first screen. This removes the
render-blocking request to Google Fonts, which is the likely cause of the 3.9 second first paint
on phones.

Six sizes on the front page, from a stylesheet that declares more than seventeen today:

| Size | Use |
|---|---|
| 12px mono | Labels, dates, ids, source class |
| 14px | Secondary row text, table cells, captions |
| 16px | Body and the read |
| 20px | Section headings; the thesis sentence at 390 |
| 24px | The thesis sentence at 1440; the h1 at 390 |
| 32px | The h1 at 1440 |

No continuous reading text under 14 pixels. Prose blocks keep `--prose-max: 68ch`.

**Colour.** The existing neutral scale stays (`#e9ecf0` page, `#fff` surface, `#d3d8df` border,
`#12161c` heading, `#3a424e` text, `#57606e` muted). One accent, the existing teal `#0b6b5e`,
used for links, focus and the current verdict. The pink and olive hues leave the chrome. Verdict
and posture states are told apart by their word and by weight and border, so a greyscale capture
still reads (D13 L5-1). The three dark panels (the top bar, the thesis block, the posture block)
become light surfaces with a strong one pixel border. Non-text contrast is sampled and recorded
for the first time, because D10 L5-6 fails today only as "not measured".

## 8. What gets removed or moved

Removing a visible page section is an owner gate. Nothing below happens without a yes, and each
item is proven with a before and after render, never by static analysis.

| Item | Proposal | Visible effect |
|---|---|---|
| Method section and methodology note on the front page | Move to `/method/`, leave a three-line summary and link (D-2) | Front page about 1,500 pixels shorter; Method reachable in one click |
| The sentence "Refresh is manual... Not a weekly news cycle" in `src/components/HowThisWorks.tsx` lines 23 to 24 | Replace with a cadence sentence the owner writes (D-4) | Lifts the freshness cap on D12 and passes D3 L3-2 |
| Dark backgrounds on three panels | Restyle light | The page stops alternating between two themes |
| Archivo typeface | Retire (D-6) | Headings change shape slightly |
| Lane cards | Become rows | Lanes shrink from about 4,000 to about 1,300 pixels |
| Domain cards | Become one table | About 600 pixels shorter, comparable across domains |

No component, stylesheet rule or data export is deleted in this run. Superseded components stay
in the tree until a later pass proves them unused by render.

## 9. Constraints the build must respect

- The prerender must-see gate: the eleven front-page ids must exist and none may sit inside a
  `details` element.
- `verify-issue` check 10 server-renders the hero, the lanes and the judgment and asserts the
  per-lane item counts and the exact signature text. Rows must keep one element per item.
- `tests/e2e/smoke.spec.ts` asserts the summary text of `#moved-depth`, the id
  `#market-call-heading`, the `#research-depth` reveal and the evidence dialog.
- `tests/e2e/lens.spec.ts` selects `.issue-lane__headline`, `.print-card h3`, the "Showing N of M"
  text and the horizontal scroll of `.vendor-lens__chips`.
- The lock manifest hashes `JSON.stringify(issue)`. New optional fields that are undefined on a
  locked issue are safe. Any edit to 2026-w36 is not.
- The OG image staleness gate ties `assets-src/og.svg` to `marketCall.headline`.
- Hydration parity is kept by convention only. Anything derived at build time ("since the last
  issue", the ledger) must be computed from data available to both the server render and the
  client, with no dates read from the clock during render. "Next issue expected" and any "late"
  label are computed from data at build time for the same reason, and the build stream must say
  how a late label appears when no build has run.
- All node, npm, build, test and capture commands run in the OrbStack dev VM. Captures use
  `evidence/baseline/capture.mjs`, because `web/scripts/shot.mjs` needs Google Chrome, which the
  VM does not have.

## 10. What this should do to the score

A projection, which is a guess until Phase 5 measures it. Both scorers re-score blind.

| Dimension | Now | If every decision below is a yes | If D-2 to D-6 are all no |
|---|---|---|---|
| D1 Thesis clarity (12) | 0 | 4 to 5 | 4 |
| D2 Thesis development (12) | 2 | 4 to 5 | 3 to 4 |
| D3 Reason to return (10) | 1 | 4 | 2 to 3 |
| D4 First screen (12) | 1 | 4 | 2 |
| D5 Evidence (8) | 3 | 4 | 4 |
| D6 Density (8) | 2 | 4 | 2 to 3 |
| D7 Wayfinding (5) | 1 | 4 | 4 |
| D8 Agent legibility (10) | 2 | 4 to 5 | 4 |
| D9 Performance (5) | 2 | 3 | 2 to 3 |
| D10 Accessibility (7) | 4 | 4 to 5 | 4 |
| D11 Conversion (3) | 0 | 3 | 3 |
| D12 Trust (5) | 2 | 4 to 5 | 2 (cap stays) |
| D13 Craft (3) | 2 | 3 to 4 | 2 |
| **Composite** | **33.0** | **about 75 to 83** | **about 58 to 64** |

The cadence cap holds D3 at 2 from 2026-10-04 if no further issue is signed, which costs four
points whatever is built. **The exposure denominator stays at 1 in every column.** None of this
changes who has read the work.

## 11. Decisions this document needs from the owner

| # | Decision | Recommendation |
|---|---|---|
| D-1 | Accept the first-screen order and the front-page order in sections 3 and 4 | Yes |
| D-2 | Move the method section to `/method/` (removes a visible front-page section) | Yes |
| D-3 | Two new optional fields on the issue model, set by the signer at signing: `lead` on an item, and a status per change condition on the judgment. Locked issues are untouched. The gather job and the draft pipeline are not changed; the signer types them in. | Yes. Without it, a week where the verdict holds shows no movement, and the lanes cannot lead with what matters. |
| D-4 | The cadence sentence and whether the site shows a "next issue expected" date and a "late" label | Yes, and the owner writes the sentence. A promised date is a commitment, so it must be his. |
| D-5 | A writing rule for future issues: the read is written for someone who has never seen the site | Yes |
| D-6 | Retire Archivo, restyle the three dark panels light | Yes |

Keyboard shortcuts for next, previous and thesis (D7 L5-4) are left out on purpose.
Single-character shortcuts bring a WCAG obligation to let readers turn them off or remap them
(SC 2.1.4), and that is more machinery than one rubric test is worth today. A command palette is
left out for the same reason. Both are recorded for the backlog.

## 12. The strongest case against this design

Written before the adversarial pass; section 13 records what that pass added.

Presentation is not what is holding this project back. One issue has been signed, thirteen days
after its week ended, the gather runtime does not work, and one person has had a real chance to
use the work. A beautiful first screen on a site that publishes once and stops is worse than the
current one, because it makes a promise of cadence in a louder voice. Every hour the owner spends
reviewing previews of this design is an hour not spent on the two things only he can do: choose
the gather runtime and name the pilot list. If those two do not happen, this design will score in
the seventies and mean nothing.

The answer the design gives: it is built to stay honest if cadence fails. The issue line shows
both dates, the "late" label appears on its own, the ledger shows its single row, and the rubric's
cadence cap takes points away after fourteen days. The design does not fix cadence and does not
claim to.

## 13. Adversarial pass

To be completed after task T3-3.
