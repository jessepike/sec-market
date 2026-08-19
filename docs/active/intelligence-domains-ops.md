# Domain vendor intelligence — how we operate

One page per operating model; vendor tables in [domain-vendor-signals-2026-08.md](domain-vendor-signals-2026-08.md) and watch lists in [domain-coverage-map.md](domain-coverage-map.md).

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-INT-DOMAIN-001` |
| **Updated** | 2026-08-17 |
| **Live surfaces** | Prints table, Tempo board (dated posture + horizon + producing evidence), edition delta in `web/src/data/edition.ts` |

---

## Question we answer (per domain)

**For each security domain — Network/SASE, Cloud, Data, Identity, SecOps, AI Runtime — are public vendors accelerating, splitting, or silent — and what should we PREPARE vs WATCH?**

Vendor **prints** = disclosed revenue/ARR where it exists. **Capital** (raises, valuations) stays on Activity, labeled not ARR.

---

## Six domains — at a glance

| Domain | Posture on site | Question we answer | Companies we follow (6 each) |
|---|---|---|---|
| **Network / SASE** | PREPARE | Is refresh live while SASE splits? | Fortinet, Zscaler, Cloudflare, Check Point, Cato, Netskope |
| **Cloud security** | WATCH | Is capacity activating without a CNAPP spend series? | Wiz, PANW cloud, CrowdStrike cloud, Orca, Aqua, Upwind |
| **Data / AI security** | PREPARE | Are data vendors up while AI governance capital runs ahead? | Rubrik, Varonis, Cyera, BigID, Sentra, Securiti |
| **Identity** | WATCH | IGA up, workforce IAM flat, agentic identity unproven? | Okta, SailPoint, CyberArk, Lumos, Entra/Ping/PE PAM |
| **SecOps** | WATCH | XDR recovery vs platform SecOps drag? | SentinelOne, CrowdStrike, Cisco SecOps, Torq |
| **AI runtime** | WATCH | Intent strong, bookings unproven? | Survey + Activity capital (Zenity, Onyx) |

**Vendor coverage today:** six Cloud rows (Wiz, Falcon Cloud, Upwind, Orca, Aqua, Prisma AIRS) plus five to eight names per other domain on the prints table.

---

## Where we get domain signals

### Public vendors (prints board)

| Signal type | Source | Refresh |
|---|---|---|
| **Quarterly earnings / ARR** | Company IR, SEC 10-Q/10-K, earnings call transcripts | **Each earnings season** (~4×/year per vendor; staggered fiscal calendars) |
| **Private ARR milestones** | Company press (Cato, etc.) | **When issued** — event-driven |
| **Segment metrics** | Earnings calls (e.g. CrowdStrike Falcon Cloud ARR) | **Quarterly** |

**Fiscal calendar note (examples):** CrowdStrike FY ends Jan; Zscaler Apr; Fortinet calendar; Netskope Jan FY. We map prints to **calendar quarters on the panel** per methodology note on site.

### Private / startup names (Activity + watch list)

| Source | Use |
|---|---|
| RoS + SecurityWeek + VC portfolios | Names entering domain (see funding/M&A ops docs) |
| [domain-coverage-map.md](domain-coverage-map.md) | 12–14 watch names per domain for weekly desk |

---

## Refresh cycle

| Cadence | Action | Surfaces updated |
|---|---|---|
| **Quarterly earnings wave** | Pull new prints for vendors that reported | Prints table, Tempo copy |
| **Weekly desk** | New private names affecting domain heat | Activity, optional Tempo note |
| **Monthly** | Re-read domain postures vs prints — tags change only with decision. Date any change, write the edition delta, keep the prior state. | Tempo tags, `asOf`, `edition.ts` |
| **Event-driven** | Private ARR press, segment breakout, major M&A in domain | Prints or Activity |

**Last vendor pass:** 2026-08-16. **Last prints ship:** Cato, Netskope, Falcon Cloud, Upwind, Torq on live site.

---

## Insight & decisions per domain

| Domain | Current read (live) | Decision it drives |
|---|---|---|
| Network/SASE | Appliance hot; SASE split (Cato/Netskope > Zscaler organic) | Prepare network refresh accounts; don’t claim SASE wave |
| Cloud | Falcon Cloud segment strong; CNAPP names on table with equity or GTM | Qualify when workloads go live |
| Data | Rubrik/Varonis up; DSPM capital and M&A on table | Prepare data/AI only where sensitive data in production |
| Identity | SailPoint up; Oak/Hush capital on table | Ask when machine identities go live |
| SecOps | S1/CRWD healthy; Cisco FY SecOps weak | Share-shift story, not new SecOps cycle |
| AI runtime | Capital heat; survey intent ≠ bookings | Do not run specialist motion from intent alone |

---

## Signal quality (honest)

| Strength | Limitation |
|---|---|
| **High** on public vendor quarterly prints with SEC/IR | Private vendors may only have last disclosed equity or GTM news |
| **High** when segment disclosed (Falcon Cloud) | Bundled SKUs (Entra, PANW organic vs headline) |
| Domain postures capped by Episode 002 | Cannot call RUN without a new research decision |
| Prints table populated per domain | Private ARR often unavailable — labeled capital vs revenue |

**Value:** Strong for **vendor tempo and account qualification**. Weak for **predicting your pipeline** without client-specific data.

---

## Next actions

- **Account teams:** Use Tempo + prints for “is this domain live in the market?” questions.
- **Lead:** Fill Orca/Aqua only when a **public** signal appears — do not invent.
- **Do not:** Change PREPARE/WATCH tags from funding news alone.
