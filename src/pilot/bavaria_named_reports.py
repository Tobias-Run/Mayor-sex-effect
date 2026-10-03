"""Recover named candidate rounds from pinned official Bavarian report PDFs.

Run from repo root: python src/pilot/bavaria_named_reports.py [--download]
Requires Python's standard library and Poppler's pdftotext command. Source data
and person-level outputs stay local. No gender or actual terms are inferred.
"""
import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

from bavaria_historical_register import load_rounds

ROOT = Path("data/raw/bavaria-reports")
OUT = Path("outputs/bavaria-named-reports")
BASE = "https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/"
REPORTS = [
    {"id": "bay2020-first", "date": "2020-03-15", "round": "first", "name_format": "comma",
     "remote": "BYHeft_derivate_00006228/B7331C%20202051.pdf",
     "sha256": "e420aa1ecc2eeb43a13df8d58445569e970ab4b8fa550e42ae9417a03ff57f24"},
    {"id": "bay2020-runoff", "date": "2020-03-29", "round": "runoff", "name_format": "comma",
     "remote": "BYHeft_derivate_00006229/B7332C%20202051.pdf",
     "sha256": "d010e1c5c862f0c0f9d7cc5ec145c3579854486113e38b5a86a73f1f4b83f962"},
    {"id": "bay2014-first", "date": "2014-03-16", "round": "first", "name_format": "space",
     "remote": "BYHeft_derivate_00005465/B7331C%20201451.pdf",
     "sha256": "f2ad501b3e0d1dbcbb235443fdaab382d8e132069f75acbee1d5cb0593e89073"},
    {"id": "bay2014-runoff", "date": "2014-03-30", "round": "runoff", "name_format": "space",
     "remote": "BYHeft_derivate_00003930/B7332C%20201451.pdf",
     "sha256": "6dd15c90ddfa54b08f13cf3009195a0f75b6a681aa05b3b76de193185d9ead6d"},
    {"id": "bay2008-runoff", "date": "2008-03-16", "round": "runoff", "name_format": "space",
     "remote": "BYHeft_derivate_00000669/B7332C%20200851.pdf",
     "sha256": "1a0fdac44662179c065b2fa64091c288190627939c727b54800b78a92dddf377"},
]
HEADER = re.compile(r"^\s*(?:Noch:\s*)?(\d{3})\s+(\d{3})\s+(.+?)\s*\((?:Lkr |Krfr\. St)")
CANDIDATE = re.compile(r"^\s*(.+?)\s{2,}(?:(Gewählt|Stichwahl)\s+)?(\d[\d ]*|X|–|-)\s+(\d+(?:,\d+)?|\.|X)(?:\s+(\d+(?:,\d+)?|\.|X))?\s*$")
STATISTICAL_LABELS = ("Stimmberechtigte", "Wähler", "Ungültige", "Zusammen", "Gültige", "Bezeichnung",
                      "Statistische", "Kommunalwahlen", "Vorläufige", "Nachweisung", "Sonstige")


def parse_report(text, metadata):
    """Read only the municipal candidate chapter; X entries are prior candidates."""
    rows = []
    ags = None
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if ags and re.search(r"(?:5\. Wahl|6\. Stichwahl) der Landräte", line):
            break
        header = HEADER.match(line)
        if header:
            ags = "09" + header[1] + header[2]
        match = CANDIDATE.match(line)
        if not match or ags is None:
            continue
        name = match[1].strip()
        if metadata["name_format"] == "comma" and "," not in name:
            continue
        if name.startswith(STATISTICAL_LABELS) or len(name.split()) < 2 or any(ch.isdigit() for ch in name):
            continue
        if any(word in name for word in ("Gewählt", "Stichwahl")):
            raise ValueError(f"Status marker leaked into candidate name: {name}")
        party = next((line.strip() for line in lines[index + 1:index + 5] if line.strip()), "")
        rows.append({"ags": ags, "candidate_name_source": name, "name_format": metadata["name_format"],
                     "election_date": metadata["date"], "round": metadata["round"],
                     "nomination_source": party, "declared_status": match[2] or "",
                     "votes": int(match[3].replace(" ", "")) if match[3][0].isdigit() else None,
                     "text_line": index + 1, "source_report": metadata["id"],
                     "gender_status": "unverified", "actual_term_status": "unverified"})
    return rows


def match_round(ags, report_rows, source_rows):
    if len(source_rows) != 1:
        return None, "historical_round_missing_or_duplicated"
    source = source_rows[0]
    if source["office_scope"] != "municipality":
        return None, "municipal_scope_unresolved"
    if not source["listed_votes_reconcile"] or source["parse_issues"]:
        return None, "historical_candidate_votes_incomplete"
    current = [row for row in report_rows if row["votes"] is not None]
    votes = [row["votes"] for row in current]
    actual = [row["votes"] for row in source["candidate_slots"]]
    if sorted(votes) != sorted(actual):
        return None, "preliminary_final_vote_vector_differs"
    if len(set(votes)) != len(votes):
        return None, "equal_candidate_votes_need_identity_review"
    # A full unique vote vector identifies slots without guessed party aliases.
    by_vote = {row["votes"]: row for row in source["candidate_slots"]}
    linked = [{**row, "historical_source_slot": by_vote[row["votes"]]["slot"],
               "historical_nomination": by_vote[row["votes"]]["nomination"]} for row in current]
    return {"ags": ags, "election_date": source["election_date"], "municipality": source["municipality"],
            "historical_source_row": source["source_row"], "valid_votes": source["valid_votes"],
            "match_method": "complete_unique_exact_vote_vector", "candidates": linked}, None


def main():
    arguments = argparse.ArgumentParser()
    arguments.add_argument("--download", action="store_true")
    args = arguments.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    _, historical = load_rounds(Path("data/raw/gerda/bavaria-historical.xlsx"))
    manifest = json.loads(Path("data/raw/gerda/bavaria-historical-retrieval.json").read_text())
    if hashlib.sha256(Path("data/raw/gerda/bavaria-historical.xlsx").read_bytes()).hexdigest() != manifest["sha256"]:
        raise ValueError("Historical workbook changed")
    source_index = defaultdict(list)
    for row in historical:
        source_index[(row["ags"], row["election_date"])].append(row)
    summary = {"historical_source_sha256": manifest["sha256"], "reports": []}
    all_candidates, all_matches, review = [], [], []
    for metadata in REPORTS:
        path = ROOT / (metadata["id"] + ".pdf")
        if not path.exists() and args.download:
            with urlopen(BASE + metadata["remote"], timeout=45) as response:
                data = response.read()
            if hashlib.sha256(data).hexdigest() != metadata["sha256"]:
                raise ValueError(f"Download checksum mismatch: {path}")
            path.write_bytes(data)
        if not path.exists():
            raise FileNotFoundError(f"{path}: use --download to acquire pinned reports")
        if hashlib.sha256(path.read_bytes()).hexdigest() != metadata["sha256"]:
            raise ValueError(f"Source checksum mismatch: {path}")
        text_path = OUT / (metadata["id"] + ".txt")
        subprocess.run(["pdftotext", "-layout", str(path), str(text_path)], check=True)
        candidates = parse_report(text_path.read_text(), metadata)
        groups = defaultdict(list)
        for row in candidates:
            groups[row["ags"]].append(row)
        reasons, matched = Counter(), []
        for ags, rows in groups.items():
            result, reason = match_round(ags, rows, source_index[(ags, metadata["date"])])
            if result:
                matched.append(result)
            else:
                reasons[reason] += 1
                review.append({"report": metadata["id"], "ags": ags, "reason": reason})
        summary["reports"].append({**metadata, "url": BASE + metadata["remote"],
                                   "municipal_report_units": len(groups),
                                   "named_current_candidate_rows": sum(row["votes"] is not None for row in candidates),
                                   "exact_full_round_matches": len(matched), "review_reasons": dict(reasons)})
        all_candidates.extend(candidates); all_matches.extend(matched)
    event_screen = json.loads(Path("outputs/bavaria-register/screen-source-comparison.json").read_text())
    selected = {(e["ags"], e["decisive_date"]): e for e in event_screen if e["first_round_date"] == "2020-03-15"}
    recovered = [{**selected[(r["ags"], r["election_date"])], "candidate_identity": r}
                 for r in all_matches if (r["ags"], r["election_date"]) in selected]
    summary["screen_2020_recovered"] = {"events": len(recovered),
                                        "within_2pp": sum(e["absolute_margin_pp"] <= 2 for e in recovered),
                                        "within_5pp": sum(e["absolute_margin_pp"] <= 5 for e in recovered),
                                        "gender_and_actual_terms_verified": False}
    summary["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    for filename, data in [("summary.json", summary), ("candidates.json", all_candidates),
                           ("matched-rounds.json", all_matches), ("recovered-screen-events.json", recovered),
                           ("review-queue.json", review)]:
        (OUT / filename).write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
