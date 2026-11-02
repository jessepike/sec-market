# November 2 scheduled Basic publication audit

A genuine scheduled collector completed on November 2 and its accepted data reached public production using a Basic build machine. The verification below used read-only GitHub/Vercel requests and public file downloads. It dispatched no job, called no model and made no provider changes. The paid managed-runtime trial remains stopped.

## Actual run chain

| Run | Actual API event and observed result |
| --- | --- |
| [41453903198](https://github.com/jessepike/sec-market/actions/runs/41453903198) | `subscription-collector.yml`, `schedule`, main `2aa87f5dd3182bc214f6efee10e709e5114a06ad`, success, 13:32:47–13:54:36 UTC. |
| [41457061782](https://github.com/jessepike/sec-market/actions/runs/41457061782) | `subscription-publisher.yml`, `workflow_run`, same main revision, success, 13:54:39–14:15:40 UTC. Its receipt records acknowledged publication, sequence 8. |
| [41458664767](https://github.com/jessepike/sec-market/actions/runs/41458664767) | `market-release-gate.yml`, `workflow_dispatch`, same main revision, success, 14:05:34–14:13:08 UTC. All 538 executed checks and all 80 required SEC claims passed. |
| [41460245364](https://github.com/jessepike/sec-market/actions/runs/41460245364) | `production-rollback-drill.yml`, `workflow_run`, workflow success. Only preflight ran; the actual rollback-and-restore job was skipped. |

The collector's API event and archived collection clock both identify a scheduled main run. The collector receipt, archived clock, sealed coverage receipt, independent gate, accepted release and public app receipt share collection run ID `51a9fbabd0cbd69cdbb807ac97f0baa5519cd8b53962bdff9f6c6096b8cf0b97`. `github-runs.json` preserves bounded native run and runner fields. The unchanged pinned callback guard requires a successful main scheduled collector. The raw `workflow_run` payload is not retained and the publication receipt does not repeat the upstream callback ID, so a direct payload-level join remains unavailable. This limitation does not substitute a manual run for the actual scheduled event.

## Accepted archive and public bytes

The collector checkpoint is archive commit `1fcd80db4ab4ee7e8b34dbb4d93d2c96096196ec`. The gate's declared input is `2942be64457c25e30b9c5e2f452bb2dab4fdaea9`. The publication acknowledgement is retained at `52632a360f4099f142ed0e10e46338e1d91f1bc9`. Its full 69,873-entry archive manifest matches declared SHA-256 `3cb739133b60e03d418480e53ee8c454dca616efa8d3585fde87c5eb9ac61438`; selected retained entries match their actual sizes and hashes.

| Identity | SHA-256 or value |
| --- | --- |
| Accepted release, independently recomputed from its manifest | `ed8ffe5d14d6e5df4e3555ab55df315d8d0f2870228d1865e3c4b2b0ba38250a` |
| Sealed collection receipt | `9e66f87384806876cdbee573e856a2e4098d7e914dd949be3b5b7b83831a3def` |
| Accepted snapshot object | `e44a985ce8e8960fc585a79c4ad64dd2cfda0ae67a0d2afa3e192c7846676b86` |
| Coverage contract | `47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a` |
| Exact build archive | `cc6e8df8d0e295474328d08bea1f3c1702b566346cb018a943c894bdbc753297` |
| Exact file inventory | `16dbf024c1ba9088e42128f80a291070cb2a2b1c14cb7b31de2f6de627c6921b` |
| Public app receipt | `d5b87f13a7361593dfe737736298f178796492882127a8ae523167e456be4e1a` |
| Archived gate receipt | `0a82fcafc9759d5b5f295efeb54f2df04846a979e13f4c9baffdafd15753b8f3` |

All three actual GitHub artifact ZIP downloads match their API digests. All 53 files inside the accepted build match the inventory. All 52 public static files match the same inventory byte for byte. The detached public deployment receipt equals the retained acknowledgement, and the gate's app receipt equals the served app receipt. The archived gate adds only the provider-assigned `githubArtifactId` to the original artifact receipt; its canonical digest matches the accepted release. The four retained gate log hashes also match. `verification.json` and `static-byte-verification.json` retain the individual checks and observation times. Large archive inputs, artifact ZIPs and full source logs remain in ignored local scratch.

Public `certifiedAt` is `2026-11-02T14:11:32.737Z`, or 6:11 a.m. Pacific. Native inspection identifies production deployment `dpl_HeZV2C32dtyzoiTfEPktBFqAubZ2`, READY, immutable URL `https://security-market-pulse-1s539qt26-pikeholdings.vercel.app`. The public alias resolved to that same native deployment. Native deployment metadata has no revision tag; its app revision is established by the matched accepted public bytes.

The actual eight-event log identifies build `bld_kkbtdzki9` with **2 cores and 8 GB**, then `.vercel/output` prebuilt artifacts and completed output deployment. Native timestamps show creation at 14:13:17.633 UTC, building at 14:13:18.575 UTC and ready at 14:13:20.291 UTC, or 6:13 a.m. Pacific. The 1.716-second building interval alone does not establish charged CPU minutes. `native-deployment.json` and `reader-build-events.json` retain the bounded authenticated provider observations; [cost-review.md](cost-review.md) and `billing-source-check.json` supply the actual charge evidence and its limits.

## Coverage and accuracy remain incomplete

The actual collector finished with **262 of 557 intake obligations** passing, leaving **295 gaps**. It charged 54 existing-subscription model calls, 24 documents and 439 fetches. `apiFallback` is false; the observed executor was GitHub-hosted with subscription Codex CLI 0.163.0. No managed trial worker or Codex Cloud execution supplied this release. Gate budget records one attempt and publication budget records the accepted release; no counters were reset by this audit.

Processing reviewed 83 of 11,671 documents, with 11,588 pending, 20 held and 1,479 unknown dates. Historical review records 84 reviewed and 11,587 pending, with 20 held. The review queue has 51 items. All intake, processing and historical completeness flags remain false. SEC accuracy credit covers the 80 required SEC claims with zero drift, and all eight accepted correction groups, including Varonis, remain in the release. It does not certify all historical supplier facts or establish reader value.

`coverage-delta.json` compares unique stable named source IDs with the November 1 retained receipt. Cohesity's official source changed from checked to HTTP 403. WitnessAI's official and citation source checks changed from checked to HTTP 504. Those three lost checks explain the net decrease from 265 to 262. The current gap errors are 254 unregistered discovery sources, 23 unverified source bindings, nine HTTP 403, four HTTP 429, two HTTP 504, two invalid Q4 list-row inventories and one unapproved source/redirect host. Daily task IDs depend on the daily inventory; they were not treated as stable cross-day identities.

`source-dates.json` preserves original October 15/20 publication dates and October 24 retrieval dates for the four admitted ordinary evidence records. November 2 certification is a new check, not a new article date.

## Rollback and financial limits

The actual rollback preflight returned `allowed: false`, `DRILL_AUTOMATIC_ACCEPTANCE_DATE_EXPIRED`, `skipped: true`, `passed: false`. The jobs API confirms `rollback-and-restore` was skipped. This run supplies no new rollback or restoration proof; the October 23 exercise remains historical.

The fresh cost observations are recorded separately in [cost-review.md](cost-review.md). November 1 is now a closed provider day and exceeded five cents. November 2 already contains the actual $0.007 Basic build charge, but the day is still open and billing can lag. No full-day under-five-cent claim follows from this successful Basic publication. The retained cumulative trial forecast still exceeds the approved $0.30 stop, so the paid trial remains stopped.
