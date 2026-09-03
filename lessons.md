# Lessons

Hot buffer. One line per insight, newest date first. Keep the last ~15; promote
cross-project patterns to the knowledge base and drop them from here.

## 2026-09-03

- [promoted:kb:eb06c6c0:2026-09-03] The first research question's frozen answer became the headline of a product meant to be a weekly pulse, and the recurring content sat in a collapsed board whose window had ended three weeks earlier. When a project moves from an episode to a recurring product, check that the front page carries the recurring question rather than the first one asked.
- [promoted:kb:1406388d:2026-09-03] Three weeks of gates, sweeps and visibility fixes were all correct and none of them moved the exposure denominator off one. Craft work on an unread page has a ceiling; the next unit of work should be the one that puts the page in front of a named reader.

## 2026-08-28

- [promoted:kb:b51ee163:2026-08-28] The site's whole message layer was collapsed and nobody had checked. "The read" — the market call, the do and avoid lists, the no-call boundaries — sits inside a closed `<details>` on production; `checkVisibility()` at 1561px returns false. The vendor scorecard was promoted out of exactly this pattern six days earlier and the read was never tested for it. Fixing one instance of a defect is not fixing the pattern, and the second instance was hiding the more valuable content.
- [promoted:kb:2f162256:2026-08-28] Adding evidence is not publishing a read. I specced three acquisition cards into a collapsed scorecard group and called it publishing the finding. The owner asked how the message actually reaches the page, which was the right question and one I had not asked myself.

## 2026-08-27

- [promoted:kb:fb388c8e:2026-08-27] A research subagent that spawns its own sub-agents can exhaust a session budget with no warning. Three lanes fanned out into eight-plus children and killed the run. The containment that worked: ban sub-agent spawning in the prompt, replace an open sweep with a fixed target list, add an explicit "record none disclosed and move on" stopping rule, and cap the output length.
- [promoted:kb:1ca920a5:2026-08-27] A null result can mean the question was aimed one layer too high. Twelve vendors disclose nothing about AI security revenue, which reads as an empty lane. The hard evidence was in the same filings one layer down, in the purchase price allocations of the acquisitions.
- [withheld:2026-08-27] A purchase price allocation says what an acquirer thinks it bought. Two AI security deals put almost the whole price in goodwill and assigned nothing to customer relationships, while an adjacent deal in the same filing put $464M of $476M into customer relationships. That contrast is stronger evidence than any figure either company would state directly.
- [promoted:kb:8dce3e63:2026-08-27] A header that undercounts what is on screen is the same defect as one that inflates it. My own spec told the implementer to keep primary and borrowed counts separate, which produced "0 prints" above a group displaying a real comparable print. Every gate passed. Nothing enforces that a group header matches its own rendered cards.
- [promoted:kb:0d1eff9b:2026-08-28] `node_modules` in `web/` was installed inside the OrbStack dev VM, so npm, npx and tsx cannot run on the host at all — esbuild refuses with a platform mismatch. Run them through `orb run -m dev`. Playwright and `shot.mjs` are the exception and do run on the host against system Chrome.

## 2026-08-22

- [promoted:kb:7c349194:2026-08-22] Being in the served HTML is not being on the page. Forty-two vendor cards were present in the markup and zero were visible; I reported them as shipped from a `curl`, and the owner was right to call it. `checkVisibility()` settles this question and `getComputedStyle` does not.
- [promoted:kb:d5b498ae:2026-08-22] `git add -A` while another worker is editing the same directory sweeps its in-flight edits into your commit. Stage explicit paths by name whenever a session is not the only writer.
- [promoted:kb:64b7354d:2026-08-22] A build can pass every gate while silently reversing the accepted design. The phone view put the framing sentence below the four cards because of two CSS `order` declarations; nothing failed, and only rendering at the design's own width against the accepted render caught it.
- [promoted:kb:7e7d7efa:2026-08-22] Codex CLI needs its prompt on stdin. Passing the prompt as a positional argument leaves it blocked reading stdin, producing nothing while appearing to work — I told the owner a review was running when it had not started.

## 2026-08-20


## 2026-08-19

- [withheld:2026-08-19] A figure in a record's `note` field is not interchangeable with one in its `value` field. Falcon Cloud at $800M is an absolute amount; every other row in that table is a growth rate. The delegate caught this and was right.
- [promoted:kb:010f9cd6:2026-08-22] Putting the new landscape on top of the old edition is two products. Collapse the edition; do not delete it.

