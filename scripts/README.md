Executable scripts live in web/scripts/. See web/README.md.

## Publishing from the phone

`gather.sh` opens a pull request titled `Issue <id> draft` against `preview` every week. Approving
that pull request in the GitHub phone app, or commenting `publish` on it, is the signature
(SEC-MARKET-PUBLISH-001 §2) — `.github/workflows/publish-issue.yml` and `publish-issue.sh` in this
directory sign the issue, run the full test suite, and promote to production, unless `preview`
already carries other site work nobody has promoted yet, in which case the issue is signed and left
on `preview` for a separate, deliberate promotion.

Adding the word `reconfirm` — an approving review whose body contains it, or a comment that is
exactly `publish reconfirm` — re-dates every judged claim (a domain stance, a hypothesis, a
Platform-pressure row) that is stale as of the signing date and that the gather did not flag in
`proposed.challengedClaimIds` (SEC-MARKET-PUBLISH-001 §4.3). Ordinary `publish` re-dates nothing.
The success comment says how many stances were re-dated and names any challenged ones left stale on
purpose — those need a session, not a rubber stamp.

`gather.sh` runs the model with `claude -p --permission-mode acceptEdits`, and a headless run cannot
answer a permission prompt, so the script also passes `--allowedTools` with the narrow, commented
list of shell and file commands the gather brief actually needs (curl, hashing, EDGAR's JSON, PDF
extraction, date arithmetic, the specific git subcommands, and `npm run`/`npm ci`), plus
`--disallowedTools` for the handful of push forms that could reach `main` or `preview`. It is a
guard against a mistaken command, not a sandbox — curl is still allowed and the subscription token
is still in this process's environment, tracked as BACKLOG SEC-051. To add or narrow a pre-approved
command, edit the `ALLOWED_TOOLS`/`DISALLOWED_TOOLS` arrays inside `gather.sh` itself, just above
where it invokes `claude -p`.

Before it starts the hour-long draft, `gather.sh` checks that the Claude login on the host running
it (macbook2014, under launchd) is still good, since launchd and a non-interactive ssh shell never
load a shell profile. It loads the subscription token from `~/.env.local` on that host, a
plain-text `KEY=value` file, mode 600, never committed, holding `CLAUDE_CODE_OAUTH_TOKEN=...`. If
that login has gone stale, the receipt says so and names the fix: run `claude setup-token` on that
host and put the printed token into `~/.env.local`.

The workflow runs in three phases, so a token is only ever in the hands of code that actually needs
to push (`.github/workflows/publish-issue.yml`, `publish-issue.sh --phase guard|build|release`).
Guard and build hold no token at all — the issue branch's own checkout has no stored git
credentials either — because build is where the branch's own TypeScript actually executes (the sign
step and the test suite import it). Only release, which runs last, authenticates a push, and only
with an explicit per-push header, never a stored credential.

Several guards run before anything pushes. The script refuses unless the branch it checked out is
still at the exact commit that was approved (a later push to the same branch needs a fresh
approval), unless a "publish" comment is older than the branch's own latest commit (a fresh comment
is needed if the branch moved after he wrote it), and unless the branch only touched the files
`docs/active/gather-brief.md` actually authorizes the gather job to write. It also refuses to
promote to `main` — loudly, as a failed run — if `preview` already differs from `main` outside pure
record-keeping paths (`docs/`, `status.md`, `decisions.md`, `BACKLOG.md`, `lessons.md`, `README.md`);
the issue still reaches `preview`, just not production, until that's promoted separately. Widening
any of these checks needs the owner's word. The workflow also runs a second, separate checkout of
`preview`'s `scripts/` directory and publishes from that copy, so a compromised issue branch cannot
rewrite the script that decides how it gets published; the release phase re-verifies that checkout
is still exactly what it started as, right before it pushes anything — see the "Known gap" note at
the top of `publish-issue.yml` for what this does and does not cover.

`test-publish-issue.sh` in this directory unit-tests the guard logic (the allowlist, the
approved-commit check, the comment-race check, the production-parity pathspec, the not-promoted
path, and a full push-order/fatal-promote run against a local file-based git remote) without a
network or npm: `bash scripts/test-publish-issue.sh`.
