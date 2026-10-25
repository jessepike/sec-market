# Actual recovery rollback and restoration

Manual drill `40173134585` passed on exact main
`6d5e87feba4ffbc75e50f35cb564cb8fd91708ca`. It exercised the retained parent release and restored
the accepted recovery release. Independent checks confirm every current static file matches on
both the restored public host and its immutable deployment. No source evidence, admission, queue
or allowance changed.

## Actual transition

| Item | Verified value |
|---|---|
| Restored accepted release | `fc8bf0984dbeacbe79519574911837d8b638f42215f6547e31ae8968b29951e4`, sequence 4. |
| Accepted deployment | `https://security-market-pulse-fqk0jyft3-pikeholdings.vercel.app`. |
| Retained baseline exercised | `19fde803d09aa544672183769c257e37faf727b75e1914955f54f3c5fb126941`, sequence 3. |
| Baseline deployment | `https://security-market-pulse-pjtpkd3hl-pikeholdings.vercel.app`. |
| Baseline application | `26181a2d4eb0aad1bd751cda70ab8e65142d2813`. |
| Drill journal | `2e55137fa20f550532be2f57dd3cf78c2621ae44ce516f09d78fc285a121bb31`. |
| Intent started | `2026-10-25T07:36:03.463501Z`. |
| Current restored | `2026-10-25T07:37:18.603441Z`. |
| Completed | `2026-10-25T07:37:39.753529Z`. |
| Final evidence archive | `b08469e082606def8ef37d9bfeb1cc9609f48176`. |
| Final archive manifest | `cb320933a9e384e87e9ba9dda631df4cfefa6cb441521b76e3b36ebeaaadd754`. |

The actual GitHub run completed successfully. Artifact `12591675214` matched GitHub's SHA-256
`1bd03981b975d45fffaa6676d9f370bf80ec122401089dab217af18f8515263f` after download.
Its receipt reports baseline byte verification and current byte restoration.

Each archived journal phase was fetched from the exact final commit and its Git blob hash checked:
`intent_archived`, `baseline_acknowledged`, `current_restored`, then `passed`. Their clocks are in
order, current and baseline identities match throughout, and no failure phase/category is present.
The completed journal head, immutable passed journal and actual acceptance record match the
downloaded receipt. The retained baseline record matches the journal, and its saved release
manifest reproduces its release hash. The production head remains the accepted sequence-4 head.

## Independent final byte proof

The retained accepted artifact was checked against its archived content address and tested
inventory. It contains 52 static files. Its authenticated detached receipt adds one expected
file, giving 53 files per host. All 106 final HTTP responses returned status 200, kept their
requested URL and matched the complete expected bytes. No sample or subset was used.

The immutable host is the accepted deployment above; the other host is
`https://securitymarketpulse.com`. Vercel's independent read-only lookup confirms deployment
`dpl_GFKc3mfpR6CSeZt7u62B5LVBqQjv` remains READY with production target. The final app, snapshot,
source expiry and corrections are the accepted recovery artifact, with no rebuilt or substituted
payload.

## Unchanged evidence and allowances

The authenticated before/after state-tree comparison shows changes only under `ci`, `cloud`,
`heads` and `rollback-drills`, which contain the drill's governance records. Every other state
subtree retains its exact Git tree hash. That includes all `objects`, `observations`, `facts`,
`correction-admissions`, `receipt-integrity`, contract and document-validation content.

The collector snapshot and correction outcome also retain their exact Git blob hashes and sizes.
The collector's 37-entry review queue, four fact-provenance references, original source clocks,
event/evidence dates and all six correction admissions therefore remain unchanged. The restored
public projection contains four current events and four pending historical records, as accepted.
Source expiry remains `2026-10-26T12:45:29.479727+00:00`.

The final ledgers exactly match the pre-drill publication ledgers: **2/2 gate attempts spent,
zero remaining**, and 72/80 source model calls, 33/40 documents and 444/5,500 fetches. The drill
did not create another release, gate, source check or admission.

Issue [12](https://github.com/jessepike/sec-market/issues/12) remains closed with its original
recovery close time `07:28:33 UTC`. The actual failed-acceptance alert step was skipped. Final
GitHub snapshots show zero in-progress and zero queued workflows.

## Scope and receipts

This was a manual drill after manual recovery. It does not establish genuine scheduled collection
or scheduled publication. I recommend recording manual recovery and rollback/restoration as
complete while leaving scheduled acceptance open. No application test suite was repeated by this
verifier. It made no commit, push, dispatch, promotion, archive write or source/model request.
All runtime, extraction and byte verification ran in OrbStack `dev`; no package was installed.

Machine-readable result:
`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/recovery-rollback-restoration-2026-10-25.json`.

Hashed evidence:
`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/receipts/recovery-rollback-restoration-2026-10-25/manifest.json`.

The receipt directory preserves the actual run/artifact metadata, downloaded result, retained
baseline, parent release, all four phase records, completed journal head and acceptance record,
before/after trees, counter records, issue and alert-step evidence, READY response and all 106
file comparisons. Raw downloaded bytes remain in OrbStack at
`/var/tmp/smp-recovery-rollback-restoration-40173134585-20261025/`.
