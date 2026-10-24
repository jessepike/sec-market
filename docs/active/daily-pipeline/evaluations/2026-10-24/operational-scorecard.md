# Operational evaluation

Evaluated: 2026-10-24T02:17:24.003382Z
Revision: `26181a2d4eb0aad1bd751cda70ab8e65142d2813`
Run: `be3ec51a71ea46309569073b255f5eeb5191165c012dde7c41aee3bdb752decd`

Offline consistency evaluation of explicitly pinned supplied receipts. Does not authenticate GitHub or replay archived source bodies. No overall score.

| Measure | Status | Observed / required | Observed at | Evidence | Limitations |
|---|---|---|---|---|---|
| All declared source checks | fail | 244 / 557 | 2026-10-24T00:38:18.811621Z | coverage, contract | Receipt-level source checks; does not establish every historical claim is accurate. |
| SEC source checks | pass | 48 / 48 | 2026-10-24T00:38:18.811621Z | coverage, contract | SEC source checks are distinct from the independent SEC claim gate. |
| Age of the collection check | pass | 1.65h / maximum 30h | 2026-10-24T00:38:18.811621Z | coverage, contract | Collection check age only. This evaluator does not replay archived observation bodies. |
| Freshness across the declared roster | fail | 244 / 557 | 2026-10-24T00:38:18.811621Z | coverage, contract | Incomplete required source checks prevent a full-roster freshness pass. |
| Known release checks | pass | 4 / 4 | Not supplied | gate | Pinned gate receipt reports known checks, including SEC recomputation. Tests do not estimate all-site precision/recall. |
| Records included in the fixed source audit | unmeasured | unmeasured | Not supplied |  | No pinned published-claim audit supplied. |
| Known contradicting records in the fixed audit | unmeasured | unmeasured | Not supplied |  | No pinned published-claim audit supplied; passing release tests do not establish absence of factual errors. |
| Claim accuracy on a reviewed benchmark | unmeasured | unmeasured | Not supplied |  | No fixed reviewed benchmark and scoring denominators supplied. |
| Eligible events found on a reviewed benchmark | unmeasured | unmeasured | Not supplied |  | No fixed reviewed benchmark and scoring denominators supplied. |
| Actual scheduled collection | unmeasured | unmeasured | Not supplied |  | No scheduled collector receipt supplied. |
| Exact release publication | pass | 1 / 1 | Not supplied | publication, gate | Pinned historical acceptance; not a new live probe. |
| Rollback and restoration | pass | 1 / 1 | 2026-10-24T01:51:46.523836Z | rollback, publication | Legacy baseline full byte inventory may be unavailable; retain that limitation. |
| Preserved facts and pending work | unmeasured | unmeasured | Not supplied |  | No pinned held-claim/historical-data continuity audit supplied. Rollback/tests do not establish preservation. |
| Sustained operation | unmeasured | unmeasured | Not supplied |  | No complete observation-window history supplied; one cycle cannot establish durability over time. |
| Observed reader value | unmeasured | unmeasured | Not supplied |  | Owner reports no observed real use yet. Technical reliability, accuracy and freshness are the current priority. |

## Pinned inputs

- contract: `operational-inputs/contract.json` SHA-256 `327e52fdab4f97d3f0d628978501aa7197b31ddadb4006d16d3f776a8acb47c0`
- coverage: `operational-inputs/coverage.json` SHA-256 `dd2b9964d49530c86429d5278a393f63ca8ecae9c35208b2b2ff45cafb1c5f35`
- gate: `../../receipts/repair-main-gate-result-2026-10-24.json` SHA-256 `fe32b8e1717c3c4163240d3c68b1950b472d7de911b15461d2b900ad15d0a96a`
- publication: `../../receipts/repair-publication-result-2026-10-24.json` SHA-256 `40b0ce787fc9f6e4ef1c427f57d67aea343e9545e2f59d43bf8140e83a5ef745`
- rollback: `../../receipts/repair-release-rollback-result-2026-10-24.json` SHA-256 `cb101d02b7784e3b82cc8b24115e96548b97729591fe06860e6c68c87bd916aa`

## Coverage inventory

244/557 successful required checks; 313 gaps. 275 verified registered bindings, 28 candidate bindings, 254 missing bindings.

Verified registration is not a successful source check. 557 total obligations remain the primary denominator. Domain totals can overlap for suppliers in multiple domains.

### By family

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| citation integrity | 196 / 208 | 208 | 0 | 0 | blocked: 11, checked_no_change: 196, failed: 1 |
| filing documents | 16 / 27 | 16 | 0 | 11 | checked_no_change: 16, not_checked: 11 |
| independent reporting | 0 / 74 | 0 | 0 | 74 | not_checked: 74 |
| investor acquirer | 0 / 56 | 3 | 1 | 52 | not_checked: 56 |
| official announcements | 0 / 75 | 16 | 20 | 39 | blocked: 2, not_checked: 73 |
| regulatory filings | 32 / 43 | 32 | 0 | 11 | checked_no_change: 32, not_checked: 11 |
| release distribution | 0 / 74 | 0 | 7 | 67 | not_checked: 74 |

### By supplier

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| Abnormal Security | 2 / 6 | 2 | 1 | 3 | checked_no_change: 2, not_checked: 4 |
| Aqua Security | 3 / 7 | 4 | 1 | 2 | checked_no_change: 3, not_checked: 4 |
| Arctic Wolf Networks, Inc. | 2 / 6 | 3 | 0 | 3 | checked_no_change: 2, not_checked: 4 |
| Armis Security Ltd. | 2 / 6 | 2 | 0 | 4 | checked_no_change: 2, not_checked: 4 |
| Axonius, Inc. | 0 / 7 | 4 | 0 | 3 | blocked: 4, not_checked: 3 |
| Barracuda Networks | 1 / 5 | 1 | 1 | 3 | checked_no_change: 1, not_checked: 4 |
| BeyondTrust | 0 / 5 | 1 | 1 | 3 | blocked: 1, not_checked: 4 |
| BigID | 0 / 5 | 1 | 0 | 4 | blocked: 1, not_checked: 4 |
| Cato Networks | 3 / 7 | 3 | 1 | 3 | checked_no_change: 3, not_checked: 4 |
| Chainguard | 2 / 6 | 2 | 1 | 3 | checked_no_change: 2, not_checked: 4 |
| Check Point Email Security | 2 / 9 | 2 | 2 | 5 | checked_no_change: 2, not_checked: 7 |
| Check Point | 5 / 10 | 5 | 1 | 4 | checked_no_change: 5, not_checked: 5 |
| Claroty Ltd. | 1 / 5 | 1 | 0 | 4 | checked_no_change: 1, not_checked: 4 |
| Cloudflare | 10 / 13 | 10 | 0 | 3 | checked_no_change: 10, not_checked: 3 |
| Cohesity | 0 / 5 | 2 | 0 | 3 | blocked: 2, not_checked: 3 |
| Commvault Systems, Inc. | 11 / 14 | 11 | 0 | 3 | checked_no_change: 11, not_checked: 3 |
| CrowdStrike Holdings, Inc. | 9 / 12 | 9 | 0 | 3 | checked_no_change: 9, not_checked: 3 |
| CrowdStrike Falcon Exposure Management | 1 / 7 | 1 | 0 | 6 | checked_no_change: 1, not_checked: 6 |
| CyberArk | 2 / 6 | 2 | 0 | 4 | checked_no_change: 2, not_checked: 4 |
| Cyera | 5 / 9 | 5 | 1 | 3 | checked_no_change: 5, not_checked: 4 |
| Delinea | 2 / 8 | 4 | 2 | 2 | blocked: 2, checked_no_change: 2, not_checked: 4 |
| Dragos, Inc. | 2 / 6 | 3 | 0 | 3 | checked_no_change: 2, not_checked: 4 |
| eSentire, Inc. | 1 / 5 | 2 | 0 | 3 | checked_no_change: 1, not_checked: 4 |
| Exabeam, Inc. | 1 / 5 | 2 | 0 | 3 | checked_no_change: 1, not_checked: 4 |
| Expel, Inc. | 2 / 6 | 3 | 0 | 3 | checked_no_change: 2, not_checked: 4 |
| Forescout Technologies, Inc. | 1 / 5 | 1 | 1 | 3 | checked_no_change: 1, not_checked: 4 |
| Fortinet | 6 / 9 | 6 | 0 | 3 | checked_no_change: 6, not_checked: 3 |
| GitHub Advanced Security | 1 / 7 | 1 | 1 | 5 | checked_no_change: 1, not_checked: 6 |
| Google SecOps | 1 / 7 | 1 | 0 | 6 | checked_no_change: 1, not_checked: 6 |
| HiddenLayer, Inc. | 1 / 5 | 2 | 0 | 3 | checked_no_change: 1, not_checked: 4 |
| Ivanti, Inc. | 2 / 6 | 3 | 0 | 3 | checked_no_change: 2, not_checked: 4 |
| JFrog Ltd. | 6 / 9 | 6 | 1 | 2 | checked_no_change: 6, not_checked: 3 |
| Lakera AI (Lakera) | 1 / 5 | 1 | 0 | 4 | checked_no_change: 1, not_checked: 4 |
| Mimecast | 2 / 6 | 3 | 0 | 3 | checked_no_change: 2, not_checked: 4 |
| Microsoft Defender for Endpoint | 1 / 7 | 1 | 0 | 6 | checked_no_change: 1, not_checked: 6 |
| Microsoft Defender for Office 365 | 1 / 7 | 1 | 0 | 6 | checked_no_change: 1, not_checked: 6 |
| Microsoft Entra ID | 1 / 7 | 1 | 0 | 6 | checked_no_change: 1, not_checked: 6 |
| Netskope | 9 / 12 | 9 | 0 | 3 | checked_no_change: 9, not_checked: 3 |
| Nozomi Networks, Inc. | 2 / 6 | 2 | 1 | 3 | checked_no_change: 2, not_checked: 4 |
| Okta | 13 / 16 | 13 | 0 | 3 | checked_no_change: 13, not_checked: 3 |
| Optiv Security Inc. | 3 / 7 | 4 | 0 | 3 | checked_no_change: 3, not_checked: 4 |
| Orca Security | 2 / 6 | 2 | 1 | 3 | checked_no_change: 2, not_checked: 4 |
| Palo Alto Networks, Inc. | 14 / 17 | 14 | 0 | 3 | checked_no_change: 14, not_checked: 3 |
| Palo Alto Networks Cortex XSIAM | 1 / 7 | 1 | 0 | 6 | checked_no_change: 1, not_checked: 6 |
| Ping Identity | 3 / 7 | 3 | 2 | 2 | checked_no_change: 3, not_checked: 4 |
| Proofpoint | 2 / 6 | 3 | 0 | 3 | checked_no_change: 2, not_checked: 4 |
| Protect AI, Inc. | 1 / 5 | 1 | 0 | 4 | checked_no_change: 1, not_checked: 4 |
| Qualys, Inc. | 7 / 10 | 7 | 0 | 3 | checked_no_change: 7, not_checked: 3 |
| Rapid7, Inc. | 12 / 15 | 12 | 1 | 2 | checked_no_change: 12, not_checked: 3 |
| Red Canary, Inc. | 1 / 5 | 1 | 0 | 4 | checked_no_change: 1, not_checked: 4 |
| ReliaQuest, LLC | 2 / 6 | 3 | 0 | 3 | checked_no_change: 2, not_checked: 4 |
| Rubrik, Inc. | 9 / 12 | 9 | 1 | 2 | checked_no_change: 9, not_checked: 3 |
| SentinelOne, Inc. | 11 / 14 | 11 | 0 | 3 | checked_no_change: 11, not_checked: 3 |
| SailPoint | 8 / 11 | 8 | 0 | 3 | checked_no_change: 8, not_checked: 3 |
| Snyk, Inc. | 2 / 6 | 3 | 0 | 3 | checked_no_change: 2, not_checked: 4 |
| Sonatype Inc. | 2 / 6 | 2 | 1 | 3 | checked_no_change: 2, not_checked: 4 |
| Sophos Group (Sophos Ltd) | 1 / 7 | 4 | 0 | 3 | blocked: 2, checked_no_change: 1, not_checked: 4 |
| Splunk | 2 / 8 | 2 | 0 | 6 | checked_no_change: 2, not_checked: 6 |
| SurePath AI, Inc. | 1 / 5 | 1 | 0 | 4 | checked_no_change: 1, not_checked: 4 |
| Sysdig | 0 / 5 | 1 | 1 | 3 | failed: 1, not_checked: 4 |
| Tenable Holdings, Inc. | 9 / 12 | 9 | 0 | 3 | checked_no_change: 9, not_checked: 3 |
| Tines | 0 / 5 | 1 | 0 | 4 | blocked: 1, not_checked: 4 |
| Torq | 2 / 6 | 2 | 1 | 3 | checked_no_change: 2, not_checked: 4 |
| Trend Micro Incorporated | 1 / 6 | 1 | 1 | 4 | checked_no_change: 1, not_checked: 5 |
| Trustwave Holdings, Inc. | 1 / 5 | 1 | 1 | 3 | checked_no_change: 1, not_checked: 4 |
| Upwind | 2 / 6 | 3 | 0 | 3 | checked_no_change: 2, not_checked: 4 |
| Varonis Systems, Inc. | 9 / 12 | 9 | 0 | 3 | checked_no_change: 9, not_checked: 3 |
| Veeam Software | 3 / 7 | 4 | 0 | 3 | checked_no_change: 3, not_checked: 4 |
| Veracode, Inc. | 1 / 5 | 1 | 1 | 3 | checked_no_change: 1, not_checked: 4 |
| WitnessAI | 1 / 5 | 2 | 0 | 3 | checked_no_change: 1, not_checked: 4 |
| Wiz | 1 / 5 | 1 | 0 | 4 | checked_no_change: 1, not_checked: 4 |
| Xage Security, Inc. | 1 / 5 | 1 | 0 | 4 | checked_no_change: 1, not_checked: 4 |
| Zenity | 1 / 5 | 1 | 1 | 3 | checked_no_change: 1, not_checked: 4 |
| Zscaler | 11 / 14 | 11 | 0 | 3 | checked_no_change: 11, not_checked: 3 |

### By domain

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| ai security | 20 / 47 | 22 | 1 | 24 | checked_no_change: 20, not_checked: 27 |
| appsec | 14 / 39 | 15 | 5 | 19 | checked_no_change: 14, not_checked: 25 |
| cloud | 31 / 58 | 34 | 3 | 21 | checked_no_change: 31, failed: 1, not_checked: 26 |
| data | 37 / 64 | 41 | 2 | 21 | blocked: 3, checked_no_change: 37, not_checked: 24 |
| email | 15 / 49 | 17 | 5 | 27 | checked_no_change: 15, not_checked: 34 |
| endpoint xdr | 37 / 63 | 40 | 1 | 22 | blocked: 2, checked_no_change: 37, not_checked: 24 |
| exposure | 40 / 69 | 45 | 1 | 23 | blocked: 4, checked_no_change: 40, not_checked: 25 |
| identity | 29 / 60 | 32 | 5 | 23 | blocked: 3, checked_no_change: 29, not_checked: 28 |
| managed security | 12 / 40 | 17 | 1 | 22 | checked_no_change: 12, not_checked: 28 |
| network sase | 58 / 82 | 58 | 2 | 22 | checked_no_change: 58, not_checked: 24 |
| ot iot | 9 / 33 | 10 | 2 | 21 | checked_no_change: 9, not_checked: 24 |
| secops | 21 / 55 | 23 | 1 | 31 | blocked: 1, checked_no_change: 21, not_checked: 33 |

### By reason

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| HISTORICAL OR UNCHANGED AUDIT PENDING | 0 / 17 | 17 | 0 | 0 | not_checked: 17 |
| HTTP 403 | 0 / 9 | 9 | 0 | 0 | blocked: 9 |
| HTTP 429 | 0 / 4 | 4 | 0 | 0 | blocked: 4 |
| NO REGISTERED DISCOVERY SOURCE | 0 / 254 | 0 | 0 | 254 | not_checked: 254 |
| SOURCE BINDING UNVERIFIED | 0 / 28 | 0 | 28 | 0 | not_checked: 28 |
| Unapproved source/redirect host | 0 / 1 | 1 | 0 | 0 | failed: 1 |
| successful | 244 / 244 | 244 | 0 | 0 | checked_no_change: 244 |

## Next actions by evidence gap

- Missing bindings: qualify an explicit source and adapter against archived primary evidence; preserve the obligation until registered.
- Candidate bindings: verify entity scope, date boundaries, pagination and positive/quiet/blocked cases before awarding coverage.
- Fetch or model caps: retain the charged limits and queue; retry only in an authorized later allowance and reuse valid prior checks.
- Blocked or failed pages: inspect the retained failure and repair the adapter or document a supported alternate primary source.
- Held claims: preserve the review queue and resolve source/date/status support before publication; do not infer an owner decision from a machine hold.
