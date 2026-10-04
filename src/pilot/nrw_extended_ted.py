"""Acquire the next six NRW close-election municipalities, preserving scope review.

The nine smallest mixed-prediction margins are an acquisition queue only. Votes
are official-source verified; predicted gender and election dates do not establish
historical gender, actual terms, authority or RDD sample eligibility.
"""
import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from bavaria_ted_linkage import FIELDS, URL, contract_date, tender_count

ROOT = Path("data/raw/ted-nrw-extension")
OUT = Path("outputs/nrw-extension")
QUERY = ("buyer-country = DEU AND (buyer-name ~ Unna OR buyer-name ~ Viersen OR buyer-name ~ Werdohl "
         "OR buyer-name ~ Frechen OR buyer-name ~ Sendenhorst OR buyer-name ~ Weilerswist) "
         "AND notice-type = can-standard AND publication-date >= 20210101 AND publication-date <= 20241231")
BUYERS = {"Kreisstadt Unna": "05978036", "Stadt Unna": "05978036", "Stadt Viersen": "05166032",
          "Stadt Werdohl": "05962060", "Stadt Frechen": "05362024", "Stadt Sendenhorst": "05570040",
          "Gemeinde Weilerswist": "05366040"}


def classify_buyer(notice):
    names = set(notice.get("buyer-name", {}).get("deu", []))
    if len(names) != 1:
        return None, "multiple_or_missing_buyer_labels_review"
    name = next(iter(names))
    if name in BUYERS:
        return BUYERS[name], None
    if name.startswith(tuple(BUYERS)):
        return None, "municipal_variant_or_represented_scope_review"
    return None, "other_organization_outside_direct_municipal_pilot"


def acquire():
    ROOT.mkdir(parents=True, exist_ok=True)
    if (ROOT / "retrieval.json").exists():
        raise FileExistsError("Preserve the existing extension snapshot before a new acquisition")
    total, ids, pages = None, set(), []
    for page in range(1, 21):
        request = {"query": QUERY, "fields": FIELDS, "page": page, "limit": 250, "scope": "ALL"}
        with urlopen(Request(URL, json.dumps(request).encode(), headers={"Content-Type": "application/json"}), timeout=40) as response:
            raw = response.read()
        result = json.loads(raw)
        if result.get("timedOut"):
            raise ValueError("Timed-out query cannot establish complete acquisition")
        if total is None:
            total = result["totalNoticeCount"]
        elif result["totalNoticeCount"] != total:
            raise ValueError("Notice count changed between pages")
        for n in result["notices"]:
            number = n["publication-number"]
            if number in ids:
                raise ValueError("Duplicate notice between extension pages")
            ids.add(number)
        filename = f"page-{page}.json"
        (ROOT / filename).write_bytes(raw)
        pages.append({"file": filename, "request": request, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        if len(ids) == total:
            break
        if not result["notices"]:
            raise ValueError("Empty page before complete acquisition")
    if len(ids) != total:
        raise ValueError("Incomplete extension snapshot")
    (ROOT / "retrieval.json").write_text(json.dumps({"url": URL, "query": QUERY, "fields": FIELDS,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "total_notice_count": total, "pages": pages}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    if args.download:
        acquire()
    meta = json.loads((ROOT / "retrieval.json").read_text())
    if meta["query"] != QUERY or meta["fields"] != FIELDS:
        raise ValueError("Extension query/field set changed")
    notices = []
    for page in meta["pages"]:
        raw = (ROOT / page["file"]).read_bytes()
        if len(raw) != page["bytes"] or hashlib.sha256(raw).hexdigest() != page["sha256"]:
            raise ValueError("Extension snapshot checksum changed")
        response = json.loads(raw)
        if response.get("timedOut") or response["totalNoticeCount"] != meta["total_notice_count"]:
            raise ValueError("Incomplete extension snapshot page")
        notices.extend(response["notices"])
    if len(notices) != meta["total_notice_count"] or len({n["publication-number"] for n in notices}) != len(notices):
        raise ValueError("Duplicate or incomplete acquired notices")
    leads = json.loads(Path("outputs/nrw-election-register/prediction-followup.json").read_text())[:9]
    events = {e["ags"]: e for e in leads if e["ags"] in set(BUYERS.values())}
    if set(events) != set(BUYERS.values()) or any(not e["votes_and_winner_verified"] or not e["decisive_pair"] for e in events.values()):
        raise ValueError("Extension elections differ from the source-verified acquisition queue")
    records, excluded = [], []
    for n in notices:
        ags, reason = classify_buyer(n)
        if reason:
            excluded.append({"publication_number": n["publication-number"], "buyer_names": n.get("buyer-name", {}).get("deu", []), "reason": reason})
            continue
        e = events[ags]
        records.append({"ags": ags, "buyer_name": n["buyer-name"]["deu"][0], "buyer_scope": "extension_strict_city_alias",
                        "publication_number": n["publication-number"], "publication_date_source": n["publication-date"],
                        "election_date": e["decisive_date"], "absolute_margin_pp": e["absolute_margin_pp"],
                        "winner_name_source": e["winner_name_source"], "source_fields": n,
                        "single_lot_awarded_tender_count": tender_count(n),
                        "single_contract_conclusion_date": contract_date(n) if n.get("BT-142-LotResult") == ["selec-w"] else None,
                        "gender_measurement": "unverified", "actual_term_assignment": "unverified"})
    prior = {r["publication_number"] for r in json.loads(Path("outputs/nrw-buyer-scope/records.json").read_text())}
    if prior.intersection(r["publication_number"] for r in records):
        raise ValueError("A retained extension notice overlaps the existing cohort")
    summary = {"query_notices": len(notices), "strict_retained_notices": len(records),
               "review_or_excluded_notices": len(excluded), "reason_counts": dict(Counter(e["reason"] for e in excluded)),
               "municipality_notice_counts": {ags: sum(r["ags"] == ags for r in records) for ags in sorted(events)},
               "municipal_election_events_selected": len(events),
               "municipal_election_events_with_strict_notices": len({r["ags"] for r in records}),
               "indexed_notices_with_strict_total_tenders": sum(r["single_lot_awarded_tender_count"] is not None for r in records),
               "indexed_notices_with_single_awarded_contract_date": sum(r["single_contract_conclusion_date"] is not None for r in records),
               "combined_distinct_retained_indexed_notices": len(prior) + len(records),
               "scope_complete": False,
               "main_treatment_or_responsibility_assignments": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in [("records", records), ("scope-review", excluded), ("summary", summary)]:
        (OUT / (name + ".json")).write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
