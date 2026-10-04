"""Add Frechen and Werdohl party evidence with explicit historical timing.

Party letters addressing another party's incumbent remain party-authored.
Werdohl's visible publication-day labels conflict with its permalinks, so the
named event reference and safe month precision are retained separately.
"""
import argparse
import csv
import json
from pathlib import Path

from bavaria_evidence_sources import html_text, verified_source
from nrw_election_register import name_key

ROOT = Path("data/raw/nrw-followup-evidence")
OUT = Path("outputs/nrw-historical-presentation-followup")
MANIFEST = Path("docs/feasibility/nrw-procedure-primary-source-manifest.csv")


def followup_presentations(raw):
    text = {k: html_text(v) for k, v in raw.items()}
    observations = []
    items = [
        ("warntafel-auf-der-elisabethstrasse-wieder-aufstellen", "05362024", "Stupp, Susanne", "female",
         "Frau Bürgermeisterin Susanne Stupp", "2020-09-23", "day", "dated_party_letter_addressee_presentation"),
        ("strassenausbaubeitraege-nicht-mehr-zeitgemaess", "05362024", "Peters, Carsten", "male",
         "Bürgermeisterkandidat Carsten Peters", "2020-08-31", "day", "dated_party_authored_candidate_presentation"),
        ("werdohl-spaeinghaus-2020", "05962060", "Späinghaus, Andreas", "male",
         "Andreas Späinghaus zum Bürgermeister-Kandidaten gewählt", "2020-06-14", "day", "party_candidate_presentation_with_dated_event_reference"),
        ("werdohl-silvia-2017", "05962060", "Voßloh, Silvia", "female",
         "Bürgermeisterin Silvia Voßloh", "2017-10", "month", "historical_party_authored_incumbent_presentation"),
    ]
    for key, ags, name, gender, quote, day, precision, kind in items:
        if quote not in text[key]:
            raise ValueError("Named primary party presentation changed")
        observations.append({"source_id": key, "ags": ags, "candidate_name_source": name, "presentation": gender,
                             "observation_date": day, "date_precision": precision, "source_quote": quote,
                             "evidence_kind": kind, "official_municipal_source": False, "registry_gender_field": False,
                             "main_treatment_assignment": "unverified"})
    if "Frechen, 23.09.2020 / 66" not in text[items[0][0]] or "September 30, 2020" not in text[items[0][0]]:
        raise ValueError("Party letter date and later article publication changed")
    observations[0].update({"source_date_kind": "letter_date", "article_publication_date": "2020-09-30"})
    if "August 31, 2020" not in text[items[1][0]]:
        raise ValueError("Dated candidate article changed")
    observations[1]["source_date_kind"] = "article_publication_date"
    event_quote = "am 14.06.2020 wurde Andreas Späinghaus offiziell mit 100 % der Stimmen zum Bürgermeisterkandidaten gewählt"
    if event_quote not in text[items[2][0]]:
        raise ValueError("Named candidate nomination event changed")
    observations[2].update({"source_date_kind": "named_nomination_event_reference", "source_event_quote": event_quote,
                            "article_publication_day_not_certified": True, "visible_publication_day_and_permalink_conflict": True})
    if "Haushaltsberatung 2017" not in text[items[3][0]] or "Vom 13.-14. Oktober" not in text[items[3][0]]:
        raise ValueError("Historical budget-event context changed")
    observations[3].update({"source_date_kind": "named_historical_event_month", "historical_2020_observation": False,
                            "source_event_date_range": ["2017-10-13", "2017-10-14"],
                            "article_publication_day_not_certified": True, "visible_publication_day_and_permalink_conflict": True})
    return observations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    sources = {s["id"]: s for s in csv.DictReader(MANIFEST.open())}
    paths = {key: verified_source(s, args.download, ROOT) for key, s in sources.items()}
    if any(path.stat().st_size != int(sources[key]["bytes"]) for key, path in paths.items()):
        raise ValueError("Primary source byte count changed")
    added = followup_presentations({key: p.read_text() for key, p in paths.items() if p.suffix == ".html"})
    events = {e["ags"]: e for e in json.loads(Path("outputs/nrw-election-register/events.json").read_text())}
    for observation in added:
        event = events[observation["ags"]]
        matches = [c for c in event["candidates"] if name_key(c["candidate_name_source"]) == name_key(observation["candidate_name_source"])
                   and (not event["has_runoff"] or c["votes_runoff"] is not None)]
        if not event["votes_and_winner_verified"] or not event["decisive_pair"] or len(matches) != 1:
            raise ValueError("Primary presentation does not match one verified decisive candidate")
        observation["candidate_name_source"] = matches[0]["candidate_name_source"]
        observation["source"] = sources[observation["source_id"]]
    observations = json.loads(Path("outputs/nrw-extension-evidence/candidate-observations.json").read_text()) + added
    pairs = [{"ags": ags, "both_mixed_primary_presentations": {o["presentation"] for o in observations if o["ags"] == ags} == {"female", "male"},
              "main_treatment_assignment": "unverified"} for ags in sorted({o["ags"] for o in observations})]
    summary = {"new_party_primary_presentations": len(added), "combined_primary_presentations": len(observations),
               "pairs_with_both_mixed_primary_presentations": sum(p["both_mixed_primary_presentations"] for p in pairs),
               "new_historical_observations_predating_2020": 1, "sources_with_uncertified_publication_day": 2,
               "main_treatment_or_responsibility_assignments": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in [("candidate-observations", observations), ("pair-status", pairs), ("summary", summary)]:
        (OUT / f"{name}.json").write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
