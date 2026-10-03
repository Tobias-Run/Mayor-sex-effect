# NRW: alternative award layouts and completed primary-presentation follow-up

Subsequent audit, 4 October 2026: the [complete 92-notice cohort](nrw-complete-pilot.md) now supplies 106 observed award units with both fields, includes an explicit lot-definition flag for 194586-2023, and preserves unresolved results. The [historical legal note](nrw-term-law.md) replaces the generic appointment-evidence requirement with election acceptance and predecessor exit. The counts below describe the earlier 46-notice stage.

Checked on 3 October 2026. This continues the [expanded NRW pilot](nrw-expanded-pilot.md), within the same 92-notice municipal cohort and three 2020 election events. The project adapts **Florio and Spagnolo's [Female Mayors and Public Procurement](https://doi.org/10.2139/ssrn.7046899)** to Germany; the [literature note](../literature.md) retains the German precedents. **No procurement effect has been estimated.**

Both previously unsupported legacy layouts now supply dated award outcomes. The full-notice pipeline yields **57 award-result units, including 52 with both contract date and total received-tender count**. Exact official presentation evidence has also been recovered for Iserlohn's other finalist. All three pilot pairs now have both mixed public primary presentations documented, with source timing and source category preserved. These results do not certify historical registry gender, complete mayoral terms or procurement responsibility.

## Iserlohn: a bid range is not a winning price

The pinned PDF [131327-2021](https://ted.europa.eu/de/notice/131327-2021/pdf) reports one undivided technical-consultancy contract for the Nußberg school project:

| Field | Explicit source value |
| --- | --- |
| Contract conclusion | **19 October 2020** |
| Total received tenders | **3** |
| Lowest considered offer | EUR 228,000.00 |
| Highest considered offer | EUR 332,000.00 |
| Originally estimated value | EUR 350,000.00 |
| Declared notice total | EUR 350,000.00 |
| Winning contract price | **Not reported as a scalar value** |

The original parser required a scalar awarded value that reconciled with the notice total. This layout instead reports a considered-offer range. The supplement preserves the range, date and count without substituting the lowest offer, highest offer, midpoint or original estimate as the winning price. The awarded-value field stays missing, and the notice retains a monetary-review flag. Its award header labels the unit `1`, but the document explicitly says there is no lot division; it is retained as one undivided contract.

This is also a consequential timing example. The contract predates Joithe's self-reported November entry even though it follows his September runoff victory. Assigning all post-election contracts to the new winner would incorrectly cross that reported entry boundary.

## Geilenkirchen: two award sections cover three lots

The pinned PDF [370898-2022](https://ted.europa.eu/de/notice/370898-2022/pdf) defines lots 1, 2 and 3 but reports two award sections:

| Award label in source | Lots covered | Contract date | Total received tenders | Reported award value |
| --- | --- | --- | ---: | ---: |
| `Los 1 + 2` | 1 and 2 together | 5 July 2022 | **6** | EUR 1.00 |
| `Los 3` | 3 | 5 July 2022 | **2** | EUR 1.00 |

The first section is one grouped-lot award. Its six received tenders are not copied into two separate observations. The parser verifies explicit group members against the declared lot definitions and rejects undefined, duplicated, overlapping or uncovered lots. It stores two award units for this notice, with the grouped label retained.

The two reported award values sum to EUR 2.00, while the PDF and indexed notice both report a total of EUR 1.00. That conflict remains visible as **unreconciled monetary values**. No amount is silently corrected, and neither one-euro award value is treated as a validated economic price. Dates and scoped counts can still be audited separately. Both dated awards overlap Ritzerfeld's documented council-head role; that overlap does not establish personal procurement authority.

## Updated full-notice totals

The buyer universe remains unchanged: 115 notices in the fixed search snapshot, 92 accepted municipal notices, and 23 excluded separate, joint or regional-authority cases. Fifty full PDFs are pinned in the [existing manifest](nrw-expanded-source-manifest.csv); 46 belong to the retained cohort.

| Full-document measure | Current count |
| --- | ---: |
| Retained full notices reviewed | **46** |
| Notices with supported awarded results | 41 |
| Explicit non-award notices | 5 |
| Remaining unsupported layout notices in this reviewed set | **0** |
| Award-result units | **57** |
| Legacy / eForm units | 37 / 20 |
| Units with explicit contract date | 55 |
| Units with explicit total tender count | 53 |
| Units with both date and total tender count | **52** |
| Grouped-lot award units | 1 |
| Bid-range units without a scalar winning price | 1 |
| Reported one-euro award values requiring review | **17** |
| Notices with conflicting notice-total / award-sum values | 1 |
| Dated Geilenkirchen units within its source-bounded head role | 9 |
| Represented independent electoral events | **3** |

The 57 units include all previously recovered awards; they must not be added to the earlier 54-unit total. Layout recovery is complete for these 46 reviewed municipal PDFs, not for every notice in the 92-notice cohort or for municipal procurement generally. Missing values and reporting selection remain substantive measurement gates.

## Iserlohn: exact named official presentation

The publicly accessible [archived person page](https://www.iserlohn.sitzung-online.de/public/kp020?KPLFDNR=1000472) identifies **“Frau Eva-Barbara Kirchhoff”**, exactly matching the state's 2020 decisive candidate `Kirchhoff, Eva-Barbara`. This resolves the primary-source identity/presentation follow-up without guessing a link from the party's shorter name “Eva Kirchhoff”.

The record also displays `Rat der Stadt Iserlohn — Erste stv. Bürgermeisterin — CDU` and a personal-record end date of **11 November 2025**. Those fields concern a deputy and her person record. They do not establish a full-time mayoral term, candidate gender as a registry field, or a 2020 observation date. The page was retrieved in October 2026; its official archived-person presentation is retained with that timing and provenance.

The combined candidate register now has **six primary observations covering the six decisive people** in Iserlohn, Velbert and Geilenkirchen. All three pairs have female and male public primary presentations. Evidence timing differs: dated 2020 municipal/party statements, historical council views and current retrospective/archived person pages remain separate categories. The new [current Velbert deputy page](https://www.velbert.de/rathaus-politik/stellv-buergermeister/in) additionally corroborates Kanschat's official female presentation, but it is stored separately from her dated April 2020 party statement. Its current second-deputy role is not recoded as a historical 2020 role or full-time mayoral authority.

## Joithe: entry claim and dated official activity are distinct

On his [own mayoral biography](https://michael-joithe.de/ihr-buergermeister/), Michael Joithe writes **“Seit meinem Amtsantritt am 02.11.2020”**. The named self-authored statement supplies an initial-entry claim of **2 November 2020**, distinct from the official decisive election date of 27 September 2020. The city separately publishes an [address for 9 November 2020](https://www.iserlohn.de/rathaus-politik/politik/buergermeister/reden-und-video-botschaften-des-buergermeisters/ansprache-9-november-2020), explicitly identifying him as mayor.

The municipal address corroborates activity in office on 9 November. It does not independently certify the exact initial legal start. The autobiographical “Amtsantritt” could refer to taking up work; its legal meaning is not inferred. The pipeline therefore stores a **self-authored entry claim** and **dated official activity** separately, with legal-start and continuous-authority verification left open.

Within the reviewed Iserlohn awards, the 19 October 2020 contract precedes that reported entry; the 19 December 2020 contract follows it. These are date comparisons with a stated source claim, not mayoral treatment or decision-responsibility assignments. The new evidence also does not determine the legal boundary of Joithe's 2025 renewed term. Velbert's actual 2020 renewal boundary remains unresolved; a 2014 first-entry biography or a later oath cannot substitute for it.

## Reproduction and publication scope

After running the earlier [expanded-pilot commands](nrw-expanded-pilot.md#reproduce-the-supplement), run:

```bash
python src/pilot/nrw_full_ted_awards.py
python src/pilot/nrw_primary_presentation_update.py --download
python -m unittest discover -s tests -q
```

The updated full-notice parser uses the same pinned PDFs. Its restricted alternative-layout handler preserves offer ranges and explicit grouped lot labels, while keeping the ordinary reconciled parser for scalar legacy layouts. `nrw_primary_presentation_update.py` combines the earlier candidate observations with source-pinned archived/current official evidence and the separate entry/activity records. Omit `--download` to audit cached HTML; changed live pages require source review rather than automatic pin updates.

All real-source pipelines complete successfully and **45 offline tests pass**. Six new tests protect missing winning prices, grouped-unit counts, incomplete or overlapping lot groups, exact archived identity, deputy versus full-time roles, and self-authored entry versus official activity. The [four-source completion manifest](nrw-pilot-completion-source-manifest.csv) and [aggregate summary](nrw-pilot-completion-summary.csv) report provenance and counts. The original 50-PDF manifest continues to cover the two recovered award cases.

Raw source pages, addresses/contact details, person-level outputs and complete contract records remain in ignored local directories. Public publication contains original code and limited cited evidence. No main-study treatment or procurement responsibility has been assigned, and GitHub Pages remains deferred until completion of the research.

## Remaining research gates

Prioritize formal entry/renewal records for Iserlohn and Velbert, continuity and delegation evidence, and full-document recovery for the unreviewed municipal notices. Establish a uniform historical gender/presentation measurement protocol before expanding beyond the pilot. Monetary and environmental outcomes still need validated definitions, missing-data rules and procedure/lot deduplication. Broader close-election coverage and sufficient independent electoral clusters are required before precision assessment and preregistration.
