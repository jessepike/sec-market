# Targeted qualification of four neutral regulatory bindings

Status: proposal only, October 24, 2026. This document changes no source declaration, contract, operation, allowance, runtime, state or publication. It authorizes no request. Root confirmed completion of the preceding promotion before this new file was written. The existing 557 obligations and six correction groups remain unchanged.

## Recommendation and present boundary

Implement one explicit `bounded_neutral_sec_qualification` diagnostic for exactly the two reviewed index/document pairs. Route it directly to the existing candidate-neutral SEC mechanics, with independent immutable result replay added before any later activation. This avoids the generic candidate endpoint fanout and keeps the operation separate from the explicit disabled HTML operation.

Use a hard ceiling of **280 logical fetch reservations**, charged only as requests are attempted. The archived planning case needs **31**: one CrowdStrike issuer root plus 12 primary bodies, and one Palo Alto issuer root plus 17 bodies. The fixed ceiling follows existing guards: two pairs × (at most 40 index pages, including each root, plus at most 100 primary bodies). It creates no new quota. Every reservation still debits the same leased 5,500-fetch daily ledger and must pass its UTC-day, monotonic deadline, persistence and final-completion checks. Calls, semantic documents, gate use and publication remain zero.

The four rows are still absent from the committed market registry. Merely adding them as candidates cannot produce normal collector requests or success: the normal collector retains its unverified-source gate. The current explicit HTML plan also cannot be used to reach the generic SEC branch: a bounded HTML plan returns through its own operation, while a disabled plan intentionally returns zero requests. Add and validate the new operation explicitly; do not make disabled mean “continue with another probe.”

## Exact subjects and declarations

Use the four candidate rows and two subject `sourceIds` appends in `four-neutral-regulatory-bindings-spec-2026-10-24.json`, with no declaration changes. Their canonical candidate-row hashes are:

| Candidate source | Canonical hash |
|---|---|
| `crwd-exposure:sec_index` | `edad9a69de0ae4827aa10193d1e2105691893a2167b483301706a04cd2167dfd` |
| `crwd-exposure:sec_documents` | `a2d3e1786c82ade238fab45d7ba91054c785fb0e5b7146c82dddf559cb7e22ce` |
| `panw-xsiam:sec_index` | `7dfafc4faa62d424de2aeebbe25943937998a395a3e6bdf7af3cda3ee117b91a` |
| `panw-xsiam:sec_documents` | `2dfa69151387f3e4bef0542d85ac37e6703f2116da7e7e20311d85b0ce5b11f9` |

The CrowdStrike pair binds segment `crwd-exposure`, parent CIK `0001535527`, exact submissions name `CrowdStrike Holdings, Inc.`, and root `https://data.sec.gov/submissions/CIK0001535527.json`. The Palo Alto pair binds segment `panw-xsiam`, parent CIK `0001327567`, exact submissions name `Palo Alto Networks Inc`, and root `https://data.sec.gov/submissions/CIK0001327567.json`. Both retain `relationship: parent`, the 365-day window, existing restricted hosts and path prefixes, required flags, and page limits. No issuer-name normalization, subject alias change or parent-company fact attribution is allowed.

The reviewed baseline is whole policy `79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60`, with 303 sources and 74 subjects. Adding the four candidates produces 307 sources while keeping 557 obligations and 74 subjects. Four missing-family gaps become four unqualified candidate gaps; successes increase by zero. The illustrative candidate hash in the older proposal is not a future activation hash. Derive the actual addition against the then-current authenticated full contract after the HTML unit has finished.

## Closed operational plan

Propose this new schema-2 operation, subject to implementation and independent review:

```text
schemaVersion: 2
operation: "bounded_neutral_sec_qualification"
marketSha256: exact final candidate whole-policy hash
maxRequests: 280
maxIndexPagesPerPair: 40
maxPrimaryBodiesPerPair: 100
lookbackDays: 365
pairs: exactly two ordered rows, CrowdStrike then Palo Alto
```

Each pair has exactly `supplierId`, `indexSourceId`, `indexSourceSha256`, `documentsSourceId`, `documentsSourceSha256`, exact `regulatoryIssuer`, and an immutable `relationshipProof` reference. The proof reference resolves to the reviewed original primary relationship evidence, source identity, observations, bodies and original policy/receipt context. It cannot contain an authored replacement issuer or release scope. Hashes bind the actual candidate declarations, not copied verified declarations.

Preflight the entire plan, both pairs and all relationship references before the first reservation. Require the exact four IDs, source ordering, one-to-one subject pairing, exact source hashes, candidate registrations, subject kind `segment`, matching issuer/CIK, root endpoints, window, hosts and bounds. Reject extras, omissions, duplicate pairs, Boolean/integer drift, alternate issuer or source IDs and substantive contract differences before transport. Do not select all candidate SEC sources from the registry or accept an empty pair set.

Operation dispatch must be exclusive. A targeted SEC plan performs only this operation; a bounded HTML plan performs only HTML traversal; a disabled plan performs zero requests. Missing, stale, unknown or malformed explicit plans fail closed. No validation failure may fall through to generic roots, robots, sitemaps, HTML samples, another operation or another registry scan. The targeted operation therefore has zero generic fanout, avoiding the roughly 117–118 extra reservations observed in earlier generic-plus-seven batches.

## Collection and request accounting

Reuse `_validate_sec_diagnostic_pair`, `_sec_diagnostic_pages`, `_validate_sec_candidate_index`, `filing_document_inventory` and `_probe_sec_candidate_pair` in `web/scripts/pipeline/onboarding.py`, together with the existing neutral `regulatory.py` validators. Add only the targeted plan/dispatch/bound/report/replay layer needed around those mechanics. Existing helper output alone is not an activation verdict.

For each pair, fetch the exact current root under its `:sec_index` source ID. Fresh HTTP 200, requested URL equal to final URL, a retained body, exact issuer name/CIK and an observation within the leased run/day are mandatory. Follow every literal older submissions page whose declared ending date intersects the derived UTC 365-day window. Independently check exact page set, counts, enclosing date ranges, table columns, accession conflicts and all source/host/path joins. Never infer an absent page from an archived response or silently truncate a cap-exhausted traversal.

Use that same freshly verified, explicitly paired index observation set to derive the document-source selection. This is one root traversal per issuer, not a second physical root request for `:sec_documents`; the document result must explicitly bind the index source, complete index references and selection hash. Fetch every distinct selected primary under its own `:sec_documents` source ID. Preserve the exact existing form set, accession, filing date, primary path and ordering. Require actual HTTP 200 with exact request/final URLs and independently reproducible readable text for every selected body. No parent-source cache, pre-existing citation observation or bodyless 304 can replace this first candidate observation. Do not insert archived parent bytes into candidate caches.

If selection exceeds the existing 100-body guard, retain the entire selected URL/date inventory and mark document qualification incomplete; do not select only the first 100. Index and document outcomes remain separately visible. A failed body, blocked/redirected root, missing older page, page/body cap, deadline, day change or cancellation preserves its partial evidence and prevents the affected proof from completing. Require both pairs complete for this proposed four-row activation batch. A smaller activation would require a different exact transition proposal.

| Pair | Archived root/older pages | Archived primary bodies | Planning reservations | Maximum reservations |
|---|---:|---:|---:|---:|
| CrowdStrike | 1 / 0 | 12 | 13 | 40 + 100 = 140 |
| Palo Alto | 1 / 0 | 17 | 18 | 40 + 100 = 140 |
| Total | 2 / 0 | 29 | 31 | 280 |

The archived planning window is October 23, 2025 through October 23, 2026, at original audit time `2026-10-23T11:34:15.010723Z`. Fresh responses and the actual future UTC day determine the new required page/body sets. There is no fixed promise that 31 will still suffice. Reserve as used, never precharge 280, stop before an operation's 281st reservation, and stop earlier on the shared daily limit or existing runtime guard. The existing transport may make bounded retries or redirects within one fetch call; the ledger and the numbers above count logical reserved fetch calls, not individual HTTP exchanges. This proposal adds no retry loop and makes no claim that those two counts are equal.

“Documents” in the shared semantic budget means model-processed documents. Downloading and checking these neutral filing bodies must leave that counter unchanged, alongside model calls and gate/publication counters. No new allowance or purchase is needed.

## Independent readiness and immutable replay

Distinguish run completion from qualification evidence. The existing paired helper can record a structural/body failure while `executionCompleted` is true because no reservation was denied. It also initializes `secIndexDiagnostic.qualificationComplete` false. Neither lifecycle flag, reason label nor a newly authored ready flag can establish qualification.

Add a pure targeted-result verifier that reconstructs both root/older-page inventories, exact selections, every primary body and readable-text reference, source/subject/issuer joins, original observations and times, and charged reservation interval. Require exact equality with the recorded partitions and counters, zero semantic/fact/coverage outputs, and final lease/day/deadline guards. A partial report must remain replayable as partial inventory evidence after a failure; it cannot become a complete proof. No new primary fact or held semantic claim is created.

Store the original full candidate contract, exact raw plan and canonical hash, exact run record, every observation/body/text reference, and complete selection manifests immutably. Historical replay must load the record's exact immutable raw plan under that original contract after the operational plan is replaced. Live execution must continue checking equality with the committed current plan. Retain original dates, statuses, charge numbers and failure snapshots. Do not rewrite an old global hash, borrow another source's cache, widen the D112 bridge or import authority through the HTML origin type.

Internal replay authenticates content joins, not external Actions provenance. Before later registration, require a source-controlled positive SEC authority entry binding the externally authenticated run identity, app revision, run/plan/contract bytes, artifact hash, archive commit/manifest and external verification receipt. Keep that registry empty until actual complete evidence exists and has been reviewed. A self-consistent rehashed diagnostic in a mutable archive cannot authorize registration. Retained diagnostic URLs may later enter a separately typed inventory predecessor; they supply no semantic review, audit cursor, refreshed date or daily-intake success.

## Original primary relationship evidence

Keep the original proposal JSON bytes pinned by raw SHA-256 `9928884e5b0b9ec99811f09033fe1477ecde2353c012a634dd83317a63769526`, with its internal proposal seal `3d8590537e2693025577c887408625f4319a37e11acc108ae833a7baaaf2ec8e`. The authenticated 9c archive manifest remains `cd9d84c67a70f11b72eeba25a012e3402a88b2d5a9c692f145c225b0a2c3418a`.

CrowdStrike relationship proof is the 10-K at `https://www.sec.gov/Archives/edgar/data/1535527/000153552726000010/crwd-20260131.htm`, whose Falcon portfolio names Exposure Management. Original observation `c8c6e9b6eb60cbced06fc5a88902e3c1bb0551c3b7360f34956e5ef1d029c10e` has status `retained_immutable`, original fetched time `2026-10-20T21:22:20.717300Z`, and body `c03d8b275ed8c532e01c8bbd412577b03a2e79038a6b4e3d867a74e8c1f88f67` (2,749,303 bytes). Its old index anchors and reuse chain remain part of the original proof.

Palo Alto relationship proof is the 10-K at `https://www.sec.gov/Archives/edgar/data/1327567/000132756726000023/panw-20260731.htm`, whose Cortex portfolio names Cortex XSIAM. Original observation `c6eceaa677080caadc165a800859935b07fe186b039e7bb12deabfb520f19e3d` is a conditional HTTP 304 at `2026-10-23T04:14:59.011680Z`, reusing `ef71d3265b0b4ac50079fa5141aa8d12ea03d510bb5a0a25a579e765a68ee6e1`; body is `8605bc5f502c555918d601b6564c60d0d44e4c4d0705726af60fc424ed8130f5` (3,083,409 bytes). Preserve that conditional history, rather than describing it as a fresh candidate fetch.

Both filings' exact inline-XBRL CIK/registrant markup and portfolio excerpts remain pinned in the original proposal. Their submissions-name punctuation/case differs from filing markup; match current submissions names exactly and join the original filing identity by exact CIK. These proofs establish the reviewed parent relationship only. They grant no product financial figure, parent financial attribution, product event, current qualification or current intake credit.

A read-only VM check for this proposal verified all 35 selected archive entries against their original byte/hash/size/mtime pins; both exact excerpts and XBRL identity markup still match. Pure candidate-index replay at the original audit time independently reproduced 1,001/1,000 unique filings and 12/17 selected primaries. A write/network/subprocess-denying audit hook protected that check. This was selected historical evidence replay, not another whole-archive verification or a current source response. No existing archive content or source-proof artifact was written.

## Required closed transitions and preservation

First finish the reviewed HTML unit. Then prepare one exact candidate-addition transition against the authenticated then-current policy: append only these four rows and the two exact subject source-ID pairs. Prove full forward/inverse canonical equality, exact array positions/types and no unrelated aliases, hosts, source, supplier, schedule, model or review-rule changes. The live targeted plan must bind the resulting whole policy atomically; do not merely repin an old plan root or old proof. Preserve historical HTML policies/plans/results under their original hashes and their own immutable replay API.

Regenerate the correction outer stamp because the market contract changes the global correction policy hash. Independently prove all six per-group review hashes, admissions, effective rows, source-body references and original dates remain exact. Preserve all 9,914 existing source/URL pairs, 24 retained reviewed bindings, four ordinary facts, 32 review-queue entries and four older-policy quarantines. Source-ID appends change the two affected supplier semantic contexts; retain their old evidence explicitly and do not automatically call those contexts equivalent. Unchanged subjects must retain their original compatible proof, including Ivanti and Proofpoint facts. The 188-origin legacy registry and old reports stay immutable.

After an actual targeted run proves both pairs complete and external provenance is authenticated, propose a separate exact SEC activation transition. It may change only the four registrations and the SEC-specific typed qualification origins justified by that operation. Independently derive activation bases from the original candidate rows; require all four expected changes and exact whole-policy forward/inverse equality. Do not reuse the HTML transition or invent normal collector run/task/attempt proofs. Preserve all previously observed SEC URL inventory, including partial runs, without inventing semantic dispositions. Replace the targeted plan atomically with the explicit disabled current-policy operation, refresh the outer correction stamp and independently replay the same six groups again.

A new normal collector must then obtain and reconcile its own fresh current-policy evidence for the same 557 obligations. Diagnostic completion supplies zero successful tasks and says nothing about all claims having been reviewed. Keep D112 intake, neutral structural/body checks and unfinished semantic/historical review distinct. The existing 16-company certification, 80 SEC claims and six factual-correction admissions remain unchanged.

## Review and tests before any dispatch

The implementer should prove exact two-pair preflight before transport; zero generic/HTML requests; disabled zero requests; immutable replay after plan replacement; and rejection of stale/unknown plans. Use fictional missing/extra pages, wrong issuer/name/source/CIK, conflicting accessions, unsafe primary paths, failed/redirected/304 bodies, unreadable/block pages, altered readable text and charge/time/run envelopes. Reject record/plan/body rehash counterexamples unless the exact external authority is listed. Exercise the 100-body and 280-reservation guards, insufficient shared budget, cancellation, last-request deadline and UTC rollover, preserving complete pending inventories and all zero counters.

All declaration, parser, dispatcher, replay, transition, correction and synthetic-budget work can be implemented and reviewed offline first. Only the eventual explicit leased diagnostic may obtain the two fresh roots, newly required literal older pages and all current eligible primary bodies. This proposal performs and authorizes none of those requests, creates no operational plan and claims no qualification or publication.

## Standalone implementation addendum

Root authorized a dormant standalone implementation in `web/scripts/pipeline/neutral_sec_qualification.py`, its focused test module and this document. Onboarding dispatch, committed plans, contracts, registrations and correction files remain outside this unit. Root will integrate the returned operation explicitly after review; importing this module performs no work.

The concrete plan adds an exact `originalContract` reference to the schema above. It names the complete original candidate contract at `contracts/<marketSha256>.json`, with exact raw/canonical hash and byte length. This is the diagnostic's original full policy, retained before transport; it is not a rewritten policy attached to earlier parent observations. Each `relationshipProof` has exactly `proposal` (the immutable object containing the exact reviewed proposal JSON bytes) and `proofId`. The module pins that already reviewed proposal's raw hash and archived authority, derives all four candidate declarations from it, and independently loads its exact original relationship observations/bodies and the reviewed baseline contract. Older retained/conditional statuses and dates remain explicit. These relationship proofs confer no current transport or registration credit.

Expose `validate_plan(contract, store, raw_plan_bytes, path=None)`, `execute(contract, store, fetcher, budget, normalized_plan)`, `verify_report(original_contract, store, raw_plan_bytes, report)` and `replay_diagnostic(original_contract, store, run_record_reference, raw_plan_reference)`. Live execution requires the exact current path bytes, a genuinely bound `PersistentProbeBudget`, and revalidation immediately before transport. Historical replay loads only the exact immutable recorded plan. Both paths enforce closed plan/pair fields and whole-policy equality.

Execution calls the existing paired candidate SEC helper through an operation-limited view of the existing budget. Independent report replay reconstructs index pages and selected bodies from immutable references, validates exact partitions, text, source/time/charge joins and final guards, and derives readiness separately from lifecycle completion. It never invokes a fetcher, writes evidence, calls a model or grants qualification. Partial evidence must remain replayable without becoming ready. The execution result keeps all four source rows and zero model, semantic-document, gate, semantic-admission, qualification and coverage counters. A standalone test fixture may construct candidate declarations in a temporary store; it changes no committed registry.

The normalized plan contains `operation`, `rawSha256`, `canonicalSha256`, `path`, `plan` and `pairs[{index, documents}]`. The execution report retains the four existing paired-helper source rows, then adds independently derived `pairReadiness`. Each readiness row separates `indexComplete`, `documentsComplete` and `evidenceComplete`, retains `selectedCount`, `observedPrimaryCount` and `pendingPrimaryUrls`, and gives a descriptive reason. Verification returns `pairs`, combined `evidenceComplete`, `qualified:false` and `coverageCredit:false`. Historical replay returns `plan`, `report` and `readiness`; no field authorizes activation.

Root integration must explicitly route only this operation to the standalone implementation before generic probing, preserving the disabled operation's zero-request return. It must also retain the exact original candidate contract and reviewed relationship-proposal object before preflight: the existing leased source-probe entry point does not automatically write a newly added candidate contract into state. Validation deliberately provides no missing-proof fallback and writes no state. The proposal object is exactly 60,966 bytes with the fixed raw hash above. Root owns the later acknowledged evidence preparation, current plan, exact candidate-addition transition and any actual request authorization. This standalone unit changes none of them.

### Offline implementation evidence

The final focused VM run passed 137 tests: the 21 new targeted-operation cases plus existing onboarding-budget, leased-source-probe, neutral filing-document, regulatory-index and regulatory-collection suites. The new tests include a complete fictional 280-reservation walk, denial before reservation 281 without an additional charge, a fully exhausted 5,500 ledger with zero requests, final in-flight deadline and UTC rollover, exact old-plan replay after live-plan replacement, body/selection/text/charge/run-envelope tampering and copied verified-declaration rejection. A structurally failed body run remains lifecycle-complete while its independently reconstructed evidence is incomplete.

Independent review found a final timestamp race: time could expire during the report's `checkedAt` capture after its first guard. The capture now sits between pre/post budget guards. A post-capture denial is recorded before deriving readiness; its original captured timestamp, all four charges and raw proof remain intact as replayable partial evidence. If the pre-guard already denies, capture the diagnostic timestamp without repeating that failed guard or inventing another charged event. Both second-clock-call monotonic expiry and second-clock-call UTC rollover regressions pass. No next-day reservation is created.

The actual local 9c archive preflight used the fixed production relationship authority, without the fictional authority substitutions used by synthetic fixtures. Both parent proofs and the original 12/17 filing selection passed. All 35 selected archive entries retained exact content hashes, sizes and modification times before and after this read-only test. That test supplies no current qualification, normal collector receipt or live request. It skips without network fallback when the authenticated local archive is unavailable.

Implementation SHA-256 is `f9eb6f9c193d8a21a13573269606af6590e999853bb1175aae660e394166beab`; focused test SHA-256 is `3802f9d0c9038ec1af31aba64a3e2a62df8180dfa3c8aa2f13476bb2e4c1755d`. The active dispatcher, current operational plan, market registry, correction files and activation authorities were not edited by this unit.
