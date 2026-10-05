# Early feasibility decision following supervisory feedback

**Subsequent checkpoint:** the single [Bavaria route test](bavaria-bounded-route.md) is now complete. The [bounded go/adapt/stop memorandum](go-adapt-stop.md) ends the current causal launch and selects a feasibility/data report. This earlier memo retains the original assumptions and finite decision-block schedule; it no longer schedules additional collection.

**5 October 2026. Decision: continue a bounded feasibility/adaptation audit; do not prepare the main causal study on the present evidence.** This is an early checkpoint, not FP16's final NRW decision or a preregistration. The supervisor's memo moves precision and the actually linkable sample ahead of extensive acquisition. It requires an explicit next decision: prepare the main study, pursue a viable targeted expansion, or end the causal claim.

**The project adapts Florio and Spagnolo (2026), [*Female Mayors and Public Procurement*](https://doi.org/10.2139/ssrn.7046899), to Germany**, building on Schild (2013), Baskaran and Hessami (2018, Hesse mayors; 2025, Bavarian councillors), and the other German foundations in the [literature crosswalk](literature-design-crosswalk.md). The contrast concerns electing a specific female-presented candidate rather than her actual opponent near the cutoff. Party, experience and other candidate attributes can differ. Our current historical presentation measure is distinct from an administrative sex/gender field.

## Sample that can currently be linked

The new [55-election linkage matrix](nrw-early-linkage-matrix.csv) combines the existing candidate dispositions with the frozen procurement pilot. It preserves unsupported scope, reporting, exposure, deduplication and follow-up as pending. **Zero certified main-study elections** remain; the numbers below describe successive provisional intersections.

| Existing evidence | Independent municipal elections | Female-presented wins / losses | Meaning |
| --- | ---: | ---: | --- |
| Supported mixed pairs within 2 pp | 4 | 1 / 3 | Presentation-supported elections; procurement eligibility not assumed |
| Most favorable resolution of the two open pairs within 2 pp | At most 6 | Best feasible balance 3 / 3 | Conditional upper bound, not six acquired/eligible assignments |
| Supported mixed pairs within 10 pp | 6 | 2 / 4 | A wider acquisition inventory, not a chosen RDD bandwidth |
| Those six with any existing dated/count pilot units | 4 | 1 / 3 | Periods vary; no complete common observation window |
| Those six with supported called-procedure dates in 1 Nov 2023–31 Dec 2024 | 3 | 1 / 2 | At least one existing result statistic in the candidate window; reporting and common result follow-up unverified |

The original **123 dated/count units across six municipalities** include Viersen and Werdohl, whose mixed-pair measurement is still unresolved. They are not 123 independent assignments or six currently eligible mixed elections. The provisional common-window intersection has **13 observed result units**, before complete deduplication, from Velbert, Geilenkirchen and Unna.

| Confirmed mixed pair | Any dated/count pilot units | Supported called units in candidate window | Remaining interpretation |
| --- | ---: | ---: | --- |
| Iserlohn | 44 | 0 | Existing supported call dates do not enter this candidate window; zero here is not zero procurement |
| Velbert | 45 | 10 | Provisional linkage; systematic reporting, results and unit graph still need audit |
| Geilenkirchen | 18 | 2 | Same unresolved study gates |
| Unna | 4 | 1 | Three no-call units require a separate timing/population rule |
| Sendenhorst | 0 | 0 | No supported dated/count pilot units in the current inventory; no conclusion about actual purchases |
| Wilnsdorf | 0 | 0 | Same acquisition limitation |

This is a join of existing evidence, **not an FP07 census**. A missing pilot unit cannot establish outcome absence, universal archive access or true nonreporting. A result notice's publication/contract date cannot substitute for its original call date. The proposed late-term window and September-2026 result cutoff remain unselected. All 15 frozen baseline pins and the candidate codebook/worksheet are unchanged.

## Early precision calculation

The [benchmark table](nrw-early-precision-benchmarks.csv) deliberately starts with a simpler experiment: independent election-level outcomes, a common Gaussian within-group SD, equal election weights, an unadjusted two-group comparison and a two-sided pooled t test. It omits running-variable slopes, kernel weights, bias correction, outcome selection and reporting uncertainty. Thus it is an **optimistic planning benchmark under declared assumptions, not RDD power, a universal lower bound or a treatment-effect estimate**. Good pretreatment adjustment can change residual variance; a real RDD and outcome audit can change sample support and uncertainty.

MDE means the effect giving **80% power** at the stated significance level, in units of the **municipal outcome SD**. A normal approximation assumes known variance; the pooled-t benchmark includes small-sample variance uncertainty.

| Scenario | Elections: wins / losses | Normal-approximation MDE, alpha .05 | Gaussian pooled-t MDE, alpha .05 | Pooled-t MDE, alpha .025 |
| --- | ---: | ---: | ---: | ---: |
| Confirmed within 2 pp | 1 / 3 | 3.23 SD | 6.53 SD | 9.25 SD |
| Most favorable six within 2 pp | 3 / 3 | 2.29 SD | 3.07 SD | 3.74 SD |
| All six confirmed within 10 pp | 2 / 4 | 2.43 SD | 3.26 SD | 3.97 SD |
| Provisional common-window intersection | 1 / 2 | 3.43 SD | 20.00 SD | 39.98 SD |
| Every unresolved pair within 10 pp becomes mixed, with best feasible balance | 22 / 23 | 0.84 SD | 0.85 SD | 0.95 SD |

Alpha .025 is a conservative Bonferroni planning allowance for two primary outcomes with family error .05. These calculations assume every election in each scenario has a defined usable outcome. The 45-election scenario excludes ten already supported same-presentation pairs and treats all 39 unresolved pairs as potentially mixed. It is **an upper-bound scenario, not an acquisition forecast, a recommended bandwidth or evidence of a viable linked sample**. Its existence prevents a definitive claim that a larger NRW study is impossible; its assumptions are much stronger than the available evidence.

For an illustrative **10 pp municipal SD**, the favorable six-election benchmark needs about **31 pp**, or **37 pp** with the two-outcome allowance. The actual variance and a substantively meaningful minimum effect have not been established. The [MDE sensitivity grid](nrw-early-precision-sensitivity.csv) also uses municipal SDs of 5 and 20 pp; the separate [effect-size/power grid](nrw-early-effect-size-power.csv) evaluates hypothetical 5/10/20-pp changes against each variance assumption. These are planning values, not empirical estimates, substantive thresholds or exact power for a bounded share. MDEs exceeding an outcome's possible range are flagged rather than presented as attainable effects.

The [balanced-election benchmarks](nrw-early-precision-required-elections.csv) illustrate scale: for a 0.5-SD effect the Gaussian two-group model needs 128 elections at alpha .05 or 156 at alpha .025; for a 1-SD effect it needs 34 or 42. These are **not universal RDD sample-size requirements or go thresholds**. Actual margins, precision, coverage, covariates and the chosen outcome population must govern a later design-specific assessment. A 5/10/20-pp effect grid is only a planning sensitivity until substantive justification exists; it must not be chosen from statistical significance.

## Cutoff support is a separate problem

The [design-support table](nrw-early-design-support.csv) checks the geometry of existing signed margins without regressing any outcome. A separate-slope local-linear matrix has four columns: intercept, assignment, margin and their interaction. Within 2 pp it has **rank 3 of 4**, because there is only one supported female winner. The three provisionally linked elections also have rank 3 of 4. Within 1 pp there are no supported female wins.

Across the six supported mixed pairs within 10 pp the linear matrix has rank 4, but the corresponding separate-side quadratic matrix has **rank 5 of 6**, with only two female wins. That does not support a conventional separately fitted quadratic bias correction using only those six elections. Rank checks are necessary algebraic diagnostics, not proof of continuity, adequate inference or a usable bandwidth. Wider support, alternative inference or covariate restrictions would require a new justified specification, not an automatic workaround.

## Selection and independent coding

The [descriptive selection audit](nrw-early-selection-audit.csv) has historical presentation evidence for **22/55 winners (40.0%) versus 18/55 losers (32.7%)**. Six pairs support only the winner and two only the loser; 16 support both and 31 neither. This difference neither proves bias nor validates unbiased inclusion. The within-2-pp candidates have 90% support, versus 16.25% beyond 2 through 10 pp, reflecting deliberate search prioritization. Round and acquired-official-document strata are also reported; document acquisition itself can reflect search effort and salience.

Incumbency, municipal size/fiscal capacity and historical web-preservation quality are not currently harmonized baseline covariates for this audit. The next selection inventory must use validated **pre-election** measures, compare included/excluded/unresolved pairs and outcome availability, and retain unavailable covariates explicitly. No predictions, names or generic titles will be used to increase the apparent sample. High agreement between coders would not by itself repair source availability or procurement selection.

An [independent-coding protocol](independent-coding-protocol.md) and empty [form](independent-coding-template.csv) are now prepared. Local packets cover **all 16 classified pairs, including the ten same-presentation exclusions, plus 12 unresolved audit pairs**. The two open priority pairs are included. Prior labels, votes, signed margins and GERDA predictions are withheld; the first-coder key is in a separate local directory. Original documents can reveal office/outcomes, so full blinding is not claimed. **No independent reviewer is assigned and no second coding has occurred.** Re-reading by the first coder or mechanical locator checks do not satisfy the independence requirement.

## Narrowed research scope

Nominate at most **two primary outcome candidates**: (1) the share of unique in-scope procedures using negotiated procedures, preserving with-call and without-call categories; (2) the share of supported called-procedure result statistics with exactly one total tender. Their denominators and timing must pass the [outcome codebook](outcome-population-codebook.md) gates before confirmation. Tender counts measure offers, not distinct firms. Conditional realized-procedure/result samples require a conditional interpretation.

Mean tenders, monetary/winner measures and environmental/social/innovation fields become secondary or exploratory/conditional feasibility extensions. They do not enlarge the primary family in this phase. If a nominated measure fails coverage, record its failure and revise the scope explicitly; do not quietly replace it with a more favorable measure. The final test family, relevant-effect thresholds and estimator remain FP18 decisions after a go finding.

## Next decision block and effort limit

The next checkpoint has a **maximum 12 focused research hours / approximately two working days**, excluding another person's independent-review time and availability. Existing long acquisition budgets are conditional on a viable route emerging. Broad notice harvesting, full 159-pair hand-searching and repeated low-yield Heiden/Viersen queries pause in this block.

| Allocation | Work and deliverable |
| --- | --- |
| 2 hours | Reconcile existing links and uncertainty; completed by this matrix, with further refinements only if a material inconsistency appears |
| 2 hours | Early precision/side-support screen and effect-size/variance sensitivity; completed by these benchmarks, with substantive-threshold input still pending |
| 2 hours | Selection inventory and reviewer packet; packet prepared, pre-election covariates and independent review still incomplete |
| 2 hours | Test one scalable source route: the available Bavaria-2020 register first, assessing actual gender evidence and overlapping procurement coverage. The Hesse replication readme/license is a secondary methods/access check; its old cohorts do not automatically supply 2020 assignments. |
| 2 hours | Compare observed and plausibly obtainable linked election counts with the relevant-effect target; write the next go/adapt/stop memorandum |
| 2 hours | Reserve for one promising material uncertainty; unused time is not a mandate for more case searching |

At the next memo, report **observed counts and expansion assumptions separately**, independent assignments by cutoff side, comparable periods/follow-up, unresolved selection/measurement, review status and outcome-specific precision. No effect estimation is used to tune the design.

**Prepare the main study** only if the linked sample, valid cutoff support, measurement/selection audit, independent coding and design-specific useful precision pass. A substantive effect threshold must be justified. This early benchmark cannot provide that authorization.

**Targeted expansion** requires a demonstrably scalable route to additional independent elections with comparable outcomes/periods. More notices per existing municipality, predicted labels or a wider numerical margin alone do not meet that condition. Pooling states/cohorts needs an explicit institutional and estimand argument.

**End the causal claim** if no credible route passes the bounded audit. Preserve the work as a reproducible feasibility/data report with explicit limits. A final positive NRW go decision still requires the full structural-pair attrition ledger; an early adapt/stop can occur before extensive collection. GitHub Pages remains deferred until research completion under the chosen publication scope.

## Reproduction and verification

Run from the repository root with the existing local artifacts pinned in [input hashes](nrw-early-feasibility-input-hashes.csv):

```sh
python -m pip install -r analysis/requirements-feasibility.txt
python src/pilot/nrw_early_feasibility.py --prepare-independent-review
python -m unittest discover -s tests -v
```

The numerical environment is separately pinned for this benchmark; it does not select or freeze the main RDD stack. The tests check null rejection probabilities, an independent noncentral-t reference, raw Gaussian Monte Carlo rejection frequencies, and insufficient-side geometry. The generator preserves the baseline and candidate annotations and publishes only event/aggregate tables, a checkpoint and an empty coding template. Source originals, person packets and first-coder keys remain local. This memo replaces the earlier collection-first execution order; it does not change the historical baseline or supply a second review.
