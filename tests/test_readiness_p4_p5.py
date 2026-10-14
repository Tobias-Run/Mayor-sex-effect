"""Guard against inflated samples and falsely completed independent review."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src/pilot'))
from readiness_p4_p5 import possible_sides,feasible_wins,conditional_bound,benchmark,packet_audit,rows,DOC
from nrw_early_feasibility import design_support

class ReadinessTests(unittest.TestCase):
    def test_partial_labels_constrain_favorable_bounds(self):
        self.assertEqual(possible_sides('male',None),{False})
        self.assertEqual(possible_sides(None,'female'),{False})
        self.assertEqual(possible_sides('female',None),{True})
        self.assertEqual(possible_sides('female','female'),set())
        self.assertEqual(possible_sides('same_presentation','same_presentation'),set())
        self.assertEqual(feasible_wins([{False},{False},{True,False}]),{0,1})
    def test_duplicate_municipalities_do_not_inflate_independent_elections(self):
        c={'cohort':'A','ags':'001'}
        with self.assertRaises(ValueError):conditional_bound([c,c],{})
    def test_cohort_specific_labels_do_not_leak_between_elections(self):
        result=conditional_bound([{'cohort':'A','ags':'001'}],{('B','001'):['male','male']})
        self.assertEqual(result['conditional_max_mixed_elections'],1)
        self.assertEqual(result['feasible_female_wins_max'],1)
    def test_one_side_has_no_contrast_and_four_cases_no_rdd_residual_df(self):
        self.assertIsNone(benchmark(0,4)['mde_sd'])
        self.assertIsNone(benchmark(1,1)['mde_sd'])
        self.assertEqual(design_support([-1.25,-.86,4.39,4.55])['linear_residual_df'],0)
    def test_known_same_pairs_stay_out_of_favorable_ceiling(self):
        result=conditional_bound([{'cohort':'A','ags':'001'}],{('A','001'):['female','female']})
        self.assertEqual(result['conditional_max_mixed_elections'],0)
        self.assertIsNone(result['mde_sd'])
    def test_prepared_packet_is_not_independent_completion(self):
        if not Path('data/interim/current-cohort-independent-coding.zip').exists():self.skipTest('Private source packet not distributed')
        links={r['event_key'] for r in rows(DOC/'eligibility-scoreboard-events.csv') if r['provisional_mixed_count_link']=='True'}
        result=packet_audit(links)
        self.assertEqual(result['completed_independent_pairs'],0)
        self.assertIsNone(result['candidate_agreement'])
        self.assertEqual(result['source_copies_verified'],22)

if __name__=='__main__':unittest.main()
