# Research reopening: the NRW 2025 election cohort

Checked 10 October 2026. This is new empirical acquisition toward the original question, not a revision of the feasibility report frozen on 5 October. The earlier no-go concerns the audited historical route; it does not establish no effect or rule out a different cohort. This project continues to adapt Florio and Spagnolo (2026) to Germany; [German research and design precedents](literature-design-crosswalk.md) remain relevant. The estimand concerns electing a particular female candidate rather than her actual opponent, not an isolated sex effect.

## A complete new official election cohort

The two [official NRW summaries](https://wahlergebnisse.nrw/kommunalwahlen/2025/KW25_pers_gemeinden.txt) enumerate 396 municipalities: 387 elections and nine no-election entries. County offices are separately excluded (31). All 387 municipal detail files were acquired and validated, with no parsing failures: 1,355 candidate records, 133 runoffs and 233 decisive two-person pairs. Checks reconcile candidate votes, decisive-round denominators and the declared winner. Single-candidate ballots and larger first-round fields are not invented pairs.

| Absolute margin | All official pairs | Predicted mixed leads | Predicted female wins / losses |
|---|---:|---:|---:|
| ≤1 pp | 9 | 2 | 0 / 2 |
| ≤2 pp | 14 | 3 | 0 / 3 |
| ≤5 pp | 30 | 10 | 5 / 5 |
| ≤10 pp | 65 | 20 | 11 / 9 |

The GERDA snapshot at upstream commit `176259ea551b12a56dcd0c15b168e0e6e608f59a`, previously acquired on 5 October, matches 385 complete official candidate/name/vote/date/winner vectors and 231 decisive pairs. Two identity discrepancies remain; names are not silently merged. Its NRW gender fields are **name predictions, not verified administrative or historical-presentation measurements**. Same-label predictions cannot exclude an actual mixed pair. None of the new pairs is certified for the causal study.

## First procurement availability screen

Before examining procurement returns, the bounded query selected **all 30 official pairs within 5 pp**, regardless of gender predictions. It queried German local-authority standard contract-award notices published from 1 November 2025 through 30 September 2026, capped at 1,500 returns. Administrative `, Stadt` suffixes were removed for city queries and exact buyer-name aliases. This is a discovery band, not a selected RDD bandwidth.

The complete two-page result contains **388 notices**. Strict German buyer-name and local-authority checks provisionally assign **100 notices to 18 municipalities**; 284 remain unmatched or ambiguous and four lack a unique German buyer name. These are result-publication counts, not deduplicated procedures or outcome observations. Zero exact matches is not evidence of no procurement.

Six predicted mixed leads have provisional matches, with three predicted female wins and three losses: Königswinter (2 notices), Neunkirchen-Seelscheid (10), Herdecke (3), Lüdenscheid (20), Lünen (7) and Mülheim an der Ruhr (4). These 46 notices provide a concrete verification queue; neither their gender assignment nor their original call dates, buyer jurisdiction and outcome eligibility have been certified.

Even if all six became usable, the independent equal-variance Gaussian pooled-t planning benchmark at two-sided α=.05 and 80% power is **3.07 outcome standard deviations**; the ten prediction leads before procurement matching would imply **2.02 SD** under those assumptions. Neither is RDD power or an estimate using observed variance. More notices cannot replace more independent elections, and a five-point discovery band cannot cure a lack of close-cutoff support. At ≤2 pp the current prediction leads have no female wins.

## Next empirical work and decision rule

1. Verify contemporaneous candidate presentation for the six provisional matched leads, plus an audit of the remaining pairs irrespective of predictions. Preserve the existing measurement codebook; do not infer treatment from names, occupations or current office titles. Separate independent coding remains required.
2. For the 46 matched-lead notices, recover original competitions and distinguish calls begun before and after the actual 2025 change in office. Establish buyer jurisdiction, actual term boundaries, procedure deduplication and single-total-tender denominators before calculating the two nominated outcomes.
3. Assess a common window using original competitions in January–March 2026, with result follow-up through September 2026, as a **candidate window only**. Check maturity and right censoring before adopting it. Results published after November 2025 may arise from earlier calls; publication date is not treatment timing. A full annual post-election window is not yet mature.
4. Reassess precision from the certified election-level sample and observed outcome variance. If this cohort remains too small or one-sided near the cutoff, inspect complete named-candidate cohorts in other states rather than widening an RDD band to obtain significance. Cross-state pooling requires institutional, office-scope and timing justification.

The national exploratory screen found that Bavaria 2026 still lacks losing candidates' names in GERDA. Other states offer named-candidate leads, but coverage is not a national census and primary-source validation is outstanding. A large new Bavaria acquisition is therefore not the next priority. The main causal study remains gated; this bounded NRW 2025 work is authorized to test a materially different route. The frozen report, its conclusions and its evidence pins remain unchanged. GitHub Pages remains deferred until completed research.

## Reproduction and evidence

Run from the repository root with the optional feasibility dependencies installed:

```sh
python src/pilot/nrw_2025_reopening.py
python src/pilot/nrw_2025_procurement_screen.py
python -m unittest discover -s tests
```

The first script requires the locally retained two summary files and pinned GERDA snapshot; official detail acquisition uses the documented public source URLs. The second retains and verifies its capped TED snapshot rather than replacing it. Raw files and candidate records stay in ignored local directories. Public outputs are the [election summary](nrw-2025-reopening-summary.json), [official source hashes](nrw-2025-source-manifest.csv), [availability matrix](nrw-2025-availability-matrix.csv), [TED request/page hashes](nrw-2025-ted-request-manifest.json) and [procurement/conditional planning summary](nrw-2025-procurement-summary.json). The new tests protect cohort separation, runoff denominators, county exclusion and selection without a gender filter.
