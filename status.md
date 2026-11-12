---
project: Security Market Pulse
stage: Operate
updated: 2026-11-12
---

# Current state

**Repair loop (2026-11-12, on preview, owner asked).** Nov 11 and 12 did not publish: the 05:17 collection hit the 45-minute limit both days, GitHub's backup collected 7 to 8 h late, and the gate then failed a test on the registry change (fixed in aa4b7d5 after both attempts were used). The health check and watchdog saw it and only reported. Now `ops/timer/lib/doctor.js` (Vercel Cron every 10 min, live once `main` advances) sorts each day into a known case and takes one bounded step (one extra collection, a publisher start after the 00:05 UTC gate reset), and a Claude scheduled task "Pipeline repair" fixes what the doctor hands on. Runbook: `docs/reference/repair-loop.md`. Open: the owner's answer on how far the repair step may promote on its own; the finish-gate loop fix belongs to the architecture thread.

**Public repository cutover (2026-11-10, D-149).** The evidence archive and the health, company request and improvement-loop issues live in `jessepike/sec-market-private` (issues #1 requests, #2 Site improvements, #3 Site health). Runners reach the archive with the deploy key `SMP_EVIDENCE_DEPLOY_KEY`; the timer writes issues through `ISSUES_REPO`; Issues are off here. The first daily run on this route passed 2026-11-10 05:17 UTC. Pre-cutover run logs and receipt files are erased. The old ref was deleted 2026-11-10; its commits may still resolve by id until GitHub cleans up (owner accepted). The repository went public 2026-11-11 00:27 UTC.

**Pipeline efficiency plan (2026-11-09, D-148, on preview, owner chose all five steps).** Built and off by default, so the daily run is unchanged: `gate.py --rehearsal` (rebuilds candidate code under the archived run's contract and writes only `rehearsal-receipt.json`; not yet wired into `market-release-gate.yml`), an optional `model.extractModel` in the contract for a smaller first-pass model (not set), and `ops/evaluation/model_tier_eval.py`. Measured: gpt-6-luna kept 11 of 11 published-fact pages and 33 of 36 pages with any finding on the first 80 of 193 checked pages; the other 113 are still to run on the owner's Mac. Next: confirm the CI Codex version accepts the model name, set `extractModel` through a contract transition, order the model queue by likely news and skip pages with no business words, a one-day test at 240 calls, then the SQLite index for evidence bookkeeping (the one approved exception to "no database"). Review: https://claude.ai/artifact/6C82atZF4nAGjz3ire17jV

**Front page states facts (2026-11-09, D-147, on preview, owner said go 2026-11-10).** From the reader-value review. The 30-day feed shows one entry per event and one per deal, and each line states the fact: results read "Revenue $179M +30.9% year over year" with the quarter before, a later merger proxy is a step inside its deal ("Proofpoint acquiring Varonis, $6.3B, preliminary merger proxy filed"), leadership lines name the person when the source does. An SEC notice that names no person, amount or deal is left to the company pages and `/filings.csv`, and the tiles count the same entries the feed lists. Growth rows carry quarterly revenue and a trend line of the year-over-year rate over the quarters on file. All domains opens with a chart of growth against free cash flow margin for the SEC filers. Private, acquired and segment rows show the date and age of their newest dated fact. The Market page growth chart opens sorted by value. Landed on `preview` after the 2026-11-10 05:17 UTC run published; it ships with that day's promotion. Deferred: a longer trend needs 12 quarters in the SEC series (certification chain), names for 8-K item 5.02 events need the AI step, and the "my vendors" view waits on the owner.

**Weekly improvement loop (2026-11-08, owner approved).** A Claude scheduled task, "Weekly site improvements", runs Sundays and follows `docs/reference/improvement-loop.md`: a deterministic scorecard (`web/scripts/improve/scan.ts`) of gaps against the product question, the company request queue and a review of local renders, then at most five ranked ideas on the "Site improvements" issue. Data fixes ship on their own; features land on preview with `Owner-Review: required` and wait for a "go" on that issue. One preview push per run, no workflows of its own, 0 Actions minutes for the AI step. First run 2026-11-08: 5 ideas on issue #28, nothing shipped (Actions minutes check red); report `docs/active/improvement-loop/2026-11-08.md`.

**Application and AI security coverage (2026-11-07, D-146, on preview, owner review).** Five more onboarding suppliers (Checkmarx, Black Duck, Semgrep, Endor Labs, Noma) in the additive roster transition, now 87. Every domain card on the front page lists its private, acquired and segment companies as rows with their latest funding, ownership or deal, so cards without SEC filers (MDR, email, OT) now show. AI security has no revenue bars and three sub-areas (usage control, app and model protection, agents).

**Site health check (2026-11-06).** One GitHub issue titled "Site health: OK" (or "N failing") is the status page. `ops/timer/api/health.js` rewrites it hourly from Vercel with 16 checks and comments only when a check newly goes bad or all recover. The collector records evidence size and free runner disk for it (`evidence-disk` annotation). Live once `main` advances, since the timer project deploys from `main`. Since 2026-11-07 it also starts the publisher when a finished gate has no publisher run after it (split release, below).

**Split release (2026-11-07, on preview).** The publisher dispatches the independent gate and exits; the gate's completion callback imports its artifact and publishes. This removes the 10-20 billed minutes a day the publisher spent waiting. Budget and idempotence are unchanged (`web/scripts/pipeline/release.py` `release_daily(split=True)`, `pending-gate` head). Proven on main 2026-11-07: GitHub does not start the callback for a gate the workflow token dispatched, so the outside timer's `/api/finish-gate` (every 10 minutes) starts the publisher once the gate finishes.

**Release recovery and collector time (2026-11-08, on main).** A failed gate is retried as soon as a fix reaches `main`: `finishGate` starts the publisher once when the newest gate failed and main's checks finished after it (db6225c). The collector reserves 25 minutes for closing work (0d70ad8) and builds the snapshot from the reconcile it just ran (66976fc, ~4 minutes saved, identical output). Nov 9 run: 32 minutes, 293 of 671 sources, limited by the 80-call model budget more than by time. After each release the publisher copies the accepted data to `preview` (first copy 304656a, Nov 9). Promote `main` after 00:00 UTC once the day's two gate attempts are used. On Nov 11 the first run with the eight graduated companies and the private evidence repository was cancelled at the 45-minute limit during closing work, so nothing was recorded. The job limit is now 90 minutes with a 60-minute closing reserve, and the collector prints the seconds each phase took (`phase` lines in the collect step log). Read those before changing the numbers again.

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
