# Daily operation through GitHub Actions and Vercel

This is the current operating route. Codex Cloud scheduling and an always-on personal computer
are not dependencies. The dedicated subscription login and existing GitHub/Vercel secrets are
already configured under D-109. Do not repeat credential entry or add a paid model API fallback.

## Jobs and receipts

| Job | UTC schedule | Responsibility |
| --- | --- | --- |
| `subscription-collector.yml` | 05:17 daily | Restore state, recover a dead runner's lease, collect bounded current changes, verify facts, archive attempts and coverage. |
| `subscription-publisher.yml` | After verified scheduled collection; 06:23 and 16:23 daily | Invoke the independent main gate, validate its exact artifact, stage production without assigning domains, promote, acknowledge and archive. Identical acknowledged collection/code skips another gate. |
| `freshness.yml` | Every six hours at minute 41 | Independently inspect the actual timer, archived coverage, heartbeat and public release; maintain an owner-assigned alert. |

05:17 UTC is 22:17 Pacific daylight time on the preceding calendar date. The schedules use UTC
and remain fixed when Pacific daylight saving time changes. GitHub can start a scheduled job late;
the overdue threshold is 30 hours. A manual dispatch never proves that a schedule fired.

The new schedules only become active when their reviewed definitions reach the default branch,
`main`. A prospective `publication.enabled: true` on preview does not activate production.
The publisher also requires main provenance and the explicit Vercel production-path controls.

## What may publish

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

The current day used both gate/publication attempts and the full conservative collection allowance.
Keep main on the accepted production revision for the rest of that UTC day. Documentation updates
stay on preview; temporary acceptance-trigger cleanup joins a later ordinary code promotion.

Full source coverage and a sustained run of clean days remain distinct acceptance work. Do not
describe partial coverage, one successful release or an installed schedule as sustained operation.
