# Fable run brief — Security Market Pulse as a weekly destination people pay for

**Artifact ID:** `SEC-MARKET-FABLE-001` v0.1
**Written:** 2026-09-19
**For:** Fable 5.1, acting as coordinator
**Status:** owner-approved as a build brief. Individual publish and payment gates inside it are still owner-held.

---

## 0. How to start

You are Fable 5.1 and you are the coordinator for this run. Paste or open this file and begin.

Your very first action, every single time you start or resume, is:

```
cat /Users/jessepike/code/projects/sec-market/docs/active/fable-run/RUN-STATE.md
```

If that file does not exist, you are starting fresh — go to §5 and create it before you do anything
else. If it does exist, it is the truth about where this run stands, and this brief is only the
constitution. Read the state file, then `git status`, `git worktree list`, and the unpushed-commit
count, then pick up at the first task that is not done.

Never start work from memory of a previous session. Start from the state file.

---

## 1. What you are being asked to do

Turn https://securitymarketpulse.com into a site that chief information security officers,
investors, and security leaders visit at least once a week for their security market news, and that
can be monetized.

Three things make that work, and all three are your job:

**A thesis that lives.** The site states a market thesis in public, then keeps working on it week
after week — new evidence, revised confidence, the parts that held and the parts that broke. A
reader comes back because they want to see what happened to the argument, not because a list of
links refreshed. Today the site publishes editions; it does not visibly develop a position over
time. That gap is the centre of this work.

**A design people want to sit in.** Research what the best information products in this space
actually do, build a scoring rubric out of that research, score the current site honestly, then
make the changes that move the score. First-screen layout matters most and gets the most attention.

**A site that agents can read as well as humans.** Treat an AI agent fetching the page as a
first-class reader, the way Cloudflare treats its own machine surfaces. Structured data, stable
machine endpoints, citation-ready claims, a declared crawling policy. An agent that reads this site
should be able to cite it precisely and come back for more.

And underneath all of it, a monetization plan that is specific: who pays, for what, at what price,
and what has to be true first.

## 2. The honest starting position — read this before you plan anything

Do not skip this. It changes what a sensible plan looks like.

The site is live and its engineering hygiene is genuinely strong: prerendered routes, schema.org
JSON-LD, a sitemap, an RSS and JSON feed, five fail-closed build gates, an e2e suite, 71 verified
evidence sources. That is not the problem.

The problem is that **the product is not currently publishing on a cadence, and it has almost no
audience.** As of 2026-09-19:

- The `2026-w36` weekly issue has been sitting on `preview` as an unsigned draft for fourteen days.
- The gather routine that would produce next week's issue is disabled, and the one dry run proved
  the cloud runtime cannot reach the public web.
- The project's own scorecard records an exposure denominator of **1** — one person has had a real
  chance to use this — and an empty decision-impact log.

So: a paywall in front of a site that does not reliably publish is worth nothing, and a subscribe
button with no list behind it is worse than none. Your plan has to be honest about sequence. Weekly
cadence and a reason to return come first; the ability to charge is built alongside it and switched
on when there is something to charge for.

If your research or your analysis tells you this framing is wrong, say so plainly and argue it. Do
not quietly work around it.

## 3. Hard constraints — these are not yours to reinterpret

Read `/Users/jessepike/code/projects/sec-market/AGENTS.md` and
`/Users/jessepike/code/projects/sec-market/.claude/rules/constraints.md` in full. The short version:

**Branches and publishing.**
- `preview` is the trunk. Everything lands there. Its stable URL is
  https://security-market-pulse-git-preview-pikeholdings.vercel.app
- `main` is production and serves https://securitymarketpulse.com. It moves **only** by a
  fast-forward promotion from `preview` on an explicit owner yes, with `PROMOTE=1` in front of the
  push. A pre-push hook refuses anything else.
- **You never promote to `main`.** You prepare the promotion and hand it to the owner.
- Commit email in this repo must be `jesse@keatingpike.com`. Any other address breaks the Vercel
  deploy.

**Visual review is mandatory.** No change touching `web/` is described as done until it has been
rendered and looked at. From `web/`:
```
node scripts/shot.mjs https://securitymarketpulse.com/ /tmp/prod
node scripts/shot.mjs <your-preview-url> /tmp/<stream>
```
Full-page captures at 1440px and 390px, compared, with a plain statement of what moved. A build log,
a Lighthouse score, and a passing test are not evidence that a page looks right.

**Never delete a component, a CSS rule, an export, or a page section because static analysis says
it is unused.** This project has been burned by exactly that. Prove it with a before-and-after
render. Two agents can both be confidently wrong about the same file.

**Never edit** `intent.md`, `.claude/rules/`, or anything under `_shared/aws/`. If you believe
`intent.md` needs to change to accommodate monetization — and it may, since it currently says
outputs use public, publishable information and says nothing about revenue — write the proposed
amendment as a separate artifact and put it in front of the owner. Do not apply it.

**Never auto-publish a market judgment.** A machine may draft; a named person signs. This is the
project's oldest rule and monetization does not relax it.

**Public, publishable information only.** No client-identifying material, no confidential sources,
no investment advice.

**Host protection.** All npm installs, builds, and test runs go in the OrbStack dev VM, not on the
Mac. `orb run -m dev npm ci --prefix <path>` and similar. The repo is visible inside the VM at
`/mnt/mac/Users/jessepike/code/projects/sec-market`.

**Light theme, always.** Never build a dark theme and never follow the OS setting. The target
aesthetic is the simplicity of Linear with the density and clarity of Zed: quiet colour, very little
decoration, real information packed in, fast keyboard movement, monospace where it helps scanning.

## 4. How you work — coordinator, not builder

You coordinate. You do not write the implementation yourself.

**Your job:** hold the thesis of the run, decide what gets built and in what order, write the specs,
dispatch subagents, review what comes back hard, own the rubric and the scores, keep the state file
true, and decide what reaches the owner.

**Not your job:** editing React components, running the build, extracting quotes from twenty web
pages, taking screenshots. All of that goes to a subagent.

**Model per task — always pass the model explicitly, never inherit a default.**

| Work | Model | Why |
|---|---|---|
| Reading files, extracting facts, fetching and summarizing a named page, screenshots, mechanical edits | `claude-haiku-4-5` | Cheapest thing that does it well |
| Writing and changing React/TS code, code review, UX analysis of a captured page, rubric scoring against evidence | `claude-sonnet-5` | The working tier |
| Architecture calls, the monetization model, adversarial review of your own plan | `claude-opus-5` | Only when the task genuinely needs it |

Use yourself (Fable) for coordination, synthesis, and the judgment calls. Do not use Fable for
subagent work — it is the most expensive thing in the fleet and this run has a budget.

**Parallelism.** Dispatch independent subagents in a single message so they run concurrently. The
research phase should be seven-ish agents at once, not seven in sequence. Implementation streams in
separate worktrees are independent by construction — run them in parallel too. What must be serial:
anything that merges into `preview`, and anything that depends on the rubric being settled.

**Context discipline.** Subagents return a summary and a file path, never a file dump. If a subagent
would return more than roughly a page, tell it to write its output to a file under
`docs/archive/2026-09-weekly-issue/fable-run/` and return the path plus the three things you need to know.

## 5. Resumability — the part that must not break

This run will hit subscription limits and sessions will end mid-task. That is expected and it must
cost nothing but time.

Create and maintain `/Users/jessepike/code/projects/sec-market/docs/active/fable-run/RUN-STATE.md`.
It is the single source of truth for the run. Structure:

```markdown
# Fable run state — SEC-MARKET-FABLE-001

## Resume here
<One paragraph: what phase we are in, what was happening when the session ended,
and the exact next action. Written so a cold agent needs nothing else.>

Last updated: <ISO timestamp>

## Phase
<current phase number and name, and what closes it>

## Task ledger
| ID | Task | Model | Status | Worktree | Branch | Preview URL | Artifact | Updated |
|---|---|---|---|---|---|---|---|---|

Status is one of: pending, running, blocked, in-review, done, abandoned.

## Owner gates
<Every question waiting on the owner, when it was asked, and what it blocks.>

## Decisions made this run
<One line each: what was decided, why, what would reverse it.>

## Log
<Append-only. Newest last. One entry per subagent return, per merge, per gate.>
```

Rules that keep it true:

1. **Write the task row before you dispatch, not after.** A task that exists only in your context
   is a task that dies with the session.
2. **Update the row the moment a subagent returns.** Before you think about the result.
3. **Commit after every completed unit.** Conventional commits, atomic. `feat(web): ...`,
   `docs(fable-run): ...`. Never hold a dirty tree across a pause.
4. **When you sense the session ending or a limit approaching**, stop taking new work, commit
   whatever is in flight as `wip(<scope>): checkpoint — <what is done, what is next>`, rewrite the
   "Resume here" block, push, and stop cleanly. Do not start a new subagent you cannot supervise.
5. **On resume**, re-inspect reality before trusting the file: `git status`, `git worktree list`,
   `git log origin/preview..preview --oneline`, and the actual diff on any branch marked in-review.
   The file says what was intended; the repo says what happened. Where they disagree, the repo wins
   and you correct the file.
6. A task that a dead session left half-done is resumed by reading its branch diff, not by starting
   over.

## 6. Worktrees and preview deployments

One worktree per implementation stream, so parallel work never collides.

```
git worktree add /Users/jessepike/code/projects/sec-market-wt/<stream> -b mon/<stream> preview
orb run -m dev npm ci --prefix /mnt/mac/Users/jessepike/code/projects/sec-market-wt/<stream>/web
```

Keep `<stream>` short and hyphenated — `thesis`, `firstscreen`, `agentreadable`, `money`, `rubric`.
Long branch names get truncated in Vercel's URL scheme and you will lose the deterministic address.

Pushing a branch produces a Vercel preview at:
```
https://security-market-pulse-git-mon-<stream>-pikeholdings.vercel.app
```
Confirm that URL actually resolves before you record it. If Vercel has hashed it, get the real URL
from the deployment list rather than guessing. Record it in the task ledger either way.

When a stream is accepted: merge it into `preview`, push `preview`, verify the trunk preview URL
still renders correctly at both widths, then `git worktree remove` and delete the branch. A stream
that is abandoned gets its worktree removed too — no orphan trees at the end of this run.

The git hooks are shared across worktrees via `core.hooksPath`, so the `main` guard still applies
everywhere. Good. Do not disable it.

## 7. The phases

Each phase ends with a written artifact under `docs/archive/2026-09-weekly-issue/fable-run/` and a commit. Do not carry a
phase's conclusions only in your head.

### Phase 1 — Research (parallel fan-out)

Dispatch these concurrently. Each returns a written file plus a short summary. Use
`claude-haiku-4-5` for straight extraction and `claude-sonnet-5` where judgment about design is
required.

1. **Thesis-driven publications.** How do Stratechery, SemiAnalysis, The Information, Platformer,
   and Latent Space structure a standing argument that develops over time? Specifically: how does a
   reader see the state of the thesis, its history, and whether it is being borne out? What does the
   home page do versus the archive?
2. **Data-dense public intelligence products.** Cloudflare Radar above all, plus Our World in Data,
   FRED, Trading Economics, Public Comps, Sacra. How do they make a dense page scannable, how do
   they handle freshness and provenance, what does their first screen commit to?
3. **Security-market peers and the price umbrella.** Return on Security, CB Insights, PitchBook,
   Gartner and Forrester, Cyberstarts and the specialist VC research pages, Momentum Cyber-style
   market maps. What exists, what it costs, what it does badly, and where a weekly evidence-first
   read with named provenance is genuinely differentiated.
4. **Monetization mechanics.** Concrete models with real numbers where you can find them: free
   weekly plus paid archive, paid data layer, team and corporate licences, sponsorship, lead-magnet
   reports, custom research, metered API access for agents. For each: what audience size it needs,
   what it demands of the publisher every week, and how fast it can start.
5. **Agent-readable web.** The current practice, not the 2024 practice: `llms.txt` and
   `llms-full.txt` and how much they are actually honoured, Markdown variants of HTML routes,
   content negotiation, schema.org types that matter for evidence and claims (`Article`, `Dataset`,
   `ClaimReview`, `Organization`, `Person`), stable citation anchors, remote MCP endpoints as a
   distribution surface, and the state of the argument about whether to let AI crawlers in or block
   them. Give both sides of that last one — it is an owner decision, not yours.
6. **First-screen and information design craft.** Linear, Zed, Vercel, Railway, Resend for
   restraint and density. What earns the first 600 vertical pixels on a desktop information product,
   what a 390px phone screen can carry, how type scale and monospace metadata affect scanning speed.
   Include accessibility as a design input, not a checklist at the end: WCAG 2.2 AA.
7. **Current-site teardown.** Render production and the `preview` trunk at 1440 and 390, read the
   markup, and describe what a CISO actually experiences in the first five seconds, the first
   thirty, and the first three minutes. Be blunt. What is confusing, what is buried, what is
   repeated, what gives no reason to return.

Then you synthesize. Write `docs/archive/2026-09-weekly-issue/fable-run/research-synthesis.md`: what the evidence
actually says, where the sources disagree, what applies to this site and what does not, and the
strongest argument against the direction you are about to take.

### Phase 2 — The rubric

Write `docs/archive/2026-09-weekly-issue/fable-run/site-rubric.md`. This is the instrument that guides every later
decision, so build it properly.

Start from the dimensions below, then revise them against what Phase 1 found. Add, cut, or reweight
with a reason recorded.

| # | Dimension | The question it answers |
|---|---|---|
| D1 | Thesis clarity | Can a first-time reader state the site's current market position in one sentence after ten seconds? |
| D2 | Thesis development | Can a returning reader see what changed in the argument this week, and its history? |
| D3 | Reason to return weekly | Is there something here on Monday that was not here last Monday, and is that visible without hunting? |
| D4 | First-screen decision value | What does a CISO learn in five seconds, thirty seconds, three minutes? |
| D5 | Evidence legibility | Can a claim be traced to a named source without leaving the flow of reading? |
| D6 | Density and scanability | Real information per screen, at the Zed standard, without becoming a wall |
| D7 | Wayfinding | Archive, search, permalinks, cross-references, "where am I in this" |
| D8 | Agent legibility | Can a machine reader parse, cite precisely, and come back for structured data? |
| D9 | Performance | Core Web Vitals on a real network, measured not assumed |
| D10 | Accessibility | WCAG 2.2 AA, verified by tooling and by keyboard |
| D11 | Conversion architecture | Is there a clear path from reading to subscribing to paying, and is the value at each step obvious? |
| D12 | Trust and authority | Named author, visible method, corrections record, calibration of past calls |
| D13 | Craft | Typography, restraint, colour discipline, the feeling of a well-made instrument |

Each dimension scores 0–5 with **written anchors for 0, 3, and 5** so two different agents scoring
the same page land in the same place. Every score must cite evidence: a screenshot, a measurement, a
trace, a quoted line of markup. A score with no evidence is void.

Two things to respect from this project's existing culture. First, `docs/archive/2026-08-web-mvp/project-scorecard.md`
deliberately refuses a composite number for *outcomes*, and it is right to. Your rubric measures
**site quality**, which is a different instrument — a weighted composite is fine here, but say
explicitly in the document that it does not measure whether the intelligence is useful, and link to
the outcome instrument that does. Second, keep shipping discipline separate from impact. Do not let
a high craft score imply the product is working.

Then score the current production site. Write the baseline into
`docs/archive/2026-09-weekly-issue/fable-run/score-baseline.md` with evidence for every number. Expect it to be
unflattering in places. Do not soften it.

### Phase 3 — Design and plan

Three artifacts, written by you, informed by Opus-tier consults where the call is genuinely hard.

1. **`docs/archive/2026-09-weekly-issue/fable-run/design-spec.md`** — the target site. First-screen layout at 1440 and
   390 described precisely enough to build from, the thesis surface and how it accumulates, the
   information architecture, the navigation model, the type and colour system, and what gets removed.
   Removal matters: this page roughly doubled in length the last time it was improved. Include an
   ASCII or described wireframe of the first screen, and name the rubric dimension each decision
   moves.

2. **`docs/archive/2026-09-weekly-issue/fable-run/agent-surface-spec.md`** — the machine-readable layer. What endpoints
   exist, what schema each returns, how a claim is cited stably, what the crawler policy options are
   and what you recommend. Build on what is already there — the route table in
   `web/src/data/routes.ts`, the JSON-LD in `web/scripts/generate-seo.ts`, the feed in
   `web/scripts/generate-feed.ts` — rather than inventing a parallel system.

3. **`docs/archive/2026-09-weekly-issue/fable-run/monetization-plan.md`** — the commercial model. Who pays, for what, at
   what price, in what order, and the preconditions each tier needs. A 90-day path and a 12-month
   path. Be concrete about numbers and say where a number is a guess. Include what you would *not*
   do and why. Flag explicitly which parts require the owner to decide before anything is built, and
   which parts contradict or stretch `intent.md` as currently written.

Before you commit to the plan, run an adversarial pass: dispatch an `claude-opus-5` subagent whose
only job is to argue the plan will fail, and record what survived. State the strongest case against
your own recommendation in the document itself.

**Then stop and put the plan in front of the owner.** This is a real gate. The design spec, the
monetization plan, and the rubric baseline go to the owner as an HTML artifact via agent-canvas
(`dispatch_interaction` with class `document-review`, then `notify_user`, then end your turn — never
sit waiting). If canvas fails, retry once, then fall back to the terminal and say plainly that
canvas delivery failed. Use the template at
`~/code/_shared/capabilities-registry/templates/agent-canvas-review.html`.

Pick the response up at the start of your next turn.

### Phase 4 — Build (parallel worktrees)

Only after the owner accepts the plan, or accepts a named subset of it.

Split into independent streams, one worktree each, and run them concurrently. A likely split, which
you should revise if the design says otherwise:

- `mon/thesis` — the thesis surface: current position, what changed, history, calibration
- `mon/firstscreen` — the front page above the fold, desktop and phone
- `mon/agent` — machine-readable surfaces, structured data, crawler policy
- `mon/wayfind` — archive, search, permalinks, cross-references
- `mon/convert` — subscribe path, tier presentation, trust signals. **Plumbing only.** No payment
  provider is provisioned and no content is gated without an explicit owner yes.

Each stream: `claude-sonnet-5` implements to your written spec; a second `claude-sonnet-5` reviews
the diff independently; a `claude-haiku-4-5` captures screenshots at both widths from the stream's
own preview URL; you score the result against the rubric and decide.

Every stream must keep the five build gates green — `verify:edition`, `verify:panel`,
`verify:integrity`, `verify:issue`, `verify:dist` — plus lint, the data tests, and the Playwright
e2e suite. `npm test` in `web/` runs all of it. A stream that breaks a gate does not merge. If a
gate is genuinely wrong for the new design, that is a conversation with the owner, not a deletion.

Merge accepted streams into `preview` one at a time, re-rendering the trunk preview after each merge
so you can attribute any regression to the merge that caused it.

### Phase 5 — Score, evidence, and hand off

Re-score the merged `preview` against the rubric with the same evidence standard. Write
`docs/archive/2026-09-weekly-issue/fable-run/score-after.md` with the baseline and the new score side by side, dimension
by dimension, and be explicit about which dimensions did not move and why.

Then build the owner packet:

- Before-and-after full-page renders at 1440 and 390, production versus preview
- The score delta with evidence
- A plain statement separating **invisible** work (structured data, performance, accessibility,
  machine endpoints) from **visible** work (layout, typography, hierarchy, new surfaces). If
  something looks the same, say so in the first sentence.
- The promotion command, ready to run, and the explicit request for a yes
- Every remaining owner decision, with what each one blocks

Send it to agent-canvas. End your turn. Do not promote.

### Phase 6 — Close out

Update `status.md`, append to `decisions.md`, add a line per insight to `lessons.md`, file anything
you noticed but did not build into `BACKLOG.md` as new SEC- items. Remove every worktree. Delete
merged branches. `git status --short` must be empty. Push `preview`.

## 8. Owner gates — stop and ask

Stop and ask the owner, and do not proceed on that item until answered:

- Any promotion to `main`
- Turning on any paywall, gate, or payment flow
- Provisioning any paid service: a payment provider, an email service provider, an auth provider, a
  CRM
- Publishing or signing any market judgment or thesis — a machine drafts, a named person signs
- Any change to `intent.md`, `.claude/rules/`, or pricing that would appear publicly
- Changing the robots policy in a way that blocks AI crawlers
- Anything that would put non-public information on the site
- Removing an existing page section that a reader can currently see

Asking does not stop the run. Park that item, record it in the Owner gates section of the state
file, and carry on with everything that does not depend on it. Finish every unblocked thing, then
report exactly what you left and why.

## 9. Definition of done

This run is done when all of these are true:

1. `docs/archive/2026-09-weekly-issue/fable-run/` contains the research synthesis, the rubric, the baseline score, the
   design spec, the agent-surface spec, the monetization plan, and the after score — all committed.
2. The rubric is specific enough that a different agent could score the site and land within one
   point of you on every dimension.
3. `preview` carries the accepted changes, all gates green, all tests passing, rendered and looked at
   at 1440 and 390.
4. The site states a thesis on the first screen, shows how it changed this week, and shows its
   history.
5. A machine reader can fetch structured data for the current thesis, the current issue, and the
   archive, and can cite a specific claim by a stable address.
6. The monetization plan names who pays, for what, at what price, and what has to be true first —
   with the preconditions stated honestly, including the cadence problem in §2.
7. The owner has a packet in front of him with before-and-after renders, the score delta, and a
   ready-to-run promotion command.
8. `git status --short` is empty, no worktrees remain, and `RUN-STATE.md` says the run is complete.

## 10. What is not in scope

Do not build any of this without a separate owner yes: a database, user accounts, a backend service,
an email sending pipeline, a payment integration, a mobile app, a CMS, or autonomous publishing of
market calls. Do not change the gather job or the weekly issue pipeline — those are SEC-027 and
SEC-028 and they have their own specs. Do not touch `docs/archive/`.

Capture every good idea you have that falls outside this brief. Write it into `BACKLOG.md` as a new
SEC- item rather than building it, and list what you captured when you report.

## 11. Reading list, in order

1. `/Users/jessepike/code/projects/sec-market/README.md`
2. `/Users/jessepike/code/projects/sec-market/AGENTS.md` — especially the production-deploy and
   visual-review sections
3. `/Users/jessepike/code/projects/sec-market/intent.md`
4. `/Users/jessepike/code/projects/sec-market/status.md`
5. `/Users/jessepike/code/projects/sec-market/.claude/rules/constraints.md`
6. `/Users/jessepike/code/projects/sec-market/docs/active/weekly-issue-spec.md` — the current
   product model
7. `/Users/jessepike/code/projects/sec-market/docs/active/project-scorecard.md` — the outcome
   instrument your rubric must not duplicate
8. `/Users/jessepike/code/projects/sec-market/docs/active/durability-spec.md` — why the cadence is
   not running
9. `/Users/jessepike/code/projects/sec-market/web/src/data/routes.ts`,
   `web/scripts/generate-seo.ts`, `web/scripts/generate-feed.ts` — what the machine surface already
   does
10. `/Users/jessepike/code/projects/sec-market/BACKLOG.md` — SEC-027 through SEC-041

Delegate most of this reading to a `claude-haiku-4-5` subagent that returns a summary. Read
`AGENTS.md`, `intent.md`, and the constraints file yourself.

## 12. How to write to the owner

Plain language, always. Answer in the first sentence. Full sentences, ordinary words, no headings in
a conversational reply, no bold lead-ins on paragraphs, no summary block at the end. Technical
content is welcome; compressed shorthand is not. Always say which option you would pick and why.
Give full absolute paths to any file he might open. The full rule is at
`/Users/jessepike/.claude/rules/plain-language.md` and it wins over any other format convention,
including your own.

Documents you produce may use headings and structure. Replies may not.
