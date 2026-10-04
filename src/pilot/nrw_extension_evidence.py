"""Verify extension primary evidence without imputing historical gender or entry.

Public presentation retains observation timing. A current winner can have been
the 2020 loser; neither that title nor a successor's entry establishes continuous
authority for the previous winner.
"""
import argparse
import csv
import json
from pathlib import Path

from bavaria_evidence_sources import html_text, pdf_page, verified_source

ROOT = Path("data/raw/nrw-extension-evidence")
MANIFEST = Path("docs/feasibility/nrw-extension-evidence-source-manifest.csv")
OUT = Path("outputs/nrw-extension-evidence")


def load_sources(download=False):
    with MANIFEST.open(newline="") as handle:
        sources = {s["id"]: s for s in csv.DictReader(handle)}
    paths = {}
    for key, source in sources.items():
        paths[key] = verified_source(source, download, ROOT)
        if paths[key].stat().st_size != int(source["bytes"]):
            raise ValueError("Pinned primary evidence byte count changed")
    return sources, paths


def unna_presentations(raw):
    text = html_text(raw)
    quotes = ["Die SPD bedankt sich bei ihrer Kandidatin Katja Schuon",
              "dem CDU-Mann Wigant mit 221 Stimmen Vorsprung"]
    if any(q not in text for q in quotes) or "28. September 2020" not in text or "Dirk Wigant" not in text:
        raise ValueError("Dated party statement or full candidate identities changed")
    return [{"ags": "05978036", "candidate_name_source": name, "presentation": gender,
             "observation_date": "2020-09-28", "date_precision": "day", "source_quote": quote,
             "evidence_kind": "dated_party_authored_candidate_presentation", "source_id": "unna-spd-0",
             "official_municipal_source": False, "registry_gender_field": False,
             "main_treatment_assignment": "unverified"}
            for name, gender, quote in zip(["Schuon, Katja", "Wigant, Dirk"], ["female", "male"], quotes)]


def reuscher_presentation(payload):
    rows = payload.get("results", [])
    if payload.get("result_count") != 1 or len(rows) != 1 or rows[0].get("Vorname") != "Katrin" or rows[0].get("Name") != "Reuscher" or rows[0].get("Anrede") != "Frau":
        raise ValueError("Named public RIS presentation changed")
    return {"ags": "05570040", "candidate_name_source": "Reuscher, Katrin", "presentation": "female",
            "observation_date": None, "date_precision": "retrieval_only", "source_quote": "Anrede=Frau; Vorname=Katrin; Name=Reuscher",
            "evidence_kind": "current_official_public_person_presentation", "source_id": "sendenhorst-reuscher",
            "official_municipal_source": True, "registry_gender_field": False, "main_treatment_assignment": "unverified"}


def hopp_presentation(raw):
    quote = "Anrede: Herr Name: Christoph Hopp"
    if quote not in html_text(raw):
        raise ValueError("Named current official presentation changed")
    return {"ags": "05166032", "candidate_name_source": "Hopp, Christoph", "presentation": "male",
            "observation_date": None, "date_precision": "retrieval_only", "source_quote": quote,
            "evidence_kind": "current_official_public_person_presentation", "source_id": "viersen-hopp",
            "official_municipal_source": True, "registry_gender_field": False, "main_treatment_assignment": "unverified"}


def hopp_entry(raw):
    quote = "Seit dem 1. November 2025 ist Christoph Hopp Bürgermeister der Stadt Viersen."
    if quote not in html_text(raw):
        raise ValueError("Named successor entry statement changed")
    return {"ags": "05166032", "candidate_name_source": "Hopp, Christoph", "reported_entry_date": "2025-11-01",
            "source_quote": quote, "source_id": "viersen-mayor", "evidence_kind": "official_retrospective_successor_entry",
            "certifies_previous_winner_continuous_term": False, "procurement_responsibility_assignment": "unverified"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    sources, paths = load_sources(args.download)
    added = unna_presentations(paths["unna-spd-0"].read_text())
    added += [reuscher_presentation(json.loads(paths["sendenhorst-reuscher"].read_text())),
              hopp_presentation(paths["viersen-hopp"].read_text())]
    page = pdf_page(sources["viersen-january-2024"], 3, root=ROOT)
    quote = "Ihre Bürgermeisterin Sabine Anemüller"
    if quote not in page or "Die nächste Ausgabe erscheint am 28. Januar 2024" not in page:
        raise ValueError("Named dated official publication changed")
    added.append({"ags": "05166032", "candidate_name_source": "Anemüller, Sabine", "presentation": "female",
                  "observation_date": "2024-01", "date_precision": "month", "source_quote": quote,
                  "pdf_page": 3, "source_id": "viersen-january-2024", "official_municipal_source": True,
                  "evidence_kind": "dated_official_gendered_title", "registry_gender_field": False,
                  "main_treatment_assignment": "unverified"})
    events = {e["ags"]: e for e in json.loads(Path("outputs/nrw-election-register/events.json").read_text())}
    for observation in added:
        e = events[observation["ags"]]
        finalists = [c["candidate_name_source"] for c in e["candidates"] if not e["has_runoff"] or c["votes_runoff"] is not None]
        if not e["votes_and_winner_verified"] or not e["decisive_pair"] or observation["candidate_name_source"] not in finalists:
            raise ValueError("Extension observation does not match a verified decisive finalist")
        observation["source"] = sources[observation["source_id"]]
    unna = events["05978036"]
    pair_votes = [c["votes_runoff"] for c in unna["candidates"] if c["votes_runoff"] is not None]
    if max(pair_votes) - min(pair_votes) != 221:
        raise ValueError("Party vote difference does not match official election")
    observations = json.loads(Path("outputs/nrw-primary-presentation/candidate-observations.json").read_text()) + added
    mixed = sum({o["presentation"] for o in observations if o["ags"] == ags} == {"female", "male"}
                for ags in {o["ags"] for o in observations})
    entry = hopp_entry(paths["viersen-mayor"].read_text())
    if events[entry["ags"]]["winner_name_source"] == entry["candidate_name_source"]:
        raise ValueError("The 2025 successor has been confused with the 2020 winner")
    entry["source"] = sources[entry["source_id"]]
    summary = {"new_primary_candidate_observations": len(added), "combined_primary_candidate_observations": len(observations),
               "pairs_with_both_mixed_primary_presentations": mixed, "new_dated_party_observations": 2,
               "new_dated_official_title_observations": 1, "new_current_official_person_observations": 2,
               "named_official_successor_entry_statements": 1, "main_treatment_or_responsibility_assignments": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in [("candidate-observations", observations), ("successor-entry", entry), ("summary", summary)]:
        (OUT / f"{name}.json").write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
