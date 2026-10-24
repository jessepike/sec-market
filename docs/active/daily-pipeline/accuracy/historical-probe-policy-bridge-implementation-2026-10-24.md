# Historical probe policy bridge implementation

The authorized repair is implemented in `web/scripts/pipeline/onboarding.py` and the existing
seven-target `contracts/source-qualification-probes.json`. Source registration, the market
contract, workflows, limits and original archive records are unchanged. This implementation
made no source or model request and performed no Git or publication action.

## Result

The current plan remains schema 1 with exactly its original four root fields and seven targets.
Its root market pin now names the actual current policy
`79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60`.
Each affected explicit historical proof contains the reviewed closed `historicalPolicyBridge` descriptor.
The validator authenticates the original full contract and requires exact whole-policy equality
after removing only the exact old/new D-112 `/version` and `/collection/mode` values. It also
derives and compares the source-specific semantic bridge. The whole-policy comparison uses
canonical hashes, so integer/float/Boolean type drift also fails. Candidate registrations stay candidates.

Independent review found that generic diagnostic proof does not replay the same completed-run
and reservation context as explicit qualification proof. The owner accepted the narrower guard:
differing-policy bridging now requires `qualification_observation` only. All seven real targets
already use that variant. Cross-policy generic evidence rejects before resolving a descriptor;
its existing same-policy behavior remains unchanged. The failed generic-record counterexample
has a regression proving zero requests, reservations or writes.

Every original diagnostic, prior plan, target row, observation, body, date, reservation, UTC-day
and runtime check runs against the selected original contract. The resolver returns exactly one
proof policy; individual guards do not accept alternate old/current hashes. Same-policy proofs
must omit the bridge and retain their prior validation output. A derived `historicalPolicyBridges`
summary is added only when a bridge was actually used. New execution still requires the normal
current-policy reservation context, pure whole-plan validation and acknowledged escrow before
the existing raw-plan write or any request.

The repaired plan's raw SHA-256 is
`6dc248c7a5fee6f96f872d97d87241a70de98bf7524298e9e7108951bbf6685d`;
its canonical SHA-256 is
`eccc8cd58af1ebea1bd0679973ba8b0a0d3bf37cbe47ba06b94a084faeae825e`.
Removing only the new descriptors and restoring the old root hash reconstructs the exact prior
raw plan `4aaa2f35c9804184dae97f0a461f48f506aeeb10d5f82ae93e339151276c05ef` and its canonical
hash `b2abf80563c2e3b36a542c9a15654b0e81f0842dca49ff6d48892f506d46f647`. All original nested
proof fields and embedded prior-plan strings are therefore unchanged.

## Verification

All runtime and tests ran in OrbStack. The focused qualification suite passed 32 tests,
the leased diagnostic suite passed 22, and persistent probe budgeting passed 15. New cases cover
explicit old-policy proof/counter/time preservation, root-only repinning rejection, missing and
unnecessary bridges, contract/reference/descriptor tampering, changed source and supplier policy,
schedule/model/publication changes, unrelated registry changes and original row/charge/time
contradictions. An invalid final target produces no request, reservation or raw-plan write.

Six fictional later execution generations use current-policy reservation contexts and keep
calls/documents unchanged. After the first bridged generation, later proofs use the same-policy
path and a single content-addressed prior-plan reference. All later plan sizes stay below 20 KB,
with less than 1 KB variation, and original historical record bytes stay exact.

The guarded actual replay is recorded in
`historical-probe-policy-bridge-replay-2026-10-24.json`. It authenticates all 31,075 manifest files
in the 9c archive, validates all seven real targets against their original full proof chains,
and retains identical content, file-mtime and directory-mtime fingerprints before and after.
The original contract reference is 200,737 bytes with raw and canonical hash
`de1932f7698d6b5ec86c23da52e77b1440c34d368e101c2aaabcbae6b39abfbe`. All seven old proofs still
name that original policy, original fetch times, original body hashes and original reservations.
The diagnostic's original ledger remains 641 fetches, 80 calls and 40 documents.

The replay denied network, model/subprocess and disk-mutation operations throughout validation.
It recorded zero denied attempts, source/model/publication calls, state/archive writes, source
qualifications, semantic admissions or credited source checks. The raw replay receipt and its
code/plan pins bind the inspected implementation. The final receipt SHA-256 is
`f25703821e90f49ada7c1134bb68a473673a535b8be0cd75327a8a6908f6d813`.
This validates reuse of historical disclosure
evidence only.
A new actual diagnostic remains separate, charged work; an earlier failed attempt remains history.
