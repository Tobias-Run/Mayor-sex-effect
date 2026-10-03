"""Build the local named-candidate queue and a source-bounded tenure pilot.

Run after bavaria_named_reports.py and bavaria_official_title_evidence.py:
    python src/pilot/bavaria_candidate_register.py [--download]
Person records and source documents remain in ignored directories. No RDD
treatment sample or uninterrupted exercise of procurement authority is inferred.
"""
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

from bavaria_evidence_sources import council_role, html_text, pdf_page, verified_source
from bavaria_historical_register import SOURCE_URL, load_rounds
from bavaria_official_title_evidence import SOURCES

OUT = Path("outputs/bavaria-candidate-register")
WORKBOOK = Path("data/raw/gerda/bavaria-historical.xlsx")
WORKBOOK_SHA = "7ba6aac1381496b3beed2bbd1d0f68209942026b7f9234af8cf1d914c81396a3"
BOUNDARY_SOURCES = [
    {"id": "muehldorf-2026-juli", "url": "https://www.muehldorf.de/files/buch_innstadtinfo_ausgabe_3_juli_2026_.pdf",
     "sha256": "443d4d4240b194f2ab39ef60a4c89d06641b34ace5287e91688d9c2926742a59"},
    {"id": "mainburg-fichtner-2020", "extension": ".html",
     "url": "https://buergerinfo-mainburg.digitalfabrix.de/kp0050.asp?__cwpnr=4&__cselect=0&__kpenr=98&smcmode=32832",
     "sha256": "2bade9dab6e7e7b06996ca9282f23329ec6f27bdc7815b565782a4b60aebd8b4"},
    {"id": "prien-buergermeister", "extension": ".html",
     "url": "https://www.prien.de/de/gemeindepolitik/buergermeister.htm",
     "sha256": "c356385785d29e839277ef4400435085e0dd8a9940eda40ab3f94b8b3f08797b"},
]


def presentation(evidence):
    labels = {row["documented_title_presentation"] for row in evidence}
    if not labels:
        return "missing"
    if len(labels) != 1:
        return "conflict"
    return labels.pop()


def first_appointment_start(first_entry, election_date):
    """A first-ever appointment before this election cannot date its renewed term."""
    if first_entry is None:
        return None
    start, election = date.fromisoformat(first_entry), date.fromisoformat(election_date)
    return first_entry if election <= start and start.year == election.year else None


def in_interval(day, start, end_exclusive):
    if not day or not start or not end_exclusive:
        return None
    return date.fromisoformat(start) <= date.fromisoformat(day) < date.fromisoformat(end_exclusive)


def require_quote(text, pattern):
    match = re.search(pattern, text)
    if not match:
        raise ValueError("Pinned appointment/role evidence was not found")
    return match[0]


def build_candidates(events, title_evidence):
    grouped = defaultdict(list)
    for row in title_evidence:
        grouped[(row["ags"], row["election_date"], row["candidate"])].append(row)
    candidates, pairs = [], []
    used = set()
    for event in events:
        identity = event["candidate_identity"]
        rows = identity["candidates"]
        if not event["source_vote_audit_pass"] or len(rows) != 2:
            raise ValueError("Candidate queue requires audited two-person decisions")
        if sum(r["votes"] for r in rows) != identity["valid_votes"]:
            raise ValueError("Decisive candidate votes do not reconcile")
        pair = []
        for row in rows:
            key = (event["ags"], event["decisive_date"], row["candidate_name_source"])
            if key in used:
                raise ValueError("Duplicate candidate identity in register")
            used.add(key)
            evidence = grouped.get(key, [])
            if any(e["candidate_votes"] != row["votes"] for e in evidence):
                raise ValueError("Title observation votes disagree with identified candidate")
            record = {"ags": key[0], "election_date": key[1], "candidate_name_source": key[2],
                      "municipality": event["municipality"], "votes": row["votes"],
                      "valid_votes": identity["valid_votes"],
                      "winner": row["votes"] == max(r["votes"] for r in rows),
                      "absolute_margin_pp": event["absolute_margin_pp"],
                      "identity_match_method": identity["match_method"],
                      "official_title_presentation": presentation(evidence),
                      "title_evidence": evidence, "registry_gender_verified": False,
                      "main_treatment_assignment": "not_promoted"}
            candidates.append(record)
            pair.append(record)
        labels = {r["official_title_presentation"] for r in pair}
        if labels == {"female", "male"}:
            female, male = (next(r for r in pair if r["official_title_presentation"] == label)
                            for label in ("female", "male"))
            pairs.append({"ags": event["ags"], "municipality": event["municipality"],
                          "election_date": event["decisive_date"],
                          "female_candidate": female["candidate_name_source"],
                          "male_candidate": male["candidate_name_source"],
                          "female_vote_margin_pp": 100 * (female["votes"] - male["votes"]) / identity["valid_votes"],
                          "coding_basis": "documented_official_gendered_titles",
                          "main_treatment_assignment": "not_promoted"})
    if set(grouped) - used:
        raise ValueError("Title evidence does not belong to the named election cohort")
    return candidates, pairs


def build_boundaries(events, download=False):
    sources = {s["id"]: s for s in SOURCES + BOUNDARY_SOURCES}
    if hashlib.sha256(WORKBOOK.read_bytes()).hexdigest() != WORKBOOK_SHA:
        raise ValueError("Historical first-entry source changed")
    _, historical = load_rounds(WORKBOOK)
    starts = {}
    for ags in ("09183128", "09273147", "09187162"):
        matches = [e for e in events if e["ags"] == ags]
        if len(matches) != 1:
            raise ValueError("Boundary source requires one unique election")
        event = matches[0]
        rows = [r for r in historical if r["ags"] == ags and
                r["election_date"] == event["decisive_date"] and r["office_scope"] == "municipality"]
        if len(rows) != 1:
            raise ValueError("First-appointment source is ambiguous")
        row = rows[0]
        identity = event["candidate_identity"]
        if (sorted(r["votes"] for r in row["candidate_slots"]) !=
                sorted(r["votes"] for r in identity["candidates"]) or
                row["valid_votes"] != identity["valid_votes"]):
            raise ValueError("Boundary source vote vector changed")
        start = first_appointment_start(row["first_entry_date"], event["decisive_date"])
        if start is None:
            raise ValueError("First-ever appointment cannot identify this elected term")
        winner = max(identity["candidates"], key=lambda r: r["votes"])
        starts[ags] = {"ags": ags, "municipality": event["municipality"],
                       "candidate": winner["candidate_name_source"], "election_date": event["decisive_date"],
                       "start_inclusive": start, "end_exclusive": None,
                       "workbook_first_entry_source": {"url": SOURCE_URL, "sha256": WORKBOOK_SHA,
                                                      "source_row": row["source_row"], "field": "Tag des ersten Amtsantritt"},
                       "boundary_evidence": [], "continuous_authority_verified": False,
                       "actual_contract_responsibility_verified": False}

    first = sources["muehldorf-2020-juli"]
    page = pdf_page(first, 3, download)
    require_quote(page, r"Name: Michael Hetzl")
    quote = require_quote(page, r"Seit 1\. Mai 2020 Erster Bürgermeister der Kreisstadt")
    record = starts["09183128"]
    record["boundary_evidence"].append({**first, "pdf_page": 3, "claim": "actual_first_appointment", "source_quote": quote})
    successor = sources["muehldorf-2026-juli"]
    page = pdf_page(successor, 6, download)
    require_quote(page, r"Amtsperiode 2026 bis 2032")
    require_quote(page, r"Clau-\s*dia Hungerhuber")  # Specific printed wrap; no generic name rewriting.
    require_quote(page, r"zur Ers-\s*ten Bürgermeisterin der Kreisstadt Mühldorf a\. Inn")
    quote = require_quote(page, r"Sie trat das Amt an der Spitze des Rat-\s*hauses am 1\. Mai an.*?am 7\. Mai im Amt vereidigt")
    record["end_exclusive"] = "2026-05-01"
    record["end_basis"] = "successor_actual_appointment"
    record["successor_oath_date"] = "2026-05-07"
    record["boundary_evidence"].append({**successor, "pdf_page": 6, "claim": "successor_appointment_not_oath", "source_quote": quote})

    source = sources["mainburg-fichtner-2020"]
    raw = verified_source(source, download).read_text()
    row = council_role(raw, "Helmut Fichtner", "2020 - 2026", "Stadtrat der Stadt Mainburg", "1. Bürgermeister")
    end = date.fromisoformat("-".join(reversed(row["Ende"].split("."))))
    record = starts["09273147"]
    record["role_end_inclusive"] = end.isoformat()
    record["end_exclusive"] = (end + timedelta(days=1)).isoformat()
    record["end_basis"] = "historical_first_mayor_role_in_city_council"
    record["boundary_evidence"].append({**source, "claim": "specific_head_role_end", "council_period": "2020 - 2026", "row": row})

    source = sources["prien-buergermeister"]
    text = html_text(verified_source(source, download).read_text())
    # Text content rather than stale image alt text; stop before the deputy's block.
    block = require_quote(text, r"Erster Bürgermeister Markt Prien a\. Chiemsee Andreas Friedrich.*?(?=2\. Bürgermeister)")
    quote = require_quote(block, r"im Amt: Seit 01\.05\.2020")
    starts["09187162"]["boundary_evidence"].append({**source, "claim": "actual_first_appointment", "source_quote": quote})
    return list(starts.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    events = json.loads(Path("outputs/bavaria-named-reports/recovered-screen-events.json").read_text())
    titles = json.loads(Path("outputs/bavaria-title-evidence/evidence.json").read_text())
    candidates, pairs = build_candidates(events, titles)
    boundaries = build_boundaries(events, args.download)
    boundary_by_ags = {r["ags"]: r for r in boundaries}
    notices = json.loads(Path("outputs/bavaria-ted-linkage/records.json").read_text())
    overlap = []
    for notice in notices:
        boundary = boundary_by_ags.get(notice["ags"])
        if not boundary:
            continue
        # Existing pilot normalises a timezone suffix in its source publication date.
        publication_date = date.fromisoformat(notice["publication_date_source"][:10]).isoformat()
        overlap.append({"ags": notice["ags"], "publication_number": notice["publication_number"],
                        "publication_in_source_bounded_interval": in_interval(publication_date, boundary["start_inclusive"], boundary["end_exclusive"]),
                        "contract_in_source_bounded_interval": in_interval(notice["single_contract_conclusion_date"], boundary["start_inclusive"], boundary["end_exclusive"]),
                        "responsibility_assignment": "unverified"})
    summary = {"named_elections": len(events), "candidate_rows": len(candidates),
               "candidate_title_observations": len(titles),
               "candidate_presentation_status": dict(Counter(r["official_title_presentation"] for r in candidates)),
               "pairs_with_documented_mixed_official_titles": len(pairs),
               "named_pairs_without_complete_title_measurement": len(events) - len(pairs),
               "first_appointment_starts_with_source_evidence": len(boundaries),
               "source_bounded_intervals": sum(r["end_exclusive"] is not None for r in boundaries),
               "continuous_authority_verified": 0, "main_treatment_labels_promoted": 0,
               "existing_ted_notices_in_publication_interval": sum(r["publication_in_source_bounded_interval"] is True for r in overlap),
               "existing_ted_notices_with_contract_in_interval": sum(r["contract_in_source_bounded_interval"] is True for r in overlap)}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in (("candidates", candidates), ("mixed-title-pairs", pairs),
                        ("tenure-boundaries", boundaries), ("ted-interval-audit", overlap), ("summary", summary)):
        (OUT / (name + ".json")).write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
