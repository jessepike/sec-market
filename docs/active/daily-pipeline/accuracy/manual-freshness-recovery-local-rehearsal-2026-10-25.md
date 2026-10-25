# Manual freshness recovery: local release rehearsal

The complete local release rehearsal passed against actual manual recovery `40169973257` using
exact main `6d5e87feba4ffbc75e50f35cb564cb8fd91708ca`. It passed 531 release tests, the actual
public-source JavaScript validator and 805 operational tests. This is local proof and consumes
none of the remaining external gate allowance.

## Inputs and isolation

| Input | Exact value |
|---|---|
| Application revision | `6d5e87feba4ffbc75e50f35cb564cb8fd91708ca` |
| Authenticated archive commit | `a50c594fb8142cee8d667b4da7161a4d48620c11` |
| Archive manifest SHA-256 | `540bb0449b922b0ea69ab3a088d35b0f3bc8926243a8d5c817ab93c2659abd8e` |
| Manifest entries checked | 45,259, each checked again for hash and size. |
| Actual collection run | `d1b5cbbf41ba2d8dfcb05a7ff2a2b00b7faada68dcaf3224ad4c7702b2d63b22` |
| Actual collection receipt | `f2486a623d93da011eaaf11926e09d6ce1533dab26d4a8f2fa2875a95a84d0b6` |

Frozen source:
`/var/tmp/smp-manual-freshness-recovery-40169973257-20261025/extracted` in OrbStack `dev`.

The isolated application came from `git archive` of that exact main revision. No future-preview
code was copied in. Its engine, collector and snapshot module hashes match the corresponding
main Git objects. Existing installed dependencies were linked into the isolated application;
no package was installed. Application build commands ran in:
`/var/tmp/smp-manual-freshness-full-gate-40169973257-20261025/application`.

The gate used a memory-only overlay over frozen evidence. It never initialized LocalStore on
the frozen archive. Eleven new local object writes remained in memory. Full-tree content,
file modification-time and directory modification-time seals match before and after across
45,263 files, including the manifest and auxiliary files, and 2,475 directories. Existing
rehearsals and application servers were untouched; browser tests used a separate local port 18816.

## Checks

| Check | Result |
|---|---|
| `refresh:edgar` | Passed using only retained authenticated SEC responses. |
| `refresh:filing-events` | Passed using only retained authenticated SEC responses. |
| `certify:sec` | Passed, all 80 required claims. |
| Full `npm test` | Passed lint, 373 data tests, 115 pipeline tests, complete gated release build and all 43 browser tests. No browser skip. |
| Direct `verifyDaily` JavaScript replay | Passed against the actual rebuilt recovery snapshot and public source inventory. |
| Exact-main operational suite | 805 tests passed. |

The release count is derived from the command output: 373 + 115 + 43 = 531. It is not copied
from the earlier rehearsal. SEC cache hooks validate source byte hashes and actual source ages.
The Python harness denies external socket work and frozen-archive mutation; child Node processes
also carried an external-socket guard. No source, account, model or external release request ran.

The previous production acknowledgement was replayed from its authentic retained accepted
release instead of requesting the live deployment. That is an explicit offline substitution.
The local gate output uses run ID zero and carries no GitHub gate or publication authority.

## Preserved actual state

| Measure | Rebuilt result |
|---|---|
| Source intake | 264/557. |
| Processing | 38/10,655 reviewed, 10 held, 10,617 pending. |
| Historical review | 39/10,655 reviewed, 10 held, 10,616 pending. |
| Original source expiry | `2026-10-26T12:45:29.479727+00:00`, unchanged. |
| Review queue | All 37 entries match the collector exactly. |
| Current fact provenance | All four references match exactly. |
| Supplier updates and dates | Match exactly. |
| Existing corrections | All six dated rows and admissions match the retained published artifact exactly. |
| Gate budget | Still one attempt spent out of two. |
| Source budget | Still 72/80 calls, 33/40 documents and 444/5,500 fetches. |

The collector holds eight event records. Main correctly projects four current-policy events
and keeps four older records in `pendingFacts` awaiting current-policy review. The audit checks
every original event, evidence record, economic date and source retrieval clock byte-for-byte
in its appropriate destination. The older records cover Mimecast on October 1, 2024; eSentire
on March 19 and September 15, 2026; and Veeam on July 9, 2026.

The initial harness required all eight collector events directly in the public projection and
therefore exited after the gate had passed. A separate post-audit verified the intended four-public,
four-pending partition and passed. The original harness log is retained. No gate code, source
input, date or admission was changed to pass that audit, and no gate command needed repeating.

## Receipts

Saved evidence:
`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/receipts/manual-freshness-recovery-local-rehearsal-2026-10-25/`.

The directory contains the manifest, local gate result, complete post-audit summary, original
harness log, post-audit output, direct public validator output, SEC check logs, operational test
log and compressed full release test log. The manifest hashes each saved file. The isolated
build archive and full snapshot remain under the new OrbStack gate-output directory.

| Local output | SHA-256 |
|---|---|
| Rebuilt snapshot bytes | `efda90573d12a78b02ae53d623b67a03a9639c7c26c8e3986bd321c7e0dc4e55` |
| Tested static artifact inventory | `881736ed03b9f077ef5e81825f17505e803fe262b92ee4e5bae3f4ff2a8ddbaa` |

There is no local compiler or source-fixture blocker. I recommend proceeding to the separately
authorized external gate for this actual archive. This rehearsal grants no external gate,
scheduled-cycle or production credit. It made no commit, push, main, contract, status, admission,
budget or publication change.
