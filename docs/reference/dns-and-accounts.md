# DNS and accounts

Current DNS, email-authentication and account settings for the two sites in this portfolio
(D-99). Both domains use Cloudflare DNS, not proxied. Records verified through public DNS on
2026-10-15.

## securitymarketpulse.com

The domain sends no email, so every record tells receivers to reject mail that claims to be from it.

| Type | Name | Value | State |
|---|---|---|---|
| TXT | `@` | `v=spf1 -all` | in place |
| TXT | `_dmarc` | `v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s` | in place |
| MX | `@` | priority `0`, server `.` (null MX) | in place |
| CAA | `@` | `0 issue "letsencrypt.org"` (Vercel issues certificates through Let's Encrypt) | open |
| DNSSEC | | Cloudflare, DNS, Settings, Enable DNSSEC | open |

Change the email records only if the email workstream (D-92) ever sends from this domain. The
current plan sends from jessepike.dev.

## jessepike.dev

Mail is Fastmail (MX and DKIM in place); the newsletter is Buttondown.

| Type | Name | Value | State |
|---|---|---|---|
| TXT | `@` | `v=spf1 include:spf.messagingengine.com ~all` | in place |
| TXT | `_dmarc` | `v=DMARC1; p=none` | in place; no report address yet |
| CAA | `@` | `0 issue "letsencrypt.org"` | open |
| DNSSEC | | as above | open |

To get DMARC reports, turn on Cloudflare Email, DMARC Management (owner click). Move to
`p=quarantine` only after 2 to 4 weeks of clean reports and after confirming Buttondown signs with
DKIM aligned to jessepike.dev; otherwise newsletter mail may be rejected.

## Web security headers

Both sites send a Content-Security-Policy, HSTS with `includeSubDomains`, frame denial, a
cross-origin opener policy and a restrictive Permissions-Policy, set in each repo's `vercel.json`.
Both publish `/.well-known/security.txt`, which expires **2027-10-15** and must be renewed before
then (tracked in [BACKLOG.md](../../BACKLOG.md)).

## Accounts

| Account | Sign-in | Notes |
|---|---|---|
| GitHub | Passkey and two-factor | Free plan; no branch protection (D-98) |
| Vercel | Passkey and two-factor | Confirm the plan permits commercial use; Hobby is non-commercial |
| Cloudflare | Passkey and two-factor | DNS for both domains |

Agents do not create tokens or copy credentials into CI without the owner's approval at the time
(D-83).
