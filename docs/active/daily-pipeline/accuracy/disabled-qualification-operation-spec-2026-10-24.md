# Disabled qualification operation

Status: implementation specification. This operation closes a completed diagnostic plan for the current full policy. It does not change source declarations, registration, intake, market data, or the active plan.

## Closed plan

Keep schema version 2 and distinguish the disabled operation with the literal `operation: "disabled_qualification_probe"`. Its exact key set is:

```json
{
  "schemaVersion": 2,
  "operation": "disabled_qualification_probe",
  "marketSha256": "<sha256 of the exact current full contract>",
  "maxRequests": 0,
  "sources": []
}
```

Validation requires these five keys and exact types: integer schema version 2, the exact operation string, the current complete contract hash, integer request allowance zero, and an empty list of sources. Booleans do not count as integers. Missing or unknown operation, extra keys, stale policy, nonzero allowance, or any source row fails closed. Existing schema-1 plans and schema-2 `bounded_candidate_traversal` plans retain their current validators and behavior.

## Execution and retained report

The dispatcher selects this operation explicitly after the current committed-plan byte check. It must return before bounded traversal or generic probing. There is no fallback from an absent, empty, malformed, unknown, or stale plan.

The report records the operation, exact current policy hash, raw-plan content reference and hash, canonical plan hash, original start and check times, and the reservation context from the existing lease-bound budget. It contains no source rows, facts, model calls, source-check credits, or qualified sources. It records zero request allowance, zero reservations and zero reservation denials. The final outer deadline and UTC-day guard remains active and can mark the enclosing diagnostic denied.

This report shows only that the policy's qualification probe was explicitly disabled. It does not imply sources were checked, current, complete, accurate, qualified, or operationally collected. Normal source collection remains on its separate path and is not disabled by this operation.

## Verification

Use temporary contracts, plans, stores, clocks, and fetchers only. Prove the exact disabled plan emits a retained zero-request diagnostic with exact plan and policy bindings and never invokes transport. Reject unknown or missing operations, extra fields, stale hashes, boolean or nonzero allowances, and nonempty source lists. Verify current schema-1 and bounded schema-2 validation paths remain unchanged. Do not modify the live qualification plan, contract, source declarations, source state, or archive; do not issue requests or publish.
