"""Extract narrowly scoped historical official-title evidence, not treatment.

Run from repo root: python src/pilot/bavaria_official_title_evidence.py [--download]
Needs Python standard library and Poppler's pdftotext. Pinned page patterns
preserve source dates; titles remain separate from registry-recorded gender.
"""
import argparse
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from urllib.request import urlopen

ROOT = Path("data/raw/bavaria-supplements")
OUT = Path("outputs/bavaria-title-evidence")
JOURNAL_BASE = "https://www.graefelfing.de/fileadmin/user_upload/Rathaus_Buergerservice/Publikationen_Filme_Bilder/Buergerjournal/"
SOURCES = [
    {"id": "graefelfing-2019-2", "url": JOURNAL_BASE + "Buergerjournal-Graefelfing-2019-2.pdf",
     "sha256": "a7459aea3a11622ea8891c7710ecf33f5aa8a1c67601be8cccc2310e803ebe83",
     "ags": "09184120", "candidate": "Wüst, Uta", "source_issue": "02/2019", "pdf_page": 2,
     "pattern": r"Ihre Uta Wüst\s+Erste Bürgermeisterin", "documented_title_presentation": "female"},
    {"id": "graefelfing-2020-1", "url": JOURNAL_BASE + "Buergerjournal-Graefelfing-2020-1.pdf",
     "sha256": "415dda33f77b539924a6cd006ef45f294df29cbfe2530b5e59c9df5877ea147b",
     "ags": "09184120", "candidate": "Köstler, Peter", "source_issue": "01/2020", "pdf_page": 2,
     "pattern": r"Peter Köstler, Erster Bürgermeister", "documented_title_presentation": "male"},
    {"id": "gauting-2020-14", "url": "https://www.gauting.de/fileadmin/gauting-online/Dateien/2_Amtsblatt_PDF/2020/Amtsblatt_14_2020.pdf",
     "sha256": "59b0b32a4ed4ef96ba5aded6d58c9721aea3936c081321e1c17d208dac32e115",
     "ags": "09188120", "candidate": "Kössinger, Dr. Brigitte", "source_issue": "14/2020; 2020-04-01", "pdf_page": 1,
     "pattern": r"Dr\. Brigitte Kössinger.*?Erste Bürgermeisterin", "documented_title_presentation": "female"},
    {"id": "mainburg-2020-21", "url": "https://daten2.verwaltungsportal.de/dateien/seitengenerator/c568c489c994bfcc54bf0c71ac81b1e224346/kurzbericht_2020_21.pdf",
     "sha256": "091b041e6a6d698668333dfb1c540bb1dfa42fb0015cbc906d2bd75d49fc3ae0",
     "ags": "09273147", "candidate": "Fichtner, Helmut", "source_issue": "2020/21; June 2021", "pdf_page": 1,
     "pattern": r"Helmut Fichtner\s+Erster Bürgermeister", "documented_title_presentation": "male"},
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    identities = json.loads(Path("outputs/bavaria-named-reports/recovered-screen-events.json").read_text())
    events = {r["ags"]: r for r in identities}
    evidence = []
    for source in SOURCES:
        path = ROOT / (source["id"] + ".pdf")
        if not path.exists() and args.download:
            with urlopen(source["url"], timeout=45) as response:
                raw = response.read()
            if hashlib.sha256(raw).hexdigest() != source["sha256"]:
                raise ValueError("Downloaded municipal source changed")
            path.write_bytes(raw)
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"Municipal source checksum changed: {path}")
        text_path = OUT / (source["id"] + ".txt")
        subprocess.run(["pdftotext", "-layout", str(path), str(text_path)], check=True)
        pages = unicodedata.normalize("NFC", text_path.read_text()).split("\f")
        page = re.sub(r"\s+", " ", pages[source["pdf_page"] - 1])
        match = re.search(source["pattern"], page)
        if not match:
            raise ValueError(f"Pinned title evidence was not found: {source['id']}")
        event = events[source["ags"]]
        candidates = [r for r in event["candidate_identity"]["candidates"]
                      if r["candidate_name_source"] == source["candidate"]]
        if len(candidates) != 1:
            raise ValueError("Official title cannot be linked to a unique verified election candidate")
        evidence.append({k: v for k, v in source.items() if k != "pattern"} | {
            "election_date": event["decisive_date"], "absolute_margin_pp": event["absolute_margin_pp"],
            "source_quote": match[0], "source_type": "official_gendered_title",
            "candidate_votes": candidates[0]["votes"],
            "registry_gender_field": False, "main_treatment_assignment": "not_promoted",
            "actual_complete_term": "unverified"})
    paired = []
    for ags in sorted({r["ags"] for r in evidence}):
        rows = [r for r in evidence if r["ags"] == ags]
        if len({r["candidate"] for r in rows}) == 2:
            paired.append({"ags": ags, "election_date": events[ags]["decisive_date"],
                           "absolute_margin_pp": events[ags]["absolute_margin_pp"],
                           "both_candidate_official_titles_documented": True,
                           "title_source_issues": [r["source_issue"] for r in rows],
                           "main_treatment_assignment": "measurement_review_required"})
    summary = {"candidate_title_observations": len(evidence), "municipalities": len({r["ags"] for r in evidence}),
               "pairs_with_both_official_titles": paired, "registry_gender_fields_recovered": 0,
               "main_treatment_labels_promoted": 0, "complete_actual_terms_verified": 0}
    (OUT / "evidence.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
