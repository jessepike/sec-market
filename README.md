# Security Market Signal Pipeline

Managed with [ADF](https://github.com/your-org/acm) (Agentic Development Framework) v2 folder structure.

## Current truth

This project creates public, publishable cybersecurity market intelligence that helps security leadership, account teams, and clients recognize consequential shifts early enough to make better-timed decisions.

The MVP consumption surface is now the **Security Market Pulse** website:

- **Product contract:** [web-mvp-product-contract.md](docs/active/web-mvp-product-contract.md)
- **External review brief:** [web-mvp-external-review-brief.md](docs/active/web-mvp-external-review-brief.md)
- **Local development:** `orb run -m dev npm run dev --prefix web`
- **Production build:** `orb run -m dev npm run build --prefix web`
- **Evidence contract:** every material call, chart, and domain posture links to source, excerpt/locator, limitations, conflicting evidence, and research artifacts
- **Production:** https://securitymarketpulse.com (Vercel alias: https://security-market-pulse.vercel.app)
- **Custom domain:** `securitymarketpulse.com` (Cloudflare DNS, unproxied CNAME to Vercel)
- **Deploy path (only):** local OrbStack preview → commit on `main` with GitHub-verified email `jesse@keatingpike.com` → `git push origin main` → Vercel builds that GitHub commit. Project `pikeholdings/security-market-pulse`, repo `jessepike/sec-market`, root `web`. Never CLI-upload a dirty working tree. `jesse@pikeholdings.co` blocks Vercel GitHub deploys.

The first completed episode is now classified as a thematic validation episode:

- **Episode:** `SEC-MARKET-SIG-001` v0.2
- **Question:** Are agents becoming a consequential cybersecurity action surface quickly enough to require preparation?
- **Decision:** **Conditional PREPARE**
  - organizations with current or planned material agent exposure should attach one bounded existing-control assessment to the relevant approval event;
  - organizations without material exposure remain in **INVESTIGATE**;
  - no standing program, specialist-platform motion, or broad procurement is authorized.
- **Research freeze:** `2026-08-15T18:18:04-07:00`
- **Independent review:** passed
- **Classification:** valid thematic application; does not validate the core infrastructure-to-security signal thesis

The primary core-signal validation episode is complete:

- **Episode:** `SEC-MARKET-SIG-002` v0.2
- **Question:** Is the current infrastructure and AI-capex cycle producing a measurable leading signal for increased cybersecurity demand, over what horizon, and which security domains are likely to capture it first?
- **Contract:** [market-signal-episode-002.md](docs/active/market-signal-episode-002.md)
- **Evidence:** [market-signal-episode-002-evidence.md](docs/active/market-signal-episode-002-evidence.md)
- **Baseline and panel:** [market-signal-episode-002-baseline.md](docs/active/market-signal-episode-002-baseline.md), [market-signal-episode-002-panel.md](docs/active/market-signal-episode-002-panel.md)
- **Accepted brief:** [market-signal-episode-002-brief.md](docs/active/market-signal-episode-002-brief.md)
- **Current gate:** passed
- **Decision:** infrastructure acceleration is evidenced; a stable infrastructure-to-security lag remains `NO-CALL`; use infrastructure activation as an account qualification trigger, not as proof of a cybersecurity boom
- **Reconciliation authority:** [intent-reconciliation-2026-08-15.md](docs/active/intent-reconciliation-2026-08-15.md)

## Authority order

Read in this order:

1. [intent.md](intent.md) — governing purpose, outcome, beneficiaries, and boundaries
2. [web-mvp-product-contract.md](docs/active/web-mvp-product-contract.md) — accepted MVP product and evidence UX
3. [intent-reconciliation-2026-08-15.md](docs/active/intent-reconciliation-2026-08-15.md) — prior downstream correction
4. [market-signal-episode-002.md](docs/active/market-signal-episode-002.md) — completed primary episode contract
5. [market-signal-episode-002-change-manifest.md](docs/active/market-signal-episode-002-change-manifest.md) — accepted packet version authority
6. [market-signal-episode-002-brief.md](docs/active/market-signal-episode-002-brief.md) — accepted timing judgment
7. [market-signal-episode-002-evidence.md](docs/active/market-signal-episode-002-evidence.md) — frozen evidence
8. [market-signal-episode-002-baseline.md](docs/active/market-signal-episode-002-baseline.md) — lag disposition and domain sufficiency
9. [market-signal-episode-002-panel.md](docs/active/market-signal-episode-002-panel.md) — sparse period-end panel
10. [market-signal-episode-002-source-manifest.md](docs/active/market-signal-episode-002-source-manifest.md) — atomic claim provenance
11. [outcome-architecture.md](docs/reference/outcome-architecture.md) — minimum causal architecture
12. [intervention-selection.md](docs/reference/intervention-selection.md) — why the manual decision episode was selected
13. [market-signal-runbook.md](docs/reference/market-signal-runbook.md) — frozen v0.2 manual method
14. [market-signal-runbook-validation.md](docs/active/market-signal-runbook-validation.md) — current second-domain validation authority
15. [shadow-collection-design-change-manifest.md](docs/active/shadow-collection-design-change-manifest.md) — shadow design version authority
16. [shadow-collection-design-v0.2.md](docs/active/shadow-collection-design-v0.2.md) — accepted design-only shadow process
17. [shadow-replay-corpus-v0.1.md](docs/active/shadow-replay-corpus-v0.1.md) — accepted seven-row Gate S1 oracle
18. [shadow-replay-implementation-spec-change-manifest.md](docs/active/shadow-replay-implementation-spec-change-manifest.md) — Gate S1 specification version authority
19. [shadow-replay-implementation-spec-v0.2.md](docs/active/shadow-replay-implementation-spec-v0.2.md) — accepted implementation specification
20. [market-signal-episode-001-change-manifest.md](docs/reference/market-signal-episode-001-change-manifest.md) — frozen Episode 001 version authority

Session state: [status.md](status.md) · Work queue: [BACKLOG.md](BACKLOG.md) · Decisions: [decisions.md](decisions.md)

[security-signal-workflow-spec-v0.4.md](docs/archive/security-signal-workflow-spec-v0.4.md) and [security-signal-BUILD-SPEC-v1.0.md](docs/archive/security-signal-BUILD-SPEC-v1.0.md) are historical source hypotheses. They are not implementation authority.

## Project state

| Layer | State |
|---|---|
| Governing Intent / Gate 1 | Passed |
| Outcome Architecture / Gate 2 | Passed — provisional |
| Intervention Selection / Gate 3 | Passed — provisional |
| Initial vendor-landscape pilot | Completed; historical validation input |
| Episode 001 — agentic runtime readiness | Completed and independently reviewed; reclassified as thematic validation |
| Episode 002 — infrastructure-to-security lag | Completed and independently reviewed |
| Manual runbook | Exercised across two materially different episodes; second-domain gate passed |
| Human-verified shadow collection design | Gate S0 passed; design accepted |
| Gate S1 replay implementation specification | Accepted after independent review |
| Gate S1 implementation and replay | Not started and not authorized |
| Security Market Pulse web MVP | Live at https://securitymarketpulse.com; owner reviewed |
| Website deployment | Vercel + custom domain live |
| Recurring public-signal intake | Authorized; not built |
| Auto-publish of market calls | Not allowed without a human check |

## Next authorized action

Stand up the signals job: gather public startup, funding, and M&A events, reason on them, and keep the site current.

Ship site changes only by committing locally, pushing `main`, and letting Vercel deploy that commit. Do not auto-publish a market call without a human check.

## Not authorized

- partner-risk-first sequencing;
- the Varonis backtest as a governing acceptance gate;
- T0–T5 as a collapsed evidence, inference, and action score;
- West/NorCal-first core delivery;
- a universal AI-security platform call;
- auto-publishing a market call without a human check; or
- reproducing or modifying the CISO Advisory ontology or vendor catalog.

The security-market project may reference CISO Advisory concepts where useful, but it owns market timing, signal evidence, and timing judgments.

## Episode 001 learning

Episode 001 produced a reconstructable thematic timing judgment and improved the manual method, but it did not test the core infrastructure-to-security lag thesis. Episode 002 now carries that validation burden.

