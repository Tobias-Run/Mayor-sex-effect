"""Protect municipal scope, non-awards and historical person-role boundaries."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from nrw_legacy_ted_awards import result_status
from nrw_official_evidence import member_title, person_head_role, within_role
from nrw_ted_linkage import classify_buyer


class BuyerScopeTests(unittest.TestCase):
    def test_exact_city_department_and_separate_utility_are_distinct(self):
        def classify(names):
            return classify_buyer({"buyer-name": {"deu": names}})
        self.assertEqual(classify(["Stadt Velbert"]), ("05158032", None))
        self.assertEqual(classify(["Stadt Velbert, Fachbereich 5"])[1], "municipal_variant_or_beneficiary_scope_needs_review")
        self.assertEqual(classify(["Stadtwerke Velbert GmbH"])[1], "other_organization_outside_direct_city_pilot")
        self.assertEqual(classify(["Stadt Velbert", "Stadt Iserlohn"])[1], "multiple_or_missing_german_buyer_labels")
        self.assertEqual(classify([])[1], "multiple_or_missing_german_buyer_labels")


class ResultNoticeTests(unittest.TestCase):
    def notice(self, statuses):
        return ("565529-2023 - Ergebnis Abschnitt I: Öffentlicher Auftraggeber "
                "Offizielle Bezeichnung: Stadt Velbert Postanschrift: Example "
                "Abschnitt II: Gegenstand " + " ".join(
                    "Abschnitt V: Auftragsvergabe Ein Auftrag/Los wurde vergeben: " + status for status in statuses))

    def test_cancelled_result_notice_has_no_awarded_status(self):
        self.assertEqual(result_status(self.notice(["nein"]), "565529-2023", "Stadt Velbert"), "not_awarded")
        self.assertEqual(result_status(self.notice(["ja"]), "565529-2023", "Stadt Velbert"), "awarded")

    def test_mixed_results_and_different_authority_need_review(self):
        for text, buyer in [(self.notice(["ja", "nein"]), "Stadt Velbert"),
                            (self.notice(["ja"]), "Stadt Iserlohn"),
                            (self.notice([]), "Stadt Velbert")]:
            with self.subTest(text=text, buyer=buyer), self.assertRaises(ValueError):
                result_status(text, "565529-2023", buyer)


class HistoricalPersonTests(unittest.TestCase):
    def role_html(self, name="Bürgermeisterin Daniela Ritzerfeld", view="Alle Daten"):
        return (f'<title>SessionNet | {name}</title>'
                f'<a aria-label="Zeitraum auswählen">{view}</a>'
                '<tr><td data-label="Gremium">Rat der Stadt Geilenkirchen</td>'
                '<td data-label="Mitarbeit">Vorsitz</td><td data-label="Beginn">01.11.2020</td>'
                '<td data-label="Ende">31.10.2025</td></tr>'
                '<tr><td data-label="Gremium">Wahlausschuss</td>'
                '<td data-label="Mitarbeit">Vorsitz</td><td data-label="Beginn">12.11.2020</td>'
                '<td data-label="Ende">31.10.2025</td></tr>')

    def test_named_person_council_role_does_not_use_committee_begin(self):
        interval = person_head_role(self.role_html(), "Bürgermeisterin Daniela Ritzerfeld")
        self.assertEqual(interval["start_inclusive"], "2020-11-01")
        self.assertFalse(interval["continuous_procurement_authority_verified"])
        self.assertTrue(within_role("2025-10-31", interval))
        self.assertFalse(within_role("2025-11-01", interval))
        self.assertFalse(within_role("2020-09-13", interval))

    def test_successor_identity_and_period_filtered_view_cannot_supply_old_boundaries(self):
        for raw in [self.role_html(name="Bürgermeister Dr. Armin Leon"),
                    self.role_html(view="Wahlperiode 2020-2025"),
                    self.role_html().replace("01.11.2020", "01.11.2026")]:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                person_head_role(raw, "Bürgermeisterin Daniela Ritzerfeld")

    def test_member_title_is_scoped_to_named_row_and_period(self):
        raw = ('<a class="smcfiltermenuselected">Wahlperiode 2020-2025</a>'
               '<tr><td data-label="Name">Bürgermeister Dr. Armin Leon</td></tr>'
               '<tr><td data-label="Name">Bürgermeisterin Daniela Ritzerfeld</td></tr>')
        expected = "Bürgermeisterin Daniela Ritzerfeld"
        self.assertEqual(member_title(raw, "2020-2025", expected), expected)
        for text, period in [(raw, "2014-2020"), (raw.replace(expected, "Daniela Ritzerfeld"), "2020-2025")]:
            with self.subTest(text=text, period=period), self.assertRaises(ValueError):
                member_title(text, period, expected)


if __name__ == "__main__":
    unittest.main()
