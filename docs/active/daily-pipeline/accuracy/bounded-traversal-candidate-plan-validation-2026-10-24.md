# Schema-2 candidate plan validation

The separate candidate plan is `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/bounded-traversal-candidate-plan-2026-10-24.json`. It passes the actual whole-plan validator against the authenticated original archive. It has not replaced the committed request plan or been executed.

The closed schema has `schemaVersion=2`, `operation=bounded_candidate_traversal`, current `marketSha256=79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60`, `maxRequests=183`, `maxIndexPagesPerSource=60`, `primarySamplesPerSource=1`, and the three ordered source rows. Each row contains only `sourceId`, `originalSourceSha256`, `proposedAdapterSha256` and `startProof`.

The proposed adapter hashes were computed solely by the actual `onboarding._candidate_adapter(source, index_url, mode)` helper and checked again against `onboarding.validate_qualification_probe_plan`. The helper changes the proposed kind, index URL and completeness mode while preserving candidate registration. No proposed verified declaration was invented.

| Source | Helper-derived proposed adapter SHA-256 |
|---|---|
| `ping-identity:official:1` | `475a96547adb246a83441b5db4e111d51c06e352ea469d6efbfed0b7d453a333` |
| `delinea:official:1` | `605e9e414b650c1fd21e2fba45b41968c37a0367cf4961c72decb3d57b647804` |
| `sonatype:official:1` | `9dfc1759b75c07838be019189d46a1b3c354e680d4359ac346356691d1e01d7f` |

The exact three start proofs are unchanged from `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/bounded-traversal-start-proof-plan-2026-10-24.json`. They retain actual diagnostic `40069462824-1` result indexes 0, 3 and 6, each original row hash, observation/body/time/charge join, and immutable prior-plan object `62385a674edf896b479dc4fb9330e3e269afcbdc0b6715dd44f9b18608adbf4f`. There are no historical-policy descriptors or nested raw-plan copies.

## Exact validation receipt

| Item | Result |
|---|---|
| Candidate raw bytes | 5,315 bytes; SHA-256 `fd0ab3821699d577782754cfb1ddc7ba7e4d4f9c2a7c6fd626d4b1f12c6644f7`. |
| Candidate canonical content | SHA-256 `7cf3f9b2e3314c930ca5d8c482551fc015fbe4a819f151df9f1dc42f333488e1`. |
| Actual helper/validator module snapshot | `/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/onboarding.py`, 92,402 bytes; SHA-256 `949abd1d5990fc513c29ca65df20310710bf821606694d06948038d4bb736c33`, unchanged during replay. |
| Original archive | `/var/tmp/smp-pagination-probe-20261024/archive-21a4f7be/jessepike-sec-market-21a4f7be073d30cef4547e1bbafcfea413024c12`. |
| Manifest | All 35,148 entries pass hash/size verification; manifest SHA-256 `77a402e1335e23e7cb42a6c0bb7aecc841f1bec07684ecc9b70d5c1708b2c7eb`. |
| Complete before/after seal | All 35,152 files preserve bytes, content hashes and modification times. Both canonical relative-path `{sha256,bytes,mtimeNs}` map hashes are `e917582dd0c64ee150e0a698978ae600adacbbc1a593cba43f0353af392842d0`. |
| Referenced immutable objects | Eight exact references; canonical key-to-reference inventory SHA-256 `eab0ea4d7ae639683e190c4068cabd367d558e778ca8598f1153d771f3379d45`. |
| Existing committed request plan | Raw SHA-256 remains `62385a674edf896b479dc4fb9330e3e269afcbdc0b6715dd44f9b18608adbf4f`, byte-for-byte unchanged. |

The whole-plan validator rejected all 11 in-memory negative cases: a missing source, reordered sources, wrong policy, expanded request cap, boolean sample cap, wrong original source hash, wrong adapter hash, wrong original result index, retimestamped observation, nested raw-plan fallback, and an added source field purporting to verify registration. These were deterministic validation checks, with no actual workflow or source execution.

An audit hook denied writes, filesystem mutations, network and subprocess creation during full archive verification and plan validation. No source request, model call, actual state write or archive write occurred. Only the new candidate file and this note were written. All three registrations remain candidates, all 74 suppliers and 557 obligations remain, and coverage/qualification/semantic credit is zero. Independent caller and candidate review is pending; root owns any later installation, activation or actual leased run.
