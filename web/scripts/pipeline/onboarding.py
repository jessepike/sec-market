"""Probe actual publisher discovery endpoints and archive registration receipts."""
import json
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

from contracts import digest, utcnow
from discovery import Page, xml_links


def probe_sources(contract, store, fetcher):
    def probe(source):
        result = {"sourceId": source["id"], "supplierId": source["supplierId"],
                  "checkedAt": utcnow(), "registration": "candidate", "observations": [], "endpoints": []}
        def get(url):
            observed = fetcher.fetch(source, url)
            result["observations"].append(store.put(observed))
            return observed, store.get(observed["body"]) if observed.get("body") else b""
        try:
            observed, root = get(source["url"])
            if observed["status"] != "fetched":
                result["reason"] = observed.get("errorCode", "ROOT_UNAVAILABLE")
                return result
            page = Page(root.decode("utf8", errors="replace"))
            robots_url = urljoin(source["url"], "/robots.txt")
            observed, robots = get(robots_url)
            parser = RobotFileParser(robots_url)
            if observed["status"] == "fetched":
                parser.parse(robots.decode("utf8", errors="replace").splitlines())
                sitemaps = re.findall(r"(?im)^sitemap:\s*(https://\S+)", robots.decode("utf8", errors="replace"))
            else:
                sitemaps = []
            candidates = [(urljoin(source["url"], u), "rss") for u in page.feeds]
            candidates += [(u, "sitemap") for u in sitemaps]
            if not candidates:
                candidates = [(urljoin(source["url"], "/sitemap.xml"), "sitemap")]
            for url, kind in list(dict.fromkeys(candidates))[:8]:
                if urlsplit(url).hostname not in source["allowedHosts"]:
                    result["endpoints"].append({"url": url, "result": "ADDITIONAL_HOST_REQUIRES_REGISTRATION"})
                    continue
                if robots and not parser.can_fetch("SecurityMarketPulse", url):
                    result["endpoints"].append({"url": url, "result": "ROBOTS_DISALLOWED"})
                    continue
                observed, body = get(url)
                if observed["status"] != "fetched":
                    result["endpoints"].append({"url": url, "result": observed.get("errorCode", "UNAVAILABLE")})
                    continue
                try:
                    parsed = xml_links(body, url)
                except (ValueError, __import__('xml.etree.ElementTree', fromlist=['ParseError']).ParseError):
                    result["endpoints"].append({"url": url, "result": "NOT_DISCOVERY_XML"})
                    continue
                result["endpoints"].append({"url": url, "kind": kind, "format": parsed["kind"],
                                            "result": "DISCOVERY_ENDPOINT_RESPONDED", "body": observed["body"],
                                            "itemCount": len(parsed["links"]), "indexCount": len(parsed["indexes"]),
                                            "sampleItems": parsed["links"][:5], "sampleIndexes": parsed["indexes"][:5]})
            # An XML response alone cannot establish entity scope, history or completeness.
            result["reason"] = "ENDPOINTS_PROBED_SCOPE_AND_HISTORY_REVIEW_REQUIRED"
        except (ValueError, OSError, RuntimeError) as exc:
            result["reason"] = type(exc).__name__
        finally:
            store.write_once(f"source-probes/{source['id'].replace(':', '_')}/{digest(result)}.json", result)
        return result
    sources = [s for s in contract["sources"] if s["registration"] == "candidate"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(probe, sources))
    return {"schemaVersion": 1, "checkedAt": utcnow(), "contractSha256": digest(contract), "sources": results}
