# Decision map — Security Market Pulse

**Written by:** the run coordinator, 2026-09-20, at the owner's request.
**What this is:** the whole effort sorted into seven buckets. Each bucket has the questions we are
trying to answer, what we already know, what I recommend, what still needs research, and who has
to act. Section 9 puts them in order. Nothing here is decided; it is a map for steering.

**Where the detail lives:** every file named below is under
`/Users/jessepike/code/projects/sec-market/docs/active/fable-run/`.

## 0. Why this run stopped, and what I would change

You asked for an end-to-end run and it stopped at the plan. Two causes, and only one of them was
necessary.

The necessary one: the brief and your kickoff both made Phase 3 a hard stop, and they were right
to, because the plan turned out to disagree with the brief in two places (the size of the build,
and the pre-built commercial plumbing).

The unnecessary one is mine. The packet asks you for about twenty decisions. Most of them are
design choices where I have a clear recommendation and you lose nothing if I simply act on it and
show you the result on a preview. Only a handful truly need you, because they are either things
only you can do or things the brief reserves for you. Section 8 separates the two lists. If you
accept that split, the run can go back to being end to end: one yes from you, then a preview to
look at.

There is also a scoping problem the run inherited. The brief told me not to touch the gather job
or the weekly issue pipeline. Those are exactly the things that decide whether the site stays
alive (bucket 2). So the run was pointed at presentation while the binding problem sat outside
its fence. That is worth fixing on purpose, not by accident.

## 1. Purpose and intent

**The questions**

- What is this site for, in one sentence you would say out loud? A credibility asset for your
  advisory work, a publication in its own right, the start of a business, or a research
  instrument for your own thinking?
- Who is the reader you would be proud to have? Security leaders and the teams who advise them
  (what `intent.md` says today), or also investors (what the kickoff for this run said)?
- What does success look like in twelve months, in terms you could check? Readers, decisions
  changed, conversations started, revenue, or reputation?
- How much of your own time per week is this worth, permanently? A named person has to sign every
  judgment, so your weekly hour is the real ceiling on everything else.
- Is earning money from it a goal, a nice-to-have, or a distraction? `intent.md` is silent on
  revenue, so today it is neither allowed nor forbidden.
- How does this sit beside your job? Same market, your name on it.

**What we know.** `intent.md` v1.2 names security leadership, account teams and clients as the
people it serves, excludes investment advice, and says the project must not optimize for traffic.
The kickoff for this run added investors and monetization. Those two documents pull in different
directions, and I built the plan on the intent file where they disagreed. You are reading the
monetization plan and feeling we are not aligned. I think that feeling is this gap.

**Recommendation.** Hold the separate high-altitude session you described, before any more
monetization work and before wave 2 of the design. Use the six questions above as its agenda. Its
output is either "intent v1.2 stands" or a proposed v1.3 that you approve. Everything in buckets
4, 5 and 6 should be re-read against that answer. The `advisor` agent is built for this kind of
session; a plain session in this repository with this file as its opening brief works as well.

**Still to understand.** Nothing that research can answer. These are your calls.

**Who acts.** You.

## 2. Durability and updating: does the site stay alive?

**The questions**

- Can the evidence for a weekly issue be gathered without you fetching things by hand?
- Where should that gathering run? The cloud routine cannot reach the public web; its one dry run
  proved that. The choices under SEC-039 are to get the cloud environment allowlisted or to run
  locally.
- How long does it take you to go from a machine draft to a signed issue, and is that a slot you
  can hold every week?
- What happens on the site when an issue is late or a week is skipped? Today nothing says so.
- What is the honest cadence to promise? Weekly, most weeks, or fortnightly?

**What we know.** One issue has been signed, thirteen days after its week ended. A draft of the
second, `2026-w37`, exists on the branch `issue/2026-w37`, made by another session. The gather
routine is disabled. The site currently says "Not a weekly news cycle" in one place while
presenting a numbered weekly issue in another. My rubric takes points away automatically if
fourteen days pass without a new issue, from 2026-10-04.

**Recommendation.** Treat this as the first priority of the whole project, ahead of design. Make
the runtime decision this week: hold the one-week deadline on the cloud allowlist, and if the
probe fails, run locally and delete the cloud routine. Get `2026-w37` signed. Pick a cadence you
will actually keep and let me put that one sentence on the site.

**Still to understand.** This run never examined the gather job or the signing workflow, because
the brief fenced them off. I do not know how long signing takes you, where the draft pipeline
breaks, or whether a local runner is reliable. That is a real gap. If you lift the fence, I can
run that investigation end to end and come back with a working recommendation, not a question.

**Who acts.** You decide the runtime and sign issues. I can do the investigation and the build if
you widen the scope.

## 3. Audience and exposure: is anyone reading?

**The questions**

- Who are the first ten to thirty people who should see this every week?
- How do they get it? They will not visit a website unprompted every week.
- How do we know it changed anything for them?
- When does public email open? It is held until four issues have been published on schedule and
  the review on 2026-10-08.

**What we know.** The project's own scorecard records that one person has had a real chance to use
this work and that no decision is recorded as changed. No design work moves either number. The
feed exists and nothing visible links to it.

**Recommendation.** Name ten to fifteen people this week and send them the signed issues
personally until email opens. Ask two of them what they did with it. That is worth more than any
redesign.

**Still to understand.** Whether these readers would rather have it in their inbox, in a feed, or
summarized by an assistant. Asking five of them answers it.

**Who acts.** You name the people. I can build the feed link now and the email path when the
review opens it.

## 4. Design and experience: does the site serve the intent?

**The questions**

- Can a first-time reader say what you believe about the market after ten seconds?
- Can a returning reader see what changed since last week without hunting?
- Does the thesis visibly develop over time, or does each week stand alone?
- Can a reader trace any claim to its source without losing their place?
- Does it feel like a well-made instrument, on a phone as well as a desk?
- Does the design support whatever bucket 1 decides about money, without turning into a sales
  page?

**What we know.** Production scores 33 of 100 on a rubric two independent scorers agreed on. The
argument is good and sits five screens down under twenty-three cards. Accessibility and the
evidence panel are already strong. Most of the fix is reordering content that already exists.
Detail: `design-spec.md`, `score-baseline.md`, `site-rubric.md`.

**Recommendation.** Two waves. Wave 1 is small and does not depend on the intent answer, apart
from one descriptive sentence: move the argument to the top, add a compact thesis block, a visible
feed link, links to the data files, and a truthful cadence sentence. Projected 55 to 60. Wave 2
(a thesis page whose record grows by one line per signed issue, a method page, rows in place of
cards, one typeface) waits for a second signed issue and for the intent session. Projected 69 to
79 after both.

**Still to understand.** Whether the first screen really fits at phone width with your real
headline lengths. That is answered by rendering it, which is the first build task. Also: ordering
items by importance needs a small change to the weekly issue format, which the brief put outside
this run. It is the largest score still on the table.

**Who acts.** Me, end to end, once you say yes to wave 1. You look at one preview.

## 5. Machine readers: can an assistant read and cite you?

**The questions**

- When someone asks an assistant about the security market, can it find your position, quote it
  with its confidence and your name attached, and link to the exact claim?
- Do you want AI companies training on your text, only retrieving it, or neither?
- What licence do you publish under?

**What we know.** The data files already exist and nothing links to them. Your signed issues
cannot be changed after publication and a public manifest proves it, which almost no publication
can say. There is no evidence yet that any of this increases citations for a small site. Detail:
`agent-surface-spec.md`.

**Recommendation.** Link what exists now, as part of wave 1. Build the rest in wave 2. Decide the
crawler policy and the licence only after the employer question in bucket 7, because both grant
standing public permission over your judgments.

**Still to understand.** Whether assistants actually cite small publications that do this. Cheap
to watch after launch by counting requests for the data files in Vercel's logs.

**Who acts.** Me for the build. You for crawler policy and licence.

## 6. Monetization

**The questions**

- Should this earn money directly at all, or is its job to make you more valuable in work you are
  already paid for?
- If directly: who pays, for what, and how much?
- What must exist first? A track record, a list, a cadence.
- What would damage the thing that makes it valuable?
- What is realistic in twelve months?

**What we know, and how good the evidence is.** Honestly, thin.

- Read directly from publishers' own pages: Return on Security's data platform is $199 a month
  with a $79 a month API add-on and a $12 a month supporter tier; Stratechery is $15 a month; The
  Information is $399 to $749 a year. Return on Security already owns the paid security-data
  lane and is one of your sources.
- Second-hand, from platform blogs nobody here read at source: a 0.62 percent median conversion
  from free to paid; sponsorship rates of $40 to $120 per thousand readers; about six and a half
  months to a first dollar.
- Found nowhere: any price for a small organization buying access to one practitioner's judgment.
  So the $3,000 licence in the plan is a guess with nothing under it.
- One Opus consult wrote the commercial model, and my plan adopts most of it. It is one opinion.
- Files: `research/03-peers-and-pricing.md`, `research/04-monetization-mechanics.md`,
  `research/09-browser-followup.md`, `consults/monetization-consult.md`, `monetization-plan.md`.

**Recommendation.** Pause this bucket until the intent session. The current plan (charge nothing
for nine months, never gate content, no vendor sponsorship ever, then one organizational licence)
follows from `intent.md` as written. If your intent is more commercial than that file says, the
plan changes, and I would rather research toward the right target than defend the wrong one.

**Still to understand, once intent is settled.**

- How have solo practitioners with a day job actually turned a public track record into income?
  Named cases, from their own accounts, not platform averages.
- What do the organizations you would sell to already pay for outside market reads, and from
  which budget?
- What is the indirect value: does a public record measurably help you win or deepen advisory
  work? How would we see it?
- If you want a bolder model (a paid tier, a data product, sponsorship from non-vendors), what
  would each need, and what would each cost in independence?
- One real conversation with one plausible buyer. It will tell you more than all of the above.

**Who acts.** You in the intent session first. Then I can run the deeper research end to end.

## 7. Permission and risk

**The questions**

- Does your employer's outside-activity policy require you to disclose, or get approval for, a
  personally owned publication that judges the market your employer sells into?
- Would taking money from a partner, competitor or client need approval?
- What independence rules does the site state publicly?
- Are the project's own rule files consistent with what is actually live?

**What we know.** Nobody on this run has read your employer's policies, so everything about them
is unverified. The first question applies today, because the site is live under your name. Also,
`.claude/rules/constraints.md` line 19 still says the website is not authorized, while
`intent.md` has listed it as decided since 2026-08-16.

**Recommendation.** Ask the employer question in writing this week. Amend the stale rule line
yourself or tell me to propose the wording. Hold every public statement about commercial
independence until you have the employer's answer.

**Who acts.** You.

## 8. What truly needs you, and what I will simply do

**Only you can do these**

1. The intent session (bucket 1).
2. The employer question (bucket 7).
3. Choose the gather runtime and sign `2026-w37` (bucket 2).
4. Name the first ten to fifteen readers (bucket 3).
5. Write one sentence: the cadence you will keep.
6. Say when the preview may be promoted to production.

**One yes from you, then I run it end to end and show you a preview**

- Wave 1 of the design and the machine links, with every design choice taken at my
  recommendation: the front page order, the compact thesis block, the plain-words note beside the
  locked headline, dropping the duplicate date in the phone header, the visible feed link, the
  data file links. If you dislike something on the preview, it changes; nothing reaches
  production without you.

**Parked until intent and the employer answer are in**

- Wave 2, the crawler policy, the licence, the independence statement, the contact sentence, the
  whole monetization path.

## 9. Order of work

| Order | Bucket | Why here | Depends on |
|---|---|---|---|
| 1 | Purpose and intent | Every other bucket is judged against it, and you already sense a gap | You |
| 1, in parallel | Permission and risk | One email, and it can stop or reshape everything | You |
| 2 | Durability and updating | A site that publishes once is not a publication. This is the real constraint | Your runtime choice; optionally a widened scope for me |
| 3 | Audience and exposure | The only thing that moves the numbers the project says it cares about | Your list of names |
| 4 | Design, wave 1 | Cheap, mostly independent of the intent answer, makes what exists legible | One yes |
| 5 | Machine readers, links only | Rides along with wave 1 | Same yes |
| 6 | Monetization research, then plan v2 | Only worth doing against a settled intent | Bucket 1 |
| 7 | Design wave 2 and the full machine surface | Worth it once a second issue is signed and intent is settled | Buckets 1 and 2 |

Timing, using your three layers. Building any of this is Layer A, days. Readers forming a habit
and an organization deciding to pay are Layer B, and that layer sets the pace for buckets 3 and
6: a track record is made of calendar weeks that no build speed shortens. The employer question
is Layer C in character, a policy answer from an organization, so ask early because it moves at
its own speed.
