# Preserve the observed coverage definition in transition alerts

Actual scheduled monitor 40064680975 correctly failed and updated issue 10 at 05:02 UTC.
All 19 monitor tests passed. The old archived report and production still use combined coverage,
but the invalid separate-coverage fallback labeled the old 244/557 result `daily_source_intake_v2`.
The failure reasons were accurate; that observed-measure label was not.

Repair only that fallback. Report `expectedCoverageMeasure: daily_source_intake_v2` when the
new policy requires a valid separate observation but none passes validation. Omit the observed
`coverageMeasure` in that case. Keep all failure reasons, counts, dates and alert delivery.
Valid collected schema-2 coverage still reports its validated observed measure. An unknown or
invalid receipt cannot earn the new definition merely because current code expects it.

Verify the actual retained legacy report, uncollected schema-2 coverage and invalid partitions
all fail without an observed measure; valid schema-2 coverage retains the intake label. Run the
focused monitor suite in OrbStack. This change admits no fact and changes no public site data.
