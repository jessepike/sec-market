# Lessons

Hot buffer. One line per insight, newest date first. Keep the last ~15; promote
cross-project patterns to the knowledge base and drop them from here.

## 2026-08-19

- A SHARE token is not a public preview. Vercel Authentication on `all_except_custom_domains` still sends strangers to login; disable SSO on the project, or they cannot give feedback.
- Putting the new landscape on top of the old edition is two products. Collapse the edition; do not delete it.

## 2026-08-17

- A passing build is not a rendered page. Five waves of work shipped without anyone opening the site, and the owner's first look was the first look anyone had taken.
- Optimizing the conditions that already work is the most expensive kind of wasted effort. The overnight waves strengthened C4 and C2 and left C3, C5 and B1 untouched — the three that were actually missing.
- `main` being production means every agent push is a publish decision. The fix is a branch and a preview URL, not more care.
- Case-sensitive grep produced a false finding: the posture vocabulary was reported absent because the code uses `PREPARE` and the search used `prepare`. A null result from one search spelling is not evidence of absence.
- "No importers found" is a hypothesis, not a fact. Two independent agents called four components dead; only a render settles it.
- A hand-written delta is a fabrication surface. Deriving Held/Moved/New from two frozen snapshots means the page cannot claim a posture held when it moved, and the claim stops depending on the honesty of whoever typed it.
- Record what a prior edition genuinely published, including what it did NOT publish. The 16 August snapshot carries `horizon: null` rather than a backfilled plausible value.
- Prove a build gate fails closed by perturbing the input and watching the build refuse. A gate nobody has seen fire is a comment.
- Adding a table column is a mobile change. The new Horizon column pushed the Tempo table past a phone viewport and clipped prose mid-sentence — the same class of bug fixed the night before.
- Assert tests against structure, not editorial copy. A smoke test pinned to the edition summary sentence breaks every edition by design.
- Branch checkouts move underneath an active session when more than one agent works a repository. Use a worktree, and re-check `git status` rather than trusting the branch you started on.
