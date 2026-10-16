# Scorecard visibility and page hierarchy

**ID:** SEC-MARKET-VIS-001 · **Status:** draft, owner decision pending · **Opened:** 2026-08-22

## The problem, measured

Verified in a real browser against production on 2026-08-21, not inferred from source:

- 42 vendor print cards exist in the DOM, grouped into eight domain headers. **Zero are visible.**
  `checkVisibility()` returns false for all 42.
- The page renders 4,316px. The hidden print grid alone is 4,655px — more hidden content than
  visible page.
- They sit behind a collapsed bar labelled "Episode 002 research and the full scorecard", which is
  positioned **below the corrections block and below the author's name and email**. Content beneath
  a signature reads as ended, so the bar is never opened.
- Behind that bar is not a section. It is an entire second edition with its own headline, its own
  market-condition stat block and its own narrative.
- The landscape names **four** domains. The scorecard groups vendors into **eight**. They share no
  identifiers. The platform-pressure table uses a **third** vocabulary (pressure groups).
- All 42 cards render a hardcoded `— no series yet —` placeholder.
- Confidence reads MEDIUM on all four landscape cards and therefore carries no information.

## What was rejected, and why

The obvious fix — lift all 42 cards to a top-level section directly under the landscape — was put to
an independent review and rejected. The objection is correct and worth stating in full, because it
is the reason this spec is staged rather than a single move:

> Forty-two expanded cards directly below the landscape would create a 4,655px evidence wall before
> readers reach "What moved", platform pressure, or tracked hypotheses. It would shift the page from
> forward-looking market judgment to backward-looking vendor reporting — the opposite of the stated
> promise. The cards deserve visibility, not primacy.

The signed posture judgments are the product. Vendor prints are the evidence underneath it. Making
the evidence visible must not make it primary.

The review also named what the fix missed entirely: **there is no recorded relationship between a
vendor print and the posture it supports, weakens, or contradicts.** Until that mapping exists,
reorganising the page is cosmetic. That is the substance of Phase 2 below.

## Target hierarchy

Four distinct jobs, currently collapsed into one page:

1. The homepage makes the call.
2. Evidence explains the call.
3. The scorecard lets a reader inspect the evidence.
4. The archive preserves prior calls.

Section order on the current page:

1. The landscape — current market judgment
2. What moved
3. **Evidence by market** (new, Phase 2)
4. Platform pressure
5. Tracked hypotheses
6. **The full scorecard** (Phase 1 — moved here, out of the Episode 002 wrapper)
7. Method
8. Corrections, author, contact — **the true end of the document**
9. Archive link

Taxonomy, as a hierarchy rather than a choice between four and eight:

- **Four decision markets** at the judgment layer. These are what a person signs.
- **Eight evidence domains** beneath them. Every vendor print belongs to exactly one.
- **Pressure groups stay a separate dimension.** "Identity" and "Outrun" answer different questions —
  which market is this, versus what competitive position is this vendor in. Do not merge them.

A print may support more than one market. Multi-mapping must be explicit; forcing one box per vendor
creates a fourth false taxonomy.

## Phase 1 — make it visible and correctly placed

Structural only. No new data, no judgment calls, safe to build and preview immediately.

1. Move the corrections block, author name and contact to the true end of the document, after every
   content section.
2. Lift `PrintGrid` out of the `research-depth` disclosure into its own top-level section placed
   after tracked hypotheses and before method. Heading: the number of vendors and domains, derived
   from the data rather than hardcoded, in the same way the landscape eyebrow already derives
   "four domains".
3. Domain group headers render visible and expanded. Cards within a group may collapse per group;
   the group headers themselves never collapse. A reader must be able to see that eight domains are
   covered without clicking anything.
4. Delete the `— no series yet —` placeholder and the empty chart space with it. When a real series
   exists, the card adopts a chart-bearing variant. Absence renders as nothing, not as an
   announcement of absence.
5. Rename the remaining disclosures to describe their contents rather than an episode number. The
   bar reading "Episode 002 research and the full scorecard" no longer holds the scorecard after
   step 2, and must not keep claiming to.

**Acceptance.** Given the production page at 1440px and 390px, when it first loads with nothing
clicked, then all eight domain group headers are visible, `checkVisibility()` returns true for the
group headers, no content of any kind appears below the author's contact line, and the string
"no series yet" appears zero times in the rendered page.

**Proof required.** Full-page renders at 1440px and 390px, before and after, per the project's
visual-review rule. A passing build is not evidence.

## Phase 2 — evidence by market

This is the real fix and it is data work before it is layout work.

1. Add an explicit mapping from each vendor print to its evidence domain and to the market posture
   or postures it bears on, including whether it **supports** or **contradicts** that posture.
   Contradicting evidence is the more valuable half and the site currently cannot express it.
2. Render "Evidence by market" under the landscape: per market, the posture, what changed, and the
   two or three most consequential signals, with supporting and contradicting evidence
   distinguished. Selection needs a stated rule — materiality, recency, or contradiction — not
   editorial choice.
3. Replace the uniform MEDIUM confidence badge with the thing a reader actually needs: what would
   change this posture, and what evidence currently pushes against it.
4. Give each print an observation period and a freshness state, so stale evidence cannot read as
   current. This depends on the cadence table, which is still owed.

## Phase 3 — archive

Episode 002 is a historical publication with its own thesis and narrative. It gets a real archive
destination and a plain "Past editions" entry point, not a collapsed bar on the homepage. Whether
that is a route or a separate document is a build decision for the CTO.

## The one decision the owner owes

**Is the scorecard a frozen Episode 002 artifact, or a continuously maintained current product?**

Everything above assumes current. If it is frozen, it belongs only in the archive and Phase 1 is
wrong. It cannot be both without making every figure on it temporally ambiguous.

**Recommendation: current.** The site's promise is where the market is going, the loop is already
weekly for at least one signal class, and a frozen scorecard cannot serve a page whose top half is
dated this week. Deciding "current" also means the scorecard stops living inside any edition, which
is what makes Phase 1 coherent rather than a reshuffle.

## Out of scope

Any change to `intent.md`. Any promotion to production. New vendors, new domains, or new evidence
records — this is about making what exists legible, not about expanding coverage.
