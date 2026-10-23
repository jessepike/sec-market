# GitHub Actions and Vercel completion

## Scope and authority

Jesse's October 22 request authorizes finishing daily collection, source validation, publishing
and failure alerts on GitHub Actions and the existing Vercel project. No Codex Cloud scheduler,
pull request, purchase or paid model API fallback is part of this route. The accepted facts-only
boundary remains. Major production changes require review of the concrete preview under AGENTS.md.

Work started from `origin/preview` at `e9d73b05df50e7faaebd65df1d0f1d0fd44ce962` in the
separate `/Users/jessepike/code/projects/sec-market-finish-20261022` checkout. The original
checkout's `lessons.md` and `status.md` changes remain untouched. Original implementation commits
are retained on local branch `codex/finish-pulse-20261022`.

## Actual production audit

Vercel reports production deployment `dpl_CMKqTcPFjP7ZtAUW114LQrQZnyJX` READY at application
revision `54590be4d91113a50879a8fb5d180441e7d149f4`. The public `/app-release.json` agrees and
reports last certified data change `2026-10-18T02:36:44.349Z`.
`/tracker.json` and `/certified-coverage.json` answer. `/deployment-receipt.json` and
`/daily-coverage.json` do not yet represent a production daily release. The existing green
scheduled certified-refresh, promotion and freshness runs are legacy operations.

The Varonis record missed the October 15 Proofpoint acquisition agreement. Its generic 8-K
leadership event was not a substitute. The correction adds the primary release, dated event,
approximately $6.3 billion consideration and transaction conditions, while retaining Varonis's
public status until closing. See `receipts/varonis-missing-event-2026-10-22.md`.

Original failed probe `39701439701` failed before project access during CLI account lookup.
The fixed team/project request passed in `39704072043`; durable prebuilt staging and exact file
verification passed in `39797014280`. No replacement Vercel credential is needed.

## Implemented candidate

The daily collector has a real Actions schedule at 05:17 UTC. A separate publisher runs at
06:23 and 16:23 UTC and accepts only the exact artifact from the independently verified main
workflow. Collection and publication serialize archive writers. Each job retains a receipt;
failures raise an assigned-owner issue and recovery closes it.

Current-source changes take priority over old pages, with a bounded historical audit allowance.
Historical queues and missing source obligations remain recorded. Publication already permits
individually verified facts under incomplete general coverage, while requiring all 80 SEC checks.
No missing source check becomes a successful check. Prior-policy coverage is conservatively held
at 0/557 with the original collection date until a run under the new policy replaces it.

The monitor independently checks GitHub's actual scheduled-event identity. A manual dispatch or
green workflow alone cannot prove the timer or complete coverage. Collection is monitored even
while public publication remains disabled.

## Verified candidate and production decision

The exact independently tested candidate is available at
https://security-market-pulse-46vmiltbr-pikeholdings.vercel.app.
Independent gate [39900926508](https://github.com/jessepike/sec-market/actions/runs/39900926508)
passed all 389 checks: 256 data, 99 pipeline and 34 browser tests. Hosted Varonis browser checks
also passed at both widths. The full-page captures were inspected at 1440px and 390px.
The layout remains consistent; visible changes include the Varonis agreement, daily cadence,
updated figures and an explicit incomplete source-coverage statement.

Staging [39901214904](https://github.com/jessepike/sec-market/actions/runs/39901214904)
verified all 25 static files against artifact SHA-256
`f98e9e9d2dd204041296dce9318772a5bbe432bbc5da54c569b5d5a9f9f44821`.
Production stayed at `54590be4d91113a50879a8fb5d180441e7d149f4`.
This preview gate is accepted for review only; publication still requires a new independent gate
on reviewed main.

The actual archived collection at `991432eea90004d3d8a2b0fb1c80ac28f01904b4` completed
244/557 source checks with zero additional model calls. Its manifest is
`a8c686a2cd6fea61ce307ebf393d8138011544b3388ed11ffee05363e225fb92`.
The cancelled older runner's reserved usage remains charged. Verified lease-only recovery
preserves those counters. Execution failure raised assigned-owner issue
[8](https://github.com/jessepike/sec-market/issues/8); coverage failures remain separate.
Local operational checks now total 57, with six monitor tests.

The requested decision is approval to activate this candidate: close the competing legacy
publication paths, advance main from reviewed preview, run the main independent gate and exact
production publisher, and perform the journaled rollback-and-restoration acceptance. No PR or
paid API fallback is involved. The retained legacy deployment remains the initial rollback target.

The completion claim still requires actual production acknowledgement, rollback restoration,
and real scheduled collection/publication receipts. Those have not yet been obtained.
Full source coverage and sustained multi-day operation remain open regardless of a green timer.

A later full hosted browser replay from the ordinary committed checkout returned 29/34:
three checks compared the staged archive's generated data with the checkout's different snapshot,
and two strict-console checks detected Vercel's preview feedback script blocked by the site's CSP.
That replay cannot replace the 34/34 exact-input gate or the 2/2 hosted Varonis checks. Production
acceptance must use the main gate's matching inputs and verify the actual production host; preview
feedback injection is not part of the static artifact.

## Pending cutover commands

The owner approval question is pending. No production setting, legacy schedule or main ref has
changed. Reviewed preview is `e30dd095658a7ec76dfde07b162845acfbf26b4c` plus receipt-only updates.
After approval, disable `certified-refresh.yml` and `promote.yml`, set Vercel
`autoAssignCustomDomains` false and `commandForIgnoringBuildStep` to
`test "$VERCEL_GIT_COMMIT_REF" = main || test "$VERCEL_GIT_COMMIT_REF" = data/archive`,
and confirm the live `54590be` app receipt remains unchanged. Then fast-forward main from
preview. Dispatch `subscription-publisher.yml` on main; it requests a fresh independent main gate
and records publication. Run `production-rollback-drill.yml` with the acknowledged release hash.
Do not cancel collection or rollback jobs. Confirm actual scheduled collector and publisher runs
and their archived receipts before claiming completion.

## Earlier verification history

- Preview code `0acd501c5821fcf55af5311333f274abfdca9b1b` deployed READY as
  `dpl_3vcMFMEVr752R2ARzgBHJ1TxCfXn`. Hosted application run `39898311917` passed.
- OrbStack: 252 data tests, 98 pipeline tests, 35 operational tests, 5 monitor tests,
  build including all 80 SEC checks, and all 32 browser tests passed.
- Full-page production and actual stable-preview captures at 1440px and 390px were inspected.
  The layout remains consistent. The visible changes are the Varonis agreement, source-check
  disclosure and updated figures already on preview; source coverage remains explicitly incomplete.
- Manual run `39898326607` failed because cancelled older run `39897975103` retained its lease.
  The assigned-owner failure alert is actual issue #8. An explicit cancelled-run recovery is being
  tested. No daily model allowance is refunded after an unacknowledged interruption.

The completion claim requires the fresh evidence archive, successful independent gate, exact
staged bytes, reviewed production cutover, production acknowledgement, rollback acceptance,
and actual `event=schedule` receipts. None is inferred from code, configuration or a manual run.
Sustained multi-day operation remains a later observation rather than something a single test proves.
