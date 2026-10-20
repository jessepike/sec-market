"""Fail-closed cross-record evidence and coverage checks independent of models."""
import re
from datetime import datetime
from decimal import Decimal
from urllib.parse import urlsplit

from contracts import canonical, digest, instant, require, unique
from discovery import Page


PREDICATES = {"funding", "valuation", "revenue", "arr", "acquisition", "leadership_change", "restructuring", "layoff", "debt", "shutdown", "late_filing"}
REVIEW_CHECKS = {"entity", "value", "currency_units", "period_date", "qualifiers", "event_status", "source_support"}


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def numbers(text):
    result = set()
    for amount, unit in re.findall(r"(?<![\w.])([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)\s*(billion|million|thousand|bn|[bmk])?\b", text.lower()):
        factor = {"billion": 10**9, "bn": 10**9, "b": 10**9, "million": 10**6, "m": 10**6, "thousand": 1000, "k": 1000}.get(unit, 1)
        result.add(Decimal(amount.replace(",", "")) * factor)
    return result


def source_dates(text):
    values = set(re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text))
    for value in re.findall(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b", text, re.I):
        try:
            values.add(datetime.strptime(value.replace(",", ""), "%B %d %Y").date().isoformat())
        except ValueError:
            pass
    return values


def verify_statement(candidate, observation, store, review, supplier, policy_hash):
    required = {"supplierId", "predicate", "valueText", "quote", "effectiveDate", "amount", "currency", "qualifier", "eventStatus", "scope"}
    require(set(candidate) == required, "Candidate schema mismatch")
    require(candidate["supplierId"] == supplier["id"], "Candidate entity mismatch")
    require(candidate["predicate"] in PREDICATES, "Unsupported claim or judgment")
    require(candidate["scope"] in ("company", "segment", "brand"), "Missing company/segment scope")
    require(candidate["eventStatus"] in ("reported", "announced", "closed"), "Invalid event status")
    require(candidate["qualifier"] in ("exact", "approximately", "at_least", "more_than", "up_to"), "Missing numeric qualifier")
    require(observation["status"] in ("fetched", "not_modified"), "Unsuccessful source observation")
    raw = store.get(observation["body"]).decode("utf8")
    page = Page(raw) if "html" in observation.get("contentType", "") else None
    text = page.readable if page else normalize(raw)
    quote, statement = normalize(candidate["quote"]), normalize(candidate["valueText"])
    require(len(quote) >= 20 and len(quote) <= 6000 and quote in text, "Exact source excerpt missing")
    require(len(statement) >= 15 and statement in quote, "Published statement must be supported verbatim")
    aliases = [supplier["name"], *supplier.get("aliases", [])]
    require(any(re.search(r"\b" + re.escape(a) + r"\b", text, re.I) for a in aliases if a), "Source entity not established")
    require(re.fullmatch(r"\d{4}-\d{2}-\d{2}", candidate["effectiveDate"] or "") is not None, "Fact date missing")
    dates = source_dates(quote)
    metadata_date = page.published[:10] if page and page.published else None
    require(candidate["effectiveDate"] in dates or (not dates and candidate["effectiveDate"] == metadata_date), "Fact date not grounded in source")
    lowered = quote.lower()
    require(not re.search(r"\b(rumou?r|denied|not confirmed)\b", lowered), "Unresolved source claim")
    if candidate["amount"] is not None:
        require(candidate["currency"] in ("USD", "EUR", "GBP", "JPY", "CAD", "AUD"), "Currency missing or unsupported")
        require(Decimal(str(candidate["amount"])) in numbers(quote), "Source number does not match candidate")
        marker = {"USD": r"\$|USD|US dollars", "EUR": r"€|EUR|euros", "GBP": r"£|GBP|pounds", "JPY": r"¥|JPY|yen", "CAD": r"CAD|C\$", "AUD": r"AUD|A\$"}[candidate["currency"]]
        require(re.search(marker, quote, re.I) is not None, "Currency is not evidenced")
    if "up to" in lowered:
        require(candidate["qualifier"] == "up_to", "Dropped up-to qualifier")
    if re.search(r"\b(approximately|about|around)\b", lowered):
        require(candidate["qualifier"] != "exact", "Dropped approximation qualifier")
    if "at least" in lowered:
        require(candidate["qualifier"] == "at_least", "Dropped at-least qualifier")
    if re.search(r"\b(more than|over)\s+[$€£¥]?\d", lowered):
        require(candidate["qualifier"] == "more_than", "Dropped more-than qualifier")
    if "annual recurring revenue" in lowered or re.search(r"\bARR\b", quote):
        require(candidate["predicate"] != "revenue", "ARR is not revenue")
    if re.search(r"\b(will|plans to|expects to|proposed)\b", lowered):
        require(candidate["eventStatus"] != "closed", "Future/announced event labelled closed")
    require(review.get("candidateSha256") == digest(candidate), "Review does not cover exact candidate")
    require(review.get("evidenceSha256") == observation["body"]["sha256"], "Review evidence mismatch")
    require(review.get("policySha256") == policy_hash, "Review policy mismatch")
    checks = review.get("checks", {})
    require(set(checks) == REVIEW_CHECKS and all(v == "pass" for v in checks.values()), "Independent semantic review incomplete or disagrees")
    require(review.get("result") == "accepted", "Independent review did not accept")
    identity = {k: candidate[k] for k in ("supplierId", "predicate", "effectiveDate", "amount", "currency", "qualifier", "eventStatus", "scope")}
    if candidate["amount"] is None:
        identity["statement"] = statement.lower()
    return {"factId": digest(identity), **candidate, "evidence": [observation["body"]],
            "sourceObservationId": observation["observationId"], "candidateSha256": digest(candidate),
            "review": store.put(review),
            "assurance": "source_statement_matched", "policySha256": policy_hash}


def reconcile(plan, receipts, contract, now, store):
    require(plan["contractSha256"] == digest(contract), "Contract changed after planning")
    require(plan["inventorySha256"] == digest(plan["tasks"]), "Task inventory changed")
    unique([r["taskId"] for r in receipts], "final task receipt")
    expected = {t["taskId"]: t for t in plan["tasks"]}
    require(set(expected) == {r["taskId"] for r in receipts}, "Required inventory missing or unexpected receipt")
    successful, gaps = [], []
    suppliers = {s["id"] for s in contract["suppliers"]}
    require(suppliers == set(plan["supplierIds"]), "Supplier denominator changed")
    for receipt in receipts:
        task = expected[receipt["taskId"]]
        require(receipt["runId"] == plan["runId"] and receipt["sourceId"] == task["sourceId"], "Receipt provenance mismatch")
        age = (instant(now) - instant(receipt["completedAt"])).total_seconds() / 3600
        require(age >= -5/60, "Future check timestamp")
        ok = receipt["outcome"] in ("updated", "checked_no_change") and receipt.get("discoveryComplete") is True and bool(receipt.get("observationIds")) and age <= contract["schedule"]["overdueHours"]
        if ok:
            sources = {s["id"]: s for s in contract["sources"]}
            source = sources.get(task["sourceId"])
            require(source and source["registration"] == "verified", "Unverified source cannot earn coverage")
            unique(receipt["observationIds"], "observation reference")
            observations = []
            for oid in receipt["observationIds"]:
                observation = store.read(f"observations/{oid}.json")
                require(observation is not None and observation["sourceId"] == source["id"], "Observation missing or wrong source")
                require(observation["status"] in ("fetched", "not_modified"), "Failed fetch cannot earn successful coverage")
                require(urlsplit(observation["requestedUrl"]).hostname in source["allowedHosts"], "Observation outside contracted host")
                observed_age = (instant(now) - instant(observation["fetchedAt"])).total_seconds() / 3600
                require(-5/60 <= observed_age <= contract["schedule"]["overdueHours"], "Stale/future source observation")
                store.get(observation["body"])
                if observation["status"] == "not_modified":
                    prior = store.read(f"observations/{observation.get('reusesObservationId')}.json")
                    require(prior and prior["requestedUrl"] == observation["requestedUrl"] and prior["sourceId"] == source["id"] and prior["body"] == observation["body"], "Invalid 304 retained-body chain")
                observations.append(observation)
            manifest = __import__('json').loads(store.get(receipt["itemManifest"]))
            require(manifest["sourceId"] == source["id"] and set(manifest["observations"]).issubset(receipt["observationIds"]), "Discovery manifest provenance mismatch")
            if source["kind"] not in ("sec_facts", "sec_submissions"):
                require(set(manifest["items"]).issubset({o["requestedUrl"] for o in observations}), "Discovered item was never checked")
            for reference in receipt.get("validatedFacts", []):
                fact = __import__("json").loads(store.get(reference))
                require(fact["supplierId"] == task["supplierId"], "Validated fact has wrong entity")
                for reference in fact["evidence"]:
                    store.get(reference)
                if fact.get("review"):
                    review = __import__("json").loads(store.get(fact["review"]))
                    candidate = {k: fact[k] for k in ("supplierId", "predicate", "valueText", "quote", "effectiveDate", "amount", "currency", "qualifier", "eventStatus", "scope")}
                    observation = store.read(f"observations/{fact['sourceObservationId']}.json")
                    supplier = next(s for s in contract["suppliers"] if s["id"] == task["supplierId"])
                    checked = verify_statement(candidate, observation, store, review, supplier, digest(contract))
                    require(checked["factId"] == fact["factId"], "Stored fact identity changed")
        if receipt["outcome"] == "checked_no_change":
            require(not receipt.get("newFactIds"), "No-change receipt contains new facts")
        if receipt["outcome"] == "updated":
            require(bool(receipt.get("newFactIds")), "Updated receipt has no accepted facts")
        if task["required"]:
            (successful if ok else gaps).append(task["taskId"])
    required = sum(t["required"] for t in plan["tasks"])
    return {"schemaVersion": 1, "runId": plan["runId"], "contractSha256": plan["contractSha256"],
            "inventorySha256": plan["inventorySha256"], "checkedAt": now, "supplierCount": len(suppliers),
            "requiredTasks": required, "successfulTasks": len(successful), "gapTaskIds": gaps,
            "complete": required > 0 and len(successful) == required, "outcome": "complete" if not gaps else "degraded",
            "receipts": receipts}


def eligible_fact_references(coverage):
    """A partial task may archive candidates, but cannot release any of them."""
    by_hash = {}
    for receipt in coverage["receipts"]:
        if receipt["outcome"] in ("updated", "checked_no_change") and receipt["discoveryComplete"]:
            for ref in receipt.get("validatedFacts", []):
                by_hash[ref["sha256"]] = ref
    return list(by_hash.values())
