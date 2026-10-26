# Runtime canary timeout repair

The reviewable patch raises the private runtime canary job limit from 10 to 20 minutes. Every test, assertion, command, step, permission, environment expression and credential boundary remains unchanged. All 16 focused canary tests pass with socket network access denied. Root owns any later commit, push and hosted run.

## Actual failure and cause

Preview push run 40270223152 at commit `34e55f78275925f4e07070a5bae510fcf23e4ebc` was cancelled. GitHub explicitly reports: "The job has exceeded the maximum execution time of 10m0s". Its full operational guards were interrupted after approximately ten minutes; archive integrity verification was skipped and no artifact existed. No assertion-failure banner appears before interruption, but this supplies no result for uncompleted tests.

The existing complete 1,015-test suite took 528.113 seconds with frozen archives present and 654.190 seconds in fresh portable archive absence. The portable case already exceeds the entire 600-second canary limit before checkout/setup, archive verification and artifact upload. This supports a bounded job allowance for expected authenticated proof replay. The evidence identifies no new infinite loop or stalled source/model transport. Tests and replay behavior remain intact.

Twenty minutes leaves roughly nine minutes above the observed portable suite for hosted variation and the remaining archive/receipt phases. This is a justified allowance, not a successful hosted canary receipt or a guarantee about runner speed. A future accepted hosted run must still finish the full suite, archive verification and artifact upload. The raw job log remains VM-only. Only the auditor's seven safe payloads plus index are retained here, authenticated against index SHA-256 `defb9c4884050db81194ec385d4a9994f1b2256c080bcb805932e92123e3c2a0`.

## Preservation and verification

The original workflow SHA-256 is `1af4f54a8bd156fad88d32eea23257362ac725d6208da73a6044fc721c999717`; the patched workflow is `107ab41bbbd86174949068210274abcafd896860a801924e2e428a2834a99f2a`. Both are 1,676 bytes. Exact byte comparison permits only the one numeric timeout replacement. Parsed YAML is identical after normalizing that timeout. All 3,002 other tracked files remain byte-exact, including every test, source policy, runtime guard, source/gate/model budget, environment expression and other workflow. No suite reduction, new skip, replay cache or paid fallback was introduced.

The existing 16 runtime-canary tests pass in OrbStack with socket connections denied: 16 passed, zero failed, zero skipped. The unchanged suite's full 1,015-test present and fresh-absence receipts are linked and pinned in the timing receipt. No fresh full-suite or web-build claim is made for this workflow-only edit. The prior portable run's 61 explicit archive-only skips remain exactly as previously reviewed; this patch adds none. Git diff checking passes.

## Native timing assessment

The collector remains a 35-minute job with its original 1,200-second collection maximum. The observed portable guards plus that full internal maximum total about 30 minutes 54 seconds, leaving about four minutes for install, archive work, receipt upload and cleanup. Guard startup precedes the internal collection deadline. This remaining margin must be compared with the next actual native timings; it does not prove all worst-case phases always fit.

The publisher remains a 55-minute job with the existing 35-minute independent-gate wait. The observed portable guards plus that full wait leave about nine minutes for setup, archive work, promotion/verification and cleanup. The separate release gate still has its original 35-minute job limit. Native collector and publisher jobs do not inherit the canary's timeout. Genuine scheduled collector callback checks and writer concurrency remain unchanged. Canary completion gives no collection, gate or publication credit.

The publisher probe, account bootstrap and rollback proof jobs also run full guards and retain their existing 15-, 20- and 25-minute limits. The 15-minute proof job has tighter headroom than the repaired canary. No actual timeout counterexample for those jobs is supplied here, so they remain unchanged under this scope. Root can assess them separately from actual timings.

## Review and release boundary

Independent review is PASS. Its own checks confirm the exact one-token change, all 3,002 protected files, all 16 focused tests under socket denial, the prior full-suite timings and the finite native margins. The review is retained at `docs/active/daily-pipeline/accuracy/receipts/runtime-canary-timeout-repair-2026-10-26/independent/review.md`, SHA-256 `33404408461aab966e491b04bcbff258ac481d1f8b7294899bebba3ae14bb175`. The independent receipt index SHA-256 is `de33ed67f4739ee45f81f78f9700c7fafcaa3c2f1b33cae88d58bf55c2f02b19`. No hosted retry, workflow dispatch, source/model request, scarce gate reservation, credential change, real state write, commit or push was performed. Status and backlog remain owned by the actual audit worker. This patch changes no web data or layout and needs no new render.
