# T7-2 report: signing on approval, and the thesis leaves the weekly issue

Task T7-2, spec `docs/active/publish-path-spec.md` (SEC-MARKET-PUBLISH-001), builds 3 and 1. Branch
`mon/publish`, worktree `/Users/jessepike/code/projects/sec-market-wt-publish`. Three commits:

- `b93cf05` — `feat(web): thesis verdict leaves the weekly issue (SEC-MARKET-PUBLISH-001 build 3)`
- `692b704` — `feat(publish): sign a weekly issue from the owner's PR approval (SEC-MARKET-PUBLISH-001 build 1)`
- `79b7388` — `fix(publish): step 1 needs no HEAD_BRANCH fetch; two e2e tests assumed the latest issue`

No file under `web/src/data/issues/` was edited, and `2026-w36`'s lock hash is unchanged (see
below). Nothing in `evidence.ts` was touched.

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

Tests added to `web/tests/issue-data.test.ts`: `newestThesisJudgment` returns `null` when no issue
has signed a verdict, and keeps the date of the last signed verdict when a newer issue has none.
`WeThink` is rendered to static markup (both the published and draft paths) for a newest issue
with no thesis, and the test asserts the output contains neither the string `null` nor the
`we-think__thesis` class. `issueEvidenceIds` with no proposed thesis returns an empty array
without throwing.

`2026-w36` itself, the one published issue, is untouched — it still carries its original signed
thesis verdict, and its lock hash did not move.

## Build 1 — signing an issue from the owner's approval

**`web/scripts/sign-issue.ts`** is a thin CLI (`npm run sign:issue -- --signed-on YYYY-MM-DD
[--id 2026-w37]`) over two pure modules so the logic is unit-testable without touching the
filesystem:

- `signIssueLogic.ts` — date validation, `findDraftToSign` (refuses on no draft, more than one
  draft, an empty or null proposed block, or an issue that is already published), and
  `computeSignedIssue`, which turns a draft into a published `Issue`.
- `signIssueRender.ts` — serializes the resulting `Issue` back into a TypeScript module in the
  same shape and style as the hand-written files under `web/src/data/issues/`.

**The posture-deltas question.** The spec said the signed issue's `weThink.postureDeltas` comes
from `proposed`, but `MachineProposal.postureDeltas` is a prose string ("None proposed, with one
flagged for a human look...") while `Issue.weThink.postureDeltas` is a structured, evidence-cited
array. There is no safe mechanical way to turn prose into a cited record, and the spec's own §4.3
describes that conversion as a second, not-yet-built step that happens after this one is merged.
So `computeSignedIssue` always signs with `postureDeltas: []`, never attempts to parse the prose,
and check 9 (`posture-deltas-agree`) passes on an empty array by construction. This is documented
in a comment on `computeSignedIssue` and confirmed against the real `origin/issue/2026-w37` draft,
whose `proposed.postureDeltas` is genuinely prose, not data.

**`scripts/publish-issue.sh`** runs spec §2.2's eight steps in order: merge `origin/preview`, sign
the one draft, append to the lock manifest, run `npm test`, commit and push, fast-forward
`preview`, promote to `main` only if `preview` already matched `main` on `web/` before the run
started, then poll the live site for up to fifteen minutes and comment the result (or open a
GitHub issue on timeout). `DRY_RUN=1` runs everything through the commit and skips every push and
the live poll. A failed step prints its name and the last 40 lines of its output and exits
non-zero; outside `DRY_RUN`, it also comments that on the pull request.

**`.github/workflows/publish-issue.yml`** triggers on an approving PR review or a comment whose
first word is "publish," gated on the actor being the repo owner, the head branch matching
`issue/*`, and the base branch being `preview`. The signing date is computed from the event
timestamp in America/Los_Angeles, never from when the job happens to run. Every value that comes
from the triggering event (`github.event.*`) is passed through `env:` and read as a shell
variable; none of it is interpolated directly into a `run:` block. I checked this by eye and
confirmed it with `awk` across the whole file: no `github.event.` string appears inside any
`run: |` body.

`AGENTS.md` gets one new paragraph in the Production deploy section naming this as the one
approval that can itself promote to `main`, and only for that issue. `scripts/README.md` gets a
short "Publishing from the phone" note.

## Acceptance test, outside both checkouts

Spec §6 asks for this to run in a scratch clone, merging `origin/issue/2026-w37`. `origin/preview`
had genuinely moved during the session (another builder's work landed), so a real merge against
it correctly produced a real conflict — proving the script's step 1 detects divergence rather than
papering over it, but not useful for testing the rest of the pipeline in isolation. I built a
frozen reference remote pinned to the commit `mon/publish` actually forked from, and ran the same
scratch-clone test against that, so every other step got exercised end to end.

Result, `DRY_RUN=1 SIGNED_ON=2026-09-21 ... scripts/publish-issue.sh`, exit 0. Excerpt:

```
=== PRE-FLIGHT: production-guard snapshot ===
preview matches main on web/: true

=== STEP: 2 sign ===
sign-issue: signed "2026-w37" as Jesse Pike on 2026-09-21

=== STEP: 3 lock manifest ===
PASS  9 posture-deltas-agree
...
Added 1 new entry: 2026-w37

=== STEP: 4 npm test ===
...
37 passed (13.3s)

=== STEP: 5 commit and push ===
[mon/publish c8c72a2] feat(issue): publish 2026-w37, signed by approval of #99
DRY_RUN=1: not pushing to issue/2026-w37

=== STEP: 6 fast-forward preview ===
DRY_RUN=1: not fast-forwarding preview

=== STEP: 7 promote to main ===
DRY_RUN=1: not promoting to main

=== STEP: 8 live check ===
DRY_RUN=1: not polling the live site
```

The signed issue came out published, signed by "Jesse Pike," locked. The lock manifest gained one
entry, `2026-w37`; `2026-w36`'s hash,
`be70d2ae9a7af0ac77e75df2cd9e9cd9ae03363168477517f69ba659c8d5fdbd`, is identical before and after
— I diffed it directly against the manifest on `mon/publish` to confirm. `npm test` passed in
full: lint clean, `test:data` (104 tests), the build with all verify gates, and 37 e2e passed with
1 pre-existing, unrelated skip. Nothing from this dry run touched my actual branch — the commit
`c8c72a2` exists only in the scratch clone, which has been deleted, along with the frozen
reference remote.

`npm test` also passed on `mon/publish` itself, after the two e2e fixes below.

## The two e2e fixes (not originally scoped, but required)

Running the acceptance test surfaced five failures, all in `corrections.spec.ts` and
`thesis.spec.ts`. Both files had hardcoded the assumption that `2026-w36` is always the newest
issue — true before this task, false the moment `2026-w37` gets signed. `corrections.spec.ts`'s
two tests now navigate to `/issues/${correction.issueId}/` (the issue the correction actually
belongs to) instead of `/` or `latestIssue.id`. `thesis.spec.ts`'s front-page test now computes
whether the newest issue actually carries a thesis verdict and asserts the pointer either shows it
or shows neither the pointer nor the word "null," instead of assuming a verdict is always present.
These are pre-existing test bugs the spec's own scope exposed, not new coverage for new behavior;
I fixed them because build 3 makes the previously-safe assumption false, and left everything else
in both files as it was.

## What I could not verify

The workflow YAML cannot run locally — GitHub Actions only executes on GitHub. `actionlint` is not
available in the OrbStack VM and host-protection rules disallow installing new system packages
there, so I validated it two ways instead: `npx --yes js-yaml` parsed the file into JSON without
error, confirming it is structurally valid YAML with every `if:` condition present, and I reviewed
every `${{ }}` expression by eye plus the `awk` scan described above. The actual trigger conditions
(actor is the repo owner, head branch matches `issue/*`, base is `preview`) and the `gh pr view`
call that resolves head/base refs for the `issue_comment` trigger are unverified beyond that
review — they cannot be exercised without a real PR and a real GitHub Actions run.

## Visible changes

Nothing changed on the currently rendered site. `2026-w36` is the only published issue and its
data, hash, and rendering are untouched; no draft in the real preview data lacks a thesis yet, so
there was nothing new to screenshot. No before/after images were captured for this task.

## What I noticed but did not build

`docs/active/gather-job-spec.md` still describes the gather job proposing a thesis verdict at
lines 45, 92, and 94, which is now inconsistent with the updated `gather-brief.md`. That file was
not named in this task's scope, so I left it as found rather than editing it; it should be updated
the next time someone touches the gather job spec. Spec §4.3 (converting an accepted posture-delta
sentence into a structured record) and any change to `.claude/rules/constraints.md` or
`intent.md` are both explicitly out of this task's scope per the spec itself, and I did not touch
either. Build 2 (spec §4) is separate scope, being built in parallel by another session.

Deferred to backlog: the stale thesis references in `docs/active/gather-job-spec.md` noted above
are the one concrete item; I did not edit that file since it was not named in my task, and I am
flagging it here rather than fixing it silently. Everything else noticed during this task (the
§4.3 posture-delta conversion, the constraints/intent files) was already explicitly out of scope
in the governing spec, not a new idea I'm introducing.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01AdcpLzcT3PoSBWQ7nuRLAT
