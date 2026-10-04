# Female Mayors and Public Procurement in Germany

Does electing a female mayor causally affect procurement practices and outcomes in German municipalities?

This repository supports an empirical research project using close mixed-gender mayoral elections and procurement records. The proposed identification strategy is a regression discontinuity design (RDD). A feasibility study must establish lawful data linkage, measurement quality, and sufficient precision before the main study is specified.

## Adapting the Italian study to Germany

**This project adapts Florio and Spagnolo (2026), [*Female Mayors and Public Procurement*](https://doi.org/10.2139/ssrn.7046899), to the German institutional and data context.** Their Italian study provides the starting point for linking close mayoral elections to procurement outcomes. We plan to adapt the close-election RDD and extend the outcome scope to documented environmental, social, and innovation criteria, subject to data availability.

The German application builds on existing research: Schild's *Do Female Mayors Make a Difference? Evidence from Bavaria* addresses female mayors and municipal fiscal decisions; Baskaran and Hessami's [*Women in Political Bodies as Policymakers*](https://doi.org/10.2139/ssrn.4377785) provides related work on women's representation and policy outcomes. These studies inform the institutional and methodological groundwork; they do not establish this project's procurement effects.

See the [literature and adaptation note](docs/literature.md) for references, verification status, and the distinction between inherited design elements and proposed extensions. The German novelty claim remains provisional.

**Status, 4 October 2026:** NRW is the active acquisition workstream. All 380 scheduled-2020 mayoral elections and 1,349 candidate records have been audited, supplying 214 two-person decisions. The [six-municipality extension](docs/feasibility/nrw-extension.md) adds **133 exact-label municipal notices**, bringing the combined acquisition inventory to **225 retained indexed notices across eight election events**. Fifty-one new buyer-scope cases remain pending; new full-text retrieval encounters an automated-access challenge. Five election pairs now have both public primary presentations documented, with their observation timing preserved.

The earlier [complete NRW pilot](docs/feasibility/nrw-complete-pilot.md) has full PDFs for all 92 retained notices and **106 observed award-result units with contract dates and total tender counts across three elections**; the extension adds no verified tender-count outcomes yet. Non-awards, pending/review cases and monetary/lot conflicts remain distinct. The [municipal register audit](docs/feasibility/municipal-tenure-registers.md) locates three tenure CSVs through GovData, verifies Düsseldorf's actual 2020 head transition and identifies a stale open-ended Münster row. The [historical legal audit](docs/feasibility/nrw-term-law.md) verifies entry through election acceptance and predecessor exit. Coverage, dated gender measurement, individual terms, responsibility and precision remain research gates; **no causal effects have been estimated**.

The [Bavaria candidate, tenure and legacy-award register](docs/feasibility/bavaria-candidate-and-tenure-register.md) remains available: 997 source-validated structural pairs, 95 named 2020 decisions, eight official title observations, three mixed-title pairs, two source-bounded tenure intervals and a historical 18-notice procurement pilot. Full Mühldorf legacy PDFs recover five dated award units within two of those notices. Bavaria's unresolved measurement and coverage gates remain explicit.

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
| [NRW six-municipality extension](docs/feasibility/nrw-extension.md) | 133 additional indexed notices, 51 pending scope cases, five primary-presentation pairs and full-text access status |
| [Municipal tenure-register audit](docs/feasibility/municipal-tenure-registers.md) | GovData discovery, Düsseldorf heads versus deputies, year-only Münster dates and a stale current-role entry |
| [Complete NRW pilot](docs/feasibility/nrw-complete-pilot.md) | All 92 full notices, 106 dated/count award units, price/lot flags and unresolved result information |
| [Historical NRW term rules](docs/feasibility/nrw-term-law.md) | 2020 council boundary, acceptance/predecessor entry rule and individual evidence gaps |
| [Earlier NRW follow-up](docs/feasibility/nrw-pilot-completion.md) | Bid ranges, grouped awards, 52 dated units with tender totals, exact Iserlohn candidate evidence and entry/activity source distinctions |
| [Expanded NRW pilot](docs/feasibility/nrw-expanded-pilot.md) | Completed buyer-scope queue, 92 municipal notices, 49 dated award/lot units with counts and dated party-source candidate evidence |
| [NRW operational pilot](docs/feasibility/nrw-operational-pilot.md) | 55 strictly matched result notices, named title evidence, role boundaries and full legacy award/cancellation checks |
| [Statewide NRW election register](docs/feasibility/nrw-statewide-election-register.md) | 380 audited elections, 1,349 candidates, 214 decisive pairs and documented GERDA identity exceptions |
| [Bavaria candidate and tenure register](docs/feasibility/bavaria-candidate-and-tenure-register.md) | 190 candidate records, three mixed-title pairs, tenure boundaries and five dated legacy award units |
| [Bavaria operational pilot](docs/feasibility/bavaria-operational-pilot.md) | Official candidate identities recovered and historical municipal TED data linked |
| [GERDA usability and Bavaria follow-up](docs/feasibility/gerda-usability-and-bavaria-followup.md) | Person-panel audit, 53 dated gender leads and historical municipal title evidence |
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
