"""Adversarial byte/inventory tests; none determines a semantic verdict."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('claim_reviews', Path(__file__).resolve().parents[1] / 'evaluation/claim_reviews.py')
reviews = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reviews)
from storage import LocalStore


class ReviewBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        self.state = LocalStore(Path(self.temp.name) / 'state')
        self.statement = 'Acme announced an agreement for $10 million, subject to approval.'
        body = self.state.put(('<html><body>' + self.statement + '</body></html>').encode())
        self.oid = 'a' * 64
        self.observation = {'observationId': self.oid, 'requestedUrl': 'https://example.invalid/release',
                            'finalUrl': 'https://example.invalid/release', 'fetchedAt': '2026-10-20T01:00:00Z',
                            'status': 'fetched', 'body': body}
        self.state.write_once('observations/' + self.oid + '.json', self.observation)
        self.events = [{'id': 'EV-a', 'supplierId': 'acme', 'date': '2026-10-19', 'text': self.statement, 'evidenceIds': ['E']},
                       {'id': 'EV-z', 'supplierId': 'zen', 'date': '2026-10-19', 'text': self.statement, 'evidenceIds': ['E']}]
        field = {'relationship': 'Agreement announced', 'evidenceIds': ['E']}
        self.suppliers = [{'id': 'private', 'ownership': field}, {'id': 'public', 'edgarId': 'public', 'ownership': field}]
        self.write_source(reviews.EVENTS, 'handCollectedEvents', self.events)
        self.write_source(reviews.SUPPLIERS, 'manualTrackerSuppliers', self.suppliers)
        (self.root / reviews.EVIDENCE).write_text('export const evidence = []\n')
        self.inventory = {'applicationRevision': 'b' * 40,
                          'createdAt': '2026-10-23T18:00:00Z',
                          'sourceFiles': {p: reviews.digest((self.root / p).read_bytes()) for p in (reviews.EVENTS, reviews.SUPPLIERS, reviews.EVIDENCE)},
                          'records': [{'id': 'event:EV-a', 'supplierId': 'acme', 'partition': 'events_a_m', 'published': self.events[0]},
                                      {'id': 'event:EV-z', 'supplierId': 'zen', 'partition': 'events_n_z', 'published': self.events[1]},
                                      {'id': 'supplier:private:ownership', 'supplierId': 'private', 'field': 'ownership', 'partition': 'supplier_fields', 'published': field}],
                          'evidence': [{'id': 'E', 'canonicalUrl': self.observation['requestedUrl']}]}
        proof = {'evidenceId': 'E', 'url': self.observation['requestedUrl'], 'observationId': self.oid,
                 'fetchedAt': self.observation['fetchedAt'], 'bodySha256': body['sha256'],
                 'bodyPath': '/untrusted/path/is/ignored', 'sourceType': 'primary', 'support': {'excerpts': [self.statement]}}
        self.ledgers = {}
        for partition in sorted(reviews.PARTITIONS):
            row = next(r for r in self.inventory['records'] if r['partition'] == partition)
            dataset = reviews.SUPPLIERS if partition == 'supplier_fields' else reviews.EVENTS
            self.ledgers[partition] = {'schemaVersion': 1, 'kind': 'archived_published_claim_review',
                'evaluatedAt': '2026-10-23T18:30:00Z',
                'datasetPath': dataset, 'datasetFileSha256': self.inventory['sourceFiles'][dataset],
                'evidenceDatasetPath': reviews.EVIDENCE, 'evidenceDatasetFileSha256': self.inventory['sourceFiles'][reviews.EVIDENCE],
                'inventoryCount': 1, 'reviewedCount': 1, 'expectedRecordIds': [row['id']],
                'records': [{'id': row['id'], 'supplierId': row['supplierId'], 'published': row['published'],
                             'verdict': 'supported', 'sourceEvidence': [copy.deepcopy(proof)], 'limitations': ['Historical only']}]}
        self.manifest = {'schemaVersion': 1, 'evaluatedAt': '2026-10-23T19:00:00Z', 'inputs': {}}
        self.repin()

    def write_source(self, path, name, value):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('export const ' + name + ': Thing[] = ' + json.dumps(value) + '\nthrow new Error("must never execute")\n')

    def pin(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
        return {'path': name, 'sha256': reviews.digest(path.read_bytes())}

    def repin(self):
        self.manifest['inputs'] = {'inventory': self.pin('inventory.json', self.inventory),
            'reviews': {p: self.pin(p + '.json', data) for p, data in self.ledgers.items()}}

    def evaluate(self):
        return reviews.evaluate(self.root, self.state.root, self.manifest)

    def test_decodes_frozen_arrays_without_executing_typescript_and_keeps_semantics_separate(self):
        self.ledgers['events_a_m']['records'][0]['verdict'] = 'contradicted'
        self.repin()
        before = sorted(str(p) for p in self.state.root.rglob('*'))
        report = self.evaluate()
        self.assertEqual(report['inventoryCount'], 3)
        self.assertEqual(report['verdictCounts']['contradicted'], 1)
        self.assertFalse(report['semanticVerdictsIndependentlyVerified'])
        self.assertTrue(report['bindingChecksPassed'])
        self.assertEqual(before, sorted(str(p) for p in self.state.root.rglob('*')))

    def test_changed_dataset_and_forged_frozen_record_fail(self):
        source = self.root / reviews.EVENTS
        source.write_text(source.read_text().replace('$10 million', '$20 million'))
        with self.assertRaisesRegex(ValueError, 'Dataset hash differs'):
            self.evaluate()

    def test_changed_inventory_cannot_change_the_decoded_published_records(self):
        self.inventory['records'][0]['published'] = {**self.events[0], 'text': 'forged'}
        self.repin()
        with self.assertRaisesRegex(ValueError, 'Frozen inventory differs'):
            self.evaluate()

    def test_omitted_and_duplicate_records_fail_even_with_updated_review_hashes(self):
        ledger = self.ledgers['events_a_m']
        original = copy.deepcopy(ledger['records'])
        for rows in ([], original + original):
            ledger['records'] = rows
            self.repin()
            with self.assertRaisesRegex(ValueError, 'omission or duplicate'):
                self.evaluate()

    def test_wrong_url_and_changed_observation_time_fail(self):
        proof = self.ledgers['events_a_m']['records'][0]['sourceEvidence'][0]
        proof['url'] = 'https://evil.invalid/other'
        self.repin()
        with self.assertRaisesRegex(ValueError, 'canonical URL differs'):
            self.evaluate()
        proof['url'] = self.observation['requestedUrl']
        proof['fetchedAt'] = '2026-10-23T01:00:00Z'
        self.repin()
        with self.assertRaisesRegex(ValueError, 'fetch time differs'):
            self.evaluate()

    def test_modified_source_body_and_invented_quote_fail(self):
        proof = self.ledgers['events_a_m']['records'][0]['sourceEvidence'][0]
        proof['support']['excerpts'] = ['Acquisition completed without conditions.']
        self.repin()
        with self.assertRaisesRegex(ValueError, 'excerpt not in source'):
            self.evaluate()
        proof['support']['excerpts'] = [self.statement]
        self.repin()
        (self.state.root / self.observation['body']['key']).write_bytes(b'changed bytes')
        with self.assertRaisesRegex(ValueError, 'integrity verification'):
            self.evaluate()

    def test_arbitrary_local_fixture_is_not_a_primary_exception(self):
        proof = self.ledgers['events_a_m']['records'][0]['sourceEvidence'][0]
        proof['observationId'] = None
        proof['bodyPath'] = 'arbitrary.html'
        (self.root / 'arbitrary.html').write_text(self.statement)
        self.repin()
        with self.assertRaisesRegex(ValueError, 'Unbound local fixture'):
            self.evaluate()

    def test_fixture_descriptor_cannot_substitute_arbitrary_bytes_for_known_primary(self):
        fake = b'Arbitrary local text'
        target = self.root / reviews.FIXTURE
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(fake)
        provenance = {'kind': 'retained_manual_primary_evidence', 'provenanceReceipt': reviews.RECEIPT,
                      'fixtures': [{'file': 'press-release.html', 'sha256': reviews.FIXTURE_SHA,
                                    'sourceUrl': reviews.FIXTURE_URL, 'bytes': len(fake),
                                    'originalRetrievalRecordedAt': '2026-10-23T03:57:13Z'}]}
        receipt = self.root / reviews.RECEIPT
        receipt.parent.mkdir(parents=True, exist_ok=True)
        receipt.write_text('Known earlier proof: ' + reviews.FIXTURE_SHA)
        self.manifest['retainedPrimary'] = {
            'provenance': self.pin(reviews.PROVENANCE, provenance),
            'receipt': {'path': reviews.RECEIPT, 'sha256': reviews.digest(receipt.read_bytes())}}
        proof = {'proofKind': 'retained_primary_fixture', 'evidenceId': reviews.FIXTURE_ID,
                 'bodyPath': reviews.FIXTURE, 'provenanceReceipt': reviews.RECEIPT,
                 'bodySha256': reviews.FIXTURE_SHA, 'url': reviews.FIXTURE_URL,
                 'fetchedAt': '2026-10-23T03:57:13Z'}
        with self.assertRaisesRegex(ValueError, 'fixture bytes differ'):
            reviews.retained_fixture(self.root, self.manifest, proof)

    def test_changed_pinned_review_is_rejected_before_assessing_its_contents(self):
        target = self.root / self.manifest['inputs']['reviews']['events_a_m']['path']
        target.write_text(target.read_text() + '\n')
        with self.assertRaisesRegex(ValueError, 'Input hash mismatch'):
            self.evaluate()

    def test_review_time_is_required_valid_and_not_after_manifest_time(self):
        ledger = self.ledgers['events_a_m']
        for value in (None, 'not-a-date', '2026-10-23T19:00:01Z'):
            ledger['evaluatedAt'] = value
            self.repin()
            with self.assertRaises(ValueError):
                self.evaluate()
        ledger['evaluatedAt'] = self.manifest['evaluatedAt']
        self.repin()
        self.assertTrue(self.evaluate()['bindingChecksPassed'])

    def test_future_proof_times_and_inventory_creation_are_held(self):
        proof = self.ledgers['events_a_m']['records'][0]['sourceEvidence'][0]
        for field in ('fetchedAt', 'sourceVerifiedAt'):
            previous = proof.get(field)
            proof[field] = '2026-10-23T19:00:01Z'
            self.repin()
            with self.assertRaisesRegex(ValueError, 'Proof timestamp after audit'):
                self.evaluate()
            if previous is None:
                proof.pop(field)
            else:
                proof[field] = previous
        self.repin()
        observation_path = self.state.root / ('observations/' + self.oid + '.json')
        observation_path.write_text(json.dumps({**self.observation, 'verifiedAt': '2026-10-23T19:00:01Z'}))
        with self.assertRaisesRegex(ValueError, 'Observation verification after audit'):
            self.evaluate()
        observation_path.write_text(json.dumps(self.observation))
        self.inventory['createdAt'] = '2026-10-23T19:00:01Z'
        self.repin()
        with self.assertRaisesRegex(ValueError, 'Inventory created after audit'):
            self.evaluate()

    def test_cli_refuses_existing_report_before_any_input_reads(self):
        prefix = Path(self.temp.name) / 'report'
        Path(str(prefix) + '.md').write_text('preserve')
        argv = ['claim_reviews.py', '--root', str(self.root), '--state', str(self.state.root),
                '--manifest', '/nonexistent', '--outputprefix', str(prefix)]
        with patch.object(sys, 'argv', argv), self.assertRaisesRegex(ValueError, 'Refusing to overwrite'):
            reviews.main()
        self.assertEqual(Path(str(prefix) + '.md').read_text(), 'preserve')

    def test_supplemental_source_requires_explicit_label_and_observation_binding(self):
        proof = copy.deepcopy(self.ledgers['events_a_m']['records'][0]['sourceEvidence'][0])
        proof['evidenceId'] = None
        self.ledgers['events_a_m']['records'][0]['sourceEvidence'].append(proof)
        self.repin()
        with self.assertRaisesRegex(ValueError, 'Unlabeled supplemental'):
            self.evaluate()
        proof['relationship'] = 'supplemental_archived_primary'
        self.repin()
        self.assertTrue(self.evaluate()['bindingChecksPassed'])


if __name__ == '__main__':
    unittest.main()
