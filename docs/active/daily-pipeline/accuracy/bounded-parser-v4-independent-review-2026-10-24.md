# Bounded candidate parser V4 independent review

Verdict: clean within the reviewed V4 parser, revision selection, candidate plan, and dormant origin scope after the sparse-adapter omission was repaired. I recommend the exact candidate plan for a fresh leased diagnostic. No new complete traversal, source qualification, intake, semantic admission, registration, or publication follows from this offline review.

## Reviewed pins

The final sealed pass checked these hashes before and after replay.

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/discovery.py` | `c1e1e58b9f4901f52c403aa4b047dec554301eaf9b56783f337d20a8f736eca4` |
| `web/scripts/pipeline/contracts.py` | `83ccf3dd6b1d93e4106899cc3c99a184a0fc7d46c8e3e849cefa2921b83c7089` |
| `web/scripts/pipeline/onboarding.py` | `61ea8ed1f9fa81bbf43346dcede0a776e5b1b255768f70cf2a24274a719de770` |
| `web/scripts/pipeline/source_qualification_origin.py` | `c57e88f2e40fc69bee9bc94411ccd5e1a8acc99a2f211a9ee8e948cab88cd15b` |
| `ops/ci/test_source_qualification_origin.py` | `62fcd1fc9e08bd6bf20b3868188ce4558780abc32a19c272ddbbccb2e9b25596` |

`docs/active/daily-pipeline/accuracy/bounded-parser-v4-candidate-plan-2026-10-24.json` passed full preflight against the authenticated c112 archive. Raw SHA-256 is `0353ec8ef62fedd09758cc44b1fcbe80bbe713e996432a3684f524acd66c6c55`; canonical SHA-256 is `2e4ade663b1a76386c44e4150f310da72b6ff1ce632f5a685c7bdf2ea5f2f917`. Explicit integer revision 4 binds Ping V3, Delinea V4, and Sonatype V4. Primary revision 4 reuses revision 3, including its raw URL, scoped readability, metadata, and block checks. The operational plan remained V3 during this review.

## Actual old reports remain exact

The final code replayed each entire original diagnostic report through its own immutable raw plan and original contract. All report objects matched exactly, including original primary shapes, failure reasons, dates, inventory, and completion fields.

| Actual run | Original record SHA-256 | Revision | Ping / Delinea / Sonatype inventory | Index completion |
|---|---|---:|---|---|
| `40072784799` | `a94e0e7f162fdc25269b14ac06a36e01e344d58883f0c9387c896cc087c11f51` | 1 | 170 / 96 / 32 | All incomplete. |
| `40075237236` | `5e47181806b8b17cb68e717844903f08cdf3ba42d0fd86de19d218fe3d4f5212` | 2 | 200 / 204 / 96 | All incomplete. |
| `40077375424` | `af8f63ecf77ffa2ea00fdbc062661ddda3340b776d0ec7afdcda00048373cbb0` | 3 | 242 / 240 / 112 | Ping complete; Delinea and Sonatype incomplete. |

Ping's original V3 25-page, 242-URL complete result remains unchanged. V4 introduces no Ping parser mode or terminal rule.

## Retained V3 pages under V4

| Original body and observation | V4 result |
|---|---|
| Delinea `https://delinea.com/news/page/21`, fetched `2026-10-24T08:19:08.905115Z`; body `2d71b1e6366129e1ca17c9436764e4091d5d1a91c44bdf073cf5ad72f664dc28` | 12 recognized cards; literal next `https://delinea.com/news/page/22`; zero inferred dates; terminal false. |
| Sonatype `https://www.sonatype.com/press-releases?page=8`, fetched `2026-10-24T08:19:12.070060Z`; body `eb3c8166d0bcf3924f2992af9c32a1d64cc817ba24e9778d4038f0c6b1b9eb6a` | 16 recognized dated cards; literal next `https://www.sonatype.com/press-releases?page=9`; terminal false. |

Both exact bodies still reject under V3. Delinea adds only its fixed `/news/company/blog/YYYY/MM/DD/<slug>` form with a real, padded calendar date and strict terminal slug. Its route date does not become publication metadata. Sonatype adds one optional trailing hyphen to the final direct or second slug segment, with reserved and numeric checks applied after that hyphen is removed. Existing raw-literal, host, card, title/image, duplicate, and pagination checks remain. Delinea still has no proved terminal layout.

## Resolved finding and adversarial checks

The first origin draft allowed V4 in `_binding` but omitted its exact tuple from `_sparse_adapter`. That would prevent a future Delinea/Sonatype V4 origin from retaining mandatory earlier schema-1 explicit-page inventory under the selected main adapter. The parent added the exact V4 tuple while retaining full derived-adapter hash equality.

At the parent's request, this reviewer added one test, `test_prior_explicit_pages_use_exact_v4_adapter_without_renewing_original_proof`, to `ops/ci/test_source_qualification_origin.py`. It exercises both sources through the real explicit-proof validator using fictional paid schema-1 proof fixtures. V3 rejects the newly shaped article, V4 parses it, the original observation/body/time remain exact, Delinea gains no date, and an altered adapter context rejects. This establishes code behavior only; it supplies no actual completion or external activation authority.

The independent sealed pass rejected 59 mutations covering Boolean, floating-point, unknown and downgraded revisions; request-limit scalar types; wrong adapter hashes; cross-source tuples; changed sparse context; invalid leap/calendar dates; unpadded or deeper historical routes; reserved/numeric/trailing-slug errors; and unsafe URL syntax. Focused OrbStack checks passed 42 tests: five V4 route tests, 13 caller/primary revision tests, and 24 origin tests, including the new explicit-page regression. Host and VM test-file hashes matched before the final origin test run.

## Archive and authority boundary

All 35,592 manifest entries authenticate in `/var/tmp/smp-bounded-v3-probe-20261024/archive-c112ffb8/jessepike-sec-market-c112ffb8b924d227e1ce3064b9c8de9edf4986b1` under manifest SHA-256 `92acb13705494a1453d8240c3f87f617dde22a07ec3ffc428cbb4deb22ea2d87`. Before/after seals for all 35,596 files and 1,325 directories matched:

| Seal | SHA-256 |
|---|---|
| Content | `24ecd18c469e11e634cc797fed2d4be46970ca54eaaeddfba30ccf1e588ffbb1` |
| File modification times | `2e1fbe0fa7214633f8e0b92a361606f87abfe8ce7efaba171c66b65ba6930932` |
| Directory modification times | `55253b6e4f6a3fbea7816d75933153fc77b56b3322b75278fe26effc3daf87b2` |

The sealed replay blocked network, subprocess, and disk mutation attempts, with no attempted violation. It made zero source/model requests and zero actual state/archive writes. Only the assigned review document and the one authorized regression test were written. `ACTIVATION_AUTHORITIES` remains empty. The 74 suppliers, 557 obligations, registrations, quotas, normal collection state, and publication state remain unchanged. Future activation still needs genuine complete source proof, all earlier inventory evidence, the closed policy transition, and separately reviewed external authority.
