"""Generate the human-readable matrix from the exact execution denominator."""
import csv
import io
from collections import Counter

from contracts import digest, plan_run


def inventory(contract, at, coverage=None):
    from separation import enabled as separated
    plan = plan_run(contract, at)
    # A receipt for a different policy must not annotate this policy as checked.
    receipts = {r["taskId"]: r for r in (coverage or {}).get("receipts", [])} if (coverage or {}).get("contractSha256") == digest(contract) else {}
    measures = {r['taskId']: r for r in (coverage or {}).get('tasks', [])} if receipts else {}
    sources = {s["id"]: s for s in contract["sources"]}
    suppliers = {s["id"]: s for s in contract["suppliers"]}
    rows = []
    for task in plan["tasks"]:
        source = sources.get(task["sourceId"], {})
        receipt = receipts.get(task["taskId"], {})
        row = {"taskId": task["taskId"], "supplierId": task["supplierId"], "supplier": suppliers[task["supplierId"]]["name"],
                     "supplierKind": suppliers[task["supplierId"]]["kind"],
                     "startupStatus": suppliers[task["supplierId"]].get("startupStatus", "unclassified"),
                     "family": source.get("family", task.get("family")), "sourceId": task["sourceId"] or "",
                     "url": source.get("url", ""), "method": source.get("kind", "missing_binding"),
                     "registration": source.get("registration", "missing"), "required": task["required"],
                     "intervalHours": contract["schedule"]["intervalHours"],
                     "lastCheckedAt": receipt.get("completedAt") or "",
                     "outcome": receipt.get("outcome", "not_checked"), "errorCode": receipt.get("errorCode") or ""}
        if separated(contract):
            measure = measures.get(task['taskId'], {})
            row.update(outcome=measure.get('intakeOutcome', 'not_checked'), errorCode=measure.get('intakeErrorCode') or '',
                       measure='daily_source_intake_v2', intakeOutcome=measure.get('intakeOutcome', 'not_checked'),
                       intakeErrorCode=measure.get('intakeErrorCode'), processingOutcome=receipt.get('outcome', 'not_checked'),
                       processingErrorCode=receipt.get('errorCode'), processing=measure.get('processing'),
                       historicalReview=measure.get('historicalReview'), processingManifest=receipt.get('processingManifest'))
        rows.append(row)
    return sorted(rows, key=lambda r: (r["supplierId"], r["family"], r["sourceId"]))


def csv_matrix(rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def markdown_matrix(contract, rows):
    counts = Counter(r["registration"] for r in rows)
    lines = ["# Daily coverage matrix", "", "Generated from `contracts/market.json`. This is a proposed execution inventory, not proof that live automation is operating.", "",
             f"Contract SHA-256: `{digest(contract)}`.", "",
             f"{len(contract['suppliers'])} suppliers; {len(rows)} required tasks; {counts['missing']} missing bindings; {counts['candidate']} candidate bindings. Every required task is due daily, with reconciliation on every run. Overdue after {contract['schedule']['overdueHours']} hours.", "",
             "A verified binding means its collector is registered; only a current successful receipt proves a check occurred. Citation integrity checks existing links; it does not discover new news. Startup status is explicitly unclassified until reviewed. A missing binding stays in the denominator.", "",
             "See `source-matrix.csv` for every task, URL, collector, registration, last check and outcome.", "",
             "| Supplier | Kind | Startup status | Required | Verified bindings | Candidates | Missing | Last run successes |",
             "|---|---|---|---:|---:|---:|---:|---:|"]
    for supplier in contract["suppliers"]:
        subset = [r for r in rows if r["supplierId"] == supplier["id"]]
        c = Counter(r["registration"] for r in subset)
        successful = sum(r["outcome"] in ("updated", "checked_no_change", "checked") for r in subset)
        lines.append(f"| {supplier['name']} | {supplier['kind']} | {supplier.get('startupStatus', 'unclassified')} | {len(subset)} | {c['verified']} | {c['candidate']} | {c['missing']} | {successful} |")
    return "\n".join(lines) + "\n"
