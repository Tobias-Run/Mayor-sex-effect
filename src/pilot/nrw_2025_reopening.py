"""Audit the full official NRW 2025 municipal mayor-election universe.

Run from repo root: python src/pilot/nrw_2025_reopening.py
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

BASE = "https://www.wahlergebnisse.nrw/kommunalwahlen/2025/"
ROOT = Path("data/raw/nrw-2025")
OUT = Path("outputs/nrw-election-register-2025")
SUMMARIES = [
    {"file": "KW25_pers_gemeinden.txt", "sha256": "05daeebda23f055301dda8ded7920e63094faf2efefa38aecf4e2ea387a1e59f", "scope": "district_municipality"},
    {"file": "KW25_pers_insgesamt.txt", "sha256": "b83d5e0c5ccaa02bc0d0935f4b347fcb48adc696fca5ba189fd1dea245a5ee8e", "scope": "combined_city_county"},
]
FIRST_DATE, RUNOFF_DATE = "2025-09-14", "2025-09-28"


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
            if row["Datum"] not in ("14.09.2025", "28.09.2025", "Es findet keine Wahl statt"):
                raise ValueError("Unexpected election date in the fixed 2025 universe")
            entry = entries.setdefault(code, {"source_code": code, "ags": official_ags(code),
                "municipality_source": name, "source_scope": "archive_city_mayor" if source["scope"] == "combined_city_county" else source["scope"], "summary_rows": []})
            if entry["municipality_source"] != name:
                raise ValueError("Conflicting municipality identity")
            entry["summary_rows"].append(row)
    for entry in entries.values():
        dates = [r["Datum"] for r in entry["summary_rows"]]
        if len(set(dates)) != len(dates):
            raise ValueError("Duplicate summary municipality/date")
        entry["election_held"] = "14.09.2025" in dates
        entry["has_runoff"] = "28.09.2025" in dates
        if set(dates) not in ({"14.09.2025"}, {"14.09.2025", "28.09.2025"}, {"Es findet keine Wahl statt"}):
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
    header_date = "28.09.2025" if entry["has_runoff"] else "14.09.2025"
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
    ROOT.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    source_root = Path("data/raw/national-reopening-2026-10-10")
    summaries = []
    for source in SUMMARIES:
        raw = (source_root / source["file"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != source["sha256"]:
            raise ValueError("Summary source changed")
        summaries.append((source, raw.decode("utf-8-sig")))
    entries, counties = universe(summaries)
    cache = ROOT / "detail-retrieval.json"
    manifest = json.loads(cache.read_text()) if cache.exists() else {}
    def acquire(entry):
        if not entry["election_held"]:
            return entry, None, None
        code = entry["source_code"]
        path = ROOT / (code + ".txt")
        url = BASE + f"aktuell/txtdateien/b{code}kw2500.txt"
        meta = manifest.get(code)
        try:
            if path.exists():
                raw = path.read_bytes()
                if not meta or meta["url"] != url or hashlib.sha256(raw).hexdigest() != meta["sha256"]:
                    raise ValueError("Cache lacks valid source pin")
            else:
                with urlopen(url, timeout=40) as response:
                    raw = response.read()
                path.write_bytes(raw)
                meta = {"url": url, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "retrieved_at_utc": datetime.now(timezone.utc).isoformat()}
            event = parse_detail(raw.decode("utf-8-sig"), entry)
            event["detail_source"] = meta
            return event, meta, None
        except Exception as error:
            return entry, meta, str(error)
    results = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for index, result in enumerate(pool.map(acquire, entries), 1):
            results.append(result)
            if index % 50 == 0:
                print(f"Checked {index}/{len(entries)} entries", flush=True)
    manifest.update({r[0]["source_code"]: r[1] for r in results if r[1]})
    cache.write_text(json.dumps(manifest, indent=2))
    events = [r[0] for r in results if r[2] is None and r[0]["election_held"]]
    path = Path("data/raw/bavaria-bounded-route/direct-source-checks/gerda-current-candidates.csv")
    if hashlib.sha256(path.read_bytes()).hexdigest() != "7ab9425dc9b4b1625eadcd5ff001689cec72e32d5f278a5740a29c7b1e9212b1":
        raise ValueError("GERDA snapshot changed")
    groups = defaultdict(list)
    for row in csv.DictReader(path.open()):
        if row["state"] == "05" and row["election_date"] == FIRST_DATE:
            groups[row["ags"]].append(row)
    comparisons, leads = [], []
    for event in events:
        rows = groups[event["ags"]]
        matched, reason = compare_gerda(event, rows)
        pair_match = compare_decisive_pair(event, rows)
        comparisons.append({"ags": event["ags"], "full_match": matched, "pair_match": pair_match, "reason": reason})
        if pair_match:
            pair = [r for r in rows if not event["has_runoff"] or r["candidate_votes_sw"]]
            if {r["candidate_gender"] for r in pair} == {"w", "m"}:
                leads.append({"ags": event["ags"], "margin_pp": event["absolute_margin_pp"], "female_label_winner": any(r["candidate_gender"] == "w" and r["is_winner"] == "TRUE" for r in pair)})
    pairs = [e for e in events if e["decisive_pair"]]
    summary = {"checked_on": "2026-10-10", "cohort": "NRW September 2025", "municipal_entries": len(entries), "elections_held": sum(e["election_held"] for e in entries), "no_election_entries": sum(not e["election_held"] for e in entries), "excluded_counties": counties, "details_validated": len(events), "failures": [{"source_code":r[0]["source_code"], "reason":r[2]} for r in results if r[2]], "candidate_records":sum(e["candidate_count"] for e in events), "runoffs":sum(e["has_runoff"] for e in events), "decisive_pairs":len(pairs), "full_gerda_matches":sum(c["full_match"] for c in comparisons), "decisive_pair_gerda_matches":sum(c["pair_match"] for c in comparisons), "bands": [{"width_pp":h, "all_pairs":sum(e["absolute_margin_pp"] <= h for e in pairs), "predicted_mixed_leads":sum(e["margin_pp"] <= h for e in leads), "predicted_female_wins":sum(e["margin_pp"] <= h and e["female_label_winner"] for e in leads)} for h in (1,2,5,10)], "verified_gender_pairs":0, "certified_linked_elections":0, "gender_warning":"Name predictions are search leads; same-label predictions cannot exclude an actual mixed pair."}
    for name, data in (("summary",summary),("events",events),("comparison",comparisons),("prediction-leads",leads)):
        (OUT / (name+".json")).write_text(json.dumps(data, indent=2, ensure_ascii=False))
    public = Path("docs/feasibility/nrw-2025-reopening-summary.json")
    public.write_text(json.dumps(summary, indent=2, ensure_ascii=False)+"\n")
    with Path("docs/feasibility/nrw-2025-source-manifest.csv").open("w", newline="") as f:
        writer=csv.DictWriter(f, fieldnames=["url","sha256","bytes","retrieved_at_utc"])
        writer.writeheader()
        for row in json.loads((source_root / "nrw2025-summary-retrieval.json").read_text()) + list(manifest.values()):
            writer.writerow({k:row[k] for k in writer.fieldnames})
    print(json.dumps(summary, indent=2), flush=True)

if __name__ == "__main__":
    main()
