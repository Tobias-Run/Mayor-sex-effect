"""Keep bid ranges and grouped-lot awards distinct from winning prices/extra units."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from nrw_full_ted_awards import parse_legacy_range_or_group


class AlternativeLegacyTests(unittest.TestCase):
    def authority(self, partition, total, definitions=""):
        return ("1-2021 - Ergebnis Abschnitt I: Öffentlicher Auftraggeber "
                "Offizielle Bezeichnung: Stadt Example Postanschrift: Example "
                "Abschnitt II: Gegenstand Aufteilung des Auftrags in Lose: " + partition +
                " II.1.7. Gesamtwert der Beschaffung Wert ohne MwSt.: " + total + " EUR II.2. Beschreibung " + definitions)

    def section(self, label, count, value):
        return (" Abschnitt V: Auftragsvergabe Auftrags-Nr.: 1 Los-Nr.: " + label +
                " Bezeichnung des Auftrags: Example Ein Auftrag/Los wurde vergeben: ja "
                "V.2.1. Tag des Vertragsabschlusses 05/07/2022 "
                "V.2.2. Angaben zu den Angeboten Anzahl der eingegangenen Angebote: " + str(count) +
                " V.2.3. Name und Anschrift Supplier V.2.4. Angaben zum Wert des Auftrags/Loses " + value)

    def grouped(self):
        return (self.authority("ja", "1,00", "Los-Nr.: 1 II.2.2. Code Los-Nr.: 2 II.2.2. Code Los-Nr.: 3 II.2.2. Code") +
                self.section("Los 1 + 2", 6, "Gesamtwert des Auftrags/Loses: 1,00 EUR") +
                self.section("Los 3", 2, "Gesamtwert des Auftrags/Loses: 1,00 EUR"))

    def test_range_does_not_supply_a_winning_price_or_an_estimated_award_value(self):
        text = self.authority("nein", "350 000,00") + self.section("1", 3,
            "Ursprünglich veranschlagter Gesamtwert des Auftrags/des Loses: 350 000,00 EUR "
            "Niedrigstes Angebot: 228 000,00 EUR / höchstes Angebot: 332 000,00 EUR das berücksichtigt wurde")
        rows, audit = parse_legacy_range_or_group(text, "1-2021", "Stadt Example")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["unit"], "undivided_contract")
        self.assertEqual(rows[0]["received_tenders"], 3)
        self.assertIsNone(rows[0]["award_value_eur"])
        self.assertEqual(rows[0]["bid_range_lower_eur"], "228000.00")
        self.assertEqual(rows[0]["bid_range_upper_eur"], "332000.00")
        self.assertIsNone(audit["award_values_reconcile"])
        self.assertEqual(audit["monetary_review_reason"], "winning_price_not_reported")

    def test_grouped_two_lots_are_one_counted_award_despite_unreconciled_money(self):
        rows, audit = parse_legacy_range_or_group(self.grouped(), "1-2021", "Stadt Example")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["lot_numbers"], ["1", "2"])
        self.assertEqual(rows[0]["unit"], "grouped_lot_award")
        self.assertEqual([r["received_tenders"] for r in rows], [6, 2])
        self.assertFalse(audit["award_values_reconcile"])
        self.assertTrue(audit["monetary_outcome_review_required"])

    def test_repeated_unknown_or_incomplete_group_members_cannot_be_guessed(self):
        for text in [self.grouped().replace("Los-Nr.: Los 3", "Los-Nr.: Los 2"),
                     self.grouped().replace("Los-Nr.: Los 1 + 2", "Los-Nr.: Los 1 + 4"),
                     self.grouped().rsplit("Abschnitt V: Auftragsvergabe", 1)[0],
                     self.grouped().replace("Los-Nr.: Los 1 + 2", "Los-Nr.: Los 1, 2")]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_legacy_range_or_group(text, "1-2021", "Stadt Example")


if __name__ == "__main__":
    unittest.main()
