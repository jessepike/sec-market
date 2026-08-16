# Security Market Signal Pipeline

## Runtime

Shared instructions for all agent runtimes (Claude, Codex, Cursor, Gemini).

## Intent

See [intent.md](intent.md)

## Classification

- **Type:** Workflow
- **Scale:** commercial
- **Scope:** mvp
- **Complexity:** standalone

## Current Stage

Operate — Security Market Pulse is live; next job is recurring public-signal intelligence

## Context Map

| File | Load When | Purpose |
|------|-----------|---------|
| [intent.md](intent.md) | Always | North Star — immutable without permission |
| [status.md](status.md) | Always | Session state — review at start, update at end |
| [BACKLOG.md](BACKLOG.md) | Always | Canonical work queue |
| [decisions.md](decisions.md) | Always | Decision log |
| [README.md](README.md) | Always | Authority order and project truth |
| [docs/reference/](docs/reference/) | Design, episode work | Settled governance and episode packet |
| [docs/active/](docs/active/) | Current work | In-progress specs and plans |
| [web/](web/) | Web product work | Security Market Pulse MVP |
| [docs/archive/](docs/archive/) | Never auto | Historical hypotheses — explicit instruction only |
| [.claude/rules/](.claude/rules/) | Always | Hard constraints |

## Workflow Type

Probabilistic/Agentic — human-steered judgment with transparent evidence

## Trigger

Recurring — public market signals are gathered on a cadence; market calls stay human-checked

## Integrations

- CISO Advisory concepts may be referenced; this project owns market timing and signal evidence
- Public static website: Vercel project `security-market-pulse`, domain `securitymarketpulse.com`
- Recurring public-signal intake is authorized; auto-publish of market calls is not

## Fresh-agent minimum context

1. [README.md](README.md)
2. [intent.md](intent.md)
3. [outcome-architecture.md](docs/reference/outcome-architecture.md)
4. Current reconciliation and active episode under [docs/active/](docs/active/) (`SEC-MARKET-RECON-001`, `SEC-MARKET-SIG-002`)
5. Frozen thematic packet under [docs/reference/](docs/reference/) (`SEC-MARKET-SIG-001` v0.2) only when needed
6. Accepted shadow design and replay corpus under [docs/active/](docs/active/) (`SEC-MARKET-SHADOW-001` v0.2, `SEC-MARKET-SHADOW-CORPUS-001` v0.1)
7. Accepted Gate S1 implementation specification under [docs/active/](docs/active/) (`SEC-MARKET-SHADOW-S1-SPEC-001` v0.2)
8. Accepted web MVP contract and implementation under [docs/active/](docs/active/) and [web/](web/) (`SEC-MARKET-WEB-001`)
9. Current signals job under [docs/active/signals-job.md](docs/active/signals-job.md)
