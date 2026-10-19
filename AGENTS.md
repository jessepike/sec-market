# Security Market Pulse

Shared instructions for every agent runtime (Claude, Codex, Cursor, Gemini, Krypton). This file is
canonical; `CLAUDE.md` and `.cursor/rules/project.mdc` point here.

## What this is

https://securitymarketpulse.com, a public tracker of the business of the security market: revenue,
funding, acquisitions, restructuring, debt and leadership changes for 74 security suppliers across
12 market domains. SEC figures for 16 public filers are checked against their filings every 4 hours.
Data and routine changes publish automatically when every check passes; the owner reviews only
major changes. No machine writes opinions. The owner is
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
| [lessons.md](lessons.md) | Mistakes not to repeat on this project |

Load on demand: [docs/reference/](docs/reference/) for the current design, [docs/active/](docs/active/)
for work in flight. Never load automatically: [docs/archive/](docs/archive/), `.ctx/` (local, uncommitted agent scratch
context).

## Continuity

Sessions start cold. Everything the next agent needs is in the repo, not in a chat:

- At the start: read `status.md`, then `git fetch`, `git status` and `git log --oneline -10 origin/preview`.
  Check the push guard is installed (`test -x .git/hooks/pre-push`, else `./.githooks/install`).
- At the end: update `status.md` (current state only, one page) and log any decision in
  `decisions.md` with the owner's words.
- Krypton, the owner's agent system, picks up from `status.md` the same way.

## Production deploy (mandatory)

The path is **local → `preview` → automatic checks → `main` → Vercel production** (D-103). The owner
reviews only major changes.

There are exactly two working branches and each one owns a URL. Any other branch is short-lived and
is deleted once merged into `preview`. One more branch, `archive/history-before-2026-10-14`, only
holds the commit history from before the trunk was restarted on 2026-10-14; never build on it or
delete it:

| Branch | URL | What it is |
|---|---|---|
| `preview` | https://security-market-pulse-git-preview-pikeholdings.vercel.app | The trunk. All work lands here. The URL is stable |
| `main` | https://securitymarketpulse.com | Production. Moves only by a fast-forward from `preview` |

1. Work on a short-lived branch from `preview`, or on `preview` itself. Never commit on `main`.
2. Run `npm test` from `web/`. Render production and the preview and compare (below).
3. Decide whether the change is major (below). If it is, end the commit message with the trailer
   `Owner-Review: required`.
4. Push `preview`. Vercel rebuilds the preview URL.
5. `.github/workflows/promote.yml` runs every 4 hours. Taking commits oldest first, it promotes up to
   the newest one that has soaked on its own clock (6 hours for the refresh bot's `data(auto)`
   commits, 24 hours for anything else) and is not major. It then requires the full test suite to
   pass on that exact commit, a fresh certification to reproduce the committed SEC data, and the
   page-structure guard to match production. A major change is held, with everything after it, and
   listed in the GitHub issue "Owner review needed"; a failure opens "Automatic promotion failed".
6. When the owner approves a held change: `git checkout main && git merge --ff-only preview &&
   PROMOTE=1 git push origin main`, then confirm the Vercel deployment and `curl` the live host.

**Major changes** need the owner and must carry the trailer:

- anything a reader would notice beyond data: layout, sections, navigation, headings, page wording
- adding or removing suppliers, domains, data sources, claim types or certified companies
- anything that sends email, adds an external service or uses a secret
- `intent.md`, `.claude/rules/`, this deploy policy, security headers, the promotion rules

The workflow also holds, without a trailer:

- protected paths: `intent.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.githooks/`, all of
  `.github/`, `web/vercel.json`, `web/package.json` and its lock file, the promotion scripts, and the
  certification chain (`app-release.mjs`, `claim-gate.mjs`, `certify-*`, `sec-verify/independent.mjs`)
- merge commits, and any workflow line that uses a secret
- a change to the page structure: routes, h1 and h2 headings, section and navigation ids, navigation
  links, the stylesheet, or the text of the dated records (thesis, issue `2026-w36`, corrections)

The guard does not see wording changes elsewhere on the tracker page, h3 and lower headings, or
chart markup. For those, the trailer is the only control: when unsure, mark it major. Everything else
is routine and goes live on its own: certified data, bug fixes, tests, docs, refactors that render
the same. Soak time comes from commit dates, so never backdate a commit.

A `pre-push` hook refuses a manual push to `main` without `PROMOTE=1`. Install it once per clone with
`./.githooks/install`. Keeping `main` a fast-forward of `preview` means production is always an exact
earlier state of the trunk, so "what is live" is answered by one `git log`.

Do **not**:

- commit or push directly to `main`, except the owner-approved promotion command above
- leave the trailer off a change you are unsure about
- deploy with `vercel --prod` or upload a working tree from the CLI
- treat `origin/main` as live until that commit has deployed
- force-push `preview` or `main`
- commit as `jesse@pikeholdings.co`. Vercel refuses the deploy (`COMMIT_AUTHOR_REQUIRED`). The repo's
  commit email is `jesse@keatingpike.com`

## Visual review before every push to `preview` (mandatory)

A build that passes is not a page that looks right. Before pushing a change that touches `web/`,
capture full-page screenshots of production and of your local build or the preview at **1440px and
390px**, compare them, and say in the commit message what moved, or that nothing did. From `web/`:

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
  so first. Anything visible beyond data is a major change.

## Content rules

- Facts only. No machine-written stance, ranking, forecast or interpretation (D-76).
- The page calls a figure certified only when `web/src/data/tracker/certification.ts` says so, and
  says "re-derived from SEC filings", never "independently verified" (D-100).
- Issue `2026-w36` and the thesis change only through a new dated correction, never by editing the
  record. Corrections themselves are append-only.
- Plain language in anything a reader sees: short sentences, no em dashes, no marketing phrasing.
