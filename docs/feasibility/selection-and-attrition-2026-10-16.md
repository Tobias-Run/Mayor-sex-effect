# Selection and attrition audit — 16 October 2026

**The existing records show uneven documentation and a small intersection of candidate and procurement evidence. They do not identify or correct selection bias.** All calculations use the fixed 176-event scoreboard and six-event exposure ledger, without additional candidate coding, outcome estimation or source acquisition. The procurement cutoff remains 30 September 2026.

## Denominators and sequential intersections

The frame contains 176 events in 159 municipalities, including seventeen repeated municipalities. It is an acquired bookkeeping union, not a complete national close-election cohort or probability sample. Cohort definitions, effort and observation windows differ. The aggregate below describes accounting only; it does not authorize pooling.

| Sequential intersection | Events retained | Do not progress from previous stage |
| --- | ---: | ---: |
| Acquired event frame | 176 | 0 |
| Both historical presentations supported | 38 | 138 |
| Opposite presentations supported by first coder | 19 | 19 |
| Mixed pair with original-supported call evidence | 9 | 10 |
| Mixed pair with supported tender-count statistic | 6 | 3 |
| Those links align with diagnostic first-post-election Q1 | 4 | 2 |
| Independently certified main-study cases | 0 | 4 |

“Do not progress” is stage-specific, not a judgement that the underlying election or procurement is invalid. Nineteen supported same-presentation pairs fail the proposed treatment contrast, whereas 138 pairs remain unresolved. A missing result statistic is not zero procurement or zero bids. The final zero jointly reflects still-open review/validity/coverage gates; it cannot be attributed solely to a particular gate's causal influence. First-post-election Q1 remains a diagnostic reference, not an adopted main-study window. Alternative ordering of checks would change stage-specific losses.

Parallel source availability must not be confused with that sequential path: 92 events have call metadata, 39 have original-supported calls, and 22 have at least one supported count statistic. Only six of those 22 also have supported mixed-presentation assignments. These figures describe current evidence, not all municipal purchasing.

## Winner/opponent documentation

Across the 176 events, winner presentation is supported in **52 (29.5%)**, opponent presentation in **39 (22.2%)**. Both are supported in 38, only the winner in 14, only the opponent in one, and neither in 123. The paired support difference is **7.39 percentage points**. Documentation of winners therefore exceeds documentation of opponents in this inventory; causation by winning, incumbency or any specific publication practice is not established.

| Cohort | Events | Winner supported | Opponent supported | Both supported |
| --- | ---: | ---: | ---: | ---: |
| Brandenburg 2024 | 5 | 1 | 1 | 1 |
| Brandenburg 2025 | 8 | 1 | 1 | 1 |
| NRW 2020 | 55 | 27 | 20 | 19 |
| NRW 2025 | 65 | 17 | 14 | 14 |
| Niedersachsen 2021 | 36 | 1 | 1 | 1 |
| Saxony 2022 plurality | 7 | 5 | 2 | 2 |

The nested 2-point bookkeeping band has support for 28 of 39 winners and 24 of 39 opponents, versus 52/176 and 39/176 in the 10-point frame. This is consistent with deliberate priority research on closer races; it is not evidence that electoral closeness itself improves documentation. Bands overlap and cannot be added. Saxony plurality events remain separate from two-candidate cohorts.

## Documentation and procurement-source availability

Pairs with original-supported call evidence have both presentations supported in **13/39 (33.3%)**, compared with **25/137 (18.2%)** without that evidence: a descriptive difference of 15.09 points. This can reflect cohort composition, prior selection and unequal review effort as well as source accessibility; it is not a selection-adjusted effect or a causal estimate.

| Cohort | Both supported among events with original calls | Both supported without original calls |
| --- | ---: | ---: |
| Brandenburg 2024 | 1/2 | 0/3 |
| Brandenburg 2025 | 0/1 | 1/7 |
| NRW 2020 | 2/8 | 17/47 |
| NRW 2025 | 9/23 | 5/42 |
| Niedersachsen 2021 | 1/5 | 0/31 |
| Saxony 2022 plurality | NA (no events with supported calls) | 2/7 |

The direction differs within cohorts. NRW 2020 has less complete pair documentation among call-linked events (25.0% versus 36.2%), whereas NRW 2025 has more (39.1% versus 11.9%). An aggregate association is therefore insufficient evidence of a universal documentation mechanism. No inverse-probability weights, missing-at-random assumption, significance tests or independence-based confidence intervals are introduced. Repeated municipalities and the nonrandom acquisition frame further limit such interpretations.

The observed statistic-linked group has 10/22 complete pairs, compared with 28/154 without a supported statistic. That comparison conditions on realized reporting and the prior source pipeline; it cannot establish unselected outcome observability. No outcome value is used to rank cases in this audit.

## What remains unmeasured

The pinned scoreboard has no harmonized historical municipality population or full-frame incumbency field. The audit therefore cannot test size or incumbency selection and does not infer those attributes from present office pages, names, occupations or document counts. Formal research-priority/effort histories are also not harmonized into a comparable exposure measure. Broader representativeness claims require a separately defined complete cohort and comparable pre-election covariates, rather than ad hoc imputation.

The current thirteen-pair independent packet includes all six provisional links plus seven controls, but is not a random full-frame audit. Its future results will assess those reviewed cases; they cannot by themselves certify the 176-event frame's error rate. No independent reviewer is currently available. Model repetition or internal accounting is not substituted for independent coding.

## Reproduce and use

```sh
python src/report/audit_feasibility_selection.py
python -m unittest discover -s tests
```

The [input manifest](internal-review-selection-inputs-2026-10-16.json) pins the public sources. The generated [flow](selection-audit-2026-10-16-flow.csv), [role accounting](selection-audit-2026-10-16-roles.csv), [source-association strata](selection-audit-2026-10-16-source-association.csv) and [summary](selection-audit-2026-10-16-summary.json) retain cohort-specific 2/5/10-point strata and explicit zero-denominator NA values. The `ALL_BOOKKEEPING_NOT_POOLED_ANALYSIS` rows are bookkeeping diagnostics, not an analysis dataset. Tests reject inconsistent treatment/source intersections, duplicate events and unsupported inferred classifications.

The findings reinforce the manuscript's limits and the P5 no-launch decision. They justify retaining unresolved and excluded cases for review, but do not supply a bias correction or additional certified elections.
