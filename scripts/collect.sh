#!/bin/bash
#
# Twice-weekly unstructured-facts collector (step 3 of
# docs/active/autonomy-coverage-plan.md, SEC-MARKET-AUTO-001, D-76/D-77).
# Everything SEC EDGAR's structured data cannot reach: funding, acquisitions,
# layoffs, restructuring, debt, ratings actions, going-concern language,
# executive changes, divestitures, shutdowns, and each public supplier's own
# headline metric. Hands the work to headless Claude Code under the owner's
# own subscription login (never an API key), with
# docs/active/auto/collect-brief.md as its full instruction.
#
# What this script does NOT do, deliberately (docs/active/auto/step3's own
# instructions): it never runs `git add`, `git commit`, or `git push`, and it
# never runs the build gates (npm run test:data / npm run build). It writes
# files only — the data files the model produces, plus this script's own
# deterministic write of the `collectorRun` receipt block in
# web/src/data/generated/collectState.json (web/src/data/runStatus.ts is a
# derived module now — see its header comment — and nothing writes it by
# hand) and a JSON receipt at .collect/receipt.json. The calling workflow
# (or, for a local test run, a person) stages, reviews, commits, and runs
# the gates; only then does scripts/auto-publish.sh decide whether any of
# it reaches production.
#
# Exit codes: 0 the run reached a decision (including "blocked-auth" or
# "incomplete" — those are honest outcomes, not script bugs); 1 something
# about the script itself failed (bad repo, bad model output the script
# could not parse).

set -uo pipefail

REPO="${SMP_REPO:-$(pwd)}"
WEB_DIR="${SMP_WEB_DIR:-web}"
MODEL="${SMP_MODEL:-claude-sonnet-5}"
BRIEF_PATH="${SMP_BRIEF_PATH:-docs/active/auto/collect-brief.md}"
TIMEOUT_SECS="${SMP_TIMEOUT:-5400}"
SCRATCH_DIR="${SMP_SCRATCH_DIR:-.collect}"

# Restrict this run to a comma-separated list of supplier ids from
# web/src/data/tracker/suppliers.ts, e.g. "optiv,snyk,cyera,rapid7,armis".
# Empty (the default) means every declared supplier. A restricted run never
# advances collectState.json's watermark (see the brief, §4) — a partial
# pass must never make the next full run skip suppliers nobody checked.
COLLECT_ONLY="${SMP_COLLECT_ONLY:-}"

# Override the computed since-date outright, e.g. for a backfill or a proof
# run against a known window. Must be YYYY-MM-DD.
COLLECT_SINCE_OVERRIDE="${SMP_COLLECT_SINCE:-}"

STAMP="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
mkdir -p "$SCRATCH_DIR"
RUN_LOG="$SCRATCH_DIR/run-$STAMP.log"
RECEIPT="$SCRATCH_DIR/receipt.json"
COLLECT_STATE_PATH="$WEB_DIR/src/data/generated/collectState.json"
PREVIOUS_SUCCESS="$(node -e 'const fs=require("fs");try{const d=JSON.parse(fs.readFileSync(process.argv[1],"utf8"));process.stdout.write(d.lastSuccessfulCollectDate||"")}catch{}' "$COLLECT_STATE_PATH")"

log() { printf '%s  %s\n' "$(date -u +%H:%M:%SZ)" "$*" | tee -a "$RUN_LOG"; }

cd "$REPO" || { echo "collect.sh: cannot cd to $REPO" >&2; exit 1; }
if [ ! -f "$WEB_DIR/package.json" ]; then
  echo "collect.sh: no $WEB_DIR/package.json here — run from the repository root" >&2
  exit 1
fi
if [ ! -f "$BRIEF_PATH" ]; then
  echo "collect.sh: brief not found at $BRIEF_PATH" >&2
  exit 1
fi

# JSON string-escape: backslash, quote, flatten newlines/tabs to spaces —
# same approach scripts/gather.sh's receipt() uses.
json_escape() {
  node -e 'process.stdout.write(JSON.stringify(process.argv[1]))' "$1"
}

# JSON array of strings from newline-separated stdin, or "[]" for empty
# input. Avoids depending on jq, which is not guaranteed present everywhere
# this script runs.
json_string_array() {
  local first=1 line out="["
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    if [ "$first" -eq 1 ]; then first=0; else out="${out},"; fi
    out="${out}$(json_escape "$line")"
  done
  out="${out}]"
  printf '%s' "$out"
}

write_receipt() {
  local state="$1" since_date="$2" only="$3" changed_json="$4" failed_json="$5" detail="$6"
  cat > "$RECEIPT" <<JSON
{
  "stamp": "$STAMP",
  "host": "$(hostname)",
  "model": "$MODEL",
  "sinceDate": "$since_date",
  "collectOnly": $(json_escape "$only"),
  "state": "$state",
  "changedFiles": $changed_json,
  "failedSources": $failed_json,
  "detail": $(json_escape "$detail"),
  "log": "$RUN_LOG"
}
JSON
  log "receipt: $RECEIPT  state=$state"
}

log "collect run $STAMP on $(hostname)"

# ---- 0. load the subscription token, if this host keeps one locally -------
# Same reasoning as scripts/gather.sh: launchd, a plain CI runner, or a
# non-interactive shell loads neither the shell profile nor a login
# environment, so a CLAUDE_CODE_OAUTH_TOKEN in ~/.env.local (mode 600, never
# committed) is otherwise invisible here. Never echo or log its value.
ENV_FILE="$HOME/.env.local"
if [ -r "$ENV_FILE" ]; then
  set -a; . "$ENV_FILE"; set +a
  log "loaded $ENV_FILE"
else
  log "no $ENV_FILE to load"
fi

# ---- 1. is this host logged in? --------------------------------------------
# One-token probe before the expensive run, exactly like gather.sh's. A dead
# subscription login returns 401 on the first call, and without this check
# the receipt would blame the collect for a problem that actually needs a
# person at a browser running `claude setup-token`.
AUTH_OUT="$(claude -p "Reply only OK. Do not use tools or read files." --model "$MODEL" --tools "" < /dev/null 2>&1)"
case "$AUTH_OUT" in
  *401*|*uthenticat*|*"access token"*)
    DETAIL="the Claude login on this host is not valid; collector credential requires owner setup. No source check performed."
    log "blocked-auth: $DETAIL"
    write_receipt "blocked-auth" "" "$COLLECT_ONLY" "[]" "[]" "$DETAIL"
    exit 1
    ;;
esac
log "auth probe ok"

# ---- 2. since-date ----------------------------------------------------------
# Portable across macOS (BSD date, on this host) and GitHub Actions ubuntu
# runners (GNU date, in the workflow) — the two places this script runs.
days_ago() {
  local n="$1"
  if date -u -d "-${n} days" +%Y-%m-%d >/dev/null 2>&1; then
    date -u -d "-${n} days" +%Y-%m-%d          # GNU date
  else
    date -u -v-"${n}"d +%Y-%m-%d               # BSD date
  fi
}

if [ -n "$COLLECT_SINCE_OVERRIDE" ]; then
  SINCE_DATE="$COLLECT_SINCE_OVERRIDE"
  log "since-date: $SINCE_DATE (SMP_COLLECT_SINCE override)"
elif [ -f "$COLLECT_STATE_PATH" ]; then
  SINCE_DATE="$(node -e "
    try {
      const s = require('./$COLLECT_STATE_PATH');
      if (s && typeof s.lastSuccessfulCollectDate === 'string') process.stdout.write(s.lastSuccessfulCollectDate);
    } catch (e) {}
  " 2>/dev/null)"
  if [ -z "$SINCE_DATE" ]; then
    SINCE_DATE="$(days_ago 30)"
    log "since-date: $SINCE_DATE (collectState.json unreadable; 30-day fallback)"
  else
    log "since-date: $SINCE_DATE (from $COLLECT_STATE_PATH)"
  fi
else
  SINCE_DATE="$(days_ago 30)"
  log "since-date: $SINCE_DATE (no $COLLECT_STATE_PATH yet; 30-day fallback)"
fi

TODAY="$(date -u +%Y-%m-%d)"
NOW_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ---- 3. prompt file ---------------------------------------------------------
# Written to a file first, not built inline in a command substitution — the
# same bash 3.2 lesson scripts/gather.sh already paid for (lessons.md,
# 2026-09-20): a here-document nested inside command substitution reads the
# apostrophes in the prose as opening quotes on bash 3.2 and never parses.
PROMPT_FILE="$SCRATCH_DIR/prompt-$STAMP.txt"

if [ -n "$COLLECT_ONLY" ]; then
  SCOPE_LINE="This run is RESTRICTED to these supplier ids only: $COLLECT_ONLY. Do not look at any other supplier. Because this is a restricted run, do NOT update web/src/data/generated/collectState.json — leave it exactly as you found it (per the brief §4)."
else
  SCOPE_LINE="This run covers every declared supplier in web/src/data/tracker/suppliers.ts. When you finish, update web/src/data/generated/collectState.json per the brief §4."
fi

cat > "$PROMPT_FILE" <<EOM
Read $BRIEF_PATH in this repository and carry it out in
full, now.

Since-date for newly appended events: $SINCE_DATE (events must be dated after this,
and on or before $TODAY). Verification of retained claims is not restricted
to that date window; follow the selected brief. $SCOPE_LINE

Follow every ground rule in section 0 of the brief. In particular: you do not
touch git at all, you do not touch web/src/data/runStatus.ts, you fetch with
curl so you hold the bytes, you hash everything you quote, only rungs 1
through 4 of the sourcing ladder may publish an event on their own, and you
never write a judgment word — state what the source said and stop. Leave
.collect/failed-sources.json, .collect/candidates.json, and
.collect/summary.txt behind, even when empty, per the brief §5.
EOM

PROMPT="$(cat "$PROMPT_FILE")"

# ---- 4. allowed tools -------------------------------------------------------
# Deliberately narrower than scripts/gather.sh's list: no git commands at
# all (this script owns git, not the model — see the header comment above
# and the brief's §0), and no npm (this script does not run gates either).
ALLOWED_TOOLS=(
  "Read"
  "Edit"
  "Write"
  "Glob"
  "Grep"
  "Bash(curl:*)"
  "Bash(shasum:*)"
  "Bash(sha256sum:*)"
  "Bash(pdftotext:*)"
  "Bash(strings:*)"
  "Bash(date:*)"
  "Bash(wc:*)"
  "Bash(jq:*)"
)

DISALLOWED_TOOLS=(
  "Bash(git:*)"
  "Bash(npm:*)"
)

log "invoking claude -p --model $MODEL (since=$SINCE_DATE, only=${COLLECT_ONLY:-all})"
CLAUDE_OUT="$SCRATCH_DIR/claude-$STAMP.txt"
RESUME_ARGS=()
if [ -n "${SMP_RESUME_SESSION:-}" ]; then
  RESUME_ARGS=(--resume "$SMP_RESUME_SESSION")
  PROMPT="Continue the interrupted full refresh in this same session. Read $BRIEF_PATH again. Preserve completed public-source research and any sourced data edits. ${SMP_RESUME_NOTE:-} Immediately persist receipts for every supplier already actually checked, then write .collect/supplier-checks.json after EACH remaining supplier so interruption never loses verified progress. Do not mark unchecked fields checked. Finish all 74 suppliers; no helpers, git, deployments or credential operations. Since-date $SINCE_DATE; through $TODAY. $PROMPT"
fi
# `timeout` is not on macOS by default; a background child plus a watchdog
# does the same job without adding a dependency (same shape as gather.sh).
(
  claude -p "$PROMPT" \
    "${RESUME_ARGS[@]}" \
    --model "$MODEL" \
    --permission-mode acceptEdits \
    --allowedTools "${ALLOWED_TOOLS[@]}" \
    --disallowedTools "${DISALLOWED_TOOLS[@]}" \
    > "$CLAUDE_OUT" 2>&1
) &
CLAUDE_PID=$!
( sleep "$TIMEOUT_SECS"; kill -0 "$CLAUDE_PID" 2>/dev/null && kill -TERM "$CLAUDE_PID" 2>/dev/null ) &
WATCHDOG=$!
wait "$CLAUDE_PID"; CLAUDE_RC=$?
kill -TERM "$WATCHDOG" 2>/dev/null
CLAUDE_LINES=$(wc -l < "$CLAUDE_OUT"); CLAUDE_LINES=${CLAUDE_LINES// /}
log "claude exited rc=$CLAUDE_RC, ${CLAUDE_LINES} lines of output"

# ---- 5. read what the model left behind ------------------------------------
FAILED_JSON="[]"
if [ -f "$SCRATCH_DIR/failed-sources.json" ]; then
  FAILED_JSON="$(cat "$SCRATCH_DIR/failed-sources.json")"
fi

DATA_PATHS=(
  "$WEB_DIR/src/data/tracker/events.ts"
  "$WEB_DIR/src/data/tracker/suppliers.ts"
  "$WEB_DIR/src/data/evidence.ts"
  "$COLLECT_STATE_PATH"
)
CHANGED_LIST=""
for p in "${DATA_PATHS[@]}"; do
  if [ -f "$p" ] && ! git diff --quiet -- "$p" 2>/dev/null; then
    CHANGED_LIST="${CHANGED_LIST}${p}"$'\n'
  fi
done
CHANGED_JSON="$(printf '%s' "$CHANGED_LIST" | json_string_array)"

# Failed-sources count, without depending on jq being present.
FAILED_COUNT="$(node -e 'const fs=require("fs");try{const a=JSON.parse(fs.readFileSync(process.argv[1],"utf8"));if(!Array.isArray(a))throw Error();process.stdout.write(String(a.length))}catch{process.stdout.write("1")}' "$SCRATCH_DIR/failed-sources.json" 2>/dev/null)"
FAILED_COUNT="${FAILED_COUNT:-0}"

if [ "$CLAUDE_RC" -ne 0 ]; then
  STATE="incomplete"
  # Third fix pass, items 1-2: no file path in `detail` — collectState.json
  # is a generated file nothing published points a reader at, and
  # runStatus.ts's own catch-all branch (collectorRun.state === 'incomplete'
  # with no per-supplier failures) renders this string close to verbatim.
  DETAIL="the collect run did not finish (claude exited $CLAUDE_RC)"
elif [ "$FAILED_COUNT" -gt 0 ]; then
  STATE="incomplete"
  DETAIL="$FAILED_COUNT source(s) failed to load"
elif [ -z "$CHANGED_LIST" ]; then
  STATE="no-change"
  DETAIL="run completed; nothing in coverage moved"
else
  STATE="updated"
  DETAIL="run completed; $(printf '%s' "$CHANGED_LIST" | grep -c .) data file(s) changed"
fi
log "outcome: state=$STATE  $DETAIL"

# ---- 6. write collectState.json's collectorRun block deterministically ----
# AUTO-001 fix pass 2, item 4: web/src/data/runStatus.ts is now a derived
# module (computed at import time from generated/edgarFacts.json and
# generated/collectState.json — see that file's own header comment) and is
# never hand-edited by anything again. This script's one deterministic write
# is this receipt block instead — same shape scripts/auto-publish.sh's
# push_incomplete_status writes for a held/blocked publish, so every writer
# of collectState.json touches it the same way. The model-owned
# `lastSuccessfulCollectDate`/`lastRunAt` fields (brief §4) are read and
# preserved exactly as the model left them, restricted run or not.
NOW_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
COLLECTSTATE_PATH="$COLLECT_STATE_PATH" \
CR_PREVIOUS_SUCCESS="$PREVIOUS_SUCCESS" \
CR_AT="$NOW_ISO" \
CR_STATE="$STATE" \
CR_DETAIL="$DETAIL" \
CR_ONLY="$COLLECT_ONLY" \
CR_FAILED_JSON="$FAILED_JSON" \
node -e '
  const fs = require("fs");
  const path = process.env.COLLECTSTATE_PATH;
  const at = process.env.CR_AT;
  const state = process.env.CR_STATE;
  const detail = process.env.CR_DETAIL;
  const only = process.env.CR_ONLY;
  let failed;
  try { failed = JSON.parse(process.env.CR_FAILED_JSON || "[]"); }
  catch (e) { failed = []; }
  if (!Array.isArray(failed)) failed = [];

  let existing = { lastSuccessfulCollectDate: null, lastRunAt: null };
  if (fs.existsSync(path)) {
    try {
      const parsed = JSON.parse(fs.readFileSync(path, "utf8"));
      if (parsed && typeof parsed === "object") {
        existing.lastSuccessfulCollectDate = parsed.lastSuccessfulCollectDate ?? null;
        existing.lastRunAt = parsed.lastRunAt ?? null;
      }
    } catch (e) {
      console.error("collect.sh: existing collectState.json unreadable, starting fresh:", e.message);
    }
  }

  const restrictedTo = only && only.trim() !== ""
    ? only.split(",").map((s) => s.trim()).filter(Boolean)
    : null;

  const next = {
    lastSuccessfulCollectDate: state === "incomplete" || restrictedTo !== null ? process.env.CR_PREVIOUS_SUCCESS || null : at.slice(0,10),
    lastRunAt: at,
    collectorRun: {
      at,
      state,
      detail,
      restrictedTo,
      failedSources: failed,
    },
  };
  fs.writeFileSync(path, JSON.stringify(next, null, 2) + "\n");
' || { log "failed to write $COLLECT_STATE_PATH"; write_receipt "$STATE" "$SINCE_DATE" "$COLLECT_ONLY" "$CHANGED_JSON" "$FAILED_JSON" "$DETAIL (and collectState.json receipt write failed)"; exit 1; }
log "wrote $COLLECT_STATE_PATH collectorRun: state=$STATE only=${COLLECT_ONLY:-none} failedSources=$FAILED_COUNT"

# ---- 7. receipt -------------------------------------------------------------
write_receipt "$STATE" "$SINCE_DATE" "$COLLECT_ONLY" "$CHANGED_JSON" "$FAILED_JSON" "$DETAIL"

exit 0
