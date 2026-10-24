# Follow-up seven-target request plan implementation

## Scope

The reviewed `proposedNextSevenPlan` from `followup-seven-target-response-review-2026-10-24.json` replaces only `contracts/source-qualification-probes.json`. Its seven explicit targets are Ping pages 4–6, Delinea pages 2 and 5, and Sonatype pages 2 and 13. All proofs use the successful current-policy diagnostic `40066513321-1`, with an immutable reference to the original raw plan object. No target carries a historical-policy descriptor or nested raw-plan copy.

The market contract, source registrations, runtime, helpers and page presentation stay unchanged. Candidate sources remain unqualified. This plan grants zero intake, history, fact or semantic credit, preserves all 557 obligations and does not dispatch requests. Actual future execution must use the existing leased, budgeted diagnostic path.

## Validation

The committed plan is exactly the reviewed proposal, with seven targets and `maxRequests=7`. Its raw size is 11,388 bytes, down from 66,126 bytes. The previous plan remains available byte-for-byte through the original actual diagnostic's `rawPlanReference`; no archived proof was rewritten.

| Binding | SHA-256 |
|---|---|
| Current market policy | `79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60` |
| New plan raw bytes | `62385a674edf896b479dc4fb9330e3e269afcbdc0b6715dd44f9b18608adbf4f` |
| New plan canonical content | `42bf79e9e0a7f8907dc47b50836ec0e826c3a7ec81c028b9ba72e3da42d98356` |
| Prior plan raw object, 66,126 bytes | `6dc248c7a5fee6f96f872d97d87241a70de98bf7524298e9e7108951bbf6685d` |
| Prior plan canonical content | `eccc8cd58af1ebea1bd0679973ba8b0a0d3bf37cbe47ba06b94a084faeae825e` |
| Original diagnostic `ci/source-probe-runs/40066513321-1.json`, 277,064 bytes | `4ef4905070ed2043b093aad72990fe0d45a73f3682d0d3832e0ac2fa966e6ee2` |
| Unchanged validator `web/scripts/pipeline/onboarding.py` | `1f76daefe9b2d6a8e2a18b87f01b2742a0cc094ba18b47919d5c7b3ef98d874e` |

The new proof objects refer to `objects/6dc248c7a5fee6f96f872d97d87241a70de98bf7524298e9e7108951bbf6685d` rather than embedding raw predecessor plans. They bind the exact original record, row index, row hash, observation, body, timestamp and raw/canonical predecessor plan hashes. All seven literal links were independently recognized by the existing validator under the unchanged current policy. The three supporting original rows are Ping page 3, Delinea's news index and Sonatype's press index; the other four original diagnostic rows were also checked against their original URLs, observations, bodies, timestamps and plan entries.

Read-only replay used the complete authenticated archive:

`/var/tmp/smp-followup-probe-20261024/archive-20f8f6ee/jessepike-sec-market-20f8f6ee9b8113aea994d4251197221a6f64a005`

Its manifest hash is `962f925f60c19aa47c368c80c80d80ad6680b736223e2ceab76e071198586d37`. Every one of its 34,962 manifest entries passed hash and size verification. A before/after seal of all 34,966 files, including archive metadata, confirmed unchanged bytes, content hashes and modification times. The seal hashes the sorted relative-path map of `{sha256, bytes, mtimeNs}`; its canonical SHA-256 was `73cebbd1c68878a2b9ce38016dcbb0706aa7b019a435cae4ff3e6e38299a3f96` both times. The 16 referenced record/plan/observation/body objects were independently checked; their canonical key-to-reference inventory hash was `000cd0963e939b3eb34c52212c256ee94e37ab4a03a798b2ccfd0a4a891f6be7`.

Original explicit reservations remain charges 759 through 765, in original target order. The original complete diagnostic ledger remains 641 to 765 fetches, 80 model calls and 40 documents, under the same 5,500-fetch limit and original day/runtime context. The existing validator independently reconstructs all 124 original reservations and their exact consecutive charges. No reservation was made for this replay or implementation.

The replay ran in the OrbStack dev VM with an audit hook denying writes, filesystem mutations, network and subprocess creation. No prohibited operation was attempted. Focused tests then passed in the VM using fictional transport and temporary stores:

| Suite | Result |
|---|---|
| `ops/ci/test_source_qualification_probe.py` | 32 passed. |
| `ops/ci/test_leased_source_probe.py` | 22 passed. |
| `ops/ci/test_onboarding_budget.py` | 15 passed. |

Only the request plan and this implementation note changed within this assignment. There were no source requests, model calls, archive writes, actual state writes, workflow dispatches or commits. Independent review and root integration remain pending. Root owns commit, promotion, public checks and any actual workflow dispatch.
