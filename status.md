---
project: Security Market Pulse
stage: Operate
updated: 2026-11-07
---

# Current state

**Application and AI security coverage (2026-11-07, D-146, on preview, owner review).** Five more onboarding suppliers (Checkmarx, Black Duck, Semgrep, Endor Labs, Noma) in the additive roster transition, now 87. Every domain card on the front page lists its private, acquired and segment companies as rows with their latest funding, ownership or deal, so cards without SEC filers (MDR, email, OT) now show. AI security has no revenue bars and three sub-areas (usage control, app and model protection, agents).

**Site health check (2026-11-06).** One GitHub issue titled "Site health: OK" (or "N failing") is the status page. `ops/timer/api/health.js` rewrites it hourly from Vercel with 16 checks and comments only when a check newly goes bad or all recover. The collector records evidence size and free runner disk for it (`evidence-disk` annotation). Live once `main` advances, since the timer project deploys from `main`. Since 2026-11-07 it also starts the publisher when a finished gate has no publisher run after it (split release, below).

**Split release (2026-11-07, on preview).** The publisher dispatches the independent gate and exits; the gate's completion callback imports its artifact and publishes. This removes the 10-20 billed minutes a day the publisher spent waiting. Budget and idempotence are unchanged (`web/scripts/pipeline/release.py` `release_daily(split=True)`, `pending-gate` head). Proven on main 2026-11-07: GitHub does not start the callback for a gate the workflow token dispatched, so the outside timer's `/api/finish-gate` (every 10 minutes) starts the publisher once the gate finishes.

**Funding rounds feed (2026-11-06, on preview, owner review).** `/funding/` lists security funding rounds by week, each confirmed against the source the Return on Security list links to, and companies newly listed on five cyber investor portfolio pages. `funding-weekly.yml` (Mondays 07:41 UTC, about 1.5 runner minutes) commits `web/src/data/funding/feed.json` to `preview`. Separate from the daily collector and the roster (D-140, SEC-084).

**Agent access (2026-11-06, on preview, owner review, D-139).** New `/data/` page and "Data" nav link; `/llms.txt`, `/index.md`, `/tracker.csv`, `/events.json`, `/events.csv`, a certified flag and source dates on every figure in `/tracker.json`, CC BY 4.0, robots Content-Signal. Built in `web/src/data/agentExport.ts` and `web/scripts/generate-agent.ts`. Checked on the preview: files serve with the right types. Same-URL Markdown on `Accept: text/markdown` does not work on a static Vercel site (the HTML file wins over a rewrite), so pages link their `.md` copy instead. Per-company pages (option B) added: `/companies/<slug>/` for all 74 suppliers with figures, SEC quarterly revenue and 12-month events, plus `index.md` and `data.json` copies; linked from `/coverage/` and the supplier record; `pageUrl` in `/tracker.json`.

**Company request box (2026-11-06, on preview, owner review).** "Want a company tracked?" under the company search sends a name to a private GitHub issue through `ops/timer/api/request.js` (D-136, SEC-081). It works once `main` advances, since the timer project deploys from `main`.

**Front page hierarchy (2026-11-04, on preview, owner review).** Pipeline status lines moved from the masthead into the Data status section (`#overview`), leaving a one-line disclaimer and link up top. Count tiles lead with the last 30 days and show the 12-month total small. The 12-month grid shades cells by count. Panel and domain card headers have a tinted band. Public supplier rows say "Quarter ended". Check Point now reads its 6-K results releases and shows the quarter ended 2026-09-30; it rolls automatically once SEC-083 adds its SEC sources. Trend Micro still has no automated path (SEC-080).

**Landing redesign (2026-11-06, on preview, owner approved the preview).** Front page: search, event tiles with one hue and icon per type, the five newest events as one line each (status and labelled dollar figure; a click opens the side pane), then "Company revenue growth" by domain or all domains with TTM operating and FCF margins. The 12-month heatmap, full growth chart, supplier list and domain index moved to a new `/market/` page. Company pages open with growth and health and keep an SEC filings ledger; `/filings.csv`. Margins come from a static snapshot (`web/src/data/generated/healthFacts.json`, `web/scripts/health/`) and are not yet in the daily refresh or the certified contract. Next: the nav, bottom-section and site-wide styling pass after the UX and consistency review.

**One page shell and new nav (2026-11-07, on preview, owner approved P1 and P2 of the UX review).** Every page uses the landing style: no dark top bar, one header, footer and panel and table style. Nav is Market, Companies (`/coverage/`), Venture rounds (`/funding/`), How this works (new `/method/`, holding Data status, How this is built and the evidence library). The landing page ends after Company revenue growth. Review: `/mnt/project-files/ux-consistency-review-2026-11-06/synthesis.md`. Open: item 12 (publisher commits the snapshot to preview, `.github/`, own owner review) and item 13 (request box on the live host).

**Cyber resilience domain (2026-11-06, D-144, on preview).** Rubrik, Commvault, Cohesity and Veeam show under a new Cyber resilience domain; Data security keeps Varonis, Cyera and BigID. Applied at display (`displayDomainIds`); `contracts/market.json` and `originals.json` still say `data` until the next contract transition.

**No count line (2026-11-06, D-142, on preview).** The homepage line "N suppliers · N domains · N SEC filers certified" and the supplier counts in page text are gone. `/coverage/` and `/data/` keep their computed counts.

**Coverage expansion (2026-11-06, D-138, on preview).** Eight suppliers (F5, Akamai, Aikido, 7AI, Straiker, Lumos, Skyflow, Secuvy) have sourced seed records in `web/src/data/tracker/onboarding.json` and show on preview only, in a "Being onboarded" section of `/coverage/`. Production is pixel-identical. The contract now lists them (82 suppliers, D-141) through a reusable additive transition that also adds Check Point's SEC sources and the Optiv closing release. Their daily data is held off every page until they graduate after three clean runs. Next: promote, run the first collection on the new contract, then build the graduation check.

The site is live and updates itself. Production (`main`) and `preview` were level at ed9cce8 on
November 3; preview is now ahead by the contact-email change and this docs cleanup.

## How it runs today

- **Daily clock (D-127, live).** Vercel project `market-pipeline-timer` (`ops/timer`) starts the
  collector at 05:17 UTC through GitHub App `market-pipeline-timer-f0e3`. GitHub's own `17 5` and
  `47 9` schedules are the backup and skip once the day has collected. The first test dispatch ran
  November 3 at 21:59 UTC (run 41726710177) and correctly skipped. The first real cron fire is
  November 4 at 05:17 UTC.
- **Outside watchdog (D-127, live).** Every 6 hours it checks for stale data (over 30 hours), a failed
  or missing collector run and an expired ChatGPT login, and alerts through one assigned GitHub issue.
- **Model route (D-126, D-128).** Codex CLI on the owner's ChatGPT subscription, one CI secret. The
  API-key fallback is deferred (SEC-075).
- **Publishing (D-110).** After collection, the publisher runs the independent gate on `main`,
  replays all 80 SEC claims and publishes the exact artifact. The gate allows 2 runs a day. A `main`
  push alone does not publish.
- **Budget (D-129).** GitHub Actions $5/month, shared with the owner's other sites. Forecast about
  59 Linux minutes a day for this site; actual monthly spend is not yet measured (SEC-078).

## Shipped November 2 to 3 (on main)

Company search in the header, the `/coverage/` page with data-derived tiers (D-131), the phone
layout fix, the timer and watchdog, and the backlog cut (D-130: 12-month history window and a
supplier-mention check before model calls, set in `contracts/history-window.json`). The backlog
cut shows on the page as "N archived as older than 12 months" once a real run records it.

## Accuracy

- First scored extraction eval (extraction step only, 30-case golden set): recall 95.8%, precision
  45.1%, date accuracy 66.7%, no facts on the 10 non-event pages.
  [Report](docs/active/daily-pipeline/evaluations/2026-11-03/extraction-eval.md). Most false positives
  are background facts the review step may reject; scoring that step is SEC-077.
- Optiv's 2026-05-08 closing date is right but cites the March 16 announcement. The owner approved
  the fix; it waits for the next accepted contract change (D-132, SEC-076).
- Site invariants (`web/src/data/tracker/invariants.ts`) pass on current data.

## Coverage (November 2 run)

Intake 262 of 557 source checks, with 295 gaps (254 missing bindings, 23 candidates, 16 transport,
2 schema). Processing 83 of 11,671 reviewed, 20 held, queue 51. All 80 SEC claims passed and all 52
public files matched. [Scorecard](docs/active/daily-pipeline/evaluations/2026-11-02/observation.md).

## Next

1. Watch the first real timer runs from November 4 and start counting clean days (SEC-062).
2. Close source gaps (SEC-071) and score the review step (SEC-077).
3. Measure Actions minutes against the $5 budget (SEC-078).
4. Owner decision waiting: email workstream inputs (SEC-060). Intent v1.5 was accepted November 4
   (D-135).

Unused runtimes (Codex Cloud, local worker, Cloudflare) and the two legacy workflows were removed
on November 4 (D-133). The collector's session runtime moved to `ops/ci/session_runtime.py`.

Plan and review write-up: https://claude.ai/artifact/Y9j74zYsvEWWeMxMrYocwj
