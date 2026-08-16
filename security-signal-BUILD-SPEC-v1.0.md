# Security Signal Pipeline — BUILD SPEC v1.1

> **Handoff notice — not authorized for implementation:** `intent.md` is the governing authority. Partner-risk-first Phase 1, the Varonis backtest gate, T0–T5 scoring, West/NorCal-first delivery, and the production pipeline described here are not authorized. Use this document only as a historical mechanism proposal until a later accepted intervention explicitly promotes part of it.

**For:** coding session (Cowork / Codex / Claude Code)
**Companion doc:** `security-signal-workflow-spec-v0.4.md` — that's the *reasoning* document. This is the *build* document.

---

## 0.0 Revision note — v1.0 → v1.1 (2026-08-14, CTO review)

v1.0 was internally inconsistent in ways a builder would have discovered only after building the wrong thing. Corrections, each traceable to the section it changed:

| # | What was wrong in v1.0 | Fixed in |
|---|---|---|
| 1 | The acceptance test was unreachable by the build order. Eight of the ten indicators need document text or market data; the build order fetched filing *metadata* only. | §2.3, §5 |
| 2 | Two different backtests. §2.5 said cutoff 2026-06-23, bar = Watch. §5 step 6 said cutoff 2026-06-01, bar = 10. | §2.5, §5 |
| 3 | No market data source existed, yet indicators 7 and 8 (4 of the 11 backtest points) require one. | §2.3 |
| 4 | No scoring lookback window. Scores could only ever rise; every entity reaches Active eventually. | §2.4 |
| 5 | `facts` declared append-only corrections and then defined a primary key that rejects them. | §3 |
| 6 | `events` had no idempotency. A daily re-read of the same 8-K double-counted and fired a false tier change. | §3 |
| 7 | `risk_scores` keyed on a DATE, so same-day re-runs and backtest replays collided and polluted the live series. | §3 |
| 8 | `signals` table (v0.4 §8.2) was missing from the "shared across all phases" contract. | §3 |
| 9 | `client_exposure_note` appeared in the alert record with no home in the schema and no stated source. | §2.6, §3 |
| 10 | Scope guard forbade "LLM-generated analysis," which reads as forbidding the text *extraction* indicator 3 requires. | §0 |
| 11 | D-15 referenced "Cut F"; v0.4 §8.5 defines cuts A–E only. | §4 |
| 12 | Nothing consumed the `runs` table. A pipeline that stops fetching looks identical to one with nothing to report. | §6 |

Three questions were surfaced rather than answered, because they are the owner's call: **D-14** (answered, see §4), **D-16** (alert threshold), **D-17** (calibration set breadth). Two open items are flagged inline where they bite: the Varonis workforce-reduction announcement date, and the repository's location relative to the ePlus confidentiality boundary.

---

## 0. How to use these two documents

**Historical instruction only:** do not hand this file to a coding agent as current authority. Begin with `README.md`, `intent.md`, and the current accepted episode packet.

v0.4 describes an eleven-domain analytical system with four signal layers. Handed to a builder as-is, it produces a sprawling half-finished thing. This file specifies one working slice at a time, each independently valuable.

**Scope guard — do NOT build in Phase 1:** composite indices, lag correlation, tempo board automation, cuts, the website, or any LLM-generated *analysis, synthesis, or narrative*. Those come after the plumbing is proven.

**The guard does not forbid extraction.** Pulling a stated fact out of a filing (a retention-rate direction from MD&A, a headcount reduction percentage from a press release) is deterministic capture with a `source_url` attached, and indicator 3 cannot be built without it. What is forbidden is a model *interpreting* what those facts mean. Extraction writes to `events` and `facts` with provenance. Interpretation writes prose, and prose waits for Phase 4.

---

## 1. Phase plan

| Phase | Deliverable | Why this order |
|---|---|---|
| **1** | **Partner & ownership risk monitor** | Free structured source, immediate standalone value, real deadline pressure (deals in flight), and it exercises the full pipeline shape end to end. |
| **2** | Earnings time-series backfill (12 qtr × 14 core entities) | Reuses Phase 1 storage and fetch patterns. Unlocks trend analytics. |
| **3** | Demand-side signals (job postings, transcript terms, startup formation) | Highest analytical value, but depends on Phase 2 storage being proven. |
| **4** | Synthesis + scorecard rendering | Only worth building once there's enough data to synthesize. |

**Phase 1 is done when it flags a real partner situation you didn't already know about.** That's the gate to Phase 2.

---

## 2. Phase 1 — Partner & Ownership Risk Monitor

### 2.1 Problem statement
ePlus signs multi-year agreements with partners and places clients on those platforms. Ownership change — PE take-private, strategic acquisition, distress — materially alters roadmap, support, pricing at renewal, and integration commitments. **All of the leading indicators are public and filed.** Nobody is watching them systematically.

### 2.2 Watchlist
Every ePlus security partner that is publicly traded. Start with the Core 14 + Extended 8 from v0.4 §4. Store as config, not code — the list will churn.

Each entry: `ticker | company | cik | domains[] | eplus_partner (bool) | tier (core|extended) | exposure_class`

`domains[]` is a list **in the config file** and loads into the `entity_domains` junction table (§3), not into a JSON column. `exposure_class` is one of `incumbent | finalist | evaluated | none` — see §2.6 on why this is a class and not an account name.

### 2.3 Data sources — all free, no auth

Sources divide into three access classes, and the distinction is load-bearing: **only two of the ten indicators in §2.4 are obtainable from filing metadata alone.** A build that stops at the submissions API cannot score this model.

**Class A — filing metadata.** Filing type, date, accession number, 8-K item codes.

| Source | Endpoint | Fetch | Feeds indicators |
|---|---|---|---|
| SEC submissions API | `data.sec.gov/submissions/CIK##########.json` | daily | 5, 10 (Item 5.02); filing-event spine for all others |

**Class B — document text.** Required by indicators 1, 3, 4, 6. These facts live in prose, not in item codes.

| Source | Endpoint | Fetch | Feeds indicators |
|---|---|---|---|
| SEC EDGAR full-text search | `efts.sec.gov/LATEST/search-index?q=...` | daily | 1 (advisor retention / "strategic alternatives" language) |
| Filing documents | `www.sec.gov/Archives/edgar/data/<cik>/<accession>/...` | on new filing | 3 (retention/NRR direction from 10-Q MD&A), 4, 6 |
| SEC 13D/G index | submissions API, form types `SC 13D`, `SC 13D/A` | daily | 2 (filer identity requires reading the cover page) |
| Company IR press releases | per-company RSS/JSON where available | daily | 4, 6 (layoffs and guidance often never file an 8-K) |

> **Verify before building:** the full-text search endpoint is undocumented and the SEC has changed it before. Isolate it behind an adapter with a recorded-fixture test so a shape change breaks one seam, not the pipeline. If it moves, indicator 1 degrades to press-release matching rather than failing the run.

**Class C — market data.** Required by indicators 7 and 8, which are 4 of the 11 points in the §2.5 backtest. v1.0 omitted this class entirely.

| Source | Endpoint | Fetch | Feeds indicators |
|---|---|---|---|
| Daily close prices | Stooq CSV (`stooq.com/q/d/l/?s=<ticker>.us&i=d`) | daily | 7 (TTM return per entity) |
| Sector index proxy | same, ETF ticker (`cibr.us` or `hack.us`) | daily | 7 (the benchmark to underperform against) |
| Shares outstanding, cash, debt | **already have it** — `companyfacts` XBRL (`dei:EntityCommonStockSharesOutstanding`, `CashAndCashEquivalentsAtCarryingValue`, `LongTermDebtNoncurrent`) | quarterly | 8 (enterprise value numerator) |

**The useful consequence:** enterprise value is derivable from EDGAR plus a close price. The only genuinely external datum in the whole system is a daily price series, and Stooq serves that free with no key and no account. **No paid market data vendor is required for Phase 1.** If Stooq proves unreliable, the fallback is a free-tier keyed provider, which changes the secrets story but not the design.

**Class D — structured financials.** Phase 2's spine, pulled in Phase 1 because indicator 8 needs the balance-sheet items anyway.

| Source | Endpoint | Fetch | Purpose |
|---|---|---|---|
| SEC company facts | `data.sec.gov/api/xbrl/companyfacts/CIK##########.json` | quarterly | revenue, margin, structured financials; EV inputs for indicator 8 |

**SEC access rules.** A descriptive `User-Agent` header with a contact email is mandatory. Rate limit 10 req/sec across all `sec.gov` hosts, not per host. No API key. Cache aggressively — filings are immutable once posted, so the cache key is the accession number and it never expires.

### 2.4 Risk indicators — the detection model

Each indicator is independently observable from public filings. Score, don't binary-flag.

| # | Indicator | Source | Weight |
|---|---|---|---|
| 1 | "Exploring strategic alternatives" / advisor retention language | 8-K, PR | 5 |
| 2 | 13D filed by PE firm or activist | SEC 13D | 5 |
| 3 | Disclosed retention/renewal deterioration, 2+ consecutive quarters | 10-Q, transcripts | 4 |
| 4 | Workforce reduction announced | 8-K, PR | 3 |
| 5 | CEO or CFO departure | 8-K Item 5.02 | 3 |
| 6 | Guidance withdrawn or cut | 8-K, PR | 3 |
| 7 | Stock underperforming sector index >30% TTM | market data | 2 |
| 8 | EV/revenue multiple <60% of peer median | derived | 2 |
| 9 | Insider selling acceleration | Form 4 | 1 |
| 10 | Board composition change | DEF 14A, 8-K | 1 |

**Tiers:** 0–4 Normal · 5–9 **Watch** · 10–14 **Elevated** · 15+ **Active**

#### 2.4.1 Scoring window (added v1.1)

v1.0 defined weights but never said over what period an indicator counts. Without a window a score can only ever rise, stale history accumulates, and every entity on the watchlist drifts to Active over a few years. Score is always computed **as of a date**, and each indicator has a stated life:

| Indicators | Life | Rationale |
|---|---|---|
| 1, 2 (strategic alternatives, 13D) | **Persist until resolved**, 24-month backstop | A live strategic review or an unwithdrawn 13D is a standing condition, not an event. Resolution means the deal closed, the review was publicly concluded, or the 13D was withdrawn. Record the resolution as its own event. |
| 4, 5, 6, 9, 10 (layoff, exec departure, guidance, insider selling, board change) | **Trailing 12 months** | Discrete events. A CFO who left fourteen months ago is not current evidence. |
| 3 (retention deterioration) | **Most recent report, requires 2+ consecutive quarters** | Carries its own window by definition. Drops to zero on the first quarter that reverses. |
| 7, 8 (relative stock, EV/revenue) | **Current state at `as_of`** | Point-in-time ratios, recomputed every run, never accumulated. |

Every score row therefore reproduces exactly from `as_of` plus the event and price history, which is also what makes the backtest harness possible at all.

### 2.5 Acceptance criteria — the Varonis backtest

*(v1.0 stated this test twice with different parameters: cutoff 2026-06-23 and bar "Watch" here, cutoff 2026-06-01 and bar "≥10" in the build order. Reconciled below to the stricter of the two.)*

**Single canonical test. The model must score Varonis at Elevated (≥10) with `as_of = 2026-06-01`, using only data captured before that date.** The 2026-06-23 Bloomberg report is the outcome being predicted, and a three-week buffer keeps the test honest about leakage rather than merely reconstructing a known headline.

Expected contributions: October 2025 renewal-rate deterioration disclosure (#3, 4), workforce reduction (#4, 3), stock down ~44% vs. sector (#7, 2), EV/rev ~3.9x vs. ~7.3x peer median (#8, 2). **Expected score 11 → Elevated.**

> **Confirm before relying on this number:** the workforce-reduction announcement date must fall before 2026-06-01. If it lands between 06-01 and 06-23, the expected score at this cutoff is **8 (Watch)**, and the choice is to move the cutoff to 2026-06-23 or lower the bar to Watch. Resolve by checking the filing date, not by adjusting weights. **Weights are never tuned to make the test pass** — that inverts the whole exercise.

**Second requirement: no false positive on a healthy vendor.** Fortinet, CrowdStrike and Cloudflare must stay below the alert threshold across the same window. What "below the threshold" means is **D-16**, open: Watch begins at 5, and one exec departure plus a board change plus insider selling reaches 5 on a company in perfect health.

**Third requirement, added v1.1: more than one positive case.** Ten weights fitted against a single known outcome is overfitting by construction. The recent record has enough resolved take-privates and activist situations to calibrate against properly — see **D-17**. A model that only recognizes Varonis has learned Varonis, not distress.

All three conditions must pass.

### 2.6 Output

**Alert record** (on tier change only — never re-alert an unchanged state):
```
company | prior_tier | new_tier | score | triggered_indicators[] |
filing_urls[] | first_observed | client_exposure_note
```

Tier change is derived by comparing the current `risk_scores` row against the most recent prior row for the same entity and scenario. No separate alert table is required; the score series *is* the state.

**`client_exposure_note` (clarified v1.1).** v1.0 named this field without giving it a source or a home, and it is the field that turns a market observation into something a rep can act on. It is **hand-maintained on `entities`**, not derived, because no public source knows which clients sit on which platform. It is also the field that makes this repository confidential: a populated `client_exposure_note` means the store holds ePlus client relationships alongside vendor distress scores.

**Consequence, and it needs deciding before any client name is entered:** if this field is populated, the repository sits inside the ePlus engagement boundary and inherits its confidentiality rules. If the intent is a general market instrument that stays outside that boundary, the field must hold a **non-identifying exposure class** (`incumbent` / `finalist` / `evaluated` / `none`) with the named accounts staying in the cockpit. **The second option is the recommended one** — it preserves the operational value of the alert while keeping this store publishable and free of account names.

**Weekly digest**, plain Markdown, only companies at Watch or above. Per company: what changed, which filings, and the **structural consequence** — not speculation.

**Language discipline (hard rule).** Report observable facts and structural consequences. Never speculate about a pending deal.

- ✅ "Varonis disclosed renewal softening in Oct 2025, reduced headcount 5%, and publicly confirmed it is exploring strategic options. If they are an incumbent or finalist: put ownership change in the risk register, confirm support SLAs, get roadmap commitments in writing, keep a second option warm."
- ❌ "Varonis is probably getting bought by Thoma Bravo."

The first is correct and useful whether or not a deal happens, sourced entirely to public disclosure. The second is the version that eventually burns you.

---

## 3. Data contracts

Shared across all phases. Get this right in Phase 1 and Phases 2–4 inherit it.

```sql
CREATE TABLE entities (
  entity_id      TEXT PRIMARY KEY,
  name           TEXT NOT NULL,
  ticker         TEXT,
  cik            TEXT,
  layer          TEXT NOT NULL,      -- infra | security | context
  tier           TEXT NOT NULL,      -- core | extended
  eplus_partner  INTEGER NOT NULL,
  exposure_class TEXT,               -- incumbent | finalist | evaluated | none  (§2.6, hand-maintained)
  hq_region      TEXT,
  status         TEXT NOT NULL,      -- active | acquired | frozen
  frozen_reason  TEXT                -- D-9: freeze + annotate, never rewrite history
);

-- v1.1: domains extracted from a JSON blob into a junction table. Phase 3 aggregates
-- startup formation BY DOMAIN (v0.4 §5.4); a JSON column cannot be joined or indexed.
CREATE TABLE entity_domains (
  entity_id TEXT NOT NULL REFERENCES entities(entity_id),
  domain    TEXT NOT NULL,
  material  INTEGER NOT NULL DEFAULT 1,   -- feeds the 3-vendor minimum, v0.4 §6.1
  PRIMARY KEY (entity_id, domain)
);

CREATE TABLE facts (
  entity_id       TEXT NOT NULL,
  period_end      DATE NOT NULL,    -- ALWAYS index on this, NEVER fiscal label
  fiscal_label    TEXT,             -- display only
  metric          TEXT NOT NULL,
  value           REAL,
  unit            TEXT,
  yoy_pct         REAL,
  organic_flag    TEXT NOT NULL,    -- reported | organic | guidance
  source_url      TEXT NOT NULL,
  confidence_tier TEXT NOT NULL,    -- T0..T5
  captured_at     TIMESTAMP NOT NULL,
  -- v1.1: captured_at IS PART OF THE KEY. Without it, invariant 2 below is
  -- unenforceable: a correction row collides with the row it corrects.
  PRIMARY KEY (entity_id, period_end, metric, organic_flag, captured_at)
);

-- Current value of any fact = the row with the greatest captured_at. Never DELETE the old one.
CREATE VIEW facts_current AS
SELECT f.* FROM facts f
WHERE f.captured_at = (
  SELECT MAX(f2.captured_at) FROM facts f2
  WHERE f2.entity_id = f.entity_id AND f2.period_end = f.period_end
    AND f2.metric = f.metric AND f2.organic_flag = f.organic_flag
);

CREATE TABLE events (
  -- v1.1: event_id MUST be deterministic, not random. Derive it as
  --   sha256(accession_no || ':' || item_code || ':' || entity_id)   [filings]
  --   sha256(source_url || ':' || event_date || ':' || indicator_id) [press releases]
  -- and write with INSERT OR IGNORE. A daily job re-reads the same 8-K every run;
  -- without this the same event scores repeatedly and fires a tier change that is
  -- an artifact of the scheduler, not the market. Caching is not idempotency.
  event_id       TEXT PRIMARY KEY,
  entity_id      TEXT NOT NULL,
  event_date     DATE NOT NULL,
  event_type     TEXT NOT NULL,     -- ma | filing | layoff | exec_change | guidance | funding | regulatory
  indicator_id   INTEGER,           -- maps to §2.4
  detail         TEXT,
  resolved_at    DATE,              -- v1.1: §2.4.1 — indicators 1 and 2 persist until resolved
  resolution     TEXT,              -- closed | withdrawn | concluded
  source_url     TEXT NOT NULL,
  captured_at    TIMESTAMP NOT NULL
);
CREATE INDEX idx_events_scoring ON events (entity_id, event_date, indicator_id);

CREATE TABLE risk_scores (
  -- v1.1: `scenario` added. Backtests write under their own label and never touch
  -- the live series; same-day recomputation replaces rather than collides.
  scenario    TEXT NOT NULL DEFAULT 'live',   -- live | backtest:<name>
  entity_id   TEXT NOT NULL,
  as_of       DATE NOT NULL,
  score       INTEGER NOT NULL,
  tier        TEXT NOT NULL,
  indicators  TEXT NOT NULL,        -- JSON array of triggered ids
  run_id      TEXT,
  PRIMARY KEY (scenario, entity_id, as_of)
);

-- v1.1: demand-side series (v0.4 §5, §8.2). Absent from v1.0 despite §3 claiming
-- to be the contract Phases 2-4 inherit. These are NOT facts: a req count is
-- observed on a scrape date, not reported for a fiscal period, so it cannot share
-- the period_end key without lying about what it is.
CREATE TABLE signals (
  signal_type     TEXT NOT NULL,    -- job_reqs | transcript_term | analyst_event | startup_formation
  signal_key      TEXT NOT NULL,    -- keyword, term, category name
  entity_id       TEXT NOT NULL DEFAULT '',   -- '' = domain-level aggregate (§5.4)
  domain          TEXT NOT NULL DEFAULT '',   -- '' = entity-level series
  observed_at     DATE NOT NULL,
  value           REAL,
  denominator     REAL,             -- total open reqs etc. §5.1 mandates ratio, never absolute
  source_url      TEXT NOT NULL,
  confidence_tier TEXT NOT NULL,
  captured_at     TIMESTAMP NOT NULL,
  PRIMARY KEY (signal_type, signal_key, entity_id, domain, observed_at, captured_at)
);
-- NOTE: entity_id and domain use '' rather than NULL deliberately. SQLite permits
-- NULLs in a non-INTEGER PRIMARY KEY and treats each as distinct, so a nullable
-- key column silently stops deduplicating. This bites every project that hits it once.

CREATE TABLE runs (
  run_id         TEXT PRIMARY KEY,
  started_at     TIMESTAMP,
  finished_at    TIMESTAMP,         -- v1.1: NULL on a crashed run — that is the health signal
  phase          TEXT,
  scenario       TEXT NOT NULL DEFAULT 'live',
  entities_hit   INTEGER,
  entities_stale INTEGER,
  errors         TEXT
);
```

**Non-negotiable invariants:**
1. **`period_end` is the join key.** Never `fiscal_label`. CrowdStrike Q1 FY27, Palo Alto Q3 FY26, Zscaler Q3 FY26, Okta Q1 FY27, and SentinelOne Q1 FY27 all end 2026-04-30. Joining on label silently compares different calendar periods.
2. **Append-only.** Corrections write a new row with a later `captured_at`. Never UPDATE a fact. *(Enforceable only because `captured_at` is in the primary key — v1.0's key made this invariant a comment.)*
3. **As-reported, never restated.** Restatements are new rows, flagged.
4. **`source_url` is NOT NULL.** No provenance, no row.
5. **Acquired entities freeze** (D-9). Never fold history into the acquirer.
6. **Every write is idempotent** (v1.1). Re-running any fetch for any date must leave the store byte-identical. The scheduler will re-run, the backtest will replay, and a retry will duplicate — the schema has to make that harmless rather than the code having to remember.
7. **Scores are reproducible from history** (v1.1). Any `risk_scores` row must recompute exactly from the events and prices available at its `as_of`. This is what makes the backtest a test rather than a demonstration.

---

## 4. Blocking decisions

| ID | Decision | Blocks | Recommendation |
|---|---|---|---|
| **D-2** | Backfill depth | Phase 2 | 12 quarters. 8 absolute minimum — below that, seasonality can't be separated from trend. |
| **D-11** | Startup data source | Phase 3 | Crunchbase/PitchBook are paid. Start with press-release parsing; upgrade if the signal proves out. |
| **D-12** | Analyst source access | Phase 3 | Does ePlus have a Gartner seat? If yes, §5.3 of v0.4 becomes the strongest signal cheaply. If no, public Hype Cycle summaries only. |
| **D-14** | Where does this run and what's the schedule? | Phase 1 | **Answered v1.1 — see below.** |
| **D-15** | Does client-facing output need marketing/legal review? | External publication of any cut (v0.4 §8.5 defines cuts A–E; v1.0's "Cut F" does not exist) | **Resolve before anything is published externally.** Cheaper to know the constraint now than to design around it later. |
| **D-16** | What tier constitutes an alert, for the false-positive test in §2.5? | Phase 1 acceptance | **Elevated (10+) alerts; Watch appears in the weekly digest but does not alert.** Watch begins at 5, and three minor indicators reach 5 on a healthy company, so alerting at Watch guarantees the noise that kills adoption of a monitor. The digest still shows Watch, so nothing is hidden. |
| **D-17** | How many historical cases calibrate the weights? | Phase 1 acceptance | **Five to eight resolved positives plus the healthy control set.** Ten weights against one case (Varonis) is fitting to a single story. Candidates from the recent record: Splunk/Cisco, SailPoint, Ping, ForgeRock, Darktrace, Sumo Logic, and Rapid7's activist episode. Confirm the list and the dates before using them; each needs a verified pre-announcement cutoff or it teaches the model nothing. |

### D-14 — Answered (CTO, v1.1)

**Run it as a launchd job on `macbook2014` writing to local SQLite, registered in the portfolio jobs registry so jobs-agent owns its health.** Schedule: daily at 06:00 local for the fetch and score, weekly Monday 07:00 for the digest render.

The workload argues for the simplest possible answer. Twenty-two entities against free endpoints, a few hundred kilobytes a day, no secrets beyond a `User-Agent` string, and no inbound surface. That is a cron job, and treating it as anything more is over-building.

- **Not the host Mac.** Host protection rules keep runtimes off it. Develop in the OrbStack dev VM, deploy to `macbook2014`.
- **Not GitHub Actions.** It would work, but SQLite state then lives in git and every run produces a commit-back, which turns an append-only store into a merge-conflict surface.
- **Not Supabase yet.** Correct answer the moment Phase 4 needs the scorecard readable from more than one device. Wrong answer now: it adds auth, secrets and a network dependency to a job whose entire value is that it runs unattended and cheaply.
- **One caveat on the host.** `macbook2014` already has an unrotated-log problem in another service. Add a `newsyslog.conf` entry for this job's output at deploy time rather than inheriting the same defect.

**Migration trigger to name now:** when the scorecard needs multi-device reads or the store passes roughly a gigabyte, move to Supabase. The schema in §3 is portable as written, so that migration is a data copy and not a redesign.

---

## 5. Phase 1 build order

*(Reordered in v1.1. v1.0's order reached the backtest at step 6 having built only the filing-metadata path, which supplies 2 of the 10 indicators and roughly 4 of the 11 points the test demands. The test could not have passed, and the likeliest failure mode was a builder quietly reweighting until it did.)*

1. Config: watchlist YAML with tickers and CIKs
2. Schema: SQLite, DDL above, including `signals` and `entity_domains`
3. Fetcher A — **Class A metadata**: EDGAR submissions API, one entity, cached by accession, correct `User-Agent`
4. Parser A: 8-K item codes → `events` rows, **deterministic `event_id`, INSERT OR IGNORE**  → *indicators 5, 10*
5. **Idempotency test before going further.** Run step 3 and 4 three times against the same entity. Row counts must be identical after each. If they are not, stop; everything downstream inherits inflated scores.
6. Fetcher B — **Class C market data**: daily close series per entity plus the sector index → *indicators 7, 8 (EV from `companyfacts`, no paid vendor)*
7. Fetcher C — **Class B document text**: filing documents and IR press releases → *indicators 1, 3, 4, 6*
8. Scorer: §2.4 weights **within the §2.4.1 windows**, `as_of`-parameterized → `risk_scores`
9. **Backtest harness: `as_of = 2026-06-01`, scenario `backtest:varonis`. Varonis must reach Elevated (≥10). Fortinet, CrowdStrike and Cloudflare must stay below the D-16 alert threshold across the same window. Weights are not tuned to pass.**
10. Expand the backtest to the D-17 calibration set
11. Expand to full watchlist
12. Delta detection: tier change against the prior `risk_scores` row, scenario `live`
13. Run-health check: stale-run and stale-entity alarm (§6)
14. Digest renderer: Markdown

**Stop at step 14.** Do not start Phase 2 until the Phase 1 gate (§6) is met.

**The order is not arbitrary.** Steps 6 and 7 exist before the scorer because a scorer built against two available indicators encodes assumptions that quietly survive when the other eight arrive. Step 5 exists before anything is scored because idempotency is not retrofittable once a month of duplicated events is already in the store.

---

## 6. What "done" looks like

- Runs unattended on a schedule, no manual intervention
- Every alert traces to a filing URL
- Zero alerts above the D-16 threshold on healthy vendors across a 12-month backtest
- Re-running any date changes nothing in the store (invariant 6)
- Weekly digest is short enough to read in two minutes
- Someone else could add an entity to the watchlist without reading the code

**Run health (added v1.1).** v1.0 created the `runs` table and then never read it. **A monitor that has silently stopped fetching is indistinguishable from a monitor with nothing to report**, and that is the characteristic way this class of system dies: not with an error, but with a quiet run of empty weeks that everyone reads as calm. Two alarms, both cheap, both required before this counts as done:

- **Stale run** — no row in `runs` with a non-NULL `finished_at` in 48 hours.
- **Stale coverage** — `entities_stale` exceeds 20% of the watchlist on any run, meaning fetches are failing per entity while the job itself still reports success.

Both route to the same channel as the digest. The weekly digest also states coverage completeness explicitly, so a light week reads as a light week and never as silence.

### 6.1 Phase 1 gate (revised v1.1)

v1.0 gated Phase 2 on "flags a real partner situation you didn't already know about." That is the right *intent* and an unusable *gate*: it hands the schedule to the market, and if no partner has a situation for a year, Phase 2 waits a year for a permission slip nobody can issue.

**Phase 1 is done when either condition is met:**

- it flags a real partner situation ahead of your knowing it, **or**
- it passes the D-17 calibration set with no false positive above the D-16 threshold, **and** has run unattended for 60 days with clean run health.

The first is the better evidence. The second is the one that is guaranteed to arrive.
