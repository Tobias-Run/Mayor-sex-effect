# Female Mayors and Public Procurement in Germany

Does electing a female mayor causally affect procurement practices and outcomes in German municipalities?

This repository supports an empirical research project using close mixed-gender mayoral elections and procurement records. The proposed identification strategy is a regression discontinuity design (RDD). A feasibility study must establish lawful data linkage, measurement quality, and sufficient precision before the main study is specified.

**Status:** project setup and feasibility planning. No empirical findings are available. Literature claims, data access, and the novelty claim in the original pitch remain to be independently verified.

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

No analysis software stack has been selected yet. Dependencies and execution commands will be documented when the pilot pipeline is implemented. Confidential records and credentials must never be committed. A public repository does not imply permission to redistribute source data.
