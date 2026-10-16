# SEC-MARKET-LANDSCAPE-DATA-001 — Data model for the landscape page

**Status:** draft, awaiting owner authorization
**Task of two.** This one changes data and types only. The layout that consumes it is
[landscape-ui-spec.md](landscape-ui-spec.md). Do not start that one until this is merged.
**Visible change on the live site: none.** This task must ship with the page looking exactly as it does today.

## Why this exists

The site presents a single dated market call. The product it needs to be is a standing landscape
reference that a security leader, an account team, or a client can check weekly. That shift is
mostly a data-model change, and doing it first, invisibly, keeps the layout work mechanical.

Governing intent: [intent.md](../../../intent.md) `SEC-MARKET-001` v1.1. Nothing here changes it.

## Hard prerequisite

Branch `edition-dated-postures` must be merged to `main` first, or this work must branch from it.
That branch already adds `asOf`, `horizon`, `DecisionHorizon`, `EditionRecord`, `PostureSnapshot`,
`Edition`, `EditionSurfaceChange`, and `formatShortDate`. Building this on plain `main` would
orphan or duplicate all of it. Confirm `git log main..edition-dated-postures` is empty before
starting.

## What is already there — reuse, do not recreate

| Existing | File | Use it for |
|---|---|---|
| `SecurityDomain` with `asOf`, `horizon`, `posture`, `tag`, `evidenceStrength` | `web/src/data/types.ts`, `domains.ts` | The four posture cards. Already complete after the branch merge. |
| `VendorPrint` (`group`, `name`, `period`, `value`, `metric`, `tone`, `evidenceIds`) | `types.ts`, `prints.ts` | Every vendor figure in the platform pressure view. |
| `ActivityItem` (`kind: 'ma' \| 'funding'`, `actor`, `target`, `value`, `domain`, `evidenceIds`) | `types.ts`, `activity.ts` | Acquisitions and funding. `actor` is the acquirer and `value` is the price, both already carrying evidence IDs. |
| `EditionRecord` / `Edition` | `types.ts` (on the branch) | The what-moved section. |
| `EvidenceRecord` and the evidence drawer | `evidence.ts`, `EvidenceDrawer.tsx` | Unchanged. Every new field that makes a claim references these IDs. |

The platform pressure view is a **derived view over the data above plus a thin judgment layer.**
It is not a new hand-authored dataset. This is the central design constraint of this task: if a
figure can be derived from an existing sourced record, derive it, so the sourcing discipline is
structural rather than a habit.

## Changes

### 1. Provenance layer discriminator

Every claim the page renders belongs to exactly one layer. This is what allows a weekly mechanical
refresh to move without a person re-approving the whole page.

Add to `web/src/data/types.ts`:

```ts
/**
 * Who is accountable for a claim.
 * 'tracked'  — mechanically refreshed from a public source. No judgment applied.
 * 'judged'   — a person set this, on a date, at a stated confidence.
 * 'unsourced'— surfaced by collection but not yet tied to an evidence record.
 */
export type ProvenanceLayer = 'tracked' | 'judged' | 'unsourced'

export interface TrackedClaim {
  layer: 'tracked'
  evidenceIds: [string, ...string[]]   // at least one, enforced by the type
  observedOn: string                    // ISO date the print was captured
}

export interface JudgedClaim {
  layer: 'judged'
  judgedOn: string                      // ISO date a person set it
  confidence: ConfidenceLevel
  evidenceIds: string[]                 // may be empty; judgment can rest on absence
}

export interface UnsourcedClaim {
  layer: 'unsourced'
  surfacedOn: string
  reason: string                        // why it has no evidence record yet
}

export type Provenance = TrackedClaim | JudgedClaim | UnsourcedClaim
```

`TrackedClaim.evidenceIds` is a non-empty tuple on purpose. A tracked claim without an evidence
record must not compile. That single rule is the product's only durable asset and it belongs in the
type system, not in a review checklist.

### 2. Vendor position

Add to `types.ts`:

```ts
export type VendorPosition = 'platform' | 'incumbent' | 'challenger' | 'early' | 'absorbed'
```

Add an optional `position?: VendorPosition` to `VendorPrint`. Populate it in `prints.ts` for the
vendors already present. Do not invent vendors to fill the categories.

### 3. Platform pressure, derived

New file `web/src/data/platformPressure.ts`. It exports a derived structure, built at module load
from `prints.ts`, `activity.ts`, and `domains.ts`. It authors no figures of its own.

```ts
export type PressureGroup = 'holding' | 'buying-in' | 'outrun' | 'challengers'

export interface PressureRow {
  id: string
  vendors: string[]              // one or two names, from VendorPrint.name or ActivityItem
  position: VendorPosition
  print: string                  // rendered from the source record, never hand-typed
  read: string                   // the judgment
  provenance: { print: Provenance; read: Provenance }
}

export const platformPressure: Record<PressureGroup, PressureRow[]>
```

Derivation rules, in order:

1. `buying-in` — every `ActivityItem` with `kind: 'ma'` whose `actor` is a platform vendor. `print`
   renders as `` `${actor} · ${value} · closed ${month} ${year}` `` from the record's own fields.
   The two current members are Palo Alto and CyberArk at $25B closed February 2026 (`act-cyberark-close`,
   evidence `D14`, `D5b`) and Google and Wiz at $32B closed March 2026 (`act-wiz`, evidence `D13`,
   `D5a`). Both are sourced today; neither may be hand-typed.
2. `outrun` — an incumbent or platform whose `VendorPrint` value is below a challenger's in the same
   `group`. Zscaler against Cato and Netskope is the current case. Cisco and Okta join on their own
   prints.
3. `challengers` — `VendorPrint` rows with `position: 'challenger'` or `'early'`.
4. `holding` — everything else with a current print.

Each row's `read` is a `JudgedClaim` carrying `judgedOn` and `confidence`. The reads currently on the
design boards are the starting text; they are judgment and may be edited, but the figures beside them
may not.

### 4. Tracked hypotheses

New file `web/src/data/hypotheses.ts`.

```ts
export type HypothesisState = 'NO-CALL' | 'TRACKING' | 'SUPPORTED' | 'FALSIFIED'

export interface Hypothesis {
  id: string
  claim: string
  state: HypothesisState
  note: string
  firstTest: string | null       // what would first move it
  evidenceIds: string[]
  provenance: JudgedClaim
}
```

Seed with four. The first two are the existing episode boundaries and carry `NO-CALL`, matching
`marketCall.noCallBoundaries` in `market.ts`. The second two are owner hypotheses recorded on
2026-08-17 and carry `TRACKING`:

- Infrastructure spend leads security spend by a stable 0 to 8 quarters. `NO-CALL`.
- AI adoption compresses that lag. `NO-CALL`.
- Platforms absorb adjacent security categories rather than compete with them. `TRACKING`.
  First tests: Wiz in cloud, CyberArk in identity.
- Incumbents that cannot pivot lose ground to challengers inside their own motion. `TRACKING`.
  First test: Cato and Netskope against Zscaler organic.

A `TRACKING` hypothesis is not a claim about the market. Nothing on the page may present one as
evidence for a posture.

## Acceptance criteria

1. `npm run build` and `npm run lint` pass in the OrbStack dev VM.
2. `npx tsc --noEmit` passes. A `TrackedClaim` written with an empty `evidenceIds` array fails to
   compile; include one commented-out example proving it.
3. Every `evidenceIds` value used anywhere in the new files resolves to a real record in
   `evidence.ts`. Add a unit test that asserts this over all new data.
4. `platformPressure.ts` contains no numeric literal and no vendor name that is not read from
   `prints.ts` or `activity.ts`. A grep for `%` and `$` in that file returns nothing.
5. **The rendered page is byte-identical to production.** Run `node scripts/shot.mjs` against the
   preview and against `https://securitymarketpulse.com/` at 1440 and 390 and confirm no visible
   difference. This task ships invisibly.

## Out of scope

The layout. The weekly collection loop. Any change to `intent.md`, to Episode 002 tags, to the
evidence library, or to the published market call. Auto-publishing anything.

## Deploy

Branch only. `main` is the live site. No merge without a Vercel preview, the screenshot pair above,
and the owner's explicit yes. See `AGENTS.md` § Production deploy.
