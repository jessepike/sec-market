# Design bake-off results — SEC-MARKET-DESIGN-BAKEOFF-001

**Date:** 2026-10-02. **Status:** awaiting the owner's choice of direction.

## Who built what (blind key, revealed after all four reviews)

| Label | Designer |
|---|---|
| A | Claude Opus 5.5 |
| B | Claude Fable 5.1 |
| C | GPT-6 Sol (revised once from the lead's renders; its sandbox blocked the browser) |
| D | GPT-6 Astra |

## Blind review scores (weighted total out of 110)

Weights from the brief: first screen ×3, look ×3, density ×2, constraints ×2, phone ×1.

| Design | Opus 5.5 | Fable 5.1 | GPT-6 Sol | GPT-6 Astra | Mean | Mean excluding own model |
|---|---:|---:|---:|---:|---:|---:|
| A (Opus) | **84** | 92 | 82 | 75 | 83.3 | 83.0 |
| B (Fable) | 81 | **86** | 70 | 78 | 78.8 | 76.3 |
| C (Sol) | 72 | 61 | **81** | 71 | 71.3 | 68.0 |
| D (Astra) | 69 | 73 | 75 | **88** | 76.3 | 72.3 |

Bold marks a reviewer scoring its own model's design. Three of four reviewers picked A as the winner
(Opus, Fable, Sol); Astra picked D, its own model's design. Fable and Sol both ranked another model's
design above their own. A leads with or without self-scores.

Runners-up: Opus and Fable chose B, Sol chose C, Astra chose B.

## What the reviewers agree A must fix

1. Remove the per-domain "Median reported revenue growth" chips, or source and scope them. They are
   machine-computed, carry no source or period, mix fiscal quarters, and in two-supplier domains are
   not a median. All four reviewers flagged this.
2. Make the twelve-month timeline usable without a mouse: 24-pixel targets, keyboard focus, and a
   one-tap source for each event. The same for sparkline values.
3. Cap "What changed" on the page (about eight items, then "Show all 25"), group each SEC filing under
   its results entry, and bring the phone page well below its 11,352 pixels with the first supplier row
   on the first phone screen.
4. Derive the SEC filer count from the data (the prototype states 16 complete; the data holds 14) and
   rewrite "the one fact that best describes where it stands" as the fixed rule it is.
5. Apply the fix pass 4 data rules (brief section 6a): one-decimal growth, dated facts in one format,
   named segment parents, 24-pixel targets throughout.

## What to borrow into A

- From B (Fable): the reported-growth dot plot (latest quarter and the quarter before, alphabetical by
  default, reader can sort by value) on the first screen, in place of the empty owner's-read box or
  beside the timeline. Also its per-supplier "N events · last date" column. Named by three reviewers.
- From C (Sol): the label, value and period stack for every fact, figures shown verbatim, its larger
  type and quieter spacing, and its tap-target sizing.
- From D (Astra): phone economy (a few events plus "Read all", selects for type and domain filters) and
  source links labelled with publisher and date instead of "Company".

## Files

- Reviews: `review/review-opus-5-5.md`, `review/review-fable-5-1.md`, `review/review-gpt-6-sol.md`,
  `review/review-gpt-6-astra.md`. Prompt: `review/review-prompt.md`. Blind copies: `review/designs/`.
- Comparison page: https://claude.ai/artifact/RPHztA8jfzRBubtfLHXPvx
