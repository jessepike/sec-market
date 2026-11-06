---
project: Security Market Pulse
stage: Operate
updated: 2026-11-06
---

# Current state

**Company request box (2026-11-06, on preview, owner review).** "Want a company tracked?" under the company search sends a name to a private GitHub issue through `ops/timer/api/request.js` (D-136, SEC-081). It works once `main` advances, since the timer project deploys from `main`.

**Front page hierarchy (2026-11-04, on preview, owner review).** Pipeline status lines moved from the masthead into the Data status section (`#overview`), leaving a one-line disclaimer and link up top. Count tiles lead with the last 30 days and show the 12-month total small. The 12-month grid shades cells by count. Panel and domain card headers have a tinted band. Public supplier rows say "Quarter ended". Check Point and Trend Micro have no automated path to a new quarter (SEC-080).

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
