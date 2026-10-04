"""Acquire public German procurement exports and parse scoped eForms results.

The Bekanntmachungsservice is an independent German open-data publisher.
Never use these functions to fetch protected TED web documents. This module
preserves typed result/contract/lot relationships and does not assign treatment.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import UUID
from xml.etree import ElementTree as ET

URL = "https://www.oeffentlichevergabe.de/api/notice-exports"
NS = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def identity(identifier, version):
    """Normalize version padding, while retaining notice identity and version."""
    if not re.fullmatch(r"[0-9]+", str(version)) or int(version) < 1:
        raise ValueError("Missing or invalid notice version")
    return str(UUID(identifier)), int(version)


def export_url(period, format_name):
    if format_name not in {"csv", "eforms", "ocds"}:
        raise ValueError("Unsupported export format")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", period):
        parsed = date.fromisoformat(period)
        if parsed < date(2022, 12, 1):
            raise ValueError("Documented archive begins 1 December 2022")
        parameter = "pubDay"
    elif re.fullmatch(r"\d{4}-\d{2}", period):
        parsed = date.fromisoformat(period + "-01")
        if parsed < date(2022, 12, 1):
            raise ValueError("Documented archive begins December 2022")
        parameter = "pubMonth"
    else:
        raise ValueError("Expected YYYY-MM or YYYY-MM-DD")
    return URL + "?" + urlencode({parameter: period, "format": format_name + ".zip"})


def acquire(period, format_name, root):
    """Store a bounded, successful ZIP response; never overwrite a snapshot."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    filename = period + "-" + format_name + ".zip"
    path = root / filename
    metadata = path.with_suffix(".json")
    if path.exists() or metadata.exists():
        raise FileExistsError("Review existing source before a new acquisition")
    url = export_url(period, format_name)
    with urlopen(Request(url, headers={"User-Agent": "Research source audit"}), timeout=60) as response:
        if response.status != 200 or response.headers.get("x-amzn-waf-action") == "challenge":
            raise ValueError("Non-success or access-protected export")
        raw = response.read(100 * 1024 * 1024 + 1)
        if len(raw) > 100 * 1024 * 1024:
            raise ValueError("Export exceeds the reviewed 100 MiB bound")
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError("Duplicate archive member names")
            if sum(info.file_size for info in archive.infolist()) > 1024 * 1024 * 1024:
                raise ValueError("Uncompressed archive exceeds the reviewed 1 GiB bound")
            if archive.testzip() is not None:
                raise ValueError("ZIP checksum failure")
        meta = {"url": url, "final_url": response.url, "http_status": response.status,
                "content_type": response.headers.get("Content-Type"), "period": period,
                "format": format_name, "file": filename, "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(), "archive_member_count": len(names),
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat()}
    path.write_bytes(raw)
    metadata.write_text(json.dumps(meta, indent=2))
    return meta


def verified_archive(root, pin):
    path = Path(root) / pin["file"]
    if path.name != pin["file"]:
        raise ValueError("Source pin must contain a filename, not a path")
    raw = path.read_bytes()
    if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
        raise ValueError("Source archive changed: " + pin["file"])
    return zipfile.ZipFile(io.BytesIO(raw))


def csv_rows(archive, table):
    with archive.open(table) as source:
        reader = csv.DictReader(io.TextIOWrapper(source, encoding="utf-8-sig", newline=""))
        if not {"noticeIdentifier", "noticeVersion"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV notice foreign keys are missing")
        yield from reader


def text_at(element, path):
    return (element.findtext(path, default="", namespaces=NS) or "").strip()


def ids_at(element, path):
    return [e.text.strip() for e in element.findall(path, NS) if e.text and e.text.strip()]


def definitions(parent, path):
    result = {}
    for item in parent.findall(path, NS):
        key = text_at(item, "cbc:ID")
        if not key or key in result:
            raise ValueError("Missing or duplicate scoped definition: " + path)
        result[key] = item
    return result


def source_date(value):
    """Retain the source's calendar day; timezone conversion can change it."""
    if not value or not re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:Z|[+-]\d{2}:\d{2})?", value):
        return None
    try:
        return date.fromisoformat(value[:10]).isoformat()
    except ValueError:
        return None


def positive_count(value):
    try:
        number = Decimal(value)
        if number.is_finite() and number > 0 and number == number.to_integral_value():
            return int(number)
    except (InvalidOperation, ValueError, TypeError):
        pass
    return None


def safe_xml(raw):
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("DTD/entity-bearing source is outside the reviewed XML format")
    return ET.fromstring(raw)


def organization_buyers(root):
    organisations = {}
    for company in root.findall(".//efac:Organizations/efac:Organization/efac:Company", NS):
        key = text_at(company, "cac:PartyIdentification/cbc:ID")
        if not key or key in organisations:
            raise ValueError("Missing or duplicate organization identifier")
        organisations[key] = text_at(company, "cac:PartyName/cbc:Name")
    buyer_refs = ids_at(root, "cac:ContractingParty/cac:Party/cac:PartyIdentification/cbc:ID")
    return [{"organization_id": ref, "name": organisations.get(ref)} for ref in buyer_refs], organisations


def parse_competition(raw):
    root = safe_xml(raw)
    if root.tag != "{urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2}ContractNotice" or text_at(root, "cbc:NoticeTypeCode") != "cn-standard":
        raise ValueError("Expected an original cn-standard UBL ContractNotice")
    notice_id, version = identity(text_at(root, "cbc:ID"), text_at(root, "cbc:VersionID"))
    buyers, _ = organization_buyers(root)
    return {"notice_identifier": notice_id, "notice_version": version,
            "procedure_identifier": text_at(root, "cbc:ContractFolderID"),
            "notice_issue_date_source": text_at(root, "cbc:IssueDate"),
            "requested_publication_date_source": text_at(root, "cbc:RequestedPublicationDate"),
            "changed_notice_reference": text_at(root, ".//efac:Changes/efbc:ChangedNoticeIdentifier"),
            "buyers": buyers}


def parse_eforms(raw):
    root = safe_xml(raw)
    expected_root = "{urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2}ContractAwardNotice"
    if root.tag != expected_root:
        raise ValueError("Expected an original UBL ContractAwardNotice")
    notice_id, version = identity(text_at(root, "cbc:ID"), text_at(root, "cbc:VersionID"))
    if text_at(root, "cbc:NoticeTypeCode") != "can-standard":
        raise ValueError("Notice is outside the fixed can-standard acquisition")
    result_nodes = root.findall(".//efac:NoticeResult", NS)
    if len(result_nodes) != 1:
        raise ValueError("Expected one explicitly scoped NoticeResult")
    result = result_nodes[0]
    contracts = definitions(result, "efac:SettledContract")
    tenders = definitions(result, "efac:LotTender")
    parties = definitions(result, "efac:TenderingParty")
    lot_results = definitions(result, "efac:LotResult")
    defined_lots = ids_at(root, "cac:ProcurementProjectLot/cbc:ID")
    buyers, organisations = organization_buyers(root)
    units = []
    for result_id, lot_result in lot_results.items():
        lot_ids = ids_at(lot_result, "efac:TenderLot/cbc:ID")
        status = text_at(lot_result, "cbc:TenderResultCode")
        statistics = [{"type_source": text_at(s, "efbc:StatisticsCode"),
                       "value_source": text_at(s, "efbc:StatisticsNumeric")}
                      for s in lot_result.findall("efac:ReceivedSubmissionsStatistics", NS)]
        totals = [s for s in statistics if s["type_source"] == "tenders"]
        count = positive_count(totals[0]["value_source"]) if len(totals) == 1 else None
        contract_refs = ids_at(lot_result, "efac:SettledContract/cbc:ID")
        tender_refs = ids_at(lot_result, "efac:LotTender/cbc:ID")
        flags = []
        if len(lot_ids) != 1 or lot_ids[0] not in defined_lots:
            flags.append("undefined_or_multiple_result_lots")
        if not contract_refs or len(contract_refs) != len(set(contract_refs)):
            flags.append("missing_or_duplicate_contract_reference")
        if not tender_refs or len(tender_refs) != len(set(tender_refs)):
            flags.append("missing_or_duplicate_tender_reference")
        mapped_contracts = []
        for contract_id in contract_refs:
            contract = contracts.get(contract_id)
            if contract is None:
                flags.append("undefined_contract_reference")
                continue
            contract_tenders = ids_at(contract, "efac:LotTender/cbc:ID")
            if not contract_tenders or not set(contract_tenders).issubset(tender_refs):
                flags.append("contract_result_tender_link_conflict")
            raw_date = text_at(contract, "cbc:IssueDate")
            mapped_contracts.append({"contract_id": contract_id, "tender_ids": contract_tenders,
                                     "contract_date_source": raw_date,
                                     "contract_conclusion_date": source_date(raw_date),
                                     "winner_selection_date_source": text_at(contract, "cbc:AwardDate")})
        winner_organizations = []
        for tender_id in tender_refs:
            tender = tenders.get(tender_id)
            if tender is None:
                flags.append("undefined_tender_reference")
                continue
            if ids_at(tender, "efac:TenderLot/cbc:ID") != lot_ids:
                flags.append("tender_result_lot_conflict")
            party_refs = ids_at(tender, "efac:TenderingParty/cbc:ID")
            if not party_refs:
                flags.append("missing_tendering_party")
            for party_id in party_refs:
                party = parties.get(party_id)
                refs = ids_at(party, "efac:Tenderer/cbc:ID") if party is not None else []
                if not refs or any(ref not in organisations for ref in refs):
                    flags.append("unresolved_winner_organization")
                winner_organizations.extend(refs)
        dates = [c["contract_conclusion_date"] for c in mapped_contracts]
        contract_date = dates[0] if dates and all(d is not None and d == dates[0] for d in dates) else None
        supported = status == "selec-w" and not flags
        units.append({"result_id": result_id, "lot_ids": lot_ids, "result_status": status,
                      "statistics_source": statistics, "received_tenders": count,
                      "total_count_status": "explicit_total" if count is not None else "missing_duplicate_or_invalid_total",
                      "mapped_contracts": mapped_contracts, "contract_conclusion_date": contract_date,
                      "multiple_contract_result": len(contract_refs) > 1,
                      "analytical_contract_unit_review_required": len(contract_refs) > 1,
                      "winner_organization_ids": sorted(set(winner_organizations)),
                      "linkage_flags": sorted(set(flags)), "award_linkage_supported": supported,
                      "dated_total_supported": supported and count is not None and contract_date is not None,
                      "main_treatment_assignment": "unverified"})
    return {"notice_identifier": notice_id, "notice_version": version,
            "procedure_identifier": text_at(root, "cbc:ContractFolderID"),
            "customization_id": text_at(root, "cbc:CustomizationID"),
            "notice_issue_date_source": text_at(root, "cbc:IssueDate"),
            "requested_publication_date_source": text_at(root, "cbc:RequestedPublicationDate"),
            "changed_notice_reference": text_at(root, ".//efac:Changes/efbc:ChangedNoticeIdentifier"),
            "buyers": buyers, "units": units}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("periods", nargs="+", help="Months YYYY-MM or days YYYY-MM-DD")
    parser.add_argument("--format", choices=["csv", "eforms", "ocds"], default="csv")
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw/federal-procurement"))
    args = parser.parse_args()
    for period in args.periods:
        meta = acquire(period, args.format, args.raw_root)
        print(json.dumps({k: meta[k] for k in ["file", "bytes", "sha256", "archive_member_count"]}), flush=True)


if __name__ == "__main__":
    main()
