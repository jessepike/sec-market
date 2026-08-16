# Security Market Signal Pipeline

@AGENTS.md

> Project context lives in AGENTS.md (canonical). This file imports it for Claude-specific sessions.

## Context Map (progressive disclosure)

**Always loaded:** Root artifacts — `intent.md`, `BACKLOG.md`, `status.md`, `decisions.md`

**Default working zone:** `docs/active/`

**Load on demand:**
- Gate chain and episode packet → `docs/reference/`
- Manual method → [market-signal-runbook.md](docs/reference/market-signal-runbook.md)
- Historical hypotheses → `docs/archive/` (explicit instruction only)

**Never load automatically:** `docs/archive/`, `.ctx/`
