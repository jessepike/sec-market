# Email workstream (D-92)

**Backlog:** SEC-060 · **Status:** waiting on two owner inputs (the API key and a postal address) · **Owner of the list:** jessepike.dev

The owner approved email capture and a digest as one unit: it ships complete or not at all, with no
loose ends. Nothing is built until the inputs below exist, so that no half-finished piece sits in
the repo.

## Scope

1. **Provider:** Buttondown, which already runs the jessepike.dev newsletter (list `pike`). One list,
   one tag per site (`smp` for this site).
2. **Signup:** a plain HTML form (no third-party script) on securitymarketpulse.com and
   jessepike.dev that posts to Buttondown, with double opt-in. CSP `form-action` adds the Buttondown
   form host.
3. **Digest:** a GitHub Actions job that sends only when certified data changed, lists only
   certified changes with their SEC links, and never sends when the gate failed. Facts only; no
   commentary (D-76).
4. **Compliance:** a privacy page naming Buttondown as processor; unsubscribe link in every email; a
   postal address in the footer (CAN-SPAM).
5. **Sender authentication:** SPF, DKIM and DMARC on jessepike.dev aligned for Buttondown (see
   [dns-and-accounts.md](../reference/dns-and-accounts.md)).
6. **Rules:** `.claude/rules/constraints.md` already lists the digest as authorized (owner approval,
   2026-10-16).
7. **Tests:** a test send to the owner before any subscriber receives mail.
8. **Docs:** update the secrets line in [architecture.md](../reference/architecture.md) and the
   operations runbook, since the digest job is the first workflow with a secret.

## Owner inputs needed

| Input | Why | How |
|---|---|---|
| Buttondown API key as GitHub secret `BUTTONDOWN_API_KEY` | The digest job sends through the API | Buttondown settings, API; then GitHub repo Settings, Secrets and variables, Actions |
| A postal address for the email footer | Required by CAN-SPAM | A PO box or virtual mailbox is fine; a home address is not recommended |
| Go-ahead after the first test send (not a blocker to building) | Confirms the format before subscribers see it | Reply to the test email |

## Not in scope

Paid tiers, tracking pixels, a database of subscribers in this repo, or any email sent from
securitymarketpulse.com (its DNS rejects all mail by design).
