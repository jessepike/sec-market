# Publisher job cancellation repair

The isolated patch replaces the publisher job's outer always() status check with an expression-wrapped !cancelled(). It preserves every existing repository/private/main/event/readiness condition, callback preflight, step, cleanup condition, concurrency rule, permission, timeout, credential expression and command. All 960 external checks of the actual YAML expression pass. Independent review is PASS; finish remains clean pending root-authorized controlled integration.

## Actual reason and scope

Scheduled publisher 40271992393 on old main 3bb9e40c continued after the owner's ordinary cancellation, entered its restore/publication command at 05:03:05Z, and required force cancellation. The command ended with exit 143 at 05:04:46Z; the separately retained job metadata says 05:04:44Z. Zero artifacts were retained. [GitHub's official cancellation reference](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-cancellation) explains that the server re-evaluates running job conditions and permits a job to continue if its condition stays true; its example is always(). This matches the actual failure.

The auditor proves remote archive 5ddcbc51613f125c12cdc724db821384886722f5 and eight remote heads unchanged, gate attempts 1/2, source counters 444/76/37, no newly persisted bootstrap/lease claim, and all 106 public-file bytes exact. Ephemeral local claim/restore state of the killed runner remains unknown. This failure produced no new release or freshness. Only eleven indexed safe payloads plus their index are retained; raw job log and raw remote heads remain outside the checkout.

## Exact patch and verification

The candidate is an isolated Git archive of ee5c2851a3e0d58455d1dddd8ae74eddf753714e. The publisher YAML changes from SHA-256 b6eb167cf43aab8624dd69eaabfe9900a4c192789cef4c286cdb477c0b897b7b (3,870 bytes) to c2872c54242468ae8e52f963818e3a01d1950a5b28318e51b0e9e5175e3ebec1 (3,881 bytes). Exact byte substitution and normalized parsed-YAML checks pass. All 3,026 other tracked files remain byte-exact. The web, ops and contracts Git trees are also identical between accepted 34e and ee5, and the isolated patch leaves them unchanged. No operational suite rerun or ee5 canary restart is needed or claimed.

The retained external evaluator parses the expression directly from the YAML. It uses GitHub's documented case-insensitive string equality for the declared string/Boolean contexts and makes no general mixed-type coercion claim. Its 960 combinations cover event schedule/manual/callback, cancelled state, correct/wrong repository, private/public repository, main/preview ref, readiness true/false/missing/uppercase TRUE/FALSE and four preflight outcomes. Every cancelled new case is false. Every uncancelled result matches the prior expression. Eligible schedule/manual cases remain true even when callback-preflight was skipped; workflow_run requires the unchanged true comparison. This is a bounded offline check of the actual expression syntax and status truth table, not a remote GitHub cancellation experiment. The first receipt harness counted the crossproduct incorrectly as 1,152; that count was corrected to 576 before the later uppercase expansion to 960, and the entire original-to-patch verification reran successfully.

## Cancellation and recovery assessment

All step-level always() conditions remain exact for receipt retention, owner alerts and ephemeral cleanup. GitHub's process cancellation remains asynchronous; this patch does not guarantee cleanup after forced termination or claim a future successful cancellation receipt. Force-cancel remains available for recovery, followed by terminal-run and authenticated remote-state verification.

Existing startup recovery proves an active lease owner/attempt terminal before releasing it, retaining all budgets. Existing release code checkpoints the gate reservation before dispatch. Promotion and crash recovery still require the tested parent manifest, staged deployment journal, acknowledgement checks and remote checkpoint, with existing date/rollback rules. Forced termination can bypass Python exception/final checkpoint handling; no new recovery success is claimed here. The actual cancelled run had no new remote lease/gate, while its local ephemeral state remains unknown.

No step, runtime code, source policy, test, assertion, source/model/gate budget, environment or credential changed. No main promotion, source/model request, state write, commit, push or dispatch was performed. Root owns controlled integration and any later actual cancellation/publication verification. The current canary is unchanged and continues on its accepted source.

## Independent handback

The auditor independently verified 2,880 expression cases, including case-insensitive strings: all 1,440 cancelled cases are denied and all uncancelled eligibility is preserved. The auditor confirms all 3,026 other tracked files remain exact and the worker evaluator finding is resolved. Review is retained under this unit's receipts/independent/review.md, SHA-256 `b4dd7563eedf9477a32b5d2405a4cb61f84f6a28a4b201ed375f04aa2a1f486f`; independent index SHA-256 is `c6af13b377c6a861197839b4a23b2d735a40d01772b88333b9d56d17f705c25c`.

The sealed copy manifest permits only this one workflow and the named new repair documentation/receipt files. The expected finish base is ee5; reject an unexpected publisher workflow change or a pre-existing differing repair target. Root acceptance and controlled copy remain required. No live cancellation success or publication result is implied.
