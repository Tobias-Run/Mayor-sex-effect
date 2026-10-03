"""Audit the full official NRW 2020 municipal mayor-election universe.

Run from repo root: python src/pilot/nrw_election_register.py --download
Stdlib only; public raw documents and person records remain in ignored folders.
GERDA names/votes are audited independently; predicted genders remain leads.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import unicodedata
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.request import urlopen

BASE = "https://www.wahlergebnisse.nrw/kommunalwahlen/2020/"
ROOT = Path("data/raw/nrw-2020")
OUT = Path("outputs/nrw-election-register")
SUMMARIES = [
    {"file": "KW20_pers_gemeinden.txt", "sha256": "1543ef83d84ac017f779c90de70ed69ea720ff70bc527cf894e132d00cc12e36", "scope": "district_municipality"},
    {"file": "KW20_pers_insgesamt.txt", "sha256": "20791d1ff493f5b5fd81d9f118104eedc1c58a68b0c08f25787b3651ff20aafe", "scope": "combined_city_county"},
]
GERDA_SHA = "5cf7c8f7695cf17d3001ffe49ba5bb5a8f2800be8426754c1db3143b200fba0e"
PANEL_SHA = "2ebbe16114981cd9fdf19e5e6922e5da9d76e70e75b6e86d6f2a2bad3a2fb2aa"
FIRST_DATE, RUNOFF_DATE = "2020-09-13", "2020-09-27"


def name_key(name):
    text = re.sub(r"\s*,\s*", ", ", unicodedata.normalize("NFC", name))
    return re.sub(r"\s+", " ", text).strip().casefold()


def official_ags(code):
    if not re.fullmatch(r"\d{6}", code):
        raise ValueError("Unexpected six-digit state archive code")
    # State archive retains the former Aachen code; GERDA uses the post-2009 AGS.
    return "05334002" if code == "313000" else "05" + code


def universe(summary_texts):
    entries = {}
    excluded_counties = set()
    for source, text in summary_texts:
        lines = text.splitlines()
        if lines[1] != "Endgültige Ergebnisse":
            raise ValueError("Expected official final-result summary")
        for row in csv.DictReader(io.StringIO("\n".join(lines[3:])), delimiter=";"):
            code, name = row["Verwaltungsbezirks-Nr."], row["Verwaltungsbezirksname"]
            if source["scope"] == "combined_city_county" and not name.startswith("Krfr. Stadt "):
                excluded_counties.add(code)
                continue
            if row["Datum"] not in ("13.09.2020", "27.09.2020", "Es findet keine Wahl statt"):
                raise ValueError("Unexpected election date in the fixed 2020 universe")
            entry = entries.setdefault(code, {"source_code": code, "ags": official_ags(code),
                "municipality_source": name, "source_scope": "archive_city_mayor" if source["scope"] == "combined_city_county" else source["scope"], "summary_rows": []})
            if entry["municipality_source"] != name:
                raise ValueError("Conflicting municipality identity")
            entry["summary_rows"].append(row)
    for entry in entries.values():
        dates = [r["Datum"] for r in entry["summary_rows"]]
        if len(set(dates)) != len(dates):
            raise ValueError("Duplicate summary municipality/date")
        entry["election_held"] = "13.09.2020" in dates
        entry["has_runoff"] = "27.09.2020" in dates
        if set(dates) not in ({"13.09.2020"}, {"13.09.2020", "27.09.2020"}, {"Es findet keine Wahl statt"}):
            raise ValueError("Contradictory no-election marker or runoff without first election")
    if len({r["ags"] for r in entries.values()}) != len(entries):
        raise ValueError("Geographic crosswalk is not unique")
    return list(entries.values()), len(excluded_counties)


def parse_detail(text, entry):
    lines = text.splitlines()
    expected = "Endgültiges Ergebnis für " + entry["municipality_source"]
    if expected not in lines or "Landrät" in entry["municipality_source"]:
        raise ValueError("Detail does not match the municipality in the official universe")
    valid_rows = [r for r in csv.reader(lines, delimiter=";") if r and r[0] == "Gültige Stimmen"]
    if len(valid_rows) != 1:
        raise ValueError("Expected one valid-vote row")
    valid = valid_rows[0]
    first_total = int(valid[1])
    runoff_total = int(valid[3]) if entry["has_runoff"] else None
    start = lines.index("davon entfielen auf:") + 1
    candidates = []
    for row in csv.reader(lines[start:], delimiter=";"):
        if not row or not any(row):
            continue
        if len(row) < 3 or not row[1].isdigit() or not row[0].rstrip().endswith(")"):
            raise ValueError("Unexpected candidate row; do not silently drop it")
        name, party = row[0].rstrip()[:-1].rsplit(" (", 1)
        candidates.append({"candidate_name_source": name.strip(), "nomination_source": party,
            "votes_first": int(row[1]), "percentage_first_source": row[2],
            "votes_runoff": int(row[3]) if len(row) > 3 and row[3].isdigit() else None,
            "percentage_runoff_source": row[4] if len(row) > 4 else None})
    listed_total = sum(r["votes_first"] for r in candidates)
    residual = first_total - listed_total
    single_approval = len(candidates) == 1 and not entry["has_runoff"]
    if residual < 0 or residual and not single_approval:
        raise ValueError("First-round votes do not reconcile")
    if single_approval and not any("% der Wähler" in line for line in lines[:12]):
        raise ValueError("Single-candidate ballot needs its distinct source denominator reviewed")
    if len({name_key(r["candidate_name_source"]) for r in candidates}) != len(candidates):
        raise ValueError("Duplicate candidate identities")
    finalists = [r for r in candidates if r["votes_runoff"] is not None]
    if entry["has_runoff"]:
        if len(finalists) != 2 or sum(r["votes_runoff"] for r in finalists) != runoff_total:
            raise ValueError("Runoff does not have a complete reconciled pair")
    elif finalists:
        raise ValueError("Unexpected runoff votes in a first-round-only election")
    decisive = finalists if entry["has_runoff"] else candidates
    field = "votes_runoff" if entry["has_runoff"] else "votes_first"
    ordered = sorted(decisive, key=lambda r: r[field], reverse=True)
    total = runoff_total if entry["has_runoff"] else first_total
    if not ordered or total <= 0 or len(ordered) > 1 and ordered[0][field] == ordered[1][field]:
        raise ValueError("Invalid or tied decisive vote outcome")
    if not entry["has_runoff"] and ordered[0][field] * 2 <= first_total:
        raise ValueError("First-round winner lacks a strict majority; missing second round needs review")
    header_date = "27.09.2020" if entry["has_runoff"] else "13.09.2020"
    marker = f"Bei der {'Stichwahl' if entry['has_runoff'] else 'Wahl'} am {header_date} gewählt:"
    declared_winner = lines[lines.index(marker) + 1].strip()
    if name_key(declared_winner) != name_key(f"{ordered[0]['candidate_name_source']} ({ordered[0]['nomination_source']})"):
        raise ValueError("Declared winner disagrees with exact decisive votes")
    return {**{k: v for k, v in entry.items() if k != "summary_rows"},
            "first_date": FIRST_DATE, "decisive_date": RUNOFF_DATE if entry["has_runoff"] else FIRST_DATE,
            "first_valid_votes": first_total, "runoff_valid_votes": runoff_total,
            "first_valid_votes_not_allocated_to_candidates": residual,
            "ballot_structure": "single_candidate_approval" if single_approval else "competitive_candidates",
            "candidate_count": len(candidates), "candidates": candidates,
            "winner_name_source": ordered[0]["candidate_name_source"],
            "decisive_pair": len(decisive) == 2,
            "absolute_margin_pp": float(Decimal(abs(ordered[0][field] - ordered[1][field])) * 100 / total) if len(decisive) == 2 else None,
            "votes_and_winner_verified": True, "gender_measurement_verified": False,
            "actual_terms_verified": False}


def compare_gerda(event, rows):
    official = {name_key(r["candidate_name_source"]): (r["votes_first"], r["votes_runoff"]) for r in event["candidates"]}
    compiled = {}
    for row in rows:
        key = name_key(row["candidate_name"])
        if key in compiled:
            return False, "duplicate_compiled_identity"
        compiled[key] = (int(row["candidate_votes_hw"]), int(row["candidate_votes_sw"]) if row["candidate_votes_sw"] else None)
    if official != compiled:
        return False, "full_candidate_name_or_vote_vector_differs"
    winners = [r for r in rows if r["is_winner"] == "TRUE"]
    if len(winners) != 1 or name_key(winners[0]["candidate_name"]) != name_key(event["winner_name_source"]):
        return False, "compiled_winner_differs"
    if any(r["election_date"] != FIRST_DATE or
           (r["election_date_sw"] or None) != (RUNOFF_DATE if event["has_runoff"] else None) for r in rows):
        return False, "compiled_dates_differ"
    return True, None


def compare_decisive_pair(event, rows):
    """An unrelated first-round name discrepancy need not invalidate the finalists."""
    if not event["decisive_pair"]:
        return False
    official = {name_key(r["candidate_name_source"]): (r["votes_first"], r["votes_runoff"])
                for r in event["candidates"] if not event["has_runoff"] or r["votes_runoff"] is not None}
    finalists = [r for r in rows if not event["has_runoff"] or r["candidate_votes_sw"]]
    if len(finalists) != 2:
        return False
    compiled = {name_key(r["candidate_name"]): (int(r["candidate_votes_hw"]),
                int(r["candidate_votes_sw"]) if r["candidate_votes_sw"] else None) for r in finalists}
    winners = [r for r in finalists if r["is_winner"] == "TRUE"]
    return (official == compiled and len(winners) == 1 and
            name_key(winners[0]["candidate_name"]) == name_key(event["winner_name_source"]) and
            all(r["election_date"] == FIRST_DATE and
                (r["election_date_sw"] or None) == (RUNOFF_DATE if event["has_runoff"] else None) for r in finalists))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    summaries = []
    for source in SUMMARIES:
        path = ROOT / source["file"]
        if not path.exists() and args.download:
            with urlopen(BASE + source["file"], timeout=30) as response:
                raw = response.read()
            if hashlib.sha256(raw).hexdigest() != source["sha256"]:
                raise ValueError("Pinned summary changed")
            path.write_bytes(raw)
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError("Official summary checksum changed")
        summaries.append((source, path.read_text(encoding="utf-8-sig")))
    entries, excluded_counties = universe(summaries)
    with Path("docs/feasibility/nrw-2020-source-manifest.csv").open(newline="") as f:
        pins = {r["source_url"]: r["sha256"] for r in csv.DictReader(f)}
    old_manifest_path = ROOT / "detail-retrieval.json"
    old_manifest = json.loads(old_manifest_path.read_text()) if old_manifest_path.exists() else {}
    def acquire(entry):
        if not entry["election_held"]:
            return entry, None, None
        code = entry["source_code"]
        path = ROOT / (code + ".txt")
        url = BASE + f"aktuell/txtdateien/b{code}kw2000.txt"
        meta = None
        try:
            if path.exists():
                meta = old_manifest[code]
                raw = path.read_bytes()
                if meta["url"] != url or hashlib.sha256(raw).hexdigest() != meta["sha256"]:
                    raise ValueError("Cached detail checksum changed")
            elif args.download:
                with urlopen(url, timeout=30) as response:
                    raw = response.read()
                path.write_bytes(raw)
                meta = {"url": url, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
                        "retrieved_at_utc": datetime.now(timezone.utc).isoformat()}
            else:
                raise FileNotFoundError("Acquire missing official detail with --download")
            if hashlib.sha256(raw).hexdigest() != pins[url]:
                raise ValueError("Official detail differs from published source pin; review changed source")
            event = parse_detail(raw.decode("utf-8-sig"), entry)
            event["detail_source"] = meta
            return event, meta, None
        except Exception as error:
            return entry, meta, str(error)
    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for index, result in enumerate(pool.map(acquire, entries), 1):
            results.append(result)
            if index % 50 == 0:
                print(f"Checked {index}/{len(entries)} municipal entries", flush=True)
    manifest = {**old_manifest, **{r[0]["source_code"]: r[1] for r in results if r[1] is not None}}
    old_manifest_path.write_text(json.dumps(manifest, indent=2))
    failures = [{"source_code": r[0]["source_code"], "reason": r[2]} for r in results if r[2]]
    events = [r[0] for r in results if r[2] is None and r[0]["election_held"]]
    path = Path("data/raw/gerda/mayoral_candidates.csv")
    if hashlib.sha256(path.read_bytes()).hexdigest() != GERDA_SHA:
        raise ValueError("Pinned GERDA source changed")
    all_nrw = [r for r in csv.DictReader(path.open()) if r["state"] == "05"]
    compiled = [r for r in all_nrw if r["election_year"] == "2020"]
    panel_path = Path("data/raw/gerda/mayor_panel.csv")
    if hashlib.sha256(panel_path.read_bytes()).hexdigest() != PANEL_SHA:
        raise ValueError("Pinned GERDA person panel changed")
    panel = [r for r in csv.DictReader(panel_path.open()) if r["state"] == "05"]
    first_observed = {}
    for row in panel:
        key = (row["person_id"], row["ags"])
        first_observed[key] = min(first_observed.get(key, row["election_date"]), row["election_date"])
    groups = defaultdict(list)
    for row in compiled:
        groups[row["ags"]].append(row)
    comparisons, predicted_pairs = [], []
    for event in events:
        rows = groups[event["ags"]]
        matched, reason = compare_gerda(event, rows)
        pair_matched = compare_decisive_pair(event, rows)
        vectors_match = (sorted((r["votes_first"], r["votes_runoff"] if r["votes_runoff"] is not None else -1) for r in event["candidates"]) ==
                         sorted((int(r["candidate_votes_hw"]), int(r["candidate_votes_sw"]) if r["candidate_votes_sw"] else -1) for r in rows))
        comparisons.append({"ags": event["ags"], "full_names_votes_dates_winner_match": matched,
                            "complete_vote_vector_matches": vectors_match, "decisive_pair_identity_matches": pair_matched, "reason": reason})
        if pair_matched:
            finalist_names = {name_key(r["candidate_name_source"]) for r in event["candidates"]
                              if not event["has_runoff"] or r["votes_runoff"] is not None}
            pair = [r for r in rows if name_key(r["candidate_name"]) in finalist_names]
            event["prediction_followup"] = [{"candidate_name": r["candidate_name"], "gender_label": r["candidate_gender"],
                "source": r["candidate_gender_source"], "method": r["candidate_gender_method"], "probability_source": r["candidate_gender_prob"]} for r in pair]
            if {r["candidate_gender"] for r in pair} == {"w", "m"}:
                predicted_pairs.append(event)
    pairs = [r for r in events if r["decisive_pair"]]
    summary = {"evidence_checked_on": "2026-10-03", "municipal_universe_entries": len(entries),
        "official_elections_held": sum(r["election_held"] for r in entries),
        "official_no_election_entries": sum(not r["election_held"] for r in entries),
        "excluded_county_office_entries": excluded_counties,
        "details_validated": len(events), "detail_failures": failures,
        "official_candidate_records": sum(r["candidate_count"] for r in events),
        "municipal_scope_counts": dict(Counter(r["source_scope"] for r in events)),
        "runoffs": sum(r["has_runoff"] for r in events),
        "first_round_decisions": sum(not r["has_runoff"] for r in events),
        "single_candidate_elections": sum(r["candidate_count"] == 1 for r in events),
        "single_candidate_elections_with_non_candidate_valid_votes": sum(r["candidate_count"] == 1 and r["first_valid_votes_not_allocated_to_candidates"] > 0 for r in events),
        "two_candidate_decisive_pairs": len(pairs),
        "all_pair_margin_counts": {str(h): sum(r["absolute_margin_pp"] <= h for r in pairs) for h in (1, 2, 5, 10)},
        "compiled_full_elections_matched": sum(r["full_names_votes_dates_winner_match"] for r in comparisons),
        "compiled_complete_vote_vectors_matched": sum(r["complete_vote_vector_matches"] for r in comparisons),
        "compiled_decisive_pair_identities_matched": sum(r["decisive_pair_identity_matches"] for r in comparisons),
        "compiled_mismatch_records": [r for r in comparisons if not r["full_names_votes_dates_winner_match"]],
        "gerda_all_years_gender_source": "predicted; not registry-recorded gender",
        "gerda_nrw_candidate_rows_all_years": len(all_nrw),
        "gerda_nrw_candidate_rows_by_year": dict(sorted(Counter(r["election_year"] for r in all_nrw).items())),
        "gerda_nrw_gender_source_counts": dict(Counter(r["candidate_gender_source"] for r in all_nrw)),
        "gerda_nrw_gender_method_counts": dict(Counter(r["candidate_gender_method"] for r in all_nrw)),
        "gerda_nrw_person_election_rows": len(panel),
        "gerda_nrw_person_id_methods": dict(Counter(r["person_id_method"] for r in panel)),
        "gerda_nrw_panel_starts_equal_first_observed_election": sum(r["term_start_date"] == first_observed[(r["person_id"], r["ags"])] for r in panel),
        "prediction_mixed_pair_followup_leads": len(predicted_pairs),
        "prediction_mixed_pair_margin_counts": {str(h): sum(r["absolute_margin_pp"] <= h for r in predicted_pairs) for h in (1, 2, 5, 10)},
        "verified_main_treatment_assignments": 0, "complete_actual_terms_verified": 0}
    for name, data in (("summary", summary), ("universe", entries), ("events", events),
                       ("gerda-comparison", comparisons), ("prediction-followup", sorted(predicted_pairs, key=lambda r: r["absolute_margin_pp"]))):
        (OUT / (name + ".json")).write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
