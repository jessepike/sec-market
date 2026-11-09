"""Graduate onboarding suppliers to the live tracker (D-138).

A supplier in web/src/data/tracker/onboarding.json goes live after one clean
scheduled daily run (owner, 2026-11-09; the plan's three runs were never asked
for) plus every build check passing. A run is clean for a supplier when, in that day's
scheduled run:
  1. every seed record verifies: each citation source either still matches, or
     an -alt copy of the same record does (the original may be blocked);
  2. at least one company, wire, owner or SEC source answered (collected, or
     reachable with its review queued);
  3. no source failed with an unexplained error (a placeholder that was never
     set up does not count against it);
  4. for a public SEC filer, the SEC validation passed.

Graduation records the supplier under `graduated` in onboarding.json, with the
date and the clean run ids. web/src/data/tracker/graduation.ts then adds its
seed record, evidence and events to the live tracker. The reviewed correction
baseline (originals.json, contracts/factual-baseline.json) is not touched.

Usage (repo root, evidence ref fetched as in ops/scorecard/build.py):
  python3 ops/onboarding/graduate.py            # report only
  python3 ops/onboarding/graduate.py --apply    # also move the passing suppliers
  [--archive DIR] [--runs 3] [--json OUT]
"""
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'ops/scorecard'))
import build as sc  # noqa: E402

ONB = ROOT / 'web/src/data/tracker/onboarding.json'
MARKET = ROOT / 'contracts/market.json'
SEC_FAILED = 'Independent SEC validation failed'


def daily_runs(archive, count):
    """The last `count` scheduled daily runs, one per day (the latest run of each day)."""
    runs = sc.load_runs(sc.Archive(archive), count + 4)
    by_day = {}
    for at, plan, rows in runs:
        by_day[at[:10]] = (at, plan, rows)
    return [by_day[d] for d in sorted(by_day)][-count:]


def verdict(supplier_id, market, rows):
    src = {s['id']: s for s in market['sources']}
    sup = next(s for s in market['suppliers'] if s['id'] == supplier_id)
    mine = {r['sourceId']: r for r in rows if r.get('sourceId') in sup['sourceIds']}
    reasons = []
    if not mine:
        return False, ['not collected in this run']
    cats = {sid: sc.category(r) for sid, r in mine.items()}
    # 1. Seed records verify, directly or through an -alt copy.
    for sid in sup['sourceIds']:
        if src[sid]['kind'] != 'citation' or '-alt' in sid:
            continue
        copies = [sid] + [x for x in sup['sourceIds'] if x.startswith(sid + '-alt')]
        if not any(cats.get(x) == 'ok' for x in copies):
            reasons.append(f'seed record {sid.split(":")[-1]} did not verify')
    # 2. A primary source answered.
    if not any(cats.get(sid) in ('ok', 'waiting') for sid in sup['sourceIds'] if src[sid]['family'] in sc.PRIMARY):
        reasons.append('no company, wire, owner or SEC source answered')
    # 3 and 4. Errors, including SEC validation.
    for sid, c in cats.items():
        if c != 'error':
            continue
        err = mine[sid].get('errorCode') or ''
        reasons.append('SEC validation failed' if err == SEC_FAILED else f'{sid} failed: {err[:60]}')
    return not reasons, sorted(set(reasons))


def evaluate(archive, needed):
    market = json.loads(MARKET.read_text())
    onb = json.loads(ONB.read_text())
    runs = daily_runs(archive, needed)
    report = []
    for s in [x for x in onb['suppliers'] if x['id'] not in onb.get('graduated', {})]:
        days = []
        for at, plan, rows in runs:
            ok, why = verdict(s['id'], market, rows)
            days.append({'day': at[:10], 'runId': plan['runId'], 'clean': ok, 'reasons': why})
        streak = 0
        for d in reversed(days):
            if not d['clean']:
                break
            streak += 1
        report.append({'id': s['id'], 'name': s['name'], 'streak': streak, 'graduates': streak >= needed, 'days': days})
    return report


def graduate(report_by_id, ids, today):
    """Mark suppliers graduated in onboarding.json. graduation.ts then publishes their seed records."""
    onb = json.loads(ONB.read_text())
    known = {s['id'] for s in onb['suppliers']}
    grad = onb.setdefault('graduated', {})
    done = []
    for sid in ids:
        if sid not in known or sid in grad:
            continue
        runs = [d['runId'] for d in report_by_id.get(sid, {}).get('days', []) if d['clean']]
        grad[sid] = {'date': today, 'runIds': runs}
        done.append(sid)
    ONB.write_text(json.dumps(onb, indent=2, ensure_ascii=False) + '\n')
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true'); ap.add_argument('--archive', default=str(ROOT))
    ap.add_argument('--runs', type=int, default=1); ap.add_argument('--json')
    ap.add_argument('--only', nargs='*', help='graduate these ids regardless of the run check (testing)')
    a = ap.parse_args()
    report = evaluate(a.archive, a.runs)
    for r in report:
        last = r['days'][-1]
        print(f"{r['id']:12} clean runs in a row: {r['streak']}/{a.runs}  {'GRADUATES' if r['graduates'] else '; '.join(last['reasons']) or 'needs more runs'}")
    if a.json:
        Path(a.json).write_text(json.dumps(report, indent=1))
    ids = a.only if a.only is not None else [r['id'] for r in report if r['graduates']]
    if a.apply and ids:
        from datetime import datetime, timezone
        print('graduated:', graduate({r['id']: r for r in report}, ids, datetime.now(timezone.utc).strftime('%Y-%m-%d')))


if __name__ == '__main__':
    main()
