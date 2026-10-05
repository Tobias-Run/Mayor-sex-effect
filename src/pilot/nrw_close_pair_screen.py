"""Audit the 55 close NRW decisions under the version-1 presentation codebook.

Run from the repository root. Raw sources and the manual, person-level review
worksheet stay local. Public outputs are event-level dispositions and metadata.
This validates review provenance and arithmetic, not a linguistic classifier.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from decimal import Decimal
from pathlib import Path

from bavaria_evidence_sources import html_text
from nrw_election_register import SUMMARIES, name_key, parse_detail, universe

MANIFEST = Path("docs/feasibility/nrw-close-pair-source-manifest.csv")
REVIEWS = Path("data/interim/nrw-close-pair-screen/reviews.json")
OUT = Path("outputs/nrw-close-pair-screen")
PUBLIC = Path("docs/feasibility/nrw-close-election-evidence-summary.csv")
CODEBOOK = Path("docs/feasibility/candidate-exposure-codebook.md")
CUES = {"named_address", "feminine_personal_role", "personal_pronoun",
        "gender_specific_personal_description"}


def normalized(text):
    return re.sub(r"\s+", " ", text).strip()


def verified_bytes(source):
    if source["status"] != "acquired":
        raise ValueError("An unavailable source cannot supply an assignment")
    raw = Path(source["local_file"]).read_bytes()
    if len(raw) != int(source["bytes"]) or hashlib.sha256(raw).hexdigest() != source["sha256"]:
        raise ValueError("Original source bytes differ from the reviewed pin")
    return raw


def source_text(source, cache):
    key = source["source_id"]
    if key not in cache:
        raw = verified_bytes(source)
        if raw.startswith(b"%PDF"):
            cache[key] = subprocess.check_output(
                ["pdftotext", "-layout", source["local_file"], "-"], text=True)
        else:
            cache[key] = html_text(raw.decode("utf-8", errors="replace"))
    return cache[key]


def decisive(event):
    people = [r for r in event["candidates"]
              if not event["has_runoff"] or r["votes_runoff"] is not None]
    field = "votes_runoff" if event["has_runoff"] else "votes_first"
    total = event["runoff_valid_votes"] if event["has_runoff"] else event["first_valid_votes"]
    if len(people) != 2 or sum(r[field] for r in people) != total or total <= 0:
        raise ValueError("A decisive pair needs exactly two reconciled vote counts")
    if people[0][field] == people[1][field]:
        raise ValueError("Tied decisive pair requires a separate assignment rule")
    winner = max(people, key=lambda r: r[field])
    if name_key(winner["candidate_name_source"]) != name_key(event["winner_name_source"]):
        raise ValueError("Winner and exact decisive votes disagree")
    margin = Decimal(abs(people[0][field] - people[1][field])) * 100 / total
    return people, field, total, margin


def select_pairs(events, maximum=Decimal(10)):
    selected = []
    for event in events:
        if event["decisive_pair"]:
            margin = decisive(event)[3]
            if margin <= maximum:
                selected.append(event)
    selected.sort(key=lambda r: (decisive(r)[3], r["ags"]))
    if len({r["ags"] for r in selected}) != len(selected):
        raise ValueError("Duplicate municipal election in the selected universe")
    return selected


def original_events(sources):
    summaries = []
    for source in SUMMARIES:
        raw = Path("data/raw/nrw-2020", source["file"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != source["sha256"]:
            raise ValueError("Official universe summary changed")
        summaries.append((source, raw.decode("utf-8-sig")))
    entries, _ = universe(summaries)
    events = []
    # The 380-file manifest is the acquisition baseline, not a prediction filter.
    with Path("docs/feasibility/nrw-2020-source-manifest.csv").open(newline="") as handle:
        pins = {r["source_url"]: r for r in csv.DictReader(handle)}
    for entry in entries:
        if not entry["election_held"]:
            continue
        code = entry["source_code"]
        url = "https://www.wahlergebnisse.nrw/kommunalwahlen/2020/aktuell/txtdateien/b" + code + "kw2000.txt"
        pin = pins[url]
        raw = Path("data/raw/nrw-2020", code + ".txt").read_bytes()
        if hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError("Official vote source changed")
        event = parse_detail(raw.decode("utf-8-sig"), entry)
        event["detail_source_id"] = "nrw-result-" + entry["ags"]
        events.append(event)
    if len(events) != 380 or sum(r["decisive_pair"] for r in events) != 214:
        raise ValueError("Official acquisition baseline changed")
    selected = select_pairs(events)
    if len(selected) != 55 or sum(decisive(r)[3] <= 2 for r in selected) != 15:
        raise ValueError("55/15 acquisition checkpoint changed")
    for event in selected:
        verified_bytes(sources[event["detail_source_id"]])
    return selected


def validate_evidence(evidence, sources, cache):
    if evidence["label"] not in {"female", "male", "other_explicit"}:
        raise ValueError("Unsupported presentation label")
    if evidence["tier"] not in {"B", "C"} or not evidence["primary_authorship"]:
        raise ValueError("Presentation requires inspected primary authorship")
    if evidence["cue"] not in CUES or not evidence["person_reference_reviewed"]:
        raise ValueError("Generic masculine titles or another person's pronouns do not qualify")
    if not evidence["original_inspected"] or not evidence["historical_2020_link_reviewed"]:
        raise ValueError("Current or unrelated presentation cannot be interpolated to 2020")
    if evidence["event_context_year"] != 2020 or not evidence["event_context_note"]:
        raise ValueError("Explicit 2020 event linkage is required")
    if evidence["document_date"] and evidence["document_date"] > "2020-12-31" and not evidence["retrospective"]:
        raise ValueError("Later historical accounts must be flagged retrospective")
    if evidence["identity_status"] not in {"matched", "manually_corroborated"}:
        raise ValueError("Unresolved finalist identity cannot receive an assignment")
    if evidence["identity_status"] == "manually_corroborated":
        if not evidence["identity_note"] or not evidence["identity_source_ids"]:
            raise ValueError("Abbreviated identities need documented corroboration")
        for source_id in evidence["identity_source_ids"]:
            verified_bytes(sources[source_id])
    source = sources[evidence["source_id"]]
    text = source_text(source, cache)
    if evidence.get("ocr_text_file"):
        if not evidence.get("visual_page_verified") or not evidence.get("physical_pdf_page"):
            raise ValueError("Scanned presentation needs recorded visual page review")
        raw = Path(evidence["ocr_text_file"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != evidence["ocr_text_sha256"]:
            raise ValueError("Reviewed OCR derivative changed")
        text = raw.decode("utf-8")
    if not evidence["locator"] or normalized(evidence["locator"]) not in normalized(text):
        raise ValueError("Exact evidence locator is absent from the pinned original or reviewed OCR")
    return evidence["label"]


def reviewed_pair(event, review, sources, cache):
    people, field, total, margin = decisive(event)
    if review["ags"] != event["ags"] or len(review["candidates"]) != 2:
        raise ValueError("Two independent finalist dispositions are required")
    labels, accepted, source_ids = [], [], set(review["reviewed_source_ids"])
    for person, candidate in zip(people, review["candidates"]):
        if candidate["candidate_name_source"] != person["candidate_name_source"]:
            raise ValueError("Review identity or official source order changed")
        if candidate["administrative_sex_gender"] is not None:
            raise ValueError("This screen supplies no explicit administrative fields")
        if not candidate["review_disposition"] or not candidate["reason"]:
            raise ValueError("Unclassified candidates need an explicit review disposition")
        evidence = candidate["accepted_evidence"]
        values = {validate_evidence(r, sources, cache) for r in evidence}
        labels.append("conflicting" if len(values) > 1 else next(iter(values), "unresolved"))
        accepted.extend(evidence)
        source_ids.update(r["source_id"] for r in evidence)
    if any(x in {"conflicting", "other_explicit"} for x in labels):
        status = "conflicting_or_other"
    elif "unresolved" in labels:
        status = "unresolved"
    elif set(labels) == {"female", "male"}:
        status = "mixed_public_presentation"
    else:
        status = "same_public_presentation"
    signed, female_win = "", ""
    if status == "mixed_public_presentation":
        female, male = (people[labels.index(label)][field] for label in ("female", "male"))
        signed = str(Decimal(female - male) * 100 / total)
        female_win = str(female > male).lower()
    return {"rank": review["rank"], "ags": event["ags"],
        "municipality": event["municipality_source"].removeprefix("Krfr. Stadt "),
        "decisive_date": event["decisive_date"],
        "decisive_round": "runoff" if event["has_runoff"] else "first",
        "valid_decisive_votes": total, "absolute_margin_pp": str(margin),
        "priority_group": "within_2_pp" if margin <= 2 else "over_2_to_10_pp",
        "pair_status": status, "supported_candidates": sum(x != "unresolved" for x in labels),
        "unresolved_candidates": labels.count("unresolved"),
        "registry_pair_status": "unresolved", "signed_female_minus_male_margin_pp": signed,
        "female_presented_winner": female_win,
        "evidence_tiers": ";".join(sorted({r["tier"] for r in accepted})),
        "has_retrospective_evidence": str(any(r["retrospective"] for r in accepted)).lower(),
        "accepted_source_ids": ";".join(sorted({r["source_id"] for r in accepted})),
        "evidence_sections": review["public_evidence_sections"],
        "reviewed_source_ids": ";".join(sorted(source_ids)),
        "official_vote_source_id": event["detail_source_id"],
        "search_batch_ids": ";".join(review["search_batch_ids"]),
        "remaining_gap": review["public_remaining_gap"],
        "review_status": "initial_review_complete", "main_study_eligibility": "pending"}


def audit_reviews(events, reviews, sources, cache=None):
    cache = {} if cache is None else cache
    by_ags = {r["ags"]: r for r in reviews}
    if len(by_ags) != len(reviews) or set(by_ags) != {r["ags"] for r in events}:
        raise ValueError("Missing, additional or duplicated pair review")
    rows = []
    for rank, event in enumerate(events, 1):
        review = by_ags[event["ags"]]
        if review["rank"] != rank or not review["search_batch_ids"]:
            raise ValueError("Acquisition priority or failed-search provenance is absent")
        for source_id in review["reviewed_source_ids"]:
            if source_id not in sources:
                raise ValueError("Unpinned review source")
        rows.append(reviewed_pair(event, review, sources, cache))
    return rows


def counts(rows):
    return {"pairs": len(rows), "candidate_dispositions": 2 * len(rows),
        "supported_public_presentations": sum(r["supported_candidates"] for r in rows),
        "unresolved_candidates": sum(r["unresolved_candidates"] for r in rows),
        "pair_statuses": dict(Counter(r["pair_status"] for r in rows)),
        "female_presented_wins": sum(r["female_presented_winner"] == "true" for r in rows),
        "female_presented_losses": sum(r["female_presented_winner"] == "false" for r in rows)}


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--reviews", type=Path, default=REVIEWS)
    parser.add_argument("--write-public-tables", action="store_true")
    args = parser.parse_args()
    with MANIFEST.open(newline="") as handle:
        records = list(csv.DictReader(handle))
    sources = {r["source_id"]: r for r in records}
    if len(sources) != len(records):
        raise ValueError("Duplicate source pin")
    for source in sources.values():
        if source["status"] == "acquired":
            verified_bytes(source)
    worksheet = json.loads(args.reviews.read_text())
    if worksheet["codebook_sha256"] != hashlib.sha256(CODEBOOK.read_bytes()).hexdigest():
        raise ValueError("Codebook changed; review and version the measurement rules first")
    events = original_events(sources)
    rows = audit_reviews(events, worksheet["reviews"], sources)
    summary = {"checked_on": "2026-10-05", "measurement": "historically_event_linked_public_presentation",
        "codebook_sha256": worksheet["codebook_sha256"],
        "local_review_sha256": hashlib.sha256(args.reviews.read_bytes()).hexdigest(),
        "all_55": counts(rows), "first_15": counts(rows[:15]), "remaining_40": counts(rows[15:]),
        "inclusive_margin_counts": {str(cut): counts([r for r in rows if Decimal(r["absolute_margin_pp"]) <= cut])
                                    for cut in (1, 2, 5, 10)},
        "source_pin_status_counts": dict(Counter(r["status"] for r in records)),
        "administrative_sex_gender_assignments": 0, "main_treatment_assignments": 0,
        "actual_exposure_histories_certified": 0, "causal_effects_estimated": False}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "review-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (OUT / "event-reviews.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    if args.write_public_tables:
        with PUBLIC.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
