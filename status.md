---
project: Security Market Pulse
stage: Operate
updated: 2026-10-20
---

# Status

## Production

https://securitymarketpulse.com serves application `54590be4d91113a50879a8fb5d180441e7d149f4`.
Last certified data change inspected: `2026-10-18T02:36:44.349Z`. The existing four-hour
SEC workflow covers 16 filers, not the entire 74-supplier site. D-103 changes remain on preview.
The owner will not promote the site to readers until sustained fresh, accurate operation is proved.

## Daily pipeline: implemented, exercised, not activated

Direct preview delivery: staging fix/research `530af0b9da4ba9d20ca07ec113b7c57136cdcaf4`;
[its full GitHub suite](https://github.com/jessepike/sec-market/actions/runs/39519068246) passed.
Earlier full implementation: `b8f6ecb4d10c7f05f51a3ad156cdd7e1ee31866e`.
[GitHub full suite](https://github.com/jessepike/sec-market/actions/runs/39510441692) passed.
The [stable preview](https://security-market-pulse-git-preview-pikeholdings.vercel.app)
acknowledged that exact revision and public 252/557 incomplete, automation-disabled coverage.
This is a major change held for review; production is unchanged.

Owner authorized daily collection AND reconciliation across the existing 74 suppliers, expansion,
evidence/deltas, subscription-backed workers, independent validation, alerts and automatic factual
batches. No supplier expansion or additional purchases. **No PRs:** the earlier draft #6 was closed
unmerged; deliver tested work directly to preview. See D-104/D-105 and the
[runbook](docs/active/daily-pipeline/README.md), [matrix](docs/active/daily-pipeline/coverage-matrix.md)
and [task receipts](docs/active/daily-pipeline/source-matrix.csv).

- Canonical inventory: 303 bindings, 557 required daily tasks; 254 missing family bindings and
  28 candidate registrations remain explicit gaps. Nineteen real sitemaps registered after probes.
  Startup status remains unclassified; private ownership alone does not establish startup status.
- Actual collection `26863a52238929063d5a6191c7e390dbeacf413920d84ac1b4f2f58bed8cdde7`
  finished `2026-10-20T22:02:44.836353Z`: **252/557 complete**, 296 not checked, six failed,
  three blocked. All 32 SEC API tasks, 16 filing-document tasks and 204 citation checks succeeded.
  Link/document retrieval does not certify every historical claim. Fourteen claims held; 8,875
  document URLs pending. Current conservative budget was reached: 80 collection model calls,
  36 document reservations and 5,000 fetch reservations. No paid API fallback.
- Official ChatGPT CLI sign-in and real extraction/review pilot succeeded. Full run produced
  no new publishable non-SEC events/field updates; candidate displays incomplete coverage near
  the headline and exposes `/daily-coverage.json`, including deadlines that become overdue locally.
- Immutable evidence (~1.5 GB) is saved via working native Git to the private custom ref
  `refs/archive/market-evidence`, excluded from ordinary branch fetches. Fresh remote restore
  verified 19,998 files at `7924a44781fea3d4b038686feefc50d4f30551a7`; manifest SHA-256
  `875227e57ebfcc8bd1ed51fca131e5a6dd72dc7db59993e56bb30df44b0d5324`.
  Restored independent reconciliation reproduces 252/557 degraded coverage. This is an actual
  remote recovery test, not a claim that coverage passed. SEC replay reproduced 80/80 proofs,
  zero changes and preserved the October 18 last-data-change timestamp.
- Implemented: PDF/HTML reading, filing primary-document archive, persistent budgets/queues,
  snapshot adapter, exact build/snapshot receipts, GitHub-hosted independent gate, prebuilt Vercel
  staging/promotion/rollback adapter, Mac/Linux worker installer, outside GitHub watchdog.
  Live promotion/rollback, alert and scheduler acceptance remain outstanding; real preview
  staging is verified. Optional Cloudflare
  examples are not deployed and are not the selected default storage/monitor path.

## Access and work remaining

- GitHub Git push and repository/Actions APIs work. Runner/secret administration returns 403,
  but the standalone worker design does not require those admin scopes. Release asset upload
  rejected the integration credential; native Git archive works. The empty test draft was removed.
- Vercel official browser OAuth is verified as `jessepike`, with owner access to the existing
  `pikeholdings/security-market-pulse` project. Management reads and prebuilt preview creation
  work. All 24 staged static files match their tested hashes; exact staged receipts and the
  immutable current-production rollback baseline are verified. All 32 remote browser checks
  passed with the test-preview toolbar disabled; the project setting was restored. The cloud network change now
  permits direct deployment probes; no further account sign-in is needed. Never request a token
  in chat or snapshot login credentials. Production settings/aliases have not been changed.
  The local computer cannot be inspected from this checkout. No persistent unattended subscription
  worker exists yet. This temporary cloud task is not a durable scheduled host.
- Finish complete source onboarding, bounded historical backfill/current-claim audits, semantic
  delta efficiency and typed ownership/non-SEC financial adapters. Existing adapter publishes
  independently supported events, selected company metrics and rounds, not every possible field.
- Validate the exact preview, actual GitHub gate artifact, Vercel stage/probe/rollback, owner alert
  delivery and missed-worker detection. Then review the concrete major cutover under AGENTS.md;
  keep publication disabled and legacy jobs running until those gates pass. Owner now requests
  research and preference for native Codex Cloud scheduled automations using the subscription,
  rather than assuming a local host is required. Current official docs confirm web scheduled
  tasks and remote cloud execution on subscription usage. Schedule-to-environment binding and
  a fresh unattended run are not verified; this onboarding toolset cannot create schedules. See
  [cloud scheduling research](docs/active/daily-pipeline/cloud-scheduling.md). The Mac/Linux
  installer is a fallback, not an owner-selected requirement.
- Cloud setup draft preserves Node 22/Python/system Chromium. Draft persistence is not environment
  publication or a fresh-task restore proof. Current checks and limits are in
  [validation](docs/active/daily-pipeline/validation.md). No PR is required for delivery.
