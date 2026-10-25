# Operational evaluation

Evaluated: 2026-10-25T07:52:32.605468Z
Revision: `6d5e87feba4ffbc75e50f35cb564cb8fd91708ca`
Run: `d1b5cbbf41ba2d8dfcb05a7ff2a2b00b7faada68dcaf3224ad4c7702b2d63b22`

Offline consistency evaluation of explicitly pinned supplied receipts. Does not authenticate GitHub or replay archived source bodies. No overall score.

| Measure | Status | Observed / required | Observed at | Evidence | Limitations |
|---|---|---|---|---|---|
| Daily source intake | fail | 264 / 557 | 2026-10-25T06:53:46.343333Z | coverage, contract | Fresh source intake only; processing and historical review are separate. No complete-event or all-site accuracy claim. |
| Observed document processing | fail | 38 / 10655 | 2026-10-25T06:53:46.343333Z | coverage, contract | Source/URL inventory; reviewed documents can contain held claims. Pinned counters are not source-body authentication or an accuracy estimate. |
| Retained historical review | fail | 39 / 10655 | 2026-10-25T06:53:46.343333Z | coverage, contract | Source/URL inventory; reviewed documents can contain held claims. Pinned counters are not source-body authentication or an accuracy estimate. |
| SEC source checks | pass | 48 / 48 | 2026-10-25T06:53:46.343333Z | coverage, contract | SEC source checks are distinct from the independent SEC claim gate. |
| Age of the collection check | pass | 0.98h / maximum 30h | 2026-10-25T06:53:46.343333Z | coverage, contract | Collection check age only. This evaluator does not replay archived observation bodies. |
| Fresh intake across the declared roster | fail | 264 / 557 | 2026-10-25T06:53:46.343333Z | coverage, contract | Fresh intake across the declared roster only; pending processing and history remain separately visible. |
| Known release checks | pass | 4 / 4 | Not supplied | gate | Pinned gate receipt reports known checks, including SEC recomputation. Tests do not estimate all-site precision/recall. |
| Records included in the fixed source audit | unmeasured | unmeasured | Not supplied |  | No pinned published-claim audit supplied. |
| Known contradicting records in the fixed audit | unmeasured | unmeasured | Not supplied |  | No pinned published-claim audit supplied; passing release tests do not establish absence of factual errors. |
| Claim accuracy on a reviewed benchmark | unmeasured | unmeasured | Not supplied |  | No fixed reviewed benchmark and scoring denominators supplied. |
| Eligible events found on a reviewed benchmark | unmeasured | unmeasured | Not supplied |  | No fixed reviewed benchmark and scoring denominators supplied. |
| Actual scheduled collection | unmeasured | unmeasured | 2026-10-25T06:53:46.343333Z | collection | A non-scheduled run supplies no timer observation or scheduled-attempt denominator. |
| Exact release publication | pass | 1 / 1 | Not supplied | publication, gate | Pinned historical acceptance; not a new live probe. |
| Rollback and restoration | pass | 1 / 1 | 2026-10-25T07:37:39.753529Z | rollback, publication | Legacy baseline full byte inventory may be unavailable; retain that limitation. |
| Preserved facts and pending work | pass | 4 / 4 | 2026-10-25T07:31:04.407756Z | continuity | Held claims and historical facts require explicit preservation checks; operational rollback cannot substitute for these. |
| review_queue | pass | 37 / 37 retained | 2026-10-25T07:31:04.407756Z | continuity | Durable retention or quarantine; not publication eligibility. |
| fact_provenance | pass | 4 / 4 retained | 2026-10-25T07:31:04.407756Z | continuity | Durable retention or quarantine; not publication eligibility. |
| current_or_quarantined_events | pass | 8 / 8 retained | 2026-10-25T07:31:04.407756Z | continuity | Durable retention or quarantine; not publication eligibility. |
| accepted_correction_groups | pass | 6 / 6 retained | 2026-10-25T07:31:04.407756Z | continuity | Durable retention or quarantine; not publication eligibility. |
| Sustained operation | unmeasured | unmeasured | Not supplied |  | No complete observation-window history supplied; one cycle cannot establish durability over time. |
| Observed reader value | unmeasured | unmeasured | Not supplied |  | Owner reports no observed real use yet. Technical reliability, accuracy and freshness are the current priority. |

## Pinned inputs

- contract: `inputs/contract.json` SHA-256 `24221c946781559c0ff3626e4e479c4647da915d0f2d7559ea88046982532c3c`
- coverage: `inputs/coverage.json` SHA-256 `f2486a623d93da011eaaf11926e09d6ce1533dab26d4a8f2fa2875a95a84d0b6`
- collection: `../../receipts/manual-freshness-recovery-40169973257-2026-10-25.json` SHA-256 `e0f7047d1d79508a51a18ac3bb0ce5a50adf8d761ee0709bebdfe931943ccf32`
- gate: `../../receipts/manual-freshness-publication-2026-10-25/gate-receipt.json` SHA-256 `f2b6718144b4aea15be01990fc7d6f7777e85e4c1e2f0128e492534225418b2c`
- publication: `../../receipts/manual-freshness-publication-2026-10-25/publication-receipt.json` SHA-256 `b4c1fd7aec6556d95aac69ff7df611bc8458f2bbfef487b4ccabec6538e0e696`
- rollback: `../../receipts/recovery-rollback-restoration-2026-10-25/drill-receipt.json` SHA-256 `9516b9ca8afd13db4f8604c0e208436113e3d65771b81a1472c4058df303f5d3`
- continuity: `inputs/continuity.json` SHA-256 `9d652656fedb6edcec1f8db44489f35b83e2edf20ebd60b95bbb92fee2ac2cba`

## Coverage inventory

264/557 successful required checks; 293 gaps. 278 verified registered bindings, 25 candidate bindings, 254 missing bindings.

Verified registration is not a successful source check. 557 total obligations remain the primary denominator. Domain totals can overlap for suppliers in multiple domains.

### By family

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| citation integrity | 196 / 208 | 208 | 0 | 0 | blocked: 11, checked: 196, failed: 1 |
| filing documents | 16 / 27 | 16 | 0 | 11 | checked: 16, not_checked: 11 |
| independent reporting | 0 / 74 | 0 | 0 | 74 | not_checked: 74 |
| investor acquirer | 3 / 56 | 3 | 1 | 52 | checked: 3, not_checked: 53 |
| official announcements | 17 / 75 | 19 | 17 | 39 | blocked: 2, checked: 17, not_checked: 56 |
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
| JFrog Ltd. | 6 / 9 | 6 | 1 | 2 | checked: 6, not_checked: 3 |
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
| Rapid7, Inc. | 12 / 15 | 12 | 1 | 2 | checked: 12, not_checked: 3 |
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
| WitnessAI | 2 / 5 | 2 | 0 | 3 | checked: 2, not_checked: 3 |
| Wiz | 1 / 5 | 1 | 0 | 4 | checked: 1, not_checked: 4 |
| Xage Security, Inc. | 1 / 5 | 1 | 0 | 4 | checked: 1, not_checked: 4 |
| Zenity | 1 / 5 | 1 | 1 | 3 | checked: 1, not_checked: 4 |
| Zscaler | 11 / 14 | 11 | 0 | 3 | checked: 11, not_checked: 3 |

### By domain

| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |
|---|---|---|---|---|---|
| ai security | 22 / 47 | 22 | 1 | 24 | checked: 22, not_checked: 25 |
| appsec | 16 / 39 | 16 | 4 | 19 | checked: 16, not_checked: 23 |
| cloud | 33 / 58 | 34 | 3 | 21 | checked: 33, failed: 1, not_checked: 24 |
| data | 38 / 64 | 41 | 2 | 21 | blocked: 3, checked: 38, not_checked: 23 |
| email | 17 / 49 | 17 | 5 | 27 | checked: 17, not_checked: 32 |
| endpoint xdr | 38 / 63 | 40 | 1 | 22 | blocked: 2, checked: 38, not_checked: 23 |
| exposure | 41 / 69 | 45 | 1 | 23 | blocked: 4, checked: 41, not_checked: 24 |
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
| NO REGISTERED DISCOVERY SOURCE | 0 / 254 | 0 | 0 | 254 | not_checked: 254 |
| SOURCE BINDING UNVERIFIED | 0 / 25 | 0 | 25 | 0 | not_checked: 25 |
| Unapproved source/redirect host | 0 / 1 | 1 | 0 | 0 | failed: 1 |
| successful | 264 / 264 | 264 | 0 | 0 | checked: 264 |

## Next actions by evidence gap

- Missing bindings: qualify an explicit source and adapter against archived primary evidence; preserve the obligation until registered.
- Candidate bindings: verify entity scope, date boundaries, pagination and positive/quiet/blocked cases before awarding coverage.
- Fetch or model caps: retain the charged limits and queue; retry only in an authorized later allowance and reuse valid prior checks.
- Blocked or failed pages: inspect the retained failure and repair the adapter or document a supported alternate primary source.
- Held claims: preserve the review queue and resolve source/date/status support before publication; do not infer an owner decision from a machine hold.
