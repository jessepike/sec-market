# Genuine scheduled H acceptance, 2026-10-25

The genuine scheduled collector **passed** its retained-evidence audit. Its automatic publisher **failed** because the October 25 UTC gate allowance was already exhausted. No new production release resulted.

## Actual execution

[Collector 40182324149](https://github.com/jessepike/sec-market/actions/runs/40182324149) ran from main `71c39356b902f3b7eff57370c79b1846129980af`, event `schedule`. GitHub created it at 09:50:43 UTC, **4h 33m 43s after 05:17 UTC**. This is actual scheduled evidence; manual recovery 40169973257 remains a separate receipt. H is unchanged at `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`.

The frozen workflow passes its cron into the guarded scheduled-main force-refresh path. The safe receipt retains the schedule event and head; it does not retain literal cron text or the force flag. The configured daily cron and actual source transport establish that relationship without rewriting any clock.

## Verified result

- Intake remains **264/557**. The 293 gaps comprise 254 unregistered discovery sources, 25 unverified bindings, 9 HTTP 403, 4 HTTP 429 and 1 unapproved redirect host.
- Processing reviewed 40/10,655 documents, with 10,615 pending, 11 held, 1 changed and 291 unknown-date documents. Historical review reached 41/10,655, with 10,614 pending and 11 held.
- The four current fact-provenance references and every old event, evidence row and original date remain exact. There are no new accepted facts or events. All 37 prior hold rows remain exact; a HiddenLayer funding candidate joins the queue because its fact date is missing. Queue: 38.
- All six correction admission objects and their dates remain exact. The correction-pass receipt advances only its own checkedAt from 06:46:28.192891 UTC to 09:56:26.497140 UTC.
- Exact-head reconciliation of all 557 tasks and collector continuity replay pass. All 48,030 archive entries pass byte-size and SHA256 checks. Earlier immutable records remain present; only mutable heads changed. Before/after content, file mtime and directory mtime seals remain exact.

## Source clocks and independent allowances

The 603 successful observation references contributing to expiry comprise 259 with status fetched/HTTP 200, 153 with status not_modified/HTTP 304 and retained-body links, and 191 immutable-body rechecks. These are observation references, not a request count. All 603 IDs are newer than the closest authenticated pre-run baseline. Original body and fetchedAt values remain retained; immutable rechecks use their separate verifiedAt. Across all newly archived observations, including noncontributing discovery/error records, there are 624 IDs; the JSON keeps this separate from the expiry set and fetch ledger.

The oldest contributing effective source clock is **2026-10-25 09:55:27.307096 UTC**; the newest is 09:59:57.709749 UTC. Adding the unchanged 30-hour limit produces **2026-10-26 15:55:27.307096 UTC**, exactly the private snapshot expiry. This grants no new public freshness until normal publication succeeds. The existing logical plan time remains unchanged.

| October 25 UTC allowance | Before | After | Actual increment | Remaining |
|---|---:|---:|---:|---:|
| Fetches |450|865|415|4,635|
| Model calls |72|80|8|0|
| Documents |33|38|5|2|
| Independent gates |2|2|0|0|

The document count comes from its independent ledger. The authenticated pre-work escrow has ceilings of 5,500 fetches, 80 calls and 40 documents. No allowance was reset or rebased.

## Automatic publisher and current public state

[Publisher 40183462577](https://github.com/jessepike/sec-market/actions/runs/40183462577) ran automatically on the same actual main revision. Its safe receipt reports `published:false`, `DAILY_GATE_BUDGET_EXHAUSTED`. Gate attempts remain 2/2; no third gate was reserved. [Issue 14](https://github.com/jessepike/sec-market/issues/14) is open, assigned to jessepike, and was updated at 10:12:18 UTC with the actual publisher link. The automatic drill 40183832621 was skipped. Prior issue 12 remains historical and closed.

The production head remains release `fc8bf0984dbeacbe79519574911837d8b638f42215f6547e31ae8968b29951e4`, sequence 4. Public code remains `6d5e87feba4ffbc75e50f35cb564cb8fd91708ca`, with snapshot `8ba13011b9d29b875082a551800d57e265238fd7ffd649ff7b99f7072ab25a89` and accepted public expiry **2026-10-26 12:45:29.479727 UTC**. The successful manual publication earlier today is unchanged by this private scheduled result. No new production or public-freshness credit is claimed.

## Archive pins and reuse

| Frozen point | Git commit | Manifest SHA256 | Entries |
|---|---|---|---:|
| Closest pre-run baseline | `9634b916c15b18f38605a168f7642de764670aab` | `600e58564c989206856ba48795bf4ce9f6fbbf73a604e806594e95327b53203a` |45,307|
| Collector acknowledged finish | `310082e9402e62b8466feea6f0b0f7d7090b7797` | `69882c245247a2f8dcfe7e5bb0999d7668e890c16b928912f3fd31ef567cd16a` |48,030|
| Observed post-callback Git baseline | `6708f37f73822d411d5ec771b307cd829c22e31d` | `8f7ae5e95610aba19ff68be30053bd4e0703a288b9482d0b9118f61cbf85350d` |48,033|

Collector manifest: 9,938,790 bytes; Git blob `835d01f482ad1f59b4014f55b7adce64aece7e82`. Post-callback manifest: 9,939,558 bytes; Git blob `0e4477a098f0a6eb6a268d844e12882dacf3bc88`. The post-callback archive changes three governance heads and adds three session records. Snapshot, production and budget heads remain exact. Its shared lease was released at 10:11:52.794373 UTC. It is an authenticated observed Git baseline, while 310082 is the collector receipt acknowledged commit.

Frozen VM inputs are `/var/tmp/smp-scheduled-h-acceptance-40182324149-20261025/extracted` and `/var/tmp/smp-scheduled-h-acceptance-40182324149-20261025/post-callback-extracted`. The latter reuses unchanged bytes through hard links and hash-checks every changed/new exact-commit object. Neither input was opened through a LocalStore constructor or written by the verifier. The read-only put adapter only looked up eight already-existing canonical objects.

The companion JSON and `receipts/scheduled-h-acceptance-2026-10-25/receipt-index.json` retain actual safe receipts, exact application pins, manifests, issue metadata, source references, independent counters and full seals. The verifier made zero source/model requests, zero gate reservations and zero operational writes. This receipt does not claim whole-site factual precision or change normal intake. A later normal publisher must use ordinary available daily capacity and normal validation.
