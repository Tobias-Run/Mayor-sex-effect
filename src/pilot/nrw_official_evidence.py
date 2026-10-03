"""Keep named municipal titles and council-role boundaries separate from treatment.

Run after nrw_election_register.py, nrw_ted_linkage.py and nrw_legacy_ted_awards.py.
Mutable public HTML must match reviewed pins; changed sources require review.
"""
import argparse
import json
import re
from datetime import date, timedelta
from pathlib import Path

from bavaria_evidence_sources import CouncilRows, council_role, html_text, pdf_page, verified_source

ROOT = Path("data/raw/nrw-evidence")
OUT = Path("outputs/nrw-official-evidence")
SOURCES = {
  "geilen-members-2020": {
    "id": "geilen-members-2020",
    "extension": ".html",
    "url": "https://rat.geilenkirchen.de/bi/kp0041.asp?__cwpnr=6&__cselect=0&",
    "sha256": "b6dc0482c78fd95093391c3ace3b839b89afb797b53afb61e2b93b3bd1c0253c",
    "bytes": 77864,
    "retrieved_at_utc": "2026-10-03T20:57:31.157620+00:00"
  },
  "geilen-members-2014": {
    "id": "geilen-members-2014",
    "extension": ".html",
    "url": "https://rat.geilenkirchen.de/bi/kp0041.asp?__cwpnr=5&__cselect=0&",
    "sha256": "8be496b46b7bced9b82f92715219525c66779d7673f8b38cd02f4a13230edd3e",
    "bytes": 51437,
    "retrieved_at_utc": "2026-10-03T20:57:30.752294+00:00"
  },
  "geilen-ritzerfeld-roles": {
    "id": "geilen-ritzerfeld-roles",
    "extension": ".html",
    "url": "https://rat.geilenkirchen.de/bi/kp0050.asp?__cwpall=1&__kpenr=1600",
    "sha256": "11a5b46a907096553ef18d3ec0ba02c077fb65d5b4abf19afea1a8ec60218f4f",
    "bytes": 13991,
    "retrieved_at_utc": "2026-10-03T20:58:47.762146+00:00"
  },
  "geilen-ritzerfeld-roles-2020": {
    "id": "geilen-ritzerfeld-roles-2020",
    "extension": ".html",
    "url": "https://rat.geilenkirchen.de/bi/kp0050.asp?__cwpnr=6&__cselect=0&__kpenr=1600",
    "sha256": "e129f05f2b7257e63100eb5d3afb6c42173e0390e1121c8c2f4f4d5abd81a6c6",
    "bytes": 14279,
    "retrieved_at_utc": "2026-10-03T21:03:06.026912+00:00"
  },
  "velbert-gazette-37": {
    "id": "velbert-gazette-37",
    "extension": ".pdf",
    "url": "https://www.velbert.de/fileadmin/user_upload/Aktuelles/Amtsblatt/amtsblatt-2020/amtsb37-2020.pdf",
    "sha256": "8256277b1495381f82cad82177a240ea1942fd568d69d9f487518a4460c16347",
    "bytes": 247072,
    "retrieved_at_utc": "2026-10-03T20:52:14.635518+00:00"
  },
  "iserlohn-mayor": {
    "id": "iserlohn-mayor",
    "extension": ".html",
    "url": "https://www.iserlohn.de/rathaus-politik/politik/buergermeister",
    "sha256": "334c94bb2d8da9af9d5a7dfd4fcf7b2314a702799d39c35f4cf69295acc5a090",
    "bytes": 90512,
    "retrieved_at_utc": "2026-10-03T20:47:20.697787+00:00"
  }
}


def member_title(raw, period, expected):
    selected = re.findall(r'<a\b[^>]*class="[^"]*\bsmcfiltermenuselected\b[^"]*"[^>]*>(.*?)</a>', raw, re.S)
    if [html_text(s) for s in selected] != [f"Wahlperiode {period}"]:
        raise ValueError("Historical member period changed")
    parser = CouncilRows()
    parser.feed(raw)
    matches = [r for r in parser.rows if r.get("Name") == expected]
    if len(matches) != 1:
        raise ValueError("Expected exactly one named title row")
    return expected


def person_head_role(raw, candidate):
    """Only a named person's all-data page supplies both explicit boundaries."""
    titles = re.findall(r"<title\b[^>]*>(.*?)</title>", raw, re.S | re.I)
    selected = re.findall(r'<a\b[^>]*class="[^"]*\bsmcfiltermenuselected\b[^"]*"[^>]*>(.*?)</a>', raw, re.S)
    controls = re.findall(r'<a\b[^>]*aria-label="Zeitraum auswählen"[^>]*>(.*?)</a>', raw, re.S)
    if len(titles) != 1 or candidate not in html_text(titles[0]) or selected or [html_text(s) for s in controls] != ["Alle Daten"]:
        raise ValueError("Person identity or all-data view changed")
    parser = CouncilRows()
    parser.feed(raw)
    matches = [r for r in parser.rows if r.get("Gremium") == "Rat der Stadt Geilenkirchen" and r.get("Mitarbeit") == "Vorsitz"]
    if len(matches) != 1:
        raise ValueError("Ambiguous historical council-head role")
    row = matches[0]
    def iso(value):
        day, month, year = map(int, value.split("."))
        return date(year, month, day).isoformat()
    start, end = iso(row["Beginn"]), iso(row["Ende"])
    if start > end:
        raise ValueError("Inverted council-role interval")
    return {"start_inclusive": start, "end_inclusive": end,
            "end_exclusive": (date.fromisoformat(end) + timedelta(days=1)).isoformat(),
            "source_quote": f'Rat der Stadt Geilenkirchen; Vorsitz; {row["Beginn"]}; {row["Ende"]}',
            "continuous_procurement_authority_verified": False}


def within_role(day, interval):
    return interval["start_inclusive"] <= day < interval["end_exclusive"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    paths = {key: verified_source(source, args.download, ROOT) for key, source in SOURCES.items()}
    raw = {key: path.read_text() for key, path in paths.items() if path.suffix == ".html"}
    titles = []
    for key, period, candidate, presentation in [
        ("geilen-members-2020", "2020-2025", "Ritzerfeld, Daniela", "female"),
        ("geilen-members-2014", "2014-2020", "Schmitz, Georg", "male")]:
        expected = "Bürgermeisterin Daniela Ritzerfeld" if presentation == "female" else "Bürgermeister Georg Schmitz"
        quote = member_title(raw[key], period, expected)
        titles.append({"ags": "05370012", "candidate_name_source": candidate, "presentation": presentation,
                       "source_quote": quote, "historical_view_period": period, "observation_date": None,
                       "evidence_kind": "historical_official_gendered_title", "source": SOURCES[key]})
    page = pdf_page(SOURCES["velbert-gazette-37"], 3, root=ROOT)
    quote = "Velbert, den 12.11.2020 Dirk Lukrafka Bürgermeister"
    if quote not in page:
        raise ValueError("Velbert dated signature changed")
    titles.append({"ags": "05158032", "candidate_name_source": "Lukrafka, Dirk", "presentation": "male",
                   "observation_date": "2020-11-12", "evidence_kind": "dated_official_gendered_title",
                   "source_quote": quote, "pdf_page": 3, "source": SOURCES["velbert-gazette-37"]})
    quote = "Bürgermeister Michael Joithe wurde bei den Kommunalwahlen am 27. September 2020 (Stichwahl)"
    if quote not in html_text(raw["iserlohn-mayor"]):
        raise ValueError("Iserlohn retrospective election/title statement changed")
    titles.append({"ags": "05962024", "candidate_name_source": "Joithe, Michael", "presentation": "male",
                   "observation_date": None, "referred_election_date": "2020-09-27",
                   "evidence_kind": "current_official_retrospective_title", "source_quote": quote,
                   "source": SOURCES["iserlohn-mayor"]})
    events = {e["ags"]: e for e in json.loads(Path("outputs/nrw-election-register/events.json").read_text())}
    for title in titles:
        event = events[title["ags"]]
        finalists = [c["candidate_name_source"] for c in event["candidates"]
                     if not event["has_runoff"] or c["votes_runoff"] is not None]
        if not event["votes_and_winner_verified"] or not event["decisive_pair"] or title["candidate_name_source"] not in finalists:
            raise ValueError("Named title does not match an officially verified decisive candidate")
        title.update({"registry_gender_field": False, "main_treatment_assignment": "unverified"})
    interval = person_head_role(raw["geilen-ritzerfeld-roles"], "Bürgermeisterin Daniela Ritzerfeld")
    historical = council_role(raw["geilen-ritzerfeld-roles-2020"], "Daniela Ritzerfeld", "2020-2025", "Rat der Stadt Geilenkirchen", "Vorsitz")
    if historical["Ende"] != "31.10.2025" or historical["Beginn"] != "":
        raise ValueError("Historical cross-check changed; inspect its boundary display")
    interval.update({"ags": "05370012", "candidate_name_source": "Ritzerfeld, Daniela",
                     "evidence_kind": "source_bounded_council_head_role", "sources": [SOURCES["geilen-ritzerfeld-roles"], SOURCES["geilen-ritzerfeld-roles-2020"]]})
    checks = []
    for filename, field in [("outputs/nrw-ted-linkage/records.json", "single_contract_conclusion_date"),
                            ("outputs/nrw-legacy-ted/awards.json", "contract_conclusion_date")]:
        for record in json.loads(Path(filename).read_text()):
            if record["ags"] == interval["ags"] and record.get(field):
                checks.append({"publication_number": record["publication_number"], "contract_date": record[field],
                               "within_source_bounded_role": within_role(record[field], interval),
                               "responsibility_assignment": "unverified"})
    if len({r["publication_number"] for r in checks}) != len(checks):
        raise ValueError("Indexed and full-text date observations overlap; deduplicate before counting")
    mixed = sum({t["presentation"] for t in titles if t["ags"] == ags} == {"female", "male"}
                for ags in {t["ags"] for t in titles})
    summary = {"candidate_title_observations": len(titles), "municipalities_with_title_evidence": len({t["ags"] for t in titles}),
               "decisive_pairs_with_both_mixed_official_titles": mixed, "source_bounded_head_role_intervals": 1,
               "dated_notice_observations_within_head_role": sum(c["within_source_bounded_role"] for c in checks),
               "main_treatment_or_procurement_responsibility_assignments": 0}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in [("titles", titles), ("role-intervals", [interval]), ("date-overlaps", checks), ("summary", summary)]:
        (OUT / (name + ".json")).write_text(json.dumps(value, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
