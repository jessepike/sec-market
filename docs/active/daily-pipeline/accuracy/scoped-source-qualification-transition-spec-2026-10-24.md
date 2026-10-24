# Scoped source qualification transitions

Status: proposed integration specification, October 24, 2026. This document changes no contract, registration, diagnostic plan, policy guard, allowance, state or production artifact. It authorizes no request. The first implementation unit should cover only the three HTML bindings. SEC candidate addition and SEC activation are later, separate units.

## Current boundary and recommendation

The current contract has 303 sources, 74 suppliers and 557 required obligations. Its canonical hash is `79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60`; its mode is `daily_intake_with_separate_history`. Keep that mode, the full discovery requirement and all current allowances. Qualification remains a fetch-only diagnostic. Its success can support a later source declaration; it cannot supply daily intake credit or semantic review.

I recommend an explicit, closed transition record for each bounded contract change, an independently replayable qualification origin, and a typed inventory-only predecessor. Do not extend the historical D-112 bridge. That bridge proves only the exact `/version` and `/collection/mode` change between the original and current whole policies. It cannot absorb source qualification, added sources, changed aliases or any allowance change.

The implementation dependencies are concrete: retained qualification replay must survive replacement of the live diagnostic plan; normal collection must import qualification inventory without importing success or semantic authority; and the replacement plan must explicitly close the completed operation. These are integration repairs within the accepted coverage goal, not a request for a new coverage policy.

## Existing guards that must remain

`web/scripts/pipeline/separation.py` derives a semantic context from the complete target source, complete target supplier and remaining policy, excluding the global version, registry lists and collection mode. That permits unchanged source semantics to survive an unrelated registry change. It does not permit a changed source to borrow its old semantic review. Compare canonical context hashes as well as the existing bridge result so Boolean, integer or other JSON type changes cannot pass through ordinary Python equality.

`web/scripts/pipeline/retained_audit.py` independently resolves original contracts, tasks, receipts, observations and primary bytes. Its fixed positive legacy registry is pinned by `6fdf2884bbcc70962a0fc41622c5c862a61c31ed79bbf97b18cc193a843b4dce`. Keep that registry and its 188 original receipt origins unchanged. A new receipt cannot become legacy by omitting its version, compatibility marker or proof fields. New runs still need their actual current-policy compatibility record. Preserve latest-transport failure, equal-time ambiguity, conditional-chain, original-discovery, revalidation-cursor and index-signature checks.

Correction loading separately hashes the whole market contract into the outer policy stamp in `web/scripts/pipeline/corrections.py`. Therefore every contract transition requires a coordinated `web/src/data/tracker/factualCorrectionPolicy.json` refresh and correction projection replay. The six per-group review policies, original admissions, effective rows, source bodies and original dates must independently remain equal before reuse. An unchanged per-group policy is necessary; a newly generated outer stamp alone proves nothing. No model review or date renewal is needed solely because an unrelated source changes.

## First unit: exactly three HTML bindings

The only allowed source IDs and operational starts are:

| Source ID | Exact index |
|---|---|
| `ping-identity:official:1` | `https://press.pingidentity.com/news-releases` |
| `delinea:official:1` | `https://delinea.com/news` |
| `sonatype:official:1` | `https://www.sonatype.com/press-releases` |

Use the source-specific completeness modes and adapter descriptors validated by the schema-2 `bounded_candidate_traversal` operation. The operation remains capped at 60 index pages and one primary shape sample per source: 183 logical reservations at most, under the existing leased 5,500 daily fetch ceiling and runtime/day guards. Keep normal candidate collection closed.

Before preparing activation, require actual complete consecutive walks to independently proved terminals and the actual source-bound primary samples. Reconstruct pages, literal controls, inventory, date hints, sample identity/readability, charge intervals and run times from retained bytes. A self-reported `complete` or `registrationReady` flag is insufficient. Missing or conflicting pages, unproved terminal, blocked sample, exhausted allowance, deadline or UTC rollover hold activation. Unknown card dates remain unknown; they are not a reason to manufacture dates or drop URLs. Do not activate a subset implicitly if one source fails: this first transition has exactly three expected rows; a smaller batch would need its own exact reviewed patch.

### Exact patch and non-circular proof binding

Retain the original full contract and exact raw diagnostic plan before any declaration change. A qualification record binds that original policy, the exact candidate source and the proposed adapter. Define an activation base deterministically as that exact adapter with only `registration` changed to `verified`, before adding an origin pointer. Hash this base independently. The qualification-origin resolver must derive this transformation itself; it must not accept an arbitrary authored target binding hash.

Add only one closed `qualificationOrigin` field to each activated row, referencing the immutable diagnostic record, its source result and original full policy/plan references. The record keeps its original policy and candidate declaration. It does not contain the future enclosing contract hash. A separate transition descriptor can then name original and activated whole-contract hashes without a hash cycle. Keep this descriptor outside the contract it hashes, in an immutable authenticated transition record included in the activation candidate and later collection evidence. Do not manufacture a normal run/task/attempt origin for a diagnostic.

The transition validator must perform all of these checks before accepting retained evidence:

1. Authenticate the original whole contract by exact reference, byte length, raw digest and canonical digest. Authenticate the qualification record, raw plan, observations and bodies in the same manner. Verify their original source, supplier, policy, charged execution and time joins under that original policy.
2. Require a closed transition kind for these exact three IDs, exact before rows, exact derived activation bases, exact origin fields and exact array positions. The allowed differences are only the justified index URL, `kind=html_index`, exact source-specific `htmlCompleteness`, `registration=verified` and that origin pointer. A field already equal needs no artificial patch. All other source fields, supplier records, registry order, required flags, aliases, hosts, categories, mode, lookbacks and limits remain exact.
3. Apply the declared forward patch to the authenticated original and require canonical equality with the entire activated contract. Apply its exact inverse to the activated contract and require canonical equality with the entire original. Reject extra/missing fields, a fourth source change, reordered arrays and JSON type drift. Semantic-context equality alone is insufficient for this whole-policy guard.
4. Resolve every unchanged source's retained semantics directly against its original contract, not a rewritten intermediate copy. Require canonical semantic-context equality and retain original proof origins. The three changed candidates have no semantic authority from their qualification; do not bridge their changed source contexts as unchanged.

Do not copy the current hash into old receipts, permit “original or current” at individual guards, add a general mismatch exception, or create a transitive chain of permissive bridges. Each transition has one authenticated baseline, one exact patch and one resulting whole policy. Future unrelated edits require their own exact transition.

### Preserve inventory, holds and accepted proof

The authenticated private transition audit established 9,914 historical source/URL references, 24 reviewed bindings, four ordinary fact references and 32 review-queue entries. Preserve their exact original proof/body references, disposition and dates. Preserve the four remaining older-policy quarantines separately. A contract transition cannot resolve a hold or discard a fact merely because its global hash changed. Compare task obligations by source/supplier/family identity because derived task/run IDs can change with policy.

Add a typed qualification-inventory origin to predecessor replay. Independently resolve the diagnostic under its original contract and proposed adapter, then require its derived activation base to match the activated source after removing only `qualificationOrigin`. Union its literal URLs with all existing source inventory; preserve each original observation and date-hint provenance. URLs seen in earlier retained partial walks must also remain reachable through an authenticated inventory manifest, even if they disappeared before the successful walk. Keep references flat and deduplicated rather than nesting whole historical reports.

This origin supplies inventory only. It supplies no reviewed disposition, semantic fact, audit cursor, fresh checked time or intake success. New candidate URLs enter pending/unknown processing until the ordinary rules dispose of them. New normal discovery must freshly prove its own complete traversal. Retained inventory cannot turn a failed current index into intake success. Preserve unresolved changed signatures through index failure/rollover and preserve independently bound revalidation cursors after genuine same-input checks; activation must not recreate a cleared change or erase a still-open one.

### Close the diagnostic operation atomically

The live schema-2 traversal requires all three sources to remain `official_discovery` candidates. It will correctly reject their verified declarations. Activation must therefore replace the operational plan in the same candidate with a closed, current-policy **disabled operation**: explicit version/operation/current-policy fields, no sources, zero request allowance, no generic fallback. Implement this operation before activation. Absence, an empty schema-1 plan, stale hash or validation failure must fail closed rather than silently select another diagnostic.

Historical verification must load the original raw plan through its immutable reference, parse it under its original full contract, and run the original operation's proof checks. The current `_verify_bounded_candidate_result` compares its plan reference with `Path(plan['path']).read_bytes()`. That is appropriate for execution-time validation but cannot be the retained-origin resolver after the committed plan changes. Split or parameterize that pure historical replay boundary without weakening current execution's committed-plan check. Preserve existing schema-1 raw plans, exact row hashes, paid reservation joins and D-112-only historical descriptors unchanged.

The atomic first unit is: exact market patch, scoped transition descriptor, qualification-origin/inventory replay support, explicit disabled diagnostic plan, regenerated correction outer stamp and independently identical six-group projection. No normal source credit follows until a genuine new normal collector independently reconciles the same 557 obligations.

## Later unit: four neutral SEC candidates

Only after the first unit is independently accepted, consider the exact four-row proposal in `accuracy/four-neutral-regulatory-bindings-spec-2026-10-24.{md,json}`: `crwd-exposure` and `panw-xsiam`, each with `sec_index` and `sec_documents`. Add only those four candidate rows and their two exact supplier source-ID appends. That changes 303 source rows to 307 while preserving 74 suppliers and 557 obligations. Candidate addition gives no qualification or intake credit.

Use another closed exact inverse-patch transition against the then-current whole contract; do not reuse a hash calculated before HTML activation. Recheck the six correction policies and regenerate the outer stamp again. The supplier record is part of semantic context, so even a source-ID append can make an existing source on either affected subject incompatible. Enumerate those contexts explicitly; do not label them unchanged just because their source row is equal. The four preserved ordinary facts belong to Ivanti and Proofpoint and therefore do not acquire this subject change. Any affected existing review stays retained but cannot gain current semantic authority unless a separately scoped, exact enrollment-only equivalence is independently justified; this proposal grants no such exception. The current SEC diagnostic support is a branch of generic probing. Before real SEC qualification, select an explicit **targeted SEC operation** with exactly these two index/document pairs, current policy, issuer/subject/endpoints/window and bounded requests. It must bypass generic candidate and HTML fanout, validate all pairs before transport, and retain the existing lease/reservation/day/deadline/5,500-cap guards. A disabled HTML operation must not accidentally execute or suppress an unrelated generic SEC branch.

Fresh candidate index roots, their mandatory literal older pages and every eligible primary URL selected in the exact 365-day window must be observed under the correct paired candidate source IDs. Retain full inventory when a primary-body guard is exceeded; do not truncate it into completeness. Parent-source cached bytes and the archived 29 eligible primary bodies are useful fixtures, not fresh candidate observations. Verify exact issuer legal names/CIKs, primary relationship evidence, selected filing forms, readability, original request/final URLs and timestamps. Index and document completion remain separate; neutral results emit zero facts and no semantic document validation. Existing 16 company-certification sources remain unchanged.

Verified SEC activation is a third exact transition, after those real proofs exist. Change only the four registrations and typed qualification origins justified by that operation; retain inventory-only provenance and zero parent-fact authority. Replace the targeted candidate plan with an explicit current-policy closed operation. Do not route SEC activation through the HTML descriptor or the D-112 bridge.

## Required acceptance evidence

Before any activation candidate is promoted, retain a read-only replay report proving:

- Exact forward/inverse whole-policy checks; rejection of unrelated source/alias/host/limit edits, type drift, wrong origin/source and incomplete qualification. No circular hashes or mutable ready flags as authority.
- Original diagnostic replay still succeeds after the live plan is replaced; current execution rejects stale plans, disabled means zero requests, targeted operations have zero generic fanout, and original paid-plan/charge/body/date joins remain exact.
- All old 9,914 URL references, 24 reviewed bindings, four exact ordinary fact references, 32 queue entries and four unresolved quarantines remain accounted for. Added qualification URLs are retained as pending evidence. Repeated-day rollover, failed newer transports and partial traversal cannot erase inventory or renew review dates.
- The legacy registry remains byte-identical; dual stripping of marker/version still rejects unknown receipts. All six correction admissions/effective rows/dates remain exact under the regenerated outer stamp.
- A new normal collector preserves the 557 denominator and earns only actually fresh discovery credit, with unfinished history still reported separately. Diagnostic replay, a private candidate and a manual run supply no publication or scheduled-run proof.

No actual qualification completion, operational hash for a future activation, current allowance reservation, source credit or new owner decision is asserted by this proposal.
