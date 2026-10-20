# Validation receipts

Validated in the Codex cloud checkout on 2026-10-20 UTC (2026-10-19 PDT), using Node 22.23.3,
Python 3.12 and system Chromium 154. No live pipeline cutover or model-backed production collection
was performed. Test doubles are restricted to unavailable network/model/storage/deployment boundaries.

| Check | Result | What it establishes |
|---|---|---|
| `npm run lint` | Pass | Existing JS/TS lint checks |
| `npm run test:data` | 244 passed, 0 failed/skipped | Existing application tests plus real SEC bridge/verifier tests and archive/watchdog handler tests |
| `npm run test:pipeline` | 63 passed, 0 failed/skipped | Real Python planning, store, execution, validation, receipt/health and release-interface logic |
| `npm run build` | Pass; 80/80 SEC claims, zero blockers/drift | Existing application's committed-input certification and full distribution build |
| `npm run test:e2e -- --config=/workspace/.cloud-setup/playwright.config.ts` | 30 passed, 0 failed/skipped | Existing desktop/phone functional/browser assertions on the built application |
| Contract validation/report | Pass; 74 suppliers, 287 bindings, 557 required tasks | Actual baseline inventory preserved, including 270 missing bindings and 47 candidates |
| Workflow syntax | Both changed workflows parsed | YAML syntax, not proof of a scheduled run or GitHub validation |
| Visual comparison | 0 changed pixels at 1440 and 390 | Production and candidate root page full-height images have identical dimensions and pixels |
| `git diff --check` | Pass | No whitespace errors |

The full application validation sequence first included 60 Python cases. Three subsequent Python
cases check UTC-equivalent run identities, rejection of health receipts from another policy,
and correct classification of distributor/investor discovery sites;
the full Python suite then passed 63 cases. No application rendering changed after the browser run.

Screenshots were captured from production and the candidate's actual built-site server, with fonts
loaded and charts painted. Full-page heights: 8,236px at 1440; 7,575px at 390. First-screen images were
also visually inspected. There are no visible page changes. Cloud-only raw logs and images are in
`/workspace/sec-market-review-evidence/`; those local paths are not durable GitHub artifacts.

GitHub also ran the unmodified `npm test` successfully on code commit `c674fba`:
[run 39367373345](https://github.com/jessepike/sec-market/actions/runs/39367373345).
Vercel reported that feature preview ready. Direct preview receipt inspection received proxy
CONNECT 403, so its deployed contents are not independently acknowledged from this cloud session.
Subsequent changes only record these operational receipts in documentation.

## Failure and recovery coverage

- Missing/duplicate task receipts, changed policy/denominator, missing discovery registration,
  blocked source, pagination limit and absent/stale/future observations cannot pass reconciliation.
- Exact source text, entity, amount/currency, date, numeric qualifiers, ARR/revenue and event status
  are checked. Unsupported judgments, invented quotes and semantic reviewer disagreement are held.
- Extraction and review bind exact evidence/policy hashes. Stored reviews are rechecked. Empty
  extraction cannot hide a clear business signal.
- Repeated runs reuse document validation; duplicate/concurrent sources do not create duplicate
  market events. Partial failed tasks cannot publish their already-archived facts; a successful
  retry retains those facts as eligible.
- Model budgets survive restart. API-authenticated CLI is rejected; infrastructure/API credential
  variables are stripped from the subscription subprocess. This tests adapter arguments/environment,
  not live model/tool isolation or provider capacity.
- Evidence is immutable/hash-checked; path escape and stale CAS are rejected. Kernel locks prevent
  concurrent local publishers and release after an actual worker-process crash. A portable backup
  is restored/verified independently of the original workspace, with an externally retained root hash.
- Production cutover defaults off. Wrong deployed data/code receipts fail; failed live probes AND
  ambiguous promotion timeouts invoke rollback and preserve the last good head. A rollback must
  acknowledge the expected previous release. Deployment behavior uses an adapter double.
- GitHub provenance checks read actual-run/artifact-shaped responses and reject changed workflow,
  branch or receipt content. They were tested with a subprocess double; no real release-gate workflow
  artifact exists yet.
- R2 handler roles, immutable collisions, hash checks, CAS races and denial of deletion are tested
  against an in-memory service double. Actual R2 consistency/permissions/retention are untested.
- Outside watchdog rejects HTTP 200 with incomplete coverage, stale receipts, reduced denominator,
  missing gaps list and old deployed code/data. Delivery failures are retried without falsely marking
  an alert delivered; repetitions are deduplicated and recovery is reported. No real message was sent.

## Live evidence remains outstanding

Successful real subscription inference; complete source discovery and filing/PDF processing;
remote archive/restore and credential isolation; every displayed claim mapped to a validated
snapshot; trusted release-gate workflow; immutable Vercel stage/promote/probe/rollback;
public operational coverage receipts; real alert delivery; missed-schedule detection; unattended
multi-day burn-in. None is established by these local tests. See the activation gates in README.md.
