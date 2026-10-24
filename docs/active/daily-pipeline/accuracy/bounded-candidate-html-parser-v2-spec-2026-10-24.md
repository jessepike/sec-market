# Bounded candidate HTML parser V2

Status: implementation note for explicit V2 parser modes. V1 parsing stays byte-for-byte compatible with historical schema-2 diagnostics. V2 is inactive until a future raw plan selects parser revision 2 and pins the matching proposed adapter hashes.

## Observed failures

The authenticated `source_probe` receipt for run `40072784799`, archived at commit `c961945736499da3105d565e513eda78a01e996a` with manifest `b23cb5f5185e6a147956b89107ae6252fb53fbb24a5f49ece507deb7da020dc0`, completed with 33 charged requests and no source credit. The three failed index bodies were independently checked against the retained archive:

| Source and exact page | Body SHA-256 and bytes | Literal same-host card path | Existing rejection |
|---|---|---|---|
| Ping `https://press.pingidentity.com/news-releases?o=170`, fetched `2026-10-24T07:08:42.623031Z` | `c749d859cc819a87e866a01bf7b8000f56769e1b44f6801f51afccc280c9f4f1`, 98,851 bytes | `https://press.pingidentity.com/201907-09-Ping-Identity-Named-Best-Identity-Management-Solution-at-the-2019-SC-Awards-Europe` | Date prefix is `YYYYMM-DD`, unlike the usual `YYYY-MM-DD` form. The card date is July 9, 2019. |
| Delinea `https://delinea.com/news/page/9`, fetched `2026-10-24T07:08:45.930750Z` | `be781fe7adb02f0b8af0d111f2a08f59538a086bac9529bb98bf4cb7e9952cc4`, 143,243 bytes | `https://delinea.com/news/fifth-consecutive-northface-scoreboard-award-` | The official title and image links share a slug with one trailing hyphen. |
| Sonatype `https://www.sonatype.com/press-releases?page=3`, fetched `2026-10-24T07:08:47.538877Z` | `b77dd7c589989b8228107f5f1a85332af93075b128bceccb62575d71dd963adb`, 139,342 bytes | `https://www.sonatype.com/press-releases/sonatype-introduces-cutting-edge-ai/ml-component-detection` | The official article slug contains the literal `ai/ml` path separator. |

Each raw body remains unchanged in the verified run archive. These are layout and inventory findings only. Run 40072784799 remains incomplete under V1 replay and receives no source or semantic credit.

## V2 bindings

Add mode names `ping-release-pagination-v2`, `delinea-news-pagination-v2`, and `sonatype-press-pagination-v2`. Their exact source ID, supplier, family, kind, host, endpoint, and page-cap checks match the corresponding V1 bindings.

V2 retains each V1 rule and adds only the observed shape:

- Ping accepts a compact `YYYYMM-DD` prefix only when it parses as a real date and equals the card’s displayed date. Existing slug characters remain limited to letters, digits, underscore, comma, and hyphen. Query strings, fragments, foreign hosts, and malformed date prefixes remain rejected.
- Delinea accepts one trailing hyphen on an otherwise valid single-segment lowercase slug. It still rejects extra path segments, the pagination route, queries, fragments, and foreign hosts.
- Sonatype accepts one exact two-segment article path: `/press-releases/sonatype-introduces-cutting-edge-ai/ml-component-detection`. Every other V2 path keeps the V1 single-segment slug rule. Queries, fragments, foreign hosts, and pagination paths remain rejected.

The raw plan must explicitly choose parser revision 2 and pin the corresponding V2 adapter hashes before runtime can use these modes. Missing or unknown revisions continue to mean V1. This parser unit does not change the active plan, contract, registration, source execution, or intake state.

## Validation boundary

Tests cover V1 rejection, V2 acceptance, exact source-contract bindings, and rejection of foreign, query-bearing, or pagination URLs. When the authenticated archive is available, a retained-body test verifies the three exact archived pages and their hashes. No transport is performed. A future bounded run must use the normal lease and retain every page, response, timestamp, source identity, and charge. V2 recognition does not establish complete pagination, readable primary documents, source qualification, semantic accuracy, or activation.
