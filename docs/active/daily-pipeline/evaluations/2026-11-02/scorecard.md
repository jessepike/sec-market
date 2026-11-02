# Operational evaluation

Evaluated: 2026-11-02T17:05:36Z
Revision: `2aa87f5dd3182bc214f6efee10e709e5114a06ad`
Run: `51a9fbabd0cbd69cdbb807ac97f0baa5519cd8b53962bdff9f6c6096b8cf0b97`

Offline consistency evaluation of explicitly pinned supplied receipts. Does not authenticate GitHub or replay archived source bodies. No overall score.

| Measure | Status | Observed / required | Observed at | Evidence | Limitations |
|---|---|---|---|---|---|
| Daily source intake | fail | 262 / 557 | 2026-11-02T13:47:47.878832Z | coverage, contract | Fresh source intake only; processing and historical review are separate. No complete-event or all-site accuracy claim. |
| Observed document processing | fail | 83 / 11671 | 2026-11-02T13:47:47.878832Z | coverage, contract | Source/URL inventory; reviewed documents can contain held claims. Pinned counters are not source-body authentication or an accuracy estimate. |
| Retained historical review | fail | 84 / 11671 | 2026-11-02T13:47:47.878832Z | coverage, contract | Source/URL inventory; reviewed documents can contain held claims. Pinned counters are not source-body authentication or an accuracy estimate. |
| SEC source checks | pass | 48 / 48 | 2026-11-02T13:47:47.878832Z | coverage, contract | SEC source checks are distinct from the independent SEC claim gate. |
| Age of the collection check | pass | 3.30h / maximum 30h | 2026-11-02T13:47:47.878832Z | coverage, contract | Collection check age only. This evaluator does not replay archived observation bodies. |
| Fresh intake across the declared roster | fail | 262 / 557 | 2026-11-02T13:47:47.878832Z | coverage, contract | Fresh intake across the declared roster only; pending processing and history remain separately visible. |
| Known release checks | pass | 4 / 4 | Not supplied | gate | Pinned gate receipt reports known checks, including SEC recomputation. Tests do not estimate all-site precision/recall. |
| Records included in the fixed source audit | unmeasured | unmeasured | Not supplied |  | No pinned published-claim audit supplied. |
| Known contradicting records in the fixed audit | unmeasured | unmeasured | Not supplied |  | No pinned published-claim audit supplied; passing release tests do not establish absence of factual errors. |
| Claim accuracy on a reviewed benchmark | unmeasured | unmeasured | Not supplied |  | No fixed reviewed benchmark and scoring denominators supplied. |
| Eligible events found on a reviewed benchmark | unmeasured | unmeasured | Not supplied |  | No fixed reviewed benchmark and scoring denominators supplied. |
| Actual scheduled collection | pass | 1 / 1 | 2026-11-02T13:47:47.878832Z | collection | One pinned scheduled cycle; not a sustained-operation rate. |
| Exact release publication | pass | 1 / 1 | Not supplied | publication, gate | Pinned historical acceptance; not a new live probe. |
| Rollback and restoration | unmeasured | unmeasured | Not supplied |  | No rollback/restoration receipt supplied. |
| Preserved facts and pending work | unmeasured | unmeasured | Not supplied |  | No pinned held-claim/historical-data continuity audit supplied. Rollback/tests do not establish preservation. |
| Sustained operation | unmeasured | unmeasured | Not supplied |  | No complete observation-window history supplied; one cycle cannot establish durability over time. |
| Observed reader value | unmeasured | unmeasured | Not supplied |  | Owner reports no observed real use yet. Technical reliability, accuracy and freshness are the current priority. |

## Pinned inputs

- contract: `inputs/contract.json` SHA-256 `bb9735d073e41a0a22bdcfd315419c59e8791b82be34bc73ead699530147b3e6`
- coverage: `inputs/coverage.json` SHA-256 `9e66f87384806876cdbee573e856a2e4098d7e914dd949be3b5b7b83831a3def`
- gate: `inputs/gate.json` SHA-256 `0a82fcafc9759d5b5f295efeb54f2df04846a979e13f4c9baffdafd15753b8f3`
- collection: `inputs/collection.json` SHA-256 `db4d8b6bb45dd489fa9f89d9c333fc8996dd696f2163846a0cb8b0a1e785882b`
- publication: `inputs/publication.json` SHA-256 `3a1c94547f0560134d113cffa1e450e648c7f07b96000cffc8820d494b8f0e26`

## Coverage inventory

262/557 successful required checks; 295 gaps. 280 verified registered bindings, 23 candidate bindings, 254 missing bindings.

Verified registration is not a successful source check. 557 total obligations remain the primary denominator. Domain totals can overlap for suppliers in multiple domains.

### By family

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| citation integrity | 195 / 208 | 208 | 0 | 0 | blocked: 11, checked: 195, failed: 1, not_checked: 1 |
| filing documents | 16 / 27 | 16 | 0 | 11 | checked: 16, not_checked: 11 |
| independent reporting | 0 / 74 | 0 | 0 | 74 | not_checked: 74 |
| investor acquirer | 3 / 56 | 3 | 1 | 52 | checked: 3, not_checked: 53 |
| official announcements | 16 / 75 | 21 | 15 | 39 | blocked: 2, checked: 16, not_checked: 57 |
| regulatory filings | 32 / 43 | 32 | 0 | 11 | checked: 32, not_checked: 11 |
| release distribution | 0 / 74 | 0 | 7 | 67 | not_checked: 74 |

### By supplier

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| Abnormal Security | 2 / 6 | 2 | 1 | 3 | checked: 2, not_checked: 4 |
| Aqua Security | 4 / 7 | 4 | 1 | 2 | checked: 4, not_checked: 3 |
| Arctic Wolf Networks, Inc. | 3 / 6 | 3 | 0 | 3 | checked: 3, not_checked: 3 |
| Armis Security Ltd. | 2 / 6 | 2 | 0 | 4 | checked: 2, not_checked: 4 |
| Axonius, Inc. | 0 / 7 | 4 | 0 | 3 | blocked: 4, not_checked: 3 |
| Barracuda Networks | 1 / 5 | 1 | 1 | 3 | checked: 1, not_checked: 4 |
| BeyondTrust | 0 / 5 | 1 | 1 | 3 | blocked: 1, not_checked: 4 |
| BigID | 0 / 5 | 1 | 0 | 4 | blocked: 1, not_checked: 4 |
| Cato Networks | 3 / 7 | 3 | 1 | 3 | checked: 3, not_checked: 4 |
| Chainguard | 2 / 6 | 2 | 1 | 3 | checked: 2, not_checked: 4 |
| Check Point Email Security | 2 / 9 | 2 | 2 | 5 | checked: 2, not_checked: 7 |
| Check Point | 5 / 10 | 5 | 1 | 4 | checked: 5, not_checked: 5 |
| Claroty Ltd. | 1 / 5 | 1 | 0 | 4 | checked: 1, not_checked: 4 |
| Cloudflare | 10 / 13 | 10 | 0 | 3 | checked: 10, not_checked: 3 |
| Cohesity | 0 / 5 | 2 | 0 | 3 | blocked: 2, not_checked: 3 |
| Commvault Systems, Inc. | 11 / 14 | 11 | 0 | 3 | checked: 11, not_checked: 3 |
| CrowdStrike Holdings, Inc. | 9 / 12 | 9 | 0 | 3 | checked: 9, not_checked: 3 |
| CrowdStrike Falcon Exposure Management | 1 / 7 | 1 | 0 | 6 | checked: 1, not_checked: 6 |
| CyberArk | 2 / 6 | 2 | 0 | 4 | checked: 2, not_checked: 4 |
| Cyera | 5 / 9 | 5 | 1 | 3 | checked: 5, not_checked: 4 |
| Delinea | 3 / 8 | 5 | 1 | 2 | blocked: 2, checked: 3, not_checked: 3 |
| Dragos, Inc. | 3 / 6 | 3 | 0 | 3 | checked: 3, not_checked: 3 |
| eSentire, Inc. | 2 / 5 | 2 | 0 | 3 | checked: 2, not_checked: 3 |
| Exabeam, Inc. | 2 / 5 | 2 | 0 | 3 | checked: 2, not_checked: 3 |
| Expel, Inc. | 3 / 6 | 3 | 0 | 3 | checked: 3, not_checked: 3 |
| Forescout Technologies, Inc. | 1 / 5 | 1 | 1 | 3 | checked: 1, not_checked: 4 |
| Fortinet | 6 / 9 | 6 | 0 | 3 | checked: 6, not_checked: 3 |
| GitHub Advanced Security | 1 / 7 | 1 | 1 | 5 | checked: 1, not_checked: 6 |
| Google SecOps | 1 / 7 | 1 | 0 | 6 | checked: 1, not_checked: 6 |
| HiddenLayer, Inc. | 2 / 5 | 2 | 0 | 3 | checked: 2, not_checked: 3 |
| Ivanti, Inc. | 3 / 6 | 3 | 0 | 3 | checked: 3, not_checked: 3 |
| JFrog Ltd. | 6 / 9 | 7 | 0 | 2 | checked: 6, not_checked: 3 |
| Lakera AI (Lakera) | 1 / 5 | 1 | 0 | 4 | checked: 1, not_checked: 4 |
| Mimecast | 3 / 6 | 3 | 0 | 3 | checked: 3, not_checked: 3 |
| Microsoft Defender for Endpoint | 1 / 7 | 1 | 0 | 6 | checked: 1, not_checked: 6 |
| Microsoft Defender for Office 365 | 1 / 7 | 1 | 0 | 6 | checked: 1, not_checked: 6 |
| Microsoft Entra ID | 1 / 7 | 1 | 0 | 6 | checked: 1, not_checked: 6 |
| Netskope | 9 / 12 | 9 | 0 | 3 | checked: 9, not_checked: 3 |
| Nozomi Networks, Inc. | 2 / 6 | 2 | 1 | 3 | checked: 2, not_checked: 4 |
| Okta | 13 / 16 | 13 | 0 | 3 | checked: 13, not_checked: 3 |
| Optiv Security Inc. | 4 / 7 | 4 | 0 | 3 | checked: 4, not_checked: 3 |
| Orca Security | 2 / 6 | 2 | 1 | 3 | checked: 2, not_checked: 4 |
| Palo Alto Networks, Inc. | 14 / 17 | 14 | 0 | 3 | checked: 14, not_checked: 3 |
| Palo Alto Networks Cortex XSIAM | 1 / 7 | 1 | 0 | 6 | checked: 1, not_checked: 6 |
| Ping Identity | 4 / 7 | 4 | 1 | 2 | checked: 4, not_checked: 3 |
| Proofpoint | 3 / 6 | 3 | 0 | 3 | checked: 3, not_checked: 3 |
| Protect AI, Inc. | 1 / 5 | 1 | 0 | 4 | checked: 1, not_checked: 4 |
| Qualys, Inc. | 7 / 10 | 7 | 0 | 3 | checked: 7, not_checked: 3 |
| Rapid7, Inc. | 12 / 15 | 13 | 0 | 2 | checked: 12, not_checked: 3 |
| Red Canary, Inc. | 1 / 5 | 1 | 0 | 4 | checked: 1, not_checked: 4 |
| ReliaQuest, LLC | 3 / 6 | 3 | 0 | 3 | checked: 3, not_checked: 3 |
| Rubrik, Inc. | 9 / 12 | 9 | 1 | 2 | checked: 9, not_checked: 3 |
| SentinelOne, Inc. | 11 / 14 | 11 | 0 | 3 | checked: 11, not_checked: 3 |
| SailPoint | 8 / 11 | 8 | 0 | 3 | checked: 8, not_checked: 3 |
| Snyk, Inc. | 3 / 6 | 3 | 0 | 3 | checked: 3, not_checked: 3 |
| Sonatype Inc. | 3 / 6 | 3 | 0 | 3 | checked: 3, not_checked: 3 |
| Sophos Group (Sophos Ltd) | 2 / 7 | 4 | 0 | 3 | blocked: 2, checked: 2, not_checked: 3 |
| Splunk | 2 / 8 | 2 | 0 | 6 | checked: 2, not_checked: 6 |
| SurePath AI, Inc. | 1 / 5 | 1 | 0 | 4 | checked: 1, not_checked: 4 |
| Sysdig | 0 / 5 | 1 | 1 | 3 | failed: 1, not_checked: 4 |
| Tenable Holdings, Inc. | 9 / 12 | 9 | 0 | 3 | checked: 9, not_checked: 3 |
| Tines | 0 / 5 | 1 | 0 | 4 | blocked: 1, not_checked: 4 |
| Torq | 2 / 6 | 2 | 1 | 3 | checked: 2, not_checked: 4 |
| Trend Micro Incorporated | 1 / 6 | 1 | 1 | 4 | checked: 1, not_checked: 5 |
| Trustwave Holdings, Inc. | 1 / 5 | 1 | 1 | 3 | checked: 1, not_checked: 4 |
| Upwind | 3 / 6 | 3 | 0 | 3 | checked: 3, not_checked: 3 |
| Varonis Systems, Inc. | 9 / 12 | 9 | 0 | 3 | checked: 9, not_checked: 3 |
| Veeam Software | 4 / 7 | 4 | 0 | 3 | checked: 4, not_checked: 3 |
| Veracode, Inc. | 1 / 5 | 1 | 1 | 3 | checked: 1, not_checked: 4 |
| WitnessAI | 0 / 5 | 2 | 0 | 3 | not_checked: 5 |
| Wiz | 1 / 5 | 1 | 0 | 4 | checked: 1, not_checked: 4 |
| Xage Security, Inc. | 1 / 5 | 1 | 0 | 4 | checked: 1, not_checked: 4 |
| Zenity | 1 / 5 | 1 | 1 | 3 | checked: 1, not_checked: 4 |
| Zscaler | 11 / 14 | 11 | 0 | 3 | checked: 11, not_checked: 3 |

### By domain

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| ai security | 20 / 47 | 22 | 1 | 24 | checked: 20, not_checked: 27 |
| appsec | 16 / 39 | 17 | 3 | 19 | checked: 16, not_checked: 23 |
| cloud | 33 / 58 | 34 | 3 | 21 | checked: 33, failed: 1, not_checked: 24 |
| data | 38 / 64 | 41 | 2 | 21 | blocked: 3, checked: 38, not_checked: 23 |
| email | 17 / 49 | 17 | 5 | 27 | checked: 17, not_checked: 32 |
| endpoint xdr | 38 / 63 | 40 | 1 | 22 | blocked: 2, checked: 38, not_checked: 23 |
| exposure | 41 / 69 | 46 | 0 | 23 | blocked: 4, checked: 41, not_checked: 24 |
| identity | 31 / 60 | 34 | 3 | 23 | blocked: 3, checked: 31, not_checked: 26 |
| managed security | 17 / 40 | 17 | 1 | 22 | checked: 17, not_checked: 23 |
| network sase | 58 / 82 | 58 | 2 | 22 | checked: 58, not_checked: 24 |
| ot iot | 10 / 33 | 10 | 2 | 21 | checked: 10, not_checked: 23 |
| secops | 22 / 55 | 23 | 1 | 31 | blocked: 1, checked: 22, not_checked: 32 |

### By reason

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| HTTP 403 | 0 / 9 | 9 | 0 | 0 | blocked: 9 |
| HTTP 429 | 0 / 4 | 4 | 0 | 0 | blocked: 4 |
| HTTP 504 | 0 / 2 | 2 | 0 | 0 | not_checked: 2 |
| NO REGISTERED DISCOVERY SOURCE | 0 / 254 | 0 | 0 | 254 | not_checked: 254 |
| Q4 INDEX INCOMPLETE:Q4 LIST ROW SCHEMA INVALID | 0 / 2 | 2 | 0 | 0 | not_checked: 2 |
| SOURCE BINDING UNVERIFIED | 0 / 23 | 0 | 23 | 0 | not_checked: 23 |
| Unapproved source/redirect host | 0 / 1 | 1 | 0 | 0 | failed: 1 |
| successful | 262 / 262 | 262 | 0 | 0 | checked: 262 |

## Next actions by evidence gap

- Missing bindings: qualify an explicit source and adapter against archived primary evidence; preserve the obligation until registered.
- Candidate bindings: verify entity scope, date boundaries, pagination and positive/quiet/blocked cases before awarding coverage.
- Fetch or model caps: retain the charged limits and queue; retry only in an authorized later allowance and reuse valid prior checks.
- Blocked or failed pages: inspect the retained failure and repair the adapter or document a supported alternate primary source.
- Held claims: preserve the review queue and resolve source/date/status support before publication; do not infer an owner decision from a machine hold.
