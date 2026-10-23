---
project: Security Market Pulse
stage: Operate
updated: 2026-10-22
---

# Status

## Live and held

**October 22 completion work is on preview; production cutover is not yet claimed.**
Use [the current GitHub/Vercel runbook](docs/active/daily-pipeline/github-operations.md) and
[acceptance record](docs/active/daily-pipeline/finish-acceptance-2026-10-22.md) before the earlier
checkpoint below. Original local `status.md` and `lessons.md` edits were preserved in the original
checkout; implementation uses `/Users/jessepike/code/projects/sec-market-finish-20261022`.

Actual fresh private Actions run `39899030431` archived **244/557** successful source checks,
zero additional model calls, at `991432eea90004d3d8a2b0fb1c80ac28f01904b4`, manifest
`a8c686a2cd6fea61ce307ebf393d8138011544b3388ed11ffee05363e225fb92`, 24,685 files.
It retained incomplete coverage and exited 2 under its older runner semantics. New code separates
successful bounded execution from incomplete coverage and retains coverage alerts. Cancelled
old-revision run `39897975103` is recovered by verified lease-only CAS; its reserved model/doc
allowance remains charged. The explicit 5,500 fetch ceiling retains charged usage, with actual
ledger now 5,367 fetches. No counter was reset.

The missing October 15 Proofpoint/Varonis acquisition agreement is primary-source verified and
rendered on preview at both widths. Daily schedules, independent gate, assigned-owner failure
alerts, interrupted-run recovery, exact production-target staging and byte verification are
implemented. Tests: 252 data, 99 pipeline, 52 operational, five monitor and 34 browser checks pass.
Actual failure alert is owner-assigned issue #8. Fresh independent preview gate is run `39899676747`.
Source coverage remains incomplete; actual scheduled and production receipts are still acceptance
work. The prospective preview policy is enabled for main after review; current production is still
the earlier revision below. No PR, purchase or paid API fallback has been used.

### Earlier production checkpoint

Production https://securitymarketpulse.com is READY at `54590be4d91113a50879a8fb5d180441e7d149f4`;
its live receipt reports certified data changed `2026-10-18T02:36:44.349Z`. The legacy four-hour SEC
schedule stays active. Work is on `preview`; the daily 74-supplier replacement still has
**publication and recurring collection disabled**. Major cutover requires owner review after
acceptance. No PRs, roster expansion, paid API fallback, infrastructure purchase, production
setting/alias change or visible change this session.

## Credentials and publisher acceptance

**Credentials are configured under D-109; do not repeat login or secret-entry requests.**
Dedicated sign-in/real subscription calls passed in `39700686412`; official refresh, rotation and
protected write-back passed on a fresh runner in `39701323872`. Owner reports both supplied tokens
have no expiration. The development cloud's restricted network is separate from CI credentials;
use connected GitHub/Vercel tools to inspect jobs.

- Existing-project read passed in `39704072043`. **Durable-credential prebuilt staging now passed**
  in [39797014280](https://github.com/jessepike/sec-market/actions/runs/39797014280), code `4dc585e`.
  A verified cached team selector avoids the official CLI's failing user-scope lookup. All **25
  static files** (24 payload files plus detached receipt) matched byte for byte at
  https://security-market-pulse-e47i6gdel-pikeholdings.vercel.app. Production was unchanged.
  This retained smoke payload is revision `a6f987b`, not a fresh independently gated daily release.
  [Receipt](docs/active/daily-pipeline/receipts/publisher-stage-2026-10-22.json).
- Application CI `39797014285` and fresh-runner canary `39797014125` passed on `4dc585e`.
  Hosted production/tested-build screenshots at 1440px and 390px were added in `5485ccf`;
  application run `39797898423` passed, including all 32 browser tests; four captures were inspected.
- Collection date repair is on `preview` in `1fcacfb`. Hosted application CI
  [39799459596](https://github.com/jessepike/sec-market/actions/runs/39799459596) passed: 251 data,
  94 pipeline and all 32 browser tests, lint/build. Final hosted captures match the inspected set. Explicit publication times now supply dates on five archived Mimecast pages.
  Arbitrary event/sidebar times, invalid dates and ambiguous listings stay held. Only affected
  extraction caches refresh; no existing hold or coverage receipt is upgraded. Local 28 worker,
  251 data and 94 pipeline tests, lint/build passed. System Chromium passed 30/32; two console
  assertions see blocked font requests. Desktop/phone before/after renders are pixel-identical.

## Collection, state and budget

Actual [bounded subscription run 39704072057](https://github.com/jessepike/sec-market/actions/runs/39704072057)
finished and archived **241/557 complete**, correctly exiting 2: 48 SEC tasks and 193 citations
passed; 301 tasks were not checked, 13 blocked and two failed. Actual usage: **80 calls / 39 documents /
412 fetches**. **October 22 UTC model capacity is exhausted; do not reset it or run another model trial.**
There are 8,557 pending source/URL pairs (7,936 distinct URLs), 28 held claims, four unpublished
historical events and no supplier patches. Dragos's investor source contributes 3,256 queued URLs;
27 holds concern dates. Repaired documents still need fresh review within a later UTC day's budget.

Latest finished `refs/archive/market-evidence`: **`9d39da64faab36500ddcab7c29a47f43a0f82b90`**,
manifest SHA-256 **`0640d1158a57c4948f5667d2f2f7fde90b11a305db2f8739bc6fc9bd99f67ee4`**.
A new independent restore verified **22,468 files**, reproduced reconciliation and rebuilt the exact
snapshot using its parent from archive history. The lease remains released. No remote archive or
budget changed. **Restore latest remote state before writing**; ordinary branch fetches exclude
this custom ref. Auth stays outside archives.
[Actual receipt](docs/active/daily-pipeline/receipts/subscription-collection-2026-10-21.json) ·
[current diagnosis](docs/active/daily-pipeline/receipts/collection-diagnosis-2026-10-22.json).

## Remaining acceptance

1. Finish full-roster coverage: 74 suppliers, 303 bindings, 557 required tasks, **254 missing family
   bindings**, 28 candidates and 19 verified sitemap registrations. Startup status stays unclassified.
   Resolve source blocks, bounded history/current-claim audits, semantic delta capacity and typed
   ownership/non-SEC financial adapters. Current limits cannot clear the historical queue daily.
   Verify Actions usage/spending limits before recurring activation.
2. Exercise the independent GitHub exact-artifact gate on reviewed main, production path controls,
   live acknowledgement/rollback, missed-worker alert and owner delivery, then sustain accurate daily
   operation. Preview write permission passed; production controls remain unaccepted. Owner-assigned
   issue #7 alert/recovery passed; phone/email delivery is unconfirmed.
3. Review the concrete major cutover before promotion or closure of competing publication paths.
   Keep legacy SEC jobs and publication/recurring holds until acceptance.

The failed native scheduler saved/ran no tasks; **do not repeat that UI handoff**. Private CI is
independent. The unapplied environment correction (`stale_base`) does not block CI; Mac/Linux is
fallback. [Runbook](docs/active/daily-pipeline/README.md) ·
[Private CI](docs/active/daily-pipeline/subscription-ci.md) ·
[Validation](docs/active/daily-pipeline/validation.md) · D-104 through D-109 in decisions.md.
