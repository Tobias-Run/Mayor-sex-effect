"""Acquire and audit a historical TED municipal linkage pilot.

Run from repo root: python src/pilot/bavaria_ted_linkage.py [--download]
Python standard library only. Never estimates treatment effects. Indexed result
fields retain their separate levels; publication dates are not award dates.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path("data/raw/ted-bavaria")
OUT = Path("outputs/bavaria-ted-linkage")
URL = "https://api.ted.europa.eu/v3/notices/search"
QUERY = ("buyer-country = DEU AND (buyer-name ~ Gauting OR buyer-name ~ Mühldorf) "
         "AND notice-type = can-standard AND publication-date >= 20210101 AND publication-date <= 20241231")
FIELDS = ["publication-number", "publication-date", "buyer-name", "buyer-city", "buyer-post-code",
          "buyer-identifier", "buyer-legal-type", "notice-type", "procedure-type", "contract-conclusion-date",
          "total-value", "total-value-cur", "winner-name", "tender-value", "tender-value-cur",
          "result-value-notice", "result-value-lot", "received-submissions-type-code",
          "received-submissions-type-val", "BT-759-LotResult", "BT-145-Contract", "BT-142-LotResult",
          "result-lot-identifier", "identifier-lot", "procedure-identifier", "notice-identifier",
          "previous-notice-id-proc", "change-notice-version-identifier", "internal-identifier-proc",
          "strategic-procurement-lot", "strategic-procurement-description-lot",
          "green-procurement-criteria-lot", "social-objective-lot"]
BUYERS = {"Gemeinde Gauting": "09188120", "Stadt Mühldorf am Inn": "09183128",
          "Kreisstadt Mühldorf a. Inn": "09183128"}


def acquire():
    ROOT.mkdir(parents=True, exist_ok=True)
    pages, ids, total = [], set(), None
    for page in range(1, 21):
        request = {"query": QUERY, "fields": FIELDS, "page": page, "limit": 250, "scope": "ALL"}
        with urlopen(Request(URL, json.dumps(request).encode(), headers={"Content-Type": "application/json"}), timeout=40) as response:
            raw = response.read()
        result = json.loads(raw)
        if result.get("timedOut"):
            raise ValueError("TED query timed out; a complete pilot is not established")
        if total is None:
            total = result["totalNoticeCount"]
        elif total != result["totalNoticeCount"]:
            raise ValueError("Notice count changed during pagination; repeat acquisition")
        filename = f"page-{page}.json"
        (ROOT / filename).write_bytes(raw)
        pages.append({"file": filename, "request": request, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        for notice in result["notices"]:
            if notice["publication-number"] in ids:
                raise ValueError("Duplicate notice across acquisition pages")
            ids.add(notice["publication-number"])
        if len(ids) == total:
            break
        if not result["notices"]:
            raise ValueError("Incomplete TED pagination")
    if len(ids) != total:
        raise ValueError("Pilot exceeded pagination guard; no complete snapshot recorded")
    metadata = {"url": URL, "query": QUERY, "fields": FIELDS, "total_notice_count": total,
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "pages": pages}
    (ROOT / "retrieval.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False))


def present(notice, field):
    return field in notice and notice[field] not in (None, [], {}, "")


def one(items):
    return items[0] if isinstance(items, list) and len(items) == 1 else None


def tender_count(notice):
    """Accept only a single identified lot and a single explicitly typed count."""
    if notice.get("BT-142-LotResult") != ["selec-w"]:
        return None
    lots = notice.get("result-lot-identifier", [])
    if len(lots) != 1 or notice.get("identifier-lot") != lots:
        return None
    if notice.get("received-submissions-type-code") != ["tenders"]:
        return None
    value = one(notice.get("received-submissions-type-val"))
    business_term = one(notice.get("BT-759-LotResult"))
    if value is None or business_term is None:
        return None
    try:
        n = Decimal(str(value))
        other = Decimal(str(business_term))
    except InvalidOperation:
        return None
    if not n.is_finite() or not other.is_finite() or n != other:
        return None
    if not n.is_finite() or n != n.to_integral_value() or n < 0:
        return None
    return int(n)


def contract_date(notice):
    value = one(notice.get("contract-conclusion-date"))
    business_term = one(notice.get("BT-145-Contract"))
    if value is None or value != business_term or not re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:Z|[+-]\d{2}:\d{2})?", value):
        return None
    try:
        return str(date.fromisoformat(value[:10]))
    except ValueError:
        return None


def main():
    arguments = argparse.ArgumentParser()
    arguments.add_argument("--download", action="store_true")
    args = arguments.parse_args()
    if args.download:
        if (ROOT / "retrieval.json").exists():
            raise FileExistsError("Preserve the existing snapshot before a new download")
        acquire()
    metadata = json.loads((ROOT / "retrieval.json").read_text())
    if metadata["query"] != QUERY or metadata["fields"] != FIELDS:
        raise ValueError("Snapshot query/field set disagrees with this pilot")
    notices = []
    for page in metadata["pages"]:
        raw = (ROOT / page["file"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != page["sha256"]:
            raise ValueError("TED snapshot checksum changed")
        response = json.loads(raw)
        if response.get("timedOut") or response["totalNoticeCount"] != metadata["total_notice_count"]:
            raise ValueError("Snapshot contains an incomplete query")
        notices.extend(response["notices"])
    if len(notices) != metadata["total_notice_count"] or len({n["publication-number"] for n in notices}) != len(notices):
        raise ValueError("Incomplete or duplicate notice snapshot")
    identity_path = Path("outputs/bavaria-named-reports/recovered-screen-events.json")
    identities = json.loads(identity_path.read_text())
    elections = {e["ags"]: e for e in identities if e["ags"] in set(BUYERS.values())}
    if set(elections) != set(BUYERS.values()):
        raise ValueError("Both exact named election pairs must be recovered before linkage")
    records, exclusions = [], Counter()
    for notice in notices:
        # Multilingual labels are not additional buyers. Use the German buyer
        # list; joint buyers and hospitals/counties are excluded conservatively.
        names = set(notice.get("buyer-name", {}).get("deu", []))
        if len(names) != 1:
            exclusions["multiple_or_missing_german_buyer_labels"] += 1
            continue
        name = next(iter(names))
        if name not in BUYERS:
            exclusions["buyer_not_in_verified_municipal_aliases"] += 1
            continue
        ags = BUYERS[name]
        event = elections[ags]
        awarded = notice.get("BT-142-LotResult") == ["selec-w"]
        explicit_date = contract_date(notice) if awarded else None
        records.append({"ags": ags, "buyer_name": name, "publication_number": notice["publication-number"],
                        "publication_date_source": notice["publication-date"],
                        "election_date": event["decisive_date"], "absolute_margin_pp": event["absolute_margin_pp"],
                        "notice_total_value_source": notice.get("total-value"),
                        "notice_total_value_currency_source": notice.get("total-value-cur"),
                        "winner_status_source": notice.get("BT-142-LotResult"),
                        "single_lot_awarded_tender_count": tender_count(notice),
                        "single_contract_conclusion_date": explicit_date,
                        "procedure_identifier_source": notice.get("procedure-identifier"),
                        "actual_term_assignment": "unverified", "gender_status": "unverified", "source_fields": notice})
    summary = {"retrieval": metadata, "query_notice_count": len(notices), "municipal_notices": len(records),
               "exclusions": dict(exclusions), "municipalities": [],
               "election_identity_sha256": hashlib.sha256(identity_path.read_bytes()).hexdigest()}
    for ags in sorted(elections):
        subset = [r for r in records if r["ags"] == ags]
        summary["municipalities"].append({"ags": ags, "municipality": elections[ags]["municipality"],
            "municipal_notices": len(subset),
            "publication_year_counts": dict(Counter(r["publication_date_source"][:4] for r in subset)),
            "field_presence": {field: sum(present(r["source_fields"], field) for r in subset)
                               for field in ["total-value", "winner-name", "contract-conclusion-date",
                                             "received-submissions-type-val", "strategic-procurement-lot",
                                             "green-procurement-criteria-lot", "social-objective-lot"]},
            "winner_status_counts": dict(Counter(one(r["winner_status_source"]) or "not_indexed" for r in subset)),
            "single_lot_awarded_tender_counts": sum(r["single_lot_awarded_tender_count"] is not None for r in subset),
            "single_contract_dates": sum(r["single_contract_conclusion_date"] is not None for r in subset),
            "actual_terms_verified": False})
    procedures = Counter((r["ags"], one(r["procedure_identifier_source"])) for r in records if one(r["procedure_identifier_source"]))
    summary["repeated_single_procedure_identifiers"] = sum(n > 1 for n in procedures.values())
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "records.json").write_text(json.dumps(records, indent=2, ensure_ascii=False))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    with (OUT / "municipal-notice-linkage.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["ags", "buyer_name", "publication_number", "publication_date_source", "election_date",
                  "absolute_margin_pp", "single_lot_awarded_tender_count", "single_contract_conclusion_date",
                  "actual_term_assignment", "gender_status"]
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        writer.writerows({k: r[k] for k in fields} for r in records)
    print(json.dumps({k: v for k, v in summary.items() if k != "retrieval"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
