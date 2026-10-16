# Lessons

Working lessons for agents on this project, newest first, at most about 15. Each line carries a tag:

- `[new:<date>]` recorded this session, not yet reviewed for the owner's shared knowledge base;
- `[withheld:<date>]` reviewed and kept here because it is specific to this project.

The owner keeps a shared knowledge base of lessons across projects, outside this repo. Lessons
promoted there are removed from this file; Git history keeps them.

## 2026-10-16

- [new:2026-10-16] `pkill -f <pattern>` kills the shell that runs it when the pattern also appears in that shell's own command line (exit 144). Kill by PID, or use a pattern the command line cannot contain.
- [new:2026-10-16] GitHub scheduled workflows on a quiet repository start late and skip slots, especially the first runs after a schedule is added: the first `17 */4` refresh ran at 16:38, after two skipped slots. Alarm on "no run in N hours", never on a missed slot.
- [new:2026-10-16] Moving hundreds of documents is safe only with a mapping file and a script that rewrites both relative links and repo-root path mentions from that map; then check links before committing.
- [new:2026-10-16] A reviewer that has not seen the work finds label overclaims the author cannot see: "the event type is certified" read true to its author until a fresh agent showed the verifier never checks type per event.

## 2026-10-02

- [withheld:2026-10-02] A backgrounded tool call wrapping a command that ALSO backgrounds itself with a trailing `&` produces an orphaned, unreliable process; the wrapper returns immediately while the real work's survival across turns (especially across a session interruption) is uncertain. Pass the long-running command directly to the backgrounding mechanism without an internal `&`; that is the form that gives a trustworthy completion notification.
- [withheld:2026-10-02] After any session-rate-limit or similar interruption, a "completed exit code 0" notification for a background task is not proof it ran; check ground truth (a result file's timestamp/content, `ps aux`) before trusting it. One batch of this session's 74-supplier collector run silently never executed despite reporting success; only a timestamp check caught it.
- [withheld:2026-10-02] A supplier's own news counting as "unreadable" is only honest after a real fallback chain, not after one fetch failing; RSS/Atom, sitemap, an IR subdomain, a wire-service copy (GlobeNewswire/PR Newswire/Business Wire), and an EDGAR full-text search, in that order, with the failure detail naming which routes were tried.

## 2026-09-21

- [withheld:2026-09-21] A build-time meaning gate (fiscal period vs. source, `verify-issue.ts`/`verify-prints.ts`) can't be satisfied by editing a locked, hashed issue or a corrected-in-place standing table. The escape hatch is an explicit, dated exemption list read by the check (`corrections.ts`, `printsUnverified.ts`), not an edit to the checked data.

## 2026-09-19

- [withheld:2026-09-19] Page composition accepted on a spec is not page composition anyone has seen. The weekly-issue front page passed three external review rounds, a full e2e suite and five build gates, and still nobody had looked at it at full page height until the promotion render: it opens with a chronological list of funding rounds down to a $60.0K pre-seed, with the judgment below four lanes. Render the whole page at both widths at the point the composition changes, not at the point it ships.

## 2026-08-27

- [withheld:2026-08-27] A purchase price allocation says what an acquirer thinks it bought. Two AI security deals put almost the whole price in goodwill and assigned nothing to customer relationships, while an adjacent deal in the same filing put $464M of $476M into customer relationships. That contrast is stronger evidence than any figure either company would state directly.

## 2026-08-19

- [withheld:2026-08-19] A figure in a record's `note` field is not interchangeable with one in its `value` field. Falcon Cloud at $800M is an absolute amount; every other row in that table is a growth rate. The delegate caught this and was right.
