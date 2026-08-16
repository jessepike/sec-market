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

- Production collectors, database, scheduler, website, digest, and autonomous pipeline are not authorized
- Posture judgment and authorization remain human-steered
- Confirm before destructive operations (delete, drop, overwrite)

## Session Discipline

- Update [status.md](../status.md) before ending a session
- Log consequential decisions in [decisions.md](../decisions.md)
- Use conventional commit format: `type(scope): description`
