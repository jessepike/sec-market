#!/usr/bin/env python3
"""Check primary URLs with actual byte hashes; success is retrieval, not proof of a newer disclosure."""
import json
import hashlib
import time
import sys
import os
import urllib.request
import urllib.error
from urllib.parse import urlparse
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

inventory = json.loads(Path(sys.argv[1]).read_text())
urls = sorted({s['canonicalUrl'] for s in inventory['sources'].values() if s and s.get('canonicalUrl')})
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
if len(sys.argv) > 3:
    receipts = json.loads(Path(sys.argv[3]).read_text())
    urls = sorted(set(urls) | {s['url'] for r in receipts for s in r['sourceChecks']} | {url for r in receipts for f in r['fields'] for url in f.get('discoverySourceUrls', [])})
cache = {}
if os.environ.get('SMP_REUSE_SOURCE_CACHE') == '1' and (out / 'source-checks.json').exists():
    cache = {s['url']: s for s in json.loads((out / 'source-checks.json').read_text())}

def check(url):
    prior = cache.get(url)
    if prior and prior['status'] == 'ok' and (datetime.now(timezone.utc) - datetime.fromisoformat(prior['checkedAt'])).total_seconds() < 3600:
        body_path = out / (prior['sha256'] + '.body')
        if body_path.exists() and hashlib.sha256(body_path.read_bytes()).hexdigest() == prior['sha256']: return prior
    item = {'url': url, 'checkedAt': datetime.now(timezone.utc).isoformat(), 'status': 'failed'}
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'SecurityMarketPulse research jesse@keatingpike.com'})
            with urllib.request.urlopen(request, timeout=25) as response:
                body = response.read(15_000_000)
                item.update(httpStatus=response.status, finalUrl=response.url)
                if not body or any(marker in body[:30000].lower() for marker in [b'<title>just a moment', b'<title>access denied', b'vercel security checkpoint', b'captcha challenge']):
                    raise ValueError('No readable source body or bot challenge')
                digest = hashlib.sha256(body).hexdigest()
                (out / (digest + '.body')).write_bytes(body)
                item.update(status='ok', sha256=digest, byteSize=len(body))
                break
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            item['reason'] = str(error)
            if isinstance(error, urllib.error.HTTPError): item['httpStatus'] = error.code
            if attempt < 2: time.sleep(1)
    return item

# Serial SEC requests stay comfortably under fair-access rate limits; other domains use four workers.
results = []
for url in [u for u in urls if urlparse(u).hostname in ['sec.gov', 'www.sec.gov', 'data.sec.gov']]:
    results.append(check(url)); time.sleep(.3)
with ThreadPoolExecutor(max_workers=4) as pool:
    results += list(pool.map(check, [u for u in urls if urlparse(u).hostname not in ['sec.gov', 'www.sec.gov', 'data.sec.gov']]))
results.sort(key=lambda r: r['url'])
(out / 'source-checks.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps({'total': len(results), 'ok': sum(r['status']=='ok' for r in results), 'failed': sum(r['status']=='failed' for r in results)}))
