#!/bin/bash
#
# Weekly gather runner.
#
# Runs on macbook2014 under launchd (com.securitymarketpulse.gather). Pulls the
# trunk, works out which issue is due, hands the job to Claude Code with
# docs/active/gather-brief.md as its instruction, and checks that a branch
# actually reached GitHub. A GitHub Action opens the pull request from that
# branch, so this host never needs a GitHub API token — it pushes over a
# read-write deploy key and nothing else.
#
# Every run writes a receipt to $LOG_DIR/receipts/<stamp>.json whether it
# succeeds or fails, because a run that failed silently and a week with no news
# must never look the same.
#
# Exit codes: 0 work done or nothing due; 1 the gather failed.

set -uo pipefail

REPO="${SMP_REPO:-$HOME/code/projects/sec-market}"
LOG_DIR="${SMP_LOG_DIR:-$HOME/gather-logs}"
MODEL="${SMP_MODEL:-claude-sonnet-5}"
REMOTE="${SMP_REMOTE:-origin}"
TIMEOUT_SECS="${SMP_TIMEOUT:-5400}"

STAMP="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
mkdir -p "$LOG_DIR/runs" "$LOG_DIR/receipts"
RUN_LOG="$LOG_DIR/runs/$STAMP.log"
RECEIPT="$LOG_DIR/receipts/$STAMP.json"

log() { printf '%s  %s\n' "$(date -u +%H:%M:%SZ)" "$*" | tee -a "$RUN_LOG"; }

# state carried into the receipt
STATE="started"; DETAIL=""; ISSUE_ID=""; BRANCH=""; PUSHED="false"

receipt() {
  cat > "$RECEIPT" <<JSON
{
  "stamp": "$STAMP",
  "host": "$(hostname)",
  "model": "$MODEL",
  "issueId": "$ISSUE_ID",
  "branch": "$BRANCH",
  "pushedToOrigin": $PUSHED,
  "state": "$STATE",
  "detail": $(printf '%s' "$DETAIL" | sed 's/\\/\\\\/g; s/"/\\"/g; s/^/"/; s/$/"/'),
  "log": "$RUN_LOG"
}
JSON
  log "receipt: $RECEIPT  state=$STATE"
}
finish() { receipt; exit "${1:-0}"; }

log "gather run $STAMP on $(hostname)"

# ---- 1. the repository, on a clean trunk -----------------------------------
cd "$REPO" || { STATE="failed"; DETAIL="repo not found at $REPO"; finish 1; }
git fetch -q "$REMOTE" || { STATE="failed"; DETAIL="git fetch failed"; finish 1; }
git checkout -q preview 2>>"$RUN_LOG" || { STATE="failed"; DETAIL="cannot check out preview"; finish 1; }
git reset -q --hard "$REMOTE/preview" || { STATE="failed"; DETAIL="cannot reset to $REMOTE/preview"; finish 1; }
git clean -qfd
log "trunk at $(git log --oneline -1)"

# ---- 2. which issue is due -------------------------------------------------
# The ISO week that ended on the most recent Sunday. %u is 1..7 with Sunday 7,
# so subtracting it lands on that Sunday from any day of the week.
# SMP_WEEK_ENDING overrides the computed Sunday. It exists for two real needs:
# backfilling a week the job missed, and proving the whole chain end to end
# without waiting a week for the next fire. It must be a Sunday; the gates
# reject anything else anyway.
DOW="$(date +%u)"
WEEK_ENDING="${SMP_WEEK_ENDING:-$(date -v-"${DOW}"d +%Y-%m-%d)}"
ISSUE_ID="$(date -j -f %Y-%m-%d "$WEEK_ENDING" +%G-w%V)"
WINDOW_START="$(date -j -v-6d -f %Y-%m-%d "$WEEK_ENDING" +%Y-%m-%d)"
BRANCH="issue/$ISSUE_ID"
log "issue due: $ISSUE_ID  window $WINDOW_START..$WEEK_ENDING"

if [ -f "web/src/data/issues/$ISSUE_ID.ts" ]; then
  STATE="nothing-due"; DETAIL="$ISSUE_ID already exists on the trunk"
  log "$DETAIL"; finish 0
fi
if git ls-remote --exit-code --heads "$REMOTE" "$BRANCH" >/dev/null 2>&1; then
  STATE="nothing-due"; DETAIL="$BRANCH already exists on the remote, awaiting review"
  log "$DETAIL"; finish 0
fi

# ---- 3. hand it to the model ----------------------------------------------
# The prompt goes to a file rather than straight into a variable. macbook2014
# runs bash 3.2, which cannot parse a here-document nested inside command
# substitution: it reads the apostrophes in the prose below as opening quotes
# and the whole script fails to parse. Writing the file first keeps the
# here-document at the top level where every bash handles it.
PROMPT_FILE="$LOG_DIR/runs/$STAMP.prompt.txt"
cat > "$PROMPT_FILE" <<EOM
Read docs/active/gather-brief.md in this repository and carry it out in full, now.

You are drafting issue $ISSUE_ID, window $WINDOW_START to $WEEK_ENDING inclusive.
Work on branch $BRANCH, created from preview.

Two things about this environment that override the brief where they differ:

1. You cannot open a pull request here — there is no GitHub token on this host.
   Push the branch $BRANCH and stop there. A GitHub Action opens the pull
   request automatically from the pushed branch. Write the pull request body
   the brief asks for to .gather/pr-body.md on the branch and commit it with
   your three files; the Action uses that file as the body.
2. Push with: git push -u $REMOTE $BRANCH

Follow every ground rule in section 0 of the brief. In particular: fetch with
curl so you hold the bytes, hash everything you quote, take each item's date
from a primary document rather than from a weekly roundup, and drop any item
you cannot date. Record "none found" rather than inventing. Run the gates and
record their exit codes before you push.
EOM

PROMPT=$(cat "$PROMPT_FILE")

log "invoking claude -p --model $MODEL"
CLAUDE_OUT="$LOG_DIR/runs/$STAMP.claude.txt"
# `timeout` is not on macOS by default; a background child plus a watchdog does
# the same job without adding a dependency.
(
  claude -p "$PROMPT" \
    --model "$MODEL" \
    --permission-mode acceptEdits \
    > "$CLAUDE_OUT" 2>&1
) &
CLAUDE_PID=$!
( sleep "$TIMEOUT_SECS"; kill -0 "$CLAUDE_PID" 2>/dev/null && kill -TERM "$CLAUDE_PID" 2>/dev/null ) &
WATCHDOG=$!
wait "$CLAUDE_PID"; CLAUDE_RC=$?
kill -TERM "$WATCHDOG" 2>/dev/null
CLAUDE_LINES=$(wc -l < "$CLAUDE_OUT")
CLAUDE_LINES=${CLAUDE_LINES// /}
log "claude exited rc=$CLAUDE_RC, ${CLAUDE_LINES} lines of output"

# ---- 4. did a branch actually reach GitHub? --------------------------------
if git ls-remote --exit-code --heads "$REMOTE" "$BRANCH" >/dev/null 2>&1; then
  PUSHED="true"
  STATE="drafted"
  DETAIL="$BRANCH pushed; the pull-request Action takes it from here"
  log "$DETAIL"
  finish 0
fi

STATE="failed"
if [ "$CLAUDE_RC" -ne 0 ]; then
  DETAIL="claude exited $CLAUDE_RC and no branch reached the remote; see $CLAUDE_OUT"
else
  DETAIL="claude exited cleanly but $BRANCH is not on the remote; see $CLAUDE_OUT"
fi
log "$DETAIL"
finish 1
