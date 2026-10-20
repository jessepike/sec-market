"""Bounded TLS-verified requests; source contracts govern redirects and targets."""
import ipaddress
import socket
import urllib.error
import urllib.request
import threading
import time
from urllib.parse import urlsplit

from contracts import require, utcnow


def safe_url(url, allowed_hosts, resolver=socket.getaddrinfo, proxy_dns=False):
    parsed = urlsplit(url)
    require(parsed.scheme == "https" and not parsed.username and not parsed.password and parsed.port in (None, 443), "Unsafe source protocol or credentials")
    require(parsed.hostname in allowed_hosts, "Unapproved source/redirect host")
    require(not parsed.hostname.endswith((".localhost", ".local", ".internal")) and parsed.hostname != "localhost", "Local network names prohibited")
    try:
        literal = ipaddress.ip_address(parsed.hostname)
    except ValueError:
        literal = None
    require(literal is None or literal.is_global, "Private/reserved network targets are prohibited")
    if proxy_dns:
        # The approved egress proxy owns DNS for CONNECT. Container DNS may be
        # disabled; it is neither the resolver nor the network used by this request.
        return url
    try:
        answers = resolver(parsed.hostname, 443, type=socket.SOCK_STREAM)
    except socket.gaierror:
        # Managed cloud networking resolves targets in its trusted HTTPS proxy.
        # Keep exact host/protocol/literal-IP checks; never enable this without a proxy.
        require(proxy_dns, "LOCAL_DNS_UNAVAILABLE_WITHOUT_TRUSTED_PROXY")
        return url
    for answer in answers:
        address = ipaddress.ip_address(answer[4][0])
        require(address.is_global, "Private/reserved network targets are prohibited")
    return url


class ContractRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, hosts, proxy_dns=False):
        self.hosts, self.proxy_dns = hosts, proxy_dns

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        safe_url(newurl, self.hosts, proxy_dns=self.proxy_dns)
        return super().redirect_request(request, fp, code, msg, headers, newurl)


class Fetcher:
    def __init__(self, store, max_bytes=32_000_000, timeout=30):
        self.store, self.max_bytes, self.timeout = store, max_bytes, timeout
        self.rate_lock = threading.Lock()
        self.last_request = {}
        self.proxy_dns = bool(urllib.request.getproxies().get("https"))

    def fetch(self, source, url=None, previous=None, attempt=0):
        url = safe_url(url or source["url"], source["allowedHosts"], proxy_dns=self.proxy_dns)
        # Shared across all matrix threads, including repeated SEC source hosts.
        with self.rate_lock:
            host = urlsplit(url).hostname
            wait = 0.3 - (time.monotonic() - self.last_request.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            self.last_request[host] = time.monotonic()
        headers = {"User-Agent": "SecurityMarketPulse research jesse@keatingpike.com", "Accept": "application/json, application/xml, text/xml, text/html"}
        if previous and previous.get("requestedUrl") == url:
            if previous.get("etag"):
                headers["If-None-Match"] = previous["etag"]
            if previous.get("lastModified"):
                headers["If-Modified-Since"] = previous["lastModified"]
        opener = urllib.request.build_opener(ContractRedirect(source["allowedHosts"], self.proxy_dns))
        try:
            response = opener.open(urllib.request.Request(url, headers=headers), timeout=self.timeout)
        except urllib.error.HTTPError as error:
            if error.code in (500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** attempt)
                return self.fetch(source, url, previous, attempt + 1)
            if error.code != 304:
                return {"requestedUrl": url, "fetchedAt": utcnow(), "status": "blocked" if error.code in (401, 403, 429) else "failed", "httpStatus": error.code, "errorCode": f"HTTP_{error.code}"}
            if not previous or not previous.get("body"):
                # Retry without validators; never award success for a bodyless 304.
                require(previous is not None, "304 received without retained evidence")
                return self.fetch(source, url, previous=None)
            try:
                self.store.get(previous["body"])
            except FileNotFoundError:
                return self.fetch(source, url, previous=None)
            return {**previous, "requestedUrl": url, "fetchedAt": utcnow(), "status": "not_modified", "httpStatus": 304, "reusesObservationId": previous["observationId"]}
        except urllib.error.URLError as error:
            # A proxy denial is a configuration failure, not a reason for a retry loop.
            blocked = "403" in str(error.reason) or isinstance(error.reason, PermissionError)
            return {"requestedUrl": url, "fetchedAt": utcnow(), "status": "blocked" if blocked else "failed", "httpStatus": 403 if blocked else None, "errorCode": "NETWORK_POLICY_BLOCKED" if blocked else "SOURCE_CONNECTION_FAILED"}
        with response:
            safe_url(response.url, source["allowedHosts"], proxy_dns=self.proxy_dns)
            body = response.read(self.max_bytes + 1)
            require(len(body) <= self.max_bytes, "Source exceeds request size budget")
            require(response.status == 200, "Unexpected source response status")
            return {"requestedUrl": url, "finalUrl": response.url, "fetchedAt": utcnow(), "status": "fetched", "httpStatus": 200, "body": self.store.put(body), "etag": response.headers.get("ETag"), "lastModified": response.headers.get("Last-Modified"), "contentType": response.headers.get("Content-Type", "")}
