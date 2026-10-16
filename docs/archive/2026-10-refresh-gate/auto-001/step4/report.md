---
id: SEC-MARKET-AUTO-001-STEP4
status: built on mon/autopublish, worktree only — no push scope for .github/workflows/
owner: Jesse Pike
author: build session, worktree sec-market-wt/autopublish
---

# Step 4: the automatic publish path

Builds `docs/archive/2026-10-refresh-gate/autonomy-coverage-plan.md` §5 step 4 — "Auto-publish path
(data-only merge to `main` on passing checks); retire the approval workflow."
No human approves a data publish (D-76). The only gates are the ones a
machine can check for itself.

## How it works

`scripts/auto-publish.sh` is called by a collector workflow (the edgar and
collect drafts in this directory) from the same checkout that just committed
data to a short-lived branch, `data/<runner>-<timestamp>`, pushed to GitHub.
It makes one of four decisions, in this order:

1. **Any file outside the data allowlist → refuse, nothing publishes.** The
   allowlist is `web/src/data/generated/**`, `web/src/data/tracker/events.ts`,
   `web/src/data/tracker/suppliers.ts`, `web/src/data/evidence.ts`, and
   `web/src/data/runStatus.ts`. A code or layout change never reaches
   production through this path, full stop — `AGENTS.md`'s "owner says yes"
   rule for `web/` still governs everything else. This is the one outcome
   that exits non-zero (the run shows failed in the Actions tab), because it
   means something tried to ship code through the data path, which is worth
   noticing rather than quietly absorbing.

2. **Gates fail → nothing from the branch publishes; a small `runStatus`-only
   commit says so.** `npm ci`, `npm run test:data`, and `npm run build` run
   against the branch's own content before anything is pushed anywhere. On
   failure, the script builds a separate commit — touching only
   `runStatus.ts`, `state: 'incomplete'`, `failedSources: ['<runner>']` — on
   top of `origin/preview` as it stood before this run, and pushes that to
   `preview` always, and to `main` too if `main` already matched `preview`
   beforehand. The failed data itself never lands anywhere; the short-lived
   branch stays on GitHub as the record of what was attempted. Exits 0 — the
   plan says not to page for an ordinary collection failure.

3. **Gates pass, but `main` already carries unreviewed site work → data lands
   on `preview` only.** Checked once, before any push, as a diff between
   `origin/main` and `origin/preview` that excludes only the five allowlisted
   paths — not the record-keeping exclusion (`docs/`, `status.md`, etc.)
   `publish-issue.sh` uses. That is a deliberate difference: this script
   publishes to production far more often and completely unattended, and it
   errs toward "only ever touches what it's allowed to" over "usually fine to
   promote everything else along with it." If it turns out to starve real
   publishes in practice — a routine `status.md` edit on `preview` blocking
   every automated run until the next promotion — loosening the exclusion
   list is an owner call, not one this script should make for itself. In this
   case the data still lands on `preview` (tested, gate-passed), followed by
   a `runStatus`-only commit reading `state: 'incomplete'`,
   `failedSources: ['site changes waiting for review']`, also on `preview`
   only. `main`, and therefore production, is untouched. Exits 0.

4. **Gates pass and `main` matches `preview` → publishes.** The branch lands
   on `preview` (fast-forward, or one merge-and-retry if another run moved
   `preview` in between — never a force-push), then the same commit
   fast-forwards `main`. The `main` push goes through the repo's own
   `.githooks/pre-push` hook (installed by the script itself if not already
   present) with `PROMOTE=1`, the same convention every other path to
   production in this repo already uses.

Every run writes a JSON receipt — runner, branch, changed paths, each gate's
name and pass/fail, whether it published and to where, and the reason — to
`$GITHUB_STEP_SUMMARY` (GitHub Actions sets this automatically; the script
also prints to stdout when it's unset, for a local run).

`web/src/data/runStatus.ts` is edited in place with a scoped regex against its
`export const runStatus: RunStatus = { ... }` block — reads the current three
fields, rewrites them, leaves everything else (the type, the interface, the
comments) untouched. If that block's shape ever changes in a way the regex
doesn't recognize, the edit refuses loudly (`process.exit(1)`) rather than
writing something malformed.

## What this deliberately does not do

Unlike `scripts/publish-issue.sh`, this script does not split into a
token-less guard/build phase and a separate token-bearing release phase. The
collector workflows run collection and publishing in one job, so a
write-scoped token sits in the job's environment for the whole run, including
while `npm ci`/`npm run build` execute. The allowlist guard still stops a
branch from carrying an unexpected file before any of that runs, but it does
not isolate the token from whatever those npm scripts pull in the way
`publish-issue.sh`'s trusted second checkout does. That is the same open door
BACKLOG SEC-051 already names for the weekly job's deploy key — worth closing
for both together, not solved here, since it wasn't asked for in this step's
design and building it unrequested would be scope beyond what was decided.

## Testing

`scripts/test-auto-publish.sh`, run with plain `git`/`bash` on the host (no
npm, no Node — `npm` and `node` are stubbed as shell functions exactly where
the script calls them, the same technique `scripts/test-publish-issue.sh`
uses). Covers:

- the file allowlist, both directions, including the `generated/**` glob at
  depth and every one of the five allowed exact paths
- the `main`-matches-`preview` drift check, proving the stricter (whole-tree,
  not record-keeping-excluded) exclusion behaves as designed
- four end-to-end scenarios against a real local bare-repo remote: an
  allowlist violation (refuses, nothing pushed), success (both `preview` and
  `main` get the data), drift (data lands on `preview` only, `main`
  untouched, `runStatus` reads incomplete with the right reason on
  `preview`), and a gate failure (neither branch reaches either ref,
  `runStatus` reads incomplete with the runner named, and — since `main`
  matched `preview` in that scenario — the incomplete status itself reaches
  `main`)

All checks pass:

```
$ bash scripts/test-auto-publish.sh
...
All checks passed.
```

## Installing the workflows

Both `docs/archive/2026-10-refresh-gate/auto-001/step4/workflows/edgar-refresh.yml.txt` and
`collect.yml.txt` are complete, ready-to-copy workflow files — this session's
token lacks the `workflow` scope needed to write under `.github/workflows/`
directly (same limit step 2 hit). Once a session with that scope is
available:

1. `cp docs/archive/2026-10-refresh-gate/auto-001/step4/workflows/edgar-refresh.yml.txt .github/workflows/edgar-refresh.yml`
   (drop the draft header above the `--- file content below ---` marker) —
   this REPLACES the step 2 draft at `docs/archive/2026-10-refresh-gate/auto-001/step2/edgar-refresh.yml.txt`,
   which never became a real workflow file either.
2. `collect.yml.txt` waits on step 3's `docs/archive/2026-10-refresh-gate/auto-001/collect-brief.md`
   existing — copy it the same way once that brief lands and the
   `CLAUDE_CODE_OAUTH_TOKEN` secret (below) is set.
3. Commit both under `.github/workflows/`, on `preview`, the normal way — this
   itself is a code change under `AGENTS.md` and needs the owner's word to
   reach `main` like any other, one time, to get the automation live. After
   that, the automation runs itself.

## GitHub repository settings needed

- **Actions secret `CLAUDE_CODE_OAUTH_TOKEN`** — the owner runs
  `claude setup-token` on his own account (subscription login, never an API
  key — AWS model-choice rule) and the coordinator puts what it prints into
  this repository's Actions secrets. Only needed for `collect.yml`, not
  `edgar-refresh.yml`.
- **Actions permissions**: both workflows declare `permissions: contents: write`
  at the job level, which is sufficient today because this is a free private
  repository with no branch protection on `main` — the default
  `GITHUB_TOKEN` can already push any branch. If BACKLOG SEC-051 (GitHub Pro,
  branch protection on `main`) is taken later, that protection must
  explicitly allow this actor to push directly with no required review, or
  both workflows' pushes to `main` start failing the day it lands — flagged
  in both workflow drafts' own headers and in
  `docs/archive/2026-10-refresh-gate/auto-001/step4/workflows/retire-notes.md`.
- **Concurrency**: both drafts share one concurrency group, `auto-publish`,
  with the existing publish-issue.yml's group (`publish-issue`) left as its
  own — so an EDGAR run and a collect run, or two EDGAR runs, never overlap
  each other's pushes to `preview`/`main`, matching the same serialization
  `publish-issue.yml` already uses for the weekly path.

## Scope note

`docs/archive/2026-10-refresh-gate/auto-001/step4/workflows/retire-notes.md` names exactly which
existing workflows and scripts to disable once these land
(`publish-issue.yml`, `scripts/publish-issue.sh`, `gather-pr.yml`,
`scripts/gather.sh`, and the macbook2014 launchd job) and what `freshness.yml`
should additionally check (`runStatus.lastChecked` no older than 2 days on
the live site, and a separate alert for `state: 'incomplete'` on production).
Not carried out here — this session doesn't have the token scope to touch
`.github/workflows/` at all, and the freshness addition depends on how step 5
ends up exposing `runStatus` publicly, which is a different builder's call.
