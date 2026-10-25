"""Exact retained Q4 samples: derived proposal evidence with no operational authority."""
import copy
import json
import re
from datetime import datetime
from pathlib import Path

from contracts import digest, instant, require
from discovery import IndexMarkup
import q4_primary_qualification as primary
from q4_press_list import _object, _constant

KIND = "q4_retained_primary_template_v1"
DESCRIPTOR_SHA256 = "f0a341f3d8d95703a70da67970ee65b4af794789076f84dd6c48c7494dd9aa93"
REPO = Path(__file__).resolve().parents[3]
INERT = primary._PublicationMetadata.INERT | {"script", "style"}


def _active(node):
    while node is not None:
        if node.tag in INERT or "hidden" in node.attrs or node.attrs.get("aria-hidden", "").lower() == "true" or re.search(
                r"(?:display\s*:\s*none|visibility\s*:\s*hidden)", node.attrs.get("style", ""), re.I):
            return False
        node = node.parent
    return True


class _Markup(IndexMarkup):
    """Reuse the structural reader only for the two fixed authenticated bodies."""
    def __init__(self, text, ids):
        self.ids, self.scripts = set(ids), []
        super().__init__(text)

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        relevant = tag in ("title", "meta", "script") or fields.get("id") in self.ids
        require(tag != "base" and (not relevant or len(attrs) == len(fields)),
                "Q4_RETAINED_BASE_OR_DUPLICATE_ATTRIBUTES")
        super().handle_starttag(tag, attrs)
        if tag == "script":
            self.scripts.append(self.stack[-1])

    def handle_startendtag(self, tag, attrs):
        require(tag not in INERT, "Q4_RETAINED_SELF_CLOSING_CONTEXT")
        super().handle_startendtag(tag, attrs)


def _text(node):
    return " ".join(node.text.split())


def _one(nodes, message):
    require(len(nodes) == 1 and nodes[0].closed and _active(nodes[0]), message)
    return nodes[0]


def _day(value, expected):
    require(isinstance(value, str) and re.match(r"^\d{4}-\d{2}-\d{2}(?:$|T| )", value),
            "Q4_RETAINED_PUBLICATION_DATE_INVALID")
    require(datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat() == expected,
            "Q4_RETAINED_PUBLICATION_DAY_CONFLICT")


def _shape(body, row, target):
    template, sample = row["template"], target["sample"]
    text = body.decode("utf-8", errors="strict")
    ids = [v for k, v in template.items() if k.endswith("Id") and k != "moduleWorkflowId"]
    markup = _Markup(text, ids)
    nodes = list(markup.root.walk())
    head = _one([n for n in nodes if n.tag == "head"], "Q4_RETAINED_HEAD_AMBIGUOUS")
    get = lambda key: _one([n for n in nodes if n.attrs.get("id") == template[key]],
                          "Q4_RETAINED_STRUCTURAL_ID_DIFFERS:" + key)
    module, item = get("moduleId"), get("itemId")
    heading_wrapper, heading, span = get("headlineWrapperId"), get("headlineId"), get("headlineSpanId")
    date_wrapper, date, time = get("dateWrapperId"), get("dateId"), get("timeId")
    article = get("bodyId")
    require(module.tag == item.tag == article.tag == heading_wrapper.tag == date_wrapper.tag == "div" and
            {"evergreen", "evergreen-news-details"} <= module.classes and
            module.attrs.get("data-workflow-id") == template["moduleWorkflowId"] and
            "evergreen-news-details-item" in item.classes and item.inside(module) and
            heading_wrapper.parent is item and "evergreen-news-headline" in heading_wrapper.classes and
            heading.parent is heading_wrapper and heading.tag == "h3" and
            {"evergreen-item-detail-title", "evergreen-news-title"} <= heading.classes and
            span.parent is heading and span.tag == "span" and len(heading.children) >= 1 and
            _text(heading) == _text(span) == sample["title"] and
            date_wrapper.parent is item and "evergreen-news-date-time" in date_wrapper.classes and
            date.parent is date_wrapper and date.tag == "span" and "evergreen-news-date-text" in date.classes and
            time.parent is date_wrapper and time.tag == "span" and not _text(time) and
            article.parent is item and "evergreen-news-body" in article.classes,
            "Q4_RETAINED_ARTICLE_STRUCTURE_OR_HEADING_DIFFERS")
    for cls, expected in (("evergreen-news-details", module), ("evergreen-news-details-item", item),
                          ("evergreen-news-title", heading), ("evergreen-news-date-text", date),
                          ("evergreen-news-body", article)):
        require([n for n in nodes if cls in n.classes] == [expected], "Q4_RETAINED_ARTICLE_NODE_AMBIGUOUS")
    require([_text(n) for n in nodes if n.tag == "h1" and _active(n)] == ["News Details"],
            "Q4_RETAINED_GENERIC_H1_DIFFERS")
    titles = [n for n in nodes if n.tag == "title"]
    require(len(titles) == 1 and titles[0].parent is head and titles[0].closed and _active(titles[0]) and
            _text(titles[0]) == template["titlePrefix"] + sample["title"], "Q4_RETAINED_DOCUMENT_TITLE_DIFFERS")
    for prop, value in (("og:title", sample["title"]), ("og:url", row["url"])):
        tags = [n for n in nodes if n.tag == "meta" and n.attrs.get("property") == prop]
        require(len(tags) == 1 and tags[0].parent is head and _active(tags[0]) and tags[0].attrs.get("content") == value,
                "Q4_RETAINED_OPEN_GRAPH_IDENTITY_DIFFERS")
    require(not [n for n in nodes if n.tag == "link" and "canonical" in n.attrs.get("rel", "").lower().split()],
            "Q4_RETAINED_CANONICAL_MUST_REMAIN_ABSENT")
    calendar = datetime.strptime(_text(date), "%B %d, %Y").date().isoformat()
    require(calendar == sample["calendarDay"], "Q4_RETAINED_VISIBLE_DATE_DIFFERS")
    readable = _text(article)
    require(len(readable) >= 100 and template["issuer"] in readable and readable.endswith(template["sourceMarker"]) and
            not any(marker in readable[:2000].lower() for marker in (
                "access denied", "verify you are human", "request rate threshold exceeded",
                "your request originates from an undeclared automated tool")), "Q4_RETAINED_BODY_UNREADABLE_OR_BLOCKED")
    metadata = primary._PublicationMetadata(text).values
    for value in metadata:
        _day(value["value"], sample["calendarDay"])
    jsonld = []
    for script in markup.scripts:
        if script.attrs.get("type", "").strip().lower() != "application/ld+json":
            continue
        require(script.parent is head and script.closed, "Q4_RETAINED_JSONLD_CONTEXT_DIFFERS")
        value = json.loads("".join(script.children), object_pairs_hook=_object, parse_constant=_constant)
        require(type(value) is dict, "Q4_RETAINED_JSONLD_SHAPE_DIFFERS")
        jsonld.append(value)
    if template["jsonLdRequired"]:
        require(len(jsonld) == 1 and jsonld[0].get("@type") == "NewsArticle" and
                jsonld[0].get("headline") == sample["title"] and
                jsonld[0].get("mainEntityOfPage") == {"@type": "WebPage", "@id": row["url"]},
                "Q4_RETAINED_JSONLD_IDENTITY_DIFFERS")
        for key in ("datePublished", "dateModified"):
            _day(jsonld[0].get(key), sample["calendarDay"])
        require(jsonld[0]["datePublished"] == jsonld[0]["dateModified"] == "2026-10-14T15:05:00Z",
                "Q4_RETAINED_OBSERVED_JSONLD_DATES_DIFFER")
    else:
        require(not jsonld and not metadata, "Q4_RETAINED_ABSENT_MACHINE_DATE_DIFFERS")
    return {"canonical": None, "identityProof": "source_bound_response_and_og_url", "heading": _text(heading),
            "genericH1": "News Details", "documentTitle": _text(titles[0]), "ogTitle": sample["title"],
            "ogUrl": row["url"], "structuralIds": {k: template[k] for k in template if k.endswith("Id")},
            "readableCharacters": len(readable), "readableSha256": digest(readable.encode()),
            "displayedDate": _text(date), "displayedCalendarDay": calendar,
            "indexDateLiteral": sample["dateLiteral"], "indexTimezone": None,
            "dateMetadata": metadata, "dateMetadataState": "present" if metadata else "unknown",
            "jsonLdIdentity": [{k: v[k] for k in ("@type", "headline", "mainEntityOfPage", "datePublished", "dateModified")}
                               for v in jsonld], "publicationComparison": "written_calendar_day"}


def _validate(contract, store, raw):
    require(type(raw) is bytes and 0 < len(raw) <= 100_000, "Q4_RETAINED_DESCRIPTOR_SIZE_INVALID")
    descriptor = json.loads(raw, object_pairs_hook=_object, parse_constant=_constant)
    require(digest(descriptor) == DESCRIPTOR_SHA256 and digest(contract) == primary.POLICY_SHA256,
            "Q4_RETAINED_EXACT_DESCRIPTOR_OR_POLICY_REQUIRED")
    proof = descriptor["actualProof"]
    pin = proof["audit"]
    audit_raw = (REPO / pin["path"]).read_bytes()
    require(len(audit_raw) == pin["bytes"] and digest(audit_raw) == pin["sha256"], "Q4_RETAINED_ACTUAL_AUDIT_DIFFERS")
    audit = json.loads(audit_raw)
    require(audit["archive"]["commit"] == proof["archive"]["commit"] and
            audit["archiveManifest"]["sha256"] == proof["archive"]["manifestSha256"] and
            audit["archiveManifest"]["bytes"] == proof["archive"]["manifestBytes"] and
            {k: audit["artifact"][k] for k in proof["artifact"]} == proof["artifact"] and
            audit["actualRunId"] == int(proof["githubRunId"]) and audit["appRevision"] == proof["appRevision"] and
            audit["artifact"]["workflow_run"]["head_sha"] == proof["appRevision"], "Q4_RETAINED_EXTERNAL_ARCHIVE_JOIN_DIFFERS")
    record = json.loads(primary._blob(store, proof["record"], r"ci/source-probe-runs/40188161705-1\.json"))
    require(all(type(record.get(k)) is type(proof[k]) and record[k] == proof[k]
                for k in ("githubRunId", "githubRunAttempt", "githubEventName", "githubRef", "appRevision")) and
            record["checkpointProfile"] == "source_probe" and record["contractSha256"] == descriptor["marketSha256"] and
            record["outcome"] == "completed_diagnostic" and record["executionCompleted"] is True and
            record["publication"] == {"published": False, "reason": "SOURCE_PROBE_DIAGNOSTIC_ONLY"} and
            record["apiFallback"] is False and record["facts"] == [] and
            all(record[k] is False for k in ("semanticAdmission", "coverageCredit")) and
            all(type(record[k]) is int and record[k] == 0 for k in primary.ZERO_FIELDS),
            "Q4_RETAINED_ACTUAL_OUTER_IDENTITY_DIFFERS")
    original = record["diagnostic"]
    plan_raw = primary._blob(store, proof["plan"])
    require(original["planReference"] == proof["plan"] and original["planCanonicalSha256"] == proof["planCanonicalSha256"],
            "Q4_RETAINED_ORIGINAL_PLAN_DIFFERS")
    replay = primary.verify_report(contract, store, plan_raw, original)
    require(replay["acceptedSamples"] == 0 and replay["proposalEvidenceComplete"] is False and
            original["executionCompleted"] is True and not original["budgetDenied"] and
            len(original["results"]) == 2, "Q4_RETAINED_ORIGINAL_HOLD_DIFFERS")
    normalized = primary.validate_plan(contract, store, plan_raw)
    return descriptor, original, normalized


def derive_report(contract, store, raw):
    """Read and recompute the exact two retained samples; never fetch or write."""
    descriptor, original, normalized = _validate(contract, store, raw)
    findings = []
    for index, row in enumerate(descriptor["sources"]):
        result, request, target = original["results"][index], original["requests"][index], normalized["targets"][index]
        require(row["resultIndex"] == index and row["sourceId"] == result["sourceId"] == target["sourceId"] and
                row["url"] == result["requestedUrl"] == result["finalUrl"] == target["url"] and
                row["observation"] == result["observation"] == request["observation"] and
                row["body"] == result["body"] and row["fetchedAt"] == result["fetchedAt"] and
                row["sample"] == normalized["plan"]["sources"][index]["sample"] and
                result["reason"] == "ContractError:BOUNDED_CANDIDATE_PRIMARY_CANONICAL_DIFFERS" and result["accepted"] is False,
                "Q4_RETAINED_SAMPLE_JOIN_DIFFERS")
        wrapper = json.loads(primary._blob(store, row["observation"]))
        require(wrapper["rawObservation"] == row["rawObservation"], "Q4_RETAINED_RAW_OBSERVATION_DIFFERS")
        observed = primary._read_observed(store, row["observation"], target)
        require(observed["status"] == "fetched" and type(observed["httpStatus"]) is int and observed["httpStatus"] == 200 and
                observed["requestedUrl"] == observed["finalUrl"] == row["url"] and observed["body"] == row["body"] and
                observed["fetchedAt"] == row["fetchedAt"] and
                instant(request["requestedAt"]) <= instant(observed["fetchedAt"]) <= instant(request["responseCheckedAt"]) and
                re.fullmatch(r"(?:text/html|application/xhtml\+xml)(?:\s*;\s*charset\s*=\s*(?:utf-8|\"utf-8\"))?\s*",
                             observed["contentType"], re.I), "Q4_RETAINED_PRIMARY_TRANSPORT_DIFFERS")
        shape = _shape(primary._body(store, row["body"]), row, target)
        findings.append({"sourceId": row["sourceId"], "url": row["url"], "body": row["body"],
                         "observation": row["observation"], "sourceRowSha256": target["sample"]["recordSha256"],
                         "fetchedAt": row["fetchedAt"], "primaryShape": shape})
    return {"schemaVersion": 1, "kind": KIND, "descriptorRawSha256": digest(raw),
            "descriptorCanonicalSha256": digest(descriptor), "contractSha256": digest(contract),
            "actualProof": copy.deepcopy(descriptor["actualProof"]), "originalReportAcceptedSamples": 0,
            "originalReportProposalEvidenceComplete": False, "originalCheckedAt": original["checkedAt"],
            "streams": [{"sourceId": s["sourceId"], "streamSha256": digest(s), "records": len(s["records"]),
                         "currentWindowRecords": len(s["currentWindowItems"]),
                         "initialBody": s["initialBody"], "initialObservation": s["initialObservation"],
                         "asOf": s["asOf"], "windowStart": s["windowStart"], "windowEnd": s["windowEnd"],
                         "timezone": s["timezone"], "declaredStreamComplete": s["declaredStreamComplete"]}
                        for s in normalized["streams"]], "retainedSamples": findings,
            "proposalEvidenceComplete": len(findings) == 2, "qualified": False, "qualifiedSources": 0,
            "sourceChecksCredited": 0, "modelCalls": 0, "facts": [], "semanticAdmission": False,
            "coverageCredit": False, "operationalIntake": False}


def verify_report(contract, store, raw, report):
    expected = derive_report(contract, store, raw)
    require(type(report) is dict and digest(report) == digest(expected), "Q4_RETAINED_REPLAYED_REPORT_DIFFERS")
    return {k: copy.deepcopy(expected[k]) for k in ("proposalEvidenceComplete", "originalReportAcceptedSamples",
            "qualified", "qualifiedSources", "sourceChecksCredited", "modelCalls", "facts", "semanticAdmission",
            "coverageCredit", "operationalIntake")}
