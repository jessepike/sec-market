---
project: Security Market Pulse
stage: Operate
updated: 2026-10-21
---

# Status

## Live and delivered

Production https://securitymarketpulse.com still serves `54590be4d91113a50879a8fb5d180441e7d149f4`.
Its last inspected certified data change is `2026-10-18T02:36:44.349Z`. Legacy four-hour SEC jobs
cover 16 filers. They stay until the daily replacement passes acceptance; they do not refresh
all 74 suppliers. The owner requires sustained accurate operation before promoting to readers.

Native cloud implementation delivered directly to preview at
`6a43ed1c4a9439fc9ef0ddc13fb76bfab3f54299`.
[Full GitHub CI passed](https://github.com/jessepike/sec-market/actions/runs/39523581752):
251 data, 91 pipeline and 32 browser tests; 80/80 SEC proofs and zero drift.
[Vercel preview](https://security-market-pulse-git-preview-pikeholdings.vercel.app) acknowledges
that exact commit and discloses incomplete coverage. Full-page desktop/phone renders reviewed;
this delivery adds no visible change beyond the existing coverage disclosure. **No PRs.**
Major changes remain held under AGENTS.md; production has not been promoted.

## Actual coverage and durability

- Contract: 74 suppliers, 303 bindings, **557 required daily tasks**, 254 missing family bindings,
  28 candidates, 19 verified sitemap registrations. Startup status is unclassified. No roster
  expansion or API/infrastructure purchase. [Matrix](docs/active/daily-pipeline/coverage-matrix.md).
- Actual full run `26863a52238929063d5a6191c7e390dbeacf413920d84ac1b4f2f58bed8cdde7`
  finished `2026-10-20T22:02:44.836353Z`: **252/557 complete** (32 SEC APIs, 16 primary-document
  archives, 204 citation checks); 296 not checked, six failed, three blocked. Fourteen held claims,
  8,875 pending URLs. Eighty collection model reservations reached the limit. No new non-SEC site
  events/patches. Retrieval does not audit every historical claim. Daily publication is disabled.
- Implemented: immutable evidence/deltas, persistent budgets, source/document queues, extraction
  plus independent review, snapshot/receipts, separate GitHub exact-artifact gate, Vercel prebuilt
  stage/probe/promote/rollback, outside watchdog and native cloud runner. The native queue needs
  no second CLI login: scheduled agents answer strict role/policy-bound work. Replays retain source
  timestamps/downloads and reservations. Expiring remote leases and archive CAS reject stale writers;
  exhausted model capacity stops historical downloads while retaining missing work.
- Real native runner restored and verified 20,010 files from archive
  `d38721ca1e1e6b2869c1dfb2dbce14024270ce3c`, acquired an acknowledged lease, and completed a
  supervised known-fact canary. A fresh retrieved HiddenLayer statement passed a separate official
  ChatGPT CLI review. This is not a fresh scheduled VM test. Three native work reservations
  (including a diagnostic duplicate input), one document, one fetch and one live CLI review;
  no paid fallback. Finish correctly exited 2, preserving 252/557 and 14 held claims, then released
  its lease. The owner-assigned GitHub notification create/recovery canary passed: issue #7 closed.
  Phone/email transport is not confirmed.
- Latest durable custom ref `refs/archive/market-evidence`:
  **`02c04f568c010e4fa036bd90c791bd9ece01e6e7`**, **20,035 files**, manifest SHA-256
  **`26f7d3249981cdb983ff6339c5f7237bdd2e57bd5c02ce49c66cddd3d50972df`**.
  A second independent fresh restore verified all 20,035 files, retained budgets, sealed
  canary responses, released lease and alert receipt. Native archive/operational state is separate from ordinary app branches and excluded from normal
  branch fetches. Older `.collect/daily-state` and prior restore copies are stale: restore the latest
  remote state before writing; never overwrite its newer budgets/heads from an old local copy.

## Exact next actions and boundaries

1. **Native scheduler handoff FAILED.** On October 21 the owner supplied a screenshot showing
   the available scheduler cannot bind this repo/published environment or guarantee fresh cloud
   chats. Neither proposed task was saved or run. Do not repeat that UI handoff. The screenshot
   is evidence about the attempted scheduler, not proof that every possible cloud surface lacks
   the capability. The [private CI alternative](docs/active/daily-pipeline/subscription-ci.md)
   uses the documented account-auth round-trip. A credential-free GitHub-hosted runtime canary
   and a seven-test credential persistence helper are prepared. No account credentials have been
   transferred; no recurring replacement worker is active. Current integration secret-management
   and Actions-admin APIs return 403 even though repository push/Actions reads work. D-83 requires
   explicit approval for a dedicated CI login and repo-restricted secret-writer credential. Actual
   runner receipt and account usage limits must be checked before activation.
2. Complete source-family onboarding, bounded backfill/current-claim audits, semantic delta efficiency
   and typed ownership/non-SEC financial adapters. Existing selected metric/round/event adapters do
   not cover every field. Current budgets do not clear the historical backlog daily.
3. Validate native fresh-VM authorization, the actual trusted GitHub gate, live promotion/rollback,
   missed-worker alert and owner delivery; sustain daily operation. Then review the concrete major
   cutover. Close competing deployment paths before activation. Current prebuilt preview proof
   covers 24 exact static files and 32 remote browser checks; production rollback baseline is saved.

GitHub Git/repository/Actions access and Vercel owner management access are verified. The proposed private CI worker needs a dedicated official account login, separately authorized
for that job stream. A future runner does not inherit personal credentials;
never snapshot or transfer OAuth files to CI. D-83 credential governance remains. No API billing
fallback. The attempted native scheduling route is blocked; private CI is being evaluated. The Mac/Linux
installer remains a fallback. The local computer
cannot be inspected here. Saved cloud draft/start instructions are not published or scheduled jobs.

[Runbook](docs/active/daily-pipeline/README.md) · [Native task runner](ops/cloud/TASKS.md) ·
[Current cloud documentation research](docs/active/daily-pipeline/cloud-scheduling.md) ·
[Validation](docs/active/daily-pipeline/validation.md) · D-104 through D-108 in decisions.md.
