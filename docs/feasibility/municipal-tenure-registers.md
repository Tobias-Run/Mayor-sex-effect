# Municipal tenure registers discovered through GovData

Reviewed on **4 October 2026**. GovData is a federal discovery catalogue; its results point to separate provider datasets. This audit found useful municipal lists, **not a verified nationwide register of individual mayoral terms**.

The public CKAN search for `Bürgermeister` returned **522 metadata matches**, with the first 20 retrieved for discovery. Many matches are election results, planning records or unrelated keyword hits. The search for `Amtszeit` returned **12 matches**, all retrieved. These numbers are catalogue hits, not counts of verified person or tenure registers. The search snapshots, three CSV files, provider descriptions and current-role check are pinned in the [evidence manifest](nrw-extension-evidence-source-manifest.csv).

## Three downloaded CSVs

| Dataset | Source rows | Boundary precision | Research relevance |
| --- | ---: | --- | --- |
| Düsseldorf, Oberbürgermeister*innen since 1946 | 15 | Day | Named municipal head-role history; useful 2020 transition evidence |
| Düsseldorf, Bürgermeister*innen since 1946 | 29 | Day | Honorary deputies elected from the council; excluded from the full-time mayor treatment role |
| Münster, Bürgermeisterinnen und Bürgermeister since 1824 | 25, including one vacancy | Year | Historical list derived from MünsterWiki; insufficient for day-level term assignment |

The [Düsseldorf head dataset](https://opendata.duesseldorf.de/dataset/oberb%C3%BCrgermeisterinnen-der-landeshauptstadt-d%C3%BCsseldorf-seit-1946) and [deputy dataset](https://opendata.duesseldorf.de/dataset/b%C3%BCrgermeisterinnen-der-stadt-d%C3%BCsseldorf-seit-1946) identify **Datenlizenz Deutschland – Zero – Version 2.0**. Münster's catalogue description identifies **GNU Free Documentation License 1.2**, with MünsterWiki as the source. Municipality hosting does not change that secondary provenance. This repository publishes original audit code and aggregate findings, not a redistributed combined person register.

No CSV has a gender field. Düsseldorf's `Titel` column contains academic titles. Names, academic titles and plural dataset headings do not assign candidate gender.

## Exact dates help, but roles and coverage matter

Düsseldorf's head CSV records **Thomas Geisel ending on 31 October 2020** and **Stephan Keller starting on 1 November 2020**. Keller matches the independently verified official 2020 winner. His recorded start is **35 days after the decisive election on 27 September**. This is direct evidence against treating an election date as the actual office-entry date.

Keller's end is blank; no separate 2025 renewal row is supplied. The list records a person's tenure history rather than splitting every renewed electoral term. It cannot by itself establish uninterrupted procurement authority, delegated decisions or a renewed-term boundary. Historical `bis` inclusion semantics are not silently standardized: older transitions can share the same date.

The provider describes a historical **dual leadership before 1994**, separating the honorary Oberbürgermeister as council chair from the Oberstadtdirektor as administrative head. The present full-time mayor combines roles. These old rows therefore require an institutional crosswalk before being pooled with modern direct elections. The distinct deputy CSV explicitly covers honorary representation in council sessions and ceremonial functions; its 29 rows must not enter the full-time mayor treatment register.

Düsseldorf is a source/measurement check outside the six-city extension queue. This discovery adds **zero RDD-eligible elections** to the acquisition sample.

## A blank end can conceal a stale list

Münster's [CSV](https://opendata.stadt-muenster.de/sites/default/files/buergermeister-muensters.csv) ends with **Markus Lewe, start year 2009, blank end**. The city's [current official mayor page](https://www.stadt-muenster.de/oberbuergermeister) instead states: “Tilman Fuchs ist seit dem 1. November 2025 Oberbürgermeister der Stadt Münster.”

This is a concrete discrepancy between an open-ended historical-list row and a separately verified current officeholder. The blank cell cannot establish that Lewe is still mayor in October 2026. The audit retains both observations, flags freshness and does not impute Lewe's exact exit from Fuchs's entry. A provider description saying blank ends mean ongoing service is not sufficient without a current-role check.

All Münster starts have year precision. A value such as `2009` remains a year, without conversion to 1 January. The `(vakant)` row is a vacancy, not a person. These restrictions prevent apparently complete tables from producing spurious dated treatment assignments.

## Implication for the wider register search

The feasible route remains a statewide official election backbone, followed by provider-specific person/role evidence, municipal open-data discovery and explicit source quality checks. GovData can accelerate discovery of downloadable local lists. It does not supply nationwide completeness, common roles, historical gender, exact exit dates or decision authority.

The reproducible audit is [nrw_municipal_registers.py](../../src/pilot/nrw_municipal_registers.py); aggregate dataset results are in [municipal-tenure-register-summary.csv](municipal-tenure-register-summary.csv). Local outputs preserve source date precision, role category, vacancies, blank ends, the named Düsseldorf transition and Münster's current-role discrepancy. Main treatment and procurement responsibility assignments remain unverified.
