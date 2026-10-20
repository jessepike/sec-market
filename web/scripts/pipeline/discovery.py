"""Source discovery with explicit pagination completeness, never empty=success."""
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from contracts import require


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.links, self.feeds, self.text, self.published = [], [], [], None
        self.skip = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if tag == "a" and a.get("href"):
            self.links.append({"url": a["href"], "next": "next" in a.get("rel", "").split()})
        if tag == "link" and a.get("href") and a.get("type", "") in ("application/rss+xml", "application/atom+xml"):
            self.feeds.append(a["href"])
        if tag == "meta" and a.get("property") in ("article:published_time", "datePublished"):
            self.published = a.get("content")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)

    @property
    def readable(self):
        return re.sub(r"\s+", " ", " ".join(self.text)).strip()


def scoped(url, source):
    p = urlsplit(url)
    return p.scheme == "https" and p.hostname in source["allowedHosts"] and any(p.path.startswith(prefix) for prefix in source["scopePrefixes"])


def xml_links(body, base):
    require(b"<!DOCTYPE" not in body.upper() and b"<!ENTITY" not in body.upper(), "XML entity declarations prohibited")
    root = ET.fromstring(body)
    kind = root.tag.rsplit("}", 1)[-1]
    links, indexes = [], []
    if kind in ("urlset", "sitemapindex"):
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1] == "loc" and element.text:
                (indexes if kind == "sitemapindex" else links).append(urljoin(base, element.text.strip()))
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
    return {"kind": kind, "links": sorted(set(links)), "indexes": sorted(set(indexes))}


def discover(source, request):
    """request(url) archives every response and returns an observation plus bytes."""
    if source["registration"] != "verified":
        return {"complete": False, "items": [], "observations": [], "reason": "SOURCE_BINDING_UNVERIFIED"}
    queue, seen, items, observations = [source["url"]], set(), set(), []
    while queue:
        if len(seen) >= source["maxPages"]:
            return {"complete": False, "items": sorted(items), "observations": observations, "reason": "PAGINATION_BUDGET_EXHAUSTED"}
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        observation, body = request(url)
        observations.append(observation)
        if observation["status"] not in ("fetched", "not_modified"):
            return {"complete": False, "items": sorted(items), "observations": observations, "reason": observation.get("errorCode", "FETCH_FAILED")}
        if source["kind"] == "citation":
            require(len(body) > 0, "Empty citation response")
            continue
        if source["kind"] in ("sec_facts", "sec_submissions"):
            value = json.loads(body)
            if source["kind"] == "sec_facts":
                require(isinstance(value.get("facts"), dict) and value.get("cik"), "Malformed SEC companyfacts response")
            else:
                recent = value.get("filings", {}).get("recent", value)
                require(isinstance(recent.get("accessionNumber"), list), "Malformed SEC submissions response")
                # Older submission pages must also be fetched to establish the full retained index.
                for archive in value.get("filings", {}).get("files", []):
                    name = archive.get("name", "")
                    require(re.fullmatch(r"CIK\d+-submissions-\d+\.json", name) is not None, "Unexpected SEC index filename")
                    queue.append(urljoin(source["url"], name))
                items.update(recent["accessionNumber"])
            continue
        content = body.lstrip()
        if content.startswith(b"<?xml") or re.match(br"<(rss|feed|urlset|sitemapindex)\b", content):
            parsed = xml_links(body, url)
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
    return {"complete": True, "items": sorted(items), "observations": observations, "reason": None}
