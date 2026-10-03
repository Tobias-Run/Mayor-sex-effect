"""Protect tenure boundaries and multi-lot legacy outcome measurement."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from bavaria_candidate_register import first_appointment_start, in_interval, presentation
from bavaria_evidence_sources import council_role
from bavaria_legacy_ted_awards import parse_legacy_awards


class TenureTests(unittest.TestCase):
    def test_first_ever_entry_does_not_date_a_renewed_term(self):
        self.assertIsNone(first_appointment_start("2014-05-01", "2020-03-29"))
        self.assertEqual(first_appointment_start("2020-05-01", "2020-03-29"), "2020-05-01")

    def test_successor_entry_is_exclusive_and_missing_date_stays_unknown(self):
        self.assertTrue(in_interval("2020-05-01", "2020-05-01", "2026-05-01"))
        self.assertTrue(in_interval("2026-04-30", "2020-05-01", "2026-05-01"))
        for day in ("2026-05-01", "2026-05-07", "2020-03-29"):
            self.assertFalse(in_interval(day, "2020-05-01", "2026-05-01"))
        self.assertIsNone(in_interval(None, "2020-05-01", "2026-05-01"))

    def test_conflicting_titles_are_not_overwritten(self):
        self.assertEqual(presentation([{"documented_title_presentation": "female"},
                                       {"documented_title_presentation": "male"}]), "conflict")

    def test_committee_end_and_unselected_period_are_not_head_role_evidence(self):
        raw = '''Person A <a class="smcfiltermenuselected">Wahlperiode 2020 - 2026</a>
        <a>Wahlperiode 2026 - 2032</a><table>
        <tr><td data-label="Gremium">Committee</td><td data-label="Mitarbeit">1. Bürgermeister</td>
        <td data-label="Ende">04.05.2026</td></tr>
        <tr><td data-label="Gremium">City council</td><td data-label="Mitarbeit">1. Bürgermeister</td>
        <td data-label="Ende">30.04.2026</td></tr></table>'''
        row = council_role(raw, "Person A", "2020 - 2026", "City council", "1. Bürgermeister")
        self.assertEqual(row["Ende"], "30.04.2026")
        with self.assertRaises(ValueError):
            council_role(raw, "Person A", "2026 - 2032", "City council", "1. Bürgermeister")
        with self.assertRaises(ValueError):
            council_role(raw, "Person A", "2020 - 2026", "City council", "2. Bürgermeister")


class LegacyAwardTests(unittest.TestCase):
    def notice(self, sections, total="30,00", divided="ja"):
        return ("123-2023 - Ergebnis Bekanntmachung vergebener Aufträge "
                "Abschnitt I: Öffentlicher Auftraggeber I.1. Offizielle Bezeichnung: Example city "
                "Postanschrift: Rathaus Abschnitt II: Gegenstand "
                f"Aufteilung des Auftrags in Lose: {divided} "
                f"II.1.7. Gesamtwert der Beschaffung Wert ohne MwSt.: {total} EUR " + sections)

    def section(self, lot, day, count, value):
        return ("Abschnitt V: Auftragsvergabe " + (f"Los-Nr.: {lot} " if lot else "") +
                "Ein Auftrag/Los wurde vergeben: ja V.2.1. Tag des Vertragsabschlusses " + day +
                " V.2.2. Angaben zu den Angeboten Anzahl der eingegangenen Angebote: " + str(count) +
                " Anzahl der eingegangenen Angebote von KMU: 0 "
                "V.2.3. Name und Anschrift Supplier A V.2.3. Name und Anschrift Supplier B "
                "V.2.4. Angaben zum Wert Gesamtwert des Auftrags/Loses: " + value + " EUR ")

    def test_lots_keep_separate_dates_and_counts_despite_multiple_suppliers(self):
        raw = self.notice(self.section("1", "03/07/2023", 1, "10,00") +
                          self.section("2", "14/07/2023", 2, "20,00"))
        rows, audit = parse_legacy_awards(raw, "123-2023", "Example city")
        self.assertEqual([(r["contract_conclusion_date"], r["received_tenders"]) for r in rows],
                         [("2023-07-03", 1), ("2023-07-14", 2)])
        self.assertEqual(len(rows), 2)
        self.assertEqual(audit["award_sections"], 2)

    def test_undivided_consortium_is_one_award(self):
        rows, _ = parse_legacy_awards(self.notice(self.section(None, "25/02/2021", 2, "30,00"), divided="nein"),
                                      "123-2023", "Example city")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["supplier_blocks_in_award"], 2)

    def test_inconsistent_values_duplicate_lot_buyer_and_unawarded_are_rejected(self):
        section = self.section("1", "03/07/2023", 1, "30,00")
        cases = [self.notice(section, total="40,00"),
                 self.notice(section + section, total="60,00"),
                 self.notice(section).replace("Example city", "County administration"),
                 self.notice(section).replace("vergeben: ja", "vergeben: nein"),
                 self.notice(section).replace("03/07/2023", "30/02/2023")]
        for raw in cases:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_legacy_awards(raw, "123-2023", "Example city")


if __name__ == "__main__":
    unittest.main()
