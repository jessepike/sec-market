"""Validated receipt projection; intake completion never implies review completion."""
from copy import deepcopy
from contracts import require

MEASURE = 'daily_source_intake_v2'


def coverage_details(coverage):
    require(coverage.get('schemaVersion') is None or
            (type(coverage.get('schemaVersion')) is int and coverage['schemaVersion'] in (1, 2)),
            'COVERAGE_SCHEMA_UNSUPPORTED')
    if coverage.get('schemaVersion') != 2:
        require(coverage.get('measure') != MEASURE and not any(k in coverage for k in ('intake', 'processing', 'historicalReview')),
                'COVERAGE_MEASURE_SCHEMA_DIFFERS')
        return {}
    require(coverage.get('measure') == MEASURE, 'COVERAGE_MEASURE_REQUIRED')
    require(type(coverage.get('successfulTasks')) is int and type(coverage.get('requiredTasks')) is int
            and type(coverage.get('complete')) is bool, 'COVERAGE_INTAKE_ALIAS_DIFFERS')
    intake = coverage.get('intake', {})
    require(intake.get('measure') == MEASURE and type(intake.get('complete')) is bool
            and type(intake.get('evaluated')) is bool
            and intake.get('status') == ('collected' if intake['evaluated'] else 'uncollected'), 'COVERAGE_INTAKE_INVALID')
    for key in ('successfulTasks', 'requiredTasks'):
        require(type(intake.get(key)) is int and intake[key] >= 0 and intake[key] == coverage.get(key), 'COVERAGE_INTAKE_ALIAS_DIFFERS')
    require(intake['requiredTasks'] > 0 and intake['successfulTasks'] <= intake['requiredTasks']
            and intake['complete'] == coverage.get('complete')
            and intake['complete'] == (intake['successfulTasks'] == intake['requiredTasks']), 'COVERAGE_INTAKE_ALIAS_DIFFERS')
    gaps = intake.get('gapTaskIds')
    require(isinstance(gaps, list) and all(isinstance(v, str) for v in gaps) and len(set(gaps)) == len(gaps)
            and set(gaps) == set(coverage.get('gapTaskIds', []))
            and len(gaps) == intake['requiredTasks'] - intake['successfulTasks'], 'COVERAGE_INTAKE_GAPS_DIFFER')
    require(intake['evaluated'] or (intake['successfulTasks'] == 0 and not intake['complete']), 'COVERAGE_UNCOLLECTED_CREDIT')
    for name in ('processing', 'historicalReview'):
        summary = coverage.get(name, {})
        fields = ['inventoryDocuments', 'reviewedDocuments', 'pendingDocuments', 'heldDocuments']
        if name == 'processing':
            fields += ['changedDocuments', 'unknownDateDocuments']
        require(type(summary.get('complete')) is bool and all(type(summary.get(k)) is int and summary[k] >= 0 for k in fields), 'COVERAGE_REVIEW_SUMMARY_INVALID')
        require(summary['reviewedDocuments'] + summary['pendingDocuments'] == summary['inventoryDocuments']
                and summary['heldDocuments'] <= summary['reviewedDocuments']
                and (not summary['complete'] or (summary['pendingDocuments'] == 0 and (name != 'processing' or summary['heldDocuments'] == 0))), 'COVERAGE_REVIEW_PARTITION_DIFFERS')
        if name == 'processing':
            require(summary['changedDocuments'] + summary['unknownDateDocuments'] <= summary['inventoryDocuments'], 'COVERAGE_REVIEW_PARTITION_DIFFERS')
        if summary.get('evaluated') is False:
            require(summary.get('status') == 'uncollected' and not summary['complete'] and all(summary[k] == 0 for k in fields), 'COVERAGE_UNCOLLECTED_CREDIT')
        else:
            require(summary['complete'] == (summary['pendingDocuments'] == 0 and
                    (name != 'processing' or summary['heldDocuments'] == 0)), 'COVERAGE_REVIEW_COMPLETION_DIFFERS')
    return deepcopy({'coverageMeasure': MEASURE, 'intake': intake, 'processing': coverage['processing'],
                     'historicalReview': coverage['historicalReview']})
