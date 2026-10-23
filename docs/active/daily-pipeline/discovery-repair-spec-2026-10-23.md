# Discovery repair specification, October 23, 2026

## Scope

Repair the two discovery failures proved by the candidate-registration audit. Keep the
74 suppliers, 557 obligations, current contracts, source registrations, budgets, primary
objects and observation times unchanged. The implementation and replay are offline and
non-admitting. No network, model, gate, publication or archive-write operation is allowed.

## Implementation

1. Add a deterministic decoded discovery view. Gzip output and ordinary input must stay
   within 32,000,000 bytes. Preserve raw bytes and classify XML or HTML after decoding.
   Keep XML entity declarations prohibited. Invalid or oversized compression fails closed.
2. Recognize Barracuda's exact observed newsroom component on the exact company/news
   endpoint. Its cards container and fallback text cannot establish quiet. Return incomplete
   with the disclosed same-host JSON endpoint and no navigation items. Do not implement
   a JSON adapter before its response and first-party controller are captured.
3. Add the explicit `orca-news-pagination-v1` HTML completeness mode. It applies only to
   the existing Orca official-announcement supplier binding and exact news-index paths.
   Separate index pages from official release cards. Read the observed featured and
   horizontal card classes, require the `Press Releases` category, a matching title link
   under `/resources/press-releases/<slug>/`, and the card's explicit publication date.
   Ignore external news cards, navigation, templates and scripts.
4. Require the known newsroom/listing/pagination containers, one current-page marker that
   matches the requested URL, safe numbered page links and agreement between head
   `rel=next` and the observed `next page-numbers` anchor. Deduplicate identical next
   signals. Advance by one page. Reject loops, conflicts, unsafe destinations, unknown
   continuation, missing pages and the existing page-cap exhaustion. Terminal recognition
   is conservative: the known pagination region has no next, higher numbered page or
   ellipsis, and its current page equals the traversal's highest advertised page. This
   contract has synthetic acceptance only; no actual terminal page is archived.
   Require a nonempty recognized static card container on every page. Synthetic quiet
   coverage uses older dated release cards after a complete synthetic traversal. An
   empty container, JavaScript placeholder or unproved empty layout remains incomplete.
5. Preserve the existing generic HTML mode and all currently verified contracts. New mode
   validation checks the exact source identity and URL roles; this work activates none.
   No runtime configuration pins a daily-changing terminal body hash. Registration
   qualification must separately retain an actual terminal response and full traversal.

## Acceptance and receipt

Dedicated offline regression tests cover bounded gzip HTML/XML, decompression failure and
limits, the Barracuda shell, Orca card isolation, next-link agreement/deduplication,
loop/unsafe/conflicting/unknown controls, page caps, missing pages and synthetic positive,
quiet and blocked terminal results. Run all existing pipeline and operational tests in
OrbStack.

Replay the actual read-only Orca and Barracuda primary bodies. Retain their exact raw hash,
size, observation ID, original retrieval time, code hashes and resulting incomplete
receipts in a new discovery-repair replay receipt. Orca page 2 is absent and cannot be
invented. Synthetic terminal success earns no source qualification or live coverage.
