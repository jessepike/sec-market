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

Deliver — manual method validated once; next episode not started

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
| [docs/archive/](docs/archive/) | Never auto | Historical hypotheses — explicit instruction only |
| [.claude/rules/](.claude/rules/) | Always | Hard constraints |

## Workflow Type

Probabilistic/Agentic — human-steered judgment with transparent evidence

## Trigger

Manual — market-timing episodes run on consequential questions

## Integrations

- CISO Advisory concepts may be referenced; this project owns market timing and signal evidence
- No production infrastructure integrations are authorized

## Fresh-agent minimum context

1. [README.md](README.md)
2. [intent.md](intent.md)
3. [outcome-architecture.md](docs/reference/outcome-architecture.md)
4. Current episode packet under [docs/reference/](docs/reference/) (`SEC-MARKET-SIG-001` v0.2)
