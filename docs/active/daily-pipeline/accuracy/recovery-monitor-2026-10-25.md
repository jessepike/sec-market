# Actual manual monitor after publication recovery

October 25, 2026. Manual monitor
[40175735011](https://github.com/jessepike/sec-market/actions/runs/40175735011)
completed with failure on exact main `6d5e87feba4ffbc75e50f35cb564cb8fd91708ca`.
Its 20 watchdog guard tests passed. The independent daily-pipeline step then exited 2.
The legacy `probe` job succeeded because publication-enabled mode retires those older checks.
This manual invocation provides no scheduled-monitor or scheduled-collector proof.

## Actual alert and expected gaps

The monitor checked at `2026-10-25T08:13:04.369084Z`.
[Issue 10](https://github.com/jessepike/sec-market/issues/10) remains open and was updated
at `2026-10-25T08:13:14Z`; a final read retained the same body and timestamp.
The actual reported reasons were:

* `SCHEDULED_COLLECTION_RECEIPT_DIFFERS`.
* `OVERDUE_OR_INCOMPLETE_COVERAGE`.
* `DAILY_INTAKE_INCOMPLETE`.
* `PROCESSING_PENDING_10617`.
* `PROCESSING_HELD_10`.
* `HISTORICAL_REVIEW_PENDING_10616`.
* `INDEPENDENT_PROBE_FAILED`.
* `ValueError`.

The first six reflect existing partial work or missing current-policy timer proof.
Daily intake is 264/557. Processing has 10,617 pending and 10 held documents; history
has 10,616 pending. The last scheduled receipt selected by this monitor is 40082520067,
which succeeded on October 24 under app `4b5e5ec1` and policy `79cdd19b…f9f60`.
That receipt cannot establish scheduled execution under current policy H
`8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`.
The successful normal recovery collector was manual.

`OVERDUE_OR_INCOMPLETE_COVERAGE` combines two conditions. Here the accepted source
receipt is incomplete. It does not establish that the recovered public data is overdue.
Public release `fc8bf0984dbeacbe79519574911837d8b638f42215f6547e31ae8968b29951e4`,
sequence 4, still serves app 6d and snapshot
`8ba13011b9d29b875082a551800d57e265238fd7ffd649ff7b99f7072ab25a89`.
Its actual public `validUntil` is `2026-10-26T12:45:29.479727+00:00`, later than this
monitor check. The archived heartbeat is also fresh and has `phases={"finish":0}`.
The monitor did not report a failed worker phase.

## Confirmed monitor defect

The actual log exposes only the exception type `ValueError`. An offline reproduction
with the exact unmodified main code and retained real inputs identifies the deterministic
failure as `ValueError("Production health receipt exceeds byte budget")`.

The actual public `daily-coverage.json` is 1,337,257 bytes with raw SHA-256
`ac8068379c6c79760331711bfb7bb6387fbc639f9ab6f921713502c6982d47fc`.
Those bytes exactly match the entry in the already accepted artifact inventory:

* Inventory SHA-256: `0c645ba2977c3e7e3df04a99d2d677ed5e7149b8608d3b472af0ea0b0c810c36`.
* Inventory bytes: 9,441.
* Entry: `static/daily-coverage.json`, with the exact size and raw hash above.

Exact main's watchdog reader permits 1,000,000 bytes for every public JSON receipt.
It reads 1,000,001 bytes from this valid larger response, then raises at
`ops/watchdog/probe.py:130`, reached from `inspect` at line 262.

The socket-denied replay uses the real `GitHubAuthority.verify_test_receipt` and the
retained authenticated gate ZIP, with captured GitHub run and artifact metadata.
Authority verification passes before any public read. The deployment acknowledgement
and app/data pair pass next. The unchanged public reader then rejects the coverage body
at its old limit. The trace retains the actual requested and returned byte counts.
It stops before public coverage semantics, public correction inventory and the review
queue checks. The missing later reasons must not be interpreted as those checks passing.

This is an actual monitor failure after successful publication recovery. The reproduced
message and phase are local diagnostic proof; the original Actions log did not print
that message. No watchdog repair has been made in this handback.

I would bind only the larger coverage read to its accepted inventory entry's exact size
and hash, with an absolute ceiling. Keep the existing one-megabyte limit for the other
receipts and preserve every partial-coverage, held-work and timer alarm.

## Retained evidence and limits

The companion summary is
`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/recovery-monitor-2026-10-25.json`.
All receipts are under
`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/receipts/recovery-monitor-2026-10-25/`.
`exact-main-cause-replay.json` records the complete safe phase trace, source pins,
artifact match and unchanged frozen-input seals. `replay-cause.py` reproduces it offline.

Both complete raw Actions job logs are retained as deterministic gzip files, with
byte-exact round trips and raw/compressed hashes. The daily-pipeline log contains the
20 actual passing guard tests and the actual unhealthy result. Current run, job, issue,
archive, scheduled-receipt, gate provenance and public receipt evidence are separately
retained and hashed. No log whitespace was normalized. The connector's decoded-log
interface could not supply a raw-byte download, so the original job-log bytes were
retained through read-only GitHub CLI GETs.

The actual archive ref remained
`b08469e082606def8ef37d9bfeb1cc9609f48176` throughout the retained observation.
The source receipt was consulted through read/get checks against the frozen authenticated
recovery archive, with no LocalStore initialization or archive writes. No new workflow,
probe, source/model request, account call, gate attempt, deployment, dispatch, issue write,
commit or push was performed by this verification. GitHub API and public health-receipt
GETs supplied the retained read-only evidence. GitHub issue update is confirmed; phone
or email delivery is not observed.
