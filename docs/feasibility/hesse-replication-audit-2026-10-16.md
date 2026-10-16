# Hesse replication archive: bounded access and reuse audit

16 October 2026. Follow-up to the [literature crosswalk](literature-design-crosswalk.md), supporting the adaptation of Florio and Spagnolo (2026). **A specifically named mayor-election dataset is listed, but neither its contents nor its reuse conditions could be validated. No usable elections or procurement links are added.**

## Identity and evidence actually obtained

The American Economic Association's [article page](https://www.aeaweb.org/articles?id=10.1257/pol.20170045) links Baskaran and Hessami's 2018 article to [openICPSR project 114710, V1](https://doi.org/10.3886/E114710V1). The bibliographic distribution date is 13 October 2019. Indexed test-server project 114662 is a different project identifier and is not substituted for the linked archive.

The official [DDI metadata export](https://pcms.icpsr.umich.edu/pcms/api/1.0/oai/studies?metadataPrefix=oai_ddi25&verb=GetRecord&identifier=114710&version=V1) was acquired directly and hash-pinned. It identifies the study and depositor-created **Other/custom license**, referring users to the separate license file. The record's metadata license applies to the catalog record, not automatically to the data. The export has no variable-level entries, so it does not establish municipality IDs, dates, candidate identities, gender fields or votes. Its generated date fields differ from the bibliographic distribution date; they are not treated as a new dataset version.

The [official migration notice](https://www.icpsr.umich.edu/sites/icpsr/openicpsr-has-moved) was also acquired: openICPSR is integrated into ICPSR, whose catalog retains the projects. This explains why current discovery should use the official catalog as well as the DOI; it does not itself provide this project's payload or permissions.

Direct requests to the legacy license/data view pages and DOI returned HTTP 403. Separately available cached search-tool representations permit metadata inspection of the public listings. Their hashes are retained as representations, not mislabelled as original file hashes. Raw responses, cached representations and the prospective protocol remain private. See the [public source manifest](hesse-replication-source-manifest-2026-10-16.csv) and [summary](hesse-replication-audit-2026-10-16-summary.json).

## Concrete payload leads and access result

The [dataset directory](https://www.openicpsr.org/openicpsr/project/114710/version/V1/view?path=/openicpsr/114710/fcr:versions/V1/data/datasets&type=folder) lists eight Stata files. Most relevant is [mayor_election_data.dta](https://www.openicpsr.org/openicpsr/project/114710/version/V1/view?path=/openicpsr/114710/fcr:versions/V1/data/datasets/mayor_election_data.dta&type=file), displayed as 220.4 KB. A separate main dataset is listed at 33.9 MB. These are displayed sizes, not acquired byte counts. The data directory also lists Stata figure/table drivers and supporting ado files. No code payload was inspected or executed.

The [readme listing](https://www.openicpsr.org/openicpsr/project/114710/version/V1/view?path=/openicpsr/114710/fcr:versions/V1/data/Readme/Readme.pdf&type=file) identifies a PDF displayed at 61.6 KB. Its download and the mayor-file download both redirect to ICPSR authentication. The [license-file listing](https://www.openicpsr.org/openicpsr/project/114710/version/V1/view?path=/openicpsr/114710/fcr:versions/V1/LICENSE.txt&type=file) identifies a 14.6 KB file, but its download returned 403. A filename and generic archive policy do not establish the contents of a project-specific license. No authentication, new terms acceptance, protected-route bypass or author contact was attempted.

## What the existing German paper can teach us

The acquired [2017 Konstanz working paper](https://www.uni-konstanz.de/FuF/wiwi/workingpaperseries/WP_09_Baskaran_Hessami_2017.pdf), printed page 9, describes official candidate identities, gender, party, votes and dates. Its 1993–2015 inventory reports 1,721 mayoral elections, 268 mixed races and 55 close races, split 29 female/26 male wins. These are authors' counts, not recomputed archive observations; their margin convention is not automatically our percentage-point scale. The pinned PDF was reread (SHA-256 `029ba808cdceaf8eae55eb4baacf06b28dbfd97edb1619adee87fbfd59b2aabd`).

An official candidate field could reduce individual-document research, subject to verified provenance and permitted use. The replication file's retained fields and equivalent modern availability remain unknown. Its historical election period precedes the modern national procurement archive; compatible original-supported windows require a separate joint-yield test.

The separate [2026 Hesse latest-election workbook audit](hessen-latest-register-scope-audit.json), already completed on 11 October, also remains relevant: 51 of eighty retained event dates/vote vectors match, with explicit winner gender fields in 41 matching rows, but no opponent identity/gender fields. That latest-election-only export does not supply a complete historical assignment register. The historical replication lead and the modern official workbook therefore address different, still-unclosed gaps. No new original workbook retrieval is claimed here.

The paper's 109,017 council candidates are outcome observations, not independent mayoral assignments or procurement observations. Final-journal PDF access failed again; methods remain attributed to the working paper.

## Reuse decision and bounded next condition

**Access/rights audit completed with an unresolved payload/rights outcome.** It is not a completed replication or a finding that reuse is prohibited. Before any Hesse sample proposal, an authorized original package must provide readable license and readme, verifiable municipality identifiers and decisive election dates/votes, documented gender provenance and a complete assignment inventory. Then verify chronological overlap with an accessible procurement source and actual original-supported joint yield. No current main-study sample is enlarged on the strength of this listing.

The source-budget accounting records five direct HTTP requests and fourteen explicit web-navigation targets, plus six discovery queries. The prospective eighteen-request cap was implemented only in the direct-fetch helper; combining the two transports gives nineteen URL requests, **one above the recorded cap**. This bookkeeping deviation is disclosed rather than retroactively raising the cap. Retrieval stopped at the access gates; no payload or individual candidate research followed. Future acquisition budgets must count both transports in one ledger.

No source originals, personal data, archive code or datasets are republished. Public outputs are the access assessment, provenance and aggregate summary. The causal reopening gates and independent-review dependency remain unchanged.
