# Correction resolution evaluator implementation addendum

This addendum implements the bounded current-remediation observation described in
`correction-resolution-evaluation-design-2026-10-23.md`. The five fixed benchmark rows,
their required before/after hashes, the 5-row denominator, and the historical 177-record
audit remain unchanged. The sixth publication-role correction is checked as a release
requirement but cannot resolve a factual benchmark row.

## Implementation boundary

`ops/evaluation/correction_resolution.py` is a read-only verifier. Offline invocation emits
five unmeasured rows. It accepts no evidence-package input and never treats nested domain
values such as `review.result: accepted` as authority. A measured result can come only from
the authenticated gather path; local flags and sidecar receipts are not used as proof.

The verifier derives the exact five contradiction IDs from the frozen audit and checks the
design mapping and hashes. For each mapping it requires the full factual group and all
atomic target hashes, replays the accepted admission through `load_policy` and
`replay_admission`, joins the independently verified gate artifact, checks the correction
projection and exported effective values, and joins the release manifest and acknowledged
production receipt. The Xage publication-role group is required in the release inventory,
but excluded from the five factual rows.

Every resolved row also traces its immutable admission to exactly one original accepted
attempt. The attempt must match the group, candidate/evidence/policy hashes and review
reference; the admission time must fall inside its start/completion interval; and the
document reservation must match the group and attempt start. The original collector
execution and its Actions receipt artifact are authenticated, and the attempt, reservation,
admission, review and collector record must all appear in the gate's exact archive
checkpoint. A later cached admission without the original accepted attempt cannot earn
resolution credit.

Authenticated mode binds the exact published source commit and its correction policy/code,
the archived collector checkpoint and GitHub receipt artifact, all six admission/review
joins, the independently authenticated gate artifact and archive checkpoint, the archived
publisher finish record and GitHub publication receipt artifact, and current Vercel receipts
and every expected static byte. The expected byte set comes from pure
`artifacts.stage_files`; the verifier never calls `adapter.stage`. It does not dispatch a
gate, write to the archive, reserve quota, stage/promote/rollback a deployment, call a model,
or fetch market sources.

The observation computes `R`, `U`, and `M = 5 - R - U` from derived per-record states.
It passes only at `R=5`, fails only when an authenticated current read positively proves an
original contradiction remains effective or a verified rollback restores the original
effective values, and otherwise remains unmeasured. Rollback credit requires the restored
release's authenticated gate and publisher receipts, a matching archived rollback event,
the acknowledged production receipt and every expected live static byte. A disabled
correction export alone never proves an unresolved target. If the restored release lacks an
effective correction export or exact runtime source proof, the rows stay unmeasured. The
numerator is `R` when any row has authenticated current state and null when none does. No
overall score is emitted. The immutable historical contradiction result stays 5/5 and is not
relabeled as current precision.

## Current authenticated observation

The VM has no standalone `gh` executable, but the existing OrbStack `mac` bridge can invoke
the host's authenticated `gh` CLI directly. The evaluator uses that narrow argv-only bridge;
it does not copy credentials or accept host-produced JSON as authority. The first live
read-only attempt exposed and fixed an oversized recursive Git tree read by requesting only
the archive commit's root tree, where the manifest resides.

The authenticated gather succeeded against archive commit
`9c8737cb4213f149f788b7ef1414921b8951bf0e`, manifest SHA-256
`cd9d84c67a70f11b72eeba25a012e3402a88b2d5a9c692f145c225b0a2c3418a`. It measured 5/5 for
the fixed mapped targets. The joins include six admitted release groups, original accepted
review attempts and document reservations, original and current collector Actions artifacts,
the independent gate artifact, the publisher artifact, and current production receipts and
static bytes. This does not estimate current claim precision, recall or general site
accuracy. The historical 177-record audit is unchanged.

Eleven focused OrbStack tests cover the frozen five-row mapping, R/U/M arithmetic, fixed
denominator, historical immutability, publisher run/artifact join with a fake reader, nested
domain acceptance values, the `mac gh` bridge, archive byte verification, rejection of a
cached admission without an original accepted attempt, original reservation matching, and
the rule that a disabled export counts unresolved only with rollback proof. The separate
authenticated gather supplied the real Actions and production evidence.

## D-112 helper and policy compatibility check

A local-only compatibility simulation used the exact helper files from the last published app
revision (`26181a2d4eb0aad1bd751cda70ab8e65142d2813`) as one fixture and the current D-112
working-tree files as a separate candidate fixture. It exercised evaluator imports and
`corrections.load_policy` in both isolated helper sets. Neither path imports `separation`,
`retained_audit`, `snapshot` or `coverage_summary`: this evaluator replays correction admissions
through `corrections.py`, checks helper identities, and verifies the sealed release bytes; it
does not call collection validation or snapshot reconstruction. The D-112 `validation.py`
imports its separation helpers lazily, outside the evaluator's correction replay path. The
`coverage_summary.py` file is a CI helper, not a pipeline runtime dependency.

The D-112 candidate changes the global correction-policy hash because `load_policy` hashes the
entire market contract. In this local simulation the published-v1 hash was
`e740d7407afc7b11be8802b250ea564224b10969717507818726e44e7b33f27e` and the candidate-v2 hash
was `aeccba5ed7151d6b06f3e02c78da5d3fe91c83e825929d07fb87574e5b961667`; all six group review
policy hashes stayed the same. If deployment changes the contract before a matching current
collector/correction receipt exists, the prior-policy receipt cannot establish current
resolution. The evaluator now emits its existing all-unmeasured observation for that transition.
It does not accept the older receipt, change any pin, or reuse its admissions as current proof.
This is a candidate compatibility simulation, not a claim that D-112 has published or is live.
