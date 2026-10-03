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
        status = unique_optional(r"Status der Preisträgerauswahl: (.*?)(?=6\.1\.[124]\.)", section)
        if status is None:
            raise ValueError("Missing explicit eForm result status")
        status = status.strip()
        if status.startswith(("Es wurde kein Gewinner ermittelt", "Es wurde kein Wettbewerbsgewinner ermittelt, und der Wettbewerb ist abgeschlossen.")):
            audits.append({"lot_number": lot, "status": "not_awarded", "source_quote": status})
            continue
        if status != "Es wurde mindestens ein Gewinner ermittelt.":
            raise ValueError("Unrecognized eForm result status: " + status)
        if section.count("Informationen zum Auftrag:") > 1:
            raise ValueError("Multiple contracts within one lot need separate contract linkage")
        date_raw = unique_optional(r"Datum des Vertragsabschlusses: (\d{2}/\d{2}/\d{4})", section)
        contract_date = datetime.strptime(date_raw, "%d/%m/%Y").date().isoformat() if date_raw else None
        selection_raw = unique_optional(r"Datum der Auswahl des Gewinners: (\d{2}/\d{2}/\d{4})", section)
        count_raw = unique_optional(r"Art der eingegangenen Einreichungen: Angebote Anzahl der eingegangenen Angebote oder Teilnahmeanträge: (\d+)\b", section)
        count = int(count_raw) if count_raw is not None else None
        if count == 0:
            raise ValueError("Awarded result with zero total tenders requires review")
        value_raw = unique_optional(r"Wert des Angebots: ([\d ,.]+) EUR", section)
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
    return "nominal_one_euro_needs_review" if Decimal(value) == 1 else "reported_not_independently_validated"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    indexed = {r["publication_number"]: r for r in json.loads(Path("outputs/nrw-buyer-scope/records.json").read_text())}
    sources = list(csv.DictReader(MANIFEST.open()))
    awards, audits = [], []
    for source in sources:
        number = source["publication_number"]
        if number not in indexed:
            continue
        path = verified_source(source, args.download, ROOT)
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
                    rows, audit = parse_legacy_awards(text, number, record["buyer_name"])
                    value = record["source_fields"].get("total-value")
                    if value is None or Decimal(str(value)) != Decimal(audit["notice_value_eur"]):
                        raise ValueError("Legacy indexed total does not reconcile with full award values")
                    audit["status"] = "awarded"
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
                        "actual_term_assignment": "unverified", "gender_measurement": "unverified"})
        awards.extend(rows)
    keys = [(r["publication_number"], r["lot_number"]) for r in awards]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate notice-lot outcome")
    interval = json.loads(Path("outputs/nrw-official-evidence/role-intervals.json").read_text())[0]
    for row in awards:
        d = row["contract_conclusion_date"]
        row["within_source_bounded_geilen_role"] = interval["start_inclusive"] <= d < interval["end_exclusive"] if row["ags"] == interval["ags"] and d else None
    summary = {"retained_full_notices_reviewed": len(audits), "notice_status_counts": dict(Counter(a["status"] for a in audits)),
               "awarded_units": len(awards), "award_unit_layout_counts": dict(Counter(a["layout"] for a in awards)),
               "award_units_with_contract_date": sum(a["contract_conclusion_date"] is not None for a in awards),
               "award_units_with_total_tender_count": sum(a["received_tenders"] is not None for a in awards),
               "award_units_with_both_date_and_total_tender_count": sum(a["received_tenders"] is not None and a["contract_conclusion_date"] is not None for a in awards),
               "nominal_one_euro_award_values": sum(a["monetary_value_status"] == "nominal_one_euro_needs_review" for a in awards),
               "dated_geilen_award_units_within_head_role": sum(a["within_source_bounded_geilen_role"] is True for a in awards),
               "represented_municipal_election_events": len({a["ags"] for a in awards}),
               "procurement_responsibility_or_main_treatment_assignments": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in [("awards", awards), ("notice-audits", audits), ("summary", summary)]:
        (OUT / (name + ".json")).write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
