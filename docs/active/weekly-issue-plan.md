# Weekly issue plan — Security Market Pulse as a recurring product

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-WEEKLY-001` |
| **Version** | v0.1 |
| **Status** | plan, for owner review |
| **Date** | 2026-09-03 |
| **Governs** | [intent.md](../../intent.md) `SEC-MARKET-001` v1.1, proposed v1.2 below |
| **Approach approved** | 2026-09-03, owner, in conversation (D-62) |
| **Backlog** | SEC-027 through SEC-031 |

## 1. What this plan does

It turns Security Market Pulse from a dated research edition into a weekly product that a security
leader or an ePlus account team can read in five minutes, every week, and trust.

Four changes, in order of importance:

1. **The weekly issue becomes the unit of product.** Five short sections, each with three to five
   sourced items, and a signed "what we now think" that is allowed to move. The Episode 002 market
   call stops being the headline and becomes a standing thesis each issue scores against.
2. **A machine drafts, a person signs.** A scheduled agent gathers every Tuesday from the sources the
   project already catalogued, drafts the issue as a pull request against `preview`, and quotes every
   figure verbatim from a fetched document. The owner spends twenty to thirty minutes reading,
   cutting and signing. Nothing publishes without that signature.
3. **The issue arrives.** Email to a named pilot list from the first issue, an RSS feed and a
   permalink per issue, analytics turned on. Public email only after four consecutive issues have held.
4. **ePlus consumes downstream.** One public core. The ePlus overlay, account triggers and rep
   framing, is built inside the ePlus channel and cockpit from a machine-readable copy of each
   issue. Pulse never receives account data and no ePlus surface lives on this domain.

Everything here is Layer A build velocity: days to weeks. The one Layer B item is whether the pilot
readers change a decision, and with a named set of five to eight people that is measured in weeks.

## 2. What does not change

- Public, publishable sources only. Every figure traces to a document a reader can open.
- Facts and judgments stay labelled separately. A funding round is never promoted to a judgment.
- NO-CALL stays available and is used when the evidence will not carry a call.
- Production moves only by fast-forward from `preview` on an explicit owner yes, after a rendered
  review at 1440 and 390 pixels.
- No confidential ePlus information in the core. No investment advice.
- The existing build gates stay and new ones are added; none are removed.

## 3. Intent reconciliation — proposed v1.2

`intent.md` may not change without the owner's explicit acceptance of the text. This is the proposed
change. Nothing in it alters purpose, beneficiaries, value or the public-evidence boundary.

**State register changes**

| Item | v1.1 | Proposed v1.2 | Promotion basis |
|---|---|---|---|
| Weekly issue as the unit of product | absent | **Decided** | Owner approval 2026-09-03 |
| Autonomous worker agents and reasoning layer | Exploring | **Decided for gather and draft only.** Publication and every judgment remain a named person's act | Owner approval 2026-09-03; shadow design v0.2 already drew this line |
| Audience- or region-specific views and newsletters | Exploring | **Decided for a named pilot list.** Public distribution follows four held issues | Owner approval 2026-09-03 |
| Confidential client overlay | Exploring | Exploring, with a decided boundary: **built downstream inside ePlus surfaces, never in the core, never on this domain** | Owner approval 2026-09-03 |

**One line added to "Must remain true"**

> A machine may retrieve, extract, compare and propose. Only a named person signs a judgment or
> publishes an issue.

**One line added to "Traceability and handoff"**

> The Episode 002 market call is a standing thesis scored by each weekly issue, not the site headline.

"Last reconciled" moves to 2026-09-03. Revision record gains a v1.2 row. The "Must not optimize"
section is unchanged and is the reason public email waits for four held issues.

## 4. Workstreams

### WS-A — Governance (this session, owner accepts)

- Owner accepts the v1.2 text above, or edits it. Then `intent.md` is updated and D-63 records it.
- BACKLOG: SEC-027 to SEC-031 opened; SEC-017 superseded by SEC-028; SEC-021 Phase 3 folded into
  SEC-027; SEC-019's frame question resolved by SEC-027; SEC-005 unchanged, scheduled for the
  earnings-season quarter.
- Owner names the pilot set (five to eight people, role and segment only in this repo, mapping in the
  ePlus cockpit per D-58) and the independent scorer for the outcome review.

**Done when:** intent v1.2 accepted, backlog reconciled, pilot set and scorer recorded.

### WS-B — The weekly issue product (SEC-027)

The spec to be written: `docs/active/weekly-issue-spec.md` (`SEC-MARKET-ISSUE-001`).

**Data model.** One `Issue` record per week in `web/src/data/issues/`: id (`2026-w38`), week ending,
published date, signed by, five sections, each a list of items, each item carrying a headline, one
sentence of why it matters, the evidence ids it rests on, and a lane tag. A closing `weThink` block
lists posture deltas against the prior issue and the Episode 002 thesis score. Issues are append-only
and hash-locked the way editions already are.

**The five lanes**, each mapped to data the site already carries:

| Lane | Question | Existing data |
|---|---|---|
| Formation | Who started or raised | `activity.ts`, funding ops |
| Absorption | Who bought whom, and what the accounting says they bought | M&A catalog, `platformPressure.ts`, the PPA finding |
| Prints | Who is actually growing or shrinking | `prints.ts`, domain ops |
| Capital and backdrop | Infrastructure versus security spend, buyer budgets | `panelRaw.ts`, Episode 002 |
| What we now think | Posture deltas, thesis score, NO-CALLs | `domains.ts`, `hypotheses.ts`, `edition.ts` |

**Page.** Latest issue opens the page: date, one-line read, five sections, what we now think, signed
and dated. Below it the archive, one row per issue with its read. Below that the standing reference:
the Episode 002 thesis with its running score, the tracked hypotheses, the vendor scorecard, the
evidence library, method. Every issue has a permalink (`/issues/2026-w38`) and its own Open Graph
image. Domain cards lead with their trigger sentence and carry the domain as a label, which closes the
SEC-019 frame question. Confidence either varies across postures or is removed; the horizon type
gains the 24-month band intent promises.

**Gates.** `verify:issue` fails the build when an item has no evidence id, an evidence record has no
verbatim excerpt from a fetched document, an issue's week overlaps another, an issue was edited after
publication, the `weThink` block is unsigned, or a section header count disagrees with rendered items.
Each check proven by perturbation before acceptance, per this project's standing rule.

**Issue #1 is written by hand.** It dogfoods the template before the agent is asked to produce it, so
the agent's brief is drawn from a real issue rather than a guess.

**Done when:** issue #1 on `preview`, rendered at both widths against production, promoted on owner
yes, permalink resolves, gates proven.

### WS-C — The Tuesday gather (SEC-028)

The spec to be written: `docs/active/gather-job-spec.md` (`SEC-MARKET-GATHER-001`).

**Shape.** A scheduled job on macbook2014 (launchd, registered with jobs-agent) runs Tuesday 06:00.
It invokes a subscription-authenticated agent run with a fixed brief and a fixed target list drawn
from the funding, M&A and domain ops documents. For each source it fetches the document, quotes the
excerpt verbatim, and records company, date, round or deal, amount if stated, and URL. It drafts the
issue file and any new evidence records, runs the full `verify:*` suite locally, and opens a pull
request on branch `issue/2026-wNN` against `preview` with a summary of what it found, what it could
not read, and what it deliberately left out.

**Rules the job obeys**, all of them lessons this project has already paid for:

- No sub-agent spawning. Fixed target list. An explicit "record none found and move on" rule.
  Output capped.
- A tool's summary of what it fetched is not evidence; the job reads the bytes it downloaded before
  quoting them.
- SEC.gov is read with the identified User-Agent its policy asks for. Blocked hosts are recorded as
  unreadable, never bypassed. Return on Security is summarised and linked, never republished.
- The job never edits `intent.md`, `decisions.md`, the market call, a posture, or a confidence value.
  It proposes deltas in the PR body; a person applies them.
- Zero readable sources is a failure, not an empty issue. The job exits non-zero and jobs-agent alerts.
- It never touches `main`.

**Owner ritual, Tuesday or Wednesday, twenty to thirty minutes.** Open the PR's preview render. Cut
anything thin. Write or edit "what we now think" and sign it. Merge to `preview`. Promote with
`PROMOTE=1` when the render checks pass. Publish day is Wednesday.

**Ownership.** The job definition and its schedule are dev-system surfaces: jobs-agent registers
the schedule; if a new agent definition is needed, Forge writes it. This session specs and reviews;
it does not author either.

**Done when:** issue #2 is agent-drafted, reviewed in under thirty minutes, and promoted; the job has
run three consecutive Tuesdays without manual intervention beyond the review.

### WS-D — Distribution (SEC-029)

- Vercel Web Analytics enabled in project settings. The component is already in the page.
- Issue #1 emailed to the pilot list by hand from the owner's mail. No provider yet.
- RSS feed generated at build from the issues array, live by issue #2.
- Permalink per issue and per-issue Open Graph image, live by issue #2.
- After four held issues: email provider chosen and the list opened to the public. Not before.

**Done when:** analytics reporting, feed validating, pilot receiving each issue.

### WS-E — ePlus downstream digest (SEC-030)

Pulse publishes a machine-readable copy of each issue at `/issues/2026-wNN.json` at the same time as
the page. That file is the whole interface. What ePlus builds from it, the internal weekly digest with
a sixth section for account triggers and partner framing, lives in the ePlus channel repo and the ePlus
cockpit and is owned there.

Two handoffs after this plan is accepted: to `eplus-security-advisor` for the rep-facing digest
format and channel, and to `eplus-ops` for the account-trigger section drawn from the cockpit. Pulse
never receives account, pipeline or partner-terms data back.

**Done when:** the JSON copy ships with issue #2 and both handoffs are acknowledged.

### WS-F — Vendor lens (SEC-031)

A filter on the issue and the scorecard by vendor or OEM, so any reader views the week through the
platforms they hold. Public and non-confidential. Scheduled after issue #2 so the issue model settles
first.

**Done when:** a reader can filter the current issue and the scorecard to a chosen set of vendors and
share that view by URL.

## 5. Sequence

| Week | Dates | Deliverable |
|---|---|---|
| 0 | Sep 3 – 9 | WS-A complete. Issue spec and gather spec written and reviewed. Analytics on. Pilot named. |
| 1 | Sep 10 – 16 | WS-B on `preview`: issue model, archive, page reframe, gates. **Issue #1** written by hand for the week ending Sep 13, promoted Wed Sep 16, emailed to the pilot. |
| 2 | Sep 17 – 23 | Gather job v1 runs Tue Sep 22 and drafts **Issue #2**. Owner signs, promoted Wed Sep 23. RSS, permalinks, JSON copy live. Handoffs to ePlus agents sent. |
| 3 | Sep 24 – 30 | **Issue #3** agent-drafted. Vendor lens on `preview`. First decision-log entries expected. |
| 4 | Oct 1 – 7 | **Issue #4** agent-drafted. Vendor lens promoted. |
| Review | Oct 8 | Four issues held? Owner time per issue? Decision log entries? Then decide public email and the earnings-season replay instrument (SEC-005). |

## 6. Measures

| Measure | Target by Oct 8 | How it is read |
|---|---|---|
| Consecutive weekly issues | 4 | archive |
| Owner time per issue | ≤ 30 minutes | logged in the PR |
| Figures failing verification | 0 | `verify:issue` and the per-issue health check |
| Pilot readers named | 5 – 8 | project scorecard denominator |
| Decision impact log entries | ≥ 2 | `decision-impact-log.md`, scored by the independent human |
| Issue delivered to pilot | every week | email sent, feed updated |

The edition health check runs on every issue and is scored by an agent. The outcome review runs
monthly and is scored by the named independent human, per D-58. The author of an issue never scores
its outcome.

## 7. Risks

| Risk | Mitigation |
|---|---|
| Thin weeks produce filler | The quiet-week rule stands. Fewer items, never invented ones. A section may be empty. |
| The agent quotes a figure the document does not state | Every excerpt is verbatim from fetched bytes; `verify:issue` fails without one; owner review reads sources on anything that moves a judgment. |
| Owner time exceeds thirty minutes and the cadence slips | Time is logged per issue. If two issues exceed the budget, the brief is tightened before adding anything else. |
| Source terms | Summarise and link. Blocked hosts recorded, not bypassed. No bulk scraping. |
| Front-page reframe regresses the accepted design | Rendered before-and-after at 1440 and 390 on every promotion; the must-see gate already exists. |
| Development tooling | `node_modules` in `web/` lives in the OrbStack VM; all npm runs go through `orb run -m dev`. Playwright and `shot.mjs` run on the host. |
| Scope creep during build | Anything not in WS-A to WS-F goes to the backlog with a note, not into the build. |

## 8. Owner decisions carried by this plan

| # | Decision | Recommendation |
|---|---|---|
| 1 | Accept the intent v1.2 text in §3 | Accept as written |
| 2 | Name the pilot set and the independent scorer | Five to eight people across CSPs, account teams and two clients |
| 3 | Publish day | Wednesday, after a Tuesday gather |
| 4 | Public email timing | After four held issues, at the Oct 8 review |
| 5 | Vendor lens timing | After issue #2 |

## 9. What this plan does not authorise

Auto-publishing anything. Changing a posture, call or confidence without a signature. A database,
scraper farm or collector beyond the single scheduled gather job. Any ePlus surface on this domain.
Any change to `main` except by the documented promotion.
