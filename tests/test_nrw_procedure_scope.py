import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from federal_procurement import NS
from nrw_procedure_scope import legacy_procedure, procedure_fields, term_claims, timing_disposition, title_candidate


def xml_procedure(code, reason=""):
    root = ET.Element("root")
    process = ET.SubElement(root, "{" + NS["cac"] + "}TenderingProcess")
    ET.SubElement(process, "{" + NS["cbc"] + "}ProcedureCode").text = code
    if reason:
        ET.SubElement(process, "{" + NS["cbc"] + "}ProcessReason").text = reason
    return root, process


class ProcedureScopeTests(unittest.TestCase):
    def test_no_call_code_is_separate_from_generic_missing_date(self):
        root, _ = xml_procedure("neg-wo-call")
        row = procedure_fields(root)
        self.assertTrue(row["no_prior_call_procedure"])
        self.assertFalse(row["italian_direct_award_equivalence_verified"])
        self.assertEqual(timing_disposition(row["procedure_code_source"], "competition_missing_or_review_pending"),
                         "no_prior_call_procedure_requires_separate_timing_rule")

    def test_no_call_status_does_not_reuse_an_earlier_linked_competition(self):
        self.assertEqual(timing_disposition("neg-wo-call", "documented_chronology_supported"),
                         "no_prior_call_procedure_requires_separate_timing_rule")

    def test_reason_text_does_not_override_the_typed_procedure(self):
        root, _ = xml_procedure("open", "Vergabe ohne Wettbewerb")
        self.assertFalse(procedure_fields(root)["no_prior_call_procedure"])
        root, _ = xml_procedure("us-free-no-tw")
        self.assertFalse(procedure_fields(root)["no_prior_call_procedure"])

    def test_duplicate_codes_require_review(self):
        root, process = xml_procedure("open")
        ET.SubElement(process, "{" + NS["cbc"] + "}ProcedureCode").text = "neg-wo-call"
        with self.assertRaises(ValueError):
            procedure_fields(root)

    def test_legacy_procedure_comes_only_from_section_iv(self):
        row = legacy_procedure("IV.1.1. Verfahrensart Nichtoffenes Verfahren IV.1.2. Angaben Abschnitt V Offenes Verfahren")
        self.assertEqual(row["procedure_code_source"], "restricted")
        row = legacy_procedure("IV.1.1. Verhandlungsverfahren ohne vorherige Bekanntmachung IV.2. Angaben")
        self.assertEqual(row["procedure_code_source"], "neg-wo-call")
        with self.assertRaises(ValueError):
            legacy_procedure("Abschnitt V Offenes Verfahren")

    def test_title_match_cannot_override_conflicting_guids_or_city(self):
        result = {"ags": "05370012", "title-proc": {"deu": "Exact project"}, "procedure-identifier": "result-guid"}
        candidate = {"buyer-name": {"deu": ["Stadt Geilenkirchen -Die Bürgermeisterin-"]},
                     "title-proc": {"deu": "Exact project"}, "procedure-identifier": "other-guid"}
        self.assertEqual(title_candidate(result, candidate), "same_city_title_but_guid_conflict_review")
        candidate["buyer-name"]["deu"] = ["Kreis Heinsberg"]
        self.assertEqual(title_candidate(result, candidate), "title_or_city_mismatch")

    def term_fixture(self):
        return {
            "viersen-anemueller-farewell": "Ausgabe November 2025 Zwei Amtszeiten lang, von 2015 bis 2025, war Sabine Anemüller Bürgermeisterin der Stadt Viersen und Chefin der Stadtverwaltung.",
            "unna-predecessors": "Werner Kolter (75) war von 2004 bis 2020 Bürgermeister in Unna",
            "unna-oath-2025": "Bürgermeister Dirk Wigant ist nach seiner Wiederwahl im September vereidigte Wigant in der konstituierenden Ratssitzung am Donnerstag, 20. November 2025_11_20_Konstituierung_Rat_BM_Tibbe_Amtskette.jpg"
        }

    def test_year_history_and_oath_do_not_supply_exact_2020_entry(self):
        rows = term_claims(self.term_fixture())
        self.assertEqual(rows[0]["boundary_precision"], "year")
        self.assertEqual(rows[2]["oath_event_date"], "2025-11-20")
        self.assertTrue(all(r["actual_entry_date"] is None and r["actual_2020_renewal_date"] is None for r in rows))

    def test_event_year_basis_must_remain_source_supported(self):
        raw = self.term_fixture()
        raw["unna-oath-2025"] = raw["unna-oath-2025"].replace("2025_11_20", "2024_11_20")
        with self.assertRaises(ValueError):
            term_claims(raw)


if __name__ == "__main__":
    unittest.main()
