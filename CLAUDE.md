# Security Market Signal Pipeline

@AGENTS.md

> Project context lives in AGENTS.md (canonical). This file imports it for Claude-specific sessions.

## Publishing to the live site — read this before touching `web/`

`main` is production. A push to `main` publishes to https://securitymarketpulse.com with nobody between the commit and the public site.

- **Never push a `web/` change to `main`.** Push a branch, get the Vercel preview URL, and ask the owner. Merging to `main` is his call, not yours.
- **Render the page and look at it** before you claim anything about how it looks. `node scripts/shot.mjs <url> <prefix>` from `web/` captures full-page images at 1440px and 390px. Compare production against the preview and say what moved.
- **Never delete a component, CSS rule, or export because static analysis says it is unused.** Prove it with a before/after render.
- When you report, separate invisible work (SEO, prerendering, bundle size, citations, accessibility) from visible work (layout, type, colour, hierarchy). If nothing visible changed, say that first.

Full contract: [AGENTS.md](AGENTS.md) § Production deploy and § Visual review before publish.

## Context Map (progressive disclosure)

**Always loaded:** Root artifacts — `intent.md`, `BACKLOG.md`, `status.md`, `decisions.md`

**Default working zone:** `docs/active/`

**Load on demand:**
- Gate chain and episode packet → `docs/reference/`
- Manual method → [market-signal-runbook.md](docs/reference/market-signal-runbook.md)
- Historical hypotheses → `docs/archive/` (explicit instruction only)

**Never load automatically:** `docs/archive/`, `.ctx/`
