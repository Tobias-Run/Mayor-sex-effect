import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'/'pilot'))
from original_recovery import alignment_days,recovery_queue
from recovery_assignment import evidence_supported

class RecoveryTests(unittest.TestCase):
    def test_alignment_crosses_year_boundary(self):
        self.assertEqual(alignment_days('2026-01-01+01:00'),['2026-01-01','2025-12-31','2025-12-30'])
    def test_zero_statistic_supported_root_prioritized_before_missing_calls(self):
        procedures=[{'procedure_identifier':'a','cohort':'Niedersachsen 2021','ags':'1','original_issue_publication_inside_window':'True','sole_original_municipal_root_buyer_supported':'True'}, {'procedure_identifier':'b','cohort':'NRW 2025','ags':'2','original_issue_publication_inside_window':'False','sole_original_municipal_root_buyer_supported':'False'}]
        linked=[{'cohort':'Niedersachsen 2021','ags':'1','observed_supported_tender_statistics':'0'}]
        notices=[{'publication-number':'call','procedure-identifier':'b','notice-type':'cn-standard','publication-date':'2026-01-01'}, {'publication-number':'result','procedure-identifier':'a','notice-type':'can-standard','publication-date':'2025-09-01'}]
        self.assertEqual([n['publication-number'] for n in recovery_queue(notices,[],procedures,linked)],['result','call'])
        self.assertEqual(recovery_queue(notices,[{'index':notices[1]}],procedures,linked),[notices[0]])
    def test_candidate_name_alone_or_wrong_election_date_is_insufficient(self):
        raw=b'<html>Alex Example Mayor candidate 24 August 2021</html>'
        self.assertTrue(evidence_supported(raw,'page.html','Alex Example','Mayor candidate','24 August 2021'))
        self.assertFalse(evidence_supported(raw,'page.html','Alex Example','female candidate','24 August 2021'))
        self.assertFalse(evidence_supported(raw,'page.html','Alex Example','Mayor candidate','24 August 2025'))

if __name__=='__main__':unittest.main()
