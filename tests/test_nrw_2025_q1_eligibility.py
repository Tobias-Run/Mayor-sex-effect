"""Protect lot-statistic identity, genuine missingness and municipal roles."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'/'pilot'))
from federal_procurement import safe_xml, NS
from nrw_2025_q1_eligibility import lot_audit, municipal_scope, audit_procedure

PREFIX='''xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1" xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"'''

def fixture():
    xml='<Notice '+PREFIX+'><cac:TenderingProcess><cbc:ProcedureCode>open</cbc:ProcedureCode></cac:TenderingProcess>'
    xml+='<cac:ContractingParty><cac:ContractingPartyType><cbc:PartyTypeCode>kommun-beh</cbc:PartyTypeCode></cac:ContractingPartyType><cac:Party><cac:PartyIdentification><cbc:ID>ORG-CITY</cbc:ID></cac:PartyIdentification></cac:Party></cac:ContractingParty>'
    xml+='<efac:Organizations>'
    for oid,name in [('ORG-CITY','Stadt Example'),('ORG-WINNER','Supplier'),('ORG-AGENT','Service provider')]:
        xml+='<efac:Organization><efac:Company><cac:PartyIdentification><cbc:ID>'+oid+'</cbc:ID></cac:PartyIdentification><cac:PartyName><cbc:Name>'+name+'</cbc:Name></cac:PartyName></efac:Company></efac:Organization>'
    xml+='</efac:Organizations>'
    for i in (1,2):xml+='<cac:ProcurementProjectLot><cbc:ID>LOT-'+str(i)+'</cbc:ID></cac:ProcurementProjectLot>'
    xml+='<efac:NoticeResult><efac:TenderingParty><cbc:ID>PARTY-1</cbc:ID><efac:Tenderer><cbc:ID>ORG-WINNER</cbc:ID></efac:Tenderer></efac:TenderingParty>'
    xml+='<efac:SettledContract><cbc:ID>CON-1</cbc:ID><cbc:IssueDate>2026-05-04</cbc:IssueDate><efac:LotTender><cbc:ID>TEN-1</cbc:ID></efac:LotTender><efac:LotTender><cbc:ID>TEN-2</cbc:ID></efac:LotTender></efac:SettledContract>'
    for i in (1,2):
        n=str(i)
        xml+='<efac:LotTender><cbc:ID>TEN-'+n+'</cbc:ID><efac:TenderLot><cbc:ID>LOT-'+n+'</cbc:ID></efac:TenderLot><efac:TenderingParty><cbc:ID>PARTY-1</cbc:ID></efac:TenderingParty></efac:LotTender>'
        xml+='<efac:LotResult><cbc:ID>RES-'+n+'</cbc:ID><cbc:TenderResultCode>selec-w</cbc:TenderResultCode><efac:TenderLot><cbc:ID>LOT-'+n+'</cbc:ID></efac:TenderLot><efac:LotTender><cbc:ID>TEN-'+n+'</cbc:ID></efac:LotTender><efac:SettledContract><cbc:ID>CON-1</cbc:ID></efac:SettledContract><efac:ReceivedSubmissionsStatistics><efbc:StatisticsCode>tenders</efbc:StatisticsCode><efbc:StatisticsNumeric>'+str(i+2)+'</efbc:StatisticsNumeric></efac:ReceivedSubmissionsStatistics></efac:LotResult>'
    return safe_xml((xml+'</efac:NoticeResult></Notice>').encode())

class EligibilityTests(unittest.TestCase):
    def test_one_contract_covering_two_lots_keeps_two_distinct_statistics(self):
        rows=lot_audit(fixture())
        self.assertEqual([r['explicit_total_tenders'] for r in rows],[3,4])
        self.assertTrue(all(r['award_graph_supported'] and r['cross_lot_contract_supported'] for r in rows))
        self.assertEqual({r['contract_ids'] for r in rows},{'CON-1'})

    def test_missing_reciprocal_result_reference_cannot_validate_cross_lot_contract(self):
        root=fixture();parent=root.find('efac:NoticeResult',NS)
        parent.remove(parent.findall('efac:LotResult',NS)[1])
        row=lot_audit(root)[0]
        self.assertFalse(row['award_graph_supported'])
        self.assertIn('nonreciprocal_contract_result_tender',row['audit_reasons'])

    def test_subset_or_duplicate_totals_do_not_replace_explicit_total(self):
        for kind in ('subset','duplicate'):
            root=fixture();lr=root.find('.//efac:LotResult',NS);stat=lr.find('efac:ReceivedSubmissionsStatistics',NS)
            if kind=='subset':stat.find('efbc:StatisticsCode',NS).text='tenders-sme'
            else:lr.append(copy.deepcopy(stat))
            row=lot_audit(root)[0]
            self.assertIsNone(row['explicit_total_tenders'])
            self.assertIn('missing_duplicate_or_invalid_total',row['audit_reasons'])

    def test_closed_without_winner_with_one_reported_tender_is_not_a_successful_single_tender_award(self):
        root=fixture();root.find('.//efac:LotResult/cbc:TenderResultCode',NS).text='clos-nw'
        row=lot_audit(root)[0]
        self.assertEqual(row['result_status'],'clos-nw')
        self.assertFalse(row['award_graph_supported'])

    def test_named_service_organization_is_not_a_second_contracting_buyer(self):
        root=fixture()
        self.assertEqual(municipal_scope(root,{'stadt example'})['scope_status'],'sole_named_municipal_contracting_party_supported')
        # Extra organizations already include the procurement agent; only actual buyer roles count.
        root.append(copy.deepcopy(root.find('cac:ContractingParty',NS)))
        self.assertEqual(municipal_scope(root,{'stadt example'})['scope_status'],'scope_unresolved')

    def test_missing_result_is_retained_in_called_inventory(self):
        root=fixture();roster={'ags':'05','procedure_identifier':'g','root_call_publication_number':'1-2026'}
        r={'index':{'publication-number':'1-2026','publication-date':'2026-02-01','notice-type':'cn-standard'},'xml':{'procedure_identifier':'g','notice_issue_date_source':'2026-01-30'}}
        row,units=audit_procedure(roster,[r],{'1-2026':root},{'stadt example'})
        self.assertTrue(row['candidate_called_composition_population_supported'])
        self.assertEqual(row['result_followup_status'],'no_indexed_standard_result_by_cutoff')
        self.assertEqual(units,[])
        self.assertFalse(row['all_category_negotiated_population_supported'])

    def test_contract_before_call_does_not_get_a_fabricated_supported_date(self):
        root=fixture();root.find('.//efac:SettledContract/cbc:IssueDate',NS).text='2025-11-01'
        roster={'ags':'05','procedure_identifier':'g','root_call_publication_number':'1-2026'}
        call={'index':{'publication-number':'1-2026','publication-date':'2026-02-01','notice-type':'cn-standard'},'xml':{'procedure_identifier':'g','notice_issue_date_source':'2026-01-30'}}
        result={'index':{'publication-number':'2-2026','publication-date':'2026-05-10','notice-type':'can-standard'},'xml':{'procedure_identifier':'g','notice_issue_date_source':'2026-05-09'},'xml_sha256':'fixture'}
        row,units=audit_procedure(roster,[call,result],{'1-2026':root,'2-2026':root},{'stadt example'})
        self.assertTrue(all(u['candidate_count_population_supported'] for u in units))
        self.assertFalse(any(u['dated_count_population_supported'] for u in units))
        self.assertTrue(all(u['contract_conclusion_date']=='2025-11-01' for u in units))

if __name__=='__main__':unittest.main()
