# P5 decision memorandum — 15 October 2026

**Decision: do not prepare a causal main-study launch under the current audited protocols. Close this bounded feasibility cycle and retain the project as a feasibility/descriptive contribution.** None of the examined routes demonstrates a sufficiently large, validated, comparable joint sample. Additional case-by-case presentation research within the current outcome inventories would not solve the precision problem. Independent review remains open and cannot be reported as passed.

This conclusion is about the examined sources and protocols. It does not establish that causal research on German mayors is impossible or that inaccessible underlying procurement records are invalid. Reopening requires a demonstrably different complete cohort/source route meeting the gates below, rather than continued unbounded retrieval.

## What the audited evidence supports

The [P1/P2 scoreboard](measurable-progress-p1-p2-checkpoint.md) contains 176 bookkeeping events in 159 municipalities, including seventeen repeated clusters; it is not a sample of eligible mixed elections. The six provisional mixed-count links comprise four NRW 2025 elections and one each from NRW 2020 and Niedersachsen 2021. **No independently certified main-study elections exist.** The [P4 audit](exposure-and-independent-review-p4.md) retains all six and their incompatible windows, without pooling them.

For NRW 2025, the 2 pp band contains two female-presented losses and no female-presented wins. At 5 pp and 10 pp it contains four elections, two wins and two losses. A local linear design with separate slopes has four columns and rank four, leaving **zero residual degrees of freedom**; a quadratic specification is underidentified. Dropping cases cannot repair that support. Treating procedures or lots as additional elections would hide the assignment-level bottleneck.

The [design-support table](readiness-design-support.csv) reports algebraic support and a simplified two-group precision benchmark separately. Actual RDD power is not estimated: there is no certified common-window outcome sample or validated outcome variance, functional form, coverage model or pre-election predictive R-squared. No causal effects or null findings are inferred.

## Conditional favorable-resolution bounds

The [full nested 2/5/10 pp table](readiness-conditional-ceilings.csv) holds current accepted first coding fixed and assumes unresolved candidate presentations resolve into mixed pairs wherever possible. Partial accepted labels constrain the feasible winning side; known same-presentation pairs stay excluded. It then assumes all remaining validity and coverage gates pass. These are deliberately favorable **conditional source-inventory ceilings**, not certified sample sizes, global bounds on Germany, or additions across routes. Independent recoding could alter accepted classifications.

The 10 pp results are:

| Fixed source route and cohort | Elections with relevant source evidence | Conditional maximum mixed elections | Best feasible win/loss balance | Gaussian 80% MDE (SD) |
|---|---:|---:|---:|---:|
| Current count window, NRW 2025 (2026 Q1 calls) | 13 | 10 | 5 / 5 | 2.33 |
| Current count window, NRW 2020 (2025 Q1 calls) | 4 | 3 | 1 / 2 | 39.98 |
| Current count window, Niedersachsen 2021 (2025 calls) | 3 | 3 | 1 / 2 | 39.98 |
| Current count window, Brandenburg 2024 | 1 | 1 | No contrast | Not estimable |
| Current count window, Brandenburg 2025 | 1 | 1 | No contrast | Not estimable |
| Separate calendar-2024 count audit, NRW 2020 | 13 | 9 | 4 / 5 | 2.54 |
| Separate calendar-2024 count audit, Niedersachsen 2021 | 4 | 4 | 2 / 2 | 8.01 |
| Historical 2019/2021 method metadata, NRW 2020 | 19 | 15 | 7 / 8 | 1.77 |

The unusually large three-election MDE follows from the pooled t benchmark's single residual degree of freedom; it is not an effect estimate. The last row has **no original-validated paired outcome sample** and is only a metadata-contingent thought experiment. P3 inspected ten fixed calibration cases, with no case original-supported in both periods; neither the all-procedure outcome nor the narrower called-only share is adopted. The seven Saxony 2022 events add two supported mixed pairs but zero original-supported count links; they do not increase these outcome-based bounds. Niedersachsen's separate calendar-2024 set is a different set of municipalities from its earlier calendar-2025 set; joins use cohort and exact AGS, never a guessed name match.

Each row uses a fixed cohort and source window. The two NRW-2020 count routes overlap in municipalities and cannot be summed. Repeated municipalities elsewhere likewise require dependence accounting. Source-specific missingness and stricter evidence requirements can select documented municipalities and roles; favorable-resolution arithmetic does not correct that selection.

## Precision scenarios and their limits

The [benchmark table](readiness-gaussian-benchmarks.csv) uses independent equal-variance Gaussian election-level observations, a pooled two-sided t test and 80% power. It has no running-variable slopes, kernel, robust bias correction, reporting selection, estimated controls or extra dependence. These are reference calculations, not RDD launch thresholds or a mathematically guaranteed lower bound for every possible estimator.

Retaining the existing planning allocation **alpha = .025 per outcome**, effects of .25, .5 and 1 outcome SD require **612, 156 and 42** balanced independent elections respectively. Assuming a pre-election predictor explains 75% of outcome variance reduces the benchmark to **156, 42 and 14**. That R-squared is unvalidated, and the calculation grants it without a control-estimation penalty. The single-primary alpha=.05 sensitivity yields 506/128/34 without adjustment; changing the primary family is not adopted to rescue feasibility.

Even the best current count ceiling of ten elections gives only about **6.0% power for .5 SD** and **18.5% for 1 SD** at alpha=.025. Its favorable adjusted MDE under the unvalidated R-squared=.75 assumption is still about **1.16 SD**. Historical method metadata's fifteen-election ceiling gives MDE **1.77 SD**, or **.89 SD** with that same unsupported adjustment. These comparisons do not require pretending metadata are validated outcomes. We cannot translate them into bidders or procurement-share percentage points without an independently justified outcome SD and substantive target effect.

## Deliverable and reopening gates

The chosen next deliverable is an English feasibility manuscript documenting the adaptation of **Florio and Spagnolo (2026)**, the relevant [German research](../literature.md), the complete source denominators, measurement failures, cohort-specific joint yields, selection concerns and precision limits. It must explicitly state that absence of a viable design is not evidence of zero procurement effects. Preserve the frozen report and historical checkpoints; any new manuscript should be a separately dated feasibility version, without causal coefficient claims. GitHub Pages remains deferred until the research contribution is complete.

A future main-study proposal needs all of the following before new extensive individual-case acquisition:

1. A named, accessible and source-pinned complete state/year cohort with official finalist identities, votes and event-specific assignment rules, plus a bounded budget and a demonstrated joint outcome yield. Metadata counts alone do not qualify.
2. A validated primary outcome/population and denominator, consistent election-relative windows, defensible decision-time proxies, mature follow-up and an audit of reporting selection. Retain original assignment through turnover for ITT; distinguish continuous-service sensitivity.
3. Independent coding covering included pairs and exclusion controls, immutable returns before key release, agreement and unresolved-disagreement accounting. No reviewer is presently available.
4. A substantively justified target effect and empirical outcome-variance/predictive inputs supporting design-specific, municipality-dependent power and robustness analysis. More procedures within the same elections do not meet this gate.

No current row clears those gates. The decision closes the bounded route tests; it does not silently relax source validity, widen the 10 pp acquisition gap, adopt an unvalidated outcome, or pool incompatible cohorts.
