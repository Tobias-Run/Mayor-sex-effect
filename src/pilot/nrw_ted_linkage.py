"""Link a fixed NRW TED pilot to three exact, source-audited 2020 elections.

Run: python src/pilot/nrw_ted_linkage.py [--download]
Result notices are not automatically awards; fields and scope retain uncertainty.
"""
import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from bavaria_ted_linkage import FIELDS, URL, contract_date, one, present, tender_count

ROOT = Path("data/raw/ted-nrw")
OUT = Path("outputs/nrw-ted-linkage")
QUERY = ("buyer-country = DEU AND (buyer-name ~ Iserlohn OR buyer-name ~ Velbert OR buyer-name ~ Geilenkirchen) "
         "AND notice-type = can-standard AND publication-date >= 20210101 AND publication-date <= 20241231")
BUYERS = {"Stadt Iserlohn": "05962024", "Stadt Velbert": "05158032",
          "Stadt Geilenkirchen": "05370012", "Stadt Geilenkirchen -Die Bürgermeisterin-": "05370012",
          "Stadt Geilenkirchen, Die Bürgermeisterin": "05370012"}


def classify_buyer(notice):
    """Use reviewed exact German authority labels; keep represented/joint scope open."""
    names = set(notice.get("buyer-name", {}).get("deu", []))
    if len(names) != 1:
        return None, "multiple_or_missing_german_buyer_labels"
    name = next(iter(names))
    if name in BUYERS:
        return BUYERS[name], None
    if name.startswith(("Stadt Iserlohn", "Stadt Velbert", "Stadt Geilenkirchen")):
        return None, "municipal_variant_or_beneficiary_scope_needs_review"
    return None, "other_organization_outside_direct_city_pilot"


def acquire():
    ROOT.mkdir(parents=True, exist_ok=True)
    if (ROOT / "retrieval.json").exists():
        raise FileExistsError("Preserve the existing snapshot before acquiring a new one")
    total, ids, pages = None, set(), []
    for page in range(1, 21):
        request = {"query": QUERY, "fields": FIELDS, "page": page, "limit": 250, "scope": "ALL"}
        with urlopen(Request(URL, json.dumps(request).encode(), headers={"Content-Type": "application/json"}), timeout=40) as response:
            raw = response.read()
        result = json.loads(raw)
        if result.get("timedOut"):
            raise ValueError("Timed-out TED query is not a complete pilot")
        if total is None:
            total = result["totalNoticeCount"]
        elif total != result["totalNoticeCount"]:
            raise ValueError("TED total changed during pagination")
        for notice in result["notices"]:
            number = notice["publication-number"]
            if number in ids:
                raise ValueError("Duplicate notice across snapshot pages")
            ids.add(number)
        filename = f"page-{page}.json"
        (ROOT / filename).write_bytes(raw)
        pages.append({"file": filename, "request": request, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        if len(ids) == total:
            break
        if not result["notices"]:
            raise ValueError("Empty page before complete acquisition")
    if len(ids) != total:
        raise ValueError("Pagination guard exceeded; incomplete snapshot")
    (ROOT / "retrieval.json").write_text(json.dumps({"url": URL, "query": QUERY, "fields": FIELDS,
        "total_notice_count": total, "retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "pages": pages}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    if args.download:
        acquire()
    meta = json.loads((ROOT / "retrieval.json").read_text())
    if meta["query"] != QUERY or meta["fields"] != FIELDS:
        raise ValueError("Query/field set does not match the pilot snapshot")
    notices = []
    for page in meta["pages"]:
        raw = (ROOT / page["file"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != page["sha256"]:
            raise ValueError("Snapshot page checksum changed")
        response = json.loads(raw)
        if response.get("timedOut") or response["totalNoticeCount"] != meta["total_notice_count"]:
            raise ValueError("Snapshot page is incomplete")
        notices.extend(response["notices"])
    if len(notices) != meta["total_notice_count"] or len({n["publication-number"] for n in notices}) != len(notices):
        raise ValueError("Incomplete or duplicate snapshot")
    identity_path = Path("outputs/nrw-election-register/events.json")
    elections = {e["ags"]: e for e in json.loads(identity_path.read_text()) if e["ags"] in set(BUYERS.values())}
    if set(elections) != set(BUYERS.values()) or any(not e["votes_and_winner_verified"] or not e["decisive_pair"] for e in elections.values()):
        raise ValueError("All three source-verified named decisions are required")
    records, excluded = [], []
    for notice in notices:
        ags, reason = classify_buyer(notice)
        if reason:
            excluded.append({"publication_number": notice["publication-number"],
                             "buyer_names": notice.get("buyer-name", {}).get("deu", []), "reason": reason})
            continue
        record = {"ags": ags, "buyer_name": next(iter(set(notice["buyer-name"]["deu"]))),
            "publication_number": notice["publication-number"], "publication_date_source": notice["publication-date"],
            "election_date": elections[ags]["decisive_date"], "absolute_margin_pp": elections[ags]["absolute_margin_pp"],
            "winner_name_source": elections[ags]["winner_name_source"],
            "single_lot_awarded_tender_count": tender_count(notice),
            "single_contract_conclusion_date": contract_date(notice) if notice.get("BT-142-LotResult") == ["selec-w"] else None,
            "gender_measurement": "unverified", "actual_term_assignment": "unverified",
            "source_fields": notice}
        records.append(record)
    summary = {"query_notice_count": len(notices), "retained_direct_city_notices": len(records),
        "excluded_or_scope_review_notices": len(excluded), "exclusion_counts": dict(Counter(r["reason"] for r in excluded)),
        "municipalities": [], "election_register_sha256": hashlib.sha256(identity_path.read_bytes()).hexdigest(),
        "main_treatment_assignments": 0}
    for ags in sorted(elections):
        subset = [r for r in records if r["ags"] == ags]
        summary["municipalities"].append({"ags": ags, "municipality": elections[ags]["municipality_source"],
            "retained_notices": len(subset),
            "publication_year_counts": dict(Counter(r["publication_date_source"][:4] for r in subset)),
            "indexed_result_status_counts": dict(Counter(one(r["source_fields"].get("BT-142-LotResult")) or "not_indexed_or_multiple" for r in subset)),
            "indexed_single_lot_awarded_tender_counts": sum(r["single_lot_awarded_tender_count"] is not None for r in subset),
            "indexed_single_contract_dates": sum(r["single_contract_conclusion_date"] is not None for r in subset),
            "indexed_field_presence": {field: sum(present(r["source_fields"], field) for r in subset) for field in
                ("total-value", "winner-name", "contract-conclusion-date", "green-procurement-criteria-lot", "social-objective-lot")}})
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in (("records", records), ("exclusion-review", excluded), ("summary", summary)):
        (OUT / (name + ".json")).write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
