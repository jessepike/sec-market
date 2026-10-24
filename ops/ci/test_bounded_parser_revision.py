"""Versioned parsing must retain old failures while accepting demonstrated layouts."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
sys.path.insert(0, str(ROOT / 'ops/ci'))
from contracts import canonical, digest
from onboarding import (_candidate_primary_shape, _candidate_adapter,
                        _validate_bounded_candidate_plan, BOUNDED_CANDIDATE_BINDINGS_V2,
                        BOUNDED_CANDIDATE_BINDINGS_V3)
import test_bounded_candidate_traversal as fixtures

URL = 'https://press.pingidentity.com/2019-08-23-Ping-Identity-Files-Registration-Statement-for-Proposed-IPO'
TITLE = 'Ping Identity Files Registration Statement for Proposed IPO'


def article():
    return (f'<html><head><title>{TITLE}</title><link rel="canonical" href="{URL}">'
            f'<meta property="og:title" content="{TITLE}"><meta property="og:url" content="{URL}">'
            '</head><body><main><div class="wd_newsfeed_releases-detail">'
            f'<div class="wd_title wd_language_left">{TITLE}</div>'
            '<div class="wd_body wd_news_body fr-view"><p>'
            + 'Original primary article text. ' * 5 + '</p></div>'
            '</div></main></body></html>').encode()


class PrimaryShapeRevisionTests(unittest.TestCase):
    def test_original_revision_keeps_the_actual_missing_h1_failure(self):
        with self.assertRaisesRegex(ValueError, 'PRIMARY_HEADING_AMBIGUOUS'):
            _candidate_primary_shape(article(), URL)
        result = _candidate_primary_shape(article(), URL, 2)
        self.assertEqual(result['heading'], TITLE)
        self.assertEqual(result['dateMetadataState'], 'unknown')

    def test_rejects_competing_regions_titles_and_h1(self):
        for extra in ('<div class="wd_newsfeed_releases-detail"></div>',
                      '<div class="wd_title">Other</div>', '<h1>Other</h1>', '<h1>Other</h1><h1>More</h1>'):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                _candidate_primary_shape(article().replace(b'</main>', extra.encode()+b'</main>'), URL, 2)

    def test_rejects_metadata_mismatch_missing_body_and_nested_title(self):
        for old, new in ((f'content="{TITLE}"', 'content="Unrelated"'),
                         ('wd_body wd_news_body', 'unrelated'),
                         (f'<div class="wd_title wd_language_left">{TITLE}</div>',
                          f'<section><div class="wd_title wd_language_left">{TITLE}</div></section>')):
            with self.subTest(new=new), self.assertRaises(ValueError):
                _candidate_primary_shape(article().replace(old.encode(), new.encode()), URL, 2)

    def test_alternate_layout_cannot_apply_to_another_host(self):
        other = URL.replace('press.pingidentity.com', 'delinea.com')
        with self.assertRaisesRegex(ValueError, 'PRIMARY_HEADING_AMBIGUOUS'):
            _candidate_primary_shape(article().replace(URL.encode(), other.encode()), other, 2)

    def test_readable_navigation_cannot_replace_a_truncated_primary_body(self):
        short = article().replace(('Original primary article text. ' * 5).encode(), b'x')
        with self.assertRaisesRegex(ValueError, 'PRIMARY_PING_DETAIL_AMBIGUOUS'):
            _candidate_primary_shape(short, URL, 2)

    def test_navigation_cannot_mask_a_blocked_primary_body(self):
        blocked = article().replace(('Original primary article text. ' * 5).encode(),
                                    ('access denied ' + 'blocked ' * 30).encode())
        blocked = blocked.replace(b'<main>', b'<main>' + b'Navigation text. ' * 200)
        with self.assertRaisesRegex(ValueError, 'SOURCE_BLOCK_PAGE'):
            _candidate_primary_shape(blocked, URL, 2)

    def test_revision_three_primary_uses_the_matching_valid_date_route_only(self):
        for date_path in ('2019-8-23', '201908-23'):
            url = URL.replace('2019-08-23', date_path)
            body = article().replace(URL.encode(), url.encode())
            with self.subTest(date_path=date_path):
                with self.assertRaisesRegex(ValueError, 'PRIMARY_HEADING_AMBIGUOUS'):
                    _candidate_primary_shape(body, url, 2)
                result = _candidate_primary_shape(body, url, 3)
                self.assertEqual(result['canonical'], url)
                self.assertEqual(result['dateMetadataState'], 'unknown')
        for invalid in ('2019-2-29', '2019-13-1'):
            url = URL.replace('2019-08-23', invalid)
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, 'PRIMARY_HEADING_AMBIGUOUS'):
                _candidate_primary_shape(article().replace(URL.encode(), url.encode()), url, 3)

    def test_revision_three_primary_rejects_raw_url_whitespace_before_parsing(self):
        for url in (' ' + URL, URL.replace('2019-08-23', '2019-\t8-23')):
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, 'Unsafe V3 literal article URL'):
                _candidate_primary_shape(article().replace(URL.encode(), url.encode()), url, 3)


class PlanRevisionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.BoundedCandidateTraversalTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def validate(self, plan):
        raw = canonical(plan)
        auth, observation = self.fixture._authenticated_test_authority()
        with auth, observation:
            return _validate_bounded_candidate_plan(self.fixture.policy, self.fixture.store,
                                                   self.fixture.path, raw, plan)

    def test_revision_is_explicit_and_rejects_unknown_or_boolean_values(self):
        plan = self.fixture.plan()
        self.assertEqual(self.validate(plan)['parserRevision'], 1)
        for revision in (True, False, 0, 1, 4, '2'):
            altered = dict(plan, parserRevision=revision)
            with self.subTest(revision=revision), self.assertRaisesRegex(ValueError, 'PARSER_REVISION_INVALID'):
                self.validate(altered)

    def test_revision_two_requires_new_exact_adapter_hashes(self):
        plan = dict(self.fixture.plan(), parserRevision=2)
        with self.assertRaisesRegex(ValueError, 'PROPOSED_ADAPTER_BINDING_INVALID'):
            self.validate(plan)
        source_map = {row['id']: row for row in self.fixture.policy['sources']}
        for row, (source_id, index, mode) in zip(plan['sources'], BOUNDED_CANDIDATE_BINDINGS_V2):
            row['proposedAdapterSha256'] = digest(_candidate_adapter(source_map[source_id], index, mode))
        validated = self.validate(plan)
        self.assertEqual(validated['parserRevision'], 2)
        self.assertTrue(all(row['mode'].endswith('-v2') for row in validated['sources']))
        wrong = copy.deepcopy(plan)
        wrong['unreviewed'] = True
        with self.assertRaisesRegex(ValueError, 'PLAN_SHAPE_OR_POLICY_INVALID'):
            self.validate(wrong)

    def test_revision_three_requires_its_own_exact_adapter_hashes(self):
        plan = dict(self.fixture.plan(), parserRevision=3)
        with self.assertRaisesRegex(ValueError, 'PROPOSED_ADAPTER_BINDING_INVALID'):
            self.validate(plan)
        source_map = {row['id']: row for row in self.fixture.policy['sources']}
        for row, (source_id, index, mode) in zip(plan['sources'], BOUNDED_CANDIDATE_BINDINGS_V3):
            row['proposedAdapterSha256'] = digest(_candidate_adapter(source_map[source_id], index, mode))
        self.assertEqual(self.validate(plan)['parserRevision'], 3)
        downgraded = dict(plan, parserRevision=2)
        with self.assertRaisesRegex(ValueError, 'PROPOSED_ADAPTER_BINDING_INVALID'):
            self.validate(downgraded)


if __name__ == '__main__':
    unittest.main()
