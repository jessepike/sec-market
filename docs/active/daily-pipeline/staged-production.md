# Exact-artifact staging

Normal daily releases upload only the independently tested static payload with
`vercel deploy --prebuilt --target=production --skip-domain --yes`.
The temporary upload directory contains `.vercel/output`, project metadata and
an empty `web` directory required by the existing project setting. It contains
no application source. The command creates a production-target deployment
without assigning the public domain. The adapter checks the app receipt,
detached release receipt and every static file byte before promotion and again
on the public domain after promotion.

Vercel documents that promoting a preview deployment performs a rebuild, while
promoting a staged production deployment preserves the build. Smoke payloads
marked `stage_only_smoke_test` still create preview deployments and cannot
qualify as daily release artifacts. Previously served production deployments
use `vercel rollback <immutable-url> --yes`; Vercel does not permit promoting
an already promoted deployment again.

This correction does not enable publication, modify project configuration or
prove a production promotion/rollback has run. Existing production-path,
independent main-gate and acknowledgement requirements remain in force.

References checked October 23, 2026:

- [Promoting deployments](https://vercel.com/docs/deployments/promoting-a-deployment).
- [Deploy target and skip-domain](https://vercel.com/docs/cli/deploy).
- [Instant rollback CLI](https://vercel.com/docs/cli/rollback).

Pinned official CLI 64.7.0 was installed only in the OrbStack dev VM. Its
rollback help accepts `--yes`; its deploy implementation converts
`--skip-domain` into `autoAssignCustomDomains=false` alongside the chosen target.
