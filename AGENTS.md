# Security Market Pulse

Shared instructions for every agent runtime (Claude, Codex, Cursor, Gemini, Krypton). This file is
canonical; `CLAUDE.md` and `.cursor/rules/project.mdc` point here.

## What this is

https://securitymarketpulse.com, a public tracker of the business of the security market: revenue,
funding, acquisitions, restructuring, debt and leadership changes for 74 security suppliers across
12 market domains. SEC figures for 16 public filers are checked against their filings every 4 hours;
a change publishes automatically when every check passes. No machine writes opinions. The owner is
Jesse Pike.

- **Stage:** Operate. The site is live and updates itself.
- **Type:** automated workflow with a static website.
- **Scope:** public information only, at commercial quality.

## Start here

| Read | For |
|---|---|
| [README.md](README.md) | What the project is and where everything lives |
| [intent.md](intent.md) | Purpose, readers and boundaries. Changes need the owner's approval |
| [status.md](status.md) | Current state, open items and what is next. Read it first in every session |
| [BACKLOG.md](BACKLOG.md) | Open work |
| [decisions.md](decisions.md) | Decision ledger; the decisions in force are indexed at the top |
| [.claude/rules/constraints.md](.claude/rules/constraints.md) | Hard rules |
| [docs/reference/architecture.md](docs/reference/architecture.md) | How the system works |
| [docs/reference/operations.md](docs/reference/operations.md) | Commands, shipping, repair |

Load on demand: [docs/reference/](docs/reference/) for the current design, [docs/active/](docs/active/)
for work in flight. Never load automatically: [docs/archive/](docs/archive/), `.ctx/` (local, uncommitted agent scratch
context).

## Continuity

Sessions start cold. Everything the next agent needs is in the repo, not in a chat:

- At the start: read `status.md`, then `git status` and `git log --oneline -10` on `preview`.
- At the end: update `status.md` (current state only, one page) and log any decision in
  `decisions.md` with the owner's words.
- Krypton, the owner's agent system, picks up from `status.md` the same way.

## Production deploy (mandatory)

The only allowed path is **local → `preview` → owner approval → `main` → Vercel production**.

There are exactly two long-lived branches and each one owns a URL:

| Branch | URL | What it is |
|---|---|---|
| `preview` | https://security-market-pulse-git-preview-pikeholdings.vercel.app | The trunk. All work lands here. The URL is stable |
| `main` | https://securitymarketpulse.com | Production. Moves only by a fast-forward from `preview` |

1. Work on a short-lived branch from `preview`, or on `preview` itself. Never commit on `main`.
2. Run `npm test` from `web/`.
3. Push `preview`. Vercel rebuilds the stable preview URL.
4. Run the visual review below and send the owner the preview URL and the screenshots.
5. **Only after the owner says yes:** `git checkout main && git merge --ff-only preview && PROMOTE=1 git push origin main`.
6. Confirm the Vercel production deployment is Ready, then `curl` the live host before saying it shipped.

A `pre-push` hook refuses a push to `main` without `PROMOTE=1`. Install it once per clone with
`./.githooks/install`. Keeping `main` a fast-forward of `preview` means production is always an
exact earlier state of the trunk, so "what is live" is answered by one `git log`.

**The one automatic exception (D-88).** `certified-refresh.yml` pushes changed certified SEC data,
and nothing else, to `preview`. `promote-certified.yml` fast-forwards `main` once a day only when
every file that differs is one of the six allowlisted data files, the newest `preview` commit is at
least 24 hours old, and a fresh certification reproduces the values at 100%. Any other commit on
`preview` blocks it until the owner promotes. So after human work lands on `preview`, ask the owner
to promote promptly, or certified data stops reaching production.

Do **not**:

- commit or push directly to `main`
- push to `main` any change that touches `web/` without the owner's approval of a preview
- deploy with `vercel --prod` or upload a working tree from the CLI
- treat `origin/main` as live until that commit has deployed
- force-push `preview` or `main`
- commit as `jesse@pikeholdings.co`. Vercel refuses the deploy (`COMMIT_AUTHOR_REQUIRED`). The repo's
  commit email is `jesse@keatingpike.com`

## Visual review before publish (mandatory)

A build that passes is not a page that looks right. No change touching `web/` reaches `main` until
an agent has **rendered the page and looked at it**.

Before asking for approval, capture full-page screenshots of production and of the preview at
**1440px and 390px**, compare them, and state plainly what moved. From `web/`:

```
node scripts/shot.mjs https://securitymarketpulse.com/ /tmp/prod
node scripts/shot.mjs <preview-url> /tmp/preview
```

- **Never delete a component, CSS rule, data export or page section on the strength of static
  analysis alone.** Render before and after and prove the pixels did not move.
- A claim that the site improved must be backed by a render, not a build log, a Lighthouse score or
  a passing test.
- Report **invisible** work (SEO, prerendering, bundle size, citations, accessibility) separately
  from **visible** work (layout, type, colour, hierarchy, charts). If nothing visible changed, say
  so first.

## Content rules

- Facts only. No machine-written stance, ranking, forecast or interpretation (D-76).
- The page calls a figure certified only when `web/src/data/tracker/certification.ts` says so, and
  says "re-derived from SEC filings", never "independently verified" (D-100).
- Issue `2026-w36` and the thesis change only through a new dated correction, never by editing the
  record. Corrections themselves are append-only.
- Plain language in anything a reader sees: short sentences, no em dashes, no marketing phrasing.
