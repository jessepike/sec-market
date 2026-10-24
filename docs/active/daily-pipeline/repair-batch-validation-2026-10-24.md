# Coverage and rollback repair validation

This batch preserves the 74 suppliers, 557 declared obligations, source admission rules and daily
limits. It repairs pending-work accounting, adds seven disclosed fetch-only diagnostic targets and
retries complete rollback receipt/static-file verification without weakening its criteria.

## Local evidence

OrbStack application verification passed 353 data tests, 115 pipeline tests and 43 browser tests.
The integrated log is
`/Users/jessepike/Documents/Codex/2026-10-22/security-market-pulse/renewal-20261024/qualification-integrated-application.log`.
The rollback repair additionally passes 18 focused tests and the complete 449-test operational suite.
Run focused rollback tests with `PYTHONPATH=web/scripts/pipeline:ops/ci` to resolve pipeline imports.

Before/after local full-page renders use the same retained input data. Both 1440px and 390px images
are pixel-identical. The comparison record is
`/Users/jessepike/Documents/Codex/2026-10-22/security-market-pulse/renewal-20261024/qualification-visual/local-comparison.json`.
Current production was also rendered at both widths. Its newly admitted correction data changes
some event counts and copy; the desktop page is 37px taller than the older local data fixture.
No layout or style change is claimed by this batch.

## Remote evidence and remaining checks

Production still serves release `a564d0a471931329bdf8a2e263bf26838ecb23d06d4a98d78cc4735c629c44f4`.
All 53 public files previously matched its exact tested artifact on both public and immutable hosts.
The failed rollback run `40047154814` restored current production and verified its bytes.
The retained parent immutable acknowledgement and all 25 files also verify independently.
The original remote failure category remains unknown.

Local tests and renders do not prove a repaired live drill or scheduled execution. The next steps
are preview CI, the approved promotion, a controlled live drill on repaired main, the leased
diagnostic and actual recurring receipts. No new source is qualified by the diagnostic alone.
