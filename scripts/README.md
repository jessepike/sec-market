Executable scripts live in web/scripts/. See web/README.md.

## Publishing from the phone

`gather.sh` opens a pull request titled `Issue <id> draft` against `preview` every week. Approving
that pull request in the GitHub phone app, or commenting `publish` on it, is the signature
(SEC-MARKET-PUBLISH-001 §2) — `.github/workflows/publish-issue.yml` and `publish-issue.sh` in this
directory sign the issue, run the full test suite, and promote to production, unless `preview`
already carries other site work nobody has promoted yet, in which case the issue is signed and left
on `preview` for a separate, deliberate promotion.
