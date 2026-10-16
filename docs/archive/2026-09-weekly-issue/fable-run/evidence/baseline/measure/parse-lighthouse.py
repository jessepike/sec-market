import json, statistics

OUT = "/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/baseline/measure"

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
    for it in items:
        rtype = it.get('resourceType')
        size = it.get('transferSize', 0) or 0
        if rtype == 'Document':
            html_bytes += size
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
        'js-bytes': js_bytes,
        'css-bytes': css_bytes,
        'lcp-element': lcp_element,
    }

def median_report(prefix, n=3):
    runs = load(prefix, n)
    extracted = [extract(d) for d in runs]
    keys = extracted[0].keys()
    result = {}
    for k in keys:
        vals = [e[k] for e in extracted]
        if k == 'lcp-element':
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
