# Bounded Bavaria expansion-route audit

**5 October 2026.** This audit tests the single Bavaria-2020 route allowed by the [early decision block](early-feasibility-decision.md). It combines the existing vote-audited register with one capped TED availability query and a fresh registry/version check. It adds **no historical candidate labels, certified study elections or treatment-effect estimates**. The resulting decision is in the [go/adapt/stop memorandum](go-adapt-stop.md).

The project adapts Florio and Spagnolo (2026), [*Female Mayors and Public Procurement*](https://doi.org/10.2139/ssrn.7046899), to Germany. Schild (2013), Baskaran and Hessami (2018, Hesse mayors; 2025, Bavarian councillors), Arnold and Frank–Stadelmann–Torgler inform the [German literature comparison](literature-design-crosswalk.md). Their historical data access does not establish access to equivalent fields here.

## Election-side scalability and missingness

The existing 997 source-validated decisions cover 2020–2024; **906** concern elections beginning in calendar 2020, including **902** in the general election beginning 15 March 2020. Official larger-municipality PDFs recover **95 named decisions** in that general cohort. Names are matched through complete exact vote vectors. These sources cover municipalities above 10,000 inhabitants, so the named subset is selected by source scope, not representative of all Bavarian municipalities.

| Absolute candidate-difference margin | General-2020 structural decisions | Named decisions | Named decisions with provisional TED results | Supported mixed-title pairs: female wins / losses |
| --- | ---: | ---: | ---: | ---: |
| At most 1 pp | 20 | 1 | 1 | 0 / 0 |
| At most 2 pp | 45 | 6 | 6 | 0 / 1 |
| At most 5 pp | 125 | 16 | 15 | 0 / 3 |
| At most 10 pp | 244 | 31 | 24 | 0 / 3 |

The [band table](bavaria-bounded-band-summary.csv) uses exact decisive source votes. Bands are acquisition diagnostics, not selected RDD bandwidths. The **45 structural decisions within 2 pp are not 45 mixed, named or outcome-eligible elections**. Thirty-nine lack names in the current named register. The six-event ceiling describes the available named route, not the maximum conceivable statewide sample.

Across all 95 named decisions, eight candidate titles are documented, yielding three mixed-title pairs: Mühldorf, Gräfelfing and Mainburg. All three female-presented candidates lost. The title acquisition is selective and has not been independently second-coded. Current GERDA gender labels, first-name predictions and old generic office titles are not substituted for historical candidate evidence.

## Fresh registry/version check

The [official Bavarian officeholder page](https://www.statistik.bayern.de/wahlen/kommunalwahlen/bgm/index.html) links an XLSX dated **14 July 2026**. Its inspected headers identify the incumbent and source-recorded gender. It has **2,056 municipal officeholder rows**, including 1,919 with a 2026 election date; none lists a 2020 election date. It supplies current officeholders, not both historical 2020 finalists. First-ever entry dates cannot identify a renewed term automatically. County rows are excluded from these counts.

GERDA's checked upstream head is now [176259ea551b12a56dcd0c15b168e0e6e608f59a](https://github.com/awiedem/german_election_data/commit/176259ea551b12a56dcd0c15b168e0e6e608f59a), two commits after our frozen acquisition at `030c1fb865ec4e6ef94d5dee2039edde081a0f5d`. The current candidate file was downloaded separately and compared by a row-order-independent semantic digest. **All 68,929 Bavarian rows are unchanged.** The **4,574 rows for 2020–2024 still have zero candidate names and zero gender labels**; all 1,915 Bavarian gender labels belong to 2026. The [pinned current README](https://github.com/awiedem/german_election_data/blob/176259ea551b12a56dcd0c15b168e0e6e608f59a/data/mayoral_elections/final/README.md) describes this source distinction. No newer data are copied into the frozen baseline.

Cite Heddesheimer et al. (2025), [GERDA: German Election Database](https://doi.org/10.1038/s41597-025-04811-5), alongside the later mayoral-extension snapshot. The existing mayoral-data redistribution uncertainty remains; complete candidate files and the officeholder workbook stay local. [Source metadata](bavaria-bounded-source-register.csv) and [input hashes](bavaria-bounded-input-hashes.csv) preserve provenance.

## Bounded procurement availability query

The [TED Search API](https://docs.ted.europa.eu/api/latest/index.html) query is restricted to Germany, the declared city-name variants of the 31 named decisions within 10 pp, local-authority legal type, standard result notices and **publication from 1 November 2023 through 30 September 2026**. This publication interval searches for possible follow-up; it is not the candidate competition cohort, a fixed outcome window or an office-exposure certificate.

The initial geographic-only count was 2,653, exceeding the predeclared 1,500-notice cap. No complete snapshot was acquired for that geographic-only query. Adding the local-authority filter reduced the result to **963 notices**, acquired completely in four pages of at most 250. Checks reject count changes, timeout flags, duplicate notices and checksum differences. This is a complete snapshot of the stated query, **not a complete municipal procurement census**.

Conservative German buyer text and local-authority matches provisionally assign **350 notices to 24 municipalities**. The other 613 comprise 606 unmatched/ambiguous municipal-name cases, six missing/multiple German buyer-name cases and one nonsingle-local-authority case. Derived aliases and city queries can miss abbreviations, shared procurement bodies, alternative buyers or municipalities' outsourced purchasing. Exact text plus legal type is still a provisional identity match; it is not an independently verified buyer/beneficiary mapping. A zero is query absence, not zero procurement.

The [31-election linkage matrix](bavaria-bounded-linkage-matrix.csv) includes every queried event, rather than only municipalities with results. The three supported mixed-title pairs have **78 provisional result notices**: Mühldorf 1, Gräfelfing 62 and Mainburg 15. Only Gräfelfing has publications in 2024, with 33; the other two have none in that calendar publication year in this query. This does not establish their original competition dates or actual procurement volume.

Strict indexed extraction identifies **35 single-lot total-tender counts across six municipalities**. None belongs to a currently supported mixed-title pair. Electronic submissions are not total tenders. Absence from indexed fields is not absence from the original XML/PDF; full documents may recover fields. No mean, single-tender share or procedure-choice effect is estimated. Deduplication, original calls, no-call rules, reporting, common follow-up and exposure remain unaudited here. **Zero main-study elections are certified.**

## Conditional election-level precision

The [pooled scenario table](bavaria-nrw-conditional-precision.csv) combines the named Bavaria inventory with NRW's 55-pair review, excludes already supported NRW same-presentation pairs and respects one-sided title constraints. It assumes every unresolved eligible pair becomes mixed and every election supplies a usable outcome. These assumptions are upper bounds, not labels, acquisition forecasts or main-study eligibility. The result-presence variant restricts **Bavaria only**; NRW remains its conditional maximum, with coverage unverified.

| Margin band | Maximum from the available named Bavaria route | Conditional NRW maximum | Combined conditional maximum | Best-balanced Gaussian pooled-t MDE, alpha .05 / .025 |
| --- | ---: | ---: | ---: | --- |
| At most 2 pp | 6 | 6 | 12 | 1.80 / 2.04 municipality SD |
| At most 5 pp | 16 | 24 | 40 | 0.91 / 1.01 SD |
| At most 10 pp | 31 | 45 | 76 | 0.65 / 0.72 SD |

Restricting Bavaria to municipalities with provisional results lowers the 5-pp maximum to 39 and the 10-pp maximum to 69. These remain very favorable incomplete-data scenarios. With a merely illustrative municipality SD of 10 pp, the 12-election benchmark needs roughly **18 pp** at alpha .05, or **20 pp** at alpha .025. The actual variance and substantively relevant minimum effect remain undetermined.

The calculations use the same independent Gaussian equal-variance two-group model as the earlier memo, with 80% power. **They are not RDD power or evidence supporting interstate pooling.** Pooling requires compatible institutional rules, periods, scope and estimands; a wider margin or a local-randomization assumption cannot simply be imposed to rescue precision. Additional lots cannot increase independent election counts. The larger statewide structural inventory prevents a claim that future German causal research is impossible, but it does not supply the missing current bulk identity/presentation route.

## Reproduction

Use the existing local inputs and the optional pinned numerical environment:

```sh
python -m pip install -r analysis/requirements-feasibility.txt
python src/pilot/bavaria_bounded_route.py --download
python -m unittest discover -s tests
```

Omit `--download` when the snapshot already exists. Existing snapshots cannot be overwritten. The fixed GERDA version and mutable official XLSX must match their pins; a changed download is a new source version requiring review. The script verifies all 15 frozen baseline hashes before/after, the candidate inputs and original source margins. Tests reject joint/ambiguous/nonmunicipal matches, changed or incomplete snapshots, invalid votes and upper bounds that violate observed presentation constraints.

The inspected registry snapshots, full result responses, original candidates and provisional notice records remain in ignored local directories. Published artifacts contain code, source metadata, election-level availability, scenario calculations and explicit unresolved gates. Hesse's older replication package and provider/author contact were not added to this bounded route; neither can be assumed to supply current German assignments. The next publication scope is specified in the decision memo.
