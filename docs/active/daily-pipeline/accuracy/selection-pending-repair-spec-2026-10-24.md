# Selection pending bookkeeping repair

The owner's current coverage-recovery request authorizes this bounded repair. It does not change the collection contract or grant coverage credit to historical documents.

## Behavior

`select_documents` returns selected due work and unselected due work. Successfully audited, unchanged documents whose rotation time has not arrived belong to retained inventory, but not pending work. The engine already retains the complete discovered/prior inventory separately in the audit inventory object; this repair does not remove any URL, observation, validation, or historical body.

History remains scoped by the engine's exact contract hash and source head. Only successful document validations create history. Missing history, a changed index signature, expired history, and malformed or future check timestamps must remain eligible. No timestamp is refreshed by selection. Existing current/audit ordering and document allowances remain unchanged.

Invalid cursor timestamps use an empty scheduling sort key, including null, missing, numeric, malformed, and future values. This keeps them due alongside normal stale timestamps without a mixed-type comparison failure.

## Verification

Focused regressions cover an entirely checked inventory with zero selected/pending, limited capacity with only remaining due work pending, missing failed history, stale/changed history, invalid/future timestamps, and input immutability. Replay the 17 pending tasks from the verified c465 archive using archived bytes only; compare before/after selection and retain all 9,897 pending-input URLs in inventory. Deny network/model access, intercept attempted archive writes, and record original archive hashes and observed counts. Run pipeline and CI Python tests in OrbStack.

## Limits

This changes pending bookkeeping only. Source-specific freshness and claim support gates remain independent. It does not complete unprocessed history, alter the 557 obligations, qualify source bindings, change limits, or modify production. Only a real collector can establish a new coverage result.

## Required integration hold

When checked, not-due inventory is omitted from new work, its prior evidence is not automatically present in the new receipt. The engine records `retainedAuditDocuments` and returns `not_checked` with `RETAINED_AUDIT_EVIDENCE_NOT_REBOUND` when unresolved pending is empty but retained evidence has not been rebound. `pendingDocuments` is zero and those URLs are not inserted into a pending manifest. The successful source cursor stays unchanged. If unresolved work remains, its existing pending reason continues to apply.

## Later evidence rebinding

A future change must independently recover hash-bound successful observations and semantic validations for every retained URL, match source, supplier, policy, raw body, extraction descriptor, candidate/fact/held-claim inventories and original check times, and enforce current source-specific freshness. An old scheduling stamp alone cannot establish this. Stale observations require genuine source checks; an unchanged body may permit validated semantic work reuse only under the existing evidence rules. Missing, changed, stale, or corrupt proof must keep completeness held. That broader change is outside this repair.
