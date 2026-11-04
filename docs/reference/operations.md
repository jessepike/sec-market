# Operations

How to run, check and repair Security Market Pulse. For how the system is built, see
[architecture.md](architecture.md). For the rules every agent follows, see
[AGENTS.md](../../AGENTS.md).

## Normal state

Nothing needs a person. Vercel Cron starts the daily collector at 05:17 UTC; GitHub's own schedule
(05:17 and a 09:47 backup) skips once the day has collected. When collection succeeds, the
publisher runs the independent release gate on `main` and publishes the exact artifact if every
check passes. Most days add few or no facts. Coverage gaps stay visible on the page and in
`/daily-coverage.json`. Code changes land on `preview` and reach production only after an approved
fast-forward of `main` and the next gated publisher run.

## Signals that need attention

| Signal | Meaning | What to do |
|---|---|---|
| GitHub issue "Daily pipeline needs attention (outside watchdog)" | Published data older than 30 hours, the latest collector failed or never started, or the ChatGPT login expired | The issue names which. For an expired login, sign in again and refresh the secret with `ops/ci/bootstrap.py`. It closes itself on recovery |
| Collector or publisher job-alert issue | A run failed | Open the linked run. Fix on `preview`, promote, and let the next run recover. Never reset a daily allowance |
| Freshness probe issue | Coverage, heartbeat or public-release gap | Read the issue; ongoing source gaps are expected and are not failures |
| GitHub Actions spend near $5 for the month | Shared Actions budget (D-129) | Check minutes per workflow in GitHub billing before adding scheduled work |

Runbook detail, receipts and recovery rules: [github-operations.md](../active/daily-pipeline/github-operations.md).

## Local commands

Run from `web/`. Node 22.

```bash
npm ci
npm run dev                  # local site at http://localhost:5173
npm run refresh:edgar        # pull SEC XBRL facts for the tracked filers
npm run refresh:filing-events
npm run certify:sec          # re-derive all 80 certified claims
npm run certify:gate         # must print "complete":true, 80/80, drift 0
npm run build                # gated production build into dist/
npm run lint
npm run test:data            # data and logic tests
npm run test:e2e             # browser tests against dist/
node scripts/shot.mjs <url> <prefix>   # full-page screenshots at 1440 and 390 (system Chrome,
                                       # or Playwright's Chromium where Chrome is absent)
```

`npm test` runs lint, data tests, build and browser tests in order.

## Shipping a change

1. Branch from `preview`. Commit as `jesse@keatingpike.com` with a conventional message
   (`type(scope): description`).
2. Run `npm test` from `web/`.
3. Merge into `preview` and push. Vercel builds
   https://security-market-pulse-git-preview-pikeholdings.vercel.app.
4. Before pushing, screenshot production and your build at 1440 and 390 (`shot.mjs`) and compare.
   If anything a reader would notice changed beyond data, or the change is otherwise major
   (AGENTS.md), end the commit message with `Owner-Review: required`.
5. Promote reviewed code with the approved fast-forward (D-110):
   `git checkout main && git merge --ff-only preview && PROMOTE=1 git push origin main`.
   A held major change waits for the owner's yes first.
6. The next gated publisher run delivers it. Confirm the acknowledged release and
   `https://securitymarketpulse.com/app-release.json` before reporting it live.

Install the push hook once per clone: `./.githooks/install`.

## Rolling back

- **Production shows something wrong:** use Vercel Instant Rollback to the previous production
  deployment (the publisher's own rollback route is in the runbook), then fix forward on `preview`.
- **A bad commit on `preview`:** `git revert <sha>` on a branch, merge to `preview`. Never
  force-push `preview` or `main`.
- **A wrong published fact:** publish a dated correction; records change only through corrections
  (D-68). The publisher can also roll back to the retained previous release (see the runbook).

## Adding a certified company

A company qualifies if it files 10-Q and 10-K reports with XBRL revenue under its own name.

1. Add it to `web/src/data/edgarRegistry.ts` (CIK) and `web/src/data/tracker/suppliers.ts`.
2. Add its id to `supplierIds` in `web/src/data/tracker/certifiedContract.json` and bump `version`.
3. Run the refresh and certification commands above. The gate must reach 100% with the new company
   included before the change ships.
4. Ship it as a major change (`Owner-Review: required`). A contract change is a decision; log it in
   [decisions.md](../../decisions.md).

## Accounts the owner holds

GitHub, Vercel and Cloudflare are under the owner's accounts, with passkey and two-factor sign-in.
Agents do not create tokens or copy credentials into CI (D-83). Open account items are
backlog item SEC-061 in [BACKLOG.md](../../BACKLOG.md).
