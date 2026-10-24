"""Mock HTTPS responses only; diagnostic metadata cannot change redirect authority."""
import contextlib
import io
from email.message import Message
from pathlib import Path
import socket
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
import urllib.response
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'web/scripts/pipeline'),str(ROOT / 'ops/ci')]
from contracts import ContractError, canonical, digest
from storage import LocalStore
import fetcher as candidate
NOW = '2026-10-24T20:00:00Z'
URL = 'https://example.invalid/archive/'
SOURCE = {'url': URL, 'allowedHosts': ['example.invalid']}
BUILD = urllib.request.build_opener


class RedirectDiagnosticsTests(unittest.TestCase):
    def run_fetch(self, route, *, diagnostic=True, previous=None, source=None):
        module = candidate
        with tempfile.TemporaryDirectory() as directory, contextlib.ExitStack() as stack:
            store = LocalStore(Path(directory))
            calls = []
            class HTTPS(urllib.request.HTTPSHandler):
                def https_open(self, req):
                    calls.append(req.full_url)
                    result = route(req, len(calls))
                    if isinstance(result, BaseException): raise result
                    code, values, body = result
                    headers = Message()
                    for key, value in values.items(): headers[key] = value
                    response = urllib.response.addinfourl(io.BytesIO(body), headers, req.full_url, code)
                    response.msg = 'Fictional response'
                    return response
            stack.enter_context(patch.object(module.urllib.request, 'build_opener', side_effect=lambda handler: BUILD(handler, HTTPS())))
            stack.enter_context(patch.object(module, 'utcnow', return_value=NOW))
            stack.enter_context(patch.object(module.time, 'sleep'))
            stack.enter_context(patch('socket.socket.connect', side_effect=AssertionError('network')))
            fetch = module.Fetcher(store, redirect_diagnostics=diagnostic)
            fetch.proxy_dns = True
            if previous:
                previous = {**previous, 'body': store.put(b'old retained body')}
            return fetch.fetch(source or SOURCE, previous=previous), calls

    def test_default_success_http_error_redirect_loop_and_conditional_outputs_match(self):
        common = {'requestedUrl': URL, 'fetchedAt': NOW}
        def body_ref(body):
            return {'key': 'objects/' + digest(body), 'sha256': digest(body), 'bytes': len(body)}
        success = {**common, 'finalUrl': URL, 'status': 'fetched', 'httpStatus': 200,
                   'body': body_ref(b'body'), 'etag': None, 'lastModified': None, 'contentType': ''}
        previous = {'requestedUrl':URL, 'etag':'e', 'observationId':'a'*64}
        routes = [
            (lambda _r, _n:(200, {'Content-Type':'text/html', 'ETag':'e'}, b'body'), None,
             {**success, 'etag':'e', 'contentType':'text/html'}, 1),
            (lambda _r, _n:(403, {'Set-Cookie':'secret', 'Authorization':'secret'}, b'private'), None,
             {**common, 'status':'blocked', 'httpStatus':403, 'errorCode':'HTTP_403'}, 1),
            (lambda _r, _n:(302, {'Location':'/loop'}, b''), None,
             {**common, 'status':'failed', 'httpStatus':302, 'errorCode':'HTTP_302'}, 5),
            (lambda _r, _n:(304, {}, b''), previous,
             {**previous, **common, 'body':body_ref(b'old retained body'), 'status':'not_modified',
              'httpStatus':304, 'reusesObservationId':'a'*64}, 1),
            (lambda _r, n:(503, {}, b'') if n<3 else (200, {}, b'body'), None, success, 3)]
        for route, prior, expected, count in routes:
            with self.subTest(previous=prior, route=route):
                actual, calls = self.run_fetch(route, diagnostic=False, previous=prior)
                self.assertEqual(canonical(actual), canonical(expected)); self.assertEqual(len(calls), count)
                self.assertNotIn('redirectDiagnostics', actual)

    def test_relative_location_is_observed_proposed_target_is_not_follow_proof(self):
        def route(req, _n):
            return (302, {'Location':'../next', 'Set-Cookie':'do not retain'}, b'') if req.full_url==URL else (200, {}, b'body')
        result, calls = self.run_fetch(route)
        diag = result['redirectDiagnostics']; event = diag['responses'][0]
        self.assertEqual(event['responseUrl'], URL); self.assertEqual(event['rawLocation'], '../next')
        self.assertEqual(event['proposedTargetUrl'], 'https://example.invalid/next')
        self.assertEqual(event['httpStatus'], 302); self.assertEqual(event['category'], 'proposal_constructed')
        self.assertEqual(calls, [URL, 'https://example.invalid/next'])
        self.assertNotIn('followed', event); self.assertNotIn('nextRequestMade', event)
        self.assertNotIn('do not retain', str(diag)); self.assertIsNone(diag['lastHttpError'])

    def test_missing_empty_uri_and_unsupported_location_remain_distinct(self):
        cases = [({}, None), ({'Location':''}, ''), ({'URI':'/next'}, None),
                 ({'Location':'mailto:someone@example.invalid'}, 'mailto:someone@example.invalid')]
        for headers, location in cases:
            with self.subTest(headers=headers):
                result, calls = self.run_fetch(lambda _r, _n:(302, headers, b''))
                self.assertEqual(result['httpStatus'], 302); self.assertEqual(result['status'], 'failed')
                self.assertNotIn('body', result); self.assertNotIn('finalUrl', result)
                diag=result['redirectDiagnostics']
                self.assertEqual(diag['lastHttpError']['rawLocation'], location)
                if diag['responses']:
                    self.assertEqual(diag['responses'][0]['rawLocation'], location)
                if headers.get('Location', '').startswith('mailto:'):
                    self.assertEqual(diag['responses'][0]['proposedTargetUrl'], None); self.assertEqual(calls,[URL])

    def test_unsafe_and_malformed_targets_do_not_reach_second_transport(self):
        for location in ('https://evil.invalid/private', 'http://example.invalid/plain',
                         'https://127.0.0.1/private', 'https://[', 'https://example.invalid:bad/'):
            route=lambda _r,_n:(302, {'Location':location}, b'')
            with self.subTest(location=location):
                with self.assertRaises((ValueError, ContractError)):
                    self.run_fetch(route, diagnostic=False)
                result,calls=self.run_fetch(route)
                self.assertEqual(calls,[URL]); self.assertEqual(result['status'],'failed')
                self.assertEqual(result['httpStatus'],302)
                self.assertIn(result['errorCode'],('REDIRECT_POLICY_REJECTED','REDIRECT_RESPONSE_INVALID'))
                self.assertNotIn('body',result); self.assertNotIn('finalUrl',result)

    def test_default_repeat_and_total_redirect_limits_are_unchanged(self):
        for route, expected_count in ((lambda _r,_n:(302,{'Location':'/same'},b''), 5),
                                      (lambda _r,n:(302,{'Location':'/next-'+str(n)},b''), 11)):
            expected,old_calls=self.run_fetch(route,diagnostic=False)
            result,calls=self.run_fetch(route)
            self.assertEqual(calls,old_calls); self.assertEqual(result['httpStatus'],expected['httpStatus'])
            self.assertEqual(len(calls),expected_count); self.assertEqual(result['status'],'failed')
            self.assertTrue(result['redirectDiagnostics']['responses'])
            self.assertEqual(candidate.DiagnosticContractRedirect.max_repeats,candidate.ContractRedirect.max_repeats)
            self.assertEqual(candidate.DiagnosticContractRedirect.max_redirections,candidate.ContractRedirect.max_redirections)

    def test_bounded_metadata_does_not_expand_transport(self):
        location='/'+'x'*9000
        result,calls=self.run_fetch(lambda _r,n:(302,{'Location':location},b'') if n==1 else (200,{},b'body'))
        event=result['redirectDiagnostics']['responses'][0]
        self.assertEqual(event['rawLocationLength'],len(location)); self.assertTrue(event['rawLocationTruncated'])
        self.assertEqual(len(event['rawLocation']),4096); self.assertEqual(len(event['proposedTargetUrl']),4096)
        self.assertEqual(len(calls),2)
        handler=candidate.DiagnosticContractRedirect(['example.invalid'],True)
        req=urllib.request.Request(URL)
        for _ in range(70):
            with patch.object(candidate.ContractRedirect,'http_error_302',return_value=None):
                handler.http_error_302(req,None,302,'fixture',Message())
        self.assertEqual(len(handler.responses),64); self.assertTrue(handler.truncated)

    def test_network_failure_after_proposal_has_metadata_without_follow_claim(self):
        result,calls=self.run_fetch(lambda _r,n:(302,{'Location':'/next'},b'') if n==1 else urllib.error.URLError('unavailable'))
        self.assertEqual(len(calls),2); self.assertEqual(result['status'],'failed')
        self.assertIsNone(result['httpStatus']); self.assertNotIn('body',result)
        self.assertEqual(result['redirectDiagnostics']['responses'][0]['category'],'proposal_constructed')

    def test_retry_keeps_prior_redirect_responses_without_extra_attempts(self):
        def route(req,n):
            if req.full_url==URL:return (302,{'Location':'/next'},b'')
            return (503,{},b'') if n<5 else (200,{},b'body')
        result,calls=self.run_fetch(route)
        expected,old_calls=self.run_fetch(route,diagnostic=False)
        self.assertEqual(calls,old_calls); self.assertEqual(result['status'],expected['status'])
        self.assertEqual(len(result['redirectDiagnostics']['responses']),3)
        self.assertEqual(result['redirectDiagnostics']['lastHttpError']['httpStatus'],503)

    def test_304_does_not_copy_prior_redirects_into_new_diagnostic_evidence(self):
        previous = {'requestedUrl': URL, 'etag': 'e', 'observationId': 'a'*64,
                    'redirectDiagnostics': {'schemaVersion': 1, 'responses': [{'old': True}],
                                            'responsesTruncated': False, 'lastHttpError': None}}
        result, calls = self.run_fetch(lambda _r,_n:(304,{},b''), previous=previous)
        self.assertEqual(len(calls),1); self.assertEqual(result['reusesObservationId'],'a'*64)
        self.assertNotIn('redirectDiagnostics',result)
        default, _ = self.run_fetch(lambda _r,_n:(304,{},b''), previous=previous, diagnostic=False)
        self.assertEqual(default['redirectDiagnostics'],previous['redirectDiagnostics'])

    def test_private_allowed_host_is_still_rejected_before_transport(self):
        source = {**SOURCE, 'allowedHosts': ['example.invalid', '127.0.0.1']}
        result,calls=self.run_fetch(lambda _r,_n:(302,{'Location':'https://127.0.0.1/private'},b''), source=source)
        self.assertEqual(calls,[URL]); self.assertEqual(result['errorCode'],'REDIRECT_POLICY_REJECTED')
        self.assertEqual(result['redirectDiagnostics']['responses'][0]['category'],'policy_rejected')

    def test_opt_in_type_is_exact_boolean(self):
        with self.assertRaises(ContractError):
            candidate.Fetcher(None,redirect_diagnostics=1)


class OrcaRedirectRouteTests(unittest.TestCase):
    def test_only_exact_orca_route_opts_in(self):
        import collect
        import test_leased_orca_probe as leased_orca
        fixture = leased_orca.LeasedOrcaProbeTests(methodName='runTest')
        fixture.setUp()
        try:
            with patch.object(collect, 'Fetcher', side_effect=fixture.transport) as factory:
                result=fixture.run_probe()
            self.assertEqual(factory.call_args.kwargs, {'timeout':12, 'redirect_diagnostics':True})
            self.assertFalse(result['coverageCredit'])
        finally:
            fixture.doCleanups()

    def test_existing_generic_route_keeps_default_constructor(self):
        import collect
        import test_leased_source_probe as leased
        fixture=leased.LeasedSourceProbeTests(methodName='runTest')
        fixture.setUp()
        try:
            with patch.object(collect, 'Fetcher', side_effect=fixture.transport) as factory:
                result=fixture.run_probe()
            self.assertEqual(factory.call_args.kwargs, {'timeout':12})
            self.assertFalse(result['coverageCredit'])
        finally:
            fixture.doCleanups()

    def test_redirect_metadata_cannot_supply_missing_index_body_or_completion(self):
        import test_orca_qualification as fixtures
        fixture=fixtures.OrcaQualificationTests(methodName='runTest')
        fixture.setUp()
        try:
            fetch=fixtures.Fetcher(fixture)
            def failed(source,url):
                fetch.calls.append((source['id'],url))
                return {'requestedUrl':url,'fetchedAt':fixture.clock.wall,'status':'failed',
                        'httpStatus':302,'errorCode':'HTTP_302',
                        'redirectDiagnostics':{'schemaVersion':1,'responses':[
                            {'httpStatus':302,'responseUrl':url,'rawLocation':'/terminal/',
                             'proposedTargetUrl':'https://orca.security/terminal/',
                             'category':'proposal_constructed'}],
                             'responsesTruncated':False,'lastHttpError':None}}
            fetch.fetch=failed
            report=fixture.run_report(fetch)
            self.assertFalse(report['indexComplete']);self.assertFalse(report['evidenceComplete'])
            self.assertFalse(fixture.verify(report)['evidenceComplete'])
            self.assertEqual(report['reason'],'ORCA_RESPONSE_INCOMPLETE')
            self.assertEqual(report['facts'],[]);self.assertFalse(report['qualified'])
        finally:
            fixture.doCleanups()


if __name__=='__main__':unittest.main()
