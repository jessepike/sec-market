# Current content triage

Read-only offline inspection found 28 current held claims across 19 documents: 10 Aqua, six Mimecast, six eSentire, four Veeam and two Upwind. The 36 historical hold references across all runs are a separate inventory. Twenty-seven current holds concern dates; one concerns Veeam entity matching.

## Existing content repairs

- Aqua already has parsed article dates; null candidate dates need re-extraction and current-policy review after the allowance renews. November transition metadata says November 5 while visible text says November 6; preserve that conflict.
- Five individual Mimecast pages now expose dates through the existing repaired parser. Three dated historical claims become metadata-groundable; the APAC null-date claim needs re-extraction. The CEO index has multiple dated cards and cannot have one publication date. A board article cannot date its three retrospective acquisition references.
- eSentire uses WebPage JSON-LD datePublished, ignored by the current parser. Two leadership claims need source-specific article-identity-bound metadata support and re-review. Four other holds are acquisition titles in related-link sidebars on unrelated articles; exclude these cards and retain holds until original evidence is reviewed.
- Three Veeam acquisition references have no exact original event date. The Goldie appointment page uses brand Veeam rather than exact legal name Veeam Software. A reviewed explicit alias is deferred agent work because changing the contract invalidates current reviews. Its July 20 metadata/visible date conflicts with July 21 JSON-LD.
- Upwind funding claims came from a multi-entry listing. Card dates outside the candidate quote cannot become global publication metadata.

Parser repairs must not amend cached candidates, lift holds, bypass current-policy independent review or renew source timestamps.

## Current HTTP403 citation checks

| Supplier | Existing URL | Retained historical successful bodies |
|---|---|---|
| tines | https://www.bloomberg.com/news/articles/2025-02-11/goldman-softbank-back-ai-startup-tines-valued-at-1-13-billion | 0 |
| bigid | https://tracxn.com/d/companies/bigid/__pHSLjAzI2aqF63ud9QosF69usdaBPTT49_kou_rHtgw/funding-and-investors | 1 |
| delinea | https://www.globenewswire.com/news-release/2026/09/23/3367539/0/en/delinea-appoints-timothy-regan-as-chief-financial-officer.html | 3 |
| sophos | https://app.researchpool.com/index.php/provider/moodys-investors-service | 0 |
| delinea | https://www.globenewswire.com/news-release/2026/03/05/3250113/0/en/delinea-completes-strongdm-acquisition-to-secure-ai-agents-with-continuous-identity-authorization.html | 2 |

Two Delinea primary distributed releases are archived with dates September 23 and March 5. Historical bytes support content inspection but cannot make current blocked checks successful. Tines Bloomberg and Sophos ResearchPool have no successful archived copies. Unrelated Sophos acquisition releases do not establish a rating action.

## BigID discrepancy

Displayed TR-bigid-1 says $60 million in March 2024 at $1 billion. Archived Tracxn body `b783a64ed0a7516138685bfc8c97d6143b8ed85261c77db0cd32563fb4cba31e` lists Feb 08, 2024, $61.4M, Series D, $1B, Riverwood Capital, Advent International and SLW. Its page metadata says 2021-08-17. This is an unresolved primary-source check. No displayed fact was changed.

## Proposed narrow parser work

For eSentire news-release pages only, consider WebPage datePublished when that JSON-LD node url/@id matches the canonical fetched article identity, there is one main article identity and no conflicting date. Never accept dateCreated/dateModified as publication; retain future/ambiguity guards. Related Resources/Company cards must remain outside article extraction. Verify exact archived identity shape before implementing.

## Owner input

None currently required. Re-extraction, parser repair, factual review and explicit alias qualification are agent work within the normal allowance. No purchase, new credentials, expanded supplier roster or weaker publishing rule is proposed. The JSON companion preserves every document URL, body hash, metadata finding, hold reference and proposed action.

The inspected eSentire nodes have no @id. Their url and string mainEntityOfPage both exactly match rel=canonical. Exact BlogBody__Content holds the article; Left/Right classes are separate. The CEO fixture body fdf96872... has matching March 19 metadata/dateline. The autonomy fixture aaf25a4a... conflicts: May 26 metadata versus May 27 dateline. Preserve this conflict; recognizing metadata alone cannot choose an effective date. The JSON records exact fixture hashes, binding rules, cache constraints and adversarial cases.
