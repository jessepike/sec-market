# Monetization plan — Security Market Pulse

**Artifact ID:** `SEC-MARKET-FABLE-MONEY` v0.1 (proposal, awaiting owner acceptance)
**Written by:** the run coordinator, 2026-09-20
**Built on:** `consults/monetization-consult.md` (an outside commercial read, consulted once),
`research/03-peers-and-pricing.md`, `research/04-monetization-mechanics.md`,
`research/09-browser-followup.md`, `research-synthesis.md`, `intent.md` v1.2 (read, not edited)

**How numbers are labelled.** *Fetched* means read from the publisher's own rendered page during
this run. *Second-hand* means a platform report or blog that nobody on this run read at source.
*Guess* means judgment, with the anchor named. Most of the pricing evidence in this field is
second-hand or worse, and the plan says so wherever it leans on it.

## 1. The answer

Do not charge for anything for roughly nine months. Never charge for the content. Keep every
issue, the archive, the thesis page and the machine surface free permanently, and rule out
sponsorship from security vendors permanently and in public. Then, if and only if the cadence has
held for twelve consecutive issues and organizations have started asking unprompted, sell one
narrow thing: an annual organizational licence, about $3,000 (a guess), sold by conversation,
which buys access to the author around a public record and gates nothing.

The reason is what the asset is. Across the sixteen publications studied, none keeps a standing,
scored, public record of its own past calls. That record is the rare thing here, and an append-only
lock manifest makes it checkable. A record nobody can check is worth nothing, so gating it destroys
the asset. The paid data lane is already occupied by Return on Security, whose data platform is
$199 a month with an MCP server and a $79 a month API add-on (both fetched), and which is one of
this site's own sources. This site sells judgment and its track record, or it sells nothing.

## 2. Who pays, for what, at what price, in what order

| Order | What | Who | Price | Evidence for the price | Precondition |
|---|---|---|---|---|---|
| 0, now | Nothing. The site is a credibility asset for the owner's existing advisory and account work. | Nobody | $0 | Not applicable. The return is real and cannot be attributed, which is its one weakness. | A named pilot list of ten to thirty of the right people |
| 1, months 4 to 7 | A free quarterly scored recap: every verdict of the quarter against what happened, misses named | Nobody | $0 | Not applicable | Twelve or so issues to recap |
| 2, months 8 to 12 | **Annual organizational licence**: a seat on the quarterly walk-through, a standing right to ask a question, internal circulation rights with attribution. No gated content. | Vendor competitive-intelligence or strategy teams, practice leaders at other resellers and integrators, CISO leadership teams, a conference or professional body | **$3,000 a year, range $2,400 to $6,000. A guess.** | Anchors, both fetched: Return on Security Signal Pro is $2,388 a year; The Information Pro is $999 a year. No team pricing below enterprise level was found anywhere, so there is no true comparable. | Twelve consecutive signed issues, two published recaps, three unprompted organizational enquiries, the employment question answered in writing, intent amended |
| 3, from month 9, inbound only | Briefings: the judgment applied live to one organization's situation | The same buyers | $2,500 to $7,500 each. A guess. | The nearest anchor is second-hand (an analyst firm's day rate of $5,000 to $15,000) | The same, capped at two a quarter, and preferably treated as the owner's own advisory work outside this project |
| Low priority | A voluntary supporter tier with no perks | Individual readers | $9 a month. A guess. | Fetched comparable: Return on Security's backer tier at $12 a month with "no extra perks" | A payment provider, which is an owner gate. Expect almost nothing: the median paid conversion of 0.62 percent is second-hand, and at a thousand readers it means six people. |

**One thing a real conversation would settle better than this whole file.** The $3,000 figure
carries the plan and rests on no comparable. One honest conversation with one plausible buyer
would tell the owner more than all the pricing research did.

## 3. What is free, permanently

Every signed issue at its permanent address. The whole archive. The thesis page with its verdict
ledger, condition statuses and corrections. The quarterly recap. The machine surface: the thesis
endpoint, the issue data, the lock manifest, the Markdown copies and the feed. The site should say
this in one sentence on `/method/`, because saying it is part of the value (rubric D11 L5-2).

## 4. What not to do

- **No sponsorship from any security vendor, ever, and say so on the site.** The owner works for
  a company that resells security products. Money from a judged vendor into the personal
  publication of someone who influences a reseller's recommendations has the shape of an
  inducement whatever anyone intends. The Phase 1 monetization research recommended a rate card on
  day one; this plan rejects that.
- **No paid archive, at any size.** The archive is the track record.
- **No paid data layer, no metered API, no paid MCP server.** That lane is taken, and this site
  would be selling a worse copy of a product it cites.
- **No migration to Ghost or Substack.** The static build with immutable issues and a public lock
  is the one property no peer has. A hosted platform would trade it for a payment button nobody
  presses yet.
- **No public rate card, no pricing page.** On a site with one issue it advertises the absence of
  readers.
- **No drift toward investors as the designed-for reader.** Intent names security leadership,
  account teams and clients, names no investors, and excludes investment advice. An investor may
  read and may even license. The line: the site may say what it believes about a segment and why,
  and never what to do about it with money.
- **No subscriber count as the measure of success.** Intent forbids optimizing traffic. The
  project's own scorecard counts qualified exposure and decisions changed.

## 5. A conflict with the brief, stated plainly

The brief's Phase 4 includes a stream, `mon/convert`, to build conversion plumbing and ship it
switched off. The outside consult argues against that, and this plan agrees. Unused commercial
code decays, it invites a later session to switch it on, and a payment link takes an hour on the
day it is actually needed. Fast building is the reason pre-building is debt and not insurance.

**Recommended scope for `mon/convert`, cut down to four small things, none of them commercial
machinery:**

1. A visible feed link and a follow line after the judgment, saying what arrives and how often.
2. One sentence saying what is free and will stay free.
3. The independence statement in section 7, if the owner approves its text.
4. One contact sentence for organizations, **only if the owner approves it** (rubric D11 L5-4 is
   written to pass only with that approval): "This publication takes no vendor sponsorship. If
   your organization wants this judgment applied to its situation, write to me."

No email capture (held until the 2026-10-08 review under SEC-029), no form, no price, no payment
code, no feature flag. The brief is the constitution for this run, so this is a proposed change to
it and needs the owner's yes. If he prefers the brief as written, the stream is built as written.

## 6. The path

### 90 days, from 2026-09-20

| Stage | Work | Gate out |
|---|---|---|
| 0. Two owner actions, outside this run | Choose the gather runtime (SEC-039: allowlist the cloud environment, or move to a local runner). Name the pilot list. | One issue's evidence gathered with no manual fetching. At least ten named people on the pilot list, recorded by role. |
| 1. Cadence and exposure | The thesis page, the first screen, the free machine surface, the corrections log, the cadence sentence, the visible feed. Zero commercial surface. | Four consecutive signed issues on their stated day. The 2026-10-08 review passed. Two entries in the decision-impact log. |
| 2. Distribution, still free | Only if the review opens it: an email provider and a public subscribe path. The whole commercial build of the first 90 days is the contact sentence in section 5. | Eight consecutive issues. About 150 of the right readers. Two unprompted organizational enquiries. |

### 12 months

| Stage | Work | Gate out |
|---|---|---|
| 3. Months 4 to 7 | First free quarterly scored recap. | Twelve consecutive issues, two recaps, at least one verdict that changed with its reasoning written out, three unprompted enquiries, the employment question answered in writing. |
| 4. Months 8 to 12 | The licence, one page describing it, the written independence policy. Target three licences, $9,000. That is not a business and is not meant to be. | Owner review. |
| 5. From month 9 | Inbound briefings only, quoted by conversation, at most two a quarter. | None. |

**Which timing layer binds.** Building any of this is Layer A and takes days. A $3,000 purchase
sits under most departmental approval limits, so buying behaves like Layer B. Layer B binds, and
for a reason speed cannot fix: a track record is made of elapsed calendar weeks. Twelve signed
issues take twelve weeks. First real revenue falls between months nine and fifteen.

### Twelve-month arithmetic

| Line | Cautious | Central | Optimistic | Basis |
|---|---|---|---|---|
| Consecutive signed issues | 30 | 40 | 48 | Guess; assumes cadence starts by 2026-11-01 |
| List size | 120 | 350 | 1,200 | Guess |
| Licences at $3,000 | 0 | 2 ($6,000) | 5 ($15,000) | Price is a guess |
| Voluntary supporters | not launched | about $75 | about $800 | Second-hand conversion rate |
| Briefings at $5,000 | 0 | 1 ($5,000) | 3 ($15,000) | Price is a guess |
| **Direct revenue** | **$0** | **about $11,000** | **about $31,000** | Derived |
| Indirect return | not measured | not measured | not measured | No honest way to attribute it exists |

The largest line in the central case is one day of the author's time. The central case is a small
consulting result with a publication around it. The honest reason to sell the first licence is
that it is the strongest entry the decision-impact log could ever receive: an organization paying
is independent evidence that the work is valued, which the scorecard has been unable to get for a
month.

## 7. Independence statement (proposed text, owner edits)

> No security vendor, agency acting for one, or investor in a security company may buy
> advertising, sponsorship, placement, or any influence over what this publication covers or how
> it scores. An organizational licence buys access to the author and buys no influence; licence
> holders are disclosed by category and get no advance notice of a verdict. No paid engagement may
> concern a vendor whose segment the standing thesis is scoring in that quarter. The author's
> employer is disclosed on this site.

The consult recommends disclosing the employer on every page. Whether and where to name the
employer is the owner's decision alone, and nothing in this run names it.

## 8. Conflicts with intent, as proposed amendments only

`intent.md` is not edited by this run. Stages 0 to 3 need **no** amendment: free issues, the
thesis page, the machine surface, the pilot list, a public list after the review and a free recap
are all inside intent v1.2 as written. Only stage 4 needs these, and only when it is reached.

**A. New row in Beneficiaries**

> | Organizations licensing the published judgment | Continuing access to the author's reasoning around the published record, for their own market planning | An organization's planning or positioning responds to evidence it would not otherwise have assembled |

**B. New row in the State register**

> | Direct revenue from the publication | Exploring, with a decided boundary: no revenue from any party whose segment the standing thesis scores, no published content gated, no commercial relationship influencing a verdict | Whether and how the publication is sold | Owner decision after twelve consecutive signed issues and two published quarterly recaps |

**C. New bullet under "Must not optimize"**

> - Revenue, subscriber count, or any commercial relationship at the expense of an unbought judgment. Where the two conflict, the judgment wins and the relationship ends.

One more tension, with the kickoff for this run and not with intent: the run's goal names
investors among the people who should visit weekly. Intent does not. This plan designs for
security leaders and lets investors read.

## 9. Decisions only the owner can make

| # | Decision | What it blocks | Recommendation |
|---|---|---|---|
| M-1 | Gather runtime under SEC-039 | Everything, including the project itself | Hold the one-week deadline on the cloud allowlist; if the probe fails, go local |
| M-2 | Name the pilot list | The exposure denominator, the impact log, every claim of value | Ten to fifteen people this week |
| M-3 | **The employment question.** Does the employer's outside-activity policy require disclosure or approval of this publication? Does taking payment from a partner, competitor or client need approval? Does the gift policy treat sponsorship as an inducement? | Every direct-revenue model | Ask now, in writing, while the answer is hypothetical and cheap. Nobody on this run has read those policies, and every statement here about them is unverified. |
| M-4 | Vendor sponsorship: ever? | The independence statement | Never, and publish it |
| M-5 | May this project ever earn money directly? | Amendments A to C | Allowed, not pursued until the stage 4 gate, written down so nobody guesses |
| M-6 | May an investor hold a licence? | Two buyer types | Yes, with the written line in section 4; prefer other buyers |
| M-7 | Email provider at the 2026-10-08 review | The list | Only if four issues have actually held |
| M-8 | May a payment provider ever be provisioned? | Stage 4 mechanics | Approve in principle, provision on the day of the first sale |
| M-9 | Briefings inside this project or outside it? | Whether intent needs a further change | Outside |
| M-10 | Cut `mon/convert` to the four items in section 5 | Phase 4 scope | Yes |
| M-11 | Approve the contact sentence for organizations | One sentence on `/method/` | Yes, after M-3 is asked |

## 10. The strongest case against monetizing at all

Every direct model earns about $11,000 on the central case, and the largest line is a day of the
author's time, which he can sell in his actual job without building anything. Each model costs
something that cannot be bought back. A licence gives an organization a relationship with the
person who scores its segment, and whatever the policy says, he will know who pays when he writes
the verdict. A supporter tier introduces a number that goes up and down, and such numbers change
what people write, which intent forbids. A payment provider brings an owner gate, a tax question
and a disclosure question at the employer, for four figures. A free, signed, unbought weekly
judgment is rare because nobody is paying for it. On this view monetizing is value-destroying,
because the publication's commercial function is to be free and every dollar taken directly
reduces a much larger indirect return.

**Where this plan lands.** It accepts almost all of that: zero direct revenue in the 90-day path
and zero in the cautious twelve-month case. It keeps the licence for one reason above the money.
A sum this small cannot distort a judgment, and an organization willing to pay is the measurement
this project has been unable to make. Two things end the commercial path outright: an answer to
M-3 that makes outside payment awkward, or twelve signed issues with no unprompted organizational
enquiry. In either case stop at stage 3 and keep the site as a free credibility asset.

## 11. Adversarial pass

To be completed after task T3-3.
