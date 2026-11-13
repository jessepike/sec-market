# Repair loop

The daily pipeline repairs itself in two layers. Each one either fixes what it finds or hands it on
with the cause. Nothing stops at "reported".

| Layer | Where | How often | Does |
|---|---|---|---|
| Doctor | `ops/timer/lib/doctor.js`, Vercel Cron `/api/doctor` | every 10 min | Sorts the day into a known case and takes one bounded step. No AI, no Actions minutes |
| Repair step | Claude scheduled task "Pipeline repair" (this runbook) | 00:37, 07:37 and 14:37 UTC | Fixes the cause of anything the doctor hands on, ships the fix, checks it worked |
| Owner | Jess, in the project thread | only for a decision | Picks an option from a recommendation |

The health issue ("Site health: ...") and the watchdog stay as they are. They describe the state.
The doctor and the repair step act on it.

## Cases

The doctor runs two tracks side by side: today's collection, and the release of the newest good
collection. Every limit is counted from GitHub's run list, so it keeps no state and cannot act twice.

| Case | Meaning | Doctor step (limit) | Hands on to |
|---|---|---|---|
| `COLLECT_TIMEOUT` | Collection hit the job limit, saved nothing | start one more collection (1 extra a day, not after 22:00 UTC) | repair, if it also timed out yesterday or the retry fails |
| `COLLECT_FAILED` | Collection failed for another reason | same as above | repair, if the retry fails |
| `NO_COLLECTION` | Nothing started by 06:00 UTC | start one | repair, if that fails |
| `RELEASE_NOT_STARTED` | Collection done 30 min ago, no gate since | start the publisher (once an hour, 3 a day) | repair after 3 |
| `GATE_BUDGET_USED` | The gate allowance is used, collection waiting. The gate allows 2 attempts per code revision and 4 in total each UTC day (D-150) | a fix on main gets its own attempts: start the publisher; otherwise wait for 00:05 UTC | repair, if refused |
| `GATE_FAILED` | Gate refused on the same code | none: a retry would fail the same way and burn an attempt | repair |
| `PUBLISH_STORM` | 3+ publisher runs refused in 2 h, no gate | none; the doctor's own starts are capped | repair |
| `PREVIEW_RED` | Preview's newest web CI run failed | none | repair: fix the test or code before anything is promoted |
| `STALE_UNEXPLAINED` | Live data over 30 h old, no case fits | none | repair |
| `LOGIN_EXPIRED` | ChatGPT login expired | none (a collection cannot succeed) | owner |

Replays of the real Nov 10-12 runs are the tests (`ops/timer/lib/doctor.test.js`). Add a replay for
every new failure the loop meets.

## The repair step

Each run:

1. `env -u GITHUB_TOKEN node ops/timer/doctor-cli.mjs --json --live-at <iso>` on `preview`. The
   cloud sandbox cannot reach the live site, so read `checkedAt` from
   `https://securitymarketpulse.com/daily-coverage.json` with the Vercel connector
   (`web_fetch_vercel_url`, then grep `checkedAt`; the file is about 2 MB) and pass it in. Exit 0
   means nothing to repair: update the checklist and end without a message.
2. For each finding handed to `repair`, find the cause from evidence: the failed run's log
   (`gh run view <id> --log-failed`), the gate's failing test, the collector's `phase` timing lines,
   recent commits on `main`. Write the cause in one sentence before changing anything.
3. Fix the cause, not the symptom. Add a doctor replay or a pipeline test that fails without the
   fix. Run the checks AGENTS.md requires, push `preview`, then promote within what the owner allowed
   (below). A failed gate on unchanged code gets a fix first; the doctor retries the release once
   `main` changes.
4. Confirm the outcome on the next run: the doctor reports `OK` or `WAITING`, and the live data is
   from today's collection. If the same case comes back the next day, the fix did not work: say so
   and try another cause.
5. Record a new failure kind in `lessons.md` and add its case to the doctor if it can be handled
   without judgment.
6. Message the owner only for a decision: what broke, the cause, the options, and a recommendation.

### What the repair step may change on its own

Pending the owner's answer of 2026-11-12 (recommended: routine fixes plus job limits within a range).

- Routine code and data fixes: yes, through preview and the approved main promotion (D-110).
- Job time limits in `.github/workflows/`: up to 120 minutes for the collector, with
  `Owner-Review: required` noted in the commit, if the owner allows it.
- Never alone: the gate's checks or its daily attempt budget, the certification chain, secrets,
  content rules, anything a reader would notice. Those wait for the owner with a recommendation.

## Guardrails

- Never dispatch workflows from the repair step: cloud tokens are refused (403), and the doctor
  owns every start so its limits hold.
- One promotion per incident. Do not promote while the gate or publisher is running.
- The repair step and the daily 08:43 loop both promote. Both use `--ff-only`; whichever runs second
  promotes what is new or nothing.
