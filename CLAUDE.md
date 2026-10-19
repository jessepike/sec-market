# Security Market Pulse

@AGENTS.md

AGENTS.md is canonical for every runtime. This file adds only what is specific to Claude sessions.

## Before touching `web/`

`main` is production, and `promote.yml` moves it to `preview` automatically once checks pass. So a
push to `preview` is a push to the public site, a day later, unless the change is held.

- Never commit or push to `main` yourself, except the owner-approved promotion command.
- Render the page and look at it before pushing (`node scripts/shot.mjs <url> <prefix>` from `web/`,
  1440px and 390px). Anything visible beyond data is major: add `Owner-Review: required`.
- Never delete code, CSS or data because static analysis says it is unused. Prove it with a
  before/after render.
- When reporting, separate invisible work from visible work. If nothing visible changed, say so first.

## Context map

- **Always loaded:** `intent.md`, `status.md`, `BACKLOG.md`, `.claude/rules/`, and the "Decisions in force"
  index at the top of `decisions.md` (open individual entries only when needed; the ledger is long)
- **Current design:** `docs/reference/` (start with `architecture.md`)
- **Work in flight:** `docs/active/`
- **Never load automatically:** `docs/archive/`, `.ctx/` (local, uncommitted agent scratch context)

## Working habits

- Do not use `pkill -f` with a pattern that also appears in your own command line; it kills the
  shell running it.
- Commit as `jesse@keatingpike.com` and end commit messages with the attribution lines the session
  provides.
