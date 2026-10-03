# Female Mayors and Public Procurement in Germany

Does electing a female mayor causally affect procurement practices and outcomes in German municipalities?

This repository supports an empirical research project using close mixed-gender mayoral elections and procurement records. The proposed identification strategy is a regression discontinuity design (RDD). A feasibility study must establish lawful data linkage, measurement quality, and sufficient precision before the main study is specified.

## Adapting the Italian study to Germany

**This project adapts Florio and Spagnolo (2026), [*Female Mayors and Public Procurement*](https://doi.org/10.2139/ssrn.7046899), to the German institutional and data context.** Their Italian study provides the starting point for linking close mayoral elections to procurement outcomes. We plan to adapt the close-election RDD and extend the outcome scope to documented environmental, social, and innovation criteria, subject to data availability.

The German application builds on existing research: Schild's *Do Female Mayors Make a Difference? Evidence from Bavaria* addresses female mayors and municipal fiscal decisions; Baskaran and Hessami's [*Women in Political Bodies as Policymakers*](https://doi.org/10.2139/ssrn.4377785) provides related work on women's representation and policy outcomes. These studies inform the institutional and methodological groundwork; they do not establish this project's procurement effects.

See the [literature and adaptation note](docs/literature.md) for references, verification status, and the distinction between inherited design elements and proposed extensions. The German novelty claim remains provisional.

**Status, 3 October 2026:** Bavaria is the active feasibility workstream. The historical vote source is acquired, and all 997 conservatively screened two-person decisions for 2020–2024 match its decisive votes and round structure. Both finalists' gender, actual term dates and historical procurement linkage remain open. See the [Bavaria assessment and reproducible register audit](docs/feasibility/bavaria-feasibility.md). No procurement effects have been estimated; the main study and novelty claim remain conditional on further evidence.

**Project language:** English for documentation, code, variable names, and research outputs. Original source documents retain their original language.

## Research workflow

1. Verify the literature and map electoral and procurement institutions.
2. Establish data access and build an eligible election register.
3. Pilot municipality–buyer linkage and assess measurement and coverage.
4. Estimate minimum detectable effects and decide whether the RDD is feasible.
5. Preregister the main analysis, construct the analysis dataset, and estimate effects.
6. Complete robustness checks, the manuscript, and reproducibility review.
7. Publish an interactive research companion using **GitHub Pages after completion of the research**.

The main study is conditional on the feasibility decision. A panel design would require a separate identification argument.

## Navigate the project

| Resource | Purpose |
| --- | --- |
| [Bavaria feasibility assessment](docs/feasibility/bavaria-feasibility.md) | Historical register, 997 source-validated decisions, German data precedents and procurement gaps |
| [Prepared Bavaria inquiry](docs/feasibility/bavaria-data-inquiry.md) | Concrete gender/term-data request and verified provider route; not sent |
| [GERDA structural screen](docs/feasibility/gerda-structural-screen.md) | Conservative contest counts and gender provenance, with executable audit |
| [Large-register discovery](docs/feasibility/large-register-search.md) | GERDA mayoral candidates located; 102 NRW vote pairs independently matched |
| [NRW exact-margin screen](docs/feasibility/nrw-margin-screen.md) | Counts within descriptive margins; gender verification remains pending |
| [District-municipality pilot](docs/feasibility/smaller-municipality-pilot.md) | Off-cycle Hallbergmoos election, gender and timing evidence |
| [Bavaria archive expansion](docs/feasibility/bavaria-archive-expansion.md) | Additional Augsburg and Nuremberg sources and validation |
| [Bavaria historical pilot](docs/feasibility/bavaria-historical-pilot.md) | Named candidates and exact votes from Munich 2020 |
| [Bavaria and NRW extraction audit](docs/feasibility/bavaria-first-nrw-second.md) | Official Bavaria workbook and 102 validated NRW runoff files |
| [Registers and German precedents](docs/feasibility/registers-and-german-precedents.md) | National vs. state sources and practical lessons from German papers |
| [Research protocol](docs/research-protocol.md) | Question, estimand, design, and interpretation |
| [Feasibility workplan](docs/feasibility/workplan.md) | Evidence required before proceeding |
| [Roadmap](docs/roadmap.md) | Milestones and completion criteria |
| [Data management](docs/data-management.md) | Provenance, access restrictions, and reproducibility |
| [Source register](docs/feasibility/source-register.csv) | Initial source leads and verification status |
| [Decision log](docs/decision-log.md) | Record consequential research decisions |
| [Interactive companion plan](website/README.md) | Deferred GitHub Pages scope and release gate |
| [Contribution guide](CONTRIBUTING.md) | Working conventions |

## Repository layout

```text
analysis/          Analysis scripts and their documentation
src/               Reusable collection, cleaning, and linkage code
data/              Local raw, interim, and processed data (ignored by Git)
docs/              Protocol, feasibility evidence, and research decisions
sources/project/   Original German research pitch
outputs/           Generated local results (ignored by Git)
manuscript/        Research paper and supporting text
website/           Plan for the post-research interactive companion
```

The current election acquisition and audit scripts use Python's standard library; [reproduction commands](docs/feasibility/bavaria-feasibility.md#reproduction) are available. The main econometric software stack is not yet selected. Confidential records and credentials must never be committed. A public repository does not imply permission to redistribute source data.
