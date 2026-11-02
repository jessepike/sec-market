# Reduce repeated GitHub runner work

The owner asked on November 2 to reduce runner usage while preserving the five-cent daily
Vercel limit and stopping the paid runtime trial. This change uses existing GitHub Actions only.

## Actual starting point

The November 2 scheduled collector `41453903198` occupied a runner for 21m24s, plus its
18-second schedule guard. Its full invariant test suite took 3m48s. Publisher `41457061782`
occupied 20m40s, plus a 16-second callback preflight; its identical suite took 6m24s.
The independent gate `41458664767` occupied 7m29s while the publisher waited. Rounded separately,
these jobs used 53 Linux minutes, before the rollback preflight, monitors, or other publisher
timers. These are actual API job/step times, not a billing settlement.

## Small, reversible change

Run the complete operational invariant suite in the existing `web` CI job on code changes.
Before a hosted collector or publisher repeats that suite, read GitHub's successful CI result
for the exact checked-out revision. Accept only this private repository's push run on main or
preview, the exact `.github/workflows/web.yml` path, and a successful `test` job with the named
successful full-suite step. The checked-out HEAD must equal `GITHUB_SHA`, the checkout must have
no tracked modifications or nonignored untracked files, and its Git tree hash is read and logged
to bind the runtime, workflow and test files together. Missing, malformed,
foreign, stale, paginated, incomplete or inaccessible proof runs the full suite as before.
The bounded readback is logged, with the actual CI run/job IDs. It does not cache a writable flag.

Every runtime input, schedule eligibility check, credential, lease, budget, source, archive,
independent SEC and exact-artifact validation remains in place. The hosted helper is not used
to enable the dormant managed runtime.

The collector-completion callback remains the primary publication trigger. Reduce its three
daily fallback publisher timers to one at 16:23 UTC. The 05:17 UTC daily collector schedule,
manual recovery entry, all execution alerts and six-hour independent monitor remain. The real
November 2 callback succeeded before that fallback despite the collector's long scheduling delay.
An unsuccessful callback can still recover at the daily fallback or next actual completion; an
unusually late failure after the fallback may wait until the following day. The existing 30-hour
overdue check continues to alert. This trades repeated no-op attempts for one daily recovery
attempt, without declaring a missed publication successful or weakening its two-attempt allowance.

Expected saving from today's observed repeated suites is 10m12s per collector/publication pair.
Each unchanged scheduled publisher timer also avoids its repeated full suite; November 2's
publisher timing suggests about 6m24s per timer, before rounding and variable test duration.
The full suite still runs once for each tested code revision, or on any uncertain CI readback.
No reduction is claimed as hosted until the reviewed code reaches main and actual runs exercise it.

## Conservative forecast from the observed November 2 timings

Round each hosted job separately to whole minutes. The observed current daily chain is schedule
guard 1 + collector 22 + callback preflight 1 + publisher 21 + gate 8 + expired rollback preflight 1
= 54 minutes. Three no-op recovery timers and their rollback preflights add 3 × (10 + 1) = 33.
The unchanged monitor's three jobs four times daily add 12. Total: about 99 minutes/day.

With exact-code CI reuse, the same observed collector becomes 18 minutes and publisher 15;
the chain is 44 minutes. One fallback becomes 4 + 1 = 5 minutes; monitoring remains 12.
Total: about 61 minutes/day, 1,830 minutes per 30 days, about $10.98 gross Linux compute at
the existing $0.006/minute rate. Against $12 included compute, this leaves about $1.02/170 minutes
for retries, code-change CI and other repositories. This is a forecast with limited headroom,
not a billing receipt or proof of a sustainable month. A failed CI proof deliberately spends
the old full-suite time, and collection/source variation can increase daily usage. Recheck actual
hosted timings and shared allowance after activation; do not enable paid GitHub overage.

## Verification and release

Exercise exact proof acceptance, SHA/ref/path/repository/job/step mismatches, failed/retried jobs,
malformed and oversized JSON, API failures and fallback test failure. Run the helper tests and full
operational suite in OrbStack. Verify workflow syntax and the three workflow edits. The source is
a major operational change and carries `Owner-Review: required`. The owner requested the work;
production still follows preview, the independent release gate and the accepted artifact.

Local verification on November 2: the full operational suite passed 1,072 tests in 190.615s
before the final clean-tree and schedule assertions; all 13 final helper/schedule tests then
passed. All three edited workflows parsed with the VM's existing PyYAML, and the source diff
passed whitespace checks. Actual old CI run `40532987330` has no new suite step, so it cannot
grant reuse. The new step must genuinely execute in hosted CI before any scheduled job can reuse
it. No workflow was dispatched and no preview/main branch was pushed by this implementation unit.
