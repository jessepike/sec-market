# Signals operating model

## 1. Control

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-SIG-OPS-001` |
| **Model version** | `v0.1` |
| **Status** | `mapping — lead reviewed 2026-08-16` |
| **Date** | 2026-08-16 |
| **Authority** | D-33 |
| **Owner** | sec-market-lead |
| **Governing intent** | `SEC-MARKET-001` v1.1 |
| **Related artifacts** | [durable-signals-job.md](durable-signals-job.md), [startup-source-catalog.md](startup-source-catalog.md), [web-mvp-product-contract.md](web-mvp-product-contract.md) |

This document is the operating model for how Pulse stays current. It is not a build spec. No collectors, scrapers, schedulers, or databases are authorized by this artifact.

---

## 2. The weekly loop (one paragraph)

Each week, a gatherer reads the latest Return on Security **Security, Funded** post and spot-checks the allowed specialist VC portfolio pages for names and rounds not yet in the curated feeds. A synthesizer turns raw captures into a short section read, five lead headlines, domain heat chips, and a longer background list — with source URLs, excerpts, and conflicting amounts shown honestly. A human checker signs the published market call (if it changes), the first-screen headlines, and the “why it might matter” framing before anything ships. A poster (or the sync session) updates versioned static data in the repo and opens a human review; production deploy follows the standing local → GitHub → Vercel path only after that review. The site remains a frozen edition refreshed on a human clock, not a live ticker.

---

## 3. Jobs

| Job | What they do | What they must **not** do | Time budget |
|---|---|---|---|
| **Gatherer** | Read RoS weekly post; scan CV deal-flow articles when new; browse the eight specialist VC portfolio pages and YL Ventures news for new names, round labels, or “first partnered” dates; capture company, date, round, amount (if stated), investors, source URL, and a short excerpt into a working packet (markdown or spreadsheet). | Scrape blocked sources (Funded Startups Daily, Crunchbase bulk, YC filtered URLs via bot); invent amounts; republish CV body text; touch `web/` or deploy; auto-publish. | **45–60 min/week** (RoS day) + **15 min** spot-check on VC pages |
| **Synthesizer** | Dedupe events; resolve conflicts (show both amounts with sources); draft the Activity section read (one paragraph), pick five lead headlines, assign domain heat chips, rank `lead` / `more` / `background` surfaces; write provisional “why it might matter” notes; flag gaps and thin portfolio-only names. | Dump every captured row to the first screen; force a market call when evidence is thin; treat raises as ARR or buyer spend; publish without human sign-off. | **30–45 min/week** after gather |
| **Human checker** | Sign or reject the section read and five headlines; confirm attribution and conflicting amounts; decide whether the published market call changes (usually it does not on a funding week); approve background demotions and “no series” handling. | Skip review because “it’s just a list”; let weekly news alone trigger a call change; approve a 50+ row link dump. | **20–30 min/week** |
| **Poster** | Prepare a clean static-data diff (activity read, items, evidence links) for the sync session; open a review note listing what changed and what stayed frozen; hand off — do not prod-deploy. | `vercel --prod` from a dirty tree; push to `main` without human checker approval; auto-publish scorecard judgment. | **15–20 min** when posting (often every 2–4 weeks, not every gather week) |

Fresh agents: any role can be one person in a manual week; split when volume grows.

---

## 4. Cadence

| Trigger | What runs | Output |
|---|---|---|
| **Weekly (RoS)** | Read new **Security, Funded** post; optional quick VC portfolio pass | Working packet of new/changed funding events; draft Activity copy if anything material |
| **Event-driven** | Mega-round (e.g. $100M+ or category-defining), material M&A close or intent, or a falsifier on Watch-next | Same pipeline on an accelerated clock; may promote one headline to `lead` between weekly RoS posts |
| **Monthly edition refresh** | Re-read Activity surfaces: demote stale `lead` items to `more` or `background`; confirm the published market call still holds; align edition date display | Static edition bump even if no mega-event — **not** “refresh because news happened” |

**Do not** treat daily security news as a refresh trigger. Weekly RoS is the spine; everything else is garnish or event-driven.

---

## 5. First durable slice: startups only

**Scope:** new cybersecurity companies, launches, and funding — not M&A (second feed, see §6).

**Allowed sources (10)** — from [startup-source-catalog.md](startup-source-catalog.md):

| # | Source | Role in the loop |
|---:|---|---|
| 1 | SYN Ventures portfolio | Round + year; best VC timing signal |
| 2 | Forgepoint companies | First-partnered year; sector tags |
| 3 | Team8 portfolio | Founded year; builder/launch signal |
| 4 | Ballistic portfolio | New names; homepage investment posts |
| 5 | Cyberstarts portfolio | Active Israeli cyber bets |
| 6 | YL Ventures news | Dated portfolio announcements |
| 7 | Evolution Equity companies | Cyber-only names; thin on amounts |
| 8 | Paladin portfolio | Name + blurb; pair with news |
| 9 | **Return on Security — Security, Funded** | **Spine:** dated rounds, amounts, investors, weekly market read |
| 10 | **Cybersecurity Ventures VC articles** | **Spine:** periodic deal roundups with amounts |

**Optional manual add:** Y Combinator cybersecurity list (browse only; no automated query URLs).

**What the first collection week proved:** almost all **dated** startup raises in the packet came from RoS weekly posts plus one Cybersecurity Ventures article. The eight portfolio pages mainly supplied **names and categories**, often without amounts or exact dates. A 58-row raw dump fails the product bar; the site needs one section read, five headlines, and heat chips on the first screen — not a spreadsheet pasted into HTML.

**Gather order each week:**

1. RoS **Security, Funded** (subscribe or read the post — do not rely on RSS bots; Cloudflare blocks non-browser fetch).
2. Check CV hub for a new linked deal-flow article since last read.
3. Scan VC portfolios for net-new names or round labels not already in (1)–(2).
4. Record misses explicitly (e.g. generalist-led seed with no cyber VC page yet).

**Event record fields** (when capturing — see catalog for full list): company, category, event_date, event_type, round, amount, investors, source_url, excerpt, why_it_might_matter, confidence, collector, collected_at.

---

## 6. How M&A joins later (second feed)

M&A is **out of scope** for the first durable slice. A parallel **M&A source catalog** (same shape as the startup catalog) will map where public cyber deal news actually lives. When that catalog is lead-reviewed:

- M&A events use the **same Activity surface** on the site (`lead` / `more` / `background`) but a **separate gather pass** and separate working packet.
- RoS and CV may cover some deal news; the M&A catalog will name additional lawful sources — not designed here.
- **One human checker** still signs combined first-screen headlines (five slots shared across funding + M&A, not five of each).
- Startup gather cadence stays weekly on RoS; M&A gather stays **event-driven** (announce, close, intent) unless the M&A catalog identifies a repeatable weekly surface worth adding.

Do not merge startup and M&A source research into one catalog; keep provenance and job boundaries clear.

---

## 7. What “post” means

**Post** does not mean “push to production immediately.” It means:

1. **Update versioned static data** — activity read, `ActivityItem` rows, linked evidence IDs, edition date — in the repo’s data layer (owned by the sync session; this ops model does not edit `web/`).
2. **Open a human review** — short note: what changed, what is `lead` vs background, what evidence supports each headline, and explicit “no call change” if the scorecard call is unchanged.
3. **Hand off to the sync session** — preview on OrbStack dev server → commit clean tree on `main` as `jesse@keatingpike.com` → `git push origin main` → Vercel builds that commit (D-31).

**Prohibited:** CLI prod upload of a dirty working tree; auto-publish of the scorecard market call; shipping without human checker approval on headlines and read.

Judgment memo / full “The read” stays off the first screen per product contract.

---

## 8. Quality bar

**World-class** for Pulse capital activity means:

- **Insight** — one honest section read (“capital, not buyer spend”; domain pattern; what changed this window).
- **Attribution** — every lead headline opens to source title, date, URL, and excerpt in the evidence drawer.
- **Conflicting amounts shown** — if RoS says $X and a company blog says $Y, show both with sources; do not pick silently.
- **Progressive disclosure** — five headlines on the first screen; expand for notes and sources; older window events collapse to Background.
- **Not a ticker** — no auto-refresh, no “just now,” no implied completeness.

**Fails the bar:** 58-row link dump; invented ARR; undisclosed amounts promoted to certainty; weekly news as an excuse to change the infrastructure lag call without new evidence.

Reference: D-32 sequence — packet → owner + lead critique → design only after the packet survives a sharp San Francisco reader.

---

## 9. What we will not automate (now)

| Category | Status |
|---|---|
| Databases, scrapers, browser automation, schedulers | **Not authorized** |
| Auto-publish of market call or Activity headlines | **Not authorized** |
| Funded Startups Daily bulk extract | **ToS-blocked** |
| RoS RSS / bot fetch | **Unreliable** (Cloudflare); manual read |
| The Signal API/MCP | **Future option** — assume paid/restricted until terms reviewed |
| Light automation **named for later** (not built): weekly fetch of RoS public HTML into a local file for human review | Optional future convenience only |

Collectors and “signal pipelines” remain unauthorized until this manual loop proves decision value in account conversations and on the site.

---

## 10. 30-day operating picture — smallest repeatable loop

**Goal:** run the loop by hand next week with no new infrastructure.

| Week | Mon–Tue | Wed | Thu | Fri |
|---|---|---|---|---|
| **1** | Gatherer: read latest RoS post; 30-min VC spot-check; write packet | Synthesizer: draft read + 5 headlines + heat chips; demote nothing yet | Human checker: 20-min review with lead | If approved: poster prepares handoff doc for sync session (no deploy required week 1) |
| **2** | Same gather | Same synthesize; compare to week-1 packet for duplicates | Human checker | Post only if headline set materially changed |
| **3** | Same gather; note CV article if new | Synthesize; start `background` list for stale names | Human checker | — |
| **4** | Monthly edition pass: surfaces, edition date, call unchanged? | Owner critique of startup section (if scheduled) | Human checker signs monthly refresh | Sync session ships when owner + lead agree |

**Minimum viable week (≈2 hours total):**

1. Read RoS **Security, Funded** (~30 min).
2. Skim Forgepoint + SYN for net-new 2026 names (~15 min).
3. Draft one read + five headlines + chips (~30 min).
4. Human sign-off (~20 min).
5. If posting: hand off static-data diff to sync session (~15 min).

**Artifacts to create each week:**

- `docs/active/startup-week-YYYY-MM-DD-packet.md` (or equivalent working file) — raw captures.
- Short review note in the handoff — what ships, what waits.

**Exit for month 1:** four weekly gathers, at least one posted Activity refresh, owner critique complete, decision on whether to keep manual or name one light automation (RoS HTML save).

---

## 11. Open risks

| Risk | Why it hurts | Mitigation |
|---|---|---|
| **RoS is the spine** | Miss a week or lose subscription → dated-round gap | Subscribe; calendar reminder; record “no post this week” explicitly |
| **Portfolio pages are thin** | Many names, no amounts — tempts filler headlines | Use portfolios for discovery only; require RoS/CV/press for dated lead headlines |
| **Generalist-led rounds invisible** | Insight/Lightspeed deals absent until cyber VC lists them | Record as known miss; optional manual SecurityWeek keyword scan |
| **Conflicting amounts** | Trust loss if we flatten to one number | Show both; lower confidence; human checker required |
| **58-row dump reflex** | Operators dismiss the product as Crunchbase-lite | Enforce five headline cap; rest in collapsed Background |
| **Weekly news ≠ call change** | Overfitting the scorecard to funding noise | Separate the startups section from the published market call; the call changes only on Watch-next falsifiers or new macro evidence |
| **Two sessions, one site** | Ops updates data; sync session owns git/Vercel | Clear handoff doc; never prod-deploy from ops session |
| **M&A not yet cataloged** | Combined Activity board may skew M&A-heavy from legacy content | Startup slice first; M&A catalog before expanding gather scope |
| **CV copyright** | Unauthorized republication | Link and excerpt only; never paste full articles |
| **Automation creep** | ToS fights and false confidence | Manual loop first; D-30 value test before any collector build |

---

## Handoff checklist (fresh agent)

- [ ] Read [startup-source-catalog.md](startup-source-catalog.md) first-week set
- [ ] Confirm RoS post date and URL for this week
- [ ] Capture into working packet with event record fields
- [ ] Synthesize: one read, five headlines, heat chips — not a full dump
- [ ] Human checker signs read + headlines (+ call if changed)
- [ ] Poster prepares static-data handoff; sync session owns commit and deploy
- [ ] Do not touch `web/`, `vercel.json`, or `intent.md` from this job
