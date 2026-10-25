# A genuine source check for the daily scheduled cycle

Date: October 25, 2026. Future preview work under the approved reliability scope. Main remains
6d5e87feba4ffbc75e50f35cb564cb8fd91708ca during actual recovery and timer acceptance. Promotion
also requires an available code-bound release gate. No active runtime change is authorized by
this specification alone.

## Supported problem

The same-day cadence review identifies two reuse layers. A manual collection and scheduled
collection under the same contract on the same UTC day share run/task IDs. Successful task
receipts may be reused. With replay enabled, saved run-download observations may also be reused.
Today force_refresh skips the first layer while still permitting the second. Old observations
keep their original clocks correctly, but a sufficiently early manual collection can leave a
later scheduled collection with too little remaining freshness for the following day's cycle.
Ordinary next-day task borrowing remains rejected. The earlier actual policy79 scheduled reuse
and the older public expiry are separate evidence; do not claim either proves an identical H
outcome or sole causation of the observed expiry.

## Small repair

1. Make existing force_refresh suppress both successful task-receipt reuse and saved run-download
   reuse. Keep conditional ETag/Last-Modified requests, original body provenance and ordinary
   same-day replay/retry behavior. A forced check must perform actual transport when required;
   never manufacture a refreshed clock on an old observation.
2. Set force_refresh only for the genuine normal daily collector event: GitHub schedule on main,
   with exact normal cron `17 5 * * *`. Normal manual runs, source diagnostics and retired
   temporary acceptance schedules keep their existing behavior. Use trusted existing event
   metadata; do not add a trigger, workflow, source, service or secret.
3. Keep in-invocation transport sharing and immutable SEC document reuse with real current index
   anchors. Keep all rate, host, size, cancellation, execution-time, daily source/model/document
   and archive guards. A depleted allowance must remain depleted; no refund or bypass.
4. Keep semantic caches, historical evidence, original dates, fact references, every held claim,
   all six old admissions and source policy H unchanged. Real conditional 304 observations have
   their actual request time and reuse chain, and are never labelled new full downloads.

## Acceptance and release boundary

Use meaningful isolated tests to show ordinary same-day replay still preserves clocks, whereas
a forced replay cannot reuse either layer and invokes bounded conditional transport. Include
normal genuine schedule selection and exclusion of manual/other branches/temporary crons/probes,
budget exhaustion and cancellation, unchanged-body 304 provenance, and immutable SEC index-anchor
behavior. Synthetic test responses are test evidence only and earn no actual collection credit.
Read frozen actual archives only through read-only adapters; retain input seals.

Run full operational and application checks, obtain independent focused review, and render the
actual production/current preview at both widths before pushing preview. The change should have
zero visible effect. Do not modify active contracts/stamps, admissions, workflow files, source
budgets, intent or main. Actual verification of this new scheduled behavior remains pending until
the repaired revision itself runs on the genuine daily timer and its source receipts are audited.
