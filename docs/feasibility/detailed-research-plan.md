# Detailed research plan

Prepared on **5 October 2026** against the evidence published through 4 October. This is an operational plan, **not a preregistration or a positive feasibility finding**. The task estimates below preserve the original planning allowances. Execution status is now tracked in the task register: the [baseline snapshot](baseline-snapshot.md), [measurement codebook](candidate-exposure-codebook.md) and [initial 55-pair review](nrw-close-election-evidence-review.md) have been produced.

**Revised after supervisory feedback:** early precision, the actually linkable election sample and selection/independent-coding readiness now precede extensive acquisition. The [early decision memo](early-feasibility-decision.md) implements this with an existing-data audit and a **maximum 12-hour / two-working-day decision block**. Four mixed pairs within 2 pp are supported, with at most six under favorable resolution. Only three supported mixed elections currently have candidate-window pilot links; zero main-study elections are certified. Broad notice harvesting and low-yield case searches pause until a credible scalable route justifies further work.

**This project adapts Florio and Spagnolo (2026), [Female Mayors and Public Procurement](https://doi.org/10.2139/ssrn.7046899), to Germany.** Its German foundations include Schild (2013), **Baskaran and Hessami (2018, female mayors in Hesse)**, Baskaran and Hessami (2025, Bavarian councillors), Arnold (2018), Frank, Stadelmann and Torgler (2023), and Heddesheimer et al. (2025, GERDA). Keep this attribution prominent in the protocol, manuscript and eventual website. The [literature note](../literature.md) and [completed targeted crosswalk](literature-design-crosswalk.md) record what has actually been read and the inspected editions.

The next objective is a **bounded go/adapt/stop memorandum supported by observed and plausibly obtainable linked election counts, meaningful-effect thresholds, precision and selection/review status**. It can recommend targeted expansion or ending the causal claim before full collection. A final positive NRW go still requires the full eligibility/coverage/precision gates. NRW 2020 remains the lead cohort; Bavaria is the first bounded scalable-route comparison. GitHub Pages stays deferred until research completion under the chosen scope.

## Starting position

| Component | Established evidence | Remaining implication |
| --- | --- | --- |
| NRW elections | 380 official elections, 1,349 candidates, 214 decisive two-person pairs | Gender measurement and actual exposure histories remain unresolved; no main-study treatment assignments |
| GERDA | 212/214 finalist identity matches; 72 prediction-based mixed-label leads | Predictions are acquisition aids, including possible false negatives among apparently same-label pairs |
| Near-cutoff inventory | All pairs: 4 / 15 / 34 / 55 within 1 / 2 / 5 / 10 pp; predicted mixed leads: 2 / 5 / 9 / 17 | These are descriptive bands, not selected RDD bandwidths or true mixed-gender counts |
| Procurement pilot | 237 retained result notices; 123 observed dated/count units in 82 notices across six elections | Units precede complete deduplication; more notices do not create more independent elections |
| Timing and scope | 115 supported competition-to-contract pairs; original types for all 123 units | Five competitive timing cases, three no-call timing rules and 37 buyer-scope cases remain open |
| Person evidence | Seven pairs have both public primary presentations documented | Evidence types and dates differ; this does not establish seven historically validated gender pairs |
| National acquisition | Public German CSV/XML exports verified; archive floor December 2022 | Above-EU mandatory reporting begins 25 October 2023; below-EU reporting is incomplete |
| Bavaria | 997 source-validated structural pairs and a smaller named/evidence pilot | Gender, terms and common procurement coverage are still gates |

Source snapshots: [statewide elections](nrw-statewide-election-register.md), [buyer and phase audit](nrw-buyer-and-phase-audit.md), [procedure and term follow-up](nrw-procedure-scope-and-term-followup.md), [national exports](national-procurement-open-data.md), and [Bavaria register](bavaria-candidate-and-tenure-register.md). Earlier supplements describe their own historical cohorts.

## Work packages and dependencies

Use [research-task-register.csv](research-task-register.csv) to track status, dependencies, outputs, acceptance conditions and budgets. Paths may be planned deliverables; consult status and evidence. One working day means approximately six focused hours; automated time and independent-review availability are separate. The original **17–33-day full-feasibility allowance** becomes conditional on the early checkpoint identifying a viable route. It is not authorization to collect extensively before precision. The new next checkpoint has a maximum **12 focused hours**, with stage allocations in the memo. Estimates are effort allowances, not promised completion dates.

| ID | Work package | Depends on | Working days | Completion evidence |
| --- | --- | --- | ---: | --- |
| FP01 | Freeze the current acquisition baseline | — | 0.25–0.5 | Commit, hashes, cohort counts and unresolved queues reconciled |
| FP02 | Complete the targeted literature and design comparison | FP01 | 1–2 | Primary methods/outcomes matrix, reproducible search log and bounded novelty claim |
| FP03 | Specify candidate and tenure evidence rules | FP01 | 0.5–1 | Codebook distinguishes registry fields, public presentation, uncertainty and continuity |
| FP04 | Specify estimands, units and outcome populations | FP02, FP03 | 0.5–1 | Separate procedure-choice and competition definitions, denominators, weights and timing |
| FP05 | Verify all 55 pairs within 10 pp, regardless of predictions | FP03 | 1.5–3 | Every pair has two candidate evidence dispositions and signed-margin status; early checkpoint |
| FP06 | Screen the other 159 pairs | FP05 | 2–4 | Every one of the 214 pairs has a documented eligibility or unresolved status |
| FP07 | Expand procurement discovery across verified close contests | FP04, FP05 | 1–2 | Coverage matrix for the 17 predicted leads and any newly verified close mixed pairs |
| FP08 | Audit and choose common observation/follow-up windows | FP04 | 0.5–1 | Window memo grounded in reporting rules and original-source availability |
| FP09 | Build exposure histories for candidate study elections | FP03, FP05, FP08 | 1–2 | Source-bounded continuity, turnover and ambiguous-date intervals |
| FP10 | Close or explicitly bound existing pilot exceptions | FP04, FP08 | 1–2 | All five timing and 37 scope cases receive auditable dispositions |
| FP11 | Acquire the common-window cohort and baseline covariates | FP07, FP08 | 2–4 | Pinned competition/result exports, buyer mappings, dated baseline-covariate inventory and explicit coverage status |
| FP12 | Deduplicate and normalize procurement units | FP04, FP10, FP11 | 2–4 | Version/phase graph and source-to-procedure/lot/result mapping reconcile |
| FP13 | Test strategic-criteria measurement | FP04, FP11 | 0.5–1 | Environmental/social/innovation fields pass a source-based measurement audit or are dropped |
| FP14 | Freeze the feasibility sample and attrition report | FP06, FP09, FP12, FP13 | 1–2 | Outcome-specific election counts, missingness, coverage and exclusion reasons |
| FP15 | Early precision now; final precision after sample construction | Early: FP01, FP03, FP05; final: FP04, FP14 | 1–2 originally | Early Gaussian/margin-support audit complete; final outcome-specific RDD assessment remains open |
| FP16 | Early bounded decision; final go/adapt/stop if work continues | Early: FP02 and early FP15; final: completed FP15 | 0.5–1 originally | Early memo complete; next bounded checkpoint and final decision remain open |
| FP17 | If needed, audit one expansion route and revisit the decision | FP16 = adapt | 3–5 initially | Bounded Bavaria/additional-cohort access test; a separate expansion budget if warranted |
| FP18 | Preregister and pin the analysis environment | FP16 = go, or successful FP17 reassessment | 1–2 | Dated frozen specification and software versions before main effect estimation |
| FP19 | Build and freeze the main analysis dataset | FP18 | 2–4 | Reproducible construction and outcome-specific samples match the specification |
| FP20 | Run primary RDD and diagnostics | FP19 | 2–4 | Estimates, uncertainty, assignment counts and diagnostic report reconcile |
| FP21 | Run prespecified robustness and sensitivity analyses | FP20 | 2–3 | Full specification ledger, including failures and exploratory deviations |
| FP22 | Complete manuscript and reproduction review | FP21 | 3–5 | Manuscript, figures and a clean reproduction run agree; limitations explicit |
| FP23 | Build and release the GitHub Pages companion | FP22 complete | 2–4 | Interactive views use checked research artifacts and pass the release gate |

Following a go decision, FP18–FP22 add approximately **10–18 working days**. Pages adds **2–4 days afterward**. A wider data expansion, unsuccessful access attempt or provider response can change these estimates. Stop or adaptation can end or reshape the causal work before the later packages.

In the task register, `depends_on` retains the prerequisites for the full work package; `conditional_depends_on` records FP17 reassessment only if expansion was chosen. The new `early_stage_depends_on`, `early_stage_deliverable` and `early_stage_status` fields make FP15/FP16's early work possible before their final-stage prerequisites. `condition_or_timebox` records budgets and holds. FP01/FP02/FP03 are completed; **FP04/FP15/FP16 are in progress**, with the early stages of FP15/FP16 completed. FP05 remains `initial_review_complete`; it is not an independent second review. FP04's v0.2 [draft](outcome-population-codebook.md) nominates at most two primary measures; denominator interpretation, no-call timing and final confirmation remain open. Actual common dates are FP08 work.

FP05 supplies all 110 candidate dispositions, not 55 verified classifications. After the [priority follow-up](nrw-close-pair-priority-followup.md), six mixed and ten same-presentation pairs are supported, with 39 unresolved. The closest 15 have 27/30 supported candidate presentations and 13/15 classified pairs; three candidate gaps in Heiden/Viersen remain. The subsequent [bounded continuation](nrw-priority-continuation.md) adds two 2020 school originals without changing labels. Carry unresolved cases into FP06 and exposure work; return to those three only for a distinct promising original/source route. No new mixed pair was added.

## Revised next execution block

1. **Use completed FP01–FP03 and the existing FP05 dispositions.** Preserve the baseline and measurement rules; unresolved evidence stays unresolved.
2. **Early FP15/FP16, now performed:** join existing candidate/procurement records, report independent elections and cutoff sides, compute assumption-based precision sensitivities and actual-margin support, and document an early decision. The three provisional window links are not final eligibility. This stage uses no treatment-effect regressions.
3. **Selection and independent review:** use the [coding protocol](independent-coding-protocol.md). Twenty-eight pair packets are prepared, covering all 16 classified pairs and 12 unresolved cases; a separate reviewer must complete the records. Inventory valid incumbency, municipal-size and historical-source covariates; unavailable fields remain missing. Coding agreement does not repair source/reporting selection.
4. **Keep FP04 narrow:** negotiated-procedure share and single-tender share are the two nominated primary candidates. Their different denominators/timing and meaningful-effect thresholds require justification. Other outcomes are secondary or conditional exploratory extensions.
5. **Test one scalable route within the remaining checkpoint allowance:** begin with the existing Bavaria-2020 register and actual gender/common-period access; the older Hesse replication record is an access/method lead, not a ready 2020 expansion. Separate supported counts from favorable projections.
6. **Write the next bounded decision:** prepare a main study only after all required gates, choose a demonstrably viable expansion, or end the causal claim and complete a feasibility/data report. Do not exhaust the former long acquisition budgets while this route remains unproven.

The nine previously predicted leads within 5 pp and eight further predicted leads through 10 pp remain stored acquisition leads. They no longer schedule an automatic next harvesting batch. Full 214-pair attrition is required for a final positive NRW go; an early adaptation or stop can occur first. Numerical bands and predictions do not determine final eligibility or the RDD bandwidth.

## Decisions to settle before the data freeze

**Literature and contribution.** FP02 completes a methods/data/outcome crosswalk for Florio–Spagnolo and the German precedents, checking final published versions where available. Record page/table references, sample construction, gender provenance, election eligibility, timing, weights, inference and replication access. Search German female-mayor/procurement and representation/procurement work with recorded queries, dates and inclusion rules. Use existing reviewed sources; do not repeatedly rediscover bibliography metadata. An inaccessible text stays unverified. The contribution statement must reflect what the search supports.

**Treatment measurement and exposure.** FP03 defines acceptable evidence types and their historical relevance, identity checks, contradictions and unknown labels. Explicit administrative sex/gender fields and documented public gender presentation are different measures; either needs an honest interpretation. Names, photographs and GERDA prediction confidence do not establish primary measurement. Date precision should be sufficient for the chosen window: a bounded uncertain entry in 2020 need not invalidate clearly documented later exposure. An oath, first workday, council calendar or first-observed election is not automatically the actual mayoral boundary.

FP04 must distinguish a **fixed-window municipal election ITT**, retaining the original election assignment through later turnover, from procurement **published while the original winner holds office**, which introduces a different exposure/population and possible post-election selection. Early exit or a successor must not silently remove events from an ITT sample. FP09 records continuity and turnover for this decision; it does not require personal mayoral signatures on contracts.

**Outcomes and analytical units.** Nominate at most two primary measures: negotiated-procedure share and single-tender share. Mean tenders, values/winners and strategic criteria are secondary or conditional exploratory extensions. Italy includes direct awards in procedure choice but limits bidder regressions to Open&Negotiated. Map German categories from originals with explicit restricted/no-call handling and separate denominators. A missing call file is not no-call procurement. Conditional realized-procedure/result outcomes require a selected-population interpretation. Tender totals and distinct firms are different measures. Confirm the family and relevant-effect thresholds using feasibility evidence, not significance.

Define procedure, lot, grouped result and contract relationships before weighting. The default proposal to evaluate is equal election weighting for a municipal estimand; contract-weighted analysis is a distinct target. A repeated lot count must not be treated as independent evidence. Missing counts, cancellations, unsuccessful procedures and municipalities without matched notices need separate states. Absence of a notice is not zero procurement; absence of an explicit strategic field is not absence of a criterion.

**Coverage and windows.** FP08 first tests an above-EU, common-calendar **1 November 2023–31 December 2024** cohort, already within acquired monthly exports, and an extension through **31 October 2025** if the 2025 source audit supports it. These are candidate windows, not selected analysis windows. For NRW 2020 they represent late-term outcomes, not immediate post-election effects or a full-term replication. Compare term/turnover implications explicitly. Below-EU voluntary records form a separate coverage stratum.

Anchor called procedures on supported competition publication. Specify a separate source-supported no-call timestamp, rather than substituting a later result publication without explanation. Competition cohorts need linked results observed through one prespecified acquisition cutoff and an explicit maturity/right-censoring rule. Test export availability through **30 September 2026** as a candidate cutoff; do not assume those archives have been acquired or that all procedures have finished. Acquire competitions, corrections, results, cancellations and no-call results systematically; collecting only complete awarded rows cannot establish the procedure-choice denominator. Retain reporting changes and unresolved coverage instead of optimizing windows using estimated effects.

FP11 also inventories a small set of official **pre-election** municipal covariates, such as 2019 population and fiscal capacity, with compatible geography and vintages for continuity checks. Pre-election procurement outcomes are included only if comparable historical coverage can be established; the newer federal archive cannot supply a 2020 baseline by itself. Later outcomes or procedure choices must not substitute for pretreatment controls.

## Bound the remaining case searches

FP10 has a maximum allowance of **two working days / approximately 12 focused hours** for the existing exceptions. Triage all 42 cases, allowing roughly 30 minutes for each of the five competitive timing cases and 10 minutes for each of the 37 scope cases, with the remaining budget used for a small number of promising source checks and documentation. These are research-effort limits, not evidence standards. A case that exhausts its budget remains unresolved; exclude it only from the outcomes for which its missing information is necessary, and record the possible coverage consequences.

**This is a later conditional exception budget, currently on hold.** It does not add 12 hours of case searches to the new 12-hour early decision block. Resume only if the early memo supports a scalable route and the exception is necessary for an intended outcome. Do not repeat low-yield individual candidate searches meanwhile.

- Geilenkirchen 126957-2024 and 196766-2024: inspect explicit original references for the same-title competition candidates; conflicting GUIDs forbid a title-only merge.
- Velbert 17130-2024, 726107-2024 and 786759-2024: resolve supported competition identity/root or retain missing timing.
- Three Unna no-call observations: apply FP04/FP08's separate timing and procedure-category rules; they are not missing-call cases.
- Thirty-seven buyer cases: seek original contracting-party or legally identified beneficiary evidence. A performance address alone is insufficient; county and joint purchases need explicit scope rules.

Protect broader election coverage from these searches becoming an indefinite dependency. If unresolved cases prevent a defensible outcome denominator, that outcome fails the coverage gate. Provider/author inquiries may be drafted; none are scheduled for sending without explicit user authorization. Use documented available routes and preserve previously identified protected-source limitations.

## Feasibility gates

| Gate | Required evidence | Response to failure |
| --- | --- | --- |
| G1: early linked-sample/precision checkpoint, now | Actual provisional links by cutoff side, existing 55-pair dispositions, meaningful-effect/variance sensitivity, side support, selection/review readiness and a realistic scalable route | Maximum 12-hour decision block; pause extensive acquisition, choose viable adaptation or end the causal claim |
| G2: measurement and coverage, after FP14 | Transparent 214-pair attrition for a positive NRW go; completed independent review/adjudication, selection audit, outcome-specific rules, reproducible units and common-window reporting/censoring | Drop an unmeasurable outcome, change the target population explicitly or record a stop |
| G3: precision and identification, FP15–FP16 | Supported cutoff neighborhoods, independent assignments, dependence-aware uncertainty, justified useful-effect thresholds and a credible continuity argument | Adapt geography/cohorts only when comparable coverage is demonstrable, or stop the causal study |
| G4: preregistration, FP18 | Frozen population, units, windows, estimands, outcomes, weights, estimator, diagnostics and deviation rules | No confirmatory effect estimation until specification is frozen |
| G5: completion and Pages, FP22–FP23 | Manuscript and reproducibility checks complete; publishable artifacts reconcile; website interactions validated | Keep Pages deferred |

FP15 reports counts of **eligible elections and distinct municipalities on each side**, not only contract totals. Simulate precision using the actual vote-margin distribution, outcome availability and cluster sizes, with documented ranges for outcome variance, within-municipality dependence, unequal volumes and missingness. Use pooled/nuisance summaries without inspecting the female-winner effect to select the sample or outcomes. Evaluate data-driven local-linear RDD inference; account for discrete margins and small-cluster limitations. Useful-effect thresholds must have a substantive justification. Report MDEs at stated power and significance levels, including any primary-family correction. There is no universal contract-count or municipality-count shortcut to a go decision.

FP15's **early stage is complete** in the [decision memo](early-feasibility-decision.md), using Gaussian two-group benchmarks and margin-matrix ranks before extensive collection. It does not fulfill the final sample-based RDD precision requirement above. FP16's early memo recommends bounded feasibility/adaptation; its final go/adapt/stop stage remains open. The independent-review packet is ready, but no independent coding is claimed.

**Go:** At least the explicitly named core outcome(s) have defensible measurement/coverage and useful expected precision under a credible design. Any outcome dropped from the original scope is documented.

**Adapt:** Choose one bounded expansion or outcome/timing revision with an explicit reason and budget, then repeat the relevant gates. Bavaria 2020 is the first geographic comparison because acquisition already exists; other cohorts require official election validation and procurement coverage during a comparable post-election period. NRW 2025 offers short follow-up at present, and older NRW elections cannot automatically be linked to much later procurement as the same exposure. Pooling states requires a justified common estimand and institutional rules. FP17's 3–5 days fund an access/sample audit, not an entire additional state dataset.

**Stop:** If measurement, coverage, cutoff support or precision cannot be made credible within a justified expansion, complete a reproducible feasibility/data report. Do not turn an underpowered causal exercise into a claim of no effect or quietly substitute an unvalidated panel design. Any interactive feasibility companion would then require a revised publication scope.

## Main study, manuscript and interactive companion

FP18 freezes the protocol before estimating main effects: decisive-round rules, gender operationalization, exposure/turnover, reporting population, phase dates, no-call handling, censoring, deduplication, weighting, outcome families, bandwidth/inference methods and planned sensitivity checks. Pin the analysis stack; retain Python collection code and select a maintained RDD implementation after validating its clustered-inference options. Clearly distinguish a dated GitHub protocol commit from any formal registry submission.

FP19–FP21 produce the main construction pipeline, local-linear estimates and robust bias-corrected intervals, assignment/cluster counts, balance and margin diagnostics, and prespecified timing, scope, missingness, weighting and bandwidth sensitivities. Failed specifications remain reported. Controls are pretreatment unless a separate conditional/mechanism estimand is declared; procedure choice is a potential mediator. Write limitations on reporting, selection, lagged outcomes, small samples and external validity alongside results.

FP22 completes a manuscript with a prominent Italian adaptation statement and German citations, matched figures/tables, sample flow, source/code versions and a clean reproduction check. Record departures from the frozen plan. FP23 then uses reviewed aggregate and specification artifacts for GitHub Pages: coverage/sample flow, running-variable plots, estimates with confidence intervals, and comparisons of completed specifications. Interactions must show their sample, units and uncertainty and reconcile with the manuscript; they must not invent new estimates. Follow the existing [website release gate](../../website/README.md).

## Progress reporting

After each execution block, update the task register and [decision log](../decision-log.md), reporting completed task IDs, source-supported changes, unresolved cases, independent election counts, and the next gate. Commit code, documentation and publishable metadata together where appropriate. Keep raw/interim data local under the [data-management rules](../data-management.md). Close a package only when its acceptance evidence exists; producing another source note alone does not complete a gate.
