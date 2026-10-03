"""Audit actual GERDA mayoral fields and create dated follow-up leads.

Run from the repo root: python src/pilot/gerda_usability_audit.py [--download]
Standard library only. The optional download acquires the pinned person panel.
2026 labels are never promoted to historical election treatment labels.
"""
import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

COMMIT = "030c1fb865ec4e6ef94d5dee2039edde081a0f5d"
ROOT = Path("data/raw/gerda")
OUT = Path("outputs/gerda-usability")
PANEL_SHA = "2ebbe16114981cd9fdf19e5e6922e5da9d76e70e75b6e86d6f2a2bad3a2fb2aa"
PANEL_URL = ("https://media.githubusercontent.com/media/awiedem/german_election_data/"
             + COMMIT + "/data/mayoral_elections/final/mayor_panel.csv")


def name_key(surname, given):
    """Normalize only case, whitespace, Unicode and explicit academic titles."""
    text = unicodedata.normalize("NFC", surname + " " + given)
    text = re.sub(r"\b(?:Dr\.|Prof\.)\s*", "", text)
    return re.sub(r"\s+", " ", text).strip().casefold()


def checked_csv(path, expected):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f"Source checksum changed: {path}")
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    panel_path = ROOT / "mayor_panel.csv"
    if not panel_path.exists() and args.download:
        with urlopen(PANEL_URL, timeout=45) as response:
            raw = response.read()
        if hashlib.sha256(raw).hexdigest() != PANEL_SHA:
            raise ValueError("Person panel checksum disagrees with pinned source")
        panel_path.write_bytes(raw)
        (ROOT / "mayor-panel-retrieval.json").write_text(json.dumps({
            "url": PANEL_URL, "sha256": PANEL_SHA, "bytes": len(raw),
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat()}, indent=2))
    candidates_manifest = json.loads((ROOT / "retrieval.json").read_text())
    candidates = checked_csv(ROOT / "mayoral_candidates.csv", candidates_manifest["sha256"])
    panel = checked_csv(panel_path, PANEL_SHA)
    by = [r for r in candidates if r["state"] == "09"]
    historical = [r for r in by if "2020" <= r["election_year"] <= "2024"]
    by_panel = [r for r in panel if r["state"] == "09"]
    summary = {"source_commit": COMMIT, "candidate_sha256": candidates_manifest["sha256"],
               "panel_sha256": PANEL_SHA, "candidate_rows_all_states": len(candidates),
               "candidate_state_count": len({r["state"] for r in candidates}),
               "bavaria_candidate_rows": len(by), "bavaria_candidate_names_present": sum(bool(r["candidate_name"]) for r in by),
               "bavaria_gender_labels": dict(Counter(r["candidate_gender"] or "missing" for r in by)),
               "bavaria_gender_years": dict(Counter(r["election_year"] for r in by if r["candidate_gender"])),
               "bavaria_2020_2024_candidate_rows": len(historical),
               "bavaria_2020_2024_names_present": sum(bool(r["candidate_name"]) for r in historical),
               "bavaria_2020_2024_gender_present": sum(bool(r["candidate_gender"]) for r in historical),
               "person_panel_rows_all_states": len(panel), "bavaria_person_elections": len(by_panel),
               "bavaria_person_id_methods": dict(Counter(r["person_id_method"] for r in by_panel)),
               "bavaria_panel_gender_present": sum(bool(r["candidate_gender"]) for r in by_panel),
               "panel_has_exact_term_end_field": "term_end_date" in panel[0]}
    index = defaultdict(list)
    for row in by:
        if row["election_year"] == "2026" and row["candidate_gender_source"] == "raw":
            index[(row["ags"], name_key(row["candidate_last_name"], row["candidate_first_name"]))].append(row)
    identity_path = Path("outputs/bavaria-named-reports/recovered-screen-events.json")
    events = json.loads(identity_path.read_text())
    leads = []
    for event in events:
        for candidate in event["candidate_identity"]["candidates"]:
            surname, given = candidate["candidate_name_source"].split(",", 1)
            hits = index.get((event["ags"], name_key(surname, given)), [])
            if len(hits) != 1:
                continue
            hit = hits[0]
            leads.append({"ags": event["ags"], "election_date": event["decisive_date"],
                "candidate_name_source": candidate["candidate_name_source"], "votes": candidate["votes"],
                "source_gender_label": hit["candidate_gender"], "source_gender_year": 2026,
                "source_gender_provenance": hit["candidate_gender_source"],
                "historical_gender_status": "dated_identity_and_gender_review_required",
                "match_method": "unique_same_ags_exact_name_after_titles_case_whitespace_unicode",
                "absolute_margin_pp": event["absolute_margin_pp"]})
    summary["dated_2026_gender_followup"] = {"candidate_observations": len(leads),
        "elections": len({(r["ags"], r["election_date"]) for r in leads}),
        "within_5pp": sum(r["absolute_margin_pp"] <= 5 for r in leads),
        "labels": dict(Counter(r["source_gender_label"] for r in leads)),
        "historic_treatment_labels_promoted": 0}
    summary["named_election_identity_sha256"] = hashlib.sha256(identity_path.read_bytes()).hexdigest()
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    (OUT / "gender-followup.json").write_text(json.dumps(leads, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
