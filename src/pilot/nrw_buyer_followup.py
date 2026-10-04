"""Verify individual buyer/beneficiary decisions for the 51-case NRW queue.

Original federal XML supports the reviewed subset. A delivery/performance address
does not establish a beneficiary, and Kreis Unna is not Kreisstadt Unna. Historic
source snapshots and the original inventory are preserved as earlier stages.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from bavaria_evidence_sources import normalized
from federal_procurement import NS, identity, verified_archive
from nrw_federal_procurement import retained_records, select_xml, wanted_keys

ROOT = Path("data/raw/ted-nrw-buyer-followup")
OUT = Path("outputs/nrw-buyer-followup")
MANIFEST = Path("docs/feasibility/nrw-buyer-followup-ted-request-manifest.json")
DECISIONS = Path("docs/feasibility/nrw-buyer-followup-decisions.csv")
ACCEPTED = {"city_department", "city_head_title", "represented_city"}
EXCLUDED = {"joint_authority_excluded", "county_authorities_excluded"}
REVIEW = "municipal_beneficiary_review_pending"


def index_snapshot(download=False):
    pin = json.loads(MANIFEST.read_text())
    path = ROOT / pin["file"]
    if download and not path.exists():
        request = Request(pin["url"], json.dumps(pin["request"]).encode(), headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=45) as response:
            if response.status != 200 or response.headers.get("x-amzn-waf-action") == "challenge":
                raise ValueError("Non-success or protected buyer index response")
            raw = response.read()
        if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError("Mutable buyer index changed; review a new snapshot")
        ROOT.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    raw = path.read_bytes()
    if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
        raise ValueError("Buyer index differs from reviewed pin")
    data = json.loads(raw)
    rows = data["notices"]
    if data.get("timedOut") or len(rows) != pin["total_notice_count"] or data["totalNoticeCount"] != len(rows):
        raise ValueError("Incomplete buyer index")
    if {r["publication-number"] for r in rows} != set(pin["expected_publication_numbers"]):
        raise ValueError("Buyer index identity set changed")
    return rows


def quote_values(xml, document, path):
    if path == "contracting_party_name":
        return [normalized(b["name"]) for b in document["buyers"] if b["name"]]
    allowed = {"cac:ProcurementProject/cbc:Description", ".//cac:RealizedLocation/cac:Address/cbc:StreetName"}
    if path not in allowed:
        raise ValueError("Unreviewed quote locator")
    return [normalized(e.text) for e in xml.findall(path, NS) if e.text]


def apply_scope(document, decision, xml):
    names = [b["name"] for b in document["buyers"]]
    if sorted(normalized(n) for n in names) != sorted(normalized(n) for n in json.loads(decision["buyer_names_json"])):
        raise ValueError("Reviewed original buyer names changed")
    kind, ags = decision["decision"], decision["ags"]
    if not any(decision["scope_quote"] in v for v in quote_values(xml, document, decision["scope_quote_path"])):
        raise ValueError("Scope quote absent from its reviewed source path")
    if kind in ACCEPTED:
        if len(names) != 1 or decision["scope_quote_path"] != "contracting_party_name":
            raise ValueError("Only a sole original contracting party can enter this reviewed city subset")
        expected = "Stadt Werdohl, vertreten durch KUBUS Kommunalberatung und Service GmbH" if ags == "05962060" else "Kreisstadt Unna"
        if ags not in {"05978036", "05962060"} or not normalized(names[0]).startswith(expected):
            raise ValueError("Unexpected municipality in reviewed decision")
        addresses = quote_values(xml, document, ".//cac:RealizedLocation/cac:Address/cbc:StreetName")
        if any("Stadtbetriebe Unna" in address for address in addresses):
            raise ValueError("An operating-unit performance address requires beneficiary review")
        if kind == "represented_city":
            if (ags != "05962060" or not decision["beneficiary_quote"]
                    or decision["beneficiary_quote_path"] != "cac:ProcurementProject/cbc:Description"):
                raise ValueError("Represented city needs an explicit beneficiary quote")
            if not any(decision["beneficiary_quote"] in v for v in quote_values(xml, document, decision["beneficiary_quote_path"])):
                raise ValueError("Represented municipal beneficiary quote changed")
        return ags, kind
    if ags:
        raise ValueError("Excluded or pending scopes cannot receive a municipality assignment")
    if kind == "county_authorities_excluded":
        if len(names) < 2 or "Kreis Unna - Der Landrat" not in names or any("Kreisstadt Unna" in n for n in names):
            raise ValueError("County-only scope changed")
    elif kind == "joint_authority_excluded":
        if set(names) != {"Rhein-Erft-Kreis", "Stadt Frechen"}:
            raise ValueError("Joint county/city scope changed")
    elif kind != REVIEW:
        raise ValueError("Unknown scope decision")
    return None, kind


def audit():
    notices = index_snapshot()
    by_number = {r["publication-number"]: r for r in notices}
    queue = [r for r in json.loads(Path("outputs/nrw-extension/scope-review.json").read_text())
             if r["reason"] != "other_organization_outside_direct_municipal_pilot"]
    if {r["publication_number"] for r in queue} != set(by_number):
        raise ValueError("Follow-up differs from the original 51-case queue")
    prior = {r["publication-number"]: r for name in ["page-1.json", "page-2.json"]
             for r in json.loads(Path("data/raw/ted-nrw-extension", name).read_text())["notices"]}
    common = set(json.loads(Path("data/raw/ted-nrw-extension/retrieval.json").read_text())["fields"]) & set(json.loads(MANIFEST.read_text())["request"]["fields"])
    if any(old.get(f) != by_number[n].get(f) for n, old in prior.items() if n in by_number for f in common):
        raise ValueError("Shared indexed fields changed during follow-up")
    wanted = wanted_keys(notices)
    documents = {}
    raw_xml = {}
    pins = json.loads(Path("docs/feasibility/federal-procurement-export-manifest.json").read_text())
    for pin in pins:
        if pin["format"] != "eforms":
            continue
        with verified_archive("data/raw/federal-procurement", pin) as archive:
            for key, document in select_xml(archive, wanted).items():
                if key in documents:
                    raise ValueError("Repeated buyer result UUID/version across monthly sources")
                documents[key] = {**document, "source_archive": pin["file"]}
                raw_xml[key] = archive.read(document["xml_file"])
    if set(documents) != set(wanted):
        raise ValueError("Known follow-up UUID/version set is incomplete in original exports")
    decisions = {r["publication_number"]: r for r in csv.DictReader(DECISIONS.open())}
    if len(decisions) != len(list(csv.DictReader(DECISIONS.open()))) or set(decisions) != {wanted[k]["publication-number"] for k in documents}:
        raise ValueError("Individual decisions do not cover every available original source")
    elections = {r["ags"]: r for r in json.loads(Path("outputs/nrw-election-register/events.json").read_text())}
    added, units, reviewed, pending = [], [], [], []
    for notice in notices:
        number = notice["publication-number"]
        if number not in decisions:
            pending.append({"publication_number": number, "reason": "original_full_notice_not_acquired",
                            "buyer_names_source": notice["buyer-name"].get("deu", [])})
            continue
        key = identity(notice["notice-identifier"], notice["notice-version"])
        source = documents[key]
        document = source["xml"]
        decision = decisions[number]
        if any(decision[k] != source[j] for k, j in [("xml_file", "xml_file"), ("xml_sha256", "xml_sha256"), ("source_archive", "source_archive")]):
            raise ValueError("Individual source pin changed")
        if normalized(document["procedure_identifier"]) != normalized(notice["procedure-identifier"]):
            raise ValueError("Follow-up XML/index procedure identity conflict")
        if sorted(normalized(b["name"]) for b in document["buyers"]) != sorted(normalized(n) for n in notice["buyer-name"]["deu"]):
            raise ValueError("Original XML/index buyer conflict")
        ags, kind = apply_scope(document, decision, ET.fromstring(raw_xml[key]))
        reviewed.append({"publication_number": number, "decision": kind, "ags": ags,
                         "source_archive": source["source_archive"], "xml_file": source["xml_file"],
                         "xml_sha256": source["xml_sha256"], "original_xml_result_units": len(document["units"])})
        if kind == REVIEW:
            pending.append({"publication_number": number, "reason": kind, "buyer_names_source": notice["buyer-name"]["deu"]})
        if ags is None:
            continue
        election = elections[ags]
        if not election["votes_and_winner_verified"] or not election["decisive_pair"]:
            raise ValueError("Municipal election identity is not source verified")
        added.append({"ags": ags, "buyer_name": normalized(document["buyers"][0]["name"]), "buyer_scope": kind,
                      "publication_number": number, "publication_date_source": notice["publication-date"],
                      "election_date": election["decisive_date"], "absolute_margin_pp": election["absolute_margin_pp"],
                      "winner_name_source": election["winner_name_source"], "source_fields": notice,
                      "gender_measurement": "unverified", "actual_term_assignment": "unverified"})
        for u in document["units"]:
            units.append({**u, "ags": ags, "buyer_scope": kind, "publication_number": number,
                          "notice_identifier": key[0], "notice_version": key[1],
                          "procedure_identifier": document["procedure_identifier"],
                          "source_archive": source["source_archive"], "xml_file": source["xml_file"],
                          "xml_sha256": source["xml_sha256"]})
    old = list(retained_records().values())
    combined = old + added
    if len({r["publication_number"] for r in combined}) != len(combined):
        raise ValueError("Buyer follow-up overlaps retained inventories")
    supported = [u for u in units if u["dated_total_supported"]]
    previous = json.loads(Path("outputs/nrw-federal-procurement/summary.json").read_text())
    summary = {"scope_queue_notices": len(queue), "index_shared_fields_unchanged": len(common),
               "scope_cases_original_xml_reviewed": len(reviewed), "new_retained_notices": len(added),
               "excluded_original_scope_cases": sum(r["decision"] in EXCLUDED for r in reviewed),
               "remaining_scope_cases": len(pending), "decision_counts": dict(Counter(r["decision"] for r in reviewed)),
               "combined_retained_result_notices": len(combined),
               "new_accepted_xml_result_units": len(units), "new_accepted_xml_result_statuses": dict(Counter(u["result_status"] for u in units)),
               "new_dated_total_supported_units": len(supported),
               "new_dated_total_distinct_notices": len({u["publication_number"] for u in supported}),
               "new_dated_total_municipal_elections": len({u["ags"] for u in supported}),
               "combined_observed_dated_total_units": previous["full_cohort_union_dated_total_units"] + len(supported),
               "main_treatment_assignments": 0, "deduplication_complete": False}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in [("records", combined), ("new-records", added), ("award-results", units),
                       ("scope-decisions", reviewed), ("scope-review", pending), ("summary", summary)]:
        (OUT / (name + ".json")).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-index", action="store_true")
    args = parser.parse_args()
    if args.download_index:
        index_snapshot(download=True)
    audit()


if __name__ == "__main__":
    main()
