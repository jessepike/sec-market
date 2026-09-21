# T7-2 report: signing on approval, and the thesis leaves the weekly issue

Task T7-2, spec `docs/active/publish-path-spec.md` (SEC-MARKET-PUBLISH-001), builds 3 and 1. Branch
`mon/publish`, worktree `/Users/jessepike/code/projects/sec-market-wt-publish`. Commits:

- `b93cf05` — `feat(web): thesis verdict leaves the weekly issue (SEC-MARKET-PUBLISH-001 build 3)`
- `692b704` — `feat(publish): sign a weekly issue from the owner's PR approval (SEC-MARKET-PUBLISH-001 build 1)`
- `79b7388` — `fix(publish): step 1 needs no HEAD_BRANCH fetch; two e2e tests assumed the latest issue`
- `2c82876` — first report
- `0bcc0a6` — merge of `origin/preview` (the scorecard-upkeep build)
- `b24fb2b` — `fix(publish): sign exactly what was approved, allowlist the branch, fix the promote-guard subshell bug` — the coordinator's five fixes, covered below

No file under `web/src/data/issues/` was edited, and `2026-w36`'s lock hash is unchanged throughout
(checked again after every dry run). Nothing in `evidence.ts` was hand-edited.

## Build 3 — the thesis is no longer a weekly verdict

`MachineProposal.thesis` (`web/src/data/types.ts`) is now optional. `docs/active/gather-brief.md`
no longer tells the gather job to propose a thesis verdict, and says plainly that the founding
thesis lives at `/thesis/` and is not a weekly call. `verify-issue.ts` check 5 now accepts a
published issue whose `weThink.thesis` is `null`, and still requires a complete verdict (basis,
evidence, confidence) when one is present.

Three rendering paths needed a null check so a missing verdict never shows an empty box or the
word "null": `WeThink.tsx`'s draft path (the published path already had one), and
`issueEvidenceIds` in `issueHelpers.ts`, which now skips the thesis entirely when
`proposed.thesis` is absent rather than throwing on `.evidenceIds` of `undefined`.
`newestThesisJudgment` and `thesisRunningScore` needed no change — both already filter on
`weThink.thesis !== null`, so an issue with no verdict was already excluded correctly.

`2026-w36` itself, the one published issue, is untouched — it still carries its original signed
thesis verdict, and its lock hash did not move.

## Build 1 — signing an issue from the owner's approval

`web/scripts/sign-issue.ts` is a thin CLI (`npm run sign:issue -- --signed-on YYYY-MM-DD
[--id 2026-w37]`) over two pure modules — `signIssueLogic.ts` (date validation, `findDraftToSign`,
`computeSignedIssue`) and `signIssueRender.ts` (serializes the published `Issue` back into a
TypeScript module matching the hand-written files) — so the logic is unit-testable without
touching the filesystem.

`scripts/publish-issue.sh` runs spec §2.2's eight steps: merge `origin/preview`, sign the one
draft, append to the lock manifest, run `npm test`, commit and push, fast-forward `preview`,
promote to `main` only if `preview` already matched `main` on `web/` before the run started, then
poll the live site and comment the result. `.github/workflows/publish-issue.yml` triggers on an
approving PR review or a "publish" comment, gated on the actor being the repo owner, head branch
`issue/*`, base `preview`.

**The posture-deltas question**, from the first review: `computeSignedIssue` always signs with
`postureDeltas: []`, since `MachineProposal.postureDeltas` is prose, not the structured record
`weThink.postureDeltas` needs, and converting one into the other is spec §4.3's separate, not-yet-
built step. Confirmed against the real `origin/issue/2026-w37` draft, whose `proposed.postureDeltas`
is genuinely prose ("None proposed, with one flagged for a human look at the CrowdStrike stance").

## The coordinator's five fixes (commit `b24fb2b`)

**1. The `NO_PROMOTE` subshell bug, fixed and regression-tested.** `run_step` puts each step on the
left side of a pipe (`"$@" 2>&1 | tee`), and bash always forks a subshell for the left side of a
pipe. `step7_promote` used to set `NO_PROMOTE="1"` inside that subshell; the write never reached
`step8_live_check`, so a "not promoted" run would still poll the live site for fifteen minutes,
fail, and file a spurious GitHub issue every time. Fixed by having step 8 read `PREVIEW_MATCHES_MAIN`
instead — a variable `main()` sets once, in the parent shell, before any step runs, and no step ever
writes to. I audited every other step for the same pattern; `PREVIEW_MATCHES_MAIN`, `ISSUE_ID`, and
the new `posture_note` are the only cross-step variables, and all three are set in `main()`, never
inside a step. Added `scripts/test-publish-issue.sh`, which sources `publish-issue.sh` (its `main`
only runs when the file is executed directly, guarded by a `BASH_SOURCE` check) and calls
`step8_live_check` directly with `DRY_RUN=0`, `PREVIEW_MATCHES_MAIN=false`, and an unreachable
`LIVE_BASE_URL`. This is a real regression test: with the old bug, this exact scenario would have
fallen through to the live poll and hung for `LIVE_POLL_SECONDS`; it now returns in under a second.
Also added `FORCE_PREVIEW_MATCHES_MAIN` as a documented test-only seam.

**2. `GH_REPO` for the gate step.** `gh pr view` in the gate step ran before any checkout, so `gh`
had no git remote to infer a repository from. Added `GH_REPO: ${{ github.repository }}` to that
step's `env`, and to the Publish step's `env` as well since it also calls `gh`. No other `gh` call
in the workflow runs outside a checkout.

**3. Sign exactly what was approved.** The gate step now also computes `approved_sha`: for a review,
`github.event.review.commit_id` directly; for a "publish" comment (which carries no commit id of its
own), `headRefOid` from the same `gh pr view` call that already resolves head/base refs. Passed to
the script as `APPROVED_SHA`. Before step 1, `publish-issue.sh` now refuses unless
`git rev-parse HEAD` equals `APPROVED_SHA`, commenting that the branch moved and asking for a fresh
approval. Required outside `DRY_RUN`; optional in `DRY_RUN`, matching the instruction.

**4. The file allowlist guard, and the trusted checkout.** Before step 1, the script now computes
`git diff --name-only "$REMOTE/preview...HEAD"` and refuses unless every changed path is one
`docs/active/gather-brief.md` actually authorizes the gather job to write. I read `gather-brief.md`
itself rather than trust the coordinator's example list: it names exactly four paths — the new
issue module (`web/src/data/issues/<id>.ts`), `web/src/data/issues/index.ts`,
`web/src/data/evidence.ts` (append only), and `web/src/data/prints.ts` — and says nothing about
`.gather/`. The suggested `.gather/` pattern is **not** in the allowlist because gather-brief.md
does not authorize it; if that's wrong, it's one line to add back, with the owner's word, per the
comment above the array. The workflow now also does a second `actions/checkout@v4` of `preview`
into `path: trusted` with `sparse-checkout: scripts`, and the Publish step runs
`./trusted/scripts/publish-issue.sh` — a compromised issue branch cannot rewrite the very script
that decides how it gets published. Recorded honestly, in both the script's header comment and the
workflow's own top-of-file comment: for the `pull_request_review` trigger, GitHub reads the workflow
YAML *itself* from the pull request's merge commit, so a branch that rewrote
`.github/workflows/publish-issue.yml` could still change what runs before the trusted script ever
gets a say. The `publish` comment trigger doesn't have this gap. The trusted checkout closes "the
branch alters the publisher script"; it does not close "the branch alters the workflow that invokes
it." Not solved here, per the instruction — recorded so it isn't rediscovered.

**5. Posture-deltas visibility.** `sign-issue.ts` now prints
`sign-issue: posture-deltas-dropped: N` on stdout (new `postureDeltasDroppedCount` in
`signIssueLogic.ts`), grepped by `publish-issue.sh` right after step 2. Since
`MachineProposal.postureDeltas` is one prose string, not a list, there's no reliable way to count
individual notes inside it — the function counts the field itself: 0 for blank or exactly
gather-brief.md's "none proposed" convention (case-insensitive), 1 for anything else, including
"None proposed, with one flagged..." (the real 2026-w37 draft, which does exactly this). That's a
stated limitation, not a silent one: a draft that ever needs more than one tracked stance note would
undercount. When the count is greater than zero, both success comments (the "signed and on preview,
not promoted" comment and the "is live" comment) append a sentence saying a posture note was signed
away unapplied and that stance changes happen separately.

## Merging `origin/preview`

`git fetch origin && git merge --no-edit origin/preview` brought in the scorecard-upkeep build
(`verify:prints`, `stale-report.ts`, new `gather-brief.md` passages, new `package.json` scripts).
One real conflict, in `web/package.json`: both sides added a script line and a `test:data` entry.
Resolved by keeping both new scripts (`sign:issue` and `verify:prints`) and both new test files
(`sign-issue.test.ts` plus `print-checks.test.ts`/`stale-report.test.ts`), and keeping the
`--tsconfig tsconfig.app.json` flag `test:data` needs for the JSX-rendering tests in
`issue-data.test.ts`. `docs/active/gather-brief.md` auto-merged cleanly; my "do not set
`proposed.thesis`" wording and their scorecard-figures instructions both survived intact. Full
`npm test` afterward: lint clean, 151 data tests (148 plus 3 new for `postureDeltasDroppedCount`),
the full build including `verify:prints`, and 37 e2e passed with 1 pre-existing unrelated skip.

## Acceptance dry run, rerun after the fixes

Built fresh, outside both checkouts: a frozen reference remote with `main` and `preview` both
pinned to `mon/publish`'s tip (`b24fb2b`) — simulating "preview after this merges" — and a scratch
clone checked out at the real, untouched `origin/issue/2026-w37` (`7647baa`), with the trusted
`publish-issue.sh` copied in from the frozen `preview`, exactly matching the workflow's own
two-checkout arrangement. `APPROVED_SHA` set to the branch's real tip. Result: exit 0.

```
approved-sha guard: HEAD matches the approved commit (7647baa7...)
=== PRE-FLIGHT: production-guard snapshot ===
preview matches main on web/: true
file allowlist guard: only allowed paths changed on issue/2026-w37

=== STEP: 2 sign ===
sign-issue: signed "2026-w37" as Jesse Pike on 2026-09-21
sign-issue: posture-deltas-dropped: 1

=== STEP: 3 lock manifest ===
PASS  9 posture-deltas-agree
Added 1 new entry: 2026-w37

=== STEP: 4 npm test ===
37 passed (12.1s)
  1 skipped

=== STEP: 5 commit and push ===
[issue/2026-w37 542e376] feat(issue): publish 2026-w37, signed by approval of #101
DRY_RUN=1: not pushing to issue/2026-w37
=== STEP: 6 fast-forward preview ===
DRY_RUN=1: not fast-forwarding preview
=== STEP: 7 promote to main ===
DRY_RUN=1: not promoting to main
=== STEP: 8 live check ===
DRY_RUN=1: not polling the live site

publish-issue.sh: done.
```

**Allowlist result for w37, asked for explicitly**: it passes. `git diff --name-only
origin/preview...origin/issue/2026-w37` on the real repo shows exactly three files —
`web/src/data/evidence.ts`, `web/src/data/issues/2026-w37.ts`, `web/src/data/issues/index.ts` — all
three on the allowlist. I did not widen the list; the branch simply stays inside what
gather-brief.md already authorizes.

The lock manifest gained one entry, `2026-w37`; `2026-w36`'s hash,
`be70d2ae9a7af0ac77e75df2cd9e9cd9ae03363168477517f69ba659c8d5fdbd`, is byte-identical to the one on
`mon/publish` — confirmed by diffing both files directly. `postureDeltasDroppedCount` correctly
read the real draft's prose as 1 (a genuine flagged item, not "none proposed" alone). Nothing from
this run touched `mon/publish`; the commit `542e376` exists only in the now-deleted scratch clone.

`scripts/test-publish-issue.sh` (17 assertions: the allowlist against 4 allowed and 6 disallowed
paths including `.gather/state.json`, the approved-sha check both ways, and the two step-8 skip
cases) — all pass, run with `bash scripts/test-publish-issue.sh`.

## YAML validation

Same two methods as before, rerun against the updated file: `npx --yes js-yaml
.github/workflows/publish-issue.yml` parses without error. I re-audited every `${{ }}` expression
by eye and confirmed the new `GH_REPO`, `REVIEW_COMMIT_SHA`, and `approved_sha` additions all stay
inside `env:` blocks or `GITHUB_OUTPUT` writes — none of them, or any pre-existing expression, sits
inside a `run: |` body. `actionlint` remains unavailable in the OrbStack VM.

## What I could not verify

Everything from the first report still holds: the workflow only truly runs on GitHub, so the actual
trigger gate (actor, head/base branch, review state, comment wording), the `gh pr view` calls, and
the trusted second checkout's exact behavior are unverified beyond YAML parsing, manual review, and
the local dry run's proof that the script side of the contract works. The `pull_request_review`
workflow-YAML gap described under fix 4 is a known, recorded limitation, not something this task
attempted to close.

## Visible changes

Nothing changed on the currently rendered site — same as the first report. `2026-w36` is still the
only published issue; its data, hash, and rendering are untouched.

## What I noticed but did not build

Same as the first report: `docs/active/gather-job-spec.md` still describes the gather job proposing
a thesis verdict (lines 45, 92, 94), now stale against `gather-brief.md`; not touched, not in scope.
Spec §4.3 (converting an accepted posture note into a structured `PostureDelta`) is explicitly a
separate, later step and I did not build it — this round makes the dropped note visible in a PR
comment, which is different from applying it. Build 2 (spec §4) is separate scope, built in
parallel. I did not widen the file allowlist to include `.gather/`, since nothing in
`gather-brief.md` authorizes it; if the gather job is meant to write there, that's the owner's call
to make, not mine to assume.

Deferred to backlog: the stale `gather-job-spec.md` thesis references, unchanged from the first
report. Everything else this round was the coordinator's own fix list, already built, not deferred.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01AdcpLzcT3PoSBWQ7nuRLAT
