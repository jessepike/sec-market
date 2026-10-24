"""Fictional Orca transport through the real lease/escrow/CAS entry point."""
import copy
import json
import signal
import unittest
from unittest.mock import patch

import collect
from contracts import canonical, digest
from storage import LocalStore
import orca_qualification as orca
import test_leased_source_probe as leased
import test_orca_qualification as fixtures


class LeasedOrcaProbeTests(unittest.TestCase):
    def setUp(self):
        self.h = leased.LeasedSourceProbeTests(methodName='runTest')
        self.h.setUp(); self.addCleanup(self.h.doCleanups)
        self.f = fixtures.OrcaQualificationTests(methodName='runTest')
        self.f.setUp(); self.addCleanup(self.f.doCleanups)
        self.h.policy = self.f.contract
        (self.h.repo / 'contracts/market.json').write_bytes(canonical(self.f.contract))
        self.callback = None
        self.state_for_transport = None
        self.calls = []

        def seed(state, _policy, path):
            for source in self.f.store.root.rglob('*'):
                if source.is_file():
                    state.write_once(source.relative_to(self.f.store.root).as_posix(), source.read_bytes())
            path.write_bytes(self.f.path.read_bytes())
        self.h.stack.enter_context(patch.object(leased, 'seed_qualification_plan', side_effect=seed))

        original_push = self.h.archive.push
        def acknowledged(state, expected_commit=None):
            result = original_push(state, expected_commit=expected_commit)
            # Match GitArchive.push's actual interface, which has no sha256 key.
            return {'commit': result['commit'], 'parentCommit': expected_commit,
                    'manifestSha256': 'd' * 64, 'files': 123, 'ref': 'archive'}
        self.h.stack.enter_context(patch.object(self.h.archive, 'push', side_effect=acknowledged))
        self.h.stack.enter_context(patch.object(collect, 'Fetcher', side_effect=self.transport))

    def transport(self, state, **_kwargs):
        self.state_for_transport = state
        outer = self
        class Transport:
            def fetch(self, source, url):
                outer.h.events.append('fetch'); outer.calls.append((source['id'], url))
                outer.assertGreaterEqual(len(outer.h.pushes), 2)
                outer.assertEqual(outer.h.pushes[1]['budget'], {**outer.h.seed, 'fetches': 5500})
                outer.f.store = state; outer.f.clock.wall = outer.h.clock.now()
                if outer.callback: outer.callback(source, url)
                outer.f.clock.wall = outer.h.clock.now()
                return fixtures.Fetcher(outer.f).fetch(source, url)
        return Transport()

    def run_probe(self):
        return self.h.run_probe()

    def replay(self, result):
        state = self.h.state()
        raw = (state.root / 'ci/source-probe-runs/123-2.json').read_bytes()
        ref = {'key': 'ci/source-probe-runs/123-2.json', 'sha256': digest(raw), 'bytes': len(raw)}
        with patch.object(state, 'put', side_effect=AssertionError('write')), \
             patch.object(state, 'write_once', side_effect=AssertionError('write')), \
             patch('socket.socket.connect', side_effect=AssertionError('network')):
            return orca.replay_diagnostic(self.f.contract, state, ref, result['diagnostic']['planReference'])

    def test_real_route_lease_escrow_cas_and_original_plan_after_disable(self):
        result = self.run_probe()
        self.assertTrue(result['diagnostic']['evidenceComplete'])
        self.assertEqual(self.calls, [(orca.SOURCE_ID, u) for u in
            (orca.INDEX, orca.INDEX + 'page/2/', 'https://orca.security/resources/press-releases/release-1/')])
        self.assertEqual(self.h.events, ['restore', 'push', 'push', 'fetch', 'fetch', 'fetch', 'push'])
        self.assertEqual([p['expected'] for p in self.h.pushes], ['b'*40, f'{1:040x}', f'{2:040x}'])
        self.assertEqual(self.h.state().read('heads/budget-2026-10-23.json'), {**self.h.seed, 'fetches': 11})
        disabled = canonical({'schemaVersion': 2, 'operation': 'disabled_qualification_probe',
            'marketSha256': orca.POLICY_SHA256, 'maxRequests': 0, 'sources': []})
        self.assertEqual(digest(disabled), 'ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4')
        (self.h.repo / 'contracts/source-qualification-probes.json').write_bytes(disabled)
        self.assertTrue(self.replay(result)['readiness']['evidenceComplete'])
        self.assertFalse(result['coverageCredit']); self.assertEqual(result['modelCalls'], 0)
        self.h.assert_preserved()

    def test_caller_expiry_reconstructs_readiness_with_no_refund(self):
        original = orca.execute
        def expires(*args):
            report = original(*args); self.assertTrue(report['evidenceComplete'])
            self.h.clock.elapsed = 60
            return report
        with patch.object(orca, 'execute', side_effect=expires): result = self.run_probe()
        report = result['diagnostic']
        self.assertFalse(report['evidenceComplete']); self.assertTrue(report['indexComplete'])
        self.assertFalse(result['executionCompleted'])
        self.assertEqual(len(report['completionDenials']), 1)
        self.assertEqual(report['reservationContext']['probeFetchReservations'], 3)
        self.assertFalse(self.replay(result)['readiness']['evidenceComplete'])
        self.h.assert_preserved()

    def test_repeated_module_and_caller_denials_keep_exact_counter(self):
        self.callback = lambda _s, u: setattr(self.h.clock, 'elapsed', 60) if not u.startswith(orca.INDEX) else None
        result = self.run_probe(); report = result['diagnostic']
        self.assertEqual(len(report['completionDenials']), 2)
        reason = report['completionDenials'][0]
        self.assertEqual(report['completionDenials'], [reason, reason])
        self.assertEqual(report['reservationContext']['reservationDenials'], {reason: 2})
        self.assertEqual(report['reason'], reason); self.assertFalse(report['evidenceComplete'])
        self.assertFalse(self.replay(result)['readiness']['evidenceComplete'])
        forged = copy.deepcopy(report); forged['completionDenials'].pop()
        with self.assertRaises(ValueError):
            orca.verify_report(self.f.contract, self.h.state(), self.f.path.read_bytes(), forged)
        self.h.assert_preserved()

    def test_caller_midnight_never_reserves_on_next_day(self):
        self.h.clock.current = '2026-10-23T23:59:59Z'
        original = orca.execute
        def rollover(*args):
            report = original(*args); self.h.clock.current = '2026-10-24T00:00:00Z'; return report
        with patch.object(orca, 'execute', side_effect=rollover): result = self.run_probe()
        self.assertFalse(result['executionCompleted']); self.assertFalse(result['diagnostic']['evidenceComplete'])
        self.assertIn('DAY', result['diagnostic']['completionDenial'])
        self.assertIsNone(self.h.state().read('heads/budget-2026-10-24.json'))
        self.assertFalse(self.replay(result)['readiness']['evidenceComplete'])
        self.h.assert_preserved()

    def test_cancelled_inflight_response_is_retained_and_no_followup(self):
        self.callback = lambda _s, _u: signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
        result = self.run_probe()
        self.assertEqual(result['outcome'], 'cancelled'); self.assertFalse(result['executionCompleted'])
        self.assertEqual(len(self.calls), 1)
        self.assertIsNotNone(result['diagnostic']['requests'][0]['observation'])
        self.assertFalse(self.replay(result)['readiness']['evidenceComplete'])
        self.h.assert_preserved()

    def test_tampered_plan_or_proof_before_escrow_has_zero_transport(self):
        restore = self.h.archive.restore
        def bad(destination):
            result = restore(destination)
            path = self.h.repo / 'contracts/source-qualification-probes.json'
            plan = json.loads(path.read_bytes()); plan['maxRequests'] = 62
            path.write_bytes(canonical(plan)); return result
        with patch.object(self.h.archive, 'restore', side_effect=bad), self.assertRaises(ValueError): self.run_probe()
        self.assertEqual(self.calls, []); self.assertTrue(all(p['budget'] == self.h.seed for p in self.h.pushes))
        self.h.assert_preserved()

    def test_tampered_original_body_before_escrow_has_zero_transport(self):
        restore = self.h.archive.restore
        def bad(destination):
            result = restore(destination)
            (LocalStore(destination).root / orca.START_PROOF['body']['key']).write_bytes(b'tampered')
            return result
        with patch.object(self.h.archive, 'restore', side_effect=bad), self.assertRaises(ValueError): self.run_probe()
        self.assertEqual(self.calls, []); self.assertTrue(all(p['budget'] == self.h.seed for p in self.h.pushes))
        self.h.assert_preserved()

    def test_plan_replacement_during_escrow_denies_before_reservation(self):
        push = self.h.archive.push
        def changed(state, expected_commit=None):
            result = push(state, expected_commit=expected_commit)
            if len(self.h.pushes) == 2:
                (self.h.repo / 'contracts/source-qualification-probes.json').write_bytes(b'{}')
            return result
        with patch.object(self.h.archive, 'push', side_effect=changed), self.assertRaisesRegex(ValueError, 'CURRENT_PLAN_CHANGED'):
            self.run_probe()
        self.assertEqual(self.calls, [])
        self.assertEqual(self.h.state().read('heads/budget-2026-10-23.json'), self.h.seed)
        self.h.assert_preserved()

    def test_escrow_or_final_archive_failure_cannot_return_success(self):
        self.h.fail_push_at = 2
        with self.assertRaises(RuntimeError): self.run_probe()
        self.assertEqual(self.calls, [])
        self.assertEqual(self.h.state().read('heads/budget-2026-10-23.json'), {**self.h.seed, 'fetches': 5500})
        self.h.assert_preserved()

    def test_final_archive_failure_retains_charges_but_has_no_success_return(self):
        self.h.fail_push_at = 3
        with self.assertRaises(RuntimeError): self.run_probe()
        self.assertEqual(len(self.calls), 3)
        self.assertEqual(self.h.state().read('heads/budget-2026-10-23.json'), {**self.h.seed, 'fetches': 11})
        self.h.assert_preserved()

    def test_full_day_cap_never_calls_transport(self):
        self.h.seed['fetches'] = 5500
        result = self.run_probe()
        self.assertEqual(self.calls, []); self.assertFalse(result['executionCompleted'])
        self.assertFalse(self.replay(result)['readiness']['evidenceComplete'])
        self.h.assert_preserved()


if __name__ == '__main__':
    unittest.main()
