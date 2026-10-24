# Repair release observation

Evaluated at 2026-10-24 01:52:28 UTC for release `19fde803d09aa544672183769c257e37faf727b75e1914955f54f3c5fb126941`, application revision `26181a2d4eb0aad1bd751cda70ab8e65142d2813`.

The release publisher run `40050633432` succeeded and main gate `40050850177` passed all four checks with 511 tests. The exact saved acknowledgement was independently matched against all 53 files on both production hosts. The daily publisher recovery issue is closed with a successful runner result.

The newest supplied collection completed 244 of the fixed 557 checks at 00:36:59 UTC. It was manually dispatched on the previous application revision, so it does not establish coverage for the current revision or a scheduled run. Its receipt is 1.20 hours old, within the policy's 30-hour age limit; full-roster freshness still fails because coverage is incomplete.

The release includes five factual correction groups mapped to the five historical contradiction IDs, plus one publication-role group. This supports only the claim that these five specific historical targets have corrections in the verified release. The fixed audit still records its original 5 contradictions among 177 records. That audit remains historical and unchanged; it does not state that the current site has zero contradictions or establish general accuracy.

The release-specific manual rollback drill `40051385049` passed at 01:51:46 UTC. It verified both baseline and current bytes and left the production head on this release. An independent follow-up at 01:52:28 UTC matched all 53 files on both production hosts. This is one manual drill; scheduled execution, sustained operation, current data continuity, precision, recall and observed use remain unmeasured.

The charged receipt records both daily gate and publication limits at 2/2. The state comparison records the day ledger at 80/80 model calls, 40/40 document calls and 641 fetches. This comparison grants no coverage credit. The JSON companion pins the receipts behind these findings. No overall score is calculated.
