# Four neutral regulatory bindings: review proposal

This proposes four source rows for the existing `crwd-exposure` and `panw-xsiam` subjects. I would stage them only after the current seven-target diagnostic and regular collection finish, then review the registry and diagnostic-plan migration together. The machine companion contains the exact rows, primary proof references, selected filing URLs and inventory joins. No contract or runtime was edited, no source was activated, and no source, network, model, Git or publication action occurred.

## Proposed rows and scope

| Proposed source ID | Subject | Family and kind | Exact parent CIK/name from submissions | Bound |
|---|---|---|---|---|
| `crwd-exposure:sec_index` | CrowdStrike Falcon Exposure Management | `regulatory_filings` / `sec_index` | `0001535527` / `CrowdStrike Holdings, Inc.` | 40 index pages; 365-day retained window |
| `crwd-exposure:sec_documents` | Same subject | `filing_documents` / `sec_documents` | Same exact parent identity | 100 index pages; every selected primary body in the 365-day window |
| `panw-xsiam:sec_index` | Palo Alto Networks Cortex XSIAM | `regulatory_filings` / `sec_index` | `0001327567` / `Palo Alto Networks Inc` | 40 index pages; 365-day retained window |
| `panw-xsiam:sec_documents` | Same subject | `filing_documents` / `sec_documents` | Same exact parent identity | 100 index pages; every selected primary body in the 365-day window |

All four proposed rows are `registration: candidate`, `required: true`, with `regulatoryIssuer.relationship: parent`. They grant zero checks while unqualified. Each index uses the exact `https://data.sec.gov/submissions/CIK<ten-digit-CIK>.json` endpoint, allowed host `data.sec.gov`, and `/submissions/` scope. Each document row uses that same root, additionally allows `www.sec.gov`, repeats the exact CIK in `cik`, and uses `/Archives/edgar/data/` scope. `seedEvidenceUrls` is empty: relationship evidence is independently pinned in the companion, rather than treating a leaf filing as a complete discovery endpoint.

Append only those two source IDs to each subject sourceIds list. Preserve the subject kind `segment`, current citation source, every alias/category/family, the parent company source rows and all other supplier records. The candidate contract was validated in memory against the existing strict source/issuer contracts. It still has 74 subjects and 557 required tasks: four absent-family tasks become four unqualified collection tasks, so actual successes increase by zero. Missing-family task count alone changes from 254 to 250, while four candidate gaps replace them. The new global policy changes task IDs throughout the plan; unchanged obligation count does not mean old receipts become current checks.

## Exact archived parent proof

The 9c archive manifest is `cd9d84c67a70f11b72eeba25a012e3402a88b2d5a9c692f145c225b0a2c3418a`. Thirty-five selected entries were independently checked against it for raw hash, size and unchanged modification time. The proposal does not claim another complete whole-archive replay.

CrowdStrike parent proof is the January 31, 2026 10-K at `https://www.sec.gov/Archives/edgar/data/1535527/000153552726000010/crwd-20260131.htm`. Its Falcon platform description expressly includes Exposure Management. Inline XBRL binds CIK `0001535527` and registrant `CROWDSTRIKE HOLDINGS, INC.`. The original observation is `c8c6e9b6eb60cbced06fc5a88902e3c1bb0551c3b7360f34956e5ef1d029c10e`, fetched `2026-10-20T21:22:20.717300Z`; body hash is `c03d8b275ed8c532e01c8bbd412577b03a2e79038a6b4e3d867a74e8c1f88f67` (2,749,303 bytes).

Palo Alto parent proof is the July 31, 2026 10-K at `https://www.sec.gov/Archives/edgar/data/1327567/000132756726000023/panw-20260731.htm`. It expressly names Cortex XSIAM on the Cortex platform. Inline XBRL binds CIK `0001327567` and registrant `Palo Alto Networks, Inc`. Original observation `c6eceaa677080caadc165a800859935b07fe186b039e7bb12deabfb520f19e3d`, fetched `2026-10-23T04:14:59.011680Z`, is a retained conditional observation; body hash is `8605bc5f502c555918d601b6564c60d0d44e4c4d0705726af60fc424ed8130f5` (3,083,409 bytes). Its status and original date remain explicit.

The submissions responses name `CrowdStrike Holdings, Inc.` and `Palo Alto Networks Inc` exactly. Those names differ in punctuation/case from the filings. The neutral adapter requires exact submissions-name equality, so its rows use the actual response names and join the primary filing identity by exact CIK. A future mismatching issuer name holds for review; do not add aliases or normalize it silently. These bytes establish parent portfolio scope, not a separate product filer, current source qualification or independently reported product figures.

## Existing adapter and historical mechanical check

Use the implemented `regulatory.py` neutral index and filing-document functions, the explicit issuer guards in `contracts.py`, the `discovery.py` neutral traversal, and independent reconciliation in `validation.py`. No new adapter is proposed. A `sec_index` receipt independently verifies the ordered initial root and every literal older-index page whose declared range intersects the 365-day retained window. Missing, extra, conflicting, truncated, wrong-issuer or cap-exhausted pages hold. It emits no facts.

A neutral `sec_documents` receipt uses that same verified index and exact CIK-bound eligible URL/date selection, then retains and independently replays every selected primary body and readable text. Existing allowed forms include 10-K/10-Q/8-K variants, merger and delisting forms, 20-F/6-K variants and the existing late-notice forms. The JSON lists the exact current allowed set. Form, accession, primary path, filing date, body and subject joins remain mandatory. The generic two-document/one-audit work cap does not apply to this SEC document path; every selected primary is required, within the unchanged shared fetch/runtime limits.

Pure adapter replay at the original `2026-10-23T11:34:15.010723Z` audit time produced:

| Issuer | Required index bodies | Unique root filings | Filings within retained window | Eligible primary documents |
|---|---:|---:|---:|---:|
| CrowdStrike | 1 | 1,001 | 258 | 12 |
| Palo Alto | 1 | 1,000 | 130 | 17 |

The older literal archive tables end in 2020 and 2019, so they are outside that retained window. The earlier 1,307/1,908 lifetime audit totals are not the neutral-window results. This does not authorize dropping a future older page: each fresh root decides which declared pages must be traversed. The 29 exact selected URLs and their original parent-body hashes/dates are in the JSON.

The pure acceptance helper requires a verified declaration. Its historical check therefore used an isolated in-memory `verified` copy solely to replay adapter mechanics; the proposed rows remain candidates, and no registration or qualification was granted. Schema validation and an archived parser result cannot stand in for actual collection.

## Fresh actual work still needed

Under the existing normal leased collector path, obtain actual current responses for the two exact submissions roots. Follow every currently disclosed required older index page under the existing page/host limits. Create separate observations and independently validated receipts for each of the four subject/source joins. Existing same-invocation sharing may reuse successful HTTP 200 data.sec.gov bytes across the parent and neutral sources; it must retain original time and separate subject provenance. Failed responses, broader redirect policy and source-specific 304 chains cannot supply shared authority. Four logical source checks are not a guaranteed four physical GETs.

Both proposed document-source IDs have no source-specific cache entries for the 29 archived selected primary URLs. On first activation they therefore need actual body requests under their new source identities, subject to the then-current index selection. Existing parent caches/body objects cannot simply be copied into new source caches. Later unchanged immutable filing reuse is allowed only through the existing same-source original fetched observation plus current complete index anchors; preserve the original fetchedAt and distinguish verifiedAt. A current index does not refresh the primary body date or admit its statements. The archived 29-body count is planning evidence, not a fixed future request count.

Current qualification still requires the exact issuer/source and parent-relationship evidence to be reviewed, normal registration proof, and an actual independently reconciled new-policy collection. Candidate registration causes no request. No standalone fetch, diagnostic dispatch, request-cap change or model invocation is authorized by this proposal. All four rows must emit zero validated facts, newFactIds, semantic document validations, held claims, parent financial attribution and product financial/market events. The existing 16-company certification and 80 SEC claim review remain unchanged.

## Diagnostic-plan dependency: activation blocker

The existing repaired seven-target plan is pinned to `79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60`. Adding these four registry rows changes that global hash, including if all existing Ping/Delinea/Sonatype fields stay exact. The D-112-only historical bridge must continue to reject this registry change. Merely repinning the plan root or changing old receipt hashes would repeat the diagnosed failure.

Finish the current seven-target diagnostic and regular cycle first and retain their exact immutable policies, plans, observations and reservations. Before activating any registry candidate, prepare a separately reviewed provenance transition limited to these four source additions and the two exact subject sourceIds appends. Every other policy field and all three diagnostic candidate source/supplier contexts must remain exact. Bind a new current-policy root plan to the authentic completed 79cdd diagnostic; keep original historical bytes and dates. That new transition is a dependency, not an implemented or authorized extension of the D-112 bridge in this proposal.

Commit the eventual registry and matching diagnostic-plan/provenance repair together only after pure whole-plan validation under the final registry policy succeeds, including strict negative registry/source/alias/schedule/model tests. Until that composite candidate exists, these source rows remain blocked for activation. Normal required-task and roster counts stay 557/74, and no prior source/fact receipt is relabelled as fresh under the new global policy.
