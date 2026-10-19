# Operations

How to run, check and repair Security Market Pulse. For how the system is built, see
[architecture.md](architecture.md). For the rules every agent follows, see
[AGENTS.md](../../AGENTS.md).

## Normal state

Nothing needs a person. Every 4 hours the certified refresh runs; most runs find no new filing and
publish nothing. When a tracked company files something, the data lands on `preview` and reaches
production 6 to 10 hours later through `promote.yml`. Routine code and docs changes reach production
about a day after they land on `preview`. Major changes wait for the owner (AGENTS.md). Scheduled
GitHub runs often start late and sometimes skip a slot; the freshness probe alarms only on real gaps.

## Signals that need attention

| Signal | Meaning | What to do |
|---|---|---|
| GitHub issue "Certified refresh held" | A run failed or fell below 100% | Open the run linked in the issue. Download the `certified-data` artifact and read `.collect/certified-attempt.json` for the blockers. Fix the cause on a branch, merge to `preview`, promote. The issue closes itself on the next good run |
| GitHub issue "Site freshness" | The probe found a gap: no refresh in 10 hours, no successful promotion in 30, certified data waiting over 48, production not serving `main` for 2, or the site down | The issue names which. Check the Actions tab and the Vercel dashboard |
| GitHub issue "Owner review needed" | A major change is held on `preview` (marked, protected path, new secret, or page structure changed) | The owner reviews the preview and promotes (below). Data behind it waits too |
| GitHub issue "Automatic promotion failed" | A promotion run failed: tests, build, or `main` not an ancestor of `preview` | Read the run log, fix on `preview`. The issue closes on the next good run |
| `promote` run green with a notice | Normal: nothing to promote, still soaking, or SEC has newer data than the candidate | Nothing |
| Vercel build failed with "Certified tier failed its gate" | The build gate refused the data | Production keeps serving the last good build. Run the gate locally (below) to see why |

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
5. Routine changes reach production through `promote.yml` once checks pass. For a held change, send
   the owner the preview URL and screenshots; after the owner says yes:
   `git checkout main && git merge --ff-only preview && PROMOTE=1 git push origin main`.
6. Confirm the Vercel production deployment is Ready and `curl https://securitymarketpulse.com/app-release.json`.

Install the push hook once per clone: `./.githooks/install`.

## Rolling back

- **Production shows something wrong:** in Vercel, open the previous production deployment and use
  Instant Rollback. This changes what is served immediately and touches no Git history. Then fix
  forward on `preview`.
- **A bad commit on `preview`:** `git revert <sha>` on a branch, merge to `preview`. Never
  force-push `preview` or `main`.
- **Bad certified data reached `preview`:** revert the `data(auto)` commit. The next refresh
  re-derives the data from SEC; if the cause is in the code, fix it before the next run or it will
  recur.

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
