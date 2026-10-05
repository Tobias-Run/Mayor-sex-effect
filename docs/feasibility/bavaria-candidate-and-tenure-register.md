# Bavaria: candidate evidence, tenure boundaries and legacy awards

**Later bounded decision, 5 October 2026:** the [register-route audit](bavaria-bounded-route.md) adds a capped 31-election TED availability check and a fresh GERDA/current-officeholder source audit. Historical gender gaps remain; no main sample is certified. The [stop/no-go memorandum](go-adapt-stop.md) makes a feasibility/data report active. Earlier acquisition priorities below are retained history and are on hold.

Evidence checked on 3 October 2026. This work continues the German adaptation of **Florio and Spagnolo (2026), [Female Mayors and Public Procurement](https://doi.org/10.2139/ssrn.7046899)**. The [German literature and adaptation note](../literature.md) explains the lessons from Schild, Arnold and Frank–Stadelmann–Torgler. Bavaria remains the priority before NRW; the interactive GitHub Pages companion follows completed research.

**Three named 2020 pairs now have documented female and male official titles. Mühldorf's full TED PDFs additionally recover five award units with explicit contract dates and tender counts.** These advances establish measurement feasibility in particular cases. They do not establish a sufficiently large, representative sample or a procurement effect.

## Candidate evidence register

The register contains the **95 named, vote-audited two-person decisions** from the [official-report pilot](bavaria-operational-pilot.md), with **190 candidate records**. Each candidate key combines AGS, decisive election date and exact source name. Full candidate vote vectors reconcile with the historical workbook. Candidate names are not inferred from anonymous party slots.

Eight candidates now have official title evidence: four female presentations and four male presentations across five municipalities. The other 182 candidate records remain without that evidence. Three pairs have both presentations documented; 92 pairs remain incomplete. The [published aggregate summary](bavaria-candidate-register-summary.csv) preserves the counts without publishing the full person register.

| Municipality | Female candidate, official title evidence | Male candidate, official title evidence | Female minus male vote margin |
| --- | --- | --- | ---: |
| Gräfelfing | Uta Wüst; municipal journal 02/2019 | Peter Köstler; municipal journal 01/2020 | −2.0463 pp |
| Mühldorf a. Inn | Marianne Zollner; INNSTADT INFO April 2020, PDF p. 2 | Michael Hetzl; INNSTADT INFO July 2020, PDF p. 2 | −1.4955 pp |
| Mainburg | Hannelore Langwieser; historical council period 2020–2026, Second Mayor | Helmut Fichtner; official 2020/21 report, PDF p. 1 | −4.2405 pp |

All three decisions were runoffs on 29 March 2020. Margin signs are descriptive calculations from final source votes, not selected RDD bandwidths. All three acquired pairs have male winners, so they supply no treated-winner variation on their own. The acquisition targeted close contests and accessible archives; it is not random sampling.

The other observations are Brigitte Kössinger in Gauting (official gazette, 1 April 2020) and Andreas Bukowski in Haar (official jubilee publication, May 2023). Haar's later document retains its own date; it is not described as a contemporaneous 2020 registry field.

### Measurement and identity rules

- Keep source-recorded registry gender, dated official gendered presentation, and algorithmic/name-based leads as different evidence types. These eight observations are **official gendered titles**, not recovered registry sex fields or self-reported gender identity.
- Preserve document dates, historical council period, title, page/row, URL, SHA-256 and the short supporting quote. A retrospectively displayed historical period is not a contemporaneously archived page; that distinction stays visible.
- Link only to a unique named election candidate with the same AGS, election date and exact candidate identity. Titles do not replace vote-vector identity verification. Conflicting presentations are flagged rather than overwritten.
- A deputy's title can document that candidate's official presentation. It cannot make the deputy the elected First Mayor. Winner status comes from the decisive vote vector.
- The exact-name 2026 GERDA matches remain follow-up leads. They are not silently copied into 2020. Hans Wilhelm Knape and Johannes Wilhelm Knape remain different unresolved identities in Gauting.

The main historical treatment sample is not yet finalized. A documented title measure can be used under an explicit, consistently applied research coding rule; registry sex is not a mandatory prerequisite for every future observation. Timing, conflicting evidence and missingness must be reviewed across the eventual eligible sample before preregistration. No treatment labels are promoted by these acquisition scripts.

## Tenure boundaries

The tenure supplement records **three source-supported first appointments** and **two intervals bounded by source evidence**. It distinguishes initial appointment, renewed term, council/committee membership, successor entry and oath. A first-ever appointment before an election does not date the renewed term after that election.

| Municipality / 2020 winner | Inclusive start | Exclusive end | Source and remaining limitation |
| --- | --- | --- | --- |
| Mühldorf / Michael Hetzl | 2020-05-01 | 2026-05-01 | July 2020 journal p. 3 explicitly dates initial appointment; July 2026 journal p. 6 dates successor entry. Intervening interruptions and delegations have not been comprehensively audited. |
| Mainburg / Helmut Fichtner | 2020-05-01 | 2026-05-01 | Historical workbook's first-entry field matches the first-winning 2020 event; historical council row for **First Mayor in the city council** ends 30 April 2026 inclusive. The role-end record is not an independent certification of uninterrupted procurement authority. |
| Prien a. Chiemsee / Andreas Friedrich | 2020-05-01 | Unknown | Official First Mayor block explicitly says “im Amt: Seit 01.05.2020”; it agrees with the initial-entry workbook field. No end is inferred from the standard electoral cycle. |

In Mühldorf, the successor took office on **1 May 2026** and was sworn in on **7 May**. The oath cannot replace the actual appointment date. The July 2026 publication also contains an old Michael Hetzl mayor caption on another page; the explicit successor appointment in the article body controls this boundary observation.

Mainburg's public SessionNet archive permits selecting the actual historical period: `__cwpnr=4` means 2020–2026, while `__cwpnr=3` means 2014–2020. The parser requires the **selected** period, not merely an available menu option. It takes the end date from the same row as the municipality's First Mayor role in the city council. A committee role ending on 4 May 2026 in the unfiltered current archive must not move the mayoral interval's boundary. Hannelore Langwieser's Second Mayor row supplies presentation evidence without confusing her office with Fichtner's.

The first-entry workbook is a GERDA-distributed copy attributed to the Bavarian State Statistical Office, not a direct delivery to this project. The [historical audit](bavaria-feasibility.md#historical-source) documents the pin and provenance. First-entry dates are used here only where they follow the identified first-winning election in the same year; they are not a general renewed-term estimator.

These intervals support chronological screening. They do not, by themselves, prove who authorized a procurement decision, rule out absence/delegation, or identify decisions taken before a contract's signature.

## Mühldorf: full legacy TED documents close index gaps

The indexed JSON left contract dates and tender counts missing for both retained Mühldorf notices. Public **German PDF documents** contain those fields. The direct XML endpoints returned empty bodies during this check; the usable evidence below comes from the PDFs.

| TED notice | Award unit | Contract concluded | Received tenders | Award value, EUR excluding VAT |
| --- | --- | --- | ---: | ---: |
| [108149-2021](https://ted.europa.eu/de/notice/108149-2021/pdf) | Undivided planning contract | 2021-02-25 | 2 | 377,140.32 |
| [437287-2023](https://ted.europa.eu/de/notice/437287-2023/pdf) | Lot 1, vehicle chassis | 2023-07-03 | 1 | 126,500.00 |
| Same notice | Lot 2, vehicle body | 2023-07-03 | 1 | 295,248.00 |
| Same notice | Lot 3, equipment | 2023-07-03 | 1 | 82,447.70 |
| Same notice | Lot 4, hydraulic rescue equipment | 2023-07-14 | 2 | 39,439.00 |

All five dates lie within Mühldorf's source-bounded interval. This is a **date-in-interval check**, not a verified responsibility or treatment assignment. The 2023 award values sum to the indexed notice total of EUR 543,634.70. The 2021 undivided award equals the indexed total of EUR 377,140.32. Currency and exact decimal reconciliation are explicit checks.

The 2021 notice lists a consortium and an additional supplier block inside one award section. These are not separate contracts. Its authority section also states that a central purchasing body awards the contract; purchaser/beneficiary scope needs further review. The 2023 notice requires chassis and body to be offered together. Those lots, and the other lots in that notice, are related observations. Five award units represent **two notices and one election event**, not five independently treated municipalities.

The new legacy records are a supplement to the original 18-notice indexed pilot, not five additional notices. They leave its indexed results intact: nine Gauting single-lot awarded tender counts and five explicit Gauting contract dates. Missing environmental/social criteria remain missing. Full-text coverage, amendments, procedure deduplication and award-date decision authority still require expansion and audit.

## Primary sources and reproducibility

New municipal sources are public official publications or the municipality-linked council system:

| Source | Exact location / extraction |
| --- | --- |
| [Mühldorf journal archive](https://www.muehldorf.de/228-Innstadt-Info.html) | Official historical journal collection |
| [April 2020](https://www.muehldorf.de/files/2020_innstadtinfo-april_web_1.pdf) | p. 2: Marianne Zollner, First Mayor |
| [July 2020](https://www.muehldorf.de/files/2020_innstadtinfo-juli-2020_web.pdf) | p. 2: Michael Hetzl title; p. 3: initial appointment |
| [July 2026](https://www.muehldorf.de/files/buch_innstadtinfo_ausgabe_3_juli_2026_.pdf) | p. 6: successor actual appointment and separate oath |
| [Mainburg, Langwieser](https://buergerinfo-mainburg.digitalfabrix.de/kp0050.asp?__cwpnr=4&__cselect=0&__kpenr=14&smcmode=32832) | Selected historical 2020–2026 period; city-council Second Mayor row |
| [Mainburg, Fichtner](https://buergerinfo-mainburg.digitalfabrix.de/kp0050.asp?__cwpnr=4&__cselect=0&__kpenr=98&smcmode=32832) | Selected historical 2020–2026 period; city-council First Mayor row |
| [Prien mayor page](https://www.prien.de/de/gemeindepolitik/buergermeister.htm) | First Mayor Andreas Friedrich block; explicit initial entry |
| [Haar jubilee publication](https://www.stadt-haar.de/ceasy/resource/?id=3309&download=1) | p. 2: Andreas Bukowski title; publication May 2023 |

The scripts pin SHA-256 for every document. Mutable council/profile HTML will generally fail a later checksum check; retain the acquired local snapshot and retrieval metadata, or review any new version before updating a pin. Automatically accepting a changed live page would erase the evidence trail. Full municipal publications, contact details and the 190-row candidate register remain local in ignored directories; the repository publishes original code, limited attributed source facts and aggregate checks.

From the repository root, after reproducing the earlier [election and TED acquisition](bavaria-operational-pilot.md#reproduction-and-outputs) and retaining the pinned raw historical workbook:

```bash
python src/pilot/bavaria_official_title_evidence.py --download
python src/pilot/bavaria_candidate_register.py --download
python src/pilot/bavaria_legacy_ted_awards.py --download
python -m unittest discover -s tests -v
```

Python's standard library and Poppler's `pdftotext` are sufficient. Downloads must match the pins; the offline tests require no downloaded sources. The title and candidate scripts produce separate local JSON files for observations, candidate rows, mixed-title pairs, tenure boundaries, indexed date audits and summaries. The legacy script produces scoped award units and notice-level reconciliation audits; it is not a universal parser for all TED layouts.

Validation passed **17 tests**, including rejection of preliminary vote differences, tied identities, unresolved name variants, wrong historical periods, committee/end-date confusion, renewed-term first-entry misuse, ongoing competitions, duplicated lots and mismatched values. Real-source runs reproduce eight title observations, 190 candidate rows, three mixed-title pairs, two bounded intervals and five legacy award units.

## Remaining Bavaria work

The statewide queue still contains 997 screened 2020–2024 decisions; only 95 currently have both candidate identities recovered from the larger-municipality official reports. The immediate acquisition priorities are the remaining close named pairs, smaller-municipality identity coverage, historical losing-candidate presentation and actual appointment/departure evidence. Gräfelfing needs its own tenure and procurement follow-up; Mühldorf's central purchasing scope needs review. Mainburg and Prien were not included in the existing TED query, so this pilot cannot describe their award coverage or record zero procurement.

Expand eligible municipal procurement queries and full legacy document extraction before judging outcome completeness. A precision calculation needs enough distinct elections, variation in winners' measured presentation and defensible coverage; additional lots within one municipality cannot substitute for those requirements. No effect has been estimated and no research companion has been deployed.
