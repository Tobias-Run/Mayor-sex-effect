"""Audit NRW procedure-specific timing and source-bounded mayoral evidence.

No prior-call procedure is distinct from a missing competition date. A matching
title never overrides conflicting GUIDs. Procedure categories and outcome samples
remain separate; no main-study treatment or automatic sample choice is assigned.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen

from bavaria_evidence_sources import html_text, normalized, verified_source
from federal_procurement import NS, identity, ids_at, parse_competition, safe_xml, verified_archive
from nrw_federal_procurement import select_xml, wanted_keys
from nrw_phase_linkage import paired_units, same_city_buyers, write_csv
from nrw_procedure_audit import snapshot

OUT = Path("outputs/nrw-procedure-scope")
RAW = Path("data/raw/nrw-procedure-term-followup")
SOURCES = Path("docs/feasibility/nrw-procedure-term-followup-source-manifest.csv")
CANDIDATES = Path("docs/feasibility/nrw-phase-candidate-ted-request-manifest.json")


def procedure_fields(root):
    codes = ids_at(root, "cac:TenderingProcess/cbc:ProcedureCode")
    if len(codes) != 1:
        raise ValueError("Missing or multiple primary procedure codes")
    reasons = ids_at(root, "cac:TenderingProcess/cbc:ProcessReasonCode")
    if len(reasons) > 1:
        raise ValueError("Multiple primary process reason codes")
    return {"procedure_code_source": codes[0], "process_reason_codes_source": reasons,
            "process_reason_texts_source": ids_at(root, "cac:TenderingProcess/cbc:ProcessReason"),
            "no_prior_call_procedure": codes[0] == "neg-wo-call",
            "italian_direct_award_equivalence_verified": False}


def legacy_procedure(text):
    parts = re.findall(r"IV\.1\.1\.(.*?)(?=IV\.1\.\d\.|IV\.2\.|Abschnitt V|\Z)", text, re.S)
    names = [("Nichtoffenes Verfahren", "restricted"), ("Offenes Verfahren", "open"),
             ("Verhandlungsverfahren ohne", "neg-wo-call"), ("Verhandlungsverfahren", "neg-w-call")]
    matches = [(phrase, code) for part in parts for phrase, code in names if phrase in part]
    # A more specific no-call label also contains the general negotiated label.
    if any(code == "neg-wo-call" for _, code in matches):
        matches = [(phrase, code) for phrase, code in matches if code != "neg-w-call"]
    if len(matches) != 1:
        raise ValueError("Missing or ambiguous legacy procedure in Section IV.1.1")
    phrase, code = matches[0]
    return {"procedure_code_source": code, "procedure_type_quote_source": phrase,
            "procedure_type_locator": "legacy Section IV.1.1", "no_prior_call_procedure": code == "neg-wo-call"}


def timing_disposition(procedure_code, previous_timing_status):
    if procedure_code == "neg-wo-call":
        return "no_prior_call_procedure_requires_separate_timing_rule"
    if previous_timing_status == "documented_chronology_supported":
        return "documented_competition_chronology_supported"
    return "competition_identity_or_date_review_pending"


def title_candidate(result, candidate):
    title = normalized(result.get("title-proc", {}).get("deu", ""))
    other = normalized(candidate.get("title-proc", {}).get("deu", ""))
    if not title or title != other or not same_city_buyers(candidate["buyer-name"]["deu"], result["ags"]):
        return "title_or_city_mismatch"
    if result.get("procedure-identifier") != candidate.get("procedure-identifier"):
        return "same_city_title_but_guid_conflict_review"
    return "same_city_title_and_guid_candidate_review"


def term_claims(raw):
    text = {key: html_text(value) for key, value in raw.items()}
    viersen = "Zwei Amtszeiten lang, von 2015 bis 2025, war Sabine Anemüller Bürgermeisterin der Stadt Viersen und Chefin der Stadtverwaltung."
    if viersen not in text["viersen-anemueller-farewell"] or "Ausgabe November 2025" not in text["viersen-anemueller-farewell"]:
        raise ValueError("Official Viersen two-term/year statement changed")
    unna = "Werner Kolter (75) war von 2004 bis 2020 Bürgermeister in Unna"
    if unna not in text["unna-predecessors"]:
        raise ValueError("Named Unna predecessor year interval changed")
    oath = "vereidigte Wigant in der konstituierenden Ratssitzung am Donnerstag, 20. November"
    if oath not in text["unna-oath-2025"] or "Bürgermeister Dirk Wigant ist nach seiner Wiederwahl im September" not in text["unna-oath-2025"]:
        raise ValueError("Unna reelection/oath context changed")
    if "2025_11_20_Konstituierung_Rat_BM_Tibbe_Amtskette.jpg" not in raw["unna-oath-2025"]:
        raise ValueError("Unna oath year from the accompanying municipal media filename changed")
    return [
        {"ags": "05166032", "person_name_source": "Sabine Anemüller", "source_id": "viersen-anemueller-farewell",
         "evidence_kind": "official_two_term_history_with_year_boundaries", "source_quote": viersen,
         "start_year_source": 2015, "end_year_source": 2025, "statement_period_source": "2025-11",
         "boundary_precision": "year", "actual_2020_renewal_date": None, "actual_entry_date": None,
         "first_day_out_of_office": None, "main_treatment_assignment": "unverified"},
        {"ags": "05978036", "person_name_source": "Werner Kolter", "source_id": "unna-predecessors",
         "evidence_kind": "official_predecessor_history_with_year_boundaries", "source_quote": unna,
         "start_year_source": 2004, "end_year_source": 2020, "statement_period_source": None,
         "boundary_precision": "year", "actual_2020_renewal_date": None, "actual_entry_date": None,
         "first_day_out_of_office": None, "main_treatment_assignment": "unverified"},
        {"ags": "05978036", "person_name_source": "Dirk Wigant", "source_id": "unna-oath-2025",
         "evidence_kind": "official_oath_after_reelection", "source_quote": oath,
         "oath_event_date": "2025-11-20", "event_year_basis": "municipal media filename; day and month in article text",
         "boundary_precision": "event_day_not_term_boundary", "actual_2020_renewal_date": None, "actual_entry_date": None,
         "first_day_out_of_office": None, "main_treatment_assignment": "unverified"}]


def candidate_index(download=False):
    pins = json.loads(CANDIDATES.read_text())
    snapshots = []
    for pin in pins:
        path = Path("data/raw/ted-nrw-phase-followup", pin["file"])
        if download and not path.exists():
            request = Request(pin["url"], json.dumps(pin["request"]).encode(), headers={"Content-Type": "application/json"})
            with urlopen(request, timeout=45) as response:
                if response.status != 200 or response.headers.get("x-amzn-waf-action") == "challenge":
                    raise ValueError("Protected or non-success candidate index response")
                raw = response.read()
            if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
                raise ValueError("Mutable candidate index changed; review before updating its pin")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        raw = path.read_bytes()
        if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError("Candidate search differs from its pin")
        data = json.loads(raw)
        if data.get("timedOut") or len(data["notices"]) != data["totalNoticeCount"] or data["totalNoticeCount"] != pin["total_notice_count"]:
            raise ValueError("Incomplete candidate discovery query")
        if {r["publication-number"] for r in data["notices"]} != set(pin["expected_publication_numbers"]):
            raise ValueError("Candidate discovery identities changed")
        snapshots.append(data["notices"])
    return snapshots


def audit(write_public=False, download=False):
    records = {r["publication_number"]: r for r in json.loads(Path("outputs/nrw-buyer-followup/records.json").read_text())}
    _, enriched = snapshot("retrieval.json")
    enriched += [r["source_fields"] for n, r in records.items() if n not in {x["publication-number"] for x in enriched}]
    wanted = wanted_keys(enriched)
    searches = candidate_index(download)
    competitions = {r["publication-number"]: r for rows in searches for r in rows if r["notice-type"] == "cn-standard"}
    candidate_wanted = wanted_keys(list(competitions.values()))
    source_rows, candidate_documents = {}, {}
    pins = json.loads(Path("docs/feasibility/federal-procurement-export-manifest.json").read_text())
    for pin in pins:
        if pin["format"] != "eforms":
            continue
        with verified_archive("data/raw/federal-procurement", pin) as archive:
            for key, source in select_xml(archive, wanted).items():
                number = wanted[key]["publication-number"]
                if number in source_rows:
                    raise ValueError("Repeated result XML source")
                root = safe_xml(archive.read(source["xml_file"]))
                if source["xml"]["procedure_identifier"] != wanted[key]["procedure-identifier"]:
                    raise ValueError("Procedure XML/index GUID conflict")
                names = [b["name"] for b in source["xml"]["buyers"]]
                if sorted(normalized(n) for n in names) != sorted(normalized(n) for n in wanted[key]["buyer-name"]["deu"]):
                    raise ValueError("Result XML/index buyer conflict")
                field = procedure_fields(root)
                indexed = records[number]["source_fields"].get("procedure-type")
                source_rows[number] = {"publication_number": number, "ags": records[number]["ags"], **field,
                    "indexed_procedure_type": indexed, "source_index_type_relation": "indexed_type_absent" if indexed is None else
                    "same_literal_code" if indexed == field["procedure_code_source"] else "different_source_codes_review",
                    "procedure_type_locator": "original XML cac:TenderingProcess/cbc:ProcedureCode",
                    "source_archive": pin["file"], "xml_file": source["xml_file"], "xml_sha256": source["xml_sha256"],
                    "actual_term_assignment": "unverified"}
            for key, source in select_xml(archive, candidate_wanted, parser=parse_competition).items():
                number = candidate_wanted[key]["publication-number"]
                if number in candidate_documents:
                    raise ValueError("Repeated competition source")
                if source["xml"]["procedure_identifier"] != candidate_wanted[key]["procedure-identifier"]:
                    raise ValueError("Candidate XML/index GUID conflict")
                candidate_documents[number] = {**source, "source_archive": pin["file"]}
    if len(source_rows) != len(wanted):
        raise ValueError("Retained result XML coverage incomplete")
    # Section IV.1.1 supplies an independent original classification for legacy
    # results. The already linked original competition disambiguates general
    # legacy negotiated wording; no-call forms are never inferred from dates.
    notices = json.loads(Path("outputs/nrw-complete-ted/notice-audits.json").read_text())
    legacy_sources = {r["publication_number"]: r for r in csv.DictReader(Path("docs/feasibility/nrw-complete-ted-source-manifest.csv").open())}
    for notice in notices:
        if notice["layout"] != "legacy":
            continue
        number = notice["publication_number"]
        pin = legacy_sources[number]
        path = verified_source(pin, False, Path("data/raw/nrw-complete-ted"))
        if path.stat().st_size != int(pin["bytes"]):
            raise ValueError("Legacy source byte count changed")
        text = subprocess.run(["pdftotext", "-layout", str(path), "-"], check=True, capture_output=True, text=True).stdout
        field = legacy_procedure(text)
        indexed = records[number]["source_fields"]["procedure-type"]
        if field["procedure_code_source"] != indexed:
            raise ValueError("Legacy original/index procedure classification conflict")
        source_rows[number] = {"publication_number": number, "ags": records[number]["ags"], **field,
                              "indexed_procedure_type": indexed, "source_index_type_relation": "same_literal_code",
                              "result_pdf_sha256": pin["sha256"], "actual_term_assignment": "unverified"}
    candidate_rows = []
    _, index_rows = snapshot("retrieval.json")
    by_number = {r["publication-number"]: r for r in index_rows}
    for number in ["126957-2024", "196766-2024"]:
        result = {**by_number[number], "ags": records[number]["ags"]}
        for candidate in competitions.values():
            status = title_candidate(result, candidate)
            if status == "title_or_city_mismatch":
                continue
            original = candidate_documents.get(candidate["publication-number"])
            if original is None:
                raise ValueError("Matching candidate lacks its original competition XML")
            if not same_city_buyers([b["name"] for b in original["xml"]["buyers"]], result["ags"]):
                raise ValueError("Candidate original buyer/city conflict")
            candidate_rows.append({"result_publication_number": number, "ags": result["ags"],
                "candidate_competition_publication_number": candidate["publication-number"],
                "candidate_publication_date_source": candidate["publication-date"],
                "result_procedure_guid": result["procedure-identifier"], "candidate_procedure_guid": candidate["procedure-identifier"],
                "title_source": candidate["title-proc"]["deu"], "link_status": status,
                "candidate_xml_file": original["xml_file"], "candidate_xml_sha256": original["xml_sha256"],
                "candidate_source_archive": original["source_archive"], "automatic_procedure_merge": False,
                "supported_baseline_date_added": False})
    previous = {u["observation_key"]: u for u in json.loads(Path("outputs/nrw-phase-linkage/observations.json").read_text())}
    observations = []
    for unit in paired_units():
        number = unit["publication_number"]
        row, prior = source_rows[number], previous[unit["observation_key"]]
        observations.append({"observation_key": unit["observation_key"], "publication_number": number, "ags": unit["ags"],
            "procedure_code_source": row["procedure_code_source"], "procedure_type_locator": row["procedure_type_locator"],
            "received_tenders": unit["received_tenders"], "contract_conclusion_date": unit["contract_conclusion_date"],
            "candidate_competition_date": prior["candidate_competition_date"], "previous_timing_status": prior["timing_status"],
            "timing_disposition": timing_disposition(row["procedure_code_source"], prior["timing_status"]),
            "bidder_outcome_sample_selection": "not_prespecified", "main_treatment_assignment": "unverified"})
    sources = {r["id"]: r for r in csv.DictReader(SOURCES.open())}
    source_paths = {key: verified_source(pin, download, RAW) for key, pin in sources.items()}
    if any(source_paths[key].stat().st_size != int(pin["bytes"]) for key, pin in sources.items()):
        raise ValueError("Primary methods/term source byte count changed")
    claims = term_claims({key: source_paths[key].read_text() for key in ["viersen-anemueller-farewell", "unna-predecessors", "unna-oath-2025"]})
    italian = subprocess.run(["pdftotext", "-layout", str(source_paths["italy-rp623"]), "-"], check=True, capture_output=True, text=True).stdout
    pages = italian.split("\f")
    if not any("Open&Negotiated" in p and "N. Bidders" in p and "Table 3: Bidders in procurement auctions" in p for p in pages):
        raise ValueError("Italian Table 3 bidder-sample definition changed")
    if not any("Direct award" in p and "Competitive procedure" in p and "Table 2: Type of procedure" in p for p in pages):
        raise ValueError("Italian Table 2 procedure-choice sample changed")
    nominations = subprocess.run(["pdftotext", "-layout", str(source_paths["werdohl-election-proposals-2020"]), "-"], check=True, capture_output=True, text=True).stdout
    mayor_section = nominations.split("A. Wahlvorschläge für das Amt der Bürgermeisterin/des Bürgermeisters", 1)[1].split("B. Wahlvorschläge", 1)[0]
    if not all(x in mayor_section for x in ["Voßloh, Silvia", "Industriekauffrau", "Späinghaus, Andreas", "Groß- und Außenhandels-", "kaufmann"]):
        raise ValueError("Official Werdohl candidate/occupation presentation changed")
    if "Sitzung am\n30.07.2020" not in nominations or "Werdohl, den 30.07.2020" not in nominations:
        raise ValueError("Werdohl nomination document date changed")
    finalist = next(r for r in json.loads(Path("outputs/nrw-election-register/events.json").read_text()) if r["ags"] == "05962060")
    nomination_names = {"Voßloh, Silvia", "Späinghaus, Andreas"}
    # The official election file has one space before the comma in Späinghaus's
    # name. Normalize comma whitespace only; retain both original spellings.
    official_names = {re.sub(r"\s*,\s*", ", ", c["candidate_name_source"]) for c in finalist["candidates"]}
    if nomination_names != official_names:
        raise ValueError("Werdohl nomination identities differ from official election finalists")
    presentations = [{"ags": "05962060", "candidate_name_source": name,
        "official_election_name_source": next(c["candidate_name_source"] for c in finalist["candidates"]
            if re.sub(r"\s*,\s*", ", ", c["candidate_name_source"]) == name),
        "occupation_presentation_source": occupation, "evidence_kind": "official_dated_nomination_occupation_presentation",
        "source_id": "werdohl-election-proposals-2020", "source_locator": "Section A mayoral nominations, PDF page 1",
        "document_signature_date_source": "2020-07-30", "source_filename_date_lead": "2020-08-14",
        "registry_gender_field": False, "main_treatment_assignment": "unverified"}
        for name, occupation in [("Voßloh, Silvia", "Industriekauffrau"),
                                  ("Späinghaus, Andreas", "Groß- und Außenhandels- kaufmann")]]
    summary = {"retained_result_notices": len(records), "original_result_xml_notices": len(wanted),
        "original_legacy_result_pdf_notices": sum(n["layout"] == "legacy" for n in notices),
        "original_procedure_type_notices": len(source_rows),
        "original_xml_procedure_code_counts": dict(Counter(r["procedure_code_source"] for r in source_rows.values() if "xml_file" in r)),
        "original_xml_index_type_relations": dict(Counter(r["source_index_type_relation"] for r in source_rows.values() if "xml_file" in r)),
        "observed_dated_total_units": len(observations),
        "observed_unit_procedure_code_counts": dict(Counter(r["procedure_code_source"] for r in observations)),
        "observed_unit_timing_dispositions": dict(Counter(r["timing_disposition"] for r in observations)),
        "same_title_different_guid_candidates": len(candidate_rows), "new_supported_competition_dates": 0,
        "official_term_or_oath_claims": len(claims), "new_certified_2020_entry_dates": 0,
        "official_2020_werdohl_finalist_presentations": len(nomination_names), "main_treatment_assignments": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in [("procedures", list(source_rows.values())), ("observations", observations), ("candidate-links", candidate_rows),
                       ("term-claims", claims), ("candidate-presentations", presentations), ("summary", summary)]:
        (OUT / (name + ".json")).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    if write_public:
        folder = Path("docs/feasibility")
        write_csv(folder / "nrw-procedure-scope-summary.csv", [{"metric": k, "value": v} for k, v in summary.items()])
        fields = list(dict.fromkeys(k for r in source_rows.values() for k in r))
        write_csv(folder / "nrw-procedure-type-sources.csv", list(source_rows.values()), fields)
        write_csv(folder / "nrw-procedure-timing-dispositions.csv", observations)
        write_csv(folder / "nrw-phase-conflicting-candidates.csv", candidate_rows)
        fields = list(dict.fromkeys(k for r in claims for k in r))
        write_csv(folder / "nrw-term-claim-followup.csv", claims, fields)
        write_csv(folder / "nrw-werdohl-nomination-presentations.csv", presentations)
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-public-tables", action="store_true")
    parser.add_argument("--download", action="store_true", help="Retrieve independently public pinned primary sources and candidate index snapshots if absent")
    args = parser.parse_args()
    audit(args.write_public_tables, args.download)
