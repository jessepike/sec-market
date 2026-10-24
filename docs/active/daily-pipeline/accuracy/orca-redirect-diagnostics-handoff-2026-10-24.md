# Orca-only redirect diagnostics

Status: implemented and tested locally. No actual request, dispatch, source activation or qualification credit occurred in the worker unit. At worker completion, the operational plan remained the exact disabled 173-byte `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4` plan. After independent review, the parent selected the exact original `93257fbffe11598ffff5ee7b890fdd0e992d59d4b276d0ad09aa8ddfe56f7d98` plan for one capped actual follow-up after CI and promotion. That plan is independently validated against the actual archived H contract and original endpoint proof, with zero state writes or network activity. Exact disabled `ad1…` restoration remains required after the run.

## What changed

Only the Orca source-probe constructor opts into redirect diagnostics. Its handler records an observed 30x response before delegating to the existing redirect implementation. The existing `ContractRedirect` class, `safe_url` checks, stdlib retry/loop limits, transport and reservation accounting remain unchanged. Default success, HTTP failure, retry, conditional and policy-exception behavior retain their existing outputs.

New observations may contain `redirectDiagnostics`: the bounded response URL/status, first raw `Location`, stdlib-derived proposed target, fixed category and relevant last `HTTPError` URL/status/`Location`. The maximum is 64 response entries and 4,096 Unicode characters per string, with explicit original character lengths and truncation flags. A proposed target records consideration by the redirect handler; it does not prove another request occurred. Metadata contains no other headers, cookies, authorization fields or body. A `URI` fallback is never relabeled as a `Location` value.

Opt-in unsafe or malformed redirects return failed observations with the actual observed status and metadata. They receive no relaxed follow behavior. The default path retains its existing exception behavior. Opt-in 304 results retain only current redirect observations; earlier metadata remains in the original immutable observation rather than being copied into newly observed redirect evidence. Failed or redirected responses remain incomplete under the unchanged Orca verifier. There is no new terminal rule or automatic retry after a terminal 302.

## Exact pins

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/fetcher.py` | `dbf25815953f1da8aac763d7b237161910f154ec8bac056a74cf5a2a547e8104` |
| `ops/ci/collect.py` | `097187b7dc1e03165eabb51d935fd6c678b84b27a733958951cb2db97222e540` |
| `ops/ci/test_orca_redirect_diagnostics.py` | `ba4c186b776bed8ed83c33fb2bd3e17460932322dbc3df1b697e718ed2328d2e` |
| `contracts/source-qualification-probes.json` (disabled at worker review) | `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4` |
| `contracts/market.json` (unchanged) | `24221c946781559c0ff3626e4e479c4647da915d0f2d7559ea88046982532c3c` |
| `web/scripts/pipeline/orca_qualification.py` (unchanged) | `731ee99cdc88bc4e69ef135f4c2e60f75248bc4db9bc389a3b5aa5773457935d` |
| `web/scripts/pipeline/onboarding.py` (unchanged) | `f15e008c081f0b9c48e53ab0b4c4388798d2bd54aaade904188b40305aa6bb69` |

Host and VM agree on these final source pins. The earlier immediate post-patch `bf67...` collector hash was stale mount propagation and is superseded by `097187b7...`. The collector diff is exactly one Orca constructor keyword. H remains canonical `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`; seed packages, activation authorities, registrations, baseline and workflow are untouched.

## Tests and actual retained replay

The 14 new focused tests use mocked urllib HTTPS responses and no actual transport. They cover exact default outputs, relative/empty/missing `Location`, URI fallback, unsupported scheme, malformed and unapproved/private destinations, default repeat/total limits, capped metadata, connection failure after a proposal, unchanged retry attempts, 304 history separation, strict Boolean opt-in, the exact Orca constructor route, unchanged generic constructor and absence of completion credit from metadata.

All 69 combined focused tests pass. The full operations suite passes all 780 tests with no skips, using a fresh Python cache path in OrbStack:

```sh
cd /mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/smp-orca-redirect-fullops \
PYTHONPATH=ops/ci:web/scripts/pipeline python3 -m unittest discover -s ops/ci -p 'test_*.py' -q
```

The full log is `/var/tmp/smp-orca-redirect-fullops-20261024.log` in the VM. `git diff --check` passes.

`docs/active/daily-pipeline/accuracy/orca-redirect-diagnostics-original-replay-2026-10-24.json` records a new pure replay of actual run `40126516584` against its original immutable plan and H contract. All 41,005 entries in acknowledged archive `3dcd8798c2e5261ded4dd8afea348168ce2224af` authenticate against manifest `34c98107d3b35af79da17fbce9874e043bb18c326b9b34083904d8d91e0e934e`. Full before/after content and modification-time seals match across all 41,009 files and 1,906 directories. The `MemoryStore` has zero mutations and the audit guard records zero attempted writes, subprocesses or network operations.

The exact original report is unchanged: 27 charged requests, 90 leads, `indexComplete=false`, `evidenceComplete=false`, `ORCA_RESPONSE_INCOMPLETE`. The original page-27 observation remains HTTP 302 with no body, final URL, `Location` or retrofitted diagnostics. This unit supplies no new evidence about that redirect's destination or terminal status.

Independent review by `correction_history` found no blocker, including five additional default/redirect/retry/304 counterchecks and original-report/seal replay. Its review is a separate parent-coordinated artifact.

## Next bounded action

I recommend one reviewed capped follow-up through the existing leased diagnostic route to observe the redirect metadata. The parent may restore the exact original `93257fbffe11598ffff5ee7b890fdd0e992d59d4b276d0ad09aa8ddfe56f7d98` plan atomically after review; this worker did not change it. Any actual result still needs authenticated run/artifact/archive/body/time/charge replay, and must keep zero model/document/gate use and zero qualification or coverage credit. Restore exact disabled `ad1...` after that diagnostic. A source activation remains separate from this transport observation repair.
