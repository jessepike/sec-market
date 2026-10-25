# Manual freshness recovery: collector 40169973257

The manual recovery collector succeeded on main `6d5e87feba4ffbc75e50f35cb564cb8fd91708ca`. It completed daily intake with gaps: **264 of 557 checks**, with no publication. Its event is `workflow_dispatch`; it provides no proof that the 05:17 scheduled collector ran.

## Actual intake and review

| Measure | Actual result |
|---|---|
| Intake | 264/557; 293 gaps. |
| Gaps | 254 missing bindings; 25 unverified candidate sources; 9 HTTP 403; 4 HTTP 429; 1 unsafe redirect. |
| Processing | 38/10,655 reviewed; 10,617 pending; 10 held; 1 changed; 291 unknown dates. |
| Historical review | 39/10,655 reviewed; 10,616 pending; 10 held. |
| Daily counters | 444/5,500 fetches; 72/80 model calls; 33/40 documents. These are independent archived counters. |
| Gate allowance | 1/2 attempts charged; one remains in this acknowledged archive. No October 25 publication-budget head exists. |
| Source expiry |26 October 2026 at 12:45:29.479727 UTC. |

The UTC 25 plan began at 06:45:06.019050Z. The minimum effective source check is 06:45:29.479727Z; the complete intake observation set reproduces the expiry exactly under the 30-hour rule. Older fetchedAt values remain intact for actual 304 reuse and retained immutable SEC documents. The audit does not renew an old body clock.

## Archive and continuity

Acknowledged archive: `a50c594fb8142cee8d667b4da7161a4d48620c11`, parent `ea15b84136da8b340498ababf6264a978f144123`. The observed remote `refs/archive/market-evidence` matched that commit. Manifest SHA-256: `540bb0449b922b0ea69ab3a088d35b0f3bc8926243a8d5c817ab93c2659abd8e`; Git blob:`628feb7cf49c3ece15ec11fef140da5e12ea18cf`. All 45,259 manifest entries passed hash/size checks before replay and again afterward.

Every prior path from `ac0260ed` and failed-publication archive `05e6b330` remains. Only mutable heads changed. Both prior archives retain their exact content, file times and directory times. All four original fact references, daily event/evidence objects, original dates and six admitted correction objects remain exact. No new ordinary fact reference entered the snapshot.

All 33 earlier held identities persist. Twenty-six queue rows are byte-equal. Seven Aqua missing-date identities now point to newer unsuccessful review receipts; their original receipts and dates remain retained exactly. Four new queue identities concern missing dates for HiddenLayer, Delinea and eSentire, and an unestablished source entity for ReliaQuest. The queue now contains 37 entries. No old held identity was closed.

Exact replay of all 557 archived receipts against policy H passed at its original checkedAt. Collector continuity passed using existing-object lookups that cannot write. The raw receipt is retained at `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/receipts/manual-freshness-recovery-40169973257-2026-10-25.json`; SHA-256:`e0f7047d1d79508a51a18ac3bb0ce5a50adf8d761ee0709bebdfe931943ccf32`.

## Publication readiness

I recommend taking this exact collection evidence through the separate publisher gate after the root checks current writers and the isolated complete release rehearsal. The collector lease was released at 06:58:47.729768Z. The acknowledged archive records one remaining gate attempt, so the current remote allowance must still be checked before use.

The collector did not publish. Root confirmed that the prior public source expiry was 06:05:06 UTC on 25 October; this collection receipt does not prove that the overdue public site recovered. A real gate, acknowledged release and verified public bytes remain required. The actual scheduled collector remains unproved.

The machine-readable report is `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/manual-freshness-recovery-40169973257-2026-10-25.json`. Authenticated temporary archive:`/var/tmp/smp-manual-freshness-recovery-40169973257-20261025/extracted`. This audit made no dispatch, source/model call, budget change, contract/runtime edit, Git mutation, status/backlog edit or credential-store read.
