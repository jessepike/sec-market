#!/bin/bash
#
# Publishes the one signed-by-approval weekly issue (SEC-MARKET-PUBLISH-001
# §2.2). Called by .github/workflows/publish-issue.yml, kept thin on purpose:
# every ordered step and every refusal lives here so it can be run and tested
# outside GitHub, in a plain clone. See scripts/test-publish-issue.sh for the
# unit-level tests of the guard logic below (sourced, not executed).
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
#   -  guard: the issue branch may only have touched files the gather job is
#      allowed to stage (docs/active/gather-brief.md) — everything else
#      refuses rather than running an unreviewed diff through a write token
#   1. merge origin/preview into the current branch (a conflict is a failure)
#   2. sign the one draft issue (web/scripts/sign-issue.ts)
#   3. append it to the lock manifest (npm run verify:issue -- --write)
#   4. run everything (npm test, in web/)
#   5. commit as Jesse Pike <jesse@keatingpike.com> and push to the issue branch
#   6. fast-forward preview to that commit
#   7. promote to main, but only if preview already matched main before this
#      run started
#   8. poll the live site for up to fifteen minutes and comment the result
#
# A failure at any step stops everything after it, prints which step failed
# and the last lines of its output, and (outside DRY_RUN, with `gh` present
# and PR_NUMBER set) comments that on the pull request.
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
#   REMOTE              git remote name (default: origin)
#   WEB_DIR             the web app's directory (default: web)
#   DRY_RUN              1 disables every push and the live poll (step 8).
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
#   LIVE_BASE_URL        the live site's origin, for step 8 (default:
#                        https://securitymarketpulse.com)
#   LIVE_POLL_SECONDS    how long step 8 polls before giving up (default: 900)
#   LIVE_POLL_INTERVAL   seconds between polls (default: 15)
#   AUTHOR_NAME          must equal AUTHOR_NAME in web/src/data/meta.ts; used
#                        for the commit author and the step 8 page check
#                        (default: Jesse Pike)
#   AUTHOR_EMAIL         the commit author's email (default:
#                        jesse@keatingpike.com — Vercel refuses any other)
#
# Exit code: 0 on success (including the step 7 "signed but not promoted"
# outcome, which is not a failure). Non-zero names the failed step, or the
# guard that refused, on stderr.

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

GH_AVAILABLE="false"
if command -v gh >/dev/null 2>&1; then GH_AVAILABLE="true"; fi

STEP_LOG="$(mktemp)"
trap 'rm -f "$STEP_LOG"' EXIT

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
    comment_pr "$(printf 'Publish of %s failed at step: %s\n\n```\n%s\n```' "$ISSUE_ID" "$name" "$tail_output")"
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
# (checked 2026-09-21 against that file's own "you write to exactly four
# files" list): the new issue module, the issues index, the append-only
# evidence file, and the scorecard figures file. Nothing under `.gather/` is
# in gather-brief.md's list — an earlier draft of this guard assumed that
# path existed and it does not, so it is not in the allowlist. Widening this
# list needs the owner's word (docs/active/publish-path-spec.md).
is_allowed_issue_branch_path() {
  local path="$1" issue_id="$2" web_dir="$3"
  case "$path" in
    "$web_dir/src/data/issues/$issue_id.ts") return 0 ;;
    "$web_dir/src/data/issues/index.ts") return 0 ;;
    "$web_dir/src/data/evidence.ts") return 0 ;;
    "$web_dir/src/data/prints.ts") return 0 ;;
    *) return 1 ;;
  esac
}

# --- The eight steps, defined at top level (not inside main) so sourcing
# this file for tests defines them without running anything. Each reads
# whatever globals it needs (ISSUE_ID, PREVIEW_MATCHES_MAIN, posture_note,
# ...) — main() sets them before any step runs, and none of these functions
# ever WRITES one back for a later step to read. That write direction is
# exactly what doesn't work: run_step below puts a step on the left side of a
# pipe, which bash always forks into a subshell, so an assignment made inside
# a step is real inside that subshell and gone the instant it exits. Reads
# work fine either way, because a forked subshell starts with a full copy of
# the parent's variables. This is, concretely, the bug the coordinator found:
# step7_promote used to set NO_PROMOTE="1" and step8_live_check used to read
# it — the read always saw the pre-step7 value, "0", so step8 never actually
# skipped. It now reads PREVIEW_MATCHES_MAIN instead, set once in main()
# before step 1 ever runs and never written to by any step. -----------------

step1_merge() {
  git fetch "$REMOTE" preview &&
    git merge --no-edit "$REMOTE/preview"
}

step2_sign() {
  ( cd "$WEB_DIR" && npm run sign:issue -- --signed-on "$SIGNED_ON" --id "$ISSUE_ID" )
}

step3_lock() {
  ( cd "$WEB_DIR" && npm run verify:issue -- --write )
}

step4_test() {
  ( cd "$WEB_DIR" && npm test )
}

step5_commit_and_push() {
  git add \
    "$WEB_DIR/src/data/issues/$ISSUE_ID.ts" \
    "$WEB_DIR/src/data/issues/issues.lock.json" &&
    git commit -m "feat(issue): publish $ISSUE_ID, signed by approval of #${PR_NUMBER:-?}" || return 1
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY_RUN=1: not pushing to $HEAD_BRANCH"
    return 0
  fi
  git push "$REMOTE" "HEAD:refs/heads/$HEAD_BRANCH"
}

step6_fastforward_preview() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY_RUN=1: not fast-forwarding preview"
    return 0
  fi
  git push "$REMOTE" "HEAD:refs/heads/preview"
}

step7_promote() {
  if [ "$PREVIEW_MATCHES_MAIN" != "true" ]; then
    echo "preview carried unpromoted site work before this run; not promoting to main."
    comment_pr "Issue $ISSUE_ID is signed and on preview. Production did not move: preview already held site work that was never promoted, and approving this issue is not approval of that. Promote preview separately, then this issue reaches production on the next promotion.${posture_note:-}"
    return 0
  fi
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY_RUN=1: not promoting to main"
    return 0
  fi
  git push "$REMOTE" "HEAD:refs/heads/main"
}

step8_live_check() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY_RUN=1: not polling the live site"
    return 0
  fi
  # Reads PREVIEW_MATCHES_MAIN from the parent shell, set once at pre-flight
  # in main(), below — see the block comment above these step definitions.
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
      comment_pr "Issue $ISSUE_ID is live at $LIVE_BASE_URL/issues/$ISSUE_ID/, signed by $AUTHOR_NAME on $SIGNED_ON.${posture_note:-}"
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

main() {
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
  if [ "$DRY_RUN" != "1" ] && [ -z "$APPROVED_SHA" ]; then
    echo "publish-issue.sh: APPROVED_SHA is required outside DRY_RUN (sign exactly what was approved)" >&2
    exit 1
  fi

  ISSUE_ID="${HEAD_BRANCH#issue/}"

  # Local (not global) git identity, set once here rather than only on the
  # final commit — step 1's merge commit needs one too, and a bare CI
  # checkout normally has none configured at all.
  git config user.name "$AUTHOR_NAME"
  git config user.email "$AUTHOR_EMAIL"

  # --- Guard: sign exactly what was approved ---------------------------------
  if [ -n "$APPROVED_SHA" ]; then
    local current_sha
    current_sha="$(git rev-parse HEAD)"
    if ! approved_sha_matches "$current_sha" "$APPROVED_SHA"; then
      comment_pr "$(printf '%s moved after this approval (approved %s, branch is now at %s). Please review and approve again.' "$HEAD_BRANCH" "$APPROVED_SHA" "$current_sha")"
      echo "publish-issue.sh: refusing — HEAD ($current_sha) does not match the approved commit ($APPROVED_SHA)" >&2
      exit 1
    fi
    echo "approved-sha guard: HEAD matches the approved commit ($APPROVED_SHA)"
  else
    echo "DRY_RUN=1 and no APPROVED_SHA given: skipping the approved-commit guard"
  fi

  # --- Pre-flight: the production guard's snapshot ---------------------------
  # Spec §2.2 step 7: "before step 1, git diff --quiet origin/main
  # origin/preview -- web must be clean." Captured now, once, against refs as
  # they stood before this run touched anything, and reused at step 7 —
  # preview will have moved by then (steps 5-6 push to it). Read by step 8 as
  # well (never by anything set inside a step function — see run_step above).
  printf '\n=== PRE-FLIGHT: production-guard snapshot ===\n'
  if [ -n "${FORCE_PREVIEW_MATCHES_MAIN:-}" ]; then
    PREVIEW_MATCHES_MAIN="$FORCE_PREVIEW_MATCHES_MAIN"
    echo "FORCE_PREVIEW_MATCHES_MAIN set — using \"$PREVIEW_MATCHES_MAIN\" instead of computing it (test seam only, never set this for a real publish)"
  else
    git fetch "$REMOTE" main preview >/dev/null 2>&1 || true
    if git diff --quiet "$REMOTE/main" "$REMOTE/preview" -- "$WEB_DIR"; then
      PREVIEW_MATCHES_MAIN="true"
    else
      PREVIEW_MATCHES_MAIN="false"
    fi
  fi
  echo "preview matches main on $WEB_DIR/: $PREVIEW_MATCHES_MAIN"

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
    comment_pr "$(printf 'Refusing to publish %s: it touches file(s) the gather job is not allowed to stage:\n\n```\n%s```\n\nAllowed: %s/src/data/issues/%s.ts, %s/src/data/issues/index.ts, %s/src/data/evidence.ts, %s/src/data/prints.ts.' \
      "$ISSUE_ID" "$allowlist_violations" "$WEB_DIR" "$ISSUE_ID" "$WEB_DIR" "$WEB_DIR" "$WEB_DIR")"
    echo "publish-issue.sh: refusing — unexpected path(s) on $HEAD_BRANCH:" >&2
    printf '%s' "$allowlist_violations" >&2
    exit 1
  fi
  echo "file allowlist guard: only allowed paths changed on $HEAD_BRANCH"

  run_step "1 merge origin/preview" step1_merge
  run_step "2 sign" step2_sign

  # sign-issue.ts prints "sign-issue: posture-deltas-dropped: N" on stdout,
  # captured to $STEP_LOG by run_step above (read here, before step 3
  # truncates it). posture_note is a global (no `local`), because step7 and
  # step8 read it and, per the note above the step definitions, a step
  # function only ever reads globals set here — it never needs to write one.
  local posture_dropped
  posture_dropped="$(grep -oE 'posture-deltas-dropped: [0-9]+' "$STEP_LOG" | grep -oE '[0-9]+$' || true)"
  posture_dropped="${posture_dropped:-0}"
  posture_note=""
  if [ "$posture_dropped" -gt 0 ]; then
    posture_note=" The proposal's posture-deltas note was not applied automatically (the signer never converts prose stance notes into structured posture deltas); stance changes are made separately."
  fi

  run_step "3 lock manifest" step3_lock
  run_step "4 npm test" step4_test
  run_step "5 commit and push" step5_commit_and_push
  run_step "6 fast-forward preview" step6_fastforward_preview
  run_step "7 promote to main" step7_promote
  run_step "8 live check" step8_live_check

  echo ""
  echo "publish-issue.sh: done."
}

# Only run main when executed directly — sourcing this file (as
# scripts/test-publish-issue.sh does) must define the guard functions above
# without validating env vars or touching git.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
