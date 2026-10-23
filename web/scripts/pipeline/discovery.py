"""Source discovery with explicit pagination completeness, never empty=success."""
import json
import gzip
import io
import re
import zlib
from datetime import date, datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from contracts import require, instant, utcnow


MAX_DISCOVERY_BYTES = 32_000_000
ORCA_HTML_MODE = "orca-news-pagination-v1"


def decoded_discovery_body(body):
    """A bounded parsing view; callers retain the original archived object."""
    if body.startswith(b"\x1f\x8b"):
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(body)) as compressed:
                body = compressed.read(MAX_DISCOVERY_BYTES + 1)
        except (OSError, EOFError, zlib.error) as exc:
            raise ValueError("Invalid compressed discovery body") from exc
    require(len(body) <= MAX_DISCOVERY_BYTES, "Decoded discovery body exceeds byte budget")
    return body


class IndexNode:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children = []
        self.closed = False

    @property
    def classes(self):
        return set(self.attrs.get("class", "").split())

    def walk(self):
        if self.tag in ("script", "style", "template", "noscript"):
            return
        yield self
        for child in self.children:
            if isinstance(child, IndexNode):
                yield from child.walk()

    @property
    def text(self):
        if self.tag in ("script", "style", "template", "noscript"):
            return ""
        return " ".join(c.text if isinstance(c, IndexNode) else c for c in self.children)

    def inside(self, ancestor):
        parent = self.parent
        while parent:
            if parent is ancestor:
                return True
            parent = parent.parent
        return False


class IndexMarkup(HTMLParser):
    """Only structural HTML is inspected; scripts and templates never supply cards."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = IndexNode("document")
        self.stack = [self.root]
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        require(len(self.stack) <= 256, "Discovery markup nesting exceeds bound")
        node = IndexNode(tag, attrs, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)
        else:
            node.closed = True

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1, 0, -1):
            if self.stack[index].tag == tag:
                self.stack[index].closed = True
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def orca_index_number(url):
    parsed = urlsplit(url)
    require(parsed.scheme == "https" and parsed.netloc == "orca.security" and not parsed.query and not parsed.fragment,
            "Unsafe Orca index destination")
    match = re.fullmatch(r"/resources/news/(?:page/([1-9]\d*)/)?", parsed.path)
    require(match is not None, "Unexpected Orca index path")
    return int(match.group(1) or 1)


def orca_index(source, url, body, highest_page):
    """Explicit candidate adapter for the archived Orca newsroom structure."""
    require(source["id"] == "orca:official:1" and source["supplierId"] == "orca" and
            source["family"] == "official_announcements" and source["allowedHosts"] == ["orca.security"] and
            source["url"] == "https://orca.security/resources/news/" and 1 <= source["maxPages"] <= 60,
            "Orca HTML mode requires its exact supplier/source binding")
    current_page = orca_index_number(url)
    nodes = list(IndexMarkup(body.decode("utf8", errors="strict")).root.walk())

    def one(values, label):
        require(len(values) == 1, "Missing or ambiguous Orca " + label)
        require(values[0].closed, "Unclosed Orca " + label)
        return values[0]

    head = one([n for n in nodes if n.tag == "head"], "head")
    newsroom = one([n for n in nodes if "newsroom-posts" in n.classes], "newsroom")
    listing = one([n for n in nodes if "newsroom-posts-listing" in n.classes and n.inside(newsroom)], "listing")
    cards_region = one([n for n in nodes if "orca-posts-container-newsroom" in n.classes and n.inside(listing)], "card container")
    pagination = one([n for n in nodes if {"orca-pagination", "archive-posts-results__show-more"} <= n.classes], "pagination")
    require(pagination.inside(newsroom), "Orca pagination outside newsroom")
    page_nodes = list(pagination.walk())
    marker = one([n for n in page_nodes if n.tag == "span" and {"page-numbers", "current"} <= n.classes and
                  n.attrs.get("aria-current") == "page"], "current page marker")
    require(marker.text.strip().isdigit() and int(marker.text.strip()) == current_page, "Orca current page mismatch")
    require(not any(n.tag in ("button", "form", "select") for n in page_nodes), "Unknown Orca pagination control")
    next_links = [n for n in nodes if n.tag == "link" and "next" in n.attrs.get("rel", "").split()]
    require(all(n.inside(head) and n.attrs.get("href") for n in next_links), "Unknown Orca head-next control")
    require(all(n.inside(pagination) for n in nodes if n.tag == "a" and {"next", "page-numbers"} <= n.classes),
            "Orca next control outside pagination")
    head_next = {urljoin(url, n.attrs["href"]) for n in next_links}
    class_next, numbered, dots = set(), {current_page}, False
    for node in page_nodes:
        if "dots" in node.classes:
            dots = True
        if node.tag != "a":
            continue
        require("page-numbers" in node.classes and node.attrs.get("href"), "Unknown Orca pagination anchor")
        target = urljoin(url, node.attrs["href"])
        number = orca_index_number(target)
        numbered.add(number)
        if "next" in node.classes:
            class_next.add(target)
        elif "prev" in node.classes:
            require(number == current_page - 1, "Unexpected Orca previous page")
        else:
            require(node.text.strip().isdigit() and int(node.text.strip()) == number, "Orca numbered page mismatch")
    require(head_next == class_next and len(head_next) <= 1, "Missing or conflicting Orca next controls")
    highest_page = max(highest_page, *numbered)
    next_url = next(iter(head_next), None)
    if next_url:
        require(orca_index_number(next_url) == current_page + 1, "Orca pagination loop or skipped page")
    else:
        require(not dots and current_page == highest_page, "Unproved Orca terminal page")

    cards = [n for n in nodes if n.tag == "div" and {"clickable-card", "horizontal-post-card"} <= n.classes and n.inside(cards_region)]
    require(bool(cards), "Orca listing has no recognized static cards")
    require(all(child in cards if isinstance(child, IndexNode) else not child.strip() for child in cards_region.children),
            "Unknown Orca card-container content")
    featured_regions = [n for n in nodes if "newsroom-listing-featured" in n.classes]
    require(len(featured_regions) <= 1, "Ambiguous Orca featured region")
    if featured_regions:
        cards += [n for n in nodes if n.tag == "article" and {"clickable-card", "post-card", "post-card--featured"} <= n.classes and n.inside(featured_regions[0])]
    items, dates = set(), {}
    for card in cards:
        require(card.closed, "Unclosed Orca card")
        card_nodes = list(card.walk())
        category = one([n for n in card_nodes if "post-card__category" in n.classes], "card category")
        label = " ".join(category.text.split())
        require(label in ("News", "Press Releases"), "Unknown Orca card category")
        title = one([n for n in card_nodes if n.tag == "h2" and "post-card__title" in n.classes], "release title")
        link = one([n for n in title.walk() if n.tag == "a" and n.attrs.get("href")], "release title link")
        require(bool(link.text.strip()), "Empty Orca card title")
        date_node = one([n for n in card_nodes if "post-card__date" in n.classes], "card date")
        value = datetime.strptime(" ".join(date_node.text.split()), "%b %d, %Y").date().isoformat()
        if label == "News":
            continue
        target = urljoin(url, link.attrs["href"])
        parsed = urlsplit(target)
        require(parsed.scheme == "https" and parsed.netloc == "orca.security" and not parsed.query and not parsed.fragment and
                re.fullmatch(r"/resources/press-releases/[A-Za-z0-9_-]+/", parsed.path), "Unsafe Orca release card")
        if card.attrs.get("data-url"):
            require(urljoin(url, card.attrs["data-url"]) == target, "Orca card URL disagreement")
        require(target not in dates or dates[target] == value, "Conflicting Orca release dates")
        items.add(target)
        dates[target] = value
    return {"items": items, "dates": dates, "next": next_url, "highestPage": highest_page}


def barracuda_shell(url, body):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "www.barracuda.com" or parsed.path != "/company/news":
        return None
    nodes = list(IndexMarkup(body.decode("utf8", errors="strict")).root.walk())
    components = [n for n in nodes if n.attrs.get("data-cmp-is") == "NewsRoom" and "cmp-news-room" in n.classes]
    containers = [n for n in nodes if n.attrs.get("data-cmp-hook-news-room") == "cardsContainer" and any(n.inside(c) for c in components)]
    endpoint = "https://www.barracuda.com/content/barracuda-corp/us/en/company/news/jcr:content/root/container/container/news_room.news_room.json"
    if len(components) == len(containers) == 1 and urljoin(url, containers[0].attrs.get("data-panel-endpoint", "")) == endpoint:
        return {"reason": "BARRACUDA_NEWSROOM_DATA_REQUIRED", "requiredEndpoints": [endpoint]}
    return {"reason": "BARRACUDA_NEWSROOM_LAYOUT_UNVERIFIED", "requiredEndpoints": []}


def discover_regulatory_index(source, request):
    """Traverse an explicitly bound issuer index without producing market facts."""
    from regulatory import validate_index_source
    observations, items, dates, seen = [], set(), {}, set()
    def result(complete, reason=None, **details):
        return {"complete": complete, "items": sorted(items), "itemDates": dates,
                "observations": observations, "reason": reason, **details}
    try:
        validate_index_source(source)
        checked = instant(source.get("checkedAt", utcnow())).astimezone(timezone.utc)
        cutoff = (checked - timedelta(days=source.get("lookbackDays", 365))).date().isoformat()
        queue = [source["url"]]
        while queue:
            require(len(seen) < source["maxPages"], "PAGINATION_BUDGET_EXHAUSTED")
            url = queue.pop(0)
            require(url not in seen, "Duplicate SEC index continuation")
            seen.add(url)
            observation, body = request(url)
            observations.append(observation)
            if observation.get("status") not in ("fetched", "not_modified"):
                return result(False, observation.get("errorCode", "SEC_INDEX_FETCH_FAILED"))
            require(observation.get("requestedUrl") == url and observation.get("finalUrl", url) == url,
                    "SEC index response URL differs")
            value = json.loads(decoded_discovery_body(body))
            require(isinstance(value, dict), "SEC index response must be an object")
            if url == source["url"]:
                issuer = source["regulatoryIssuer"]
                cik = value.get("cik")
                require((type(cik) is int or isinstance(cik, str) and re.fullmatch(r"\d{1,10}", cik)) and
                        str(cik).zfill(10) == issuer["cik"] and value.get("name") == issuer["legalName"],
                        "SEC index initial issuer CIK/name differs")
                filings = value.get("filings")
                require(isinstance(filings, dict) and isinstance(filings.get("files"), list), "SEC history metadata missing")
                recent = filings.get("recent")
                names = set()
                for archive in filings["files"]:
                    require(isinstance(archive, dict) and set(archive) == {"name", "filingCount", "filingFrom", "filingTo"},
                            "SEC older index metadata schema differs")
                    name = archive["name"]
                    require(isinstance(name, str) and re.fullmatch(r"CIK" + issuer["cik"] + r"-submissions-\d{3}\.json", name),
                            "Unsafe SEC older index filename or wrong issuer")
                    require(name not in names, "Duplicate SEC older index metadata")
                    names.add(name)
                    first, last = date.fromisoformat(archive["filingFrom"]), date.fromisoformat(archive["filingTo"])
                    require(first <= last <= checked.date() and type(archive["filingCount"]) is int and archive["filingCount"] > 0,
                            "SEC older index date/count boundaries invalid")
                    if last.isoformat() >= cutoff:
                        queue.append(urljoin(source["url"], name))
            else:
                recent = value
            fields = {"accessionNumber", "filingDate", "reportDate", "acceptanceDateTime", "act", "form",
                      "fileNumber", "filmNumber", "items", "size", "isXBRL", "isInlineXBRL", "primaryDocument", "primaryDocDescription"}
            require(isinstance(recent, dict) and fields.issubset(recent) and
                    all(isinstance(column, list) for column in recent.values()),
                    "SEC filing index arrays missing")
            require(all(len(column) == len(recent["accessionNumber"]) for column in recent.values()),
                    "SEC filing index array lengths differ")
            for accession, filed in zip(recent["accessionNumber"], recent["filingDate"]):
                require(isinstance(accession, str) and re.fullmatch(r"\d{10}-\d{2}-\d{6}", accession), "Unsafe SEC accession")
                day = date.fromisoformat(filed).isoformat()
                require(day <= checked.date().isoformat(), "Future SEC index filing date")
                if day >= cutoff:
                    require(accession not in dates or dates[accession] == day, "Conflicting SEC accession date")
                    items.add(accession)
                    dates[accession] = day
        return result(True)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        return result(False, "SEC_INDEX_INCOMPLETE", detail=str(exc)[:160])


class Page(HTMLParser):
    def __init__(self, html, source_url=None):
        super().__init__(convert_charrefs=True)
        self.source_url = source_url
        source = urlsplit(source_url or '')
        self.esentire_scope = source.scheme == 'https' and source.hostname == 'www.esentire.com' and source.path.startswith('/news-releases/') and bool(source.path.removeprefix('/news-releases/')) and not source.query and not source.fragment and not source.username and source.port in (None, 443)
        self.canonicals, self.webpage_nodes = [], []
        self.scoped_articles, self.scoped_article_text = 0, []
        self.scoped_extraction, self.publication_ambiguous = False, False
        self.links, self.feeds, self.text, self.published = [], [], [], None
        self.regions, self.region_text = [], {"article": [], "main": []}
        self.json_ld, self.json_parts, self.json_dates, self.meta_published = False, [], set(), False
        self.time_dates, self.published_from_time = set(), False
        self.skip = 0
        self.feed(html)
        self._finish_scoped_publication()
        # A labeled article publication date is usable metadata. An arbitrary
        # event time, modified date or a multi-entry listing is not.
        if not self.publication_ambiguous and not self.published and not self.json_dates and len(self.time_dates) == 1:
            self.published = next(iter(self.time_dates))
            self.published_from_time = True

    def _finish_scoped_publication(self):
        if not self.esentire_scope or not self.scoped_articles:
            return
        # This exact archived source layout has no semantic article/main element.
        # Scope the body even when its publication metadata remains conflicting.
        self.scoped_extraction = True
        matching = [node for node in self.webpage_nodes if node.get('url') == self.source_url and node.get('mainEntityOfPage') == self.source_url]
        self.publication_ambiguous = True
        if self.canonicals != [self.source_url] or len(self.webpage_nodes) != 1 or len(matching) != 1 or self.scoped_articles != 1:
            self.published = None
            return
        value = matching[0].get('datePublished')
        try:
            published = instant(value)
            require(published.date() <= date.today(), 'Future publication date')
        except (ValueError, TypeError):
            self.published = None
            return
        article = re.sub(r'\s+', ' ', ' '.join(self.scoped_article_text)).strip()
        dateline = re.search(r'^[^.!?]{0,100}?\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b', article)
        if dateline:
            from datetime import datetime
            try:
                day = datetime.strptime(dateline.group(1).replace(',', ''), '%B %d %Y').date().isoformat()
            except ValueError:
                self.published = None
                return
            if day != value[:10]:
                self.published = None
                return
        other_dates = self.json_dates | ({self.published} if self.published else set())
        if any(item[:10] != value[:10] for item in other_dates):
            self.published = None
            return
        self.published = value
        self.publication_ambiguous = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.regions = [(t, r, depth + (t == tag)) for t, r, depth in self.regions]
        region = tag if tag in ("article", "main") else "main" if a.get("role") == "main" else None
        if self.esentire_scope and 'BlogBody__Content' in a.get('class', '').split():
            self.scoped_articles += 1
            self.regions.append((tag, 'scoped_article', 1))
        if region:
            self.regions.append((tag, region, 1))
        # This explicit press-release label is verified against archived
        # Mimecast pages. Generic post-date classes can belong to sidebar cards.
        publication_classes = {'press-release-details__date'}
        if publication_classes.intersection(a.get('class', '').split()):
            self.regions.append((tag, 'publication', 1))
        regions = {r for _, r, _ in self.regions}
        if tag == 'time' and (('article' in regions and 'datePublished' in a.get('itemprop', '').split()) or
                             ('publication' in regions and bool(regions & {'main', 'article'}))):
            value = a.get('datetime', '')
            if re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:T.*)?', value):
                try:
                    self.time_dates.add(date.fromisoformat(value[:10]).isoformat())
                except ValueError:
                    pass
        if tag == "script" and a.get("type") == "application/ld+json":
            self.json_ld, self.json_parts = True, []
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if tag == "a" and a.get("href"):
            self.links.append({"url": a["href"], "next": "next" in a.get("rel", "").split()})
        if tag == "link" and a.get("href") and a.get("type", "") in ("application/rss+xml", "application/atom+xml"):
            self.feeds.append(a["href"])
        if tag == 'link' and 'canonical' in a.get('rel', '').split() and a.get('href'):
            self.canonicals.append(a['href'])
        if tag == "meta" and a.get("property") in ("article:published_time", "datePublished"):
            self.published = a.get("content")
            self.meta_published = bool(self.published)

    def handle_endtag(self, tag):
        if tag == "script" and self.json_ld:
            self.json_ld = False
            try:
                value = json.loads("".join(self.json_parts))
                def dates(item):
                    if isinstance(item, list):
                        for entry in item: dates(entry)
                    elif isinstance(item, dict):
                        types = item.get("@type", [])
                        types = [types] if isinstance(types, str) else types
                        if self.esentire_scope and 'WebPage' in types:
                            self.webpage_nodes.append(item)
                        if any(t in ("Article", "NewsArticle", "BlogPosting", "PressRelease") for t in types):
                            date = item.get("datePublished", "")
                            if isinstance(date, str) and re.match(r"^\d{4}-\d{2}-\d{2}", date): self.json_dates.add(date)
                        if "@graph" in item: dates(item["@graph"])
                dates(value)
                if not self.meta_published:
                    self.published = next(iter(self.json_dates)) if len(self.json_dates) == 1 else None
            except (ValueError, TypeError):
                pass
        for index in range(len(self.regions)-1, -1, -1):
            if self.regions[index][0] == tag:
                t, r, depth = self.regions[index]
                if depth == 1:
                    self.regions.pop(index)
                else:
                    self.regions[index] = (t, r, depth-1)
        if tag in ("script", "style", "noscript"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if self.json_ld and sum(map(len, self.json_parts)) + len(data) <= 100_000:
            self.json_parts.append(data)
        if not self.skip:
            self.text.append(data)
            if any(region == 'scoped_article' for _, region, _ in self.regions):
                self.scoped_article_text.append(data)
            for region in {region for _, region, _ in self.regions if region in self.region_text}:
                self.region_text[region].append(data)

    @property
    def readable(self):
        if self.scoped_extraction and self.scoped_articles == 1:
            return re.sub(r'\s+', ' ', ' '.join(self.scoped_article_text)).strip()
        for region in ("article", "main"):
            text = re.sub(r"\s+", " ", " ".join(self.region_text[region])).strip()
            if len(text) >= 100:
                return text
        return re.sub(r"\s+", " ", " ".join(self.text)).strip()


def scoped(url, source):
    p = urlsplit(url)
    return p.scheme == "https" and p.hostname in source["allowedHosts"] and any(p.path.startswith(prefix) for prefix in source["scopePrefixes"])


def xml_links(body, base):
    body = decoded_discovery_body(body)
    require(b"<!DOCTYPE" not in body.upper() and b"<!ENTITY" not in body.upper(), "XML entity declarations prohibited")
    root = ET.fromstring(body)
    kind = root.tag.rsplit("}", 1)[-1]
    links, indexes, modified = [], [], {}
    if kind in ("urlset", "sitemapindex"):
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1] == "loc" and element.text:
                (indexes if kind == "sitemapindex" else links).append(urljoin(base, element.text.strip()))
        for entry in root:
            fields = {e.tag.rsplit("}", 1)[-1]: e.text for e in entry}
            if fields.get("loc") and fields.get("lastmod"):
                modified[urljoin(base, fields["loc"].strip())] = fields["lastmod"].strip()
    elif kind in ("rss", "feed"):
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1] == "link" and element.attrib.get("rel") == "next":
                require(bool(element.attrib.get("href")), "Malformed feed pagination")
                indexes.append(urljoin(base, element.attrib["href"]))
        for entry in root.iter():
            if entry.tag.rsplit("}", 1)[-1] not in ("item", "entry"):
                continue
            for element in entry:
                if element.tag.rsplit("}", 1)[-1] == "link":
                    value = element.attrib.get("href") or element.text
                    if value and element.attrib.get("rel", "alternate") == "alternate":
                        links.append(urljoin(base, value.strip()))
    else:
        raise ValueError("Unsupported XML discovery format")
    return {"kind": kind, "links": sorted(set(links)), "indexes": sorted(set(indexes)), "modified": modified}


def discover(source, request):
    """request(url) archives every response and returns an observation plus bytes."""
    if source["registration"] != "verified":
        return {"complete": False, "items": [], "observations": [], "reason": "SOURCE_BINDING_UNVERIFIED"}
    if source["kind"] == "sec_index":
        return discover_regulatory_index(source, request)
    queue, seen, items, observations, item_dates, item_modified = [source["url"]], set(), set(), [], {}, {}
    highest_orca_page = 1
    orca_mode = source.get("htmlCompleteness") == ORCA_HTML_MODE
    def incomplete(reason, **details):
        return {"complete": False, "items": sorted(items), "itemDates": item_dates,
                "itemModified": item_modified, "observations": observations, "reason": reason, **details}
    while queue:
        if len(seen) >= source["maxPages"]:
            return incomplete("PAGINATION_BUDGET_EXHAUSTED")
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            observation, body = request(url)
        except (OSError, ValueError):
            if not orca_mode:
                raise
            return incomplete("ORCA_INDEX_REQUEST_FAILED", missingUrl=url)
        observations.append(observation)
        if observation["status"] not in ("fetched", "not_modified"):
            return incomplete(observation.get("errorCode", "FETCH_FAILED"))
        if source["kind"] == "citation":
            require(len(body) > 0, "Empty citation response")
            continue
        if source["kind"] in ("sec_facts", "sec_submissions", "sec_documents"):
            value = json.loads(body)
            if source["kind"] == "sec_facts":
                require(isinstance(value.get("facts"), dict) and value.get("cik"), "Malformed SEC companyfacts response")
            else:
                recent = value.get("filings", {}).get("recent", value)
                require(isinstance(recent.get("accessionNumber"), list), "Malformed SEC submissions response")
                # Older submission pages must also be fetched to establish the full retained index.
                cutoff = (instant(source.get("checkedAt", utcnow())) - timedelta(days=source.get("lookbackDays", 365))).date().isoformat()
                for archive in value.get("filings", {}).get("files", []):
                    if source["kind"] == "sec_documents" and archive.get("filingTo", "9999") < cutoff:
                        continue
                    name = archive.get("name", "")
                    require(re.fullmatch(r"CIK\d+-submissions-\d+\.json", name) is not None, "Unexpected SEC index filename")
                    queue.append(urljoin(source["url"], name))
                if source["kind"] == "sec_documents":
                    cik = str(int(source["cik"]))
                    if "cik" in value:
                        require(str(int(value["cik"])) == cik, "SEC document index CIK mismatch")
                    for i, accession in enumerate(recent["accessionNumber"]):
                        if recent["filingDate"][i] < cutoff or recent["form"][i] not in ("10-K", "10-K/A", "10-Q", "10-Q/A", "8-K", "8-K/A", "NT 10-K", "NT 10-Q", "DEFM14A", "PREM14A", "25", "25-NSE", "20-F", "20-F/A", "6-K", "6-K/A"):
                            continue
                        primary = recent["primaryDocument"][i]
                        require(re.fullmatch(r"\d{10}-\d{2}-\d{6}", accession) and re.fullmatch(r"[A-Za-z0-9_.-]+", primary), "Unsafe SEC document path")
                        document_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}/{primary}"
                        items.add(document_url)
                        item_dates[document_url] = recent["filingDate"][i]
                else:
                    items.update(recent["accessionNumber"])
            continue
        try:
            body = decoded_discovery_body(body)
            if orca_mode:
                require(source["kind"] == "html_index", "Orca mode requires HTML index kind")
                parsed_index = orca_index(source, url, body, highest_orca_page)
                for target, value in parsed_index["dates"].items():
                    require(target not in item_dates or item_dates[target] == value, "Conflicting Orca dates across pages")
                items.update(parsed_index["items"])
                item_dates.update(parsed_index["dates"])
                # Explicit card publication is an index scheduling signature,
                # not semantic evidence of the event's effective date.
                item_modified.update(parsed_index["dates"])
                highest_orca_page = parsed_index["highestPage"]
                if parsed_index["next"]:
                    require(parsed_index["next"] not in seen, "Orca pagination loop")
                    queue.append(parsed_index["next"])
                continue
            shell = barracuda_shell(url, body)
            if shell:
                return incomplete(**shell)
        except ValueError as exc:
            if orca_mode:
                return incomplete("ORCA_INDEX_INCOMPLETE", detail=str(exc))
            raise
        content = body.lstrip()
        if content.startswith(b"<?xml") or re.match(br"<(rss|feed|urlset|sitemapindex)\b", content):
            parsed = xml_links(body, url)
            item_modified.update(parsed["modified"])
            for index in parsed["indexes"]:
                require(urlsplit(index).hostname in source["allowedHosts"], "Unapproved sitemap host")
                if index not in seen:
                    queue.append(index)
            items.update(item for item in parsed["links"] if scoped(item, source))
        else:
            require(source["kind"] == "html_index", "Discovery endpoint must be a validated feed, sitemap or HTML index")
            require(source.get("htmlCompleteness") == "rel-next-exhaustion-v1", "HTML completeness rule must be explicitly registered")
            page = Page(body.decode("utf8", errors="replace"))
            require(len(page.readable) > 60, "Empty or unreadable discovery page")
            for link in page.links:
                target = urljoin(url, link["url"]).split("#")[0]
                if link["next"]:
                    require(scoped(target, source), "Unapproved pagination destination")
                    if target not in seen:
                        queue.append(target)
                elif scoped(target, source) and target not in seen:
                    items.add(target)
    return {"complete": True, "items": sorted(items), "itemDates": item_dates, "itemModified": item_modified, "observations": observations, "reason": None}
