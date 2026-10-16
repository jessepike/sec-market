---
for: owner (Cloudflare DNS changes); Krypton for follow-up
created: 2026-10-15
decision: D-98
---

# DNS and account hardening checklist

Both domains use Cloudflare DNS (DNS only, not proxied). These changes are made in the Cloudflare dashboard. State checked 2026-10-15 with public DNS queries.

## securitymarketpulse.com (sends no email)

Found: no MX, no SPF, no DMARC, no CAA, no DNSSEC. Anyone can send mail that claims to be from this domain.

| Type | Name | Value |
|---|---|---|
| TXT | `@` | `v=spf1 -all` |
| TXT | `_dmarc` | `v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s` |
| MX | `@` | priority `0`, mail server `.` (null MX; skip if Cloudflare rejects it, SPF and DMARC already cover spoofing) |
| CAA | `@` | `0 issue "letsencrypt.org"` (Vercel issues certificates through Let's Encrypt) |

Change these when the email workstream (D-91) starts sending from this domain.

## jessepike.dev (Fastmail mail, Buttondown newsletter)

Found: Fastmail MX and DKIM in place; SPF ends in `?all` (neutral, gives no protection); no DMARC; no CAA; no DNSSEC.

| Type | Name | Value |
|---|---|---|
| TXT | `@` | replace with `v=spf1 include:spf.messagingengine.com ~all` |
| TXT | `_dmarc` | `v=DMARC1; p=none; rua=mailto:<an address you read>` |
| CAA | `@` | `0 issue "letsencrypt.org"` |

Start DMARC at `p=none` to collect reports without blocking mail. Before moving to `p=quarantine` (after 2 to 4 weeks of clean reports), confirm Buttondown sends with DKIM aligned to jessepike.dev, or newsletter mail may be rejected. If Buttondown sends from its own domain, add its include to SPF only if its settings say so.

## Both domains

- DNSSEC: Cloudflare dashboard, DNS, Settings, Enable DNSSEC. If the registrar is not Cloudflare, copy the DS record Cloudflare shows into the registrar.
- After changes, verify with `dig TXT _dmarc.<domain>` or an online checker.

## Accounts (D-97)

- GitHub: passkey two-factor; remove any unused personal access tokens.
- Vercel and Cloudflare: passkey or hardware-key two-factor.
- Vercel plan: confirm the team's plan permits this use. The free Hobby plan is for non-commercial use.

## Recurring

- `security.txt` on both sites expires 2027-10-15. Renew before then. The monitoring work in AUTO-002 should alert 30 days ahead.
