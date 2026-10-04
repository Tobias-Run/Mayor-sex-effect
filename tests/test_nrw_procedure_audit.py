"""Guard version identity, local-ID collisions and flattened indexed statistics."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from nrw_procedure_audit import legacy_reference, local_reference_groups, procedure_groups, single_awarded_lot_total, version_links
from nrw_historical_presentation_followup import followup_presentations

P1 = "11111111-1111-1111-1111-111111111111"
P2 = "22222222-2222-2222-2222-222222222222"
N1 = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
N2 = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"


def lot_notice():
    return {"result-lot-identifier": ["LOT-0001"], "identifier-lot": ["LOT-0001"], "BT-142-LotResult": ["selec-w"],
            "received-submissions-type-code": ["tenders", "t-esubm"], "received-submissions-type-val": ["4", "4"],
            "BT-759-LotResult": ["4", "4"]}


class ProcedureIdentityTests(unittest.TestCase):
    def test_same_guid_is_scoped_to_city(self):
        records = [{"publication-number": "A", "procedure-identifier": P1}, {"publication-number": "B", "procedure-identifier": P1}]
        self.assertEqual(len(procedure_groups(records, {"A": {"ags": "1"}, "B": {"ags": "2"}})), 2)
        self.assertEqual(len(procedure_groups(records, {"A": {"ags": "1"}, "B": {"ags": "1"}})), 1)

    def test_generic_local_reference_does_not_override_different_guids(self):
        records = [{"publication-number": "A", "procedure-identifier": P1, "internal-identifier-proc": "standard label"},
                   {"publication-number": "B", "procedure-identifier": P2, "internal-identifier-proc": "standard label"}]
        group = local_reference_groups(records, {"A": {"ags": "1"}, "B": {"ags": "1"}}, "internal-identifier-proc")[0]
        self.assertEqual(group["distinct_nonmissing_procedure_guids"], 2)
        self.assertFalse(group["automatic_merge"])

    def test_parent_uuid_and_version_must_both_match(self):
        parent = {"publication-number": "A", "procedure-identifier": P1, "notice-identifier": N1, "notice-version": 1}
        child = {"publication-number": "B", "procedure-identifier": P1, "notice-identifier": N2, "notice-version": 1,
                 "change-notice-version-identifier": N1 + "-01"}
        index = {"A": {"ags": "1"}, "B": {"ags": "1"}}
        self.assertEqual(version_links([parent, child], index)[0]["status"], "verified_same_city_procedure_parent_version")
        child["change-notice-version-identifier"] = N1 + "-02"
        self.assertEqual(version_links([parent, child], index)[0]["status"], "unresolved_parent_version")

    def test_conflicting_procedure_and_changed_statuses_are_preserved(self):
        parent = {"publication-number": "A", "procedure-identifier": P1, "notice-identifier": N1, "notice-version": 1, "BT-142-LotResult": ["open-nw"]}
        child = {"publication-number": "B", "procedure-identifier": P2, "change-notice-version-identifier": N1 + "-01", "BT-142-LotResult": ["selec-w"]}
        row = version_links([parent, child], {"A": {"ags": "1"}, "B": {"ags": "1"}})[0]
        self.assertEqual(row["status"], "identity_conflict_review")
        self.assertEqual(row["parent_result_statuses_source"], ["open-nw"])
        self.assertFalse(row["automatic_award_deduplication"])


class IndexedStatisticTests(unittest.TestCase):
    def test_equal_values_are_invariant_to_type_order_without_imputing_date(self):
        notice = lot_notice()
        first = single_awarded_lot_total(notice)
        notice["received-submissions-type-code"].reverse()
        self.assertEqual(first["received_tenders"], single_awarded_lot_total(notice)["received_tenders"])
        self.assertIsNone(first["contract_conclusion_date"])
        self.assertFalse(first["fulltext_validated"])

    def test_unequal_values_cannot_be_zipped_to_types(self):
        notice = lot_notice()
        notice["received-submissions-type-val"] = notice["BT-759-LotResult"] = ["4", "3"]
        self.assertIsNone(single_awarded_lot_total(notice))

    def test_multiple_lots_and_pending_results_cannot_supply_awarded_lot_counts(self):
        notice = lot_notice()
        notice["identifier-lot"] = ["LOT-0001", "LOT-0002"]
        self.assertIsNone(single_awarded_lot_total(notice))
        notice = lot_notice()
        notice["BT-142-LotResult"] = ["open-nw"]
        self.assertIsNone(single_awarded_lot_total(notice))

    def test_noninteger_nonfinite_zero_and_inconsistent_aliases_are_rejected(self):
        for value in ["0", "-1", "1.5", "NaN", "Infinity"]:
            notice = lot_notice()
            notice["received-submissions-type-val"] = notice["BT-759-LotResult"] = [value, value]
            self.assertIsNone(single_awarded_lot_total(notice))
        notice = lot_notice()
        notice["BT-759-LotResult"] = ["5", "5"]
        self.assertIsNone(single_awarded_lot_total(notice))

    def test_missing_or_repeated_total_type_stays_unknown(self):
        notice = lot_notice()
        for codes in [["t-esubm", "t-sme"], ["tenders", "tenders"]]:
            notice["received-submissions-type-code"] = codes
            self.assertIsNone(single_awarded_lot_total(notice))


class HistoricalSourceTests(unittest.TestCase):
    def test_legacy_reference_stays_in_procedure_header(self):
        text = "Abschnitt I: Öffentlicher Auftraggeber II.1.1. Bezeichnung Referenznummer der Bekanntmachung: TEST/2020 II.1.2. Hauptcode V. Referenznummer der Bekanntmachung: OTHER"
        self.assertEqual(legacy_reference(text), "TEST/2020")
        self.assertIsNone(legacy_reference("V. Referenznummer der Bekanntmachung: OTHER"))

    def source_fixture(self):
        return {"warntafel-auf-der-elisabethstrasse-wieder-aufstellen": "Frau Bürgermeisterin Susanne Stupp Frechen, 23.09.2020 / 66 September 30, 2020",
                "strassenausbaubeitraege-nicht-mehr-zeitgemaess": "Bürgermeisterkandidat Carsten Peters August 31, 2020",
                "werdohl-spaeinghaus-2020": "Andreas Späinghaus zum Bürgermeister-Kandidaten gewählt am 14.06.2020 wurde Andreas Späinghaus offiziell mit 100 % der Stimmen zum Bürgermeisterkandidaten gewählt",
                "werdohl-silvia-2017": "Bürgermeisterin Silvia Voßloh Haushaltsberatung 2017 Vom 13.-14. Oktober"}

    def test_letter_event_and_article_dates_are_distinct(self):
        observations = followup_presentations(self.source_fixture())
        self.assertEqual(observations[0]["observation_date"], "2020-09-23")
        self.assertEqual(observations[0]["article_publication_date"], "2020-09-30")
        self.assertTrue(observations[2]["article_publication_day_not_certified"])
        self.assertEqual(observations[3]["date_precision"], "month")
        self.assertFalse(observations[3]["historical_2020_observation"])

    def test_surname_only_or_wrong_historical_year_is_not_an_exact_observation(self):
        raw = self.source_fixture()
        raw["werdohl-silvia-2017"] = raw["werdohl-silvia-2017"].replace("Silvia Voßloh", "Voßloh")
        with self.assertRaises(ValueError):
            followup_presentations(raw)


if __name__ == "__main__":
    unittest.main()
