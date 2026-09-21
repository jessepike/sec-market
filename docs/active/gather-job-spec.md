# Gather job specification — the Tuesday draft

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-GATHER-001` |
| **Version** | v0.2 — amended 2026-09-03 after external review |
| **Status** | specification, being built under D-64 |
| **Date** | 2026-09-03 |
| **Governs** | SEC-028 |
| **Parent** | [weekly-issue-plan.md](weekly-issue-plan.md) WS-C; [weekly-issue-spec.md](weekly-issue-spec.md) for the data it writes |
| **Intent** | `SEC-MARKET-001` v1.2: a machine may retrieve, extract, compare and propose; only a named person signs or publishes |

## 1. Job

Every Tuesday, draft the issue for the ISO week that ended the previous Sunday, as a pull request
against `preview`. Every figure in the draft is quoted verbatim from a document the job fetched
with `curl` and read as bytes. The job proposes; it never signs, never applies a judgment, never
publishes, and never touches `main`.

## 2. Runtime

A **Claude Code cloud routine** (a scheduled cloud session with its own checkout of
`https://github.com/jessepike/sec-market`). Chosen over a launchd job on macbook2014 because it needs
no host, no runtime install, no Forge or jobs-agent dependency, runs on the subscription, and its run
logs are inspectable from any session.

| Setting | Value |
|---|---|
| Schedule | Tuesdays 06:00 America/Los_Angeles = `0 13 * * 2` UTC (winter: 14:00 UTC; accept the drift) |
| Model | `claude-sonnet-5` |
| Tools | Bash, Read, Write, Edit, Glob, Grep. No WebFetch: every document is fetched with `curl` so the job holds the bytes it quotes and can hash them |
| Sources | the repo, checked out at `preview` |
| Connectors | none. The job needs nothing but the public web and the repo |
| Prompt | `docs/active/gather-brief.md`, read from the checkout, so the brief is versioned with the data model |

The routine's prompt is one line: read `docs/active/gather-brief.md` from this checkout and do
exactly what it says. That keeps the operative instructions in git, reviewable, and on `preview`.

## 3. What the job produces

One pull request, branch `issue/<id>` where `<id>` is the ISO week being drafted (`2026-w38`), base
`preview`, containing:

1. `web/src/data/issues/<id>.ts` — a draft `Issue` (shape in the issue spec §3): `status: 'draft'`,
   `weThink.thesis: null`, `weThink.postureDeltas: []`, `weThink.summary: ''`, signature fields null,
   and `proposed` filled with the machine's proposal.
2. `web/src/data/issues/index.ts` with the new issue appended last.
3. New evidence records appended to `web/src/data/evidence.ts`, exactly one per fetched document,
   each with a verbatim `excerpt`, `canonicalUrl`, `retrievedAt`, and a `retrieval` receipt (final
   URL, sha256 of the bytes, fetch time, locator such as a page or section). An excerpt never spans
   documents; an item cites several records instead.
4. The PR body, in this order: the one-line read the job proposes; what it found per lane with counts;
   proposed posture deltas as text, never applied; sources it could not read and why; what it
   deliberately left out and why; the exact commands it ran and their exit codes.

The PR is the whole output. Nothing else is written, and nothing is pushed anywhere but `issue/<id>`.

## 4. Sources, fixed

The target list is closed. The job reads these and nothing else, in this order.

| Lane | Source | How |
|---|---|---|
| Formation | Return on Security, latest *Security, Funded* issue | fetch the post; summarise and link; never republish body text |
| Formation | Cybersecurity Ventures VC hub | look for a new deal-flow article since the last issue |
| Formation | Eight specialist VC portfolio pages named in `docs/active/startup-source-catalog.md` | new names or round labels only |
| Absorption | SecurityWeek M&A tag; SEC EDGAR full-text search for 8-K items 1.01 and 2.01 from the issuers in `prints.ts` | fetch each hit; quote the deal terms |
| Absorption | Acquirer press releases linked from the above | verbatim price and stated materiality |
| Prints | Investor-relations pages and SEC filings for the issuers in `prints.ts` whose fiscal quarter closed in the last five weeks | earnings release and 10-Q or 10-K; quote the figure and its period |
| Capital and backdrop | The hyperscaler and infrastructure issuers already in `panelRaw.ts`, same rule | quarterly capex figure and any demand-versus-capacity sentence |

The exact URLs and query templates live in the brief's source manifest and are versioned with it.
The VC list is read from `docs/active/startup-source-catalog.md` and the issuer lists from
`prints.ts` and `panelRaw.ts` at run time, so the brief has no second copy to drift. An EDGAR hit is
quoted only after the filer name and CIK are confirmed against the intended issuer.

SEC.gov is fetched with the identified `User-Agent` its access policy asks for. A host that blocks
is recorded as unreadable, never bypassed, and never retried through a proxy. Return on Security is
read once, summarised, and linked.

## 5. Rules the job obeys

Each of these is a lesson this project has already paid for.

- **No sub-agent spawning.** The brief forbids it. One session, one pass, fixed list.
- **A summary is not a document.** The job reads the bytes it downloaded before quoting them. If a
  fetch returns something other than the requested document, the source is recorded as unreadable.
- **Every figure is verbatim.** An evidence record's `excerpt` is copied from the document, not
  paraphrased. A figure that cannot be quoted does not enter the draft.
- **Record none found and move on.** A source with nothing new yields a one-line note in the PR body
  and no item. An empty lane is an empty lane.
- **Proposes, never signs or applies.** The job's read, no-calls and posture
  suggestions go in `proposed` on the draft and in the PR body, labelled as a machine proposal. It
  never writes `weThink.thesis`, `weThink.postureDeltas`, a signature, `domains.ts`,
  `hypotheses.ts`, `market.ts`, `meta.ts`, `intent.md`, `decisions.md`, or any prior issue.
- **Gates before push.** The job runs `npm run verify:edition`, `verify:panel`, `verify:integrity`
  and `verify:issue` in its sandbox and includes the exit codes in the PR body. A failing gate does
  not block the PR; it is reported at the top of the body so the reviewer sees it first.
- **Zero readable sources is a failure.** If nothing could be read, the job still opens the PR, with
  the body's first line stating that, and exits non-zero so the run shows as failed.
- **Output is capped.** At most eight items per lane in the draft. More than that goes to the PR body
  as a list of what was left out.
- **Never `main`.** The brief names the branch and base explicitly and says so.

## 6. The review ritual

Tuesday or Wednesday, twenty to thirty minutes, owner:

1. Open the PR. Read the body top to bottom.
2. Open the preview deploy of the branch. Read the draft issue as a reader would.
3. Cut anything thin. Edit headlines and "why it matters" freely.
4. Form your own view. Change anything in `proposed` you do not accept, then approve the pull
   request or comment `publish` (D-73, `docs/active/publish-path-spec.md`). The publish workflow
   signs `proposed` under your name with that day's date, locks the issue, runs every check and
   publishes. The thesis is no longer a weekly verdict; it lives at `/thesis/`. Signing by hand in a
   session still works: set `weThink`, `proposed: null`, `signedBy`, `signedOn`, `published`,
   `status: 'published'`, and run `npm run verify:issue -- --write`.
5. If the branch's Vercel build failed, do not merge on the strength of the PR body; fix or reject.
6. Merge to `preview`. Promote with `PROMOTE=1` after the render check.

`verify:issue` refuses a build where a published issue lacks a signature, still carries a
proposal, or names a signer other than `AUTHOR_NAME`.

## 7. First run

The routine is created disabled with a `run_once_at` for a dry run during the build, so its first
PR can be inspected and the brief corrected before the schedule is armed. Arming the Tuesday schedule
is the last step of SEC-028 and is recorded in the PR that closes it.

## 8. Acceptance

- The routine exists, points at the repo, reads the brief from the checkout, and is disabled until
  the dry run passes.
- The dry run opens a PR on `issue/<id>` against `preview` with the three artefacts in §3 and a body
  in the order given.
- Every evidence record in the PR carries a verbatim excerpt and a URL that resolves.
- The job wrote to nothing outside `web/src/data/issues/<id>.ts`, `web/src/data/issues/index.ts`
  and `web/src/data/evidence.ts`.
- Exit codes for all four gates appear in the PR body.
- The brief is committed at `docs/active/gather-brief.md` and is the only instruction the routine
  receives beyond "read it and do it".

## 9. Not in scope

Any collector, database, scraper farm, or second job. Any source not in §4. Any write to a judgment.
Any publish.
