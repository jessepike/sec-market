"""Probe actual publisher discovery endpoints and archive registration receipts."""
import json
import re
import copy
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import timezone
from pathlib import Path
import threading
import time
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

from contracts import digest, instant, require, utcnow, valid_hash
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


def _qualification_url(url, source):
    require(isinstance(url, str), 'QUALIFICATION_URL_INVALID')
    value = urlsplit(url)
    require(value.scheme == 'https' and value.hostname in source['allowedHosts']
            and not value.username and not value.password and value.port in (None, 443)
            and not value.fragment and not any(c.isspace() for c in url), 'QUALIFICATION_URL_HOST_INVALID')
    return url


def _qualification_reference(store, reference, pattern):
    require(isinstance(reference, dict) and set(reference) == {'key', 'sha256', 'bytes'}
            and isinstance(reference['key'], str) and re.fullmatch(pattern, reference['key'])
            and valid_hash(reference['sha256']) and type(reference['bytes']) is int
            and 0 < reference['bytes'] <= 32_000_000, 'QUALIFICATION_PROOF_REFERENCE_INVALID')
    if reference['key'].startswith('objects/'):
        require(reference['key'] == 'objects/' + reference['sha256'], 'QUALIFICATION_OBJECT_ADDRESS_INVALID')
    return store.get(reference)


def validate_qualification_probe_plan(contract, store, path):
    """Read and prove the entire committed allowlist without writing or fetching."""
    raw = Path(path).read_bytes()
    require(0 < len(raw) <= 1_000_000, 'QUALIFICATION_PLAN_SIZE_INVALID')
    plan = json.loads(raw)
    require(isinstance(plan, dict) and set(plan) == {'schemaVersion', 'marketSha256', 'maxRequests', 'targets'}
            and type(plan['schemaVersion']) is int and plan['schemaVersion'] == 1
            and plan['marketSha256'] == digest(contract)
            and type(plan['maxRequests']) is int and plan['maxRequests'] == 7
            and isinstance(plan['targets'], list) and len(plan['targets']) == 7,
            'QUALIFICATION_PLAN_SHAPE_OR_POLICY_INVALID')
    sources = {s['id']: s for s in contract['sources']}
    identifiers, urls, validated = set(), set(), []
    for target in plan['targets']:
        require(isinstance(target, dict) and set(target) == {'id', 'sourceId', 'url', 'expectedFormat', 'proof'}
                and isinstance(target['id'], str) and re.fullmatch(r'[a-z][a-z0-9-]{0,79}', target['id'])
                and target['id'] not in identifiers and isinstance(target['sourceId'], str)
                and target['sourceId'] in sources and target['expectedFormat'] in ('html', 'rss'),
                'QUALIFICATION_TARGET_INVALID')
        source = sources[target['sourceId']]
        require(source['registration'] == 'candidate', 'QUALIFICATION_SOURCE_MUST_REMAIN_CANDIDATE')
        url = _qualification_url(target['url'], source)
        require(url not in urls, 'QUALIFICATION_TARGET_DUPLICATE_URL')
        identifiers.add(target['id']); urls.add(url)
        proof = target['proof']
        require(isinstance(proof, dict) and proof.get('type') in ('source_observation', 'diagnostic_observation'),
                'QUALIFICATION_PROOF_TYPE_INVALID')
        fields = {'type', 'record', 'body', 'fetchedAt'}
        if proof['type'] == 'diagnostic_observation':
            fields.add('observation')
        require(set(proof) == fields, 'QUALIFICATION_PROOF_SHAPE_INVALID')
        if proof['type'] == 'source_observation':
            observation = json.loads(_qualification_reference(store, proof['record'], r'observations/[a-f0-9]{64}\.json'))
            require(isinstance(observation, dict) and observation.get('observationId') == Path(proof['record']['key']).stem,
                    'QUALIFICATION_OBSERVATION_ID_DIFFERS')
            original = sources.get(observation.get('sourceId'))
            require(original and original['supplierId'] == source['supplierId']
                    and original['registration'] == 'verified'
                    and observation.get('requestedUrl') == original['url'], 'QUALIFICATION_SOURCE_BINDING_DIFFERS')
        else:
            recorded = json.loads(_qualification_reference(store, proof['record'], r'ci/source-probe-runs/[0-9]+-[0-9]+\.json'))
            require(isinstance(recorded, dict) and recorded.get('checkpointProfile') == 'source_probe'
                    and recorded.get('contractSha256') == digest(contract)
                    and all(type(recorded.get(k)) is int and recorded[k] == 0
                            for k in ('modelCalls', 'sourceChecksCredited', 'qualifiedSources'))
                    and recorded.get('semanticAdmission') is False and recorded.get('coverageCredit') is False
                    and recorded.get('githubEventName') == 'workflow_dispatch' and recorded.get('githubRef') == 'refs/heads/main'
                    and str(recorded.get('githubRunId')) + '-' + str(recorded.get('githubRunAttempt')) == Path(proof['record']['key']).stem,
                    'QUALIFICATION_DIAGNOSTIC_PROVENANCE_INVALID')
            diagnostic = recorded.get('diagnostic', {})
            require(isinstance(diagnostic, dict) and isinstance(diagnostic.get('sources'), list),
                    'QUALIFICATION_DIAGNOSTIC_SHAPE_INVALID')
            require(all(isinstance(r, dict) for r in diagnostic['sources']), 'QUALIFICATION_DIAGNOSTIC_SOURCE_SHAPE_INVALID')
            matches = [r for r in diagnostic['sources'] if r.get('sourceId') == source['id']]
            require(len(matches) == 1 and matches[0].get('supplierId') == source['supplierId']
                    and matches[0].get('qualified') is False and matches[0].get('facts') == []
                    and matches[0].get('registration') == 'candidate'
                    and matches[0].get('semanticAdmission') is False and matches[0].get('coverageCredit') is False
                    and isinstance(matches[0].get('observations'), list)
                    and proof['observation'] in matches[0].get('observations', []),
                    'QUALIFICATION_DIAGNOSTIC_SOURCE_BINDING_DIFFERS')
            reservations = matches[0].get('fetchReservations')
            require(isinstance(reservations, list) and all(isinstance(r, dict) for r in reservations),
                    'QUALIFICATION_DIAGNOSTIC_RESERVATIONS_INVALID')
            observation = json.loads(_qualification_reference(store, proof['observation'], r'objects/[a-f0-9]{64}'))
            require(isinstance(observation, dict)
                    and observation.get('requestedUrl') in [r.get('url') for r in reservations],
                    'QUALIFICATION_DIAGNOSTIC_REQUEST_DIFFERS')
        require(isinstance(observation, dict) and observation.get('status') == 'fetched'
                and observation.get('httpStatus') == 200 and observation.get('body') == proof['body']
                and observation.get('fetchedAt') == proof['fetchedAt'], 'QUALIFICATION_OBSERVATION_BODY_OR_TIME_DIFFERS')
        require(isinstance(proof['fetchedAt'], str), 'QUALIFICATION_PROOF_TIMESTAMP_INVALID')
        instant(proof['fetchedAt'])
        _qualification_url(observation.get('requestedUrl'), source)
        base = _qualification_url(observation.get('finalUrl') or observation['requestedUrl'], source)
        body = decoded_discovery_body(_qualification_reference(store, proof['body'], r'objects/[a-f0-9]{64}'))
        content = body.lstrip()
        if content.startswith(b'<?xml') or re.match(br'<(rss|feed)\b', content):
            parsed = xml_links(body, base)
            require(parsed['kind'] in ('rss', 'feed'), 'QUALIFICATION_DISCLOSURE_XML_INVALID')
            literal_urls = set(parsed['links'])
            recognition = 'rss_or_atom_item_link'
        else:
            page = Page(body.decode('utf8', errors='strict'), source_url=base)
            literal_urls = {urljoin(base, u) for u in [*page.canonicals, *page.feeds, *(link['url'] for link in page.links)]}
            recognition = 'html_link_feed_or_canonical'
        require(url in literal_urls, 'QUALIFICATION_TARGET_NOT_LITERAL_IN_PROOF')
        validated.append({**copy.deepcopy(target), 'literalRecognition': recognition})
    return {'rawSha256': digest(raw), 'canonicalSha256': digest(plan), 'path': str(path),
            'marketSha256': digest(contract), 'maxRequests': 7, 'plan': plan, 'targets': validated}


def _probe_qualification_targets(contract, store, fetcher, budget, plan):
    sources = {s['id']: s for s in contract['sources']}
    results = []
    for target in plan['targets']:
        row = {'targetId': target['id'], 'sourceId': target['sourceId'], 'url': target['url'],
               'expectedFormat': target['expectedFormat'], 'proof': target['proof'],
               'qualified': False, 'semanticAdmission': False, 'coverageCredit': False,
               'sourceChecksCredited': 0, 'qualifiedSources': 0, 'modelCalls': 0, 'facts': [],
               'reservation': None, 'observation': None, 'budgetDenied': False}
        try:
            row['reservation'] = budget.reserve_fetch()
            budget.before_fetch()
            observed = fetcher.fetch(sources[target['sourceId']], target['url'])
            row['observation'] = store.put(observed)
            require(observed.get('requestedUrl') == target['url'], 'QUALIFICATION_RESPONSE_URL_DIFFERS')
            if observed.get('status') != 'fetched' or observed.get('httpStatus') != 200:
                row['reason'] = observed.get('errorCode') or 'HTTP_' + str(observed.get('httpStatus', 'UNAVAILABLE'))
            elif observed.get('finalUrl', target['url']) != target['url']:
                row['reason'] = 'QUALIFICATION_REDIRECTED'
            else:
                body = decoded_discovery_body(store.get(observed['body']))
                if target['expectedFormat'] == 'rss':
                    parsed = xml_links(body, target['url'])
                    require(parsed['kind'] in ('rss', 'feed'), 'QUALIFICATION_EXPECTED_RSS_OR_ATOM')
                    row.update(format=parsed['kind'], itemCount=len(parsed['links']), continuationCount=len(parsed['indexes']))
                    row['reason'] = ('RESPONSE_RETAINED_SCOPE_AND_HISTORY_REVIEW_REQUIRED' if parsed['links'] else
                                     'EMPTY_FEED_RETAINED_REQUIRES_QUALIFICATION')
                else:
                    require(re.search(br'<(?:html|head|body)\b', body[:8192], re.I), 'QUALIFICATION_EXPECTED_HTML')
                    page = Page(body.decode('utf8', errors='strict'), source_url=target['url'])
                    require(bool(page.readable.strip()), 'QUALIFICATION_EMPTY_HTML')
                    row.update(format='html', canonicals=page.canonicals, advertisedFeeds=page.feeds)
                    row['reason'] = 'RESPONSE_RETAINED_SCOPE_AND_HISTORY_REVIEW_REQUIRED'
        except ProbeReservationDenied as error:
            row.update(reason=error.reason, budgetDenied=True)
        except (ValueError, OSError, RuntimeError, ET.ParseError, KeyError, TypeError) as error:
            row.update(reason=str(error)[:160] if isinstance(error, ValueError) else type(error).__name__,
                       errorType=type(error).__name__)
        store.write_once(f"source-probes/qualification/{plan['canonicalSha256']}/{digest(row)}.json", row)
        results.append(row)
    return {'plan': plan, 'targets': results, 'maximumExplicitRequests': 7,
            'chargedExplicitRequests': sum(row['reservation'] is not None for row in results),
            'qualifiedSources': 0, 'sourceChecksCredited': 0, 'semanticAdmission': False,
            'coverageCredit': False, 'modelCalls': 0, 'facts': []}


def probe_sources(contract, store, fetcher, *, reservation_context=None, qualification_plan_path=None):
    require(isinstance(reservation_context, PersistentProbeBudget), 'SOURCE_PROBE_BOUND_RESERVATION_CONTEXT_REQUIRED')
    reservation_context.assert_bound(store, contract)
    qualification = (validate_qualification_probe_plan(contract, store, qualification_plan_path)
                     if qualification_plan_path is not None else None)
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
    explicit = _probe_qualification_targets(contract, store, fetcher, reservation_context, qualification) if qualification else None
    denied = any(result['budgetDenied'] for result in results)
    denied = denied or bool(explicit and any(row['budgetDenied'] for row in explicit['targets']))
    report = {"schemaVersion": 1, "checkedAt": reservation_context.clock(), "contractSha256": digest(contract), "sources": results,
            "reservationContext": reservation_context.summary(), "qualified": False,
            "executionCompleted": not denied, "budgetDenied": denied,
            "sourceChecksCredited": 0, "qualifiedSources": 0,
            "semanticAdmission": False, "coverageCredit": False, "facts": []}
    if explicit is not None:
        report['qualification'] = explicit
    return report
