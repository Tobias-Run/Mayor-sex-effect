import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from federal_procurement import NS
from nrw_buyer_followup import apply_scope
from nrw_phase_linkage import competition_graph, phase_observation, previous_competition, same_city_buyers

N1 = "11111111-1111-1111-1111-111111111111"
N2 = "22222222-2222-2222-2222-222222222222"


def node(number="A", identifier=N1, day="2024-01-01", parent=""):
    return {"ags": "05978036", "procedure_identifier": "same-guid", "publication_number": number,
            "notice_identifier": identifier, "notice_version": 1, "competition_publication_date": day,
            "changed_notice_reference": parent}


class CompetitionGraphTests(unittest.TestCase):
    def test_root_is_supported_only_with_exact_parent_version(self):
        rows = [node(), node("B", N2, "2024-01-02", N1 + "-01")]
        self.assertEqual(competition_graph(rows)["candidate_competition_date"], "2024-01-01")
        rows[1]["changed_notice_reference"] = N1 + "-02"
        result = competition_graph(rows)
        self.assertIsNone(result["candidate_competition_date"])
        self.assertIn("missing_parent_version", result["graph_flags"])

    def test_unlinked_competitions_do_not_select_the_earliest_date(self):
        result = competition_graph([node(), node("B", N2, "2024-01-02")])
        self.assertIsNone(result["candidate_competition_date"])
        self.assertIn("multiple_or_missing_roots", result["graph_flags"])

    def test_cycles_and_reverse_parent_chronology_are_flagged(self):
        rows = [node(parent=N2 + "-01"), node("B", N2, "2024-01-02", N1 + "-01")]
        result = competition_graph(rows)
        self.assertIsNone(result["candidate_competition_date"])
        self.assertIn("parent_cycle", result["graph_flags"])
        self.assertIn("parent_published_after_child", result["graph_flags"])

    def test_city_and_guid_scope_cannot_be_crossed(self):
        for field in ["ags", "procedure_identifier"]:
            other = node("B", N2, "2024-01-02")
            other[field] = "other"
            with self.assertRaises(ValueError):
                competition_graph([node(), other])

    def test_candidate_root_does_not_certify_earliest_ever_publication(self):
        result = competition_graph([node()])
        self.assertEqual(result["graph_status"], "documented_root_supported")
        self.assertFalse(result["earliest_ever_publication_verified"])


class LegacyPhaseTests(unittest.TestCase):
    def test_reference_is_read_only_in_section_iv_and_keeps_literal_zeros(self):
        text = ("IV.2.1. Frühere Bekanntmachung Bekanntmachungsnummer im ABl.: 2020/S 200-000481715 "
                "IV.2.2. Verfahren Abschnitt V Bekanntmachungsnummer im ABl.: 2021/S 001-999999")
        result = previous_competition(text)
        self.assertEqual(result["previous_publication_number"], "481715-2020")
        self.assertIn("000481715", result["previous_reference_source"])
        with self.assertRaises(ValueError):
            previous_competition("Abschnitt V Bekanntmachungsnummer im ABl.: 2020/S 200-481715")

    def test_duplicate_previous_references_require_review(self):
        text = "IV.2.1. Bekanntmachungsnummer im ABl.: 2020/S 200-481715 " * 2 + "Abschnitt V"
        with self.assertRaises(ValueError):
            previous_competition(text)

    def test_missing_competition_does_not_use_contract_or_result_date(self):
        unit = {"observation_key": "one", "ags": "05962024", "publication_number": "result",
                "contract_conclusion_date": "2021-01-01", "received_tenders": 2}
        result = phase_observation(unit, {}, "2020-09-27")
        self.assertIsNone(result["candidate_competition_date"])
        self.assertIsNone(result["competition_before_council_boundary"])
        self.assertEqual(result["main_treatment_assignment"], "unverified")

    def test_before_boundary_call_is_separate_from_after_boundary_contract(self):
        unit = {"observation_key": "one", "ags": "05962024", "publication_number": "result",
                "contract_conclusion_date": "2021-01-01", "received_tenders": 2}
        result = phase_observation(unit, {"candidate_competition_date": "2020-10-30"}, "2020-09-27")
        self.assertTrue(result["competition_before_council_boundary"])
        self.assertFalse(result["competition_before_decisive_election"])
        self.assertFalse(result["contract_before_council_boundary"])
        result = phase_observation(unit, {"candidate_competition_date": "2021-01-02"}, "2020-09-27")
        self.assertEqual(result["timing_status"], "contract_before_documented_competition_review")


class BuyerScopeTests(unittest.TestCase):
    def fixture(self, names=None, decision="city_department", ags="05978036"):
        names = names or ["Kreisstadt Unna - Zentrale Vergabestelle"]
        xml = ET.Element("root")
        document = {"buyers": [{"name": n} for n in names]}
        row = {"buyer_names_json": json.dumps(names), "decision": decision, "ags": ags,
               "scope_quote": names[0], "scope_quote_path": "contracting_party_name",
               "beneficiary_quote": "", "beneficiary_quote_path": ""}
        return document, row, xml

    def test_city_and_county_names_do_not_match_by_substring(self):
        self.assertTrue(same_city_buyers(["Kreisstadt Unna - Zentrale Vergabestelle"], "05978036"))
        self.assertFalse(same_city_buyers(["Kreis Unna - Der Landrat"], "05978036"))
        self.assertFalse(same_city_buyers(["Stadt Werdohler Straße"], "05962060"))
        self.assertFalse(same_city_buyers(["Kreisstadt Unna", "Kreis Unna"], "05978036"))

    def test_sole_city_buyer_does_not_require_personal_mayoral_signature(self):
        document, row, xml = self.fixture()
        self.assertEqual(apply_scope(document, row, xml), ("05978036", "city_department"))

    def test_operating_unit_performance_address_keeps_beneficiary_pending(self):
        document, row, xml = self.fixture()
        current = xml
        for tag in ["RealizedLocation", "Address"]:
            current = ET.SubElement(current, "{" + NS["cac"] + "}" + tag)
        ET.SubElement(current, "{" + NS["cbc"] + "}StreetName").text = "Stadtbetriebe Unna"
        with self.assertRaises(ValueError):
            apply_scope(document, row, xml)

    def test_joint_buyer_cannot_enter_accepted_city_subset(self):
        document, row, xml = self.fixture(["Kreisstadt Unna", "Kreis Unna"])
        with self.assertRaises(ValueError):
            apply_scope(document, row, xml)

    def test_represented_city_needs_quote_at_project_description_path(self):
        document, row, xml = self.fixture(["Stadt Werdohl, vertreten durch KUBUS Kommunalberatung und Service GmbH"],
                                          "represented_city", "05962060")
        project = ET.SubElement(xml, "{" + NS["cac"] + "}ProcurementProject")
        ET.SubElement(project, "{" + NS["cbc"] + "}Description").text = "Gaslieferung für die Stadt Werdohl"
        row["beneficiary_quote"] = "Gaslieferung für die Stadt Werdohl"
        row["beneficiary_quote_path"] = "cac:ProcurementProject/cbc:Description"
        self.assertEqual(apply_scope(document, row, xml)[0], "05962060")
        bad = deepcopy(row)
        bad["beneficiary_quote_path"] = ".//cac:RealizedLocation/cac:Address/cbc:StreetName"
        with self.assertRaises(ValueError):
            apply_scope(document, bad, xml)


if __name__ == "__main__":
    unittest.main()
