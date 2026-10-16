---
title: "From Close Elections to Procurement Outcomes"
subtitle: "A bounded German feasibility audit adapting Florio and Spagnolo (2026)"
date: "16 October 2026 — Version 0.2, review draft"
lang: en
---

# Abstract

Can German municipal data support a close-election study of female mayors and public procurement? We adapt the research question and close-election strategy of **Florio and Spagnolo (2026), *Female Mayors and Public Procurement*** to German institutions and data sources. Existing German mayoral research supplies institutional and methodological precedents, including Schild (2013) and Baskaran and Hessami (2018). We audit election identities, historical public presentation, municipal buyer linkage, original procurement notices, observation windows and assignment-level precision. An expanded bookkeeping frame contains {{events}} events in {{municipalities}} municipalities. It yields {{provisional_elections}} provisional mixed-presentation elections with original-supported tender-count statistics, spanning incompatible cohort windows, and {{certified_elections}} independently certified main-study elections. A favorable-resolution ceiling for the current NRW 2025 count route is ten elections; its simplified Gaussian 80% minimum detectable effect is 2.33 outcome standard deviations. These are feasibility results, not treatment-effect estimates. The audited protocols do not support launching the proposed causal main study. Independent coding and substantive manuscript review remain incomplete.

# 1. Research question and attribution

The proposed application asks whether electing a female-presented mayor rather than her actual opponent changes procurement competition or procedure choice. Florio and Spagnolo (2026) provide the explicit Italian foundation. Their procurement populations, reporting system and electoral context cannot simply be assumed to transfer to Germany. The present contribution assesses that transfer's data and design requirements. It does not reproduce their Italian estimates or establish that their findings apply in Germany.

Schild (2013) studies female mayors and fiscal decisions in Bavaria. Baskaran and Hessami (2018) provide a direct German female-mayor close-election precedent in Hesse, studying subsequent female political participation. Baskaran and Hessami's *Women in Political Bodies as Policymakers* studies a different treatment, councillors, and childcare outcomes. These papers inform event-specific election rules, outcome timing, treatment definitions and inference. None supplies procurement effects for the sample audited here. GERDA (Heddesheimer et al., 2025) provides a valuable election compilation; later mayoral extensions and their source provenance still require version-specific validation.

The intended estimand is the local effect of electing a particular female-presented candidate instead of the particular competing candidate near a decisive-round tie. Candidate characteristics and political platforms accompany that assignment. The design cannot identify an isolated biological sex or gender effect. Historical public presentation is also distinct from an administrative sex/gender register measure, which the accepted source observations do not establish.

The literature review is targeted rather than systematic. The pinned literature crosswalk documents inspected editions, exact source locators and access failures. The Italian working paper was obtained; the 2018 German study was inspected through its 2017 working paper because final-journal access failed. Its replication record was identified, but the package, license and data were not audited. The 2025 councillor article's journal version was likewise not inspected; methodological statements refer to the acquired 2023 working paper. No German novelty priority claim follows from this review.

# 2. Audit scope and evidence rules

The audit began with Bavaria and NRW and tested bounded extensions to Brandenburg, Niedersachsen and Saxony. Historical checkpoints retain their original populations and dates. This synthesis uses the P1–P5 evidence through 15 October 2026, at evidence commit `aa70a89c31afa33003711fa5688db1ab4fb67e3f`. The procurement observation cutoff remains **30 September 2026**. Neither the manuscript date nor a later retrieval date extends follow-up.

Nationwide procurement discovery is possible through the German procurement OpenData exports and TED. This does not create a universal, complete municipal purchase register. Reporting coverage, thresholds, procedure categories, original accessibility and identifier continuity differ. Official election information and historic candidate identities still require state- and event-specific sources. Bavaria's structural election coverage and scalable TED availability did not demonstrate a jointly validated historical candidate/outcome sample. NRW's official election and original-notice routes were more productive, but their joint sample remained small.

Election events are keyed by cohort, municipality identifier (AGS) and decisive date. Official identities, votes, valid-vote denominators and assignment rules are checked separately. The 10 percentage-point ceiling is an acquisition rule, retaining nested 2/5-point strata; it is not a selected RDD estimation bandwidth. Saxony's second-round plurality events are audited separately rather than silently equated to two-candidate runoff assignments.

Candidate observations require an explicit, personally attributable historical primary-source presentation linked to the relevant identity and election context. Names, photographs, name predictions, occupational stereotypes and generic masculine office nouns do not substitute for evidence. Unresolved pairs remain unresolved. A known same-presentation pair is distinct from an unclassified pair. These rules improve traceability but may favor well-documented candidates and municipalities; they do not remove selection bias.

Procurement records pass distinct checks for municipal contracting-party scope, procedure identity, original call timing, result linkage and the requested statistic. A notice, notice version, procedure, contract, lot and tender-count statistic are different units. Missing statistics remain missing; they are not zero bids or zero purchases. The call inventory provides the relevant observed denominator even where a supported result statistic is absent. Original-source validation is limited to the acquired records and does not establish complete reporting.

# 3. Results: source coverage is larger than the joint sample

The current scoreboard contains **{{events}} bookkeeping events in {{municipalities}} municipalities**, including seventeen excess repeat events/seventeen repeated municipal clusters. Its broader structural discovery union has 674 events in 649 municipalities. Neither quantity is a count of eligible treatment assignments. Repeated municipalities also require dependence accounting in any future design.

The seven Saxony 2022 leads all received official final-result and event-law checks. Fourteen candidate dispositions support two mixed pairs, both female-presented losses, and leave five pairs unresolved. The two mixed pairs fall outside five percentage points. Their 654 calendar-2024 call notice/version records lack procedure GUIDs, yielding no additional original-supported mixed-count link. Calendar availability and successful finalist identification therefore do not establish a usable outcome sample.

The six provisional mixed-count links in Table 1 are the intersection of accepted first coding and supported original tender-count evidence. They contain **{{procedures}} call procedures and {{statistics}} statistics**. The two totals need not match: multi-lot procedures can produce several statistics, whereas other supported calls have none. All six remain uncertified for main-study use.

**Table 1. Provisional joint links; statistics are not independent elections.**

{{linked_table}}

NRW 2025 uses Q1 2026 calls. Werdohl's NRW 2020 link uses Q1 2025, and Bückeburg's Niedersachsen 2021 link uses calendar 2025. Only the four NRW 2025 cases align with the diagnostic first Q1 after the election. Relabeling the older late-term ledgers would not create comparable first-term windows. The table preserves them for audit rather than pooling them into an effect estimate.

Bückeburg has six supported call procedures without a supported tender statistic. Those calls remain in the inventory. Award dates after the call-selection window can be valid follow-up; restricting results to that same calendar interval would introduce another selection step. Actual procurement decision dates, complete reporting and continuous original-winner exposure remain unverified for all six events.

Office-entry documents and dated role observations improve chronology but do not independently adjudicate every legal entry boundary or establish uninterrupted service. An intention-to-treat design would retain the original election assignment through subsequent turnover. Continuous original-winner service is a separate exposure sensitivity, not an ITT inclusion condition. None of the nine NRW 2025 call procedures has nine months of follow-up at the retained cutoff. The eleven older procedures are calendar-mature, which still does not establish reporting completeness.

# 4. Alternative outcome and expansion tests

The historical procedure-choice calibration retains all 55 NRW 2020 elections in its availability frame. Nineteen have method metadata in both 2019 and 2021, but a fixed ten-case original-source calibration produced only two usable originals after thirty attempts and no case validated in both periods. Inaccessible records are not thereby proven invalid. They cannot be promoted to validated paired outcomes.

Accessible method details agree with their original records, while one buyer-type conflict remains. Compiled broad categories can also obscure distinctions such as competitive negotiation versus open procedure. Eleven explicit no-call records, a missing award date, source-year/date conflicts and repeated document references complicate a naive pre/post share. An all-procedure choice outcome requires defensible direct/no-call coverage; an advertised-procedure share answers a narrower, potentially selected-population question. Neither is adopted as a validated primary outcome.

Calendar-2024 alternatives and wider acquisition frames create additional leads, but their source inventories overlap with existing routes and their municipal composition differs across years. Joins require exact cohort/AGS keys. Outcomes cannot be pooled merely to raise nominal sample size. More procurement records within one municipality do not create additional independently assigned elections.

# 5. Design support and conditional precision

Among the provisional NRW 2025 links, the 2-point band has two female-presented losses and no wins. At five and ten points, four elections split two wins/two losses. A local linear specification with an intercept, treatment indicator, running variable and treatment-by-running-variable interaction has four columns and rank four: no residual degrees of freedom remain. A six-column quadratic specification is underidentified. This algebraic diagnostic is not an RDD power simulation.

Table 2 asks a deliberately favorable question: holding accepted first coding and current source availability fixed, what if every unresolved presentation and every other unverified gate resolved favorably? Partial accepted labels constrain the possible winning side and known same-presentation pairs stay excluded. Independent recoding could change the accepted classifications. These are conditional ceilings for specific inventories, not global bounds on Germany.

**Table 2. Ten-point acquisition-band ceilings, separately by route and cohort.**

{{ceiling_table}}

Source N counts elections with relevant source evidence; Max mixed N is the favorable-resolution maximum. W/L denotes female-presented wins/losses at the best feasible balance. The historical-method row is a metadata-only thought experiment with **zero original-validated paired outcome cases**. Rows overlap and cannot be added. NA indicates no estimable two-sided contrast. The unusually large three-election MDE reflects one residual degree of freedom in the pooled t benchmark.

MDEs assume independent equal-variance Gaussian election-level observations, a two-sided pooled t test, 80% power and alpha .025 per outcome, retaining the earlier two-primary-outcome planning allocation. They omit RDD slopes, kernels, bias correction, selection, estimated controls and extra dependence. They are illustrative comparisons, not RDD launch thresholds or guaranteed lower bounds for every estimator. No outcome SD or pre-election predictive R-squared has been validated.

**Table 3. Balanced election requirements under the same simplified benchmark.**

{{precision_table}}

The R-squared scenario grants 75% explained variance without a control-estimation penalty; it is an assumption, not an achieved adjustment. At the best current count ceiling of ten elections, benchmark power is about 6.0% for .5 SD and 18.5% for 1 SD, with MDE 2.33 SD. Even that unsupported adjustment leaves MDE about 1.16 SD. The single-primary alpha .05 sensitivity appears in the pinned benchmark table but is not adopted to rescue feasibility. Conversion to bidder counts or percentage points requires an independently justified outcome variance and substantive target effect.

# 6. Selection, independent review and reproducibility

Municipal documentation, incumbency, winning status, publication practices and usable identifiers may affect inclusion. Strict sourcing can change who is observed. The audit records excluded and unresolved events, including cases without procurement matches, rather than retaining only successful joins. It does not estimate an inclusion propensity, demonstrate ignorable missingness or correct selection by favorable-resolution arithmetic.

The current independent-review packet covers thirteen pairs: all six provisional links plus seven controls, with 26 blank forms and 22 verified source copies. **No independent reviewer is available, no pair has been independently completed, and agreement and disagreement counts are NA.** Packet preparation is not independent validation. Forms omit first-coder labels, winner/margin and outcomes; original documents and public context can nevertheless reveal facts. A reviewer must declare prior exposure. Returned coding must be preserved before key release, with disagreements retained before adjudication. An additional model pass is not presented as independent human review.

This manuscript is generated from thirteen SHA-256-pinned public evidence artifacts. Its tables and accounting can be rebuilt offline without person-level files. The public reproduction checks establish consistency with those artifacts, not independent validity of the original classifications or complete replication of the private source audit. Candidate worksheets, original-document bundles and reviewer keys remain local. The frozen v0.1 report and its evidence cutoff are preserved. This new synthesis is a **review draft**, with independent coding, substantive review and a completed-report decision still outstanding. GitHub Pages remains deferred.

# 7. Decision and conditions for reopening

The bounded audit does not support a causal main-study launch under the examined protocols. The contribution is a documented feasibility assessment of transferring the Italian design: source scale does not guarantee joint assignment/outcome support, and a large procurement inventory cannot repair very few independent elections. No treatment coefficient, causal effect, primary-outcome mean or null-effect conclusion is reported. This is not evidence that female mayors have no procurement effect, nor that German causal mayor research is generally impossible.

Further extensive individual-case retrieval should follow a materially different, source-pinned complete cohort with demonstrated joint outcome yield and a finite budget. Before reopening, the project needs a validated outcome population and denominator; comparable election-relative windows and mature, audited follow-up; independent coding of inclusions and exclusion controls; and a substantively justified effect target with empirical variance and design-specific precision accounting for repeated municipalities. No current route meets that combined standard. A panel or other design would require its own identification argument rather than an automatic fallback.

# References

Baskaran, T., and Z. Hessami. 2018. “Does the Election of a Female Leader Clear the Way for More Women in Politics?” *American Economic Journal: Economic Policy* 10(3): 95–121. https://doi.org/10.1257/pol.20170045. Methods inspected in the 2017 working-paper edition; final-journal differences unverified.

Baskaran, T., and Z. Hessami. 2025. “Women in Political Bodies as Policymakers.” *Review of Economics and Statistics* 107(6): 1501–1517. https://doi.org/10.1162/rest_a_01352. Methods inspected in the 2023 working paper; final-journal differences unverified.

Florio, E., and G. Spagnolo. 2026. *Female Mayors and Public Procurement*. Working paper, CEIS Research Paper 623, revised July 2026. https://doi.org/10.2139/ssrn.7046899. Explicit foundation of the German adaptation.

Heddesheimer, V., H. Hilbig, F. Sichart, and A. Wiedemann. 2025. “GERDA: The German Election Database.” *Scientific Data* 12: 618. https://doi.org/10.1038/s41597-025-04811-5. Later mayoral repository extensions require their own snapshot attribution.

Schild, C.-J. 2013. *Do Female Mayors Make a Difference? Evidence from Bavaria*. IWQW Discussion Paper 07/2013. https://hdl.handle.net/10419/81935.

# Evidence and reproduction

Repository: https://github.com/Tobias-Run/Mayor-sex-effect. The companion README links the source-specific audits, measurement codebooks, literature crosswalk, public input manifest and build command. The report does not introduce new source retrievals or revise the retained procurement cutoff.
