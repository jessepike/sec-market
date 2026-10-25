# SentinelOne filing transport implementation

October 25, 2026. Future-preview repair under `s1-exact-filing-transport-spec-2026-10-25.md`.

The implementation accepts an optional `source.transportAttestation` only when its complete
versioned tuple equals the specified SentinelOne identity. It pins the configured source,
immutable evidence, request/canonical URL, actual final URL and 49,404-byte body. Every field is
required; extra fields fail. No URL normalization occurs. The complete rule and attestation enter
only the using group's review-policy hash. The global review-rules version remains unchanged.

The attested runtime checks exact observation/source/request/final/body/time joins and successful
HTTP status pairs. A 304 must retain a valid, chronological reuse chain ending at a real 200 for
the same exact tuple. It rejects cycles, missing or changed predecessors and transport-cache reuse.
The existing complete decoding, freshness, document limit, literal excerpt and independent
subscription-review/admission checks remain in force. A source without the attestation retains
the original exact final-URL requirement.

## Changed files

* `/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/corrections.py`
* `/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/verify-factual-corrections.mjs`
* `/Users/jessepike/code/projects/sec-market-finish-20261022/ops/ci/test_s1_exact_filing_transport.py`
* `/Users/jessepike/code/projects/sec-market-finish-20261022/ops/ci/fixtures/s1-exact-filing-transport.json`
* `/Users/jessepike/code/projects/sec-market-finish-20261022/web/tests/s1-exact-filing-transport.test.mjs`
* This handback file.

The fixture copies the exact proposed SentinelOne group from
`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/remaining-event-admission-readiness-2026-10-25.json`
and adds the proposed optional attestation. It is test material; it grants no admission.

## Verification

All runtimes, tests, builds and screenshots ran in OrbStack `dev`. No packages were installed.

| Check | Result |
|---|---|
| Focused Python transport tests | 10 passed. |
| Focused JavaScript transport and existing correction-build tests | 24 passed. |
| Python/JavaScript parity | The same policy hashes or rejections across 80 cases; 8 accepted shapes and 72 rejected mutations. |
| Full operational suite | `python3 -B -m unittest discover -s ops/ci`: 828 passed. |
| Full `npm test` | Lint, 377 data tests, 115 pipeline tests, gated build and 42 browser tests passed; one existing fixture-dependent browser test skipped. |
| Whitespace check | `git diff --check` passed. |

The actual archive was read through a `read/get` adapter that has no write methods or LocalStore
initialization. Its manifest pin is
`895213b31bb9f75814acc9484cad9aabd3719e07ddd72c621275a9b2568a1e5c`.
Every selected read checked manifest hash and size; touched bytes and modification times remained
unchanged. The actual latest 304 observation
`a32b2e55b927c37ffd4e5ab9c2e31a242f9b311c01f47651566c421c13bdbe14`
replayed its eight-observation chain through the original 200
`eafc5bf53cc59e4b0cb49f78039670ce6cff0baff0417b91eb465bf05cc533ab`.
The 200 was tested at its original October 20 observation clock; the 304 at its original October 24
clock. Neither was relabelled as a new response. All six actual prior admissions replayed unchanged.

Mutation tests reject altered identities, pins, body, observation joins, missing/extra fields,
request/final reversal, and nearby scheme, host, port, issuer, accession, filename, query, fragment,
encoding and traversal spellings. They also retain stale/future, complete-body and literal-excerpt
rejections. Temporary contract copies exercise the optional schema without changing operational files.

## Existing policy hashes

| Group | Unchanged review-policy SHA-256 |
|---|---|
| `FC-20261023-checkpoint-sase` | `36bc23722c1131f94ab3c2db1c553505539987aa55738cfa9bb72dfa3871ad6f` |
| `FC-20261023-optiv` | `4f9e7feb90232a3aafe2cd84265c2e8202c9e009229e7592c5ab87373f64bcf5` |
| `FC-20261023-splunk` | `270b7c7a1f7180b3fef2896b7633a87bf0667b9f4a3c75593fa72b959ecb87f6` |
| `FC-20261023-zscaler` | `dc8522069fc87cbf0371e0ea29ec80fbf647c1dd7ce816e02a7fb4a94b35a390` |
| `FC-20261023-expel` | `d1ea72b754450e603d89092cc38d9fa81d165575af2a36745e5938220fd82087` |
| `XAGE-SOURCE-CLASS-20261023` | `c01560dba484aa5aa5696c8bfe5b44acefc6337ee1cebe0cd96751849e15646a` |

## Render evidence

Full-page production and current local-build screenshots were captured with `web/scripts/shot.mjs`
at 1440 and 390 pixels. Local used its own port 18814. Both local images exactly match the preceding
`http-status-local` images: zero changed pixels at 1440×8379 and 390×7749. This repair is invisible.
Production and local remain separate fixtures with the previously accepted policy/data differences.

Images and test logs are under
`/Users/jessepike/Documents/Codex/2026-10-22/security-market-pulse/renewal-20261024/`:

* `s1-transport-production-1440.png` and `s1-transport-production-390.png`.
* `s1-transport-local-1440.png` and `s1-transport-local-390.png`.
* `s1-transport-visual-comparison.json` records dimensions, pixel comparisons and screenshot hashes.
* `s1-transport-ops-tests.log` and `s1-transport-web-tests.log` retain full check output.

No operational contract, build stamp, admission, source policy, workflow or retained archive was
changed by this repair. No commit, push, new source/model request, admission, qualification credit
or production promotion occurred. Screenshot navigation used ordinary production browser requests.
Main remains outside this change. The unsupported Varonis wording and other pending source/record
work remain separate. There is no implementation blocker. I recommend independent review before
landing the inactive repair on preview; any future group still needs its own admission.
