"""Closed retained PRN proposal proof. Read/get only; no operational registration."""
import copy
from datetime import datetime
import json
from pathlib import Path
import re

from contracts import digest, instant, require
import onboarding
from prnewswire_press_list import SOURCES, _Markup, _walk, _one, _text, _active, derive_stream
from q4_press_list import _object, _constant
from q4_primary_qualification import _PublicationMetadata
from discovery import IndexMarkup

REPO = Path(__file__).resolve().parents[3]
KIND = "prnewswire_retained_window_proposal_v1"
DESCRIPTOR_SHA256 = "034e555e8e7968dbb21b481412d767fb1e7c3406b57a9dfeed50f5c391304a7e"


def _json(raw):
    return json.loads(raw, object_pairs_hook=_object, parse_constant=_constant)


def _blob(store, ref, pattern=r"objects/[a-f0-9]{64}"):
    raw = onboarding._qualification_reference(store, ref, pattern)
    require(type(raw) is bytes and len(raw) == ref["bytes"] and digest(raw) == ref["sha256"],
            "PRN_RETAINED_REFERENCE_DIFFERS")
    return raw


def _day(value):
    require(isinstance(value, str) and re.match(r"^\d{4}-\d{2}-\d{2}(?:T|$)", value), "PRN_PRIMARY_DATE_INVALID")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        require(False, "PRN_PRIMARY_DATE_INVALID")


def _readable(node):
    if not _active(node):
        return ""
    return " ".join(_readable(c) if hasattr(c, "tag") else c for c in node.children)


class _PrimaryMarkup(_Markup):
    def handle_startendtag(self, tag, attrs):
        # Exact legacy Cato language-menu token, a sibling of the article heading.
        # The retained body pin prevents this exception becoming a generic DOM rule.
        if tag == "ul" and attrs == [("class", "dropdown-menu"), ("role", "menu"),
                                     ("aria-labelledby", "langauge-dropdown")] and self.stack[-1].tag == "div" and \
                self.stack[-1].classes == {"dropdown", "lang-switch"} and any(
                    n.tag == "header" and "release-header" in n.classes for n in self.stack):
            return IndexMarkup.handle_startendtag(self, tag, attrs)
        super().handle_startendtag(tag, attrs)


def primary_shape(raw, url, source_id, calendar_day):
    """Recompute the same-issuer primary template and supplied metadata without executing scripts."""
    require(source_id in SOURCES and type(raw) is bytes and 0 < len(raw) <= 2_000_000, "PRN_PRIMARY_SOURCE_OR_SIZE")
    text = raw.decode("utf-8", errors="strict")
    nodes = list(_walk(_PrimaryMarkup(text).root))
    head = _one([n for n in nodes if n.tag == "head"], "PRIMARY_HEAD")
    canonical = [n for n in nodes if n.tag == "link" and "canonical" in n.attrs.get("rel", "").split()]
    require(len(canonical) == 1 and canonical[0].parent is head and canonical[0].attrs.get("href") == url,
            "PRN_PRIMARY_CANONICAL_DIFFERS")
    main = _one([n for n in nodes if n.tag == "main"], "PRIMARY_MAIN")
    article = _one([n for n in nodes if n.tag == "article" and "news-release" in n.classes], "PRIMARY_ARTICLE")
    require(article.parent is main and main.attrs.get("id") == "main", "PRN_PRIMARY_ARTICLE_SCOPE")
    heading = _one([n for n in nodes if n.tag == "h1"], "PRIMARY_HEADING")
    header = _one([n for n in nodes if "release-header" in n.classes], "PRIMARY_HEADER")
    body = _one([n for n in nodes if "release-body" in n.classes], "PRIMARY_BODY")
    require(header.tag == "header" and body.tag == "section" and header.parent is article and
            body.parent is article and heading.inside(header), "PRN_PRIMARY_CONTAINER_JOIN_DIFFERS")
    require(not any(not _active(n) for n in _walk(heading)), "PRN_PRIMARY_HIDDEN_HEADING_CONTENT")
    readable = " ".join(_readable(body).split())
    require(len(readable) >= 100 and SOURCES[source_id][1] in readable and not any(
            marker in readable[:2000].lower() for marker in ("access denied", "verify you are human",
                                                           "request rate threshold exceeded")), "PRN_PRIMARY_UNREADABLE")
    scripts = [n for n in nodes if n.tag == "script" and
               n.attrs.get("type", "").strip().lower() == "application/ld+json"]
    require(len(scripts) == 1 and scripts[0].parent is head and scripts[0].closed, "PRN_PRIMARY_JSONLD_AMBIGUOUS")
    data = _json("".join(scripts[0].children))
    require(type(data) is dict and data.get("@type") == "NewsArticle" and data.get("headline") == _text(heading)
            and data.get("mainEntityOfPage") == {"@id": url}, "PRN_PRIMARY_SUPPLIED_IDENTITY_DIFFERS")
    require(_day(data.get("datePublished")) == calendar_day, "PRN_PRIMARY_WRITTEN_DAY_DIFFERS")
    # Modification is preserved independently; later modification is not a replacement publication date.
    if "dateModified" in data:
        _day(data["dateModified"])
    metadata = _PublicationMetadata(text).values
    require(bool(metadata) and all(_day(row["value"]) == calendar_day for row in metadata),
            "PRN_PRIMARY_PUBLICATION_METADATA_CONFLICT")
    return {"canonical": url, "heading": _text(heading), "readableCharacters": len(readable),
            "readableSha256": digest(readable.encode()), "suppliedJsonLd": data,
            "jsonLdScriptTextSha256": digest("".join(scripts[0].children).encode()),
            "publicationMetadata": metadata, "publicationCalendarDay": calendar_day,
            "indexTimezone": None, "publicationComparison": "written_calendar_day"}


def _external(descriptor):
    files = []
    for pin in descriptor["externalFiles"]:
        raw = (REPO / pin["path"]).read_bytes()
        require(len(raw) == pin["bytes"] and digest(raw) == pin["sha256"], "PRN_EXTERNAL_ACTUAL_PROOF_DIFFERS")
        files.append(_json(raw))
    current, actual, old, listing, primary = files
    archive = descriptor["archive"]
    require(current["verdict"] == actual["verdict"] == old["verdict"] == "PASS" and
            current["acknowledgedArchive"]["commit"] == actual["acknowledgedArchive"]["commit"] == archive["commit"] and
            actual["manifest"]["sha256"] == archive["manifestSha256"] and
            actual["manifest"]["bytes"] == archive["manifestBytes"] and
            actual["allEntriesVerified"] == archive["entries"] and
            actual["fullLegacyTraversalReplay"]["passed"] is True and old["fullLegacyTraversalReplay"]["passed"] is True,
            "PRN_EXTERNAL_ARCHIVE_OR_FULL_REPLAY_DIFFERS")
    return actual, old, listing, primary


def _original(contract, store, pin, audit):
    record = _json(_blob(store, pin["record"], r"ci/source-probe-runs/[0-9]+-1\.json"))
    require(record["githubRunId"] == pin["runId"] == str(audit["actualRunId"]) and
            record["appRevision"] == pin["appRevision"] == audit["appRevision"] and
            record["githubRunAttempt"] == 1 and record["githubEventName"] == "workflow_dispatch" and
            record["githubRef"] == "refs/heads/main" and record["checkpointProfile"] == "source_probe" and
            record["contractSha256"] == digest(contract) and record["executionCompleted"] is True and
            record["publication"] == {"published": False, "reason": "SOURCE_PROBE_DIAGNOSTIC_ONLY"} and
            record["apiFallback"] is False and all(record[k] is False for k in ("semanticAdmission", "coverageCredit")) and
            all(type(record[k]) is int and record[k] == 0 for k in ("qualifiedSources", "sourceChecksCredited", "modelCalls")),
            "PRN_ORIGINAL_OUTER_IDENTITY_DIFFERS")
    diagnostic = record["diagnostic"]
    raw = _blob(store, pin["rawPlan"])
    require(diagnostic["qualification"]["plan"]["rawPlanReference"] == pin["rawPlan"] and
            digest(_json(raw)) == pin["planCanonicalSha256"], "PRN_ORIGINAL_PLAN_DIFFERS")
    checked = onboarding._validate_legacy_qualification_probe_plan(contract, store,
        diagnostic["qualification"]["plan"]["path"], raw=raw, plan=_json(raw))
    require(checked == {k: v for k, v in diagnostic["qualification"]["plan"].items() if k != "rawPlanReference"},
            "PRN_ORIGINAL_FULL_PLAN_REPLAY_DIFFERS")
    sources = {s["id"]: s for s in contract["sources"]}
    observed = []
    for index, row in enumerate(diagnostic["qualification"]["targets"]):
        proof = {"observation": row["observation"], "priorPlanReference": pin["rawPlan"],
                 "priorPlanRawSha256": digest(raw), "priorPlanCanonicalSha256": pin["planCanonicalSha256"],
                 "priorTargetIndex": index, "priorTargetId": row["targetId"], "priorTargetSha256": digest(row),
                 "fetchedAt": _json(_blob(store, row["observation"]))["fetchedAt"]}
        value = onboarding._qualification_explicit_observation(record, proof, sources[row["sourceId"]], contract, store)
        require(value["status"] == "fetched" and type(value["httpStatus"]) is int and value["httpStatus"] == 200,
                "PRN_ORIGINAL_TARGET_NOT_ACTUAL_200")
        _blob(store, value["body"])
        observed.append(value)
    return record, observed


def _chain(store, pin, as_of):
    chain = [_json(_blob(store, ref, r"observations/[a-f0-9]{64}\.json")) for ref in pin["reuseChain"]]
    require(pin["reuseChain"][0] == pin["latest"] and pin["reuseChain"][-1] == pin["full200"],
            "PRN_PRIMARY_CHAIN_ENDPOINT_DIFFERS")
    for index, observed in enumerate(chain):
        require(observed["sourceId"] == pin["sourceId"] and
                observed["requestedUrl"] == observed["finalUrl"] == pin["url"] and
                observed["body"] == pin["body"] and pin["reuseChain"][index]["key"] ==
                    "observations/" + observed["observationId"] + ".json" and
                re.fullmatch(r"text/html;\s*charset=utf-8", observed["contentType"], re.I),
                "PRN_PRIMARY_EXACT_TRANSPORT_JOIN_DIFFERS")
        require(instant(observed["fetchedAt"]) <= instant(as_of), "PRN_PRIMARY_CLOCK_AFTER_ASOF")
        if index + 1 < len(chain):
            require(observed["status"] == "not_modified" and type(observed["httpStatus"]) is int and
                    observed["httpStatus"] == 304 and observed["reusesObservationId"] == chain[index + 1]["observationId"] and
                    instant(chain[index + 1]["fetchedAt"]) <= instant(observed["fetchedAt"]), "PRN_PRIMARY_REUSE_CHAIN_DIFFERS")
        else:
            require(observed["status"] == "fetched" and type(observed["httpStatus"]) is int and observed["httpStatus"] == 200 and
                    observed["fetchedAt"] == pin["originalFetchedAt"], "PRN_PRIMARY_FULL_BODY_ORIGIN_DIFFERS")
    return chain


def _primary(store, row, stream, inspection):
    pin = row["primary"]
    matching = [r for r in stream["records"] if r["url"] == pin["url"]]
    require(len(matching) == 1, "PRN_PRIMARY_NOT_IN_EXACT_ISSUER_INVENTORY")
    chain = _chain(store, pin, stream["asOf"])
    shape = primary_shape(_blob(store, pin["body"]), pin["url"], row["sourceId"], matching[0]["calendarDay"])
    actual = next(r for r in inspection["rows"] if r["sourceId"] == pin["sourceId"])
    require(actual["actual304To200ReuseChain"] == chain and actual["full200Observation"] == chain[-1] and
            actual["indexCardWrittenDates"] == [matching[0]["dateLiteral"]] and actual["writtenCalendarDayJoin"] is True,
            "PRN_PRIMARY_EXTERNAL_ORIGINAL_JOIN_DIFFERS")
    return {"sourceId": pin["sourceId"], "url": pin["url"], "body": pin["body"], "shape": shape,
            "originalFull200FetchedAt": chain[-1]["fetchedAt"], "latestRevalidationAt": chain[0]["fetchedAt"],
            "originalReuseChain": chain, "noClockRenewal": True}


def derive_report(contract, store, raw):
    """Only recompute the exact retained proposal. The store needs read/get, never a writer."""
    require(type(raw) is bytes and 0 < len(raw) <= 100_000, "PRN_DESCRIPTOR_SIZE_INVALID")
    descriptor = _json(raw)
    require(digest(descriptor) == DESCRIPTOR_SHA256 and digest(contract) == descriptor["marketSha256"],
            "PRN_EXACT_DESCRIPTOR_AND_ORIGINAL_H_REQUIRED")
    actual, old, listing, primary = _external(descriptor)
    runs = {}
    for pin, audit in zip(descriptor["originalRuns"], (old, actual)):
        runs[pin["runId"]] = _original(contract, store, pin, audit)
    require(descriptor["asOf"] == runs["40193925490"][0]["diagnostic"]["checkedAt"], "PRN_ORIGINAL_ASOF_DIFFERS")
    streams, samples = [], []
    for row in descriptor["sources"]:
        source = next(s for s in contract["sources"] if s["id"] == row["sourceId"])
        require(digest(source) == row["originalSourceSha256"] and source["registration"] == "candidate" and
                source["family"] == "release_distribution", "PRN_ORIGINAL_SOURCE_ROLE_DIFFERS")
        pages, transports = [], []
        for page in row["pages"]:
            record, observations = runs[page["runId"]]
            result = record["diagnostic"]["qualification"]["targets"][page["resultIndex"]]
            observed = observations[page["resultIndex"]]
            require(result["sourceId"] == row["sourceId"] and result["targetId"] == page["targetId"] and
                    digest(result) == page["targetSha256"] and result["url"] == observed["requestedUrl"] ==
                    observed["finalUrl"] == page["url"] and result["observation"] == page["observation"] and
                    observed["body"] == page["body"] and observed["fetchedAt"] == page["fetchedAt"] and
                    re.fullmatch(r"text/html;\s*charset=utf-8", observed["contentType"], re.I),
                    "PRN_PAGE_EXACT_SOURCE_BODY_CLOCK_JOIN_DIFFERS")
            pages.append({"url": page["url"], "body": _blob(store, page["body"])})
            transports.append({"url": page["url"], "observation": page["observation"], "body": page["body"],
                               "originalFetchedAt": page["fetchedAt"], "originalRunId": page["runId"]})
        stream = derive_stream(row["sourceId"], pages, descriptor["asOf"])
        expected = listing["groups"][row["sourceId"]]["inventoryUrls"]
        require(stream["items"] == expected and stream["dailyWindowComplete"] is True and
                stream["unresolvedDateItems"] == [], "PRN_KNOWN_INVENTORY_OR_DAILY_PROOF_DIFFERS")
        stream["knownSeedUrls"] = copy.deepcopy(source["seedEvidenceUrls"])
        stream["seedUrlsOutsideObservedList"] = sorted(set(source["seedEvidenceUrls"]) - set(stream["items"]))
        stream["sourceWideRecallProved"] = False
        stream["sourceScopeComplete"] = not stream["seedUrlsOutsideObservedList"]
        stream["qualificationReadiness"] = False
        stream["qualificationReadinessReason"] = "PENDING_SEPARATE_SCOPE_REVIEW_AND_NORMAL_INTAKE_ACTIVATION"
        stream["sourceScopeBasis"] = "known contract seed membership in the bounded observed issuer distribution list"
        gaps = []
        for pin in row["knownSeedsOutsideList"]:
            citation = next(s for s in contract["sources"] if s["id"] == pin["sourceId"])
            require(citation["supplierId"] == source["supplierId"] and citation["url"] == pin["url"] and
                    citation["registration"] == "verified" and pin["url"] in stream["seedUrlsOutsideObservedList"],
                    "PRN_KNOWN_SEED_SOURCE_JOIN_DIFFERS")
            chain = _chain(store, pin, descriptor["asOf"])
            shape = primary_shape(_blob(store, pin["body"]), pin["url"], row["sourceId"], pin["publicationCalendarDay"])
            gaps.append({"url": pin["url"], "sourceId": pin["sourceId"], "shape": shape,
                         "body": pin["body"], "originalFull200FetchedAt": pin["originalFetchedAt"],
                         "originalReuseChain": chain, "presentInObservedList": False,
                         "calendarWindowState": "older_calendar_day" if pin["publicationCalendarDay"] < stream["windowStart"]
                             else "unresolved_known_seed_scope_gap"})
        require(sorted(g["url"] for g in gaps) == stream["seedUrlsOutsideObservedList"], "PRN_KNOWN_SEED_GAP_OMITTED")
        stream["knownSeedsOutsideObservedList"] = gaps
        stream["knownEvidenceUnion"] = sorted(set(stream["items"]) | set(source["seedEvidenceUrls"]))
        stream["originalTransports"] = transports
        streams.append(stream)
        samples.append(_primary(store, row, stream, primary))
    return {"schemaVersion": 1, "kind": KIND, "descriptorRawSha256": digest(raw),
            "descriptorCanonicalSha256": digest(descriptor), "originalContractSha256": digest(contract),
            "archive": copy.deepcopy(descriptor["archive"]), "originalAsOf": descriptor["asOf"],
            "originalRuns": copy.deepcopy(descriptor["originalRuns"]), "streams": streams, "primarySamples": samples,
            "proposalEvidenceComplete": True, "qualified": False, "qualifiedSources": 0, "sourceChecksCredited": 0,
            "semanticAdmission": False, "coverageCredit": False, "operationalIntake": False,
            "modelCalls": 0, "facts": []}


def verify_report(contract, store, raw, report):
    expected = derive_report(contract, store, raw)
    require(type(report) is dict and digest(report) == digest(expected), "PRN_REPLAYED_PROPOSAL_REPORT_DIFFERS")
    return {k: copy.deepcopy(expected[k]) for k in ("proposalEvidenceComplete", "qualified", "qualifiedSources",
            "sourceChecksCredited", "semanticAdmission", "coverageCredit", "operationalIntake", "modelCalls", "facts")}
