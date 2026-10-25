# Unexpected HTTP status diagnostics: independent review

Result: clean. No actionable correctness, security or regression findings in the reviewed bytes.
I recommend retaining this narrow patch on preview pending the assigned actual scheduled-H and
public acceptance. This review supplies no promotion or fresh source-qualification evidence.

## Scope and findings

Reviewed the specification, the two runtime diffs, the new focused test module and the one
authorized existing schema-1 constructor assertion change. The default-off strict boolean adds
one failed-observation return after existing final-host validation and the complete bounded read.
Default success and unexpected-status exception/body-write behavior remain unchanged. Existing
HTTPError, 304, rate limiting, retry and redirect handling is unchanged. Only the validated
schema-1 leased diagnostic route enables the option; schema 2, Orca and ordinary collection keep
their existing constructors.

The actual diagnostic loop archives failed observations and stops before discovery parsing.
Successful qualification proof still requires fetched status and HTTP 200. Failed retained bodies
receive zero source-check, qualification, semantic, model or publication credit. No policy,
adapter binding, qualification-origin authority or original proof interpretation changed.

The former Check Point numeric HTTP status remains **UNKNOWN**. Fictional 206 tests and a future
captured failed status cannot repair or supplement that past observation.

## Independently executed checks

All Python execution ran in OrbStack dev. Transport tests used fictional HTTPS responses and
temporary stores, with socket transport forbidden. Host and VM hashes matched before tests.

- All 13 new focused tests passed, including the real leased diagnostic loop, schema selection,
  failed proof rejection, bounded retention, strict boolean checks and default transport parity.
- All 26 qualification-origin tests and all 19 HTML qualification-seed tests passed.
- Twenty additional temporary adversarial scenarios passed. Opened 202/203/205/207/226/299
  responses preserved default exceptions and retained exact failed bodies only when enabled,
  including the exact size boundary. HTTPError 300/301/302/307/308/401/404/418/500/502/504 paths
  preserved response/read/write/retry parity. Unsafe final protocol, credentials and port rejected
  before reads or retention.
- The actual frozen archive's three current-policy qualification origins replayed through a
  separate read-only store adapter, with no LocalStore construction. The policy remains
  `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`.
  Delinea retained 290 inventory items, Ping 242 and Sonatype 205. All retain inventory-only
  authority and original completion time `2026-10-24T17:38:02.691908Z`.
- That actual replay ran under write, network and subprocess-denying audit hooks. All 41,249
  frozen archive files retained identical SHA-256, size and modification time; there were zero
  guarded operation attempts. The archive was
  `/var/tmp/smp-seven-source-40131875060-20261024/extracted` in the VM.
- The reviewed runtime/existing-test diff passes `git diff --check`.

## Reviewed hashes

Paths are relative to `/Users/jessepike/code/projects/sec-market-finish-20261022`.

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/fetcher.py` | `82084e87bb41687fec8ebfc969cf0a37294e04312a47a27993f5c359a585adce` |
| `ops/ci/collect.py` | `70823c921fb849fa814b7a26f39044448896638b1eae9961a6c0d6b684bbb5fc` |
| `ops/ci/test_unexpected_http_status_diagnostics.py` | `14b99ea73de9f43b1e9ed9b0ff22497f31ca8239655495f2a46b4a757bd84bb9` |
| `ops/ci/test_orca_redirect_diagnostics.py` | `10d9d49bb46fcc90c0c5ab109f81961ee0b561557ca0ad869181cda9f889fc9d` |

The operational plan remains disabled schema 2, hash
`ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4`.
No code, contract, plan, archive, state, budget, dispatch, Git reference or remote changed during
this review. This report is the sole repository write. The root agent owns full application,
render and later release checks; main remains assigned to frozen `6d5e87fe` acceptance.

Review writes stop here.
