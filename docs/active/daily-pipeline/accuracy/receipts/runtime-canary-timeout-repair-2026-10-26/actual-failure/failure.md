# Actual preview canary timeout

Run `40270223152`, preview push at exact candidate `34e55f78275925f4e07070a5bae510fcf23e4ebc`, ended cancelled. GitHub explicitly records: “The job has exceeded the maximum execution time of 10m0s”.

The job ran from `2026-10-26T04:39:57Z` to `04:50:15Z`. The full guard-test step ran from `04:40:09Z` to `04:50:11Z` before cancellation. Its last completed tests were PR Newswire primary-capture cases. No test assertion-failure banner was recorded before the interruption, but the suite did not finish.

The subsequent private-runner archive check was skipped. Receipt upload failed because `/home/runner/work/_temp/smp-runtime-canary.json` does not exist. GitHub reports zero artifacts. No artifact digest, successful runtime receipt, or current-eight-group canary replay can be authenticated from this run. Existing eight-group actual archive evidence remains separately valid.

The canary's archive-integrity code did not execute and supplies no source/model, semantic, coverage, publication or remote-gate credit. The timeout does not spend or reset a publication gate. The auditor issued no source/model request, dispatch, real-state write, finish write or reservation.

The raw 140,561-byte job log remains VM-only in this namespace, SHA-256 `372a1d51e619e6d26c78a2e79442fab290b11d5797e494409a1d9ab861dd67be`. Safe bounded evidence is indexed separately. Root owns any retry or promotion; the assigned worker owns the narrow canary runtime repair.
