"""Build the private source scorecard from the evidence archive.

Read-only. Reads the last daily runs from refs/archive/market-evidence and the
current contract, then writes scorecard.json (for agents) and scorecard.html
(the private page). The evidence lives in jessepike/sec-market-private
(web/scripts/pipeline/archive.py EVIDENCE_REMOTE). Fetch the ref into any clone:
  git -C ARCHIVE fetch <private remote> '+refs/archive/market-evidence:refs/archive/market-evidence'
Usage: python3 ops/scorecard/build.py OUT_DIR [--archive ARCHIVE] [--days 7]
ARCHIVE defaults to this repository.
"""
import argparse, collections, json, subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = 'refs/archive/market-evidence'
OKS = {'checked_no_change', 'updated', 'checked_changed'}
PRIMARY = {'official_announcements', 'filing_documents', 'regulatory_filings', 'release_distribution', 'investor_acquirer'}
WHY = {'SOURCE_BINDING_UNVERIFIED': 'Placeholder; never set up', 'HTTP_403': 'Site refuses the collector',
       'HTTP_429': 'Site rate-limits the collector', 'Unapproved source/redirect host': 'Redirects to an unapproved address',
       'CI_COLLECTION_TIME_BUDGET_EXHAUSTED': 'Run ran out of time', 'SUBSCRIPTION_CALL_BUDGET_EXHAUSTED': 'Run ran out of AI calls',
       'HISTORICAL_OR_UNCHANGED_AUDIT_PENDING': 'Found pages, AI review queued',
       'EMPTY_EXTRACTION_NOT_INDEPENDENTLY_CONFIRMED': 'Found pages, review not confirmed',
       'Independent SEC validation failed': 'SEC data not wired for this company yet',
       'Q4_INDEX_INCOMPLETE:Q4_LIST_ROW_SCHEMA_INVALID': 'Press list format changed', 'HTTP_504': 'Site timed out'}
KIND = {'sitemap': 'Newsroom sitemap', 'rss': 'Newsroom feed', 'html_index': 'Newsroom page', 'q4_press_list': 'Investor press list',
        'official_discovery': 'Company site (unset)', 'citation': 'Single record', 'sec_facts': 'SEC financial data',
        'sec_submissions': 'SEC filing index', 'sec_documents': 'SEC filings', 'sec_index': 'SEC filings'}
FAM = {'independent_reporting': 'Independent news', 'release_distribution': 'Wire service', 'investor_acquirer': 'Owner or acquirer',
       'official_announcements': 'Company newsroom', 'regulatory_filings': 'SEC data', 'filing_documents': 'SEC filings'}


class Archive:
    def __init__(self, git_dir):
        self.dir = git_dir
        self.p = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=git_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def read(self, spec):
        self.p.stdin.write((spec + '\n').encode()); self.p.stdin.flush()
        head = self.p.stdout.readline().split()
        if head[-1] == b'missing':
            return None
        body = self.p.stdout.read(int(head[2])); self.p.stdout.read(1)
        return body

    def ls(self, path):
        out = subprocess.run(['git', 'ls-tree', '--name-only', f'{REF}:{path}'], cwd=self.dir, capture_output=True, text=True)
        return out.stdout.split() if out.returncode == 0 else []


def category(r):
    o, e = r['outcome'], r.get('errorCode') or ''
    if o in OKS: return 'ok'
    if e == 'SOURCE_BINDING_UNVERIFIED': return 'setup'
    if 'BUDGET' in e or 'AUDIT_PENDING' in e or e == 'EMPTY_EXTRACTION_NOT_INDEPENDENTLY_CONFIRMED': return 'waiting'
    if e.startswith(('HTTP_403', 'HTTP_429')) or 'redirect' in e: return 'blocked'
    return 'error'


def load_runs(a, days):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    runs = []
    for rid in a.ls('state/runs'):
        plan = a.read(f'{REF}:state/runs/{rid}/plan.json')
        if not plan: continue
        plan = json.loads(plan)
        if plan['scheduledAt'] < cutoff: continue
        rows = [json.loads(a.read(f'{REF}:state/runs/{rid}/attempts/{n}')) for n in a.ls(f'state/runs/{rid}/attempts')]
        if rows: runs.append((plan['scheduledAt'], plan, rows))
    runs.sort(key=lambda x: x[0])
    return runs


def build(days, archive=ROOT):
    a = Archive(archive)
    market = json.loads((ROOT / 'contracts/market.json').read_text())
    cert = set(json.loads((ROOT / 'web/src/data/tracker/certifiedContract.json').read_text())['supplierIds'])
    onb = {s['id'] for s in json.loads((ROOT / 'web/src/data/tracker/onboarding.json').read_text())['suppliers']}
    src = {s['id']: s for s in market['sources']}
    actions = json.loads((Path(__file__).parent / 'actions.json').read_text())['actions']
    runs = load_runs(a, days)
    if not runs: raise SystemExit('No runs in the evidence archive for that window')
    hist = collections.defaultdict(list)
    for at, _, rows in runs:
        for r in rows:
            if r.get('sourceId'): hist[r['sourceId']].append((at[:10], r))
    for h in hist.values(): h.sort(key=lambda x: (x[0], x[1].get('completedAt') or ''))
    missing = collections.defaultdict(list)
    for t in runs[-1][1]['tasks']:
        if t['kind'] == 'missing_discovery': missing[t['supplierId']].append(FAM.get(t['family'], t['family']))
    out = []
    for s in market['suppliers']:
        rows = []
        for sid in s['sourceIds']:
            so, h = src[sid], hist.get(sid, [])
            last = h[-1][1] if h else None
            c = category(last) if last else 'new'
            err = (last.get('errorCode') or '') if last else ''
            reason = 'Collected' if c == 'ok' else ('Added after the latest run' if c == 'new' else WHY.get(err, err[:60]))
            if c == 'ok' and so['kind'] == 'citation': reason = 'Record still matches'
            rows.append({'id': sid, 'label': KIND.get(so['kind'], so['kind']), 'host': so['url'].split('/')[2],
                         'family': so['family'], 'status': c, 'reason': reason, 'errorCode': err or None,
                         'lastOk': max((d for d, r in h if category(r) == 'ok'), default=None), 'url': so['url']})
        live = [r for r in rows if r['family'] in PRIMARY and r['status'] in ('ok', 'waiting')]
        health = ('good' if any(r['status'] == 'ok' for r in live) else 'partial') if live else 'none'
        if health == 'none' and s['kind'] in ('segment', 'acquired') and any(r['status'] == 'ok' for r in rows):
            health = 'parent'  # numbers come from the parent's or acquirer's SEC filings, rechecked every run
        out.append({'id': s['id'], 'name': s['name'], 'kind': s['kind'], 'domains': s['domainIds'],
                    'certified': s['id'] in cert, 'onboarding': s['id'] in onb, 'health': health,
                    'counts': dict(collections.Counter(r['status'] for r in rows)), 'sources': rows,
                    'missingFamilies': sorted(set(missing.get(s['id'], []))), 'action': actions.get(s['id'])})
    return {'generatedAt': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'), 'latestRun': runs[-1][0][:10],
            'latestRunId': runs[-1][1]['runId'], 'runDays': sorted({at[:10] for at, _, _ in runs}), 'suppliers': out}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--days', type=int, default=7); ap.add_argument('--archive', default=str(ROOT))
    args = ap.parse_args(); out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    data = build(args.days, args.archive)
    (out / 'scorecard.json').write_text(json.dumps(data, indent=1))
    tpl = (Path(__file__).parent / 'template.html').read_text()
    (out / 'scorecard.html').write_text(tpl.replace('__DATA__', json.dumps(data).replace('</', '<\\/')))
    st = collections.Counter(r['status'] for s in data['suppliers'] for r in s['sources'])
    print(data['latestRun'], data['runDays'], dict(st), dict(collections.Counter(s['health'] for s in data['suppliers'])))


if __name__ == '__main__':
    main()
