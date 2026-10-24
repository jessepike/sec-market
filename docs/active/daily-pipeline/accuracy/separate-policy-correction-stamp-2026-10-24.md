# Correction policy binding during D-112 migration

The prospective market contract changes from `market-daily-v1` to `market-daily-v2`, adding
`daily_intake_with_separate_history`. The enclosing correction-policy stamp therefore changes
from `e740d7407afc7b11be8802b250ea564224b10969717507818726e44e7b33f27e` to
`aeccba5ed7151d6b06f3e02c78da5d3fe91c83e825929d07fb87574e5b961667`.

The stamp was recomputed from the complete current market contract, unchanged correction requests
and immutable baseline. All six group-specific review-policy hashes are exactly unchanged.
The Python `load_policy` verifier passes. No original admission, source observation, review
hash, candidate, effective value, publication date or failed attempt was rewritten.

The build test retains the old global-policy assertion against the pinned historical contract
and separately derives the prospective stamp from the current contract. The build verifier
continues to require an exact stamp and full group/source/target binding. No validator was
relaxed to accommodate the migration. A new exact gate and publication receipt remain necessary
before this prospective policy can describe production.

The reproducible actual-archive [migration replay](separate-policy-correction-replay-2026-10-24.json)
also passes. It verifies all 31,075 archive files and the tested production artifact, replays all
six cached admissions under the prospective policy, and projects a simulated next-day release.
Every group row, all 12 targets, original admission metadata and group publication dates remain
exactly unchanged. Source/model calls, reservations, state writes and publication attempts are
all zero; archive content and timestamp seals match before and after. The simulated future time
exercises date retention only and supplies no new current-release or collection credit.

Run `ops/ci/replay_correction_policy_migration.py` in OrbStack with the verified extracted archive
and its pinned manifest SHA-256. It refuses external network/process/file mutations during replay.
