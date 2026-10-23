# Operational evaluation

Evaluated: 2026-10-23T18:11:16.090121+00:00
Revision: `7bd94ec77e99462c068f254e134235a894585cbb`
Run: `e054ea73c89fe78db9702f94d2a3b669ce91884f7d7abda0a88698dbcfc7ec50`

Offline consistency evaluation of explicitly pinned supplied receipts. Does not authenticate GitHub or replay archived source bodies. No overall score.

| Measure | Status | Observed / required | Observed at | Evidence | Limitations |
|---|---|---|---|---|---|
| All declared source checks | fail | 121 / 557 | 2026-10-23T11:34:15.010723Z | coverage, contract | Receipt-level source checks; does not establish every historical claim is accurate. |
| SEC source checks | pass | 48 / 48 | 2026-10-23T11:34:15.010723Z | coverage, contract | SEC source checks are distinct from the independent SEC claim gate. |
| Age of the collection check | pass | 6.62h / maximum 30h | 2026-10-23T11:34:15.010723Z | coverage, contract | Collection check age only. This evaluator does not replay archived observation bodies. |
| Freshness across the declared roster | fail | 121 / 557 | 2026-10-23T11:34:15.010723Z | coverage, contract | Incomplete required source checks prevent a full-roster freshness pass. |
| Known release checks | pass | 4 / 4 | Not supplied | gate | Pinned gate receipt reports known checks, including SEC recomputation. Tests do not estimate all-site precision/recall. |
| Claim accuracy on a reviewed benchmark | unmeasured | unmeasured | Not supplied |  | No fixed reviewed benchmark and scoring denominators supplied. |
| Eligible events found on a reviewed benchmark | unmeasured | unmeasured | Not supplied |  | No fixed reviewed benchmark and scoring denominators supplied. |
| Actual scheduled collection | pass | 1 / 1 | 2026-10-23T11:34:15.010723Z | collection | One pinned cycle; not a sustained-operation rate. |
| Exact release publication | pass | 1 / 1 | Not supplied | publication, gate | Pinned historical acceptance; not a new live probe. |
| Rollback and restoration | pass | 1 / 1 | 2026-10-23T11:46:13.860251Z | rollback, publication | Legacy baseline full byte inventory may be unavailable; retain that limitation. |
| Preserved facts and pending work | fail | 0 / 2 | 2026-10-23T17:42:59Z | continuity | Held claims and historical facts require explicit preservation checks; operational rollback cannot substitute for these. |
| Unresolved reviews retained | fail | 14 / 28 retained | 2026-10-23T17:42:59Z | continuity | Durable retention or quarantine; not publication eligibility. |
| Historical candidates retained or quarantined | fail | 0 / 4 retained | 2026-10-23T17:42:59Z | continuity | Durable retention or quarantine; not publication eligibility. |
| Sustained operation | unmeasured | unmeasured | Not supplied |  | No complete observation-window history supplied; one cycle cannot establish durability over time. |
| Observed reader value | unmeasured | unmeasured | Not supplied |  | Owner reports no observed real use yet. Technical reliability, accuracy and freshness are the current priority. |

## Pinned inputs

- contract: `inputs/contract.json` SHA-256 `327e52fdab4f97d3f0d628978501aa7197b31ddadb4006d16d3f776a8acb47c0`
- coverage: `inputs/coverage.json` SHA-256 `370c35cf48074658a53f920c66b4ba1e4be711a158111fd04a03ad9c8cfde410`
- gate: `../../receipts/accepted-main-gate-2026-10-23.json` SHA-256 `0e5ea2283ff87a6857b368450aab05e9e4b51cd4408cfd00b3fe9c85ec693bab`
- collection: `../../receipts/actual-scheduled-collection-2026-10-23.json` SHA-256 `9e7bb3dc4b263bd483f9f750f6d9a9d5ffca42bbcdd91f3031cba6496973a6a4`
- publication: `../../receipts/actual-publication-2026-10-23.json` SHA-256 `df48bd23d296d6fe7ebc93e970ae980bba480bcaf8b6dc4b564457397e2e5af7`
- rollback: `../../receipts/actual-rollback-restoration-2026-10-23.json` SHA-256 `4a3a4d390970bba171ce35f466b6e7fb98e8ddb002d970d4dfe7cd43134f0ebb`
- continuity: `../../receipts/data-continuity-baseline-2026-10-23.json` SHA-256 `b8b48d9ddddc6be0fc38b977fe1a6ac688c8cf55e5b799a507ea277dba263a9f`

## Coverage inventory

121/557 successful required checks; 436 gaps. 275 verified registered bindings, 28 candidate bindings, 254 missing bindings.

Verified registration is not a successful source check. 557 total obligations remain the primary denominator. Domain totals can overlap for suppliers in multiple domains.

### By family

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| citation integrity | 73 / 208 | 208 | 0 | 0 | blocked: 5, checked_no_change: 73, failed: 130 |
| filing documents | 16 / 27 | 16 | 0 | 11 | checked_no_change: 16, not_checked: 11 |
| independent reporting | 0 / 74 | 0 | 0 | 74 | not_checked: 74 |
| investor acquirer | 0 / 56 | 3 | 1 | 52 | failed: 3, not_checked: 53 |
| official announcements | 0 / 75 | 16 | 20 | 39 | failed: 16, not_checked: 59 |
| regulatory filings | 32 / 43 | 32 | 0 | 11 | checked_no_change: 32, not_checked: 11 |
| release distribution | 0 / 74 | 0 | 7 | 67 | not_checked: 74 |

### By supplier

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| Abnormal Security | 1 / 6 | 2 | 1 | 3 | checked_no_change: 1, failed: 1, not_checked: 4 |
| Aqua Security | 1 / 7 | 4 | 1 | 2 | checked_no_change: 1, failed: 3, not_checked: 3 |
| Arctic Wolf Networks, Inc. | 0 / 6 | 3 | 0 | 3 | failed: 3, not_checked: 3 |
| Armis Security Ltd. | 0 / 6 | 2 | 0 | 4 | failed: 2, not_checked: 4 |
| Axonius, Inc. | 0 / 7 | 4 | 0 | 3 | failed: 4, not_checked: 3 |
| Barracuda Networks | 1 / 5 | 1 | 1 | 3 | checked_no_change: 1, not_checked: 4 |
| BeyondTrust | 0 / 5 | 1 | 1 | 3 | failed: 1, not_checked: 4 |
| BigID | 0 / 5 | 1 | 0 | 4 | blocked: 1, not_checked: 4 |
| Cato Networks | 1 / 7 | 3 | 1 | 3 | checked_no_change: 1, failed: 2, not_checked: 4 |
| Chainguard | 0 / 6 | 2 | 1 | 3 | failed: 2, not_checked: 4 |
| Check Point Email Security | 0 / 9 | 2 | 2 | 5 | failed: 2, not_checked: 7 |
| Check Point | 2 / 10 | 5 | 1 | 4 | checked_no_change: 2, failed: 3, not_checked: 5 |
| Claroty Ltd. | 1 / 5 | 1 | 0 | 4 | checked_no_change: 1, not_checked: 4 |
| Cloudflare | 6 / 13 | 10 | 0 | 3 | checked_no_change: 6, failed: 4, not_checked: 3 |
| Cohesity | 0 / 5 | 2 | 0 | 3 | failed: 2, not_checked: 3 |
| Commvault Systems, Inc. | 7 / 14 | 11 | 0 | 3 | checked_no_change: 7, failed: 4, not_checked: 3 |
| CrowdStrike Holdings, Inc. | 7 / 12 | 9 | 0 | 3 | checked_no_change: 7, failed: 2, not_checked: 3 |
| CrowdStrike Falcon Exposure Management | 1 / 7 | 1 | 0 | 6 | checked_no_change: 1, not_checked: 6 |
| CyberArk | 1 / 6 | 2 | 0 | 4 | checked_no_change: 1, failed: 1, not_checked: 4 |
| Cyera | 3 / 9 | 5 | 1 | 3 | checked_no_change: 3, failed: 2, not_checked: 4 |
| Delinea | 0 / 8 | 4 | 2 | 2 | blocked: 2, failed: 2, not_checked: 4 |
| Dragos, Inc. | 0 / 6 | 3 | 0 | 3 | failed: 3, not_checked: 3 |
| eSentire, Inc. | 1 / 5 | 2 | 0 | 3 | checked_no_change: 1, failed: 1, not_checked: 3 |
| Exabeam, Inc. | 1 / 5 | 2 | 0 | 3 | checked_no_change: 1, failed: 1, not_checked: 3 |
| Expel, Inc. | 1 / 6 | 3 | 0 | 3 | checked_no_change: 1, failed: 2, not_checked: 3 |
| Forescout Technologies, Inc. | 1 / 5 | 1 | 1 | 3 | checked_no_change: 1, not_checked: 4 |
| Fortinet | 3 / 9 | 6 | 0 | 3 | checked_no_change: 3, failed: 3, not_checked: 3 |
| GitHub Advanced Security | 1 / 7 | 1 | 1 | 5 | checked_no_change: 1, not_checked: 6 |
| Google SecOps | 1 / 7 | 1 | 0 | 6 | checked_no_change: 1, not_checked: 6 |
| HiddenLayer, Inc. | 1 / 5 | 2 | 0 | 3 | checked_no_change: 1, failed: 1, not_checked: 3 |
| Ivanti, Inc. | 1 / 6 | 3 | 0 | 3 | checked_no_change: 1, failed: 2, not_checked: 3 |
| JFrog Ltd. | 4 / 9 | 6 | 1 | 2 | checked_no_change: 4, failed: 2, not_checked: 3 |
| Lakera AI (Lakera) | 0 / 5 | 1 | 0 | 4 | failed: 1, not_checked: 4 |
| Mimecast | 0 / 6 | 3 | 0 | 3 | failed: 3, not_checked: 3 |
| Microsoft Defender for Endpoint | 0 / 7 | 1 | 0 | 6 | failed: 1, not_checked: 6 |
| Microsoft Defender for Office 365 | 0 / 7 | 1 | 0 | 6 | failed: 1, not_checked: 6 |
| Microsoft Entra ID | 0 / 7 | 1 | 0 | 6 | failed: 1, not_checked: 6 |
| Netskope | 6 / 12 | 9 | 0 | 3 | checked_no_change: 6, failed: 3, not_checked: 3 |
| Nozomi Networks, Inc. | 1 / 6 | 2 | 1 | 3 | checked_no_change: 1, failed: 1, not_checked: 4 |
| Okta | 8 / 16 | 13 | 0 | 3 | checked_no_change: 8, failed: 5, not_checked: 3 |
| Optiv Security Inc. | 2 / 7 | 4 | 0 | 3 | checked_no_change: 2, failed: 2, not_checked: 3 |
| Orca Security | 1 / 6 | 2 | 1 | 3 | checked_no_change: 1, failed: 1, not_checked: 4 |
| Palo Alto Networks, Inc. | 6 / 17 | 14 | 0 | 3 | checked_no_change: 6, failed: 8, not_checked: 3 |
| Palo Alto Networks Cortex XSIAM | 0 / 7 | 1 | 0 | 6 | failed: 1, not_checked: 6 |
| Ping Identity | 1 / 7 | 3 | 2 | 2 | checked_no_change: 1, failed: 2, not_checked: 4 |
| Proofpoint | 1 / 6 | 3 | 0 | 3 | checked_no_change: 1, failed: 2, not_checked: 3 |
| Protect AI, Inc. | 0 / 5 | 1 | 0 | 4 | failed: 1, not_checked: 4 |
| Qualys, Inc. | 3 / 10 | 7 | 0 | 3 | checked_no_change: 3, failed: 4, not_checked: 3 |
| Rapid7, Inc. | 9 / 15 | 12 | 1 | 2 | checked_no_change: 9, failed: 3, not_checked: 3 |
| Red Canary, Inc. | 0 / 5 | 1 | 0 | 4 | failed: 1, not_checked: 4 |
| ReliaQuest, LLC | 0 / 6 | 3 | 0 | 3 | failed: 3, not_checked: 3 |
| Rubrik, Inc. | 4 / 12 | 9 | 1 | 2 | checked_no_change: 4, failed: 5, not_checked: 3 |
| SentinelOne, Inc. | 5 / 14 | 11 | 0 | 3 | checked_no_change: 5, failed: 6, not_checked: 3 |
| SailPoint | 5 / 11 | 8 | 0 | 3 | checked_no_change: 5, failed: 3, not_checked: 3 |
| Snyk, Inc. | 0 / 6 | 3 | 0 | 3 | failed: 3, not_checked: 3 |
| Sonatype Inc. | 0 / 6 | 2 | 1 | 3 | failed: 2, not_checked: 4 |
| Sophos Group (Sophos Ltd) | 0 / 7 | 4 | 0 | 3 | blocked: 1, failed: 3, not_checked: 3 |
| Splunk | 0 / 8 | 2 | 0 | 6 | failed: 2, not_checked: 6 |
| SurePath AI, Inc. | 1 / 5 | 1 | 0 | 4 | checked_no_change: 1, not_checked: 4 |
| Sysdig | 0 / 5 | 1 | 1 | 3 | failed: 1, not_checked: 4 |
| Tenable Holdings, Inc. | 5 / 12 | 9 | 0 | 3 | checked_no_change: 5, failed: 4, not_checked: 3 |
| Tines | 0 / 5 | 1 | 0 | 4 | blocked: 1, not_checked: 4 |
| Torq | 1 / 6 | 2 | 1 | 3 | checked_no_change: 1, failed: 1, not_checked: 4 |
| Trend Micro Incorporated | 0 / 6 | 1 | 1 | 4 | failed: 1, not_checked: 5 |
| Trustwave Holdings, Inc. | 0 / 5 | 1 | 1 | 3 | failed: 1, not_checked: 4 |
| Upwind | 2 / 6 | 3 | 0 | 3 | checked_no_change: 2, failed: 1, not_checked: 3 |
| Varonis Systems, Inc. | 6 / 12 | 9 | 0 | 3 | checked_no_change: 6, failed: 3, not_checked: 3 |
| Veeam Software | 1 / 7 | 4 | 0 | 3 | checked_no_change: 1, failed: 3, not_checked: 3 |
| Veracode, Inc. | 0 / 5 | 1 | 1 | 3 | failed: 1, not_checked: 4 |
| WitnessAI | 0 / 5 | 2 | 0 | 3 | failed: 2, not_checked: 3 |
| Wiz | 0 / 5 | 1 | 0 | 4 | failed: 1, not_checked: 4 |
| Xage Security, Inc. | 0 / 5 | 1 | 0 | 4 | failed: 1, not_checked: 4 |
| Zenity | 0 / 5 | 1 | 1 | 3 | failed: 1, not_checked: 4 |
| Zscaler | 6 / 14 | 11 | 0 | 3 | checked_no_change: 6, failed: 5, not_checked: 3 |

### By domain

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| ai security | 8 / 47 | 22 | 1 | 24 | checked_no_change: 8, failed: 14, not_checked: 25 |
| appsec | 5 / 39 | 15 | 5 | 19 | checked_no_change: 5, failed: 10, not_checked: 24 |
| cloud | 17 / 58 | 34 | 3 | 21 | checked_no_change: 17, failed: 17, not_checked: 24 |
| data | 21 / 64 | 41 | 2 | 21 | blocked: 1, checked_no_change: 21, failed: 19, not_checked: 23 |
| email | 5 / 49 | 17 | 5 | 27 | checked_no_change: 5, failed: 12, not_checked: 32 |
| endpoint xdr | 18 / 63 | 40 | 1 | 22 | blocked: 1, checked_no_change: 18, failed: 21, not_checked: 23 |
| exposure | 26 / 69 | 45 | 1 | 23 | checked_no_change: 26, failed: 19, not_checked: 24 |
| identity | 15 / 60 | 32 | 5 | 23 | blocked: 2, checked_no_change: 15, failed: 15, not_checked: 28 |
| managed security | 4 / 40 | 17 | 1 | 22 | checked_no_change: 4, failed: 13, not_checked: 23 |
| network sase | 30 / 82 | 58 | 2 | 22 | checked_no_change: 30, failed: 28, not_checked: 24 |
| ot iot | 3 / 33 | 10 | 2 | 21 | checked_no_change: 3, failed: 7, not_checked: 23 |
| secops | 9 / 55 | 23 | 1 | 31 | blocked: 1, checked_no_change: 9, failed: 13, not_checked: 32 |

### By reason

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| FETCHES BUDGET EXHAUSTED | 0 / 149 | 149 | 0 | 0 | failed: 149 |
| HTTP 403 | 0 / 5 | 5 | 0 | 0 | blocked: 5 |
| NO REGISTERED DISCOVERY SOURCE | 0 / 254 | 0 | 0 | 254 | not_checked: 254 |
| SOURCE BINDING UNVERIFIED | 0 / 28 | 0 | 28 | 0 | not_checked: 28 |
| successful | 121 / 121 | 121 | 0 | 0 | checked_no_change: 121 |

## Next actions by evidence gap

- Missing bindings: qualify an explicit source and adapter against archived primary evidence; preserve the obligation until registered.
- Candidate bindings: verify entity scope, date boundaries, pagination and positive/quiet/blocked cases before awarding coverage.
- Fetch or model caps: retain the charged limits and queue; retry only in an authorized later allowance and reuse valid prior checks.
- Blocked or failed pages: inspect the retained failure and repair the adapter or document a supported alternate primary source.
- Held claims: preserve the review queue and resolve source/date/status support before publication; do not infer an owner decision from a machine hold.
