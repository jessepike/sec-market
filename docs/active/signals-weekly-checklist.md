# Signals weekly checklist

One-page runbook for a fresh agent. **~2 hours total.** Plain English. **Do not ship** — stop for human sign-off.

---

## Control

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-SIG-WEEKLY-001` |
| **Version** | `v0.1` |
| **Authority** | [signals-operating-model.md](signals-operating-model.md) |
| **Owner** | sec-market-lead |

---

## Before you start (~5 min)

- [ ] Read [signals-operating-model.md](signals-operating-model.md) — jobs, cadence, quality bar
- [ ] Read [startup-source-catalog.md](startup-source-catalog.md) and [ma-source-catalog.md](ma-source-catalog.md) — allowed sources only
- [ ] Confirm last week’s packet in `docs/active/signals-week-YYYY-MM-DD.md` (if any) so you do not re-dump old rows
- [ ] Create this week’s file: `docs/active/signals-week-YYYY-MM-DD.md` (use today’s date)
- [ ] Set status to `desk-run — lead review pending`

**Prohibited every week:** edit `web/`, deploy, build scrapers, auto-publish, change `intent.md` or the published market call without human checker approval.

---

## 1. Gather — Return on Security (~30 min)

- [ ] Open https://www.returnonsecurity.com/ and find the **latest** **Security, Funded** post (not an essay or partner piece)
- [ ] Record post number, title, URL, publish date, and the **week window** stated in the intro (e.g. “week of August 3rd, 2026”)
- [ ] If a newer issue will not load, use the newest one that **does** load and say so in the packet control block
- [ ] Read **Funding By Company** — capture every product-company round in that week’s window
- [ ] Read **Mergers & Acquisitions** in the **same post** — capture every deal listed
- [ ] Note **Market Summary** counts (deals, disclosed total, categories) for the draft read
- [ ] Do **not** rely on RSS or curl alone — Cloudflare often blocks bots; use browser or WebFetch that returns full HTML

**Capture per funding event:** company, category, event_date (week or date from source), round, amount, investors, source URL, short excerpt, confidence (`high` / `medium` / `low`).

**Capture per M&A deal:** acquirer, target, category, value, prior funding if stated, source URL, excerpt, confidence.

---

## 2. Spot-check VC portfolios (~15 min)

- [ ] **SYN Ventures** — https://www.synventures.com/portfolio — any **2026** round labels or new active names not already in the RoS post?
- [ ] **Forgepoint** — https://forgepointcap.com/companies — any **First Partnered 2026** or new sector tags not in RoS?
- [ ] If you find net-new names **without** dates or amounts, list them under “portfolio-only discoveries” — do **not** promote them to lead headlines without press/RoS backing
- [ ] Honor Forgepoint `Crawl-delay: 3`; no query-string URLs

---

## 3. Optional garnish (~10 min)

- [ ] **SecurityWeek M&A roundup** — only if a **new month** posted since last gather: https://www.securityweek.com/category/cybersecurity-funding-news/ma/
- [ ] Skip if nothing new; RoS weekly pass is the spine
- [ ] Do not paste full article bodies — link and excerpt only

---

## 4. Synthesize (~30 min)

- [ ] Dedupe against prior week packets — this file is **this week only**, not a cumulative summer dump
- [ ] Target **8–15 funding events** from the RoS window (product companies first; note service/media rounds separately)
- [ ] Include **all M&A rows** from the same RoS post (product + service; label type)
- [ ] Draft **one section read** (3–4 sentences): what pattern moved capital this week; attribute Return on Security; no boom/bust hype
- [ ] Draft **five headlines** — funding and/or M&A share the five slots; mega-deals or strategic acquirers may take a slot
- [ ] Draft **three heat chips** (domain labels, e.g. Agent governance · CTEM / offense · SSPM)
- [ ] Flag **conflicts** — two amounts for one round, undisclosed values, SEC filing “may be incomplete” caveats
- [ ] Flag **missing amounts** and thin portfolio-only names explicitly
- [ ] State **published market call** — almost always **no change** (weekly funding ≠ Episode macro call)

---

## 5. Stop for human sign-off (~20 min — not your job to skip)

- [ ] Set packet status: `desk-run — lead review pending`
- [ ] Hand to **human checker** (lead): sign or reject section read + five headlines + heat chips
- [ ] Human decides whether the **published market call** changes (default: **frozen**)
- [ ] **Do not ship** — no `web/` edits, no commit to static data, no deploy from this job

---

## 6. After approval (poster / sync session — usually later)

- [ ] Poster prepares static-data handoff when checker approves and posting is warranted
- [ ] Sync session owns commit, preview, and Vercel — see operating model §7

---

## Artifacts

| Artifact | Path |
|---|---|
| This checklist | `docs/active/signals-weekly-checklist.md` |
| Weekly working packet | `docs/active/signals-week-YYYY-MM-DD.md` |

---

## Time budget

| Step | Minutes |
|---|---|
| Read ops model + prior packet | 5 |
| RoS Security, Funded (funding + M&A) | 30 |
| SYN + Forgepoint spot-check | 15 |
| Optional SecurityWeek roundup | 10 |
| Synthesize read + headlines + chips | 30 |
| Human sign-off (checker) | 20 |
| **Total** | **~110 min (~2 h)** |

---

## Exit (desk agent)

- [ ] Checklist exists and matches this run
- [ ] Week packet exists, sourced from verifiable RoS URL
- [ ] Funding count and M&A count stated in control block
- [ ] Five draft headlines and “market call unchanged” (or explicit change request) recorded
- [ ] No code, no `web/` edits, no auto-publish
