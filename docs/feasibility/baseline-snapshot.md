# Acquisition baseline — 5 October 2026

FP01 records the existing acquisition cohort before interpreting the new candidate screen. Its code and documentation baseline is commit [`bdacc72`](https://github.com/Tobias-Run/Mayor-sex-effect/commit/bdacc72f3982694bcf02da9bd17fc82c5e51dc07). The [15 artifact hashes](baseline-source-hashes.csv) pin the election register, procurement summaries and observations, underlying source manifests and construction modules. The linked source manifests retain individual original-document/archive hashes; this snapshot does not redistribute their contents or person records.

| Component | Reconciled baseline | Open gate |
| --- | --- | --- |
| Official NRW 2020 election universe | 396 municipal entries: 380 elections and 16 explicit no-election entries; 31 county-office entries excluded | This is not a nationwide mayor register |
| Original election details | 380 checked files, 1,349 candidates, 117 runoffs, 214 decisive two-person pairs | Sex/gender and complete actual terms are not source fields |
| Acquisition margins | 4 / 15 / 34 / 55 pairs within inclusive 1 / 2 / 5 / 10 pp | Descriptive acquisition bands, not an RDD bandwidth |
| GERDA comparison | 212/214 decisive identity matches; all NRW gender-source values predicted | Do not restrict verification to the 72 predicted mixed leads |
| Retained procurement | 237 result notices | Retention is not complete municipal procurement coverage |
| Dated/count observations | 123 units in 82 notices across six municipal elections | Full deduplication and analytical unit choice pending |
| Procedure chronology | 115 supported competition-to-contract observations, five competitive timing cases unresolved, three explicit no-call cases | Outcome-specific timing rules pending |
| Buyer scope | 37 cases still pending | Addresses and generic municipal references do not establish legal beneficiary scope |
| Main research | Zero certified main-study assignments; no causal effects estimated | Measurement, common windows, sample support and precision must pass first |

The 123/82/6 count is recomputed directly from the pinned `outputs/nrw-procedure-scope/observations.json`, grouping unique `publication_number` and `ags`; it agrees with the prior phase/buyer audit. Election totals reconcile to the pinned statewide summary. The source hashes identify the existing local artifacts, not evidence of an independent replication of every earlier pipeline in this work package.

The [new close-pair review](nrw-close-election-evidence-review.md) adds historical presentation evidence under the version-1 codebook. It does not change this procurement inventory, certify full exposure histories or convert predictions into recorded administrative sex/gender. Earlier seven-pair public-presentation inventories used different temporal and title evidence; they are preserved as dated acquisition history and are not the new historical eligibility count.

The project continues to adapt Florio and Spagnolo (2026), with German foundations documented in the [literature note](../literature.md). GitHub Pages remains deferred until research completion.
