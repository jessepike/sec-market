"""V5 warning provenance; all caller transport and run envelopes are fictional.

The portable fixture repeats the actual suspect card's URL, title and displayed
date inside synthetic pagination. The optional retained-body check reads the
hash-pinned original index bytes without changing their observation time.
"""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'web/scripts/pipeline'), str(ROOT / 'ops/ci')]

from contracts import canonical, digest
from discovery import (SONATYPE_INDEX, SONATYPE_HTML_MODE_V5,
                       SONATYPE_V5_PUBLISHER_LEAD_URL, parse_source_html_index)
from onboarding import (BOUNDED_CANDIDATE_BINDINGS_V5, PersistentProbeBudget,
                        _bounded_candidate_page_snapshot, _candidate_adapter,
                        probe_sources, replay_bounded_candidate_diagnostic)
import test_bounded_candidate_traversal as traversal
from test_html_archive_discovery import source, sonatype_page

TITLE = 'Sonatype Nexus Delivers Advanced Staging; Further Simplifying DevOps-Native Software Development'
WARNING = {'url': SONATYPE_V5_PUBLISHER_LEAD_URL, 'cardTitle': TITLE,
           'indexDate': '2018-07-09', 'reason': 'PUBLISHER_CARD_LINK_REQUIRES_PRIMARY_REVIEW'}
ACTUAL_BODY = Path('/var/tmp/smp-bounded-v4-probe-20261024/target-bundle/sonatype.body')
ACTUAL_SHA = '9b94a74c28bfee4c52761c5730c567e0fd61b64604c6f4df8e8851afb05abf74'


class BoundedV5WarningReplayTests(unittest.TestCase):
    def setUp(self):
        self.fixture = traversal.BoundedCandidateTraversalTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def report(self):
        fixture = self.fixture
        plan = fixture.plan()
        plan['parserRevision'] = 5
        sources = {row['id']: row for row in fixture.policy['sources']}
        for row, (sid, url, mode) in zip(plan['sources'], BOUNDED_CANDIDATE_BINDINGS_V5):
            row['proposedAdapterSha256'] = digest(_candidate_adapter(sources[sid], url, mode))
        fixture.path.write_bytes(canonical(plan))
        body = sonatype_page(1, last=1)
        # Equal displayed dates keep this synthetic page ordered. They make no
        # claim about the other fictional cards' real publication dates.
        import re
        body = re.sub(rb'<p>October [0-9]+, 2026</p>', b'<p>July 9, 2018</p>', body)
        body = body.replace((SONATYPE_INDEX + '/fixture-1-0').encode(),
                            SONATYPE_V5_PUBLISHER_LEAD_URL.encode())
        body = body.replace(b'<h3>Fixture title</h3>', ('<h3>' + TITLE + '</h3>').encode(), 1)

        class Fetcher(traversal.CandidateFetcher):
            def fetch(self, source_row, url):
                if source_row['id'] == 'sonatype:official:1' and url == SONATYPE_INDEX:
                    self.calls.append((source_row['id'], url))
                    return {'status': 'fetched', 'httpStatus': 200, 'requestedUrl': url,
                            'finalUrl': url, 'fetchedAt': self.clock.now(),
                            'contentType': 'text/html', 'body': self.store.put(body)}
                return super().fetch(source_row, url)

        fetcher = Fetcher(fixture.store, clock=fixture.clock)
        budget = PersistentProbeBudget(fixture.store, fixture.policy,
                                       clock=fixture.clock.now, monotonic=fixture.clock.monotonic)
        auth, observation = fixture._authenticated_test_authority()
        with auth, observation:
            return probe_sources(fixture.policy, fixture.store, fetcher,
                                 reservation_context=budget, qualification_plan_path=fixture.path)

    def archive(self, report, run=99550):
        record = {'schemaVersion': 1, 'checkpointProfile': 'source_probe',
                  'githubRunId': str(run), 'githubRunAttempt': 1,
                  'githubEventName': 'workflow_dispatch', 'githubRef': 'refs/heads/main',
                  'appRevision': 'a' * 40, 'contractSha256': digest(self.fixture.policy),
                  'diagnostic': report, 'executionCompleted': report['executionCompleted'],
                  'outcome': 'completed_diagnostic' if report['executionCompleted'] else 'budget_denied',
                  'modelCalls': 0, 'apiFallback': False, 'semanticAdmission': False,
                  'coverageCredit': False, 'sourceChecksCredited': 0, 'qualifiedSources': 0,
                  'publication': {'published': False, 'reason': 'SOURCE_PROBE_DIAGNOSTIC_ONLY'}}
        raw = canonical(record)
        key = f'ci/source-probe-runs/{run}-1.json'
        self.fixture.store.write_once(key, raw)
        return {'key': key, 'sha256': digest(raw), 'bytes': len(raw)}

    @staticmethod
    def page(report):
        row = next(s for s in report['sources'] if s['sourceId'] == 'sonatype:official:1')
        return row['observations'][0]

    def test_caller_records_body_derived_warning_and_historical_replay_keeps_it(self):
        report = self.report()
        page = self.page(report)
        self.assertEqual(page['parser']['publisherLeadWarnings'], [WARNING])
        self.assertEqual(page['parser']['dates'][SONATYPE_V5_PUBLISHER_LEAD_URL], '2018-07-09')
        replay = replay_bounded_candidate_diagnostic(self.fixture.policy, self.fixture.store,
                                                    self.archive(report), report['planReference'])
        self.assertEqual(replay['report'], report)
        self.assertEqual(replay['plan']['parserRevision'], 5)
        self.assertEqual(report['modelCalls'], 0)
        self.assertEqual(report['facts'], [])
        self.assertEqual(report['sourceChecksCredited'], 0)
        self.assertFalse(report['semanticAdmission'])
        self.assertFalse(report['coverageCredit'])

    def test_rehashed_self_reported_warning_changes_cannot_replace_body_replay(self):
        original = self.report()
        mutations = [('omitted', lambda p: p.pop('publisherLeadWarnings')),
                     ('empty', lambda p: p.update(publisherLeadWarnings=[])),
                     ('null', lambda p: p.update(publisherLeadWarnings=None)),
                     ('duplicate', lambda p: p['publisherLeadWarnings'].append(copy.deepcopy(WARNING)))]
        for field, value in [('url', SONATYPE_INDEX + '/different'), ('cardTitle', 'Unrelated'),
                             ('indexDate', '2022-01-01'), ('reason', 'PRIMARY_ALREADY_VALIDATED')]:
            mutations.append((field, lambda p, f=field, v=value: p['publisherLeadWarnings'][0].update({f: v})))
        for index, (name, mutate) in enumerate(mutations):
            altered = copy.deepcopy(original)
            mutate(self.page(altered)['parser'])
            # Rehash a valid immutable report/envelope, keeping the original
            # body, source/adapter wrapper and charged request unchanged.
            with self.subTest(mutation=name), self.assertRaisesRegex(
                    ValueError, 'BOUNDED_CANDIDATE_PAGE_PARSER_REPLAY_DIFFERS'):
                replay_bounded_candidate_diagnostic(self.fixture.policy, self.fixture.store,
                    self.archive(altered, run=99560 + index), original['planReference'])

    def test_old_revisions_keep_exact_snapshot_fields_and_v5_copies_warnings(self):
        parsed = {'currentPage': 1, 'highestPage': 1, 'items': {'b', 'a'},
                  'dates': {}, 'next': None, 'terminalProved': True,
                  'publisherLeadWarnings': [copy.deepcopy(WARNING)]}
        expected = {'currentPage': 1, 'highestPage': 1, 'items': ['a', 'b'],
                    'dates': {}, 'next': None, 'terminalProved': True}
        for revision in (1, 2, 3, 4):
            with self.subTest(revision=revision):
                self.assertEqual(_bounded_candidate_page_snapshot(parsed, revision), expected)
        new = _bounded_candidate_page_snapshot(parsed, 5)
        self.assertEqual(new, dict(expected, publisherLeadWarnings=[WARNING]))
        parsed['publisherLeadWarnings'][0]['cardTitle'] = 'Mutated after snapshot'
        self.assertEqual(new['publisherLeadWarnings'], [WARNING])

    @unittest.skipUnless(ACTUAL_BODY.exists(), 'authenticated actual V4 body is VM-local')
    def test_original_retained_card_reconstructs_exact_warning_without_new_date(self):
        body = ACTUAL_BODY.read_bytes()
        self.assertEqual(digest(body), ACTUAL_SHA)
        parsed = parse_source_html_index(source('sonatype') | {'htmlCompleteness': SONATYPE_HTML_MODE_V5},
            SONATYPE_INDEX + '?page=10', body, 13, '2026-10-24T08:45:25.132878Z')
        self.assertEqual(parsed['publisherLeadWarnings'], [WARNING])
        self.assertEqual(parsed['dates'][SONATYPE_V5_PUBLISHER_LEAD_URL], '2018-07-09')
        self.assertFalse(parsed['terminalProved'])
        self.assertEqual(parsed['next'], SONATYPE_INDEX + '?page=11')


if __name__ == '__main__':
    unittest.main()
