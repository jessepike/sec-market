# Actual collector renewal audit, October 24, 2026

Manual collector `40042968468` completed 244/557 checks for the same 74 suppliers, 123 more than the prior 121. Independent reconciliation exactly reproduces its archived result at `2026-10-24T00:11:47.483353Z`. It completed with gaps and did not publish.

I would resolve the two correction reviews and inspect the already-started leased source-probe results next. No owner source choice blocks the work. Endpoint availability alone cannot qualify complete supplier coverage.

## Archive and budget

Revision `399f77608970c39c5f418af2e76982e86db54693`. Archive `cc898bbd1fcd6b9816d774b2b11b52c505f19201`. Manifest `bb56469079ab63c7dfc50cc39b1d73176e40b464ac4e181123ea4c3959ed3633`. All 29,562 files passed manifest verification, and every size/mtime entry remained unchanged. Run `be3ec51a71ea46309569073b255f5eeb5191165c012dde7c41aee3bdb752decd`. Raw snapshot `34b0c397b0259382ce3507e29e748d14592a62c8c549af09c1e52be500e985cd`.

The fixed archive ledger is 64/80 model calls, 33/40 documents and 377/5,500 fetches. Remaining at this archive only: 16 calls, seven documents and 5,123 fetches. October 23 remains byte-identical at 80/40/5,500. The acknowledged collector lease is released. A later source-probe archive supersedes these capacity figures.

## Exact task reasons

| Outcome | Reason | Tasks |
|---|---|---|
| blocked | HTTP_403 | 9 |
| blocked | HTTP_429 | 4 |
| checked_no_change | No error. | 244 |
| failed | Unapproved source/redirect host | 1 |
| not_checked | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 17 |
| not_checked | NO_REGISTERED_DISCOVERY_SOURCE | 254 |
| not_checked | SOURCE_BINDING_UNVERIFIED | 28 |

Successful checks comprise 196 citations, 32 SEC regulatory checks and 16 filing-document checks. Zero tasks failed for fetch allowance. Missing family bindings remain 254 and candidate registrations remain 28. The 17 bounded historical-audit tasks retain 9897 pending document references. Partial document facts do not complete their source task.

| Existing source task still unresolved | Reason | Pending documents |
|---|---|---|
| `axonius:citation:TR-axonius-1` | HTTP_429 | 0 |
| `sophos:citation:TR-sophos-3` | HTTP_403 | 0 |
| `cohesity:citation:TR-cohesity-1` | HTTP_403 | 0 |
| `delinea:citation:TR-delinea-5` | HTTP_403 | 0 |
| `axonius:citation:TR-axonius-3` | HTTP_429 | 0 |
| `beyondtrust:citation:TR-beyondtrust-1` | HTTP_403 | 0 |
| `sophos:citation:TR-sophos-2` | HTTP_403 | 0 |
| `tines:citation:TR-tines-1` | HTTP_403 | 0 |
| `delinea:citation:TR-delinea-3` | HTTP_403 | 0 |
| `axonius:citation:TR-axonius-2` | HTTP_429 | 0 |
| `bigid:citation:TR-bigid-1` | HTTP_403 | 0 |
| `sysdig:citation:TR-sysdig-1` | Unapproved source/redirect host | 0 |
| `axonius:official:1` | HTTP_429 | 0 |
| `proofpoint:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 211 |
| `cohesity:official:1` | HTTP_403 | 0 |
| `veeam:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 726 |
| `exabeam:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 636 |
| `hiddenlayer:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 87 |
| `optiv:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 179 |
| `aqua:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 448 |
| `mimecast:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 137 |
| `arctic-wolf:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 1296 |
| `witnessai:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 241 |
| `expel:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 329 |
| `ivanti:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 428 |
| `reliaquest:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 90 |
| `upwind:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 974 |
| `sophos:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 636 |
| `snyk:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 54 |
| `esentire:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 170 |
| `dragos:official:1` | HISTORICAL_OR_UNCHANGED_AUDIT_PENDING | 3255 |

The JSON retains all 557 original task receipts, source/family/URL joins, attempt paths and every cited observation with its original status, time and body hash. HTTP 403/429 remains blocked; Sysdig’s unapproved redirect host remains failed.

## Source ages

At audit time `2026-10-24T00:30:24.258312Z`, the 244 successful tasks cite 442 observation bindings: 111 fetched, 140 not-modified and 191 retained-immutable checks. Effective check times span `2026-10-24T00:05:06.295968Z` to `2026-10-24T00:06:05.593075Z`. The oldest effective age is 0.111 hours at original reconciliation and 0.422 hours at audit. Archived validity ends `2026-10-25T06:05:06.295968+00:00`.

The 191 immutable filing bodies retain October 20 fetched times and separately recorded fresh index verification. Both dates remain in the JSON. A retained-body check never renews an event date or old semantic review.

## Holds and quarantine

All 28 earlier candidate/reason holds remain open. Twenty-seven queue rows are byte-identical. Veeam’s month-only Securiti AI acquisition claim stays held with a new current-policy receipt pointer; its original held object remains unchanged. Three new HiddenLayer date-missing holds and one Proofpoint semantic-disagreement hold bring the queue to 32. Both Veeam receipt identities and all raw held objects remain pinned.

The raw collector snapshot has eight events: four prior events plus four new Proofpoint/Ivanti events supported by independently verified partial document receipts. Its archived actual published baseline has zero daily events. Isolated read-only publication projection yields four current-policy events, all 32 holds and exactly four older-policy quarantines. All object writes were intercepted in memory. This is not an actual gate or publication receipt.

| Old-policy candidate retained for quarantine | Supplier | Body SHA-256 | Original fetched time |
|---|---|---|---|
| `224b00aa63a063098804d0c66a4a94e3c2dfd2ccfde21cec84f6b5cf90bdbf14` | esentire | `fdf968725a257486319f6310cbe634262f5aa28950733bf5ea55ce061386a994` | `2026-10-22T01:15:11.031986Z` |
| `3b2898c3c70e8e2edb7fb3147d849751e046af41c0414d60fc6834076a80ae57` | veeam | `b0b5170289740b6f973d9d36045d74a375a8179f05cac030dd8bbf7aa40c9385` | `2026-10-22T01:19:41.757039Z` |
| `d8589772bc58cb801c3df57ec830f223f7aef17d01746d128e655b5efca31d71` | mimecast | `a9f6b8b041e6f1c9a6b34fbd042c14b201bed62d008c9953b0288f1166267186` | `2026-10-22T01:16:30.033827Z` |
| `df46b12d4f5430d97adc156e63f681977ac0f7c27f248eec63651ec4303830b3` | esentire | `2ccb24ddfbf84b3c3aa52fd5e3cc940339e5e02f09ed6d105affd5a7247b078f` | `2026-10-22T01:12:19.352443Z` |

All four original fact files are unchanged. Their review policy is `ea9fa9b42a96f6715839de0d51cb58f9238f13618e5aecad2f5575524c1679b1`; current policy is `de1932f7698d6b5ec86c23da52e77b1440c34d368e101c2aaabcbae6b39abfbe`. None is currently re-admitted. No collector continuity bug was demonstrated.

The exact boundary is `/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/gate.py`: line 58 verifies collector continuity; lines 77–78 require correction admissions; line 79 creates the publication snapshot from the archived production baseline and continuity. The two held correction groups currently stop ordinary gate preparation before that snapshot write.

## Actual correction reviews

Optiv, Splunk, Expel and the Xage publication-role group were accepted. Check Point source support failed; Zscaler source support was unknown and the review ambiguous. Other recorded checks passed. These actual review decisions remain in force. Four accepted groups do not establish a complete accepted bundle or a public release.

| Group | Actual result | Attempt object | Review object |
|---|---|---|---|
| `FC-20261023-checkpoint-sase` | rejected | `e1bf99e7516dfc3e648d3eae9a4968ee9e2edfa6e7666a5ef2bd4065bcd572f9` | `dd8de73b7d8f95b8bba647f80ef0d1e1a976b0571a4f1ac6a696923016c8ee68` |
| `FC-20261023-optiv` | accepted | `2d12fb074b83a7677d5f30317bc293eaeac157e51bd4225023875d8252528c39` | `faf2a5773a4b7eacd806e8a1995bc8719d8a12a2bfb30e0fa5e77db24d1df44c` |
| `FC-20261023-splunk` | accepted | `165d43a8a9d430a832b910db959fb521295b343ec1babaac1b08c955746370c4` | `f5366dfae77204b65cc05a3f5b6fd65f1c86bcc3edd38da0a342761667dc6887` |
| `FC-20261023-zscaler` | ambiguous | `92fd58797420c18e1ea36b56334d7276dc7d5d0a5ca86a9bd7e1264c9394d2ec` | `890c1cc09d894c5966751404930161d1c7bc5e897c4c1006d108b00cd931243f` |
| `FC-20261023-expel` | accepted | `7e729351e103378b72329f29a27b32e2492f23df05822cfbc8e6d8e1db65d946` | `d70505f6c750763f017bf3aa7ae88e366dfc0ffe2dcd6c47b599b56d59bed70f` |
| `XAGE-SOURCE-CLASS-20261023` | accepted | `5f7d33f76cbc3c940f1a28af6440e78bd0449458ec21e52b681ecfe9cf133956` | `5d806d7b4897fa6082cba2ae8b1a496b863ddfbd6af2721d4e1f957d93bfdf46` |

## Bounded source qualification

The current leased source_probe visits all 28 configured candidate bindings; no selector exists. It spends fetch capacity only and cannot activate a source. Review the actual terminal probe archive before another writer. The following historical literal leads guide qualification review; none was fetched or activated by this audit.

| Existing binding | Retained literal lead | Required proof |
|---|---|---|
| `delinea:official:1` | `https://delinea.com/news/rss.xml` | Supplier/item identity, dates, feed retention and every continuation. |
| `ping-identity:official:1` | `https://press.pingidentity.com/news-releases?pagetemplate=rss` | Official Ping release paths and current-window retention. |
| `sonatype:official:1` | `https://www.sonatype.com/press-releases/rss.xml` | Press-release scope, dates and complete traversal. |
| `orca:official:1` | `https://orca.security/resources/news/` | Actual page 2 and conservative terminal traversal. |
| `barracuda:official:1` | `https://www.barracuda.com/content/barracuda-corp/us/en/company/news/jcr:content/root/container/container/news_room.news_room.json` | Disclosed JSON filters/paging; empty shell stays incomplete. |

The JSON pins each literal disclosure to original primary observations and body hashes. Company and shared-distributor roots remain entry points. No unqualified endpoint earns coverage credit.

## Limits

Source/network/model calls, admissions, real state writes, quota changes, registrations and publication attempts were zero. Both archives and immutable original inventories remained unchanged. Only the two dated report files were written.

Detailed evidence: `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/renewal-collector-audit-2026-10-24.json`.
