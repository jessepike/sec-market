# Independent review of ordinary publisher stage cost controls

Reviewed source: `06894f56c6f665d4c7f71224136b28b46682faa0`.
Reviewer scope: source inspection and denied-provider local checks. No source edits, provider calls,
creation, dispatch, deployment, credential use or spending occurred during this review.

## Recommendation

Accept this repair for the normal reviewed release route, subject to the combined exact-code
checks and existing release gates. No blocking defect was found in the reviewed change.
It adds useful limits and preserves publication authority. Actual provider operation, cancellation
timing and completed-day cost remain unproved by these local checks.

## Publication and spending boundaries

The ordinary publisher already requires its remote checkpoint callback. The new publication
checkpoint saves the release attempt and consumed daily attempt before the adapter can create a
deployment. A failed checkpoint blocks creation. A lost creation response leaves that attempt
consumed; the adapter does not issue another create or guess a cancellation target.

An immutable URL returned by the CLI is saved only as an explicitly unverified hint. Cancellation
requires a separate native read that matches the deployment ID, project, URL, target and release,
application and artifact metadata. Management calls are team-scoped. Native fields must have the
expected object/string forms and allowed states; unknown identities and states hold publication.
The creation journal is separate from `deployment-attempts`, which is written only after byte
verification. Recovery still requires the existing verified attempt journal, manifest and live
acknowledgement. A creation or URL hint cannot authorize recovery or promotion.

Before creating, the adapter verifies the accepted artifact inventory through `stage_files` and
limits the complete staged output, including config and detached receipt, to 20,000,000 bytes.
The existing artifact parser accepts config plus static members, rejects Functions/executable
output and external rewrites, and remains unchanged. The temporary deployment directory contains
accepted output and pinned project IDs. The source checkout and Git configuration are not uploaded
through this prebuilt path. No new main deployment route is introduced.

The project preflight requires the pinned project and account IDs and a resource object with
`buildMachineType` equal to `basic`, `buildMachineSelection` equal to `fixed` and
`elasticConcurrencyEnabled` exactly false. Missing, unknown and changed settings fail before
creation. These fields match the provider's [project response schema](https://github.com/vercel/sdk/blob/main/src/models/getprojectresponsebody.ts).
This is a settings observation before creation; it cannot guarantee unchanged provider settings
or a final charge after that observation.

## CLI, deadline and uncertain outcomes

The workflow pins Vercel CLI 64.7.0. Its retained local help receipt explicitly supports
`--no-wait`, metadata, prebuilt output and skipped domain assignment. The official
[deploy documentation](https://vercel.com/docs/cli/deploy#no-wait) confirms the early-return
behavior. The normal target remains production with domains unassigned, followed by the existing
exact-byte probe and promotion process. The smoke path remains a preview target.

The 90-second elapsed deadline starts before creation. Creation has a 30-second subprocess
timeout, and management calls have 10-second timeouts. Once native identity is established, a
failure or deadline attempts one scoped cancellation and then reads native state. The cancellation
endpoint and terminal-state behavior match the provider's [native cancellation implementation](https://github.com/vercel/sdk/blob/main/src/funcs/deploymentsCancelDeployment.ts).
A lost cancellation response is reconciled by read-back, without sending another cancellation.
Late READY and unknown stop outcomes hold publication. No uncertain result leads to promotion.

This is a proportionate control against unexpectedly long builds. It is not a provider-enforced
billing ceiling. Checkpoint time, network calls, process interruption, unknown creation identity
and provider billing rules can extend billable work beyond the local deadline. A slow remote
checkpoint can also consume the readiness allowance and hold an otherwise successful deployment.
That availability tradeoff is explicit and conservative. The next genuine scheduled run should
retain creation/readiness/checkpoint timing and actual billing before making a savings claim.
The stopped managed-runtime trial and five-cent completed-day requirement remain separate.

## Git build path

The only web configuration change is `git.deploymentEnabled` set to `{"**": false, "preview": true}`.
The provider's [Git configuration rules](https://vercel.com/docs/project-configuration/git-configuration#branches-matching-multiple-rules)
state that a matching true rule permits deployment. The broad false pattern closes unspecified
and slash-containing branches while exact preview remains enabled. The existing ignored-build
command remains unchanged. The prebuilt publication path does not consume this source config.
Actual suppression on the next main push requires provider observation after adoption; local
configuration and tests cannot establish that hosted result. Page/UI source is unchanged by this
repair.

## Independent verification

At the reviewed commit, independently reran `test_stage_cost_bound.py` in OrbStack with existing
dependencies: all 15 tests passed, zero skipped, unittest time 0.014 seconds. These exercise
payload rejection before creation, Basic preflight rejection, durable attempt ordering, lost
create responses, native identity mismatch, untrusted hints, checkpoint failure, readiness,
deadline cancellation, cancellation read-back, late READY and no repeated create/cancel.

The implementer reported 13 staging tests, eight publisher tests and 115 pipeline tests passing.
Those broader suites were not duplicated here. Full operational verification was still running
when the source was handed over; the delivery owner must use its final receipt before release.
The reviewed diff contains only the adapter, publication ordering, safe failure categories,
necessary tests, branch configuration and supporting documentation. No provider or hosted result
is claimed by this independent review.
