# T7-2 report: signing on approval, and the thesis leaves the weekly issue

Task T7-2, spec `docs/active/publish-path-spec.md` (SEC-MARKET-PUBLISH-001), builds 3 and 1. Branch
`mon/publish`, worktree `/Users/jessepike/code/projects/sec-market-wt-publish`. Commits:

- `b93cf05` — `feat(web): thesis verdict leaves the weekly issue (SEC-MARKET-PUBLISH-001 build 3)`
- `692b704` — `feat(publish): sign a weekly issue from the owner's PR approval (SEC-MARKET-PUBLISH-001 build 1)`
- `79b7388` — `fix(publish): step 1 needs no HEAD_BRANCH fetch; two e2e tests assumed the latest issue`
- `2c82876` — first report
- `0bcc0a6` — merge of `origin/preview` (the scorecard-upkeep build)
- `b24fb2b` — `fix(publish): sign exactly what was approved, allowlist the branch, fix the promote-guard subshell bug` — the coordinator's five fixes, covered below
- `b6a8a8f` — `fix(publish): split guard/build/release phases, close the twelve adversarial findings` — the coordinator's twelve-point adversarial review, covered below

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

## The coordinator's twelve-point adversarial review (commit `b6a8a8f`)

An adversarial review found twelve findings, A through L, all accepted, several in a modified form.
The fix that mattered most: **publish-issue.sh now runs as three phases** —
`--phase guard|build|release` — because the issue branch this checks out is not trusted, and nothing
it could influence should ever run holding write credentials. Everything else below either serves
that split or is a smaller, independent fix.

**A — the phase split itself.** `guard` is pure git plumbing (the approved-sha check, the D and E
guards below, the file allowlist) and holds no token; it runs from the trusted checkout, before
`setup-node`, `npm ci`, or Playwright install ever touch what the branch shipped. `build` (merge,
sign, lock, `npm test`, one local commit) also holds no token — this is where the branch's own
TypeScript actually executes, in the sign step and in the test suite's own imports. Only `release`
holds `GH_TOKEN`, and it does three things the earlier version didn't: it authenticates each push
with an explicit per-invocation header (`git -c http.extraheader=...`, built fresh each call, never
written to `.git/config` or echoed) rather than a stored credential — the issue-branch checkout uses
`persist-credentials: false`, so nothing else has push rights at all; it runs with
`core.hooksPath=/dev/null`; and before it pushes anything, it re-verifies the trusted checkout
(`trusted/`) is still exactly what the workflow checked out — same commit, no local changes — using a
SHA the workflow captured right after that checkout step. A guard or build refusal can't call `gh`
(no token), so it writes a plain-text reason to `$STATE_DIR/phase-result.txt`; a later workflow step,
which does hold a token, reads that file and posts it — truncated, inside a code block, since it's
untrusted regardless of which phase wrote it. Cross-phase state (whether preview matched main, how
many posture notes were dropped) crosses the same way: small, narrowly-typed plain-text files in
`$STATE_DIR`, read with a strict `true`/`false` or digits-only check, never sourced or evaluated.

**B — `.gather/pr-body.md` added to the allowlist.** `gather.sh` line ~120 already told the job to
commit this file on every branch; `gather-brief.md`'s own list just hadn't caught up. Both now agree
on five files, not four.

**C — `computeSignedIssue` takes `read` from `proposed.read` explicitly**, rather than leaving
`issue.read` untouched on the assumption the gather always writes the same text to both fields.
`web/tests/sign-issue.test.ts` has a dedicated test with a draft whose top-level `read` deliberately
differs from `proposed.read`, proving the signed issue takes the latter.

**D — the comment-race guard.** A "publish" comment has no commit id of its own; the gate step reads
the PR's `headRefOid` fresh, but a new commit could land in the gap between the comment being posted
and that read resolving. Guard now refuses if the branch's own committer time is later than the
comment's timestamp. Both are compared as **Unix-epoch seconds**, never as ISO-8601 text — the gate
step computes the epoch itself (it always runs on `ubuntu-latest`, where GNU `date -d` works), so
`publish-issue.sh` — which is also tested on this Mac host, whose BSD `date` does not understand
`-d` — never has to parse a timestamp at all. Not applied to the review-triggered path: a review's
`commit_id` is already atomic with the approval, no race window to close.

**E — the production-parity guard now covers the whole tree.** It used to diff `origin/main` against
`origin/preview` on `-- web` only; a difference in `scripts/`, `.github/`, hooks, rules, or
`AGENTS.md` would have gone unnoticed. It now diffs everything except pure record-keeping paths
(`docs/`, `status.md`, `decisions.md`, `BACKLOG.md`, `lessons.md`, `README.md`), kept in one
commented array (`PRODUCTION_GUARD_EXCLUDE`). `scripts/test-publish-issue.sh` proves the old guard's
gap directly: an identical-except-`scripts/foo.sh` pair of branches reads as *not* matching under the
new guard.

**F — `gather.sh` checks its own push.** After confirming the branch reached the remote (the real
push happens inside the delegated `claude -p` subprocess, so this can't run strictly *before* it),
`gather.sh` now diffs the pushed branch against `origin/preview` and records a new `blocked-paths`
receipt state, in the same style as the existing `blocked-auth` state, if anything outside the same
five-path allowlist was touched. A minimal, independent duplicate of the check in
`publish-issue.sh` — that file belongs to another session, so the two are not sharing code, just the
same five paths.

**G — a real publish attempt that fails now gets a reason.** The gate step used to resolve the pull
request's head/base branches only *after* confirming the comment said "publish" — so a wrong-wording
comment, or an unapproved review, on a genuine `issue/*`-into-`preview` pull request from the owner
went completely silent. It now resolves head/base first for any owner-authored comment, checks
wording after, and posts the reason whenever the actor is the owner and the resolved pull request is
`issue/*`→`preview` but something else failed. Every other actor and every other pull request stays
silent, exactly as before.

**H — push order: preview, then the issue branch, then main.** A rejected preview push (someone else
moved it first) now means nothing else has happened yet, so "approve again" is a complete, honest
instruction. `scripts/test-publish-issue.sh` proves the order against a real, local, file-based git
remote (not a network call — a bare repo on disk): the commit lands on preview, then the issue
branch, then main, in that order, and each push actually reaches that remote's refs.

**I — the comment trigger is now an exact match.** "publish" or "publish reconfirm" (trimmed,
lower-cased) — not just "the first word is publish", which used to let "publish now please" through.
A `RECONFIRM` flag is computed in the gate step from untrusted event text (never interpolated into a
`run:` body directly, per this file's own rule — only through `env:`), passed to guard/build as an
env var, and logged. Nothing else consumes it yet, per the instruction; a later task wires it up.

**J — "production did not move" is now a failed run.** It used to return 0 with just a comment,
which is exactly the kind of thing that's easy to miss on a phone. `step8_promote` now returns 1 in
that case, and `scripts/test-publish-issue.sh`'s local-remote integration test proves both halves at
once: preview and the issue branch still take the push, main does not move, and the run reports
failure.

**K — `quoteString` also escapes `\r`, U+2028, and U+2029** (LINE SEPARATOR / PARAGRAPH SEPARATOR —
legal inside a JS string literal, historically mishandled by naive line-splitting and JSON tooling).
A backtick, `${...}`, and `</script>` need no escaping here (never a template literal, never inlined
into HTML) but are tested anyway, round-tripped through a real dynamic `import()` of a generated
module, to prove they pass through unmangled rather than assuming it. One real bug found and fixed
while building this: the first draft of the fix put the literal U+2028/U+2029 *characters* inside the
regex slashes instead of the ` `/` ` escape sequences — a line separator character inside a
regex literal's source text is itself a line terminator in JS grammar, so esbuild read it as an
unterminated regex. Fixed to use the escape-sequence text, not the raw character.

**L — an already-published issue is not a failure.** `findDraftToSign` throws a distinct
`AlreadyPublishedError` when `--id` names an issue that exists but isn't a draft; `sign-issue.ts`
exits with code 2 specifically for that class (every other failure still exits 1). The build phase
checks for exit code 2 after step 2, and when it sees it, prints "already published — nothing to
sign", sets a `already-published` step output, and returns success — the workflow's release phase is
skipped entirely (via that output), and a dedicated step posts a plain "already published, nothing to
do" comment instead of the release phase ever running.

**Test results.** `web/tests/sign-issue.test.ts`: 25/25 (covers C, K, L's TypeScript side).
`scripts/test-publish-issue.sh`: 33/33 — the original allowlist/approved-sha/not-promoted-skips-live-
check assertions, plus new coverage for D (`branch_changed_after_comment`, both directions and the
equal-epoch edge), E (the five-branch production-guard pathspec scenario above), and a combined H/J
integration test that runs `step6_push_preview`/`step7_push_issue_branch`/`step8_promote` for real
against a local file-based git remote, twice — once where preview already matches main (all three
pushes land, main included) and once where it doesn't (preview and the issue branch still take the
push, main does not move, and the run fails). Full `npm test` in the OrbStack VM: 154/154 data tests,
37/37 e2e (1 pre-existing unrelated skip), lint clean, full build including `verify:prints`.

**Acceptance dry run, rerun against the phase-split script.** Built fresh: a frozen reference remote
with `main` and `preview` both pinned to `mon/publish`'s tip (`b6a8a8f`) and a scratch clone checked
out at the real, untouched `origin/issue/2026-w37` (`7647baa`), with the trusted `publish-issue.sh`
copied in from the frozen `preview` — byte-identical to the worktree's own copy, confirmed by diff.
Run as **three separate process invocations**, `--phase guard` then `--phase build` then
`--phase release`, sharing one `$STATE_DIR` — exactly how the three workflow steps share state in CI,
not the single-process `--phase all` convenience path. All three exited 0:

```
=================== GUARD PHASE ===================
publish-issue.sh: phase = guard
RECONFIRM=false (logged only — coordinator review point I, 2026-09-21; not yet used for anything)
approved-sha guard: HEAD matches the approved commit (7647baa7...)

=== PRE-FLIGHT: production-guard snapshot ===
preview matches main (excluding record-keeping paths): true
file allowlist guard: only allowed paths changed on issue/2026-w37
publish-issue.sh: guard phase passed.
guard exit=0

=================== BUILD PHASE ===================
[... step 1 merge, step 2 sign, step 3 lock (9 posture-deltas-agree, PASS), step 4 npm test
     (154 data tests, 37/38 e2e with 1 pre-existing skip, verify:dist, verify:prints) ...]
=== STEP: 5 commit ===
[issue/2026-w37 2b94e12] feat(issue): publish 2026-w37, signed by approval of #?
build exit=0

=================== RELEASE PHASE ===================
publish-issue.sh: phase = release
no TRUSTED_SHA_EXPECTED given, skipping the trusted-checkout integrity check (local/manual run)

=== STEP: 6 push preview ===
DRY_RUN=1: not pushing to preview
=== STEP: 7 push issue branch ===
DRY_RUN=1: not pushing to issue/2026-w37
=== STEP: 8 promote to main ===
DRY_RUN=1: not promoting to main
=== STEP: 9 live check ===
DRY_RUN=1: not polling the live site

publish-issue.sh: done.
release exit=0
```

`$STATE_DIR` correctly carried `preview-matches-main=true` and `posture-dropped=1` from the guard and
build processes into the release process — proving the cross-process state-file mechanism (point A)
actually works, not just the same-process `--phase all` path. `2026-w36`'s lock hash,
`be70d2ae9a7af0ac77e75df2cd9e9cd9ae03363168477517f69ba659c8d5fdbd`, is confirmed byte-identical to
before. The allowlist result for `origin/issue/2026-w37` is unchanged: exactly the same three files
as the first report (`web/src/data/evidence.ts`, `web/src/data/issues/2026-w37.ts`,
`web/src/data/issues/index.ts`), all allowed, still including `.gather/pr-body.md` in the allowlist
even though this real branch doesn't use it.

**YAML validation.** `npx --yes js-yaml .github/workflows/publish-issue.yml` parses without error. I
re-audited every `${{ }}` expression by eye, including the one I initially got wrong and then fixed:
the "Post the result of a failed guard or build phase" step first referenced `${{ steps.build.outcome
}}` directly inside its `run:` body, which violates this file's own stated rule that event/step text
only ever reaches a script through `env:`; moved to a `BUILD_OUTCOME` env var instead. Confirmed no
other `run:` body anywhere in the file contains a bare `${{ }}` expression (checked programmatically,
not just by eye, this time). `actionlint` remains unavailable in the OrbStack VM.

**What I could not do exactly as specified, and why.** Point F's `gather.sh` check runs *after* the
push, not before it, because the actual push happens inside a delegated `claude -p` subprocess that
does its own commit-and-push — this script can observe the result but can't interpose before it. The
coordinator's own instruction acknowledged this ("this can only run AFTER the push above"), so this
isn't a deviation, just recorded plainly. Point I's `RECONFIRM` is computed and threaded through as
asked, but nothing consumes it — that's the instruction, not a gap. I did not add an `actionlint`
check; it remains unavailable in the OrbStack VM, same as every prior round.

### Residual risks

Three things this build does not close, stated plainly rather than left to be rediscovered:

1. For the `pull_request_review` trigger, GitHub reads this workflow's own YAML from the pull
   request's merge commit, not from the default branch. A branch that rewrote
   `.github/workflows/publish-issue.yml` could still change what runs — including before the guard
   phase or the trusted checkout ever get a say — on that trigger. The `issue_comment` ("publish")
   trigger doesn't have this gap; `issue_comment` always runs the default branch's copy of the
   workflow. The trusted second checkout closes "the branch alters the publisher script itself"; it
   does not and cannot close "the branch alters the workflow that invokes it."
2. The data files on the issue branch (`web/src/data/issues/<id>.ts`, `evidence.ts`, `prints.ts`) are
   executable TypeScript, not inert JSON — anything that imports them actually runs whatever a
   compromised branch put there. The sign step and the full test suite both import them, and both run
   in the build phase, which holds no token, specifically because of this. That mitigation is real
   but partial: a compromised branch running inside build could still, for example, try to exfiltrate
   whatever it can reach on the runner (source, environment) over the network, even without a GitHub
   token. Nothing in this build sandboxes that further.
3. The weekly gather job (`scripts/gather.sh`, run by `launchd` on macbook2014) pushes with a
   read-write deploy key that is not scoped to `issue/*` — it can push to any branch, including
   `main`, if the host or the key were ever compromised. This is a free private GitHub repository,
   which has no branch protection rules available to enforce that scoping server-side. Point F's new
   `blocked-paths` check in `gather.sh` catches an accidental over-broad commit; it does nothing
   against a compromised host that pushes deliberately. Scoping the key, or moving to a paid plan with
   branch protection, is outside this build's scope.

## Visible changes

Nothing changed on the currently rendered site — same as the first report. `2026-w36` is still the
only published issue; its data, hash, and rendering are untouched.

## What I noticed but did not build

`docs/active/gather-job-spec.md` still describes the gather job proposing a thesis verdict (lines 45,
92, 94), now stale against `gather-brief.md`; not touched, not in scope, unchanged since the first
report. Spec §4.3 (converting an accepted posture note into a structured `PostureDelta`) is still a
separate, later step, not built here. Point I's `RECONFIRM` flag is computed, threaded through, and
logged, exactly as asked, with nothing built on top of it — a later task is explicitly meant to wire
it up, per the coordinator's own instruction. The three residual risks above (the
`pull_request_review` workflow-YAML gap, executable data files on the branch, and the gather job's
unscoped deploy key) are none of them built against in this round; they're recorded so a future
session doesn't have to rediscover them, not because I judged them out of scope on my own — the
coordinator asked for exactly this list.

Deferred to backlog: the stale `gather-job-spec.md` thesis references, unchanged from the first
report. Everything else this round was the coordinator's own twelve-point fix list, already built,
not deferred.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01AdcpLzcT3PoSBWQ7nuRLAT
