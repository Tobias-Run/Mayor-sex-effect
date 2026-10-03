"""Guard consequential source-linkage and outcome-classification failures.

These tests use synthetic records, require no downloads, and do not assert that
a changing live TED snapshot will retain a particular count.
"""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from bavaria_named_reports import match_round, parse_report
from bavaria_ted_linkage import contract_date, tender_count


class ElectionIdentityTests(unittest.TestCase):
    def setUp(self):
        self.report = [{"votes": 790, "candidate_name_source": "A, Person"},
                       {"votes": 736, "candidate_name_source": "B, Person"}]
        self.source = {"office_scope": "municipality", "listed_votes_reconcile": True,
                       "parse_issues": [], "candidate_slots": [
                           {"votes": 736, "slot": 2, "nomination": "B"},
                           {"votes": 790, "slot": 1, "nomination": "A"}],
                       "election_date": "2020-03-29", "municipality": "Example",
                       "source_row": 1, "valid_votes": 1526}

    def test_reordered_slots_are_matched_by_exact_votes(self):
        linked, reason = match_round("09473138", self.report, [self.source])
        self.assertIsNone(reason)
        self.assertEqual([c["historical_source_slot"] for c in linked["candidates"]], [1, 2])

    def test_preliminary_difference_and_duplicate_source_are_rejected(self):
        report = copy.deepcopy(self.report)
        report[0]["votes"] += 1
        self.assertIsNone(match_round("09473138", report, [self.source])[0])
        self.assertIsNone(match_round("09473138", self.report, [self.source, self.source])[0])

    def test_ties_and_unreported_residual_are_not_identity_links(self):
        source = copy.deepcopy(self.source)
        source["candidate_slots"][0]["votes"] = 790
        tied = [{"votes": 790}, {"votes": 790}]
        self.assertIsNone(match_round("09473138", tied, [source])[0])
        source["listed_votes_reconcile"] = False
        self.assertIsNone(match_round("09473138", self.report, [source])[0])

    def test_prior_candidates_and_county_chapter_are_excluded(self):
        text = "\n".join([
            " 188 120 Example (Lkr Example)",
            " Person, Current    Gewählt 5 412 50,5 48,0", " Party A",
            " Person, Earlier    X X 45,0", " Party B",
            " 6. Stichwahl der Landräte", " 188 000 County (Lkr Example)",
            " County, Person    Gewählt 7 000 60,0 55,0", " Party C"])
        rows = parse_report(text, {"name_format": "comma", "date": "2020-03-29",
                                   "round": "runoff", "id": "synthetic"})
        self.assertEqual(len(rows), 2)
        self.assertEqual([r["votes"] for r in rows], [5412, None])
        self.assertEqual({r["ags"] for r in rows}, {"09188120"})


class ProcurementOutcomeTests(unittest.TestCase):
    def setUp(self):
        self.notice = {"BT-142-LotResult": ["selec-w"], "result-lot-identifier": ["LOT-1"],
                       "identifier-lot": ["LOT-1"], "received-submissions-type-code": ["tenders"],
                       "received-submissions-type-val": [3], "BT-759-LotResult": ["3"],
                       "publication-date": "2024-08-22Z",
                       "contract-conclusion-date": ["2024-08-06Z"],
                       "BT-145-Contract": ["2024-08-06Z"]}

    def test_contract_date_is_not_publication_date(self):
        self.assertEqual(contract_date(self.notice), "2024-08-06")
        del self.notice["contract-conclusion-date"]
        self.assertIsNone(contract_date(self.notice))

    def test_ongoing_competition_is_never_an_awarded_bid_count(self):
        self.notice["BT-142-LotResult"] = ["open-nw"]
        for n in (0, 1, 3):
            self.notice["received-submissions-type-val"] = [n]
            self.notice["BT-759-LotResult"] = [str(n)]
            self.assertIsNone(tender_count(self.notice))

    def test_typed_count_must_identify_one_awarded_lot(self):
        self.assertEqual(tender_count(self.notice), 3)
        for change in ({"identifier-lot": ["LOT-2"]},
                       {"result-lot-identifier": ["LOT-1", "LOT-2"]},
                       {"received-submissions-type-code": ["requests"]},
                       {"BT-759-LotResult": ["4"]},
                       {"BT-142-LotResult": ["selec-w", "selec-w"]}):
            with self.subTest(change=change):
                self.assertIsNone(tender_count({**self.notice, **change}))

    def test_malformed_counts_and_dates_remain_missing(self):
        for value in ("unknown", "NaN", "Infinity", "-1", "2.5"):
            with self.subTest(value=value):
                self.assertIsNone(tender_count({**self.notice,
                    "received-submissions-type-val": [value], "BT-759-LotResult": [value]}))
        for dates in (["2024-02-30Z"], ["2024-08-06Z", "2024-08-07Z"]):
            self.assertIsNone(contract_date({**self.notice, "contract-conclusion-date": dates,
                                             "BT-145-Contract": dates}))


if __name__ == "__main__":
    unittest.main()
