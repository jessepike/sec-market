# Lessons from run SEC-MARKET-FABLE-001, waiting to go into `lessons.md`

`lessons.md` in the project root carries another session's uncommitted change, so this run did not
touch it. Whoever next owns `lessons.md` should move these lines in and delete this file.

- 2026-09-20: Check the stated intent against the owner's own words early. The run brief and `intent.md` had drifted from what he wanted, and one conversation changed the centre of the product after a full design had been built on the old one.
- 2026-09-20: At a gate, split decisions into those only the owner can make and those the agent takes on its own recommendation. Handing over twenty decisions reads as not having run the work end to end.
- 2026-09-20: An external review by a different model caught what the coordinator and an adversarial pass by the same model family both missed: a ranked supplier table that implied endorsement, and two quarterly figures labelled as full-year in a signed issue. Use one on anything reader-facing.
- 2026-09-20: A rubric written by the designer rewards the designer's own design. Get an outside model to review the rubric, and add blockers that a high score cannot hide.
- 2026-09-20: A gate that checks a number appears in its source does not check what the number means. Company or segment, metric, period and units have to be validated together.
- 2026-09-20: Colour on a figure is a comparison. Green and red growth numbers rank suppliers by eye even under a caption that says they are not ranked.
- 2026-09-20: Spot-check subagent claims about status codes, prices and anything described as "empty" or "identical" before citing them. Haiku invents "typical" prices when a pricing page is rendered by JavaScript unless it is told to label fetched versus remembered.
- 2026-09-20: An Xcode update can break `/usr/bin/git` and `python3` mid-session. Workaround: `export DEVELOPER_DIR=/Library/Developer/CommandLineTools`. Fix: `sudo xcodebuild -license`.
- 2026-09-20: `web/scripts/shot.mjs` needs Google Chrome and fails in the OrbStack VM. `docs/active/fable-run/evidence/baseline/capture.mjs` uses plain chromium and works there.
- 2026-09-20: GitHub refuses a push that touches `.github/workflows/` unless the token has the `workflow` scope. `gh auth refresh -h github.com -s workflow` adds it and needs a browser approval.
- 2026-09-20: A leftover `vite preview` process on port 4173 makes the Playwright suite time out. Kill it before running `npm test`.
- 2026-09-20: `codex exec -m gpt-6-astra -s read-only -C <dir> -o <file> "<prompt>"` works for a read-only external review. SendMessage can redirect a background agent that is still running, and resume one that has finished.
- 2026-09-21: Promotion can be done without switching branches: `PROMOTE=1 git push origin <preview-sha>:refs/heads/main`, then `git fetch origin main:main`, then fetch the live host and check for content, not only a 200. Safe when the shared checkout holds another session's uncommitted files.
- 2026-09-21: After merging a tested branch, run `git diff --stat HEAD origin/<branch> -- web`. An empty result proves the trunk's `web/` equals the head that was tested.
- 2026-09-21: A blind scorer's sample can miss errors the coordinator already knows about. Tell it to check every lane headline, not only the scorecard.
- 2026-09-21: A scorer with no measurement evidence scores "not measured" as a fail. Run the baseline's measurement scripts against the new build before scoring it.
- 2026-09-21: A subagent filled a JUDGED stamp with the site's last-updated date. A date under the author's name must come from signed data, never from a build constant.
- 2026-09-21: A Haiku capture agent can leave stray image copies in `web/`. Check `git status` after any capture task.
- 2026-09-21: A subagent can die on a subscription usage limit (429) in the middle of a task. Check the branch and the deploy, then resume it with SendMessage.
- 2026-09-21: Two sessions reshaping the same page force a rebase mid-task. Give `web/` a single owner at session open.
- 2026-09-21: The owner does not want commands handed to him or a long list of things that need him. Ask for the word in one sentence and run it.
- 2026-09-21: A gate on what a figure means needs an exemption that reads `corrections.ts`, because a locked issue cannot be edited to pass it.
- 2026-09-21: macbook2014 is reachable over ssh from the laptop. Its Claude login expired (401 on `claude -p`), which blocks every headless job there until `claude setup-token` is run interactively.
