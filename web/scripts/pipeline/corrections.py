"""Hash-bound factual correction admission. No fetching or quota bypasses.

API: load_policy(repo, market), validate_baseline(inventories, baseline),
process_corrections(repo, store, market, agent, reserve, now, cancelled=None),
project_bundle(repo, store, market, outcome, previous_bundle=None, publication_at=None).
Only SubscriptionAgent reviews admit changes. A test agent with synthetic=True writes
non-admitting attempts, never an admission cache usable by the publication gate.
"""
import copy
import json
import re
import uuid
from datetime import timezone
from pathlib import Path
from urllib.parse import urlsplit

from agents import SubscriptionAgent
from contracts import canonical, digest, instant, require, unique, utcnow, valid_hash
from discovery import Page
from validation import REVIEW_CHECKS

ORIGINALS = "web/src/data/tracker/originals.json"
BASELINE = "contracts/factual-baseline.json"
REQUESTS = "contracts/factual-corrections.json"
INVENTORIES = {"suppliers", "events", "evidence"}
SUPPLIER_FIELDS = {
    "lastRound": ({"date", "stage", "amount", "evidenceIds"}, {"lead", "valuation"}),
    "headlineMetric": ({"label", "value", "period", "evidenceIds"}, set()),
    "ownership": ({"status", "evidenceIds"}, {"acquirer", "announced", "closed", "price", "relationship"}),
}
EVIDENCE_MUTABLE = {"title", "publicationDate", "economicPeriod", "excerpt", "limitations"}


def _keys(value, expected, label):
    require(isinstance(value, dict) and set(value) == set(expected), label + " schema mismatch")


def _time(value):
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value), "Correction timestamp must be UTC Z")
    return instant(value).astimezone(timezone.utc)


def _reference(ref):
    _keys(ref, {"key", "sha256", "bytes"}, "Correction object reference")
    require(valid_hash(ref["sha256"]) and ref["key"] == "objects/" + ref["sha256"]
            and type(ref["bytes"]) is int and ref["bytes"] > 0, "Invalid content-addressed correction reference")


def validate_baseline(inventories, baseline):
    """Compare the whole raw inventories, including untouched records and IDs."""
    _keys(baseline, {"schemaVersion", "inventories"}, "Correction baseline")
    require(type(baseline["schemaVersion"]) is int and baseline["schemaVersion"] == 1, "Unsupported correction baseline")
    _keys(inventories, INVENTORIES, "Raw correction inventories")
    _keys(baseline["inventories"], INVENTORIES, "Baseline inventories")
    for name in sorted(INVENTORIES):
        rows = inventories[name]
        require(isinstance(rows, list) and all(isinstance(row, dict) and isinstance(row.get("id"), str) and row["id"] for row in rows), "Invalid raw inventory: " + name)
        unique([row["id"] for row in rows], "raw " + name)
        expected = baseline["inventories"][name]
        require(isinstance(expected, dict) and all(valid_hash(v) for v in expected.values()), "Invalid baseline digests")
        require({row["id"]: digest(row) for row in rows} == expected, "Immutable original inventory changed: " + name)
    return inventories


def _read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate JSON property: " + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_bytes(), object_pairs_hook=pairs,
                      parse_constant=lambda _: require(False, "Non-finite correction value"))


def _inventories(repo):
    return _read_json(Path(repo) / ORIGINALS)


def _maps(inventories):
    return {name: {row["id"]: row for row in inventories[name]} for name in INVENTORIES}


def _target(target, group, records):
    _keys(target, {"targetId", "operation", "original", "originalSha256", "proposedValue"}, "Correction target")
    require(valid_hash(target["originalSha256"]) and target["originalSha256"] == digest(target["original"]), "Correction before hash differs")
    require(target["operation"] in ("replace", "withdraw"), "Unknown correction operation")
    require(isinstance(target["targetId"], str) and target["targetId"], "Invalid correction target ID")
    parts = target["targetId"].split(":")
    original, proposed = target["original"], target["proposedValue"]
    if parts[0] == "supplier" and len(parts) == 3:
        _, supplier_id, field = parts
        require(supplier_id == group["supplierId"] and field in SUPPLIER_FIELDS, "Disallowed supplier correction field")
        supplier = records["suppliers"].get(supplier_id, {})
        require(field in supplier and canonical(original) == canonical(supplier[field]), "Supplier before value differs")
        require(target["operation"] == "replace" and isinstance(proposed, dict), "Supplier withdrawal prohibited")
        required, optional = SUPPLIER_FIELDS[field]
        require(required.issubset(proposed) and set(proposed).issubset(required | optional), "Supplier field value schema mismatch")
        require(all(isinstance(value, str) and value.strip() for key, value in proposed.items() if key != "evidenceIds"), "Invalid supplier field value")
    elif parts[0] in ("event", "evidence") and len(parts) == 2:
        name = "events" if parts[0] == "event" else "evidence"
        require(parts[1] in records[name] and canonical(original) == canonical(records[name][parts[1]]), "Record before value differs")
        require(isinstance(original, dict) and original.get("id") == parts[1], "Original correction identity differs")
        if name == "events":
            require(original.get("supplierId") == group["supplierId"], "Correction event supplier differs")
            if target["operation"] == "withdraw":
                require(proposed is None, "Withdrawal requires null proposed value")
                return
            require(isinstance(proposed, dict) and set(proposed) == set(original), "Event replacement schema differs")
            require(all(proposed[key] == original[key] for key in ("id", "supplierId", "type", "rung")), "Protected event identity changed")
            require(isinstance(proposed.get("text"), str) and bool(proposed["text"].strip()), "Empty corrected event")
            require(isinstance(proposed.get("date"), str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", proposed["date"]), "Invalid corrected event date")
            _time(proposed["date"] + "T00:00:00Z")
        else:
            require(target["operation"] == "replace" and isinstance(proposed, dict), "Evidence withdrawal prohibited")
            require(set(proposed) == set(original), "Evidence replacement schema differs")
            require(all(proposed[key] == value for key, value in original.items() if key not in EVIDENCE_MUTABLE), "Protected evidence metadata changed")
            require(all(isinstance(proposed.get(key), str) and proposed[key].strip() for key in EVIDENCE_MUTABLE), "Invalid corrected evidence metadata")
            return
    else:
        require(False, "Invalid correction target ID")
    require(isinstance(proposed.get("evidenceIds"), list) and proposed["evidenceIds"] and all(isinstance(e, str) and e in records["evidence"] for e in proposed["evidenceIds"]), "Corrected citation absent from original evidence inventory")
    unique(proposed["evidenceIds"], "corrected citations")


def load_policy(repo, market):
    requests = _read_json(Path(repo) / REQUESTS)
    _keys(requests, {"schemaVersion", "version", "baseline", "groups"}, "Correction requests")
    require(type(requests["schemaVersion"]) is int and requests["schemaVersion"] == 1 and isinstance(requests["version"], str) and requests["version"], "Invalid correction requests version")
    pin = requests["baseline"]
    _keys(pin, {"path", "sha256"}, "Correction baseline pin")
    require(pin["path"] == BASELINE and valid_hash(pin["sha256"]), "Unexpected correction baseline pin")
    raw = (Path(repo) / BASELINE).read_bytes()
    require(digest(raw) == pin["sha256"], "Correction baseline pin mismatch")
    baseline = _read_json(Path(repo) / BASELINE)
    inventories = validate_baseline(_inventories(repo), baseline)
    records = _maps(inventories)
    require(isinstance(requests["groups"], list) and requests["groups"], "Correction request groups missing")
    group_ids, target_ids = [], []
    for group in requests["groups"]:
        _keys(group, {"id", "supplierId", "reasonCode", "noteTemplate", "targets", "sources"}, "Correction group")
        require(all(isinstance(group[key], str) and group[key].strip() for key in ("id", "supplierId", "reasonCode", "noteTemplate")), "Empty correction group metadata")
        require(group["supplierId"] in records["suppliers"] and group["supplierId"] in {s["id"] for s in market["suppliers"]}, "Unknown correction supplier")
        require(group["noteTemplate"].count("{date}") == 1 and not re.search(r"[{}]", group["noteTemplate"].replace("{date}", "")), "Correction note needs one date placeholder")
        require(isinstance(group["targets"], list) and group["targets"] and isinstance(group["sources"], list) and group["sources"], "Incomplete correction group")
        group_ids.append(group["id"])
        for target in group["targets"]:
            _target(target, group, records)
            target_ids.append(target["targetId"])
        evidence_ids = []
        source_ids = {s["id"]: s for s in market["sources"]}
        for source in group["sources"]:
            _keys(source, {"evidenceId", "sourceId", "url", "observationId", "body", "fetchedAt"}, "Correction source")
            require(all(isinstance(source[key], str) and source[key] for key in ("evidenceId", "sourceId", "url")), "Invalid correction source binding")
            evidence = records["evidence"].get(source["evidenceId"])
            configured = source_ids.get(source["sourceId"])
            require(evidence and evidence.get("sourceClass") in ("IR", "FILING", "OFFICIAL"), "Correction requires primary organization evidence")
            require(configured and configured["supplierId"] == group["supplierId"] and configured["registration"] == "verified", "Correction source binding unverified")
            require(source["sourceId"] in next(s for s in market["suppliers"] if s["id"] == group["supplierId"])["sourceIds"], "Correction source not configured for supplier")
            url = urlsplit(source["url"])
            require(source["url"] == evidence["canonicalUrl"] and url.scheme == "https" and not url.username and not url.password and url.port in (None, 443) and url.hostname in configured["allowedHosts"], "Correction canonical source URL differs")
            if configured["kind"] == "citation":
                require(configured["url"] == source["url"], "Correction configured citation URL differs")
            require(isinstance(evidence.get("organization"), str) and evidence["organization"].strip(), "Correction source organization missing")
            require(valid_hash(source["observationId"]), "Invalid correction observation ID")
            _reference(source["body"])
            _time(source["fetchedAt"])
            evidence_ids.append(source["evidenceId"])
        unique(evidence_ids, "correction evidence source")
        required_evidence = set()
        for target in group["targets"]:
            if target["targetId"].startswith("evidence:"):
                required_evidence.add(target["original"]["id"])
            else:
                required_evidence.update(target["original"].get("evidenceIds", []))
                if target["proposedValue"] is not None:
                    required_evidence.update(target["proposedValue"].get("evidenceIds", []))
        require(required_evidence.issubset(evidence_ids), "Correction group source inventory incomplete")
    unique(group_ids, "correction group ID")
    unique(target_ids, "correction target ID")
    policy = digest({"marketSha256": digest(market), "requestsSha256": digest(requests), "baselineSha256": pin["sha256"]})
    stamp = _read_json(Path(repo) / "web/src/data/tracker/factualCorrectionPolicy.json")
    source_ids = {group["id"]: [source["evidenceId"] for source in group["sources"]] for group in requests["groups"]}
    require(type(stamp.get("schemaVersion")) is int and stamp == {"schemaVersion": 1, "policySha256": policy, "groupIds": group_ids, "targetIds": target_ids, "sourceEvidenceIds": source_ids},
            "Correction build policy manifest differs")
    return {"requests": requests, "baseline": baseline, "policySha256": policy}


def _normalize(value):
    # Page already decodes HTML entities once. Decoding again would let a
    # double-escaped source support characters absent from its displayed text.
    return re.sub(r"\s+", " ", value).strip()


def validate_sources(group, store, market, admitted_at):
    """Replay exact source/observation joins and freshness at initial admission."""
    documents = []
    at = _time(admitted_at)
    for source in group["sources"]:
        observation = store.read("observations/" + source["observationId"] + ".json")
        require(observation and observation.get("observationId") == source["observationId"] and observation.get("sourceId") == source["sourceId"], "Correction observation/source differs")
        require(observation.get("status") in ("fetched", "not_modified"), "Correction source observation unsuccessful")
        require(observation.get("requestedUrl") == source["url"] and observation.get("finalUrl", source["url"]) == source["url"], "Correction observation URL differs")
        require(observation.get("body") == source["body"] and observation.get("fetchedAt") == source["fetchedAt"], "Correction observation body or time differs")
        if observation.get("verifiedAt"):
            require(_time(observation["verifiedAt"]) <= at, "Correction observation verification after admission")
        age = (at - _time(source["fetchedAt"])).total_seconds()
        require(0 <= age <= 30 * 3600, "Correction source expired or future at admission")
        raw = store.get(source["body"]).decode("utf8", errors="strict")
        page = Page(raw, source_url=source["url"])
        # Whole decoded source text is retained. No excerpt-only or silent truncation.
        text = _normalize(" ".join(page.text))
        require(len(text) >= 100 and len(text) <= market["model"]["maxDocumentChars"], "Correction primary document exceeds limit or is unreadable")
        require(not re.search(r"access denied|verify you are human|request rate threshold exceeded", text[:2000], re.I), "Correction source block page")
        documents.append({"source": source, "text": text})
    for target in group["targets"]:
        if target["targetId"].startswith("evidence:"):
            evidence = target["proposedValue"]
            texts = [d["text"] for d in documents if d["source"]["evidenceId"] == evidence["id"]]
            require(any(_normalize(evidence["excerpt"]) in text for text in texts), "Correction evidence excerpt not literally in primary source")
    return documents


def _review(review, group, policy_hash):
    _keys(review, {"result", "candidateSha256", "evidenceSetSha256", "policySha256", "checks"}, "Correction review")
    require(review["candidateSha256"] == digest(group), "Correction review candidate hash differs")
    require(review["evidenceSetSha256"] == digest(group["sources"]), "Correction review evidence set hash differs")
    require(review["policySha256"] == policy_hash, "Correction review policy hash differs")
    require(review["result"] == "accepted", "Correction independent review did not accept")
    require(isinstance(review["checks"], dict) and set(review["checks"]) == REVIEW_CHECKS and all(v == "pass" for v in review["checks"].values()), "Correction independent review checks incomplete")


def _index(group, policy):
    return "correction-admissions/" + policy + "/" + digest(group) + "-" + digest(group["sources"]) + ".json"


def replay_admission(group, reference, store, market, policy_hash, checked_at=None):
    _reference(reference)
    admission = json.loads(store.get(reference))
    _keys(admission, {"groupId", "candidateSha256", "evidenceSetSha256", "policySha256", "admittedAt", "review", "sources"}, "Correction admission")
    require(admission["groupId"] == group["id"] and admission["candidateSha256"] == digest(group)
            and admission["evidenceSetSha256"] == digest(group["sources"]) and admission["policySha256"] == policy_hash
            and admission["sources"] == group["sources"], "Correction admission binding differs")
    _time(admission["admittedAt"])
    if checked_at:
        require(_time(admission["admittedAt"]) <= _time(checked_at), "Correction admission after gate time")
    validate_sources(group, store, market, admission["admittedAt"])
    _reference(admission["review"])
    _review(json.loads(store.get(admission["review"])), group, policy_hash)
    indexed = store.read(_index(group, policy_hash))
    require(indexed == {"groupId": group["id"], "admission": reference}, "Correction admission missing immutable accepted index")
    return admission


def process_corrections(repo, store, market, agent, reserve, now, cancelled=None, clock=None):
    clock = clock or utcnow
    context = load_policy(repo, market)
    policy = context["policySha256"]
    _time(now)
    result = {"policySha256": policy, "admitted": [], "pending": [], "attempts": []}
    for group in context["requests"]["groups"]:
        cached = store.read(_index(group, policy))
        if cached:
            try:
                replay_admission(group, cached["admission"], store, market, policy, now)
                result["admitted"].append(cached)
                continue
            except (ValueError, OSError, KeyError, TypeError) as exc:
                result["pending"].append({"groupId": group["id"], "reason": str(exc)[:240]})
                continue
        attempt = {"groupId": group["id"], "candidateSha256": digest(group), "evidenceSetSha256": digest(group["sources"]),
                   "policySha256": policy, "startedAt": now, "sources": copy.deepcopy(group["sources"]),
                   "nonce": uuid.uuid4().hex, "review": None, "outcome": "pending", "error": None}
        try:
            require(not cancelled or not cancelled(), "CORRECTION_CANCELLED_OR_DEADLINE")
            documents = validate_sources(group, store, market, now)
            require(isinstance(agent, SubscriptionAgent) and callable(reserve), "CORRECTION_SUBSCRIPTION_REVIEW_REQUIRED")
            require(not getattr(agent, "synthetic", False), "SYNTHETIC_CORRECTION_REVIEW_NON_ADMITTING")
            agent.reserve = reserve
            reservation = "correction-document-reservations/" + now[:10] + "/" + digest({"group": group, "policy": policy}) + ".json"
            if not store.read(reservation):
                reserve("documents", market["model"]["maxDocumentsPerRun"])
                store.write_once(reservation, {"groupId": group["id"], "candidateSha256": digest(group), "reservedAt": now})
            require(not cancelled or not cancelled(), "CORRECTION_CANCELLED_OR_DEADLINE")
            response = agent.review_correction(documents, group, policy)
            attempt["review"] = store.put(response)
            _review(response, group, policy)
            admitted_at = clock()
            require(_time(admitted_at) >= _time(now), "Correction admission completion precedes attempt")
            require(not cancelled or not cancelled(), "CORRECTION_CANCELLED_OR_DEADLINE")
            validate_sources(group, store, market, admitted_at)
            admission = {"groupId": group["id"], "candidateSha256": digest(group), "evidenceSetSha256": digest(group["sources"]),
                         "policySha256": policy, "admittedAt": admitted_at, "review": attempt["review"], "sources": copy.deepcopy(group["sources"])}
            entry = {"groupId": group["id"], "admission": store.put(admission)}
            store.write_once(_index(group, policy), entry)
            result["admitted"].append(entry)
            attempt["outcome"] = "accepted"
        except BaseException as exc:
            attempt["error"] = str(exc)[:240]
            result["pending"].append({"groupId": group["id"], "reason": attempt["error"]})
            if not isinstance(exc, Exception):
                raise
        finally:
            attempt["completedAt"] = clock()
            _time(attempt["completedAt"])
            reference = store.put(attempt)
            store.write_once("correction-attempts/" + reference["sha256"] + ".json", reference)
            result["attempts"].append(reference)
    return result


def project_bundle(repo, store, market, outcome, previous_bundle=None, publication_at=None):
    """Require every request and replay accepted immutable evidence without a model."""
    context = load_policy(repo, market)
    policy, groups = context["policySha256"], context["requests"]["groups"]
    _time(publication_at)
    require(isinstance(outcome, dict) and outcome.get("policySha256") == policy and not outcome.get("pending"), "Correction admissions pending or policy changed")
    entries = outcome.get("admitted", [])
    require(isinstance(entries, list) and len(entries) == len(groups), "Correction admission inventory incomplete")
    for entry in entries:
        _keys(entry, {"groupId", "admission"}, "Correction admitted entry")
        require(isinstance(entry["groupId"], str), "Invalid admitted correction group")
    unique([e["groupId"] for e in entries], "admitted correction group")
    require({e["groupId"] for e in entries} == {g["id"] for g in groups}, "Correction admission group manifest differs")
    old = {}
    if previous_bundle is not None:
        _keys(previous_bundle, {"schemaVersion", "enabled", "policySha256", "checkedAt", "groups"}, "Previous correction bundle")
        require(type(previous_bundle["schemaVersion"]) is int and previous_bundle["schemaVersion"] == 1
                and type(previous_bundle["enabled"]) is bool, "Previous correction bundle schema differs")
        if not previous_bundle["enabled"]:
            require(previous_bundle == {"schemaVersion": 1, "enabled": False, "policySha256": None, "checkedAt": None, "groups": []},
                    "Disabled correction bundle must be empty")
    if previous_bundle and previous_bundle.get("enabled"):
        require(previous_bundle.get("policySha256") == policy, "Published correction policy changed")
        require(_time(previous_bundle["checkedAt"]) <= _time(publication_at), "Published correction check time is future")
        old = {g["id"]: g for g in previous_bundle["groups"]}
        require(len(old) == len(previous_bundle["groups"]) and set(old) == {g["id"] for g in groups}, "Published correction inventory changed")
    public = []
    for group in groups:
        entry = next(e for e in entries if e["groupId"] == group["id"])
        _keys(entry, {"groupId", "admission"}, "Correction admitted entry")
        admission = replay_admission(group, entry["admission"], store, market, policy, publication_at)
        metadata = {key: admission[key] for key in ("candidateSha256", "evidenceSetSha256", "policySha256", "admittedAt")}
        metadata.update(reviewSha256=admission["review"]["sha256"], result="accepted")
        day = old.get(group["id"], {}).get("date", publication_at[:10])
        _time(day + "T00:00:00Z")
        require(day <= publication_at[:10], "Correction publication date is future")
        row = {"id": group["id"], "supplierId": group["supplierId"], "reasonCode": group["reasonCode"], "date": day,
               "note": group["noteTemplate"].replace("{date}", day), "targets": copy.deepcopy(group["targets"]), "admission": metadata}
        require(group["id"] not in old or old[group["id"]] == row, "Historical correction changed")
        public.append(row)
    return {"schemaVersion": 1, "enabled": True, "policySha256": policy, "checkedAt": publication_at, "groups": public}
