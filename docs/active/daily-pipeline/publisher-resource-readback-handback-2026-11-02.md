# Native publisher resource read-back handback

The local change is ready for independent review at source
`a0b50d4c8af4128028952a8d5bc63d920e9cd08f`, on the already reviewed combined candidate.
The governing specification was committed before implementation. Only
`ops/ci/publisher_probe.py` and `ops/ci/test_publisher_probe.py` changed among existing code.

The existing fixed-project GET now retains three typed scalar values from native resourceConfig:
`buildMachineType`, `buildMachineSelection`, `elasticConcurrencyEnabled`. A missing or non-object
resourceConfig produces three nulls. Missing/wrongly typed individual fields remain null while
valid siblings survive. The entire native object is never retained. These are observational
fields; null does not pass the separate Basic/fixed/no-elastic staging preflight.

Nine focused cases passed in OrbStack with zero skips, including existing auth-file permission,
credential/environment isolation, fixed GET interface, cleanup and error-redaction checks.
The added cases exercise valid Basic/fixed/false, absent/non-object resource shapes, malformed
individual fields and unrelated native fields that must never leak into a receipt. No real
Vercel call occurred. No full-suite/npm repeat was needed for this bounded internal receipt
change; prior 1,090 operational and full npm results remain their own frozen evidence.

All 3,581 other preexisting tracked paths match the before Git tree. The UI, full-page/fold
rendered comparison, K source/baseline, three-source guard, staging adapter, branch configuration,
workflow and secret lines remain exact. Evidence is under
`docs/active/daily-pipeline/receipts/publisher-resource-readback-2026-11-02/`.

## Route and security scope

AGENTS permits short-lived work branches from Preview. This is such a branch; no rule was
changed to allow it. The existing hook continues to protect main. The existing manual probe
requires this exact private repository, uses the already scoped token with temporary private
file-backed authentication, runs one fixed project/team GET, and retains only the existing
receipt plus the three selected scalar fields. The bounded Security Review input/leakage lens
found no new CLI input, endpoint selection, auth exposure or permission change. This is not a
claim of a new project-wide security audit.

The stage step still requires the head_commit message marker. A workflow_dispatch event has no
head_commit, so the stage condition is false for that manual route. No workflow or event input
was added. The stage code cannot be reached by that dispatch under the retained condition.
This conclusion is the source/event-shape assessment; an actual skipped hosted step is still
necessary as the native execution receipt. It does not authorize a dispatch here.

A read-only native GitHub rules query for `codex/coverage-release-20261102` returned HTTP 403,
with the feature message that GitHub Pro or a public repository is needed to enable that rules
endpoint. The exact response/error is retained. It does not establish a branch-push prohibition
or approval. No plan upgrade or repository visibility change is proposed. No explicit local
rule prohibits the prepared short-lived branch route; no unknown remote rule is bypassed.

## Held next actions and financial boundary

A later operator may, after independent exact-source review and a fresh financial-risk decision,
push only the short-lived branch and inspect native Git activity for deployment suppression.
The reviewed deploymentEnabled map is `**: false`, `preview: true`. Native Git suppression is
still unproved; the source map is not a zero-charge receipt. A historical ignored deployment
had positive native billing, so an ignored build must not be budgeted as free. Any unexpected
provider deployment/build must be retained as an actual/unknown liability and stop the route.

The existing read-only manual workflow also installs its pinned CLI and runs the full guard
suite on a GitHub-hosted Ubuntu runner. It can consume included/billable runner minutes even
when Vercel staging is skipped. Check current shared runner allowance and all-writer/Pacific-day
cost bounds before authorizing that action. Historical usage and the local focused tests grant
no new spending allowance. The paid managed-runtime trial stays stopped.

Only a genuine successful native project GET can supply current resource values. Only native
branch activity can prove no competing deployment was created. Neither result has been earned.
There was no push, dispatch, provider authentication/permission/project mutation, purchase,
source capture, archive write, paid build, main movement or production activation. The parent
owns the independent review, live risk decision and any later operator action. This handback
records this worktree's current state without editing its separately owned status surface.
