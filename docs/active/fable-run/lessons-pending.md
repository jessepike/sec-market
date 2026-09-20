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
