# Actual manual freshness publication

Manual publisher `40172130763` and its actual independent gate `40172376435` completed successfully.
The public release is verified against the accepted artifact, including every static file on
both its immutable deployment and the public host. This restores freshness; genuine timer proof
remains pending.

## Actual release

| Measure | Verified value |
|---|---|
| Application | Exact main `6d5e87feba4ffbc75e50f35cb564cb8fd91708ca`. |
| Release | `fc8bf0984dbeacbe79519574911837d8b638f42215f6547e31ae8968b29951e4`, sequence 4. |
| Deployment | `dpl_GFKc3mfpR6CSeZt7u62B5LVBqQjv`, production target, actual Vercel state READY. |
| Immutable host | `https://security-market-pulse-fqk0jyft3-pikeholdings.vercel.app`. |
| Public host | `https://securitymarketpulse.com`. |
| Gate | `40172376435`, successful, 531 tests: 373 data, 115 pipeline and all 43 browser tests. |
| Gate artifact | `12590843044`, SHA-256 `ef628abef50d32f88c9c8dec0a04099f74b84a5fa7d954f1d22d7e8931d6b3d4`. |
| Tested inventory | `0c645ba2977c3e7e3df04a99d2d677ed5e7149b8608d3b472af0ea0b0c810c36`. |
| Snapshot bytes | `8ba13011b9d29b875082a551800d57e265238fd7ffd649ff7b99f7072ab25a89`. |
| Actual collection receipt | `f2486a623d93da011eaaf11926e09d6ce1533dab26d4a8f2fa2875a95a84d0b6`. |
| Gate input archive | `c19d505b5ea723e64827e604cca6e09ee05a9879`; manifest `ba84f3aeade2f4e4850020ed9eb386025ebcbb55727eb91c33e5dd4c165463f0`. |
| Final publication archive | `f96c3bbf27ca98805dd0a6d99d1c7aa7ac27aa30`; manifest `3eb885833fabf8c7ce4e4219908e306e184c054b739762b15203c11ec1d5a81b`. |

## Independent byte check

The actual gate artifact ZIP and actual publisher receipt were downloaded and matched their
GitHub SHA-256 transport digests. The inner build ZIP, complete tested inventory, snapshot bytes,
release content hash and gate/artifact provenance were checked independently. The archived release
record came from its exact final publication commit, with its Git blob hash checked after decoding.

The accepted build contains 52 static files. Its detached acknowledgement was reconstructed from
the authenticated release manifest, producing 53 expected files per host. All 106 HTTP responses
returned status 200, kept their exact requested URL and matched the complete expected bytes.
That includes the public app receipt, current data and detached deployment receipt. No file was
sampled or omitted. Vercel's read-only deployment lookup independently reported READY.

The check completed before the separately authorized manual rollback/restoration drill. These
receipts prove the release at that point; the drill's result belongs to its own evidence.

## Current data and preserved evidence

| Measure | Actual served value |
|---|---|
| Source intake | 264/557. |
| Processing | 38/10,655 reviewed; 10 held; 10,617 pending. |
| Historical review | 39/10,655 reviewed; 10 held; 10,616 pending. |
| Source expiry | October 26, 2026 at `12:45:29.479727 UTC`, unchanged from actual collection. |
| Review queue | All 37 entries match the new actual collector snapshot. |
| Fact provenance | All four references match the new actual collector snapshot. |
| Current event projection | Four current-policy events. |
| Historical quarantine | Four older events remain in `pendingFacts`. |
| Corrections | All six dated rows and admissions match the previous accepted artifact exactly. |

Every one of the collector's eight event objects and linked evidence objects compares exactly
with its current or pending destination. Original event dates, evidence text and source retrieval
clocks remain unchanged. Supplier updates and update dates also match. The queue comparison is to
the new recovery snapshot; it does not claim that every older queue row or held-receipt reference
was unchanged during collection.

Issue [12](https://github.com/jessepike/sec-market/issues/12) closed at `07:28:33 UTC`. The publisher
workflow completed successfully, including recovery reporting. In-progress and queued run
snapshots showed no writers before the root dispatched the separate manual drill.

## Allowances and limits

The final authenticated gate ledger records **2/2 attempts spent, zero remaining**. The gate's
input archive predates this reservation and still records one spent; the final publisher archive
records two. No reset or refund occurred. The source ledger remains 72/80 model calls, 33/40
documents and 444/5,500 fetches.

This publisher was `workflow_dispatch` and followed a manual recovery collection. It supplies no
genuine scheduled collection/publication proof. Source coverage and processing/history remain
incomplete. The verification made no commit, push, dispatch, source/model request, archive write
or Vercel mutation. It did not repeat the application tests.

## Evidence

Machine-readable result:
`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/manual-freshness-publication-2026-10-25.json`.

Hashed receipts and logs:
`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/receipts/manual-freshness-publication-2026-10-25/`.

The receipt directory includes the actual publisher result, actual gate result, GitHub run and
artifact metadata, READY response, decoded authenticated release/counter records, issue state,
all 106 file comparisons, SEC logs and compressed actual gate test output. Its manifest hashes
every saved receipt. Raw downloaded ZIPs remain in OrbStack at
`/var/tmp/smp-manual-freshness-publication-40172130763-20261025/`.
