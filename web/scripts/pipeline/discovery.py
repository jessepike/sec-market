"""Source discovery with explicit pagination completeness, never empty=success."""
import json
import gzip
import io
import re
from datetime import timedelta
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from contracts import require, instant, utcnow


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.links, self.feeds, self.text, self.published = [], [], [], None
        self.regions, self.region_text = [], {"article": [], "main": []}
        self.json_ld, self.json_parts, self.json_dates, self.meta_published = False, [], set(), False
        self.skip = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.regions = [(t, r, depth + (t == tag)) for t, r, depth in self.regions]
        region = tag if tag in ("article", "main") else "main" if a.get("role") == "main" else None
        if region:
            self.regions.append((tag, region, 1))
        if tag == "script" and a.get("type") == "application/ld+json":
            self.json_ld, self.json_parts = True, []
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if tag == "a" and a.get("href"):
            self.links.append({"url": a["href"], "next": "next" in a.get("rel", "").split()})
        if tag == "link" and a.get("href") and a.get("type", "") in ("application/rss+xml", "application/atom+xml"):
            self.feeds.append(a["href"])
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
            for region in {region for _, region, _ in self.regions}:
                self.region_text[region].append(data)

    @property
    def readable(self):
        for region in ("article", "main"):
            text = re.sub(r"\s+", " ", " ".join(self.region_text[region])).strip()
            if len(text) >= 100:
                return text
        return re.sub(r"\s+", " ", " ".join(self.text)).strip()


def scoped(url, source):
    p = urlsplit(url)
    return p.scheme == "https" and p.hostname in source["allowedHosts"] and any(p.path.startswith(prefix) for prefix in source["scopePrefixes"])


def xml_links(body, base):
    if body.startswith(b"\x1f\x8b"):
        with gzip.GzipFile(fileobj=io.BytesIO(body)) as compressed:
            body = compressed.read(32_000_001)
        require(len(body) <= 32_000_000, "Decompressed sitemap exceeds byte budget")
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
    queue, seen, items, observations, item_dates, item_modified = [source["url"]], set(), set(), [], {}, {}
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
                        if recent["filingDate"][i] < cutoff or recent["form"][i] not in ("10-K", "10-K/A", "10-Q", "10-Q/A", "8-K", "8-K/A", "NT 10-K", "NT 10-Q", "DEFM14A", "PREM14A", "25", "25-NSE"):
                            continue
                        primary = recent["primaryDocument"][i]
                        require(re.fullmatch(r"\d{10}-\d{2}-\d{6}", accession) and re.fullmatch(r"[A-Za-z0-9_.-]+", primary), "Unsafe SEC document path")
                        document_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}/{primary}"
                        items.add(document_url)
                        item_dates[document_url] = recent["filingDate"][i]
                else:
                    items.update(recent["accessionNumber"])
            continue
        content = body.lstrip()
        if content.startswith((b"<?xml", b"\x1f\x8b")) or re.match(br"<(rss|feed|urlset|sitemapindex)\b", content):
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
