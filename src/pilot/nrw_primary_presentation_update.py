"""Add exact official Iserlohn identity/presentation and current Velbert corroboration.

Current archived-person/deputy titles retain retrieval timing. A deputy's personal
record end is not the elected full-time mayor's tenure end or appointment date.
"""
import argparse
import json
import re
from pathlib import Path

from bavaria_evidence_sources import html_text, verified_source

ROOT = Path("data/raw/nrw-completion")
OUT = Path("outputs/nrw-primary-presentation")
SOURCES = {
  "iserlohn-kirchhoff-person": {
    "id": "iserlohn-kirchhoff-person",
    "extension": ".html",
    "url": "https://www.iserlohn.sitzung-online.de/public/kp020?KPLFDNR=1000472",
    "sha256": "269bc5f2e1b5123d9b2ad27db08d4009884ea13ee81bb79d3dd3f23ce4f6aaf6",
    "bytes": 18754,
    "retrieved_at_utc": "2026-10-03T22:04:53.878029+00:00"
  },
  "velbert-deputies": {
    "id": "velbert-deputies",
    "extension": ".html",
    "url": "https://www.velbert.de/rathaus-politik/stellv-buergermeister/in",
    "sha256": "10ef86561e8959d5ed525a8ed3cfad17e6a875c2b6ad2d256464e7c4765c9935",
    "bytes": 83743,
    "retrieved_at_utc": "2026-10-03T21:51:08.758817+00:00"
  },
  "joithe-about-0": {
    "id": "joithe-about-0",
    "extension": ".html",
    "url": "https://michael-joithe.de/ihr-buergermeister/",
    "sha256": "2b852977de879c346da75b07394e1ed7e4220f45caca152f043aa912479bb84a",
    "bytes": 115067,
    "retrieved_at_utc": "2026-10-03T22:11:04.420789+00:00"
  },
  "iserlohn-nov9-2020": {
    "id": "iserlohn-nov9-2020",
    "extension": ".html",
    "url": "https://www.iserlohn.de/rathaus-politik/politik/buergermeister/reden-und-video-botschaften-des-buergermeisters/ansprache-9-november-2020",
    "sha256": "aa48f363d58fa61a7feb685366dfc661a211f4a79ba4fd2d38ce67fd40989348",
    "bytes": 83895,
    "retrieved_at_utc": "2026-10-03T22:09:50.867166+00:00"
  }
}


def kirchhoff_observation(raw):
    text = html_text(raw)
    title = re.findall(r"<title\b[^>]*>(.*?)</title>", raw, re.S | re.I)
    quote = "Frau Eva-Barbara Kirchhoff"
    if len(title) != 1 or "Recherche Person Eva-Barbara Kirchhoff" not in html_text(title[0]) or quote not in text:
        raise ValueError("Archived official person identity/presentation changed")
    endings = re.findall(r"Endedatum: (\d{2}\.\d{2}\.\d{4})", text)
    if endings != ["11.11.2025"] or "Rat der Stadt Iserlohn Erste stv. Bürgermeisterin CDU" not in text:
        raise ValueError("Official archived-person context changed")
    return {"ags": "05962024", "candidate_name_source": "Kirchhoff, Eva-Barbara", "presentation": "female",
            "evidence_kind": "current_official_archived_person_presentation", "observation_date": None,
            "retrieved_at_utc": SOURCES["iserlohn-kirchhoff-person"]["retrieved_at_utc"],
            "source_quote": quote, "source": SOURCES["iserlohn-kirchhoff-person"],
            "person_record_end_date_source": "2025-11-11", "person_record_end_is_not_full_time_mayor_term_end": True,
            "official_municipal_source": True, "registry_gender_field": False,
            "main_treatment_assignment": "unverified"}


def kanschat_corroboration(raw):
    quote = "2. stellvertretende Bürgermeisterin Dr. Esther Kanschat"
    if quote not in html_text(raw):
        raise ValueError("Current municipal deputy title changed")
    return {"ags": "05158032", "candidate_name_source": "Kanschat, Dr. Esther", "presentation": "female",
            "evidence_kind": "current_official_deputy_presentation_corroboration",
            "source_quote": quote, "source": SOURCES["velbert-deputies"], "official_municipal_source": True,
            "historical_2020_observation": False, "registry_gender_field": False,
            "deputy_role_is_not_full_time_mayor_authority": True, "main_treatment_assignment": "unverified"}


def joithe_entry_claim(raw):
    text = html_text(raw)
    quote = "Seit meinem Amtsantritt am 02.11.2020"
    if "Name: Michael Joithe" not in text or quote not in text:
        raise ValueError("Named autobiographical entry claim changed")
    return {"ags": "05962024", "candidate_name_source": "Joithe, Michael",
            "reported_entry_date": "2020-11-02", "evidence_kind": "self_authored_initial_entry_claim",
            "source_quote": quote, "source": SOURCES["joithe-about-0"],
            "legal_office_start_verified": False, "complete_term_or_continuous_authority_verified": False}


def joithe_official_activity(raw):
    text = html_text(raw)
    quote = "Ansprache 9. November 2020 Ansprache von Bürgermeister Michael Joithe zum 9. November"
    if quote not in text:
        raise ValueError("Dated official mayoral activity changed")
    return {"ags": "05962024", "candidate_name_source": "Joithe, Michael", "activity_date": "2020-11-09",
            "evidence_kind": "dated_official_mayoral_activity", "source_quote": quote,
            "source": SOURCES["iserlohn-nov9-2020"], "exact_initial_entry_verified": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    paths = {key: verified_source(source, args.download, ROOT) for key, source in SOURCES.items()}
    added = kirchhoff_observation(paths["iserlohn-kirchhoff-person"].read_text())
    corroboration = kanschat_corroboration(paths["velbert-deputies"].read_text())
    entry = joithe_entry_claim(paths["joithe-about-0"].read_text())
    activity = joithe_official_activity(paths["iserlohn-nov9-2020"].read_text())
    earlier = json.loads(Path("outputs/nrw-candidate-followup/candidate-observations.json").read_text())
    observations = earlier + [added]
    events = {e["ags"]: e for e in json.loads(Path("outputs/nrw-election-register/events.json").read_text())}
    for evidence in [added, corroboration]:
        event = events[evidence["ags"]]
        if not event["votes_and_winner_verified"] or not event["decisive_pair"] or not any(
                c["candidate_name_source"] == evidence["candidate_name_source"] and c["votes_runoff"] is not None for c in event["candidates"]):
            raise ValueError("New presentation evidence does not match an official decisive finalist")
    event = events[entry["ags"]]
    if event["winner_name_source"] != entry["candidate_name_source"] or not event["votes_and_winner_verified"] or not event["decisive_date"] < entry["reported_entry_date"] <= activity["activity_date"]:
        raise ValueError("Entry/activity claims conflict with the verified election identity or chronology")
    checks = [{"publication_number": r["publication_number"], "contract_conclusion_date": r["contract_conclusion_date"],
               "before_reported_initial_entry": r["contract_conclusion_date"] < entry["reported_entry_date"],
               "procurement_responsibility_assignment": "unverified"}
              for r in json.loads(Path("outputs/nrw-full-ted/awards.json").read_text())
              if r["ags"] == entry["ags"] and r["contract_conclusion_date"] is not None]
    mixed = sum({r["presentation"] for r in observations if r["ags"] == ags} == {"female", "male"} for ags in {r["ags"] for r in observations})
    summary = {"primary_candidate_observations": len(observations), "new_official_archived_person_observations": 1,
               "separate_current_official_corroborations": 1, "pairs_with_both_mixed_primary_presentations": mixed,
               "self_authored_initial_entry_claims": 1, "dated_official_mayoral_activity_observations": 1,
               "dated_award_units_before_reported_initial_entry": sum(c["before_reported_initial_entry"] for c in checks),
               "historical_gender_or_actual_office_boundary_assignments": 0, "main_treatment_assignments": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in [("candidate-observations", observations), ("current-corroborations", [corroboration]),
                        ("entry-claims", [entry]), ("office-activity-observations", [activity]),
                        ("entry-claim-date-checks", checks), ("summary", summary)]:
        (OUT / (name + ".json")).write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
