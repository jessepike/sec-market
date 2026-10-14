#!/bin/bash
#
# Auto-publish path for data-only collector branches (autonomy-coverage-plan.md
# §5 step 4, SEC-MARKET-AUTO-001). A collector workflow (edgar-refresh,
# the twice-weekly model runner) checks out `preview`, writes data files
# only, commits them to a short-lived branch `data/<runner>-<timestamp>`,
# and calls this script from that same checkout. No human approves a data
# publish; the checks below are the only gate (D-76).
#
# What this refuses to ever do, no matter what:
#   - publish a path outside the fixed data allowlist (a code or layout
#     change never reaches production through this script, D-76 / AGENTS.md)
#   - move `main` while `preview` carries any unreviewed site change outside
#     that allowlist
#   - force-push anything, to any branch
#
# Order of operations, and why:
#   1. the file allowlist is checked first, against everything, before a
#      single npm command runs — a code change on the branch is refused
#      before it can even be built or tested.
#   2. whether `main` already matches `preview` outside the allowlist is
#      captured now, once, against the refs as they stood before this run
#      touched anything (mirrors publish-issue.sh's production-guard
#      snapshot, same reason: preview moves under this script's own pushes
#      later, so the check has to happen before that).
#   3. the gate set runs (npm ci, test:data, build) against the branch's own
#      content — regardless of whether main and preview already match,
#      because untested data must never land on preview either.
#   4. only then does the script decide what to push, from the two facts
#      gathered above:
#        gates failed                -> nothing from this branch publishes;
#                                        a runStatus-only commit marks the
#                                        run incomplete, landing on preview
#                                        always and on main too if main
#                                        already matched preview.
#        gates passed, main matched  -> the data lands on preview, then
#                                        main is fast-forwarded to it.
#        gates passed, main differed -> the data lands on preview only,
#                                        followed by a runStatus-only commit
#                                        explaining why main did not move.
#
# This script assumes the invariant the rest of the project already relies
# on: `main` is always a fast-forward ancestor of `preview` (AGENTS.md,
# "Production deploy"). It never force-pushes, so if that invariant is ever
# broken by something outside this script, the `main` push below fails
# loudly rather than overwriting anything.
#
# Known simplification, recorded rather than solved here: unlike
# scripts/publish-issue.sh, this script does not split into a token-less
# guard/build phase and a separate token-bearing release phase. The
# workflows that call it (docs/active/auto/step4/workflows/*.yml.txt) run
# collector and publisher in one job, so a write-scoped token is present in
# the job's environment throughout, including while `npm ci`/`npm run build`
# execute. The allowlist guard below still stops a branch from carrying an
# unexpected file, but it does not isolate the token from whatever those npm
# scripts pull in. Same open door SEC-051 already names for the weekly
# job's deploy key; worth closing for both jobs together, not solved here.
#
# Required environment:
#   RUNNER   short identifier for the collector that produced this branch,
#            e.g. "edgar" or "collect" — used in commit messages, the
#            collectState.json collectorRun.failedSources entry (which
#            runStatus.ts derives its failedSources from), and the receipt.
#   BRANCH   the short-lived branch this was invoked from, e.g.
#            data/edgar-2026-09-26T13-00-11Z. Must match data/*. The script
#            assumes it is already checked out (HEAD) with full history, one
#            or more commits ahead of $REMOTE/preview, and that all of it is
#            already pushed to $REMOTE (the calling workflow's job).
#
# Optional environment:
#   REMOTE                git remote name (default: origin)
#   WEB_DIR                the web app's directory (default: web)
#   AUTHOR_NAME            commit author for both the data merge (when it is
#                          a merge commit, not a fast-forward) and the
#                          runStatus-only commit (default: Security Market
#                          Pulse bot, matching the existing edgar-refresh
#                          draft — never "Jesse Pike"; these commits are not
#                          his signature)
#   AUTHOR_EMAIL           default: jesse@keatingpike.com (Vercel refuses
#                          any other)
#   GH_TOKEN               required outside DRY_RUN. Used only to
#                          authenticate an explicit, per-push header (never
#                          written to git config, never echoed) — see
#                          authed_push, copied from publish-issue.sh.
#   DRY_RUN                1 disables every push. Everything else — the
#                          allowlist check, the drift snapshot, and the gate
#                          set — still runs. (default: 0)
#   FORCE_MAIN_MATCHES_PREVIEW  test seam only: "true"/"false" skips the
#                          real git-diff snapshot. Never set this for a real
#                          publish. (default: unset — computed for real)
#   GITHUB_STEP_SUMMARY    when set (GitHub Actions sets this itself), the
#                          JSON receipt is appended there inside a fenced
#                          code block. Otherwise the receipt is printed to
#                          stdout. (default: unset)
#
# Exit code: 0 whenever the run completed its own decision, including every
# "did not publish" outcome that is not itself a bug — an allowlist
# violation, a gate failure, or unreviewed site work blocking main. Those
# are ordinary outcomes of an automatic run and the plan says not to page
# for them (autonomy-coverage-plan.md §5, "Publishing"). Non-zero means the
# script could not even reach a decision: bad arguments, a push that was
# rejected and could not be resolved, or a git operation that failed
# outright.

set -uo pipefail

REMOTE="${REMOTE:-origin}"
WEB_DIR="${WEB_DIR:-web}"
AUTHOR_NAME="${AUTHOR_NAME:-Security Market Pulse bot}"
AUTHOR_EMAIL="${AUTHOR_EMAIL:-jesse@keatingpike.com}"
RUNNER="${RUNNER:-}"
BRANCH="${BRANCH:-}"
GH_TOKEN="${GH_TOKEN:-}"
DRY_RUN="${DRY_RUN:-0}"
FORCE_MAIN_MATCHES_PREVIEW="${FORCE_MAIN_MATCHES_PREVIEW:-}"

# The one place the five allowed paths are named (autonomy-coverage-plan.md
# §5 step 4a). Widening this needs the owner's word, same as
# is_allowed_issue_branch_path in publish-issue.sh.
#
# AUTO-001 fix pass 2, item 4: web/src/data/runStatus.ts dropped out of this
# list. It used to be a hand-set data file each writer patched directly; it
# is now a derived module computed from generated/edgarFacts.json and
# generated/collectState.json (both still covered by the generated/* line
# below), so a change to runStatus.ts itself is a code change again and goes
# through ordinary review rather than the autonomous data-only publish path.
is_allowed_data_path() {
  local path="$1" web_dir="$2"
  case "$path" in
    "$web_dir"/src/data/generated/*) return 0 ;;
    "$web_dir/src/data/tracker/events.ts") return 0 ;;
    "$web_dir/src/data/tracker/suppliers.ts") return 0 ;;
    "$web_dir/src/data/evidence.ts") return 0 ;;
    *) return 1 ;;
  esac
}

# Pathspecs for the main/preview drift snapshot. Only paths that change what
# production serves or how it is published are compared: the site ($web_dir),
# the workflows (.github/) and these scripts (scripts/), each minus the data
# allowlist. Record-keeping under docs/ and the root markdown files is not
# compared, so an ordinary docs commit on preview does not stop facts from
# publishing; it simply rides along on the next fast-forward (AUTO-001, D-79).
data_allowlist_exclude() {
  local web_dir="$1"
  printf '%s\n' \
    ":(exclude)$web_dir/src/data/generated/**" \
    ":(exclude)$web_dir/src/data/tracker/events.ts" \
    ":(exclude)$web_dir/src/data/tracker/suppliers.ts" \
    ":(exclude)$web_dir/src/data/evidence.ts"
}

# True when `$remote/main` and `$remote/preview` are identical outside the
# data allowlist. Both refs must already be fetched.
main_matches_preview() {
  local remote="$1" web_dir="$2"
  local exclude=()
  while IFS= read -r line; do exclude+=("$line"); done < <(data_allowlist_exclude "$web_dir")
  git diff --quiet "$remote/main" "$remote/preview" -- "$web_dir" .github scripts "${exclude[@]}"
}

# Pushes with an explicit, per-invocation auth header rather than a stored
# credential — copied from scripts/publish-issue.sh's authed_push, same
# reasoning: nothing but this one command needs push rights, and the header
# is never written to git config or echoed.
authed_push() {
  local refspec="$1"
  local basic
  basic="$(printf 'x-access-token:%s' "$GH_TOKEN" | base64 | tr -d '\n')"
  git -c "http.extraheader=AUTHORIZATION: basic $basic" -c core.hooksPath=/dev/null push "$REMOTE" "$refspec"
}

# The `main` push alone goes through the repo's own pre-push hook
# (.githooks/pre-push, PROMOTE=1) rather than neutralizing hooks the way
# authed_push does for preview — belt and suspenders on the one branch a
# force-push or a wrong-ref push would actually reach production. The hook
# only fires on refs/heads/main, so this has no effect on the preview push
# above. Installing it here (rather than assuming the runner already has it)
# means the check is live in CI too, not only on a human's clone.
authed_push_main() {
  local refspec="$1"
  if [ -f .githooks/install ] || [ -x .githooks/install ]; then
    ./.githooks/install >/dev/null 2>&1 || true
  fi
  local basic
  basic="$(printf 'x-access-token:%s' "$GH_TOKEN" | base64 | tr -d '\n')"
  PROMOTE=1 git -c "http.extraheader=AUTHORIZATION: basic $basic" push "$REMOTE" "$refspec"
}

log() { printf '%s\n' "$*" >&2; }

validate_common() {
  if [ -z "$RUNNER" ]; then
    echo "auto-publish.sh: RUNNER is required (e.g. edgar, collect)" >&2
    exit 1
  fi
  if [ -z "$BRANCH" ]; then
    echo "auto-publish.sh: BRANCH is required (e.g. data/edgar-2026-09-26T13-00-11Z)" >&2
    exit 1
  fi
  case "$BRANCH" in
    data/*) : ;;
    *)
      echo "auto-publish.sh: BRANCH \"$BRANCH\" does not match data/*" >&2
      exit 1
      ;;
  esac
  if [ ! -f "$WEB_DIR/package.json" ]; then
    echo "auto-publish.sh: no $WEB_DIR/package.json here — run this from the repository root" >&2
    exit 1
  fi
  if [ "$DRY_RUN" != "1" ] && [ -z "$GH_TOKEN" ]; then
    echo "auto-publish.sh: GH_TOKEN is required outside DRY_RUN" >&2
    exit 1
  fi
}

# --- Receipt -----------------------------------------------------------
# Machine-readable JSON, written to $GITHUB_STEP_SUMMARY (or stdout, for a
# local/manual run) — always, on every exit path, success or refusal alike.
RECEIPT_GATES_JSON="[]"

write_receipt() {
  local published="$1" published_to="$2" reason="$3"
  local changed_json
  changed_json="$(printf '%s\n' "${CHANGED_FILES_ARR[@]:-}" | jq -R . | jq -s 'map(select(length > 0))')"
  local json
  json="$(jq -n \
    --arg runner "$RUNNER" \
    --arg branch "$BRANCH" \
    --argjson changedPaths "$changed_json" \
    --argjson gates "$RECEIPT_GATES_JSON" \
    --argjson published "$published" \
    --arg publishedTo "$published_to" \
    --arg reason "$reason" \
    --arg at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{runner: $runner, branch: $branch, changedPaths: $changedPaths, gates: $gates, published: $published, publishedTo: $publishedTo, reason: $reason, at: $at}')"
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
    {
      echo "### auto-publish receipt: $RUNNER"
      echo '```json'
      printf '%s\n' "$json"
      echo '```'
    } >> "$GITHUB_STEP_SUMMARY"
  else
    printf '%s\n' "$json"
  fi
}

# --- Gates ---------------------------------------------------------------
# Each gate is a name plus a command. Runs stop at the first failure —
# gate_failed_name/gate_failed_log are then used both for the runStatus
# commit and the receipt. Real npm calls; scripts/test-auto-publish.sh
# stubs `npm` as a shell function so the test harness never needs a real
# Node toolchain (same technique scripts/test-publish-issue.sh uses).
GATE_FAILED_NAME=""
GATE_FAILED_LOG=""

run_gates() {
  local gates_json="[]"
  local name cmd_log rc
  local gate_names=("npm ci" "npm run test:data" "npm run build")
  local gate_cmds=("npm_ci_gate" "npm_test_data_gate" "npm_build_gate")
  local i
  for i in "${!gate_names[@]}"; do
    name="${gate_names[$i]}"
    log "=== GATE: $name ==="
    cmd_log="$("${gate_cmds[$i]}" 2>&1)"
    rc=$?
    printf '%s\n' "$cmd_log" >&2
    if [ "$rc" -eq 0 ]; then
      gates_json="$(printf '%s' "$gates_json" | jq --arg n "$name" '. + [{name: $n, passed: true}]')"
    else
      gates_json="$(printf '%s' "$gates_json" | jq --arg n "$name" '. + [{name: $n, passed: false}]')"
      GATE_FAILED_NAME="$name"
      GATE_FAILED_LOG="$(printf '%s' "$cmd_log" | tail -n 40)"
      RECEIPT_GATES_JSON="$gates_json"
      return 1
    fi
  done
  RECEIPT_GATES_JSON="$gates_json"
  return 0
}

npm_ci_gate() { ( cd "$WEB_DIR" && npm ci ); }
npm_test_data_gate() { ( cd "$WEB_DIR" && npm run test:data ); }
npm_build_gate() { ( cd "$WEB_DIR" && npm run build ); }

# --- Publishing the data branch to preview --------------------------------
# Fast-forward when preview has not moved since this branch was cut from it
# (the ordinary case — this job's own checkout just did that a few minutes
# earlier); falls back to one merge-and-retry if it has (another run landed
# in between), matching "fast-forward or a merge commit" in the design.
# Never force-pushes.
push_data_to_preview() {
  if [ "$DRY_RUN" = "1" ]; then
    log "DRY_RUN=1: not pushing $BRANCH to preview"
    return 0
  fi
  if authed_push "HEAD:refs/heads/preview"; then
    return 0
  fi
  log "push to preview was not a fast-forward; fetching and merging preview once, then retrying"
  git fetch "$REMOTE" preview || return 1
  git merge --no-edit "$REMOTE/preview" || return 1
  authed_push "HEAD:refs/heads/preview"
}

push_preview_to_main() {
  if [ "$DRY_RUN" = "1" ]; then
    log "DRY_RUN=1: not fast-forwarding main"
    return 0
  fi
  authed_push_main "HEAD:refs/heads/main"
}

# Builds and pushes a commit that touches nothing but
# generated/collectState.json's collectorRun receipt block, on top of
# $base_ref (a real ref, already fetched), marking the run incomplete.
# $promote_to_main: "true" pushes the same commit to main afterward (only
# ever called with "true" when main already matched preview before this
# run); "false" leaves main alone. Detaches HEAD to build it, since by the
# time this runs the script has already decided the data branch itself is
# not what's landing — the pushed data/<runner>-<ts> branch on GitHub is the
# durable record of what this run collected, untouched by this commit.
#
# AUTO-001 fix pass 2, item 4: this used to patch web/src/data/runStatus.ts
# directly (the same hand-set-file pattern the two blind rescores caught).
# runStatus.ts is now a derived module — see its header comment — so this
# writes the same collectorRun receipt scripts/collect.sh's step 6 writes,
# with restrictedTo left null (this path marks a gate failure or a held
# publish, not a scope-restricted collect run) and the model-owned
# lastSuccessfulCollectDate/lastRunAt fields preserved untouched.
push_incomplete_status() {
  local base_ref="$1" reason="$2" failed_source="$3" promote_to_main="$4"

  git checkout -q --detach "$base_ref" || return 1

  # Date-only precision (not full time-of-day), matching the previous
  # runStatus.ts patch's granularity: a same-day rerun with the same reason
  # and failed source produces the same bytes, so the diff-empty check
  # below still dedupes a same-day retry into one commit instead of many.
  local today_iso
  today_iso="$(date -u +%Y-%m-%d)T00:00:00Z"
  COLLECTSTATE_PATH="$WEB_DIR/src/data/generated/collectState.json" \
  CR_AT="$today_iso" \
  CR_REASON="$reason" \
  CR_FAILED_SOURCE="$failed_source" \
  node -e '
    const fs = require("fs");
    const path = process.env.COLLECTSTATE_PATH;
    const at = process.env.CR_AT;
    const reason = process.env.CR_REASON;
    const failedSource = process.env.CR_FAILED_SOURCE;

    let existing = { lastSuccessfulCollectDate: null, lastRunAt: null };
    if (fs.existsSync(path)) {
      try {
        const parsed = JSON.parse(fs.readFileSync(path, "utf8"));
        if (parsed && typeof parsed === "object") {
          existing.lastSuccessfulCollectDate = parsed.lastSuccessfulCollectDate ?? null;
          existing.lastRunAt = parsed.lastRunAt ?? null;
        }
      } catch (e) {
        console.error("auto-publish.sh: existing collectState.json unreadable, starting fresh:", e.message);
      }
    }

    // Third fix pass, items 1-2: failedSources is now an array of
    // { supplierId, reason, detail } objects (web/src/data/runStatus.ts CollectFailure)
    // for a per-supplier news-read failure. A held or failed publish is not
    // about one particular supplier source, it is the gate or runner
    // (failedSource) that failed, so it stays out of failedSources
    // entirely and rides in the detail field instead. runStatus.ts catch-all
    // branch for collectorRun.state === "incomplete" with no per-supplier
    // failures renders that string directly.
    const next = {
      lastSuccessfulCollectDate: existing.lastSuccessfulCollectDate,
      lastRunAt: existing.lastRunAt,
      collectorRun: {
        at,
        state: "incomplete",
        detail: `${reason} (${failedSource})`,
        restrictedTo: null,
        failedSources: [],
      },
    };
    fs.writeFileSync(path, JSON.stringify(next, null, 2) + "\n");
  ' || return 1

  git add "$WEB_DIR/src/data/generated/collectState.json"
  if git diff --cached --quiet; then
    log "collectState.json already reflects this incomplete run; nothing to commit"
    return 0
  fi
  git commit -m "data(runstatus): mark incomplete — $reason" -m "runner: $RUNNER, branch: $BRANCH" || return 1

  if [ "$DRY_RUN" = "1" ]; then
    log "DRY_RUN=1: not pushing the incomplete-status commit"
    return 0
  fi
  authed_push "HEAD:refs/heads/preview" || return 1
  if [ "$promote_to_main" = "true" ]; then
    authed_push_main "HEAD:refs/heads/main" || return 1
  fi
  return 0
}

main() {
  validate_common

  git config user.name "$AUTHOR_NAME"
  git config user.email "$AUTHOR_EMAIL"

  git fetch "$REMOTE" main preview >/dev/null 2>&1 || {
    echo "auto-publish.sh: could not fetch $REMOTE main/preview" >&2
    exit 1
  }

  mapfile -t CHANGED_FILES_ARR < <(git diff --name-only "$REMOTE/preview...HEAD" 2>&1)

  if [ "${#CHANGED_FILES_ARR[@]}" -eq 0 ] || [ -z "${CHANGED_FILES_ARR[0]:-}" ]; then
    log "no changed files between $REMOTE/preview and $BRANCH; nothing to publish"
    write_receipt false "none" "no data changes on $BRANCH"
    exit 0
  fi

  local violation=""
  local f
  for f in "${CHANGED_FILES_ARR[@]}"; do
    [ -z "$f" ] && continue
    if ! is_allowed_data_path "$f" "$WEB_DIR"; then
      violation="${violation}${f}"$'\n'
    fi
  done
  if [ -n "$violation" ]; then
    log "auto-publish.sh: refusing — $BRANCH touches file(s) outside the data allowlist:"
    printf '%s' "$violation" >&2
    write_receipt false "none" "touches file(s) outside the data allowlist: $(printf '%s' "$violation" | tr '\n' ' ')"
    exit 1
  fi
  log "file allowlist guard: only allowed data paths changed on $BRANCH"

  local main_matched="false"
  if [ -n "$FORCE_MAIN_MATCHES_PREVIEW" ]; then
    main_matched="$FORCE_MAIN_MATCHES_PREVIEW"
    log "FORCE_MAIN_MATCHES_PREVIEW set — using \"$main_matched\" instead of computing it (test seam only)"
  elif main_matches_preview "$REMOTE" "$WEB_DIR"; then
    main_matched="true"
  fi
  log "main matches preview (excluding the data allowlist): $main_matched"

  if ! run_gates; then
    log "auto-publish.sh: gate \"$GATE_FAILED_NAME\" failed; nothing from $BRANCH publishes"
    write_receipt false "none" "refresh/build gate failed; published snapshot and complete-refresh date retained: $GATE_FAILED_NAME"
    exit 2
  fi
  log "all gates passed"

  if [ "$main_matched" != "true" ]; then
    log "preview carries unreviewed site work outside the data allowlist; landing data on preview only"
    if ! push_data_to_preview; then
      write_receipt false "none" "gates passed but the push of $BRANCH to preview failed"
      exit 1
    fi
    # HEAD, not $REMOTE/preview: push_data_to_preview just pushed HEAD there
    # (fast-forward or the one merge retry), so the local ref cached from the
    # fetch at the top of main() is now stale — HEAD is the accurate base.
    if push_incomplete_status "HEAD" "site changes waiting for review" "site changes waiting for review" "false"; then
      write_receipt false "preview" "data landed on preview; main did not move because preview carries unreviewed site changes outside the data allowlist"
      exit 0
    else
      write_receipt true "preview" "data landed on preview (the follow-up incomplete-status commit failed to push; see the job log)"
      exit 0
    fi
  fi

  log "gates passed and main already matches preview; publishing to production"
  if ! push_data_to_preview; then
    write_receipt false "none" "gates passed but the push of $BRANCH to preview failed"
    exit 1
  fi
  if ! push_preview_to_main; then
    write_receipt false "preview" "data landed on preview; the fast-forward of main failed (see the job log) — retry will pick it up on the next run"
    exit 1
  fi
  write_receipt true "preview+main" "gates passed, main matched preview, data published"
  exit 0
}

# Only run main when executed directly — sourcing this file (as
# scripts/test-auto-publish.sh does) must define the guard/step functions
# above without validating env vars or touching git.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
