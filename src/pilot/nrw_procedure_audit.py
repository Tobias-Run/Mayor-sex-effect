"""Audit procedure/version identity and permutation-safe indexed lot counts.

This index supplement does not fetch protected full notices. Shared local
references, previous competition notices and repeated contract labels do not
automatically identify duplicate awards. Full-text outcomes stay unchanged.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.request import Request, urlopen
from uuid import UUID

from bavaria_evidence_sources import normalized, verified_source
from bavaria_ted_linkage import URL, contract_date

ROOT = Path("data/raw/ted-nrw-procedures")
OUT = Path("outputs/nrw-procedure-audit")
FIELDS = ["publication-number", "publication-date", "buyer-name", "notice-identifier", "notice-version",
          "procedure-identifier", "internal-identifier-proc", "internal-identifier-glo", "identifier-glo",
          "previous-notice-id-proc", "change-notice-version-identifier", "change-previous-notice-section-identifier",
          "title-proc", "notice-title", "contract-identifier", "contract-title", "contract-tender-id",
          "tender-identifier", "tender-lot-identifier", "result-lot-identifier", "identifier-lot",
          "BT-150-Contract", "BT-145-Contract", "BT-1451-Contract", "contract-conclusion-date",
          "received-submissions-type-code", "received-submissions-type-val", "BT-759-LotResult", "BT-142-LotResult"]
BASELINE_FIELDS = ["publication-date", "buyer-name", "procedure-identifier", "notice-identifier",
                   "internal-identifier-proc", "received-submissions-type-code", "received-submissions-type-val",
                   "BT-759-LotResult", "BT-142-LotResult", "identifier-lot", "result-lot-identifier",
                   "BT-145-Contract", "contract-conclusion-date"]


def retained_records():
    records = [r for folder in ["nrw-buyer-scope", "nrw-extension"]
               for r in json.loads(Path(f"outputs/{folder}/records.json").read_text())]
    result = {r["publication_number"]: r for r in records}
    if len(result) != len(records):
        raise ValueError("Overlapping retained acquisition cohorts")
    return result


def acquire(indexed):
    if (ROOT / "retrieval.json").exists():
        raise FileExistsError("Preserve the reviewed snapshot before a new acquisition")
    ids = sorted(indexed)
    query = "(" + " OR ".join("publication-number = " + n for n in ids) + ")"
    if len(ids) > 250:
        raise ValueError("Fixed one-page acquisition requires a separately reviewed expansion")
    payload = {"query": query, "fields": FIELDS, "page": 1, "limit": 250, "scope": "ALL"}
    with urlopen(Request(URL, json.dumps(payload).encode(), headers={"Content-Type": "application/json"}), timeout=45) as response:
        raw = response.read()
    data = json.loads(raw)
    if data.get("timedOut") or data["totalNoticeCount"] != len(ids) or len(data["notices"]) != len(ids) or {n["publication-number"] for n in data["notices"]} != set(ids):
        raise ValueError("Enriched index acquisition is incomplete")
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "page-1.json").write_bytes(raw)
    meta = {"url": URL, "request": payload, "expected_publication_numbers": ids, "total_notice_count": len(ids),
            "file": "page-1.json", "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat()}
    (ROOT / "retrieval.json").write_text(json.dumps(meta, indent=2))
    previous_ids = sorted({target for n in data["notices"] for target in n.get("previous-notice-id-proc", [])})
    context_request = {"query": "(" + " OR ".join("publication-number = " + n for n in previous_ids) + ")",
                       "fields": ["publication-number", "publication-date", "notice-type", "buyer-name",
                                  "procedure-identifier", "notice-identifier", "notice-version"],
                       "page": 1, "limit": 10, "scope": "ALL"}
    if not previous_ids or len(previous_ids) > 10:
        raise ValueError("Reviewed context acquisition requires one to ten previous notices")
    with urlopen(Request(URL, json.dumps(context_request).encode(), headers={"Content-Type": "application/json"}), timeout=45) as response:
        raw = response.read()
    result = json.loads(raw)
    if result.get("timedOut") or result["totalNoticeCount"] != len(previous_ids) or len(result["notices"]) != len(previous_ids) or {n["publication-number"] for n in result["notices"]} != set(previous_ids):
        raise ValueError("Previous-notice context acquisition is incomplete")
    (ROOT / "previous-notices.json").write_bytes(raw)
    context_meta = {"url": URL, "request": context_request, "expected_publication_numbers": previous_ids,
                    "total_notice_count": len(previous_ids), "file": "previous-notices.json", "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(), "retrieved_at_utc": datetime.now(timezone.utc).isoformat()}
    (ROOT / "previous-retrieval.json").write_text(json.dumps(context_meta, indent=2))


def snapshot(metadata):
    meta = json.loads((ROOT / metadata).read_text())
    reviewed = json.loads(Path("docs/feasibility/nrw-procedure-ted-request-manifest.json").read_text())
    pin = next((p for p in reviewed if p["file"] == meta["file"]), None)
    if pin is None or any(meta[k] != pin[k] for k in ["url", "request", "expected_publication_numbers", "total_notice_count", "file", "bytes", "sha256"]):
        raise ValueError("Procedure snapshot differs from the published reviewed pin")
    raw = (ROOT / meta["file"]).read_bytes()
    if len(raw) != meta["bytes"] or hashlib.sha256(raw).hexdigest() != meta["sha256"]:
        raise ValueError("Indexed procedure snapshot changed")
    data = json.loads(raw)
    ids = {n["publication-number"] for n in data["notices"]}
    if data.get("timedOut") or data["totalNoticeCount"] != meta["total_notice_count"] or len(data["notices"]) != len(ids) or ids != set(meta["expected_publication_numbers"]):
        raise ValueError("Incomplete or duplicate procedure snapshot")
    return meta, data["notices"]


def guid(value):
    return str(UUID(value)) if value else None


def procedure_groups(notices, indexed):
    groups = defaultdict(list)
    for n in notices:
        key = guid(n.get("procedure-identifier"))
        if key:
            groups[(indexed[n["publication-number"]]["ags"], key)].append(n["publication-number"])
    return [{"ags": ags, "procedure_guid": key, "publication_numbers": sorted(numbers)}
            for (ags, key), numbers in sorted(groups.items())]


def version_links(notices, indexed):
    by_version = defaultdict(list)
    for n in notices:
        if n.get("notice-identifier") and n.get("notice-version") is not None:
            by_version[(guid(n["notice-identifier"]), n["notice-version"])].append(n)
    links = []
    for n in notices:
        reference = n.get("change-notice-version-identifier")
        if not reference:
            continue
        match = re.fullmatch(r"([0-9a-fA-F-]{36})-(\d+)", reference)
        targets = by_version.get((guid(match[1]), int(match[2])), []) if match else []
        row = {"publication_number": n["publication-number"], "parent_reference_source": reference,
               "status": "unresolved_parent_version", "automatic_award_deduplication": False}
        if len(targets) == 1:
            target = targets[0]
            same_city = indexed[n["publication-number"]]["ags"] == indexed[target["publication-number"]]["ags"]
            same_proc = guid(n.get("procedure-identifier")) is not None and guid(n.get("procedure-identifier")) == guid(target.get("procedure-identifier"))
            row.update({"parent_publication_number": target["publication-number"],
                        "status": "verified_same_city_procedure_parent_version" if same_city and same_proc else "identity_conflict_review",
                        "parent_result_statuses_source": target.get("BT-142-LotResult"),
                        "child_result_statuses_source": n.get("BT-142-LotResult")})
        links.append(row)
    return links


def local_reference_groups(notices, indexed, field):
    groups = defaultdict(list)
    for n in notices:
        raw = n.get(field)
        values = raw if isinstance(raw, list) else [raw] if raw else []
        for value in set(values):
            groups[(indexed[n["publication-number"]]["ags"], value)].append(n)
    return [{"ags": ags, "reference_source": ref, "publication_numbers": sorted(n["publication-number"] for n in rows),
             "distinct_nonmissing_procedure_guids": len({guid(n["procedure-identifier"]) for n in rows if n.get("procedure-identifier")}),
             "automatic_merge": False}
            for (ags, ref), rows in sorted(groups.items()) if len(rows) > 1]


def single_awarded_lot_total(notice):
    """All statistics must equal the same positive integer; no array zipping.

With one explicitly awarded lot and exactly one total-tenders type, an equal
value for every returned statistic leaves the total invariant to any permutation.
Unequal values require unavailable type/value/lot associations and stay unknown.
"""
    lots = notice.get("result-lot-identifier", [])
    codes = notice.get("received-submissions-type-code", [])
    values = notice.get("received-submissions-type-val", [])
    business = notice.get("BT-759-LotResult", [])
    if notice.get("BT-142-LotResult") != ["selec-w"] or len(lots) != 1 or notice.get("identifier-lot") != lots:
        return None
    if not codes or codes.count("tenders") != 1 or len(set(codes)) != len(codes) or not len(codes) == len(values) == len(business):
        return None
    try:
        numbers = [Decimal(str(v)) for v in values + business]
    except InvalidOperation:
        return None
    if any(not v.is_finite() or v < 1 or v != v.to_integral_value() for v in numbers) or len(set(numbers)) != 1:
        return None
    return {"lot_number": lots[0], "received_tenders": int(numbers[0]),
            "statistic_types_source": codes, "all_statistic_values_identical": True,
            "contract_conclusion_date": contract_date(notice), "evidence_kind": "index_supported_single_awarded_lot",
            "fulltext_validated": False, "responsibility_assignment": "unverified"}


def legacy_reference(text):
    pre = normalized(text).split("II.1.2.")[0]
    if "Abschnitt I: Öffentlicher Auftraggeber" not in pre or "II.1.1." not in pre:
        return None
    values = re.findall(r"Referenznummer der Bekanntmachung: (.*?)(?=II\.1\.2\.|$)", pre)
    if len(values) > 1:
        raise ValueError("Multiple legacy procedure references in the header")
    return values[0].strip() if values else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    indexed = retained_records()
    if args.download:
        acquire(indexed)
    meta, notices = snapshot("retrieval.json")
    if set(meta["expected_publication_numbers"]) != set(indexed) or meta["request"]["fields"] != FIELDS:
        raise ValueError("Reviewed enriched index cohort or fields changed")
    for n in notices:
        old = indexed[n["publication-number"]]["source_fields"]
        if any(n.get(k) != old.get(k) for k in BASELINE_FIELDS):
            raise ValueError("Previously reviewed buyer/result fields changed; review the update")
    groups = procedure_groups(notices, indexed)
    links = version_links(notices, indexed)
    internal = local_reference_groups(notices, indexed, "internal-identifier-proc")
    contracts = local_reference_groups(notices, indexed, "contract-identifier")
    context_meta, context = snapshot("previous-retrieval.json")
    by_number = {n["publication-number"]: n for n in context}
    previous = [{"publication_number": n["publication-number"], "previous_publication_number": target,
                 "previous_notice_type": by_number.get(target, {}).get("notice-type"),
                 "automatic_award_deduplication": False}
                for n in notices for target in n.get("previous-notice-id-proc", [])]
    counts = []
    for n in notices:
        result = single_awarded_lot_total(n)
        if result:
            counts.append(dict(result, publication_number=n["publication-number"], ags=indexed[n["publication-number"]]["ags"]))
    original = {r["publication_number"] for r in json.loads(Path("outputs/nrw-buyer-scope/records.json").read_text())}
    manifest = list(csv.DictReader(Path("docs/feasibility/nrw-complete-ted-source-manifest.csv").open()))
    refs, legacy = [], 0
    for source in manifest:
        number = source["publication_number"]
        if number not in original:
            continue
        path = verified_source(source, root=Path("data/raw/nrw-complete-ted"))
        if path.stat().st_size != int(source["bytes"]):
            raise ValueError("Full-text byte count changed")
        text = subprocess.run(["pdftotext", "-layout", str(path), "-"], check=True, capture_output=True, text=True).stdout
        legacy += "Abschnitt I: Öffentlicher Auftraggeber" in normalized(text)
        reference = legacy_reference(re.sub(re.escape(number) + r"\s+Page \d+/\d+", " ", text))
        if reference:
            refs.append({"publication_number": number, "ags": indexed[number]["ags"], "legacy_reference_source": reference,
                         "automatic_merge": False})
    ref_groups = Counter((r["ags"], r["legacy_reference_source"]) for r in refs)
    awards = json.loads(Path("outputs/nrw-complete-ted/awards.json").read_text())
    dated = [a for a in awards if a["contract_conclusion_date"] is not None and a["received_tenders"] is not None]
    concentration = [{"ags": ags, "dated_count_award_units": sum(a["ags"] == ags for a in dated),
                      "distinct_dated_count_notices": len({a["publication_number"] for a in dated if a["ags"] == ags})}
                     for ags in sorted({a["ags"] for a in dated})]
    summary = {"retained_indexed_notices": len(notices), "unchanged_baseline_fields_per_notice": len(BASELINE_FIELDS),
               "notices_with_procedure_guid": sum(len(g["publication_numbers"]) for g in groups),
               "distinct_scoped_observed_procedure_guids": len(groups),
               "notices_without_procedure_guid": sum(not n.get("procedure-identifier") for n in notices),
               "multiple_notice_procedure_groups": sum(len(g["publication_numbers"]) > 1 for g in groups),
               "verified_parent_version_links": sum(l["status"] == "verified_same_city_procedure_parent_version" for l in links),
               "previous_notice_context_rows": len(context), "previous_notice_links": len(previous),
               "shared_internal_reference_groups": len(internal),
               "shared_internal_reference_groups_with_different_guids": sum(g["distinct_nonmissing_procedure_guids"] > 1 for g in internal),
               "shared_contract_reference_groups_with_different_guids": sum(g["distinct_nonmissing_procedure_guids"] > 1 for g in contracts),
               "original_legacy_notices_checked": legacy, "legacy_header_reference_notices": len(refs),
               "repeated_scoped_legacy_reference_groups": sum(c > 1 for c in ref_groups.values()),
               "index_supported_single_lot_total_counts": len(counts),
               "index_supported_single_lot_counts_with_contract_dates": sum(c["contract_conclusion_date"] is not None for c in counts),
               "original_fulltext_dated_count_units_unchanged": len(dated),
               "original_fulltext_independent_election_events": len(concentration),
               "new_fulltext_award_units": 0, "automatic_notice_or_award_merges": 0,
               "main_treatment_or_responsibility_assignments": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in [("procedure-groups", groups), ("version-links", links), ("previous-notice-links", previous),
                        ("internal-reference-groups", internal), ("contract-reference-groups", contracts),
                        ("index-supported-counts", counts), ("legacy-references", refs),
                        ("award-concentration", concentration), ("summary", summary)]:
        (OUT / f"{name}.json").write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps({"summary": summary, "concentration": concentration}, indent=2))


if __name__ == "__main__":
    main()
