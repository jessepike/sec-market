# What to disable or delete once step 4 lands

For the coordinator, once `docs/active/auto/step4/workflows/edgar-refresh.yml.txt`
and `collect.yml.txt` are copied into `.github/workflows/` by a session with the
`workflow` token scope. Nothing here is done by this build — a scope this
session does not have needs to disable these, and disabling them is itself a
site-behavior change worth the owner seeing happen rather than silently
disappearing.

## Retire

- **`.github/workflows/publish-issue.yml`** and **`scripts/publish-issue.sh`**
  (plus `web/scripts/sign-issue.ts`, the `reconfirm` machinery, and the
  `issue/<id>` → `preview` pull request flow it drives). D-76 already ended the
  weekly-issue-as-signature model for facts; the standing tracker replaces the
  signed weekly issue as the unit of product (D-77). Nothing publishes through
  approving a pull request or commenting `publish` once the tracker is the
  product — that whole path becomes dead code the day step 5 lands the
  per-domain tracker view. Don't delete it the same day step 4 merges,
  though: issue 2026-w36 and any later signed issues stay as the historical
  record, and the code that renders them (`/issues/`) is a separate,
  unrelated concern from the publish workflow. Retire the WORKFLOW and the
  PUBLISHING script; leave the rendering and the archived issues alone unless
  a later step says otherwise.
- **`.github/workflows/gather-pr.yml`** and **`scripts/gather.sh`** (plus the
  macbook2014 launchd job `com.securitymarketpulse.gather` and its
  `~/gather-logs/`). This is the weekly-issue gather that opens the pull
  request `publish-issue.yml` used to wait on. Once nothing signs a weekly
  issue anymore, nothing needs to gather one either. Unload the launchd agent
  on macbook2014 (`launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.securitymarketpulse.gather.plist`
  or the project's own equivalent) before deleting the plist, so it does not
  keep firing into a dead script.
- **Anything else tied to signing**: `web/src/data/reconfirmations.ts` and the
  `--reconfirm` flag stop being written to (no more approvals to carry the
  word), but the file itself is historical record for every stance that was
  ever re-dated under someone's approval — do not delete the data, only the
  path that writes new rows to it. `web/scripts/stale-report.ts` stays; going
  stale is still a real question for a standing tracker, it just stops being
  answered inside a weekly pull request body.

## What `freshness.yml` should additionally check

`freshness.yml` today only checks that `/issues/index.json` has a published
issue newer than `STALE_DAYS` (10). Once the standing tracker is the product
and nothing publishes a weekly issue, that check answers a question nobody is
asking anymore. Add, alongside (not instead of, until the issue path is
actually retired) a check that:

- fetches the live site's `runStatus` — however step 5 ends up exposing it on
  a page (`/`, or a small `/status.json` if one gets built; not this step's
  call to make) — and fails the same way the existing check does when
  `lastChecked` is more than **2 days** old. Two days, not ten: the tracker's
  whole selling point is a daily/twice-weekly pipeline that stays current
  without a human, so a two-day-old `lastChecked` on production means EITHER
  runner has been quietly failing for multiple cycles, which is exactly the
  silent-failure case a freshness probe exists to catch.
- treats `runStatus.state === 'incomplete'` on production as its own alert
  condition (separate title/label from plain staleness), because
  `scripts/auto-publish.sh` can put that state on `main` directly (the
  gate-failure and drift-blocked paths both can, when main already matched
  preview beforehand) — that is a "the automated pipeline is telling you
  something, not just going quiet" signal, worth a different message than
  "nothing has shipped in N days."

Not built here — recorded so step 5 (or whoever builds the tracker's public
surface) has it, since the exact JSON shape to poll depends on how that step
exposes `runStatus` publicly.
