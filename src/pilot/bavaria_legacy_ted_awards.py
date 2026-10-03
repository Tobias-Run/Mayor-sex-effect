"""Recover scoped legacy award sections from two pinned Mühldorf TED PDFs.

Run after bavaria_candidate_register.py:
    python src/pilot/bavaria_legacy_ted_awards.py [--download]
Do not collapse multi-lot notices or treat supplier addresses as new contracts.
This is a pilot for a specific German legacy layout, not a universal TED parser.
"""
import argparse
import json
import re
import subprocess
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from bavaria_candidate_register import in_interval
from bavaria_evidence_sources import normalized, verified_source

OUT = Path("outputs/bavaria-legacy-ted")
SOURCES = [
    {"id": "ted-108149-2021", "publication_number": "108149-2021",
     "url": "https://ted.europa.eu/de/notice/108149-2021/pdf",
     "sha256": "8cb94303e172550f0822efa4032d1122d1bcb46e1b344da69a21b9f9d6734b34",
     "buyer": "Kreisstadt Mühldorf a. Inn"},
    {"id": "ted-437287-2023", "publication_number": "437287-2023",
     "url": "https://ted.europa.eu/de/notice/437287-2023/pdf",
     "sha256": "61aac29fe613105b472ba63145b185290efdda41dc17318caba5292f5419bdfc",
     "buyer": "Stadt Mühldorf am Inn"},
]


def one(pattern, text):
    matches = re.findall(pattern, text)
    if len(matches) != 1:
        raise ValueError(f"Expected one scoped legacy field: {pattern}")
    return matches[0]


def euro(raw):
    return Decimal(raw.replace(" ", "").replace(".", "").replace(",", "."))


def parse_legacy_awards(text, number, buyer):
    # Remove only the exact notice's page footer, keeping award/lot headings.
    text = re.sub(re.escape(number) + r"\s+Page \d+/\d+", " ", text)
    text = normalized(text)
    if number + " - Ergebnis" not in text or "Bekanntmachung vergebener Aufträge" not in text:
        raise ValueError("Not the expected legacy award notice")
    authority = one(r"Abschnitt I: Öffentlicher Auftraggeber (.*?)Abschnitt II: Gegenstand", text)
    actual_buyer = one(r"Offizielle Bezeichnung: (.*?)(?: Nationale Identifikationsnummer:| Postanschrift:)", authority)
    if actual_buyer != buyer:
        raise ValueError("Legacy document buyer does not match the reviewed municipal alias")
    total = euro(one(r"II\.1\.7\. Gesamtwert der Beschaffung Wert ohne MwSt\.: ([\d ,.]+) EUR", text))
    sections = text.split("Abschnitt V: Auftragsvergabe")[1:]
    if not sections:
        raise ValueError("No explicit award sections")
    awarded = []
    for index, section in enumerate(sections, 1):
        section = section.split("Abschnitt VI: Weitere Angaben")[0]
        if one(r"Ein Auftrag/Los wurde vergeben: (ja|nein)", section) != "ja":
            raise ValueError("Unawarded sections require a separate missing-outcome branch")
        raw_date = one(r"V\.2\.1\. Tag des Vertragsabschlusses (\d{2}/\d{2}/\d{4})", section)
        contract_date = datetime.strptime(raw_date, "%d/%m/%Y").date().isoformat()
        received = int(one(r"V\.2\.2\. Angaben zu den Angeboten Anzahl der eingegangenen Angebote: (\d+)\b", section))
        lot_ids = re.findall(r"Los-Nr\.: (\d+)\b", section)
        if len(lot_ids) > 1:
            raise ValueError("Ambiguous award-lot identity")
        if not lot_ids and "Aufteilung des Auftrags in Lose: nein" not in text:
            raise ValueError("Unnumbered award in a multi-lot notice")
        award_value = euro(one(r"(?<!veranschlagter )Gesamtwert des Auftrags/Loses: ([\d ,.]+) EUR", section))
        awarded.append({"publication_number": number, "award_section": index,
                        "lot_number": lot_ids[0] if lot_ids else None,
                        "unit": "lot" if lot_ids else "undivided_contract",
                        "contract_conclusion_date": contract_date, "received_tenders": received,
                        "award_value_eur": str(award_value),
                        "contract_date_source_quote": "V.2.1. Tag des Vertragsabschlusses " + raw_date,
                        "received_tenders_source_quote": "Anzahl der eingegangenen Angebote: " + str(received),
                        "supplier_blocks_in_award": section.count("V.2.3. Name und Anschrift"),
                        "responsibility_assignment": "unverified"})
    keys = [r["lot_number"] for r in awarded]
    if len(set(keys)) != len(keys) or sum(Decimal(r["award_value_eur"]) for r in awarded) != total:
        raise ValueError("Legacy lot keys or values do not reconcile with the notice")
    return awarded, {"publication_number": number, "buyer": buyer, "award_sections": len(awarded),
                     "notice_value_eur": str(total), "award_values_reconcile": True,
                     "central_purchasing_statement_present": "Der Auftrag wird von einer zentralen Beschaffungsstelle vergeben" in authority,
                     "missing_central_purchasing_statement_is_not_false": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    boundaries = json.loads(Path("outputs/bavaria-candidate-register/tenure-boundaries.json").read_text())
    interval = next(r for r in boundaries if r["ags"] == "09183128")
    notices = {r["publication_number"]: r for r in json.loads(Path("outputs/bavaria-ted-linkage/records.json").read_text())}
    awards, notice_audits = [], []
    for source in SOURCES:
        path = verified_source(source, args.download)
        text = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True,
                              text=True, check=True).stdout
        rows, audit = parse_legacy_awards(text, source["publication_number"], source["buyer"])
        indexed = notices[source["publication_number"]]
        if indexed["ags"] != "09183128" or Decimal(str(indexed["notice_total_value_source"])) != Decimal(audit["notice_value_eur"]):
            raise ValueError("Pinned PDF does not reconcile with the indexed notice")
        audit["source"] = source
        notice_audits.append(audit)
        for row in rows:
            row.update({"ags": "09183128", "source": source,
                        "contract_in_source_bounded_interval": in_interval(row["contract_conclusion_date"], interval["start_inclusive"], interval["end_exclusive"]),
                        "continuous_authority_verified": False})
        awards.extend(rows)
    summary = {"notices_with_full_legacy_awards": len(notice_audits), "award_units": len(awards),
               "award_units_with_explicit_contract_date_and_tender_count": len(awards),
               "contract_dates_within_source_bounded_interval": sum(r["contract_in_source_bounded_interval"] is True for r in awards),
               "notices_with_single_award_unit": sum(r["award_sections"] == 1 for r in notice_audits),
               "notices_with_multiple_award_units": sum(r["award_sections"] > 1 for r in notice_audits),
               "represented_election_events": 1, "responsibility_assignments_verified": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in (("awards", awards), ("notice-audits", notice_audits), ("summary", summary)):
        (OUT / (name + ".json")).write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
