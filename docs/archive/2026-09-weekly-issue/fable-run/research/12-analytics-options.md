# Analytics Tool Comparison

**Recommendation: Plausible at 10,000 page views** ($9/month, read on https://plausible.io pricing page, 2026-09-20). Fallback: Fathom ($15/month, read on https://usefathom.com/pricing, 2026-09-20) if additional features are needed. Both are cookieless, block free of ad-blocker concerns, and cost under ten dollars for the target traffic. Plausible wins on price; Fathom wins on feature depth.

| Tool | <10k views | 100k views | Cookieless | Returning Visitors | Referrers | Downloads/Outbound | Custom Events | Ad Blocker Risk | Data Location |
|------|-----------|-----------|-----------|------------------|-----------|------------------|---------------|-----------------|---------------|
| Vercel Web Analytics | Free (50k/mo) | $30+ | No mention | Not tracked | Yes (Plus) | Not mentioned | Yes (Pro+) | Medium | Vercel servers |
| Vercel Speed Insights | Free | Free | N/A | N/A | N/A | N/A | N/A | Low | Vercel servers |
| Plausible | $9/mo | $14/mo | Yes | Cannot | Yes | Yes | Yes | Low | EU/US |
| Fathom | $15/mo | $15/mo | Yes | Yes (unclear method) | Yes | Yes | Yes | Low | US |
| Simple Analytics | $20+ | $20+ | Yes | Cannot | Yes | Not mentioned | Not mentioned | Low | EU/US |
| GoatCounter | Free | Free | Yes | Yes (cookieless hashing) | Yes | Not mentioned | Yes | Low | Self-hosted |
| Cloudflare Web Analytics | Free | Free | Not mentioned | Not mentioned | Not mentioned | Not mentioned | Not mentioned | Low | Cloudflare |
| PostHog (free tier) | Free (1M events) | Free (1M events) | No | Yes | Yes | Yes | Yes | High | US |
| Pirsch | $6/mo | Higher tier | Yes (HTTP hashing) | Yes | Yes | Yes | Yes | Low | Germany |
| Umami cloud | Could not open | Could not open | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown |

**Plausible detail** (read on https://plausible.io/docs, 2026-09-20): lightweight script, tracks downloads and outbound links, custom event support, does NOT track returning visitors versus new ones due to cookieless architecture. Works from first-party domain. Script size lightweight and rarely blocked.

**Fathom detail** (read on https://usefathom.com/pricing, 2026-09-20): pricing flat at $15 regardless of volume below 100k, supports conversions and custom events, claims returning visitor tracking but method unclear. Privacy-friendly, GDPR compliant, email reports included.

**Vercel logs without analytics script**: Vercel Hobby plan logs available for 1 hour; Pro plan logs for 1 day. Build logs stored indefinitely. HTTP request logs can be drained to third-party observability (Datadog, etc.) for counting /feed.xml fetches and JSON file downloads by user agent, but requires setup and ongoing cost. Does not show returning visitors. Hobby plan includes 50k Web Analytics events free, which covers this site's traffic.

**Could not open**: Umami cloud pricing (site returned 404), Fathom blog (DNS resolution failed), Simple Analytics docs (redirect loop).

