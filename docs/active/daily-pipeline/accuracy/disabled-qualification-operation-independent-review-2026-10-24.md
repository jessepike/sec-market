# Independent review: disabled qualification operation

Status: clean within this small dormant slice. I recommend including it without selecting it in the current operational plan.

## Reviewed pins

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/onboarding.py` | `fed079e1d6db2a1dad0767eedc971a7b5950ec32f137da74b778ff0281d5c198` |
| `ops/ci/test_disabled_qualification_plan.py` | `25a45eed5161a2362cc6d13e536bf4363d54549f16d9155835d3014903a8102d` |
| `accuracy/disabled-qualification-operation-spec-2026-10-24.md` | `19de845fac1b03be585799ac19b38e1ca036e69f5096f2250e3f99d0a6e50f70` |

The operational plan remains the reviewed V2 plan, raw SHA-256 `c6755ab3dd3bb491b24d2c5f791349b5f69682167ea381bbf9faefd9d8b479e5`. No source declaration or activation authority changed.

## Behavior and counterexamples

The validator requires exactly five keys, integer schema version2, the exact disabled operation, the full current-policy hash, integer allowance0 and an empty source array. The explicit dispatcher return occurs after the current-plan byte check and before bounded traversal or generic probing. Existing schema1 and bounded schema2 plans retain their separate validators.

All four focused tests pass independently in OrbStack. Eight additional checks confirm the valid operation returns zero requests/reservations, rejects float schema/allowance, Boolean allowance, object-valued sources, an extra parser revision and a missing committed file, and remains subject to the outer deadline denial. Every malformed case made zero transport calls, zero reservations and zero object writes. Valid and expired disabled cases retained only the exact raw-plan object in their temporary stores.

Bounded traversal and generic thread-pool entry points were patched to raise during the independent checks; neither was reached. A changed plan after validation is rejected before archiving or transport. Existing tests also reject unknown/missing operation, extra fields, stale policy, nonzero allowance and nonempty sources.

The report preserves the actual plan reference, raw/canonical hashes, current policy, original start/check times and unchanged reservation context. Its source rows, facts and new fact IDs are empty; model, qualification and source-check counters are zero. The unchanged outer `execute_source_probe` guard can mark the enclosing run denied after deadline or UTC rollover. Disabled execution is not source freshness, qualification, intake or coverage evidence.

No source, network or model request, actual state/archive write, source/plan selection, allowance change, Git operation or publication occurred. Temporary fictional stores were removed. The separate actual V2 run is outside this verdict; its completion and retained archive need independent evidence.
