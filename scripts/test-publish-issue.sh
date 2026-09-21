#!/bin/bash
#
# Unit-level tests for the guard logic in scripts/publish-issue.sh, run
# without a network or npm — because publish-issue.sh's `main` only runs
# when the file is executed directly (see its last few lines), sourcing it
# here just defines the guard functions and step functions. A couple of
# tests below do touch git, but only local, on-disk repos (a `git remote`
# pointing at a local path, or a branch literally named "origin/main") —
# that is not a network call, and it is how points E and H/J below get real
# coverage without a GitHub round trip.
#
# Run: bash scripts/test-publish-issue.sh
# Exit: 0 if every assertion passes, 1 (with a FAIL line) otherwise.
#
# Added for the coordinator's review of SEC-MARKET-PUBLISH-001 build 1
# (2026-09-21), specifically to prove the NO_PROMOTE subshell bug is fixed:
# step8_promote used to set a variable inside a step function, which
# run_step forks into a subshell (it runs on the left of a pipe), so the
# assignment never reached step9_live_check. The fix reads a variable set
# before any step runs (PREVIEW_MATCHES_MAIN), and this file's `not-promoted
# path skips the live check` test is the regression guard for that specific
# bug. Extended for the coordinator's twelve-point adversarial review
# (2026-09-21): points D, E, H, J below (points B, C, K, L are either
# already covered here, TypeScript-side, or in web/tests/sign-issue.test.ts).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./publish-issue.sh
source "$SCRIPT_DIR/publish-issue.sh"

FAILURES=0

check() {
  local description="$1" got="$2" want="$3"
  if [ "$got" = "$want" ]; then
    echo "PASS: $description"
  else
    echo "FAIL: $description — got [$got], want [$want]"
    FAILURES=$((FAILURES + 1))
  fi
}

check_contains() {
  local description="$1" haystack="$2" needle="$3"
  if printf '%s' "$haystack" | grep -qF "$needle"; then
    echo "PASS: $description"
  else
    echo "FAIL: $description — expected to find [$needle] in output"
    FAILURES=$((FAILURES + 1))
  fi
}

echo "--- is_allowed_issue_branch_path (file allowlist guard) ---"
if is_allowed_issue_branch_path "web/src/data/issues/2026-w37.ts" "2026-w37" "web"; then
  echo "PASS: the draft's own issue module is allowed"
else
  echo "FAIL: the draft's own issue module should be allowed"; FAILURES=$((FAILURES + 1))
fi
if is_allowed_issue_branch_path "web/src/data/issues/2026-w36.ts" "2026-w37" "web"; then
  echo "FAIL: a different issue's module should not be allowed"; FAILURES=$((FAILURES + 1))
else
  echo "PASS: a different issue's module is refused"
fi
for allowed in \
  "web/src/data/issues/index.ts" \
  "web/src/data/evidence.ts" \
  "web/src/data/prints.ts" \
  ".gather/pr-body.md"; do
  if is_allowed_issue_branch_path "$allowed" "2026-w37" "web"; then
    echo "PASS: $allowed is allowed"
  else
    echo "FAIL: $allowed should be allowed"; FAILURES=$((FAILURES + 1))
  fi
done
for disallowed in \
  "web/src/data/domains.ts" \
  "web/src/data/meta.ts" \
  "web/scripts/verify-issue.ts" \
  "web/src/data/reconfirmations.ts" \
  ".gather/state.json" \
  "intent.md" \
  ".claude/rules/constraints.md"; do
  if is_allowed_issue_branch_path "$disallowed" "2026-w37" "web"; then
    echo "FAIL: $disallowed should NOT be allowed"; FAILURES=$((FAILURES + 1))
  else
    echo "PASS: $disallowed is refused"
  fi
done

echo ""
echo "--- approved_sha_matches (sign exactly what was approved) ---"
if approved_sha_matches "abc123" "abc123"; then
  echo "PASS: identical shas match"
else
  echo "FAIL: identical shas should match"; FAILURES=$((FAILURES + 1))
fi
if approved_sha_matches "abc123" "def456"; then
  echo "FAIL: different shas should not match"; FAILURES=$((FAILURES + 1))
else
  echo "PASS: different shas (branch moved after approval) are refused"
fi

echo ""
echo "--- branch_changed_after_comment (coordinator review point D) ---"
if branch_changed_after_comment "2000" "1000"; then
  echo "PASS: a branch committed after the comment is refused"
else
  echo "FAIL: branch epoch 2000 > comment epoch 1000 should refuse"; FAILURES=$((FAILURES + 1))
fi
if branch_changed_after_comment "1000" "2000"; then
  echo "FAIL: branch epoch 1000 < comment epoch 2000 should NOT refuse"; FAILURES=$((FAILURES + 1))
else
  echo "PASS: a branch that predates the comment is allowed"
fi
if branch_changed_after_comment "1000" "1000"; then
  echo "FAIL: equal epochs (branch committed at exactly the comment's second) should NOT refuse"; FAILURES=$((FAILURES + 1))
else
  echo "PASS: equal epochs are allowed (not strictly after)"
fi

echo ""
echo "--- production-guard exclusion pathspec (coordinator review point E) ---"
# A real, local, on-disk repo — no network — with two branches literally
# named "origin/main" and "origin/preview" (git allows slashes in branch
# names), so git diff --quiet "$REMOTE/main" "$REMOTE/preview" ... resolves
# them exactly like it would resolve real remote-tracking refs, without
# needing an actual remote.
PG_REPO="$(mktemp -d)"
(
  cd "$PG_REPO" || exit 1
  git init -q .
  git config user.email test@example.com
  git config user.name "Test"
  mkdir -p docs web/src scripts
  echo "one" > web/src/app.ts
  echo "one" > scripts/deploy.sh
  echo "one" > docs/notes.md
  echo "one" > status.md
  git add -A
  git commit -qm "base"
  git branch "origin/main"
  git branch "origin/preview"
)

pg_diff_clean() {
  ( cd "$PG_REPO" && git diff --quiet "origin/main" "origin/preview" -- . "${PRODUCTION_GUARD_EXCLUDE[@]}" )
}

if pg_diff_clean; then
  echo "PASS: identical branches read as matching"
else
  echo "FAIL: identical branches should read as matching"; FAILURES=$((FAILURES + 1))
fi

( cd "$PG_REPO" && git checkout -q "origin/preview" && echo "two" > docs/notes.md && git add -A && git commit -qm "docs only" )
if pg_diff_clean; then
  echo "PASS: a docs/-only difference is excluded (still matching)"
else
  echo "FAIL: a docs/-only difference should still read as matching"; FAILURES=$((FAILURES + 1))
fi

( cd "$PG_REPO" && echo "two" > status.md && git add -A && git commit -qm "status only" )
if pg_diff_clean; then
  echo "PASS: a status.md-only difference is excluded (still matching)"
else
  echo "FAIL: a status.md-only difference should still read as matching"; FAILURES=$((FAILURES + 1))
fi

( cd "$PG_REPO" && echo "two" > scripts/deploy.sh && git add -A && git commit -qm "scripts too" )
if pg_diff_clean; then
  echo "FAIL: a scripts/ difference should NOT be excluded — this is exactly what the old -- web pathspec missed"
  FAILURES=$((FAILURES + 1))
else
  echo "PASS: a scripts/ difference is caught (the old guard only checked web/)"
fi

( cd "$PG_REPO" && git checkout -q "origin/main" && echo "two" > web/src/app.ts && git add -A && git commit -qm "site code" )
if pg_diff_clean; then
  echo "FAIL: a web/ difference should NOT be excluded"
  FAILURES=$((FAILURES + 1))
else
  echo "PASS: a web/ difference is still caught"
fi

rm -rf "$PG_REPO"

echo ""
echo "--- step2_sign: passes --reconfirm to sign:issue only when RECONFIRM=true (SEC-MARKET-PUBLISH-001 §4.3) ---"
# Stubs `npm` as a shell function so this stays a unit test (no real npm, no
# network, no actual signing) while still exercising step2_sign's own
# command construction — the thing coordinator task T7-4 changed.
STEP2_DIR="$(mktemp -d)"
mkdir -p "$STEP2_DIR/web"
npm() {
  printf 'npm-called: %s\n' "$*" > "$STEP2_DIR/npm-call.txt"
}
export -f npm

(
  cd "$STEP2_DIR" || exit 1
  WEB_DIR="web"
  SIGNED_ON="2026-09-21"
  ISSUE_ID="2026-w37"
  RECONFIRM="false"
  step2_sign
)
if grep -q -- '--reconfirm' "$STEP2_DIR/npm-call.txt"; then
  echo "FAIL: RECONFIRM=false should not pass --reconfirm to sign:issue"
  FAILURES=$((FAILURES + 1))
else
  echo "PASS: RECONFIRM=false omits --reconfirm"
fi

(
  cd "$STEP2_DIR" || exit 1
  WEB_DIR="web"
  SIGNED_ON="2026-09-21"
  ISSUE_ID="2026-w37"
  RECONFIRM="true"
  step2_sign
)
if grep -q -- '--reconfirm' "$STEP2_DIR/npm-call.txt"; then
  echo "PASS: RECONFIRM=true passes --reconfirm"
else
  echo "FAIL: RECONFIRM=true should pass --reconfirm to sign:issue"
  FAILURES=$((FAILURES + 1))
fi

unset -f npm
rm -rf "$STEP2_DIR"

echo ""
echo "--- step9_live_check: the not-promoted path skips the live check ---"
# Regression test for the NO_PROMOTE subshell bug: PREVIEW_MATCHES_MAIN is a
# parent-shell variable read by step9_live_check, never one a step function
# tried to set. DRY_RUN=0 here on purpose, so a bug that fell through to the
# real polling loop would hang for LIVE_POLL_SECONDS instead of returning
# immediately — this test would time out rather than silently pass.
DRY_RUN="0"
PREVIEW_MATCHES_MAIN="false"
GH_AVAILABLE="false"
ISSUE_ID="test-issue"
AUTHOR_NAME="Jesse Pike"
SIGNED_ON="2026-09-21"
LIVE_BASE_URL="http://127.0.0.1:1"   # unreachable on purpose — any real curl call fails fast
LIVE_POLL_SECONDS="600"
LIVE_POLL_INTERVAL="5"
PR_NUMBER=""
STEP_LOG="$(mktemp)"

start="$(date +%s)"
output="$(step9_live_check 2>&1)"
rc=$?
elapsed="$(( $(date +%s) - start ))"
rm -f "$STEP_LOG"

check "not-promoted path returns success" "$rc" "0"
check_contains "not-promoted path explains why it skipped" "$output" "skipping the live check"
if [ "$elapsed" -lt 5 ]; then
  echo "PASS: returned immediately ($elapsed s) rather than entering the poll loop"
else
  echo "FAIL: took ${elapsed}s — looks like it fell through to the real poll loop"
  FAILURES=$((FAILURES + 1))
fi

echo ""
echo "--- step9_live_check: DRY_RUN always skips regardless of PREVIEW_MATCHES_MAIN ---"
DRY_RUN="1"
PREVIEW_MATCHES_MAIN="true"
STEP_LOG="$(mktemp)"
output="$(step9_live_check 2>&1)"
rc=$?
rm -f "$STEP_LOG"
check "DRY_RUN path returns success" "$rc" "0"
check_contains "DRY_RUN path says it is not polling" "$output" "DRY_RUN=1: not polling the live site"

echo ""
echo "--- step8_promote: the not-promoted path is now fatal (coordinator review point J) ---"
DRY_RUN="0"
PREVIEW_MATCHES_MAIN="false"
GH_AVAILABLE="false"
PR_NUMBER=""
posture_note=""
STEP_LOG="$(mktemp)"
output="$(step8_promote 2>&1)"
rc=$?
rm -f "$STEP_LOG"
check "not-promoted path is now a failure (exit 1, not 0)" "$rc" "1"
check_contains "not-promoted path still explains why" "$output" "not promoting to main"

echo ""
echo "--- release_phase, end to end, against a local (no-network) file remote: push order (H) and a fatal promote (J) ---"
# A real "origin" — an actual git remote — but a bare repo on local disk, not
# a network endpoint. This exercises step6/7/8 (push preview, push issue
# branch, promote to main) exactly as release_phase() runs them, including
# authed_push, without ever reaching GitHub. GH_TOKEN is a throwaway value:
# a local file:// remote does no auth at all, so the header authed_push adds
# is inert here — this test is about push ORDER and the promote guard, not
# about token handling itself.
E2E_REMOTE="$(mktemp -d)"
E2E_CLONE="$(mktemp -d)"
(
  cd "$E2E_REMOTE" || exit 1
  git init -q --bare .
)
(
  cd "$E2E_CLONE" || exit 1
  git clone -q "$E2E_REMOTE" repo
  cd repo || exit 1
  git config user.email test@example.com
  git config user.name "Test"
  mkdir -p web
  echo '{}' > web/package.json
  echo "base" > README.md
  git add -A
  git commit -qm "base"
  git branch -m main
  git push -q origin main
  git checkout -q -b preview
  git push -q origin preview
  git checkout -q -b issue/2026-w99
  echo "signed" > web/signed.txt
  git add -A
  git commit -qm "feat(issue): publish 2026-w99"
)

(
  cd "$E2E_CLONE/repo" || exit 1
  REMOTE="origin"
  WEB_DIR="web"
  DRY_RUN="0"
  GH_AVAILABLE="false"
  GH_TOKEN="not-checked-by-a-local-remote"
  PR_NUMBER=""
  PREVIEW_MATCHES_MAIN="true"
  posture_note=""
  ISSUE_ID="2026-w99"
  HEAD_BRANCH="issue/2026-w99"

  step6_push_preview && step7_push_issue_branch && step8_promote
)
E2E_RC=$?

if [ "$E2E_RC" -eq 0 ]; then
  echo "PASS: release_phase's push steps succeeded end to end against a local remote"
else
  echo "FAIL: release_phase's push steps should have succeeded (rc=$E2E_RC)"; FAILURES=$((FAILURES + 1))
fi

E2E_MAIN_HAS_COMMIT="$(cd "$E2E_REMOTE" && git log main --oneline 2>/dev/null | grep -c "publish 2026-w99" || true)"
E2E_PREVIEW_HAS_COMMIT="$(cd "$E2E_REMOTE" && git log preview --oneline 2>/dev/null | grep -c "publish 2026-w99" || true)"
E2E_ISSUE_HAS_COMMIT="$(cd "$E2E_REMOTE" && git log "issue/2026-w99" --oneline 2>/dev/null | grep -c "publish 2026-w99" || true)"
check "the commit reached preview" "$E2E_PREVIEW_HAS_COMMIT" "1"
check "the commit reached the issue branch" "$E2E_ISSUE_HAS_COMMIT" "1"
check "the commit reached main (PREVIEW_MATCHES_MAIN was true)" "$E2E_MAIN_HAS_COMMIT" "1"

# Now the fatal-promote case (point J): a second issue, with
# PREVIEW_MATCHES_MAIN=false — preview and the issue branch should still
# take the push, but main must NOT move, and the phase must fail.
(
  cd "$E2E_CLONE/repo" || exit 1
  git fetch -q origin
  git checkout -q main
  git reset -q --hard origin/main
  git checkout -q preview
  git reset -q --hard origin/preview
  git checkout -q -b issue/2026-w98
  echo "signed again" > web/signed2.txt
  git add -A
  git commit -qm "feat(issue): publish 2026-w98"
)

(
  cd "$E2E_CLONE/repo" || exit 1
  REMOTE="origin"
  WEB_DIR="web"
  DRY_RUN="0"
  GH_AVAILABLE="false"
  GH_TOKEN="not-checked-by-a-local-remote"
  PR_NUMBER=""
  PREVIEW_MATCHES_MAIN="false"
  posture_note=""
  ISSUE_ID="2026-w98"
  HEAD_BRANCH="issue/2026-w98"

  step6_push_preview && step7_push_issue_branch && step8_promote
)
E2E_RC2=$?

check "the not-promoted case fails the whole run (point J)" "$E2E_RC2" "1"
E2E_MAIN_HAS_W98="$(cd "$E2E_REMOTE" && git log main --oneline 2>/dev/null | grep -c "publish 2026-w98" || true)"
E2E_PREVIEW_HAS_W98="$(cd "$E2E_REMOTE" && git log preview --oneline 2>/dev/null | grep -c "publish 2026-w98" || true)"
check "main did NOT move when preview did not already match it" "$E2E_MAIN_HAS_W98" "0"
check "preview still took the push (it is separate from the main guard)" "$E2E_PREVIEW_HAS_W98" "1"

rm -rf "$E2E_REMOTE" "$E2E_CLONE"

echo ""
if [ "$FAILURES" -eq 0 ]; then
  echo "All checks passed."
  exit 0
else
  echo "$FAILURES check(s) failed."
  exit 1
fi
