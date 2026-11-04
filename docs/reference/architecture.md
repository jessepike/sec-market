# Architecture

How Security Market Pulse works as of 4 November 2026. This is the current design. The
day-to-day runbook is [github-operations.md](../active/daily-pipeline/github-operations.md); the
reasoning behind the certified tier is in [auto-002-proposal.md](auto-002-proposal.md) and the two
phase specs beside it, which are dated plans.

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
headline metrics such as ARR, ownership text, event summaries and quoted filing text. They come from
company releases, filings and pages, each with its own source and date. The daily collector checks
registered sources and adds new facts only after automated review; they are labeled not certified. The full list is `notCertified` in
[certifiedContract.json](../../web/src/data/tracker/certifiedContract.json).

No machine publishes a judgment: no stance, ranking, forecast or interpretation (D-76). Judgments
appear only when the owner writes them.

## Data flow

```
Vercel Cron (project market-pipeline-timer, ops/timer)      GitHub schedule 05:17 + 09:47 backup
   |  05:17 UTC: workflow_dispatch timer=true                  |  skips once the day has collected
   v                                                           v
subscription-collector.yml  (GitHub Actions, private repo)
   |  restore evidence archive (refs/archive/market-evidence), take the shared lease,
   |  fetch registered sources within the daily budget, Codex CLI on the owner's ChatGPT login
   |  extracts and reviews candidate facts, 12-month history window (contracts/history-window.json)
   v
evidence archive commit + coverage receipt (daily_source_intake_v2)
   |  workflow_run callback (16:23 UTC daily recovery timer)
   v
subscription-publisher.yml  -> market-release-gate.yml on main (independent gate)
   |  verify every archived hash, rebuild the snapshot, replay all 80 SEC claims from archived
   |  bytes, run the full app test suite, export the exact static artifact
   v
Vercel staging without a domain -> byte-for-byte check -> promote -> verify public host
   v
https://securitymarketpulse.com   (production-rollback-drill.yml checks rollback after publishing)
```

Code changes take a separate path: work lands on `preview` (Vercel preview URL), then an approved
fast-forward moves `main`. A push to `main` alone does not publish; the next gated publisher run
does. Vercel Git builds of `main` and automatic domain assignment are off (D-110). The older
four-hour `certified-refresh.yml` and `promote.yml` workflows were removed on 2026-11-04 (D-133).

## Monitoring

| Monitor | Where | What it catches |
|---|---|---|
| Outside watchdog | `ops/timer/api/watchdog`, Vercel Cron every 6 hours | Published `daily-coverage.json` older than 30 hours or unreadable, the latest collector run failed or missing, an expired ChatGPT login. Alerts through one GitHub App issue assigned to the owner; works even when Actions is blocked |
| Freshness probe | `freshness.yml`, every 6 hours at :41 | Coverage, heartbeat and public-release gaps; keeps an owner-assigned issue |
| Job alerts | `ops/ci/job_alert.py` in collector and publisher | A failed run; one assigned issue that closes on recovery |
| Rollback drill | `production-rollback-drill.yml` | A release that cannot be rolled back |

## Safeguards

| Safeguard | Where | What it stops |
|---|---|---|
| 100% SEC gate | `web/scripts/certify-gate.ts`, `claim-gate.mjs` | Publishing when any of the 80 certified claims fails, is missing, or drifts |
| Independent release gate | `market-release-gate.yml`, `ops/ci/stage_gate.py` | Publishing anything not rebuilt from the hashed evidence archive on reviewed `main` code |
| Exact artifact | `ops/ci/publish.py`, `publisher_stage.py` | Production serving bytes other than the gate's artifact |
| Daily budgets | `contracts/market.json`, collector ledger | More than the daily fetch, model-call and document allowance; no paid API fallback (D-128) |
| Two gate runs a day | publisher | Runaway publication |
| Accuracy gate | `web/scripts/sec-verify/event-text.mjs`, data tests, `web/src/data/tracker/invariants.ts` | Malformed machine-written text and broken data invariants |
| Structure guard | `web/scripts/promotion/structure.mjs` | Unreviewed changes to routes, headings, ids, navigation or dated records |
| Push guard | `.githooks/pre-push` | A manual push to `main` without `PROMOTE=1` |
| Pinned actions | all workflows | A third-party action changing under us |

## Repository layout

| Path | What it holds |
|---|---|
| `web/` | The site (Vite, React, prerendered to static HTML) and its data, scripts and tests. See [web/README.md](../../web/README.md) |
| `web/scripts/pipeline/` | The daily collector engine (Python): fetch, extract, review, archive, release |
| `contracts/` | `market.json` (roster, sources, budgets; digest pinned), `history-window.json` (backlog cut), qualification seeds |
| `ops/ci/` | Collector (with its session runtime), gate, publisher, alert and rollback steps run by the workflows, with tests |
| `ops/timer/` | Vercel Cron project: daily dispatch and outside watchdog (D-127) |
| `ops/watchdog/` | Coverage probe used by `freshness.yml` |
| `ops/evaluation/` | Extraction eval (golden set), scorecard and audit scripts |
| `.github/workflows/` | Collector, publisher, release gate, rollback drill, freshness, account probes, web CI |
| `.githooks/` | `pre-push` guard for `main` |
| `docs/` | Current design in `reference/`, work in flight and receipts in `active/`, history in `archive/` |

## Public routes

`/` (tracker), `/coverage/` (all 74 suppliers and their coverage tier), `/issues/` and
`/issues/2026-w36/` (the one signed weekly issue, kept as a dated record), `/thesis/` (the founding
thesis, a dated record), `/corrections/`. Machine-readable: `/tracker.json`, `/feed.xml`,
`/sitemap.xml`, `/corrections.json`, `/certified-coverage.json`, `/daily-coverage.json`,
`/app-release.json`. The `/refresh-*.json` files are frozen receipts from the AUTO-001 phase.

## Hosting and accounts

| Service | Use | Notes |
|---|---|---|
| GitHub `jessepike/sec-market` | Code, Actions, evidence archive | Private. Actions budget $5/month, shared with the owner's other sites (D-129) |
| Vercel `pikeholdings/security-market-pulse` | Site hosting | Production is staged and promoted by the publisher only |
| Vercel `market-pipeline-timer` | Daily timer and watchdog crons | Holds the GitHub App key; nothing else |
| ChatGPT subscription | Model step (Codex CLI) | Owner's login stored as one CI secret (D-109, D-126) |
| Cloudflare | DNS only | See [dns-and-accounts.md](dns-and-accounts.md) |
| SEC EDGAR | Data source | Public API, no key; User-Agent names the site and a contact address |
