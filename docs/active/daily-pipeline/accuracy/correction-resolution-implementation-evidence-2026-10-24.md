# Current remediation evaluator implementation evidence

The bounded evaluator is implemented in
[`ops/evaluation/correction_resolution.py`](../../../../ops/evaluation/correction_resolution.py).
It preserves the pinned 177-record audit and measures only the five fixed contradiction
targets in `correction-resolution-evaluation-design-2026-10-23.json`. Offline mode keeps all
five current states unmeasured. It does not accept an evidence JSON argument or change the
scorecard denominator.

Authenticated gather joins these existing surfaces:

- GitHub reads at the acknowledged release's exact app revision bind policy inputs and
  published helper code.
- The verified private archive binds the release, admissions, review records, admission
  index, source observations, collector checkpoint and gate checkpoint.
- Each resolved admission is tied to its unique original accepted attempt, matching review
  reference, time interval, document reservation and authenticated collector Actions
  artifact. Those bytes must occur in the exact gate archive checkpoint; a cached later
  admission cannot substitute for the original review.
- GitHub Actions API reads authenticate the collector, independent main-gate and publisher
  artifacts. Artifact download digests and receipts are checked against archived identities.
- `load_policy`, `replay_admission` and `project_bundle` replay all six release groups,
  including the publication-role-only Xage group, while only the fixed five factual rows
  enter the measure.
- `VercelAdapter` and `stage_files` bind the acknowledged production receipts and every
  expected static byte to the tested release. No staging or deployment method is called.

The authenticated live gather read archive commit
`9c8737cb4213f149f788b7ef1414921b8951bf0e`, manifest SHA-256
`cd9d84c67a70f11b72eeba25a012e3402a88b2d5a9c692f145c225b0a2c3418a`, and derived 5/5
resolved mapped targets. The joins covered original accepted review attempts and document
reservations, collector Actions artifacts, the independent gate artifact, the publisher
artifact, and current production receipts and static bytes. This does not estimate current
claim precision, recall or general site accuracy. The historical 177-record audit is
unchanged.

A rollback counts an original effective value as unresolved only when an archived rollback
event identifies the restored release, the failed staged release names it as parent, the
restored gate and publisher receipts are authentic, every live static byte matches, and the
exact correction export is disabled. A missing export or unavailable published runtime
source remains unmeasured. Original wording in JavaScript or immutable history, and arbitrary
sidecar flags, are not proof.

The VM run `orb run -m dev python3 -m unittest ops.ci.test_correction_resolution -v` passed
all eleven focused tests. They cover frozen input pins, exact five-row scope, R/U/M arithmetic,
historical immutability, a publisher artifact/checkpoint join with a fake reader, nested
domain values, the `mac gh` bridge, archive byte checks, rejection of a cached admission
without its original accepted attempt, reservation matching and rollback-gated unresolved
classification. The separate authenticated gather supplies real Actions and production
evidence for the current 5/5 observation.

The read-only command is:

```sh
orb run -m dev python3 ops/evaluation/correction_resolution.py --root . \
  --authenticate-production --restored-archive /path/to/verified/extracted/archive \
  --outputprefix /tmp/smp-resolution/current-remediation
```

Without `--authenticate-production`, the command writes an unmeasured observation. An
authenticated gather requires the extracted archive to match the authenticated current
private ref, plus the existing GitHub and Vercel read paths.
