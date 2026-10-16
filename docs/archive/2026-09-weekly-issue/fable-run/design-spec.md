# Design specification — Security Market Pulse

**Artifact ID:** `SEC-MARKET-FABLE-DESIGN` v0.4
**Written by:** the run coordinator, 2026-09-20.
**Governing document:** `docs/archive/2026-09-weekly-issue/product-core.md`. v0.3 replaces v0.2 because the owner
restated what the site is for: a practitioner's market pulse for people who run security programs,
with the founding thesis as one standing analysis. v0.2 (git history) put a thesis panel on the
first screen; that is withdrawn. What v0.2 got right and still holds is carried over and marked.
**Built on:** `site-rubric.md` v2.1, `consults/external-review-astra.md`, `content-inventory.md`, `codebase-map.md`,
`consults/adversarial-pass.md`.
**Authorization:** the owner said to build. Everything lands on `preview`. Promotion to production
needs his explicit word.

## 1. The design in one paragraph

A security leader should land on the site and see, without scrolling far, what it is, this
period's read of the market, and a picture of each security domain: the owner's stance on it, and what each tracked supplier in it
last reported, with the evidence behind each figure. Below that: what happened this period,
most consequential first. Below that: the standing analyses, of which the infrastructure-and-
security thesis is one, labelled for the advisors and partner teams who care about it. Every
figure says what it measures, where it came from and how old it is. Nothing is ranked by a
machine, and nothing a machine assembled is presented as the owner's opinion.

## 2. Principles

1. **Market picture before inventory, inventory before analysis.** The reader is a security
   leader first.
2. **Tracked and judged never blur.** The supplier table is tracked fact, alphabetical, and says
   so in its caption: the metrics differ, nothing is ranked, and listing is not a recommendation.
   A stance on a domain is the owner's judgment and carries his name and date.
3. **Every number carries its kind, its period and its date** on the row, not only in a panel.
4. **Honest about gaps and age.** A domain with no comparable public growth figures says so. A
   judgment made five weeks ago shows that date, not the build date.
5. **Plain words.** Site copy a security leader would not understand is rewritten. Text inside a
   published issue is locked and gets a plain-words note beside it.
6. **Accessibility is protected** (zero axe violations today), and **the gates stay green**
   (section 7).

## 3. The front page

### 3.1 Order

| # | Section | id | What changes | Step |
|---|---|---|---|---|
| 1 | What this is, and this period's read | `overview` | New one-line description of the site (section 3.2). The as-of line. The read as the h1, with a plain-words note when it uses a term of art. A small visible feed link | A |
| 2 | **The market by domain** | new, `market` | New component, section 3.3. The centre of the page | A |
| 3 | What we think this period | `we-think` | Moves up from y=5,137 to directly under the market picture | A |
| 4 | What happened this period: the four lanes | `formation`, `absorption`, `prints-this-week`, `capital` | Section headings in plain words (3.5). Cards become rows | A headings, B rows |
| 5 | Follow | new, `follow` | One sentence, what arrives and how often, with the feed link | A |
| 6 | Domain detail | `landscape` | Unchanged content, now the drill-down under the market picture | none |
| 7 | Platform moves, prints, vendor filter | `platforms`, `vendor-lens-slot`, `prints` | Order kept | none |
| 8 | **Standing analysis: infrastructure and security spending** | `read` | Moves down from the second position. A label says who it is for. Content unchanged | A |
| 9 | Hypotheses | `hypotheses` | Follows the analysis it belongs to | A |
| 10 | Depth sections, corrections and contact | unchanged | Unchanged | none |

Every id the prerender must-see gate requires still exists and none moves inside a closed
section. No gate or test asserts section order (checked by the adversarial pass).

### 3.2 The description line (new copy, the owner edits it on the preview)

> A practitioner's read on the business of the security market: who is growing, who is
> consolidating, who is being bought, and what it means if you run a security program. Public
> sources only. Written by Jesse Pike.

It goes in `src/data/meta.ts` and is reused for the page description and the machine surface.

### 3.3 The market by domain (new component `MarketPicture`)

One table, six rows, built only from data that exists. **Changed in v0.4 after the external
review: vendors are listed alphabetically and are not ranked.** v0.3 ordered a top three by
reported growth. Growth percentages here sit on different bases (a small company can grow faster
while adding less revenue; acquisitions, hardware cycles and changed definitions move the number),
so ordering by them implies a comparison the data cannot support, and for an author who works at a
reseller of these vendors a ranked list reads as his endorsement whatever the caption says.

| Column | Source | Tracked or judged |
|---|---|---|
| Domain | `domains.ts` | n/a |
| Stance, in plain words, with its horizon and the date it was judged | `domains.ts` `posture`, `tag`, `horizon`, `asOf` | **Judged.** The owner's name and the date. This is where "who is winning" belongs, because it is his call |
| Tracked suppliers and what they last reported: every vendor with a comparable public figure, alphabetical, each with the figure, the exact metric, the period, a "product line, not the whole company" tag where that applies, the earlier figure for the same metric where one exists, and the existing source control | `prints.ts`, only records whose `surface` is `print` | **Tracked.** Not ordered by size |

Caption, always visible: "These are figures the companies themselves reported, listed
alphabetically. They measure different things over different periods, so they are labelled and not
ranked. Being listed is not a recommendation, and being absent is not a criticism. Private
companies that publish no comparable figures are tracked through funding and acquisitions
instead."

No direction arrow or "accelerating" wording appears unless two records carry the identical metric
label. A figure more than 120 days old is marked "older figure". Cloud Security and AI Runtime say
plainly that no comparable public figures exist yet, with a link to their funding and acquisition
records. At 390 the table becomes one block per domain, same content, same order. Each domain row
gets `id="domain-<id>"` and each vendor entry a unique `id`, so a colleague can be sent a link to
one domain.

### 3.4 Freshness, shown honestly

The header badge says "September 19, 2026" because the site rebuilt that day, while the domain
stances were last judged on 16 August. The as-of line shows both, from constants that already
exist in `meta.ts`: "Updated 19 Sep 2026. Domain stances judged 16 Aug 2026." Each vendor figure
shows its own period. A figure more than 120 days old is marked "older figure"; quarterly results
are legitimately months old, so a shorter threshold would cry wolf.

### 3.5 Plain words for site copy

| Today | Becomes | Where |
|---|---|---|
| Formation | New companies and funding | lane heading (site copy) |
| Absorption | Acquisitions and consolidation | lane heading |
| Prints this week | Earnings and reported numbers | lane heading |
| Capital | Capital and financial position | lane heading |
| PREPARE, INVESTIGATE, WATCH | kept, each with a one-line meaning beside its first use | domain stance |
| "the lag call" | note beside the locked headline: "The lag call is this site's refusal to claim that infrastructure spending leads security spending by a fixed interval." | beside the h1 |
| "Refresh is manual... Not a weekly news cycle" | "Tracked figures are updated as companies report. A signed read is published most weeks." The owner edits this | `src/components/HowThisWorks.tsx` lines 23 to 24 |

The lane `id`s and class names do not change, only the visible heading text. The full jargon list
is in `content-inventory.md` section 7; anything not in this table waits.

## 4. Step B: rows, and fresher vendor figures

**Rows for lane cards**, as specified in v0.2 section 4.2 and unchanged: one element per item,
class names `.issue-lane__item` and `.issue-lane__headline` kept for `lens.spec.ts`, the source
class shown on the row, `id={item.id}` on each row, targets at least 24 by 24 pixels.

**Fresher vendor figures: held, not built today.** The content inventory found the vendor
scorecard (`prints.ts`) showing April to June figures for six vendors while the signed issue of
19 September reports later figures for the same companies. v0.3 proposed copying the newer figures
into the scorecard. The external review checked the sources and found that is not safe to do
mechanically: the signed issue's own headlines call two quarterly revenue figures full-year
figures (Zscaler "FY2026 revenue grows to \.2M" and Palo Alto "FY2026 revenue grows 34% to
\.41B", where the cited evidence records are fourth-quarter results), and the older Zscaler entry
is organic ARR growth while the newer one is total ARR growth, so the two cannot be read as a trend.
A number appearing in a source is not enough; the company or segment, the metric definition, the
period, the units and the acquisition treatment have to be validated together. That validation is
specified in the automation plan and the refresh waits for it. Until then the market table marks
older figures as older.

**A correction the owner needs to see.** Those two headlines are in a published, hash-locked
issue under his signature. They cannot be edited. The right remedy is a dated correction entry,
which he approves. It is listed in the owner packet.

The longer fix is architectural: the weekly pipeline should write its figures back into the
scorecard so the two never drift. That belongs to the automation plan.

## 5. What is not in this build

| Item | Why | Where it is recorded |
|---|---|---|
| Distress signals (debt, downgrades, layoffs, shutdowns) | No such data exists yet, and reporting it safely needs a sourcing method first | `research/11-distress-signal-sources.md`, product core question 12 |
| "What this means if you run a security program" | The existing do and avoid lists are written for account teams. Advice for a security leader is new judgment that the owner has to write or approve | product core question 8 |
| A page per standing analysis with its record, a method page, one typeface, light panels | v0.2 wave 2. Still right, less urgent than the market picture | v0.2 in git history |
| The full machine surface | `agent-surface-spec.md`; links to existing data files are in step A | same |
| Ordering lane items by consequence | Needs a field on the issue model (SEC-027) | backlog |
| A section about the owner | He raised it and was unsure | product core question 13 |
| Analytics | Recommendation ready (`research/12-analytics-options.md`); adding a third-party script and a paid service is his decision | product core question 14 |

## 6. Step A machine links (from `agent-surface-spec.md`, unchanged)

Visible and `rel="alternate"` links to `/issues/index.json`, the newest issue's JSON and
`/issues/lock.json`; the same three in the sitemap; a visible feed link; `author` and dates on the
archive page's JSON-LD. `robots.txt` is not touched.

## 7. Constraints the build must respect

Carried from v0.2 section 9, all still true: the must-see ids and the no-`details`-ancestor rule;
`verify-issue` check 10 (one element per lane item, exact signature text, draft banner on a
draft); `smoke.spec.ts` (summary texts of `#moved-depth`, `#method`, `#research-depth`; the id
`#market-call-heading`; `.landscape .evidence-link` contents; the evidence dialog);
`lens.spec.ts` selectors; `issue.spec.ts` (the permalink's "Thesis" link goes to `/#read`, which
still exists); the OG image gate tied to `marketCall.headline`; nothing reads the clock during
render; no edits under `web/src/data/issues/` or to `web/src/data/evidence.ts`; every thesis or
verdict surface reads the newest **published** issue; all node work in the OrbStack dev VM;
captures with `evidence/baseline/capture.mjs`.

## 8. Expected effect on the score (rubric v2.0)

A guess until two blind scorers measure it. The v2.0 baseline is in `score-baseline-v2.md`.
Step A should pass D1's four level-3 tests and two or three of its level-5 tests, D3's first four
level-3 tests, D4 level-3 tests 1, 2 and 4 and level-5 tests 1 and 3, D11's three level-3 tests,
and D8's level-3 set. Step B adds D6 level-3 test 1 and D2 level-3 test 2. D4 level-3 test 3
(consequence ordering) still fails, so D4 cannot pass 2 until SEC-027 allows a lead marker. The
exposure figure stays at 1.

## 9. The strongest case against this design

The market picture is only as good as `prints.ts`, which a person last reviewed as a set on
16 August and which no job updates. Putting a vendor table at the top of the page makes the
stalest data on the site its most prominent feature. If the automation does not follow quickly,
the table will be visibly old within weeks, in front of exactly the readers the owner wants to
impress. The design answers this only partly: every figure shows its period and age, and step B
brings six vendors up to date. The real answer is the automation plan, and the owner has said the
same thing: do not promote the site until it updates itself reliably.

A second risk: a table of vendors ordered by growth, published by someone who works for a
reseller of those vendors, will be read by some as his ranking however it is captioned. The
caption, the tracked label and the mechanical ordering rule are the mitigation. The owner should
look at this table on the preview with that reading in mind.

## 10. Reviews

The adversarial pass on v0.2 is in `consults/adversarial-pass.md`; its accepted findings are
carried into section 7.

**External review of v0.3 by Codex on `gpt-6-astra`** (`consults/external-review-astra.md`,
thirteen findings). Its verdict: the core deserves to continue, but v0.3 "improves presentation
while deferring the buyer value". What was done with it:

| # | Finding | Outcome |
|---|---|---|
| 1 | The design leaves out the thing that would justify a security leader reading it: what a development means for someone who buys from these suppliers (continuity, renewals, consolidation, what to ask the supplier) | Accepted as the most important gap. It is new judgment, so it cannot be published without the owner. A machine-drafted buyer brief for his approval is specified in the automation plan and listed in the owner packet. Not on the page today |
| 2 | Replace the growth leaderboard with a supplier comparison that declares no winners | **Accepted and built.** Section 3.3 |
| 3 | The recurring product should be a dependable weekly account of material changes, including "no material change found", kept distinct from "collection incomplete" and "interpretation pending" | Accepted into the automation plan as the target output. The three states are a requirement there |
| 4 | The facts-versus-judgments split leaks: choosing vendors, metrics and which events matter is judgment, and the existing "why" lines contain interpretation | Accepted. `product-core.md` section 6 is tightened: only bounded, attributed observations publish automatically, under collection and presentation rules the owner approves in advance; "why it matters" text is judgment |
| 5 | The reseller relationship needs real editorial safeguards: disclosure, inclusion rules, equal standards for partners and competitors | Accepted as an owner decision. He parked the employer question; the reader-facing disclosure is separate and is raised in the owner packet. The rubric gains a disclosure test |
| 6 | Refreshing figures is not enough; their meaning needs validation. Found two mislabelled figures in the signed issue | **Accepted, verified by the coordinator against `web/src/data/issues/2026-w36.ts` lines 168 and 208 and the evidence titles.** Step B's data refresh is held (section 4) and a correction is put to the owner |
| 7, 8, 9 | The rubric is a presentation checklist, some tests reward the author's own design, weights under-value decision usefulness and trust | Accepted. Rubric v2.1: reweighted, fit-for-purpose blockers added, self-serving tests replaced |
| 10 | A universal 45-day age threshold is wrong; show the period, the source date, the last check and the judgment date separately | Accepted. The 120-day "older figure" mark is a stopgap; the four dates are an automation requirement |
| 11 | Six inherited domains do not cover what a security program buys (endpoint and managed services have no home); publish a bounded coverage list | Accepted as an open question for the owner (product core question 11). Not changed today |
| 12 | Cut the ranked podium, the thesis-centred headline and its note, and the full four-lane inventory from the front page | First: done. Second: the headline is the locked read of a published issue; a new front-page introduction is new judgment and waits for the owner, so the plain-words note stays as the interim. Third: removing the lanes from the front page is an owner gate and the build gates require them; they stay, below the market picture |
| 13 | Promise less: a declared supplier set and one short weekly buyer brief, with a reduced-service state when the owner cannot review | Accepted into the automation plan |
