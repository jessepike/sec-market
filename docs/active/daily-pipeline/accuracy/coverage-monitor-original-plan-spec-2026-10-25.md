# Preserve the original collection identity in monitor checks

October 25, 2026. Companion reliability repair to the inventory-bound coverage reader.
This addresses a separate retained counterexample. No source policy, source clock, publication
payload, allowance, schedule or main revision changes here.

## Retained counterexample

Independent replay of the complete cross-day release rehearsal retains real prior-day source
evidence with scheduledAt `2026-10-24T18:28:54.713214Z` and publication checkedAt
`2026-10-25T01:00:34.491456Z`. The original run is 2c57fb25…; its plan's raw SHA-256 is
52f5875609394b7aa52c793fe133c1d10a970f64cc57cff69fe89f21342e30c3 (104,866 bytes),
authenticated under the retained seven-source archive manifest 895213b3…a1e5c.
Its rebuilt public coverage bytes are SHA-256
56b42229af9d56a739791e72faeda61ebd7c54122a729a5fabc14364b54b8c14 (1,337,255 bytes).
This is retained local release-rehearsal evidence, not a newly published or scheduled release.

The current separate_health reconstructs tasks from final checkedAt, generating the October 25
run and task IDs. It rejects this valid older source inventory as invalid/uncollected, suppressing
the specific backlog alarms. Replaying the unchanged original plan restores the exact incomplete
intake, processing-pending 10,632, held 5 and historical-pending 10,631 reasons. Healthy stays false.

## Scope

For accepted separate-intake coverage, use each coverage object's original archived run plan.
Read and validate it through the existing authenticated archive reader. Independently reconstruct
that plan from the current contract and its original scheduledAt and require exact identity,
inventory, task and supplier/source joins. Validate run IDs before constructing archive paths.
Require coverage runId, contract and inventory identities to match that verified original plan.
Require original scheduledAt not to follow checkedAt. Any existing public scheduledAt must agree
with the original plan. Missing, forged, differently bound or malformed plans must fail closed.

Use the original plan for raw collection and public separate-health task checks. The current raw
collection and accepted public release may legitimately be different runs: load the public
release's own plan and keep the existing collection-has-not-reached-production alarm rather than
substituting the latest private plan into older public data. The inventory-bound reader still
requires the accepted manifest/gate/public-byte binding before trusting a public payload.

Keep receipt-age and actual source-expiry evaluation against the current monitor clock. Do not
replace any observation, economic date, scheduledAt, checkedAt or validUntil with a new time.
Keep all 557 obligations and all incomplete intake, processing/history, held-claim, candidate,
unregistered-source, stale-source and pending-timer alarms. Old-policy non-separated behavior
remains unchanged. This is an identity repair, with no new coverage or qualification credit.

## Verification

Use the retained actual cross-day public bytes, rebuilt raw coverage and original archived plan
to reproduce the old rejection and prove exact preserved backlog reasons after repair. Record
which raw receipt is source-original versus gate-rebuilt; do not conflate them. Seal all consulted
frozen inputs and use a read-only adapter. Include actual current fc8bf098 coverage as a same-day
regression. No passing fixture may gain a fabricated original plan or refreshed date.

Tests must reject wrong run/day/contract, changed plan/tasks/inventory, source/supplier mismatch,
invented or future scheduledAt, missing plans and falsely fresh public data. Verify a valid older
accepted public run remains separately checked when newer private collection is pending. Run
the watchdog and operational suites, independently review the complete combined watchdog diff,
and retain the precise original-versus-repaired results. No web build or visual change follows.

The inventory reader and original-plan repair stay on preview until reviewed promotion is
allowed. A later manual preview monitor can exercise both against actual production; real
scheduled-main monitor operation remains a distinct receipt to obtain after promotion.
