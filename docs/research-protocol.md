# Research protocol — preliminary

This document translates the original pitch into working research specifications. It is not a preregistration. Unresolved choices must be settled using feasibility evidence and documented before the main analysis.

## Question and contribution

Does electing a female mayor causally affect public procurement practices and outcomes in German municipalities? The project investigates competition, procurement procedure choice, and documented environmental, social, and innovation criteria. The proposed German contribution and the cited international findings require literature verification.

## Identification and estimand

Compare eligible decisive mayoral elections in which a woman narrowly defeats a man with elections in which she narrowly loses. Define the running variable as the female candidate's vote share minus the male candidate's vote share, measured in percentage points in the decisive round. Treatment is election of the female candidate; the threshold is zero. Ties and exceptional election outcomes require explicit rules.

The local effect concerns electing the female candidate rather than her actual male opponent. It does not identify gender independently of party, experience, incumbency, or other candidate characteristics. Eligibility rules must account for state-specific electoral institutions, multi-candidate races, and runoffs.

Causal interpretation requires continuity of potential outcomes at the cutoff and a defensible account of selection and election processes. Covariate adjustment cannot repair an invalid design.

## Outcomes under consideration

- Competition: number of bids and the share of awards with a single bid.
- Procedure: procurement procedure categories, subject to consistent definitions and coverage.
- Strategic procurement: documented environmental, social, and innovation criteria.
- Secondary candidates: SME winners, contract values, local winners, and repeated winners when measurable.

Cost overruns, delays, and renegotiations are excluded unless systematic, comparable measurement is demonstrated. Strategic criteria measure documentation, not realized environmental or social effects. Choose a small set of primary outcomes and testing families before the main study.

## Timing, units, and estimation

Link awards to actual terms in office using a documented date rule. Investigate preparation under predecessors, delayed effects, equal observation windows, and short follow-up after late elections.

The proposed estimator is local linear RDD with data-driven bandwidths and robust bias-corrected confidence intervals. Account for within-municipality dependence; repeated elections require municipal clustering. Many contracts do not substitute for sufficient independent elections.

Contract-level and election-level weighting imply different estimands. Weighting, handling of repeated elections, treatment compliance, and the final sample must be decided before the main analysis.

## Diagnostics and limitations

Assess covariate balance, vote-margin distributions, alternative bandwidths, placebo cutoffs where appropriate, and pre-election outcomes when available. Recognize discrete vote counts and small-sample limits of density tests. Separate baseline characteristics from post-treatment variables.

Investigate reporting thresholds, missing values, procurement volumes, buyer responsibilities, and treatment-related selection into observed records. Public notices and TED cover selected procurement, not all municipal purchases. Describe the population represented by the final data.

A non-significant estimate is not evidence of no effect unless precision supports that conclusion. Procedure changes alone do not establish efficiency or corruption effects. Generalization beyond eligible close elections is limited.
