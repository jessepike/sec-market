# Historical probe proof across the D-112 policy change

Status: proposed repair specification for review. No runtime, contract, plan, source registration,
state, archive or allowance changed. No source, network or model request was made for this review.

Implementation addendum: the owner of this work reviewed this specification and authorized the
repair on October 24. The implementation is confined to the qualification validator, the current
seven-target plan, focused qualification tests and scoped proof documents. No workflow or source
request is included. The implementation will keep same-policy validation output unchanged and
add a derived `historicalPolicyBridges` summary only when a historical bridge is actually used.

## Problem and recommendation

The committed qualification plan still names the original market policy
`de1932f7698d6b5ec86c23da52e77b1440c34d368e101c2aaabcbae6b39abfbe`. The active D-112 contract is
`79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60`. The current validator correctly
rejects that root plan before requests. Repinning only the root plan would still fail because
the historical diagnostic, reservation context and prior committed plan retain the old hash.
Those old hashes describe real historical execution and must remain unchanged.

I recommend a narrow, explicit historical-proof bridge on each affected proof. Keep the root
plan pinned to the actual current contract. Authenticate the original full contract and validate
the complete old proof under that original contract. Permit the bridge only when the entire
old and current policies differ in the exact two D-112 fields below. Keep every existing request,
disclosure, reservation, time and provenance check. This grants permission to reuse a literal
historical disclosure for a new diagnostic request; it grants no qualification or coverage.

## Verified policy boundary

Read-only inspection of the authenticated 9c archive found the original policy at
`state/contracts/de1932f7698d6b5ec86c23da52e77b1440c34d368e101c2aaabcbae6b39abfbe.json`.
Its raw length is 200,737 bytes; raw and canonical SHA-256 both equal the original policy hash.
The full current policy differs at exactly these paths:

| Path | Original value | Current value |
|---|---|---|
| `/version` | `market-daily-v1` | `market-daily-v2` |
| `/collection/mode` | `delta_with_retained_audit` | `daily_intake_with_separate_history` |

Every source and supplier record, registration flag, allowed host, alias, category, seed,
schedule, runtime, fetch/model/document limit, model/input rule and publication rule is equal.
`separation.bridge` independently succeeds for `ping-identity:official:1`, `delinea:official:1`
and `sonatype:official:1`. Candidate registration does not prevent that pure context comparison.
However, that existing helper deliberately excludes unrelated registry records. It is therefore
necessary but insufficient for this strictly D-112-only bridge. Compare the whole policies too.

## Smallest machine format

Preserve the existing root plan's four-field schema: `schemaVersion`, `marketSha256`,
`maxRequests` and `targets`. Keep schema version 1, seven exact targets and current-market
equality. Add only one optional, closed field named `historicalPolicyBridge` to the existing
`qualification_observation` proof variant only. Differing-policy generic
`diagnostic_observation` evidence is rejected even with a descriptor: its existing same-policy
checks do not independently replay the full completed-run and reservation context required for
a bridge. Same-policy generic behavior remains unchanged. Do not add the bridge to
`source_observation`, whose current verified-source join remains unchanged.

The field is required if the bound diagnostic's policy differs from the current policy, and
forbidden if its policy is already current. Its exact fields are:

```json
{
  "schemaVersion": 1,
  "transition": "d112-intake-history-separation",
  "originalContract": {
    "key": "contracts/de1932f7698d6b5ec86c23da52e77b1440c34d368e101c2aaabcbae6b39abfbe.json",
    "sha256": "de1932f7698d6b5ec86c23da52e77b1440c34d368e101c2aaabcbae6b39abfbe",
    "bytes": 200737
  },
  "originalContractSha256": "de1932f7698d6b5ec86c23da52e77b1440c34d368e101c2aaabcbae6b39abfbe",
  "currentContractSha256": "79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60",
  "semanticContextSha256": "841fede849ffbaf7b14d35ee36719970eb5ce62ece0a2b12a9dc7c62a2bf008f"
}
```

The example context is Ping's. Delinea's is
`866271eaf5cb1f232d21ea0bcd6142c05509eb1c8998ddd73ec2a4f88299f4ce`; Sonatype's is
`1856d455d96e6c881662b06bab7dcbaaeccf2885f02f8dd840faddc81a545ea5`.
These values must be independently derived and compared, not accepted as authored trust flags.
The reference is read-only and content/size checked. Require its exact
`contracts/<originalContractSha256>.json` key and raw digest, then parse/validate the full contract
and require its canonical digest to equal that same hash and the historical record's policy.
Missing original bytes fail before requests; never substitute the current contract.

The reference keeps future diagnostic generations bounded. Do not embed the full contract in
each of seven proofs, re-embed old plans, mutate the historical plan or manufacture an archive
object during pure validation. The old contract is already present in the state archive. The
existing raw-plan-reference rule continues to store each newly executed root plan exactly once
after the acknowledged escrow and pure validation.

## Independent validation and execution order

1. Validate the entire current root plan with its existing strict size, shape, seven-target,
   duplicate, current source/candidate/host and current policy checks. Its `marketSha256` must
   remain exactly the loaded current contract hash.
2. Load the exact hash/size-bound diagnostic record using the existing proof record reference.
   Preserve all main-branch/manual-run, run ID, checkpoint, completion, zero-model, zero-credit
   and zero-publication requirements. If its hash is current, take the existing same-policy path
   and reject any unnecessary historical bridge.
3. For a differing historical hash, require the closed bridge. Verify the original contract
   bytes and canonical identity. Require the precise old/new versions and modes above. Deep-copy
   both full contracts, remove only `/version` and `/collection/mode`, and require exact canonical
   hash equality. Ordinary Python equality is insufficient because it equates integer, float
   and Boolean values; those type changes must reject too.
   Reject additional missing fields, source/subject changes, source registration changes,
   reordered or added registries, schedule changes, changed limits or model/publication changes.
   No generic list of allowed old hashes or permissive `acceptLegacy` flag is allowed.
4. Derive `separation.bridge(original, current, target.sourceId)` and compare its three hash
   fields with the descriptor. Independently require the complete original source and subject
   supplier to equal the current ones; both candidate registrations stay candidates. This is
   a source- and subject-bound proof, not authority borrowed from another source or alias.
5. Select exactly one `proof_contract`: the verified original contract for historical evidence,
   otherwise the current contract. Historical bridging requires `qualification_observation`
   before loading its original contract. Run all existing historical diagnostic/explicit-proof
   validation against that contract. In particular, `_qualification_explicit_observation`
   must require the historical record, diagnostic summary, prior plan's original raw/canonical
   hashes and content, validated target projection, target row/hash/index, source join and
   reservation context to match the original policy. Use its original fetch/runtime limits.
   Never change a guard into “old hash or new hash” at each comparison, and never rewrite a
   historical hash to pass a current-policy comparison.
6. Preserve every existing full reservation inventory/charge interval, unchanged model/document
   counter, successful exact nonredirected observation, source/URL/body/time join, UTC-day,
   strict runtime and literal disclosure check. Current target URLs still pass the current
   source contract. Original source equality makes these two contexts agree without loosening
   either one. Failed, unreserved, paid-fallback, credited, ambiguous or altered old rows fail.
7. Complete pure validation of all seven targets before generic or explicit transport. Emit
   the existing validated target projection without adding unrecorded target fields. The
   `historicalPolicyBridge` is part of the new root proof and therefore part of its raw and
   canonical hashes. An optional derived top-level validation summary may list the original
   record and recomputed bridge per target; it must not alter the nested original plan/rows.
8. Only the normal existing execution path may make a request: current contract-bound persistent
   reservation context, shared lease, checkpoint, fetch-only escrow, UTC/runtime guards and
   expected-commit checks. Fresh observations/results name the current contract and their real
   new times. Old observations, failed attempts, hashes, reservations and dates remain intact.

There is no need to recursively repin the nested original plans. They remain authenticated
verbatim under their own original policy. Future proofs of a newly executed current-policy
diagnostic use the same-policy path; its original plan may contain the historical bridge as
part of its immutable proof bytes, without nesting another full old policy or raw plan.

## Focused implementation boundary after review

The expected small change is in `web/scripts/pipeline/onboarding.py`: one pure historical-policy
resolver, one additional closed proof field, and passing the selected original contract/source
to the existing old-receipt checks. `separation.py` can supply the existing subject context hash;
it must not be weakened for this task. The current root plan then receives the current market
pin and explicit bridges on its seven affected proofs. Old proof fields and raw prior-plan bytes
remain byte-for-byte unchanged. No collector workflow, source registration, allowance, freshness,
semantic admission or publication behavior needs a change.

## Required evidence and negative tests

Use fictional temporary stores for focused tests and an archive read-only adapter for actual
proof inspection. Before any actual source run:

- Preserve same-policy plan/receipt behavior and existing legacy raw-plan versus object-reference
  rules. An old root plan fails; merely changing its top policy also fails without the bridge.
- Accept the real seven historical targets only after authenticating the old full contract and
  deriving the exact two-field transition. Assert no old row, proof, date, reservation or raw
  plan changes, and zero source/model/archive-write activity during validation.
- Reject missing/forged/oversized contracts, wrong key/hash/size/canonical identity, substituted
  current bytes, unknown transition/version/mode, current-to-old reversal, unnecessary bridges,
  extra descriptor fields and a bridge belonging to another target/source/supplier.
- Mutate schedule/runtime/fetch/model/document limits, source registration/URL/hosts/class/family,
  supplier aliases/categories, an unrelated registry entry and publication rules one at a time.
  Every mutation rejects even where the more general `separation.bridge` alone would permit an
  unrelated registry change. Only the reviewed D-112 delta is allowed here.
- Reject a differing-policy generic diagnostic even with a valid descriptor and rehashed record.
  Include the reviewer's failed-run, paid-fallback, published, wrong-policy diagnostic and
  uncharged-reservation counterexample. Preserve same-policy generic behavior.
- Retain all existing moved-row, wrong-index, altered raw-plan/reference, body/time/source,
  redirect, failed terminal, incomplete/credited run, missing/duplicate/unreserved charge and
  wrong UTC-day/runtime counterexamples. An invalid final target causes zero requests and no
  raw-plan write.
- Execute multiple fictional later generations. Each records its actual current policy and a
  single raw-plan object reference; later plans stay bounded and do not duplicate full old
  contracts or grow a nested proof chain.

The failed diagnostic under the mismatched plan remains honest failure history. A later repaired
diagnostic still requires real charged requests and returns no source qualification, semantic
admission or coverage credit. This proposal authorizes none of those requests itself.
