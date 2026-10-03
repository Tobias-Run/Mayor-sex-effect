"""Inspect three pinned NRW legacy PDFs, preserving a cancelled result notice.

Run after nrw_ted_linkage.py: python src/pilot/nrw_legacy_ted_awards.py [--download]
No actual office interval or mayoral treatment responsibility is assigned.
"""
import argparse
import json
import re
import subprocess
from decimal import Decimal
from pathlib import Path

from bavaria_evidence_sources import normalized, verified_source
from bavaria_legacy_ted_awards import one, parse_legacy_awards

ROOT = Path("data/raw/nrw-evidence")
OUT = Path("outputs/nrw-legacy-ted")
SOURCES = [
    {"id": "ted-iserlohn-21732-2021", "publication_number": "21732-2021", "ags": "05962024",
     "url": "https://ted.europa.eu/de/notice/21732-2021/pdf", "buyer": "Stadt Iserlohn",
     "sha256": "dd3871e6a2484171e98d10e48c38ae42e3ed9fe5c42728a0a7a110fb7db6ad51"},
    {"id": "ted-geilen-510704-2021", "publication_number": "510704-2021", "ags": "05370012",
     "url": "https://ted.europa.eu/de/notice/510704-2021/pdf", "buyer": "Stadt Geilenkirchen -Die Bürgermeisterin-",
     "sha256": "da1ee68494c1c6d58f677f2f94a030ebf00d804297cde5b42c917add896a5298"},
    {"id": "ted-velbert-565529-2023", "publication_number": "565529-2023", "ags": "05158032",
     "url": "https://ted.europa.eu/de/notice/565529-2023/pdf", "buyer": "Stadt Velbert",
     "sha256": "5d748140931f88acc38f016b9bfc5d23914c8b4389979bec443de9d4cc28a3a1"},
]


def result_status(text, number, buyer):
    text = re.sub(re.escape(number) + r"\s+Page \d+/\d+", " ", text)
    text = normalized(text)
    if number + " - Ergebnis" not in text:
        raise ValueError("Unexpected legacy notice identity")
    authority = one(r"Abschnitt I: Öffentlicher Auftraggeber (.*?)Abschnitt II: Gegenstand", text)
    actual_buyer = one(r"Offizielle Bezeichnung: (.*?)(?: Nationale Identifikationsnummer:| Postanschrift:)", authority)
    if actual_buyer != buyer:
        raise ValueError("Buyer identity changed")
    sections = text.split("Abschnitt V: Auftragsvergabe")[1:]
    if not sections:
        raise ValueError("No full-text result section")
    statuses = [one(r"Ein Auftrag/Los wurde vergeben: (ja|nein)", s.split("Abschnitt VI: Weitere Angaben")[0]) for s in sections]
    if all(s == "nein" for s in statuses):
        return "not_awarded"
    if all(s == "ja" for s in statuses):
        return "awarded"
    raise ValueError("Mixed awarded and unawarded sections need separate lot-level handling")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    indexed = {r["publication_number"]: r for r in json.loads(Path("outputs/nrw-ted-linkage/records.json").read_text())}
    audits, awards = [], []
    for source in SOURCES:
        path = verified_source(source, args.download, ROOT)
        text = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=True).stdout
        notice = indexed[source["publication_number"]]
        if notice["ags"] != source["ags"] or notice["buyer_name"] != source["buyer"]:
            raise ValueError("Full PDF does not match a retained municipal notice")
        status = result_status(text, source["publication_number"], source["buyer"])
        if status == "not_awarded":
            audits.append({"source": source, "fulltext_result_status": status, "award_units": 0,
                           "awarded_tender_count": None, "contract_conclusion_date": None,
                           "source_quote": "Ein Auftrag/Los wurde vergeben: nein"})
            continue
        rows, audit = parse_legacy_awards(text, source["publication_number"], source["buyer"])
        if Decimal(str(notice["source_fields"]["total-value"])) != Decimal(audit["notice_value_eur"]):
            raise ValueError("Legacy award values differ from indexed notice total")
        audit.update({"source": source, "fulltext_result_status": status})
        audits.append(audit)
        for row in rows:
            row.update({"ags": source["ags"], "source": source, "actual_term_assignment": "unverified", "gender_measurement": "unverified"})
        awards.extend(rows)
    summary = {"full_legacy_notices_reviewed": len(audits),
               "notices_with_awarded_units": sum(a["fulltext_result_status"] == "awarded" for a in audits),
               "notices_explicitly_not_awarded": sum(a["fulltext_result_status"] == "not_awarded" for a in audits),
               "awarded_units_with_contract_date_and_tender_count": len(awards),
               "actual_term_or_responsibility_assignments": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in (("notice-audits", audits), ("awards", awards), ("summary", summary)):
        (OUT / (name + ".json")).write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
