# Security Market Pulse publication and recovery evidence index — 2026-10-27

This index links two consecutive automated publications and the retained recovery exercise. The proofs are in temporary evidence directories; no file in `sec-market-finish-20261022` or Git ref was changed for this audit. Current app revision remains `f514cfe017a60b3dea50bc4da37980f4b892f657`.

## Oct. 26 publication and recovery

The Oct. 26 publisher receipt pins release `00ce24b2f1c77c5164bc9e41cd931ab8ff7f501cc1e5ed156c6372fef896c878`, sequence 5, and immutable deployment `https://security-market-pulse-5sjl32w82-pikeholdings.vercel.app`. The archived receipt hash is `5626f9b7cd3a6c8a737dcab9046be9292df743fed8e184492d4446b2cb3badf1`. The independent exact-byte receipt recorded 106/106 matching files across that deployment and the custom production host; hash `67be0a40d1a7d18431293a382782e90df89adccdf34b9b65ae4af04025d64c4a`.

The Oct. 26 rollback-and-restore run `40348882047` completed successfully. Its retained artifact `12663820521` has digest `33edca3f91033d46f488f24b3f783c7db072430ffb123d66fb0fc5c14bc00594`. The receipt says the drill passed: it tested the sequence-4 baseline’s byte inventory, restored sequence 5, verified both baseline and current bytes, and recorded that the production head remained on sequence 5. Receipt path in the current VM workspace is `/var/tmp/smp-oct27-proof-40493431849-40494821057-40348882047/drill/smp-rollback-drill-receipt.json`; receipt SHA-256 `f2345ff74a13f443a2a39d9640eafa6d83a51ca8705880c6ef5ece65c18eb111`.

The complete Oct. 26 report and detailed byte ledger remain at `/tmp/smp-production-publication-audit-20261026.md` and `/var/tmp/smp-prod-audit-40316085839-40317378869/byte-verification-receipt-rootpaths.json`. Keep those originals as the record of the sequence-5 publication; this index does not replace or rewrite them.

## Oct. 27 publication

Publisher run `40493431849` and gate callback run `40494821057` both completed successfully. The retained publisher receipt names release `f1f67666db35e28cd4998503afd4bc65c1ef6da5e06fef8065e103bda8aa2911`, sequence 6, immutable deployment `https://security-market-pulse-hzte4a2bp-pikeholdings.vercel.app`, app revision `f514cfe017a60b3dea50bc4da37980f4b892f657`, and snapshot SHA-256 `930cc1ecac174d0b6c3e0e5eb665202601e8f574147ea70d1403d32ec919209b`. Publisher receipt SHA-256 is `55d10de32f21d3d4d5a1a8c89ce562f5b133ad6949b5d9e83eb4b326f3bad92e`.

The Vercel API independently identifies deployment `dpl_D492WhfeRk124FjGCEQLtm8b37PM` as `READY`, target `production`, with the same immutable host. The response has no deployment-expiry field. The production-head object at current archive ref `15009eeec54f5df60070d19f8b29ef1e27821aa1` also names sequence 6, that release ID, and that host.

The gate receipt records all four checks passing and 538 tests. It pins contract `47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a`, exact build inventory `237d8dcdee8b85fb41dc44d411531bc165873d711f1c6385ca92399ff9e51630`, archive manifest SHA `51b2231de2b9336ec0d2c6cfbf3de80fc63542033bcd874ca64fc80672ce7699`, and snapshot `930cc1ec…919209b`. The `build.zip` SHA-256 is `6054a6fd18d3ff3eb60805c5762daf4d5e13e44e7fc4ee36dd2278da24729244`. Re-running the repository `unpack()` and `inventory()` helpers reproduced the exact inventory pin.

An OrbStack VM verifier fetched all 53 public paths from both the immutable host and `https://securitymarketpulse.com`: 106 GETs, 106 exact byte matches, no failures, with status and final URL checked. The full per-path byte receipt is `/var/tmp/smp-oct27-proof-40493431849-40494821057-40348882047/byte-verification-receipt.json`, SHA-256 `5e05057b0f68a5f4e0a0b04cb436a4cb902088b1b895ccdaad860d6c8bb0741c`.

The Oct. 27 factual-corrections artifact has eight groups and preserves the six original groups plus both Varonis and SentinelOne qualifier groups. The full eight group objects match the Oct. 26 release-5 artifact exactly; there are no new correction groups in this publication. Policy SHA-256 is `1c629249347b9bdacaf4fadf563e1a0ed807b96c0cbb02e3e2492ae00a839e5b`. The current group artifact SHA-256 is `3e049cb099dc7cc1c9fe3cfb4b8c56540b4a18882ffdea8557a18b1cb06fce50`.

Coverage is still marked incomplete and degraded: 74 suppliers, 266 of 557 required tasks successful, 291 gaps. Its `validUntil` is `2026-10-28T16:48:26.281000+00:00`. This is the source-freshness deadline; it is distinct from GitHub artifact retention and Vercel deployment lifetime.

## Retained artifact expiry

The Oct. 27 publisher artifact `12730468850` expires `2026-11-10T11:28:05Z`; its digest is `f5569ce54a64f91b8564a6e6c7d4a9a9466d6bae359f936f5839eb85ec675778`. Gate artifact `12729909242` expires `2026-11-03T11:25:28Z`; digest `0cafc52ff5f80a500252b6c4b01ced3ab8b0abfb5b64bb1f30101411e9d97aaa`. Screenshot artifact `12729704563` expires `2026-11-03T11:26:00Z`; digest `711514c705925bd5848e858748e0014c295c31116b01cee250c9df2bf609772a`. The Oct. 26 drill artifact expires `2026-11-09T15:36:47Z`.

Oct. 27 evidence is under `/var/tmp/smp-oct27-proof-40493431849-40494821057-40348882047/`. The separate Oct. 26 evidence directory and publication report are retained as cited above. This is an evidence index, not a statement that incomplete coverage is complete or that the source has been promoted from its existing authority state.
