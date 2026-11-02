# Ordinary publisher stage safety

November 2, 2026. Implementation scope: the existing static Vercel adapter, its publication
checkpoint, and focused tests. Platform guidance read at
`ff32b0055293e4fb3bce550bade4652cc2ee1aa3`; existing T2 hosted runtime exception remains.

Before any provider creation, validate the exact accepted static payload, including the detached
receipt, against a 20,000,000-byte total. Functions remain prohibited by the existing artifact
validator. Read the native project and require fixed Basic builds with elastic concurrency off;
missing or changed resource fields hold before creation. Persist the existing publication attempt and consumed daily attempt remotely before
creation. Use the official CLI's `--no-wait` option with fixed release metadata. Resolve and
validate the returned deployment against the existing project, target, URL and release metadata;
persist and remotely checkpoint its identity before waiting for readiness.
The creation receipt is separate from the existing tested deployment attempt, so crash recovery
cannot treat an unprobed creation as a byte-verified artifact.

The stage has a 90-second local elapsed deadline, beginning before the create call. Management
calls have short timeouts. Request cancellation once when that deadline is reached or an
observation fails after the scoped native identity is known. Read back the terminal state. A late
READY result, cancellation race, failed cancellation or missing acknowledgement holds publication.
There is no automatic create retry, alias assignment or promotion after an uncertain result.

This is a runaway-build control, not a guaranteed billing cap. Vercel includes post-build time
and rounds billing to whole minutes. Network delay, scheduler delay, a lost create response or a
worker failure can prevent timely cancellation. A two-minute build reservation remains an
estimate rather than an enforced provider ceiling. Cost approval must preserve that uncertainty;
this repair cannot justify a guaranteed one-minute charge or a five-cent completed-day claim.

The ordinary site's `git.deploymentEnabled` map disables `**` and enables only exact `preview`.
This prevents a main/archive/feature-branch push from allocating an ignored build. The provider's
documented minimatch rules allow the specific true Preview exception to override the broad false
pattern. A single `*` would leave slash-containing refs unspecified and therefore enabled.
The existing ignored-build command remains defense in depth. Prebuilt publication uploads only
the accepted output, its detached receipt and pinned project IDs from a fresh temporary directory;
it never uploads this Git configuration or the source checkout. Its official CLI path remains.
Actual suppression of a main push still needs provider read-back after adoption.

Primary contracts: [CLI deployment](https://vercel.com/docs/cli/deploy),
[native cancellation implementation](https://github.com/vercel/sdk/blob/main/src/funcs/deploymentsCancelDeployment.ts),
and [billable duration](https://vercel.com/changelog/deployments-now-show-billable-duration-and-cpu-minutes).
[Git branch configuration](https://vercel.com/docs/project-configuration/git-configuration) and
the [project resource schema](https://github.com/vercel/sdk/blob/main/src/models/getprojectresponsebody.ts)
define the added preflight fields and automatic-deployment rules.
No new provider, credential, runtime, dependency, paid trial, live action or permission is added.

Verification covers accepted output only, payload rejection before create, fixed metadata,
scoped native identity, successful readiness, timeout cancellation, cancellation acknowledgement,
late READY and unknown outcomes, and remote checkpoint ordering. Hosted operation remains open.
