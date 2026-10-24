# Actual bounded traversal V4 review

The V4 diagnostic preserved all earlier accepted index inventories and completed Ping's index walk. Delinea remains incomplete because terminal-page evidence is still unproved. Sonatype remains incomplete because page 10 contains an article path the parser rejects. None of the three candidate sources is qualified or credited.

## Run and exact replay

Run `40079036392`, attempt 1, was a `workflow_dispatch` on `refs/heads/main` at application revision `4b5e5ec1669ddad052c6320ddf4a4dffdb9c1f5e`. Its archived diagnostic started at `2026-10-24T08:44:46.410288Z` and checked at `2026-10-24T08:45:25.560536Z`. The retained receipt is [bounded-traversal-v4-source-probe-result-2026-10-24.json](../receipts/bounded-traversal-v4-source-probe-result-2026-10-24.json).

I replayed the V1, V2, V3 and V4 reports with `replay_bounded_candidate_diagnostic`, using a read-only store over the authenticated archive. All four reports reproduced exactly. V4's retained report matches the receipt's diagnostic. Its raw plan hash is `0353ec8ef62fedd09758cc44b1fcbe80bbe713e996432a3684f524acd66c6c55`, and its referenced plan object is 5,338 bytes. V4 also has the same contract hash as the original policy, `79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60`.

| Run | Ping URLs | Delinea URLs | Sonatype URLs | Total accepted pairs |
|---|---:|---:|---:|---:|
| V1, `40072784799` | 170 | 96 | 32 | 298 |
| V2, `40075237236` | 200 | 204 | 96 | 500 |
| V3, `40077375424` | 242 | 240 | 112 | 594 |
| V4, `40079036392` | 242 | 290 | 144 | 676 |

Every V1, V2 and V3 `(sourceId, URL)` pair appears in V4. The original observations and reports remain unchanged; V4 adds inventory only where it has new accepted literal index cards.

## V4 result

The diagnostic retained 60 index responses and three primary samples, for 63 fetch reservations. The daily fetch counter moved from 1,375 to 1,438 against the 5,500 cap. Model calls remained 0; the already-used model and document ledgers remained at 80 and 40. There were no reservation denials. Exact replay checked the retained source and adapter bindings, page order, observations, response bodies, times, reservations and all three primary-sample joins. The primary samples passed readable-shape checks; they do not establish index completeness or semantic truth.

| Candidate source | Index responses | Accepted URLs | Result |
|---|---:|---:|---|
| Ping Identity | 25 | 242 | Complete diagnostic inventory; terminal page proved. |
| Delinea | 25 | 290 | Incomplete; terminal page remains unproved. |
| Sonatype | 10 | 144 | Incomplete; `Unsafe HTML archive article path` on page 10. |

The run reports `executionCompleted: true` for the diagnostic. It reports zero source checks credited, zero qualified sources, zero facts, zero model calls, `semanticAdmission: false`, and `coverageCredit: false`. This is a completed diagnostic with two incomplete source traversals, not a completed qualification or collection.

## Archive integrity and limits

The authenticated archive is `/var/tmp/smp-bounded-v4-probe-20261024/archive-e467ab00/jessepike-sec-market-e467ab000b8225931d6684eb6d0aa39bbba1f6c9`, commit `e467ab000b8225931d6684eb6d0aa39bbba1f6c9`, manifest SHA-256 `ce989f357ecda7ef5a460ad96ceededf6a8f4b1cd566a408eb6ba79f3a4fad70`. The verification receipt is `/var/tmp/smp-bounded-v4-probe-20261024/verification.json`. It records 35,790 manifest files, all 35,592 preceding paths retained, 198 additions, no removed files or immutable changes, and unchanged protected collection, correction, snapshot and production heads. Only the budget and cloud-lease heads changed. The archive contained 35,794 files and 1,330 directories before and after replay; content, file-time and directory-time seals were identical. The verifier recorded zero store mutations and exact artifact-to-retained-report equality.

This review establishes the retained diagnostic and its boundaries. It does not establish source qualification, a candidate registration change, intake credit, production publication or scheduled collection. A future parser revision may review only the new literal route form while leaving the historical V1 through V4 reports under their original parser meanings.
