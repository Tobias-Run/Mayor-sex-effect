import sys,unittest,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'/'pilot'))
from creative_cached_2024 import shared_guids
from creative_historical_bridge import total_statistics,earliest_call_date
from creative_precision_scenarios import residual_effect
from multi_candidate_plurality_screen import plurality_lead

class CreativeRouteTests(unittest.TestCase):
    def test_shared_guid_withheld_only_for_cross_election_assignment(self):
        row={'procedure_identifier_source':'guid','cohort':'NRW 2020','ags':'1'}
        self.assertEqual(shared_guids([row,dict(row)]),set())
        self.assertEqual(shared_guids([row,dict(row,ags='2')]),{'guid'})
        self.assertEqual(shared_guids([dict(row,procedure_identifier_source=''),dict(row,ags='2',procedure_identifier_source='')]),set())
    def test_subcounts_are_not_total_bids(self):
        r={'bids':{'statistics':[{'measure':'electronicBids','value':5},{'measure':'smeBids','value':5}]}}
        self.assertEqual(total_statistics(r),[])
        r['bids']['statistics'].append({'measure':'bids','value':6,'relatedLot':'1'})
        self.assertEqual(total_statistics(r)[0]['count'],6)
        r['bids']['statistics']=[{'measure':'bids','value':True}]
        self.assertEqual(total_statistics(r),[])
    def test_file_year_does_not_override_earliest_call_date(self):
        r={'date':'2021-06-01','tender':{'documents':[{'documentType':'tenderNotice','datePublished':'2019-02-01T00:00:00Z'},{'documentType':'tenderNotice','datePublished':'2021-01-01T00:00:00Z'}]}}
        self.assertEqual(earliest_call_date(r),'2019-02-01')
    def test_prognostic_variance_is_only_an_assumption(self):
        self.assertEqual(residual_effect(.5,0),.5)
        self.assertEqual(residual_effect(.5,.75),1)
        with self.assertRaises(ValueError):residual_effect(.5,1)
        with self.assertRaises(ValueError):residual_effect(.5,-.1)
    def test_plurality_gap_uses_all_votes_and_does_not_require_absolute_majority(self):
        rows=[]
        for i,v in enumerate((25,24,21),1):
            rows.append({'state':'14','ags':'14000001','ags_name':'Example','election_type':'Bürgermeisterwahl','office_type':'Bürgermeister','flag_superseded':'FALSE','flag_shared_ags':'FALSE','flag_decisive_round_missing':'FALSE','has_stichwahl':'TRUE','election_date_sw':'2022-07-03','candidate_votes_sw':str(v),'n_candidates_sw':'3','candidate_rank_sw':str(i),'is_winner':'TRUE' if i==1 else 'FALSE','candidate_voteshare_sw':str(v/70),'candidate_name':'Candidate '+str(i)})
        r=plurality_lead(rows)
        self.assertAlmostEqual(r['absolute_top_two_gap_pp'],100/70)
        self.assertEqual(r['valid_decisive_votes'],70)
        for row in rows:row['has_stichwahl']='FALSE'
        self.assertIsNone(plurality_lead(rows))

if __name__=='__main__':unittest.main()
