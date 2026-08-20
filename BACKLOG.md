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

**Authorization state:** approved by the owner 2026-08-20 (D-52). Implementation delegated to an external operator.

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
