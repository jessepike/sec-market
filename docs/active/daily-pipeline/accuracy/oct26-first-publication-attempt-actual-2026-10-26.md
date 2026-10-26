# Actual October 26 first publication attempt

Publisher 40266519925 and its independent main gate 40266928448 failed. No new production release was published. The gate correctly stopped before an accepted static build or promotion.

## Exact failure

Both runs used main 3bb9e40c8f6324aa4f419fbe13022ec4dcaece55. The actual diagnostic artifact is 12627410461, SHA-256 c938df8b339ddb9987fb5e6417c795b82f4915b7f2a5eaa8bbd8f9d30bca1ec7. SEC certification passed all 80 proofs for 16 suppliers, with one record updated, 255 unchanged and zero failures. These 80 certified claims are separate from the 557 source obligations.

The data suite passed 378 of 379 tests. The single failure was `J baseline preserves full H history and all dates while granting zero credit`, in `web/tests/q4-baseline-migration.test.mjs:32`. Its snapshot input comes from mutable `web/src/data/generated/dailyMarket.json`. Before the test, the real gate correctly replaces that file with the fresh ordinary snapshot. The strict historical migration verifier then rejects the live snapshot as the frozen zero-credit fixture. The selected failure excerpt, exact source hashes and call-path pointers are retained. No runtime guard was weakened.

## State and charges

Post-failure archive 5ddcbc51613f125c12cdc724db821384886722f5 authenticates all 56,266 entries under manifest 8f58843e0121ce686ec7bbcff5994cd10ca96f1ab827a591358bc21e752e992e. It descends from the actual ordinary collection acknowledgement 6cf79ce0af6cfd63f8ed237465e5c6bf0800ff9c. That collection, all eight accepted correction reviews, the source bindings, 37 unchanged held rows and the exact verified Upwind document resolution remain intact.

The settled source ledger remains 444 fetches, 76 calls and 37 document reservations. The actual gate ledger records one of two attempts spent; one remains under the unchanged allowance. The publication-budget head is absent. October 25 ledgers are unchanged. The publisher lease was released at 2026-10-26T04:07:01.428398Z. There was no reset or refund.

## Actual public site

All 106 checks passed for the 52 accepted static files plus detached receipt on both the immutable deployment and public host. Every response was HTTP 200, kept its requested URL and matched the exact accepted bytes. Production remains fc8bf0984dbeacbe79519574911837d8b638f42215f6547e31ae8968b29951e4, sequence 4, app 6d5e87feba4ffbc75e50f35cb564cb8fd91708ca, snapshot 8ba13011b9d29b875082a551800d57e265238fd7ffd649ff7b99f7072ab25a89. The Vercel read-only lookup confirms dpl_GFKc3mfpR6CSeZt7u62B5LVBqQjv is READY in the existing project/team.

Public intake remains 264/557 and expiry remains October 26 at 12:45:29.479727 UTC. The six old correction rows remain exact. The two new Varonis/SentinelOne corrections are privately admitted and are not yet public. Private source expiry remains October 27 at 09:26:58.065250 UTC. There are no new-release screenshots because no new release exists.

The historical test needs a frozen historical input and then normal independent review and checks before another gate. This audit made no source/model request, state mutation, reservation, dispatch, commit, push or deployment. Genuine scheduled J operation and new production acknowledgement remain open.

## Evidence

[Hashed safe receipts](receipts/oct26-first-publication-attempt-actual-2026-10-26/receipt-index.json) retain the actual diagnostic artifact pin, selected failure excerpt, 106 exact file comparisons, actual state/allowances and safe Vercel READY response. Full raw job logs remain only in the VM.
