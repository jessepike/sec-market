# Architecture

How Security Market Pulse works as of 16 October 2026. This is the current design; the reasoning
behind it is in [auto-002-proposal.md](auto-002-proposal.md) and the two phase specs beside it.

## What the site publishes

Two kinds of figure, labeled as such on the page.

**Certified.** For 16 public security companies that file structured financial data with the SEC,
the site publishes five claim groups per company (80 claims in all):

| Group | What it is |
|---|---|
| `identity` | Name, ticker and listing status |
| `revenue.latest` | Latest quarterly revenue and its period |
| `revenue.prior` | The same quarter a year earlier, for year-over-year growth |
| `revenue.history` | Up to eight quarters of revenue |
| `secEvents` | SEC filings in the last 12 months that match the filed-event rules (8-K items and forms listed on the Method page) |

Every certified claim is re-derived from SEC EDGAR by a verifier that shares no code with the
producer. Both apply the same XBRL rules, so this is a reproducibility check, not a second method.
The page says "re-derived from SEC filings", never "independently verified".

**Not certified.** Everything else: private companies, segments of larger companies, non-US filers,
headline metrics such as ARR, ownership text, event summaries and quoted filing text. These were
collected earlier from company releases and pages, keep their own source and date, and are not
re-checked automatically. The full list is `notCertified` in
[certifiedContract.json](../../web/src/data/tracker/certifiedContract.json).

No machine publishes a judgment: no stance, ranking, forecast or interpretation (D-76). Judgments
appear only when the owner writes them.

## Data flow

```
SEC EDGAR APIs
   |  every 4 hours (certified-refresh.yml, certify job, read-only token)
   v
edgar-refresh.ts + filing-events.ts   -> web/src/data/generated/*.json
   v
certify-sec.ts (sec-verify/independent.mjs re-derives every claim)
   v
certify-gate.ts                        -> must report 80/80 and zero drift
   v
data tests, allowlist check, certify-changed.mjs (did any certified value change?)
   |  only if complete AND changed (publish job, write token, runs no repo code)
   v
commit of six allowlisted data files to `preview`  -> Vercel preview build
   |  daily at 15:23 UTC (promote-certified.yml)
   |  only if data-only, 24 h soak, and a fresh certification reproduces the values
   v
fast-forward `main`  -> Vercel production build (gated again by certify-gate)
   v
https://securitymarketpulse.com
```

The six allowlisted data files are `edgarFacts.json`, `filingEvents.json`, `filingEvidence.json`,
`filingRun.json`, `certifiedCoverage.json` and `certifiedVerification.json` under
`web/src/data/generated/`.

## Safeguards

| Safeguard | Where | What it stops |
|---|---|---|
| 100% gate | `web/scripts/certify-gate.ts`, `claim-gate.mjs` | Publishing when any certified claim fails, is missing, or drifts from the build inputs |
| Build gate | `web/scripts/app-release.mjs` | A Vercel build of the site when the gate fails; the last good deployment keeps serving |
| Allowlist | `certified-refresh.yml`, `promote-certified.yml` | The bot changing anything except the six data files |
| Two trust levels | `certified-refresh.yml` | The job holding a write token never runs `npm` or repo code |
| Soak and re-check | `promote-certified.yml` | Production moving within 24 hours of a data change, or on values a fresh run cannot reproduce |
| Code blocks automation | `promote-certified.yml` | Any non-data commit on `preview` stops auto-promotion until the owner promotes |
| Held-run issue | `certified-refresh.yml` report job | A failed or incomplete run going unnoticed; one GitHub issue opens and closes on recovery |
| Freshness probe | `freshness.yml`, every 6 hours | The refresh silently stopping (no run in 10 hours) or the site going down |
| Raw-response archive | `sec-archive` workflow artifact, 90 days | Losing the evidence a certified value was derived from |
| Pinned actions | all workflows | A third-party action changing under us; each is pinned to a commit SHA |

## Repository layout

| Path | What it holds |
|---|---|
| `web/` | The site (Vite, React, prerendered to static HTML). Vercel root directory. See [web/README.md](../../web/README.md) |
| `web/src/data/tracker/` | Supplier list, domains, events, the certified contract and the certification helpers |
| `web/src/data/generated/` | Machine-written data. Six files are refreshed by the bot; the rest are frozen records from earlier phases |
| `web/scripts/` | Data refresh, certification, build, prerender and verification scripts |
| `web/scripts/sec-verify/` | The independent verifier and the 8-K Item 2.03 excerpt extractor |
| `web/tests/` | Data tests (`node --test`) and browser tests (`tests/e2e`, Playwright) |
| `.github/workflows/` | `certified-refresh`, `promote-certified`, `freshness`, `web` (CI) |
| `.githooks/` | `pre-push` hook that refuses a push to `main` without `PROMOTE=1` |
| `docs/` | Current design in `reference/`, work in flight in `active/`, history in `archive/` |

## Public routes

`/` (tracker), `/issues/` and `/issues/2026-w36/` (the one signed weekly issue, kept as a dated
record), `/thesis/` (the founding thesis, a dated record), `/corrections/`. Machine-readable:
`/tracker.json`, `/feed.xml`, `/sitemap.xml`, `/corrections.json`, `/certified-coverage.json` (the
certification receipt), `/app-release.json` (what this build is and when it was certified). The
`/refresh-*.json` files are frozen receipts from the AUTO-001 phase and do not change.

## Hosting and accounts

| Service | Use | Notes |
|---|---|---|
| GitHub `jessepike/sec-market` | Code, Actions | Free plan; no branch protection (D-98), so `main` is protected by the hook and the workflows' design |
| Vercel `pikeholdings/security-market-pulse` | Hosting, Web Analytics | Builds `preview` and `main` from Git; commits must be authored by `jesse@keatingpike.com` |
| Cloudflare | DNS for `securitymarketpulse.com` | No email is sent from this domain; SPF `-all`, DMARC `reject`, null MX. See [dns-and-accounts.md](dns-and-accounts.md) |
| SEC EDGAR | Data source | Public API, no key. User-Agent names the site and a contact address; requests stay under 5 per second |

There are no secrets in the repository or in GitHub Actions. The workflows use only the built-in
`GITHUB_TOKEN`.
