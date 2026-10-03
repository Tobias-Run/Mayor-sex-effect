"""Apply individually reviewed full-notice scope decisions to the fixed NRW query.

The original strict pilot remains a baseline. This supplement does not broaden
name-prefix matching to unseen notices or merge municipal companies into cities.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

from bavaria_evidence_sources import normalized, verified_source
from bavaria_ted_linkage import contract_date, tender_count
from nrw_ted_linkage import FIELDS, QUERY, classify_buyer

ROOT = Path("data/raw/nrw-expanded")
OUT = Path("outputs/nrw-buyer-scope")
MANIFEST = Path("docs/feasibility/nrw-expanded-source-manifest.csv")
REVIEW = Path("docs/feasibility/nrw-buyer-scope-review.csv")


def fulltext_buyers(text, number):
    text = normalized(re.sub(re.escape(number) + r"\s+Page \d+/\d+", " ", text))
    if number + " - Ergebnis" not in text:
        raise ValueError("Full notice identity changed")
    if "Abschnitt I: Öffentlicher Auftraggeber" in text:
        authority = re.findall(r"Abschnitt I: Öffentlicher Auftraggeber (.*?)Abschnitt II: Gegenstand", text)
        if len(authority) != 1:
            raise ValueError("Ambiguous legacy authority section")
        return re.findall(r"Offizielle Bezeichnung: (.*?)(?: Nationale Identifikationsnummer:| Postanschrift:)", authority[0])
    authority = re.findall(r"1\. Beschaffer (.*?) 2\. Verfahren", text)
    if len(authority) != 1:
        raise ValueError("Ambiguous eForm buyer section")
    return re.findall(r"Offizielle Bezeichnung: (.*?)(?= E-Mail:| Rechtsform des Erwerbers:)", authority[0])


def apply_decision(notice, decision):
    names = notice.get("buyer-name", {}).get("deu", [])
    if set(names) != set(json.loads(decision["buyer_names_json"])):
        raise ValueError("Reviewed buyer labels differ from indexed notice")
    kind = decision["decision"]
    if kind in ("city_department", "represented_city"):
        if len(set(names)) != 1 or " / " in names[0] or " für die " in names[0]:
            raise ValueError("Joint or regional scope cannot be promoted as a single city")
        if kind == "represented_city" and "vertreten durch" not in names[0]:
            raise ValueError("Expected a represented municipal authority")
        if decision["ags"] not in {"05158032", "05370012", "05962024"}:
            raise ValueError("Unexpected municipality in reviewed scope")
        return decision["ags"], kind
    if kind not in ("regional_beneficiary_excluded", "joint_authority_excluded") or decision["ags"]:
        raise ValueError("Unrecognized buyer-scope decision")
    return None, kind


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    sources = {r["publication_number"]: r for r in csv.DictReader(MANIFEST.open())}
    decisions = list(csv.DictReader(REVIEW.open()))
    if len({r["publication_number"] for r in decisions}) != len(decisions):
        raise ValueError("Duplicate scope decision")
    meta = json.loads(Path("data/raw/ted-nrw/retrieval.json").read_text())
    if meta["query"] != QUERY or meta["fields"] != FIELDS:
        raise ValueError("The reviewed query changed")
    notices = []
    for page in meta["pages"]:
        raw = Path("data/raw/ted-nrw", page["file"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != page["sha256"]:
            raise ValueError("TED snapshot checksum changed")
        result = json.loads(raw)
        if result.get("timedOut") or result["totalNoticeCount"] != meta["total_notice_count"]:
            raise ValueError("Incomplete reviewed snapshot")
        notices.extend(result["notices"])
    indexed = {n["publication-number"]: n for n in notices}
    if len(indexed) != len(notices) or len(notices) != meta["total_notice_count"]:
        raise ValueError("Duplicate or incomplete reviewed snapshot")
    queue = {n["publication-number"] for n in notices if classify_buyer(n)[1] in
             {"municipal_variant_or_beneficiary_scope_needs_review", "multiple_or_missing_german_buyer_labels"}}
    if queue != {r["publication_number"] for r in decisions}:
        raise ValueError("Reviewed decisions do not cover the entire original scope queue")
    audited = {}
    for row in decisions:
        number = row["publication_number"]
        source = sources[number]
        path = verified_source(source, args.download, ROOT)
        text = subprocess.run(["pdftotext", "-layout", str(path), "-"], check=True, capture_output=True, text=True).stdout
        if set(fulltext_buyers(text, number)) != set(indexed[number]["buyer-name"]["deu"]):
            raise ValueError("PDF contracting authorities differ from reviewed index labels")
        clean = normalized(re.sub(re.escape(number) + r"\s+Page \d+/\d+", " ", text))
        if row["scope_quote"] not in clean:
            raise ValueError("Reviewed scope quote changed")
        audited[number] = apply_decision(indexed[number], row)
    baseline = json.loads(Path("outputs/nrw-ted-linkage/records.json").read_text())
    records = [{**r, "buyer_scope": "original_strict_city_alias"} for r in baseline]
    elections = {e["ags"]: e for e in json.loads(Path("outputs/nrw-election-register/events.json").read_text())}
    for number, (ags, kind) in audited.items():
        if ags is None:
            continue
        notice, election = indexed[number], elections[ags]
        if not election["votes_and_winner_verified"] or not election["decisive_pair"]:
            raise ValueError("Election is not source verified")
        records.append({"ags": ags, "buyer_name": notice["buyer-name"]["deu"][0], "buyer_scope": kind,
            "publication_number": number, "publication_date_source": notice["publication-date"],
            "election_date": election["decisive_date"], "absolute_margin_pp": election["absolute_margin_pp"],
            "winner_name_source": election["winner_name_source"], "source_fields": notice,
            "single_lot_awarded_tender_count": tender_count(notice),
            "single_contract_conclusion_date": contract_date(notice) if notice.get("BT-142-LotResult") == ["selec-w"] else None,
            "gender_measurement": "unverified", "actual_term_assignment": "unverified"})
    if len({r["publication_number"] for r in records}) != len(records):
        raise ValueError("Duplicate retained notice")
    retained = {r["publication_number"] for r in records}
    exclusions = [{"publication_number": number, "reason": audited[number][1] if number in audited else classify_buyer(n)[1]}
                  for number, n in indexed.items() if number not in retained]
    summary = {"query_notices": len(notices), "baseline_retained_notices": len(baseline),
               "scope_cases_fulltext_reviewed": len(decisions), "scope_decision_counts": dict(Counter(r["decision"] for r in decisions)),
               "expanded_retained_notices": len(records), "remaining_excluded_notices": len(exclusions),
               "exclusion_counts": dict(Counter(r["reason"] for r in exclusions)),
               "municipality_notice_counts": dict(Counter(r["ags"] for r in records)),
               "buyer_scope_counts": dict(Counter(r["buyer_scope"] for r in records)),
               "main_treatment_assignments": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in [("records", records), ("exclusions", exclusions), ("summary", summary)]:
        (OUT / (name + ".json")).write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
