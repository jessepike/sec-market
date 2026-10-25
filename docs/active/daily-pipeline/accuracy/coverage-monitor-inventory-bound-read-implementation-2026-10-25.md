# Coverage monitor repair implementation

October 25, 2026. The combined repair passes all 36 watchdog tests and all 858 operational tests, with zero skips. Independent review passes with no open material findings. This is a reviewed preview repair; actual manual preview and scheduled-main execution require their own receipts.

## Change and scope

The public coverage reader now derives its exact byte count and SHA-256 from the accepted release's authenticated artifact inventory. It joins the production head, self-hashed manifest, current contract, verified GitHub gate and artifact identity before reading the canonical inventory. The only larger allowance is for `https://securitymarketpulse.com/daily-coverage.json`, using the sole exact `static/daily-coverage.json` entry. The reference and entry have closed schemas, positive integer counts excluding booleans, valid hashes and the existing absolute ceiling of 40,000,000 bytes. Invalid references fail before inventory I/O.

The reader requests the expected length plus one, then checks exact raw length and hash before parsing. HTTP 200, the unchanged final URL and the 25-second timeout remain required. Other receipts retain their 1,000,000-byte limit. Content-Length cannot grant an allowance. Old paths without authenticated authority retain the default limit.

The separately approved original-plan repair loads each coverage object's own archived run plan. It reconstructs the complete plan from the current contract, original scheduledAt and prior-run identity, then checks its digest, run, inventory, tasks and source joins. Raw and public coverage use their respective plans. Missing or forged plans still fail closed. Receipt age and source expiry continue to use the monitor clock.

The changed runtime and test files are:

| File | Raw SHA-256 |
|---|---|
| `/Users/jessepike/code/projects/sec-market-finish-20261022/ops/watchdog/probe.py` | `0b9793222a04511ee0b670bb4a3131ec5cd9662f33dd111a0d319797d3b80ac3` |
| `/Users/jessepike/code/projects/sec-market-finish-20261022/ops/watchdog/test_probe.py` | `24ae33093032fb59b87211af68a94c13a8802202b626159e60ee5b764e529aeb` |
| `/Users/jessepike/code/projects/sec-market-finish-20261022/ops/watchdog/test_coverage_reader.py` | `75b80f03d1010ee4b5db2fdaf14bde017662842b267cd08a78071dcdc481e70f` |

The governing specifications are `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/coverage-monitor-inventory-bound-read-spec-2026-10-25.md` and `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/coverage-monitor-original-plan-spec-2026-10-25.md`.

## Actual retained evidence

The accepted coverage body is 1,337,257 bytes with raw SHA-256 `ac8068379c6c79760331711bfb7bb6387fbc639f9ab6f921713502c6982d47fc`. Its canonical accepted inventory is 9,441 bytes with SHA-256 `0c645ba2977c3e7e3df04a99d2d677ed5e7149b8608d3b472af0ea0b0c810c36`. The unchanged main reader rejects these bytes after reading 1,000,001 bytes. The repaired reader requests 1,337,258 bytes and accepts only the exact pinned body.

The full offline current-production replay uses the real GitHubAuthority verifier with retained actual gate metadata and artifact ZIP, followed by the real HTTP reader through a bounded fake opener. Sockets are denied. It reaches the specific incomplete-intake, pending-processing, held-document, historical-review, public-progress and `HELD_CLAIMS_37` alarms without ValueError or a generic probe failure. The original actual collection diagnosis, `SCHEDULED_COLLECTION_RECEIPT_DIFFERS`, remains in the combined replay. This is offline proof, not a new Actions run.

At the actual monitor clock `2026-10-25T08:13:04.369084Z`, source validUntil remains `2026-10-26T12:45:29.479727+00:00`. The combined incomplete-or-overdue alarms reflect incomplete work here; they do not prove source expiry. The original actual failure and unchanged-main reproduction remain in `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/recovery-monitor-2026-10-25.md`.

The cross-day evidence preserves three distinct forms of the same actual run and its original plan:

| Input | Unchanged clock | Old result | Repaired result |
|---|---|---|---|
| Source-original raw receipt. | `2026-10-24T18:32:56.227836Z` checkedAt. | Four specific backlog alarms. | The same four alarms. |
| Gate-rebuilt raw receipt from retained local rehearsal. | `2026-10-25T00:59:59.916017Z` checkedAt. | Generic invalid/uncollected alarm. | Four specific backlog alarms. |
| Rebuilt public receipt from that rehearsal. | `2026-10-25T01:00:34.491456Z` checkedAt. | Generic invalid/uncollected alarm. | Four specific backlog alarms. |

The original plan begins at `2026-10-24T18:28:54.713214Z`, with SHA-256 `52f5875609394b7aa52c793fe133c1d10a970f64cc57cff69fe89f21342e30c3`. All three coverage forms retain run `2c57fb25697bfc4b40df574890334adfa1d6d0df610837e12aa3a71e22515523`. The restored alarms are `DAILY_INTAKE_INCOMPLETE`, `PROCESSING_PENDING_10632`, `PROCESSING_HELD_5` and `HISTORICAL_REVIEW_PENDING_10631`. No date, task, receipt or source value changes.

The older-public/newer-private test uses these exact older H rehearsal bytes and their original plan alongside the actual newer private run. A synthetic routing manifest and stubbed acknowledgement isolate plan selection and preserve `COLLECTION_HAS_NOT_REACHED_PRODUCTION`. This test does not establish an accepted older H production release. The actually accepted prior release 19fde uses old policy de1932 and schema 1, and correctly fails the current H separate-intake check.

## Checks and retained output

All runtimes ran in OrbStack dev. The final commands were `python3 -B -m unittest discover -s ops/watchdog -p 'test_*.py' -v` and `python3 -B -m unittest discover -s ops/ci -p 'test_*.py' -v`, run from the finish repository with bytecode disabled. They pass 36 and 858 tests respectively, with zero skips. The operational suite completes in 19.192 seconds. The existing 20 watchdog tests remain covered. Git diff whitespace checks pass. No application build or render was needed for this watchdog-only change.

All receipts are under `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/receipts/coverage-monitor-inventory-bound-read-2026-10-25/`. The test logs use deterministic gzip with byte-exact verified round trips; no raw output was normalized.

| Log | Raw SHA-256 | Raw bytes / lines | Retained gzip SHA-256 |
|---|---|---|---|
| `watchdog-tests.log.gz` | `c579c0d5249f89723f49a2a8b9e5da4f6f08eb55180ba04d2e9608c335af9498` | 6,471 / 41. | `bc3f38213b4f7e22ab255a720de52763f61fc9109a2be9db8eabbf395c939e57` |
| `operational-tests.log.gz` | `04d821c12afed968145dc860f547fa04e67fc2231de45e23912dc1d4a4b718e4` | 159,820 / 863. | `f4cf38d58deaeea53ebd5f37d38d2767ba10b8f908f202042deea9997cb576da` |

The receipt directory also contains authenticated compressed actual fixtures, `fixture-input-seals.json`, `current-production-replay.json`, `cross-day-original-versus-repaired.json` and the final `verification.json`. Ten directly consulted original archive/rehearsal inputs preserve bytes, length and mtime. No LocalStore was initialized on a frozen archive. The independent review rechecks all 41 consulted retained files and 20 code/protected pins.

The independent review is `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/coverage-monitor-inventory-bound-read-independent-review-2026-10-25.md`, SHA-256 `fd0bf77eb91b979ab68acbd0948fb9ace0f9d15b4f8debdf6b7e26740bb4989b`. Its JSON companion has SHA-256 `8c977ec082e8881d5f7cf46b86dec161dd5c4bd22981f560a3d1e99f30acf095`. Two review passes, 36 independent tests, 31 reader mutations and 27 plan mutations pass with zero open material findings.

## Remaining validation and preservation

I would retain this reviewed repair on preview because it restores inspection of the accepted coverage and its original task identity while preserving the actual alarms. An actual manual preview monitor and a genuine scheduled-main monitor remain separate execution evidence. This implementation handback grants no scheduled-run, production, coverage or admission credit.

This unit makes no source or model requests, gate reservations, workflow dispatches, archive writes, publication changes or main changes. Contracts, workflow files, source freshness repair, quotas, factual corrections, admissions, queue and source clocks remain unchanged. The accepted release remains `fc8bf0984dbeacbe79519574911837d8b638f42215f6547e31ae8968b29951e4`, sequence 4, with the actual pending, held and timer reasons retained. No code, test or fixture bytes changed after independent review. Parent owns commits, preview execution and release decisions.
