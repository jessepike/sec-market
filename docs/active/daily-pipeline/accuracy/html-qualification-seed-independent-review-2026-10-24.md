# HTML qualification seed importer independent review

## Result

The importer is dormant and fails closed today: `SEED_PACKAGES` in `ops/ci/html_qualification_seed.py` and `ACTIVATION_AUTHORITIES` in `web/scripts/pipeline/source_qualification_origin.py` are both empty. The synthetic positive fixture exercises the intended flow, but it does not admit a real package.

The first review found that the importer compared a derived preservation summary with the same package's declared summary, without joining the selected coverage object to the original snapshot. The worker fixed that gap in the reviewed bytes below. The current verifier requires the original coverage's run and policy identity and all public coverage fields, except the private receipts and checked time, to match the sealed original snapshot's coverage projection. It also requires the original coverage check to be no later than the snapshot's check. The new negative test rejects an empty or different-run coverage object even when it carries the old contract hash.

The original repro used a temporary fixture: I replaced coverage with an empty object, recomputed the summary, and refreshed the fictional `SEED_PACKAGES` pin. That version accepted zero inventory pairs, zero bindings and zero facts. This changed the trusted fixture pin too, so it did not show archive-only self-authorization. The current coverage-to-snapshot join closes the demonstrated case.

The real positive package still needs its independent audit before either registry is populated. It must establish 26,969 all-pairs, 9,914 retained pairs, 24 bindings, 52 facts (including four ordinary facts), 32 holds and four public quarantines from the exact source archive. It must also verify that the four protected references identify the preserved quarantine evidence. The synthetic test fixture does not establish those real package values.

## Checks that passed

The bounded implementation otherwise has the intended ordering and closed payload shape:

- The ordinary collector hook calls `seed_before_collection` before scheduled reuse, restoring the model credential, creating the subscription agent or constructing the collector (`ops/ci/collect.py`, lines 305–323).
- For an activated contract, the seed preflights the complete seven-key payload and all three inventory origins through a read-only overlay before the first seed `write_once` (`ops/ci/html_qualification_seed.py`, lines 128–192 and 215–228). The no-origin path returns before payload access.
- The allowed payload graph is limited to the three inventory manifests, the transition descriptor and pointer, the activated contract, and the exact snapshot object named by the package. Existing immutable bytes must match (`html_qualification_seed.py`, lines 149–176).
- The run is bound to the private repository, `main`, the current app revision, collector role, exact GitHub run identity, ordinary lease and a non-probe event (`html_qualification_seed.py`, lines 195–212). The existing checkpoint compares the restored archive parent and updates the acknowledged archive head only after push (`ops/cloud/run.py`, lines 87–117); the seed then verifies the local acknowledgement and receipt fields (`html_qualification_seed.py`, lines 228–240).
- The seed receipt explicitly carries no coverage credit, semantic admission or source-check credit, and does not change the daily budget (`html_qualification_seed.py`, lines 226–228; `ops/ci/test_html_qualification_seed.py`, lines 208–217).

The focused suite passed in OrbStack: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ops/ci -p test_html_qualification_seed.py -v` (17 tests). The tests cover inactive no-I/O behavior, empty authorities, payload allowlisting and integrity, path/symlink rejection, all-three-origin preflight before import, lease/context rejection, remote acknowledgement failure, idempotent retry, and the coverage-to-snapshot join. The tests use temporary fixtures; they do not prove the real package’s preservation totals.

## Review pins

This review covers these exact bytes:

| File | SHA-256 |
|---|---|
| `ops/ci/html_qualification_seed.py` | `8a4b7561e9b6bdece984b635e8266a43ae5110e7cbf6d907193943c348502c7f` |
| `ops/ci/collect.py` | `00429db123d6e8e4a81665786118956708c52db4e62d9c13527d38eb3221f79a` |
| `ops/ci/test_html_qualification_seed.py` | `faa2cd236d26d45aedf65e838a6f57d53759fa8958c68d737fdd855801aec03b` |
| `web/scripts/pipeline/source_qualification_origin.py` | `5a762c411f1d81d9e4fc405a96a92194f28abfaedb8216dd4a3b6c8741218243` |
| `web/scripts/pipeline/storage.py` | `66ce4736cc1f5fb50998d1e59067904e6145a8195fa1c1fd27415e8cf93f00a5` |
| `web/scripts/pipeline/separation.py` | `b2c225fef1bb704701441a611ea921e325a5a28e6ac00fcdb2b4d7273413e629` |
| `docs/active/daily-pipeline/accuracy/html-source-activation-packaging-spec-2026-10-24.md` | `004c555923c5cfcd8ba1df0c2e1ad4e78dbdb2e655f6cae3fafe5cd29bdf27e2` |

No production authority was added, and no source requests, archive writes or runtime code edits were made for this review. Test fixtures wrote only to temporary directories.
