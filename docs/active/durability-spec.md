# Durability specification — a fresh site every week without a resident

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-DURABLE-001` |
| **Version** | v0.1 — draft for owner review |
| **Status** | proposed |
| **Date** | 2026-09-07 |
| **Governs** | SEC-039 |
| **Parent** | [weekly-issue-plan.md](weekly-issue-plan.md); [gather-job-spec.md](gather-job-spec.md) v0.2; [weekly-issue-spec.md](weekly-issue-spec.md) v0.2 |
| **Intent** | `SEC-MARKET-001` v1.2: a machine may retrieve, extract, compare and propose; only a named person signs or publishes |

## 1. What durable means here

The site is fresh when its newest published issue is the week that just ended, and relevant when
every item in it is sourced, dated inside the window, and read by the signer before it goes out.
Durable means that state is reached every week with about fifteen minutes of the owner's time, and
that when it is not reached, somebody is told before a reader notices. Autonomy runs from the
source fetch to a reviewed pull request and a one-command signature; it stops at the signature.

The 2026-09-05 dry run showed where the pipeline is thin: the cloud runtime cannot reach the
public web; a missing run would go unnoticed; the signing pass is a hand edit of a TypeScript file;
nothing checks production after a promotion. Each section below closes one of those.

## 2. Cadence: Sunday afternoon

| Step | When (Pacific) | When (UTC) | Who |
|---|---|---|---|
| Gather runs, drafts the ISO week ending today | Sunday 13:00 | `0 20 * * 0` | routine |
| Receipt check: a PR titled `Issue <id> draft` exists | Sunday 15:00 | `0 22 * * 0` | probe |
| Signing pass | Sunday evening | | owner |
| Merge to `preview`, promote to `main` | Sunday night | | owner |
| Readers | Sunday night, Monday morning | | |

Brief change: §1 step 3 of `gather-brief.md` becomes "the ISO week that ends today (Sunday)";
`weekEnding` is today, `windowStart` six days earlier. Friday's SEC filings and Sunday's
newsletters are inside the window; a Sunday-evening print is not, and is picked up next week.
Winter drift moves the run to 12:00 Pacific; accepted.

## 3. Runtime: allowlist first, local runner as the fallback

The brief is runtime-agnostic. Two runtimes are specified; one is chosen by a probe, not by hope.

**Primary, cloud routine.** The environment's egress allowlist gains the fixed source hosts:
`www.returnonsecurity.com`, `cybersecurityventures.com`, `www.securityweek.com`, `www.sec.gov`,
`efts.sec.gov`, `techcrunch.com`, the eight specialist VC hosts named in
`startup-source-catalog.md`, and the investor-relations hosts of every issuer in `prints.ts` and
`panelRaw.ts`. Acquirer newsrooms discovered at run time are not on the list; the brief already
records an unreachable host as unreadable and moves on. A one-off **probe routine** curls every
allowlisted host and reports status codes; the schedule is armed only after the probe reads clean.

**Fallback, local runner.** `scripts/gather.sh` in the repo: checks out `preview`, runs
`claude -p --model claude-sonnet-5` with the brief as its prompt and the repo as its working
directory, and pushes the branch. It runs from the laptop by hand, or as a launchd job on macmini
registered through jobs-agent. Same brief, same three files, same PR.

Decision rule: if the probe cannot be made to pass within one week of the allowlist change, the
fallback becomes primary and the cloud routine is deleted.

## 4. Receipts and alerts

Every run leaves two receipts: the PR (opened even with zero readable sources, its body starting
with the gate exit codes) and the run log. Two probes watch them.

- **Sunday 22:00 UTC, run receipt.** If no open PR titled `Issue <id> draft` exists for this
  week's id, raise an alert: a push notification from a one-line routine, and a line in
  jobs-agent's sweep. The alert names the id and the run log URL if a run exists.
- **Daily 14:00 UTC, site probe.** `curl` production `/`, `/feed.xml`, `/issues/index.json`,
  `/issues/lock.json`; all must return 200. Read the newest entry of `index.json`; if its
  `weekEnding` is more than nine days old, or its status is `draft` on a Tuesday or later, report
  "stale" with the date. Report into jobs-agent's registry; jobs-agent owns the probe's health.

Both probes are bash and curl only, registered with jobs-agent, no runtime installs.

## 5. The signing pass, fifteen minutes

Today the signer edits a TypeScript file by hand. Replace with `npm run sign -- <id>`:

1. Prints the draft's read, the four lanes as a checklist, and the machine proposal.
2. Reads `docs/active/issues/<id>-sign.md`, a short file the signer writes in the PR branch:
   the summary, accepted posture deltas, thesis verdict and confidence, no-calls, item ids to
   drop, and any headline edits. The template is generated from the proposal so accepting is a
   matter of deleting what is not accepted.
3. Writes `weThink` from that file, sets `proposed: null`, `signedBy` from `AUTHOR_NAME`,
   `signedOn` and `published` to today, `status: 'published'`; removes dropped items and their
   orphaned evidence; runs `verify:issue -- --write`; commits on the PR branch.

The signer still reads every item. The script removes the typing, not the judgment.

## 6. Source resilience

- Three attempts per source, then unreadable (already in the brief).
- Each source in the manifest gains an alternate: the RSS feed for the HTML page, the EDGAR
  browse endpoint for full-text search, the archive page for the newsletter post.
- If more than half the manifest is unreadable, the PR title carries `(degraded)` and the
  proposed `read` says so. The site still receives a draft; the signer decides whether a degraded
  week publishes with `quiet: true` or waits.
- Never invent, never paraphrase, never bypass a block; unchanged.

## 7. After promotion

`scripts/post-promote.sh`, run by the owner after `PROMOTE=1`: waits for the production deploy
(GitHub deployment status), curls the same four URLs as the daily probe, confirms
`/issues/lock.json` equals the repo manifest, and prints one line. Promotion itself stays a
person's act.

## 8. Drift

- `engines.node` pinned (22.x, present); the routine and the runner use `npm ci`, never
  `npm install`, so the lockfile is authority.
- A monthly reminder line in the site probe: Playwright and Vite versions in `package.json`
  against the dev VM's installed versions; report a mismatch, change nothing.
- The Vercel CLI token expires; the probes use GitHub deployment statuses and public URLs, never
  the Vercel API.

## 9. What autonomy never includes

Signing a judgment, publishing an issue, promoting to `main`, editing `intent.md`, a posture, a
confidence, or any prior issue. A run that cannot reach its sources says so and stops. The
routine's connectors stay empty.

## 10. Measures, reviewed 2026-10-08

| Measure | Target |
|---|---|
| Freshness: days since the newest published `weekEnding`, read Monday | ≤ 1 |
| Run receipt rate: Sundays with a PR by 22:00 UTC | 4 of 4 |
| Owner minutes per week on the signing pass | ≤ 15 |
| Alerts that fired and were true | every one |

## 11. Not in this specification

- A fifth "frontier" lane on AI-frontier security developments: SEC-040, an owner decision on
  scope, and a change to the four-lane data model.
- The pilot list: the site is public; whether email exists at all is the owner's call and an
  intent register change if dropped.
- An always-on project agent: revisit after four issues if the ritual still costs more than the
  target above.

## 12. Owner decisions

1. Sunday cadence as in §2.
2. Allowlist attempt on the cloud environment, or straight to the local runner.
3. Whether the signing file in §5 is the shape you want to edit on a Sunday evening.
4. Authorise the build: brief change, probe routine, two probes via jobs-agent, sign script,
   post-promote script, source alternates.
