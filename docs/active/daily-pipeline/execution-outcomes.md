# Runner completion and source coverage

The private collector reports `executionCompleted: true` only after collection,
reconciliation, snapshot creation and the final acknowledged archive checkpoint
finish without cancellation or an exception. Its command then exits zero.
`outcome` is `completed_complete` when coverage is complete and
`completed_with_gaps` when source obligations remain incomplete.

The existing `complete` coverage field retains its actual value. A completed
bounded run with missing sources still reports `complete: false`. It does not
upgrade any task, field, source, freshness claim or publication gate. The
independent coverage monitor continues reporting those gaps. The runner alert
reports execution failures and cancellation separately.

Setup failures, exceptions, missing execution completion and cancellation exit
two. Cancelled runs report `outcome: cancelled` when they can finish a graceful
checkpoint; abrupt termination can leave conservative escrow and a missing final
receipt instead. Existing recovery rules preserve that unknown usage.
