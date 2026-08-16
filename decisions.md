# Decision Log

Append-only. Record owner and project decisions that shape direction. Do not edit past entries; supersede with a new entry.

---

**D-1 · 2026-08-15 — Governing Intent accepted (`SEC-MARKET-001` v1.0).**

Gate 1 passed. Human Acceptance and AI Readiness recorded in [intent.md](intent.md). Public, publishable initial core; national and global observation; transparent calibrated judgments. Partner-risk-first Phase 1 from the build spec is not authorized.

**D-2 · 2026-08-15 — Outcome Architecture accepted provisionally (`SEC-MARKET-OA-001` v0.1).**

Gate 2 passed — provisional. Minimum causal architecture in [outcome-architecture.md](docs/reference/outcome-architecture.md).

**D-3 · 2026-08-15 — Manual decision episode selected (`SEC-MARKET-G3-001` v0.1).**

Gate 3 passed — provisional. Intervention rationale in [intervention-selection.md](docs/reference/intervention-selection.md).

**D-4 · 2026-08-15 — Initial decision contract sealed (`SEC-MARKET-DC-001` v0.1).**

AI data security and governance vendor landscape pilot completed. Contract in [decision-contract.md](docs/reference/decision-contract.md).

**D-5 · 2026-08-15 — Episode 001 decision: Conditional PREPARE (`SEC-MARKET-SIG-001` v0.2).**

Question: Are agents becoming a consequential cybersecurity action surface quickly enough to require preparation?

- Organizations with current or planned material agent exposure: attach one bounded existing-control assessment to the relevant approval event
- Organizations without material exposure: remain in INVESTIGATE
- No standing program, specialist-platform motion, or broad procurement authorized

Research freeze: 2026-08-15. Independent review passed. Packet authority: [market-signal-episode-001-change-manifest.md](docs/reference/market-signal-episode-001-change-manifest.md).

**D-6 · 2026-08-15 — Next authorized action: repeatability test.**

Run one materially different cybersecurity market-signal episode before any collection/normalization mechanics or production infrastructure. Identity is a candidate domain, not automatic for market-timing.

**D-7 · 2026-08-15 — ADF v2 project initialization.**

Repository scaffolded per ADF Folder Structure v2: root control surfaces, `docs/` lifecycle folders, workflow directories. Governance and episode packet promoted to `docs/reference/`; historical workflow and build specs to `docs/archive/`.

**D-8 · 2026-08-15 — Episode 001 reclassified as thematic validation.**

Owner review found that Episode 001 did not test the original core thesis that infrastructure, investment, financial, and demand signals can reveal future cybersecurity demand. The accepted Governing Intent already contains that thesis, so no intent-version change is required. Episode 001 remains a valid frozen thematic artifact but is not evidence that the core signal model or cross-domain repeatability has been validated. Reconciliation: [intent-reconciliation-2026-08-15.md](docs/active/intent-reconciliation-2026-08-15.md).

**D-9 · 2026-08-15 — Episode 002 infrastructure-to-security lag question authorized.**

Owner acceptance: “agree. proceed.”

Question: Is the current infrastructure and AI-capex cycle producing a measurable leading signal for increased cybersecurity demand, over what horizon, and which security domains are likely to capture it first?

Episode contract: [market-signal-episode-002.md](docs/active/market-signal-episode-002.md). Production automation remains unauthorized.

**D-10 · 2026-08-15 — Episode 002 decision accepted after independent review (`SEC-MARKET-SIG-002` v0.2).**

- Infrastructure and hyperscaler investment remain broadly accelerating.
- A stable infrastructure-to-security lag is `NO-CALL`; the public window cannot support an exact band or causal claim.
- Domain momentum differs, but infrastructure causality and “which domain captures first” remain `NO-CALL`.
- Use infrastructure activation as an account qualification trigger.
- Bounded readiness is appropriate only where cloud/AI capacity, sensitive data, machine identity, network refresh, or SASE displacement is becoming operational.
- No broad cybersecurity-boom narrative, vendor selection, procurement, or production automation is authorized.

Evidence, baseline, quarterly panel, source manifest, and accepted brief are under [docs/active/](docs/active/). Evidence, strategy, and practitioner reviews passed.

**D-11 · 2026-08-15 — Shadow-mode eligibility reached; authorization still required.**

The manual method has now been exercised across two materially different episodes. Collection and normalization mechanics may be proposed for human-verified shadow mode, but no design or build begins without a separate owner decision. Posture judgment remains human-steered.

**D-12 · 2026-08-15 — Reconciliation metadata and current authority registered.**

Owner authorization: “agree. proceed.”

The owner-authorized reconciliation required a metadata-only update to `intent.md`: `Last reconciled`, the reconciliation-event pointer, current operational validation, and fresh-agent context now identify `SEC-MARKET-RECON-001` and the completed Episode 002 packet. Governing Intent `SEC-MARKET-001` remains version 1.0; purpose, outcome, beneficiaries, boundaries, assumptions, state register, and dual acceptance are unchanged.

Current supporting authorities:

- `SEC-MARKET-SIG-MAN-002` — Episode 002 v0.2 packet and correction authority
- `SEC-MARKET-RUN-VAL-002` — second-domain validation overlay for frozen runbook v0.2

These records preserve the frozen Episode 001 packet while making current handoff state explicit.

**D-13 · 2026-08-15 — Human-verified shadow collection design authorized.**

Owner selection: “design of a human-verified shadow collection process.”

Authorization was limited to design. It did not authorize a collector, storage implementation, replay, live cycle, scheduler, database, publication, or automated evidence promotion.

**D-14 · 2026-08-15 — Shadow collection design v0.2 accepted; Gate S0 passed.**

`SEC-MARKET-SHADOW-001` v0.2 and `SEC-MARKET-SHADOW-CORPUS-001` v0.1 passed independent architecture, governance, and operator reviews.

Version authority: `SEC-MARKET-SHADOW-MAN-001`.

The accepted design:

- limits the first slice to seven primary financial facts;
- requires human-only verification and a different human promotion authority;
- makes blind bulk promotion structurally invalid;
- preserves source, definition, omission, and failure provenance;
- writes only append-only shadow evidence;
- prohibits automated posture, publication, and run closure; and
- keeps S1–S3 manually triggered.

The next possible step is a bounded Gate S1 replay implementation specification. It requires separate owner authorization and assignment of two distinct human identities. No implementation or replay is authorized by this decision.

**D-15 · 2026-08-15 — Gate S1 replay implementation specification authorized.**

Owner authorization: “go.”

Authorization is limited to producing and independently reviewing the implementation specification. It does not authorize:

- implementation or package installation;
- fixture capture or source retrieval;
- assignment of invented human identities;
- the replay run;
- S2/S3 live collection;
- a scheduler, database service, posture change, or publication.

The two distinct human identities remain a hard blocker for implementation and replay.

**D-16 · 2026-08-15 — Gate S1 implementation specification v0.2 accepted.**

`SEC-MARKET-SHADOW-S1-SPEC-001` v0.2 passed architecture, security/governance, and builder/operator review.

The accepted specification selects:

- Python 3.12 standard library in the OrbStack `dev` VM;
- local content-addressed artifacts and append-only/tamper-evident SQLite state;
- seven issuer runs in one replay cycle;
- canonical source and locator recipes for the seven gold facts;
- owner-attested SSH identities with human-only verification and separate promotion;
- signed two-person manual retrieval fallback for blocked IR sources;
- manually triggered commands only;
- atomic promotion and rollback testing; and
- a complete negative/bypass test matrix.

Implementation remains unauthorized. Fixture capture/source retrieval and the replay run each require later separate authorization. The named human verifier and different promotion authority remain unset.

**D-17 · 2026-08-16 — Responsive website selected as the MVP delivery mechanism.**

Owner acceptance: “yes this represents what i want to use.”

The website must maintain attribution and access to supporting research and evidence for users who want to validate or investigate a claim. This promotes the website from Exploring to Decided in Governing Intent v1.1 without changing the project’s purpose or public-evidence boundary.

**D-18 · 2026-08-16 — Project lead and model-routing team established.**

- `sec-market-lead`: Claude Sonnet high, outcome and orchestration
- `sec-market-builder`: Composer 2.5, implementation
- `sec-market-reviewer`: Claude Sonnet high, read-only review
- Claude Opus reserved for consequential architecture or final high-risk review
- One worker by default; at most two concurrent workers unless independent

**D-19 · 2026-08-16 — Security Market Pulse web MVP completed for local review.**

The React/TypeScript static website presents the accepted Episode 002 call, derived market-layer data, domain postures, latest signals, account prompts, and an evidence library with source links, excerpts, limitations, conflicting evidence, and research-artifact access.

Evidence, accessibility, and leadership-product reviews passed after correcting unsupported chart data, evidence navigation, modal accessibility, mobile behavior, and first-screen usability. Local build and lint pass. Deployment remains a later explicit decision.

**D-20 · 2026-08-16 — Emergency model-usage recalibration.**

The Ultra plan’s Other Models pool reached approximately 65% usage one day into the cycle.

Effective immediately:

- Composer 2.5 is the default for all project orchestration, implementation, research, testing, and review.
- GPT, Claude, Gemini, and other external models require explicit owner authorization for each invocation.
- Grok remains disabled until the owner confirms the Cursor Models pool status.
- Only one agent runs at a time unless the owner explicitly authorizes parallel work.
- Direct work is preferred when delegation would duplicate context.
- Automatic council/reviewer/verifier launches are disabled.

The owner must switch the main chat model to Composer 2.5 in Cursor; agents cannot change the parent model from inside a session.

**D-21 · 2026-08-16 — Grok restored to the Cursor Models pool.**

Owner confirmed Grok is included in the same Cursor Models pool as Composer. The emergency Composer-only hold on Grok is lifted.

Effective immediately:

- Lead / orchestrator / thinking: Grok 4.6 (`grok-4.6` frontmatter; `cursor-grok-4.6-high-fast` for Task).
- Worker / implementer / routine review: Composer 2.5 (`composer-2.5` frontmatter; `composer-2.5-fast` for Task).
- GPT, Claude, Gemini, and other Other Models invocations still require explicit owner authorization.
- Single-worker default, no automatic council launches, and no `inherit`/omitted Task models remain in force.

This aligns the project with the global Ultra model-routing rule.

**D-22 · 2026-08-16 — Pulse is a frozen edition with headline-first depth.**

The website is a dated edition, not a live feed. Old data is demoted, not deleted: current on the scorecard, still-true context in Background, superseded prints in evidence only, acquired vendors frozen and annotated.

Capital activity (M&A and funding) shows one section read and five headlines; notes and sources expand on the row. Remaining window events and last-disclosed raises stay collapsed.

Refresh is manual: earnings clusters, material closes or raises, and Watch-next falsifiers. Not a weekly news cycle. Raises and deal values are not ARR.

External reviewers start at [web-mvp-external-review-brief.md](docs/active/web-mvp-external-review-brief.md). Deploy remains a separate track.

**D-23 · 2026-08-16 — External review P1 fixes before public ship.**

Research-artifact links no longer point at a private GitHub repo; packet labels are text and canonical sources stay in the drawer. Network / SASE is capped at PREPARE, matching Episode 002. Tempo and Method guardrails stack on small screens instead of hiding. Scorecard cards are current prints only; no-series names collapse under the group.

**D-24 · 2026-08-16 — Render the written judgment; prints become a table.**

The overview contract fields in `market.ts` (what changed, do/avoid, meaning, confidence, no-call boundaries, change triggers) are now on the page. Prints are a comparable table. The content shell is 1200px for data; prose stays at 68ch.

An edition archive / back catalogue is a product-strategy decision and is not authorized by this change.

**D-25 · 2026-08-16 — Public website deployment authorized on Vercel.**

Owner selected `securitymarketpulse.com` and authorized public hosting. Vercel project `pikeholdings/security-market-pulse` is linked to `jessepike/sec-market` with root directory `web`.

- Production: https://security-market-pulse.vercel.app
- Custom hosts claimed: `securitymarketpulse.com` (apex) and `www.securitymarketpulse.com` (308 to apex)
- DNS remains on Cloudflare (`georgia` / `jerry`). Records must be DNS-only (grey cloud), not proxied.
- First production deploy was a CLI upload of the current working tree.

This authorizes the public static website. It does not by itself authorize auto-publishing judgments without a human check.

**D-26 · 2026-08-16 — `securitymarketpulse.com` DNS cutover complete.**

Two unproxied CNAMEs written on Cloudflare zone `34251ea7b517605f017007f13625555a` to `8406d7f2fc89acd7.vercel-dns-016.com`. Vercel domain config is no longer misconfigured. Apex returns HTTP 200 with a Vercel-issued Let’s Encrypt cert (`CN=securitymarketpulse.com`, SAN includes www). `www` 308s to apex. Title: `Security Market Pulse | Episode 002`.

GitHub `main` was behind the live CLI deploy at the time of cutover.

**D-27 · 2026-08-16 — Owner product review is complete.**

Owner stated the live Pulse site has already been reviewed and that “owner review pending” is stale. `SEC-MARKET-WEB-001` is accepted for use. Remaining work is to keep the site current and turn one-shot research into recurring market intelligence.

**D-28 · 2026-08-16 — Recurring public-signal intelligence is now the job.**

Owner direction: Security Market Pulse is a cybersecurity market-intelligence site, not a finished research paper. It must regularly show what is happening in the market — including new security startups, funding, and M&A — from public sources.

The previous hold that blocked collectors, schedulers, and a signal pipeline is lifted for this purpose. A dedicated signals job will gather public events, reason on them, and turn them into intelligence the site can publish. Auto-publishing a market call without a human check remains out of bounds.

Numbering note: the two 2026-08-16 entries previously both labeled D-23/D-24 are now D-25 (deploy) and D-26 (DNS).
