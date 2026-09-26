# Collect brief — the twice-weekly unstructured-facts run

Version 0.1, 2026-09-26. Step 3 of `docs/active/autonomy-coverage-plan.md` (`SEC-MARKET-AUTO-001`,
D-76/D-77). This is the complete instruction for the scheduled collector that reads everything SEC
EDGAR's structured data cannot reach: funding rounds, acquisitions, layoffs, restructuring, debt,
ratings actions, going-concern language, executive changes, divestitures, shutdowns, and each public
supplier's own headline metric from its latest results release. `scripts/collect.sh` reads this file
and hands it to a headless Claude Code run under the owner's own subscription login. No human
approves what you find — sourced, checkable facts publish on their own (D-76). That also means you
publish **no judgment**: never a stance, a ranking, a forecast, or a sentence interpreting what a
fact means. State what the source says, in the source's own terms, and stop.

## 0. Ground rules, each one load-bearing

- Do not spawn sub-agents or helper agents. One session, one pass, the fixed tools you were given.
- **You do not touch git.** Do not run `git add`, `git commit`, `git push`, or any other git
  write command. `scripts/collect.sh` and the workflow that calls it own git entirely; your job
  ends when the files on disk are correct. (If a `git` command is not in your allowed tools, that
  is deliberate, not an oversight — stop trying it and move on.)
- **You do not touch `web/src/data/runStatus.ts`.** `scripts/collect.sh` writes it after you finish,
  from what you leave in `.collect/`. Writing it yourself would race that step.
- You write only within this allowlist, nothing else:
  - `web/src/data/tracker/events.ts` — append only. Never edit or remove an existing entry.
  - `web/src/data/tracker/suppliers.ts` — only the `headlineMetric`, `lastRound`, and `ownership`
    fields of an *existing* supplier record. Never add or remove a supplier record, never touch
    `domainIds`, `kind`, `ticker`, `cik`, `edgarId`, or `revenue` (that field belongs to the EDGAR
    runner, step 2, and is not yours to touch even when you find a headline metric that looks like
    revenue — see §2).
  - `web/src/data/evidence.ts` — append only, one `EvidenceRecord` per fetched document.
  - `web/src/data/generated/collectState.json` — see §4 for exactly when you may update it.
  - Scratch files under `.collect/` (gitignored, never committed) — see §5.
- Fetch every document with `curl` from Bash so you hold the actual bytes. Do not use a
  summarizing fetch tool. For PDFs use `pdftotext` if present, otherwise `strings`; if neither
  yields readable text, record the source as unreadable in `.collect/failed-sources.json`.
- Fetch SEC.gov with a descriptive User-Agent:
  `curl -sL -A "SecurityMarketPulse research jesse@keatingpike.com"`. A host that blocks you is
  recorded as unreadable. Never bypass a block, never use a proxy, never retry more than three
  times.
- Compute `sha256sum` (or `shasum -a 256` — both are allowed; use whichever exists) of every
  document's bytes before you quote from it. Record the hash, the exact URL you fetched, and
  today's date in the evidence record's `retrieval` field.
- Every fact you write down is something you actually read in a fetched document, not something an
  aggregator or search snippet told you. Confirm the document you received is the one you asked
  for — company name, date — before quoting it. For an EDGAR hit, confirm the filer name and CIK
  match the issuer you intended.
- **One factual line per event. No interpretation, no adjective that isn't in the source, no
  causal claim the source didn't make.** The build gate (`web/scripts/verify-tracker.ts`) fails the
  whole run on any of these words anywhere you write: leading, strong, weak, solid, healthy,
  concerning, accelerating, struggling, winning, fading. There is no way around this gate and no
  reason to want one — state what happened, in the source's words or a plain paraphrase of them,
  and let the reader judge.
- Record "none found" and move on. An empty supplier is an empty supplier. Never invent a fact to
  fill a category, never round a number, never guess a date.
- If a source fails three attempts, mark it unreadable in `.collect/failed-sources.json` and move
  on to the next.

## 1. The sourcing ladder — read before you write a single event

`docs/active/fable-run/research/11-distress-signal-sources.md` §5 sets the rule. Five rungs,
strongest to weakest:

1. Company's own SEC filing (8-K, 10-Q, 10-K) — EDGAR, `sec.gov`, `data.sec.gov`.
2. A rating agency action, as republished by the company or a wire service.
3. A state WARN Act notice, from the state agency itself.
4. A confirmed primary corporate action — the acquirer's own press release, an 8-K disclosing a
   deal, or a company/parent's own statement, from the company's newsroom, GlobeNewswire, PR
   Newswire, Business Wire, or an SEC filing.
5. Trade press, including anonymous-sourced reporting.

**Rungs 1 through 4 may publish an event on their own. Rung 5 never may — it is a lead to a primary
document, nothing more.** If trade press is the only thing you can find for a claim, use it to find
the company's or acquirer's own statement or filing and cite that instead. If no rung 1–4 source
exists anywhere, do not write the event — note the trade-press lead and what you could not confirm
in `.collect/candidates.json` or `.collect/failed-sources.json` (your judgment which fits better)
and move on. `web/scripts/verify-tracker.ts` hard-fails the build on any event tagged `rung: 5`, so
writing one is never a shortcut, only a wasted event.

Every claim carries its source's own date, not the date you read about it in a roundup. If a
secondary source pointed you to a primary document with no clear date, drop the item rather than
inventing or estimating one.

## 2. What to look for, per supplier

You were given, in the prompt that invoked this brief, a since-date and (for a restricted run) a
list of supplier ids to cover. Only look at suppliers on that list, and only for facts dated **after**
the since-date and on or before today.

Read `web/src/data/tracker/suppliers.ts` for the current record of each supplier you're covering —
its `id`, `kind`, `ticker`/`cik` if public, and what it already has for `headlineMetric`, `lastRound`,
and `ownership`. Read `web/src/data/tracker/events.ts` for its existing events, so you do not
duplicate one and so you know the highest existing `EV-<supplier>-N` number to continue from. Read
`web/src/data/evidence.ts` for its existing `TR-<supplier>-N` evidence ids, so you continue that
numbering too rather than colliding with it.

For each supplier, look for facts of these kinds, each dated after the since-date:

- **New funding round.** `type: 'funding'`. Update `lastRound` on the supplier record only if this
  round is newer than what's already there.
- **Acquisition** announced or closed, by the supplier or of it. `type: 'acquisition'`. If the
  supplier itself is the one acquired and the deal closed, update `ownership` on the supplier
  record and consider whether `kind` should become `'acquired'` — but you may not change `kind`
  yourself (§0); if the record's `kind` looks stale after your finding, say so plainly in your
  final output so a person can make that edit, and do not silently leave `kind` wrong without
  saying so.
- **Layoffs** — company statement, state WARN notice, or an 8-K. `type: 'layoff'`.
- **Restructuring** — SEC 8-K Item 2.05 or a company's own statement of a restructuring plan.
  `type: 'restructuring'`.
- **Debt raised or refinanced.** `type: 'debt'`.
- **Credit ratings actions** — the agency's own press release, republished by the company or a wire.
  `type: 'rating'`.
- **Going-concern language** — from a 10-Q or 10-K liquidity/going-concern section. `type:
  'going-concern'`.
- **CEO or CFO change.** `type: 'exec-change'`.
- **Divestiture.** `type: 'divestiture'`.
- **Shutdown.** `type: 'shutdown'`.
- **For public suppliers only: the company's own headline metric from its latest results release**
  (the 8-K's EX-99.1 exhibit), when it is newer than what `headlineMetric` already shows. This is
  the company's own named metric — ARR, NGS ARR, subscription ARR, billings, whatever the company
  itself leads with — never GAAP revenue, which the EDGAR runner (step 2) already covers from
  structured XBRL data and which you must not touch (`revenue` field, `web/src/data/generated/
  edgarFacts.json`). Write this as both a `results`-type event and an update to `headlineMetric` on
  the supplier record.

A single primary document (e.g. one 8-K or one results release) often supports more than one event
— a results release naming both a new ARR figure and a restructuring charge is two events, one
evidence record, both evidence ids pointing at the same `TR-` entry. That is normal and expected;
do not force one event per evidence record.

## 3. Suppliers not on the declared list

If, while reading a primary source, you notice a security company that plausibly belongs in one of
the twelve domains (`web/src/data/tracker/domains.ts`) but is not in `web/src/data/tracker/
suppliers.ts`, **do not add it.** Write it to `.collect/candidates.json` instead — name, likely
domain, one line of why it came up, and the source URL. That file is not committed; a person
reviews it later and decides whether to add the supplier as a deliberate data edit.

## 4. `web/src/data/generated/collectState.json`

This file holds one thing: the date through which the full declared supplier list has been checked.
Shape:

```json
{
  "lastSuccessfulCollectDate": "2026-09-25",
  "lastRunAt": "2026-09-25T14:03:11Z"
}
```

**Update it only when this run covered every supplier on the declared list — no restriction in
effect.** The prompt that invoked you says plainly whether this run is restricted to a named subset
of suppliers. If it is restricted, leave this file exactly as you found it (or, if it does not exist
yet, do not create it) — advancing the watermark on a partial run would make the next full run skip
suppliers nobody actually checked. If this run is unrestricted and completes, set
`lastSuccessfulCollectDate` to today's date (the since-date for the *next* run) and `lastRunAt` to
the current UTC timestamp.

**You will also see a `collectorRun` field in this file.** That block is script-owned —
`scripts/collect.sh` step 6 writes it after you exit, and `scripts/auto-publish.sh` writes it too on
a held or failed publish. It is `web/src/data/runStatus.ts`'s one input alongside
`generated/edgarFacts.json` (AUTO-001 fix pass 2, item 4 — see that file's header comment for the
derivation). You never write it yourself; the two fields above are still the only ones this brief
asks of you.

## 5. What to leave in `.collect/` for `scripts/collect.sh`

Create the directory if it doesn't exist. Write these, even when empty:

- `.collect/failed-sources.json` — a JSON array of short strings naming every source that failed to
  load after three attempts (e.g. `"Moody's press release for Sophos"`, `"California EDD WARN
  portal"`). Empty array if nothing failed.
- `.collect/candidates.json` — a JSON array of objects for suppliers you noticed but did not add
  (§3). Empty array if none.
- `.collect/summary.txt` — a short plain-text summary for the run receipt: how many suppliers you
  checked, how many new events you wrote, how many evidence records, and one line per new event
  (supplier, type, date). This is read by a person reviewing the run, not published anywhere.

## 6. Before you stop

Reread every event and evidence record you wrote. For each one: does the `text` say only what the
source said, with no added judgment? Does every `evidenceIds` entry resolve to a real record you
just wrote, with a real `canonicalUrl` and a `retrievedAt` or `publicationDate`? Is every date on or
before today and after the since-date? Is every `rung` between 1 and 4? If any answer is no, fix it
or drop the item — do not leave something in that you know is wrong and hope the gate catches it.

Your final message: how many suppliers you covered, how many new events and evidence records you
wrote, what you flagged in `.collect/candidates.json`, and what failed to load. Nothing else.
