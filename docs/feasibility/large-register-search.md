# Large-register search: GERDA changes the acquisition strategy

Checked: 3 October 2026. **The current GERDA repository contains a cross-state mayoral candidate dataset and mayor panels.** This updates our earlier provisional conclusion that we would need to construct the entire register from separate local sources. A nationwide official register is still not established; a large reusable research compilation is now located and downloaded.

## GERDA: paper versus current repository

Heddesheimer, Vincent, Hanno Hilbig, Florian Sichart, and Andreas Wiedemann (2025). *GERDA: The German Election Database*. Scientific Data 12, 618. [DOI](https://doi.org/10.1038/s41597-025-04811-5).

The paper primarily describes harmonized municipal council, state and federal party results. The [current repository](https://github.com/awiedem/german_election_data) has subsequently expanded its scope to mayoral candidates and person-level mayor panels. Therefore the paper alone understates what is now available. [Mayoral dataset documentation](https://github.com/awiedem/german_election_data/blob/main/data/mayoral_elections/final/README.md).

The dataset documentation describes coverage in **13 states**, with unequal historical ranges and completeness. This is not full coverage of every municipality and year. It also includes head-of-municipal-association elections, which require office-type restrictions for our project. County executives have separate files.

## Download and initial checks

The candidate CSV downloaded through GitHub's media/LFS endpoint contains **113,345 rows and 47 fields**. Fields include municipality identifiers, election and runoff dates, names where available, nominations, exact candidate votes in both rounds, ranks, winner flags, source-quality flags, gender and gender provenance.

Pinned source commit: `030c1fb865ec4e6ef94d5dee2039edde081a0f5d`.

Downloaded CSV SHA-256: `5cf7c8f7695cf17d3001ffe49ba5bb5a8f2800be8426754c1db3143b200fba0e`.

The file is stored locally under ignored `data/raw/gerda/`. A normal raw GitHub URL initially returned a Git LFS pointer; that pointer was not interpreted as a CSV. The subsequent media download retrieved the actual 26 MB dataset.

| Initial local file audit | Bayern | NRW |
| --- | --- | --- |
| Candidate rows, all available years | 68,929 | 5,117 |
| Rows in 2020 | 4,239 | 1,349 |
| Named candidate rows in 2020 | 0 | 1,349 |
| Gender provenance in 2020 | Empty for all inspected rows | `predicted` for all 1,349 rows |

These are candidate rows, not independent elections. NRW years in the file are 2009, 2014, 2015, 2020 and 2025. Bayern's documented historical source is an official *Wahlen seit 1945* workbook plus the 2026 officeholder supplement. Individual source completeness and release rights still require assessment.

**Independent NRW check:** for all 102 previously audited district-municipality runoffs in 2020, the sorted pair of GERDA candidate runoff vote counts exactly matches the independently downloaded official detailed files: **102/102 matched, no discrepancies**. This validates votes in this subset, not all variables or states.

## Important limits for the research

- **Gender prediction is not verified gender.** Code and provenance explicitly identify first-name classification using `gender-guesser`. Use predicted labels only as screening leads; prioritize independent verification near the cutoff. Our primary eligibility rules must explicitly address provenance.
- **Bayern historical identities remain a gap.** The public dataset does not provide historical candidate names or gender for the audited 2020 rows. The compilation gives us votes and elections, but cannot by itself identify woman-versus-man contests.
- **Terms need caution.** The mayor-panel documentation says `term_start_date` is first entry for Bayern but first election date elsewhere. Annual panels are forward-filled. Neither is automatically a verified exact term interval suitable for contract-level assignment.
- **License scope is dataset-specific.** The root README's explicit CC BY permission is for processed federal election data; it does not establish mayoral-data redistribution rights. Keep the downloaded candidate data local while reviewing source terms. The mayoral README describes anonymization and scientific-use limitations for some states.
- **Dates and source flags matter.** Documentation records corrected source errors, superseded elections and missing decisive rounds. Do not drop those flags during import. A current snapshot contains elections beyond the session's current date; restrict all temporal samples to a documented cutoff and investigate snapshot timing rather than claiming future data were available historically.
- **Harmonization is not sufficient for electoral identification.** Use original election units with explicit geographic mapping. Population-weighted aggregation of historical results can change an election margin and does not necessarily preserve the assignment unit of a mayoral RDD.

## Additional large-source leads

1. **Baskaran and Hessami (2018):** *Does the Election of a Female Leader Clear the Way for More Women in Politics?* American Economic Journal: Economic Policy 10(3): 95–121. [Official article](https://www.aeaweb.org/articles?id=10.1257/pol.20170045), [linked replication package](https://doi.org/10.3886/E114710V1). The article page reports 109,017 council candidates across four elections in all 426 municipalities of a German state and a close mixed-gender mayoral design. Replication contents have not yet been inspected; council candidate volume is not mayoral election count.
2. **Hessami (2018):** GERDA's documentation identifies *Accountability and Incentives of Appointed and Elected Public Officials*, with [Harvard Dataverse DOI 10.7910/DVN/FZWOMK](https://doi.org/10.7910/DVN/FZWOMK), as a source of historical Hessian names. This is a documented lead, not a reviewed dataset.
3. **Konrad Adenauer Foundation's Kommunales Wahllexikon:** the GERDA paper cites Bremer, Di Carlo and Wansleben (2023), *The constrained politics of local public investment under cooperative federalism*, as using local executive party information from annual reports for 1990–2018. Potentially useful for political context, but no candidate-complete election register or access route was verified here.
4. **Arnold (2018):** *Turnout and Closeness: Evidence from 60 Years of Bavarian Mayoral Elections*, cited by GERDA, provides another historical Bavaria research lead. Replication/access remains unreviewed.

Commercial/current-mayor directory probes did not establish usable historical registers: `buergermeister.de` timed out and `kommunalwahl.de` displayed a placeholder. Zenodo's broad unquoted search queries returned mostly irrelevant results; the exact phrase `German mayoral` returned zero hits. Those results do not prove absence of datasets.

## Acquisition decision

Use the **pinned GERDA mayoral compilation as the candidate base for a structured audit**, preserving provenance and uncertainty. Retain the official-source pilot as independent validation rather than continuing to reconstruct every vote from scratch. Focus further acquisition on (a) Bayern's missing historical identities/gender, (b) verifying NRW predicted gender near the cutoff, (c) actual terms, and (d) permissible procurement linkage.

No research feasibility approval or causal estimate follows from finding this dataset. A large nominal register can still contain too few usable mixed-gender close elections in the procurement window.
