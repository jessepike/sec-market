"""D-138 / SEC-083: the additive roster transition inverts to J exactly and refuses anything else."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from contracts import ContractError, digest, validate_contract
import roster_transition as roster

J = '47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a'


class RosterTransitionTests(unittest.TestCase):
    def setUp(self):
        self.market = json.loads((ROOT / 'contracts/market.json').read_bytes())
        self.transition = roster.load_transition()

    def test_current_contract_is_j_or_its_declared_successor(self):
        validate_contract(copy.deepcopy(self.market))
        self.assertEqual(digest(roster.base_contract(self.market)), J)
        if digest(self.market) != J:
            self.assertEqual(digest(self.market), self.transition['activatedContractSha256'])

    def test_additions_are_only_new_suppliers_and_sources(self):
        base = roster.base_contract(self.market)
        old_suppliers = {s['id'] for s in base['suppliers']}
        self.assertFalse(old_suppliers & set(self.transition['addedSuppliers']))
        self.assertFalse({s['id'] for s in base['sources']} & set(self.transition['addedSources']))
        self.assertEqual(len(self.market['suppliers']), len(base['suppliers']) + len(self.transition['addedSuppliers']))

    def test_onboarding_suppliers_match_the_site_seed_records(self):
        seeds = json.loads((ROOT / 'web/src/data/tracker/onboarding.json').read_bytes())
        self.assertEqual(sorted(s['id'] for s in seeds['suppliers']), sorted(self.transition['addedSuppliers']))

    def test_any_change_to_an_existing_row_is_refused(self):
        if digest(self.market) == J:
            self.skipTest('No successor declared')
        tampered = copy.deepcopy(self.market)
        target = next(s for s in tampered['sources'] if s['id'] not in self.transition['addedSources'])
        target['maxPages'] += 1
        with self.assertRaises(ContractError):
            roster.base_contract(tampered)
        # Even with a matching declared hash, the inverse must still be J.
        forged = dict(self.transition, activatedContractSha256=digest(tampered))
        with self.assertRaises(ContractError):
            roster.base_contract(tampered, forged)

    def test_undeclared_addition_is_refused(self):
        extra = copy.deepcopy(self.market)
        source = copy.deepcopy(extra['sources'][0])
        source['id'] = source['supplierId'] + ':official:99'
        extra['sources'].append(source)
        next(s for s in extra['suppliers'] if s['id'] == source['supplierId'])['sourceIds'].append(source['id'])
        with self.assertRaises(ContractError):
            roster.base_contract(extra)
        forged = dict(self.transition, activatedContractSha256=digest(extra))
        with self.assertRaises(ContractError):
            roster.base_contract(extra, forged)

    def test_authority_contract_passes_other_contracts_through(self):
        other = copy.deepcopy(self.market)
        other['version'] = 'synthetic'
        self.assertIs(roster.authority_contract(other), other)


if __name__ == '__main__':
    unittest.main()
