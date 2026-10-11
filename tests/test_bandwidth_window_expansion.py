"""Guard acquisition boundaries, unchanged label rules and censoring targets."""
import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'pilot'))
import bandwidth_window_expansion as audit


class BandwidthWindowTests(unittest.TestCase):
    def test_nested_boundary_assignment(self):
        self.assertEqual([audit.band(h) for h in (2, 2.01, 5, 5.01, 10, 10.01)],
                         ['within_2pp', 'over_2_to_5pp', 'over_2_to_5pp',
                          'over_5_to_10pp', 'over_5_to_10pp', 'outside_10pp'])
        with self.assertRaises(ValueError): audit.band(-1)

    def test_calendar_followup_clips_month_end_and_leap_year(self):
        self.assertEqual(audit.followup_end('2025-05-31'), date(2026, 2, 28))
        self.assertEqual(audit.followup_end('2023-05-31'), date(2024, 2, 29))
        self.assertEqual(audit.followup_end('2025-12-31'), audit.SOURCE_CUTOFF)
        self.assertGreater(audit.followup_end('2026-01-01'), audit.SOURCE_CUTOFF)

    def test_older_full_year_and_younger_partial_year_not_pooled(self):
        for cohort in ('Niedersachsen 2021', 'Brandenburg 2024'):
            self.assertEqual(audit.cohort_window(cohort)[:2], ('2025-01-01', '2025-12-31'))
        for cohort in ('NRW 2025', 'Brandenburg 2025'):
            self.assertEqual(audit.cohort_window(cohort)[:2], ('2026-01-01', '2026-03-31'))
        with self.assertRaises(ValueError): audit.cohort_window('Hesse 2021')

    def test_identical_repeated_export_is_not_a_second_notice(self):
        seen = {}; key = ('example', 1)
        row = {'publicationDate': '2025-09-01'}
        buyer = {'organisationName': 'Stadt Example'}
        self.assertTrue(audit.first_metadata_occurrence(seen, key, row, [buyer]))
        self.assertFalse(audit.first_metadata_occurrence(seen, key, dict(row), [dict(buyer)]))
        with self.assertRaisesRegex(ValueError, 'Conflicting duplicate'):
            audit.first_metadata_occurrence(seen, key, {'publicationDate': '2025-10-01'}, [buyer])

    def test_wider_acquisition_retains_missing_names_and_unknown_labels(self):
        def record(ags, state, year, margin):
            return {'ags': ags, 'state': state, 'municipality': 'Example',
                    'decisive_date': year + '-09-26', 'absolute_margin_pp': margin,
                    'both_names_available': False, 'candidates': []}
        records = [record('03111111','03','2021',10),
                   record('03222222','03','2021',10.01),
                   record('03333333','03','2023',4),
                   record('12111111','12','2025',7),
                   record('06111111','06','2021',4)]
        with patch.object(audit, 'official_nrw_frame', return_value=([], [])):
            events, _ = audit.active_frame(records)
        self.assertEqual({e['ags'] for e in events}, {'03111111', '12111111'})
        self.assertTrue(all(not e['both_names_available'] for e in events))


if __name__ == '__main__': unittest.main()
