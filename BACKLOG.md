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

**Contract:** [market-signal-episode-002.md](docs/active/market-signal-episode-002.md)

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

### SEC-010 — Durable signals operation (map only)

How weekly gather → synthesize → human check → post works so this is not a one-off.

**Output:** `docs/active/signals-operating-model.md`

**Authorization state:** mapping authorized (D-33). Build not authorized.

### SEC-011 — M&A source catalog (map only)

Where public cybersecurity M&A actually shows up, and what we can use. Same shape as the startup catalog. No collection week until the catalog is reviewed.

**Output:** `docs/active/ma-source-catalog.md`

**Authorization state:** research authorized (D-33). Collection not authorized.

### SEC-012 — Orphaned signals data (map only, no deletion authorized)

`web/src/data/signals.ts` (the `marketSignals` array) and the `MarketSignal`
type in `web/src/data/types.ts` lost their only consumer when the unused
`SignalFeed` component was deleted during the 2026-08 hardening pass. The
data itself is real evidence-linked content (headlines, dates, evidence
IDs), not scaffolding, so it was left in place rather than deleted — that
call belongs to whoever decides whether this content should be surfaced
somewhere on the page or formally retired.

**Output:** a decision — either wire `marketSignals` into a live section, or
remove the array/type as dead content.

**Authorization state:** not authorized either way; flagged only.

### SEC-010 — Visual design pass on the live site

The site has never had one. Five waves of launch hardening on 2026-08-17 improved
prerendering, discoverability, bundle size, citation accuracy, and accessibility, and
changed nothing a reader can see. The owner opened it expecting a night of work to show
and read the absence of change as a regression.

This is the gating work for a public share, and it is a governance concern rather than a
vanity one: B1 (reasoned beneficiary uptake) cannot begin until a CSP peer reads the page,
and the surface has to earn that read.

Do it on a branch with a Vercel preview and owner approval before merge, per AGENTS.md.

**Status:** highest priority. Not started.

### SEC-011 — Lock past editions against silent edits

`web/src/data/edition.ts` is append-only by convention and by comment. Two build gates
check that the CURRENT edition's snapshot matches what the site publishes, but nothing
stops a future session from quietly editing a SHIPPED edition's snapshot, which would
falsify every delta computed against it.

The repository already solves this shape of problem for the derived data panel with a
SHA-256 hash lock (`web/scripts/verify-panel.ts`). The same pattern applies here.

Needs a decision on where the lock file lives and whether it covers all prior editions or
only the immediately preceding one.

**Status:** flagged, not authorized.

### SEC-012 — Decide whether the restored vendor print cards stay

A parallel session restored the vendor print cards to `main` on 2026-08-17 (commit
`727ce6a`, "Restore vendor print cards from the scorecard visual"). That reverses part of
a prints-table conversion made earlier.

Nobody has confirmed which presentation the owner wants. Resolve before the next public
share so the two do not keep swapping.

**Status:** open question for the owner.

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
