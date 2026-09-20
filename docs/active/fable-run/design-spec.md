# Design specification — Security Market Pulse

**Artifact ID:** `SEC-MARKET-FABLE-DESIGN` v0.2 (proposal, awaiting owner acceptance)
**Written by:** the run coordinator, 2026-09-20. v0.2 is v0.1 revised after the adversarial pass
(`consults/adversarial-pass.md`); section 13 lists what changed and why.
**Built on:** `site-rubric.md` v1.2, `score-baseline.md` (composite 33.0, exposure denominator 1),
`research-synthesis.md`, `codebase-map.md`, `research/08-thesis-history-inventory.md`
**Status:** nothing in this document has been built. Phase 4 starts only after the owner accepts it.

## 1. The design in one paragraph

The site already contains a good argument. It is in the wrong order. The signed judgment, what
changed, what to do and avoid, what the site refuses to call, and the four conditions that would
change the call all exist today, well written, between 4,700 and 7,000 pixels down a 15,000 pixel
page, underneath twenty-three funding and filing cards. This design moves the argument to the top.
That part is small, needs no new route and no new data, and is proposed as **wave 1**. The larger
part (rows for cards, a page of its own for the thesis that grows one line per signed issue, a
method page, one typeface, no dark panels) is proposed as **wave 2**, to start only after a second
issue has been signed, because a thesis ledger and a redesign are worth little on a site that has
published once. Section 11 gives the owner the choice between the full build, the two waves, and
wave 1 alone.

## 2. Principles

1. **Argument before inventory.** A security leader came for the read. The tracked items are the
   evidence for the read and sit below it.
2. **The thesis is a standing object, the issue is a weekly event.** They look different and are
   never confused on screen.
3. **The thesis sentence never travels alone.** Wherever it appears, for a person or a machine, it
   sits with its verdict, confidence, signer, date and what it does not claim. Intent requires
   claims to keep their uncertainty.
4. **Honest at small scale.** One signed issue exists. Every history surface shows one row and
   says so.
5. **Rows, tables and plain labels.** Linear's restraint, Zed's density. One accent. Light only.
6. **Accessibility is the thing to protect.** The site scores 4 of 5 today with zero axe
   violations. Every stream re-runs the measurements in `evidence/baseline/measure/` before merge.
7. **Keep the gates green.** Section 9.

## 3. The first screen

The first screen is the first viewport with no scrolling, at 1440 by 900 and at 390 by 844. The
reading order is the same at both widths.

### 3.1 What goes in it, with the real strings

| Block | Exact text today | Size | Lines at 1440 (left 7 columns, about 730 px; right 5, about 500 px) | Lines at 390 |
|---|---|---|---|---|
| Descriptor | New copy, owner edits: "A weekly signed read on where security spending is actually moving, for security leaders and the teams who advise them. Public sources only." | 16px | 2 | 4 |
| Issue line | "ISSUE 2026-W36 · WEEK ENDING 6 SEP 2026 · PUBLISHED 19 SEP 2026" (exists) | 12px mono | 1 | 2 |
| Label and h1 | "Record earnings from CrowdStrike, Zscaler, Palo Alto, Rubrik and NVIDIA meet thin VC and quiet M&A — the infra-to-security lag call holds." (138 characters, locked) | 32px / 24px | 4 | 6 |
| Gloss | New site-level annotation: "The lag call is this site's refusal to claim that infrastructure spending leads security spending by a fixed interval." | 14px | 2 | 3 |
| Thesis label | "STANDING THESIS" | 12px mono | 1 | 1 |
| Thesis | "Infrastructure is running ahead. Security is splitting, not booming." (68 characters) | 24px / 20px | 2 | 3 |
| Verdict line | "HOLDS · medium confidence · judged 19 Sep 2026 by Jesse Pike" | 14px | 1 to 2 | 2 |
| Running score | "Held in 1 of 1 signed issues", linked to the issue | 14px | 1 | 1 |
| Does not claim | "Does not claim: a stable 0 to 8 quarter infrastructure-to-security lag." (first of four boundaries, from `marketCall.noCallBoundaries`) | 14px | 2 | 2 |

Estimated height at 1440: header region, then about 60 (descriptor) + 30 (issue line) + 190 (h1
block with gloss) on the left and about 260 on the right, which fits beside the h1. It fits in 900
with room to spare. At 390 the blocks stack to roughly 640 to 700 pixels under the chrome, which is
tight. **These are estimates from character counts.** The first task of the build is a rendered
prototype of this screen at both widths with the real strings, measured, and the owner approves
the first screen from that render and not from this table.

**Moved below the fold since v0.1:** the four change conditions. Their real text runs 64 to 103
characters each and does not fit the panel without truncating, and a truncated condition is not a
visible condition. They sit in full directly under the first screen, in the standing call, where
rubric D2 L3-3 still passes. "Since the last issue" also sits there.

```
1440                                                   390
+---------------------------------------------------+  +----------------------+
| provenance rail (existing)                        |  | rail (existing)      |
| header: brand · nav                               |  | header: brand · Menu |
+---------------------------------------------------+  +----------------------+
| Descriptor, two lines                             |  | Descriptor           |
| ISSUE 2026-W36 · WEEK ENDING ... · PUBLISHED ...  |  | Issue line           |
|                                                   |  | THIS WEEK'S READ     |
| THIS WEEK'S READ         | STANDING THESIS        |  | h1, six lines        |
| h1, four lines           | Infrastructure is      |  | gloss                |
|                          | running ahead. ...     |  | STANDING THESIS      |
| gloss, two lines         | HOLDS · medium · date  |  | thesis, three lines  |
|                          | Held in 1 of 1 ->      |  | HOLDS · medium · ... |
|                          | Does not claim: ...    |  | Held in 1 of 1 ->    |
+---------------------------------------------------+  | Does not claim: ...  |
                                                       +----------------------+
```

### 3.2 Site chrome on phones

Chrome at 390 is 221 pixels today, 26.2 percent of the viewport, and the rubric asks for a quarter
or less (211). The chrome is two things: the provenance rail, about 90 pixels, which carries the
"as of" date and the tracked-versus-judged legend, and the header, which carries the brand, a
second date stamp and the Menu control. **The rail stays.** It is the legend that rubric D5 L3-3
depends on. The proposal is only to drop the header's date stamp at 390, because the rail shows the
same date directly above it. That brings chrome to about 138 pixels, 16 percent. It removes a
visible element, so it is its own owner decision, D-7. v0.1 claimed 48 pixels; that figure was
wrong, because it could only be reached by deleting the rail, which v0.1 never said.

### 3.3 Two states: the newest issue is signed, or it is a draft

Production always shows a signed newest issue, because `verify-issue` refuses to build `main` with
a draft on top. The `preview` trunk often will not: a draft of `2026-w37` already exists on the
branch `issue/2026-w37`. So every thesis surface reads from the **newest published issue**, never
from the newest issue.

| | Newest is signed | Newest is a draft (preview only) |
|---|---|---|
| Issue line and h1 | The signed issue | The draft, with the existing "Draft. Not yet signed." banner, unchanged |
| Thesis block | Verdict, confidence, signer and date from this issue | The same fields from the last signed issue, labelled "as judged in issue 2026-w36" |
| Running score | Counts published issues | Counts published issues |

### 3.4 The jargon problem

The locked headline of 2026-w36 ends "the infra-to-security lag call holds". That is internal
language and fails D1 L3-3. Published text is hash-locked and is not edited. The gloss in 3.1 is a
site-level annotation rendered beside the headline from a small term list; it is not part of the
issue, does not enter the issue JSON, and the permalink labels it "Note added by the site, not part
of the signed issue". The lasting fix is a writing rule for future issues, decision D-5.

## 4. The rest of the front page

### 4.1 Order

| # | Section | id (unchanged) | Change | Wave |
|---|---|---|---|---|
| 1 | First screen | `overview` | Descriptor, gloss and a compact thesis block added | 1 |
| 2 | The signed judgment | `we-think` | Moves up from y=5,137 to directly under the first screen. Target: signature above y=1,800 at 1440 and y=1,700 at 390 | 1 |
| 3 | The standing call: what changed, do, avoid, will not call, would change the call | `read` | Moves up with it | 1 |
| 4 | Follow line | new, `follow` | One sentence and a visible feed link, after the judgment | 1 |
| 5 | Domain postures | `landscape` | Order only in wave 1. Six cards become one table in wave 2 | 1, 2 |
| 6 | Vendor filter | `vendor-lens-slot` | Moves to the head of the lanes it filters. Class names unchanged | 2 |
| 7 | The four lanes | `formation`, `absorption`, `prints-this-week`, `capital` | Below the argument in wave 1. Cards become rows in wave 2 | 1, 2 |
| 8 | Platform pressure, hypotheses, prints | `platforms`, `hypotheses`, `prints` | Order kept | none |
| 9 | Depth sections | `moved-depth`, `research-depth`, `layers`, `watch`, `method`, `research` | Stay closed. Summary text unchanged, because the smoke test asserts it | none |
| 10 | Corrections and contact | `next` | Kept. It is the block that says "If a figure is wrong, send it". See section 5 on keeping one corrections statement | none |

No gate or test asserts section order; the adversarial pass checked `prerender.ts`, the three e2e
specs and `verify-issue.ts` and confirmed it. Nothing here puts a required section inside a closed
one.

**Height.** Wave 1 puts the judgment, the change conditions and the postures inside about 3,500
pixels at 1440. The week's evidence (the lanes, still cards) follows and runs to roughly 8,000.
Rubric v1.2 D4 L5-1 asks for everything essential inside 5,000 pixels; that passes only in wave 2,
when the lanes shrink from about 4,000 pixels to about 1,300.

### 4.2 Lane rows (wave 2)

One row per tracked item. The class names `.issue-lane__item` and `.issue-lane__headline` stay,
because `tests/e2e/lens.spec.ts` selects on them, and one element per item stays, because
`verify-issue` check 10 counts them.

```
1440:  06 SEP   Headline that states the fact, up to 110 characters            FILING   Source ›   #
                Why it matters, one sentence, 14px, muted
 390:  06 SEP · FILING · Source ›
       Headline that states the fact
       Why it matters
```

- About 64 pixels a row at 1440, so a lane of eight fits one screen (D6 L3-1, L5-4). About 150 at
  390.
- The evidentiary kind from `EvidenceRecord.sourceClass` is shown on the row, not only inside the
  evidence panel (D5 L5-1).
- The source control is the existing chip and opens the existing panel. Targets stay at least 24
  by 24 pixels.
- Each row gets `id={item.id}`. The ids already exist in the data. The adversarial pass confirmed
  this creates no duplicate ids, because the front page and the permalink are separate routes.
- **Ordering by consequence is not in this design.** It needs a new field on the issue item, the
  issue model belongs to `weekly-issue-spec.md` under SEC-027, and the brief puts that outside this
  run. So rubric tests D4 L3-3 and D6 L3-2 keep failing, and D4 and D6 stay at 2 until SEC-027
  takes it up. This is recorded for the backlog and is the largest single score left on the table,
  about eight composite points.

### 4.3 The evidence panel (wave 2)

Left alone apart from two additions: the retrieved date, already in the data as `retrievedAt`, and
a "Report a problem with this source" mail link carrying the evidence id (D5 L5-2, L5-4).

## 5. The thesis surface, and how it accumulates (wave 2)

A new route, `/thesis/`: the stable address for the argument (D1 L5-2) and the one place the whole
history sits in order (D2 L5-2). The front page anchor `/#read` stays alive.

| Block | Content | Source | Accumulates how |
|---|---|---|---|
| Statement | The thesis with its verdict, confidence, signer and date, then a plain paragraph on what it means | `marketCall.headline`, `.meaning`, `.confidenceNote`, newest published `weThink.thesis` | Changes only when the owner changes the standing call |
| Does not claim | The four no-call boundaries | `marketCall.noCallBoundaries` | Same |
| Verdict ledger | Table, newest first: issue, week ending, verdict, confidence, one-line basis, signed by, link | Derived from every published issue | **One new row per signed issue, with no extra work** |
| Change conditions | The four conditions in full, each with a current status and an "as of" date | `marketCall.changeTriggers`, plus decision D-3 | The owner updates the status when he signs |
| Earlier record | The three unsigned edition records of 16, 17 and 28 August, labelled "unsigned edition record" | `src/data/edition.ts`, rendered today in a closed section | Closed history |
| How scoring works | What holds, strengthens, weakens and no-call mean; how "held in N of M" is computed | New method copy from `issueHelpers.ts` lines 62 to 91 | Static |
| Calibration | One honest statement that the thesis has no resolution date yet, so there is nothing to calibrate against | New copy, owner edits | Becomes a table later |
| Corrections | A dated list at `/thesis/#corrections`, "None to date." today | New empty data file | One entry per correction |

**One corrections statement, one address.** The front page block `#next` says today "There is no
form and no list." When the list exists, that sentence changes to point at it; the owner approves
the wording on the preview. The site never says both.

**D-3, restated after the adversarial pass.** v0.1 put condition statuses on the issue's judgment.
That was wrong twice: it changes the issue model that SEC-027 owns, and it cannot apply to the
locked 2026-w36, so the first screen would have shown statuses that do not exist. The statuses now
live on the standing call in `web/src/data/market.ts`, beside the conditions themselves, as a
current status and a date. No issue field, no lock question. A status is a market judgment, so the
owner sets each one himself and nothing is shown until he has; the build ships the field empty and
the page omits the column while it is empty.

The permalink becomes the immutable record of one week: it says so under its header, links the
lock manifest and the previous and next issues, and when it is not the newest says "This is a past
issue. The newest is <link>."

## 6. Information architecture and navigation (wave 2)

| Route | Status | Purpose |
|---|---|---|
| `/` | exists, reordered in wave 1 | The current state of the argument, then this week's evidence |
| `/thesis/` | new | The standing thesis, its verdict ledger, corrections |
| `/issues/` | exists | The archive. Gains verdict and confidence columns (D7 L3-1) |
| `/issues/<id>/` | exists | The immutable record. Gains previous and next, the past-issue line, the lock link |
| `/method/` | new, decision D-2 | How evidence becomes a call, who the author is, boundaries, independence, machine access, terms |

A new route is not discovered automatically. The build must widen `RouteKind` and the route table
in `src/data/routes.ts`, add the route's ids to `MUST_SEE_SECTION_IDS` in `scripts/prerender.ts`,
and add a branch in `scripts/generate-seo.ts` (near lines 145 and 158), or the new page silently
inherits the front page's JSON-LD. `tests/e2e/issue.spec.ts` lines 92 to 106 assert that "Thesis"
navigates to `/#read` and must be changed on purpose.

## 7. Type and colour (wave 2)

**Type.** IBM Plex Sans for prose and headings, IBM Plex Mono for dates, ids, amounts and labels.
Archivo is retired (D-6). Both families self-hosted as subset `woff2` with `font-display: swap`,
which removes the render-blocking request to Google Fonts. Six sizes on the front page: 12 mono,
14, 16, 20, 24, 32, against more than seventeen declared today. No continuous reading text under
14 pixels.

**Colour.** The existing neutral scale stays. One accent, the existing teal `#0b6b5e`, for links,
focus and the current verdict. Verdict and posture states are told apart by their word, weight and
border, so a greyscale capture still reads. The three dark panels (the provenance rail, the thesis
block, the posture block) become light surfaces with a strong one pixel border. Non-text contrast
is sampled for the first time, because D10 L5-6 fails today only as "not measured".

## 8. What gets removed or moved

Removing a visible page element is an owner gate. Nothing below happens without a yes, and each is
proven with a before and after render, never by static analysis. No component, stylesheet rule or
data export is deleted in this run.

| Item | Proposal | Wave | Decision | Tests it breaks, to be changed on purpose |
|---|---|---|---|---|
| Header date stamp at 390 | Remove at phone width; the rail shows the same date | 1 | D-7 | none found |
| The sentence "Refresh is manual... Not a weekly news cycle", `src/components/HowThisWorks.tsx` lines 23 to 24 | Replace with a cadence sentence the owner writes | 1 | D-4 | none |
| Method section and methodology note on the front page | Move to `/method/`, leave a three-line summary and a link | 2 | D-2 | `smoke.spec.ts` line 38 asserts `#method summary` reads "How this is built" |
| Dark backgrounds on three panels | Restyle light | 2 | D-6 | none found |
| Archivo typeface | Retire | 2 | D-6 | none |
| Lane cards | Become rows | 2 | D-1 | none if class names are kept |
| Domain cards | Become one table | 2 | D-1 | `smoke.spec.ts` lines 35 to 37 select `.landscape .evidence-link`; keep the class |

## 9. Constraints the build must respect

- The prerender must-see gate: the eleven front-page ids exist and none sits inside a `details`
  element. Presence only, not order.
- `verify-issue` check 10 server-renders the hero, the lanes and the judgment and asserts per-lane
  item counts, the exact signature text and the draft banner on a draft.
- `tests/e2e/smoke.spec.ts`: the summary text of `#moved-depth`, `#method` and `#research-depth`,
  the id `#market-call-heading`, `.landscape .evidence-link` contents, and the evidence dialog.
- `tests/e2e/lens.spec.ts`: `.issue-lane__headline`, `.print-card h3`, "Showing N of M", and the
  horizontal scroll of `.vendor-lens__chips`.
- The lock manifest hashes `JSON.stringify(issue)`. The adversarial pass confirmed an optional
  field that is undefined on a locked issue changes neither the hash nor the `verify-dist` equality
  check. This design adds no issue fields anyway.
- The OG image staleness gate ties `assets-src/og.svg` to `marketCall.headline`.
- Hydration parity is by convention only. Everything derived ("since the last issue", the ledger,
  the running score) comes from data available to both renders. **Nothing reads the clock.** For
  that reason there is no "late" label: a static site with no scheduler cannot compute lateness at
  build time, and computing it in the browser would be invisible to machine readers and break the
  no-clock rule. Rubric D3 L5-1 is accepted as not achievable here.
- **Branching.** A draft `2026-w37` is on `issue/2026-w37` and touches `web/src/data/evidence.ts`,
  `issues/2026-w37.ts` and `issues/index.ts`. No stream in this run edits anything under
  `web/src/data/issues/` or `evidence.ts`. Phase 4 branches from `preview` after that issue has
  landed, or from a named commit the owner picks, and re-captures the baseline screens first if
  the newest issue has changed.
- All node, npm, build, test and capture commands run in the OrbStack dev VM. Captures use
  `evidence/baseline/capture.mjs`, because `web/scripts/shot.mjs` needs Google Chrome, which the
  VM does not have.

## 10. What this should do to the score

A projection, which is a guess until Phase 5 measures it with two blind scorers. The same agent
wrote the rubric and the design, which is a reason to distrust these numbers; the re-score uses an
independent scorer for that reason. Each cell is score, then points (score ÷ 5 × weight).

| Dimension (weight) | Now | Wave 1 only | Waves 1 and 2 | What holds it back |
|---|---|---|---|---|
| D1 Thesis clarity (12) | 0 / 0.0 | 4 to 5 / 9.6 to 12.0 | 4 to 5 / 9.6 to 12.0 | The cold-reader test |
| D2 Thesis development (12) | 2 / 4.8 | 3 / 7.2 | 4 to 5 / 9.6 to 12.0 | 5 needs the owner's condition statuses (D-3) |
| D3 Reason to return (10) | 1 / 2.0 | 3 to 4 / 6.0 to 8.0 | 4 / 8.0 | No "late" label. Cadence cap from 2026-10-04 |
| D4 First screen (12) | 1 / 2.4 | 2 / 4.8 | 2 / 4.8 | Consequence ordering belongs to SEC-027 |
| D5 Evidence (8) | 3 / 4.8 | 3 / 4.8 | 4 / 6.4 | |
| D6 Density (8) | 2 / 3.2 | 2 / 3.2 | 2 / 3.2 | Same SEC-027 dependency |
| D7 Wayfinding (5) | 1 / 1.0 | 1 / 1.0 | 4 / 4.0 | |
| D8 Agent legibility (10) | 2 / 4.0 | 3 / 6.0 | 4 to 5 / 8.0 to 10.0 | 5 needs a crawler policy and terms from the owner |
| D9 Performance (5) | 2 / 2.0 | 2 / 2.0 | 2 / 2.0 | Self-hosted fonts may help first paint; not counted |
| D10 Accessibility (7) | 4 / 5.6 | 4 / 5.6 | 4 to 5 / 5.6 to 7.0 | |
| D11 Conversion (3) | 0 / 0.0 | 3 / 1.8 | 3 / 1.8 | |
| D12 Trust (5) | 2 / 2.0 | 2 / 2.0 | 4 to 5 / 4.0 to 5.0 | |
| D13 Craft (3) | 2 / 1.2 | 2 / 1.2 | 3 to 4 / 1.8 to 2.4 | |
| **Composite** | **33.0** | **55.2 to 59.6** | **68.8 to 78.6** | |

If SEC-027 later adds consequence ordering, D4 and D6 can each reach 4, worth eight more points.
The cadence cap holds D3 at 2 from 2026-10-04 if no further issue is signed, which costs four to
six points in either column. **The exposure denominator is 1 in every column.** None of this
changes who has read the work.

## 11. Decisions this document needs from the owner

**First, the size of Phase 4.**

| Option | What is built | Review cost to the owner | Recommendation |
|---|---|---|---|
| A. The brief as written | Everything in this document and the agent-surface spec, in five parallel worktrees, now | Five previews | No |
| **B. Two waves** | Wave 1 now, in one worktree: the reorder, the compact thesis block, the descriptor, the gloss, the cadence sentence, the follow line and feed link, the phone chrome fix, and the wave 1 items of the agent-surface spec. Wave 2 (everything else) starts when a second issue has been signed | One preview now, two or three later | **Yes** |
| C. Wave 1 only | As B, and the rest is dropped until four issues have been signed and the owner asks again | One preview | The adversarial reviewer's choice. Reasonable |

B over C because building is cheap and a second signed issue is real evidence the cadence is alive;
waiting for four adds a month and tells little more. B over A because the owner's review time is
the scarce thing, and it is better spent on the gather runtime and the pilot list than on five
previews of a site that has published once.

| # | Decision | Wave | Recommendation |
|---|---|---|---|
| D-1 | Accept the first-screen contents (3.1) and the front-page order (4.1), subject to approving the rendered prototype | 1 | Yes |
| D-4 | The owner writes the cadence sentence that replaces "Not a weekly news cycle". No "next issue expected" date and no "late" label | 1 | Yes |
| D-5 | A writing rule for future issues: the read is written for someone who has never seen the site. This is guidance to the signer, not a change to the pipeline | 1 | Yes |
| D-7 | Remove the header date stamp at phone width | 1 | Yes |
| D-2 | Move the method section to `/method/` | 2 | Yes |
| D-3 | A current status and date for each change condition, held on the standing call in `market.ts`, set by the owner | 2 | Yes. Without it, a week where the verdict holds shows no movement |
| D-6 | Retire Archivo; restyle the three dark panels light | 2 | Yes |

Left out on purpose and recorded for the backlog: consequence ordering of lane items (SEC-027),
keyboard shortcuts (single-character shortcuts bring a WCAG 2.1.4 obligation to let readers turn
them off), a command palette, and a "late issue" label.

One thing outside this design that the owner should know: `.claude/rules/constraints.md` line 19
still says the website is "not authorized", while `intent.md` has listed it as decided since
2026-08-16 and it has been live throughout. This run does not edit rules files. The line needs the
owner's amendment.

## 12. The strongest case against this design

Presentation is not what is holding this project back. One issue has been signed, thirteen days
after its week ended, the gather runtime does not work, and one person has had a real chance to
use the work. The run's own research synthesis says all of this is decoration if the cadence does
not start. A better first screen on a site that publishes once and stops makes a promise of
cadence in a louder voice, and every hour the owner spends reviewing previews is an hour not spent
on the two things only he can do.

v0.1 answered this by saying the design "stays honest if cadence fails" because a "late" label
would appear on its own. The adversarial pass showed that label cannot work on a static site, so
that answer is withdrawn. What remains is weaker and true: both dates are on the issue line, the
ledger shows its one row, and the rubric takes points away after fourteen days without an issue.
The design does not fix cadence and cannot. That is the reason for the two waves: spend little
now, and spend the rest only once a second issue proves the cadence exists.

## 13. Adversarial pass: what changed and what survived

Task T3-3, `claude-opus-5`, `consults/adversarial-pass.md`, sixteen findings. The coordinator
checked the five most load-bearing factual claims against the code before accepting them (the
`issue/2026-w37` branch, the provenance rail in `App.tsx`, `smoke.spec.ts` line 38, the text of
`NextEdition.tsx`, `constraints.md` line 19). All five were correct.

| # | Finding | Outcome |
|---|---|---|
| 1 | A draft 2026-w37 exists and the design assumed a signed newest issue | Accepted. Section 3.3, the branching rule in section 9. One correction to the finding: production can never show a draft, so this affects previews and merges, not the live first screen |
| 2 | The run is aimed at the wrong problem; keep about a quarter | Accepted in substance. Section 11 now offers the quarter as wave 1 and recommends two waves |
| 3 | D-3 changed the issue model and showed statuses that could not exist | Accepted. Statuses move to `market.ts`; the `lead` field is dropped |
| 4 | The 48 pixel chrome figure needed two undisclosed deletions | Accepted. The rail stays; the figure is 138; the date stamp is decision D-7 |
| 5 | The wireframe used invented copy | Accepted. Section 3.1 uses the real strings, moves the conditions below the fold, and makes a measured prototype the first build task |
| 6 | The "late" label cannot work | Accepted. Dropped, and section 12 rewritten |
| 7 | The composite did not reconcile with its table; D9 at 3 not credible | Accepted. Section 10 recomputed with the arithmetic shown; D9 held at 2 |
| 8 | Rubric D4 L5-1 was unpassable ("whichever is smaller") | Accepted. Rubric v1.2 makes it a flat 5,000 pixels. The baseline score does not change, because D4 fails at level 3 |
| 9 | Section 9 missed the one assertion D-2 breaks, and two file pointers were wrong | Accepted. Sections 6, 8 and 9 corrected |
| 14 | Two corrections surfaces would contradict each other | Accepted. Section 5 |
| 10 to 13, 15 | Employment question, consult provenance, crawler and terms, the bare thesis string, Markdown negotiation | Handled in `monetization-plan.md` and `agent-surface-spec.md` |

**What the reviewer tried to break and could not:** the lock hash is safe from optional fields;
no gate asserts section order; item ids on rows create no duplicates; the diagnosis (the judgment
at y=5,137, three unlinked JSON files, the one contradicting sentence) is right; the honesty at
small scale rule is applied and no padding was found.
