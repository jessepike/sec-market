# November 1 scheduled publication audit

The actual November 1 scheduled collector completed and its accepted data reached public production. The managed runtime trial remains separate and unactivated. This audit used read-only GitHub/Vercel requests and public file downloads. It dispatched no job, called no model and changed no provider setting.

## Actual run chain

| Run | API event and observed result |
| --- | --- |
| [41303798977](https://github.com/jessepike/sec-market/actions/runs/41303798977) | `subscription-collector.yml`, `schedule`, main `2aa87f5dd3182bc214f6efee10e709e5114a06ad`, success, 11:52:17–12:17:57 UTC. Both schedule guard and collection jobs ran on GitHub-hosted runners. |
| [41305812133](https://github.com/jessepike/sec-market/actions/runs/41305812133) | `subscription-publisher.yml`, `workflow_run`, same main revision, success, 12:17:59–12:41:46 UTC. Receipt records an acknowledged publication, sequence 7. |
| [41306711599](https://github.com/jessepike/sec-market/actions/runs/41306711599) | `market-release-gate.yml`, `workflow_dispatch`, same main revision, success, 12:29:04–12:39:00 UTC. Gate reports 538 executed tests, matching check-log hashes and all 80 required SEC claims re-derived without drift. |
| [41307712849](https://github.com/jessepike/sec-market/actions/runs/41307712849) | `production-rollback-drill.yml`, `workflow_run`, workflow success, 12:41:48–12:42:03 UTC. Only preflight ran. The actual rollback-and-restore job was skipped. |

`github-runs.json` preserves API event fields and runner results. The collector API and archived collection clock both say `schedule`; this finding does not depend on a run title. The pinned publisher workflow accepts only the collector completion callback, and its callback code requires a successful actual main scheduled collector through the GitHub API. The publication receipt does not repeat the upstream callback ID and the raw event payload was not retained, so that direct payload-level join remains unavailable. The collector, gate, accepted release and public app receipt have the same actual collection run ID `892bb5f3dcc1febfc917b14fca23c68d7f60b27546542bb1a598294ca82c43b9`.

## Exact archive and public joins

The collector checkpoint is archive commit `9d7723b14792399d974e9ecec26845b47e687abc`. The gate input identifies archive `899783054185fe22e46bc26005c33da4c6c527c7`. The acknowledged publication is retained at `536313307b5a9d5d6ae8e2c9f60cc46e3371c39c`, with the actual 13,943,013-byte archive manifest hashing to `e157a71102ac9abb9febc5716edca6ea3fdcbc84631454dc01bdf7a8956934af`. Its selected entries match the fetched bytes, including the production pointer, collection clock, gate receipt and accepted release. The full manifest and large objects remain outside this package in local scratch.

| Identity | SHA-256 or value |
| --- | --- |
| Accepted release, recomputed from its manifest | `55024dd8cac9b122949694b3e146ad5ba45652ae247412a90e634603e60684c5` |
| Sealed collection receipt bytes | `0f4205930c424a373563bbf5706a7ad9341335d1094d7aba4e51ad05cc5367df` |
| Accepted snapshot object bytes | `e6e142836cd1a035163fed7882eb06d36fa0145b7e70297158425bd5adb2ac46` |
| Coverage contract | `47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a` |
| Build archive bytes | `8b215926a19a7f3ecde9e23eeaf2404523792ea483a40b7cf8e6299c4f36f62a` |
| Exact artifact inventory bytes | `dcfe1b3befdc0713d704de8e0c1a12d770e2966bc24c00b8307976945ccf2b6d` |
| Public and gate app receipt bytes | `de5ced024876d62a8843770e2eb126aae1aaacc01671baab3fe652b1ab4b21da` |

All three downloaded GitHub artifact ZIP hashes match the API's artifact digests. All 53 files inside the accepted build archive match its inventory. At 18:17:49 UTC, all 52 public static files matched that inventory byte for byte. The additional detached public deployment receipt equals the archived acknowledgement. `verification.json` and `static-byte-verification.json` preserve the individual checks.

The public receipt certifies at `2026-11-01T12:36:49.269Z` and names app revision `2aa87f5dd3182bc214f6efee10e709e5114a06ad`. Native Vercel inspection identifies `dpl_4TYQBozYnNJYvWNyb24mxPqzCQ8n`, production target, READY, immutable URL `https://security-market-pulse-kgzpftsl3-pikeholdings.vercel.app`. The public `securitymarketpulse.com` alias points to that same native deployment. Native deployment metadata has no revision tag; the revision join comes from the matched accepted public bytes. Unrelated account and access-bypass metadata was omitted from `native-deployment.json`.

The actual reader build `bld_qjmqgrq90` used a **30-core, 60-GB Turbo Build Machine**. Its complete eight-event log says it used prebuilt artifacts from `.vercel/output` and then deployed outputs; it shows no install or compilation event. The native deployment was created at 12:39:12.955 UTC, began building at 12:39:13.755 and was ready at 12:39:15.113, a 1.358-second build interval. That timing does not establish the billed CPU minimum. Separate November 1 inventory queries for both existing projects, without target/status filters, return one reader deployment (this one) and zero controller deployments, with no next page. `reader-build-events.json`, `reader-build-attribution.json` and `nov1-deployment-inventory.json` preserve the source and attribution. The saved event payload hashes to `ba533603bb8def41fa917ce5cf1a7875124e2509d3cb5c992111346f2ef83939`. Prebuilt publication did not select a Basic machine.

The [financial review](cost-review.md) applies the spending stops. The actual provider CSV at `/Users/jessepike/code/projects/sec-market-finish-20261022/.ctx/vercel-managed-runtime/evidence-20261101-1822/billing.csv` hashes to `7dfb007a52acb9a41c34916781fcccbf9b1ac5b23af24c1d0a051ea20824022a`. Independent decimal arithmetic confirms 379 source rows, 31 selected two-project rows, cumulative reported USD `0.2583832475052626338510`, and November 1 reported USD `0.1087825084558269693`. The reader's November 1 Build CPU Minutes row is USD `0.105`, usage `30`, formatted `30 minutes`. The CSV groups by project/day and has no deployment ID; the complete same-day deployment inventory and actual Turbo event provide the attribution. These partial reported charges already exceed the unchanged USD `0.05` daily limit. They do not establish the settled final-day total. `billing-source-check.json` preserves the selected build row, actual source hash, original provider download metadata and independent totals without copying the complete CSV. Further paid work remains stopped under the financial review; the live publication supplies no daily-budget acceptance.

## What remains incomplete

The collector completed with gaps: 265 of 557 intake obligations passed, leaving 292 gaps. Processing reviewed 74 of 11,665 documents, with 11,591 pending, 19 held and 822 unknown dates. Historical review records 75 reviewed and 11,590 pending, with 19 held. The review queue has 51 items. All public intake, processing and historical completeness flags remain false. The actual day ledger records 68 subscription model calls, 33 documents and 454 fetches. This audit made none of those calls. The gate ledger records two attempts, and the publication ledger records the accepted release. No costs or allowances were reset.

The four generic evidence records retain publication dates October 15/20 and retrieval dates October 24. The two retained document revalidation resolutions retain October 26/27 dates. `source-dates.json` and `revalidation-dates.json` preserve these original clocks. November 1 certification and intake times do not make retained source articles new. All eight prior factual-correction groups remain present, with no new group in this publication.

The November 1 rollback preflight returned `allowed: false`, `DRILL_AUTOMATIC_ACCEPTANCE_DATE_EXPIRED`, `skipped: true`, `passed: false`. There is no November 1 rollback/restoration receipt. `historical-rollback-2026-10-23.json` is the retained October 23 acceptance: production returned to its baseline and then restored the then-current sequence-1 deployment. That historical proof does not cover the November 1 sequence-7 release. The old baseline had no complete byte inventory, as its receipt explicitly records.

The observed path used GitHub-hosted runners, the subscription Codex CLI and Vercel static production. No Codex Cloud execution or managed trial runtime appears in this release chain. The live collector installed Codex CLI 0.163.0 and application dependencies; this run does not exercise the separate candidate's dependency reuse. One successful scheduled release proves this day's publication path. Full coverage, sustained clean days, complete operating-cost fit and the managed runtime qualification remain separate unfinished work.

## Saved evidence

The JSON files beside this audit contain bounded public/nonsecret receipts and projections. `sha256sums.txt` hashes every saved file except itself. Raw logs, artifact ZIPs, large archive manifests, the snapshot and sealed collection receipt remain in `.ctx/scheduled-2026-11-01/`; none is required as executable code, and no downloaded code was executed. Native API metadata is intentionally reduced. The byte comparison checks content only and supplies no new visual-layout review.
