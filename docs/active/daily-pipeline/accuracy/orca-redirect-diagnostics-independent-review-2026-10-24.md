# Independent review of Orca redirect diagnostics

The reviewed change has no blocking finding. I recommend the narrow diagnostic change for the approved capped Orca follow-up. This review establishes no new actual source response, source qualification, normal intake, semantic admission or publication credit.

## Stable reviewed code

Host and OrbStack copies matched the following final hashes:

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/fetcher.py` | `dbf25815953f1da8aac763d7b237161910f154ec8bac056a74cf5a2a547e8104` |
| `ops/ci/collect.py` | `097187b7dc1e03165eabb51d935fd6c678b84b27a733958951cb2db97222e540` |
| `ops/ci/test_orca_redirect_diagnostics.py` | `16bf3ca6b5b70855a35a802624d02d58976bcda43fcc7694bf090155499e2d72` |

The collector diff is one constructor keyword: `redirect_diagnostics=True` only within the exact `bounded_orca_qualification` branch. The generic source-probe constructor retains its default arguments. The original `ContractRedirect` implementation, URL safety checks, normal handler selection, stdlib redirect limits, network policy, retries and conditional-request behavior remain intact.

The opt-in handler records observed redirect responses and proposed targets before delegating to the existing implementation. A proposed target does not assert that transport occurred. Metadata is limited to response/error URLs, status, first raw Location, proposed URL, fixed categories and truncation fields. It retains no unrelated headers or bodies. The event list is bounded at 64, with each text value bounded at 4,096 characters. An unsafe target remains prohibited; diagnostic failure metadata cannot supply a missing response body, final URL or traversal terminal.

## Independent checks

All execution occurred in OrbStack with mocked HTTP responses and blocked socket connections. All 14 installed tests passed:

```sh
PYTHONPATH=ops/ci:web/scripts/pipeline PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPYCACHEPREFIX=/tmp/smp-orca-redirect-installed-review-cache \
  python3 -m unittest test_orca_redirect_diagnostics -v
```

These tests cover ordinary success/error/304 output, retries, relative Location versus proposed URL, missing and empty Location, URI fallback, malformed or unsafe targets, denied/private destinations, loop limits, metadata bounds, network failure after a proposal, prior-versus-current 304 metadata, exact boolean opt-in, Orca-only routing and unchanged incomplete-evidence replay.

Five further independent checks used the original fetcher and the draft fetcher against the same mocked response sequences:

| Check | Result |
|---|---|
| URI fallback followed by success. | Default output and both transport calls exactly matched the original fetcher. |
| Empty Location with a URI header. | Default output and five loop-limited transport calls exactly matched the original fetcher. Empty Location stayed distinct from missing Location. |
| Unsupported `file:` target. | Default output and the single transport call exactly matched the original fetcher. |
| Retry, redirect, another retry, then success. | Default output and four transport calls exactly matched the original fetcher. |
| A current redirect followed by 304 with retained prior redirect metadata. | Only the current redirect event was retained. The original observation reuse reference remained, and the terminal 304 was recorded without copying old redirect events into current evidence. |

The independent extra-check script is `/tmp/smp-orca-redirect-independent-extra.py` in the dev VM. The 11 executable draft tests also passed before installation; they are the fetcher subset of the final 14 tests, rather than additional distinct coverage.

## Actual original report replay

The original manual run `40126516584` remains incomplete. Its 27 charged requests produced 26 successful index pages and 90 raw leads; page 27 returned HTTP 302 without retained destination or body. This change does not reinterpret that old observation or explain its redirect destination.

I independently replayed its exact immutable report with the diagnostic draft fetcher imported, using a read-only MemoryStore over:

`/var/tmp/smp-orca-40126516584-20261024/extracted/jessepike-sec-market-3dcd8798c2e5261ded4dd8afea348168ce2224af`

Every one of the archive's 41,005 manifest entries passed hash and size checks. The manifest digest is `34c98107d3b35af79da17fbce9874e043bb18c326b9b34083904d8d91e0e934e`. Replay preserved the exact diagnostic digest `e5e4a89f6f234ad8bc19e05e41171c22ddc012434dd46ee3b379e577f1cb6c55`, all 90 leads and all 27 charges. Evidence remained incomplete. There were zero MemoryStore writes and zero network, subprocess or filesystem-write guard attempts.

The archive's 41,009 files and 1,906 directories retained identical before/after seals:

| Seal | SHA-256 |
|---|---|
| Content inventory | `eab114a22d66d2f8b5f5b0baa51e27092f391da999dcef331f7b0a106b86e405` |
| File modification times | `6cf088ea5f5d35a3af4c3e0d4043010102e5651e7bc35d0dc8600447cef48661` |
| Directory modification times | `52d929d497e5266f25e7b5b7686cb87c482e85ddd022fbaceb2a6a08a43fabf6` |

The independent replay script and output are `/tmp/smp-orca-redirect-original-replay.py` and `/tmp/smp-orca-redirect-original-replay.json` in the dev VM. The implementation operator separately retained its final-pin replay receipt at `docs/active/daily-pipeline/accuracy/orca-redirect-diagnostics-original-replay-2026-10-24.json`, SHA-256 `c8456def3dbb47792e0f90788659a2222f9893244df3d9bb42c8373c9ded28c7`. That operator's broader suite results are separate from this independent review's 14 tests and five extra checks.

## Plan state and remaining actual evidence

This independent review and original-report replay ran while the operational plan was the exact disabled plan, raw SHA-256 `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4`. Historical replay loaded the immutable original operational plan, SHA-256 `93257fbffe11598ffff5ee7b890fdd0e992d59d4b276d0ad09aa8ddfe56f7d98`, without consulting a newly enabled live plan.

After those checks, the parent locally restored that exact original operational plan only for the already approved single capped follow-up after code CI and promotion. This later local plan state supplies no fresh response or qualification proof. Actual Actions, artifact, archive, charge and response authentication still has to follow the real run. The current H policy, candidate registration, source authorities, seed package and model/document allowances are unchanged.

Only this new review file was written in the repository for this review. No runtime implementation or source evidence was edited by the reviewer.

The parent removed one trailing blank line from the test file after the reviewed implementation. The original test SHA-256 was `ba4c186b776bed8ed83c33fb2bd3e17460932322dbc3df1b697e718ed2328d2e`; the final formatting-only SHA-256 is `16bf3ca6b5b70855a35a802624d02d58976bcda43fcc7694bf090155499e2d72`. The 14 focused tests were rerun successfully after normalization. Runtime code is unchanged.
