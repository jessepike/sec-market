"""Bounded TLS-verified requests; source contracts govern redirects and targets."""
import ipaddress
import socket
import urllib.error
import urllib.request
import threading
import time
from urllib.parse import urlsplit

from contracts import ContractError, require, utcnow


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



# These diagnostics describe observed responses and considered targets only.
# They do not assert that a proposed redirect request actually reached transport.
REDIRECT_EVENT_LIMIT, REDIRECT_TEXT_LIMIT = 64, 4096


def _redirect_text(value):
    if value is None:
        return None, False, None
    value = str(value)
    return value[:REDIRECT_TEXT_LIMIT], len(value) > REDIRECT_TEXT_LIMIT, len(value)


def _redirect_fields(**values):
    fields = {}
    for name, value in values.items():
        fields[name], fields[name + 'Truncated'], fields[name + 'Length'] = _redirect_text(value)
    return fields


class DiagnosticContractRedirect(ContractRedirect):
    """Observe redirects while delegating every policy and loop decision."""
    def __init__(self, hosts, proxy_dns=False):
        super().__init__(hosts, proxy_dns)
        self.responses, self.truncated, self.active = [], False, None

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        if self.active is not None:
            self.active.update(_redirect_fields(proposedTargetUrl=newurl), category='proposal_constructed')
        try:
            return super().redirect_request(request, fp, code, msg, headers, newurl)
        except ContractError:
            if self.active is not None:
                self.active['category'] = 'policy_rejected'
            raise

    def http_error_302(self, request, fp, code, msg, headers):
        event = {'httpStatus': code, **_redirect_fields(responseUrl=request.full_url,
                 rawLocation=headers.get('Location'), proposedTargetUrl=None), 'category': 'observed'}
        if len(self.responses) < REDIRECT_EVENT_LIMIT:
            self.responses.append(event)
        else:
            self.truncated = True
        prior, self.active = self.active, event
        try:
            return super().http_error_302(request, fp, code, msg, headers)
        except urllib.error.HTTPError:
            if event['category'] != 'policy_rejected':
                event['category'] = 'http_redirect_error'
            raise
        except ValueError:
            if event['category'] != 'policy_rejected':
                event['category'] = 'invalid_redirect'
            raise
        finally:
            self.active = prior

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302


def _redirect_result(result, handler, error=None):
    later = result.get('redirectDiagnostics')
    relevant_error = error is not None and error.code in (301, 302, 303, 307, 308)
    if not handler.responses and not handler.truncated and not relevant_error:
        return result
    responses = handler.responses + (later['responses'] if later else [])
    terminal = None
    if error is not None:
        terminal = {'httpStatus': error.code, 'category': 'http_error',
                    **_redirect_fields(errorUrl=error.url, rawLocation=error.headers.get('Location') if error.headers else None)}
    if later and later['lastHttpError'] is not None:
        terminal = later['lastHttpError']
    return {**result, 'redirectDiagnostics': {'schemaVersion': 1,
        'responses': responses[:REDIRECT_EVENT_LIMIT],
        'responsesTruncated': handler.truncated or len(responses) > REDIRECT_EVENT_LIMIT or bool(later and later['responsesTruncated']),
        'lastHttpError': terminal}}


class Fetcher:
    def __init__(self, store, max_bytes=32_000_000, timeout=30, *, redirect_diagnostics=False,
                 unexpected_status_diagnostics=False):
        require(type(redirect_diagnostics) is bool, "Redirect diagnostic mode must be boolean")
        require(type(unexpected_status_diagnostics) is bool, "Unexpected status diagnostic mode must be boolean")
        self.redirect_diagnostics = redirect_diagnostics
        self.unexpected_status_diagnostics = unexpected_status_diagnostics
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
        handler = (DiagnosticContractRedirect if self.redirect_diagnostics else ContractRedirect)(source["allowedHosts"], self.proxy_dns)
        opener = urllib.request.build_opener(handler)
        def retained(result, error=None):
            return _redirect_result(result, handler, error) if self.redirect_diagnostics else result
        try:
            response = opener.open(urllib.request.Request(url, headers=headers), timeout=self.timeout)
        except urllib.error.HTTPError as error:
            if error.code in (500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** attempt)
                return retained(self.fetch(source, url, previous, attempt + 1), error)
            if error.code != 304:
                return retained({"requestedUrl": url, "fetchedAt": utcnow(), "status": "blocked" if error.code in (401, 403, 429) else "failed", "httpStatus": error.code, "errorCode": f"HTTP_{error.code}"}, error)
            if not previous or not previous.get("body"):
                # Retry without validators; never award success for a bodyless 304.
                require(previous is not None, "304 received without retained evidence")
                return retained(self.fetch(source, url, previous=None), error)
            try:
                self.store.get(previous["body"])
            except FileNotFoundError:
                return retained(self.fetch(source, url, previous=None), error)
            prior = previous if not self.redirect_diagnostics else {k: v for k, v in previous.items() if k != "redirectDiagnostics"}
            return retained({**prior, "requestedUrl": url, "fetchedAt": utcnow(), "status": "not_modified", "httpStatus": 304, "reusesObservationId": previous["observationId"]}, error)
        except urllib.error.URLError as error:
            # A proxy denial is a configuration failure, not a reason for a retry loop.
            blocked = "403" in str(error.reason) or isinstance(error.reason, PermissionError)
            return retained({"requestedUrl": url, "fetchedAt": utcnow(), "status": "blocked" if blocked else "failed", "httpStatus": 403 if blocked else None, "errorCode": "NETWORK_POLICY_BLOCKED" if blocked else "SOURCE_CONNECTION_FAILED"})
        except ValueError as error:
            if not self.redirect_diagnostics or not handler.responses:
                raise
            return retained({"requestedUrl": url, "fetchedAt": utcnow(), "status": "failed",
                "httpStatus": handler.responses[-1]["httpStatus"],
                "errorCode": "REDIRECT_POLICY_REJECTED" if isinstance(error, ContractError) else "REDIRECT_RESPONSE_INVALID"})
        with response:
            safe_url(response.url, source["allowedHosts"], proxy_dns=self.proxy_dns)
            body = response.read(self.max_bytes + 1)
            require(len(body) <= self.max_bytes, "Source exceeds request size budget")
            if self.unexpected_status_diagnostics and response.status != 200:
                return retained({"requestedUrl": url, "finalUrl": response.url, "fetchedAt": utcnow(),
                    "status": "failed", "httpStatus": response.status, "body": self.store.put(body),
                    "contentType": response.headers.get("Content-Type", ""), "errorCode": "UNEXPECTED_HTTP_STATUS"})
            require(response.status == 200, "Unexpected source response status")
            return retained({"requestedUrl": url, "finalUrl": response.url, "fetchedAt": utcnow(), "status": "fetched", "httpStatus": 200, "body": self.store.put(body), "etag": response.headers.get("ETag"), "lastModified": response.headers.get("Last-Modified"), "contentType": response.headers.get("Content-Type", "")})
