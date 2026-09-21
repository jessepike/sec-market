# T7-3 — Figure-meaning check, unverified list, and stale report

Nothing on the site looks any different. Confirmed by building `origin/preview` (f47fd633, in a
scratch worktree removed afterward) and this branch with the same `npm run build` in the OrbStack
dev VM, then diffing `dist/index.html` and `dist/thesis/index.html` from both builds with the
hashed asset filenames normalized out (`-XXXXXXXX.js`/`.css` — Vite reassigns these every build
regardless of content): both files came back byte-identical. Detail and the exact commands are in
`dist-parity-check.txt` in this folder. This task only added build-time checks and a report script;
it did not touch `prints.ts`'s values, `domains.ts`, `hypotheses.ts`, or any other rendered data.

## What the check can and cannot verify mechanically

`web/scripts/verify-prints.ts` (npm script `verify:prints`, now in the `build` chain) compares
every scorecard print in `web/src/data/prints.ts` against the evidence it cites on four things:
company or segment, metric, reporting period, and value/units.

- **Company or segment** — checkable. It looks for the print's name (or, for a multi-name card, any
  one part of it) in the cited evidence's `organization` field, `title`, or `excerpt`. Organization
  alone was not enough: a small acquired company's evidence is often bylined under its acquirer
  (Veza's press appears under ServiceNow's name), so title and excerpt are checked too.
- **Reporting period** — checkable, using `EvidenceRecord.economicPeriod`'s free text. It classifies
  both the card's compact tag ("JUN '26", "FY26", "Q3 FY26", "Closed") and the evidence's period
  text into quarter / fiscal-year / calendar-year / point-in-time / unknown, and fails a card that
  labels a full year when its only cited evidence is a single quarter — the same shape of mistake
  SEC-043 corrected on an issue headline.
- **Value and units** — checkable. It extracts the card's numeric figure and the evidence excerpt's
  figures (expanding spelled-out "million"/"billion"/"percent" so "$12 billion" is comparable to
  "$12B"), and requires a matching figure of the same unit, exact or within a small, stated rounding
  tolerance (±1 percentage point for rates, ±2% relative for currency — Arista's card "+38%" against
  its evidence's stated "37.7 percent" passes on that tolerance; nothing in the real data needed it
  by more than that).
- **Metric — not checkable.** `EvidenceRecord` carries no structured metric field, only free text.
  Matching a metric label like "organic revenue" or "ending ARR" against prose would mean guessing
  at phrasing, which the spec asked me not to do. Every print reports this dimension
  "not-checkable," never a guessed pass.

A print's overall result fails only if a *checkable* dimension fails; a not-checkable dimension
never blocks a pass or hides a real problem, since it is reported separately and counted.

## Results on the repository as shipped

44 of 45 prints pass every checkable dimension. One is on the unverified list. Not-checkable
counts: metric 45 of 45 (always, by design), period 6, value 6, units 6 — the six are the scorecard
entries whose card value is categorical rather than numeric ("Closed" close-events, "No series",
"Seed," "Undisclosed," "Split," "TD SYNNEX"), so there is no figure to check.

**One real defect found, one entry on the unverified list — there are not three reasons to report,
only one:** `print-crwd-cloud` (CrowdStrike Falcon Cloud) labels its period "FY26," a full fiscal
year, while the only evidence it cites (`C13`) states "Quarter ended 2026-01-31" — a single
quarter's ending ARR. The figure itself (`>$800M`, `>35%`) is not in question, only the period
label. This is recorded in the new `web/src/data/printsUnverified.ts`, dated 2026-09-21, and its id
is in the shrink-only baseline `web/scripts/prints-unverified-baseline.json` — I did not fix the
label, per the instruction to record rather than fix a wrong figure; that is the owner's correction
process.

The check was proven to fail closed on two synthetic cases that are not on any list: a card
labelling a full year over quarterly-only evidence, and a card value absent from its cited
evidence's excerpt. Both fail as expected — output in `verify-prints-deliberate-failures.txt`. The
same two cases (plus several more) are also asserted directly in `web/tests/print-checks.test.ts`.

## Going stale

`web/scripts/stale-report.ts` (npm script `report:stale`) as of 2026-09-21: 0 judged claims older
than 45 days (domain stances, hypotheses, and Platform-pressure rows are all currently within the
window), 19 of the 45 scorecard prints whose period ended more than 150 days ago (oldest is
`print-secuvy` at 995 days — a 2023 seed round with no fresher disclosure), 0 prints with a period
the parser could not understand. Full output in `stale-report-2026-09-21.md`.

## Test results

`npm test` (lint, `test:data`, `build`, `test:e2e`) passed in full: lint 0 warnings/errors,
`test:data` 124/124 (including the 44 new tests across `print-checks.test.ts` and
`stale-report.test.ts`), the build chain including the new `verify:prints` step, and `test:e2e`
37 passed / 1 skipped. Full output in `npm-test-output.txt`.

## Files changed

New: `web/src/data/printPeriod.ts`, `web/src/data/printChecks.ts`, `web/src/data/staleReport.ts`,
`web/src/data/printsUnverified.ts`, `web/scripts/verify-prints.ts`, `web/scripts/stale-report.ts`,
`web/scripts/prints-unverified-baseline.json`, `web/tests/print-checks.test.ts`,
`web/tests/stale-report.test.ts`. Edited: `web/package.json` (two new npm scripts, `verify:prints`
added to the `build` chain, the two new test files added to `test:data`),
`docs/active/gather-brief.md` (new §3 steps 5–6 and matching Deliver/PR-body lines; the file's
thesis-related lines, owned by a parallel builder, were not touched), `BACKLOG.md` (SEC-044,
SEC-045 statuses). No file listed as off-limits in the task (`intent.md`, `.claude/rules/`,
`lessons.md`, `web/src/data/evidence.ts`, anything under `web/src/data/issues/`,
`.github/workflows/`) was touched, and no value, label, tone, or note in `prints.ts` was changed.

## What I noticed but did not build

The month-year card comparison (e.g. "JUN '26") falls back to reading a month name and year
directly out of an evidence record's title/excerpt text when the record's structured
`publicationDate` names an earlier stage of the same event (an acquisition's announcement date
rather than its later close date — this is exactly `print-veza`'s real shape). That is a genuine,
if narrow, gap: `EvidenceRecord` has no structured "close date" or "effective date" field separate
from `publicationDate`, so a few point-in-time prints rely on text search rather than a structured
field. Adding such a field would make this cleaner, but it is a schema change to `evidence.ts`,
which this task was explicitly not allowed to touch, and it is more than this task asked for. Not
built; not added to BACKLOG.md either, since it is a small, speculative refinement rather than a
decision the owner needs to make now — worth raising only if a future print's period check is ever
wrong for this specific reason.
