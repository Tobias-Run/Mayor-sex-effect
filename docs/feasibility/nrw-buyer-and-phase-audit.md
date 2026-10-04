# NRW buyer scope and procurement-phase linkage

Reviewed on **4 October 2026**. This advances the German adaptation of **Florio and Spagnolo (2026), [Female Mayors and Public Procurement](https://doi.org/10.2139/ssrn.7046899)**. The [literature note](../literature.md) retains German precedents, including Schild's Bavaria study and Baskaran and Hessami's work on women's representation. The Italian baseline assigns procedures by tender publication under the elected mayor; publication of a later result and contract conclusion describe different stages. The [proposed protocol](../research-protocol.md) retains municipal election-level ITT, subject to verified buyer/beneficiary scope, actual term windows and historical treatment measurement.

**The acquisition inventory now has 237 retained result notices. There are 123 observed award-result units with an explicit total tender count and contract date, across six municipal elections. Of these, 115 also have a documented competition-publication date with supported chronology. These are feasibility observations, before complete deduplication and analytical unit selection. No causal effects or main-study treatment assignments have been produced.**

Earlier [PDF](nrw-complete-pilot.md), [indexed-procedure](nrw-procedure-and-presentation-audit.md) and [federal XML](national-procurement-open-data.md) outputs remain unchanged as separate stages. A dated award observation is not necessarily one legal contract or one independent election.

**Later procedure supplement:** the [procedure-specific timing and term audit](nrw-procedure-scope-and-term-followup.md) verifies original types for every paired observation. Three of the eight timing cases explicitly have no prior call and require a separate timing rule; five remain competitive-procedure identity/date cases. Two same-title Geilenkirchen competition candidates have conflicting GUIDs and do not add supported dates. New municipal year-history/oath evidence and a Werdohl official 2020 nomination retain their limits. The counts below describe this preceding phase-audit stage.

## Resolving individual buyer cases

The 51-case queue was queried through the independently public TED Search API. All 17 shared indexed fields agree with the preceding snapshot. Sixteen cases have exact UUID/version matches in the already pinned federal original-XML archives; each receives an individual [source-pinned decision](nrw-buyer-followup-decisions.csv).

| Original-source decision | Notices | Treatment in the acquisition inventory |
| --- | ---: | --- |
| Sole Kreisstadt Unna contracting party, including municipal departments | 11 | Retain |
| Stadt Werdohl represented by KUBUS, with explicit city gas-supply beneficiary | 1 | Retain |
| Joint Rhein-Erft-Kreis/Stadt Frechen electricity procurement | 1 | Exclude from the direct municipal pilot |
| Registry procurement by six counties, including Kreis Unna | 1 | Exclude; Kreis Unna is distinct from Kreisstadt Unna |
| Unna notices mentioning Stadtbetriebe Unna in a performance address | 2 | Municipal beneficiary remains pending |
| Earlier notices without an acquired original full notice | 35 | Remain pending |

This adds **12 retained notices**, leaving **37 pending cases**. A delivery/performance address does not establish the beneficiary's legal identity. No independent-entity claim for Stadtbetriebe Unna is made: the ordinary homepage request returned HTTP 503 and supplied no usable legal evidence. Personal mayoral signatures are not an eligibility requirement for municipal ITT.

Five added notices have both supported contract dates and explicit result-level total counts:

| Municipality | Result publication | Contract conclusion | Total tenders |
| --- | --- | --- | ---: |
| Unna | 374488-2024 | 21 June 2024 | 1 |
| Unna | 610665-2024 | 13 September 2024 | 1 |
| Unna | 657189-2024 | 25 October 2024 | 1 |
| Unna | 740622-2024 | 2 December 2024 | 5 |
| Werdohl | 519951-2024 | 26 August 2024 | 5 |

The other seven retained notices add no paired observation. Missing original contract dates, missing total statistics and unsupported contract/tender links remain missing or flagged.

## Competition dates and correction histories

An expanded indexed request covers all **72 known procedure GUIDs** in the previous retained inventory and the 16 reviewed scope cases, without a lower date restriction and with publication through **31 December 2024**. It returns **59 competition notices for 45 GUIDs**. All 59 match original federal XML by exact notice UUID/version, procedure GUID and contracting-party names. This is complete for the pinned query, not evidence of complete municipal procurement coverage or earliest-ever publication.

The 14 existing monthly XML archives contain 58 matches. Competition **665574-2023**, published on **31 October 2023**, is verified in the independently public daily export for that date, adding one pinned archive. Its XML issue date is **30 October 2023**; dispatch/issue and actual indexed publication stay distinct. Ordinary October monthly requests returned HTTP 503; the documented daily export returned HTTP 200. This used the public German export API and did not retry protected TED web full notices.

Only **55 competition notices, in 42 GUID groups**, align to a sole contracting party in the retained municipal scope. The four other notices concern the excluded county purchase or the two unresolved Stadtbetriebe cases; their context does not add municipal award observations.

Within those 42 groups, **39 have one complete, chronological, acyclic documented root**. Exact parent UUID **and version** must match. Three groups have multiple competition notices without an explicit connecting correction reference:

| Municipality | Competition publications | Consequence |
| --- | --- | --- |
| Velbert | 485593-2024; 560607-2024 | Original baseline publication remains under review |
| Velbert | 388784-2024; 406944-2024 | Original baseline publication remains under review |
| Unna | 386531-2024; 418762-2024; 484646-2024; 733445-2024 | Original baseline publication remains under review |

The earliest row is not automatically selected in these three groups. Even a complete checked graph supplies a **first documented competition in that graph**, rather than proof that no earlier call exists in another notice family. Sole-city contracting-party alignment also does not settle every legal beneficiary or actual term question.

The original result XML verifies two explicit previous-competition references: Geilenkirchen **707371-2023 → 546284-2023** and Werdohl **253377-2024 → 96667-2024**. The source locator is `cac:TenderingProcess/cac:NoticeDocumentReference/cbc:ID`. Both targets have pinned indexed competition metadata; Werdohl's target also has original XML in the 59-notice set. Geilenkirchen's older target has no indexed GUID. This literal reference supports the link without inventing a GUID or globally merging local contract labels.

## Recovering older competition references

All **63 retained legacy full-notice PDFs**, including non-awards, are rechecked against their source hashes and byte counts. Each has one explicit previous competition reference in **Section IV.2.1**. All 63 cited publication numbers are independently returned as `cn-standard` notices by the public TED index, with a sole city buyer aligned to the result municipality and publication preceding the result notice.

The original result PDF establishes the reference. The previous competition's **date and buyer are indexed metadata**; its original legacy full notice has not been acquired in this step. Header identifiers, references in Section V and supplier names cannot substitute for Section IV.2.1. Literal OJ references and source hashes are retained in the [legacy reference ledger](nrw-phase-legacy-references.csv).

Three linked competition dates precede the regular **1 November 2020 council boundary**:

| Municipality | Competition publication and date | Linked result | Contract conclusion |
| --- | --- | --- | --- |
| Iserlohn | 279440-2020; 16 June 2020 | 131327-2021 | 19 October 2020 |
| Iserlohn | 481715-2020; 13 October 2020 | 21732-2021 | 19 December 2020 |
| Iserlohn | 517850-2020; 30 October 2020 | 103107-2021 | 1 February 2021 |

The June publication also precedes Iserlohn's decisive election on 27 September 2020. The two October calls occur after the election but before the regular council boundary, while their contracts occur afterwards. Election date, council boundary and legally supported individual office entry are separate. The [historical term audit](nrw-term-law.md) retains Iserlohn's actual-entry evidence gap; this diagnostic does not automatically include or exclude observations from the main study.

## Coverage and remaining gates

| Municipality | Observed dated/count units | Distinct result notices | Supported competition/contract pairs |
| --- | ---: | ---: | ---: |
| Velbert | 45 | 32 | 42 |
| Viersen | 11 | 4 | 11 |
| Geilenkirchen | 18 | 15 | 16 |
| Iserlohn | 44 | 26 | 44 |
| Werdohl | 1 | 1 | 1 |
| Unna | 4 | 4 | 1 |
| **Total** | **123** | **82** | **115** |

Six municipal elections, rather than 123 award rows, determine the current independent-election coverage. There is no finding that this pilot provides adequate RDD precision or a representative sample. The paired observations retain grouped contracts and historical notice versions; complete procedure/contract deduplication, analytical units and weighting remain open.

Eight observations lack a supported baseline competition date: Velbert **17130-2024**, **726107-2024**, **786759-2024**; Geilenkirchen **196766-2024**, **126957-2024**; and Unna **374488-2024**, **610665-2024**, **657189-2024**. Two Velbert observations have unresolved correction graphs; six have no linked competition. Contract/result publication dates never fill this gap. There are **zero negative lags** among the 115 supported pairs.

Next priorities are these eight timing gaps, the 37 remaining buyer cases, consistent historical finalist measurement and source-supported initial/renewed terms. Broader coverage and independent eligible elections are needed before minimum-detectable-effect assessment. The Italian timing rules must be adapted explicitly, including any overlap or washout restrictions. GitHub Pages remains deferred until the research is complete.

## Reproduction and source limits

Run after the [complete PDF cohort](nrw-complete-pilot.md), [procedure audit](nrw-procedure-and-presentation-audit.md) and [federal export audit](national-procurement-open-data.md):

```bash
python src/pilot/nrw_buyer_followup.py --download-index
python src/pilot/federal_procurement.py 2023-10-31 --format eforms
python src/pilot/nrw_phase_linkage.py --download-index --write-public-tables
python -m unittest discover -s tests
```

The buyer and phase requests are pinned in [buyer metadata](nrw-buyer-followup-ted-request-manifest.json), [GUID competition metadata](nrw-phase-ted-request-manifest.json), [legacy competition metadata](nrw-legacy-competition-ted-request-manifest.json) and the previously published [explicit-reference metadata](nrw-procedure-ted-request-manifest.json). The [additional daily export manifest](nrw-phase-additional-export-manifest.json) records URL, byte count, hash and retrieval time. Changed mutable responses require review before pin updates.

Source data and generated working files remain local. Offline reproduction requires the previously archived PDFs; current protected TED web access prevents reacquiring those PDFs through that route. The public index and German bulk exports are independently accessible sources. The scripts refuse incomplete or changed snapshots and do not bypass protected endpoints.

Public derived outputs are the [summary](nrw-buyer-and-phase-summary.csv), [concentration table](nrw-buyer-and-phase-concentration.csv), [237-result phase ledger](nrw-phase-links.csv), [123-observation timing ledger](nrw-phase-observations.csv), [59 original competition source records](nrw-phase-competition-sources.csv), [63 legacy references](nrw-phase-legacy-references.csv), and the 16 individual buyer decisions. The combined suite passes **110 offline tests**, covering city/county separation, joint buyers, represented beneficiaries, delivery-address ambiguity, exact parent versions, cycles, unlinked roots, literal legacy references and distinct timing boundaries.
