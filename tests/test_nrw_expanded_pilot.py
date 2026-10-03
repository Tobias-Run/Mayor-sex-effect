"""Protect reviewed authority scope and separately typed full-notice outcomes."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from nrw_buyer_scope import apply_decision, fulltext_buyers
from nrw_candidate_followup import party_observation
from nrw_full_ted_awards import monetary_status, parse_eform_results


class ReviewedScopeTests(unittest.TestCase):
    def test_joint_and_external_regional_labels_cannot_be_promoted(self):
        for names in [["Stadt Velbert / Stadtwerke Velbert GmbH"],
                      ["Stadt Iserlohn für die LEADER-Region HIM - das sind wir!"],
                      ["Stadt Velbert", "Technische Betriebe Velbert AöR"]]:
            with self.subTest(names=names), self.assertRaises(ValueError):
                apply_decision({"buyer-name": {"deu": names}},
                    {"buyer_names_json": json.dumps(names), "decision": "city_department", "ags": "05158032"})

    def test_only_scoped_buyers_are_read_not_suppliers_or_appeal_bodies(self):
        text = ("1-2024 - Ergebnis 1. Beschaffer 1.1. Beschaffer Offizielle Bezeichnung: Stadt Velbert "
                "Rechtsform des Erwerbers: Lokale Gebietskörperschaft 2. Verfahren "
                "Offizielle Bezeichnung: Supplier 8. Organisationen Offizielle Bezeichnung: Appeal body")
        self.assertEqual(fulltext_buyers(text, "1-2024"), ["Stadt Velbert"])
        with self.assertRaises(ValueError):
            fulltext_buyers(text, "2-2024")


class EFormResultTests(unittest.TestCase):
    def notice(self, result, definition=""):
        return ("1-2024 - Ergebnis 1. Beschaffer 1.1. Beschaffer Offizielle Bezeichnung: Stadt Velbert "
                "Rechtsform des Erwerbers: Lokale Gebietskörperschaft 2. Verfahren "
                "5.1. Los: LOT-0001 " + definition +
                " 6. Ergebnisse 6.1. Ergebnis, Los-– Kennung: LOT-0001 " + result + " 8. Organisationen")

    def awarded(self, details):
        return ("Status der Preisträgerauswahl: Es wurde mindestens ein Gewinner ermittelt. "
                "6.1.2. Informationen über die Gewinner Informationen zum Auftrag: " + details +
                " 6.1.4. Statistische Informationen")

    def test_selection_date_and_electronic_subset_do_not_fill_contract_or_total_count(self):
        text = self.notice(self.awarded("Datum der Auswahl des Gewinners: 14/02/2024 "
            "Art der eingegangenen Einreichungen: Angebote auf elektronischem Wege eingereicht "
            "Anzahl der eingegangenen Angebote oder Teilnahmeanträge: 5"))
        rows, _ = parse_eform_results(text, "1-2024", ["Stadt Velbert"])
        self.assertIsNone(rows[0]["contract_conclusion_date"])
        self.assertIsNone(rows[0]["received_tenders"])
        self.assertEqual(rows[0]["winner_selection_date_source"], "14/02/2024")

    def test_typed_total_and_contract_date_are_separate_from_strategic_goal(self):
        details = ("Datum des Vertragsabschlusses: 02/02/2024 "
                   "Art der eingegangenen Einreichungen: Angebote von kleinen Unternehmen "
                   "Anzahl der eingegangenen Angebote oder Teilnahmeanträge: 2 "
                   "Art der eingegangenen Einreichungen: Angebote "
                   "Anzahl der eingegangenen Angebote oder Teilnahmeanträge: 3")
        definition = ("Beschreibung: Lieferung erneuerbarer Energie "
                      "5.1.7. Strategische Auftragsvergabe Ziel der strategischen Auftragsvergabe: Keine strategische Beschaffung "
                      "5.1.10. Zuschlagskriterien Kriterium: Art: Preis 5.1.15. Techniken")
        rows, _ = parse_eform_results(self.notice(self.awarded(details), definition), "1-2024", ["Stadt Velbert"])
        self.assertEqual(rows[0]["received_tenders"], 3)
        self.assertEqual(rows[0]["contract_conclusion_date"], "2024-02-02")
        self.assertEqual(rows[0]["strategic_goal_source"], "Keine strategische Beschaffung")
        self.assertEqual(rows[0]["award_criteria_source"], "Kriterium: Art: Preis")

    def test_closed_non_award_is_not_a_zero_tender_award(self):
        result = ("Status der Preisträgerauswahl: Es wurde kein Wettbewerbsgewinner ermittelt, "
                  "und der Wettbewerb ist abgeschlossen. Grund, warum kein Gewinner ausgewählt wurde: Sonstiges "
                  "6.1.4. Statistische Informationen")
        rows, audit = parse_eform_results(self.notice(result), "1-2024", ["Stadt Velbert"])
        self.assertEqual(rows, [])
        self.assertEqual(audit[0]["status"], "not_awarded")

    def test_multiple_lots_keep_their_own_typed_counts_and_dates(self):
        first = self.awarded("Datum des Vertragsabschlusses: 02/02/2024 Art der eingegangenen Einreichungen: Angebote Anzahl der eingegangenen Angebote oder Teilnahmeanträge: 4")
        second = self.awarded("Datum des Vertragsabschlusses: 03/02/2024 Art der eingegangenen Einreichungen: Angebote Anzahl der eingegangenen Angebote oder Teilnahmeanträge: 5")
        text = self.notice(first).replace("6. Ergebnisse", "5.1. Los: LOT-0002 Other lot 6. Ergebnisse").replace(
            "8. Organisationen", "6.1. Ergebnis, Los-– Kennung: LOT-0002 " + second + " 8. Organisationen")
        rows, _ = parse_eform_results(text, "1-2024", ["Stadt Velbert"])
        self.assertEqual([(r["lot_number"], r["received_tenders"], r["contract_conclusion_date"]) for r in rows],
                         [("LOT-0001", 4, "2024-02-02"), ("LOT-0002", 5, "2024-02-03")])

    def test_ambiguous_contracts_duplicate_totals_and_unknown_lots_require_review(self):
        cases = [self.notice(self.awarded("Informationen zum Auftrag: Datum des Vertragsabschlusses: 02/02/2024")),
                 self.notice(self.awarded("Art der eingegangenen Einreichungen: Angebote Anzahl der eingegangenen Angebote oder Teilnahmeanträge: 2 "
                                         "Art der eingegangenen Einreichungen: Angebote Anzahl der eingegangenen Angebote oder Teilnahmeanträge: 3")),
                 self.notice(self.awarded("")).replace("Kennung: LOT-0001", "Kennung: LOT-0002")]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_eform_results(text, "1-2024", ["Stadt Velbert"])


class ProvenanceTests(unittest.TestCase):
    def test_nominal_money_and_dated_party_presentation_remain_distinct(self):
        self.assertEqual(monetary_status("1.00"), "nominal_one_euro_needs_review")
        self.assertEqual(monetary_status(None), "not_reported")
        title = "Schulentwicklung völlig entgegen Elternwillen 29. April 2020 Fraktionsvorsitzende Bündnis 90/Die Grünen und Bürgermeisterkandidatin Frau Dr. Esther Kanschat"
        row = party_observation(title)
        self.assertFalse(row["official_municipal_source"])
        self.assertEqual(row["main_treatment_assignment"], "unverified")
        with self.assertRaises(ValueError):
            party_observation(title.replace("2020", "2025"))


if __name__ == "__main__":
    unittest.main()
