"""Pure, source-bound PR Newswire calendar-window evidence. No transport or credit."""
from datetime import datetime, timedelta, timezone
import re
from urllib.parse import urljoin

from contracts import digest, instant, require
from discovery import IndexMarkup, IndexNode

VERSION = "prnewswire-issuer-calendar-window-v1"
SOURCES = {
    "cato:official:1": ("cato-networks", "Cato Networks"),
    "chainguard:official:1": ("chainguard", "Chainguard"),
}
HOST = "https://www.prnewswire.com"
MAX_BYTES, MAX_PAGES, MAX_CARDS = 2_000_000, 8, 25
INERT = {"script", "style", "template", "noscript", "iframe", "object", "textarea", "xmp", "plaintext", "svg", "math"}
LANGUAGE_PATHS = {
    "cato:official:1": {"en-US": ("/news-releases/",), "il": ("/il/news-releases/",),
        "fr": ("/news-releases/", "/fr/communiques-de-presse/"), "de": ("/news-releases/",),
        "no": ("/news-releases/",), "fi": ("/news-releases/",), "sv": ("/news-releases/",),
        "nl": ("/nl/persberichten/",), "da": ("/news-releases/",)},
    "chainguard:official:1": {"en-US": ("/news-releases/",), "in": ("/in/news-releases/",)},
}


def _walk(node):
    yield node
    for child in node.children:
        if isinstance(child, IndexNode):
            yield from _walk(child)


def _active(node):
    while node:
        if node.tag in INERT or "hidden" in node.attrs or node.attrs.get("aria-hidden", "").lower() == "true" or re.search(
                r"display\s*:\s*none|visibility\s*:\s*hidden", node.attrs.get("style", ""), re.I):
            return False
        node = node.parent
    return True


class _Markup(IndexMarkup):
    def handle_starttag(self, tag, attrs):
        require(tag != "base", "PRN_BASE_FORBIDDEN")
        self.node_count = getattr(self, "node_count", 0) + 1
        require(self.node_count <= 50_000, "PRN_NODE_BOUND_EXCEEDED")
        require(len(attrs) == len(dict(attrs)), "PRN_DUPLICATE_ATTRIBUTES")
        super().handle_starttag(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        require(tag in self.VOID or tag in {"path", "circle", "rect", "polygon", "line", "polyline", "ellipse", "use"} and
                any(n.tag == "svg" for n in self.stack), "PRN_SELF_CLOSING_NONVOID")
        super().handle_startendtag(tag, attrs)


def _one(nodes, label):
    require(len(nodes) == 1 and nodes[0].closed and _active(nodes[0]), "PRN_" + label + "_AMBIGUOUS")
    return nodes[0]


def _text(node):
    return " ".join(node.text.split())


def _whitespace(node):
    require(all(not c.strip() for c in node.children if isinstance(c, str)), "PRN_UNKNOWN_CONTAINER_TEXT")


def _direct(node):
    return " ".join(" ".join(c for c in node.children if isinstance(c, str)).split())


def _path(node, ancestors):
    for tag, classes in ancestors:
        node = node.parent
        require(node is not None and node.tag == tag and set(classes) <= node.classes and node.closed and _active(node),
                "PRN_CONTAINER_PATH_DIFFERS")
    return node


def index_url(source_id, number=1, *, query_one=False):
    require(source_id in SOURCES and type(number) is int and 1 <= number <= MAX_PAGES, "PRN_SOURCE_OR_PAGE_INVALID")
    root = HOST + "/news/" + SOURCES[source_id][0] + "/"
    return root if number == 1 and not query_one else root + "?page=" + str(number) + "&pagesize=25"


def page_number(source_id, url, *, navigation=False):
    require(source_id in SOURCES and isinstance(url, str), "PRN_SOURCE_OR_URL_INVALID")
    if url == index_url(source_id):
        return 1
    for number in range(1 if navigation else 2, MAX_PAGES + 1):
        if url == index_url(source_id, number, query_one=True):
            return number
    require(False, "PRN_EXACT_INDEX_URL_REQUIRED")


def _detail(source_id, language, href):
    prefixes = LANGUAGE_PATHS[source_id].get(language, ())
    require(isinstance(href, str) and any(re.fullmatch(re.escape(prefix) + r"[A-Za-z0-9_.,~()-]+\.html", href)
                                        for prefix in prefixes),
            "PRN_DETAIL_URL_INVALID")
    return HOST + href


def _date(literal):
    if literal is None or not re.fullmatch(r"[A-Z][a-z]{2} \d{2}, \d{4}, \d{2}:\d{2} ET", literal):
        return None
    try:
        return datetime.strptime(literal, "%b %d, %Y, %H:%M ET")
    except ValueError:
        require(False, "PRN_IMPOSSIBLE_CALENDAR_DATE")


def _classify(records, as_of):
    day = instant(as_of).astimezone(timezone.utc).date()
    cutoff, tomorrow = day - timedelta(days=30), day + timedelta(days=1)
    current, older, future, unresolved, boundary, anomalies = [], [], [], [], [], []
    previous = None
    for row in records:
        stamp = _date(row["dateLiteral"])
        row["calendarDay"], row["timezone"] = stamp.date().isoformat() if stamp else None, None
        row["dateAnomaly"], row["boundaryAmbiguous"] = None, False
        if stamp is None:
            unresolved.append(row["url"])
            continue
        require(previous is None or stamp <= previous, "PRN_INCREASING_WRITTEN_DATE")
        previous = stamp
        date = stamp.date()
        if cutoff <= date <= day:
            current.append(row["url"])
        elif date < cutoff:
            older.append(row["url"])
        else:
            future.append(row["url"])
        if date in (cutoff, day, tomorrow):
            row["boundaryAmbiguous"] = True
            boundary.append(row["url"])
        if date > tomorrow:
            row["dateAnomaly"] = "FUTURE_PUBLICATION_CALENDAR_UNRESOLVED"
            anomalies.append({"url": row["url"], "reason": row["dateAnomaly"]})
    return {"windowStart": cutoff.isoformat(), "windowEnd": day.isoformat(), "datePrecision": "calendar_day",
            "timezone": None, "currentWindowItems": current, "historicalItems": older,
            "undeterminedWindowItems": future, "unresolvedDateItems": unresolved,
            "boundaryAmbiguousItems": boundary, "sourceDateAnomalies": anomalies,
            "olderBoundaryPresent": bool(older), "orderingProved": not unresolved,
            "olderBoundary": next((r for r in records if r["url"] in older), None)}


def parse_page(source_id, url, raw, as_of):
    """Inspect exactly one issuer page; preserve unresolved date rows without quiet credit."""
    number = page_number(source_id, url)
    require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES, "PRN_BODY_SIZE_INVALID")
    markup = _Markup(raw.decode("utf-8", errors="strict"))
    nodes = list(_walk(markup.root))
    require(len(nodes) <= 50_000, "PRN_NODE_BOUND_EXCEEDED")
    main = _one([n for n in nodes if n.tag == "main"], "MAIN")
    require(main.attrs.get("id") == "main" and main.attrs.get("role") == "main" and
            main.attrs.get("tabindex") == "-1" and main.classes == {"headline-listing"}, "PRN_MAIN_IDENTITY_DIFFERS")
    head = _one([n for n in nodes if n.tag == "head"], "HEAD")
    canonical = [n for n in nodes if n.tag == "link" and "canonical" in n.attrs.get("rel", "").lower().split()]
    require(len(canonical) == 1 and canonical[0].parent is head and
            canonical[0].attrs.get("href") == index_url(source_id) + ("?page=" + str(number) if number > 1 else ""),
            "PRN_INDEX_CANONICAL_DIFFERS")
    head_paging = [n for n in nodes if n.tag == "link" and
                   {"next", "prev"} & set(n.attrs.get("rel", "").lower().split())]
    h1 = _one([n for n in nodes if n.tag == "h1"], "ISSUER_H1")
    require(_path(h1, [("section", {"container"})]).parent is main and
            _direct(h1) == "News from " + SOURCES[source_id][1] and
            len([c for c in h1.children if isinstance(c, IndexNode)]) == 1 and
            h1.children[next(i for i, c in enumerate(h1.children) if isinstance(c, IndexNode))].tag == "small",
            "PRN_ISSUER_HEADING_DIFFERS")
    listing = _one([n for n in nodes if "card-list" in n.classes], "CARD_LIST")
    require(listing.tag == "div" and listing.classes == {"card-list", "card-list-hr", "nativo-section"} and
            _path(listing, [("div", {"col-md-8", "col-sm-12"}), ("div", {"row"}),
                            ("section", {"container"})]).parent is main, "PRN_LIST_CONTAINER_DIFFERS")
    latest = _one([n for n in nodes if n.tag == "h2" and "section-header" in n.classes], "LATEST")
    require(latest.parent is listing and _direct(latest) == "Latest" and
            len([c for c in latest.children if isinstance(c, IndexNode)]) == 1 and
            all(c.tag == "small" and c.closed and not _text(c) for c in latest.children if isinstance(c, IndexNode)),
            "PRN_LATEST_HEADING_DIFFERS")
    rows = [n for n in nodes if "newsCards" in n.classes]
    require(0 < len(rows) <= MAX_CARDS and all(n.parent is listing and n.tag == "div" and
            n.classes == {"row", "newsCards"} and n.attrs.get("lang") in LANGUAGE_PATHS[source_id] and n.closed and _active(n)
            for n in rows), "PRN_CARD_ROWS_INVALID")
    require(all(c in rows or c is latest for c in listing.children if isinstance(c, IndexNode)),
            "PRN_UNKNOWN_LIST_CHILD")
    _whitespace(listing)
    records, anchors, card_nodes = [], [], []
    for position, row in enumerate(rows):
        _whitespace(row)
        card = _one([c for c in row.children if isinstance(c, IndexNode)], "CARD")
        _whitespace(card)
        require(card.tag == "div" and card.classes in ({"card", "col-view"}, {"card", "col-sm-12"}) and
                card.attrs.get("role") == "group" and card.attrs.get("aria-label") == "News Release",
                "PRN_CARD_VARIANT_DIFFERS")
        descendants = list(_walk(card))
        require(all(n.closed and _active(n) for n in descendants) and
                not any(n.tag in {"button", "form", "select"} for n in descendants), "PRN_INERT_OR_HIDDEN_CARD")
        anchor = _one([n for n in descendants if n.tag == "a"], "CARD_LINK")
        require(anchor.parent is card and anchor.classes == {"newsreleaseconsolidatelink", "display-outline", "w-100"},
                "PRN_CARD_LINK_SCOPE_DIFFERS")
        heading = _one([n for n in descendants if n.tag == "h3"], "CARD_HEADING")
        require(heading.inside(anchor), "PRN_CARD_HEADING_OUTSIDE_LINK")
        dates = [n for n in descendants if n.tag == "small"]
        require(len(dates) <= 1 and all(n.parent is heading and not any(isinstance(c, IndexNode) for c in n.children) for n in dates), "PRN_CARD_DATE_AMBIGUOUS")
        spans = [n for n in heading.children if isinstance(n, IndexNode) and n.tag == "span"]
        require(len(spans) <= 1 and all(n.classes == {"langspan"} and n.attrs.get("lang") == row.attrs["lang"] and
                not any(isinstance(c, IndexNode) for c in n.children) for n in spans), "PRN_TITLE_LANGUAGE_DIFFERS")
        title = _text(spans[0]) if spans else _direct(heading)
        require(bool(title) and (not spans or not _direct(heading)) and
                [n for n in heading.children if isinstance(n, IndexNode)] == dates + spans,
                "PRN_CARD_TITLE_AMBIGUOUS")
        records.append({"sourceId": source_id, "pageNumber": number, "cardIndex": position,
                        "url": _detail(source_id, row.attrs["lang"], anchor.attrs.get("href")), "title": title,
                        "language": row.attrs["lang"],
                        "dateLiteral": _text(dates[0]) if dates else None})
        anchors.append(anchor)
        card_nodes.append(card)
    require([n for n in nodes if n.tag == "a" and "newsreleaseconsolidatelink" in n.classes] == anchors and
            [n for n in nodes if n.attrs.get("aria-label") == "News Release"] == card_nodes,
            "PRN_DECOY_CARD_OR_LINK")
    require(len({r["url"] for r in records}) == len(records), "PRN_DUPLICATE_DETAIL_URL")
    pager = _one([n for n in nodes if n.tag == "nav" and n.attrs.get("aria-label") == "pagination"], "PAGER")
    require(_path(pager, [("div", {"page-list", "pull-right"}), ("div", {"pagination-bar"}),
                         ("div", {"toolbar-container"}), ("div", {"col-sm-12"}), ("div", {"row"}),
                         ("section", {"container"})]).parent is main, "PRN_PAGER_CONTAINER_DIFFERS")
    ul = _one([c for c in pager.children if isinstance(c, IndexNode)], "PAGER_LIST")
    require(ul.tag == "ul" and ul.classes == {"pagination"} and
            [n for n in nodes if "pagination" in n.classes] == [ul], "PRN_PAGER_LIST_DIFFERS")
    _whitespace(pager); _whitespace(ul)
    controls, numbered, following, previous = [], [], [], []
    children = [c for c in ul.children if isinstance(c, IndexNode)]
    require(3 <= len(children) <= 7, "PRN_PAGER_CONTROL_BOUND")
    for index, li in enumerate(children):
        require(li.tag == "li" and li.closed and _active(li) and li.classes <= {"active", "disabled"},
                "PRN_PAGER_CONTROL_INVALID")
        _whitespace(li)
        link = _one([c for c in li.children if isinstance(c, IndexNode)], "PAGER_LINK")
        require(link.tag == "a" and len([n for n in _walk(li) if n.tag == "a"]) == 1,
                "PRN_PAGER_LINK_INVALID")
        label, href = _text(link), link.attrs.get("href")
        if index in (0, len(children) - 1):
            direction, expected, out = ("Previous", number - 1, previous) if index == 0 else ("Next", number + 1, following)
            require(link.attrs.get("aria-label") == direction and label == ("«" if index == 0 else "»") and
                    li.classes in (set(), {"disabled"}), "PRN_DIRECTION_CONTROL_DIFFERS")
            if "disabled" in li.classes:
                require(href is None and (index != 0 or number == 1), "PRN_DISABLED_CONTROL_HAS_TARGET")
                out.append(None)
            else:
                target = urljoin(url, href or "")
                require(href == "?page=" + str(expected) + "&pagesize=25" and
                        page_number(source_id, target, navigation=True) == expected, "PRN_DIRECTION_TARGET_DIFFERS")
                out.append(target)
        else:
            require(label.isascii() and label.isdecimal() and "disabled" not in li.classes and
                    not link.attrs.get("aria-label"), "PRN_NUMBER_CONTROL_INVALID")
            value = int(label)
            if "active" in li.classes:
                require(value == number and href is None, "PRN_ACTIVE_PAGE_DIFFERS")
            else:
                require(href == "?page=" + label + "&pagesize=25" and value != number and
                        page_number(source_id, urljoin(url, href), navigation=True) == value, "PRN_NUMBER_TARGET_DIFFERS")
            numbered.append(value)
        controls.append({"text": label, "classes": sorted(li.classes), "href": href})
    require(len(previous) == len(following) == 1 and
            sum("active" in n.classes for n in children) == 1 and
            numbered == list(range(min(numbered), max(numbered) + 1)) and number in numbered and
            (number != 1 or previous == [None]) and
            (following == [None] or number + 1 in numbered) and
            (following != [None] or number == max(numbered)) and
            (following == [None] or len(records) == MAX_CARDS), "PRN_PAGER_SEQUENCE_DIFFERS")
    require(not any(n.tag in {"button", "form", "select", "script"} for n in _walk(pager)),
            "PRN_UNKNOWN_PAGER_CONTROL")
    expected_head = {}
    if previous[0] is not None:
        expected_head["prev"] = index_url(source_id) + ("?page=" + str(number - 1) if number > 2 else "")
    if following[0] is not None:
        expected_head["next"] = index_url(source_id) + "?page=" + str(number + 1)
    require(len(head_paging) == len(expected_head) and all(
            n.parent is head and n.attrs.get("rel") in expected_head and
            n.attrs.get("href") == expected_head[n.attrs["rel"]] for n in head_paging) and
            {n.attrs["rel"] for n in head_paging} == set(expected_head), "PRN_HEAD_BODY_PAGING_CONFLICT")
    dates = _classify(records, as_of)
    return {"parserVersion": VERSION, "sourceId": source_id, "url": url, "pageNumber": number,
            "bodySha256": digest(raw), "bodyBytes": len(raw), "issuer": SOURCES[source_id][1],
            "publisherOrdering": "recognized_issuer_latest_nonincreasing_written_dates",
            "records": records, "items": [r["url"] for r in records], "asOf": as_of,
            "controls": controls, "next": following[0], "terminalProved": following == [None],
            "headPaginationMetadata": expected_head,
            "literalPaginationUrls": sorted({urljoin(url, c["href"]) for c in controls if c["href"]}), **dates}


def derive_stream(source_id, pages, as_of):
    """Prove an observed prefix's daily window; preserve its separate unknown older history."""
    require(type(pages) is list and 0 < len(pages) <= MAX_PAGES, "PRN_PAGE_INPUT_BOUND")
    parsed = []
    for index, page in enumerate(pages):
        require(type(page) is dict and set(page) == {"url", "body"}, "PRN_PAGE_INPUT_SCHEMA")
        require(page["url"] == index_url(source_id, index + 1) and
                (not parsed or parsed[-1]["next"] == page["url"]), "PRN_PAGE_GAP_OR_FALSE_TERMINAL")
        parsed.append(parse_page(source_id, page["url"], page["body"], as_of))
    records = [dict(r) for p in parsed for r in p["records"]]
    require(len({r["url"] for r in records}) == len(records), "PRN_DUPLICATE_OR_CONFLICTING_URL_ACROSS_PAGES")
    dates = _classify(records, as_of)
    complete = dates["orderingProved"] and dates["olderBoundaryPresent"]
    terminal = parsed[-1]["terminalProved"]
    observed = {p["url"] for p in parsed} | {index_url(source_id, 1, query_one=True)}
    pending = sorted({u for p in parsed for u in p["literalPaginationUrls"]} - observed)
    return {"schemaVersion": 1, "parserVersion": VERSION, "sourceId": source_id,
            "family": "release_distribution", "asOf": as_of, "pages": parsed, "records": records,
            "items": sorted(r["url"] for r in records), **dates, "dailyWindowComplete": complete,
            "historicalEnumerationComplete": terminal, "unknownOlderHistory": not terminal,
            "pendingLiteralPaginationUrls": pending,
            "currentWindowQuiet": complete and not dates["currentWindowItems"] and
                not dates["undeterminedWindowItems"] and not dates["unresolvedDateItems"],
            "orderingInferenceLimit": "recognized publisher issuer list; no universal website recall",
            "qualified": False, "qualifiedSources": 0, "sourceChecksCredited": 0,
            "semanticAdmission": False, "coverageCredit": False, "modelCalls": 0, "facts": [],
            "operationalIntake": False}
