"""Validity boundaries for the P1/P2 scoreboard and plurality audit."""
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src/pilot'))
from measurable_progress import official_round,boundary,pair,indexed,saxony_aliases
from cohort_expansion_national import municipal_match

class ProgressValidityTests(unittest.TestCase):
    def setUp(self):
        self.lead={'ags':'14612000','municipality':'Example, Stadt','decisive_date':'2022-07-03','valid_decisive_votes':100,'final_candidate_count':3,'candidates':[{'votes':45},{'votes':40},{'votes':15}]}
        self.raw='''<h1>Endgültiges Ergebnis - 2. Wahlgang am 03.07.2022 in der Gemeinde Example, Stadt</h1>
<table><tr><th>Gewählter Bürgermeister</th><th>Absolut</th><th>Prozent</th></tr><tr><td>Winner, Person (Group)</td><td>45</td><td>45,0</td></tr></table>
<table><tr><th></th><th>Absolut</th><th>Prozent</th></tr><tr><td>Gültige Stimmen</td><td>100</td><td>100,0</td></tr><tr><td>Third, Person (Group)</td><td>15</td><td>15,0</td></tr><tr><td>Other, Person (Group)</td><td>40</td><td>40,0</td></tr><tr><td>Winner, Person (Group)</td><td>45</td><td>45,0</td></tr></table>'''.encode()
    def test_exact_final_original_reconciles_all_ranked_candidates(self):
        self.assertEqual([c['votes'] for c in official_round(self.raw,self.lead)],[45,40,15])
    def test_http_success_wrong_selector_or_provisional_round_is_not_evidence(self):
        for data in [b'<html>Google Gmail Images Sign in</html>',self.raw.replace('Endgültiges'.encode(),'Vorläufiges'.encode())]:
            with self.assertRaises(ValueError):official_round(data,self.lead)
    def test_incomplete_candidate_vector_or_wrong_total_fails(self):
        for data in [self.raw.replace(b'<td>100</td>',b'<td>99</td>'),self.raw.replace(b'<td>15</td>',b'<td>14</td>')]:
            with self.assertRaises(ValueError):official_round(data,self.lead)
    def test_margin_uses_all_votes_and_geometric_check_is_not_certification(self):
        result=boundary(self.lead)
        self.assertEqual(result['top_two_gap_pp'],5)
        self.assertEqual(result['runner_up_third_gap_pp'],25)
        self.assertTrue(result['third_below_tied_top_if_winner_votes_transferred_to_runner'])
        self.assertFalse(result['causal_boundary_stability_certified'])
    def test_unknown_opponent_does_not_become_same_or_mixed_pair(self):
        self.assertEqual(pair(['female','unresolved']),'unresolved')
        self.assertEqual(pair(['female','male']),'mixed_public_presentation')
    def test_repeat_municipality_cohorts_remain_distinct_and_duplicate_join_fails(self):
        events=[{'cohort':'2020','ags':'00000001'},{'cohort':'2025','ags':'00000001'}]
        self.assertEqual(len(indexed(events)),2)
        with self.assertRaises(ValueError):indexed(events+[events[0]])
    def test_exact_dresden_authority_alias_excludes_utility_and_multiple_buyers(self):
        aliases=saxony_aliases([self.lead])
        buyer={'organisationName':'Landeshauptstadt Dresden','organisationCountryCode':'DEU','buyerLegalType':'kommun-beh'}
        self.assertEqual(municipal_match([buyer],aliases)[0],'14612000')
        self.assertIsNone(municipal_match([buyer,buyer],aliases)[0])
        self.assertIsNone(municipal_match([dict(buyer,organisationName='Stadtwerke Dresden')],aliases)[0])
        self.assertIsNone(municipal_match([dict(buyer,organisationCountryCode='AUT')],aliases)[0])

if __name__=='__main__':unittest.main()
