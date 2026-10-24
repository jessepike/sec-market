import copy
import unittest
from coverage_summary import coverage_details, MEASURE
from collect import execution_outcome


def separated_coverage():
    return {'schemaVersion': 2, 'measure': MEASURE, 'successfulTasks': 1, 'requiredTasks': 1,
            'complete': True, 'gapTaskIds': [],
            'intake': {'measure': MEASURE, 'evaluated': True, 'status': 'collected',
                       'successfulTasks': 1, 'requiredTasks': 1, 'complete': True, 'gapTaskIds': []},
            'processing': {'complete': False, 'inventoryDocuments': 3, 'reviewedDocuments': 1,
                           'pendingDocuments': 2, 'heldDocuments': 1, 'changedDocuments': 2, 'unknownDateDocuments': 1},
            'historicalReview': {'complete': False, 'inventoryDocuments': 20, 'reviewedDocuments': 2,
                                 'pendingDocuments': 18, 'heldDocuments': 1}}


class CoverageSummaryTests(unittest.TestCase):
    def test_intake_execution_does_not_claim_review_completion(self):
        coverage = separated_coverage()
        result = execution_outcome(True, coverage=coverage)
        self.assertEqual(result['outcome'], 'completed_intake')
        self.assertTrue(result['intake']['complete'])
        self.assertFalse(result['processing']['complete'])
        self.assertFalse(result['historicalReview']['complete'])
        self.assertEqual(result['coverageMeasure'], MEASURE)
        result['processing']['pendingDocuments'] = 0
        self.assertEqual(coverage['processing']['pendingDocuments'], 2)

    def test_legacy_output_unchanged_and_cancelled_v2_honest(self):
        self.assertEqual(coverage_details({'schemaVersion': 1}), {})
        self.assertEqual(execution_outcome(True), {'executionCompleted': True, 'outcome': 'completed_complete'})
        self.assertEqual(execution_outcome(True, True, separated_coverage())['outcome'], 'cancelled')

    def test_incomplete_intake_is_explicit(self):
        coverage = separated_coverage()
        coverage.update(successfulTasks=0, complete=False, gapTaskIds=['gap'])
        coverage['intake'].update(successfulTasks=0, complete=False, gapTaskIds=['gap'])
        self.assertEqual(execution_outcome(False, coverage=coverage)['outcome'], 'completed_intake_with_gaps')

    def test_bad_alias_partition_or_false_completion_fails_closed(self):
        for modify in (lambda c: c['intake'].update(successfulTasks=0),
                       lambda c: c['processing'].update(complete=True),
                       lambda c: c['historicalReview'].update(reviewedDocuments=3),
                       lambda c: c['intake'].update(evaluated=False),
                       lambda c: c.update(measure='unknown'),
                       lambda c: c.update(schemaVersion=1)):
            coverage = separated_coverage()
            modify(coverage)
            with self.assertRaises(ValueError):
                coverage_details(coverage)

    def test_unknown_schema_and_boolean_top_level_counts_fail_closed(self):
        for update in ({'schemaVersion': 3}, {'schemaVersion': True},
                       {'successfulTasks': True}, {'requiredTasks': True}, {'complete': 1}):
            with self.subTest(update=update), self.assertRaises(ValueError):
                coverage_details({**separated_coverage(), **update})

    def test_collected_review_completion_must_equal_exact_remaining_work(self):
        for name in ('processing', 'historicalReview'):
            coverage = separated_coverage()
            coverage[name].update(inventoryDocuments=1, reviewedDocuments=1, pendingDocuments=0,
                                  heldDocuments=0, complete=False)
            if name == 'processing':
                coverage[name].update(changedDocuments=0, unknownDateDocuments=0)
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'COMPLETION_DIFFERS'):
                coverage_details(coverage)

    def test_explicit_uncollected_zero_review_has_no_completion_credit(self):
        coverage = separated_coverage()
        for name in ('processing', 'historicalReview'):
            summary = coverage[name]
            for key in list(summary):
                summary[key] = False if key == 'complete' else 0
            summary.update(evaluated=False, status='uncollected')
        result = coverage_details(coverage)
        self.assertFalse(result['processing']['complete'])
        self.assertFalse(result['historicalReview']['complete'])
