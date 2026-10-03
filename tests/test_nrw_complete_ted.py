"""Keep conflicting money, losing bids and unfinished procedures out of outcomes."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from nrw_full_ted_awards import legacy_lot_definition_audit, monetary_status, parse_eform_results, parse_legacy_value_mismatch


class CompleteLegacyTests(unittest.TestCase):
    def notice(self, partition="nein", definitions="", label=""):
        return ("1-2023 - Ergebnis Abschnitt I: Öffentlicher Auftraggeber "
                "Offizielle Bezeichnung: Stadt Example Postanschrift: Example "
                "Abschnitt II: Gegenstand Aufteilung des Auftrags in Lose: " + partition +
                " II.1.7. Gesamtwert der Beschaffung Wert ohne MwSt.: 200 000,00 EUR " + definitions +
                " Abschnitt V: Auftragsvergabe " + label +
                "Bezeichnung des Auftrags: Example Ein Auftrag/Los wurde vergeben: ja "
                "V.2.1. Tag des Vertragsabschlusses 08/03/2023 "
                "V.2.2. Angaben zu den Angeboten Anzahl der eingegangenen Angebote: 17 "
                "V.2.4. Angaben zum Wert des Auftrags/Loses "
                "Ursprünglich veranschlagter Gesamtwert des Auftrags/des Loses: 200 000,00 EUR "
                "Gesamtwert des Auftrags/Loses: 203 906,52 EUR")

    def test_conflicting_money_does_not_erase_scoped_dates_and_tender_totals(self):
        rows, audit = parse_legacy_value_mismatch(self.notice(), "1-2023", "Stadt Example")
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]["lot_number"])
        self.assertEqual(rows[0]["contract_conclusion_date"], "2023-03-08")
        self.assertEqual(rows[0]["received_tenders"], 17)
        self.assertEqual(rows[0]["award_value_eur"], "203906.52")
        self.assertEqual(audit["notice_value_eur"], "200000.00")
        self.assertFalse(audit["award_values_reconcile"])

    def test_numeric_lot_labels_allow_leading_zeros_but_require_full_coverage(self):
        text = self.notice("ja", "Los-Nr.: 01 II.2.2. Code", "Los-Nr.: 1 ")
        rows, audit = parse_legacy_value_mismatch(text, "1-2023", "Stadt Example")
        self.assertEqual(rows[0]["lot_number"], "1")
        self.assertEqual(audit["declared_lots_source"], ["01"])
        for bad in [text.replace("Los-Nr.: 1 ", "Los-Nr.: 2 "),
                    text.replace("Los-Nr.: 01", "Los-Nr.: 01 Los-Nr.: 1"),
                    text.replace("Los-Nr.: 01", "Los-Nr.: 01 Los-Nr.: 02"),
                    text.replace("Los-Nr.: 1 Bezeichnung", "Bezeichnung")]:
            with self.subTest(text=bad), self.assertRaises(ValueError):
                parse_legacy_value_mismatch(bad, "1-2023", "Stadt Example")

    def test_partitioned_award_without_lot_identity_cannot_be_spread_across_lots(self):
        text = self.notice("ja", "Los-Nr.: 01 II.2.2. Code Los-Nr.: 02 II.2.2. Code")
        with self.assertRaisesRegex(ValueError, "explicit numeric lot identity"):
            parse_legacy_value_mismatch(text, "1-2023", "Stadt Example")

    def test_awarded_extra_lot_is_flagged_even_when_its_money_reconciles(self):
        rows = [{"lot_number": "1"}, {"lot_number": "2"}]
        audit = legacy_lot_definition_audit(self.notice("ja", "Los-Nr.: 1 II.2.2. Code"), "1-2023", rows)
        self.assertTrue(audit["lot_definition_coverage_review_required"])
        self.assertEqual(audit["award_lots_without_definition"], ["2"])
        self.assertTrue(rows[0]["award_lot_defined_in_source"])
        self.assertFalse(rows[1]["award_lot_defined_in_source"])

    def test_repeated_label_prefix_is_a_source_number_not_an_unobserved_lot(self):
        rows = [{"lot_number": "1"}]
        text = self.notice("ja", "Los-Nr.: Los-Nr. 1 II.2.2. Code")
        audit = legacy_lot_definition_audit(text, "1-2023", rows)
        self.assertFalse(audit["lot_definition_coverage_review_required"])


class CompleteEFormTests(unittest.TestCase):
    def notice(self, result):
        return ("1-2024 - Ergebnis 1. Beschaffer 1.1. Beschaffer Offizielle Bezeichnung: Stadt Example "
                "Rechtsform des Erwerbers: Lokale Gebietskörperschaft 2. Verfahren "
                "5.1. Los: LOT-0001 Example 6. Ergebnisse 6.1. Ergebnis, Los-– Kennung: LOT-0001 " +
                result + " 8. Organisationen")

    def test_pending_competition_with_three_tenders_is_not_an_awarded_outcome(self):
        result = ("Status der Preisträgerauswahl: Ein Wettbewerbsgewinner wurde noch nicht ermittelt, "
                  "der Wettbewerb ist noch nicht abgeschlossen. 6.1.4. Statistische Informationen "
                  "Art der eingegangenen Einreichungen: Angebote Anzahl der eingegangenen Angebote oder Teilnahmeanträge: 3")
        rows, audit = parse_eform_results(self.notice(result), "1-2024", ["Stadt Example"])
        self.assertEqual(rows, [])
        self.assertEqual(audit[0]["status"], "pending_no_award_yet")

    def test_losing_bid_value_cannot_be_a_winning_price(self):
        result = ("Status der Preisträgerauswahl: Es wurde mindestens ein Gewinner ermittelt. "
                  "6.1.3. Nicht erfolgreiche Bieter Wert des Angebots: 0,00 EUR "
                  "6.1.4. Statistische Informationen")
        with self.assertRaisesRegex(ValueError, "lacks a winner section"):
            parse_eform_results(self.notice(result), "1-2024", ["Stadt Example"])

    def test_price_and_date_are_scoped_to_the_winner_not_other_bidders(self):
        result = ("Status der Preisträgerauswahl: Es wurde mindestens ein Gewinner ermittelt. "
                  "6.1.2. Informationen über die Gewinner Wert des Angebots: 250,00 EUR "
                  "Informationen zum Auftrag: Datum des Vertragsabschlusses: 01/02/2024 "
                  "6.1.3. Nicht erfolgreiche Bieter Wert des Angebots: 400,00 EUR "
                  "Datum des Vertragsabschlusses: 02/02/2024 "
                  "6.1.4. Statistische Informationen Art der eingegangenen Einreichungen: Angebote "
                  "Anzahl der eingegangenen Angebote oder Teilnahmeanträge: 2")
        rows, _ = parse_eform_results(self.notice(result), "1-2024", ["Stadt Example"])
        self.assertEqual(rows[0]["award_value_eur"], "250.00")
        self.assertEqual(rows[0]["contract_conclusion_date"], "2024-02-01")
        self.assertEqual(rows[0]["received_tenders"], 2)

    def test_one_cent_and_zero_are_flagged_separately_from_missing_values(self):
        self.assertEqual(monetary_status("0.01"), "nominal_one_cent_needs_review")
        self.assertEqual(monetary_status("0.00"), "zero_value_needs_review")
        self.assertEqual(monetary_status(None), "not_reported")


if __name__ == "__main__":
    unittest.main()
