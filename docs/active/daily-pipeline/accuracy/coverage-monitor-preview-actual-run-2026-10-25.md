# Actual repaired monitor against accepted production

October 25, 2026. The repaired monitor executed in actual GitHub Actions run
[40177951978](https://github.com/jessepike/sec-market/actions/runs/40177951978)
on preview `05965a710f0a1cb84b582e9dc134deecf04535fe`. This was an authorized manual
read-only production check with the existing alert update. It provides no scheduled-main,
new collection, source qualification or production publication credit.

## Observed result

All 36 watchdog tests passed in the actual runner, with zero skips. The monitor checked
production at `2026-10-25T08:46:36.785971Z` and updated assigned
[issue 10](https://github.com/jessepike/sec-market/issues/10) at `08:46:50Z`.
The issue remains open. The workflow's conclusion is failure because the real remaining
coverage, historical-review, held-record and scheduled-operation gaps remain. The legacy
probe job passed through its retired-path branch.

The generic `INDEPENDENT_PROBE_FAILED` / `ValueError` result from actual main run
40175735011 is absent. Production inspection now reaches the public coverage and held-record
checks. Its exact actual reasons are retained in `actual-monitor-result.json`:

* `SCHEDULED_COLLECTION_RECEIPT_DIFFERS`.
* `OVERDUE_OR_INCOMPLETE_COVERAGE` and `DAILY_INTAKE_INCOMPLETE`.
* `PROCESSING_PENDING_10617`, `PROCESSING_HELD_10` and `HISTORICAL_REVIEW_PENDING_10616`.
* The four corresponding `PUBLIC_` intake/processing/history reasons.
* `PUBLIC_COVERAGE_INCOMPLETE_OR_OVERDUE` and `HELD_CLAIMS_37`.

Current intake is 264/557. The selected actual scheduled run is still October 24's
40082520067 under the preceding policy. Current-policy scheduled collection remains unproved.
The accepted public source expiry is October 26 at `12:45:29.479727+00:00`, later than this
monitor check. The combined incomplete-or-overdue reasons therefore do not establish expiry.

## Exact production and unchanged state

The actual before/after public application receipt, deployment acknowledgement and raw
coverage bytes are identical. Accepted release remains
`fc8bf0984dbeacbe79519574911837d8b638f42215f6547e31ae8968b29951e4`, sequence 4,
app `6d5e87feba4ffbc75e50f35cb564cb8fd91708ca`, snapshot
`8ba13011b9d29b875082a551800d57e265238fd7ffd649ff7b99f7072ab25a89`.
Coverage is exactly 1,337,257 bytes, raw SHA-256
`ac8068379c6c79760331711bfb7bb6387fbc639f9ab6f921713502c6982d47fc`.

The evidence archive ref remained `b08469e082606def8ef37d9bfeb1cc9609f48176`.
The monitor made no source/model call, gate reservation, collection, deployment or archive write.
Existing source and gate counters are unchanged. The observed write is the existing GitHub
alert update. GitHub issue delivery is confirmed; phone/email delivery is unmeasured.

The reviewed repair stays on preview while main is held for current-policy scheduled
acceptance and the existing code-bound gate allowance. Genuine repaired scheduled-main
monitoring remains a separate future receipt. No page data or appearance changed.
Preview web CI 40177941631 passed. Vercel preview deployment
`dpl_x8eMjP1csPinhA6R8aj81QhnneVT` is READY at
`https://security-market-pulse-ff52pu89e-pikeholdings.vercel.app` and its actual application
receipt matches revision 05965a71. Its uncollected preview fixture is outside publication.

## Retained proof

Evidence directory:
`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/receipts/coverage-monitor-preview-2026-10-25/`.

`verification.json` seals the actual run/jobs, before/after issue, archive ref and public
receipts, both complete original Actions job logs, and the extracted actual result. Logs
are retained as deterministic gzip with raw/compressed hashes, sizes and exact round trips.
`verify-retained-run.py` independently checks those recorded observations in OrbStack.
The [implementation handback](coverage-monitor-inventory-bound-read-implementation-2026-10-25.md)
and [independent review](coverage-monitor-inventory-bound-read-independent-review-2026-10-25.md)
retain 36 focused tests, 858 operational tests and the separate retained cross-day counterexample.

I would keep the actual monitor red until the reported gaps recover. A passing reader check
cannot establish completed source coverage or sustained daily operation.
