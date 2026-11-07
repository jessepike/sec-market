# Daily operation through GitHub Actions and Vercel

This is the current operating route. Codex Cloud scheduling and an always-on personal computer
are not dependencies. The dedicated subscription login and existing GitHub/Vercel secrets are
already configured under D-109. Do not repeat credential entry or add a paid model API fallback.

## Jobs and receipts

| Job | UTC schedule | Responsibility |
| --- | --- | --- |
| `subscription-collector.yml` | 05:17 daily | Restore state, recover a dead runner's lease, collect bounded current changes, verify facts, archive attempts and coverage. |
| `subscription-publisher.yml` | After verified scheduled collection; after the independent gate finishes; 00:23, 06:23 and 16:23 daily | Split release (2026-11-07): the first run reserves a gate attempt, dispatches the independent main gate, records the open `pending-gate` head and ends, so no job is billed while the gate runs. The outside timer's `/api/finish-gate` check (every 10 minutes) starts the publisher once the gate has finished, because GitHub does not start the workflow_run callback for a gate dispatched by the workflow token. That run, or the next scheduled publisher run, validates its exact artifact, stages production without assigning domains, promotes, acknowledges and archives. A newer collection or code revision supersedes a pending gate. Identical acknowledged collection/code skips another gate. The two-attempt daily cap remains. |
| `freshness.yml` | Every six hours at minute 41 | Independently inspect the actual timer, archived coverage, heartbeat and public release; maintain an owner-assigned alert. |

05:17 UTC is 22:17 Pacific daylight time on the preceding calendar date. The schedules use UTC
and remain fixed when Pacific daylight saving time changes. GitHub can start a scheduled job late;
the overdue threshold is 30 hours. A manual dispatch never proves that a schedule fired.

The new schedules only become active when their reviewed definitions reach the default branch,
`main`. A prospective `publication.enabled: true` on preview does not activate production.
The publisher also requires main provenance and the explicit Vercel production-path controls.

## What may publish

D-112 versions source coverage as `daily_source_intake_v2`. Intake still uses the complete
557-obligation denominator. Processing and historical review have separate source/URL inventories,
reviewed, pending and held counts. Unknown dates remain explicit. An intake pass means the declared
source check completed; it supplies no complete-event, historical-accuracy or reader-value result.
Old combined 121/557 and 244/557 receipts keep their original contracts and meaning.

Version-2 collection receipts use `completed_intake` or `completed_intake_with_gaps` for successful
runner execution and retain the separate summaries through the immutable clock, checkpoint,
scheduled reuse, build, public app receipt and monitor. Completed historical review can still hold
claims. An uncollected preview baseline grants zero fresh checks and exposes its old timestamps.
The read-only canary retains its contract-match guard: an old-policy archive cannot prove that
the new-policy collector ran. Only actual new-policy collection can clear that transition hold.

Keep original semantic review dates during retained reuse. Known article changes and failures
remain due work within the existing bounded selection. Derived revalidation holds need their own
replayable provenance and close only against an independently verified current result; original
candidate-held records remain archived. A subsequent quiet day must reuse a sealed revalidation
cursor without presenting the old article as newly retrieved.

Public, sourced facts may publish after automated checks. Market judgments remain owner-written.
All 80 SEC claims must pass independent re-derivation from archived inputs. General coverage may
remain incomplete; every changed generic fact still needs its own source bytes, exact supporting
text and independent review. An unavailable source, exhausted allowance or missing registration
never counts as a successful check. Source checks do not certify every historical claim.

Current changes get priority over the retained historical audit queue. Every deferred URL remains
recorded. Finishing a bounded run is distinct from completing all 557 required source obligations.
The operational receipt says `executionCompleted` and `completed_with_gaps` separately from
`complete: false`. Job failures alert separately from ongoing coverage gaps.

## Publication and rollback

The fresh gate checks the evidence manifest, reconstructs the candidate, replays SEC data, runs
the complete application suite and exports the exact static payload. The publisher verifies the
actual GitHub run, main revision and artifact digest. It stages those files with production target
and no assigned domain, then checks every static file and detached receipt byte for byte.
After promotion it repeats the checks against the public host.

Promotion intent is checkpointed remotely before changing production. A failed acknowledgement
returns to the retained, previously served immutable deployment using Vercel's rollback API.
A subsequent runner can recover an interrupted, fully journaled promotion. A preview gate can
produce a review-only deployment, but its provenance cannot authorize production.

The initial cutover must disable the legacy `certified-refresh.yml` and `promote.yml` schedules,
turn off Vercel auto-assignment and ignore Git builds from main/archive. This closes competing
publication routes. Preserve the currently verified production deployment as the rollback baseline
before that cutover. No dirty checkout or source upload is used by the publisher.

The owner approved activation and the one-time rollback/restoration check under D-110. These
controls were applied and verified. Promotion and rollback use explicit project/team API routes;
the high-level CLI account lookup that caused the earlier probe/promotion failure is bypassed.
After an alias change, the adapter verifies that automatic domain assignment stays disabled.

After an acknowledged release, the publisher's `preview-data` job copies the gate's tested data
files (`generated.zip`, hashed in the gate receipt as `generatedSha256`) to
`web/src/data/generated/` on `preview`, so the preview URL shows current figures. It never touches
`main` or production and uses no secret. It skips when preview's own daily-data check refuses the
data, for example when preview already carries a newer source contract. The data commit is pushed
with the workflow token, so it starts no web CI run. To promote a tip that ends in a data commit,
fast-forward `main` to the newest commit with a passing `web` run, or let the next push to preview
run CI over it.

## Failure and recovery

Collector/publisher execution failures create or update an issue assigned to `jessepike` and
close it after execution recovers. The separate monitor maintains the coverage/publication alert.
An assigned issue and GitHub API receipt prove GitHub delivery; phone/email delivery additionally
depends on the owner's GitHub notification settings.

Only a GitHub run that the API confirms has finished may have its abandoned lease released.
Recovery records the identity and preserves every budget counter. Cooperative cancellation stops
new reservations and attempts to archive in-flight work. A hard kill conservatively retains the
reserved allowance because actual usage is unknown. Never reset that allowance to force a retry.

The October 23 UTC fetch ceiling was explicitly set to 5,500 after an interrupted old-revision test
reserved 5,000 requests. The additional 500 deterministic requests are bounded; the charged 80
model calls and 40 documents were not refunded. Actual fresh run `39899030431` used no model
calls and finished 244/557 checks, with final charged fetch count 5,367. SEC work has priority over
citations when the remaining allowance is scarce. The next UTC day naturally gets its own ledger.

Candidate-source diagnostics use the existing collector workflow's manual `source_probe: true`
input on `main`. Standalone `onboard` fails before opening state or transport. The diagnostic run
restores the verified archive, acquires the shared remote lease and acknowledges a fetch-only
ceiling before any request. It preserves model counters, normal collection receipts and alerts.
Each logical request uses the actual current UTC day; exhausted capacity, deadline, cancellation
or a day change stops further requests without a refund. Final persistence requires the last
acknowledged archive commit. Manual archive pushes also require `--expected-commit`.

The command after the reviewed implementation reaches main is:

```sh
gh workflow run subscription-collector.yml --repo jessepike/sec-market --ref main -f source_probe=true
```

This produces a separate `source-probe-receipt` artifact, with no source qualification, coverage
credit, model work or publication. It does not replace the actual scheduled collector. Never use
a temporary empty store or a separate restored clone to spend outside the shared lease.

## Evidence

- Production audit and completion record: `finish-acceptance-2026-10-22.md`.
- Varonis primary-source correction: `receipts/varonis-missing-event-2026-10-22.md`.
- Fresh collection: run `39899030431`, archive `991432eea90004d3d8a2b0fb1c80ac28f01904b4`,
  manifest `a8c686a2cd6fea61ce307ebf393d8138011544b3388ed11ffee05363e225fb92`, 24,685 files.
- Actual failure alert: issue #8, assigned to the owner.
- Actual October 23 scheduled collection `39946689429`, gate `39947450834`, publication
  `39947099729` and controlled rollback/restoration `39947974279` passed. The published revision
  is `7bd94ec77e99462c068f254e134235a894585cbb`; all 25 public static files match the gate artifact.
- Scheduled publisher `39948978666` correctly skipped an identical release. Scheduled acceptance
  retry `39954446259` verified the prior actual scheduled source work without fetching again or
  changing its check time or budget counters.
- Execution alerts #8/#9 recovered. Scheduled monitor `39950995198` keeps assigned issue #10 open
  for incomplete coverage and 28 held review items. See [activation receipts](activation-2026-10-23.md).

October 23 used both gate/publication attempts and its conservative collection allowance. Preserve
that historical outcome. Current allowances come from the acknowledged UTC-day ledger. The
[reviewed October 25 promotion decision](accuracy/main-code-promotion-before-next-gate-decision-review-2026-10-25.md)
allows reviewed collector repairs and bounded diagnostics through preview/main while production
waits for its separate gate. Vercel Git production builds and automatic domain assignment remain
closed. A later main revision needs its own code-bound gate; never reset or refund an allowance.

Full source coverage and a sustained run of clean days remain distinct acceptance work. Do not
describe partial coverage, one successful release or an installed schedule as sustained operation.
