# Handoff — finish securitymarketpulse.com DNS

**Status:** Done 2026-08-16. Exit condition met.  
**Date:** 2026-08-16  
**From:** Cursor Grok session that created the Vercel project  
**To:** a desktop Cursor session with Cloudflare + Vercel plugin MCPs authenticated  
**Exit condition:** `https://securitymarketpulse.com` returns HTTP 200 with a Vercel certificate and the Security Market Pulse title. **Met.**

## Do this

1. Use the **Cloudflare API MCP** (`search` / `execute`), not `$CLOUDFLARE_API_TOKEN`. That shell token can list this zone and gets 403 on DNS.
2. Create two **unproxied** (grey cloud, `proxied: false`) CNAMEs on zone `securitymarketpulse.com`.
3. Confirm Vercel no longer reports the domain as misconfigured.
4. Verify HTTPS on apex and that `www` 308s to apex.
5. Update `status.md`, `decisions.md` (append under D-23 or add D-24), and this file’s status. Do not commit unless the owner asks.

## Already done — do not redo

- Domain registered at Cloudflare Registrar; nameservers `georgia` / `jerry.ns.cloudflare.com`.
- Vercel project `pikeholdings/security-market-pulse`
  - Project ID: `prj_g8sZPXo81XT2Xopa1oLrsbYjTehV`
  - Team: `team_gRV7FrVjjr1PPI1IvgoCEJrH` (`pikeholdings`)
  - Root directory: `web`
  - Git: `jessepike/sec-market`
  - Node 24.x, Vite, `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`
- Production live: https://security-market-pulse.vercel.app
- Custom hosts claimed on the project:
  - `securitymarketpulse.com` (apex)
  - `www.securitymarketpulse.com` → 308 to `securitymarketpulse.com`
- First production deploy was a **CLI upload of the local working tree** (scorecard restyle). That split is closed: later sessions commit locally, push `main`, and let Vercel build the GitHub commit (D-31). Do not CLI-upload a dirty tree again.
- Decision **D-25** records the original deploy authorization; **D-31** is the standing path.
- `web/vercel.json` exists. `.vercel/` is gitignored.

## DNS to write

Zone ID: `34251ea7b517605f017007f13625555a`  
Account ID (Cloudflare MCP): `870b8b1fdf9751c0bad885031db2ffd0`

| Type | Name | Content | Proxy |
|---|---|---|---|
| CNAME | `@` | `8406d7f2fc89acd7.vercel-dns-016.com` | DNS only (`proxied: false`) |
| CNAME | `www` | `8406d7f2fc89acd7.vercel-dns-016.com` | DNS only (`proxied: false`) |

Orange-cloud / proxied will block Vercel TLS. Apex CNAME is OK — Cloudflare flattens.

Fallback target if the project-specific CNAME fails: `cname.vercel-dns.com`.

## Verify

```bash
dig +short securitymarketpulse.com CNAME
dig +short www.securitymarketpulse.com CNAME
# or against Cloudflare NS:
dig +short @georgia.ns.cloudflare.com securitymarketpulse.com
curl -sI https://securitymarketpulse.com | head -20
curl -sI https://www.securitymarketpulse.com | head -15
curl -s https://securitymarketpulse.com | grep -o '<title>.*</title>'
```

Expect: Vercel `server` header, HTTP 200 on apex, 308 from www, title `Security Market Pulse | Episode 002`.

Vercel domain config was `misconfigured: true` before DNS. Recheck via Vercel MCP `get_project` or API `GET /v6/domains/securitymarketpulse.com/config?teamId=team_gRV7FrVjjr1PPI1IvgoCEJrH`.

## Out of scope

- Gate S1 implementation
- Collectors, database, scheduler, autonomous pipeline
- Changing nameservers off Cloudflare

## Why the previous session stopped

The creating agent used the shell API token (403 on DNS) and could not invoke Cursor plugin MCPs (`plugin-cloudflare-cloudflare-api`, `plugin-vercel-vercel`) even after desktop OAuth. Those plugins are authenticated in Cursor desktop; use them from a desktop chat, not a plugin-blind agent runtime.
