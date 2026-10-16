import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('selection_audit', ROOT / 'src/report/audit_feasibility_selection.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def event(ags='00000001', cohort='Example 2020', pair='unresolved', winner='pass', loser='unresolved', calls='0', statistics='0', linked='False'):
    return dict(ags=ags, cohort=cohort, decisive_date='2020-09-01', absolute_margin_pp='1',
                winner_presentation_gate=winner, loser_presentation_gate=loser, pair_status=pair,
                original_supported_procedures=calls, original_supported_tender_statistics=statistics,
                provisional_mixed_count_link=linked, metadata_call_notice_versions='0', main_study_eligibility_certified='False')


class SelectionAuditTests(unittest.TestCase):
    def test_unresolved_opponent_is_not_mixed_or_same(self):
        r = event()
        self.assertEqual(audit.stages(r, {}), [True, False, False, False, False, False, False])
        for label in ['mixed_public_presentation', 'same_public_presentation']:
            with self.assertRaisesRegex(ValueError, 'Pair status'):
                audit.validate([dict(r, pair_status=label)])

    def test_more_lot_statistics_do_not_create_elections(self):
        r = event(pair='mixed_public_presentation', loser='pass', calls='1', statistics='7', linked='True')
        exposure = [{'cohort': r['cohort'], 'ags': r['ags'], 'decisive_date': r['decisive_date'], 'existing_window_matches_reference': 'True'}]
        flow, roles, _ = audit.selection_tables([r], exposure)
        counts = [x['events_retained'] for x in flow if x['cohort'].startswith('ALL_') and x['nested_abs_gap_pp'] == 10]
        self.assertEqual(counts, [1, 1, 1, 1, 1, 1, 0])
        self.assertEqual(roles[0]['events'], 1)

    def test_repeated_municipality_across_cohorts_remains_distinct(self):
        r = event()
        audit.validate([r, dict(r, cohort='Example 2025', decisive_date='2025-09-01')])
        with self.assertRaisesRegex(ValueError, 'Duplicate election'):
            audit.validate([r, copy.deepcopy(r)])

    def test_missing_source_stratum_has_na_fraction_not_zero(self):
        _, _, available = audit.selection_tables([event()], [])
        empty = next(r for r in available if r['has_source_evidence'])
        self.assertEqual(empty['events'], 0)
        self.assertIsNone(empty['both_support_fraction'])

    def test_link_requires_count_and_mixed_presentation(self):
        for r in [event(linked='True'), event(pair='same_public_presentation', loser='pass', calls='1', statistics='1', linked='True')]:
            with self.assertRaisesRegex(ValueError, 'Link must require'):
                audit.validate([r])

    def test_public_ledgers_reconcile_and_flow_is_nested(self):
        events = audit.rows(ROOT / 'docs/feasibility/eligibility-scoreboard-events.csv')
        exposure = audit.rows(ROOT / 'docs/feasibility/readiness-exposure-audit.csv')
        flow, roles, _ = audit.selection_tables(events, exposure)
        for r in flow:
            self.assertGreaterEqual(r['events_not_progressing'], 0)
        r = next(x for x in roles if x['cohort'].startswith('ALL_') and x['nested_abs_gap_pp'] == 10)
        self.assertEqual(r['winner_only'] + r['loser_only'] + r['both_supported'] + r['neither_supported'], len(events))
