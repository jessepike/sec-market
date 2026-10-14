# Complete-refresh publication gate — 14 October 2026

## Production status

The owner withdrew the pending promotion at 22:47 UTC before any main checkout, merge, push or deployment. Vercel independently confirms production **Ready**, deployment `dpl_9mjdUV7fWSSgBrmSPuUbv4ekRUeg`, exact GitHub main SHA `28c7ffdd2508ab1805397fbe76448c02ad40a525`, at https://securitymarketpulse.com. The rollback/reference baseline is the same deployment, https://security-market-pulse-bp6p56xy3-pikeholdings.vercel.app. No rollback is needed or performed.

The existing deployed preview is the held incomplete review candidate `c052190897e81945171aee962e435d8dd8c0d29d`, https://security-market-pulse-git-preview-pikeholdings.vercel.app. It predates the new rule. The new guard work has no publishable deployment: the release build correctly exits 2 before emitting an artifact. Do not promote either the old candidate or this new guarded branch while the contract is unmet.

No historical refresh is verified at 100%. The complete-refresh ledger is **not established**, rather than borrowing a collector or application deployment date. Production still displays its older site's legacy date until a compliant app/data release can be made. That is an outstanding limitation, not a claim that production now has the new date UI.

## Implemented controls

- `web/scripts/refresh-publication-gate.mjs`: fixed supplier/group inventory, required components and pinned existing qualifiers, exact candidate-value hashes, substantive primary evidence/locator plus current discovery, per-category verification age. No successful HTTP response alone, completion label, dropped field, failed retry, unreviewed absence or changed denominator can pass.
- `web/src/data/tracker/refreshContract.json`: a conservative v1 gate over 74 suppliers × seven logical claim bundles = **518 required bundles**, including all components. Identity monthly; reported metric and latest/prior financial pair/current company-event discovery daily; ownership/latest round weekly. These windows are an engineering proposal from the parent's metric work. No exclusion or undisclosed-answer policy is silently enabled. This is the release guard inventory, **not a published final refresh-score denominator**. More granular scoring remains separate.
- `web/src/data/tracker/publishedSnapshot.json`: immutable legacy-production baseline hashes and revision. Some tracker inputs did not yet exist on production; their addition is a candidate change. A legacy baseline is not certified complete merely because it was previously published.
- `refreshVerification.json` starts empty; the existing untyped receipt is not upgraded into fabricated proof. Collector edit guard refuses collector-written certificates or public timestamps. The missing independent proof-generation adapter is a real blocker.
- Normal `npm run build` begins with the complete-refresh publication gate. The coverage generator itself cannot label an attempt complete based on raw status counts.
- `prepare-refresh-publication.mjs` advances the public complete-refresh timestamp only after 100% required certification; a matching public date is required before a changed snapshot can build.
- Nightly runner requires a clean isolated checkout, snapshots active data, preserves held partial candidate/receipts and restores active data/date on failure, releases its lock and never stages failed data.
- Autonomous publisher no longer pushes failed-gate status-only commits to either preview or production.
- Installed `.git/hooks/pre-push` now requires owner promotion, exact clean checked-out SHA and the publication guard; `PROMOTE=1` cannot override completeness. The hook installer correctly handles Git worktrees.
- Site's local header, rail, masthead, snapshot and coverage now distinguish **last complete refresh**, **latest attempt**, **reporting period** and **app deployment**. App deployment is explicitly unrecorded until separately observed. No score is added to the UI.
- Future built endpoints include `/refresh-publication.json` and `/refresh-certification.json`; health monitor requires certificate verification, not a `complete` label. They are not live because this candidate cannot build.

## Notifications / attempt receipt

`.collect/refresh-attempt.json` is the per-run delivery envelope: stable notification ID, attempt date, complete-refresh date, changed file hashes, 107 candidate property changes with supplier/field/value/period/reason/source URLs, contract coverage and blockers. `deliveryState` is `pending-parent-delivery`. A prepared complete candidate is not a deployment: send a data-updated notification only after the exact deployed candidate is Ready and its public receipt matches. Blocker notifications are distinct from data-updated notifications. No new notification automation or duplicate collector has been created here.

## Existing receipt and score recommendations

The Oct 14 raw receipt has **1,086 rows**, not a consistent logical-claim denominator: 107 updated, 444 checked-no-change, 14 unavailable, 248 failed, zero not-checked, 199 not-applicable, 74 configured. Excluding configured and NA yields 813 rows; 551/813 = **67.8% raw successful-status row share**. Excluding unavailable also gives 551/799 = 69.0%, but neither is a valid final score. Optional properties, collapsed null groups and one events array containing many facts give uneven weights. All 74 suppliers were attempted; 37 have failures. Retrieval success is a separate measure.

The new conservative certificate has **0 of 518 bundles certified** because the previous format does not contain the independent substantive proofs required by the new contract. This does **not** say none of the 551 legacy successful properties were researched or correct. It says they cannot be represented as a 100% certified release under the new rule.

The final score should use a versioned fixed catalog of required applicable logical data points, with each claim's required values, scope, units, qualifiers and source period; numerator = substantively verified within its declared freshness interval; denominator = every required applicable logical point. Verified no-change counts. Failed/missing checks stay in the denominator. An undisclosed answer counts only if the exact question explicitly permits a disclosure-status answer and primary evidence plus current discovery substantiate it. Historical immutable event values retain their original verification/provenance and reporting dates; latestness/discovery is a separate rolling obligation. Current prior-quarter comparison is verified for compatibility to the latest quarter without describing the old quarter as newly reported.

Separate claim verification, disclosure availability, current-discovery interval coverage, source retrieval/failures, proof age, attempt coverage and pipeline/deployment health. Retrying a failed source never renews a successful proof timestamp. Track per-claim `lastVerifiedAt`, per-discovery `checkedAt`/`coveredThrough`, publication/reporting dates, verification method, exact value hash, primary source/locator, source hash and contract version. Keep last attempt, last complete refresh, last published snapshot and app deployment as separate records. Do not add arbitrary green thresholds or treat an old reporting period as stale verification.

## Validation

- 267 data/guard tests pass; lint has zero warnings/errors; TypeScript passes.
- Publication guard rejects the real held candidate; normal release build exits **2**, and `lastCompleteRefreshAt` remains null.
- All autonomous-publisher fixture checks pass, including failed run leaving both remote refs exactly unchanged.
- Transaction fixture forces collector failure after changing data and a false date: all active files/date restore, partial candidate persists and lock releases.
- 26 local development UI browser checks pass at desktop/phone. Six generated JSON/feed endpoint checks cannot pass on a dev server without the withheld release build; the initial full dev-server run exposed that distinction and one test import issue, which was fixed. No claim of a 32-check production-artifact pass is made for this new change.
- Local full-page renders at 1440/390 plus folds were captured and inspected. The updated date/status wraps on phone. New local UI contains held candidate facts; it is not a substitute for the production snapshot or an approved deployment.
- Original repo remains on preview with only unrelated `lessons.md` dirty, hash `e41099bf38d20cac88ee0cfff4f8496b9e1027cb3eb0a42140daff19384d7af4`; its contents are preserved.

## Remaining work

The strict goal is not achieved: **no 100% refresh exists**. Previously failed primary sources/current-discovery coverage remain blocked (37 suppliers), 14 undisclosed answers need explicit question policies, and private/segment/ownership applicability needs a reviewed fixed inventory. Do not convert these into passes or fabricate dates. The complete contract also needs an independent source-content/structured-data verification adapter that emits typed proofs, fixtures against incorrect/contradictory content, and exact-value mappings for every required component. Current receipts contain URL/body hashes and narrative reasons; this is insufficient for automated substantive certification.

Next implementation: reconcile the parent's fine-grained catalog/applicability/undisclosed policies into the versioned contract; add the independent content-match and structured-SEC proof adapters; retain successful proof timestamps while retrying genuine failures and alternate public sources; rerun the single collector pipeline until every required claim passes. Then prepare the publication/date/change receipt, run the full built-artifact suite and compare desktop/phone renders, obtain approval of the new preview as required, promote the exact clean SHA, verify Ready and exact public receipt, and deliver the update message. If approved exclusions alter scope, report the changed denominator and contract version explicitly.

Workflow installation, owner-provided dedicated hosted collector secret and production build-skip placement remain separate prerequisites. No credentials/tokens/scopes/settings expansion, new scheduler, or weakened gate was introduced. A scheduler cannot guarantee unavailable external sources; the complete-refresh gate guarantees they cannot silently publish a partial update.
