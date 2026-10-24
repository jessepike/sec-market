# Rollback verification repair

Root independently verified the retained parent release's exact acknowledgement and all 25 static
files on its immutable Vercel URL at `2026-10-24T01:09:54.590281Z`, without changing production.
See [parent verification](receipts/rollback-parent-immutable-verification-2026-10-24.json).
The failed run's journal confirms current restoration and byte verification. Its original baseline
failure category remains unknown; the reproduced propagation gap is a repairable defect, not a
proven explanation of that remote exception.

The approved drill against accepted release `a564d0a471931329bdf8a2e263bf26838ecb23d06d4a98d78cc4735c629c44f4` restored the current deployment and verified its bytes, but did not acknowledge the retained baseline. The archived error type alone does not establish why baseline verification failed.

The code performs a single baseline probe after the alias API observes the expected application receipt. The detached receipt or static assets can still lag that application receipt. Current restoration already has a bounded convergence probe. The retained parent for this drill is an accepted daily release, so its exact manifest, detached acknowledgement and static inventory are available.

## Required behavior

- Reconstruct and integrity-check the exact retained artifact before alias changes. Reject an empty static payload inventory before any mutation.
- For an accepted daily parent, verify the application/detached receipt pair, all acknowledgement fields and the exact retained static bytes on its immutable host and on the public host after rollback. Retry the complete check at most six times with five seconds between attempts. Each retry keeps the same expected manifest, acknowledgement and byte inventory.
- Preserve the existing legacy-baseline exception: it has an application receipt but no retained artifact inventory. Retry its exact application receipt without claiming static-byte verification.
- Always attempt restoration of the accepted current immutable deployment after a rollback attempt, including permanent baseline receipt or byte failures. Verify current receipt pairing and bytes before recording restoration.
- Preserve the production head throughout the drill. Journal only fixed failure phase/category labels, never raw remote errors or response contents.
- Do not retry a live drill, deploy, change workflows, alter quotas or change credentials as part of this repair.

## Verification

Tests cover a nonlegacy parent, delayed application/detached/static convergence, permanent baseline failure followed by exact current restoration, empty payload rejection before alias changes, safe diagnostics and an unchanged production head. The propagation explanation remains a tested failure mode, rather than a claim that it caused the observed remote failure.

OrbStack verification passed all 18 rollback tests and all 449 operational tests. No live rollback, deployment, remote mutation or Git operation was performed for this repair.
