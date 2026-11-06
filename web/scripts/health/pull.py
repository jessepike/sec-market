"""Pulls the SEC XBRL companyfacts concepts used for operating and free cash flow margins.

Mockup-stage helper (homepage momentum view, 2026-11-06). Run where data.sec.gov is reachable:
    python3 scripts/health/pull.py .ctx/health-raw.json
then:
    python3 scripts/health/compute.py .ctx/health-raw.json src/data/generated/edgarFacts.json src/data/generated/healthFacts.json
Not yet part of the daily refresh or the certified check.
"""
import json, sys, time, urllib.request
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[2] / 'src/data/tracker/certifiedContract.json'
CONCEPTS = ["OperatingIncomeLoss", "NetIncomeLoss", "NetCashProvidedByUsedInOperatingActivities",
            "PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets", "PaymentsForSoftware",
            "PaymentsToDevelopSoftware", "CashAndCashEquivalentsAtCarryingValue", "ShortTermInvestments",
            "MarketableSecuritiesCurrent", "AvailableForSaleSecuritiesDebtSecuritiesCurrent", "LongTermDebt",
            "LongTermDebtNoncurrent", "LongTermDebtCurrent", "ConvertibleNotesPayable", "ConvertibleNotesPayableCurrent",
            "ConvertibleLongTermNotesPayable", "ConvertibleDebtNoncurrent", "ConvertibleDebtCurrent"]

def main(out_path: str) -> None:
    ids = set(json.loads(REGISTRY.read_text())['supplierIds'])
    edgar = json.loads((REGISTRY.parents[1] / 'generated/edgarFacts.json').read_text())
    out = {}
    for s in edgar['suppliers']:
        if s['id'] not in ids: continue
        req = urllib.request.Request(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{s['cik']}.json",
                                     headers={"User-Agent": "SecurityMarketPulse research jesse@keatingpike.com", "Accept": "application/json"})
        g = json.load(urllib.request.urlopen(req, timeout=60)).get("facts", {}).get("us-gaap", {})
        out[s['id']] = {c: [f for f in g[c]["units"]["USD"] if f.get("end", "") >= "2023-01-01"]
                        for c in CONCEPTS if g.get(c, {}).get("units", {}).get("USD")}
        time.sleep(0.3)
    Path(out_path).write_text(json.dumps(out))

if __name__ == '__main__':
    main(sys.argv[1])
