# Independent review of the two-request Q4 data diagnostic

Date: 2026-10-25. Governing specification: `q4-initial-data-diagnostic-spec-2026-10-25.md`, introduced in `71c39356`. Verdict: PASS, with no open material findings after two review passes. This accepts the dormant implementation for the next reviewed activation step. It grants no source qualification or actual API-response evidence.

## Reviewed scope and proof

The new module permits the two reviewed initial GETs for JFrog and Rapid7. The fixed canonical plan hash rejects extra, absent, mistyped or substituted fields before it reads historical proof. This includes method, request body, query order/values, source, category, controller row, host and archive references. It permits equivalent JSON formatting of the same closed plan; it does not generate new targets. As in the existing Q4 plan parser, duplicate known JSON keys use their final parsed value. That parsed object must still match the exact approved canonical tuple, and the report binds the submitted raw plan bytes. This format behavior creates no additional source, method or query authority. Rubrik and its separate legacy widget remain excluded.

`web/scripts/pipeline/q4_initial_data_capture.py:26` checks the exact actual capture record, outer run/attempt/event/ref/app revision, completed diagnostic status, unpublished outcome and zero-credit fields. It then invokes the unchanged `q4_controller_capture.verify_report` on the original six-script plan and complete retained report. The source joins at line 55 separately bind JFrog and Rapid7 to their original HTML and actual API wrapper/raw-observation/body/time. Identical API body hashes cannot transfer the observation or source authority between them. The sealed inspection excerpts bind the public/language functions, widget/category configuration and controller request construction without evaluating JavaScript.

The actual proof came from the authenticated `9634b916c15b18f38605a168f7642de764670aab` extraction at `/var/tmp/smp-q4-controller-actual-20261025/extracted`. Its manifest SHA-256 remains `600e58564c989206856ba48795bf4ce9f6fbbf73a604e806594e95327b53203a`. The actual capture record reference is `ci/source-probe-runs/40179255547-1.json`, SHA-256 `0e5a08ff0c64750dcb441e640fc1dae0926a2cf5ab674920e48058bfd7da02d7`, 10,301 bytes. All original clocks stay attached to their retained observations.

## Runtime and failure behavior

`validate_plan` at line 92 performs the complete proof check before operation writes. `execute` at line 199 checks the current raw plan and exclusive bound budget, then stores the plan and permits at most two logical reservations. The caller change in `ops/ci/collect.py:243` adds only the new operation selection to the existing leased source-probe path. Preflight still precedes budget construction and escrow. Existing bootstrap and failure receipts remain available.

The response check at line 112 requires actual HTTP 200, unchanged exact final URL, no observed redirect, an explicit JSON MIME, UTF-8 and a nonempty JSON object. Known raw bytes are retained before classification. HTML, empty/nonobject/malformed JSON, invalid UTF-8, nonstandard NaN/Infinity constants, wrong MIME/charset/status, and redirects retain their diagnostic failure evidence. A service-error object can be captured for review but earns no business-data or completeness claim. The real existing Fetcher continues to send GET with its JSON-capable Accept header, no body and no Content-Type or conditional validators for these calls.

When Fetcher returns no observation after a network, read or size-cap failure, response status/MIME/body/final URL remain unknown and the charged transport error remains recorded. This does not add response metadata that the existing transport did not supply. Two logical reservations retain the existing Fetcher retry and redirect policy; they are not a new guarantee of exactly two physical HTTP exchanges under every failure.

The module and caller finalization preserve cancellation, partial/full quota denial, pre-invocation midnight denial with its charge but no request marker, and final in-flight day/deadline checks. The retained-report verifier at line 247 reconstructs results and joins counters, reservations, observations and times. Every result and report keeps facts empty, model calls/source checks/qualifications zero, and semantic admission/coverage credit false. The normal collector, source scopes, publication route and admission code are unchanged.

## Independent checks

Pass one reviewed the specification, complete new module, exact dormant plan, caller diff, existing Fetcher, original HTML/controller proof, and tests. No material defect was found. The response-retention boundary above and rejection of Python's nonstandard JSON constants were checked explicitly.

Pass two ran in OrbStack with network sockets denied:

- All 22 focused tests passed, with no skips: 19 new-operation tests, two actual previous-controller proof tests, and the existing test covering all six original admissions.
- A separate read/get-only actual-archive replay passed with LocalStore construction denied. The unchanged six-script verifier was invoked, including its original charged parent proof.
- All 244 independently generated recursive plan mutations failed before any proof read. They removed every dictionary key, added an unknown key to every dictionary and replaced every leaf with an invalid type.
- A malformed caller plan produced only its allowed failure receipt. Budget construction, escrow and Fetcher construction were guarded to fail if called, and none was called.
- A separate real-Fetcher offline harness sent the exact two synthetic GETs, with no body, Content-Type or conditional headers. It retained both JSON responses and changed only the temporary fetch counter from 450 to 452; model calls 72 and documents 33 stayed fixed.
- All 16 additional report mutations were rejected, covering source ownership, query-proof reference, extra request fields, third requests, clocks, budget day/counts, altered result reasons and every nonzero-credit attempt in that set.
- All six actual admissions from the acknowledged archive and their existing per-group review-policy hashes replayed unchanged. Their exact references and hashes are retained in the companion JSON.

All 76 consulted original input seals retained their bytes, lengths and nanosecond mtimes. The archive had no write interface in the pure proof/admission checks. Writable synthetic execution used a separate temporary overlay. No source or model requests were made and no JavaScript was executed.

The implementation worker separately ran 74 focused route tests, 877 operational tests, 36 watchdog tests and the full application suite. Its retained gzip logs independently match their compressed/raw hashes and exit-zero metadata. The application suite passed 377 data tests, 115 pipeline tests and 42 executed browser tests, with one existing browser-fixture skip. Both same-data local render files are byte-identical to the previous reviewed local files at 1440 and 390 pixels. These are worker-run full-suite/render results, with independent receipt-byte verification here; they are not additional actual source evidence.

## Reviewed seals and limits

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/q4_initial_data_capture.py` | `87ded82d37b5c51a121b769eaa084ad20bc691ca16a25929d13e7b004a99f8be` |
| `ops/ci/collect.py` | `928e082f5b633a973a6ad7704ab70ecc150d5f2dbbd5aa448e3e03d9a4a3592b` |
| `ops/ci/test_q4_initial_data_capture.py` | `8a97c12233f34c8fa6e333a321437f989c8286785b9a1dc49e0223ebb7e914e0` |
| Dormant `accuracy/q4-initial-data-capture-plan-2026-10-25.json` | `a316e39658c2e9b5872adeb6008ef138618c8b20a080ca78ee458bd3e51f0ddc` |

The dormant plan canonical hash is `5ec3a0fc8588e64af13f8caeec32f3c4327f3b60c2526123ff49b41d219a8dae`. The active `contracts/source-qualification-probes.json` remains disabled SHA-256 `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4`. H remains canonical `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`, raw `24221c946781559c0ff3626e4e479c4647da915d0f2d7559ea88046982532c3c`. The six-script module remains `8720cd8bed0c533201c24565ca28b23198f99f8a352213e07774f6f05f15ffb3`.

I recommend proceeding with the separately reviewed exact-plan activation. The actual API responses still need to establish status, JSON contents, dates, response size, server limits and primary links. Neither `pageSize=-1`, `year=-1` nor captureComplete establishes the required thirty-day window or full source pagination. No admission, source-policy change, publication acceptance or scheduled-run proof follows from this review.

Companion evidence: `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/q4-initial-data-diagnostic-independent-review-2026-10-25.json`.
