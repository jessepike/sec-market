# Lessons

Hot buffer. One line per insight, newest date first. Keep the last ~15; promote
cross-project patterns to the knowledge base and drop them from here.

## 2026-08-27

- A research subagent that spawns its own sub-agents can exhaust a session budget with no warning. Three lanes fanned out into eight-plus children and killed the run. The containment that worked: ban sub-agent spawning in the prompt, replace an open sweep with a fixed target list, add an explicit "record none disclosed and move on" stopping rule, and cap the output length.
- A null result can mean the question was aimed one layer too high. Twelve vendors disclose nothing about AI security revenue, which reads as an empty lane. The hard evidence was in the same filings one layer down, in the purchase price allocations of the acquisitions.
- A purchase price allocation says what an acquirer thinks it bought. Two AI security deals put almost the whole price in goodwill and assigned nothing to customer relationships, while an adjacent deal in the same filing put $464M of $476M into customer relationships. That contrast is stronger evidence than any figure either company would state directly.
- A header that undercounts what is on screen is the same defect as one that inflates it. My own spec told the implementer to keep primary and borrowed counts separate, which produced "0 prints" above a group displaying a real comparable print. Every gate passed. Nothing enforces that a group header matches its own rendered cards.
- `node_modules` in `web/` was installed inside the OrbStack dev VM, so npm, npx and tsx cannot run on the host at all — esbuild refuses with a platform mismatch. Run them through `orb run -m dev`. Playwright and `shot.mjs` are the exception and do run on the host against system Chrome.

## 2026-08-22

- [promoted:kb:7c349194:2026-08-22] Being in the served HTML is not being on the page. Forty-two vendor cards were present in the markup and zero were visible; I reported them as shipped from a `curl`, and the owner was right to call it. `checkVisibility()` settles this question and `getComputedStyle` does not.
- [promoted:kb:d5b498ae:2026-08-22] `git add -A` while another worker is editing the same directory sweeps its in-flight edits into your commit. Stage explicit paths by name whenever a session is not the only writer.
- [promoted:kb:64b7354d:2026-08-22] A build can pass every gate while silently reversing the accepted design. The phone view put the framing sentence below the four cards because of two CSS `order` declarations; nothing failed, and only rendering at the design's own width against the accepted render caught it.
- [promoted:kb:7e7d7efa:2026-08-22] Codex CLI needs its prompt on stdin. Passing the prompt as a positional argument leaves it blocked reading stdin, producing nothing while appearing to work — I told the owner a review was running when it had not started.

## 2026-08-20

- [promoted:kb:f9e2584f:2026-08-20] A subagent inherits the premises of its prompt and returns them with fresh evidence attached, which makes an inherited error harder to see rather than easier. I put a wrong quarter into a source-hunt prompt; the agent reasoned correctly from it and recommended deleting two accurate records, supported by a real document, a slide number and a verbatim quote. Check a delegated finding against the data before acting on it, and check hardest when the finding looks well supported.
- [promoted:kb:e171ddd5:2026-08-20] Scope a verification against the schema, not against the subset of fields you extracted. Feeding agents only `canonicalUrl` while records also carry a `sourceAttributions` array produced five false "unsourced" findings, including one where the hunt "found" a URL already sitting in the record.
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
- [promoted:kb:010f9cd6:2026-08-22] Putting the new landscape on top of the old edition is two products. Collapse the edition; do not delete it.

