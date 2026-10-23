"""Probe actual publisher discovery endpoints and archive registration receipts."""
import json
import re
import copy
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import timezone
import threading
import time
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

from contracts import digest, instant, require, utcnow
from discovery import Page, decoded_discovery_body, xml_links


class ProbeReservationDenied(RuntimeError):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


class PersistentProbeBudget:
    """A current-day, store/contract-bound reservation context; never a refund."""
    def __init__(self, store, contract, *, clock=utcnow, monotonic=time.monotonic, maximum_seconds=1200):
        limit = contract['schedule'].get('maxFetchesPerRun', 5000)
        runtime = contract['schedule'].get('maxRuntimeSeconds', 7200)
        require(type(limit) is int and 1 <= limit <= 5500, 'SOURCE_PROBE_FETCH_LIMIT_INVALID')
        require(type(runtime) is int and runtime > 0 and type(maximum_seconds) is int
                and 0 < maximum_seconds <= 1200, 'SOURCE_PROBE_RUNTIME_LIMIT_INVALID')
        self.store, self.contract_sha256, self.clock, self.monotonic = store, digest(contract), clock, monotonic
        self.started_at = clock()
        self.started = instant(self.started_at).astimezone(timezone.utc)
        self.day = self.started.date().isoformat()
        self.budget_name = 'budget-' + self.day
        self.limit, self.maximum_seconds = limit, min(runtime, maximum_seconds)
        self.deadline = monotonic() + self.maximum_seconds
        self.mutex = threading.RLock()
        self.reservations, self.denials = 0, Counter()
        with store.lock('daily-budget-reservation', blocking=True):
            self.initial_budget = copy.deepcopy(store.read('heads/' + self.budget_name + '.json'))

    def assert_bound(self, store, contract):
        require(self.store is store and self.contract_sha256 == digest(contract), 'SOURCE_PROBE_RESERVATION_CONTEXT_UNBOUND')

    def _guard(self):
        try:
            moment = instant(self.clock()).astimezone(timezone.utc)
        except (ValueError, TypeError, AttributeError):
            raise ProbeReservationDenied('SOURCE_PROBE_CLOCK_INVALID') from None
        if moment.date().isoformat() != self.day:
            raise ProbeReservationDenied('SOURCE_PROBE_UTC_DAY_CHANGED')
        if moment < self.started:
            raise ProbeReservationDenied('SOURCE_PROBE_CLOCK_REGRESSED')
        if self.monotonic() >= self.deadline:
            raise ProbeReservationDenied('SOURCE_PROBE_DEADLINE_EXCEEDED')

    def reserve_fetch(self):
        with self.mutex:
            try:
                self._guard()
                # The same lock and head are shared with daily collection.
                with self.store.lock('daily-budget-reservation', blocking=True):
                    self._guard()
                    previous = self.store.read('heads/' + self.budget_name + '.json')
                    if previous is not None and not isinstance(previous, dict):
                        raise ProbeReservationDenied('SOURCE_PROBE_FETCH_LEDGER_INVALID')
                    counts = dict(previous) if previous is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
                    count = counts.get('fetches', 0)
                    if type(count) is not int or count < 0:
                        raise ProbeReservationDenied('SOURCE_PROBE_FETCH_LEDGER_INVALID')
                    if count >= self.limit:
                        raise ProbeReservationDenied('FETCHES_BUDGET_EXHAUSTED')
                    counts['fetches'] = count + 1
                    self.store.compare_and_swap(self.budget_name, previous, counts)
                    self.reservations += 1
                    return {'budgetDay': self.day, 'fetchLimit': self.limit, 'chargedFetchCount': counts['fetches']}
            except ProbeReservationDenied as error:
                self.denials[error.reason] += 1
                raise
            except (ValueError, OSError, RuntimeError):
                reason = 'SOURCE_PROBE_RESERVATION_PERSISTENCE_FAILED'
                self.denials[reason] += 1
                raise ProbeReservationDenied(reason) from None

    def before_fetch(self):
        # A reservation remains charged if the deadline/day changes between
        # its durable write and the immediate transport invocation.
        with self.mutex:
            try:
                self._guard()
            except ProbeReservationDenied as error:
                self.denials[error.reason] += 1
                raise

    def summary(self):
        with self.mutex, self.store.lock('daily-budget-reservation', blocking=True):
            return {'budgetDay': self.day, 'contractSha256': self.contract_sha256,
                    'fetchLimit': self.limit, 'maximumRuntimeSeconds': self.maximum_seconds,
                    'startedAt': self.started_at, 'initialBudget': copy.deepcopy(self.initial_budget),
                    'probeFetchReservations': self.reservations, 'reservationDenials': dict(self.denials),
                    'currentBudget': self.store.read('heads/' + self.budget_name + '.json')}


def probe_sources(contract, store, fetcher, *, reservation_context=None):
    require(isinstance(reservation_context, PersistentProbeBudget), 'SOURCE_PROBE_BOUND_RESERVATION_CONTEXT_REQUIRED')
    reservation_context.assert_bound(store, contract)
    def probe(source):
        result = {"sourceId": source["id"], "supplierId": source["supplierId"],
                  "checkedAt": reservation_context.clock(), "registration": "candidate", "observations": [], "endpoints": [],
                  "qualified": False, "semanticAdmission": False, "coverageCredit": False, "facts": [],
                  "fetchReservations": [], "reservationDenials": []}
        def get(url):
            reservation = None
            try:
                reservation = reservation_context.reserve_fetch()
                result['fetchReservations'].append({'url': url, **reservation})
                reservation_context.before_fetch()
            except ProbeReservationDenied as error:
                result['reservationDenials'].append({'url': url, 'reason': error.reason,
                    'budgetDay': reservation_context.day,
                    'reservationCharged': None if error.reason == 'SOURCE_PROBE_RESERVATION_PERSISTENCE_FAILED' else reservation is not None})
                raise
            observed = fetcher.fetch(source, url)
            result["observations"].append(store.put(observed))
            return observed, store.get(observed["body"]) if observed.get("body") else b""
        try:
            observed, root = get(source["url"])
            if observed["status"] != "fetched":
                result["reason"] = observed.get("errorCode", "ROOT_UNAVAILABLE")
                return result
            root_text = decoded_discovery_body(root).decode('utf8', errors='strict' if root.startswith(b'\x1f\x8b') else 'replace')
            page = Page(root_text)
            robots_url = urljoin(source["url"], "/robots.txt")
            observed, robots = get(robots_url)
            parser = RobotFileParser(robots_url)
            if observed["status"] == "fetched":
                robots_text = decoded_discovery_body(robots).decode('utf8', errors='strict' if robots.startswith(b'\x1f\x8b') else 'replace')
                parser.parse(robots_text.splitlines())
                sitemaps = re.findall(r"(?im)^sitemap:\s*(https://\S+)", robots_text)
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
        except ProbeReservationDenied as exc:
            result['reason'] = exc.reason
        except (ValueError, OSError, RuntimeError) as exc:
            result["reason"] = type(exc).__name__
        finally:
            result['executionCompleted'] = not bool(result['reservationDenials'])
            result['budgetDenied'] = bool(result['reservationDenials'])
            store.write_once(f"source-probes/{source['id'].replace(':', '_')}/{digest(result)}.json", result)
        return result
    sources = [s for s in contract["sources"] if s["registration"] == "candidate"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(probe, sources))
    denied = any(result['budgetDenied'] for result in results)
    return {"schemaVersion": 1, "checkedAt": reservation_context.clock(), "contractSha256": digest(contract), "sources": results,
            "reservationContext": reservation_context.summary(), "qualified": False,
            "executionCompleted": not denied, "budgetDenied": denied,
            "sourceChecksCredited": 0, "qualifiedSources": 0,
            "semanticAdmission": False, "coverageCredit": False, "facts": []}
