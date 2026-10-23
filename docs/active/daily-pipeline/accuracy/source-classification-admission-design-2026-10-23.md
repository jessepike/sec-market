# Xage publication-role correction: admission design

Revised 2026-10-23T21:33:29.832155Z. This is a candidate design under SEC-072. Root's design-review recommendation is to reuse the existing dated correction machinery. This is not claimed owner approval. No request, implementation, review or production record changed.

## Recommended operation in the existing ledger

Add a narrowly typed `reclassify_publisher_disclosure` target operation with group review scope `publisher_disclosure_only` to the current dated correction ledger, projector and independent gate. The only permitted target is `evidence:TR-xage-1`, changing `INDEPENDENT` → `OFFICIAL` and the limitations text below. Preserve Yahoo Finance as publisher and keep the URL, excerpt, numbers, dates, retrieval information, identity and all other fields identical.

Use `contracts/factual-corrections.json`, `web/scripts/pipeline/corrections.py`, the existing `factualCorrections.json` projection and seal, and the existing release/history path. This avoids a second request inventory, generated enabled file or publication route. The existing five group objects and their exact per-group review-policy derivations remain unchanged. No sixth request is appended in this task. A later reviewed implementation may append this one disjoint scoped group; that updates the existing global inventory policy and complete manifest in the normal way while retaining the first five review hashes and accepted rows.

The publisher's own disclosure is primary evidence of its publication role. The ordinary factual-correction primary-source guard continues reading immutable original source class and its own proof; the general protected-fields guard remains unchanged. An `OFFICIAL` display or publication-role admission must never authorize financial extraction, certification, a factual-source admission or recurring-source qualification.

## Retained proof and document size

The exact configured URL is `https://finance.yahoo.com/news/xage-security-hits-record-growth-120000615.html`. Observation `3659081ca33f1558ed74ea30327c580c2d1664dcf7429e440758089b872499b6` was fetched at `2026-10-23T04:14:56.139543Z`. Its 1,021,859-byte body has SHA-256 `01cf60192caf9038e618e16a67aed61087e163a4aff82a724ca406f56c1e2afc`. The observation and body match the frozen archive manifest.

The complete normalized `Page.text` is **16,832 characters**, SHA-256 `c98a0f42e0107dce354b5885d4788498689b8ba5a6e39a8beffb82824ffb7749`. Article-readable text is 10,289 characters and main-region text is 13,323. Send the whole visible-page parsing view without truncation under the existing **30,000-character** cap. Raw HTML is 1,021,815 characters and is not the bounded readable-document input. Each document and the combined group must fit before reserving a document or model call.

The unique article wrapper contains the exact publisher notice, dateline and byline context:

> This is a paid press release. Contact the press release distributor directly with any inquiries.

> PALO ALTO, Calif., March 18, 2026 (GLOBE NEWSWIRE) -- Xage Security

> Xage Security March 18, 2026 7 min read

Canonical-bound structured metadata names Yahoo Finance as publisher, Xage Security as author/creator and GlobeNewswire as provider. These are the publisher's own attribution statements. The [detailed design JSON](source-classification-admission-design-2026-10-23.json) retains exact quote positions, text/body hashes, the complete original observation and source binding, and relevant metadata.

The page links to GlobeNewswire's homepage and an opaque GlobeNewswire tracker labelled Xage Security. No original wire-story permalink or direct issuer URL is present. The unobserved tracker destination remains unknown. The page nevertheless supports review of the publisher's own explicit paid-release classification. Use this proposed limitations text:

> Yahoo Finance labels this page as a paid press release and attributes it to Xage Security with a GlobeNewswire dateline. It is issuer-attributed release material republished by Yahoo Finance, not independent editorial reporting. This publication-role correction does not independently verify the financial, funding or operating figures in the unchanged excerpt.

The complete original record hashes to `62bb8bcce0698b5f164867d9bc070be77ee4eebde095947dd96eb8a693d0d6fb`. The complete proposed record hashes to `86b06657bb1139a5d98d293b5599590539baec7e099b59294a3a3e7e0001fe76`. Only `sourceClass` and `limitations` differ. Keep the old record, including its previous limitations, in immutable history.

## Strict scope and independent admission

Within the existing loader and projector, dispatch the new target operation only when the committed group has `reviewScope: publisher_disclosure_only`. Accept one exact Xage target, original hash and class transition. Compare complete record shapes and every protected field by canonical equality. Ordinary `replace` still rejects class or publisher changes. Unknown scopes, mixed factual/role targets and any other ID/transition/field fail closed. The current ledger's duplicate-target guard prevents collision with factual groups or another correction.

Bind the candidate to its complete before/after, operation, scope, reason and dated note template. Bind its evidence set to the verified configured supplier citation, actual requested/final canonical URL, successful observation ID, raw body reference/length, original fetch time, complete normalized text hash and disclosure quotes. Require the notice, Xage byline and GlobeNewswire dateline in the same unique article. A sidebar disclosure, logo or bare hostname alone is insufficient. Preserve the unchanged financial paraphrase without treating it as a newly verified literal quote.

Reuse the existing subscription client and reservation flow. Add a strict role-review schema with the explicit scope echo and all three hashes. Require seven role-specific checks to pass: target identity, publisher source binding, release attribution, literal disclosure, class transition, limitations scope, and unchanged claims/history. The reviewer sees all 16,832 characters, the complete target and the note. It must reject uncertainty and must not certify the finances. The ordinary seven factual checks and their review protocol remain unchanged for existing groups.

The new group-review policy uses a distinct rules version and includes the explicit scope, exact candidate, baseline, supplier identity, relevant configured source, model text cap/provider, 30-hour freshness rule, exact transition allowlist and sorted role-check names. Its precise candidate basis/digest is in the JSON. Existing groups without a role scope continue using their exact current formula; no new default field is injected into their hash inputs. This prevents cross-scope review reuse without duplicating the ledger.

Reuse `correction-attempts`, `correction-admissions` and the existing policy/candidate/evidence cache key. The scoped policy hash and candidate identity distinguish this review. New role reviews, admissions and public rows echo `publisher_disclosure_only`; retain the legacy exact admission schemas and rows. The gate derives the expected scope from committed requests, then authenticates the real immutable review/admission and accepted index. Caller acceptance flags and author-written or synthetic results are insufficient.

Reserve one document per group and charge one call per actual request through existing persistent limits. Failed, invalid, interrupted or late reviews keep their charges. After the review returns, recheck cancellation/deadline and source age at actual completion time. This observation permits initial review completion only through **2026-10-24T10:14:56.139543Z**. A future real admission may replay its original age later; this design is no admission and cannot reserve or backdate that eligibility.

## Existing build, runtime, history and publication path

Extend the current Python independent gate, Node build verifier and pure TypeScript projector with matching strict operation/scope dispatch. Node independently derives the complete shared inventory and each applicable group-policy formula. The existing explicit global policy and expected review map must reject missing, extra, stale or forged entries. The browser's scoped target case enforces the exact ID, before record, class transition and protected fields; ordinary evidence replacement retains its existing rules.

The one enabled `factualCorrections.json` bundle must contain every requested group, including all five factual groups and the later scoped group. Its existing seal and release/static manifest bind the entire inventory, file bytes, review scope, new IDs and publication date. There is no partial group bundle, parallel seal, disabled-role exception or earlier-publication bypass. Ordinary group rows and their original dates/reviews remain byte-identical when a disjoint group is added.

Extend the existing independent expected-current-views reconstruction and actual-export assertions. Original histories stay raw. Current `evidenceRecords`/`evidenceById`, drawers, library, current exports and corrections page/JSON/feed use the same admitted view. Supplier/event views, financial excerpt and certified figures remain identical; a local export edit after projection must fail. Display the narrow scope and exact before/after with publisher attribution without claiming financial certification or owner approval.

Use the current UTC first-publication boundary and rollback/restoration checks. Keep `admittedAt` separate from actual public date, reject late first publication and retain all prior rows, dates, review metadata and original history. Render the affected drawer/library/history at desktop and phone through the existing preview/release workflow. Only the intended metadata and dated history may change.

## Next proof and remaining work

The retained publisher body is sufficient for the recommended publication-role scope. It does not establish an independently fetched original wire/issuer page or the truth of financial figures. If the observation expires before review, fetch the same exact configured Yahoo URL through the normal renewed allowance, archive the real response and rebind its actual time/body/text. Never renew the old observation.

If a new page lacks clear disclosures, hold the operation. Follow only the literal retained tracker as a bounded provenance probe with safe redirect/host checks, or find an original permalink on an actually fetched page. No direct wire or issuer story URL is proven yet. Any finance repair needs its own ordinary primary proof and factual review.

I recommend implementing this typed branch inside the existing correction machinery because it keeps one publication path while preserving scope-specific proof and independent review. No owner factual choice is currently required. Agents still need the reviewed implementation and adversarial backend/build/runtime tests, a later explicit scoped request addition, real quota-respecting review and full independent gate/publication receipts. The fixed 177-record audit, its five contradictions, existing five groups/11 targets, 97/74/273 original inventories and actual 121/557 source result remain unchanged by this design revision.
