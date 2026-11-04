# Security Market Pulse

@AGENTS.md

AGENTS.md is canonical for every runtime. This file adds only what is specific to Claude sessions.

## Before touching `web/`

`main` is the production code line. It moves only by an approved fast-forward from `preview`
(AGENTS.md, D-110); the next gated publisher run then delivers it. The old `promote.yml` route is
disabled, so a push to `preview` does not reach the public site by itself.

- Never commit or push to `main` yourself, except the owner-approved promotion command.
- Render the page and look at it before pushing (`node scripts/shot.mjs <url> <prefix>` from `web/`,
  1440px and 390px). Anything visible beyond data is major: add `Owner-Review: required`.
- Cloud sessions cannot load securitymarketpulse.com or the preview host in a browser (the proxy
  refuses them). Render a local build (`npx vite preview`) instead, or use Remote Control on the
  owner's Mac for the live site.
- Never delete code, CSS or data because static analysis says it is unused. Prove it with a
  before/after render.
- When reporting, separate invisible work from visible work. If nothing visible changed, say so first.

## Context map

- **Always loaded:** `intent.md`, `status.md`, `BACKLOG.md`, `.claude/rules/`, and the "Decisions in force"
  index at the top of `decisions.md` (open individual entries only when needed; the ledger is long)
- **Current design:** `docs/reference/` (start with `architecture.md`)
- **Work in flight:** `docs/active/` (the daily-pipeline runbook is `docs/active/daily-pipeline/github-operations.md`)
- **Never load automatically:** `docs/archive/`, `.ctx/` (local, uncommitted agent scratch context)

## Working habits

- Do not use `pkill -f` with a pattern that also appears in your own command line; it kills the
  shell running it.
- Commit as `jesse@keatingpike.com` and end commit messages with the attribution lines the session
  provides.
