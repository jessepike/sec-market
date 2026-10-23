# Security Market Pulse

https://securitymarketpulse.com

A public tracker of the business of the security market. For 74 security suppliers across 12 market
domains it shows reported revenue and growth, funding rounds, acquisitions, restructuring, debt and
leadership changes, each with its source and date. It is written for security leaders and the people
who advise and sell to them. It publishes facts, not opinions.

## How it works

- **Certified figures.** For 16 public companies that file structured data with the SEC, the site
  re-derives name and ticker, quarterly revenue, year-over-year growth, up to eight quarters of
  history, and SEC-filed events straight from EDGAR. All 80 claims must pass before anything
  publishes.
- **Everything else** was collected from company releases and pages, keeps its own source and date,
  and is labeled as not certified on the page.
- **Daily operation.** Private GitHub Actions collects bounded source changes at 05:17 UTC daily.
  A separate publisher runs after successful scheduled collection and at 06:23/16:23 UTC. It
  replays the SEC claims, tests the exact artifact, uploads it to the existing Vercel project and
  verifies production bytes. Public facts may publish after these checks; market judgments remain
  owner-written. Coverage gaps remain visible. The existing protected GitHub secrets supply the
  subscription account and publisher; Codex Cloud and a running laptop are not dependencies.

Current operation: [GitHub/Vercel runbook](docs/active/daily-pipeline/github-operations.md).
Architecture: [docs/reference/architecture.md](docs/reference/architecture.md).

## Status

The approved daily pipeline is live. Actual scheduled collection, exact-artifact publication and
controlled rollback/restoration passed on October 23, 2026. Source coverage remains incomplete.
Current state and receipt links: [status.md](status.md).

## Repository

| Path | What it holds |
|---|---|
| [intent.md](intent.md) | Why the project exists, who it serves, what it must never do |
| [AGENTS.md](AGENTS.md) | Rules for any agent working here: deploy path, visual review, content rules |
| [CLAUDE.md](CLAUDE.md) | Claude-specific additions to AGENTS.md |
| [status.md](status.md) | Current state, one page |
| [BACKLOG.md](BACKLOG.md) | Open work |
| [decisions.md](decisions.md) | Every decision since 2026-08-15, with an index of those in force |
| [lessons.md](lessons.md) | Working lessons for agents |
| [.claude/rules/](.claude/rules/) | Hard constraints |
| [web/](web/) | The site and its data, scripts and tests ([web/README.md](web/README.md)) |
| [.github/workflows/](.github/workflows/) | Daily collection, exact-artifact gate/publisher, independent monitoring, CI |
| [.githooks/](.githooks/) | Push guard for `main` |
| [docs/](docs/) | Current design in `reference/`, work in flight in `active/`, history in `archive/` ([docs/README.md](docs/README.md)) |

## Working on it

```bash
orb run -m dev bash -lc 'cd /mnt/mac/Users/jessepike/code/projects/sec-market/web && npm ci && npm run dev'
# In another terminal, run lint, data tests, gated build and browser tests:
orb run -m dev bash -lc 'cd /mnt/mac/Users/jessepike/code/projects/sec-market/web && npm test'
```

Shipping goes through `preview` and the owner's approval: see [AGENTS.md](AGENTS.md) and
[docs/active/daily-pipeline/github-operations.md](docs/active/daily-pipeline/github-operations.md).

## Hosting

Vercel (`pikeholdings/security-market-pulse`, root `web`), Cloudflare DNS, GitHub Actions. The
author hub and email list live at [jessepike.dev](https://jessepike.dev).

The legacy SEC-only refresh and promotion schedules are disabled. The daily collector covers the
declared roster subject to explicit source and budget gaps; it does not claim every supplier is
fresh. [Activation receipts](docs/active/daily-pipeline/activation-2026-10-23.md) record what ran.
