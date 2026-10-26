# Actual controlled observer-failure delivery

PASS. Manual run `40276665629` used temporary fault commit `d3a646515b65187731a37027049769cfd6356fbc`, directly after clean preview `f514cfe017a60b3dea50bc4da37980f4b892f657`. Its only difference is the seven-line intentionally failing watchdog test; the workflow and production code remain exact.

The hosted runner completed 56 tests in 1.560 seconds, with exactly the one intended failure and 55 passes. The trusted probe step was skipped. The checkout-independent reporter succeeded and acknowledged opening distinct observer issue 15: https://github.com/jessepike/sec-market/issues/15 . A direct issue read confirms its exact title, open state, Jesse assignment, the exact fault run URL and failed-test/skipped-probe stages. The actual reporter receipt says observerRecovered=false and healthIssueChanged=false.

The entire parsed issue 10 object, including body, state and updated_at, is identical to root's full pre-fault snapshot `e22512c5e1945e525a21934ac2e00ab6d103c38b8bce1b01ef6bbbef1bb3ea32`. Its last update remains `2026-10-26T05:50:35Z`. The fault reporter did not alter the health issue. The existing legacy job succeeded separately; root confirmed that no legacy Site freshness issue was open before the drill.

This is actual failure delivery through GitHub, with no native-schedule, source/model, publication or phone/email credit. Clean-preview recovery and temporary-branch cleanup remain separate required actions. Full raw logs and issue metadata remain VM-only; bounded evidence and hashes are indexed here. No dispatch, Git ref or issue mutation was performed by the audit.
