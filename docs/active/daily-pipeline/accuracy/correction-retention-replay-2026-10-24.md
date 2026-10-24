# Correction retention replay, October 24, 2026

Checked at 2026-10-24T01:33:53.481495Z. [Machine-readable evidence](correction-retention-replay-2026-10-24.json).

The six live correction groups, including the five factual groups and the separate Xage publication-role repair, remain effective after their original sources become older than 30 hours. The earliest window closes at 2026-10-24T10:14:49.799584Z; it limits making a new initial admission. It does not expire an accepted correction.

The replay used the actual six admissions in archive `4b325ab62385379c9d76b585ee3c3575ba8cab4d`, independently verified against manifest `3bebbef137b62f331b218fbf947bff25ca00a5bebf45bb3441dace9fd1fe619e` and all 30,823 files. The previous public bundle has hash `032d646ea910b1c1ad4cf78435b5e5bed07bf657ce64817e9dbc5d4de0cbb6e5`, bound to release `a564d0a471931329bdf8a2e263bf26838ecb23d06d4a98d78cc4735c629c44f4` and the retained production-byte receipt. No fresh network verification was performed.

With no model agent, a reservation function that raises, and all three store mutation methods guarded to raise, replay at October 24 05:17 UTC, October 24 16:23 UTC, October 25 16:23 UTC and December 1 16:23 UTC returned six admitted groups, zero pending groups and zero new attempts. Every public row, original publication date and review reference remained exactly equal to the live bundle. The archive's file sizes and modification times remained unchanged.

The key distinction is in [corrections.py](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/corrections.py:449): historical source checks use the original `admittedAt`. The accepted cache is replayed before any model/reservation path at lines 465–470. A direct initial-admission check of the same old pins at October 24 16:23 correctly fails as expired; historical replay succeeds.

Held or missing admissions returned no projection: `Correction admissions pending or policy changed` and `Correction admission inventory incomplete`. Relevant dependency changes require exact new proof and cannot relabel an old review. Published groups cannot disappear, and existing public rows/dates must remain exact ([corrections.py](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/corrections.py:526)). A new review cannot silently rewrite an existing published group’s admission metadata. Publisher preflight checks this against the previous artifact before reserving a gate; the independent gate repeats it before building. An unavailable required new review therefore holds the next release and leaves the corrected site served.

The browser uses a static validated projection, with no current-clock expiry or silent fallback to frozen originals. Coverage or SEC freshness can separately hold a later batch. An exact acknowledged code/collection pair remains a no-op; a failed later promotion rolls back to the prior acknowledged corrected release.

No expiry repair is needed. Preserve the existing historical-admission replay and complete-group continuity, and do not spend exhausted model/document capacity to renew accepted facts. These future-time tests establish code behavior, not completed future schedules. They made no source/model/remote calls, archive writes or quota changes.
