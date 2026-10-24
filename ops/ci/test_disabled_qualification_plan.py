"""Offline tests for the explicit disabled qualification plan operation."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))

from contracts import canonical, digest
import onboarding
from onboarding import (DISABLED_QUALIFICATION_OPERATION, PersistentProbeBudget,
                        probe_sources, validate_qualification_probe_plan)
from storage import LocalStore


NOW = '2026-10-24T12:00:00Z'


class Clock:
    def __init__(self):
        self.elapsed = 0

    def now(self):
        return NOW

    def monotonic(self):
        return self.elapsed


class NoTransport:
    def __init__(self):
        self.calls = []

    def fetch(self, source, url):
        self.calls.append((source, url))
        raise AssertionError('disabled qualification operation attempted transport')


class DisabledQualificationPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = LocalStore(self.root / 'state')
        self.contract = json.loads((ROOT / 'contracts/market.json').read_text())
        self.path = self.root / 'plan.json'
        self.clock = Clock()

    def plan(self):
        return {'schemaVersion': 2, 'operation': DISABLED_QUALIFICATION_OPERATION,
                'marketSha256': digest(self.contract), 'maxRequests': 0, 'sources': []}

    def write_plan(self, plan):
        self.path.write_bytes(canonical(plan))

    def budget(self):
        return PersistentProbeBudget(self.store, self.contract, clock=self.clock.now,
                                     monotonic=self.clock.monotonic)

    def test_exact_plan_returns_retained_zero_request_diagnostic(self):
        plan = self.plan()
        raw = canonical(plan)
        self.path.write_bytes(raw)
        validated = validate_qualification_probe_plan(self.contract, self.store, self.path)
        fetcher = NoTransport()
        budget = self.budget()
        before = self.store.read('heads/budget-2026-10-24.json')

        report = probe_sources(self.contract, self.store, fetcher, reservation_context=budget,
                               qualification_plan_path=self.path)

        self.assertEqual(fetcher.calls, [])
        self.assertEqual(report['operation'], DISABLED_QUALIFICATION_OPERATION)
        self.assertTrue(report['disabled'])
        self.assertTrue(report['executionCompleted'])
        self.assertFalse(report['budgetDenied'])
        self.assertEqual(report['contractSha256'], digest(self.contract))
        self.assertEqual(report['planRawSha256'], digest(raw))
        self.assertEqual(report['planCanonicalSha256'], digest(plan))
        self.assertEqual(report['planReference'], self.store.put(raw))
        self.assertEqual(self.store.get(report['planReference']), raw)
        self.assertEqual(report['startedAt'], NOW)
        self.assertEqual(report['checkedAt'], NOW)
        self.assertEqual(report['sources'], [])
        self.assertEqual(report['maxRequests'], 0)
        self.assertEqual(report['facts'], [])
        self.assertEqual(report['newFactIds'], [])
        self.assertEqual(report['modelCalls'], 0)
        self.assertEqual(report['sourceChecksCredited'], 0)
        self.assertEqual(report['qualifiedSources'], 0)
        self.assertFalse(report['qualified'])
        self.assertFalse(report['semanticAdmission'])
        self.assertFalse(report['coverageCredit'])
        context = report['reservationContext']
        self.assertEqual(context['contractSha256'], digest(self.contract))
        self.assertEqual(context['budgetDay'], '2026-10-24')
        self.assertEqual(context['probeFetchReservations'], 0)
        self.assertEqual(context['reservationDenials'], {})
        self.assertEqual(context['initialBudget'], before)
        self.assertEqual(context['currentBudget'], before)
        self.assertEqual(validated['rawSha256'], digest(raw))
        self.assertEqual(validated['operation'], DISABLED_QUALIFICATION_OPERATION)

    def test_invalid_disabled_shapes_reject_before_transport(self):
        cases = {
            'missing operation': lambda p: p.pop('operation'),
            'unknown operation': lambda p: p.update(operation='generic_probe'),
            'extra field': lambda p: p.update(targets=[]),
            'stale policy': lambda p: p.update(marketSha256='0' * 64),
            'boolean allowance': lambda p: p.update(maxRequests=False),
            'nonzero allowance': lambda p: p.update(maxRequests=1),
            'nonempty sources': lambda p: p.update(sources=[{'id': 'unexpected'}]),
            'boolean schema version': lambda p: p.update(schemaVersion=True),
        }
        for name, corrupt in cases.items():
            with self.subTest(name=name):
                plan = self.plan()
                corrupt(plan)
                self.write_plan(plan)
                fetcher = NoTransport()
                with self.assertRaises(ValueError):
                    probe_sources(self.contract, self.store, fetcher, reservation_context=self.budget(),
                                  qualification_plan_path=self.path)
                self.assertEqual(fetcher.calls, [])

    def test_unknown_schema_two_operation_cannot_fall_through_to_generic_probe(self):
        plan = self.plan()
        plan['operation'] = 'unrecognized'
        self.write_plan(plan)
        fetcher = NoTransport()
        with self.assertRaisesRegex(ValueError, 'QUALIFICATION_PLAN_OPERATION_UNKNOWN'):
            probe_sources(self.contract, self.store, fetcher, reservation_context=self.budget(),
                          qualification_plan_path=self.path)
        self.assertEqual(fetcher.calls, [])

    def test_plan_changed_after_validation_is_rejected_before_archive_or_transport(self):
        self.write_plan(self.plan())
        original_validator = onboarding.validate_qualification_probe_plan

        def validate_then_change(contract, store, path):
            validated = original_validator(contract, store, path)
            changed = self.plan()
            changed['maxRequests'] = 1
            self.write_plan(changed)
            return validated

        fetcher = NoTransport()
        with patch('onboarding.validate_qualification_probe_plan', side_effect=validate_then_change):
            with self.assertRaisesRegex(ValueError, 'QUALIFICATION_CURRENT_PLAN_CHANGED_AFTER_VALIDATION'):
                probe_sources(self.contract, self.store, fetcher, reservation_context=self.budget(),
                              qualification_plan_path=self.path)
        self.assertEqual(fetcher.calls, [])
        self.assertEqual(list((self.store.root / 'objects').glob('*')), [])


if __name__ == '__main__':
    unittest.main()
