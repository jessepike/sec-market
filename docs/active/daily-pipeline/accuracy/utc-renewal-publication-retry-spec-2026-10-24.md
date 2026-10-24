# Publish after UTC allowance renewal without resetting a charge

Status: independently reviewed and implemented as a preview candidate under the existing activation approval.

## Actual evidence and problem

October 24 has two charged gate and publication attempts, so the approved new-policy code cannot
publish again until the next natural UTC day. Current production retains a source observation at
approximately October 24 00:38 UTC, with a 30-hour deadline at October 25 06:38 UTC. The existing
scheduled publisher runs at 06:23 and 16:23 UTC, plus genuine successful scheduled-collector
callbacks. That leaves only about 15 minutes between the first nominal October 25 publisher and
the old production deadline, before scheduler delay, the independent gate or staging time.

Actual scheduled collector 39954446259 was created October 23 at 12:35:17 UTC, while its retained
GitHub log identifies cron `7 7 23 10 *`. That observation is over five hours after the nominal
temporary schedule. It does not establish a fixed delay or a future guarantee, but it rules out
relying on a 15-minute nominal margin. The new normal 05:17 UTC collection has not appeared as of
05:21 UTC October 24. Do not replace its required actual timer evidence with manual dispatch.

## Scoped repair

Add 00:23 UTC to the existing daily publisher cron, retaining 06:23, 16:23 and the authenticated
collector callback. Use the same existing private GitHub workflow, lease, archive, current
correction preflight, independent gate and exact-artifact Vercel path. Retain the two-batch daily
cap and all charged attempts. No manual acceptance gate, counter reset, extra source/model work,
new service, purchase or paid API fallback is part of this change.

The early attempt can publish October 24's genuine new-policy source result after the allowance
renews, before the old production deadline. A later fresh October 25 collection can use the
remaining existing batch. An already acknowledged exact collection and code returns before any
gate charge, so a quiet extra scheduled attempt does not spend a gate/publication allowance.
Missing or invalid evidence still holds. This additional opportunity improves the margin; GitHub
cron remains best effort and must be judged by its actual execution receipt.

## Verification

Independently review the live old deadline, existing charged limits and the `release_daily` order:
exact acknowledged-code/data reuse and correction preflight precede the two-batch gate reservation.
Run the existing publication/release-control guard tests after the one-line schedule edit. Keep
collection schedule, source freshness, budgets, secrets and publication code unchanged. Retain
actual scheduled collector, early publisher, independent gate and production bytes as acceptance
evidence. A parsed cron or passing test is not an executed publication receipt.

## Local verification

The existing 50 publisher boundary, authorization, artifact-byte, disclosure/correction and
staging tests pass in OrbStack after the one-line cron change. No publication/controller,
collection, budget, credential or freshness code changed. The earlier code candidate passed
561 operational, 115 pipeline, 368 data and 42 browser tests; one uncollected deadline was skipped.
All actual early retry and production acceptance receipts remain pending.
