"""Build a source-round register and independently audit the GERDA Bayern screen.

Run from the repository root after acquiring the pinned source files:
    python src/pilot/bavaria_historical_register.py

Python standard library only. Record-level outputs remain local. Candidate slots
are nominations, not identified people; no gender or actual terms are inferred.
"""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path("data/raw/gerda")
OUT = Path("outputs/bavaria-register")
COMMIT = "030c1fb865ec4e6ef94d5dee2039edde081a0f5d"
SOURCE_URL = ("https://media.githubusercontent.com/media/awiedem/german_election_data/"
              + COMMIT + "/data/mayoral_elections/raw/bayern/20251114_Wahlen_seit_1945.xlsx")
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
MUNICIPAL_TITLES = {
    "Ehrenamtliche(r) 1. Bürgermeister*in", "Berufsmäßige(r) 1. Bürgermeister*in",
    "Oberbürgermeister*in", "Oberbürgermeister*in einer großen Kreisstadt",
}


def number(value):
    if value in (None, "", "NA"):
        return None
    n = Decimal(value)
    if not n.is_finite() or n != n.to_integral_value():
        raise ValueError(f"Expected integer, received {value!r}")
    return int(n)


def excel_date(value):
    n = number(value)
    return (date(1899, 12, 30) + timedelta(days=n)).isoformat() if n is not None else None


def column(index):
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def read_sheet(archive, path, strings):
    result = []
    for row in ET.fromstring(archive.read(path)).findall(".//m:sheetData/m:row", NS):
        values = {}
        for cell in row:
            element = cell.find("m:v", NS)
            value = element.text if element is not None else ""
            if cell.get("t") == "s":
                value = strings[int(value)]
            elif cell.get("t") == "inlineStr":
                value = "".join(cell.find("m:is", NS).itertext())
            values["".join(c for c in cell.get("r") if c.isalpha())] = value
        result.append((int(row.get("r")), values))
    return result


def load_rounds(path):
    with ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        if workbook.find("m:workbookPr", NS).get("date1904", "0") not in ("0", "false"):
            raise ValueError("Unexpected 1904 Excel date system")
        strings = ["".join(e.itertext()) for e in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        sheet = read_sheet(archive, "xl/worksheets/sheet1.xml", strings)
    expected = {"A": "Gemeindeschlüssel", "C": "Tag der Wahl", "E": "Amtstitel",
                "J": "Gültige Stimmen", "K": "Tag des ersten Amtsantritt",
                "N": "gültige Stimmen restliche Bewerber", "AN": "gültige Stimmen Bewerber 14"}
    if any(sheet[0][1].get(k) != v for k, v in expected.items()):
        raise ValueError("Historical workbook schema changed")
    headers = sheet[0][1]
    rows = []
    for row_number, source in sheet[1:]:
        key = source.get("A", "")
        if len(key) != 6 or not key.isdigit():
            raise ValueError(f"Unexpected municipality key at source row {row_number}")
        candidates = []
        parse_issues = []
        def source_number(col):
            try:
                return number(source.get(col))
            except (ValueError, InvalidOperation):
                parse_issues.append({"column": col, "raw_value": source.get(col)})
                return None
        for slot in range(1, 15):
            party_column, votes_column = ("L", "M") if slot == 1 else (column(11 + 2 * slot), column(12 + 2 * slot))
            party, votes = source.get(party_column, ""), source_number(votes_column)
            if party or votes is not None:
                candidates.append({"slot": slot, "nomination": party, "votes": votes})
        valid = source_number("J")
        winner = source_number("M")
        residual = source_number("N")
        fully_counted = all(c["votes"] is not None for c in candidates)
        listed_sum = sum(c["votes"] for c in candidates) if fully_counted else None
        rows.append({"source_row": row_number, "ags": "09" + key, "municipality": source.get("B"),
                     "election_date": excel_date(source.get("C")), "round_label": source.get("D", ""),
                     "office_title": source.get("E", ""), "first_entry_date": excel_date(source.get("K")),
                     "valid_votes": valid, "winner_votes": winner, "residual_votes": residual,
                     "eligible_voters": source_number("F"), "voters": source_number("G"),
                     "invalid_votes": source_number("I"), "candidate_slots": candidates, "parse_issues": parse_issues,
                     "listed_votes_sum": listed_sum,
                     "listed_votes_reconcile": valid is not None and listed_sum == valid,
                     "listed_plus_residual_reconcile": None if residual is None or valid is None or listed_sum is None else listed_sum + residual == valid,
                     "gender_status": "unresolved", "actual_term_status": "unverified"})
    # Resolve only missing office titles from explicit labels on the same unit.
    # No default that could silently mix county heads and municipal mayors.
    by_ags = defaultdict(list)
    for row in rows:
        by_ags[row["ags"]].append(row)
    for row in rows:
        title = row["office_title"]
        if title:
            origin = "source_title"
        else:
            titles = {r["office_title"] for r in by_ags[row["ags"]]
                      if r["office_title"] and abs((date.fromisoformat(r["election_date"]) - date.fromisoformat(row["election_date"])).days) <= 60}
            title = next(iter(titles)) if len(titles) == 1 else ""
            origin = "unique_companion_title_within_60_days" if title else "unresolved"
        row["office_scope"] = "municipality" if title in MUNICIPAL_TITLES else "county" if title == "Landrat/Landrätin" else "unresolved"
        row["office_scope_provenance"] = origin
    return headers, rows


def audit_gerda(rows):
    events = json.loads(Path("outputs/gerda-screen/events.json").read_text())
    selected = [e for e in events if e["state"] == "09" and "2020-01-01" <= e["decisive_date"] <= "2024-12-31"]
    candidates = defaultdict(list)
    with (ROOT / "mayoral_candidates.csv").open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["state"] == "09":
                candidates[(row["ags"], row["election_date"])].append(row)
    source_index = defaultdict(list)
    for row in rows:
        source_index[(row["ags"], row["election_date"])].append(row)
    results = []
    for event in selected:
        source = source_index[(event["ags"], event["decisive_date"])]
        reasons = []
        if len(source) != 1:
            reasons.append("source_round_not_unique")
        else:
            source = source[0]
            vote_field = "candidate_votes_sw" if event["round"] == "runoff" else "candidate_votes_hw"
            pair = [r for r in candidates[(event["ags"], event["first_round_date"])] if number(r[vote_field]) is not None]
            pair_votes = sorted(number(r[vote_field]) for r in pair)
            source_votes = sorted(c["votes"] for c in source["candidate_slots"] if c["votes"] is not None)
            if len(pair) != 2 or len(source["candidate_slots"]) != 2 or pair_votes != source_votes:
                reasons.append("decisive_votes_differ")
            if not source["listed_votes_reconcile"]:
                reasons.append("source_valid_votes_differ")
            if source["office_scope"] != "municipality":
                reasons.append("municipal_office_unverified")
            if event["round"] == "runoff" and source["round_label"] != "Stichwahl":
                reasons.append("unexpected_runoff_label")
            if event["round"] == "first" and source["round_label"] != "erster Wahlgang":
                reasons.append("unexpected_first_round_label")
            source_pairs = sorted((c["nomination"], c["votes"]) for c in source["candidate_slots"] if c["votes"] is not None)
            gerda_pairs = sorted((r["candidate_party"], number(r[vote_field])) for r in pair)
            if source_pairs != gerda_pairs:
                reasons.append("nomination_votes_differ")
        vote_reasons = [r for r in reasons if r != "nomination_votes_differ"]
        results.append({**event, "source_audit_pass": not reasons, "source_vote_audit_pass": not vote_reasons, "audit_reasons": reasons,
                        "source_row": source["source_row"] if isinstance(source, dict) else None,
                        "municipality": source["municipality"] if isinstance(source, dict) else None})
    return results


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    path = ROOT / "bavaria-historical.xlsx"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = json.loads((ROOT / "bavaria-historical-retrieval.json").read_text())
    if digest != manifest["sha256"] or manifest["url"] != SOURCE_URL:
        raise ValueError("Historical source checksum or URL disagrees with pinned manifest")
    candidate_manifest = json.loads((ROOT / "retrieval.json").read_text())
    if hashlib.sha256((ROOT / "mayoral_candidates.csv").read_bytes()).hexdigest() != candidate_manifest["sha256"]:
        raise ValueError("GERDA candidate file changed")
    screen_manifest = json.loads(Path("outputs/gerda-screen/summary.json").read_text())["source"]
    if screen_manifest["sha256"] != candidate_manifest["sha256"]:
        raise ValueError("Re-run structural screen for this candidate snapshot")
    headers, rows = load_rounds(path)
    audited = audit_gerda(rows)
    register = [r for r in rows if "2014-01-01" <= r["election_date"] <= "2024-12-31"]
    summary = {"source": manifest, "source_round_rows": len(rows), "source_headers": headers,
               "earliest_round": min(r["election_date"] for r in rows),
               "latest_round": max(r["election_date"] for r in rows), "windows": {}}
    for start in ("2014-01-01", "2020-01-01"):
        subset = [r for r in register if r["election_date"] >= start]
        municipal = [r for r in subset if r["office_scope"] == "municipality"]
        summary["windows"][start + "_2024-12-31"] = {
            "round_rows": len(subset), "office_scope": dict(Counter(r["office_scope"] for r in subset)),
            "municipal_unique_ags": len({r["ags"] for r in municipal}),
            "municipal_round_labels": dict(Counter(r["round_label"] for r in municipal)),
            "municipal_listed_votes_reconciled": sum(r["listed_votes_reconcile"] for r in municipal),
            "municipal_rounds_with_numeric_parse_issues": sum(bool(r["parse_issues"]) for r in municipal),
            "municipal_listed_plus_residual_status": dict(Counter(str(r["listed_plus_residual_reconcile"]) for r in municipal)),
            "municipal_voters_ballots_disagree": sum(r["voters"] != r["valid_votes"] + r["invalid_votes"] for r in municipal if None not in (r["voters"], r["valid_votes"], r["invalid_votes"])),
            "duplicate_municipal_round_keys": sum(n > 1 for n in Counter((r["ags"], r["election_date"]) for r in municipal).values()),
        }
    summary["gerda_2020_2024_audit"] = {"screened_events": len(audited), "votes_and_structure_passed": sum(r["source_vote_audit_pass"] for r in audited), "including_nomination_text_passed": sum(r["source_audit_pass"] for r in audited),
                                         "failure_reasons": dict(Counter(reason for r in audited for reason in r["audit_reasons"]))}
    (OUT / "rounds.json").write_text(json.dumps(register, indent=2, ensure_ascii=False))
    (OUT / "screen-source-comparison.json").write_text(json.dumps(audited, indent=2, ensure_ascii=False))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    with (OUT / "identity-verification-queue.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["ags", "municipality", "first_round_date", "decisive_date", "round", "absolute_margin_pp", "source_row", "source_audit_pass", "gender_status", "term_status"]
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for row in sorted(audited, key=lambda r: (r["absolute_margin_pp"], r["ags"], r["decisive_date"])):
            writer.writerow({**{key: row[key] for key in fields[:-2]}, "gender_status": "unresolved", "term_status": "unverified"})
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
