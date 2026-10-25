# Independent review of the coverage monitor repairs

October 25, 2026. Verdict: **pass for future preview**. Two review passes found no open
material defects in the combined watchdog change. The review covers the authenticated
coverage read and the separately approved original-plan repair. It grants no production,
scheduled-monitor, coverage, source or admission credit.

The governing files are
`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/coverage-monitor-inventory-bound-read-spec-2026-10-25.md`
and
`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/coverage-monitor-original-plan-spec-2026-10-25.md`.

## Actual defects and their repairs

The original failure is reproduced with the unchanged main reader and exact retained
coverage bytes. Manual monitor 40175735011 recorded a ValueError after the accepted gate,
deployment acknowledgement and application/data pairing checks. Its accepted public
coverage is 1,337,257 bytes, raw SHA-256
`ac8068379c6c79760331711bfb7bb6387fbc639f9ab6f921713502c6982d47fc`.
The old reader requests 1,000,001 bytes and rejects it. Unpacking the accepted build
reproduces the exact 9,441-byte inventory
`0c645ba2977c3e7e3df04a99d2d677ed5e7149b8608d3b472af0ea0b0c810c36`
and its sole `static/daily-coverage.json` entry matches the public bytes.

The repaired reader grants the larger bound only to the exact production coverage URL.
It first joins the production head to the self-hashed manifest, sequence and current
contract, verifies the exact GitHub gate receipt and artifact, and authenticates the
archived canonical inventory through a closed content-addressed reference. The sole
exact coverage entry must contain a raw SHA-256 and a positive integer size, excluding
booleans, with a fixed 40,000,000-byte ceiling. Invalid references fail before inventory
I/O. Missing authority cannot grant an inventory allowance.

The HTTP reader requests expected bytes plus one and requires exact raw size and hash
before JSON parsing. It preserves HTTP 200, unchanged final URL and the 25-second timeout.
Content-Length grants no authority. Other receipts keep the 1,000,000-byte default.
There is no larger generic reader, source fetch, host expansion or relaxed publication
acceptance. See `/Users/jessepike/code/projects/sec-market-finish-20261022/ops/watchdog/probe.py:145`
through its accepted-inventory and `get_json` helpers.

During pass one, a separate concrete durability finding was reproduced in the retained
cross-day release rehearsal. The original source plan begins October 24, while rebuilt
coverage finishes October 25. The old watchdog planned from the final checkedAt and
therefore generated different task IDs. It returned a generic invalid/uncollected alarm
instead of the real pending and held-work alarms. Root approved the companion scope
before implementation. This material finding, CM-IR-01, is resolved by the original-plan
helper at `/Users/jessepike/code/projects/sec-market-finish-20261022/ops/watchdog/probe.py:29`.

Each separate-health check now loads the archived plan for that coverage object's valid
run ID, reconstructs it exactly from the current contract and original scheduledAt, and
checks the complete plan digest, inventory, task and supplier/source joins. ScheduledAt
cannot follow checkedAt, and any public scheduledAt must match the original. Missing or
forged plans fail closed. Raw and public coverage load their own plans. Receipt age and
public validUntil still use the monitor clock. All existing subject, discovery, counter,
gap and candidate-registration checks remain in place.

## Evidence and independent checks

All runtime checks ran in OrbStack dev with sockets denied for actual-data fixtures.
No LocalStore was created on an actual archive. The reviewer wrote only this document
and its companion JSON.

* All 36 watchdog tests pass with zero skips, including the 20 existing tests. Command:
  `orb run -m dev env PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s ops/watchdog -p 'test_*.py' -v`.
* An additional 31 independent reader/inventory mutations reject short, long or changed
  bytes, wrong HTTP status, redirect, missing bounds, invalid types and hashes,
  oversized counts, wrong URLs, changed/missing/duplicate inventory and invalid JSON.
  The exact public response reads 1,337,258 bytes at most. Ordinary receipts still read
  1,000,001 bytes at most. Lying response headers have no effect.
* An additional 27 independent original-plan mutations fail closed, covering every
  required field omission, wrong run/day/contract/task/inventory, extra fields,
  source/supplier mismatches, future or invented scheduledAt and missing plans. An
  invalid run ID is rejected before construction of an archive path.
* Complete publication inspection passes through the real GitHubAuthority verifier
  using retained actual run metadata, artifact metadata and gate ZIP, followed by the
  real HTTP reader through a bounded fake opener. It reaches the honest unhealthy
  coverage, processing, public-progress and `HELD_CLAIMS_37` results without a generic
  probe exception. The main-loop regression separately preserves the actual prior
  pending-timer diagnosis. This is offline replay, not a newly exercised monitor.
* The original collection receipt, gate-rebuilt raw coverage and rebuilt public
  coverage all preserve their input clocks and restore the exact four cross-day
  alarms: `DAILY_INTAKE_INCOMPLETE`, `PROCESSING_PENDING_10632`,
  `PROCESSING_HELD_5` and `HISTORICAL_REVIEW_PENDING_10631`.

The exact cross-day evidence is deliberately distinguished:

| Evidence | Original clock and raw identity |
|---|---|
| Original archived plan | scheduledAt `2026-10-24T18:28:54.713214Z`; SHA-256 `52f5875609394b7aa52c793fe133c1d10a970f64cc57cff69fe89f21342e30c3`; 104,866 bytes. |
| Source-original raw collection | checkedAt `2026-10-24T18:32:56.227836Z`; SHA-256 `4780f1b69db3d5b7fef1d599ce88819d80fe84fbf5d002f1f21ff00b64672180`; 1,100,518 bytes. |
| Gate-rebuilt raw coverage | checkedAt `2026-10-25T00:59:59.916017Z`; retained inside release-input.json SHA-256 `bae92100e98b4431d8084f0911fa420f240849f6e7eff4565a361ac4199fed7e`. |
| Gate-rebuilt public coverage | checkedAt `2026-10-25T01:00:34.491456Z`; SHA-256 `56b42229af9d56a739791e72faeda61ebd7c54122a729a5fabc14364b54b8c14`; 1,337,255 bytes. |

Those three coverage forms retain run `2c57fb25697bfc4b40df574890334adfa1d6d0df610837e12aa3a71e22515523`
and inventory `aeea6e8fadb530e67ade88b41ed83886a9fea5360dae15d7a2ffb1acd97148ba`.
The source-original receipt already passed the old same-day check. The rebuilt forms
provide the actual counterexample. The rehearsal is local retained gate evidence; it
was never an accepted production release or an actual scheduled run.

The older-public/newer-private test uses these exact older H rehearsal bytes and their
original plan alongside the actual newer private run. It isolates routing and preserves
`COLLECTION_HAS_NOT_REACHED_PRODUCTION`; its synthetic routing manifest and stubbed
acknowledgement do not establish accepted older H production provenance. The actually
accepted prior release 19fde803 uses old policy de1932 and schema 1, so it correctly
cannot serve as a passing H separate-intake fixture. No passing fixture invents a plan
or changes a date.

At the original monitor time `2026-10-25T08:13:04.369084Z`, accepted public validUntil is
still `2026-10-26T12:45:29.479727+00:00`. The combined incomplete-or-overdue alarm does
not establish source expiry. Expiry, incomplete intake, processing/history backlog,
held claims, correction inventory and actual-timer checks remain distinct and active.

## Seals and remaining validation

| Reviewed file | Raw SHA-256 |
|---|---|
| `ops/watchdog/probe.py` | `0b9793222a04511ee0b670bb4a3131ec5cd9662f33dd111a0d319797d3b80ac3` |
| `ops/watchdog/test_probe.py` | `24ae33093032fb59b87211af68a94c13a8802202b626159e60ee5b764e529aeb` |
| `ops/watchdog/test_coverage_reader.py` | `75b80f03d1010ee4b5db2fdaf14bde017662842b267cd08a78071dcdc481e70f` |
| Inventory-bound read specification | `5027f5832800fc28bfc1b418d1bc762fe62619baace4f7722995cd9d510a57d3` |
| Original-plan specification | `39267d5bdb052a75d022aa371c4a3e909e7fb9f54335322dae9bda0138826729` |

All 41 consulted retained files preserve raw bytes, size and mtime. Their complete
inventory is in the companion JSON, with seal
`93c917984f13107b4a421758614f6e1ac8ab269b9e304de495714f65165553c6`.
The two actual archive manifests remain exact 895213b3 and 540bb044. Fixture copies are
checked against the corresponding originals, accepted build entries and original
manifest records. The JSON also pins the unchanged workflows, source contract,
disabled operational diagnostic, collector, Fetcher, provenance, publication,
correction policy, baseline, original facts and watchdog worker configuration.

The implementation worker's retained full operational suite passes all 858 tests in
19.192 seconds. Root verified that its final code/test hashes match this review. The
raw log is 159,820 bytes, SHA-256
`04d821c12afed968145dc860f547fa04e67fc2231de45e23912dc1d4a4b718e4`;
the retained gzip SHA-256 is
`f4cf38d58deaeea53ebd5f37d38d2767ba10b8f908f202042deea9997cb576da`.
This full-suite result is separately attributed to the implementation worker and was
not duplicated by this reviewer. No application build or render is needed for this watchdog-only change.
I would retain the reviewed repair on preview because it restores inspection of the
accepted bytes and their original task identity while keeping the real failures
visible. An actual manual preview monitor and eventual genuine scheduled-main monitor
remain separate execution receipts to obtain through the approved release path.
