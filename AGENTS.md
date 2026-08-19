# Security Market Signal Pipeline

## Runtime

Shared instructions for all agent runtimes (Claude, Codex, Cursor, Gemini).

## Intent

See [intent.md](intent.md)

## Classification

- **Type:** Workflow
- **Scale:** commercial
- **Scope:** mvp
- **Complexity:** standalone

## Current Stage

Operate — Security Market Pulse is live; next job is recurring public-signal intelligence

## Context Map

| File | Load When | Purpose |
|------|-----------|---------|
| [intent.md](intent.md) | Always | North Star — immutable without permission |
| [status.md](status.md) | Always | Session state — review at start, update at end |
| [BACKLOG.md](BACKLOG.md) | Always | Canonical work queue |
| [decisions.md](decisions.md) | Always | Decision log |
| [README.md](README.md) | Always | Authority order and project truth |
| [docs/reference/](docs/reference/) | Design, episode work | Settled governance and episode packet |
| [docs/active/](docs/active/) | Current work | In-progress specs and plans |
| [web/](web/) | Web product work | Security Market Pulse MVP |
| [docs/archive/](docs/archive/) | Never auto | Historical hypotheses — explicit instruction only |
| [.claude/rules/](.claude/rules/) | Always | Hard constraints |

## Workflow Type

Probabilistic/Agentic — human-steered judgment with transparent evidence

## Trigger

Recurring — public market signals are gathered on a cadence; market calls stay human-checked

## Integrations

- CISO Advisory concepts may be referenced; this project owns market timing and signal evidence
- Public static website: Vercel project `security-market-pulse`, domain `securitymarketpulse.com`
- Recurring public-signal intake is authorized; auto-publish of market calls is not

## Production deploy (mandatory)

The only allowed path is **local → `preview` → owner approval → `main` → Vercel production**.

There are exactly two long-lived branches and each one owns a URL:

| Branch | URL | What it is |
|---|---|---|
| `preview` | https://security-market-pulse-git-preview-pikeholdings.vercel.app | The trunk. All work lands here. The URL is stable — bookmark it and refresh. |
| `main` | https://securitymarketpulse.com | Production. Moves **only** by a deliberate merge from `preview`. |

`main` is production. Pushing to `main` publishes to the public site with no human between the commit and the world, so `main` moves only when the owner says to promote. Every other branch is short-lived and merges into `preview`, not into `main`.

1. Develop against the OrbStack dev server (`orb run -m dev npm run dev --prefix web`).
2. Commit a clean tree on `preview`, or on a short-lived branch that merges into `preview`. **Never commit directly on `main`.**
3. `git push origin preview`. Vercel rebuilds the same stable preview URL above.
4. Run the visual review below and send the owner that URL plus the before/after screenshots.
5. **Promotion, and only after the owner says yes:** `git checkout main && git merge --ff-only preview && git push origin main`.
6. Vercel builds that `main` commit (project `pikeholdings/security-market-pulse`, root `web`) and serves the live domain. Confirm Ready, then curl the live host.

Keeping `main` a fast-forward of `preview` is deliberate. It means production is always an exact earlier state of the trunk, never a parallel history, so "what is live" is answerable by one `git log`.

Do **not**:

- commit or push anything directly to `main` — it moves only by promotion from `preview`
- push to `main` any change that touches `web/` without owner approval of a preview
- `vercel --prod` / CLI-upload a dirty or uncommitted working tree
- treat `origin/main` as live until that commit has actually deployed
- push an older `main` that would regress the scorecard already on production
- commit with `jesse@pikeholdings.co` — Vercel blocks the GitHub deploy (`COMMIT_AUTHOR_REQUIRED`) because GitHub cannot map that address to a user

This repo’s commit email must be the GitHub-verified address `jesse@keatingpike.com` (`git config user.email` in this repo). After a push, confirm the Vercel deploy is Ready, then curl the live host before telling the owner it is shipped.

First production ship was a CLI upload. That split local, GitHub, and Vercel. Do not recreate it.

## Visual review before publish (mandatory)

A build that passes is not a page that looks right. No change touching `web/` reaches `main` until an agent has **rendered the page and looked at it**.

Before asking for approval, capture full-page screenshots of the current production site and of the preview build at **1440px and 390px** widths, compare them, and state plainly what moved. Send the owner the images with the preview URL. Run from `web/`:

```
node scripts/shot.mjs https://securitymarketpulse.com/ /tmp/prod
node scripts/shot.mjs <preview-url> /tmp/preview
```

Hard rules:

- **Never delete a component, a CSS rule, a data export, or a page section on the strength of static analysis alone.** "No importers found" is a hypothesis. Render the page before and after and prove the pixels did not move. Two independent agents can both be wrong about the same file.
- A claim that the site improved must be backed by a render, not by a build log, a lighthouse score, or a passing test.
- Separate **invisible** work (SEO, prerendering, bundle size, citation accuracy, accessibility) from **visible** work (layout, typography, colour, hierarchy, charts) when reporting. Say which of the two you did. Never let a long list of invisible wins imply the page looks different.
- If a session's goal is "make it better" and no visible change was made, say so in the first sentence of the report.

## Fresh-agent minimum context

1. [README.md](README.md)
2. [intent.md](intent.md)
3. [outcome-architecture.md](docs/reference/outcome-architecture.md)
4. Current reconciliation and active episode under [docs/active/](docs/active/) (`SEC-MARKET-RECON-001`, `SEC-MARKET-SIG-002`)
5. Frozen thematic packet under [docs/reference/](docs/reference/) (`SEC-MARKET-SIG-001` v0.2) only when needed
6. Accepted shadow design and replay corpus under [docs/active/](docs/active/) (`SEC-MARKET-SHADOW-001` v0.2, `SEC-MARKET-SHADOW-CORPUS-001` v0.1)
7. Accepted Gate S1 implementation specification under [docs/active/](docs/active/) (`SEC-MARKET-SHADOW-S1-SPEC-001` v0.2)
8. Accepted web MVP contract and implementation under [docs/active/](docs/active/) and [web/](web/) (`SEC-MARKET-WEB-001`)
9. Current signals job under [docs/active/signals-job.md](docs/active/signals-job.md)
10. Production deploys only via local → GitHub → Vercel (this file, D-31)
