# HTML qualification ACK repair review

The repair matches the production API. `GitArchive.push()` returns `commit`, `parentCommit`, `manifestSha256`, `files`, and `ref` in [archive.py](/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/archive.py:105). `checkpoint()` returns that object as `archive` after writing the same value to `heads/remote-archive.json` in [run.py](/Users/jessepike/code/projects/sec-market-finish-20261022/ops/cloud/run.py:115). The seed now requires a 64-character `manifestSha256` and exact equality with the stored remote ACK in [html_qualification_seed.py](/Users/jessepike/code/projects/sec-market-finish-20261022/ops/ci/html_qualification_seed.py:246).

The regression test calls the production checkpoint and `GitArchive.push()` code, checks the manifest digest computed from the generated archive manifest, and checks the stored ACK equals the returned archive object. Only the Git transport boundary is stubbed; no network or subprocess is used. Separate cases reject legacy `sha256`-only and missing-manifest ACKs even when those malformed values are written as the stored head. The focused OrbStack suite passed all 19 tests.

The fix changes only the ACK field name and its tests. It leaves the exact package, H, payload allowlist, authority registries, preservation checks, and zero-credit behavior unchanged. The previous mismatch explains why the first ordinary collection stopped before model or source work; this review does not claim a successful H collection or a production publication.

Reviewed code SHA-256: `68c66beda7c00e65361c90e7bc30efffc2e19a41804ae76ebffd40914d9236e4`.
Reviewed test SHA-256: `0a4fa2722229369d8179938a2fa2fb9b1428a0825d6ac438071eef774ee56b6d`.
