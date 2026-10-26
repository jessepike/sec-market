# Runtime canary timeout repair

## Authority and exact failure

Root authorized a narrow operational repair at clean finish commit `34e55f78275925f4e07070a5bae510fcf23e4ebc`. Only `.github/workflows/subscription-runtime-canary.yml` and this repair's documents/receipts are owned. Tests, assertions, application/runtime code, credentials, source policies, state, all budgets and other workflows must remain byte-exact. Root owns any commit, push, main selection or retry.

Actual preview canary `40270223152`, job `121401232257`, was cancelled. GitHub's failure annotation says, "The job has exceeded the maximum execution time of 10m0s". The job ran from `04:39:57Z` to `04:50:15Z`; its full operational test step ran from `04:40:09Z` to `04:50:11Z` and was interrupted. Archive verification was skipped and the artifact upload found no receipt. There were zero artifacts. The bounded actual log contains no assertion-failure banner before interruption. It does not prove the remaining tests would have passed.

The auditor sealed seven safe payloads under `/var/tmp/smp-oct26-canary-40270223152/`, index SHA-256 `defb9c4884050db81194ec385d4a9994f1b2256c080bcb805932e92123e3c2a0`. The raw 140,561-byte job log remains VM-only, SHA-256 `372a1d51e619e6d26c78a2e79442fab290b11d5797e494409a1d9ab861dd67be`.

## Cause and chosen change

The canary wraps the full operational suite, GitHub archive restore/integrity verification and receipt upload in one 10-minute job limit. The accepted 1,015-test combined suite took 528.113 seconds with retained archives present and 654.190 seconds in fresh portable archive absence. The portable run alone exceeds 600 seconds. The hosted failure is the corresponding whole-job deadline counterexample. Expensive authenticated proof replay is expected test work; the evidence does not identify a stalled transport, assertion regression or new runtime loop.

Change only the canary job's `timeout-minutes` from `10` to `20`. Keep its exact full unittest discovery command and every step unchanged. Twenty minutes is a bounded allowance above the observed 10 minute 54 second portable suite, leaving about nine minutes for runner variation, checkout/setup, archive verification and receipt upload. This is an operational allowance, not a claim that a subsequent hosted run is guaranteed to finish. The next actual canary must complete all tests, archive verification and receipt upload before it supplies successful evidence.

Do not cache or bypass replay, reduce the suite, skip tests, relax assertions, change source/gate/model budgets, change environment or credentials, or add paid fallback. No workflow dispatch or retry belongs to this unit.

## Related native timing assessment

The native collector job remains 35 minutes. It runs the same guard suite before its bounded collection, whose explicit maximum remains 1,200 seconds. At the observed 654.190-second portable guard duration, those two phases consume about 30 minutes 54 seconds, leaving about four minutes for installation, archive restore/checkpoint, receipt upload and cleanup. The guard suite occurs before collection startup; it does not reduce or extend the collector's internal 20-minute deadline. This margin is finite and must be judged against the next actual native timings. This repair does not establish that worst-case setup plus full collection always fits.

The native publisher remains 55 minutes. It runs the same guards before restoration and a separate independent gate wait bounded at 35 minutes in release.py. Using the observed portable guard duration plus the full gate wait leaves about nine minutes for setup, archive work, promotion/verification and cleanup. The independent gate job itself remains 35 minutes and its gate process phase timeout remains unchanged. A native collector completion callback still requires the genuine successful scheduled main collection and existing concurrency/authority checks. Canary success supplies no native collection, gate or publication credit.

Other manual proof workflows also share the full suite: publisher probe has a 15-minute job limit, account bootstrap 20 minutes and rollback drill 25 minutes. The 15-minute proof workflow has less headroom than the proposed canary. No current timeout counterexample for those workflows is supplied here; their timeouts remain unchanged under this narrow scope. The account probe does not run this full suite. Native collector/publisher are distinct jobs and do not inherit the canary's 20-minute limit.

## Verification and handback

Before mutation, pin the original workflow and all tracked files. Verify the final workflow differs by exactly the one intended numeric timeout token and that the unittest command, step graph, archive command, permissions, credential expressions, concurrency, artifact retention and all other workflows/tests remain exact. Run the existing focused runtime-canary tests in OrbStack with network denied; no archived-source requests occur. Use the already sealed full 1,015-test present/absence receipts for the unchanged suite, without claiming a fresh whole-suite run.

Retain the safe actual failure payloads, source/patch pins, focused command/output, prior suite timing pins and a complete before/after protection receipt. Obtain independent review of the cause, bounded allowance, preserved guards and native timing assessment. Supply a sealed report/index for root acceptance. No new build/render is required because no web code or data changes.
