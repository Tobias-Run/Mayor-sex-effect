"""Audit NRW competition-to-result timing without assigning mayoral treatment.

Pinned original legacy PDFs establish explicit previous-notice references. Original
eForms establish GUIDs and correction UUID/version links. TED indexed dates remain
publication dates; dispatch, requested publication and contract dates stay distinct.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

from bavaria_evidence_sources import normalized, verified_source
from federal_procurement import identity, ids_at, parse_competition, safe_xml, source_date, verified_archive
from nrw_federal_procurement import select_xml, wanted_keys
from nrw_procedure_audit import snapshot
from nrw_term_law import PERIOD_START

RAW = Path("data/raw/ted-nrw-buyer-followup")
OUT = Path("outputs/nrw-phase-linkage")
CITY_PREFIX = {"05158032": "Stadt Velbert", "05370012": "Stadt Geilenkirchen",
               "05962024": "Stadt Iserlohn", "05166032": "Stadt Viersen",
               "05978036": "Kreisstadt Unna", "05962060": "Stadt Werdohl",
               "05362024": "Stadt Frechen", "05566084": "Gemeinde Senden",
               "05366040": "Gemeinde Weilerswist"}


def pinned_index(manifest, root, download=False, pin_index=None):
    pin = json.loads(Path(manifest).read_text())
    if pin_index is not None:
        pin = pin[pin_index]
    path = Path(root) / pin["file"]
    if download and not path.exists():
        request = Request(pin["url"], json.dumps(pin["request"]).encode(),
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=45) as response:
            if response.status != 200 or response.headers.get("x-amzn-waf-action") == "challenge":
                raise ValueError("Non-success or protected phase index response")
            raw = response.read()
        if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError("Mutable phase index changed; review a new snapshot")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    raw = path.read_bytes()
    if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
        raise ValueError("Phase index differs from its pin")
    data = json.loads(raw)
    rows = data["notices"]
    if data.get("timedOut") or len(rows) != pin["total_notice_count"] or data["totalNoticeCount"] != len(rows):
        raise ValueError("Incomplete phase index")
    numbers = [r["publication-number"] for r in rows]
    if len(set(numbers)) != len(numbers):
        raise ValueError("Duplicate indexed publication number")
    if "expected_publication_numbers" in pin and set(numbers) != set(pin["expected_publication_numbers"]):
        raise ValueError("Phase index notice identities changed")
    if "procedure_identifiers_queried" in pin and any(r["procedure-identifier"] not in pin["procedure_identifiers_queried"] for r in rows):
        raise ValueError("Phase index contains an unqueried GUID")
    if any(r["notice-type"] != "cn-standard" for r in rows):
        raise ValueError("Phase context contains a non-competition notice")
    return rows


def same_city_buyers(names, ags):
    """A sole city contracting party; county and joint bodies stay outside."""
    prefix = CITY_PREFIX[ags]
    return len(names) == 1 and bool(re.match(re.escape(prefix) + r"(?:$|[\s,\-])", normalized(names[0])))


def previous_competition(text):
    """Read legacy Section IV.2.1 only, preserving the literal OJ reference."""
    sections = re.findall(r"IV\.2\.1\.(.*?)(?=IV\.2\.\d\.|Abschnitt V|\Z)", text, re.S)
    matches = [m for s in sections for m in re.finditer(
        r"Bekanntmachungsnummer im ABl\.:\s*(\d{4})/S\s+(\d{3})-(\d+)", s)]
    if len(matches) != 1:
        raise ValueError("Missing or ambiguous previous competition in Section IV.2.1")
    match = matches[0]
    return {"previous_publication_number": str(int(match[3])) + "-" + match[1],
            "previous_reference_source": normalized(match[0])}


def competition_graph(nodes):
    """Require one complete, acyclic, chronological parent graph for a root.

    A root is only the first documented call in this checked graph. It is not
    proof that no earlier publication exists in another notice family or index.
    """
    if not nodes:
        return {"graph_status": "competition_not_found", "candidate_competition_date": None}
    keys = [identity(n["notice_identifier"], n["notice_version"]) for n in nodes]
    if len(set(keys)) != len(keys):
        raise ValueError("Repeated competition UUID/version")
    by_key = dict(zip(keys, nodes))
    if len({(n["ags"], n["procedure_identifier"]) for n in nodes}) != 1:
        raise ValueError("Competition graph crosses city or procedure scope")
    parents, flags = {}, set()
    for key, node in by_key.items():
        ref = node.get("changed_notice_reference")
        if not ref:
            continue
        try:
            parent = identity(*ref.rsplit("-", 1))
        except (ValueError, TypeError):
            flags.add("invalid_parent_reference")
            continue
        parents[key] = parent
        if parent not in by_key:
            flags.add("missing_parent_version")
        elif by_key[parent]["competition_publication_date"] > node["competition_publication_date"]:
            flags.add("parent_published_after_child")
    for key in by_key:
        seen, current = set(), key
        while current in parents:
            if current in seen:
                flags.add("parent_cycle")
                break
            seen.add(current)
            current = parents[current]
    roots = [n for k, n in by_key.items() if k not in parents]
    if len(roots) != 1:
        flags.add("multiple_or_missing_roots")
    root = roots[0] if not flags else None
    return {"graph_status": "documented_root_supported" if root else "correction_graph_review_pending",
            "graph_flags": sorted(flags), "competition_notices": [n["publication_number"] for n in nodes],
            "correction_edges": len(parents),
            "candidate_competition_publication_number": root["publication_number"] if root else None,
            "candidate_competition_date": root["competition_publication_date"] if root else None,
            "earliest_ever_publication_verified": False}


def paired_units():
    pdf = json.loads(Path("outputs/nrw-complete-ted/awards.json").read_text())
    rows = [{**u, "observation_key": u["publication_number"] + ":pdf:" + u["layout"] + ":"
             + str(u["award_section"] if u["layout"] == "legacy" else u["lot_number"])}
            for u in pdf if u.get("contract_conclusion_date") and u.get("received_tenders") is not None]
    federal = json.loads(Path("outputs/nrw-federal-procurement/award-results.json").read_text())
    extra = [u for u in federal if u["dated_total_supported"] and u["pdf_comparison"] != "conflict_review"
             and (u["extension_retained_cohort"] or not u.get("already_in_original_dated_total_cohort", False))]
    extra += [u for u in json.loads(Path("outputs/nrw-buyer-followup/award-results.json").read_text())
              if u["dated_total_supported"]]
    rows += [{**u, "observation_key": u["publication_number"] + ":xml:" + u["result_id"]} for u in extra]
    if len({u["observation_key"] for u in rows}) != len(rows):
        raise ValueError("Repeated observation key; review before counting")
    expected = json.loads(Path("outputs/nrw-buyer-followup/summary.json").read_text())["combined_observed_dated_total_units"]
    if len(rows) != expected:
        raise ValueError("Phase cohort differs from the previous observed union")
    return rows


def phase_observation(unit, phase, election_date):
    published = phase.get("candidate_competition_date")
    concluded = unit["contract_conclusion_date"]
    status = "competition_missing_or_review_pending" if published is None else (
        "contract_before_documented_competition_review" if concluded < published else "documented_chronology_supported")
    return {"observation_key": unit["observation_key"], "publication_number": unit["publication_number"],
            "ags": unit["ags"], "received_tenders": unit["received_tenders"],
            "contract_conclusion_date": concluded, "candidate_competition_date": published,
            "candidate_competition_publication_number": phase.get("candidate_competition_publication_number"),
            "phase_evidence": phase.get("phase_evidence", "none"), "timing_status": status,
            "competition_before_decisive_election": published < election_date if published else None,
            "competition_before_council_boundary": published < PERIOD_START if published else None,
            "contract_before_council_boundary": concluded < PERIOD_START,
            "contract_lag_days": (date.fromisoformat(concluded) - date.fromisoformat(published)).days if published else None,
            "actual_term_assignment": "unverified", "main_treatment_assignment": "unverified",
            "automatic_award_deduplication": False}


def write_csv(path, rows, fields=None):
    if not fields:
        fields = list(rows[0])
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list, bool)) else v
                             for k, v in row.items() if k in fields})


def public_tables(records, phases, context, references, observations, summary):
    folder = Path("docs/feasibility")
    buyer_summary = json.loads(Path("outputs/nrw-buyer-followup/summary.json").read_text())
    metrics = []
    for stage, data in [("buyer_scope", buyer_summary), ("phase_linkage", summary)]:
        for key, value in data.items():
            if isinstance(value, dict):
                metrics += [{"stage": stage, "metric": key + "." + k, "value": v} for k, v in value.items()]
            else:
                metrics.append({"stage": stage, "metric": key, "value": value})
    write_csv(folder / "nrw-buyer-and-phase-summary.csv", metrics)
    concentration = []
    for ags in sorted({u["ags"] for u in observations}):
        units = [u for u in observations if u["ags"] == ags]
        concentration.append({"ags": ags, "municipality": CITY_PREFIX[ags], "observed_award_result_units": len(units),
                              "distinct_result_notices": len({u["publication_number"] for u in units}),
                              "documented_competition_and_contract_pairs": sum(u["timing_status"] == "documented_chronology_supported" for u in units),
                              "competition_before_council_boundary_units": sum(u["competition_before_council_boundary"] is True for u in units),
                              "main_treatment_assignments": 0})
    write_csv(folder / "nrw-buyer-and-phase-concentration.csv", concentration)
    links = []
    for number, record in sorted(records.items()):
        phase = phases.get(number, {})
        links.append({"publication_number": number, "ags": record["ags"],
                      "candidate_competition_publication_number": phase.get("candidate_competition_publication_number"),
                      "candidate_competition_date": phase.get("candidate_competition_date"),
                      "phase_evidence": phase.get("phase_evidence", "none"),
                      "graph_status": phase.get("graph_status", "explicit_previous_reference" if phase else "competition_not_found"),
                      "graph_flags_json": phase.get("graph_flags", []), "result_pdf_sha256": phase.get("result_pdf_sha256"),
                      "result_xml_sha256": phase.get("xml_sha256"),
                      "earliest_ever_publication_verified": False, "main_treatment_assignment": "unverified"})
    write_csv(folder / "nrw-phase-links.csv", links)
    write_csv(folder / "nrw-phase-observations.csv", observations)
    fields = ["publication_number", "ags", "notice_identifier", "notice_version", "procedure_identifier", "buyer_scope",
              "competition_publication_date_source", "competition_publication_date", "notice_issue_date_source",
              "requested_publication_date_source", "changed_notice_reference", "buyers", "source_archive", "xml_file", "xml_sha256"]
    write_csv(folder / "nrw-phase-competition-sources.csv", context, fields)
    write_csv(folder / "nrw-phase-legacy-references.csv", references)


def audit(write_public=False):
    records = {r["publication_number"]: r for r in json.loads(Path("outputs/nrw-buyer-followup/records.json").read_text())}
    _, enriched = snapshot("retrieval.json")
    result_index = {r["publication-number"]: r for r in enriched}
    result_index.update({n: r["source_fields"] for n, r in records.items() if n not in result_index})
    if set(result_index) != set(records):
        raise ValueError("Enriched phase index differs from retained scope")
    modern = pinned_index("docs/feasibility/nrw-phase-ted-request-manifest.json", RAW)
    legacy = {r["publication-number"]: r for r in pinned_index(
        "docs/feasibility/nrw-legacy-competition-ted-request-manifest.json", RAW)}
    previous = {r["publication-number"]: r for r in pinned_index(
        "docs/feasibility/nrw-procedure-ted-request-manifest.json", "data/raw/ted-nrw-procedures", pin_index=1)}
    guid_cities = defaultdict(set)
    for record in records.values():
        guid = record["source_fields"].get("procedure-identifier")
        if guid:
            guid_cities[guid].add(record["ags"])
    wanted, documents, result_xml = wanted_keys(modern), {}, {}
    result_rows = list(result_index.values())
    wanted_results = wanted_keys(result_rows)
    pins = json.loads(Path("docs/feasibility/federal-procurement-export-manifest.json").read_text())
    pins += json.loads(Path("docs/feasibility/nrw-phase-additional-export-manifest.json").read_text())
    for pin in pins:
        if pin["format"] != "eforms":
            continue
        with verified_archive("data/raw/federal-procurement", pin) as archive:
            for key, document in select_xml(archive, wanted, parser=parse_competition).items():
                if key in documents:
                    raise ValueError("Competition repeated across source archives")
                documents[key] = {**document, "source_archive": pin["file"]}
            for key, notice in wanted_results.items():
                filename = key[0] + "-" + str(key[1]).zfill(2) + ".xml"
                if filename in archive.namelist():
                    if key in result_xml:
                        raise ValueError("Result source repeated across archives")
                    raw = archive.read(filename)
                    xml = safe_xml(raw)
                    if identity(xml.findtext("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID"),
                                xml.findtext("{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}VersionID")) != key:
                        raise ValueError("Result XML notice identity changed")
                    result_xml[key] = {"refs": ids_at(xml, "cac:TenderingProcess/cac:NoticeDocumentReference/cbc:ID"),
                                       "xml_sha256": hashlib.sha256(raw).hexdigest(), "source_archive": pin["file"], "xml_file": filename}
    if set(documents) != set(wanted) or set(result_xml) != set(wanted_results):
        raise ValueError("Original competition/result UUID/version sources incomplete")
    context, groups = [], defaultdict(list)
    for key, index in wanted.items():
        source, xml = documents[key], documents[key]["xml"]
        guid = xml["procedure_identifier"]
        names = [b["name"] for b in xml["buyers"]]
        if guid != index["procedure-identifier"] or sorted(normalized(n) for n in names) != sorted(normalized(n) for n in index["buyer-name"]["deu"]):
            raise ValueError("Competition XML/index buyer or GUID conflict")
        cities = guid_cities.get(guid, set())
        ags = next(iter(cities)) if len(cities) == 1 else None
        in_scope = ags is not None and same_city_buyers(names, ags)
        row = {**xml, "publication_number": index["publication-number"], "ags": ags if in_scope else None,
               "competition_publication_date_source": index["publication-date"],
               "competition_publication_date": source_date(index["publication-date"]),
               "buyer_scope": "sole_city_buyer_aligned" if in_scope else "outside_retained_city_scope_or_review",
               "source_archive": source["source_archive"], "xml_file": source["xml_file"], "xml_sha256": source["xml_sha256"]}
        if row["competition_publication_date"] is None:
            raise ValueError("Indexed competition publication date invalid")
        context.append(row)
        if in_scope:
            groups[(ags, guid)].append(row)
    graphs = [{"ags": ags, "procedure_identifier": guid, **competition_graph(nodes)} for (ags, guid), nodes in sorted(groups.items())]
    graph_map = {(g["ags"], g["procedure_identifier"]): g for g in graphs}
    phases = {}
    for number, record in records.items():
        guid = record["source_fields"].get("procedure-identifier")
        if (record["ags"], guid) in graph_map:
            phases[number] = {**graph_map[(record["ags"], guid)], "phase_evidence": "original_eforms_guid_and_correction_graph"}
    # The previous competition is linked by the literal PDF reference, not a local
    # contract label, supplier name or guessed match from title text.
    pdf_notices = json.loads(Path("outputs/nrw-complete-ted/notice-audits.json").read_text())
    legacy_results = {u["publication_number"] for u in pdf_notices if u["layout"] == "legacy"}
    sources = {s["publication_number"]: s for s in csv.DictReader(Path("docs/feasibility/nrw-complete-ted-source-manifest.csv").open())}
    references = []
    for number in sorted(legacy_results):
        source = sources[number]
        path = verified_source(source, False, Path("data/raw/nrw-complete-ted"))
        if len(path.read_bytes()) != int(source["bytes"]):
            raise ValueError("Legacy PDF byte count changed")
        text = subprocess.run(["pdftotext", "-layout", str(path), "-"], check=True, capture_output=True, text=True).stdout
        if not re.match(r"\s*" + re.escape(number) + r"\s+-\s+Ergebnis\b", text):
            raise ValueError("Legacy PDF header identity absent: " + number)
        ref = previous_competition(text)
        index = legacy[ref["previous_publication_number"]]
        record = records[number]
        if not same_city_buyers(index["buyer-name"]["deu"], record["ags"]):
            raise ValueError("Legacy previous competition buyer/city conflict")
        day = source_date(index["publication-date"])
        if day is None or day > source_date(record["publication_date_source"]):
            raise ValueError("Legacy competition/result chronology conflict")
        row = {"publication_number": number, "ags": record["ags"], **ref,
               "candidate_competition_publication_number": index["publication-number"], "candidate_competition_date": day,
               "competition_publication_date_source": index["publication-date"], "previous_buyer_names_source": index["buyer-name"]["deu"],
               "phase_evidence": "original_result_pdf_reference_and_indexed_competition_metadata",
               "result_pdf_sha256": source["sha256"], "earliest_ever_publication_verified": False}
        phases[number] = row
        references.append(row)
    if {r["previous_publication_number"] for r in references} != set(legacy):
        raise ValueError("Legacy context differs from original references")
    explicit = []
    for key, source in result_xml.items():
        number = wanted_results[key]["publication-number"]
        for ref in sorted(set(source["refs"])):
            if ref not in previous:
                raise ValueError("Unreviewed explicit eForms previous notice")
            index, record = previous[ref], records[number]
            if not same_city_buyers(index["buyer-name"]["deu"], record["ags"]):
                raise ValueError("Explicit previous competition buyer conflict")
            day = source_date(index["publication-date"])
            if day is None or day > source_date(record["publication_date_source"]):
                raise ValueError("Explicit previous notice date conflict")
            row = {"publication_number": number, "ags": record["ags"], **source,
                   "previous_publication_number": ref, "candidate_competition_publication_number": ref,
                   "candidate_competition_date": day,
                   "phase_evidence": "original_result_xml_reference_and_indexed_competition_metadata",
                   "earliest_ever_publication_verified": False}
            old = phases.get(number, {})
            if old.get("candidate_competition_date") not in {None, day}:
                raise ValueError("Explicit reference and GUID graph dates differ")
            phases[number] = row
            explicit.append(row)
    observations = [phase_observation(u, phases.get(u["publication_number"], {}), records[u["publication_number"]]["election_date"])
                    for u in paired_units()]
    scope = Counter(r["buyer_scope"] for r in context)
    summary = {"retained_result_notices": len(records), "original_result_xml_notices": len(result_xml),
               "original_competition_xml_notices": len(context),
               "original_competition_distinct_guids": len({r["procedure_identifier"] for r in context}),
               "competition_scope_counts": dict(scope), "retained_city_competition_groups": len(graphs),
               "correction_graph_statuses": dict(Counter(g["graph_status"] for g in graphs)),
               "correction_graph_flags": dict(Counter(f for g in graphs for f in g["graph_flags"])),
               "explicit_legacy_previous_competition_links": len(references), "explicit_eforms_previous_competition_links": len(explicit),
               "observed_dated_total_units": len(observations), "observed_municipal_elections": len({u["ags"] for u in observations}),
               "phase_timing_statuses": dict(Counter(u["timing_status"] for u in observations)),
               "phase_evidence_counts": dict(Counter(u["phase_evidence"] for u in observations)),
               "competition_before_council_boundary_units": sum(u["competition_before_council_boundary"] is True for u in observations),
               "competition_before_decisive_election_units": sum(u["competition_before_decisive_election"] is True for u in observations),
               "contract_before_council_boundary_units": sum(u["contract_before_council_boundary"] for u in observations),
               "main_treatment_assignments": 0, "deduplication_complete": False}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in [("competition-context", context), ("correction-graphs", graphs), ("legacy-references", references),
                       ("explicit-eforms-references", explicit), ("observations", observations), ("summary", summary)]:
        (OUT / (name + ".json")).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    if write_public:
        public_tables(records, phases, context, references, observations, summary)
    print(json.dumps(summary, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-index", action="store_true")
    parser.add_argument("--write-public-tables", action="store_true", help="Regenerate reviewed derived tables in docs/feasibility")
    args = parser.parse_args()
    if args.download_index:
        for manifest in ["nrw-phase-ted-request-manifest.json", "nrw-legacy-competition-ted-request-manifest.json"]:
            pinned_index(Path("docs/feasibility") / manifest, RAW, download=True)
    audit(args.write_public_tables)


if __name__ == "__main__":
    main()
