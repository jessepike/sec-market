# Private hosting canary runner reduction, November 2, 2026

The final proposal runs seven fictional auth tests before the unchanged native archive canary
and uses the conservative pipeline-wide path filter. The final source diff restores the original
runtime test module completely. The superseding specification and results are at the end;
the initial specification and evidence below remain as implementation history.

## Specification before implementation

Base: origin/preview `0fa0ed39a899539dee680ae572a56eb21d2f47e0`.
Scope: the private hosting canary workflow, its existing focused tests, and this evidence folder.
The parent delivery owns the final status update, full combined CI check and release path.
No push, dispatch, production build, credential use or provider change is authorized here.

Replace the canary's duplicate full operational suite with two explicit unittest discovery
commands for `test_auth_store.py` and `test_runtime_canary.py`. Preserve the exact full-suite
step named `Verify all operational guards for exact code` in web CI, including its command.
Reuse of that full-suite receipt and its fallback remain unchanged.

Restrict canary push paths to its runtime dependency closure, fictional-auth helper and focused
tests, and its own workflow. Preserve manual dispatch, private repository condition,
read-only permissions, native archive restore/integrity verification, and bounded receipt upload.
There is no schedule change and no change to collection, alerts, publication or source guards.

## Dependency inspection and plan

`runtime_canary.py` imports archive, contracts, storage and coverage_summary. Archive imports
contracts and storage; storage and coverage_summary import contracts. Runtime reads
`contracts/market.json`; the archive ref and remote are bound in Python code.
The initial top-level inspection missed conditional imports inside contract validation. The
recursive dependency check found Q4 and regulatory validators and their import closure, including
separation, discovery and documents. All are retained in the trigger list. No additional bound
configuration is read on the canary validation path; source-review files referenced by other
functions in these modules are not read by contract validation.
`auth_store.py` and its focused test use standard library imports only.

The existing runtime canary tests import fixtures from two unrelated test modules, which in
turn import collection and discovery code. Move those two small fictional fixtures into the
existing focused test module so its dependency closure matches this job's scope. The existing
Fetcher.fetch prohibition remains unchanged, and fetcher.py remains in the trigger list.
The real archive restore and integrity checks remain exercised. Both fixture functions retain
identical syntax trees and values; NOW and MEASURE remain the same.

Push paths will explicitly list these five operational files: runtime_canary.py, auth_store.py,
coverage_summary.py, test_auth_store.py, and test_runtime_canary.py. They will also list archive.py,
contracts.py, storage.py, fetcher.py, the 12 transitive pipeline dependencies, contracts/market.json,
and the workflow itself. The resulting 23 explicit paths cover the full static local import
closure, including conditional imports. Collection, correction and unrelated operational changes
remain covered by full web CI without repeating native archive restoration. Modules shared with
contract validation still trigger the native canary. Auth persistence, archive integrity and
contract changes still run it.

## Verification and fallback

Run both focused suites with existing dependencies in OrbStack. Run exact-code CI proof tests,
parse the actual workflow YAML if existing PyYAML is available, and test the actual push filters
against the dependency closure and unrelated changes. Inspect that the full web guard step,
private execution step, permissions and receipt upload remain intact. Retain command results
and wall-clock times locally. Do not run market requests or a model worker.

A failed focused test or a missing trigger dependency blocks handoff. The fallback is restoring
the old broad paths and duplicate full-suite step through the normal reviewed release route.
Hosted savings and new native restore time require the next actual hosted run. Local timings
cannot establish those results. This event-only change saves development-push work and does not
reduce the existing 99-to-59 Linux-minute daily forecast further.

The paid managed-runtime trial remains stopped. No service or spending change is included;
the five-cent full-day condition remains. Personal platform standards read at
`ff32b0055293e4fb3bce550bade4652cc2ee1aa3`; existing T2 sensitivity and runtime exceptions stand.

## Results

The OrbStack run passed 7 fictional-auth tests, 18 runtime-canary tests (the original 16 plus two
workflow boundary checks), and 13 exact-code guard reuse/fallback tests. Existing PyYAML 6.0.1
parsed the workflow and checked the preview-only push, manual dispatch, no schedule, private
repository restriction, read-only permission and always-uploaded 14-day receipt. Actionlint is
not installed; nothing was installed. The full web workflow is byte-identical to the base.
All original canary methods and assertions are unchanged except removal of the now-local fixture
import. The parent delivery will run the full operational suite once for its combined change.

The two focused local commands took 0.038757 and 0.161913 seconds, 0.200670 seconds combined.
The guard reuse/fallback suite took 0.036463 seconds. These are local process wall times.
The retained real hosted canary run 41485463964 spent 311 seconds in its old duplicate full-suite
step, 62 seconds in native archive verification and 409 seconds in the job overall. That receipt
is copied unchanged into this evidence folder. Local and hosted timings are different measures;
the next real hosted run must establish the new duration and savings.

The actual dependency-filter check initially failed on the missing conditional imports and
blocked handoff until all 12 paths were included. Final results and preservation checks are in
`receipts/canary-runner-reduction-2026-11-02/`. This change is local and unpushed. The sensitive
workflow change carries `Owner-Review: required`; parent delivery owns final review and release.

## Superseding scope after parent review

The initial implementation and results above are retained as history of commit `fe691523`.
The following final specification supersedes the two-suite canary step, copied fixtures, and
23-path import-closure test. This amendment was specified before its validation and commit.

The final workflow runs only the seven fictional `test_auth_store.py` cases before the unchanged
actual native private archive canary. Full web CI still executes all operational tests once,
including the original 16 runtime-canary cases. Restore `test_runtime_canary.py` byte-for-byte
from base `0fa0ed39`; no copied fixture or AST traversal remains in the final source diff.

Use eight conservative push patterns: the canary runtime, auth helper, coverage summary, the two
focused test files, `web/scripts/pipeline/**`, `contracts/market.json`, and the workflow itself.
The whole pipeline pattern covers current and future conditional validator imports without a
maintained import list. This intentionally permits native archive checks on any pipeline edit.
Unrelated operational, collection and correction-test edits, plus website UI edits, skip this
native canary while retaining full web CI. Auth and archive changes remain covered.

Revalidate seven auth tests, the original 16 canary tests, 13 exact-code CI guard tests, actual YAML
and trigger boundaries. Preserve all initial evidence files. Save amendment results separately.
The expected saving is removal of the old 311-second duplicate hosted full suite plus avoided
native canary runs on unrelated ops edits. Actual new hosted timings remain unproved, and the
existing daily forecast does not change. No service, spend, schedule or alert changes are included.

Final amendment checks passed in OrbStack: seven auth cases in 0.034270 seconds, the original 16
runtime cases in 0.104934 seconds and 13 exact-code guard cases in 0.034728 seconds. Existing
PyYAML parsed the real workflow. Positive and negative path checks passed, including future
pipeline validators, current archive/auth files and excluded unrelated ops/UI edits. The native
canary and receipt steps are identical to base. Both the runtime test module and web workflow are
byte-identical to base. Final results are saved under the original evidence folder's
`final-amendment/` directory; the earlier 18-case results remain historical evidence only.
