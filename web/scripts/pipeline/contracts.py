"""Reviewed coverage inventory and canonical hashing; no network or model calls."""
import hashlib
import json
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit


class ContractError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def utcnow():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def instant(value):
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.tzinfo is None:
            raise ValueError("Timezone required")
        return result
    except (ValueError, AttributeError) as exc:
        raise ContractError("Invalid timezone-aware timestamp") from exc


def require(condition, reason):
    if not condition:
        raise ContractError(reason)


def unique(items, label):
    require(len(items) == len(set(items)), f"Duplicate {label}")


def validate_contract(contract):
    require(contract.get("schemaVersion") == 1, "Unsupported contract schema")
    require(bool(contract.get("version")), "Contract version required")
    if "collection" in contract:
        policy = contract["collection"]
        require(policy.get("mode") in ("delta_with_retained_audit", "daily_intake_with_separate_history"), "Unsupported collection mode")
        for key in ("currentWindowDays", "maxDocumentsPerSource", "maxAuditDocumentsPerSource"):
            require(type(policy.get(key)) is int and policy[key] > 0, "Invalid collection bound: " + key)
        require(policy["maxAuditDocumentsPerSource"] <= policy["maxDocumentsPerSource"], "Audit exceeds source budget")
        if "historyWindowDays" in policy:
            require(policy["mode"] == "daily_intake_with_separate_history", "History window needs separated intake")
            require(type(policy["historyWindowDays"]) is int and policy["historyWindowDays"] > policy["currentWindowDays"],
                    "History window must be a whole number of days longer than the current window")
        if "maxFetchAuditDocumentsPerSource" in policy:
            require("historyWindowDays" in policy and type(policy["maxFetchAuditDocumentsPerSource"]) is int
                    and policy["maxFetchAuditDocumentsPerSource"] >= 0,
                    "Fetch audit allowance needs a history window and a whole number")
    schedule = contract["schedule"]
    require(schedule["intervalHours"] == 24 and schedule["reconcileEveryRun"] is True,
            "Every required daily run must reconcile coverage")
    require(24 < schedule["overdueHours"] <= 36, "Daily freshness threshold out of bounds")
    require(1 <= schedule["maxWorkers"] <= 16, "Unsafe worker parallelism")
    require(contract["model"]["provider"] == "codex_subscription", "Only approved subscription provider allowed")
    require(contract["model"]["allowApiBilling"] is False, "Paid API fallback is prohibited")
    if "extractModel" in contract["model"]:
        name = contract["model"]["extractModel"]
        require(type(name) is str and re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,63}", name) is not None, "Invalid first-pass model name")
    for key in ("maxDocumentsPerRun", "maxCallsPerRun", "maxDocumentChars", "timeoutSeconds"):
        require(0 < contract["model"][key], f"Invalid model budget: {key}")
    suppliers, sources = contract["suppliers"], contract["sources"]
    require(bool(suppliers), "Supplier denominator cannot be empty")
    unique([s["id"] for s in suppliers], "supplier ID")
    unique([s["id"] for s in sources], "source ID")
    supplier_ids = {s["id"] for s in suppliers}
    source_map = {s["id"]: s for s in sources}
    for source in sources:
        require(type(source["required"]) is bool, "Source requirement must be boolean")
        require(source["supplierId"] in supplier_ids, "Orphan source binding")
        require(source["registration"] in ("verified", "candidate"), "Unknown source registration")
        require(source["kind"] in ("sec_facts", "sec_submissions", "sec_documents", "sec_index", "official_discovery", "rss", "sitemap", "html_index", "q4_press_list", "citation"), "Unknown collector kind")
        if source['kind'] == 'q4_press_list':
            from q4_qualification_origin import validate_source
            validate_source(source)
        require(bool(source.get("family")), "Source family required")
        url = urlsplit(source["url"])
        require(url.scheme == "https" and not url.username and not url.password and url.port in (None, 443), "Unsafe source URL")
        require(url.hostname in source["allowedHosts"], "Source host is outside its contract")
        require(1 <= source["maxPages"] <= 1000, "Invalid pagination limit")
        if source["kind"] == "sec_index":
            from regulatory import validate_index_source
            validate_index_source(source, suppliers)
        elif source["kind"] == "sec_documents" and "regulatoryIssuer" in source:
            from regulatory import validate_filing_source
            validate_filing_source(source, suppliers)
        else:
            require("regulatoryIssuer" not in source, "Explicit regulatory issuer requires neutral SEC index or filing documents kind")
        if source.get("htmlCompleteness") == "orca-news-pagination-v1":
            require(source["kind"] == "html_index" and source["id"] == "orca:official:1" and
                    source["supplierId"] == "orca" and source["family"] == "official_announcements" and
                    source["allowedHosts"] == ["orca.security"] and
                    source["url"] == "https://orca.security/resources/news/" and source["maxPages"] <= 60,
                    "Orca HTML mode requires its exact source, supplier and index endpoint")
        if source.get("htmlCompleteness") == "ping-release-pagination-v1":
            require(source["kind"] == "html_index" and source["id"] == "ping-identity:official:1" and
                    source["supplierId"] == "ping-identity" and source["family"] == "official_announcements" and
                    source["allowedHosts"] == ["press.pingidentity.com"] and
                    source["url"] == "https://press.pingidentity.com/news-releases" and
                    type(source["maxPages"]) is int and source["maxPages"] <= 60,
                    "Ping HTML mode requires its exact source, supplier and index endpoint")
        if source.get("htmlCompleteness") == "ping-release-pagination-v2":
            require(source["kind"] == "html_index" and source["id"] == "ping-identity:official:1" and
                    source["supplierId"] == "ping-identity" and source["family"] == "official_announcements" and
                    source["allowedHosts"] == ["press.pingidentity.com"] and
                    source["url"] == "https://press.pingidentity.com/news-releases" and
                    type(source["maxPages"]) is int and source["maxPages"] <= 60,
                    "Ping HTML v2 mode requires its exact source, supplier and index endpoint")
        if source.get("htmlCompleteness") == "ping-release-pagination-v3":
            require(source["kind"] == "html_index" and source["id"] == "ping-identity:official:1" and
                    source["supplierId"] == "ping-identity" and source["family"] == "official_announcements" and
                    source["allowedHosts"] == ["press.pingidentity.com"] and
                    source["url"] == "https://press.pingidentity.com/news-releases" and
                    type(source["maxPages"]) is int and source["maxPages"] <= 60,
                    "Ping HTML v3 mode requires its exact source, supplier and index endpoint")
        for mode, supplier_id, host, index in (
                ('delinea-news-pagination-v1', 'delinea', 'delinea.com', 'https://delinea.com/news'),
                ('delinea-news-pagination-v2', 'delinea', 'delinea.com', 'https://delinea.com/news'),
                ('delinea-news-pagination-v3', 'delinea', 'delinea.com', 'https://delinea.com/news'),
                ('delinea-news-pagination-v4', 'delinea', 'delinea.com', 'https://delinea.com/news'),
                ('delinea-news-pagination-v5', 'delinea', 'delinea.com', 'https://delinea.com/news'),
                ('sonatype-press-pagination-v1', 'sonatype', 'www.sonatype.com', 'https://www.sonatype.com/press-releases'),
                ('sonatype-press-pagination-v2', 'sonatype', 'www.sonatype.com', 'https://www.sonatype.com/press-releases'),
                ('sonatype-press-pagination-v3', 'sonatype', 'www.sonatype.com', 'https://www.sonatype.com/press-releases'),
                ('sonatype-press-pagination-v4', 'sonatype', 'www.sonatype.com', 'https://www.sonatype.com/press-releases'),
                ('sonatype-press-pagination-v5', 'sonatype', 'www.sonatype.com', 'https://www.sonatype.com/press-releases')):
            if source.get('htmlCompleteness') == mode:
                require(source['kind'] == 'html_index' and source['id'] == supplier_id + ':official:1' and
                        source['supplierId'] == supplier_id and source['family'] == 'official_announcements' and
                        source['allowedHosts'] == [host] and source['url'] == index and
                        type(source['maxPages']) is int and source['maxPages'] <= 60,
                        'HTML archive mode requires its exact source, supplier and index endpoint')
    for supplier in suppliers:
        require(bool(supplier["requiredCategories"]), "Supplier has no coverage requirements")
        require(bool(supplier.get("requiredFamilies")), "Supplier has no required source families")
        unique(supplier["sourceIds"], "supplier source binding")
        unique(supplier["requiredCategories"], "required category")
        unique(supplier["requiredFamilies"], "required source family")
        require(set(supplier["sourceIds"]) == {s["id"] for s in sources if s["supplierId"] == supplier["id"]}, "Source absent from supplier inventory")
        for sid in supplier["sourceIds"]:
            require(sid in source_map and source_map[sid]["supplierId"] == supplier["id"], "Invalid supplier/source join")
    return contract


def plan_run(contract, scheduled_at, previous_run=None):
    validate_contract(contract)
    at = instant(scheduled_at).astimezone(timezone.utc)
    contract_hash = digest(contract)
    # Same approved contract and UTC day generate the same logical inventory.
    run_id = digest({"contract": contract_hash, "day": at.date().isoformat()})
    tasks = []
    for source in contract["sources"]:
        tasks.append({"taskId": digest({"run": run_id, "source": source["id"]}),
                      "sourceId": source["id"], "supplierId": source["supplierId"],
                      "kind": "collect", "required": source["required"]})
    # Missing discovery bindings are explicit failed work, never an absent denominator.
    for supplier in contract["suppliers"]:
        bound = {s["family"] for s in contract["sources"] if s["supplierId"] == supplier["id"] and s["required"]}
        for family in supplier["requiredFamilies"]:
            if family in bound:
                continue
            tasks.append({"taskId": digest({"run": run_id, "gap": supplier["id"], "family": family}),
                          "sourceId": None, "supplierId": supplier["id"],
                          "kind": "missing_discovery", "family": family, "required": True})
    inventory = sorted(tasks, key=lambda t: t["taskId"])
    return {"schemaVersion": 1, "runId": run_id, "scheduledAt": at.isoformat().replace("+00:00", "Z"),
            "contractVersion": contract["version"], "contractSha256": contract_hash,
            "previousRunId": previous_run, "inventorySha256": digest(inventory),
            "supplierIds": sorted(s["id"] for s in contract["suppliers"]), "tasks": inventory}


def valid_hash(value):
    return isinstance(value, str) and bool(re.fullmatch(r"[a-f0-9]{64}", value))
