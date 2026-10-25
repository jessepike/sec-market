# Cross-day public source inventory repair

## Actual failure and diagnosis

Manual publisher 40147731858 on main aefc3fbd0c48d4a32348fa298737b038ece30735 failed after independent gate 40148005688. The gate verified its complete evidence archive and passed SEC refresh, filing events, SEC certification, 373 data tests and 115 pipeline tests. The build entry point then rejected the candidate: "Daily v2 coverage completion differs from its source receipts". No production deployment or candidate artifact was accepted.

The diagnostic artifact is 12581695199, ZIP SHA-256 4aad5a069e8160c286d6d5b3cfaf0ed63f64c7ad217e1ed5e708b11b7a909f0e. Its test.log contains the exact failure. The actual gate archive is 82dcdf07ace4e96d9eb461992e81c0bfffe457ec, manifest 1dd9af6ae42efb862067629c9583f140c529038852bd089f2444ad368fb868b2. The failed publisher subsequently advanced the remote archive; retain both historical checkpoints.

Task identities contain their original UTC collection day. build_snapshot currently calls reporting.inventory(contract, now, verified). After midnight that creates the next day's task IDs, which cannot join the original verified receipts. Its aggregate still reports 264/557 while the individual rows fall back to unchecked and their IDs disagree with the 293 original gaps. Earlier offline reconstruction inspected aggregates and continuity, but did not execute the JavaScript public-source verifier. That was an acceptance gap.

## Required change

Use the exact verified plan's original scheduledAt when constructing its public inventory. Keep gate-time reconciliation and source freshness at now. Preserve the 557 obligations, original task/run identities, receipt times, normal four fact references, 33 review entries, all retained evidence and six corrections.

Prefer the narrow snapshot call-site repair. Do not weaken verify-daily.mjs, invent checked rows, use aggregate totals to overwrite source receipts, change the contract or origin authorities, renew evidence dates, alter budgets, reset/refund the charged attempt, or infer scheduled execution. The qualification plan stays exact disabled ad1.

## Acceptance

Reproduce the actual cross-day failure before the repair. Add a portable regression exercising snapshot reconstruction across UTC midnight and the real JavaScript public-source validator. Demonstrate that required row IDs, checked count, gap IDs, processing/history summaries and original source times agree with the verified source receipt; unsupported or inconsistent data still fails. Verify same-day behavior and current-time expiry remain unchanged.

Replay the actual acknowledged normal archive read-only under MemoryStore, with file/directory seals unchanged. For the complete release rehearsal use a separate VM application copy, actual archived evidence, archived SEC cache and the actual baseline release. Run reconstruction, SEC refresh/certification and the complete npm test/build/browser path. No source collection, models, production changes or gate attempt is consumed by this local rehearsal. Keep the original checkout untouched and use OrbStack for all runtime work.

The failed October25 gate attempt remains charged. No remote retry is authorized by this specification itself. Root will decide the remaining attempt after the defect is fixed and reviewed, while preserving genuine scheduled-run verification.
