import json, statistics

OUT = "/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/after/measure"

def load(prefix, n):
    return [json.load(open(f"{OUT}/{prefix}-{i}.json")) for i in range(1, n+1)]

def extract(d):
    audits = d['audits']
    cats = d['categories']
    def numeric(key):
        return audits[key]['numericValue'] if key in audits and audits[key].get('numericValue') is not None else None
    total_bytes = audits['total-byte-weight']['numericValue']
    # resource breakdown
    items = audits['network-requests']['details']['items']
    num_requests = len(items)
    html_bytes = 0
    js_bytes = 0
    css_bytes = 0
    main_doc_bytes = None
    from urllib.parse import urlparse as _up
    final_url = d.get('finalDisplayedUrl') or d.get('finalUrl') or (items[0].get('url', '') if items else '')
    final_origin = _up(final_url).netloc
    for it in items:
        rtype = it.get('resourceType')
        size = it.get('transferSize', 0) or 0
        if rtype == 'Document':
            html_bytes += size
            # the main document is the one served from the page's own origin; a preview
            # deployment also loads a vercel.live feedback-toolbar document, which is a
            # Vercel preview-only artifact, not part of the site and not present in production.
            if _up(it.get('url', '')).netloc == final_origin:
                main_doc_bytes = size
        elif rtype == 'Script':
            js_bytes += size
        elif rtype == 'Stylesheet':
            css_bytes += size
    lcp_element = None
    try:
        for item in audits['lcp-breakdown-insight']['details']['items']:
            if item.get('type') == 'node':
                lcp_element = f"{item.get('selector')} — \"{item.get('nodeLabel')}\""
                break
    except Exception:
        pass
    # third-party detection: main doc origin vs. every request origin
    from urllib.parse import urlparse
    main_url = d.get('finalDisplayedUrl') or d.get('finalUrl') or items[0].get('url', '')
    main_origin = urlparse(main_url).netloc
    third_party = {}
    for it in items:
        origin = urlparse(it.get('url', '')).netloc
        if origin and origin != main_origin:
            third_party.setdefault(origin, []).append(it)
    third_party_summary = []
    for origin, reqs in third_party.items():
        render_blocking = any(r.get('renderBlockingStatus') == 'blocking' for r in reqs)
        third_party_summary.append({
            'origin': origin,
            'requestCount': len(reqs),
            'renderBlocking': render_blocking,
            'urls': [r.get('url') for r in reqs],
        })
    return {
        'performance': cats['performance']['score'],
        'accessibility': cats['accessibility']['score'],
        'best-practices': cats['best-practices']['score'],
        'seo': cats['seo']['score'],
        'lcp': numeric('largest-contentful-paint'),
        'cls': numeric('cumulative-layout-shift'),
        'tbt': numeric('total-blocking-time'),
        'fcp': numeric('first-contentful-paint'),
        'speed-index': numeric('speed-index'),
        'total-bytes': total_bytes,
        'num-requests': num_requests,
        'html-bytes': html_bytes,
        'main-doc-bytes': main_doc_bytes,
        'js-bytes': js_bytes,
        'css-bytes': css_bytes,
        'lcp-element': lcp_element,
        'third-party': third_party_summary,
    }

def median_report(prefix, n=3):
    runs = load(prefix, n)
    extracted = [extract(d) for d in runs]
    keys = extracted[0].keys()
    result = {}
    for k in keys:
        vals = [e[k] for e in extracted]
        if k in ('lcp-element', 'third-party'):
            result[k] = vals[0]  # just report one (should be stable)
            continue
        nums = [v for v in vals if v is not None]
        result[k] = statistics.median(nums) if nums else None
    result['_raw_runs'] = extracted
    return result

mobile = median_report('lh-mobile', 3)
desktop = median_report('lh-desktop', 3)

print("=== MOBILE (median of 3) ===")
for k, v in mobile.items():
    if k == '_raw_runs': continue
    print(f"{k}: {v}")

print()
print("=== DESKTOP (median of 3) ===")
for k, v in desktop.items():
    if k == '_raw_runs': continue
    print(f"{k}: {v}")

with open(f"{OUT}/lighthouse-medians.json", "w") as f:
    json.dump({'mobile': mobile, 'desktop': desktop}, f, indent=2)
