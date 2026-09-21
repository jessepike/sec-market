Executable scripts live in web/scripts/. See web/README.md.

## Publishing from the phone

`gather.sh` opens a pull request titled `Issue <id> draft` against `preview` every week. Approving
that pull request in the GitHub phone app, or commenting `publish` on it, is the signature
(SEC-MARKET-PUBLISH-001 §2) — `.github/workflows/publish-issue.yml` and `publish-issue.sh` in this
directory sign the issue, run the full test suite, and promote to production, unless `preview`
already carries other site work nobody has promoted yet, in which case the issue is signed and left
on `preview` for a separate, deliberate promotion.

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
