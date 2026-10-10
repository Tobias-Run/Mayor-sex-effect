# Female Mayors and Public Procurement in Germany

Does electing a female mayor causally affect procurement practices and outcomes in German municipalities?

This repository supports an empirical research project using close mixed-gender mayoral elections and procurement records. The proposed identification strategy is a regression discontinuity design (RDD). A feasibility study must establish lawful data linkage, measurement quality, and sufficient precision before the main study is specified.

**English report draft available, 9 October 2026:** read [*Can German Municipal Data Support a Female-Mayor Procurement Study?*](manuscript/feasibility-report.md) or download the [PDF](manuscript/feasibility-report.pdf). It consolidates the evidence frozen on **5 October**, with sample-flow and assumption-based precision figures, a fact ledger and reproduction from 22 pinned public inputs. The current causal launch is **no-go**: four supported mixed pairs within 2 pp, only three provisional common-window links, and zero certified main-study elections. This is a feasibility finding, not a finding of no effect. Independent second coding is uncompleted; the report remains a review draft. GitHub Pages follows completed research.

**10 October review checkpoint:** the [internal quality review](manuscript/report-quality-review-2026-10-10.md) reconciles central claims without changing the frozen report. A portable local handoff is ready for independent coding: 28 cases, 56 blank forms and 96 verified originals; the first-coder key is excluded. **160 offline tests pass without skips.** A separate reviewer's actual coding and completed-report decision remain open; no packet has been sent and Pages remains deferred.

## Adapting the Italian study to Germany

**This project adapts Florio and Spagnolo (2026), [*Female Mayors and Public Procurement*](https://doi.org/10.2139/ssrn.7046899), to the German institutional and data context.** Their Italian study provides the starting point for linking close mayoral elections to procurement outcomes. The report assesses that adaptation's feasibility. The proposed close-election RDD and broader environmental, social and innovation outcomes remain conditional on a justified future reopening.

The German application builds on existing research: Schild's [*Do Female Mayors Make a Difference? Evidence from Bavaria*](https://hdl.handle.net/10419/81935) addresses female mayors and fiscal decisions; **Baskaran and Hessami (2018), [*Does the Election of a Female Leader Clear the Way for More Women in Politics?*](https://doi.org/10.1257/pol.20170045), is a direct German female-mayor close-election precedent in Hesse**; their [*Women in Political Bodies as Policymakers*](https://doi.org/10.1162/rest_a_01352) examines Bavarian councillors and childcare. These studies inform the institutional and methodological groundwork; they do not establish this project's procurement effects.

See the [literature and adaptation note](docs/literature.md) for references, verification status, and the distinction between inherited design elements and proposed extensions. The German novelty claim remains provisional.

**Current decision, 5 October 2026:** the [bounded go/adapt/stop memorandum](docs/feasibility/go-adapt-stop.md) ends the present causal main-study claim and makes a reproducible **feasibility/data report** the active deliverable. The [Bavaria register-route audit](docs/feasibility/bavaria-bounded-route.md) finds scalable TED acquisition but no demonstrated joint historical candidate/outcome sample. A newer GERDA snapshot leaves all Bavarian rows unchanged. Main-study acquisition and effect estimation remain on hold; a future reopening requires material new linked-sample evidence. This is not a finding of no effect.

**Earlier NRW acquisition and early-checkpoint evidence, 5 October 2026:** All 380 scheduled-2020 mayoral elections and 1,349 candidate records have been audited, supplying 214 two-person decisions. The [latest buyer and procurement-phase audit](docs/feasibility/nrw-buyer-and-phase-audit.md) expands the retained inventory to **237 result notices** and **123 observed award-result units with contract dates and total tender counts across six municipal elections**, before complete deduplication and analytical unit selection. Original federal XML verifies 12 further city notices, adding four paired results in Unna and one in Werdohl. The [nationwide export audit](docs/feasibility/national-procurement-open-data.md) establishes the German OpenData route; the earlier [complete PDF cohort](docs/feasibility/nrw-complete-pilot.md) retains its original 106 paired observations.

Competition context now includes **59 original XML notices for 45 GUIDs** and **63 explicit legacy PDF references with independently indexed competition metadata**. **115 of the 123 paired observations have supported competition-to-contract chronology**. The [procedure-specific follow-up](docs/feasibility/nrw-procedure-scope-and-term-followup.md) verifies original procedure types for all 123 observations: three are explicitly without a prior call, while five competitive-procedure timing cases remain unresolved. Two same-title Geilenkirchen calls have conflicting GUIDs and stay unlinked. Italy includes direct awards in procedure-choice outcomes but uses Open&Negotiated for bidder counts; the [preliminary protocol](docs/research-protocol.md) now distinguishes outcome populations and no-call timing. **The new [historical close-election review](docs/feasibility/nrw-close-election-evidence-review.md) records all 55 pairs within 10 pp: six mixed, ten same-presentation and 39 unresolved pairs under the [measurement codebook](docs/feasibility/candidate-exposure-codebook.md).** After the [priority follow-up](docs/feasibility/nrw-close-pair-priority-followup.md), the first 15 within 2 pp contain four mixed, nine same and two unresolved pairs, with 27/30 candidate presentations supported. These are historically linked public-presentation measures; administrative sex/gender remains unavailable. Earlier occupational, generic-title and current-page inventories do not supply the historical assignment automatically. Official Viersen/Unna history adds year/term and oath evidence while preserving missing exact 2020 boundaries. Thirty-seven buyer cases, historical treatment measurement, actual terms, deduplication and precision remain unresolved; **no causal effects have been estimated**.

The [Bavaria candidate, tenure and legacy-award register](docs/feasibility/bavaria-candidate-and-tenure-register.md) remains available: 997 source-validated structural pairs, 95 named 2020 decisions, eight official title observations, three mixed-title pairs, two source-bounded tenure intervals and a historical 18-notice procurement pilot. Full Mühldorf legacy PDFs recover five dated award units within two of those notices. Bavaria's unresolved measurement and coverage gates remain explicit.

**Earlier execution, 5 October 2026:** the [literature/design comparison](docs/feasibility/literature-design-crosswalk.md) completes FP02's targeted review and identifies the 2018 Hesse study's public replication record, whose package/license/data still require inspection. The [outcome/population draft](docs/feasibility/outcome-population-codebook.md) starts FP04 with explicit units, weights, procedure/tender denominators, missingness and turnover rules. A bounded [candidate-source continuation](docs/feasibility/nrw-priority-continuation.md) examines two original school documents; the three Heiden/Viersen gaps and all checkpoint counts remain unchanged.

**Next steps:** review the [English manuscript and reproduction package](manuscript/README.md), complete the outstanding independent review and record a completed-report decision. Twenty-eight NRW pair packets are prepared, but no independent second coding has occurred. The two nominated outcome measures remain measurement questions, not estimated effects. The [research plan](docs/feasibility/detailed-research-plan.md) and [task register](docs/feasibility/research-task-register.csv) preserve unmet positive-go gates. Broad collection is on hold. GitHub Pages remains deferred until research completion under the reviewed report scope.

**Project language:** English for documentation, code, variable names, and research outputs. Original source documents retain their original language.

## Research workflow

The active path is feasibility report → substantive/independent review → completed-report decision → GitHub Pages companion. The full causal workflow below remains conditional on material new evidence satisfying the reopening gates.

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
| [English feasibility report](manuscript/feasibility-report.md) · [PDF](manuscript/feasibility-report.pdf) | Review draft with Italian/German attribution, source-specific sample flow, selection limits and assumption-based precision |
| [Report reproduction guide](manuscript/README.md) | Template, 22 input pins, fact ledger, figures, software versions and verification record |
| [Early feasibility decision and precision](docs/feasibility/early-feasibility-decision.md) | Actual provisional linkage, independent-election MDE benchmarks, side support, narrowed scope and bounded go/adapt/stop checkpoint |
| [Independent coding protocol](docs/feasibility/independent-coding-protocol.md) | All classified pairs plus unresolved audit, separated first-coder key, selection checks and uncompleted reviewer gate |
| [Literature/design crosswalk](docs/feasibility/literature-design-crosswalk.md) | Italian adaptation, German mayoral/council precedents, inspected editions, replication routes and dated search evidence |
| [Bounded go/adapt/stop decision](docs/feasibility/go-adapt-stop.md) | No-go for the current causal launch, feasible report scope and explicit reopening conditions |
| [Bavaria scalable-route audit](docs/feasibility/bavaria-bounded-route.md) | Current registry/version check, 31-election TED availability and conditional election-level precision |
| [Report completion outline](docs/feasibility/report-completion-outline.md) | Active manuscript sections, evidence artifacts and completion requirements |
| [Outcome/population draft](docs/feasibility/outcome-population-codebook.md) | Units, denominators, weights, turnover, category/timing rules and the remaining FP04 decisions |
| [Bounded candidate-source continuation](docs/feasibility/nrw-priority-continuation.md) | Two new 2020 school originals, no new labels and unchanged priority counts |
| [Historical close-election review](docs/feasibility/nrw-close-election-evidence-review.md) | All 55 dispositions, the priority 15, primary-source evidence and explicit unresolved cases |
| [Priority evidence follow-up](docs/feasibility/nrw-close-pair-priority-followup.md) | Five closed candidate gaps, four additional complete pairs, dated official originals and the three remaining priority gaps |
| [Candidate/exposure measurement codebook](docs/feasibility/candidate-exposure-codebook.md) | Historical presentation, administrative fields, identity, exact margins and term uncertainty |
| [Detailed research plan and task register](docs/feasibility/detailed-research-plan.md) | Priorities, 23 work packages, effort estimates, evidence gates and the path to analysis and Pages |
| [NRW procedure-specific timing and term follow-up](docs/feasibility/nrw-procedure-scope-and-term-followup.md) | Original types for all 123 observations, three no-call cases, five timing cases, two conflicting GUID candidates and additional official person evidence |
| [NRW buyer and procurement-phase audit](docs/feasibility/nrw-buyer-and-phase-audit.md) | 237 retained results, 123 paired observations across six elections, 115 supported phase links and 37 remaining buyer cases |
| [Nationwide procurement OpenData and NRW XML audit](docs/feasibility/national-procurement-open-data.md) | Verified federal exports, 118 paired result observations across four elections, CSV conversion checks and 50 competition notices |
| [NRW procedure and presentation audit](docs/feasibility/nrw-procedure-and-presentation-audit.md) | Verified notice history, reference collisions, four index-supported counts, seven primary-presentation pairs and outcome concentration |
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
