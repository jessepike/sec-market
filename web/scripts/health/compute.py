import json, sys
from datetime import date, timedelta
raw = json.load(open(sys.argv[1])); ef = json.load(open(sys.argv[2]))
D = lambda s: date.fromisoformat(s)
def facts(rec, c):
    best = {}
    for f in rec.get(c, []):
        if f.get('form') not in ('10-Q', '10-K', '10-Q/A', '10-K/A'): continue
        k = (f.get('start'), f['end'])
        if k not in best or f['filed'] > best[k]['filed']: best[k] = f
    return list(best.values())
def ttm(rec, c, end):
    fs = [f for f in facts(rec, c) if f.get('start')]
    at = [f for f in fs if f['end'] == end]
    if not at: return None
    f = max(at, key=lambda f: (D(f['end']) - D(f['start'])).days)
    days = (D(f['end']) - D(f['start'])).days
    if days > 350: return f['val'], [f]
    fy = [g for g in fs if D(g['end']) == D(f['start']) - timedelta(days=1) and (D(g['end']) - D(g['start'])).days > 350]
    py = [g for g in fs if abs((D(g['end']) - (D(f['end']) - timedelta(days=365))).days) <= 7 and abs((D(g['end']) - D(g['start'])).days - days) <= 7]
    if not fy or not py: return None
    return fy[0]['val'] + f['val'] - py[0]['val'], [f, fy[0], py[0]]
def ttm_bridged(rec, c, alt, end):
    # Same as ttm, but when the prior fiscal year is tagged only under `alt`, use it if the two
    # concepts carry identical values for at least one shared prior-year period (a tag rename).
    r = ttm(rec, c, end)
    if r: return r
    fs = {(f.get('start'), f['end']): f['val'] for f in facts(rec, c) if f.get('start')}
    alts = {(f.get('start'), f['end']): f['val'] for f in facts(rec, alt) if f.get('start')}
    shared = [k for k in fs if k in alts and fs[k] == alts[k]]
    if not shared: return None
    merged = dict(rec); merged[c] = rec.get(c, []) + [f for f in rec.get(alt, []) if (f.get('start'), f['end']) not in fs and (D(f['end']) - D(f['start'])).days > 350]
    r = ttm(merged, c, end)
    return (r[0], r[1], 'bridged') if r else None
def inst(rec, c, end):
    at = [f for f in facts(rec, c) if f['end'] == end and not f.get('start')]
    return max(at, key=lambda f: f['filed']) if at else None
url = lambda f: f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{f['accn'].replace('-', '')}/{f['accn']}-index.htm"
out = {'generatedAt': ef['generatedAt'], 'method': {
  'operatingMargin': 'OperatingIncomeLoss over revenue, trailing four quarters ending on the latest revenue quarter. Year-to-date facts are converted with the prior fiscal year: FY + YTD - prior YTD.',
  'fcfMargin': 'NetCashProvidedByUsedInOperatingActivities minus PaymentsToAcquirePropertyPlantAndEquipment (PaymentsToAcquireProductiveAssets when PP&E is not tagged) minus capitalized software (PaymentsToDevelopSoftware or PaymentsForSoftware), over revenue, trailing four quarters.',
  'revenue': 'The same four quarters of certified SEC revenue the tracker shows (edgarFacts.json).'},
  'suppliers': {}, 'gaps': {}}
for s in ef['suppliers']:
    sid = s['id']; rec = raw.get(sid)
    if rec is None: continue
    cik = s['cik']; qs = sorted(s['quarters'], key=lambda q: q['periodEnd'], reverse=True)[:4]
    end = qs[0]['periodEnd']; gaps = []; notes = []
    ends = [D(q['periodEnd']) for q in qs]
    consecutive = len(qs) == 4 and all(80 <= (ends[i] - ends[i + 1]).days <= 100 for i in range(3))
    rev = sum(q['value'] for q in qs) if consecutive else None
    if rev is None: gaps.append('four consecutive revenue quarters')
    op = ttm(rec, 'OperatingIncomeLoss', end); cfo = ttm(rec, 'NetCashProvidedByUsedInOperatingActivities', end)
    if rec.get('PaymentsToAcquirePropertyPlantAndEquipment'):
        capc = 'PaymentsToAcquirePropertyPlantAndEquipment'; cap = ttm_bridged(rec, capc, 'PaymentsToAcquireProductiveAssets', end)
    else:
        capc = 'PaymentsToAcquireProductiveAssets'; cap = ttm(rec, capc, end)
    if cap and len(cap) == 3: notes.append('prior fiscal year capital expenditure tagged as PaymentsToAcquireProductiveAssets; matched on a shared period')
    sw = [ttm(rec, c, end) for c in ('PaymentsToDevelopSoftware', 'PaymentsForSoftware')]
    sw = next((x for x in sw if x), None)
    h = {'operatingMargin': None, 'fcfMargin': None, 'balance': None}
    if op and rev: h['operatingMargin'] = {'value': round(op[0] / rev * 100, 1), 'periodEnd': end, 'form': op[1][0]['form'], 'sourceUrl': url(op[1][0])}
    else: gaps.append('operating income, trailing four quarters')
    if cfo and cap and rev:
        fcf = cfo[0] - cap[0] - (sw[0] if sw else 0)
        h['fcfMargin'] = {'value': round(fcf / rev * 100, 1), 'periodEnd': end, 'form': cfo[1][0]['form'], 'sourceUrl': url(cfo[1][0])}
    else: gaps.append('operating cash flow or capital expenditure, trailing four quarters')
    out['suppliers'][sid] = h
    if gaps: out['gaps'][sid] = gaps
    if notes: out.setdefault('notes', {})[sid] = notes
    print(f"{sid:11} {end} rev {rev and rev/1e6:9.0f}M op {h['operatingMargin'] and h['operatingMargin']['value']}% fcf {h['fcfMargin'] and h['fcfMargin']['value']}% capex={capc[:22]} sw={'y' if sw else 'n'} {gaps}")
json.dump(out, open(sys.argv[3], 'w'), indent=1)
