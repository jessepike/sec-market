# Three start proofs for bounded candidate traversal

Status: exact provenance inputs for a future schema-2 `bounded_candidate_traversal` plan. No adapter binding is constructed here. The actual request plan, runtime, market contract and source registrations are unchanged.

Use the three `rows[].startProof` objects in `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/bounded-traversal-start-proof-plan-2026-10-24.json` once the final adapter helper supplies its independently derived proposed bindings. I recommend those objects unchanged because each retains the complete existing `qualification_observation` format and a literal canonical-root disclosure from an actual archived response.

## Exact origins

All three rows come from `ci/source-probe-runs/40069462824-1.json`, raw SHA-256 `e737f0436db33a783f3e583cb316865357017b4122d5a9c07474b160e89da4f7`, 109,959 bytes. That actual diagnostic ran on application `377043028e01301b3433790caddc7a7dd5aaebc5` under market policy `79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60`.

| Source | Actual origin | Zero-based result index | Literal canonical starting URL | Original fetch charge |
|---|---|---:|---|---:|
| `ping-identity:official:1` | `ping-page-4` | 0 | `https://press.pingidentity.com/news-releases` | 1,230 |
| `delinea:official:1` | `delinea-news-page-2` | 3 | `https://delinea.com/news` | 1,233 |
| `sonatype:official:1` | `sonatype-press-page-13` | 6 | `https://www.sonatype.com/press-releases` | 1,236 |

Each starting root is the sole canonical link inside its original HTML head. Those roots are disclosed by the bodies even though the actual requested URLs were paginated pages. No start URL is inferred by removing a path/query component or by inventing an endpoint.

The original source hashes below are canonical hashes of the exact candidate source objects in the authenticated original market contract. They are not hashes of proposed HTML declarations.

| Original candidate source | Canonical SHA-256 |
|---|---|
| Ping | `b38afb84403d53cadcda401c89b10a1f66ef57ec4e119466a89daea6cee3998e` |
| Delinea | `d6130aaaa8b1b04cb3324289c5befe7f76de687d297b3774b33629914babdee5` |
| Sonatype | `19596f68dcf01c09d6a043dc47cd67ebbde0bdc079b5a7b42cad057f518da17e` |

The original market object is `contracts/79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60.json`, 200,746 bytes. Its raw and canonical hashes both equal the pinned policy hash.

Every start proof carries the exact diagnostic record reference, prior target ID/index/row hash, original observation/body references, original fetch time, and prior raw/canonical plan hashes. The raw prior plan remains the immutable 11,388-byte object `objects/62385a674edf896b479dc4fb9330e3e269afcbdc0b6715dd44f9b18608adbf4f`; its canonical hash is `42bf79e9e0a7f8907dc47b50836ec0e826c3a7ec81c028b9ba72e3da42d98356`. Each proof uses `priorPlanReference`, with no nested raw-plan copy and no historical-policy descriptor. Original reservations remain alongside the proof in the evidence row; no unsupported extra field is inserted into `startProof`.

## Validation and limits

The existing original-policy and explicit-qualification replay functions validated each selected proof. That replay checks the original complete seven-row plan, raw/canonical plan bindings, exact row position/hash, source/supplier, successful exact request/final URL, body, original timestamps and runtime/day context. It also reconstructs all 125 original reservations, with consecutive charges 1,112 through 1,236. The source scope and the single canonical-root link were then checked independently from the retained body.

The frozen input archive is `/var/tmp/smp-pagination-probe-20261024/archive-21a4f7be/jessepike-sec-market-21a4f7be073d30cef4547e1bbafcfea413024c12`. Its manifest hash is `77a402e1335e23e7cb42a6c0bb7aecc841f1bec07684ecc9b70d5c1708b2c7eb`. All 35,148 manifest entries passed hash/size verification. A before/after seal of all 35,152 files, including metadata, confirms unchanged bytes, content hashes and modification times; both canonical seal hashes are `e917582dd0c64ee150e0a698978ae600adacbbc1a593cba43f0353af392842d0`. The JSON records the seal definition, selected immutable references and verifier hash.

This guarded read-only VM replay made no network, primary-source or model request and wrote no archive or actual state. Its only outputs are these two new documents. It does not validate a future adapter binding, prove a full traversal, renew any original observation time, create a reservation, qualify a source or earn daily intake. All three source registrations remain candidates, all 74 suppliers and 557 obligations remain, and the original 244/557 report is unchanged.

The JSON's `inputsSha256` is `b62f6ac8b4c9e21f825df32200ca2d40bbcbb8dbe3b7bf347522eb40c5055038`, computed over its canonical content with that field omitted. Its raw-file SHA-256 is `08a1a8efe24970f8d5fee41c2959819d06ceb32c0d7bafc9f52aec47d3b08717`.
