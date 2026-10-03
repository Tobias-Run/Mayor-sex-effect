# NRW: named candidates, council-role boundaries and municipal TED pilot

Checked on 3 October 2026. This pilot continues the [380-election NRW audit](nrw-statewide-election-register.md). It adapts **Florio and Spagnolo's [Female Mayors and Public Procurement](https://doi.org/10.2139/ssrn.7046899)** to Germany; the [literature review](../literature.md) records the German precedents. **No causal effects have been estimated.**

The new evidence comprises **55 strictly matched municipal result notices**, **four named official title observations**, **one source-bounded council-head interval**, and **two legacy awarded contracts with explicit dates and tender counts**. A third full notice explicitly reports no award. These are acquisition and measurement results, not an eligible RDD sample.

## Three deliberately selected follow-up municipalities

| Municipality / AGS | Official 2020 winner | Decisive election date | Absolute winner–runner-up margin, percentage points |
| --- | --- | --- | ---: |
| Iserlohn / 05962024 | Michael Joithe | 27 September 2020 | 0.397174 |
| Velbert / 05158032 | Dirk Lukrafka | 27 September 2020 | 0.898546 |
| Geilenkirchen / 05370012 | Daniela Ritzerfeld | 13 September 2020 | 1.091427 |

The margin uses exact winner minus runner-up votes divided by all valid votes in the decisive round. These are three close-election leads drawn from the 72 GERDA mixed-prediction pairs. They include prospective female- and male-winner cases, but selection is exploratory and gender measurement is reviewed separately. Neither these margins nor the three-municipality selection define an RDD bandwidth or analytical sample.

## Municipal TED acquisition and buyer scope

The [TED public search API](https://api.ted.europa.eu/v3/notices/search) returned **115 distinct notices**, with complete pagination and no reported timeout, for this fixed query:

```text
buyer-country = DEU AND
(buyer-name ~ Iserlohn OR buyer-name ~ Velbert OR buyer-name ~ Geilenkirchen)
AND notice-type = can-standard
AND publication-date >= 20210101 AND publication-date <= 20241231
```

The snapshot was retrieved at `2026-10-03T20:44:27.990581+00:00`; its single JSON page has SHA-256 `c3ca88cea6ac3072298a0c53684c50ccc6e5f0847e2275f77fdbf1f344b5134e`. The [request manifest](nrw-ted-request-manifest.json) records the exact field set and pagination. Completeness applies to this query and snapshot, not to all procurement in the municipalities.

Strict matching requires one distinct German buyer label and an exact reviewed alias: `Stadt Iserlohn`, `Stadt Velbert`, `Stadt Geilenkirchen`, `Stadt Geilenkirchen -Die Bürgermeisterin-`, or `Stadt Geilenkirchen, Die Bürgermeisterin`. Labels in other languages are not additional buyers.

Of the 115 notices, **55 are retained**. Of the other 60, **40 need municipal-label/department/represented-beneficiary review**, **19 concern other organizations**, and **one has multiple or missing German buyer labels**. Separate utilities and hospitals are not automatically city administrations. A buyer identifier such as Iserlohn's legacy `DEA58` denotes a NUTS region, not its eight-digit AGS.

| Municipality | Retained result notices | Notice total-value field present | Strict indexed awarded tender counts | Unambiguous indexed contract dates |
| --- | ---: | ---: | ---: | ---: |
| Iserlohn | 36 | 28 | 0 | 0 |
| Velbert | 4 | 3 | 0 | 0 |
| Geilenkirchen | 15 | 11 | 0 | 3 |
| Total | **55** | **42** | **0** | **3** |

The conservative base-name aliases leave many Velbert department labels in review. The four retained Velbert notices therefore do not establish lower procurement activity. The table is a field-availability audit under stated matching rules; it is unsuitable for comparisons of municipal outcomes.

An indexed tender count is accepted only for one identified awarded lot, one explicitly typed `tenders` count, and matching business-term values. Typed arrays and multiple lots are not joined by list position. None of these 55 notices meets that strict indexed rule; this means **unresolved count measurement**, not zero tenders. A date is accepted only when the indexed result is awarded and the unique contract-date values agree. Missing indexed environmental/social fields remain unknown; they are not proof that no criteria were used. Amendments, repeated procedures and related lots still need deduplication before analysis.

## Full legacy notices: awards and cancellations differ

Each PDF is checked against its publication number, exact contracting authority, retained municipal record and pinned checksum. Award sections are parsed separately; lot values must reconcile with the notice's total and indexed value. Repeated supplier blocks do not create extra contracts.

| Full notice | Full-text result | Contract date | Received tenders | Award value, EUR |
| --- | --- | --- | ---: | ---: |
| [21732-2021, Iserlohn](https://ted.europa.eu/de/notice/21732-2021/pdf) | One awarded undivided contract | 19 December 2020 | 3 | 319,200.00 |
| [510704-2021, Geilenkirchen](https://ted.europa.eu/de/notice/510704-2021/pdf) | One awarded undivided contract | 4 October 2021 | 11 | 39,844.66 |
| [565529-2023, Velbert](https://ted.europa.eu/de/notice/565529-2023/pdf) | Explicitly not awarded | Unknown / not applicable | Unknown / not applicable | No awarded unit extracted |

The Velbert PDF states **“Ein Auftrag/Los wurde vergeben: nein”**. It must not become an awarded contract or a zero-tender outcome. Iserlohn's contract was concluded in **2020** although its notice was published on 18 January **2021**: a publication-window query does not impose the same contract-date window.

Three selectively reviewed PDFs do not establish full outcome coverage. The two tender counts describe two contracts in two municipalities, not a gender effect or a precision assessment.

## Named official presentation and historical role boundaries

| Decisive candidate | Verified official wording | Source timing and measurement |
| --- | --- | --- |
| Daniela Ritzerfeld, Geilenkirchen | “Bürgermeisterin Daniela Ritzerfeld” | [Historical member view, 2020–2025](https://rat.geilenkirchen.de/bi/kp0041.asp?__cwpnr=6&__cselect=0&) |
| Georg Schmitz, Geilenkirchen | “Bürgermeister Georg Schmitz” | [Historical member view, 2014–2020](https://rat.geilenkirchen.de/bi/kp0041.asp?__cwpnr=5&__cselect=0&) |
| Dirk Lukrafka, Velbert | “Velbert, den 12.11.2020 … Dirk Lukrafka Bürgermeister” | [Municipal gazette no. 37/2020](https://www.velbert.de/fileadmin/user_upload/Aktuelles/Amtsblatt/amtsblatt-2020/amtsb37-2020.pdf), PDF page 3; issue dated 16 November 2020 |
| Michael Joithe, Iserlohn | “Bürgermeister Michael Joithe wurde bei den Kommunalwahlen am 27. September 2020 (Stichwahl) …” | [Current official mayor page](https://www.iserlohn.de/rathaus-politik/politik/buergermeister), retrospective statement retrieved on 3 October 2026 |

The official electoral register independently identifies these four people as decisive candidates. **Geilenkirchen is the first NRW pair in this pilot with both female and male official titles documented.** Schmitz's title concerns the preceding historical council period; Joithe's page is current and retrospective. Retrieval date, referred period and observation date are retained separately. These are public official gendered presentations, not recorded registry sex fields or self-reported gender. No treatment label is automatically promoted from them. The other decisive candidates in Iserlohn and Velbert still need primary evidence.

Ritzerfeld's named [all-data person-role page](https://rat.geilenkirchen.de/bi/kp0050.asp?__cwpall=1&__kpenr=1600) explicitly records **Rat der Stadt Geilenkirchen — Vorsitz — 01.11.2020 to 31.10.2025**. This supports the source-bounded head-role interval **[1 November 2020, 1 November 2025)**, not a September election-date start. The [2020–2025 person-role view](https://rat.geilenkirchen.de/bi/kp0050.asp?__cwpnr=6&__cselect=0&__kpenr=1600) independently displays the same end, while leaving its start cell blank. The explicit start therefore comes from the all-data view. Committee chairmanships start on 12 November 2020 and are not substituted for the council-head start.

A historical council roster can contain both Ritzerfeld and her boundary successor, with different dates. The code uses her named person page and the exact council-head row rather than choosing the first chair entry in a roster. It rejects mismatched people, periods and ambiguous roles.

Four Geilenkirchen notice-date observations lie inside this source-bounded interval: legacy notice `510704-2021` and indexed notices `196766-2024`, `218390-2024`, and `628629-2024`. This establishes temporal overlap only. It does not audit leave, acting appointments, procurement initiation or delegated/central purchasing responsibility. Actual renewed-term starts for Iserlohn and Velbert remain unresolved; Velbert's 2014 first-entry biography is not a 2020 renewal date.

## Reproduction, tests and release scope

From the repository root, with the [NRW election inputs](nrw-statewide-election-register.md#reproduce-and-inspect) acquired:

```bash
python src/pilot/nrw_ted_linkage.py --download
python src/pilot/nrw_legacy_ted_awards.py --download
python src/pilot/nrw_official_evidence.py --download
python -m unittest discover -s tests -v
```

Omit `--download` to audit cached files. TED acquisition refuses to overwrite an existing snapshot. Municipal and legacy-PDF sources must match their reviewed pins; changing HTML requires source review. A new TED search can have different counts; retain its manifest and compare it with the published snapshot. Python's standard library and Poppler's `pdftotext` suffice.

Generated records, exclusions, source quotes and date checks remain under `outputs/nrw-ted-linkage/`, `outputs/nrw-legacy-ted/` and `outputs/nrw-official-evidence/`; raw snapshots remain under `data/raw/ted-nrw/` and `data/raw/nrw-evidence/`. The public release contains original code, limited cited facts, the [aggregate summary](nrw-operational-pilot-summary.csv), and a [ten-source manifest](nrw-operational-source-manifest.csv). It does not redistribute complete source pages, personal contact records or the GERDA candidate dataset.

All three real-source pipelines complete successfully. **31 offline tests pass**, including six new tests of buyer scope, non-awards, mixed award sections, named-person historical boundaries, committee dates and successor-day exclusion.

## Next acquisition gates

Review the 40 municipal scope/alias cases, expand full notices and verify beneficiary municipalities before interpreting coverage. Obtain primary presentation evidence for both remaining finalists and actual office boundaries in Iserlohn and Velbert; extend the same protocol to the remaining close-election queue. Document procedure/lot deduplication, reporting selection and environmental/social outcome availability. Only then count independently eligible elections and assess precision. GitHub Pages remains deferred until the research is complete.
