# Security Market Pulse — Web

Responsive single-page product for frozen Episode 002 market evidence (`SEC-MARKET-SIG-002`).

## Local development

From the repository root (via OrbStack dev VM):

```bash
orb run -m dev npm install --prefix web
orb run -m dev npm run dev --prefix web
```

Open the URL printed by Vite (typically `http://localhost:5173`).

## Production build

```bash
orb run -m dev npm run build --prefix web
```

Static output is written to `web/dist/`. Preview locally:

```bash
orb run -m dev npm run preview --prefix web
```

## Lint

```bash
orb run -m dev npm run lint --prefix web
```

## Panel data integrity

Quarterly chart indices are **derived in code** from frozen raw panel values in `src/data/panelRaw.ts` (`derivePanel.ts`, `panelIntegrity.ts`). The build runs `verify:panel` before compile; it fails if derived values drift from the frozen snapshot.

After intentional panel edits:

```bash
orb run -m dev npm run verify:panel --prefix web
# inspect output, then update EXPECTED_DERIVED_PANEL_JSON in src/data/panelIntegrity.ts
```

## Updating evidence and content

1. **Evidence records** — Edit `src/data/evidence.ts` using only claims from accepted docs in `docs/active/market-signal-episode-002-*.md`. Each record needs: title, organization, dates, canonical URL, excerpt, interpretation, limitations, conflicting IDs, and artifact label.
2. **Sparse panel raw values** — Edit `src/data/panelRaw.ts` from `SEC-MARKET-SIG-PANEL-002`; run `verify:panel` and update the frozen JSON in `panelIntegrity.ts`.
3. **Market call, domains, signals, prompts** — Edit the typed modules in `src/data/` (`market.ts`, `domains.ts`, `signals.ts`, `prompts.ts`). Keep claims aligned with the brief and source manifest.
4. **Metadata** — `src/data/meta.ts` for freeze date and episode version.

Components read from data modules only; do not embed claims directly in JSX.

## Stack

- Vite + React 19 + TypeScript
- Recharts (market layers, buyer budgets)
- lucide-react (icons)
- Static data — no API, auth, or database
