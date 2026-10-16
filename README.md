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
- **Fully automated.** GitHub Actions checks SEC filings every 4 hours. A change goes to the preview
  site, then to production a day later after a fresh check reproduces it. Code changes still need
  the owner's approval. No laptop and no secrets. GitHub,
  Vercel and Cloudflare run on free plans; whether Vercel's Hobby plan allows commercial use is
  still to be checked (SEC-061).

Details: [docs/reference/architecture.md](docs/reference/architecture.md).

## Status

Live and updating itself. Current state, open items and next steps: [status.md](status.md).

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
| [.github/workflows/](.github/workflows/) | Scheduled refresh, automatic promotion, freshness probe, CI |
| [.githooks/](.githooks/) | Push guard for `main` |
| [docs/](docs/) | Current design in `reference/`, work in flight in `active/`, history in `archive/` ([docs/README.md](docs/README.md)) |

## Working on it

```bash
cd web
npm ci
npm run dev        # local site
npm test           # lint, data tests, gated build, browser tests
```

Shipping goes through `preview` and the owner's approval: see [AGENTS.md](AGENTS.md) and
[docs/reference/operations.md](docs/reference/operations.md).

## Hosting

Vercel (`pikeholdings/security-market-pulse`, root `web`), Cloudflare DNS, GitHub Actions. The
author hub and email list live at [jessepike.dev](https://jessepike.dev).
