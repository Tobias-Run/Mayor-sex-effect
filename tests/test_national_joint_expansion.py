import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'/'pilot'))
from national_joint_expansion import eligible_links,event_key
from national_result_metadata import positive_total_count
from national_joint_recovery import recovery_rank
from current_cohort_coding_handoff import blank_form,neutral_id,review_has_work

class JointExpansionTests(unittest.TestCase):
    def test_repeated_municipality_keeps_event_links_and_shared_cluster(self):
        events=[{'ags':'05000001','decisive_date':'2020-09-27'},{'ags':'05000001','decisive_date':'2025-09-28'}]
        self.assertEqual(eligible_links(events,'2025-02-01'),events[:1])
        self.assertEqual(eligible_links(events,'2026-02-01'),events[1:])
        self.assertNotEqual(event_key(events[0]),event_key(events[1]))
        older=[events[0],{'ags':'05000001','decisive_date':'2019-02-01'}]
        self.assertEqual(len(eligible_links(older,'2025-02-01')),2)
        self.assertEqual(eligible_links(events,'2024-12-31'),[])
    def test_total_tenders_require_unambiguous_successful_lot(self):
        row={'receivedSubmissionsCount':'3','receivedSubmissionsType':'tenders'};lot={'winnerChosen':'selec-w'}
        self.assertTrue(positive_total_count(row,[lot]))
        self.assertFalse(positive_total_count(row,[lot,lot]))
        self.assertFalse(positive_total_count(row,[{'winnerChosen':'open-nw'}]))
        self.assertFalse(positive_total_count(dict(row,receivedSubmissionsType='t-sme'),[lot]))
        self.assertFalse(positive_total_count(dict(row,receivedSubmissionsCount='0'),[lot]))
        self.assertFalse(positive_total_count(dict(row,receivedSubmissionsCount='3.2'),[lot]))
    def test_recovery_prioritizes_counterpart_before_unpaired_notice(self):
        call={'publication-number':'1','publication-date':'2025-03-01','procedure-identifier':'a','notice-type':'cn-standard'}
        result={'index':{'procedure-identifier':'a','notice-type':'can-standard'}}
        unpaired=dict(call,publication_number='2',**{'procedure-identifier':'b'})
        self.assertLess(recovery_rank(call,[result]),recovery_rank(unpaired,[result]))
    def test_independent_form_omits_first_coder_and_assignment_information(self):
        form=blank_form('case','A','Example Candidate','2021','Example Municipality')
        self.assertEqual(form['independent_presentation'],'')
        self.assertEqual(form['reviewer_identity'],'')
        self.assertTrue({'winner','margin','votes','first_coder_label','procurement_outcome'}.isdisjoint(form))
        self.assertEqual(form['target_election_year'],'2021')
    def test_case_ids_distinguish_repeated_municipal_elections(self):
        self.assertNotEqual(neutral_id('AGS:2020-09-27'),neutral_id('AGS:2025-09-28'))
    def test_even_partial_review_work_is_preserved(self):
        form=blank_form('case','A','Example Candidate','2021','Municipality')
        self.assertFalse(review_has_work(form))
        form['exact_locator']='Historical source p3'
        self.assertTrue(review_has_work(form))

if __name__=='__main__':unittest.main()
