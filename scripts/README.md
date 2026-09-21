Executable scripts live in web/scripts/. See web/README.md.

## Publishing from the phone

`gather.sh` opens a pull request titled `Issue <id> draft` against `preview` every week. Approving
that pull request in the GitHub phone app, or commenting `publish` on it, is the signature
(SEC-MARKET-PUBLISH-001 §2) — `.github/workflows/publish-issue.yml` and `publish-issue.sh` in this
directory sign the issue, run the full test suite, and promote to production, unless `preview`
already carries other site work nobody has promoted yet, in which case the issue is signed and left
on `preview` for a separate, deliberate promotion.

Two guards run before anything else. The script refuses unless the branch it checked out is still
at the exact commit that was approved (a later push to the same branch needs a fresh approval), and
it refuses unless the branch only touched the files `docs/active/gather-brief.md` actually
authorizes the gather job to write. Widening either check needs the owner's word. The workflow also
runs a second, separate checkout of `preview`'s `scripts/` directory and publishes from that copy,
so a compromised issue branch cannot rewrite the script that decides how it gets published — see the
"Known gap" note at the top of `publish-issue.yml` for what this does and does not cover.

`test-publish-issue.sh` in this directory unit-tests the guard logic (the allowlist, the
approved-commit check, and the not-promoted path that skips the live check) without a repo, a
network, or npm: `bash scripts/test-publish-issue.sh`.
