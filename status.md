---
project: Security Market Pulse
stage: Operate
updated: 2026-10-21
---

# Status

## Live and held

Production https://securitymarketpulse.com last acknowledged
`54590be4d91113a50879a8fb5d180441e7d149f4`; certified data last changed
`2026-10-18T02:36:44.349Z`. The legacy four-hour SEC schedule covers 16 filers and stays active.
The daily 74-supplier replacement is on `preview`, with **publication and recurring collection
disabled**. Major production cutover still requires owner approval after acceptance. No PRs,
roster expansion, paid API fallback or new infrastructure purchase. No web/layout changes this session.

## Credentials and private CI acceptance

D-109 authorizes the dedicated official Codex login, repository-only secret writer and existing-
project Vercel credential. **Credentials are configured; do not repeat login or secret-entry
requests.** The owner reports both supplied tokens have no expiration.

- Dedicated runner sign-in, encrypted login storage and real subscription call passed in
  [39700686412](https://github.com/jessepike/sec-market/actions/runs/39700686412).
- A second fresh runner proved official `account/read` refresh, token rotation, protected write-back
  and a real subscription call in [39701323872](https://github.com/jessepike/sec-market/actions/runs/39701323872).
- Vercel probe `39701439701` hid its CLI error. Diagnostic `39703939654` located it in user lookup
  before project access. Fixed probe addresses the pinned project with explicit `teamId`, avoiding
  `--scope` user discovery. [39704072043](https://github.com/jessepike/sec-market/actions/runs/39704072043)
  passed with the configured credential. Read access is proved; publish permission and production-
  path controls are not accepted. [Receipt](docs/active/daily-pipeline/receipts/publisher-access-2026-10-21.json).
- First collector `39703939715` stopped before collection: fresh Ubuntu lacked `pdftotext`.
  Fixed workflow installs Poppler and initializes a nonsecret setup-failure receipt. Corrected pin
  **`255f5fadca18ad86b5a7fcb1277413ffb6bc7ca9`** passed
  [application CI](https://github.com/jessepike/sec-market/actions/runs/39704072065) and
  [private host canary](https://github.com/jessepike/sec-market/actions/runs/39704072051).
  24 worker, 251 data, 91 pipeline and 32 hosted browser tests passed; lint/build passed.
  Local browser 30/32 was limited by blocked Google Fonts requests; hosted browser 32/32 passed.

## Actual collection and durability

[Bounded subscription run 39704072057](https://github.com/jessepike/sec-market/actions/runs/39704072057)
completed on the corrected pin, archived its final state and correctly **exited 2 for incomplete
coverage**. Run `a466a48826e856d93851c0e8eedf76b47ab3e5cd957086b78196337792b6698d`, scheduled
`2026-10-22T01:11:00.854231Z`, reconciled `2026-10-22T01:21:15.264539Z`:

- **241/557 complete**: 32 SEC APIs, 16 filing archives, 193 citation checks; 301 not checked,
  13 blocked, two failed. Prior run was 252/557. Eleven previously passing citations now have
  five HTTP 403s, three 429s, two 502s and one timeout. All 48 SEC tasks passed.
- **80 model calls, 39 document reservations, 412 fetches**, no API fallback. October 22 UTC model
  capacity is exhausted; preserve that budget. 8,557 URLs remain pending, 28 claims held. Four
  historical source-backed events are retained in the unpublished snapshot; no supplier patches.
- Fresh independent restore verified **22,468 files**, reproduced every reconciled task and the
  exact snapshot seal/content. Final lease released `2026-10-22T01:21:35.837403Z`. Pre-work fresh
  restore also verified the remotely acknowledged 80/40/5,000 crash-protection escrow. Final
  acknowledged budget records actual 80/39/412 usage. Auth remains outside archived state.

Latest finished `refs/archive/market-evidence`: **`9d39da64faab36500ddcab7c29a47f43a0f82b90`**,
manifest SHA-256 **`0640d1158a57c4948f5667d2f2f7fde90b11a305db2f8739bc6fc9bd99f67ee4`**.
[Actual receipt and independent verification](docs/active/daily-pipeline/receipts/subscription-collection-2026-10-21.json).
Snapshot SHA-256 `d031c5221056248cacc829b524185b1c166b5c609abc169e44e825441bfd5929`.
**Restore the latest remote state before writing.** Old local copies and the earlier 20,035-file
archive are stale and must not overwrite newer heads or budgets. Ordinary branch fetches exclude
this custom ref. Source dates and held work are preserved; retrieval is not a historical claim audit.

## Remaining acceptance

1. Complete full-roster coverage: 74 suppliers, 303 bindings, 557 required daily tasks, **254 missing
   family bindings**, 28 candidates and 19 verified sitemap registrations. Startup status remains
   unclassified. [Current matrix](docs/active/daily-pipeline/coverage-matrix.md) and CSV now reflect
   the actual latest run. Address source blocks/retries, bounded backfill/current-claim audits,
   semantic delta capacity and typed ownership/non-SEC financial adapters. Current budgets do not
   clear the historical queue daily. Verify Actions usage/spending limits before recurring activation.
2. Exercise the actual independent GitHub exact-artifact gate, prebuilt publisher permission,
   promotion/rollback, missed-worker alert and owner delivery; sustain accurate daily operation.
   Prior prebuilt preview proof covers 24 exact files and 32 remote browser checks; production
   rollback baseline is saved. Owner-assigned GitHub alert/recovery issue #7 passed; phone/email
   delivery remains unconfirmed. Close competing publication paths only in the reviewed cutover.
3. Keep publication and recurring collection disabled until those gates and owner-reviewed major
   cutover pass. This trial proves bounded private-runner operation, not complete daily acceptance.

The attempted native scheduler could not bind this repo/environment or guarantee fresh chats;
no native tasks were saved or run. **Do not repeat that failed UI handoff.** Private CI is independent.
The environment instruction correction returned `stale_base`; its
[portable proposal](docs/active/daily-pipeline/environment-correction-2026-10-21.json) remains
unapplied and does not block CI. Saved drafts are not published jobs. Mac/Linux installer is fallback.

[Runbook](docs/active/daily-pipeline/README.md) · [Private CI](docs/active/daily-pipeline/subscription-ci.md) ·
[Validation](docs/active/daily-pipeline/validation.md) · D-104 through D-109 in decisions.md.
