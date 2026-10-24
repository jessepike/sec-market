# Bounded candidate parser V3 independent review

Verdict: clean within this parser, caller revision, candidate plan, and dormant origin scope after two V3-only URL fixes. I recommend the exact reviewed plan for a fresh leased diagnostic. Its actual responses must be replayed before any qualification review. This audit grants no registration, completeness, intake, semantic, or publication credit.

## Exact reviewed inputs

All four code hashes matched before and after the final sealed replay.

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/onboarding.py` | `76cb6dc13d487d00ba4ecadeddb7a4c08007a3e9944032bd9ea9be60f2e91af1` |
| `web/scripts/pipeline/discovery.py` | `2bd9650c36adb7b723acac1c2b87187cdf1b3bc8e4ff1f9b6c7e540a766154d5` |
| `web/scripts/pipeline/contracts.py` | `6ed3cc8aa7a8e826d96a8fe4db3758f170b7ffa4f44c68bbaf40beaf5c37476f` |
| `web/scripts/pipeline/source_qualification_origin.py` | `c3c060710dfda74eeda0bb180251e1e9fe2f77ca6ec04c1ddc14d8b666f98be2` |

The separate candidate plan at `docs/active/daily-pipeline/accuracy/bounded-parser-v3-candidate-plan-2026-10-24.json` passed full pure preflight against the authenticated archive. Its raw hash is `c4f70c5fdef811f15794c0c2c40fd5a20bdd652a13760523154d1210876f91a9`; its canonical hash is `5f345173b2c52b613d3776533eb2ec2d947eee4167ae4f5c74965391f9562bb1`. It explicitly selects integer revision 3 and the exact three source-bound V3 adapter hashes. The operational plan remained revision 2, raw `c6755ab3dd3bb491b24d2c5f791349b5f69682167ea381bbf9faefd9d8b479e5`, during this review. The market contract bytes remained `5b2b52dc2d17709f562b64ad6cb435086971ff8a6ccb9ce2fe95296a1ce1a7ff`.

## Actual historical replay

The final code replayed each entire original diagnostic report through `replay_bounded_candidate_diagnostic`, using its immutable original raw plan and original contract. The replayed report objects equalled the stored reports exactly.

| Actual run | Original record SHA-256 | Revision | Ping / Delinea / Sonatype retained items | Result |
|---|---|---:|---|---|
| `40072784799` | `a94e0e7f162fdc25269b14ac06a36e01e344d58883f0c9387c896cc087c11f51` | 1 | 170 / 96 / 32 | All incomplete. Original Ping heading failure and both original archive-path failures remain. |
| `40075237236` | `5e47181806b8b17cb68e717844903f08cdf3ba42d0fd86de19d218fe3d4f5212` | 2 | 200 / 204 / 96 | All incomplete. Original Ping and both archive-path failures remain. |

The V2 report's retained failure-page bytes parse under the proposed V3 adapters as follows. Original observation times and bytes remain unchanged.

| Original request URL and fetched time | Body SHA-256 | V3 cards / literal continuation |
|---|---|---|
| `https://press.pingidentity.com/news-releases?o=200`, `2026-10-24T07:46:02.113398Z` | `fb43c33de4629c766ac62e84895fa446e6d7d12513dfdaf6bb34fc7cff86cdef` | 10; `https://press.pingidentity.com/news-releases?o=210` |
| `https://delinea.com/news/page/18`, `2026-10-24T07:46:07.678527Z` | `e4b5201c4f21e94415f203717ccc2f3000d68852fdef1c627bed9b84adf7e791` | 12; `https://delinea.com/news/page/19` |
| `https://www.sonatype.com/press-releases?page=7`, `2026-10-24T07:46:10.653427Z` | `2e94dddf68d90a83fa76cb8bc264d5cb206ead4cf73a1358c2a884fc223ff7bf` | 16; `https://www.sonatype.com/press-releases?page=8` |

Every page above returns `terminalProved=false`. Each still fails under its original V2 parser. Delinea's parser continues to return an unproved terminal; no terminal layout or successful full traversal is inferred. The V3 primary path check preserves unknown date metadata rather than converting the route's date into source publication metadata.

## Counterexamples and resolved findings

The initial V3 code accepted reserved or numeric direct article slugs such as `/news/page` and `/press-releases/123`. It also accepted relative links with interior empty segments after `urljoin` collapsed them, such as `press-releases/foo//bar`. Both findings were sent to the parent and repaired only in V3. Final retests reject 15 reserved/numeric direct or historical terminal slugs, four relative empty-segment cases, and Ping relative dot, empty-segment, and protocol-relative cases. V1/V2 branches retain their original interpretation.

The final sealed check rejected 56 independently constructed mutations covering strict integer revisions and request limits, revision downgrade, wrong adapter hashes, cross-source mode tuples, altered sparse adapter context, unsafe route syntax, and the original V2 failure cases. Additional rehashed actual-report tests reject forged completion/terminal flags and qualification/credit flags. The three V3 candidate adapters still return `SOURCE_BINDING_UNVERIFIED` with zero transport calls through ordinary discovery.

The focused suites passed 40 tests in OrbStack: 11 caller/primary revision tests, 8 V3 archive tests, and 21 dormant origin tests. These cover valid calendar dates, card-date disagreement, source-bound modes, unsafe destinations, scoped primary readability/block detection, raw primary URL whitespace, and retention of fictional V1/V2 partial inventories through a V3 origin. The fictional origin tests establish code behavior only. `ACTIVATION_AUTHORITIES` remains empty.

An extra report-level `parserRevision` field is ignored metadata: adding `3` to a rehashed V2 report still selects revision 2 from its original immutable raw plan. It cannot select V3 or grant credit. The historical replay API checks internal evidence joins; external run authenticity remains a separate fixed-authority requirement for any future activation.

## Read-only archive proof and remaining boundary

The final replay authenticated all 35,412 manifest entries under `/var/tmp/smp-bounded-v2-probe-20261024/archive-d161a23d/jessepike-sec-market-d161a23d80ea9e1756113644624cc2f646d2c3ed`. Manifest SHA-256 is `09909886e98bd9f6be1ebe8da243f80b8af73352889a989a2093b96e89c92362`. All 35,416 files and 1,320 directories had identical before/after seals:

| Seal | SHA-256 |
|---|---|
| File content | `ceadeaa57d7a3b37e695ca57359211533e61e5ca9419542833cedc068faedace` |
| File modification times | `f50fc5ddae221be1bbe8bcb1c536669ad564a731d1996058ab1c445fc1001de3` |
| Directory modification times | `109a79c2199558ec1c4cba1eb615e16d0d888b58ad8cd02026ef7388678b7789` |

The sealed pass blocked network, subprocess, and disk mutation attempts; no blocked attempt occurred. This audit made zero source/model requests and zero actual state/archive writes. The 74 suppliers and 557 obligations remain unchanged. Future activation still requires authenticated complete traversal, all earlier in-scope literal inventory evidence, the closed policy transition, preserved normal inventory and claim/hold continuity, and its separately reviewed authority entry.
