# Retained audit rebinding implementation addendum

October 24, 2026. The existing owner request authorizes this normal coverage repair. This addendum
makes the implementation choices concrete before code changes. It does not change the market
contract, collection bounds, freshness, source registration, budgets or publication rules.

## Runtime changes

Add `retained_audit.py` for a process-local, read-only evidence index and shared document replay.
Index immutable sealed receipts and content-addressed coverage memberships once per store. Build
source/URL lookups and observation lookups once; recheck every chosen record through the store.
Register newly completed attempts in that in-memory index. Prefer the latest applicable
transport/proof and hold on a newer failed or mismatched check. Never search backward for a good
result after a newer contradictory result. Rebinding points directly to the original document
check; a receipt that merely copied an older binding cannot become a new origin.

Reconstruct predecessor inventory from anchored prior receipt manifests and pending inventories.
For a legacy audit head, require every retained URL to occur in that independently anchored
inventory. Current discovery, anchored predecessors and the receipt's full retained inventory
must join exactly. A raw cursor can add an unresolved obligation but cannot authenticate semantic
coverage or silently shrink the inventory. New receipts record explicit predecessor origin
references, so gate replay does not depend on a later mutable head.

The format migration uses a source-controlled registry of 188 exact legacy receipt digests from
the authenticated pre-cutover archive `9c8737cb4213f149f788b7ef1414921b8951bf0e`. Its archive
manifest is `cd9d84c67a70f11b72eeba25a012e3402a88b2d5a9c692f145c225b0a2c3418a`. Each entry binds
the contract, run, task, attempt, supplier and source, and an original seal or coverage membership.
The registry file's raw hash is fixed in runtime code:
`6fdf2884bbcc70962a0fc41622c5c862a61c31ed79bbf97b18cc193a843b4dce`.
Every legacy use resolves that original evidence again. Unknown unversioned receipts fail closed,
including a new receipt with both its proof fields and the run compatibility record removed.
This is a one-time format boundary, rather than a URL-specific coverage exception.

Before starting a new run's attempts, also write one immutable compatibility record listing that
run's eligible old origins. Repaired bounded receipts require the versioned inventory and binding
fields and an exact reference to this record. The marker cannot grant legacy eligibility; the
fixed migration registry is required independently. These records change the state format only,
not the contract hash or logical task inventory.

The engine writes the full inventory and predecessor references, replays retained documents,
appends exact original references, and keeps unresolved binding reasons explicit. New document
checks retain normal work and reservation rules. Only newly checked documents update audit
timestamps. Copied facts do not enter `newFactIds`. Failed or stale bindings retain the source
hold; genuine expired transport becomes bounded due work and cannot renew itself offline.

Reconciliation repeats origin, inventory, body/input, source/supplier/policy, candidate, accepted,
held, empty and exclusion checks even for incomplete repaired receipts. Existing historical
receipt paths retain compatibility. Repaired successful receipts must have the complete full
inventory, successful fresh discovery and fresh document observations. The same shared replay
function validates original semantic chains from incomplete predecessor tasks without importing
their task-level outcome.

Current discovery and current document validation also check the latest registered transport,
including failed later observations. Equal-time observations with different transport results
hold as ambiguous. Independently required inventory includes every known anchored predecessor
completed at or before the current attempt's start, including time ties. An incomplete-discovery
receipt cannot carry facts, held claims, new fact identifiers, document validations or retained
inventory authority. The public snapshot repeats this same replay before consuming claims.

The partial-fact release path uses the shared full-inventory proof for repaired receipts. This
allows an accepted retained document that disappeared from today's feed to be released from a
still-incomplete source only after its origin, inventory and semantic chain independently replay.

## Tests and offline acceptance

Add focused Python operations/CI tests for sealed and legacy coverage origins, copy-only origin
rejection, downgrade prevention, exact inventory/predecessor joins, proof/body/input/context and
disposition tampering, latest failed transport, stale boundaries, cache reuse, immutable cursors
and facts, no duplicate events, and partial-receipt replay. Run existing pipeline/CI suites in
OrbStack. Replay the pinned b9 archive through the actual new implementation using a guarded
read-only store and memory-only new receipt objects. Preserve complete content and mtime
fingerprints before and after. Report the actual retained subset and remaining 17-task gaps.

The scheduled daily cadence still cannot complete large histories under the existing per-source
selection and 30-hour observation rules. This implementation must report that limit rather than
turn stale historical proof into current source completeness.

## Recorded implementation checks

The focused suite contains 24 passing cases, including the independent review's dual-strip,
incomplete-discovery claim injection, later failed transport and equal-time counterexamples.
The compressed-input suite has 22 passing cases and the existing pipeline suite has 115.
Independent review separately reproduced all four failures and verified every migration entry
against the authenticated 9c archive: 94 coverage origins and 94 seals covering 43 suppliers.

The actual b9 and 9c archive replays each bind 24 documents within 9,914 full-inventory URLs,
leave 9,890 URLs pending and all 17 historical source tasks incomplete, and independently replay
four partial fact references. Coverage remains 244 of 557. Both runs use one process-local index
scan and make zero source requests, model calls, archive writes or denied-call attempts. Full
manifest verification and before/after content, file-mtime and directory-mtime fingerprints
confirm both archives remain unchanged. Source audit cursor times also remain unchanged.

The exact code pins, object references, per-task results and guards are recorded in
`retained-audit-rebinding-implementation-verification-2026-10-24.json` (b9) and
`retained-audit-rebinding-9c-verification-2026-10-24.json`. The reproducible entry point is
`ops/ci/replay_retained_audit.py`, run through OrbStack with the archive root and authenticated
manifest hash as arguments. It denies disk mutations, network and subprocess operations after
loading archive evidence; all new receipts and heads exist only in memory. These checks establish
mechanical replay behavior and do not admit new facts or establish a live collection result.
