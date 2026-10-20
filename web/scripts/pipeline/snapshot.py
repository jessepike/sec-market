"""Materialize only independently rechecked facts into the site's data schema."""
import json
import re
from datetime import timedelta
from decimal import Decimal

from contracts import digest, instant, require
from validation import eligible_fact_references, normalize, reconcile, verified_partial_document_facts
from reporting import inventory

EVENT_TYPES = {"funding": "funding", "valuation": "funding", "revenue": "results", "arr": "results",
               "acquisition": "acquisition", "leadership_change": "exec-change", "restructuring": "restructuring",
               "layoff": "layoff", "debt": "debt", "shutdown": "shutdown", "late_filing": "late-filing"}


def money(fact):
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CAD": "C$", "AUD": "A$"}
    amount = Decimal(str(fact["amount"]))
    text = format(amount, ",f").rstrip("0").rstrip(".") if amount % 1 else format(amount, ",.0f")
    prefix = {"exact": "", "approximately": "approximately ", "at_least": "at least ", "more_than": "more than ", "up_to": "up to "}[fact["qualifier"]]
    return prefix + symbols[fact["currency"]] + text


def build_snapshot(contract, plan, coverage, store, now, baseline=None, previous=None):
    # Recompute from raw receipts and evidence, not a worker's completion flag.
    verified = reconcile(plan, coverage["receipts"], contract, now, store)
    require(verified["runId"] == coverage["runId"], "Snapshot run differs")
    age = (instant(now) - instant(coverage["checkedAt"])).total_seconds() / 3600
    require(0 <= age <= contract["schedule"]["overdueHours"], "Snapshot coverage is stale/future")
    suppliers = {s["id"]: s for s in contract["suppliers"]}
    baseline = {s["id"]: s for s in (baseline or [])}
    sources = {s["id"]: s for s in contract["sources"]}
    previous = previous if (previous or {}).get("enabled") else {}
    events = {e["id"]: e for e in previous.get("events", [])}
    evidence = {e["id"]: e for e in previous.get("evidence", [])}
    updates = dict(previous.get("supplierUpdates", {}))
    update_dates = dict(previous.get("supplierUpdateDates", {}))
    queue, facts_by_id, sec_records = list(previous.get("reviewQueue", [])), {}, {}
    for receipt in verified["receipts"]:
        for ref in receipt.get("heldClaims", []):
            held = json.loads(store.get(ref))
            queue.append({"factId": held["candidateSha256"], "supplierId": held["supplierId"],
                          "reason": held["reason"], "receiptSha256": ref["sha256"]})
    references = [*eligible_fact_references(verified), *verified_partial_document_facts(plan, verified, contract, now, store)]
    for reference in references:
        fact = json.loads(store.get(reference))
        if fact.get("assurance") == "sec_rederived":
            if fact["predicate"] == "sec_revenue_snapshot":
                sec_records[fact["supplierId"]] = fact["value"]
            continue
        require(fact.get("review") and fact.get("assurance") == "source_statement_matched", "Unreviewed fact in snapshot")
        observation = store.read(f"observations/{fact['sourceObservationId']}.json")
        source = sources[observation["sourceId"]]
        # A single independent-media report cannot establish the published fact.
        if source["family"] not in ("official_announcements", "release_distribution", "investor_acquirer", "filing_documents"):
            queue.append({"factId": fact["factId"], "supplierId": fact["supplierId"], "reason": "PRIMARY_SOURCE_REQUIRED"})
            continue
        require(fact["supplierId"] in suppliers and fact["predicate"] in EVENT_TYPES, "Unknown supplier/predicate")
        require(fact["scope"] == "company" or suppliers[fact["supplierId"]]["kind"] == "segment", "Claim entity scope requires review")
        # Prefer company/filing evidence to a distributed copy for the same assertion.
        rank = 1 if source["family"] in ("official_announcements", "filing_documents") else 4
        old = facts_by_id.get(fact["factId"])
        if old is None or rank < old[0]:
            facts_by_id[fact["factId"]] = (rank, fact, observation, source)
    for rank, fact, observation, source in sorted(facts_by_id.values(), key=lambda x: (x[1]["effectiveDate"], x[1]["factId"])):
        fid, sid, date = fact["factId"], fact["supplierId"], fact["effectiveDate"]
        eid = f"DAILY-{fid}"
        evidence[eid] = {"id": eid, "title": f"{suppliers[sid]['name']}: reported {fact['predicate'].replace('_', ' ')}",
                         "organization": suppliers[sid]["name"] if rank == 1 else source["allowedHosts"][0],
                         "publicationDate": date, "economicPeriod": f"Statement dated {date}",
                         "canonicalUrl": observation.get("finalUrl", observation["requestedUrl"]), "excerpt": normalize(fact["quote"]),
                         "sourceClass": "FILING" if source["family"] == "filing_documents" else "OFFICIAL",
                         "interpretation": "", "limitations": "Source statement matched. This does not certify undisclosed information.",
                         "conflictingEvidenceIds": [], "artifactLabel": "Archived source statement", "tags": ["daily", sid],
                         "retrievedAt": observation["fetchedAt"][:10],
                         "retrieval": {"finalUrl": observation.get("finalUrl", observation["requestedUrl"]), "sha256": observation["body"]["sha256"], "fetchedAt": observation["fetchedAt"], "locator": fact["quote"]}}
        events[f"EV-daily-{fid}"] = {"id": f"EV-daily-{fid}", "supplierId": sid, "date": date,
                                           "type": EVENT_TYPES[fact["predicate"]], "text": normalize(fact["valueText"]), "evidenceIds": [eid], "rung": rank}
        field, value = None, None
        if fact["predicate"] in ("arr", "revenue") and fact["amount"] is not None and suppliers[sid]["kind"] not in ("public", "segment"):
            # Keep reported ARR distinct; never replace certified GAAP quarter fields.
            field = "headlineMetric"
            value = {"label": "ARR" if fact["predicate"] == "arr" else "Reported revenue", "value": money(fact), "period": f"Reported {date}", "evidenceIds": [eid]}
        elif fact["predicate"] == "funding" and fact["amount"] is not None:
            stage = re.search(r"\b(Series [A-Z](?:-\d)?|pre-seed|seed)\b", fact["quote"], re.I)
            existing = updates.get(sid, {}).get("lastRound") or baseline.get(sid, {}).get("lastRound", {})
            if stage and date > existing.get("date", ""):
                field, value = "lastRound", {"date": date, "stage": stage[0], "amount": money(fact), "evidenceIds": [eid]}
            elif not stage:
                queue.append({"factId": fid, "supplierId": sid, "reason": "ROUND_DETAILS_HELD_EVENT_ONLY"})
        if field:
            key = f"{sid}.{field}"
            if date > update_dates.get(key, ""):
                updates[sid] = {**updates.get(sid, {}), field: value}
                update_dates[key] = date
            elif date == update_dates.get(key) and updates[sid].get(field) != value:
                # Two same-date assertions must not silently overwrite each other.
                updates[sid].pop(field, None)
                queue.append({"factId": fid, "supplierId": sid, "reason": "CONFLICTING_SAME_DATE_FIELD"})
    tasks_by_supplier = {}
    for task in plan["tasks"]:
        if task["required"]:
            tasks_by_supplier.setdefault(task["supplierId"], []).append(task["taskId"])
    gaps = set(verified["gapTaskIds"])
    public_coverage = {k: v for k, v in verified.items() if k != "receipts"}
    public_coverage["sources"] = inventory(contract, now, verified)
    public_coverage["automationEnabled"] = contract["publication"]["enabled"]
    public_coverage["overdueHours"] = contract["schedule"]["overdueHours"]
    public_coverage["scheduledAt"] = plan["scheduledAt"]
    public_coverage["lastCollectionAt"] = max(r["completedAt"] for r in verified["receipts"])
    observed_at = []
    for receipt in verified["receipts"]:
        for oid in receipt.get("observationIds", []):
            observed = store.read(f"observations/{oid}.json")
            if observed and observed["status"] in ("fetched", "not_modified", "retained_immutable"):
                observed_at.append(instant(observed.get("verifiedAt", observed["fetchedAt"])))
    public_coverage["validUntil"] = (min(observed_at) + timedelta(hours=contract["schedule"]["overdueHours"])).isoformat() if observed_at else None
    public_coverage["suppliers"] = [{"id": sid, "name": supplier["name"], "required": len(tasks_by_supplier[sid]),
                                      "checked": sum(t not in gaps for t in tasks_by_supplier[sid]),
                                      "complete": not any(t in gaps for t in tasks_by_supplier[sid])}
                                     for sid, supplier in suppliers.items()]
    public_coverage["categories"] = {s["id"]: [{"category": category, "state": "source_checks_complete" if not any(t in gaps for t in tasks_by_supplier[s["id"]]) else "incomplete", "claimAssurance": "displayed facts retain their own source and date"} for category in s["requiredCategories"]] for s in contract["suppliers"]}
    result = {"schemaVersion": 1, "enabled": True, "runId": verified["runId"], "checkedAt": now,
              "contractSha256": digest(contract), "supplierUpdates": updates, "supplierUpdateDates": update_dates,
              "events": sorted(events.values(), key=lambda e: (e["date"], e["id"])), "evidence": list(evidence.values()),
              "coverage": public_coverage, "reviewQueue": list({(q["factId"], q["reason"]): q for q in queue}.values()), "secRecords": sec_records,
              "parentSnapshotSha256": digest(previous) if previous else None}
    return {**result, "snapshotSha256": digest(result)}
