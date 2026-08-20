# Source verification sweep — 2026-08-20

**Scope:** all 71 canonical evidence records in `web/src/data/evidence.ts`
**Run by:** CPO, six parallel verification agents (pass one), three recovery agents (pass two)
**Status of this document:** append-only historical record. Do not edit a past run; add a new dated file.

## Correction — this sweep overstated the defect

**Read this before the sections above.** The sweep fed its agents only each record's top-level
`canonicalUrl`. The schema also has a `sourceAttributions` array carrying a per-source
`canonicalUrl`, it is rendered by `EvidenceDrawer.tsx`, and seven records already use it correctly.
Agents therefore reported claims as unsourced when their source was sitting in a field they had
never been shown.

Five of the eleven flagged records were **already correctly cited** and are not defects: B3
(Alphabet's capex commentary attributes the Q2 2026 earnings-call transcript), D7 (the Wiz claim
attributes the exact Wiz DeepSeek post an agent later went and "found"), D10 (the March 2026 launch
attributes its own PR Newswire release), D11 (the earnings call attributes `aka.ms/transcriptfy26q4`),
and D12 (Ping, BeyondTrust and Delinea each attributed). D9 likewise.

**The real defect is six records, roughly eight percent of the corpus**, not eleven at fifteen
percent:

| id | Status | Second claim needing a source |
|---|---|---|
| A3 | Fixed 2026-08-20 | Q1 2023 revenue comparison — now attributes Arista's 2023-05-01 release |
| A5 | Fixed 2026-08-20 | Orders, book-to-bill, backlog — now attributes Vertiv's Q4 2025 exhibit |
| B1 | Fixed 2026-08-20 | "Demand exceeds available capacity" — now attributes the FY26 Q4 call |
| C2 | Open | Palo Alto growth excluding acquisitions (~14% / 28% / 22%) |
| C7 | Open | Okta dollar-based net retention 107% |
| D6 | Open, partial | SEC and EIOPA/DORA are attributed; **Marsh is not** |

The three fixed records were repaired using primary sources independently located and quoted
verbatim, not by deleting the claim or rewording it to match the page.

**This error is the same class as the one recorded under "Method note" below.** There, a grep
searched a corpus containing its own definitions file and reported full coverage. Here, a
verification scoped itself to one field when the data used two. Both are a check that could only
return the answer it returned. Scope a verification against the schema, not against the subset of
it you happened to extract.

**The durable fix is a gate, not a data pass.** `verify:integrity` should fail the build when a
record's excerpt spans more than one organization or economic period and the record carries no
`sourceAttributions`. Every one of the six defects would have been caught at authoring time. That
check is owed and not yet built.


## Why this run happened

The owner set the standard on 2026-08-19: everything the site shows must be accurate, current,
and traceable, and that has to be true before the site expands to cover anything new. This is the
first full verification of the evidence base against the live sources it cites.

## What was checked

Every record was checked on three questions, independently of the others:

1. **Link.** Does the stored `canonicalUrl` still resolve, and does it land where it claims to?
2. **Excerpt fidelity.** Is every figure and every clause in the stored excerpt actually present on
   that page, matching?
3. **Supersession.** Is there visible evidence the page was corrected, restated, or updated after
   the date we recorded?

Verdicts were constrained so that a failure to read a page could never be recorded as a pass.
A blocked fetch is `UNVERIFIABLE`, never `DEAD` and never `EXACT`. The instruction given to every
agent was that a false `EXACT` is far worse than an admitted `UNVERIFIABLE`.

## Headline result

**No figure on the site was found to contradict its source.** Across every record where the page
could actually be read, every number matched. That is the result the sweep was built to test for,
and it came back clean.

The defects that did surface are all the same shape, and it is a different shape than expected.

## Results at a glance

| Verdict | Pass one | After SEC recovery |
|---|---|---|
| EXACT — every figure and clause present and matching | 39 | 46 |
| CLOSE — substance matches, wording paraphrased rather than quotable | 5 | 5 |
| DRIFT — a claim with no support at the cited URL | 4 | 8 |
| UNVERIFIABLE — page could not be read (a tooling limit, see below) | 23 | 12 |
| **Total** | **71** | **71** |

Zero records showed a figure contradicting its source. Every `DRIFT` is a missing source, not a
wrong number. The second column reflects re-reading the 11 SEC.gov records that a generic fetch
could not open; the remaining 12 unverifiable records are still in recovery.

One agent's own summary line disagreed with its own table — it reported seven exact where its rows
showed eight. The totals above are recounted from the per-record rows, not from the agents' summary
lines. An agent that miscounts its own output is a reason to recompute from primary rows every run.


## The one real defect class: a claim without a source

Four records carry a claim their cited URL does not support. In every case the figures that *are*
on the page match exactly, and a second claim bundled into the same excerpt has no support at that
URL at all.

| id | Organization | What checks out | What has no source at the cited URL |
|---|---|---|---|
| A3 | Arista Networks | $3.036B Q2 2026 revenue, +37.7% YoY | The $1.351B comparison figure for the period ended 2023-03-31 |
| A5 | Vertiv | 24% sales growth: 18% organic, 5% acquisitions, 1% FX | Organic orders +252%, book-to-bill ~2.9x, backlog $15.0B |
| B1 | Microsoft | $35,802M quarterly and $115,948M FY2026 capex | "Customer demand continues to exceed available capacity" |
| D7 | Mandiant / Wiz | The Mandiant account compromise, absent MFA, infostealer credentials | The Wiz / ClickHouse / DeepSeek claim — the URL is Mandiant-only |

Four more records have the same structural problem in a milder or already-disclosed form:

| id | Issue |
|---|---|
| D12 | Excerpt claims cover Ping Identity, BeyondTrust and Delinea; the URL documents only Ping. The record's own `limitations` field already admits this. |
| D6 | Excerpt claims span SEC, EIOPA/DORA and Marsh; the single URL is the SEC rule PDF, which could not corroborate the other two even if it loaded. |
| D10 | Excerpt describes a March 2026 launch; the cited press release is dated May 2024, so it cannot contain the claim regardless of its content. |
| D11 | Excerpt says a topic "is discussed on the call"; the cited URL is the press-release exhibit, a different document from the call. |

That is eight records, roughly eleven percent of the corpus, where a reader who clicked through
would not find what they were promised. None of it is a wrong number. All of it is a traceability
gap, which is precisely the standard this run was measuring against.

**Root cause.** The excerpt field is being used to hold a synthesized claim assembled from more
than one source, while `canonicalUrl` holds only one link. The data model allows one URL per
record, so a multi-source claim silently loses its other sources. This is a schema limitation
surfacing as an accuracy defect, not a research failure — the underlying facts appear to be real
and published, just published elsewhere.

## Pass two — SEC.gov recovery

All 11 records that SEC.gov had refused were read directly, HTTP 200, no redirects, using the
identifying User-Agent that SEC's own fair-access policy asks automated requesters to declare.
Every link resolved. None showed any sign of correction or restatement.

Seven were exact. **Four were new instances of the same defect**, which is the significant result:
recovering blocked records did not just close gaps, it found more of the one problem this sweep
identified.

| id | Organization | What checks out | What has no source at the cited URL |
|---|---|---|---|
| C2 | Palo Alto Networks | 31% revenue growth to $3.0B, $388M from CyberArk and Chronosphere | "approximately 14 percent revenue, 28 percent NGS ARR, 22 percent RPO growth excluding those acquisitions" — the strings 14%, 28%, 22%, "organic" and "excluding" return zero matches |
| C7 | Okta | Revenue $765M (+11%), cRPO $2.499B (+12%) | "DBNRR 107 percent" — the word "retention" appears zero times; this is reported in the investor deck, a different document |
| B3 | Alphabet | Capex $44.924B (Q2) and $80.598B (H1), both in the cash-flow table | "the increase in the range is primarily due to an acceleration in the delivery of capacity" — "range", "outlook", "acceleration" and "capacity" all appear zero times; this is earnings-call commentary |
| D6 | SEC / EIOPA / Marsh | The SEC final rule's cyber-incident and board-oversight disclosure content | The DORA application date and the entire Marsh cyber-insurance claim — "DORA" and "Marsh" each appear zero times in a 391KB document |

D6 was suspected structurally in pass one and is now confirmed: two of its three source
organizations are wholly absent from the only URL it cites.

**Superseded by the Correction section at the top of this document.** The count stated here
(eleven records) was wrong: it treated correctly-attributed records as defects because the agents
were only shown the top-level `canonicalUrl`. The true figure is six. Still not one wrong number.


## Link integrity

One genuine link defect:

- **D21 Hush Security.** The stored `ylventures.com` URL 301-redirects off-domain and lands on
  `prnewswire.com`. The content checks out at the redirect target, but the canonical link does not
  resolve where it claims to.

## Date and supersession notes

None of these are errors on their own; each is a discrepancy worth a decision.

- **C23 ServiceNow / Veza** — the page was edited after publication to append "Update: The Veza
  acquisition closed on March 2, 2026" to what was a December 2025 post.
- **D16 Cisco / Astrix** — same pattern: a May 2026 intent-to-acquire post with a June 29, 2026
  completion note layered on. The record's `limitations` field already discloses this.
- **C18 Orca Security** — a 2021 page carrying a `dateModified` of 2023-12-19 with no visible
  content change.
- **D2 Enterprise Technology Research** — stored publication date 2026-04-29, page byline April 1, 2026.
- **D29 Return on Security** — stored publication date 2026-08-03, issue dated August 10, 2026.
- **D4 (ISC)²** — the page identifies itself as a "first look" ahead of a fuller study, so a more
  complete figure from the same organization likely exists.

## Reachability is a property of our tools, not of the sources

Pass one returned 23 records as unverifiable. That number describes the fetching tool, not the
health of the sources, and it should not be read as a finding about the evidence base.

Two independent methods proved this. One agent, faced with SEC.gov returning HTTP 403, used the
identified-User-Agent method SEC.gov's own fair-access policy asks automated requesters to use,
and got HTTP 200 on the real documents. The same agent, faced with a PDF the fetch tool could not
parse, extracted the text from the downloaded bytes directly. It closed all eleven of its records
where other agents left theirs open. Pass two applies that method to the remaining 23.

The failure modes, kept separate because they need different fixes:

| Cause | Count | Recoverable |
|---|---|---|
| SEC.gov HTTP 403 to a generic user agent | 11 | Yes — documented identified-UA method |
| Investor-relations or newswire host timeout | 10 | Usually — retry, or a browser user agent |
| JavaScript-rendered page returning empty text | 2 | Yes — needs a real browser |

## Tooling defect worth knowing about

On one record, the fetch tool returned a **completely unrelated document** — a Check Point earnings
PDF in place of the requested IANS Research report. It surfaced only because that agent read the
downloaded bytes directly rather than trusting the tool's summary of what it had fetched.

This is the most serious finding in the run, and it is not about the site. Any unattended
verification pipeline that trusts a fetch tool's own account of what it retrieved can silently
verify a claim against the wrong document and report a pass. Verification must read the artifact,
not the tool's description of the artifact.

## Method note for the next run

Two rules earned by this run:

1. **Never let the search corpus contain the thing being searched for.** An earlier check in this
   session reported every evidence id as referenced, because the grep ran over a directory that
   included the definitions file, so every id matched its own definition. Five records were actually
   orphaned.
2. **A check that returns nothing is not a check that passed.** A gate perturbation in this session
   returned no verdict because the perturbation broke the file's syntax and the script crashed
   before reaching the assertion. An empty result must fail loudly.

## Disposition

Corrections that are factual and unambiguous are applied directly. Anything that needs a source we
do not yet have, or a judgment call the owner owns, goes to `BACKLOG.md` under SEC-020 rather than
being guessed at. Nothing in this report was fixed by rewording a claim to match whatever the page
happened to say.
