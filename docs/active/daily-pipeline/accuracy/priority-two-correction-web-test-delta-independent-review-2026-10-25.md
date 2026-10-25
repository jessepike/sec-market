# Priority corrections: separate web-test fixture delta review

PASS. The three test files now use the existing hash-pinned historical-six request/stamp fixtures for their historical mechanics. No assertion was weakened and no skip was added. The current eight-group policy remains independently checked by the pending-integration tests and runtime validators.

Independent execution used the active-eight isolated application and the project tsx runner with `tsconfig.app.json`: all 43 selected tests passed, with no skips. The worker final full npm log was authenticated and losslessly decompressed: 379 data tests, 115 pipeline tests, all 80 SEC claims, and 42 browser tests passed, with one existing browser fixture skip; lint has no error and one existing warning.

The requests fixture remains raw SHA-256 `9c9fbe0d3d40ece11e1407ce9460086c732f62da88d3b0f220ab9d6f8757da00`; the historical J stamp remains `365058911a182610cde401307fb30cc1855930b7940969440a618441cbbef9b2`. Both are explicitly checked before use. Only the three named test files change. All 31 prior worker handback paths and the original independent review MD/JSON remain byte-exact. All 2,662 base Git blobs were checked again; differences are confined to the original reviewed overlay and these three tests. No runtime, request, stamp, baseline or accepted view changed.

The actual initial npm failure remains retained: ten historical-fixture failures stopped its data stage. A separate independent ad-hoc invocation omitted the project JSX configuration and failed one React render; the corrected project runner passed without a code change. Neither failed run is recast as passing.

The companion JSON records exact new test pins, selected command/results, full npm raw/gzip pins, protected old handoffs and limits. The separate receipt folder retains the diff, successful selected log and independent driver failure. No source/model request, real admission, archive write or checkout write occurred. Root controls copying this test-only delta.
