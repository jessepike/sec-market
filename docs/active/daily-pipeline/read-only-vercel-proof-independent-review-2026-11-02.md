# Independent review of the native read-only Vercel proof route

Reviewed source: `a0b50d4c8af4128028952a8d5bc63d920e9cd08f`.
Governing specification: `publisher-resource-readback-spec-2026-11-02.md`, committed before the
source change. The independent review owns only this document and performs no live action.

## Recommendation

Accept the bounded route described below. No blocking finding was found in the exact source,
manual event path or configured branch suppression. This acceptance is conditional on the
existing financial review, current shared Actions allowance and native suppression observation;
it does not authorize a paid Vercel deployment contingency.

Push only the short-lived `codex/coverage-release-20261102` branch with the reviewed code and
existing Git configuration. Do not move Preview, main or a tag. Retain native branch/SHA-scoped
activity observations and stop on an unexpected deployment; any existing emergency cancellation
must first establish the exact deployment/project/branch identity. Proceed with the existing
manual `subscription-publisher-probe.yml` on that same reviewed branch only after the native
observation supports the expected no-deployment route. Retain the actual resource receipt and
actual skipped-stage result. These are future operator actions, not actions performed by this
review.

## Trusted source and read boundary

The source commit changes only `publisher_probe.py` and its focused tests. The production
adapter, K source policy/baseline, UI, branch map, workflow, secret lines and permissions remain
unchanged by this commit. The combined predecessor has separate source and exact-artifact reviews;
this small addition does not introduce an unreviewed command, input URL or provider setting.

The probe's sole CLI operation is the existing GET of one pinned Vercel project, with a pinned
team query parameter. Project/account identity must match before a successful receipt is returned.
The added projection exposes only `buildMachineType`, `buildMachineSelection` and
`elasticConcurrencyEnabled` from resourceConfig. Their accepted Python types are exactly string,
string and boolean. Missing/non-object resource data and incorrectly typed individual fields
remain null; valid siblings remain visible. The full native resource object is never copied.
Unknown or null values remain observations and cannot satisfy the separate Basic staging guard.

Existing private-repository workflow checks, fresh auth directory validation, 0700 directory and
0600 auth file permissions, finally cleanup and bounded error classification remain unchanged.
The token is removed from the process environment and placed only in temporary CLI auth storage.
The child environment uses the existing allowlist and excludes Vercel, GitHub, model and auth-store
credentials; no token is placed on argv. The native response is captured and projected, not
printed raw. The receipt retains no new secret object or credential field.

## Manual event and workflow trigger checks

The workflow has no declared manual inputs. The staging condition is unchanged:
`contains(github.event.head_commit.message, '[stage-publisher]')`. An ordinary workflow_dispatch
payload has no head_commit, so that condition is false; selecting a commit whose message contains
a marker does not create a head_commit in the manual event. The job permits the manual route but
the stage command remains skipped. This conclusion comes from the actual event shape and source
condition; its hosted skipped-step receipt must still be retained after execution.

The workflow's declared permissions remain contents:read and actions:read. Its full fictional
guard suite runs before the read step, and only that read step receives the existing Vercel
secret. It installs the existing pinned CLI 64.7.0 and uploads the nonsecret receipt. The dispatch
has no staging input, new scope, new credential, archive write or promotion command on its active
path.

Every current repository push workflow explicitly restricts branches to Preview or main.
No workflow listens for branch creation or repository_dispatch. Thus pushing the specified
short-lived branch does not select another repository push job. The completion callbacks watch
the exact collector or daily publisher workflow names, not this read-only probe. No collector,
publication callback, rollback drill or source job is selected by this manual proof's completion.

The existing web Git map is exactly `{"**": false, "preview": true}`. Under the provider's
[documented matching rules](https://vercel.com/docs/project-configuration/git-configuration#branches-matching-multiple-rules),
a matching true entry permits a deployment. The short-lived branch matches the broad false
pattern and not exact preview. The source therefore requests suppression before a build, while
preserving Preview. Native suppression remains a fact to observe after the push; source config
alone is not a zero-charge receipt. Historical ignored builds must not be assumed free.

## Independent checks, authority and limits

Applied the bounded input-validation and information-leakage lens from the local Security Review
skill. It contains no separate permission requirement for this read-only review or an authorized
short-lived branch route. AGENTS explicitly permits short-lived work branches from Preview and
continues to protect main. The unavailable native branch-rules endpoint establishes no additional
permission and no bypass authority. Existing D-110 credential authority and the financial decision
remain their own governing records; this review creates neither.

Independently reran all nine focused publisher-probe tests in OrbStack, with all socket operations
denied: nine passed, zero skipped, in 0.005 unittest seconds. These cover fixed endpoint use,
auth/environment isolation and cleanup, typed positive/missing/malformed resource projection,
unrelated-field exclusion and safe errors. Parsed all workflow files and checked their actual
push/event selectors, the manual stage condition, read-only permission declarations and exact Git
map. No full operational/npm suite was duplicated and no provider request was made.

The existing manual workflow consumes GitHub-hosted runner time for installation and its full
suite even when staging is skipped. Fresh shared-runner and all-writer/Pacific-day cost checks
remain required by the accepted financial boundary. There is no expected Vercel build on this
route, no paid-build fallback approval and no managed-runtime trial restart. Actual Basic fields,
branch suppression, hosted step behavior and their bounded cost observations remain unproved
until the authorized operator retains native receipts. This review performed no push, dispatch,
provider authentication, deployment, source request, model call, settings change or paid action.

## Amendment after the first actual read-back

The original review above records the pre-execution state. Parent-retained native run
`41520910334` subsequently passed the fixed project GET, skipped staging and completed credential
cleanup. The parent observed an unchanged three-deployment Vercel inventory. Its saved receipt
reports Basic/fixed, with a null concurrency projection. That projection does not distinguish a
missing native key from native JSON null or an incorrectly typed value. It establishes no
concurrency-off result. The unchanged staging guard correctly continues to hold on that receipt.

Reviewed diagnostic amendment: `d5eec6481c624d59af9e8fd0f777925c1b9c3cba`, following the committed
specification `publisher-resource-defaults-amendment-2026-11-02.md`. Accept this diagnostic-only
amendment and the same financially conditional, watched short-lived-branch/read-only route. No
blocking defect was found. This accepts a better observation, not a change to effective settings
or production readiness.

The fixed project GET now separately projects native object presence/type, override flag
presence/type, default object presence/type and a strictly boolean-or-null default flag. Missing,
null, malformed and unavailable remain distinguishable. No raw resource/default object or
unexpected value is retained. There is no effective-setting field, merge, precedence rule or
missing-equals-false conversion. The guard, Basic preflight, source policy and publication adapter
are unchanged. No buildQueue field is added by this exact amendment; any later queue diagnostic
must remain separately whitelisted rather than copying a native object.

The only workflow change replaces the duplicate full operational test command with the focused
`test_publisher_probe.py` suite. An independent full-file comparison against the prior reviewed
workflow confirms every other byte remains unchanged: private-repository guard, manual event,
absent-head_commit staging condition, permissions, existing secret scope, fixed endpoint, pinned
CLI/actions, artifact handling, timeout and cleanup. Full operational guards remain in web CI.
The selected focused suite covers both credential isolation and the new diagnostic projection.

Independently reran all 12 focused tests with socket operations denied in OrbStack: 12 passed,
zero skipped, in 0.012 unittest seconds. Parsed the actual workflow and verified its no-input
manual route, unchanged staging condition and read-only permissions. The staging adapter,
publication ordering and full web CI are byte-identical to the prior reviewed source. No provider
request, push, dispatch, source edit, installation or paid action occurred in this review.

## Primary-source concurrency research

The current official SDK models make the concurrency boolean optional in both
[project resourceConfig](https://github.com/vercel/sdk/blob/main/src/models/getprojectresponsebody.ts)
and [defaultResourceConfig](https://github.com/vercel/sdk/blob/main/src/models/getprojectbuilds.ts).
Their generated schemas describe object shapes and optional booleans. They provide no selector
that merges these locations, no precedence order and no rule converting omission to false.
JSON null is not the declared boolean type. Optionality proves omission is possible; it does not
prove what the deployment server does when a value is absent.

The existing cached official CLI 64.7.0 was inspected in OrbStack without installation:
`/tmp/smp-vercel-stage-check/node_modules/vercel/dist/commands-bulk.js`, SHA-256
`2e77988a3dcff2b42cd124e82378f5903298b06135e6d708a488c1334b57908d`.
Its settings reader selects `project.resourceConfig[field]`; for this flag it contains no
`defaultResourceConfig` reference or effective-value resolver. Its toggle display maps true to
on, false to off and any other value to Auto. Thus the CLI does not substantiate missing=false,
and its display behavior is not evidence of server-side inheritance order.

The provider's current [managing-builds documentation](https://vercel.com/docs/builds/managing-builds#on-demand-concurrent-builds)
says projects default to on-demand concurrency. Its two documented buildQueue modes either run
builds immediately or restrict a branch to one active build; both are described within enabled
on-demand concurrency. Therefore WAIT_FOR_NAMESPACE_QUEUE alone cannot establish concurrency
off. Basic/fixed machine selection also does not determine that separate flag.

No authoritative effective-resolution order or absent/null server policy was found in the
inspected public primary sources or pinned CLI. This is an unresolved fact, not an implementation
rule. A second typed native read can establish the actual override/default shapes and values;
it cannot by itself establish undocumented precedence. Preserve unknown status until explicit
native off authority or an authoritative resolver supplies the missing rule. Do not relax the
staging guard based solely on missing flags, a false default with unknown precedence, queue mode
or a successful GET. The prior Basic/fixed read-back and this diagnostic review earn no new
staging or paid deployment authority.
