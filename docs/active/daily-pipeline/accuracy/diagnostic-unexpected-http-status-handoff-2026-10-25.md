# Unexpected HTTP status diagnostic handoff

The narrow correction is ready for independent review. `Fetcher` now accepts the strict boolean,
default-off `unexpected_status_diagnostics` option. After the existing final-host and bounded-body
checks, opted-in opened non-200 responses return failed observations with exact status, URLs,
time, content type, body reference and `UNEXPECTED_HTTP_STATUS`. Only the validated schema-1
source-probe caller enables it. Existing HTTPError, 304, retry and redirect handling remains.

## Verification

All runtime work ran in the OrbStack `dev` VM against fictional HTTPS transport and temporary
archives. Host and VM code hashes matched. Each run used a fresh `PYTHONPYCACHEPREFIX` directory.

- The new focused module passed all 13 tests. It covers default exception/no-body-write parity,
  unchanged successful responses, exact 201/204/206 retention, complete body identity, strict
  boolean rejection, host and size guards, HTTPError 403/429/503 and 304 behavior, unchanged
  transport/retry counts, actual leased diagnostics, schema-2/Orca constructor parity, and proof
  rejection. The actual diagnostic loop retained seven failed explicit observations, stopped
  before parsing those bytes, and returned zero source-check, coverage, semantic or model credit.
- The full operational suite passed all 818 tests in 21.658 seconds:
  `python3 -m unittest discover -s ops/ci -p 'test_*.py'`.
- With the parent's explicit approval, one existing test in
  `ops/ci/test_orca_redirect_diagnostics.py` was renamed and its schema-1 constructor expectation
  was updated to include the new opt-in. The rest of that module is unchanged.

## Reviewed file hashes

SHA-256 values, relative to `/Users/jessepike/code/projects/sec-market-finish-20261022`:

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/fetcher.py` | `82084e87bb41687fec8ebfc969cf0a37294e04312a47a27993f5c359a585adce` |
| `ops/ci/collect.py` | `70823c921fb849fa814b7a26f39044448896638b1eae9961a6c0d6b684bbb5fc` |
| `ops/ci/test_unexpected_http_status_diagnostics.py` | `14b99ea73de9f43b1e9ed9b0ff22497f31ca8239655495f2a46b4a757bd84bb9` |
| `ops/ci/test_orca_redirect_diagnostics.py` | `10d9d49bb46fcc90c0c5ab109f81961ee0b561557ca0ad869181cda9f889fc9d` |

## Limits and remaining work

This is local preparation only. No Git operation, dispatch, source/model request, operational
plan change, main promotion or actual archive write was performed. The original Check Point
status remains unknown; fictional 206 coverage does not establish its status or add evidence to
the old receipt. Main remains assigned to the frozen `6d5e87fe` scheduled-H acceptance and the
operational plan remains assigned to disabled `ad1`; neither was mutated by this work.

One immediate VM test after a host edit saw a partial mounted file and failed import. A subsequent
host/VM hash match and fresh-cache rerun passed before the complete suite ran. No source repair was
needed. Root owns independent review, preview build/render checks and any later promotion after
actual H acceptance. Worker writes stop at this handoff.
