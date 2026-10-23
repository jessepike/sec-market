# Retain unchanged correction reviews during coverage repair

Prepared October 23, 2026 under SEC-072. No factual corrections have been admitted or published,
so this changes the candidate protocol before its first real use. It changes neither intent nor
the 74-supplier / 557-obligation baseline, budgets, source dates or publication authority.

## Problem

The candidate binds every correction review to the hash of the entire market contract and entire
correction request list. Adding an unrelated source or a later correction therefore invalidates
all existing reviews. The projector also rejects a previous bundle merely because its global
policy hash differs. That prevents durable correction history while the declared coverage gaps
are repaired. It must be fixed before activation.

## Two precise bindings

The existing global `policySha256` remains the hash of market, full requests and baseline pin.
It binds the build, collection outcome, required group/target inventory and release. No task is
removed and no new registry entry is activated by this change.

Each atomic group's independent review instead binds to a group review policy:

```
digest({
  "schemaVersion": 1,
  "rulesVersion": "dated-factual-correction-review-1",
  "baselineSha256": requests.baseline.sha256,
  "candidateSha256": digest(group),
  "supplier": {"id": supplier.id, "name": supplier.name, "aliases": supplier.aliases, "kind": supplier.kind},
  "sources": configured source objects for group.sources, in their committed group order,
  "model": {"provider": market.model.provider, "allowApiBilling": market.model.allowApiBilling,
            "maxDocumentChars": market.model.maxDocumentChars},
  "freshnessHours": 30,
  "checks": sorted seven existing review check names
})
```

Only relevant exact source registrations participate; unrelated registrations, global request
version/list growth and run/gate time do not. Candidate and evidence-set hashes retain their
existing definitions. The review response and admission's `policySha256` now mean this group's
review policy. The bundle and collection outcome's `policySha256` continue to mean the global
inventory/build policy. Name these two roles clearly in code and documentation.

The committed build stamp gains `reviewPolicySha256ByGroup`. Both backend and build verifier
independently derive it; pure browser projections receive the explicit expected map. Enabled
groups must match their own expected review policy. A missing or changed expected group policy
fails closed. Do not accept an arbitrary historic hash or silently fall back to the global hash.

## Replay and history

Accepted cache indices use the group review policy. The current gate replays the exact original
admission, full source bytes and initial source age under the currently derived group policy.
The evidence is not fetched again or relabelled. An unchanged historical admission does not
expire merely because an unrelated registration/request was added.

The projector can accept a previous bundle with a different global policy, but each retained row
must still exactly equal its newly derived row: ID, supplier, targets, dated note and all admission
metadata. A changed candidate/source/rules policy cannot reuse its old review, and cannot overwrite
an already published correction row. Such a change remains held for explicit reconciliation.
New disjoint groups require their own real current subscription reviews and new publication date.
Every group in the new global request inventory is still mandatory; no partial release.

This does not add sequential re-corrections of the same target or source revocation policy. Those
remain explicit future design work when needed. It does make the existing declared source repair
and addition of disjoint factual corrections possible without rewriting the first five rows.

## Verification

Prove that changing an unrelated source or adding a disjoint request changes the global policy
while leaving an unchanged group's review policy/cache and public row intact. No additional call,
document charge or new date may appear for that group. Changed relevant source/supplier/candidate,
wrong expected map, partial groups and forged hashes must fail. Old policy checks, atomicity,
post-review freshness/deadline, original export checks and real admission requirements remain.
Run backend and full application checks in disabled and isolated enabled modes. Synthetic reviews
and consistency seals cannot count as real admission. Main stays frozen for October 23 UTC.
