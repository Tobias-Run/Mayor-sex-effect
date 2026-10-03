"""Add dated party-authored candidate presentation without relabelling it official.

The existing municipal evidence stays a separate source category. Public title
presentation does not automatically establish the main-study treatment measure.
"""
import argparse
import json
from pathlib import Path

from bavaria_evidence_sources import html_text, verified_source

ROOT = Path("data/raw/nrw-expanded")
OUT = Path("outputs/nrw-candidate-followup")
SOURCE = {
  "id": "kanschat-2020-party",
  "extension": ".html",
  "url": "https://www.gruene-velbert.de/schulentwicklung-voellig-entgegen-elternwillen/",
  "sha256": "1c3609b21ed59ca56cf2c599ffafed1fc7674041b48cf7a0f358e2732155c9a4",
  "bytes": 63856,
  "retrieved_at_utc": "2026-10-03T21:20:50.988885+00:00"
}


def party_observation(raw):
    text = html_text(raw)
    quote = "Fraktionsvorsitzende Bündnis 90/Die Grünen und Bürgermeisterkandidatin Frau Dr. Esther Kanschat"
    dated = "Schulentwicklung völlig entgegen Elternwillen 29. April 2020 " + quote
    if dated not in text:
        raise ValueError("Dated named candidate statement changed")
    return {"ags": "05158032", "candidate_name_source": "Kanschat, Dr. Esther", "presentation": "female",
            "observation_date": "2020-04-29", "source_quote": quote, "source": SOURCE,
            "evidence_kind": "dated_party_authored_candidate_presentation", "official_municipal_source": False,
            "registry_gender_field": False, "main_treatment_assignment": "unverified"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    path = verified_source(SOURCE, args.download, ROOT)
    party = party_observation(path.read_text())
    official = json.loads(Path("outputs/nrw-official-evidence/titles.json").read_text())
    events = {e["ags"]: e for e in json.loads(Path("outputs/nrw-election-register/events.json").read_text())}
    e = events[party["ags"]]
    if not e["votes_and_winner_verified"] or not e["decisive_pair"] or not any(
            c["candidate_name_source"] == party["candidate_name_source"] and c["votes_runoff"] is not None for c in e["candidates"]):
        raise ValueError("Party candidate does not match an official decisive finalist")
    all_titles = official + [party]
    pairs = [{"ags": ags, "mixed_primary_presentations": {t["presentation"] for t in all_titles if t["ags"] == ags} == {"female", "male"},
              "both_official_municipal_sources": {t["presentation"] for t in official if t["ags"] == ags} == {"female", "male"},
              "main_treatment_assignment": "unverified"} for ags in sorted({t["ags"] for t in all_titles})]
    summary = {"official_municipal_title_observations": len(official), "dated_party_candidate_observations": 1,
               "pairs_with_both_mixed_primary_presentations": sum(p["mixed_primary_presentations"] for p in pairs),
               "pairs_with_both_mixed_official_municipal_titles": sum(p["both_official_municipal_sources"] for p in pairs),
               "main_treatment_assignments": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in [("candidate-observations", all_titles), ("pair-status", pairs), ("summary", summary)]:
        (OUT / (name + ".json")).write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
