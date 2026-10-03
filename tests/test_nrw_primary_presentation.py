"""Protect exact archived identity and the distinct meanings of office-date evidence."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from nrw_primary_presentation_update import (joithe_entry_claim, joithe_official_activity,
                                            kanschat_corroboration, kirchhoff_observation)


class PrimaryPresentationTests(unittest.TestCase):
    def person(self):
        return ("<title>ALLRIS - Recherche Person Eva-Barbara Kirchhoff</title>"
                "Frau Eva-Barbara Kirchhoff Endedatum: 11.11.2025 "
                "Rat der Stadt Iserlohn Erste stv. Bürgermeisterin CDU")

    def test_person_record_end_and_deputy_title_do_not_assign_full_time_mayor_terms(self):
        row = kirchhoff_observation(self.person())
        self.assertTrue(row["person_record_end_is_not_full_time_mayor_term_end"])
        self.assertFalse(row["registry_gender_field"])
        self.assertIsNone(row["observation_date"])
        self.assertEqual(row["main_treatment_assignment"], "unverified")
        current = kanschat_corroboration("2. stellvertretende Bürgermeisterin Dr. Esther Kanschat")
        self.assertFalse(current["historical_2020_observation"])
        self.assertTrue(current["deputy_role_is_not_full_time_mayor_authority"])

    def test_shortened_identity_or_changed_archival_context_requires_review(self):
        for raw in [self.person().replace("Eva-Barbara", "Eva"),
                    self.person().replace("11.11.2025", "01.11.2025"),
                    self.person().replace("Erste stv. Bürgermeisterin", "Bürgermeisterin")]:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                kirchhoff_observation(raw)

    def test_self_authored_entry_and_later_official_activity_do_not_certify_legal_start(self):
        entry = joithe_entry_claim("Name: Michael Joithe Seit meinem Amtsantritt am 02.11.2020")
        activity = joithe_official_activity("Ansprache 9. November 2020 Ansprache von Bürgermeister Michael Joithe zum 9. November")
        self.assertEqual(entry["reported_entry_date"], "2020-11-02")
        self.assertFalse(entry["legal_office_start_verified"])
        self.assertFalse(activity["exact_initial_entry_verified"])
        with self.assertRaises(ValueError):
            joithe_entry_claim("Name: Michael Joithe Seit meinem Amtsantritt am 27.09.2020")


if __name__ == "__main__":
    unittest.main()
