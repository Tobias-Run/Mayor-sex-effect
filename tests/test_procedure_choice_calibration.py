"""Calibration validity tests: selection, timing, denominators and source scope."""
import csv,random,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src/pilot'))
from procedure_choice_calibration import select_cases,unique_documents,award_timing,original_fields,assess_scope

class ProcedureCalibrationTests(unittest.TestCase):
    def test_selection_is_order_independent_and_retains_unmatched_control(self):
        path=Path(__file__).resolve().parents[1]/'docs/feasibility/creative-procedure-choice-assignment-opportunities.csv'
        with path.open() as handle:frame=list(csv.DictReader(handle))
        first=select_cases(frame)
        random.Random(9).shuffle(frame)
        self.assertEqual(first,select_cases(frame))
        self.assertEqual([r['ags'] for r in first],['05378028','05970044','05962024','05158032','05978036','05962032','05570008','05978024','05166032','05166012'])
        self.assertEqual(first[-1]['has_method_metadata_pre_and_post'],'False')
    def test_missing_source_election_does_not_shrink_denominator_silently(self):
        with self.assertRaises(ValueError):select_cases([])
    def test_repeated_award_document_is_not_another_procedure_or_notice(self):
        document={'url':'https://example.test/notice/1','documentType':'awardNotice','datePublished':'2019-01-14'}
        self.assertEqual(len(unique_documents([document,dict(document)])),1)
    def test_award_year_does_not_equal_publication_or_snapshot_year(self):
        self.assertEqual(award_timing(['2018-12-17'],'2019'),'outside_source_year_or_spanning_years')
        self.assertEqual(award_timing([],'2021'),'missing')
        self.assertEqual(award_timing(['2021-01-01','2022-01-01'],'2021'),'outside_source_year_or_spanning_years')
    def test_method_parser_uses_scoped_literal_not_broad_open_or_body_mentions(self):
        text='''<h1>1-2021 - Competition</h1>OJ S 1/2021 10/03/2021
I.1. Name and addresses Official name: Stadt Example Postal address: Street Town: Example Country: Germany E-mail: source@example.test I.3. Communication
I.4. Type of the contracting authority Regional or local authority I.5. Main activity
Section II: Object Description mentions Open procedure
IV.1.1. Type of procedure Competitive procedure with negotiation IV.1.3. Information
VI.5. Date of dispatch of this notice 05/03/2021'''
        result=original_fields(text.encode(),'original.html','1-2021')
        self.assertEqual(result['method_details'],'pt_competitive_negotiation')
        self.assertEqual(result['dispatch_date'],'2021-03-05')
        self.assertEqual(result['publication_date'],'2021-03-10')
        self.assertFalse(result['decision_date_verified'])
    def test_empty_accepted_response_or_wrong_notice_is_not_original_evidence(self):
        for data in (b'',b'<html>Other notice</html>'):
            with self.assertRaises(ValueError):original_fields(data,'original.html','1-2021')
    def test_named_city_does_not_override_country_or_authority_type_conflict(self):
        fields={'buyer_names':['Stadt Example'],'buyer_country':'Germany','municipal_buyer_type':False}
        self.assertEqual(assess_scope(fields,'Stadt Example'),'named_municipality_but_authority_type_conflict')
        fields.update(municipal_buyer_type=True,buyer_country='Austria')
        self.assertEqual(assess_scope(fields,'Stadt Example'),'country_missing_or_conflicting')
        fields.update(buyer_country='Germany',buyer_names=['Stadt Example','Stadt Other'])
        self.assertEqual(assess_scope(fields,'Stadt Example'),'unresolved_multiple_or_missing_named_buyers')

if __name__=='__main__':unittest.main()
