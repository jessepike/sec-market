# Backlog

Canonical work queue for the Security Market Signal Pipeline. Owner decisions live in [decisions.md](decisions.md). Nothing here is authorized merely by appearing in this file unless [README.md](README.md) or [intent.md](intent.md) already authorize it.

## Completed episode

### SEC-002 — Test infrastructure-to-security demand lag

**Status:** completed

Run `SEC-MARKET-SIG-002` to determine whether infrastructure and AI-capex acceleration leads increased cybersecurity demand, over what horizon, and in which domains.

**Requires:**

- A 2023-to-current quarterly baseline
- Infrastructure-supplier and hyperscaler-capex signals
- Cybersecurity financial and demand-side signals
- A 0–8-quarter lag assessment
- Category-shift versus share-shift decomposition
- A public evidence freeze
- A timing posture with falsifiers
- Independent review

**Method:** [market-signal-runbook.md](docs/reference/market-signal-runbook.md)

**Contract:** [market-signal-episode-002.md](docs/episodes/002/market-signal-episode-002.md)

**Result:** completed and independently reviewed; stable lag remains `NO-CALL`

**Not authorized by this work:** production infrastructure or automated posture judgment

## Completed design

### SEC-003 — Human-verified shadow mode exploration

Design a human-verified shadow collection process after the second episode passes.

**Eligibility condition:** satisfied by SEC-002 completion and independent review

**Result:** `SEC-MARKET-SHADOW-001` v0.2 and replay corpus v0.1 accepted; Gate S0 passed

## Completed specification

### SEC-004 — Gate S1 replay implementation specification

Specify—but do not yet run—the bounded seven-row replay implementation.

**Requires:**

- explicit owner authorization to specify;
- implementation choices for runtime and storage;
- replay tests against `SEC-MARKET-SHADOW-CORPUS-001`; and
- no scheduler, live run, or automated promotion.

**Result:** `SEC-MARKET-SHADOW-S1-SPEC-001` v0.2 accepted and independently reviewed

## Pending owner authorization

### SEC-005 — Implement the Gate S1 replay instrument

Build—but do not run—the accepted seven-row replay instrument.

**Hard prerequisites:**

- separate owner authorization for implementation;
- named human verifier and different promotion authority;
- later separate authorization for fixture capture/source retrieval; and
- later separate authorization for the replay run.

**Authorization state:** not authorized

## Completed product MVP

### SEC-006 — Security Market Pulse website

Build a responsive, evidence-linked website using accepted Episode 002 research.

**Result:** implemented under `web/`; build, lint, evidence review, accessibility review, and leadership-product review passed

## Completed product decisions

### SEC-007 — Owner review and deployment

Owner reviewed the live site. Public Vercel deploy is live at https://security-market-pulse.vercel.app and https://securitymarketpulse.com.

**Result:** live at https://securitymarketpulse.com. Local, GitHub `main`, and Vercel match (`8b35e45` / `f780e88`). Deploy only via `git push origin main` with `jesse@keatingpike.com`.

## Active work

### SEC-009 — Recurring public-signal intelligence

Turn Pulse from a one-shot research edition into a living cybersecurity market-intelligence site.

**Steer from:** [docs/active/sec-009-execution.md](docs/active/sec-009-execution.md) + [leadership-brief-2026-08.md](docs/active/leadership-brief-2026-08.md).

**Shipped:** site, prints, Activity, ops artifacts (D-43).

**Ongoing:** Loop A — Tuesday multi-source gather (funding + M&A + domain checks).

**Also done:** M&A catalog, weekly desk checklist, domain vendor packet. Mapping and desk only — no scrapers.

**Authorization state:** authorized by owner on 2026-08-16 (D-28); parallel mapping authorized 2026-08-16 (D-33)

**Not authorized by this work:** auto-publishing a market call without a human check; inventing sources; using confidential ePlus data

### SEC-013 — Landscape page (Option D)

Rebuild the front page as a standing landscape reference rather than a single dated edition. Accepted direction is Option D (D-47).

**Two tasks, in order:**

1. [landscape-data-spec.md](docs/active/landscape-data-spec.md) — merged to `main`.
2. [landscape-ui-spec.md](docs/active/landscape-ui-spec.md) — Option D, merged to `main` in `57d4f5b`.

**Live:** https://securitymarketpulse.com. The `landscape/ui`, `landscape/data`, and `edition-dated-postures` branches were merged and deleted on 2026-08-19; their preview URLs no longer resolve.

**Authorization state:** design accepted (D-47), one-product pass accepted (D-48), promotion to production approved by the owner and reconciled on 2026-08-19 (D-51 retracts D-49). Merged to `main` and live, verified by query against https://securitymarketpulse.com. Closed.

**Not authorized by this work:** the weekly collection loop, new sources, auto-publishing, any change to the published market call or Episode 002 tags.

### SEC-014 — Visual design pass on the live site

Option D landscape is the accepted visual pass (D-47, D-48). It is merged and serving on production.

**Status:** shipped. No open items; the D-48 promotion record was reconciled on 2026-08-19 (D-51).

### SEC-018 — Integrity pass

Remove the places where the site states something about itself that is not true. Eight items: derive the landscape eyebrow from the data, remove the never-used "needs a source" provenance state, stop asserting a weekly cadence, fix the SecOps print line before promoting SecOps crashes the page, de-duplicate evidence ids in the moved-this-window section, give the two judged rows a stated basis, add a `verify:integrity` build gate, and derive the evidence-library filter options from the records present.

**Spec:** [integrity-pass-spec.md](docs/active/integrity-pass-spec.md) (`SEC-MARKET-INTEGRITY-001` v0.1)

**Status:** complete. All eight items landed as eight atomic commits, merged to `preview` in `c9384de`. Verified independently on 2026-08-20: every acceptance criterion in the spec holds, all five `verify:integrity` checks were observed to fail closed under deliberate perturbation and to pass once reverted, and the rendered diff against production shows only the six expected visible changes. `main` untouched and still a fast-forward ancestor of `preview`.

**Authorization state:** approved by the owner 2026-08-20 (D-52). Implemented by Cursor Composer, verified by the CPO session. Promotion to production is a separate owner decision and has not been made.

**Not authorized by this work:** new content of any kind — no new domains, sources, vendors, figures, print cards, or changed postures. No push or merge to `main`.

### SEC-019 — Make the declared model mean something

Deferred from SEC-018 on purpose, because each item is a judgment or design call rather than a correction.

- Confidence is `medium` on all six domains, so the mark carries no information. Either it varies or it goes.
- `DecisionHorizon` tops out at "Next 1–4 quarters" while intent promises the present through 24 months. The longer horizon is currently unrepresentable in the type.
- Three domain taxonomies coexist and share no identifiers: six posture domains, eight scorecard groups, seven free-text activity labels.
- All 42 print cards render a hardcoded "— no series yet —" placeholder. There is no sparkline behind it. Build it or remove the slot.
- Wire the five unreferenced evidence records — Dell, Vertiv, Broadcom, Meta, Oracle — into the infrastructure and hyperscaler-capex surfaces the method already names. Figures must be verified against each source.
- Intent names relevance as one of four properties every claim preserves. No field or proxy for it exists anywhere.

**Authorization state:** not authorized. Needs the owner's direction first on what belongs above the fold — six of thirteen top-level sections are currently collapsed behind a click, including the market call, the scorecard, the method and the evidence library.

### SEC-021 — Make the vendor scorecard findable

The owner remembered a per-vendor, per-domain card grid and asked which decision removed it. None
did. All 42 cards were in the served markup, nested inside a collapsed `<details>` four sections
down, so nothing told a reader they existed. Measured in a browser: 42 in the document, zero visible.

**Spec:** [scorecard-visibility-spec.md](docs/active/scorecard-visibility-spec.md) (`SEC-MARKET-VIS-001`). Decision: D-54.

**Phase 1 complete and live in production** (promoted 2026-08-25, D-57). The scorecard is a top-level section under the tracked
hypotheses, its eight domain groups collapse individually so a phone does not receive a 17,000-pixel
wall, the group counts derive from the data, and the placeholder spark that never became a chart is
gone. Phone page height fell from 17,013 to 8,309 pixels; desktop unchanged.

**Phase 2 — not started.** Map each print to the posture it supports, so a reader can move from a
domain card to the evidence under it rather than to an undifferentiated list.

**Phase 3 — not started.** Give the archive real prior editions instead of a single frozen snapshot.

**Rejected in review before it was built:** promoting all 42 cards to the top of the page. That
trades a reader who cannot find the evidence for a reader who cannot find the read.

**Authorization state:** Phase 1 authorized and built. Phases 2 and 3 need an owner go, and Phase 2
overlaps the above-the-fold question that gates SEC-019.

### SEC-022 — Project scorecard and its baseline

An instrument to keep the work honest against `intent.md`, which says plainly that completing agents,
a website or reports does not constitute success.

**Instrument:** [project-scorecard.md](docs/active/project-scorecard.md) v0.2. Decision: D-55.

Outcomes carry an evidence state rather than a score, every rate reads against an exposure
denominator, there is no composite number to optimise, and the per-edition pass/fail health check is
kept separate from the outcome review so shipping discipline is never mistaken for impact.

**Baseline, deliberately unflattering:** every outcome is `not_assessed`, the exposure denominator is
1, legibility fails, and [decision-impact-log.md](docs/active/decision-impact-log.md) has zero entries.

**Owner owes two answers, and I should not guess either:** who scores this independently, and which
named people count as qualified exposure.

**Open work off the baseline:** raise the exposure denominator above 1; close the legibility check;
add lead-time and incremental-value questions to the decision impact log.

### SEC-023 — Phone view

**Fixed 2026-08-22 (D-56) and live in production since 2026-08-25 (D-57).** The phone view had drifted from the accepted Option D design: the
framing sentence, headline and lede all rendered *after* the four domain cards, because the
implementation set `order: 2` on the intro and `order: 1` on the cards inside the phone breakpoint.
Every build gate passed the whole time and nobody had rendered a phone width since Option D landed.

Corrected and now serving: document order restored, the eyebrow hidden above the framing line as the
design has it, the lede tightened, the card judged footer collapsed from three stacked lines to one,
and the missing Scorecard entry added to the navigation. Phone page 8,309 → 8,237 pixels; desktop
identical at 8,274 pixels and its judged footer still two stacked lines, both confirmed by render.

**Open, needs an owner yes or no:** the accepted design uses shorter footer labels — "JUDGED 17 AUG ·
THIS QUARTER · CONF MEDIUM" — which fit one line where the current wording wraps to two. That drops
the year and the word CONFIDENCE from a provenance stamp, so it is a content call rather than a
styling one. Worth roughly another 70 pixels off the phone page.

## Completed mapping

### SEC-010 — Durable signals operation (map only)

How weekly gather → synthesize → human check → post works so this is not a one-off.

**Output:** `docs/active/signals-operating-model.md`

**Authorization state:** mapping authorized (D-33). Build not authorized.

### SEC-011 — M&A source catalog (map only)

Where public cybersecurity M&A actually shows up, and what we can use. Same shape as the startup catalog.

**Output:** `docs/active/ma-source-catalog.md`

**Authorization state:** research authorized (D-33). Collection not authorized.

## Flagged (not authorized)

### SEC-012 — Orphaned signals data

`web/src/data/signals.ts` (`marketSignals`) and `MarketSignal` in `types.ts` lost their only consumer when `SignalFeed` was removed. Real evidence-linked content — wire into UI or retire with a logged decision.

**Status:** resolved — retired 2026-08-19. Content superseded by Activity board and landscape what-moved; array removed.

### SEC-015 — Lock past editions against silent edits

`web/src/data/edition.ts` is append-only by convention. Two build gates check the current edition snapshot, but nothing stops editing a shipped edition snapshot. Extend the `verify-panel.ts` SHA-256 pattern.

**Status:** partial — `verify-edition.ts` added (locks full editions array hash).

### SEC-016 — Print cards vs table presentation

Commit `727ce6a` restored vendor print cards on `main`, partially reversing the prints-table conversion. Resolve before the next public share.

**Status:** resolved by landscape merge — print cards remain in collapsed scorecard section per D-48.

### SEC-017 — Weekly refresh loop

Make the tracked layer actually refresh weekly. Separate from SEC-013 on purpose.

**Authorization state:** not authorized. Scope not yet written.

### SEC-008 — Account conversation prompts

Reconsider account-facing prompts only after the core monthly scorecard, recency model, and domain coverage are trusted.

**Status:** parked by owner feedback; removed from the MVP website

## Not authorized

- Partner-risk-first sequencing
- Varonis backtest as governing acceptance gate
- T0–T5 collapsed evidence/inference/action score
- West/NorCal-first core delivery
- Universal AI-security platform call
- Production infrastructure or broad automation
- Reproducing or modifying CISO Advisory ontology or vendor catalog

### SEC-020 — Accuracy and traceability sweep

The owner's standard is 100% certainty that everything shown is accurate, current, and traceable to a source a reader can check. Opened 2026-08-20.

**Desk audit complete.** 150 displayed figures checked against the evidence records they cite: 141 fully supported, 8 partial, 1 unsupported. Three defects were corrected the same day (see below). The rest need a source, not a judgment.

**Fixed 2026-08-20:**

- `act-oasis` claimed Cyera raised $600M "eight weeks earlier". No cited source states a week count, and the gap between the two records' own dates is 48 days. Now reads "weeks earlier", matching what evidence D22 actually says.
- `print-panw` attributed the whole headline-versus-organic gap to CyberArk. Evidence C2 names CyberArk *and Chronosphere*. Corrected.
- `marketCall` quoted Cisco networking orders +40% and Zscaler organic ARR +21% without citing A2 or C4, the records that prove them. Both added. Separately, `chartEvidenceIds` cited C6b (Cisco) although the security composite in `derivePanel.ts` is a median of CrowdStrike, Okta, Fortinet, Zscaler and Check Point — no Cisco. Removed from the chart citations; it stays on the market call where it belongs.

**Open — needs a source or an owner answer, not a guess:**

- The Activity board states "Window: Jul 6 – Aug 10, 2026" while four items predate it and none reach the end date. It is unclear whether this describes a *collection* window (in which case background items are outside it by design and the wording should say so) or an event-date window (in which case it is wrong). Do not rewrite it until that is settled.
- `edition.ts` claims the activity window covers RoS issues #252–#256. Only #254 and #256 are cited anywhere in the evidence set. Verify before the next edition.
- `print-varonis` sources its "headline 52%" from evidence C8b's `limitations` field rather than its excerpt; `print-secuvy` and `act-secuvy` source the "Seed" label from a structured attribution field, not the excerpt. Defensible, but both should be confirmed against the primary release during the source sweep.
- Latent, not currently visible: `trackedPrintEvidenceIds()` resolves print-line tokens by prefix, and `print-crwd-cloud` precedes `print-crwd` in the array, so a bare "CrowdStrike" token would silently bind to the Falcon Cloud segment (C13) rather than total ending ARR (C1). The SecOps print line now contains exactly that token. It does not fire today because SecOps is not a landscape card — but promoting SecOps is under active consideration and would mis-cite on the first render. Fix the resolver before any promotion.

**Source sweep pass one complete 2026-08-20.** All 71 canonical sources checked by six parallel
agents on three questions each: does the link resolve, is every figure and clause in the stored
excerpt actually on that page, and is there any sign the page was corrected or restated. Results:
39 exact, 5 close, 4 drift, 23 unverifiable (recounted from per-record rows; one agent's own summary line miscounted its table). Full record at
[docs/audits/2026-08-20-source-verification.md](docs/audits/2026-08-20-source-verification.md).

**No figure on the site contradicts its source.** Every drift is a missing source rather than a
wrong number.

**The sweep initially overstated the defect and was corrected the same day.** Agents were fed only
each record's top-level `canonicalUrl`, but the schema also carries a `sourceAttributions` array
with a per-source `canonicalUrl` that `EvidenceDrawer.tsx` already renders and seven records already
use. Five records reported as drift (B3, D7, D10, D11, D12) were correctly cited all along. The real
defect is six records, not eleven.

**Fixed 2026-08-20** — `sourceAttributions` added, each URL independently located and quoted
verbatim from the primary document before use:

- A3 Arista: the $1.351B comparison now attributes Arista's 2023-05-01 Q1 2023 release.
- A5 Vertiv: orders +252%, book-to-bill 2.9x, backlog $15.0B now attribute the Q4 2025 exhibit
  (2026-02-11), which states them verbatim.
- B1 Microsoft: "Customer demand continues to exceed available capacity" now attributes the FY26 Q4
  earnings call, which is where the CFO said it, using the same `aka.ms/transcriptfy26q4` link D11
  already uses for that document.

**Closed 2026-08-20 — all six.** C2 attributes the Q3 FY2026 investor deck (slide 3) for the
excluding-acquisition growth rates. C7 attributes Okta's Q1 FY2027 posted commentary for the 107%
net retention figure. D6 attributes Marsh for both halves — the Q2 2026 US rates page and the
twelve-controls page.

A caution recorded with them: the source hunt recommended deleting C2 and C7 as unverifiable,
because I told it in the prompt that they claimed a quarter ended 2026-07-31. They do not; both
correctly state the quarter ended 2026-04-30. The agent reasoned correctly from a false premise I
supplied and produced a well-evidenced recommendation to remove two accurate records. D9 and D10
were flagged the same way and are also fine.

**Still unreadable — 11 records, all host-side.** Eight investor-relations timeouts, two BusinessWire
403s from Akamai, one Incapsula bot challenge on Cato which must not be bypassed. Broadcom loads but
serves a JavaScript shell that a fetcher cannot read; a browser would resolve it. Fortinet was
separately confirmed healthy in a real browser. None of these are dead links and none are known
defects.

**Owed and not built — the durable fix.** `verify:integrity` should fail the build when a record's
excerpt spans more than one organization or economic period and the record carries no
`sourceAttributions`. All six defects would have been caught at authoring time. This replaces the
earlier data-model recommendation: no schema change is needed, because the field already exists and
already renders. It is not being enforced.

**Pass two complete.** The recoverable records were re-fetched with the method that worked (SEC.gov's
documented identified-User-Agent policy, `pdftotext` on PDFs, a browser user agent on investor-relations
hosts) and a primary source was located for each genuinely unattributed claim. Eleven records remain
unreadable for host-side reasons only, listed above.

**Authorization state:** authorized by the owner 2026-08-20. Fixes above already applied; the source sweep is scoped and awaiting a go on full versus partial.
