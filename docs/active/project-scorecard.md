# Project scorecard

**ID:** `SEC-MARKET-SCORE-001` · **Version:** v0.1 draft · **Opened:** 2026-08-22

## What this is

A standing instrument for rating this project against its own governing intent, so the roadmap is
chosen by evidence instead of by whatever is easiest to build next.

It is append-only. A past score is never edited. Each new assessment adds a row and says what
changed and why.

## What this is not

It is not the vendor scorecard on the website. That is a different thing with a confusingly similar
name. This rates the project. That rates the market.

It does not rate effort, output, or shipping. `intent.md` is explicit: "Completing agents, a
website, reports, or other deliverables alone does not constitute success." A score cannot rise
because work happened.

## The two tiers, and why the split matters

**Outcome dimensions** are lifted directly from Observable Success in `intent.md`. They are what
intent says success *is*.

**Enabling dimensions** come from Must Remain True and Must Not Optimize. They are what has to be
true for an outcome to become possible. They are not success.

**The capping rule.** The overall grade is capped at the mean of the four outcome scores. Enabling
work can never lift the grade past what the project has actually achieved. Without this rule the
instrument would reward polishing the website forever, which is the exact failure intent warns
against.

## Outcome dimensions

### O1 — Decision impact
*Intent: "changed or accelerated a GTM or resource decision."*

| Band | What it takes |
|---|---|
| 0 | No decision influenced, and no way to know if one was |
| 1–2 | A mechanism exists to capture impact; nothing recorded in it |
| 3–4 | One decision recorded, self-reported by the author |
| 5–6 | One decision recorded by somebody other than the author |
| 7–8 | Several decisions, across more than one kind of beneficiary |
| 9–10 | Decisions trace to specific evidence, and repeat across more than one edition |

### O2 — Account-team conversation
*Intent: "supported a meaningful account-team client conversation."*

Same bands, reading "conversation" for "decision."

### O3 — Client decision support
*Intent: "helped a client evaluate technology, timing, or partner choices."*

Same bands, reading "client choice" for "decision."

### O4 — Reconstructable reasoning
*Intent: "produced reasoning another person can reconstruct from its evidence."*

| Band | What it takes |
|---|---|
| 0 | Claims appear without sources |
| 1–2 | Sources listed but unverified, or links that do not resolve |
| 3–4 | Sources verified once, by the author |
| 5–6 | Every figure traces to a primary document, verified independently |
| 7–8 | Verification repeats on a stated cadence, and a build gate enforces it |
| 9–10 | A stranger has actually rebuilt a call from the evidence and reached the same place |

## Enabling dimensions

### E1 — Evidence integrity
Sources resolve, figures match the document, freshness is known, multi-source claims name every
source. Enforced by gates rather than by care.

### E2 — Epistemic honesty
*Intent: "preserve provenance, uncertainty, conflicting evidence, and credible alternatives," and
label the confidence and basis of forward-looking judgments.*

Scores low when a confidence field is present but uniform, because a field that always says the same
thing carries no information. Scores high when contradicting evidence is expressed as clearly as
supporting evidence, and when the page can say what would change a call.

### E3 — Legibility
Can a reader find and use what is there. Content that exists but does not render scores zero here,
however good it is.

### E4 — Operating cadence
The loop runs at a stated interval, each signal family has a declared refresh rate, and staleness is
visible. Scores low if the cadence is undeclared, and also low if volume or automation grows at the
expense of decision value — intent forbids optimizing for those.

## How a score is set

1. Every score cites evidence. A number without a reason is not a score.
2. Evidence is a thing that can be checked: a log entry, a measurement, a commit, a verification run.
   Not an impression.
3. When unsure between two bands, take the lower one.
4. Movement is explained in the history table. A score that moves without a stated cause is a
   drafting error, not a result.

## How this drives the roadmap

**The next work attacks the lowest outcome dimension, or the enabling dimension most clearly
blocking it.** Nothing else gets picked up while an outcome dimension sits below 3, unless it is a
correctness or trust defect, which is always allowed to jump the queue.

This is the whole point of the instrument. It exists to stop the roadmap drifting toward pleasant
enabling work while the outcomes stay at zero.

## Baseline — 2026-08-22

| # | Dimension | Score | Evidence |
|---|---|---|---|
| O1 | Decision impact | **2** | `docs/active/decision-impact-log.md` exists with a template and reads "None yet — first use wins the proof." Mechanism present, zero entries |
| O2 | Account-team conversation | **1** | No capture mechanism distinct from O1's log; no entries |
| O3 | Client decision support | **0** | Site has been shared with one person. No client has used it. No mechanism to know |
| O4 | Reconstructable reasoning | **6** | All 71 canonical sources verified against live pages 2026-08-20; no figure contradicts its source; six unattributed claims found and fixed with primary documents. Not yet on a cadence, so not 7 |
| E1 | Evidence integrity | **7** | Three build gates enforce it, proven fail-closed by perturbation. Freshness is not yet checked, and 11 sources remain unread behind host blocks |
| E2 | Epistemic honesty | **3** | Provenance model is genuinely good — tracked versus judged, signed and dated. But confidence reads MEDIUM on all four domains, so it carries no information, and contradicting evidence has no place in the data model at all |
| E3 | Legibility | **2** | 42 vendor cards exist and zero render. Measured, not estimated. They sit below the author signature behind a bar named for a past episode |
| E4 | Operating cadence | **3** | A weekly loop is running and documented, but no signal family has a declared refresh rate and staleness is invisible to a reader |

**Overall: 2.25**, capped by the mean of O1–O4. Enabling work sits well above it, which is exactly
the imbalance the capping rule is built to expose.

### What the baseline says

The project is good at being trustworthy and bad at being used. Evidence integrity and
reconstructable reasoning are the two strongest scores, and both came from work done in the last
three days. Every outcome dimension except O4 is at or near zero, and O4 is the one outcome
dimension that is really about craft rather than about anybody using anything.

Nothing here is a surprise given the site is a week old and has been shown to one person. The
number is not a judgment about effort. It is a statement about where the next work has to go.

### What the baseline implies for the roadmap

O3 is lowest, but it is not the right first target — a client cannot use something that has not
proven useful internally first, and intent orders the beneficiaries that way too.

**O1 is the first target.** It is the load-bearing one in intent, it has a mechanism already built
and unused, and it needs one real logged use rather than a feature.

**E3 is the enabling dimension most clearly blocking it**, because a reader cannot act on a page
where the substance does not render. That is already specced as
`docs/active/scorecard-visibility-spec.md` and in build.

E2 is the second enabling target, and it is larger than it looks: making confidence mean something
and giving contradicting evidence a place in the data model is the same work the outside review
called the missing link between evidence and judgment.

## Score history

| Date | O1 | O2 | O3 | O4 | E1 | E2 | E3 | E4 | Overall | What moved and why |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-22 | 2 | 1 | 0 | 6 | 7 | 3 | 2 | 3 | 2.25 | Baseline. First assessment |

## Review cadence

Scored at each edition, and whenever an outcome dimension has evidence that it moved. Not scored on
a calendar, because a score that changes without evidence is noise.

## Open questions on the instrument itself

- Should O2 and O3 stay separate? They may collapse into one beneficiary-use dimension if the
  distinction never produces different roadmap choices.
- Is an eight-dimension instrument too heavy to actually run every edition? Prefer cutting a
  dimension to letting the scorecard go unscored.
- The capping rule is deliberately harsh. Confirm it survives contact with a quarter where enabling
  work genuinely was the right call.
