#!/usr/bin/env python3
"""Fact-extraction accuracy eval: replays the pipeline's own extractor on saved pages and scores it.

`run` is manual. It needs a logged-in Codex CLI (subscription, never an API key) and makes one
model call per golden case. `score` is offline and deterministic.

Golden case layout: <golden>/<case-id>/case.json and <golden>/<case-id>/page.html (raw bytes).
"""
import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PIPELINE = REPO / "web/scripts/pipeline"
sys.path.insert(0, str(PIPELINE))

from agents import FACT_SCHEMA  # noqa: E402

PREDICATES = FACT_SCHEMA["properties"]["facts"]["items"]["properties"]["predicate"]["enum"]
EVENT_STATUSES = FACT_SCHEMA["properties"]["facts"]["items"]["properties"]["eventStatus"]["enum"]
DATE_WINDOW_DAYS = 3
AMOUNT_TOLERANCE = Decimal("0.01")
ABORT_ERRORS = {"CHATGPT_SUBSCRIPTION_LOGIN_REQUIRED", "CHATGPT_SIGN_IN_AGAIN", "SUBSCRIPTION_LIMIT_REACHED",
                "SUBSCRIPTION_RUNNER_UNAVAILABLE", "SUBSCRIPTION_CALL_BUDGET_EXHAUSTED"}
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


# ---------- golden set ----------

def validate_case(case):
    """Return a list of problems with a case.json object (empty when valid)."""
    problems = []
    required = {"id", "url", "capturedAt", "supplierId", "supplierName", "kind", "expectedFacts", "notes"}
    missing = required - set(case)
    if missing:
        problems.append(f"missing keys: {sorted(missing)}")
        return problems
    if case["kind"] not in ("positive", "negative"):
        problems.append("kind must be positive or negative")
    if not str(case["url"]).startswith("https://"):
        problems.append("url must be https")
    if not ISO_DATE.fullmatch(case["capturedAt"]):
        problems.append("capturedAt must be YYYY-MM-DD")
    if not isinstance(case["expectedFacts"], list):
        return problems + ["expectedFacts must be a list"]
    if case["kind"] == "negative" and case["expectedFacts"]:
        problems.append("a negative case must have no expected facts")
    if case["kind"] == "positive" and not [f for f in case["expectedFacts"] if not f.get("optional")]:
        problems.append("a positive case needs at least one required fact")
    for i, fact in enumerate(case["expectedFacts"]):
        where = f"expectedFacts[{i}]"
        allowed = {"predicate", "effectiveDate", "amount", "currency", "eventStatus", "acceptableDates", "optional"}
        extra = set(fact) - allowed
        if extra:
            problems.append(f"{where}: unknown keys {sorted(extra)}")
        if fact.get("predicate") not in PREDICATES:
            problems.append(f"{where}: predicate {fact.get('predicate')!r} not in FACT_SCHEMA enum")
        for key in (fact.get("effectiveDate"), *fact.get("acceptableDates", [])):
            if key is not None and not ISO_DATE.fullmatch(key):
                problems.append(f"{where}: bad date {key!r}")
        if fact.get("amount") is not None and parse_amount(fact["amount"]) is None:
            problems.append(f"{where}: amount {fact['amount']!r} is not numeric")
        if fact.get("eventStatus") is not None and fact["eventStatus"] not in EVENT_STATUSES:
            problems.append(f"{where}: eventStatus {fact['eventStatus']!r} not in FACT_SCHEMA enum")
    return problems


def load_golden(golden_dir):
    cases = []
    for folder in sorted(p for p in Path(golden_dir).iterdir() if p.is_dir()):
        case = json.loads((folder / "case.json").read_text())
        case["_dir"] = folder
        cases.append(case)
    return cases


# ---------- run (manual, uses the subscription CLI) ----------

def cmd_run(args):
    from agents import SubscriptionAgent, ModelUnavailable
    from documents import article_input

    output = Path(args.output)
    if output.exists():
        sys.exit(f"Refusing to overwrite {output}")
    contract = json.loads((REPO / "contracts/market.json").read_text())
    suppliers = {s["id"]: s for s in contract["suppliers"]}
    agent = SubscriptionAgent(contract["model"])
    results, aborted = {}, None
    for case in load_golden(args.golden):
        if aborted:
            results[case["id"]] = {"facts": None, "error": f"NOT_RUN_{aborted}"}
            continue
        try:
            # Same model input as production (engine.py): readable text plus publication-date metadata.
            text = article_input((case["_dir"] / "page.html").read_bytes(), {"requestedUrl": case["url"]})["modelText"]
            results[case["id"]] = {"facts": agent.extract(text, suppliers[case["supplierId"]]), "error": None}
        except ModelUnavailable as exc:
            results[case["id"]] = {"facts": None, "error": str(exc)}
            if str(exc) in ABORT_ERRORS:
                aborted = str(exc)
        except Exception as exc:  # a bad page or a budget refusal must not stop the whole run
            results[case["id"]] = {"facts": None, "error": f"{type(exc).__name__}: {exc}"}
        print(f"{case['id']}: {results[case['id']]['error'] or len(results[case['id']]['facts'])} ", file=sys.stderr)
    payload = {"schemaVersion": 1, "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "model": {k: contract["model"][k] for k in ("provider", "maxDocumentChars", "timeoutSeconds")},
               "cases": results}
    with open(output, "x") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    print(f"Wrote {output}")


# ---------- score (offline) ----------

def parse_amount(value):
    if value is None:
        return None
    try:
        return Decimal(str(value).replace(",", ""))
    except InvalidOperation:
        return None


def day_gap(a, b):
    return abs((date.fromisoformat(a) - date.fromisoformat(b)).days)


def date_ok(expected_dates, predicted):
    """True when the dates are compatible. A null expected date is not checked.

    A missing or partial predicted date (None, "2026", "2026-01") still matches when it
    agrees with an expected date, so the fact counts as found; date accuracy then
    reports it as not exact instead of the scorer counting one miss plus one false positive.
    """
    if not expected_dates:
        return True
    if predicted is None:
        return True
    if not ISO_DATE.fullmatch(predicted):
        return any(d.startswith(predicted) for d in expected_dates) if re.fullmatch(r"\d{4}(-\d{2})?", predicted) else False
    return any(day_gap(d, predicted) <= DATE_WINDOW_DAYS for d in expected_dates)


def amount_ok(expected, predicted):
    e, p = parse_amount(expected), parse_amount(predicted)
    if expected is None or predicted is None:
        return True
    if e is None or p is None:
        return False
    if e == 0:
        return p == 0
    return abs(p - e) / abs(e) <= AMOUNT_TOLERANCE


def compatible(case, expected, fact):
    dates = [d for d in [expected.get("effectiveDate"), *expected.get("acceptableDates", [])] if d]
    return (fact.get("supplierId") == case["supplierId"] and fact.get("predicate") == expected["predicate"]
            and date_ok(dates, fact.get("effectiveDate")) and amount_ok(expected.get("amount"), fact.get("amount")))


def score_case(case, facts):
    """Match predictions to expectations one-to-one, required facts first."""
    order = sorted(range(len(case["expectedFacts"])), key=lambda i: bool(case["expectedFacts"][i].get("optional")))
    used, matches, missed = set(), [], []
    for i in order:
        expected = case["expectedFacts"][i]
        options = [j for j, f in enumerate(facts) if j not in used and compatible(case, expected, f)]
        if not options:
            if not expected.get("optional"):
                missed.append(expected)
            continue
        primary = expected.get("effectiveDate")
        best = min(options, key=lambda j: (facts[j].get("effectiveDate") != primary, facts[j].get("effectiveDate") or ""))
        used.add(best)
        got = facts[best]
        exact = {expected.get("effectiveDate"), *expected.get("acceptableDates", [])} - {None}
        matches.append({"expected": expected, "predicted": got,
                        "dateChecked": bool(exact), "dateExact": got.get("effectiveDate") in exact,
                        "statusChecked": expected.get("eventStatus") is not None,
                        "statusCorrect": got.get("eventStatus") == expected.get("eventStatus")})
    extras, duplicates = [], []
    for j, fact in enumerate(facts):
        if j in used:
            continue
        # A second statement of an already matched fact (for example each appointee in one release) is not an error.
        if any(compatible(case, m["expected"], fact) for m in matches):
            duplicates.append(fact)
        else:
            extras.append(fact)
    return {"matches": matches, "missed": missed, "falsePositives": extras, "duplicates": duplicates}


def ratio(num, den):
    return round(num / den, 4) if den else None


def tally(rows):
    tp = sum(r["tp"] for r in rows)
    fp = sum(r["fp"] for r in rows)
    fn = sum(r["fn"] for r in rows)
    dc = sum(r["dateChecked"] for r in rows)
    sc = sum(r["statusChecked"] for r in rows)
    return {"truePositives": tp, "falsePositives": fp, "misses": fn,
            "precision": ratio(tp, tp + fp), "recall": ratio(tp, tp + fn),
            "dateAccuracy": ratio(sum(r["dateExact"] for r in rows), dc), "dateChecked": dc,
            "typeAccuracy": ratio(sum(r["statusCorrect"] for r in rows), sc), "typeChecked": sc}


def score(golden_dir, predictions):
    cases = load_golden(golden_dir)
    per_case, rows_by_predicate, all_rows = {}, {}, []
    unscored, negatives, negatives_with_fp, negative_fact_count = [], 0, 0, 0
    for case in cases:
        entry = predictions.get("cases", {}).get(case["id"])
        if entry is None or entry.get("facts") is None:
            unscored.append({"id": case["id"], "reason": (entry or {}).get("error") or "no prediction"})
            continue
        result = score_case(case, entry["facts"])
        per_case[case["id"]] = {"kind": case["kind"], "url": case["url"], **result}
        for m in result["matches"]:
            row = {"tp": 1, "fp": 0, "fn": 0, "dateChecked": int(m["dateChecked"]), "dateExact": int(m["dateChecked"] and m["dateExact"]),
                   "statusChecked": int(m["statusChecked"]), "statusCorrect": int(m["statusChecked"] and m["statusCorrect"])}
            rows_by_predicate.setdefault(m["expected"]["predicate"], []).append(row)
            all_rows.append(row)
        for miss in result["missed"]:
            row = {"tp": 0, "fp": 0, "fn": 1, "dateChecked": 0, "dateExact": 0, "statusChecked": 0, "statusCorrect": 0}
            rows_by_predicate.setdefault(miss["predicate"], []).append(row)
            all_rows.append(row)
        for fp in result["falsePositives"]:
            row = {"tp": 0, "fp": 1, "fn": 0, "dateChecked": 0, "dateExact": 0, "statusChecked": 0, "statusCorrect": 0}
            rows_by_predicate.setdefault(fp.get("predicate") or "unknown", []).append(row)
            all_rows.append(row)
        if case["kind"] == "negative":
            negatives += 1
            negative_fact_count += len(entry["facts"])
            negatives_with_fp += bool(entry["facts"])
    return {
        "schemaVersion": 1,
        "scoredCases": len(per_case), "unscoredCases": unscored,
        "matching": {"dateWindowDays": DATE_WINDOW_DAYS, "amountTolerance": float(AMOUNT_TOLERANCE),
                     "typeAccuracyMeans": "eventStatus agrees, among matched facts whose expected eventStatus is set",
                     "duplicates": "extra statements of an already matched fact are listed but not counted as false positives"},
        "overall": tally(all_rows),
        "byPredicate": {p: tally(rows) for p, rows in sorted(rows_by_predicate.items())},
        "negativePages": {"cases": negatives, "casesWithAnyFact": negatives_with_fp, "factsReturned": negative_fact_count,
                          "falsePositiveRate": ratio(negatives_with_fp, negatives)},
        "cases": per_case,
    }


def pct(x):
    return "n/a" if x is None else f"{x * 100:.1f}%"


def markdown(report):
    o = report["overall"]
    lines = ["# Extraction eval", "",
             f"Scored {report['scoredCases']} cases; {len(report['unscoredCases'])} not scored.", "",
             "| Predicate | Precision | Recall | Date accuracy | Type accuracy | TP | FP | Miss |", "|---|---|---|---|---|---|---|---|"]
    for name, t in [*report["byPredicate"].items(), ("**overall**", o)]:
        lines.append(f"| {name} | {pct(t['precision'])} | {pct(t['recall'])} | {pct(t['dateAccuracy'])} | {pct(t['typeAccuracy'])} | {t['truePositives']} | {t['falsePositives']} | {t['misses']} |")
    n = report["negativePages"]
    lines += ["", f"No-fact pages: {n['casesWithAnyFact']} of {n['cases']} returned at least one fact "
              f"(false-positive rate {pct(n['falsePositiveRate'])}, {n['factsReturned']} facts in all).", ""]
    if report["unscoredCases"]:
        lines += ["## Not scored", *[f"- {u['id']}: {u['reason']}" for u in report["unscoredCases"]], ""]
    misses = [(cid, m) for cid, c in report["cases"].items() for m in c["missed"]]
    fps = [(cid, f) for cid, c in report["cases"].items() for f in c["falsePositives"]]
    miss_lines = [f"- {cid}: {m['predicate']} {m.get('effectiveDate')} {m.get('amount') or ''}".rstrip() for cid, m in misses]
    fp_lines = [f"- {cid}: {f.get('predicate')} {f.get('effectiveDate')} {f.get('amount') or ''} \"{(f.get('valueText') or '')[:80]}\"" for cid, f in fps]
    lines += ["## Misses", *(miss_lines or ["- none"]), "", "## False positives", *(fp_lines or ["- none"]), ""]
    return "\n".join(lines)


def cmd_score(args):
    out = Path(args.output)
    md = out.with_suffix(".md")
    for path in (out, md):
        if path.exists():
            sys.exit(f"Refusing to overwrite {path}")
    report = score(args.golden, json.loads(Path(args.predictions).read_text()))
    with open(out, "x") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    with open(md, "x") as handle:
        handle.write(markdown(report))
    print(f"Wrote {out} and {md}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="manual: call the subscription extractor on every golden case")
    run.add_argument("--golden", required=True)
    run.add_argument("--output", required=True)
    run.set_defaults(func=cmd_run)
    sc = sub.add_parser("score", help="offline: score a predictions file")
    sc.add_argument("--golden", required=True)
    sc.add_argument("--predictions", required=True)
    sc.add_argument("--output", required=True, help="JSON report path; the Markdown summary is written beside it")
    sc.set_defaults(func=cmd_score)
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
