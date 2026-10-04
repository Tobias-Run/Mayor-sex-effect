# Nationwide procurement open data and the NRW structured-source audit

Reviewed on **4 October 2026**. The German Bekanntmachungsservice supplies a working, publicly documented national procurement export. This supplement to the [NRW procedure audit](nrw-procedure-and-presentation-audit.md) recovers original structured notices through that independent German publisher. It supports our adaptation of **Florio and Spagnolo's Italian study** and the [German research foundation](../literature.md).

**Result:** all **57 retained notices with a known UUID/version** are matched in both original XML and converted CSV. Original XML supports **11 additional dated/count results in Viersen** and **one additional grouped result in Geilenkirchen**. Together with the earlier 106 PDF-supported observations, this gives **118 observed award-result units across four election events**, before complete deduplication and analytical unit selection. No main treatment labels or causal effects have been assigned.

## A national service, with a defined archive and selected coverage

The GovData dataset [*Bekanntmachungen öffentlicher Auftraggeber aus Bund, Ländern und Kommunen*](https://www.govdata.de/ckan/api/3/action/package_show?id=72e38a75-efef-4fd7-874c-b5cf12457ca3) identifies the national service and its public [OpenData documentation](https://www.oeffentlichevergabe.de/documentation/swagger-ui/opendata/index.html). The linked [OpenAPI JSON](https://www.oeffentlichevergabe.de/documentation/api/opendata) documents:

- `GET /api/notice-exports`, using either `pubMonth=YYYY-MM` or `pubDay=YYYY-MM-DD`.
- Original `eforms.zip`, converted `csv.zip`, and converted `ocds.zip`.
- A documented lower archive boundary of **1 December 2022**.
- Publication-period selection in **Europe/Berlin**, with daily data processed before the preceding midnight available for retrieval.
- All published notice versions in the requested period; a monthly archive is not a table of unique procedures or contracts.

The catalogue states that publication above EU thresholds became mandatory on the service on **25 October 2023**, citing VgV § 10a(5). It also describes below-threshold eForms submissions and imports from service.bund.de with reduced information. This verifies the provider's coverage statement; it does not establish universal completeness, retroactive reporting or the content of every earlier month. **The interface's documented 2022 boundary does not solve pre-2020 procurement coverage.**

We acquired **November 2023 through December 2024**, in both CSV and original eForms: **28 pinned monthly ZIPs**. CSV archives contain 341,350 notice rows; eForms archives contain 341,231 members. These are format-level row/file counts, not verified counts of distinct notices, and their difference requires wider source-level review before a national completeness claim. The fixed NRW cohort has complete UUID/version matches in both formats.

GovData labels the general API resource and explicit eForms example **CC0**; its explicit CSV example carries **Datenlizenz Deutschland – Namensnennung 2.0**. Preserve resource-specific license metadata rather than assume every format has identical terms. The [documentation/catalogue source manifest](national-procurement-source-manifest.csv) and [28-export manifest](federal-procurement-export-manifest.json) preserve reviewed URLs, hashes, sizes and retrieval times. Original bulk files and notice-level outputs remain local.

## NRW also advertises a state interface

The GovData dataset [*Ausschreibungen des Vergabemarktplatzes NRW*](https://www.govdata.de/ckan/api/3/action/package_show?id=9896c2dc-3ee1-4047-841f-0e324a40a27b) advertises “Aktuelle und archivierte Vergabedaten” at `https://daten.vergabe.nrw.de/rest/evergabe`, under DL-BY-DE 2.0.

Its official [documentation, dated 7 September 2018](https://open.nrw/sites/default/files/opendatafiles/daten-vergabe-nrw-de-Dokumentation-v1.pdf), is readable. Pages 2–3 document JSON/XML negotiation, `page` and `size`, full-text queries, field filters, individual documents by ID, and range filters. **`CREATED_AT` is first indexing; `UPDATED_AT` is last updating and may change without content changes. Neither is a contract date.** The date-range example applies to these special fields.

A normal first-page JSON request failed with **proxy CONNECT HTTP 403**. No successful data response was obtained and no alternate host, route or transport was attempted. Therefore historical retention, award-versus-tender content, bid fields and live coverage remain **unverified**. A catalogue description of archived data alone cannot establish the needed historical award register.

## Fixed-cohort linkage and extraction

The existing inventory remains **225 result notices**. Of these, **57 have a usable notice UUID/version**, and **168 do not**. Original eForms acquisitions cover all 57 exact pairs; version padding `01` versus `1` is normalized without dropping the version. Procedure GUIDs agree across TED index, original XML and CSV. Original XML contracting-party names agree with the retained TED buyer scope after whitespace normalization.

The original XML audit follows explicit relationships:

1. A named result identifies its lot and selected-winner/open/closed status.
2. Each statistic has its own type and value within that result. Only a single explicit positive-integer `tenders` statistic supplies a total.
3. The result references settled contracts and tenders by ID. Contract definitions reference tenders, and tender definitions reference the same lot and identified tendering parties.
4. Contract `IssueDate` supplies the conclusion date; `AwardDate` is retained as winner selection. Notice issue date, requested publication and indexed actual publication remain separate.

Electronic, SME and participation-request counts never substitute for missing totals. Non-awards and unfinished results remain separate. Missing definitions, conflicting tender links, undefined lots and multiple inconsistent contract dates prevent a supported date/count pair. XML is parsed with fixed namespaces and explicit identity checks; this is not a claim of full XSD validation or source correctness.

| Original-XML result | Count |
| --- | ---: |
| Exact retained notice UUID/version matches | 57 |
| Observed lot-result sections | 88 |
| Selected-winner results | 61 |
| Closed non-awards | 22 |
| Open results | 5 |
| Results with explicit valid total-tenders count, regardless of outcome | 64 |
| Award results with supported lot/tender/contract/winner linkage | 51 |
| Award results with supported conclusion date and total count | **30** |

Of the 30 paired XML observations, **18 match existing PDF observations**, **one supplements a reviewed original-cohort notice**, and **11 belong to the extension**. There are zero conflicting nonmissing count/date fields in matched PDF units. This is agreement between two representations of published notices, not independent validation of actual bidding or legal dates.

## Additional observations and remaining source ambiguity

| Municipality | Notice | Observed paired result units | Conclusion date | Total tenders per result |
| --- | --- | ---: | --- | --- |
| Viersen | 254530-2024 | 5 | 15 April 2024 | 1, 1, 1, 1, 1 |
| Viersen | 381033-2024 | 4 | 21 June 2024 | 3, 2, 3, 2 |
| Viersen | 760455-2024 | 1 | 29 November 2024 | 3 |
| Viersen | 761195-2024 | 1 | 29 November 2024 | 3 |
| Geilenkirchen | 126957-2024 | 1 grouped lot result | 14 February 2024 | 3 |

Geilenkirchen **126957-2024** was previously held for review because its PDF has two contract-information blocks in one lot. The original XML explicitly links **one result, one lot and two settled-contract records**, both dated 14 February 2024, with one result-level total of three tenders. Retain both contract records; count the observed lot result once. This does **not** establish that there is only one legal contract or resolve duplicate/economic-value issues. The analytical contract unit remains flagged. The original PDF parser/output is unchanged; this is a separately documented XML supplement.

Viersen **381033-2024** retains its verified parent relationship to **315657-2024**. The parent has four open results and two closed non-awards; the later notice has four selected-winner results and two closed non-awards. Counts in the two closed results do not become awarded observations. An arbitrary latest-row or first-row rule would erase parts of the history.

The four previously index-supported totals—Werdohl **253377-2024** and Viersen **557169-2024**, **724046-2024**, **785396-2024**—are corroborated by explicit original XML totals of **4, 9, 3, 3**. **All four conclusion dates remain absent in the original**, so they add no paired observations. Iserlohn **50377-2024** and **51385-2024** still have conflicting result/contract tender links; selected-winner status alone does not resolve them.

The paired inventory is now **118 observations in 77 notices across four elections**: the original 106 in 72 notices, 11 Viersen results in four additional notices, and one Geilenkirchen grouped result in a previously reviewed notice. This remains an acquisition/measurement inventory. It is not an eligible RDD sample or evidence of sufficient precision.

## Converted CSV cannot supply buyer roles or counts without validation

Within the 57 matched notices, **25 require CSV conversion review**, including **94 rows with blank statistic types** and **16 notices where CSV buyer names differ from original contracting-party roles**. For example, **190347-2024** has an XML/TED buyer of Stadt Viersen; the CSV additionally gives a Vergabekammer record role `buyer`. Duplicate organization rows and reused administrative identifiers are retained in the source and do not create new municipalities or awards.

Use original XML contracting-party references for this audit. Preserve the converted CSV disagreement rather than silently repair its role fields. CSV `publicationDate` also differs from source notice issue/requested dates in selected cases. Its timestamp label must not substitute for verified competition publication. Original sources themselves may contain missing dates or contradictory objects; a different encoding does not automatically repair them.

## Recovering the original competition phase

The same monthly archives contain **50 `cn-standard` competition notices for 38 procedure GUIDs**, linked to **39 retained result notices**. All 50 are matched by exact UUID/version in original XML, CSV and a separately pinned [public TED Search API request](federal-competition-ted-request-manifest.json). They are context, not additions to the 225-result inventory. Eight GUIDs have more than one competition notice; original-publication selection and phase-specific municipal beneficiary scope remain to be reviewed.

For Viersen's cleaning procedure, competition **141329-2024** was published on **7 March 2024**, while contracts in result **381033-2024** were concluded on **21 June 2024** and that later result was published on **27 June 2024**. Werdohl competition **96667-2024** was published on **15 February 2024**, whereas its result **253377-2024** was published on **29 April 2024** and still has no conclusion date. The XML requested-publication dates are 6 March and 14 February respectively, also distinct from actual indexed publication.

These phase links directly support the [Italian timing adaptation](../research-protocol.md#timing-units-and-estimation). They do not yet assign exposure windows or treatment. Municipal procurement scope and actual office timing matter for the proposed election-level ITT; personal mayoral signatures are not a universal contract-eligibility requirement.

## Reproduction and next acquisition

First reproduce the [complete PDF cohort](nrw-complete-pilot.md), the [extension](nrw-extension.md) and the [enriched procedure index](nrw-procedure-and-presentation-audit.md). Download each reviewed monthly period using the acquisition utility, for example:

```bash
python src/pilot/federal_procurement.py 2024-06 --format csv
python src/pilot/federal_procurement.py 2024-06 --format eforms
python src/pilot/nrw_federal_procurement.py --download-context
python -m unittest discover -s tests
```

Run the acquisition command for all months listed in the manifest. Existing snapshots are never overwritten. The audit verifies all 28 archive hashes and the competition index against published pins before extracting selected records. A changed mutable source requires review; fresh retrieval does not silently change a reviewed result. The combined suite passes **96 offline tests**, including scoped multi-lot linkage, subset-versus-total counts, non-awards, date types, source hashes, version identity and grouped contracts.

The later [buyer and phase audit](nrw-buyer-and-phase-audit.md) reviews 16 of the 51 buyer cases, retains 12 city notices and leaves 37 cases pending. It raises the observed paired inventory to 123 units across six elections, verifies 59 original competition XML notices and 63 legacy previous-competition references, and supports competition-to-contract chronology for 115 units. Its daily October 2023 export extends source coverage before the monthly window above. The 57-result/118-observation counts in this document describe this earlier federal-audit stage. Historical treatment evidence, actual terms, analytical units, complete deduplication, independent-election precision, below-threshold coverage and pre-2022 sources remain open. GitHub Pages remains deferred until research completion.
