# SEC-009 execution plan

One page. This is what the lead steers from. Not a new Governing Intent.

| Field | Value |
|---|---|
| **Governs** | [intent.md](../../intent.md) `SEC-MARKET-001` v1.1 (`84619b48`, 2026-08-16, clean) |
| **Job** | [BACKLOG.md](../../BACKLOG.md) SEC-009 — living public-signal intelligence on the website |
| **Authority** | D-28, D-36, D-39, D-40, D-41 |
| **Owner babysitting** | Only if the **published market call** would change |

---

## Where we are

The site is live. The frozen infrastructure-lag call is on the page, with a judgment layer, a prints table, and Tempo joined to the new vendor rows.

That is still a **one-shot research edition plus a capital board that is a month behind the story**. SEC-009 is not done until the Activity board is the current edition and a desk loop can refresh it without reinventing the project.

| Surface | Live now | Next |
|---|---|---|
| Market call | Episode 002 NO-CALL — frozen | Do not touch unless evidence forces an escalate |
| The read / prints / Tempo | Shipped `8b16cfe` | Maintenance only |
| Activity | Old leads (Wiz, CyberArk, Cyera, Onyx, Astrix) | Fable rewrite, held for a newer RoS than #256 |
| Desk | Checklist + #256 packet exist | Run when #257+ exists, then ship |

---

## One goal

**A reader can open the site, see what moved in funding and M&A this window, and decide what to prepare or ignore — from sourced evidence, in two minutes.**

Not a new section. Not a RoS reprint. Not a 58-row dump. The next edition of the existing Activity board.

**Increment exit (done):**

- Activity edition is **live** on https://securitymarketpulse.com
- Window label matches the newest Return on Security Security, Funded issue that existed at ship
- Five shared lead slots + section read match D-36
- Avoid line and Activity board do not contradict
- Published market call **unchanged** unless the lead escalates to the owner
- Vercel Ready on that commit; live JS contains the new leads (Zenity / Oak / Hush / Oasis / Onyx) and not Wiz as lead

**Prep exit (done before RoS exists):**

- This plan is on `main`
- Activity data + D19–D29 sit on `cursor/activity-edition-ready`, rebased on current `main`
- Lead has already checked the five headlines against the live Avoid line
- Desk runbook is the existing checklist — no new process
- **Lead check 2026-08-16:** five headlines vs live Avoid line — **pass**. New leads are this-window capital. Wiz/CyberArk move to background, which is what Avoid is for. Market call stays frozen.

---

## Loops (run without asking)

### Loop 1 — RoS desk → Activity ship

When https://www.returnonsecurity.com/ shows a Security, Funded issue **newer than #256**:

1. Gather per `signals-weekly-checklist.md` (RoS + SYN + Forgepoint). No scrapers.
2. Diff against the August Activity draft. Keep D-36 spine unless a new issue **breaks** it.
3. Lead-check five headlines + read + Avoid. Default: market call stays frozen.
4. Update `web/src/data/activity.ts` + evidence on the ready branch.
5. Preview on OrbStack. Build + lint.
6. Merge to `main` as `jesse@keatingpike.com`, push, confirm Vercel Ready, curl live JS.
7. Stop. Do not invent the next episode.

If no newer issue exists: do not sit idle on this loop — the increment is **blocked**, not the project. See Loop 2.

### Loop 2 — Live-page honesty

If the live page contradicts itself (prints vs Tempo vs Avoid vs Activity), fix and ship. Do not change domain **tags** or the market call.

### Loop 3 — Stop / escalate

Stop and tell the owner only when:

- the published market call would change
- a source conflict cannot be resolved from official pages / RoS / filings
- a deploy would require `vercel --prod` or a dirty tree

Do **not** stop to ask whether to keep working, whether to plan again, or whether Orca/Aqua are ready.

---

## Out of this increment

Scrapers, archive, Gate S1 collector, account-prompt copy, new Startups nav, Orca/Aqua hunt, weekly public refresh (cadence is **monthly edition**).

---

## Current block

Return on Security #256 (2026-08-10) is the latest Security, Funded post. #257–#258 are not published. Loop 1 cannot finish until one of them exists. Typical next post: the following Monday.
