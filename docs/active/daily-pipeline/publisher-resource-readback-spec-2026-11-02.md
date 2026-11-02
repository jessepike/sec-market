# Native publisher resource read-back preparation

Prepare three nonsecret fields in the existing read-only publisher access receipt:
`buildMachineType`, `buildMachineSelection`, and `elasticConcurrencyEnabled`, read only from
the fixed project's native GET response `resourceConfig`. Preserve the exact existing project,
team, private-runner, token isolation, endpoint and all receipt flags. A missing/non-dictionary
resourceConfig yields null for all three fields. Missing or incorrectly typed individual fields
also yield null. Return only string/string/boolean scalar values; never dump the resource object.
No workflow, branch rule, secret, permission, credential or provider setting changes.

The existing `subscription-publisher-probe.yml` allows manual dispatch for this exact private
repository. Its stage step requires `github.event.head_commit.message` containing the stage
marker. A manual event has no head_commit, so that step is skipped. This preparation leaves the
condition and every workflow byte unchanged. The probe's sole CLI call is GET on the fixed
existing project with the known team selector. Existing D-110 token use remains scoped to that
same read; no new token or environment is requested.

AGENTS permits a short-lived work branch from Preview. The installed push guard protects main;
no guard is removed or weakened. The already reviewed candidate's deploymentEnabled map disables
all Git branches except Preview. A future branch-only push may test native suppression and a
later manual read-only probe may expose the native resource fields, but neither action is
performed here. Actual branch suppression and zero deployment/build activity remain unproved.
Before any push/dispatch, require independent exact-source review and fresh financial-risk
assessment. No paid build, provider activation/purchase, source request, archive write, main
promotion or deployment is authorized. Existing paid trial stays stopped.

Apply the Security Review skill's bounded input-validation/information-leakage lens to this
change; unrelated project-wide findings are outside scope. Run existing publisher probe tests
plus focused positive, absent, non-object and malformed field cases only in OrbStack. The full
1,090 operational and npm suites already passed for the combined candidate; no web source changes
are proposed. Preserve all UI, staging guard, K source, baseline, admission and workflow bytes.
Existing personal platform standard ff32b0055293e4fb3bce550bade4652cc2ee1aa3 applies: T2 Important,
Public configuration/Internal receipt; GitHub/private archive exception unchanged.
