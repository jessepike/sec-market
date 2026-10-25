# Q4 normal-intake CI portability review

PASS. The two-file test repair can proceed to hosted CI. No material finding remains.

The reviewed application is a fresh export of `f32946c11f7db4bf3b63fc0380780ab9bf5d6836` with only `ops/ci/test_q4_normal_intake.py` and `ops/ci/q4_intake_fixtures.py` overlaid. All 2,569 Git blob files were checked before and after tests. Only those two files differ; the other 81 original implementation pins match.

| Check | Independent result |
|---|---|
| Retained archive available | 14 passed, no skips |
| External archive absent; frozen reads denied | 12 passed; exactly two full-archive positives skipped; zero frozen-read attempts |
| Fixed committed package | All 55 payloads, 4,742,948 bytes authenticated in both modes |
| Corrupt payload, missing package, missing Q4 proof | Each rejected in both modes; none silently skipped |
| Worker full suite, authenticated logs | Present: 935 passed. Absent: 896 passed, 39 skipped, no errors/failures; 37 skips already existed and two belong to this repair |

The portable tests execute the 206/323 arrays and 529 inventory rows, exact H/J policy and provenance mutations, ordinary 200/304 transport, dates and unknown dates, future/quiet cases, and quota mechanics. The quota test uses a real Pipeline, SubscriptionAgent, GuardedRunner and isolated LocalStore with synthetic transport/login status and no model execution. Guard-only importer tests explicitly supply their checked preflight result. The two external positives retain complete unmocked validation and all six correction admissions when the archive is present.

The actual hosted setup failure `40197621420` remains a failure before the canary. The worker first local full-absence harness had three import errors; its failed log remains retained, and the corrected full rerun passed. Neither is recast as a successful initial run.

This accepts test portability. Hosted CI and actual J collection/acknowledgement remain separate evidence. It supplies no publication, coverage or freshness credit. No runtime, policy, seed payload, frozen archive, account allowance, or prior sealed review was changed. No source or model request was made.

The companion JSON records exact old/new SHA-256 pins, successful test names, attribution and limits. The receipt folder retains the independent driver, logs, fresh-export proof, Git blob inventory, diffs and post-test closure. Root controls copying and subsequent CI.
