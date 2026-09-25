# Project Constraints

These are non-negotiable rules. Agents must not creatively reinterpret or work around them.

## Security

- Never commit secrets, credentials, or API keys
- Initial core uses public, publishable information only

## Governance

- Never modify `.claude/rules/` without explicit human approval
- Never modify [intent.md](../intent.md) without explicit human approval
- Do not read from [docs/archive/](../docs/archive/) without explicit instruction
- Historical specs in `docs/archive/` are not implementation authority

## Authorization

- Authorized (D-76, 2026-09-25): the public website, scheduled collectors, and an autonomous pipeline that publishes sourced, machine-validated facts with automated checks as the only gate and no human approval step
- Not authorized: a machine publishing judgments — stances, rankings, forecasts, or interpretation of what a fact means. Judgments are published only when the owner writes them
- A database and an email digest are not yet authorized
- Confirm before destructive operations (delete, drop, overwrite)

## Session Discipline

- Update [status.md](../status.md) before ending a session
- Log consequential decisions in [decisions.md](../decisions.md)
- Use conventional commit format: `type(scope): description`
