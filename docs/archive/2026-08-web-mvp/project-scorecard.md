# Project scorecard

**ID:** `SEC-MARKET-SCORE-001` · **Version:** v0.2 · **Opened:** 2026-08-22

## Why v0.2 replaces v0.1 the same day

v0.1 was sent for independent critique and largely failed it. The failures are recorded here rather
than quietly fixed, because the instrument's whole purpose is to stop this project fooling itself.

1. **It scored "nobody has tried it yet" as failure.** Client value was scored 0. A zero means tested
   and found useless. Nothing had been tested. The instrument manufactured a deficit and then used
   that deficit to set priorities.
2. **It rewarded exactly the inflation it claimed to prevent.** Decision impact scored 2 for having
   an empty logging template. That is enabling work scoring as an outcome.
3. **The single overall number hid the thing that mattered.** A compensatory mean let a strong craft
   score cover a nonexistent use score.
4. **The author scored his own work.** The three highest scores all rated work done in the previous
   three days by the person doing the scoring.
5. **It confused source integrity with reconstructable reasoning.** Verifying that a figure matches
   its document does not show that another person could rebuild the call. Those are different claims
   and v0.1 collapsed them.
6. **It invented an intent claim.** v0.1 said intent orders the beneficiaries, leadership before
   account teams before clients. It does not. Intent lists them in a table. That was a fabrication
   of the same kind this project has been fixing all week.
7. **It missed the central thesis.** Nothing measured earliness, which is the entire purpose.

## What this rates

The project, against `intent.md`. Not the vendor scorecard on the website, which is a different
thing with a confusingly similar name.

Append-only. A past assessment is never edited.

## Two instruments, deliberately separate

Eight scored dimensions every edition would go stale or become a ritual of copying last month's
numbers forward. So the work splits by how fast each thing can actually change.

**The outcome review** runs monthly, or whenever evidence appears that something moved. It asks
whether the intelligence is doing its job.

**The edition health check** runs every edition. It is pass, fail, or exception. No scores.

### Who scores which — settled 2026-08-25 (D-58)

The two instruments have different independence needs, so they get different scorers.

The **outcome review is scored by a named human who did not build this**. It is the only instrument
where independence is load-bearing, because `independently_evidenced` is defined as recorded by
somebody who did not build it, and an author cannot satisfy that definition about his own work at
any level of care.

The **edition health check is scored by an agent**. Its five checks are mechanical enough to be
repeatable — sources resolve or they do not, content renders or it does not — and H4 in particular
is a browser measurement anyone can reproduce. An agent running the same checks every edition is
more consistent than a human doing it occasionally, and it costs nobody's calendar.

The corollary is that the author of an edition never scores its outcome review, including when the
author is an agent.

---

# Instrument 1 — Outcome review

## States, not scores

Every outcome carries a state, not a number. The distinction that matters most is between *nobody
tried it* and *someone tried it and it did nothing*.

| State | Meaning |
|---|---|
| `not_assessed` | No qualified person had a real chance to use it. Not a failure |
| `no_observed_effect` | A real opportunity existed and nothing happened. This is the honest bad result |
| `anecdotal` | Recorded, but self-reported by the author |
| `independently_evidenced` | Recorded by somebody who did not build it |
| `repeated` | Happened across more than one edition |

## The exposure denominator

Recorded first, every time, because no use measure means anything without it.

**How many qualified people had a genuine opportunity to use this intelligence, and who were they?**

An outcome cannot be rated better than `not_assessed` while the denominator is zero.

### Who counts — settled 2026-08-25 (D-58)

Qualified exposure is a **small deliberate pilot set, named in advance**, drawn from two of intent's
three beneficiaries: ePlus account teams and CSPs, and named clients. Security leadership peers
outside the engagement are deliberately excluded from the denominator. They may still read the site
and their reactions are worth having, but their decisions are not observable to us, so counting them
would inflate the denominator with exposure that can never produce an outcome.

Naming the set in advance is the point. A denominator assembled afterwards from whoever happened to
respond measures reach, not opportunity.

### How identities are recorded

Intent excludes client-identifying and confidential ePlus information from this project, and H5
checks for it. The repository is private, so this is a boundary rule rather than a disclosure risk,
but the rule holds either way.

**This repository records role, segment and a stable pseudonymous identifier. It does not record
names of ePlus personnel, accounts, or clients.** An entry reads "account team A, West NorCal" or
"client 3, financial services". The mapping from identifier to person lives in the ePlus operating
cockpit, which is the private store built for confidential engagement data, and it stays there.

This preserves everything the instrument actually needs. The denominator is a count, the beneficiary
tag is a role, and the outcome is a described change. None of those require a name to be true.

## Outcome dimensions

| # | Dimension | The question |
|---|---|---|
| U1 | Observed use | Did someone act differently? Tagged by beneficiary: leadership/CSP, account team, or client |
| U2 | Incremental value | Did it add anything beyond what that person already had from conversations, pipeline, partners, or their own judgment? Intent requires augmenting rather than replacing, so this is the load-bearing one |
| U3 | Lead time | Was it early enough that options were still open? Intent's purpose is recognizing shifts *early enough* to change timing. Nothing in v0.1 measured this |
| U4 | Reconstructable reasoning | Has another person actually rebuilt a call from the evidence and landed in the same place? Source verification is not this |
| U5 | Call calibration | Over time, were the postures and confidence levels borne out? Requires editions to age before it can be answered |
| U6 | Learning velocity | Are editions resolving the assumptions in `intent.md`, or just accumulating material? |

U1 keeps beneficiary tags rather than splitting into three dimensions, because three separate scores
implied a precision that did not exist.

---

# Instrument 2 — Edition health check

Pass, fail, or exception. An exception must name what and why.

| # | Check | Passes when |
|---|---|---|
| H1 | Provenance and evidence integrity | Sources resolve, figures match their documents, multi-source claims name every source |
| H2 | Uncertainty and alternatives | Conflicting evidence and credible alternatives are expressed as clearly as supporting evidence. Confidence carries information rather than reading the same everywhere |
| H3 | Freshness | Each signal family has a declared refresh rate and staleness is visible to a reader |
| H4 | Legibility | The substance renders. Content that exists but does not display fails this outright |
| H5 | Boundary safety | No client-identifying or confidential information, no investment advice, no forced call the evidence cannot support, no manufactured certainty |

H5 exists because those are hard prohibitions in intent, and v0.1 never checked them at all.

---

# Baseline — 2026-08-22

## Exposure denominator: 1

The site has been shown to one person. That single number governs everything below it.

## Outcome review

| # | Dimension | State | Evidence |
|---|---|---|---|
| U1 | Observed use | `not_assessed` | `docs/archive/2026-08-web-mvp/decision-impact-log.md` holds a template and zero entries. With a denominator of 1, no use outcome can be rated |
| U2 | Incremental value | `not_assessed` | No mechanism exists to ask whether it added anything beyond what a reader already knew |
| U3 | Lead time | `not_assessed` | Not measured, and no mechanism exists to measure it. This is the largest gap in the instrument and the project |
| U4 | Reconstructable reasoning | `not_assessed` | Nobody has attempted a reconstruction. The 2026-08-20 sweep proved sources match figures, which is a different claim |
| U5 | Call calibration | `not_assessed` | Two editions exist. Nothing has aged enough to be right or wrong yet |
| U6 | Learning velocity | `not_assessed` | The core lag hypothesis stands at `NO-CALL`, which is honest, but no assumption has been resolved either way |

**Every outcome is `not_assessed`, and that is the correct reading.** The project is one week old with
one reader. It has not failed at anything. It has not yet been given the chance to succeed.

## Edition health check

| # | Check | Result | Evidence |
|---|---|---|---|
| H1 | Provenance and evidence integrity | **Pass with exception** | All 71 canonical sources verified 2026-08-20; no figure contradicts its source; six unattributed claims fixed. Exception: 11 sources unread behind host blocks, and no freshness checking exists |
| H2 | Uncertainty and alternatives | **Fail** | Confidence reads MEDIUM on all four domains, so it carries no information. Contradicting evidence has no place in the data model at all |
| H3 | Freshness | **Fail** | No signal family has a declared refresh rate. Staleness is invisible |
| H4 | Legibility | **Fail** | 42 vendor cards exist and zero render. Measured, not estimated |
| H5 | Boundary safety | **Pass** | Public sources only. No investment advice. The core lag hypothesis is held at `NO-CALL` rather than forced, which is the specific behaviour intent demands |

## Independence

The author of this baseline performed the 2026-08-20 verification work that H1 rates, and the page
measurements that H4 rates. **Both are self-assessed and should be treated as provisional until an
independent scorer confirms them.** H4 is a measurement anyone can repeat in a browser, so it is the
lower risk of the two. H1 rests on judgment about what "verified" means and is the one that needs a
second pair of eyes.

There is no composite score. There deliberately never will be.

---

## How this guides the roadmap

The scorecard **informs** the roadmap. It does not dictate it. v0.1 had a rule forcing work at the
lowest score, which would have prioritised whatever happened to be least measurable.

Work is chosen by the largest evidenced obstacle to learning or to intended value, weighing exposure,
dependencies, risk, reversibility, and how much would actually be learned.

### What this baseline says to do

Every outcome is `not_assessed` and the exposure denominator is 1. **The binding constraint is not
quality. It is that almost nobody has seen it.** No amount of further polish changes a `not_assessed`
into anything else.

That points at three things, in order:

1. **Raise the denominator.** Get it in front of a defined set of qualified people. Until that
   happens the outcome review cannot report anything, and the project cannot learn.
2. **Fix H4, legibility.** This one is genuinely blocking, not merely low. A reader cannot act on a
   page where the substance does not render, so exposure without it wastes the exposure. Already
   specced and in build.
3. **Build the lead-time and incremental-value questions into the impact log.** Right now the log
   asks what changed. It does not ask whether the reader already knew, or whether they still had
   options. Those two questions are the difference between counting uses and knowing if this works.

H2 and H3 are real failures but they are not what is stopping the project learning this month.

## Open questions

- Who is the independent scorer? Without one, H1 stays provisional indefinitely.
- What is the qualified-exposure list, and how large does it need to be before `no_observed_effect`
  becomes a meaningful verdict rather than a small sample?
- U5 calibration needs aged editions. What is the shortest honest interval before it can be asked?
