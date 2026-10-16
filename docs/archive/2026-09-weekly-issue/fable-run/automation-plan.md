# Automation and durability plan

Task T5-1, run SEC-MARKET-FABLE-001. Read-only against the repository except for this file. Every
claim about current behavior below names the file and line I checked it against. Anything inferred
rather than read directly is labeled as an estimate or inference.

## 1. How it works today

The chain runs from a public document to a published page in nine steps. Three are automated, three
are manual by design, and one is broken.

1. **Public sources exist on the open web.** Return on Security, SEC EDGAR, SecurityWeek, named VC
   pages, and issuer investor-relations pages. Nothing to automate here; this is the input.

2. **A gather routine is supposed to fetch them on a schedule and draft a pull request.** Specified in
   `docs/archive/2026-09-weekly-issue/gather-job-spec.md` (`SEC-MARKET-GATHER-001` v0.2) and `docs/archive/2026-09-weekly-issue/gather-brief.md`
   v0.2: a Claude Code cloud routine, model `claude-sonnet-5`, firing Tuesdays 06:00 Pacific
   (`gather-job-spec.md` lines 27-33). **Status: broken.** The routine
   (`trig_01VeQpLYzXjccqKeSFS1Xgo6`) exists but is disabled (`BACKLOG.md` line 117). A dry run on
   2026-09-05 proved why: the cloud environment's egress proxy returns 403 on every outbound host
   outside a small default allowlist, so Return on Security, SEC.gov, SecurityWeek, Cybersecurity
   Ventures and even a control host were all unreachable (`status.md` line 141, confirmed by
   `git show --stat` on branch `origin/issue/2026-w35-dryrun`, commit `13ade8b`, whose message states
   "every source in the fixed manifest was unreachable" with zero evidence gathered). The mechanics
   worked. The network did not.

3. **In place of the schedule, a person starts an agent by hand to do the same job.** This is exactly
   the manual step the owner said he cannot have, and it happened again today: branch
   `origin/issue/2026-w37`, commit `7647baa`, authored 2026-09-20 00:44 local time under the owner's
   git identity with `Co-Authored-By: Claude Opus 5 (1M context)`. It drafted eleven real items with
   sha256 receipts and all gates green, but it is manual, not scheduled, and it used Opus 5 rather
   than the spec'd Sonnet 5, a real drift from both the spec and the model-tier rule that
   gather-and-draft work belongs on Sonnet.

4. **Build gates run automatically on every push.** `web/vercel.json` line 4 sets
   `"buildCommand": "npm run build"`, and `web/package.json`'s `build` script chains
   `verify:edition && verify:panel && verify:integrity && verify:issue && tsc -b && ... && verify:dist`
   on every Vercel deploy of `preview` and `main`, no human step. `verify:integrity`
   (`web/scripts/verify-integrity.ts`, spec `docs/archive/2026-08-web-mvp/integrity-pass-spec.md`) and `verify:issue`
   (`web/scripts/verify-issue.ts`, 1016 lines, fifteen checks in `weekly-issue-spec.md` §6 and its
   four amendment rounds) already check that every fact's evidence id resolves to a real record, every
   date falls inside the window, and every number in a headline or "why" appears verbatim in a cited
   excerpt (check 12). Real, working, automated validation.

5. **A published issue is locked against silent rewriting.** `issues.lock.json` holds one sha256 hash
   per published issue id (I read it directly: one entry, `"2026-w36"`). Check 8 in `verify-issue.ts`
   compares this against two independent anchors, the git parent commits and the live
   `/issues/lock.json` on production, per `weekly-issue-spec.md` lines 246-264. Automated.

6. **Signing is a manual, hand-edited step today.** `durability-spec.md` line 77 says it plainly: "the
   signer edits a TypeScript file by hand." `gather-job-spec.md` §6 (lines 105-121) specs a 20-30
   minute ritual: open the PR, cut anything thin, write `weThink` yourself, run
   `verify:issue -- --write`. For the one issue that has shipped, calendar time ran far longer than
   that: the draft was ready 2026-09-05 (D-65, `decisions.md` line 702) and the signature landed
   2026-09-19 (D-66, `decisions.md` line 731), fourteen days later. **Estimate, not hands-on time:**
   the review itself is likely still short; what took fourteen days is that nothing pushed the task
   back in front of the owner between those dates.

7. **Merging to `preview` and promoting to `main` are both manual, and deliberately so.**
   `.githooks/pre-push` refuses a direct push to `main` unless `PROMOTE=1` is set in the pusher's own
   shell (I read the hook: a plain environment-variable test in a `while read` loop over refs). D-66
   (`decisions.md` line 739) confirms this exact command moved `main` from `b423b70` to `aa04875`.
   This hook only runs on a machine that installed it; it never runs when GitHub itself performs a
   merge server-side, which matters for section 4 below.

8. **Nothing watches for a missed week.** No run-receipt check and no site-freshness probe exist
   today. Both are fully designed in `durability-spec.md` §4 but carry the status "not yet authorized"
   (`BACKLOG.md` SEC-039, line 509). If the Tuesday schedule silently failed to fire, or fired and
   found nothing, no one would be told. **Missing, by design gap rather than by oversight.** The
   design exists on paper and has simply not been built.

9. **No channel exists to notify the owner of anything.** I grepped the repository for Slack, Resend,
   SendGrid, Mailgun and webhook code; the only hits are research notes and open backlog items
   (`BACKLOG.md` line 443). Pilot email is still sent "by hand from the owner's mail"
   (`weekly-issue-plan.md` line 163); an email provider is a separate, unbuilt item, SEC-034.
   **Missing.**

## 2. Why it stalled

Four separate causes, not one.

First, the one runtime the built spec actually calls for cannot reach the public web. The gather job
is designed around a Claude Code cloud routine specifically because it needs no host and no runtime
install (`gather-job-spec.md` lines 24-26), and that same routine's egress proxy blocks every source
it needs to read. The design assumed a capability the environment does not currently grant.

Second, even once a draft exists, nothing tells the owner it is waiting. `product-core.md` line 84
quotes his non-negotiable bar, and the same document's open question 9 admits the channel question is
still open. A PR sitting on GitHub, unannounced, is indistinguishable from a PR that does not exist,
to someone who is not looking for it.

Third, the fixes for both of the above are designed but not authorized. `durability-spec.md` is a
complete proposal, dated 2026-09-07, and its own §12 lists four owner decisions still waiting.
`BACKLOG.md` records SEC-039 as "proposed... not yet authorized." The project did the design work and
stopped at the owner's own gate, correctly, since nothing here should ship without his yes.

Fourth, the two governing documents disagree on cadence: `gather-job-spec.md` (built and shipped) says
Tuesday 06:00 Pacific; `durability-spec.md` (proposed, unbuilt) proposes Sunday afternoon. Nobody has
reconciled that, so "when does this run" does not currently have one answer.

## 3. The target

The chain the owner described, stated as one flow. Everything past step 2 depends on the split in
section 5, which is not yet decided; where a step depends on that decision I say so.

1. A scheduled job fires on its own, no person starts it, reads the fixed source list, and drafts an
   issue exactly as `gather-brief.md` already specifies.
2. The existing gates run automatically and must pass first: evidence resolution, verbatim
   numeric-token matching, date-in-window, append-only history.
3. If the facts-versus-judgments split in section 5 is adopted, the four fact lanes that pass every
   gate publish on their own; if not, the whole draft waits for the owner, as today.
4. Either way, a short message drops into a channel he actually checks, on his own cadence: "Issue
   2026-wNN is drafted. Needs your read: [link]." He sees this without opening a terminal.
5. He taps once. The tap opens the pull request, on GitHub's own site or mobile app, and merges it
   into `preview`. That single action is the review.
6. Promotion to `main`, the act that changes the public site, stays a deliberate, separate act,
   ideally folded into the same weekly moment so it is one habit rather than two.
7. If he does not respond by the next check, nothing needing his judgment goes out; validated facts
   still publish if section 5 is adopted; the page itself states, in plain text, how many days old its
   newest signed judgment is, so a reader is never told a false story about freshness.
8. A separate, quiet channel message fires only when something is wrong: no draft appeared, or
   production has gone stale past a stated threshold. Not the same message as step 4.

## 4. Options for each moving part

### Where the scheduled job runs

**Cloud routine with an egress allowlist.** Already spec'd (`durability-spec.md` §3, lines 44-51) with
the exact host list and a one-off probe routine to test it before arming the schedule. Cost: $0
marginal, runs on the subscription. Risk: unproven, since the dry run already failed once, and the
spec names hosts (acquirer newsrooms discovered at run time) that cannot sit on a fixed allowlist and
will stay unreadable regardless. The spec's own decision rule: if the probe cannot pass within one
week of the allowlist change, stop and use the fallback (line 57).

**A local runner on macbook2014 or macmini, via launchd.** Also already spec'd (`durability-spec.md`
§3, `scripts/gather.sh` invoking `claude -p --model claude-sonnet-5`, lines 52-56), matching the
owner's stated preference for always-on Macs. Needs no allowlist negotiation, since home internet has
ordinary outbound access. I could not verify whether either host is currently reachable for a new
launchd job; section 7 covers this gap.

**GitHub Actions on a cron trigger, or Vercel Cron.** Neither is named in any spec here, and I do not
recommend either. A GitHub-hosted runner calling Claude would most likely need an API key rather than
the subscription, against the standing no-API-key rule; the site is also a fully static build with no
serverless functions (`vercel.json` has none today), so Vercel Cron would mean adding a function for
no benefit over the two options above.

**My recommendation:** follow the decision rule already written into `durability-spec.md` §3. Try the
cloud routine and allowlist first, because it is the cheapest to test and needs no host reachability
work. Give it the one-week window the spec already names. If it is not clean by then, move straight to
the local runner, which the owner already prefers as a default pattern.

### Which model runs the gather and the draft

`gather-job-spec.md` line 30 already specifies `claude-sonnet-5`, which matches the model-tier rule:
gather-and-draft is extraction and analysis, not architecture. The actual `2026-w37` draft used Opus 5
instead (commit `7647baa`), a real drift worth correcting, not repeating. Invocation without an API
key is already solved two ways, both subscription-based: the cloud routine runs on the Claude Code
subscription directly, and the local-runner fallback invokes `claude -p --model claude-sonnet-5` from
a repository checkout, per `~/code/_shared/agent-exec/docs/environment-tiers.md` line 40, "Programmatic
Claude calls: use `claude -p` (Max subscription)."

### How validation works, and what is missing

What already blocks publication, and works: every fact's evidence id must resolve to a real record;
every date must fall inside the stated window; every number in a headline or explanation must appear,
verbatim, in a cited excerpt (`weekly-issue-spec.md` check 12, sharpened twice more in amendments G2
and H2 against false positives like "M12" or "1Password"); published history cannot be silently
rewritten (check 8, two independent anchors). This is a strong set of gates and I recommend reusing all
of it rather than replacing any of it.

What is missing, honestly:

- **Source reachability at publish time, not just at fetch time.** A retrieval receipt records a
  sha256 of the bytes fetched (amendment F9), but nothing re-checks the source URL later. Recommend a
  weekly, alert-only check (not build-blocking) that re-fetches each cited `canonicalUrl` and flags a
  404 or a changed hash.
- **Cross-issue duplicate detection.** The brief tells the model to read the newest issue so it does
  not repeat itself (`gather-brief.md` §1 step 4), an instruction to a model, not a gate. I found no
  hard check catching the same round or filing reported in two separate issues. Worth a real gate:
  match company, amount and date across all published issues before a new one publishes.
- **Run-receipt and site-freshness probes.** Fully designed in `durability-spec.md` §4 and simply not
  built: a Sunday check that a draft PR exists, and a daily curl of production flagging staleness.
  Build exactly what is already specified rather than redesigning it.
- **Robots and source-terms compliance is instruction-only.** The brief tells the model the rules;
  nothing in the gates checks it followed them. With no history of a violation, I would not add a gate
  now, only note this rests on the model's discipline rather than on code.

### How the decision reaches him, and how a tap becomes a publish

Four channels, weighed honestly.

**A Slack incoming webhook, or email, posting a link.** Either is cheap (Slack is free at this volume;
an email provider is SEC-034's still-open choice), and neither needs a new backend: it is a one-way
notification, and the "tap" happens on GitHub's own site or mobile app, not inside the message. This
satisfies "drop into a channel" directly.

**True in-Slack or in-email one-tap buttons (an Approve action, not just a link).** This needs a live
endpoint to receive the click, which is new infrastructure the project has deliberately avoided so
far. Possible later as a small addition; not recommended as the first build.

**Agent-canvas.** This is the owner's own standing convention for review-gated artifacts, but by his
own rule it is meant for genuine reading content with a decision falling out of it, not a bare
approve/reject wrapped around nothing (`agent-canvas-collab.md`, "Stays in the terminal" section names
exactly this as the anti-pattern). It is also picked up "on the dispatching manager's next
invocation," which risks recreating the very thing the owner said he cannot have: something has to run
again to notice his answer. I recommend against using it for this recurring, thin decision, and
reserve it for a richer, one-off review if one is ever wanted.

**My recommendation:** a Slack incoming webhook, or email if he prefers no new Slack workspace,
carrying the PR link and a one-line summary; the tap itself is merging the pull request from the
GitHub mobile app. Zero new backend to build.

**How a tap becomes a publish, given the `PROMOTE=1` guard.** This needs care. The pre-push hook only
runs on a machine that has it installed; a merge performed by GitHub itself, from the phone, never
touches that hook at all. That means a phone-tap merge is safe for the PR's actual target,
`preview` (`gather-job-spec.md` line 41: "base `preview`"), because nothing in that path was ever
guarded. It is not safe, and was never designed to be safe, for `main`. Two honest options:

- **Minimal, no new build:** the phone tap merges the draft into `preview` only. Promotion to `main`
  stays a separate, deliberate, less-frequent laptop act, ideally folded into the same weekly moment.
- **Fuller, needs explicit owner sign-off because it touches the promotion contract in `AGENTS.md`:** a
  GitHub Action triggered by a PR comment such as "/promote," which itself runs
  `git checkout main && git merge --ff-only preview && PROMOTE=1 git push origin main` from a CI
  runner rather than the owner's laptop. This makes the loop phone-native, but changes who can promote
  from "a human at a keyboard" to "an authenticated GitHub comment," a real change to a rule the owner
  wrote deliberately to make promotion inconvenient. I would not build this without his explicit say-so.

I recommend the minimal option to start.

### What happens when he does not respond

Today, if he does not act, the draft simply sits unsigned, and the site keeps showing whatever last
published with no visible statement of how old that is. That silence is itself a defect against his
own bar in `product-core.md` line 86: "the site must be updated regularly and without fail... if that
can't happen, then it's worthless." I recommend one small, low-risk addition regardless of how the
facts-versus-judgments question resolves: a plain, permanent line on the front page stating how many
days old the newest signed issue is. If section 5 is adopted, validated facts keep publishing in his
silence; if not, nothing publishes, as today, and the honesty line keeps that silence from reading as
neglect.

### Monitoring and alerting when a job fails silently

`durability-spec.md` §4 already specifies this in full: a Sunday 22:00 UTC check that a draft PR
exists, and a daily 14:00 UTC curl of production's four key endpoints, both "bash and curl only, no
runtime installs" (line 73). Build exactly this, routed into the same channel as the weekly
notification above, so one place carries both "here is this week's draft" and "something is wrong."

## 5. The facts-versus-judgments split

This is still an open, undecided question (`product-core.md` line 131, item 8: "Open. Recommendation
in section 6"). What follows describes what would have to change if the owner accepts it. I have not
drafted any of the actual rule or intent text, as instructed.

**The issue data model** (`web/src/data/types.ts`, described in `weekly-issue-spec.md` §3) currently
gates an entire issue behind one signature: `weThink.signedBy` must equal `AUTHOR_NAME` before
anything in that issue counts as published. To let the four fact lanes publish independently of the
judgment block, the `Issue` type would need its lanes and its `weThink` block to carry separate
publication states, or the fact lanes would need to become their own feed, separate from the signed
issue. That is a real schema change, not a small one.

**The verify:issue gates** (`web/scripts/verify-issue.ts`) would need new logic. Check 5 currently
requires a full, signed `weThink` before any `status: 'published'` issue passes; a partial, facts-only
publish state does not exist today. More importantly, the gates would need to become the sole guard
against a bad fact reaching production with nobody looking, a much higher bar than catching most
errors before a human reviews the rest anyway.

**The lock manifest** (`issues.lock.json` and its two-anchor append-only check) currently treats a
published issue as one unit. A split model needs either two manifests, or one that can anchor a
fact-lane snapshot independently of the judgment snapshot.

**`intent.md` and `.claude/rules/constraints.md`** both read as a blanket rule today: "a machine may
retrieve, extract, compare and propose; only a named person signs or publishes" (`gather-job-spec.md`
line 11, quoting the intent), and constraints.md separately lists the "autonomous pipeline" as not
authorized. The split would need the owner to approve new language in both files distinguishing
"publishing a validated fact" from "signing a judgment." I am not proposing that language;
`product-core.md` §9 item 5 already names it as the amendment he would need to accept.

**The honest risk:** a wrong fact could publish under the owner's name with nobody looking. The kind
of error that slips past a verbatim-quote gate is exactly the kind a human catches and a mechanical
check does not: a filing later restated, an EDGAR match on a similarly-named but wrong company, a
document correctly hashed and quoted but wrongly interpreted. The product's entire value is
credibility (`product-core.md` line 20, "a credibility asset"), so one such error costs more than the
convenience saves.

**Safeguards that would make it acceptable, if the owner decides to proceed:** keep every existing gate
exactly as strict as today; add the source-reachability re-check named above so a fact does not
publish on a since-retracted source; add a short cool-down window between a fact passing every gate
and it appearing on the page, so the owner has a standing chance to catch something without an active
review step; and mark an auto-published fact with its own permanent label, distinct from a signed
judgment's, so a reader always knows which kind of claim they are looking at. The provenance rail
already distinguishes two kinds of claims (`integrity-pass-spec.md` §2, item 2); extending what it
labels is a small change to something that exists, not new machinery.

## 6. Build order

**Step 0, smallest possible, no schema change.** Post a message to a channel whenever the gather PR
opens: "Issue drafted, needs your read: [link]." This alone converts "I have to fire up an agent" into
"something dropped into a channel," even before the schedule is fixed, since it can announce the
already-working manual gather too. Agent-hours: about 2, for a GitHub Action that runs `curl` against
a webhook on PR-opened, no model call. Owner-minutes: about 10, to create the Slack webhook (or choose
an email address) and save it as a repository secret. **Owner must provide:** the webhook URL, or a
destination email address and provider credential.

**Step 1, fix the runtime.** Try the cloud-routine allowlist first per the spec's own one-week rule;
fall back to the local runner if it is not clean by then. Agent-hours: 2-4 for the allowlist attempt
and probe, 2 more for the local-runner script if the fallback is needed. Owner-minutes: about 15, to
add hosts at the environment settings page, which only he can authorize. **Owner must provide:** access
to `https://claude.ai/code/environments`, or confirmation that macbook2014 or macmini can run a new
launchd job today.

**Step 2, arm the schedule and build the two probes.** Reconcile the Tuesday-versus-Sunday cadence
conflict with one owner decision, then build the run-receipt and site-freshness probes from
`durability-spec.md` §4, routed to the Step 0 channel. Agent-hours: 3-5. Owner-minutes: about 5.

**Step 3, build the sign script.** `npm run sign -- <id>` per `durability-spec.md` §5, replacing the
hand-edited file with a short checklist and a small `<id>-sign.md` input. Agent-hours: about 3. No
change to owner time, but less room for a mistake.

**Step 4, the phone-tap flow.** No new build: confirm that merging the draft PR from the GitHub mobile
app, into `preview` only, is the whole action. Promotion to `main` stays separate. Agent-hours: near 0.

**Step 5, close the two gate gaps.** Add cross-issue duplicate detection and the periodic
evidence-link liveness check named in section 4. Agent-hours: 4-6.

**Step 6, only after four consecutive good weeks** (the project's own bar, `weekly-issue-plan.md` line
207). Revisit the facts-versus-judgments split as its own decision, with `intent.md` and
`constraints.md` amendment proposals for the owner, not built ahead of that review.

**Everything the owner alone must provide, gathered in one place:** the Slack webhook URL or an email
provider credential; access to edit the Claude Code cloud environment's egress allowlist; a decision on
whether macbook2014 or macmini can host a new launchd job right now; the Tuesday-versus-Sunday cadence
choice; the decision to arm the schedule; approval of spend beyond the ten-to-twenty-dollar target;
and, later, his review of any proposed `intent.md` or `constraints.md` language for the split.

## 7. What I could not determine

- Whether macbook2014 or macmini can host a new launchd job today. My only measurement is
  `~/code/_shared/agent-exec/docs/infrastructure.md`, dated 2026-08-02, which found neither host
  answering SSH on port 22, and I was told not to attempt SSH myself.
- Whether the Claude Code cloud environment's egress allowlist can be scoped precisely enough,
  including hosts discovered at run time, which `durability-spec.md` §3 already expects will stay
  unreadable regardless.
- The actual dollar cost of an email provider or of Slack past its free tier at this volume; pricing
  messaging providers was outside this task's scope.
- Whether merging a pull request from the GitHub mobile app on this repository behaves the way I have
  assumed; I read the hook and the promotion contract but did not test an actual mobile merge.
- Whether jobs-agent can currently reach macbook2014 to register a new launchd job, the same gap.
- Whether a weekly gather run at Sonnet-5 or Opus-5 tier would hit any subscription rate or quota
  ceiling; the no-API-key rule rules out per-call dollar cost but not a usage limit.
