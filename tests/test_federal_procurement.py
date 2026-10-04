"""Guard scoped XML result linkage, original dates and exact notice versions."""
import copy
import hashlib
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from federal_procurement import NS, export_url, identity, parse_competition, parse_eforms, source_date, verified_archive
from nrw_federal_procurement import select_xml

N1 = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
P1 = "11111111-1111-1111-1111-111111111111"


def fixture():
    xml = f'''<ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cbc="{NS['cbc']}" xmlns:cac="{NS['cac']}" xmlns:efac="{NS['efac']}" xmlns:efbc="{NS['efbc']}">
      <cbc:ID>{N1}</cbc:ID><cbc:VersionID>01</cbc:VersionID>
      <cbc:ContractFolderID>{P1}</cbc:ContractFolderID><cbc:NoticeTypeCode>can-standard</cbc:NoticeTypeCode>
      <cbc:IssueDate>2024-06-26+02:00</cbc:IssueDate>
      <cac:ContractingParty><cac:Party><cac:PartyIdentification><cbc:ID>BUYER</cbc:ID></cac:PartyIdentification></cac:Party></cac:ContractingParty>
      <cac:ProcurementProjectLot><cbc:ID>LOT-1</cbc:ID></cac:ProcurementProjectLot>
      <cac:ProcurementProjectLot><cbc:ID>LOT-2</cbc:ID></cac:ProcurementProjectLot>
      <efac:Organizations>
        <efac:Organization><efac:Company><cac:PartyIdentification><cbc:ID>BUYER</cbc:ID></cac:PartyIdentification><cac:PartyName><cbc:Name>Example City</cbc:Name></cac:PartyName></efac:Company></efac:Organization>
        <efac:Organization><efac:Company><cac:PartyIdentification><cbc:ID>WINNER</cbc:ID></cac:PartyIdentification><cac:PartyName><cbc:Name>Example Supplier</cbc:Name></cac:PartyName></efac:Company></efac:Organization>
      </efac:Organizations><efac:NoticeResult>'''
    for i, total, subset in [(1, 5, 4), (2, 3, 2)]:
        xml += f'''<efac:LotResult><cbc:ID>RES-{i}</cbc:ID><cbc:TenderResultCode>selec-w</cbc:TenderResultCode>
          <efac:TenderLot><cbc:ID>LOT-{i}</cbc:ID></efac:TenderLot>
          <efac:LotTender><cbc:ID>TEN-{i}</cbc:ID></efac:LotTender>
          <efac:SettledContract><cbc:ID>CON-{i}</cbc:ID></efac:SettledContract>
          <efac:ReceivedSubmissionsStatistics><efbc:StatisticsCode>t-esubm</efbc:StatisticsCode><efbc:StatisticsNumeric>{subset}</efbc:StatisticsNumeric></efac:ReceivedSubmissionsStatistics>
          <efac:ReceivedSubmissionsStatistics><efbc:StatisticsCode>tenders</efbc:StatisticsCode><efbc:StatisticsNumeric>{total}</efbc:StatisticsNumeric></efac:ReceivedSubmissionsStatistics>
          </efac:LotResult>
          <efac:SettledContract><cbc:ID>CON-{i}</cbc:ID><cbc:AwardDate>2024-05-01+02:00</cbc:AwardDate><cbc:IssueDate>2024-06-0{i}+02:00</cbc:IssueDate><efac:LotTender><cbc:ID>TEN-{i}</cbc:ID></efac:LotTender></efac:SettledContract>
          <efac:LotTender><cbc:ID>TEN-{i}</cbc:ID><efac:TenderLot><cbc:ID>LOT-{i}</cbc:ID></efac:TenderLot><efac:TenderingParty><cbc:ID>PARTY</cbc:ID></efac:TenderingParty></efac:LotTender>'''
    xml += '''<efac:TenderingParty><cbc:ID>PARTY</cbc:ID><efac:Tenderer><cbc:ID>WINNER</cbc:ID></efac:Tenderer></efac:TenderingParty></efac:NoticeResult></ContractAwardNotice>'''
    return ET.fromstring(xml)


def parse(root):
    return parse_eforms(ET.tostring(root))


def notice_result(root):
    return root.find("efac:NoticeResult", NS)


class FederalResultTests(unittest.TestCase):
    def test_explicit_lot_contract_links_preserve_different_counts_and_dates(self):
        units = parse(fixture())["units"]
        self.assertEqual([u["received_tenders"] for u in units], [5, 3])
        self.assertEqual([u["contract_conclusion_date"] for u in units], ["2024-06-01", "2024-06-02"])
        self.assertTrue(all(u["dated_total_supported"] for u in units))

    def test_electronic_subsets_never_replace_missing_total(self):
        root = fixture()
        result = notice_result(root).find("efac:LotResult", NS)
        result.remove(result.findall("efac:ReceivedSubmissionsStatistics", NS)[1])
        unit = parse(root)["units"][0]
        self.assertIsNone(unit["received_tenders"])
        self.assertFalse(unit["dated_total_supported"])

    def test_non_awards_with_counts_are_kept_out_of_awarded_results(self):
        root = fixture()
        notice_result(root).find("efac:LotResult/cbc:TenderResultCode", NS).text = "clos-nw"
        unit = parse(root)["units"][0]
        self.assertEqual(unit["received_tenders"], 5)
        self.assertFalse(unit["award_linkage_supported"])

    def test_winner_selection_date_does_not_fill_contract_date(self):
        root = fixture()
        contract = notice_result(root).find("efac:SettledContract", NS)
        contract.remove(contract.find("cbc:IssueDate", NS))
        unit = parse(root)["units"][0]
        self.assertIsNone(unit["contract_conclusion_date"])
        self.assertEqual(unit["mapped_contracts"][0]["winner_selection_date_source"], "2024-05-01+02:00")

    def test_duplicate_total_statistics_are_not_silently_collapsed(self):
        root = fixture()
        result = notice_result(root).find("efac:LotResult", NS)
        result.append(copy.deepcopy(result.findall("efac:ReceivedSubmissionsStatistics", NS)[1]))
        self.assertIsNone(parse(root)["units"][0]["received_tenders"])

    def test_nonfinite_fractional_zero_and_negative_totals_stay_unknown(self):
        for value in ["NaN", "Infinity", "1.5", "0", "-2"]:
            root = fixture()
            notice_result(root).find("efac:LotResult", NS).findall("efac:ReceivedSubmissionsStatistics", NS)[1].find("efbc:StatisticsNumeric", NS).text = value
            self.assertIsNone(parse(root)["units"][0]["received_tenders"])

    def test_reused_scoped_contract_definition_is_rejected(self):
        root = fixture()
        result = notice_result(root)
        result.append(copy.deepcopy(result.find("efac:SettledContract", NS)))
        with self.assertRaises(ValueError):
            parse(root)

    def test_wrong_contract_tender_link_is_flagged(self):
        root = fixture()
        notice_result(root).find("efac:SettledContract/efac:LotTender/cbc:ID", NS).text = "TEN-2"
        unit = parse(root)["units"][0]
        self.assertIn("contract_result_tender_link_conflict", unit["linkage_flags"])
        self.assertFalse(unit["dated_total_supported"])

    def test_undefined_lot_is_flagged(self):
        root = fixture()
        root.remove(root.find("cac:ProcurementProjectLot", NS))
        unit = parse(root)["units"][0]
        self.assertIn("undefined_or_multiple_result_lots", unit["linkage_flags"])
        self.assertFalse(unit["dated_total_supported"])

    def test_shared_contract_references_with_different_dates_do_not_fill_one_date(self):
        root = fixture()
        result = notice_result(root)
        lot = result.find("efac:LotResult", NS)
        second_ref = copy.deepcopy(lot.find("efac:SettledContract", NS))
        second_ref.find("cbc:ID", NS).text = "CON-3"
        lot.append(second_ref)
        extra = copy.deepcopy(result.find("efac:SettledContract", NS))
        extra.find("cbc:ID", NS).text = "CON-3"
        extra.find("cbc:IssueDate", NS).text = "2024-06-20+02:00"
        result.append(extra)
        self.assertIsNone(parse(root)["units"][0]["contract_conclusion_date"])

    def test_two_explicit_contracts_with_one_shared_result_are_one_observed_result(self):
        root = fixture()
        result = notice_result(root)
        lot = result.find("efac:LotResult", NS)
        ref = copy.deepcopy(lot.find("efac:SettledContract", NS))
        ref.find("cbc:ID", NS).text = "CON-3"
        lot.append(ref)
        extra = copy.deepcopy(result.find("efac:SettledContract", NS))
        extra.find("cbc:ID", NS).text = "CON-3"
        result.append(extra)
        units = parse(root)["units"]
        self.assertEqual(len(units), 2)
        self.assertEqual(len(units[0]["mapped_contracts"]), 2)
        self.assertEqual(units[0]["contract_conclusion_date"], "2024-06-01")
        self.assertTrue(units[0]["analytical_contract_unit_review_required"])

    def test_exact_version_and_xml_identity_both_required(self):
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w") as archive:
            archive.writestr(N1 + "-01.xml", ET.tostring(fixture()))
        with zipfile.ZipFile(data) as archive:
            self.assertEqual(select_xml(archive, {(N1, 2): {}}), {})
            self.assertEqual(len(select_xml(archive, {(N1, 1): {}})), 1)
        self.assertEqual(identity(N1, "01"), identity(N1, 1))

    def test_changed_archive_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            raw = b"changed snapshot"
            Path(folder, "source.zip").write_bytes(raw)
            pin = {"file": "source.zip", "bytes": len(raw), "sha256": hashlib.sha256(b"original snapshot").hexdigest()}
            with self.assertRaises(ValueError):
                verified_archive(folder, pin)

    def test_source_calendar_day_does_not_shift_to_utc(self):
        self.assertEqual(source_date("2024-06-01+02:00"), "2024-06-01")
        self.assertIsNone(source_date("2024-02-30+01:00"))
        self.assertIsNone(source_date("2024"))

    def test_documented_period_parameters_and_dtd_guard(self):
        self.assertIn("pubMonth=2024-06", export_url("2024-06", "csv"))
        self.assertIn("pubDay=2024-06-01", export_url("2024-06-01", "eforms"))
        with self.assertRaises(ValueError):
            export_url("2021-12", "csv")
        with self.assertRaises(ValueError):
            parse_eforms(b'<!DOCTYPE test [<!ENTITY x "test">]><test/>')

    def test_competition_context_preserves_its_phase_and_cannot_be_an_award(self):
        root = fixture()
        root.tag = "{urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2}ContractNotice"
        root.find("cbc:NoticeTypeCode", NS).text = "cn-standard"
        row = parse_competition(ET.tostring(root))
        self.assertEqual(row["notice_issue_date_source"], "2024-06-26+02:00")
        self.assertNotIn("units", row)
        with self.assertRaises(ValueError):
            parse(root)


if __name__ == "__main__":
    unittest.main()
