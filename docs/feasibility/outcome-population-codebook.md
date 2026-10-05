# Outcome and population codebook — feasibility draft

**Version 0.2, 5 October 2026; FP04 in progress.** Following supervisory feedback, this draft nominates at most two primary outcome candidates and moves precision/linked-sample assessment ahead of extensive acquisition. It is not a preregistration, a completed sample definition or permission to estimate effects. Denominator interpretation, coverage and a defensible no-call timing rule remain open. Common dates are an FP08 decision; final outcome confirmation is an FP18 gate. The [early decision memo](early-feasibility-decision.md) establishes the new bounded execution order.

**The project adapts Florio and Spagnolo (2026) to Germany**, informed by the [Italian/German literature crosswalk](literature-design-crosswalk.md). Candidate measurement and signed margins follow the unchanged [candidate/exposure codebook](candidate-exposure-codebook.md). Historically linked public presentation is the currently available measure; administrative sex/gender remains unavailable. Every construction record must retain the original source and rule version.

## Election assignment and interpretation

For a source-verified mixed-presentation decisive election, let `D_e = 1` if the female-presented finalist wins and `D_e = 0` if she loses. The signed running variable is `(female_votes − male_votes) / decisive_valid_votes × 100`; positive means a female-presented win. Same-presentation and unresolved pairs do not receive a fabricated signed margin. The existing 55-pair screen is an acquisition queue, not the RDD sample or bandwidth.

The proposed **fixed-calendar-window municipal election ITT** keeps `D_e` attached to the original election throughout the window, including documented turnover. It compares electing that candidate with electing her actual opponent near a zero margin. It does not isolate gender from other candidate attributes or identify the effect of a mayor personally handling procurement.

Two distinct restrictions must be reported separately:

| Specification | Assignment and population | Interpretation |
| --- | --- | --- |
| Proposed fixed-window election assignment | Use the same prespecified calendar window for both cutoff sides; retain the original assignment through turnover | A local election-assignment contrast for the **defined observable outcome**. A conditional ratio or an outcome-selected election sample is not automatically an unconditional ITT over all municipal purchases. |
| Original-winner exposure sensitivity | Retain procurement events whose supported relevant phase occurred while the original winner held office | A different, potentially selected exposure population. Turnover may respond to the election; exclusions and uncertainty must be reported. |
| Same-winner publication/conclusion sensitivity | Require both supported phase dates within the original winner's term | Closer to one Italian sensitivity restriction; an additional post-election selection, not the default fixed-window ITT. |

Exposure histories still matter for chronology, turnover description and sensitivities. An uncertain 2020 entry that lies entirely before a later supported window need not prevent window-specific continuity assessment. An oath, first workday or GERDA panel date cannot certify the actual boundary. A window crossing the 2025 election must explicitly describe successor exposure; it cannot be called a pure original-winner term window.

## Reporting universe and municipal scope

The first coverage audit concerns **above-EU reported municipal procurement**. Mandatory reporting and successful archive retrieval do not prove a census of all purchases. Below-EU voluntary records, concessions and special-regime notices form separate strata until their coverage and category definitions are verified. The current 237-result-notice/123-dated-count-unit pilot was acquired from selected municipal leads and periods; it is not a ready denominator.

Proposed primary scope is the municipality as an explicitly identified contracting party, or an external agent explicitly purchasing exclusively for that municipality. Municipal department aliases require validated entity mapping. Do not require a personal mayoral signature.

| Buyer case | Draft disposition |
| --- | --- |
| Validated municipal legal buyer or department | Include in the municipal scope inventory, subject to reporting/timing/unit rules |
| External procurement agent with explicit exclusive municipal representation/beneficiary evidence | Include with a representation flag; retain the legally identified buyer and beneficiary separately |
| County, hospital, independent municipal enterprise, utility or other separate entity | Keep outside the proposed direct-municipal primary scope; a distinct sensitivity stratum requires documented legal identity/control and its own interpretation |
| Joint purchase for several public entities | Keep outside the primary scope unless a separate allocation rule is justified and frozen; never allocate by performance address or divide equally without evidence |
| Ambiguous buyer/beneficiary identity | `scope_unresolved`; retain in coverage/attrition, withhold from outcomes requiring that scope |

The 37 unresolved buyer cases are not automatically excluded from every descriptive inventory or retrospectively relabelled by this draft. FP10 must apply an explicit disposition to each case.

## Units and duplication

Maintain a graph of **source notice UUID/version → procedure → lot → result/tender statistics → contract(s)**. These are different units. Preserve explicit original GUIDs, parent/change references, lot IDs and contract associations. Shared titles, addresses, local reference numbers and supplier names do not establish identity.

| Object | Use and rule |
| --- | --- |
| Source notice/version | Acquisition and reporting audit; no independent procurement count |
| Supported procurement procedure | Proposed procedure-choice unit, counted once after correction/history reconciliation |
| Explicit lot result or source-defined grouped-lot result | Proposed tender-count unit; a single total covering lots 1+2 remains one grouped statistic, not two independent totals |
| Contract | Separate monetary/legal record; two contracts referencing the same result statistic do not duplicate that tender total |
| Municipal election | Proposed outcome aggregation/assignment unit; many procedures or lots do not add independent elections |

For the snapshot at a fixed result cutoff, use the latest **supported linked correction/version** as of that cutoff, retaining earlier values and the change reason. Do not select the latest timestamp across unlinked records with similar titles. Pending, cancelled, unsuccessful and awarded states must reconcile within the graph; an unresolved collision remains unresolved. A purported correction must not silently turn a historical event into a new procedure.

The pipeline implementation and full graph audit are FP12 work. Existing observed units remain frozen as pilot evidence until that construction is implemented and reviewed.

## Outcome populations and denominators

Nominate a maximum two-measure primary family: **negotiated-procedure share** among unique in-scope procedures and **single-tender share** among supported called-procedure result statistics. They require different universes. The early precision screen reports alpha .05 and a conservative per-test .025 allowance for a two-outcome family. Coverage/denominators, substantive effect thresholds and the final family still require confirmation; no effect direction is assumed. Mean total tenders, values/winners and strategic criteria are secondary or exploratory/conditional extensions in this phase. Failure of a nominated measure must be recorded; it is not silently replaced to obtain a favorable result.

| Candidate measure | Numerator/value | Required denominator/population | Interpretation and missing states |
| --- | --- | --- | --- |
| Procedure-category share | Number of unique supported procedures in a literal mapped category | All unique in-scope, reporting-eligible procedures with supported cohort timing and a classifiable category, including pending/unsuccessful/cancelled procedures | Composition of the defined observed procedure population. Award-result-only collection cannot supply this denominator. Unknown codes are reported separately. |
| Negotiated-procedure share | `neg-w-call` plus `neg-wo-call`, also report each separately | Same procedure denominator, **only after both timing rules and code meanings are supported** | A German procedural measure, not an Italian direct-award mapping or a generic corruption score. A called-only population is a separately named restriction. |
| Mean total tenders | Sum of explicit positive total-tender counts | Source-defined completed successful lot/grouped-result statistics in the declared called-procedure categories, observed by the result cutoff | A conditional competition outcome. Preserve its reporting coverage and number of procedures/results; missing counts are not zero. |
| Single-tender share | Number of qualifying result statistics with `total_tenders = 1` | The same set of qualifying results with valid total-tender counts | A limited-competition indicator. It is not the share of all contracts with a single distinct bidder and does not prove corruption. |
| Observed procedure/result counts or counts per dated pre-election population | Count of supported source events; optional rate uses verified 2019 municipal population | Same fixed calendar and reporting-acquisition coverage for every election; population must use compatible official geography | Possible complement to conditional ratios. A zero **observed record count** after a complete acquisition audit does not mean zero procurement. This option requires an explicit primary estimand decision. |
| Documented environmental/social/innovation criteria | Explicit source-supported criterion/strategic-field indicator, with specifications distinguished from award criteria | Comparable field-applicability and reporting population, to be tested in FP13 | Conditional extension. Blank, absent or inapplicable fields remain separate; documentation does not establish realized environmental/social performance. |

Competition starts with `open`, `restricted` and `neg-w-call` as **separate audit strata** where a prior call and total-tender semantics can be supported. Pooling them is an adaptation decision, rather than an inherited Italian sample. Restricted procedures are not silently omitted because Table 3 in Italy says Open&Negotiated. Counts in `neg-wo-call` remain preserved and can be described separately; their recruitment/count mechanism requires validation before a common competition analysis.

Tender totals are not counts of distinct bidder firms. Electronic, SME, admissible and other subset statistics do not replace total tenders. The same firm may submit several tenders or appear in several lots. Consortium supplier blocks do not add tenders or contracts. Noninteger, negative, conflicting or successful-result zero totals require review; an explicit unsuccessful-procedure zero, if present, remains a separate state rather than a single-tender award.

**Selection must be visible.** The procedure denominator, successful-result denominator, count-reporting denominator and municipality with at least one usable result can all respond to treatment. Equal election weights do not remove that selection. Report the nested denominators, outcome availability and category mix by election and cutoff side before interpreting a conditional contrast. Do not code an undefined tender mean or share as zero. FP04 must choose whether a defensible unconditional observed-event count/rate complements the ratios, or restrict the final claim to clearly conditional outcomes; FP15 evaluates the resulting independent sample.

For procedure shares, report an unknown-category rate against the full supported procedure inventory. With `k` known target-category procedures, `n` fully classified procedures and `u` unknown categories, the descriptive all-category share can be bounded by `k/(n+u)` and `(k+u)/(n+u)` when `n+u > 0`. These bounds do not repair unknown scope, omitted procedures, missing timing or differential reporting and are not causal estimates.

## Procedure coding

Use the original XML `TenderingProcess/ProcedureCode` or the explicitly scoped legacy Section IV.1.1. Preserve raw codes and source locators before mapping.

| Observed original code | Draft class | Prior-call handling |
| --- | --- | --- |
| `open` | Open | Supported competition identity/date required for a called cohort |
| `restricted` | Restricted | Same requirement; retain separate competition stratum |
| `neg-w-call` | Negotiated with prior call | Same requirement |
| `neg-wo-call` | Negotiated without prior call | Separate no-call timestamp rule; never invent a missing call |
| `us-free-no-tw` | Source-specific regime, not yet harmonized | Retain the literal code; verify legal reporting/category meaning before pooling |
| Any other code, legacy ambiguity or conflicting versions | `category_unresolved` | Preserve the reason; do not force a direct-award/open category |

Absence of an acquired competition document is not evidence of no-call procurement. A reason for using a procedure and its literal procedure type are separate fields. If an original procedure has inconsistent lot-specific/global classifications, retain the conflict and withhold the affected aggregate until FP12 resolves the relationship.

## Timing, cohort entry and follow-up

FP08 tests **1 November 2023–31 December 2024** as a common called-procedure cohort and an extension through **31 October 2025** if source coverage supports it. Result availability through **30 September 2026** is a candidate follow-up cutoff, not an acquired fact. Those late-term windows differ from a full-term or immediate post-election study.

| Event | Cohort rule proposed for the audit |
| --- | --- |
| Called procedure | Supported original competition publication, using the linked correction graph. A documented earliest graph root is not automatically earliest-ever publication. |
| No-call procedure | **Unsettled:** audit whether a harmonized administrative event is present in original sources. Preserve contract conclusion and result publication separately. No substitution is adopted in this draft. |
| Contract conclusion/winner selection | Retain separately for outcomes, maturity and exposure sensitivities; they do not replace tender publication |
| Award/result publication | Ascertain when the outcome became observable and whether it was before the cutoff; it may describe a much earlier procedure |
| Cancellation/unsuccessful/pending result | Preserve status, supported date and linkage; no fake award or zero-tender successful result |

A called procedure enters by supported cohort publication and remains in the procedure inventory even if its result is unobserved at the cutoff. Acquisition must cover competitions, corrections, results, cancellations and no-call notices systematically. A latest-result cohort would preferentially select completed/reporting procedures and cannot stand in for that inventory.

FP08 must select and document a maturity/right-censoring rule using reporting lags and available histories, without looking at treatment-effect estimates. Report publication-to-cutoff follow-up, pending results, unlinked results and reported count completeness. Equal follow-up or a prespecified minimum lag may address observation time but cannot certify full outcome ascertainment. Mixed date precision is retained; if an interval overlaps a window boundary, classify the affected timing as ambiguous rather than assigning a midpoint.

Until no-call timing is supported, **do not claim a complete all-category procedure-choice cohort**. A called-procedure composition statistic may be constructed for feasibility only with that restriction in its name and denominator. Excluding no-call records changes the research target and must be decided explicitly, rather than repaired by deleting the three pilot cases.

## Aggregation, weighting and inference

The draft preference is **one outcome row per municipal election**, with each election receiving the same base weight before the RDD kernel. Within an election/window, procedure shares use unique procedures; tender means/shares use supported lot/grouped-result statistics. These within-election weights are explicit: this is a mean over observed result statistics, not over firms, suppliers or duplicated contracts. Report the result count and grouped-lot share for each election.

A pooled result-weighted estimate is a distinct secondary estimand that gives high-volume municipalities greater influence. Do not call municipality-clustered standard errors equal-election weighting: clustering addresses dependence, not the target weights. If a future design repeats outcomes across race/year rows, inverse-row-count weights require a documented target, as in the German council precedent.

For the single NRW-2020 cohort, one election per municipality means election and municipality assignments coincide. Pooling repeated municipal elections would require compatible boundaries/windows and municipality-level dependence handling. Use exact election/municipality counts on both sides. Contract/result rows never supply additional independent mayoral assignments.

Proposed main inference is local linear RDD with data-driven bandwidths and robust bias-corrected uncertainty. FP15 must assess discrete-margin support, outcome-selected samples, few clusters and useful precision before a particular implementation is adopted. Pretreatment adjustment candidates include official 2019 population/fiscal variables with compatible vintages. Realized procedure, contract size, award success and post-election council composition are potential mediators/selection variables, not automatic baseline controls. No estimator has been run to select this draft's rules.

## Required construction states and completion evidence

Each future analysis row must be traceable to election ID, original assignment evidence/margin, municipality mapping, reporting stratum, buyer/beneficiary scope, procedure/lot/result/contract graph IDs, literal category, phase dates/date precision, outcome field type/value, result state, source UUID/version/hash and inclusion reason. Keep separate statuses for `unacquired`, `unlinked`, `scope_unresolved`, `timing_unresolved`, `category_unresolved`, `count_missing`, `result_pending`, `closed_unsuccessful`, `cancelled`, `awarded` and `conflicting_source`. Statuses can overlap; one generic missing flag loses the reason.

| Next decision | Responsible work package | Evidence required |
| --- | --- | --- |
| Confirm the two nominated primary candidates and settle conditional versus unconditional observed-event targets | FP04, informed by early FP15 and bounded coverage work | Coverage/denominator audits and useful precision for the intended claim; no effect-based selection |
| Establish or reject a common no-call event timestamp | FP04–FP08 | Original administrative fields and comparable semantic interpretation across source regimes |
| Select actual dates, maturity and follow-up cutoff | FP08 | Pinned archive availability and reporting-lag/phase audit |
| Apply individual scope/timing dispositions and unit rules | FP10–FP12 | Case ledger and graph reconciliation, including all finite pilot exceptions |
| Establish candidate/exposure and full election attrition | FP06/FP09/FP14 | Source-bounded histories and every structural pair's disposition |
| Decide whether strategic criteria are usable | FP13 | Field-applicability and completeness audit |
| Demonstrate useful precision and freeze confirmatory specifications | FP15–FP18 | Independent assignments, MDE/design checks, explicit go decision and dated preregistration |

FP04 is **in progress**, with this reviewable draft as its current output. Later source-dependent gates remain open. The pilot counts, candidate labels and frozen baseline have not been changed by drafting these rules. GitHub Pages remains deferred until research completion.

The [early linked-sample/precision audit](early-feasibility-decision.md) now precedes extensive FP06–FP13 execution. It finds three provisional candidate-window links, not a main-study sample. Independent coding is a separate gate under the [review protocol](independent-coding-protocol.md); packet preparation does not satisfy it. A bounded adaptation/stop decision can precede full collection.
