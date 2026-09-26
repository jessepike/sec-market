#!/bin/bash
#
# Tests for scripts/auto-publish.sh, in the style of
# scripts/test-publish-issue.sh: sourcing the script only defines its
# functions (main() never runs unless the file is executed directly — see
# its last few lines), so this stays a pure git/bash test with no network
# and, deliberately, no real Node — `npm` and `node` are stubbed as shell
# functions exactly where the script calls them, the same technique
# test-publish-issue.sh uses for step2_sign. That keeps this harness
# runnable on the plain host (git and bash only) per the build instructions
# for SEC-MARKET-AUTO-001 step 4, without needing a real npm install or a
# Node toolchain on the host.
#
# Run: bash scripts/test-auto-publish.sh
# Exit: 0 if every assertion passes, 1 (with a FAIL line) otherwise.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./auto-publish.sh
source "$SCRIPT_DIR/auto-publish.sh"

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

check_not_contains() {
  local description="$1" haystack="$2" needle="$3"
  if printf '%s' "$haystack" | grep -qF "$needle"; then
    echo "FAIL: $description — did not expect to find [$needle]"
    FAILURES=$((FAILURES + 1))
  else
    echo "PASS: $description"
  fi
}

echo "--- is_allowed_data_path (file allowlist guard) ---"
for allowed in \
  "web/src/data/generated/edgarFacts.json" \
  "web/src/data/generated/collectState.json" \
  "web/src/data/generated/nested/deeper.json" \
  "web/src/data/tracker/events.ts" \
  "web/src/data/tracker/suppliers.ts" \
  "web/src/data/evidence.ts"; do
  if is_allowed_data_path "$allowed" "web"; then
    echo "PASS: $allowed is allowed"
  else
    echo "FAIL: $allowed should be allowed"; FAILURES=$((FAILURES + 1))
  fi
done
# AUTO-001 fix pass 2, item 4: web/src/data/runStatus.ts is a derived module
# now (computed from the two generated/* files above), not a hand-set data
# file, so it dropped out of the allowlist — a change to it is a code
# change again and must NOT qualify for the autonomous data-only path.
for disallowed in \
  "web/src/data/prints.ts" \
  "web/src/data/domains.ts" \
  "web/src/data/tracker/index.ts" \
  "web/src/data/runStatus.ts" \
  "web/scripts/edgar-refresh.ts" \
  "web/package.json" \
  ".github/workflows/edgar-refresh.yml" \
  "scripts/auto-publish.sh" \
  "AGENTS.md"; do
  if is_allowed_data_path "$disallowed" "web"; then
    echo "FAIL: $disallowed should NOT be allowed"; FAILURES=$((FAILURES + 1))
  else
    echo "PASS: $disallowed is refused"
  fi
done

echo ""
echo "--- main_matches_preview (drift guard over site, workflows and scripts) ---"
MMP_REPO="$(mktemp -d)"
(
  cd "$MMP_REPO" || exit 1
  git init -q .
  git config user.email test@example.com
  git config user.name "Test"
  mkdir -p docs web/src/data/generated web/src/data/tracker scripts
  echo "one" > web/src/app.ts
  echo "one" > web/src/data/generated/edgarFacts.json
  echo "one" > web/src/data/tracker/events.ts
  echo "one" > web/src/data/evidence.ts
  echo "one" > docs/notes.md
  echo "one" > status.md
  git add -A
  git commit -qm "base"
  git branch "origin/main"
  git branch "origin/preview"
)
mmp_matches() { ( cd "$MMP_REPO" && main_matches_preview "origin" "web" ) }

if mmp_matches; then
  echo "PASS: identical branches read as matching"
else
  echo "FAIL: identical branches should read as matching"; FAILURES=$((FAILURES + 1))
fi

( cd "$MMP_REPO" && git checkout -q "origin/preview" && echo "two" > web/src/data/generated/edgarFacts.json && echo "two" > web/src/data/tracker/events.ts && echo "two" > web/src/data/evidence.ts && git add -A && git commit -qm "data only" )
if mmp_matches; then
  echo "PASS: an allowlist-only difference is excluded (still matching)"
else
  echo "FAIL: an allowlist-only difference should still read as matching"; FAILURES=$((FAILURES + 1))
fi

( cd "$MMP_REPO" && echo "two" > docs/notes.md && git add -A && git commit -qm "docs only" )
if mmp_matches; then
  echo "PASS: a docs/-only difference does not block publishing (D-79)"
else
  echo "FAIL: a docs/-only difference should not block publishing (D-79)"
  FAILURES=$((FAILURES + 1))
fi

( cd "$MMP_REPO" && git checkout -q "origin/main" && echo "two" > web/src/app.ts && git add -A && git commit -qm "site code" )
if mmp_matches; then
  echo "FAIL: a web/ code difference should NOT be excluded"
  FAILURES=$((FAILURES + 1))
else
  echo "PASS: a web/ code difference is caught"
fi

rm -rf "$MMP_REPO"

# --- End-to-end scenarios, against a real local bare remote --------------
# `npm` and `node` are stubbed as shell functions for the whole of this
# section: `npm` records what it was called with and exits 0 or 1 depending
# on $E2E_NPM_FAIL_ON; `node` — the one real dependency of
# push_incomplete_status — is stubbed to perform the same collectState.json
# receipt write in plain bash (AUTO-001 fix pass 2, item 4: this used to
# patch web/src/data/runStatus.ts directly; runStatus.ts is a derived module
# now, so the real script writes generated/collectState.json's collectorRun
# block instead, reading the exact env vars — COLLECTSTATE_PATH, CR_AT,
# CR_REASON, CR_FAILED_SOURCE — auto-publish.sh sets before calling it, so
# the git plumbing around it is exercised for real without a Node toolchain.
npm() {
  echo "$*" >> "$E2E_NPM_CALLS"
  case "$1 ${2:-}" in
    "run test:data") [ "$E2E_NPM_FAIL_ON" = "test:data" ] && { echo "npm stub: test:data failed"; return 1; } ;;
    "run build") [ "$E2E_NPM_FAIL_ON" = "build" ] && { echo "npm stub: build failed"; return 1; } ;;
    "ci") [ "$E2E_NPM_FAIL_ON" = "ci" ] && { echo "npm stub: ci failed"; return 1; } ;;
  esac
  return 0
}
export -f npm

node() {
  # Only ever called here as: node -e '<script>' — ignores the script text
  # entirely and performs the same collectState.json receipt write
  # push_incomplete_status's real node call performs, preserving the
  # model-owned lastSuccessfulCollectDate/lastRunAt fields with grep/sed
  # instead of real JSON.parse/stringify.
  local last_successful="null" last_run="null" v
  if [ -f "$COLLECTSTATE_PATH" ]; then
    v="$(grep -o '"lastSuccessfulCollectDate": *[^,]*' "$COLLECTSTATE_PATH" | sed 's/.*: *//')"
    [ -n "$v" ] && last_successful="$v"
    v="$(grep -o '"lastRunAt": *[^,]*' "$COLLECTSTATE_PATH" | sed 's/.*: *//')"
    [ -n "$v" ] && last_run="$v"
  fi
  # Third fix pass, items 1-2: failedSources is now an array of
  # { supplierId, reason, detail } objects, and a held/failed publish isn't
  # a per-supplier failure — the real node call folds CR_FAILED_SOURCE (the
  # runner name) into `detail` instead and leaves failedSources empty; this
  # mock matches that.
  cat > "$COLLECTSTATE_PATH" <<EOF
{
  "lastSuccessfulCollectDate": ${last_successful},
  "lastRunAt": ${last_run},
  "collectorRun": {
    "at": "${CR_AT}",
    "state": "incomplete",
    "detail": "${CR_REASON} (${CR_FAILED_SOURCE})",
    "restrictedTo": null,
    "failedSources": []
  }
}
EOF
}
export -f node

make_e2e_remote() {
  local remote_dir="$1"
  git init -q --bare "$remote_dir"
  local seed
  seed="$(mktemp -d)"
  (
    cd "$seed" || exit 1
    git init -q .
    git config user.email test@example.com
    git config user.name "Test"
    mkdir -p web/src/data/generated web/src/data/tracker
    echo '{}' > web/package.json
    # AUTO-001 fix pass 2, item 4: runStatus.ts is a derived module (computed
    # from generated/edgarFacts.json + generated/collectState.json — see its
    # header comment); this fixture seeds it as a plausible checked-in file,
    # not something this bash-only harness ever executes.
    cat > web/src/data/runStatus.ts <<'EOF'
export type RunState = 'updated' | 'no-change' | 'incomplete'

export interface RunStatus {
  lastChecked: string
  state: RunState
  failedSources: string[]
  detail?: string
}

// Derived at import time from generated/edgarFacts.json and
// generated/collectState.json — see this file's real counterpart in
// web/src/data/runStatus.ts for the actual derivation logic.
EOF
    cat > web/src/data/generated/collectState.json <<'EOF'
{
  "lastSuccessfulCollectDate": "2026-09-01",
  "lastRunAt": "2026-09-01T00:00:00Z",
  "collectorRun": {
    "at": "2026-09-01T00:00:00Z",
    "state": "updated",
    "detail": "run completed; 0 data file(s) changed",
    "restrictedTo": null,
    "failedSources": []
  }
}
EOF
    echo '{"suppliers":[]}' > web/src/data/generated/edgarFacts.json
    echo "// events" > web/src/data/tracker/events.ts
    echo "base" > README.md
    git add -A
    git commit -qm "base"
    git branch -m main
    git remote add origin "$remote_dir"
    git push -q origin main
    git checkout -q -b preview
    git push -q origin preview
  )
  rm -rf "$seed"
}

echo ""
echo "--- end to end: allowlist violation refuses before any push ---"
E2E1_REMOTE="$(mktemp -d)"; make_e2e_remote "$E2E1_REMOTE"
E2E1_CLONE="$(mktemp -d)"
git clone -q "$E2E1_REMOTE" "$E2E1_CLONE/repo"
(
  cd "$E2E1_CLONE/repo" || exit 1
  git config user.email test@example.com
  git config user.name "Test"
  git checkout -q -b data/test-1
  echo "changed" > web/src/data/prints.ts
  git add -A
  git commit -qm "data(test): touches a disallowed path"
  git push -q origin data/test-1
)
E2E1_OUT="$(
  cd "$E2E1_CLONE/repo" || exit 1
  E2E_NPM_CALLS="$(mktemp)"; export E2E_NPM_CALLS
  E2E_NPM_FAIL_ON=""
  REMOTE=origin WEB_DIR=web RUNNER=test BRANCH=data/test-1 DRY_RUN=1 GH_TOKEN=x main
)"
E2E1_RC=$?
check "allowlist violation: exit 1" "$E2E1_RC" "1"
check_contains "allowlist violation: receipt names the disallowed path" "$E2E1_OUT" "prints.ts"
check_contains "allowlist violation: receipt says published false" "$E2E1_OUT" '"published": false'
rm -rf "$E2E1_REMOTE" "$E2E1_CLONE"

echo ""
echo "--- end to end: gates pass, main matches preview -> publishes to both ---"
E2E2_REMOTE="$(mktemp -d)"; make_e2e_remote "$E2E2_REMOTE"
E2E2_CLONE="$(mktemp -d)"
git clone -q "$E2E2_REMOTE" "$E2E2_CLONE/repo"
(
  cd "$E2E2_CLONE/repo" || exit 1
  git config user.email test@example.com
  git config user.name "Test"
  git checkout -q preview
  git checkout -q -b data/edgar-1
  echo '{"suppliers":["x"]}' > web/src/data/generated/edgarFacts.json
  git add -A
  git commit -qm "data(edgar): refresh"
  git push -q origin data/edgar-1
)
E2E2_OUT="$(
  cd "$E2E2_CLONE/repo" || exit 1
  E2E_NPM_CALLS="$(mktemp)"; export E2E_NPM_CALLS
  E2E_NPM_FAIL_ON=""
  REMOTE=origin WEB_DIR=web RUNNER=edgar BRANCH=data/edgar-1 DRY_RUN=0 GH_TOKEN=x main
)"
E2E2_RC=$?
check "success: exit 0" "$E2E2_RC" "0"
check_contains "success: receipt says published true" "$E2E2_OUT" '"published": true'
check_contains "success: receipt says preview+main" "$E2E2_OUT" "preview+main"
E2E2_MAIN_HAS_DATA="$(cd "$E2E2_REMOTE" && git show main:web/src/data/generated/edgarFacts.json | grep -c '"x"' || true)"
E2E2_PREVIEW_HAS_DATA="$(cd "$E2E2_REMOTE" && git show preview:web/src/data/generated/edgarFacts.json | grep -c '"x"' || true)"
check "success: main carries the new data" "$E2E2_MAIN_HAS_DATA" "1"
check "success: preview carries the new data" "$E2E2_PREVIEW_HAS_DATA" "1"
rm -rf "$E2E2_REMOTE" "$E2E2_CLONE"

echo ""
echo "--- end to end: main/preview drift -> data lands on preview only, main untouched ---"
E2E3_REMOTE="$(mktemp -d)"; make_e2e_remote "$E2E3_REMOTE"
E2E3_CLONE="$(mktemp -d)"
git clone -q "$E2E3_REMOTE" "$E2E3_CLONE/repo"
(
  cd "$E2E3_CLONE/repo" || exit 1
  git config user.email test@example.com
  git config user.name "Test"
  # An un-promoted site change on preview: outside the data allowlist.
  git checkout -q preview
  mkdir -p web/src
  echo "unreviewed" > web/src/unreviewed.ts
  git add -A
  git commit -qm "feat(web): unreviewed site change"
  git push -q origin preview
  git checkout -q -b data/edgar-2
  echo '{"suppliers":["y"]}' > web/src/data/generated/edgarFacts.json
  git add -A
  git commit -qm "data(edgar): refresh"
  git push -q origin data/edgar-2
)
E2E3_OUT="$(
  cd "$E2E3_CLONE/repo" || exit 1
  E2E_NPM_CALLS="$(mktemp)"; export E2E_NPM_CALLS
  E2E_NPM_FAIL_ON=""
  REMOTE=origin WEB_DIR=web RUNNER=edgar BRANCH=data/edgar-2 DRY_RUN=0 GH_TOKEN=x main
)"
E2E3_RC=$?
check "drift: exit 0 (an ordinary, non-broken outcome)" "$E2E3_RC" "0"
check_contains "drift: receipt says published false" "$E2E3_OUT" '"published": false'
check_contains "drift: reason names unreviewed site changes" "$E2E3_OUT" "site changes waiting for review"
E2E3_MAIN_HAS_DATA="$(cd "$E2E3_REMOTE" && git show main:web/src/data/generated/edgarFacts.json | grep -c '"y"' || true)"
E2E3_PREVIEW_HAS_DATA="$(cd "$E2E3_REMOTE" && git show preview:web/src/data/generated/edgarFacts.json | grep -c '"y"' || true)"
E2E3_PREVIEW_STATUS="$(cd "$E2E3_REMOTE" && git show preview:web/src/data/generated/collectState.json)"
check "drift: main did NOT get the new data" "$E2E3_MAIN_HAS_DATA" "0"
check "drift: preview DID get the new data" "$E2E3_PREVIEW_HAS_DATA" "1"
check_contains "drift: preview's collectState reads incomplete" "$E2E3_PREVIEW_STATUS" '"state": "incomplete"'
check_contains "drift: preview's collectState names the reason" "$E2E3_PREVIEW_STATUS" "site changes waiting for review"
rm -rf "$E2E3_REMOTE" "$E2E3_CLONE"

echo ""
echo "--- end to end: gate failure -> nothing from the branch publishes, incomplete status lands ---"
E2E4_REMOTE="$(mktemp -d)"; make_e2e_remote "$E2E4_REMOTE"
E2E4_CLONE="$(mktemp -d)"
git clone -q "$E2E4_REMOTE" "$E2E4_CLONE/repo"
(
  cd "$E2E4_CLONE/repo" || exit 1
  git config user.email test@example.com
  git config user.name "Test"
  git checkout -q preview
  git checkout -q -b data/edgar-3
  echo '{"suppliers":["z"]}' > web/src/data/generated/edgarFacts.json
  git add -A
  git commit -qm "data(edgar): refresh"
  git push -q origin data/edgar-3
)
E2E4_OUT="$(
  cd "$E2E4_CLONE/repo" || exit 1
  E2E_NPM_CALLS="$(mktemp)"; export E2E_NPM_CALLS
  E2E_NPM_FAIL_ON="build"
  REMOTE=origin WEB_DIR=web RUNNER=edgar BRANCH=data/edgar-3 DRY_RUN=0 GH_TOKEN=x main
)"
E2E4_RC=$?
check "gate failure: exit 0 (an ordinary, non-broken outcome)" "$E2E4_RC" "0"
check_contains "gate failure: receipt names the failed gate" "$E2E4_OUT" "npm run build"
E2E4_MAIN_HAS_DATA="$(cd "$E2E4_REMOTE" && git show main:web/src/data/generated/edgarFacts.json | grep -c '"z"' || true)"
E2E4_PREVIEW_HAS_DATA="$(cd "$E2E4_REMOTE" && git show preview:web/src/data/generated/edgarFacts.json | grep -c '"z"' || true)"
E2E4_MAIN_STATUS="$(cd "$E2E4_REMOTE" && git show main:web/src/data/generated/collectState.json)"
E2E4_PREVIEW_STATUS="$(cd "$E2E4_REMOTE" && git show preview:web/src/data/generated/collectState.json)"
check "gate failure: main did NOT get the failed data" "$E2E4_MAIN_HAS_DATA" "0"
check "gate failure: preview did NOT get the failed data either" "$E2E4_PREVIEW_HAS_DATA" "0"
check_contains "gate failure: main's collectState reads incomplete (main matched preview beforehand)" "$E2E4_MAIN_STATUS" '"state": "incomplete"'
check_contains "gate failure: preview's collectState reads incomplete" "$E2E4_PREVIEW_STATUS" '"state": "incomplete"'
check_contains "gate failure: detail names the runner" "$E2E4_PREVIEW_STATUS" "edgar"
rm -rf "$E2E4_REMOTE" "$E2E4_CLONE"

echo ""
if [ "$FAILURES" -eq 0 ]; then
  echo "All checks passed."
  exit 0
else
  echo "$FAILURES check(s) failed."
  exit 1
fi
