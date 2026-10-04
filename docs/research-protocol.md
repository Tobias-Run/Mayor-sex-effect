# Research protocol — preliminary

This document translates the original pitch into working research specifications. It is not a preregistration. Unresolved choices must be settled using feasibility evidence and documented before the main analysis.

## Question and contribution

Does electing a female mayor causally affect public procurement practices and outcomes in German municipalities? The project investigates competition, procurement procedure choice, and documented environmental, social, and innovation criteria. The proposed German contribution and the cited international findings require literature verification.

## Relationship to prior research

The project is a German adaptation of Florio and Spagnolo (2026), *Female Mayors and Public Procurement*, rather than an independently originated procurement design. It carries over the research question and close-election identification logic while adapting election eligibility, municipal responsibility, data linkage, and outcome measurement to Germany. Strategic procurement criteria are a proposed extension, conditional on measurement quality.

Existing German research is explicitly part of the foundation: Schild (2013), *Do Female Mayors Make a Difference? Evidence from Bavaria*, and Baskaran and Hessami (2025), *Women in Political Bodies as Policymakers* (also available as a 2023 working paper). Selected primary methods and data sections have been reviewed; the mayoral and council treatments remain distinct. Arnold (2018), Frank, Stadelmann and Torgler (2023), and GERDA inform acquisition and election comparability. See [literature.md](literature.md) for verified references and reading limits.

A comparison with Italy alone cannot identify the causal role of institutional differences between countries.

## Identification and estimand

Compare eligible decisive mayoral elections in which a woman narrowly defeats a man with elections in which she narrowly loses. Define the running variable as the female candidate's vote share minus the male candidate's vote share, measured in percentage points in the decisive round. Treatment is election of the female candidate; the threshold is zero. Ties and exceptional election outcomes require explicit rules.

The local effect concerns electing the female candidate rather than her actual male opponent. It does not identify gender independently of party, experience, incumbency, or other candidate characteristics. Eligibility rules must account for state-specific electoral institutions, multi-candidate races, and runoffs.

Causal interpretation requires continuity of potential outcomes at the cutoff and a defensible account of selection and election processes. Covariate adjustment cannot repair an invalid design.

The proposed target is the election-level intention-to-treat effect on procurement attributable to the municipality. It does **not** require the elected mayor to personally sign, award or manage each contract. Florio and Spagnolo describe a separate procurement officer responsible for the procedure (Section 2). Administrative delegation may transmit a political effect; restricting the sample to personally handled contracts could introduce selection. Verify municipal buyer/beneficiary scope and define how independent enterprises, joint purchasing and external agents enter the study. Personal involvement and delegation are potential mechanisms, not universal contract-eligibility certificates. Existing pilot fields marked `responsibility_assignment=unverified` are provenance flags and do not, by themselves, rule out municipal ITT eligibility.

## Outcomes under consideration

- Competition: number of bids and the share of awards with a single bid.
- Procedure: procurement procedure categories, subject to consistent definitions and coverage.
- Strategic procurement: documented environmental, social, and innovation criteria.
- Secondary candidates: SME winners, contract values, local winners, and repeated winners when measurable.

Cost overruns, delays, and renegotiations are excluded unless systematic, comparable measurement is demonstrated. Strategic criteria measure documentation, not realized environmental or social effects. Choose a small set of primary outcomes and testing families before the main study.

## Timing, units, and estimation

**Proposed timing alignment with Italy:** Florio and Spagnolo's baseline aggregates procedures published under the elected mayor (Section 4). Their robustness checks also consider publication and conclusion under the same mayor, and delayed publication after the election (Sections 5.2–5.3 and appendix). For German procedures with a prior call, prefer the original competition/tender publication date where observable; retain contract conclusion as a separate event and possible alternative specification. Publication of a later award-result notice is not the original tender publication. The Italian study also includes direct awards assigned without publishing a tender. Its ANAC publication field therefore cannot be assumed to mean prior-call publication for every procedure type. The exact direct-award administrative timestamp and a defensible German no-call timing rule remain to be established. A contract-date or result-publication substitution changes the exposure definition and requires explicit justification before preregistration.

**Procedure-specific outcome populations:** Italy's Table 2 includes direct awards in procedure-choice outcomes, while Table 3 restricts bidder-count regressions to Open&Negotiated. Specify separate eligibility and denominator rules for German procedure-choice and bidder outcomes, including restricted procedures and national source codes. German `neg-wo-call` is not automatically equivalent to the Italian direct-award category; a no-call procedure is distinct from an unacquired competition notice. The [procedure-scope audit](feasibility/nrw-procedure-scope-and-term-followup.md) identifies three such paired observations. Preserve their documented counts, reasons and dates without inventing an earlier tender date or silently removing them from every outcome. Treatment can affect procedure choice, so conditioning on realized competitive procedures selects an outcome-specific population. Interpret such estimates accordingly, assess composition and reporting, and do not automatically describe them as the ITT over all municipal purchases.

Link procurement phases to source-supported actual head-role intervals and retain the source, date precision and any unresolved boundary or interruption. A dated official person-role history can supply observational term boundaries; formal acceptance and predecessor-exit records help resolve ambiguous entries under NRW law. The legal council calendar, oath and first workday remain distinct. No personal-signature certificate is required. The evidence rule and handling of uncertain intervals must be chosen before the main analysis; this clarification does not automatically relabel pilot records. Investigate preparation under predecessors, delayed effects, equal observation windows, early exit and short follow-up after late elections.

The proposed estimator is local linear RDD with data-driven bandwidths and robust bias-corrected confidence intervals. Account for within-municipality dependence; repeated elections require municipal clustering. Many contracts do not substitute for sufficient independent elections.

Contract-level and election-level weighting imply different estimands. Weighting, handling of repeated elections, treatment compliance, and the final sample must be decided before the main analysis.

Preserve original notice UUID/version and explicit lot–result–tender–contract relationships. Select result histories using a specified rule; do not equate notices, procedures, lots and contracts. The [federal export audit](feasibility/national-procurement-open-data.md) supplies original eForms and demonstrates that converted CSV buyer roles and statistic types can differ from the original. Source timestamps, dispatch/requested publication, actual publication and contract dates must remain distinct.

## Diagnostics and limitations

Assess covariate balance, vote-margin distributions, alternative bandwidths, placebo cutoffs where appropriate, and pre-election outcomes when available. Recognize discrete vote counts and small-sample limits of density tests. Separate baseline characteristics from post-treatment variables.

Procedure choice, contract volume, contractor selection and procurement-officer assignment may themselves respond to treatment. Do not automatically copy the Italian paper's procedure controls into the German primary model; define any conditional or mechanism estimand separately.

Investigate reporting thresholds, missing values, procurement volumes, buyer responsibilities, and treatment-related selection into observed records. Public notices and TED cover selected procurement, not all municipal purchases. Describe the population represented by the final data.

A non-significant estimate is not evidence of no effect unless precision supports that conclusion. Procedure changes alone do not establish efficiency or corruption effects. Generalization beyond eligible close elections is limited.
