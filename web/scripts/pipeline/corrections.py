"""Hash-bound factual correction admission. No fetching or quota bypasses.

API: load_policy(repo, market), validate_baseline(inventories, baseline),
process_corrections(repo, store, market, agent, reserve, now, cancelled=None),
project_bundle(repo, store, market, outcome, previous_bundle=None, publication_at=None).
Only SubscriptionAgent reviews admit changes. A test agent with synthetic=True writes
non-admitting attempts, never an admission cache usable by the publication gate.
The outcome/bundle policy binds the global inventory. Review/admission policies bind
only the atomic group's current exact review dependencies and rules.
"""
import copy
import json
import re
import uuid
from datetime import timezone
from pathlib import Path
from urllib.parse import urlsplit

from agents import SubscriptionAgent, PUBLISHER_DISCLOSURE_SCOPE, PUBLISHER_DISCLOSURE_CHECKS
from contracts import canonical, digest, instant, require, unique, utcnow, valid_hash
from discovery import Page, IndexMarkup, decoded_discovery_body
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
REVIEW_RULES_VERSION = "dated-factual-correction-review-1"
PUBLISHER_RULES_VERSION = "dated-publisher-disclosure-classification-1"
PUBLISHER_OPERATION = "reclassify_publisher_disclosure"
PUBLISHER_ORIGINAL_SHA256 = "62bb8bcce0698b5f164867d9bc070be77ee4eebde095947dd96eb8a693d0d6fb"
PUBLISHER_PROPOSED_SHA256 = "86b06657bb1139a5d98d293b5599590539baec7e099b59294a3a3e7e0001fe76"
PUBLISHER_URL = "https://finance.yahoo.com/news/xage-security-hits-record-growth-120000615.html"
PUBLISHER_LIMITATIONS = ("Yahoo Finance labels this page as a paid press release and attributes it to Xage Security "
                         "with a GlobeNewswire dateline. It is issuer-attributed release material republished by Yahoo "
                         "Finance, not independent editorial reporting. This publication-role correction does not "
                         "independently verify the financial, funding or operating figures in the unchanged excerpt.")
PUBLISHER_QUOTES = {
    "publisher_paid_disclosure": "This is a paid press release. Contact the press release distributor directly with any inquiries.",
    "issuer_attributed_dateline": "PALO ALTO, Calif., March 18, 2026 (GLOBE NEWSWIRE) -- Xage Security",
    "article_issuer_byline_context": "Xage Security March 18, 2026 7 min read",
}


def _publisher_scope(group):
    if "reviewScope" not in group:
        return False
    require(group["reviewScope"] == PUBLISHER_DISCLOSURE_SCOPE, "Unknown correction review scope")
    return True


def group_review_policy(group, market, baseline_sha256):
    """Bind the review rules and this group's exact dependencies, independent of run inventory."""
    require(valid_hash(baseline_sha256), "Invalid correction review baseline hash")
    suppliers = [supplier for supplier in market["suppliers"] if supplier["id"] == group["supplierId"]]
    require(len(suppliers) == 1, "Correction review supplier missing or duplicate")
    supplier = suppliers[0]
    require(all(key in supplier for key in ("id", "name", "aliases", "kind")), "Correction review supplier identity incomplete")
    require(all(isinstance(supplier[key], str) and supplier[key] for key in ("id", "name", "kind"))
            and isinstance(supplier["aliases"], list) and all(isinstance(alias, str) for alias in supplier["aliases"]),
            "Correction review supplier identity invalid")
    configured = []
    for source in group["sources"]:
        matching = [entry for entry in market["sources"] if entry["id"] == source["sourceId"]]
        require(len(matching) == 1, "Correction review source missing or duplicate")
        configured.append(matching[0])
    basis = {"schemaVersion": 1, "rulesVersion": REVIEW_RULES_VERSION,
                   "baselineSha256": baseline_sha256, "candidateSha256": digest(group),
                   "supplier": {key: supplier[key] for key in ("id", "name", "aliases", "kind")},
                   "sources": configured,
                   "model": {key: market["model"][key] for key in ("provider", "allowApiBilling", "maxDocumentChars")},
                   "freshnessHours": 30, "checks": sorted(REVIEW_CHECKS)}
    if _publisher_scope(group):
        basis.update(rulesVersion=PUBLISHER_RULES_VERSION, reviewScope=PUBLISHER_DISCLOSURE_SCOPE,
                     allowedTransition={"targetId": "evidence:TR-xage-1", "originalSha256": PUBLISHER_ORIGINAL_SHA256,
                                        "from": "INDEPENDENT", "to": "OFFICIAL",
                                        "mutableFields": ["limitations", "sourceClass"]},
                     checks=sorted(PUBLISHER_DISCLOSURE_CHECKS))
    return digest(basis)


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


def _publisher_target(target, group, records):
    original, proposed = target["original"], target["proposedValue"]
    require(group["supplierId"] == "xage" and target["targetId"] == "evidence:TR-xage-1"
            and target["operation"] == PUBLISHER_OPERATION, "Publisher disclosure target or operation differs")
    require(target["originalSha256"] == PUBLISHER_ORIGINAL_SHA256
            and canonical(original) == canonical(records["evidence"].get("TR-xage-1")),
            "Publisher disclosure immutable original differs")
    require(isinstance(proposed, dict) and set(proposed) == set(original), "Publisher disclosure record shape differs")
    require(original.get("sourceClass") == "INDEPENDENT" and proposed.get("sourceClass") == "OFFICIAL"
            and proposed.get("limitations") == PUBLISHER_LIMITATIONS, "Publisher disclosure class or limitations differs")
    require(all(proposed[key] == value for key, value in original.items() if key not in ("sourceClass", "limitations")),
            "Publisher disclosure protected metadata changed")
    require(digest(proposed) == PUBLISHER_PROPOSED_SHA256, "Publisher disclosure proposed record differs")


def _publisher_group_schema(group):
    require(group["supplierId"] == "xage" and len(group["targets"]) == 1 and len(group["sources"]) == 1,
            "Publisher disclosure requires one exact target and source")
    quotes = group["disclosureQuotes"]
    require(isinstance(quotes, list) and len(quotes) == len(PUBLISHER_QUOTES), "Publisher disclosure quote inventory differs")
    require([q.get("id") if isinstance(q, dict) else None for q in quotes] == list(PUBLISHER_QUOTES),
            "Publisher disclosure quote identities differ")
    for quote in quotes:
        _keys(quote, {"id", "text", "normalizedWholePageStart", "normalizedWholePageEnd", "textSha256",
                      "literalInWholePageText", "literalInUniqueArticle", "scope"}, "Publisher disclosure quote")
        text = PUBLISHER_QUOTES[quote["id"]]
        require(quote["text"] == text and quote["textSha256"] == digest(text.encode()),
                "Publisher disclosure quote text/hash differs")
        require(type(quote["normalizedWholePageStart"]) is int and quote["normalizedWholePageStart"] >= 0
                and type(quote["normalizedWholePageEnd"]) is int
                and quote["normalizedWholePageEnd"] == quote["normalizedWholePageStart"] + len(text),
                "Publisher disclosure quote positions invalid")
        # These descriptive fields grant no authority; validate_sources replays every claim.
        require(quote["literalInWholePageText"] is True and quote["literalInUniqueArticle"] is True
                and quote["scope"] == "publication role and attribution only", "Publisher disclosure quote scope differs")


def _target(target, group, records):
    _keys(target, {"targetId", "operation", "original", "originalSha256", "proposedValue"}, "Correction target")
    require(valid_hash(target["originalSha256"]) and target["originalSha256"] == digest(target["original"]), "Correction before hash differs")
    if _publisher_scope(group):
        _publisher_target(target, group, records)
        return
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
        require(isinstance(group, dict), "Invalid correction group")
        publisher = _publisher_scope(group)
        _keys(group, {"id", "supplierId", "reasonCode", "noteTemplate", "targets", "sources"}
              | ({"reviewScope", "disclosureQuotes"} if publisher else set()), "Correction group")
        require(all(isinstance(group[key], str) and group[key].strip() for key in ("id", "supplierId", "reasonCode", "noteTemplate")), "Empty correction group metadata")
        require(group["supplierId"] in records["suppliers"] and group["supplierId"] in {s["id"] for s in market["suppliers"]}, "Unknown correction supplier")
        require(group["noteTemplate"].count("{date}") == 1 and not re.search(r"[{}]", group["noteTemplate"].replace("{date}", "")), "Correction note needs one date placeholder")
        require(isinstance(group["targets"], list) and group["targets"] and isinstance(group["sources"], list) and group["sources"], "Incomplete correction group")
        if publisher:
            _publisher_group_schema(group)
        group_ids.append(group["id"])
        for target in group["targets"]:
            _target(target, group, records)
            target_ids.append(target["targetId"])
        evidence_ids = []
        source_ids = {s["id"]: s for s in market["sources"]}
        for source in group["sources"]:
            _keys(source, {"evidenceId", "sourceId", "url", "observationId", "body", "fetchedAt"}
                  | ({"proofScope", "visibleText", "disclosureQuoteIds"} if publisher else set()), "Correction source")
            require(all(isinstance(source[key], str) and source[key] for key in ("evidenceId", "sourceId", "url")), "Invalid correction source binding")
            evidence = records["evidence"].get(source["evidenceId"])
            configured = source_ids.get(source["sourceId"])
            if publisher:
                require(evidence and digest(evidence) == PUBLISHER_ORIGINAL_SHA256
                        and source["evidenceId"] == "TR-xage-1" and source["sourceId"] == "xage:citation:TR-xage-1"
                        and source["url"] == PUBLISHER_URL and source["proofScope"] == PUBLISHER_DISCLOSURE_SCOPE,
                        "Publisher disclosure source scope differs")
                require(configured and configured.get("kind") == "citation"
                        and configured.get("evidenceId") == "TR-xage-1" and configured.get("family") == "citation_integrity",
                        "Publisher disclosure requires the exact configured citation")
                _keys(source["visibleText"], {"rulesVersion", "sha256", "chars"}, "Publisher disclosure visible text")
                text_pin = source["visibleText"]
                require(text_pin["rulesVersion"] == "page-all-visible-text-whitespace-1" and valid_hash(text_pin["sha256"])
                        and type(text_pin["chars"]) is int and 100 <= text_pin["chars"] <= min(market["model"]["maxDocumentChars"], 30000),
                        "Publisher disclosure whole document exceeds limit or text pin invalid")
                require(source["disclosureQuoteIds"] == list(PUBLISHER_QUOTES), "Publisher disclosure source quote inventory differs")
            else:
                # Financial authority is always taken from immutable originals, never a projected display class.
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
    global_policy = digest({"marketSha256": digest(market), "requestsSha256": digest(requests), "baselineSha256": pin["sha256"]})
    review_policies = {group["id"]: group_review_policy(group, market, pin["sha256"]) for group in requests["groups"]}
    stamp = _read_json(Path(repo) / "web/src/data/tracker/factualCorrectionPolicy.json")
    source_ids = {group["id"]: [source["evidenceId"] for source in group["sources"]] for group in requests["groups"]}
    require(type(stamp.get("schemaVersion")) is int and stamp == {"schemaVersion": 1, "policySha256": global_policy, "groupIds": group_ids, "targetIds": target_ids, "sourceEvidenceIds": source_ids, "reviewPolicySha256ByGroup": review_policies},
            "Correction build policy manifest differs")
    return {"requests": requests, "baseline": baseline, "policySha256": global_policy, "reviewPolicySha256ByGroup": review_policies}


def _normalize(value):
    # Page already decodes HTML entities once. Decoding again would let a
    # double-escaped source support characters absent from its displayed text.
    return re.sub(r"\s+", " ", value).strip()


def _publisher_document(group, source, raw, page, text):
    """Bind publisher self-disclosures to this exact article, never to financial authority."""
    pin = source["visibleText"]
    require(pin["sha256"] == digest(text.encode()) and pin["chars"] == len(text),
            "Publisher disclosure complete text pin differs")
    require(page.canonicals == [source["url"]], "Publisher disclosure canonical URL differs")
    root = IndexMarkup(raw).root
    nodes = list(root.walk())
    articles = [node for node in nodes if node.tag == "article"]
    require(len(articles) == 1 and articles[0].closed
            and articles[0].attrs.get("data-testid") == "article-content-wrapper",
            "Publisher disclosure unique article missing or ambiguous")
    article = articles[0]
    article_text = _normalize(article.text)
    disclaimers = [node for node in nodes if node.attrs.get("data-testid") == "press-release-disclaimer"]
    require(len(disclaimers) == 1 and disclaimers[0].closed and disclaimers[0].inside(article)
            and _normalize(disclaimers[0].text) == PUBLISHER_QUOTES["publisher_paid_disclosure"],
            "Publisher disclosure paid notice is not in the same article")
    bylines = [node for node in nodes if "byline-attr-author" in node.classes]
    require(len(bylines) == 1 and bylines[0].closed and bylines[0].inside(article)
            and _normalize(bylines[0].text) == "Xage Security", "Publisher disclosure issuer byline differs")
    require(PUBLISHER_QUOTES["issuer_attributed_dateline"] in article_text,
            "Publisher disclosure provider dateline missing from article")

    # IndexNode.walk excludes scripts; examine only the one structured metadata script separately.
    pending, metadata_nodes = [root], []
    while pending:
        node = pending.pop()
        if node.tag == "script" and node.attrs.get("type") == "application/ld+json":
            metadata_nodes.append(node)
        pending.extend(child for child in node.children if not isinstance(child, str))
    require(len(metadata_nodes) == 1 and metadata_nodes[0].closed, "Publisher disclosure metadata missing or ambiguous")
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "Duplicate publisher disclosure metadata property")
            result[key] = value
        return result
    metadata = json.loads("".join(child for child in metadata_nodes[0].children if isinstance(child, str)),
                          object_pairs_hook=pairs,
                          parse_constant=lambda _: require(False, "Non-finite publisher disclosure metadata"))
    require(isinstance(metadata, dict) and metadata.get("@type") == "NewsArticle"
            and isinstance(metadata.get("mainEntityOfPage"), dict)
            and metadata["mainEntityOfPage"].get("@id") == source["url"],
            "Publisher disclosure metadata article URL differs")
    publisher, provider = metadata.get("publisher"), metadata.get("provider")
    require(isinstance(publisher, dict) and publisher.get("url") == "https://finance.yahoo.com/"
            and "Yahoo Finance" in (publisher.get("name"), publisher.get("alternateName"))
            and isinstance(provider, dict) and provider.get("name") == "GlobeNewswire"
            and provider.get("url") == "https://www.globenewswire.com/",
            "Publisher disclosure publisher/provider attribution differs")
    require(all(isinstance(metadata.get(key), dict) and metadata[key].get("name") == "Xage Security"
                for key in ("author", "creator")), "Publisher disclosure metadata issuer differs")
    headlines = [node for node in article.walk() if node.tag == "h1"]
    require(len(headlines) == 1 and headlines[0].closed and isinstance(metadata.get("headline"), str)
            and _normalize(headlines[0].text) == metadata["headline"] and bool(metadata["headline"].strip()),
            "Publisher disclosure metadata headline differs")
    for quote in group["disclosureQuotes"]:
        start, end = quote["normalizedWholePageStart"], quote["normalizedWholePageEnd"]
        require(text[start:end] == quote["text"] and text.count(quote["text"]) == 1
                and quote["text"] in article_text and digest(quote["text"].encode()) == quote["textSha256"],
                "Publisher disclosure literal quote binding differs")


def validate_sources(group, store, market, admitted_at):
    """Replay exact source/observation joins and freshness at initial admission."""
    documents = []
    at = _time(admitted_at)
    publisher = _publisher_scope(group)
    limit = min(market["model"]["maxDocumentChars"], 30000) if publisher else market["model"]["maxDocumentChars"]
    for source in group["sources"]:
        observation = store.read("observations/" + source["observationId"] + ".json")
        require(observation and observation.get("observationId") == source["observationId"] and observation.get("sourceId") == source["sourceId"], "Correction observation/source differs")
        require(observation.get("status") in ("fetched", "not_modified"), "Correction source observation unsuccessful")
        if publisher:
            require((observation["status"], observation.get("httpStatus")) in (("fetched", 200), ("not_modified", 304)),
                    "Publisher disclosure HTTP status differs")
        require(observation.get("requestedUrl") == source["url"] and observation.get("finalUrl", source["url"]) == source["url"], "Correction observation URL differs")
        require(observation.get("body") == source["body"] and observation.get("fetchedAt") == source["fetchedAt"], "Correction observation body or time differs")
        if observation.get("verifiedAt"):
            require(_time(observation["verifiedAt"]) <= at, "Correction observation verification after admission")
        age = (at - _time(source["fetchedAt"])).total_seconds()
        require(0 <= age <= 30 * 3600, "Correction source expired or future at admission")
        raw = decoded_discovery_body(store.get(source["body"])).decode("utf8", errors="strict")
        page = Page(raw, source_url=source["url"])
        # Whole decoded source text is retained. No excerpt-only or silent truncation.
        text = _normalize(" ".join(page.text))
        require(len(text) >= 100 and len(text) <= limit, "Correction primary document exceeds limit or is unreadable")
        require(not re.search(r"access denied|verify you are human|request rate threshold exceeded", text[:2000], re.I), "Correction source block page")
        if publisher:
            _publisher_document(group, source, raw, page, text)
        documents.append({"source": source, "text": text})
    require(sum(len(document["text"]) for document in documents) <= limit,
            "Correction primary document set exceeds model input budget")
    if publisher:
        # The immutable financial paraphrase is preserved; only literal role disclosures are admitted.
        return documents
    for target in group["targets"]:
        if target["targetId"].startswith("evidence:"):
            evidence = target["proposedValue"]
            texts = [d["text"] for d in documents if d["source"]["evidenceId"] == evidence["id"]]
            require(any(_normalize(evidence["excerpt"]) in text for text in texts), "Correction evidence excerpt not literally in primary source")
    return documents


def _review(review, group, review_policy_hash):
    publisher = _publisher_scope(group)
    _keys(review, {"result", "candidateSha256", "evidenceSetSha256", "policySha256", "checks"}
          | ({"reviewScope"} if publisher else set()), "Correction review")
    if publisher:
        require(review["reviewScope"] == PUBLISHER_DISCLOSURE_SCOPE, "Publisher disclosure review scope differs")
    require(review["candidateSha256"] == digest(group), "Correction review candidate hash differs")
    require(review["evidenceSetSha256"] == digest(group["sources"]), "Correction review evidence set hash differs")
    require(review["policySha256"] == review_policy_hash, "Correction review policy hash differs")
    require(review["result"] == "accepted", "Correction independent review did not accept")
    checks = PUBLISHER_DISCLOSURE_CHECKS if publisher else REVIEW_CHECKS
    require(isinstance(review["checks"], dict) and set(review["checks"]) == checks and all(v == "pass" for v in review["checks"].values()), "Correction independent review checks incomplete")


def _index(group, review_policy_hash):
    return "correction-admissions/" + review_policy_hash + "/" + digest(group) + "-" + digest(group["sources"]) + ".json"


def replay_admission(group, reference, store, market, review_policy_hash, checked_at=None):
    _reference(reference)
    admission = json.loads(store.get(reference))
    publisher = _publisher_scope(group)
    _keys(admission, {"groupId", "candidateSha256", "evidenceSetSha256", "policySha256", "admittedAt", "review", "sources"}
          | ({"reviewScope"} if publisher else set()), "Correction admission")
    if publisher:
        require(admission["reviewScope"] == PUBLISHER_DISCLOSURE_SCOPE, "Publisher disclosure admission scope differs")
    require(admission["groupId"] == group["id"] and admission["candidateSha256"] == digest(group)
            and admission["evidenceSetSha256"] == digest(group["sources"]) and admission["policySha256"] == review_policy_hash
            and admission["sources"] == group["sources"], "Correction admission binding differs")
    _time(admission["admittedAt"])
    if checked_at:
        require(_time(admission["admittedAt"]) <= _time(checked_at), "Correction admission after gate time")
    validate_sources(group, store, market, admission["admittedAt"])
    _reference(admission["review"])
    _review(json.loads(store.get(admission["review"])), group, review_policy_hash)
    indexed = store.read(_index(group, review_policy_hash))
    require(indexed == {"groupId": group["id"], "admission": reference}, "Correction admission missing immutable accepted index")
    return admission


def process_corrections(repo, store, market, agent, reserve, now, cancelled=None, clock=None):
    clock = clock or utcnow
    context = load_policy(repo, market)
    global_policy = context["policySha256"]
    _time(now)
    result = {"policySha256": global_policy, "admitted": [], "pending": [], "attempts": []}
    for group in context["requests"]["groups"]:
        review_policy = context["reviewPolicySha256ByGroup"][group["id"]]
        cached = store.read(_index(group, review_policy))
        if cached:
            try:
                replay_admission(group, cached["admission"], store, market, review_policy, now)
                result["admitted"].append(cached)
                continue
            except (ValueError, OSError, KeyError, TypeError) as exc:
                result["pending"].append({"groupId": group["id"], "reason": str(exc)[:240]})
                continue
        attempt = {"groupId": group["id"], "candidateSha256": digest(group), "evidenceSetSha256": digest(group["sources"]),
                   "policySha256": review_policy, "startedAt": now, "sources": copy.deepcopy(group["sources"]),
                   "nonce": uuid.uuid4().hex, "review": None, "outcome": "pending", "error": None}
        publisher = _publisher_scope(group)
        if publisher:
            attempt["reviewScope"] = PUBLISHER_DISCLOSURE_SCOPE
        try:
            require(not cancelled or not cancelled(), "CORRECTION_CANCELLED_OR_DEADLINE")
            documents = validate_sources(group, store, market, now)
            require(isinstance(agent, SubscriptionAgent) and callable(reserve), "CORRECTION_SUBSCRIPTION_REVIEW_REQUIRED")
            require(not getattr(agent, "synthetic", False), "SYNTHETIC_CORRECTION_REVIEW_NON_ADMITTING")
            agent.reserve = reserve
            reservation = "correction-document-reservations/" + now[:10] + "/" + digest({"group": group, "policy": review_policy}) + ".json"
            if not store.read(reservation):
                reserve("documents", market["model"]["maxDocumentsPerRun"])
                store.write_once(reservation, {"groupId": group["id"], "candidateSha256": digest(group), "reservedAt": now})
            require(not cancelled or not cancelled(), "CORRECTION_CANCELLED_OR_DEADLINE")
            response = (agent.review_publisher_disclosure(documents, group, review_policy) if publisher
                        else agent.review_correction(documents, group, review_policy))
            attempt["review"] = store.put(response)
            _review(response, group, review_policy)
            admitted_at = clock()
            require(_time(admitted_at) >= _time(now), "Correction admission completion precedes attempt")
            require(not cancelled or not cancelled(), "CORRECTION_CANCELLED_OR_DEADLINE")
            validate_sources(group, store, market, admitted_at)
            admission = {"groupId": group["id"], "candidateSha256": digest(group), "evidenceSetSha256": digest(group["sources"]),
                         "policySha256": review_policy, "admittedAt": admitted_at, "review": attempt["review"], "sources": copy.deepcopy(group["sources"])}
            if publisher:
                admission["reviewScope"] = PUBLISHER_DISCLOSURE_SCOPE
            entry = {"groupId": group["id"], "admission": store.put(admission)}
            store.write_once(_index(group, review_policy), entry)
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
    global_policy, groups = context["policySha256"], context["requests"]["groups"]
    _time(publication_at)
    require(isinstance(outcome, dict) and outcome.get("policySha256") == global_policy and not outcome.get("pending"), "Correction admissions pending or policy changed")
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
        require(valid_hash(previous_bundle.get("policySha256")), "Published correction policy invalid")
        require(_time(previous_bundle["checkedAt"]) <= _time(publication_at), "Published correction check time is future")
        old = {g["id"]: g for g in previous_bundle["groups"]}
        require(len(old) == len(previous_bundle["groups"]) and bool(old) and set(old).issubset({g["id"] for g in groups}), "Published correction inventory changed")
        if previous_bundle["policySha256"] == global_policy:
            require(set(old) == {g["id"] for g in groups}, "Published correction inventory changed")
    public = []
    for group in groups:
        entry = next(e for e in entries if e["groupId"] == group["id"])
        _keys(entry, {"groupId", "admission"}, "Correction admitted entry")
        review_policy = context["reviewPolicySha256ByGroup"][group["id"]]
        admission = replay_admission(group, entry["admission"], store, market, review_policy, publication_at)
        metadata = {key: admission[key] for key in ("candidateSha256", "evidenceSetSha256", "policySha256", "admittedAt")}
        metadata.update(reviewSha256=admission["review"]["sha256"], result="accepted")
        if _publisher_scope(group):
            metadata["reviewScope"] = PUBLISHER_DISCLOSURE_SCOPE
        day = old.get(group["id"], {}).get("date", publication_at[:10])
        _time(day + "T00:00:00Z")
        require(day <= publication_at[:10], "Correction publication date is future")
        row = {"id": group["id"], "supplierId": group["supplierId"], "reasonCode": group["reasonCode"], "date": day,
               "note": group["noteTemplate"].replace("{date}", day), "targets": copy.deepcopy(group["targets"]), "admission": metadata}
        if _publisher_scope(group):
            row["reviewScope"] = PUBLISHER_DISCLOSURE_SCOPE
        require(group["id"] not in old or old[group["id"]] == row, "Historical correction changed")
        public.append(row)
    return {"schemaVersion": 1, "enabled": True, "policySha256": global_policy, "checkedAt": publication_at, "groups": public}
