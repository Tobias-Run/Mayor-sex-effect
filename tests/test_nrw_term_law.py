"""Protect acceptance/predecessor timing and half-open statutory calendar checks."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from nrw_term_law import council_period_location, legal_entry_from_verified_components


class TermLawTests(unittest.TestCase):
    def test_early_acceptance_waits_for_predecessors_first_day_out_of_office(self):
        self.assertEqual(legal_entry_from_verified_components("2020-09-28", "2020-11-01"), "2020-11-01")

    def test_late_acceptance_can_move_entry_after_the_scheduled_period_start(self):
        self.assertEqual(legal_entry_from_verified_components("2020-11-02", "2020-11-01"), "2020-11-02")

    def test_calendar_election_or_oath_does_not_fill_missing_individual_components(self):
        self.assertIsNone(legal_entry_from_verified_components(None, "2020-11-01"))
        self.assertIsNone(legal_entry_from_verified_components("2020-09-28", None))

    def test_period_checks_include_start_exclude_end_and_preserve_missing_dates(self):
        self.assertEqual(council_period_location("2020-10-31"), "before_scheduled_council_period")
        self.assertEqual(council_period_location("2020-11-01"), "within_scheduled_council_period")
        self.assertEqual(council_period_location("2025-10-31"), "within_scheduled_council_period")
        self.assertEqual(council_period_location("2025-11-01"), "after_scheduled_council_period")
        self.assertEqual(council_period_location(None), "contract_date_missing")


if __name__ == "__main__":
    unittest.main()
