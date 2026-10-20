---
project: Security Market Pulse
stage: Operate
updated: 2026-10-20
---

# Status

## Live

- https://securitymarketpulse.com serves `54590be4d91113a50879a8fb5d180441e7d149f4`.
  Last certified data change: `2026-10-18T02:36:44.349Z` (Oct 17, 7:36pm PDT).
- Latest SEC refresh inspected: [39324337964](https://github.com/jessepike/sec-market/actions/runs/39324337964),
  `2026-10-19T21:02:46Z` (Oct 19, 2:02pm PDT), success; certification passed, data publication skipped.
  A no-change check does not advance the last data-change timestamp.
- Existing production automation checks 16 SEC filers every four hours. It does not refresh the
  entire 74-supplier site. D-103 promotion changes remain on `preview` ahead of production.
- Owner's outreach hold stands until sustained fresh, accurate operation is demonstrated.

## Authorized work in progress (D-104)

Owner requested implementation of daily collection **and daily reconciliation** for all current
74 suppliers, expansion-ready contracts, durable evidence/deltas, subscription-backed agents,
independent checks and alerts, automatic factual releases, and separate data/application releases.
No supplier expansion or additional spending is authorized.

`feat/durable-daily-pipeline` is based on `preview`. Implementation and exact activation gaps:
[runbook](docs/active/daily-pipeline/README.md),
[74-supplier matrix](docs/active/daily-pipeline/coverage-matrix.md),
[all source tasks](docs/active/daily-pipeline/source-matrix.csv).

- Canonical policy: 557 required daily tasks; 270 missing source-family bindings; 47 unverified
  discovery candidates. Missing work stays in the denominator. Startup status is unclassified.
- Implemented execution core: immutable evidence, resumable manifests, conditional fetches,
  deduplication, persistent model budgets, separate semantic review, deterministic reconciliation,
  release/provenance/rollback interfaces and disabled collection workflow. Existing published
  claims/page/schedule remain unchanged. Independent SEC verifier now correctly anchors late
  notices/transaction forms to their filing date, with regression tests.
- Local checks: 63 pipeline tests; full existing data/operations and browser checks recorded in
  [validation](docs/active/daily-pipeline/validation.md). Production/candidate full-page screenshots
  at 1440/390 were pixel-identical. Local tests do not establish live operational readiness.

## Blocked live prerequisites and remaining implementation

- Owner confirmed **no persistent unattended subscription worker or scheduled cloud task exists**.
  Existing cloud CLI recognizes ChatGPT login; inference probe failed with proxy CONNECT 403.
  GitHub-hosted jobs do not inherit this login. No API fallback or copied login tokens.
- GitHub repository/Actions access works; secret administration returned 403. Vercel management
  token is unbound/missing. Public production GET works. The user's local computer is not accessible.
- Cloud setup draft saved Node 22/Python/system-Chromium instructions and 59 custom network hosts.
  Review/save in environment settings; saving a draft does not prove runtime application/publication.
- Still required: verified discovery bindings and filing/PDF collectors; startup classifications;
  durable remote-store integration/independent backups; full claim-to-site snapshot mapping;
  actual trusted release-gate workflow and Vercel artifact adapter; public coverage endpoint;
  deployed outside watchdog and confirmed owner alert destination. Cloudflare files are tested
  handler examples, not deployed services or proof of zero cost.
- Keep `MARKET_PIPELINE_ENABLED` unset/false and publication disabled until the runbook's live
  acceptance gates pass. Current four-hour legacy automation stays until a verified daily cutover.

## Next

1. Configure the selected unattended host, required source/auth network access and secure Vercel
   binding; choose storage/backup and alert destination without exceeding the approved cost ceiling.
2. Continue source onboarding and snapshot/release integration against real receipts, then run the
   runbook's complete live failure/recovery/rollback tests. Review the concrete preview before the
   external-service/deploy-policy cutover, as required by AGENTS.md.
3. Establish burn-in duration before outreach. Prior open items remain: intent v1.5 confirmation,
   SEC-060 email inputs, SEC-061 account items, SEC-063 retired snapshot cleanup.
