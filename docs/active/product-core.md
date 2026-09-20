# Product core — Security Market Pulse

**Artifact ID:** `SEC-MARKET-CORE-001` v0.2
**Source:** the owner's own words, given in the terminal on 2026-09-20, written down by the run
coordinator so that no later session or reviewer has to reconstruct them.
**Standing:** this is the working statement of what the product is for. Where it disagrees with
`intent.md` v1.2, the disagreement is listed in section 9 as a proposed amendment. `intent.md`
itself is unchanged until the owner approves new text.
**Use:** every design decision, rubric, review and automation plan starts from this file. A
reviewer who has read only this file should be able to judge whether the site is doing its job.

## 1. What it is, in one sentence

Security Market Pulse is a practitioner's running read on the business of the security market:
who is growing, who is stalling, who is consolidating, who is being bought or shut down, who is in
financial trouble, and what that means if you run a security program or advise someone who does.

## 2. What it is for

First, it is a **credibility asset for the owner's advisory work**. Success is reputation: the
owner can say "I run Security Market Pulse" on a panel and it means something; partners mention
it; sales representatives want to share it with their clients nationally; readers come back
because it is accurate, clear and trusted; people write in to say "this is useful, I would like to
see X".

Second, it is a **working instrument the owner uses himself**. His job is to stand in front of a
security leader and say he can find the best solution for their requirements. To do that he needs
current, evidence-backed answers to "for this domain, which two or three vendors are on solid
footing, and why". The example he gave: a request came in to give a vendor's team time in front
of the account team. His sense was that the market was not talking about that vendor, but sense
is not evidence. Evidence is what the market is telling us: if a vendor is not growing in line
with its competitors, that is one signal (never the only one) that extra attention is not
warranted. The site has to be able to support a decision like that, for each domain, kept current.

Money is a **nice-to-have, later**. Brand and audience first. A newsletter may follow. Running
cost should stay around ten to twenty dollars a month.

## 3. Who it is written for

| Tier | Reader | What they come for |
|---|---|---|
| 1. Written for | Security leaders and decision makers: chief information security officers, security architects, the people running a security program | "What is happening in the market I buy from? Who is winning, who is fading, who is being absorbed, who might not be here in two years? What should I be thinking about?" |
| 2. Also for | People who advise and sell to tier 1: the owner, his colleagues and leadership at his employer (a security reseller and integrator), and vendor partner teams | The same picture, plus the forward look: where spending is heading, which vendors to build a practice around, what to bring to a client conversation |
| 3. Welcome | Anyone who wants a practitioner's pulse on the security market | The same |

Investors are **not** a designed-for reader. The kickoff for the Fable run named them; the owner
withdrew that on 2026-09-20. The site still gives no investment advice.

## 4. What it covers, and what it does not

**Covers:** the business of the security market, from public information. Earnings and growth by
vendor. Funding. Acquisitions and consolidation. Shutdowns, layoffs, debt and distress (the owner
named a large security services firm's debt problems as the kind of thing he wants captured).
Platform moves. For each security domain, who the leading two or three players are and what the
evidence says about their footing. AI security belongs here because it is where the market's
money and attention are moving, covered as a market (who is buying whom, what is actually
revenue), not as news.

**The time frame:** look back three to six months at what actually happened, in filings and
public numbers, and use that to say what is likely over the next three to six months. Backward
view grounded in evidence; forward view labelled as judgment.

**Does not cover:** daily security news, vulnerabilities, breaches as events, product reviews,
technical evaluations. "It is not where I go for my security news. It is a market pulse."

## 5. Where the founding thesis sits now

The project began from one question of the owner's: does security spending lag infrastructure
spending, and by how much. That thesis ("Infrastructure is running ahead. Security is splitting,
not booming.") is **one standing analysis on the site, not the site's identity.** A security
leader is unlikely to care about it. An advisor or a vendor partner will, because it helps them
plan. So it keeps a home (its own section or page, with its record), and it leaves the first
screen. The first screen belongs to the market picture in section 4.

This reverses the centre of the Fable run brief and of `design-spec.md` v0.2, which put a
standing-thesis panel on the first screen. Both are superseded on this point.

## 6. How it has to run

The owner's words: "Fully automated, where jobs are running, and then once or twice a week I can
glance at something and make a decision." It has to come to him, in a channel (email or Slack are
the candidates). He cannot be starting agents by hand.

Non-negotiable quality bar, also his words: the site must be updated regularly and without fail,
with accurate, fresh, validated information people can trust. "If that can't happen, then it's
worthless." That comes **before** promotion to a wider audience.

Order of work he set: first get the site saying the right thing for the right reader. Then make
it durable and automatic. Then promote it. Then, maybe, money.

**Open, and important: what needs a human decision at all.** `intent.md` v1.2 and the project's
rules say a machine drafts and a named person signs every judgment. The owner now doubts that
"sign every judgment" fits what the product needs. The coordinator's recommendation, to be decided
by the owner, is a split:

- **Bounded observations** may publish automatically on a schedule: "this company reported this
  figure, for this period, in this filing", "this acquisition was announced" (kept distinct from
  "this acquisition closed"). Each carries its source, a retrieval receipt, and machine validation
  of the company or segment, the metric definition, the period and the units together. They
  publish under collection and presentation rules the owner approves once, in advance: which
  suppliers are covered, which metric is shown for each, how they are listed.
- **Judgments** need the owner's approval, one tap in the channel, and the approval covers the
  exact text and the evidence it rested on. This includes more than it first seems: which events
  matter, any "why it matters" sentence, any word such as accelerating or leading, any stance,
  forecast or claim of distress. When the evidence under an approved judgment changes materially,
  the judgment shows as awaiting review and is not presented as freshly endorsed.
- The weekly output always states one of three things plainly: material changes found, no
  material change found within our coverage, or collection incomplete. A failed run and a quiet
  week must never look the same.

(v0.2, tightened after the external review, which showed that choosing vendors, metrics and what
matters is itself judgment, and that the existing "why it matters" lines contain interpretation.)

This keeps the promise that matters (nothing that reads as the owner's opinion goes out without
him) while removing the thing that stalled the site (nothing at all going out without him).

## 7. How we will know it is working

| Signal | How it is seen |
|---|---|
| The site is fresh | Every scheduled update happened; the newest item is days old, never weeks |
| People return | Visits and returning visitors, from privacy-respecting analytics (the owner is willing to pay for analytics) |
| People share it | Inbound referrals; colleagues and partners forwarding it; requests to share with clients |
| People engage | Replies and requests ("I would like to see X") |
| It changes decisions | Entries in `docs/active/decision-impact-log.md`. The vendor-attention decision in section 2 is the first real one and should be logged there by the owner, in whatever form he is comfortable putting in writing |
| It builds the owner's standing | He uses it in meetings and introductions, and it holds up |

## 8. Open questions register

Questions raised in `docs/active/fable-run/decision-map.md`, with where each stands. Nothing is
dropped; answered ones are marked.

| # | Question | Status |
|---|---|---|
| 1 | What is the site for? | **Answered 2026-09-20.** Section 2 |
| 2 | Who is the reader? | **Answered.** Section 3. Not investors |
| 3 | What does success look like? | **Answered.** Sections 2 and 7 |
| 4 | Is money a goal? | **Answered.** Nice-to-have, later; brand and audience first |
| 5 | How does it sit beside the owner's job? | **Answered.** A credibility asset and a talking point whose value attaches to him and to his employer |
| 6 | Is the founding thesis the centre of the site? | **Answered.** No. Section 5 |
| 7 | How much of the owner's week is this worth? | **Partly answered.** A glance once or twice a week. The exact budget depends on question 8 |
| 8 | What needs a human decision before it publishes? | **Open.** Recommendation in section 6 |
| 9 | Where do the jobs run, and what channel do decisions arrive in? | **Open.** Being worked in `docs/active/fable-run/automation-plan.md` |
| 10 | What cadence does the site promise? | **Open.** Recommendation: tracked facts update through the week as they are validated; one read a week. The sentence for the site is drafted in the design spec for the owner to edit |
| 11 | Which domains, and which vendors per domain, does the site commit to covering? | **Open.** The site has six domains and a vendor panel today; whether that is the right set for a security leader is unreviewed |
| 12 | How are distress signals (debt, layoffs, shutdowns) sourced reliably from public information? | **Open. Needs research** |
| 13 | Should the site say more about the owner himself? | **Open.** He raised it and was unsure |
| 14 | Which analytics, and what is measured? | **Open.** Must respect the project's rule against optimizing for traffic: measure return visits and sharing, not volume |
| 15 | Is there a monetization opportunity worth pursuing later? | **Parked by the owner.** Research so far: `docs/active/fable-run/monetization-plan.md`. Revisit once there is an audience |
| 16 | The employer's outside-activity policy | **Parked by the owner on 2026-09-20.** He is not worried about it now. Kept on the backlog |
| 17 | Crawler policy and content licence | **Open, low priority** |
| 18 | The issue already drafted for the week ending 13 September (`2026-w37`) | **Open.** Whether the weekly numbered issue remains the unit of publishing depends on question 8 |

## 9. Proposed amendments to `intent.md` (not applied)

For the owner to accept, change or reject. The run does not edit `intent.md`.

1. **Purpose.** State plainly that the project is first a credibility asset for the owner's
   advisory work and a working instrument for vendor and domain decisions.
2. **Beneficiaries.** Put security leaders and practitioners first. Add vendor partner teams to
   the advisor tier. Keep investors out.
3. **The founding thesis** becomes one standing analysis among the site's outputs, not the
   organizing question.
4. **Scope.** Add distress and consolidation signals explicitly. Add the three-to-six-month look
   back and look ahead. Say what it is not: a security news site.
5. **Autonomy.** Replace "a named person signs every judgment" with the split in section 6, if
   the owner accepts it: validated tracked facts may publish automatically; judgments need his
   approval. This also requires amending `.claude/rules/constraints.md`, which still lists the
   website and an autonomous pipeline as not authorized.
6. **Revenue.** One line: not a current goal; may be explored once an audience exists; never at
   the expense of an unbought judgment.
7. **Must not optimize.** Keep "traffic". Add that measuring return visits, sharing and engagement
   is allowed and wanted, because the owner needs to know whether the work is being used.

## 10. Raised by the external review, for the owner

1. **What a security leader actually needs is mostly not on the site yet**: what a development
   means for someone who buys from these suppliers (continuity, renewals, consolidation, support
   changes, what to ask the supplier). This is the product's missing centre. It is judgment, so it
   is his to write or approve; a machine can draft it.
2. **The reader needs to know the author's interests.** Separate from the parked employer-policy
   question: a reader judging a market read is entitled to know the author works for a reseller of
   these vendors, how suppliers are chosen for coverage, and that partners and competitors are
   held to the same evidence standard. Whether and how to say this on the site is his decision.
3. **Coverage.** Six inherited domains do not cover what a security program buys; endpoint and
   managed security services have no home. Start with a declared, bounded supplier list he can
   keep current, and publish what is not covered.
4. **Promise less.** A declared supplier set and one short weekly brief, with an honest
   reduced-service state when he cannot review, will earn more trust than broad coverage approved
   in a hurry.
