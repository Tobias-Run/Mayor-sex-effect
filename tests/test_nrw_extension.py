"""Guard buyer scope, source precision and named primary presentation."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from nrw_extended_ted import classify_buyer
from nrw_extension_evidence import hopp_entry, hopp_presentation, reuscher_presentation, unna_presentations
from nrw_municipal_registers import boundary, parse_register


def notice(*names):
    return {"buyer-name": {"deu": list(names)}}


class ExtensionScopeTests(unittest.TestCase):
    def test_county_is_not_the_same_named_municipality(self):
        self.assertEqual(classify_buyer(notice("Kreisstadt Unna")), ("05978036", None))
        self.assertEqual(classify_buyer(notice("Kreis Unna"))[1], "other_organization_outside_direct_municipal_pilot")

    def test_represented_city_and_its_enterprise_remain_pending(self):
        for name in ["Stadt Sendenhorst vertreten durch Kommunal Agentur NRW GmbH",
                     "Kreisstadt Unna (für Stadtbetriebe Unna)", "Gemeinde Weilerswist - Die Bürgermeisterin"]:
            self.assertEqual(classify_buyer(notice(name))[1], "municipal_variant_or_represented_scope_review")

    def test_joint_buyer_is_not_promoted_by_one_city_label(self):
        self.assertEqual(classify_buyer(notice("Stadt Frechen", "Rhein-Erft-Kreis"))[1], "multiple_or_missing_buyer_labels_review")
        self.assertEqual(classify_buyer(notice())[1], "multiple_or_missing_buyer_labels_review")


class RegisterPrecisionTests(unittest.TestCase):
    def test_year_and_blank_end_do_not_become_exact_dates(self):
        self.assertEqual(boundary("2009"), {"source_value": "2009", "precision": "year", "day": None, "year": 2009})
        self.assertIsNone(boundary("")["day"])
        self.assertEqual(boundary("01.11.2020")["day"], "2020-11-01")

    def test_deputy_with_academic_title_has_no_treatment_assignment(self):
        rows = parse_register(b"Titel;Vorname;Name;vom;bis\nDr.;A;Example;05.11.2020;\n", "dusseldorf-deputies-csv")
        self.assertEqual(rows[0]["role_category"], "honorary_deputy_history")
        self.assertTrue(rows[0]["blank_end_is_not_verified_continuity"])
        self.assertEqual(rows[0]["main_treatment_or_responsibility_assignment"], "unverified")

    def test_vacancy_is_not_a_person(self):
        rows = parse_register(b"Jahr von,Jahr bis,Oberb\xc3\xbcrgermeister Name,Partei,Wiki-Link\n1848,1850,(vakant),,\n", "muenster-heads-csv")
        self.assertTrue(rows[0]["vacant_source_row"])
        self.assertIsNone(rows[0]["start"]["day"])

    def test_inverted_days_within_same_year_are_rejected(self):
        with self.assertRaises(ValueError):
            parse_register(b"Titel;Vorname;Name;von;bis\n;A;Example;02.11.2020;01.11.2020\n", "dusseldorf-heads-csv")


class ExtensionEvidenceTests(unittest.TestCase):
    def test_party_presentation_requires_date_and_both_named_candidates(self):
        text = "28. September 2020 Dirk Wigant Die SPD bedankt sich bei ihrer Kandidatin Katja Schuon dem CDU-Mann Wigant mit 221 Stimmen Vorsprung"
        observations = unna_presentations(text)
        self.assertEqual({o["presentation"] for o in observations}, {"female", "male"})
        self.assertTrue(all(o["observation_date"] == "2020-09-28" for o in observations))
        with self.assertRaises(ValueError):
            unna_presentations(text.replace("28. September 2020", "28. September 2025"))

    def test_person_search_requires_single_exact_identity(self):
        payload = {"result_count": 1, "results": [{"Vorname": "Katrin", "Name": "Reuscher", "Anrede": "Frau"}]}
        self.assertIsNone(reuscher_presentation(payload)["observation_date"])
        payload["results"][0]["Name"] = "Example"
        with self.assertRaises(ValueError):
            reuscher_presentation(payload)

    def test_current_successor_title_does_not_create_historical_entry(self):
        self.assertIsNone(hopp_presentation("Anrede: Herr Name: Christoph Hopp")["observation_date"])
        entry = hopp_entry("Seit dem 1. November 2025 ist Christoph Hopp Bürgermeister der Stadt Viersen.")
        self.assertEqual(entry["reported_entry_date"], "2025-11-01")
        self.assertFalse(entry["certifies_previous_winner_continuous_term"])


if __name__ == "__main__":
    unittest.main()
