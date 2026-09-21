#!/bin/bash
#
# Publishes the one signed-by-approval weekly issue (SEC-MARKET-PUBLISH-001
# §2.2). Called by .github/workflows/publish-issue.yml, kept thin on purpose:
# every ordered step and every refusal lives here so it can be run and tested
# outside GitHub, in a plain clone. See scripts/test-publish-issue.sh for the
# unit-level tests of the guard logic below (sourced, not executed).
#
# Runs as three phases (coordinator review, point A, 2026-09-21), because the
# issue branch this checks out is not trusted: nothing it could influence
# (its own file contents, npm test output, a compromised package) should ever
# run in a process holding write credentials.
#
#   guard    pure git plumbing, no push, NO TOKEN. Refuses before anything
#            else from the branch runs: setup-node, npm ci, Playwright
#            install, npm test, all come after this in the workflow.
#   build    merges preview, signs, locks the manifest, runs npm test, and
#            makes ONE LOCAL COMMIT. Still NO TOKEN — this is where branch-
#            authored TypeScript actually executes (the sign step and the
#            test suite import it), so it must never hold write credentials.
#   release  the only phase with a token. Verifies the trusted checkout is
#            still exactly what was checked out, then pushes (preview, then
#            the issue branch, then main), polls the live site, and posts
#            every comment.
#
# `--phase guard|build|release` selects one; `--phase all` (also the default
# with no flag) runs all three in this one process, for local/manual use —
# the real workflow always calls one phase per invocation. Guard and build
# never call `gh`, so a refusal there is written to
# `$STATE_DIR/phase-result.txt` for a LATER, token-bearing workflow step to
# read and post (`if: failure()`); that file's content is untrusted no matter
# which phase wrote it, so the reading step truncates it and posts it inside
# a code block rather than trusting its shape.
#
# Assumes it is invoked from the repository root, on a checkout that is
# ALREADY on the pull request's head branch (issue/<id>) with full history —
# that is the GitHub Actions checkout step's job, not this script's. In CI
# this script itself is invoked from a second, trusted checkout of `preview`
# (path `trusted/`) so a compromised issue branch cannot alter the very
# script that publishes it; the working directory stays the issue-branch
# checkout the whole time. What this script does, in order, is:
#
#   -  guard: the checked-out commit must equal the approval's own commit
#      (APPROVED_SHA), unless DRY_RUN and no APPROVED_SHA was given
#   -  guard: on the comment-triggered path only, the branch must not have
#      changed after the "publish" comment was written
#   -  guard: preview must not already differ from main outside pure
#      record-keeping paths, or promotion later is skipped (and now fails
#      loudly rather than just noting it)
#   -  guard: the issue branch may only have touched files the gather job is
#      allowed to stage — everything else refuses rather than running an
#      unreviewed diff through a write token
#   1. merge origin/preview into the current branch (a conflict is a failure)
#   2. sign the one draft issue (web/scripts/sign-issue.ts) — exit code 2
#      means the issue is already published, which is not a failure
#   3. append it to the lock manifest (npm run verify:issue -- --write)
#   4. run everything (npm test, in web/)
#   5. commit locally as Jesse Pike <jesse@keatingpike.com> (no push yet)
#   6. push that commit to preview (fast-forward; a rejection here means
#      nothing else has happened yet)
#   7. push that same commit to the issue branch
#   8. push it to main too, but only if preview already matched main before
#      this run started — otherwise this is now a fatal refusal, not a note
#   9. poll the live site for up to fifteen minutes and comment the result
#
# A failure at any step stops everything after it, prints which step failed
# and the last lines of its output, and reports it (guard/build: a result
# file for a later step to post; release: directly, via `gh`, since only
# release holds a token).
#
# Known gap, not solved here: for the pull_request_review trigger, GitHub
# reads the *workflow YAML itself* from the pull request's merge commit, so a
# branch that rewrote .github/workflows/publish-issue.yml could still change
# what runs before this script (and this script's own copy) ever gets a say.
# The `publish` comment trigger doesn't have this gap — issue_comment always
# runs the default branch's copy of the workflow. The trusted second
# checkout closes the "the branch alters the publisher script" gap; it does
# not close "the branch alters the workflow that invokes it."
#
# Required environment:
#   HEAD_BRANCH   the pull request's head branch, e.g. issue/2026-w37
#   SIGNED_ON     YYYY-MM-DD, the approval's date in America/Los_Angeles —
#                 computed by the caller from the event timestamp, never from
#                 when this script happens to run
#
# Optional environment:
#   PR_NUMBER          the pull request number, for the commit message and
#                       any PR comments (default: unset — comments are
#                       skipped, and the commit message says "approval" with
#                       no number)
#   APPROVED_SHA        the commit the owner actually approved — for a review,
#                       github.event.review.commit_id; for a "publish"
#                       comment, the PR's headRefOid read at gate time. The
#                       script refuses to continue if the checked-out branch
#                       tip does not match this, so an approval can never
#                       sign a commit added after the approval. Required
#                       outside DRY_RUN; optional in DRY_RUN (default: unset)
#   COMMENT_CREATED_AT  Unix-epoch seconds (an integer, NOT an ISO-8601
#                       string) for the "publish" comment's own timestamp —
#                       set only on the comment-triggered path. The gate step
#                       computes the epoch itself (it always runs on
#                       ubuntu-latest, where GNU date's `-d` works) so this
#                       script never has to parse a timestamp — it's also
#                       tested on the Mac host, whose BSD date does not
#                       understand `-d`. Guard refuses if the branch's own
#                       committer time is later than this (coordinator
#                       review point D, 2026-09-21): a race between the
#                       comment posting and the gate step reading the PR's
#                       head could otherwise let a later, unapproved commit
#                       through on SHA equality alone. Unset on the review-
#                       triggered path, where commit_id is already atomic
#                       with the approval. (default: unset — the check is
#                       skipped)
#   RECONFIRM           "true" only when the owner's own approval contained
#                       the word `reconfirm` (SEC-MARKET-PUBLISH-001 §4.3,
#                       coordinator task T7-4, wiring up review point I).
#                       Passed to `npm run sign:issue -- --reconfirm` in step
#                       2, which then re-dates every stale, unchallenged
#                       judged claim under the owner's name. "false" (the
#                       default) re-dates nothing. (default: false)
#   REMOTE              git remote name (default: origin)
#   WEB_DIR             the web app's directory (default: web)
#   STATE_DIR           a directory this script's phases share small,
#                       narrowly-typed plain-text state through — never
#                       source'd or eval'd, always read with a strict
#                       true/false or digits-only check before use. Must be
#                       the SAME directory across the guard/build/release
#                       invocations in CI (they are separate processes on the
#                       same runner). (default: a fresh mktemp -d, removed on
#                       exit — fine for `--phase all`, where every phase runs
#                       in this one process anyway)
#   TRUSTED_SHA_EXPECTED  the trusted/ checkout's HEAD, captured by the
#                       workflow right after that checkout step. The release
#                       phase refuses to push anything unless `trusted/` is
#                       still at exactly this commit with no local
#                       modifications (coordinator review point A(4),
#                       2026-09-21). (default: unset — the check is skipped,
#                       for local/test runs with no trusted/ checkout)
#   DRY_RUN              1 disables every push and the live poll (step 9).
#                        Everything else — the merge, the sign, the lock
#                        write, npm test, and the local commit — still runs,
#                        so a dry run proves the issue comes out signed and
#                        locked and that the test suite passes, without
#                        touching any remote ref. (default: 0)
#   FORCE_PREVIEW_MATCHES_MAIN  test seam only: when set (`true`/`false`),
#                        skips the real production-guard snapshot (the git
#                        diff against origin/main and origin/preview) and
#                        uses this value instead. Never set this in a real
#                        publish. (default: unset — computed for real)
#   LIVE_BASE_URL        the live site's origin, for step 9 (default:
#                        https://securitymarketpulse.com)
#   LIVE_POLL_SECONDS    how long step 9 polls before giving up (default: 900)
#   LIVE_POLL_INTERVAL   seconds between polls (default: 15)
#   AUTHOR_NAME          must equal AUTHOR_NAME in web/src/data/meta.ts; used
#                        for the commit author and the step 9 page check
#                        (default: Jesse Pike)
#   AUTHOR_EMAIL         the commit author's email (default:
#                        jesse@keatingpike.com — Vercel refuses any other)
#   GH_TOKEN             required for the release phase outside DRY_RUN.
#                        Never given to the guard or build phase. Used only
#                        to authenticate an explicit, per-push header (never
#                        written to git config, never echoed) and by `gh`.
#
# Exit code: 0 on success, including build detecting the issue is already
# published (point L). Non-zero names the failed step or the guard that
# refused, on stderr — including, now, the step 8 "preview already carried
# unpromoted work, so production did not move" outcome (coordinator review
# point J, 2026-09-21): that used to return 0 with just a comment, which is
# easy to miss; it is now a failed job, the loud version of the same comment.

set -uo pipefail

REMOTE="${REMOTE:-origin}"
WEB_DIR="${WEB_DIR:-web}"
DRY_RUN="${DRY_RUN:-0}"
LIVE_BASE_URL="${LIVE_BASE_URL:-https://securitymarketpulse.com}"
LIVE_POLL_SECONDS="${LIVE_POLL_SECONDS:-900}"
LIVE_POLL_INTERVAL="${LIVE_POLL_INTERVAL:-15}"
AUTHOR_NAME="${AUTHOR_NAME:-Jesse Pike}"
AUTHOR_EMAIL="${AUTHOR_EMAIL:-jesse@keatingpike.com}"
HEAD_BRANCH="${HEAD_BRANCH:-}"
SIGNED_ON="${SIGNED_ON:-}"
PR_NUMBER="${PR_NUMBER:-}"
APPROVED_SHA="${APPROVED_SHA:-}"
COMMENT_CREATED_AT="${COMMENT_CREATED_AT:-}"
RECONFIRM="${RECONFIRM:-false}"
STATE_DIR="${STATE_DIR:-}"
TRUSTED_SHA_EXPECTED="${TRUSTED_SHA_EXPECTED:-}"
GH_TOKEN="${GH_TOKEN:-}"
PHASE="${PHASE:-all}"

GH_AVAILABLE="false"
if command -v gh >/dev/null 2>&1; then GH_AVAILABLE="true"; fi

# Set once main() knows which phase is running: "true" only for a phase that
# actually holds a token (release; also all, for local/manual end-to-end
# runs). guard and build are never able to comment directly, by design —
# notify_failure below is how every guard/build refusal still gets word out.
PHASE_CAN_COMMENT="false"
STATE_DIR_OWNED="0"

STEP_LOG="$(mktemp)"
cleanup() {
  rm -f "$STEP_LOG"
  if [ "$STATE_DIR_OWNED" = "1" ] && [ -n "$STATE_DIR" ]; then
    rm -rf "$STATE_DIR"
  fi
}
trap cleanup EXIT

comment_pr() {
  local body="$1"
  if [ "$DRY_RUN" = "1" ]; then
    printf '[DRY_RUN, not commenting on #%s]\n%s\n' "${PR_NUMBER:-?}" "$body"
    return 0
  fi
  if [ "$GH_AVAILABLE" != "true" ] || [ -z "$PR_NUMBER" ]; then
    printf '[no gh or no PR_NUMBER, not commenting]\n%s\n' "$body"
    return 0
  fi
  gh pr comment "$PR_NUMBER" --body "$body" || echo "publish-issue.sh: warning — gh pr comment failed" >&2
}

# Writes a refusal/failure for a LATER, token-bearing workflow step to post
# (coordinator review point A, 2026-09-21) — guard and build hold no token
# and must never call `gh` themselves. Plain text only, never source'd or
# eval'd by whatever reads it next.
write_result() {
  local body="$1"
  printf '%s\n' "$body" > "$STATE_DIR/phase-result.txt"
}

# The one thing every guard/build/release refusal calls: comments directly
# when this phase actually holds a token, defers to a result file otherwise.
notify_failure() {
  local body="$1"
  if [ "$PHASE_CAN_COMMENT" = "true" ]; then
    comment_pr "$body"
  else
    write_result "$body"
  fi
}

# Runs one named step, capturing its combined output to $STEP_LOG (banner
# printed either way) so a failure can quote the last lines of it. Uses
# PIPESTATUS rather than $? because the command is piped through tee. NOTE:
# the command runs on the left side of a pipe, which bash always forks into a
# subshell — a step function must never set a variable another step reads
# later. (This is exactly the bug fixed in step7/step8 below: use a variable
# set in the parent shell, before run_step, never one set inside a step.)
run_step() {
  local name="$1"
  shift
  printf '\n=== STEP: %s ===\n' "$name"
  : > "$STEP_LOG"
  "$@" 2>&1 | tee "$STEP_LOG"
  local rc="${PIPESTATUS[0]}"
  if [ "$rc" -ne 0 ]; then
    local tail_output
    tail_output="$(tail -n 40 "$STEP_LOG")"
    notify_failure "$(printf 'Publish of %s failed at step: %s\n\n```\n%s\n```' "$ISSUE_ID" "$name" "$tail_output")"
    printf '\npublish-issue.sh: FAILED at step: %s (exit %s)\n' "$name" "$rc" >&2
    exit 1
  fi
}

# --- Pure guard functions (sourced and unit-tested by
# scripts/test-publish-issue.sh; take everything as arguments so they need no
# repo, no network, and no globals to test) --------------------------------

# Whether `current` (the checked-out commit) is the commit the owner actually
# approved. Trivial on its own; the point is giving the check one name and
# one place, so the refusal message and the test live next to the same rule.
approved_sha_matches() {
  local current="$1" approved="$2"
  [ "$current" = "$approved" ]
}

# The files an issue branch may touch, per docs/active/gather-brief.md
# (checked 2026-09-21 against that file's own allowed-files list, which now
# names five paths — coordinator review point B added .gather/pr-body.md,
# which scripts/gather.sh's own prompt already told the job to commit): the
# new issue module, the issues index, the append-only evidence file, the
# scorecard figures file, and the pull request body the Action reads.
# Widening this list further needs the owner's word
# (docs/active/publish-path-spec.md).
is_allowed_issue_branch_path() {
  local path="$1" issue_id="$2" web_dir="$3"
  case "$path" in
    "$web_dir/src/data/issues/$issue_id.ts") return 0 ;;
    "$web_dir/src/data/issues/index.ts") return 0 ;;
    "$web_dir/src/data/evidence.ts") return 0 ;;
    "$web_dir/src/data/prints.ts") return 0 ;;
    ".gather/pr-body.md") return 0 ;;
    *) return 1 ;;
  esac
}

# True when the branch's own committer time is after the "publish" comment's
# timestamp — meaning a commit landed in the race window between the comment
# being posted and the gate step reading the PR's current head (coordinator
# review point D, 2026-09-21). Both arguments are Unix-epoch seconds, never
# ISO-8601 text, specifically so this stays a plain integer comparison — see
# the COMMENT_CREATED_AT doc above for why.
branch_changed_after_comment() {
  local branch_epoch="$1" comment_epoch="$2"
  [ "$branch_epoch" -gt "$comment_epoch" ]
}

# Paths excluded from the production-parity guard (git diff origin/main vs
# origin/preview): pure record-keeping, never rendered, safe to differ
# between preview and main without blocking a promotion. Coordinator review
# point E, 2026-09-21: the old guard only checked `$WEB_DIR`, which would
# have missed a difference in scripts/, .github/, hooks, rules, or
# AGENTS.md — any of which differing means production must not move.
# Anything not in this array is checked; keep this list short and specific.
PRODUCTION_GUARD_EXCLUDE=(
  ':(exclude)docs/**'
  ':(exclude)status.md'
  ':(exclude)decisions.md'
  ':(exclude)BACKLOG.md'
  ':(exclude)lessons.md'
  ':(exclude)README.md'
)

# --- The nine steps, defined at top level (not inside main) so sourcing
# this file for tests defines them without running anything. Each reads
# whatever globals it needs (ISSUE_ID, PREVIEW_MATCHES_MAIN, posture_note,
# ...) — the phase functions below set them before any step runs, and none
# of these functions ever WRITES one back for a later step in the SAME
# process to read (cross-process state, i.e. across separate guard/build/
# release invocations, goes through $STATE_DIR files instead — see the doc
# comment at the top of this file). That write direction is exactly what
# doesn't work within one process either: run_step above puts a step on the
# left side of a pipe, which bash always forks into a subshell, so an
# assignment made inside a step is real inside that subshell and gone the
# instant it exits. Reads work fine either way, because a forked subshell
# starts with a full copy of the parent's variables. This is, concretely,
# the bug the coordinator found in an earlier round: step7_promote used to
# set NO_PROMOTE="1" and step8_live_check used to read it — the read always
# saw the pre-step7 value, "0", so step8 never actually skipped. It now
# reads PREVIEW_MATCHES_MAIN instead, set once before step 1 ever runs and
# never written to by any step. -----------------

step1_merge() {
  git fetch "$REMOTE" preview &&
    git merge --no-edit "$REMOTE/preview"
}

step2_sign() {
  local reconfirm_flag=()
  if [ "$RECONFIRM" = "true" ]; then
    reconfirm_flag=(--reconfirm)
  fi
  ( cd "$WEB_DIR" && npm run sign:issue -- --signed-on "$SIGNED_ON" --id "$ISSUE_ID" "${reconfirm_flag[@]}" )
}

step3_lock() {
  ( cd "$WEB_DIR" && npm run verify:issue -- --write )
}

step4_test() {
  ( cd "$WEB_DIR" && npm test )
}

step5_commit() {
  # web/src/data/reconfirmations.ts is written by step2_sign only when
  # --reconfirm added an entry; git add on an unchanged tracked file is a
  # no-op, so this is safe to run every time (coordinator task T7-4). It is
  # deliberately NOT in is_allowed_issue_branch_path — the gather job never
  # writes it, only this step does.
  git add \
    "$WEB_DIR/src/data/issues/$ISSUE_ID.ts" \
    "$WEB_DIR/src/data/issues/issues.lock.json" \
    "$WEB_DIR/src/data/reconfirmations.ts" &&
    git commit -m "feat(issue): publish $ISSUE_ID, signed by approval of #${PR_NUMBER:-?}"
}

# Pushes with an explicit, per-invocation auth header rather than a stored
# credential (coordinator review point A(4), 2026-09-21): the issue-branch
# checkout uses persist-credentials: false, so nothing but this one command
# ever has push rights, and the header is never written to git config or
# echoed. `-c core.hooksPath=/dev/null` neutralizes any repo-local hook a
# branch might have added, in case one ever reaches this checkout.
authed_push() {
  local refspec="$1"
  local basic
  basic="$(printf 'x-access-token:%s' "$GH_TOKEN" | base64 | tr -d '\n')"
  git -c "http.extraheader=AUTHORIZATION: basic $basic" -c core.hooksPath=/dev/null push "$REMOTE" "$refspec"
}

# Order (coordinator review point H, 2026-09-21): preview first. A rejection
# here (someone else moved preview first) means nothing else has happened
# yet — no issue-branch push, no promotion — so "approve again" is a safe,
# complete instruction.
step6_push_preview() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY_RUN=1: not pushing to preview"
    return 0
  fi
  if ! authed_push "HEAD:refs/heads/preview"; then
    echo "push to preview for $ISSUE_ID was rejected — something else moved preview first, and nothing else happened for this run. Approve again and it will retry against the current preview."
    return 1
  fi
}

step7_push_issue_branch() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY_RUN=1: not pushing to $HEAD_BRANCH"
    return 0
  fi
  authed_push "HEAD:refs/heads/$HEAD_BRANCH"
}

step8_promote() {
  if [ "$PREVIEW_MATCHES_MAIN" != "true" ]; then
    # Fatal on purpose (coordinator review point J, 2026-09-21): a soft,
    # zero-exit comment here was the only way he'd learn of it, and that's
    # too easy to miss. The job showing failed is the loud version of the
    # same message. Not calling comment_pr directly here — run_step's
    # generic failure handler tails this echoed message and posts the one
    # comment, so a caller does not get this reason twice.
    echo "preview carried unpromoted site work before this run; not promoting to main. Issue $ISSUE_ID is signed and on preview, but production did not move: promote preview separately, then this issue reaches production on the next promotion.${posture_note:-}${reconfirm_note:-}"
    return 1
  fi
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY_RUN=1: not promoting to main"
    return 0
  fi
  authed_push "HEAD:refs/heads/main"
}

step9_live_check() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY_RUN=1: not polling the live site"
    return 0
  fi
  # Reads PREVIEW_MATCHES_MAIN from the parent shell — see the block comment
  # above these step definitions.
  if [ "$PREVIEW_MATCHES_MAIN" != "true" ]; then
    echo "preview did not match main before this run; nothing was promoted, skipping the live check"
    return 0
  fi

  local deadline
  deadline=$(( $(date +%s) + LIVE_POLL_SECONDS ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    local index_body page_body
    if index_body="$(curl -fsSL "$LIVE_BASE_URL/issues/index.json" 2>/dev/null)" \
      && printf '%s' "$index_body" | grep -q "\"$ISSUE_ID\"" \
      && page_body="$(curl -fsSL "$LIVE_BASE_URL/issues/$ISSUE_ID/" 2>/dev/null)" \
      && printf '%s' "$page_body" | grep -qF "$AUTHOR_NAME" \
      && printf '%s' "$page_body" | grep -qF "$SIGNED_ON"
    then
      comment_pr "Issue $ISSUE_ID is live at $LIVE_BASE_URL/issues/$ISSUE_ID/, signed by $AUTHOR_NAME on $SIGNED_ON.${posture_note:-}${reconfirm_note:-}"
      return 0
    fi
    sleep "$LIVE_POLL_INTERVAL"
  done

  comment_pr "Issue $ISSUE_ID was promoted but did not reach $LIVE_BASE_URL within $LIVE_POLL_SECONDS seconds. Check the Vercel deploy for the main branch."
  if [ "$GH_AVAILABLE" = "true" ] && [ "$DRY_RUN" != "1" ]; then
    gh issue create \
      --title "Publish of $ISSUE_ID did not reach the live site" \
      --body "publish-issue.sh promoted $ISSUE_ID to main but $LIVE_BASE_URL/issues/$ISSUE_ID/ did not carry it within $LIVE_POLL_SECONDS seconds. Check the Vercel deploy for main." \
      || echo "publish-issue.sh: warning — gh issue create failed" >&2
  fi
  return 1
}

# Refuses unless trusted/ — the second, separate checkout of preview's
# scripts/ this very script was invoked from — is still exactly what the
# workflow checked out, with nothing added or changed (coordinator review
# point A(4), 2026-09-21). Skipped, not failed, when no expectation was
# given: local/manual runs have no trusted/ checkout at all.
verify_trusted_checkout() {
  if [ -z "$TRUSTED_SHA_EXPECTED" ]; then
    echo "no TRUSTED_SHA_EXPECTED given, skipping the trusted-checkout integrity check (local/manual run)"
    return 0
  fi
  if [ ! -d trusted ]; then
    echo "publish-issue.sh: refusing — TRUSTED_SHA_EXPECTED was given but there is no trusted/ checkout here" >&2
    return 1
  fi
  local trusted_status trusted_sha_now
  trusted_status="$(git -C trusted status --porcelain 2>&1)" || {
    echo "publish-issue.sh: could not check trusted/'s status" >&2
    return 1
  }
  if [ -n "$trusted_status" ]; then
    echo "publish-issue.sh: refusing — trusted/ has local modifications:" >&2
    printf '%s\n' "$trusted_status" >&2
    return 1
  fi
  trusted_sha_now="$(git -C trusted rev-parse HEAD)"
  if [ "$trusted_sha_now" != "$TRUSTED_SHA_EXPECTED" ]; then
    echo "publish-issue.sh: refusing — trusted/ is at $trusted_sha_now, expected $TRUSTED_SHA_EXPECTED" >&2
    return 1
  fi
  echo "trusted-checkout integrity guard: trusted/ is clean and at the expected commit ($TRUSTED_SHA_EXPECTED)"
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --phase)
        PHASE="$2"
        shift 2
        ;;
      --phase=*)
        PHASE="${1#--phase=}"
        shift
        ;;
      *)
        shift
        ;;
    esac
  done
}

validate_common() {
  if [ -z "$HEAD_BRANCH" ]; then
    echo "publish-issue.sh: HEAD_BRANCH is required (e.g. issue/2026-w37)" >&2
    exit 1
  fi
  case "$HEAD_BRANCH" in
    issue/*) : ;;
    *)
      echo "publish-issue.sh: HEAD_BRANCH \"$HEAD_BRANCH\" does not match issue/*" >&2
      exit 1
      ;;
  esac
  if [ -z "$SIGNED_ON" ]; then
    echo "publish-issue.sh: SIGNED_ON is required (YYYY-MM-DD)" >&2
    exit 1
  fi
  if [ ! -f "$WEB_DIR/package.json" ]; then
    echo "publish-issue.sh: no $WEB_DIR/package.json here — run this from the repository root" >&2
    exit 1
  fi
  ISSUE_ID="${HEAD_BRANCH#issue/}"
}

guard_phase() {
  echo "publish-issue.sh: phase = guard"
  echo "RECONFIRM=$RECONFIRM (SEC-MARKET-PUBLISH-001 §4.3 — true re-dates stale, unchallenged judged claims at sign time)"

  if [ "$DRY_RUN" != "1" ] && [ -z "$APPROVED_SHA" ]; then
    echo "publish-issue.sh: APPROVED_SHA is required outside DRY_RUN (sign exactly what was approved)" >&2
    exit 1
  fi

  # Local (not global) git identity — the pre-flight fetch below needs none,
  # but keeping this here (rather than only in build) means guard can be run
  # standalone against a real checkout without a separate setup step.
  git config user.name "$AUTHOR_NAME"
  git config user.email "$AUTHOR_EMAIL"

  # --- Guard: sign exactly what was approved ---------------------------------
  if [ -n "$APPROVED_SHA" ]; then
    local current_sha
    current_sha="$(git rev-parse HEAD)"
    if ! approved_sha_matches "$current_sha" "$APPROVED_SHA"; then
      notify_failure "$(printf '%s moved after this approval (approved %s, branch is now at %s). Please review and approve again.' "$HEAD_BRANCH" "$APPROVED_SHA" "$current_sha")"
      echo "publish-issue.sh: refusing — HEAD ($current_sha) does not match the approved commit ($APPROVED_SHA)" >&2
      exit 1
    fi
    echo "approved-sha guard: HEAD matches the approved commit ($APPROVED_SHA)"
  else
    echo "DRY_RUN=1 and no APPROVED_SHA given: skipping the approved-commit guard"
  fi

  # --- Guard: the branch did not change after the "publish" comment ---------
  # (coordinator review point D, 2026-09-21). Comment-triggered path only.
  if [ -n "$COMMENT_CREATED_AT" ]; then
    local branch_epoch
    branch_epoch="$(git log -1 --format=%cd --date=unix HEAD)"
    if branch_changed_after_comment "$branch_epoch" "$COMMENT_CREATED_AT"; then
      notify_failure "$(printf '%s changed after you wrote "publish" (branch committed at epoch %s, the comment was at epoch %s). Comment publish again to sign the branch as it stands now.' "$HEAD_BRANCH" "$branch_epoch" "$COMMENT_CREATED_AT")"
      echo "publish-issue.sh: refusing — branch committer time ($branch_epoch) is after the comment ($COMMENT_CREATED_AT)" >&2
      exit 1
    fi
    echo "comment-race guard: the branch predates the publish comment"
  fi

  # --- Pre-flight: the production guard's snapshot ---------------------------
  # Spec §2.2 step 7: preview must not already differ from main outside pure
  # record-keeping paths (coordinator review point E, 2026-09-21 widened
  # this from just $WEB_DIR to the whole tree, see PRODUCTION_GUARD_EXCLUDE
  # above). Captured now, once, against refs as they stood before this run
  # touched anything, and written to $STATE_DIR for the release phase to
  # read later — preview will have moved by then (steps 6-7 push to it).
  printf '\n=== PRE-FLIGHT: production-guard snapshot ===\n'
  local preview_matches_main
  if [ -n "${FORCE_PREVIEW_MATCHES_MAIN:-}" ]; then
    preview_matches_main="$FORCE_PREVIEW_MATCHES_MAIN"
    echo "FORCE_PREVIEW_MATCHES_MAIN set — using \"$preview_matches_main\" instead of computing it (test seam only, never set this for a real publish)"
  else
    git fetch "$REMOTE" main preview >/dev/null 2>&1 || true
    if git diff --quiet "$REMOTE/main" "$REMOTE/preview" -- . "${PRODUCTION_GUARD_EXCLUDE[@]}"; then
      preview_matches_main="true"
    else
      preview_matches_main="false"
    fi
  fi
  echo "preview matches main (excluding record-keeping paths): $preview_matches_main"
  printf '%s' "$preview_matches_main" > "$STATE_DIR/preview-matches-main"

  # --- Guard: only the files the gather job may stage ------------------------
  local changed_files allowlist_violations=""
  changed_files="$(git diff --name-only "$REMOTE/preview...HEAD" 2>&1)" ||
    {
      echo "publish-issue.sh: could not diff $REMOTE/preview...HEAD to check the file allowlist" >&2
      echo "$changed_files" >&2
      exit 1
    }
  while IFS= read -r changed; do
    [ -z "$changed" ] && continue
    if ! is_allowed_issue_branch_path "$changed" "$ISSUE_ID" "$WEB_DIR"; then
      allowlist_violations="${allowlist_violations}${changed}"$'\n'
    fi
  done <<< "$changed_files"
  if [ -n "$allowlist_violations" ]; then
    notify_failure "$(printf 'Refusing to publish %s: it touches file(s) the gather job is not allowed to stage:\n\n```\n%s```\n\nAllowed: %s/src/data/issues/%s.ts, %s/src/data/issues/index.ts, %s/src/data/evidence.ts, %s/src/data/prints.ts, .gather/pr-body.md.' \
      "$ISSUE_ID" "$allowlist_violations" "$WEB_DIR" "$ISSUE_ID" "$WEB_DIR" "$WEB_DIR" "$WEB_DIR")"
    echo "publish-issue.sh: refusing — unexpected path(s) on $HEAD_BRANCH:" >&2
    printf '%s' "$allowlist_violations" >&2
    exit 1
  fi
  echo "file allowlist guard: only allowed paths changed on $HEAD_BRANCH"

  echo "publish-issue.sh: guard phase passed."
}

build_phase() {
  echo "publish-issue.sh: phase = build"

  git config user.name "$AUTHOR_NAME"
  git config user.email "$AUTHOR_EMAIL"

  run_step "1 merge origin/preview" step1_merge

  # step 2 is not run through run_step: sign-issue.ts exits 2 specifically
  # when the named issue is already published (coordinator review point L,
  # 2026-09-21), and that is a benign "nothing to do", not a failure.
  printf '\n=== STEP: 2 sign ===\n'
  : > "$STEP_LOG"
  step2_sign 2>&1 | tee "$STEP_LOG"
  local sign_rc="${PIPESTATUS[0]}"
  if [ "$sign_rc" -eq 2 ]; then
    echo "publish-issue.sh: $ISSUE_ID is already published — nothing to sign."
    if [ -n "${GITHUB_OUTPUT:-}" ]; then
      echo "outcome=already-published" >> "$GITHUB_OUTPUT"
    fi
    return 0
  elif [ "$sign_rc" -ne 0 ]; then
    local tail_output
    tail_output="$(tail -n 40 "$STEP_LOG")"
    notify_failure "$(printf 'Publish of %s failed at step: %s\n\n```\n%s\n```' "$ISSUE_ID" "2 sign" "$tail_output")"
    printf '\npublish-issue.sh: FAILED at step: 2 sign (exit %s)\n' "$sign_rc" >&2
    exit 1
  fi

  # sign-issue.ts prints "sign-issue: posture-deltas-dropped: N" on stdout,
  # captured to $STEP_LOG above. Written to $STATE_DIR (a plain digits-only
  # count) for the release phase's comments to read later.
  local posture_dropped
  posture_dropped="$(grep -oE 'posture-deltas-dropped: [0-9]+' "$STEP_LOG" | grep -oE '[0-9]+$' || true)"
  posture_dropped="${posture_dropped:-0}"
  printf '%s' "$posture_dropped" > "$STATE_DIR/posture-dropped"

  # sign-issue.ts also prints "sign-issue: reconfirmed: N" and
  # "sign-issue: challenged-left-stale: id1,id2" (comma-joined, possibly
  # empty) on every run, --reconfirm or not (SEC-MARKET-PUBLISH-001 §4.3,
  # coordinator task T7-4) — read here the same way posture_dropped is, for
  # the release phase's success comment.
  local reconfirmed_count
  reconfirmed_count="$(grep -oE 'sign-issue: reconfirmed: [0-9]+' "$STEP_LOG" | grep -oE '[0-9]+$' || true)"
  reconfirmed_count="${reconfirmed_count:-0}"
  printf '%s' "$reconfirmed_count" > "$STATE_DIR/reconfirmed-count"

  local challenged_left_stale
  challenged_left_stale="$(grep -E '^sign-issue: challenged-left-stale: ' "$STEP_LOG" | sed -E 's/^sign-issue: challenged-left-stale: //' || true)"
  printf '%s' "$challenged_left_stale" > "$STATE_DIR/challenged-left-stale"

  run_step "3 lock manifest" step3_lock
  run_step "4 npm test" step4_test
  run_step "5 commit" step5_commit

  echo ""
  echo "publish-issue.sh: build phase done. Local commit: $(git rev-parse HEAD)"
}

release_phase() {
  echo "publish-issue.sh: phase = release"

  if [ "$DRY_RUN" != "1" ] && [ -z "$GH_TOKEN" ]; then
    echo "publish-issue.sh: GH_TOKEN is required for the release phase outside DRY_RUN" >&2
    exit 1
  fi

  git config user.name "$AUTHOR_NAME"
  git config user.email "$AUTHOR_EMAIL"
  # Neutralizes any repo-local hook a branch might have added, before any
  # git operation in this token-bearing phase touches it (coordinator review
  # point A(4), 2026-09-21).
  git config core.hooksPath /dev/null

  if ! verify_trusted_checkout; then
    comment_pr "Refusing to release $ISSUE_ID: the trusted copy of the publisher script no longer matches what this run checked out at the start. Nothing was pushed."
    exit 1
  fi

  if [ -f "$STATE_DIR/preview-matches-main" ]; then
    PREVIEW_MATCHES_MAIN="$(cat "$STATE_DIR/preview-matches-main")"
  else
    PREVIEW_MATCHES_MAIN="${FORCE_PREVIEW_MATCHES_MAIN:-false}"
    echo "publish-issue.sh: no $STATE_DIR/preview-matches-main from the guard phase; using \"$PREVIEW_MATCHES_MAIN\""
  fi
  case "$PREVIEW_MATCHES_MAIN" in
    true|false) : ;;
    *)
      echo "publish-issue.sh: refusing — preview-matches-main state \"$PREVIEW_MATCHES_MAIN\" is not true/false" >&2
      exit 1
      ;;
  esac

  posture_note=""
  if [ -f "$STATE_DIR/posture-dropped" ]; then
    local posture_dropped
    posture_dropped="$(cat "$STATE_DIR/posture-dropped")"
    case "$posture_dropped" in
      ''|*[!0-9]*) posture_dropped=0 ;;
    esac
    if [ "$posture_dropped" -gt 0 ]; then
      posture_note=" The proposal's posture-deltas note was not applied automatically (the signer never converts prose stance notes into structured posture deltas); stance changes are made separately."
    fi
  fi

  # Reconfirmation note (SEC-MARKET-PUBLISH-001 §4.3, coordinator task T7-4):
  # says how many stale, unchallenged stances this approval just re-dated,
  # and names any challenged ones it deliberately left stale because this
  # week's evidence cuts against them — those need a human look, not a
  # rubber stamp, so the comment says so plainly.
  local reconfirm_note=""
  local reconfirmed_count=0
  if [ -f "$STATE_DIR/reconfirmed-count" ]; then
    reconfirmed_count="$(cat "$STATE_DIR/reconfirmed-count")"
    case "$reconfirmed_count" in
      ''|*[!0-9]*) reconfirmed_count=0 ;;
    esac
  fi
  local challenged_left_stale=""
  if [ -f "$STATE_DIR/challenged-left-stale" ]; then
    challenged_left_stale="$(cat "$STATE_DIR/challenged-left-stale")"
  fi
  if [ "$RECONFIRM" = "true" ]; then
    reconfirm_note=" $reconfirmed_count stance(s) re-dated on this approval."
    if [ -n "$challenged_left_stale" ]; then
      reconfirm_note="${reconfirm_note} Left stale because this week's evidence cuts against them (needs a session): ${challenged_left_stale}."
    fi
  fi

  run_step "6 push preview" step6_push_preview
  run_step "7 push issue branch" step7_push_issue_branch
  run_step "8 promote to main" step8_promote
  run_step "9 live check" step9_live_check

  echo ""
  echo "publish-issue.sh: done."
}

main() {
  parse_args "$@"
  case "$PHASE" in
    guard|build|release|all) : ;;
    *)
      echo "publish-issue.sh: unknown --phase \"$PHASE\" (want guard, build, release, or all)" >&2
      exit 1
      ;;
  esac

  validate_common

  if [ -z "$STATE_DIR" ]; then
    STATE_DIR="$(mktemp -d)"
    STATE_DIR_OWNED="1"
  fi
  mkdir -p "$STATE_DIR"

  case "$PHASE" in
    guard|build) PHASE_CAN_COMMENT="false" ;;
    release|all) PHASE_CAN_COMMENT="true" ;;
  esac

  case "$PHASE" in
    guard) guard_phase ;;
    build) build_phase ;;
    release) release_phase ;;
    all)
      guard_phase
      build_phase
      release_phase
      ;;
  esac
}

# Only run main when executed directly — sourcing this file (as
# scripts/test-publish-issue.sh does) must define the guard functions above
# without validating env vars or touching git.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
