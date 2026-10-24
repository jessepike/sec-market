# Independent review: midnight partition replay

## Finding

The narrow repair preserves the intended split between an immutable processing record and current freshness. I found no remaining cross-midnight partition defect in the reviewed path. The actual archive replay succeeds at the next-day gate time without moving source dates, changing the saved partition, adding facts, or renewing the collection timestamp.

`reconcile` now loads the sealed receipt object and requires both the coverage receipt and immutable attempt record to equal it in full. It reconstructs the stored processing partition from that sealed receipt at its original `completedAt` through `HistoricalStoreView`, then separately computes current processing and intake details using the gate's real `now` and the current store. This prevents caller-supplied receipt fields such as `startedAt` or retained bindings from selecting a different historical window. The exact repair is in [validation.py](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/validation.py:229).

The current-time path remains strict. On the actual b78 archive, a read-only reconciliation more than 30 hours after collection returned a degraded result with 0/557 successful intake tasks and 557 gaps rather than treating the historical receipt as fresh or aborting the whole report. The focused regression separately confirms that a stale required primary transport is rejected with `Retained latest transport is stale or future`; old timestamps cannot satisfy a current required-document check.

## Actual archive evidence

The replay used actual collection run `2c57fb25697bfc4b40df574890334adfa1d6d0df610837e12aa3a71e22515523`, policy `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`, and archive `b78bd35bb531ed49480ce1557780d3b2d9a522a2` with manifest SHA-256 `3971ae961442d6a18c5ed145c64660d68190d91f470acf27b74c3d136f6d6849`.

At `2026-10-25T00:23:00Z`, the actual reconstruction completed reconciliation, collector-continuity validation, and snapshot rebuilding. It retained 264/557 intake successes, 23/10,655 currently reviewed documents, 10,632 pending, five held, one changed, and 291 with unknown dates. Historical review remained 24 reviewed, 10,631 pending, and five held. All four ordinary fact references and the 33-entry review queue remained present; no new fact IDs were produced. The original `lastCollectionAt` and `validUntil` were unchanged. These same counts and preserved timestamps were confirmed at `06:23Z` and `16:23Z`; those later reconstructions are not new collections or scheduled runs.

The canonical sealed replay and its exact command, full counts, snapshot hashes, and before/after archive seals are recorded in [the preflight evidence](/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/next-scheduled-publication-preflight-2026-10-24.md). That replay used an in-memory store for derived objects, denied filesystem writes, network and subprocess activity, and verified the unchanged 40,921-file / 1,904-directory archive. Its content, file-mtime, and directory-mtime digests remained unchanged.

## Tamper and snapshot checks

The five focused tests pass. They cover rollover of an item on the original 30-day boundary, reconstruction of the original partition, a changed/rehashed partition manifest, changed `completedAt`, alterations to the sealed receipt or immutable attempt record, expired current transport, and a later failed primary or changed subject policy. I independently ran the five focused tests and all 25 existing separate-freshness tests in OrbStack; both suites passed.

There is no second cross-time partition comparison at [snapshot.py](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/snapshot.py:229). `build_snapshot` first calls `reconcile` at the current time. The later read of the sealed manifest at line 270 only emits a revalidation marker for URLs already in its `revalidationRequired` list; `reconcile` has already authenticated that list against the original-time reconstruction. Marker verification also replays the original receipt at its original time.

The reviewed code pins are:

- `validation.py`: `38b19ad77aff48ba971589add57a9c1b01d505ca49d3c4738bb447007cd71b08`
- `test_midnight_partition_replay.py`: `5221f005f7dc12a956845b8b3673ec370be28e14ce4b331fa6c53b1ff440ef81`
- `snapshot.py`: `90d43e14582aca6567c2b611eb9d33700fb196ceba103bc26add3c499233b234`

This is an offline audit of validation and snapshot construction. It does not establish a scheduled collector run, successful publisher gate, publication, or new freshness beyond the recorded timestamps.
