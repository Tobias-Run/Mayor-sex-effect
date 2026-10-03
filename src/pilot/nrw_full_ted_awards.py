"""Audit scoped legacy and eForm results for the expanded NRW municipal pilot.

Keep total tenders distinct from electronic/SME subsets, selection dates from
contract dates, reported strategic aims from award criteria, and nominal prices
from usable monetary outcomes. Unsupported layouts remain explicit review cases.
"""
import argparse
import csv
import json
import re
import subprocess
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from bavaria_evidence_sources import normalized, verified_source
from bavaria_legacy_ted_awards import euro, parse_legacy_awards
from nrw_buyer_scope import MANIFEST, ROOT, fulltext_buyers
from nrw_legacy_ted_awards import result_status

OUT = Path("outputs/nrw-full-ted")


def unique_optional(pattern, text):
    values = re.findall(pattern, text)
    if len(values) > 1:
        raise ValueError("Multiple scoped fields require contract/lot review: " + pattern)
    return values[0] if values else None


def parse_eform_results(text, number, buyers):
    text = normalized(re.sub(re.escape(number) + r"\s+Page \d+/\d+", " ", text))
    if set(fulltext_buyers(text, number)) != set(buyers):
        raise ValueError("eForm buyer identity differs from reviewed scope")
    lots = re.findall(r"5\.1\. Los: (LOT-\d+) (.*?)(?=5\.1\. Los:|6\. Ergebnisse)", text)
    if not lots or len({key for key, _ in lots}) != len(lots):
        raise ValueError("Missing or duplicate eForm lot definitions")
    definitions = dict(lots)
    results = re.findall(r"6\.1\. Ergebnis, Los[-– ]+Kennung: (LOT-\d+) (.*?)(?=6\.1\. Ergebnis, Los|8\. Organisationen)", text)
    if not results or len({key for key, _ in results}) != len(results):
        raise ValueError("Missing or duplicate eForm result sections")
    rows, audits = [], []
    for lot, section in results:
        if lot not in definitions:
            raise ValueError("Result lot has no matching definition")
        definition = definitions[lot]
        status = unique_optional(r"Status der Preisträgerauswahl: (.*?)(?=6\.1\.\d+\.)", section)
        if status is None:
            raise ValueError("Missing explicit eForm result status")
        status = status.strip()
        if status == "Ein Wettbewerbsgewinner wurde noch nicht ermittelt, der Wettbewerb ist noch nicht abgeschlossen.":
            audits.append({"lot_number": lot, "status": "pending_no_award_yet", "source_quote": status})
            continue
        if status.startswith(("Es wurde kein Gewinner ermittelt", "Es wurde kein Wettbewerbsgewinner ermittelt, und der Wettbewerb ist abgeschlossen.")):
            audits.append({"lot_number": lot, "status": "not_awarded", "source_quote": status})
            continue
        if status != "Es wurde mindestens ein Gewinner ermittelt.":
            raise ValueError("Unrecognized eForm result status: " + status)
        winner = unique_optional(r"6\.1\.2\. Informationen über die Gewinner (.*?)(?=6\.1\.\d+\.|$)", section)
        if winner is None:
            raise ValueError("Awarded status lacks a winner section; unsuccessful bids cannot supply award outcomes")
        if winner.count("Informationen zum Auftrag:") > 1:
            raise ValueError("Multiple contracts within one lot need separate contract linkage")
        date_raw = unique_optional(r"Datum des Vertragsabschlusses: (\d{2}/\d{2}/\d{4})", winner)
        contract_date = datetime.strptime(date_raw, "%d/%m/%Y").date().isoformat() if date_raw else None
        selection_raw = unique_optional(r"Datum der Auswahl des Gewinners: (\d{2}/\d{2}/\d{4})", winner)
        count_raw = unique_optional(r"Art der eingegangenen Einreichungen: Angebote Anzahl der eingegangenen Angebote oder Teilnahmeanträge: (\d+)\b", section)
        count = int(count_raw) if count_raw is not None else None
        if count == 0:
            raise ValueError("Awarded result with zero total tenders requires review")
        value_raw = unique_optional(r"Wert des Angebots: ([\d ,.]+) EUR", winner)
        value = str(euro(value_raw)) if value_raw else None
        strategy = unique_optional(r"Ziel der strategischen Auftragsvergabe: (.*?)(?=5\.1\.[\d]+\.)", definition)
        criterion = unique_optional(r"5\.1\.10\. Zuschlagskriterien (.*?)(?=5\.1\.[\d]+\.)", definition)
        rows.append({"publication_number": number, "lot_number": lot, "unit": "awarded_lot_result",
                     "contract_conclusion_date": contract_date, "received_tenders": count, "award_value_eur": value,
                     "winner_selection_date_source": selection_raw,
                     "contract_date_source_quote": "Datum des Vertragsabschlusses: " + date_raw if date_raw else None,
                     "received_tenders_source_quote": "Art der eingegangenen Einreichungen: Angebote; Anzahl: " + count_raw if count_raw else None,
                     "strategic_goal_source": strategy.strip() if strategy else None,
                     "award_criteria_source": criterion.strip() if criterion else None,
                     "responsibility_assignment": "unverified"})
        audits.append({"lot_number": lot, "status": "awarded", "total_tender_count_present": count is not None,
                       "contract_date_present": contract_date is not None,
                       "strategic_statement_is_not_award_criterion": True})
    if set(definitions) != {key for key, _ in results}:
        raise ValueError("Some defined eForm lots lack reviewed results")
    return rows, audits


def monetary_status(value):
    if value is None:
        return "not_reported"
    amount = Decimal(value)
    if amount == 1:
        return "nominal_one_euro_needs_review"
    if amount == Decimal("0.01"):
        return "nominal_one_cent_needs_review"
    if amount == 0:
        return "zero_value_needs_review"
    return "reported_not_independently_validated"


def legacy_lot_definition_audit(text, number, rows):
    """Flag explicit award labels absent from Section II; retain observed results."""
    text = normalized(re.sub(re.escape(number) + r"\s+Page \d+/\d+", " ", text))
    before = text.split("Abschnitt V: Auftragsvergabe")[0]
    partition = unique_optional(r"Aufteilung des Auftrags in Lose: (ja|nein)", before)
    labels = re.findall(r"Los-Nr\.: (?:Los-Nr\. )?(\d+)\b", before)
    defined = [str(int(label)) for label in labels]
    if partition not in ("ja", "nein") or len(defined) != len(set(defined)):
        raise ValueError("Ambiguous legacy lot-definition coverage")
    observed = []
    for row in rows:
        members = row.get("lot_numbers", [row["lot_number"]] if row["lot_number"] else [])
        observed.extend(members)
        row["award_lot_defined_in_source"] = all(key in defined for key in members) if partition == "ja" else None
    missing = sorted(set(observed).difference(defined)) if partition == "ja" else []
    unawarded = sorted(set(defined).difference(observed)) if partition == "ja" else []
    return {"declared_lots_source": labels, "award_lots_without_definition": missing,
            "defined_lots_without_supported_award": unawarded,
            "lot_definition_coverage_review_required": bool(missing or unawarded)}


def parse_legacy_value_mismatch(text, number, buyer):
    """Recover separate dates/counts while flagging conflicting scalar values.

    Explicit numeric award lots must cover every declared lot once. Leading
    zeros are retained as source labels and normalized only for that comparison.
    A missing lot label in a partitioned notice remains unresolved.
    """
    text = normalized(re.sub(re.escape(number) + r"\s+Page \d+/\d+", " ", text))
    if set(fulltext_buyers(text, number)) != {buyer} or result_status(text, number, buyer) != "awarded":
        raise ValueError("Scalar legacy review lacks the expected awarded authority")
    before, *sections = text.split("Abschnitt V: Auftragsvergabe")
    partition = unique_optional(r"Aufteilung des Auftrags in Lose: (ja|nein)", before)
    defined_raw = re.findall(r"Los-Nr\.: (\d+)\b", before)
    defined = [str(int(label)) for label in defined_raw]
    if partition not in ("ja", "nein") or len(defined) != len(set(defined)) or "0" in defined:
        raise ValueError("Missing or ambiguous declared legacy lots")
    if partition == "ja" and not defined or partition == "nein" and defined:
        raise ValueError("Declared lots conflict with the notice partition flag")
    total_raw = unique_optional(r"II\.1\.7\. Gesamtwert der Beschaffung Wert ohne MwSt\.: ([\d ,.]+) EUR", before)
    if total_raw is None or not sections:
        raise ValueError("Missing legacy total or award sections")
    rows, used = [], set()
    for index, section in enumerate(sections, 1):
        section = section.split("Abschnitt VI: Weitere Angaben")[0]
        header = section.split("Ein Auftrag/Los wurde vergeben:")[0]
        label = unique_optional(r"Los-Nr\.: (.*?) Bezeichnung des Auftrags:", header)
        if partition == "nein":
            if len(sections) != 1 or label not in (None, "1"):
                raise ValueError("Unexpected undivided legacy award label")
            lot, unit = None, "undivided_contract"
        else:
            if label is None or not re.fullmatch(r"[0-9]+", label):
                raise ValueError("Partitioned legacy award lacks an explicit numeric lot identity")
            lot, unit = str(int(label)), "lot"
            if lot not in defined or lot in used:
                raise ValueError("Undefined or repeated scalar legacy award lot")
            used.add(lot)
        date_raw = unique_optional(r"V\.2\.1\. Tag des Vertragsabschlusses (\d{2}/\d{2}/\d{4})", section)
        count_raw = unique_optional(r"V\.2\.2\. Angaben zu den Angeboten Anzahl der eingegangenen Angebote: (\d+)\b", section)
        value_raw = unique_optional(r"(?<!veranschlagter )Gesamtwert des Auftrags/Loses: ([\d ,.]+) EUR", section)
        if date_raw is None or count_raw is None or int(count_raw) < 1 or value_raw is None:
            raise ValueError("Scalar legacy award lacks a unique date, total tender count or value")
        if "Niedrigstes Angebot:" in section:
            raise ValueError("Range layout requires its separate parser")
        rows.append({"publication_number": number, "award_section": index,
                     "lot_number": lot, "lot_label_source": label, "unit": unit,
                     "contract_conclusion_date": datetime.strptime(date_raw, "%d/%m/%Y").date().isoformat(),
                     "received_tenders": int(count_raw), "award_value_eur": str(euro(value_raw)),
                     "contract_date_source_quote": "V.2.1. Tag des Vertragsabschlusses " + date_raw,
                     "received_tenders_source_quote": "Anzahl der eingegangenen Angebote: " + count_raw,
                     "responsibility_assignment": "unverified"})
    if partition == "ja" and used != set(defined):
        raise ValueError("Incomplete scalar legacy lot coverage")
    total = str(euro(total_raw))
    reconciled = sum(Decimal(row["award_value_eur"]) for row in rows) == Decimal(total)
    if reconciled:
        raise ValueError("Value-mismatch fallback does not establish a mismatch")
    return rows, {"publication_number": number, "buyer": buyer, "notice_value_eur": total,
                  "award_sections": len(rows), "declared_lots_source": defined_raw,
                  "award_values_reconcile": False, "monetary_outcome_review_required": True,
                  "monetary_review_reason": "declared_notice_total_differs_from_award_sum"}


def parse_legacy_range_or_group(text, number, buyer):
    """Recover dated awards with explicit ranges/groups; never split a grouped count.

    This fallback accepts only the two reviewed alternative value/lot layouts.
    Scalar legacy awards continue through the existing reconciled parser.
    """
    text = normalized(re.sub(re.escape(number) + r"\s+Page \d+/\d+", " ", text))
    if set(fulltext_buyers(text, number)) != {buyer} or result_status(text, number, buyer) != "awarded":
        raise ValueError("Alternative legacy layout does not identify the expected awarded authority")
    before, *sections = text.split("Abschnitt V: Auftragsvergabe")
    partition = unique_optional(r"Aufteilung des Auftrags in Lose: (ja|nein)", before)
    defined = re.findall(r"Los-Nr\.: (\d+)\b", before)
    if partition not in ("ja", "nein") or len(defined) != len(set(defined)):
        raise ValueError("Unclear legacy lot definitions")
    declared_total = unique_optional(r"II\.1\.7\. Gesamtwert der Beschaffung Wert ohne MwSt\.: ([\d ,.]+) EUR", before)
    if declared_total is None:
        raise ValueError("Missing declared notice value")
    rows, used, alternative = [], set(), False
    for index, section in enumerate(sections, 1):
        section = section.split("Abschnitt VI: Weitere Angaben")[0]
        header = section.split("Ein Auftrag/Los wurde vergeben:")[0]
        label = unique_optional(r"Los-Nr\.: (.*?) Bezeichnung des Auftrags:", header)
        if label is None:
            raise ValueError("Missing explicit award/lot label")
        if partition == "nein":
            if len(sections) != 1 or label != "1" or defined:
                raise ValueError("Unexpected undivided contract label")
            lot_numbers, unit = [], "undivided_contract"
        else:
            if not re.fullmatch(r"Los \d+(?: \+ \d+)*", label):
                raise ValueError("Unsupported declared lot grouping")
            lot_numbers = re.findall(r"\d+", label)
            if len(set(lot_numbers)) != len(lot_numbers) or used.intersection(lot_numbers) or not set(lot_numbers).issubset(defined):
                raise ValueError("Repeated, overlapping or undefined award lots")
            used.update(lot_numbers)
            unit = "grouped_lot_award" if len(lot_numbers) > 1 else "lot"
            alternative |= len(lot_numbers) > 1
        date_raw = unique_optional(r"V\.2\.1\. Tag des Vertragsabschlusses (\d{2}/\d{2}/\d{4})", section)
        count_raw = unique_optional(r"V\.2\.2\. Angaben zu den Angeboten Anzahl der eingegangenen Angebote: (\d+)\b", section)
        if date_raw is None or count_raw is None or int(count_raw) < 1:
            raise ValueError("Alternative legacy award lacks a valid date/total tender count")
        value_raw = unique_optional(r"(?<!veranschlagter )Gesamtwert des Auftrags/Loses: ([\d ,.]+) EUR", section)
        ranges = re.findall(r"Niedrigstes Angebot: ([\d ,.]+) EUR / höchstes Angebot: ([\d ,.]+) EUR das berücksichtigt wurde", section)
        if value_raw is not None and ranges or len(ranges) > 1 or value_raw is None and not ranges:
            raise ValueError("Ambiguous scalar/range value in legacy award")
        low, high = (str(euro(v)) for v in ranges[0]) if ranges else (None, None)
        if ranges and Decimal(low) > Decimal(high):
            raise ValueError("Inverted reported bid range")
        alternative |= bool(ranges)
        rows.append({"publication_number": number, "award_section": index,
                     "lot_number": "+".join(lot_numbers) if lot_numbers else None,
                     "lot_numbers": lot_numbers, "lot_label_source": label, "unit": unit,
                     "contract_conclusion_date": datetime.strptime(date_raw, "%d/%m/%Y").date().isoformat(),
                     "received_tenders": int(count_raw), "award_value_eur": str(euro(value_raw)) if value_raw else None,
                     "bid_range_lower_eur": low, "bid_range_upper_eur": high,
                     "winning_price_not_inferred_from_range": bool(ranges),
                     "contract_date_source_quote": "V.2.1. Tag des Vertragsabschlusses " + date_raw,
                     "received_tenders_source_quote": "Anzahl der eingegangenen Angebote: " + count_raw,
                     "responsibility_assignment": "unverified"})
    if not alternative or partition == "ja" and used != set(defined):
        raise ValueError("Unsupported alternative layout or incomplete declared-lot coverage")
    total = str(euro(declared_total))
    complete_values = all(r["award_value_eur"] is not None for r in rows)
    reconciled = sum(Decimal(r["award_value_eur"]) for r in rows) == Decimal(total) if complete_values else None
    return rows, {"publication_number": number, "buyer": buyer, "status": "awarded",
                  "notice_value_eur": total, "award_values_reconcile": reconciled,
                  "monetary_outcome_review_required": reconciled is not True,
                  "monetary_review_reason": "declared_notice_total_differs_from_award_sum" if reconciled is False else "winning_price_not_reported" if reconciled is None else None,
                  "declared_lots": defined, "award_sections": len(rows), "alternative_legacy_layout": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--raw-root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--require-complete-cohort", action="store_true")
    args = parser.parse_args()
    indexed = {r["publication_number"]: r for r in json.loads(Path("outputs/nrw-buyer-scope/records.json").read_text())}
    sources = list(csv.DictReader(args.manifest.open()))
    if len({s["publication_number"] for s in sources}) != len(sources):
        raise ValueError("Duplicate source notice in full-text manifest")
    missing_sources = set(indexed).difference(s["publication_number"] for s in sources)
    if args.require_complete_cohort and missing_sources:
        raise ValueError("Full-text manifest does not cover the complete retained cohort")
    awards, audits = [], []
    for source in sources:
        number = source["publication_number"]
        if number not in indexed:
            continue
        path = verified_source(source, args.download, args.raw_root)
        text = subprocess.run(["pdftotext", "-layout", str(path), "-"], check=True, capture_output=True, text=True).stdout
        record = indexed[number]
        if set(fulltext_buyers(text, number)) != {record["buyer_name"]}:
            raise ValueError("Full notice does not match retained municipal authority")
        legacy = "Abschnitt I: Öffentlicher Auftraggeber" in text
        try:
            if legacy:
                status = result_status(text, number, record["buyer_name"])
                if status == "not_awarded":
                    rows, lot_audits = [], []
                    audit = {"status": status, "source_quote": "Ein Auftrag/Los wurde vergeben: nein"}
                else:
                    try:
                        rows, audit = parse_legacy_awards(text, number, record["buyer_name"])
                    except ValueError:
                        try:
                            rows, audit = parse_legacy_range_or_group(text, number, record["buyer_name"])
                        except ValueError:
                            rows, audit = parse_legacy_value_mismatch(text, number, record["buyer_name"])
                    value = record["source_fields"].get("total-value")
                    if value is None or Decimal(str(value)) != Decimal(audit["notice_value_eur"]):
                        raise ValueError("Legacy indexed total does not reconcile with full award values")
                    audit["status"] = "awarded"
                    audit.update(legacy_lot_definition_audit(text, number, rows))
                    lot_audits = []
            else:
                rows, lot_audits = parse_eform_results(text, number, [record["buyer_name"]])
                statuses = {a["status"] for a in lot_audits}
                audit = {"status": next(iter(statuses)) if len(statuses) == 1 else "mixed_lot_results"}
                value = record["source_fields"].get("total-value")
                if rows and value is not None and all(r["award_value_eur"] is not None for r in rows):
                    if sum(Decimal(r["award_value_eur"]) for r in rows) != Decimal(str(value)):
                        raise ValueError("eForm total differs from scoped winning tender values")
                    audit["notice_values_reconcile"] = True
            audit.update({"publication_number": number, "ags": record["ags"], "layout": "legacy" if legacy else "eform",
                          "source": source, "lot_audits": lot_audits, "award_units": len(rows),
                          "indexed_notice_value_status": monetary_status(str(record["source_fields"]["total-value"])) if record["source_fields"].get("total-value") is not None else "not_reported"})
        except ValueError as exc:
            audits.append({"publication_number": number, "ags": record["ags"], "layout": "legacy" if legacy else "eform",
                           "source": source, "status": "outcome_layout_review_required", "reason": str(exc), "award_units": 0})
            continue
        audits.append(audit)
        for row in rows:
            row.update({"ags": record["ags"], "buyer_scope": record["buyer_scope"], "source": source,
                        "layout": audit["layout"], "monetary_value_status": monetary_status(row["award_value_eur"]),
                        "notice_award_values_reconcile": audit.get("award_values_reconcile", audit.get("notice_values_reconcile")),
                        "monetary_outcome_review_required": audit.get("monetary_outcome_review_required", False) or row["award_value_eur"] is None or monetary_status(row["award_value_eur"]) != "reported_not_independently_validated",
                        "actual_term_assignment": "unverified", "gender_measurement": "unverified"})
        awards.extend(rows)
    keys = [(r["publication_number"], r["lot_number"]) for r in awards]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate notice-lot outcome")
    interval = json.loads(Path("outputs/nrw-official-evidence/role-intervals.json").read_text())[0]
    for row in awards:
        d = row["contract_conclusion_date"]
        row["within_source_bounded_geilen_role"] = interval["start_inclusive"] <= d < interval["end_exclusive"] if row["ags"] == interval["ags"] and d else None
    summary = {"retained_cohort_notices": len(indexed), "retained_cohort_notices_without_pinned_fulltext": len(missing_sources),
               "retained_full_notices_reviewed": len(audits), "notice_status_counts": dict(Counter(a["status"] for a in audits)),
               "awarded_units": len(awards), "award_unit_layout_counts": dict(Counter(a["layout"] for a in awards)),
               "award_units_with_contract_date": sum(a["contract_conclusion_date"] is not None for a in awards),
               "award_units_with_total_tender_count": sum(a["received_tenders"] is not None for a in awards),
               "award_units_with_both_date_and_total_tender_count": sum(a["received_tenders"] is not None and a["contract_conclusion_date"] is not None for a in awards),
               "nominal_one_euro_award_values": sum(a["monetary_value_status"] == "nominal_one_euro_needs_review" for a in awards),
               "nominal_one_cent_award_values": sum(a["monetary_value_status"] == "nominal_one_cent_needs_review" for a in awards),
               "grouped_lot_award_units": sum(a["unit"] == "grouped_lot_award" for a in awards),
               "bid_range_without_winning_price_units": sum(a.get("winning_price_not_inferred_from_range", False) for a in awards),
               "notices_with_unreconciled_award_values": sum(a.get("award_values_reconcile") is False for a in audits),
               "notices_with_lot_definition_coverage_review": sum(a.get("lot_definition_coverage_review_required", False) for a in audits),
               "award_units_with_undefined_source_lot": sum(a.get("award_lot_defined_in_source") is False for a in awards),
               "dated_geilen_award_units_within_head_role": sum(a["within_source_bounded_geilen_role"] is True for a in awards),
               "represented_municipal_election_events": len({a["ags"] for a in awards}),
               "procurement_responsibility_or_main_treatment_assignments": 0}
    args.out.mkdir(parents=True, exist_ok=True)
    for name, value in [("awards", awards), ("notice-audits", audits), ("summary", summary)]:
        (args.out / (name + ".json")).write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
