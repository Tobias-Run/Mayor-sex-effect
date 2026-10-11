"""Protect completed-but-unresolved searches and prediction-neutral scope."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'/'pilot'))
from nrw_2025_closest_review import assemble_review

class ClosestReviewTests(unittest.TestCase):
    def fixture(self):
        events=[{'ags':'05','decisive_pair':True,'absolute_margin_pp':2.0,'municipality_source':'Example, Stadt'}]
        records=[{'ags':'05','official_finalist_role':role,'disposition':'reviewed_unresolved','tier':'E','source_id':'failed-search','reason':'No accessible original primary evidence.','context_date':'2025','context':'named_2025_candidacy'} for role in ('winner','loser')]
        return events, records, {'05':{'verified_original_q1_procedures':'0'}}

    def test_no_accepted_evidence_and_no_procurement_does_not_drop_election(self):
        events, records, coverage=self.fixture()
        rows=assemble_review(events,[],records,coverage)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['pair_status'],'unresolved')
        self.assertTrue(rows[0]['review_complete'])
        self.assertEqual(rows[0]['original_q1_procedures'],0)
        self.assertIsNone(rows[0]['female_presented_winner'])

    def test_missing_or_duplicate_finalist_cannot_close_review(self):
        events, records, coverage=self.fixture()
        for bad in (records[:1],records+[records[0]]):
            with self.assertRaises(ValueError):assemble_review(events,[],bad,coverage)

    def test_exact_inclusive_scope_ignores_predictions_and_procurement(self):
        events, records, coverage=self.fixture()
        events[0]['predicted_gender']='same'
        events.append({'ags':'06','decisive_pair':True,'absolute_margin_pp':2.00001,'municipality_source':'Outside'})
        self.assertEqual(len(assemble_review(events,[],records,coverage)),1)
        bad=records+[dict(records[0],ags='06')]
        with self.assertRaises(ValueError):assemble_review(events,[],bad,coverage)

if __name__=='__main__':unittest.main()
