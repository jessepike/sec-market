# Docs

| Folder | What it holds | Read it when |
|---|---|---|
| [reference/](reference/) | How the system works and how to operate it, plus the AUTO-002 decision records behind it | Before changing anything |
| [active/](active/) | Specs and plans for work in flight | Working on that item |
| [archive/](archive/) | Retired material, grouped by era, with an [index](archive/README.md) | Only when the owner asks |

## reference/

| File | What it is |
|---|---|
| [architecture.md](reference/architecture.md) | How the site works: what is certified, the data flow, the safeguards, the repo layout |
| [operations.md](reference/operations.md) | How to run, check, ship and repair it |
| [dns-and-accounts.md](reference/dns-and-accounts.md) | DNS, email authentication, security headers and accounts |
| [auto-002-proposal.md](reference/auto-002-proposal.md) | Decision record: `SEC-MARKET-AUTO-002`, why the site is automated the way it is, with the council review and owner decisions |
| [auto-002-phase0-spec.md](reference/auto-002-phase0-spec.md) | Decision record: Phase 0, the certified tier and its 100% gate, with the audit record |
| [auto-002-phase2-spec.md](reference/auto-002-phase2-spec.md) | Decision record: Phase 2, production renders the certified tracker |

The three decision records are dated and written as plans; where they differ from
`architecture.md` and `operations.md`, those two are current. AUTO-002 Phase 1 (the scheduled
workflows) has no separate spec; it is described in the proposal
and recorded in [decisions.md](../decisions.md) (D-88, D-96, D-98).

## active/

| Path | What it is |
|---|---|
| [daily-pipeline/](active/daily-pipeline/) | The daily collector and publisher: [runbook](active/daily-pipeline/github-operations.md), specs, evaluations and dated receipts. Tests and pipeline code read some receipts, so do not move or delete files here without checking `git grep` |
| [email-workstream.md](active/email-workstream.md) | SEC-060, waiting on two owner inputs |
| [company-search-2026-11-02.md](active/company-search-2026-11-02.md) | Company search as shipped November 2026 (SEC-073) |
