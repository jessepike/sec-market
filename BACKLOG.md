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

**Remaining hygiene:** commit and push the live working tree so GitHub matches production.

## Active work

### SEC-009 — Recurring public-signal intelligence

Turn Pulse from a one-shot research edition into a living cybersecurity market-intelligence site.

**Must cover:**

- new security startups;
- funding and the VC activity behind them;
- M&A;
- public records and filings that change the market call.

**Job:** a signals function that gathers public events, reasons on them, and turns them into intelligence the site can use.

**Authorization state:** authorized by owner on 2026-08-16 (D-28)

**Not authorized by this work:** auto-publishing a market call without a human check; inventing sources; using confidential ePlus data

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
