# Genuine scheduled monitor acceptance, 2026-10-25

The repaired scheduled monitor **passed its behavior and evidence audit**. The actual workflow concluded **failure**, with healthy=false, because real intake, processing, historical-review, held-record and publisher gaps remain. No runtime change is indicated by this receipt.

## Actual scheduled execution

[Run 40191154739](https://github.com/jessepike/sec-market/actions/runs/40191154739) used event `schedule`, branch main, revision `bd38e818f4aa7d2bae2169178a02047d252b260c`. GitHub created it at 11:59:23 UTC; the monitor checked at 11:59:34.176433 UTC and the run was terminal at 11:59:47 UTC. H remains `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`.

The actual daily-pipeline runner passed **all 36 watchdog tests, with zero skips**, then reached the accepted public-coverage checks. The legacy probe job passed its retired-path branch. This is a genuine repaired scheduled-main receipt; earlier manual and preview monitor runs remain separate evidence.

Neither `INDEPENDENT_PROBE_FAILED` nor `SCHEDULED_COLLECTION_RECEIPT_DIFFERS` appears in the actual result or updated issue. The selected scheduled collector is the successful genuine run 40182324149. The former scheduled-policy mismatch is resolved by actual H timer evidence, without another monitor code change.

## Why the monitor remains red

The exact actual reasons are retained in the JSON and raw job log:

- `OVERDUE_OR_INCOMPLETE_COVERAGE`, `DAILY_INTAKE_INCOMPLETE` and their public counterparts where supplied.
- Private `PROCESSING_PENDING_10615`, `PROCESSING_HELD_11` and `HISTORICAL_REVIEW_PENDING_10614`.
- Public `PUBLIC_PROCESSING_PENDING_10617`, `PUBLIC_PROCESSING_HELD_10` and `PUBLIC_HISTORICAL_REVIEW_PENDING_10616`.
- `PUBLIC_COVERAGE_INCOMPLETE_OR_OVERDUE`, `HELD_CLAIMS_38` and `WORKER_PHASE_FAILED`.

Both source-intake views remain 264/557, with 293 gaps. Private processing reviewed 40/10,655 and historical review 41/10,655; the accepted public snapshot retains 38 and 39. Private held queue 38 remains separate from accepted public held queue 37. Processing-held document counts 11 and 10 are separate measures from those queue counts.

The worker failure is the authentic `github-publisher-40190348786-1` heartbeat with `failed:2`, produced by the actual scheduled publisher's spent-gate failure. The collector itself succeeded. The monitor reports that publisher failure truthfully.

The public source expiry is still **2026-10-26T12:45:29.479727+00:00**, later than the actual check. Its private counterpart remains **2026-10-26T15:55:27.307096+00:00**. The combined incomplete-or-overdue reason does not establish elapsed expiry here. No expiry was invented or rebased.

## Exact reader and plan verification

The exact-main offline replay reproduces the actual result, excluding the separate notification write, with sockets, live subprocesses and LocalStore construction denied. It uses the authenticated frozen post-publisher 496 archive, original retained GitHub gate/collector fixtures and accepted public bytes. The real GitHubAuthority verifier checks the authentic retained gate artifact digest and exact receipt rather than accepting a trusted flag.

The real accepted-inventory reader accepts the 1,337,257-byte public coverage object at SHA256 `ac8068379c6c79760331711bfb7bb6387fbc639f9ab6f921713502c6982d47fc`. A same-size changed body is rejected. Both private and public source inventories reconstruct from the original plan at `2026-10-25T06:45:06.019050Z`, plan SHA256 `0470e19e732f7c8d5bef1fd434a4e1798bdb61f9bf28285199102eda021eb429`. A substituted original-plan date is rejected. The accepted gate and public application/snapshot pairing remain the manual release fc8b, code 6d5e87fe, snapshot 8ba13011; this monitor creates no new release.

The monitor does not emit its actual selected archive commit. The later observed ref 9deb0c9ce9fe34999da0cf13bb023dfdfecc15c8 is retained only as a post-run observation. The offline replay's chosen 496 baseline is labelled explicitly and is not attributed to the actual monitor read. Its normal records reproduce the actual output exactly. Literal triggering cron occurrence is also not emitted, so this audit invents no nominal-run or lateness association.

## Alert and retained proof

[Issue 10](https://github.com/jessepike/sec-market/issues/10) remained open and assigned to jessepike, updated at 11:59:44 UTC with the actual check time and exact reasons. GitHub alert update is proven. Phone/email delivery remains unmeasured.

Original raw job logs are preserved as deterministic gzip with exact hashes, sizes and round-trip checks. Exact application pins, original output, issue metadata, authentic gate/collector fixtures, accepted public bytes, read-only replay harness and unchanged consumed-input seals are indexed under `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/receipts/scheduled-monitor-acceptance-2026-10-25/receipt-index.json`.

The audit made no source/model request, dispatch, gate reservation, archive write or policy change. The scheduled monitor provides operational reporting evidence; source coverage remains incomplete and no new publication or source-freshness credit is claimed. A future publisher still requires ordinary daily capacity and normal checks.

The later seven-source diagnostic callbacks `40191202723` and `40191222934` have successful workflow-shell conclusions. Their actual job metadata is retained in the companion JSON; the publication and drill/restore jobs were skipped. These later observations confer no publication or drill credit and do not change the earlier actual monitor result.
