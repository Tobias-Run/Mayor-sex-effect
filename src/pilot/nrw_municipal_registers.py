"""Audit city-specific tenure CSVs found through the federal GovData catalogue.

Year-only boundaries, blank ends and honorary deputy roles remain explicit.
Academic titles are not gender fields. Historical head-role comparability and
renewed election terms require separate checks.
"""
import argparse
import csv
import io
import json
import re
from datetime import date
from pathlib import Path

from bavaria_evidence_sources import html_text
from nrw_extension_evidence import load_sources

OUT = Path("outputs/nrw-municipal-registers")
DATASETS = {
    "dusseldorf-heads-csv": ("05111000", "municipal_head_history", ";", "von", "bis"),
    "dusseldorf-deputies-csv": ("05111000", "honorary_deputy_history", ";", "vom", "bis"),
    "muenster-heads-csv": ("05515000", "historical_list_from_muensterwiki", ",", "Jahr von", "Jahr bis"),
}


def boundary(value):
    value = value.strip()
    if not value:
        return {"source_value": value, "precision": "not_reported", "day": None, "year": None}
    if re.fullmatch(r"\d{4}", value):
        return {"source_value": value, "precision": "year", "day": None, "year": int(value)}
    if re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", value):
        day, month, year = map(int, value.split("."))
        return {"source_value": value, "precision": "day", "day": date(year, month, day).isoformat(), "year": year}
    raise ValueError("Unsupported source date precision")


def parse_register(raw, source_id):
    ags, role, delimiter, start, end = DATASETS[source_id]
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")), delimiter=delimiter)
    expected = (["Jahr von", "Jahr bis", "Oberbürgermeister Name", "Partei", "Wiki-Link"] if delimiter == ","
                else ["Titel", "Vorname", "Name", start, end])
    if reader.fieldnames != expected:
        raise ValueError("Reviewed tenure register schema changed")
    rows = []
    for row in reader:
        if None in row or any(v is None for v in row.values()):
            raise ValueError("Malformed register row")
        name = row.get("Oberbürgermeister Name") or " ".join(row[k].strip() for k in ["Titel", "Vorname", "Name"] if row[k].strip())
        begin, finish = boundary(row[start]), boundary(row[end])
        if not begin["year"] or (finish["year"] is not None and finish["year"] < begin["year"]):
            raise ValueError("Missing or inverted register boundary")
        if finish["day"] is not None and begin["day"] is not None and finish["day"] < begin["day"]:
            raise ValueError("Inverted day boundary")
        rows.append({"ags": ags, "name_source": name, "role_category": role, "source_id": source_id,
                     "start": begin, "end": finish, "vacant_source_row": name == "(vakant)",
                     "blank_end_is_not_verified_continuity": finish["precision"] == "not_reported",
                     "end_inclusion_semantics": "not_assumed", "main_treatment_or_responsibility_assignment": "unverified"})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    sources, paths = load_sources(args.download)
    terms = json.loads(paths["govdata-terms"].read_text())
    mayors = json.loads(paths["govdata-mayors"].read_text())
    if not terms.get("success") or len(terms["result"]["results"]) != terms["result"]["count"] or not mayors.get("success"):
        raise ValueError("Catalogue search snapshot is incomplete or failed")
    mun = [r for r in terms["result"]["results"] if r["id"] == "70bca091-79b8-412c-8641-4aff9ab5f76d"]
    if len(mun) != 1 or "MünsterWiki" not in mun[0]["notes"] or "GNU Free Documentation License 1.2" not in mun[0]["notes"]:
        raise ValueError("Muenster secondary provenance or licence changed")
    heads_text = html_text(paths["dusseldorf-heads-dataset"].read_text())
    deputies_text = html_text(paths["dusseldorf-deputies-dataset"].read_text())
    if "Bis 1994 gab es die sog. Kommunale Doppelspitze" not in heads_text or "ehrenamtliche Stellvertreter" not in deputies_text:
        raise ValueError("Reviewed institutional roles changed")
    for text in [heads_text, deputies_text]:
        if "Datenlizenz Deutschland – Zero – Version 2.0" not in text:
            raise ValueError("Dusseldorf dataset licence changed")
    rows = [r for key in DATASETS for r in parse_register(paths[key].read_bytes(), key)]
    summaries = [{"source_id": key, "ags": DATASETS[key][0], "role_category": DATASETS[key][1],
                  "source_rows": len(selected := [r for r in rows if r["source_id"] == key]),
                  "vacancy_rows": sum(r["vacant_source_row"] for r in selected),
                  "day_precision_starts": sum(r["start"]["precision"] == "day" for r in selected),
                  "year_precision_starts": sum(r["start"]["precision"] == "year" for r in selected),
                  "blank_ends": sum(r["end"]["precision"] == "not_reported" for r in selected),
                  "registry_gender_field": False} for key in DATASETS]
    keller = [r for r in rows if r["source_id"] == "dusseldorf-heads-csv" and r["name_source"] == "Dr. Stephan Keller"]
    geisel = [r for r in rows if r["source_id"] == "dusseldorf-heads-csv" and r["name_source"] == "Thomas Geisel"]
    if len(keller) != 1 or len(geisel) != 1 or keller[0]["start"]["day"] != "2020-11-01" or geisel[0]["end"]["day"] != "2020-10-31":
        raise ValueError("Reviewed 2020 named head transition changed")
    event = next(e for e in json.loads(Path("outputs/nrw-election-register/events.json").read_text()) if e["ags"] == "05111000")
    if not event["votes_and_winner_verified"] or event["winner_name_source"] != "Keller, Dr. Stephan":
        raise ValueError("Tenure identity does not match the official election winner")
    transition = {"ags": event["ags"], "winner_name_source": event["winner_name_source"],
                  "election_date": event["decisive_date"], "source_reported_start": keller[0]["start"]["day"],
                  "predecessor_source_reported_end": geisel[0]["end"]["day"],
                  "days_after_decisive_election": (date.fromisoformat(keller[0]["start"]["day"]) - date.fromisoformat(event["decisive_date"])).days,
                  "gender_measurement": "unverified", "separate_2025_renewal_record": False,
                  "in_extension_close_mixed_acquisition_queue": False, "continuous_procurement_authority_verified": False}
    muenster_text = html_text(paths["muenster-current-mayor"].read_text())
    successor_quote = "Tilman Fuchs ist seit dem 1. November 2025 Oberbürgermeister der Stadt Münster."
    lewes = [r for r in rows if r["source_id"] == "muenster-heads-csv" and r["name_source"] == "Markus Lewe"]
    if successor_quote not in muenster_text or len(lewes) != 1 or lewes[0]["end"]["precision"] != "not_reported":
        raise ValueError("Reviewed blank-end versus current official role discrepancy changed")
    discrepancy = {"ags": "05515000", "csv_last_named_person": "Markus Lewe", "csv_end": None,
                   "official_current_named_person": "Tilman Fuchs", "official_successor_entry": "2025-11-01",
                   "source_quote": successor_quote, "source_id": "muenster-current-mayor",
                   "blank_end_cannot_establish_current_occupant": True,
                   "previous_person_end_imputed": False, "continuous_procurement_authority_verified": False}
    summary = {"govdata_mayor_keyword_results": mayors["result"]["count"],
               "govdata_term_keyword_results": terms["result"]["count"],
               "csv_datasets_audited": len(DATASETS), "municipalities_in_csv_audit": 2,
               "source_rows": len(rows), "vacancy_rows": sum(r["vacant_source_row"] for r in rows),
               "blank_end_current_role_discrepancies": 1,
               "national_person_register_confirmed": False, "new_rdd_eligible_elections": 0,
               "main_treatment_or_responsibility_assignments": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in [("rows", rows), ("dataset-summaries", summaries), ("dusseldorf-2020-transition", transition),
                        ("muenster-current-role-discrepancy", discrepancy), ("summary", summary)]:
        (OUT / f"{name}.json").write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps({"summary": summary, "datasets": summaries, "transition": transition}, indent=2))


if __name__ == "__main__":
    main()
