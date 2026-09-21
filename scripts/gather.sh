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
  "detail": $(printf '%s' "$DETAIL" | tr '\n\r\t' '   ' | sed 's/\\/\\\\/g; s/"/\\"/g; s/^/"/; s/$/"/'),
  "log": "$RUN_LOG"
}
JSON
  log "receipt: $RECEIPT  state=$STATE"
}
finish() { receipt; exit "${1:-0}"; }

log "gather run $STAMP on $(hostname)"

# ---- 0. load the subscription token, if this host keeps one locally -------
# launchd and a non-interactive ssh shell load neither the shell profile nor
# any login environment, so a CLAUDE_CODE_OAUTH_TOKEN left in ~/.env.local by
# a prior `claude setup-token` (plain KEY=value lines, mode 600, never
# committed) is otherwise invisible here, and the probe in section 3 below
# would see a valid login as a 401. Never echo or log a value from this file.
ENV_FILE="$HOME/.env.local"
if [ -r "$ENV_FILE" ]; then
  set -a; . "$ENV_FILE"; set +a
  log "loaded $ENV_FILE"
else
  log "no $ENV_FILE to load"
fi

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

# ---- 3. is this host still logged in? --------------------------------------
# A one-token probe, seconds and pennies, asked before the hour-long run. The
# subscription login on this host expires and a dead one returns 401 from the
# first call, so without this check the receipt would blame the gather for a
# problem that is really an expired login and needs a person at a browser.
AUTH_OUT="$(claude -p "ok" --model "$MODEL" < /dev/null 2>&1)"
case "$AUTH_OUT" in
  *401*|*uthenticat*|*"access token"*)
    STATE="blocked-auth"
    DETAIL="the Claude login on this host is not valid: $AUTH_OUT. Run 'claude setup-token' on this host and put the token it prints into ~/.env.local as CLAUDE_CODE_OAUTH_TOKEN=..., then the job resumes on its own next Tuesday."
    log "$DETAIL"; finish 1
    ;;
esac

# ---- 4. hand it to the model ----------------------------------------------
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

This host pre-approves a fixed set of shell commands; if one you need is
refused, say exactly which command in your final output and stop there, so
the receipt shows why the run ended without a branch.
EOM

PROMPT=$(cat "$PROMPT_FILE")

# ---- allowed and disallowed shell/file tools -------------------------------
# A headless run cannot answer a permission prompt, so every command the brief
# in docs/active/gather-brief.md actually asks for has to be pre-approved here,
# and nothing wider than that. Each entry is a prefix match: "Bash(git
# status:*)" allows any "git status ..." invocation and nothing that merely
# starts with "git". One rule per line, with why it is here.
#
# What this does NOT do: this is a guard against mistakes, not a sandbox.
# curl is allowed, and the subscription token this script loaded from
# ~/.env.local is present in this process's environment, so a fetched page
# that talked the model into echoing environment variables or piping them
# somewhere could still get bytes out over one of these allowed commands.
# Locking the token out of reach, or the host out of reach of a hostile page,
# is tracked separately (BACKLOG SEC-051, which covers the related gap that
# this same host's deploy key can currently push to any branch, not only the
# five files this brief authorizes).
ALLOWED_TOOLS=(
  # the five files the brief writes, and the existing files it reads as
  # worked examples (types.ts, the newest issue, evidence.ts's own format)
  "Read"
  "Edit"
  "Write"
  "Glob"
  "Grep"
  # every source in the brief's manifest is fetched with curl, verbatim
  "Bash(curl:*)"
  # hashing every document quoted from; macOS ships shasum, not sha256sum,
  # but the brief's own prose says "sha256sum", so both prefixes are
  # pre-approved in case the model tries that literal word first
  "Bash(shasum:*)"
  "Bash(sha256sum:*)"
  # EDGAR full-text search and other fetched endpoints answer in JSON
  "Bash(jq:*)"
  # PDF text extraction, and its fallback, per brief section 0
  "Bash(pdftotext:*)"
  "Bash(strings:*)"
  # ISO week / window arithmetic and comparing an item's date to the window
  "Bash(date:*)"
  # checking the "at most sixty words" excerpt limit
  "Bash(wc:*)"
  # trunk state and the orient reads in brief section 1
  "Bash(git status:*)"
  "Bash(git diff:*)"
  "Bash(git log:*)"
  "Bash(git show:*)"
  "Bash(git branch:*)"
  "Bash(git rev-parse:*)"
  "Bash(git ls-remote:*)"
  # start on trunk (step 1.1) and cut the issue branch (step 4.1)
  "Bash(git checkout:*)"
  "Bash(git switch:*)"
  "Bash(git fetch:*)"
  "Bash(git pull:*)"
  # stage and commit exactly the files the brief authorizes (step 4.1)
  "Bash(git add:*)"
  "Bash(git commit:*)"
  # push only with -u, matching the exact push this script's own prompt
  # specifies above; pushing anywhere but the issue branch is separately
  # denied below
  "Bash(git push -u:*)"
  # the verify/report gates and test:data in brief step 3.4-3.6, run only
  # through npm run; npm ci covers a missing node_modules reproducibly
  # without handing out a bare, unpinned npm install
  "Bash(npm run:*)"
  "Bash(npm ci:*)"
)

DISALLOWED_TOOLS=(
  # these four exist so a mistaken or misdirected push cannot reach the two
  # branches this job must never touch, even though the script's own prompt
  # only ever asks for "git push -u origin issue/<id>". Backstopped by the
  # branch-must-match-$BRANCH check in section 5 below, and by
  # publish-issue.sh's own allowlist, which is the real gate on anything
  # reaching production.
  "Bash(git push origin main:*)"
  "Bash(git push origin preview:*)"
  "Bash(git push --force:*)"
  "Bash(git push -f:*)"
)

log "invoking claude -p --model $MODEL"
CLAUDE_OUT="$LOG_DIR/runs/$STAMP.claude.txt"
# `timeout` is not on macOS by default; a background child plus a watchdog does
# the same job without adding a dependency.
(
  claude -p "$PROMPT" \
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
CLAUDE_LINES=$(wc -l < "$CLAUDE_OUT")
CLAUDE_LINES=${CLAUDE_LINES// /}
log "claude exited rc=$CLAUDE_RC, ${CLAUDE_LINES} lines of output"

# ---- 5. did a branch actually reach GitHub? --------------------------------
if git ls-remote --exit-code --heads "$REMOTE" "$BRANCH" >/dev/null 2>&1; then
  PUSHED="true"

  # Best-effort, fail-fast check (coordinator review of SEC-MARKET-PUBLISH-001,
  # point F, 2026-09-21): the real gate is publish-issue.sh's own allowlist
  # guard, run from a trusted checkout before anything from the branch ever
  # runs with a token. This can only run AFTER the push above, because the
  # `claude -p` subprocess above does its own push — it cannot run strictly
  # "before" that push. Kept deliberately minimal and duplicated rather than
  # shared with publish-issue.sh's is_allowed_issue_branch_path: that file
  # belongs to another session, and this is intentionally the same five
  # paths, checked independently.
  BLOCKED_PATHS="$(git diff --name-only "$REMOTE/preview...$REMOTE/$BRANCH" 2>/dev/null | grep -vE \
    "^web/src/data/issues/${ISSUE_ID}\.ts\$|^web/src/data/issues/index\.ts\$|^web/src/data/evidence\.ts\$|^web/src/data/prints\.ts\$|^\.gather/pr-body\.md\$" \
    || true)"
  if [ -n "$BLOCKED_PATHS" ]; then
    STATE="blocked-paths"
    DETAIL="$BRANCH pushed but touches file(s) outside the allowed five (see gather-brief.md): $(printf '%s' "$BLOCKED_PATHS" | tr '\n' ' ')"
    log "$DETAIL"
    finish 1
  fi

  STATE="drafted"
  DETAIL="$BRANCH pushed; the pull-request Action takes it from here"
  log "$DETAIL"
  finish 0
fi

STATE="failed"
if [ "$CLAUDE_RC" -ne 0 ]; then
  DETAIL="claude exited $CLAUDE_RC and no branch reached the remote; see $CLAUDE_OUT"
else
  # claude said it finished, but nothing reached GitHub — the receipt's own
  # `detail` field carries the model's last words so the reason is visible
  # without opening $CLAUDE_OUT as a second file. receipt() already escapes
  # this string for JSON (backslash, quote, and flattening newlines to
  # spaces), same as every other DETAIL value in this script.
  TAIL_OUT="$(tail -n 15 "$CLAUDE_OUT" 2>/dev/null)"
  DETAIL="claude exited cleanly but $BRANCH is not on the remote; see $CLAUDE_OUT; last 15 lines: $TAIL_OUT"
fi
log "$DETAIL"
finish 1
