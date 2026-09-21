#!/bin/bash
#
# Unit-level tests for the guard logic in scripts/publish-issue.sh, run
# without a repo, a network, or npm — because publish-issue.sh's `main` only
# runs when the file is executed directly (see its last few lines), sourcing
# it here just defines the guard functions and step functions.
#
# Run: bash scripts/test-publish-issue.sh
# Exit: 0 if every assertion passes, 1 (with a FAIL line) otherwise.
#
# Added for the coordinator's review of SEC-MARKET-PUBLISH-001 build 1
# (2026-09-21), specifically to prove the NO_PROMOTE subshell bug is fixed:
# step7_promote used to set a variable inside a step function, which
# run_step forks into a subshell (it runs on the left of a pipe), so the
# assignment never reached step8_live_check. The fix reads a variable set in
# the parent shell (PREVIEW_MATCHES_MAIN) before any step runs, and this
# file's `not-promoted path skips the live check` test is the regression
# guard for that specific bug.

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
  "web/src/data/prints.ts"; do
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
echo "--- step8_live_check: the not-promoted path skips the live check ---"
# Regression test for the NO_PROMOTE subshell bug: PREVIEW_MATCHES_MAIN is a
# parent-shell variable read by step8_live_check, never one a step function
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
output="$(step8_live_check 2>&1)"
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
echo "--- step8_live_check: DRY_RUN always skips regardless of PREVIEW_MATCHES_MAIN ---"
DRY_RUN="1"
PREVIEW_MATCHES_MAIN="true"
STEP_LOG="$(mktemp)"
output="$(step8_live_check 2>&1)"
rc=$?
rm -f "$STEP_LOG"
check "DRY_RUN path returns success" "$rc" "0"
check_contains "DRY_RUN path says it is not polling" "$output" "DRY_RUN=1: not polling the live site"

echo ""
if [ "$FAILURES" -eq 0 ]; then
  echo "All checks passed."
  exit 0
else
  echo "$FAILURES check(s) failed."
  exit 1
fi
