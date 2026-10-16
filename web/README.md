# Security Market Pulse: web

The site at https://securitymarketpulse.com. Vite, React 19 and TypeScript, prerendered to static
HTML at build time. No server, API, database or secrets. How the whole system fits together is in
[docs/reference/architecture.md](../docs/reference/architecture.md); day-to-day commands are in
[docs/reference/operations.md](../docs/reference/operations.md).

## Commands

Node 22. Run from this folder.

| Command | What it does |
|---|---|
| `npm ci` | Install exact dependencies |
| `npm run dev` | Local development server |
| `npm run build` | Gated production build into `dist/` (what Vercel runs) |
| `npm test` | Lint, data tests, build, browser tests |
| `npm run test:data` | Data and logic tests only |
| `npm run test:e2e` | Playwright tests against `dist/` |
| `npm run refresh:edgar`, `refresh:filing-events` | Pull SEC data for the tracked filers |
| `npm run certify:sec`, `certify:gate` | Re-derive and gate the 80 certified claims |
| `npm run check:links` | Check internal links in the built site |
| `node scripts/shot.mjs <url> <prefix>` | Full-page screenshots at 1440 and 390 |

## Build pipeline

`npm run build` runs [scripts/app-release.mjs](scripts/app-release.mjs):

1. `certify-gate.ts --at-certification` must report every certified claim verified with no drift,
   or the build stops.
2. `build:certified` runs the content gates (`verify:edition`, `verify:panel`, `verify:integrity`,
   `verify:issue`, `verify:prints`, `verify:tracker`), type-checks, builds the client and server
   bundles, prerenders each route, writes SEO files and the feed, and checks the output
   (`verify:dist`).
3. The certification receipt and `app-release.json` are copied into `dist/`.

## Where things live

| Path | Contents |
|---|---|
| `src/App.tsx`, `src/entry-server.tsx`, `src/main.tsx` | Page shell, prerender entry and client entry |
| `src/components/` | Page sections. `MarketDesk.tsx` is the tracker; `HowThisWorks.tsx` is the Method section |
| `src/data/tracker/` | Suppliers, domains, events, the certified contract (`certifiedContract.json`) and what the page may call certified (`certification.ts`) |
| `src/data/generated/` | Machine-written data. The six files refreshed by the bot are listed in the architecture doc |
| `src/data/issues/` | The one signed weekly issue (`2026-w36`), locked by hash in `issues.lock.json` |
| `src/data/*.ts` | Evidence records, corrections, thesis and panel data, and their helpers |
| `scripts/` | Refresh, certification, build, prerender and verification scripts |
| `scripts/sec-verify/` | The independent SEC verifier and the 8-K Item 2.03 excerpt extractor |
| `tests/` | Data tests (`*.test.ts`, `*.test.mjs`) and browser tests (`e2e/`) |
| `public/` | Static files, including `.well-known/security.txt` |
| `vercel.json` | Install command and security headers |

## Content rules

- Components read from data modules; claims are never written directly in JSX.
- The signed issue `2026-w36` and the thesis are dated records. Change them only through a
  published correction (`src/data/corrections.ts`), never by editing the record.
- Nothing on the page may call a figure certified unless `certification.ts` says it is.
