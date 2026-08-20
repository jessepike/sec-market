# Lessons

Hot buffer. One line per insight, newest date first. Keep the last ~15; promote
cross-project patterns to the knowledge base and drop them from here.

## 2026-08-20

- [promoted:kb:4d7e316f:2026-08-20] A verification tool's account of what it fetched is not proof it fetched the right document. One fetch returned a Check Point earnings PDF in place of the requested IANS report; it surfaced only because the agent read the downloaded bytes instead of the tool's summary. Any unattended pipeline that trusts the summary can verify a claim against the wrong document and report a pass.
- [promoted:kb:0af2d678:2026-08-20] Never let the search corpus contain the thing being searched for. A grep run from `data/` matching evidence ids against `..` included `evidence.ts` itself, so every id matched its own definition and the check reported full coverage. Five records were actually orphaned.
- [promoted:kb:80b4d1bd:2026-08-20] A gate that returns nothing is not a gate that passed. A perturbation test produced no verdict because the edit broke the file's syntax and the script died before the assertion ran. Empty must fail loudly, or an unproven gate ships looking proven.
- [promoted:kb:dfe234cc:2026-08-20] HTTP 403 from SEC.gov is a published access policy, not a dead link. SEC asks automated requesters to declare an identifying User-Agent; doing so returns 200. Roughly half of a curl-based link check was false failures — 25 bot-blocks and 9 identical HTTP/2 errors across unrelated hosts, all healthy in a real browser.
- [promoted:kb:346eba72:2026-08-20] Server-rendered comment markers split text nodes, so a string-presence check against rendered HTML gives a false absent. `four<!-- --> <!-- -->domains` does not match `four domains`. Strip the markers before asserting.
- [promoted:kb:e9f33563:2026-08-20] Every drift found in a 71-source sweep was a missing source, never a wrong number. One `canonicalUrl` per record cannot carry an excerpt synthesized from several sources, so the extra claims silently lose their provenance. A schema limit surfaces as an accuracy defect.

## 2026-08-19

- [promoted:kb:4e46b8a2:2026-08-19] A review subagent briefed against the files I already read confirms my own blind spot. I flagged an acquirer and a price as unsourced; both were sitting in `activity.ts`, which I had not opened and had not told the reviewer to open. Scope a reviewer against the data, not against my reading list.
- [promoted:kb:4a4d0db6:2026-08-19] A fabricated "needs a source" marker is the same class of defect as a fabricated figure. Both put an untrue statement about the evidence on a page whose only claim is that every figure is checkable.
- [withheld:2026-08-19] A figure in a record's `note` field is not interchangeable with one in its `value` field. Falcon Cloud at $800M is an absolute amount; every other row in that table is a growth rate. The delegate caught this and was right.
- [promoted:kb:88658cce:2026-08-19] Asked for an opinion, I gave a hedge (run two directions together). The hedge was worse than either direction and the owner had to ask again. Pick one and say why.
- [promoted:kb:4c2dc09e:2026-08-19] A SHARE token is not a public preview. Vercel Authentication on `all_except_custom_domains` still sends strangers to login; disable SSO on the project, or they cannot give feedback.
- Putting the new landscape on top of the old edition is two products. Collapse the edition; do not delete it.

## 2026-08-17

- [promoted:kb:747452c9:2026-08-19] A passing build is not a rendered page. Five waves of work shipped without anyone opening the site, and the owner's first look was the first look anyone had taken.
- [promoted:kb:4d27f0b6:2026-08-19] Optimizing the conditions that already work is the most expensive kind of wasted effort. The overnight waves strengthened C4 and C2 and left C3, C5 and B1 untouched — the three that were actually missing.
- [promoted:kb:0133ef44:2026-08-19] `main` being production means every agent push is a publish decision. The fix is a branch and a preview URL, not more care.
- [promoted:kb:4972b1b1:2026-08-19] Case-sensitive grep produced a false finding: the posture vocabulary was reported absent because the code uses `PREPARE` and the search used `prepare`. A null result from one search spelling is not evidence of absence.
- [promoted:kb:4ceff6f3:2026-08-19] "No importers found" is a hypothesis, not a fact. Two independent agents called four components dead; only a render settles it.
- [promoted:kb:615b1d65:2026-08-19] A hand-written delta is a fabrication surface. Deriving Held/Moved/New from two frozen snapshots means the page cannot claim a posture held when it moved, and the claim stops depending on the honesty of whoever typed it.
- [promoted:kb:7ea10ade:2026-08-19] Record what a prior edition genuinely published, including what it did NOT publish. The 16 August snapshot carries `horizon: null` rather than a backfilled plausible value.
- [promoted:kb:700270a9:2026-08-19] Prove a build gate fails closed by perturbing the input and watching the build refuse. A gate nobody has seen fire is a comment.
- [promoted:kb:5ee97283:2026-08-19] Adding a table column is a mobile change. The new Horizon column pushed the Tempo table past a phone viewport and clipped prose mid-sentence — the same class of bug fixed the night before.
- [promoted:kb:9af282b6:2026-08-19] Assert tests against structure, not editorial copy. A smoke test pinned to the edition summary sentence breaks every edition by design.
- [promoted:kb:59445476:2026-08-19] Branch checkouts move underneath an active session when more than one agent works a repository. Use a worktree, and re-check `git status` rather than trusting the branch you started on.
