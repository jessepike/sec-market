# Immutable qualification-plan replay

Status: implementation specification for read-only historical replay of the schema-2 bounded candidate diagnostic. This interface preserves original evidence after the live plan changes. It does not authorize a source request, source registration, intake, semantic admission, or coverage credit.

## Entry point

Add `replay_bounded_candidate_diagnostic(original_contract, store, run_record_reference, raw_plan_reference)` in `web/scripts/pipeline/onboarding.py`. It returns the validated historical plan and its independently replayed diagnostic report. The caller must supply the full original contract and an authenticated immutable run-record reference. It may use only the exact plan reference carried by that record's diagnostic.

The function reads the run record through the existing immutable-store reference mechanism and requires its key to match `ci/source-probe-runs/<run>-<attempt>.json`. It checks the record's run ID and attempt against the key, the `source_probe` checkpoint, current-for-that-record contract hash, main-branch `workflow_dispatch` envelope, app revision, non-publication state, and exact zero-credit fields. The report is the record's `diagnostic` object. The passed plan reference must equal `diagnostic.planReference` exactly.

The function loads the raw plan bytes only from that reference, verifies its content hash and byte count, requires the closed schema-2 `bounded_candidate_traversal` shape, and invokes the existing strict three-source plan validator under the supplied original contract. It then replays the report bodies, source-bound observation wrappers, parser outputs, timestamps, sample choices, denial records, and reservation interval against those exact plan bytes. This historical path has no live filesystem plan path and cannot accept an alternate authored plan.

## Validation boundary

Historical replay may return a valid but incomplete traversal. It preserves the original time and partial inventory and reports the validated plan and report as historical evidence. It also accepts the collector's explicit final deadline/UTC-day guard when the authenticated run record contains that unreserved denial and the timing and reservation-context totals reconcile. The caller that evaluates origin eligibility decides whether the replay is complete enough for its separate purpose. Historical replay itself never changes a source declaration or labels a source verified.

The live execution verifier remains stricter about its current plan path: it must confirm that the committed plan file still has the exact raw bytes whose hash was validated before the operation. Do not add a flag that disables this live equality check. The historical entry point is a separate function and shares the receipt-replay core only after it has loaded the raw bytes from the authenticated record's exact reference.

The API accepts the original full contract as context, then binds it to the run record, diagnostic, reservation context, and plan hashes. It does not accept a source row, candidate declaration, adapter, or current policy override as a substitute. The caller remains responsible for authenticating the run record's external Actions provenance; this function rechecks its archive reference and internal run envelope.

## Scope and verification

Changes are limited to `onboarding.py`, focused historical replay tests, and this specification. Do not edit the current market contract, source declarations, active qualification plan, parser, retained-audit integration, or source/runtime state. Tests use temporary immutable stores and synthetic records only. Include valid complete and incomplete historical receipts, changed live plan contents with unchanged historical replay, and rejection of plan-reference, run-envelope, contract, observation-wrapper, body, time, and reservation tampering. No source fetch, store mutation outside disposable test stores, publication, workflow dispatch, or model request is part of this unit.
