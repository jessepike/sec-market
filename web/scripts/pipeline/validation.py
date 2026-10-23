"""Fail-closed cross-record evidence and coverage checks independent of models."""
import re
from datetime import datetime, timezone
from decimal import Decimal
from urllib.parse import urlsplit

from contracts import canonical, digest, instant, require, unique
from discovery import Page, decoded_discovery_body


PREDICATES = {"funding", "valuation", "revenue", "arr", "acquisition", "leadership_change", "restructuring", "layoff", "debt", "shutdown", "late_filing"}
REVIEW_CHECKS = {"entity", "value", "currency_units", "period_date", "qualifiers", "event_status", "source_support"}


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def mentions_entity(text, supplier):
    return any(re.search(r"\b" + re.escape(a) + r"\b", text, re.I) for a in [supplier["name"], *supplier.get("aliases", [])] if a)


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
    page = Page(raw, source_url=observation.get('finalUrl') or observation['requestedUrl']) if "html" in observation.get("contentType", "") else None
    text = page.readable if page else normalize(raw)
    quote, statement = normalize(candidate["quote"]), normalize(candidate["valueText"])
    require(len(quote) >= 20 and len(quote) <= 6000 and quote in text, "Exact source excerpt missing")
    require(len(statement) >= 15 and statement in quote, "Published statement must be supported verbatim")
    aliases = [supplier["name"], *supplier.get("aliases", [])]
    require(any(re.search(r"\b" + re.escape(a) + r"\b", text, re.I) for a in aliases if a), "Source entity not established")
    require(re.fullmatch(r"\d{4}-\d{2}-\d{2}", candidate["effectiveDate"] or "") is not None, "Fact date missing")
    require(candidate["effectiveDate"] <= observation["fetchedAt"][:10], "Future effective date requires review")
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
    sources = {s["id"]: s for s in contract["sources"]}
    require(suppliers == set(plan["supplierIds"]), "Supplier denominator changed")
    for receipt in receipts:
        task = expected[receipt["taskId"]]
        source = sources.get(task["sourceId"])
        if source and source["kind"] == "sec_index":
            require(all(receipt.get(key, []) == [] for key in
                        ("validatedFacts", "newFactIds", "documentValidations", "heldClaims", "documents")),
                    "Neutral SEC index receipt contains facts or semantic document work")
        require(receipt["runId"] == plan["runId"] and receipt["sourceId"] == task["sourceId"], "Receipt provenance mismatch")
        age = (instant(now) - instant(receipt["completedAt"])).total_seconds() / 3600
        require(age >= -5/60, "Future check timestamp")
        ok = receipt["outcome"] in ("updated", "checked_no_change") and receipt.get("discoveryComplete") is True and bool(receipt.get("observationIds")) and age <= contract["schedule"]["overdueHours"]
        if ok:
            require(source and source["registration"] == "verified", "Unverified source cannot earn coverage")
            unique(receipt["observationIds"], "observation reference")
            observations = []
            for oid in receipt["observationIds"]:
                observation = store.read(f"observations/{oid}.json")
                require(observation is not None and observation["sourceId"] == source["id"], "Observation missing or wrong source")
                require(observation["status"] in ("fetched", "not_modified", "retained_immutable"), "Failed fetch cannot earn successful coverage")
                require(urlsplit(observation["requestedUrl"]).hostname in source["allowedHosts"], "Observation outside contracted host")
                observed_age = (instant(now) - instant(observation.get("verifiedAt", observation["fetchedAt"]))).total_seconds() / 3600
                require(-5/60 <= observed_age <= contract["schedule"]["overdueHours"], "Stale/future source observation")
                store.get(observation["body"])
                if observation["status"] == "not_modified":
                    prior = store.read(f"observations/{observation.get('reusesObservationId')}.json")
                    require(prior and prior["requestedUrl"] == observation["requestedUrl"] and prior["sourceId"] == source["id"] and prior["body"] == observation["body"], "Invalid 304 retained-body chain")
                if observation["status"] == "retained_immutable":
                    require(source["kind"] == "sec_documents", "Only contracted SEC accession documents may be retained immutable")
                    prior = store.read(f"observations/{observation.get('reusesObservationId')}.json")
                    require(prior and prior["requestedUrl"] == observation["requestedUrl"] and prior["body"] == observation["body"] and prior["sourceId"] == source["id"], "Immutable document provenance differs")
                    prefix = f"https://www.sec.gov/Archives/edgar/data/{int(source['cik'])}/"
                    require(observation["requestedUrl"].startswith(prefix), "Wrong immutable filing CIK")
                    anchored = False
                    for aid in observation.get("anchorObservationIds", []):
                        require(aid in receipt["observationIds"], "SEC anchor is outside this run")
                        anchor = store.read(f"observations/{aid}.json")
                        require(anchor and anchor["sourceId"] == source["id"] and anchor["status"] in ("fetched", "not_modified"), "SEC anchor was not checked")
                        value = __import__('json').loads(store.get(anchor["body"]))
                        recent = value.get("filings", {}).get("recent", value)
                        for accession, document in zip(recent.get("accessionNumber", []), recent.get("primaryDocument", [])):
                            if prefix + accession.replace('-', '') + '/' + document == observation["requestedUrl"]:
                                anchored = True
                    require(anchored, "Retained filing absent from current SEC index")
                observations.append(observation)
            manifest = __import__('json').loads(store.get(receipt["itemManifest"]))
            require(manifest["sourceId"] == source["id"] and set(manifest["observations"]).issubset(receipt["observationIds"]), "Discovery manifest provenance mismatch")
            if source["kind"] == "sec_index":
                from regulatory import validate_index_source, verify_index_documents
                validate_index_source(source, contract["suppliers"])
                record = __import__('json').loads(store.get(receipt["regulatoryIndexValidation"]))
                require(set(record) == {"sourceId", "supplierId", "contractSha256", "traversalAsOf", "checkedAt", "observationIds", "documents", "verification"},
                        "Neutral SEC index validation record schema differs")
                require(record["sourceId"] == source["id"] and record["supplierId"] == task["supplierId"] and
                        record["contractSha256"] == digest(contract) and record["observationIds"] == receipt["observationIds"] and
                        manifest["observations"] == receipt["observationIds"], "Neutral SEC index validation provenance differs")
                require(instant(receipt["startedAt"]) <= instant(record["traversalAsOf"]) <= instant(record["checkedAt"]) <= instant(receipt["completedAt"]),
                        "Neutral SEC index check time is outside its attempt")
                require(instant(record["traversalAsOf"]).astimezone(timezone.utc).date() == instant(record["checkedAt"]).astimezone(timezone.utc).date(),
                        "Neutral SEC index traversal window changed")
                require(all(instant(o["fetchedAt"]) <= instant(record["checkedAt"]) for o in observations),
                        "Neutral SEC index validation precedes source observation")
                require(all(o.get("finalUrl", o["requestedUrl"]) == o["requestedUrl"] for o in observations),
                        "Neutral SEC index final response URL differs")
                bindings = [{"url": o["requestedUrl"], "observationId": o["observationId"], "body": o["body"]} for o in observations]
                require(record["documents"] == bindings, "Neutral SEC index document URL/body binding differs")
                documents = [{"url": o["requestedUrl"], "document": __import__('json').loads(decoded_discovery_body(store.get(o["body"])))}
                             for o in observations]
                checked = verify_index_documents(source, documents, record["checkedAt"])
                require(checked == record["verification"] and checked["facts"] == [], "Neutral SEC index independent replay differs")
                accessions = set()
                for item in documents:
                    table = item["document"].get("filings", {}).get("recent", item["document"])
                    accessions.update(accession for accession, day in zip(table["accessionNumber"], table["filingDate"])
                                      if checked["windowStart"] <= day <= checked["windowEnd"])
                require(type(manifest["items"]) is list and all(isinstance(item, str) and re.fullmatch(r"\d{10}-\d{2}-\d{6}", item)
                                                              for item in manifest["items"]),
                        "Neutral SEC index accession inventory must be an array of accession strings")
                unique(manifest["items"], "neutral SEC index accession")
                require(set(manifest["items"]) == accessions, "Neutral SEC index accession inventory differs")
            if source["kind"] not in ("sec_facts", "sec_submissions", "sec_index"):
                require(set(manifest["items"]).issubset({o["requestedUrl"] for o in observations}), "Discovered item was never checked")
            if source["kind"] == "sec_documents":
                require(set(manifest["items"]) == {d["url"] for d in receipt.get("documents", [])}, "SEC primary text inventory incomplete")
                for document in receipt.get("documents", []):
                    store.get(document["body"])
                    require(len(store.get(document["text"])) >= 100, "SEC document text missing")
            if source["kind"] not in ("sec_facts", "sec_submissions", "sec_documents", "sec_index", "citation"):
                validations = receipt.get("documentValidations", [])
                unique([d["url"] for d in validations], "document validation")
                require(set(manifest["items"]) == {d["url"] for d in validations}, "Document semantic validation inventory incomplete")
                current = {o["requestedUrl"]: o for o in observations}
                fact_hashes = {r["sha256"] for r in receipt.get("validatedFacts", [])}
                for document in validations:
                    validation = __import__('json').loads(store.get(document["validation"]))
                    observation = current[document["url"]]
                    require(validation["body"] == observation["body"] and validation["contractSha256"] == digest(contract) and validation["supplierId"] == task["supplierId"], "Document semantic validation covers different evidence/policy/entity")
                    refs = validation["factRefs"]
                    require(all(r["sha256"] in fact_hashes for r in refs), "Validated document facts missing from receipt")
                    hashes = [__import__('json').loads(store.get(r))["candidateSha256"] for r in refs]
                    held_hashes = {r["sha256"] for r in receipt.get("heldClaims", [])}
                    for ref in validation.get("heldClaims", []):
                        require(ref["sha256"] in held_hashes, "Unresolved claim missing from review queue")
                        held = __import__('json').loads(store.get(ref))
                        require(held["supplierId"] == task["supplierId"] and held["policySha256"] == digest(contract) and held["evidence"] == observation["body"], "Unresolved claim provenance differs")
                        require(held["candidateSha256"] == digest(held["candidate"]), "Unresolved candidate hash differs")
                        store.get(held["review"])
                        hashes.append(held["candidateSha256"])
                    require(sorted(hashes) == sorted(validation["candidateHashes"]), "Document candidate inventory differs")
                    if not validation["candidateHashes"]:
                        text = Page(store.get(observation["body"]).decode('utf8', errors='replace'), source_url=observation.get('finalUrl') or observation['requestedUrl']).readable
                        if validation.get("exclusionRule") == "no-registered-entity-mention-v1":
                            supplier = next(s for s in contract["suppliers"] if s["id"] == task["supplierId"])
                            require(source["family"] in ("investor_acquirer", "release_distribution") and len(text) >= 100 and not mentions_entity(text, supplier), "Invalid shared-publisher entity exclusion")
                        else:
                            review = __import__('json').loads(store.get(validation["emptyReview"]))
                            require(review.get("noRelevantFacts") is True and review.get("evidenceSha256") == observation["body"]["sha256"] and review.get("policySha256") == digest(contract), "Empty document review missing or mismatched")
                            require(not re.search(r"\b(funding|raised|acquisition|appointed|restructuring|layoffs|ARR|revenue|debt|shutdown)\b", text, re.I), "Empty extraction hides a business signal")
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


def verified_partial_document_facts(plan, coverage, contract, now, store):
    """Release a completed document's facts while another document remains queued.

This earns no source coverage and never advances the source cursor. A crashed
extraction without its complete document validation receipt remains ineligible.
"""
    require(plan["contractSha256"] == digest(contract), "Partial-document policy differs")
    sources = {s["id"]: s for s in contract["sources"]}
    suppliers = {s["id"]: s for s in contract["suppliers"]}
    tasks = {t["taskId"]: t for t in plan["tasks"]}
    accepted = {}
    for receipt in coverage["receipts"]:
        if receipt["outcome"] in ("updated", "checked_no_change") or not receipt.get("discoveryComplete"):
            continue
        task = tasks[receipt["taskId"]]
        source = sources.get(task["sourceId"])
        require(receipt["runId"] == plan["runId"] and receipt["sourceId"] == task["sourceId"], "Partial-document run/source differs")
        if not source or source["registration"] != "verified":
            continue
        if source["kind"] == "sec_index":
            require(all(receipt.get(key, []) == [] for key in
                        ("validatedFacts", "newFactIds", "documentValidations", "heldClaims", "documents")),
                    "Neutral SEC index cannot release partial semantic facts")
            continue
        manifest = __import__('json').loads(store.get(receipt["itemManifest"]))
        require(manifest["sourceId"] == source["id"], "Partial discovery manifest differs")
        observations = [store.read(f"observations/{oid}.json") for oid in receipt["observationIds"]]
        current = {o["requestedUrl"]: o for o in observations if o}
        receipt_refs = {ref["sha256"] for ref in receipt.get("validatedFacts", [])}
        for document in receipt.get("documentValidations", []):
            require(document["url"] in manifest["items"], "Partial document is outside discovery inventory")
            observation = current.get(document["url"])
            require(observation and observation["sourceId"] == source["id"] and observation["status"] in ("fetched", "not_modified"), "Partial document lacks a successful source check")
            require(urlsplit(document["url"]).hostname in source["allowedHosts"], "Partial document outside source host")
            age = (instant(now)-instant(observation["fetchedAt"])).total_seconds()/3600
            require(-5/60 <= age <= contract["schedule"]["overdueHours"], "Partial document check is stale/future")
            store.get(observation["body"])
            if observation["status"] == "not_modified":
                old = store.read(f"observations/{observation.get('reusesObservationId')}.json")
                require(old and old["body"] == observation["body"] and old["requestedUrl"] == document["url"] and old["sourceId"] == source["id"], "Partial document 304 chain differs")
            validation = __import__('json').loads(store.get(document["validation"]))
            require(validation["supplierId"] == task["supplierId"] and validation["body"] == observation["body"] and validation["contractSha256"] == digest(contract), "Partial-document semantic receipt differs")
            for reference in validation["factRefs"]:
                require(reference["sha256"] in receipt_refs, "Partial fact missing from task receipt")
                fact = __import__('json').loads(store.get(reference))
                original = store.read(f"observations/{fact['sourceObservationId']}.json")
                require(original and original["body"] == observation["body"], "Partial fact covers different source bytes")
                review = __import__('json').loads(store.get(fact["review"]))
                candidate = {k: fact[k] for k in ("supplierId", "predicate", "valueText", "quote", "effectiveDate", "amount", "currency", "qualifier", "eventStatus", "scope")}
                require(digest(candidate) in validation["candidateHashes"], "Partial candidate missing from validated inventory")
                checked = verify_statement(candidate, original, store, review, suppliers[task["supplierId"]], digest(contract))
                require(checked["factId"] == fact["factId"], "Partial fact identity differs")
                accepted[reference["sha256"]] = reference
    return list(accepted.values())
