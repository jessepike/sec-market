# Publisher job cancellation predicate repair

## Authority and actual counterexample

Root authorized only the publisher job cancellation predicate in `.github/workflows/subscription-publisher.yml` plus this new documentation/receipt namespace. Base finish commit is `ee5c2851a3e0d58455d1dddd8ae74eddf753714e`. Every step, command, cleanup condition, credential expression, permission, timeout, concurrency rule, test and budget must remain unchanged. Status and backlog are outside this worker's ownership. Root owns all Git changes, promotion and dispatch.

Actual scheduled publisher `40271992393` ran old main `3bb9e40c8f6324aa4f419fbe13022ec4dcaece55`. Root's ordinary cancel was accepted during setup, but the job continued through its existing 972 guard tests and entered the restore/publication command at `05:03:05Z`. Force cancellation was required; the command ended with exit 143 at `05:04:46Z`. The separate job metadata records `05:04:44Z`; retain both original values. Receipt, alert and cleanup steps were skipped and there were zero artifacts.

The auditor's safe index is `/var/tmp/smp-oct26-scheduled-publisher-cancelled-40271992393/receipt-index.json`, SHA-256 `f2c0ffe610031de84c80532ac18649399706b56d1d79a2660aef33e80a4bcf14`. Its eleven payloads contain bounded diagnostics and authenticated state/public-file digests. Raw job log and raw remote heads stay outside the checkout. Remote archive remains `5ddcbc51613f125c12cdc724db821384886722f5`; gate attempts remain one of two and source counters remain 444 fetches, 76 calls and 37 documents. No new remote bootstrap or lease claim was persisted. Killed-runner ephemeral local state is unknown. All 106 public-file checks remain exact; this event gives no publication credit.

## Chosen one-line repair

[GitHub's official cancellation reference](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-cancellation) explains that the server re-evaluates a running job's `if` expression on cancellation and lets it continue when that condition remains true. Its explicit example uses `always()`. The current outer publisher predicate starts with that function, matching the actual continuation.

Replace only the publish job's `always()` status function with `!cancelled()`, enclosing the complete expression in `${{ ... }}` so YAML accepts the leading exclamation. Preserve the exact existing repository, private repository, main ref and event/readiness conditions. Keep the entire callback-preflight job unchanged.

`!cancelled()` is an explicit status check, so eligible schedule/manual runs retain their ability to run when callback-preflight is skipped. A workflow_run callback still requires readiness matching the existing `true` comparison. Cancelled workflows must be denied in every context. Wrong repository, public repository and non-main refs must remain denied. Leave all step-level `always()` conditions intact, including receipt retention, alert and ephemeral cleanup.

## Verification

Before mutation, pin all tracked bytes and save the original workflow. Verify that the final bytes are the exact original with only the intended job-if substitution and wrapper. Parse both YAML documents and prove their complete structures match after restoring only that job-if value. Confirm every other tracked file, every test and all other workflows remain exact.

Use an external, bounded expression evaluator that parses the actual YAML expression rather than a separately hand-copied policy. Evaluate old and new predicates against explicit cases for schedule/manual with skipped preflight, callback ready true/false/missing and uppercase TRUE/FALSE, wrong repository, private false, wrong ref and cancelled contexts. Evaluate all relevant combinations and compare to separately expressed eligibility expectations. Require every cancelled new case false, all eligible uncancelled cases true, and unchanged uncancelled eligibility compared with the original. Retain the evaluator, exact inputs and outputs as receipts; add no ops/ci test or production code.

Existing operational tests do not need repeating for this predicate-only patch. The ongoing ee5 canary must continue without a restart because operational sources are unchanged. Independent auditor review of the exact predicate, YAML preservation, expression checks and recovery assessment is required before root commits or promotes. Do not dispatch a cancellation experiment or consume a gate/source/model request.

## Existing cancellation and recovery boundaries

This change makes the job eligible for GitHub's normal cancellation handling. It does not prove a future actual cancellation receipt, guarantee every cleanup step after force termination, or change child-process signal handling. Keep force-cancel as a recovery action when ordinary cancellation does not terminate a run; inspect terminal metadata and authenticated remote state before resuming.

Existing publisher startup calls abandoned-lease recovery before bootstrap. That recovery releases a remotely active GitHub lease only after proving its exact owner/attempt is terminal and leaves all budgets unchanged. Existing release code persists the gate reservation remotely before dispatch. Promotion uses a tested manifest, staged-deployment journal, acknowledgement checks and pre-promotion remote checkpoint. Recovery accepts only the matching tested parent/journal/live acknowledgement and retains existing date/rollback checks. These conditions remain byte-exact; a forced kill does not guarantee the exception/checkpoint path runs. For the actual cancelled publisher, no new remote lease or gate was observed, while ephemeral local state remains unknown. No new recovery success is claimed by this patch.
