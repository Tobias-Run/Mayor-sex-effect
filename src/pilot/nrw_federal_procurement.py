"""Audit pinned federal exports against the fixed 225-notice NRW inventory."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from bavaria_evidence_sources import normalized
from urllib.request import Request, urlopen

from federal_procurement import csv_rows, identity, parse_competition, parse_eforms, verified_archive
from nrw_procedure_audit import retained_records, snapshot

TABLES = ["notice.csv", "procedure.csv", "lot.csv", "organisation.csv", "procedureLotResult.csv",
          "receivedSubmissions.csv", "contract.csv", "strategicProcurement.csv", "changes.csv"]


def wanted_keys(notices):
    wanted = {}
    for row in notices:
        if row.get("notice-identifier") and row.get("notice-version") is not None:
            key = identity(row["notice-identifier"], row["notice-version"])
            if key in wanted:
                raise ValueError("Retained index contains duplicate notice UUID/version")
            wanted[key] = row
    return wanted


def select_csv(archive, wanted):
    selected = {key: defaultdict(list) for key in wanted}
    identifiers = {key[0] for key in wanted}
    for table in TABLES:
        for row in csv_rows(archive, table):
            # Other national records may use non-UUID identifiers. They are
            # outside this fixed exact-UUID acquisition, not malformed matches.
            if row["noticeIdentifier"].lower() not in identifiers:
                continue
            key = identity(row["noticeIdentifier"], row["noticeVersion"])
            if key in selected:
                selected[key][table].append(row)
    return {key: dict(tables) for key, tables in selected.items() if tables}


def select_xml(archive, wanted, parser=parse_eforms):
    result = {}
    for filename in archive.namelist():
        if Path(filename).name != filename or not filename.endswith(".xml"):
            raise ValueError("Unexpected eForms archive filename")
        try:
            key = identity(*Path(filename).stem.rsplit("-", 1))
        except (ValueError, TypeError):
            continue  # Non-UUID national records are outside the fixed cohort.
        if key not in wanted:
            continue
        raw = archive.read(filename)
        parsed = parser(raw)
        if identity(parsed["notice_identifier"], parsed["notice_version"]) != key:
            raise ValueError("XML identity differs from archive filename")
        if key in result:
            raise ValueError("Repeated XML notice UUID/version in one export")
        result[key] = {"xml": parsed, "xml_file": filename,
                       "xml_sha256": hashlib.sha256(raw).hexdigest(), "xml_bytes": len(raw)}
    return result


def competition_index(root, download=False):
    pin = json.loads(Path("docs/feasibility/federal-competition-ted-request-manifest.json").read_text())
    path = Path(root) / pin["file"]
    if download and not path.exists():
        request = Request(pin["url"], json.dumps(pin["request"]).encode(), headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=45) as response:
            if response.status != 200 or response.headers.get("x-amzn-waf-action") == "challenge":
                raise ValueError("Non-success or protected competition index response")
            raw = response.read()
        if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError("Mutable competition index changed; review a new snapshot")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    raw = path.read_bytes()
    if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
        raise ValueError("Competition index differs from reviewed pin")
    data = json.loads(raw)
    rows = data["notices"]
    if data.get("timedOut") or data["totalNoticeCount"] != pin["total_notice_count"] or len(rows) != data["totalNoticeCount"]:
        raise ValueError("Incomplete competition index")
    if {r["notice-identifier"] for r in rows} != set(pin["expected_notice_identifiers"]):
        raise ValueError("Competition index identity set changed")
    return {identity(r["notice-identifier"], r["notice-version"]): r for r in rows}


def compare_pdf_unit(unit, pdf_units):
    """Match existing PDF results by notice and lot, without adding duplicates."""
    candidates = [r for r in pdf_units if r["publication_number"] == unit["publication_number"]
                  and r.get("lot_number") in unit["lot_ids"]]
    if len(candidates) != 1:
        return {"pdf_comparison": "missing_or_ambiguous_pdf_unit"}
    pdf = candidates[0]
    fields = ["received_tenders", "contract_conclusion_date"]
    conflicts = [name for name in fields if pdf.get(name) is not None and unit.get(name) is not None
                 and pdf[name] != unit[name]]
    return {"pdf_comparison": "conflict_review" if conflicts else "nonmissing_fields_agree",
            "pdf_conflicting_fields": conflicts,
            "already_in_original_dated_total_cohort": pdf.get("received_tenders") is not None
            and pdf.get("contract_conclusion_date") is not None}


def audit(root, pins, out):
    _, notices = snapshot("retrieval.json")
    indexed = retained_records()
    wanted = wanted_keys(notices)
    csv_data = {}
    xml_data = {}
    competition_csv = {}
    competition_xml = {}
    procedure_ids = {n["procedure-identifier"] for n in wanted.values()}
    volume = []
    for pin in sorted(pins, key=lambda p: (p["format"] != "csv", p["file"])):
        with verified_archive(root, pin) as archive:
            if pin["format"] == "csv":
                selected = select_csv(archive, wanted)
                volume.append({"file": pin["file"], "format": "csv", "archive_members": len(archive.namelist()),
                               "notice_rows": sum(1 for _ in csv_rows(archive, "notice.csv")),
                               "retained_uuid_version_matches": len(selected)})
                for key, tables in selected.items():
                    if key in csv_data:
                        raise ValueError("Duplicate CSV UUID/version across reviewed monthly exports")
                    if len(tables.get("notice.csv", [])) != 1:
                        raise ValueError("CSV notice row missing or repeated")
                    csv_data[key] = {"tables": tables, "csv_source_file": pin["file"]}
                for row in csv_rows(archive, "notice.csv"):
                    if row["noticeType"] == "cn-standard" and row["procedureIdentifier"] in procedure_ids:
                        key = identity(row["noticeIdentifier"], row["noticeVersion"])
                        if key in competition_csv:
                            raise ValueError("Duplicate competition context UUID/version")
                        competition_csv[key] = {**row, "csv_source_file": pin["file"]}
            elif pin["format"] == "eforms":
                selected = select_xml(archive, wanted)
                volume.append({"file": pin["file"], "format": "eforms", "archive_members": len(archive.namelist()),
                               "retained_uuid_version_matches": len(selected)})
                for key, document in selected.items():
                    if key in xml_data:
                        raise ValueError("Duplicate XML UUID/version across reviewed monthly exports")
                    xml_data[key] = {**document, "xml_source_file": pin["file"]}
                for key, document in select_xml(archive, competition_csv, parser=parse_competition).items():
                    if key in competition_xml:
                        raise ValueError("Duplicate competition XML context UUID/version")
                    competition_xml[key] = {**document, "xml_source_file": pin["file"]}
            else:
                raise ValueError("Unsupported format in reviewed audit manifest")
    if set(csv_data) != set(wanted) or set(xml_data) != set(wanted):
        raise ValueError("Reviewed export cohort does not cover every retained UUID/version")
    context_index = competition_index(root)
    if set(context_index) != set(competition_csv) or set(competition_xml) != set(competition_csv):
        raise ValueError("Competition context CSV/XML/index identities disagree")
    context = []
    for key, row in competition_csv.items():
        xml = competition_xml[key]
        ted = context_index[key]
        if row["procedureIdentifier"] != xml["xml"]["procedure_identifier"] or ted["procedure-identifier"] != row["procedureIdentifier"]:
            raise ValueError("Competition context procedure identities disagree")
        if ted["notice-type"] != "cn-standard":
            raise ValueError("Competition context type mismatch")
        if {normalized(x) for x in ted["buyer-name"].get("deu", [])} != {normalized(b["name"]) for b in xml["xml"]["buyers"] if b["name"]}:
            raise ValueError("Competition original XML/TED buyer mismatch")
        context.append({"notice_identifier": key[0], "notice_version": key[1],
                        "publication_number": ted["publication-number"],
                        "procedure_identifier": row["procedureIdentifier"],
                        "ted_competition_publication_date_source": ted["publication-date"],
                        "csv_publication_date_source": row["publicationDate"],
                        "notice_issue_date_source": xml["xml"]["notice_issue_date_source"],
                        "requested_publication_date_source": xml["xml"]["requested_publication_date_source"],
                        "changed_notice_reference": xml["xml"]["changed_notice_reference"],
                        "buyers": xml["xml"]["buyers"], "csv_source_file": row["csv_source_file"],
                        "xml_source_file": xml["xml_source_file"], "xml_file": xml["xml_file"],
                        "xml_sha256": xml["xml_sha256"],
                        "linked_retained_result_publication_numbers": sorted(n["publication-number"] for n in wanted.values() if n["procedure-identifier"] == row["procedureIdentifier"]),
                        "municipal_beneficiary_scope": "phase_specific_review_pending",
                        "automatic_baseline_publication_selection": False})
    pdf_units = json.loads(Path("outputs/nrw-complete-ted/awards.json").read_text())
    old_retained = {r["publication_number"] for r in json.loads(Path("outputs/nrw-buyer-scope/records.json").read_text())}
    units = []
    records = []
    conversion_review = []
    for key, notice in sorted(wanted.items(), key=lambda item: item[1]["publication-number"]):
        number = notice["publication-number"]
        tables = csv_data[key]["tables"]
        document = xml_data[key]
        xml = document["xml"]
        main = tables["notice.csv"][0]
        if main["procedureIdentifier"] != xml["procedure_identifier"] or xml["procedure_identifier"] != notice.get("procedure-identifier"):
            raise ValueError("Procedure identity conflicts across federal XML/CSV/TED")
        if main["noticeType"] != "can-standard":
            raise ValueError("CSV notice type changed")
        # CSV organisation roles carry scoped buyer status, not a guessed first row.
        csv_buyers = sorted(r["organisationName"] for r in tables.get("organisation.csv", []) if r["organisationRole"] == "buyer")
        xml_buyers = sorted(b["name"] for b in xml["buyers"] if b["name"] is not None)
        csv_buyer_agreement = {normalized(x) for x in csv_buyers} == {normalized(x) for x in xml_buyers}
        ted_buyers = notice["buyer-name"].get("deu", [])
        if {normalized(x) for x in ted_buyers} != {normalized(x) for x in xml_buyers}:
            raise ValueError("Original XML buyer differs from retained TED scope for " + number)
        common = {"publication_number": number, "ags": indexed[number]["ags"],
                  "buyer_scope": indexed[number]["buyer_scope"], "notice_identifier": key[0],
                  "notice_version": key[1], "procedure_identifier": xml["procedure_identifier"],
                  "csv_source_file": csv_data[key]["csv_source_file"],
                  "xml_source_file": document["xml_source_file"], "xml_file": document["xml_file"],
                  "xml_sha256": document["xml_sha256"], "xml_bytes": document["xml_bytes"]}
        xml_count = sum(u["received_tenders"] is not None for u in xml["units"])
        csv_count = sum(r["receivedSubmissionsType"] == "tenders" for r in tables.get("receivedSubmissions.csv", []))
        csv_missing_types = sum(not r["receivedSubmissionsType"] for r in tables.get("receivedSubmissions.csv", []))
        if csv_missing_types or csv_count != xml_count or not csv_buyer_agreement:
            conversion_review.append({**common, "csv_blank_statistic_types": csv_missing_types,
                                      "csv_tenders_rows": csv_count, "xml_results_with_valid_total": xml_count,
                                      "csv_xml_buyer_names_agree": csv_buyer_agreement,
                                      "csv_buyer_rows_source": csv_buyers, "xml_buyer_names_source": xml_buyers})
        records.append({**common, "buyers": xml["buyers"], "customization_id": xml["customization_id"],
                        "csv_buyer_rows_source": csv_buyers,
                        "csv_xml_buyer_names_agree": csv_buyer_agreement,
                        "ted_result_notice_publication_date_source": notice["publication-date"],
                        "csv_publication_date_source": main["publicationDate"],
                        "notice_issue_date_source": xml["notice_issue_date_source"],
                        "requested_publication_date_source": xml["requested_publication_date_source"],
                        "changed_notice_reference": xml["changed_notice_reference"],
                        "strategic_procurement_csv_rows": tables.get("strategicProcurement.csv", []),
                        "result_unit_count": len(xml["units"]), "csv_statistic_types_missing": csv_missing_types})
        for u in xml["units"]:
            row = {**common, **u, "unit": "observed_award_lot_result",
                   "original_retained_cohort": number in old_retained,
                   "extension_retained_cohort": number not in old_retained}
            row.update(compare_pdf_unit(row, pdf_units))
            units.append(row)
    dated = [u for u in units if u["dated_total_supported"] and u["pdf_comparison"] != "conflict_review"]
    added = [u for u in dated if u["extension_retained_cohort"]]
    original_supplement = [u for u in dated if u["original_retained_cohort"] and not u.get("already_in_original_dated_total_cohort", False)]
    by_city = defaultdict(list)
    for u in added:
        by_city[u["ags"]].append(u)
    summary = {
        "retained_index_notices": len(notices), "index_notices_with_uuid_version": len(wanted),
        "retained_index_notices_without_uuid_version": len(notices) - len(wanted),
        "csv_monthly_exports": sum(p["format"] == "csv" for p in pins),
        "xml_monthly_exports": sum(p["format"] == "eforms" for p in pins),
        "csv_exact_notice_version_matches": len(csv_data), "xml_exact_notice_version_matches": len(xml_data),
        "xml_result_units": len(units), "xml_result_statuses": dict(Counter(u["result_status"] for u in units)),
        "xml_results_with_explicit_total": sum(u["received_tenders"] is not None for u in units),
        "xml_linkage_supported_award_results": sum(u["award_linkage_supported"] for u in units),
        "xml_dated_total_supported_units": len(dated),
        "xml_dated_total_units_in_original_cohort": sum(u["original_retained_cohort"] for u in dated),
        "xml_dated_total_units_matching_original_pdf": sum(u.get("already_in_original_dated_total_cohort", False) for u in dated),
        "original_cohort_additional_xml_result_units": len(original_supplement),
        "extension_new_dated_total_units": len(added),
        "extension_new_dated_total_distinct_notices": len({u["publication_number"] for u in added}),
        "extension_new_dated_total_election_events": len(by_city),
        "pdf_comparison_conflicts": sum(u["pdf_comparison"] == "conflict_review" for u in units),
        "csv_conversion_review_notices": len(conversion_review),
        "csv_blank_statistic_type_rows": sum(r["csv_blank_statistic_types"] for r in conversion_review),
        "csv_xml_buyer_role_conflict_notices": sum(not r["csv_xml_buyer_names_agree"] for r in conversion_review),
        "all_main_treatment_assignments": 0,
        "original_pdf_dated_total_units": sum(r.get("received_tenders") is not None and r.get("contract_conclusion_date") is not None for r in pdf_units),
        "full_cohort_union_dated_total_units": sum(r.get("received_tenders") is not None and r.get("contract_conclusion_date") is not None for r in pdf_units) + len(added) + len(original_supplement),
        "deduplication_complete": False,
        "competition_context_notices_csv_xml_and_ted": len(context),
        "competition_context_distinct_procedure_guids": len({r["procedure_identifier"] for r in context}),
        "competition_context_retained_result_notices_linked": len({n for r in context for n in r["linked_retained_result_publication_numbers"]}),
        "source_population": "Published result notices with exact UUID/version in the fixed acquisition inventory; not all German municipal purchases",
    }
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for name, data in [("records", records), ("award-results", units), ("conversion-review", conversion_review),
                       ("export-volume", volume), ("summary", summary)]:
        (out / (name + ".json")).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    (out / "competition-context.json").write_text(json.dumps(context, ensure_ascii=False, indent=2))
    with (out / "extension-concentration.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ags", "dated_total_units", "distinct_notices", "independent_election_events"])
        writer.writeheader()
        for ags, rows in sorted(by_city.items()):
            writer.writerow({"ags": ags, "dated_total_units": len(rows),
                             "distinct_notices": len({r["publication_number"] for r in rows}), "independent_election_events": 1})
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("docs/feasibility/federal-procurement-export-manifest.json"))
    parser.add_argument("--raw-root", type=Path, default=Path("data/raw/federal-procurement"))
    parser.add_argument("--out", type=Path, default=Path("outputs/nrw-federal-procurement"))
    parser.add_argument("--download-context", action="store_true", help="Acquire reviewed public competition index if absent")
    args = parser.parse_args()
    if args.download_context:
        competition_index(args.raw_root, download=True)
    audit(args.raw_root, json.loads(args.manifest.read_text()), args.out)


if __name__ == "__main__":
    main()
