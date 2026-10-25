# October 25 recovery scorecard

The actual recovery restored production. The unmodified offline evaluator now scores that
release using its original complete collection receipt and actual independent gate, publisher
and rollback receipts. This observation is fixed at 07:52:32 UTC on October 25. It does not
replace the October 23 or 24 baselines or turn manual recovery into timer evidence.

| Measure | Actual result |
|---|---|
| Daily intake | Fail: 264/557. All 293 gaps remain: 254 missing bindings, 25 candidates and 14 access failures. |
| Document processing | Fail: 38/10,655 reviewed; 10,617 pending and 10 held. |
| Historical review | Fail: 39/10,655 reviewed; 10,616 pending and 10 held. |
| SEC source tasks | Pass: 48/48. The separate release gate also re-derived all 80 required SEC claims. |
| Known release checks | Pass: all four required commands and 531 executed release tests. This is not a general accuracy estimate. |
| Publication and recovery | Pass for this manual cycle: actual publisher 40172130763 and rollback/restoration 40173134585. |
| Data continuity | Pass for the four explicit preservation checks: all 37 review entries, four fact references, eight current-or-quarantined events and six accepted correction groups. |
| Genuine timer and sustained operation | Unmeasured for this revision. No current-policy daily timer receipt had appeared when this observation was generated. The earlier overdue window remains a failure in the operational record. |
| General claim precision, event recall and reader value | Unmeasured. |

The evaluator's receipt-age pass refers only to the original collection receipt at
06:53:46 UTC. It is not an oldest-source freshness calculation. The separately verified
production artifact preserves its actual source-bound validUntil of October 26 at
12:45:29.479727 UTC. A later evaluator run cannot renew that expiry or make all 557 checks fresh.

The continuity input is derived from the already authenticated actual publication verification,
with both the verification summary and original collector receipt hash-pinned. It does not repeat
source authentication or independent admission. The eight preserved events comprise four
current-policy projections and four pending historical records with original dates and evidence.

The historical 177-record audit retains its original verdicts. It is not supplied as a current
revision claim audit. The separately verified five-record contradiction-remediation benchmark
remains 5/5 fixed; no broad current precision, recall or absence-of-errors percentage follows.
Remaining record qualifier proposals and unsupported claims stay on their existing review queue.

## Reproduction and retained inputs

From `/Users/jessepike/code/projects/sec-market-finish-20261022`:

```sh
orb run -m dev bash -lc 'cd /mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022 && python3 -B ops/evaluation/scorecard.py --manifest docs/active/daily-pipeline/evaluations/2026-10-25/scorecard-inputs.json --output /var/tmp/smp-recovery-scorecard-20261025'
```

Choose a new output prefix if it already exists; the evaluator refuses overwrite. The manifest
pins complete copied policy and coverage bytes, actual collector/gate/publication/rollback
receipts and the derived continuity audit. Coverage bytes match the gate's original collection
receipt SHA-256 f2486a623d93da011eaaf11926e09d6ce1533dab26d4a8f2fa2875a95a84d0b6.
The frozen source file kept its exact bytes, size and modification time after the read.

Generated reports:

* [Operational scorecard](operational-scorecard.md).
* [Machine-readable scorecard](operational-scorecard.json).
* [Pinned input manifest](scorecard-inputs.json).

The next operational proof is the actual scheduled collector and automatic publisher outcome.
The next coverage work is source-specific qualification and supported document review within the
same charged allowances. No source decision or new purchase is needed from the owner.
