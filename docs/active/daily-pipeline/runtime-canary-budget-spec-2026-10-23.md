# Read-only runtime canary

Date: 2026-10-23. Scope: close the runtime canary's unreserved market-source request while preserving its existing hosting/archive check.

## Contract

The previous canary fetched one SEC company-facts source directly after restoring the archive. That request bypassed the shared lease and persistent fetch ledger, including when the day's fetch allowance was already exhausted. Existing historical receipts truthfully describe those requests and remain unchanged. This repair does not refund or backfill the ledger.

The canary now verifies actual private GitHub Actions context, the checked-out revision, and the existing `GitArchive.restore` manifest/body verification. It validates the current source contract, reads the exact hash-bound archived coverage object, checks its deterministic task plan and exact archived attempt inventory, and preserves its historical coverage time and verdict. This is archive/contract consistency, without fresh source or semantic revalidation. It uses no transport, account/model client, lease, budget reservation, archive push, collection checkpoint or snapshot write. The copied state stays byte-identical after restore.

Success means `runtimeCanaryScope: private_hosting_archive_integrity` and `runtimeCanaryPassed: true`. Every success and failure receipt explicitly carries `sourceProbe: {performed: false, reason: LEASED_COLLECTOR_WORKFLOW_REQUIRED}`, `marketSourceRequests: 0`, `sourceChecksCredited: 0`, `qualifiedSources: 0`, `coverageCredit: false`, `semanticAdmission: false`, and zero model calls. It makes no source-connectivity claim. `archivedCoverage` retains its original `checkedAt` and is marked historical. Missing coverage, a mismatched contract, changed task inventory/attempts, failed archive integrity, or an invalid private hosting context fails the canary honestly. Failure text remains a fixed local category.

Actual market-source diagnostics use the existing collector workflow's guarded manual `source_probe` mode, as specified in [leased-source-probe-spec-2026-10-23.md](leased-source-probe-spec-2026-10-23.md). This repair changes only the canary and its workflow wording. It creates no new workflow, service, secret or publication path.

## Tests

OrbStack tests build fictional local manifests and use the real archive verify/restore path with mocked remote opening. They prove a fully charged 5,500/80/40 ledger starts zero source requests, every restored file stays byte-identical, no archive push/state write/model work occurs, partial historical coverage can pass hosting integrity without earning coverage, and missing coverage/contract mismatch/corrupt body/failed restore fail. They also check failure receipts cannot imply successful source connectivity and preserve the workflow's read-only permission scope. No actual network, GitHub request, source fetch, archive mutation, model call or workflow dispatch is authorized by the tests.

The candidate passed all 15 focused canary tests and all 430 operational tests in OrbStack. Historical canary receipts were not edited. No live canary or workflow was run for this verification.
