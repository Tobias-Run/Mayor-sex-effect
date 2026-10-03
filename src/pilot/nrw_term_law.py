"""Verify historical NRW term rules without assigning individual mayoral authority."""
import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from bavaria_evidence_sources import html_text, verified_source

MANIFEST = Path("docs/feasibility/nrw-term-law-source-manifest.csv")
ROOT = Path("data/raw/nrw-term-law")
OUT = Path("outputs/nrw-term-law")
PERIOD_START = "2020-11-01"
PERIOD_END = "2025-11-01"


def legal_entry_from_verified_components(acceptance_date, predecessor_first_day_out):
    """Conditional rule only: inputs require verified person/event evidence.

    The predecessor input is the first day outside office, not their last day
    in office. Missing components stay missing; election/oath dates do not fill
    them. This helper does not certify acceptance, succession or renewed terms.
    """
    if acceptance_date is None or predecessor_first_day_out is None:
        return None
    return max(date.fromisoformat(acceptance_date), date.fromisoformat(predecessor_first_day_out)).isoformat()


def council_period_location(day):
    if day is None:
        return "contract_date_missing"
    date.fromisoformat(day)
    if day < PERIOD_START:
        return "before_scheduled_council_period"
    if day >= PERIOD_END:
        return "after_scheduled_council_period"
    return "within_scheduled_council_period"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    sources = {s["id"]: s for s in csv.DictReader(MANIFEST.open())}
    raw = {key: verified_source(source, args.download, ROOT).read_text() for key, source in sources.items()}
    for parent, body, title in [("go-2020-nov", "go-2020-body", "01.11.2020 Gemeindeordnung"),
                                ("kwahlg-2020", "kwahlg-2020-body", "07.05.2020 Bekanntmachung"),
                                ("lbg-2018", "lbg-2018-body", "25.05.2018 Gesetz")]:
        if title not in html_text(raw[parent]) or urlsplit(sources[body]["url"]).path not in raw[parent]:
            raise ValueError("Historical version page does not identify the pinned linked statute")
    navigation = html_text(raw["lbg-current"])
    if "vom 25.05.2018" not in navigation or "vom 16.07.2021" not in navigation:
        raise ValueError("LBG historical-version navigation changed")
    text = {key: html_text(value) for key, value in raw.items()}
    statements = [
        ("go-2020-body", "GO NRW § 42(1)", "The regular council period lasts five years.",
         "Die Ratsmitglieder werden von den Bürgern in allgemeiner, unmittelbarer, freier, gleicher und geheimer Wahl für die Dauer von fünf Jahren gewählt."),
        ("go-2020-body", "GO NRW § 65(1)", "The regular mayoral election is for five years alongside the council.",
         "Der Bürgermeister wird von den Bürgern in allgemeiner, unmittelbarer, freier, gleicher und geheimer Wahl auf die Dauer von fünf Jahren nach den Grundsätzen der Mehrheitswahl zugleich mit dem Rat gewählt."),
        ("go-2020-body", "GO NRW § 65(3)", "The mayor is sworn in and introduced in a council meeting.",
         "Der Bürgermeister wird vom Vorsitzenden (ehrenamtlicher Stellvertreter oder Altersvorsitzender) in einer Sitzung des Rates vereidigt und in sein Amt eingeführt."),
        ("kwahlg-2020-body", "2013 transition act, Article 5 § 2, reproduced with KWahlG", "The 2020 council period begins on 1 November 2020.",
         "Die Wahlperiode der im Jahr 2020 gewählten Vertretungen beginnt am 1. November 2020."),
        ("lbg-2018-body", "LBG NRW § 118(3)", "Mayoral office starts with acceptance, no earlier than predecessor exit; appointment is unnecessary.",
         "Das Beamtenverhältnis wird mit dem Tage der Annahme der Wahl, frühestens mit dem Ausscheiden der Vorgängerin oder des Vorgängers aus dem Amt, begründet (Amtsantritt) und bedarf keiner Ernennung."),
    ]
    rules = []
    for key, provision, meaning, quote in statements:
        if text[key].count(quote) != 1:
            raise ValueError("Historical legal statement is missing or repeated: " + provision)
        rules.append({"provision": provision, "meaning": meaning, "source_quote": quote, "source": sources[key]})
    awards = json.loads(Path("outputs/nrw-complete-ted/awards.json").read_text())
    checks = [{"publication_number": a["publication_number"], "lot_number": a["lot_number"], "ags": a["ags"],
               "contract_conclusion_date": a["contract_conclusion_date"],
               "scheduled_council_period_location": council_period_location(a["contract_conclusion_date"]),
               "individual_legal_entry_date": None, "procurement_responsibility_assignment": "unverified"} for a in awards]
    summary = {"pinned_legal_sources": len(sources), "historical_legal_statements_verified": len(rules),
               "scheduled_council_period_start": PERIOD_START, "scheduled_council_period_end_exclusive": PERIOD_END,
               "period_is_not_a_certified_individual_mayoral_term": True, "award_units_checked": len(checks),
               "contract_date_location_counts": dict(Counter(c["scheduled_council_period_location"] for c in checks)),
               "individual_legal_entry_dates_assigned": 0, "main_treatment_or_procurement_responsibility_assignments": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in [("legal-rules", rules), ("award-period-checks", checks), ("summary", summary)]:
        (OUT / (name + ".json")).write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
