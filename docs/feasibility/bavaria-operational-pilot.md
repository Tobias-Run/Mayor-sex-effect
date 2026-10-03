# Bavaria: operational election–procurement pilot

Evidence checked on 3 October 2026. This pilot develops the German adaptation of [Florio and Spagnolo's Italian procurement study](../literature.md). It verifies source linkage and outcome availability; it does not estimate a mayor-gender effect. Bavaria remains the priority before NRW.

## What now works

Five official statistical reports recover names for **450 municipal election rounds**, with **1,432 matched candidate-round observations**, from 2008, 2014 and 2020. These are observations across rounds, not distinct people. Within the conservative 2020 two-candidate election screen, **95 decisive rounds** have named candidate pairs: six within two percentage points and 16 within five. Candidate gender and actual individual terms remain unverified.

A public TED JSON query retrieves 204 result notices published during 2021–2024 mentioning Gauting or Mühldorf. Strict municipal buyer aliases retain **18 notices**: 16 for Gauting and two for Mühldorf am Inn. Nine Gauting notices contain an unambiguous awarded single-lot tender count; five contain an explicit contract conclusion date. These are usable measurement observations, not independent treated municipalities or a complete procurement census.

## Named election archives

The [Statistical Library](https://www.statistischebibliothek.de/) preserves official Bavarian reports even where old Landesamt links no longer work. Search `Kommunalwahlen 2020 Bayern` and follow the document viewer's PDF link. The downloaded reports have pinned SHA-256 checksums in [the extraction script](../../src/pilot/bavaria_named_reports.py).

| Official report | Municipal units parsed | Current candidate rows | Complete rounds matched |
| --- | ---: | ---: | ---: |
| [2020 first round, 15 March](https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/BYHeft_derivate_00006228/B7331C%20202051.pdf) | 213 | 925 | 145 |
| [2020 runoff, 29 March](https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/BYHeft_derivate_00006229/B7332C%20202051.pdf) | 103 | 206 | 79 |
| [2014 first round, 16 March](https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/BYHeft_derivate_00005465/B7331C%20201451.pdf) | 173 | 623 | 123 |
| [2014 runoff, 30 March](https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/BYHeft_derivate_00003930/B7332C%20201451.pdf) | 65 | 130 | 53 |
| [2008 runoff, 16 March](https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/BYHeft_derivate_00000669/B7332C%20200851.pdf) | 57 | 114 | 50 |

These named tables cover municipalities above 10,000 inhabitants at election time. They cannot establish statewide close-election coverage. County elections are excluded by chapter boundaries. Entries marked `X` for the current election are previous-election candidates and are excluded from current vote vectors.

The reports explicitly contain **preliminary results**. Names attach to historical workbook slots only when the entire municipal vote vector agrees exactly, votes are distinct, and the workbook has a unique, complete, reconciled round. No guessed party aliases or approximate vote matching are used. For example, Munich's preliminary runoff counts (158,782 and 401,859) differ from the final counts (158,773 and 401,856), so that round fails this automatic identity match. Review queues retain mismatches and incomplete rounds. Existing final-result evidence is preserved.

The 450 matched rounds include both first and second rounds and several years. The 95 count applies only to decisive rounds in the conservative 2020 screen; these counts must not be added together.

### Supplementary smaller-municipality evidence

An [official final Itzgrund runoff notice](https://www.itzgrund.de/media/bek_abschliessendes_ergebnis_stichwahl.pdf), linked from the [municipality's election page](https://www.itzgrund.de/gemeinde-rathaus/wahlen.html), was downloaded, rendered and visually checked. On 29 March 2020, Nina Liebermann received 790 votes and Dirk Ruppenstein 736; valid votes were 1,526. This matches historical AGS `09473138`, source row 18,266. The notice marks the result final and the winner's acceptance. The margin is approximately 3.54 percentage points.

This is **one additional manually verified named pair**, separate from the 95 automatically recovered report pairs. The PDF SHA-256 is `dcad7c21483baffec17577ce02c8b858e6fe40fb5369e43ae07e700a1bd61fac`. Nomination labels differ between sources (`FWI/SPD` versus `Freie Wählergruppe Itzgrund`) and are retained separately. Its named candidates, gender and complete actual term are different evidence questions: the latter two remain unverified. Manual transcription evidence remains in ignored local outputs and is not silently incorporated into automatic counts.

## Historical TED fields and buyer linkage

The [official Search API documentation](https://docs.ted.europa.eu/api/latest/search.html) describes unauthenticated public reuse. The [OpenAPI schema](https://api.ted.europa.eu/api-v3.yaml) provides supported index fields. Indexed JSON offers a working historical outcome route despite unresolved empty HTTP 202 responses from some XML download links.

The exact query is:

```text
buyer-country = DEU AND (buyer-name ~ Gauting OR buyer-name ~ Mühldorf)
AND notice-type = can-standard
AND publication-date >= 20210101 AND publication-date <= 20241231
```

The snapshot was retrieved on 3 October 2026. Pagination, total count, duplicate publication numbers and response hashes are checked. This complete 204-notice query result is **not complete municipal procurement coverage**. Exact German buyer aliases are `Gemeinde Gauting`, `Stadt Mühldorf am Inn` and `Kreisstadt Mühldorf a. Inn`. Missing/multiple German labels exclude 11 notices; 175 other buyer labels are excluded. Hospitals, counties and shared procurement do not automatically become municipal outcomes because their names or addresses mention a municipality.

| Available indexed evidence | Gauting | Mühldorf am Inn |
| --- | ---: | ---: |
| Retained municipal notices | 16 | 2 |
| Notice total value present | 4 | 2 |
| Winner name present | 9 | 0 |
| Explicit contract date present and accepted | 5 | 0 |
| Tender-count field present | 12 | 0 |
| Awarded, identified single-lot tender count accepted | 9 | 0 |
| Winner selected (`selec-w`) | 9 | 0 |
| Competition ongoing (`open-nw`) | 3 | 0 |
| Winner status not indexed | 4 | 2 |

The [eForms winner-selection codelist](https://raw.githubusercontent.com/OP-TED/eForms-SDK/1.13.0/codelists/winner-selection-status.gc) distinguishes `selec-w` (at least one winner chosen), `open-nw` (competition ongoing, no winner yet) and `clos-nw` (competition closed without a winner). Gauting's three `open-nw` notices have submission counts 0, 0 and 1. They are excluded from awarded tender-count outcomes. Missing legacy status does not imply no winner.

An accepted tender count requires exactly one identified lot, the `tenders` submission type, matching indexed and `BT-759-LotResult` values, an integer count and explicit winner selection. Arrays from several lots are not paired by position. Contract dates require matching single-valued date fields and explicit winner selection. Publication dates are never substituted: for example, publication on 22 August 2024 can report a contract concluded on 6 August 2024.

Notice-level total values, lot result values and tender values remain separate. Twelve Gauting notices carry `strategic-procurement-lot = none`; the queried green and social objective fields are absent. Absence cannot be recoded as a negative objective. No repeated single procedure identifier occurs in this retained subset, but missing identifiers and unqueried notices prevent a general claim of contract deduplication. There is no municipal-year zero imputation, inflation adjustment or effect estimate at this stage.

## Reproduction and outputs

Run from the repository root with Python 3 and Poppler's `pdftotext` installed:

```bash
python src/pilot/acquire_bavaria_sources.py
python src/pilot/gerda_structural_screen.py
python src/pilot/bavaria_historical_register.py
python src/pilot/bavaria_named_reports.py --download
python src/pilot/bavaria_ted_linkage.py --download
python -m unittest discover -s tests -p 'test_bavaria_operational_pilot.py'
```

For existing local files, omit `--download`. TED acquisition deliberately refuses to replace an existing snapshot: preserve it before obtaining a new one. The five PDFs total approximately 10.7 MB. Raw data and person-level outputs stay in ignored `data/raw/` and `outputs/`; public summaries contain only counts and source metadata. Live TED results may change, so a fresh snapshot may differ from these dated figures. PDF and historical workbook hashes must match the pinned files.

Local election outputs include `matched-rounds.json`, `review-queue.json` and `recovered-screen-events.json` under `outputs/bavaria-named-reports/`. Local TED outputs include the query manifest, full source fields, municipal notice linkage and field-availability summary. Published aggregate tables are [the report summary](bavaria-named-reports-summary.csv) and [the TED pilot summary](bavaria-ted-pilot-summary.csv).

## Remaining research gates

Official sources must establish candidate gender, including losing candidates, and actual individual term dates. Names alone do not meet that requirement. Gauting's [council archive](https://buergerinfo-gauting.digitalfabrix.de/kp0040.asp?__cwpnr=6&__cselect=0&__kgrnr=1) identifies the statutory council window 1 May 2020–30 April 2026, which does not prove uninterrupted service by an individual mayor. Its `Johannes Wilhelm Knape` entry differs from the election report's `Hans Wilhelm Knape`; that identity variant requires review before joining biography evidence. Vaterstetten's current mayor title is evidence about 2026, not a substitute for 2020 candidate or tenure records.

German precedents provide useful source and design guidance: Schild and Arnold used richer historical candidate data; Frank, Stadelmann and Torgler examined municipalities above 10,000 inhabitants and the 2020 postal-runoff change. Their data availability and gender measurement should be handled according to the [literature audit](../literature.md), rather than treated as access already secured.

Before a main RDD, expand valid woman–man pairs and procurement coverage, audit reporting selection and actual mayor responsibility, deduplicate contracts/lots, and assess election-level precision. EU-threshold reporting cannot represent all local purchasing. Two linked municipalities cannot support the proposed causal analysis. GitHub Pages remains deferred until the research is complete.
