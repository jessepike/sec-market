# Project Constraints

These are non-negotiable rules. Agents must not creatively reinterpret or work around them.

## Security

- Never commit secrets, credentials, or API keys
- Never create tokens or copy credentials into CI without the owner's approval at the time (D-83)
- The site uses public, publishable information only

## Governance

- Never modify `.claude/rules/` without explicit human approval
- Never modify [intent.md](../../intent.md) without explicit human approval
- Do not read from [docs/archive/](../../docs/archive/) without explicit instruction
- Archived documents are not implementation authority

## Authorization

- Authorized (D-76, 2026-09-25): the public website, scheduled collectors, and an autonomous pipeline that publishes sourced, machine-validated facts with automated checks as the only gate and no human approval step
- Authorized (D-88, 2026-10-15; widened by D-103; route replaced by D-110, 2026-10-23): facts reach production automatically through the daily collector and the independent release gate. Code reaches production only by an approved fast-forward of `main` from `preview`. Major changes, as defined in AGENTS.md, need the owner's approval of a preview
- Authorized (D-92, 2026-10-15; rule updated with owner approval 2026-10-16): email capture and a digest of certified changes, built as one complete workstream
- Not authorized: a machine publishing judgments: stances, rankings, forecasts, or interpretation of what a fact means. Judgments are published only when the owner writes them
- Not authorized: a database. One exception (D-147, 2026-11-09): a single SQLite index file for evidence bookkeeping, kept in the private evidence repo. No hosted database and no new service
- Confirm before destructive operations (delete, drop, overwrite)

## Session Discipline

- Update [status.md](../../status.md) before ending a session
- Log consequential decisions in [decisions.md](../../decisions.md)
- Use conventional commit format: `type(scope): description`
