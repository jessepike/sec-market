---
id: SEC-MARKET-PUBLISH-001
version: 0.1
status: accepted for build (owner approval D-73, 2026-09-21)
owner: Jesse Pike
author: run SEC-MARKET-FABLE-001 coordinator
---

# Publishing and upkeep without a terminal session

## 1. What this is for

The owner's bar is a site that stays accurate and fresh while he spends a minute or two a week on
it, from his phone. Before this spec, three things needed an agent session at a terminal: signing a
weekly issue, promoting it to the live site, and any update at all to the standing picture (the
supplier scorecard, the domain stances, Platform pressure, the hypotheses). Nothing did the third.

D-73 approved three builds. This document is their spec.

The principle does not change: **a machine drafts, a named person signs.** What changes is what a
signature is. It becomes his approval of the weekly pull request, given from the GitHub phone app.

## 2. Build 1: his approval is the signature

### 2.1 What he does

The weekly job opens a pull request titled `Issue <id> draft` against `preview` (D-70). GitHub sends
the notification to his phone. He reads the pull request body and either:

- approves the pull request, or
- comments `publish` on it.

Both mean the same thing: "I sign this issue as proposed, today." If he wants different words, the
text in `proposed` on the branch is changed first (by him in the GitHub editor, or by an agent he
asks), and he approves after. What gets signed is exactly what `proposed` holds at the commit he
approved. "Request changes", a plain comment, or silence do nothing.

### 2.2 What the machine then does

One workflow, `.github/workflows/publish-issue.yml`, kept thin. The logic lives in
`scripts/publish-issue.sh` and `web/scripts/sign-issue.ts` so it can be run and tested outside
GitHub.

Conditions, all required, otherwise the workflow exits without doing anything:

- the actor is the repository owner (`github.repository_owner`), not a bot and not a collaborator;
- the pull request's head branch is `issue/<id>` in this repository and its base is `preview`;
- the event is an approving review, or a comment whose first word is `publish`.

Steps, in order. A failure at any step stops everything after it and posts a plain comment on the
pull request saying which step failed and the last lines of its output.

1. Check out the head branch with full history. Merge `origin/preview` into it so the result can
   fast-forward `preview`. A merge conflict is a failure.
2. Sign: `sign-issue.ts` takes the one draft issue and writes it back as published.
   - `weThink.summary`, `weThink.postureDeltas`, `weThink.noCalls` and `read` come from `proposed`.
   - `weThink.thesis` is `null` (build 3).
   - `weThink.signedBy` is `AUTHOR_NAME` from `web/src/data/meta.ts`. `weThink.signedOn` and
     `published` are the date of the approval in the owner's timezone (America/Los_Angeles), passed
     in by the workflow from the event timestamp. Never the build date.
   - `status` becomes `published`, `proposed` becomes `null`.
   - The script refuses to run if there is not exactly one draft, if `proposed` is null or empty, or
     if the issue is already signed.
3. Append the issue to the lock manifest with `npm run verify:issue -- --write`.
4. Run everything: `npm test` in `web/` (lint, data tests, all five gates inside the build, and the
   end-to-end suite). The same bar a session holds itself to.
5. Commit as `Jesse Pike <jesse@keatingpike.com>` (Vercel refuses any other author), message
   `feat(issue): publish <id>, signed by approval of #<n>`. Push to the issue branch.
6. Fast-forward `preview` to that commit.
7. Promote to `main`, but only if production would receive this issue and nothing else. The test:
   before step 1, `git diff --quiet origin/main origin/preview -- web` must be clean. If `preview`
   carries site changes that were never promoted, the workflow stops after step 6 and comments that
   the issue is signed and on `preview`, and that production did not move because `preview` holds
   unreviewed site work. His approval of an issue is not approval of anything else.
8. Confirm the live site: poll `https://securitymarketpulse.com/issues/index.json` and
   `/issues/<id>/` until the new issue is the newest and the page carries his name and the signing
   date, for up to fifteen minutes. Comment the result. If it never appears, comment that plainly
   and open a GitHub issue titled `Publish of <id> did not reach the live site`, which notifies him.

`main` stays a fast-forward of `preview` throughout.

### 2.3 What this changes in the project's rules

`AGENTS.md`, section "Production deploy", says `main` moves only when the owner says to promote.
That stays true. The builder adds one paragraph: his approval of a weekly issue pull request is that
word, for that issue only, carried out by `publish-issue.yml` under the step 7 condition. Every
other change reaches `main` the way it does today.

Two files are the owner's alone to amend and this run does not touch them. The proposed wording:

- `.claude/rules/constraints.md`, Authorization. The line "Production collectors, database,
  scheduler, website, digest, and autonomous pipeline are not authorized" has been overtaken by
  D-31 (the site), D-70 (the scheduler) and D-73. Proposed replacement: "The public website, the
  weekly scheduled gather, and publication of a weekly issue on the owner's recorded approval are
  authorized. A database, accounts, an email pipeline, payments, and any publication of a judgment
  without the owner's recorded approval are not."
- `intent.md`: wherever it says market calls are human-checked, no change is needed. If it names a
  terminal session or a manual step as the check, replace that with "the owner's recorded approval".

### 2.4 Known limits

- A comment trigger only works once the workflow file is on the default branch. Approval works from
  `preview`. Both go live for certain after the next promotion.
- He cannot approve a pull request opened under his own account. The weekly job's pull requests are
  opened by the GitHub Actions bot, so approval works; the `publish` comment covers the other case.
- This laptop's GitHub token cannot push workflow files. The branch is pushed through the read-write
  deploy key on macbook2014.

## 3. Build 3: the thesis verdict leaves the weekly issue

Decided in D-72 and D-73: the founding thesis is one standing analysis at `/thesis/`, not a weekly
ruling. A weekly verdict that is nearly always "holds" is noise, and it is a judgment he would be
signing each week without reading.

- `docs/active/gather-brief.md` stops asking for `proposed.thesis` and stops listing it in the pull
  request body.
- `MachineProposal.thesis` becomes optional. An older draft that carries one still type-checks; the
  sign step ignores it.
- The checks allow a published issue with `weThink.thesis: null`.
- `WeThink`, `ThesisPointer`, `ThesisRunningScore` and `newestThesisJudgment` must behave with a
  newest issue that has no verdict: the pointer keeps showing the date of the last verdict that was
  actually signed, the running score keeps its record and says as of when, and no "null" or empty
  block renders. Any sentence on `/thesis/` that promises a weekly score is reworded to say the
  record runs to the last scored issue and is revisited when the evidence moves.
- Issue 2026-w36 is locked and is not touched. Its hash must not change.

## 4. Build 2: the weekly job maintains the standing picture

### 4.1 Scorecard figures (SEC-044, SEC-045)

A supplier's reported figure is a tracked fact with a source, not a judgment. The weekly job may
therefore update `web/src/data/prints.ts` in the same pull request as the issue, and his approval
covers it, provided a check proves the figure means what the card says.

- The brief gains a step: for every supplier print in this week's window, update the matching
  scorecard entry (`period`, `value`, `metric`, `note`, `evidenceIds`). `tone` compares the supplier
  with its own previous figure on the same metric and nothing else. The pull request body lists each
  change as old value, new value, source link.
- A new check, part of the build, compares each print with the evidence it cites on four things
  together: the company or segment, the metric, the reporting period (a quarter is never labelled a
  year), and the units. The value must appear in the cited evidence.
- Existing entries that cannot pass are not deleted and not silently exempted. They go in a dated
  list, `web/src/data/printsUnverified.ts`, each with the reason. The list may only shrink: the
  check fails if an id is added that was not there at the previous commit on `preview`. The brief
  forbids the job from editing that list.

### 4.2 Going stale

`web/scripts/stale-report.ts` prints, as Markdown, every judged claim (domain stances, Platform
pressure rows, hypotheses) whose judged date is older than 45 days, and every scorecard entry whose
period ended more than 150 days ago, oldest first, with the claim's one-line text. The weekly job
puts that under "Going stale" in the pull request body. The site's own stamps keep showing the real
dates, so the page never claims more freshness than it has.

### 4.3 Re-confirming a stance (second step, after build 1 is merged)

Re-dating a judgment under his name must be something he said, not a side effect. If his approving
review, or his `publish` comment, contains the word `reconfirm`, the sign step also re-dates the
stances the pull request listed as stale and unchanged by this week's evidence. Without that word,
nothing is re-dated. This needs the judged dates to be stored per claim; today most come from one
constant. That refactor is part of this step and is invisible on the page.

## 5. Out of scope, recorded in BACKLOG.md

- A `promote` comment that moves everything on `preview` to production from the phone.
- Automatic wording of new stances. The machine may flag and re-date on his word; it does not write
  a new judgment.
- Link-liveness and duplicate-item checks in the weekly job (SEC-049).

## 6. Acceptance

- Build 1: run against the existing draft branch `issue/2026-w37` in a scratch clone with pushes
  disabled. The issue comes out signed, locked, and `npm test` passes. Issue 2026-w36's hash is
  unchanged. The workflow file passes `actionlint` or an equivalent syntax check.
- Build 3: all tests pass with a fixture newest issue that has no verdict; `/thesis/` and the front
  page render at 1440 and 390 with no empty block; before and after captures are attached.
- Build 2: the new check fails on a deliberately wrong period label and on a value absent from its
  evidence, and passes on the repository as shipped with the unverified list in place. The stale
  report runs and its output is attached.
