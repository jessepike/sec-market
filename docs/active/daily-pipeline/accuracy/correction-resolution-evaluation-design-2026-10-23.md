# Current correction resolution: bounded evaluation design

Prepared 2026-10-23T22:27:00.529263Z. Design only. The external-font gate repair takes priority; no evaluator implementation is proposed for this turn.

Add one optional **current-remediation observation**, paired with the immutable historical audit. Its sole measure is `accuracy.known_contradictions_resolved`: the number of the exact five contradicted records with a real admitted correction confirmed in production. Keep the fixed177 verdicts and existing `accuracy.known_contradictions` result unchanged. Do not add an averaged score or a wider metrics system.

## Exact scope

| Fixed audit target | Current factual group | Required result |
|---|---|---|
| `event:EV-checkpoint-2` | `FC-20261023-checkpoint-sase` | Withdraw from unfiltered retained events |
| `event:EV-optiv-2` | `FC-20261023-optiv` | Apply exact replacement |
| `event:EV-splunk-1` | `FC-20261023-splunk` | Withdraw from unfiltered retained events |
| `event:EV-zscaler-2` | `FC-20261023-zscaler` | Apply exact replacement |
| `supplier:expel:ownership` | `FC-20261023-expel` | Apply exact replacement |

The [JSON design](correction-resolution-evaluation-design-2026-10-23.json) binds each original/required-after hash, operation, current group/evidence/review-policy hashes and all atomic targets. Mapping SHA-256 is `502bf1d3a5ee23808dc803bafe3cbe10fee0e739dd7ec606b1783d2ea1c94580`. Expel ownership counts once; its last-round field and related evidence must still be admitted with the complete group. The related evidence repairs add no benchmark rows.

Xage's `publisher_disclosure_only` issue stays separate and cannot satisfy a factual row or change this denominator. All actual release requirements remain in force, currently six groups/12 targets. Source refresh can change candidate/evidence/review hashes only through proper new admission; a newly computed hash is not proof.

## Evidence required for credit

The read-only verifier must join four existing proof surfaces:

1. **The frozen audit and real admission.** Match the exact five contradicted IDs and published before objects. Authenticate the original approved main collector run/attempt and its receipt/checkpoint, then bind the accepted attempt, review, admission and index. Replay each full atomic group through `load_policy`/`replay_admission` using release-specific JSON and source bytes. A cached zero-call run or local synthetic accepted index does not establish original review execution. Validate freshness at the original admission time, not the later evaluation time.
2. **The independent gate and tested artifact.** Use `GitHubAuthority.verify_test_receipt` to authenticate the actual successful main gate and GitHub artifact digest/receipt. Bind its archive, snapshot, correction seal and full request inventory. Recompute the artifact inventory and replay the exact public correction bundle at its original check time, with the acknowledged parent bundle for retained history dates. Do not run another gate.
3. **Acknowledged release and current public bytes.** Authenticate the publisher run/artifact and validate the release ID/acknowledgement. Read the existing Vercel project/team/current-domain target and require READY. Compare the actual public app/deployment receipts and every expected static file with the tested artifact, including correction/history/tracker JSON and referenced JS chunks. Require unchanged receipts before/after the probe.
4. **The effective target.** Require the exact admitted after-value in effective unfiltered data, or an authenticated withdrawal plus absence from retained effective events. The actual exports must have passed the authenticated gate's runtime assertion and the fetched public app must equal that tested artifact. A history entry, screenshot or filtered-screen absence alone is insufficient.

One existing API detail matters: `VercelAdapter.pending_files` defaults to `None`, so a receipt probe can verify zero app files. Populate it from the pure `stage_files(readOnlyStore, artifact, acknowledgement)` helper, or use `publisher_stage.verify_files`, before the read-only production probe. Never call `adapter.stage`. `_get` is a bounded JSON-receipt reader; use the static byte verifier for large JS.

The original false text may deliberately remain in immutable history and compiled JS. Its literal presence cannot prove the effective correction failed. Equally, an old event falling outside the UI date window cannot prove withdrawal.

## Observation and states

Use a separate sidecar with the raw baseline audit/inventory pins, mapping hash, actual production revision/release, observation time, proof pins and exactly five derived record states. Keep scorecard's existing `claimAudit.appRevision == manifest.appRevision` equality unchanged. The sidecar explicitly distinguishes the historical baseline revision from the newly observed production revision. Link it beside the historical report; no scorecard schema or identity change is needed for this first step.

Let R be fully proven resolved rows, U positively proven unresolved rows and M = 5 − R − U. Pass only when R = 5; fail when U > 0; otherwise report unmeasured. Show R/5 when any target has authenticated current state, otherwise a null numerator, and always show R/U/M. `Unresolved` requires positive current evidence of the original effective error or a verified rollback. Missing proof remains unmeasured and the repair stays pending. Inconsistent IDs, hashes or joins reject the supplied claim.

Only an explicit authenticated gather+verify invocation may produce a current measured observation. Arbitrary offline JSON replay cannot acquire authority from `accepted`, `published`, `live` or `trusted` flags. Hashes/schema do not prove that a workflow, model or deployment ran. If current interfaces cannot authenticate the original collector/gate/publication chain, leave the row unmeasured. Review JSON has no provider signature; this design relies on the existing authenticated approved collector execution/checkpoint chain and states that limit openly.

The current result remains **unmeasured**, with zero verified repairs and all five repairs pending. Main still serves the baseline application without corrections. No new live pass can be produced from the supplied candidate/synthetic receipts.

## Proposed bounded invocation

A small future `ops/evaluation/correction_resolution.py` helper may reuse those existing read-only APIs and write only a new observation/report directory. This command is a proposed interface, **not implemented or run**:

```sh
orb run -m dev python3 ops/evaluation/correction_resolution.py --root . \
  --input /tmp/smp-resolution/pinned-inputs.json \
  --state /tmp/verified-published-evidence/state \
  --authenticate-production \
  --capture /tmp/smp-resolution/new-observations \
  --outputprefix /tmp/smp-resolution/current-remediation
```

Without authenticated reads, it reports unmeasured. It must not call the model, `process_corrections`, any gate/publisher/deployment action, real archive checkpoint or quota operation. Preserve source/review/publication times. A later observation may prove regression; old evidence cannot be relabelled current. Test forged/synthetic proof, missing origin, wrong artifact, partial groups, wrong effective values, empty expected-file inventory, rollback and partial R/U/M counts. No monitor, attestation service, new workflow or general history infrastructure is needed.
