# Controlled rollback acceptance

This manual drill is prepared for the owner's cutover review. It has not run.
After the first accepted main-gate release is acknowledged in production, run
the `controlled production rollback acceptance` workflow on main with that
current release's SHA-256. The job uses the existing credential and project.

The owner's activation approval also authorizes one automatic acceptance after
a successful actual scheduled `daily exact-artifact publisher` run on main.
The workflow independently reads the upstream run from GitHub and requires its
private repository, workflow path, main revision, scheduled event and completed
success. This route is restricted to UTC October 23, 2026. It skips a legacy
production head and any previously recorded drill phase, so it cannot repeat on
later daily runs. It derives the target from the accepted archived production
head and verifies that release matches the upstream publisher revision.

A separate read-only preflight runs before requesting the shared account
concurrency group. It skips when a collector is queued or running, and requires
a successfully finished actual scheduled collector with its matching immutable
archive receipt. Manual collection cannot substitute for this proof. This
avoids placing a new pending acceptance job ahead of a waiting collector; if
preflight skips, the already authorized manual drill remains available. Only
the mutating job receives the existing Vercel credential. The preflight has no
model work, archive writes or production access.

The retained receipt includes the upstream scheduled publisher ID and clock,
and matching archived collection-run receipts when available. Missing or
incomplete source coverage is preserved. Manual acceptance still requires its
explicit expected release and can be used for a directed recovery or rerun.

Before publication replaces the production head, it retains the previous head
at `production-baselines/<releaseId>.json`. Its ordinary pre-promotion remote
checkpoint archives that immutable record. The drill obtains the baseline
through the accepted manifest's parent release ID; it accepts no deployment URL
from workflow inputs.

The drill checks both immutable deployments are ready production targets in
the existing project. It verifies the current accepted main-gate artifact and
all its static bytes, then remotely acknowledges its drill intent before any
domain change. It rolls back to the retained prior production deployment,
checks the live baseline receipt, and always attempts to restore the latest
accepted immutable deployment in a `finally` block. Restoration checks every
static byte against the accepted artifact. The production head stays on the
latest accepted release throughout; a separate `heads/rollback-drill.json`
records the temporary phase and final outcome.

The original legacy baseline has an exact app receipt and immutable URL, but
no retained original static inventory. Its receipt check is reported with
`baselineByteInventoryAvailable: false`; the restored current release receives
the full static-byte check. Later daily-release baselines retain their tested
artifact inventories and receive full byte checks too.

The drill creates no release, gate attempt or publication-budget exception.
It uses instant rollback for both already served deployments. No rebuild or
unvalidated payload is introduced. A forced runner termination can prevent
the `finally` restoration from completing; the remotely acknowledged intent
and current-restored phase distinguish that state. The owner alert and archived
immutable targets support recovery. Do not cancel a running drill to test this.
