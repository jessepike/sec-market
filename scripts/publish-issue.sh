#!/bin/bash
#
# Publishes the one signed-by-approval weekly issue (SEC-MARKET-PUBLISH-001
# §2.2). Called by .github/workflows/publish-issue.yml, kept thin on purpose:
# every ordered step and every refusal lives here so it can be run and tested
# outside GitHub, in a plain clone.
#
# Assumes it is invoked from the repository root, on a checkout that is
# ALREADY on the pull request's head branch (issue/<id>) with full history —
# that is the GitHub Actions checkout step's job, not this script's. What
# this script does, in order, is exactly spec §2.2 steps 1-8:
#
#   1. merge origin/preview into the current branch (a conflict is a failure)
#   2. sign the one draft issue (web/scripts/sign-issue.ts)
#   3. append it to the lock manifest (npm run verify:issue -- --write)
#   4. run everything (npm test, in web/)
#   5. commit as Jesse Pike <jesse@keatingpike.com> and push to the issue branch
#   6. fast-forward preview to that commit
#   7. promote to main, but only if preview carried nothing preview already
#      matched main on before this run started
#   8. poll the live site for up to fifteen minutes and comment the result
#
# A failure at any step stops everything after it, prints which step failed
# and the last lines of its output, and (outside DRY_RUN, with `gh` present
# and PR_NUMBER set) comments that on the pull request.
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
#   REMOTE              git remote name (default: origin)
#   WEB_DIR             the web app's directory (default: web)
#   DRY_RUN              1 disables every push and the live poll (step 8).
#                        Everything else — the merge, the sign, the lock
#                        write, npm test, and the local commit — still runs,
#                        so a dry run proves the issue comes out signed and
#                        locked and that the test suite passes, without
#                        touching any remote ref. (default: 0)
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
# outcome, which is not a failure). Non-zero names the failed step on stderr.

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

# Local (not global) git identity, set once here rather than only on the
# final commit — step 1's merge commit needs one too, and a bare CI checkout
# normally has none configured at all.
git config user.name "$AUTHOR_NAME"
git config user.email "$AUTHOR_EMAIL"

GH_AVAILABLE="false"
if command -v gh >/dev/null 2>&1; then GH_AVAILABLE="true"; fi

NO_PROMOTE="0"
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
# PIPESTATUS rather than $? because the command is piped through tee.
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

# --- Pre-flight, before step 1: the production guard's snapshot -------------
# Spec §2.2 step 7: "before step 1, git diff --quiet origin/main
# origin/preview -- web must be clean." Captured now, once, against
# refs as they stood before this run touched anything, and reused at step 7
# — preview will have moved by then (steps 5-6 push to it).
printf '\n=== PRE-FLIGHT: production-guard snapshot ===\n'
git fetch "$REMOTE" main preview >/dev/null 2>&1 || true
if git diff --quiet "$REMOTE/main" "$REMOTE/preview" -- "$WEB_DIR"; then
  PREVIEW_MATCHES_MAIN="true"
else
  PREVIEW_MATCHES_MAIN="false"
fi
echo "preview matches main on $WEB_DIR/: $PREVIEW_MATCHES_MAIN"

# --- Step 1: merge preview into the (already checked out) head branch -------
step1_merge() {
  git fetch "$REMOTE" preview "$HEAD_BRANCH" &&
    git merge --no-edit "$REMOTE/preview"
}
run_step "1 merge origin/preview" step1_merge

# --- Step 2: sign the one draft issue ---------------------------------------
step2_sign() {
  ( cd "$WEB_DIR" && npm run sign:issue -- --signed-on "$SIGNED_ON" --id "$ISSUE_ID" )
}
run_step "2 sign" step2_sign

# --- Step 3: append to the lock manifest ------------------------------------
step3_lock() {
  ( cd "$WEB_DIR" && npm run verify:issue -- --write )
}
run_step "3 lock manifest" step3_lock

# --- Step 4: run everything --------------------------------------------------
step4_test() {
  ( cd "$WEB_DIR" && npm test )
}
run_step "4 npm test" step4_test

# --- Step 5: commit and push to the issue branch ----------------------------
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
run_step "5 commit and push" step5_commit_and_push

# --- Step 6: fast-forward preview -------------------------------------------
step6_fastforward_preview() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY_RUN=1: not fast-forwarding preview"
    return 0
  fi
  git push "$REMOTE" "HEAD:refs/heads/preview"
}
run_step "6 fast-forward preview" step6_fastforward_preview

# --- Step 7: promote to main, only if preview carried nothing else ----------
step7_promote() {
  if [ "$PREVIEW_MATCHES_MAIN" != "true" ]; then
    NO_PROMOTE="1"
    echo "preview carried unpromoted site work before this run; not promoting to main."
    comment_pr "Issue $ISSUE_ID is signed and on preview. Production did not move: preview already held site work that was never promoted, and approving this issue is not approval of that. Promote preview separately, then this issue reaches production on the next promotion."
    return 0
  fi
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY_RUN=1: not promoting to main"
    return 0
  fi
  git push "$REMOTE" "HEAD:refs/heads/main"
}
run_step "7 promote to main" step7_promote

# --- Step 8: confirm the live site ------------------------------------------
step8_live_check() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY_RUN=1: not polling the live site"
    return 0
  fi
  if [ "$NO_PROMOTE" = "1" ]; then
    echo "nothing was promoted this run; skipping the live check"
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
      comment_pr "Issue $ISSUE_ID is live at $LIVE_BASE_URL/issues/$ISSUE_ID/, signed by $AUTHOR_NAME on $SIGNED_ON."
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
run_step "8 live check" step8_live_check

echo ""
echo "publish-issue.sh: done."
