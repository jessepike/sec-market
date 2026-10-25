"""Fictional HTTPS transport and temporary archives; no live source requests."""
import contextlib
import copy
import io
import json
from email.message import Message
from pathlib import Path
import sys
import tempfile
import unittest
import urllib.request
import urllib.response
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'web/scripts/pipeline'), str(ROOT / 'ops/ci')]
import collect
import fetcher as candidate
import onboarding
from contracts import ContractError, canonical, digest
from storage import LocalStore
import test_leased_source_probe as leased
import test_source_qualification_probe as qualification

NOW = '2026-10-23T12:00:00Z'
URL = 'https://example.invalid/archive/'
SOURCE = {'url': URL, 'allowedHosts': ['example.invalid']}
BUILD = urllib.request.build_opener


@contextlib.contextmanager
def fictional_https(route):
    """Use urllib's real opener, response/error handlers and redirect policy."""
    calls, reads = [], []
    class Body(io.BytesIO):
        def read(self, size=-1):
            reads.append(size)
            return super().read(size)
    class HTTPS(urllib.request.HTTPSHandler):
        def https_open(self, req):
            calls.append(req.full_url)
            code, values, body, final = route(req, len(calls))
            headers = Message()
            for key, value in values.items():
                headers[key] = value
            response = urllib.response.addinfourl(Body(body), headers, final or req.full_url, code)
            response.msg = 'Fictional response'
            return response
    with contextlib.ExitStack() as stack:
        stack.enter_context(patch.object(candidate.urllib.request, 'build_opener',
            side_effect=lambda handler: BUILD(handler, HTTPS())))
        stack.enter_context(patch.object(candidate, 'utcnow', return_value=NOW))
        stack.enter_context(patch.object(candidate.time, 'sleep'))
        stack.enter_context(patch('socket.socket.connect', side_effect=AssertionError('network forbidden')))
        yield calls, reads


def response(code, body=b'complete response', headers=None, final=None):
    return lambda _req, _n: (code, headers or {}, body, final)


class UnexpectedHttpStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(Path(self.temp.name) / 'state')

    def fetcher(self, **kwargs):
        fetch = candidate.Fetcher(self.store, **kwargs)
        fetch.proxy_dns = True
        return fetch

    def test_default_opened_non200_still_raises_without_retaining_body(self):
        for status in (201, 204, 206):
            with self.subTest(status=status), fictional_https(response(status)) as (calls, reads), \
                    patch.object(self.store, 'put', wraps=self.store.put) as put:
                with self.assertRaisesRegex(ContractError, '^Unexpected source response status$'):
                    self.fetcher().fetch(SOURCE)
                put.assert_not_called()
                self.assertEqual(calls, [URL])
                self.assertEqual(reads, [32_000_001])
        self.assertFalse((self.store.root / 'objects').exists())

    def test_success_is_identical_with_diagnostic_off_or_on(self):
        results = []
        for enabled in (False, True):
            with fictional_https(response(200, b'body', {'ETag': 'tag',
                    'Last-Modified': 'date', 'Content-Type': 'text/html'})) as (calls, reads):
                results.append(self.fetcher(unexpected_status_diagnostics=enabled).fetch(SOURCE))
                self.assertEqual(calls, [URL])
                self.assertEqual(reads, [32_000_001])
        self.assertEqual(canonical(results[0]), canonical(results[1]))
        self.assertEqual(results[0]['status'], 'fetched')
        self.assertEqual(results[0]['httpStatus'], 200)
        self.assertNotIn('errorCode', results[0])

    def test_opted_in_201_204_206_retain_exact_complete_observation_once(self):
        for status, body in ((201, b'created'), (204, b''), (206, b'actual partial-status body')):
            final = URL + '?actual=final'
            with self.subTest(status=status), fictional_https(response(status, body,
                    {'Content-Type': 'text/plain', 'Set-Cookie': 'private', 'ETag': 'not retained'}, final)) as (calls, reads), \
                    patch.object(self.store, 'put', wraps=self.store.put) as put:
                result = self.fetcher(unexpected_status_diagnostics=True).fetch(SOURCE)
                self.assertEqual(result, {'requestedUrl': URL, 'finalUrl': final, 'fetchedAt': NOW,
                    'status': 'failed', 'httpStatus': status, 'body': {'key': 'objects/' + digest(body),
                    'sha256': digest(body), 'bytes': len(body)}, 'contentType': 'text/plain',
                    'errorCode': 'UNEXPECTED_HTTP_STATUS'})
                self.assertEqual(self.store.get(result['body']), body)
                put.assert_called_once_with(body)
                self.assertEqual(calls, [URL])
                self.assertEqual(reads, [32_000_001])

    def test_real_redirect_preserves_requested_and_final_urls_without_extra_requests(self):
        def route(req, number):
            return (302, {'Location': '/final'}, b'', None) if number == 1 else (206, {}, b'bounded', None)
        with fictional_https(route) as (calls, _reads):
            result = self.fetcher(unexpected_status_diagnostics=True).fetch(SOURCE)
        self.assertEqual(calls, [URL, 'https://example.invalid/final'])
        self.assertEqual(result['requestedUrl'], URL)
        self.assertEqual(result['finalUrl'], calls[-1])
        self.assertEqual(result['httpStatus'], 206)
        self.assertNotIn('redirectDiagnostics', result)

    def test_option_requires_exact_boolean_before_transport(self):
        for value in (1, 0, None, 'true', [], {}):
            with self.subTest(value=value), self.assertRaisesRegex(ContractError, 'must be boolean'):
                self.fetcher(unexpected_status_diagnostics=value)

    def test_size_limit_and_unsafe_final_host_reject_without_retention(self):
        cases = [(response(206, b'12345'), 'Source exceeds request size budget', [5]),
                 (response(206, b'1234', final='https://unapproved.invalid/'), 'Unapproved source/redirect host', []),
                 (response(206, b'1234', final='https://127.0.0.1/'), 'Private/reserved network targets', [])]
        source = {**SOURCE, 'allowedHosts': ['example.invalid', '127.0.0.1']}
        for route, error, expected_reads in cases:
            with self.subTest(error=error), fictional_https(route) as (calls, reads), \
                    patch.object(self.store, 'put', wraps=self.store.put) as put:
                with self.assertRaisesRegex(ContractError, error):
                    self.fetcher(max_bytes=4, unexpected_status_diagnostics=True).fetch(source)
                put.assert_not_called()
                self.assertEqual(calls, [URL])
                self.assertEqual(reads, expected_reads)

    def test_http_error_403_429_503_behavior_and_retry_counts_are_unchanged(self):
        for status, count in ((403, 1), (429, 1), (503, 3)):
            results = []
            for enabled in (False, True):
                with self.subTest(status=status, enabled=enabled), fictional_https(response(status)) as (calls, reads), \
                        patch.object(self.store, 'put', wraps=self.store.put) as put:
                    results.append(self.fetcher(unexpected_status_diagnostics=enabled).fetch(SOURCE))
                    self.assertEqual(len(calls), count)
                    self.assertEqual(reads, [])
                    put.assert_not_called()
            self.assertEqual(canonical(results[0]), canonical(results[1]))
            self.assertEqual(results[1]['errorCode'], 'HTTP_' + str(status))
            self.assertNotIn('body', results[1])

    def test_503_retry_success_and_304_reuse_or_unconditional_retry_are_unchanged(self):
        previous = {'requestedUrl': URL, 'etag': 'prior', 'observationId': 'a'*64,
                    'body': self.store.put(b'prior bytes')}
        cases = [(lambda _r, n: (503, {}, b'', None) if n < 3 else (200, {}, b'ok', None), None, 3),
                 (response(304), previous, 1),
                 (lambda _r, n: (304, {}, b'', None) if n == 1 else (200, {}, b'ok', None), {}, 2),
                 (lambda _r, n: (304, {}, b'', None) if n == 1 else (200, {}, b'ok', None),
                  {**previous, 'body': {'key': 'objects/missing', 'sha256': 'b'*64, 'bytes': 4}}, 2)]
        for route, prior, count in cases:
            results = []
            for enabled in (False, True):
                with fictional_https(route) as (calls, _reads):
                    results.append(self.fetcher(unexpected_status_diagnostics=enabled).fetch(SOURCE, previous=prior))
                    self.assertEqual(len(calls), count)
            self.assertEqual(canonical(results[0]), canonical(results[1]))
        for enabled in (False, True):
            with fictional_https(response(304)) as (calls, _reads), \
                    self.assertRaisesRegex(ContractError, '304 received without retained evidence'):
                self.fetcher(unexpected_status_diagnostics=enabled).fetch(SOURCE)
            self.assertEqual(calls, [URL])


class DiagnosticRouteTests(unittest.TestCase):
    def fixture(self):
        fixture = leased.LeasedSourceProbeTests(methodName='runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        return fixture

    def test_schema1_actual_leased_loop_retains_failures_without_parsing_or_credit(self):
        fixture = self.fixture()
        failed_body = b'<html><body>never parse</body></html>'
        decode = onboarding.decoded_discovery_body
        def decode_prior_evidence(body):
            self.assertNotEqual(body, failed_body, 'failed response must stop before parsing')
            return decode(body)
        def transport(state, **kwargs):
            fetch = candidate.Fetcher(state, **kwargs)
            fetch.proxy_dns = True
            return fetch
        with patch.object(collect, 'Fetcher', side_effect=transport) as factory, \
                fictional_https(response(206, failed_body)) as (calls, _reads), \
                patch.object(onboarding, 'decoded_discovery_body', side_effect=decode_prior_evidence):
            result = fixture.run_probe()
        self.assertEqual(factory.call_args.kwargs, {'timeout': 12, 'unexpected_status_diagnostics': True})
        self.assertEqual(len(calls), 8)
        self.assertEqual(result['diagnostic']['qualification']['chargedExplicitRequests'], 7)
        for row in result['diagnostic']['qualification']['targets']:
            observed = json.loads(fixture.state().get(row['observation']))
            self.assertEqual(observed['httpStatus'], 206)
            self.assertEqual(observed['status'], 'failed')
            self.assertEqual(observed['errorCode'], 'UNEXPECTED_HTTP_STATUS')
            self.assertEqual(observed['requestedUrl'], row['url'])
            self.assertEqual(observed['fetchedAt'], NOW)
            self.assertEqual(fixture.state().get(observed['body']), failed_body)
            self.assertEqual(row['reason'], 'UNEXPECTED_HTTP_STATUS')
            self.assertEqual(row['facts'], [])
            self.assertFalse(row['coverageCredit'])
            self.assertFalse(row['qualified'])
        self.assertEqual(result['sourceChecksCredited'], 0)
        self.assertEqual(result['qualifiedSources'], 0)
        self.assertEqual(result['modelCalls'], 0)
        self.assertFalse(result['coverageCredit'])
        self.assertFalse(result['semanticAdmission'])
        self.assertFalse(result['publication']['published'])
        fixture.assert_preserved()

    def test_validated_schema2_keeps_default_constructor(self):
        fixture = self.fixture()
        original = fixture.archive.restore
        def restore(destination):
            result = original(destination)
            plan = {'schemaVersion': 2, 'operation': onboarding.DISABLED_QUALIFICATION_OPERATION,
                    'marketSha256': digest(fixture.policy), 'maxRequests': 0, 'sources': []}
            (fixture.repo / 'contracts/source-qualification-probes.json').write_bytes(canonical(plan))
            return result
        with patch.object(fixture.archive, 'restore', side_effect=restore), \
                patch.object(collect, 'Fetcher', side_effect=fixture.transport) as factory:
            result = fixture.run_probe()
        self.assertEqual(factory.call_args.kwargs, {'timeout': 12})
        self.assertFalse(result['coverageCredit'])

    def test_orca_keeps_its_existing_redirect_only_constructor(self):
        import test_leased_orca_probe as leased_orca
        fixture = leased_orca.LeasedOrcaProbeTests(methodName='runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        with patch.object(collect, 'Fetcher', side_effect=fixture.transport) as factory:
            fixture.run_probe()
        self.assertEqual(factory.call_args.kwargs, {'timeout': 12, 'redirect_diagnostics': True})

    def test_invalid_schema1_plan_cannot_construct_fetcher(self):
        fixture = self.fixture()
        original = fixture.archive.restore
        def restore(destination):
            result = original(destination)
            path = fixture.repo / 'contracts/source-qualification-probes.json'
            plan = json.loads(path.read_bytes())
            plan['schemaVersion'] = True
            path.write_bytes(canonical(plan))
            return result
        with patch.object(fixture.archive, 'restore', side_effect=restore), \
                patch.object(collect, 'Fetcher') as factory, self.assertRaises(ValueError):
            fixture.run_probe()
        factory.assert_not_called()

    def test_actual_failed_observation_cannot_become_qualification_proof(self):
        fixture = qualification.SourceQualificationProbeTests(methodName='runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        plan, record, key = fixture.explicit_followup()
        target = record['diagnostic']['qualification']['targets'][0]
        source = {**fixture.policy['sources'][0], 'url': target['url']}
        fetch = candidate.Fetcher(fixture.store, unexpected_status_diagnostics=True)
        fetch.proxy_dns = True
        with fictional_https(response(201, b'<html><body>failed proof</body></html>')):
            failed = fetch.fetch(source)
        fixture.repin_explicit_observation(copy.deepcopy(plan), copy.deepcopy(record), key, failed)
        before = qualification.retained_files(fixture.store)
        with self.assertRaisesRegex(ValueError, 'QUALIFICATION_OBSERVATION_BODY_OR_TIME_DIFFERS'):
            fixture.validate()
        self.assertEqual(qualification.retained_files(fixture.store), before)


if __name__ == '__main__':
    unittest.main()
