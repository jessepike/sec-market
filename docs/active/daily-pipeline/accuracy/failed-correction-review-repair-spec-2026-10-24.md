# Check Point and Zscaler correction review repair

Proposed bounded repair, reviewed by root under the existing accuracy work. This document does not admit or publish either correction. Exact hashes, source excerpts and the four preserved admissions are in [failed-correction-review-repair-spec-2026-10-24.json](failed-correction-review-repair-spec-2026-10-24.json).

## Finding

Actual manual collector `40042968468` produced 244/557 coverage and admitted Optiv, Splunk, Expel and the scoped Xage publication-role correction. Check Point's review returned `rejected` with `source_support: fail`; Zscaler returned `ambiguous` with `source_support: unknown`. Each passed the other six checks. Neither response contains a rationale. The failed attempt/review objects remain immutable.

Both submitted notes claim that the event was already recorded elsewhere in the tracker. Issuer documents cannot establish that internal tracker state. Check Point also calls the entry a duplicate, and Zscaler calls the resignation unrelated. Removing those assertions is a supported reduction in scope; their presence is a plausible explanation for the source-support results, not a proven account of the reviewer's reasoning.

The complete pinned primary texts support the retained factual correction. Check Point's December 2025 Form 6-K explicitly dates closing to December 8, 2025, with total principal of $2.0 billion. Its July 2026 results release describes the $1.8 billion cash comparison net of issuance costs and purchased capped calls. The filing separately states approximately $1.97 billion before the capped-call use; those amounts must not be collapsed. Zscaler's April filing explicitly dates the board resignation effective April 15, 2026; April 16 is the signature date. Its September filing supports the October 1 CRO transition and advisory period through December 31. Both groups pass existing structural/source/excerpt checks against these complete retained bodies, with combined inputs of 27,245 and 7,511 characters.

## Exact permitted changes

Change only Check Point's `reasonCode` from `duplicate-issuance` to `incorrect-issuance-period` and replace its note with:

> Correction, {date}. The Check Point debt entry dated 30 July 2026 incorrectly described a new Q2 offering. The offering closed on 8 December 2025. The Q2 cash comparison used proceeds after issuance costs and capped-call purchases. The July issuance entry is withdrawn.

Replace only Zscaler's note with:

> Correction, {date}. The Zscaler entry dated 24 September 2026 included a board resignation with an incorrect effective date. Raj Judge resigned from the board effective 15 April 2026. That clause is removed; the September entry retains the Chief Revenue Officer transition.

Keep every target original/proposed object, operation, ID, source binding, complete body, observation time and evidence excerpt unchanged. Keep all four accepted group objects and per-group review hashes exact. Regenerate only the global policy stamp and changed groups' review hashes using the existing formula. Dependent synthetic build fixtures may change only where they pin those exact policy values or expected notes. Leave immutable originals, historical audits, prior drafts, accepted admissions and review protocols unchanged.

## Admission and verification

The changed candidates require new independent real reviews through the existing leased collector. No result may be inherited from the failed candidates, and acceptance is not assured. The seven checks, literal excerpt rule, 30,000-character whole-document-set cap, current clock/completion checks, reservation charges and all mandatory-group publication gates remain in force. Failed/ambiguous historical attempts remain visible. This is a corrected input, not a blind retry.

Prove a canonical diff contains exactly the three fields above and four accepted groups remain byte-equivalent. Recompute and independently match backend/Node/TypeScript policy expectations. Replay the four actual admissions read-only with zero model calls. Run focused correction/history/build checks and the operational suite in OrbStack before the next real collector. Initial admission using the current pins must finish by October 24 at 10:15:09.250598 UTC for Check Point and 10:15:08.041972 UTC for Zscaler. If that window is missed, require actual leased source refresh/rebinding before review; never renew an old timestamp locally. Publication still requires all six groups, the independent exact-artifact gate and acknowledged production/public-byte verification.

The offline diagnosis performs zero source requests, model calls, admissions, quota changes or archive writes. Production is unchanged. Root accepted this narrow repair direction; independent admission remains pending.

Independent review of the implemented request/stamp change passed: reversing exactly the three permitted fields reproduces the original full requests hash, every target/source is unchanged, and the new global policy is `e740d7407afc7b11be8802b250ea564224b10969717507818726e44e7b33f27e`. All four real accepted admissions replay under the new committed policy with unchanged group/review hashes and zero calls. This verifies retention and the input edit; the two changed candidates still require real review.
