# Collector and publication continuity

## Confirmed defect

The first independent gate used the committed snapshot as its generic-data
baseline while production still had a legacy baseline. Later gates used the
published snapshot. Neither path included the collector's cumulative history.
This dropped unresolved work from the gate artifact even though the private
archive retained it.

At exact archive commit `b78cfa15980d7be9da54b31e28b16a0840c1d112`, both collector
snapshot heads have 466,580 bytes and raw SHA-256
`6bb35e0e786c96cf1ec51521ed60dde66a53745b871c7d566475690e6400da95`.
Their internal snapshot hash is
`c659d3cf6d969ab7d559779d60f2f69436a20aad1e04c556a5c407b16b59cc5e`.
They contain four historical events and 28 unresolved holds. The accepted
production artifact contains zero generic events and 14 holds. The monitor
reads the collector's queue, which explains its different count.

The four archived events concern the Mimecast board appointment dated
2024-10-01, eSentire CEO appointment dated 2026-03-19, Veeam partner/channel
appointment dated 2026-07-09 and eSentire acquisition dated 2026-09-15. Their
independent reviews use the older policy hash. They require explicit current
admission before publication; preserving them does not make them current facts.

## Conservative correction

The gate keeps the live published baseline for certified-data comparison and
previously published facts. Separately, it validates the collector snapshot's
digest, exact run, policy and coverage identity. It checks each held claim's
content hash, candidate, evidence, observation and review provenance. It replays
historical fact validation against its recorded review policy and verifies the
event and linked evidence against the archived source.

All unresolved holds are merged by stable claim and reason. Unpublished
collector events are retained in `pendingFacts`, including their original event,
evidence, source observation and review. Older-policy records receive
`CURRENT_POLICY_REVIEW_REQUIRED`; a current-policy record still needs admission
through the current independent receipt path. They do not enter public events
or supplier fields merely because a collector snapshot contains them. Existing
published events retain their original provenance and dates.

## Actual archive replay

The complete source archive was verified separately: 25,777 files, manifest
`760b5c38fcb7fba2a3a223233539cce4eb5aa47d559571efa95b287047ac1ff8`.
An offline replay used that restored state through a read-only store that
rejects writes. It combined the actual accepted production baseline with the
actual collector snapshot and reconciled archived receipts at the explicit
replay time `2026-10-23T12:00:00Z`.

| Result | Before | Candidate |
| --- | ---: | ---: |
| Published generic events | 0 | 0 |
| Unresolved holds retained | 14 | 28 |
| Unpublished historical facts durably quarantined | 0 | 4 |

All four retain their original source fetch times and evidence. The source
input coverage check stays `2026-10-23T11:34:15.010723Z`. The replay output snapshot hash
is `f4cd55db42ad690c26671d08ccbc97f10bf32bebf232263b7b50d246d6413873`.
No baseline write, source fetch, model call, counter change or publication took
place. Synthetic tests additionally reject snapshot tampering, a wrong run,
altered source bytes, resealed event edits and missing linked evidence.

## Remaining queue-resolution work

The existing snapshot builder carries old review items forward without an
explicit resolution record. A later accepted review of the same claim does not
automatically close the old queue entry. This correction preserves those holds;
it does not waive them. A separate resolution record must bind any closure to
the successful current-policy claim, evidence and independent review, retaining
the old receipt for audit. The 28 existing reasons are 18 missing dates, nine
ungrounded dates and one entity match. They are evidence/parser problems until
shown otherwise, rather than 28 decisions requiring the owner.

The candidate needs normal preview and release verification. It does not change
the frozen production revision or remove any of the 557 source obligations.
