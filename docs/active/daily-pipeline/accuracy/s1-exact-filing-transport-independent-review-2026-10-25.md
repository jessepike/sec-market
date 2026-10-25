# Independent review: exact SentinelOne filing transport

Date: October 25, 2026. Verdict: **pass for the specified dormant preview support**. Two review passes found no material or minor issue. This review does not admit the proposed correction or authorize moving frozen main `6d5e87feba4ffbc75e50f35cb564cb8fd91708ca` before scheduled H collection and public acceptance.

## Scope and result

The first pass compared the implementation with `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/s1-exact-filing-transport-spec-2026-10-25.md`, checked the complete diff and followed Python admission and JavaScript build bindings. The second pass ran focused tests and independent mutations against the actual retained archive. The reviewer changed only this review and its companion receipt. Implementation, contracts, policy stamps, source archive, budgets, Git refs and the Git index were not modified by the reviewer.

Python `_transport_attestation` accepts only the complete, exact descriptor and exact source shape. The tuple binds supplier `s1`, source `s1:citation:TR-s1-3`, evidence `TR-s1-3`, their pinned configured-source and immutable-evidence digests, the original padded request/canonical URL, the one unpadded final URL, and the exact 49,404-byte filing body. `load_policy` still checks verified source registration, supplier membership and the original canonical citation. There is no general URL normalization or additional transport permission.

`validate_sources` keeps the exact requested URL and all existing observation, body, time, freshness, complete-document and literal-excerpt checks. The final URL exception requires the explicit attestation. `_transport_reuse` reconstructs the actual 304 chain to a full 200 origin, binding every node's ID, source, request, final URL and body and requiring non-increasing original fetch times. It rejects cycles, missing predecessors, status mismatches and transport-reused observations. A real 304 remains a revalidation of the retained bytes, not a newly downloaded body.

Python and JavaScript contain the same closed descriptor and add `sourceTransportRules` only when an attestation is present. The descriptor is also in the group/evidence-set hashes. The global review-rules version is unchanged. JavaScript independently checks the request-side descriptor, configured source and immutable evidence. Python remains responsible for replaying actual archived observations; the public projector receives no new URL equivalence rule.

## Actual evidence and preservation

The retained chain has eight observations. Its latest observation is `a32b2e55b927c37ffd4e5ab9c2e31a242f9b311c01f47651566c421c13bdbe14`, HTTP 304, fetched `2026-10-24T18:30:00.677520Z`. Its full-body origin is `eafc5bf53cc59e4b0cb49f78039670ce6cff0baff0417b91eb465bf05cc533ab`, HTTP 200, fetched `2026-10-20T21:11:29.566045Z`. Every node retains the exact request/final pair and body SHA-256 `e9cc9fc8a899fc7367c173837291a7f8f27d0adad52f81e5adf9dfdf04b04b78`.

The body identifies CIK `0001583708`, registrant `SENTINELONE, INC.`, Form 8-K and report date May 28, 2026. Both original 200 and current 304 validate at their own original clocks; the 30-hour boundary passes and older/future admission times fail.

All six committed group review-policy hashes still match the unchanged stamp. All six actual accepted admissions replay from the archive with their immutable bytes unchanged. H, the operational correction requests, original inventories, baseline and policy stamp kept identical hash, size and modification time during the independent checks. The 45 consulted archive files also kept identical hash, size and modification time. Their touched-file preservation seal is `83577c5ace69bc4adeba87e18a778bf857ef199a605b0623cbe8e2c00d9ac368`. This is a seal of consulted files, not a claim that this review reauthenticated every archive entry.

## Focused verification

Executed in OrbStack dev with bytecode writes disabled:

* `python3 -B -m unittest discover -s ops/ci -p test_s1_exact_filing_transport.py -v`: **10 passed, zero skipped**.
* `node --test web/tests/s1-exact-filing-transport.test.mjs`: **4 passed, zero skipped**, including cross-runtime policy agreement for valid and rejected cases.
* Independent in-memory replay: **71 mutations rejected**, plus **eight positive, boundary and historical checks passed**. This covered omission of every source field; request/final/source/ID/time/reuse mutation at every chain position; and additional trailing slash, path case, double slash, empty query/fragment, host trailing dot, user information and alternate port spellings. The supplied tests additionally cover changed issuer/accession/filename, encoding, traversal, reversal, attestation fields, immutable evidence, body corruption, stale/future clocks and the missing-attestation failure.

Network was denied during the independent mutation replay. It constructed no LocalStore, reserved no budget, made no source/model request and wrote no archive object. Synthetic overlays existed only in memory. Full operational/web suites and rendering remain the implementation worker's separate evidence and are not counted here.

## Reviewed file pins

| File, relative to `/Users/jessepike/code/projects/sec-market-finish-20261022/` | SHA-256 |
|---|---|
| `web/scripts/pipeline/corrections.py` | `d742a91d4d23da5db3b426afcef76a80971c47dd54f8e4312065a6994f87b11f` |
| `web/scripts/verify-factual-corrections.mjs` | `386093e726ccf9c2bdbe0b9115885ad74360e2c7cd81577554f335e9ee4f2f06` |
| `ops/ci/test_s1_exact_filing_transport.py` | `a0b04d59fde295e452ac8d1d892f1455d55843510237ef74ce823488a6b81450` |
| `web/tests/s1-exact-filing-transport.test.mjs` | `be7c2f23767d4799e9dfde2ce509bc045386ecca443e980c09ec0550a83d28ba` |
| `ops/ci/fixtures/s1-exact-filing-transport.json` | `8d6584024b7caa44189968afb41132f795671fffc1ecc187e9030f1e903abb0e` |
| `docs/active/daily-pipeline/accuracy/s1-exact-filing-transport-spec-2026-10-25.md` | `2de15c5d35ad3a5e9da306bf27589db1f5730a79bc612b26a0c7fcce7365398d` |

## Issue log and next boundary

No findings. No code fix was made. I would retain this narrow implementation for the reviewed preview path because it resolves the demonstrated identity mismatch while preserving all other joins. Operational correction activation still needs the exact new groups, outer stamp, actual independent admissions and the existing gated release. The six existing groups, H and the main acceptance freeze remain in force.
